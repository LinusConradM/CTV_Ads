import { useState } from 'react';
import { Users, UserCheck, Crown, TrendingUp } from 'lucide-react';
import { useSegmentation } from '../hooks/useSegmentation';
import KPICard from '../components/ui/KPICard';
import ChartCard from '../components/ui/ChartCard';
import DataTable from '../components/ui/DataTable';
import LoadingSpinner from '../components/ui/LoadingSpinner';
import EmptyState from '../components/ui/EmptyState';
import AreaLineChart from '../components/charts/AreaLineChart';
import BarChartComponent from '../components/charts/BarChartComponent';
import ScatterChartComponent from '../components/charts/ScatterChartComponent';
import { formatCompact, formatCurrency, formatPercent, formatNumber } from '../utils/formatters';
import { CHART_COLORS } from '../utils/colors';

const valueColumns = [
  { key: 'segment', label: 'Segment', format: (v: number) => `Segment ${v}` },
  { key: 'users', label: 'Users', format: (v: number) => formatCompact(v) },
  { key: 'avg_impressions', label: 'Avg Impressions', format: (v: number) => formatNumber(v, 0) },
  { key: 'avg_cpm', label: 'Avg CPM', format: (v: number) => formatCurrency(v) },
  { key: 'conversion_rate', label: 'Conv Rate', format: (v: number) => formatPercent(v) },
  { key: 'avg_completion', label: 'Avg Completion', format: (v: number) => formatPercent(v) },
  { key: 'reach_share', label: 'Reach Share', format: (v: number) => formatPercent(v) },
];

export default function AudienceSegments() {
  const [k, setK] = useState(4);
  const { data, isLoading, isError } = useSegmentation(k);

  if (isLoading) return <LoadingSpinner />;
  if (isError || !data) return <EmptyState title="Failed to load" message="Unable to load segmentation data. Please try again." />;

  const { kpis, elbow_curve, pca_projection, value_analysis } = data;

  // Prepare bar chart data with segment labels
  const convBySegment = value_analysis.map((s) => ({
    segment: `Seg ${s.segment}`,
    conversion_rate: s.conversion_rate,
  }));

  const cpmBySegment = value_analysis.map((s) => ({
    segment: `Seg ${s.segment}`,
    avg_cpm: s.avg_cpm,
  }));

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-100">Audience Segments</h1>
          <p className="mt-1 text-sm text-slate-400">K-Means clustering with PCA visualization and segment value analysis</p>
        </div>

        {/* K Selector */}
        <div className="flex items-center gap-3">
          <label htmlFor="k-select" className="text-sm font-medium text-slate-300">
            Clusters (K):
          </label>
          <select
            id="k-select"
            value={k}
            onChange={(e) => setK(Number(e.target.value))}
            className="bg-slate-800 border border-slate-700 text-slate-200 text-sm rounded-lg px-3 py-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
          >
            {[2, 3, 4, 5, 6, 7, 8].map((val) => (
              <option key={val} value={val}>
                {val}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <KPICard
          title="Segments"
          value={kpis.num_segments}
          icon={Users}
          color="blue"
        />
        <KPICard
          title="Total Users"
          value={formatCompact(kpis.total_users)}
          icon={UserCheck}
          color="green"
        />
        <KPICard
          title="Largest Segment"
          value={formatCompact(kpis.largest_segment_size)}
          icon={Crown}
          color="amber"
        />
        <KPICard
          title="Best Conv Rate"
          value={formatPercent(kpis.best_conversion_rate)}
          icon={TrendingUp}
          color="rose"
        />
      </div>

      {/* Row 1: Elbow Curve + Silhouette Score */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <ChartCard title="Elbow Curve" subtitle="Inertia by number of clusters">
          <AreaLineChart
            data={elbow_curve}
            xKey="k"
            lines={[{ key: 'inertia', color: CHART_COLORS[0], name: 'Inertia' }]}
          />
        </ChartCard>

        <ChartCard title="Silhouette Score" subtitle="Cluster quality by K">
          <AreaLineChart
            data={elbow_curve}
            xKey="k"
            lines={[{ key: 'silhouette_score', color: CHART_COLORS[1], name: 'Silhouette Score' }]}
          />
        </ChartCard>
      </div>

      {/* PCA Scatter Plot */}
      <ChartCard title="PCA Projection" subtitle="2D visualization of audience segments">
        <ScatterChartComponent
          data={pca_projection}
          xKey="pc1"
          yKey="pc2"
          colorKey="segment"
          height={400}
        />
      </ChartCard>

      {/* Row 2: Conv Rate + CPM by Segment */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <ChartCard title="Conversion Rate by Segment" subtitle="Which segments convert best">
          <BarChartComponent
            data={convBySegment}
            xKey="segment"
            bars={[{ key: 'conversion_rate', color: CHART_COLORS[1], name: 'Conv Rate' }]}
          />
        </ChartCard>

        <ChartCard title="Avg CPM by Segment" subtitle="Cost efficiency per segment">
          <BarChartComponent
            data={cpmBySegment}
            xKey="segment"
            bars={[{ key: 'avg_cpm', color: CHART_COLORS[2], name: 'Avg CPM' }]}
          />
        </ChartCard>
      </div>

      {/* Value Analysis Table */}
      <ChartCard title="Segment Value Analysis" subtitle="Detailed metrics for each audience segment">
        <DataTable columns={valueColumns} data={value_analysis} />
      </ChartCard>
    </div>
  );
}
