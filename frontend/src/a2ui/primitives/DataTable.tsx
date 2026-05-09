interface Column {
  key: string;
  label: string;
}

interface DataTableProps {
  props: {
    title?: string;
    columns: Column[];
    rows: Record<string, unknown>[];
  };
}

export function DataTable({ props }: DataTableProps) {
  return (
    <div style={wrapStyle}>
      {props.title && <div style={titleStyle}>{props.title}</div>}
      <table style={tableStyle}>
        <thead>
          <tr>
            {props.columns.map((col) => (
              <th key={col.key} style={thStyle}>{col.label}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {props.rows.map((row, i) => (
            <tr key={i}>
              {props.columns.map((col) => (
                <td key={col.key} style={tdStyle}>{String(row[col.key] ?? "")}</td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

const wrapStyle: React.CSSProperties = {
  border: "1px solid #e4e7ec",
  borderRadius: 8,
  overflow: "hidden",
  background: "#fff",
};

const titleStyle: React.CSSProperties = {
  padding: "12px 16px",
  fontSize: 14,
  fontWeight: 600,
  borderBottom: "1px solid #e4e7ec",
};

const tableStyle: React.CSSProperties = {
  width: "100%",
  borderCollapse: "collapse",
  fontSize: 13,
};

const thStyle: React.CSSProperties = {
  textAlign: "left",
  padding: "8px 12px",
  borderBottom: "1px solid #e4e7ec",
  background: "#f9fafb",
  color: "#667085",
  fontWeight: 500,
  fontSize: 12,
};

const tdStyle: React.CSSProperties = {
  padding: "8px 12px",
  borderBottom: "1px solid #f2f4f7",
  color: "#344054",
};
