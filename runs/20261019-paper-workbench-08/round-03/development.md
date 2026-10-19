# Development — Paper Workbench round-03 native transport

Root Development/coordinator. Frozen/pushed source **`bc39eda53b22a5b333e9fd7d432005653beab546`** on `codex/gpt-agent-workflow`. The separate formal Planning followed full round-02 Revision→Wiki handoff; round-02 reports/raw receipt/controlled diagnosis were published separately in records commit **`28798f6f04d29a0abca22e06e1e45775a6ab2fec`**, preserving old reports and source HEAD. Prior c484 and8cbd remain rejected; no approval transfers. This report does not approve delivery.

## Bounded change

- Native PDF module transport now uses `data:text/javascript;base64,` with **exact original decompressed worker bytes**. No worker-source rewrite, dependency upgrade, external network/CDN, fake-worker/main-thread fallback, speculative transport retry or browser-policy change. Existing PDF.js custom native port and disabled network/fake-worker imports remain. The same static worker SHA is `9536359f1b8367850d485731ca1d5e45c159a7b7a0912325e539937aa21ceb18`; paper manifest explicitly declares `native-module-data-url`.
- Encoder preserves arbitrary UTF8/binary bytes across base64 chunks. The adapter releases encoded references after construction; destroy removes listeners, bounds PDF.js shutdown then unconditionally terminates the native worker and clears task/document/buffer owners. Native error/messageerror and bounded operation timeouts settle pending loading/metadata/text/render, retain actionable English failure and permit valid reselect. Existing size/page/encrypted limits, cancellation/page cleanup/private in-memory sources remain.
- Native failure diagnostics are fixed categories/finite numbers, whitelisted browser/protocol/version and opaque-origin/transport/stage; arbitrary messages, filenames/paths, PDF data and data/blob/file URLs never enter diagnostics. Count capped3 per read. Native default reporting is prevented to avoid giant data URLs.
- Test-only constructor observation retains genuine native Worker. Strict guard decodes canonical base64 and compares **every byte plus SHA** with installed hard-pinned dependency and manifest; validates module/name and genuine worker events/cleanup. No broad data allowance. Guard negative cases reject foreign/truncated/changed bytes, unrelated data/scripts/external/blob URLs, wrong MIME/manifest. Arbitrary request/console/page-error data are recorded by finite category/length/digest only. A finite terminal error boundary keeps exit1/code-frame identifiers without original Playwright Aria snapshots/private page text/giant URLs.
- Normal HTTP opaque-origin regression executes the actual pinned native data module and requires its real worker→main ready, then terminates/closes context. It is explicitly **ready-only**; full application PDF parsing/rendering/text and actual-file mode remain separate required gates.
- Existing same-ID chemistry receiver QA-PW-01 fix and held-D3-guard keyboard regressions preserved. No seed/library data or generic merge precedence changed.

Helper reports: `development-worker.md`, `development-worker-checks.md`. Ten source-commit paths include formal Planning, adapter/helper, strict smoke/guard/tests and transport manifest/notices. Current paper dependency bytes remain unmodified; license notice still identifies only the pre-existing main-thread external/fake-worker import removal.

## Exact-source local results

All **11** commands in `local/checks.json` exited0. Raw logs and SHA inventory `local-files.json`:

- Python **341 PASS / 1 Windows-only DPAPI SKIP**, expected existing Starlette/httpx warning. Seventeen new focused transport/integrity/finite-diagnostic tests run actual helper code, including installed worker byte/SHA equality.
- Hosted TypeScript/Vite build and full real browser receiver/map/structure/storage/mobile suite PASS.
- Main portable build/resource-denied offline mocked HTTP full suite PASS.
- Paper portable build + strict resource denied mocked HTTP full native worker/PDF/canvas/text/curation/export→main suite PASS. This includes actual unmodified static worker byte validation, opaque ready-only profile, native error/messageerror injection cleanup and valid PDF reselect/real parse/render/text, source pairing/storage/sketcher/stereo gates and all empty/partial/facts-only/empty-composition/prefix existing-ID receiving, preservation, no-op/conflicts/backup/readback/quota/stale/concurrent profiles.
- Payload gates: tracked198, hosted16, main portable16, paper3 PASS. No source documents/page images/prose or worker base64 were added to tracked source/reports.

The local browser is managed Chromium154; its administrator policy blocks file navigation. **Local actual file tests NOT RUN**, no override/alternative browser. Both portable local smokes remain explicitly HTTP-only and cannot satisfy actual-file delivery. The controlled opaque probe supports the selected transport but cannot conclusively attribute historical Chromium151's old opaque Blob failure; that exact old underlying event remains unavailable.

## Candidate identity and pending required CI

Both complete manifests are captured in `candidate-manifests.json`; root independently hashed actual local HTML bytes against them:

- Main `Chembrain.html` 5111218 bytes SHA256 `26d1f83ba3887b768a5a8600ad25935c2e37d34db9b34e1eccf1384f1cf8c724`.
- Paper `Chembrain-Paper-Workbench.html` 10165047 bytes SHA256 `b0b775cd659265fc35bd7ed7a3bd40debf8dcfe53262266a4a683d47365242db`.
- Same new full source `bc39eda53b22a5b333e9fd7d432005653beab546`; library `7172a3f6970790c5795f074a8861555456eef330648a6591289ded34165df825`. RDKit2026.9.1, PDF.js6.4.299, OpenChemLib9.25.1 unchanged; original worker `9536359f1b8367850d485731ca1d5e45c159a7b7a0912325e539937aa21ceb18`.

Fresh exact-source CI **39278014757**: https://github.com/chemryu/chembrain/actions/runs/39278014757 . At cutoff **PENDING**, observed tests phase. Actual-file both programs/full transfer, artifact and hosting not inferred from local success. Root will preserve immutable terminal raw files and add `ci-outcome.md`; separate QA/Revision must verify exact source/manifests/bytes and mandatory file gates before Wiki closure. No artifact ZIP independently downloaded/hashed. Main HTML happens byte-identical to c484 because the main program code is unchanged, but both manifests/reviews/gates must still identify this new SHA.

## Limits

Private source-assisted/manual curation, graph encoding and explicit human PDF comparison remain distinct from automatic exact OCSR or scientific validation (not implemented). Original PDFs/text/images are memory-only and excluded from compact facts/Git. No journal downloader/weekly activation, personal AI API/keys, user-PC install, Box sync or perpetual agents. No main merge, permission/visibility/history changes, production release or new Pages claim. Prior historical quotations/crops/Public constraints retained.
