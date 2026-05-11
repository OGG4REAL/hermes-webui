import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import path from "path";

export default defineConfig({
  plugins: [react()],
  build: {
    lib: {
      entry: path.resolve(__dirname, "src/rmWorkbenchIsland.tsx"),
      formats: ["iife"],
      name: "RmWorkbenchIsland",
      fileName: () => "rm-workbench-island.js",
    },
    outDir: path.resolve(__dirname, "../static/rm-workbench"),
    emptyOutDir: true,
    cssCodeSplit: false,
  },
  define: {
    "process.env.NODE_ENV": JSON.stringify("production"),
  },
});
