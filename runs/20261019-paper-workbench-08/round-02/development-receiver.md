# Development — reviewed receiving of existing chemistry facts

- Rejected baseline: `8cbd5fe2fa92da03169922e1cc7a43bb59b0a89d`.
- Implemented against the round-02 Planning contract. This is Development evidence, not independent approval. Root owns the new frozen source SHA, aggregate builds, actual-file CI and the final review loop.
- Owned application/test files only: `src/importReview.ts`, `src/MolecularLibrary.tsx`, `src/import-review.css`, `tests/test_import_review.py`, `scripts/import_handoff_smoke.py`.

## Receiving contract

The planner validates the complete package and resolves chemical IDs/InChIKeys and normalized DOI/paper IDs before comparing source facts. Same-ID solutions now receive compatible missing quantities/concentration and a genuinely empty composition. Chemical/role keys align solutes, preserving local ordering. Known unit/context mismatches, duplicate identities and nonempty changed memberships/roles are explicit conflicts; no numerical conversions are invented.

Existing reactions now receive an explicit ordered sequence when their stages are empty, compatible missing temperature/time on uniquely aligned stages, and a suffix only when the entire existing ordered sequence is an unambiguous prefix. Changed links, insertion, reordering, shortening and changed repeated-solution sequences conflict. Strictly identical complete same-pot repeated-solution sequences are accepted as no-ops; they need no ambiguous alignment. Yield and basis use a shared compatibility rule, so a new basis is not attached to a retained unmatched yield.

Distinct DOI-remapped paper/page/locator tuples append without collapsing main/SI locations; exact incoming duplicates do not multiply. Existing names, notes, status, structures and other known edits are retained or protected. Retained source differences are reported separately. New stage solution rows remain connected through accepted stage references, and any conflict rejects the whole candidate.

## Review and persistence

The main review shows `Existing chemistry changes` with entity IDs, fields/actions and Previous/Incoming values, changed existing molecule/solution/reaction counts, qualified label additions, retained values and precise conflict fields. Conflict guidance tells the user to load the latest main Backup JSON in Workbench and reconcile current IDs/order/known values before source-checking/exporting again. Completed counts come from the candidate, and repeated unchanged import explicitly reports `no changes` with no primary rewrite or backup.

Every accepted change to an existing chemical, solution or reaction requires Apply and the same exact-private-byte transaction: validate the full candidate and displayed/raw baseline; save to a unique private backup; verify exact readback; recheck primary bytes after backup; perform one primary write; then update React state. Fact-only imports use this protection even with zero structure upgrades. Failed backup/readback/write or stale/concurrent state does not replace primary data or display the unpersisted candidate. Delayed older File.text results cannot replace a newer import plan.

## Executed checks

- `npx tsc --noEmit`: **PASS**, exit 0.
- `.venv/bin/python -m pytest -q tests/test_import_review.py`: **14 PASS**, exit 0. Actual TypeScript helpers are executed through TypeScript transpilation/Node, not a mirrored Python implementation.
- Real managed Chromium against an isolated Vite development server on port 5193: **PASS**, no page errors. Ran the complete `check_import_handoff(page)` including prior structure/identity/alias checks and new reaction/solution-only preview, exact backup, visible linked steps/conditions and DOI reference locations, reload persistence, no-op zero writes, quota/stale failure with old facts still visible, and an actual delayed File.text old-import/new-import race. The development server was stopped afterward.

The domain regressions cover empty and partial stages, empty composition, chemical/role quantity alignment, compatible missing units, concentration, yield/basis, ordered prefix with a linked new solution, insertion/reordering/reuse conflicts, all known scalar/unit/context conflicts, chemical and DOI ID remapping, distinct/deduplicated main/SI evidence, null-source preservation, invalid relations, exact whitespace backups, write/readback/primary/concurrency failures, and exact unchanged same-pot sequence idempotence.

The real Workbench-UI-export to main-UI transfer is owned by the separate Development transfer helper and remains distinct evidence. No hosted/portable build, actual file:// check, commit, independent approval or delivery claim is made by this receiver report. Root must run and record those checks for the new exact source SHA.
