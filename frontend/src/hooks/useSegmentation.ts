import { useQuery } from '@tanstack/react-query';
import { fetchSegmentation } from '../api/endpoints';
import { useFilters } from './useFilters';

export function useSegmentation(k: number = 4) {
  const { filters } = useFilters();

  return useQuery({
    queryKey: ['segmentation', filters, k],
    queryFn: () => fetchSegmentation(filters, k),
    staleTime: 5 * 60 * 1000,
    enabled: !!filters.start_date,
  });
}
