# Planning — 20261017-web-03 / round-02

- Status: READY FOR DEVELOPMENT; no source/delivery approval.
- Rejected source: `e424b34653fb96b911f5ee5708286c92baddfe5f`; corrected source SHA will be recorded only after freeze.
- Required order respected: final QA → Revision → Wiki handoff was saved and published at records commit `128c3fca84fbc222043c5aaaddcc126bcc62c172` before this plan.
- Inputs: complete round-01 [QA](../round-01/qa.md), [Revision](../round-01/revision.md), [handoff](../round-01/handoff.md), and post-implementation [scope audit](../round-01/planning-addendum.md).
- Scope: four bounded repairs plus truthful current-status documentation and a reviewable scheduler-bootstrap artifact. Preserve molecule-first empty initial reactions, browser-local edits, compact-only transfer, all evidence/locators, scientific unknowns and OA-only collection. No cosmetic redesign, institutional authentication, automatic chemistry approval, personal API key or broad main merge.

## Development assignments and repair contracts

### UI editor Development — WEB-QA-01 / WEB-REV-01

Primary paths: `src/RecordFields.tsx`, necessary editor handling in `src/MolecularLibrary.tsx`, actual-browser regression.

Treat valid JSON with an invalid shape as an unsaved malformed draft, not a renderable record. Guard root objects and arrays/nested rows before structured field rendering; retain the exact raw draft, useful validation message, app shell and correction/cancel controls. Do not silently coerce/save invalid shapes or overwrite browser storage. Cover chemical aliases, paper authors, reaction steps and solution solutes, including null/non-array roots and malformed nested members. Real Chromium must verify no page errors/unmount, unchanged stored data on rejected save/cancel, and successful correction/save afterward. Preserve normal structured editing and initial empty-selection behavior.

### Portable-contract Development — WEB-QA-02 / WEB-REV-02

Primary paths: `paper_pipeline/schema.py`, `src/libraryData.ts`, explicit shared contract documentation/fixtures and parity tests.

Specify required fields, scalar/array/object types, nullable scientific values and canonical defaults. Align validation/normalization on both runtimes: either consistently reject absent required fields or consistently emit documented null/empty defaults for genuinely optional values. Do not invent experimental conditions. Test missing journal, steps, targets, concentration, concentration unit, solute amount/unit and malformed nested shapes, booleans/nonfinite numbers where applicable. A successfully exported normalized package must pass browser validation and actual import; failed export/import must preserve the prior output/current browser data. Use a common mutation corpus exercised by Python and Node, not two self-confirming tests that assert incompatible behavior. Keep DOI/known-structure normalization, foreign-key remapping, local edit preservation and document-payload exclusions.

### Weekly-queue Development — WEB-QA-03 / WEB-REV-03

Primary paths: `paper_pipeline/__main__.py`, its bounded public gateway/service helpers only if needed, and fixture tests.

Persist known eligible pending PDF work before cap deferral/failure, independent of metadata publication-window checkpoints. Retry pending work even after its publication date leaves the overlap. Report pending/deferred/attempted/saved outcomes honestly; metadata completion does not imply completed downloads. Bound attempts/work per run, reuse verified files and avoid duplicate review outputs. A retry must revalidate current explicit OA license/version and matching DOI/PDF route, preferably from refreshed public metadata; do not trust a stale candidate whose license has expired/changed. Provider failure retains retryable pending work, while no-longer-supported/OA-unverified outcomes remain explicit and never trigger an unauthorized fetch. Preserve limits, private archive separation and already downloaded files.

Required fixture: 11 eligible articles at date A, cap saves 10 and durably reports 1 pending; date B after publication overlap still processes the final item. Add failure/retry and changed/expired license cases, idempotent repeated run and existing-file reuse. Keep metadata checkpoint/continuation semantics separate from pending download completion. If candidate generation fails after download, retain a recoverable processing stage rather than permanently skipping the known file on the next valid-attachment check.

### Root Development — WEB-QA-04 / WEB-REV-04, docs and dispatcher artifact

Primary paths: `.github/workflows/web-library.yml`, `scripts/report_web_build.py`, `scripts/check_published_web.py`, focused provenance tests and current README/request/role-status documentation.

Preserve distinct identities: immutable trigger/workflow/code source, actual post-collection build/data commit, and SHA-256 of the exact published compact library bytes. Pass build identity through explicit build-job outputs into publish, HTTP verification and terminal reporting. A fresh checkout in a later job must not replace it with event `GITHUB_SHA`. Published markers must describe the actual built tree/data and the HTTP checker must verify both expected identity and actual library digest. Retain event/code provenance instead of merely relabeling B as if it were A.

Use a controlled scenario with event/code A followed by normalized-data commit B: marker, deployment verifier and final receipt retain A/B/digest correctly; a different marker or library body must fail. Keep receipt source/run binding and actual stage outcomes. Do not infer deployment from build success or let observation placeholders claim independent approval.

Update current usage/status wording: the earlier capacity failure is history; existing QA/Revision resumed and returned four actual findings. Preserve original frozen planning/snapshots/reports, and state current candidate review status honestly. Document bibliography/candidate generation versus human-curated chemistry, feature-only inactive cron, unrun PC installer, browser-local persistence and lack of cross-device sync.

Prepare a concrete, narrowly scoped **one-file default-branch dispatcher artifact** for review, with fixed/guarded tested source target, Monday UTC schedule, bounded nonrecursive dispatch and repository-token permissions only. Do not install or activate it yet, merge the application, alter default-branch settings, or use it to bypass Pages 403. Activation comes only after corrected exact-source independent app checks, review of this dispatcher and an actual authorized configuration path. Record dispatcher/code/data provenance separately when eventually installed.

## External hosting state

Round-01 Pages configuration was HTTP 403 `Resource not accessible by integration`; deployment and actual public HTTP were SKIPPED/NOT RUN, URL null. Root awaits the owner-setting response asynchronously. Continue independent code repairs meanwhile. A new workflow, green tests, guessed URL or account-setting request is not a deployed preview. If the owner path remains blocked, record the exact external blocker; no main merge/scheduler activation is a substitute.

## Required verification and handoff

1. Run the four focused regressions, cross-runtime corpus and actual malformed-editor/corrected-import browser cases; then full Python suite, production subpath web build and full browser workflow/persistence/mobile checks.
2. Freeze one corrected full source SHA; Development records actual commands, changed paths, outcomes and known limits in `development.md`. Current docs must not invent that future SHA or claim reviews before they occur.
3. Independent QA and Revision separately replay the four repair contracts on the frozen SHA; Wiki preserves complete reports and returns remaining work to Planning. Existing green tests and factual spot checks do not approve new changes automatically.
4. Inspect exact-source Pages CI/build/browser and actual built-data/digest evidence. To claim an accessible preview, require real successful deployment plus public HTTPS verification against that code/data identity. If hosting is still blocked, code-review result and deployment blocker remain separate.
5. Deliver only the milestone actually verified: browser preview versus activated weekly operation are distinct. Weekly completion additionally requires a reviewed, installed and exercised scheduler route; human-reviewed chemical export remains explicit. No production release, Windows approval, user-PC installation, Box synchronization or autonomous GPT background service is claimed.

This plan authorizes Development's bounded repairs in this active task. It neither grants final approval nor authorizes bootstrap activation before its stated gates.
