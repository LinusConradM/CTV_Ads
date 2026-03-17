import { BarChart3, Users, Repeat, DollarSign, Eye, Target } from 'lucide-react';
import { useOverview } from '../hooks/useOverview';
import KPICard from '../components/ui/KPICard';
import ChartCard from '../components/ui/ChartCard';
import DataTable from '../components/ui/DataTable';
import LoadingSpinner from '../components/ui/LoadingSpinner';
import EmptyState from '../components/ui/EmptyState';
import AreaLineChart from '../components/charts/AreaLineChart';
import { formatCompact, formatCurrency, formatPercent, formatNumber } from '../utils/formatters';
import { CHART_COLORS } from '../utils/colors';

const campaignColumns = [
  { key: 'campaign_id', label: 'Campaign' },
  { key: 'impressions', label: 'Impressions', format: (v: number) => formatCompact(v) },
  { key: 'avg_cpm', label: 'Avg CPM', format: (v: number) => formatCurrency(v) },
  { key: 'viewable_rate', label: 'Viewable Rate', format: (v: number) => formatPercent(v) },
  { key: 'conversion_rate', label: 'Conv Rate', format: (v: number) => formatPercent(v) },
  { key: 'unique_reach', label: 'Unique Reach', format: (v: number) => formatCompact(v) },
];

export default function Dashboard() {
  const { data, isLoading, isError } = useOverview();

  if (isLoading) return <LoadingSpinner />;
  if (isError || !data) return <EmptyState title="Failed to load" message="Unable to load overview data. Please try again." />;

  const { kpis, daily_trend, campaign_summary } = data;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-100">Dashboard</h1>
        <p className="mt-1 text-sm text-slate-400">Platform overview and key performance metrics</p>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-4">
        <KPICard
          title="Total Impressions"
          value={formatCompact(kpis.total_impressions)}
          icon={BarChart3}
          color="blue"
        />
        <KPICard
          title="Unique Reach"
          value={formatCompact(kpis.unique_reach)}
          icon={Users}
          color="green"
        />
        <KPICard
          title="Avg Frequency"
          value={formatNumber(kpis.avg_frequency, 1)}
          icon={Repeat}
          color="amber"
        />
        <KPICard
          title="Avg CPM"
          value={formatCurrency(kpis.avg_cpm)}
          icon={DollarSign}
          color="rose"
        />
        <KPICard
          title="Viewable Rate"
          value={formatPercent(kpis.viewable_rate)}
          icon={Eye}
          color="blue"
        />
        <KPICard
          title="Conv Rate"
          value={formatPercent(kpis.conversion_rate)}
          icon={Target}
          color="green"
        />
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-6">
        <ChartCard title="Daily Impressions" subtitle="Impression volume over time">
          <AreaLineChart
            data={daily_trend}
            xKey="report_date"
            lines={[{ key: 'impressions', color: CHART_COLORS[0], name: 'Impressions' }]}
            areaFill
          />
        </ChartCard>

        <ChartCard title="Daily CPM Trend" subtitle="Average CPM over time">
          <AreaLineChart
            data={daily_trend}
            xKey="report_date"
            lines={[{ key: 'avg_cpm', color: CHART_COLORS[2], name: 'Avg CPM' }]}
            areaFill
          />
        </ChartCard>
      </div>

      {/* Campaign Summary Table */}
      <ChartCard title="Campaign Summary" subtitle="Performance by campaign">
        <DataTable columns={campaignColumns} data={campaign_summary} />
      </ChartCard>
    </div>
  );
}
