# Development — 20261017-gpt-02 / round-02

- Frozen source: `c96c210a89a077869da78e7e570f06c80768cc16`, pushed on `codex/gpt-agent-workflow`.
- Previous source `36fde22d2791475062565161bf986b88f035b2da` remains rejected. Round-01 reports and handoff were published at records commit `27ad901ccd0183f018d840d78259ebd4158bb728` before Planning began round-02.
- Implemented the four bounded repairs in [Planning](planning.md). Development is not final approval; exact-source Windows evidence and separate Independent QA/Revision remain required.

## Changes and reason

1. `server/jacs_collection.py`: immutable licensed candidate carries expected DOI, original supplied PDF URL, effective license start/optional end and matched content version. A shared policy validates the initial PDF URL and every actual urllib redirect hop against that DOI and approved ACS article-PDF routes, preserving HTTPS/public-DNS/origin/query/credential protections. Metadata transport remains separate. Wrong-paper, SI and unrelated routes cannot reach their outgoing request.
2. Attachment provenance retains license URL/start/end, content version, supplied URL, upstream type and existing checksum/page/download metadata. New source collection metadata and collector-owned ARTICLES metadata retain the upstream Crossref type, including when reusing an existing user-edited source without changing its fields. The live observation script uses the same structured candidate.
3. PDF bytes remain capped at 30 MB; parsed pages are now capped at 400 before staging/install or attachment metadata changes. Over-limit rejection preserves previous good attachment bytes, bibliography, reactions and original uploads. README and packaged instructions document the limits.
4. `server/store.py`: main/unspecified duplicate matches are selected deterministically and reported as structured nonfatal notices, preserving every record and keeping the existing two-value return contract. Notices persist across cursor continuation, do not block checkpoints and do not conflate an ordinary main/SI pair. `src/JacsCollection.tsx` shows DOI, retained IDs/count and selected ID separately from actual errors; older receipts without notices still render.
5. `scripts/desktop.py`: the existing isolated `--smoke-test` now also executes a bundled collector fixture, validates locally saved licensed-PDF provenance and repeats import to check idempotence. It makes no publisher requests and cannot affect user data. Existing app/UI smoke remains.
6. AGENTS/RULEBOOK/current request record the rejected round-01 and new Planning handoff; no role permissions, scope or pass criteria were relaxed. Grouped reaction-reference cards, scheduler and ordinary DOI-only app behavior remain.

## Actual local validation

- `.venv/bin/python -m pytest -q`: **227 passed, 1 skipped** (Windows-only DPAPI), one existing Starlette/httpx deprecation warning. An earlier intermediate run was 226/1; after the final notice-resume repair the entire suite was rerun to obtain 227/1.
- Focused collector suite from Development helper: **64 passed**. Includes actual production opener/redirect handler with fake HTTPS transport (same DOI allowed, different DOI/unrelated route/SI/private target/extra parameters rejected, second-hop revalidation); exact audit evidence; 400/401-page boundary; encrypted PDF; previous-file/evidence preservation; deterministic/repeated/concurrent duplicate handling and continuation notices.
- `npm run build`: **PASS**, Development UI helper.
- `.venv/bin/python scripts/browser_smoke.py`: **PASS**, real Chromium against final backend/UI, Development UI helper. Includes original app workflows, one card per paper with all main/SI locators and structured duplicate notices with enabled collection controls; legacy receipts render.
- `.venv/bin/python scripts/check_desktop_launch.py .venv/bin/python scripts/desktop.py --no-browser`: **PASS**, ordinary source startup and real second-process restart over the same temporary default data folder; user changes and all records identical.
- `.venv/bin/python scripts/desktop.py --smoke-test`: **PASS**, including `JACS_COLLECTOR_FIXTURE_PASS`; no network.
- `git diff --check`: **PASS** before freeze.

## Pending evidence and limits

The new source push triggers its own Windows build, packaged smoke/fixture, ordinary zero-argument launch, packaged browser UI, restart retention, restricted runtime PATH and real temporary scheduler registration/inspection/removal. Await exact-SHA results; no earlier candidate's approval or artifact is reused.

Cloud public Crossref connectivity previously observed **UNAVAILABLE** (network/DNS). No new live publisher success is claimed by these deterministic repairs. Windows retains a distinct public connectivity observation; UNAVAILABLE must remain visibly different from PASS. Clean Windows VM and actual user default browser remain NOT RUN. No user-PC schedule installation, Box write/synchronization, institutional authentication, subscription download or external personal AI API call occurred. No public release was published.
