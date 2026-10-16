import hashlib
import json

import pymupdf
import pytest
from fastapi.testclient import TestClient

from scripts.import_literature import import_manifest, preflight
from server.app import create_app


def fixture_manifest(tmp_path):
    pdf = tmp_path / "fixture.pdf"
    with pymupdf.open() as document:
        page = document.new_page()
        page.insert_text((40, 60), "Fixture oxidation reaction. Isolated yield was 80 percent.")
        document.save(pdf)
    return {
        "id": "test-import",
        "sources": [{"filename": pdf.name, "sha256": hashlib.sha256(pdf.read_bytes()).hexdigest(), "metadata": {"title": "Fixture article", "doi": "10.1000/fixture", "document_role": "main"}, "related_files": []}],
        "molecules": [{"key": "a", "name": "Methanol", "smiles": "CO", "formula": "CH4O"}, {"key": "b", "name": "Formaldehyde", "smiles": "C=O", "formula": "CH2O"}],
        "reactions": [{"key": "fixture", "name": "Fixture oxidation", "reactants": ["a"], "products": ["b"], "yield_percent": 80, "status": "reviewed", "evidence": [{"source": pdf.name, "page": 1, "quote": "Isolated yield was 80 percent.", "locator": "Fixture only"}]}],
    }


def test_repeat_import_preserves_user_records_and_bibliographic_edits(tmp_path):
    manifest = fixture_manifest(tmp_path)
    paths = preflight(manifest, tmp_path)
    client = TestClient(create_app(tmp_path / "data", demo=False))
    first = import_manifest(client, manifest, paths)
    assert first["counts"] == {"created_sources": 1, "created_molecules": 2, "created_reactions": 1, "reused_sources": 0, "reused_molecules": 0, "reused_reactions": 0}
    rid = first["reaction_ids"]["fixture"]
    reaction = client.get("/api/workspace").json()["reactions"][0]
    reaction.update(notes="User correction must survive repeat import.", yield_percent=75, status="draft")
    assert client.put(f"/api/reactions/{rid}", json=reaction).status_code == 200
    sid = first["source_ids"]["fixture.pdf"]
    assert client.put(f"/api/sources/{sid}/metadata", json={"title": "User title", "doi": "10.1000/fixture", "citation": "User citation"}).status_code == 200
    second = import_manifest(client, manifest, paths)
    assert second["counts"] == {"created_sources": 0, "created_molecules": 0, "created_reactions": 0, "reused_sources": 1, "reused_molecules": 2, "reused_reactions": 1}
    workspace = client.get("/api/workspace").json()
    assert workspace["reactions"][0]["yield_percent"] == 75
    assert workspace["reactions"][0]["notes"] == "User correction must survive repeat import."
    assert workspace["sources"][0]["title"] == "User title"


@pytest.mark.parametrize("problem", ["checksum", "quote", "formula", "stereo"])
def test_preflight_rejects_wrong_source_or_chemistry(tmp_path, problem):
    manifest = fixture_manifest(tmp_path)
    if problem == "checksum":
        manifest["sources"][0]["sha256"] = "0" * 64
    elif problem == "quote":
        manifest["reactions"][0]["evidence"][0]["quote"] = "Invented yield."
    elif problem == "formula":
        manifest["molecules"][0]["formula"] = "C2H6O"
    else:
        manifest["molecules"][0]["expected_cip"] = ["R"]
    with pytest.raises(ValueError):
        preflight(manifest, tmp_path)


def test_published_manifest_keeps_conflicting_results_as_drafts():
    from pathlib import Path
    from server.chemistry import describe_molecule

    manifest = json.loads((Path(__file__).resolve().parent.parent / "examples/uploaded-literature.json").read_text(encoding="utf-8"))
    for molecule in manifest["molecules"]:
        assert describe_molecule(molecule["smiles"])["formula"] == molecule["formula"]
    nicewicz = [r for r in manifest["reactions"] if r["key"].startswith("nicewicz")]
    assert len(nicewicz) == 2
    assert all(r["status"] == "draft" and "article" in r["notes"] and "SI" in r["notes"] for r in nicewicz)
    horn6 = next(r for r in manifest["reactions"] if r["key"] == "horn-compound6")
    horn7 = next(r for r in manifest["reactions"] if r["key"] == "horn-compound7")
    assert horn6["conditions"]["Solvent"].startswith("MeCN")
    assert horn7["conditions"]["Solvent"].startswith("acetone")
    assert "Current density" not in horn6["conditions"]
