export interface SurfaceData {
  surfaceId: string;
  surface: string;
  data: Record<string, unknown>;
  components?: unknown[];
}

export interface PendingInteraction {
  interaction_id: string;
  surface_id: string;
  action: string;
  blocking: boolean;
  schema: Record<string, unknown>;
}
