import { useMemo } from 'react';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  Legend,
} from 'recharts';
import { CHART_COLORS, DARK_THEME } from '../../utils/colors';

interface BinData {
  bin_start: number;
  bin_end: number;
  count: number;
}

interface HistogramChartProps {
  data: BinData[];
  height?: number;
  color?: string;
  secondaryData?: BinData[];
  secondaryColor?: string;
}

const tooltipStyle = {
  backgroundColor: '#1e293b',
  border: '1px solid #334155',
  borderRadius: '8px',
  color: '#f1f5f9',
};

const axisTickStyle = {
  fill: DARK_THEME.textSecondary,
  fontSize: 12,
};

export default function HistogramChart({
  data,
  height = 300,
  color = CHART_COLORS[0],
  secondaryData,
  secondaryColor = CHART_COLORS[3],
}: HistogramChartProps) {
  const chartData = useMemo(() => {
    const binMap = new Map<string, { label: string; primary: number; secondary: number }>();

    for (const bin of data) {
      const label = String(bin.bin_start);
      binMap.set(label, {
        label,
        primary: bin.count,
        secondary: 0,
      });
    }

    if (secondaryData) {
      for (const bin of secondaryData) {
        const label = String(bin.bin_start);
        const existing = binMap.get(label);
        if (existing) {
          existing.secondary = bin.count;
        } else {
          binMap.set(label, {
            label,
            primary: 0,
            secondary: bin.count,
          });
        }
      }
    }

    return Array.from(binMap.values()).sort(
      (a, b) => Number(a.label) - Number(b.label)
    );
  }, [data, secondaryData]);

  const hasSecondary = secondaryData && secondaryData.length > 0;

  return (
    <ResponsiveContainer width="100%" height={height}>
      <BarChart data={chartData} barCategoryGap="2%">
        <CartesianGrid
          stroke={DARK_THEME.gridStroke}
          strokeDasharray="3 3"
        />
        <XAxis
          dataKey="label"
          tick={axisTickStyle}
          axisLine={{ stroke: DARK_THEME.border }}
          tickLine={{ stroke: DARK_THEME.border }}
        />
        <YAxis
          tick={axisTickStyle}
          axisLine={{ stroke: DARK_THEME.border }}
          tickLine={{ stroke: DARK_THEME.border }}
        />
        <Tooltip
          contentStyle={tooltipStyle}
          labelStyle={{ color: DARK_THEME.textPrimary }}
          itemStyle={{ color: DARK_THEME.textPrimary }}
          cursor={{ fill: 'rgba(148, 163, 184, 0.1)' }}
        />
        {hasSecondary && <Legend wrapperStyle={{ color: DARK_THEME.textSecondary }} />}
        <Bar
          dataKey="primary"
          name="Primary"
          fill={color}
          opacity={hasSecondary ? 0.7 : 1}
          radius={[4, 4, 0, 0]}
        />
        {hasSecondary && (
          <Bar
            dataKey="secondary"
            name="Secondary"
            fill={secondaryColor}
            opacity={0.7}
            radius={[4, 4, 0, 0]}
          />
        )}
      </BarChart>
    </ResponsiveContainer>
  );
}
