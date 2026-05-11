interface Column {
  key: string;
  label?: string;
}

interface DataTableProps {
  props: {
    title?: string;
    columns?: Column[];
    rows?: Record<string, unknown>[];
  };
}

// Per ADR-010: best-effort. If columns omitted, infer from first row keys.
function inferColumns(rows: Record<string, unknown>[]): Column[] {
  if (rows.length === 0) return [];
  return Object.keys(rows[0]).map((k) => ({ key: k, label: k }));
}

export function DataTable({ props }: DataTableProps) {
  const rows = Array.isArray(props.rows) ? props.rows : [];
  const columns = Array.isArray(props.columns) && props.columns.length > 0
    ? props.columns
    : inferColumns(rows);

  if (columns.length === 0 && rows.length === 0) {
    return (
      <div style={wrapStyle}>
        {props.title && <div style={titleStyle}>{props.title}</div>}
        <div style={emptyStyle}>表格数据不完整</div>
      </div>
    );
  }

  return (
    <div style={wrapStyle}>
      {props.title && <div style={titleStyle}>{props.title}</div>}
      <table style={tableStyle}>
        <thead>
          <tr>
            {columns.map((col) => (
              <th key={col.key} style={thStyle}>{col.label ?? col.key}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row, i) => (
            <tr key={i}>
              {columns.map((col) => (
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

const emptyStyle: React.CSSProperties = {
  padding: "24px 16px",
  textAlign: "center",
  color: "#98a2b3",
  fontSize: 13,
};
