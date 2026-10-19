import createRDKitModule, { type MainModule, type Mol } from '@rdkit/rdkit';
import compressedWasm from 'virtual:chembrain-rdkit-wasm';
import {molecularFormula} from './molecularFormula';

/** Rendering is derived from current SMILES; images never enter library JSON. */
export type StructureResult =
 | {status:'ready';src:string}
 | {status:'missing';message:string}
 | {status:'invalid';message:string}
 | {status:'unavailable';message:string};

const MAX_SMILES_LENGTH=3000;
const MAX_CACHE_ENTRIES=64;
const cache=new Map<string,Promise<StructureResult>>();
let modulePromise:Promise<MainModule>|undefined;

const missing:StructureResult={status:'missing',message:'Structure not encoded'};
const invalid:StructureResult={status:'invalid',message:'Invalid SMILES'};

async function initialize():Promise<MainModule> {
 if(typeof WebAssembly==='undefined'||typeof DecompressionStream==='undefined')throw new Error('This browser does not support the bundled structure renderer.');
 // Build-time gzip and base64 keep the single-file download small. No network,
 // object URL, CDN or local asset is used, including when opened via file://.
 const binary=atob(compressedWasm);
 const compressed=new Uint8Array(binary.length);
 for(let i=0;i<binary.length;i++)compressed[i]=binary.charCodeAt(i);
 const decompressed=new Blob([compressed]).stream().pipeThrough(new DecompressionStream('gzip'));
 const wasmBinary=new Uint8Array(await new Response(decompressed).arrayBuffer());
 const compiled=await WebAssembly.compile(wasmBinary);
 // This pinned MinimalLib build exposes instantiateWasm but does not wire the
 // usual wasmBinary option. Explicit instantiation avoids its fetch fallback.
 const rdkit=await createRDKitModule({instantiateWasm:(imports:WebAssembly.Imports,receive:(instance:WebAssembly.Instance)=>void)=>{
  const instance=new WebAssembly.Instance(compiled,imports);
  receive(instance);
  return instance.exports;
 }});
 // Invalid user input is reported next to its chemical rather than as console
 // parser noise. This setting affects RDKit's own logs, not library validation.
 rdkit.disable_logging();
 return rdkit;
}

function module():Promise<MainModule> {
 if(!modulePromise)modulePromise=initialize();
 return modulePromise;
}

export type StructureInspection={smiles:string;canonical_smiles:string;formula:string;inchikey:string;molecular_weight:number;engine:string;fragments:number;unassigned_stereocenters:number};

/** Compute identity from the actual graph. Source agreement is a separate human check. */
export async function inspectStructure(smiles:string):Promise<StructureInspection> {
 if(!smiles.trim()||smiles.length>MAX_SMILES_LENGTH)throw new Error('Enter a SMILES below 3000 characters.');
 const rdkit=await module();let molecule:Mol|null=null;
 try{
  molecule=rdkit.get_mol(smiles);
  if(!molecule||!molecule.is_valid()||!molecule.get_num_atoms())throw new Error('Invalid SMILES.');
  const descriptors=JSON.parse(molecule.get_descriptors()) as Record<string,number>;
  const canonical_smiles=molecule.get_smiles();
  const formula=molecularFormula(molecule.get_json());
  const inchikey=rdkit.get_inchikey_for_inchi(molecule.get_inchi());
  if(!formula||!inchikey||!Number.isFinite(descriptors.amw))throw new Error('This structure cannot be normalized.');
  return {smiles,canonical_smiles,formula,inchikey,molecular_weight:Math.round(descriptors.amw*100)/100,engine:'RDKit '+rdkit.version(),fragments:canonical_smiles.split('.').length,unassigned_stereocenters:descriptors.NumUnspecifiedAtomStereoCenters??0};
 }finally{molecule?.delete();}
}

async function draw(smiles:string):Promise<StructureResult> {
 let rdkit:MainModule;
 try{rdkit=await module();}
 catch{return {status:'unavailable',message:'Structure renderer unavailable. Open this file in a current Chrome or Edge browser.'};}
 let molecule:Mol|null=null;
 try{
  try{molecule=rdkit.get_mol(smiles);}
  catch{return invalid;}
  if(!molecule||!molecule.is_valid()||molecule.get_num_atoms()===0)return invalid;
  const svg=molecule.get_svg(600,360);
  if(!/<svg(?:\s|>)/i.test(svg))return {status:'unavailable',message:'Structure drawing unavailable for this SMILES.'};
  // An image source gives generated SVG its own document context. Never inject
  // molecule-derived SVG as application HTML, even for imported user records.
  return {status:'ready',src:'data:image/svg+xml;charset=utf-8,'+encodeURIComponent(svg)};
 }catch{return {status:'unavailable',message:'Structure drawing unavailable for this SMILES.'};}
 finally{if(molecule)molecule.delete();}
}

/** Full-input LRU cache also shares in-flight work across tile/map/selection. */
export function renderStructure(smiles:string|null|undefined):Promise<StructureResult> {
 if(!smiles||!smiles.trim())return Promise.resolve(missing);
 if(smiles.length>MAX_SMILES_LENGTH)return Promise.resolve(invalid);
 const previous=cache.get(smiles);
 if(previous){cache.delete(smiles);cache.set(smiles,previous);return previous;}
 const pending=draw(smiles).catch(():StructureResult=>({status:'unavailable',message:'Structure drawing unavailable for this SMILES.'}));
 cache.set(smiles,pending);
 if(cache.size>MAX_CACHE_ENTRIES)cache.delete(cache.keys().next().value!);
 return pending;
}
