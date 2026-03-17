import { useQuery } from '@tanstack/react-query';
import { fetchAnomalies } from '../api/endpoints';
import { useFilters } from './useFilters';
import type { AnomalyData } from '../types';

export function useAnomalies(contamination: number = 0.05, metric: string = 'clearing_price_cpm') {
  const { filters } = useFilters();

  return useQuery<AnomalyData>({
    queryKey: ['anomalies', filters, contamination, metric],
    queryFn: () => fetchAnomalies(filters, contamination, metric),
    enabled: !!filters.start_date,
    staleTime: 5 * 60 * 1000,
  });
}
