import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

const backendTarget = process.env.RM_WORKBENCH_BACKEND ?? "http://127.0.0.1:8787";

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      "/api": {
        target: backendTarget,
        changeOrigin: true,
        configure(proxy) {
          proxy.on("proxyReq", (proxyReq, req) => {
            if (req.headers.host) {
              proxyReq.setHeader("X-Forwarded-Host", req.headers.host);
            }
          });
        },
      },
    },
  },
});
