"""Run the actual offline workbench domain in Node, including strict export gates."""
import json
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def model_modules(tmp_path_factory):
    destination = tmp_path_factory.mktemp("paper-workbench-js")
    script = r"""
import fs from 'node:fs';
import ts from 'typescript';
const root=process.argv[1],destination=process.argv[2];
for(const name of ['libraryData','paperWorkbenchModel']){
 const source=fs.readFileSync(root+'/src/'+name+'.ts','utf8');
 const code=ts.transpileModule(source,{compilerOptions:{module:ts.ModuleKind.ESNext,target:ts.ScriptTarget.ES2022}}).outputText.replaceAll("'./libraryData'","'./libraryData.mjs'");
 fs.writeFileSync(destination+'/'+name+'.mjs',code);
}
"""
    result = subprocess.run(
        ["node", "--input-type=module", "-e", script, str(ROOT), str(destination)],
        cwd=ROOT, text=True, capture_output=True, timeout=20,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    return destination


def run_model(model_modules, body):
    script = f"""
import assert from 'node:assert/strict';
import fs from 'node:fs';
import crypto from 'node:crypto';
import * as m from {json.dumps((model_modules / 'paperWorkbenchModel.mjs').as_uri())};
import {{validateLibrary}} from {json.dumps((model_modules / 'libraryData.mjs').as_uri())};
const sources=[{{document:'main',page:3,locator:'Scheme 1, compound 1'}}];
const descriptors={{
 CCO:{{smiles:'CCO',canonical_smiles:'CCO',formula:'C2H6O',inchikey:'LFQSCWFLJHTTHZ-UHFFFAOYSA-N',molecular_weight:46.069,engine:'RDKit 2026.9.1',fragments:1,unassigned_stereocenters:0}},
 'C=O':{{smiles:'C=O',canonical_smiles:'C=O',formula:'CH2O',inchikey:'WSFSSNUMVMOOMR-UHFFFAOYSA-N',molecular_weight:30.026,engine:'RDKit 2026.9.1'}},
 O:{{smiles:'O',canonical_smiles:'O',formula:'H2O',inchikey:'XLYOFNOQVPJJNP-UHFFFAOYSA-N',molecular_weight:18.015,engine:'RDKit 2026.9.1'}}
}};
function draft(){{
 let p=m.createProject('HTTPS://doi.org/10.1000/Fixture',['A. Author']);
 p=m.addChemical(p,{{label:'1',name:'Ethanol',kind:'compound',smiles:'CCO',sources}});
 p=m.addChemical(p,{{label:'2',name:'Formaldehyde',kind:'compound',smiles:'C=O',sources}});
 p=m.addChemical(p,{{label:'water',name:'Water',kind:'solvent',smiles:'O',sources}});
 const [a,b,w]=p.chemicals.map(c=>c.id);
 p=m.addSolution(p,{{label:'stage 1',solvents:[w],solutes:[{{chemical_id:a,role:'substrate',amount:1,unit:'mmol'}}],sources}});
 p=m.addReaction(p,{{label:'1 to 2',name:'Source-recorded fixture transformation',reactants:[a],products:[b],targets:[b],yield_percent:78,steps:[{{solution_id:p.solutions[0].id,temperature:'20 C',time:'1 h'}}],evidence:sources}});
 return p;
}}
function checked(){{
 let p=draft();for(const c of p.chemicals)p=m.checkChemical(p,c.id,descriptors[c.smiles],true);
 p=m.checkSolution(p,p.solutions[0].id,true);p=m.checkReaction(p,p.reactions[0].id,true);return p;
}}
{body}
"""
    result = subprocess.run(
        ["node", "--input-type=module", "-e", script], cwd=ROOT,
        text=True, capture_output=True, timeout=20,
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_stable_doi_scoped_ids_and_qualified_labels(model_modules):
    run_model(model_modules, """
const hash=crypto.createHash('sha256').update('10.1000/fixture\\0'+'1').digest('hex');
assert.equal(m.stableRecordId('chemical','https://doi.org/10.1000/FIXTURE',' 1 '),'pw-chemical-'+hash);
assert.notEqual(m.stableRecordId('chemical','10.1000/other','1'),m.stableRecordId('chemical','10.1000/fixture','1'));
assert.notEqual(m.stableRecordId('chemical','10.1000/fixture','main:1'),m.stableRecordId('chemical','10.1000/fixture','SI:1'));
let p=draft();assert.equal(p.paper.doi,'10.1000/fixture');
assert.throws(()=>m.addChemical(p,{label:'1',name:'Conflicting label',kind:'compound'}),/unique/);
assert.throws(()=>m.validateProject({...p,chemicals:[{...p.chemicals[0],id:'arbitrary-id'}]}),/identity/);
const old=p.chemicals[0].id;p=m.updateChemical(p,old,{label:'main:1'});const next=p.chemicals[0].id;
assert.notEqual(old,next);assert.deepEqual(p.reactions[0].reactants,[next]);assert.equal(p.solutions[0].solutes[0].chemical_id,next);
""")


def test_strict_checked_export_and_no_private_field_leak(model_modules):
    run_model(model_modules, """
const p=checked(),out=await m.buildExport(p);assert.deepEqual(m.blockers(p),[]);validateLibrary(out);
assert.equal(out.reactions[0].status,'reviewed');assert.equal(out.chemicals[0].smiles,'CCO');
assert.equal(out.chemicals[0].formula,'C2H6O');assert.equal(out.chemicals[0].inchikey,descriptors.CCO.inchikey);
assert.ok(out.chemicals[0].aliases.includes('Paper label 1; DOI 10.1000/fixture'));
assert.equal(out.reactions[0].evidence[0].locator,'Main article; PDF page 3; Scheme 1, compound 1');
const keys=new Set();function walk(x){if(Array.isArray(x))x.forEach(walk);else if(x&&typeof x==='object')for(const [k,v] of Object.entries(x)){keys.add(k);walk(v);}}walk(out);
for(const k of ['project_schema','baseline','checked','signature','inspection','unknown_reason','sources','canonical_smiles','engine','document'])assert.ok(!keys.has(k),'leaked '+k);
let q=m.addChemical(p,{label:'draft',name:'Unverified draft',kind:'compound',sources});
assert.equal((await m.buildExport(q)).chemicals.length,3,'unapproved drafts must stay behind');
q=m.updateReaction(p,p.reactions[0].id,{evidence:[{document:'supporting',page:8,locator:'Procedure S2'}]});
assert.ok(!q.reactions[0].checked);assert.equal(p.reactions[0].checked.source_checked,true,'immutable input');
""")


def test_source_structure_and_foreign_key_gates(model_modules):
    run_model(model_modules, """
let p=draft(),id=p.chemicals[0].id;
assert.throws(()=>m.checkChemical(p,id,descriptors.CCO,false),/source/);
assert.throws(()=>m.checkChemical(p,id,descriptors.O,true),/stale/);
assert.throws(()=>m.checkChemical(p,id,null,true),/Inspect/);
assert.throws(()=>m.checkSolution(p,p.solutions[0].id,true),/every/);
assert.throws(()=>m.checkReaction(p,p.reactions[0].id,true),/every/);
assert.throws(()=>m.updateChemical(p,id,{sources:[{document:'main',page:0,locator:'x'}]}),/positive/);
assert.throws(()=>m.updateReaction(p,p.reactions[0].id,{reactants:['not-present']}),/participants/);
assert.throws(()=>m.updateReaction(p,p.reactions[0].id,{steps:[{solution_id:'missing'}]}),/stage/);
assert.throws(()=>m.updateSolution(p,p.solutions[0].id,{solutes:[{chemical_id:id,role:'substrate',amount:-1,unit:'mmol'}]}),/solution/);
p=m.updateChemical(p,id,{smiles:null});assert.throws(()=>m.checkChemical(p,id,null,true),/compound/);
p=m.addChemical(p,{label:'unknown catalyst',name:'Reported catalyst mixture',kind:'catalyst',sources});const catalyst=p.chemicals.at(-1).id;
assert.throws(()=>m.checkChemical(p,catalyst,null,true),/Explain/);
p=m.updateChemical(p,catalyst,{unknown_reason:'Composition is not specified in this source'});p=m.checkChemical(p,catalyst,null,true);
const out=await m.buildExport(p);assert.equal(out.chemicals.length,1);assert.equal(out.chemicals[0].smiles,null);
""")


def test_any_meaningful_edit_invalidates_checks_and_dependencies(model_modules):
    run_model(model_modules, """
const p=checked(),id=p.chemicals[0].id;
for(const patch of [{name:'Corrected label'},{notes:'Source correction'},{aliases:['new alias']},{sources:[{document:'supporting',page:4,locator:'S4'}]},{smiles:'C[C@H](O)Cl'},{formula:'wrong'}]){
 const q=m.updateChemical(p,id,patch);assert.ok(!q.chemicals[0].checked);assert.ok(!q.solutions[0].checked);assert.ok(!q.reactions[0].checked);
}
let q=m.updateChemical(p,id,{name:p.chemicals[0].name});assert.ok(q.chemicals[0].checked,'a no-op retains check');
q=structuredClone(p);q.chemicals[0].smiles='CC';await assert.rejects(()=>m.buildExport(q),/stale/);
q=structuredClone(p);q.solutions[0].concentration=0.5;await assert.rejects(()=>m.buildExport(q),/stale/);
q=structuredClone(p);q.reactions[0].yield_percent=90;await assert.rejects(()=>m.buildExport(q),/stale/);
q=structuredClone(p);q.paper.authors=['Different author'];await assert.rejects(()=>m.buildExport(q),/stale/);
q=m.updatePaper(p,{authors:['Different author']});assert.ok(q.chemicals.every(c=>!c.checked));assert.ok(!q.reactions[0].checked);
assert.throws(()=>m.removeChemical(p,id),/first/);assert.throws(()=>m.removeSolution(p,p.solutions[0].id),/first/);
q=m.removeReaction(p,p.reactions[0].id);q=m.removeSolution(q,q.solutions[0].id);q=m.removeChemical(q,id);assert.equal(q.chemicals.length,2);
""")


def test_private_backup_validation_rejects_unrecognized_data(model_modules):
    run_model(model_modules, """
const p=checked(),raw=JSON.stringify(p);assert.deepEqual(m.validateProject(JSON.parse(raw)),p);
for(const field of ['pdf','text','pages','quote','svg','image','base64']){
 assert.throws(()=>m.validateProject({...p,[field]:'private bytes'}),/project/);
 const q=structuredClone(p);q.chemicals[0][field]='private bytes';assert.throws(()=>m.validateProject(q),/unique/);
}
assert.throws(()=>m.validateProject({...p,baseline:{schema_version:1,papers:[],chemicals:[],solutions:[],reactions:[]}}),/baseline/);
assert.throws(()=>m.validateProject({...p,chemicals:[...p.chemicals,p.chemicals[0]]}),/unique/);
const q=structuredClone(p);q.chemicals[0].checked.inspection.smiles='O';await assert.rejects(()=>m.buildExport(q),/stale/);
""")


def test_existing_example_draft_preserves_ids_without_auto_approval(model_modules):
    run_model(model_modules, f"""
const library=JSON.parse(fs.readFileSync({json.dumps(str(ROOT / 'public/library.json'))},'utf8'));
for(const paper of library.papers){{
 const p=m.importLibraryDraft(library,paper.id),expected=library.reactions.filter(r=>r.evidence.some(e=>e.paper_id===paper.id));
 assert.deepEqual(p.reactions.map(r=>r.id),expected.map(r=>r.id));assert.ok(p.reactions.every(r=>!r.checked));assert.ok(p.chemicals.every(c=>!c.checked));
 for(const r of p.reactions){{for(const id of [...r.reactants,...r.products,...r.targets])assert.ok(p.chemicals.some(c=>c.id===id));}}
 const c=p.chemicals[0],q=m.updateChemical(p,c.id,{{name:c.name+' corrected'}});assert.equal(q.chemicals[0].id,c.id,'imported IDs must remain correctable in the main library');
 await assert.rejects(()=>m.buildExport(p),/No checked/);
}}
assert.throws(()=>m.importLibraryDraft(library,'missing'),/Choose a paper/);
""")


def test_stereochemical_salt_fragments_and_multistage_route_survive_exactly(model_modules):
    from rdkit import Chem
    from rdkit.Chem import Descriptors, rdMolDescriptors

    raw = "C[C@H](O)C(=O)[O-].[Na+]"
    molecule = Chem.MolFromSmiles(raw)
    inspection = {
        "smiles": raw,
        "canonical_smiles": Chem.MolToSmiles(molecule, isomericSmiles=True),
        "formula": rdMolDescriptors.CalcMolFormula(molecule),
        "inchikey": Chem.MolToInchiKey(molecule),
        "molecular_weight": Descriptors.MolWt(molecule),
        "engine": "RDKit 2026.9.1",
        "fragments": len(Chem.GetMolFrags(molecule)),
        "unassigned_stereocenters": 0,
    }
    run_model(model_modules, f"""
let p=checked(),id=p.chemicals[0].id;
const descriptor={json.dumps(inspection)};
p=m.updateChemical(p,id,{{smiles:descriptor.smiles}});p=m.checkChemical(p,id,descriptor,true);
p=m.checkSolution(p,p.solutions[0].id,true);
const r=p.reactions[0],solution=p.solutions[0].id;
p=m.updateReaction(p,r.id,{{steps:[{{solution_id:solution,temperature:'-78 C',time:'10 min'}},{{solution_id:solution,temperature:'20 C',time:'2 h'}}],evidence:[...sources,{{document:'supporting',page:12,locator:'Compound 1 characterization'}}]}});
p=m.checkReaction(p,r.id,true);const out=await m.buildExport(p);
assert.equal(out.chemicals[0].smiles,descriptor.smiles,'preserve source stereo and salt fragments, not just a canonical parent');
assert.equal(out.chemicals[0].formula,descriptor.formula);assert.equal(out.chemicals[0].inchikey,descriptor.inchikey);
assert.deepEqual(out.reactions[0].reactants,[id]);assert.deepEqual(out.reactions[0].products,[p.chemicals[1].id]);
assert.equal(out.reactions.length,1,'no extra reaction inferred from two condition stages');
assert.equal(out.reactions[0].steps.length,2);assert.equal(out.reactions[0].steps[0].temperature,'-78 C');
assert.equal(out.reactions[0].evidence[1].locator,'Supporting information; PDF page 12; Compound 1 characterization');
""")
