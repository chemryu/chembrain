# Planning — 20261016-gpt-01 / round-01

- Role: separate Planning GPT agent; implementation and approval are outside this role.
- Starting documentation HEAD: `f48e9cc2928b5ee3ade2231e25af7a417cedab17`.
- Inherited application source: `5c1c15a920a6f50dc330366507597902c8a0ef64`.
- User direction: **“지금 바로 시작해줘”** supersedes the earlier usage-reset pause. Work is authorized immediately; a scheduled restart is unnecessary.
- Shared record store: GitHub `chemryu/chembrain`, branch `codex/gpt-agent-workflow`. Windows Box access/synchronization is unavailable in this session; do not claim files were saved there.
- Execution: GPT roles in this active Codex task. No personal OpenAI/Anthropic API calls, API keys, or local API controller are needed.

## Requirements and scope

Complete the existing English local desktop chemistry app, preserving user records and the current supported flows: molecule creation/editing, reaction creation/editing and conditions, graph and paper filtering, bounded route search with draft exclusion, persisted data after real restart, and Markdown export. Present papers as citations and DOI links; do not introduce full-paper viewers or export paper text/excerpts. The Windows package must start without installing Python or Node.js.

This round targets the known DOI integrity defect and the Windows verification gap introduced by the new branch. Avoid broad redesign, additional cloud services, new credentials, automatic releases, and unrelated changes to the legacy API workflow kit. Activate the five-role records and retain historical pause records as history while making the current active status unambiguous.

## Required defect correction

Baseline: [initial finding](../../../reviews/baseline-doi-finding.md). `PUT /api/sources/{sid}/metadata` currently allows an empty DOI on a DOI-only reference, including one used by a reviewed reaction with `citation_only` evidence. The reaction remains reviewed and participates in routes, yet cannot be saved again because its source no longer satisfies evidence validation. The DOI input in `src/SourceMetadata.tsx` also permits this deletion.

1. Reject removal of a DOI from every `kind: reference` source, even when no reaction currently uses it: that source has no alternative original-document evidence.
2. Reject removal of a DOI from an uploaded source when **any** reaction references it with `citation_only: true`, including drafts. Reaction save validates draft citations too; protecting reviewed reactions alone would leave inconsistent saved data.
3. Apply the check before persistence. Treat omitted DOI, `""`, and whitespace normalized to empty consistently. Return a useful English 422 error and leave the complete existing source, reactions, and route results unchanged.
4. Preserve legitimate uploaded-document behavior: an unlinked upload or upload used only by text-backed evidence may retain/clear an optional DOI. Do not force a DOI onto every lab note or original document.
5. Align metadata editing with the server rule: mark DOI as required when necessary and explain the requirement in English. The backend remains authoritative if the browser has stale source/reaction state. Valid normalized DOI replacement and unrelated metadata edits must continue to work without losing IDs or original uploads.

No migration should rewrite, delete, or silently downgrade a user's existing reaction. Already inconsistent data, if discovered, should be reported and repaired through the normal metadata editor rather than invented evidence.

## Development work and checks

| Work | Meaningful verification |
| --- | --- |
| Server DOI guard and UI requirement | Focused regression: DOI-only unlinked and linked sources; uploaded source linked to draft/reviewed citation-only evidence; blank/whitespace/omitted DOI rejected; valid replacement accepted; ordinary text-backed upload can clear DOI. Compare workspace before/after failed update and restart with the same directory. |
| Preserve reviewed-reaction consistency | After rejected deletion, original DOI is retained, the same reviewed reaction can be saved again, route candidates retain it, and Markdown still links the DOI without paper text. |
| Real browser metadata edit | Extend the existing browser scenario to attempt removal, observe required validation or English rejection, reload and verify the original link, then make a valid edit and continue reaction/route/export flows. This same suite runs against the packaged EXE. |
| New branch Windows build | `.github/workflows/windows-exe.yml` currently auto-runs only for `codex/chembrain-mvp`. Include `codex/gpt-agent-workflow` so a push of this exact candidate builds the EXE. Preserve validation, smoke, ordinary launch, restart, restricted-runtime, artifact checksum and no-release behavior. |
| Local regression and frontend | Run the existing Python suite and `npm run build`; run the source browser/ordinary-start checks appropriate to the metadata change. Do not replace execution with source inspection. |
| Windows artifact evidence | Wait for the generated `build/windows-status` receipt whose `commit` equals the exact candidate SHA. Require successful validation/packaging/artifact stages, `--smoke-test`, no-argument launch, rendered UI, real restart persistence and restricted Python/Node PATH checks. Preserve logs, artifact URL and SHA-256. |

Development must record exact commands, outcomes, changed files and source commit in `development.md`. Initial planning/document commits are not application validation evidence. Commit the final implementation before Independent QA so its SHA is stable; if code or executable inputs change afterward, invalidate approval and repeat affected checks and both reviews on the new SHA.

## Independent roles and loop

1. Development implements and provides evidence for a full source SHA.
2. Independent QA independently inspects that SHA and runs/reproduces meaningful checks, including the baseline DOI failure cases and relevant preservation behavior. Record PASS/FAIL/NOT RUN and distinguish local checks from Windows CI evidence in `qa.md`; no application edits.
3. Revision independently compares this plan, implementation, QA, and exact-SHA CI evidence; records every unresolved finding and concrete next work in `revision.md`; no application edits.
4. Wiki preserves both complete reports, records the round and status in `wiki.md`, and writes `handoff.md`. Any remaining finding returns to Planning; do not silently waive it. If an external blocker prevents required evidence, record BLOCKED rather than iterating without purpose.

## Acceptance and user delivery

Delivery is permitted only when all of the following hold:

- The DOI cases above pass and all retained application requirements are verified without data loss.
- Required Python/frontend/browser checks pass; the exact candidate has a successful Windows build, smoke test, zero-argument start, packaged browser UI, real restart data retention, and Python/Node PATH-independence evidence.
- Independent QA and Revision each report zero unresolved findings for the **same full candidate SHA** as Windows CI. A source change requires a new review/evidence cycle.
- The downloadable Windows candidate ZIP and its SHA-256 match that validated commit's receipt; use a commit-specific GitHub Actions artifact, never the known-broken `windows-3` release or a previous SHA's file. Include concise extraction/double-click instructions and the persistent-data location.
- Wiki records a complete terminal handoff and honest limitations. No release publication, permission changes, deployment, Box synchronization, background agent activity or future automatic scheduling is claimed or performed.

Clean Windows VM execution and the user's default-browser integration remain explicitly **NOT RUN** unless actually performed. Restricted-runtime PATH checks and the browser-intent probe do not establish those results. They are known manual coverage limits, not replacements for the required automated checks or evidence of a clean-machine/default-browser pass. Convey these limitations with any candidate delivery.
