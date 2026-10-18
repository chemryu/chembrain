# Planning — molecule-selected synthesis brainstorming map

- Run/round: `20261018-synthesis-map-06 / round-01`.
- Role: separate Planning, before application implementation.
- Inspected baseline source: `aaf4d8b13d4604e98458cd6eec59cc8205254bae`.
- Latest user: “molecule을 누르면 brainstorming처럼 합성과정이 나오게 해줘.”
- Final QA/Revision must target the new complete source SHA and its actual downloadable HTML; this baseline's previous approval does not transfer.

## Scope and resulting behavior

Clicking a molecular-library tile opens an interactive branching synthesis map in the ordinary English browser application and the same install-free `Chembrain.html`. The selected molecule is visually distinct. Molecule cards connect through reaction cards, allowing recorded convergent reactants, products, alternative routes and intermediate steps to be understood spatially. Pan, zoom and Fit controls make a large route navigable. Clicking a reaction opens its existing conditions, solvent/solute, yield, draft/review status and deduplicated DOI/author details. Preserve record editing, the accessible reaction list, browser persistence and JSON backup/import.

Before a molecule is selected, retain the current empty reaction panel: no automatic route or molecule selection. The map is an evidence viewer, not an API-driven synthesis generator. No paper collection, schedule activation, dependency changes, desktop redesign, Public toggle, Pages permission changes, history rewrite or main merge belong to this feature.

## Data inspection and chemistry boundary

The baseline has normalized `Chemical`, `RecordReaction` and `Solution` types in `src/libraryData.ts`. Each reaction's `reactants` and `products` hold actual chemical IDs. Its `targets` is route membership, not a recorded chemical transformation. Conditions and solution stages do not define additional reactant/product edges. The old `src/Graph.tsx` belongs to the explicit desktop API model and references `/api/molecules/...`; copying that model into the offline browser would break this boundary. The existing `@xyflow/react` dependency is available for a browser-only component.

The current seed comprises 12 draft records from three DOI references. It is incomplete, not a reconstruction of every transformation in those total syntheses:

- Paclitaxel: eight target-tagged records. Baran `baran-19 → baran-20 → baran-21 → baran-22` is a genuine three-reaction connected fragment. `baran-34 + baran-35 → paclitaxel` is a separate recorded final coupling. Holton `5 → 6`, `17 → 18`, `20b → 21`, and `24b + 25 → paclitaxel` likewise do not have recorded connecting reactions.
- Doxycycline: `charest-13 + charest-14 → charest-15 → charest-16` and `charest-5 + charest-20 → charest-21 → doxycycline` are two separate recorded fragments.

Draw only exact `chemical ID → reaction ID → chemical ID` edges present in reactants/products. Never join fragments using shared DOI, paper order, names, step numbering, or `targets`. Display a clear English notice that separate fragments have unrecorded connecting steps. Unknown structures remain labelled placeholders; do not invent SMILES, conditions, structures, yields or transformations. Draft status remains visible. Paper metadata stays DOI/authors only, with existing concise chemistry facts and evidence locators.

## Smallest useful implementation

1. Add a pure normalized-graph projection helper and a separate browser map component. Namespace molecule and reaction node IDs so imported IDs cannot collide across tables. Map edges retain direction and convergent participants; deduplicate repeated endpoints without duplicating reactions.
2. On molecule selection, include its directly related recorded transformations and recursive recorded precursor transformations. For target molecules, show their recorded target-tagged synthesis steps by default so the user actually sees the synthesis fragments, not only final coupling cards. Preserve a clear scope control to restrict to directly related records if useful. Any expanded scope must be reflected in the list/count/legend. No implicit shared-tag edge is permitted.
3. Arrange actual connected components so disconnected fragments remain spatially separate. Label selected molecule, chemical and reaction node types, edge direction, draft/review state and incomplete-route limitation. Long names wrap or truncate with accessible full text. Conditions remain readable in the existing HTML detail view rather than tiny graph labels.
4. Provide working pan, zoom in/out and Fit controls without backend/network requests. Reaction selection opens its card/details and has a visible active state. Retain the keyboard-accessible card list as an alternative; add accessible control names and reaction-node activation. Avoid inventing a full graph editor or saving node layout as chemistry data.
5. Bound traversal and rendering for imported libraries. Use visited sets for cycles and shared intermediates; deterministic output; do not recurse forever. If records exceed the chosen explicit cap/depth, show an honest visible truncation message and keep every displayed reaction's participant nodes/edges. Never silently present a capped graph as complete. Disconnected/no-reaction molecules produce an understandable empty state.
6. Keep the single HTML build offline and self-contained, with no `/api` calls or remote fonts/images/layout services. Local storage/import data does not change merely by exploring the graph. Existing fixed-source artifact identity/checksums and payload gates remain intact.

## Acceptance and required evidence

### Focused graph projection tests

Use real runtime TypeScript checks through existing Node/Python test conventions, not source-text assertions.

- Seed paclitaxel and doxycycline expose recorded multi-step and convergent fragments; edge sets contain only actual reactant/product relationships. In particular, Baran22 is not connected to Baran34 or paclitaxel without an intervening recorded reaction; Holton fragments are not falsely chained.
- A synthetic fully connected convergent/alternative route renders complete participants and correct arrow direction. A selected intermediate can show its recorded context without unrelated DOI-only reactions.
- Cycles, shared intermediates, duplicate participant entries, imported cross-table ID collisions and no-related-reaction selections are safe/deterministic/nonmutating.
- Large imported route reaches an explicit bound, returns a truncation indication, and never leaves a displayed edge without both endpoints.

### Real browser checks

Extend the existing smoke suite rather than replacing its persistence/edit/import coverage. On the actual built web app at `/chembrain/`, verify initial blank selection, molecule click → visible map, correct connected/fragmented seed graph, working zoom/Fit and pan/drag behavior, reaction activation → solvent/solute/conditions/DOI detail, and a molecule with no recorded reaction. Ensure editing and import cause the visible map to refresh, without overwriting user edits. Check mobile width, browser errors, accessible list fallback and no backend requests.

Build the actual single-file portable HTML and run equivalent essential map/selection/detail controls from `file://` with network blocked. Preserve the existing offline, storage failure, backup/import and hostile embedding checks. Record the artifact's real bytes/SHA-256 and source SHA; do not claim that development-server smoke proves downloadable file behavior.

Run appropriate focused tests, full existing Python suite, ordinary web TypeScript/production build, standalone build, source/dist payload gates and real browser smoke. CI's fresh exact-source result is preferred for the delivered artifact. Existing Pages403 remains an external limitation; a tested downloadable HTML does not need a working hosted Pages URL.

## Review and handoff

Development implements the plan and records changed paths, commands, results and the frozen new SHA. Separate Independent QA independently checks scientific connectivity, interaction, cap/cycle behavior and actual offline output. Separate Revision compares QA and implementation, returns actionable findings or zero unresolved material findings for that exact SHA. Wiki preserves both complete reports and hashes, writes the run's handoff, and updates current progress without erasing earlier reports. If a material finding remains, return through Wiki to Planning for the next bounded round. Stop when both independent reviews have no unresolved material findings and required checks pass for the delivered source/artifact.

The known historical quotation/crop blobs, unverified remote Actions storage, Pages403, private browser storage/file-location limits, inactive collection schedule and lack of Box direct sync remain outside this feature and must not be reclassified as fixed.

## Agreed UI integration addendum (before implementation)

Development proposed and Planning accepts a default **Map** tab after molecule selection plus an explicit **List** tab. The Map uses the full normalized library and selected chemical to display recorded synthesis context/fragments; the List retains its existing direct-related default and `Include synthesis-route steps` checkbox. Each view labels its own scope/count so the eight paclitaxel route records are not confused with the two direct records. A Map reaction click opens one condition/DOI/edit inspector using the existing detail renderer; chemical activation may refocus the selected molecule. A selected inspector must reset when its reaction no longer belongs to the displayed context. Map target-focus/show-all controls refer to the selected molecule's recorded synthesis context, never every unrelated reaction in the library. Existing browser edit/list regressions may switch explicitly to List; new dedicated tests must exercise the default Map.
