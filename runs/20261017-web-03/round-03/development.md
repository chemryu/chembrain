# Development — web round 03

Frozen source: **56be43bf15b4c98b8b515d2dc3bbd2bd0fcbbbae** (parent rejected source d423c718ca3c0b7d1dd090a362ba02990d7e223a).

User explicitly resumed the saved pause with “이어서 진행해줘”. Separate Planning read the complete published round-02 QA → Revision → Wiki handoff and wrote this round's plan before implementation. Its pre-freeze clarification covers the same WEB-QA-05 recent-checkpoint window edge. Root implemented CI state publication/proof checks and real-Git recovery tests; a separate Development helper implemented standalone processor/anchor failure recovery. This handoff is not independent approval.

## Repair and unchanged scope

- Shared `prepare_anchors(config, work, out)` and `python -m paper_pipeline anchor` create only original-window replay anchors for initially empty progress, before network discovery. Existing progress and malformed inputs are handled without silently narrowing/replacing their windows. Window/time validation fails closed before new anchor writes.
- All advancing metadata page cursors and completed-window checkpoints are buffered across journals until the full package validates and its atomic output replacement succeeds. Failed output retains the old package and old progress/replay anchor. A subsequent state-write failure is reported; the new bibliography stays available and old progress can replay idempotently.
- Checkpoint-derived discovery starts at the fixed checkpoint minus 14 days. The old clock-dependent minimum could itself lose known late-indexed metadata on a much later retry with a very recent checkpoint; the new regression preserves the exact original lower bound. Existing resume windows remain exact; first-ever discovery is a 14-day initial window.
- CI restores authoritative durable metadata progress, prepares/saves nonadvancing bootstrap anchors against the already-origin-acknowledged feed A, then crawls. Only after normalized feed B is committed/pushed does it save advanced state. A failed/cancelled feed push leaves the old anchored remote state available even after cache eviction.
- Actual `paper_state.save` requires explicit feed ref, feed commit and library SHA-256. It compares exact local bytes, committed blob bytes and origin's advertised ref; local unpublished B, wrong ref/hash/commit and stale acknowledgments cannot modify the state branch. Verified feed provenance is stored with the bounded whitelist state. Same-run bootstrap A/final B is accepted; newer-run/CAS protection remains.
- A cached metadata checkpoint absent from the durable index is discarded on explicit restore, preserving PDF archives. Cached unacknowledged progress cannot bootstrap itself as authority. Private PDF/review bytes never enter the state branch or Pages.

The prior four repaired contracts, English molecule-first UI, browser-local edits, DOI-reference grouping and all 3-paper/12-draft starter facts/assets are unchanged. The separate PDF pending queue, current-license checks, attempt limits and review recovery remain. No main merge, dispatcher activation, user-PC installation, Box sync, personal model API or automatic reviewed chemical extraction is claimed.

## Actual checks before freeze

- `.venv/bin/python -m pytest -q`: **273 passed, 1 skipped** (Windows-only DPAPI), existing Starlette/httpx deprecation warning only; 9.95s.
- `CHEMBRAIN_BASE=/chembrain/ npm run build:web`: **PASS**, TypeScript + Vite.
- `.venv/bin/python scripts/web_smoke.py`: **PASS**, actual Chromium molecule-first/stage/DOI/edit/reload/import/42-malformed-draft/actual-Python-export/backup/mobile/subpath/no-backend scenarios.
- Local processor/durability helper's focused suite: **34 passed**, including completed/interrupted/capped output failure, 101 records, first/recent/old checkpoint delayed replay, validation failure, two journals, post-output state failure, malformed/inverted windows and bootstrap-write failure.
- Real-Git state/provenance focused tests pass, including acknowledged A, unpublished B rejection, pushed B same-run save, wrong/stale identities, private-file exclusion, cache eviction and first-anchor November retry recovering October metadata.
- Diff checks and YAML parsing of actual workflow and still-unconfigured dispatcher artifact: **PASS**.

A new source-bound GitHub CI run is triggered by this push; evidence is pending at this handoff. Prior source d423's actual Pages 403 is historical evidence, not presumed to describe this source. Root has asked for the owner's current Source setting. No real public URL or HTTPS success is established. The dispatcher remains only a review artifact, with weekly activation unfinished and raw archive cache explicitly best effort.

## Exact-source GitHub result and environment readiness

New run https://github.com/chemryu/chembrain/actions/runs/39093753253 reached immutable terminal receipt **5829825cf51ea5a5677922886eb1c8575405822e** for exact source **56be43bf15b4c98b8b515d2dc3bbd2bd0fcbbbae**. Its tests are **273 passed / 1 skipped**, web build and full real-browser smoke PASS. Workflow/built source both equal56be for this non-collection push; library SHA-256 remains25e98df9810b686e9da2c3c3b3f7f5da627dd2186ab3b00533b28d34072aef8c. Collection/feed were skipped in this push; controlled real-Git fixtures supplied collection-failure boundary evidence. All six original receipt files and SHA-256/byte manifest are preserved under web/.

Pages configuration is a fresh actual **403 Resource not accessible by integration**. Deployment and actual HTTPS identity verification are **SKIPPED / NOT RUN**, page_url=null. No public address is established. Owner Source-setting response remains pending; a green build cannot supply Pages authorization.

Cloud readiness was rechecked using retained Python3.12/Node24 and a real static preview process with CHEMBRAIN_BASE=/chembrain/. Internal HTTP verified English HTML plus schema1/3-paper/12-reaction compact data at the repository subpath, with no API server. The owned preview was stopped after checking. A transient occupied-port retry was resolved by starting an owned process on another free port; it did not change app source or claim public access.

Cloud configuration draft `a3552723-4d36-40f1-84be-07f1391d95b6~cecfgdraft_6ad284a0831c8191890e572d9068e6ba` returned status=saved, requires_publish=true. Saved fields: current-browser `start_skill` and exact repository56be at mount chembrain after checkout discovery; install_script, network and secrets unchanged. /workspace/.git is an empty nonrepository environment placeholder and .cache/uv/sdists-v9/.git is an empty cache marker; chembrain is the sole valid project checkout. Startup directions cover current build:web, meaningful local checks, persistence, private processor workspace and existing review/hosting limits. The user must review/save the environment settings and Publish the environment to activate that configuration for later tasks. Draft persistence is not environment publication or Pages deployment; no fresh-task restoration is claimed.
