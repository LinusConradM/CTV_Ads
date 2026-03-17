import { useQuery } from '@tanstack/react-query';
import { fetchFrequency } from '../api/endpoints';
import { useFilters } from './useFilters';
import type { FrequencyData } from '../types';

export function useFrequency(campaignId?: string) {
  const { filters } = useFilters();

  return useQuery<FrequencyData>({
    queryKey: ['frequency', filters, campaignId],
    queryFn: () => fetchFrequency(filters, campaignId),
    enabled: !!filters.start_date,
  });
}
