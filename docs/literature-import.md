# Optional original-PDF import

The desktop app already includes DOI-only versions of the curated examples. Original PDFs are not required to browse the map, inspect reaction conditions, follow paper links or search routes.

For source-based provenance review, place the six original user-supplied files in `papers/`:

- science.1161976.pdf
- nicewicz.som.pdf
- science.1255525.pdf
- zuo.sm.pdf
- nature17431.pdf
- 41586_2016_BFnature17431_MOESM219_ESM.pdf

With the API running, execute `.venv/bin/python scripts/import_literature.py` (Windows: `.venv\Scripts\python.exe scripts\import_literature.py`). Override `--base-url`, `--attachments-dir` or `--manifest` when needed.

Before any API write, the importer checks each file's SHA256, extracted evidence quotes, molecular formulas and specified CIP configurations. Repeated imports reuse original-file records and preserve user edits. Original files stay in local `.data/uploads`; the interface uses DOI citations and does not display full paper text. Markdown exports omit full text and evidence excerpts.

The portable starter library is DOI-only and has distinct provenance identifiers. To avoid duplicate citations when testing the original-PDF importer, use a separate source-mode database rather than the desktop starter database. Importing original PDFs into the DOI starter database is not a replacement or upgrade procedure.

The curated manifest contains only six representative reactions. Article/SI discrepancies for Nicewicz Table 1 entries 3 and 4 are retained as drafts. Horn compound 6 uses MeCN, while compound 7 uses acetone. Horn's 10 mA/mmol describes current per substrate amount, not electrode-area current density. Zuo's selected examples use Procedure A, not Procedure B.
