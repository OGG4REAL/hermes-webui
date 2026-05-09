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
    labelKey: string;
    valueKey: string;
    data: Record<string, unknown>[];
  };
}

const COLORS = ["#1570ef", "#067647", "#b54708", "#6941c6", "#b42318", "#344054"];

export function PieChartBlock({ props }: PieChartBlockProps) {
  const chartData = props.data.map((row) => ({
    name: String(row[props.labelKey] ?? ""),
    value: Number(row[props.valueKey] ?? 0),
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
