import { defineConfig, loadEnv } from "vite";
import react from "@vitejs/plugin-react";
export default defineConfig(({mode}) => ({
  plugins: [react()],
  base: loadEnv(mode, ".", "").CHEMBRAIN_BASE || "/",
  server: { proxy: { "/api": "http://127.0.0.1:8000" } },
}));
