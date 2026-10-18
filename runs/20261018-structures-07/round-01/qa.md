# Independent QA — offline molecular structures

- Run/round: `20261018-structures-07 / round-01`.
- Role: separate Independent QA. No application, data, test, build input/output or source commit was edited by this role; only this report is written. Existing builds were inspected/executed without rebuilding them.
- Exact inspected source: **`b38260d5c0f97a7d7b08711dde178555658df136`**, unchanged after resumption.
- Verdict: **PASS for the bounded downloadable browser preview; zero unresolved material findings.** This approval targets the new source and validated HTML identity below, not a previous run or a Public/production deployment.
- Some independent browser processes were started before the session interruption but their final outputs were unavailable afterward. They were not credited as passed; hosted and portable probes were restarted after resumption. Only observed completion and separately identified CI evidence are credited below.

## Independent scientific identity and provenance checks

Fetched the pinned official RDKit tutorials ChEMBL snapshot directly into memory at review time, without persisting its full contents. Its **830677 compressed bytes** independently matched recorded SHA-256 **`07634c2891a950829204d633a0f8098f9cd9e48c9e0cd888cabdb756e75507e8`**. The exact source ID, source name and source SMILES for each of the two target records matched an actual snapshot row, rather than merely agreeing with a checked-in constant.

Independently parsed those observed source SMILES using Python RDKit and recomputed formula, stereochemical InChIKey, assigned centers, formal charge and fragment count:

| Target / observed source ID | Computed formula | Computed stereochemical InChIKey | Assigned centers | Identity |
| --- | --- | --- | --- | --- |
| Paclitaxel / CHEMBL428647 | C47H51NO14 | RCINICONZNJXQF-MZXODVADSA-N | 11; no unassigned centers | Neutral, one fragment |
| Doxycycline / CHEMBL1433 | C22H24N2O8 | JBIWCJUYHHGXTC-AKNGSSGZSA-N | 6; no unassigned centers | Neutral parent, one fragment |

The manifest correctly separates **observed source ID/name/SMILES** from **locally computed** canonical isomeric SMILES/formula/key/mass/stereocenter checks. The InChIKeys are not misrepresented as registry-observed fields. The cited snapshot's tautomer representation is explicit. Doxycycline's parent structure is distinguished from the paper's hydrochloride/hyclate isolate; the existing reaction note identifying the hydrochloride remains intact.

There are 49 seed chemicals, 10 encoded structures and 39 still unencoded; all 22 paper-numbered intermediates remain unknown and all 12 curated reaction records remain draft. No paper crop, inferred intermediate, guessed stereochemistry or synthetic transformation was added. Reproducible generation was executed in a temporary directory by the independent test subset and agrees with the checked-in normalized chemistry.

## Source and data-preservation review

- `structureRenderer.ts` uses pinned bundled RDKit2026.9.1 JS/WASM, cached by complete current SMILES. It decompresses and explicitly instantiates embedded bytes rather than relying on a CDN, runtime registry, backend or local-file WASM fetch. Parsed RDKit molecule objects are deleted. The cache is bounded; empty, oversized, invalid or unavailable rendering has an explicit result.
- `StructureDiagram.tsx` checks the active input SMILES before showing any prior asynchronous result, cancels obsolete effect results and displays generated SVG through an isolated image URL rather than injecting imported text as HTML. Name changes update alt text without invalidating a valid structure. Invalid or missing inputs have readable fallbacks; unknown paper structures stay unknown.
- The explicit example enrichment is narrow: known ID, exact name, compound kind, missing SMILES and compatible existing identity properties. Existing non-null structures, changed identity, notes, aliases and all other chemistry records retain precedence. The complete candidate is validated before persistence. Original primary bytes are checked against the current in-memory library, saved under a new private backup key and read back before the one primary replacement. Backup/readback/primary-write/concurrent-change failures preserve original primary bytes.
- Normal loading now avoids replacing identical normalized saved data merely to change whitespace. General merge precedence was not reversed. Private browser backups do not enter compact exports or GitHub data.
- Actual diagrams appear in tiles, selected large structure and synthesis nodes. The renderer follows current imported/edited SMILES independently of seed ID/name. Existing map fragment/cycle/cap, pan/zoom/Focus, conditions, DOI/authors-only references, editing, backup/import and browser preservation behavior remain covered.
- RDKit BSD3-Clause notice is in hosted public assets, packaging README and the delivered HTML. Strict normalized JSON has no diagram/base64/SVG fields. Source/distribution payload gates pass.

## Independently executed checks

Environment: retained Python3.12 virtual environment, Node24 and managed Chromium/Playwright; existing checkout only.

| Check | Result | Evidence |
| --- | --- | --- |
| Focused tests | **22 PASS** | `tests/test_verified_structures.py tests/test_web_library_data.py tests/test_portable_contract.py tests/test_repository_payloads.py tests/test_synthesis_graph.py`; actual RDKit corruption/reproducibility and runtime graph/contract tests |
| Actual pinned public chemical snapshot and RDKit identity | **PASS** | Fresh remote digest/exact row match and own formula/key/stereo/charge/fragment computations above |
| Tracked-source payload gate | **PASS: 170 files** | `.venv/bin/python scripts/check_repository_payloads.py` |
| Hosted and portable distribution gates | **PASS: 16 files each** | Both existing distributions independently checked |
| Independent hosted full real-browser suite | **PASS after restart** | `.venv/bin/python scripts/web_smoke.py`; real decoded vector bond paths, targets/selected/map, non-seed stereo/charged/multifragment input, rename/edit/invalid recovery, private upgrade, previous map/editor/storage/security cases |
| Additional renderer-unavailable browser probe | **PASS** | Disabled `WebAssembly` before startup: explicit tile and selected fallback, no stale image, no page error and no storage write |
| Independent portable HTTP-only suite | **RUNNING at initial final-report write** | Restarted after session interruption; final output will be appended. This is not local actual-file evidence. |
| Local managed-browser actual `file://` execution | **NOT RUN** | Administrative file-URL policy retained; no bypass |
| Full suite/build/actual-file verification | **CI PASS, separately identified below** | Not falsely labelled as the independent22-test subset or local actual-file execution |

## Exact-source CI, packaged renderer and artifact identity

Fresh [CI39148232731](https://github.com/chemryu/chembrain/actions/runs/39148232731), immutable terminal receipt **`1df362f303bb14ba60e9e70fe45cf894fce2f866`**:

- Actual workflow and built source are both **`b38260d5c0f97a7d7b08711dde178555658df136`**.
- Actual CI Python **297 PASS / Windows-only DPAPI 1 SKIP**, hosted production build and full browser **PASS**, portable build and **actual offline `file://` browser PASS**. The latter checks real target/selected/map vector drawings, imported stereo/charged/disconnected SMILES, current edits and invalid recovery, private structure upgrade and all retained offline/storage/import/map cases, with zero additional app network/assets.
- Independently compared **all nine retained raw files** with immutable Git objects and their byte counts/SHA-256 in `web/receipt-files.json`. CI `browser-manifest.json` is byte-identical to the local manifest.
- Independently hashed the actual local delivered HTML and library: **5079906 bytes**, HTML SHA-256 **`f5c3137adbe840c0530b10870d231ceae28f7bc534c1228979cb41724f737897`**; library SHA-256 **`7172a3f6970790c5795f074a8861555456eef330648a6591289ded34165df825`**. CI actual-file log states this same source/HTML hash.
- Independently decoded the HTML's embedded JavaScript and verified its manifest hash; located/decompressed the actual embedded gzip-WASM payload and byte-compared it with pinned `node_modules/@rdkit/rdkit/dist/RDKit_minimal.wasm`. It is **7379879 bytes**, SHA-256 **`594ceaed387adc70ea13bfbb2e8eace916f6c782254ed5a6f0f0a0a7a4fe4061`**, matching the manifest. RDKit license text is present in the actual HTML. The first independent extraction pattern assumed quote-delimited output and matched no payload because the minifier used a template literal; widening the inspection pattern to include that delimiter verified the bytes, with no application change.
- Artifact upload **SUCCESS**, ID **`12143773443`**, [download](https://github.com/chemryu/chembrain/actions/runs/39148232731/artifacts/12143773443), CI-reported archive digest **`39b86d57530c38c6c374c989a3e29b06ea566688b0a544e50ce95680cc1dca26`**. **The artifact ZIP was not independently downloaded or rehashed**; the reported archive identity and matching tested HTML identity are stated distinctly.

The fresh CI actually observed Pages configuration **403 `Resource not accessible by integration`**. Deployment/access were SKIPPED/NOT RUN, URL null; collection was skipped. These publishing limits do not change the validated downloadable-file result. Historical quotations/crops in Git, unverified old remote artifact/cache contents, inactive collection, no Box sync, browser profile/file-path storage limits and old synthesis-run CI failure cause remain unchanged separate history. No Public clearance, source/history rewrite, main merge, permissions change or production deployment is approved.

Handoff: **zero material findings for this exact downloadable preview**; separate Revision should compare the complete report and exact evidence, then Wiki preserves both originals and hashes. No approval is transferred to any later source or artifact.

## Independent portable completion supplement

The restarted independent `.venv/bin/python scripts/portable_smoke.py --http-only` completed **PASS** on exact source `b38260d5c0f97a7d7b08711dde178555658df136` and HTML hash `f5c3137adbe840c0530b10870d231ceae28f7bc534c1228979cb41724f737897`. It independently exercised the new real vector/stereo/current-edit/private-upgrade scenarios and all retained offline/map/editor/storage/security cases with additional resources rejected. Local actual `file://` remains NOT RUN; genuine CI actual-file PASS is separately established above. Final preview PASS/zero material findings is unchanged; this report is complete for Revision/Wiki preservation.
