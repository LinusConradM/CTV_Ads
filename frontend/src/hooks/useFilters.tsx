import { createContext, useContext, useState, useEffect, type ReactNode } from 'react';
import { fetchFilters } from '../api/endpoints';
import type { FilterOptions, FilterParams } from '../types';

interface FilterContextType {
  filters: FilterParams;
  options: FilterOptions | null;
  setFilters: (filters: FilterParams) => void;
  isLoading: boolean;
}

const FilterContext = createContext<FilterContextType | null>(null);

export function FilterProvider({ children }: { children: ReactNode }) {
  const [options, setOptions] = useState<FilterOptions | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [filters, setFilters] = useState<FilterParams>({});

  useEffect(() => {
    fetchFilters()
      .then((data) => {
        setOptions(data);
        setFilters({
          start_date: data.date_range.min,
          end_date: data.date_range.max,
        });
        setIsLoading(false);
      })
      .catch(() => setIsLoading(false));
  }, []);

  return (
    <FilterContext.Provider value={{ filters, options, setFilters, isLoading }}>
      {children}
    </FilterContext.Provider>
  );
}

export function useFilters() {
  const context = useContext(FilterContext);
  if (!context) throw new Error('useFilters must be used within FilterProvider');
  return context;
}
