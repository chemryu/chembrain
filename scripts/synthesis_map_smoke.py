"""Shared real-browser assertions for the hosted and offline synthesis map."""
import re
import json
from pathlib import Path
from playwright.sync_api import expect


def _check_post_drag_keyboard(page, graph, coupling, node, before_drag, original):
    """Exercise real keyboard input while D3's real post-drag click guard lives.

    Clock control makes this short interval deterministic; it neither replaces
    the D3 handler nor waits it away before the required keyboard assertions.
    The mouse is already down and the header has actually moved on entry.
    """
    page.clock.install(time=0)
    page.clock.pause_at(1000)
    page.evaluate('''()=>{
      window.__mapKeyboardClicks=0;
      window.__mapClickObserver=event=>{
        if(event.detail===0&&event.target.closest?.('.synthesis-node-button'))window.__mapKeyboardClicks++;
      };
      window.addEventListener('click',window.__mapClickObserver,true);
    }''')
    suppression="(window.__on||[]).some(handler=>handler.type==='click'&&handler.name==='drag')"
    try:
        page.mouse.up()
        expect(node).not_to_have_attribute('style', before_drag)
        dragged=node.get_attribute('style')
        assert page.evaluate(suppression), 'Post-drag regression did not retain the actual D3 click guard'
        coupling.focus()
        expect(coupling).to_be_focused()
        page.keyboard.press('Enter')
        inspector=page.get_by_role('region', name='Selected reaction details', exact=True)
        expect(inspector).to_be_visible()
        expect(inspector.locator('.step')).to_have_count(3)
        expect(inspector).to_contain_text('Ethanol')
        expect(inspector.locator('.paper-reference')).to_have_count(1)
        expect(inspector.locator('.paper-reference a')).to_have_attribute('href', 'https://doi.org/10.1021/ja00083a067')
        expect(coupling).to_have_attribute('aria-pressed', 'true')
        expect(node).to_have_attribute('style', dragged)
        # A held Space must activate on release, not on initial/repeat keydown.
        other=graph.get_by_role('button', name='Open reaction: Taxol coupling and hydrogenolysis sequence', exact=True)
        other.focus();expect(other).to_be_focused()
        page.keyboard.down('Space');page.keyboard.down('Space')
        expect(coupling).to_have_attribute('aria-pressed', 'true')
        expect(other).to_have_attribute('aria-pressed', 'false')
        page.keyboard.up('Space')
        expect(other).to_have_attribute('aria-pressed', 'true')
        expect(coupling).to_have_attribute('aria-pressed', 'false')
        expect(node).to_have_attribute('style', dragged)
        assert page.evaluate("localStorage.getItem('chembrain.normalized-library.v1')")==original
        # Both molecule keys must also work during that same D3 guard interval.
        chemical=graph.get_by_role('button', name='Open molecule: Holton compound 24b', exact=True)
        chemical.focus();expect(chemical).to_be_focused();page.keyboard.press('Enter')
        expect(page.locator('.selected-heading h2')).to_have_text('Holton compound 24b')
        expect(inspector).to_have_count(0)
        expect(page.get_by_role('tab', name='Map', exact=True)).to_have_attribute('aria-selected', 'true')
        next_chemical=graph.get_by_role('button', name='Open molecule: Holton compound 25', exact=True)
        next_chemical.focus();page.keyboard.down('Space')
        expect(page.locator('.selected-heading h2')).to_have_text('Holton compound 24b')
        # Blurring a held Space cancels it. A bare release on another button
        # must not activate a molecule that never received the matching press.
        chemical.focus();page.keyboard.up('Space')
        next_chemical.focus();page.keyboard.up('Space')
        expect(page.locator('.selected-heading h2')).to_have_text('Holton compound 24b')
        page.keyboard.down('Space');page.keyboard.down('Space')
        expect(page.locator('.selected-heading h2')).to_have_text('Holton compound 24b')
        page.keyboard.up('Space')
        expect(page.locator('.selected-heading h2')).to_have_text('Holton compound 25')
        expect(inspector).to_have_count(0)
        assert page.evaluate(suppression), 'Keyboard checks unexpectedly waited away D3 click suppression'
        assert page.evaluate("localStorage.getItem('chembrain.normalized-library.v1')")==original
        # Only after the boundary assertions release the timer. Normal Enter
        # still works, and prevented native clicks cannot duplicate activation.
        page.clock.run_for(1)
        assert not page.evaluate(suppression), 'D3 click guard did not clear with its timer'
        coupling.focus();expect(coupling).to_be_focused()
        page.keyboard.down('Enter');page.keyboard.down('Enter');page.keyboard.up('Enter')
        expect(inspector).to_be_visible()
        assert page.evaluate('window.__mapKeyboardClicks')==0, 'Map keys emitted duplicate native clicks'
        assert page.evaluate("localStorage.getItem('chembrain.normalized-library.v1')")==original
    except Exception as error:
        state=page.evaluate('''()=>({
          active:document.activeElement?.getAttribute('aria-label'),
          d3ClickGuard:(window.__on||[]).some(handler=>handler.type==='click'&&handler.name==='drag'),
          selected:document.querySelector('.selected-heading h2')?.textContent,
          inspectorCount:document.querySelectorAll('.map-reaction-inspector').length,
          nativeKeyboardClicks:window.__mapKeyboardClicks
        })''')
        raise AssertionError('Post-drag keyboard state: '+json.dumps(state)) from error
    finally:
        page.clock.run_for(1);page.clock.resume()
        page.evaluate('''()=>{
          window.removeEventListener('click',window.__mapClickObserver,true);
          delete window.__mapClickObserver;delete window.__mapKeyboardClicks;
        }''')


def check_synthesis_map(page):
    # Exploration must never write the only browser copy or change chemistry.
    original = page.evaluate("localStorage.getItem('chembrain.normalized-library.v1')")
    expect(page.locator('.synthesis-map')).to_have_count(0)
    page.locator('.molecule-tile').filter(has_text='Paclitaxel (Taxol)').click()
    expect(page.get_by_role('tab', name='Map', exact=True)).to_have_attribute('aria-selected', 'true')
    graph = page.locator('.synthesis-map')
    expect(graph).to_be_visible()
    expect(graph.locator('.synthesis-heading')).to_contain_text('8 recorded reactions')
    expect(graph.locator('.synthesis-fragment-note')).to_contain_text('unrecorded connecting steps')
    expect(graph.get_by_role('button', name=re.compile('^Open reaction: '))).to_have_count(8)
    expect(graph.locator('.react-flow__edge')).not_to_have_count(0)
    viewport = graph.locator('.react-flow__viewport')
    page.get_by_role('button', name='Focus selected molecule', exact=True).click()
    # Assert an actual zoom transformation, then exercise a background pan.
    page.wait_for_timeout(220)
    before = viewport.get_attribute('style')
    graph.get_by_role('button', name='Zoom in synthesis map', exact=True).click()
    expect(viewport).not_to_have_attribute('style', before)
    page.wait_for_timeout(180)
    before = viewport.get_attribute('style')
    pane = graph.locator('.react-flow__pane')
    pane.scroll_into_view_if_needed()
    box = pane.bounding_box()
    page.mouse.move(box['x'] + 12, box['y'] + 12)
    page.mouse.down()
    page.mouse.move(box['x'] + 82, box['y'] + 56, steps=8)
    page.mouse.up()
    expect(viewport).not_to_have_attribute('style', before)
    graph.get_by_role('button', name='Fit synthesis map', exact=True).click()
    page.wait_for_timeout(220)
    page.screenshot(path='/tmp/chembrain-synthesis-map-all.png', full_page=True)
    graph.get_by_role('button', name='Focus selected molecule', exact=True).click()
    page.wait_for_timeout(220)
    page.screenshot(path='/tmp/chembrain-synthesis-map.png', full_page=True)
    # Reaction activation must reuse the real editable conditions/DOI inspector.
    coupling = graph.get_by_role('button', name='Open reaction: Taxol side-chain coupling and deprotection sequence', exact=True)
    node = graph.locator('.react-flow__node').filter(has=page.get_by_role('button', name='Open reaction: Taxol side-chain coupling and deprotection sequence', exact=True))
    before_drag = node.get_attribute('style')
    handle = node.locator('.synthesis-drag')
    handle.scroll_into_view_if_needed()
    box = handle.bounding_box()
    page.mouse.move(box['x']+box['width']/2, box['y']+box['height']/2)
    page.mouse.down()
    page.mouse.move(box['x']+box['width']/2+35, box['y']+box['height']/2+28, steps=8)
    _check_post_drag_keyboard(page, graph, coupling, node, before_drag, original)
    page.locator('.molecule-tile').filter(has_text='Doxycycline').click()
    expect(page.locator('.synthesis-heading')).to_contain_text('4 recorded reactions')
    # Both true multi-step fragments must be present, without a guessed bridge.
    expect(page.get_by_role('button', name=re.compile('^Open reaction: '))).to_have_count(4)
    expect(page.locator('.synthesis-fragment-note')).to_be_visible()
    page.set_viewport_size({'width':390, 'height':844})
    expect(page.locator('.synthesis-map')).to_be_visible()
    assert page.evaluate('document.documentElement.scrollWidth <= innerWidth + 1'), 'Map mobile horizontal overflow'
    # QA-SYN-01: on a narrow canvas Focus must use the live dragged card,
    # including its measured dimensions, instead of the initial layout.
    graph=page.locator('.synthesis-map')
    graph.locator('.synthesis-canvas').scroll_into_view_if_needed()
    graph.get_by_role('button',name='Focus selected molecule',exact=True).click()
    page.wait_for_timeout(250)
    target=graph.locator('.react-flow__node[data-id="chemical:doxycycline"]')
    before=target.get_attribute('style')
    header=target.locator('.synthesis-drag').bounding_box()
    x=header['x']+header['width']/2;y=header['y']+header['height']/2
    page.mouse.move(x,y);page.mouse.down();page.mouse.move(x+200,y,steps=12);page.mouse.up()
    expect(target).not_to_have_attribute('style',before)
    graph.get_by_role('button',name='Focus selected molecule',exact=True).click()
    page.wait_for_function('''()=>{
      const node=document.querySelector('.react-flow__node[data-id="chemical:doxycycline"]')?.getBoundingClientRect();
      const canvas=document.querySelector('.synthesis-canvas')?.getBoundingClientRect();
      return node&&canvas&&node.x>=canvas.x&&node.right<=canvas.right&&node.y>=canvas.y&&node.bottom<=canvas.bottom;
    }''')
    assert page.evaluate("localStorage.getItem('chembrain.normalized-library.v1')") == original
    page.set_viewport_size({'width':1440, 'height':1000})
    assert page.evaluate("localStorage.getItem('chembrain.normalized-library.v1')") == original
    # Real edits refresh the graph and invalidate stale inspectors. The temporary
    # fixture data is confined to this disposable smoke-test browser context.
    page.locator('.molecule-tile').filter(has_text='Paclitaxel (Taxol)').click()
    coupling = page.get_by_role('button', name='Open reaction: Taxol side-chain coupling and deprotection sequence', exact=True)
    coupling.focus(); page.keyboard.press('Enter')
    page.get_by_role('button', name='Edit record', exact=True).click()
    page.get_by_label('Reaction name', exact=True).fill('Map-only revision fixture')
    page.get_by_role('button', name='Validate & save', exact=True).click()
    expect(page.get_by_role('region', name='Selected reaction details', exact=True)).to_have_count(0)
    page.get_by_role('button', name='Open reaction: Map-only revision fixture', exact=True).focus()
    page.keyboard.press('Enter')
    page.get_by_role('button', name='Edit record', exact=True).click()
    page.get_by_label('Reaction name', exact=True).fill('Taxol side-chain coupling and deprotection sequence')
    page.get_by_role('button', name='Validate & save', exact=True).click()
    incoming = json.loads((Path(__file__).resolve().parents[1]/'public/library.json').read_text())
    incoming['chemicals'].append({'id':'map-orphan-fixture','name':'Browser orphan fixture','kind':'compound','aliases':[],'smiles':None})
    extra = dict(incoming['reactions'][0],id='map-import-fixture',name='Browser graph import fixture',reactants=['holton-6'],products=['holton-17'])
    incoming['reactions'].append(extra)
    page.get_by_label('Import normalized library').set_input_files({'name':'map-fixture.json','mimeType':'application/json','buffer':json.dumps(incoming).encode()})
    expect(page.get_by_role('status')).to_contain_text('Import complete')
    expect(page.locator('.synthesis-heading')).to_contain_text('9 recorded reactions')
    expect(page.get_by_role('button',name='Open reaction: Browser graph import fixture',exact=True)).to_have_count(1)
    page.locator('.molecule-tile').filter(has_text='Browser orphan fixture').click()
    expect(page.locator('.synthesis-empty')).to_contain_text('No recorded reactions')
    expect(page.locator('.react-flow__node')).to_have_count(0)
    # An oversized whole reaction must be reported as omitted, never as absent.
    participants=[{'id':f'map-wide-{i}','name':f'Browser participant {i}','kind':'reagent','aliases':[],'smiles':None} for i in range(400)]
    incoming['chemicals'].extend(participants)
    incoming['reactions'].append(dict(incoming['reactions'][0],id='map-wide-fixture',name='Browser oversized reaction fixture',reactants=[c['id'] for c in participants],products=['map-orphan-fixture'],targets=['map-orphan-fixture']))
    page.get_by_label('Import normalized library').set_input_files({'name':'map-cap-fixture.json','mimeType':'application/json','buffer':json.dumps(incoming).encode()})
    expect(page.locator('.synthesis-truncation')).to_contain_text('display limit reached')
    expect(page.locator('.synthesis-empty')).to_contain_text('No complete reaction fits')
    expect(page.locator('.react-flow__node')).to_have_count(0)
    page.get_by_role('tab',name='List',exact=True).click()
    expect(page.locator('.reaction-summary')).to_have_count(1)
    expect(page.locator('.reaction-summary')).to_contain_text('Browser oversized reaction fixture')
    page.evaluate("(raw)=>{const key='chembrain.normalized-library.v1';if(raw===null)localStorage.removeItem(key);else localStorage.setItem(key,raw)}", original)
    # Return to the exact initial state; later legacy editor/import assertions
    # deliberately use the List alternative, preserving their complete coverage.
    page.reload(wait_until='load')
    expect(page.get_by_role('heading', name='Select a molecule', exact=True)).to_be_visible()
    expect(page.locator('.synthesis-map')).to_have_count(0)
