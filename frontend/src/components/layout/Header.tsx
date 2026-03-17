import { Calendar, Filter } from 'lucide-react';
import { useFilters } from '../../hooks/useFilters';

interface HeaderProps {
  title: string;
}

export default function Header({ title }: HeaderProps) {
  const { filters, options } = useFilters();

  const campaignCount = options?.campaigns?.length ?? 0;
  const deviceCount = options?.device_types?.length ?? 0;

  const formatDate = (dateStr?: string) => {
    if (!dateStr) return '';
    try {
      return new Date(dateStr).toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
        year: 'numeric',
      });
    } catch {
      return dateStr;
    }
  };

  return (
    <header className="sticky top-0 z-10 bg-slate-900/95 backdrop-blur border-b border-slate-700/50 px-6 py-3">
      <div className="flex items-center justify-between">
        {/* Page Title */}
        <h1 className="text-xl font-semibold text-slate-100">{title}</h1>

        {/* Right Section */}
        <div className="flex items-center gap-4">
          {/* Filter Summary */}
          {options && (
            <div className="flex items-center gap-2 text-sm text-slate-400">
              <Filter className="w-4 h-4" />
              <span>
                {campaignCount} campaign{campaignCount !== 1 ? 's' : ''}
                {', '}
                {deviceCount} device{deviceCount !== 1 ? 's' : ''}
              </span>
            </div>
          )}

          {/* Date Range */}
          {filters.start_date && filters.end_date && (
            <div className="flex items-center gap-2 rounded-lg bg-slate-800 border border-slate-700/50 px-3 py-1.5 text-sm text-slate-300">
              <Calendar className="w-4 h-4 text-slate-400" />
              <span>
                {formatDate(filters.start_date)} &ndash;{' '}
                {formatDate(filters.end_date)}
              </span>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}
