# Revision — synthesis map round-01

- Role: separate Revision. Application code, tests and build inputs were not edited; no push, deployment, visibility change or browser-policy change was performed.
- Reviewed exact source: **`e6ed4e70028fa77dfd59cbeede249ccc1a52b274`**.
- Compared the independent Planning, Development and complete Independent QA reports, graph projection, map component and browser integration. Source HEAD remained unchanged at review completion.
- Decision: **CHANGES REQUESTED — 1 unresolved material application finding**. The user-delivery stopping criterion is not satisfied. Passing broad tests or a later successful CI run cannot approve the defect below.

## QA-SYN-01 — confirmed, P2, correction required

The mobile `focusSelected` branch in `src/SynthesisMap.tsx` reads the original projected `graph.nodes` position, while a card-header drag changes the live ReactFlow controlled nodes through `onNodesChange`. Consequently, the Focus button returns to the old graph location instead of the selected molecule's current location. The desktop branch delegates to live-node `fitView` and has different behavior.

Revision independently reproduced this against the already built production application at `/chembrain/` in real Chromium with viewport **390 × 844**, in an isolated disposable browser context:

1. Select **Paclitaxel (Taxol)**, bring the map canvas into view and press **Focus selected molecule**.
2. Drag the selected card header 200 screen pixels right.
3. Press **Focus selected molecule** again.

Measured selected-card bounds initially: `x=144.75, width=168`; after drag: `x=324.75, width=168`; after Focus: **`x=405.75, width=168`**. The canvas was **`x=40, width=310`**, ending at `x=350`. The selected card therefore remained entirely outside its visible canvas after Focus. No browser page errors occurred. These independent measurements differ slightly from QA's pixel values, but reproduce the same functional failure and confirm its cause in source. No chemistry or persistent user data was changed.

### Bounded task for next Planning → Development

Use the selected node's **current ReactFlow position and measured dimensions**, for example via `instance.getNode(graph.selectedNodeId)`, or a selected-node `fitView` using live state, when focusing on a narrow canvas. Keep the mobile card readable and respect the current canvas size. Do not use `graph.nodes`' initial placement for interaction after a drag. Preserve desktop context focus, graph scientific edges, normal pan/zoom, inspection without layout resets, and the rule that exploratory layout changes do not become chemistry data.

Extend the shared real-browser synthesis-map regression with the actual mobile interaction: select a target, Focus, drag its selected header far enough to move it beyond the canvas, Focus again, and assert that the live selected card is visibly inside the canvas with useful readable dimensions. Exercise this shared assertion in hosted and actual offline HTML checks. A source-string assertion or calling Focus before dragging does not cover the failure. Rebuild the web and portable outputs, freeze a new complete source SHA and obtain fresh independent QA/Revision plus exact-source portable CI/artifact evidence.

## Remaining requirement comparison

The reviewed implementation otherwise follows the bounded plan: molecule selection opens Map; List preserves the existing records/editing; edges derive only from recorded reactant/product IDs; target membership selects context without inventing missing chemistry; disconnected fragments and capped displays are stated explicitly; namespace separation, iterative cycle handling and whole-reaction participant retention protect graph integrity. Reaction selection reuses the existing condition/solution/DOI-author inspector. No additional material issue was identified in these reviewed areas.

Evidence must retain its actual provenance: Development reports **289 passed / 1 Windows-only skipped** for its full Python suite. Independent QA separately executed **15 focused tests**, production build, hosted browser suite and source/distribution payload gates, all PASS; its extra mobile selected-card drag test failed. Revision independently executed the focused mobile reproduction above, rather than relabelling Development's full suite as its own. The review does not erase any passing result, but the missing regression allowed QA-SYN-01 to escape the broad smoke.

At this report's completion, fresh CI run **`39140468551`** is pending final receipt/artifact verification by the coordinator. Local actual `file://` execution remains NOT RUN because the managed browser blocks file URLs; no workaround or policy bypass was attempted. The exact-source portable manifest recorded by QA is identity evidence only, not approval of that artifact. Even subsequent successful CI evidence for this SHA will not resolve QA-SYN-01.

Pages configuration/access, old reachable quotations/crops, unverified remote artifact/cache contents, inactive weekly scheduling, lack of Box sync and browser/profile/file-location storage constraints remain separate pre-existing limits. This report approves neither a hosted URL nor Public/history cleanup nor a production release.

## Wiki handoff / stopping criterion

Preserve complete `qa.md` and this `revision.md` verbatim and record their hashes. Return **QA-SYN-01** through Wiki to a bounded **round-02 Planning** task using the correction and real-browser regression above. Keep round-01 source and artifact explicitly rejected; do not replace this report with a later fix's verdict or transfer approvals between SHAs. Final application delivery must wait for the new source's zero-finding independent reports and required exact-source checks.

## Subsequent exact-source CI supplement — required browser check blocked

After the initial report, the coordinator captured the terminal immutable receipt **`44c569c9fc284fe30fb59b440a61eb7ad084ed57`** for run **`39140468551`**, source/build **`e6ed4e70028fa77dfd59cbeede249ccc1a52b274`**. Revision independently compared all four captured raw files (`status.json`, `web-tests.log`, `web-build.log`, `web-browser.log`) byte-for-byte with that Git receipt and verified their byte counts and SHA-256 values against `web/manifest.json`; all matched.

The actual CI result supersedes the earlier pending observation: Python **289 PASS / 1 SKIP** and TypeScript/production build **PASS**, but the hosted browser step **FAIL**. Portable build/file-browser validation and portable artifact upload were **SKIPPED** after that failure. Collection/feed were SKIPPED. Pages publication was **not attempted in this run**; prior Pages403 remains historical evidence rather than a fresh observation here. The terminal receipt is blocked with `page_url=null`; there is no newly approved downloadable artifact or hosted delivery for this source.

The captured browser log contains a large DOM snapshot without the original traceback/assertion. Inspection of `scripts/report_web_build.py` confirms its last-120-lines truncation can discard that diagnostic before preserving the receipt. Therefore the failed CI browser assertion's **cause is unresolved**. Do not label the independent mobile defect as the cause without actual traceback evidence; local hosted smoke passing also cannot turn the runner failure into PASS.

Add a second bounded task to round-02 Planning: preserve useful browser failure diagnostics in the receipt (bounded head plus tail, or a concise exception/traceback summary alongside bounded context), rerun the exact-source browser CI, inspect the actual failing assertion and fix any demonstrated app/test problem without weakening the check. Require the hosted browser step, standalone build, actual offline `file://` check and artifact identity verification to succeed on the new fixed SHA. The current disposition remains **1 unresolved material application finding plus an unresolved required-CI evidence failure**, not zero-finding delivery approval. Original report chronology and all current evidence remain preserved.
