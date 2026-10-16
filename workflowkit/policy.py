"""Fail-closed edit, review, and receipt policy for the local workflow controller."""
from __future__ import annotations

import json
import os
from pathlib import Path, PurePosixPath
import re
import tempfile
from datetime import datetime, timezone
from uuid import uuid4

MAX_FILE_BYTES = 200 * 1024
MAX_TOTAL_BYTES = 1024 * 1024
DEFAULT_PROTECTED = ('.git', '.github', 'workflowkit', 'agents', 'RULEBOOK.md',
                     'wiki.md', 'config.json', '.env', 'credentials', 'secrets',
                     'scripts/check_desktop_launch.py', 'scripts/report_windows_build.sh',
                     'scripts/browser_smoke.py', 'tests', 'packaging')
RESERVED = re.compile(r'^(?:con|prn|aux|nul|com[1-9]|lpt[1-9])(?:\..*)?$', re.I)
SHA = re.compile(r'^[0-9a-f]{40}$')
CHECKSUM = re.compile(r'^[0-9a-fA-F]{64}\s+\*?[^\r\n]+$', re.M)
MARKERS = {
    'packaged_ui': 'WINDOWS_PACKAGED_UI_PASS',
    'restart_persistence': 'WINDOWS_RESTART_PERSISTENCE_PASS',
    'runtime_path_independence': 'WINDOWS_RUNTIME_PATH_INDEPENDENCE_PASS',
}


def _safe_path(value: str) -> str:
    if not isinstance(value, str) or not value or '\\' in value:
        raise ValueError('Edit paths must be nonempty, forward-slash relative paths.')
    if any(ord(char) < 32 for char in value) or any(char in value for char in ':*?"<>|'):
        raise ValueError('Invalid or Windows-unsafe path.')
    path = PurePosixPath(value)
    parts = value.split('/')
    if path.is_absolute() or any(part in ('', '.', '..') for part in parts):
        raise ValueError('Absolute paths, traversal, and path aliases are forbidden.')
    if any(part.endswith((' ', '.')) or RESERVED.fullmatch(part) for part in parts):
        raise ValueError('Reserved Windows names and trailing dots/spaces are forbidden.')
    return value


def _protected(path: str, protected_paths: list[str] | None) -> bool:
    parts = [part.casefold() for part in path.split('/')]
    protected = tuple(DEFAULT_PROTECTED) + tuple(protected_paths or ())
    folded = path.casefold()
    for item in protected:
        candidate = item.replace('\\', '/').strip('/').casefold()
        if folded == candidate or folded.startswith(candidate + '/'):
            return True
    # Credentials and control files are protected at every depth, not just root.
    for part in parts:
        if part in {'.git', '.github', '.agents', '.claude', '.codex', '.aws', '.ssh',
                    'workflowkit', 'agents', 'agents.md', 'claude.md', 'rulebook.md', 'wiki.md',
                    'config.json', 'credentials', 'credentials.json', 'secrets', 'secrets.json',
                    'id_rsa', 'id_ed25519', '.netrc', '_netrc', '.npmrc', '.pypirc'}:
            return True
        if part.startswith('.env') or part.endswith(('.pem', '.key', '.p12', '.pfx')):
            return True
    return False


def _validate_text_edits(files: list[dict], protected_paths: list[str] | None,
                         snapshot: bool = False) -> list[dict]:
    """Validate a complete author proposal before touching any repository files."""
    if not isinstance(files, list):
        raise ValueError('files must be a list.')
    result, seen, total = [], set(), 0
    for edit in files:
        if not isinstance(edit, dict) or set(edit) != {'path', 'content'}:
            raise ValueError('Every edit must contain exactly path and content.')
        path = _safe_path(edit['path'])
        if _protected(path, protected_paths) and not snapshot:
            raise ValueError(f'Author may not modify protected path: {path}')
        if snapshot and _sensitive_snapshot_path(path):
            raise ValueError(f'Sensitive files may not be materialized: {path}')
        key = path.casefold()
        if key in seen:
            raise ValueError('Duplicate or case-aliased edit paths.')
        seen.add(key)
        content = edit['content']
        if content is not None:
            if not isinstance(content, str) or '\x00' in content:
                raise ValueError('Edits must contain UTF-8 text or null for deletion.')
            try:
                size = len(content.encode('utf-8'))
            except UnicodeEncodeError as exc:
                raise ValueError('Invalid UTF-8 text.') from exc
            total += size
            if size > MAX_FILE_BYTES or total > MAX_TOTAL_BYTES:
                raise ValueError('Author proposal exceeds text size limits.')
        result.append({'path': path, 'content': content})
    return result


def validate_edits(files: list[dict], protected_paths: list[str] | None = None) -> list[dict]:
    """Validate author edits with non-removable intrinsic control-file protections."""
    return _validate_text_edits(files, protected_paths)


def _sensitive_snapshot_path(path: str) -> bool:
    for part in path.casefold().split('/'):
        if part in {'.git', '.aws', '.ssh', 'credentials', 'credentials.json',
                    'secrets', 'secrets.json', 'id_rsa', 'id_ed25519', '.netrc',
                    '_netrc', '.npmrc', '.pypirc', 'config.json'}:
            return True
        if part.startswith('.env') or part.endswith(('.pem', '.key', '.p12', '.pfx')):
            return True
    return False


def _target(root: Path, relative: str) -> Path:
    current = root
    for part in relative.split('/'):
        # Reject case aliases even when the controller itself runs on Linux.
        if current.is_dir():
            aliases = [p for p in current.iterdir() if p.name.casefold() == part.casefold()]
            if any(p.name != part for p in aliases):
                raise ValueError('Edit path aliases an existing filename by case.')
        current = current / part
        if current.is_symlink():
            raise ValueError('Symlink edit paths are forbidden.')
        if current.exists() and current != root / relative and not current.is_dir():
            raise ValueError('A path parent is not a directory.')
    if not current.resolve().is_relative_to(root):
        raise ValueError('Edit escapes repository root.')
    if current.exists() and not current.is_file():
        raise ValueError('Only regular project text files may be edited.')
    return current


def apply_edits(root: Path, files: list[dict]) -> None:
    """Apply validated edits; repository must be controller-owned and idle."""
    _apply_validated(root, validate_edits(files))


def materialize_snapshot(root: Path, snapshot: dict[str, str]) -> None:
    """Materialize trusted GitHub text context, never an author edit proposal.

    CI and policy source may be included for review, but credential files and Git
    administrative state must never be copied into an agent-visible snapshot.
    """
    if not isinstance(snapshot, dict) or not all(isinstance(v, str) for v in snapshot.values()):
        raise ValueError('Snapshot must map relative paths to UTF-8 text.')
    edits = _validate_text_edits(
        [{'path': path, 'content': content} for path, content in snapshot.items()],
        None, snapshot=True)
    _apply_validated(root, edits)


def _apply_validated(root: Path, edits: list[dict]) -> None:
    root = Path(root)
    if root.is_symlink() or not root.is_dir():
        raise ValueError('Repository root must be an existing nonsymlink directory.')
    root = root.resolve()
    targets = [_target(root, edit['path']) for edit in edits]
    paths = [PurePosixPath(edit['path']) for edit in edits]
    if any(a != b and (a in b.parents or b in a.parents) for a in paths for b in paths):
        raise ValueError('Proposal contains conflicting file and parent edits.')
    # Refuse overwriting arbitrary existing binaries, even with a text replacement.
    for target in targets:
        if target.exists():
            try:
                existing = target.read_bytes()
                if len(existing) > MAX_FILE_BYTES or b'\x00' in existing:
                    raise ValueError('Existing file is not an eligible project text file.')
                existing.decode('utf-8')
            except UnicodeDecodeError as exc:
                raise ValueError('Existing file is not UTF-8 text.') from exc
    for edit, target in zip(edits, targets):
        _target(root, edit['path'])
        if edit['content'] is None:
            target.unlink(missing_ok=True)
        else:
            atomic_text(target, edit['content'])


def _steps(receipt: dict) -> dict:
    value = receipt.get('steps', {})
    return value if isinstance(value, dict) else {}


def receipt_checks(receipt: dict) -> list[dict]:
    """Read explicit CI evidence; a green job never implies every behavior passed."""
    steps = _steps(receipt)
    succeeded = receipt.get('status') == 'success'
    package_ok = succeeded and steps.get('packaging') == 'success' and steps.get('validation') == 'success'
    built = package_ok and steps.get('artifact') == 'success'
    logs = receipt.get('logs', {})
    normal = logs.get('normal-launch', '') if isinstance(logs, dict) else ''
    lines = set(normal.splitlines()) if isinstance(normal, str) else set()
    checks = [{'name': 'windows_build', 'status': 'PASS' if built else 'NOT RUN'}]
    for name, marker in MARKERS.items():
        checks.append({'name': name, 'status': 'PASS' if package_ok and marker in lines else 'NOT RUN'})
    return checks


def _check_map(checks: object) -> dict | None:
    if not isinstance(checks, list):
        return None
    mapping = {}
    for check in checks:
        if not isinstance(check, dict) or not isinstance(check.get('name'), str):
            return None
        if check['name'] in mapping:
            return None
        mapping[check['name']] = check.get('status')
    return mapping


def review_approved(review: dict, commit: str, receipt: dict, required_checks: list[str]) -> bool:
    if not isinstance(review, dict) or not isinstance(receipt, dict):
        return False
    if not isinstance(commit, str) or not SHA.fullmatch(commit):
        return False
    if review.get('commit') != commit or receipt.get('commit') != commit:
        return False
    if review.get('verdict') != 'approved' or review.get('findings') != []:
        return False
    if receipt.get('status') != 'success':
        return False
    if not isinstance(receipt.get('artifact_url'), str) or not receipt['artifact_url'].startswith('https://github.com/'):
        return False
    checksums = receipt.get('checksums', '')
    if not isinstance(checksums, str) or not CHECKSUM.search(checksums):
        return False
    reviewed = _check_map(review.get('checks'))
    explicit = _check_map(receipt.get('checks', []))
    if reviewed is None or explicit is None:
        return False
    recorded = {**explicit, **{c['name']: c['status'] for c in receipt_checks(receipt)}}
    if not required_checks or len(set(required_checks)) != len(required_checks):
        return False
    for check in required_checks:
        if reviewed.get(check) != 'PASS' or recorded.get(check) != 'PASS':
            return False
    return True


def atomic_text(path: Path, content: str) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.is_symlink():
        raise ValueError('Cannot atomically replace a symlink.')
    fd, temporary = tempfile.mkstemp(prefix='.' + path.name + '.', dir=path.parent)
    try:
        with os.fdopen(fd, 'w', encoding='utf-8', newline='') as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        Path(temporary).unlink(missing_ok=True)


def atomic_json(path: Path, obj: object) -> None:
    atomic_text(path, json.dumps(obj, ensure_ascii=False, indent=2, allow_nan=False) + '\n')


def append_event(root: Path, event: dict) -> Path:
    """One immutable event per file avoids Box concurrent JSONL append conflicts."""
    now = datetime.now(timezone.utc)
    directory = Path(root) / 'events'
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / (now.strftime('%Y%m%dT%H%M%S.%fZ') + '-' + uuid4().hex + '.json')
    atomic_json(path, {**event, 'recorded_at': now.isoformat()})
    return path
