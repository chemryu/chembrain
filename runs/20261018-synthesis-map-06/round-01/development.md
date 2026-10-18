# Development — branching synthesis map

Frozen pushed source: **e6ed4e70028fa77dfd59cbeede249ccc1a52b274**, baselineaaf4d8b. Separate Planning preceded implementation; root owns UI integration/shared real-browser regressions/docs, Development helper owns graphprojection/component/CSS/coretests. No prior-source approval transfers.

## Result

Selecting a molecular tile opens Map by default. Selected molecule, intermediate and reaction nodes connect only using normalized reactants/products; route targets choose context but never invent a chemical arrow. Direct records, recorded precursor closure and target-tagged fragments are cycle-safe, deterministic and namespaced. Atomic display caps360nodes/120reactions keep all participants in each displayed reaction; disconnected/gapped and capped context has explicit labels. Oversized-all-omitted reactions are distinguished from no recorded reactions; capped counts say displayed. Unknown structures retain placeholders.

Existing @xyflow/react supplies pan/zoom/fit and draggableheaders; no new dependency/API/resource service. Initial focus includes selected molecule+directrecordparticipants. Complete recorded fragments are available via Show all recorded steps. Reaction buttons open the existing conditions/solution/yield/DOI/edit renderer; graphchemicalbuttons refocus context. Map and List have clearly separate scope; List preserves direct-records filter/cards. Exploration writes no chemistry/storage. Opening inspection preserves draggedpositions. Save/import clears stale inspector; fresh edited/imported facts rebuild graph. Initial screen remains unselected/no map.

Metadata-only boundary, English UI, private local backups, no PDF/sourceprose/crops and standalone offlinebuild remain. No mainmerge/Public/history rewrite/schedule/PC/Box action.

## Actual Development checks

Full pytest **289PASS/1WindowsDPAPISKIP**, existing Starlette/httpx deprecation warning. Graph pure runtime **5PASS**, TypeScript PASS. Production hosted browser smoke PASS with all previous editing/persistence/import/DOI/legacyfailure checks retained through explicit List view. New shared map assertions verify targetbranches/fragments, direction presence, pan/zoom/fit, actualheaderdrag and retainedposition oninspection, keyboardmolecule/reactionactivation, three-stage solution/oneDOI, noexplorationwrites, contextreset, edit/renamegraphrefresh, importnewreactiongraphrefresh, genuineorphan, oversized400-inputreactionatomicomission+truthfulcapmessage/Listfallback, mobile. Raw testfixture packages live only in disposable browser context and are restored before subsequent regression flows; they are not distributed chemistry. First added drag locator incorrectly nested the already-rooted scope in a has-filter; corrected test locator and reran successfully before freeze (not app defect).

Visually inspected actual screenshots /tmp/chembrain-synthesis-map.png and -all.png: two Taxol final branches converge on the selected target; recorded disconnected fragments are separate. Known sparse total-synthesis data remains12draftrecords/3papers/49chemicals.

Source payload **156filesPASS**; dist payload **13filesPASS**. Exact-source standalone rebuild and HTTP-only map regression are in progress. Localactualfile remains NOTRUN due managedadminURLpolicy; policy not changed or bypassed. Required actualfileCI on separate normal runner and exact artifact digest remain pending.

Reusable environment draft repository pointer updated to this frozen source; installation/start instructions unchanged and still apply, requiresPublish=true. Draft save is not website publication. Previoushistory quotation/crops and remoteartifactcacheUNVERIFIED stay NOTCLEAREDforPublic. Pages403 awaits new observation.
