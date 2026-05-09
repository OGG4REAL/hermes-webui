import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";

interface SeriesEntry {
  key: string;
  label: string;
  color?: string;
}

interface BarChartBlockProps {
  props: {
    title?: string;
    xKey: string;
    series: SeriesEntry[];
    data: Record<string, unknown>[];
  };
}

const DEFAULT_COLORS = ["#067647", "#1570ef", "#b54708", "#6941c6", "#b42318"];

export function BarChartBlock({ props }: BarChartBlockProps) {
  return (
    <div style={wrapStyle}>
      {props.title && <div style={titleStyle}>{props.title}</div>}
      <ResponsiveContainer width="100%" height={260}>
        <BarChart data={props.data} margin={{ top: 8, right: 16, bottom: 4, left: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#f2f4f7" />
          <XAxis dataKey={props.xKey} tick={{ fontSize: 12 }} />
          <YAxis tick={{ fontSize: 12 }} />
          <Tooltip />
          <Legend />
          {props.series.map((s, i) => (
            <Bar
              key={s.key}
              dataKey={s.key}
              name={s.label}
              fill={s.color ?? DEFAULT_COLORS[i % DEFAULT_COLORS.length]}
            />
          ))}
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}

const wrapStyle: React.CSSProperties = {
  border: "1px solid #e4e7ec",
  borderRadius: 8,
  padding: 16,
  background: "#fff",
};

const titleStyle: React.CSSProperties = {
  fontSize: 14,
  fontWeight: 600,
  marginBottom: 12,
};
