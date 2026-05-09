import { useReducer, useEffect, useCallback, useState } from "react";
import { workbenchReducer, initialState } from "./agui/aguiReducer";
import type { WorkbenchPhase } from "./agui/aguiReducer";
import { mockTranscript } from "./fixtures/rmWorkbenchTranscript";
import { A2UISurfaceRenderer } from "./a2ui/A2UISurfaceRenderer";
import { resolveInteraction, seedPendingInteraction, fetchMockStream, parseRmWorkbenchSSE } from "./api/hermesClient";

const SESSION_ID = "smoke-session-001";
const INTERACTION_ID = "pi_001";

const phaseLabels: Record<WorkbenchPhase, string> = {
  idle: "空闲",
  loading: "正在加载会话记录",
  surfaces_rendered: "组件已渲染",
  pending_interaction: "等待产品选择",
  submitting: "正在提交",
  resolved: "选择已确认",
  error: "出错",
};

const phaseBadgeColors: Record<WorkbenchPhase, string> = {
  idle: "#667085",
  loading: "#b54708",
  surfaces_rendered: "#067647",
  pending_interaction: "#b54708",
  submitting: "#b54708",
  resolved: "#067647",
  error: "#b42318",
};

export default function App() {
  const [state, dispatch] = useReducer(workbenchReducer, initialState);
  const [setupWarning, setSetupWarning] = useState<string | null>(null);
  const [dataSource, setDataSource] = useState<"backend" | "fallback" | null>(null);

  const handleRmWorkbenchEvent = useCallback((eventData: string) => {
    const events = parseRmWorkbenchSSE(eventData);
    if (events.length > 0) {
      dispatch({ type: "APPEND_EVENTS", events });
    }
  }, []);

  useEffect(() => {
    (window as unknown as Record<string, unknown>).__rmWorkbenchEvent = handleRmWorkbenchEvent;
    return () => {
      delete (window as unknown as Record<string, unknown>).__rmWorkbenchEvent;
    };
  }, [handleRmWorkbenchEvent]);

  useEffect(() => {
    let cancelled = false;

    async function loadStream() {
      const streamResult = await fetchMockStream();
      if (cancelled) return;

      if (streamResult.ok && streamResult.events) {
        setDataSource("backend");
        dispatch({ type: "LOAD_TRANSCRIPT", events: streamResult.events });
      } else {
        setDataSource("fallback");
        setSetupWarning(
          `后端模拟流不可用，已回退至本地静态记录：${streamResult.error ?? "未知错误"}`
        );
        dispatch({ type: "LOAD_TRANSCRIPT", events: mockTranscript });
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

  const handleConfirm = useCallback(async (selectedIds: string[]) => {
    dispatch({ type: "SET_PHASE", phase: "submitting" });
    const interactionId = state.pendingInteraction?.interaction_id;
    const result = await resolveInteraction(SESSION_ID, selectedIds, interactionId);
    if (result.ok) {
      setSetupWarning(null);
      dispatch({ type: "CLEAR_PENDING" });
    } else {
      dispatch({ type: "SET_ERROR", error: result.error ?? "未知错误" });
    }
  }, [state.pendingInteraction]);

  const interactionDisabled = state.phase !== "pending_interaction";

  return (
    <div style={layoutStyle}>
      <header style={headerStyle}>
        <h1 style={titleStyle}>客户经理工作台 V0</h1>
        <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
          <span
            style={{
              ...badgeStyle,
              color: phaseBadgeColors[state.phase],
              borderColor: phaseBadgeColors[state.phase],
            }}
          >
            {phaseLabels[state.phase]}
          </span>
          {state.runId && (
            <span style={metaStyle}>运行：{state.runId}</span>
          )}
        </div>
      </header>

      {state.error && (
        <div style={errorBannerStyle}>
          {state.error}
          <button
            style={dismissBtnStyle}
            onClick={() => dispatch({ type: "SET_PHASE", phase: state.pendingInteraction ? "pending_interaction" : "surfaces_rendered" })}
          >
            关闭
          </button>
        </div>
      )}

      {setupWarning && (
        <div style={warningBannerStyle}>
          后端冒烟初始化失败：{setupWarning}
        </div>
      )}

      {state.phase === "idle" && (
        <p style={{ color: "#667085", textAlign: "center", padding: 40 }}>
          正在初始化工作台...
        </p>
      )}

      {state.surfaces.length > 0 && (
        <A2UISurfaceRenderer
          surfaces={state.surfaces}
          interactionDisabled={interactionDisabled}
          onConfirmSelection={handleConfirm}
        />
      )}

      {state.memoryProposals.length > 0 && (
        <div style={warningBannerStyle}>
          记忆提案：{state.memoryProposals.length} 条待审批（仅展示，V0 不写入）
        </div>
      )}

      {state.phase === "resolved" && (
        <div style={successBannerStyle}>
          产品选择已确认。
        </div>
      )}

      <footer style={footerStyle}>
        <span>
          {dataSource === "backend"
            ? "数据来源：后端模拟流"
            : dataSource === "fallback"
              ? "数据来源：本地静态记录（回退）"
              : "正在加载..."}
          {" "}&middot; 会话：{SESSION_ID}
        </span>
        <span>已支持真实 Hermes 流 (rm_workbench SSE)</span>
      </footer>
    </div>
  );
}

const layoutStyle: React.CSSProperties = {
  maxWidth: 780,
  margin: "0 auto",
  padding: "24px 16px",
  fontFamily: "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
  color: "#101828",
};

const headerStyle: React.CSSProperties = {
  display: "flex",
  justifyContent: "space-between",
  alignItems: "center",
  marginBottom: 20,
  paddingBottom: 12,
  borderBottom: "1px solid #e4e7ec",
};

const titleStyle: React.CSSProperties = {
  fontSize: 18,
  fontWeight: 700,
  margin: 0,
};

const badgeStyle: React.CSSProperties = {
  fontSize: 12,
  fontWeight: 500,
  padding: "2px 8px",
  borderRadius: 4,
  border: "1px solid",
};

const metaStyle: React.CSSProperties = {
  fontSize: 11,
  color: "#98a2b3",
  fontFamily: "monospace",
};

const errorBannerStyle: React.CSSProperties = {
  background: "#fef3f2",
  border: "1px solid #fda29b",
  borderRadius: 6,
  padding: "10px 14px",
  marginBottom: 16,
  fontSize: 13,
  color: "#b42318",
  display: "flex",
  justifyContent: "space-between",
  alignItems: "center",
};

const warningBannerStyle: React.CSSProperties = {
  background: "#fffaeb",
  border: "1px solid #fedf89",
  borderRadius: 6,
  padding: "10px 14px",
  marginBottom: 16,
  fontSize: 13,
  color: "#93370d",
};

const dismissBtnStyle: React.CSSProperties = {
  background: "none",
  border: "1px solid #fda29b",
  borderRadius: 4,
  padding: "2px 8px",
  fontSize: 12,
  color: "#b42318",
  cursor: "pointer",
};

const successBannerStyle: React.CSSProperties = {
  background: "#ecfdf3",
  border: "1px solid #6ce9a6",
  borderRadius: 6,
  padding: "10px 14px",
  marginTop: 16,
  fontSize: 13,
  color: "#067647",
};

const footerStyle: React.CSSProperties = {
  marginTop: 24,
  paddingTop: 12,
  borderTop: "1px solid #e4e7ec",
  display: "flex",
  justifyContent: "space-between",
  fontSize: 11,
  color: "#98a2b3",
};
