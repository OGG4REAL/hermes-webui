interface Brief {
  title: string;
  summary: string;
  talking_points: string[];
}

interface Props {
  data: Record<string, unknown>;
}

export function BriefExportPanel({ data }: Props) {
  const brief = data.brief as Brief | undefined;
  const props = (data.surface_props ?? {}) as Record<string, unknown>;
  const formats = (props.formats ?? []) as string[];

  if (!brief) {
    return (
      <div style={cardStyle}>
        <h3 style={headerStyle}>会前简报</h3>
        <p style={{ color: "#667085", fontSize: 13 }}>暂无简报数据。</p>
      </div>
    );
  }

  return (
    <div style={cardStyle}>
      <h3 style={headerStyle}>会前简报</h3>
      <p style={{ fontSize: 14, fontWeight: 500, margin: "0 0 6px" }}>{brief.title}</p>
      <p style={{ fontSize: 13, color: "#344054", margin: "0 0 12px" }}>{brief.summary}</p>
      <h4 style={{ fontSize: 13, fontWeight: 600, margin: "0 0 6px" }}>沟通要点</h4>
      <ol style={{ margin: 0, paddingLeft: 18, fontSize: 13 }}>
        {brief.talking_points.map((tp, i) => (
          <li key={i} style={{ marginBottom: 4 }}>
            {tp}
          </li>
        ))}
      </ol>
      {formats.length > 0 && (
        <div style={{ marginTop: 12, fontSize: 12, color: "#667085" }}>
          可导出格式：{formats.join("、")}
        </div>
      )}
    </div>
  );
}

const cardStyle: React.CSSProperties = {
  border: "1px solid #d0d5dd",
  borderRadius: 6,
  padding: 16,
  background: "#fff",
};

const headerStyle: React.CSSProperties = {
  margin: "0 0 12px",
  fontSize: 15,
  fontWeight: 600,
};
