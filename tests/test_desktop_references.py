import io
import json
import zipfile
from pathlib import Path

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
