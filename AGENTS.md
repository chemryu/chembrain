# ChemBrain GPT workflow

Read [RULEBOOK.md](RULEBOOK.md), [wiki.md](wiki.md), [progress.json](progress.json) and [requests/current.md](requests/current.md) before implementation. GitHub is the shared record store. No personal OpenAI/Anthropic API calls or credentials are needed for this workflow.

The user requested five separate roles: Planning → Development → Independent QA → Revision → Wiki → Planning. On an active implementation task, use separate GPT agents for Planning, Independent QA, Revision and Wiki; the primary agent may handle Development and coordination. Respect the role instructions in agents/. Independent QA and Revision must not edit application code. The Wiki agent records each round, saves Revision's complete report and returns unresolved work to Planning. Stop the loop only after both independent reviews have no unresolved findings and required checks pass for the exact source commit.

The current state is RUNNING / PLANNING for run `20261016-gpt-01`, round `round-01`. On 2026-10-16 (America/Chicago), the user explicitly requested "지금 바로 시작해줘" (start now). This latest instruction supersedes the earlier request to wait for the usage reset described as "2026-10-16 7:43pm CST". Implementation and independent review may proceed now. There is no scheduled automatic resume. Preserve the earlier pause in the historical record.

Preserve user data, the English UI and DOI-only paper presentation. Do not treat unrun tests as passed or transfer approval between commits. Record the evidence and limitations, and do not publish a release, deploy a service or change permissions as part of the internal review loop. Use the existing checkout; do not create another worktree unless requested.
