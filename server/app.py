import hashlib
import io
import json
import os
import re
import uuid
import zipfile
from datetime import datetime, timezone
from pathlib import Path

import pymupdf
from fastapi import FastAPI, File, HTTPException, Query, UploadFile
from fastapi.responses import FileResponse, HTMLResponse, PlainTextResponse, Response
from fastapi.staticfiles import StaticFiles

from .chemistry import describe_molecule, molecule_svg
from .models import MoleculeInput, ReactionInput, SourceMetadataInput
from .routes import find_routes
from .seed import seed
from .store import Store

ROOT = Path(__file__).resolve().parent.parent
MAX_UPLOAD = 20 * 1024 * 1024


def source_summary(source: dict) -> dict:
    return {k: v for k, v in source.items() if k not in ("pages", "candidates", "stored_filename")}


def extract_candidates(pages: list[dict]) -> list[dict]:
    pattern = re.compile(r"yield|reaction|irradiat|electro|cataly|solvent|stirr|synthes|수율|반응|전극|용매|촉매|합성", re.I)
    candidates = []
    for page in pages:
        for paragraph in re.split(r"\n\s*\n|(?<=[.!?])\s+", page["text"]):
            if pattern.search(paragraph) and len(paragraph.strip()) > 25:
                candidates.append({"page": page["number"], "text": paragraph.strip()[:3000]})
                if len(candidates) >= 30:
                    return candidates
    return candidates


def create_app(data_dir: Path | None = None, demo: bool | None = None) -> FastAPI:
    store = Store(data_dir or Path(os.environ.get("CHEMBRAIN_DATA_DIR", ROOT / ".data")))
    if not store.initialized():
        seed_demo = demo if demo is not None else os.environ.get("CHEMBRAIN_SEED_DEMO", "1") != "0"
        if seed_demo:
            seed(store)
        store.mark_initialized()
    app = FastAPI(title="Chembrain", version="0.1.0")
    app.state.store = store

    def get_record(kind: str, record_id: str) -> dict:
        record = store.get(kind, record_id)
        if record is None:
            raise HTTPException(404, "항목을 찾을 수 없습니다.")
        return record

    @app.get("/api/health")
    def health():
        return {"status": "ok", "storage": "sqlite", "chemistry": "rdkit", "pdf": "pymupdf"}

    @app.get("/api/workspace")
    def workspace():
        return {"molecules": store.all("molecule"), "reactions": store.all("reaction"), "sources": [source_summary(s) for s in store.all("source")]}

    @app.post("/api/molecules", status_code=201)
    def add_molecule(body: MoleculeInput):
        try:
            chemistry = describe_molecule(body.smiles)
        except ValueError as exc:
            raise HTTPException(422, str(exc)) from exc
        for existing in store.all("molecule"):
            if existing["inchikey"] == chemistry["inchikey"] and existing["smiles"] == chemistry["smiles"]:
                if existing.get("is_demo"):
                    result = {**body.model_dump(), **chemistry, "id": existing["id"], "is_demo": False}
                    store.put("molecule", result)
                    return result
                raise HTTPException(409, f"이미 등록된 구조입니다: {existing['name']}")
        result = {**body.model_dump(), **chemistry, "id": uuid.uuid4().hex, "is_demo": False}
        store.put("molecule", result)
        return result

    @app.get("/api/molecules/{mid}/svg")
    def structure(mid: str):
        return Response(molecule_svg(get_record("molecule", mid)["smiles"]), media_type="image/svg+xml", headers={"Cache-Control": "private, max-age=3600", "X-Content-Type-Options": "nosniff"})

    def validate_reaction(body: ReactionInput):
        for mid in body.reactants + body.products:
            get_record("molecule", mid)
        if len(set(body.reactants)) != len(body.reactants) or len(set(body.products)) != len(body.products):
            raise HTTPException(422, "같은 역할에 분자를 중복 등록할 수 없습니다.")
        if set(body.reactants) & set(body.products):
            raise HTTPException(422, "동일 분자를 반응물과 생성물로 동시에 지정할 수 없습니다.")
        if body.status == "reviewed" and not body.evidence:
            raise HTTPException(422, "검토 완료 기록에는 원문 근거가 한 개 이상 필요합니다.")
        for evidence in body.evidence:
            source = get_record("source", evidence.source_id)
            if evidence.page > source["page_count"]:
                raise HTTPException(422, "근거 페이지가 자료의 페이지 범위를 벗어납니다.")
            text = source["pages"][evidence.page - 1]["text"]
            normalized_quote = " ".join(evidence.quote.split())
            if not normalized_quote or normalized_quote not in " ".join(text.split()):
                raise HTTPException(422, "근거 문장은 선택한 원문 페이지에서 복사해 주세요.")

    def save_reaction(body: ReactionInput, rid: str, previous: dict | None = None):
        validate_reaction(body)
        participants = [get_record("molecule", mid) for mid in body.reactants + body.products]
        sources = [get_record("source", e.source_id) for e in body.evidence]
        real_evidence = any(not s.get("is_demo") for s in sources)
        is_demo = any(s.get("is_demo") for s in sources) or (not real_evidence and (bool(previous and previous.get("is_demo")) or any(m.get("is_demo") for m in participants)))
        result = {**body.model_dump(), "id": rid, "is_demo": bool(is_demo), "updated_at": datetime.now(timezone.utc).isoformat()}
        store.put("reaction", result)
        if not is_demo:
            for molecule in participants:
                if molecule.get("is_demo"):
                    # Chemical identity is reusable; illustrative inventory is not.
                    store.put("molecule", {**molecule, "is_demo": False, "availability": "unknown", "notes": ""})
        return result

    @app.post("/api/reactions", status_code=201)
    def add_reaction(body: ReactionInput):
        return save_reaction(body, uuid.uuid4().hex)

    @app.put("/api/reactions/{rid}")
    def update_reaction(rid: str, body: ReactionInput):
        return save_reaction(body, rid, get_record("reaction", rid))

    @app.post("/api/sources", status_code=201)
    async def upload_source(file: UploadFile = File(...)):
        filename = Path((file.filename or "document").replace("\\", "/")).name
        suffix = Path(filename).suffix.lower()
        if suffix not in (".pdf", ".md", ".txt"):
            raise HTTPException(415, "PDF, Markdown(.md), 텍스트(.txt) 파일을 선택하세요.")
        chunks, size = [], 0
        while chunk := await file.read(1024 * 1024):
            size += len(chunk)
            if size > MAX_UPLOAD:
                raise HTTPException(413, "파일은 20 MB 이하로 업로드하세요.")
            chunks.append(chunk)
        content = b"".join(chunks)
        if not content:
            raise HTTPException(422, "빈 파일입니다.")
        digest = hashlib.sha256(content).hexdigest()
        for source in store.all("source"):
            if source["sha256"] == digest:
                raise HTTPException(409, f"이미 업로드한 자료입니다: {source['title']}")
        try:
            if suffix == ".pdf":
                with pymupdf.open(stream=content, filetype="pdf") as document:
                    if document.needs_pass:
                        raise ValueError("암호가 걸린 PDF입니다. 암호를 해제한 파일을 사용하세요.")
                    if len(document) > 400:
                        raise ValueError("PDF는 400페이지 이하로 나눠 올려주세요.")
                    pages = []
                    characters = 0
                    for index, page in enumerate(document):
                        text = page.get_text(sort=True)
                        characters += len(text)
                        if characters > 2_000_000:
                            raise ValueError("추출 텍스트가 너무 큽니다. 파일을 나눠 주세요.")
                        pages.append({"number": index + 1, "text": text})
            else:
                text = content.decode("utf-8-sig")
                if len(text) > 2_000_000:
                    raise ValueError("텍스트는 200만 자 이하로 나눠 올려주세요.")
                pages = [{"number": 1, "text": text}]
            if not pages:
                raise ValueError("읽을 수 있는 페이지가 없습니다.")
        except (ValueError, RuntimeError, pymupdf.FileDataError) as exc:
            raise HTTPException(422, f"파일을 읽지 못했습니다. {exc}") from exc
        source_id = uuid.uuid4().hex
        stored = source_id + suffix
        result = {"id": source_id, "title": Path(filename).stem, "filename": filename, "kind": suffix[1:], "is_demo": False, "page_count": len(pages), "pages": pages, "text_characters": sum(len(p["text"]) for p in pages), "sha256": digest, "stored_filename": stored, "created_at": datetime.now(timezone.utc).isoformat(), "candidates": extract_candidates(pages)}
        path = store.directory / "uploads" / stored
        path.write_bytes(content)
        try:
            store.put("source", result)
        except Exception:
            path.unlink(missing_ok=True)
            raise
        return source_summary(result)

    @app.get("/api/sources/{sid}")
    def source_detail(sid: str):
        source = get_record("source", sid)
        return {k: v for k, v in source.items() if k != "stored_filename"}

    @app.put("/api/sources/{sid}/metadata")
    def update_source_metadata(sid: str, body: SourceMetadataInput):
        source = get_record("source", sid)
        if sid in body.related_source_ids or len(body.related_source_ids) != len(set(body.related_source_ids)):
            raise HTTPException(422, "연결 자료에서 자기 자신과 중복 항목은 제외하세요.")
        for related_id in body.related_source_ids:
            get_record("source", related_id)
        updated = {**source, **body.model_dump()}
        store.put("source", updated)
        return {k: v for k, v in updated.items() if k != "stored_filename"}

    @app.get("/api/sources/{sid}/file")
    def source_file(sid: str):
        source = get_record("source", sid)
        if source.get("stored_filename"):
            return FileResponse(store.directory / "uploads" / source["stored_filename"], filename=source["filename"], content_disposition_type="inline", media_type="application/pdf" if source["kind"] == "pdf" else "text/plain", headers={"X-Content-Type-Options": "nosniff"})
        return PlainTextResponse(source["pages"][0]["text"])

    @app.get("/api/routes")
    def routes(target: str, max_steps: int = Query(3, ge=1, le=6), limit: int = Query(12, ge=1, le=20), include_drafts: bool = False):
        get_record("molecule", target)
        candidates = find_routes(target, store.all("molecule"), store.all("reaction"), max_steps, limit, include_drafts)
        return {"routes": candidates, "max_steps": max_steps, "notice": "등록된 반응을 연결한 후보입니다. 각 단계의 조건 호환성·전체 경로 재현성·구매 가능성을 확인하세요. 후보 수를 제한한 탐색이며 모든 경로를 열거하지 않습니다."}

    @app.get("/api/export")
    def export():
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as archive:
            archive.writestr("README.md", "# Chembrain 내보내기\n\n분자·반응·자료는 고유 ID 기반 [[백링크]]로 연결됩니다. 원본 PDF는 포함하지 않습니다. 예시 데이터는 실험·문헌 근거가 아닙니다.\n")
            for kind in ("molecule", "reaction", "source"):
                for record in store.all(kind):
                    lines = [f"# {record.get('name', record.get('title', record['id']))}", ""]
                    if record.get("is_demo"):
                        lines += ["> 데모 데이터 · 실험 및 문헌 검증 전", ""]
                    if kind == "source":
                        if record.get("citation"):
                            lines += [record["citation"], ""]
                        if record.get("doi"):
                            lines += [f"DOI: https://doi.org/{record['doi']}", ""]
                        if record.get("notes"):
                            lines += ["> " + record["notes"], ""]
                        if record.get("related_source_ids"):
                            lines += ["## 같은 논문의 연결 자료", *[f"- [[{sid}]]" for sid in record["related_source_ids"]], ""]
                    if kind == "molecule":
                        lines += [f"SMILES: `{record['smiles']}`", f"InChIKey: `{record['inchikey']}`", "", record.get("notes", "")]
                        related = [r for r in store.all("reaction") if record["id"] in r["reactants"] + r["products"]]
                        lines += ["", "## 연결된 반응", *[f"- [[{r['id']}]] — {r['name']}" for r in related]]
                    elif kind == "reaction":
                        lines += ["## 반응물", *[f"- [[{mid}]]" for mid in record["reactants"]], "", "## 생성물", *[f"- [[{mid}]]" for mid in record["products"]], "", "## 조건", *[f"- {k}: {v}" for k, v in record["conditions"].items()], f"- 수율: {str(record['yield_percent']) + '%' if record['yield_percent'] is not None else '미기재'}", f"- 검토 상태: {record['status']}", "", "## 근거"]
                        for evidence in record["evidence"]:
                            locator = f" · {evidence['locator']}" if evidence.get("locator") else ""
                            lines += [f"[[{evidence['source_id']}]] · PDF p.{evidence['page']}{locator}", "", evidence["quote"], ""]
                        lines += [record.get("notes", "")]
                    else:
                        for page in record["pages"]:
                            lines += [f"## Page {page['number']}", "", page["text"], ""]
                    lines += ["", "## 구조화 데이터", "", "```json", json.dumps({k: v for k, v in record.items() if k not in ("pages", "stored_filename", "candidates")}, ensure_ascii=False, indent=2), "```"]
                    archive.writestr(f"{record['id']}.md", "\n".join(lines))
        return Response(buffer.getvalue(), media_type="application/zip", headers={"Content-Disposition": 'attachment; filename="chembrain-notes.zip"'})

    dist = ROOT / "dist"
    if (dist / "assets").exists():
        app.mount("/assets", StaticFiles(directory=dist / "assets"), name="assets")

    @app.get("/")
    def index():
        if (dist / "index.html").exists():
            return FileResponse(dist / "index.html")
        return HTMLResponse("<h1>Chembrain</h1><p>npm run build 후 서버를 다시 시작하세요.</p>", status_code=503)

    return app


app = create_app()
