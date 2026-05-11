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
  label?: string;
  color?: string;
}

interface BarChartBlockProps {
  props: {
    title?: string;
    xKey?: string;
    series?: SeriesEntry[];
    data?: Record<string, unknown>[];
  };
}

const DEFAULT_COLORS = ["#067647", "#1570ef", "#b54708", "#6941c6", "#b42318"];

// Per ADR-010: primitives must render best-effort. Missing required props
// (xKey, series, empty data) produce a placeholder, not a runtime crash.
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

export function BarChartBlock({ props }: BarChartBlockProps) {
  const data = Array.isArray(props.data) ? props.data : [];
  const xKey = props.xKey ?? inferXKey(data) ?? "x";
  const series = Array.isArray(props.series) && props.series.length > 0
    ? props.series
    : inferSeriesFromData(data, xKey);

  if (data.length === 0 || series.length === 0) {
    return (
      <div style={wrapStyle}>
        {props.title && <div style={titleStyle}>{props.title}</div>}
        <div style={emptyStyle}>柱状图数据不完整</div>
      </div>
    );
  }

  return (
    <div style={wrapStyle}>
      {props.title && <div style={titleStyle}>{props.title}</div>}
      <ResponsiveContainer width="100%" height={260}>
        <BarChart data={data} margin={{ top: 8, right: 16, bottom: 4, left: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#f2f4f7" />
          <XAxis dataKey={xKey} tick={{ fontSize: 12 }} />
          <YAxis tick={{ fontSize: 12 }} />
          <Tooltip />
          <Legend />
          {series.map((s, i) => (
            <Bar
              key={s.key}
              dataKey={s.key}
              name={s.label ?? s.key}
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

const emptyStyle: React.CSSProperties = {
  padding: "24px 0",
  textAlign: "center",
  color: "#98a2b3",
  fontSize: 13,
};
