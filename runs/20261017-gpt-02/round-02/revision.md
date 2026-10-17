# Revision — 20261017-gpt-02 / round-02

- Role: separate GPT Revision; no application, test, CI, packaging or source-history edits.
- Reviewed source: `c96c210a89a077869da78e7e570f06c80768cc16` on `codex/gpt-agent-workflow`.
- Inputs: [Planning](planning.md), [Development](development.md), final [Independent QA](qa.md), prior round's complete findings, source changes and controlled complementary runtime checks.
- Final verdict: **BLOCKED_REQUIRED_WINDOWS_EVIDENCE**.
- Unresolved application-code findings: **0**; the four prior application findings are resolved. Required Windows gates are **NOT VERIFIED**. Revision approval and delivery authorization: **NO**.

## Prior findings independently resolved

| Prior finding | Revision judgment | Independent basis |
| --- | --- | --- |
| REV-01 / QA-01: same-host wrong-paper/non-PDF redirects | **RESOLVED** | The immutable `LicensedPDF` candidate supplies an expected DOI and content version through `CrossrefClient.pdf()` into the production redirect policy. Revision executed a real urllib opener with a controlled HTTPS transport: a percent-encoded/case-varied same-DOI `/doi/epdf/…` first redirect was accepted, while a wrong-DOI second redirect raised before any outgoing request to that other article. Existing host, public-address, credentials/query and route protections remain. |
| REV-02 / QA-02: lost OA/type provenance | **RESOLVED** | Revision's independent AM-version fixture retained the supplied PDF URL, recognized license URL, normalized start `2020-01-02T12:30:00+00:00`, explicit expiry, `am` version and `journal-article` type. Collector-owned ARTICLES metadata retained type while original user dictionaries were unchanged. QA separately verified its own timestamp/version fixture and new-reference metadata. |
| REV-03 / QA-03: no PDF page bound | **RESOLVED** | Revision generated 400- and 401-page PDFs. The 400-page attachment was accepted; 401 pages raised `PDFPageLimitError` before replacement. Previous good bytes and complete attachment metadata were identical afterward, with no `.download-*` files. The documented 30 MB byte bound and parser/encryption checks remain. |
| REV-04 / QA-04: duplicate DOI ambiguity hidden | **RESOLVED** | Revision imported a DOI with two main candidates, one unspecified/other candidate and a separate SI. It received exactly one structured nonfatal notice containing three retained matching IDs and deterministic selected ID `a-main`; SI was excluded. The run succeeded, advanced its checkpoint and preserved every user/source record. Repeat collection retained the notice and reused the valid PDF without another download. |

These complementary checks ran against temporary fixture storage with generated PDF bytes and mocked transport/DNS, without publisher network requests, institutional credentials, personal model APIs or source edits. They reported `REVISION_IMMUTABLE_REDIRECT_POLICY_PASS` and `REVISION_PROVENANCE_PAGE_BOUND_DUPLICATE_REUSE_PASS`.

Revision also inspected the changed source, structured notice UI, continuation persistence, observation script and bundled smoke fixture. No further application finding was identified. At completion, current HEAD was the reviewed SHA and the application/test/build-input diff against it was empty.

## Local evidence and its limits

Independent QA reports **227 passed / 1 Windows-only skip**, production build PASS, real Chromium scenario PASS, two-process source restart PASS and source `--smoke-test` PASS including the offline collector fixture. Its complete report describes independently replayed repairs and preservation of source IDs, user fields, original uploads and long printed/SI citation locators. Revision's independent cases above agree with those results.

The Windows-only DPAPI skip is not a Linux pass. Source startup, a source CLI unit test and an offline collector fixture inside `--smoke-test` do not prove actual packaged `--sync-jacs` execution or Windows scheduler operation. No required Windows check is inferred from green local checks.

## Windows evidence blocker: known observations, unknown runner state

Revision inspected both retained raw records:

- [last-observed-status.json](windows-pending/last-observed-status.json): exact source `c96c210a89a077869da78e7e570f06c80768cc16`, `status: running`, `steps: {}`, `artifact_url: null`.
- [observation.json](windows-pending/observation.json): observed at `2026-10-17T07:35:21.810849Z`; latest receipt commit `65a2dcf538f6ce8ef11fce32ee9615a6c38ad35f` was published at `2026-10-17T07:04:12Z`; configured job budget 30 minutes; no final receipt available; GitHub Actions API remained Forbidden after the environment reconnect.

Run: <https://github.com/chemryu/chembrain/actions/runs/39011910077>.

More than the configured job budget elapsed after the published start receipt without a newer observable terminal result. **Actual current job state is UNKNOWN.** This does not establish that the job timed out, failed, stopped or is still running. The stale start receipt is not terminal evidence.

Required exact-source Windows package build/tests, bundled smoke/collector fixture, no-argument launch, packaged UI, true restart retention, restricted runtime PATH, actual temporary scheduler registration/inspection/removal, headless packaged CLI evidence and final artifact checksum are therefore **NOT VERIFIED**. There is no approved artifact URL or candidate ZIP hash for this source. No earlier source's receipt or artifact can fill that gap.

## Separate headless-CLI observation gap

Revision identified a concrete verification-path dependency in `scripts/observe_jacs_gateway.py`: the packaged `--sync-jacs` invocation occurs only after the initial live Crossref observation succeeds. An initial provider/network failure skips that invocation entirely. Its missing `packaged_cli` field must remain **NOT RUN**, rather than being inferred from an offline `--smoke-test` fixture.

Round-01 Planning requires meaningful headless packaged operation and round-02 preserves those gates. The next verification repair must exercise the packaged CLI independently of public-provider availability. A bounded invocation that honestly returns provider-unavailable JSON and a corresponding meaningful exit can verify that branch's failure behavior; a controlled packaged headless fixture can verify deterministic success. Neither should be labeled a successful live PDF download. This is a verification gap to repair without changing the application's OA-only scope.

## Wiki → Planning: round-03 infrastructure work

Wiki should preserve this complete report and QA's final report, record **0 unresolved application findings / BLOCKED_REQUIRED_WINDOWS_EVIDENCE / no approved deliverable**, then return the following bounded work to Planning:

1. Persist source/run-bound timestamps and before/after receipts around dependencies, frontend/API validation, EXE packaging, bundled smoke/collector fixture, ordinary launch/UI/restart/PATH, safe temporary scheduler check, headless CLI, gateway observation and artifact upload. Preserve bounded useful diagnostic logs without credentials, environment dumps or paper text.
2. Bound individual stages and make terminal evidence independent of a final step inside the potentially interrupted build job. Handle job failure/timeout/cancellation honestly; distinguish an authoritative terminal outcome from unavailable observation. Do not infer failure or success from elapsed time alone, suppress a failed check, or replace actual evidence with a heartbeat.
3. Make packaged headless `--sync-jacs` verification independent of the initial live metadata probe as described above. Keep deterministic checks, actual packaged process behavior and live provider observations distinct. Preserve all existing required Windows tests and current-user future-task registration/cleanup without running a collection task during scheduler testing.
4. Freeze changed workflow/reporting/check inputs as a new full SHA and rerun required checks and both independent reviews. Preserve the resolved four repairs and user data. If a late authoritative final receipt for the present source arrives before new source changes, inspect it explicitly; the current start receipt alone remains insufficient.

No application redesign, institutional authentication, new personal API key, release publication or user-PC permission change is needed to address this blocker. Do not deliver an old EXE, inherit a prior approval or lower the original gates to bypass the missing evidence.

## Honest manual and live limits

Cloud public metadata connectivity was previously observed **UNAVAILABLE**; Revision has no new live publisher/PDF success to report. Exact-source Windows gateway observations are unavailable with the other final evidence. Fixture success is not live service success.

Clean Windows VM, actual user default-browser integration, user-PC collection/schedule installation and Windows Box writes/synchronization remain **NOT RUN**. No subscription PDF retrieval, institutional login, public release, deployment or perpetual background GPT process was performed or approved. GitHub remains the shared records location.
