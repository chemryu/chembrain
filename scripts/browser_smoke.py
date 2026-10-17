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


def exercise_collection_controls(browser, base_url):
    """Check controls with local API fixtures; never schedule or download live papers."""
    page = browser.new_page()
    schedules = []
    collections = []
    workspace_requests = []
    requests_to_fail = {'status': 1, 'schedule': 1}
    status = {
        'journal': 'Journal of the American Chemical Society', 'policy': 'open_access_only',
        'running': False, 'last_run': {
            'started_at': '2026-10-16T14:00:00+00:00', 'finished_at': '2026-10-16T14:01:00+00:00',
            'status': 'completed', 'discovered': 0, 'added': 0, 'existing': 0, 'pdfs_saved': 0, 'errors': [],
        }, 'totals': {'articles': 0, 'pdfs': 0},
        'schedule': {'supported': True, 'enabled': False, 'weekday': 'Monday', 'time': '09:00'},
    }

    def respond(route):
        request = route.request
        if request.url.endswith('/schedule'):
            if requests_to_fail['schedule']:
                requests_to_fail['schedule'] -= 1
                route.fulfill(status=500, json={'detail': 'Schedule fixture failure'})
                return
            payload = request.post_data_json
            schedules.append(payload)
            status['schedule'].update(payload)
            route.fulfill(json=status['schedule'])
        elif request.url.endswith('/run'):
            collections.append(request.post_data_json)
            status['totals'] = {'articles': 2, 'pdfs': 1}
            status['last_run'] = {
                'started_at': '2026-10-17T14:00:00+00:00', 'finished_at': '2026-10-17T14:01:00+00:00',
                'status': 'completed', 'discovered': 2, 'added': 2, 'existing': 0, 'pdfs_saved': 1, 'errors': [],
                'notices': [{'code': 'duplicate_doi_matches', 'doi': '10.1021/jacs.fixture',
                             'source_ids': ['kept-main-a', 'kept-main-b'], 'selected_source_id': 'kept-main-a'}],
            }
            route.fulfill(status=202, json={'started': True})
        else:
            if requests_to_fail['status']:
                requests_to_fail['status'] -= 1
                route.fulfill(status=503, json={'detail': 'Temporary status fixture failure'})
                return
            route.fulfill(json=status)

    page.route(re.compile(r'/api/collection/jacs(?:/run|/schedule)?$'), respond)
    page.on('request', lambda request: workspace_requests.append(request.url) if request.url.endswith('/api/workspace') else None)
    page.goto(base_url, wait_until='networkidle')
    page.get_by_role('button', name='Paper library').click()
    collect = page.get_by_role('button', name='Collect now', exact=True)
    expect(page.locator('.jacs-collection').get_by_role('alert')).to_contain_text('Temporary status fixture failure')
    with page.expect_request(re.compile(r'/api/workspace$')):
        expect(collect).to_be_enabled()
    expect(page.locator('.jacs-collection').get_by_role('alert')).to_have_count(0)
    expect(page.locator('.collection-notices')).to_have_count(0)  # Legacy run without a notices field.
    assert not collections, 'Opening the library must not collect papers'
    initially_refreshed = len(workspace_requests)
    page.get_by_role('checkbox', name='Weekly collection', exact=True).check()
    page.get_by_label('Collection day', exact=True).select_option('Friday')
    page.get_by_label('Collection local time', exact=True).fill('13:20')
    # A status poll must not overwrite an unsaved schedule choice.
    page.wait_for_timeout(2700)
    expect(page.get_by_label('Collection day', exact=True)).to_have_value('Friday')
    assert len(workspace_requests) == initially_refreshed, 'The same completed run must not cause a refresh loop'
    page.get_by_role('button', name='Save weekly schedule', exact=True).click()
    expect(page.locator('.jacs-collection').get_by_role('alert')).to_contain_text('Schedule fixture failure')
    page.wait_for_timeout(2700)
    expect(page.locator('.jacs-collection').get_by_role('alert')).to_contain_text('Schedule fixture failure')
    page.get_by_role('button', name='Save weekly schedule', exact=True).click()
    expect(page.get_by_role('button', name='Save weekly schedule', exact=True)).to_be_enabled()
    expect(page.locator('.jacs-collection').get_by_role('alert')).to_have_count(0)
    assert schedules == [{'enabled': True, 'weekday': 'Friday', 'time': '13:20'}], schedules
    before = len(workspace_requests)
    collect.click()
    expect(page.locator('.collection-result')).to_contain_text('2 found · 2 added · 0 already in library · 1 PDFs saved')
    expect(page.locator('.collection-totals')).to_contain_text('2 collected papers · 1 open-access PDFs')
    expect(collect).to_be_enabled()
    page.get_by_text('Duplicate DOI matches (1)', exact=True).click()
    notices = page.locator('.collection-notices')
    expect(notices).to_contain_text('DOI: 10.1021/jacs.fixture')
    expect(notices).to_contain_text('2 existing records retained. Selected source: kept-main-a')
    expect(notices).to_contain_text('Retained source IDs: kept-main-a, kept-main-b')
    expect(notices).to_contain_text('These matches do not stop collection.')
    expect(page.locator('.collection-errors')).to_have_count(0)
    expect(collect).to_be_enabled()
    assert collections == [{}], collections
    assert len(workspace_requests) > before, 'Completed collection must reload the paper workspace'
    page.close()


def exercise_ui(base_url: str, screenshot_dir=None):
    """Run the same UI checks against either a source server or a packaged EXE."""
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(executable_path=os.environ.get("CHROMIUM_PATH") or shutil.which("chromium"), args=["--no-sandbox"])
        page = browser.new_page(viewport={"width": 1440, "height": 1000})
        errors = []
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.goto(base_url, wait_until="networkidle")
        expect(page.get_by_role("heading", name="Where ideas become reactions")).to_be_visible()
        expect(page.locator(".molecule-node")).to_have_count(14)
        expect(page.locator(".reaction-node")).to_have_count(6)
        assert not re.search('[가-힣]', page.locator('body').inner_text())
        evidence_links = page.locator('.inspector a.evidence-card')
        expect(evidence_links).to_have_count(1)
        expect(evidence_links.first).to_have_attribute('href', re.compile(r'https://doi.org/10\.1126/'))
        expect(page.locator('.inspector .reference-provenance')).to_have_count(4)
        expect(evidence_links.first).to_contain_text('Main article: Nicewicz 2008 · Main article')
        expect(evidence_links.first).to_contain_text('Supporting information: Nicewicz 2008 · SI')
        expect(evidence_links.first).to_contain_text('Entry 3 procedure: 7 h, 105 mg, 93% yield, 91% ee')
        expect(evidence_links.first).to_contain_text('Table 1; 23 °C, yields and ee checked visually in table image')
        expect(page.locator('.inspector .badge-row')).to_contain_text('1 reference')
        expect(page.locator('blockquote, .source-text')).to_have_count(0)
        page.get_by_label('Paper filter', exact=True).select_option('10.1038/nature17431')
        expect(page.locator('.reaction-node')).to_have_count(2)
        expect(page.locator('.molecule-node')).to_have_count(4)
        page.get_by_label('Paper filter', exact=True).select_option('all')
        if screenshot_dir: page.screenshot(path=str(Path(screenshot_dir) / 'chembrain-english.png'), full_page=True)
        page.get_by_role('button', name='Paper library').click()
        expect(page.get_by_role('heading', name='JACS weekly collection', exact=True)).to_be_visible()
        expect(page.get_by_role('button', name='Collect now', exact=True)).to_be_visible()
        expect(page.locator('.jacs-collection')).to_contain_text('Subscription PDFs are not downloaded automatically.')
        expect(page.locator('.source-card')).to_have_count(6)
        expect(page.locator('.source-card a.source-doi')).to_have_count(6)
        page.locator('.source-card').first.get_by_role('button', name='Reference details').click()
        expect(page.locator('.jacs-collection')).to_have_count(0)
        expect(page.get_by_role('link', name='Open DOI', exact=True)).to_be_visible()
        expect(page.locator('.source-text, pre, iframe')).to_have_count(0)
        page.get_by_role('button', name='All papers', exact=True).click()
        page.get_by_label('Paper title', exact=True).fill('Browser fixture paper')
        page.get_by_label('DOI or DOI URL', exact=True).fill('https://doi.org/10.1000/browser-fixture')
        page.get_by_label('Citation', exact=True).fill('Browser test fixture only')
        page.get_by_role('button', name='Add reference', exact=True).click()
        expect(page.get_by_role('heading', name='Browser fixture paper', exact=True)).to_be_visible()
        page.get_by_role('button', name='Edit reference', exact=True).click()
        metadata = page.locator('.source-metadata-form')
        doi = metadata.get_by_label('DOI', exact=True)
        doi.fill('')
        metadata.get_by_role('button', name='Save reference', exact=True).click()
        assert doi.evaluate('(input) => input.validity.valueMissing')
        expect(metadata).to_be_visible()
        doi.fill('   ')
        metadata.get_by_role('button', name='Save reference', exact=True).click()
        expect(metadata.get_by_role('alert')).to_contain_text('A DOI is required')
        expect(page.get_by_role('link', name='Open DOI', exact=True)).to_have_attribute('href','https://doi.org/10.1000/browser-fixture')
        doi.fill('https://doi.org/10.1000/browser-fixture')
        metadata.get_by_role('button', name='Save reference', exact=True).click()
        expect(metadata).not_to_be_visible()
        page.get_by_role('button', name='Molecule library', exact=True).click()
        page.get_by_role('button', name='Add molecule', exact=True).click()
        dialog = page.get_by_role('dialog')
        dialog.get_by_label('Molecule name', exact=True).fill('Methanol fixture')
        dialog.locator('input[name="smiles"]').fill('CO')
        dialog.get_by_role('button', name='Save molecule', exact=True).click()
        expect(dialog).not_to_be_visible()
        page.locator('.molecule-tile').filter(has_text='Methanol fixture').click()
        page.get_by_role('button', name='Edit molecule', exact=True).click()
        dialog = page.get_by_role('dialog', name='Edit molecule', exact=True)
        dialog.get_by_label('Molecule name', exact=True).fill('Methanol fixture updated')
        dialog.get_by_label('Aliases', exact=True).fill('MeOH fixture')
        dialog.get_by_label('Availability', exact=True).select_option('in_stock')
        dialog.get_by_label('Research notes', exact=True).fill('User inventory correction survives restart.')
        dialog.get_by_role('button', name='Save molecule', exact=True).click()
        expect(dialog).not_to_be_visible()
        expect(page.locator('.inspector h2')).to_have_text('Methanol fixture updated')
        expect(page.locator('.inspector')).to_contain_text('In stock')
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
        dialog.get_by_label('Add Reactants', exact=True).select_option(label='Methanol fixture updated')
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
        page.locator('.reaction-equation button').filter(has_text='Methanol fixture updated').click()
        page.get_by_role('button', name='Edit molecule', exact=True).click()
        dialog = page.get_by_role('dialog', name='Edit molecule', exact=True)
        expect(dialog.get_by_label('SMILES', exact=True)).not_to_be_editable()
        dialog.get_by_label('Research notes', exact=True).fill('Linked molecule metadata remains editable.')
        dialog.get_by_role('button', name='Save molecule', exact=True).click()
        expect(dialog).not_to_be_visible()
        page.get_by_role('button', name='Find routes', exact=True).first.click()
        page.get_by_label('Target product', exact=True).select_option(label='Formaldehyde fixture')
        page.locator('.route-search').get_by_role('button', name='Find routes', exact=True).click()
        expect(page.locator('.route-card')).to_have_count(1)
        expect(page.locator('.route-card')).to_contain_text('Methanol fixture updated')
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
            assert 'Reference page 1 (numbering unspecified)' in exported
        page.get_by_role('button', name='Reaction map', exact=True).click()
        page.get_by_placeholder('Search molecules, reactions, SMILES').fill('not-a-real-molecule')
        expect(page.get_by_role('heading', name='No matching results')).to_be_visible()
        page.get_by_role('button', name='Clear search', exact=True).click()
        page.reload(wait_until='networkidle')
        expect(page.locator('.molecule-node')).to_have_count(16)
        mobile = browser.new_page(viewport={'width':390,'height':844}, is_mobile=True, has_touch=True)
        mobile.goto(base_url,wait_until='networkidle')
        expect(mobile.locator('.molecule-node')).to_have_count(16)
        assert mobile.evaluate('document.documentElement.scrollWidth <= 390'), 'Mobile page overflows'
        mobile.get_by_role('button',name='Paper library').click()
        expect(mobile.locator('.source-card')).to_have_count(7)
        assert mobile.evaluate('document.documentElement.scrollWidth <= 390'), 'Mobile paper library overflows'
        if screenshot_dir: mobile.screenshot(path=str(Path(screenshot_dir) / 'chembrain-english-mobile.png'),full_page=True)
        assert not errors, errors
        exercise_collection_controls(browser, base_url)
        browser.close()
        print(json.dumps({'status':'passed','checks':['English interface','14-molecule literature starter','one reaction reference per paper with all main/SI provenance','DOI links without full text','JACS open-access collection panel','paper filter','DOI reference creation','DOI deletion rejected without losing the citation','nested molecule creation','molecule metadata editing','DOI citation reaction create/edit','photochemical conditions','route search and draft exclusion','DOI-only Markdown export','persistent reload','mobile layouts','no JS errors']}))


def verify_restarted_ui(base_url: str):
    """Read persisted user data through a fresh browser after process restart."""
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(executable_path=os.environ.get("CHROMIUM_PATH") or shutil.which("chromium"), args=["--no-sandbox"])
        page = browser.new_page()
        page.goto(base_url, wait_until="networkidle")
        page.get_by_role('button', name='Molecule library', exact=True).click()
        expect(page.locator('.molecule-tile').filter(has_text='User-corrected literature name')).to_be_visible()
        page.locator('.molecule-tile').filter(has_text='Persistent user molecule').click()
        expect(page.locator('.inspector')).to_contain_text('Persisted user notes')
        expect(page.locator('.inspector')).to_contain_text('In stock')
        browser.close()
    print('Restarted UI: persisted user molecule, notes and inventory visible.', flush=True)


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
                exercise_ui('http://127.0.0.1:8765', screenshot_dir='/tmp')
            finally:
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill(); process.wait()


if __name__ == '__main__':
    main()
