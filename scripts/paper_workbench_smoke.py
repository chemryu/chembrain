"""Exercise the separate single-HTML paper workbench and real main-app handoff.

Default uses actual file:// documents in CI. --http-only exercises the identical
bytes at mocked loopback URLs, without claiming file support on managed hosts.
All PDF/MOL fixtures are synthetic and generated privately in a temporary folder.
"""
import argparse
import base64
from copy import deepcopy
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import tempfile

import pymupdf as fitz
from playwright.sync_api import expect, sync_playwright
from rdkit import Chem
from rdkit.Chem import AllChem

from structure_smoke import _diagram

ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = 'chembrain.paper-workbench.v1'
LIBRARY = 'chembrain.normalized-library.v1'
DOI = '10.1000/workbench-fixture'
SALT = 'C[C@H](O)C(=O)[O-].[Na+]'
OPAQUE = 'PRIVATE_SYNTHETIC_PAGE_TEXT_NOT_FOR_PUBLIC_FACTS'


def artifact(filename, manifest_name):
    release = ROOT / 'release'
    raw = (release / filename).read_bytes()
    manifest = json.loads((release / manifest_name).read_bytes())
    assert manifest['source_commit'] and len(manifest['source_commit']) == 40
    assert manifest['sha256'] == hashlib.sha256(raw).hexdigest()
    assert manifest['bytes'] == len(raw)
    encoded = re.findall(r"app\.textContent=decode\('([A-Za-z\d+/=]+)'\)", raw.decode())
    assert len(encoded) == 1
    program = base64.b64decode(encoded[0], validate=True)
    assert manifest['javascript_sha256'] == hashlib.sha256(program).hexdigest()
    return raw.decode(), manifest


def make_fixtures(folder):
    pdf = fitz.open()
    p = pdf.new_page(width=612, height=792)
    p.insert_text((45, 45), 'Synthetic source for software testing only', fontsize=15)
    for line, value in enumerate([
        OPAQUE, 'Article DOI: '+DOI, 'Reference DOI: 10.1000/reference-only',
        'Isomeric SMILES: '+SALT, 'Scheme 1: local compound 1 to local compound 2.',
        'Ethylene glycol solvent; stage 1: 20 C, 1 h; stage 2: 40 C, 2 h; yield 70%.',
    ]):
        p.insert_text((45, 80+line*23), value, fontsize=10)
    p.draw_line((65, 300), (130, 260), color=(0, 0, 0), width=2)
    p.draw_line((130, 260), (195, 300), color=(0, 0, 0), width=2)
    blank = pdf.new_page(width=612, height=792)
    # Image-only page: actual rendered pixels, no text layer and no OCR claim.
    pix = fitz.Pixmap(fitz.csRGB, fitz.IRect(0, 0, 150, 80), False)
    pix.clear_with(240)
    blank.insert_image(fitz.Rect(45, 100, 345, 260), pixmap=pix)
    blank.draw_rect(fitz.Rect(70, 120, 300, 220), color=(0.2, 0.3, 0.5), width=4)
    source = folder / 'synthetic-source.pdf'
    source.write_bytes(pdf.tobytes())
    pdf.close()
    replacement = fitz.open()
    replacement.new_page().insert_text((45, 45), 'Different synthetic document')
    (folder / 'different-source.pdf').write_bytes(replacement.tobytes())
    replacement.close()
    encrypted = fitz.open(source)
    (folder / 'encrypted.pdf').write_bytes(encrypted.tobytes(encryption=fitz.PDF_ENCRYPT_AES_256,
                                                           owner_pw='test-owner', user_pw='test-user'))
    encrypted.close()
    many = fitz.open()
    for _ in range(401):
        many.new_page(width=72, height=72)
    (folder / 'too-many-pages.pdf').write_bytes(many.tobytes())
    many.close()
    mol = Chem.MolFromSmiles('C[C@@H](O)C(=O)[O-].[Na+]')
    AllChem.Compute2DCoords(mol)
    # MDL V2000's absent chiral flag denotes relative/racemic stereochemistry.
    # Do not manufacture absolute identity from its otherwise similar wedges.
    (folder / 'relative-stereo.mol').write_text(Chem.MolToMolBlock(mol))
    mol.SetIntProp('_MolFileChiralFlag', 1)
    (folder / 'opposite-stereo.mol').write_text(Chem.MolToMolBlock(mol))
    return source


def context_for(browser, documents, init=None):
    context = browser.new_context(offline=True, accept_downloads=True,
                                  viewport={'width': 1440, 'height': 1000})
    requests, errors, forbidden, workers = [], [], [], []

    def resource(route):
        address = route.request.url
        if address in documents and route.request.is_navigation_request():
            if documents[address] is None:
                route.continue_()
            else:
                route.fulfill(status=200, content_type='text/html; charset=utf-8', body=documents[address])
        elif address.startswith('blob:'):
            # Locally constructed PDF worker/module or downloaded JSON only.
            route.continue_()
        else:
            forbidden.append(address)
            route.abort('internetdisconnected')

    context.route('**/*', resource)
    if init:
        context.add_init_script(init)
    page = context.new_page()
    page.on('request', lambda request: requests.append(request.url))
    page.on('pageerror', lambda error: errors.append(str(error)))
    page.on('worker', lambda worker: workers.append(worker.url))
    return context, page, requests, errors, forbidden, workers


def verify_resources(state, documents, require_worker=False):
    _, _, requests, errors, forbidden, workers = state
    assert not errors, errors
    assert not forbidden, forbidden
    assert all(url in documents or url.startswith('blob:') for url in requests), requests
    assert all(url.startswith('blob:') for url in workers), workers
    if require_worker:
        assert workers, 'Actual locally constructed PDF worker never ran'


def start(page, url):
    page.goto(url, wait_until='load')
    expect(page.get_by_role('heading', name='From paper to connected chemistry', exact=True)).to_be_visible()
    expect(page.get_by_text('Chembrain Paper Workbench', exact=True)).to_be_visible()


def section(page, name):
    return page.locator('section.pw-record-editor').filter(has=page.get_by_role('heading', name=name, exact=True))


def source(editor, locator='Scheme 1, synthetic fixture'):
    editor.get_by_role('button', name='Add source location', exact=True).click()
    editor.get_by_label('Source locator 1', exact=True).fill(locator)


def inspect_confirm(editor):
    editor.get_by_role('button', name='Inspect structure', exact=True).click()
    expect(editor.locator('.pw-inspection')).to_be_visible(timeout=30000)
    editor.get_by_role('checkbox', name='I compared this identity, structure and stereochemistry against the cited PDF.', exact=True).check()
    editor.get_by_role('button', name='Confirm chemical', exact=True).click()
    expect(editor.get_by_role('heading', name='Checked chemical', exact=True)).to_be_visible()


def add_chemical(page, name, label, smiles, kind='compound'):
    page.get_by_role('button', name='2. Chemicals', exact=True).click()
    page.get_by_role('button', name='Add chemical', exact=True).click()
    editor = page.get_by_role('region', name='Chemical editor', exact=True)
    editor.get_by_label('Paper-local label', exact=True).fill(label)
    editor.get_by_label('Chemical name', exact=True).fill(name)
    editor.get_by_role('combobox', name='Kind', exact=True).select_option(kind)
    editor.get_by_role('textbox', name='SMILES', exact=True).fill(smiles)
    source(editor)
    expect(editor.get_by_role('button', name='Confirm chemical', exact=True)).to_be_disabled()
    inspect_confirm(editor)
    return editor


def downloaded_json(page, button):
    with page.expect_download() as pending:
        button.click()
    raw = Path(pending.value.path()).read_bytes()
    return raw, json.loads(raw)


def create_checked_package(page, url, folder):
    start(page, url)
    page.get_by_label('Open local PDF', exact=True).set_input_files(str(folder / 'synthetic-source.pdf'))
    canvas = page.get_by_label('Private PDF page', exact=True)
    expect(canvas).to_have_attribute('data-rendered', 'true', timeout=30000)
    assert canvas.evaluate('''canvas=>{const data=canvas.getContext('2d').getImageData(0,0,canvas.width,canvas.height).data;
      let ink=0;for(let i=0;i<data.length;i+=4)if(data[i]<200||data[i+1]<200||data[i+2]<200)ink++;return ink>500;}'''), 'PDF canvas has no actual rendered ink'
    page.get_by_text('Private page text and explicit notation candidates', exact=True).click()
    expect(page.get_by_role('button', name='Use DOI candidate '+DOI, exact=True)).to_be_visible()
    expect(page.get_by_role('button', name='Use DOI candidate 10.1000/reference-only', exact=True)).to_be_visible()
    expect(page.get_by_label('Article DOI', exact=True)).to_have_value('')
    page.get_by_label('Article DOI', exact=True).fill(DOI)
    page.get_by_label('Authors (separate with semicolons)', exact=True).fill('A. Synthetic; B. Fixture')
    page.get_by_role('button', name='Create paper project', exact=True).click()
    page.get_by_role('button', name='Add unchecked notation draft', exact=True).click()
    editor = page.get_by_role('region', name='Chemical editor', exact=True)
    expect(editor.get_by_role('textbox', name='SMILES', exact=True)).to_have_value(SALT)
    editor.get_by_label('Paper-local label', exact=True).fill('main:1')
    editor.get_by_label('Chemical name', exact=True).fill('Synthetic stereochemical salt')
    # An edit after inspection clears the button and real opposite stereochemistry
    # produces another vector; no prior source approval follows an edited graph.
    first = _diagram(editor.locator('img'), SALT, 3)
    editor.get_by_role('button', name='Inspect structure', exact=True).click()
    expect(editor.locator('.pw-inspection')).to_contain_text('C3H5NaO3', timeout=30000)
    editor.get_by_role('textbox', name='SMILES', exact=True).fill(SALT.replace('[C@H]', '[C@@H]'))
    expect(editor.locator('.pw-inspection')).to_have_count(0)
    second = _diagram(editor.locator('img'), SALT.replace('[C@H]', '[C@@H]'), 3)
    assert first != second, 'Stereochemical vector remained stale'
    editor.get_by_role('textbox', name='SMILES', exact=True).fill('C1(')
    expect(editor.locator('img')).to_have_count(0)
    expect(editor.locator('[data-structure-state="invalid"]')).to_be_visible(timeout=30000)
    editor.get_by_role('textbox', name='SMILES', exact=True).fill(SALT)
    inspect_confirm(editor)
    editor.get_by_role('textbox', name='Chemistry notes', exact=True).fill('Source review correction; human comparison is still required')
    editor.get_by_role('button', name='Save chemical draft', exact=True).click()
    expect(editor.get_by_role('heading', name='Chemical draft', exact=True)).to_be_visible()
    expect(editor.get_by_role('checkbox', name='I compared this identity, structure and stereochemistry against the cited PDF.', exact=True)).not_to_be_checked()
    inspect_confirm(editor)
    add_chemical(page, 'Synthetic acetaldehyde', 'main:2', 'CC=O')
    add_chemical(page, 'Synthetic glycol solvent', 'glycol', 'OCCO', 'solvent')
    page.get_by_role('button', name='3. Solutions', exact=True).click()
    page.get_by_role('button', name='Add solution', exact=True).click()
    solution = page.get_by_role('region', name='Solution editor', exact=True)
    solution.get_by_label('Solution label', exact=True).fill('stage 1')
    solution.get_by_role('group', name='Solvents', exact=True).get_by_role('checkbox', name='Synthetic glycol solvent', exact=True).check()
    solution.get_by_role('button', name='Add solute', exact=True).click()
    solution.get_by_label('Solute chemical 1', exact=True).select_option(label='Synthetic stereochemical salt')
    solution.get_by_label('Solute role 1', exact=True).fill('substrate')
    solution.get_by_label('Solute amount 1', exact=True).fill('1')
    solution.get_by_label('Solute unit 1', exact=True).fill('mmol')
    solution.get_by_label('Concentration', exact=True).fill('0.1')
    solution.get_by_label('Concentration unit', exact=True).fill('M')
    source(solution, 'Procedure 1; synthetic solvent and solute')
    solution.get_by_role('checkbox', name='I checked these solvents, solutes and amounts against the source.', exact=True).check()
    solution.get_by_role('button', name='Confirm solution', exact=True).click()
    expect(page.locator('.pw-record-list button')).to_have_text('✓ stage 1')
    page.get_by_role('button', name='Add solution', exact=True).click()
    solution.get_by_label('Solution label', exact=True).fill('stage 2')
    solution.get_by_role('group', name='Solvents', exact=True).get_by_role('checkbox', name='Synthetic glycol solvent', exact=True).check()
    solution.get_by_role('button', name='Add solute', exact=True).click()
    solution.get_by_label('Solute chemical 1', exact=True).select_option(label='Synthetic acetaldehyde')
    solution.get_by_label('Solute role 1', exact=True).fill('substrate')
    solution.get_by_label('Solute amount 1', exact=True).fill('0.5')
    solution.get_by_label('Solute unit 1', exact=True).fill('mmol')
    solution.get_by_label('Concentration', exact=True).fill('0.25')
    solution.get_by_label('Concentration unit', exact=True).fill('M')
    source(solution, 'Procedure 2; distinct recorded stage solution')
    solution.get_by_role('checkbox', name='I checked these solvents, solutes and amounts against the source.', exact=True).check()
    solution.get_by_role('button', name='Confirm solution', exact=True).click()
    expect(page.locator('.pw-record-list button').filter(has_text='stage 2')).to_have_text('✓ stage 2')
    page.get_by_role('button', name='4. Reactions', exact=True).click()
    page.get_by_role('button', name='Add reaction', exact=True).click()
    reaction = page.get_by_role('region', name='Reaction editor', exact=True)
    reaction.get_by_label('Reaction label', exact=True).fill('1 to 2')
    reaction.get_by_label('Reaction name', exact=True).fill('Synthetic recorded fixture transformation')
    reaction.get_by_role('group', name='Reactants', exact=True).get_by_role('checkbox', name='Synthetic stereochemical salt', exact=True).check()
    reaction.get_by_role('group', name='Products', exact=True).get_by_role('checkbox', name='Synthetic acetaldehyde', exact=True).check()
    reaction.get_by_label('Reported yield (%)', exact=True).fill('70')
    reaction.get_by_label('Yield basis', exact=True).fill('Two recorded synthetic test stages')
    reaction.get_by_role('button', name='Add stage', exact=True).click()
    reaction.get_by_label('Temperature', exact=True).fill('20 C')
    reaction.get_by_label('Time', exact=True).fill('1 h')
    reaction.get_by_role('button', name='Add stage', exact=True).click()
    reaction.get_by_role('combobox', name='Stage solution', exact=True).nth(1).select_option(label='stage 2')
    reaction.get_by_label('Temperature', exact=True).nth(1).fill('40 C')
    reaction.get_by_label('Time', exact=True).nth(1).fill('2 h')
    source(reaction, 'Scheme 1; Procedure 1 synthetic test')
    reaction.get_by_role('button', name='Add source location', exact=True).click()
    reaction.get_by_label('Source locator 2', exact=True).fill('Procedure 2; separate recorded stage conditions')
    reaction.get_by_role('checkbox', name='I checked all participants, directions, stages and yield against the source.', exact=True).check()
    reaction.get_by_role('button', name='Confirm reaction', exact=True).click()
    page.get_by_role('button', name='5. Export', exact=True).click()
    expect(page.get_by_role('button', name='Recheck and export facts', exact=True)).to_be_enabled()
    expect(page.locator('.react-flow__edge')).to_have_count(2)
    facts_raw, facts = downloaded_json(page, page.get_by_role('button', name='Recheck and export facts', exact=True))
    assert set(facts) == {'schema_version', 'papers', 'chemicals', 'solutions', 'reactions'}
    assert facts['papers'] == [{'id': facts['papers'][0]['id'], 'doi': DOI, 'authors': ['A. Synthetic', 'B. Fixture']}]
    assert len(facts['chemicals']) == 3 and len(facts['solutions']) == 2 and len(facts['reactions']) == 1
    salt = next(c for c in facts['chemicals'] if c['name'] == 'Synthetic stereochemical salt')
    product = next(c for c in facts['chemicals'] if c['name'] == 'Synthetic acetaldehyde')
    solvent = next(c for c in facts['chemicals'] if c['kind'] == 'solvent')
    assert salt['smiles'] == SALT and salt['formula'] == 'C3H5NaO3'
    assert facts['solutions'][0]['solvents'] == [solvent['id']]
    assert facts['solutions'][0]['solutes'][0] == {'chemical_id': salt['id'], 'role': 'substrate', 'amount': 1, 'unit': 'mmol'}
    assert facts['reactions'][0]['reactants'] == [salt['id']] and facts['reactions'][0]['products'] == [product['id']]
    assert facts['reactions'][0]['status'] == 'reviewed'
    assert facts['reactions'][0]['steps'][0]['solution_id'] == facts['solutions'][0]['id']
    assert facts['reactions'][0]['steps'][1] == {'solution_id': facts['solutions'][1]['id'], 'temperature': '40 C', 'time': '2 h', 'notes': ''}
    assert len(facts['reactions'][0]['evidence']) == 2
    forbidden = {'project_schema', 'baseline', 'checked', 'signature', 'inspection', 'sources', 'canonical_smiles', 'engine', 'document', 'pdf', 'text', 'image', 'svg', 'base64', 'pdf_hashes'}
    def check_keys(value):
        if isinstance(value, dict):
            assert not forbidden.intersection(value), forbidden.intersection(value)
            for item in value.values(): check_keys(item)
        elif isinstance(value, list):
            for item in value: check_keys(item)
    check_keys(facts)
    assert OPAQUE.encode() not in facts_raw and b'%PDF-' not in facts_raw
    assert len(facts_raw) < 15000
    page.get_by_role('button', name='Save workspace', exact=True).click()
    _, backup = downloaded_json(page, page.get_by_role('button', name='Backup workspace', exact=True))
    expected_hash = hashlib.sha256((folder / 'synthetic-source.pdf').read_bytes()).hexdigest()
    assert backup['pdf_hashes']['main'] == expected_hash
    assert all(c.get('checked') for c in backup['project']['chemicals'])
    original = page.evaluate('(key)=>localStorage.getItem(key)', WORKSPACE)
    page.reload(wait_until='load')
    expect(page.locator('.pw-notice')).to_contain_text('Private workspace restored')
    expect(page.get_by_label('Private PDF page', exact=True)).to_have_attribute('data-rendered', 'false')
    page.get_by_label('Open local PDF', exact=True).set_input_files(str(folder / 'different-source.pdf'))
    expect(page.get_by_role('alert')).to_contain_text('does not match the saved document fingerprint')
    assert page.evaluate('(key)=>localStorage.getItem(key)', WORKSPACE) == original
    page.get_by_label('Open local PDF', exact=True).set_input_files(str(folder / 'synthetic-source.pdf'))
    expect(canvas).to_have_attribute('data-rendered', 'true', timeout=30000)
    page.get_by_role('button', name='Next page', exact=True).click()
    expect(page.get_by_label('View PDF page', exact=True)).to_have_value('2')
    expect(canvas).to_have_attribute('data-rendered', 'true', timeout=30000)
    page.get_by_text('Private page text and explicit notation candidates', exact=True).click()
    expect(page.locator('.pw-private-text')).to_have_text('No extractable text on this page.')
    expect(page.get_by_role('button', name='Add unchecked notation draft', exact=True)).to_have_count(0)
    return facts_raw, facts, original


def sketcher_and_failure_checks(page, folder, original):
    page.get_by_role('button', name='2. Chemicals', exact=True).click()
    page.locator('.pw-record-list button').filter(has_text='Synthetic stereochemical salt').click()
    editor = page.get_by_role('region', name='Chemical editor', exact=True)
    editor.get_by_text('Draw structure or load a MOL / SDF file', exact=True).click()
    sketcher = editor.get_by_role('region', name='Paper structure sketcher', exact=True)
    expect(sketcher.locator('canvas[tabindex="0"]')).to_be_visible(timeout=30000)
    sketcher.get_by_label('Load MOL/SDF', exact=True).set_input_files(str(folder / 'relative-stereo.mol'))
    expect(sketcher.locator('.paper-sketcher-notice')).to_contain_text('The SMILES field has not changed')
    sketcher.get_by_role('button', name='Use drawn structure', exact=True).click()
    expect(sketcher.locator('.paper-sketcher-notice')).to_contain_text('relative or racemic stereochemistry')
    expect(editor.get_by_role('textbox', name='SMILES', exact=True)).to_have_value(SALT)
    sketcher.get_by_label('Load MOL/SDF', exact=True).set_input_files(str(folder / 'opposite-stereo.mol'))
    expect(sketcher.locator('.paper-sketcher-notice')).to_contain_text('The SMILES field has not changed')
    expect(editor.get_by_role('textbox', name='SMILES', exact=True)).to_have_value(SALT)
    sketcher.get_by_role('button', name='Use drawn structure', exact=True).click()
    expect(sketcher.locator('.paper-sketcher-notice')).to_contain_text('Copied the drawn structure', timeout=30000)
    converted = editor.get_by_role('textbox', name='SMILES', exact=True).input_value()
    assert Chem.MolToInchiKey(Chem.MolFromSmiles(converted)) == Chem.MolToInchiKey(Chem.MolFromSmiles(SALT.replace('[C@H]', '[C@@H]')))
    expect(editor.get_by_role('button', name='Confirm chemical', exact=True)).to_be_disabled()
    mol = (folder / 'opposite-stereo.mol').read_bytes()
    sketcher.get_by_label('Load MOL/SDF', exact=True).set_input_files({
        'name': 'two-molecules.sdf', 'mimeType': 'chemical/x-mdl-sdfile',
        'buffer': mol+b'\n$$$$\n'+mol+b'\n$$$$\n'})
    expect(sketcher.locator('.paper-sketcher-notice')).to_contain_text('exactly one molecule')
    expect(editor.get_by_role('textbox', name='SMILES', exact=True)).to_have_value(converted)
    assert page.evaluate('(key)=>localStorage.getItem(key)', WORKSPACE) == original
    # Bad inputs must not replace the accepted workspace or erase valid PDF.
    for filename, marker in [('encrypted.pdf', 'Encrypted or password-protected'),
                             ('too-many-pages.pdf', '400 pages or fewer')]:
        page.get_by_label('Open local PDF', exact=True).set_input_files(str(folder / filename))
        expect(page.get_by_role('alert')).to_contain_text(marker, timeout=30000)
        assert page.evaluate('(key)=>localStorage.getItem(key)', WORKSPACE) == original
    for payload, marker in [
        ({'name': 'empty.pdf', 'mimeType': 'application/pdf', 'buffer': b''}, 'non-empty local PDF'),
        ({'name': 'oversize.pdf', 'mimeType': 'application/pdf', 'buffer': b'%PDF-'+b' '* (30*1024*1024)}, '30 MB or smaller'),
    ]:
        page.get_by_label('Open local PDF', exact=True).set_input_files(payload)
        expect(page.get_by_role('alert')).to_contain_text(marker)
        assert page.evaluate('(key)=>localStorage.getItem(key)', WORKSPACE) == original
    page.get_by_label('Open local PDF', exact=True).set_input_files({'name': 'not.pdf', 'mimeType': 'application/pdf', 'buffer': b'not a PDF'})
    expect(page.get_by_role('alert')).to_contain_text('PDF file header was not found')
    page.get_by_label('Restore private workspace', exact=True).set_input_files({'name': 'wrong.json', 'mimeType': 'application/json', 'buffer': b'{"format":"bad"}'})
    expect(page.get_by_role('alert')).to_contain_text('Choose a private Paper Workbench backup')
    assert page.evaluate('(key)=>localStorage.getItem(key)', WORKSPACE) == original
    page.set_viewport_size({'width': 390, 'height': 844})
    assert page.evaluate('document.documentElement.scrollWidth <= innerWidth + 1'), 'Workbench mobile horizontal overflow'


def private_storage_failure(browser, documents, url, original):
    init = '''(()=>{const key=KEY,raw=RAW;localStorage.setItem(key,raw);
      const read=Storage.prototype.getItem,write=Storage.prototype.setItem;
      Storage.prototype.setItem=function(k,v){if(k===key)throw new DOMException('Private storage full','QuotaExceededError');return write.call(this,k,v)};
      globalThis.__originalPrivate=()=>read.call(localStorage,key);})();'''.replace('KEY', json.dumps(WORKSPACE)).replace('RAW', json.dumps(original))
    state = context_for(browser, documents, init)
    context, page = state[:2]
    try:
        start(page, url)
        expect(page.locator('.pw-notice')).to_contain_text('Private workspace restored')
        page.get_by_role('button', name='Save workspace', exact=True).click()
        expect(page.get_by_role('alert')).to_contain_text('Private storage full')
        assert page.evaluate('globalThis.__originalPrivate()') == original
        _, backup = downloaded_json(page, page.get_by_role('button', name='Backup workspace', exact=True))
        assert backup == json.loads(original)
        verify_resources(state, documents)
    finally:
        context.close()


def handoff_baseline(facts, mode='empty'):
    """Real old-library states; no direct import-helper-derived expectations."""
    baseline = deepcopy(facts)
    for c in baseline['chemicals']:
        if mode == 'empty':
            for field in ['smiles', 'formula', 'inchikey', 'molecular_weight']:
                c[field] = None
        c['notes'] = 'Private existing annotation to preserve'
        c['aliases'].append('Private existing alias')
    reaction = baseline['reactions'][0]
    reaction['notes'] = 'Private existing reaction note'
    reaction['status'] = 'draft'
    reaction['evidence'] = [{'paper_id': baseline['papers'][0]['id'], 'page': 2,
                             'locator': 'Existing private source locator'}]
    if mode in ['empty', 'facts-only-empty', 'empty-composition']:
        reaction['steps'] = []
        reaction['yield_percent'] = None
        reaction['yield_basis'] = None
        for solution in baseline['solutions']:
            solution['concentration'] = solution['concentration_unit'] = None
            for solute in solution['solutes']:
                solute['amount'] = solute['unit'] = None
        if mode == 'empty-composition':
            baseline['solutions'][0]['solvents'] = []
            baseline['solutions'][0]['solutes'] = []
    elif mode == 'partial':
        reaction['steps'][0]['time'] = None
        reaction['steps'][0]['notes'] = 'Private stage note retained'
        reaction['steps'][1]['temperature'] = None
        reaction['yield_basis'] = None
        baseline['solutions'][0]['concentration_unit'] = None
        baseline['solutions'][0]['solutes'][0]['unit'] = None
        baseline['solutions'][1]['concentration'] = baseline['solutions'][1]['concentration_unit'] = None
        baseline['solutions'][1]['solutes'][0]['amount'] = None
    elif mode == 'prefix':
        reaction['steps'] = reaction['steps'][:1]
        reaction['steps'][0]['notes'] = 'Private stage note retained'
        baseline['solutions'] = baseline['solutions'][:1]
    # Include shipped feed data so the ordinary startup feed merge need not
    # rewrite this deliberately formatted exact-original baseline.
    seed = json.loads((ROOT / 'public/library.json').read_bytes())
    for table in ['papers', 'chemicals', 'solutions', 'reactions']:
        baseline[table].extend(seed[table])
    return baseline


def receiving_context(browser, url, documents, baseline):
    baseline_raw = json.dumps(baseline, indent=3)+'\n'
    # Install once per profile, not at every reload: persistence is under test.
    init = '''(()=>{const once='chembrain.test-baseline-installed';if(!sessionStorage.getItem(once)){
      localStorage.setItem(KEY,RAW);sessionStorage.setItem(once,'yes');}})();'''.replace('KEY', json.dumps(LIBRARY)).replace('RAW', json.dumps(baseline_raw))
    state = context_for(browser, documents, init)
    page = state[1]
    page.goto(url, wait_until='load')
    expect(page.get_by_role('heading', name='Your molecular library', exact=True)).to_be_visible()
    expect(page.get_by_role('button', name='Import package', exact=True)).to_be_enabled()
    assert page.evaluate('(key)=>localStorage.getItem(key)', LIBRARY) == baseline_raw, 'Fixture changed during ordinary feed merge'
    return state, baseline_raw


def import_package(page, raw):
    page.get_by_label('Import normalized library', exact=True).set_input_files({
        'name': 'chembrain-reviewed-facts.json', 'mimeType': 'application/json', 'buffer': raw})


def import_backups(page):
    return page.evaluate('''()=>Object.keys(localStorage).filter(k=>k.includes('.import-backup.')).map(k=>localStorage.getItem(k))''')


def assert_received_facts(page, facts, mode):
    stored = json.loads(page.evaluate('(key)=>localStorage.getItem(key)', LIBRARY))
    for source_solution in facts['solutions']:
        actual = next(s for s in stored['solutions'] if s['id'] == source_solution['id'])
        assert actual == source_solution, ('Incomplete source solution transfer', mode, actual, source_solution)
    expected = facts['reactions'][0]
    received = next(r for r in stored['reactions'] if r['id'] == expected['id'])
    assert len(received['steps']) == 2
    assert [step['solution_id'] for step in received['steps']] == [step['solution_id'] for step in expected['steps']]
    for actual, wanted in zip(received['steps'], expected['steps'], strict=True):
        assert actual['temperature'] == wanted['temperature'] and actual['time'] == wanted['time']
        assert any(s['id'] == actual['solution_id'] for s in stored['solutions']), 'Imported stage is disconnected'
    if mode in ['partial', 'prefix']:
        assert received['steps'][0]['notes'] == 'Private stage note retained'
    assert received['yield_percent'] == expected['yield_percent'] == 70
    assert received['yield_basis'] == expected['yield_basis']
    assert received['status'] == 'draft', 'Import promoted local scientific review status'
    assert received['notes'] == 'Private existing reaction note'
    assert len(received['evidence']) == 3
    for evidence in expected['evidence']:
        assert evidence in received['evidence']
    assert any(e['locator'] == 'Existing private source locator' for e in received['evidence'])
    for source_chemical in facts['chemicals']:
        row = next(c for c in stored['chemicals'] if c['id'] == source_chemical['id'])
        assert row['notes'] == 'Private existing annotation to preserve'
        assert 'Private existing alias' in row['aliases']
        assert row['smiles'] == source_chemical['smiles']
    return stored


def main_handoff(browser, url, documents, raw, facts):
    for mode in ['empty', 'partial', 'facts-only-empty', 'empty-composition', 'prefix']:
        state, baseline_raw = receiving_context(browser, url, documents, handoff_baseline(facts, mode))
        context, page = state[:2]
        try:
            import_package(page, raw)
            review = page.get_by_role('region', name='Review paper import', exact=True)
            expect(review).to_be_visible()
            expect(review.get_by_role('button', name='Apply import', exact=True)).to_be_enabled()
            changes = review.get_by_role('list', name='Existing chemistry changes', exact=True)
            expect(changes).to_be_visible()
            expect(changes).to_contain_text('reaction')
            if mode != 'prefix':
                expect(changes).to_contain_text('1 h')
            expect(changes).to_contain_text('40 C')
            if mode != 'prefix':
                expect(changes).to_contain_text('solution')
                expect(changes).to_contain_text('0.25')
            assert page.evaluate('(key)=>localStorage.getItem(key)', LIBRARY) == baseline_raw
            assert import_backups(page) == []
            review.get_by_role('button', name='Apply import', exact=True).click()
            expect(review).to_have_count(0)
            expect(page.locator('.web-notice')).to_contain_text('Import complete')
            stored = assert_received_facts(page, facts, mode)
            assert import_backups(page) == [baseline_raw], ('No exact original backup for fact enrichment', mode)
            chemical = next(c for c in facts['chemicals'] if c['name'] == 'Synthetic stereochemical salt')
            tile = page.locator('.molecule-tile').filter(has=page.get_by_text(chemical['name'], exact=True))
            _diagram(tile.locator('img'), chemical['smiles'], 3)
            tile.click()
            expect(page.locator('.react-flow__edge')).to_have_count(2)
            _diagram(page.locator('.react-flow__node[data-id="chemical:'+chemical['id']+'"] img'), chemical['smiles'], 3)
            # Reload genuinely uses the accepted persistent value, never the
            # fixture's install script. The detailed stage UI uses those facts.
            before = page.evaluate('(key)=>localStorage.getItem(key)', LIBRARY)
            page.reload(wait_until='load')
            expect(page.get_by_role('button', name='Import package', exact=True)).to_be_enabled()
            assert json.loads(page.evaluate('(key)=>localStorage.getItem(key)', LIBRARY)) == stored
            tile.click()
            page.get_by_role('tab', name='List', exact=True).click()
            page.locator('.reaction-summary').filter(has_text='Synthetic recorded fixture transformation').click()
            expect(page.locator('.reaction-expanded .step')).to_have_count(2)
            expect(page.locator('.reaction-expanded')).to_contain_text('40 C')
            expect(page.locator('.reaction-expanded')).to_contain_text('0.25')
            # Repeated identical facts do not rewrite primary bytes or create
            # another backup, even though private notes/status were retained.
            page.evaluate('''()=>{globalThis.__handoffPrimaryWrites=0;const write=Storage.prototype.setItem;
              Storage.prototype.setItem=function(k,v){if(k==='chembrain.normalized-library.v1')globalThis.__handoffPrimaryWrites++;return write.call(this,k,v)}}''')
            import_package(page, raw)
            expect(page.locator('.web-notice')).to_contain_text(re.compile(r'no changes|already up.to.date|nothing.*chang', re.I))
            expect(page.get_by_role('region', name='Review paper import', exact=True)).to_have_count(0)
            assert page.evaluate('(key)=>localStorage.getItem(key)', LIBRARY) == before
            assert page.evaluate('globalThis.__handoffPrimaryWrites') == 0
            assert import_backups(page) == [baseline_raw]
            verify_resources(state, documents)
        finally:
            context.close()
        print('PAPER_TRANSFER_CHECK: '+mode+' persisted all ordered source facts, protected local edits and exact backup; repeated import was a no-op', flush=True)


def receiving_conflicts(browser, url, documents, raw, facts):
    for mode in ['temperature', 'time', 'amount', 'unit', 'concentration', 'yield', 'yield-basis', 'order', 'composition', 'role']:
        baseline = handoff_baseline(facts, 'partial')
        reaction = baseline['reactions'][0]
        solution = baseline['solutions'][0]
        if mode == 'temperature': reaction['steps'][0]['temperature'] = '99 C'
        elif mode == 'time': reaction['steps'][1]['time'] = '99 h'
        elif mode == 'amount': solution['solutes'][0]['amount'] = 99
        elif mode == 'unit': solution['solutes'][0]['unit'] = 'g'
        elif mode == 'concentration': solution['concentration'] = 99
        elif mode == 'yield': reaction['yield_percent'] = 99
        elif mode == 'yield-basis': reaction['yield_basis'] = 'Conflicting yield context'
        elif mode == 'order': reaction['steps'].reverse()
        elif mode == 'composition': solution['solvents'] = [facts['chemicals'][1]['id']]
        elif mode == 'role': solution['solutes'][0]['role'] = 'catalyst'
        state, baseline_raw = receiving_context(browser, url, documents, baseline)
        context, page = state[:2]
        try:
            import_package(page, raw)
            review = page.get_by_role('region', name='Review paper import', exact=True)
            expect(review).to_be_visible()
            expect(review.get_by_role('button', name='Apply import', exact=True)).to_have_count(0)
            expect(review).to_contain_text('Paper Workbench')
            expect(review).to_contain_text('Backup JSON')
            expect(review.locator('.import-conflicts')).to_be_visible()
            if mode in ['temperature', 'time', 'amount', 'concentration', 'yield']:
                expect(review.locator('.import-conflicts')).to_contain_text('99')
            assert page.evaluate('(key)=>localStorage.getItem(key)', LIBRARY) == baseline_raw, mode
            assert import_backups(page) == [], mode
            verify_resources(state, documents)
        finally:
            context.close()
    print('PAPER_TRANSFER_CHECK: known conditions/amounts/units/concentration/yield/basis, stage order, composition and roles all require visible reconciliation; no writes', flush=True)


def receiving_failures(browser, url, documents, raw, facts):
    for mode in ['backup-write', 'backup-readback', 'primary-write', 'stale', 'concurrent-backup']:
        baseline = handoff_baseline(facts, 'facts-only-empty')
        state, baseline_raw = receiving_context(browser, url, documents, baseline)
        context, page = state[:2]
        try:
            sentinel_key = LIBRARY+'.import-backup.pre-existing'
            sentinel = 'Previous private backup remains byte-for-byte unchanged'
            page.evaluate('({key,value})=>localStorage.setItem(key,value)', {'key': sentinel_key, 'value': sentinel})
            import_package(page, raw)
            review = page.get_by_role('region', name='Review paper import', exact=True)
            expect(review.get_by_role('button', name='Apply import', exact=True)).to_be_enabled()
            alternate = deepcopy(baseline)
            alternate['reactions'][0]['notes'] = 'Concurrent external private edit'
            alternate_raw = json.dumps(alternate, indent=2)+'\n'
            page.evaluate('''({mode,alternate})=>{const key='chembrain.normalized-library.v1';
              const read=Storage.prototype.getItem,write=Storage.prototype.setItem;
              globalThis.__handoffRead=k=>read.call(localStorage,k);
              if(mode==='stale')write.call(localStorage,key,alternate);
              Storage.prototype.getItem=function(k){if(mode==='backup-readback'&&k.includes('.import-backup.'))return 'Invalid backup readback';return read.call(this,k)};
              Storage.prototype.setItem=function(k,v){
                if((mode==='backup-write'&&k.includes('.import-backup.'))||(mode==='primary-write'&&k===key))throw new DOMException('Simulated full storage','QuotaExceededError');
                write.call(this,k,v);
                if(mode==='concurrent-backup'&&k.includes('.import-backup.'))write.call(this,key,alternate);
              };}''', {'mode': mode, 'alternate': alternate_raw})
            review.get_by_role('button', name='Apply import', exact=True).click()
            expect(page.get_by_role('alert')).to_be_visible()
            expect(review).to_be_visible()
            expected_raw = alternate_raw if mode in ['stale', 'concurrent-backup'] else baseline_raw
            assert page.evaluate('(key)=>globalThis.__handoffRead(key)', LIBRARY) == expected_raw, mode
            assert page.evaluate('(key)=>globalThis.__handoffRead(key)', sentinel_key) == sentinel, mode
            _, visible = downloaded_json(page, page.get_by_role('button', name='Backup JSON', exact=True))
            assert visible['reactions'][0]['steps'] == [], 'Working UI switched to an unpersisted proposed route'
            assert visible['solutions'][0]['concentration'] is None
            assert all(c['smiles'] for c in visible['chemicals'][:3]), 'Fact-only failure damaged existing structures'
            verify_resources(state, documents)
        finally:
            context.close()
    print('PAPER_TRANSFER_CHECK: fact-only backup write/readback, primary quota, stale review and concurrent-backup failures preserved primary and working route', flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--http-only', action='store_true', help='Mocked HTTP only; does not verify file://.')
    args = parser.parse_args()
    paper, paper_manifest = artifact('Chembrain-Paper-Workbench.html', 'paper-manifest.json')
    main_html, main_manifest = artifact('Chembrain.html', 'browser-manifest.json')
    assert paper_manifest['source_commit'] == main_manifest['source_commit'], 'Paper/main packages must share exact source'
    paper_url = 'http://127.0.0.1/paper-workbench-smoke' if args.http_only else (ROOT / 'release/Chembrain-Paper-Workbench.html').as_uri()
    main_url = 'http://127.0.0.1/main-handoff-smoke' if args.http_only else (ROOT / 'release/Chembrain.html').as_uri()
    documents = {paper_url: paper if args.http_only else None, main_url: main_html if args.http_only else None}
    with tempfile.TemporaryDirectory(prefix='chembrain-private-workbench-') as temporary:
        folder = Path(temporary)
        make_fixtures(folder)
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(executable_path=os.environ.get('CHROMIUM_PATH') or shutil.which('chromium'), args=['--no-sandbox'])
            state = context_for(browser, documents)
            context, page = state[:2]
            try:
                raw, facts, original = create_checked_package(page, paper_url, folder)
                print('PAPER_CHECK: source PDF, checked chemistry, strict facts export and private reload passed', flush=True)
                sketcher_and_failure_checks(page, folder, original)
                print('PAPER_CHECK: explicit sketcher transfer, relative-stereo refusal, PDF bounds and failure preservation passed', flush=True)
                verify_resources(state, documents, require_worker=True)
                private_storage_failure(browser, documents, paper_url, original)
                print('PAPER_CHECK: private storage failure retained the last valid workspace and backup', flush=True)
                main_handoff(browser, main_url, documents, raw, facts)
                receiving_conflicts(browser, main_url, documents, raw, facts)
                receiving_failures(browser, main_url, documents, raw, facts)
            finally:
                context.close()
                browser.close()
    mode = 'PAPER_HTTP_ONLY_PASS: mocked HTTP bytes (file:// NOT VERIFIED)' if args.http_only else 'PAPER_OFFLINE_PASS: actual file://'
    print(mode+'; real local blob PDF worker, rendered canvas and explicit candidates; no DOI auto-selection, no invented image chemistry/OCR; checked stereo/charge/fragments, solution/recorded arrows, strict downloaded facts → explicit main import, exact backup/local-note preservation and idempotency; private hash pairing/reload, mismatched/encrypted/over-limit PDF rejection; MOL sketcher explicit transfer; zero external requests; source='+paper_manifest['source_commit']+' paper_sha256='+paper_manifest['sha256']+' main_sha256='+main_manifest['sha256'])


if __name__ == '__main__':
    main()
