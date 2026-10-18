"""Run the actual single-HTML preview with file:// and all network blocked."""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile

from playwright.sync_api import expect, sync_playwright
from synthesis_map_smoke import check_synthesis_map

ROOT = Path(__file__).resolve().parents[1]
STORE = 'chembrain.normalized-library.v1'


def package_fixture_tests(browser, http_only=False):
    # Invoke the real exported packager, then inspect exact JS/CSS semantics in a
    # browser. Encoding must also cover HTML comment/double-escaped-script cases.
    label = 'Normalized label π </script><script>globalThis.__injected=1</script><!--<script>'
    css = '.fixture::after { content: "</style><script>globalThis.__styleInjected=1</script>"; }'
    javascript = 'globalThis.__fixture=' + json.dumps(label) + ';document.getElementById("root").textContent=globalThis.__fixture;'
    shell = '<!doctype html><meta charset="utf-8"><link rel="stylesheet" href="./assets/style.css"><div id="root"></div><script type="module" src="./assets/main.js"></script>'
    node = '''import {readFileSync} from 'node:fs';
import {inlinePortableHtml,packageBrowser} from './scripts/package_browser.mjs';
const input=JSON.parse(readFileSync(0,'utf8'));
if(input.action==='package') await packageBrowser(input.options);
else process.stdout.write(inlinePortableHtml(input.html,input.js,input.styles));'''

    def invoke(payload):
        return subprocess.run(['node', '--input-type=module', '-e', node], cwd=ROOT,
                              input=json.dumps(payload), capture_output=True, text=True, timeout=30)

    rendered = invoke({'html': shell, 'js': javascript, 'styles': [css]})
    assert rendered.returncode == 0, rendered.stderr
    assert label not in rendered.stdout and css not in rendered.stdout
    with tempfile.TemporaryDirectory(prefix='chembrain-inline-fixture-') as temporary:
        fixture = Path(temporary) / 'fixture.html'
        fixture.write_text(rendered.stdout, encoding='utf-8')
        fixture_url = 'http://127.0.0.1/chembrain-inline-fixture' if http_only else fixture.as_uri()
        context, page, requests, errors, forbidden = context_for(
            browser, fixture_url, document=rendered.stdout if http_only else None)
        page.goto(fixture_url)
        expect(page.locator('#root')).to_have_text(label)
        assert page.evaluate('globalThis.__fixture') == label
        assert page.evaluate('document.querySelector("style").textContent') == css
        assert page.evaluate('globalThis.__injected === undefined && globalThis.__styleInjected === undefined')
        verify_no_requests(requests, errors, forbidden, fixture_url)
        context.close()
        assets = Path(temporary) / 'assets'
        assets.mkdir()
        (Path(temporary) / 'index.html').write_text(shell)
        (assets / 'main.js').write_text('document.getElementById("root").textContent="safe";')
        (assets / 'style.css').write_text('body{color:black}')
        (assets / 'unexpected.js').write_text('throw new Error("Unexpected chunk")')
        rejected = invoke({'action': 'package', 'options': {'buildDir': temporary,
                          'outputDir': str(Path(temporary) / 'output'), 'sourceCommit': 'a' * 40}})
        assert rejected.returncode != 0 and 'Unexpected portable build asset' in rejected.stderr
    for javascript_bad, styles_bad, shell_bad in [
        ('import("./other.js")', [], shell),
        ('import x from "./other.js";', [], shell),
        ('console.log(1)', ['@import "https://example.invalid/a.css";'], shell),
        ('console.log(1)', ['body{background:url(./missing.png)}'], shell),
        ('console.log(1)', [], shell + '<link rel="modulepreload" href="./other.js">'),
    ]:
        rejected = invoke({'html': shell_bad, 'js': javascript_bad, 'styles': styles_bad})
        assert rejected.returncode != 0, ('Unsafe/unexpected dependency accepted', javascript_bad, styles_bad, shell_bad)


def context_for(browser, url, init_script=None, document=None):
    context = browser.new_context(offline=True, accept_downloads=True,
                                  viewport={'width': 1440, 'height': 1000})
    requests, errors, forbidden = [], [], []

    def reject_resource(route):
        if route.request.url == url and route.request.is_navigation_request():
            if document is None:
                route.continue_()
            else:
                route.fulfill(status=200, content_type='text/html; charset=utf-8', body=document)
        else:
            forbidden.append(route.request.url)
            route.abort('internetdisconnected')

    context.route('**/*', reject_resource)
    page = context.new_page()
    page.on('request', lambda request: requests.append(request.url))
    page.on('pageerror', lambda error: errors.append(str(error)))
    if init_script:
        page.add_init_script(init_script)
    return context, page, requests, errors, forbidden


def startup(page, url):
    page.goto(url, wait_until='load')
    expect(page.get_by_role('heading', name='Your molecular library', exact=True)).to_be_visible()
    expect(page.get_by_role('heading', name='Select a molecule', exact=True)).to_be_visible()
    expect(page.locator('.web-tag')).to_have_text('PREVIEW · LOCAL BROWSER FILE')
    expect(page.locator('.molecule-tile').first).to_be_visible()
    expect(page.locator('.web-reaction')).to_have_count(0)


def saved_data(page):
    return json.loads(page.evaluate('(key)=>localStorage.getItem(key)', STORE))


def verify_no_requests(requests, errors, forbidden, url):
    assert not errors, errors
    assert not forbidden, forbidden
    assert not any(request != url for request in requests), requests


def edit_and_transfer(browser, url, document=None):
    context, page, requests, errors, forbidden = context_for(browser, url, document=document)
    startup(page, url)
    check_synthesis_map(page)
    with page.expect_download() as initial_download:
        page.get_by_role('button', name='Backup JSON', exact=True).click()
    assert json.loads(Path(initial_download.value.path()).read_bytes()) == json.loads((ROOT / 'public/library.json').read_text())
    expect(page.get_by_text('All reactions', exact=True)).to_have_count(0)
    expect(page.get_by_text('Organic synthesis', exact=True)).to_have_count(0)
    assert page.locator('.molecule-tile img').count() > 0
    assert page.locator('.molecule-tile img').evaluate_all(
        '(images)=>images.every(image=>image.src.startsWith("data:image/svg+xml")&&image.complete&&image.naturalWidth>0)')
    expect(page.locator('.molecule-tile').filter(has_text='Paclitaxel (Taxol)').locator('img')).to_have_count(0)
    page.locator('.molecule-tile').filter(has_text='Paclitaxel (Taxol)').click();page.get_by_role('tab',name='List',exact=True).click()
    expect(page.locator('.web-reaction')).to_have_count(2)
    page.get_by_role('button', name='Edit molecule', exact=True).click()
    page.get_by_label('Aliases (separate with semicolons)').fill('Offline curated molecule')
    page.get_by_role('button', name='Validate & save', exact=True).click()
    page.locator('.reaction-summary').filter(has_text='Taxol side-chain coupling').click()
    expect(page.locator('.paper-reference')).to_have_count(1)
    expect(page.locator('.paper-reference a')).to_have_attribute('href', 'https://doi.org/10.1021/ja00083a067')
    page.get_by_role('button', name='Edit record', exact=True).click()
    page.get_by_label('Reaction name', exact=True).fill('Offline curated coupling')
    page.get_by_role('button', name='Validate & save', exact=True).click()
    page.get_by_role('button', name='Edit solution', exact=True).first.click()
    page.get_by_label('Concentration (blank = not reported)', exact=True).fill('0.125')
    page.get_by_role('button', name='Validate & save', exact=True).click()
    page.get_by_role('button', name='Edit citation', exact=True).click()
    expect(page.get_by_label('Title', exact=True)).to_have_count(0)
    expect(page.get_by_label('Journal', exact=True)).to_have_count(0)
    expect(page.get_by_label('Notes', exact=True)).to_have_count(0)
    page.get_by_label('Authors (separate with semicolons)').fill('Offline author correction; Robert A. Holton')
    page.get_by_role('button', name='Validate & save', exact=True).click()
    saved = saved_data(page)
    assert all(set(paper) == {'id', 'doi', 'authors'} for paper in saved['papers'])
    page.reload(wait_until='load')
    expect(page.get_by_role('heading', name='Select a molecule', exact=True)).to_be_visible()
    expect(page.locator('.web-reaction')).to_have_count(0)
    assert saved_data(page) == saved
    page.locator('.molecule-tile').filter(has_text='Paclitaxel (Taxol)').click();page.get_by_role('tab',name='List',exact=True).click()
    expect(page.locator('.reaction-summary').filter(has_text='Offline curated coupling')).to_have_count(1)
    before = page.evaluate('(key)=>localStorage.getItem(key)', STORE)
    bad = {**saved, 'papers': [{**saved['papers'][0], 'abstract': 'Unsupported document field'}, *saved['papers'][1:]]}
    page.get_by_label('Import normalized library').set_input_files({'name': 'bad.json', 'mimeType': 'application/json', 'buffer': json.dumps(bad).encode()})
    expect(page.get_by_role('alert')).to_be_visible()
    assert page.evaluate('(key)=>localStorage.getItem(key)', STORE) == before
    page.get_by_label('Import normalized library').set_input_files(str(ROOT / 'public/library.json'))
    expect(page.get_by_role('status')).to_contain_text('Import complete')
    assert saved_data(page) == saved
    with page.expect_download() as downloaded:
        page.get_by_role('button', name='Backup JSON', exact=True).click()
    backup = Path(downloaded.value.path()).read_bytes()
    assert json.loads(backup) == saved
    page.set_viewport_size({'width': 390, 'height': 844})
    assert page.evaluate('document.documentElement.scrollWidth <= innerWidth + 1'), 'Mobile horizontal overflow'
    verify_no_requests(requests, errors, forbidden, url)
    context.close()
    # A different browser profile receives edits only through the supported JSON
    # import; the HTML itself contains no personal data or hidden backup.
    context, page, requests, errors, forbidden = context_for(browser, url, document=document)
    startup(page, url)
    page.get_by_label('Import normalized library').set_input_files({'name': 'chembrain-library.json', 'mimeType': 'application/json', 'buffer': backup})
    expect(page.get_by_role('status')).to_contain_text('Import complete')
    assert saved_data(page) == saved
    verify_no_requests(requests, errors, forbidden, url)
    context.close()


def storage_failure_checks(browser, url, document=None):
    starter = json.loads((ROOT / 'public/library.json').read_text())
    starter['chemicals'][0]['notes'] = 'Existing private chemistry edit retained'
    original = json.dumps(starter, indent=3) + '\n'
    legacy = json.loads(original)
    legacy['papers'][0]['title'] = 'Private legacy metadata remains in browser only'
    legacy_raw = json.dumps(legacy, indent=3) + '\n'
    for mode in ['read', 'write', 'legacy-backup']:
        raw = legacy_raw if mode == 'legacy-backup' else original
        script = '''(()=>{
          const key=KEY,original=ORIGINAL,mode=MODE;
          Storage.prototype.setItem.call(localStorage,key,original);
          const get=Storage.prototype.getItem,set=Storage.prototype.setItem;
          if(mode==='read')Storage.prototype.getItem=function(k){if(k===key)throw new DOMException('Storage unavailable','SecurityError');return get.call(this,k)};
          Storage.prototype.setItem=function(k,v){if(mode==='write'||(mode==='legacy-backup'&&k.includes('.legacy-backup.')))throw new DOMException('Storage full','QuotaExceededError');return set.call(this,k,v)};
          globalThis.__storedOriginal=()=>get.call(localStorage,key);
        })();'''.replace('KEY', json.dumps(STORE)).replace('ORIGINAL', json.dumps(raw)).replace('MODE', json.dumps(mode))
        context, page, requests, errors, forbidden = context_for(browser, url, script, document)
        page.goto(url, wait_until='load')
        expect(page.get_by_role('alert')).to_be_visible()
        assert page.evaluate('globalThis.__storedOriginal()') == raw
        if mode != 'legacy-backup':
            expect(page.locator('.molecule-tile').first).to_be_visible()
            page.locator('.molecule-tile').filter(has_text='Paclitaxel (Taxol)').click();page.get_by_role('tab',name='List',exact=True).click()
            expect(page.locator('.web-reaction')).to_have_count(2)
        if mode == 'write':
            with page.expect_download() as downloaded:
                page.get_by_role('button', name='Backup JSON', exact=True).click()
            assert json.loads(Path(downloaded.value.path()).read_bytes()) == starter
            page.get_by_role('button', name='Edit molecule', exact=True).click()
            page.get_by_label('Aliases (separate with semicolons)').fill('This save must fail')
            page.get_by_role('button', name='Validate & save', exact=True).click()
            expect(page.get_by_role('dialog')).to_be_visible()
            assert page.evaluate('globalThis.__storedOriginal()') == raw
        else:
            expect(page.get_by_role('button', name='Import package', exact=True)).to_be_disabled()
            expect(page.get_by_role('button', name='Backup JSON', exact=True)).to_be_disabled()
        verify_no_requests(requests, errors, forbidden, url)
        context.close()


def check_artifact():
    release = ROOT / 'release'
    artifact = release / 'Chembrain.html'
    manifest = json.loads((release / 'browser-manifest.json').read_text())
    payload = artifact.read_bytes()
    assert len(payload) == manifest['bytes']
    assert hashlib.sha256(payload).hexdigest() == manifest['sha256']
    assert hashlib.sha256((ROOT / 'public/library.json').read_bytes()).hexdigest() == manifest['library_sha256']
    for line in (release / 'SHA256SUMS.txt').read_text().splitlines():
        digest, name = line.split('  ', 1)
        assert name in ['Chembrain.html', 'README-Browser.txt', 'browser-manifest.json']
        assert hashlib.sha256((release / name).read_bytes()).hexdigest() == digest
    html = payload.decode('utf-8')
    # Decode and inspect the only embedded program; raw paper payloads must not be
    # hidden in base64 merely because the outer file is a clean HTML shell.
    import re
    encoded = re.findall(r"app\.textContent=decode\('([A-Za-z\d+/=]+)'\)", html)
    assert len(encoded) == 1
    javascript = base64.b64decode(encoded[0], validate=True).decode('utf-8')
    assert hashlib.sha256(javascript.encode()).hexdigest() == manifest['javascript_sha256']
    for forbidden in ['%PDF-', 'data:application/pdf', 'paclitaxel.png', 'doxycycline.png']:
        assert forbidden not in javascript, forbidden
    return artifact.as_uri(), manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--http-only', action='store_true', help='Exercise in-memory HTTP document only; does not verify file:// use.')
    args = parser.parse_args()
    url, manifest = check_artifact()
    document = None
    if args.http_only:
        document = (ROOT / 'release/Chembrain.html').read_text()
        url = 'http://127.0.0.1/chembrain-portable-preview'
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(executable_path=os.environ.get('CHROMIUM_PATH') or shutil.which('chromium'), args=['--no-sandbox'])
        try:
            package_fixture_tests(browser, args.http_only)
            edit_and_transfer(browser, url, document)
            storage_failure_checks(browser, url, document)
        finally:
            browser.close()
    mode = 'HTTP_ONLY_PORTABLE_PASS: in-memory HTTP document (file:// NOT VERIFIED)' if args.http_only else 'PORTABLE_BROWSER_PASS: actual file:// HTML'
    print(mode + ', offline and all additional resource requests rejected; zero app network/assets; default synthesis map, pan/zoom/fit, keyboard node/detail navigation, branches/gaps, Map/List and mobile; embedded SVGs, initial empty reaction panel, molecule filter, one DOI/authors reference, chemical/reaction/solution/paper edits, reload, backup/profile import, unknown import rejected, unavailable/full storage retains originals, mobile, malicious raw-text fixture and unexpected chunks rejected; source=' + manifest['source_commit'] + ' html_sha256=' + manifest['sha256'])


if __name__ == '__main__':
    main()
