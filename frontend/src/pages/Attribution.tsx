import { useState } from 'react';
import { Target, Route, BarChart3, DollarSign } from 'lucide-react';
import KPICard from '../components/ui/KPICard';
import ChartCard from '../components/ui/ChartCard';
import DataTable from '../components/ui/DataTable';
import LoadingSpinner from '../components/ui/LoadingSpinner';
import BarChartComponent from '../components/charts/BarChartComponent';
import { useAttribution } from '../hooks/useAttribution';
import { formatCompact, formatCurrency } from '../utils/formatters';

const HALF_LIFE_OPTIONS = [1, 3, 7, 14, 30];

const comparisonColumns = [
  { key: 'campaign_id', label: 'Campaign' },
  {
    key: 'last_touch',
    label: 'Last Touch',
    format: (v: number) => v.toFixed(1),
  },
  {
    key: 'first_touch',
    label: 'First Touch',
    format: (v: number) => v.toFixed(1),
  },
  {
    key: 'linear',
    label: 'Linear',
    format: (v: number) => v.toFixed(1),
  },
  {
    key: 'time_decay',
    label: 'Time Decay',
    format: (v: number) => v.toFixed(1),
  },
  {
    key: 'total_spend',
    label: 'Total Spend',
    format: (v: number) => formatCurrency(v),
  },
];

export default function Attribution() {
  const [halfLifeDays, setHalfLifeDays] = useState(7);

  const { data, isLoading, error } = useAttribution(halfLifeDays);

  if (isLoading) return <LoadingSpinner />;
  if (error) {
    return (
      <div className="flex items-center justify-center h-64 text-rose-400">
        Failed to load attribution data. Please try again.
      </div>
    );
  }
  if (!data) return null;

  const { kpis, comparison } = data;

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-100">Attribution</h1>
          <p className="mt-1 text-sm text-slate-400">
            Multi-touch attribution model comparison
          </p>
        </div>

        {/* Controls */}
        <div className="flex items-center gap-3">
          <label className="text-sm text-slate-400">Half-life (days):</label>
          <select
            value={halfLifeDays}
            onChange={(e) => setHalfLifeDays(Number(e.target.value))}
            className="bg-slate-700 border border-slate-600 text-slate-200 rounded-lg px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            {HALF_LIFE_OPTIONS.map((val) => (
              <option key={val} value={val}>
                {val} {val === 1 ? 'day' : 'days'}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* KPI Row */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <KPICard
          title="Total Conversions"
          value={formatCompact(kpis.total_conversions)}
          icon={Target}
          color="blue"
        />
        <KPICard
          title="Avg Path Length"
          value={kpis.avg_path_length.toFixed(1)}
          icon={Route}
          color="green"
        />
        <KPICard
          title="Campaigns Credited"
          value={kpis.campaigns_credited}
          icon={BarChart3}
          color="amber"
        />
        <KPICard
          title="Total Spend"
          value={formatCurrency(kpis.total_spend)}
          icon={DollarSign}
          color="rose"
        />
      </div>

      {/* Attribution Comparison Chart */}
      <ChartCard
        title="Attribution Comparison"
        subtitle="Conversion credits across attribution models by campaign"
      >
        <BarChartComponent
          data={comparison}
          xKey="campaign_id"
          bars={[
            { key: 'last_touch', name: 'Last Touch', color: '#3b82f6' },
            { key: 'first_touch', name: 'First Touch', color: '#10b981' },
            { key: 'linear', name: 'Linear', color: '#f59e0b' },
            { key: 'time_decay', name: 'Time Decay', color: '#f43f5e' },
          ]}
          height={400}
        />
      </ChartCard>

      {/* Attribution Comparison Table */}
      <div>
        <h2 className="text-lg font-semibold text-slate-200 mb-3">
          Attribution Comparison Detail
        </h2>
        <DataTable columns={comparisonColumns} data={comparison} pageSize={15} />
      </div>
    </div>
  );
}
