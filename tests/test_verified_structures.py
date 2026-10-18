"""Reference identity, stereo integrity and reproducible chemistry-only seed output."""
import copy
import json
import subprocess
import sys
from pathlib import Path

import pytest
from rdkit import Chem

from scripts.build_total_synthesis import load_verified_structures

ROOT = Path(__file__).resolve().parents[1]
REFERENCE = ROOT / 'examples/verified-structures.json'


def test_verified_parents_have_explicit_identity_and_complete_stereochemistry():
    structures = load_verified_structures()
    expected = {
        'paclitaxel': ('C47H51NO14', 'RCINICONZNJXQF-MZXODVADSA-N', 11),
        'doxycycline': ('C22H24N2O8', 'JBIWCJUYHHGXTC-AKNGSSGZSA-N', 6),
    }
    package = json.loads(REFERENCE.read_text())
    source = package['source']
    assert source['git_commit'] in source['url']
    assert source['sha256'] == '07634c2891a950829204d633a0f8098f9cd9e48c9e0cd888cabdb756e75507e8'
    assert source['observed_fields'] == ['source_id', 'source_name', 'source_smiles']
    assert 'inchikey' in package['computed_with']['fields']
    for identifier, (formula, key, stereo_count) in expected.items():
        record = structures[identifier]
        assert (record['formula'], record['inchikey'], record['assigned_stereocenters']) == (formula, key, stereo_count)
        mol = Chem.MolFromSmiles(record['canonical_isomeric_smiles'])
        assert mol is not None
        assert len(Chem.GetMolFrags(mol)) == 1 and Chem.GetFormalCharge(mol) == 0
        assert all(label != '?' for _, label in Chem.FindMolChiralCenters(mol, includeUnassigned=True))
    assert 'Not the hydrochloride/hyclate isolate' in structures['doxycycline']['representation']


@pytest.mark.parametrize('mutation', ['inverted_stereo', 'missing_stereo', 'wrong_formula', 'wrong_key', 'salt_fragment'])
def test_reference_corruption_is_rejected_before_diagrams_are_generated(tmp_path, mutation):
    package = copy.deepcopy(json.loads(REFERENCE.read_text()))
    record = package['structures'][0]
    if mutation == 'inverted_stereo':
        record['source_smiles'] = record['source_smiles'].replace('[C@H]', '[C@@H]', 1)
    elif mutation == 'missing_stereo':
        record['source_smiles'] = record['source_smiles'].replace('@', '')
    elif mutation == 'wrong_formula':
        record['formula'] = 'C47H50NO14'
    elif mutation == 'wrong_key':
        record['inchikey'] = package['structures'][1]['inchikey']
    else:
        record['source_smiles'] += '.Cl'
    path = tmp_path / 'reference.json'
    path.write_text(json.dumps(package))
    with pytest.raises(ValueError, match='Reference structure checks do not match'):
        load_verified_structures(path)


def test_generator_is_reproducible_without_inventing_intermediates(tmp_path):
    def generate():
        subprocess.run([sys.executable, str(ROOT / 'scripts/build_total_synthesis.py')], cwd=tmp_path, check=True, capture_output=True, text=True)
        return {str(p.relative_to(tmp_path)): p.read_bytes() for p in tmp_path.rglob('*') if p.is_file()}

    (tmp_path / 'examples').mkdir()
    first = generate()
    assert generate() == first
    library = json.loads(first['public/library.json'])
    assert library == json.loads(first['examples/total-synthesis.json'])
    checked_in = json.loads((ROOT / 'public/library.json').read_text())
    assert library == checked_in
    assert len(library['reactions']) == 12 and len(library['chemicals']) == 49
    intermediates = [record for record in library['chemicals'] if record['id'].startswith(('holton-', 'baran-', 'charest-'))]
    assert len(intermediates) == 22
    assert all(record['smiles'] is None for record in intermediates)
    for identifier in ['paclitaxel', 'doxycycline']:
        record = next(c for c in library['chemicals'] if c['id'] == identifier)
        assert record['smiles'] and record['inchikey']
        svg = first[f'public/structures/{identifier}.svg'].decode()
        assert '<svg' in svg and 'class=\'bond-' in svg
        assert '<image' not in svg and 'data:image' not in svg and '%PDF-' not in svg
