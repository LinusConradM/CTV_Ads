import {
  ResponsiveContainer,
  LineChart,
  AreaChart,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  Line,
  Area,
} from 'recharts';
import { CHART_COLORS, DARK_THEME } from '../../utils/colors';

interface LineConfig {
  key: string;
  color?: string;
  name?: string;
}

interface AreaLineChartProps {
  data: any[];
  xKey: string;
  lines: LineConfig[];
  height?: number;
  showGrid?: boolean;
  areaFill?: boolean;
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

export default function AreaLineChart({
  data,
  xKey,
  lines,
  height = 300,
  showGrid = true,
  areaFill = false,
}: AreaLineChartProps) {
  const ChartComponent = areaFill ? AreaChart : LineChart;

  return (
    <ResponsiveContainer width="100%" height={height}>
      <ChartComponent data={data}>
        {showGrid && (
          <CartesianGrid
            stroke={DARK_THEME.gridStroke}
            strokeDasharray="3 3"
          />
        )}
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
        <Tooltip
          contentStyle={tooltipStyle}
          labelStyle={{ color: DARK_THEME.textPrimary }}
          itemStyle={{ color: DARK_THEME.textPrimary }}
        />
        {lines.map((line, index) => {
          const color = line.color ?? CHART_COLORS[index % CHART_COLORS.length];
          const name = line.name ?? line.key;

          if (areaFill) {
            return (
              <Area
                key={line.key}
                type="monotone"
                dataKey={line.key}
                name={name}
                stroke={color}
                fill={color}
                fillOpacity={0.15}
                strokeWidth={2}
                dot={false}
                activeDot={{ r: 4, fill: color }}
              />
            );
          }

          return (
            <Line
              key={line.key}
              type="monotone"
              dataKey={line.key}
              name={name}
              stroke={color}
              strokeWidth={2}
              dot={false}
              activeDot={{ r: 4, fill: color }}
            />
          );
        })}
      </ChartComponent>
    </ResponsiveContainer>
  );
}
