import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// In dev, the API runs on uvicorn at :8765. Proxy the API paths so the
// frontend can use relative URLs (which also work in the single-process
// build, where FastAPI serves both the SPA and the API).
const API_TARGET = process.env.VITE_API_TARGET ?? "http://localhost:8765";

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      "/filings": API_TARGET,
      "/search": API_TARGET,
      "/stats": API_TARGET,
    },
  },
});
