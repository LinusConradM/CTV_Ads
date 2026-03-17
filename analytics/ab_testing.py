"""
Analytics — A/B Testing Framework

End-to-end experimentation for ad creative and targeting variant testing.
Includes power analysis, z-test, t-test, bootstrap CI, CUPED variance
reduction, and sequential testing.
"""

import numpy as np
import pandas as pd
from scipy import stats


class ABTestAnalyzer:
    """Analyzer for A/B test results on ad campaign metrics."""

    def __init__(self, control: pd.Series, treatment: pd.Series):
        self.control = control.dropna()
        self.treatment = treatment.dropna()

    @property
    def n_control(self) -> int:
        return len(self.control)

    @property
    def n_treatment(self) -> int:
        return len(self.treatment)

    @property
    def effect_size(self) -> float:
        return self.treatment.mean() - self.control.mean()

    @property
    def relative_lift(self) -> float:
        ctrl_mean = self.control.mean()
        if ctrl_mean == 0:
            return 0.0
        return self.effect_size / ctrl_mean

    def power_analysis(self, alpha: float = 0.05, power: float = 0.80, mde: float = None) -> dict:
        """Compute minimum sample size for desired statistical power.

        Args:
            alpha: significance level
            power: desired power (1 - beta)
            mde: minimum detectable effect (absolute). If None, uses observed effect.
        """
        if mde is None:
            mde = abs(self.effect_size)
            if mde == 0:
                mde = 0.01  # default small effect

        pooled_std = np.sqrt(
            (self.control.std() ** 2 + self.treatment.std() ** 2) / 2
        )

        if pooled_std == 0:
            return {"min_sample_size_per_group": 0, "mde": mde, "alpha": alpha, "power": power}

        z_alpha = stats.norm.ppf(1 - alpha / 2)
        z_beta = stats.norm.ppf(power)

        n = ((z_alpha + z_beta) * pooled_std / mde) ** 2
        n = int(np.ceil(n))

        return {
            "min_sample_size_per_group": n,
            "mde": round(mde, 6),
            "pooled_std": round(pooled_std, 6),
            "alpha": alpha,
            "power": power,
            "current_n_control": self.n_control,
            "current_n_treatment": self.n_treatment,
            "is_sufficiently_powered": min(self.n_control, self.n_treatment) >= n,
        }

    def run_ztest(self) -> dict:
        """Two-proportion z-test (for binary outcomes like conversion rate)."""
        p1 = self.control.mean()
        p2 = self.treatment.mean()
        n1 = self.n_control
        n2 = self.n_treatment

        p_pool = (p1 * n1 + p2 * n2) / (n1 + n2)
        se = np.sqrt(p_pool * (1 - p_pool) * (1/n1 + 1/n2))

        if se == 0:
            return {"z_stat": 0, "p_value": 1.0, "significant": False}

        z = (p2 - p1) / se
        p_value = 2 * (1 - stats.norm.cdf(abs(z)))

        ci_se = np.sqrt(p1*(1-p1)/n1 + p2*(1-p2)/n2)
        ci_lower = (p2 - p1) - 1.96 * ci_se
        ci_upper = (p2 - p1) + 1.96 * ci_se

        return {
            "z_stat": round(z, 4),
            "p_value": round(p_value, 6),
            "significant": p_value < 0.05,
            "control_rate": round(p1, 6),
            "treatment_rate": round(p2, 6),
            "absolute_lift": round(p2 - p1, 6),
            "relative_lift": round((p2 - p1) / p1, 4) if p1 > 0 else None,
            "ci_95": (round(ci_lower, 6), round(ci_upper, 6)),
        }

    def run_ttest(self) -> dict:
        """Welch's t-test for continuous metrics."""
        t_stat, p_value = stats.ttest_ind(self.treatment, self.control, equal_var=False)

        # 95% CI for difference in means
        se = np.sqrt(
            self.control.var() / self.n_control +
            self.treatment.var() / self.n_treatment
        )
        ci_lower = self.effect_size - 1.96 * se
        ci_upper = self.effect_size + 1.96 * se

        return {
            "t_stat": round(t_stat, 4),
            "p_value": round(p_value, 6),
            "significant": p_value < 0.05,
            "control_mean": round(self.control.mean(), 6),
            "treatment_mean": round(self.treatment.mean(), 6),
            "effect_size": round(self.effect_size, 6),
            "relative_lift": round(self.relative_lift, 4),
            "ci_95": (round(ci_lower, 6), round(ci_upper, 6)),
        }

    def cuped_adjustment(self, covariate: pd.Series) -> tuple[pd.Series, float]:
        """CUPED variance reduction using pre-experiment covariate.

        Args:
            covariate: pre-experiment metric values aligned with treatment group
        Returns:
            adjusted treatment values, theta coefficient
        """
        covariate = covariate.dropna()
        min_len = min(len(self.treatment), len(covariate))
        treatment = self.treatment.iloc[:min_len]
        cov = covariate.iloc[:min_len]

        cov_matrix = np.cov(treatment, cov)
        if cov_matrix[1, 1] == 0:
            return treatment, 0.0

        theta = cov_matrix[0, 1] / cov_matrix[1, 1]
        adjusted = treatment - theta * (cov - cov.mean())

        return adjusted, round(theta, 4)

    def bootstrap_ci(self, n_iterations: int = 10000, ci: float = 0.95) -> dict:
        """Bootstrap confidence interval for difference in means."""
        rng = np.random.default_rng(42)
        diffs = []

        for _ in range(n_iterations):
            ctrl_sample = rng.choice(self.control.values, size=self.n_control, replace=True)
            treat_sample = rng.choice(self.treatment.values, size=self.n_treatment, replace=True)
            diffs.append(treat_sample.mean() - ctrl_sample.mean())

        diffs = np.array(diffs)
        alpha = (1 - ci) / 2

        return {
            "mean_diff": round(np.mean(diffs), 6),
            "ci_lower": round(np.percentile(diffs, alpha * 100), 6),
            "ci_upper": round(np.percentile(diffs, (1 - alpha) * 100), 6),
            "ci_level": ci,
            "n_iterations": n_iterations,
            "significant": not (np.percentile(diffs, alpha * 100) <= 0 <= np.percentile(diffs, (1 - alpha) * 100)),
        }

    def sequential_test(self, alpha_spending: str = "obrien_fleming", n_looks: int = 5) -> dict:
        """Sequential testing with alpha spending for early stopping.

        Uses O'Brien-Fleming-like boundaries.
        """
        total_alpha = 0.05
        n_per_look = self.n_treatment // n_looks

        results = []
        for look in range(1, n_looks + 1):
            n_current = min(look * n_per_look, self.n_treatment)
            info_fraction = n_current / self.n_treatment

            # O'Brien-Fleming boundary
            if alpha_spending == "obrien_fleming":
                z_boundary = stats.norm.ppf(1 - total_alpha / (2 * np.sqrt(1 / info_fraction)))
            else:
                z_boundary = stats.norm.ppf(1 - total_alpha / (2 * n_looks))

            # Compute z-stat at this look
            ctrl = self.control.iloc[:n_current]
            treat = self.treatment.iloc[:n_current]

            if len(ctrl) == 0 or len(treat) == 0:
                continue

            pooled_se = np.sqrt(ctrl.var() / len(ctrl) + treat.var() / len(treat))
            if pooled_se == 0:
                z_stat = 0
            else:
                z_stat = (treat.mean() - ctrl.mean()) / pooled_se

            results.append({
                "look": look,
                "n_per_group": n_current,
                "info_fraction": round(info_fraction, 2),
                "z_stat": round(z_stat, 4),
                "z_boundary": round(z_boundary, 4),
                "reject_null": abs(z_stat) > z_boundary,
            })

        return {
            "alpha_spending": alpha_spending,
            "n_looks": n_looks,
            "looks": results,
            "early_stop": any(r["reject_null"] for r in results),
        }

    def summarize_results(self) -> dict:
        """Comprehensive test summary."""
        return {
            "sample_sizes": {
                "control": self.n_control,
                "treatment": self.n_treatment,
            },
            "means": {
                "control": round(self.control.mean(), 6),
                "treatment": round(self.treatment.mean(), 6),
            },
            "effect_size": round(self.effect_size, 6),
            "relative_lift": round(self.relative_lift, 4),
            "ttest": self.run_ttest(),
            "power": self.power_analysis(),
        }
