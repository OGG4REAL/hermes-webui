import { useState } from "react";

interface OptionInput {
  // Accept either id or value as identifier (best-effort, ADR-010).
  id?: string;
  value?: string;
  label?: string;
  description?: string;
}

interface NormalizedOption {
  id: string;
  label: string;
  description?: string;
}

interface ChoiceListProps {
  props: {
    title?: string;
    multiple?: boolean;
    options?: OptionInput[];
  };
}

function normalizeOptions(raw: OptionInput[] | undefined): NormalizedOption[] {
  if (!Array.isArray(raw)) return [];
  return raw.map((opt, idx) => {
    const id = opt.id ?? opt.value ?? `opt-${idx}`;
    const label = opt.label ?? id;
    return { id, label, description: opt.description };
  });
}

export function ChoiceList({ props }: ChoiceListProps) {
  const options = normalizeOptions(props.options);
  const [selected, setSelected] = useState<Set<string>>(new Set());

  if (options.length === 0) {
    return (
      <div style={wrapStyle}>
        {props.title && <div style={titleStyle}>{props.title}</div>}
        <div style={emptyStyle}>选项不完整</div>
      </div>
    );
  }

  const toggle = (id: string) => {
    setSelected((prev) => {
      const next = new Set(prev);
      if (next.has(id)) {
        next.delete(id);
      } else {
        if (!props.multiple) next.clear();
        next.add(id);
      }
      return next;
    });
  };

  return (
    <div style={wrapStyle}>
      {props.title && <div style={titleStyle}>{props.title}</div>}
      <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
        {options.map((opt) => {
          const active = selected.has(opt.id);
          return (
            <button
              key={opt.id}
              onClick={() => toggle(opt.id)}
              style={{
                ...optionStyle,
                borderColor: active ? "#1570ef" : "#e4e7ec",
                background: active ? "#eff8ff" : "#fff",
              }}
            >
              <div style={{ fontWeight: 500, fontSize: 13, color: "#344054" }}>
                {opt.label}
              </div>
              {opt.description && (
                <div style={{ fontSize: 12, color: "#667085", marginTop: 2 }}>
                  {opt.description}
                </div>
              )}
            </button>
          );
        })}
      </div>
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

const optionStyle: React.CSSProperties = {
  textAlign: "left",
  padding: "10px 14px",
  border: "1px solid",
  borderRadius: 6,
  cursor: "pointer",
  transition: "border-color 0.15s, background 0.15s",
};

const emptyStyle: React.CSSProperties = {
  padding: "16px 0",
  textAlign: "center",
  color: "#98a2b3",
  fontSize: 13,
};
