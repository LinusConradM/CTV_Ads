import { useMemo } from 'react';
import {
  ResponsiveContainer,
  ScatterChart,
  Scatter,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
} from 'recharts';
import { CHART_COLORS, DARK_THEME } from '../../utils/colors';

interface ScatterChartComponentProps {
  data: any[];
  xKey: string;
  yKey: string;
  colorKey?: string;
  height?: number;
  colors?: string[];
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

export default function ScatterChartComponent({
  data,
  xKey,
  yKey,
  colorKey,
  height = 300,
  colors = CHART_COLORS,
}: ScatterChartComponentProps) {
  const groups = useMemo(() => {
    if (!colorKey) {
      return [{ name: 'All', data }];
    }

    const grouped = new Map<string, Record<string, unknown>[]>();
    for (const point of data) {
      const groupValue = String(point[colorKey] ?? 'Unknown');
      if (!grouped.has(groupValue)) {
        grouped.set(groupValue, []);
      }
      grouped.get(groupValue)!.push(point);
    }

    return Array.from(grouped.entries()).map(([name, points]) => ({
      name,
      data: points,
    }));
  }, [data, colorKey]);

  return (
    <ResponsiveContainer width="100%" height={height}>
      <ScatterChart>
        <CartesianGrid
          stroke={DARK_THEME.gridStroke}
          strokeDasharray="3 3"
        />
        <XAxis
          dataKey={xKey}
          type="number"
          name={xKey}
          tick={axisTickStyle}
          axisLine={{ stroke: DARK_THEME.border }}
          tickLine={{ stroke: DARK_THEME.border }}
        />
        <YAxis
          dataKey={yKey}
          type="number"
          name={yKey}
          tick={axisTickStyle}
          axisLine={{ stroke: DARK_THEME.border }}
          tickLine={{ stroke: DARK_THEME.border }}
        />
        <Tooltip
          contentStyle={tooltipStyle}
          labelStyle={{ color: DARK_THEME.textPrimary }}
          itemStyle={{ color: DARK_THEME.textPrimary }}
          cursor={{ strokeDasharray: '3 3', stroke: DARK_THEME.textSecondary }}
        />
        {groups.map((group, index) => (
          <Scatter
            key={group.name}
            name={group.name}
            data={group.data}
            fill={colors[index % colors.length]}
            opacity={0.8}
          />
        ))}
      </ScatterChart>
    </ResponsiveContainer>
  );
}
