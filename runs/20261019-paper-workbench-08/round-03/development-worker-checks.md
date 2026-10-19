# Development — worker smoke and integrity boundary

Development role only; no independent approval. Candidate source is not frozen here; root owns source identity, shared builds, aggregate results and CI receipts.

Changed `scripts/paper_workbench_smoke.py`, added stdlib-only `scripts/paper_worker_smoke.py` and meaningful `tests/test_paper_worker_resource_guard.py`.

The validator accepts exactly `data:text/javascript;base64,` followed by canonical standard base64 of unchanged pinned PDF.js 6.4.299 worker bytes. It verifies decoded byte equality, hard-pinned dependency SHA-256 and release paper manifest `pdf_worker_sha256`, and requires `worker_transport=native-module-data-url`. Changed/truncated/foreign bytes, arbitrary data scripts, external/blob URLs, noncanonical encoding, wrong MIME and manifest mismatch are rejected. URL values stay in memory. Failures expose only finite category/length/digest, never the URI or payload. The helper imports only standard-library modules so normal pytest collection does not depend on Playwright.

A test-only constructor Proxy retains genuine native Worker construction and observes module/name, bounded errors and termination. Playwright genuine worker events independently validate the exact URL and count closed workers; app workers require module type and `chembrain-local-pdf` name. Request/console/page-error records retain finite summaries. First-PDF failure emits browser/protocol/opaque category, safe worker/lifecycle/console information and explicit native-detail presence before raising a short assertion. The terminal failure boundary preserves exit status 1 and emits only exception category/length/digest plus at most twelve traceback code basenames/function names/numeric lines, suppressing original Playwright exception strings and Aria snapshots. Console diagnostics accept fixed adapter enums only, rejecting forged filename/text fields. Focused tests cover both boundaries. No application public debug API, PDF page/source contents or screenshots were added.

Default smoke still opens the actual release file URI, performs real PDF canvas/pixels/text and all existing curation, private storage and two-program transfer profiles. `--http-only` remains explicitly supplemental. An added normal HTTP `sandbox=allow-scripts` opaque-origin iframe executes the actual static data-module worker and requires PDF.js worker→main ready, one genuine worker event and no external resources; it terminates the worker and closes its context. This is explicitly **ready-only**, never parse/render/file proof. Full app PDF parsing/rendering/text remains mandatory. Added error/messageerror injection profiles dispatch DOM events on a genuine native worker, require closure within three seconds, then require valid reselect and real app PDF render/text. They do not fake a success worker.

Focused validation performed in the existing environment:

- `.venv/bin/python -m pytest -q tests/test_paper_worker_resource_guard.py`: **13 PASS**.
- `.venv/bin/python -m py_compile scripts/paper_worker_smoke.py scripts/paper_workbench_smoke.py`: **PASS**.
- Direct `opaque_worker_ready(...)` on normal managed Chromium, no additional browser/security flags: **PASS ready-only**; actual exact pinned worker executes in HTTP sandbox opaque origin, terminates and closes context.

Shared builds, full HTTP app smoke/new failure profiles and all actual-file gates are **NOT RUN by this worker-checks role**. Root must record aggregate results after its coordinated build pair. Managed file policy must not be bypassed; normal CI actual-file and complete transfer remain required for acceptance. No source/app edits, dependency changes, generated PDF fixtures, worker base64/source copies, shared builds or commits were made by this role.
