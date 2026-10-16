"""Gateway tests never invoke a live API, push a commit, or publish a release."""
import base64
import hashlib
import io
import json
import stat
import urllib.error
import urllib.request
import zipfile
from unittest.mock import Mock

import pytest

from workflowkit.github import GitHub, GitHubError, StaleBranchError, _SafeRedirect
from workflowkit.providers import AIProviders, ProviderError

SHA = 'a' * 40
OTHER = 'b' * 40


def zip_bytes(files):
    result = io.BytesIO()
    with zipfile.ZipFile(result, 'w') as archive:
        for name, content in files.items():
            archive.writestr(name, content)
    return result.getvalue()


def github():
    return GitHub('SECRET-token', 'owner/repo', 'feature/branch')


def test_snapshot_ignores_caches_binary_and_rejects_traversal():
    client = github()
    client._request = Mock(return_value=zip_bytes({
        'owner-repo-sha/src/a.py': 'print(1)', 'owner-repo-sha/.venv/x.py': 'no',
        'owner-repo-sha/test.png': b'PNG', 'owner-repo-sha/src/b.py': b'\x00binary'}))
    assert client.snapshot(SHA) == {'src/a.py': 'print(1)'}
    client._request.return_value = zip_bytes({'owner-repo-sha/../escape.py': 'bad'})
    with pytest.raises(GitHubError, match='Unsafe'):
        client.snapshot(SHA)


def test_snapshot_rejects_symlink_and_size_limit():
    client = github()
    archive = io.BytesIO()
    with zipfile.ZipFile(archive, 'w') as bundle:
        info = zipfile.ZipInfo('root/evil.py')
        info.create_system = 3
        info.external_attr = (stat.S_IFLNK | 0o777) << 16
        bundle.writestr(info, '/etc/passwd')
    client._request = Mock(return_value=archive.getvalue())
    with pytest.raises(GitHubError, match='symlink'):
        client.snapshot(SHA)
    client.max_text_bytes = 3
    client._request.return_value = zip_bytes({'root/a.py': '1234'})
    with pytest.raises(GitHubError, match='limit'):
        client.snapshot(SHA)


def test_commit_checks_branch_and_updates_non_force():
    client = github()
    client.head = Mock(side_effect=[SHA, SHA])
    client._request = Mock(side_effect=[{'sha': 'blob'}, {'tree': {'sha': 'base-tree'}},
                                       {'sha': 'new-tree'}, {'sha': OTHER}, {}])
    assert client.commit_files(SHA, [{'path': 'src/a.py', 'content': 'hello'}], 'Fix') == OTHER
    call = client._request.call_args
    assert call.args[0] == '/git/refs/heads/feature%2Fbranch'
    assert call.args[1] == {'sha': OTHER, 'force': False}
    assert call.kwargs['method'] == 'PATCH'
    client.head = Mock(return_value=OTHER)
    client._request.reset_mock()
    with pytest.raises(StaleBranchError):
        client.commit_files(SHA, [{'path': 'a.py', 'content': 'x'}], 'Fix')
    client._request.assert_not_called()


def test_commit_checks_branch_again_after_objects_are_created():
    client = github()
    client.head = Mock(side_effect=[SHA, OTHER])
    client._request = Mock(side_effect=[{'sha': 'blob'}, {'tree': {'sha': 'tree'}}, {'sha': 'tree2'}, {'sha': OTHER}])
    with pytest.raises(StaleBranchError):
        client.commit_files(SHA, [{'path': 'a.py', 'content': 'x'}], 'fix')
    assert not any(call.kwargs.get('method') == 'PATCH' for call in client._request.call_args_list)


def test_receipt_ignores_other_commit_and_pins_status_files():
    client = github()
    client._request = Mock(return_value={'object': {'sha': OTHER}})
    client._receipt_file = Mock(return_value=json.dumps({'commit': OTHER}))
    assert client.receipt(SHA) is None
    checksum = 'c' * 64 + '  Chembrain-Windows-x64.zip\n'
    client._receipt_file = Mock(side_effect=[json.dumps({'commit': SHA, 'status': 'success'}),
                                           'API PASS', 'LAUNCH PASS', 'SMOKE PASS', checksum])
    receipt = client.receipt(SHA)
    assert receipt['_receipt_sha'] == OTHER
    assert receipt['sha256'] == 'c' * 64
    assert receipt['logs']['normal-launch'] == 'LAUNCH PASS'
    assert all(call.args[1] == OTHER for call in client._receipt_file.call_args_list)


def artifact_fixture():
    inner = zip_bytes({'Chembrain.exe': b'MZ fake executable'})
    digest = hashlib.sha256(inner).hexdigest()
    sums = digest + '  Chembrain-Windows-x64.zip\n'
    outer = zip_bytes({'Chembrain-Windows-x64.zip': inner, 'SHA256SUMS.txt': sums})
    receipt = {'status': 'success', 'commit': SHA, 'artifact_url':
               'https://github.com/owner/repo/actions/runs/12/artifacts/34', 'checksums': sums, 'sha256': digest}
    metadata = {'expired': False, 'expires_at': '2099-01-01T00:00:00Z',
                'workflow_run': {'id': 12, 'head_sha': SHA},
                'digest': 'sha256:' + hashlib.sha256(outer).hexdigest()}
    return inner, outer, receipt, metadata


def test_artifact_validates_run_commit_outer_digest_and_inner_checksum():
    inner, outer, receipt, metadata = artifact_fixture()
    client = github()
    client._request = Mock(side_effect=[metadata, outer])
    assert client.artifact(receipt) == inner
    metadata['workflow_run']['head_sha'] = OTHER
    client._request = Mock(return_value=metadata)
    with pytest.raises(GitHubError, match='different commit'):
        client.artifact(receipt)
    assert client._request.call_count == 1


def test_artifact_rejects_digest_mismatch_and_receipt_checksum_disagreement():
    _, outer, receipt, metadata = artifact_fixture()
    client = github()
    client._request = Mock(side_effect=[metadata, outer + b'changed'])
    with pytest.raises(GitHubError, match='digest mismatch'):
        client.artifact(receipt)
    receipt['sha256'] = '0' * 64
    client._request = Mock(side_effect=[metadata, outer])
    with pytest.raises(GitHubError, match='immutable receipt'):
        client.artifact(receipt)


def test_redirect_never_forwards_auth_across_hosts():
    request = urllib.request.Request('https://api.github.com/archive',
                                     headers={'Authorization': 'Bearer SECRET-token'})
    redirected = _SafeRedirect().redirect_request(request, None, 302, 'Found', {}, 'https://storage.example/archive')
    assert not redirected.has_header('Authorization')
    with pytest.raises(GitHubError, match='non-HTTPS'):
        _SafeRedirect().redirect_request(request, None, 302, 'Found', {}, 'http://storage.example/archive')


def test_provider_requests_use_distinct_headers_and_structured_outputs():
    providers = AIProviders('openai-secret', 'anthropic-secret', 'author-model', 'reviewer-model')
    providers._post = Mock(return_value={'status': 'completed', 'output': [{'content': [
        {'type': 'output_text', 'text': json.dumps({'summary': 'Fix', 'files': [{'path': 'a.py', 'content': None}]})}]}]})
    assert providers.author({'commit': SHA})['files'][0]['content'] is None
    url, headers, payload = providers._post.call_args.args
    assert url == 'https://api.openai.com/v1/responses'
    assert headers == {'Authorization': 'Bearer openai-secret'}
    assert payload['text']['format']['strict'] is True
    report = {'commit': SHA, 'verdict': 'changes_requested', 'findings': [{'severity': 'high', 'message': 'Crash'}],
              'checks': [{'name': 'launch', 'status': 'FAIL'}], 'summary': 'Needs fix'}
    providers._post.return_value = {'stop_reason': 'tool_use', 'content': [
        {'type': 'tool_use', 'name': 'review_result', 'input': report}]}
    assert providers.review({'commit': SHA}) == report
    _, headers, payload = providers._post.call_args.args
    assert headers['x-api-key'] == 'anthropic-secret'
    assert payload['tool_choice']['name'] == 'review_result'
    assert 'openai-secret' not in json.dumps(payload)


def test_provider_fails_closed_on_truncated_or_invalid_reports():
    providers = AIProviders('one', 'two', 'author', 'reviewer')
    providers._post = Mock(return_value={'status': 'incomplete', 'output': []})
    with pytest.raises(ProviderError, match='did not complete'):
        providers.author({})
    providers._post.return_value = {'stop_reason': 'max_tokens', 'content': []}
    with pytest.raises(ProviderError, match='invalid report'):
        providers.review({})


def test_http_errors_do_not_leak_credentials(monkeypatch):
    secret = 'DO-NOT-LEAK'
    def fail(*args, **kwargs):
        raise urllib.error.HTTPError('https://example/' + secret, 401, secret, {}, None)
    monkeypatch.setattr(urllib.request, 'urlopen', fail)
    with pytest.raises(ProviderError) as caught:
        AIProviders._post('https://api.openai.com/v1/responses', {'Authorization': secret}, {})
    assert secret not in str(caught.value)
    client = github()
    client.opener.open = fail
    with pytest.raises(GitHubError) as caught:
        client.head()
    assert secret not in str(caught.value)


def test_snapshot_excludes_sensitive_files_before_size_counting_and_agent_context():
    client = github()
    client.max_text_bytes = 10
    secret = 'PRIVATE-CREDENTIAL-NEVER-SEND'
    sensitive = ['.npmrc', '.env', '.env.local', 'credentials.json', 'secrets.json',
                 'config.json', '.aws/config.json', '.ssh/settings.json', '.netrc',
                 'nested/.ENV.production.json', 'credentials/notes.md', 'secrets/README.md',
                 'nested/certificate.pem', 'nested/private.key', '.pypirc']
    files = {'root/' + path: secret * 100 for path in sensitive}
    files['root/src/a.py'] = 'print(1)'
    client._request = Mock(return_value=zip_bytes(files))
    snapshot = client.snapshot(SHA)
    assert snapshot == {'src/a.py': 'print(1)'}
    assert secret not in json.dumps(snapshot)


@pytest.mark.parametrize('path', ['CON.py', 'src/aux.txt', 'src/x .py.', 'src/A?.py',
                                 'src/evil\n.py', 'src/a.py:stream'])
def test_snapshot_rejects_windows_unsafe_paths_before_agent_context(path):
    client = github()
    client._request = Mock(return_value=zip_bytes({'root/' + path: 'bad'}))
    with pytest.raises(GitHubError, match='Unsafe'):
        client.snapshot(SHA)


def test_snapshot_rejects_case_aliases_before_agent_context():
    client = github()
    client._request = Mock(return_value=zip_bytes({'root/a.py': 'one', 'root/A.py': 'two'}))
    with pytest.raises(GitHubError, match='case-aliased'):
        client.snapshot(SHA)


def test_actual_safe_snapshot_agrees_with_policy_materialization(tmp_path):
    from workflowkit.policy import materialize_snapshot
    client = github()
    client._request = Mock(return_value=zip_bytes({'root/src/a.py': 'print(1)',
                                                  'root/.npmrc': 'SECRET'}))
    snapshot = client.snapshot(SHA)
    materialize_snapshot(tmp_path, snapshot)
    assert (tmp_path / 'src/a.py').read_text() == 'print(1)'
    assert not (tmp_path / '.npmrc').exists()
