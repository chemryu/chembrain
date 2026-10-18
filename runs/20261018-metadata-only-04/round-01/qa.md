# Independent QA — metadata-only round 01

Reviewed exact frozen source **6280794c87e7867b0ccd2e2d4f6924814917997a** (parent 56be43bf15b4c98b8b515d2dc3bbd2bd0fcbbbae). Independent QA read AGENTS.md, RULEBOOK.md, current request, Planning, Development, current/history audit evidence, changed schema/browser/processor/state/workflow/gate code and relevant regression tests. Application and tests were not edited; no commits, pushes, visibility changes or history rewrites were performed.

## Findings

**Unresolved material application/policy findings: 0.** Current source implements the requested publication boundary. This is an exact-source code assessment, not clearance to make the existing repository Public and not evidence of a live website.

Nonblocking wording nit: the workflow-dispatch `collect` description still mentions supported OA PDFs. The invoked command and mandatory `GITHUB_ACTIONS` guard correctly enforce metadata-only behavior regardless of the flag. This label does not authorize or execute PDF collection; update when that workflow is next edited.

## Independently executed checks

- Focused portable contract, processor, durability, state, repository payload and web-domain tests: **56 PASS**, 4.91 seconds.
- Entire suite run independently with `GITHUB_ACTIONS=true`: **284 PASS, 1 SKIP**, 20.41 seconds. The skip is the Windows-only DPAPI test; existing Starlette/httpx deprecation warning. The explicit environment tests verify Actions behavior, while synthetic local-PDF fixtures deliberately restore their intended local environment.
- Real Chromium `scripts/web_smoke.py`: **PASS**. Exercised repository-subpath loading, initially empty reaction panel, molecule selection, stage solutions, DOI reference deduplication, malformed-editor recovery, edit/reload/import persistence, Python-export/browser-import parity, DOI/authors-only paper display/editor/export, exact-byte legacy backup, backup-write and primary-write failures, unknown-field rejection, no copied paper assets, compact download and mobile layout. No backend request is introduced.
- `scripts/check_repository_payloads.py`: **PASS**, 146 tracked working files.
- `scripts/check_repository_payloads.py --dist dist`: **PASS**, 13 deployment files.
- Source/test paths remained unchanged during QA. Production build was supplied by Development for the frozen SHA and the actual generated artifact was exercised independently; QA did not rebuild or substitute a different artifact.

## Boundary assessment

Python and TypeScript public contracts reject unknown keys at each table row and nested solute/step/evidence object. Public papers consist solely of stable internal ID, canonical DOI and authors; chemistry/solution/reaction facts and technical locators remain. Explicit legacy projection accepts only known previous citation fields, preserving chemistry. Browser migration writes and verifies the exact original string under a unique browser-private backup key before replacing primary storage. Unsupported legacy fields and failed backup writes retain the original primary data and block unsafe imports/exports. Primary-write failures also preserve originals. Compact downloads use validated working tables and omit private backup keys.

Actual cropped target PNGs and their seed mappings are removed. The generator emits only encoded-chemistry SVG diagrams; unencoded targets show an honest placeholder. Current public starter has three paper DOI/author rows and twelve draft reactions, not a claim of complete extraction or experimentally verified chemistry. Distributed legacy manifest quotations are removed, while an optional locally supplied quotation can still be checked by the separate local importer.

Actions weekly collection forces metadata-only mode even when callers omit its CLI flag, skips old pending PDF work, does not instantiate the archive Store, and never reaches license/PDF/review creation. Direct ingestion refuses Actions before opening a supplied path. The whole paper-work cache is gone. Durable state validates checkpoint/anchor-only shapes and rejects legacy private pending snapshots rather than uploading them again. Output-before-state and remote feed acknowledgment protections remain covered by passing durability tests. Local bounded private PDF processing is retained outside Git; this does not upload originals.

Payload gates provide source/build checks for supported document signatures, archives, private review output and raw-document JSON fields, independently validating the portable public library. They are automation controls, not a server-side prohibition on an owner deliberately uploading through another route. Bounded allowed technical text fields cannot semantically prove that every arbitrary user-entered sentence is never a quotation; documentation makes that limit explicit.

## Historical/publication limitations

The recorded reachable-history audit covered all fetched advertised heads and the obtainable tag. It found **zero PDF blobs**, **two earlier quotation-bearing JSON blobs**, and **two earlier source-PDF crop image blobs**. Current removal does not erase them. The audit records IDs/paths/counts without redistributing the original text. Native Git cannot establish removal of GitHub Actions caches/artifacts, deleted server refs or server-retained unreachable objects; these remain **UNVERIFIED**. No history rewrite, deletion of shared refs/remote artifacts, or Public switch was authorized or performed. Before making this existing repository Public, the owner must decide how to handle the known earlier quotations/images; an independently clean publication repository is a separate option. This external decision is a required Public-readiness condition, not an application defect to resolve through unapproved destructive cleanup.

Pages activation remains externally blocked by the previously observed private-plan/403 issue; no live deployment or active weekly scheduler is claimed. At report writing the new run's GitHub CI receipt is pending root's fetch; this report does not infer its outcome. Root must bind any later receipt to this exact source SHA and retain its actual results separately. Windows native execution/user-PC scheduling were not run and are not the requested delivery format.

Disposition: **current-source metadata-only policy and local browser behavior PASS; repository Public clearance and live internet delivery NOT CLEARED.** Forward this complete report to Revision, then Wiki; do not inherit earlier source approval or silently erase historical qualifications.

## Actual CI verification supplement

After the preceding report was written, root captured immutable receipt commit **c3add00d19e2e6e2daf1e9d92efe69b3835d48f2**, GitHub Actions run **39098202973**, for exact workflow/built source **6280794c87e7867b0ccd2e2d4f6924814917997a**. QA independently compared all six preserved raw files byte-for-byte against that Git object, verified manifest byte counts and SHA-256 values, and confirmed public/library.json matches provenance digest **7853ba5d2b335c274733b8c726ac7b80c899e9d51bfd42295279ea75df2452bb**. Evidence is retained under `web/` beside this report.

Actual CI tests: **284 PASS, 1 SKIP**, 7.16 seconds. Build/app and real-browser outcomes are success. The successful build job reached `upload-pages-artifact`, after its required tracked-source and built-artifact payload gates; both gates therefore completed successfully. Weekly collection/feed were **SKIPPED** in this run, not live-network-tested.

The **new** Pages configuration attempt failed HTTP **403**, `Resource not accessible by integration`; deployment and public HTTP access checks were **SKIPPED**, `page_url` is null. Terminal status is blocked. No live website, active schedule, clean historical repository or remote cache/artifact purge is established. Earlier pending-CI wording above is preserved as chronology and is superseded only by these actual results. Material code findings remain zero; Public-readiness qualifications remain unchanged.
