# CI outcome supplement — round-02

- Exact source **`c484897d6ccc504a517406e8a766c8d95a05cb76`**. Run **39274614887**: https://github.com/chemryu/chembrain/actions/runs/39274614887.
- Immutable terminal receipt **`93613c39b6d6cad681e5a2d3d7bc86fa8c615394`**. Ten exact Git blob files plus SHA256 inventory preserved in `web/`; no truncation or replacement by local logs.
- This supplement supersedes the earlier Development cutoff's CI-PENDING state, not its local-only evidence limits.

## Actual results

| Gate | Result | Evidence |
|---|---|---|
| Python | PASS324 / SKIP1 Windows DPAPI | web-tests.log |
| Hosted TypeScript/Vite build | PASS | web-build.log |
| Hosted full browser/map/receiving | PASS | web-browser.log; browser step success |
| Main portable build + actual file:// offline UI/structures/storage | PASS | portable-build.log, portable-browser.log; portable step success |
| Paper standalone build + payload | PASS | paper-build.log, paper-manifest.json |
| Actual file:// Paper PDF/native-worker + two-program transfer | **FAIL** | paper-browser.log: first synthetic PDF never renders; canvas0x0, data-renderedfalse |
| Download artifact | SKIPPED | portable_artifact step skipped; no new artifact URL |
| Pages publish/HTTPS | SKIPPED / NOT RUN | build job failed; publish skipped. No new403 claim |

Paper UI correctly exposes: **“PDF worker could not run locally. Use a current Chrome or Edge browser that allows local module workers.”** Traceback is `create_checked_package` at first PDF canvas assertion, before chemical/solution/reaction exports and the actual-file main handoff. Thus the passing local mocked HTTP test does not establish portable file behavior. Native local Blob module-worker behavior on the normal GitHub Chromium file origin is a hypothesis to diagnose; this receipt lacks the underlying Worker error event, so a precise root cause is not asserted. No managed local file-policy bypass, alternative browser or retry-without-change is authorized.

Both CI HTML manifests are **byte-for-byte JSON-equal to the local captured manifests**, same source/library/engine/worker digest and HTML lengths/SHA. This does not make the failing Paper program deliverable; the required functional gate still failed. Artifact ZIP was not created or independently downloaded/hashed.

Independent QA and Revision must record this exact-source failure, then Wiki→Planning returns a bounded worker compatibility/diagnostic repair. Original round-01 rejection stays preserved. No source modifications during independent review, no delivery approval and no production/Pages claim.
