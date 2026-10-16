# Chembrain

A local chemistry workspace that connects molecules, reaction conditions and paper citations in an interactive reaction map. The interface and bundled examples are in English. Papers open through DOI links; no full-text reader or paper downloads are needed.

## Windows: double-click to run

Open [Releases](https://github.com/chemryu/chembrain/releases), download **Chembrain-Windows-x64.zip** from a successful Windows build, extract it, then double-click **Chembrain.exe**. This package includes Python, RDKit, the local API and the compiled interface. **You do not need to install Python or Node.js.**

The app opens your browser automatically. Keep the console window open while using it; close that window or press Ctrl+C to quit. Windows 10/11, 64-bit is required. This build is unsigned, so Windows may display a publisher warning.

Your records are saved in `%LOCALAPPDATA%\Chembrain`, separately from the EXE. Keep that folder when updating and back it up to preserve your records. Internet access is only needed when opening a publisher's DOI link.

**Code → Download ZIP** downloads the source code, not the ready-to-run application. The Windows package is created by [Build Windows EXE](https://github.com/chemryu/chembrain/actions/workflows/windows-exe.yml); if no release is available, check that workflow's result. A saved workflow is not proof that an EXE has been built.

## What is included

- An interactive map of molecules and organic, photochemical and electrochemical reactions.
- RDKit-validated SMILES, stereochemical identifiers and molecular structure drawings.
- A paper library with DOI links, citations, reference notes and linked reactions. Add new papers by DOI without uploading PDFs.
- Reaction records with method-specific conditions, yields and page/figure/procedure locators. New DOI citations record manual review; they do not claim an automatic text match.
- Bounded route search that retains all reactant branches and excludes drafts by default.
- Markdown export with ID-based backlinks and DOI citations. Full paper text and source excerpts are omitted.

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

The workflow builds on `windows-latest` using Python 3.12 and Node.js 24, installs hash-locked application dependencies, builds the UI, runs the API tests, packages a single EXE with PyInstaller and runs that EXE's functional smoke test. Only a passing build publishes the Windows ZIP and checksum file to GitHub Releases. An Actions artifact is also available for 30 days.

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
npm run build
.venv/bin/python scripts/desktop.py --smoke-test
python3 scripts/browser_smoke.py
```

The browser smoke test needs Playwright and a Chromium installation; `CHROMIUM_PATH` can override its executable path.

Original PDF ingestion is still available to the import tools for evidence verification. It is optional and is not included in the desktop package. See [literature import](docs/literature-import.md) for preserving original-file provenance.
