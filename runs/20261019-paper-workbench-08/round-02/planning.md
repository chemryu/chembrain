# Planning — Paper Workbench round-02 receiving-contract repair

- Run/role: `20261019-paper-workbench-08 / round-02`, separate Planning. This role writes this plan only; no application/test/build changes or approval.
- Rejected baseline: **`8cbd5fe2fa92da03169922e1cc7a43bb59b0a89d`** on `codex/gpt-agent-workflow`.
- Inputs read: AGENTS/RULEBOOK/current request and round-01 Planning, complete Independent QA and Revision reports including terminal CI supplements, formal Wiki→Planning `round-01/handoff.md`, immutable receipt manifest and the receiving planner/transaction/UI plus current import and two-program/map smoke tests.
- New implementation/review SHA: **not frozen**. All source changes require a new full SHA and fresh exact-source review; no prior approval or artifact transfers.

## Why another round is required

Both independent roles returned **CHANGES_REQUESTED**, one **P1 QA-PW-01**. The existing import planner detects chemical identity/structure collisions, solution membership changes and reaction participant changes. Its old-record-wins merge then silently discards same-ID incoming reaction stages/solution links, conditions, quantities and evidence differences. Empty `steps=[]` and null concentration/solute amounts therefore stay empty despite a source-checked Workbench export. An appended stage can import its new solution as a disconnected row while dropping the actual stage link. Different known values are retained without showing the chemistry that was not received.

Preserving local edits remains correct. The fix must distinguish compatible missing-fact enrichment from known-value conflicts, explicitly show/apply accepted changes and provide a concrete reconciliation path for rejected differences. Do not replace existing rows wholesale or change generic feed precedence.

The second blocker is independent: actual CI **39204595894**, immutable receipt **`546a9afe693f52c5165d76651748dd0984c56924`**, contains **316 PASS / 1 Windows DPAPI SKIP**, hosted build PASS and hosted browser **FAIL**. The preserved traceback reaches `scripts/synthesis_map_smoke.py:59`; the reaction inspector is absent after a card drag followed by focus/Enter. The underlying application-versus-interaction/timing cause is **UNRESOLVED**. Main portable, Workbench, actual-file transfer and artifact upload were skipped; Pages was not attempted. This run provides no new deliverable. The older Pages403 and earlier lost-diagnostic CI remain historical, separate facts.

## Bounded Development tasks

### 1. Plan existing chemistry facts after consistent identity mapping

Extend the reviewed import plan to cover concrete existing **solution** and **reaction** facts, not just structures/labels. Build the final chemical, solution and DOI/paper identity maps first, validate their collisions, then compare the canonical remapped records. Every candidate stage reference and evidence paper ID must resolve to the accepted final entity. Names/formulas alone never establish chemical identity. Solution IDs with incompatible nonempty composition are not interchangeable merely because stage positions agree.

For each existing solution, inspect solvent membership, each solute's chemical ID **and role**, amount/unit, and concentration/unit. Truly empty composition may receive the explicit incoming composition; compatible existing composition may receive genuinely missing values. Nonempty differing memberships, duplicated/ambiguous chemical-role alignment and different known roles are visible conflicts, not automatic relinking. Treat a number and its unit as a meaningful pair: filling an absent amount while retaining an incompatible local unit must not create a new incorrect fact. Apply the same compatibility rule to concentration/unit. Preserve all known user values and private notes.

For each existing reaction, inspect ordered stages/solution links, stage temperature/time, yield/yield basis and all accepted evidence after remapping. An empty stage list may receive the incoming explicit sequence after review. Aligned existing stages may receive compatible missing conditions. A new suffix may be proposed only when the complete existing ordered sequence is an unambiguous compatible prefix; inserting/reordering stages, reused/ambiguous stage identities or incompatible solution links requires reconciliation. Do not match stages by a convenient index, unordered solution set or similar condition text. Preserve recorded ordering and distinct stage instances. Null/empty incoming fields never erase local facts.

Yield and yield basis require compatible context; a missing basis must not silently be attached to a different retained yield. Different non-null temperatures, times, yields, units, concentrations or amounts remain visible retained/conflicting source facts. Existing names, aliases except already-authorized paper-label additions, notes, status and non-null structures remain local; any ignored incoming differences relevant to the review are identified instead of implying complete receipt. Do not automatically promote draft records to scientifically reviewed status.

Source evidence is additive only after valid DOI identity mapping and distinct document/page/locator preservation. Deduplicate exact evidence tuples without collapsing same-DOI main/SI locations. Every new accepted stage solution must stay connected to its reaction. If an intended stage cannot be accepted, the package is visibly unresolved/rejected rather than apparently complete with a disconnected new row.

### 2. Show the actual proposal and reconciliation path

Add structured plan entries for every existing-field/stage/evidence enrichment and every retained/conflicting known fact. The main review UI shows entity name/ID, field or ordered stage, previous value and incoming value, plus concrete additions/retentions/conflicts and counts. Count changed chemicals, solutions and reactions separately from added rows; preview and final notice derive from the actual resulting candidate, not only source counts.

All existing-fact changes require explicit Apply. A safe initial behavior is to block a conflicting whole package and explain the exact record/field and how to reconcile it: export the latest main backup, load it in Workbench, preserve current IDs/order/local values, make the intended source changes, source-check and export again. Do not silently dismiss conflicting incoming values, create new IDs behind the user's back, invent conversion values or make an import look complete when facts remain unresolved. Safe missing additions in a conflict-free package can be applied together. The final notice states actual changes and retained records; a no-op is explicitly a no-op.

### 3. Generalize the existing private transaction to every accepted fact update

Construct and validate the **entire** proposed library and all foreign keys before touching storage. For any accepted update to existing structures, labels, solutions, stages, conditions, yield or evidence:

1. Compare exact current primary bytes with the import's captured raw baseline and confirm the validated baseline matches the currently displayed library.
2. Save those exact raw bytes to a unique private backup key; verify byte-for-byte readback without overwriting another backup.
3. Recheck primary bytes after backup and immediately before the one primary replacement.
4. Write the fully validated candidate once, then update the working React state only after successful persistence.

A backup, readback, primary-write or stale/concurrent-baseline failure must not replace primary data or switch the working UI to an unpersisted candidate. Concurrent user changes remain untouched. The UI's asynchronous molecular inspection must not let an older import or changed displayed library apply a stale plan. All existing-fact enrichment triggers review and backup even when there is no structure upgrade. General new-row import behavior remains compatible. Re-import of an accepted unchanged package is idempotent and causes no unnecessary primary rewrite/backup.

### 4. Diagnose and repair the real hosted keyboard failure separately

Use the complete saved CI traceback/state and the read-only diagnostic agent's observations to establish the current cause. Keep drag geometry, keyboard focus/Enter activation, inspector contents, selected state and placement assertions. If the test races real focus/layout, wait for the actual state and assert focus before activation; if the app mishandles a real keyboard action after dragging, repair that behavior. Do not replace Enter with pointer clicking, remove assertions, add blind retries that hide failures or describe an unverified hypothesis as the cause. Preserve concise actionable diagnostics for another failure. Earlier local PASS does not satisfy the actual runner gate.

## Acceptance and meaningful regressions

**Domain/transaction tests must exercise the actual helpers**, with preserved baseline/source snapshots and no implementation-mirroring-only assertions:

- Saved same-ID reaction starts with `steps=[]`; incoming provides a source-checked sequence, linked solution, conditions, quantities, concentration and evidence. The exact facts reach the proposed candidate only through explicit review.
- Existing stage has partially known temperature/time and existing solution has known composition but null amount/unit or concentration/unit. Fill only compatible gaps, retain known values and custom notes, and report every change. Include empty composition as a distinct case.
- Existing ordered stages form an exact unambiguous prefix of a longer incoming route; accepted new stage and its new solution remain linked. Insertion/reordering, duplicate solution reuse, conflicting links, incomplete ambiguous stage alignment, nonempty changed composition and differing solute roles produce visible reconciliation conflicts. Do not leave a disconnected imported solution while claiming its stage transferred.
- Different non-null time/temperature/yield/basis/concentration/amount/unit remains protected and visible. Quantity/unit pairs with incompatible retained context are rejected. Null incoming values do not erase local data.
- Chemical InChIKey-based identity remap and normalized same-DOI paper ID remap propagate through solution components, reaction participants/targets, stages and every evidence tuple. Same-DOI main/SI locators survive distinctly; evidence duplicates are idempotent.
- Exact original whitespace/bytes backup precedes every chemistry fact update even with **zero chemical structure upgrades**. Test backup write/readback failure, primary failure, changed primary before review/apply, concurrent change during backup, displayed-baseline mismatch and stale asynchronous import results. Old primary and UI remain usable; existing backup is never overwritten. Repeat import produces no new changes or writes.
- Preview counts/field values match the actual persisted candidate; conflict/no-op/completed notices are truthful. Invalid nested data/dangling foreign keys still reject the full candidate without storage mutations.

**Actual two-program browser transfer is mandatory**, not a synthetic direct-helper-only substitute. Extend the Workbench smoke so it source-checks and exports through the real UI, opens the real main program with a previously saved library containing the **same IDs**, then reviews/applies and reloads to verify:

1. empty stages and null quantities/concentration receive the complete ordered stage links, conditions and evidence;
2. a partially known existing stage/quantity baseline receives only its compatible missing facts;
3. conflicting known facts and stage order show the reconciliation path and do not mutate storage;
4. exact private backup exists for solution/reaction-only enrichment, repeated import is a no-op, and simulated quota/stale review failures leave old data visible.

Keep the existing current-SMILES/stereo/source-state/private-PDF/strict-projection/security, drawing/sketcher, molecule-first map/List/mobile Focus, legacy migration and edited-data preservation checks. Use synthetic private PDF fixtures only in automated tests; no actual paper bytes/prose/page images/private source paths in Git, public outputs, CI receipts, artifacts or traces.

## Required evidence and role loop

Development records affected/full Python results, TypeScript, hosted build/browser, both portable builds, payload gates and local supported checks. Local HTTP-only portable results remain explicitly HTTP-only; the managed file-policy restriction is not bypassed. Freeze/push a **new full source SHA** before both independent reviews.

Fresh exact-source CI must pass hosted keyboard/map interaction and proceed through **both actual file:// HTML programs**, real private synthetic PDF/worker, export-to-main transfer, storage/update regressions and both artifact manifests. Match actual HTML bytes/SHA-256, same source SHA, dependency notices/versions and relevant library digest to the preserved immutable receipt. A skipped or pending mandatory file/artifact step is not PASS. Do not independently claim a downloaded artifact ZIP hash if only the reported CI digest was observed.

Independent QA and Revision separately inspect the new frozen source and concrete transfer regressions without changing application code. Each must resolve QA-PW-01 and assess any new findings. Required checks and both independent verdicts must pass for the exact delivered source/artifacts. Wiki preserves round-01 rejection/raw receipt and this round's full reports, then returns unresolved work to Planning or records completion with zero unresolved material findings. Root publishes final records on the separate records branch; no source approval is created by a record commit.

## Unchanged scope and limits

Workbench remains private source-assisted manual curation and graph encoding, not automatic exact optical structure recognition or scientific validation of the paper. No new journal downloader, weekly activation, external model API/credentials, user-PC installation, Box sync, perpetual agents, main merge, visibility/permissions change or shared-history rewrite. No publication success is inferred from a downloadable artifact. Earlier paper quotations/crops and unverified remote storage remain historical Public limitations. Browser profile/file-path storage limits and exact private backups remain explicit. This plan is the formal bounded repair handoff, not implementation or final delivery approval.
