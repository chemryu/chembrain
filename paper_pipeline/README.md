# Separate paper processor

The web library never downloads or stores PDFs. This Python program collects public bibliography by journal, archives only explicitly licensed supported OA PDFs, and creates local review candidates. It uses no model API keys or institutional cookies. JACS is enabled; edit `journals.json` to add journal ISSNs. ACS article PDFs are the supported automatic resolver; other publishers remain DOI-only or accept locally supplied PDFs. It does not promise all OA PDFs.

```sh
python -m paper_pipeline ingest path/to/paper.pdf --work-dir /path/outside/site/review
python -m paper_pipeline export --curated reviewed-package.json --out library.json
python -m paper_pipeline weekly --work-dir /path/outside/site/archive --out library.json
```

Install `paper_pipeline/requirements.txt` for the source processor; its trusted HTTP/chemistry modules live in this repository. The browser app needs no Python. Uploaded multi-article PDFs may contain unrelated DOIs: `charest2005.pdf` contains both an adjacent article DOI and `10.1126/science.1109755`; review identity rather than picking the first match. Use `--doi` only after checking the relevant article.

Candidates are not reaction records. A human encodes scheme participants, stereochemistry, authors, stage-specific solvents/solutes and evidence into the portable v1 tables. Missing amounts/concentrations/SMILES stay null. Scheme OCR and automatic exact structure extraction are not implemented. `examples/total-synthesis.json` is a draft curated starter from the supplied main papers; SI/procedures and complex structures still need review. Salt isolates and multi-step yields are recorded as notes, not silently treated as free-base/single-step results.

Only `papers`, `chemicals`, `solutions`, and `reactions` enter the exported package. Papers deduplicate by canonical DOI; known structures by canonical isomeric SMILES/InChIKey; unknown numbered intermediates remain namespaced to their paper. No PDF text, figures, binary payloads or review candidates may be embedded. The web app validates imports, keeps existing edits, and exports compact backups.

The optional GitHub weekly workflow is scheduled for Monday 15:00 UTC (09:00 CST / 10:00 CDT). GitHub only activates scheduled workflows from its default branch: the schedule is not active merely because this feature branch was pushed. No automatic merge/default-branch change was made. Alternatively install a weekly task locally with `scripts/install_paper_schedule.ps1`. Raw archives are not published to Pages. Public bibliography updates may be published with the site; draft reaction candidates are never auto-promoted. A page-bound or provider failure retains the checkpoint and reports a partial collection; late-indexed older papers can require manual backfill. This is weekly bounded discovery, not a guarantee of exhaustive coverage. The main app imports updates while preserving browser edits; it has no cross-device account sync.
