"""Verify ordinary launch, browser intent, persistence and optionally the real UI.

python scripts/check_desktop_launch.py --browser-ui --restricted-runtime release/Chembrain.exe
python scripts/check_desktop_launch.py .venv/bin/python scripts/desktop.py --no-browser

The EXE receives zero arguments. BROWSER uses a short-lived OS shell probe;
Playwright separately exercises the UI, avoiding external browser profile locks.
Default app data is isolated and reused across an actual process restart.
"""
import argparse
import json
import os
import re
import shutil
import signal
import subprocess
import sys
import tempfile
import time
import urllib.request
from contextlib import contextmanager
from pathlib import Path


def browser_command(record: Path) -> str:
    """Use the documented BROWSER setting to record a real webbrowser.open call."""
    escaped = record.as_posix().replace("'", "''" if os.name == 'nt' else "'\"'\"'")
    if os.name == 'nt':
        powershell = Path(os.environ['SystemRoot']) / 'System32/WindowsPowerShell/v1.0/powershell.exe'
        return f'"{powershell.as_posix()}" -NoProfile -NonInteractive -Command "Set-Content -LiteralPath \'{escaped}\' -Encoding ascii -Value \'%s\'"'
    return f'"/bin/sh" -c "echo \'%s\' > \'{escaped}\'"'


def stop(process):
    if process.poll() is not None:
        return
    if os.name == 'nt':
        subprocess.run(['taskkill', '/PID', str(process.pid), '/T', '/F'], capture_output=True, timeout=20, check=False)
    else:
        os.killpg(process.pid, signal.SIGTERM)
    try:
        process.wait(timeout=20)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait(timeout=10)


@contextmanager
def launch(command, folder, env, attempt):
    record = folder / 'browser-request.txt'
    record.unlink(missing_ok=True)
    log_path = folder / f'launch-{attempt}.log'
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
                if match and ('--no-browser' in command or record.exists()):
                    url = match.group(1)
                    if '--no-browser' not in command:
                        assert record.read_text(encoding='ascii').strip() == url
                    break
                if time.monotonic() >= deadline:
                    raise RuntimeError(f'Ordinary launch or browser intent was not ready:\n{output}')
                time.sleep(.2)
            opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))

            def request(path, body=None, method=None):
                data = None if body is None else json.dumps(body).encode('utf-8')
                req = urllib.request.Request(url + path, data=data, method=method, headers={'Content-Type':'application/json'})
                with opener.open(req, timeout=15) as response:
                    return response.read()

            assert json.loads(request('/api/health'))['chemistry'] == 'rdkit'
            html = request('/').decode('utf-8')
            assert '<html lang="en"' in html
            assets = re.findall(r'(?:src|href)="(/assets/[^\"]+)"', html)
            assert assets and all(request(asset) for asset in assets)
            yield url, request
            assert process.poll() is None, log_path.read_text(encoding='utf-8', errors='replace')
        finally:
            stop(process)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--browser-ui', action='store_true')
    parser.add_argument('--restricted-runtime', action='store_true')
    parser.add_argument('command', nargs=argparse.REMAINDER)
    args = parser.parse_args()
    if not args.command:
        parser.error('Pass the executable or Python launcher command to check.')
    command = [str(Path(arg).absolute()) if Path(arg).is_file() else arg for arg in args.command]
    with tempfile.TemporaryDirectory(prefix='chembrain normal launch ') as temporary:
        folder = Path(temporary)
        env = {**os.environ, 'LOCALAPPDATA':str(folder / 'Local App Data'), 'XDG_DATA_HOME':str(folder / 'Local App Data'),
               'BROWSER':browser_command(folder / 'browser-request.txt')}
        if args.restricted_runtime:
            if os.name != 'nt':
                parser.error('Restricted runtime validation targets the Windows EXE.')
            root = Path(os.environ['SystemRoot'])
            env['PATH'] = os.pathsep.join(map(str, [root / 'System32']))
            for name in ('PYTHONHOME','PYTHONPATH','VIRTUAL_ENV','CONDA_PREFIX','NODE_PATH'):
                env.pop(name, None)
            for executable in ('python','python3','py','node','npm'):
                assert shutil.which(executable, path=env['PATH']) is None, executable
            print('Runtime check: Python/Node launchers absent from child PATH. This is not a clean Windows VM.', flush=True)
        with launch(command, folder, env, 1) as (url, request):
            initial = json.loads(request('/api/workspace'))
            assert len(initial['molecules']) == 14 and len(initial['reactions']) == 6
            assert len(initial['sources']) == 6 and all(s.get('doi') for s in initial['sources'])
            assert b'<svg' in request(f"/api/molecules/{initial['molecules'][0]['id']}/svg")
            if args.browser_ui:
                from browser_smoke import exercise_ui
                exercise_ui(url)
            created = json.loads(request('/api/molecules', {'name':'Persistent user molecule','smiles':'CCO','notes':'Persisted user notes','availability':'in_stock'}, 'POST'))
            original = initial['molecules'][0]
            request('/api/molecules/' + original['id'], {**original,'name':'User-corrected literature name','notes':'User correction must survive restart.','availability':'in_stock'}, 'PUT')
            snapshot = json.loads(request('/api/workspace'))
            print('First ordinary launch: API, structures and user changes verified.', flush=True)
        with launch(command, folder, env, 2) as (url, request):
            restored = json.loads(request('/api/workspace'))
            assert restored == snapshot, 'An EXE restart changed or reseeded existing user data.'
            assert any(m['id'] == created['id'] and m['notes'] == 'Persisted user notes' for m in restored['molecules'])
            if args.browser_ui:
                from browser_smoke import verify_restarted_ui
                verify_restarted_ui(url)
            print('Second ordinary launch: same default data folder, all records and user corrections preserved.', flush=True)
    if os.name == 'nt':
        if args.browser_ui:
            print('WINDOWS_PACKAGED_UI_PASS', flush=True)
        print('WINDOWS_RESTART_PERSISTENCE_PASS', flush=True)
        if args.restricted_runtime:
            print('WINDOWS_RUNTIME_PATH_INDEPENDENCE_PASS', flush=True)
    print('Ordinary launch validation passed: browser request, UI/assets, RDKit and process restart with existing data. Temporary files cleaned.', flush=True)


if __name__ == '__main__':
    main()
