import type { ReactNode } from "react";
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
import { PrimitiveErrorBoundary } from "./PrimitiveErrorBoundary";

interface Props {
  surfaces: SurfaceData[];
  interactionDisabled: boolean;
  onConfirmSelection: (selectedIds: string[]) => void;
}

function renderGenericPrimitive(s: SurfaceData) {
  const dataObj = (s.data as Record<string, unknown>) ?? {};
  const rawProps = dataObj.props;
  const props = (typeof rawProps === "object" && rawProps !== null
    ? rawProps
    : {}) as Record<string, unknown>;
  switch (s.surface) {
    case "MetricCard":
      return <MetricCard props={props as never} />;
    case "DataTable":
      return <DataTable props={props as never} />;
    case "LineChart":
      return <LineChartBlock props={props as never} />;
    case "BarChart":
      return <BarChartBlock props={props as never} />;
    case "PieChart":
      return <PieChartBlock props={props as never} />;
    case "ChoiceList":
      return <ChoiceList props={props as never} />;
    default:
      return null;
  }
}

const GENERIC_PRIMITIVES = new Set([
  "MetricCard", "DataTable", "LineChart", "BarChart", "PieChart", "ChoiceList",
]);

function renderSurface(
  s: SurfaceData,
  interactionDisabled: boolean,
  onConfirmSelection: (selectedIds: string[]) => void,
): ReactNode {
  if (GENERIC_PRIMITIVES.has(s.surface)) {
    return renderGenericPrimitive(s);
  }
  switch (s.surface) {
    case "CustomerProfileCard":
      return <CustomerProfileCard data={s.data} />;
    case "ProductFitTable":
      return (
        <ProductFitTable
          data={s.data}
          disabled={interactionDisabled}
          onConfirm={onConfirmSelection}
        />
      );
    case "BriefExportPanel":
      return <BriefExportPanel data={s.data} />;
    default:
      return (
        <div style={{ padding: 12, border: "1px solid #e4e7ec", borderRadius: 6 }}>
          未识别的组件面板：{s.surface}
        </div>
      );
  }
}

export function A2UISurfaceRenderer({
  surfaces,
  interactionDisabled,
  onConfirmSelection,
}: Props) {
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
      {surfaces.map((s) => (
        <PrimitiveErrorBoundary
          key={s.surfaceId}
          primitiveName={s.surface || s.surfaceId}
        >
          {renderSurface(s, interactionDisabled, onConfirmSelection)}
        </PrimitiveErrorBoundary>
      ))}
    </div>
  );
}
