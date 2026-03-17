import { type LucideIcon, TrendingUp, TrendingDown } from 'lucide-react';

const colorMap = {
  blue: {
    bg: 'bg-blue-500/10',
    text: 'text-blue-400',
    ring: 'ring-blue-500/20',
  },
  green: {
    bg: 'bg-emerald-500/10',
    text: 'text-emerald-400',
    ring: 'ring-emerald-500/20',
  },
  amber: {
    bg: 'bg-amber-500/10',
    text: 'text-amber-400',
    ring: 'ring-amber-500/20',
  },
  rose: {
    bg: 'bg-rose-500/10',
    text: 'text-rose-400',
    ring: 'ring-rose-500/20',
  },
} as const;

interface KPICardProps {
  title: string;
  value: string | number;
  change?: number;
  icon?: LucideIcon;
  color?: keyof typeof colorMap;
}

export default function KPICard({
  title,
  value,
  change,
  icon: Icon,
  color = 'blue',
}: KPICardProps) {
  const palette = colorMap[color];
  const isPositive = change !== undefined && change >= 0;

  return (
    <div className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-5 hover:border-slate-600/50 transition-all">
      <div className="flex items-start justify-between">
        <div className="space-y-2">
          <p className="text-sm font-medium text-slate-400">{title}</p>
          <p className="text-2xl font-bold text-slate-100">{value}</p>
        </div>
        {Icon && (
          <div
            className={`flex items-center justify-center w-10 h-10 rounded-full ${palette.bg} ring-1 ${palette.ring}`}
          >
            <Icon className={`w-5 h-5 ${palette.text}`} />
          </div>
        )}
      </div>

      {change !== undefined && (
        <div className="mt-3 flex items-center gap-1.5">
          {isPositive ? (
            <TrendingUp className="w-4 h-4 text-emerald-400" />
          ) : (
            <TrendingDown className="w-4 h-4 text-rose-400" />
          )}
          <span
            className={`text-sm font-medium ${
              isPositive ? 'text-emerald-400' : 'text-rose-400'
            }`}
          >
            {isPositive ? '+' : ''}
            {change.toFixed(1)}%
          </span>
          <span className="text-xs text-slate-500">vs prior period</span>
        </div>
      )}
    </div>
  );
}
