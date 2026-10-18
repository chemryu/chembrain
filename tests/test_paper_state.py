"""Real Git publication boundary, retry-state recovery and private-file exclusion."""
import copy
import hashlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from datetime import datetime,timezone
from urllib.parse import parse_qs,urlsplit

import pytest
from scripts.paper_state import restore,save,checked,REF

ROOT=Path(__file__).resolve().parents[1]

def git(root,*args):
    return subprocess.check_output(['git',*args],cwd=root,text=True).strip()

def fixture_repo(tmp_path):
    repository=tmp_path/'repo';repository.mkdir();remote=tmp_path/'remote.git'
    subprocess.run(['git','init','--bare',str(remote)],check=True,capture_output=True)
    git(repository,'init','-b','source');git(repository,'config','user.name','Fixture');git(repository,'config','user.email','fixture@example.test')
    git(repository,'remote','add','origin',str(remote));(repository/'public').mkdir()
    library=repository/'public/library.json';library.write_bytes((ROOT/'public/library.json').read_bytes())
    git(repository,'add','.');git(repository,'commit','-m','Published feed A');a=git(repository,'rev-parse','HEAD');git(repository,'push','origin','HEAD:refs/heads/source')
    work=tmp_path/'work'
    return repository,work,library,a

def persist(repository,work,run='100',commit=None,ref='refs/heads/source',digest=None):
    return save(repository,work,run,git(repository,'rev-parse','HEAD'),feed_ref=ref,
                feed_commit=commit or git(repository,'rev-parse','HEAD'),
                library_sha256=digest or hashlib.sha256((repository/'public/library.json').read_bytes()).hexdigest())

def state_commit(repository):
    return git(repository,'ls-remote','origin',REF).split()[0]

def test_pending_survives_missing_cache_without_archiving_document_text(tmp_path):
    repository,work,library,a=fixture_repo(tmp_path);folder=work/'jacs';folder.mkdir(parents=True)
    source={'DOI':'10.1021/jacs.fixture','type':'journal-article','ISSN':['0002-7863'],'title':['Public title'],'license':[],'link':[]}
    pending={'version':1,'items':{source['DOI']:{'source':source,'status':'pending'}}}
    state={'last_success':'2026-10-17T00:00:00+00:00'}
    (folder/'pending.json').write_text(json.dumps(pending));(folder/'state.json').write_text(json.dumps(state))
    (folder/'review').mkdir();(folder/'review/private.review.json').write_text('PRIVATE CANDIDATE TEXT')
    (folder/'archive').mkdir();(folder/'archive/private.pdf').write_bytes(b'PRIVATE PDF')
    assert persist(repository,work).startswith('SAVED')
    payload=git(repository,'show','FETCH_HEAD:state.json')
    assert 'PRIVATE' not in payload and 'archive' not in payload and 'review' not in payload
    snapshot=json.loads(payload)
    assert snapshot['feed']=={'ref':'refs/heads/source','commit':a,'library_sha256':hashlib.sha256(library.read_bytes()).hexdigest()}
    shutil.rmtree(work)
    assert restore(repository,work).startswith('RESTORED')
    assert json.loads((folder/'pending.json').read_text())==pending
    assert json.loads((folder/'state.json').read_text())==state
    assert not (folder/'archive').exists() and not (folder/'review').exists()
    with pytest.raises(ValueError,match='newer'):
        persist(repository,work,run='99')
    empty=tmp_path/'empty';empty.mkdir();persist(repository,empty,run='101')
    shutil.rmtree(work);restore(repository,work)
    assert json.loads((folder/'pending.json').read_text())==pending
    bad={'version':1,'journals':{'jacs':{'pending':{'version':1,'items':{source['DOI']:{'source':{**source,'candidate_text':'document body'},'status':'pending'}}}}}}
    with pytest.raises(ValueError,match='source'):checked(bad)


def test_unpublished_feed_cannot_advance_state_and_same_run_published_feed_can(tmp_path):
    repository,work,library,a=fixture_repo(tmp_path);folder=work/'jacs';folder.mkdir(parents=True)
    (folder/'state.json').write_text(json.dumps({'last_success':'2026-10-17T00:00:00+00:00'}))
    original=library.read_bytes();persist(repository,work);prior=state_commit(repository)
    body=json.loads(original);body['generated_at']='2026-10-18T00:00:00+00:00';library.write_text(json.dumps(body))
    changed=library.read_bytes();git(repository,'commit','-am','Unpublished feed B');b=git(repository,'rev-parse','HEAD')
    (folder/'state.json').write_text(json.dumps({'last_success':'2026-10-18T00:00:00+00:00'}))
    for parameters in [dict(),dict(ref='refs/heads/missing'),dict(commit=a),dict(digest='0'*64)]:
        with pytest.raises(ValueError):persist(repository,work,**parameters)
        assert state_commit(repository)==prior
    git(repository,'push','origin','HEAD:refs/heads/source')
    persist(repository,work) # same run 100 supports bootstrap A and advanced B.
    advanced=state_commit(repository);snapshot=json.loads(git(repository,'show',advanced+':state.json'))
    assert snapshot['feed']['commit']==b
    assert snapshot['feed']['library_sha256']==hashlib.sha256(changed).hexdigest()
    assert snapshot['journals']['jacs']['state']['last_success'].startswith('2026-10-18')
    library.write_bytes(original) # old acknowledgment A remains invalid after origin moved to B.
    with pytest.raises(ValueError,match='acknowledged'):persist(repository,work,commit=a)
    assert state_commit(repository)==advanced
    library.write_bytes(changed)
    env={**os.environ,'GITHUB_WORKSPACE':str(repository),'GITHUB_RUN_ID':'101','GITHUB_SHA':b}
    result=subprocess.run([sys.executable,str(ROOT/'scripts/paper_state.py'),'save','--work-dir',str(work)],env=env,capture_output=True,text=True)
    assert result.returncode!=0 and 'save requires' in result.stderr
    assert state_commit(repository)==advanced


def test_first_anchor_recovers_non_oa_metadata_after_output_failure_and_cache_eviction(tmp_path,monkeypatch):
    import paper_pipeline.__main__ as pipeline
    from server.jacs_collection import CrossrefClient
    repository,work,library,a=fixture_repo(tmp_path)
    clock={'now':datetime(2026,10,17,tzinfo=timezone.utc)}
    class Clock(datetime):
        @classmethod
        def now(cls,tz=None):return clock['now']
    monkeypatch.setattr(pipeline,'datetime',Clock)
    article={'DOI':'10.1021/jacs.failed-publication','type':'journal-article','ISSN':['0002-7863'],'title':['Non-OA metadata only']}
    windows=[]
    def get(self,url,*args):
        query=parse_qs(urlsplit(url).query);window=query['filter'][0];windows.append(window)
        start=window.split('from-pub-date:',1)[1].split(',')[0]
        items=[article] if start<='2026-10-04' else []
        return json.dumps({'message':{'items':items,'total-results':len(items)}}).encode()
    monkeypatch.setattr(CrossrefClient,'_get',get)
    pipeline.prepare_anchors(ROOT/'paper_pipeline/journals.json',work,library)
    persist(repository,work) # nonadvancing bootstrap against already published A, BEFORE discovery.
    prior=state_commit(repository);before=library.read_bytes();anchor=(work/'jacs/state.json').read_bytes()
    real_write=pipeline.write_json
    def output_failure(path,value):
        if Path(path)==library:raise OSError('Injected output replacement failure')
        return real_write(path,value)
    monkeypatch.setattr(pipeline,'write_json',output_failure)
    with pytest.raises(OSError):pipeline.weekly(ROOT/'paper_pipeline/journals.json',work,library,ROOT/'examples/total-synthesis.json')
    assert library.read_bytes()==before and (work/'jacs/state.json').read_bytes()==anchor
    assert state_commit(repository)==prior
    shutil.rmtree(work) # total runner/cache loss; only acknowledged A and state branch survive.
    restore(repository,work);clock['now']=datetime(2026,11,24,tzinfo=timezone.utc)
    monkeypatch.setattr(pipeline,'write_json',real_write)
    report=pipeline.weekly(ROOT/'paper_pipeline/journals.json',work,library,ROOT/'examples/total-synthesis.json')
    output=json.loads(library.read_text())
    assert not report['failures']
    assert sum(p['doi']==article['DOI'] for p in output['papers'])==1
    assert all('from-pub-date:2026-10-03' in w for w in windows)
    assert output['reactions']==json.loads(before)['reactions']


def test_restore_does_not_trust_unpublished_checkpoint_left_in_cache(tmp_path):
    repository,work,library,a=fixture_repo(tmp_path)
    folder=work/'jacs';folder.mkdir(parents=True)
    (folder/'state.json').write_text(json.dumps({'last_success':'2099-01-01T00:00:00+00:00'}))
    (folder/'archive').mkdir();(folder/'archive/retained.pdf').write_bytes(b'archive bytes')
    assert restore(repository,work)=='NO_DURABLE_STATE_YET'
    assert not (folder/'state.json').exists()
    assert (folder/'archive/retained.pdf').exists()
