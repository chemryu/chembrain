import { defineConfig, loadEnv } from "vite";
import react from "@vitejs/plugin-react";
import { readFileSync, readdirSync } from "node:fs";
const portableModule = "virtual:chembrain-portable-data";
export default defineConfig(({mode}) => ({
  plugins: [react(), {
    name: "chembrain-portable-data",
    resolveId(id) { if (id === portableModule) return "\0" + portableModule; },
    load(id) {
      if (id !== "\0" + portableModule) return;
      if (mode !== "portable") return "export const library=null;export const depictions={};";
      const library = JSON.parse(readFileSync(new URL("./public/library.json", import.meta.url), "utf8"));
      const directory = new URL("./public/structures/", import.meta.url);
      const depictions = Object.fromEntries(readdirSync(directory).filter(file => file.endsWith(".svg"))
        .map(file => [file, readFileSync(new URL(file, directory), "utf8")]));
      return "export const library=" + JSON.stringify(library) + ";export const depictions=" + JSON.stringify(depictions) + ";";
    },
  }],
  base: mode === "portable" ? "./" : loadEnv(mode, ".", "").CHEMBRAIN_BASE || "/",
  build: mode === "portable" ? {
    modulePreload: false,
    cssCodeSplit: false,
    assetsInlineLimit: 10_000_000,
    rolldownOptions: { output: { codeSplitting: false } },
  } : undefined,
  server: { proxy: { "/api": "http://127.0.0.1:8000" } },
}));
