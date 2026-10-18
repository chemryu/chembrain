# Independent QA — synthesis map round-02

- Role: separate Independent QA; no application source edits.
- Exact inspected/executed source: **`02d0dff2ce66a00f10e0c873baea80fa6f94e963`**.
- Run: `20261018-synthesis-map-06 / round-02`.
- Prior round-01 report is retained unchanged, including the exact CI failure supplement.
- Initial status: **QA-SYN-01 RESOLVED; no new material source findings found. Required fresh CI / actual-file artifact evidence PENDING, so final delivery approval is not yet granted.** A final evidence supplement will be appended rather than replace this chronology.

## QA-SYN-01 independently resolved

`focusSelected` now reads the live ReactFlow node with `instance.getNode(graph.selectedNodeId)` and its measured width/height, instead of stale projected `graph.nodes` coordinates. This preserves exploratory drag placement and desktop live-node Fit behavior. Missing initial measurements have explicit size fallbacks.

Independently rebuilt the exact source with `CHEMBRAIN_BASE=/chembrain/ npm run build:web` and reran the **same independent reproduction** `/tmp/qa_synthesis_mobile_focus.py`, not merely a source-string assertion:

1. Real Chromium 390 × 844; choose Paclitaxel, Focus.
2. Drag the selected molecule's header 200 screen pixels right, asserting placement changed.
3. Focus again and measure the actual current card/canvas boxes.

**PASS**: live card `x=144.75,width=168,y=355.78125,height=133.04296875` lies within canvas `x=40,width=310,y=182.15625,height=480`. The old rejected source left that same card at `x=438.375` wholly off-canvas. The fix changes viewport focus, not chemistry or saved layout.

The shared hosted/portable browser suite additionally tests a dragged selected doxycycline card at mobile width and awaits actual complete card containment in the canvas. This covers a separate target and retains the no-storage-write assertion.

## Diagnostics review

`bounded_log` now preserves all short logs as bytes instead of retaining only 120 lines. Oversized UTF-8 logs retain bounded beginning/end context plus an explicit omission marker. The actual temporary-Git receipt regression verifies a 600-line short DOM diagnostic survives complete and byte-identical across build and later terminal jobs; the large Unicode regression checks size, diagnostic beginning/end and valid retained UTF-8.

These changes repair evidence retention. They **do not prove the cause** of round-01 CI39140468551's hosted-browser failure; that old failure remains cause-unresolved because its traceback head was absent. Fresh actual CI must pass, or its now-retained assertion must be diagnosed. The P2 fix is not claimed as the historical CI failure cause.

## Independent checks executed so far

| Check | Result | Scope |
| --- | --- | --- |
| Focused runtime/contract/payload/receipt tests | **17 PASS** | `tests/test_synthesis_graph.py tests/test_web_library_data.py tests/test_portable_contract.py tests/test_repository_payloads.py tests/test_web_provenance.py` |
| Hosted TypeScript and production build | **PASS** | exact source at `/chembrain/` |
| Original independent mobile Paclitaxel drag/Focus repro | **PASS** | actual measured containment described above |
| Tracked source payload gate | **PASS: 157 files** | no source document payload |
| Hosted dist payload gate | **PASS: 13 files** | actual distribution |
| Full hosted browser suite | **RUNNING at initial report** | result will be appended |
| Portable offline HTTP-only suite | **PENDING at initial report** | Root currently rebuilding; do not confuse with actual file execution |
| Local managed-browser actual `file://` execution | **NOT RUN** | administrative policy blocks file URLs; no bypass |
| Fresh exact-source CI hosted + actual-file artifact | **PENDING** | Root owns immutable receipt capture; required for final delivery |

Root's broad development checks are separate evidence and are not labelled independently rerun here. Full source changes are limited to the live-position focus correction, shared browser regression, diagnostic retention/tests and planning/request records. Recorded chemistry graph behavior from round-01 is preserved: genuine edges only, no inferred missing transformations, separated fragments, cycles/namespaces/caps, whole-participant omission and List fallback. No new scientific data, network API, dependency, PDF, permission or history change was introduced.

## External constraints retained

No source/artifact approval is inherited from e6ed4e7 or aaf4d8b. Existing history quotation/crop blobs, unverified remote Actions storage, inactive collection, browser profile/file-location storage and no Box sync remain unchanged. Hosted Pages observations must be reported from the fresh run if actually attempted, with earlier403 labelled historical otherwise. No Public clearance, main merge or production release is implied.

## Independent local completion supplement

The exact-source **full hosted browser suite PASS** completed, including the new real mobile selected-card containment regression and every retained map/editor/import/backup/storage/security case. Local actual-file remains NOT RUN under the managed browser policy.

The inspected stable portable manifest identifies **722585 bytes**, HTML SHA-256 **`a1a175882c6701e2d3f98b61b80dbed27d643e0de1eb661823c930b36384278d`**, source `02d0dff2ce66a00f10e0c873baea80fa6f94e963`, unchanged normalized-library SHA-256 `7853ba5d2b335c274733b8c726ac7b80c899e9d51bfd42295279ea75df2452bb`. Independent HTTP-only portable execution is in progress; this identity is not a download/file-execution approval. New exact CI39141206671 is pending, separate from historical failed run39140468551. Root reports development full-suite290PASS/1SKIP; this is not the independent17-test subset.

Independent `.venv/bin/python scripts/portable_smoke.py --http-only` now completed **PASS** on those exact stable bytes and source. It exercised the mobile selected-card drag/Focus geometry and all prior offline/embedded-asset/no-network/editor/storage-failure/backup/import/hostile-embedding checks with all additional requests rejected. It remains explicitly **HTTP-only, actual `file://` NOT VERIFIED locally**. Await fresh CI actual hosted/file-browser PASS and artifact identity before a final download verdict.

## Final exact-source CI and artifact supplement — bounded download preview PASS

Fresh actual [CI39141206671](https://github.com/chemryu/chembrain/actions/runs/39141206671), immutable terminal receipt **`8c8d3c6317433502ffd4984df39fd6b4290ef52e`**, is now captured. Independent QA matched **all nine raw evidence files** to their immutable Git objects and manifest byte counts/SHA-256. Both workflow and actual built source are exactly **`02d0dff2ce66a00f10e0c873baea80fa6f94e963`**.

- Actual CI Python suite: **290 PASS / Windows-only DPAPI 1 SKIP**; hosted TypeScript/production build and **actual hosted-browser suite PASS**.
- Portable build and **actual offline `file://` browser suite PASS**, explicitly recorded in `portable-browser.log`. This includes new Map/mobile dragging/Focus, all earlier editor/backup/import/storage failure/security cases, offline additional-request rejection and no app network assets. Local administrative file policy was not bypassed; this is the separate normal CI runner's genuine file execution.
- Portable artifact upload **SUCCESS**. Artifact ID **`12140894328`**, [download](https://github.com/chemryu/chembrain/actions/runs/39141206671/artifacts/12140894328), CI-reported archive digest **`d5ba0bad0030913a63c36824123dd4ae2561c5034556cab32e1daa23eb331ee2`**.
- Independently compared CI `browser-manifest.json` byte-for-byte with local release manifest, then independently hashed the local actual HTML and current library. Exact identity: HTML **722585 bytes**, SHA-256 **`a1a175882c6701e2d3f98b61b80dbed27d643e0de1eb661823c930b36384278d`**; source `02d0dff2ce66a00f10e0c873baea80fa6f94e963`; library SHA-256 `7853ba5d2b335c274733b8c726ac7b80c899e9d51bfd42295279ea75df2452bb`. CI actual-file log names this same source/HTML hash. **The uploaded artifact ZIP itself was not independently downloaded**; reported archive digest and matching validated HTML identity are stated distinctly.
- This fresh CI actually attempted Pages configuration and observed **403 `Resource not accessible by integration`**. Deployment/access were **SKIPPED / NOT RUN**, URL **null**. Journal collection was skipped. The download's build/validation success is distinct from Pages publishing failure.

**Final Independent QA verdict: PASS for the bounded downloadable browser preview, zero unresolved material source findings; QA-SYN-01 RESOLVED.** Current exact-source required hosted and actual-file validation gates pass. Round-01 e6ed4e7's historical CI failure cause remains **UNRESOLVED** because its original traceback was lost; this report does not invent a causal explanation or relabel that old run as passed. The current fresh required check is satisfied by observed current CI PASS, not by assuming the P2 fix caused the earlier failure.

No public hosted site, production release, repository Public clearance, old-history cleanup, external artifact/cache cleanup, schedule activation or Box sync is approved. Hand off the unchanged complete report to separate Revision and Wiki for final comparison and preservation.
