"""Exercise actual data-commit capture, terminal receipt and public-response binding."""
import json
import os
from pathlib import Path
import subprocess
import sys

import pytest
from scripts.web_provenance import capture_identity, resolve_identity, verify_payload

ROOT=Path(__file__).resolve().parents[1]

def git(root,*args):
    return subprocess.check_output(['git',*args],cwd=root,text=True).strip()

def test_collected_data_commit_survives_fresh_checkout_terminal_and_http(tmp_path):
    work=tmp_path/'work';work.mkdir()
    remote=tmp_path/'remote.git'
    subprocess.run(['git','init','--bare',str(remote)],check=True,capture_output=True)
    git(work,'init','-b','source');git(work,'config','user.name','Fixture');git(work,'config','user.email','fixture@example.test')
    (work/'public').mkdir();body=json.loads((ROOT/'public/library.json').read_text())
    (work/'public/library.json').write_text(json.dumps(body))
    git(work,'add','.');git(work,'commit','-m','Code and seed A');a=git(work,'rev-parse','HEAD')
    body['generated_at']='2026-10-18T00:00:00+00:00'
    (work/'public/library.json').write_text(json.dumps(body))
    git(work,'commit','-am','Collected compact data B');b=git(work,'rev-parse','HEAD')
    git(work,'remote','add','origin',str(remote))
    identity=capture_identity(work,a)
    assert identity['workflow_commit']==a and identity['built_commit']==b and a!=b
    library=(work/'public/library.json').read_bytes()
    verify_payload(identity,identity,library,b'<html lang="en">')
    with pytest.raises(ValueError,match='digest'):
        verify_payload(identity,identity,library+b' ',b'<html lang="en">')
    with pytest.raises(ValueError,match='identity'):
        verify_payload(identity,{**identity,'built_commit':a},library,b'<html lang="en">')
    temp=tmp_path/'runner';temp.mkdir()
    env={**os.environ,'GITHUB_WORKSPACE':str(work),'GITHUB_SHA':a,'GITHUB_RUN_ID':'123','GITHUB_REPOSITORY':'fixture/chembrain','RUNNER_TEMP':str(temp),'WEB_PHASE':'build-finished','WEB_PROVENANCE':json.dumps(identity)}
    script=ROOT/'scripts/report_web_build.py'
    first=subprocess.run([sys.executable,str(script)],env=env,capture_output=True,text=True)
    assert first.returncode==0,first.stderr
    # A later job checks out the workflow trigger; it must retain data B from the receipt.
    git(work,'checkout',a)
    env.pop('WEB_PROVENANCE');env.update(WEB_TERMINAL='1',WEB_PHASE='terminal',WEB_RESULT='blocked')
    final=subprocess.run([sys.executable,str(script)],env=env,capture_output=True,text=True)
    assert final.returncode==0,final.stderr
    d=json.loads(final.stdout)
    assert d['terminal'] is True and d['commit']==a and d['built_commit']==b
    assert d['provenance']==identity and d['page_url'] is None
    stored=json.loads(git(work,'show','FETCH_HEAD:status.json'))
    assert stored['provenance']==identity
    with pytest.raises(ValueError,match='changed'):
        resolve_identity({**identity,'built_commit':a},identity,a)
    # A code modification cannot masquerade as a collection-only data change.
    (work/'unexpected-code.py').write_text('print(1)')
    git(work,'add','.');git(work,'commit','-m','Unreviewed code')
    with pytest.raises(ValueError,match='code differs'):
        capture_identity(work,a)
