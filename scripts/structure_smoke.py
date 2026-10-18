"""Shared real-browser checks of structures in hosted and offline builds.

The assertions decode RDKit's actual SVG bond paths, rather than accepting a
placeholder image. Temporary imported/edited chemistry lives only in the smoke
browser, and the exact original storage bytes are restored even after failure.
"""
import json
from pathlib import Path
import re
from urllib.parse import unquote
import xml.etree.ElementTree as ET

from playwright.sync_api import expect

STORE = 'chembrain.normalized-library.v1'
ROOT = Path(__file__).resolve().parents[1]


def _tile(page, name):
    return page.locator('.molecule-tile').filter(
        has=page.get_by_text(name, exact=True))


def _diagram(image, smiles, minimum_bonds=1):
    """Require a decoded, loaded vector drawing with nonempty chemical bonds."""
    expect(image).to_have_count(1, timeout=30000)
    expect(image).to_have_attribute('data-structure-state', 'ready', timeout=30000)
    expect(image).to_have_attribute('data-smiles', smiles)
    expect(image).to_have_js_property('complete', True, timeout=30000)
    expect(image).to_have_js_property('naturalWidth', 600, timeout=30000)
    expect(image).to_have_js_property('naturalHeight', 360)
    source = image.get_attribute('src')
    assert source.startswith('data:image/svg+xml;charset=utf-8,'), source[:100]
    svg = unquote(source.partition(',')[2])
    root = ET.fromstring(svg)
    assert root.tag == '{http://www.w3.org/2000/svg}svg'
    paths = [node for node in root.iter()
             if node.tag == '{http://www.w3.org/2000/svg}path'
             and re.search(r'\bbond-\d+\b', node.get('class', ''))
             and node.get('d', '').strip()]
    assert len(paths) >= minimum_bonds, ('No real chemical bond drawing', len(paths))
    assert len({node.get('d') for node in paths}) > 1
    # The data-image document must contain vector geometry, never a source paper
    # raster, embedded external document or script masquerading as a diagram.
    assert not any(node.tag.rsplit('}', 1)[-1] in
                   {'image', 'script', 'foreignObject'} for node in root.iter())
    assert not any(key.rsplit('}', 1)[-1] == 'href'
                   for node in root.iter() for key in node.attrib)
    return source


def _edit(page, *, name=None, smiles=None):
    page.get_by_role('button', name='Edit molecule', exact=True).click()
    dialog = page.get_by_role('dialog', name='Edit normalized record', exact=True)
    if name is not None:
        dialog.get_by_label('Molecule name', exact=True).fill(name)
    if smiles is not None:
        dialog.get_by_label(re.compile(r'^SMILES')).fill(smiles)
    dialog.get_by_role('button', name='Validate & save', exact=True).click()
    expect(dialog).to_have_count(0)


def wait_for_seed_tile_images(page):
    seed = json.loads((ROOT / 'public/library.json').read_text())
    expected = sum(bool(row.get('smiles')) for row in seed['chemicals']
                   if row['kind'] == 'compound')
    expect(page.locator('.molecule-tile img')).to_have_count(expected, timeout=30000)
    page.wait_for_function('''()=>Array.from(document.querySelectorAll('.molecule-tile img'))
      .every(image=>image.src.startsWith('data:image/svg+xml')&&image.complete&&image.naturalWidth>0)''')


def check_structures(page):
    original = page.evaluate('(key)=>localStorage.getItem(key)', STORE)
    viewport = page.viewport_size
    seed = json.loads((ROOT / 'public/library.json').read_text())
    try:
        for identity, name, minimum_bonds in [
            ('paclitaxel', 'Paclitaxel (Taxol)', 40),
            ('doxycycline', 'Doxycycline', 20),
        ]:
            chemical = next(row for row in seed['chemicals'] if row['id'] == identity)
            smiles = chemical['smiles']
            assert smiles and '@' in smiles, ('Target stereo missing', identity)
            tile = _tile(page, name)
            drawn = _diagram(tile.locator('img'), smiles, minimum_bonds)
            tile.click()
            expect(page.locator('.selected-heading h2')).to_have_text(name)
            expect(page.get_by_role('tab', name='Map', exact=True)).to_have_attribute('aria-selected', 'true')
            assert _diagram(page.locator('img.structure-diagram-large'), smiles,
                            minimum_bonds) == drawn
            node = page.locator(f'.react-flow__node[data-id="chemical:{identity}"]')
            assert _diagram(node.locator('img'), smiles, minimum_bonds) == drawn
            assert page.evaluate('(key)=>localStorage.getItem(key)', STORE) == original, 'Viewing structure saved chemistry'

        # Unknown local paper-numbered intermediates must stay visibly unknown.
        unknown = _tile(page, 'Holton compound 24b')
        expect(unknown.locator('img')).to_have_count(0)
        expect(unknown.locator('[data-structure-state="missing"]')).to_contain_text('Structure not encoded')
        unknown.click()
        expect(page.locator('.structure-diagram-large[data-structure-state="missing"]')).to_contain_text('verified')
        expect(page.locator('.react-flow__node[data-id="chemical:holton-24b"] img')).to_have_count(0)

        # This chiral zwitterion plus sodium/chloride is deliberately absent from
        # all seed IDs/names/manifests. Real imported SMILES must draw on its own.
        smiles = 'C[C@H]([NH3+])C(=O)[O-].[Na+].[Cl-]'
        identity = 'browser-structure-fixture'
        name = 'Browser stereochemical salt fixture'
        incoming = json.loads(original) if original is not None else seed
        incoming['chemicals'].append({'id': identity, 'name': name, 'kind': 'compound',
                                     'aliases': [], 'smiles': smiles})
        incoming['reactions'].append({**incoming['reactions'][0],
            'id': 'browser-structure-reaction', 'name': 'Browser drawing fixture reaction',
            'reactants': ['paclitaxel'], 'products': [identity], 'targets': [identity]})
        page.get_by_label('Import normalized library').set_input_files({
            'name': 'structure-fixture.json', 'mimeType': 'application/json',
            'buffer': json.dumps(incoming).encode()})
        expect(page.locator('.web-notice')).to_contain_text('Import complete')
        tile = _tile(page, name)
        drawn = _diagram(tile.locator('img'), smiles, 4)
        tile.click()
        assert _diagram(page.locator('img.structure-diagram-large'), smiles, 4) == drawn
        node = page.locator(f'.react-flow__node[data-id="chemical:{identity}"]')
        assert _diagram(node.locator('img'), smiles, 4) == drawn
        assert '.' in smiles and '@' in smiles and '+' in smiles and '-' in smiles

        # A name edit must not invalidate the same molecular graph. An opposite
        # stereocenter must change the encoded vector drawing immediately.
        renamed = 'Renamed browser stereochemical salt fixture'
        _edit(page, name=renamed)
        expect(_tile(page, name)).to_have_count(0)
        tile = _tile(page, renamed)
        assert _diagram(tile.locator('img'), smiles, 4) == drawn
        expect(tile.locator('img')).to_have_attribute('alt', renamed + ' structure diagram')
        edited = smiles.replace('[C@H]', '[C@@H]')
        _edit(page, smiles=edited)
        changed = _diagram(tile.locator('img'), edited, 4)
        assert changed != drawn, 'SMILES stereochemistry changed but the old diagram remained'
        assert _diagram(page.locator('img.structure-diagram-large'), edited, 4) == changed
        assert _diagram(node.locator('img'), edited, 4) == changed

        # Invalid input remains an editable chemistry fact but cannot reuse the
        # last valid image in a tile, selected view or reaction-map molecule.
        _edit(page, smiles='C1(')
        for scope in (tile, page.locator('.selected-structure'), node):
            expect(scope.locator('img')).to_have_count(0)
            expect(scope.locator('[data-structure-state="invalid"]')).to_contain_text('Invalid SMILES', timeout=30000)
        _edit(page, smiles='')
        expect(tile.locator('[data-structure-state="missing"]')).to_contain_text('Structure not encoded')
        expect(page.locator('img.structure-diagram-large')).to_have_count(0)
        _edit(page, smiles=edited)
        assert _diagram(tile.locator('img'), edited, 4) == changed
        page.reload(wait_until='load')
        _tile(page, renamed).click()
        assert _diagram(page.locator('img.structure-diagram-large'), edited, 4) == changed

        # JSON backups contain editable chemistry only. In a fresh import after
        # removing this disposable profile's saved data, diagrams regenerate.
        with page.expect_download() as downloaded:
            page.get_by_role('button', name='Backup JSON', exact=True).click()
        backup = Path(downloaded.value.path()).read_bytes()
        parsed = json.loads(backup)
        row = next(chemical for chemical in parsed['chemicals'] if chemical['id'] == identity)
        assert row['smiles'] == edited and row['name'] == renamed
        assert not {'image', 'svg', 'base64'} & set(row)
        page.evaluate('(key)=>localStorage.removeItem(key)', STORE)
        page.reload(wait_until='load')
        page.get_by_label('Import normalized library').set_input_files({
            'name': 'structure-backup.json', 'mimeType': 'application/json', 'buffer': backup})
        expect(page.locator('.web-notice')).to_contain_text('Import complete')
        _tile(page, renamed).click()
        assert _diagram(page.locator('img.structure-diagram-large'), edited, 4) == changed
        page.set_viewport_size({'width': 390, 'height': 844})
        large = page.locator('img.structure-diagram-large')
        large.scroll_into_view_if_needed()
        box = large.bounding_box()
        assert box['width'] >= 200 and box['height'] >= 100, ('Unreadable mobile structure', box)
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth + 1'), 'Structure mobile horizontal overflow'
    finally:
        page.evaluate('''(raw)=>{const key='chembrain.normalized-library.v1';
          if(raw===null)localStorage.removeItem(key);else localStorage.setItem(key,raw)}''', original)
        if viewport:
            page.set_viewport_size(viewport)
        page.reload(wait_until='load')
        expect(page.get_by_role('heading', name='Select a molecule', exact=True)).to_be_visible()
        assert page.evaluate('(key)=>localStorage.getItem(key)', STORE) == original
