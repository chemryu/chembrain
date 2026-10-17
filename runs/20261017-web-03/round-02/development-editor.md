# Development — editor repair

- Role: Development, bounded WEB-QA-01 / WEB-REV-01 repair.
- Base source: `e424b34653fb96b911f5ee5708286c92baddfe5f`; this is a working-tree check, not approval of the not-yet-frozen round-02 source.
- Changed only `src/RecordFields.tsx`, `src/MolecularLibrary.tsx`, `scripts/web_smoke.py` and this handoff.

`parseRecordDraft` now checks only the structural shapes used by the structured form before rendering or attempting a save. Malformed root objects, aliases/authors arrays, participants, steps/solutes and their rendered nested fields produce a field-specific error without changing the exact advanced JSON draft. The editor shell, raw text, save and close controls remain available. Ordinary unfinished fields retain their form controls; full schema/reference/scientific validation still happens only on save. Correcting a draft or closing the editor clears stale save errors. Saving remains atomic through the existing library validation and browser persistence path.

Actual Chromium regression covers 42 syntactically valid but malformed drafts across all four record kinds, including null/array/primitive roots, null/non-array list fields, primitive/null nested entries, and malformed rendered scalar values. Each attempted save leaves storage byte-for-byte unchanged and retains the dialog/raw draft. Alternating correction/save and cancel/reopen recover without losing stored data. Syntax errors and a temporarily blank ordinary molecule name also recover. Existing initial-empty-panel, DOI grouping, solution display, reload/import preservation, backup, repository-subpath, mobile and no-external/backend-request checks still pass.

Checks performed after these owned edits:

- `CHEMBRAIN_BASE=/chembrain/ npm run build:web`: PASS (TypeScript and Vite).
- `.venv/bin/python scripts/web_smoke.py`: PASS (real Chromium, zero page errors).
- `python -m py_compile scripts/web_smoke.py`: PASS.
- `git diff --check -- src/RecordFields.tsx src/MolecularLibrary.tsx scripts/web_smoke.py`: PASS.

Root will repeat required final checks after other bounded Development changes are complete and freeze a new SHA for independent QA/Revision. No approval, commit, push or publication was performed by this Development agent.
