"""Single-owner, bounded author/reviewer loop. The models cannot execute commands."""
import hashlib
import json
import os
import platform
import re
import time
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

from .policy import validate_edits, apply_edits, materialize_snapshot, review_approved, receipt_checks, atomic_json, atomic_text

REQUIRED = ['windows_build','packaged_ui','restart_persistence','runtime_path_independence']


def now():
    return datetime.now(timezone.utc).isoformat()


def config_for(root):
    config = json.loads((root / 'config.json').read_text(encoding='utf-8-sig'))
    if not all(config.get(key) for key in ('repository','branch','author_model','reviewer_model')):
        raise ValueError('Configure the repository, branch and both API model names before running.')
    if config.get('owner_host') and config['owner_host'] != platform.node():
        raise ValueError('This Box folder has a different controller host. Stop that controller before explicitly reconfiguring ownership.')
    if not 1 <= int(config.get('max_rounds',5)) <= 10:
        raise ValueError('max_rounds must be between 1 and 10.')
    if config.get('required_checks') != REQUIRED:
        raise ValueError('The four baseline Windows checks cannot be removed or replaced.')
    return config


@contextmanager
def controller_lock(root, purpose='run'):
    """OS file lock outside the synced folder; no stale-lock bypass after a crash."""
    name = hashlib.sha256((str(root.resolve()).casefold() + ':' + purpose).encode()).hexdigest()[:24]
    folder = Path(os.environ.get('LOCALAPPDATA', Path.home() / '.local/share')) / 'ChembrainWorkflow' / 'locks'
    folder.mkdir(parents=True, exist_ok=True)
    with (folder / (name + '.lock')).open('a+b') as handle:
        handle.seek(0)
        handle.write(b'0'); handle.flush(); handle.seek(0)
        try:
            if os.name == 'nt':
                import msvcrt
                msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl
                fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError as error:
            raise RuntimeError('Another controller already owns this folder on this machine.') from error
        try:
            yield
        finally:
            handle.seek(0)
            if os.name == 'nt':
                msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                fcntl.flock(handle.fileno(), fcntl.LOCK_UN)


class Workflow:
    def __init__(self, root, github, providers, config, secrets=(), sleep=time.sleep, monotonic=time.monotonic):
        self.root = Path(root)
        self.github, self.providers, self.config = github, providers, config
        self.secrets = [s for s in secrets if s]
        self.sleep, self.monotonic = sleep, monotonic
        self.run_id = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ-') + uuid.uuid4().hex[:8]
        self.log = self.root / 'runs' / self.run_id
        self.log.mkdir(parents=True, exist_ok=True)
        self.state = {'run_id':self.run_id,'status':'STARTING','round':0,'updated_at':now(),'release_published':False}

    def redact(self, value):
        text = str(value)
        for secret in self.secrets:
            text = text.replace(secret, '[REDACTED]')
        return text

    def safe_context(self, context):
        encoded = json.dumps(context, ensure_ascii=False)
        if any(secret in encoded for secret in self.secrets):
            raise ValueError('A configured credential appears in agent context; no model request was sent.')
        return context

    def record(self, status, message, **fields):
        self.state.update(status=status, updated_at=now(), **fields)
        safe_message = self.redact(message)
        atomic_json(self.root / 'state.json', self.state)
        event = {**self.state,'message':safe_message}
        # Each event is immutable; wiki remains a human-readable communication index.
        index = len(list(self.log.glob('event-*.json'))) + 1
        atomic_json(self.log / f'event-{index:04}.json', event)
        wiki = self.root / 'wiki.md'
        before = wiki.read_text(encoding='utf-8') if wiki.exists() else '# ChemBrain workflow wiki\n'
        current = ("<!-- CURRENT_STATUS -->\n"
                   f"현재 상태: **{status}** · 회차 {self.state['round']} · 실행 `{self.run_id}`\n\n"
                   f"커밋: `{self.state.get('commit','—')}` · 갱신: {self.state['updated_at']}\n"
                   "<!-- /CURRENT_STATUS -->")
        if '<!-- CURRENT_STATUS -->' in before:
            before = re.sub(r'<!-- CURRENT_STATUS -->.*?<!-- /CURRENT_STATUS -->', lambda _: current, before, flags=re.S)
        else:
            before = current + '\n\n' + before
        atomic_text(wiki, before + f"\n## {now()} · {status}\n- Run: `{self.run_id}`\n- Round: {self.state['round']}\n- Commit: `{self.state.get('commit','—')}`\n\n{safe_message}\n")

    def wait_for_receipt(self, commit):
        deadline = self.monotonic() + min(max(int(self.config.get('ci_timeout_seconds',1800)),1),3600)
        self.record('WAITING_FOR_VALIDATION','Waiting for a Windows receipt matching this exact commit.',commit=commit)
        while self.monotonic() < deadline:
            receipt = self.github.receipt(commit)
            if receipt and receipt.get('commit') == commit and receipt.get('status') in ('success','failure','cancelled'):
                return receipt
            self.sleep(min(max(int(self.config.get('poll_seconds',20)),1),60))
        raise TimeoutError('No completed matching Windows validation receipt arrived. No delivery was made.')

    def run(self, request):
        try:
            self.safe_context({'request':request})
            atomic_text(self.log / 'request.md', request)
            self.record('REQUEST_RECEIVED', request)
            previous = None
            for number in range(1, int(self.config.get('max_rounds',5)) + 1):
                self.state['round'] = number
                commit = self.github.head()
                source = self.github.snapshot(commit)
                if any(secret in content for secret in self.secrets for content in source.values()):
                    raise ValueError('A configured secret appears in repository context; refusing model access or synchronization.')
                workspace = self.root / 'workspace' / self.run_id / f'round-{number:02}'
                workspace.mkdir(parents=True, exist_ok=True)
                materialize_snapshot(workspace, source)
                self.record('AUTHORING','Author receives requirements, source and the previous independent findings.',commit=commit)
                proposal = self.providers.author(self.safe_context({'request':request,'commit':commit,'source':source,'previous_review':previous,
                                                  'role_rules':(self.root / 'agents/author.md').read_text(encoding='utf-8'),
                                                  'required_checks':REQUIRED, 'wiki':(self.root / 'wiki.md').read_text(encoding='utf-8')[-20000:]}))
                edits = validate_edits(proposal.get('files',[]), self.config.get('protected_paths'))
                if any(secret in (item.get('content') or '') for secret in self.secrets for item in edits):
                    raise ValueError('A proposed code change contains a configured credential; no commit was made.')
                summary = self.redact(proposal.get('summary','Source changes'))
                atomic_json(self.root / 'changes' / f'{self.run_id}-round-{number:02}.json', {'base_commit':commit,'summary':summary,'files':edits})
                apply_edits(workspace, edits)
                if edits:
                    commit = self.github.commit_files(commit, edits, summary)
                    source = self.github.snapshot(commit)
                self.record('SOURCE_READY',summary,commit=commit)
                receipt = self.wait_for_receipt(commit)
                checks = receipt_checks(receipt)
                self.safe_context({'receipt':receipt})
                atomic_json(self.log / f'validation-{number:02}.json', receipt)
                self.record('VALIDATION_RECEIVED', json.dumps(checks,ensure_ascii=False),commit=commit)
                self.record('REVIEWING','Independent reviewer reads the exact committed source and validation evidence.',commit=commit)
                review = self.providers.review(self.safe_context({'request':request,'commit':commit,'source':source,'receipt':receipt,'verified_checks':checks,
                                                'role_rules':(self.root / 'agents/reviewer.md').read_text(encoding='utf-8'),
                                                'required_checks':REQUIRED, 'wiki':(self.root / 'wiki.md').read_text(encoding='utf-8')[-20000:]}))
                # Validate the report as data; never execute instructions or code from it.
                review = json.loads(self.redact(json.dumps(review)))
                if review.get('commit') != commit:
                    raise ValueError('Reviewer returned a stale or mismatched commit.')
                atomic_json(self.root / 'reviews' / f'{self.run_id}-round-{number:02}.json',review)
                self.record('REVIEW_RECEIVED',self.redact(json.dumps(review,ensure_ascii=False)),commit=commit)
                if review_approved(review, commit, receipt, REQUIRED):
                    if self.github.head() != commit:
                        raise RuntimeError('The branch changed after review; delivery is blocked.')
                    data = self.github.artifact(receipt)
                    expected = receipt.get('sha256')
                    actual = hashlib.sha256(data).hexdigest()
                    if not expected or actual.lower() != expected.lower():
                        raise RuntimeError('The candidate artifact does not match the validated checksum.')
                    # Recheck after download to avoid delivering a stale branch version.
                    if self.github.head() != commit:
                        raise RuntimeError('The branch changed during artifact verification; delivery is blocked.')
                    folder = self.root / 'deliverables' / commit
                    folder.mkdir(parents=True, exist_ok=True)
                    archive = folder / 'Chembrain-Windows-x64.zip'
                    temp = archive.with_suffix('.zip.part')
                    temp.write_bytes(data); temp.replace(archive)
                    manifest = {'commit':commit,'sha256':actual,'run_id':self.run_id,'checks':checks,'review':review,
                                'limits':receipt.get('limits',[]),'release_published':False,'delivered_at':now()}
                    atomic_json(folder / 'manifest.json',manifest)
                    atomic_text(folder / 'READY.md',f"# Independently reviewed candidate\n\nCommit: `{commit}`\n\nSHA256: `{actual}`\n\n" + '\n'.join('- ' + str(x) for x in receipt.get('limits',[])))
                    self.record('READY',f'Exact tested archive saved to deliverables after independent approval. SHA256: {actual}',commit=commit,delivery=str(archive))
                    return self.state
                verdict = review.get('verdict')
                if verdict == 'blocked':
                    self.record('BLOCKED','Independent reviewer requires external action; no delivery.',commit=commit)
                    return self.state
                if verdict not in ('approved','changes_requested'):
                    raise ValueError('Invalid reviewer verdict.')
                if verdict == 'approved':
                    self.record('BLOCKED','Approval did not satisfy all strict checks or still contained findings; no delivery.',commit=commit)
                    return self.state
                previous = review
            self.record('NEEDS_ATTENTION','The configured round limit was reached. No approved artifact was delivered.')
            return self.state
        except Exception as error:
            self.record('BLOCKED',self.redact(error))
            return self.state
