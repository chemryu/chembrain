# Development — post-drag map keyboard activation

Role: Development helper; no independent QA/Revision approval. Rejected source baseline: `8cbd5fe2fa92da03169922e1cc7a43bb59b0a89d`; final round-02 SHA is not frozen here. Read AGENTS, RULEBOOK, current request, Development role, and round-02 Planning. Owned changes only `src/SynthesisMap.tsx`, `scripts/synthesis_map_smoke.py`, and this report. No commit, shared build-directory replacement, policy bypass, publication, or source data changes.

## Proven defect and attribution limit

The pinned XYFlow/D3 drag handler installs a temporary window capture `click.drag` listener after a genuine moved card-header drag, removing it with its scheduled timer. The listener also captures a native keyboard-generated click (`detail=0`), so an already-focused native button can receive Enter yet fail to activate before that timer clears. Earlier read-only atomic-focus and real-input traces reproduced this; replacing focus+Enter with locator.press does not solve it. This establishes an actual timing vulnerability consistent with the saved CI inspector failure. The historical CI did not preserve its event trace, so its precise causal path is not claimed conclusively established.

## Implementation and regression

A shared internal MapActionButton activates Enter directly on initial keydown, arms Space on initial keydown and activates it on release. It prevents the corresponding native synthetic click, ignores repeated keydowns, and clears the armed Space on blur. Pointer click, native button semantics, accessible names, pressed state, drag headers, graph layout and underlying chemistry storage remain intact. Both molecule and reaction cards use it.

The existing map smoke now freezes the real post-drag timer *before mouseup*. It asserts that the actual pinned D3 click guard is present, then uses real focused keyboard input while that guard remains present. It keeps the original three-stage conditions/DOI, selected reaction, moved-node placement and byte-identical localStorage assertions. Additional assertions cover reaction Space-on-release/repeat, molecule Enter and Space, blur cancellation of held Space, and absence of duplicate native keyboard clicks. Only after those boundary assertions does the test advance the timer and verify ordinary/repeated Enter. The original pan/zoom, mobile dragged-target Focus, route fragments, List fallback and storage checks remain. Failure reports include focus, guard, selected molecule, inspector count and native keyboard-click count.

## Focused verification

- Private build: `npx vite build --base=/chembrain/ --outDir /tmp/chembrain-map-keyboard-build --emptyOutDir` — PASS. Existing RDKit browser-externalization and chunk-size warnings remain. Shared `dist` was not touched.
- Local managed Chromium `154.0.8037.57`, temporary HTTP server calling the real `check_synthesis_map` against that build — PASS both normal CPU and CDP CPU4. Full original mobile/layout/storage assertions and new held-guard Enter/Space/blur assertions ran, with no page errors. Servers/browser were closed in finally blocks.
- Negative control: private temporary source copy with only `SynthesisMap.tsx` restored from rejected HEAD8cbd, built separately, same new shared smoke — EXPECTED FAIL at the first Enter inspector assertion. Diagnostic: focused coupling button, real D3 guard true, inspector count0, one native keyboard click. This demonstrates the regression detects the pre-fix behavior instead of merely waiting away the problematic interval.
- `git diff --check -- src/SynthesisMap.tsx scripts/synthesis_map_smoke.py` — PASS; Python compile of the shared smoke — PASS.
- First temporary harness invocation used the wrong asset base and failed waiting for seed images; correcting the temporary build base resolved that harness error. It is not counted as an application/keyboard failure or omitted as an unexplained success.

Evidence retained locally: `/tmp/chembrain-keyboard-round2-check.log` (SHA256 `97fed1428ee2862b2f8c79e8bc4920b21fe64ab6c2285f55a723089731a032ac`), `/tmp/chembrain-keyboard-round2-baseline-check.log`, temporary harness `/tmp/chembrain_keyboard_round2_check.py`, build logs in `/tmp/chembrain-map-keyboard[-baseline]-build.log`. No real paper content was used by these probes.

Reviewed helper file SHA256:
- `src/SynthesisMap.tsx`: `c6fe90b0b77dc9c72cee937d581b498cce02ba3d03aea0a00ea8c1de2bcafd95`
- `scripts/synthesis_map_smoke.py`: `aa7e65c3146d61ea3af892328c4ac18f3eae7676fb9ba071a3806e6338ace879`

Root still must run aggregate checks and fresh exact-source hosted CI, both actual-file programs and handoff, then separate Independent QA/Revision/Wiki. These local HTTP checks do not prove file:// support or final delivery readiness. No alternate browser or managed-file-policy workaround was used.
