# ChemBrain GPT workflow

Read [RULEBOOK.md](RULEBOOK.md), [wiki.md](wiki.md), [progress.json](progress.json) and [requests/current.md](requests/current.md) before implementation. GitHub is the shared record store. No personal OpenAI/Anthropic API calls or credentials are needed for this workflow.

The user requested five separate roles: Planning → Development → Independent QA → Revision → Wiki → Planning. On an active implementation task, use separate GPT agents for Planning, Independent QA, Revision and Wiki; the primary agent may handle Development and coordination. Respect the role instructions in agents/. Independent QA and Revision must not edit application code. The Wiki agent records each round, saves Revision's complete report and returns unresolved work to Planning. Stop the loop only after both independent reviews have no unresolved findings and required checks pass for the exact source commit.

The current state is PAUSED. The user requested resuming after the usage reset described as "2026-10-16 7:43pm CST". Do not begin implementation or additional review before the user's post-reset resume request. Preparing and saving these requested documents is authorized. There is no scheduled automatic resume.

Preserve user data, the English UI and DOI-only paper presentation. Do not treat unrun tests as passed or transfer approval between commits. Record the evidence and limitations, and do not publish a release, deploy a service or change permissions as part of the internal review loop. Use the existing checkout; do not create another worktree unless requested.
