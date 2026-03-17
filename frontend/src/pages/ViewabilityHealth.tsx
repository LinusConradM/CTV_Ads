import { Eye, Video, Monitor, Maximize, Clock } from 'lucide-react';
import { useViewability } from '../hooks/useViewability';
import KPICard from '../components/ui/KPICard';
import ChartCard from '../components/ui/ChartCard';
import DataTable from '../components/ui/DataTable';
import LoadingSpinner from '../components/ui/LoadingSpinner';
import EmptyState from '../components/ui/EmptyState';
import BarChartComponent from '../components/charts/BarChartComponent';
import ControlChartComponent from '../components/charts/ControlChartComponent';
import { formatPercent, formatNumber, formatCurrency, formatCompact } from '../utils/formatters';
import { CHART_COLORS } from '../utils/colors';

const publisherColumns = [
  { key: 'publisher_id', label: 'Publisher' },
  { key: 'impressions', label: 'Impressions', format: (v: number) => formatCompact(v) },
  { key: 'viewable_rate', label: 'Viewable Rate', format: (v: number) => formatPercent(v) },
  { key: 'avg_pixel_visibility', label: 'Avg Pixel Visibility', format: (v: number) => formatPercent(v) },
  { key: 'avg_cpm', label: 'Avg CPM', format: (v: number) => formatCurrency(v) },
  { key: 'rank', label: 'Rank', format: (v: number) => formatNumber(v) },
];

export default function ViewabilityHealth() {
  const { data, isLoading, isError } = useViewability();

  if (isLoading) return <LoadingSpinner />;
  if (isError || !data) return <EmptyState title="Failed to load" message="Unable to load viewability data. Please try again." />;

  const { kpis, campaign_report, device_breakdown, publisher_scorecard, trend } = data;

  // Map trend data to include `value` for ControlChartComponent
  const controlChartData = trend.map((t) => ({
    ...t,
    value: t.viewable_rate,
  }));

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-100">Viewability Health</h1>
        <p className="mt-1 text-sm text-slate-400">IAB MRC viewability standards and publisher quality scoring</p>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-4">
        <KPICard
          title="Viewable Rate"
          value={formatPercent(kpis.viewable_rate)}
          icon={Eye}
          color="blue"
        />
        <KPICard
          title="Video Viewable"
          value={formatPercent(kpis.video_viewable_rate)}
          icon={Video}
          color="green"
        />
        <KPICard
          title="Display Viewable"
          value={formatPercent(kpis.display_viewable_rate)}
          icon={Monitor}
          color="amber"
        />
        <KPICard
          title="Avg Pixel Visibility"
          value={formatPercent(kpis.avg_pixel_visibility)}
          icon={Maximize}
          color="rose"
        />
        <KPICard
          title="Avg View Duration"
          value={`${formatNumber(kpis.avg_view_duration, 1)}s`}
          icon={Clock}
          color="blue"
        />
      </div>

      {/* Row 1: Viewable Rate by Campaign + by Device */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <ChartCard title="Viewable Rate by Campaign" subtitle="Campaign-level viewability">
          <BarChartComponent
            data={campaign_report}
            xKey="campaign_id"
            bars={[{ key: 'viewable_rate', color: CHART_COLORS[0], name: 'Viewable Rate' }]}
          />
        </ChartCard>

        <ChartCard title="Viewable Rate by Device" subtitle="Device-level viewability">
          <BarChartComponent
            data={device_breakdown}
            xKey="device_type"
            bars={[{ key: 'viewable_rate', color: CHART_COLORS[1], name: 'Viewable Rate' }]}
          />
        </ChartCard>
      </div>

      {/* Viewability Trend Control Chart */}
      <ChartCard title="Viewability Trend" subtitle="Statistical process control chart with UCL/LCL bounds">
        <ControlChartComponent data={controlChartData} />
      </ChartCard>

      {/* Publisher Scorecard */}
      <ChartCard title="Publisher Scorecard" subtitle="Publisher quality ranking by viewability metrics">
        <DataTable columns={publisherColumns} data={publisher_scorecard} />
      </ChartCard>
    </div>
  );
}
