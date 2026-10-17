"""Bind the triggering workflow, actual built tree and exact public-library bytes."""
import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

FIELDS = {'schema_version', 'workflow_commit', 'built_commit', 'library_sha256'}

def validate_identity(value, workflow_commit=None):
    if not isinstance(value, dict) or set(value) != FIELDS or type(value['schema_version']) is not int or value['schema_version'] != 1:
        raise ValueError('Invalid web build identity')
    for field, size in [('workflow_commit', 40), ('built_commit', 40), ('library_sha256', 64)]:
        if not isinstance(value[field], str) or not re.fullmatch('[0-9a-f]{'+str(size)+'}', value[field]):
            raise ValueError('Invalid web identity field: '+field)
    if workflow_commit and value['workflow_commit'] != workflow_commit:
        raise ValueError('Web identity belongs to a different workflow source')
    return dict(value)

def capture_identity(root, workflow_commit):
    root = Path(root)
    def git(*args):
        return subprocess.check_output(['git', *args], cwd=root, text=True).strip()
    built = git('rev-parse', 'HEAD')
    # Collection may commit normalized data; it must not quietly change app code.
    if any(p != 'public/library.json' for p in git('diff', '--name-only', workflow_commit, built).splitlines()):
        raise ValueError('Built code differs from the triggering workflow')
    if git('status', '--porcelain', '--untracked-files=no'):
        raise ValueError('Commit tracked changes before recording the built tree')
    identity = {'schema_version': 1, 'workflow_commit': workflow_commit, 'built_commit': built,
                'library_sha256': hashlib.sha256((root/'public/library.json').read_bytes()).hexdigest()}
    return validate_identity(identity, workflow_commit)

def resolve_identity(current, previous, workflow_commit):
    """Later fresh checkouts may preserve, but cannot replace, the captured build."""
    if current:
        value = validate_identity(current, workflow_commit)
        if previous and validate_identity(previous, workflow_commit) != value:
            raise ValueError('Build identity changed within the same run')
        return value
    return validate_identity(previous, workflow_commit) if previous else None

def verify_payload(expected, marker, library_bytes, html_bytes):
    expected = validate_identity(expected)
    if validate_identity(marker) != expected:
        raise ValueError('Published build identity is stale or different')
    if hashlib.sha256(library_bytes).hexdigest() != expected['library_sha256']:
        raise ValueError('Published library digest differs from the built data')
    if b'<html lang="en"' not in html_bytes:
        raise ValueError('Published HTML is unavailable')
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from paper_pipeline.schema import validate
    validate(json.loads(library_bytes))

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workflow-commit', required=True)
    parser.add_argument('--root', type=Path, default=Path('.'))
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    identity = capture_identity(args.root, args.workflow_commit)
    args.out.write_text(json.dumps(identity, separators=(',', ':'))+'\n')
    print(json.dumps(identity, separators=(',', ':')))

if __name__ == '__main__':
    main()
