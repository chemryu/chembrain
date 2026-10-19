"""Run the actual browser handoff planner and private transaction without a DOM."""
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def check_import(body):
    script = f"""
import assert from 'node:assert/strict';
import fs from 'node:fs';
import ts from 'typescript';
const original=fs.readFileSync({json.dumps(str(ROOT/'src/importReview.ts'))},'utf8');
const executableSource=original.replaceAll("'./libraryData'",{json.dumps(repr((ROOT/'src/libraryData.ts').as_uri()))});
const js=ts.transpileModule(executableSource,{{compilerOptions:{{target:ts.ScriptTarget.ES2022,module:ts.ModuleKind.ESNext}}}}).outputText;
const {{prepareImportReview,assertImportBaseline,commitReviewedImport}}=await import('data:text/javascript;base64,'+Buffer.from(js).toString('base64'));
const STORE='chembrain.normalized-library.v1';
const chemical=(id,smiles=null)=>({{id,name:id,kind:'compound',aliases:[],smiles}});
const fixture=()=>({{schema_version:1,papers:[{{id:'p',doi:'10.5555/handoff-fixture',authors:['Fixture author']}}],
 chemicals:[{{...chemical('paper-a'),notes:'Private custom note',aliases:['My alias']}},chemical('paper-b','C=O')],
 solutions:[{{id:'s',solvents:[],solutes:[{{chemical_id:'paper-a',role:'reactant',amount:1,unit:'mmol'}}],concentration:0.1,concentration_unit:'M'}}],
 reactions:[{{id:'r',name:'My edited reaction',reactants:['paper-a'],products:['paper-b'],targets:['paper-b'],yield_percent:42,status:'draft',steps:[{{solution_id:'s',temperature:'20 °C'}}],evidence:[{{paper_id:'p',page:2,locator:'Scheme 1'}}],notes:'My reaction note'}}]}});
function incoming(d){{const x=structuredClone(d);Object.assign(x.chemicals[0],{{smiles:'CCO',formula:'C2H6O',inchikey:'LFQSCWFLJHTTHZ-UHFFFAOYSA-N',molecular_weight:46.07,notes:'Incoming note',aliases:['Incoming alias']}});return x;}}
function storage(raw,fail=''){{const values=new Map([[STORE,raw]]),writes=[];return {{values,writes,
 getItem(k){{if(fail==='backup-readback'&&k.includes('.import-backup.')&&values.has(k))return 'wrong bytes';return values.get(k)??null;}},
 setItem(k,v){{writes.push([k,v]);if((fail==='backup'&&k.includes('.import-backup.'))||(fail==='primary'&&k===STORE))throw new Error('Storage full');values.set(k,v);if(fail==='concurrent-backup'&&k.includes('.import-backup.'))values.set(STORE,raw+' ');}}
}};}}
{body}
"""
    result = subprocess.run(['node', '--experimental-strip-types', '--input-type=module', '-e', script], cwd=ROOT, capture_output=True, text=True, timeout=20)
    assert result.returncode == 0, result.stdout + result.stderr


def test_missing_structure_is_explicit_and_all_other_user_records_are_preserved():
    check_import("""
const d=fixture(),x=incoming(d),before=JSON.stringify(d),source=JSON.stringify(x);
x.chemicals.push(chemical('paper-c','CC'));
x.reactions.push({...x.reactions[0],id:'new-r',name:'New route step',reactants:['paper-b'],products:['paper-c']});
const plan=prepareImportReview(d,x);
assert.deepEqual(plan.conflicts,[]);assert.equal(plan.upgrades.length,1);
assert.deepEqual(plan.upgrades[0].fields,['smiles','inchikey','formula','molecular_weight']);
assert.equal(plan.added.chemicals,1);assert.equal(plan.added.reactions,1);
const row=plan.next.chemicals.find(c=>c.id==='paper-a');
assert.equal(row.smiles,'CCO');assert.equal(row.notes,d.chemicals[0].notes);assert.deepEqual(row.aliases,d.chemicals[0].aliases);
for(const table of ['papers','reactions','solutions'])for(const old of d[table])assert.deepEqual(plan.next[table].find(r=>r.id===old.id),old);
assert.equal(JSON.stringify(d),before);
const invalid=JSON.parse(source);invalid.reactions[0].products=['missing'];assert.throws(()=>prepareImportReview(d,invalid),/participants/);
assert.equal(JSON.stringify(d),before);
""")


def test_protected_identities_and_path_collisions_block_whole_package():
    check_import("""
const d=fixture();
for(const change of [{name:'Another identity'},{kind:'reagent'}]){
 const x=incoming(d);Object.assign(x.chemicals[0],change);const plan=prepareImportReview(d,x);
 assert.ok(plan.conflicts.length);assert.equal(plan.next,null);
}
for(const [field,oldValue,newValue] of [['smiles','CO','CCO'],['inchikey','OLD-KEY','NEW-KEY'],['formula','CH4O','C2H6O'],['molecular_weight',32.04,46.07]]){
 const base=fixture();base.chemicals[0][field]=oldValue;const x=incoming(base);x.chemicals[0][field]=newValue;
 const plan=prepareImportReview(base,x);assert.ok(plan.conflicts.length,field);assert.equal(plan.next,null);
 assert.throws(()=>commitReviewedImport(plan,storage(JSON.stringify(base)),JSON.stringify(base)),/collisions/);
}
const route=incoming(d);route.reactions[0].reactants=['paper-b'];assert.equal(prepareImportReview(d,route).conflicts[0].table,'reaction');
const solution=incoming(d);solution.solutions[0].solutes[0].chemical_id='paper-b';assert.equal(prepareImportReview(d,solution).conflicts[0].table,'solution');
const ambiguous=fixture();ambiguous.chemicals[1].inchikey='KEY';const x=incoming(ambiguous);x.chemicals[0].inchikey='KEY';assert.match(prepareImportReview(ambiguous,x).conflicts[0].reason,/different existing/);
""")


def test_verified_exact_private_backup_precedes_single_primary_save():
    check_import("""
const d=fixture(),raw=JSON.stringify(d,null,3)+'\\n',store=storage(raw),plan=prepareImportReview(d,incoming(d));
const next=commitReviewedImport(plan,store,raw);
assert.equal(store.writes.length,2);assert.ok(store.writes[0][0].includes('.import-backup.'));
assert.equal(store.writes[0][1],raw);assert.equal(store.getItem(store.writes[0][0]),raw);
assert.equal(store.writes[1][0],STORE);assert.deepEqual(JSON.parse(store.getItem(STORE)),next);
assert.equal(next.chemicals[0].notes,'Private custom note');
const repeat=prepareImportReview(next,incoming(d));assert.equal(repeat.upgrades.length,0);assert.equal(repeat.changed,false);
const count=store.writes.length;commitReviewedImport(repeat,store,store.getItem(STORE));assert.equal(store.writes.length,count);
""")


def test_backup_and_storage_failures_do_not_replace_original_primary():
    check_import("""
const d=fixture(),raw=JSON.stringify(d,null,2)+'\\n',plan=prepareImportReview(d,incoming(d));
for(const failure of ['backup','backup-readback','primary']){
 const store=storage(raw,failure);assert.throws(()=>commitReviewedImport(plan,store,raw));
 assert.equal(store.values.get(STORE),raw,failure);
}
const changed=storage(raw);changed.values.set(STORE,raw+' ');assert.throws(()=>commitReviewedImport(plan,changed,raw),/changed/);assert.equal(changed.writes.length,0);
const raced=storage(raw,'concurrent-backup');assert.throws(()=>commitReviewedImport(plan,raced,raw),/changed/);assert.equal(raced.values.get(STORE),raw+' ');assert.ok(!raced.writes.some(([k])=>k===STORE));
const diverged=storage(JSON.stringify({...d,generated_at:'different'}));assert.throws(()=>assertImportBaseline(plan,diverged,diverged.getItem(STORE)),/differs/);
""")


def test_fresh_backup_keeps_incoming_precedence_and_compatible_local_metadata():
    check_import("""
const d=fixture(),x=incoming(d);x.chemicals[0].name='Imported personal name';
const fresh=prepareImportReview(d,x,false);assert.deepEqual(fresh.conflicts,[]);assert.deepEqual(fresh.upgrades,[]);assert.equal(fresh.next.chemicals[0].name,'Imported personal name');
const noLibrary={getItem(){return null;}};assertImportBaseline(fresh,noLibrary,null);
const local=fixture();Object.assign(local.chemicals[0],{formula:'C2H6O',molecular_weight:46.069});
const plan=prepareImportReview(local,incoming(local));assert.deepEqual(plan.conflicts,[]);assert.equal(plan.next.chemicals[0].molecular_weight,46.069);assert.ok(!plan.upgrades[0].fields.includes('molecular_weight'));
""")


def test_alternate_smiles_require_two_graph_preflight_not_forged_matching_metadata():
    check_import("""
const d=fixture();Object.assign(d.chemicals[0],{smiles:'OCC',formula:'C2H6O',inchikey:'LFQSCWFLJHTTHZ-UHFFFAOYSA-N',molecular_weight:46.07});
const x=incoming(d),label='Paper label 17; DOI '+x.papers[0].doi;x.chemicals[0].aliases.push(label);
// Matching supplied fields alone never prove that two actual graphs agree.
assert.ok(prepareImportReview(d,x).conflicts.length);
const proof={currentId:'paper-a',incomingId:'paper-a',currentSmiles:'OCC',incomingSmiles:'CCO',canonicalSmiles:'CCO',inchikey:'LFQSCWFLJHTTHZ-UHFFFAOYSA-N',formula:'C2H6O'};
const checked=prepareImportReview(d,x,true,[proof]);
assert.deepEqual(checked.conflicts,[]);assert.equal(checked.upgrades.length,0);assert.equal(checked.labelAdditions.length,1);
assert.equal(checked.next.chemicals[0].smiles,'OCC');assert.equal(checked.next.chemicals[0].notes,d.chemicals[0].notes);
assert.deepEqual(checked.next.chemicals[0].aliases,['My alias',label]);
const raw=JSON.stringify(d,null,2)+'\\n',store=storage(raw);commitReviewedImport(checked,store,raw);
assert.equal(store.writes.length,2);assert.equal(store.writes[0][1],raw);assert.equal(store.writes[1][0],STORE);
const repeat=prepareImportReview(checked.next,x,true,[proof]);assert.equal(repeat.changed,false);assert.equal(repeat.labelAdditions.length,0);
const count=store.writes.length;commitReviewedImport(repeat,store,store.getItem(STORE));assert.equal(store.writes.length,count);
for(const change of [{currentSmiles:'CCO'},{incomingSmiles:'CO'},{formula:'CH4O'},{inchikey:'FORGED'}])assert.ok(prepareImportReview(d,x,true,[{...proof,...change}]).conflicts.length);
const forged=incoming(d);forged.chemicals[0].smiles='CO';assert.ok(prepareImportReview(d,forged).conflicts.length);
const wrongDoi=structuredClone(x);wrongDoi.chemicals[0].aliases=['Paper label 17; DOI 10.5555/not-in-package'];assert.equal(prepareImportReview(d,wrongDoi,true,[proof]).labelAdditions.length,0);
""")


def test_unknown_same_paper_labels_keep_source_scope_without_claiming_structure():
    check_import("""
const d=fixture(),x=structuredClone(d),label='Paper label 17; DOI '+d.papers[0].doi;x.chemicals[0].aliases.push(label);
const direct=prepareImportReview(d,x);assert.deepEqual(direct.conflicts,[]);assert.equal(direct.upgrades.length,0);assert.equal(direct.labelAdditions.length,1);
assert.equal(direct.next.chemicals[0].smiles,null);assert.deepEqual(direct.next.chemicals[0].aliases,['My alias',label]);
const raw=JSON.stringify(d,null,2),store=storage(raw);commitReviewedImport(direct,store,raw);assert.equal(store.writes.length,2);assert.equal(store.writes[0][1],raw);
// Catalyst/solvent labels are grounded in the solution used by an evidenced step.
const catalyst=fixture();catalyst.chemicals.push({...chemical('unresolved-catalyst'),kind:'catalyst'});catalyst.solutions[0].solutes.push({chemical_id:'unresolved-catalyst',role:'catalyst',amount:null,unit:null});
const catalystIn=structuredClone(catalyst);catalystIn.chemicals[2].aliases.push('Paper label Pd/C; DOI '+d.papers[0].doi);assert.deepEqual(prepareImportReview(catalyst,catalystIn).conflicts,[]);
const targetOnly=fixture();targetOnly.chemicals.push(chemical('target-only'));targetOnly.reactions[0].targets.push('target-only');const targetIn=structuredClone(targetOnly);targetIn.chemicals[2].aliases.push(label);assert.ok(prepareImportReview(targetOnly,targetIn).conflicts.length);
const wrongPaper=structuredClone(x);wrongPaper.papers.push({id:'other',doi:'10.5555/other-paper',authors:[]});wrongPaper.chemicals[0].aliases=['Paper label 17; DOI 10.5555/other-paper'];assert.ok(prepareImportReview(d,wrongPaper).conflicts.length);
""")
