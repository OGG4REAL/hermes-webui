import {
  PieChart,
  Pie,
  Cell,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";

interface PieChartBlockProps {
  props: {
    title?: string;
    labelKey?: string;
    valueKey?: string;
    data?: Record<string, unknown>[];
  };
}

const COLORS = ["#1570ef", "#067647", "#b54708", "#6941c6", "#b42318", "#344054"];

// Per ADR-010: best-effort. If labelKey/valueKey not provided, infer first
// non-numeric and first numeric field from data sample.
function inferKeys(data: Record<string, unknown>[]): { labelKey: string | null; valueKey: string | null } {
  if (data.length === 0) return { labelKey: null, valueKey: null };
  const sample = data[0];
  let labelKey: string | null = null;
  let valueKey: string | null = null;
  for (const k of Object.keys(sample)) {
    if (typeof sample[k] === "number" && valueKey === null) valueKey = k;
    else if (labelKey === null) labelKey = k;
  }
  return { labelKey, valueKey };
}

export function PieChartBlock({ props }: PieChartBlockProps) {
  const data = Array.isArray(props.data) ? props.data : [];
  const inferred = inferKeys(data);
  const labelKey = props.labelKey ?? inferred.labelKey;
  const valueKey = props.valueKey ?? inferred.valueKey;

  if (data.length === 0 || !labelKey || !valueKey) {
    return (
      <div style={wrapStyle}>
        {props.title && <div style={titleStyle}>{props.title}</div>}
        <div style={emptyStyle}>饼图数据不完整</div>
      </div>
    );
  }

  const chartData = data.map((row) => ({
    name: String(row[labelKey] ?? ""),
    value: Number(row[valueKey] ?? 0),
  }));

  return (
    <div style={wrapStyle}>
      {props.title && <div style={titleStyle}>{props.title}</div>}
      <ResponsiveContainer width="100%" height={260}>
        <PieChart>
          <Pie
            data={chartData}
            dataKey="value"
            nameKey="name"
            cx="50%"
            cy="50%"
            outerRadius={90}
            label={(entry) => `${entry.name ?? ""} ${((entry.percent ?? 0) * 100).toFixed(0)}%`}
          >
            {chartData.map((_, i) => (
              <Cell key={i} fill={COLORS[i % COLORS.length]} />
            ))}
          </Pie>
          <Tooltip />
          <Legend />
        </PieChart>
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
