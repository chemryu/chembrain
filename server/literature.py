"""Portable DOI-only starter library and conservative legacy English migration."""
import json
from datetime import datetime, timezone
from pathlib import Path

from .chemistry import describe_molecule
from .store import Store


def seed_literature(store: Store, manifest_path: Path):
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    source_ids = {s["filename"]: "literature-source-" + str(i) for i, s in enumerate(manifest["sources"])}
    now = datetime.now(timezone.utc).isoformat()
    for source in manifest["sources"]:
        sid = source_ids[source["filename"]]
        store.put("source", {**source["metadata"], "id": sid, "filename": "", "kind": "reference", "is_demo": False,
                             "page_count": 0, "pages": [], "candidates": [], "text_characters": 0,
                             "sha256": "doi-only-" + source["sha256"], "created_at": now,
                             "related_source_ids": [source_ids[f] for f in source.get("related_files", [])]})
    molecule_ids = {m["key"]: "literature-molecule-" + m["key"] for m in manifest["molecules"]}
    for molecule in manifest["molecules"]:
        store.put("molecule", {"id": molecule_ids[molecule["key"]], "name": molecule["name"],
                               **describe_molecule(molecule["smiles"]), "aliases": molecule.get("aliases", []),
                               "notes": molecule.get("notes", "Literature example; inventory and purchasing status unknown."),
                               "availability": "unknown", "is_demo": False})
    for reaction in manifest["reactions"]:
        result = {k: v for k, v in reaction.items() if k not in ("key", "reactants", "products", "evidence")}
        result.update(id="literature-reaction-" + reaction["key"], is_demo=False, updated_at=now,
                      reactants=[molecule_ids[k] for k in reaction["reactants"]], products=[molecule_ids[k] for k in reaction["products"]],
                      evidence=[{"source_id": source_ids[e["source"]], "page": e["page"], "locator": e["locator"],
                                 "quote": "", "citation_only": True, "page_numbering": "pdf"} for e in reaction["evidence"]])
        store.put("reaction", result)


def translate_known_records(store: Store, translations_path: Path):
    """Only replace exact original sample strings; user edits and original PDFs survive."""
    if not translations_path.exists():
        return
    translations = json.loads(translations_path.read_text(encoding="utf-8"))

    def translate(value):
        if isinstance(value, str):
            return translations.get(value, value)
        if isinstance(value, list):
            return [translate(item) for item in value]
        if isinstance(value, dict):
            return {translations.get(k, k): translate(v) for k, v in value.items()}
        return value

    for kind in ("molecule", "reaction", "source"):
        for record in store.all(kind):
            translated = translate(record)
            if translated != record:
                store.put(kind, translated)
