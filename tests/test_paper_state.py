"""The actual scheduled path retains capped DOI work even if its PDF cache vanishes."""
import json
import shutil
import subprocess
from pathlib import Path

import pytest
from scripts.paper_state import restore,save,checked

def git(root,*args):
    return subprocess.check_output(['git',*args],cwd=root,text=True).strip()

def test_pending_survives_missing_cache_without_archiving_document_text(tmp_path):
    repository=tmp_path/'repo';repository.mkdir();remote=tmp_path/'remote.git'
    subprocess.run(['git','init','--bare',str(remote)],check=True,capture_output=True)
    git(repository,'init','-b','source');git(repository,'remote','add','origin',str(remote))
    work=tmp_path/'work';folder=work/'jacs';folder.mkdir(parents=True)
    source={'DOI':'10.1021/jacs.fixture','type':'journal-article','ISSN':['0002-7863'],'title':['Public title'],'license':[],'link':[]}
    pending={'version':1,'items':{source['DOI']:{'source':source,'status':'pending'}}}
    state={'last_success':'2026-10-17T00:00:00+00:00'}
    (folder/'pending.json').write_text(json.dumps(pending));(folder/'state.json').write_text(json.dumps(state))
    (folder/'review').mkdir();(folder/'review/private.review.json').write_text('PRIVATE CANDIDATE TEXT')
    (folder/'archive').mkdir();(folder/'archive/private.pdf').write_bytes(b'PRIVATE PDF')
    assert save(repository,work,'100','a'*40).startswith('SAVED')
    payload=git(repository,'show','FETCH_HEAD:state.json')
    assert 'PRIVATE' not in payload and 'archive' not in payload and 'review' not in payload
    shutil.rmtree(work)
    assert restore(repository,work).startswith('RESTORED')
    assert json.loads((folder/'pending.json').read_text())==pending
    assert json.loads((folder/'state.json').read_text())==state
    assert not (folder/'archive').exists() and not (folder/'review').exists()
    with pytest.raises(ValueError,match='newer'):
        save(repository,work,'99','a'*40)
    # A failed invocation producing no files cannot clear another journal's queue.
    empty=tmp_path/'empty';empty.mkdir();save(repository,empty,'101','a'*40)
    shutil.rmtree(work);restore(repository,work)
    assert json.loads((folder/'pending.json').read_text())==pending
    bad={'version':1,'journals':{'jacs':{'pending':{'version':1,'items':{source['DOI']:{'source':{**source,'candidate_text':'document body'},'status':'pending'}}}}}}
    with pytest.raises(ValueError,match='source'):
        checked(bad)
