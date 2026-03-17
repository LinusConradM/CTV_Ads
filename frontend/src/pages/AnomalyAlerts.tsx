import { useState } from 'react';
import { AlertTriangle, Shield, Folder, Bot } from 'lucide-react';
import KPICard from '../components/ui/KPICard';
import ChartCard from '../components/ui/ChartCard';
import DataTable from '../components/ui/DataTable';
import LoadingSpinner from '../components/ui/LoadingSpinner';
import HistogramChart from '../components/charts/HistogramChart';
import BarChartComponent from '../components/charts/BarChartComponent';
import ControlChartComponent from '../components/charts/ControlChartComponent';
import { useAnomalies } from '../hooks/useAnomalies';
import { formatCompact, formatCurrency, formatPercent } from '../utils/formatters';

const CONTAMINATION_OPTIONS = [0.01, 0.02, 0.05, 0.10];
const METRIC_OPTIONS = [
  { value: 'clearing_price_cpm', label: 'Clearing Price (CPM)' },
  { value: 'pixels_visible_pct', label: 'Pixels Visible (%)' },
  { value: 'view_duration_seconds', label: 'View Duration (s)' },
];

const flaggedColumns = [
  { key: 'impression_id', label: 'Impression ID' },
  { key: 'campaign_id', label: 'Campaign' },
  { key: 'device_type', label: 'Device' },
  {
    key: 'clearing_price_cpm',
    label: 'CPM',
    format: (v: number) => formatCurrency(v),
  },
  {
    key: 'pixels_visible_pct',
    label: 'Pixels Visible',
    format: (v: number) => formatPercent(v),
  },
  {
    key: 'view_duration_seconds',
    label: 'View Duration (s)',
    format: (v: number) => v.toFixed(1),
  },
  {
    key: 'anomaly_score',
    label: 'Anomaly Score',
    format: (v: number) => v.toFixed(4),
  },
];

export default function AnomalyAlerts() {
  const [contamination, setContamination] = useState(0.05);
  const [metric, setMetric] = useState('clearing_price_cpm');

  const { data, isLoading, error } = useAnomalies(contamination, metric);

  if (isLoading) return <LoadingSpinner />;
  if (error) {
    return (
      <div className="flex items-center justify-center h-64 text-rose-400">
        Failed to load anomaly data. Please try again.
      </div>
    );
  }
  if (!data) return null;

  const { kpis, summary, control_chart, flagged_records, score_distribution } = data;

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-100">Anomaly Alerts</h1>
          <p className="mt-1 text-sm text-slate-400">
            Isolation Forest anomaly detection and monitoring
          </p>
        </div>

        {/* Controls */}
        <div className="flex items-center gap-3">
          <select
            value={contamination}
            onChange={(e) => setContamination(Number(e.target.value))}
            className="bg-slate-700 border border-slate-600 text-slate-200 rounded-lg px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            {CONTAMINATION_OPTIONS.map((val) => (
              <option key={val} value={val}>
                Contamination: {val}
              </option>
            ))}
          </select>

          <select
            value={metric}
            onChange={(e) => setMetric(e.target.value)}
            className="bg-slate-700 border border-slate-600 text-slate-200 rounded-lg px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            {METRIC_OPTIONS.map((opt) => (
              <option key={opt.value} value={opt.value}>
                {opt.label}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* KPI Row */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <KPICard
          title="Anomaly Rate"
          value={`${kpis.anomaly_rate.toFixed(1)}%`}
          icon={AlertTriangle}
          color="rose"
        />
        <KPICard
          title="Anomalies Flagged"
          value={formatCompact(kpis.anomalies_flagged)}
          icon={Shield}
          color="amber"
        />
        <KPICard
          title="Flagged Campaigns"
          value={kpis.flagged_campaigns}
          icon={Folder}
          color="blue"
        />
        <KPICard
          title="Bot Traffic Rate"
          value={`${kpis.bot_traffic_rate.toFixed(1)}%`}
          icon={Bot}
          color="rose"
        />
      </div>

      {/* Row 1: Score Distribution + Category Breakdown */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <ChartCard title="Anomaly Score Distribution" subtitle="Distribution of isolation forest scores">
          <HistogramChart data={score_distribution} color="#f43f5e" />
        </ChartCard>

        <ChartCard title="Anomaly Categories" subtitle="Breakdown by anomaly type">
          <BarChartComponent
            data={summary}
            xKey="category"
            bars={[{ key: 'count', color: '#f43f5e', name: 'Count' }]}
          />
        </ChartCard>
      </div>

      {/* Full-width Control Chart */}
      <ChartCard title="Control Chart" subtitle="Statistical process control monitoring over time">
        <ControlChartComponent data={control_chart} height={350} />
      </ChartCard>

      {/* Flagged Records Table */}
      <div>
        <h2 className="text-lg font-semibold text-slate-200 mb-3">Flagged Records</h2>
        <DataTable columns={flaggedColumns} data={flagged_records} pageSize={15} />
      </div>
    </div>
  );
}
