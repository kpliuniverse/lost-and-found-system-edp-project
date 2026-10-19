import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// Any request to /api is forwarded to the FastAPI server, so no CORS fuss in development.
const backendTarget = process.env.VITE_PROXY_TARGET || "http://127.0.0.1:8000";

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: { "/api": backendTarget },
  },
});
