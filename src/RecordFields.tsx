import type { Chemical } from './libraryData';

const isObject = (value: unknown): value is Record<string, unknown> =>
  value !== null && typeof value === 'object' && !Array.isArray(value);

// This checks rendering safety only. Referential and scientific validation stays
// in validateLibrary at save time, so an ordinary unfinished form stays editable.
export function parseRecordDraft(kind: string, value: string): Record<string, unknown> {
  let parsed: unknown;
  try { parsed = JSON.parse(value); }
  catch { throw new Error('Correct the advanced JSON syntax before using the form or saving.'); }
  const bad = (field: string, expected: string): never => {
    throw new Error(`Advanced JSON: ${field} must be ${expected}. Correct the draft below or close the editor to discard it.`);
  };
  if (!isObject(parsed)) return bad('record', 'an object');
  const row = parsed;
  const scalar = (object: Record<string, unknown>, key: string, path = key, number = false) => {
    const v = object[key];
    if (v != null && typeof v !== (number ? 'number' : 'string')) bad(path, number ? 'a number or null' : 'a string or null');
  };
  const strings = (key: string) => {
    if (!Array.isArray(row[key]) || !(row[key] as unknown[]).every(v => typeof v === 'string')) bad(key, 'an array of strings');
  };
  const objects = (key: string): Record<string, unknown>[] => {
    if (!Array.isArray(row[key])) return bad(key, 'an array of objects');
    return (row[key] as unknown[]).map((v, i) => isObject(v) ? v : bad(`${key}[${i}]`, 'an object'));
  };
  scalar(row, 'id');
  if (kind === 'chemical' || kind === 'reaction') scalar(row, 'notes');
  if (kind === 'paper') {
    scalar(row, 'doi');
    strings('authors');
  } else if (kind === 'chemical') {
    for (const k of ['name', 'smiles']) scalar(row, k);
    strings('aliases');
  } else if (kind === 'reaction') {
    for (const k of ['name', 'status']) scalar(row, k);
    scalar(row, 'yield_percent', 'yield_percent', true);
    strings('reactants'); strings('products');
    objects('steps').forEach((step, i) => {
      for (const k of ['temperature', 'time']) scalar(step, k, `steps[${i}].${k}`);
    });
  } else if (kind === 'solution') {
    strings('solvents');
    scalar(row, 'concentration', 'concentration', true);
    scalar(row, 'concentration_unit');
    objects('solutes').forEach((solute, i) => {
      for (const k of ['chemical_id', 'role', 'unit']) scalar(solute, k, `solutes[${i}].${k}`);
      scalar(solute, 'amount', `solutes[${i}].amount`, true);
    });
  } else bad('record kind', 'a supported record type');
  return row;
}
export function RecordFields({kind,value,onChange,chemicals}:{kind:string;value:string;onChange:(s:string)=>void;chemicals:Chemical[]}){
 let row:Record<string,unknown>;try{row=parseRecordDraft(kind,value);}catch(error){return <p role="alert">{(error as Error).message}</p>;}
 const update=(key:string,v:unknown)=>onChange(JSON.stringify({...row,[key]:v},null,2));
 const field=(key:string,label:string,type='text')=><label className="record-field" key={key}>{label}<input type={type} value={String(row[key]??'')} onChange={e=>update(key,type==='number'?(e.target.value===''?null:Number(e.target.value)):e.target.value)}/></label>;
 const participants=(key:string,label:string)=><label className="record-field">{label}<select multiple size={5} value={(row[key] as string[])||[]} onChange={e=>update(key,Array.from(e.target.selectedOptions,x=>x.value))}>{chemicals.map(c=><option key={c.id} value={c.id}>{c.name}</option>)}</select><small>Use Ctrl/Cmd to select multiple entries.</small></label>;
 return <div className="record-fields">{kind==='paper'?<>{field('doi','DOI')}<label className="record-field">Authors (separate with semicolons)<textarea rows={3} value={(row.authors as string[]).join('; ')} onChange={e=>update('authors',e.target.value.split(';').map(s=>s.trim()).filter(Boolean))}/></label></>:kind==='chemical'?<>{field('name','Molecule name')}{field('smiles','SMILES (optional; normalize in processor)')}<label className="record-field">Aliases (separate with semicolons)<input value={(row.aliases as string[]).join('; ')} onChange={e=>update('aliases',e.target.value.split(';').map(s=>s.trim()).filter(Boolean))}/></label></>:kind==='reaction'?<>{field('name','Reaction name')}{field('yield_percent','Reported yield (%)','number')}<label className="record-field">Review status<select value={String(row.status)} onChange={e=>update('status',e.target.value)}><option value="draft">Draft</option><option value="reviewed">Reviewed by me</option></select></label>{participants('reactants','Reactants')}{participants('products','Products')}{(row.steps as Record<string,unknown>[]).map((step,i)=><fieldset key={i}><legend>Step {i+1}</legend>{['temperature','time'].map(k=><label className="record-field" key={k}>{k}<input value={String(step[k]??'')} placeholder="Not reported" onChange={e=>update('steps',(row.steps as Record<string,unknown>[]).map((s,j)=>j===i?{...s,[k]:e.target.value||null}:s))}/></label>)}</fieldset>)}</>:<>{participants('solvents','Solvents')}{field('concentration','Concentration (blank = not reported)','number')}{field('concentration_unit','Concentration unit')}<h3>Solutes</h3>{(row.solutes as Record<string,unknown>[]).map((solute,i)=><fieldset key={i}><legend>Solute {i+1}</legend><select aria-label={'Solute '+(i+1)} value={String(solute.chemical_id)} onChange={e=>update('solutes',(row.solutes as Record<string,unknown>[]).map((s,j)=>j===i?{...s,chemical_id:e.target.value}:s))}>{chemicals.map(c=><option key={c.id} value={c.id}>{c.name}</option>)}</select>{['role','amount','unit'].map(k=><label className="record-field" key={k}>{k}<input type={k==='amount'?'number':'text'} step="any" value={String(solute[k]??'')} onChange={e=>update('solutes',(row.solutes as Record<string,unknown>[]).map((s,j)=>j===i?{...s,[k]:k==='amount'?(e.target.value===''?null:Number(e.target.value)):(e.target.value||null)}:s))}/></label>)}<button onClick={()=>update('solutes',(row.solutes as Record<string,unknown>[]).filter((_,j)=>i!==j))}>Remove solute</button></fieldset>)}<button onClick={()=>update('solutes',[...(row.solutes as unknown[]),{chemical_id:chemicals[0]?.id||'',role:'reagent',amount:null,unit:null}])}>Add solute</button></>}{(kind==='chemical'||kind==='reaction')&&<label className="record-field">Notes<textarea rows={3} value={String(row.notes||'')} onChange={e=>update('notes',e.target.value)}/></label>}</div>;
}
