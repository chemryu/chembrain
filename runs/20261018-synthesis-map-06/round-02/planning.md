# Planning — synthesis map round-02

- Role: separate Planning; no application implementation, commit or publication performed.
- Run/round: `20261018-synthesis-map-06 / round-02`.
- Starting source: **`e6ed4e70028fa77dfd59cbeede249ccc1a52b274`**; rejected round-01 candidate, not a delivery approval.
- Sequence: read the complete round-01 `qa.md` and `revision.md`, including subsequent exact-source CI supplements, then the formal [Wiki → Planning handoff](../round-01/handoff.md) before finalizing this plan.
- Current disposition: **1 confirmed material application finding (QA-SYN-01), plus an unresolved required CI browser failure**. Preserve all original reports and their chronology.

## User goal and preserved scope

The user requested a brainstorming-style synthesis process when clicking a molecule. Keep the implemented molecule-selected default Map and explicit List alternative, genuine reactant → reaction → product edges, target-tagged but unconnected fragments, visible missing-step/draft/cap notices, pan/zoom/Fit, reaction conditions and DOI/author inspector, chemical refocus, edits, browser data and JSON backup/import. Existing runtime graph cycle/cap/namespace/nonmutation protections and strict chemistry/DOI/authors-only metadata remain intact. This round is a bounded repair, not a new graph design or chemistry-generation feature.

## Task 1 — QA-SYN-01: mobile Focus must use live dragged positions

The narrow-canvas branch of `focusSelected` in `src/SynthesisMap.tsx` currently reads the initial `graph.nodes` position. Header dragging updates ReactFlow's live controlled nodes, leaving that original position stale. Both independent roles reproduced a 390 × 844 mobile selected-card drag after which Focus leaves the card entirely off-canvas.

Development must focus the **current** selected ReactFlow node, for example through `instance.getNode(graph.selectedNodeId)` with its live position and measured dimensions, or selected-node `fitView` that reads live state. Keep the mobile card readable, account for the actual canvas dimensions, and retain desktop context behavior. Handle the brief not-yet-measured/missing-node state safely. Merely resetting all nodes to original layout before Focus would discard the user's exploratory arrangement and is not the requested correction.

Add the regression to `scripts/synthesis_map_smoke.py`, shared by hosted and portable suites:

1. Select Paclitaxel at viewport 390 × 844, bring its canvas into view and Focus.
2. Drag the **selected molecule's header** approximately 200 screen pixels so the live card moves beyond the canvas, asserting a real placement change.
3. Focus again and assert the live card is visibly inside the canvas at useful readable dimensions. Compare actual card/canvas bounding boxes, not only viewport transform strings.
4. Verify no page errors, no chemistry/local-storage write from graph exploration, and preserve desktop pan/zoom, card placement across reaction inspection and Map/List coverage.

Use bounded Playwright readiness/geometry assertions for animations and node measurement instead of weakening the assertion or relying only on a longer arbitrary delay. Run the same essential interaction from actual offline `file://` HTML in the authorized CI browser; local HTTP-only execution must remain labelled HTTP-only.

## Task 2 — retain CI diagnostics, then resolve the observed browser failure

Actual round-01 CI **39140468551**, immutable receipt **`44c569c9fc284fe30fb59b440a61eb7ad084ed57`**, proves Python **289 PASS / 1 SKIP**, TypeScript/build **PASS**, and hosted browser **FAIL** for `e6ed4e7...`. Portable build/file-browser/artifact steps were **SKIPPED**. Pages configuration was not attempted; publish/access were NOT RUN and URL null. Prior Pages403 is historical, not an observation from this failed run.

The original failure cause is **UNRESOLVED** because `scripts/report_web_build.py` retains only the final 120 lines before applying a byte cap. A verbose DOM snapshot displaced the traceback and failed assertion even though the resulting receipt is only a few kilobytes. Do not declare QA-SYN-01 to be the CI cause without an actual traceback; independent local hosted PASS does not invalidate runner FAIL.

Development must preserve actionable bounded evidence:

- Preserve short diagnostic logs completely, based on the byte bound rather than an unconditional line-tail cutoff.
- For larger logs, retain bounded beginning and ending context with an explicit omission marker, staying within a documented size limit. Ensure the actual exception/test identity remains available; a concise failing phase/exception summary near the end of the smoke output is also useful.
- Add a focused meaningful regression reproducing a short, many-line assertion/DOM log whose first traceback would formerly be lost, plus an oversized log with distinguishable beginning/end diagnostics. Assert bounded size and preservation of both diagnostic ends. Existing receipt source/run identity, immutable evidence and finalizer semantics must remain intact.
- Re-run the actual hosted browser CI on the fixed frozen SHA. Inspect the retained failing assertion if any and fix the demonstrated application/test defect without skipping a test, changing FAIL to warning, relaxing the scientific requirement or substituting a different source's local PASS. A demonstrated new material issue returns through the existing QA/Revision/Wiki workflow.

## Exact-source acceptance and evidence

Development records changed paths and actual commands, then freezes a new full source SHA. Appropriate focused map/data/receipt tests and the full existing Python suite must pass, as must ordinary web TypeScript/production build, standalone build, tracked-source and distribution payload gates, real hosted browser and shared mobile-drag regression. Preserve every prior editor/import/storage-failure/backup/security/offline check.

The fresh CI must show hosted browser **PASS**, portable build **PASS**, actual offline **file://** browser **PASS**, and an uploaded portable artifact with its source SHA, real HTML bytes/SHA-256 and manifest identity verified. If local browser policy blocks file URLs, record local actual-file **NOT RUN** without bypass and use fresh CI's genuine file execution as that evidence. Do not approve a local manifest alone or claim a skipped artifact exists. A Pages permission failure, if actually encountered later, is separate from successfully validated downloadable HTML and must be recorded as observed.

Separate Independent QA independently reproduces the fixed mobile scenario and reviews the new exact source, diagnostics and actual CI/artifact. Separate Revision compares QA and implementation, confirms resolution or returns actionable findings. Wiki preserves full reports/hashes and updates progress. Stop only when both independent roles have zero unresolved material findings and all checks required for the delivered artifact pass for its exact source. Never transfer round-01 source/artifact identity or approval to the fix.

## Limits retained

No additional dependency or personal AI API, fabricated chemistry, PDF/original-paper upload, Public/permission change, shared-history rewrite, main merge, Box synchronization or schedule activation is authorized. Old quotation/crop blobs and unverified remote Actions storage remain separate. Browser profile/file-location storage limitations and existing collection inactivity remain unchanged. The older `aaf4d8b...` download is historical, not a synthesized-map feature artifact.
