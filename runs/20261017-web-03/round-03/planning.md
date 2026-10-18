# Planning — 20261017-web-03 / round-03

- Status: READY FOR DEVELOPMENT; this plan is not source approval or delivery approval.
- Latest user instruction **“이어서 진행해줘”** resumes this task immediately and supersedes the saved pause. No clock wait or automatic scheduled resumption is claimed.
- Rejected/frozen source: `d423c718ca3c0b7d1dd090a362ba02990d7e223a`. Development must record a new full source SHA after implementation and checks; existing approvals do not transfer.
- Inputs read: AGENTS.md, RULEBOOK.md, agents/planning.md, requests/current.md, wiki.md, progress.json, [resume checkpoint](../RESUME.md), and complete round-02 [QA](../round-02/qa.md), [Revision](../round-02/revision.md), [Wiki handoff](../round-02/handoff.md). Those reports are already published on records commit `b9285eca83cb4dc5128b9ef00f146fb43675bd88`.
- One unresolved finding: **WEB-QA-05 / WEB-REV-05**, bibliography progress becoming durable before the bibliography. The four preceding editor/contract/PDF-queue/build-identity repairs remain resolved and must be preserved.

## Bounded implementation contract

### Standalone processor: output before all advancing metadata progress

Primary paths: `paper_pipeline/__main__.py`, the smallest shared preparation helper if useful, and focused processor tests.

1. Buffer every metadata progress update in memory, including intermediate page cursors, processed counts and completed-window `last_success`. Persist them only after the full normalized package validates and its atomic output replacement succeeds. Cover successful, capped, partially received and interrupted discovery paths, and all enabled journals; changing only the final checkpoint is insufficient.
2. A failed output validation/write leaves the previous package and all pre-existing metadata progress unchanged. Independent OA pending/retry work retains its existing safety, revalidation, bounded attempts, queue saturation and private review/archive rules; do not expand it into a public document archive.
3. Before the first provider request, create a durable **nonadvancing replay anchor** for any journal without usable prior progress: preserve the chosen original start date, end date, initial cursor, processed count and crawl-start timestamp. Existing valid progress is not replaced by a newer window. A failed first output may leave this initial anchor, but never an advanced cursor/checkpoint. This prevents a later-date retry from losing the first window when no earlier checkpoint or output `generated_at` exists.
4. Expose a small shared helper and explicit preparation CLI for this anchor operation. Standalone `weekly` must call the same helper automatically; CI calls it before crawling. Validate existing inputs and fail closed rather than silently discarding malformed progress.
5. If output succeeds but a subsequent state write fails, report failure and retain whichever older progress is durable. A retry must replay safely: every discovered DOI exactly once, prior reactions and user fields unchanged. Do not roll output back merely because older progress remains.

### CI: origin-acknowledged feed before advancing remote state

Primary paths: `.github/workflows/web-library.yml`, `scripts/paper_state.py`, and focused real-Git tests. Preserve separate immutable workflow/code source, actual built/data commit and exact public-library digest through existing build/receipt/HTTP paths.

Required order for an actual collection run:

1. Restore durable public metadata state, prepare initial/nonadvancing anchors with the shared CLI, then durably save that bootstrap state **before discovery**, bound to already-origin-acknowledged old feed **A**. If restoration, anchor creation or its guarded durable save fails, do not crawl. An evictable cache alone is insufficient protection.
2. Crawl and atomically write normalized feed **B**. Validate and commit/push only the allowed compact feed change. If publication fails or is cancelled, do not save advanced remote progress; the old anchored state remains replayable after total runner/cache loss.
3. Only after origin acknowledges the exact feed ref and commit, save advanced public metadata state bound to that feed's exact `public/library.json` SHA-256. A no-change feed still needs the same acknowledgment/hash check. Bootstrap A and final B saves in one run must both be supported without weakening newer-run or compare-and-swap protection.
4. Enforce the publication boundary inside the actual `paper_state.save` implementation/CLI, not just workflow step order. Require explicit feed ref, feed commit and digest; verify origin's current advertised ref resolves to that exact commit and its library blob matches the supplied/local output digest. Reject unpublished local B, an incorrect ref/commit/hash and stale publication acknowledgments without modifying the durable state branch. Persist the verified feed provenance in the state snapshot.
5. Retain the bounded public metadata whitelist, archive/private-text exclusion, newer-run protection and force-with-lease behavior. Do not turn collection failure/partial output into unqualified success. Do not activate the dispatcher, change the default branch, merge the app into main, alter repository permissions or bypass Pages settings.

## Required regressions and completion checks

Development must first add meaningful failure/recovery coverage against the actual processor and persistence code:

- Completed-window output-write failure with prior package and progress, followed by a substantially later-date retry: prior state/output preserved on failure and every discovered DOI recovered exactly once.
- A capped 101-item result with a 100-item first page: failed output must not durably advance to page two; successful retry retains all 101 DOI records across completion.
- First-ever run without checkpoint/generated timestamp: durable initial anchor survives failed output, later-date retry and full work/cache eviction after saving/restoring bootstrap state against origin feed A. The original window must remain recoverable, including bibliography-only non-OA records.
- Output success followed by state-write failure: safe idempotent replay, no missing/duplicate DOI or mutation of original reactions/user fields.
- Actual temporary Git remote A→local unpublished B→pushed B: fail-closed rejection of unpublished B, wrong ref/hash/commit and stale acknowledgment; acceptance only of the exact acknowledged feed; same-run bootstrap/final saves and preservation of old remote state on failure. Inspect saved provenance and ensure private files never enter it.
- Preserve existing four repair regressions, cross-runtime contract corpus, PDF continuation/license checks and source/data identity tests. Run the appropriate focused suite, then full Python suite, production repository-subpath web build and real-browser persistence/import/mobile checks once the changes are stable.

Freeze and push one corrected full source SHA. Development writes actual changed paths, commands, results and limitations in `development.md`. Separate Independent QA and Revision then review that exact SHA and fault-injection recovery, without source edits. Wiki preserves their complete reports and source-bound CI evidence; any remaining issue returns through a new handoff to Planning. No preliminary zero-finding message or green old build grants approval.

## Separate external milestones and retained scope

The last exact-source Pages run had actual **HTTP 403 `Resource not accessible by integration`**; deployment and public HTTPS verification were NOT RUN, URL null. The owner's Pages Source setting response remains pending. Continue the code repair independently, but claim an accessible preview only after real deployment and HTTPS verification of the exact workflow/built-data identity and library digest. A new SHA needs its own evidence; old hosting failure is history, not an assumed current result.

UI, three-paper/twelve-draft starter facts and depictions stay unchanged. Preserve molecule-first empty initial reaction panel, English UI, DOI-deduplicated paper cards with all locators, scientific unknowns, compact-only exports and browser-local edits/backups. Weekly dispatcher remains an unconfigured review artifact; no weekly operation, user-PC installation, Box synchronization, institutional login, personal model API use, complete chemistry extraction or autonomous background GPT service is claimed. Publishing the explicitly requested labelled preview remains separate from production release approval.

This plan authorizes only the bounded durability repair and its necessary tests/documentation in the active task. It does not approve the resulting implementation or authorize scheduler/default-branch activation.

## Pre-freeze clarification: checkpoint-only windows must also replay stably

Development identified another instance of the same WEB-QA-05 boundary before source freeze. Merely preserving a valid `last_success` byte-for-byte is insufficient if the next query computes `min(now − 14 days, checkpoint − 7 days)`: checkpoint October 16 gives an October 3 start on October 17, but a November retry starts October 9 and loses an uncommitted October 4 article.

For a checkpoint-only run, derive the lower window boundary **only from the durable checkpoint**, using a fixed fourteen-day lookback. Thus the example starts October 2 on both attempts. Retain an existing resume anchor's exact bounds; retain the first-ever fourteen-day anchor when no checkpoint exists. This bounded expansion of the former seven-day checkpoint overlap preserves the required pre-existing state byte identity without adding a fresh resume write over an existing checkpoint before output. The same window-selection rule must be used wherever shared preparation and weekly discovery derive a checkpoint-based window; no moving `now`-based minimum may narrow a replayable earlier window.

Add an actual regression with the recent October 16 checkpoint, October 17 failed output, October 4 bibliography-only DOI and substantially later successful retry. Assert the first failure leaves prior checkpoint/output bytes unchanged, both requests retain the same lower bound, and recovery exports the DOI exactly once with original reactions/user fields intact. This clarification is part of the same unfrozen durability repair, not a new feature, approval or completed test.
