# Planning addendum — post-implementation scope audit

- Role: separate Planning GPT agent, resumed after the earlier capacity limitation. No API keys/model calls or limit-avoidance mechanism were introduced.
- Audited source: `e424b34653fb96b911f5ee5708286c92baddfe5f` on `codex/gpt-agent-workflow`.
- This document was written **after implementation and source freeze**, while independent QA/Revision and Pages CI were underway. It supplements [the original planning snapshot](planning.md); it does not pretend that an independent Planning agent approved the implementation beforehand.
- Inputs: `requests/current.md`, the original snapshot, paper processor/schema, browser data/UI, schedule installer and Pages workflow. The 237-test/build/browser results described by Development are implementation evidence, not tests run or approval issued by this Planning role.

## User requirements versus present scope

| Requirement | Observed implementation scope; remaining gate |
| --- | --- |
| Internet browser use, selected GitHub Pages + browser storage | Static browser entry, no backend/model key, local edits and compact JSON backup/import. A live preview requires successful Pages deployment and actual HTTPS HTML/assets/library/source-marker checks; creating a workflow/URL alone is insufficient. Independent review is still required before claiming independent approval. |
| Molecule-first initial screen | No initial selected molecule, no populated reaction/category panel, molecule selection reveals related reactions and optional synthesis-route steps. Verify first visit, reload and mobile behavior, including absence of legacy All reactions/Organic synthesis controls in this browser mode. |
| Separate paper information processor | `paper_pipeline` archives supported OA PDFs/review candidates outside the application tree and exports normalized papers/chemicals/solutions/reactions. Main UI excludes PDFs and extracted body text. Verify schema/import boundaries and preservation of user edits/foreign keys rather than treating a small JSON file as proof of correct information separation. |
| Chemical/reaction/solution/DOI/author facts | Three-paper, 12-draft curated starter; unknown structures, amounts and conditions remain missing. Normalization and stage-specific solvent/solute links are present. Source accuracy/provenance must be independently reviewed. This is bounded manual curation, not complete automatic synthesis/scheme extraction. |
| Weekly operation | A feature-branch cron and an unrun local installer are prepared, but neither proves an active weekly service. GitHub scheduled workflows execute only from the default branch. User-PC task installation is NOT RUN. Weekly activation remains unfinished until one real route is installed and verified. |

The current weekly processor discovers bibliography, archives supported OA PDFs and creates local review candidates. It does **not** automatically turn each newly published paper into validated reaction/chemical/solution records. Human curation followed by normalized export/import remains necessary. This distinction must be explicit in delivery and any completion status; do not call automated chemistry extraction complete.

## Preserve the selected boundaries

Keep all JACS papers without a subject filter, explicit OA-only PDF policy, no institutional cookies/subscription download path, no personal AI API, honest provider failures/checkpoints, and paper-specific unknown intermediates. Browser changes stay local to that browser; no automatic cross-device synchronization is promised. Initial selection remains empty after reload. Do not publish raw archives/candidates or promote drafts to reviewed records automatically.

The user's explicit browser-preview authorization replaces the prior Windows-delivery blocker for this preview; it does not retroactively approve Windows or transfer old review decisions. PREVIEW labeling remains appropriate. Do not rewrite historical quota-blocked reports as if reviews occurred then; record new reports and their actual SHA/ordering now.

## Concrete path to finish weekly activation without an app merge

The user's requested weekly operating behavior supports preparing and implementing its necessary bounded scheduler configuration. A full merge of the application into `main` is unnecessary. The old local rule against automatically merging the application must not be treated as an automatic request for fresh permission for every reversible, narrowly scoped scheduling step.

Recommended sequence:

1. Finish QA → Revision → Wiki on the actual candidate. Any concrete application/data/pipeline gaps become a new Planning round before fixing source; do not expand this addendum into implementation or waive findings.
2. Verify the concrete public preview over HTTPS and retain its source/data marker plus real CI results. If Pages/account policy blocks deployment, record the exact blocker instead of claiming internet availability.
3. Prepare a **single-file, default-branch scheduled dispatcher**, with an exact reviewable diff, rather than merging app/source/data into main. An effective bootstrap can occupy the same `.github/workflows/web-library.yml` path on the default branch, with only `schedule` and `workflow_dispatch`, and dispatch that workflow's tested definition on the source branch with `collect: true`. Registering the same workflow path on default is significant: a different dispatcher calling an otherwise feature-only, unregistered dispatch workflow may not activate it.
4. Use the repository-provided `GITHUB_TOKEN` with only required `actions: write` and `contents: read`; no personal token or new external credential. The default dispatcher must not recursively dispatch its own default-branch definition. It targets the named source branch whose executable/workflow tree was reviewed. Verify that target before dispatch; if later public/library.json data-only updates are allowed, explicitly restrict that exception and validate compact data instead of trusting arbitrary future branch changes. Record dispatcher commit, triggering run, target full SHA and data/build provenance separately.
5. Review/test the dispatcher contract, fixed target, cron, event inputs and failure behavior before activation. A single-file nonforce default-branch commit is the bounded operating change, if repository policy permits; no force push, branch setting change, full app merge or release. Then exercise one bounded dispatch/collection cycle and confirm actual collection outcome separately from Pages availability. Schedule time is the documented UTC cron (Monday 15:00 UTC), not a falsely fixed local daylight-saving time.
6. Only report GitHub weekly scheduling as active after the default workflow is installed, recognized and exercised; preserve partial/provider-unavailable results honestly. Browser refresh imports published compact updates while preserving local edits; new chemical facts still require curated input.

This is a Development recommendation, **not** permission for this Planning agent to write main or a claim that the bootstrap was executed. If repository branch protection requires a maintainer merge or GitHub policy blocks Actions/Pages, prepare the concrete PR/diff first and identify that actual platform requirement. That is a genuine owner action; do not ask for broad approval merely because a default-branch file is involved. A locally installed PC schedule is an alternative, but this cloud cannot install it on the user's Windows PC, and it cannot be called active until the user executes and verifies it.

## Review and completion record

QA/Revision should assess the weekly activation gap, processor-versus-curated-chemistry distinction, strict compact-package boundary, paper/structure normalization and preservation, source-paper examples, molecule-first browser flow and public preview evidence. Concrete gaps follow QA/Revision → Wiki → next Planning, not an undocumented bypass of the requested roles.

Deliver the verified browser preview with accurate known limits when its preview requirements pass; distinguish a preview milestone from the unfinished weekly operating milestone. Final weekly-operation completion additionally needs an installed, inspected and successfully invoked scheduler route, truthful collection evidence, and independent review of any added dispatch/build inputs. Keep exact source/report provenance; no production-release approval is issued here. Box writes/sync, actual user-PC installation and institution-authenticated retrieval remain NOT RUN.
