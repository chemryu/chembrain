"""Double-click launcher; PyInstaller bundles Python, RDKit, the API and UI."""
import argparse
import json
import logging
import os
import socket
import sys
import tempfile
import threading
import time
import urllib.request
import webbrowser
from pathlib import Path


def default_data_dir() -> Path:
    if sys.platform == "win32":
        return Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData/Local")) / "Chembrain"
    return Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local/share")) / "chembrain"


def main():
    parser = argparse.ArgumentParser(description="Chembrain local desktop launcher")
    parser.add_argument("--data-dir", type=Path, default=default_data_dir())
    parser.add_argument("--no-browser", action="store_true")
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument("--smoke-test", action="store_true", help="Verify the packaged API, structures, DOI examples and UI, then exit")
    modes.add_argument("--sync-jacs", action="store_true", help="Collect JACS bibliography and verified open PDFs, then exit without opening the app")
    modes.add_argument("--install-jacs-schedule", action="store_true")
    modes.add_argument("--remove-jacs-schedule", action="store_true")
    parser.add_argument("--weekday", default="Monday", choices=['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday'])
    parser.add_argument("--time", dest="schedule_time", default="09:00")
    parser.add_argument("--metadata-only", action="store_true")
    parser.add_argument("--days", type=int)
    parser.add_argument("--max-pages", type=int, default=20)
    args = parser.parse_args()
    if args.metadata_only and not args.sync_jacs:
        parser.error("--metadata-only requires --sync-jacs")
    if args.days is not None and not 1 <= args.days <= 366:
        parser.error("--days must be between 1 and 366")
    if not 1 <= args.max_pages <= 20:
        parser.error("--max-pages must be between 1 and 20")
    if args.sync_jacs or args.install_jacs_schedule or args.remove_jacs_schedule:
        if not getattr(sys, "frozen", False):
            sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
        from server.store import Store
        store = Store(args.data_dir)
        if args.sync_jacs:
            from server.jacs_collection import collect_jacs, CollectionBusy
            try:
                result = collect_jacs(store, metadata_only=args.metadata_only, days=args.days, max_pages=args.max_pages)
            except CollectionBusy:
                print(json.dumps({"status":"already_running"}), flush=True)
                return 0
            print(json.dumps(result, ensure_ascii=True), flush=True)
            return 0 if result['status'] == 'success' else 1
        from server.collection_schedule import configure_schedule
        result = configure_schedule(store, args.install_jacs_schedule, args.weekday, args.schedule_time)
        print(json.dumps(result), flush=True)
        return 0
    if args.smoke_test:
        with tempfile.TemporaryDirectory(prefix="chembrain-packaged-smoke-") as temporary:
            run(Path(temporary), no_browser=True, smoke_test=True)
    else:
        run(args.data_dir, no_browser=args.no_browser)


def run(data_dir: Path, no_browser: bool, smoke_test: bool = False):
    data_dir.mkdir(parents=True, exist_ok=True)
    os.environ["CHEMBRAIN_DATA_DIR"] = str(data_dir)
    os.environ["CHEMBRAIN_SEED_LITERATURE"] = "1"
    os.environ["CHEMBRAIN_SEED_DEMO"] = "0"
    logger = logging.getLogger()
    handler = logging.FileHandler(data_dir / "chembrain.log", encoding="utf-8")
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)
    try:
        serve(data_dir, no_browser, smoke_test)
    finally:
        logger.removeHandler(handler)
        handler.close()


def collector_fixture_smoke(data_dir: Path):
    """Exercise the bundled collector without publisher access or user data."""
    import pymupdf
    from server.jacs_collection import ATTACHMENTS, collect_jacs, collection_status
    from server.store import Store

    doi = "10.1021/jacs.packaging-fixture"
    article = {
        "DOI": doi, "type": "journal-article", "ISSN": ["0002-7863"],
        "title": ["Local packaging fixture"],
        "published": {"date-parts": [[2026, 1, 1]]},
        "license": [{"URL": "https://creativecommons.org/licenses/by/4.0/",
                     "content-version": "vor", "start": {"date-time": "2020-01-01T00:00:00Z"}}],
        "link": [{"URL": "https://pubs.acs.org/doi/pdf/" + doi,
                  "content-type": "application/pdf", "content-version": "vor"}],
    }
    with pymupdf.open() as document:
        document.new_page().insert_text((50, 50), "Local collector fixture")
        pdf = document.tobytes()

    class FixtureClient:
        def page(self, start, cursor):
            return {"items": [article], "total-results": 1}

        def pdf(self, candidate):
            return pdf

    store = Store(data_dir / "collector-fixture")
    result = collect_jacs(store, client=FixtureClient())
    assert result["status"] == "success" and result["added"] == result["pdfs_saved"] == 1
    assert store.all("source")[0]["doi"] == doi
    attachment = store.get_metadata(ATTACHMENTS)[doi]
    assert attachment["page_count"] == 1
    assert attachment["supplied_url"] == article["link"][0]["URL"]
    assert attachment["license"] == article["license"][0]["URL"]
    assert attachment["license_start"] and attachment["license_end"] is None
    assert attachment["content_version"] == "vor" and attachment["upstream_type"] == "journal-article"
    assert collection_status(store)["totals"] == {"articles": 1, "pdfs": 1}
    repeat = collect_jacs(store, client=FixtureClient())
    assert repeat["status"] == "success" and repeat["existing"] == 1 and repeat["pdfs_saved"] == 0
    print("JACS_COLLECTOR_FIXTURE_PASS: bundled metadata, licensed PDF and idempotent storage; no network.", flush=True)


def serve(data_dir: Path, no_browser: bool, smoke_test: bool):
    if not getattr(sys, "frozen", False):
        sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    # Bind once and give that same socket to Uvicorn, avoiding port races.
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as listener:
        listener.bind(("127.0.0.1", 0))
        listener.listen(128)
        port = listener.getsockname()[1]
        url = f"http://127.0.0.1:{port}"
        import uvicorn
        from server.app import app

        server = uvicorn.Server(uvicorn.Config(app, host="127.0.0.1", port=port, log_config=None, access_log=False))
        outcome = {"error": None}

        def ready():
            try:
                opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
                deadline = time.monotonic() + 60
                while not server.started:
                    if time.monotonic() > deadline:
                        raise RuntimeError("The local server did not start within 60 seconds")
                    time.sleep(.1)
                if smoke_test:
                    def get(path):
                        with opener.open(url + path, timeout=15) as response:
                            return response.read()
                    assert json.loads(get("/api/health"))["chemistry"] == "rdkit"
                    workspace = json.loads(get("/api/workspace"))
                    assert len(workspace["molecules"]) == 14 and len(workspace["reactions"]) == 6
                    assert all(s.get("doi") and not s.get("pages") for s in workspace["sources"])
                    assert b"<svg" in get(f"/api/molecules/{workspace['molecules'][0]['id']}/svg")
                    assert b'<html lang="en"' in get("/")
                    for asset in (Path(__import__('server.app', fromlist=['ROOT']).ROOT) / "dist/assets").iterdir():
                        assert get("/assets/" + asset.name)
                    collector_fixture_smoke(data_dir)
                    print("Packaged smoke test passed: English UI, RDKit SVG, 14 molecules, 6 reactions, DOI-only references.", flush=True)
                    server.should_exit = True
                else:
                    print(f"Chembrain is running at {url}\nData: {data_dir}\nKeep this window open. Close it or press Ctrl+C to quit.", flush=True)
                    if not no_browser:
                        webbrowser.open(url)
            except BaseException as error:
                outcome["error"] = error
                logging.exception("Launcher readiness failed")
                server.should_exit = True
        worker = threading.Thread(target=ready, daemon=True)
        worker.start()
        server.run(sockets=[listener])
        worker.join(timeout=20)
        if outcome["error"]:
            raise RuntimeError(str(outcome["error"])) from outcome["error"]
        if not server.started:
            raise RuntimeError("Unable to start the local server")


if __name__ == "__main__":
    try:
        raise SystemExit(main() or 0)
    except Exception as error:
        logging.exception("Chembrain failed to start")
        print(f"Chembrain could not start: {error}", file=sys.stderr)
        if getattr(sys, "frozen", False) and not any(arg in sys.argv for arg in ("--smoke-test", "--sync-jacs", "--install-jacs-schedule", "--remove-jacs-schedule")):
            input("Press Enter to close...")
        raise SystemExit(1)
