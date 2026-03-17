import { type LucideIcon, Inbox } from 'lucide-react';

interface EmptyStateProps {
  icon?: LucideIcon;
  title?: string;
  message?: string;
}

export default function EmptyState({
  icon: Icon = Inbox,
  title = 'No data found',
  message = 'There is nothing to display at the moment. Try adjusting your filters or check back later.',
}: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center py-20 text-center">
      <div className="flex items-center justify-center w-14 h-14 rounded-full bg-slate-800 ring-1 ring-slate-700/50 mb-4">
        <Icon className="w-7 h-7 text-slate-500" />
      </div>
      <h3 className="text-base font-semibold text-slate-300">{title}</h3>
      <p className="mt-1.5 max-w-sm text-sm text-slate-500">{message}</p>
    </div>
  );
}
