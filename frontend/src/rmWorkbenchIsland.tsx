import { createRoot } from "react-dom/client";
import RmWorkbenchHost from "./RmWorkbenchHost";

const MOUNT_ID = "rmWorkbenchIslandRoot";

function mount() {
  const container = document.getElementById(MOUNT_ID);
  if (!container) {
    console.warn("[rm_workbench_island] mount point not found:", MOUNT_ID);
    return;
  }

  console.log("[rm_workbench_island] mounting embedded RmWorkbenchHost");
  container.removeAttribute("hidden");

  createRoot(container).render(
    <RmWorkbenchHost mode="embedded" />
  );
}

mount();
