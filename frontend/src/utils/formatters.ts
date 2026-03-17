export function formatNumber(n: number, decimals: number = 0): string {
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`;
  if (n >= 1_000) return `${(n / 1_000).toFixed(1)}K`;
  return n.toFixed(decimals);
}

export function formatCurrency(n: number, decimals: number = 2): string {
  return `$${n.toFixed(decimals)}`;
}

export function formatPercent(n: number, decimals: number = 1): string {
  return `${(n * 100).toFixed(decimals)}%`;
}

export function formatCompact(n: number): string {
  return new Intl.NumberFormat('en-US', { notation: 'compact' }).format(n);
}
