# Independent QA — 20261017-gpt-02 / round-02

- Role: separate GPT Independent QA; no application, test, workflow or source-history edits.
- Frozen source: `c96c210a89a077869da78e7e570f06c80768cc16` on `codex/gpt-agent-workflow`.
- Final round verdict: **BLOCKED_REQUIRED_WINDOWS_EVIDENCE**. **0 unresolved application-code findings**, but mandatory Windows evidence is unavailable. There is no final QA approval or delivery authorization.
- Previous source `36fde22d2791475062565161bf986b88f035b2da` remains rejected. Its eventual tests/artifact cannot approve this source.
- No institutional authentication, subscription retrieval or personal model API calls were used during QA.

## Prior findings independently rechecked

| Finding | Resolution | Independent evidence |
| --- | --- | --- |
| QA-01 — wrong-paper/non-PDF redirects | RESOLVED | A frozen expected DOI/content-version policy is passed into the production opener and redirect handler. Direct calls with public DNS mocked rejected the prior wrong-DOI PDF, `/action/showLogin` and SI-route cases; a canonical same-DOI `/doi/epdf/…` URL with DOI case variation was allowed. The focused/full suite also exercises actual urllib redirect transport and multiple hops, including rejection before issuing a forbidden outgoing request. Metadata transport retains a separate policy. |
| QA-02 — omitted OA/type evidence | RESOLVED | An independent collection fixture with an AM license starting `2020-02-03T04:05:06-06:00` and ending in 2099 persisted start `2020-02-03T10:05:06+00:00`, exact end, matching `am`, supplied PDF URL, recognized CC URL and `journal-article` type. Collector-owned article metadata also retained type while existing user source dictionaries stayed exactly unchanged. The immutable `LicensedPDF` candidate carries this selected decision through download/install. |
| QA-03 — no PDF page ceiling | RESOLVED | An independently generated 400-page PDF was saved. A 401-page PDF raised `PDFPageLimitError` before installation; previous attachment bytes and complete metadata were identical afterward and no `.download-*` file remained. Fresh-store collection of the 401-page fixture retained its DOI reference, recorded a specific 400-page limit failure and installed no attachment. |
| QA-04 — duplicate ambiguity hidden | RESOLVED | Independent fixtures with two main sources using case/prefix DOI variants and an ordinary SI produced exactly one nonfatal structured notice, both retained main IDs, deterministic selected ID and a successful checkpoint. Repeat collection retained the notice, reused the verified PDF without another download and preserved all source/user/evidence records. SI was not misreported as a duplicate main match. Real Chromium verified notice visibility separately from actual errors. |

## Direct local execution

| Command/check | Result |
| --- | --- |
| `.venv/bin/python -m pytest -q` | **PASS: 227 passed, 1 skipped**, 6.16 seconds. The skip is Windows-only DPAPI; existing Starlette/httpx deprecation warning only. |
| `npm run build` | **PASS**: TypeScript and production Vite build, 1,726 modules. |
| `.venv/bin/python scripts/browser_smoke.py` | **PASS** after production assets were fully built. Actual Chromium: one reaction reference per paper with all main/SI provenance; collection controls/status and visible duplicate notices; older stored run compatibility; English interface, DOI removal guard, molecule/reaction create/edit, conditions, routes/drafts, text-free Markdown export, reload/mobile and no JavaScript errors. |
| `.venv/bin/python scripts/check_desktop_launch.py .venv/bin/python scripts/desktop.py --no-browser` | **PASS**: two real source processes, same isolated default data directory, full workspace and user corrections unchanged after restart. This command intentionally skips browser launch and is not Windows binary evidence. |
| `.venv/bin/python scripts/desktop.py --smoke-test` | **PASS**, including `JACS_COLLECTOR_FIXTURE_PASS` and the ordinary English/RDKit/DOI app smoke. Isolated temporary data; no publisher requests. |
| Independent repair reproductions beyond the committed tests | **PASS**, as detailed above; original sources, user notes, source page counts, long printed/SI citation evidence, existing attachment bytes and repeated import results preserved. |

The first browser attempt overlapped the production rebuild and could not load its heading; rerunning after the completed build passed without changing a check or application source. An initial scratch scenario compared workspace timestamps after explicitly resaving a reaction; the valid save updates its timestamp. The corrected independent preservation scenario made no such intervening write and passed. Neither verification-setup issue was treated as an application finding or hidden as a passing first attempt.

## Windows and live-provider gates

**BLOCKED / NOT VERIFIED**: final receipt, packaged tests/fixture, zero-argument EXE startup, rendered packaged UI, true restart, restricted runtime PATH, actual temporary scheduler registration/inspection/removal, artifact checksum and public-provider observation for exact source `c96c210a89a077869da78e7e570f06c80768cc16`.

Root captured the actual available evidence in [windows-pending/last-observed-status.json](windows-pending/last-observed-status.json) and [windows-pending/observation.json](windows-pending/observation.json). At `2026-10-17T07:35:21.810849Z`, the latest immutable receipt was still Git commit `65a2dcf538f6ce8ef11fce32ee9615a6c38ad35f`, published at `2026-10-17T07:04:12Z`. It identifies this exact source and run <https://github.com/chemryu/chembrain/actions/runs/39011910077>, but contains only `status: running`, empty stage results and a null artifact URL. It has not supplied final logs or a checksum.

More than the workflow's configured 30-minute job budget elapsed after that published start receipt without a newer observable result. **The actual current job state is UNKNOWN**. This observation does not prove that the job timed out, failed, stopped or is still running. The cloud's GitHub Actions API requests remain Forbidden, including Root's post-environment-reconnect retry, so the stale start receipt cannot be reconciled with an authoritative live Actions state here.

No required Windows check is recorded as PASS from that receipt. Passing local checks do not replace packaged/scheduler evidence, and no artifact is approved or delivered. A receipt for `36fde22d…`, `3f102821…` or another SHA is not acceptable.

The cloud's previously observed public metadata connectivity was **UNAVAILABLE**, according to Development. These deterministic fixtures are not a live provider or live OA-PDF success. Windows gateway observation must retain its actual outcome, including refusal or unavailable service. No live publisher PDF was downloaded by QA in this round.

## Manual limits retained

- Clean Windows VM: **NOT RUN**. Restricted runtime PATH, when verified, is narrower evidence.
- Actual user default-browser integration: **NOT RUN**. CI probes browser intent and renders UI separately.
- User-PC collection/schedule installation, Box local writes or synchronization: **NOT RUN**.
- No release, deployment, permission change, institutional login or perpetual GPT background process is claimed or authorized.

## Concrete next-round handoff

The four application repairs remain independently resolved. The new blocker returns through **Revision → Wiki → Planning** for round-03: repair CI evidence observability without changing the collector's scope or weakening any gate.

Recommended bounded work:

1. Persist source/run-bound timestamps and before/after status around dependency installation, frontend/API checks, packaging, packaged smoke/collector fixture, ordinary launch/UI/restart/PATH, temporary scheduler check, gateway observation and artifact upload. Preserve useful bounded diagnostic logs at checkpoints; avoid exposing credentials or environments.
2. Add a timeout/cancellation-safe final evidence path independent of a final step inside the potentially interrupted build job. It should distinguish authoritative terminal results from missing/unavailable observations; it must not invent a timeout or success from elapsed time alone.
3. Keep every required Windows test, actual safe temporary-task registration/removal, OA-only observation semantics, exact source SHA and artifact checksum gate. Do not substitute the old EXE or lower approval criteria merely because the current result is inaccessible.
4. Freeze any changed workflow/reporting inputs as a new full SHA and rerun the required exact-source Windows evidence and separate Independent QA/Revision decisions. Preserve this blocked round as history. If an actual late final receipt for the present SHA appears before new source changes, inspect it explicitly rather than treating this stale receipt as final.

The user-PC task, API permissions and application source are not changed by this QA report. Delivery remains blocked until complete, truthful same-source evidence and both independent approvals exist.
