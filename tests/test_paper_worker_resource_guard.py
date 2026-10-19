"""Real pinned dependency negative integrity checks, without browser imports."""
import base64
import importlib.util
from pathlib import Path
import pytest

spec = importlib.util.spec_from_file_location('paper_worker_smoke', Path(__file__).resolve().parents[1] / 'scripts/paper_worker_smoke.py')
guard = importlib.util.module_from_spec(spec)
spec.loader.exec_module(guard)

@pytest.fixture
def worker():
    raw = guard.pinned_worker()
    return raw, {'pdf_worker_sha256': guard.PINNED_SHA256, 'worker_transport': 'native-module-data-url'}

def test_exact_pinned_native_worker(worker):
    raw, manifest = worker
    record = guard.validate_worker_url(guard.PREFIX + base64.b64encode(raw).decode(), raw, manifest)
    assert record['valid'] and record['worker_sha256'] == guard.PINNED_SHA256

@pytest.mark.parametrize('case', ['changed', 'truncated', 'foreign', 'arbitrary-data', 'external', 'blob', 'base64-space', 'wrong-mime'])
def test_reject_untrusted_workers_without_payload_errors(worker, case):
    raw, manifest = worker
    encoded = base64.b64encode(raw).decode()
    address = {
        'changed': guard.PREFIX + base64.b64encode(bytes([raw[0] ^ 1]) + raw[1:]).decode(),
        'truncated': guard.PREFIX + encoded[:-4],
        'foreign': guard.PREFIX + base64.b64encode(b'/* foreign */'+raw[13:]).decode(),
        'arbitrary-data': 'data:text/javascript,postMessage("secret-marker")',
        'external': 'https://foreign.invalid/private-secret-marker.js',
        'blob': 'blob:http://foreign.invalid/private-secret-marker',
        'base64-space': guard.PREFIX + ' '+encoded[1:],
        'wrong-mime': 'data:application/javascript;base64,'+encoded,
    }[case]
    with pytest.raises(AssertionError) as caught:
        guard.validate_worker_url(address, raw, manifest)
    message = str(caught.value)
    assert len(message) < 300
    assert address not in message and 'secret-marker' not in message
    assert encoded[:100] not in message

@pytest.mark.parametrize('field,value', [('pdf_worker_sha256', '0'*64), ('worker_transport','blob')])
def test_manifest_is_binding(worker, field, value):
    raw, manifest = worker
    manifest[field] = value
    with pytest.raises(AssertionError, match='manifest'):
        guard.validate_worker_url(guard.PREFIX+base64.b64encode(raw).decode(), raw, manifest)

def test_console_diagnostic_allows_only_fixed_categories():
    value = guard.safe_diagnostic({'event':'error', 'stage':'render', 'line':12,
        'errorName':'private-source.pdf', 'errorCategory':'secret-marker',
        'sourceCategory':'data', 'version':'154', 'module':True,
        'protocol':'file:///private-source.pdf', 'extra':'secret-marker'})
    assert value == {'event':'error', 'stage':'render', 'line':12, 'column':None,
                     'sourceCategory':'data', 'version':'154', 'module':True}


def test_terminal_failure_hides_playwright_snapshot_and_worker_payload(worker):
    raw, _ = worker
    secret = 'PRIVATE_PAGE_TEXT secret-source.pdf '+guard.PREFIX+base64.b64encode(raw).decode()
    try:
        raise RuntimeError(secret)
    except RuntimeError as error:
        record = guard.safe_terminal_failure(error)
    import json
    logged = json.dumps(record)
    assert len(logged) < 1000
    assert 'PRIVATE_PAGE_TEXT' not in logged and 'secret-source' not in logged
    assert guard.PREFIX not in logged and str(Path(__file__).parent) not in logged
    assert record['frames'][-1]['file'] == Path(__file__).name
