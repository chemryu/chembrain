# Independent QA — 20261017-web-03 / round-03

- Frozen source: **`56be43bf15b4c98b8b515d2dc3bbd2bd0fcbbbae`**, branch `codex/gpt-agent-workflow`; rejected parent `d423c718ca3c0b7d1dd090a362ba02990d7e223a`.
- Role: a separate Independent QA GPT. Read-only application/CI/test review and independent execution; no source, tests, permissions or source history edited. This report is the only repository write by this role. No personal model API, institutional credentials, publisher PDF request, schedule activation or repository-setting change was used.
- **Final source-review verdict: PASS; 0 unresolved code findings in the bounded round-03 review.** WEB-QA-05 / WEB-REV-05 is resolved by the implementation and failure/recovery evidence below. Previous source approval is not inherited.
- **Hosted-preview verdict: BLOCKED_EXTERNAL_PAGES_CONFIGURATION.** The new exact-source GitHub run independently passes tests/build/browser, then actually receives Pages HTTP 403 `Resource not accessible by integration`. Deployment and public HTTP checks are skipped/NOT RUN; URL is null. This is zero unresolved code findings with an external delivery blocker, not completed accessible-preview delivery.

## Resolution of WEB-QA-05 — output and progress durability

The shared preparation helper creates a nonadvancing first replay anchor before any discovery request. It retains the original start/end dates, initial cursor, zero processed count and crawl-start timestamp. Existing usable progress is retained; malformed progress/configuration is rejected before discovery and before writing a new journal anchor. Standalone `weekly` automatically calls the same helper exposed by the explicit `anchor` CLI used by CI.

All advancing metadata updates are now buffered in memory across every enabled journal: current-page resume, next-page cursor, processed count and completed-window checkpoint. The complete normalized output validates and atomically replaces the prior package before any of those buffered states are saved. A failed output/validation leaves the previous output and old progress unchanged, apart from the explicitly nonadvancing first anchor. A subsequent state-write failure is reported; already-persisted bibliography remains available and old progress replays safely.

Checkpoint-based windows use a fixed checkpoint minus fourteen days. They no longer narrow when a retry occurs substantially later. Existing resume bounds remain exact. The focused tests include both old and recent checkpoints, including October 16 checkpoint → October 17 failed output → November retry recovering an October 4 article; capped 101-item pagination; interrupted second page; output validation failure; two journals; first-ever output failure; anchor write failure and output-success/state-failure recovery. These tests passed in this QA's direct execution of the full suite.

## CI publication boundary and independent integration fixture

Reviewed the actual workflow rather than only a helper: authoritative public state restore → shared anchor preparation → guarded bootstrap-state save against acknowledged feed A → discovery/output B → compact-only feed commit/push → guarded final state save. Bootstrap failure stops discovery. Feed push failure prevents the final state step. Collection failure retains its failed outcome and is not converted into successful collection by a later build.

The actual `paper_state.save` checks the explicit feed ref/commit/library SHA-256 against local output bytes, committed blob bytes and origin's advertised exact ref. It rejects unpublished local B, a wrong ref/commit/hash and stale acknowledgments before touching the state branch. The state snapshot records the verified feed provenance. Existing newer-run rejection and force-with-lease remain; same-run bootstrap A then final B is supported. Restore discards cached advancing checkpoints absent from the durable index while preserving archive bytes.

Independently authored and executed a temporary, nonrepository fixture against the actual processor and actual Git persistence code. It used two journals with 101 bibliography-only articles each and a real local bare Git origin:

1. Prepare original October replay anchors and save them against already-pushed feed A.
2. Fail only the atomic output replacement after discovery. The old output, both anchor bytes and remote state remain unchanged.
3. Run a capped page, producing local B with the first 100 entries from each journal. Reject its actual Git push with a temporary local-remote pre-receive hook. `paper_state.save` also rejects unpublished B and preserves the exact bootstrap-state ref.
4. Delete the entire processor work/cache tree and discard the unpublished feed. Restore only acknowledged A and its durable public anchors.
5. Advance the fixture clock to November 24. Discovery still uses the original October 3–17 bounds, recovers both pages, and exports all **202 discovered DOIs exactly once**, together with the existing bibliography, twelve original reactions/solutions and an appended user paper's title/author/note.
6. Push recovered B, save the final state in the same run and check B's exact provenance. Private PDF/review fixture files never enter the state snapshot or survive restoration from that public branch.

Result: **PASS**, including a real rejected feed push plus complete cache eviction, rather than output-preservation assertions alone. No external publisher request was made.

Preservation scope is explicit: the standalone processor's supplied curated baseline remains authoritative for same-ID starter facts, an unchanged behavior from the parent source. This fixture verifies appended user-record fields and prior reactions/solutions. It does not claim that edits to an older generated feed override the explicitly supplied curated baseline. Personal edits in the web app remain browser-local and are preserved by import/merge, verified separately in Chromium.

## Direct execution and prior repaired contracts

| Check | Result |
| --- | --- |
| `.venv/bin/python -m pytest -q` | **PASS: 273 passed, 1 skipped**, 6.87 seconds. The skip is Windows-only DPAPI, outside this browser milestone. Existing Starlette/httpx deprecation warning only. |
| `CHEMBRAIN_BASE=/chembrain/ npm run build:web` | **PASS**, TypeScript and production repository-subpath build. |
| `.venv/bin/python scripts/web_smoke.py` | **PASS**, actual Chromium molecule-first empty panel, related reactions/stage solutions, deduplicated DOI references, editing/reload/import preservation, 42 malformed-draft render/recovery/cancel/storage cases, actual Python-export import, backup, mobile/subpath assets and no backend API requests. |
| Independent output/capped-feed-push/cache-eviction fixture above | **PASS**, two journals, 202 eventual unique DOIs, retained prior facts/user record and public-state private-file exclusion. |
| Actual workflow and state-save source review | **PASS** for bootstrap/output/feed/state ordering, explicit origin acknowledgement, digest identity and failure preservation. |
| `git diff --check` | **PASS**. |

The four preceding repairs remain resolved. Full-suite execution includes the shared cross-runtime corpus/actual CLI export failures, durable deferred PDF queue/current-license/retry/file reuse regressions, and source/data commit/digest identity regressions. The real browser smoke independently rechecks malformed-editor recovery and processor-to-browser import. The round-03 diff does not change the UI, seed facts, structure assets or browser smoke; the prior factual review of the three papers/twelve draft reactions remains the stated factual scope, with scientific unknowns kept unknown. This is not complete reaction extraction or an assertion of verified experimental conditions.

## Exact-source CI and external/operational limits

This QA independently verified all six retained raw files byte-for-byte against immutable Git receipt **`5829825cf51ea5a5677922886eb1c8575405822e`**, as well as each manifest byte count and SHA-256. See [manifest](web/manifest.json) and [GitHub run 39093753253](https://github.com/chemryu/chembrain/actions/runs/39093753253). The terminal receipt binds workflow and built commits to the exact source `56be43bf15b4c98b8b515d2dc3bbd2bd0fcbbbae`; its library digest `25e98df9810b686e9da2c3c3b3f7f5da627dd2186ab3b00533b28d34072aef8c` matches actual local public-library bytes.

GitHub independently reports **273 passed / 1 Windows-only skip**, production web build PASS and real browser smoke PASS. Collection/feed steps were skipped in this push run; controlled local fault-injection tests above supply collection/failure coverage without activating a schedule. This new run actually receives **HTTP 403 `Resource not accessible by integration`** during Pages configuration. Publish fails; deployment and public HTTPS verification are **SKIPPED / NOT RUN**, not successful. The terminal status is blocked and `page_url` is null. The owner Pages Source setting remains pending. No verified public URL, production release or completed hosted-preview delivery is claimed. The weekly dispatcher remains an unconfigured review artifact, not an installed default-branch schedule. No user-PC scheduled task or Box synchronization was installed. Private PDF/review bytes remain in the separate persistent local processor work directory or best-effort Actions cache, not in the compact public feed/state branch or Pages bundle.
