"""Fault injection at the bibliography/output progress publication boundary."""
from collections import Counter
from datetime import datetime,timezone
import json
from pathlib import Path
import urllib.parse

import pytest

import paper_pipeline.__main__ as pipeline
from paper_pipeline.schema import validate
from server.jacs_collection import CrossrefClient

ROOT=Path(__file__).resolve().parents[1]
CURATED=ROOT/'examples/total-synthesis.json'


def fixture(tmp_path,monkeypatch,count=1,existing=True,journals=1):
    clock={'now':datetime(2026,10,17,tzinfo=timezone.utc)}
    class FrozenDate(datetime):
        @classmethod
        def now(cls,tz=None):return clock['now']
    monkeypatch.setattr(pipeline,'datetime',FrozenDate)
    entries=[{'id':'jacs','issn':'0002-7863','name':'JACS'}]
    if journals==2:entries.append({'id':'science','issn':'0036-8075','name':'Science'})
    config=tmp_path/'journals.json';config.write_text(json.dumps({'journals':entries}))
    work=tmp_path/'archive';out=tmp_path/'library.json'
    original=json.loads(CURATED.read_text())
    original['papers'].append({'id':'user-paper','doi':'10.1021/jacs.personal','authors':['My author']})
    if existing:out.write_text(json.dumps(original))
    items={journal['issn']:[{'DOI':f'10.1021/jacs.durable-{journal["id"]}-{i}','type':'journal-article','ISSN':[journal['issn']],'title':[f'Durable {i}'],'author':[{'given':'Ada','family':'Chemist'}]} for i in range(count)] for journal in entries}
    calls=[]
    def get(self,url,*args,**kwargs):
        assert '/journals/' in url,'No non-OA bibliography item should trigger a PDF refresh'
        issn=url.split('/journals/',1)[1].split('/')[0]
        query=urllib.parse.parse_qs(urllib.parse.urlsplit(url).query)
        filters=dict(part.split(':',1) for part in query['filter'][0].split(','))
        cursor=query['cursor'][0];start=filters['from-pub-date'];until=filters['until-pub-date']
        calls.append((issn,start,until,cursor))
        selected=items[issn] if start<='2026-10-04'<=until else []
        offset=0 if cursor=='*' else 100
        assert cursor in ('*','page-two')
        return json.dumps({'message':{'items':selected[offset:offset+100],'total-results':len(selected),'next-cursor':'page-two'}}).encode()
    monkeypatch.setattr(CrossrefClient,'_get',get)
    def run(max_pages=3):return pipeline.weekly(config,work,out,CURATED,max_pages,metadata_only=True)
    def assert_recovered():
        data=validate(json.loads(out.read_text()));counts=Counter(p['doi'] for p in data['papers'])
        assert all(counts[item['DOI']]==1 for journal_items in items.values() for item in journal_items)
        if existing:
            assert next(p for p in data['papers'] if p['id']=='user-paper')==original['papers'][-1]
            assert data['reactions']==original['reactions']
            assert data['solutions']==original['solutions']
        return data
    return clock,config,work,out,items,calls,run,assert_recovered


def fail_output(monkeypatch,out):
    actual=pipeline.write_json
    def write(path,data):
        if Path(path)==out:raise OSError('injected output failure')
        return actual(path,data)
    monkeypatch.setattr(pipeline,'write_json',write)
    return actual


@pytest.mark.parametrize(('checkpoint','expected_start'),[
    ('2026-10-01T00:00:00+00:00','2026-09-17'),
    ('2026-10-16T00:00:00+00:00','2026-10-02'),
])
def test_completed_window_output_failure_preserves_progress_and_later_retry(tmp_path,monkeypatch,checkpoint,expected_start):
    clock,config,work,out,items,calls,run,recovered=fixture(tmp_path,monkeypatch,journals=2)
    old={}
    for slug in ('jacs','science'):
        path=work/slug/'state.json';path.parent.mkdir(parents=True)
        path.write_text(json.dumps({'last_success':checkpoint}));old[slug]=path.read_bytes()
    original=out.read_bytes();actual=fail_output(monkeypatch,out)
    with pytest.raises(OSError,match='output failure'):run()
    assert out.read_bytes()==original
    assert all((work/slug/'state.json').read_bytes()==value for slug,value in old.items())
    # At this point a new fourteen-day default window would lose October 4.
    clock['now']=datetime(2026,11,1,tzinfo=timezone.utc);monkeypatch.setattr(pipeline,'write_json',actual)
    assert not run()['failures'];recovered()
    assert all(start==expected_start for _,start,_,_ in calls)
    for slug in old:assert json.loads((work/slug/'state.json').read_text())=={'last_success':'2026-11-01T00:00:00+00:00'}


def test_capped_hundred_item_page_output_failure_never_skips_first_page(tmp_path,monkeypatch):
    clock,config,work,out,items,calls,run,recovered=fixture(tmp_path,monkeypatch,count=101)
    path=work/'jacs/state.json';path.parent.mkdir(parents=True)
    path.write_text(json.dumps({'last_success':'2026-10-01T00:00:00+00:00'}));old=path.read_bytes();original=out.read_bytes()
    actual=fail_output(monkeypatch,out)
    with pytest.raises(OSError):run(max_pages=1)
    assert path.read_bytes()==old and out.read_bytes()==original
    monkeypatch.setattr(pipeline,'write_json',actual)
    partial=run(max_pages=1)
    assert partial['failures'] and len(json.loads(out.read_text())['papers'])==104
    assert json.loads(path.read_text())['resume']['cursor']=='page-two'
    assert not run(max_pages=1)['failures'];recovered()
    assert [cursor for _,_,_,cursor in calls]==['*','*','page-two']


def test_interrupted_second_page_and_failed_output_replays_all_received_bibliography(tmp_path,monkeypatch):
    clock,config,work,out,items,calls,run,recovered=fixture(tmp_path,monkeypatch,count=101)
    path=work/'jacs/state.json';path.parent.mkdir(parents=True)
    path.write_text(json.dumps({'last_success':'2026-10-01T00:00:00+00:00'}));old=path.read_bytes();original=out.read_bytes()
    get=CrossrefClient._get;interrupt={'enabled':True}
    def flaky(self,url,*args,**kwargs):
        response=get(self,url,*args,**kwargs)
        if interrupt['enabled'] and 'cursor=page-two' in url:raise OSError('provider interrupted')
        return response
    monkeypatch.setattr(CrossrefClient,'_get',flaky)
    actual=fail_output(monkeypatch,out)
    with pytest.raises(OSError,match='output failure'):run()
    assert path.read_bytes()==old and out.read_bytes()==original
    interrupt['enabled']=False;monkeypatch.setattr(pipeline,'write_json',actual)
    assert not run()['failures'];recovered()
    assert [cursor for _,_,_,cursor in calls]==['*','page-two','*','page-two']


def test_output_validation_failure_cannot_advance_existing_progress(tmp_path,monkeypatch):
    clock,config,work,out,items,calls,run,recovered=fixture(tmp_path,monkeypatch)
    path=work/'jacs/state.json';path.parent.mkdir(parents=True)
    path.write_text(json.dumps({'last_success':'2026-10-01T00:00:00+00:00'}));old=path.read_bytes();original=out.read_bytes()
    actual=pipeline.validate;identifier=items['0002-7863'][0]['DOI']
    def reject_new_output(data):
        if any(p['doi']==identifier for p in data['papers']):raise ValueError('injected package validation failure')
        return actual(data)
    monkeypatch.setattr(pipeline,'validate',reject_new_output)
    with pytest.raises(ValueError,match='package validation failure'):run()
    assert path.read_bytes()==old and out.read_bytes()==original
    monkeypatch.setattr(pipeline,'validate',actual)
    assert not run()['failures'];recovered()


def test_first_ever_output_failure_retains_original_nonadvancing_window_on_late_retry(tmp_path,monkeypatch):
    clock,config,work,out,items,calls,run,recovered=fixture(tmp_path,monkeypatch,existing=False)
    actual=fail_output(monkeypatch,out)
    with pytest.raises(OSError):run()
    assert not out.exists()
    path=work/'jacs/state.json';anchor=json.loads(path.read_text())
    assert anchor=={'resume':{'cursor':'*','start':'2026-10-03','until':'2026-10-17','processed':0,'started_at':'2026-10-17T00:00:00+00:00'}}
    clock['now']=datetime(2026,11,1,tzinfo=timezone.utc)
    assert pipeline.prepare_anchors(config,work,out)=={'journals':[]}
    assert json.loads(path.read_text())==anchor
    monkeypatch.setattr(pipeline,'write_json',actual)
    assert not run()['failures'];recovered()
    assert calls==[('0002-7863','2026-10-03','2026-10-17','*')]*2
    assert json.loads(path.read_text())['last_success']=='2026-10-17T00:00:00+00:00'


def test_anchor_write_failure_stops_before_provider_or_package_mutation(tmp_path,monkeypatch):
    clock,config,work,out,items,calls,run,recovered=fixture(tmp_path,monkeypatch)
    original=out.read_bytes();actual=pipeline.write_json
    def write(path,data):
        if Path(path).name=='state.json':raise OSError('anchor failed')
        return actual(path,data)
    monkeypatch.setattr(pipeline,'write_json',write)
    with pytest.raises(OSError,match='anchor failed'):run()
    assert not calls and out.read_bytes()==original
    assert not (work/'jacs/state.json').exists()


def test_state_write_failure_after_output_keeps_durable_data_and_replay_is_idempotent(tmp_path,monkeypatch):
    clock,config,work,out,items,calls,run,recovered=fixture(tmp_path,monkeypatch)
    pipeline.prepare_anchors(config,work,out)
    statefile=work/'jacs/state.json';anchor=statefile.read_bytes();actual=pipeline.write_json
    def write(path,data):
        if Path(path)==statefile:raise OSError('injected private state failure')
        return actual(path,data)
    monkeypatch.setattr(pipeline,'write_json',write)
    report=run()
    assert report['failures']==['jacs metadata state: OSError']
    assert statefile.read_bytes()==anchor
    first=recovered()
    assert 'injected private' not in json.dumps(report)
    monkeypatch.setattr(pipeline,'write_json',actual)
    assert not run()['failures'];second=recovered()
    for table in ('papers','chemicals','solutions','reactions'):assert first[table]==second[table]
    assert not run()['failures'];recovered()


def test_anchor_uses_existing_output_checkpoint_and_never_replaces_valid_progress(tmp_path,monkeypatch):
    clock,config,work,out,items,calls,run,recovered=fixture(tmp_path,monkeypatch,journals=2)
    data=json.loads(out.read_text());data['generated_at']='2026-09-20T00:00:00+00:00';out.write_text(json.dumps(data))
    statefile=work/'science/state.json';statefile.parent.mkdir(parents=True)
    statefile.write_text(json.dumps({'last_success':'2026-09-01T00:00:00+00:00'}));original=statefile.read_bytes()
    assert pipeline.prepare_anchors(config,work,out)=={'journals':['jacs']}
    assert statefile.read_bytes()==original
    assert json.loads((work/'jacs/state.json').read_text())['resume']['start']=='2026-09-06'
    clock['now']=datetime(2026,11,1,tzinfo=timezone.utc)
    assert pipeline.prepare_anchors(config,work,out)=={'journals':[]}
    assert not calls


def test_future_output_timestamp_cannot_create_an_inverted_anchor(tmp_path,monkeypatch):
    clock,config,work,out,items,calls,run,recovered=fixture(tmp_path,monkeypatch,journals=2)
    data=json.loads(out.read_text());data['generated_at']='2027-01-01T00:00:00+00:00';out.write_text(json.dumps(data));old=out.read_bytes()
    with pytest.raises(ValueError,match='window order'):run()
    assert out.read_bytes()==old and not calls
    assert not list(work.rglob('state.json'))


@pytest.mark.parametrize('state',[
    [],{'unknown':'discard me'},{'last_success':'not a date'},{'last_success':'2026-10-17'},
    {'resume':{}},{'resume':{'cursor':'*','start':'2026-10-03','until':'2026-10-17','processed':-1,'started_at':'2026-10-17T00:00:00+00:00'}},
    {'resume':{'cursor':'*','start':'2026-10-18','until':'2026-10-17','processed':0,'started_at':'2026-10-17T00:00:00+00:00'}},
])
def test_malformed_progress_fails_closed_before_any_anchor_or_provider_request(tmp_path,monkeypatch,state):
    clock,config,work,out,items,calls,run,recovered=fixture(tmp_path,monkeypatch,journals=2)
    # The malformed second journal must prevent even the absent first journal's
    # preparation; no silently reset window or partially initialized crawl.
    path=work/'science/state.json';path.parent.mkdir(parents=True);path.write_text(json.dumps(state));old=path.read_bytes()
    with pytest.raises(ValueError):run()
    assert path.read_bytes()==old and not (work/'jacs/state.json').exists() and not calls
