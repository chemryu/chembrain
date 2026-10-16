import json
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
