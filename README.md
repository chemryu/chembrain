# Chembrain browser preview

## Open the updated program

The download now contains **two independent programs**: **Chembrain-Paper-Workbench.html** for private PDF/source checking and chemistry preparation, and **Chembrain.html** for the main molecular/route library. Workbench has a local PDF viewer, offline sketcher/MOL import, real RDKit identity/stereo checks, explicit source confirmations and recorded reaction/stage editors. Export checked facts, then use the main app's Import package and explicit review/apply for missing structures. Load an existing main Backup JSON as a Workbench draft to preserve IDs when correcting blank intermediates. Original PDFs, extracted prose and private workspace proofs never enter the compact handoff. It is source-assisted curation; exact image-to-structure OCR is not implemented. See [paper tools](paper_pipeline/README.md).

The normal app now opens the molecule-first browser library. Clicking a molecule opens its branching **Map**: recorded molecules connect through reaction steps, with arrows showing synthesis direction. Drag the canvas to pan, use zoom/Fit controls, and click a reaction to inspect its conditions, solvents/solutes, yield and DOI reference. Click another molecule node to explore its synthesis context. **List** keeps the existing reaction cards and editing workflow. Separate recorded fragments remain separate when intervening transformations have not been curated; target tags do not create reaction arrows. Layout exploration is not saved as chemistry data. No Python backend or AI API key is needed for this interface.

For a ready-built download, open the latest successful build for this branch in **GitHub → Actions → Publish Chembrain browser preview**, then download the **Chembrain-Browser-<source SHA>** artifact. Extract it and double-click **Chembrain.html** in Chrome or Edge. Python, Node.js and a local server are not required to open this file. The file is an explicitly labelled preview; it works offline, and DOI links open online when clicked. An artifact build can succeed while the separate Pages publishing job is blocked.

Edits stay in the current browser. Keep the file at the same filename/location and use **Backup JSON before moving, replacing or updating it**; open the new file and use **Import package** to transfer your saved data. File-URL storage depends on browser/privacy settings, so keep exported backups. The standalone file uses its bundled data; weekly updates are imported as normalized packages.

For source development, install Node.js 24, then run `npm ci` and `npm run dev`. A standard `npm run build` or `npm run build:web` creates the hosted browser app in `dist`. To generate the single-file download yourself, run `npm run build:portable`; the result is `release/Chembrain.html` with a SHA-256 manifest and README. The explicit `npm run build:desktop` / `npm run dev:desktop` commands retain the earlier API-backed desktop interface. `scripts/setup.*`, `scripts/start.*` and `scripts/dev.sh` are legacy desktop helpers requiring Python.

This download does not enable GitHub Pages or change repository visibility. The known historical quotations/images remain a separate concern before making the existing repository Public.


Current paper-data boundary: GitHub receives only normalized reactions, chemicals, solutions (solvents/solutes), DOI and authors, plus internal linking/curation fields. Paper records have only id, doi and authors. Full PDFs, extracted prose, quoted procedures, paper-derived images and private review candidates are excluded. GitHub Actions collects metadata only and cannot ingest/download papers; private paper-work Actions caches are removed. Local PDF processing remains separate, outside Git checkouts, and must not be copied into GitHub.

The current reachable Git history contains earlier prose quotations and two paper-derived crops even after their current files are cleaned. No PDF blobs were found in the fetched-head audit. A clean current branch does not erase old commits or remote Actions artifacts/caches; do not infer that making the existing repository Public would expose only the current data. See [data boundary](docs/data-boundary.md).


The current app starts with only the molecular library. Select a molecule to open its recorded synthesis Map. Switch to List for direct reaction cards and the optional synthesis-route filter. There is no initial all-reactions/category panel. Edits are stored in the current browser, with JSON backup/import and no account sync. The app uses no AI API key or Python runtime in the browser.

The starter contains three uploaded total-synthesis papers and 12 draft curated reaction records. Numbered intermediates remain paper-specific; unknown SMILES/stereochemistry, amounts, concentrations and unreported conditions stay empty. Only structure SVGs generated from encoded SMILES are included. Verified parent structures for Taxol and doxycycline are included with source attribution. The bundled offline RDKit renderer draws any valid current SMILES in tiles, the selected molecule and map nodes, including imported/edited molecules. Unencoded paper intermediates show an honest placeholder; source-paper crops were removed. Older matching saved examples can use **Add verified example structures**, which first makes an exact private browser backup and keeps other edits. Full PDFs and page text are excluded. Stage-specific solutions, multi-step yields, salts and uncertain ranges retain their context. These draft facts are not full substrate scopes or independently reproduced procedures.

`npm ci` then `CHEMBRAIN_BASE=/chembrain/ npm run build:web` builds the static Pages app; `scripts/web_smoke.py` checks its real browser workflows at the repository subpath. The Pages workflow builds/tests, publishes an explicit preview and verifies its workflow source, actual built-data commit and exact library SHA-256 over HTTPS. A URL is not considered live merely because a workflow was created. A repository/account Pages restriction may require its owner to enable Actions-based Pages in Settings → Pages. No personal token is requested.

The **separate** [paper processor](paper_pipeline/README.md) supports metadata-only weekly runs on GitHub Actions and separate private local PDF processing. Local processing may archive supported OA papers and create private candidates; only reviewed normalized information is exported as `papers`, `chemicals`, `solutions`, and `reactions`. JACS is the enabled default; additional ISSNs are configurable. Other publisher PDFs require an appropriate supported resolver or local ingestion; subscription credentials are not automated. Public metadata updates are separate from reviewed chemical extraction. Raw paper archives/review text never enter Pages. The schedule is Monday 15:00 UTC (09:00 CST / 10:00 CDT), but GitHub only activates it after the workflow is installed on the default branch. No main merge was made. A fail-closed dispatcher design is in `docs/weekly-dispatcher.yml`; it is a review artifact with an intentionally unconfigured approved-source placeholder, not an installed schedule. The local Windows installer is an alternative that the user must run explicitly.

Separate GPT Planning, Development, Independent QA, Revision and Wiki roles operate within the active Codex task without personal AI API keys. After the earlier usage reset, the same independent roles resumed and found four issues in the first web candidate; the next candidate repairs them and requires new exact-source reviews. Old reports and approvals are retained for their own commits only. Hosting success and code-review approval are separate. The legacy desktop build remains available via manual Windows workflow, but it is not the current delivery target.

---

## Legacy desktop documentation

# Chembrain

A local chemistry workspace that connects molecules, reaction conditions and paper citations in an interactive reaction map. The interface and bundled examples are in English. Papers open through DOI links; no full-text reader or paper downloads are needed.

Development now uses a [GPT-only, five-role review workflow](README-GPT.md) within Codex. No external AI API key is required. Current review records are maintained in the [workflow wiki](https://github.com/chemryu/chembrain/blob/codex/gpt-workflow-records/wiki.md), separately from the exact source commit being tested.

## Windows: review candidates

Windows builds on this branch are **review candidates**, not approved releases. The old `windows-3` release has a known ordinary-startup bug and must not be treated as the validated output of the current branch.

[Validate Windows EXE](https://github.com/chemryu/chembrain/actions/workflows/windows-exe.yml) builds and tests the EXE, then retains a commit-specific Actions artifact and checksum for independent review. It does **not** publish a GitHub Release. A new release is held until independent review is complete.

An approved package is intended to run by extracting its ZIP and double-clicking `Chembrain.exe`. It bundles Python, RDKit, the API and the compiled interface. Data is stored separately in `%LOCALAPPDATA%\Chembrain`; updating the EXE must preserve that folder. Keep the console open while using the app.

Current automated validation checks ordinary zero-argument startup, a captured browser-open request, browser interactions against the packaged EXE and a real restart using existing user data. The EXE also runs with Python/Node launchers removed from its PATH. **That is not a clean Windows VM test**; clean-machine validation and the normal system-default browser integration remain separate checks. The shell browser probe prevents unrelated Edge profile locks; Playwright checks the actual UI independently.

## What is included

- An interactive map of molecules and organic, photochemical and electrochemical reactions.
- RDKit-validated SMILES, stereochemical identifiers and molecular structure drawings. Molecules support name, alias, inventory and note editing; structures already used in reactions cannot be replaced in place.
- A paper library with DOI links, citations, reference notes and linked reactions. Add new papers by DOI without uploading PDFs.
- Reaction records with method-specific conditions, yields and page/figure/procedure locators. New DOI citations record manual review; they do not claim an automatic text match.
- Bounded route search that retains all reactant branches and excludes drafts by default.
- Markdown export with ID-based backlinks and DOI citations. Original PDF page indices, printed pages and unspecified numbering are distinguished. Full paper text and source excerpts are omitted.
- Reaction references are grouped by normalized DOI: a paper's main article and SI appear in one card with all individual evidence locations retained. Editing and original records keep their separate provenance.

## Weekly JACS collection

Open **Paper library → JACS weekly collection** to collect Journal of the American Chemical Society articles. **Collect now** fetches public Crossref bibliography, checks normalized DOIs against existing references and preserves user edits. The first run covers the previous 14 days of publication; later runs overlap the previous collection window and catch up after missed runs. Bounded pagination resumes on the next collection when necessary. No chemistry record is automatically marked reviewed.

Only PDFs with a currently effective, recognized Creative Commons/public-domain license and matching ACS PDF metadata are downloaded. A PDF link alone is insufficient. Every PDF redirect must retain the selected article DOI on a supported ACS PDF route. Downloads are limited to 30 MB and 400 pages, and their license dates, version and supplied PDF link are retained locally for audit. This conservative policy can leave some open papers without a downloaded file when metadata or a supported link is absent. Subscription PDFs are not fetched using your institutional entitlement. Use **Open DOI** on your campus network or VPN to access those papers normally. No campus credentials, AI API key or publisher cookie is requested.

PDFs are saved separately in `%LOCALAPPDATA%\Chembrain\jacs_pdfs`; attaching them does not replace original documents or alter citation page numbering. The app continues showing DOI links rather than full papers. Network failures and incomplete collections appear in the panel and retain retry/checkpoint state. If older library records contain duplicate main/unspecified sources for a DOI, collection reports their retained IDs and selected source separately from errors; it does not merge or delete them.

In the Windows EXE, enable **Weekly collection**, choose the day/time and click **Save weekly schedule**. The default is Monday 09:00 in your PC's local time. A current-user Windows task runs a stable copy of the EXE without opening the app UI. Keep the PC on, online and logged in; missed runs are configured to start when available, and simultaneous collectors are prevented. Disable the checkbox and save to remove the task. Nothing is installed on your PC merely by generating this package in the cloud.

For a one-time command-line collection without opening the app:

```powershell
.\Chembrain.exe --sync-jacs
```

`--metadata-only`, `--days 7` and `--max-pages 1` support bounded metadata inspection/backfill. Public-provider availability and actual downloads from your PC remain distinct from fixture tests; CI retains a separate public metadata connectivity observation, never treating an unavailable provider as a successful live download.

The desktop app starts with **14 molecules and 6 representative reactions from 3 papers**. Four records are reviewed; two Nicewicz entries remain drafts because article and SI yields disagree. This is partial assisted curation, not independent experimental reproduction or a complete substrate-scope database. Inventory and purchasing status are unknown.

| Paper | DOI |
| --- | --- |
| Nicewicz & MacMillan, Science (2008) | [10.1126/science.1161976](https://doi.org/10.1126/science.1161976) |
| Zuo et al., Science (2014) | [10.1126/science.1255525](https://doi.org/10.1126/science.1255525) |
| Horn et al., Nature (2016) | [10.1038/nature17431](https://doi.org/10.1038/nature17431) |

## Run from source

Source development requires Python 3.12 and Node.js 24 LTS. Use the existing checkout; no extra worktree is needed.

Windows PowerShell:

```powershell
.\scripts\setup.cmd
.\scripts\start.cmd
```

Linux/macOS:

```sh
bash scripts/setup.sh
bash scripts/start.sh
```

Open the local address printed by the server. Source mode starts with illustrative demo data on first run. To start with the PDF-free literature library instead, run:

```sh
.venv/bin/python scripts/desktop.py --data-dir .data-desktop
```

Windows source-mode equivalent:

```powershell
.venv\Scripts\python.exe scripts\desktop.py --data-dir .data-desktop
```

`CHEMBRAIN_DATA_DIR` overrides source-mode storage; `CHEMBRAIN_PORT` overrides the source startup port. Desktop mode chooses a free local port automatically. Existing records and uploaded originals are preserved. Exact original sample strings are migrated to English; custom titles and notes are retained.

For UI development, `bash scripts/dev.sh` runs Vite and the API together. No external AI service or API key is required.

## Build a Windows EXE

The workflow builds on `windows-latest` using Python 3.12 and Node.js 24, installs hash-locked application dependencies, builds the UI, runs the API tests, packages a single EXE with PyInstaller and runs both its functional smoke test and an ordinary zero-argument EXE launch. The smoke test includes a collector fixture in temporary storage, checking licensed-PDF provenance and repeat-import behavior without accessing a publisher. It exercises the packaged UI using Playwright, then restarts the EXE over the same default data folder and compares all records. Passing candidates and their checksums are retained as Actions artifacts for 30 days; no release is published automatically.

To build locally on Windows after source setup:

```powershell
.venv\Scripts\python.exe -m pip install pyinstaller==6.16.0
.venv\Scripts\python.exe -m PyInstaller packaging\chembrain.spec --noconfirm --distpath release
.\release\Chembrain.exe --smoke-test
```

PyInstaller must run on the target OS. Building the Linux package does not validate the Windows binary.

## Validate

```sh
.venv/bin/python -m pytest -q
npm run build:desktop
.venv/bin/python scripts/desktop.py --smoke-test
.venv/bin/python scripts/check_desktop_launch.py .venv/bin/python scripts/desktop.py --no-browser
python3 scripts/browser_smoke.py
```

The browser smoke test needs Playwright and a Chromium installation; `CHROMIUM_PATH` can override its executable path.

Original PDF ingestion is still available to the import tools for evidence verification. It is optional and is not included in the desktop package. See [literature import](docs/literature-import.md) for preserving original-file provenance.
