# Revision — 20261017-web-03 / round-03

- Role: separate GPT Revision; read-only application, test, CI and source-history review. This report is the only repository file written by this role. No source change, permission change, model API, institutional login or schedule activation was performed.
- Reviewed frozen source: **`56be43bf15b4c98b8b515d2dc3bbd2bd0fcbbbae`**, parent `d423c718ca3c0b7d1dd090a362ba02990d7e223a`.
- Inputs: AGENTS/RULEBOOK/current request, complete round-02 QA → Revision → Wiki handoff, round-03 [Planning](planning.md), [Development](development.md), source diff and final [Independent QA](qa.md). This final judgment follows the actual final QA report, not a preliminary zero-finding message.
- **Source-review verdict: PASS; 0 unresolved code findings in this bounded round. WEB-REV-05 / WEB-QA-05 is RESOLVED.** The four preceding repaired contracts remain resolved; approval is assessed on this source rather than inherited from a parent.
- **Overall accessible-preview delivery: BLOCKED_EXTERNAL_PAGES_CONFIGURATION.** Exact-source build checks pass, but actual Pages configuration returns HTTP 403. Deployment/public HTTPS verification are NOT RUN; no verified URL or final deliverable is approved.

## Independent judgment on the durability repair

The implementation addresses every advancement path in the original finding. Standalone discovery buffers both intermediate page cursors and completed-window checkpoints across journals. The complete package validates and its atomic output replacement succeeds before any advancing metadata state is saved. Failed output therefore retains previous bibliography and progress; a state-write error after output is reported while the new bibliography remains available for safe replay. This resolves both the original completed-window loss and the 101-item capped-cursor variant, rather than changing only `last_success`.

The shared `prepare_anchors` helper and explicit `anchor` CLI add only nonadvancing original-window state before the first provider request. Existing usable state remains unchanged; malformed or inverted windows fail closed. Initial anchors preserve October bounds across a substantially later retry, and checkpoint-only windows use the durable checkpoint minus fourteen days. That fixed lower bound resolves the additional recent-checkpoint case without silently narrowing discovery as the clock moves. All enabled journals share the same output-before-progress boundary.

Revision independently executed the processor/durability/state suite: **38 passed in 3.05 seconds**. The actual failure-injection tests cover old and recent checkpoints, completed and interrupted discovery, capped 101-item pagination, first-ever failed output, multiple journals, invalid output, failed anchor creation and output-success/state-failure idempotence. Prior reactions/solutions and appended user-record fields remain intact. These checks use controlled provider fixtures, not real publisher downloads.

Final Independent QA additionally reports an independently authored real-Git integration scenario: two journals with 101 articles each, failed atomic output, a rejected actual feed-B push, guarded state-save rejection, total work/cache eviction, November replay of original October anchors and recovery of **202 distinct DOIs exactly once**. QA then pushes recovered B, verifies its provenance and excludes private fixture files. Revision inspected that final report and the production code; this combined fixture is QA's independent execution, not claimed as a second Revision execution.

The standalone exporter still treats the explicitly supplied curated baseline as authoritative for matching IDs. This unchanged behavior is distinguished from appended user-record preservation and browser-local personal edits; the review does not claim an older generated feed overrides the chosen curated source.

## CI feed/state boundary and actual concurrency check

The actual workflow now orders authoritative restore → shared anchor preparation → guarded durable bootstrap against acknowledged old feed A → discovery/output B → compact feed commit/push → guarded advanced-state save. A failed bootstrap stops discovery, and failed feed publication cannot reach the final state step. The failed collection outcome is preserved even when subsequent valid output/build steps succeed.

The actual `paper_state.save` verifies explicit ref/commit/library digest against local output, the committed library blob and origin's exact advertised ref. An unpublished B or wrong/stale identity fails before remote state changes. Bootstrap A and final B can be saved in the same run. Restore removes advancing cached metadata absent from the authoritative snapshot while retaining archive bytes. The bounded public whitelist and newer-run rejection remain intact.

Beyond static inspection and the focused tests, Revision independently injected a real temporary bare-Git race: run 102 published state after run 101 had read the old state but before run 101 pushed. The production `--force-with-lease` push rejected run 101 with stale information; the remote retained the exact run-102 snapshot. Result: **`REVISION_ACTUAL_STATE_CAS_RACE_PASS`**. This verifies that a competing update is not silently overwritten. No repository source or external remote was modified by this fixture.

## Exact-source build evidence and separate hosting block

Revision recomputed all six retained [manifest](web/manifest.json) file byte counts/hashes and compared every raw byte with immutable receipt **`5829825cf51ea5a5677922886eb1c8575405822e`**. Result: **`REVISION_ROUND03_EXACT_CI_EVIDENCE_BYTES_PASS`**.

- Run: <https://github.com/chemryu/chembrain/actions/runs/39093753253>.
- Workflow and built commits: `56be43bf15b4c98b8b515d2dc3bbd2bd0fcbbbae`.
- Public-library SHA-256: `25e98df9810b686e9da2c3c3b3f7f5da627dd2186ab3b00533b28d34072aef8c`, matching actual local bytes.
- GitHub Python tests: **273 passed, 1 skipped**; the skip is Windows-only DPAPI, outside the superseding browser milestone. Production web build and real Chromium smoke: **PASS**. QA independently reran the full suite/build/browser as recorded in its report.
- Collection/feed steps were skipped on this push run. Local actual-processor/Git fixtures establish failure-recovery coverage; this is not represented as live scheduled collection.
- New, actually observed Pages result: **HTTP 403 `Resource not accessible by integration`**. Deployment and public HTTPS checks are **SKIPPED / NOT RUN**; terminal status is `blocked`, `page_url` is null.

The prior source's Pages failure was not assumed. This current receipt establishes the same external configuration blocker on the newly reviewed source. Owner Pages Source information remains pending. No guessed URL, permission bypass, main merge or green build substitutes for successful deployment and actual HTTP source/data/digest verification.

## Wiki handoff and termination boundary

Wiki should preserve this report and final QA verbatim, record **WEB-QA-05 / WEB-REV-05 resolved, 0 remaining code findings, both independent source reviews PASS**, and retain **overall delivery BLOCKED_EXTERNAL_PAGES_CONFIGURATION**. There is no new code repair to return to Planning from this round. Await owner configuration and obtain actual exact-source deployment/HTTPS evidence before declaring the accessible preview delivered. Any later source/build-input change requires a new frozen SHA and affected checks plus both independent reviews.

Weekly operation remains unactivated: the dispatcher is a fail-closed unconfigured review artifact; no default-branch schedule, user-PC task or Box synchronization was installed. Private PDF/review storage is a persistent local processor directory or best-effort Actions cache, not a permanent Git document archive. The three-paper/twelve-draft starter facts and scientific unknowns remain unchanged; complete extraction, stereochemical verification, SI review, all-publisher OA coverage and autonomous background GPT service are not claimed. Browser edits remain local with compact backups. Windows EXE checks are not required for this superseding browser delivery.
