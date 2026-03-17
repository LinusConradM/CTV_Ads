import { useQuery } from '@tanstack/react-query';
import { fetchOverview } from '../api/endpoints';
import { useFilters } from './useFilters';

export function useOverview() {
  const { filters } = useFilters();

  return useQuery({
    queryKey: ['overview', filters],
    queryFn: () => fetchOverview(filters),
    staleTime: 5 * 60 * 1000,
    enabled: !!filters.start_date,
  });
}
