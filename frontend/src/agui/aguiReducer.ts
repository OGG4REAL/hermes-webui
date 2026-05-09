import type { SurfaceData, PendingInteraction } from "../a2ui/types";

export interface AGUIEvent {
  type: string;
  thread_id?: string;
  run_id?: string;
  step_name?: string;
  name?: string;
  value?: Record<string, unknown>;
  delta?: unknown[];
}

export type WorkbenchPhase =
  | "idle"
  | "loading"
  | "surfaces_rendered"
  | "pending_interaction"
  | "submitting"
  | "resolved"
  | "error";

export interface MemoryProposal {
  id: string;
  [key: string]: unknown;
}

export interface WorkbenchState {
  phase: WorkbenchPhase;
  runId: string | null;
  threadId: string | null;
  surfaces: SurfaceData[];
  pendingInteraction: PendingInteraction | null;
  memoryProposals: MemoryProposal[];
  error: string | null;
}

export const initialState: WorkbenchState = {
  phase: "idle",
  runId: null,
  threadId: null,
  surfaces: [],
  pendingInteraction: null,
  memoryProposals: [],
  error: null,
};

export type WorkbenchAction =
  | { type: "LOAD_TRANSCRIPT"; events: AGUIEvent[] }
  | { type: "APPEND_EVENTS"; events: AGUIEvent[] }
  | { type: "SET_PHASE"; phase: WorkbenchPhase }
  | { type: "SET_ERROR"; error: string }
  | { type: "CLEAR_PENDING" };

function applyEvents(state: WorkbenchState, events: AGUIEvent[]): WorkbenchState {
  let next = state;
  for (const event of events) {
    if (event.type === "RUN_STARTED") {
      next = { ...next, runId: event.run_id ?? null, threadId: event.thread_id ?? null };
    } else if (event.type === "RUN_ERROR") {
      const message = (event as unknown as Record<string, unknown>).message as string | undefined;
      next = { ...next, error: message ?? "Unknown error from RM workbench bridge" };
    } else if (event.type === "CUSTOM" && event.name === "a2ui.surface.messages") {
      const v = event.value!;
      const surfaceId = v.surface_id as string;
      const surface = v.surface as string;
      const messages = v.messages as Array<Record<string, unknown>>;
      let data: Record<string, unknown> = {};
      let components: unknown[] | undefined;
      for (const msg of messages) {
        if (msg.updateDataModel) {
          const udm = msg.updateDataModel as Record<string, unknown>;
          data = { ...data, ...(udm.data as Record<string, unknown>) };
        }
        if (msg.updateComponents) {
          const uc = msg.updateComponents as Record<string, unknown>;
          components = (uc.components as unknown[]) ?? components;
        }
      }
      const newSurface = { surfaceId, surface, data, components };
      const idx = next.surfaces.findIndex(s => s.surfaceId === surfaceId);
      const surfaces = idx >= 0
        ? next.surfaces.map((s, i) => i === idx ? newSurface : s)
        : [...next.surfaces, newSurface];
      next = { ...next, surfaces };
    } else if (event.type === "CUSTOM" && event.name === "rm.pending_interaction.created") {
      const v = event.value!;
      next = {
        ...next,
        pendingInteraction: {
          interaction_id: v.interaction_id as string,
          surface_id: v.surface_id as string,
          action: v.action as string,
          blocking: v.blocking as boolean,
          schema: v.schema as Record<string, unknown>,
        },
      };
    } else if (event.type === "CUSTOM" && event.name === "rm.memory_proposal.created") {
      const v = event.value!;
      const proposals = (v.proposals as MemoryProposal[]) ?? [];
      next = {
        ...next,
        memoryProposals: [...next.memoryProposals, ...proposals],
      };
    }
  }
  return next;
}

function derivePhase(state: WorkbenchState): WorkbenchPhase {
  if (state.error) return "error";
  if (state.pendingInteraction) return "pending_interaction";
  if (state.surfaces.length > 0) return "surfaces_rendered";
  return "loading";
}

export function workbenchReducer(
  state: WorkbenchState,
  action: WorkbenchAction
): WorkbenchState {
  switch (action.type) {
    case "LOAD_TRANSCRIPT": {
      const reset: WorkbenchState = { ...state, phase: "loading", surfaces: [], pendingInteraction: null, memoryProposals: [], error: null };
      const next = applyEvents(reset, action.events);
      return { ...next, phase: derivePhase(next) };
    }
    case "APPEND_EVENTS": {
      const next = applyEvents(state, action.events);
      return { ...next, phase: derivePhase(next) };
    }
    case "SET_PHASE":
      return { ...state, phase: action.phase, error: action.phase === "error" ? state.error : null };
    case "SET_ERROR":
      return { ...state, phase: "error", error: action.error };
    case "CLEAR_PENDING":
      return { ...state, pendingInteraction: null, phase: "resolved" };
    default:
      return state;
  }
}
