import { useQuery } from '@tanstack/react-query';
import { fetchCampaigns } from '../api/endpoints';
import { useFilters } from './useFilters';

export function useCampaigns() {
  const { filters } = useFilters();

  return useQuery({
    queryKey: ['campaigns', filters],
    queryFn: () => fetchCampaigns(filters),
    staleTime: 5 * 60 * 1000,
    enabled: !!filters.start_date,
  });
}
