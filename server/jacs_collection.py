"""Bounded, keyless JACS discovery. Only explicitly licensed open PDFs are fetched.

No institutional sessions, cookies, credentials or access-control workarounds are used.
Bibliographic records and downloaded files are unreviewed research inputs.
"""
from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
import hashlib
import ipaddress
import json
import os
from pathlib import Path
import re
import socket
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid

import pymupdf as fitz

from .store import Store

JOURNAL = "Journal of the American Chemical Society"
ISSNS = {"0002-7863", "1520-5126"}
STATE = "jacs_collection_state"
ATTACHMENTS = "jacs_collection_attachments"
CHECKPOINT = "jacs_collection_checkpoint"
ARTICLES = "jacs_collection_articles"
RESUME = "jacs_collection_resume"
MAX_PDF_BYTES = 30 * 1024 * 1024
MAX_PDF_PAGES = 400


def canonical_doi(value: str) -> str:
    value = re.sub(r"^https?://(?:dx\.)?doi\.org/", "", str(value).strip(), flags=re.I).casefold()
    if len(value) > 200 or not re.fullmatch(r"10\.\d{4,9}/[^\s<>\x00-\x1f?#]+", value):
        raise ValueError("Invalid DOI metadata")
    return value


def _timestamp(value: str) -> datetime:
    result = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if result.tzinfo is None:
        result = result.replace(tzinfo=timezone.utc)
    return result.astimezone(timezone.utc)


def _utc() -> datetime:
    return datetime.now(timezone.utc)


class CollectionBusy(RuntimeError):
    pass


class PDFPageLimitError(ValueError):
    pass


class CollectionHTTPError(RuntimeError):
    def __init__(self, status: int):
        self.status = status
        super().__init__(f"Collection HTTP request failed ({status})")


def _failure(stage: str, exc: Exception) -> str:
    suffix = f"HTTP {exc.status}" if isinstance(exc, CollectionHTTPError) else f"PDF exceeds {MAX_PDF_PAGES} pages" if isinstance(exc, PDFPageLimitError) else type(exc).__name__
    return f"{stage} failed ({suffix})"


def _retry_delay(headers) -> float:
    value = headers.get("Retry-After", "") if headers else ""
    try:
        seconds = float(value)
    except (TypeError, ValueError):
        try:
            seconds = (parsedate_to_datetime(value) - _utc()).total_seconds()
        except (TypeError, ValueError, OverflowError):
            seconds = 2
    return max(0, min(seconds, 30))


@contextmanager
def collection_lock(store: Store):
    """Kernel-owned lock; an interrupted process cannot leave a permanent busy flag."""
    stream = (store.directory / "jacs-collection.lock").open("a+b")
    locked = False
    try:
        stream.seek(0)
        if stream.read(1) == b"":
            stream.write(b"0")
            stream.flush()
        stream.seek(0)
        try:
            if os.name == "nt":
                import msvcrt
                msvcrt.locking(stream.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl
                fcntl.flock(stream.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            locked = True
        except (BlockingIOError, OSError) as exc:
            raise CollectionBusy("A JACS collection is already running") from exc
        yield
    finally:
        if locked:
            stream.seek(0)
            if os.name == "nt":
                import msvcrt
                msvcrt.locking(stream.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                import fcntl
                fcntl.flock(stream.fileno(), fcntl.LOCK_UN)
        stream.close()


def _public_url(url: str, hosts: set[str], *, resolve: bool = True):
    if any(ord(character) < 32 or ord(character) == 127 for character in url):
        raise ValueError("Invalid collection URL characters")
    parsed = urllib.parse.urlsplit(url)
    if parsed.scheme != "https" or parsed.hostname not in hosts or parsed.username or parsed.password or parsed.port not in (None, 443):
        raise ValueError("Untrusted collection URL")
    if parsed.query or parsed.fragment:
        raise ValueError("Unexpected collection URL parameters")
    if resolve:
        addresses = socket.getaddrinfo(parsed.hostname, 443, type=socket.SOCK_STREAM)
        if not addresses or any(not ipaddress.ip_address(item[4][0]).is_global for item in addresses):
            raise ValueError("Non-public collection destination")


@dataclass(frozen=True)
class LicensedPDF:
    doi: str
    supplied_url: str
    license_url: str
    license_start: str
    license_end: str | None
    content_version: str
    upstream_type: str


@dataclass(frozen=True)
class _PDFPolicy:
    expected_doi: str
    content_version: str

    def validate(self, url: str, *, resolve: bool = True):
        if self.content_version not in ("vor", "am"):
            raise ValueError("Unsupported licensed PDF version")
        _public_url(url, {"pubs.acs.org"}, resolve=resolve)
        path = urllib.parse.unquote(urllib.parse.urlsplit(url).path)
        match = re.fullmatch(r"/doi/(?:pdf|epdf)/(10\.\d{4,9}/.+)", path)
        if not match or any(part in (".", "..") for part in path.split("/")):
            raise ValueError("Unapproved article PDF route")
        if canonical_doi(match.group(1)) != canonical_doi(self.expected_doi):
            raise ValueError("PDF URL does not match licensed article")


class _Redirect(urllib.request.HTTPRedirectHandler):
    def __init__(self, hosts, pdf_policy: _PDFPolicy | None = None):
        super().__init__()
        self.hosts = hosts
        self.pdf_policy = pdf_policy

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        if "pubs.acs.org" in self.hosts:
            if self.pdf_policy is None:
                raise ValueError("PDF redirect requires immutable article policy")
            self.pdf_policy.validate(newurl)
        else:
            _public_url(newurl, self.hosts)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


class CrossrefClient:
    """Small allowlisted HTTP gateway; real network is replaced in unit tests."""
    def __init__(self, until: str | None = None):
        self._last = 0.0
        self.until = until or _utc().date().isoformat()

    def _get(self, url: str, hosts: set[str], limit: int, *, pdf_policy: _PDFPolicy | None = None) -> bytes:
        parsed = urllib.parse.urlsplit(url)
        # Crossref pagination has public, controller-generated query parameters.
        if "pubs.acs.org" in hosts:
            if pdf_policy is None:
                raise ValueError("PDF retrieval requires immutable article policy")
            pdf_policy.validate(url)
        else:
            _public_url(urllib.parse.urlunsplit(parsed._replace(query="")), hosts)
        opener = urllib.request.build_opener(_Redirect(hosts, pdf_policy))
        for attempt in range(2):
            time.sleep(max(0, 0.5 - (time.monotonic() - self._last)))
            self._last = time.monotonic()
            try:
                request = urllib.request.Request(url, headers={"User-Agent": "Chembrain-JACS-Collector/1.0 (public bibliographic metadata; open-access-only PDFs)", "Accept": "application/json" if "api.crossref.org" in hosts else "application/pdf"})
                with opener.open(request, timeout=30) as response:
                    length = response.headers.get("Content-Length")
                    if length and int(length) > limit:
                        raise ValueError("Collection response exceeds size limit")
                    data = response.read(limit + 1)
                    if len(data) > limit:
                        raise ValueError("Collection response exceeds size limit")
                    return data
            except urllib.error.HTTPError as exc:
                if attempt == 0 and (exc.code == 429 or 500 <= exc.code < 600):
                    time.sleep(_retry_delay(exc.headers))
                    continue
                raise CollectionHTTPError(exc.code) from None
            except (urllib.error.URLError, TimeoutError, OSError):
                raise RuntimeError("Collection network request failed") from None
        raise RuntimeError("Collection request failed")

    def page(self, start: str, cursor: str) -> dict:
        query = urllib.parse.urlencode({"filter": f"from-pub-date:{start},until-pub-date:{self.until},type:journal-article", "rows": 100, "cursor": cursor})
        payload = self._get("https://api.crossref.org/journals/0002-7863/works?" + query, {"api.crossref.org"}, 8 * 1024 * 1024)
        result = json.loads(payload)
        if not isinstance(result, dict) or not isinstance(result.get("message"), dict):
            raise ValueError("Invalid Crossref response")
        return result["message"]

    def pdf(self, candidate: LicensedPDF) -> bytes:
        if not isinstance(candidate, LicensedPDF):
            raise ValueError("A verified OA candidate is required")
        policy = _PDFPolicy(candidate.doi, candidate.content_version)
        return self._get(candidate.supplied_url, {"pubs.acs.org"}, MAX_PDF_BYTES, pdf_policy=policy)


def _licensed_pdf(item: dict, now: datetime) -> LicensedPDF | None:
    """A PDF link alone is not OA evidence; require a current matching CC license."""
    licenses = {}
    for license in item.get("license", []):
        if not isinstance(license, dict):
            continue
        url = str(license.get("URL", ""))
        parsed = urllib.parse.urlsplit(url)
        if parsed.scheme not in ("https", "http") or parsed.hostname not in ("creativecommons.org", "www.creativecommons.org") or parsed.username or parsed.password or parsed.query or parsed.fragment:
            continue
        if not re.fullmatch(r"/(?:licenses/(?:by|by-sa|by-nd|by-nc|by-nc-sa|by-nc-nd)/(?:[1234]\.0)|publicdomain/(?:zero|mark)/1\.0)/?", parsed.path):
            continue
        version = license.get("content-version")
        if version not in ("vor", "am"):
            continue
        try:
            start = license.get("start", {})
            if start.get("date-time"):
                effective = _timestamp(start["date-time"])
            else:
                values = start["date-parts"][0]
                effective = datetime(*values[:3], tzinfo=timezone.utc)
            if effective > now:
                continue
            expires = None
            end = license.get("end")
            if end:
                if end.get("date-time"):
                    expires = _timestamp(end["date-time"])
                else:
                    expires = datetime(*end["date-parts"][0][:3], tzinfo=timezone.utc)
                if expires <= now:
                    continue
        except (KeyError, TypeError, ValueError, IndexError, AttributeError):
            continue
        licenses[version] = {"url": url, "start": effective.isoformat(), "end": expires.isoformat() if expires is not None else None}
    for link in item.get("link", []):
        if not isinstance(link, dict) or link.get("content-type") not in (None, "unspecified", "application/pdf") or link.get("content-version") not in licenses:
            continue
        url = str(link.get("URL", ""))
        try:
            doi = canonical_doi(item["DOI"])
            _PDFPolicy(doi, link["content-version"]).validate(url, resolve=False)
        except (ValueError, KeyError):
            continue
        evidence = licenses[link["content-version"]]
        return LicensedPDF(doi=doi, supplied_url=url, license_url=evidence["url"],
                           license_start=evidence["start"], license_end=evidence["end"],
                           content_version=link["content-version"], upstream_type=str(item.get("type", "")))
    return None


def _reference(item: dict, started_at: str) -> dict:
    doi = canonical_doi(item["DOI"])
    if not doi.startswith("10.1021/") or item.get("type") != "journal-article":
        raise ValueError("Unexpected journal article metadata")
    if not ISSNS.intersection(item.get("ISSN", [])) and JOURNAL not in item.get("container-title", []):
        raise ValueError("Journal identity was not confirmed")
    title = " ".join(str(item.get("title", [""])[0]).split())[:500]
    if not title:
        raise ValueError("Article title is missing")
    authors = [" ".join(str(author.get(part, "")) for part in ("given", "family")).strip() for author in item.get("author", []) if isinstance(author, dict)]
    date_parts = item.get("published", item.get("published-online", item.get("published-print", {}))).get("date-parts", [[]])[0]
    publication_date = "-".join(str(value).zfill(2) for value in date_parts[:3])
    citation = "; ".join(filter(None, [", ".join(authors), title, JOURNAL, publication_date, "https://doi.org/" + doi]))[:2000]
    return {"id": uuid.uuid4().hex, "doi": doi, "title": title, "citation": citation,
            "document_role": "main", "related_source_ids": [], "notes": "", "filename": "",
            "kind": "reference", "is_demo": False, "page_count": 0, "pages": [], "candidates": [],
            "text_characters": 0, "sha256": "reference-" + uuid.uuid4().hex, "created_at": started_at,
            "collection": {"journal": JOURNAL, "authors": authors, "publication_date": publication_date, "provider": "Crossref", "type": item["type"]}}


def _save_pdf(store: Store, doi: str, data: bytes, candidate: LicensedPDF, source_id: str, now: str):
    if canonical_doi(doi) != candidate.doi:
        raise ValueError("Attachment candidate DOI mismatch")
    _PDFPolicy(candidate.doi, candidate.content_version).validate(candidate.supplied_url, resolve=False)
    if not isinstance(data, bytes) or len(data) > MAX_PDF_BYTES or not data.startswith(b"%PDF-"):
        raise ValueError("Invalid or oversized open-access PDF")
    try:
        with fitz.open(stream=data, filetype="pdf") as document:
            if document.is_encrypted or len(document) == 0:
                raise ValueError("Encrypted or empty PDF")
            page_count = len(document)
            if page_count > MAX_PDF_PAGES:
                raise PDFPageLimitError("PDF page ceiling exceeded")
    except PDFPageLimitError:
        raise
    except Exception:
        raise ValueError("Open-access download is not a readable PDF") from None
    folder = store.directory / "jacs_pdfs"
    folder.mkdir(exist_ok=True)
    filename = hashlib.sha256(doi.encode()).hexdigest() + ".pdf"
    descriptor, temporary = tempfile.mkstemp(prefix=".download-", dir=folder)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, folder / filename)
    finally:
        Path(temporary).unlink(missing_ok=True)
    attachments = store.get_metadata(ATTACHMENTS, {})
    file_stat = (folder / filename).stat()
    attachments[doi] = {"source_id": source_id, "filename": "jacs_pdfs/" + filename,
                        "size_bytes": file_stat.st_size, "mtime_ns": file_stat.st_mtime_ns,
                        "sha256": hashlib.sha256(data).hexdigest(), "page_count": page_count,
                        "license": candidate.license_url, "license_start": candidate.license_start,
                        "license_end": candidate.license_end, "content_version": candidate.content_version,
                        "supplied_url": candidate.supplied_url, "upstream_type": candidate.upstream_type,
                        "downloaded_at": now, "policy": "open_access_only"}
    store.set_metadata(ATTACHMENTS, attachments)


def _attachment_valid(store: Store, doi: str, attachment: dict, *, full: bool = True) -> bool:
    path = store.directory / "jacs_pdfs" / (hashlib.sha256(doi.encode()).hexdigest() + ".pdf")
    try:
        if not path.is_file():
            return False
        stat = path.stat()
        if stat.st_size > MAX_PDF_BYTES:
            return False
        # Avoid rehashing the entire vault on every UI status poll. Changed files
        # are rehashed; the weekly collector always requests full verification.
        if not full and stat.st_size == attachment.get("size_bytes") and stat.st_mtime_ns == attachment.get("mtime_ns"):
            return True
        return hashlib.sha256(path.read_bytes()).hexdigest() == attachment.get("sha256")
    except OSError:
        return False


def collection_status(store: Store) -> dict:
    running = False
    try:
        with collection_lock(store):
            pass
    except CollectionBusy:
        running = True
    last = store.get_metadata(STATE)
    if last and last.get("status") == "running" and not running:
        last = {**last, "status": "interrupted"}
    attachments = store.get_metadata(ATTACHMENTS, {})
    articles = store.get_metadata(ARTICLES, {})
    return {"journal": JOURNAL, "policy": "open_access_only", "running": running, "last_run": last,
            "totals": {"articles": len(articles), "pdfs": sum(_attachment_valid(store, doi, attachment, full=False) for doi, attachment in attachments.items())}}


def collect_jacs(store: Store, *, client=None, metadata_only: bool = False, days: int | None = None,
                 max_pages: int = 20, max_pdfs: int = 20) -> dict:
    if days is not None and (isinstance(days, bool) or not 1 <= days <= 3650):
        raise ValueError("days must be between 1 and 3650")
    if not 1 <= max_pages <= 100 or not 0 <= max_pdfs <= 100:
        raise ValueError("Collection limits exceed bounds")
    with collection_lock(store):
        now = _utc()
        started_at = now.isoformat()
        result = {"started_at": started_at, "finished_at": None, "status": "running", "discovered": 0,
                  "added": 0, "existing": 0, "pdfs_saved": 0, "errors": [], "notices": [], "oa_unconfirmed": 0,
                  "metadata_only": metadata_only}
        store.set_metadata(STATE, result)
        checkpoint = store.get_metadata(CHECKPOINT)
        start = now - timedelta(days=days or 14)
        if checkpoint and days is None:
            try:
                start = min(start, _timestamp(checkpoint) - timedelta(days=7))
            except (ValueError, TypeError):
                pass
        resume = store.get_metadata(RESUME) if days is None else None
        cursor = "*"
        until = now.date().isoformat()
        crawl_started = started_at
        processed = 0
        if isinstance(resume, dict) and resume.get("cursor") and resume.get("start") and resume.get("until") and resume.get("started_at"):
            try:
                start = datetime.fromisoformat(resume["start"]).replace(tzinfo=timezone.utc)
                until = datetime.fromisoformat(resume["until"]).date().isoformat()
                crawl_started = _timestamp(resume["started_at"]).isoformat()
                cursor = str(resume["cursor"])
                processed = int(resume.get("processed", 0))
                result["errors"] = [value for value in resume.get("errors", []) if isinstance(value, str)][:100]
                result["notices"] = [notice for notice in resume.get("notices", []) if isinstance(notice, dict) and notice.get("code") == "duplicate_doi_matches"]
            except (ValueError, TypeError):
                cursor = "*"
                processed = 0
        gateway = client if client is not None else CrossrefClient(until=until)
        result["window_start"] = start.date().isoformat()
        result["window_end"] = until
        result["resumed"] = cursor != "*"
        seen = set()
        pdf_attempts = 0
        seen_cursors = {cursor}
        complete = False
        metadata_errors = False
        try:
            for index in range(max_pages):
                message = gateway.page(start.date().isoformat(), cursor)
                items = message.get("items")
                if not isinstance(items, list) or len(items) > 100:
                    raise ValueError("Crossref items were not a list")
                if not items:
                    complete = True
                    break
                for item in items:
                    stage = "Article metadata import"
                    try:
                        record = _reference(item, started_at)
                        doi = record["doi"]
                        if doi in seen:
                            continue
                        seen.add(doi)
                        result["discovered"] += 1
                        source, added = store.import_jacs_reference(record, notices=result["notices"])
                        result["added" if added else "existing"] += 1
                        articles = store.get_metadata(ARTICLES, {})
                        articles[doi] = {"source_id": source["id"], "last_seen": started_at, "type": item["type"], "provider": "Crossref"}
                        store.set_metadata(ARTICLES, articles)
                        attachment = store.get_metadata(ATTACHMENTS, {}).get(doi)
                        if metadata_only:
                            continue
                        if attachment and _attachment_valid(store, doi, attachment):
                            continue
                        stage = "Open-access PDF download"
                        candidate = _licensed_pdf(item, now)
                        if candidate is None:
                            result["oa_unconfirmed"] += 1
                        elif pdf_attempts < max_pdfs:
                            pdf_attempts += 1
                            _save_pdf(store, doi, gateway.pdf(candidate), candidate, source["id"], started_at)
                            result["pdfs_saved"] += 1
                        else:
                            raise ValueError("Open-access PDF limit reached; repeat collection to continue")
                    except Exception as exc:
                        # Never persist exception text, download URLs, cookies or credentials.
                        result["errors"].append(_failure(stage, exc))
                        if stage == "Article metadata import":
                            metadata_errors = True
                processed += len(items)
                total = message.get("total-results")
                page_size = message.get("items-per-page")
                if (isinstance(total, int) and not isinstance(total, bool) and processed >= total) or (isinstance(page_size, int) and page_size > 0 and len(items) < page_size):
                    complete = True
                    break
                next_cursor = message.get("next-cursor")
                if not next_cursor or next_cursor in seen_cursors:
                    raise ValueError("Crossref pagination did not finish")
                seen_cursors.add(next_cursor)
                cursor = next_cursor
                if not metadata_errors:
                    store.set_metadata(RESUME, {"cursor": cursor, "start": start.date().isoformat(), "until": until,
                                               "started_at": crawl_started, "processed": processed, "errors": result["errors"][:100],
                                               "notices": result["notices"]})
            else:
                result["errors"].append("Metadata page limit reached; collection checkpoint retained")
        except Exception as exc:
            result["errors"].append(_failure("Metadata collection", exc))
        result["status"] = "partial" if result["errors"] else "success"
        result["finished_at"] = _utc().isoformat()
        if complete or metadata_errors:
            store.set_metadata(RESUME, None)
        if not result["errors"] and complete:
            store.set_metadata(CHECKPOINT, crawl_started)
        store.set_metadata(STATE, result)
        return result
