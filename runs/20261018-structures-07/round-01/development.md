# Development — current molecular structures

Exact frozen and pushed source: `b38260d5c0f97a7d7b08711dde178555658df136` on `codex/gpt-agent-workflow`. Baseline `02d0dff2ce66a00f10e0c873baea80fa6f94e963` remains historical approval only. Root coordinates Development; separate Planning, renderer and chemical-data Development helpers were used; QA/Revision cannot edit application source.

## Change and purpose

The old display only matched eight exact seed ID/name/SMILES manifest entries. It could neither draw the unencoded targets nor newly imported/edited SMILES. `src/structureRenderer.ts` and `StructureDiagram.tsx` now render the current full SMILES with pinned bundled `@rdkit/rdkit@2026.9.1`. Gzip/base64 WASM is embedded at build time; explicit WebAssembly instantiation avoids the package fetch fallback. No app-runtime CDN, backend, registry or WASM asset request. Full-input bounded 64-entry cache, released RDKit molecule handles, invalid/missing/unavailable messages and render-time stale-input protection prevent misleading images. Safe data-image SVG is used rather than injected HTML. Tiles and map nodes use this component; the selected molecule has a readable large drawing. Renaming preserves its structural diagram; changed SMILES derives a new drawing. Unknown numbered intermediates stay explicitly unencoded.

`examples/verified-structures.json` records only two chemical structures, immutable official RDKit tutorial ChEMBL snapshot attribution/hash and separate source-observed vs locally computed fields. Paclitaxel CHEMBL428647 and doxycycline CHEMBL1433 retain complete assigned stereochemistry, expected formula/InChIKey, neutral charge and one fragment. These are the cited snapshot parent/tautomer representations, not paper intermediate reconstruction. Doxycycline's existing hydrochloride-isolate reaction note stays unchanged. Reproducible generator verifies the facts before output. Seed is 49 chemicals, 10 encoded (two new targets plus eight existing), 22 paper-numbered intermediates remain null; all 12 draft reactions, solutions, papers and other 47 chemicals are preserved. Generated SVGs are chemical drawings, never paper crops. Papers still have only id/DOI/authors.

`verifiedExamples.ts` implements explicit Add verified example structures for old matching targets with missing/empty SMILES. Exact name/kind and compatible formula/key/mass are required; non-null structures, changed identities, notes, aliases, other chemistry and citations are retained. It validates the whole next library, rejects a changed primary library, saves and verifies exact original bytes under a new private browser backup key, then performs one primary write. Backup/readback/primary failure leaves original primary bytes untouched. Loading an otherwise identical modern library no longer rewrites its whitespace. Existing narrow legacy migration still writes only after backup. General saved-edit import precedence is unchanged.

Packaging includes RDKit BSD notice both inside HTML and accompanying README, plus hosted distribution notice. Artifact manifest records renderer package/version/WASM hash as well as source/library/HTML hashes. Portable size is about 5.08 MB (5,079,906 bytes), including the offline engine. README, RULEBOOK, current request and agent instructions describe the bounded feature. No new schedule, main merge, repository visibility/history operation, Box sync or production release.

## Verification on exact source

All eight commands in `local/checks.json` exited zero; full logs retained in `local/`:

- Python: 297 PASS, 1 Windows DPAPI SKIP. New checks validate true stereo/formula/key identity, reject corrupted stereo/formula/key/salt data, and reproduce the generator twice.
- Subpath hosted build + full real-browser smoke: PASS. Actual decoded vector bond geometry in target/selected/map drawings; new nonseed stereo/charged/3-fragment import; rename; opposite stereochemistry changes SVG; invalid/empty input removes stale image; edit/reload/backup/reimport and mobile; old-example success/identity mismatch/non-null preservation/concurrent change/backup and primary-write failures. Existing map branches/gaps, pan/zoom/Fit/live mobile Focus, List, DOI-only details, all editors and strict metadata/storage regressions retained.
- Portable build + offline in-memory HTTP same-HTML smoke: PASS. This local check explicitly does not establish file:// because managed local Chromium blocks it; policy was not altered or bypassed.
- Tracked source, hosted dist and portable dist document-payload gates: PASS.

GitHub Actions run `39148232731` independently executed the exact source: tests, hosted build/browser, portable build and actual file:// offline smoke PASS. The actual file check rejects every extra resource request and exercises the same real structure tests and legacy map/edit/storage regressions. Immutable terminal receipt `1df362f303bb14ba60e9e70fe45cf894fce2f866` is copied byte-for-byte to `web/` (nine raw files); `web/receipt-files.json` records hashes. Overall workflow status is blocked only by separate Pages configuration HTTP403 “Resource not accessible by integration”; deploy/public HTTPS remain NOT RUN, not live.

## Artifact identity

- Download: https://github.com/chemryu/chembrain/actions/runs/39148232731/artifacts/12143773443
- HTML: 5,079,906 bytes; SHA-256 `f5c3137adbe840c0530b10870d231ceae28f7bc534c1228979cb41724f737897`.
- Library SHA-256 `7172a3f6970790c5795f074a8861555456eef330648a6591289ded34165df825`.
- Renderer WASM SHA-256 `594ceaed387adc70ea13bfbb2e8eace916f6c782254ed5a6f0f0a0a7a4fe4061`.
- CI manifest equals local release manifest exactly; local HTML bytes/hash verified. Actions reports archive digest `39b86d57530c38c6c374c989a3e29b06ea566688b0a544e50ce95680cc1dca26`. Archive was not independently downloaded/rehashed through unavailable API access; do not claim otherwise.

Independent QA and Revision must finalize their own exact-source reports before bounded download approval. Previous agent turn hit a real usage limit; the user's continuation resumed the same role successfully, not a background scheduled restart. All required checks were retained.

Known external boundaries remain: earlier paper quotation/crop Git blobs were not erased, no Public clearance, Pages403, no user-PC/Box sync, no activated default-branch weekly schedule, no clean Windows-user/default-browser claim, no perpetual agents.
