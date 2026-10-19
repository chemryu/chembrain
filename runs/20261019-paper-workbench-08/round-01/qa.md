# Independent QA — Paper Workbench / round 01

- Role: separate Independent QA; no application, test, data, build input or Git HEAD changes.
- Exact inspected source: `8cbd5fe2fa92da03169922e1cc7a43bb59b0a89d`.
- Run: `20261019-paper-workbench-08 / round-01`.
- Decision: **CHANGES_REQUESTED**. One unresolved material finding; no approval is transferred from an earlier source or artifact.

## QA-PW-01 — source-checked stages and solution quantities disappear on existing-ID handoff

**Severity: P1 / high.** Files: `src/importReview.ts:78`, `src/importReview.ts:82`, `src/importReview.ts:88`; receiving UI `src/MolecularLibrary.tsx:65`, `src/MolecularLibrary.tsx:104`.

The receiving planner protects existing solution chemical-ID sets and reaction participant/target sets, then calls the old-record-wins merge. It does not compare or propose additions for a reaction's ordered stages/solution links, temperature/time, yield/evidence, or a solution's concentration and solute role/amount/unit. Chemical structure upgrades and paper-label additions have explicit review, but these chemistry facts do not. Consequently a Workbench correction of an existing draft can export accurate recorded stages and still leave the main app's corresponding stage blank without a conflict or a retained-fact warning. A newly added source-stage solution can be imported as a disconnected row while the old reaction silently retains its previous stage list. Preserving existing user edits is necessary; silently dropping newly recorded route/solution facts does not meet the handoff requirement.

### Independent reproduction

I ran the actual TypeScript `prepareImportReview`/`commitReviewedImport` through the existing read-only Node harness in `tests/test_import_review.py`, without changing tests or sources:

1. Start from `fixture()` with a saved reaction `r` and solution `s`. Set `r.steps=[]`, `s.concentration=null`, `s.concentration_unit=null`, and its solute's `amount/unit=null`.
2. Clone as incoming normalized facts, preserving every ID and participant. Set `r.steps=[{solution_id:'s',temperature:'-78 °C',time:'30 min'}]`, solution concentration `0.1 M`, and solute amount `1 mmol`.
3. Call `prepareImportReview(current,incoming)`.
4. Actual: `conflicts=[]`, `changed=false`, `next.reactions[0].steps=[]`, concentration/amount remain `null`; committing performs zero writes. The UI's normal completion notice does not identify any discarded facts.
5. A second probe keeps the old first stage, adds a new incoming solution `source-stage2`, and appends its recorded second stage. Actual: `added.solutions===1`, no conflict, and the resulting existing reaction still has one stage; the new solution has no new link from that reaction.

Expected: after remapping participant/solution IDs, distinguish safe missing-fact enrichment from differences with existing values. Display the proposed stage/solution changes or a clear retained/conflicting-facts review, require explicit apply for saved-library changes, preserve non-null local edits, and back up exact original private bytes before applying. Do not overwrite local steps or conditions blindly. Repeat import must remain idempotent. Meaningful regression cases must cover old empty stages, added ordered stages/new solution links, missing concentration/amount/unit, differing existing values and failure of backup/primary storage.

## Independently executed checks

| Check | Result | Evidence / limit |
| --- | --- | --- |
| Exact source and role/review constraints | PASS | HEAD was checked before and after probes: full source SHA above. Only this QA report was written. |
| Current focused domain/identity/import regressions | PASS | `.venv/bin/python -m pytest -q tests/test_paper_workbench_model.py tests/test_structure_inspection.py tests/test_paper_pdf_candidates.py tests/test_import_review.py` — **19 passed in 7.02s**. |
| Real RDKit descriptor/stereo/fragment check | PASS within focused tests | Bundled JS inspection compared with Python RDKit for explicit stereoisomers, salts/fragments, isotopes, charged structures and invalid/unknown cases. This verifies graph representation, not agreement with a paper. |
| Checked-state staleness / dependency invalidation / strict projection | PASS within focused tests and source review | Meaningful edits invalidate chemical/solution/reaction confirmations; exact checked SMILES inspected at UI export; unchecked rows excluded. IDs are DOI/label scoped; existing imported draft IDs remain stable. |
| Existing blank-structure enrichment and local-edit/backup regressions | PASS within focused tests | Exact original private bytes backed up for reviewed structure/label additions; collisions and several backup/primary storage failures reject replacement. Does not cover QA-PW-01's missing stage/solution facts. |
| Independent missing-stage and quantity transfer probes | **FAIL** | Both concrete reproductions above succeeded in demonstrating information loss. |
| Private PDF / sketcher / packaging source inspection | Reviewed; no additional confirmed finding | PDF bytes are selected into memory; private page text/candidates excluded by compact projection; document re-selection uses SHA-256 pairing; sketcher says manual source encoding, rejects unresolved/query/enhanced stereo features it cannot preserve. Embedded PDF worker/RDKit assets and safe HTML module embedding reviewed. Source inspection alone is not browser runtime proof. |
| New exact-source complete CI, actual offline file transfer and both HTML hashes | NOT RUN by this role at report time | Root was still running/finalizing exact-source local and CI evidence. I did not rebuild shared artifacts, fetch changing CI refs, test blocked managed `file://`, or substitute local HTTP for file evidence. These cannot turn a source with QA-PW-01 into an approved delivery. |

## Boundaries and handoff

The implemented workflow is source-assisted manual curation with private PDF viewing, not automatic exact chemical image recognition. A successful SMILES parser cannot certify scientific source identity or stereochemical correctness. I did not assert complete extraction of the user's three real papers, inspect their private original content as published data, or approve a public website, history cleanup, user-PC scheduler or Box sync.

Development must fix QA-PW-01 after Revision → Wiki → Planning records this round. A source change requires a new full SHA, all affected checks, both exact-source artifact manifests and actual offline two-program transfer evidence, followed by fresh Independent QA and Revision. This report remains the original rejection of `8cbd5fe2fa92da03169922e1cc7a43bb59b0a89d`.

## Post-cutoff CI evidence supplement

The original report and its one material source finding above are preserved. After that report's cutoff, root supplied actual CI run **39204595894**, terminal immutable receipt **`546a9afe693f52c5165d76651748dd0984c56924`**, for the same exact source `8cbd5fe2fa92da03169922e1cc7a43bb59b0a89d`. I read the four raw files in `round-01/web/` and independently verified every file's byte length/SHA-256 against `receipt-files.json` **and byte-for-byte equality with its corresponding `git show <receipt>:<filename>` object**. No moving-ref fetch or source/artifact rebuild was performed.

- `web-tests.log`: **316 passed, 1 skipped**, with one dependency deprecation warning. This is CI-provided full-suite evidence, distinct from the 19 tests I executed directly.
- `web-build.log` and terminal step facts: browser app build **PASS**.
- `web-browser.log`: hosted browser **FAIL**. The complete traceback identifies `scripts/synthesis_map_smoke.py:59`: `Selected reaction details` inspector is absent after the coupling node header drag followed by focus and Enter. The immediate failing assertion is preserved; its underlying cause remains **UNRESOLVED**. It is not QA-PW-01 and is not attributed to any older historical CI failure.
- Terminal facts: portable main build/check, Paper Workbench build/check, actual `file://` two-program transfer, and artifact upload were **SKIPPED** after the hosted-browser failure. There is no new CI download artifact or pair of approved HTML manifests from this run.
- Pages publication was **NOT ATTEMPTED / skipped** in this run. Prior Pages403 is historical context, not the observed cause of this run's build failure.

Decision remains **CHANGES_REQUESTED**, one confirmed source finding QA-PW-01 plus the additional required hosted-browser failure and missing downstream evidence. The next plan must diagnose the hosted interaction separately, preserve the current complete failure log, and require fresh same-source hosted/offline checks and both actual HTML identities before any delivery approval.
