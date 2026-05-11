import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";

interface SeriesEntry {
  key: string;
  label?: string;
  color?: string;
}

interface LineChartBlockProps {
  props: {
    title?: string;
    xKey?: string;
    series?: SeriesEntry[];
    data?: Record<string, unknown>[];
  };
}

const DEFAULT_COLORS = ["#1570ef", "#067647", "#b54708", "#6941c6", "#b42318"];

function inferSeriesFromData(data: Record<string, unknown>[], xKey: string): SeriesEntry[] {
  if (data.length === 0) return [];
  const sample = data[0];
  return Object.keys(sample)
    .filter((k) => k !== xKey && typeof sample[k] === "number")
    .map((k) => ({ key: k }));
}

function inferXKey(data: Record<string, unknown>[]): string | null {
  if (data.length === 0) return null;
  const sample = data[0];
  for (const k of Object.keys(sample)) {
    if (typeof sample[k] !== "number") return k;
  }
  return Object.keys(sample)[0] ?? null;
}

export function LineChartBlock({ props }: LineChartBlockProps) {
  const data = Array.isArray(props.data) ? props.data : [];
  const xKey = props.xKey ?? inferXKey(data) ?? "x";
  const series = Array.isArray(props.series) && props.series.length > 0
    ? props.series
    : inferSeriesFromData(data, xKey);

  if (data.length === 0 || series.length === 0) {
    return (
      <div style={wrapStyle}>
        {props.title && <div style={titleStyle}>{props.title}</div>}
        <div style={emptyStyle}>折线图数据不完整</div>
      </div>
    );
  }

  return (
    <div style={wrapStyle}>
      {props.title && <div style={titleStyle}>{props.title}</div>}
      <ResponsiveContainer width="100%" height={260}>
        <LineChart data={data} margin={{ top: 8, right: 16, bottom: 4, left: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#f2f4f7" />
          <XAxis dataKey={xKey} tick={{ fontSize: 12 }} />
          <YAxis tick={{ fontSize: 12 }} />
          <Tooltip />
          <Legend />
          {series.map((s, i) => (
            <Line
              key={s.key}
              type="monotone"
              dataKey={s.key}
              name={s.label ?? s.key}
              stroke={s.color ?? DEFAULT_COLORS[i % DEFAULT_COLORS.length]}
              strokeWidth={2}
              dot={false}
            />
          ))}
        </LineChart>
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

const emptyStyle: React.CSSProperties = {
  padding: "24px 0",
  textAlign: "center",
  color: "#98a2b3",
  fontSize: 13,
};
