export type Paper = { id:string; doi:string; title:string; journal:string; year?:number; authors:string[]; notes?:string };
export type Chemical = { id:string; name:string; kind:'compound'|'solvent'|'reagent'|'catalyst'; smiles?:string|null; inchikey?:string; formula?:string; molecular_weight?:number; aliases:string[]; notes?:string };
export type Solution = { id:string; solvents:string[]; solutes:{chemical_id:string;role:string;amount:number|null;unit:string|null}[]; concentration:number|null;concentration_unit:string|null };
export type RecordReaction = { id:string;name:string;reactants:string[];products:string[];targets:string[];yield_percent:number|null;yield_basis?:string;status:'draft'|'reviewed';steps:{solution_id:string;temperature?:string|null;time?:string|null;notes?:string}[];evidence:{paper_id:string;page:number;locator:string}[];notes?:string };
export type Library = {schema_version:1;generated_at?:string;papers:Paper[];chemicals:Chemical[];solutions:Solution[];reactions:RecordReaction[]};
export const emptyLibrary:Library={schema_version:1,papers:[],chemicals:[],solutions:[],reactions:[]};
export const normalizeDoi=(s:string)=>s.trim().replace(/^(?:https?:\/\/(?:dx\.)?doi\.org\/|doi:\s*)/i,'').toLowerCase();
const fail=(s:string):never=>{throw new Error(s);};
export function validateLibrary(value:unknown):Library {
 const d=structuredClone(value) as Library;
 if(!d||d.schema_version!==1||JSON.stringify(d).length>5_000_000)fail('Use a Chembrain v1 package smaller than 5 MB.');
 if(Object.keys(d).some(k=>!['schema_version','generated_at','papers','chemicals','solutions','reactions'].includes(k)))fail('Only normalized library tables may be imported.');
 const string=(v:unknown):v is string=>typeof v==='string'&&v.length<=3000;
 const strings=(v:unknown):v is string[]=>Array.isArray(v)&&v.every(string);
 const ids:Record<string,Set<string>>={};
 for(const kind of ['papers','chemicals','solutions','reactions'] as const){
  if(!Array.isArray(d[kind]))fail('Missing '+kind+' table.');ids[kind]=new Set();
  for(const r of d[kind]){if(!r||!string(r.id)||! /^[A-Za-z0-9][A-Za-z0-9._:-]{0,120}$/.test(r.id)||ids[kind].has(r.id))fail('Invalid or duplicate '+kind+' ID.');ids[kind].add(r.id);}
 }
 const optionalString=(v:unknown)=>v==null||string(v);
 const seen=new Set<string>();
 for(const p of d.papers){if(!string(p.doi)||!string(p.title)||!p.title||!string(p.journal)||!strings(p.authors)||!optionalString(p.notes)||(p.year!=null&&(!Number.isInteger(p.year)||p.year<1500||p.year>3000)))fail('Paper title, journal, DOI and authors are required.');p.doi=normalizeDoi(p.doi);if(!/^10\.\d{4,9}\/[^\s<>?#]+$/.test(p.doi)||seen.has(p.doi))fail('Each paper needs a unique valid DOI.');seen.add(p.doi);}
 for(const c of d.chemicals)if(!string(c.name)||!c.name||!['compound','reagent','solvent','catalyst'].includes(c.kind)||!strings(c.aliases)||(c.smiles!=null&&!string(c.smiles))||(c.inchikey!=null&&!string(c.inchikey))||!optionalString(c.formula)||!optionalString(c.notes))fail('Invalid chemical metadata.');
 for(const s of d.solutions)if(!strings(s.solvents)||s.solvents.some(id=>!ids.chemicals.has(id))||!Array.isArray(s.solutes)||s.solutes.some(c=>!c||!ids.chemicals.has(c.chemical_id)||!string(c.role)||(c.amount!==null&&(typeof c.amount!=='number'||!Number.isFinite(c.amount)||c.amount<0))||(c.unit!==null&&!string(c.unit)))||(s.concentration!==null&&(typeof s.concentration!=='number'||!Number.isFinite(s.concentration)||s.concentration<0))||(s.concentration_unit!==null&&!string(s.concentration_unit)))fail('A solution references an unknown chemical or invalid amount.');
 for(const r of d.reactions){
  if(!string(r.name)||!r.name||!optionalString(r.notes)||!optionalString(r.yield_basis)||!['draft','reviewed'].includes(r.status)||!strings(r.reactants)||!r.reactants.length||!strings(r.products)||!r.products.length||!strings(r.targets)||[...r.reactants,...r.products,...r.targets].some(id=>!ids.chemicals.has(id)))fail('Invalid reaction participants.');
  if(r.yield_percent!==null&&(typeof r.yield_percent!=='number'||!Number.isFinite(r.yield_percent)||r.yield_percent<0||r.yield_percent>100))fail('Yield must be 0–100 or null.');
  if(!Array.isArray(r.steps)||r.steps.some(s=>!s||!ids.solutions.has(s.solution_id)||['temperature','time','notes'].some(k=>(s as Record<string,unknown>)[k]!=null&&!string((s as Record<string,unknown>)[k]))))fail('Invalid reaction solution/conditions.');
  if(!Array.isArray(r.evidence)||!r.evidence.length||r.evidence.some(e=>!e||!ids.papers.has(e.paper_id)||!Number.isInteger(e.page)||e.page<1||!string(e.locator)||!e.locator))fail('Reaction DOI evidence and PDF page/locator are required.');
 }
 const compact=(v:unknown):void=>{if(typeof v==='string'&&!string(v))fail('Text field exceeds compact package limit.');if(Array.isArray(v))v.forEach(compact);else if(v&&typeof v==='object')for(const [k,x]of Object.entries(v)){if(['pdf','pages','full_text','text','quote','candidate_text','svg','image','base64'].includes(k))fail('PDF text and images belong in the separate processor.');compact(x);}};compact(d);
 return structuredClone(d);
}
export function mergeLibrary(current:Library,incoming:Library):Library {
 const a=validateLibrary(current),b=validateLibrary(incoming);const paperMap=new Map<string,string>(),chemMap=new Map<string,string>();
 for(const p of b.papers){const old=a.papers.find(x=>x.doi===p.doi);const collision=a.papers.find(x=>x.id===p.id);if(collision&&collision.doi!==p.doi)fail('Paper ID collision with another DOI.');paperMap.set(p.id,old?.id||p.id);if(!old)a.papers.push(p);}
 for(const c of b.chemicals){const old=a.chemicals.find(x=>x.id===c.id||(c.inchikey&&x.inchikey===c.inchikey));if(old?.inchikey&&c.inchikey&&old.inchikey!==c.inchikey)fail('Chemical ID collision with another structure.');chemMap.set(c.id,old?.id||c.id);if(!old)a.chemicals.push(c);}
 for(const s of b.solutions)if(!a.solutions.some(x=>x.id===s.id))a.solutions.push({...s,solvents:s.solvents.map(id=>chemMap.get(id)!),solutes:s.solutes.map(c=>({...c,chemical_id:chemMap.get(c.chemical_id)!}))});
 for(const r of b.reactions)if(!a.reactions.some(x=>x.id===r.id))a.reactions.push({...r,reactants:r.reactants.map(id=>chemMap.get(id)!),products:r.products.map(id=>chemMap.get(id)!),targets:r.targets.map(id=>chemMap.get(id)!),evidence:r.evidence.map(e=>({...e,paper_id:paperMap.get(e.paper_id)!}))});
 return validateLibrary(a);
}
export function relatedReactions(d:Library,id:string|null,route=false):RecordReaction[]{return id?d.reactions.filter(r=>r.reactants.includes(id)||r.products.includes(id)||(route&&r.targets.includes(id))):[];}
export function paperReferences(d:Library,r:RecordReaction){return [...new Set(r.evidence.map(e=>e.paper_id))].map(id=>({paper:d.papers.find(p=>p.id===id)!,evidence:r.evidence.filter(e=>e.paper_id===id)}));}
