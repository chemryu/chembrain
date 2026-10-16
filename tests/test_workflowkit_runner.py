import hashlib
import json
import os
from pathlib import Path

import pytest

from workflowkit.cli import initialize, run_once
from workflowkit.runner import Workflow, REQUIRED, config_for, controller_lock

SHA = 'a' * 40
ZIP = b'fixture artifact verified by fake GitHub adapter'


def receipt(commit=SHA):
    digest = hashlib.sha256(ZIP).hexdigest()
    return {'commit':commit,'status':'success','artifact_url':'https://github.com/chemryu/chembrain/actions/runs/1/artifacts/2',
        'sha256':digest,'checksums':digest + '  Chembrain-Windows-x64.zip\n',
        'steps':{'validation':'success','packaging':'success','artifact':'success'},
        'logs':{'normal-launch':'WINDOWS_PACKAGED_UI_PASS\nWINDOWS_RESTART_PERSISTENCE_PASS\nWINDOWS_RUNTIME_PATH_INDEPENDENCE_PASS\n'},
        'limits':['Clean Windows VM not tested.']}


def review(commit=SHA, verdict='approved', findings=None):
    return {'commit':commit,'verdict':verdict,'summary':'Independent result','findings':findings or [],
            'checks':[{'name':name,'status':'PASS'} for name in REQUIRED]}


class FakeGitHub:
    def __init__(self):
        self.sha = SHA
        self.source = {'server/example.py':'original source', '.github/workflows/verify.yml':'trusted baseline'}
        self.result = receipt()
        self.commits = []
        self.downloads = 0
    def head(self): return self.sha
    def snapshot(self, commit): return dict(self.source)
    def commit_files(self, base, files, summary):
        assert base == self.sha
        self.commits.append(files)
        for item in files:
            self.source[item['path']] = item['content']
        self.sha = 'b' * 40
        self.result = receipt(self.sha)
        return self.sha
    def receipt(self, commit): return self.result
    def artifact(self, proof):
        self.downloads += 1
        return ZIP


class FakeProviders:
    def __init__(self, reports=None, proposals=None):
        self.reports = list(reports or [review()])
        self.proposals = list(proposals or [{'summary':'No code change necessary','files':[]}])
        self.author_contexts = []
        self.review_contexts = []
    def author(self, context):
        self.author_contexts.append(context)
        return self.proposals.pop(0)
    def review(self, context):
        self.review_contexts.append(context)
        return self.reports.pop(0)


def setup(tmp_path):
    root = initialize(tmp_path / 'Box folder with spaces')
    config = json.loads((root / 'config.json').read_text())
    config.update(author_model='configured-author',reviewer_model='configured-reviewer',ci_timeout_seconds=1,poll_seconds=1,max_rounds=2)
    (root / 'config.json').write_text(json.dumps(config))
    return root, config


def test_initialization_preserves_user_wiki_and_does_not_activate_request(tmp_path):
    root, _ = setup(tmp_path)
    assert 'WORKFLOW_REQUEST_INACTIVE' in (root / 'requests/current.md').read_text(encoding='utf-8')
    (root / 'wiki.md').write_text('User wiki',encoding='utf-8')
    initialize(root)
    assert (root / 'wiki.md').read_text() == 'User wiki'
    with pytest.raises(ValueError,match='inactive'):
        run_once(root)
    assert not (root / 'state.json').exists()
    assert len(list((root / 'agents').glob('*.md'))) == 5


def test_approved_loop_delivers_only_matching_archive_and_audit(tmp_path):
    root, config = setup(tmp_path)
    github, providers = FakeGitHub(), FakeProviders()
    state = Workflow(root,github,providers,config).run('Verify the app')
    assert state['status'] == 'READY' and state['release_published'] is False
    delivery = Path(state['delivery'])
    assert delivery.read_bytes() == ZIP and delivery.is_relative_to(root)
    assert json.loads((delivery.parent / 'manifest.json').read_text())['limits'] == ['Clean Windows VM not tested.']
    assert (root / 'workspace' / state['run_id'] / 'round-01/.github/workflows/verify.yml').exists()
    assert 'REVIEW_RECEIVED' in (root / 'wiki.md').read_text(encoding='utf-8')
    assert 'wiki' in providers.author_contexts[0] and 'wiki' in providers.review_contexts[0]
    assert github.downloads == 1


def test_findings_are_returned_to_author_and_only_revised_sha_is_delivered(tmp_path):
    root, config = setup(tmp_path)
    github = FakeGitHub()
    finding = {'severity':'medium','message':'Fix the implementation','path':'server/example.py'}
    providers = FakeProviders([review(verdict='changes_requested',findings=[finding]),review('b'*40)],
        [{'summary':'Inspect baseline','files':[]},{'summary':'Fixed implementation','files':[{'path':'server/example.py','content':'fixed source'}]}])
    state = Workflow(root,github,providers,config).run('Fix the app')
    assert state['status'] == 'READY' and state['commit'] == 'b'*40
    assert len(github.commits) == 1
    assert providers.author_contexts[1]['previous_review']['findings'] == [finding]


@pytest.mark.parametrize('case',['stale_review','not_run','finding','failed_ci','missing_marker','protected_edit','bad_artifact'])
def test_invalid_evidence_or_forbidden_actions_never_deliver(tmp_path,case):
    root,config = setup(tmp_path)
    github, providers = FakeGitHub(), FakeProviders()
    if case == 'stale_review': providers.reports = [review('c'*40)]
    if case == 'not_run': providers.reports[0]['checks'][0]['status'] = 'NOT RUN'
    if case == 'finding': providers.reports[0]['findings'] = [{'severity':'low','message':'Still unresolved'}]
    if case == 'failed_ci': github.result['status'] = 'failure'
    if case == 'missing_marker': github.result['logs']['normal-launch'] = ''
    if case == 'protected_edit': providers.proposals[0]['files'] = [{'path':'scripts/check_desktop_launch.py','content':'forge pass'}]
    if case == 'bad_artifact': github.artifact = lambda _: b'different bytes'
    state = Workflow(root,github,providers,config).run('Check the app')
    assert state['status'] == 'BLOCKED'
    assert not list((root / 'deliverables').rglob('*.zip'))
    if case != 'bad_artifact': assert github.downloads == 0


def test_round_limit_stops_without_silent_retries(tmp_path):
    root,config = setup(tmp_path)
    finding = [{'severity':'medium','message':'unresolved'}]
    providers = FakeProviders([review(verdict='changes_requested',findings=finding)]*2,
                             [{'summary':'No changes','files':[]}]*2)
    state = Workflow(root,FakeGitHub(),providers,config).run('Fix the app')
    assert state['status'] == 'NEEDS_ATTENTION' and len(providers.author_contexts) == 2


def test_configured_secrets_never_reach_context_or_wiki(tmp_path):
    root,config = setup(tmp_path)
    github,providers = FakeGitHub(),FakeProviders()
    github.source['server/example.py'] = 'my-private-key-value'
    state = Workflow(root,github,providers,config,secrets=['my-private-key-value']).run('Fix the app')
    assert state['status'] == 'BLOCKED' and not providers.author_contexts
    assert 'my-private-key-value' not in (root / 'wiki.md').read_text(encoding='utf-8')


def test_baseline_checks_cannot_be_removed(tmp_path):
    root,config = setup(tmp_path)
    config['required_checks'] = []
    (root / 'config.json').write_text(json.dumps(config))
    with pytest.raises(ValueError,match='cannot be removed'):
        config_for(root)


def test_controller_lock_rejects_second_controller(tmp_path,monkeypatch):
    monkeypatch.setenv('LOCALAPPDATA',str(tmp_path / 'Local'))
    with controller_lock(tmp_path):
        with pytest.raises(RuntimeError,match='Another controller'):
            with controller_lock(tmp_path):
                pass


@pytest.mark.skipif(os.name != 'nt', reason='Windows user-bound DPAPI test')
def test_windows_credentials_roundtrip_outside_box(tmp_path,monkeypatch):
    from workflowkit import credentials
    monkeypatch.setenv('LOCALAPPDATA',str(tmp_path / 'Local App Data'))
    values = {'openai_key':'author-test-secret','anthropic_key':'review-test-secret','github_token':'repo-test-secret'}
    credentials.save(values)
    assert credentials.load() == values
    stored = credentials.credentials_path().read_bytes()
    assert all(value.encode() not in stored for value in values.values())

@pytest.mark.parametrize('location',['request','wiki','role','receipt'])
def test_secrets_in_every_context_channel_block_provider_transmission(tmp_path,location):
    root,config = setup(tmp_path)
    github,providers = FakeGitHub(),FakeProviders()
    secret = 'credential-context-regression-key'
    request = 'Inspect app'
    if location == 'request': request += secret
    if location == 'wiki': (root / 'wiki.md').write_text(secret)
    if location == 'role': (root / 'agents/author.md').write_text(secret)
    if location == 'receipt': github.result['logs']['api'] = secret
    state = Workflow(root,github,providers,config,secrets=[secret]).run(request)
    assert state['status'] == 'BLOCKED'
    if location != 'receipt': assert not providers.author_contexts
    assert not providers.review_contexts
    assert not list((root / 'deliverables').rglob('*.zip'))
    for path in (root / 'runs').rglob('*'):
        if path.is_file(): assert secret not in path.read_text()
