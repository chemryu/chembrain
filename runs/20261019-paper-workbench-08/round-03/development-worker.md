# Development — bounded native worker transport

Scope: `src/paperPdf.ts`, new internal `src/paperWorkerTransport.ts`, and `tests/test_paper_worker_transport.py`. Implements the formal round-03 plan; no independent approval. Root owns packaging, full builds, exact-source freeze and actual-file CI evidence.

The existing embedded gzip decompresses into original worker bytes and encodes directly into the standard `data:text/javascript;base64,` representation. Base64 chunks are 24,576 bytes (a multiple of three); binary bytes never pass through a Unicode text decoder or FileReader. The real native Worker retains `type: 'module'`, `name: 'chembrain-local-pdf'` and its explicit PDF.js port. No worker-source transformation, external fetch, fallback, retry or dependency change. The pinned original worker SHA-256 remains `9536359f1b8367850d485731ca1d5e45c159a7b7a0912325e539937aa21ceb18`.

Native `error` and `messageerror` handlers suppress default reporting before emitting a fixed-category diagnostic. Console prefix is `PDF worker diagnostic`; the object contains event/stage, browser/major version, protocol/opaque-origin category, data-URL/module transport, whitelisted error name, fixed error/source categories and finite bounded line/column or null. At most three diagnostics per open document. Arbitrary native strings, URLs, source filenames, paths and message payloads never enter this object. Missing native detail is explicit. Visible worker failure text is concise English and asks for a current local-module-worker-capable browser.

The 45-second operation race now covers metadata, text and rendering as well as loading. Native failures reject pending operations; explicit destruction rejects pending work with AbortError. Existing size/page/encryption checks, page disposal, render epochs and cancellation remain. Destruction gives PDF.js at most one second to acknowledge termination; a nested finally always reaches native termination even if PDF.js destroy throws. It removes native listeners and releases URL/native/PDF task/document/render/source-buffer references. The URL reference is released immediately after successful construction; data URLs do not use object-URL revocation.

Executed in the existing checkout:

- `.venv/bin/python -m pytest -q tests/test_paper_worker_transport.py tests/test_paper_pdf_candidates.py`: **8 PASS**. Four new tests execute the actual TypeScript helper in Node: Unicode and arbitrary byte preservation around chunk boundaries; actual pinned dependency byte/hash preservation; adversarial paths/huge base64/nonfinite input privacy; useful diagnostic categories/locations.
- `npx tsc --noEmit`: **PASS**.

No shared builds or commits performed by this scoped Development role. Browser/native lifecycle and full actual-file checks belong to coordinated smoke/root evidence and are not claimed by these helper tests. The historical CI failure cause remains unresolved; a data-module transport candidate is not actual-file delivery approval.
