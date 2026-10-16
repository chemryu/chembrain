from .chemistry import describe_molecule
from .store import Store


def seed(store: Store):
    text = """Chembrain product examples — illustrative synthesis data
This is illustrative product data. Conditions, yields and reproducibility have not been verified.
Nitrobenzene → Aniline: Illustrative reduction connection.
Aniline + Acetic anhydride → Acetanilide: Illustrative acylation connection.
Benzyl alcohol → Benzaldehyde: Illustrative photochemical oxidation connection.
Benzaldehyde → Benzoic acid: Illustrative electrochemical oxidation connection.
Conditions and yields are left blank because no source evidence is available.
"""
    store.put("source", {"id": "demo-source", "title": "Product examples", "filename": "demo.md", "kind": "demo", "is_demo": True, "page_count": 1, "pages": [{"number": 1, "text": text}], "text_characters": len(text), "created_at": "", "sha256": "demo", "candidates": []})
    molecules = [
        ("nitrobenzene", "Nitrobenzene", "O=[N+]([O-])c1ccccc1", "Nitrobenzene", "in_stock"),
        ("aniline", "Aniline", "Nc1ccccc1", "Aniline", "unknown"),
        ("acetic-anhydride", "Acetic anhydride", "CC(=O)OC(C)=O", "Acetic anhydride", "in_stock"),
        ("acetanilide", "Acetanilide", "CC(=O)Nc1ccccc1", "Acetanilide", "unknown"),
        ("benzyl-alcohol", "Benzyl alcohol", "OCc1ccccc1", "Benzyl alcohol", "in_stock"),
        ("benzaldehyde", "Benzaldehyde", "O=Cc1ccccc1", "Benzaldehyde", "unknown"),
        ("benzoic-acid", "Benzoic acid", "O=C(O)c1ccccc1", "Benzoic acid", "unknown"),
    ]
    for mid, name, smiles, alias, availability in molecules:
        store.put("molecule", {"id": mid, "name": name, **describe_molecule(smiles), "aliases": [alias], "availability": availability, "notes": "Illustrative product data, including inventory labels.", "is_demo": True})
    reactions = [
        ("demo-reduction", "Aromatic nitro reduction", "organic", ["nitrobenzene"], ["aniline"], "Nitrobenzene → Aniline: Illustrative reduction connection."),
        ("demo-acylation", "Amine acylation", "organic", ["aniline", "acetic-anhydride"], ["acetanilide"], "Aniline + Acetic anhydride → Acetanilide: Illustrative acylation connection."),
        ("demo-photo", "Photochemical alcohol oxidation", "photochemical", ["benzyl-alcohol"], ["benzaldehyde"], "Benzyl alcohol → Benzaldehyde: Illustrative photochemical oxidation connection."),
        ("demo-electro", "Electrochemical aldehyde oxidation", "electrochemical", ["benzaldehyde"], ["benzoic-acid"], "Benzaldehyde → Benzoic acid: Illustrative electrochemical oxidation connection."),
    ]
    for rid, name, category, reactants, products, quote in reactions:
        store.put("reaction", {"id": rid, "name": name, "category": category, "reactants": reactants, "products": products, "reagents": "", "conditions": {}, "yield_percent": None, "status": "reviewed", "evidence": [{"source_id": "demo-source", "page": 1, "quote": quote}], "notes": "Illustrative connection; not experimentally or literature validated.", "is_demo": True})
