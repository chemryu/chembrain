"""Shared real-browser checks for reviewed paper-package → main-library transfer.

Chemistry below is explicitly disposable test data, not a Holton structure claim.
The caller supplies either its hosted page or the actual offline HTML page.
"""
import copy
import json
from pathlib import Path

from playwright.sync_api import expect
from structure_smoke import _diagram

ROOT = Path(__file__).resolve().parents[1]
STORE = 'chembrain.normalized-library.v1'


def check_import_handoff(page):
    original = page.evaluate('(key)=>localStorage.getItem(key)', STORE)
    original_keys = page.evaluate('Object.keys(localStorage)')
    seed = json.loads((ROOT / 'public/library.json').read_text())
    baseline = copy.deepcopy(seed)
    target_id = 'holton-17'
    target = next(c for c in baseline['chemicals'] if c['id'] == target_id)
    target.update(smiles=None, notes='My private handoff note', aliases=['My private alias'])
    for field in ['formula', 'inchikey', 'molecular_weight']:
        target.pop(field, None)
    baseline['reactions'][0]['notes'] = 'Private reaction edit kept'
    baseline['solutions'][0]['concentration'] = 0.123
    incoming = copy.deepcopy(baseline)
    imported_target = next(c for c in incoming['chemicals'] if c['id'] == target_id)
    imported_target.update(smiles='CCOC', formula='C3H8O', inchikey='XOBKSJJDNFUZPF-UHFFFAOYSA-N',
                           molecular_weight=60.1, notes='Incoming fixture note', aliases=['Incoming alias'])
    paper_label = 'Paper label 17; DOI ' + incoming['papers'][0]['doi']
    imported_target['aliases'].append(paper_label)
    new_id = 'paper-handoff-product'
    incoming['chemicals'].append({'id': new_id, 'name': 'Handoff product fixture', 'kind': 'compound',
                                  'aliases': [], 'smiles': 'C=O'})
    reaction_id = 'paper-handoff-reaction'
    incoming['reactions'].append({**copy.deepcopy(incoming['reactions'][0]), 'id': reaction_id,
                                  'name': 'Handoff fixture reaction', 'reactants': [target_id],
                                  'products': [new_id], 'targets': [new_id]})

    def stored():
        return page.evaluate('(key)=>localStorage.getItem(key)', STORE)

    def load(data):
        raw = json.dumps(data, indent=3, ensure_ascii=False) + '\n'
        page.evaluate('([key,raw])=>localStorage.setItem(key,raw)', [STORE, raw])
        page.reload(wait_until='load')
        expect(page.locator('.molecule-tile').first).to_be_visible()
        assert stored() == raw
        return raw

    def upload(package):
        page.get_by_label('Import normalized library').set_input_files({
            'name': 'paper-handoff.json', 'mimeType': 'application/json',
            'buffer': json.dumps(package).encode()})

    def backups():
        return page.evaluate('Object.keys(localStorage).filter(k=>k.includes(".import-backup.")).map(k=>localStorage.getItem(k))')

    review = page.get_by_role('region', name='Review paper import', exact=True)
    apply = review.get_by_role('button', name='Apply import', exact=True)
    try:
        raw = load(baseline)
        previous_backups = backups()
        upload(incoming)
        expect(review).to_be_visible()
        expect(review).to_contain_text('Holton compound 17')
        expect(apply).to_be_visible()
        assert stored() == raw and backups() == previous_backups
        _diagram(review.locator('img'), 'CCOC')
        review.get_by_role('button', name='Cancel import', exact=True).click()
        expect(review).to_have_count(0)
        assert stored() == raw and backups() == previous_backups

        upload(incoming)
        expect(apply).to_be_visible()
        apply.click()
        expect(review).to_have_count(0)
        expect(page.locator('.web-notice')).to_contain_text('1 existing structures added')
        after = json.loads(stored())
        assert raw in backups() and len(backups()) == len(previous_backups) + 1
        upgraded = next(c for c in after['chemicals'] if c['id'] == target_id)
        for field, value in target.items():
            if field not in ['smiles', 'aliases']:
                assert upgraded[field] == value, ('Existing chemical edit replaced', field)
        assert upgraded['aliases'] == target['aliases'] + [paper_label]
        for field in ['smiles', 'formula', 'inchikey', 'molecular_weight']:
            assert upgraded[field] == imported_target[field]
        for table in ['reactions', 'solutions', 'papers']:
            for old in baseline[table]:
                assert next(row for row in after[table] if row['id'] == old['id']) == old, table
        assert any(c['id'] == new_id for c in after['chemicals'])
        tile = page.locator('.molecule-tile').filter(has=page.get_by_text('Holton compound 17', exact=True))
        _diagram(tile.locator('img'), 'CCOC')
        tile.click()
        _diagram(page.locator('img.structure-diagram-large'), 'CCOC')
        _diagram(page.locator(f'.react-flow__node[data-id="chemical:{target_id}"] img'), 'CCOC')
        expect(page.get_by_role('button', name='Open reaction: Handoff fixture reaction', exact=True)).to_have_count(1)
        edge_ids = page.locator('.react-flow__edge').evaluate_all('(nodes)=>nodes.map(n=>n.getAttribute("data-id"))')
        projected_edges = [json.loads(value) for value in edge_ids]
        assert ['in', target_id, reaction_id] in projected_edges, projected_edges
        assert ['out', reaction_id, new_id] in projected_edges, projected_edges
        first_saved = stored()
        count = len(backups())
        upload(incoming)
        expect(page.locator('.web-notice')).to_contain_text('0 existing structures added')
        expect(review).to_have_count(0)
        assert stored() == first_saved and len(backups()) == count, 'Repeated handoff changed data or made another backup'
        page.reload(wait_until='load')
        assert stored() == first_saved

        # Equivalent SMILES representations are checked as actual graphs while
        # the user's local representation remains byte-for-byte untouched.
        equivalent = copy.deepcopy(after)
        next(c for c in equivalent['chemicals'] if c['id'] == target_id)['smiles'] = 'COCC'
        raw = load(equivalent)
        count = len(backups())
        upload(incoming)
        expect(page.locator('.web-notice')).to_contain_text('0 existing structures added')
        expect(review).to_have_count(0)
        assert stored() == raw and len(backups()) == count
        # A new qualified paper label uses the same explicit, backed-up review.
        more_labels = copy.deepcopy(incoming)
        new_label = 'Paper label product-17; DOI ' + incoming['papers'][0]['doi']
        next(c for c in more_labels['chemicals'] if c['id'] == target_id)['aliases'].append(new_label)
        upload(more_labels)
        expect(review.get_by_label('Paper labels to add')).to_contain_text(new_label)
        expect(apply).to_be_visible()
        assert stored() == raw
        apply.click()
        expect(review).to_have_count(0)
        equivalent_after = json.loads(stored())
        equivalent_row = next(c for c in equivalent_after['chemicals'] if c['id'] == target_id)
        assert equivalent_row['smiles'] == 'COCC'
        assert equivalent_row['aliases'] == target['aliases'] + [paper_label, new_label]
        assert equivalent_row['notes'] == target['notes']
        assert raw in backups() and len(backups()) == count + 1

        # Forged equal supplied keys/formulas never stand in for graph checks.
        forged_local = copy.deepcopy(equivalent)
        next(c for c in forged_local['chemicals'] if c['id'] == target_id)['smiles'] = 'CO'
        raw = load(forged_local)
        count = len(backups())
        upload(incoming)
        expect(page.get_by_role('alert')).to_contain_text('Stored molecule')
        expect(review).to_have_count(0)
        assert stored() == raw and len(backups()) == count

        # Conflicts reject the entire handoff, including its unrelated new rows.
        for change in [{'name': 'Different paper molecule'}, {'smiles': 'CO'}]:
            guarded = copy.deepcopy(baseline)
            if 'smiles' in change:
                next(c for c in guarded['chemicals'] if c['id'] == target_id)['smiles'] = change['smiles']
                package = incoming
            else:
                package = copy.deepcopy(incoming)
                next(c for c in package['chemicals'] if c['id'] == target_id).update(change)
            raw = load(guarded)
            count = len(backups())
            upload(package)
            expect(review).to_contain_text('conflicting IDs')
            expect(apply).to_have_count(0)
            assert stored() == raw and len(backups()) == count
            review.get_by_role('button', name='Cancel import', exact=True).click()

        # Actual graph validation precedes the preview and every persistence write.
        for field, value in [('smiles', 'C1('), ('formula', 'C9H9')]:
            raw = load(baseline)
            invalid = copy.deepcopy(incoming)
            next(c for c in invalid['chemicals'] if c['id'] == target_id)[field] = value
            count = len(backups())
            upload(invalid)
            expect(page.get_by_role('alert')).to_be_visible()
            expect(review).to_have_count(0)
            assert stored() == raw and len(backups()) == count

        for failure in ['backup', 'backup-readback', 'primary', 'concurrent']:
            raw = load(baseline)
            upload(incoming)
            expect(apply).to_be_visible()
            if failure == 'concurrent':
                raw += ' '
                page.evaluate('([key,raw])=>localStorage.setItem(key,raw)', [STORE, raw])
            else:
                page.evaluate('''([key,failure])=>{
                  const set=Storage.prototype.setItem,get=Storage.prototype.getItem;
                  Storage.prototype.setItem=function(k,v){
                    if((failure==='backup'&&k.includes('.import-backup.'))||(failure==='primary'&&k===key))throw new DOMException('Storage full','QuotaExceededError');
                    return set.call(this,k,v);
                  };
                  Storage.prototype.getItem=function(k){return failure==='backup-readback'&&k.includes('.import-backup.')?'incorrect backup':get.call(this,k)};
                }''', [STORE, failure])
            apply.click()
            expect(page.get_by_role('alert')).to_be_visible()
            assert stored() == raw, (failure, 'Import replaced the original primary bytes')
            expect(review).to_be_visible()
            page.reload(wait_until='load')
    finally:
        page.reload(wait_until='load')  # Restore any patched Storage methods.
        page.evaluate('''([key,raw,oldKeys])=>{
          for(const k of Object.keys(localStorage))if(!oldKeys.includes(k))localStorage.removeItem(k);
          if(raw===null)localStorage.removeItem(key);else localStorage.setItem(key,raw);
        }''', [STORE, original, original_keys])
        page.reload(wait_until='load')
        expect(page.get_by_role('heading', name='Select a molecule', exact=True)).to_be_visible()
        assert stored() == original
