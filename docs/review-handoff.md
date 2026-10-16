# Independent review handoff

The previous report inspected commit `1680473769dc0c84c1b35c4b154898fd03297893`. Re-review the new branch HEAD and require the Windows receipt's `commit` to match it exactly.

| Previous finding | Change | Evidence to review |
| --- | --- | --- |
| Windows check fails while Edge locks its redirected profile | Use documented BROWSER override with an OS shell probe; assert the actual browser request URL. Exercise the rendered app independently with Playwright. Cleanup errors still fail validation. | `tests/test_desktop_launcher.py`, `scripts/check_desktop_launch.py`, `normal-launch.log` |
| Molecule editing absent | PUT endpoint and English edit form for name, aliases, availability, notes and validated unlinked structures. Reject identity changes for reaction-linked molecules and duplicate structures. | `tests/test_molecule_edit.py`, source and packaged browser UI checks |
| Ambiguous PDF page labels | Explicit pdf/printed/unspecified numbering; curated starter data identifies original PDF indices. Export and UI share matching terminology; no full-text excerpts. | export regression test and browser export check |
| Old release mistaken for reviewed output | Disable release publication; mark README and packaged notes as candidates. Retain commit-specific Actions artifact and SHA256SUMS. | workflow, receipt `release_published: false` |
| No EXE restart or existing-data check | Launch twice using the same isolated default app data directory, create a user molecule, correct a starter record, compare the entire workspace after process restart. | `normal-launch.log` |
| UI checks only cover source mode | The same browser suite runs against the packaged EXE, including molecule/reaction edits, DOI links, route/draft behavior, export and mobile layouts. | `normal-launch.log` |
| Python/Node-free Windows unverified | Restrict the EXE child PATH to Windows system directories, remove Python/Node environment overrides and assert launchers cannot be found. | This establishes PATH independence, **not a clean Windows VM**. Clean-machine test remains NOT RUN. |

The browser-intent probe confirms webbrowser.open receives the running server URL. It does not claim to validate Edge/Chrome's default-handler configuration on a user's machine. That system integration remains a separate manual check.

CI uploads a candidate only after all automated steps pass. It never publishes a release. Inspect the tested commit, outcomes, errors and limitations without changing code, triggering publication or treating NOT RUN as PASS. Return remaining issues for another implementation/review cycle.
