// Filter types
export interface FilterParams {
  start_date?: string;
  end_date?: string;
  campaigns?: string[];
  device_types?: string[];
}

export interface FilterOptions {
  campaigns: string[];
  device_types: string[];
  creative_ids: string[];
  date_range: { min: string; max: string };
  campaign_creatives: Record<string, string[]>;
}

// Overview
export interface OverviewKPIs {
  total_impressions: number;
  unique_reach: number;
  avg_frequency: number;
  avg_cpm: number;
  viewable_rate: number;
  conversion_rate: number;
}

export interface DailyTrend {
  report_date: string;
  impressions: number;
  avg_cpm: number;
  viewable_rate: number;
  conversions: number;
}

export interface CampaignSummary {
  campaign_id: string;
  impressions: number;
  avg_cpm: number;
  viewable_rate: number;
  conversion_rate: number;
  unique_reach: number;
}

export interface OverviewData {
  kpis: OverviewKPIs;
  daily_trend: DailyTrend[];
  campaign_summary: CampaignSummary[];
}

// Campaign
export interface CampaignKPIs {
  total_impressions: number;
  unique_reach: number;
  avg_frequency: number;
  avg_cpm: number;
  viewable_rate: number;
  completion_rate: number;
}

export interface CampaignPerformance {
  campaign_id: string;
  impressions: number;
  unique_reach: number;
  avg_cpm: number;
  viewable_rate: number;
  completion_rate: number;
  conversion_rate: number;
  total_spend: number;
  frequency: number;
}

export interface CPMTrend {
  report_date: string;
  avg_cpm: number;
  impressions: number;
}

export interface DeviceBreakdown {
  device_type: string;
  impressions: number;
  avg_cpm: number;
  viewable_rate: number;
}

export interface CategoryBreakdown {
  content_category: string;
  impressions: number;
  avg_cpm: number;
}

export interface DMAData {
  dma_name: string;
  impressions: number;
  avg_cpm: number;
}

export interface CampaignData {
  kpis: CampaignKPIs;
  performance_table: CampaignPerformance[];
  cpm_trend: CPMTrend[];
  device_breakdown: DeviceBreakdown[];
  category_breakdown: CategoryBreakdown[];
  top_dmas: DMAData[];
}

// Viewability
export interface ViewabilityKPIs {
  viewable_rate: number;
  video_viewable_rate: number;
  display_viewable_rate: number;
  avg_pixel_visibility: number;
  avg_view_duration: number;
}

export interface ViewabilityCampaignReport {
  campaign_id: string;
  total_impressions: number;
  viewable_impressions: number;
  avg_pixel_visibility: number;
  avg_view_duration: number;
  avg_completion_pct: number;
  viewable_rate: number;
}

export interface ViewabilityTrend {
  report_date: string;
  impressions: number;
  viewable_rate: number;
  avg_pixel_visibility: number;
  ucl: number;
  lcl: number;
  mean_line: number;
  out_of_control: boolean;
}

export interface PublisherScorecard {
  publisher_id: string;
  impressions: number;
  viewable_rate: number;
  avg_pixel_visibility: number;
  avg_cpm: number;
  rank: number;
}

export interface ViewabilityData {
  kpis: ViewabilityKPIs;
  distribution: Record<string, any>;
  campaign_report: ViewabilityCampaignReport[];
  device_breakdown: any[];
  publisher_scorecard: PublisherScorecard[];
  trend: ViewabilityTrend[];
}

// Segmentation
export interface SegmentationKPIs {
  num_segments: number;
  total_users: number;
  largest_segment_size: number;
  best_conversion_rate: number;
}

export interface ElbowPoint {
  k: number;
  inertia: number;
  silhouette_score: number;
}

export interface PCAPoint {
  pc1: number;
  pc2: number;
  segment: number;
  user_id_hashed: string;
}

export interface SegmentValue {
  segment: number;
  users: number;
  avg_impressions: number;
  avg_cpm: number;
  conversion_rate: number;
  avg_completion: number;
  reach_share: number;
}

export interface SegmentationData {
  kpis: SegmentationKPIs;
  elbow_curve: ElbowPoint[];
  pca_projection: PCAPoint[];
  value_analysis: SegmentValue[];
}

// Anomaly
export interface AnomalyKPIs {
  anomaly_rate: number;
  anomalies_flagged: number;
  flagged_campaigns: number;
  bot_traffic_rate: number;
}

export interface AnomalyCategory {
  category: string;
  count: number;
  pct_of_anomalies: number;
}

export interface ControlChartPoint {
  report_date: string;
  value: number;
  n: number;
  mean_line: number;
  ucl: number;
  lcl: number;
  out_of_control: boolean;
}

export interface HistogramBin {
  bin_start: number;
  bin_end: number;
  count: number;
}

export interface FlaggedRecord {
  impression_id: string;
  campaign_id: string;
  device_type: string;
  clearing_price_cpm: number;
  pixels_visible_pct: number;
  view_duration_seconds: number;
  user_campaign_frequency: number;
  anomaly_score: number;
}

export interface AnomalyData {
  kpis: AnomalyKPIs;
  summary: AnomalyCategory[];
  control_chart: ControlChartPoint[];
  flagged_records: FlaggedRecord[];
  score_distribution: HistogramBin[];
}

// Attribution
export interface AttributionKPIs {
  total_conversions: number;
  avg_path_length: number;
  campaigns_credited: number;
  total_spend: number;
}

export interface AttributionComparison {
  campaign_id: string;
  last_touch: number;
  first_touch: number;
  linear: number;
  time_decay: number;
  total_spend: number;
}

export interface AttributionData {
  kpis: AttributionKPIs;
  comparison: AttributionComparison[];
  path_stats: { total_paths: number; avg_path_length: number; max_path_length: number };
}

// A/B Testing
export interface ABTestKPIs {
  control_mean: number;
  treatment_mean: number;
  effect_size: number;
  p_value: number;
  significant: boolean;
  is_powered: boolean;
}

export interface TTestResult {
  t_stat: number;
  p_value: number;
  significant: boolean;
  control_mean: number;
  treatment_mean: number;
  effect_size: number;
  relative_lift: number;
  ci_95: [number, number];
}

export interface PowerAnalysis {
  min_sample_size_per_group: number;
  mde: number;
  pooled_std: number;
  alpha: number;
  power: number;
  current_n_control: number;
  current_n_treatment: number;
  is_sufficiently_powered: boolean;
}

export interface BootstrapCI {
  mean_diff: number;
  ci_lower: number;
  ci_upper: number;
  ci_level: number;
  n_iterations: number;
  significant: boolean;
}

export interface SequentialLook {
  look: number;
  n_per_group: number;
  info_fraction: number;
  z_stat: number;
  z_boundary: number;
  reject_null: boolean;
}

export interface SequentialTest {
  alpha_spending: string;
  n_looks: number;
  looks: SequentialLook[];
  early_stop: boolean;
}

export interface ABTestData {
  kpis: ABTestKPIs;
  ttest: TTestResult;
  power_analysis: PowerAnalysis;
  bootstrap: BootstrapCI;
  sequential_test: SequentialTest;
  control_distribution: HistogramBin[];
  treatment_distribution: HistogramBin[];
}

// Frequency
export interface FrequencyKPIs {
  total_reach: number;
  avg_frequency: number;
  median_frequency: number;
  max_frequency: number;
  recommended_cap_conv: number | null;
  recommended_cap_reach: number | null;
}

export interface ReachPoint {
  impressions_served: number;
  unique_reach: number;
  reach_pct: number;
}

export interface FrequencyBucket {
  frequency_bucket: string;
  user_count: number;
  pct_of_users: number;
}

export interface OptimalFrequency {
  freq_bucket: string;
  users: number;
  conversions: number;
  conversion_rate: number;
  is_optimal?: boolean;
}

export interface DiminishingReturn {
  impressions: number;
  cumulative_reach: number;
  incremental_reach: number;
  incremental_impressions: number;
  marginal_reach_rate: number;
}

export interface CapRecommendation {
  recommended_cap: number | null;
  objective: string;
  reason: string;
  [key: string]: any;
}

export interface FrequencyData {
  kpis: FrequencyKPIs;
  reach_curve: ReachPoint[];
  frequency_distribution: FrequencyBucket[];
  optimal_frequency: OptimalFrequency[];
  diminishing_returns: DiminishingReturn[];
  cap_recommendation: {
    conversions: CapRecommendation;
    reach: CapRecommendation;
  };
}
