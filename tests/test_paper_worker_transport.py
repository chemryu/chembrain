"""Execute the shipping TypeScript encoder and finite native diagnostics in Node."""
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def transport_check(body: str) -> None:
    script = f"""
import assert from 'node:assert/strict';
import {{workerDataUrl, workerDiagnostic}} from {json.dumps((ROOT / 'src/paperWorkerTransport.ts').as_uri())};
{body}
"""
    result = subprocess.run(
        ['node', '--experimental-strip-types', '--input-type=module', '-e', script],
        cwd=ROOT, capture_output=True, text=True, timeout=20,
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_encoder_preserves_unicode_and_arbitrary_bytes_across_base64_chunks():
    transport_check(r"""
const inputs = [new TextEncoder().encode('// 한글 🧪 café\nexport const x="λ";'),
  ...[0,1,2,3,24575,24576,24577,49151,49152,49153,1000000].map(length =>
    Uint8Array.from({length}, (_,i) => (i*131+255)%256))];
for (const bytes of inputs) {
  const actual=workerDataUrl(bytes);
  assert.equal(actual, 'data:text/javascript;base64,'+Buffer.from(bytes).toString('base64'));
  assert.deepEqual(new Uint8Array(Buffer.from(actual.split(',')[1], 'base64')),bytes);
}
""")


def test_encoder_preserves_the_actual_pinned_pdf_worker_digest():
    transport_check(r"""
const {readFileSync}=await import('node:fs');
const {createHash}=await import('node:crypto');
const original=readFileSync('node_modules/pdfjs-dist/build/pdf.worker.min.mjs');
const url=workerDataUrl(original);
const decoded=Buffer.from(url.slice('data:text/javascript;base64,'.length),'base64');
assert.deepEqual(decoded,original);
assert.equal(createHash('sha256').update(decoded).digest('hex'),
  '9536359f1b8367850d485731ca1d5e45c159a7b7a0912325e539937aa21ceb18');
""")


def test_diagnostics_never_emit_arbitrary_native_strings_or_nonfinite_numbers():
    transport_check(r"""
const secret='PRIVATE paper path with spaces/α.pdf';
const payload='A'.repeat(100000);
const unsafe=[secret,'file:///home/user/'+secret,'C:\\Users\\user\\'+secret,
  'data:text/javascript;base64,'+payload,'blob:https://host/'+secret,
  'https://host/'+secret,payload];
for (const value of unsafe) {
  const report=workerDiagnostic('error','loading',{
    message:value,filename:value,name:value,line:Infinity,column:-1},
    {userAgent:value,protocol:value,origin:value});
  const encoded=JSON.stringify(report);
  assert.ok(encoded.length<500);
  assert.ok(!encoded.includes(secret));assert.ok(!encoded.includes('A'.repeat(20)));
  assert.equal(report.errorName,'unknown');assert.equal(report.protocol,'other');
  assert.equal(report.line,null);assert.equal(report.column,null);
}
for (const invalid of [NaN,Infinity,-Infinity,-1,1.5,10000001,'12',{},null]) {
  const report=workerDiagnostic('messageerror','ready',{line:invalid,column:invalid},{});
  assert.equal(report.line,null);assert.equal(report.column,null);
  assert.equal(report.errorCategory,'detail-unavailable');
}
""")


def test_diagnostics_keep_only_useful_fixed_categories_and_numeric_locations():
    transport_check(r"""
const report=workerDiagnostic('error','construction',{
  message:'SecurityError: access denied to file:///private/path with spaces.pdf',
  filename:'data:text/javascript;base64,PRIVATE',name:'SecurityError',line:17,column:0},
  {userAgent:'Mozilla/5.0 Chrome/154.0.1.2 Safari/537.36',protocol:'file:',origin:'null'});
assert.deepEqual(report,{
  event:'error',stage:'construction',browser:'chromium',version:'154',protocol:'file:',
  opaqueOrigin:true,transport:'data-url',module:true,errorName:'SecurityError',
  errorCategory:'security',sourceCategory:'data',line:17,column:0,
});
for (const [message,category] of [['Unexpected token','syntax'],['Failed to fetch','load'],
  ['Data could not be deserialized','serialization'],['arbitrary private source','unclassified']]) {
  assert.equal(workerDiagnostic('error','render',{message},{}).errorCategory,category);
}
assert.equal(workerDiagnostic('timeout','metadata',{},{}).errorCategory,'detail-unavailable');
""")
