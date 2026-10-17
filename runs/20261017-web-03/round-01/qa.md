# Independent QA — 20261017-web-03 / round-01

- Frozen source: `e424b34653fb96b911f5ee5708286c92baddfe5f`, branch `codex/gpt-agent-workflow`.
- Role: existing separate Independent QA GPT role, resumed normally after the stated reset. No model/key switch or personal model API was used. The earlier quota blocker is historical; this report is actual independent review.
- Verdict: **CHANGES REQUESTED — 4 unresolved findings**, plus an independent external Pages publication blocker. No final approval or verified public-site availability is claimed.
- Latest scope: GitHub Pages and browser-local normalized data, separate weekly paper processing, molecule-first view with an initially empty reaction panel. The user superseded the Windows-delivery objective; old Windows or older-source approvals do not apply to this web source.
- QA did not edit application, test or workflow source, commit/push, change hosting permissions, activate a schedule or download publisher PDFs.

## Findings

### WEB-QA-01 — MEDIUM: malformed advanced JSON crashes the entire editor/app before validation

- Location: `src/RecordFields.tsx:3–7`, reached from `src/MolecularLibrary.tsx` advanced JSON editing.
- Independent real-Chromium reproduction: load the standalone app, choose Paclitaxel, click **Edit molecule**, expand **Advanced normalized JSON**, and replace `aliases` with `null` in otherwise valid JSON. Do not click Save.
- Actual captured result:

```json
{"edited_field":"aliases:null",
 "page_errors":["Cannot read properties of null (reading 'join')"],
 "remaining_app_shells":0,"save_buttons":0}
```

- `JSON.parse` succeeds, then `.join()`/`.map()` calls assume unvalidated array/object shapes during render. Authors, steps and solutes have analogous unsafe assumptions. A draft edit should not unmount the whole app or prevent the user correcting/canceling it.
- Expected: render malformed drafts safely and retain the raw edit with a useful error; validate shapes before field rendering/saving or use safe field fallbacks and an editor error boundary. Do not silently save an invalid record or erase existing browser data. Add an actual browser regression for valid JSON with invalid record shapes, not only invalid JSON syntax.

### WEB-QA-02 — MEDIUM: processor-exported v1 packages can fail the browser's v1 contract

- Locations: `paper_pipeline/schema.py:validate/normalize`, compared with `src/libraryData.ts:validateLibrary`.
- Independent cross-runtime reproduction from the valid starter:

```text
delete papers[0].journal:   Python validate ACCEPTS; browser rejects required paper metadata
delete reactions[0].steps: Python validate ACCEPTS; browser rejects reaction solution/conditions
delete reactions[0].targets: Python validate ACCEPTS; browser rejects reaction participants
```

- Revision separately reproduced missing solution concentration/solute/unit fields passing the actual normalization/export path and failing browser import. Python treats absent fields as defaults for checking but does not emit those defaults, while the browser requires the resulting arrays/null fields. Missing journal is not rejected by Python either.
- Expected: one explicit portable contract. Reject missing required fields consistently, or emit documented canonical empty/null defaults for genuinely optional fields, without inventing scientific values. Every successfully exported valid package should be browser-importable. Add cross-language acceptance/rejection parity checks across required fields, nested shapes and null/missing cases; preserve current data on failed import/export.

### WEB-QA-03 — MEDIUM: the weekly PDF cap silently drops eligible work after checkpoint advancement

- Location: `paper_pipeline/__main__.py:84–105`.
- The processor tests `candidate and pdfs < 10`; later eligible candidates are silently skipped. A completed metadata page still advances `last_success` with no failure or pending work recorded.
- Independent controlled fixture, with no publisher requests:

```text
11 explicitly licensed eligible JACS articles published 2026-10-04
clock 2026-10-17: 11 bibliography items, 10 PDFs saved, complete=true, failures=[]
state: last_success=2026-10-17T00:00:00+00:00
clock 2026-10-24: next window starts 2026-10-10, zero matching articles, failures=[]
archive remains 10 PDFs; the known eligible eleventh article is never retried
```

- This differs from unsupported/unknown OA metadata or upstream denial: the processor already had a supported eligible candidate and discarded it because of its own bound. The bounded-discovery disclaimer does not provide a retry path or truthful pending count for that work.
- Expected: persist eligible pending PDF work/continuation across scheduled runs, report cap/deferred outcomes, and keep metadata checkpoint semantics separate from outstanding downloads. Reuse verified files, revalidate the OA evidence when retrying and retain the byte/page/network limits. Do not broaden authentication or publisher scope to fix this.

### WEB-QA-04 — MEDIUM: collected-data builds publish the trigger SHA as though it identified the built data

- Locations: `.github/workflows/web-library.yml:54–83`, `scripts/check_published_web.py`, `scripts/report_web_build.py`.
- In scheduled or `collect=true` execution, the workflow commits the updated `public/library.json`, moving checkout HEAD from trigger A to data commit B. It then builds that tree but writes `dist/version.json.commit` from immutable event `GITHUB_SHA` A. The public checker compares against A and can report an exact-source PASS although the library came from B.
- Intermediate build receipts record `built_commit: B`, but publish/terminal jobs freshly check out A and overwrite the final receipt's built-commit field with A. That loses the useful distinction from the final audited handoff. This follows directly from the workflow/runtime environment; QA did not activate a live schedule or mutate the remote branch to reproduce it.
- Expected: retain separate immutable workflow/code SHA and actual built data commit/digest, pass the built identity through jobs and HTTP verification, and prevent a fresh checkout in the finalizer from replacing it. The current push-only preview without collection is not affected by this particular mismatch. The future weekly/manual-collect feature is.

## Independent positive evidence

| Check | Result |
| --- | --- |
| `.venv/bin/python -m pytest -q` | **PASS: 237 passed, 1 Windows-only DPAPI skipped**, 4.64 seconds; existing Starlette/httpx deprecation warning only. |
| `CHEMBRAIN_BASE=/chembrain/ npm run build:web` | **PASS**, TypeScript and production browser build. Build completed before browser execution. |
| `.venv/bin/python scripts/web_smoke.py` | **PASS** for its supported scenarios: initially empty reaction panel, no default All reactions/Organic synthesis view, selected-molecule relations, stage solutions, unique paper reference, edit/reload/import preservation, backup, repository-subpath assets, mobile layout and no backend API calls. This does not cover the separate malformed-editor failure above. |
| Independent controlled malformed-editor browser scenario | **FAIL**, exact error and app-unmount evidence in WEB-QA-01. |
| Independent Python/Node contract comparison | **FAIL**, mismatched exported/importable shapes in WEB-QA-02. |
| Independent two-date weekly fixture | **FAIL**, known eligible capped work lost in WEB-QA-03. |
| Uploaded-paper factual QA by a separate read-only helper | **No concrete mismatch identified** across all 12 draft records and three papers, as detailed below. |

The factual helper checked the actual supplied Holton 1994, Charest 2005 and Kanda/Baran 2020 PDFs, including rendering Baran's Scheme 1. Titles, authors, year and target DOIs matched. Holton's 93% at 90% conversion, 95%, 80–85% range and 93% final-sequence yield were represented without an invented midpoint/single-step claim. Charest's 73/62/79/90% and two-operation yields, hydrochloride isolate and unspecified Pd support were retained correctly. Baran's 19→20→21→22 and 34+35→Taxol connections, 94/49/81/85% yields and caption conditions matched. The missing DMDO solvent was not invented from a different optimization entry. Unknown numbered-intermediate SMILES remain unencoded and drafts remain drafts. This is not atomic structure validation, complete route extraction or SI procedure verification.

The public package contains compact normalized metadata, not PDF text/binaries. The separate target-diagram crops have source provenance; small encoded structures use generated depictions. Existing imports preserve ordinary tested local edits; no account or cross-device sync is implied.

## Exact-source CI and public-hosting observation

Independently inspected immutable receipt Git commit `0331192af8d03426f4a2c28a584eaf7f9d34bb1d` from run <https://github.com/chemryu/chembrain/actions/runs/39062568338>. It matches source `e424b34653fb96b911f5ee5708286c92baddfe5f` and is terminal with `status: blocked`.

- Build tests, web build and browser checks: **PASS**. The preserved test log reports 237 passed/1 skipped, and browser log has `WEB_LIBRARY_BROWSER_PASS`.
- Pages configuration: **BLOCKED**, HTTP 403, `Resource not accessible by integration`, verified in the immutable `pages-config.log` and `pages-config.json`.
- Deployment and actual public HTTP check: **SKIPPED / NOT RUN**, not PASS. `page_url` is null. No accessible public preview is established by this evidence.
- Collection step: skipped in this push run; CI does not exercise the live weekly-collection marker case in WEB-QA-04.

Root preserves the original CI files in this round's `web/` evidence folder. The immutable receipt's `independent_qa: BLOCKED_USAGE_LIMIT; preview only` is its earlier placeholder, not the current review result. It is not edited retroactively into approval; this actual independent report supersedes that placeholder for review status.

The external Pages permission/account blocker needs an authorized owner configuration path; it is not resolved by code tests. A labelled preview was authorized, but no permission change, automatic main merge or default-branch change was performed by QA.

## Handoff and limits

Send the four findings through Revision → Wiki → Planning for a bounded repair round. Preserve the molecular-first UI, local browser data, all evidence/locators and scientific uncertainty. Freeze the corrected source, rerun relevant tests and both independent reviews, and verify the actual hosted source/data marker before claiming an accessible preview.

GitHub's weekly schedule is inactive while this workflow exists only on the feature branch. The optional PC scheduler was not installed/tested on the user's PC. No live publisher collection, institutional login, complete OA coverage, API-free autonomous background GPT service or Box synchronization is claimed. Browser-local edits still require JSON backups to move between browsers/devices.

There is no independently approved final deliverable for this source. Passing the existing regression suite does not resolve the four reproduced/inspected findings or the separate hosting blocker.
