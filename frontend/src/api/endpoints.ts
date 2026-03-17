import client from './client';
import type {
  FilterParams,
  FilterOptions,
  OverviewData,
  CampaignData,
  ViewabilityData,
  SegmentationData,
  AnomalyData,
  AttributionData,
  ABTestData,
  FrequencyData,
} from '../types';

function buildParams(filters: FilterParams): URLSearchParams {
  const params = new URLSearchParams();
  if (filters.start_date) params.append('start_date', filters.start_date);
  if (filters.end_date) params.append('end_date', filters.end_date);
  if (filters.campaigns) {
    filters.campaigns.forEach(c => params.append('campaigns', c));
  }
  if (filters.device_types) {
    filters.device_types.forEach(d => params.append('device_types', d));
  }
  return params;
}

export async function fetchFilters(): Promise<FilterOptions> {
  const { data } = await client.get('/filters');
  return data;
}

export async function fetchOverview(filters: FilterParams): Promise<OverviewData> {
  const { data } = await client.get('/overview', { params: buildParams(filters) });
  return data;
}

export async function fetchCampaigns(filters: FilterParams): Promise<CampaignData> {
  const { data } = await client.get('/campaigns', { params: buildParams(filters) });
  return data;
}

export async function fetchViewability(filters: FilterParams): Promise<ViewabilityData> {
  const { data } = await client.get('/viewability', { params: buildParams(filters) });
  return data;
}

export async function fetchSegmentation(filters: FilterParams, k: number = 4): Promise<SegmentationData> {
  const params = buildParams(filters);
  params.append('k', k.toString());
  const { data } = await client.get('/segmentation', { params });
  return data;
}

export async function fetchAnomalies(
  filters: FilterParams,
  contamination: number = 0.05,
  metric: string = 'clearing_price_cpm'
): Promise<AnomalyData> {
  const params = buildParams(filters);
  params.append('contamination', contamination.toString());
  params.append('metric', metric);
  const { data } = await client.get('/anomalies', { params });
  return data;
}

export async function fetchAttribution(filters: FilterParams, halfLifeDays: number = 7): Promise<AttributionData> {
  const params = buildParams(filters);
  params.append('half_life_days', halfLifeDays.toString());
  const { data } = await client.get('/attribution', { params });
  return data;
}

export async function fetchABTesting(
  campaignId: string,
  controlCreative: string,
  treatmentCreative: string,
  metric: string = 'view_completion_pct',
  filters: FilterParams = {}
): Promise<ABTestData> {
  const params = buildParams(filters);
  params.append('campaign_id', campaignId);
  params.append('control_creative', controlCreative);
  params.append('treatment_creative', treatmentCreative);
  params.append('metric', metric);
  const { data } = await client.get('/ab-testing', { params });
  return data;
}

export async function fetchFrequency(filters: FilterParams, campaignId?: string): Promise<FrequencyData> {
  const params = buildParams(filters);
  if (campaignId) params.append('campaign_id', campaignId);
  const { data } = await client.get('/frequency', { params });
  return data;
}
