"""Compare the actual bundled inspection graph with Python RDKit, not mock values."""
import base64
import gzip
import json
from pathlib import Path
import subprocess

import pytest
from rdkit import Chem
from rdkit.Chem import Descriptors, rdMolDescriptors

ROOT = Path(__file__).resolve().parents[1]


def test_real_rdkitjs_inspection_preserves_identity_formula_stereo_and_fragments(tmp_path):
    rdkit_js = ROOT / 'node_modules/@rdkit/rdkit/dist/RDKit_minimal.js'
    if not rdkit_js.exists():
        pytest.skip('npm dependencies are not installed')
    wasm = ROOT / 'node_modules/@rdkit/rdkit/dist/RDKit_minimal.wasm'
    encoded = base64.b64encode(gzip.compress(wasm.read_bytes(), mtime=0)).decode()
    compressed_file = tmp_path / 'wasm.base64'
    compressed_file.write_text(encoded)
    script = r"""
import fs from 'node:fs';
import ts from 'typescript';
const root=process.argv[1],output=process.argv[2],factory=process.argv[3],compressed=fs.readFileSync(process.argv[4],'utf8');
for(const file of ['molecularFormula','structureRenderer']){
 let source=fs.readFileSync(root+'/src/'+file+'.ts','utf8');
 source=source.replace(/import createRDKitModule,[^;]+from '@rdkit\/rdkit';/,'import createRDKitModule from '+JSON.stringify(factory)+';')
  .replace("import compressedWasm from 'virtual:chembrain-rdkit-wasm';",'const compressedWasm='+JSON.stringify(compressed)+';')
  .replace("'./molecularFormula'","'./molecularFormula.mjs'");
 fs.writeFileSync(output+'/'+file+'.mjs',ts.transpileModule(source,{compilerOptions:{module:ts.ModuleKind.ESNext,target:ts.ScriptTarget.ES2022}}).outputText);
}
"""
    result = subprocess.run(['node', '--input-type=module', '-e', script, str(ROOT),
                             str(tmp_path), rdkit_js.as_uri(), str(compressed_file)],
                            cwd=ROOT, capture_output=True, text=True, timeout=30)
    assert result.returncode == 0, result.stdout + result.stderr
    cases = ['CCO', 'c1ccccc1', 'C[C@H](O)C(=O)[O-].[Na+]',
             'C[C@@H](O)C(=O)[O-].[Na+]', '[NH4+].[Cl-]', '[NH4+]',
             '[13CH3]CO', '[2H]O[2H]', '[H][H]', '[H]Cl', 'P(=O)(O)(O)O',
             '[Fe+2]', '[AlH4-]']
    exercise = f"""
import assert from 'node:assert/strict';
import {{inspectStructure,renderStructure}} from {json.dumps((tmp_path / 'structureRenderer.mjs').as_uri())};
const cases={json.dumps(cases)},results=[];
for(const smiles of cases)results.push(await inspectStructure(smiles));
for(const bad of ['', 'C1(', '*', 'C'.repeat(3001)])await assert.rejects(()=>inspectStructure(bad));
assert.equal((await renderStructure('C1(')).status,'invalid');
assert.equal((await renderStructure(null)).status,'missing');
process.stdout.write(JSON.stringify(results));
"""
    result = subprocess.run(['node', '--input-type=module', '-e', exercise],
                            cwd=ROOT, capture_output=True, text=True, timeout=60)
    assert result.returncode == 0, result.stdout + result.stderr
    actual = json.loads(result.stdout)
    for smiles, inspected in zip(cases, actual, strict=True):
        mol = Chem.MolFromSmiles(smiles)
        assert mol is not None
        assert inspected['smiles'] == smiles
        assert inspected['canonical_smiles'] == Chem.MolToSmiles(mol, isomericSmiles=True)
        assert inspected['formula'] == rdMolDescriptors.CalcMolFormula(mol), smiles
        assert inspected['inchikey'] == Chem.MolToInchiKey(mol), smiles
        assert abs(inspected['molecular_weight'] - Descriptors.MolWt(mol)) <= 0.0051
        assert inspected['fragments'] == len(Chem.GetMolFrags(mol))
        assert inspected['engine'].startswith('RDKit ')
    assert actual[2]['inchikey'] != actual[3]['inchikey'], 'Opposite stereo lost chemical identity'
