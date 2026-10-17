# Development — 20261017-gpt-02 / round-01

- Frozen source SHA: `36fde22d2791475062565161bf986b88f035b2da`
- Source branch: `codex/gpt-agent-workflow`
- Scope: JACS bibliography plus verified open-access PDFs only; one displayed reaction reference per DOI, retaining every main/SI locator. No institutional authentication or AI API keys.

## Implementation

- `server/jacs_collection.py`, `server/store.py`: public Crossref journal discovery, fixed publication-date windows, initial 14-day lookback and overlap/catch-up, bounded resumable pagination, atomic normalized-DOI reference registration shared with manual creation, user/source-ID preservation, process lock and persisted run status. PDF attachments are separate from source kind/page counts, so existing citations and original uploads remain unchanged. Only matching current recognized CC/public-domain licenses and trusted ACS PDF routes qualify; byte/parse/size/hash verification and atomic file installation follow. Missing/corrupt attachments can be repaired. Unknown metadata is not a paywall determination.
- `server/collection_schedule.py`, `scripts/desktop.py`: no-browser `--sync-jacs`, metadata-only inspection, bounded backfill; current-user weekly Windows task with a stable copied EXE, editable local weekday/time, missed-run recovery and no-overlap. No password, elevated task or task installation on the user's PC is performed in this cloud.
- `server/app.py`, `src/JacsCollection.tsx`: local status and manual collection, schedule registration/removal, completion refresh, English policy/status/error display. Schedule controls require the packaged Windows app. Existing DOI deletion protections remain.
- `src/references.ts`, `src/main.tsx`: canonical DOI presentation grouping and grouped counts; main/SI locations remain visible, editor/storage records remain separate. DOI-less sources group only by their actual source ID.
- `scripts/browser_smoke.py`, tests: existing workflow plus grouping/provenance, collection controls, completed-run refresh, status recovery and retained errors/drafts. Backend fixtures cover public gateways, licensed PDFs, pagination/retry/dedup/data preservation and process coordination.
- Windows CI now tests real temporary future task registration/inspection/removal with the bundled EXE. A separate public metadata/PDF connectivity observation reports unavailable services honestly; it does not turn network blockage into a test pass.

## Local checks

| Check | Result |
| --- | --- |
| `.venv/bin/python -m pytest -q` | 210 passed, 1 Windows-only DPAPI skipped; existing Starlette/httpx deprecation warning |
| `npm run build` | PASS |
| `.venv/bin/python scripts/browser_smoke.py` | PASS against final backend; actual Chromium, grouped references/all provenance, existing chemistry flows and fixture-driven collection controls |
| `.venv/bin/python scripts/check_desktop_launch.py .venv/bin/python scripts/desktop.py --no-browser` | PASS; ordinary source startup twice, entire user workspace preserved |
| Final focused collector suite | 47 passed, including supplied ACS PDF links with unspecified type under an explicit matching license |
| `git diff --check` | PASS before source commit |

UI and collector helpers operated within Development; Planning, Independent QA, Revision and Wiki remain separate roles. The UI helper installed pinned Playwright into the existing cloud venv; app dependency manifests were not changed.

## Pending evidence and limits

The cloud's direct public metadata observation returned `UNAVAILABLE` (network/DNS restriction); it is not live-download success. Windows CI will separately record public-provider observations where possible. No user-PC collection, campus session, user-PC task or live subscription download was performed. Open PDF coverage depends on supported explicit license/link metadata and provider responses. Late metadata beyond the overlapping publication window may require backfill. Clean Windows VM and actual default-browser integration remain manual coverage limits.

Exact-source Windows validation, Independent QA and Revision are pending at this implementation handoff. Prior source receipts or old artifacts are not evidence for this candidate. Final reports are recorded separately from the frozen source.
