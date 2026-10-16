# Development — 20261016-gpt-01 / round-01

- Source commit: `3f102821649ff13b5581ebdff18274ef46602322`
- Source branch: `codex/gpt-agent-workflow`
- Role: primary GPT agent, implementation and coordination; not independent approval.
- Changed behavior: a DOI-only reference or any source used by citation-only evidence cannot lose its DOI through metadata editing. The rejection happens before any persistence. Normal uploaded notes backed by original text keep an optional DOI.

## Changes

- `server/app.py`: guard empty/normalized-whitespace/omitted DOI for DOI-only and citation-linked sources, including draft reactions.
- `src/SourceMetadata.tsx`, `src/main.tsx`: matching required field and English explanation; browser input limits match server DOI length.
- `tests/test_desktop_references.py`: meaningful DOI loss regressions covering uploaded and DOI-only sources, draft/reviewed reactions, unchanged source/workspace/routes on rejection, restart, reaction resave, export, valid DOI correction and original-file preservation; text-backed optional DOI remains supported.
- `scripts/browser_smoke.py`: actual UI attempts to clear a DOI, verifies browser-required rejection and server rejection of whitespace, then saves the valid DOI and completes reaction/route/export flows. The same suite runs against the Windows EXE.
- `.github/workflows/windows-exe.yml`: also builds this GPT workflow branch; release publication stays disabled.
- Workflow docs: activate immediate user-authorized work and record the five roles without external AI API calls.

## Local evidence

| Command | Outcome |
| --- | --- |
| `.venv/bin/python -m pytest tests/test_desktop_references.py -q` | 9 passed |
| `.venv/bin/python -m pytest -q` | 153 passed, 1 skipped (Windows-only DPAPI); existing FastAPI deprecation warning |
| `npm run build` | PASS, TypeScript and production frontend |
| `python3 scripts/browser_smoke.py` | PASS, real Chromium UI including DOI deletion guard and retained DOI |
| `.venv/bin/python scripts/check_desktop_launch.py .venv/bin/python scripts/desktop.py --no-browser` | PASS, ordinary source startup and real restart preserving all records |
| `git diff --check` before commit | PASS |

The initial attempt to run browser_smoke using .venv failed because Playwright is provided by system Python in this cloud. Re-running with the documented `python3 scripts/browser_smoke.py` used installed Playwright/Chromium and passed; no assertion was disabled.

## Pending at implementation handoff

Exact-source Windows CI was triggered by the source push. The old receipt for `5c1c15a` is not evidence for this commit. Independent QA, Revision and current Windows result remain pending. Clean Windows VM and actual user default-browser integration are not executed in this Linux session and must remain explicit limitations.

This report is an evidence record to be committed on `codex/gpt-workflow-records`, not a change to the frozen source or packaged inputs.
