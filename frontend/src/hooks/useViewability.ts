import { useQuery } from '@tanstack/react-query';
import { fetchViewability } from '../api/endpoints';
import { useFilters } from './useFilters';

export function useViewability() {
  const { filters } = useFilters();

  return useQuery({
    queryKey: ['viewability', filters],
    queryFn: () => fetchViewability(filters),
    staleTime: 5 * 60 * 1000,
    enabled: !!filters.start_date,
  });
}
