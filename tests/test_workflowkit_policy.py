import json

import pytest

from workflowkit.policy import (apply_edits, append_event, atomic_json, materialize_snapshot, receipt_checks,
                                review_approved, validate_edits)


COMMIT = 'a' * 40
REQUIRED = ['windows_build', 'packaged_ui', 'restart_persistence', 'runtime_path_independence']


def valid_gate():
    checks = [{'name': key, 'status': 'PASS'} for key in REQUIRED]
    review = {'commit': COMMIT, 'verdict': 'approved', 'findings': [], 'checks': checks}
    receipt = {'commit': COMMIT, 'status': 'success',
               'steps': {'packaging': 'success', 'validation': 'success', 'artifact': 'success'},
               'artifact_url': 'https://github.com/chemryu/chembrain/actions/runs/1/artifacts/1',
               'checksums': 'b' * 64 + '  Chembrain-Windows-x64.zip\n',
               'logs': {'normal-launch': '\n'.join([
                   'WINDOWS_PACKAGED_UI_PASS', 'WINDOWS_RESTART_PERSISTENCE_PASS',
                   'WINDOWS_RUNTIME_PATH_INDEPENDENCE_PASS'])}}
    return review, receipt


@pytest.mark.parametrize('path', ['/tmp/file', '../file', 'a/../file', './file', 'a//file',
    'C:/temp/file', 'C:\\temp\\file', '\\\\server\\share', '//server/share',
    'foo.txt:stream', 'NUL', 'con.txt', 'a/LPT1.py', 'a./file', 'a /file',
    '.git/config', '.github/workflows/a.yml', 'server/.env.production',
    'nested/credentials.json', 'nested/id_rsa', 'wiki.md', 'workflowkit/policy.py',
    'agents/author.md', 'RULEBOOK.md', 'nested/secrets.json', 'tests/test_gate.py',
    'packaging/build.spec', 'scripts/check_desktop_launch.py',
    'scripts/report_windows_build.sh', 'scripts/browser_smoke.py'])
def test_unsafe_author_paths(path):
    with pytest.raises(ValueError):
        validate_edits([{'path': path, 'content': 'x'}])


def test_edit_validation_and_limits():
    assert validate_edits([]) == []
    assert validate_edits([{'path': 'src/app.ts', 'content': None}]) == [{'path': 'src/app.ts', 'content': None}]
    for files in ([{'path': 'a', 'content': '1'}, {'path': 'A', 'content': None}],
                  [{'path': 'a', 'content': '\0'}],
                  [{'path': 'a', 'content': 'a' * (200 * 1024 + 1)}],
                  [{'path': f'{i}.txt', 'content': 'a' * (200 * 1024)} for i in range(6)]):
        with pytest.raises(ValueError):
            validate_edits(files)
    with pytest.raises(ValueError):
        validate_edits([{'path': 'src/app.py', 'content': 'x'}], ['src'])
    with pytest.raises(ValueError):
        validate_edits([{'path': 'tests/test_gate.py', 'content': 'x'}], [])


def test_trusted_snapshot_can_include_validator_and_controller_source(tmp_path):
    snapshot = {'.github/workflows/windows.yml': 'jobs: {}\n',
                'tests/test_app.py': 'assert True\n',
                'workflowkit/policy.py': '# trusted policy source\n',
                'RULEBOOK.md': '# Rules\n'}
    materialize_snapshot(tmp_path, snapshot)
    assert all((tmp_path / path).read_text(encoding='utf-8') == value for path, value in snapshot.items())


@pytest.mark.parametrize('path', ['.git/config', '.env.local', '.aws/credentials',
                                  'nested/credentials.json', '.ssh/config',
                                  'secrets.json', '../escape', 'C:/escape',
                                  'x:stream', 'NUL', 'config.json'])
def test_snapshot_never_materializes_credentials_or_unsafe_paths(tmp_path, path):
    with pytest.raises(ValueError):
        materialize_snapshot(tmp_path, {path: 'sensitive'})


def test_snapshot_enforces_text_size_and_symlink_limits(tmp_path):
    (tmp_path / 'linked').symlink_to(tmp_path.parent, target_is_directory=True)
    with pytest.raises(ValueError):
        materialize_snapshot(tmp_path, {'linked/escape.py': 'x'})
    with pytest.raises(ValueError):
        materialize_snapshot(tmp_path, {'large.py': 'a' * (200 * 1024 + 1)})
    with pytest.raises(ValueError):
        materialize_snapshot(tmp_path, {'binary.py': '\x00'})
    with pytest.raises(ValueError):
        materialize_snapshot(tmp_path, {'delete.py': None})


def test_safe_apply_preflights_entire_proposal(tmp_path):
    outside = tmp_path / 'outside'
    outside.mkdir()
    root = tmp_path / 'repo'
    root.mkdir()
    (root / 'link').symlink_to(outside, target_is_directory=True)
    with pytest.raises(ValueError):
        apply_edits(root, [{'path': 'good.py', 'content': 'yes'},
                           {'path': 'link/escaped.py', 'content': 'no'}])
    assert not (root / 'good.py').exists()
    assert not (outside / 'escaped.py').exists()
    apply_edits(root, [{'path': 'src/app.py', 'content': 'print(1)\n'}])
    assert (root / 'src/app.py').read_text(encoding='utf-8') == 'print(1)\n'
    with pytest.raises(ValueError):
        apply_edits(root, [{'path': 'SRC/app.py', 'content': 'alias'}])
    with pytest.raises(ValueError):
        apply_edits(root, [{'path': 'x', 'content': 'a'}, {'path': 'x/y', 'content': 'b'}])
    (root / 'binary').write_bytes(b'\0binary')
    with pytest.raises(ValueError):
        apply_edits(root, [{'path': 'binary', 'content': None}])
    apply_edits(root, [{'path': 'src/app.py', 'content': None}])
    assert not (root / 'src/app.py').exists()


def test_review_gate_accepts_only_complete_matching_evidence():
    review, receipt = valid_gate()
    assert review_approved(review, COMMIT, receipt, REQUIRED)
    assert all(c['status'] == 'PASS' for c in receipt_checks(receipt))


@pytest.mark.parametrize('mutation', [
    lambda v, r: v.update(commit='c' * 40),
    lambda v, r: r.update(commit='c' * 40),
    lambda v, r: v.update(verdict='APPROVED'),
    lambda v, r: v.update(findings=[{'severity': 'low', 'message': 'still open'}]),
    lambda v, r: v.pop('findings'),
    lambda v, r: r.update(status='failure'),
    lambda v, r: r['steps'].update(packaging='failure'),
    lambda v, r: r['steps'].update(artifact='skipped'),
    lambda v, r: r.update(artifact_url=None),
    lambda v, r: r.update(checksums='not a checksum'),
    lambda v, r: r.update(logs={}),
    lambda v, r: r.update(logs={'normal-launch': 'everything PASS'}),
    lambda v, r: v['checks'][0].update(status='NOT RUN'),
    lambda v, r: v['checks'].pop(),
    lambda v, r: v['checks'].append(dict(v['checks'][0])),
    lambda v, r: r.update(checks=[{'name': 'packaged_ui', 'status': 'PASS'}], logs={}),
])
def test_review_gate_rejects_missing_stale_and_fabricated_green_flags(mutation):
    review, receipt = valid_gate()
    mutation(review, receipt)
    assert not review_approved(review, COMMIT, receipt, REQUIRED)


def test_marker_must_be_exact_and_each_behavior_has_separate_evidence():
    review, receipt = valid_gate()
    receipt['logs']['normal-launch'] = 'WINDOWS_PACKAGED_UI_PASS\nMaybe WINDOWS_RESTART_PERSISTENCE_PASS\n'
    result = {item['name']: item['status'] for item in receipt_checks(receipt)}
    assert result == {'windows_build': 'PASS', 'packaged_ui': 'PASS',
                      'restart_persistence': 'NOT RUN', 'runtime_path_independence': 'NOT RUN'}
    assert not review_approved(review, COMMIT, receipt, REQUIRED)


def test_atomic_records_and_journal(tmp_path):
    config = tmp_path / 'state.json'
    atomic_json(config, {'hello': '안녕'})
    assert json.loads(config.read_text(encoding='utf-8')) == {'hello': '안녕'}
    first = append_event(tmp_path, {'type': 'review_received', 'commit': COMMIT})
    second = append_event(tmp_path, {'type': 'review_received', 'commit': COMMIT})
    assert first != second
    assert json.loads(first.read_text(encoding='utf-8'))['type'] == 'review_received'
    assert len(list((tmp_path / 'events').glob('*.json'))) == 2
