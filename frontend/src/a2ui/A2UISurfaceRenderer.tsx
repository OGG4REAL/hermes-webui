import type { SurfaceData } from "./types";
import { CustomerProfileCard } from "../rm/surfaces/CustomerProfileCard";
import { ProductFitTable } from "../rm/surfaces/ProductFitTable";
import { BriefExportPanel } from "../rm/surfaces/BriefExportPanel";
import { MetricCard } from "./primitives/MetricCard";
import { DataTable } from "./primitives/DataTable";
import { LineChartBlock } from "./primitives/LineChartBlock";
import { BarChartBlock } from "./primitives/BarChartBlock";
import { PieChartBlock } from "./primitives/PieChartBlock";
import { ChoiceList } from "./primitives/ChoiceList";

interface Props {
  surfaces: SurfaceData[];
  interactionDisabled: boolean;
  onConfirmSelection: (selectedIds: string[]) => void;
}

function renderGenericPrimitive(s: SurfaceData) {
  const props = (s.data as Record<string, unknown>).props as Record<string, unknown>;
  switch (s.surface) {
    case "MetricCard":
      return <MetricCard key={s.surfaceId} props={props as never} />;
    case "DataTable":
      return <DataTable key={s.surfaceId} props={props as never} />;
    case "LineChart":
      return <LineChartBlock key={s.surfaceId} props={props as never} />;
    case "BarChart":
      return <BarChartBlock key={s.surfaceId} props={props as never} />;
    case "PieChart":
      return <PieChartBlock key={s.surfaceId} props={props as never} />;
    case "ChoiceList":
      return <ChoiceList key={s.surfaceId} props={props as never} />;
    default:
      return null;
  }
}

const GENERIC_PRIMITIVES = new Set([
  "MetricCard", "DataTable", "LineChart", "BarChart", "PieChart", "ChoiceList",
]);

export function A2UISurfaceRenderer({
  surfaces,
  interactionDisabled,
  onConfirmSelection,
}: Props) {
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
      {surfaces.map((s) => {
        if (GENERIC_PRIMITIVES.has(s.surface)) {
          return renderGenericPrimitive(s);
        }
        switch (s.surface) {
          case "CustomerProfileCard":
            return <CustomerProfileCard key={s.surfaceId} data={s.data} />;
          case "ProductFitTable":
            return (
              <ProductFitTable
                key={s.surfaceId}
                data={s.data}
                disabled={interactionDisabled}
                onConfirm={onConfirmSelection}
              />
            );
          case "BriefExportPanel":
            return <BriefExportPanel key={s.surfaceId} data={s.data} />;
          default:
            return (
              <div key={s.surfaceId} style={{ padding: 12, border: "1px solid #e4e7ec", borderRadius: 6 }}>
                未识别的组件面板：{s.surface}
              </div>
            );
        }
      })}
    </div>
  );
}
