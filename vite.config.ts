import { defineConfig, loadEnv } from "vite";
import react from "@vitejs/plugin-react";
import { readFileSync, readdirSync } from "node:fs";
import { gzipSync } from "node:zlib";
const portableModule = "virtual:chembrain-portable-data";
const rdkitModule = "virtual:chembrain-rdkit-wasm";
const pdfModule = "virtual:chembrain-pdf-worker";
const isPortable = (mode:string) => mode === "portable" || mode === "paper-portable";
export default defineConfig(({mode}) => ({
  plugins: [react(), {
    name: "chembrain-portable-data",
    transform(code, id) {
      if (!id.replaceAll('\\', '/').endsWith('/pdfjs-dist/build/pdf.mjs')) return;
      const wrapper = /this\._createCDNWrapper = url => \{[\s\S]*?\n    \};/;
      const fallback = /const worker = await import\([\s\S]*?this\.workerSrc\);\s*return worker\.WorkerMessageHandler;/;
      if (!wrapper.test(code) || !fallback.test(code)) throw new Error('Pinned PDF worker fallback changed; review offline packaging.');
      return code.replace(wrapper, 'this._createCDNWrapper = () => { throw new Error("External PDF workers are disabled."); };')
        .replace(fallback, 'throw new Error("The bundled local PDF worker is required.");');
    },
    resolveId(id) { if (id === portableModule || id === rdkitModule || id === pdfModule) return "\0" + id; },
    load(id) {
      if (id === "\0" + pdfModule) {
        const bytes = readFileSync(new URL("./node_modules/pdfjs-dist/build/pdf.worker.min.mjs", import.meta.url));
        return "export default " + JSON.stringify(gzipSync(bytes, { level: 9 }).toString("base64")) + ";";
      }
      if (id === "\0" + rdkitModule) {
        const bytes = readFileSync(new URL("./node_modules/@rdkit/rdkit/dist/RDKit_minimal.wasm", import.meta.url));
        return "export default " + JSON.stringify(gzipSync(bytes, { level: 9 }).toString("base64")) + ";";
      }
      if (id !== "\0" + portableModule) return;
      if (mode !== "portable") return "export const library=null;export const depictions={};";
      const library = JSON.parse(readFileSync(new URL("./public/library.json", import.meta.url), "utf8"));
      const directory = new URL("./public/structures/", import.meta.url);
      const depictions = Object.fromEntries(readdirSync(directory).filter(file => file.endsWith(".svg"))
        .map(file => [file, readFileSync(new URL(file, directory), "utf8")]));
      return "export const library=" + JSON.stringify(library) + ";export const depictions=" + JSON.stringify(depictions) + ";";
    },
  }],
  publicDir: mode === "paper-portable" ? false : "public",
  base: isPortable(mode) ? "./" : loadEnv(mode, ".", "").CHEMBRAIN_BASE || "/",
  build: isPortable(mode) ? {
    modulePreload: false,
    cssCodeSplit: false,
    assetsInlineLimit: 10_000_000,
    rolldownOptions: { ...(mode === "paper-portable" ? {input:"paper.html"} : {}), output: { codeSplitting: false } },
  } : undefined,
  server: { proxy: { "/api": "http://127.0.0.1:8000" } },
}));
