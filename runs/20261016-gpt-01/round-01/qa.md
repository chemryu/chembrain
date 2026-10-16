# Independent QA — 20261016-gpt-01 / round-01

- Role: separate GPT Independent QA; no application, test or CI source edits.
- Frozen source: `3f102821649ff13b5581ebdff18274ef46602322` on `codex/gpt-agent-workflow`.
- Scope: Planning's DOI integrity correction and retained English chemistry desktop behavior. No personal external AI API calls were made.
- Final verdict: **PASS for the scoped review candidate**. Unresolved findings: **0**. Local checks and required Windows evidence pass for this exact source SHA. Revision must still make its separate decision before final handoff; this is not public-release authorization.

## Independent source review

Reviewed the final diff and surrounding source in `server/app.py`, `server/models.py`, `server/store.py`, `src/SourceMetadata.tsx`, `src/main.tsx`, DOI and molecule regression tests, the shared browser scenario, desktop launcher and launch harness, packaging notes and Windows workflow.

The metadata guard runs before persistence and requires a DOI for every DOI-only `reference` source or any source mentioned by citation-only evidence. It does not filter by reaction status, so draft citations are protected too. Pydantic normalizes DOI URLs and whitespace before the guard. Uploaded PDF/Markdown/text documents backed solely by matching original-text evidence retain an optional DOI. The English editor derives its required condition from all reactions; the server remains authoritative when a browser has stale state. Valid corrections preserve the source ID and original upload. No source migration or reaction status downgrade was added.

No unresolved application finding was identified in this review.

## Independently executed local checks

All commands ran from the frozen source checkout in the Linux cloud. Temporary fixture data was used; existing user records were not the test target.

| Check | Result | Evidence |
| --- | --- | --- |
| `.venv/bin/python -m pytest -q` | PASS | 153 passed, 1 skipped in 4.96 seconds. The skip is the Windows-only credential encryption roundtrip; it is not claimed as a Linux pass. Existing Starlette/httpx deprecation warning only. |
| `npm run build` | PASS | TypeScript and production Vite build completed; 1,724 modules transformed. |
| `python3 scripts/browser_smoke.py` | PASS | Real Chromium rendered the English UI and exercised DOI links with no full-paper view, DOI deletion rejection, molecule creation/editing including linked identity protection, reaction create/edit with photochemical conditions, paper filter, reviewed routes/draft exclusion, DOI-only Markdown export, reload, mobile layouts and no JavaScript page errors. |
| `.venv/bin/python scripts/check_desktop_launch.py .venv/bin/python scripts/desktop.py --no-browser` | PASS | Ordinary source launcher started twice with the same isolated default data folder; entire workspace, added molecule and corrected starter metadata survived the real process restart. This invocation deliberately skipped browser launch and was not Windows EXE evidence. |
| Independent inline API matrix, separate from committed regression tests | PASS | 54 scenarios described below; no application/test source files were changed to run it. |
| Independent additional Chromium scenarios | PASS | An uploaded source linked to a draft citation shows the English explanation and browser-required DOI. A browser loaded before a new reviewed citation was added still receives the authoritative server 422 when clearing its formerly optional DOI; the original link and stored DOI remain intact. |

The independent API matrix used actual `reference`, `.txt`, `.md` and generated one-page `.pdf` sources. It covered unlinked sources and both draft/reviewed reactions; citation-only and original-text evidence where legal; empty DOI, whitespace DOI and omitted DOI. All DOI-required cases returned 422 with the useful English message; the complete source and workspace stayed unchanged and remained unchanged after reopening the same data directory. Optional uploaded-document DOI clearing succeeded. Valid `HTTPS://DX.DOI.ORG/…` replacement normalized successfully in every scenario, and every original uploaded file remained byte-for-byte identical. Existing committed regressions additionally verify unchanged routes, reaction resaving and DOI-only exports after rejection.

## Exact-source Windows evidence

Independently fetched the completed `build/windows-status` receipt, then captured every evidence file using the immutable generated Git commit `0c6df260af7ef7a340cd2aff80415d4577c63bbf`. Each file in [windows/](windows/) is byte-preserved from `git show <receipt-commit>:<file>`, rather than copied from a previous build.

- Commit: `3f102821649ff13b5581ebdff18274ef46602322` — exact match.
- Status: `success`; dependency, validation, packaging and artifact stages all `success`.
- Run: <https://github.com/chemryu/chembrain/actions/runs/38978428660>.
- Artifact: <https://github.com/chemryu/chembrain/actions/runs/38978428660/artifacts/12080600552>.
- ZIP: `Chembrain-Windows-x64.zip`.
- CI-produced SHA-256: `ceacbc857ec919b45687f4108fe1394d8a4405643e592358e75cf942ba06b9c0`.
- Release publication: `false`.

| Windows evidence inspected by QA | Result | Retained evidence |
| --- | --- | --- |
| Exact source, all stages successful and commit-specific artifact | PASS | [status.json](windows/status.json) |
| Windows Python tests including the DPAPI check skipped on Linux | PASS | [api.log](windows/api.log): **154 passed**, no skips; existing deprecation warning only. |
| Bundled executable smoke: English assets, RDKit SVG, starter DOI-only references | PASS | [packaged-smoke.log](windows/packaged-smoke.log) |
| Zero-argument ordinary EXE launch and rendered app UI | PASS | [normal-launch.log](windows/normal-launch.log), including `WINDOWS_PACKAGED_UI_PASS` and the complete shared browser scenario. |
| Real EXE process restart using the same default directory, whole workspace and user corrections retained, fresh browser reads persisted notes/inventory | PASS | `WINDOWS_RESTART_PERSISTENCE_PASS`, first/second launch output and restarted-UI output in the same log. |
| EXE child runs after Python/Node launchers are absent from its restricted PATH | PASS | `WINDOWS_RUNTIME_PATH_INDEPENDENCE_PASS` in the same log. |
| Inner Windows ZIP checksum generated after tests and uploaded alongside that candidate | PASS | [SHA256SUMS.txt](windows/SHA256SUMS.txt), value above. This session inspected CI's checksum; it did not independently download the authenticated artifact and recompute its bytes. |

The workflow computes the checksum from the just-tested executable package and uploads that ZIP and checksum together. Handoff must use the artifact linked above without substituting or repacking another build. No previous source commit's Windows receipt was accepted.

## Explicit coverage limits

- Clean Windows VM without any developer tools: **NOT RUN**. Restricted child PATH testing, once passed, establishes PATH independence only.
- User default-browser registration/integration: **NOT RUN**. CI uses a short-lived browser-intent probe and separately renders the actual packaged UI with Chromium.
- This Linux session cannot install into the user's Windows Box folder or certify that a Box sync completed.
- No public release, deployment, Windows permission change or perpetual GPT background worker was performed or approved.

These labeled manual coverage limits are consistent with the round's candidate-delivery scope and are not represented as automated passes. Required exact-source automated evidence is complete. There is no remaining QA finding to return to Planning; the result proceeds to the separate Revision review and Wiki record.
