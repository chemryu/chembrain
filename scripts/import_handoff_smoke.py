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
        check_fact_handoff(page)
    finally:
        page.reload(wait_until='load')  # Restore any patched Storage methods.
        page.evaluate('''([key,raw,oldKeys])=>{
          for(const k of Object.keys(localStorage))if(!oldKeys.includes(k))localStorage.removeItem(k);
          if(raw===null)localStorage.removeItem(key);else localStorage.setItem(key,raw);
        }''', [STORE, original, original_keys])
        page.reload(wait_until='load')
        expect(page.get_by_role('heading', name='Select a molecule', exact=True)).to_be_visible()
        assert stored() == original


def check_fact_handoff(page):
    """Exercise existing reaction/solution-only updates through the real main UI.

    This is complementary to the mandatory actual Workbench UI-export transfer.
    All experimental values here are private synthetic test values.
    """
    source = json.loads((ROOT / 'public/library.json').read_text())
    reaction_id = 'h-methyl'
    reaction = next(row for row in source['reactions'] if row['id'] == reaction_id)
    first_id = reaction['steps'][0]['solution_id']
    first = next(row for row in source['solutions'] if row['id'] == first_id)
    first.update(concentration=0.1, concentration_unit='M')
    for item in first['solutes']:
        item.update(amount=1, unit='mmol')
    second = copy.deepcopy(first)
    second.update(id='handoff-facts-second', concentration=0.25)
    for item in second['solutes']:
        item['amount'] = 0.5
    source['solutions'].append(second)
    reaction.update(steps=[{'solution_id': first_id, 'temperature': '20 °C', 'time': '1 h'},
                            {'solution_id': second['id'], 'temperature': '40 °C', 'time': '2 h'}],
                    yield_percent=88, yield_basis='Synthetic receiving fixture, both stages', status='reviewed')
    reaction['evidence'].append({**reaction['evidence'][0], 'locator': 'SI, synthetic receiving fixture'})
    baseline = copy.deepcopy(source)
    old_reaction = next(row for row in baseline['reactions'] if row['id'] == reaction_id)
    old_reaction.update(steps=[], yield_percent=None, notes='Private fact-only reaction note', status='draft')
    old_reaction.pop('yield_basis', None)
    old_reaction['evidence'] = old_reaction['evidence'][:1]
    for solution in baseline['solutions']:
        if solution['id'] in [first_id, second['id']]:
            solution.update(concentration=None, concentration_unit=None)
            for item in solution['solutes']:
                item.update(amount=None, unit=None)

    def stored():
        return page.evaluate('(key)=>localStorage.getItem(key)', STORE)

    def load(data=baseline):
        raw = json.dumps(data, indent=3, ensure_ascii=False) + '\n'
        page.evaluate('([key,raw])=>localStorage.setItem(key,raw)', [STORE, raw])
        page.reload(wait_until='load')
        expect(page.locator('.molecule-tile').first).to_be_visible()
        assert stored() == raw
        return raw

    def upload(data=source, name='facts-only.json'):
        page.get_by_label('Import normalized library').set_input_files({
            'name': name, 'mimeType': 'application/json', 'buffer': json.dumps(data).encode()})

    def backup_values():
        return page.evaluate('Object.keys(localStorage).filter(k=>k.includes(".import-backup.")).map(k=>localStorage.getItem(k))')

    review = page.get_by_role('region', name='Review paper import', exact=True)
    apply = review.get_by_role('button', name='Apply import', exact=True)
    raw = load()
    old_backups = backup_values()
    upload()
    changes = review.get_by_label('Existing chemistry changes', exact=True)
    expect(changes).to_contain_text('steps')
    expect(changes).to_contain_text('concentration')
    expect(changes).to_contain_text('Previous')
    expect(changes).to_contain_text('Incoming')
    expect(review).to_contain_text('0 existing molecules · 2 existing solutions · 1 existing reactions')
    assert stored() == raw and backup_values() == old_backups
    apply.click()
    expect(page.locator('.web-notice')).to_contain_text('0 existing structures added')
    expect(page.locator('.web-notice')).to_contain_text('2 existing solutions and 1 existing reactions updated')
    after = json.loads(stored())
    actual = next(row for row in after['reactions'] if row['id'] == reaction_id)
    for field in ['steps', 'yield_percent', 'yield_basis', 'evidence']:
        assert actual[field] == reaction[field], ('Missing imported reaction fact', field)
    assert actual['notes'] == old_reaction['notes'] and actual['status'] == 'draft'
    for expected in [first, second]:
        assert next(row for row in after['solutions'] if row['id'] == expected['id']) == expected
    assert raw in backup_values() and len(backup_values()) == len(old_backups) + 1
    saved = stored()
    page.reload(wait_until='load')
    assert stored() == saved
    tile = page.locator('.molecule-tile').filter(has=page.get_by_text('Holton compound 17', exact=True))
    tile.click()
    page.get_by_role('tab', name='List', exact=True).click()
    page.locator(f'.web-reaction[data-reaction-id="{reaction_id}"] .reaction-summary').click()
    expect(page.locator('.step')).to_have_count(2)
    expect(page.locator('.step').nth(0)).to_contain_text('20 °C · 1 h')
    expect(page.locator('.step').nth(1)).to_contain_text('40 °C · 2 h')
    expect(page.locator('.paper-reference')).to_have_count(1)
    expect(page.locator('.paper-reference')).to_contain_text('SI, synthetic receiving fixture')
    count = len(backup_values())
    page.evaluate('''()=>{window.__factWrites=[];const set=Storage.prototype.setItem;
      Storage.prototype.setItem=function(k,v){window.__factWrites.push(k);return set.call(this,k,v);};}''')
    upload()
    expect(page.locator('.web-notice')).to_contain_text('no changes')
    expect(review).to_have_count(0)
    assert stored() == saved and len(backup_values()) == count
    assert page.evaluate('window.__factWrites') == [], 'No-op rewrote private storage'
    page.reload(wait_until='load')

    for failure in ['backup', 'concurrent']:
        raw = load()
        upload()
        expect(apply).to_be_visible()
        if failure == 'backup':
            page.evaluate('''()=>{const set=Storage.prototype.setItem;Storage.prototype.setItem=function(k,v){
              if(k.includes('.import-backup.'))throw new DOMException('Quota','QuotaExceededError');return set.call(this,k,v);};}''')
        else:
            raw += ' '
            page.evaluate('([key,raw])=>localStorage.setItem(key,raw)', [STORE, raw])
        apply.click()
        expect(page.get_by_role('alert')).to_be_visible()
        assert stored() == raw
        tile.click()
        page.get_by_role('tab', name='List', exact=True).click()
        page.locator(f'.web-reaction[data-reaction-id="{reaction_id}"] .reaction-summary').click()
        expect(page.locator('.step')).to_have_count(0)
        expect(page.locator('.reaction-expanded')).to_contain_text('Private fact-only reaction note')
        page.reload(wait_until='load')

    # An older delayed File.text() result must not replace a newer import plan.
    raw = load()
    first_source = copy.deepcopy(source)
    next(row for row in first_source['reactions'] if row['id'] == reaction_id)['steps'][0]['temperature'] = 'STALE first temperature'
    latest_source = copy.deepcopy(source)
    next(row for row in latest_source['reactions'] if row['id'] == reaction_id)['steps'][0]['temperature'] = 'LATEST temperature'
    page.evaluate('''()=>{const text=File.prototype.text;File.prototype.text=function(){
      if(this.name!=='slow-first-facts.json')return text.call(this);
      const file=this;return new Promise(resolve=>{window.__releaseSlowFacts=()=>{
        window.__slowFactsDone=text.call(file).then(resolve);};});};}''')
    upload(first_source, 'slow-first-facts.json')
    page.wait_for_function('typeof window.__releaseSlowFacts === "function"')
    upload(latest_source, 'latest-facts.json')
    expect(changes).to_contain_text('LATEST temperature')
    page.evaluate('''async()=>{window.__releaseSlowFacts();await window.__slowFactsDone;
      await new Promise(requestAnimationFrame);await new Promise(requestAnimationFrame);}''')
    expect(changes).to_contain_text('LATEST temperature')
    expect(changes).not_to_contain_text('STALE first temperature')
    assert stored() == raw
    apply.click()
    expect(review).to_have_count(0)
    assert next(row for row in json.loads(stored())['reactions'] if row['id'] == reaction_id)['steps'][0]['temperature'] == 'LATEST temperature'
    page.reload(wait_until='load')
