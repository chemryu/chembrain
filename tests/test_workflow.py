import io
import zipfile

import pymupdf
import pytest
from fastapi.testclient import TestClient

from server.app import create_app
from server.routes import find_routes


@pytest.fixture
def client(tmp_path):
    return TestClient(create_app(tmp_path, demo=False))


def molecule(client, name, smiles):
    response = client.post("/api/molecules", json={"name": name, "smiles": smiles})
    assert response.status_code == 201, response.text
    return response.json()


def source(client):
    document = pymupdf.open()
    page = document.new_page()
    page.insert_text((40, 60), "Test fixture only. Methanol oxidation reaction gives formaldehyde.")
    page.insert_text((40, 90), "The isolated yield was 80 percent. Solvent: water.")
    second = document.new_page()
    second.insert_text((40, 60), "Second page for evidence boundary testing.")
    content = document.tobytes()
    document.close()
    response = client.post("/api/sources", files={"file": ("example.pdf", content, "application/pdf")})
    assert response.status_code == 201, response.text
    return response.json(), content


def reaction(client):
    a = molecule(client, "Methanol", "CO")
    b = molecule(client, "Formaldehyde", "C=O")
    s, _ = source(client)
    body = {"name": "Fixture oxidation", "category": "photochemical", "reactants": [a["id"]], "products": [b["id"]], "conditions": {"용매": "water", "파장": "450 nm"}, "yield_percent": 80, "status": "reviewed", "evidence": [{"source_id": s["id"], "page": 1, "quote": "The isolated yield was 80 percent."}]}
    response = client.post("/api/reactions", json=body)
    assert response.status_code == 201, response.text
    return a, b, s, response.json(), body


def test_pdf_review_route_export_and_restart(client, tmp_path):
    a, b, s, r, _ = reaction(client)
    detail = client.get(f"/api/sources/{s['id']}").json()
    assert detail["page_count"] == 2
    assert len(detail["candidates"]) >= 1
    assert detail["candidates"][0]["page"] == 1
    assert "oxidation" in detail["pages"][0]["text"]
    assert client.get(f"/api/sources/{s['id']}/file").content.startswith(b"%PDF")
    assert "svg" in client.get(f"/api/molecules/{a['id']}/svg").text
    routes = client.get("/api/routes", params={"target": b["id"]}).json()["routes"]
    assert len(routes) == 1
    assert routes[0]["starting_materials"] == [a["id"]]
    assert routes[0]["unknown_availability"] == [a["id"]]
    assert not routes[0]["is_demo"]
    export = client.get("/api/export")
    with zipfile.ZipFile(io.BytesIO(export.content)) as archive:
        text = archive.read(r["id"] + ".md").decode()
        assert f"[[{s['id']}]]" in text and "450 nm" in text and "80.0%" in text
    restored = TestClient(create_app(tmp_path, demo=True))
    workspace = restored.get("/api/workspace").json()
    assert len(workspace["reactions"]) == 1
    assert len(workspace["molecules"]) == 2  # do not inject demo into initialized data
    assert restored.get(f"/api/sources/{s['id']}/file").status_code == 200


def test_structure_validation_deduplication_and_stereo(client):
    assert client.post("/api/molecules", json={"name": "bad", "smiles": "invalid"}).status_code == 422
    assert client.post("/api/molecules", json={"name": " ", "smiles": "CO"}).status_code == 422
    a = molecule(client, "ethanol", "CCO")
    duplicate = client.post("/api/molecules", json={"name": "same", "smiles": "OCC"})
    assert duplicate.status_code == 409
    left = molecule(client, "L", "C[C@H](O)C(=O)O")
    right = molecule(client, "D", "C[C@@H](O)C(=O)O")
    assert left["inchikey"] != right["inchikey"]
    assert a["formula"] == "C2H6O"


def test_evidence_must_match_source_and_page(client):
    _, _, _, r, body = reaction(client)
    body["evidence"][0]["quote"] = "An invented yield was 99 percent."
    assert client.put(f"/api/reactions/{r['id']}", json=body).status_code == 422
    body["evidence"][0]["quote"] = "The isolated yield was 80 percent."
    body["evidence"][0]["page"] = 2
    assert client.put(f"/api/reactions/{r['id']}", json=body).status_code == 422
    body["evidence"][0]["page"] = 99
    assert client.put(f"/api/reactions/{r['id']}", json=body).status_code == 422
    body["evidence"] = []
    assert client.put(f"/api/reactions/{r['id']}", json=body).status_code == 422
    body["status"] = "draft"
    assert client.put(f"/api/reactions/{r['id']}", json=body).status_code == 200
    target = body["products"][0]
    assert not client.get("/api/routes", params={"target": target}).json()["routes"]
    assert client.get("/api/routes", params={"target": target, "include_drafts": True}).json()["routes"][0]["contains_drafts"]


def test_invalid_references_and_yields(client):
    _, _, _, r, body = reaction(client)
    body["yield_percent"] = 101
    assert client.put(f"/api/reactions/{r['id']}", json=body).status_code == 422
    body["yield_percent"] = None
    body["reactants"] = ["missing"]
    assert client.put(f"/api/reactions/{r['id']}", json=body).status_code == 404
    body["reactants"] = body["products"]
    assert client.put(f"/api/reactions/{r['id']}", json=body).status_code == 422
    assert client.get("/api/routes", params={"target": "missing"}).status_code == 404


def test_upload_errors_and_scan_detection(client):
    s, content = source(client)
    assert client.post("/api/sources", files={"file": ("same.pdf", content)}).status_code == 409
    assert client.post("/api/sources", files={"file": ("bad.pdf", b"not a pdf")} ).status_code == 422
    assert client.post("/api/sources", files={"file": ("bad.exe", b"bytes")} ).status_code == 415
    assert client.post("/api/sources", files={"file": ("blank.txt", b"")} ).status_code == 422
    assert client.post("/api/sources", files={"file": ("bad.txt", b"\xff")} ).status_code == 422
    assert client.post("/api/sources", files={"file": ("large.txt", b"x" * (20 * 1024 * 1024 + 1))} ).status_code == 413
    document = pymupdf.open()
    document.new_page()
    response = client.post("/api/sources", files={"file": ("scan.pdf", document.tobytes())})
    document.close()
    assert response.status_code == 201
    assert response.json()["text_characters"] == 0
    assert client.get(f"/api/sources/{s['id']}/file").headers["x-content-type-options"] == "nosniff"


def test_demo_is_explicit_and_multi_reactant_branches_are_preserved(tmp_path):
    client = TestClient(create_app(tmp_path))
    data = client.get("/api/workspace").json()
    assert len(data["molecules"]) == 7 and len(data["reactions"]) == 4
    assert all(r["is_demo"] and r["yield_percent"] is None for r in data["reactions"])
    one_step = client.get("/api/routes", params={"target": "acetanilide", "max_steps": 1}).json()["routes"]
    assert len(one_step) == 1
    assert set(one_step[0]["starting_materials"]) == {"aniline", "acetic-anhydride"}
    two_steps = client.get("/api/routes", params={"target": "acetanilide", "max_steps": 2}).json()["routes"]
    assert two_steps[0]["steps"] == 2
    assert set(two_steps[0]["starting_materials"]) == {"nitrobenzene", "acetic-anhydride"}
    assert all(r["is_demo"] for r in two_steps)


def test_branched_route_budget_and_cycles():
    molecules = [{"id": c, "availability": "unknown"} for c in "abcdef"]
    def r(rid, reactants, products):
        return {"id": rid, "reactants": list(reactants), "products": list(products), "status": "reviewed"}
    reactions = [r("end", "bc", "a"), r("left", "d", "b"), r("right", "e", "c"), r("cycle", "a", "d")]
    routes = find_routes("a", molecules, reactions, 3, 20, False)
    assert any(set(route["starting_materials"]) == {"d", "e"} and route["steps"] == 3 for route in routes)
    bounded = find_routes("a", molecules, reactions, 2, 20, False)
    assert all(route["steps"] <= 2 for route in bounded)
    assert not any("cycle" in route["reaction_ids"] for route in routes)


def test_markdown_upload_and_unknown_api(client):
    response = client.post("/api/sources", files={"file": ("../notes.md", "# 실험 노트\n반응 조건과 수율을 검토합니다. 충분한 길이의 예시 문장입니다.".encode())})
    assert response.status_code == 201
    assert response.json()["filename"] == "notes.md"
    assert response.json()["page_count"] == 1
    assert client.get("/api/not-real").status_code == 404


def test_real_evidence_reuses_seed_structures_without_demo_inventory(tmp_path):
    client = TestClient(create_app(tmp_path))
    uploaded = client.post("/api/sources", files={"file": ("real-note.md", b"Uploaded fixture: a reduction reaction was recorded.")}).json()
    response = client.post("/api/reactions", json={"name": "Uploaded reduction", "reactants": ["nitrobenzene"], "products": ["aniline"], "status": "reviewed", "evidence": [{"source_id": uploaded["id"], "page": 1, "quote": "a reduction reaction was recorded."}]})
    assert response.status_code == 201
    assert not response.json()["is_demo"]
    molecules = {m["id"]: m for m in client.get("/api/workspace").json()["molecules"]}
    assert not molecules["nitrobenzene"]["is_demo"]
    assert molecules["nitrobenzene"]["availability"] == "unknown"
    promoted = client.post("/api/molecules", json={"name": "Actual acetic anhydride", "smiles": "CC(=O)OC(C)=O", "availability": "order"})
    assert promoted.status_code == 201
    assert promoted.json()["id"] == "acetic-anhydride"
    assert not promoted.json()["is_demo"]


def test_source_metadata_links_keep_original_pages_and_validate_doi(client):
    first, original = source(client)
    second = client.post("/api/sources", files={"file": ("support.md", b"Supporting information fixture.")}).json()
    body = {"title": "Article — main", "doi": "https://doi.org/10.1126/science.1255525", "citation": "Zuo et al. (2014), Science 345, 437–440.", "document_role": "main", "related_source_ids": [second["id"]], "notes": "PDF pages differ from printed page numbers."}
    response = client.put(f"/api/sources/{first['id']}/metadata", json=body)
    assert response.status_code == 200
    updated = response.json()
    assert updated["doi"] == "10.1126/science.1255525"
    assert updated["pages"][0]["text"].startswith("Test fixture only.")
    assert "stored_filename" not in updated
    assert client.get(f"/api/sources/{first['id']}/file").content == original
    with zipfile.ZipFile(io.BytesIO(client.get("/api/export").content)) as archive:
        text = archive.read(first["id"] + ".md").decode()
        assert "https://doi.org/10.1126/science.1255525" in text
        assert f"[[{second['id']}]]" in text
    body["doi"] = "javascript:alert(1)"
    assert client.put(f"/api/sources/{first['id']}/metadata", json=body).status_code == 422
    body["doi"] = ""
    body["related_source_ids"] = [first["id"]]
    assert client.put(f"/api/sources/{first['id']}/metadata", json=body).status_code == 422
    body["related_source_ids"] = ["missing"]
    assert client.put(f"/api/sources/{first['id']}/metadata", json=body).status_code == 404


def test_evidence_locator_survives_edit_and_export(client):
    _, _, _, r, body = reaction(client)
    body["evidence"][0]["locator"] = "General procedure, second paragraph"
    updated = client.put(f"/api/reactions/{r['id']}", json=body)
    assert updated.status_code == 200
    assert updated.json()["evidence"][0]["locator"] == body["evidence"][0]["locator"]
    with zipfile.ZipFile(io.BytesIO(client.get("/api/export").content)) as archive:
        assert "General procedure, second paragraph" in archive.read(r["id"] + ".md").decode()
