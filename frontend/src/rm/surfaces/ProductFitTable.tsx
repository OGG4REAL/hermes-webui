import { useState } from "react";

interface Product {
  id: string;
  name: string;
  asset_class: string;
  risk_level: string;
  fit_score: number;
  reasons: string[];
}

interface Props {
  data: Record<string, unknown>;
  disabled: boolean;
  onConfirm: (selectedIds: string[]) => void;
}

export function ProductFitTable({ data, disabled, onConfirm }: Props) {
  const products = (data.product_candidates ?? []) as Product[];
  const props = (data.surface_props ?? {}) as Record<string, unknown>;
  const maxSelection = (props.max_selection as number) ?? 3;

  const [selected, setSelected] = useState<Set<string>>(new Set());

  function toggle(id: string) {
    setSelected((prev) => {
      const next = new Set(prev);
      if (next.has(id)) {
        next.delete(id);
      } else if (next.size < maxSelection) {
        next.add(id);
      }
      return next;
    });
  }

  const canConfirm = selected.size >= 1 && selected.size <= maxSelection && !disabled;

  return (
    <div style={cardStyle}>
      <h3 style={headerStyle}>产品匹配</h3>
      <table style={tableStyle}>
        <thead>
          <tr>
            <th style={thStyle}></th>
            <th style={thStyle}>产品</th>
            <th style={thStyle}>资产类别</th>
            <th style={thStyle}>风险</th>
            <th style={thStyle}>匹配度</th>
            <th style={thStyle}>推荐理由</th>
          </tr>
        </thead>
        <tbody>
          {products.map((p) => (
            <tr key={p.id} style={selected.has(p.id) ? selectedRowStyle : undefined}>
              <td style={cellStyle}>
                <input
                  type="checkbox"
                  checked={selected.has(p.id)}
                  disabled={disabled || (!selected.has(p.id) && selected.size >= maxSelection)}
                  onChange={() => toggle(p.id)}
                />
              </td>
              <td style={cellStyle}>{p.name}</td>
              <td style={cellStyle}>{p.asset_class}</td>
              <td style={cellStyle}>{p.risk_level}</td>
              <td style={{ ...cellStyle, fontWeight: 600 }}>{p.fit_score}</td>
              <td style={{ ...cellStyle, fontSize: 12, color: "#667085" }}>
                {p.reasons.join("；")}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      <div style={footerStyle}>
        <span style={{ fontSize: 12, color: "#667085" }}>
          已选 {selected.size}/{maxSelection}
        </span>
        <button
          style={canConfirm ? btnStyle : btnDisabledStyle}
          disabled={!canConfirm}
          onClick={() => onConfirm([...selected])}
        >
          确认选择
        </button>
      </div>
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

const tableStyle: React.CSSProperties = {
  width: "100%",
  fontSize: 13,
  borderCollapse: "collapse",
};

const thStyle: React.CSSProperties = {
  textAlign: "left",
  padding: "6px 8px",
  borderBottom: "2px solid #e4e7ec",
  fontSize: 12,
  fontWeight: 600,
  color: "#475467",
};

const cellStyle: React.CSSProperties = {
  padding: "8px",
  borderBottom: "1px solid #f2f4f7",
  verticalAlign: "top",
};

const selectedRowStyle: React.CSSProperties = {
  background: "#f0f7ff",
};

const footerStyle: React.CSSProperties = {
  display: "flex",
  justifyContent: "space-between",
  alignItems: "center",
  marginTop: 12,
};

const btnBase: React.CSSProperties = {
  padding: "8px 20px",
  borderRadius: 6,
  fontSize: 13,
  fontWeight: 600,
  border: "none",
  cursor: "pointer",
};

const btnStyle: React.CSSProperties = {
  ...btnBase,
  background: "#1570ef",
  color: "#fff",
};

const btnDisabledStyle: React.CSSProperties = {
  ...btnBase,
  background: "#e4e7ec",
  color: "#98a2b3",
  cursor: "not-allowed",
};
