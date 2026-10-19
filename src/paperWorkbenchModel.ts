import { normalizeDoi, validateLibrary, type Chemical, type Library, type Paper, type RecordReaction, type Solution } from './libraryData';

/** Private working data. Export is an explicit allowlisted projection, never a spread. */
export type SourceLocator = { document:'main'|'supporting'; page:number; locator:string };
export type StructureInspection = { smiles:string; canonical_smiles:string; formula:string; inchikey:string; molecular_weight:number; engine:string; fragments?:number; unassigned_stereocenters?:number };
export type Approval = { signature:string; source_checked:true; inspection?:StructureInspection };
export type WorkbenchChemical = Chemical & { label:string; sources:SourceLocator[]; unknown_reason:string; checked?:Approval };
export type WorkbenchSolution = Solution & { label:string; sources:SourceLocator[]; checked?:Approval };
export type WorkbenchReaction = Omit<RecordReaction,'status'|'evidence'> & { label:string; evidence:SourceLocator[]; checked?:Approval };
export type WorkbenchProject = { project_schema:1; kind:'chembrain-paper-workbench'; paper:Paper; chemicals:WorkbenchChemical[]; solutions:WorkbenchSolution[]; reactions:WorkbenchReaction[]; baseline?:Library };

const error=(message:string):never=>{throw new Error(message);};
const object=(value:unknown):value is Record<string,unknown>=>!!value&&typeof value==='object'&&!Array.isArray(value);
const string=(value:unknown):value is string=>typeof value==='string'&&value.length<=3000;
const strings=(value:unknown):value is string[]=>Array.isArray(value)&&value.every(string);
const fields=(value:unknown,keys:readonly string[])=>object(value)&&Object.keys(value).every(key=>keys.includes(key));
const finite=(value:unknown):value is number=>typeof value==='number'&&Number.isFinite(value);
const compactString=(value:unknown)=>value==null||string(value);
const identifier=(value:unknown):value is string=>string(value)&&/^[A-Za-z0-9][A-Za-z0-9._:-]{0,120}$/.test(value);
const canonical=(value:unknown):string=>Array.isArray(value)?'['+value.map(canonical).join(',')+']':object(value)?'{'+Object.keys(value).sort().map(k=>JSON.stringify(k)+':'+canonical(value[k])).join(',')+'}':JSON.stringify(value)??'null';

// Synchronous SHA-256 gives the UI deterministic DOI/label IDs without a server,
// platform crypto API or abbreviation collisions. This is a state fingerprint,
// not authentication of who checked a record.
function digest(text:string):string {
 const bytes=new TextEncoder().encode(text),length=Math.ceil((bytes.length+9)/64)*64,data=new Uint8Array(length);
 data.set(bytes);data[bytes.length]=128;const view=new DataView(data.buffer);view.setUint32(length-4,bytes.length*8);
 const constants=[1116352408,1899447441,3049323471,3921009573,961987163,1508970993,2453635748,2870763221,3624381080,310598401,607225278,1426881987,1925078388,2162078206,2614888103,3248222580,3835390401,4022224774,264347078,604807628,770255983,1249150122,1555081692,1996064986,2554220882,2821834349,2952996808,3210313671,3336571891,3584528711,113926993,338241895,666307205,773529912,1294757372,1396182291,1695183700,1986661051,2177026350,2456956037,2730485921,2820302411,3259730800,3345764771,3516065817,3600352804,4094571909,275423344,430227734,506948616,659060556,883997877,958139571,1322822218,1537002063,1747873779,1955562222,2024104815,2227730452,2361852424,2428436474,2756734187,3204031479,3329325298];
 const state=[1779033703,3144134277,1013904242,2773480762,1359893119,2600822924,528734635,1541459225];
 const rotate=(n:number,x:number)=>(x>>>n)|(x<<(32-n));
 for(let offset=0;offset<length;offset+=64){
  const words=new Uint32Array(64);for(let i=0;i<16;i++)words[i]=view.getUint32(offset+i*4);
  for(let i=16;i<64;i++){const x=words[i-15],y=words[i-2];words[i]=(words[i-16]+(rotate(7,x)^rotate(18,x)^(x>>>3))+words[i-7]+(rotate(17,y)^rotate(19,y)^(y>>>10)))>>>0;}
  let [a,b,c,d,e,f,g,h]=state;
  for(let i=0;i<64;i++){const t1=(h+(rotate(6,e)^rotate(11,e)^rotate(25,e))+((e&f)^(~e&g))+constants[i]+words[i])>>>0,t2=((rotate(2,a)^rotate(13,a)^rotate(22,a))+((a&b)^(a&c)^(b&c)))>>>0;h=g;g=f;f=e;e=(d+t1)>>>0;d=c;c=b;b=a;a=(t1+t2)>>>0;}
  for(const [i,value] of [a,b,c,d,e,f,g,h].entries())state[i]=(state[i]+value)>>>0;
 }
 return state.map(x=>x.toString(16).padStart(8,'0')).join('');
}
export function stableRecordId(kind:'paper'|'chemical'|'solution'|'reaction',doi:string,label=''):string {
 return 'pw-'+kind+'-'+digest(normalizeDoi(doi)+'\u0000'+label.trim());
}
const withoutCheck=<T extends {checked?:Approval}>(value:T)=>{const row=structuredClone(value);delete row.checked;return row;};
const fingerprint=(value:unknown)=>digest(canonical(value));
const chemicalSignature=(project:WorkbenchProject,row:WorkbenchChemical,inspection?:StructureInspection)=>fingerprint({paper:project.paper,row:withoutCheck(row),inspection:inspection??null});
const chemicalChecked=(project:WorkbenchProject,row:WorkbenchChemical)=>!!row.checked&&row.checked.source_checked===true&&row.checked.signature===chemicalSignature(project,row,row.checked.inspection);
const chemicalIds=(s:WorkbenchSolution)=>[...s.solvents,...s.solutes.map(x=>x.chemical_id)];
const reactionIds=(r:WorkbenchReaction)=>[...r.reactants,...r.products,...r.targets];
function solutionSignature(project:WorkbenchProject,row:WorkbenchSolution):string {
 return fingerprint({paper:project.paper,row:withoutCheck(row),chemicals:chemicalIds(row).map(id=>({id,checked:project.chemicals.find(c=>c.id===id)?.checked??null}))});
}
const solutionChecked=(project:WorkbenchProject,row:WorkbenchSolution)=>!!row.checked&&row.checked.source_checked===true&&row.checked.signature===solutionSignature(project,row)&&chemicalIds(row).every(id=>chemicalChecked(project,project.chemicals.find(c=>c.id===id)!));
function reactionSignature(project:WorkbenchProject,row:WorkbenchReaction):string {
 return fingerprint({paper:project.paper,row:withoutCheck(row),chemicals:reactionIds(row).map(id=>({id,checked:project.chemicals.find(c=>c.id===id)?.checked??null})),solutions:row.steps.map(s=>({id:s.solution_id,checked:project.solutions.find(x=>x.id===s.solution_id)?.checked??null}))});
}
const reactionChecked=(project:WorkbenchProject,row:WorkbenchReaction)=>!!row.checked&&row.checked.source_checked===true&&row.checked.signature===reactionSignature(project,row)&&reactionIds(row).every(id=>chemicalChecked(project,project.chemicals.find(c=>c.id===id)!))&&row.steps.every(s=>solutionChecked(project,project.solutions.find(x=>x.id===s.solution_id)!));

export function createProject(doi:string,authors:string[]=[]):WorkbenchProject {
 const normalized=normalizeDoi(doi);
 const paper=validateLibrary({schema_version:1,papers:[{id:stableRecordId('paper',normalized),doi:normalized,authors}],chemicals:[],solutions:[],reactions:[]}).papers[0];
 return {project_schema:1,kind:'chembrain-paper-workbench',paper,chemicals:[],solutions:[],reactions:[]};
}
function baselineScope(project:WorkbenchProject):{chemicals:Set<string>;solutions:Set<string>;reactions:Set<string>} {
 const rows=project.baseline?.reactions.filter(r=>r.evidence.some(e=>e.paper_id===project.paper.id))??[];
 const solutions=new Set(rows.flatMap(r=>r.steps.map(s=>s.solution_id)));
 const solutionRows=project.baseline?.solutions.filter(s=>solutions.has(s.id))??[];
 return {reactions:new Set(rows.map(r=>r.id)),solutions,chemicals:new Set([...rows.flatMap(r=>[...r.reactants,...r.products,...r.targets]),...solutionRows.flatMap(s=>[...s.solvents,...s.solutes.map(x=>x.chemical_id)])])};
}
function validateSources(value:unknown):asserts value is SourceLocator[] {
 if(!Array.isArray(value)||value.some(s=>!fields(s,['document','page','locator'])||!object(s)||!['main','supporting'].includes(s.document as string)||!Number.isInteger(s.page)||Number(s.page)<1||!string(s.locator)||!s.locator.trim()))error('A source needs main/supporting document, a positive PDF page and a locator.');
}
function validateInspection(value:unknown):asserts value is StructureInspection {
 if(!fields(value,['smiles','canonical_smiles','formula','inchikey','molecular_weight','engine','fragments','unassigned_stereocenters'])||!object(value)||!string(value.smiles)||!value.smiles.trim()||!string(value.canonical_smiles)||!value.canonical_smiles.trim()||!string(value.formula)||!value.formula.trim()||!string(value.inchikey)||!/^[A-Z]{14}-[A-Z]{10}-[A-Z]$/.test(value.inchikey)||!finite(value.molecular_weight)||value.molecular_weight<=0||!string(value.engine)||!value.engine.trim()||['fragments','unassigned_stereocenters'].some(k=>value[k]!==undefined&&(!Number.isInteger(value[k])||Number(value[k])<0)))error('Inspect this exact SMILES with the bundled RDKit engine before checking it.');
}
function validateApproval(value:unknown):void {
 if(value===undefined)return;
 if(!fields(value,['signature','source_checked','inspection'])||!object(value)||typeof value.signature!=='string'||!/^[a-f0-9]{64}$/.test(value.signature)||value.source_checked!==true)error('Invalid private check record.');
 const approval=value as Approval;if(approval.inspection!==undefined)validateInspection(approval.inspection);
}

/** Accepts only this private format; a PDF, image, prose cache or arbitrary object cannot become a project. */
export function validateProject(value:unknown):WorkbenchProject {
 if(!fields(value,['project_schema','kind','paper','chemicals','solutions','reactions','baseline'])||!object(value)||value.project_schema!==1||value.kind!=='chembrain-paper-workbench'||new TextEncoder().encode(JSON.stringify(value)).length>10_000_000)error('Use a Paper Workbench project backup smaller than 10 MB.');
 const project=structuredClone(value) as WorkbenchProject;
 if(!Array.isArray(project.chemicals)||!Array.isArray(project.solutions)||!Array.isArray(project.reactions))error('Missing private project tables.');
 if([project.chemicals,project.solutions,project.reactions].some(rows=>rows.length>2000)||project.chemicals.length+project.solutions.length+project.reactions.length>5000)error('Split this paper project: use at most 2000 records per table and 5000 records in total.');
 project.paper=validateLibrary({schema_version:1,papers:[project.paper],chemicals:[],solutions:[],reactions:[]}).papers[0];
 if(project.baseline!==undefined){project.baseline=validateLibrary(project.baseline);if(!project.baseline.papers.some(p=>p.id===project.paper.id&&p.doi===project.paper.doi))error('The baseline does not contain this paper identity.');}
 else if(project.paper.id!==stableRecordId('paper',project.paper.doi))error('Paper identity does not match its normalized DOI.');
 const sets={chemicals:new Set<string>(),solutions:new Set<string>(),reactions:new Set<string>()},legacyScope=baselineScope(project);
 const keys={chemicals:['id','label','name','kind','smiles','inchikey','formula','molecular_weight','aliases','notes','sources','unknown_reason','checked'],solutions:['id','label','solvents','solutes','concentration','concentration_unit','sources','checked'],reactions:['id','label','name','reactants','products','targets','yield_percent','yield_basis','steps','evidence','notes','checked']};
 const kind={chemicals:'chemical',solutions:'solution',reactions:'reaction'} as const;
 for(const table of ['chemicals','solutions','reactions'] as const){const labels=new Set<string>();for(const row of project[table]){
  if(!fields(row,keys[table])||!object(row)||!identifier(row.id)||sets[table].has(row.id)||!string(row.label)||!row.label.trim()||row.label!==row.label.trim()||labels.has(row.label))error('Each '+kind[table]+' needs a unique ID and local label.');
  sets[table].add(row.id);labels.add(row.label);validateApproval(row.checked);
  const legacy=legacyScope[table].has(row.id);
  if(!legacy&&row.id!==stableRecordId(kind[table],project.paper.doi,row.label))error('A record identity must match the paper DOI and local label.');
 }}
 for(const row of project.chemicals){
  if(!string(row.name)||!row.name.trim()||!['compound','solvent','reagent','catalyst'].includes(row.kind)||!strings(row.aliases)||!compactString(row.smiles)||!compactString(row.formula)||!compactString(row.inchikey)||!compactString(row.notes)||(row.molecular_weight!=null&&(!finite(row.molecular_weight)||row.molecular_weight<0))||!string(row.unknown_reason))error('Invalid private chemical metadata.');
  validateSources(row.sources);
 }
 for(const row of project.solutions){
  if(!strings(row.solvents)||row.solvents.some(id=>!sets.chemicals.has(id))||!Array.isArray(row.solutes)||row.solutes.some(s=>!fields(s,['chemical_id','role','amount','unit'])||!object(s)||!sets.chemicals.has(s.chemical_id as string)||!string(s.role)||(s.amount!==null&&(!finite(s.amount)||s.amount<0))||(s.unit!==null&&!string(s.unit)))||(row.concentration!==null&&(!finite(row.concentration)||row.concentration<0))||(row.concentration_unit!==null&&!string(row.concentration_unit)))error('Invalid solution or unknown chemical dependency.');
  validateSources(row.sources);
 }
 for(const row of project.reactions){
  if(!string(row.name)||!row.name.trim()||!strings(row.reactants)||!strings(row.products)||!strings(row.targets)||reactionIds(row).some(id=>!sets.chemicals.has(id))||(row.yield_percent!==null&&(!finite(row.yield_percent)||row.yield_percent<0||row.yield_percent>100))||!compactString(row.yield_basis)||!compactString(row.notes)||!Array.isArray(row.steps)||row.steps.some(s=>!fields(s,['solution_id','temperature','time','notes'])||!object(s)||!sets.solutions.has(s.solution_id as string)||!compactString(s.temperature)||!compactString(s.time)||!compactString(s.notes)))error('Invalid reaction participants, yield or stage solution.');
  validateSources(row.evidence);
 }
 return project;
}

const locate=<T extends {id:string}>(rows:T[],id:string):T=>rows.find(row=>row.id===id)??error('Unknown project record: '+id);
type ChemicalInput=Partial<Omit<WorkbenchChemical,'id'|'checked'>> & Pick<WorkbenchChemical,'label'|'name'|'kind'>;
type SolutionInput=Partial<Omit<WorkbenchSolution,'id'|'checked'>> & Pick<WorkbenchSolution,'label'>;
type ReactionInput=Partial<Omit<WorkbenchReaction,'id'|'checked'>> & Pick<WorkbenchReaction,'label'|'name'>;
export function addChemical(project:WorkbenchProject,input:ChemicalInput):WorkbenchProject {
 const next=validateProject(project);next.chemicals.push({aliases:[],smiles:null,sources:[],unknown_reason:'',...input,label:input.label.trim(),id:stableRecordId('chemical',next.paper.doi,input.label)});return validateProject(next);
}
export function addSolution(project:WorkbenchProject,input:SolutionInput):WorkbenchProject {
 const next=validateProject(project);next.solutions.push({solvents:[],solutes:[],concentration:null,concentration_unit:null,sources:[],...input,label:input.label.trim(),id:stableRecordId('solution',next.paper.doi,input.label)});return validateProject(next);
}
export function addReaction(project:WorkbenchProject,input:ReactionInput):WorkbenchProject {
 const next=validateProject(project);next.reactions.push({reactants:[],products:[],targets:[],yield_percent:null,steps:[],evidence:[],...input,label:input.label.trim(),id:stableRecordId('reaction',next.paper.doi,input.label)});return validateProject(next);
}
function invalidateChemicalDependencies(project:WorkbenchProject,id:string):void {
 const solutions=new Set<string>();for(const row of project.solutions)if(chemicalIds(row).includes(id)){delete row.checked;solutions.add(row.id);}
 for(const row of project.reactions)if(reactionIds(row).includes(id)||row.steps.some(s=>solutions.has(s.solution_id)))delete row.checked;
}
export function updateChemical(project:WorkbenchProject,id:string,patch:Partial<Omit<WorkbenchChemical,'id'|'checked'>>):WorkbenchProject {
 const next=validateProject(project),row=locate(next.chemicals,id),previous=canonical(withoutCheck(row));Object.assign(row,patch);row.label=row.label.trim();
 if(canonical(withoutCheck(row))!==previous){delete row.checked;invalidateChemicalDependencies(next,id);if(!next.baseline?.chemicals.some(x=>x.id===id)){const replacement=stableRecordId('chemical',next.paper.doi,row.label);row.id=replacement;for(const s of next.solutions){s.solvents=s.solvents.map(x=>x===id?replacement:x);s.solutes=s.solutes.map(x=>({...x,chemical_id:x.chemical_id===id?replacement:x.chemical_id}));}for(const r of next.reactions){r.reactants=r.reactants.map(x=>x===id?replacement:x);r.products=r.products.map(x=>x===id?replacement:x);r.targets=r.targets.map(x=>x===id?replacement:x);}}}
 return validateProject(next);
}
export function updateSolution(project:WorkbenchProject,id:string,patch:Partial<Omit<WorkbenchSolution,'id'|'checked'>>):WorkbenchProject {
 const next=validateProject(project),row=locate(next.solutions,id),previous=canonical(withoutCheck(row));Object.assign(row,patch);row.label=row.label.trim();
 if(canonical(withoutCheck(row))!==previous){delete row.checked;for(const r of next.reactions)if(r.steps.some(s=>s.solution_id===id))delete r.checked;if(!next.baseline?.solutions.some(x=>x.id===id)){row.id=stableRecordId('solution',next.paper.doi,row.label);for(const r of next.reactions)for(const s of r.steps)if(s.solution_id===id)s.solution_id=row.id;}}
 return validateProject(next);
}
export function updateReaction(project:WorkbenchProject,id:string,patch:Partial<Omit<WorkbenchReaction,'id'|'checked'>>):WorkbenchProject {
 const next=validateProject(project),row=locate(next.reactions,id),previous=canonical(withoutCheck(row));Object.assign(row,patch);row.label=row.label.trim();if(canonical(withoutCheck(row))!==previous){delete row.checked;if(!next.baseline?.reactions.some(x=>x.id===id))row.id=stableRecordId('reaction',next.paper.doi,row.label);}return validateProject(next);
}
export function updatePaper(project:WorkbenchProject,patch:{authors:string[]}):WorkbenchProject {
 const next=validateProject(project);if(!fields(patch,['authors']))error('Create a new project to change the paper DOI.');
 if(canonical(next.paper.authors)!==canonical(patch.authors)){next.paper.authors=structuredClone(patch.authors);for(const row of [...next.chemicals,...next.solutions,...next.reactions])delete row.checked;}
 return validateProject(next);
}
export function removeChemical(project:WorkbenchProject,id:string):WorkbenchProject {
 const next=validateProject(project);locate(next.chemicals,id);
 if(next.solutions.some(s=>chemicalIds(s).includes(id))||next.reactions.some(r=>reactionIds(r).includes(id)))error('Remove this chemical from its reactions and solutions first.');
 next.chemicals=next.chemicals.filter(c=>c.id!==id);return validateProject(next);
}
export function removeSolution(project:WorkbenchProject,id:string):WorkbenchProject {
 const next=validateProject(project);locate(next.solutions,id);if(next.reactions.some(r=>r.steps.some(s=>s.solution_id===id)))error('Remove this solution from its reaction stages first.');
 next.solutions=next.solutions.filter(s=>s.id!==id);return validateProject(next);
}
export function removeReaction(project:WorkbenchProject,id:string):WorkbenchProject {
 const next=validateProject(project);locate(next.reactions,id);next.reactions=next.reactions.filter(r=>r.id!==id);return validateProject(next);
}

function requireSources(sources:SourceLocator[]):void {if(!sources.length)error('Record at least one source document, PDF page and precise locator before checking.');}
export function checkChemical(project:WorkbenchProject,id:string,inspection:StructureInspection|null,sourceChecked:boolean):WorkbenchProject {
 const next=validateProject(project),row=locate(next.chemicals,id);if(sourceChecked!==true)error('Compare this chemical and its stereochemistry with the source first.');requireSources(row.sources);
 if(row.smiles?.trim()){
  validateInspection(inspection);if(inspection.smiles!==row.smiles)error('The inspection is stale. Inspect the exact current SMILES again.');
  row.formula=inspection.formula;row.inchikey=inspection.inchikey;row.molecular_weight=inspection.molecular_weight;
 }else{if(row.kind==='compound')error('A compound needs a source-checked structure before export.');if(!row.unknown_reason.trim())error('Explain why this reagent/solvent/catalyst structure is unknown.');if(inspection!==null)error('An unknown structure cannot have an RDKit inspection.');}
 invalidateChemicalDependencies(next,id);row.checked={source_checked:true,signature:chemicalSignature(next,row,inspection??undefined),...(inspection?{inspection:structuredClone(inspection)}:{})};return validateProject(next);
}
export function checkSolution(project:WorkbenchProject,id:string,sourceChecked:boolean):WorkbenchProject {
 const next=validateProject(project),row=locate(next.solutions,id);if(sourceChecked!==true)error('Compare the solution composition with the source first.');requireSources(row.sources);
 if(!chemicalIds(row).length)error('A solution must contain a recorded solvent or solute.');
 if(chemicalIds(row).some(key=>!chemicalChecked(next,locate(next.chemicals,key))))error('Check every solvent and solute chemical before checking this solution.');
 for(const r of next.reactions)if(r.steps.some(s=>s.solution_id===id))delete r.checked;
 row.checked={source_checked:true,signature:solutionSignature(next,row)};return validateProject(next);
}
export function checkReaction(project:WorkbenchProject,id:string,sourceChecked:boolean):WorkbenchProject {
 const next=validateProject(project),row=locate(next.reactions,id);if(sourceChecked!==true)error('Compare participants, stages and conditions with the source first.');requireSources(row.evidence);
 if(!row.reactants.length||!row.products.length)error('A reaction needs recorded reactants and products.');
 if(reactionIds(row).some(key=>!chemicalChecked(next,locate(next.chemicals,key))))error('Check every reaction compound and target first.');
 if(row.steps.some(s=>!solutionChecked(next,locate(next.solutions,s.solution_id))))error('Check every stage solution first.');
 row.checked={source_checked:true,signature:reactionSignature(next,row)};return validateProject(next);
}

/** Stale checks block export; unchecked draft rows are deliberately left behind. */
export function blockers(project:WorkbenchProject):string[] {
 const next=validateProject(project),messages:string[]=[];
 for(const c of next.chemicals)if(c.checked&&(!chemicalChecked(next,c)||!c.sources.length||(c.kind==='compound'&&!c.smiles?.trim())||(!!c.smiles?.trim()&&(!c.checked.inspection||c.checked.inspection.smiles!==c.smiles||c.formula!==c.checked.inspection.formula||c.inchikey!==c.checked.inspection.inchikey||c.molecular_weight!==c.checked.inspection.molecular_weight))||(!c.smiles?.trim()&&!c.unknown_reason.trim())))messages.push('Chemical '+c.label+': stale or incomplete source check.');
 for(const s of next.solutions)if(s.checked&&(!solutionChecked(next,s)||!s.sources.length||!chemicalIds(s).length))messages.push('Solution '+s.label+': stale check or unapproved chemical dependency.');
 for(const r of next.reactions)if(r.checked&&(!reactionChecked(next,r)||!r.evidence.length||!r.reactants.length||!r.products.length))messages.push('Reaction '+r.label+': stale check or unapproved participant/stage dependency.');
 if(!next.chemicals.some(c=>c.checked)&&!next.solutions.some(s=>s.checked)&&!next.reactions.some(r=>r.checked))messages.push('No checked records to export. Drafts stay in this private project.');
 return messages;
}
export async function buildExport(project:WorkbenchProject):Promise<Library> {
 const next=validateProject(project),problems=blockers(next);if(problems.length)error(problems.join('\n'));
 const chemicals=next.chemicals.filter(c=>c.checked).map(c=>({id:c.id,name:c.name,kind:c.kind,aliases:[...new Set([...c.aliases,'Paper label '+c.label+'; DOI '+next.paper.doi])],...(c.smiles!==undefined?{smiles:c.smiles}:{}),...(c.formula!==undefined?{formula:c.formula}:{}),...(c.inchikey!==undefined?{inchikey:c.inchikey}:{}),...(c.molecular_weight!==undefined?{molecular_weight:c.molecular_weight}:{}),...(c.notes!==undefined?{notes:c.notes}:{})}));
 const solutions=next.solutions.filter(s=>s.checked).map(s=>({id:s.id,solvents:[...s.solvents],solutes:structuredClone(s.solutes),concentration:s.concentration,concentration_unit:s.concentration_unit}));
 const reactions=next.reactions.filter(r=>r.checked).map(r=>({id:r.id,name:r.name,reactants:[...r.reactants],products:[...r.products],targets:[...r.targets],yield_percent:r.yield_percent,...(r.yield_basis!==undefined?{yield_basis:r.yield_basis}:{}),status:'reviewed' as const,steps:structuredClone(r.steps),evidence:r.evidence.map(e=>({paper_id:next.paper.id,page:e.page,locator:(e.document==='supporting'?'Supporting information':'Main article')+'; PDF page '+e.page+'; '+e.locator})),...(r.notes!==undefined?{notes:r.notes}:{})}));
 return validateLibrary({schema_version:1,papers:[structuredClone(next.paper)],chemicals,solutions,reactions});
}

/** Existing examples become editable drafts, not source-approved chemistry. */
export function importLibraryDraft(value:unknown,paperId?:string):WorkbenchProject {
 const baseline=validateLibrary(value),paper=(paperId?baseline.papers.find(p=>p.id===paperId):baseline.papers[0])??error('Choose a paper from a normalized library package.');
 const reactions=baseline.reactions.filter(r=>r.evidence.some(e=>e.paper_id===paper.id));
 const solutionIds=new Set(reactions.flatMap(r=>r.steps.map(s=>s.solution_id))),solutions=baseline.solutions.filter(s=>solutionIds.has(s.id));
 const chemicalSet=new Set([...reactions.flatMap(r=>[...r.reactants,...r.products,...r.targets]),...solutions.flatMap(s=>[...s.solvents,...s.solutes.map(c=>c.chemical_id)])]);
 const sources=(evidence:RecordReaction['evidence']):SourceLocator[]=>evidence.filter(e=>e.paper_id===paper.id).map(e=>({document:/supporting|\bSI\b/i.test(e.locator)?'supporting':'main',page:e.page,locator:e.locator}));
 const uniqueSources=(rows:SourceLocator[])=>rows.filter((row,index)=>rows.findIndex(x=>canonical(x)===canonical(row))===index);
 const project:WorkbenchProject={project_schema:1,kind:'chembrain-paper-workbench',paper:structuredClone(paper),baseline,chemicals:baseline.chemicals.filter(c=>chemicalSet.has(c.id)).map(c=>({...structuredClone(c),label:c.id,sources:uniqueSources(reactions.filter(r=>[...r.reactants,...r.products,...r.targets].includes(c.id)||r.steps.some(s=>{const solution=solutions.find(x=>x.id===s.solution_id);return solution&&[...solution.solvents,...solution.solutes.map(x=>x.chemical_id)].includes(c.id);})).flatMap(r=>sources(r.evidence))),unknown_reason:''})),solutions:solutions.map(s=>({...structuredClone(s),label:s.id,sources:uniqueSources(reactions.filter(r=>r.steps.some(x=>x.solution_id===s.id)).flatMap(r=>sources(r.evidence)))})),reactions:reactions.map(r=>{const {status:_status,evidence,...row}=structuredClone(r);return {...row,label:r.id,evidence:sources(evidence)};})};
 return validateProject(project);
}
