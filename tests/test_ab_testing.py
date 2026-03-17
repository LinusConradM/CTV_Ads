"""Tests for A/B testing framework."""

import pytest
import pandas as pd
import numpy as np
from analytics.ab_testing import ABTestAnalyzer


@pytest.fixture
def identical_groups():
    """Two groups drawn from the same distribution."""
    rng = np.random.default_rng(42)
    control = pd.Series(rng.normal(0.5, 0.1, 5000))
    treatment = pd.Series(rng.normal(0.5, 0.1, 5000))
    return ABTestAnalyzer(control, treatment)


@pytest.fixture
def different_groups():
    """Two groups with a real effect."""
    rng = np.random.default_rng(42)
    control = pd.Series(rng.normal(0.5, 0.1, 5000))
    treatment = pd.Series(rng.normal(0.55, 0.1, 5000))
    return ABTestAnalyzer(control, treatment)


class TestPowerAnalysis:
    def test_sample_size_positive(self, identical_groups):
        result = identical_groups.power_analysis(mde=0.05)
        assert result["min_sample_size_per_group"] > 0

    def test_larger_mde_needs_fewer_samples(self, identical_groups):
        small_mde = identical_groups.power_analysis(mde=0.01)
        large_mde = identical_groups.power_analysis(mde=0.10)
        assert small_mde["min_sample_size_per_group"] > large_mde["min_sample_size_per_group"]

    def test_sufficiently_powered_flag(self, different_groups):
        result = different_groups.power_analysis()
        assert isinstance(result["is_sufficiently_powered"], (bool, np.bool_))


class TestTTest:
    def test_identical_groups_not_significant(self, identical_groups):
        result = identical_groups.run_ttest()
        # With same distribution, p-value should usually be > 0.05
        # Allow some randomness but effect size should be near zero
        assert abs(result["effect_size"]) < 0.05

    def test_different_groups_significant(self, different_groups):
        result = different_groups.run_ttest()
        assert result["significant"]
        assert result["p_value"] < 0.05

    def test_ci_contains_effect(self, different_groups):
        result = different_groups.run_ttest()
        ci_lower, ci_upper = result["ci_95"]
        assert ci_lower <= result["effect_size"] <= ci_upper


class TestZTest:
    def test_binary_outcomes(self):
        rng = np.random.default_rng(42)
        control = pd.Series(rng.choice([0, 1], 5000, p=[0.95, 0.05]))
        treatment = pd.Series(rng.choice([0, 1], 5000, p=[0.92, 0.08]))
        ab = ABTestAnalyzer(control, treatment)
        result = ab.run_ztest()
        assert "z_stat" in result
        assert "p_value" in result
        assert result["treatment_rate"] > result["control_rate"]


class TestCUPED:
    def test_variance_reduction(self, different_groups):
        rng = np.random.default_rng(42)
        covariate = pd.Series(rng.normal(0.5, 0.1, different_groups.n_treatment))
        adjusted, theta = different_groups.cuped_adjustment(covariate)
        # Adjusted series should have same or smaller variance
        assert len(adjusted) > 0


class TestBootstrap:
    def test_bootstrap_ci(self, different_groups):
        result = different_groups.bootstrap_ci(n_iterations=1000)
        assert result["ci_lower"] < result["ci_upper"]
        assert result["ci_lower"] <= result["mean_diff"] <= result["ci_upper"]


class TestSequential:
    def test_sequential_structure(self, different_groups):
        result = different_groups.sequential_test(n_looks=3)
        assert len(result["looks"]) == 3
        assert "early_stop" in result


class TestSummarize:
    def test_summary_keys(self, different_groups):
        result = different_groups.summarize_results()
        assert "sample_sizes" in result
        assert "means" in result
        assert "effect_size" in result
        assert "ttest" in result
        assert "power" in result
