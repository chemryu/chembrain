# Separate paper tools

The install-free **Chembrain-Paper-Workbench.html** is the source-assisted chemistry curation program, separate from **Chembrain.html**, the main molecular library. Open both in current Chrome/Edge. No Python or AI API key is needed for these HTML files. Download both from the same source-bound browser artifact.

Workbench reads a local PDF in memory, previews its pages, suggests explicit text SMILES/DOIs, and provides an offline molecular sketcher or single-record MOL/SDF import. It does not recognize arbitrary scheme drawings automatically. Compare each encoded structure/stereochemistry against the source and confirm its identity, then connect explicit reactants/products and stage-specific solutions. Export facts includes checked rows only; private drafts, original PDFs, text, images and workspace review proofs are excluded. Public paper rows remain ID/DOI/authors only. Undefined stereo and parent/salt form require source review; parser validity is not a scientific match.

For the current missing-chemical issue, use the main app's Backup JSON with **Load library draft** in Workbench, select the paper, complete its structures, solution quantities and recorded stages, source-check the facts, then export. This keeps its original IDs. New paper-local labels get DOI-scoped IDs; qualify distinct repeated labels as main:4/SI:4. In the main app, **Import package → Review paper import → Apply import** previews safe missing structure fields, paper labels, solution quantities/concentration, ordered reaction stages, conditions, yield context and additive source evidence before an exact private backup and one apply. Names, notes, known chemical facts and existing stage order remain protected. Empty stages or an unambiguous complete prefix may receive explicit recorded stages; different known values, roles, memberships or stage order block the whole package. Reconcile the indicated fields using the latest main backup loaded in Workbench; no silent overwrite or relinking occurs. Equivalent alternate SMILES require real graph verification. No incoming-wins feed behavior was introduced.

Use **Save workspace / Backup workspace** for private progress, and **Export facts** for the main library. Reselect the same fingerprinted PDFs after reload. Failed storage/restore/import leaves previous data usable. Neither JSON contains PDF bytes. The user must install or activate a future weekly collector separately; this workbench does not download journals or run on a schedule.

Developer commands: `npm ci`, `npm run dev:paper` then open the local `/paper.html` internally, or `npm run build:paper` for the self-contained file in `release/`. Real `scripts/paper_workbench_smoke.py` verifies actual offline file execution on normal CI, including a real private synthetic PDF and exported JSON consumed by the main app. Managed local file policy is not bypassed; `--http-only` is explicitly only a local same-HTML check.

---

# Separate journal discovery / local CLI processor

The browser and all GitHub publication paths accept only compact chemistry facts and paper DOI/authors. Public paper rows contain `id`, `doi`, `authors`; titles, abstracts, journals, years, source paths, PDF download links and paper prose are not portable metadata. Reactions, chemicals and solutions remain normalized tables with explicit stage conditions and DOI-linked evidence locators. Unknown structures and conditions remain unknown.

GitHub Actions is **metadata-only**. `weekly --metadata-only` queries public journal discovery for DOI/authors; the `GITHUB_ACTIONS` environment independently enforces this even if the flag is omitted. It never reads pending PDF jobs, creates a PDF archive, resolves a license/download link, downloads a PDF or creates private review candidates. Direct `ingest` also refuses to run in Actions. Actions do not cache private processor directories. The durable `build/paper-state` snapshot admits only metadata replay anchors/checkpoints and feed acknowledgment; it rejects old snapshots containing pending provider/PDF work rather than reposting them. Existing historical snapshots and older Actions caches/artifacts require a separate audit/remediation; these code changes do not delete them.

```sh
python -m paper_pipeline weekly --metadata-only --work-dir /private/path/outside/git/state --out library.json
python -m paper_pipeline anchor --config paper_pipeline/journals.json --work-dir /private/path/outside/git/state --out library.json
python -m paper_pipeline export --curated reviewed-package.json --out library.json
```

JACS is enabled in `journals.json`; other journal ISSNs can be configured for public DOI/authors discovery. No model API keys, publisher cookies or university credentials are used. Source processor installation requires Python and `paper_pipeline/requirements.txt`; the browser app needs no Python. The trusted HTTP/chemistry modules remain in this repository.

## Optional private local work

Outside GitHub Actions, a user may separately ingest PDFs or run the local OA resolver. Keep all PDF inputs, archives, review work and backups outside **every Git checkout**, and out of any folder published or synchronized to a public service. The processor refuses a work directory inside this application's checkout; that check is not a universal detector of other Git repositories or cloud-sync folders. Such private directories are never a GitHub upload package.

```sh
python -m paper_pipeline ingest /private/paper.pdf --work-dir /private/path/outside/git/review
python -m paper_pipeline weekly --work-dir /private/path/outside/git/archive --out library.json
```

Local weekly PDF processing supports ACS PDFs only when a current explicit matching OA license and trusted route are verified; other publishers remain DOI/authors-only or accept local files. It does not promise all OA PDFs. Local candidates contain bounded extracted excerpts and filename provenance and **must remain private**. They are not portable library records and are never automatically exported or promoted to reactions. Human curation supplies allowed chemistry facts, DOI and authors. A PDF containing multiple DOI identifiers requires identity review; `--doi` applies only after checking the article. Complex scheme OCR and automatic exact structure extraction are not implemented.

Private local PDF work uses bounded `pending.json` work (2,000 entries / 8 MB; each source at most 32 KB), up to 10 attempts per run and fresh public eligibility checks before downloading. Failed/deferred local work survives metadata overlap; saved files can be processed without redownload. These private source/license/link records are never saved by the public state script. Metadata-only mode ignores even malformed private pending files.

## Durability and scheduling

The processor atomically replaces its validated compact output before writing **any** advancing journal cursor/checkpoint. A failed output preserves old progress and output. A failed later checkpoint save leaves new output available and retries safely replay earlier metadata. On a journal's first run the anchor command records only its original date window, initial cursor, zero processed count and timestamp before discovery; delayed retries preserve this window. Initial discovery uses fourteen days; subsequent windows start fourteen days before the saved checkpoint. A capped page preserves its original end date/cursor. Bounded discovery does not guarantee exhaustive coverage of late-indexed papers; manual backfill may be needed.

CI restores compact public anchors/checkpoints, saves nonadvancing anchors against the already origin-acknowledged feed before discovery, publishes the compact feed, then advances durable state. The state save verifies the exact remote feed ref, commit and library digest; a failed feed push cannot advance durable progress. Full cache eviction therefore does not discard the original metadata replay anchor. A legacy public snapshot containing PDF/provider queue fields fails closed and requires explicit owner remediation.

The optional weekly workflow is Monday 15:00 UTC (09:00 CST / 10:00 CDT). GitHub runs schedules only from its default branch; feature-branch presence does not activate it. No automatic merge, default-branch change or PC task installation is implied. The optional local `scripts/install_paper_schedule.ps1` must be deliberately installed by the user. The reviewed dispatcher document is not installed. Browser imports preserve local edits; there is no cross-device account sync. Raw PDFs and private candidates never belong in GitHub, Pages, Actions artifacts/caches or the compact library.
