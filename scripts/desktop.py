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
    parser.add_argument("--smoke-test", action="store_true", help="Verify the packaged API, structures, DOI examples and UI, then exit")
    args = parser.parse_args()
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
        main()
    except Exception as error:
        logging.exception("Chembrain failed to start")
        print(f"Chembrain could not start: {error}", file=sys.stderr)
        if getattr(sys, "frozen", False) and "--smoke-test" not in sys.argv:
            input("Press Enter to close...")
        raise SystemExit(1)
