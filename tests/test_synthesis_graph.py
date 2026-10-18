"""Execute the real TypeScript projection on recorded and hostile-size routes."""
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def graph_check(body: str) -> None:
    script = f"""
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {{buildSynthesisGraph,moleculeNodeId,reactionNodeId}} from {json.dumps((ROOT/'src/synthesisGraph.ts').as_uri())};
const chemical=id=>({{id,name:id,kind:'compound',aliases:[]}});
const reaction=(id,reactants,products,targets=[])=>({{id,name:id,reactants,products,targets,status:'draft',yield_percent:null,steps:[],evidence:[]}});
const library=(ids,reactions)=>({{schema_version:1,papers:[],chemicals:ids.map(chemical),solutions:[],reactions}});
function assertExactEdges(g,d){{
 const nodes=new Map(g.nodes.map(n=>[n.id,n]));
 assert.equal(nodes.size,g.nodes.length);
 for(const e of g.edges){{
  assert.ok(nodes.has(e.source)&&nodes.has(e.target),'dangling edge');
  const source=nodes.get(e.source),target=nodes.get(e.target);
  if(e.role==='reactant'){{assert.equal(source.kind,'chemical');assert.equal(target.kind,'reaction');assert.ok(target.reaction.reactants.includes(source.recordId));}}
  else{{assert.equal(source.kind,'reaction');assert.equal(target.kind,'chemical');assert.ok(source.reaction.products.includes(target.recordId));}}
 }}
 for(const id of g.reactionIds){{
  const r=d.reactions.find(r=>r.id===id);
  assert.ok(nodes.has(reactionNodeId(id)));
  for(const c of new Set(r.reactants))assert.ok(g.edges.some(e=>e.source===moleculeNodeId(c)&&e.target===reactionNodeId(id)),'lost reactant');
  for(const c of new Set(r.products))assert.ok(g.edges.some(e=>e.source===reactionNodeId(id)&&e.target===moleculeNodeId(c)),'lost product');
 }}
}}
{body}
"""
    result = subprocess.run(
        ['node', '--experimental-strip-types', '--input-type=module', '-e', script],
        cwd=ROOT, capture_output=True, text=True, timeout=20,
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_recorded_seed_fragments_are_not_falsely_joined():
    graph_check(f"""
const d=JSON.parse(fs.readFileSync({json.dumps(str(ROOT/'public/library.json'))},'utf8'));
const before=JSON.stringify(d),taxol=buildSynthesisGraph(d,'paclitaxel'),doxy=buildSynthesisGraph(d,'doxycycline');
assert.equal(taxol.reactionIds.length,8);assert.equal(taxol.componentCount,5);
assert.equal(doxy.reactionIds.length,4);assert.equal(doxy.componentCount,2);
assertExactEdges(taxol,d);assertExactEdges(doxy,d);
const component=id=>taxol.nodes.find(n=>n.id===moleculeNodeId(id)).component;
assert.equal(component('baran-19'),component('baran-22'));
assert.notEqual(component('baran-22'),component('baran-34'));
assert.notEqual(component('holton-5'),component('holton-17'));
assert.equal(component('baran-34'),component('paclitaxel'));
assert.equal(JSON.stringify(d),before);
assert.deepEqual(buildSynthesisGraph(d,'paclitaxel'),taxol);
""")


def test_convergent_alternative_precursors_and_direct_intermediate_context():
    graph_check("""
const d=library(['a','b','c','m','target','after','x','y'],[
 reaction('join',['a','b'],['m']),reaction('finish',['m','c'],['target']),
 reaction('alternative',['a'],['target']),reaction('consumer',['target'],['after']),
 reaction('same-doi-unrelated',['x'],['y']),
]);
const g=buildSynthesisGraph(d,'target');
assert.deepEqual(new Set(g.reactionIds),new Set(['join','finish','alternative','consumer']));
assert.equal(g.componentCount,1);assertExactEdges(g,d);
assert.equal(g.edges.filter(e=>e.target===reactionNodeId('join')).length,2);
const intermediate=buildSynthesisGraph(d,'m');
assert.deepEqual(new Set(intermediate.reactionIds),new Set(['join','finish']));
assert.ok(!intermediate.reactionIds.includes('alternative'));
assertExactEdges(intermediate,d);
assert.ok(g.focusNodeIds.includes(moleculeNodeId('target')));
assert.ok(g.focusNodeIds.includes(reactionNodeId('finish')));
for(const id of ['m','c','a','after'])assert.ok(g.focusNodeIds.includes(moleculeNodeId(id)),'focus lost a direct reaction participant');
""")


def test_target_tags_group_fragments_without_creating_transformations():
    graph_check("""
const d=library(['a','b','target','x','y'],[
 reaction('tag-only',['a'],['b'],['target']),reaction('unrelated',['x'],['y']),
]);
const g=buildSynthesisGraph(d,'target');
assert.deepEqual(g.reactionIds,['tag-only']);assert.equal(g.componentCount,2);
assert.equal(g.edges.length,2);assertExactEdges(g,d);
assert.ok(!g.edges.some(e=>e.source===moleculeNodeId('target')||e.target===moleculeNodeId('target')));
const empty=buildSynthesisGraph(d,'x',{maxNodes:1});
assert.equal(empty.reactionIds.length,0);assert.equal(empty.nodes.length,1);assert.equal(empty.truncated,true);
const missing=buildSynthesisGraph(d,'missing');assert.equal(missing.nodes.length,0);assert.equal(missing.edges.length,0);
""")


def test_cycles_duplicate_participants_and_cross_table_ids_are_safe():
    graph_check("""
const d=library(['same','b','c','lonely'],[
 reaction('same',['same','same'],['b','b']),reaction('return',['b'],['same']),
 reaction('shared',['b'],['c']),
]);
const before=JSON.stringify(d),g=buildSynthesisGraph(d,'same');
assert.deepEqual(new Set(g.reactionIds),new Set(['same','return']));
assert.notEqual(moleculeNodeId('same'),reactionNodeId('same'));
assert.equal(g.edges.length,4);assert.equal(g.componentCount,1);assertExactEdges(g,d);
assert.equal(new Set(g.nodes.map(n=>JSON.stringify(n.position))).size,g.nodes.length,'overlapping cycle nodes');
assert.ok(g.nodes.every(n=>Number.isFinite(n.position.x)&&Number.isFinite(n.position.y)));
assert.deepEqual(buildSynthesisGraph(d,'same'),g);assert.equal(JSON.stringify(d),before);
const empty=buildSynthesisGraph(d,'lonely');assert.equal(empty.nodes.length,1);assert.equal(empty.reactionIds.length,0);assert.equal(empty.truncated,false);
""")


def test_large_context_and_huge_fanout_omit_whole_reactions_with_notice():
    graph_check("""
const ids=Array.from({length:700},(_,i)=>'c'+i);
const rows=ids.slice(1).map((id,i)=>reaction('r'+String(i).padStart(4,'0'),[ids[i]],[id]));
const d=library(ids,rows),before=JSON.stringify(d);
const g=buildSynthesisGraph(d,'c699',{maxReactions:37,maxNodes:100});
assert.equal(g.truncated,true);assert.equal(g.reactionIds.length,37);assert.ok(g.nodes.length<=100);
assertExactEdges(g,d);assert.equal(JSON.stringify(d),before);
const star=library(['target','a','b','c','d','e','small'],[
 reaction('00-too-wide',['a','b','c','d','e'],['target']),
 reaction('01-small',['small'],['target']),
]);
const bounded=buildSynthesisGraph(star,'target',{maxReactions:20,maxNodes:4});
assert.equal(bounded.truncated,true);assert.deepEqual(bounded.reactionIds,['01-small']);
assert.equal(bounded.nodes.length,3);assert.equal(bounded.edges.length,2);assertExactEdges(bounded,star);
assert.ok(!bounded.nodes.some(n=>n.recordId==='00-too-wide'));
assert.ok(!bounded.nodes.some(n=>n.recordId==='a'));
""")
