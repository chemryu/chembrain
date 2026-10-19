# Independent QA — Paper Workbench / round-02

- Separate Independent QA role. Exact source: **`c484897d6ccc504a517406e8a766c8d95a05cb76`** on `codex/gpt-agent-workflow`.
- Reviewed AGENTS/RULEBOOK, Independent QA role, current request, current wiki/progress, round-01 QA/Revision/handoff, round-02 Planning/Development and all three Development helper reports. Current wiki/progress still preserve round-01 rejection pending the complete new role loop; they are not this source's verdict.
- **Final decision: CHANGES_REQUESTED. One unresolved P1 finding: QA-PW-02, actual-file Workbench PDF worker failure.** QA-PW-01 is resolved in this inspected source and local execution. Fresh exact-source CI now proves main actual-file PASS but Workbench actual-file FAIL before source curation/transfer; artifact upload was skipped. No delivery approval or earlier approval transfers. The initial local review found zero material issues before this required CI exposed QA-PW-02; the terminal supplement below supplies the final evidence.
- No application, test, data, build input, shared `dist`/release or Git HEAD changes. Only this QA report was written inside the checkout; isolated build output went under `/tmp`.

## QA-PW-01 resolution and independent review

The actual planner now compares same-ID existing solution/reaction facts after chemical ID/InChIKey and normalized DOI/paper mapping. Safe missing quantities, units, concentration, ordered stages, compatible stage conditions, contextual yield/basis and additive distinct evidence become field-level Previous/Incoming proposals. Existing-field changes require explicit Apply and exact private raw-byte backup. Prefix stages append only with a complete unambiguous existing ordered prefix; a new accepted solution stays linked by the appended stage. Differing known values, composition/roles, ambiguous repeated-solution changes and inserted/reordered/relinked stages reject the whole candidate with a concrete latest-main-backup → Workbench reconciliation path. Local notes/status and known structures remain protected and visible as retentions. Null incoming facts do not erase known values; a repeated unchanged accepted package performs no writes.

I independently exercised the actual TypeScript helpers, including a combined adversarial case beyond the saved tests: alternative chemical ID matched by InChIKey, normalized same-DOI alternate paper ID, a missing quantity/time, prefix-linked new solution/stage, distinct main/SI source locations, exact original whitespace-byte backup, repeated zero-write import and incompatible retained unit rejection. Every final chemical/evidence foreign key resolved to the existing canonical identity. A separate unsupported unit-only source could not graft a unit onto an unrelated known amount. Source and baseline snapshots remained unchanged. All probes passed; the original empty-stage/quantity loss is not reproduced on this source.

The transaction validates the entire candidate and raw/displayed baseline before mutation, uses a unique backup key with exact readback, checks the primary baseline again after backup, then writes primary once. UI state changes only after successful commit. The async importer sequence rejects an older import result, while primary/displayed-baseline checks reject intervening edits. Existing focused tests and real UI regression code cover backup write/readback, primary quota, stale/concurrent baseline, displayed mismatch, protected backup keys, prior usable working UI, and no-op behavior.

The ordered stage matcher is deliberately conservative about reused solution IDs: an exactly unchanged repeated same-pot sequence is a no-op; a changed ambiguous sequence is rejected. Chemical-role keys align quantities independently of source display order. Number/unit and yield/basis checks prevent attaching a new value to incompatible retained context. No conversion, participant matching by names/formulas or invented route edge is performed.

## Independently executed checks

| Check | Result | Evidence / practical limit |
| --- | --- | --- |
| Frozen source and protected-input status | PASS | HEAD checked as full SHA above; `git diff --name-only HEAD -- src scripts tests packaging .github package.json package-lock.json` empty. Existing records-only changes preserved. |
| Actual helper/model/chemistry/source-candidate suites | PASS | `.venv/bin/python -m pytest -q tests/test_import_review.py tests/test_paper_workbench_model.py tests/test_structure_inspection.py tests/test_paper_pdf_candidates.py`: **27 passed in 10.32s**. Actual TypeScript and bundled JS RDKit are executed, not mirrored Python-only logic. |
| Independent combined remapping/stage/quantity/evidence/transaction adversarial probe | PASS | Read-only Node helper harness described above; safe full proposal, exact backup, idempotence and whole-package conflict rejection all asserted. |
| Isolated current-source hosted build | PASS | `npx vite build --base=/chembrain/ --outDir /tmp/chembrain-qa-c484897-hosted --emptyOutDir`; existing RDKit browser-externalization and chunk-size warnings. This focused build does not replace Development's TypeScript/full build receipt. |
| Actual Chromium held-post-drag-guard map regression | PASS | Own isolated build, Chromium154.0.8037.57, normal and CPU4; actual D3 guard held through focused Enter/Space/repeat/blur, inspector condition/DOI, placement, molecule activation, mobile dragged-target Focus, List fallback and unchanged storage assertions. Browser/server closed. Existing temporary harness reused; actual current shared smoke imported. |
| Development local evidence integrity | PASS | Independently read and hashed **12** inventory files from `local-files.json`, all **11** command logs against `local/checks.json`; lengths/hashes match. |
| Both current local artifact bytes | PASS | Independently hashed actual `release` HTML bytes against both candidate manifests; exact identities below. This is local byte identity, not actual-file execution. |
| Fresh exact-source mandatory CI actual file and artifact receipt | **FAIL** | Immutable receipt `93613c39b6d6cad681e5a2d3d7bc86fa8c615394`, run39274614887: main actual-file PASS; Workbench actual-file PDF worker FAIL; upload SKIPPED. All ten raw files independently hash-checked and byte-compared with immutable Git objects. |

Development-provided exact-source evidence was read and integrity-checked, separately from checks I executed: full Python **324 passed / 1 Windows-only DPAPI skip**, TypeScript/hosted build, hosted broad browser, both portable builds, both resource-blocked HTTP-only smokes and all four payload gates PASS. The paper HTTP log explicitly exercises real Workbench PDF/check/export UI → main saved same-ID review/Apply/reload for empty, partial, facts-only, empty-composition and prefix profiles; conflicting known values/roles/order and backup/readback/quota/stale/concurrent failures also pass. These are genuine two-program UI transfer tests but the local logs correctly say file:// NOT VERIFIED.

## Private source, graph and route scope

Source/code and focused runtime review found no additional material issue in strict nested export allowlists, DOI/label-scoped IDs, imported baseline ID retention, dependent-check invalidation or exact current-SMILES inspection. Main/SI document/page/locator evidence remains distinct and exact duplicates do not multiply. The source-wrapper import repair has an actual three-cycle recheck/export regression and honors an explicit Main wrapper even if the precise locator mentions SI.

PDF bytes/text/page images remain in memory; source hash pairing is private workspace metadata excluded from compact facts. PDF scripts/link overlays/external asset fetches are not used; the embedded local Blob worker has explicit error/bounds/cleanup handling. The sketcher is manual graph encoding, requires explicit transfer, and refuses unresolved/query/enhanced relative-stereo features it cannot preserve. Bundled RDKit validates actual graph descriptors including isotope, charge, fragments and stereo; this proves representation, not scientific agreement with a paper. Human source comparison remains explicit and required. The Map continues to draw only recorded participant arrows, with target membership distinct from edges and List fallback.

Automatic exact recognition of PDF chemical drawings is **not implemented or claimed**. No scientific completeness review of the user's real papers was performed. Journal downloading/scheduling, user-PC/default-browser installation, Box sync and perpetual agents are outside this round. Current payload safety does not erase historical quotations/crops or grant Public/history clearance. No policy bypass, Pages/deployment, main merge, visibility change or shared-history rewrite was performed by this role.

## Artifact identities and remaining gate

Both candidate local manifests identify source **`c484897d6ccc504a517406e8a766c8d95a05cb76`**:

- Main `Chembrain.html`: **5111218 bytes**, SHA-256 **`26d1f83ba3887b768a5a8600ad25935c2e37d34db9b34e1eccf1384f1cf8c724`**; library SHA-256 `7172a3f6970790c5795f074a8861555456eef330648a6591289ded34165df825`.
- Paper `Chembrain-Paper-Workbench.html`: **10161674 bytes**, SHA-256 **`2b2bca186078bc709aff287ba4190d1d62cc42d2cea66835031c11976dc17b0a`**.
- Pinned embedded dependencies: RDKit2026.9.1, PDF.js6.4.299 and OpenChemLib9.25.1; packaging notices/manifest declarations inspected.

Managed local Chromium's actual file:// policy restriction was not bypassed. Required fresh CI evidence must show hosted keyboard/map PASS, main actual-file offline PASS, separate Workbench actual-file PDF/worker/sketcher/export-to-main transfer and failure regressions PASS, and same-source manifests/artifact outcome. A later immutable receipt supplement can resolve this evidence gate without changing source; any source change requires fresh checks/review. Artifact ZIP was not independently downloaded or rehashed. Clean user PC/default browser NOT RUN. No delivery approval at this interim cutoff.


## Terminal CI supplement — QA-PW-02

Fresh run **39274614887**, immutable terminal receipt **`93613c39b6d6cad681e5a2d3d7bc86fa8c615394`**, targets the same exact source **`c484897d6ccc504a517406e8a766c8d95a05cb76`**. I independently read all **10** raw files in `round-02/web/`, verified their lengths and SHA-256 against `receipt-files.json`, and compared every byte with `git show <immutable-receipt>:<filename>`. Both CI manifests exactly equal the candidate manifests whose local HTML bytes I independently hashed. No moving-ref fetch, source change or managed-file-policy workaround was used.

### QA-PW-02 — offline Paper Workbench cannot open its first private PDF

**Severity: P1 / high.** Worker startup/error path: `src/paperPdf.ts:106`–`src/paperPdf.ts:114`; real failing assertion: `scripts/paper_workbench_smoke.py:178`. The CI-provided actual-file runtime is the reproduction; this was not independently rerun through the managed local file restriction.

Reproduction on the required supported CI workflow:

1. Build both single HTML programs from the frozen source above, matching the preserved manifests.
2. Run `.venv/bin/python scripts/paper_workbench_smoke.py` without `--http-only` (CI equivalent uses `python`). This opens the actual `file://` Workbench in Chromium with external resources blocked and creates only temporary synthetic private PDF fixtures.
3. Through the actual Open local PDF input, select the valid first `synthetic-source.pdf` fixture.
4. Actual: the native PDF worker emits an error; the visible UI alert is **“PDF worker could not run locally. Use a current Chrome or Edge browser that allows local module workers.”** The canvas remains width0/height0 with `data-rendered="false"`; the required 30-second render assertion fails. No checked chemistry/export-to-main transfer is reached.
5. Expected: the install-free actual-file Workbench starts its bundled worker, renders/extracts this supported local synthetic PDF without network access and continues through explicit source checking and real JSON transfer.

This blocks a core requested offline workflow and is not an acceptable substituted HTTP-only PASS. The exact underlying cause is **UNRESOLVED**. Opaque/file-origin or Blob module-worker compatibility may be investigated, but the current log records no detailed native-worker event or browser console cause; this review does not assert that hypothesis as established. The app fails visibly and does not claim successful extraction; no source data corruption was observed. Development must diagnose the actual worker startup/embedding/runtime failure and preserve useful native error/console evidence while retaining offline/private constraints and the real actual-file assertions.

### Final required-check accounting

| Exact-source CI check | Result | Evidence / limit |
| --- | --- | --- |
| Full Python | PASS | 324 passed, 1 Windows-only DPAPI skip, one dependency deprecation warning; CI-provided execution. |
| Hosted TypeScript/build and real hosted browser | PASS | Both raw logs and terminal facts agree. The previous hosted drag/Enter required-gate failure is not reproduced; direct independent normal/CPU4 held-guard checks also passed. |
| Main portable build and actual-file offline browser | PASS | `PORTABLE_BROWSER_PASS: actual file:// HTML`, matching main SHA; keyboard/map/structure/storage/security regressions ran. |
| Paper portable build/manifest | PASS | Matching source, HTML SHA/bytes, embedded engine versions/digests and private-source exclusion declaration. A successful build does not establish runtime success. |
| Paper actual-file PDF/worker | **FAIL — QA-PW-02** | First supported synthetic PDF never renders; exact worker alert and complete traceback retained. |
| Paper actual-file sketcher/source-confirmation/export-to-main and fact receiving/failure profiles | **NOT RUN** | The first PDF render failure stops the smoke before these later assertions; HTTP-only results do not substitute. |
| Artifact upload | **SKIPPED** | Terminal `portable_artifact` outcome skipped. No new downloadable approved ZIP; ZIP digest not independently downloaded/rehashed. |
| Pages/publication | **SKIPPED / NOT ATTEMPTED in this run** | Terminal publish skipped, page URL null. Earlier Pages403 remains separate historical context. |

**Final: CHANGES_REQUESTED; QA-PW-01 resolved, QA-PW-02 P1 unresolved, no approved deliverable.** Separate Revision must assess this finding, then Wiki preserves the complete reports/raw receipt and returns a bounded native-worker diagnosis/repair plus fresh actual-file evidence requirement to Planning. A fix requires a new full source SHA, affected/full required checks and fresh independent QA/Revision. The existing repaired receiving contract and passed hosted/main checks must be preserved, without carrying their source approval to new code.
