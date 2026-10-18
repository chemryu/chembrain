import { useEffect, useState } from 'react';
import type { Chemical } from './libraryData';
import { renderStructure, type StructureResult } from './structureRenderer';
import './structure-diagram.css';

type DisplayResult=StructureResult|{status:'loading';message:string};
const initial=(smiles:string):DisplayResult=>smiles.trim()?{status:'loading',message:'Drawing structure…'}:{status:'missing',message:'Structure not encoded'};

export default function StructureDiagram({chemical,large=false}:{chemical:Chemical;large?:boolean}) {
 const smiles=chemical.smiles||'';
 const [state,setState]=useState<{smiles:string;result:DisplayResult}>(()=>({smiles,result:initial(smiles)}));
 useEffect(()=>{
  let active=true;
  setState({smiles,result:initial(smiles)});
  renderStructure(smiles).then(result=>{if(active)setState({smiles,result});});
  return ()=>{active=false;};
 },[smiles]);
 // Effects run after a render. Hide the previous SMILES immediately, including
 // the frame between an edit/import and this input's asynchronous resolution.
 const result=state.smiles===smiles?state.result:initial(smiles);
 const className='structure-diagram'+(large?' structure-diagram-large':'');
 if(result.status==='ready')return <img className={className} src={result.src} alt={chemical.name+' structure diagram'} data-smiles={smiles} data-structure-state="ready" width={600} height={360} onError={()=>setState({smiles,result:{status:'unavailable',message:'Structure image could not be displayed.'}})}/>;
 const explanation=result.status==='missing'?'No verified SMILES is recorded. Paper-numbered intermediates need a verified structure before a diagram can be drawn.':result.status==='invalid'?'This SMILES could not be parsed as a valid molecule. Edit the chemical and check its structural notation.':result.message;
 return <span className={className+' structure-fallback'} data-smiles={smiles} data-structure-state={result.status} title={explanation}><span>{result.message}</span>{large&&<small>{explanation}</small>}</span>;
}
