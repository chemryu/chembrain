from .chemistry import describe_molecule
from .store import Store


def seed(store: Store):
    text = """Chembrain 제품 사용 예시 — 합성 데모 데이터
이 자료는 논문이나 실제 실험 기록이 아닙니다. 아래 연결은 제품 기능을 설명하기 위한 예시이며, 실험 조건·수율·재현성이 검증되지 않았습니다.
Nitrobenzene → Aniline: 환원 반응 연결 예시.
Aniline + Acetic anhydride → Acetanilide: 아실화 반응 연결 예시.
Benzyl alcohol → Benzaldehyde: 광화학 산화 연결 예시.
Benzaldehyde → Benzoic acid: 전기화학 산화 연결 예시.
조건과 수율은 원문 근거가 없으므로 미기재로 보관합니다.
"""
    store.put("source", {"id": "demo-source", "title": "제품 사용 예시", "filename": "demo.md", "kind": "demo", "is_demo": True, "page_count": 1, "pages": [{"number": 1, "text": text}], "text_characters": len(text), "created_at": "", "sha256": "demo", "candidates": []})
    molecules = [
        ("nitrobenzene", "Nitrobenzene", "O=[N+]([O-])c1ccccc1", "니트로벤젠", "in_stock"),
        ("aniline", "Aniline", "Nc1ccccc1", "아닐린", "unknown"),
        ("acetic-anhydride", "Acetic anhydride", "CC(=O)OC(C)=O", "아세트산 무수물", "in_stock"),
        ("acetanilide", "Acetanilide", "CC(=O)Nc1ccccc1", "아세트아닐라이드", "unknown"),
        ("benzyl-alcohol", "Benzyl alcohol", "OCc1ccccc1", "벤질 알코올", "in_stock"),
        ("benzaldehyde", "Benzaldehyde", "O=Cc1ccccc1", "벤즈알데하이드", "unknown"),
        ("benzoic-acid", "Benzoic acid", "O=C(O)c1ccccc1", "벤조산", "unknown"),
    ]
    for mid, name, smiles, alias, availability in molecules:
        store.put("molecule", {"id": mid, "name": name, **describe_molecule(smiles), "aliases": [alias], "availability": availability, "notes": "제품 사용 예시입니다. 재고 표기도 데모입니다.", "is_demo": True})
    reactions = [
        ("demo-reduction", "방향족 니트로기 환원", "organic", ["nitrobenzene"], ["aniline"], "Nitrobenzene → Aniline: 환원 반응 연결 예시."),
        ("demo-acylation", "아민의 아실화", "organic", ["aniline", "acetic-anhydride"], ["acetanilide"], "Aniline + Acetic anhydride → Acetanilide: 아실화 반응 연결 예시."),
        ("demo-photo", "알코올의 광화학 산화", "photochemical", ["benzyl-alcohol"], ["benzaldehyde"], "Benzyl alcohol → Benzaldehyde: 광화학 산화 연결 예시."),
        ("demo-electro", "알데하이드의 전기화학 산화", "electrochemical", ["benzaldehyde"], ["benzoic-acid"], "Benzaldehyde → Benzoic acid: 전기화학 산화 연결 예시."),
    ]
    for rid, name, category, reactants, products, quote in reactions:
        store.put("reaction", {"id": rid, "name": name, "category": category, "reactants": reactants, "products": products, "reagents": "", "conditions": {}, "yield_percent": None, "status": "reviewed", "evidence": [{"source_id": "demo-source", "page": 1, "quote": quote}], "notes": "데모 연결입니다. 실험 또는 문헌으로 검증된 경로가 아닙니다.", "is_demo": True})
