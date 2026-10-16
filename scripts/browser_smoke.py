"""Exercise the English DOI-only desktop workflow in a real browser.

Needs Playwright and system Chromium; CHROMIUM_PATH can override the browser.
Uses an isolated temporary database and never changes existing user records.
"""
import io
import json
import os
import re
import shutil
import subprocess
import tempfile
import time
import urllib.request
import zipfile
from pathlib import Path

from playwright.sync_api import expect, sync_playwright

ROOT = Path(__file__).resolve().parent.parent


def main():
    with tempfile.TemporaryDirectory(prefix="chembrain-browser-") as temporary:
        log_path = Path(temporary) / "api.log"
        with log_path.open("w") as log:
            process = subprocess.Popen([str(ROOT / ".venv/bin/python"), "-m", "uvicorn", "server.app:app", "--host", "127.0.0.1", "--port", "8765"], cwd=ROOT,
                env={**os.environ, "CHEMBRAIN_DATA_DIR": str(Path(temporary) / "data"), "CHEMBRAIN_SEED_DEMO": "0", "CHEMBRAIN_SEED_LITERATURE": "1"}, stdout=log, stderr=log)
            try:
                for _ in range(60):
                    try:
                        urllib.request.urlopen("http://127.0.0.1:8765/api/health", timeout=1).close()
                        break
                    except OSError:
                        if process.poll() is not None:
                            raise RuntimeError(log_path.read_text())
                        time.sleep(.2)
                else:
                    raise RuntimeError("API did not become ready")
                with sync_playwright() as playwright:
                    browser = playwright.chromium.launch(executable_path=os.environ.get("CHROMIUM_PATH") or shutil.which("chromium"), args=["--no-sandbox"])
                    page = browser.new_page(viewport={"width": 1440, "height": 1000})
                    errors = []
                    page.on("pageerror", lambda error: errors.append(str(error)))
                    page.goto("http://127.0.0.1:8765", wait_until="networkidle")
                    expect(page.get_by_role("heading", name="Where ideas become reactions")).to_be_visible()
                    expect(page.locator(".molecule-node")).to_have_count(14)
                    expect(page.locator(".reaction-node")).to_have_count(6)
                    assert not re.search('[가-힣]', page.locator('body').inner_text())
                    evidence_links = page.locator('.inspector a.evidence-card')
                    expect(evidence_links.first).to_have_attribute('href', re.compile(r'https://doi.org/10\.1126/'))
                    expect(page.locator('blockquote, .source-text')).to_have_count(0)
                    page.get_by_label('Paper filter', exact=True).select_option('10.1038/nature17431')
                    expect(page.locator('.reaction-node')).to_have_count(2)
                    expect(page.locator('.molecule-node')).to_have_count(4)
                    page.get_by_label('Paper filter', exact=True).select_option('all')
                    page.screenshot(path='/tmp/chembrain-english.png', full_page=True)
                    page.get_by_role('button', name='Paper library').click()
                    expect(page.locator('.source-card')).to_have_count(6)
                    expect(page.locator('.source-card a.source-doi')).to_have_count(6)
                    page.locator('.source-card').first.get_by_role('button', name='Reference details').click()
                    expect(page.get_by_role('link', name='Open DOI', exact=True)).to_be_visible()
                    expect(page.locator('.source-text, pre, iframe')).to_have_count(0)
                    page.get_by_role('button', name='All papers', exact=True).click()
                    page.get_by_label('Paper title', exact=True).fill('Browser fixture paper')
                    page.get_by_label('DOI or DOI URL', exact=True).fill('https://doi.org/10.1000/browser-fixture')
                    page.get_by_label('Citation', exact=True).fill('Browser test fixture only')
                    page.get_by_role('button', name='Add reference', exact=True).click()
                    expect(page.get_by_role('heading', name='Browser fixture paper', exact=True)).to_be_visible()
                    page.get_by_role('button', name='Molecule library', exact=True).click()
                    page.get_by_role('button', name='Add molecule', exact=True).click()
                    dialog = page.get_by_role('dialog')
                    dialog.get_by_label('Molecule name', exact=True).fill('Methanol fixture')
                    dialog.locator('input[name="smiles"]').fill('CO')
                    dialog.get_by_role('button', name='Save molecule', exact=True).click()
                    expect(dialog).not_to_be_visible()
                    page.get_by_role('button', name='Reaction map', exact=True).click()
                    page.get_by_role('button', name='Add reaction', exact=True).click()
                    dialog = page.get_by_role('dialog')
                    dialog.locator('input[name="name"]').fill('Browser fixture oxidation')
                    dialog.get_by_role('button', name='Add new molecule', exact=True).click()
                    nested = page.get_by_role('dialog', name='Add molecule', exact=True)
                    nested.get_by_label('Molecule name', exact=True).fill('Formaldehyde fixture')
                    nested.locator('input[name="smiles"]').fill('C=O')
                    nested.get_by_role('button', name='Save molecule', exact=True).click()
                    expect(nested).not_to_be_visible()
                    dialog = page.get_by_role('dialog', name='New reaction record', exact=True)
                    expect(dialog.locator('input[name="name"]')).to_have_value('Browser fixture oxidation')
                    dialog.get_by_label('Method', exact=True).select_option('photochemical')
                    dialog.get_by_label('Add Reactants', exact=True).select_option(label='Methanol fixture')
                    dialog.get_by_label('Add Products', exact=True).select_option(label='Formaldehyde fixture')
                    dialog.get_by_label('Wavelength', exact=True).fill('450 nm')
                    dialog.get_by_label('Yield (%)', exact=True).fill('80')
                    dialog.get_by_label('Reference', exact=True).select_option(label='Browser fixture paper')
                    dialog.get_by_label('Page, figure or procedure', exact=True).fill('SI, procedure A')
                    dialog.get_by_role('button', name='Add citation', exact=True).click()
                    dialog.get_by_label('Review status', exact=True).select_option('reviewed')
                    dialog.get_by_role('button', name='Save reaction', exact=True).click()
                    expect(dialog).not_to_be_visible()
                    expect(page.locator('.inspector h2')).to_have_text('Browser fixture oxidation')
                    expect(page.locator('.inspector .conditions')).to_contain_text('450 nm')
                    expect(page.locator('.inspector a.evidence-card')).to_have_attribute('href','https://doi.org/10.1000/browser-fixture')
                    page.get_by_role('button', name='Edit reaction record', exact=True).click()
                    dialog = page.get_by_role('dialog')
                    expect(dialog.get_by_label('Page, figure or procedure', exact=True).first).to_have_value('SI, procedure A')
                    expect(dialog.locator('pre, details, blockquote')).to_have_count(0)
                    dialog.get_by_role('button', name='Save reaction', exact=True).click()
                    expect(dialog).not_to_be_visible()
                    page.get_by_role('button', name='Find routes', exact=True).first.click()
                    page.get_by_label('Target product', exact=True).select_option(label='Formaldehyde fixture')
                    page.locator('.route-search').get_by_role('button', name='Find routes', exact=True).click()
                    expect(page.locator('.route-card')).to_have_count(1)
                    expect(page.locator('.route-card')).to_contain_text('Methanol fixture')
                    page.get_by_label('Target product', exact=True).select_option('literature-molecule-nice-entry3')
                    page.locator('.route-search').get_by_role('button', name='Find routes', exact=True).click()
                    expect(page.get_by_role('heading', name='No connected routes')).to_be_visible()
                    page.get_by_role('checkbox', name='Include drafts', exact=True).check()
                    page.locator('.route-search').get_by_role('button', name='Find routes', exact=True).click()
                    expect(page.locator('.route-card')).to_have_count(1)
                    expect(page.locator('.route-card')).to_contain_text('Contains drafts')
                    with page.expect_download() as download:
                        page.get_by_role('link', name='Export Markdown', exact=True).click()
                    with zipfile.ZipFile(io.BytesIO(Path(download.value.path()).read_bytes())) as archive:
                        exported = '\n'.join(archive.read(n).decode() for n in archive.namelist())
                        assert 'https://doi.org/10.1000/browser-fixture' in exported
                        assert '"quote"' not in exported and '"pages"' not in exported
                    page.get_by_role('button', name='Reaction map', exact=True).click()
                    page.get_by_placeholder('Search molecules, reactions, SMILES').fill('not-a-real-molecule')
                    expect(page.get_by_role('heading', name='No matching results')).to_be_visible()
                    page.get_by_role('button', name='Clear search', exact=True).click()
                    page.reload(wait_until='networkidle')
                    expect(page.locator('.molecule-node')).to_have_count(16)
                    mobile = browser.new_page(viewport={'width':390,'height':844}, is_mobile=True, has_touch=True)
                    mobile.goto('http://127.0.0.1:8765',wait_until='networkidle')
                    expect(mobile.locator('.molecule-node')).to_have_count(16)
                    assert mobile.evaluate('document.documentElement.scrollWidth <= 390'), 'Mobile page overflows'
                    mobile.get_by_role('button',name='Paper library').click()
                    expect(mobile.locator('.source-card')).to_have_count(7)
                    assert mobile.evaluate('document.documentElement.scrollWidth <= 390'), 'Mobile paper library overflows'
                    mobile.screenshot(path='/tmp/chembrain-english-mobile.png',full_page=True)
                    assert not errors, errors
                    browser.close()
                    print(json.dumps({'status':'passed','checks':['English interface','14-molecule literature starter','DOI links without full text','paper filter','DOI reference creation','nested molecule creation','DOI citation reaction create/edit','photochemical conditions','route search and draft exclusion','DOI-only Markdown export','persistent reload','mobile layouts','no JS errors']}))
            finally:
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill(); process.wait()


if __name__ == '__main__':
    main()
