import { useQuery } from '@tanstack/react-query';
import { fetchAttribution } from '../api/endpoints';
import { useFilters } from './useFilters';
import type { AttributionData } from '../types';

export function useAttribution(halfLifeDays: number = 7) {
  const { filters } = useFilters();

  return useQuery<AttributionData>({
    queryKey: ['attribution', filters, halfLifeDays],
    queryFn: () => fetchAttribution(filters, halfLifeDays),
    enabled: !!filters.start_date,
  });
}
