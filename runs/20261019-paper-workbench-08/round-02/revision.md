# Revision — Paper Workbench round-02

- Separate Revision role; reviewed source **`c484897d6ccc504a517406e8a766c8d95a05cb76`**, verified as current HEAD. No approval transfers from rejected round-01 `8cbd5fe2fa92da03169922e1cc7a43bb59b0a89d` or an earlier run.
- **Decision: CHANGES_REQUESTED. QA-PW-01 resolved; QA-PW-02 P1 confirmed and unresolved.** The mandatory actual-file Workbench workflow fails before its first source PDF can render. Required downstream actual-file transfer and artifact gates have not passed, so delivery and loop closure are not approved.
- Inputs: AGENTS.md, RULEBOOK.md, agents/revision.md, requests/current.md, round-02 Planning/Development, final Independent QA including terminal supplement, CI-outcome supplement, raw terminal receipt and relevant receiving/worker/packaging/smoke implementation. This role changed only this report; no application, tests, build inputs, shared outputs, source commit or deployment changes.

## Independent evidence assessment

I independently read all ten raw files in `web/receipt-files.json`, verified their byte counts and SHA-256, and compared every byte with the corresponding immutable Git object in receipt **`93613c39b6d6cad681e5a2d3d7bc86fa8c615394`**. The inventory, terminal status and raw logs agree. This is a terminal failure, superseding Development's earlier PENDING cutoff.

Run **39274614887**, https://github.com/chemryu/chembrain/actions/runs/39274614887, records workflow/built source `c484897d6ccc504a517406e8a766c8d95a05cb76` and library digest `7172a3f6970790c5795f074a8861555456eef330648a6591289ded34165df825`. Both CI manifests are exactly JSON-equal to the captured local candidate manifests. I independently hashed the actual local release HTML bytes against those manifests:

| Program | Bytes | SHA-256 |
| --- | --- | --- |
| Main `Chembrain.html` | 5111218 | `26d1f83ba3887b768a5a8600ad25935c2e37d34db9b34e1eccf1384f1cf8c724` |
| Paper `Chembrain-Paper-Workbench.html` | 10161674 | `2b2bca186078bc709aff287ba4190d1d62cc42d2cea66835031c11976dc17b0a` |

These checks establish source/artifact evidence identity, not successful Paper execution or a downloaded artifact ZIP. No artifact ZIP was independently downloaded or rehashed.

I also independently executed `.venv/bin/python -m pytest -q tests/test_import_review.py`: **14 passed in 8.12s**. These tests exercise the actual TypeScript planner/transaction. No broad test rerun or browser policy workaround was needed for this assessment. Protected source diff against HEAD was empty for `src`, `scripts`, `tests`, `packaging`, `.github`, package manifest and lockfile. No servers were started by this role.

## QA-PW-01 — existing same-ID chemistry facts: resolved

The source now explicitly inspects existing solution and reaction facts instead of relying on the generic old-record-wins merge. I reviewed `src/importReview.ts`, including canonical chemical/DOI mapping, whole-candidate conflict handling, field-level proposal construction, ordered-prefix stage alignment, additive distinct evidence and the private transaction. The focused tests independently passed the original empty-stage/fact-only loss, partial facts, prefix-linked new solution, chemical/paper remapping, incompatible quantities/roles/stage ordering, exact raw-byte backup, no-op and failure-preservation cases.

Safe missing amounts/units/concentration, conditions, ordered stage links and compatible yield context become concrete proposals. Known incompatible values or ambiguous stage alignment reject the whole candidate; no apparent complete import with an orphaned intended stage is accepted. Number/unit and yield/basis context checks prevent grafting a missing field onto incompatible retained context. Exactly unchanged repeated same-pot stages are a no-op; changes to an ambiguous repeated sequence remain conservatively blocked. Distinct main/SI evidence survives canonical paper mapping. Known user structures, notes and status remain protected, with visible retentions.

The transaction validates the candidate and captured/displayed baseline, writes exact original bytes to a unique private backup key, verifies readback, rechecks the baseline and performs one primary write before UI state replacement. Existing-fact updates trigger that protection even without a structure upgrade. Stale/concurrent data, backup/readback/quota failures and identical repeated imports retain the specified protections. This agrees with final QA's broader 27-test plus combined adversarial remapping/backup assessment and Development's genuine HTTP-only two-program UI transfer results. Those broader executions are attributed evidence, not checks rerun by Revision.

No additional material receiving-contract finding was identified. Resolution of this code defect does not substitute for the still-failing actual-file end-to-end gate.

## QA-PW-02 — first actual-file private PDF fails: confirmed P1

The raw `web/paper-browser.log` establishes the failure in the required supported CI actual-file run. `scripts/paper_workbench_smoke.py` uses actual release file URIs unless `--http-only` is selected, opens the real local PDF input and generates only temporary synthetic PDF fixtures. Its first `create_checked_package` assertion at line178 waits for a rendered canvas. The log records `width="0" height="0" data-rendered="false"` throughout the timeout and the visible alert:

> PDF worker could not run locally. Use a current Chrome or Edge browser that allows local module workers.

Expected behavior is opening/rendering/extracting the supported synthetic local PDF with the bundled native worker, without external resources, before explicit source checking and chemistry export. Actual behavior prevents the core requested offline source-assisted workflow immediately. A successful portable build, valid checksum and passing HTTP-only execution cannot satisfy this actual-file requirement. P1 is warranted by the blocked primary workflow; no silent success or observed source-data corruption is asserted.

Relevant implementation is `src/paperPdf.ts:106`–114: gzip-decompressed pinned worker bytes become a local JavaScript Blob, `new Worker(url, {type:'module'})` creates a native worker, its error handler rejects loading with the exact observed message, and PDF.js receives that explicit native port. `vite.config.ts` bundles the pinned worker and deliberately disables external/CDN and fake-worker import fallbacks. `scripts/package_paper.mjs` packages the same program into the single HTML and records worker/HTML hashes. This supports that the observed alert is the native-worker error path; it does **not** disclose the native event's underlying cause because the handler discards that detail. The smoke retains page errors/workers for final checks, but its early failed assertion does not emit those diagnostics.

**Underlying root cause remains UNRESOLVED.** File/opaque-origin Blob module-worker behavior is a hypothesis, not an established diagnosis. Worker source compatibility, packaging/runtime execution and resource blocking must be distinguished using actual error evidence. The required CI fixture failed; Revision did not independently reproduce it by bypassing managed local Chromium's administrative `file://` restriction or selecting an alternate browser. The failure is not dismissed as merely local policy: the terminal CI successfully opens both actual HTML programs and the main actual-file suite passes.

## Required gates and closure assessment

| Gate for this exact source | Result | Basis / limit |
| --- | --- | --- |
| Full Python suite | PASS324 / SKIP1 | CI and Development logs; Windows-only DPAPI skip remains distinct. |
| TypeScript/hosted build and hosted browser | PASS | Immutable CI logs/status. Final QA separately exercised held-guard keyboard behavior normally and at CPU4. |
| Main actual-file offline browser | PASS | Immutable `portable-browser.log`, same main source/hash. |
| Paper standalone build/manifest/payload | PASS | Immutable build/manifest plus preserved local payload evidence; runtime success is separate. |
| Paper actual-file PDF/native worker | **FAIL** | First valid synthetic PDF: QA-PW-02. |
| Later Paper actual-file sketcher/source confirmation and checked-facts JSON transfer to main, persistence/conflict/failure profiles | **NOT RUN** | First PDF assertion stops the smoke before those checks. Local HTTP-only passes do not replace this gate. |
| Artifact upload/download availability | **SKIPPED** | Terminal `portable_artifact` skipped; no approved ZIP or independent ZIP digest. |
| Pages publication | **SKIPPED / NOT ATTEMPTED** | Publish skipped and page URL null; this run makes no new Pages403 observation. |
| Clean user PC/default browser | **NOT RUN** | Not represented by CI or the managed local environment. |

Final QA and Revision therefore agree on **one unresolved material P1**, and mandatory checks are incomplete. RULEBOOK closure criteria are not met. Preserve the successful receiving repair and hosted/main behavior as evidence for this source, while requiring fresh evidence/reviews for any modified source.

## Bounded Wiki → Planning handoff

Wiki must preserve the complete final QA/Revision, prior rejection and immutable receipts, then return the following work through formal Planning **before Development edits the application**:

1. Diagnose the native worker's actual startup/runtime error in an ordinary supported actual-file environment. Capture useful bounded native error/message/filename/location, worker/page console or equivalent diagnostics, browser/runtime identity and allowed/blocked resource facts. Use only synthetic fixtures; avoid source-document content/private paths in receipts. Keep concise visible failure handling and cleanup. Distinguish the app, worker bytes/runtime, packaging and test-resource policy using the concrete evidence; do not turn the current opaque-origin hypothesis into a claimed root cause.
2. Repair ordinary install-free offline `file://` support for the bundled PDF worker. Preserve a real native worker, pinned embedded bytes, private in-memory PDF/text/images, cancellation/bounds/failure handling and zero external requests. Do not enable CDN access, silently use fake-worker/main-thread fallback, bypass browser administrator policy, choose an alternate browser to evade it, serve HTTP as the claimed file fix, remove actual rendering/worker assertions or mask failures with blind retries. No prescribed implementation is justified until the error is known.
3. Keep the existing receiving contract, exact private backups, canonical ID/evidence handling, source-check/manual-sketcher/RDKit guarantees and map keyboard regression intact. Add a meaningful actual-file regression for the diagnosed worker failure while retaining first-PDF rendered pixels/text and native-worker verification, source reselect/failure cleanup and two-program UI transfer. Scientific agreement still requires the explicit source comparison; automatic exact chemical drawing OCR and journal downloading remain outside this repair.
4. Freeze/push a new full source SHA after the repair. Run affected/full required checks: Python, TypeScript/build, hosted browser, both portable builds/payload gates, both actual-file programs, the Paper native-worker/render/text/sketcher/source-confirmation/export → main saved same-ID review/Apply/reload and conflict/backup/stale/quota profiles. Preserve complete terminal raw evidence and same-source manifests, matching actual HTML bytes/hashes and engine/library identities; record artifact upload/download status truthfully. Local managed-file-policy limits remain explicit and are not waived.
5. Obtain fresh separate Independent QA and Revision on that exact source/evidence, then Wiki records the result. No source or artifact approval is inherited; closure requires zero unresolved findings and all required gates PASS. Do not publish a release, merge main, change permissions/visibility, rewrite shared history, activate journal scheduling/Box sync/perpetual agents or claim new Pages success as part of this bounded loop.

**Final verdict: CHANGES_REQUESTED.** QA-PW-01 resolved; QA-PW-02 P1 unresolved; actual-file downstream transfer NOT RUN and artifact upload SKIPPED. No approved deliverable.
