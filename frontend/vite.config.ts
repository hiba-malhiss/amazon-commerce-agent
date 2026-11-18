import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

const BACKEND = "http://127.0.0.1:8000";

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      "/threads": BACKEND,
      "/interactions": BACKEND,
      "/knowledge-bases": { target: BACKEND, ws: true }, // + the live document updates
      "/health": BACKEND,
      "/ws": { target: BACKEND, ws: true },
    },
  },
});
