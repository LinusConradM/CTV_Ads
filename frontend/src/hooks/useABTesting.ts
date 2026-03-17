import { useQuery } from '@tanstack/react-query';
import { fetchABTesting } from '../api/endpoints';
import { useFilters } from './useFilters';
import type { ABTestData } from '../types';

export function useABTesting(
  campaignId: string,
  controlCreative: string,
  treatmentCreative: string,
  metric: string = 'view_completion_pct'
) {
  const { filters } = useFilters();

  return useQuery<ABTestData>({
    queryKey: ['ab-testing', campaignId, controlCreative, treatmentCreative, metric, filters],
    queryFn: () => fetchABTesting(campaignId, controlCreative, treatmentCreative, metric, filters),
    enabled: !!campaignId && !!controlCreative && !!treatmentCreative && !!filters.start_date,
    staleTime: 5 * 60 * 1000,
  });
}
