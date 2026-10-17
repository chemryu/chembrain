import copy,json
from pathlib import Path
import pymupdf
import pytest
from paper_pipeline.schema import normalize,validate
from paper_pipeline.__main__ import ingest,weekly
ROOT=Path(__file__).resolve().parents[1]
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
 out=tmp_path/'library.json';report=weekly(ROOT/'paper_pipeline/journals.json',tmp_path/'archive',out,ROOT/'examples/total-synthesis.json')
 assert report['failures'];assert 'private query' not in json.dumps(report)
 assert len(validate(json.loads(out.read_text()))['reactions'])==12
 assert not (tmp_path/'archive/jacs/state.json').exists()
def test_weekly_verified_oa_goes_only_to_private_archive(tmp_path,monkeypatch):
 from server.jacs_collection import CrossrefClient
 item={'DOI':'10.1021/jacs.fixture','type':'journal-article','ISSN':['0002-7863'],'title':['Fixture'], 'author':[{'given':'Ada','family':'Chemist'}], 'license':[{'URL':'https://creativecommons.org/licenses/by/4.0/','content-version':'vor','start':{'date-time':'2020-01-01T00:00:00Z'}}], 'link':[{'URL':'https://pubs.acs.org/doi/pdf/10.1021/jacs.fixture','content-type':'application/pdf','content-version':'vor'}]}
 monkeypatch.setattr(CrossrefClient,'_get',lambda *a,**k:json.dumps({'message':{'items':[item],'total-results':1}}).encode())
 with pymupdf.open() as doc:doc.new_page();pdf=doc.tobytes()
 monkeypatch.setattr(CrossrefClient,'pdf',lambda *a:pdf)
 out=tmp_path/'library.json';report=weekly(ROOT/'paper_pipeline/journals.json',tmp_path/'archive',out,ROOT/'examples/total-synthesis.json')
 assert not report['failures'];assert report['journals'][0]['pdfs_saved']==1
 assert list((tmp_path/'archive').rglob('*.pdf'));assert 'jacs_pdfs' not in out.read_text();assert 'Fixture' in out.read_text()
 repeat=weekly(ROOT/'paper_pipeline/journals.json',tmp_path/'archive',out,ROOT/'examples/total-synthesis.json');assert repeat['journals'][0]['pdfs_saved']==0
