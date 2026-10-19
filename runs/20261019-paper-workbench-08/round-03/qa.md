# Independent QA — Paper Workbench / round-03

- Separate Independent QA role. Exact inspected source: **`bc39eda53b22a5b333e9fd7d432005653beab546`**, `codex/gpt-agent-workflow`.
- Inputs: repository/role/current-request instructions; formal round-03 Planning, Development/helper reports and raw local evidence; complete round-02 QA/Revision/handoff and controlled worker diagnosis. Prior rejected-source reports remain unchanged. No earlier approval transfers.
- **Final decision: CHANGES_REQUESTED. QA-PW-03/P2: confirmed required-test metadata snapshot race.** QA-PW-01 remains resolved. QA-PW-02 has passing bounded local implementation/runtime regressions, but its actual-file resolution remains **NOT VERIFIED** because fresh CI failed earlier in hosted metadata verification and skipped both file gates. This run does not demonstrate a recurring worker failure. No delivery approval. The terminal supplement below supersedes the initial pending cutoff.
- This role changed only `round-03/qa.md` inside the checkout, no application/tests/build inputs/shared `dist`/release or Git HEAD. Independent synthetic fixtures were temporary and browser/context closed after use.

## Source and failure-boundary review

`paperPdf.ts` retains a genuine native Worker with explicit PDF.js port, `type:'module'`, stable private name and exact embedded pinned dependency bytes. The transport alone changes from Blob to a standard JavaScript/base64 data URL. The encoder handles arbitrary bytes without Unicode text conversion; its 24576-byte chunks are multiples of three, so joined base64 padding remains valid. No worker-source rewrite, dependency upgrade, external fetch/CDN, fake worker, main-thread fallback or transport retry was introduced. Original worker digest remains `9536359f1b8367850d485731ca1d5e45c159a7b7a0912325e539937aa21ceb18`.

The adapter emits finite fixed diagnostics, with whitelisted browser/major version, stage/event/protocol/origin/transport, category/error-name and bounded integer location. Arbitrary native strings, filenames, paths, URLs and MessageEvent data never enter its logged object. Native error default reporting is prevented to avoid giant data-URL reports. Diagnostic count is capped. Visible errors stay concise English. Construction, native error/messageerror and 45-second operation timeout paths reject loading/metadata/text/render safely. Destruction bounds PDF.js teardown to one second, removes listeners, unconditionally terminates native Worker through nested finally blocks and releases buffer/task/URL references. Data URLs require no Blob revocation. Existing size/page/encrypted/invalid limits, render epoch and source-change guards remain.

The test resource boundary accepts exactly canonical `data:text/javascript;base64,` for the expected unchanged dependency. It strictly base64-decodes and compares all bytes plus hard-pinned dependency/manifest SHA, expected transport, module/name construction and genuine Playwright worker events. Changed/truncated/foreign/unrelated scripts, MIME variants, external/blob worker addresses and manifest mismatches fail. Request handling has no arbitrary data exception. Existing separate Blob module/download handling is paired with strict worker-event validation, so it cannot make a foreign Blob worker pass. Constructor observation wraps the actual native constructor; failure profiles inject error/messageerror events on genuine native Workers without inventing a success worker. URL values stay in memory, summaries retain only category/length/digest, and the terminal exception boundary removes arbitrary Playwright Aria snapshots/source paths/payloads while preserving finite code-frame identifiers.

The normal HTTP sandbox regression proves actual pinned native module initialization in an opaque origin and is correctly labelled **ready-only**. It does not parse/render a PDF and is not actual-file proof. Full application smoke separately requires PDF pixels/text, native workers, explicit source checking and complete two-program transfer. Historical Chromium151's exact native event remains unavailable; neither the old controlled Chromium154 transport probe nor a future passing fixed CI establishes its precise historical cause.

## Independently executed checks

| Check | Result | Evidence / limit |
| --- | --- | --- |
| Exact source and bounded edit surface | PASS | HEAD is full SHA above; worker-only source change inspected. Receiver and map app sources are byte-unchanged from c484. No app/test/shared build edits by QA. |
| Actual transport/strict guard/receiver/model tests | PASS | `.venv/bin/python -m pytest -q tests/test_paper_worker_transport.py tests/test_paper_worker_resource_guard.py tests/test_import_review.py tests/test_paper_workbench_model.py`: **39 passed in 9.01s**. Includes actual TypeScript execution and installed worker byte/hash checks, plus negative integrity/privacy cases. |
| Independent native timeout/recovery boundary probe | PASS, HTTP-only | In the actual shipped Paper HTML with all external resources denied, a constructor Proxy constructs the genuine exact-byte worker then suppresses its first communication. Advancing the actual page clock beyond45s produces the expected operation-timeout alert and safe `timeout` diagnostic; failed worker closes. Selecting the valid synthetic source again through real UI renders a nonzero canvas and extracts the expected DOI. Strict module/name/URL/byte/SHA resource assertions pass. Browser/context and temporary fixture directory closed. No fake success/fallback worker or file-policy bypass. |
| Local evidence file integrity | PASS | All **12** `local-files.json` entries independently read, byte-count/hash checked; all **11** command receipt log hashes verified. |
| Actual local HTML/manifests | PASS | Independently hashed both actual release HTML files and checked full source/bytes/hashes against candidate manifests; identities below. |
| Required fresh CI actual-file/full transfer/artifact | **FAIL before file gates / downstream SKIPPED** | Run39278014757, immutable `f94c3d1ddd9cdd3c2dca006d8e6f0f4b4e54be17`: hosted metadata assertion fails; both actual-file builds/smokes and artifact upload skipped. Four raw files independently verified against inventory and immutable Git objects. |

Development-provided raw local evidence, independently read/hash-checked but not rerun wholesale by QA: **341 Python PASS / 1 Windows-only DPAPI SKIP**, TypeScript/hosted build/browser, both portable builds, main resource-blocked HTTP and complete paper HTTP smoke, and all four payload gates PASS. Paper HTTP logs include genuine exact-byte worker, rendered PDF/text, opaque ready-only, native error/messageerror close/reselect, source pairing/sketcher/private storage and real checked-facts UI export → main saved same-ID empty/partial/facts-only/empty-composition/prefix profiles, reload/no-op/conflicts/backup/readback/quota/stale/concurrent preservation. Local logs explicitly say file:// NOT VERIFIED.

## Chemistry, privacy and scope preservation

QA-PW-01's explicit existing-fact review/Apply, safe missing fields, ordered prefix linkage, protected known-value/role/context conflicts, canonical chemical/DOI/evidence mapping, exact private raw-byte backup and no-op transaction remain intact. Focused actual receiver/model tests pass on this new SHA. Hosted/main broad tests also retain held-real-D3-guard Enter/Space/repeat/blur, mobile dragged-target Focus, recorded-edge Map and List fallback. Source-assisted manual structure entry/sketcher and actual RDKit graph/stereo inspection remain separate from human source comparison. Strict compact nested allowlists exclude source document/text/image/inspection-private caches; private source hash pairing stays outside main facts.

Automatic exact chemical drawing OCR is not implemented or claimed. No scientific-completeness review of the user's real papers was performed. Journal download/scheduling, external AI APIs, user-PC/default-browser installation, Box sync and perpetual agents remain outside this round. No new deployment, main merge, visibility/permission/history changes or cleanup claim. Historical quotations/crops/remote-storage Public boundaries remain separate. Managed local file:// restrictions were not bypassed or replaced with an alternate browser.

## Candidate identities and interim boundary

Both local manifests target **`bc39eda53b22a5b333e9fd7d432005653beab546`**:

- Main `Chembrain.html`: **5111218 bytes**, SHA-256 **`26d1f83ba3887b768a5a8600ad25935c2e37d34db9b34e1eccf1384f1cf8c724`**; library `7172a3f6970790c5795f074a8861555456eef330648a6591289ded34165df825`.
- Paper `Chembrain-Paper-Workbench.html`: **10165047 bytes**, SHA-256 **`b0b775cd659265fc35bd7ed7a3bd40debf8dcfe53262266a4a683d47365242db`**; `worker_transport=native-module-data-url` and unchanged worker hash above.
- RDKit2026.9.1/WASM, PDF.js6.4.299 and OpenChemLib9.25.1 pins/notices unchanged. Main HTML happens byte-identical to c484, but new same-source manifests/checks/reviews are still mandatory.

Required terminal evidence must prove both actual-file programs, first real PDF parse/render/text/native worker, native failure cleanup/reselect and complete checked JSON transfer/failure profiles; manifests must agree with actual delivered bytes and artifact upload must be confirmed. Main success alone cannot close QA-PW-02. Clean user PC/default browser NOT RUN. Artifact ZIP was not independently downloaded/rehash-verified by this role. No delivery approval at the interim cutoff; a terminal immutable-receipt supplement will determine the final decision.


## Terminal CI supplement and independent deterministic race diagnosis

Fresh run **39278014757**, immutable terminal receipt **`f94c3d1ddd9cdd3c2dca006d8e6f0f4b4e54be17`**, identifies the same exact source **`bc39eda53b22a5b333e9fd7d432005653beab546`** and expected library digest. I independently read all **four** raw receipt files, checked lengths/SHA against `web/receipt-files.json`, and compared every byte with its immutable `git show <receipt>:<filename>` object. No moving-ref fetch or source changes.

- Python **341 PASS / 1 Windows DPAPI SKIP** and TypeScript/hosted build PASS.
- Hosted browser **FAIL** at `scripts/web_smoke.py:152`, inside `check_metadata_boundary`: the already-captured `projected['papers']` still contains legacy fields when compared with the strict id/doi/authors key set.
- Main portable and Paper Workbench steps, including both actual-file smokes and the full actual-file PDF/worker/curation/transfer/failure profiles, are **SKIPPED / NOT RUN**. Artifact upload and publish also SKIPPED; page URL null. There are no new CI portable/paper manifests or uploaded artifact from this run.
- This failure precedes Paper execution. It is **not evidence of a new data-worker error**, and does not resolve QA-PW-02. Main byte identity with a previously passing build does not transfer source approval or waive current gates.

### QA-PW-03 — required metadata smoke captures primary bytes before migration completes

**Severity: P2 / medium, test/gate defect.** File: `scripts/web_smoke.py:139`–`scripts/web_smoke.py:152`; relevant app lifecycle `src/MolecularLibrary.tsx:43`–`src/MolecularLibrary.tsx:60` and completed rendering at line167.

`check_metadata_boundary` captures `actual` and `backups` immediately after `page.goto(..., wait_until='networkidle')`. Its later status wait does not establish that the earlier captured bytes represent completed migration: the app posts the exact-backup status **before** awaiting the remote library fetch and before compact primary persistence. Network idleness is not React/lifecycle completion. The fixture can assert the correct strict key set against the original legacy snapshot and report an application defect while the unchanged application subsequently persists the correct projection.

I independently proved this on an isolated **current-source** hosted build under `/tmp/chembrain-qa-bc39-hosted`, using a temporary HTTP server and normal managed Chromium. Only a test init script delayed initiation of the library fetch by4s; application/source/test files were unchanged.

1. Seed exact formatted synthetic legacy bytes with supported extra citation fields.
2. Delay actual `fetch(...library.json)` initiation through its normal promise boundary; navigate with `networkidle` exactly as the fixture does.
3. Capture primary/backups. Actual primary is still exact original legacy bytes; the private backup is exact original bytes. The later visible status already says “backed up privately”. Strict paper-key assertion on that captured value fails deterministically.
4. Wait for `.molecular-grid` count1, which this source renders only after `loading` is false, then capture a **new** primary snapshot.
5. Fresh primary has exactly id/doi/authors paper fields; chemicals/reactions/solutions remain equal to the original chemistry, and the exact private backup remains. The previously captured string still has old fields, proving the stale-snapshot error. No page errors. Browser/context/server closed.

Expected fixture behavior: await an explicit completed-load/migration UI condition before capturing primary and backup bytes, then keep all existing strict projection, exact-backup, chemistry-preservation, failure/recovery and reload/export assertions. The always-present-after-loading grid (including empty/error cases) is a concrete candidate completion boundary in this implementation; use it before the snapshot across all fixture branches. A wait after capturing cannot refresh the stored Python string. Add a meaningful delayed-fetch regression so the required gate cannot return a false rejection from this timing window. Do not loosen the allowlist, skip migration assertions, replace product checks with sleeps/retries or change unchanged application behavior merely to satisfy this fixture.

The exact historical CI event ordering was not logged. The receipt proves its failure location, while the independent delayed-fetch probe proves a concrete reachable defect matching it. This review does not invent an event trace for the runner or claim every such assertion could only have this cause. The successful completion snapshot in the controlled reproduction establishes that this demonstrated defect is in test synchronization, not a confirmed compact-projection/data-loss regression.

### Final disposition

**CHANGES_REQUESTED.** Confirmed new required-test finding **QA-PW-03/P2** remains open. QA-PW-01 remains resolved. Prior **QA-PW-02/P1 actual-file acceptance remains unresolved/NOT VERIFIED** for the new transport, with no actual-file worker failure observed on this source because that step did not run. Source-level review, 39 focused tests, genuine-native timeout/reselect and all local integrity checks pass, but required fresh actual-file/full-transfer/artifact evidence is absent.

Separate Revision must assess this report, then Wiki preserves the full originals/receipt and returns a bounded metadata-fixture synchronization repair through Planning. After a new frozen SHA, rerun required checks through both actual-file programs, first PDF native-worker/render/text, full transfer/failure profiles and artifact upload, followed by fresh QA/Revision. Do not retry unchanged CI as the fix or inherit earlier artifact/source approval. No approved deliverable or new download from this round; artifact ZIP has not been independently downloaded/rehashed.
