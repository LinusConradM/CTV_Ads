import { BarChart3, Users, Repeat, DollarSign, Eye, CheckCircle } from 'lucide-react';
import { useCampaigns } from '../hooks/useCampaigns';
import KPICard from '../components/ui/KPICard';
import ChartCard from '../components/ui/ChartCard';
import DataTable from '../components/ui/DataTable';
import LoadingSpinner from '../components/ui/LoadingSpinner';
import EmptyState from '../components/ui/EmptyState';
import AreaLineChart from '../components/charts/AreaLineChart';
import BarChartComponent from '../components/charts/BarChartComponent';
import { formatCompact, formatCurrency, formatPercent, formatNumber } from '../utils/formatters';
import { CHART_COLORS } from '../utils/colors';

const performanceColumns = [
  { key: 'campaign_id', label: 'Campaign' },
  { key: 'impressions', label: 'Impressions', format: (v: number) => formatCompact(v) },
  { key: 'unique_reach', label: 'Unique Reach', format: (v: number) => formatCompact(v) },
  { key: 'avg_cpm', label: 'Avg CPM', format: (v: number) => formatCurrency(v) },
  { key: 'viewable_rate', label: 'Viewable Rate', format: (v: number) => formatPercent(v) },
  { key: 'completion_rate', label: 'Completion Rate', format: (v: number) => formatPercent(v) },
  { key: 'conversion_rate', label: 'Conv Rate', format: (v: number) => formatPercent(v) },
  { key: 'total_spend', label: 'Total Spend', format: (v: number) => formatCurrency(v) },
  { key: 'frequency', label: 'Frequency', format: (v: number) => formatNumber(v, 1) },
];

export default function CampaignOverview() {
  const { data, isLoading, isError } = useCampaigns();

  if (isLoading) return <LoadingSpinner />;
  if (isError || !data) return <EmptyState title="Failed to load" message="Unable to load campaign data. Please try again." />;

  const { kpis, performance_table, cpm_trend, device_breakdown, category_breakdown, top_dmas } = data;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-100">Campaign Overview</h1>
        <p className="mt-1 text-sm text-slate-400">Detailed campaign performance and breakdown analysis</p>
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
          title="Completion Rate"
          value={formatPercent(kpis.completion_rate)}
          icon={CheckCircle}
          color="green"
        />
      </div>

      {/* Row 1: CPM Trend + CPM by Device */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <ChartCard title="Daily CPM Trend" subtitle="Average CPM over time">
          <AreaLineChart
            data={cpm_trend}
            xKey="report_date"
            lines={[{ key: 'avg_cpm', color: CHART_COLORS[2], name: 'Avg CPM' }]}
          />
        </ChartCard>

        <ChartCard title="CPM by Device Type" subtitle="Average CPM across devices">
          <BarChartComponent
            data={device_breakdown}
            xKey="device_type"
            bars={[{ key: 'avg_cpm', color: CHART_COLORS[0], name: 'Avg CPM' }]}
          />
        </ChartCard>
      </div>

      {/* Row 2: Category + Top DMAs */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <ChartCard title="CPM by Content Category" subtitle="Average CPM by content type">
          <BarChartComponent
            data={category_breakdown}
            xKey="content_category"
            bars={[{ key: 'avg_cpm', color: CHART_COLORS[4], name: 'Avg CPM' }]}
          />
        </ChartCard>

        <ChartCard title="Top 10 DMAs" subtitle="Highest impression markets">
          <BarChartComponent
            data={top_dmas}
            xKey="dma_name"
            bars={[{ key: 'impressions', color: CHART_COLORS[1], name: 'Impressions' }]}
            layout="horizontal"
          />
        </ChartCard>
      </div>

      {/* Performance Table */}
      <ChartCard title="Campaign Performance" subtitle="Detailed metrics by campaign">
        <DataTable columns={performanceColumns} data={performance_table} />
      </ChartCard>
    </div>
  );
}
