# Development — recorded synthesis graph

Role: delegated Development implementation, not independent approval. Baseline inspected: `aaf4d8b13d4604e98458cd6eec59cc8205254bae`. Final integrated source SHA and downloadable-file verification are recorded by the coordinating Development agent and independently reviewed afterward.

## Changed files

- `src/synthesisGraph.ts`: pure browser-independent projection of selected-molecule chemistry. Only actual recorded reactant → reaction → product relationships become edges. Direct transformations, target-tagged route members and recursively recorded precursor transformations are included. Namespace-prefixed chemical and reaction IDs cannot collide across normalized tables. Repeated endpoints are deduplicated. Connected components remain separate; iterative strongly connected component condensation keeps cycles finite. Deterministic layout and no library mutation.
- `src/SynthesisMap.tsx`: existing ReactFlow dependency renders distinct molecule/reaction cards, draft/review labels, selected-molecule outline, active reaction highlight, direction arrows and partial-fragment notices. Clicking a real button calls the root molecule/reaction callback. Existing depiction callback preserves honest unknown-structure placeholders. Zoom, Fit and target focus operate locally. Pan and header drag affect presentation only; no layout persistence, APIs or added assets/dependencies.
- `src/synthesis-map.css`: namespaced canvas/cards/controls, focus indication and mobile heights.
- `tests/test_synthesis_graph.py`: actual Node TypeScript runtime checks, rather than source-text matching.

## Boundaries and interface

`buildSynthesisGraph(library, selectedId, {maxNodes?,maxReactions?})` returns nodes, exact edges, displayed reaction IDs, selected/focus node IDs, component count and truncation flag. Defaults: 360 nodes / 120 reactions; caller limits are themselves bounded to at most 1000 / 400. If a whole reaction cannot fit with every participant, it is omitted and the graph is visibly labelled partial; no dangling edge or trimmed convergence is rendered. Queued traversal stops at the reaction cap, and visited sets prevent cycles.

`SynthesisMap` accepts `library`, `selectedId`, `onSelectMolecule`, `onSelectReaction`, `depiction` and optional `activeReactionId`. Initial desktop focus includes the selected molecule, included direct reactions and every participant in those reactions. Mobile target focus keeps the selected card legible; users pan or Show all recorded steps to inspect the rest. Map/List selection and the condition/DOI inspector belong to the root integration.

When all candidate reactions are omitted by the node cap, the empty canvas explains that no complete reaction fits the display limit and directs the user to List. The no-recorded-reactions message applies only when traversal was not truncated; oversized records are not mislabelled absent.

Accessible selectors for browser evidence:

- Map root: `section.synthesis-map`, labelled `Recorded synthesis map`.
- Canvas: `.synthesis-canvas`; ReactFlow node types `synthesisMolecule` / `synthesisReaction`.
- Card buttons: `Open molecule: NAME` and `Open reaction: NAME`; keyboard Enter/Space uses native buttons. Drag handle: `.synthesis-drag`.
- Controls: `Zoom in synthesis map`, `Zoom out synthesis map`, `Fit synthesis map` (visible text `Show all recorded steps`), `Focus selected molecule`.
- Scope text: `8 recorded reactions · 5 connected fragments` for paclitaxel, `4 recorded reactions · 2 connected fragments` for doxycycline. Only exact recorded relationships join fragments.

## Development verification

- `./node_modules/.bin/tsc --noEmit`: PASS.
- `.venv/bin/python -m pytest -q tests/test_synthesis_graph.py`: 5 PASS.
- Focused runtime cases: both real seed routes and absence of false Baran/Holton connections; synthetic two-input convergence, alternatives and precursor context; target membership with no inferred target edges; cycles, repeated participants, imported same-ID chemical/reaction records and unconnected selection; 700-step imported chain hitting explicit bounds and oversized convergent reaction omitted atomically while a smaller reaction remains valid. All displayed participant/edge endpoints are checked and determinism/nonmutation asserted.

No browser evidence is claimed in this helper report; root extends the actual hosted and standalone-file smoke tests and inspects the integrated graph. Independent QA/Revision have not been replaced by these Development checks. No commits, pushes, build output, root integration, paper data, permission or history changes were performed by this helper.
