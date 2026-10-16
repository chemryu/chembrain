"""Read-only checks against the existing original-PDF workspace on port 8000."""
import json
import os
import shutil
from pathlib import Path

from playwright.sync_api import expect, sync_playwright

ROOT = Path(__file__).resolve().parent.parent


def main():
    report = json.loads((ROOT / '.data/curations/uploaded-literature-report.json').read_text())
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(executable_path=os.environ.get('CHROMIUM_PATH') or shutil.which('chromium'), args=['--no-sandbox'])
        page = browser.new_page(viewport={'width':1440,'height':1000})
        errors = []
        page.on('pageerror', lambda error: errors.append(str(error)))
        page.goto('http://127.0.0.1:8000', wait_until='networkidle')
        expect(page.get_by_role('checkbox',name='Include demos')).not_to_be_checked()
        expect(page.locator('.molecule-node')).to_have_count(14)
        expect(page.locator('.reaction-node')).to_have_count(6)
        page.get_by_label('Paper filter',exact=True).select_option('10.1038/nature17431')
        expect(page.locator('.reaction-node')).to_have_count(2)
        page.locator('.reaction-node').filter(has_text='tert-butyl (6)').click()
        expect(page.locator('.inspector .conditions')).to_contain_text('MeCN 3 mL')
        expect(page.locator('.inspector .conditions')).to_contain_text('52%')
        evidence = page.locator('.evidence-card').filter(has_text='Compound 6')
        expect(evidence).to_have_attribute('href','https://doi.org/10.1038/nature17431')
        expect(evidence).to_contain_text('Original PDF page 45')
        expect(page.locator('blockquote, .source-text')).to_have_count(0)
        page.get_by_role('button',name='Paper library').click()
        expect(page.locator('.source-card')).to_have_count(6)
        page.locator('.source-card').filter(has_text='Horn 2016 · SI').get_by_role('button',name='Reference details').click()
        expect(page.get_by_role('link',name='Open DOI',exact=True)).to_have_attribute('href','https://doi.org/10.1038/nature17431')
        expect(page.locator('pre, iframe')).to_have_count(0)
        page.locator('.linked-sources button').filter(has_text='Horn 2016 · Main article').click()
        expect(page.get_by_role('heading',name='Horn 2016 · Main article',exact=True)).to_be_visible()
        page.get_by_role('button',name='Edit reference',exact=True).click()
        expect(page.locator('.source-metadata-form input[name="doi"]')).to_have_value('10.1038/nature17431')
        page.get_by_role('button',name='Close editor',exact=True).click()
        page.get_by_role('button',name='Find routes',exact=True).first.click()
        page.get_by_label('Target product',exact=True).select_option(report['molecule_ids']['nice-entry3'])
        page.locator('.route-search').get_by_role('button',name='Find routes',exact=True).click()
        expect(page.get_by_role('heading',name='No connected routes')).to_be_visible()
        page.get_by_role('checkbox',name='Include drafts',exact=True).check()
        page.locator('.route-search').get_by_role('button',name='Find routes',exact=True).click()
        expect(page.locator('.route-card')).to_have_count(1)
        expect(page.locator('.route-card')).to_contain_text('Contains drafts')
        assert not errors, errors
        browser.close()
        print(json.dumps({'status':'passed','checks':['existing PDF records preserved','English conditions','DOI evidence links','no full-text rendering','main/SI reference links','editable bibliography','conflicting drafts excluded by default','explicit draft route','no JS errors']}))


if __name__ == '__main__':
    main()
