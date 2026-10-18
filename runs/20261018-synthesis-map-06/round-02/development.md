# Development — round-02 mobile focus and CI diagnostics

Frozen/pushed exact source **02d0dff2ce66a00f10e0c873baea80fa6f94e963**, based on rejected e6ed4e7. Followed formal round-01 Revision→Wiki→Planning handoff; original reports/failedCI4files preserved. No prior approval transferred.

## Changes

QA-SYN-01: mobile Focus now reads instance.getNode for the live selectedcard position and measured width/height, with safe dimensions fallback. It no longer centers stale initial projectedcoords after dragging. Shared hosted/offline browser regression moves the selected Doxycycline card200screenpx at390×844 and requires its complete actual bbox back insidecanvas afterFocus; no chemistry/storage changes. Existing broad map/list/edit/import/metadata regressions retained.

CI failurediagnostics: removed destructive last120lines cropping. All diagnostic files up to100000bytes are retained complete. Larger logs preserve boundedUTF8-safe head+tail with an explicit omissionmarker. Real-Git receipt fixture now captures actionableassertion plus600DOMlines and checks exactbytes survive fresh-job terminalreceipt. New oversizeUnicode diagnostic test checks header+summary, cap and UTF8. This improves diagnosis without claiming the old hostedCI failure was the mobilebug. Its actual assertion cause remainsUNRESOLVED until newCI evidence.

## Actual local checks

TypeScript/production hosted buildPASS; shared real-hostedbrowser suitePASS including newmobilegeometry and all oldcontracts. Original independentQA repro script /tmp/qa_synthesis_mobile_focus.py nowPASS: selectedcardx144.75,width168 withincanvasx40,width310 after200pxdrag→Focus. Focused graph+receipt tests7PASS. New source standalonebuild/HTTP-only/fullpytest in progress. ExactCI required before artifactacceptance, no guesses about its formerfailure.

No PDF/prose/crop upload, schema/data invention, main merge, visibility/history rewrite, schedule/PC/Box actions. Pages previous403 is historical; rejectedround01CI didnotattemptpublish, artifactSKIPPED. Localmanagedfile restrictionunchanged/no bypass; legitimate separateCIactualfilecheckstillrequired.

## Final Development evidence

Exact standalone722585bytes HTMLsha256a1a175882c6701e2d3f98b61b80dbed27d643e0de1eb661823c930b36384278d, source02d0dff, library7853ba5d2b335c274733b8c726ac7b80c899e9d51bfd42295279ea75df2452bb. Fullpytest290PASS/1DPAPISKIP; standalone HTTP-only allnewmap/mobile and allprioroffline/storage/injectionflowsPASS.

Actual exactsourceCI39141206671 / immutable8c8d3c6317433502ffd4984df39fd6b4290ef52e: tests290/1, hostedbuild/browser, source/distgates and actualfile:// offline browserPASS. ArtifactuploadSUCCESS id12140894328, reportedzipdigestd5ba0bad0030913a63c36824123dd4ae2561c5034556cab32e1daa23eb331ee2; ZIPnotindependentlydownloaded here. All9receiptfiles+manifest preserved web/, CIHTMLmanifest equalslocal. NewPages403 Resource notaccessiblebyintegration, deployaccessSKIP/noURL; collectionSKIP.

Olde6CIassertion cause cannot be recovered from its losthead and remains historicalUNRESOLVED; no causalidentification is claimed. The newsource's complete hosted+filemandatorychecks pass, withoutdisablingassertions or borrowingoldapproval. Logpreservation is nowcoveredbyrealGitreceiptregression. Independentreviewsdecidefinalcurrentpreviewapproval. Environmentdraftrepositorypointer updated02d0dff; requiresPublish remains separate fromdownloadapp/Pages.
