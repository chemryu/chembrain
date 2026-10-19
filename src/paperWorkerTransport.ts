/** Encode bytes directly: decoding worker source as text can alter its bytes. */
export function workerDataUrl(bytes: Uint8Array): string {
  const chunks: string[] = [];
  // A multiple of three keeps padding confined to the final base64 chunk.
  const chunkSize = 24_576;
  for (let offset = 0; offset < bytes.length; offset += chunkSize) {
    const chunk = bytes.subarray(offset, offset + chunkSize);
    let binary = '';
    for (const byte of chunk) binary += String.fromCharCode(byte);
    chunks.push(btoa(binary));
  }
  return 'data:text/javascript;base64,' + chunks.join('');
}

export type WorkerStage = 'construction' | 'loading' | 'metadata' | 'ready' | 'text' | 'render';
export type WorkerFailureEvent = 'error' | 'messageerror' | 'timeout' | 'constructor';

/** Native strings are untrusted: emit fixed categories, never redacted excerpts. */
export function workerDiagnostic(
  event: WorkerFailureEvent, stage: WorkerStage,
  detail: { message?: unknown; filename?: unknown; name?: unknown; line?: unknown; column?: unknown },
  environment: { userAgent?: unknown; protocol?: unknown; origin?: unknown },
) {
  const ua = typeof environment.userAgent === 'string' ? environment.userAgent.slice(0, 512) : '';
  const browserMatch = /\b(Edg)\/(\d{1,4})(?:\.(\d{1,4})){0,3}(?![\d.])/.exec(ua)
    ?? /\b(Chrome|Firefox|Version)\/(\d{1,4})(?:\.(\d{1,4})){0,3}(?![\d.])/.exec(ua);
  const browser = browserMatch ? ({ Edg: 'edge', Chrome: 'chromium', Firefox: 'firefox', Version: 'safari' } as const)[browserMatch[1] as 'Edg' | 'Chrome' | 'Firefox' | 'Version'] : 'unknown';
  const message = typeof detail.message === 'string' ? detail.message.slice(0, 1024).toLowerCase() : '';
  const errorCategory = !message ? 'detail-unavailable' : /syntax|unexpected token/.test(message) ? 'syntax' : /security|cross.origin|not allowed|denied/.test(message) ? 'security' : /network|fetch|load/.test(message) ? 'load' : /clone|deserial/.test(message) ? 'serialization' : 'unclassified';
  const filename = typeof detail.filename === 'string' ? detail.filename : '';
  const sourceCategory = !filename ? 'unavailable' : filename.startsWith('data:') ? 'data' : filename.startsWith('blob:') ? 'blob' : filename.startsWith('file:') ? 'file' : /^https?:/.test(filename) ? 'http' : 'other';
  const names = ['Error', 'TypeError', 'SyntaxError', 'SecurityError', 'NetworkError', 'DataCloneError', 'AbortError', 'TimeoutError'];
  const position = (value: unknown) => typeof value === 'number' && Number.isSafeInteger(value) && value >= 0 && value <= 10_000_000 ? value : null;
  return {
    event, stage, browser, version: browserMatch?.[2] ?? 'unknown',
    protocol: typeof environment.protocol === 'string' && ['file:', 'http:', 'https:', 'data:', 'blob:'].includes(environment.protocol) ? environment.protocol : 'other',
    opaqueOrigin: environment.origin === 'null', transport: 'data-url', module: true,
    errorName: typeof detail.name === 'string' && names.includes(detail.name) ? detail.name : 'unknown',
    errorCategory, sourceCategory, line: position(detail.line), column: position(detail.column),
  };
}
