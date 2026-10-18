# Independent QA — synthesis map round-01

- Role: separate Independent QA; application source not edited.
- Exact inspected and executed source: `e6ed4e70028fa77dfd59cbeede249ccc1a52b274`.
- Run: `20261018-synthesis-map-06 / round-01`.
- Verdict: **CHANGES REQUESTED — 1 unresolved material finding**. Passing broad smoke does not override the independently reproduced focus-control defect below. This source and its portable artifact are not approved for delivery.

## QA-SYN-01 — P2: mobile Focus uses the old layout after the selected card is dragged

- Location: `src/SynthesisMap.tsx:59`–`62`, `focusSelected` narrow-canvas branch.
- Cause: the mobile branch reads `graph.nodes` projected positions and passes them to `instance.setCenter`. Dragging changes ReactFlow's controlled `nodes` through `onNodesChange`, not those original graph positions. Desktop focus uses `fitView` on live nodes and does not have this mismatch.
- Reproduction on the real built app at `/chembrain/`, Chromium, viewport **390 × 844**:
  1. Choose Paclitaxel (Taxol), scroll the map canvas into view, and press **Focus selected molecule**.
  2. Drag the selected molecule's card header **200 screen pixels to the right**.
  3. Press **Focus selected molecule** again.
- Expected: the selected molecule's current card is brought back into the visible canvas.
- Actual: focus returns to the initial graph coordinates, leaving the actual dragged card entirely off-canvas. The independently measured card box was `x=438.375,width=168`; canvas box was `x=40,width=310`, so the card lies wholly beyond the visible right edge. No storage or chemistry data was changed.
- Required correction: use the current ReactFlow node position/dimensions, or fit the current selected node, in the narrow-canvas branch. Add a real-browser regression that drags the selected molecule on a mobile canvas and verifies Focus brings that live card into view. Rebuild and review a new exact source/artifact; do not transfer this source's passing checks to the fix.

## Independently executed checks

Environment: Python 3.12 virtual environment, Node 24, installed local Chromium through Playwright; existing checkout only.

| Check | Result | Evidence / scope |
| --- | --- | --- |
| Focused actual runtime tests | **PASS: 15** | `tests/test_synthesis_graph.py tests/test_web_library_data.py tests/test_portable_contract.py tests/test_repository_payloads.py` |
| Hosted production TypeScript/build | **PASS** | `CHEMBRAIN_BASE=/chembrain/ npm run build:web`; source unchanged |
| Actual hosted browser suite | **PASS** | `.venv/bin/python scripts/web_smoke.py`; Map/List, recorded fragments, node keyboard, reaction inspection, pan/zoom/Fit, dragged reaction retaining placement, empty/oversized map, map refresh after edit/import, old data preservation/editor/import/mobile cases |
| Extra independent mobile selected-card-drag test | **FAIL** | QA-SYN-01 above; this case was absent from the development smoke |
| Tracked-source payload gate | **PASS** | 156 tracked files |
| Hosted distribution payload gate | **PASS** | 13 distribution files |
| Actual `file://` portable execution on local managed browser | **NOT RUN** | Known local browser administrative policy blocks file URLs. No policy bypass performed. Fresh CI evidence is still pending and cannot be inferred from HTTP-only testing. |
| New exact-source CI final result / artifact download | **PENDING at initial report** | Root owns receipt fetch. CI result cannot cure QA-SYN-01 and this source remains rejected. |

The full `289 passed / 1 Windows-only skip` result is Development evidence, not an independently rerun full suite in this QA role. The independent 15-test subset and browser checks are reported separately.

## Code and scientific review

No additional material finding in the reviewed projection/integration:

- Edges derive exclusively from actual reactant/product IDs. Target membership does not invent a transformation. Paclitaxel's five recorded connected fragments and doxycycline's two stay separate, with visible gap notices and draft status.
- Molecule/reaction namespaces, endpoint deduplication, iterative SCC/cycle handling, deterministic layout and nonmutation match the normalized contract. Reaction/node caps omit whole reactions with all participants; explicit partial/no-complete-reaction messages and List fallback avoid false completeness.
- Default Map opens only after a molecule is selected. Existing linear cards, editing, solution conditions and DOI/author-only references remain available. Selection, save/import and view changes clear stale reaction inspection. Layout exploration writes no chemistry data.
- No new dependency, backend API, PDF, paper crop, generated scientific fact, visibility change or history rewrite is introduced.

## Artifact and external limits

Local exact-source portable manifest at review time: `Chembrain.html`, **722493 bytes**, SHA-256 **`fc5560a6469c725e286fff65a16c24a9493f05828c4756cdded7ff709f50c614`**, source `e6ed4e70028fa77dfd59cbeede249ccc1a52b274`; normalized-library SHA-256 `7853ba5d2b335c274733b8c726ac7b80c899e9d51bfd42295279ea75df2452bb`. This is identity information, not artifact approval or proof of a downloaded archive.

Prior Pages403, old quotation/image blobs in Git history, remote artifact/cache contents not fully inspected, inactive weekly collection, no Box sync and browser profile/file-location storage limitations remain separate unchanged constraints. No hosted URL, Public clearance or production release is approved by this report.

Handoff: Revision should independently assess QA-SYN-01 and return its complete report through Wiki to a bounded next Planning round.

## Independent portable supplement (same rejected source)

`.venv/bin/python scripts/portable_smoke.py --http-only` completed **PASS** on the exact manifest/HTML above. Its in-memory main document ran offline with every additional request rejected; embedded assets, new map controls, old editor/backup/import/storage-failure/mobile/hostile-embedding coverage passed. This is explicitly **HTTP-only**, not a local `file://` execution claim. It does not cover the additional mobile selected-card-drag scenario and does not resolve QA-SYN-01.

## Exact-source CI supplement — terminal evidence, original report preserved

- Fresh run: [39140468551](https://github.com/chemryu/chembrain/actions/runs/39140468551).
- Immutable terminal receipt: `44c569c9fc284fe30fb59b440a61eb7ad084ed57`.
- Both workflow and built source: `e6ed4e70028fa77dfd59cbeede249ccc1a52b274`; normalized-library hash agrees with the identity recorded above.
- Independently byte-compared **all four** retained `web/` raw files with their immutable Git objects and the capture manifest's byte counts/SHA-256. No personal GitHub API access or artifact-download claim is implied.
- Actual full CI tests: **289 PASS / Windows-only 1 SKIP**. Hosted app production build: **PASS**. Actual hosted-browser workflow: **FAIL**, so aggregate build job is **FAIL**. This differs from the independently passing local hosted suite; both observations are retained.
- The retained `web-browser.log` is only the last 120 lines, dominated by a large DOM snapshot. The assertion/traceback head is absent. Therefore **the CI failure cause is UNRESOLVED**. QA-SYN-01 is independently established but is **not claimed as this CI failure's cause**.
- Portable build/execution and downloadable-artifact upload were **SKIPPED** after the hosted-browser failure. There is no new CI-verified `file://` artifact or download for this source. Local HTTP-only portable PASS is not upgraded to file execution.
- Pages publish was **NOT ATTEMPTED / SKIPPED** on this run, `page_url=null`. Prior Pages403 belongs to earlier runs and is historical; no fresh Pages403 is claimed here. Journal collection was skipped.

Final round-01 verdict remains **CHANGES REQUESTED — QA-SYN-01 unresolved**, with the additional **required CI browser check FAIL / cause unresolved**. Next Planning must include durable compact failure diagnostics (retain assertion/traceback head as well as tail) and a fresh actual CI rerun, alongside the mobile live-position focus fix. A passing local suite or a guessed CI cause is insufficient for delivery.
