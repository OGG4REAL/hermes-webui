interface Customer {
  id: string;
  name: string;
  risk_level: string;
  aum: number;
  liquidity_need: string;
  investment_horizon: string;
}

interface MemoryRef {
  id: string;
  type: string;
  summary: string;
}

interface Props {
  data: Record<string, unknown>;
}

export function CustomerProfileCard({ data }: Props) {
  const customer = data.customer as Customer;
  const memories = (data.memory_references ?? []) as MemoryRef[];

  return (
    <div style={cardStyle}>
      <h3 style={headerStyle}>客户画像</h3>
      <table style={tableStyle}>
        <tbody>
          <Row label="姓名" value={customer.name} />
          <Row label="客户ID" value={customer.id} />
          <Row label="风险等级" value={customer.risk_level} />
          <Row label="资产规模" value={`¥${customer.aum.toLocaleString()}`} />
          <Row label="流动性需求" value={customer.liquidity_need} />
          <Row label="投资期限" value={customer.investment_horizon} />
        </tbody>
      </table>
      {memories.length > 0 && (
        <>
          <h4 style={{ margin: "12px 0 6px", fontSize: 13 }}>记忆摘要</h4>
          <ul style={{ margin: 0, paddingLeft: 18, fontSize: 13 }}>
            {memories.map((m) => (
              <li key={m.id} style={{ marginBottom: 4 }}>
                <span style={tagStyle}>{m.type}</span> {m.summary}
              </li>
            ))}
          </ul>
        </>
      )}
    </div>
  );
}

function Row({ label, value }: { label: string; value: string }) {
  return (
    <tr>
      <td style={labelCellStyle}>{label}</td>
      <td style={valueCellStyle}>{value}</td>
    </tr>
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

const labelCellStyle: React.CSSProperties = {
  padding: "3px 8px 3px 0",
  color: "#667085",
  fontWeight: 500,
  whiteSpace: "nowrap",
  width: 90,
};

const valueCellStyle: React.CSSProperties = {
  padding: "3px 0",
};

const tagStyle: React.CSSProperties = {
  display: "inline-block",
  background: "#f2f4f7",
  borderRadius: 3,
  padding: "1px 5px",
  fontSize: 11,
  fontWeight: 500,
  color: "#344054",
  marginRight: 4,
};
