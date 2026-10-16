import io
import zipfile

from fastapi.testclient import TestClient

from server.app import create_app


def test_molecule_edit_validates_identity_and_keeps_id(tmp_path):
    client = TestClient(create_app(tmp_path, demo=False))
    original = client.post('/api/molecules', json={'name':'Methanol','smiles':'CO'}).json()
    body = {**original, 'name':'User name','aliases':['MeOH'],'availability':'in_stock','notes':'Shelf A'}
    edited = client.put('/api/molecules/' + original['id'], json=body)
    assert edited.status_code == 200
    assert edited.json()['id'] == original['id']
    assert edited.json()['notes'] == 'Shelf A' and edited.json()['availability'] == 'in_stock'
    changed = client.put('/api/molecules/' + original['id'], json={**body,'smiles':'CCO'})
    assert changed.status_code == 200 and changed.json()['formula'] == 'C2H6O'
    other = client.post('/api/molecules', json={'name':'Water','smiles':'O'}).json()
    assert client.put('/api/molecules/' + original['id'], json={**body,'smiles':other['smiles']}).status_code == 409
    assert client.put('/api/molecules/' + original['id'], json={**body,'smiles':'invalid@@'}).status_code == 422
    assert client.put('/api/molecules/missing', json=body).status_code == 404
    restored = TestClient(create_app(tmp_path, demo=False)).get('/api/workspace').json()
    assert next(m for m in restored['molecules'] if m['id'] == original['id'])['formula'] == 'C2H6O'


def test_linked_molecule_metadata_can_change_but_identity_cannot(tmp_path):
    client = TestClient(create_app(tmp_path, demo=False))
    a = client.post('/api/molecules', json={'name':'Methanol','smiles':'CO'}).json()
    b = client.post('/api/molecules', json={'name':'Formaldehyde','smiles':'C=O'}).json()
    reaction = client.post('/api/reactions', json={'name':'Oxidation fixture','reactants':[a['id']],'products':[b['id']]}).json()
    assert client.put('/api/molecules/' + a['id'], json={**a,'smiles':'CCO'}).status_code == 422
    assert client.put('/api/molecules/' + a['id'], json={**a,'name':'Corrected methanol','notes':'User notes'}).status_code == 200
    workspace = client.get('/api/workspace').json()
    assert workspace['reactions'][0] == reaction
    assert next(m for m in workspace['molecules'] if m['id'] == a['id'])['smiles'] == a['smiles']


def test_doi_export_distinguishes_numbering_without_paper_text(tmp_path):
    client = TestClient(create_app(tmp_path, demo=False))
    a = client.post('/api/molecules', json={'name':'Methanol','smiles':'CO'}).json()
    b = client.post('/api/molecules', json={'name':'Formaldehyde','smiles':'C=O'}).json()
    source = client.post('/api/references', json={'title':'Fixture paper','doi':'10.1000/export'}).json()
    for numbering in ('pdf','printed','unspecified'):
        assert client.post('/api/reactions', json={'name':numbering,'reactants':[a['id']],'products':[b['id']],
            'evidence':[{'source_id':source['id'],'page':3,'locator':'Procedure A','citation_only':True,'page_numbering':numbering}]}).status_code == 201
    with zipfile.ZipFile(io.BytesIO(client.get('/api/export').content)) as archive:
        text = '\n'.join(archive.read(name).decode() for name in archive.namelist())
    assert 'Original PDF page 3 (1-based; printed page labels may differ)' in text
    assert 'Printed page 3' in text
    assert 'Reference page 3 (numbering unspecified)' in text
    assert 'PDF p.3' not in text and '"quote"' not in text
    assert 'https://doi.org/10.1000/export' in text
