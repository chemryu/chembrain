import json
import re
from contextlib import contextmanager
import sqlite3
from pathlib import Path


class Store:
    def __init__(self, directory: Path):
        self.directory = directory
        directory.mkdir(parents=True, exist_ok=True)
        (directory / "uploads").mkdir(exist_ok=True)
        self.path = directory / "chembrain.sqlite3"
        with self.connect() as db:
            db.execute("CREATE TABLE IF NOT EXISTS records (kind TEXT NOT NULL, id TEXT PRIMARY KEY, data TEXT NOT NULL)")
            db.execute("CREATE INDEX IF NOT EXISTS records_kind ON records(kind)")
            db.execute("CREATE TABLE IF NOT EXISTS metadata (key TEXT PRIMARY KEY, value TEXT NOT NULL)")

    @contextmanager
    def connect(self):
        db = sqlite3.connect(self.path, timeout=30)
        try:
            db.execute("PRAGMA journal_mode=WAL")
            with db:
                yield db
        finally:
            db.close()

    def all(self, kind: str) -> list[dict]:
        with self.connect() as db:
            return [json.loads(row[0]) for row in db.execute("SELECT data FROM records WHERE kind=? ORDER BY rowid", (kind,))]

    def get(self, kind: str, record_id: str) -> dict | None:
        with self.connect() as db:
            row = db.execute("SELECT data FROM records WHERE kind=? AND id=?", (kind, record_id)).fetchone()
            return json.loads(row[0]) if row else None

    def put(self, kind: str, record: dict):
        with self.connect() as db:
            db.execute("INSERT INTO records(kind,id,data) VALUES(?,?,?) ON CONFLICT(id) DO UPDATE SET data=excluded.data WHERE kind=excluded.kind", (kind, record["id"], json.dumps(record, ensure_ascii=False)))

    def initialized(self) -> bool:
        with self.connect() as db:
            return db.execute("SELECT 1 FROM metadata WHERE key='initialized'").fetchone() is not None

    def mark_initialized(self):
        with self.connect() as db:
            db.execute("INSERT OR IGNORE INTO metadata VALUES('initialized','1')")

    def get_metadata(self, key: str, default=None):
        with self.connect() as db:
            row = db.execute("SELECT value FROM metadata WHERE key=?", (key,)).fetchone()
            return json.loads(row[0]) if row else default

    def set_metadata(self, key: str, value):
        with self.connect() as db:
            db.execute("INSERT INTO metadata(key,value) VALUES(?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value", (key, json.dumps(value, ensure_ascii=False)))

    @staticmethod
    def _doi(value: str) -> str:
        return re.sub(r"^https?://(?:dx\.)?doi\.org/", "", value.strip(), flags=re.I).casefold()

    def create_reference(self, record: dict):
        """Atomic manual insert: DOI + document role identify a reference, not an SI."""
        with self.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            for row in db.execute("SELECT data FROM records WHERE kind='source'"):
                previous = json.loads(row[0])
                if self._doi(previous.get("doi", "")) == self._doi(record.get("doi", "")) and previous.get("document_role", "other") == record.get("document_role", "other"):
                    raise ValueError("This DOI and document type are already in your library.")
            db.execute("INSERT INTO records(kind,id,data) VALUES('source',?,?)", (record["id"], json.dumps(record, ensure_ascii=False)))
        return record

    def import_jacs_reference(self, record: dict, *, notices: list[dict] | None = None) -> tuple[dict, bool]:
        """Use an existing main/unspecified record; preserve uploads and all user metadata."""
        with self.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            candidates = []
            for row in db.execute("SELECT data FROM records WHERE kind='source'"):
                previous = json.loads(row[0])
                if self._doi(previous.get("doi", "")) == self._doi(record["doi"]) and previous.get("document_role", "other") in ("main", "other"):
                    candidates.append(previous)
            if candidates:
                candidates.sort(key=lambda item: (item.get("document_role") != "main", item["id"]))
                if notices is not None and len(candidates) > 1:
                    notice = {"code": "duplicate_doi_matches", "doi": self._doi(record["doi"]),
                              "source_ids": [item["id"] for item in candidates], "selected_source_id": candidates[0]["id"]}
                    if notice not in notices:
                        notices.append(notice)
                return candidates[0], False
            db.execute("INSERT INTO records(kind,id,data) VALUES('source',?,?)", (record["id"], json.dumps(record, ensure_ascii=False)))
            return record, True
