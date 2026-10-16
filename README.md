# Chembrain

A local chemistry workspace that connects molecules, reaction conditions and paper citations in an interactive reaction map. The interface and bundled examples are in English. Papers open through DOI links; no full-text reader or paper downloads are needed.

Development now uses a [GPT-only, five-role review workflow](README-GPT.md) within Codex. No external AI API key is required. See [wiki.md](wiki.md) for the current paused state and unresolved review finding.

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

The workflow builds on `windows-latest` using Python 3.12 and Node.js 24, installs hash-locked application dependencies, builds the UI, runs the API tests, packages a single EXE with PyInstaller and runs both its functional smoke test and an ordinary zero-argument EXE launch. It exercises the packaged UI using Playwright, then restarts the EXE over the same default data folder and compares all records. Passing candidates and their checksums are retained as Actions artifacts for 30 days; no release is published automatically.

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
.venv/bin/python scripts/check_desktop_launch.py .venv/bin/python scripts/desktop.py --no-browser
python3 scripts/browser_smoke.py
```

The browser smoke test needs Playwright and a Chromium installation; `CHROMIUM_PATH` can override its executable path.

Original PDF ingestion is still available to the import tools for evidence verification. It is optional and is not included in the desktop package. See [literature import](docs/literature-import.md) for preserving original-file provenance.
