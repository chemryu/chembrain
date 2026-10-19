# Revision — Paper Workbench round-03

- Separate Revision role. Reviewed exact frozen source **`bc39eda53b22a5b333e9fd7d432005653beab546`**, independently verified as HEAD. Prior c484/8cbd rejections and reports remain preserved; no approval transfers.
- **Decision: CHANGES_REQUESTED. QA-PW-03/P2 is confirmed as a required-test synchronization defect. QA-PW-01 remains resolved. QA-PW-02/P1 actual-file acceptance remains NOT VERIFIED**, because this CI fails before either actual-file program runs. This is not a demonstrated recurring native-worker error on the new source.
- Read formal round-03 Planning, Development and both helper reports, final QA including terminal/race supplement, CI outcome, all four raw terminal files, startup-snapshot diagnosis/probe, and relevant startup/fixture/native-worker/strict-guard implementation. Role/repository/current-request instructions and prior complete Revision remain applicable.
- This role wrote only this report. No source/tests/build inputs/shared outputs or earlier reports changed; no commit, server, browser-policy workaround, alternate browser or deployment. No broad unchanged suite was rerun.

## Independent evidence verification

Run **39278014757**, https://github.com/chemryu/chembrain/actions/runs/39278014757, has immutable terminal receipt **`f94c3d1ddd9cdd3c2dca006d8e6f0f4b4e54be17`**. I independently verified all **four** `web/receipt-files.json` entries against byte lengths/SHA-256 and compared every byte with the named immutable Git objects. Terminal status, failure traceback and source provenance agree. The full source and library digest `7172a3f6970790c5795f074a8861555456eef330648a6591289ded34165df825` match the candidate. No current CI portable manifests exist because those steps were skipped.

I independently hashed both actual local release HTML files against the round-03 candidate manifests and checked their source fields:

| Local candidate | Bytes | SHA-256 |
| --- | --- | --- |
| `Chembrain.html` | 5111218 | `26d1f83ba3887b768a5a8600ad25935c2e37d34db9b34e1eccf1384f1cf8c724` |
| `Chembrain-Paper-Workbench.html` | 10165047 | `b0b775cd659265fc35bd7ed7a3bd40debf8dcfe53262266a4a683d47365242db` |

Both identify source bc39 above. Main byte identity with the preceding source does not transfer approval or waive the new exact-source gates. The protected source diff against HEAD was empty for application/scripts/tests/packaging/workflow/package inputs. These are independent read-only integrity/code checks; browser reproduction and test executions below are explicitly attributed, not represented as rerun by Revision. No ZIP was independently downloaded or rehashed.

## QA-PW-03 — confirmed P2 fixture startup snapshot race

The actual CI traceback fails at `scripts/web_smoke.py:152`, the strict id/doi/authors key assertion in `check_metadata_boundary`. Source inspection confirms the fixture captures `actual` and `backups` immediately after `goto(..., wait_until='networkidle')`, before its later notice/alert assertion. That Python string is immutable and does not refresh after a later UI wait.

The application's ordering in `src/MolecularLibrary.tsx` is decisive: legacy input is validated/projected, exact raw bytes are privately backed up, and the “backed up privately” notice is posted **before** `await fetch(base+'library.json')`. Compact primary persistence occurs only after remote fetch/validation/merge; `setLoading(false)` runs in `finally`. The `.molecular-grid` container is rendered only when loading is false, including empty or failure/recovery states. Thus neither network idleness nor the early backup notice establishes completed primary migration, and grid completion before capture is a concrete synchronization boundary for this source.

The preserved finite `startup-snapshot-diagnosis/probe.json` reports the reachable early state: original legacy primary plus exact backup, with completed-grid count0 even while the backup notice is visible; after grid completion, fresh primary has normalized paper fields, all chemistry and exact backup preserved, and zero page errors. Final QA separately reproduced that transition using an isolated current-source hosted build and a delayed initiation of the normal library fetch. Root's independent controlled probe agrees. I checked that this behavior follows the actual code ordering; it does not require a migration logic or allowlist change.

**Finding upheld:** the mandatory fixture can falsely reject correct completed projection by asserting against a prematurely captured primary snapshot. Its blocking of the required gate warrants P2. The exact historical runner scheduling is unavailable; the receipt proves the assertion location and the controlled probes prove a reachable matching defect, not a reconstructed historical trace or a claim that all possible failures at this assertion have one cause. No compact-projection data-loss regression is established by this evidence.

The bounded repair is to await `.molecular-grid` count1 **before reading either primary or backup storage**, across all success/failure/unknown branches, then keep the existing assertions on fresh bytes. A later wait after capture cannot fix the stale string. Retain reload/persistence/export checks and consider the same completed-load boundary before any post-reload snapshot that depends on startup completion. Do not loosen strict public fields, remove exact-byte/failure assertions, modify unchanged application behavior, add arbitrary sleeps or retry an unchanged CI as the repair.

## Native worker repair and prior findings

**QA-PW-01 remains resolved.** The receiving implementation and map app sources are unchanged from the previously inspected repair, and final QA's focused actual-helper/model tests and full local transfer evidence preserve explicit missing-fact review/Apply, canonical identity/evidence mapping, protected conflicts, linked ordered stages, exact private backups and zero-write no-op behavior. No additional receiving finding was identified by this role.

The worker candidate follows the formal bounded plan. `paperWorkerTransport.ts` directly base64-encodes original bytes with a chunk size divisible by three; `paperPdf.ts` constructs a genuine native module Worker with the stable private name and passes its port to PDF.js. Worker source/dependency bytes are unchanged. The original worker SHA remains **`9536359f1b8367850d485731ca1d5e45c159a7b7a0912325e539937aa21ceb18`**; paper manifest declares `native-module-data-url`. Existing disabled external/fake-worker import paths remain; no alternate transport retry, CDN or main-thread fallback was added.

I reviewed failure/operation timeout and destruction ordering: bounded races cover loading/metadata/text/render, pending native failure is observed, teardown removes listeners and bounds PDF.js shutdown before unconditional native termination/releasing owners. Diagnostic objects contain fixed enums/finite locations rather than arbitrary messages, filenames, worker URLs or source contents; default native error reporting is prevented and event count is capped. `scripts/paper_worker_smoke.py` requires canonical exact JavaScript/base64 representation, strict decoded byte equality and pinned/manifest SHA, expected module/name and genuine worker events. Negative integrity cases and finite URL/terminal diagnostics are meaningful; no broad arbitrary data-worker allowance is used. No new material worker-adapter finding was identified.

Final QA independently ran **39 focused tests** and a genuine-native-worker timeout/recovery probe through the actual Paper HTML under resource-denied HTTP: the real timeout/error cleanup is followed by valid synthetic PDF reselect, rendering and expected text with strict worker byte/name/module verification. Development's complete local HTTP PDF/curation/export-to-main smoke also passes. These support the candidate and are attributed execution evidence. The opaque-origin probe remains correctly **ready-only**. Neither HTTP evidence nor source review proves actual-file support, and no exact historical Chromium151 native error cause is established.

**QA-PW-02 actual-file acceptance therefore stays unresolved/NOT VERIFIED for bc39.** This round did not reach Paper execution; do not label it a recurrence of the old worker failure, mark it resolved, or infer success from the unchanged main HTML.

## Required gate accounting

| Gate for bc39 | Result | Evidence / practical limit |
| --- | --- | --- |
| Python full suite | PASS341 / SKIP1 | Immutable CI log; Windows-only DPAPI skip remains distinct. |
| TypeScript/hosted build | PASS | Immutable CI build log. |
| Hosted browser | **FAIL** | Required metadata assertion, QA-PW-03; subsequent map/receiving profiles in this CI do not execute. |
| Local worker/receiver/model regressions | PASS, attributed | QA39 focused checks and native HTTP timeout/reselect; Development all11 local commands plus complete HTTP browser profiles. |
| Main portable build/actual-file | **SKIPPED / NOT RUN** | Current terminal receipt. Prior main success is historical. |
| Paper portable build/actual-file native PDF/worker/full transfer and failure profiles | **SKIPPED / NOT RUN** | CI stops before these steps. Local builds/HTTP checks are supplemental. |
| Artifact upload/download availability | **SKIPPED** | No new artifact URL or approved ZIP; no independent ZIP hash. |
| Pages | **SKIPPED / NOT ATTEMPTED** | Publish skipped, page URL null; no new403 observation. |
| Clean user PC/default browser | **NOT RUN** | Not established by current local or CI evidence. |

Final QA and Revision agree that closure criteria are unmet: one new confirmed P2 test finding and the prior mandatory actual-file acceptance requirement remain open. No approved deliverable or new download exists.

## Bounded Wiki → Planning handoff

1. Wiki preserves complete round-03 QA/Revision, raw immutable receipt, startup diagnosis and all prior reports, then returns through formal Planning before Development edits source/tests. Keep bc39 evidence separate from the next source.
2. Repair only the required metadata fixture synchronization: after initial navigation, await actual completed-load `.molecular-grid` count1 before taking primary **and backup** snapshots in every success/backup-failure/primary-failure/unknown-field branch. Take fresh values after the boundary; retain exact original bytes, strict paper allowlist, all chemistry, recovery-blocked controls, unsupported nested/container imports, no-mutation checks, export and reload persistence assertions. No application change is justified by this demonstrated fixture defect.
3. Add a deterministic controlled delayed-fetch-start regression. On unchanged app behavior, prove an early stage with the exact legacy primary and exact backup while the notice is visible and grid absent; release the fetch through an explicit test-controlled boundary, wait for the completed grid, and prove fresh strict projection/all chemistry/exact backup. Prefer explicit synchronization over a wall-clock sleep. This must expose the old premature-snapshot behavior and pass the corrected fixture; no blind retry, allowlist relaxation or skipped assertion.
4. Preserve native exact-byte data-module transport, safe bounded diagnostics/cleanup, strict resource/integrity guard, all private PDF/source-check/manual sketcher/RDKit and receiving/keyboard regressions. Do not bypass managed local `file://` policy, select an alternate browser, claim HTTP as file proof, enable network/CDN/fake workers or expose private document/worker payloads in diagnostics.
5. Freeze/push a new full source SHA for the test repair and run required checks through completion: Python, TypeScript/build, full hosted browser, both portable builds/payload checks, both actual-file programs, first Paper native-worker PDF parse/render/text, cleanup/reselect, explicit checked-facts UI export → saved same-ID main review/Apply/reload, conflicts/no-op/raw backup/quota/stale/concurrent profiles and artifact outcome. Preserve complete immutable terminal logs/inventory and same-source manifests; verify actual delivered HTML bytes, engine/worker/library identities. State ZIP verification only if actually performed. No unchanged CI retry is a repair.
6. Obtain fresh separate QA and Revision for that exact source and terminal evidence, then Wiki records closure only with zero unresolved findings and all mandatory gates PASS. Source/artifact approval cannot be inherited from bc39/c484. Actual-file failure, if any, must use its new bounded diagnostic evidence and return through the same role loop.

Scientific scope remains source-assisted manual curation and human source comparison, not automatic exact structure OCR or scientific completeness validation. Journal downloading/scheduling is later. No external AI API, Box sync/perpetual agent activation, main merge, release, Pages/configuration publication, permission/visibility change, shared-history rewrite or historical Public clearance is part of this repair.

**Final: CHANGES_REQUESTED — QA-PW-03/P2 confirmed; QA-PW-01 resolved; QA-PW-02 actual-file resolution NOT VERIFIED; mandatory downstream gates and artifact upload SKIPPED.**
