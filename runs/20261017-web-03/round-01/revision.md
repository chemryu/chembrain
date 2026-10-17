# Revision — 20261017-web-03 / round-01

- Role: existing separate GPT Revision, resumed normally after the documented usage-reset time. No model/account switching, personal model API or source edits.
- Reviewed source: `e424b34653fb96b911f5ee5708286c92baddfe5f` on `codex/gpt-agent-workflow`.
- Inputs: [Planning](planning.md), [Development](development.md), final [Independent QA](qa.md), implementation and original CI evidence in [web/](web/).
- Final verdict: **CHANGES REQUESTED — 4 unresolved findings**, plus an external Pages publication blocker.
- Delivery approval: **NO**. No publicly accessible preview has been verified.

## Current scope

The latest request replaces waiting for Windows delivery with an explicitly labeled GitHub Pages preview and browser-local storage. The main view is molecule-first, with no automatically populated reaction/category view. Weekly bibliography/OA archiving and paper-information review remain in a separate Python processor; only compact normalized papers, chemicals, stage solutions and curated reactions enter the browser package. Missing science remains unknown and all 12 starter reactions are drafts. The previous desktop approval and blocked Windows rounds are historical, not approval of this source.

The source-time quota statements are preserved preparation history. The existing independent agents have now actually resumed and reviewed this source; their present results are this report and QA's final report. A future documentation update should state the current outcome without rewriting the old frozen snapshot as though it had been approved then.

## Findings and Revision judgment

### WEB-REV-01 / WEB-QA-01 — MEDIUM: valid JSON with an invalid shape unmounts the application

**Confirmed independently in real Chromium.** Open Paclitaxel → **Edit molecule** → **Advanced normalized JSON** and change `aliases` to `null` in otherwise valid JSON. Before clicking Save, `RecordFields` calls `.join()` on the unvalidated value. Revision observed:

```text
PAGE_ERRORS ["Cannot read properties of null (reading 'join')"]
REMAINING_WEB_SHELLS 0
```

`JSON.parse` succeeding is insufficient before rendering authors/aliases/steps/solutes with `.join()`/`.map()`. QA separately reproduced the same failure. Existing browser data was not saved by this reproduction, but the blank screen prevents correction or cancellation until reload.

**Repair contract:** retain malformed draft text and present a useful validation message while keeping the app/editor usable. Validate required shapes before structured-field rendering, use safe handling of incomplete drafts and/or an appropriate error boundary. Do not silently coerce and save an invalid record. Add actual browser cases for syntactically valid malformed arrays/objects across editor kinds, with correction/cancel and stored-data preservation.

### WEB-REV-02 / WEB-QA-02 — MEDIUM: the processor and browser disagree about the portable v1 contract

**Confirmed independently through the actual normalization path and Node browser validator.** Revision deleted `solutions[0].concentration` from the valid starter, ran `paper_pipeline.schema.normalize`, and passed its accepted output to `src/libraryData.ts:validateLibrary`. The processor accepted and retained the missing field; the browser rejected it:

```text
PROCESSOR_NORMALIZE_ACCEPTED_MISSING_CONCENTRATION
BROWSER_REJECTED: A solution references an unknown chemical or invalid amount.
```

Python also checks some missing nested fields through defaults without emitting those defaults. QA separately found missing journal/steps/targets accepted by Python validation but rejected by the browser. The normalization/export path must not emit a supposedly valid package the main program cannot import.

**Repair contract:** define required fields and canonical optional defaults once as an explicit portable contract, then align both implementations. Missing genuine scientific values can become documented `null`/empty defaults; required identity/shape errors should reject consistently. Do not invent conditions or overwrite current browser data on failed import. Add cross-language parity cases covering absent fields, nulls, nested shapes and successful processor-export → browser-import behavior.

### WEB-REV-03 / WEB-QA-03 — MEDIUM: a PDF bound discards already-known eligible work

**QA finding accepted; source path independently inspected.** In `paper_pipeline.__main__.weekly`, `candidate and pdfs < 10` silently skips the eleventh eligible candidate. Metadata completion can nevertheless advance `last_success` without a failure or durable pending record.

QA's controlled two-date fixture discovered 11 supported, explicitly licensed articles dated October 4. At the October 17 run, 10 PDFs were saved and completion/checkpoint advanced with no failures. At October 24, the new publication window began October 10, leaving the known eleventh PDF outside discovery and never retried. This is loss of already-discovered eligible work due to the controller's own cap, distinct from unknown OA evidence or denied downloads. Revision did not label this fixture a live publisher observation.

**Repair contract:** keep durable eligible download continuation/pending work across runs and expose deferred counts/outcomes. Metadata checkpoints and outstanding download work must remain distinct. Retry pending work even after its publication date leaves the discovery overlap, revalidate explicit OA eligibility, reuse verified attachments and preserve all network/byte/page limits. Do not broaden institutional access or publisher scope.

### WEB-REV-04 / WEB-QA-04 — MEDIUM: weekly collection can publish data from a different commit than its source marker

**QA finding confirmed by independent workflow/reporting inspection.** Scheduled or manual `collect=true` execution commits changed `public/library.json`, moving the build checkout from event SHA A to data commit B. The build then writes `version.json.commit` from unchanged `GITHUB_SHA` A, and the HTTP checker expects A. Publish/terminal jobs check out A again; `report_web_build.py` recomputes `built_commit` from that fresh checkout and replaces the intermediate B identity in the terminal record.

Thus the future collected-data build can report an exact-source HTTP pass while its normalized data came from B. The present push-only run skipped collection, so this finding does not falsely claim that its current input tree differed from `e424b346…`.

**Repair contract:** preserve distinct immutable triggering/workflow/code identity and actual built data commit/digest. Pass the latter from the build through deployment, HTTP verification and terminal records; fresh finalizer checkouts must not overwrite it. Add a controlled collected-data scenario whose build input changes after the event SHA, verifying accurate markers and rejection of a mismatched published library.

## Positive evidence and scientific limits

Independent QA reran **237 Python tests passed / 1 Windows-only skip**, production `build:web` and the real Chromium smoke. They verify supported molecule-first selection, stage solutions, unique paper references, ordinary edits/reload, rejected imports, retained local edits, backup, subpath assets, mobile layout and absence of backend API calls. Passing smoke does not exercise or resolve the malformed-editor failure above. Revision's complementary browser and processor/browser cases were executed without source edits.

QA's separate factual review checked all 12 starter reactions against the three supplied PDFs and identified no concrete factual mismatch. Revision also spot-checked original Holton, Charest and Baran pages; staged yields, missing values and source locators are presented as draft curation. This is not complete route extraction, stereochemical encoding, SI procedure verification or automatic reviewed chemistry. Complex numbered structures remain unencoded where not established. PDFs/review text remain outside the compact main package; source-backed target-diagram assets have separate provenance.

## Actual CI and external Pages blocker

Revision inspected the preserved terminal receipt for run <https://github.com/chemryu/chembrain/actions/runs/39062568338>, immutable receipt commit `0331192af8d03426f4a2c28a584eaf7f9d34bb1d`:

| Evidence for exact source `e424b34653fb96b911f5ee5708286c92baddfe5f` | Result |
| --- | --- |
| Build tests, production browser build and real-browser smoke | **PASS**, terminal build result `success`; 237 passed/1 skipped and browser marker retained |
| Pages configuration | **BLOCKED**, HTTP 403 `Resource not accessible by integration` |
| Deployment | **SKIPPED / NOT RUN** |
| Actual public HTTP/source marker | **SKIPPED / NOT RUN**; `page_url: null` |
| Weekly live collection in this push run | **SKIPPED / NOT RUN** |

The observed Pages problem is a repository/account integration permission/configuration blocker, not an automatic approval-review rejection and not fixed by green code tests. Owner configuration confirmation remains an external step coordinated by root. This review does not grant permissions or claim a public URL exists. The receipt's earlier `BLOCKED_USAGE_LIMIT; preview only` placeholder is not current independent approval and is not retroactively edited.

## Wiki → Planning handoff

Wiki should preserve this complete report and QA's complete report, record **CHANGES REQUESTED / 4 unresolved findings / external Pages 403 / no verified public deliverable**, and return the four repair contracts to Planning for a bounded `round-02`. Update current quota/status wording honestly while preserving the original frozen preparation snapshot and review history.

Development should preserve molecule-first behavior, browser-local data, scientific unknowns and evidence/locators while repairing the four paths. Freeze a new full SHA, rerun relevant parity/browser/weekly/provenance checks and both independent reviews, and inspect that source/data identity's actual Pages receipt and public HTTP response before claiming accessibility. Owner Pages configuration must be resolved through the authorized account path; do not automatically merge to main or activate a schedule as a workaround.

The optional weekly GitHub schedule remains inactive while its workflow exists only on the feature branch. No user-PC processor task, institutional login, live subscription download, full OA coverage, cross-device account synchronization, Box synchronization or autonomous background GPT service is claimed. Browser backups remain necessary to move edits between browsers/devices. Prior Windows checks and approvals do not substitute for this new web scope.
