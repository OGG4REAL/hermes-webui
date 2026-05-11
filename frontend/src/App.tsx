import { useEffect, useState } from "react";
import RmWorkbenchHost from "./RmWorkbenchHost";
import { mockTranscript } from "./fixtures/rmWorkbenchTranscript";
import { fetchMockStream, seedPendingInteraction } from "./api/hermesClient";

const SESSION_ID = "smoke-session-001";
const INTERACTION_ID = "pi_001";

export default function App() {
  const [dataSource, setDataSource] = useState<"backend" | "fallback" | null>(null);
  const [setupWarning, setSetupWarning] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    async function loadStream() {
      const streamResult = await fetchMockStream();
      if (cancelled) return;

      const events = streamResult.ok && streamResult.events
        ? streamResult.events
        : mockTranscript;

      if (streamResult.ok) {
        setDataSource("backend");
      } else {
        setDataSource("fallback");
        setSetupWarning(
          `后端模拟流不可用，已回退至本地静态记录：${streamResult.error ?? "未知错误"}`
        );
      }

      const payload = JSON.stringify({ kind: "agui_events", events });
      if (typeof (window as any).__rmWorkbenchEvent === "function") {
        (window as any).__rmWorkbenchEvent(payload);
      }

      const seedResult = await seedPendingInteraction(SESSION_ID, INTERACTION_ID);
      if (cancelled) return;
      if (!seedResult.ok) {
        setSetupWarning((prev) =>
          prev
            ? `${prev}；后端交互初始化失败：${seedResult.error}`
            : seedResult.error ?? "无法初始化后端待处理交互"
        );
      }
    }

    loadStream();
    return () => { cancelled = true; };
  }, []);

  return (
    <div>
      <RmWorkbenchHost mode="standalone" sessionId={SESSION_ID} />
      {setupWarning && (
        <div style={warningBannerStyle}>
          后端冒烟初始化失败：{setupWarning}
        </div>
      )}
      <footer style={footerStyle}>
        <span>
          {dataSource === "backend"
            ? "数据来源：后端模拟流"
            : dataSource === "fallback"
              ? "数据来源：本地静态记录（回退）"
              : "正在加载..."}
        </span>
      </footer>
    </div>
  );
}

const warningBannerStyle: React.CSSProperties = {
  background: "#fffaeb",
  border: "1px solid #fedf89",
  borderRadius: 6,
  padding: "10px 14px",
  fontSize: 13,
  color: "#93370d",
  maxWidth: 780,
  margin: "0 auto 16px",
};

const footerStyle: React.CSSProperties = {
  maxWidth: 780,
  margin: "0 auto",
  padding: "12px 16px 0",
  borderTop: "1px solid #e4e7ec",
  display: "flex",
  justifyContent: "space-between",
  fontSize: 11,
  color: "#98a2b3",
};
