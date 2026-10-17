# Development — web round 02

Frozen source: `d423c718ca3c0b7d1dd090a362ba02990d7e223a` (parent rejected web source `e424b34653fb96b911f5ee5708286c92baddfe5f`). Root coordinated Development and implemented CI/state/provenance; separate Development helpers implemented editor, contract and queue repairs. No Development author supplies final approval.

The complete round-01 QA/Revision → Wiki handoff was published in records commit `128c3fca84fbc222043c5aaaddcc126bcc62c172` before separate Planning wrote this round's plan. Detailed helper handoffs are preserved as development-editor.md, development-contract.md and development-queue.md.

## Four repairs

1. Editor parse/render shape guards retain malformed raw drafts and a useful error without unmounting the app. The same structural guard precedes save; full scientific/referential validation remains save-time so unfinished normal form fields stay editable. Real Chromium covers 42 malformed drafts across chemicals, papers, reactions and solutions, correction, rejected save, cancel/reopen and exact persisted-data preservation.
2. Python/TypeScript portable v1 validation shares strict required fields/explicit-null rules, nested types, numeric/text/date bounds, and document-body exclusion. Normalization still deduplicates/remaps known structures and DOI sources without inventing values. A common 195-case mutation corpus exercises actual Python export, Node validation/import and failure-preservation; real Chromium imports a Python-exported new paper while preserving all existing edited rows.
3. Private bounded pending DOI work persists separately from metadata checkpoints, retries after the publication overlap, revalidates current DOI/journal/OA evidence, counts failed work against the attempt bound and retries failed local review creation without downloading a verified PDF again. Controlled tests cover 11 items → 10+1 on two dates, failures, revoked/expired license, wrong DOI and queue saturation. The CI route additionally restores/saves public DOI queue/checkpoint metadata to `build/paper-state`, so cache eviction cannot erase pending work. Only whitelisted source metadata/state goes to that branch; PDF/review bytes remain outside it and outside Pages. Their Actions cache is best effort, not a permanent document archive; persistent local storage is required for long-term raw PDFs.
4. Workflow identity records immutable trigger/workflow SHA, actual post-collection built commit and exact public/library.json SHA-256. Build outputs pass that identity to publish/HTTP/terminal jobs. A later fresh checkout cannot replace the built commit. Controlled real-Git A→data-B receipt tests verify terminal preservation and reject stale marker/wrong library bytes/unreviewed code changes.

Current docs now record normal post-reset independent roles and the first candidate's four findings rather than a stale current usage block. Original frozen preparation snapshots and complete reports remain unchanged. `docs/weekly-dispatcher.yml` is a fail-closed, intentionally unconfigured review artifact only; it is NOT installed/active, does NOT merge the app and does NOT bypass the Pages 403.

## Checks actually run

- Full Python suite: **253 passed, 1 skipped**, Windows-only DPAPI skip; existing Starlette/httpx deprecation warning only.
- `CHEMBRAIN_BASE=/chembrain/ npm run build:web`: **PASS**, TypeScript and Vite.
- `.venv/bin/python scripts/web_smoke.py`: **PASS**, real Chromium; all prior molecule-first/DOI/stage/persistence/backup/mobile/subpath/no-backend flows plus malformed editor recovery and actual Python-export import.
- Focused portable corpus **195 cases** inside the new tests; queue file **17 tests PASS**; real-Git state/provenance tests **PASS**.
- Compile checks, git diff --check and YAML parsing of actual workflow + dispatcher artifact: **PASS**. PyYAML was a temporary external validation tool, not added to application requirements.

New exact-source GitHub CI/publish evidence is pending at this handoff. The prior e424 run's 403 is retained as historical actual evidence, not assumed to be the outcome of this source. Owner Pages Source-setting response is pending; no actual public URL or HTTP success is claimed. Weekly activation remains unfinished while the dispatcher is only an artifact. No user-PC task, Box synchronization, model API keys or automatic reviewed chemical extraction is claimed.

## New source-bound CI observation

Run https://github.com/chemryu/chembrain/actions/runs/39063636131 reached an authoritative terminal receipt `4fb229121ebd4597c51bae7dec30cf37dc759d61` for exactly `d423c718ca3c0b7d1dd090a362ba02990d7e223a`. Build result success: tests **253 passed / 1 skipped**, production web build and full Chromium smoke PASS. Workflow/built commit both equal d423 in this non-collection run; library SHA-256 `25e98df9810b686e9da2c3c3b3f7f5da627dd2186ab3b00533b28d34072aef8c` is retained through final reporting. Code A/data B behavior was exercised by controlled real-Git tests rather than misrepresented as live collection.

New actual Pages configuration result is HTTP **403** `Resource not accessible by integration`. Deployment and public HTTP verification are **SKIPPED / NOT RUN**, URL null. The new result is not inferred from the prior run. Original byte-exact receipt files with SHA-256/byte manifest are preserved in `web/`; independent agents received the actual evidence. The owner-setting answer is still pending; no public availability or weekly activation is claimed.
