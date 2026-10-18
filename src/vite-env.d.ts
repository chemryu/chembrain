/// <reference types="vite/client" />
declare module "virtual:chembrain-rdkit-wasm" {
  const gzipBase64: string;
  export default gzipBase64;
}
declare module "virtual:chembrain-portable-data" {
  export const library: unknown;
  export const depictions: Record<string, string>;
}
