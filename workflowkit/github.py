"""GitHub REST gateway. No checkout execution, force push, or release publishing."""
import base64
import datetime
import hashlib
import io
import json
from pathlib import PurePosixPath
import re
import stat
import urllib.error
import urllib.parse
import urllib.request
import zipfile

from .policy import _safe_path as _policy_safe_path, _sensitive_snapshot_path


class GitHubError(RuntimeError):
    pass


class StaleBranchError(GitHubError):
    pass


class _SafeRedirect(urllib.request.HTTPRedirectHandler):
    """Do not forward GitHub authorization to archive/artifact storage redirects."""
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        if urllib.parse.urlsplit(newurl).scheme != 'https':
            raise GitHubError('GitHub redirected to a non-HTTPS URL')
        redirected = super().redirect_request(req, fp, code, msg, headers, newurl)
        if redirected is not None and urllib.parse.urlsplit(req.full_url).netloc != urllib.parse.urlsplit(newurl).netloc:
            redirected.remove_header('Authorization')
        return redirected


def _safe_path(name):
    # Share the Windows materialization rules with the controller so every path
    # sent to an agent can later be written without aliases or device names.
    try:
        _policy_safe_path(name)
    except (TypeError, ValueError):
        raise GitHubError('Unsafe archive or proposed file path') from None
    return PurePosixPath(name)


class GitHub:
    def __init__(self, token, repository, branch, max_text_bytes=1_000_000):
        if not re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+', repository):
            raise GitHubError('Repository must use owner/name format')
        if not token or not branch or any(c in branch for c in '\r\n'):
            raise GitHubError('GitHub token and branch are required')
        self.token, self.repository, self.branch = token, repository, branch
        self.max_text_bytes = max_text_bytes
        self.base = 'https://api.github.com/repos/' + repository
        self.opener = urllib.request.build_opener(_SafeRedirect())

    def _request(self, path, data=None, raw=False, limit=4_000_000, missing_ok=False, method=None):
        url = self.base + path
        request = urllib.request.Request(url, data=None if data is None else json.dumps(data).encode(),
            headers={'Authorization': 'Bearer ' + self.token,
                     'Accept': 'application/vnd.github+json', 'X-GitHub-Api-Version': '2022-11-28',
                     'User-Agent': 'Chembrain-Workflow', 'Content-Type': 'application/json'},
            method=method or ('POST' if data is not None else 'GET'))
        try:
            with self.opener.open(request, timeout=180) as response:
                body = response.read(limit + 1)
            if len(body) > limit:
                raise GitHubError('GitHub response exceeds size limit')
            return body if raw else json.loads(body)
        except urllib.error.HTTPError as exc:
            if exc.code == 404 and missing_ok:
                return None
            if exc.code in (409, 422):
                raise StaleBranchError('GitHub rejected a conflicting or stale update') from None
            raise GitHubError(f'GitHub request failed (HTTP {exc.code})') from None
        except (urllib.error.URLError, TimeoutError, OSError, ValueError):
            raise GitHubError('GitHub transport or JSON response failed') from None

    def head(self):
        return self._request('/git/ref/heads/' + urllib.parse.quote(self.branch, safe=''))['object']['sha']

    def snapshot(self, sha):
        if not re.fullmatch(r'[0-9a-fA-F]{40}', sha):
            raise GitHubError('Snapshot requires an immutable commit SHA')
        archive = self._request('/zipball/' + sha, raw=True, limit=30_000_000)
        included = {}
        ignored = {'.git', '.venv', 'node_modules', '.cache', '.data', '__pycache__', 'dist',
                   'release', 'papers', '.pytest_cache', '.mypy_cache'}
        extensions = {'.py', '.tsx', '.ts', '.jsx', '.js', '.json', '.html', '.css', '.md', '.txt',
                      '.yml', '.yaml', '.toml', '.ini', '.cfg', '.sh', '.cmd', '.ps1', '.spec', '.lock'}
        consumed = 0
        seen = set()
        try:
            with zipfile.ZipFile(io.BytesIO(archive)) as bundle:
                if len(bundle.infolist()) > 10000:
                    raise GitHubError('Archive contains too many files')
                for item in bundle.infolist():
                    name = item.filename.rstrip('/')
                    _safe_path(name)
                    if stat.S_ISLNK(item.external_attr >> 16):
                        raise GitHubError('Archive symlink is not permitted')
                    if item.is_dir():
                        continue
                    parts = PurePosixPath(name).parts[1:]
                    if not parts or any(part in ignored for part in parts):
                        continue
                    path = '/'.join(parts)
                    if _sensitive_snapshot_path(path):
                        continue
                    if PurePosixPath(path).suffix not in extensions and PurePosixPath(path).name not in (
                            '.gitignore', 'Dockerfile'):
                        continue
                    # Lock files remain available locally but giant dependency hashes are not model context.
                    if path in ('package-lock.json', 'requirements.lock'):
                        continue
                    if consumed + item.file_size > self.max_text_bytes:
                        raise GitHubError('Source snapshot exceeds configured text limit')
                    content = bundle.read(item)
                    if b'\x00' in content:
                        continue
                    try:
                        text = content.decode('utf-8-sig')
                    except UnicodeDecodeError:
                        continue
                    if path.casefold() in seen:
                        raise GitHubError('Duplicate or case-aliased source archive path')
                    seen.add(path.casefold())
                    consumed += len(content)
                    included[path] = text
        except GitHubError:
            raise
        except (zipfile.BadZipFile, RuntimeError):
            raise GitHubError('GitHub source archive is invalid') from None
        return included

    def commit_files(self, base_sha, files, summary):
        if self.head() != base_sha:
            raise StaleBranchError('Branch changed since the reviewed source snapshot')
        if not files:
            return base_sha
        if len(files) > 100:
            raise GitHubError('Too many proposed files')
        entries, seen, total = [], set(), 0
        for item in files:
            path, content = item['path'], item['content']
            _safe_path(path)
            if path in seen:
                raise GitHubError('Duplicate proposed file path')
            seen.add(path)
            if content is not None:
                if not isinstance(content, str):
                    raise GitHubError('Proposed content must be text or null')
                encoded = content.encode('utf-8')
                total += len(encoded)
                if total > self.max_text_bytes:
                    raise GitHubError('Proposed changes exceed text limit')
                blob = self._request('/git/blobs', {'content': base64.b64encode(encoded).decode(), 'encoding': 'base64'})
                blob_sha = blob['sha']
            else:
                blob_sha = None
            entries.append({'path': path, 'mode': '100644', 'type': 'blob', 'sha': blob_sha})
        commit = self._request('/git/commits/' + base_sha)
        tree = self._request('/git/trees', {'base_tree': commit['tree']['sha'], 'tree': entries})
        new = self._request('/git/commits', {'message': summary[:500], 'tree': tree['sha'], 'parents': [base_sha]})
        if self.head() != base_sha:
            raise StaleBranchError('Branch advanced while preparing the proposed commit')
        self._request('/git/refs/heads/' + urllib.parse.quote(self.branch, safe=''),
                      {'sha': new['sha'], 'force': False}, method='PATCH')
        return new['sha']

    def _receipt_file(self, name, ref, missing_ok=True):
        result = self._request('/contents/' + urllib.parse.quote(name, safe='/') + '?ref=' +
                               urllib.parse.quote(ref, safe=''), missing_ok=missing_ok)
        if result is None:
            return None
        if result.get('encoding') != 'base64' or result.get('size', 0) > 100_000:
            raise GitHubError('Invalid build receipt file')
        try:
            return base64.b64decode(result['content'], validate=False).decode('utf-8-sig')
        except (ValueError, UnicodeError):
            raise GitHubError('Invalid build receipt encoding') from None

    def receipt(self, sha):
        branch = self._request('/git/ref/heads/build%2Fwindows-status', missing_ok=True)
        if branch is None:
            return None
        receipt_sha = branch['object']['sha']
        body = self._receipt_file('status.json', receipt_sha)
        if body is None:
            return None
        try:
            receipt = json.loads(body)
        except ValueError:
            raise GitHubError('Build receipt is not valid JSON') from None
        if receipt.get('commit') != sha:
            return None
        receipt['_receipt_sha'] = receipt_sha
        receipt['logs'] = {name: self._receipt_file(name + '.log', receipt_sha)
                           for name in ('api', 'normal-launch', 'packaged-smoke')}
        receipt['checksums'] = self._receipt_file('SHA256SUMS.txt', receipt_sha)
        checksum = re.search(r'^([0-9a-fA-F]{64})\s+\*?Chembrain-Windows-x64\.zip\s*$',
                             receipt['checksums'] or '', flags=re.MULTILINE)
        receipt['sha256'] = checksum.group(1).lower() if checksum else None
        return receipt

    def artifact(self, receipt):
        if receipt.get('status') != 'success' or not re.fullmatch(r'[0-9a-fA-F]{40}', receipt.get('commit', '')):
            raise GitHubError('A successful matching build receipt is required')
        pattern = r'https://github\.com/' + re.escape(self.repository) + r'/actions/runs/(\d+)/artifacts/(\d+)'
        match = re.fullmatch(pattern, receipt.get('artifact_url') or '')
        if not match:
            raise GitHubError('Receipt has no valid artifact URL for this repository')
        run_id, artifact_id = match.groups()
        metadata = self._request('/actions/artifacts/' + artifact_id)
        if metadata.get('expired') or str(metadata.get('workflow_run', {}).get('id')) != run_id or (
                metadata.get('workflow_run', {}).get('head_sha') != receipt['commit']):
            raise GitHubError('Artifact is expired or belongs to a different commit/run')
        expires = metadata.get('expires_at')
        if expires and datetime.datetime.fromisoformat(expires.replace('Z', '+00:00')) <= datetime.datetime.now(datetime.timezone.utc):
            raise GitHubError('Artifact has expired')
        data = self._request('/actions/artifacts/' + artifact_id + '/zip', raw=True, limit=350_000_000)
        digest = metadata.get('digest')
        if not isinstance(digest, str) or not re.fullmatch(r'sha256:[0-9a-fA-F]{64}', digest):
            raise GitHubError('Artifact has no supported integrity digest')
        if hashlib.sha256(data).hexdigest() != digest[7:].lower():
            raise GitHubError('Artifact archive digest mismatch')
        try:
            with zipfile.ZipFile(io.BytesIO(data)) as bundle:
                for item in bundle.infolist():
                    _safe_path(item.filename.rstrip('/'))
                    if stat.S_ISLNK(item.external_attr >> 16):
                        raise GitHubError('Artifact symlink is not permitted')
                info = bundle.getinfo('Chembrain-Windows-x64.zip')
                if info.file_size > 300_000_000:
                    raise GitHubError('Packaged application exceeds size limit')
                inner = bundle.read(info)
                sums_info = bundle.getinfo('SHA256SUMS.txt')
                if sums_info.file_size > 10000:
                    raise GitHubError('Artifact checksums exceed size limit')
                packaged_sums = bundle.read(sums_info).decode('utf-8-sig')
        except GitHubError:
            raise
        except (zipfile.BadZipFile, KeyError, UnicodeError, RuntimeError):
            raise GitHubError('Artifact does not contain the expected Windows ZIP and checksum') from None
        checksum = re.search(r'^([0-9a-fA-F]{64})\s+\*?Chembrain-Windows-x64\.zip\s*$',
                             receipt.get('checksums') or '', flags=re.MULTILINE)
        if not checksum or receipt.get('sha256') != checksum.group(1).lower() or not re.search(r'^' + checksum.group(1) + r'\s+\*?Chembrain-Windows-x64\.zip\s*$',
                                        packaged_sums, flags=re.MULTILINE | re.IGNORECASE):
            raise GitHubError('Artifact checksum does not match the immutable receipt')
        if hashlib.sha256(inner).hexdigest() != checksum.group(1).lower():
            raise GitHubError('Packaged application checksum mismatch')
        return inner
