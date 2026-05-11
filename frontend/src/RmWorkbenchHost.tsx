import { useReducer, useEffect, useCallback, useState } from "react";
import { workbenchReducer, initialState } from "./agui/aguiReducer";
import type { WorkbenchPhase } from "./agui/aguiReducer";
import { A2UISurfaceRenderer } from "./a2ui/A2UISurfaceRenderer";
import { resolveInteraction, parseRmWorkbenchSSE } from "./api/hermesClient";

export interface RmWorkbenchHostProps {
  mode: "standalone" | "embedded";
  sessionId?: string;
}

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

export default function RmWorkbenchHost({ mode, sessionId }: RmWorkbenchHostProps) {
  const [state, dispatch] = useReducer(workbenchReducer, initialState);
  const [setupWarning, setSetupWarning] = useState<string | null>(null);

  const handleRmWorkbenchEvent = useCallback((eventData: string) => {
    const events = parseRmWorkbenchSSE(eventData);
    console.log("[rm_workbench_host] received event data, parsed", events.length, "events");
    if (events.length > 0) {
      dispatch({ type: "APPEND_EVENTS", events });
    }
  }, []);

  useEffect(() => {
    const w = window as unknown as Record<string, unknown>;
    w.__rmWorkbenchEvent = handleRmWorkbenchEvent;

    const queue = w.__rmWorkbenchEventQueue as string[] | undefined;
    if (Array.isArray(queue)) {
      for (const data of queue) {
        handleRmWorkbenchEvent(data);
      }
      queue.length = 0;
    }

    return () => {
      if (w.__rmWorkbenchEvent === handleRmWorkbenchEvent) {
        delete w.__rmWorkbenchEvent;
      }
    };
  }, [handleRmWorkbenchEvent]);

  const handleConfirm = useCallback(async (selectedIds: string[]) => {
    dispatch({ type: "SET_PHASE", phase: "submitting" });
    const interactionId = state.pendingInteraction?.interaction_id;
    let resolveSessionId = sessionId;
    if (!resolveSessionId && mode === "embedded") {
      const s = (window as any).S;
      resolveSessionId = s?.session?.session_id ?? undefined;
    }
    if (!resolveSessionId) {
      dispatch({ type: "SET_ERROR", error: "无法获取当前会话 ID，请刷新页面重试" });
      return;
    }
    const result = await resolveInteraction(resolveSessionId, selectedIds, interactionId);
    if (result.ok) {
      setSetupWarning(null);
      dispatch({ type: "CLEAR_PENDING" });
    } else {
      dispatch({ type: "SET_ERROR", error: result.error ?? "未知错误" });
    }
  }, [state.pendingInteraction, sessionId, mode]);

  const interactionDisabled = state.phase !== "pending_interaction";
  const isEmbedded = mode === "embedded";
  const hasContent = state.surfaces.length > 0 || state.pendingInteraction || state.phase === "resolved" || state.error;

  if (isEmbedded && !hasContent) {
    return null;
  }

  return (
    <div style={isEmbedded ? embeddedLayoutStyle : standaloneLayoutStyle}>
      {!isEmbedded && (
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
      )}

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

      {!isEmbedded && state.phase === "idle" && (
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

      {!isEmbedded && (
        <footer style={footerStyle}>
          <span>会话：{sessionId ?? "smoke-session-001"}</span>
          <span>已支持真实 Hermes 流 (rm_workbench SSE)</span>
        </footer>
      )}
    </div>
  );
}

const standaloneLayoutStyle: React.CSSProperties = {
  maxWidth: 780,
  margin: "0 auto",
  padding: "24px 16px",
  fontFamily: "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
  color: "#101828",
};

const embeddedLayoutStyle: React.CSSProperties = {
  maxWidth: 800,
  margin: "12px auto",
  padding: "0 24px",
  fontFamily: "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
  color: "var(--text, #101828)",
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
