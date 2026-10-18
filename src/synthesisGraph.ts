import type { Chemical, Library, RecordReaction } from './libraryData';

/** Typed IDs keep imported chemical/reaction IDs in separate namespaces. */
export const moleculeNodeId = (id:string) => 'chemical:'+id;
export const reactionNodeId = (id:string) => 'reaction:'+id;
export const SYNTHESIS_NODE_WIDTH=224;
export const SYNTHESIS_NODE_HEIGHT=206;

export type SynthesisNode = {
 id:string; kind:'chemical'|'reaction'; recordId:string;
 position:{x:number;y:number}; component:number;
 chemical?:Chemical; reaction?:RecordReaction;
};
export type SynthesisEdge = {id:string;source:string;target:string;role:'reactant'|'product'};
export type SynthesisGraph = {
 nodes:SynthesisNode[]; edges:SynthesisEdge[]; reactionIds:string[];
 selectedNodeId:string; focusNodeIds:string[];
 componentCount:number; truncated:boolean; limits:{maxNodes:number;maxReactions:number};
};
type Limits={maxNodes?:number;maxReactions?:number};
const unique=(values:string[])=>[...new Set(values)];
const compare=(a:string,b:string)=>a<b?-1:a>b?1:0;
const bounded=(value:number|undefined,fallback:number,maximum:number)=>
 value===undefined||!Number.isFinite(value)?fallback:Math.max(1,Math.min(maximum,Math.floor(value)));

/**
 * Recorded chemistry only: targets select route members but NEVER make edges.
 * Include directly related transformations, target-tagged fragments, and their
 * recorded precursors. A displayed reaction always retains every participant.
 * Traversal/render limits stop expansion explicitly, including cyclic imports.
 */
export function buildSynthesisGraph(library:Library,selectedId:string,options:Limits={}):SynthesisGraph {
 const limits={maxNodes:bounded(options.maxNodes,360,1000),maxReactions:bounded(options.maxReactions,120,400)};
 const chemicals=new Map(library.chemicals.map(c=>[c.id,c]));
 const selectedNodeId=moleculeNodeId(selectedId);
 const result:SynthesisGraph={nodes:[],edges:[],reactionIds:[],selectedNodeId,focusNodeIds:[],componentCount:0,truncated:false,limits};
 if(!chemicals.has(selectedId))return result;
 const producers=new Map<string,RecordReaction[]>();
 const direct:RecordReaction[]=[],tagged:RecordReaction[]=[];
 // Iteration is bounded by the already validated compact package size. Only the
 // selected context is traversed; unrelated records are never rendered.
 const ordered=[...library.reactions].sort((a,b)=>compare(a.id,b.id));
 for(const reaction of ordered){
  for(const id of unique(reaction.products)){
   const rows=producers.get(id)||[];rows.push(reaction);producers.set(id,rows);
  }
  if(reaction.reactants.includes(selectedId)||reaction.products.includes(selectedId))direct.push(reaction);
  else if(reaction.targets.includes(selectedId))tagged.push(reaction);
 }
 const queue=[...direct,...tagged];
 const queued=new Set(queue.map(r=>r.id)),visited=new Set<string>();
 const includedChemicals=new Set([selectedId]);
 const chosen:RecordReaction[]=[];
 for(let cursor=0;cursor<queue.length;cursor++){
  const reaction=queue[cursor];
  if(visited.has(reaction.id))continue;
  visited.add(reaction.id);
  if(chosen.length>=limits.maxReactions){result.truncated=true;break;}
  const participants=unique([...reaction.reactants,...reaction.products]);
  const additional=participants.filter(id=>!includedChemicals.has(id));
  // Never trim a large convergent reaction down to a misleading subset.
  if(participants.some(id=>!chemicals.has(id))||includedChemicals.size+chosen.length+1+additional.length>limits.maxNodes){
   result.truncated=true;continue;
  }
  chosen.push(reaction);additional.forEach(id=>includedChemicals.add(id));
  for(const id of unique(reaction.reactants))for(const precursor of producers.get(id)||[]){
   if(!queued.has(precursor.id)){queue.push(precursor);queued.add(precursor.id);}
  }
 }
 result.reactionIds=chosen.map(r=>r.id);
 for(const id of [...includedChemicals].sort(compare))result.nodes.push({id:moleculeNodeId(id),kind:'chemical',recordId:id,chemical:chemicals.get(id)!,position:{x:0,y:0},component:0});
 for(const reaction of chosen){
  const id=reactionNodeId(reaction.id);
  result.nodes.push({id,kind:'reaction',recordId:reaction.id,reaction,position:{x:0,y:0},component:0});
  for(const chemical of unique(reaction.reactants))result.edges.push({id:JSON.stringify(['in',chemical,reaction.id]),source:moleculeNodeId(chemical),target:id,role:'reactant'});
  for(const chemical of unique(reaction.products))result.edges.push({id:JSON.stringify(['out',reaction.id,chemical]),source:id,target:moleculeNodeId(chemical),role:'product'});
 }
 const directIds=new Set([selectedNodeId]);
 for(const reaction of direct)if(result.reactionIds.includes(reaction.id)){
  directIds.add(reactionNodeId(reaction.id));
  for(const id of [...reaction.reactants,...reaction.products])directIds.add(moleculeNodeId(id));
 }
 result.focusNodeIds=result.nodes.filter(n=>directIds.has(n.id)).map(n=>n.id);
 layoutGraph(result);
 return result;
}

/** SCC condensation gives bounded ranks even when imported records form cycles. */
function layoutGraph(graph:SynthesisGraph):void {
 const nodes=new Map(graph.nodes.map(n=>[n.id,n]));
 const next=new Map(graph.nodes.map(n=>[n.id,[] as string[]]));
 const previous=new Map(graph.nodes.map(n=>[n.id,[] as string[]]));
 for(const edge of graph.edges){next.get(edge.source)!.push(edge.target);previous.get(edge.target)!.push(edge.source);}
 const components:string[][]=[];const seen=new Set<string>();
 const starts=[graph.selectedNodeId,...nodes.keys()];
 for(const start of starts){
  if(seen.has(start)||!nodes.has(start))continue;
  const group=[start];seen.add(start);
  for(let i=0;i<group.length;i++)for(const id of [...next.get(group[i])!,...previous.get(group[i])!])if(!seen.has(id)){seen.add(id);group.push(id);}
  components.push(group);
 }
 graph.componentCount=components.length;
 let offsetY=0;
 for(const [component,group] of components.entries()){
  const visited=new Set<string>(),finish:string[]=[];
  // Iterative DFS avoids a recursion-depth dependency in long user routes.
  for(const start of group){
   if(visited.has(start))continue;
   const stack:{id:string;exit:boolean}[]=[{id:start,exit:false}];
   while(stack.length){
    const item=stack.pop()!;
    if(item.exit){finish.push(item.id);continue;}
    if(visited.has(item.id))continue;
    visited.add(item.id);stack.push({id:item.id,exit:true});
    for(const id of [...next.get(item.id)!].reverse())if(!visited.has(id))stack.push({id,exit:false});
   }
  }
  const scc=new Map<string,number>();const members:string[][]=[];
  for(const start of finish.reverse()){
   if(scc.has(start))continue;
   const list=[start],number=members.length;scc.set(start,number);
   for(let i=0;i<list.length;i++)for(const id of previous.get(list[i])!)if(!scc.has(id)){scc.set(id,number);list.push(id);}
   members.push(list);
  }
  const successors=members.map(()=>new Set<number>()),incoming=members.map(()=>0),ranks=members.map(()=>0);
  for(const id of group)for(const destination of next.get(id)!){
   const a=scc.get(id)!,b=scc.get(destination)!;
   if(a!==b&&!successors[a].has(b)){successors[a].add(b);incoming[b]++;}
  }
  const queue=incoming.flatMap((n,i)=>n===0?[i]:[]);
  for(let i=0;i<queue.length;i++)for(const to of successors[queue[i]]){
   ranks[to]=Math.max(ranks[to],ranks[queue[i]]+1);
   if(--incoming[to]===0)queue.push(to);
  }
  const columns=new Map<number,string[]>();
  for(const id of [...group].sort(compare)){const rank=ranks[scc.get(id)!];const column=columns.get(rank)||[];column.push(id);columns.set(rank,column);}
  const height=Math.max(...[...columns.values()].map(column=>column.length))*(SYNTHESIS_NODE_HEIGHT+38);
  for(const [rank,column] of columns)for(const [row,id] of column.entries()){
   const node=nodes.get(id)!;node.component=component;
   node.position={x:rank*(SYNTHESIS_NODE_WIDTH+104),y:offsetY+(height-column.length*(SYNTHESIS_NODE_HEIGHT+38))/2+row*(SYNTHESIS_NODE_HEIGHT+38)};
  }
  offsetY+=height+140;
 }
}
