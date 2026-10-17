from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
import copy
import hashlib
from pathlib import Path

import fitz
import pytest

from server.jacs_collection import (ATTACHMENTS, CHECKPOINT, STATE, CollectionBusy, JOURNAL, _licensed_pdf,
                                    _public_url, canonical_doi, collect_jacs, collection_lock, collection_status)
from server.store import Store


def article(doi="10.1021/jacs.6b00001", *, oa=True):
    item = {"DOI": doi, "type": "journal-article", "ISSN": ["0002-7863"], "title": ["A photochemical reaction"],
            "container-title": [JOURNAL], "author": [{"given": "Ada", "family": "Chemist"}],
            "published": {"date-parts": [[2026, 10, 16]]},
            "link": [{"URL": "https://pubs.acs.org/doi/pdf/" + doi, "content-type": "application/pdf", "content-version": "vor"}]}
    if oa:
        item["license"] = [{"URL": "https://creativecommons.org/licenses/by/4.0/", "content-version": "vor",
                            "start": {"date-time": "2020-01-01T00:00:00Z"}}]
    return item


def pdf_bytes():
    with fitz.open() as document:
        document.new_page().insert_text((50, 50), "Open access article")
        return document.tobytes()


class Client:
    def __init__(self, pages, pdf=None):
        self.pages = iter(pages)
        self.calls = []
        self.downloads = []
        self.data = pdf_bytes() if pdf is None else pdf

    def page(self, start, cursor):
        self.calls.append((start, cursor))
        value = next(self.pages)
        if isinstance(value, Exception):
            raise value
        return value

    def pdf(self, url):
        self.downloads.append(url)
        if isinstance(self.data, Exception):
            raise self.data
        return self.data


def pages(*items):
    return [{"items": list(items), "next-cursor": "second"}, {"items": []}]


def test_collect_metadata_pdf_repeat_idempotent(tmp_path):
    store = Store(tmp_path)
    client = Client(pages(article()))
    result = collect_jacs(store, client=client)
    assert result["status"] == "success"
    assert result["added"] == 1 and result["pdfs_saved"] == 1
    reference = store.all("source")[0]
    assert reference["kind"] == "reference" and reference["page_count"] == 0
    assert reference["collection"]["authors"] == ["Ada Chemist"]
    attachment = store.get_metadata(ATTACHMENTS)[reference["doi"]]
    assert hashlib.sha256((tmp_path / attachment["filename"]).read_bytes()).hexdigest() == attachment["sha256"]
    repeat = Client(pages(article()))
    result = collect_jacs(store, client=repeat)
    assert result["existing"] == 1 and result["added"] == 0 and not repeat.downloads
    assert len(store.all("source")) == 1
    assert collection_status(store)["totals"] == {"articles": 1, "pdfs": 1}


def test_preserve_user_uploads_and_supplement(tmp_path):
    store = Store(tmp_path)
    main = {"id": "main", "doi": "HTTPS://DOI.ORG/10.1021/JACS.6B00001", "document_role": "main", "title": "My title", "kind": "pdf", "page_count": 17, "pages": [{"text": "Uploaded text"}], "stored_filename": "original.pdf", "notes": "My notes"}
    si = {**main, "id": "supplement", "document_role": "supplement", "page_count": 200}
    store.put("source", si)
    store.put("source", main)
    result = collect_jacs(store, client=Client(pages(article())))
    assert result["existing"] == 1 and result["added"] == 0
    assert store.get("source", "main") == main
    assert store.get("source", "supplement") == si
    assert store.get_metadata(ATTACHMENTS)["10.1021/jacs.6b00001"]["source_id"] == "main"


def test_supplement_does_not_suppress_main_import(tmp_path):
    store = Store(tmp_path)
    store.put("source", {"id": "si", "doi": article()["DOI"], "document_role": "supplement"})
    result = collect_jacs(store, client=Client(pages(article(oa=False))))
    assert result["added"] == 1 and len(store.all("source")) == 2


@pytest.mark.parametrize("change", ["no_license", "future", "expired", "missing_start", "missing_version", "mismatch", "publisher_license", "bogus_cc", "different_doi", "third_party", "query", "http", "port", "credentials"])
def test_only_current_explicit_matching_oa_downloaded(tmp_path, change):
    item = article()
    if change == "no_license":
        item.pop("license")
    elif change == "future":
        item["license"][0]["start"]["date-time"] = "2099-01-01T00:00:00Z"
    elif change == "expired":
        item["license"][0]["end"] = {"date-time": "2020-01-02T00:00:00Z"}
    elif change == "missing_start":
        item["license"][0].pop("start")
    elif change == "missing_version":
        item["license"][0].pop("content-version")
    elif change == "mismatch":
        item["license"][0]["content-version"] = "am"
    elif change == "publisher_license":
        item["license"][0]["URL"] = "https://pubs.acs.org/userlicense"
    elif change == "bogus_cc":
        item["license"][0]["URL"] = "https://creativecommons.org/licenses/free/4.0/"
    elif change == "different_doi":
        item["link"][0]["URL"] += "different"
    elif change == "third_party":
        item["link"][0]["URL"] = item["link"][0]["URL"].replace("pubs.acs.org", "attacker.invalid")
    elif change == "query":
        item["link"][0]["URL"] += "?token=secret"
    elif change == "http":
        item["link"][0]["URL"] = item["link"][0]["URL"].replace("https:", "http:")
    elif change == "port":
        item["link"][0]["URL"] = item["link"][0]["URL"].replace("pubs.acs.org", "pubs.acs.org:9000")
    elif change == "credentials":
        item["link"][0]["URL"] = item["link"][0]["URL"].replace("pubs.acs.org", "name:secret@pubs.acs.org")
    client = Client(pages(item))
    result = collect_jacs(Store(tmp_path), client=client)
    assert result["status"] == "success" and result["oa_unconfirmed"] == 1
    assert not client.downloads


def test_publicdomain_license_dateparts():
    item = article()
    item["license"][0] = {"URL": "https://creativecommons.org/publicdomain/zero/1.0/", "start": {"date-parts": [[2020, 1, 1]]}, "content-version": "vor"}
    assert _licensed_pdf(item, datetime.now(timezone.utc)) is not None


@pytest.mark.parametrize("data", [b"<html>Institutional login</html>", b"%PDF-invalid", b"%PDF-" + b"x" * (30 * 1024 * 1024)])
def test_invalid_pdf_is_not_attached_or_partial_file(tmp_path, data):
    store = Store(tmp_path)
    result = collect_jacs(store, client=Client(pages(article()), pdf=data))
    assert result["status"] == "partial" and result["added"] == 1
    assert not store.get_metadata(ATTACHMENTS)
    assert not list(tmp_path.glob("jacs_pdfs/*"))
    assert store.get_metadata(CHECKPOINT) is None


def test_metadata_only_does_not_download(tmp_path):
    client = Client(pages(article()))
    result = collect_jacs(Store(tmp_path), client=client, metadata_only=True)
    assert result["added"] == 1 and result["pdfs_saved"] == 0 and not client.downloads


def test_failures_keep_checkpoint_and_partial_records_retry(tmp_path):
    store = Store(tmp_path)
    checkpoint = "2026-01-01T00:00:00+00:00"
    store.set_metadata(CHECKPOINT, checkpoint)
    client = Client([{"items": [article(oa=False)], "next-cursor": "next"}, RuntimeError("https://example.invalid?secret=do-not-log")])
    result = collect_jacs(store, client=client)
    assert result["status"] == "partial" and result["added"] == 1
    assert store.get_metadata(CHECKPOINT) == checkpoint
    assert client.calls[0][0] == "2025-12-25"
    assert "do-not-log" not in str(result)
    retry = collect_jacs(store, client=Client(pages(article(oa=False))))
    assert retry["existing"] == 1 and retry["status"] == "success"
    assert store.get_metadata(CHECKPOINT) != checkpoint


def test_cross_page_duplicates_and_bound(tmp_path):
    first = article(oa=False)
    second = article("10.1021/jacs.6b00002", oa=False)
    client = Client([{"items": [first], "next-cursor": "next"}, {"items": [first, second], "next-cursor": "more"}, {"items": []}])
    result = collect_jacs(Store(tmp_path), client=client)
    assert result["discovered"] == 2 and result["added"] == 2
    limited = collect_jacs(Store(tmp_path / "limited"), client=Client(pages(first)), max_pages=1)
    assert limited["status"] == "partial"


def test_repeated_cursor_is_partial_not_infinite(tmp_path):
    result = collect_jacs(Store(tmp_path), client=Client([{"items": [article(oa=False)], "next-cursor": "*"}]))
    assert result["status"] == "partial"


def test_live_lock_and_interrupted_status(tmp_path):
    store = Store(tmp_path)
    store.set_metadata(STATE, {"status": "running"})
    assert collection_status(store)["last_run"]["status"] == "interrupted"
    with collection_lock(store):
        assert collection_status(store)["running"]
        with pytest.raises(CollectionBusy):
            collect_jacs(store, client=Client([]))
    assert not collection_status(store)["running"]


def test_atomic_manual_and_collector_import(tmp_path):
    store = Store(tmp_path)
    def importer(index):
        return store.import_jacs_reference({"id": str(index), "doi": article()["DOI"], "document_role": "main"})
    with ThreadPoolExecutor(max_workers=8) as executor:
        results = list(executor.map(importer, range(20)))
    assert sum(added for _, added in results) == 1 and len(store.all("source")) == 1
    with pytest.raises(ValueError):
        store.create_reference({"id": "manual", "doi": article()["DOI"].upper(), "document_role": "main"})
    store.create_reference({"id": "si", "doi": article()["DOI"], "document_role": "supplement"})
    assert len(store.all("source")) == 2


def test_public_url_rejects_private_dns(monkeypatch):
    monkeypatch.setattr("server.jacs_collection.socket.getaddrinfo", lambda *args, **kwargs: [(2, 1, 6, "", ("127.0.0.1", 443))])
    with pytest.raises(ValueError, match="Non-public"):
        _public_url("https://pubs.acs.org/doi/pdf/10.1021/a", {"pubs.acs.org"})


@pytest.mark.parametrize("value", ["10.1021/test?password=secret", "10.1021/test#x", "http://evil.invalid/a", "10.1021/a\nb", "10.1021/<a>"])
def test_invalid_doi(value):
    with pytest.raises(ValueError):
        canonical_doi(value)


def test_pdf_download_failure_retried_next_run_and_attempts_bounded(tmp_path):
    store = Store(tmp_path)
    client = Client(pages(article(), article("10.1021/jacs.6b00002")), pdf=RuntimeError("token=hidden"))
    result = collect_jacs(store, client=client, max_pdfs=1)
    assert result["status"] == "partial" and len(client.downloads) == 1
    assert result["added"] == 2 and store.get_metadata(CHECKPOINT) is None
    retry = collect_jacs(store, client=Client(pages(article(), article("10.1021/jacs.6b00002"))))
    assert retry["existing"] == 2 and retry["pdfs_saved"] == 2 and retry["status"] == "success"


def test_missing_or_corrupt_vault_file_downloaded_again(tmp_path):
    store = Store(tmp_path)
    collect_jacs(store, client=Client(pages(article())))
    attachment = next(iter(store.get_metadata(ATTACHMENTS).values()))
    path = tmp_path / attachment["filename"]
    path.write_bytes(b"corrupted")
    result = collect_jacs(store, client=Client(pages(article())))
    assert result["pdfs_saved"] == 1
    path.unlink()
    result = collect_jacs(store, client=Client(pages(article())))
    assert result["pdfs_saved"] == 1 and path.exists()


def test_malformed_and_wrong_journal_records_do_not_abort_valid_items(tmp_path):
    wrong = article("10.1021/acs.organomet.6b00001")
    wrong["ISSN"] = ["9999-9999"]
    wrong["container-title"] = ["Another journal"]
    result = collect_jacs(Store(tmp_path), client=Client(pages({}, wrong, article(oa=False))))
    assert result["status"] == "partial" and result["added"] == 1
    assert len(result["errors"]) == 2


def test_transport_retry_and_bounded_read(monkeypatch):
    from server.jacs_collection import CrossrefClient
    import urllib.error
    monkeypatch.setattr("server.jacs_collection._public_url", lambda *args, **kwargs: None)
    monkeypatch.setattr("server.jacs_collection.time.sleep", lambda _: None)
    class Response:
        headers = {}
        def __enter__(self):
            return self
        def __exit__(self, *args):
            return False
        def read(self, size):
            assert size == 101
            return b"x" * 101
    class Opener:
        calls = 0
        def open(self, request, timeout):
            self.calls += 1
            if self.calls == 1:
                raise urllib.error.HTTPError("https://api.crossref.org?secret=hidden", 429, "rate limited", {}, None)
            return Response()
    opener = Opener()
    monkeypatch.setattr("server.jacs_collection.urllib.request.build_opener", lambda *args: opener)
    with pytest.raises(ValueError, match="size limit"):
        CrossrefClient()._get("https://api.crossref.org/test", {"api.crossref.org"}, 100)
    assert opener.calls == 2


def test_redirect_cannot_reach_other_or_private_host(monkeypatch):
    from server.jacs_collection import _Redirect
    import urllib.request
    request = urllib.request.Request("https://pubs.acs.org/doi/pdf/10.1021/a")
    handler = _Redirect({"pubs.acs.org"})
    for url in ("http://pubs.acs.org/pdf", "https://evil.invalid/pdf", "https://127.0.0.1/pdf"):
        with pytest.raises(ValueError):
            handler.redirect_request(request, None, 302, "redirect", {}, url)


def test_bounded_crawl_resumes_instead_of_replaying_prefix(tmp_path):
    from server.jacs_collection import RESUME
    store = Store(tmp_path)
    first = Client([{"items": [article(oa=False)], "next-cursor": "resume-here", "total-results": 2}])
    limited = collect_jacs(store, client=first, max_pages=1)
    assert limited["status"] == "partial"
    assert store.get_metadata(RESUME)["cursor"] == "resume-here"
    second = Client([{"items": [article("10.1021/jacs.6b00002", oa=False)], "next-cursor": "resume-here", "total-results": 2}])
    completed = collect_jacs(store, client=second, max_pages=1)
    assert completed["status"] == "success" and completed["resumed"]
    assert second.calls[0][1] == "resume-here"
    assert store.get_metadata(RESUME) is None
    assert store.get_metadata(CHECKPOINT) == limited["started_at"]
    assert len(store.all("source")) == 2


def test_realistic_final_short_page_repeated_cursor_is_complete(tmp_path):
    result = collect_jacs(Store(tmp_path), client=Client([{"items": [article(oa=False)], "next-cursor": "*", "items-per-page": 100, "total-results": 1}]))
    assert result["status"] == "success"


def test_earlier_pdf_error_is_not_erased_by_successful_resume(tmp_path):
    store = Store(tmp_path)
    first = Client([{"items": [article()], "next-cursor": "next", "total-results": 2}], pdf=RuntimeError("failed"))
    assert collect_jacs(store, client=first, max_pages=1)["status"] == "partial"
    second = Client([{"items": [article("10.1021/jacs.6b00002", oa=False)], "next-cursor": "next", "total-results": 2}])
    result = collect_jacs(store, client=second)
    assert result["status"] == "partial"
    assert store.get_metadata(CHECKPOINT) is None


def test_crossref_query_filters_publication_window(monkeypatch):
    from server.jacs_collection import CrossrefClient
    import json
    import urllib.parse
    client = CrossrefClient(until="2026-10-17")
    calls = []
    def get(url, *args):
        calls.append(url)
        return json.dumps({"message": {"items": []}}).encode()
    monkeypatch.setattr(client, "_get", get)
    client.page("2026-10-03", "*")
    query = urllib.parse.parse_qs(urllib.parse.urlsplit(calls[0]).query)
    assert query["filter"] == ["from-pub-date:2026-10-03,until-pub-date:2026-10-17,type:journal-article"]


def test_retry_after_is_bounded_and_http_errors_are_sanitized(tmp_path):
    from server.jacs_collection import CollectionHTTPError, _retry_delay
    assert _retry_delay({"Retry-After": "99999"}) == 30
    assert _retry_delay({"Retry-After": "5"}) == 5
    assert _retry_delay({"Retry-After": "invalid"}) == 2
    result = collect_jacs(Store(tmp_path), client=Client(pages(article()), pdf=CollectionHTTPError(403)))
    assert "Open-access PDF download failed (HTTP 403)" in result["errors"]


def test_totals_do_not_count_missing_vault_files_and_count_existing_imports(tmp_path):
    store = Store(tmp_path)
    store.put("source", {"id": "main", "doi": article()["DOI"], "document_role": "main", "title": "User title"})
    collect_jacs(store, client=Client(pages(article())))
    assert collection_status(store)["totals"] == {"articles": 1, "pdfs": 1}
    attachment = next(iter(store.get_metadata(ATTACHMENTS).values()))
    (tmp_path / attachment["filename"]).unlink()
    assert collection_status(store)["totals"] == {"articles": 1, "pdfs": 0}


@pytest.mark.parametrize("content_type", ["unspecified", None, "text/html"])
def test_acs_explicit_pdf_path_with_unspecified_content_type(tmp_path, content_type):
    item = article()
    if content_type is None:
        item["link"][0].pop("content-type")
    else:
        item["link"][0]["content-type"] = content_type
    client = Client(pages(item))
    result = collect_jacs(Store(tmp_path), client=client)
    assert result["status"] == "success"
    assert result["pdfs_saved"] == (0 if content_type == "text/html" else 1)
    assert bool(client.downloads) == (content_type != "text/html")
