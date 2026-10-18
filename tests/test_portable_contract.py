"""One mutation corpus validates actual processor exports in the browser runtime."""
import copy
import json
from pathlib import Path
import subprocess
import sys

import pytest

from paper_pipeline.__main__ import main
from paper_pipeline.schema import normalize, validate, project_legacy_library

ROOT = Path(__file__).resolve().parents[1]


def package():
    # Deliberately synthetic minimal package; scientific unknowns are explicit.
    return {
        'schema_version': 1,
        'papers': [{'id': 'p', 'doi': '10.1021/fixture', 'authors': []}],
        'chemicals': [{'id': 'c', 'name': 'Ethanol fixture', 'kind': 'compound',
                       'aliases': [], 'smiles': 'CCO'}],
        'solutions': [{'id': 's', 'solvents': ['c'],
                       'solutes': [{'chemical_id': 'c', 'role': 'fixture', 'amount': None, 'unit': None}],
                       'concentration': None, 'concentration_unit': None}],
        'reactions': [{'id': 'r', 'name': 'Fixture', 'status': 'draft',
                       'reactants': ['c'], 'products': ['c'], 'targets': [],
                       'steps': [{'solution_id': 's'}], 'yield_percent': None,
                       'evidence': [{'paper_id': 'p', 'page': 1, 'locator': 'fixture'}]}],
    }


def corpus():
    cases = [('valid', package(), True)]

    def add(label, path, value=None, *, remove=False, expected=False):
        data = package()
        parent = data
        for component in path[:-1]:
            parent = parent[component]
        if remove:
            del parent[path[-1]]
        else:
            parent[path[-1]] = value
        cases.append((label, data, expected))

    required = [
        ('papers', 0, 'doi'), ('papers', 0, 'authors'),
        ('chemicals', 0, 'name'), ('chemicals', 0, 'kind'), ('chemicals', 0, 'aliases'),
        ('solutions', 0, 'solvents'), ('solutions', 0, 'solutes'),
        ('solutions', 0, 'concentration'), ('solutions', 0, 'concentration_unit'),
        ('solutions', 0, 'solutes', 0, 'chemical_id'), ('solutions', 0, 'solutes', 0, 'role'),
        ('solutions', 0, 'solutes', 0, 'amount'), ('solutions', 0, 'solutes', 0, 'unit'),
        ('reactions', 0, 'name'), ('reactions', 0, 'status'), ('reactions', 0, 'reactants'),
        ('reactions', 0, 'products'), ('reactions', 0, 'targets'), ('reactions', 0, 'steps'),
        ('reactions', 0, 'yield_percent'), ('reactions', 0, 'evidence'),
        ('reactions', 0, 'steps', 0, 'solution_id'),
        ('reactions', 0, 'evidence', 0, 'paper_id'), ('reactions', 0, 'evidence', 0, 'page'),
        ('reactions', 0, 'evidence', 0, 'locator'),
    ]
    nullable = {'amount', 'unit', 'concentration', 'concentration_unit', 'yield_percent'}
    for path in required:
        name = '.'.join(map(str, path))
        add(name + ' missing', path, remove=True)
        add(name + ' null', path, expected=path[-1] in nullable)
        add(name + ' object', path, {})
        add(name + ' bool', path, True)
    for table in ('papers', 'chemicals', 'solutions', 'reactions'):
        for value in (None, {}, 'bad', [None], [[]], [True]):
            add(table + ' invalid ' + repr(value), (table,), value)
    for path in [('reactions', 0, 'steps', 0), ('reactions', 0, 'evidence', 0),
                 ('solutions', 0, 'solutes', 0)]:
        for value in (None, [], True, 'bad', {}):
            add(str(path) + repr(value), path, value)
    for value in (True, False, 1499, 3001, 2000.5, '2000', {}, []):
        add('invalid year ' + repr(value), ('papers', 0, 'year'), value)
    for value in (None, 1500, 2026, 3000, 2000.0):
        add('removed year ' + repr(value), ('papers', 0, 'year'), value)
    for field in ('name', 'notes', 'formula', 'smiles', 'inchikey'):
        add('chemical text object ' + field, ('chemicals', 0, field), {})
    for field in ('temperature', 'time', 'notes'):
        add('step text object ' + field, ('reactions', 0, 'steps', 0, field), {})
        add('step text null ' + field, ('reactions', 0, 'steps', 0, field), None, expected=True)
    for value in (True, -1, '2', {}, []):
        add('invalid molecular weight ' + repr(value), ('chemicals', 0, 'molecular_weight'), value)
    for value in (None, 0, 46.07):
        add('valid molecular weight ' + repr(value), ('chemicals', 0, 'molecular_weight'), value, expected=True)
    for value in (True, {}, [], 1):
        add('generated_at invalid ' + repr(value), ('generated_at',), value)
    add('generated_at unknown', ('generated_at',), None, expected=True)
    add('non-ASCII DOI registrant digits', ('papers', 0, 'doi'), '10.１２３４/fixture')
    add('ECMAScript trim BOM', ('papers', 0, 'doi'), '\ufeff10.1021/FIXTURE\ufeff', expected=True)
    add('DOI-prefix non-JS whitespace', ('papers', 0, 'doi'), 'doi:\u008510.1021/fixture')
    add('untrimmed non-JS whitespace', ('papers', 0, 'doi'), '\u008510.1021/fixture')
    add('canonical DOI', ('papers', 0, 'doi'), 'https://doi.org/10.1021/FIXTURE', expected=True)
    add('Unicode bounded', ('chemicals', 0, 'notes'), '🧪' * 1500, expected=True)
    add('Unicode over bound', ('chemicals', 0, 'notes'), '🧪' * 1501)
    add('unknown chemical reference', ('solutions', 0, 'solvents'), ['unknown'])
    add('forbidden nested body', ('papers', 0, 'metadata'), {'full_text': 'private'})
    add('optional notes null', ('chemicals', 0, 'notes'), None, expected=True)
    for field in ('title', 'journal', 'notes'):
        add('removed paper ' + field, ('papers', 0, field), 'legacy metadata')
    for path in [('papers', 0), ('chemicals', 0), ('solutions', 0), ('reactions', 0),
                 ('solutions', 0, 'solutes', 0), ('reactions', 0, 'steps', 0),
                 ('reactions', 0, 'evidence', 0)]:
        for field in ('abstract', 'body', 'content', 'attachment', 'custom'):
            for value in ('private', {'disguised': 'document'}):
                add(str(path) + field + str(value), (*path, field), value)
    return cases


def test_shared_corpus_python_export_is_browser_importable(tmp_path, monkeypatch):
    """Compare the SAME input cases and actual CLI-exported bytes, not mirror tests."""
    browser_cases = []
    out = tmp_path / 'library.json'
    curated = tmp_path / 'curated.json'
    prior = b'previous user export must survive failure\n'
    for label, data, expected in corpus():
        try:
            validate(data)
            python_accepts = True
        except ValueError:
            python_accepts = False
        assert python_accepts == expected, label
        curated.write_text(json.dumps(data), encoding='utf-8')
        out.write_bytes(prior)
        monkeypatch.setattr(sys, 'argv', ['paper_pipeline', 'export', '--curated', str(curated), '--out', str(out)])
        try:
            assert main() == 0
            exported = json.loads(out.read_text())
        except ValueError:
            assert not expected, label
            assert out.read_bytes() == prior, label
            exported = None
        else:
            assert expected, label
            assert validate(exported)
        browser_cases.append({'label': label, 'data': data, 'expected': expected, 'exported': exported})
    fixture = tmp_path / 'corpus.json'
    fixture.write_text(json.dumps(browser_cases), encoding='utf-8')
    script = r"""
import fs from 'node:fs';
import assert from 'node:assert/strict';
import {validateLibrary,mergeLibrary,emptyLibrary} from MODULE;
const cases=JSON.parse(fs.readFileSync(process.argv[1],'utf8'));
for(const {label,data,expected,exported} of cases){
 let accepted=true;try{validateLibrary(data);}catch{accepted=false;}
 assert.equal(accepted,expected,label);
 if(exported!==null){assert.doesNotThrow(()=>validateLibrary(exported),'actual Python export: '+label);assert.doesNotThrow(()=>mergeLibrary(emptyLibrary,exported),'browser import merge: '+label);}
}
// Nonfinite values cannot be encoded by JSON, so inject the same runtime corpus
// after parsing. Reject them even when hidden in otherwise optional metadata.
for(const v of [NaN,Infinity,-Infinity]){
 for(const path of [['chemicals',0,'molecular_weight'],['papers',0,'year'],['solutions',0,'concentration'],['papers',0,'extra']]){
  const d=structuredClone(cases[0].data);let row=d;for(const p of path.slice(0,-1))row=row[p];row[path.at(-1)]=v;
  assert.throws(()=>validateLibrary(d),'nonfinite '+path.join('.'));
 }
}
console.log('PORTABLE_CONTRACT_PASS '+cases.length+' shared cases; actual Python exports validated');
""".replace('MODULE', json.dumps((ROOT / 'src/libraryData.ts').as_uri()))
    result = subprocess.run(['node', '--experimental-strip-types', '--input-type=module', '-e', script, str(fixture)], capture_output=True, text=True, timeout=30)
    assert result.returncode == 0, result.stdout + result.stderr
    assert 'PORTABLE_CONTRACT_PASS' in result.stdout


@pytest.mark.parametrize('value', [float('nan'), float('inf'), float('-inf'), 10 ** 1000])
def test_non_json_numbers_raise_value_error(value):
    for path in [('chemicals', 0, 'molecular_weight'), ('papers', 0, 'year'), ('papers', 0, 'extra')]:
        data = package(); row = data
        for part in path[:-1]:
            row = row[part]
        row[path[-1]] = value
        with pytest.raises(ValueError):
            validate(data)
        with pytest.raises(ValueError):
            normalize(data)


def test_validation_does_not_mutate_input_and_normalization_preserves_evidence():
    data = package()
    data['papers'][0]['doi'] = 'https://doi.org/10.1021/FIXTURE'
    duplicate = copy.deepcopy(data['papers'][0]); duplicate['id'] = 'p2'
    data['papers'].append(duplicate)
    data['reactions'][0]['evidence'].append({'paper_id': 'p2', 'page': 2, 'locator': 'second source'})
    original = copy.deepcopy(data)
    normalized = normalize(data)
    assert data == original
    assert len(normalized['papers']) == 1
    assert normalized['papers'][0]['doi'] == '10.1021/fixture'
    assert [e['paper_id'] for e in normalized['reactions'][0]['evidence']] == ['p', 'p']
    assert len(normalized['reactions'][0]['evidence']) == 2


def test_explicit_legacy_projection_is_narrow_and_preserves_chemistry(tmp_path):
    legacy = package()
    legacy['papers'][0].update(title='Old title', journal='Old journal', year=2005,
                               notes='Private legacy metadata')
    original = copy.deepcopy(legacy)
    projected = project_legacy_library(legacy)
    assert legacy == original
    assert projected['papers'] == package()['papers']
    assert {k:v for k,v in projected.items() if k != 'papers'} == {k:v for k,v in legacy.items() if k != 'papers'}
    with pytest.raises(ValueError): validate(legacy)
    with pytest.raises(ValueError): normalize(legacy)
    rejects = []
    for path in [('papers', 0), ('chemicals', 0), ('solutions', 0), ('reactions', 0),
                 ('solutions', 0, 'solutes', 0), ('reactions', 0, 'steps', 0),
                 ('reactions', 0, 'evidence', 0)]:
        bad = copy.deepcopy(legacy); row = bad
        for key in path: row = row[key]
        row['abstract'] = 'Must not be laundered by migration'
        with pytest.raises(ValueError): project_legacy_library(bad)
        rejects.append(bad)
    for field,value in [('title', None), ('title', ''), ('journal', {}), ('year', True),
                        ('year', 3001), ('notes', {}), ('notes', 'x'*3001)]:
        bad=copy.deepcopy(legacy);bad['papers'][0][field]=value
        with pytest.raises(ValueError): project_legacy_library(bad)
        rejects.append(bad)
    fixture=tmp_path/'legacy.json'
    fixture.write_text(json.dumps({'legacy': legacy, 'projected': projected, 'rejects': rejects}))
    script = r"""
import fs from 'node:fs';import assert from 'node:assert/strict';
import {projectLegacyLibrary,validateLibrary} from MODULE;
const {legacy,projected,rejects}=JSON.parse(fs.readFileSync(process.argv[1],'utf8'));
const raw=JSON.stringify(legacy);
assert.deepEqual(projectLegacyLibrary(legacy),projected);
assert.equal(JSON.stringify(legacy),raw);
assert.throws(()=>validateLibrary(legacy));
assert.deepEqual(projectLegacyLibrary(projected),projected);
for(const bad of rejects)assert.throws(()=>projectLegacyLibrary(bad));
""".replace('MODULE', json.dumps((ROOT / 'src/libraryData.ts').as_uri()))
    result=subprocess.run(['node','--experimental-strip-types','--input-type=module','-e',script,str(fixture)],capture_output=True,text=True,timeout=30)
    assert result.returncode == 0, result.stdout+result.stderr
