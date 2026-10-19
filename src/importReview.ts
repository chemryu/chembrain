import {mergeLibrary,validateLibrary,type Chemical,type Library} from './libraryData';
// Kept independent of JSON-loaded example fixtures so the handoff validator also
// runs without a browser; this is the same private library key as the main app.
const LIBRARY_STORE='chembrain.normalized-library.v1';

export type StructureImportUpgrade={id:string;name:string;fields:string[];smiles:string};
/** Supplied only by the UI's actual, two-graph RDKit preflight; never from JSON. */
export type VerifiedImportGraphMatch={currentId:string;incomingId:string;currentSmiles:string;incomingSmiles:string;canonicalSmiles:string;inchikey:string;formula:string};
export type ImportLabelAddition={id:string;name:string;aliases:string[]};
export type ImportConflict={id:string;table:'chemical'|'solution'|'reaction';reason:string};
export type ImportReviewPlan={
 baseline:string;saved:boolean;next:Library|null;upgrades:StructureImportUpgrade[];labelAdditions:ImportLabelAddition[];
 conflicts:ImportConflict[];added:{chemicals:number;reactions:number;solutions:number;papers:number};changed:boolean;
};
const text=(value:string|null|undefined)=>value?.trim()||'';
const sameIds=(a:string[],b:string[])=>JSON.stringify([...new Set(a)].sort())===JSON.stringify([...new Set(b)].sort());
export function paperLabelAliases(chemical:Chemical,incoming:Library):string[]{
 return chemical.aliases.filter(alias=>{
  const match=/^Paper label .+; DOI (10\.\d{4,9}\/[^\s<>?#]+)$/.exec(alias);
  return !!match&&incoming.papers.some(p=>p.doi===match[1]);
 });
}

/** Check the entire package before constructing an explicit, narrow enrichment.
 * General feed precedence is unchanged: names, notes, aliases and recorded routes
 * remain local. Identity collisions block the whole handoff, never just its row.
 */
export function prepareImportReview(current:Library,incoming:Library,saved=true,verifiedMatches:readonly VerifiedImportGraphMatch[]=[]):ImportReviewPlan {
 const before=validateLibrary(current),source=validateLibrary(incoming);
 const plan:ImportReviewPlan={baseline:JSON.stringify(before),saved,next:null,upgrades:[],labelAdditions:[],conflicts:[],added:{chemicals:0,reactions:0,solutions:0,papers:0},changed:false};
 const fail=(table:ImportConflict['table'],id:string,reason:string)=>plan.conflicts.push({table,id,reason});
 const mapping=new Map<string,string>();
 if(saved){
  for(const c of source.chemicals){
   const exact=before.chemicals.find(x=>x.id===c.id);
   const keyed=text(c.inchikey)?before.chemicals.filter(x=>text(x.inchikey)===text(c.inchikey)):[];
   if(keyed.length>1||(exact&&keyed.some(x=>x.id!==exact.id))){fail('chemical',c.id,'The ID and InChIKey identify different existing molecules.');continue;}
   const old=exact||keyed[0];mapping.set(c.id,old?.id||c.id);
   if(!old)continue;
   const verified=verifiedMatches.find(m=>m.currentId===old.id&&m.incomingId===c.id&&m.currentSmiles===old.smiles&&m.incomingSmiles===c.smiles&&text(m.canonicalSmiles)&&text(m.inchikey)&&text(m.formula)
    &&(!text(old.inchikey)||old.inchikey===m.inchikey)&&(!text(c.inchikey)||c.inchikey===m.inchikey)&&(!text(old.formula)||old.formula===m.formula)&&(!text(c.formula)||c.formula===m.formula));
   const issues:string[]=[];
   if(exact&&old.name!==c.name)issues.push('name differs');
   if(old.kind!==c.kind)issues.push('chemical role differs');
   if(text(old.smiles)&&text(c.smiles)&&text(old.smiles)!==text(c.smiles)&&!verified)issues.push('both records contain different, unverified SMILES graphs');
   if(text(old.inchikey)&&text(c.inchikey)&&text(old.inchikey)!==text(c.inchikey))issues.push('InChIKey differs');
   if(text(old.formula)&&text(c.formula)&&text(old.formula)!==text(c.formula))issues.push('formula differs');
   if(old.molecular_weight!=null&&c.molecular_weight!=null&&Math.abs(old.molecular_weight-c.molecular_weight)>=0.02)issues.push('molecular weight differs');
   if(issues.length){fail('chemical',c.id,issues.join('; ')+'.');continue;}
   // An alternative ID may denote the same encoded molecule, but must never
   // fill a differently named, structure-less local paper label implicitly.
   if(!text(old.smiles)&&text(c.smiles)){
    if(!exact||old.name!==c.name){fail('chemical',c.id,'A differently identified local molecule has no structure; reconcile its ID and name in Paper Workbench.');continue;}
    const fields=['smiles'];
    for(const field of ['inchikey','formula','molecular_weight'] as const)if((old[field]==null||old[field]==='')&&c[field]!=null&&c[field]!=='')fields.push(field);
    plan.upgrades.push({id:old.id,name:old.name,fields,smiles:c.smiles!});
   }
   const labels=[...new Set(paperLabelAliases(c,source))].filter(alias=>!old.aliases.includes(alias));
   if(labels.length){
    if(text(old.smiles)&&!verified){fail('chemical',c.id,'New paper labels need the existing and incoming structures to be verified as the same graph.');continue;}
    if(!text(old.smiles)&&!text(c.smiles)){
     // An existing unresolved paper record may retain an additional label from
     // its own evidenced paper without claiming a molecular graph. Target tags
     // alone are not evidence that a particular compound occurs in that paper.
     const evidenced=new Set(before.reactions.filter(r=>r.reactants.includes(old.id)||r.products.includes(old.id)||r.steps.some(step=>{
      const solution=before.solutions.find(s=>s.id===step.solution_id);
      return !!solution&&(solution.solvents.includes(old.id)||solution.solutes.some(solute=>solute.chemical_id===old.id));
     })).flatMap(r=>r.evidence.map(e=>before.papers.find(p=>p.id===e.paper_id)!.doi)));
     if(!exact||labels.some(alias=>!evidenced.has(alias.slice(alias.lastIndexOf('; DOI ')+6)))){fail('chemical',c.id,'An unresolved existing record can only receive labels from its already evidenced paper. Load the latest main-library backup in Paper Workbench and preserve its exact ID and name.');continue;}
    }
    const previous=plan.labelAdditions.find(row=>row.id===old.id);
    if(previous)previous.aliases=[...new Set([...previous.aliases,...labels])];
    else plan.labelAdditions.push({id:old.id,name:old.name,aliases:labels});
   }
  }
  // Existing IDs also protect the actual path. Otherwise mergeLibrary would
  // retain an old path while reporting a successful import of a changed one.
  for(const s of source.solutions){
   const old=before.solutions.find(x=>x.id===s.id);if(!old)continue;
   if(!sameIds(old.solvents,s.solvents.map(id=>mapping.get(id)||id))||!sameIds(old.solutes.map(x=>x.chemical_id),s.solutes.map(x=>mapping.get(x.chemical_id)||x.chemical_id)))fail('solution',s.id,'The existing solution ID links different chemicals.');
  }
  for(const r of source.reactions){
   const old=before.reactions.find(x=>x.id===r.id);if(!old)continue;
   if((['reactants','products','targets'] as const).some(field=>!sameIds(old[field],r[field].map(id=>mapping.get(id)||id))))fail('reaction',r.id,'The existing reaction ID connects a different synthesis path.');
  }
 }
 if(plan.conflicts.length)return plan;
 const next=saved?mergeLibrary(before,source):mergeLibrary(source,before);
 for(const upgrade of plan.upgrades){
  const old=next.chemicals.find(c=>c.id===upgrade.id)!;
  const incomingChemical=source.chemicals.find(c=>c.id===upgrade.id)!;
  for(const field of upgrade.fields as (keyof Chemical)[]){
   // The key set above is fixed to structure fields; keep every user field.
   Object.assign(old,{[field]:incomingChemical[field]});
  }
 }
 for(const addition of plan.labelAdditions){const chemical=next.chemicals.find(c=>c.id===addition.id)!;chemical.aliases=[...new Set([...chemical.aliases,...addition.aliases])];}
 plan.next=validateLibrary(next);
 for(const table of ['chemicals','reactions','solutions','papers'] as const)plan.added[table]=plan.next[table].length-before[table].length;
 plan.changed=JSON.stringify(plan.next)!==plan.baseline;
 return plan;
}

export function assertImportBaseline(plan:ImportReviewPlan,storage:Pick<Storage,'getItem'>,expectedRaw:string|null):void {
 if(storage.getItem(LIBRARY_STORE)!==expectedRaw)throw new Error('The stored library changed while this import was open. Cancel, reload and review the package again.');
 if(plan.saved){
  if(expectedRaw===null||JSON.stringify(validateLibrary(JSON.parse(expectedRaw)))!==plan.baseline)throw new Error('The stored library differs from this view. Reload before importing; no records were replaced.');
 }else if(expectedRaw!==null)throw new Error('A saved library appeared in another tab. Reload before importing; no records were replaced.');
}

/** Back up the exact original private bytes, verify, then do one primary save. */
export function commitReviewedImport(plan:ImportReviewPlan,storage:Pick<Storage,'getItem'|'setItem'>,expectedRaw:string|null):Library {
 if(plan.conflicts.length||!plan.next)throw new Error('Resolve the ID collisions in Paper Workbench before importing.');
 const next=validateLibrary(plan.next);
 assertImportBaseline(plan,storage,expectedRaw);
 if(!plan.changed)return next;
 if(plan.upgrades.length||plan.labelAdditions.length){
  if(expectedRaw===null)throw new Error('The original private library is missing. Reload before importing.');
  const key=LIBRARY_STORE+'.import-backup.'+crypto.randomUUID();
  try{
   if(storage.getItem(key)!==null)throw new Error('Backup already exists.');
   storage.setItem(key,expectedRaw);
   if(storage.getItem(key)!==expectedRaw)throw new Error('Backup verification failed.');
  }catch{throw new Error('Import paused: a verified private backup could not be saved. The original library is unchanged. Free browser storage and try again.');}
  assertImportBaseline(plan,storage,expectedRaw);
 }
 storage.setItem(LIBRARY_STORE,JSON.stringify(next));
 return next;
}
