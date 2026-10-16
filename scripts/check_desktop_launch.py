"""Check a real ordinary launch, without the launcher's --smoke-test path.

Examples:
  python scripts/check_desktop_launch.py release/Chembrain.exe
  python scripts/check_desktop_launch.py .venv/bin/python scripts/desktop.py --no-browser

Uses isolated default app data, a working directory with spaces, and only kills
processes started by this check. The EXE invocation uses no extra arguments.
"""
import argparse
import json
import os
import re
import signal
import subprocess
import tempfile
import time
import urllib.request
from pathlib import Path


def stop(process):
    if process.poll() is not None:
        return
    if os.name == 'nt':
        # A one-file PyInstaller EXE has a bootloader parent and a server child.
        subprocess.run(['taskkill', '/PID', str(process.pid), '/T', '/F'], capture_output=True, timeout=20, check=False)
    else:
        os.killpg(process.pid, signal.SIGTERM)
    try:
        process.wait(timeout=20)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait(timeout=10)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', nargs=argparse.REMAINDER)
    args = parser.parse_args()
    if not args.command:
        parser.error('Pass the executable or Python launcher command to check.')
    command = [str(Path(arg).absolute()) if Path(arg).is_file() else arg for arg in args.command]
    with tempfile.TemporaryDirectory(prefix='chembrain normal launch ') as temporary:
        folder = Path(temporary)
        log_path = folder / 'launch-output.log'
        env = {**os.environ, 'LOCALAPPDATA': str(folder / 'Local App Data'), 'XDG_DATA_HOME': str(folder / 'Local App Data')}
        with log_path.open('wb') as log:
            process = subprocess.Popen(command, cwd=folder, env=env, stdin=subprocess.DEVNULL,
                                       stdout=log, stderr=subprocess.STDOUT, start_new_session=os.name != 'nt')
            try:
                deadline = time.monotonic() + 90
                while True:
                    output = log_path.read_text(encoding='utf-8', errors='replace')
                    if process.poll() is not None:
                        raise RuntimeError(f'Ordinary launch exited with {process.returncode}:\n{output}')
                    match = re.search(r'Chembrain is running at (http://127\.0\.0\.1:\d+)', output)
                    if match:
                        url = match.group(1)
                        break
                    if time.monotonic() >= deadline:
                        raise RuntimeError(f'Ordinary launch did not become ready:\n{output}')
                    time.sleep(.2)
                opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))

                def get(path):
                    with opener.open(url + path, timeout=15) as response:
                        return response.read()

                assert json.loads(get('/api/health'))['chemistry'] == 'rdkit'
                workspace = json.loads(get('/api/workspace'))
                assert len(workspace['molecules']) == 14 and len(workspace['reactions']) == 6
                assert len(workspace['sources']) == 6 and all(s.get('doi') for s in workspace['sources'])
                html = get('/').decode('utf-8')
                assert '<html lang="en"' in html
                assets = re.findall(r'(?:src|href)="(/assets/[^\"]+)"', html)
                assert assets and all(get(asset) for asset in assets)
                assert b'<svg' in get(f"/api/molecules/{workspace['molecules'][0]['id']}/svg")
                assert process.poll() is None, log_path.read_text(encoding='utf-8', errors='replace')
            finally:
                stop(process)
    print('Ordinary launch passed without --smoke-test: local server, English UI and assets, RDKit SVG, 14 molecules, 6 reactions and DOI references.', flush=True)


if __name__ == '__main__':
    main()
