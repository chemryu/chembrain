# Revision — Paper Workbench / round 01

- Role: separate Revision. Application, tests, data, build inputs and Git HEAD were not edited; this report is the only written file.
- Exact reviewed source: `8cbd5fe2fa92da03169922e1cc7a43bb59b0a89d`.
- Run: `20261019-paper-workbench-08 / round-01`.
- Decision: **CHANGES_REQUESTED**. **One unresolved material finding, QA-PW-01 (P1 / high).** The termination criteria are not met. Do not deliver this source or its artifacts as independently approved.

## Independent assessment of QA-PW-01

**Confirmed.** The finding affects the user's immediate requirement: source-checked chemical facts and their recorded synthesis/stage connections must survive transfer into the main library. Keeping local edits is necessary, but a generic success notice after silently omitting newly supplied facts is insufficient.

I read the current request, run Planning, Independent QA report, role/rulebook constraints, the current main import/review/apply UI, the strict normalized schema and `mergeLibrary`, the Workbench checked-state/export/import model, and the actual import regressions. In `src/importReview.ts:78` existing solutions are compared only by solvent IDs and the set of solute chemical IDs. In `src/importReview.ts:82` existing reactions are compared only by reactant/product/target sets. The saved-library merge at line 88 retains the whole old reaction and solution. Subsequent explicit enrichments cover only chemical structure fields and paper-label aliases. No branch compares or proposes reaction stages, solution links, conditions or quantities, and the completion notice reports that the import completed with existing edits retained.

I independently ran the actual TypeScript helpers through the read-only Node harness provided by `tests/test_import_review.py`, with three separate synthetic chemistry fixtures. No application/test source was changed.

1. **Empty stages and missing quantities.** Start with the saved fixture's reaction `steps=[]`; solution concentration/unit and solute amount/unit are all null. Incoming rows retain the IDs and participants, but supply one stage using that solution, `-78 °C`, `30 min`, `0.1 M`, and `1 mmol`. Actual: `conflicts=[]`, `changed=false`; `next` still has empty stages and null quantities. Calling `commitReviewedImport` performs zero storage writes. Thus the checked information is lost even without a competing non-null user value.
2. **Appended ordered stage/new solution.** Retain the existing first stage, add an incoming `new-stage-s` solution and append a second stage using it. Actual: `conflicts=[]`, `changed=true`, `added.solutions===1`; the resulting reaction still contains only its first stage, and no reaction references the newly added solution. The solution's presence alone does not transfer its recorded route connection.
3. **Different existing non-null values.** Change the incoming existing stage temperature/time, solution concentration, solute amount and reaction yield. Actual: no conflicts and `changed=false`; all local values remain. Preservation is correct, but the differences are not shown as retained/conflicting chemistry facts and the caller can still report ordinary completion. This shares the same planner/review omission and is not a separate finding.

The reported scope is accurate. New-ID reactions and their steps can transfer; this is specifically a same-ID existing-library correction/enrichment gap. Parser/source checks in Workbench cannot repair a receiving planner that discards the checked stage data. It is not solved by relabeling null compounds, changing the structure renderer, or blindly making incoming records win.

## Required Revision → Wiki → Planning handoff

Round 02 should address QA-PW-01 as one coherent receiving-contract change:

1. After the established identity remapping, review **existing reaction stage order and solution references**, stage temperature/time and relevant reported facts, and **existing solution concentration/unit plus each solute's role/amount/unit**. Include yield/evidence/other incoming chemistry differences in an explicit retained/conflicting-facts decision rather than silently suggesting they were imported.
2. Distinguish truly missing compatible facts from non-null local edits. For unambiguous missing fields/stages, show concrete proposed additions and require explicit application. For incompatible or ambiguous stage alignment/order, solution membership, roles or existing values, block or clearly present a retained/conflicting-facts review with a reliable reconciliation path. Preserve non-null user facts and private notes; do not infer stage order or overwrite a route wholesale merely because IDs/participants match.
3. A new solution intended as a recorded stage must either remain linked in the accepted reviewed result or cause a visible unresolved/rejected import. Do not accept an apparently complete package while severing its new stage link.
4. Validate the complete proposed library and references before any mutation. Any accepted enrichment of existing reaction/solution data must use the same explicit transaction guarantees as structure/label upgrades: compare the current primary bytes, save and verify a unique exact private backup first, recheck baseline, then perform one primary write. A failed backup, readback, concurrent change or primary write must leave the old primary and working UI intact.
5. Extend meaningful regressions beyond the passing structure-only cases: empty stages, compatible missing conditions/quantities, appended stages/new solution links, ordered-stage ambiguity/conflicting existing values, preservation of user edits, exact backup/failure paths, and idempotent repeated imports. Add an actual two-program browser transfer case that begins with saved existing IDs and confirms the received stage/solution facts and route links, including the downloadable `file://` programs.
6. Freeze and review a new full source SHA. Re-run affected/full required checks and obtain both same-source HTML manifests/hashes and actual offline transfer evidence before fresh Independent QA and Revision. Preserve this rejection verbatim; do not revise its source approval based on later fixes.

## Independently executed verification

| Check | Result | Scope and limitation |
| --- | --- | --- |
| Frozen source / role boundary | PASS | HEAD was checked before and after review/probes and remained `8cbd5fe2fa92da03169922e1cc7a43bb59b0a89d`; no shared build, app/test/data edit or Git fetch was performed. |
| Import and Workbench model regressions | PASS | `.venv/bin/python -m pytest -q tests/test_import_review.py tests/test_paper_workbench_model.py`: **14 passed in 4.45s**. Existing tests do not cover the reproduced missing-stage/quantity gap. |
| Three independent same-ID receiving probes | **FAIL** | All three reproduced the concrete information-loss/review omission above using the actual helper implementation. |
| Development's 11 local checks | Reported PASS; not counted as my independent execution | Root reported full Python **316 passed / 1 Windows-only DPAPI skip**, hosted/main portable and Paper Workbench HTTP end-to-end checks, builds and payload gates. Their green result does not negate QA-PW-01. |
| New exact-source CI actual-file two-program transfer and both artifact receipts | **NOT RUN / pending at review cutoff** | Root owns CI fetch/receipt capture; run `39204595894` was not terminal at this report's cutoff. I did not rebuild shared artifacts, fetch changing refs, bypass managed `file://` policy, or call HTTP evidence an actual-file pass. Later raw terminal evidence may be attached separately without changing this source rejection. |
| Final independently downloaded artifact ZIP/hash | NOT RUN | No new artifact is approved for delivery by this review. Earlier structure-release approval and hashes do not transfer. |

## Bounded interpretation and final status

The separate Workbench is source-assisted manual curation with a private local PDF viewer and structure encoding/checking. It is not automatic exact recognition of chemical drawings, and software acceptance of a SMILES graph is not independent scientific confirmation of a paper structure or its stereochemistry. This review does not claim complete extraction of the user's real papers, activation of journal downloads/scheduling, Box synchronization, a public website, history cleanup, or changes to permissions.

**No additional separately confirmed material finding. QA-PW-01 remains unresolved; source/artifact delivery approval is withheld.** Wiki must preserve the full QA and Revision reports, record the failing existing-ID handoff, and return the concrete work above to Planning for round 02. Even if the pending CI finishes successfully, this source still requires the application fix and new exact-source review.

## Supplement — terminal CI received after the original review cutoff

The original body above is preserved. Root subsequently captured terminal run **`39204595894`**, immutable receipt **`546a9afe693f52c5165d76651748dd0984c56924`**, for the same reviewed source. I read the four saved raw files in `round-01/web/` and independently verified each file's exact byte count and SHA-256 against `receipt-files.json`. I performed no Git fetch or rebuild.

- Python tests: **316 passed / 1 Windows-only DPAPI skip**; web build: PASS.
- Hosted browser: **FAIL**. The complete saved traceback reaches `scripts/synthesis_map_smoke.py:59`: the `Selected reaction details` region is absent after the test's drag/focus/Enter sequence. The saved accessibility snapshot still shows the synthesis graph and reaction buttons. The underlying cause is **UNRESOLVED**: these facts alone do not distinguish an application keyboard/focus defect from a test interaction/timing issue. This is a separate required-check blocker, not evidence of QA-PW-01, and it must not be attributed to the earlier historical CI whose diagnostic head was lost.
- Main portable build/check, Paper Workbench build/actual-file two-program transfer and artifact upload: **SKIPPED** after the hosted failure. Thus this run supplies **no new actual-file pass or downloadable artifact**.
- Pages/publish: SKIPPED / **NOT ATTEMPTED in this run**; the older Pages403 remains historical context, not this run's observed failure.

Round-02 Planning must additionally diagnose the current full CI failure and repair its actual cause while retaining meaningful keyboard activation and drag/map regressions. If it is a test race, synchronize on the real focus/layout state rather than removing Enter assertions or substituting pointer clicks. Re-run the required new exact-source CI through actual offline checks and both artifact receipts. The original **CHANGES_REQUESTED**, one confirmed material code finding and withheld delivery approval remain unchanged; this terminal CI adds a concrete failed required gate.
