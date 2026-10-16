#!/usr/bin/env python3
"""Import a reviewed literature manifest and its exact PDFs without overwriting edits.

Run from the checkout with .venv/bin/python scripts/import_literature.py.
Original PDFs stay in local storage; they are not bundled in the repository.
"""
import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import httpx
import pymupdf
from rdkit import Chem

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from server.chemistry import describe_molecule  # noqa: E402
from server.models import ReactionInput, SourceMetadataInput  # noqa: E402


def preflight(manifest: dict, attachments: Path) -> dict[str, Path]:
    """Check every PDF, structure, and quote before making the first API write."""
    paths = {}
    pages = {}
    for source in manifest["sources"]:
        matches = [p for p in attachments.rglob(source["filename"]) if p.is_file() and hashlib.sha256(p.read_bytes()).hexdigest() == source["sha256"]]
        if not matches:
            raise ValueError(f"원본 PDF가 없거나 체크섬이 다릅니다: {source['filename']}")
        paths[source["filename"]] = matches[0]
        with pymupdf.open(matches[0]) as document:
            pages[source["filename"]] = [" ".join(page.get_text(sort=True).split()) for page in document]
        SourceMetadataInput(**source["metadata"])
    keys = set()
    for molecule in manifest["molecules"]:
        if molecule["key"] in keys:
            raise ValueError(f"중복 분자 키: {molecule['key']}")
        keys.add(molecule["key"])
        chemistry = describe_molecule(molecule["smiles"])
        if chemistry["formula"] != molecule["formula"]:
            raise ValueError(f"분자식이 맞지 않습니다: {molecule['key']}")
        if "expected_cip" in molecule:
            labels = sorted(label for _, label in Chem.FindMolChiralCenters(Chem.MolFromSmiles(molecule["smiles"]), includeUnassigned=True))
            if labels != molecule["expected_cip"]:
                raise ValueError(f"절대배치가 맞지 않습니다: {molecule['key']}")
    for reaction in manifest["reactions"]:
        if not set(reaction["reactants"] + reaction["products"]) <= keys:
            raise ValueError(f"등록되지 않은 분자 참조: {reaction['key']}")
        evidence = []
        for item in reaction["evidence"]:
            if item["source"] not in pages or not 1 <= item["page"] <= len(pages[item["source"]]):
                raise ValueError(f"잘못된 자료/페이지: {reaction['key']}")
            if " ".join(item["quote"].split()) not in pages[item["source"]][item["page"] - 1]:
                raise ValueError(f"원문과 일치하지 않는 인용: {reaction['key']}, {item['source']} p.{item['page']}")
            evidence.append({"source_id": item["source"], **{k: v for k, v in item.items() if k != "source"}})
        ReactionInput(**{**reaction, "evidence": evidence})
    return paths


def import_manifest(client: httpx.Client, manifest: dict, paths: dict[str, Path]) -> dict:
    workspace = client.get("/api/workspace").raise_for_status().json()
    counts = {"created_sources": 0, "created_molecules": 0, "created_reactions": 0, "reused_sources": 0, "reused_molecules": 0, "reused_reactions": 0}
    source_ids, molecule_ids, reaction_ids = {}, {}, {}
    sources_by_hash = {s["sha256"]: s for s in workspace["sources"]}
    source_records = {}
    for source in manifest["sources"]:
        existing = sources_by_hash.get(source["sha256"])
        if existing:
            counts["reused_sources"] += 1
        else:
            with paths[source["filename"]].open("rb") as stream:
                existing = client.post("/api/sources", files={"file": (source["filename"], stream, "application/pdf")}).raise_for_status().json()
            counts["created_sources"] += 1
        source_ids[source["filename"]] = existing["id"]
        source_records[source["filename"]] = existing
    for source in manifest["sources"]:
        existing = source_records[source["filename"]]
        # Existing bibliographic edits take precedence on repeat imports.
        if not existing.get("doi") and not existing.get("citation"):
            metadata = {**source["metadata"], "related_source_ids": [source_ids[file] for file in source.get("related_files", [])]}
            client.put(f"/api/sources/{existing['id']}/metadata", json=metadata).raise_for_status()
    molecules_by_structure = {m["smiles"]: m for m in workspace["molecules"]}
    for molecule in manifest["molecules"]:
        canonical = describe_molecule(molecule["smiles"])["smiles"]
        existing = molecules_by_structure.get(canonical)
        if existing and not existing.get("is_demo"):
            counts["reused_molecules"] += 1
        else:
            body = {"name": molecule["name"], "smiles": molecule["smiles"], "aliases": molecule.get("aliases", []), "availability": "unknown", "notes": molecule.get("notes", "사용자 제공 논문의 대표 사례에서 구조·분자식을 확인한 문헌 분자. 구매·재고 상태 미확인.")}
            existing = client.post("/api/molecules", json=body).raise_for_status().json()
            counts["created_molecules"] += 1
            molecules_by_structure[canonical] = existing
        molecule_ids[molecule["key"]] = existing["id"]
    for reaction in manifest["reactions"]:
        body = {k: v for k, v in reaction.items() if k not in ("key", "evidence", "reactants", "products")}
        body["reactants"] = [molecule_ids[key] for key in reaction["reactants"]]
        body["products"] = [molecule_ids[key] for key in reaction["products"]]
        body["evidence"] = [{"source_id": source_ids[e["source"]], **{k: v for k, v in e.items() if k != "source"}} for e in reaction["evidence"]]
        evidence_sources = {e["source_id"] for e in body["evidence"]}
        existing = next((r for r in workspace["reactions"] if r["name"] == body["name"] and set(r["reactants"]) == set(body["reactants"]) and set(r["products"]) == set(body["products"]) and {e["source_id"] for e in r["evidence"]} == evidence_sources), None)
        if existing:
            counts["reused_reactions"] += 1
        else:
            existing = client.post("/api/reactions", json=body).raise_for_status().json()
            workspace["reactions"].append(existing)
            counts["created_reactions"] += 1
        reaction_ids[reaction["key"]] = existing["id"]
    return {"manifest_id": manifest["id"], "checked_at": datetime.now(timezone.utc).isoformat(), "counts": counts, "source_ids": source_ids, "molecule_ids": molecule_ids, "reaction_ids": reaction_ids}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=ROOT / "examples/uploaded-literature.json")
    parser.add_argument("--attachments-dir", type=Path, default=ROOT / "papers")
    parser.add_argument("--base-url", default="http://127.0.0.1:8000")
    parser.add_argument("--report", type=Path, default=ROOT / ".data/curations/uploaded-literature-report.json")
    args = parser.parse_args()
    manifest = json.loads(args.manifest.read_text())
    paths = preflight(manifest, args.attachments_dir)
    with httpx.Client(base_url=args.base_url, timeout=120, trust_env=False) as client:
        report = import_manifest(client, manifest, paths)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"status": "imported", "report": str(args.report), **report["counts"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
