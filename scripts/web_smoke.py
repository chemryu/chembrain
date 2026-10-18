"""Real-browser checks for the standalone Pages app at a repository subpath."""
import json,os,shutil,subprocess,sys,tempfile,threading
from functools import partial
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
from playwright.sync_api import sync_playwright,expect
ROOT=Path(__file__).resolve().parents[1]
class Handler(SimpleHTTPRequestHandler):
 def do_GET(self):
  if not self.path.startswith('/chembrain/'):
   self.send_error(404);return
  self.path=self.path[len('/chembrain'):];super().do_GET()
 def log_message(self,*args):pass

def check_malformed_editor_drafts(page, errors):
 # Exercise the real React editor, not just a validator function. Each malformed
 # draft must remain visible and editable without changing browser persistence.
 store="localStorage.getItem('chembrain.normalized-library.v1')"
 for kind, button in [('chemical','Edit molecule'),('paper','Edit citation'),('reaction','Edit record'),('solution','Edit solution')]:
  page.get_by_role('button',name=button,exact=True).first.click()
  dialog=page.get_by_role('dialog',name='Edit normalized record')
  dialog.get_by_text('Advanced normalized JSON',exact=True).click()
  raw=dialog.get_by_label('Normalized record JSON')
  original=json.loads(raw.input_value())
  malformed=[None,[], 'draft', 7, False]
  key={'chemical':'aliases','paper':'authors','reaction':'steps','solution':'solutes'}[kind]
  malformed.extend([{**original,key:v} for v in [None,{},[None],[False]]])
  if kind in ('chemical','paper'):
   malformed.append({**original,key:['valid',{}]})
  elif kind=='reaction':
   malformed.extend([{**original,'reactants':None},{**original,'steps':[{**original['steps'][0],'temperature':{}}]}])
  else:
   malformed.extend([{**original,'solvents':{}},{**original,'solutes':[{**original['solutes'][0],'role':{}}]}])
  for i,bad in enumerate(malformed):
   before=page.evaluate(store)
   draft=json.dumps(bad,indent=1)
   raw.fill(draft)
   expect(dialog.get_by_role('alert').first).to_contain_text('Advanced JSON:')
   expect(raw).to_have_value(draft)
   dialog.get_by_role('button',name='Validate & save').click()
   expect(dialog).to_be_visible()
   assert page.evaluate(store)==before, (kind,i,'invalid save replaced browser data')
   assert not errors,errors
   # Both correction/save and cancel/reopen must recover from a bad draft.
   if i%2:
    dialog.get_by_role('button',name='Close editor').click()
    assert page.evaluate(store)==before, (kind,i,'cancel replaced browser data')
    page.get_by_role('button',name=button,exact=True).first.click()
    dialog.get_by_text('Advanced normalized JSON',exact=True).click()
   else:
    raw.fill(json.dumps(original))
    dialog.get_by_role('button',name='Validate & save').click()
    expect(dialog).to_have_count(0)
    assert page.evaluate(store)==before, (kind,i,'corrected unchanged draft replaced record')
    page.get_by_role('button',name=button,exact=True).first.click()
    dialog.get_by_text('Advanced normalized JSON',exact=True).click()
   raw=dialog.get_by_label('Normalized record JSON')
  # Invalid JSON syntax is also retained; changing it back restores the form.
  before=page.evaluate(store)
  raw.fill('{')
  expect(dialog.get_by_role('alert').first).to_contain_text('JSON syntax')
  raw.fill(json.dumps(original))
  if kind=='chemical':
   name=dialog.get_by_label('Molecule name',exact=True)
   name.fill('')
   expect(name).to_be_visible()  # no full semantic validation on every keystroke
   dialog.get_by_role('button',name='Validate & save').click()
   expect(dialog).to_be_visible()
   assert page.evaluate(store)==before
   name.fill(original['name'])
  dialog.get_by_role('button',name='Validate & save').click()
  expect(dialog).to_have_count(0)
  assert page.evaluate(store)==before

def check_processor_export_import(page):
 # Exercise the real independent processor CLI and browser importer together.
 # All temporary files live outside the app/dist; no PDF or review text is used.
 with tempfile.TemporaryDirectory(prefix='chembrain-portable-browser-') as folder:
  temporary=Path(folder)
  source=json.loads((ROOT/'examples/total-synthesis.json').read_text())
  paper={'id':'processor-export-smoke','doi':'10.5555/chembrain-export-smoke',
         'authors':['Browser contract fixture']}
  source['papers'].append(paper)
  curated=temporary/'curated.json';exported=temporary/'normalized.json'
  curated.write_text(json.dumps(source),encoding='utf-8')
  result=subprocess.run([sys.executable,'-m','paper_pipeline','export','--curated',str(curated),'--out',str(exported)],
                        cwd=ROOT,capture_output=True,text=True,timeout=60)
  assert result.returncode==0, result.stderr
  payload=exported.read_bytes()
  assert json.loads(payload)['schema_version']==1
  before=json.loads(page.evaluate("localStorage.getItem('chembrain.normalized-library.v1')"))
  assert not any(p['id']==paper['id'] for p in before['papers'])
  page.get_by_label('Import normalized library').set_input_files({'name':'processor-normalized.json','mimeType':'application/json','buffer':payload})
  expect(page.get_by_role('status')).to_contain_text('Import complete')
  after=json.loads(page.evaluate("localStorage.getItem('chembrain.normalized-library.v1')"))
  assert any(p==paper for p in after['papers'])
  for table in ('papers','chemicals','solutions','reactions'):
   for old in before[table]:
    assert next(row for row in after[table] if row['id']==old['id'])==old, (table,old['id'],'processor import overwrote existing edit')
  expect(page.locator('.reaction-summary').filter(has_text='User curated coupling')).to_have_count(1)

def check_metadata_boundary(browser,url):
 compact=json.loads((ROOT/'public/library.json').read_text())
 assert all(set(row)=={'id','doi','authors'} for row in compact['papers'])
 for name in ['paclitaxel.png','doxycycline.png']:
  assert not (ROOT/'dist/structures'/name).exists(), 'Copied paper image in deployment'
 assert not list((ROOT/'dist').rglob('*.pdf'))
 legacy=json.loads(json.dumps(compact))
 legacy['papers'][0].update(title='Private legacy citation',journal='Private journal',year=1994,notes='Private old paper metadata')
 legacy['reactions'][0]['name']='Private chemistry edit retained'
 legacy['chemicals'][0]['notes']='Private chemistry annotation retained'
 legacy['solutions'][0]['concentration']=0.125
 raw=json.dumps(legacy,indent=3,ensure_ascii=False)+'\n'  # byte-exact backup, not reserialization
 key='chembrain.normalized-library.v1'
 for failure in [None,'backup','primary','unknown']:
  context=browser.new_context()
  page=context.new_page();errors=[]
  page.on('pageerror',lambda error:errors.append(str(error)))
  initial=raw
  if failure=='unknown':
   unknown=json.loads(raw);unknown['papers'][0]['abstract']='Unexpected legacy document field'
   initial=json.dumps(unknown)
  page.add_init_script('''(()=>{
   const key='chembrain.normalized-library.v1';
   const write=Storage.prototype.setItem;
   if(localStorage.getItem(key)===null)write.call(localStorage,key,INITIAL);
   const failure=FAILURE;
   Storage.prototype.setItem=function(k,v){
    if((failure==='backup'&&k.includes('.legacy-backup.'))||(failure==='primary'&&k===key))throw new DOMException('Test storage full','QuotaExceededError');
    return write.call(this,k,v);
   };
  })();'''.replace('INITIAL',json.dumps(initial)).replace('FAILURE',json.dumps(failure)))
  page.goto(url,wait_until='networkidle')
  actual=page.evaluate('(k)=>localStorage.getItem(k)',key)
  backups=page.evaluate("Object.keys(localStorage).filter(k=>k.includes('.legacy-backup.')).map(k=>localStorage.getItem(k))")
  if failure in ['backup','unknown']:
   expect(page.get_by_role('alert')).to_be_visible()
   assert actual==initial and backups==[],failure
   expect(page.get_by_role('button',name='Import package',exact=True)).to_be_disabled()
   expect(page.get_by_role('button',name='Backup JSON',exact=True)).to_be_disabled()
  else:
   assert backups==[raw],failure
   if failure=='primary':
    expect(page.get_by_role('alert')).to_be_visible();assert actual==raw
   else:
    expect(page.get_by_role('status')).to_contain_text('backed up privately')
    projected=json.loads(actual)
    assert all(set(row)=={'id','doi','authors'} for row in projected['papers'])
    for table in ['chemicals','reactions','solutions']:assert projected[table]==legacy[table],table
    page.reload(wait_until='networkidle')
    assert page.evaluate('(k)=>localStorage.getItem(k)',key)==actual
    with page.expect_download() as download:page.get_by_role('button',name='Backup JSON',exact=True).click()
    exported=json.loads(Path(download.value.path()).read_text())
    assert exported==projected
    assert 'Private legacy citation' not in json.dumps(exported)
    # Unsupported imports fail closed; only the explicit startup migration accepts known legacy keys.
    for bad in [legacy,{**compact,'abstract':'Unknown document container'},
                {**compact,'reactions':[{**compact['reactions'][0],'steps':[{**compact['reactions'][0]['steps'][0],'body':'Unknown document field'}]}]}]:
     page.get_by_label('Import normalized library').set_input_files({'name':'unsupported.json','mimeType':'application/json','buffer':json.dumps(bad).encode()})
     expect(page.get_by_role('alert')).to_be_visible()
     assert page.evaluate('(k)=>localStorage.getItem(k)',key)==actual
  assert not errors,errors
  context.close()

def main():
 server=ThreadingHTTPServer(('127.0.0.1',0),partial(Handler,directory=str(ROOT/'dist')))
 threading.Thread(target=server.serve_forever,daemon=True).start()
 try:
  with sync_playwright() as p:
   browser=p.chromium.launch(executable_path=os.environ.get('CHROMIUM_PATH') or shutil.which('chromium'),args=['--no-sandbox'])
   page=browser.new_page(viewport={'width':1440,'height':1000});errors=[];requests=[]
   page.on('pageerror',lambda e:errors.append(str(e)));page.on('request',lambda r:requests.append(r.url))
   url=f'http://127.0.0.1:{server.server_port}/chembrain/'
   check_metadata_boundary(browser,url)
   page.goto(url,wait_until='networkidle');expect(page.get_by_role('heading',name='Select a molecule',exact=True)).to_be_visible()
   expect(page.locator('.web-reaction')).to_have_count(0);expect(page.get_by_text('All reactions',exact=True)).to_have_count(0);expect(page.get_by_text('Organic synthesis',exact=True)).to_have_count(0)
   page.screenshot(path='/tmp/chembrain-web-library.png',full_page=True)
   assert page.locator('.molecule-tile img').evaluate_all('(xs)=>xs.every(x=>x.complete&&x.naturalWidth>0)')
   page.locator('.molecule-tile').filter(has_text='Paclitaxel (Taxol)').click();expect(page.locator('.web-reaction')).to_have_count(2)
   page.locator('.reaction-summary').filter(has_text='Taxol side-chain coupling').click();expect(page.locator('.paper-reference')).to_have_count(1)
   expect(page.locator('.paper-reference a')).to_have_attribute('href','https://doi.org/10.1021/ja00083a067')
   expect(page.locator('.paper-reference a')).to_have_text('10.1021/ja00083a067 ↗')
   expect(page.locator('.molecule-tile').filter(has_text='Paclitaxel (Taxol)').locator('img')).to_have_count(0)
   expect(page.locator('.step')).to_have_count(3);expect(page.locator('.step').nth(2)).to_contain_text('Ethanol')
   page.get_by_role('button',name='Edit record',exact=True).click();page.get_by_label('Reaction name',exact=True).fill('User curated coupling');page.get_by_role('button',name='Validate & save').click()
   saved=page.evaluate("localStorage.getItem('chembrain.normalized-library.v1')")
   assert 'User curated coupling' in saved
   page.reload(wait_until='networkidle');expect(page.get_by_role('heading',name='Select a molecule',exact=True)).to_be_visible();expect(page.locator('.web-reaction')).to_have_count(0)
   page.locator('.molecule-tile').filter(has_text='Paclitaxel (Taxol)').click();expect(page.locator('.reaction-summary').filter(has_text='User curated coupling')).to_have_count(1)
   before=page.evaluate("localStorage.getItem('chembrain.normalized-library.v1')")
   page.get_by_label('Import normalized library').set_input_files({'name':'bad.json','mimeType':'application/json','buffer':b'{"schema_version":1,"papers":[]}'})
   expect(page.get_by_role('alert')).to_contain_text('Missing');assert page.evaluate("localStorage.getItem('chembrain.normalized-library.v1')")==before
   page.get_by_label('Import normalized library').set_input_files(str(ROOT/'public/library.json'))
   expect(page.get_by_role('status')).to_contain_text('Import complete');expect(page.locator('.reaction-summary').filter(has_text='User curated coupling')).to_have_count(1)
   check_processor_export_import(page)
   page.get_by_role('checkbox',name='Include synthesis-route steps').check();expect(page.locator('.web-reaction')).to_have_count(8)
   page.locator('.molecule-tile').filter(has_text='Doxycycline').click();expect(page.locator('.web-reaction')).to_have_count(1)
   page.locator('.reaction-summary').click();expect(page.locator('.paper-reference a')).to_have_attribute('href','https://doi.org/10.1126/science.1109755')
   page.get_by_role('button',name='Edit citation',exact=True).click();expect(page.get_by_label('Title',exact=True)).to_have_count(0);expect(page.get_by_label('Journal',exact=True)).to_have_count(0);expect(page.get_by_label('Notes',exact=True)).to_have_count(0);page.get_by_label('Authors (separate with semicolons)').fill('Author correction; Andrew G. Myers');page.get_by_role('button',name='Validate & save').click();expect(page.locator('.paper-reference')).to_contain_text('Author correction')
   check_malformed_editor_drafts(page,errors)
   with page.expect_download() as downloaded:page.get_by_role('button',name='Backup JSON',exact=True).click()
   assert downloaded.value.suggested_filename=='chembrain-library.json'
   page.set_viewport_size({'width':390,'height':844});page.screenshot(path='/tmp/chembrain-web-mobile.png',full_page=True)
   assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1'),'Mobile horizontal overflow'
   assert not errors,errors
   assert not any('/api/' in r or not r.startswith(url.split('/chembrain')[0]) for r in requests),requests
   browser.close()
   print('WEB_LIBRARY_BROWSER_PASS: empty initial panel, molecule-related records, stage solutions, one DOI reference, edit/reload/import preservation, malformed-editor correction/cancel/storage, Python-export browser import, metadata-only DOI/authors display/export, byte-exact legacy backup and storage-failure recovery, unknown-field rejection, no copied paper assets, backup, subpath assets and mobile; no backend API.')
 finally:server.shutdown();server.server_close()
if __name__=='__main__':main()
