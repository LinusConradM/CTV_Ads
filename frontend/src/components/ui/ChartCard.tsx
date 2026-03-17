import type { ReactNode } from 'react';

interface ChartCardProps {
  title: string;
  subtitle?: string;
  children: ReactNode;
  loading?: boolean;
  className?: string;
}

export default function ChartCard({
  title,
  subtitle,
  children,
  loading = false,
  className = '',
}: ChartCardProps) {
  return (
    <div
      className={`bg-slate-800/50 border border-slate-700/50 rounded-xl p-5 hover:border-slate-600/50 transition-all ${className}`}
    >
      {/* Header */}
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-slate-200">{title}</h3>
        {subtitle && (
          <p className="mt-0.5 text-xs text-slate-400">{subtitle}</p>
        )}
      </div>

      {/* Content */}
      {loading ? (
        <div className="space-y-3 animate-pulse">
          <div className="h-4 bg-slate-700/50 rounded w-3/4" />
          <div className="h-48 bg-slate-700/30 rounded-lg" />
          <div className="h-4 bg-slate-700/50 rounded w-1/2" />
        </div>
      ) : (
        <div>{children}</div>
      )}
    </div>
  );
}
