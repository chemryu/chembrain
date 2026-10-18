"""Exercise explicit example enrichment against real private browser storage."""
import copy
import json
from pathlib import Path

from playwright.sync_api import expect

ROOT = Path(__file__).resolve().parents[1]
STORE = 'chembrain.normalized-library.v1'


def check_structure_upgrade(page):
    original = page.evaluate('(k)=>localStorage.getItem(k)', STORE)
    old_keys = page.evaluate('Object.keys(localStorage)')
    seed = json.loads((ROOT / 'public/library.json').read_text())
    legacy = copy.deepcopy(seed)
    for c in legacy['chemicals']:
        if c['id'] in ['paclitaxel', 'doxycycline']:
            c['smiles'] = None
            c.pop('inchikey', None)
            c.pop('molecular_weight', None)
            c['notes'] = 'My private structure annotation'
            c['aliases'].append('Private alias')
    legacy['reactions'][0]['name'] = 'My private reaction edit'
    legacy['solutions'][0]['concentration'] = 0.125

    def load(data):
        raw = json.dumps(data, indent=3, ensure_ascii=False) + '\n'
        page.evaluate('([k,v])=>localStorage.setItem(k,v)', [STORE, raw])
        page.reload(wait_until='load')
        expect(page.locator('.molecule-tile').first).to_be_visible()
        # Loading identical normalized data must preserve even its whitespace.
        assert page.evaluate('(k)=>localStorage.getItem(k)', STORE) == raw
        return raw

    def stored():
        return page.evaluate('(k)=>localStorage.getItem(k)', STORE)

    button = page.get_by_role('button', name='Add verified example structures', exact=True)
    try:
        raw = load(legacy)
        expect(button).to_be_visible()
        button.click()
        expect(page.get_by_role('status')).to_contain_text('Verified example structures added')
        updated = json.loads(stored())
        for before, after in zip(legacy['chemicals'], updated['chemicals']):
            if before['id'] in ['paclitaxel', 'doxycycline']:
                for k, v in before.items():
                    if k != 'smiles':
                        assert after[k] == v, (k, 'custom chemistry metadata overwritten')
                expected = next(c for c in seed['chemicals'] if c['id'] == before['id'])
                for k in ['smiles', 'inchikey', 'formula', 'molecular_weight']:
                    assert after[k] == expected[k]
            else:
                assert before == after
        for table in ['reactions', 'solutions', 'papers']:
            assert updated[table] == legacy[table]
        backups = page.evaluate('Object.keys(localStorage).filter(k=>k.includes(".structure-backup.")).map(k=>localStorage.getItem(k))')
        assert raw in backups
        expect(button).to_have_count(0)
        page.locator('.molecule-tile').filter(has=page.locator('strong', has_text='Paclitaxel (Taxol)')).click()
        expect(page.locator('.selected-structure img')).to_have_count(1, timeout=30000)
        expect(page.locator('.molecule-note')).to_contain_text('My private structure annotation')
        with page.expect_download() as download:
            page.get_by_role('button', name='Backup JSON', exact=True).click()
        assert json.loads(Path(download.value.path()).read_bytes()) == updated
        page.reload(wait_until='load')
        assert json.loads(stored()) == updated

        # ID alone must never select an imported row with changed identity.
        for changed in [{'name': 'My different molecule'}, {'smiles': 'CCO'},
                        {'formula': 'C2H6O'}, {'inchikey': 'USER-IDENTITY'},
                        {'molecular_weight': 123.45}, {'kind': 'reagent'}]:
            candidate = copy.deepcopy(legacy)
            candidate['chemicals'][0].update(changed)
            load(candidate)
            button.click()
            after = json.loads(stored())
            assert after['chemicals'][0] == candidate['chemicals'][0], changed
            assert after['chemicals'][1]['smiles'], changed

        for failure in ['backup', 'backup-readback', 'primary', 'concurrent']:
            raw = load(legacy)
            if failure == 'concurrent':
                raw += ' '
                changed = copy.deepcopy(legacy)
                changed['chemicals'][0]['notes'] = 'Another tab changed the library'
                raw = json.dumps(changed, indent=2)
                page.evaluate('([k,v])=>localStorage.setItem(k,v)', [STORE, raw])
            else:
                page.evaluate('''([key,failure])=>{
                  const set=Storage.prototype.setItem,get=Storage.prototype.getItem;
                  Storage.prototype.setItem=function(k,v){
                    if((failure==='backup'&&k.includes('.structure-backup.'))||(failure==='primary'&&k===key))throw new DOMException('Storage full','QuotaExceededError');
                    return set.call(this,k,v);
                  };
                  Storage.prototype.getItem=function(k){return failure==='backup-readback'&&k.includes('.structure-backup.')?'wrong backup':get.call(this,k)};
                }''', [STORE, failure])
            button.click()
            expect(page.get_by_role('alert')).to_be_visible()
            assert stored() == raw, (failure, 'original primary bytes changed')
            expect(button).to_be_visible()
            page.reload(wait_until='load')  # restores the normal Storage prototype
    finally:
        page.reload(wait_until='load')
        page.evaluate('''([key,raw,oldKeys])=>{
          for(const k of Object.keys(localStorage))if(!oldKeys.includes(k))localStorage.removeItem(k);
          if(raw===null)localStorage.removeItem(key);else localStorage.setItem(key,raw);
        }''', [STORE, original, old_keys])
        page.reload(wait_until='load')
        expect(page.get_by_role('heading', name='Select a molecule', exact=True)).to_be_visible()
        assert stored() == original
