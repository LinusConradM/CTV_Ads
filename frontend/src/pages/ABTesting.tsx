import { useState, useMemo } from 'react';
import { FlaskConical, TrendingUp, Percent, Binary, CheckCircle, Zap } from 'lucide-react';
import KPICard from '../components/ui/KPICard';
import ChartCard from '../components/ui/ChartCard';
import LoadingSpinner from '../components/ui/LoadingSpinner';
import HistogramChart from '../components/charts/HistogramChart';
import AreaLineChart from '../components/charts/AreaLineChart';
import { useABTesting } from '../hooks/useABTesting';
import { useFilters } from '../hooks/useFilters';

const METRIC_OPTIONS = [
  { value: 'view_completion_pct', label: 'View Completion (%)' },
  { value: 'converted', label: 'Converted' },
  { value: 'pixels_visible_pct', label: 'Pixels Visible (%)' },
];

export default function ABTesting() {
  const { options } = useFilters();

  const [campaignId, setCampaignId] = useState('');
  const [metric, setMetric] = useState('view_completion_pct');
  const [controlCreative, setControlCreative] = useState('');
  const [treatmentCreative, setTreatmentCreative] = useState('');

  // Get available creatives for the selected campaign
  const availableCreatives = useMemo(() => {
    if (!campaignId || !options?.campaign_creatives) return [];
    return options.campaign_creatives[campaignId] ?? [];
  }, [campaignId, options]);

  // Filter treatment options to exclude control
  const treatmentOptions = useMemo(() => {
    return availableCreatives.filter((c) => c !== controlCreative);
  }, [availableCreatives, controlCreative]);

  // Reset creatives when campaign changes
  const handleCampaignChange = (newCampaignId: string) => {
    setCampaignId(newCampaignId);
    setControlCreative('');
    setTreatmentCreative('');
  };

  // Reset treatment when control changes
  const handleControlChange = (newControl: string) => {
    setControlCreative(newControl);
    if (treatmentCreative === newControl) {
      setTreatmentCreative('');
    }
  };

  const selectionsComplete = campaignId && controlCreative && treatmentCreative;

  const { data, isLoading, error } = useABTesting(
    campaignId,
    controlCreative,
    treatmentCreative,
    metric
  );

  const selectClass =
    'bg-slate-700 border border-slate-600 text-slate-200 rounded-lg px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500';

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div>
        <h1 className="text-2xl font-bold text-slate-100">A/B Testing</h1>
        <p className="mt-1 text-sm text-slate-400">
          Statistical comparison of creative performance
        </p>
      </div>

      {/* Controls */}
      <div className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-5">
        <h2 className="text-sm font-semibold text-slate-300 mb-4">Test Configuration</h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {/* Campaign */}
          <div className="space-y-1.5">
            <label className="text-xs font-medium text-slate-400">Campaign</label>
            <select
              value={campaignId}
              onChange={(e) => handleCampaignChange(e.target.value)}
              className={`${selectClass} w-full`}
            >
              <option value="">Select campaign...</option>
              {options?.campaigns.map((c) => (
                <option key={c} value={c}>
                  {c}
                </option>
              ))}
            </select>
          </div>

          {/* Metric */}
          <div className="space-y-1.5">
            <label className="text-xs font-medium text-slate-400">Metric</label>
            <select
              value={metric}
              onChange={(e) => setMetric(e.target.value)}
              className={`${selectClass} w-full`}
            >
              {METRIC_OPTIONS.map((opt) => (
                <option key={opt.value} value={opt.value}>
                  {opt.label}
                </option>
              ))}
            </select>
          </div>

          {/* Control Creative */}
          <div className="space-y-1.5">
            <label className="text-xs font-medium text-slate-400">Control Creative</label>
            <select
              value={controlCreative}
              onChange={(e) => handleControlChange(e.target.value)}
              disabled={!campaignId}
              className={`${selectClass} w-full disabled:opacity-50 disabled:cursor-not-allowed`}
            >
              <option value="">Select control...</option>
              {availableCreatives.map((c) => (
                <option key={c} value={c}>
                  {c}
                </option>
              ))}
            </select>
          </div>

          {/* Treatment Creative */}
          <div className="space-y-1.5">
            <label className="text-xs font-medium text-slate-400">Treatment Creative</label>
            <select
              value={treatmentCreative}
              onChange={(e) => setTreatmentCreative(e.target.value)}
              disabled={!controlCreative}
              className={`${selectClass} w-full disabled:opacity-50 disabled:cursor-not-allowed`}
            >
              <option value="">Select treatment...</option>
              {treatmentOptions.map((c) => (
                <option key={c} value={c}>
                  {c}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Conditional Content */}
      {!selectionsComplete ? (
        <div className="flex flex-col items-center justify-center py-20 text-center">
          <FlaskConical className="w-16 h-16 text-slate-600 mb-4" />
          <h3 className="text-lg font-semibold text-slate-300 mb-2">Configure Your Test</h3>
          <p className="text-sm text-slate-500 max-w-md">
            Select a campaign, metric, and two creatives to compare. The control is your baseline
            and the treatment is the variant you want to evaluate.
          </p>
        </div>
      ) : isLoading ? (
        <LoadingSpinner />
      ) : error ? (
        <div className="flex items-center justify-center h-64 text-rose-400">
          Failed to load A/B test data. Please try again.
        </div>
      ) : data ? (
        <div className="space-y-6">
          {/* KPI Row */}
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-4">
            <KPICard
              title="Control Mean"
              value={data.kpis.control_mean.toFixed(4)}
              icon={TrendingUp}
              color="blue"
            />
            <KPICard
              title="Treatment Mean"
              value={data.kpis.treatment_mean.toFixed(4)}
              icon={TrendingUp}
              color="green"
            />
            <KPICard
              title="Effect Size"
              value={data.kpis.effect_size.toFixed(4)}
              icon={Percent}
              color="amber"
            />
            <KPICard
              title="P-Value"
              value={data.kpis.p_value.toFixed(4)}
              icon={Binary}
              color={data.kpis.p_value < 0.05 ? 'green' : 'rose'}
            />
            <KPICard
              title="Significant"
              value={data.kpis.significant ? 'Yes' : 'No'}
              icon={CheckCircle}
              color={data.kpis.significant ? 'green' : 'rose'}
            />
            <KPICard
              title="Powered"
              value={data.kpis.is_powered ? 'Yes' : 'No'}
              icon={Zap}
              color={data.kpis.is_powered ? 'green' : 'amber'}
            />
          </div>

          {/* Row 1: Distribution Histograms */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            <ChartCard title="Control Distribution" subtitle={`Creative: ${controlCreative}`}>
              <HistogramChart data={data.control_distribution} color="#3b82f6" />
            </ChartCard>

            <ChartCard
              title="Treatment vs Control Distribution"
              subtitle={`Treatment: ${treatmentCreative}`}
            >
              <HistogramChart
                data={data.control_distribution}
                color="#3b82f6"
                secondaryData={data.treatment_distribution}
                secondaryColor="#10b981"
              />
            </ChartCard>
          </div>

          {/* Bootstrap CI Card */}
          <div className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-5">
            <h3 className="text-sm font-semibold text-slate-200 mb-4">
              Bootstrap Confidence Interval
            </h3>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-6">
              <div>
                <p className="text-xs text-slate-400 mb-1">Mean Difference</p>
                <p className="text-lg font-bold text-slate-100">
                  {data.bootstrap.mean_diff.toFixed(4)}
                </p>
              </div>
              <div>
                <p className="text-xs text-slate-400 mb-1">CI Lower</p>
                <p className="text-lg font-bold text-slate-100">
                  {data.bootstrap.ci_lower.toFixed(4)}
                </p>
              </div>
              <div>
                <p className="text-xs text-slate-400 mb-1">CI Upper</p>
                <p className="text-lg font-bold text-slate-100">
                  {data.bootstrap.ci_upper.toFixed(4)}
                </p>
              </div>
              <div>
                <p className="text-xs text-slate-400 mb-1">Significant</p>
                <p
                  className={`text-lg font-bold ${
                    data.bootstrap.significant ? 'text-emerald-400' : 'text-rose-400'
                  }`}
                >
                  {data.bootstrap.significant ? 'Yes' : 'No'}
                </p>
              </div>
            </div>
          </div>

          {/* Sequential Test Chart */}
          <ChartCard
            title="Sequential Testing"
            subtitle={`Alpha spending: ${data.sequential_test.alpha_spending} | ${data.sequential_test.n_looks} looks`}
          >
            <AreaLineChart
              data={data.sequential_test.looks}
              xKey="info_fraction"
              lines={[
                { key: 'z_stat', name: 'Z-Statistic', color: '#3b82f6' },
                { key: 'z_boundary', name: 'Boundary', color: '#f43f5e' },
              ]}
              height={350}
            />
          </ChartCard>
        </div>
      ) : null}
    </div>
  );
}
