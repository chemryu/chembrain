import { useEffect,useMemo,useRef,useState,type ReactNode } from 'react';
import { Background,BackgroundVariant,Handle,MarkerType,Position,ReactFlow,useNodesState,type Edge,type Node,type NodeProps,type ReactFlowInstance } from '@xyflow/react';
import { ArrowRight,Focus,Maximize2,Minus,Plus } from 'lucide-react';
import type { Chemical,Library,RecordReaction } from './libraryData';
import { buildSynthesisGraph,SYNTHESIS_NODE_HEIGHT,SYNTHESIS_NODE_WIDTH } from './synthesisGraph';
import '@xyflow/react/dist/style.css';
import './synthesis-map.css';

type MoleculeMapNode=Node<{chemical:Chemical;selected:boolean;activate:(id:string)=>void;depiction:(chemical:Chemical)=>ReactNode},'synthesisMolecule'>;
type ReactionMapNode=Node<{reaction:RecordReaction;active:boolean;activate:(id:string)=>void},'synthesisReaction'>;
type MapNode=MoleculeMapNode|ReactionMapNode;
function MoleculeCard({data}:NodeProps<MoleculeMapNode>){
 return <div className={'synthesis-node synthesis-molecule '+(data.selected?'is-target':'')}>
  <Handle type="target" position={Position.Left}/>
  <div className="synthesis-drag">{data.selected?'Selected molecule':'Molecule'}<span aria-hidden="true">⠿</span></div>
  <button className="synthesis-node-button nodrag nopan" aria-label={'Open molecule: '+data.chemical.name} onClick={()=>data.activate(data.chemical.id)}>
   <div className="synthesis-depiction">{data.depiction(data.chemical)}</div>
   <strong title={data.chemical.name}>{data.chemical.name}</strong>
   <small>{data.chemical.formula||'Structure pending'}</small>
  </button>
  <Handle type="source" position={Position.Right}/>
 </div>;
}
function ReactionCard({data}:NodeProps<ReactionMapNode>){
 return <div className={'synthesis-node synthesis-reaction '+(data.active?'is-active':'')}>
  <Handle type="target" position={Position.Left}/>
  <div className="synthesis-drag">Reaction<ArrowRight size={13}/></div>
  <button className="synthesis-node-button nodrag nopan" aria-label={'Open reaction: '+data.reaction.name} aria-pressed={data.active} onClick={()=>data.activate(data.reaction.id)}>
   <span className={'synthesis-review '+data.reaction.status}>{data.reaction.status==='reviewed'?'Reviewed record':'Draft · verify source'}</span>
   <strong title={data.reaction.name}>{data.reaction.name}</strong>
   <small>{data.reaction.yield_percent==null?'Yield not reported':data.reaction.yield_percent+'% reported yield'}</small>
   <span className="synthesis-open-detail">View conditions & DOI ↗</span>
  </button>
  <Handle type="source" position={Position.Right}/>
 </div>;
}
const nodeTypes={synthesisMolecule:MoleculeCard,synthesisReaction:ReactionCard};

export function SynthesisMap({library,selectedId,onSelectMolecule,onSelectReaction,depiction,activeReactionId=null}:{
 library:Library;selectedId:string;onSelectMolecule:(id:string)=>void;onSelectReaction:(id:string)=>void;
 depiction:(chemical:Chemical)=>ReactNode;activeReactionId?:string|null;
}){
 const graph=useMemo(()=>buildSynthesisGraph(library,selectedId),[library,selectedId]);
 const callbacks=useRef({onSelectMolecule,onSelectReaction,depiction});
 callbacks.current={onSelectMolecule,onSelectReaction,depiction};
 const canvas=useRef<HTMLDivElement>(null);
 const [instance,setInstance]=useState<ReactFlowInstance<MapNode,Edge>|null>(null);
 const [nodes,setNodes,onNodesChange]=useNodesState<MapNode>([]);
 const projected=useMemo<MapNode[]>(()=>graph.nodes.map(node=>({
  id:node.id,position:node.position,width:SYNTHESIS_NODE_WIDTH,dragHandle:'.synthesis-drag',
  type:node.kind==='chemical'?'synthesisMolecule':'synthesisReaction',
  data:node.kind==='chemical'?{chemical:node.chemical!,selected:node.recordId===selectedId,activate:(id:string)=>callbacks.current.onSelectMolecule(id),depiction:(chemical:Chemical)=>callbacks.current.depiction(chemical)}:{reaction:node.reaction!,active:false,activate:(id:string)=>callbacks.current.onSelectReaction(id)},
 })) as MapNode[],[graph,selectedId]);
 const edges=useMemo<Edge[]>(()=>graph.edges.map(edge=>({...edge,type:'smoothstep',markerEnd:{type:MarkerType.ArrowClosed,color:'#71895a',width:15,height:15},style:{stroke:'#8d9f79',strokeWidth:1.7}})),[graph]);
 useEffect(()=>{setNodes(projected);},[projected,setNodes]);
 useEffect(()=>{setNodes(current=>current.map(node=>node.type==='synthesisReaction'?{...node,data:{...node.data,active:node.data.reaction.id===activeReactionId}}:node));},[activeReactionId,projected,setNodes]);
 function focusSelected(duration=180){
  if(!instance)return;
  const selected=instance.getNode(graph.selectedNodeId);
  if((canvas.current?.clientWidth||0)<560&&selected){
   // Keep the selected card readable on a phone; pan or Fit to inspect branches.
   const width=selected.measured?.width??selected.width??SYNTHESIS_NODE_WIDTH;
   const height=selected.measured?.height??selected.height??SYNTHESIS_NODE_HEIGHT;
   void instance.setCenter(selected.position.x+width/2-45,selected.position.y+height/2,{zoom:0.75,duration});
  }else void instance.fitView({nodes:graph.focusNodeIds.map(id=>({id})),padding:0.25,minZoom:0.55,maxZoom:0.9,duration});
 }
 useEffect(()=>{
  if(!instance)return;
  const timer=setTimeout(()=>focusSelected(0),100);
  return()=>clearTimeout(timer);
  // Node placement changes only with chemistry context, not opening its details.
 },[instance,graph]);
 return <section className="synthesis-map" aria-label="Recorded synthesis map">
  <div className="synthesis-heading"><div><h3>Recorded synthesis map</h3><p>{graph.reactionIds.length} {graph.truncated?'displayed':'recorded'} reactions · {graph.componentCount} connected {graph.componentCount===1?'fragment':'fragments'}</p></div><span className="synthesis-selected-key">Selected molecule</span></div>
  <p className="synthesis-boundary">Arrows show recorded reactants → reaction → products. Target tags group steps; they do not establish chemical connections. Draft records require source review.</p>
  {graph.componentCount>1&&<p className="synthesis-fragment-note" role="note">Separate fragments have unrecorded connecting steps. They are shown apart; no missing transformations are inferred.</p>}
  {graph.truncated&&<p className="synthesis-truncation" role="status">Partial map: display limit reached ({graph.limits.maxReactions} reactions / {graph.limits.maxNodes} nodes). Some whole reactions are omitted; every displayed reaction keeps all its recorded participants.</p>}
  {!graph.reactionIds.length?<div className="synthesis-empty">{graph.truncated?'No complete reaction fits this display limit. Use List to inspect the recorded reactions.':'No recorded reactions for this molecule. Import a normalized package to add evidence.'}</div>:<>
   <div className="synthesis-controls" aria-label="Synthesis map controls">
    <button aria-label="Zoom in synthesis map" onClick={()=>void instance?.zoomIn({duration:150})}><Plus size={15}/><span>Zoom in</span></button>
    <button aria-label="Zoom out synthesis map" onClick={()=>void instance?.zoomOut({duration:150})}><Minus size={15}/><span>Zoom out</span></button>
    <button aria-label="Fit synthesis map" onClick={()=>void instance?.fitView({padding:0.16,minZoom:0.08,maxZoom:0.9,duration:180})}><Maximize2 size={15}/><span>Show all recorded steps</span></button>
    <button aria-label="Focus selected molecule" onClick={()=>focusSelected()}><Focus size={15}/><span>Focus selected molecule</span></button>
   </div>
   <div className="synthesis-canvas" ref={canvas}>
    <ReactFlow<MapNode,Edge> nodes={nodes} edges={edges} nodeTypes={nodeTypes} onInit={setInstance} onNodesChange={onNodesChange} nodesConnectable={false} nodesFocusable={false} edgesFocusable={false} elementsSelectable={false} minZoom={0.08} maxZoom={1.5} panOnScroll={false} preventScrolling={false} proOptions={{hideAttribution:true}} aria-label="Interactive recorded synthesis graph">
     <Background color="#ccd6bd" gap={22} size={1} variant={BackgroundVariant.Dots}/>
    </ReactFlow>
   </div>
   <p className="synthesis-instructions">Drag the background to pan; drag a card header to arrange it. Click a molecule to explore it or a reaction for conditions and DOI. Use List for a linear view. Layout changes are not saved as chemistry data.</p>
  </>}
 </section>;
}
