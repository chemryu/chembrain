# Development — web round 01

Reviewed source: `e424b34653fb96b911f5ee5708286c92baddfe5f`, based on `c96c210a89a077869da78e7e570f06c80768cc16`.
Author: root / Development. This is an implementation handoff, not an independent approval.

Implemented a static English molecule-first library with initially empty reaction panel, molecule-related direct/route reaction selection, stage solutions, unique DOI paper references, browser-local record editing, validated compact import and JSON backup. Legacy desktop entry remains separate. No application backend, personal AI API, PDF document or paper body is published.

Three supplied papers were manually curated into 12 draft reaction examples (49 chemical records, including reagents; 25 molecular-library entries), 3 papers with DOI/authors and stage-specific solutions. Unknown structures, quantities and conditions remain null. Selected target diagrams have per-paper provenance. The ~22 KB package is selected structured information, not a complete or lossless extraction of the papers.

Separate `paper_pipeline` performs journal metadata collection, explicitly licensed ACS OA archiving, private bounded text candidates and validated curated export. Private review/PDF work is rejected inside the repository. Chemistry candidates require review before export. Other journals currently provide metadata/local-PDF ingestion, not generalized publisher PDF acquisition. Weekly feature-branch cron is NOT active until a default-branch dispatcher/configuration is established; the optional Windows installer was prepared but NOT installed on the user's PC.

Local checks on this source: pytest 237 passed, 1 skipped (Windows DPAPI); TypeScript + build:web passed; real Chromium smoke passed initial empty view, molecule/route selection, unique references/stage solutions, local save/reload, import rejection and preservation, backup, mobile and /chembrain/ subpath. These checks did not catch the additional independently reproduced malformed-editor/schema/weekly issues; no claim that passing smoke means zero findings.

GitHub run https://github.com/chemryu/chembrain/actions/runs/39062568338 independently ran tests (237 passed, 1 skipped), web build and real-browser smoke successfully. Immutable terminal receipt `0331192af8d03426f4a2c28a584eaf7f9d34bb1d` and byte-exact files are preserved in `web/manifest.json` + adjacent files. Pages configuration failed HTTP 403 `Resource not accessible by integration`; deployment and live access were skipped, page_url=null. Owner Pages Source setting confirmation requested asynchronously. No actual public URL or live-access success exists yet.

The receipt's independent_qa usage-limit string reflects the source-time state; after the recorded reset time, the same existing independent agents resumed normally and found issues. It is not a current approval. No model/account switching was used. QA and Revision reports determine the next round; source stays frozen during review.
