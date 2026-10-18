# Revision — synthesis map round-02

- Role: separate Revision; no application source edits or publication actions.
- Reviewed exact source: **`02d0dff2ce66a00f10e0c873baea80fa6f94e963`**.
- Compared the complete rejected round-01 reports and Wiki handoff, round-02 Planning/Development, provisional Independent QA and actual bounded source diff.
- Initial disposition: **QA-SYN-01 resolved; zero unresolved material source findings identified. Final artifact delivery approval PENDING fresh exact-source CI hosted/actual-file/artifact evidence.** This report does not transfer an older SHA's approval.

## Independent correction assessment

The narrow-canvas Focus control now reads `instance.getNode(graph.selectedNodeId)` with the live selected card's measured width/height and safe fallback dimensions. It no longer uses the initial graph projection's stale coordinates after a drag. The desktop live-node fit path remains intact. The fix does not discard the user's arrangement, edit chemistry records or change edges/data schemas.

Revision independently reran its own round-01 reproduction on the already built production application at `/chembrain/`, real Chromium **390 × 844**: choose Paclitaxel, Focus, drag the selected card header 200 screen pixels to the right, then Focus again. The card really moved (`x=144.75` initially, `x=324.75` after drag), and Focus returned its actual live box to **`x=144.75,y=355.78125,width=168,height=133.04296875`**, entirely inside canvas **`x=40,y=182.15625,width=310,height=480`**. No page errors occurred and browser chemistry storage remained byte-identical. The identical Revision scenario previously failed on e6ed4e7, leaving the card wholly outside the canvas.

The shared hosted/offline smoke additionally measures actual mobile doxycycline card containment after its selected header is dragged. The regression verifies a real drag and a readable card; a source-string check or transform-only check is not substituted. Existing inspection-position preservation and no-exploration-write checks remain.

## Diagnostics and scientific integrity

`bounded_log` preserves short diagnostics completely and bounds large ones with explicit UTF-8-safe beginning/end context. The actual temporary-Git regression now retains an actionable assertion followed by 600 DOM lines byte-for-byte through both build and terminal receipt jobs. A separate oversized Unicode case checks the byte cap, valid UTF-8 and both diagnostic ends. This corrects evidence loss without asserting that QA-SYN-01 caused the old CI browser failure; that old assertion remains unrecoverable from its truncated receipt.

Revision independently executed **7 focused runtime tests PASS** (`tests/test_synthesis_graph.py` and `tests/test_web_provenance.py`) plus the real mobile reproduction above. Independent QA separately reports **17 focused tests**, hosted TypeScript/production build, full hosted browser suite, source/distribution payload gates, independent mobile reproduction and portable HTTP-only suite PASS. Root separately reports **290 full-suite PASS / 1 Windows-only SKIP**. These are distinct evidence sources, not a claim that this role repeated every full check.

The source diff is limited to mobile focus, shared regression, diagnostic preservation/tests and request/planning records. Recorded chemistry projection is unchanged: only recorded reactant/product edges, target membership without invented transformations, separate missing-step fragments, iterative cycles, ID namespaces, whole-reaction participant retention under explicit caps and List fallback. No new chemical facts, original paper payload, PDF, API, dependency, visibility/history/main/schedule action is introduced.

## Initial evidence limits / pending final observation

Exact-source stable portable identity reported by QA/Development: `Chembrain.html`, **722585 bytes**, SHA-256 **`a1a175882c6701e2d3f98b61b80dbed27d643e0de1eb661823c930b36384278d`**, unchanged library SHA-256 **`7853ba5d2b335c274733b8c726ac7b80c899e9d51bfd42295279ea75df2452bb`**. This manifest alone is not proof of an uploaded archive or actual local-file execution.

Fresh CI **`39141206671`** is pending at this initial report. The coordinator owns receipt capture; a final supplement must compare the immutable receipt, exact source/build IDs, hosted browser result, standalone build, genuine offline `file://` execution and artifact identity before any download approval. The local managed-browser file policy remains unchanged, so local actual-file is NOT RUN; HTTP-only offline smoke remains explicitly HTTP-only.

Earlier Pages403 is historical until the fresh run actually attempts configuration; no hosted URL may be inferred. Existing reachable quotation/crop blobs, unverified remote artifacts/caches, inactive collection, no Box sync and browser profile/file-location storage limitations remain outside this bounded repair. No Public clearance or production release is approved.

Wiki should preserve the complete original round-01 reports and this round-02 chronology. Do not finalize the stopping criterion until the pending required delivery evidence is actually available and independently checked.

## Final exact-source evidence and Revision decision

Independent QA's complete final supplement now records **PASS for the bounded downloadable browser preview, zero unresolved material source findings, QA-SYN-01 resolved**. Revision separately verified all **nine** raw evidence files byte-for-byte against immutable terminal receipt **`8c8d3c6317433502ffd4984df39fd6b4290ef52e`**, and checked every byte count and SHA-256 against `web/manifest.json`. The receipt and provenance both identify workflow/built source **`02d0dff2ce66a00f10e0c873baea80fa6f94e963`**, fresh actual [CI run39141206671](https://github.com/chemryu/chembrain/actions/runs/39141206671).

The actual runner evidence is **290 Python PASS / 1 Windows-only DPAPI SKIP**, TypeScript/hosted production build **PASS**, hosted real-browser suite **PASS**, standalone build **PASS**, and genuine offline **`file://` browser suite PASS**. The shared new mobile selected-card drag/Focus assertion is part of the hosted and portable browser checks. The normal CI runner's real local-file execution supplies that required evidence; this role did not bypass the local managed browser policy or mislabel HTTP-only smoke as file execution. Collection/feed remain SKIPPED, not a collection-success claim.

Revision also compared the CI browser manifest byte-for-byte with the local release manifest and independently hashed `release/Chembrain.html` and `public/library.json`. Exact HTML identity is **722585 bytes**, SHA-256 **`a1a175882c6701e2d3f98b61b80dbed27d643e0de1eb661823c930b36384278d`**; current library SHA-256 is **`7853ba5d2b335c274733b8c726ac7b80c899e9d51bfd42295279ea75df2452bb`**. The actual-file CI log explicitly names that source and HTML hash. Artifact upload succeeded with ID **`12140894328`**, [download URL](https://github.com/chemryu/chembrain/actions/runs/39141206671/artifacts/12140894328), reported archive digest **`d5ba0bad0030913a63c36824123dd4ae2561c5034556cab32e1daa23eb331ee2`**; artifact outputs match the captured manifest. **Revision did not independently download the uploaded ZIP**. The runner's successful upload/digest and validated HTML bytes are distinct evidence, stated without claiming an archive download that did not occur.

This fresh run actually observed Pages configuration **403 `Resource not accessible by integration`**; deployment and access were **SKIPPED / NOT RUN**, `page_url=null`. Thus the overall workflow remains blocked for hosted publication, while the bounded downloadable HTML's required build and validation gates pass. Existing history quotation/crops and remote-storage uncertainty still prevent any Public-clearance claim. No visibility/history/permission change or unrelated activation was performed.

**Final Revision verdict: PASS for this exact-source downloadable browser preview; zero unresolved material application findings, QA-SYN-01 resolved, required current hosted/portable validation satisfied.** The original e6ed4e7 CI browser failure remains historical and cause-unresolved because its diagnostic head was lost; successful current-source evidence does not identify that old cause or relabel the old run. The current gate is satisfied by actual current CI success and independent review, not a guessed causal attribution.

Wiki may now preserve both complete round-02 reports and hashes, record the bounded preview approval and separate Pages/history limitations, and close this implementation loop for source `02d0dff2ce66a00f10e0c873baea80fa6f94e963`. Do not loop Planning solely to repair unrelated Pages permissions or publish a site without the already separate owner configuration path. Preserve the rejected round-01 reports and prior delivery history unchanged.
