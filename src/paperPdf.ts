import { AnnotationMode, getDocument, PDFWorker, VerbosityLevel } from 'pdfjs-dist';
import type { PDFDocumentLoadingTask, PDFDocumentProxy, PDFPageProxy, RenderTask } from 'pdfjs-dist';
import compressedWorker from 'virtual:chembrain-pdf-worker';
import { workerDataUrl, workerDiagnostic } from './paperWorkerTransport';
import type { WorkerFailureEvent, WorkerStage } from './paperWorkerTransport';

export { extractCandidates } from './paperPdfCandidates';
export type { DoiCandidate, SmilesCandidate, PaperCandidates } from './paperPdfCandidates';

export const PDF_MAX_BYTES = 30 * 1024 * 1024;
export const PDF_MAX_PAGES = 400;
const MAX_PAGE_TEXT = 500_000;
const LOAD_TIMEOUT_MS = 45_000;

export interface PaperPdf {
  /** Exact original file SHA-256. It is an identity pointer, not PDF.js's document ID. */
  readonly fingerprint: string;
  readonly hash: string;
  readonly pageCount: number;
  getPageText(page: number): Promise<string>;
  renderPage(page: number, canvas: HTMLCanvasElement): Promise<void>;
  destroy(): Promise<void>;
}

function abortError(): DOMException {
  return new DOMException('This PDF operation was replaced or the PDF was closed.', 'AbortError');
}

function readableError(error: unknown, action: string): Error {
  const name = error instanceof Error ? error.name : '';
  if (name === 'AbortError' || name === 'RenderingCancelledException') return abortError();
  if (name === 'PasswordException') return new Error('Encrypted or password-protected PDFs are not supported. Open an unencrypted copy locally.');
  if (name === 'InvalidPDFException') return new Error('This file is not a readable PDF, or its PDF data is damaged.');
  if (error instanceof Error && error.message.startsWith('PDF ')) return error;
  return new Error(`PDF ${action} failed. The file may be damaged or require unsupported fonts, images, or features. Try an unencrypted PDF in a current Chrome or Edge browser.`);
}

async function workerUrl(): Promise<string> {
  if (typeof Worker === 'undefined' || typeof DecompressionStream === 'undefined' || !globalThis.crypto?.subtle) {
    throw new Error('PDF review needs a current Chrome or Edge browser with local module workers and gzip support.');
  }
  const raw = atob(compressedWorker);
  const compressed = new Uint8Array(raw.length);
  for (let index = 0; index < raw.length; index++) compressed[index] = raw.charCodeAt(index);
  const stream = new Blob([compressed]).stream().pipeThrough(new DecompressionStream('gzip'));
  return workerDataUrl(new Uint8Array(await new Response(stream).arrayBuffer()));
}

/**
 * Open a local file strictly in memory. No URLs, uploads, storage, document
 * scripts, link overlays, external fonts/CMaps, or OCR are used. Only selected
 * reviewed facts may leave the workbench through its separate export contract.
 */
export async function readPdf(file: File): Promise<PaperPdf> {
  if (!file || !Number.isSafeInteger(file.size) || file.size < 1) throw new Error('Choose a non-empty local PDF file.');
  if (file.size > PDF_MAX_BYTES) throw new Error('PDF files must be 30 MB or smaller.');
  let data: ArrayBuffer;
  try { data = await file.arrayBuffer(); } catch { throw new Error('The local PDF file could not be read. Choose it again.'); }
  const header = new TextDecoder('ascii').decode(new Uint8Array(data, 0, Math.min(data.byteLength, 1024)));
  if (!header.includes('%PDF-')) throw new Error('Choose a PDF file. Its PDF file header was not found.');
  if (!globalThis.crypto?.subtle) throw new Error('PDF review needs a current browser with local SHA-256 support.');
  const digest = await crypto.subtle.digest('SHA-256', data);
  const hash = [...new Uint8Array(digest)].map(value => value.toString(16).padStart(2, '0')).join('');
  let url: string | undefined;
  let nativeWorker: Worker | undefined;
  let pdfWorker: PDFWorker | undefined;
  let loading: PDFDocumentLoadingTask | undefined;
  let document: PDFDocumentProxy | undefined;
  let activeRender: RenderTask | undefined;
  let renderEpoch = 0;
  let closed = false;
  let closing: Promise<void> | undefined;
  let workerFailure: Error | undefined;
  let stage: WorkerStage = 'construction';
  let diagnosticCount = 0;
  let rejectWorker!: (reason: Error) => void;
  const failedWorker = new Promise<never>((_resolve, reject) => { rejectWorker = reject; });
  // A native event may arrive between operations, when no race is observing it.
  void failedWorker.catch(() => undefined);
  const diagnose = (event: WorkerFailureEvent, detail: Parameters<typeof workerDiagnostic>[2] = {}) => {
    if (diagnosticCount++ >= 3) return;
    console.warn('PDF worker diagnostic', workerDiagnostic(event, stage, detail, {
      userAgent: navigator.userAgent, protocol: location.protocol, origin: globalThis.origin,
    }));
  };
  const failWorker = () => {
    if (closed || workerFailure) return;
    workerFailure = new Error('PDF worker could not run locally. Reopen the PDF in a current Chrome or Edge browser that allows local module workers.');
    rejectWorker(workerFailure);
    void destroy().catch(() => undefined);
  };
  const onWorkerError = (event: ErrorEvent) => {
    // Default browser reporting can include the complete multi-megabyte data URL.
    event.preventDefault();
    diagnose('error', { message: event.message, filename: event.filename, name: event.error?.name, line: event.lineno, column: event.colno });
    failWorker();
  };
  const onMessageError = (event: MessageEvent) => {
    event.preventDefault();
    diagnose('messageerror'); // Never inspect or print event.data.
    failWorker();
  };
  const workerOperation = async <T>(operation: Promise<T>): Promise<T> => {
    let timeout: ReturnType<typeof setTimeout> | undefined;
    try {
      return await Promise.race([operation, failedWorker, new Promise<never>((_resolve, reject) => {
        timeout = setTimeout(() => {
          diagnose('timeout');
          const error = new Error('PDF operation took too long. Reopen a smaller or simpler unencrypted PDF.');
          workerFailure = error;
          rejectWorker(error);
          reject(error);
          void destroy().catch(() => undefined);
        }, LOAD_TIMEOUT_MS);
      })]);
    } finally { clearTimeout(timeout); }
  };

  const destroy = (): Promise<void> => {
    if (closing) return closing;
    closed = true;
    if (!workerFailure) rejectWorker(abortError());
    renderEpoch++;
    try { activeRender?.cancel(); } catch { /* Native worker may already be gone. */ }
    closing = (async () => {
      let timeout: ReturnType<typeof setTimeout> | undefined;
      try {
        // A crashed worker cannot acknowledge PDF.js's Terminate message. Give
        // orderly cleanup a brief chance, then always free the native worker.
        await Promise.race([
          loading?.destroy().catch(() => undefined),
          new Promise<void>(resolve => { timeout = setTimeout(resolve, 1_000); }),
        ]);
      } finally {
        clearTimeout(timeout);
        try { pdfWorker?.destroy(); }
        finally {
          try {
            nativeWorker?.removeEventListener('error', onWorkerError);
            nativeWorker?.removeEventListener('messageerror', onMessageError);
            nativeWorker?.terminate();
          } finally {
            // Data URLs need no revocation. Drop every owner after terminating.
            url = undefined;
            nativeWorker = undefined;
            pdfWorker = undefined;
            loading = undefined;
            activeRender = undefined;
            document = undefined;
            data = new ArrayBuffer(0);
          }
        }
      }
    })();
    return closing;
  };
  const assertPage = (page: number): PDFDocumentProxy => {
    if (workerFailure) throw workerFailure;
    if (closed || !document) throw abortError();
    if (!Number.isSafeInteger(page) || page < 1 || page > document.numPages) throw new Error(`PDF page must be between 1 and ${document.numPages}.`);
    return document;
  };

  try {
    url = await workerUrl();
    try { nativeWorker = new Worker(url, { type: 'module', name: 'chembrain-local-pdf' }); }
    catch (error) {
      diagnose('constructor', { name: error instanceof Error ? error.name : undefined });
      throw new Error('PDF worker could not start locally. Use a current Chrome or Edge browser that allows local module workers.');
    }
    url = undefined; // Worker owns its script; do not retain another encoded copy.
    nativeWorker.addEventListener('error', onWorkerError);
    nativeWorker.addEventListener('messageerror', onMessageError);
    stage = 'loading';
    pdfWorker = PDFWorker.create({ port: nativeWorker, verbosity: VerbosityLevel.ERRORS });
    loading = getDocument({
      data: new Uint8Array(data), worker: pdfWorker,
      // PDF.js 6 removed the old isEvalSupported option and dynamic JS compiler.
      useWasm: false, useWorkerFetch: false,
      disableFontFace: true, useSystemFonts: false,
      disableAutoFetch: true, disableStream: true, disableRange: true,
      enableXfa: false, stopAtErrors: true,
      maxImageSize: 25_000_000, canvasMaxAreaInBytes: 16_000_000,
      verbosity: VerbosityLevel.ERRORS,
    });
    document = await workerOperation(loading.promise);
    if (document.numPages > PDF_MAX_PAGES) throw new Error('PDF files must contain 400 pages or fewer. Split the file locally before review.');
    stage = 'metadata';
    const metadata = await workerOperation(document.getMetadata());
    if ((metadata.info as Record<string, unknown>).EncryptFilterName) {
      throw new Error('PDF encrypted documents are not supported. Open an unencrypted copy locally.');
    }
    const pageCount = document.numPages;
    stage = 'ready';
    return {
      fingerprint: hash, hash, pageCount,
      async getPageText(pageNumber) {
        const pdf = assertPage(pageNumber);
        let page: PDFPageProxy | undefined;
        try {
          stage = 'text';
          page = await workerOperation(pdf.getPage(pageNumber));
          if (closed) throw abortError();
          const content = await workerOperation(page.getTextContent({ includeMarkedContent: false, disableNormalization: false }));
          if (closed) throw abortError();
          const parts: string[] = [];
          let length = 0;
          let previous: { y: number; end: number; eol: boolean } | undefined;
          for (const item of content.items) {
            if (!('str' in item)) continue;
            const y = Number(item.transform[5]);
            const x = Number(item.transform[4]);
            const separator = previous ? (previous.eol || Math.abs(previous.y - y) > 2 ? '\n' : x > previous.end + 1 ? ' ' : '') : '';
            length += separator.length + item.str.length;
            if (length > MAX_PAGE_TEXT) throw new Error('PDF page text exceeds the 500,000-character review limit. Review a smaller section locally.');
            parts.push(separator, item.str);
            previous = { y, end: x + item.width, eol: item.hasEOL };
          }
          return parts.join('');
        } catch (error) { throw readableError(error, 'text extraction'); }
        finally { page?.cleanup(); }
      },
      async renderPage(pageNumber, canvas) {
        const pdf = assertPage(pageNumber);
        const epoch = ++renderEpoch;
        const oldRender = activeRender;
        activeRender = undefined;
        oldRender?.cancel();
        if (oldRender) await oldRender.promise.catch(() => undefined);
        if (closed || epoch !== renderEpoch) throw abortError();
        canvas.width = 0;
        canvas.height = 0;
        let page: PDFPageProxy | undefined;
        let render: RenderTask | undefined;
        try {
          stage = 'render';
          page = await workerOperation(pdf.getPage(pageNumber));
          if (closed || epoch !== renderEpoch) throw abortError();
          const base = page.getViewport({ scale: 1 });
          if (!(base.width > 0 && base.height > 0 && Number.isFinite(base.width) && Number.isFinite(base.height))) throw new Error('PDF page dimensions are not valid.');
          const scale = Math.min(2, 1800 / base.width, 2400 / base.height, Math.sqrt(4_000_000 / (base.width * base.height)));
          const viewport = page.getViewport({ scale });
          canvas.width = Math.max(1, Math.ceil(viewport.width));
          canvas.height = Math.max(1, Math.ceil(viewport.height));
          if (!canvas.getContext('2d')) throw new Error('PDF page canvas is unavailable in this browser.');
          render = page.render({ canvas, viewport, annotationMode: AnnotationMode.DISABLE, background: 'rgb(255,255,255)' });
          activeRender = render;
          await workerOperation(render.promise);
          if (closed || epoch !== renderEpoch) throw abortError();
        } catch (error) {
          if (epoch === renderEpoch) { canvas.width = 0; canvas.height = 0; }
          throw readableError(error, 'page rendering');
        } finally {
          if (activeRender === render) activeRender = undefined;
          page?.cleanup();
        }
      },
      destroy,
    };
  } catch (error) {
    await destroy().catch(() => undefined);
    throw readableError(error, 'opening');
  }
}
