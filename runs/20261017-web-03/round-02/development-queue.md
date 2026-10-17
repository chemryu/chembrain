# Development — weekly pending queue repair

Development working tree for round-02; final source SHA is assigned by root after freeze. This is implementation evidence, not independent approval.

Owned changes: `paper_pipeline/__main__.py`, `tests/test_paper_pipeline.py`, queue-specific paragraph in `paper_pipeline/README.md`.

- Known supported work is atomically persisted in private journal `pending.json` before metadata cursor/checkpoint advancement. Queue limits: 2,000 entries / 8 MB, 32 KB source metadata per item. A saturated queue retains the current discovery page instead of losing later eligible work.
- Stored public source identity includes DOI/type/ISSN/title/authors and complete license/link evidence. It is provenance rather than authorization: old pending work refreshes its DOI through the existing allowlisted public Crossref gateway and rechecks DOI, journal, current license/version and trusted PDF route before any fetch. Publisher, redirect, byte and page bounds remain unchanged.
- At most 10 pending work attempts per run, including failed refresh/download/review stages; failures rotate to avoid permanent starvation. Deferred and failed work remains independent of metadata date windows and checkpoint advancement. Reports separate metadata and download completion, pending/deferred/attempted/saved/reused/review outcomes.
- Verified saved files are reused; a failed review-creation stage remains pending and reprocesses the local PDF without redownloading it, even outside the publication overlap. Weekly review paths are DOI-specific so identical PDF bytes under distinct article identities do not overwrite each other's review metadata.
- No archive PDF, review candidate or local path enters the compact export. No institutional authentication, additional publisher support, model API or automatic chemistry verification was added.

Executed: `.venv/bin/python -m pytest -q tests/test_paper_pipeline.py` → **17 passed** (1.20 seconds); `compileall` and `git diff --check` passed. The 8 new controlled test cases cover 11 eligible works saved 10+1 across two dates, failed-attempt bound and recovery, revoked/expired/mismatched DOI/provider-failure fresh retries, saved-PDF review retry and queue saturation. They make no real publisher requests.

Local work-directory persistence is required. An evictable Actions cache alone does not guarantee durable pending/archive storage; root is evaluating a public-metadata-only Git state channel separately. Completed PDF archives themselves still require retained private storage. This subtask did not activate any scheduler, change GitHub settings, commit or push.
