# Revision — 20261017-web-03 / round-02

- Role: separate GPT Revision; no application, test, CI, publishing configuration or source-history edits.
- Reviewed source: `d423c718ca3c0b7d1dd090a362ba02990d7e223a` on `codex/gpt-agent-workflow`.
- Inputs: [Planning](planning.md), [Development](development.md), the three detailed Development handoffs, final [Independent QA](qa.md), original source and exact-source CI evidence.
- Final verdict: **CHANGES REQUESTED — 1 new unresolved code finding**. All four round-01 findings are resolved.
- Hosting: **BLOCKED_EXTERNAL_PAGES_CONFIGURATION**. No final code approval or verified accessible preview is granted.

## Four prior repairs independently verified

| Prior finding | Revision decision and evidence |
| --- | --- |
| WEB-REV-01: malformed advanced JSON crashes the app | **RESOLVED.** Revision independently reran the original Chromium crash and null/array-root/invalid-alias variants. The shell, exact raw draft and correction controls remained visible, rejected saves left storage byte-identical, correction/save/reload succeeded, and no page error occurred. Save-time schema validation is retained. |
| WEB-REV-02: exported/importable contracts disagree | **RESOLVED.** Inspected strict required fields, explicit scientific nulls, Unicode/numeric bounds and normalization. Independently executed the common 195-case actual Python-export/Node-browser corpus and failure-preservation coverage; previous missing concentration/unit/array cases now reject consistently instead of emitting unusable output. |
| WEB-REV-03: capped eligible PDFs are lost outside the date window | **RESOLVED.** Independently executed the queue regressions: durable 10+1 continuation, later-date refresh, changed/expired OA decision, failures/attempt bounds, existing-file/review retry and saturated queue. The public-only durable state path survives cache loss without exporting PDF/review bodies. Bibliography progress and pending download work are distinct; the new finding below concerns durability of the bibliography output itself. |
| WEB-REV-04: built data B is reported as trigger A | **RESOLVED.** Revision independently exercised a real temporary Git A→data-B fixture: workflow A and built B remain distinct, the exact library digest matches, preserved identity survives a fresh-job resolution, and stale marker/changed body bytes are rejected. Inspected explicit build outputs through publish/terminal jobs. |

Revision's focused execution of portable-contract, queue, durable-state and provenance tests returned **25 passed in 2.02 seconds**. Complementary browser and real-Git scenarios reported `REVISION_EDITOR_RECOVERY_PASS` and `REVISION_CODE_DATA_IDENTITY_PASS`. These are local controlled checks, not live deployment or publisher success.

## New WEB-REV-05 / WEB-QA-05 — MEDIUM: metadata progress advances before its bibliography is durable

**Confirmed independently in two runtime reproductions; QA separately confirmed the completed-window case.** `paper_pipeline.__main__.weekly` writes metadata page cursors and `last_success` during discovery, before its final `write_json(out, validate(data))`. A subsequent output error correctly preserves the old package but leaves progress pointing beyond records that package never received.

### Completed-window reproduction

- Fixture: an ordinary bibliography-only JACS article published October 4; no eligible OA work or PDF pending entry. First clock: October 17. A valid prior normalized output exists.
- Inject `OSError` only at the final output-path write, leaving production state writes enabled.
- Actual: old output bytes stay unchanged, but `jacs/state.json.last_success` is already `2026-10-17T00:00:00+00:00`.
- Restore successful writing and advance the clock to October 24. Discovery now starts October 10, returns no items and reports no failures; the previously discovered DOI remains absent from the exported package.

```json
{"first_output_write":"OSError",
 "checkpoint_advanced_before_output":"2026-10-17T00:00:00+00:00",
 "second_window":"2026-10-10",
 "recovery_failures":[],"known_paper_permanently_absent":true}
```

### Capped-page cursor reproduction

- Fixture: 101 bibliography-only items, with 100 on the first page and `next-cursor: second`; run with `max_pages=1`.
- Inject the same final output error. The first 100 records are not exported, but the saved resume cursor is already `second`.
- Retry with successful output writing. The actual requested cursors were `["*", "second"]`; only item 101 was exported. All first-page records remained absent.

This is one ordering defect affecting **all metadata-progress advancement**, not merely `last_success`. Bibliography-only records have no PDF queue to rescue them. Preserving an old output file is necessary but does not make the new discovered records recoverable.

### The same boundary in CI

Independent workflow inspection confirms a second persistence boundary: `.github/workflows/web-library.yml` currently saves `build/paper-state` **before** committing/pushing `public/library.json`. Cancellation or a failed normalized-feed push can therefore leave a remotely durable checkpoint beyond the durable feed. This is a code-path analysis, not a claim that a live push failure was observed in this run; collection was skipped in this CI invocation.

## Bounded round-03 repair contract

Return this one finding through Wiki → Planning, preserving all four completed repairs:

1. Do not durably advance **any** metadata resume cursor or completed-window checkpoint until the corresponding normalized bibliography is durably written, or persist a replayable durable bibliography before advancing. Defer all affected state writes, not only `last_success`. Pending PDF work remains independent and retains its safety/retry rules.
2. On an output validation/write failure, preserve the previous package and prior metadata progress so retry can rediscover every uncommitted DOI. If writing state fails **after** successful output publication, replaying an older cursor must be idempotent and safe.
3. In CI, persist public progress to `build/paper-state` only after the corresponding normalized feed commit/push succeeds, or use an equally safe durable metadata replay contract. A local output file alone is insufficient on an evictable runner. Preserve prior remote state on failed feed publication; do not discard pending work or treat best-effort cache as the sole durable recovery mechanism.
4. Meaningful regressions must cover final-window and capped multi-page output failures, later-date and immediate retries, post-output state-write failure, and the CI/durable-state feed-publication boundary. Assert every discovered DOI is eventually present exactly once, original reactions/user fields remain unchanged and no checkpoint can outrun durable output.

No additional publisher/authentication scope, schema redesign or UI redesign is needed. Freeze a corrected full SHA and rerun affected tests, exact-source web CI and both independent reviews; current green tests do not cover or resolve the new reproductions.

## Exact-source CI: positive checks and separate hosting block

Revision read [web/status.json](web/status.json) and [web/manifest.json](web/manifest.json), recomputed all six retained file hashes/byte counts and compared their bytes against immutable receipt commit **`4fb229121ebd4597c51bae7dec30cf37dc759d61`**. The check reported `REVISION_EXACT_CI_EVIDENCE_BYTES_PASS`.

- Source: `d423c718ca3c0b7d1dd090a362ba02990d7e223a`.
- Run: <https://github.com/chemryu/chembrain/actions/runs/39063636131>.
- Tests: **253 passed, 1 Windows-only DPAPI skipped**; production browser build and real Chromium checks **PASS**.
- Terminal identity retains workflow/built SHA `d423c718…` and library SHA-256 `25e98df9810b686e9da2c3c3b3f7f5da627dd2186ab3b00533b28d34072aef8c`.
- New, actually observed Pages configuration result: **HTTP 403**, `Resource not accessible by integration`.
- Deployment and public HTTPS verification: **SKIPPED / NOT RUN**; `page_url: null`, terminal status `blocked`.

The prior source's Pages result was not assumed. This current evidence establishes successful build checks and an external hosting blocker, not an accessible preview. Owner configuration remains separate from code repair; no permission change, main merge or guessed URL can substitute for actual successful deployment and identity/digest HTTP verification.

## Wiki handoff and remaining milestone limits

Wiki should preserve this complete report and QA's final corrected report, record **4 prior findings resolved / 1 new unresolved ordering finding / CHANGES REQUESTED / external Pages 403 / no approved deliverable**, and return the bounded contract above to Planning for `round-03`. Preliminary local zero-finding messages are superseded by the independently reproduced defect and these final reports; do not retain them as approval.

The dispatcher remains a fail-closed, unconfigured review artifact outside active workflows. Its static review/default guard does not mean it is installed, scheduled or live-dispatch tested. Weekly operational delivery still requires an authorized configured and exercised route. The 12 factual starter drafts are unchanged; their prior factual checks are reused honestly, not presented as new full extraction/structure/SI validation.

No user-PC task, Box synchronization, institutional login, complete OA coverage, cross-device account sync or autonomous background GPT service has been performed or claimed. Browser edits remain local with JSON backups. Application source and build inputs remained unchanged from the frozen SHA throughout this review; only this Revision report is written by this role.
