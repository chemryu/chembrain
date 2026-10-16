# Revision — 20261016-gpt-01 / round-01

- Role: separate GPT Revision agent; no application, test, packaging or CI source edits.
- Reviewed source: `3f102821649ff13b5581ebdff18274ef46602322` on `codex/gpt-agent-workflow`.
- Inputs: [Planning](planning.md), [Development](development.md), complete [Independent QA](qa.md), source diff and surrounding implementation, and exact-source Windows evidence.
- Final judgment: **PASS for delivery of the scoped review candidate**.
- Unresolved findings: **0**. Required automated checks: **PASS**. No additional implementation round is required.

## Findings and disposition

| Item | Revision judgment | Basis |
| --- | --- | --- |
| DOI-only references could lose their DOI and invalidate saved citations | **RESOLVED** | The metadata handler rejects an empty normalized DOI before any persistence for every `kind: reference`, including unlinked references. Omitted values and whitespace are handled consistently by the existing input model and new guard. |
| Uploaded sources linked to draft or reviewed DOI citations could lose their DOI | **RESOLVED** | The guard checks all stored reactions and all evidence entries, without filtering on review status. Both Independent QA's matrix and Revision's complementary mixed-evidence draft scenario pass. |
| A blanket mandatory DOI would incorrectly exclude ordinary lab notes | **NO REGRESSION FOUND** | Unlinked uploads and uploads supported solely by original-text evidence can retain an optional DOI. Independent QA exercised actual PDF, Markdown and text uploads; Revision independently confirmed omitted/empty DOI on an unlinked text upload. |
| DOI editor could permit a destructive metadata save | **RESOLVED** | The English editor derives `required` from the same source/reaction condition and explains it. QA's real-browser scenarios cover both the required uploaded-draft field and stale browser state receiving authoritative server rejection. |
| Failed updates might partially save metadata or damage user records | **NO REGRESSION FOUND** | Rejected updates leave the complete source/workspace and route results unchanged. Restart, reaction resave, valid normalized DOI correction and byte-for-byte original uploads are verified. No migration, record deletion, invented evidence or silent review-status downgrade was introduced. |
| New source branch lacked matching Windows candidate evidence | **RESOLVED** | The Windows trigger includes `codex/gpt-agent-workflow`. Completed CI and all inspected evidence explicitly identify the same frozen source SHA; no earlier artifact is substituted. |

Revision independently inspected `server/app.py`, its models/store interactions, `src/SourceMetadata.tsx`, the caller's required-field condition, DOI regressions, browser scenario, desktop launcher and harness, packaging notes and Windows workflow. The current application/test/build-input diff against the frozen source was empty when this report was completed.

## Complementary checks executed by Revision

Revision ran an inline API scenario against temporary fixture storage using `.venv/bin/python`, independently of the committed regressions and QA's matrix. It reported `REVISION_COMPLEMENTARY_DOI_MATRIX_PASS` and verified:

- An unlinked uploaded note can clear or omit its DOI.
- A draft with original-text evidence first and citation-only evidence in a later slot still requires the DOI.
- Empty URL prefixes (`https://doi.org/` and whitespace-padded `HTTP://DX.DOI.ORG/`), blank values, whitespace and an omitted DOI reject without changing the workspace.
- The full workspace remains identical after reopening the same data directory.
- A valid URL-form replacement normalizes successfully; the same reaction can be saved again and the uploaded file bytes are preserved.
- An unlinked DOI-only reference cannot lose its DOI through URL-prefix normalization.

Only the existing Starlette/httpx deprecation warning appeared. These checks did not edit application or test files and did not use external AI APIs or credentials.

## Evidence cross-check

Revision read the completed Windows receipt and logs directly from immutable generated receipt commit `0c6df260af7ef7a340cd2aff80415d4577c63bbf`, then compared the final QA report and retained evidence with that result.

| Required evidence | Result |
| --- | --- |
| Independent QA final verdict for the same full source SHA | **PASS**, 0 unresolved findings |
| Independent Linux Python suite | **PASS**, 153 passed; 1 Windows-only DPAPI skip is explicitly labeled |
| Production frontend build and source Chromium UI | **PASS**, independently executed by QA |
| Source ordinary startup and real process restart | **PASS**, independently executed by QA |
| Windows dependency, validation, packaging and artifact stages | **PASS**, all stages `success` in [status.json](windows/status.json) |
| Windows full Python suite | **PASS**, 154 passed with no skips in [api.log](windows/api.log) |
| Bundled executable smoke | **PASS**, [packaged-smoke.log](windows/packaged-smoke.log) |
| No-argument EXE launch and rendered packaged UI | **PASS**, complete browser scenario and `WINDOWS_PACKAGED_UI_PASS` in [normal-launch.log](windows/normal-launch.log) |
| Real EXE restart with all records and user corrections preserved | **PASS**, first/second launch evidence, restarted UI and `WINDOWS_RESTART_PERSISTENCE_PASS` |
| Python/Node launchers absent from EXE child's restricted PATH | **PASS**, explicit runtime check and `WINDOWS_RUNTIME_PATH_INDEPENDENCE_PASS` |
| Commit-specific tested candidate and CI-produced checksum | **PASS**, artifact URL and [SHA256SUMS.txt](windows/SHA256SUMS.txt) identify the package below |

- CI run: <https://github.com/chemryu/chembrain/actions/runs/38978428660>.
- Candidate artifact: <https://github.com/chemryu/chembrain/actions/runs/38978428660/artifacts/12080600552>.
- Inner package: `Chembrain-Windows-x64.zip`.
- CI-produced SHA-256: `ceacbc857ec919b45687f4108fe1394d8a4405643e592358e75cf942ba06b9c0`.

The workflow hashes the package containing the just-tested EXE, then uploads that ZIP and checksum together in this exact-source run. This session inspected that CI provenance and checksum; it did not independently download the authenticated artifact and recompute its bytes. Delivery must link this artifact without substitution or repacking. Do not transfer this judgment to a changed source commit or the old broken `windows-3` release.

## Scope, limitations and Wiki handoff

The source satisfies this round's planned candidate-delivery criteria. Clean Windows VM execution and the user's actual default-browser registration/integration remain **NOT RUN**. Planning explicitly identifies these as manual coverage limits; PATH isolation and the browser-intent probe do not establish either result. This judgment supports delivery of the labeled review candidate with those limits disclosed, and does not authorize a production release or claim a clean-machine/default-browser pass.

Wiki should preserve this complete report and QA's complete report, record zero unresolved findings and the exact source/artifact/checksum, and close the round without returning an empty work list to Planning. No public release, deployment, permission grant, Box synchronization, scheduled execution or perpetual GPT background agent has been performed. GitHub is the shared record store; this Linux session has not written to the user's Windows Box folder. No additional code task remains for Planning in the agreed scope.
