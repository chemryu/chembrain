# Planning — 20261017-gpt-02 / round-02

- Status: READY FOR DEVELOPMENT; no delivery approval.
- Rejected source: `36fde22d2791475062565161bf986b88f035b2da`.
- Published round-01 record commit: `27ad901ccd0183f018d840d78259ebd4158bb728`.
- Inputs: round-01 [handoff](../round-01/handoff.md), [Independent QA](../round-01/qa.md), [Revision](../round-01/revision.md) and [scope](../round-01/planning.md). Both reviewers rejected the source with four confirmed unresolved findings. Passing tests or a later successful Windows build for that SHA cannot reverse that rejection.
- Scope is restricted to these four repairs and their meaningful regressions. Preserve all JACS bibliography + OA-only PDF collection, publication windows/resume, existing data/evidence, scheduling, English DOI-only UI and grouped reaction references. No cosmetic redesign or new collection/authentication scope.

## Repairs and concrete contracts

### REV-01 / QA-01 — bind every PDF hop to the licensed article

- Primary file: `server/jacs_collection.py`; relevant production path is `_licensed_pdf` → `CrossrefClient.pdf` / `_get` → `_Redirect.redirect_request`.
- Introduce one reusable PDF URL policy that validates existing HTTPS/public-address/origin/credential/query constraints **and** the supplied expected normalized DOI and approved same-paper PDF route. Pass the immutable expected DOI/policy through the PDF transport, instead of deriving it anew from a redirect destination. Keep the licensed content version bound to that selected candidate; unrelated routes must not silently select another representation.
- Validate the initial request and every redirect destination before issuing the next request. A same ACS host is insufficient: reject different DOI, unrelated/SI/non-PDF path, unexpected host and malformed URL. Canonical/percent-encoded representations of the same DOI may pass only on explicitly approved article-PDF routes. Crossref metadata requests retain their separate metadata transport policy.
- Add tests that invoke the actual production redirect handler/transport: permitted same-article redirect; different article DOI; same-host arbitrary route/SI; unapproved host/private target; existing HTTPS/credentials/query protections. Checking only `_licensed_pdf` selection is insufficient.

### REV-02 / QA-02 — retain the complete OA/type decision

- Primary file: `server/jacs_collection.py`; update `scripts/observe_jacs_gateway.py` and fixture callers for any changed candidate contract.
- Replace the lossy two-string candidate tuple with an explicit structured candidate carrying supplied PDF URL, recognized license URL, validated effective start, optional expiry, and matching content version. Carry that exact decision into `_save_pdf`; use normalized timestamps or preserve the original values unambiguously. Do not recompute provenance from an unrelated response.
- Persist this public evidence together with existing attachment hash/size/page count/download time/policy. Retain Crossref `journal-article` type in new-reference `collection` and collector-owned `ARTICLES` metadata so pre-existing manually edited sources also have upstream type provenance without replacing their title/citation/notes/DOI/ID/upload fields.
- Existing user bibliographic data remains unchanged; no `kind`, source `page_count`, citation evidence or original upload mutation. Do not expose private filenames/absolute paths or full text in ordinary summaries/UI/export. Missing license end is represented explicitly as absent/null, not invented.
- Verify a persisted attachment contains the exact selected license/date/version/supplied-link evidence and collector metadata retains the upstream type for both new and pre-existing sources.

### REV-03 / QA-03 — enforce the PDF page ceiling before installation

- Primary files: `server/jacs_collection.py`, `tests/test_jacs_collection.py`, and the user-facing collection documentation containing limits.
- Define/document a `MAX_PDF_PAGES` constant; 400 pages is a sensible consistent choice with existing ordinary PDF upload. Preserve current 30 MB byte limit and magic/readability/encryption/nonempty checks.
- Reject over-limit documents after parsing their page count but before staging/replacing files or updating attachment metadata. Return an accurate bounded failure outcome without storing exception secrets or paper text. The DOI reference, previous valid attachment bytes/metadata, reactions and original uploads must survive rejection; no temporary file remains.
- Test exact page-limit acceptance and limit+1 rejection with generated fixtures, including an existing good attachment that must remain unchanged. Keep corruption/encryption/byte-limit/empty-PDF coverage; do not relax another check to pass the new boundary.

### REV-04 / QA-04 — surface nonfatal duplicate-source ambiguity

- Primary files: `server/store.py`, `server/jacs_collection.py`, `src/JacsCollection.tsx`, `tests/test_jacs_collection.py`, plus the existing browser scenario as needed.
- Preserve `Store.import_jacs_reference`'s existing return contract using an optional notice sink or backward-compatible helper. Return/report all qualifying existing main/unspecified source IDs for the normalized DOI and the deterministic selected ID; do not merge/delete records, modify user fields or conflate a normal SI/main pair.
- Recommended collection result contract: `notices: [{code: "duplicate_doi_matches", doi, source_ids, selected_source_id}]`; count is explicit or derived from `source_ids.length`. IDs must be stable and selection deterministic. Repeated collection reports the current ambiguity without creating new records or unbounded duplicate notices inside a run.
- Notices are distinct from `errors`: valid duplicate reuse must not make the run partial, prevent a complete checkpoint, or be silently hidden behind success. Persist notices in last-run status and render a separate English details summary showing DOI, retained IDs/count and selected source. Continue to show actual download/metadata failures separately. Old stored runs without `notices` remain renderable.
- Test multiple main candidates (DOI case/prefix variants), deterministic selection, repeat collection, every original record/user field preserved, correct main/SI distinction, success/checkpoint with notices but no errors, and browser visibility of the structured warning.

## Validation and handoff

Development records targeted reproductions before/after repairs and actual commands/outcomes in round-02 `development.md`. Run the focused collector suite, full Python suite, production frontend build and source browser/real-restart checks appropriate to changed UI/metadata. Preserve previous evidence compatibility, DOI-removal guards, publication-window continuation, OA-only selection and scheduler/grouped-reference regressions.

Freeze a new full source SHA after repairs. Require that SHA's Windows EXE build/smoke, zero-argument startup, packaged UI, true restart data retention, restricted runtime PATH, packaged collector fixture and actual temporary scheduler registration/inspection/removal. Scheduling checks must never execute a collection task or install a user-PC job. Inspect exact-SHA receipt, logs and artifact checksum; no prior-source approval transfer.

Independent QA and Revision separately inspect the corrected source and replay the four cases, recording zero unresolved findings only after actual resolution. Wiki preserves both complete reports and either returns remaining work to Planning or records delivery eligibility. Final records use the records branch without moving the reviewed executable SHA.

All earlier delivery gates remain: required checks PASS, two independent reviews with zero unresolved findings, identical full source SHA for review and Windows evidence, artifact SHA-256 match, no release publication. Public gateway outcomes remain honest observations (cloud UNAVAILABLE is not a live-download PASS); fixture success is separate. Clean Windows VM, actual user default-browser integration, user-PC schedule installation and Box access/sync remain NOT RUN unless actually performed. No institutional authentication or external personal model API call is introduced.
