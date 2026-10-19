import {mergeLibrary,validateLibrary,type Chemical,type Library,type Solution,type RecordReaction} from './libraryData';
// Kept independent of JSON-loaded example fixtures so the handoff validator also
// runs without a browser; this is the same private library key as the main app.
const LIBRARY_STORE='chembrain.normalized-library.v1';

export type StructureImportUpgrade={id:string;name:string;fields:string[];smiles:string};
/** Supplied only by the UI's actual, two-graph RDKit preflight; never from JSON. */
export type VerifiedImportGraphMatch={currentId:string;incomingId:string;currentSmiles:string;incomingSmiles:string;canonicalSmiles:string;inchikey:string;formula:string};
export type ImportLabelAddition={id:string;name:string;aliases:string[]};
type ImportTable='chemical'|'solution'|'reaction'|'paper';
export type ImportConflict={id:string;table:ImportTable;reason:string;field?:string;previous?:unknown;incoming?:unknown};
export type ImportFactChange={table:'solution'|'reaction';id:string;name:string;field:string;previous:unknown;incoming:unknown;action:'fill'|'add'|'append'};
export type ImportRetention={table:ImportTable;id:string;name:string;field:string;previous:unknown;incoming:unknown;reason:string};
export type ImportReviewPlan={
 baseline:string;saved:boolean;next:Library|null;upgrades:StructureImportUpgrade[];labelAdditions:ImportLabelAddition[];
 conflicts:ImportConflict[];factChanges:ImportFactChange[];retentions:ImportRetention[];
 changedExisting:{chemicals:number;solutions:number;reactions:number};
 added:{chemicals:number;reactions:number;solutions:number;papers:number};changed:boolean;
};
const text=(value:string|null|undefined)=>value?.trim()||'';
const sameIds=(a:string[],b:string[])=>JSON.stringify([...new Set(a)].sort())===JSON.stringify([...new Set(b)].sort());
const snapshot=(value:unknown)=>value===undefined?null:structuredClone(value);
const same=(a:unknown,b:unknown)=>JSON.stringify(a)===JSON.stringify(b);
const present=(value:unknown)=>value!==null&&value!==undefined&&(typeof value!=='string'||!!value.trim());
export const hasExistingImportChanges=(plan:ImportReviewPlan)=>Object.values(plan.changedExisting).some(count=>count>0);

/** Inspect only fields with explicit, unambiguous identity. No conversions or
 * positional guesses are used to attach a source fact to an existing record. */
function inspectExistingFacts(before:Library,source:Library,next:Library,chemicalMap:Map<string,string>,paperMap:Map<string,string>,plan:ImportReviewPlan){
 const conflict=(table:'solution'|'reaction',id:string,field:string,previous:unknown,incoming:unknown,reason:string)=>plan.conflicts.push({table,id,field,previous:snapshot(previous),incoming:snapshot(incoming),reason});
 const change=(table:'solution'|'reaction',id:string,name:string,field:string,previous:unknown,incoming:unknown,action:ImportFactChange['action']='fill')=>plan.factChanges.push({table,id,name,field,previous:snapshot(previous),incoming:snapshot(incoming),action});
 const retain=(table:ImportTable,id:string,name:string,field:string,previous:unknown,incoming:unknown,reason:string)=>{
  if(!same(previous,incoming)&&(present(previous)||present(incoming)))plan.retentions.push({table,id,name,field,previous:snapshot(previous),incoming:snapshot(incoming),reason});
 };
 // Amount/unit and concentration/unit are one context. A unit supplied without
 // a matching source number cannot be attached to a retained different number.
 const pair=(table:'solution'|'reaction',id:string,name:string,field:string,unitField:string,old:Record<string,unknown>,incoming:Record<string,unknown>,candidate:Record<string,unknown>,prefix='')=>{
  const a=old[field],b=incoming[field],u=old[unitField],v=incoming[unitField];
  const knownA=present(a),knownB=present(b),knownU=present(u),knownV=present(v);
  let blocked=false;
  if(knownA&&knownB&&a!==b){conflict(table,id,prefix+field,a,b,'Different known values are protected. Reconcile the original quantity/context before importing.');blocked=true;}
  if(knownU&&knownV&&text(u as string)!==text(v as string)){conflict(table,id,prefix+unitField,u,v,'Different known units or yield bases are protected; no conversion or replacement is inferred.');blocked=true;}
  if(!knownA&&knownB&&knownU&&!knownV){conflict(table,id,prefix+field,{value:a,unit:u},{value:b,unit:v},'The incoming value has no unit/basis to verify against the retained context.');blocked=true;}
  if(knownA&&!knownB&&!knownU&&knownV){conflict(table,id,prefix+unitField,{value:a,unit:u},{value:b,unit:v},'The incoming unit/basis has no matching source value; it cannot be attached to the retained value.');blocked=true;}
  if(blocked)return;
  for(const key of [field,unitField]){
   const previous=old[key],value=incoming[key];
   if(!present(previous)&&present(value)){candidate[key]=structuredClone(value);change(table,id,name,prefix+key,previous,value);}
   else if(present(previous)&&!present(value))retain(table,id,name,prefix+key,previous,value,'The incoming field is unreported; the existing fact is retained.');
  }
 };
 const condition=(id:string,name:string,index:number,key:'temperature'|'time',old:RecordReaction['steps'][number],incoming:RecordReaction['steps'][number],candidate:RecordReaction['steps'][number])=>{
  const a=old[key],b=incoming[key],field=`steps[${index}].${key}`;
  if(present(a)&&present(b)&&text(a)!==text(b))conflict('reaction',id,field,a,b,'Different known stage conditions are protected. Preserve the current ordered stages when reconciling.');
  else if(!present(a)&&present(b)){candidate[key]=b;change('reaction',id,name,field,a,b);}
  else if(present(a)&&!present(b))retain('reaction',id,name,field,a,b,'The incoming condition is unreported; the existing fact is retained.');
 };
 for(const raw of source.solutions){
  const old=before.solutions.find(s=>s.id===raw.id);if(!old)continue;
  const incoming:Solution={...raw,solvents:raw.solvents.map(id=>chemicalMap.get(id)!),solutes:raw.solutes.map(s=>({...s,chemical_id:chemicalMap.get(s.chemical_id)!}))};
  const candidate=next.solutions.find(s=>s.id===old.id)!;
  const key=(s:Solution['solutes'][number])=>JSON.stringify([s.chemical_id,s.role]);
  if(new Set(old.solvents).size!==old.solvents.length||new Set(incoming.solvents).size!==incoming.solvents.length||new Set(old.solutes.map(key)).size!==old.solutes.length||new Set(incoming.solutes.map(key)).size!==incoming.solutes.length){conflict('solution',old.id,'composition',{solvents:old.solvents,solutes:old.solutes},{solvents:incoming.solvents,solutes:incoming.solutes},'Duplicate solvent or chemical/role entries make composition alignment ambiguous.');continue;}
  if(!old.solvents.length&&!old.solutes.length&&(incoming.solvents.length||incoming.solutes.length)){
   candidate.solvents=structuredClone(incoming.solvents);candidate.solutes=structuredClone(incoming.solutes);
   change('solution',old.id,old.id,'composition',{solvents:[],solutes:[]},{solvents:incoming.solvents,solutes:incoming.solutes},'add');
  }else{
   if(incoming.solvents.length&&!sameIds(old.solvents,incoming.solvents))conflict('solution',old.id,'solvents',old.solvents,incoming.solvents,'Nonempty existing composition has different solvent membership. Reconcile the solution instead of relinking its ID.');
   else if(!incoming.solvents.length&&old.solvents.length)retain('solution',old.id,old.id,'solvents',old.solvents,[],'The incoming solvent list is unreported; existing membership is retained.');
   if(incoming.solutes.length&&!sameIds(old.solutes.map(key),incoming.solutes.map(key)))conflict('solution',old.id,'solutes',old.solutes,incoming.solutes,'Nonempty existing composition has different chemical membership or roles. Roles are part of quantity identity.');
   else if(!incoming.solutes.length&&old.solutes.length)retain('solution',old.id,old.id,'solutes',old.solutes,[],'The incoming solute list is unreported; existing membership is retained.');
   else for(let i=0;i<old.solutes.length;i++){
    const item=old.solutes[i],other=incoming.solutes.find(s=>key(s)===key(item));if(!other)continue;
    pair('solution',old.id,old.id,'amount','unit',item as unknown as Record<string,unknown>,other as unknown as Record<string,unknown>,candidate.solutes[i] as unknown as Record<string,unknown>,`solutes[${i}].`);
   }
  }
  pair('solution',old.id,old.id,'concentration','concentration_unit',old as unknown as Record<string,unknown>,incoming as unknown as Record<string,unknown>,candidate as unknown as Record<string,unknown>);
 }
 for(const raw of source.reactions){
  const old=before.reactions.find(r=>r.id===raw.id);if(!old)continue;
  const incoming:RecordReaction={...raw,reactants:raw.reactants.map(id=>chemicalMap.get(id)!),products:raw.products.map(id=>chemicalMap.get(id)!),targets:raw.targets.map(id=>chemicalMap.get(id)!),evidence:raw.evidence.map(e=>({...e,paper_id:paperMap.get(e.paper_id)!}))};
  const candidate=next.reactions.find(r=>r.id===old.id)!;
  for(const field of ['reactants','products','targets'] as const){
   if(field==='targets'&&!incoming.targets.length){if(old.targets.length)retain('reaction',old.id,old.name,field,old[field],incoming[field],'Unreported incoming route tags do not remove current membership.');}
   else if(!sameIds(old[field],incoming[field]))conflict('reaction',old.id,field,old[field],incoming[field],'The existing reaction ID connects a different synthesis path. Preserve current participant IDs during reconciliation.');
  }
  for(const field of ['name','notes','status'] as const)retain('reaction',old.id,old.name,field,old[field],incoming[field],'The existing local record field is retained; import does not rename, replace notes or promote review status.');
  pair('reaction',old.id,old.name,'yield_percent','yield_basis',old as unknown as Record<string,unknown>,incoming as unknown as Record<string,unknown>,candidate as unknown as Record<string,unknown>);
  const oldIds=old.steps.map(step=>step.solution_id),newIds=incoming.steps.map(step=>step.solution_id);
  // A repeated same-pot sequence can be scientifically valid. Exact unchanged
  // sequences need no alignment; only attempts to modify them are ambiguous.
  if(same(old.steps,incoming.steps)){/* no stage changes */}
  else if(!incoming.steps.length){if(old.steps.length)retain('reaction',old.id,old.name,'steps',old.steps,[],'An empty incoming stage list does not remove existing stages.');}
  else if(new Set(oldIds).size!==oldIds.length||new Set(newIds).size!==newIds.length)conflict('reaction',old.id,'steps',old.steps,incoming.steps,'Repeated solution IDs make ordered stage alignment ambiguous. Give distinct stage solutions their own stable IDs.');
  else if(!old.steps.length){candidate.steps=structuredClone(incoming.steps);change('reaction',old.id,old.name,'steps',[],incoming.steps,'add');}
  else if(incoming.steps.length<old.steps.length||old.steps.some((step,i)=>step.solution_id!==incoming.steps[i]?.solution_id))conflict('reaction',old.id,'steps',old.steps,incoming.steps,'The complete existing ordered stages must be an exact, unambiguous prefix. Inserting, reordering, shortening or relinking stages requires reconciliation.');
  else{
   old.steps.forEach((step,i)=>{for(const field of ['temperature','time'] as const)condition(old.id,old.name,i,field,step,incoming.steps[i],candidate.steps[i]);retain('reaction',old.id,old.name,`steps[${i}].notes`,step.notes,incoming.steps[i].notes,'Existing stage notes stay local; edit the current record explicitly to change them.');});
   const suffix=incoming.steps.slice(old.steps.length);
   if(suffix.length){candidate.steps.push(...structuredClone(suffix));change('reaction',old.id,old.name,`steps[${old.steps.length}:]`,[],suffix,'append');}
  }
  const evidenceKey=(e:RecordReaction['evidence'][number])=>JSON.stringify([e.paper_id,e.page,e.locator]);
  const seen=new Set(old.evidence.map(evidenceKey)),additions:RecordReaction['evidence']=[];
  for(const evidence of incoming.evidence){const key=evidenceKey(evidence);if(!seen.has(key)){seen.add(key);additions.push(evidence);}}
  if(additions.length){candidate.evidence.push(...structuredClone(additions));change('reaction',old.id,old.name,'evidence',old.evidence,additions,'append');}
 }
}
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
 const plan:ImportReviewPlan={baseline:JSON.stringify(before),saved,next:null,upgrades:[],labelAdditions:[],conflicts:[],factChanges:[],retentions:[],changedExisting:{chemicals:0,solutions:0,reactions:0},added:{chemicals:0,reactions:0,solutions:0,papers:0},changed:false};
 const fail=(table:ImportConflict['table'],id:string,reason:string,field?:string,previous?:unknown,incomingValue?:unknown)=>plan.conflicts.push({table,id,reason,field,previous:snapshot(previous),incoming:snapshot(incomingValue)});
 const mapping=new Map<string,string>();
 const paperMapping=new Map<string,string>();
 if(saved){
  for(const p of source.papers){
   const collision=before.papers.find(old=>old.id===p.id&&old.doi!==p.doi);
   if(collision)fail('paper',p.id,'The existing paper ID belongs to another DOI. Reconcile the paper IDs before importing.','doi',collision.doi,p.doi);
   const old=before.papers.find(row=>row.doi===p.doi);paperMapping.set(p.id,old?.id||p.id);
   if(old&&!same(old.authors,p.authors))plan.retentions.push({table:'paper',id:old.id,name:old.doi,field:'authors',previous:old.authors,incoming:p.authors,reason:'Existing author edits are retained.'});
  }
  const sourceKeys=new Map<string,string>();
  for(const c of source.chemicals){
   if(text(c.inchikey)){
    const duplicate=sourceKeys.get(c.inchikey!);
    if(duplicate)fail('chemical',c.id,'Multiple incoming IDs use the same InChIKey. Reconcile their paper labels into one molecule before export.','inchikey',duplicate,c.id);
    sourceKeys.set(c.inchikey!,c.id);
   }
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
   if(issues.length){fail('chemical',c.id,issues.join('; ')+'.','identity',old,c);continue;}
   for(const field of ['name','notes','smiles','molecular_weight'] as const)if(!same(old[field],c[field])&&(present(old[field])||present(c[field]))){
    if(field==='smiles'&&!text(old.smiles))continue;
    if(field==='molecular_weight'&&!present(old.molecular_weight)&&!text(old.smiles)&&text(c.smiles))continue;
    plan.retentions.push({table:'chemical',id:old.id,name:old.name,field,previous:snapshot(old[field]),incoming:snapshot(c[field]),reason:field==='smiles'&&verified?'Actual graphs match; the existing SMILES representation is retained.':'The existing local record field is retained.'});
   }
   const ignoredAliases=c.aliases.filter(alias=>!old.aliases.includes(alias)&&!paperLabelAliases(c,source).includes(alias));
   if(ignoredAliases.length)plan.retentions.push({table:'chemical',id:old.id,name:old.name,field:'aliases',previous:old.aliases,incoming:ignoredAliases,reason:'Existing aliases are retained; only qualified paper-label aliases are proposed additively.'});
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
 }
 if(plan.conflicts.length)return plan;
 const next=saved?mergeLibrary(before,source):mergeLibrary(source,before);
 if(saved)inspectExistingFacts(before,source,next,mapping,paperMapping,plan);
 if(plan.conflicts.length)return plan;
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
 for(const table of ['chemicals','reactions','solutions','papers'] as const)plan.added[table]=plan.next[table].filter(row=>!before[table].some(old=>old.id===row.id)).length;
 if(saved)for(const table of ['chemicals','solutions','reactions'] as const)plan.changedExisting[table]=before[table].filter(old=>!same(old,plan.next![table].find(row=>row.id===old.id))).length;
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
 if(hasExistingImportChanges(plan)){
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
