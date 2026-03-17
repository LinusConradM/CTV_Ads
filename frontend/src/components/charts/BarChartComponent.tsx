import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
} from 'recharts';
import { CHART_COLORS, DARK_THEME } from '../../utils/colors';

interface BarConfig {
  key: string;
  color?: string;
  name?: string;
  stackId?: string;
}

interface BarChartComponentProps {
  data: any[];
  xKey: string;
  bars: BarConfig[];
  height?: number;
  layout?: 'vertical' | 'horizontal';
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

export default function BarChartComponent({
  data,
  xKey,
  bars,
  height = 300,
  layout = 'vertical',
}: BarChartComponentProps) {
  const isHorizontal = layout === 'horizontal';

  return (
    <ResponsiveContainer width="100%" height={height}>
      <BarChart data={data} layout={isHorizontal ? 'vertical' : 'horizontal'}>
        <CartesianGrid
          stroke={DARK_THEME.gridStroke}
          strokeDasharray="3 3"
        />
        {isHorizontal ? (
          <>
            <XAxis
              type="number"
              tick={axisTickStyle}
              axisLine={{ stroke: DARK_THEME.border }}
              tickLine={{ stroke: DARK_THEME.border }}
            />
            <YAxis
              type="category"
              dataKey={xKey}
              tick={axisTickStyle}
              axisLine={{ stroke: DARK_THEME.border }}
              tickLine={{ stroke: DARK_THEME.border }}
              width={100}
            />
          </>
        ) : (
          <>
            <XAxis
              dataKey={xKey}
              tick={axisTickStyle}
              axisLine={{ stroke: DARK_THEME.border }}
              tickLine={{ stroke: DARK_THEME.border }}
            />
            <YAxis
              tick={axisTickStyle}
              axisLine={{ stroke: DARK_THEME.border }}
              tickLine={{ stroke: DARK_THEME.border }}
            />
          </>
        )}
        <Tooltip
          contentStyle={tooltipStyle}
          labelStyle={{ color: DARK_THEME.textPrimary }}
          itemStyle={{ color: DARK_THEME.textPrimary }}
          cursor={{ fill: 'rgba(148, 163, 184, 0.1)' }}
        />
        {bars.map((bar, index) => (
          <Bar
            key={bar.key}
            dataKey={bar.key}
            name={bar.name ?? bar.key}
            fill={bar.color ?? CHART_COLORS[index % CHART_COLORS.length]}
            stackId={bar.stackId}
            radius={[4, 4, 0, 0]}
          />
        ))}
      </BarChart>
    </ResponsiveContainer>
  );
}
