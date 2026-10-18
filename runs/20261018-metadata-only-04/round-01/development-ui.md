# Development UI — metadata-only round 01

Working-tree changes based on `56be43bf15b4c98b8b515d2dc3bbd2bd0fcbbbae`; this report is development evidence, not independent approval. Root must freeze the final full source SHA after the other bounded development areas finish.

## Changes

- `src/MolecularLibrary.tsx`: paper references show canonical DOI links and authors only; no title/journal/year display. Initial molecular-library-only behavior, DOI deduplication, browser-only edits and concise reaction/solution/chemical facts remain. Browser startup first validates the new strict data; only the explicit legacy helper may project the four recognized former paper fields away. Before any primary replacement it writes the **exact original raw localStorage bytes**, verifies the backup readback and retains that private backup under a unique local-only key. The migration notice identifies the private key and explains it is excluded from compact exports/GitHub packages. A backup failure leaves the original primary bytes untouched. Unrecognized legacy keys reject. If original data cannot be recovered safely, import/export are disabled until recovery/reload to avoid accidental empty exports or overwriting unrecovered originals. Primary-storage write failure retains original bytes; a successfully backed-up/projected library can still be viewed and exported.
- `src/RecordFields.tsx`: paper form is DOI/authors only, with no paper notes field. Existing rendering-safety checks and malformed-draft recovery remain.
- `scripts/build_total_synthesis.py`, `examples/total-synthesis.json`, `public/library.json`: paper rows have exactly `id`, `doi`, `authors`; generator reproduces strict starter. Chemistry data remains 49 chemicals and 12 explicitly draft reactions; compact starter is 21,675 bytes. No full-text extraction/completeness claim.
- Deleted both `public/structures/paclitaxel.png` and `doxycycline.png`, and removed their `src/seedDepictions.json` entries. Targets without encoded structures now display the existing honest structure-not-encoded placeholder. `public/structures/provenance.json` describes only encoded-SMILES-generated SVGs. SVG files remained byte-identical.
- `scripts/web_smoke.py`: real browser assertions cover DOI/authors-only UI/exports, strict actual Python export to browser import, legacy exact-byte backup and chemistry preservation/reload, private backup exclusion from export, backup/primary persistence failure, invalid legacy/import unknown fields and guarded recovery, absence of copied PNG/PDF artifacts. Existing molecule-first, solution/DOI dedup, malformed editor, persistence, subpath/mobile and no-external-request checks remain.

## Verification

- `.venv/bin/python -m py_compile scripts/web_smoke.py scripts/build_total_synthesis.py` — PASS.
- `.venv/bin/python scripts/build_total_synthesis.py` — PASS; strict normalized 49-chemical/12-reaction starter, no changed SVGs.
- `CHEMBRAIN_BASE=/chembrain/ npm run build:web` — PASS (TypeScript and production Vite build).
- `.venv/bin/python scripts/web_smoke.py` — PASS in real Chromium, including the metadata boundary/migration/storage failure cases above.
- `git diff --check` for owned source/data paths — PASS.

## Retained limits

No commit/push/deployment, scheduling activation, repository visibility change or destructive history rewrite performed by this role. Current-tree crop removal does not remove historical Git blobs. The root audit and independent reviews must qualify historical/remote artifact exposure. Private legacy backups intentionally remain private browser data and can contain former paper metadata. Bounded free-text chemistry labels cannot prove semantic absence of quotations in arbitrary user input. Source PDFs/private candidate work remain outside portable library data; automatic chemistry extraction is not claimed.
