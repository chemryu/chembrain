"""Private in-memory worker validation and bounded smoke diagnostics (stdlib only)."""
import base64
import binascii
import hashlib
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PREFIX = 'data:text/javascript;base64,'
PINNED_SHA256 = '9536359f1b8367850d485731ca1d5e45c159a7b7a0912325e539937aa21ceb18'


def safe_summary(value):
    """Never retain native strings: categories, length and digest suffice."""
    value = str(value)
    category = next((kind for kind in ('data:', 'blob:', 'file:', 'https:', 'http:')
                     if value.startswith(kind)), 'other')
    return {'category': category, 'length': len(value),
            'sha256': hashlib.sha256(value.encode('utf-8', errors='replace')).hexdigest()}


def pinned_worker():
    raw = (ROOT / 'node_modules/pdfjs-dist/build/pdf.worker.min.mjs').read_bytes()
    if hashlib.sha256(raw).hexdigest() != PINNED_SHA256:
        raise AssertionError('Pinned PDF dependency worker digest mismatch')
    return raw


def validate_worker_url(address, expected, manifest):
    """Strict representation AND exact original bytes; exceptions never quote input."""
    summary = safe_summary(address)
    def reject(reason):
        raise AssertionError('PDF worker rejected: '+reason+' '+json.dumps(summary, sort_keys=True))
    digest = hashlib.sha256(expected).hexdigest()
    if digest != PINNED_SHA256 or manifest.get('pdf_worker_sha256') != digest:
        reject('dependency/manifest digest mismatch')
    if manifest.get('worker_transport') != 'native-module-data-url':
        reject('manifest transport mismatch')
    if not isinstance(address, str) or not address.startswith(PREFIX):
        reject('unexpected transport')
    encoded = address[len(PREFIX):]
    if len(encoded) != 4 * ((len(expected) + 2) // 3):
        reject('encoded length mismatch')
    try:
        decoded = base64.b64decode(encoded, validate=True)
    except (ValueError, binascii.Error):
        reject('invalid base64')
    if base64.b64encode(decoded).decode('ascii') != encoded:
        reject('noncanonical base64')
    if decoded != expected or hashlib.sha256(decoded).hexdigest() != digest:
        reject('worker bytes mismatch')
    return {**summary, 'valid': True, 'worker_sha256': digest}


# Test-only init script. A Proxy constructs the genuine native Worker; Python
# receives URL values only in memory and stores finite validated summaries.
WORKER_OBSERVER = r'''(() => {
 const NativeWorker = window.Worker;
 window.Worker = new Proxy(NativeWorker, {construct(target, args, newTarget) {
   const worker = Reflect.construct(target, args, newTarget);
   const options = args[1] || {};
   window.__pwWorkerObservation({event:'construct', url:String(args[0]),
     module:options.type==='module', named:options.name==='chembrain-local-pdf'});
   let terminated=false;
   const terminate=worker.terminate.bind(worker);
   worker.terminate=()=>{if(!terminated){terminated=true;
     window.__pwWorkerObservation({event:'terminate'});}return terminate();};
   for(const event of ['error','messageerror']) worker.addEventListener(event,()=>
     window.__pwWorkerObservation({event}));
   return worker;
 }});
})();'''


def opaque_worker_ready(browser, expected, manifest):
    """Ready-only native transport regression; full parsing is the app smoke gate."""
    address = PREFIX + base64.b64encode(expected).decode('ascii')
    validate_worker_url(address, expected, manifest)
    child = '''<script>
    const worker=new Worker(ADDRESS,{type:'module',name:'chembrain-local-pdf'});
    let settled=false; const timer=setTimeout(()=>finish('timeout'),8000);
    function finish(event){if(settled)return;settled=true;clearTimeout(timer);
      worker.terminate();parent.postMessage({event,opaque:self.origin==='null'},'*');}
    worker.onmessage=e=>{if(e.data?.action==='ready' && e.data?.sourceName==='worker'
      && e.data?.targetName==='main')finish('ready');};
    worker.onerror=()=>finish('error');worker.onmessageerror=()=>finish('messageerror');
    </script>'''.replace('ADDRESS', json.dumps(address))
    body = '''<script>window.result=null;addEventListener('message',e=>{
      if(e.source===document.querySelector('iframe').contentWindow && e.origin==='null')
        window.result=e.data;});</script><iframe sandbox="allow-scripts" srcdoc="'''+html.escape(child, quote=True)+'"></iframe>'
    context = browser.new_context()
    page = context.new_page()
    worker_records, forbidden = [], []
    def route_resource(route):
        if route.request.url == 'http://127.0.0.1/opaque-worker-regression' and route.request.is_navigation_request():
            route.fulfill(status=200, content_type='text/html', body=body)
        else:
            forbidden.append(safe_summary(route.request.url))
            route.abort()
    context.route('**/*', route_resource)
    page.on('worker', lambda worker: worker_records.append(validate_worker_url(worker.url, expected, manifest)))
    try:
        page.goto('http://127.0.0.1/opaque-worker-regression')
        try:
            page.wait_for_function('window.result !== null', timeout=10000)
        except Exception:
            raise AssertionError('Opaque worker regression timed out; workers='+str(len(worker_records))) from None
        result = page.evaluate('window.result')
        if result != {'event': 'ready', 'opaque': True} or len(worker_records) != 1 or forbidden:
            raise AssertionError('Opaque worker ready-only failed '+json.dumps({
                'event': result.get('event') if result else 'absent', 'workers': len(worker_records),
                'forbidden': forbidden[:8]}))
        print('PAPER_WORKER_OPAQUE_READY_ONLY_PASS: normal HTTP sandbox; exact pinned native module; terminated; PDF parse/render/text required separately', flush=True)
    finally:
        context.close()


def safe_diagnostic(value):
    """Accept adapter enums only; forged console objects cannot expose text."""
    if not isinstance(value, dict):
        return {}
    enums = {
        'event': {'error', 'messageerror', 'timeout', 'constructor'},
        'stage': {'construction', 'loading', 'metadata', 'ready', 'text', 'render'},
        'browser': {'edge', 'chromium', 'firefox', 'safari', 'unknown'},
        'protocol': {'file:', 'http:', 'https:', 'data:', 'blob:', 'other'},
        'transport': {'data-url'},
        'errorName': {'Error', 'TypeError', 'SyntaxError', 'SecurityError', 'NetworkError', 'DataCloneError', 'AbortError', 'TimeoutError', 'unknown'},
        'errorCategory': {'detail-unavailable', 'syntax', 'security', 'load', 'serialization', 'unclassified'},
        'sourceCategory': {'unavailable', 'data', 'blob', 'file', 'http', 'other'},
    }
    result = {key: item for key, options in enums.items()
              if isinstance((item := value.get(key)), str) and item in options}
    for key in ('module', 'opaqueOrigin'):
        if isinstance(value.get(key), bool):
            result[key] = value[key]
    for key in ('line', 'column'):
        item = value.get(key)
        if item is None or type(item) is int and 0 <= item <= 10_000_000:
            result[key] = item
    version = value.get('version')
    if isinstance(version, str) and (version == 'unknown' or version.isascii() and version.isdigit() and len(version) <= 4):
        result['version'] = version
    return result


def safe_terminal_failure(error):
    """Finite traceback without exception strings, Aria snapshots or source paths."""
    import traceback
    frames = traceback.extract_tb(error.__traceback__)[-12:]
    return {'event': 'smoke-failure', 'error': safe_summary(error),
            'frames': [{'file': Path(frame.filename).name[:80],
                        'function': ''.join(c for c in frame.name if c.isascii() and (c.isalnum() or c == '_'))[:80],
                        'line': frame.lineno} for frame in frames]}
