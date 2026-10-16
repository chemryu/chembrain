import io
import json
import zipfile
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from server.app import create_app
from server.store import Store
from server.literature import translate_known_records


def test_doi_reference_creation_and_citation_validation(tmp_path):
    client = TestClient(create_app(tmp_path, demo=False))
    reference = client.post('/api/references', json={'title': 'Example paper', 'doi': 'https://doi.org/10.1000/example', 'document_role': 'main'})
    assert reference.status_code == 201
    source = reference.json()
    assert source['doi'] == '10.1000/example' and source['kind'] == 'reference'
    assert 'pages' not in source
    assert client.post('/api/references', json={'title': 'Duplicate', 'doi': '10.1000/example', 'document_role': 'main'}).status_code == 409
    assert client.post('/api/references', json={'title': 'Invalid', 'doi': 'javascript:alert(1)'}).status_code == 422
    a = client.post('/api/molecules', json={'name': 'Methanol', 'smiles': 'CO'}).json()
    b = client.post('/api/molecules', json={'name': 'Formaldehyde', 'smiles': 'C=O'}).json()
    evidence = {'source_id': source['id'], 'page': 5, 'citation_only': True, 'locator': 'SI, procedure A'}
    body = {'name': 'Citation-backed oxidation', 'reactants': [a['id']], 'products': [b['id']], 'status': 'reviewed', 'evidence': [evidence]}
    assert client.post('/api/reactions', json=body).status_code == 201
    evidence['locator'] = ''
    assert client.post('/api/reactions', json=body).status_code == 422
    evidence.update(locator='SI', citation_only=False, quote='Cannot claim a text match for a DOI-only reference.')
    assert client.post('/api/reactions', json=body).status_code == 422
    assert client.get(f"/api/sources/{source['id']}/file").status_code == 404


def test_desktop_starter_is_pdf_free_and_keeps_conflicts_and_user_changes(tmp_path, monkeypatch):
    monkeypatch.setenv('CHEMBRAIN_SEED_LITERATURE', '1')
    app = create_app(tmp_path, demo=False)
    client = TestClient(app)
    workspace = client.get('/api/workspace').json()
    assert len(workspace['molecules']) == 14 and len(workspace['reactions']) == 6
    assert len(workspace['sources']) == 6
    assert sum(r['status'] == 'draft' for r in workspace['reactions']) == 2
    assert all(s['kind'] == 'reference' and s['doi'] for s in workspace['sources'])
    assert all(not app.state.store.get('source', s['id'])['pages'] for s in workspace['sources'])
    assert not list((tmp_path / 'uploads').iterdir())
    horn = next(r for r in workspace['reactions'] if r['id'].endswith('horn-compound6'))
    assert horn['conditions']['Solvent'].startswith('MeCN')
    assert 'Current density' not in horn['conditions']
    horn['notes'] = 'User correction survives updates.'
    assert client.put('/api/reactions/' + horn['id'], json=horn).status_code == 200
    restarted = TestClient(create_app(tmp_path, demo=False)).get('/api/workspace').json()
    assert next(r for r in restarted['reactions'] if r['id'] == horn['id'])['notes'] == horn['notes']


def test_export_omits_full_text_and_quotes_but_keeps_doi_and_locators(tmp_path):
    app = create_app(tmp_path, demo=False)
    client = TestClient(app)
    source = client.post('/api/sources', files={'file': ('private.md', b'Full document sentinel. A short reaction excerpt.', 'text/markdown')}).json()
    client.put('/api/sources/' + source['id'] + '/metadata', json={'title': 'Private original', 'doi': '10.1000/private'})
    with zipfile.ZipFile(io.BytesIO(client.get('/api/export').content)) as archive:
        text = '\n'.join(archive.read(name).decode() for name in archive.namelist())
        assert 'https://doi.org/10.1000/private' in text
        assert 'Full document sentinel' not in text and 'A short reaction excerpt' not in text
    assert app.state.store.get('source', source['id'])['pages'][0]['text'].startswith('Full document sentinel')


def test_legacy_translation_preserves_custom_edits(tmp_path):
    store = Store(tmp_path)
    store.put('reaction', {'id': 'custom', 'name': 'My own Korean title', 'conditions': {'용매': 'water'}, 'notes': 'Edited notes'})
    translation_path = Path(__file__).resolve().parent.parent / 'examples/english-translations.json'
    translate_known_records(store, translation_path)
    record = store.get('reaction', 'custom')
    assert record['name'] == 'My own Korean title' and record['notes'] == 'Edited notes'
    assert record['conditions'] == {'Solvent': 'water'}


@pytest.mark.parametrize('kind', ['reference', 'upload'])
@pytest.mark.parametrize('status', ['reviewed', 'draft'])
def test_cited_doi_cannot_be_removed_or_break_saved_reactions(tmp_path, kind, status):
    client = TestClient(create_app(tmp_path, demo=False))
    metadata = {'title': 'Cited fixture', 'doi': '10.1000/preserved', 'document_role': 'main'}
    if kind == 'reference':
        source = client.post('/api/references', json=metadata).json()
    else:
        source = client.post('/api/sources', files={'file': ('original.txt', b'Original source must survive metadata edits.')}).json()
        assert client.put(f"/api/sources/{source['id']}/metadata", json=metadata).status_code == 200
    first = client.post('/api/molecules', json={'name': 'Methanol', 'smiles': 'CO'}).json()
    second = client.post('/api/molecules', json={'name': 'Formaldehyde', 'smiles': 'C=O'}).json()
    body = {'name': 'Preserved citation', 'reactants': [first['id']], 'products': [second['id']], 'status': status,
            'evidence': [{'source_id': source['id'], 'page': 1, 'locator': 'Procedure A', 'citation_only': True}]}
    created = client.post('/api/reactions', json=body)
    assert created.status_code == 201
    reaction_id = created.json()['id']
    params = {'target': second['id'], 'include_drafts': True}
    before = client.get('/api/workspace').json()
    routes = client.get('/api/routes', params=params).json()
    assert routes['routes']
    for change in [{'doi': ''}, {'doi': '  \t'}, {}]:
        attempt = {**metadata, 'notes': 'This rejected note must not be saved.'}
        attempt.pop('doi')
        response = client.put(f"/api/sources/{source['id']}/metadata", json={**attempt, **change})
        assert response.status_code == 422
        assert 'A DOI is required' in response.json()['detail']
        assert client.get('/api/workspace').json() == before
        assert client.get('/api/routes', params=params).json() == routes
    restarted = TestClient(create_app(tmp_path, demo=False))
    assert restarted.get('/api/workspace').json() == before
    assert restarted.put('/api/reactions/' + reaction_id, json=body).status_code == 200
    with zipfile.ZipFile(io.BytesIO(restarted.get('/api/export').content)) as archive:
        text = archive.read(reaction_id + '.md').decode('utf-8')
        assert 'https://doi.org/10.1000/preserved' in text
        assert 'Original source must survive' not in text
    updated = restarted.put(f"/api/sources/{source['id']}/metadata", json={**metadata, 'doi': 'https://doi.org/10.1000/corrected'})
    assert updated.status_code == 200 and updated.json()['doi'] == '10.1000/corrected'
    assert updated.json()['id'] == source['id']
    assert restarted.put('/api/reactions/' + reaction_id, json=body).status_code == 200
    if kind == 'upload':
        assert restarted.get(f"/api/sources/{source['id']}/file").content == b'Original source must survive metadata edits.'


def test_unlinked_reference_requires_doi_but_text_evidence_keeps_it_optional(tmp_path):
    client = TestClient(create_app(tmp_path, demo=False))
    reference = client.post('/api/references', json={'title': 'Unlinked paper', 'doi': '10.1000/unlinked'}).json()
    assert client.put(f"/api/sources/{reference['id']}/metadata", json={'title': 'Unlinked paper'}).status_code == 422
    source = client.post('/api/sources', files={'file': ('note.txt', b'Observed reaction in a lab note.')}).json()
    metadata = {'title': 'Lab note', 'doi': '10.1000/optional'}
    assert client.put(f"/api/sources/{source['id']}/metadata", json=metadata).status_code == 200
    a = client.post('/api/molecules', json={'name': 'Methanol', 'smiles': 'CO'}).json()
    b = client.post('/api/molecules', json={'name': 'Formaldehyde', 'smiles': 'C=O'}).json()
    body = {'name': 'Text-backed reaction', 'reactants': [a['id']], 'products': [b['id']], 'status': 'reviewed',
            'evidence': [{'source_id': source['id'], 'page': 1, 'quote': 'Observed reaction in a lab note.'}]}
    created = client.post('/api/reactions', json=body)
    assert created.status_code == 201
    updated = client.put(f"/api/sources/{source['id']}/metadata", json={**metadata, 'doi': ''})
    assert updated.status_code == 200 and updated.json()['doi'] == ''
    assert client.put('/api/reactions/' + created.json()['id'], json=body).status_code == 200
