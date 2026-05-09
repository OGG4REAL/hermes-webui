import type { AGUIEvent } from "../agui/aguiReducer";

interface ApiResult {
  ok?: boolean;
  resolved?: number;
  error?: string;
}

interface RmWorkbenchSSEPayload {
  kind: string;
  events?: AGUIEvent[];
}

async function readApiResult(res: Response): Promise<{ payload: ApiResult | null; text: string }> {
  const text = await res.text();
  if (!text) {
    return { payload: null, text };
  }

  try {
    return { payload: JSON.parse(text) as ApiResult, text };
  } catch {
    return { payload: null, text };
  }
}

export function parseRmWorkbenchSSE(eventData: string): AGUIEvent[] {
  try {
    const payload = JSON.parse(eventData) as RmWorkbenchSSEPayload;
    if (payload.kind === "agui_events" && Array.isArray(payload.events)) {
      return payload.events;
    }
  } catch {
    // ignore malformed payloads
  }
  return [];
}

export async function fetchMockStream(): Promise<{ ok: boolean; events?: AGUIEvent[]; error?: string }> {
  try {
    const res = await fetch("/api/rm-workbench/mock-stream");
    if (!res.ok) {
      return { ok: false, error: `HTTP ${res.status}：后端模拟流请求失败` };
    }
    const body = await res.text();
    const events: AGUIEvent[] = [];
    for (const line of body.split("\n")) {
      if (!line.startsWith("data: ")) continue;
      const payload = line.slice(6);
      if (payload === "[DONE]") continue;
      events.push(JSON.parse(payload) as AGUIEvent);
    }
    if (events.length === 0) {
      return { ok: false, error: "后端模拟流返回空事件列表" };
    }
    return { ok: true, events };
  } catch {
    return { ok: false, error: "无法连接后端模拟流服务" };
  }
}

function backendErrorText(payload: ApiResult | null, text: string): string {
  const raw = String(payload?.error ?? (text || "空响应")).trim();
  const normalized = raw.toLowerCase();
  if (normalized === "not found") {
    return "接口未找到";
  }
  if (normalized.includes("cross-origin request rejected")) {
    return "跨源请求被拒绝";
  }
  return raw;
}

export async function seedPendingInteraction(
  sessionId: string,
  interactionId: string
): Promise<{ ok: boolean; error?: string }> {
  try {
    const qs = new URLSearchParams({
      session_id: sessionId,
      interaction_id: interactionId,
    });
    const res = await fetch(`/api/rm-workbench/inject_test?${qs.toString()}`);
    const { payload, text } = await readApiResult(res);
    if (!res.ok) {
      return { ok: false, error: `HTTP ${res.status}：${backendErrorText(payload, text)}` };
    }
    if (payload?.ok !== true) {
      return { ok: false, error: `后端返回异常：${backendErrorText(payload, text)}` };
    }
    return { ok: true };
  } catch {
    return { ok: false, error: "无法连接后端服务" };
  }
}

export async function resolveInteraction(
  sessionId: string,
  selectedProductIds: string[],
  interactionId?: string
): Promise<{ ok: boolean; error?: string }> {
  try {
    const body: Record<string, unknown> = {
      session_id: sessionId,
      payload: { selected_product_ids: selectedProductIds },
    };
    if (interactionId) {
      body.interaction_id = interactionId;
    }
    const res = await fetch("/api/rm-workbench/pending/resolve", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    const { payload, text } = await readApiResult(res);
    if (!res.ok) {
      return { ok: false, error: `HTTP ${res.status}：${backendErrorText(payload, text)}` };
    }
    if (payload?.ok !== true) {
      return { ok: false, error: `后端返回异常：${backendErrorText(payload, text)}` };
    }
    if ((payload.resolved ?? 0) < 1) {
      return {
        ok: false,
        error: "没有成功处理待确认交互。请刷新冒烟工作台，重新初始化后端队列。",
      };
    }
    return { ok: true };
  } catch {
    return { ok: false, error: "无法连接后端服务" };
  }
}
