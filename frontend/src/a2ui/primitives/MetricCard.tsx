interface MetricCardProps {
  props: {
    label?: string;
    value?: string | number;
    unit?: string;
    trend?: "up" | "down" | "flat";
    delta?: string;
  };
}

const trendColors: Record<string, string> = {
  up: "#067647",
  down: "#b42318",
  flat: "#667085",
};

const trendArrows: Record<string, string> = {
  up: "↑",
  down: "↓",
  flat: "→",
};

export function MetricCard({ props }: MetricCardProps) {
  const trend = props.trend ?? "flat";
  return (
    <div style={cardStyle}>
      <div style={{ fontSize: 12, color: "#667085", marginBottom: 4 }}>
        {props.label ?? "Metric"}
      </div>
      <div style={{ fontSize: 28, fontWeight: 700, color: "#101828" }}>
        {props.value ?? "-"}
        {props.unit && (
          <span style={{ fontSize: 14, fontWeight: 400, color: "#98a2b3", marginLeft: 4 }}>
            {props.unit}
          </span>
        )}
      </div>
      {props.delta && (
        <div style={{ fontSize: 13, color: trendColors[trend], marginTop: 4 }}>
          {trendArrows[trend]} {props.delta}
        </div>
      )}
    </div>
  );
}

const cardStyle: React.CSSProperties = {
  padding: "16px 20px",
  border: "1px solid #e4e7ec",
  borderRadius: 8,
  background: "#fff",
};
