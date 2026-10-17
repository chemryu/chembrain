# Independent QA — 20261017-gpt-02 / round-02

- Role: separate GPT Independent QA; no application, test, workflow or source-history edits.
- Frozen source: `c96c210a89a077869da78e7e570f06c80768cc16` on `codex/gpt-agent-workflow`.
- Local verdict: **0 unresolved findings; required exact-source Windows evidence pending**. This is not final approval or delivery authorization yet.
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

**PENDING** at this checkpoint: receipt, packaged tests/fixture, zero-argument EXE startup, rendered packaged UI, true restart, restricted runtime PATH, actual temporary scheduler registration/inspection/removal, artifact checksum and public-provider observation for exact source `c96c210a89a077869da78e7e570f06c80768cc16`.

Root has now observed that exact source's running receipt and run <https://github.com/chemryu/chembrain/actions/runs/39011910077>. A running job has not passed its gates; final logs/artifact remain pending.

Root coordinates shared receipt fetching/capture to avoid reference races. QA will independently inspect the copied immutable receipt/logs and update this report before a final decision. A receipt for `36fde22d…`, `3f102821…` or another SHA is not acceptable.

The cloud's previously observed public metadata connectivity was **UNAVAILABLE**, according to Development. These deterministic fixtures are not a live provider or live OA-PDF success. Windows gateway observation must retain its actual outcome, including refusal or unavailable service. No live publisher PDF was downloaded by QA in this round.

## Manual limits retained

- Clean Windows VM: **NOT RUN**. Restricted runtime PATH, when verified, is narrower evidence.
- Actual user default-browser integration: **NOT RUN**. CI probes browser intent and renders UI separately.
- User-PC collection/schedule installation, Box local writes or synchronization: **NOT RUN**.
- No release, deployment, permission change, institutional login or perpetual GPT background process is claimed or authorized.

No new code finding currently returns to Planning. The next step is exact-source Windows evidence, followed by the separate Revision decision and Wiki record; final handoff remains blocked until those gates complete.
