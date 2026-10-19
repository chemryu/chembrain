import { useEffect,useRef,useState } from 'react';
import { BookOpen,Download,Upload,Search,Hexagon,ArrowRight,FlaskConical,X,ChevronDown } from 'lucide-react';
import {emptyLibrary,validateLibrary,projectLegacyLibrary,mergeLibrary,relatedReactions,paperReferences,type Library,type Chemical,type RecordReaction} from './libraryData';
import './web.css';
import { RecordFields, parseRecordDraft } from './RecordFields';
import { SynthesisMap } from './SynthesisMap';
import StructureDiagram from './StructureDiagram';
import {inspectStructure,type StructureInspection} from './structureRenderer';
import {prepareImportReview,assertImportBaseline,commitReviewedImport,paperLabelAliases,hasExistingImportChanges,type ImportReviewPlan,type VerifiedImportGraphMatch} from './importReview';
import './import-review.css';
import {LIBRARY_STORE,verifiedExampleCount,saveVerifiedExamples} from './verifiedExamples';
import {library as portableLibrary} from 'virtual:chembrain-portable-data';
const portable=import.meta.env.MODE==='portable';
const STORE=LIBRARY_STORE;
const base=import.meta.env.BASE_URL;
export function MolecularLibrary(){
 // Fresh starter rows must not override a user's imported backup. Once saved,
 // browser edits keep precedence over later feed/package imports.
 const hasSavedLibrary=useRef(false);
 const importSequence=useRef(0);
 const [importReview,setImportReview]=useState<{plan:ImportReviewPlan;raw:string|null}|null>(null);
 const [importResult,setImportResult]=useState<ImportReviewPlan|null>(null);
 const [importing,setImporting]=useState(false);
 const [view,setView]=useState<'map'|'list'>('map');
 const [inspected,setInspected]=useState<string|null>(null);
 const [recoveryBlocked,setRecoveryBlocked]=useState(false);
 const [data,setData]=useState<Library>(emptyLibrary),[selected,setSelected]=useState<string|null>(null),[query,setQuery]=useState(''),[route,setRoute]=useState(false),[error,setError]=useState(''),[notice,setNotice]=useState(''),[loading,setLoading]=useState(true),[editor,setEditor]=useState<{kind:'chemical'|'reaction'|'paper'|'solution';id:string;value:string}|null>(null),[open,setOpen]=useState<string|null>(null);const input=useRef<HTMLInputElement>(null);
 useEffect(()=>{
  let active=true;
  async function load(){
   let stored:Library|undefined;let originalPresent=false;let migrated=false;
   try{
    const raw=localStorage.getItem(STORE);originalPresent=raw!==null;
    if(raw){
     const parsed:unknown=JSON.parse(raw);
     try{stored=validateLibrary(parsed);}
     catch{
      const projected=projectLegacyLibrary(parsed);
      // Backup the original bytes BEFORE writing any compact replacement. Never
      // overwrite another private backup, and fail closed if browser storage fails.
      const key=STORE+'.legacy-backup.'+crypto.randomUUID();
      try{localStorage.setItem(key,raw);if(localStorage.getItem(key)!==raw)throw new Error('Backup verification failed.');}
      catch{throw new Error('Legacy migration paused: a private browser backup could not be saved. Free browser storage and reload; the original data remains untouched.');}
      stored=projected;migrated=true;
      if(active)setNotice('Legacy metadata was removed from the working library. Its exact original bytes were backed up privately in this browser ('+key+'). This private backup is not included in compact exports or GitHub uploads.');
     }
    }
    hasSavedLibrary.current=stored!==undefined;
    let remote:Library;
    if(portable)remote=validateLibrary(portableLibrary);
    else{
     const r=await fetch(base+'library.json');
     if(!r.ok)throw new Error('Library update could not be loaded.');
     remote=validateLibrary(await r.json());
    }
    const d=stored?mergeLibrary(stored,remote):remote;
    if(stored&&(migrated||JSON.stringify(d)!==JSON.stringify(stored)))localStorage.setItem(STORE,JSON.stringify(d));
    if(active)setData(d);
   }catch(e){if(active){if(stored)setData(stored);else if(originalPresent)setRecoveryBlocked(true);else if(portable){setData(validateLibrary(portableLibrary));setRecoveryBlocked(true);}setError((e as Error).message+' Existing browser data was not replaced.');}}
   finally{if(active)setLoading(false);}
  }
  void load();return()=>{active=false;};
 },[]);
 function save(next:Library){if(recoveryBlocked)throw new Error('Resolve browser data recovery and reload before saving.');const valid=validateLibrary(next);localStorage.setItem(STORE,JSON.stringify(valid));hasSavedLibrary.current=true;setData(valid);setInspected(null);}
 function download(){if(recoveryBlocked)return;const url=URL.createObjectURL(new Blob([JSON.stringify(data)],{type:'application/json'}));const a=document.createElement('a');a.href=url;a.download='chembrain-library.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);}
 function importedNotice(plan:ImportReviewPlan){return `Import complete: ${plan.changed?'':'no changes. '}${plan.added.chemicals} new molecules, ${plan.added.solutions} new solutions, ${plan.added.reactions} new reactions; ${plan.changedExisting.chemicals} existing molecules, ${plan.changedExisting.solutions} existing solutions and ${plan.changedExisting.reactions} existing reactions updated; ${plan.upgrades.length} existing structures added; ${plan.labelAdditions.reduce((n,row)=>n+row.aliases.length,0)} paper labels added. ${plan.retentions.length} existing field value(s) retained.`;}
 const importValue=(value:unknown)=>value==null?'Not recorded':typeof value==='string'?(value||'(empty)'):JSON.stringify(value,null,2);
 function retainedFacts(plan:ImportReviewPlan){return !!plan.retentions.length&&<details className="import-retentions"><summary>{plan.retentions.length} existing field value(s) retained</summary><ul aria-label="Retained import facts">{plan.retentions.map((row,index)=><li key={index}><strong>{row.name}</strong><small>{row.table} · {row.id} · {row.field}</small><dl><dt>Previous</dt><dd><pre>{importValue(row.previous)}</pre></dd><dt>Incoming</dt><dd><pre>{importValue(row.incoming)}</pre></dd></dl><p>{row.reason}</p></li>)}</ul></details>;}
 async function importFile(file?:File){
  if(!file||recoveryBlocked)return;
  const sequence=++importSequence.current;setError('');setNotice('');setImportReview(null);setImportResult(null);setImporting(true);
  try{
   if(file.size>5_000_000)throw new Error('Use a normalized JSON package below 5 MB.');
   let incoming=validateLibrary(JSON.parse(await file.text()));
   const raw=localStorage.getItem(STORE);
   let plan=prepareImportReview(data,incoming,hasSavedLibrary.current);
   assertImportBaseline(plan,localStorage,raw);
   const graphChecks=new Map<string,Promise<StructureInspection>>();
   const inspect=(smiles:string)=>{let check=graphChecks.get(smiles);if(!check){check=inspectStructure(smiles);graphChecks.set(smiles,check);}return check;};
   const verifyMetadata=(chemical:Chemical,graph:StructureInspection,stored=false)=>{
    if((chemical.inchikey&&chemical.inchikey!==graph.inchikey)||(chemical.formula&&chemical.formula!==graph.formula)||(chemical.molecular_weight!=null&&Math.abs(chemical.molecular_weight-graph.molecular_weight)>=0.02))throw new Error(`${stored?'Stored molecule':'Import rejected'}: ${chemical.name} (${chemical.id}) has structure metadata that does not match its SMILES. Correct ${stored?'the existing record before importing':'and export it again in Paper Workbench'}.`);
   };
   const matches:VerifiedImportGraphMatch[]=[];
   if(hasSavedLibrary.current)for(const candidate of incoming.chemicals){
    const existing=data.chemicals.find(c=>c.id===candidate.id)||data.chemicals.find(c=>candidate.inchikey&&c.inchikey===candidate.inchikey);
    if(!existing?.smiles?.trim()||!candidate.smiles?.trim())continue;
    const needsLabels=paperLabelAliases(candidate,incoming).some(alias=>!existing.aliases.includes(alias));
    if(existing.smiles===candidate.smiles&&!needsLabels)continue;
    const [currentGraph,incomingGraph]=await Promise.all([inspect(existing.smiles),inspect(candidate.smiles)]);
    verifyMetadata(existing,currentGraph,true);verifyMetadata(candidate,incomingGraph);
    if(currentGraph.canonical_smiles===incomingGraph.canonical_smiles&&currentGraph.inchikey===incomingGraph.inchikey&&currentGraph.formula===incomingGraph.formula)matches.push({currentId:existing.id,incomingId:candidate.id,currentSmiles:existing.smiles,incomingSmiles:candidate.smiles,canonicalSmiles:incomingGraph.canonical_smiles,inchikey:incomingGraph.inchikey,formula:incomingGraph.formula});
   }
   plan=prepareImportReview(data,incoming,hasSavedLibrary.current,matches);
   if(plan.conflicts.length){if(sequence===importSequence.current)setImportReview({plan,raw});return;}
   // A processor's supplied descriptors must agree with its actual molecular
   // graph before filling an existing blank structure. Source review remains
   // the Workbench user's responsibility, independently of parser validity.
   for(const upgrade of plan.upgrades){
    const candidate=incoming.chemicals.find(c=>c.id===upgrade.id)!;
    const graph=await inspect(upgrade.smiles);
    verifyMetadata(candidate,graph);
    incoming={...incoming,chemicals:incoming.chemicals.map(c=>c.id===candidate.id?{...c,smiles:graph.canonical_smiles,inchikey:c.inchikey||graph.inchikey,formula:c.formula||graph.formula,molecular_weight:c.molecular_weight??graph.molecular_weight}:c)};
   }
   if(sequence!==importSequence.current)return;
   plan=prepareImportReview(data,incoming,hasSavedLibrary.current,matches);
   assertImportBaseline(plan,localStorage,raw);
   if(hasExistingImportChanges(plan)||plan.conflicts.length){setImportReview({plan,raw});return;}
   if(plan.changed)save(plan.next!);
   setNotice(importedNotice(plan));setImportResult(plan);
  }catch(e){if(sequence===importSequence.current)setError((e as Error).message);}
  finally{if(sequence===importSequence.current)setImporting(false);if(input.current)input.current.value='';}
 }
 function applyImport(){
  if(!importReview||recoveryBlocked)return;setError('');
  try{const next=commitReviewedImport(importReview.plan,localStorage,importReview.raw);hasSavedLibrary.current=true;setData(next);setInspected(null);setNotice(importedNotice(importReview.plan)+' The exact original library was backed up privately in this browser.');setImportResult(importReview.plan);setImportReview(null);}
  catch(e){setError((e as Error).message);}
 }
 function editSave(){if(!editor)return;setError('');try{parseRecordDraft(editor.kind,editor.value);const row=JSON.parse(editor.value);if(row.id!==editor.id)throw new Error('Keep the entity ID unchanged.');const next=structuredClone(data);if(editor.kind==='chemical'){const previous=data.chemicals.find(x=>x.id===editor.id);if(row.smiles!==previous?.smiles){delete row.inchikey;delete row.formula;delete row.molecular_weight;row.notes=(row.notes||'')+' SMILES edited locally; normalize with the processor before trusting structure metadata.';}next.chemicals=next.chemicals.map(x=>x.id===editor.id?row:x);}else if(editor.kind==='paper')next.papers=next.papers.map(x=>x.id===editor.id?row:x);else if(editor.kind==='solution')next.solutions=next.solutions.map(x=>x.id===editor.id?row:x);else next.reactions=next.reactions.map(x=>x.id===editor.id?row:x);save(next);setEditor(null);setNotice('Changes saved in this browser.');}catch(e){setError((e as Error).message);}}
 const molecule=data.chemicals.find(c=>c.id===selected);const names=(ids:string[])=>ids.map(id=>data.chemicals.find(c=>c.id===id)?.name||id).join(' + ');const related=relatedReactions(data,selected,route);const chemicals=data.chemicals.filter(c=>c.kind==='compound'&&[c.name,c.smiles||'',...c.aliases].join(' ').toLowerCase().includes(query.toLowerCase())).sort((a,b)=>Number(['paclitaxel','doxycycline'].includes(b.id))-Number(['paclitaxel','doxycycline'].includes(a.id))||a.name.localeCompare(b.name));
 const depiction=(c:Chemical)=><StructureDiagram chemical={c}/>;
 const exampleCount=verifiedExampleCount(data);
 function addExamples(){if(recoveryBlocked)return;setError('');try{const next=saveVerifiedExamples(data,localStorage);hasSavedLibrary.current=true;setData(next);setNotice('Verified example structures added. Your original library was backed up privately in this browser. Other records and edits were retained.');}catch(e){setError((e as Error).message);}}

 function details(r:RecordReaction){return <div className="reaction-expanded"><div className="record-actions"><span>{r.yield_basis}</span><button onClick={()=>setEditor({kind:'reaction',id:r.id,value:JSON.stringify(r,null,2)})}>Edit record</button></div>{r.steps.map((s,i)=>{const solution=data.solutions.find(x=>x.id===s.solution_id)!;return <section className="step" key={i}><h4>Step {i+1} <button onClick={()=>setEditor({kind:"solution",id:solution.id,value:JSON.stringify(solution,null,2)})}>Edit solution</button></h4><dl><dt>Solvent(s)</dt><dd>{names(solution.solvents)||'Not reported'}</dd><dt>Solute(s)</dt><dd>{solution.solutes.map((c,j)=><div key={j}>{names([c.chemical_id])} <small>· {c.role}{c.amount!=null?` · ${c.amount} ${c.unit||''}`:''}</small></div>)}</dd><dt>Concentration</dt><dd>{solution.concentration??'Not reported'} {solution.concentration_unit}</dd><dt>Temperature / time</dt><dd>{s.temperature||'Not reported'} · {s.time||'Not reported'}</dd></dl>{s.notes&&<p>{s.notes}</p>}</section>;})}<p className="record-note">{r.notes}</p><h4>References ({paperReferences(data,r).length})</h4>{paperReferences(data,r).map(({paper,evidence})=><div className="paper-reference" key={paper.id}><a href={'https://doi.org/'+paper.doi} target="_blank" rel="noreferrer">{paper.doi} ↗</a><p>{paper.authors.join('; ')}</p><button onClick={()=>setEditor({kind:"paper",id:paper.id,value:JSON.stringify(paper,null,2)})}>Edit citation</button>{evidence.map((e,i)=><small key={i}>PDF page {e.page} · {e.locator}</small>)}</div>)}</div>;}
 function chooseMolecule(id:string){setSelected(id);setOpen(null);setRoute(false);setView('map');setInspected(null);}
 function reactionCard(r:RecordReaction){return <article className="web-reaction" key={r.id} data-reaction-id={r.id}>
  <button className="reaction-summary" aria-expanded={open===r.id} onClick={()=>setOpen(open===r.id?null:r.id)}>
   <div><span className={'review-label '+r.status}>{r.status==='reviewed'?'Reviewed record':'Draft · verify against source'}</span><h3>{r.name}</h3><p>{names(r.reactants)} <ArrowRight size={15}/> {names(r.products)}</p></div>
   <div className="yield-badge">{r.yield_percent==null?'—':r.yield_percent+'%'}<small>reported yield</small><ChevronDown size={16}/></div>
  </button>{open===r.id&&details(r)}
 </article>;}
 const inspectedReaction=data.reactions.find(r=>r.id===inspected);
 return <div className="web-shell">
  <header className="web-header">
   <a href={portable?'#':base} className="web-brand"><Hexagon/>chembrain<span>.</span></a>
   <span className="web-tag">{portable?'PREVIEW · LOCAL BROWSER FILE':'PREVIEW · MOLECULE-FIRST LIBRARY'}</span>
   <div className="web-tools"><button onClick={()=>input.current?.click()} disabled={loading||recoveryBlocked||importing}><Upload size={16}/>{importing?'Checking import…':'Import package'}</button><button onClick={download} disabled={loading||recoveryBlocked}><Download size={16}/>Backup JSON</button></div>
   <input ref={input} type="file" accept=".json,application/json" aria-label="Import normalized library" hidden onChange={e=>void importFile(e.target.files?.[0])}/>
  </header>
  <div className="web-intro"><div><p className="web-kicker">LESS PAPER. MORE CHEMISTRY.</p><h1>Your molecular library</h1><p>Choose a molecule to explore its synthesis map, conditions and DOI references.</p></div><span className="browser-storage">Saved in this browser<br/><small>{portable?'Keep this file in the same location. Use Backup JSON before moving or updating it.':'Export a backup to move between devices'}</small></span></div>
  {error&&<div className="web-alert" role="alert">{error}<button aria-label="Dismiss error" onClick={()=>setError('')}><X size={16}/></button></div>}
  {notice&&<div className="web-notice" role="status">{notice}<button aria-label="Dismiss notice" onClick={()=>setNotice('')}><X size={16}/></button></div>}
  {!importReview&&importResult&&retainedFacts(importResult)}
  {importReview&&<section className="import-review" aria-label="Review paper import">
   <h2>Review paper import</h2>
   {importReview.plan.conflicts.length?<>
    <p>This package has conflicting IDs or known chemistry facts. No records were imported. Export the latest main Backup JSON, load it in Paper Workbench and reconcile the exact fields below. Preserve current IDs, ordered stages and known local values; source-check and export again. A different molecule or synthesis step needs its own intentional paper-scoped ID.</p>
    <ul className="import-conflicts" aria-label="Import conflicts">{importReview.plan.conflicts.map((conflict,index)=><li key={index}><strong>{conflict.table} · {conflict.id}{conflict.field&&' · '+conflict.field}</strong><span>{conflict.reason}</span>{conflict.field&&<dl><dt>Previous</dt><dd><pre>{importValue(conflict.previous)}</pre></dd><dt>Incoming</dt><dd><pre>{importValue(conflict.incoming)}</pre></dd></dl>}</li>)}</ul>
   </>:<>
    <p>Review {importReview.plan.upgrades.length} missing structure(s) and {importReview.plan.labelAdditions.reduce((n,row)=>n+row.aliases.length,0)} added paper label(s). Your names, notes, existing aliases, structures and other edits are retained. Check these facts against the source in Paper Workbench before applying.</p>
    <p>{importReview.plan.added.chemicals} new molecules · {importReview.plan.added.reactions} new reactions · {importReview.plan.added.solutions} new solutions · {importReview.plan.added.papers} new papers</p>
    <p>{importReview.plan.changedExisting.chemicals} existing molecules · {importReview.plan.changedExisting.solutions} existing solutions · {importReview.plan.changedExisting.reactions} existing reactions will be updated.</p>
    <ul>{importReview.plan.upgrades.map(row=><li key={row.id}><strong>{row.name}</strong><small>{row.id} · adding {row.fields.join(', ')}</small><StructureDiagram chemical={importReview.plan.next!.chemicals.find(c=>c.id===row.id)!}/></li>)}</ul>
    {!!importReview.plan.labelAdditions.length&&<ul aria-label="Paper labels to add">{importReview.plan.labelAdditions.map(row=><li key={row.id}><strong>{row.name}</strong>{row.aliases.map(alias=><small key={alias}>{alias}</small>)}</li>)}</ul>}
    {!!importReview.plan.factChanges.length&&<ul aria-label="Existing chemistry changes">{importReview.plan.factChanges.map((row,index)=><li key={index} data-record-id={row.id} data-field={row.field}><strong>{row.name}</strong><small>{row.table} · {row.id} · {row.field} · {row.action}</small><dl><dt>Previous</dt><dd><pre>{importValue(row.previous)}</pre></dd><dt>Incoming</dt><dd><pre>{importValue(row.incoming)}</pre></dd></dl></li>)}</ul>}
    {retainedFacts(importReview.plan)}
    <p>The original library will be backed up privately in this browser before the import is saved.</p>
    <button className="web-primary" onClick={applyImport}>Apply import</button>
   </>}
   <button onClick={()=>{setImportReview(null);setError('');}}>Cancel import</button>
  </section>}
  {exampleCount>0&&!loading&&!recoveryBlocked&&<div className="example-structures"><p>{exampleCount} matching example molecule(s) have no structure. Add verified parent structures for Taxol / doxycycline; your notes and other records are retained.</p><button onClick={addExamples}>Add verified example structures</button></div>}
  <main className="web-columns">
   <aside className="molecular-panel">
    <div className="panel-heading"><h2><Hexagon size={17}/>Molecular library</h2><span>{chemicals.length}</span></div>
    <label className="web-search"><Search size={17}/><input aria-label="Search molecular library" placeholder="Name, alias or SMILES" value={query} onChange={e=>setQuery(e.target.value)}/></label>
    {loading?<p className="web-empty">Loading library…</p>:<div className="molecular-grid">{chemicals.map(c=><button className={'molecule-tile '+(selected===c.id?'active':'')} key={c.id} onClick={()=>chooseMolecule(c.id)} aria-pressed={selected===c.id}>{depiction(c)}<strong>{c.name}</strong><small>{c.formula||'Paper-specific intermediate'}</small></button>)}</div>}
    {!loading&&!chemicals.length&&<p className="web-empty">No matching molecules.</p>}
   </aside>
   <section className="reaction-panel">
    {!molecule?<div className="selection-empty"><div><Hexagon size={38}/></div><h2>Select a molecule</h2><p>Its synthesis map will appear here.</p><span>No reaction is selected automatically.</span></div>:<>
     <header className="selected-heading"><div><p className="web-kicker">SELECTED MOLECULE</p><h2>{molecule.name}</h2><p>{molecule.formula||'Structure pending'} {molecule.inchikey&&'· '+molecule.inchikey}</p></div><button onClick={()=>setEditor({kind:'chemical',id:molecule.id,value:JSON.stringify(molecule,null,2)})}>Edit molecule</button></header>
     <figure className="selected-structure"><StructureDiagram chemical={molecule} large/><figcaption>{molecule.smiles?'Diagram from recorded SMILES · molecular identity does not verify a draft reaction.':'A verified structure is needed for this paper-specific compound.'}</figcaption></figure>
     {molecule.notes&&!(molecule.smiles&&molecule.notes==='Structure not encoded; compound label is local to the cited paper.')&&<p className="molecule-note">{molecule.notes}</p>}
     <div className="library-view-tabs" role="tablist" aria-label="Synthesis display">
      <button role="tab" aria-selected={view==='map'} onClick={()=>{setView('map');setInspected(null);}}>Map</button>
      <button role="tab" aria-selected={view==='list'} onClick={()=>{setView('list');setInspected(null);}}>List</button>
     </div>
     {view==='map'?<>
      <SynthesisMap key={molecule.id} library={data} selectedId={molecule.id} activeReactionId={inspected} onSelectMolecule={chooseMolecule} onSelectReaction={id=>{setInspected(id);setOpen(id);}} depiction={depiction}/>
      {inspectedReaction&&<section className="map-reaction-inspector" aria-label="Selected reaction details"><h3>Selected reaction</h3>{reactionCard(inspectedReaction)}</section>}
     </>:<>
      <div className="related-toolbar"><h3><FlaskConical size={17}/>{related.length} related reactions</h3><label><input type="checkbox" checked={route} onChange={e=>setRoute(e.target.checked)}/>Include synthesis-route steps</label></div>
      {!related.length?<p className="web-empty">No recorded reactions for this molecule. Import a normalized package to add evidence.</p>:related.map(reactionCard)}
     </>}
    </>}
   </section>
  </main>
  <footer className="web-footer"><BookOpen size={16}/><span>Only chemistry facts, DOI and authors are shared. Source PDFs and paper images are excluded. Draft structures and conditions require review.</span><span>{data.papers.length} papers · {data.reactions.length} draft/curated records · {Math.ceil(JSON.stringify(data).length/1024)} KB data</span></footer>
  {editor&&<div className="web-modal-backdrop"><section className="web-editor" role="dialog" aria-modal="true" aria-label="Edit normalized record"><div><h2>Edit {editor.kind}</h2><button aria-label="Close editor" onClick={()=>{setEditor(null);setError('');}}><X/></button></div><p>Stable IDs link molecules, solutions and papers. Missing experimental values stay null.</p>{error&&<p role="alert">{error}</p>}<RecordFields kind={editor.kind} value={editor.value} chemicals={data.chemicals} onChange={value=>{setEditor({...editor,value});setError('');}}/><details><summary>Advanced normalized JSON</summary><textarea aria-label="Normalized record JSON" value={editor.value} onChange={e=>{setEditor({...editor,value:e.target.value});setError('');}}/></details><button className="web-primary" onClick={editSave}>Validate & save</button></section></div>}
 </div>;
}
