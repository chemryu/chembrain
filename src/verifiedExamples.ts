import verified from '../examples/verified-structures.json';
import { validateLibrary, type Chemical, type Library } from './libraryData';

export const LIBRARY_STORE='chembrain.normalized-library.v1';
const examples=verified.structures;

function exampleFor(c:Chemical) {
 return examples.find(e=>c.id===e.id&&c.name===e.name&&c.kind==='compound'&&!c.smiles?.trim()
  &&(!c.formula||c.formula===e.formula)&&(!c.inchikey||c.inchikey===e.inchikey)
  &&(c.molecular_weight==null||Math.abs(c.molecular_weight-e.molecular_weight)<0.02));
}

export function verifiedExampleCount(data:Library) {
 return data.chemicals.filter(c=>exampleFor(c)).length;
}

/** Explicit, narrow enrichment: never replace a user's structure or other facts. */
export function prepareVerifiedExamples(data:Library):Library {
 const next=validateLibrary(data);
 next.chemicals=next.chemicals.map(c=>{
  const e=exampleFor(c);
  return e?{...c,smiles:e.canonical_isomeric_smiles,formula:c.formula||e.formula,
   inchikey:c.inchikey||e.inchikey,molecular_weight:c.molecular_weight??e.molecular_weight}:c;
 });
 return validateLibrary(next);
}

/** Original private bytes are verified before the single primary replacement. */
export function saveVerifiedExamples(data:Library,storage:Pick<Storage,'getItem'|'setItem'>):Library {
 const next=prepareVerifiedExamples(data);
 if(!verifiedExampleCount(data))return next;
 const raw=storage.getItem(LIBRARY_STORE);
 if(raw===null||JSON.stringify(validateLibrary(JSON.parse(raw)))!==JSON.stringify(validateLibrary(data)))
  throw new Error('The stored library changed. Reload before adding example structures.');
 const backup=LIBRARY_STORE+'.structure-backup.'+crypto.randomUUID();
 try{
  if(storage.getItem(backup)!==null)throw new Error('Backup already exists.');
  storage.setItem(backup,raw);
  if(storage.getItem(backup)!==raw)throw new Error('Backup verification failed.');
 }catch{throw new Error('Example structures were not added: a private backup could not be saved. The original library is unchanged.');}
 storage.setItem(LIBRARY_STORE,JSON.stringify(next));
 return next;
}
