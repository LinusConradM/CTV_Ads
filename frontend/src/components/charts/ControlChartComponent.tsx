import { useMemo } from 'react';
import {
  ResponsiveContainer,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  ReferenceLine,
  Scatter,
  ComposedChart,
} from 'recharts';
import { DARK_THEME } from '../../utils/colors';

interface ControlChartComponentProps {
  data: any[];
  xKey?: string;
  height?: number;
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

interface DotProps {
  cx?: number;
  cy?: number;
  payload?: any;
}

export default function ControlChartComponent({
  data,
  xKey = 'report_date',
  height = 300,
}: ControlChartComponentProps) {
  const { meanValue, uclValue, lclValue } = useMemo(() => {
    if (data.length === 0) return { meanValue: undefined, uclValue: undefined, lclValue: undefined };
    const last = data[data.length - 1];
    return {
      meanValue: last.mean_line,
      uclValue: last.ucl,
      lclValue: last.lcl,
    };
  }, [data]);

  const outOfControlPoints = useMemo(() => {
    return data.filter(
      (d) => d.value > d.ucl || d.value < d.lcl
    );
  }, [data]);

  const renderDot = (props: DotProps) => {
    const { cx, cy, payload } = props;
    if (!cx || !cy || !payload) return null;

    const isOutOfControl = payload.value > payload.ucl || payload.value < payload.lcl;
    if (isOutOfControl) {
      return (
        <circle
          cx={cx}
          cy={cy}
          r={5}
          fill="#f43f5e"
          stroke="#fff"
          strokeWidth={1.5}
        />
      );
    }
    return null;
  };

  return (
    <ResponsiveContainer width="100%" height={height}>
      <ComposedChart data={data}>
        <CartesianGrid
          stroke={DARK_THEME.gridStroke}
          strokeDasharray="3 3"
        />
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

        {/* UCL reference line */}
        {uclValue !== undefined && (
          <ReferenceLine
            y={uclValue}
            stroke="#f43f5e"
            strokeDasharray="6 3"
            label={{
              value: 'UCL',
              position: 'right',
              fill: '#f43f5e',
              fontSize: 11,
            }}
          />
        )}

        {/* LCL reference line */}
        {lclValue !== undefined && (
          <ReferenceLine
            y={lclValue}
            stroke="#f43f5e"
            strokeDasharray="6 3"
            label={{
              value: 'LCL',
              position: 'right',
              fill: '#f43f5e',
              fontSize: 11,
            }}
          />
        )}

        {/* Mean reference line */}
        {meanValue !== undefined && (
          <ReferenceLine
            y={meanValue}
            stroke="#10b981"
            strokeDasharray="6 3"
            label={{
              value: 'Mean',
              position: 'right',
              fill: '#10b981',
              fontSize: 11,
            }}
          />
        )}

        {/* Main value line */}
        <Line
          type="monotone"
          dataKey="value"
          name="Value"
          stroke="#3b82f6"
          strokeWidth={2}
          dot={renderDot}
          activeDot={{ r: 5, fill: '#3b82f6' }}
        />

        {/* Out-of-control scatter overlay */}
        {outOfControlPoints.length > 0 && (
          <Scatter
            data={outOfControlPoints}
            dataKey="value"
            fill="#f43f5e"
            shape="circle"
            legendType="none"
          />
        )}
      </ComposedChart>
    </ResponsiveContainer>
  );
}
