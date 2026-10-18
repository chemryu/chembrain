import copy,json
from pathlib import Path
import pymupdf
import pytest
from paper_pipeline.schema import normalize,validate
from paper_pipeline.__main__ import ingest,weekly,prepare_anchors
ROOT=Path(__file__).resolve().parents[1]
@pytest.fixture(autouse=True)
def local_processor_environment(monkeypatch):
 monkeypatch.delenv('GITHUB_ACTIONS',raising=False)

def sample():return json.loads((ROOT/'examples/total-synthesis.json').read_text())
def test_starter_has_no_paper_body_and_has_page_evidence():
 d=validate(sample());assert len(d['papers'])==3 and len(d['reactions'])==12
 assert all(r['status']=='draft' for r in d['reactions'])
 assert len(json.dumps(d))<35000
 assert next(p for p in d['papers'] if p['id']=='charest')['doi']=='10.1126/science.1109755'
 assert next(r for r in d['reactions'] if r['id']=='h-oxetane')['yield_percent'] is None
 assert next(r for r in d['reactions'] if r['id']=='b-dmdo')['steps'][0]['solution_id']
def test_normalization_relinks_duplicate_papers_and_known_structures():
 d=sample();p=copy.deepcopy(d['papers'][0]);p.update(id='duplicate',doi='https://doi.org/'+p['doi'].upper());d['papers'].append(p)
 c=copy.deepcopy(next(c for c in d['chemicals'] if c['id']=='ethanol'));c.update(id='duplicate-ethanol',smiles='OCC');d['chemicals'].append(c)
 d['solutions'][0]['solvents'].append(c['id']);d['reactions'][0]['evidence'].append({'paper_id':p['id'],'page':1,'locator':'second locator'})
 n=normalize(d);assert len(n['papers'])==3;assert len(n['chemicals'])==len(d['chemicals'])-1
 assert n['solutions'][0]['solvents'][-1]=='ethanol';assert n['reactions'][0]['evidence'][-1]['paper_id']=='holton'
@pytest.mark.parametrize('field',['full_text','pdf','candidate_text','svg'])
def test_library_rejects_document_payload(field):
 d=sample();d['papers'][0][field]='private body'
 with pytest.raises(ValueError):validate(d)
def test_multi_doi_pdf_requires_identity_review_and_archive_cannot_be_public(tmp_path):
 path=tmp_path/'mixed.pdf'
 with pymupdf.open() as doc:
  doc.new_page().insert_text((30,30),'10.1126/science.1107996 10.1126/science.1109755')
  doc.save(path)
 result=ingest(path,tmp_path/'review');assert result['doi'] is None;assert len(result['doi_candidates'])==2
 with pytest.raises(ValueError):ingest(path,ROOT/'public')
def test_weekly_provider_failure_preserves_curated_data_and_checkpoint(tmp_path,monkeypatch):
 from server.jacs_collection import CrossrefClient
 def fail(*a,**k):raise RuntimeError('private query details')
 monkeypatch.setattr(CrossrefClient,'_get',fail)
 out=tmp_path/'library.json';work=tmp_path/'archive'
 prepared=prepare_anchors(ROOT/'paper_pipeline/journals.json',work,out)
 anchor=json.loads((work/'jacs/state.json').read_text())
 assert prepared=={'journals':['jacs']} and set(anchor)=={'resume'}
 assert anchor['resume']['cursor']=='*' and anchor['resume']['processed']==0
 report=weekly(ROOT/'paper_pipeline/journals.json',work,out,ROOT/'examples/total-synthesis.json')
 assert report['failures'];assert 'private query' not in json.dumps(report)
 assert len(validate(json.loads(out.read_text()))['reactions'])==12
 # An unavailable provider may retain only the original, nonadvancing anchor;
 # retry must not silently move the initial window to a later date.
 assert json.loads((work/'jacs/state.json').read_text())==anchor
def test_weekly_verified_oa_goes_only_to_private_archive(tmp_path,monkeypatch):
 from server.jacs_collection import CrossrefClient
 item={'DOI':'10.1021/jacs.fixture','type':'journal-article','ISSN':['0002-7863'],'title':['Fixture'], 'author':[{'given':'Ada','family':'Chemist'}], 'license':[{'URL':'https://creativecommons.org/licenses/by/4.0/','content-version':'vor','start':{'date-time':'2020-01-01T00:00:00Z'}}], 'link':[{'URL':'https://pubs.acs.org/doi/pdf/10.1021/jacs.fixture','content-type':'application/pdf','content-version':'vor'}]}
 monkeypatch.setattr(CrossrefClient,'_get',lambda *a,**k:json.dumps({'message':{'items':[item],'total-results':1}}).encode())
 with pymupdf.open() as doc:doc.new_page();pdf=doc.tobytes()
 monkeypatch.setattr(CrossrefClient,'pdf',lambda *a:pdf)
 out=tmp_path/'library.json';report=weekly(ROOT/'paper_pipeline/journals.json',tmp_path/'archive',out,ROOT/'examples/total-synthesis.json')
 assert not report['failures'];assert report['journals'][0]['pdfs_saved']==1
 assert list((tmp_path/'archive').rglob('*.pdf'));assert 'jacs_pdfs' not in out.read_text();assert next(p for p in json.loads(out.read_text())['papers'] if p['doi']==item['DOI'])=={'id':__import__('paper_pipeline.schema',fromlist=['key']).key('paper',item['DOI']),'doi':item['DOI'],'authors':['Ada Chemist']}
 repeat=weekly(ROOT/'paper_pipeline/journals.json',tmp_path/'archive',out,ROOT/'examples/total-synthesis.json');assert repeat['journals'][0]['pdfs_saved']==0

# Controlled public-gateway fixtures only: no ACS/Crossref requests are made.
def queue_fixture(tmp_path,monkeypatch,count=11):
 import urllib.parse
 from datetime import datetime,timezone
 import paper_pipeline.__main__ as pipeline
 import server.jacs_collection as collector
 clock={'now':datetime(2026,10,17,tzinfo=timezone.utc)}
 class FrozenDate(datetime):
  @classmethod
  def now(cls,tz=None):return clock['now']
 monkeypatch.setattr(pipeline,'datetime',FrozenDate)
 monkeypatch.setattr(collector,'_utc',lambda:clock['now'])
 def article(index):
  identifier=f'10.1021/jacs.queue{index}'
  return {'DOI':identifier,'type':'journal-article','ISSN':['0002-7863'],'title':[f'Queue {index}'],'published':{'date-parts':[[2026,10,4]]},'license':[{'URL':'https://creativecommons.org/licenses/by/4.0/','content-version':'vor','start':{'date-time':'2020-01-01T00:00:00Z'}}],'link':[{'URL':'https://pubs.acs.org/doi/pdf/'+identifier,'content-type':'application/pdf','content-version':'vor'}]}
 items=[article(i) for i in range(count)];current={i['DOI']:copy.deepcopy(i) for i in items}
 calls={'downloads':[],'refreshes':[],'windows':[],'fail_pdfs':set(),'fail_refresh':set()}
 def get(self,url,*args,**kwargs):
  if '/journals/' in url:
   query=urllib.parse.parse_qs(urllib.parse.urlsplit(url).query)
   start=query['filter'][0].split('from-pub-date:')[1].split(',')[0]
   calls['windows'].append(start)
   selected=items if start<='2026-10-04' else []
   return json.dumps({'message':{'items':selected,'total-results':len(selected)}}).encode()
  identifier=urllib.parse.unquote(url.split('/works/',1)[1]);calls['refreshes'].append(identifier)
  if identifier in calls['fail_refresh']:raise RuntimeError('secret provider failure')
  return json.dumps({'message':current[identifier]}).encode()
 def pdf(self,candidate):
  calls['downloads'].append(candidate)
  if candidate.doi in calls['fail_pdfs']:raise RuntimeError('secret PDF failure')
  with pymupdf.open() as doc:
   doc.new_page().insert_text((30,30),candidate.doi);return doc.tobytes()
 monkeypatch.setattr(collector.CrossrefClient,'_get',get);monkeypatch.setattr(collector.CrossrefClient,'pdf',pdf)
 out=tmp_path/'library.json';work=tmp_path/'archive'
 def run():return pipeline.weekly(ROOT/'paper_pipeline/journals.json',work,out,ROOT/'examples/total-synthesis.json')
 def pending():return json.loads((work/'jacs/pending.json').read_text())['items']
 return clock,items,current,calls,run,pending,work,out


def leave_metadata_overlap(clock,run,monkeypatch):
 from datetime import datetime,timezone
 import paper_pipeline.__main__ as pipeline
 # A fixed checkpoint-derived fourteen-day lookback intentionally rediscovers
 # October 4 on the next pass. Advance metadata once with downloads deferred,
 # then exercise pending work after that article truly leaves the next window.
 clock['now']=datetime(2026,10,24,tzinfo=timezone.utc)
 with monkeypatch.context() as context:
  context.setattr(pipeline,'PDF_WORK_LIMIT',0)
  metadata=run();assert not metadata['failures']
  assert metadata['journals'][0]['pdf_work_attempted']==0
 clock['now']=datetime(2026,10,31,tzinfo=timezone.utc)


def test_weekly_pending_eleventh_pdf_survives_metadata_overlap_and_is_idempotent(tmp_path,monkeypatch):
 from datetime import datetime,timezone
 clock,items,current,calls,run,pending,work,out=queue_fixture(tmp_path,monkeypatch)
 first=run();j=first['journals'][0]
 assert not first['failures'] and j['metadata_complete'] and j['complete']
 assert j['pdfs_saved']==j['pdf_work_attempted']==10 and j['pending']==j['deferred']==1
 assert not j['downloads_complete'] and len(pending())==1
 deferred=items[-1]['DOI'];source=pending()[deferred]['source']
 assert source['DOI']==deferred and source['license']==current[deferred]['license'] and source['link']==current[deferred]['link']
 assert json.loads((work/'jacs/state.json').read_text())['last_success'].startswith('2026-10-17')
 leave_metadata_overlap(clock,run,monkeypatch)
 second=run();j=second['journals'][0]
 assert calls['windows'][-1]=='2026-10-10' and j['bibliographic_items']==0
 assert not second['failures'] and j['pdfs_saved']==j['pdf_work_attempted']==1 and j['downloads_complete'] and not pending()
 assert calls['refreshes']==[deferred] and len(calls['downloads'])==11
 assert len(list(work.rglob('*.pdf')))==len(list(work.rglob('*.review.json')))==11
 again=run();assert not again['failures'] and again['journals'][0]['pdf_work_attempted']==0
 assert len(calls['downloads'])==11 and len(list(work.rglob('*.review.json')))==11
 assert 'pending.json' not in out.read_text() and 'license' not in out.read_text()


def test_weekly_failed_attempts_are_bounded_and_retried_with_fresh_identity(tmp_path,monkeypatch):
 from datetime import datetime,timezone
 clock,items,current,calls,run,pending,work,out=queue_fixture(tmp_path,monkeypatch)
 calls['fail_pdfs']={item['DOI'] for item in items}
 first=run();j=first['journals'][0]
 assert j['pdf_work_attempted']==10 and j['pdfs_saved']==0 and j['pending']==11 and j['deferred']==1
 assert len(calls['downloads'])==10 and first['failures'] and 'secret' not in json.dumps(first)
 # Metadata completion/checkpoint is distinct from the durable failed downloads.
 assert j['metadata_complete'] and not j['downloads_complete']
 assert len(pending())==11
 leave_metadata_overlap(clock,run,monkeypatch);calls['fail_pdfs'].clear()
 second=run();assert second['journals'][0]['pdfs_saved']==10 and len(pending())==1
 assert len(calls['refreshes'])==10
 third=run();assert third['journals'][0]['pdfs_saved']==1 and not pending()
 assert len(calls['downloads'])==21


@pytest.mark.parametrize('changed',['revoked','expired','wrong-doi','provider-failure'])
def test_weekly_pending_revalidates_current_license_and_doi_before_download(tmp_path,monkeypatch,changed):
 from datetime import datetime,timezone
 clock,items,current,calls,run,pending,work,out=queue_fixture(tmp_path,monkeypatch)
 run();identifier=items[-1]['DOI'];leave_metadata_overlap(clock,run,monkeypatch)
 if changed=='revoked':current[identifier]['license']=[]
 elif changed=='expired':current[identifier]['license'][0]['end']={'date-time':'2026-10-20T00:00:00Z'}
 elif changed=='wrong-doi':current[identifier]['DOI']='10.1021/jacs.other'
 else:calls['fail_refresh'].add(identifier)
 before=len(calls['downloads']);report=run()
 assert len(calls['downloads'])==before and identifier in pending()
 assert report['journals'][0]['pdf_work_attempted']==1 and not report['journals'][0]['downloads_complete']
 assert report['failures'] and 'secret' not in json.dumps(report)
 if changed in ('revoked','expired'):
  assert report['journals'][0]['oa_unverified']==1 and pending()[identifier]['status']=='oa_unverified'
 # Later fresh eligibility can recover the same durable identity; no stale URL
 # or expired license from the original queue is used to authorize the retry.
 current[identifier]=copy.deepcopy(items[-1]);current[identifier]['license'][0]['URL']='https://creativecommons.org/licenses/by-sa/4.0/'
 calls['fail_refresh'].clear();retry=run()
 assert not retry['failures'] and not pending() and calls['downloads'][-1].license_url.endswith('/by-sa/4.0/')


def test_weekly_saved_pdf_with_failed_review_is_reprocessed_without_redownload(tmp_path,monkeypatch):
 from datetime import datetime,timezone
 import paper_pipeline.__main__ as pipeline
 clock,items,current,calls,run,pending,work,out=queue_fixture(tmp_path,monkeypatch,count=1)
 real_ingest=pipeline.ingest
 def fail(*args,**kwargs):raise RuntimeError('private processing error')
 monkeypatch.setattr(pipeline,'ingest',fail)
 first=run();j=first['journals'][0]
 assert j['pdfs_saved']==1 and j['reviews_created']==0 and j['pending']==1 and first['failures']
 assert len(list(work.rglob('*.pdf')))==1
 monkeypatch.setattr(pipeline,'ingest',real_ingest)
 # Retry local processing after the article has left the metadata overlap. Its
 # current license may be absent: processing the archived file makes no fetch.
 leave_metadata_overlap(clock,run,monkeypatch)
 current[items[0]['DOI']]['license']=[]
 second=run();j=second['journals'][0]
 assert not second['failures'] and j['pdfs_saved']==0 and j['pdfs_reused']==1 and j['reviews_created']==1
 assert len(calls['downloads'])==1 and not calls['refreshes'] and not pending()
 assert j['bibliographic_items']==0 and len(list(work.rglob('*.review.json')))==1


def test_weekly_queue_bound_keeps_metadata_page_retryable(tmp_path,monkeypatch):
 import paper_pipeline.__main__ as pipeline
 clock,items,current,calls,run,pending,work,out=queue_fixture(tmp_path,monkeypatch,count=2)
 monkeypatch.setattr(pipeline,'PENDING_LIMIT',1)
 first=run();j=first['journals'][0]
 assert first['failures'] and not j['metadata_complete'] and j['pdfs_saved']==1
 state=json.loads((work/'jacs/state.json').read_text())
 assert state['resume']['cursor']=='*' and 'last_success' not in state
 second=run();assert not second['failures'] and second['journals'][0]['pdfs_saved']==1 and not pending()
 assert len(calls['downloads'])==2


@pytest.mark.parametrize('ci,flag',[(False,True),(True,False),(True,True)])
def test_metadata_only_never_reads_queue_resolves_saves_or_ingests_pdf(tmp_path,monkeypatch,ci,flag):
 import paper_pipeline.__main__ as pipeline
 import server.jacs_collection as collector
 import server.store as storage
 if ci:monkeypatch.setenv('GITHUB_ACTIONS','true')
 article={'DOI':'10.1021/jacs.metadata-only','type':'journal-article','ISSN':['0002-7863'],'title':['PRIVATE TITLE'],'abstract':'PRIVATE BODY','author':[{'given':'Ada','family':'Chemist'},{'name':'Chemistry Consortium'}],'license':[{'URL':'PRIVATE LICENSE'}],'link':[{'URL':'PRIVATE PDF ROUTE'}]}
 def forbidden(*a,**k):raise AssertionError('PDF/private processing is forbidden')
 monkeypatch.setattr(collector.CrossrefClient,'_get',lambda self,url,*a:json.dumps({'message':{'items':[article],'total-results':1}}).encode() if '/journals/' in url else forbidden())
 for name in ('_licensed_pdf','_save_pdf','_attachment_valid'):monkeypatch.setattr(collector,name,forbidden)
 monkeypatch.setattr(collector.CrossrefClient,'pdf',forbidden);monkeypatch.setattr(storage,'Store',forbidden);monkeypatch.setattr(pipeline,'ingest',forbidden);monkeypatch.setattr(pipeline,'_queue_source',forbidden)
 work=tmp_path/'work';folder=work/'jacs';folder.mkdir(parents=True)
 # Invalid pending JSON proves metadata collection never even reads it.
 pending=folder/'pending.json';pending.write_text('PRIVATE INVALID QUEUE')
 out=tmp_path/'library.json'
 report=pipeline.weekly(ROOT/'paper_pipeline/journals.json',work,out,ROOT/'examples/total-synthesis.json',metadata_only=flag)
 assert not report['failures'] and report['pdf_policy']=='metadata_only'
 assert report['journals'][0]['pdf_work_attempted']==report['journals'][0]['reviews_created']==0
 assert pending.read_text()=='PRIVATE INVALID QUEUE' and not (folder/'archive').exists() and not (folder/'review').exists()
 paper=next(p for p in json.loads(out.read_text())['papers'] if p['doi']==article['DOI'])
 assert set(paper)=={'id','doi','authors'} and paper['authors']==['Ada Chemist','Chemistry Consortium']
 assert 'PRIVATE' not in out.read_text()


def test_github_actions_rejects_direct_pdf_ingest_before_file_access(tmp_path,monkeypatch):
 monkeypatch.setenv('GITHUB_ACTIONS','true')
 with pytest.raises(ValueError,match='disabled in GitHub Actions'):
  ingest(tmp_path/'absent.pdf',tmp_path/'review')
