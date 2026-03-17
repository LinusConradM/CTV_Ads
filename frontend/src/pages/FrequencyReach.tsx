import { useState } from 'react';
import { Users, Repeat, Hash, TrendingUp, Shield } from 'lucide-react';
import KPICard from '../components/ui/KPICard';
import ChartCard from '../components/ui/ChartCard';
import LoadingSpinner from '../components/ui/LoadingSpinner';
import AreaLineChart from '../components/charts/AreaLineChart';
import BarChartComponent from '../components/charts/BarChartComponent';
import { useFrequency } from '../hooks/useFrequency';
import { useFilters } from '../hooks/useFilters';
import { formatCompact } from '../utils/formatters';

export default function FrequencyReach() {
  const { options } = useFilters();
  const [campaignId, setCampaignId] = useState<string | undefined>(undefined);

  const { data, isLoading, error } = useFrequency(campaignId);

  if (isLoading) return <LoadingSpinner />;
  if (error) {
    return (
      <div className="flex items-center justify-center h-64 text-rose-400">
        Failed to load frequency data. Please try again.
      </div>
    );
  }
  if (!data) return null;

  const { kpis, reach_curve, frequency_distribution, optimal_frequency, diminishing_returns, cap_recommendation } = data;

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-100">Frequency & Reach</h1>
          <p className="mt-1 text-sm text-slate-400">
            Frequency distribution, reach curves, and cap recommendations
          </p>
        </div>

        {/* Controls */}
        <div className="flex items-center gap-3">
          <select
            value={campaignId ?? ''}
            onChange={(e) => setCampaignId(e.target.value || undefined)}
            className="bg-slate-700 border border-slate-600 text-slate-200 rounded-lg px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">All Campaigns</option>
            {options?.campaigns.map((c) => (
              <option key={c} value={c}>
                {c}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* KPI Row */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-4">
        <KPICard
          title="Total Reach"
          value={formatCompact(kpis.total_reach)}
          icon={Users}
          color="blue"
        />
        <KPICard
          title="Avg Frequency"
          value={kpis.avg_frequency.toFixed(1)}
          icon={Repeat}
          color="green"
        />
        <KPICard
          title="Median Frequency"
          value={kpis.median_frequency.toFixed(1)}
          icon={Hash}
          color="amber"
        />
        <KPICard
          title="Max Frequency"
          value={kpis.max_frequency}
          icon={TrendingUp}
          color="rose"
        />
        <KPICard
          title="Recommended Cap"
          value={kpis.recommended_cap_conv ?? 'N/A'}
          icon={Shield}
          color="blue"
        />
      </div>

      {/* Row 1: Reach Curve + Frequency Distribution */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <ChartCard title="Reach Curve" subtitle="Unique reach by impressions served">
          <AreaLineChart
            data={reach_curve}
            xKey="impressions_served"
            lines={[{ key: 'unique_reach', name: 'Unique Reach', color: '#3b82f6' }]}
            areaFill
          />
        </ChartCard>

        <ChartCard title="Frequency Distribution" subtitle="Users by exposure frequency">
          <BarChartComponent
            data={frequency_distribution}
            xKey="frequency_bucket"
            bars={[{ key: 'user_count', name: 'Users', color: '#3b82f6' }]}
          />
        </ChartCard>
      </div>

      {/* Row 2: Conversion Rate + Diminishing Returns */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <ChartCard
          title="Conversion Rate by Frequency"
          subtitle="Identifying optimal exposure frequency"
        >
          <BarChartComponent
            data={optimal_frequency}
            xKey="freq_bucket"
            bars={[{ key: 'conversion_rate', name: 'Conversion Rate', color: '#10b981' }]}
          />
        </ChartCard>

        <ChartCard title="Diminishing Returns" subtitle="Marginal reach rate by impressions">
          <AreaLineChart
            data={diminishing_returns}
            xKey="impressions"
            lines={[{ key: 'marginal_reach_rate', name: 'Marginal Reach Rate', color: '#f59e0b' }]}
          />
        </ChartCard>
      </div>

      {/* Cap Recommendations */}
      <div>
        <h2 className="text-lg font-semibold text-slate-200 mb-3">Cap Recommendations</h2>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          {/* Conversion Optimization */}
          <div className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-5">
            <h3 className="text-sm font-semibold text-emerald-400 mb-3">
              Conversion Optimization
            </h3>
            <div className="space-y-3">
              <div>
                <p className="text-xs text-slate-400 mb-1">Recommended Cap</p>
                <p className="text-3xl font-bold text-slate-100">
                  {cap_recommendation.conversions.recommended_cap ?? 'N/A'}
                </p>
              </div>
              <p className="text-sm text-slate-400 leading-relaxed">
                {cap_recommendation.conversions.reason}
              </p>
            </div>
          </div>

          {/* Reach Optimization */}
          <div className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-5">
            <h3 className="text-sm font-semibold text-blue-400 mb-3">Reach Optimization</h3>
            <div className="space-y-3">
              <div>
                <p className="text-xs text-slate-400 mb-1">Recommended Cap</p>
                <p className="text-3xl font-bold text-slate-100">
                  {cap_recommendation.reach.recommended_cap ?? 'N/A'}
                </p>
              </div>
              <p className="text-sm text-slate-400 leading-relaxed">
                {cap_recommendation.reach.reason}
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
