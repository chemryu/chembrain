# Independent QA — 20261017-web-03 / round-02

- Frozen source: `d423c718ca3c0b7d1dd090a362ba02990d7e223a`, branch `codex/gpt-agent-workflow`.
- Role: separate Independent QA GPT; application, tests, CI, permissions and source history were not edited. No personal model API, alternate model/key, institutional login or publisher PDF requests were used.
- **Final code-review verdict: CHANGES REQUESTED; 1 new unresolved code finding.** All four previous findings are resolved on this exact source, but the output/checkpoint durability issue below prevents approval.
- **Hosted-preview verdict: BLOCKED_EXTERNAL_PAGES_CONFIGURATION.** Exact-source build/tests/browser checks pass, but Pages configuration returns HTTP 403; deployment/public HTTP verification did not run. This is not an approved accessible preview or completed weekly-service delivery.
- Scope: the four round-02 repairs and their related regressions, source/data provenance and the unconfigured dispatcher review artifact. Previous rejected sources and older Windows approvals are not approval evidence for this source.

## Independent resolution checks

### WEB-QA-01 — malformed editor drafts: RESOLVED

Reviewed the render-shape guard and its use both before structured field rendering and before save. In an independent Chromium scenario, the original `aliases: null` reproduction now retains the app shell, editor and exact raw JSON. An attempted save leaves browser storage exactly unchanged. Correcting the draft allows a normal save; reload retains the correction while returning to an empty initial reaction selection. There were no page errors or app unmounts.

Independently ran the full browser smoke after the production build finished. It additionally exercises 42 malformed chemical/paper/reaction/solution drafts, roots and nested rows, correction/cancel, unchanged persisted data on rejected drafts, and ordinary field editing. Malformed scientific/referential data is still rejected at save; safe draft rendering is not mistaken for acceptance of an invalid record.

### WEB-QA-02 — processor/browser portable contract: RESOLVED

Both runtimes now require the same table/row shapes and explicit scientific nulls rather than allowing absent required fields to escape export. Independently replayed the previous missing `paper.journal`, reaction `steps`/`targets` and solution `concentration`/`concentration_unit`/`solutes` cases: Python validation and normalization and Node/browser validation all reject them.

Independently executed the full suite containing the shared 195-case corpus through actual processor CLI exports and Node import/merge, including failure-output preservation, malformed nested objects, nullable scientific values, finite-number bounds, Unicode limits and forbidden document payloads. Chromium imported an actual Python-exported package successfully while preserving existing edited rows. Code inspection confirms failures occur before replacement of the previous output/browser data and normalization preserves source evidence/foreign keys without inventing conditions.

### WEB-QA-03 — durable deferred PDF work: RESOLVED

The private insertion-ordered DOI queue is independent of metadata-window completion, bounded in count/bytes and attempts, and reports pending/deferred/attempted/reused/saved states. Deferred old work refreshes its current public DOI/journal/license/link decision before a new download. Failed/revoked/unverified work remains explicit; failed review creation can reuse a verified local PDF without a duplicate fetch. Queue saturation retains the current metadata page for retry.

A separate read-only QA helper independently ran the focused processor/state suite (**18 passed**) and a stronger end-to-end local fixture:

```text
11 eligible → 10 saved + 1 durable pending
save public pending/checkpoint state into a local bare Git remote
delete the entire work/cache tree, including PDF/review files
restore public pending/checkpoint metadata only
one month later, publication discovery returns zero
refresh pending DOI; license changes from CC-BY to eligible CC-BY-SA
save/review the final PDF exactly once; repeat has zero attempts
```

The compact package retains all eleven bibliography records and the original twelve curated reactions. The persisted state excludes archives/review bodies/private source fields; the helper verified that extra top-level private source metadata is rejected. Source inspection and the passing regressions also cover expired/revoked licenses, wrong DOI, provider/download failures, bounded retries, local review recovery and saturation replay. No network PDF requests were made.

Completed private PDF/review bytes are still best-effort Actions cache contents, not a permanent Git document archive. The durable branch preserves pending work/checkpoints; a local persistent processor directory is required for long-term raw document storage. This documented boundary is not represented as permanent cloud PDF retention.

### WEB-QA-04 — code/data publication identity: RESOLVED

Reviewed immutable workflow SHA versus actual post-collection build commit and the exact library SHA-256 through capture, explicit build outputs, publish/terminal jobs and HTTP checking. Fresh checkouts cannot substitute event SHA for the captured built/data identity. Changes outside `public/library.json` are rejected as collection-only builds.

Independently executed the full suite's real-Git A→data-B scenario and actual terminal receipt script: A/B remain distinct across fresh checkout, marker and body digest bind to B, stale marker/wrong bytes are rejected, and unreviewed code changes cannot masquerade as a data-only update. This is a controlled local Git/HTTP-payload check, not live deployment.

The exact-source push CI below independently records the same source/build SHA and a library digest matching the actual local bytes. Scheduled collection was skipped in that push run; the real-Git fixture supplies A→B mutation coverage without activating a schedule.

## Direct local execution

### New WEB-QA-05 — MEDIUM: metadata progress can become durable before its bibliography output

- Location: `paper_pipeline/__main__.py`, the `statefile` resume/checkpoint writes during/after journal discovery versus the final `write_json(out, validate(data))`.
- Revision found this failure case late in review; Independent QA then reproduced it with a separate controlled two-date fixture. The final verdict above incorporates that result; the initial local provisional zero-finding assessment is not approval.
- Fixture: one JACS bibliography-only DOI published 2026-10-04, first-run clock 2026-10-17, prior valid output file. Inject `OSError` only when writing the final output file, leaving all actual state writes enabled.
- Actual: the original output is correctly unchanged, but `jacs/state.json` already contains `last_success: 2026-10-17T00:00:00+00:00`. Restore successful writing and advance the fixture clock to 2026-10-24: the collector starts 2026-10-10, finds zero articles, reports no failures/downloads complete, and the previously discovered DOI remains permanently absent from the package.
- Revision also independently reproduced the cursor variant: after reading the first 100 items of a 101-item result and persisting the next-page cursor, final output failure leaves that cursor durable; retry resumes with only item 101 and never exports the first 100. This is the same ordering defect, not a second unrelated finding.
- Expected: do not durably advance any publication-window completion or page cursor beyond bibliography durably committed to the normalized output or a recoverable durable bibliography record. Keep the pending OA queue independent and preserve the prior output. A safe sequence can commit output first and checkpoint afterward with idempotent replay, or persist recoverable bibliography before cursor advancement. Merely fixing `last_success` while leaving early cursor writes unchanged does not resolve the issue.
- Required regression: simulated output-write failure for both final-window and capped-cursor paths; recovery with the original data, a later publication window and a restored cache/durable-state route must retain every discovered bibliography DOI. Do not count a successful old-output preservation check alone as complete data durability.

| Check | Result |
| --- | --- |
| `.venv/bin/python -m pytest -q` | **PASS: 253 passed, 1 skipped**, 6.06 seconds. The skip is Windows-only DPAPI, outside this browser milestone; existing Starlette/httpx deprecation warning only. |
| `CHEMBRAIN_BASE=/chembrain/ npm run build:web` | **PASS**, TypeScript and production repository-subpath build. |
| `.venv/bin/python scripts/web_smoke.py` | **PASS**: molecule-first empty initial panel, relations/stage solutions, DOI references, ordinary editing/reload/import preservation, malformed-editor recovery, actual Python-export import, backup, mobile, subpath assets and no backend API calls. |
| Independent original-crash browser replay | **PASS**, exact raw-draft retention, storage unchanged on rejection, successful correction/reload, no page error/unmount. |
| Independent six prior contract reproducers | **PASS**, both validators and processor normalization reject missing required fields. |
| Independent queue/cache-loss helper | **PASS**, 18 focused tests and the month-later Git-state/cache-eviction scenario above. |
| Dispatcher artifact's default execution | **PASS, fail-closed**: extracted its actual Python guard and ran it with the shipped placeholder. It stops with `Scheduler artifact is unconfigured; no workflow dispatched` before any Git/network call; mocked calls would fail the check if reached. |
| Independent output-failure/next-week fixture | **FAIL**, unchanged prior output but advanced metadata checkpoint loses the discovered DOI; WEB-QA-05. |

`docs/weekly-dispatcher.yml` remains an artifact outside `.github/workflows`. Reviewed its fixed branch, exact-source guard, allowed data-only changes, bounded single dispatch, repository-token scope and nonrecursive trigger design. It is **not configured, installed, activated or live-dispatch tested**. Installing/exercising an authorized scheduler route is still a separate milestone; static/default-guard review is not weekly-operation verification.

The twelve factual draft examples, generator and public structure depictions are byte-unchanged from `e424b346…`, verified with Git. The prior round's actual uploaded-PDF fact checks therefore remain relevant factual evidence, explicitly reused rather than presented as a new complete OCR/OCSR/SI extraction. Missing structures and experimental values remain unknown/draft.

## Exact-source CI and deployment evidence

Independently inspected [web/manifest.json](web/manifest.json) and every retained raw file. Recomputed each SHA-256/byte count and compared all six files byte-for-byte against immutable receipt Git commit **`4fb229121ebd4597c51bae7dec30cf37dc759d61`**. Source/run binding matches:

- Source: `d423c718ca3c0b7d1dd090a362ba02990d7e223a`.
- Run: <https://github.com/chemryu/chembrain/actions/runs/39063636131>.
- Receipt: terminal, `status: blocked`, `page_url: null`.
- Build/tests/browser: **PASS**. [web-tests.log](web/web-tests.log): **253 passed, 1 skipped**; [web-build.log](web/web-build.log) and [web-browser.log](web/web-browser.log) pass.
- Build identity and terminal provenance retain both workflow/built commit `d423c718…` and library SHA-256 **`25e98df9810b686e9da2c3c3b3f7f5da627dd2186ab3b00533b28d34072aef8c`**. QA recomputed that hash from `public/library.json`; it matches.
- Pages configuration: **BLOCKED**, [pages-config.json](web/pages-config.json) and log show HTTP **403**, **`Resource not accessible by integration`**.
- Deployment and actual public HTTP verification: **SKIPPED / NOT RUN**. No accessible site or successful public response is inferred from the green build or artifact stage.

The prior source's hosting failure was not assumed: this is a new exact-source observation. The remaining gate requires an authorized owner/hosting configuration path. A code repair, dispatcher activation or main merge is not a substitute for that external access.

## Separate decisions and remaining scope

Return **WEB-QA-05** through Revision → Wiki → Planning for one bounded round-03 repair covering all metadata-progress/output ordering, including both completion and cursor writes. Preserve the four resolved contracts and existing deterministic checks; freeze a new source SHA and repeat the appropriate exact-source checks and independent decisions. The present source has no code approval. Keep this code finding separate from the external hosting blocker and inactive weekly scheduling.

No main/default-branch change, dispatcher activation, user-PC task, Box synchronization, institutional download, complete OA coverage or autonomous background GPT service is claimed. Browser storage remains local with JSON backups for moving devices. This source is ready for the independent Revision code decision, but it is not a verified accessible preview or a completed weekly collection service until the corresponding live gates pass.
