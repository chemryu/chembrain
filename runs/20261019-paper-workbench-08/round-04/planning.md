# Planning — Paper Workbench round-04 fixture completion boundary

- Separate Planning role; output only this plan. No application/tests/build edits or final approval by Planning.
- Rejected frozen baseline: **`bc39eda53b22a5b333e9fd7d432005653beab546`** on `codex/gpt-agent-workflow`. New repair source SHA: **not frozen**. Application behavior must remain unchanged; a test-only repair still requires a new full source SHA and fresh exact-source gates/reviews.
- Read AGENTS/RULEBOOK/Planning role/current request, current wiki/progress, final round-03 QA and complete Revision, CI outcome, controlled startup probe, local eleven-check receipt, actual fixture/app lifecycle and, after they existed, complete round-03 `handoff.md` and `wiki-record.md`. This is the formal Wiki→Planning handoff before Development edits.

## Findings and evidence boundary

**QA-PW-03/P2 is confirmed:** `scripts/web_smoke.py::check_metadata_boundary` reads primary and backup storage immediately after networkidle. The unchanged application creates an exact private legacy backup and notice before awaiting its library fetch; primary normalization follows that fetch. The fixture's later notice wait cannot refresh its earlier Python string. `.molecular-grid` count1 is a concrete completed-load boundary because it is rendered after loading=false in success and caught failure/recovery branches. Controlled root/QA probes show legacy primary/exact backup/grid0 before completion and fresh strict paper projection/all chemistry/exact backup after completion. This establishes a reachable fixture defect; exact historical runner scheduling remains unknown, and no application projection/data-loss defect is established.

CI39278014757, immutable receipt **`f94c3d1ddd9cdd3c2dca006d8e6f0f4b4e54be17`**, records Python341 PASS/1 Windows DPAPI SKIP and build PASS, then hosted metadata assertion FAIL. Later hosted map/receiving, both portable/actual-file programs and complete transfer were NOT RUN; artifact/publish SKIPPED. No new CI portable manifests/download/Pages attempt or403 exists.

**QA-PW-01 remains resolved. QA-PW-02 actual-file acceptance remains NOT VERIFIED.** The exact-byte native data-module worker has passing source/local HTTP PDF and failure/reselect evidence, but this CI never reached Paper. Do not describe the old worker error as recurring or resolved. HTTP opaque-worker readiness remains ready-only. Prior application/artifact approval does not transfer, even if resulting HTML bytes match a preceding build.

## Bounded Development tasks

1. **Repair only fixture synchronization in `scripts/web_smoke.py`.** Factor a small shared completed-load wait if helpful: await `.molecular-grid` count1 with Playwright's bounded assertion before taking either primary or backup snapshots. Use it after initial navigation in every existing profile: success, backup failure, primary failure and unknown legacy field. Read fresh storage only after the boundary. Apply the same boundary after reload before asserting persisted primary bytes; include fresh backup verification there where relevant. Keep alerts/notices as outcome assertions, not readiness substitutes. Do not change app migration, loading order, public allowlist, storage transaction or UI to satisfy this test.
2. **Add a deterministic held-fetch regression against the real unchanged application.** Extend the successful metadata fixture with a controlled delayed-start variation while retaining all four existing profiles. An init-script wrapper holds the promise before the normal `/library.json` request starts, only while primary storage equals the exact synthetic legacy raw bytes; normalized reloads pass directly through. After release it calls genuine fetch and returns the actual response. Blocking an already-started response could make networkidle wait and hide this race. Bound the gate, handle every relevant startup attempt and avoid pending work at teardown.
3. **Prove a negative control before invoking the repaired path.** After goto(networkidle), with fetch still held, assert the hold has been reached, the backup notice is visible, `.molecular-grid` count0, primary equals the exact formatted synthetic legacy bytes and the private backup equals those bytes. Assert that this early primary still has the known legacy citation fields and therefore does not satisfy strict id/doi/authors projection. Retain that early snapshot and later show it remains legacy while a newly read snapshot is normalized. This demonstrates precisely what the old fixture captured, without intentionally failing the suite or loosening its assertions.
4. **Make the positive regression sensitive to removal of the readiness wait.** From the held state, arm a short browser-controlled release timer (for example `setTimeout(release, 1000)`) and immediately execute the same shared completion-wait→fresh-snapshot path used by the ordinary profiles. This timer is solely synthetic delayed-fetch input: the test must never sleep for it or infer readiness from elapsed time. Readiness is always grid count1. Releasing and then waiting for completion in some separate setup path would mask a missing wait in the function under test; preserve this negative/positive distinction. Verify fresh strict paper projection, every chemistry table, exact backup, persistence/export and unsupported-import behavior through the normal successful branch. On reload, ensure the test gate cannot deadlock and again wait on actual completed loading.
5. **Keep the assertions and test ownership narrow.** Preserve exact original whitespace/bytes, strict normalized paper keys, chemistry edits/notes/concentration, backup failure/no-backup and recovery-blocked controls, primary failure retaining raw primary plus exact backup, unknown-field failure, unsupported legacy/nested/container imports rejecting without mutation, backup JSON contents and reload persistence. No arbitrary sleeps, retries, shortened validation or exception swallowing. Add finite synthetic outcome diagnostics only if useful; no private paths, raw document contents or giant worker URLs. Prefer this actual-browser regression over a mirrored unit model of React timing.

Expected executable edit surface is the metadata fixture and a narrow helper/regression if justified. Application `src/`, dependency pins/lockfile, packaging and worker adapter/guard behavior remain byte-unchanged from bc39. Preserve all existing tests and checks. If a different app defect is discovered, record it and return through the review loop instead of expanding this authorized repair silently.

## Acceptance and preserved contracts

The new delayed-fetch case must deterministically observe the old early state, then pass strict completed-state assertions using the shared wait before any success-dependent storage capture. Removing/bypassing that shared wait must expose the premature-snapshot defect under the held-release profile; demonstrate this with a temporary isolated test mutation or equivalent controlled execution, restore it, and record both outcomes without committing the broken variation. A test-only release timer is allowed as controlled scheduling input; a fixed delay used instead of readiness is not.

All four original profiles and post-reload persistence remain meaningful. The application source must compare byte-unchanged to bc39. QA-PW-01's canonical ID/DOI/evidence remapping, field-level missing-fact review/Apply, ordered linked stages, known-value conflicts, exact private raw backup/readback, stale/concurrent protection and repeated no-op remain covered. Keep held-real-drag-guard keyboard/map, mobile Focus and List regressions.

Preserve pinned native module/data-URL PDF worker bytes/hash, strict URL decode/byte/hash resource allowlist, finite redacted diagnostics, cancellation/timeouts/unconditional worker cleanup and failure/reselect. PDF/text/images remain private memory-only; compact facts never include them. Keep source pairing/recheck, explicit source comparison, manual sketcher transfer, actual RDKit stereo/graph checks and recorded route/solution edges. No automatic exact structure OCR or scientific-completeness claim.

## Required checks and exact-source evidence

Rerun **all eleven local checks** for the new frozen source, recording commands, exit status, counts, full bounded logs and SHA inventory. Use the same supported setup and subpath build environment (`CHEMBRAIN_BASE=/chembrain/`) as round-03:

| Check | Required command/workflow |
| --- | --- |
| Full Python | `.venv/bin/python -m pytest -q`; actual counts, Windows-only DPAPI skip separate |
| Hosted TypeScript/build | `npm run build:web` |
| Full hosted browser | `.venv/bin/python scripts/web_smoke.py`; held-fetch regression plus all subsequent structure/receiver/map profiles |
| Hosted payload | `.venv/bin/python scripts/check_repository_payloads.py --dist dist` |
| Main portable build | `npm run build:portable` |
| Main local HTTP | `.venv/bin/python scripts/portable_smoke.py --http-only` |
| Main portable payload | `.venv/bin/python scripts/check_repository_payloads.py --dist dist-portable` |
| Paper portable build | `npm run build:paper` |
| Paper local HTTP | `.venv/bin/python scripts/paper_workbench_smoke.py --http-only` |
| Paper payload | `.venv/bin/python scripts/check_repository_payloads.py --dist dist-paper` |
| Tracked payload | `.venv/bin/python scripts/check_repository_payloads.py` |

Local HTTP is supplemental. Managed Chromium file policy remains respected: no policy modification, security/file-access flags or alternate browser to evade it. Mark local actual-file NOT RUN rather than using HTTP as file proof. Stop/close temporary servers/browsers started for verification.

Freeze/push a **new full source SHA** and obtain fresh terminal CI through all required gates: full Python/build/hosted browser including the deterministic regression; both portable builds/payload gates; **both actual file:// programs**; first synthetic PDF native-worker parse/rendered pixels/text, native failure/timeout cleanup and valid reselect; explicit source-checked UI export/download→saved same-ID main review/Apply/reload. Preserve empty/partial/facts-only/empty-composition/prefix transfer plus known conflicts/no-op/exact raw backup/readback/quota/stale/concurrent profiles. Do not waive these because only tests changed.

Preserve immutable terminal raw receipts and byte/SHA inventories. Check both local/CI manifests against the new full source, actual HTML lengths/SHA-256, library digest, native-module-data-url transport, original worker digest `9536359f1b8367850d485731ca1d5e45c159a7b7a0912325e539937aa21ceb18`, RDKit2026.9.1/WASM, PDF.js6.4.299 and OpenChemLib9.25.1. Preserve underlying command exit codes; PASS/FAIL/SKIP/NOT RUN/PENDING remain distinct. Confirm upload before claiming an artifact download exists; independent ZIP download/rehash is claimed only if performed. Pages is separate and not attempted as this fixture repair.

## Role loop and limits

After Development, obtain fresh **separate Independent QA and Revision** for the exact frozen SHA and terminal evidence. They must resolve QA-PW-03, assess QA-PW-02 only from executed actual-file results, confirm QA-PW-01 protections and unchanged application, and inspect the delayed-fetch negative/positive regression. They do not edit application code. Wiki then preserves complete reports/evidence and either closes with zero unresolved findings/all mandatory gates PASS or returns concrete unresolved work to Planning. Any executable edit after review begins requires a new SHA and appropriate checks/reviews. No inherited approval or unchanged CI retry substitutes for this repair.

Root publishes records separately from source. After this plan read Wiki's pending-publication handoff, root confirmed round-03 push acknowledgement at **`472f30465b1998ee1268f198e1eb890cb82a584f`**, with source bc39 unchanged; preceding round-02 records parent is `28798f6f04d29a0abca22e06e1e45775a6ab2fec`. Preserve earlier reports and distinguish this confirmed records publication from source/artifact approval.

No journal downloading/scheduling, external AI API, Box sync/perpetual agents, user-PC installation, main merge, release, Pages/deployment/configuration, permissions/visibility change, history rewrite or Public clearance belongs to this bounded work. Historical quotations/crops and unverified remote storage remain separate boundaries. This plan authorizes the fixture repair and verification, not delivery approval.
