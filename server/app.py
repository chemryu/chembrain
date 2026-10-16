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
from .literature import seed_literature, translate_known_records
from .store import Store

ROOT = Path(__file__).resolve().parent.parent
MAX_UPLOAD = 20 * 1024 * 1024


def source_summary(source: dict) -> dict:
    return {k: v for k, v in source.items() if k not in ("pages", "candidates", "stored_filename")}


def export_record(record: dict) -> dict:
    result = {k: v for k, v in record.items() if k not in ("pages", "stored_filename", "candidates")}
    if "evidence" in result:
        result["evidence"] = [{k: v for k, v in item.items() if k != "quote"} for item in result["evidence"]]
    return result


def evidence_page_label(evidence: dict, source: dict | None = None) -> str:
    numbering = evidence.get("page_numbering", "unspecified")
    if numbering == "pdf" or (not evidence.get("citation_only") and numbering == "unspecified" and source and source.get("kind") == "pdf"):
        return f"Original PDF page {evidence['page']} (1-based; printed page labels may differ)"
    if numbering == "printed":
        return f"Printed page {evidence['page']}"
    return f"Reference page {evidence['page']} (numbering unspecified)"


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
        if os.environ.get("CHEMBRAIN_SEED_LITERATURE") == "1":
            seed_literature(store, ROOT / "examples/uploaded-literature.json")
        store.mark_initialized()
    translate_known_records(store, ROOT / "examples/english-translations.json")
    app = FastAPI(title="Chembrain", version="0.2.0")
    app.state.store = store

    def get_record(kind: str, record_id: str) -> dict:
        record = store.get(kind, record_id)
        if record is None:
            raise HTTPException(404, "Record not found.")
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
                raise HTTPException(409, f"Structure already registered: {existing['name']}")
        result = {**body.model_dump(), **chemistry, "id": uuid.uuid4().hex, "is_demo": False}
        store.put("molecule", result)
        return result

    @app.put("/api/molecules/{mid}")
    def update_molecule(mid: str, body: MoleculeInput):
        previous = get_record("molecule", mid)
        try:
            chemistry = describe_molecule(body.smiles)
        except ValueError as exc:
            raise HTTPException(422, str(exc)) from exc
        identity_changed = chemistry["smiles"] != previous["smiles"] or chemistry["inchikey"] != previous["inchikey"]
        if identity_changed and any(mid in r["reactants"] + r["products"] for r in store.all("reaction")):
            raise HTTPException(422, "This structure is used in reactions. Add a new molecule to change its chemical identity.")
        for existing in store.all("molecule"):
            if existing["id"] != mid and existing["smiles"] == chemistry["smiles"] and existing["inchikey"] == chemistry["inchikey"]:
                raise HTTPException(409, f"Structure already registered: {existing['name']}")
        result = {**previous, **body.model_dump(), **chemistry, "updated_at": datetime.now(timezone.utc).isoformat()}
        store.put("molecule", result)
        return result

    @app.get("/api/molecules/{mid}/svg")
    def structure(mid: str):
        return Response(molecule_svg(get_record("molecule", mid)["smiles"]), media_type="image/svg+xml", headers={"Cache-Control": "private, max-age=3600", "X-Content-Type-Options": "nosniff"})

    def validate_reaction(body: ReactionInput):
        for mid in body.reactants + body.products:
            get_record("molecule", mid)
        if len(set(body.reactants)) != len(body.reactants) or len(set(body.products)) != len(body.products):
            raise HTTPException(422, "A molecule cannot appear twice in the same role.")
        if set(body.reactants) & set(body.products):
            raise HTTPException(422, "A molecule cannot be both a reactant and a product.")
        if body.status == "reviewed" and not body.evidence:
            raise HTTPException(422, "A reviewed record requires at least one reference.")
        for evidence in body.evidence:
            source = get_record("source", evidence.source_id)
            if evidence.citation_only:
                if not source.get("doi") or not evidence.locator.strip():
                    raise HTTPException(422, "A DOI citation requires a DOI and a page, figure or procedure locator.")
                if source["page_count"] and evidence.page > source["page_count"]:
                    raise HTTPException(422, "The citation page is outside the document.")
                continue
            if source["kind"] == "reference":
                raise HTTPException(422, "DOI references require citation_only evidence; no original text is available for verification.")
            if evidence.page > source["page_count"]:
                raise HTTPException(422, "The evidence page is outside the document.")
            text = source["pages"][evidence.page - 1]["text"]
            normalized_quote = " ".join(evidence.quote.split())
            if not normalized_quote or normalized_quote not in " ".join(text.split()):
                raise HTTPException(422, "The evidence quote must match the selected source page.")

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
            raise HTTPException(415, "Choose a PDF, Markdown (.md), or text (.txt) file.")
        chunks, size = [], 0
        while chunk := await file.read(1024 * 1024):
            size += len(chunk)
            if size > MAX_UPLOAD:
                raise HTTPException(413, "Files must be 20 MB or smaller.")
            chunks.append(chunk)
        content = b"".join(chunks)
        if not content:
            raise HTTPException(422, "The file is empty.")
        digest = hashlib.sha256(content).hexdigest()
        for source in store.all("source"):
            if source["sha256"] == digest:
                raise HTTPException(409, f"Document already uploaded: {source['title']}")
        try:
            if suffix == ".pdf":
                with pymupdf.open(stream=content, filetype="pdf") as document:
                    if document.needs_pass:
                        raise ValueError("Use a PDF without password protection.")
                    if len(document) > 400:
                        raise ValueError("PDFs must contain no more than 400 pages.")
                    pages = []
                    characters = 0
                    for index, page in enumerate(document):
                        text = page.get_text(sort=True)
                        characters += len(text)
                        if characters > 2_000_000:
                            raise ValueError("Extracted text exceeds the size limit. Split the document.")
                        pages.append({"number": index + 1, "text": text})
            else:
                text = content.decode("utf-8-sig")
                if len(text) > 2_000_000:
                    raise ValueError("Text files must contain no more than two million characters.")
                pages = [{"number": 1, "text": text}]
            if not pages:
                raise ValueError("No readable pages found.")
        except (ValueError, RuntimeError, pymupdf.FileDataError) as exc:
            raise HTTPException(422, f"Unable to read the file. {exc}") from exc
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

    @app.post("/api/references", status_code=201)
    def add_reference(body: SourceMetadataInput):
        if not body.doi:
            raise HTTPException(422, "A DOI is required.")
        if body.related_source_ids:
            for sid in body.related_source_ids:
                get_record("source", sid)
        if any(s.get("doi", "").lower() == body.doi.lower() and s.get("document_role") == body.document_role for s in store.all("source")):
            raise HTTPException(409, "This DOI and document type are already in your library.")
        result = {**body.model_dump(), "id": uuid.uuid4().hex, "filename": "", "kind": "reference", "is_demo": False,
                  "page_count": 0, "pages": [], "candidates": [], "text_characters": 0, "sha256": "reference-" + uuid.uuid4().hex,
                  "created_at": datetime.now(timezone.utc).isoformat()}
        store.put("source", result)
        return source_summary(result)

    @app.get("/api/sources/{sid}")
    def source_detail(sid: str):
        source = get_record("source", sid)
        return {k: v for k, v in source.items() if k != "stored_filename"}

    @app.put("/api/sources/{sid}/metadata")
    def update_source_metadata(sid: str, body: SourceMetadataInput):
        source = get_record("source", sid)
        doi_required = source["kind"] == "reference" or any(
            evidence.get("source_id") == sid and evidence.get("citation_only")
            for reaction in store.all("reaction")
            for evidence in reaction.get("evidence", [])
        )
        if doi_required and not body.doi:
            raise HTTPException(422, "A DOI is required for DOI-only references and references used by DOI citations.")
        if sid in body.related_source_ids or len(body.related_source_ids) != len(set(body.related_source_ids)):
            raise HTTPException(422, "Related references must be unique and cannot include this reference.")
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
        if not source.get("pages"):
            raise HTTPException(404, "This reference is available through its DOI link.")
        return PlainTextResponse(source["pages"][0]["text"])

    @app.get("/api/routes")
    def routes(target: str, max_steps: int = Query(3, ge=1, le=6), limit: int = Query(12, ge=1, le=20), include_drafts: bool = False):
        get_record("molecule", target)
        candidates = find_routes(target, store.all("molecule"), store.all("reaction"), max_steps, limit, include_drafts)
        return {"routes": candidates, "max_steps": max_steps, "notice": "Candidates connect recorded reactions. Check condition compatibility, route reproducibility and material availability. Search is bounded and does not enumerate every route."}

    @app.get("/api/export")
    def export():
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as archive:
            archive.writestr("README.md", "# Chembrain export\n\nMolecules, reactions and references use ID-based [[backlinks]]. Papers are linked by DOI; full text and source excerpts are omitted. Demo data is illustrative.\n")
            for kind in ("molecule", "reaction", "source"):
                for record in store.all(kind):
                    lines = [f"# {record.get('name', record.get('title', record['id']))}", ""]
                    if record.get("is_demo"):
                        lines += ["> Demo data · not experimentally verified", ""]
                    if kind == "source":
                        if record.get("citation"):
                            lines += [record["citation"], ""]
                        if record.get("doi"):
                            lines += [f"DOI: https://doi.org/{record['doi']}", ""]
                        if record.get("notes"):
                            lines += ["> " + record["notes"], ""]
                        if record.get("related_source_ids"):
                            lines += ["## Related references", *[f"- [[{sid}]]" for sid in record["related_source_ids"]], ""]
                    if kind == "molecule":
                        lines += [f"SMILES: `{record['smiles']}`", f"InChIKey: `{record['inchikey']}`", "", record.get("notes", "")]
                        related = [r for r in store.all("reaction") if record["id"] in r["reactants"] + r["products"]]
                        lines += ["", "## Linked reactions", *[f"- [[{r['id']}]] — {r['name']}" for r in related]]
                    elif kind == "reaction":
                        lines += ["## Reactants", *[f"- [[{mid}]]" for mid in record["reactants"]], "", "## Products", *[f"- [[{mid}]]" for mid in record["products"]], "", "## Conditions", *[f"- {k}: {v}" for k, v in record["conditions"].items()], f"- Yield: {str(record['yield_percent']) + '%' if record['yield_percent'] is not None else 'Not reported'}", f"- Review status: {record['status']}", "", "## References"]
                        for evidence in record["evidence"]:
                            locator = f" · {evidence['locator']}" if evidence.get("locator") else ""
                            source = store.get("source", evidence["source_id"])
                            doi = f" · https://doi.org/{source['doi']}" if source and source.get("doi") else ""
                            lines += [f"[[{evidence['source_id']}]] · {evidence_page_label(evidence, source)}{locator}{doi}", ""]
                        lines += [record.get("notes", "")]
                    lines += ["", "## Structured data", "", "```json", json.dumps(export_record(record), ensure_ascii=False, indent=2), "```"]
                    archive.writestr(f"{record['id']}.md", "\n".join(lines))
        return Response(buffer.getvalue(), media_type="application/zip", headers={"Content-Disposition": 'attachment; filename="chembrain-notes.zip"'})

    dist = ROOT / "dist"
    if (dist / "assets").exists():
        app.mount("/assets", StaticFiles(directory=dist / "assets"), name="assets")

    @app.get("/")
    def index():
        if (dist / "index.html").exists():
            return FileResponse(dist / "index.html")
        return HTMLResponse("<h1>Chembrain</h1><p>Run npm run build and restart the server.</p>", status_code=503)

    return app


app = create_app()
