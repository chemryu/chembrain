"""Source/run-bound Pages preview receipts, including an independent terminal job."""
import json,os,subprocess,tempfile
from datetime import datetime,timezone
from pathlib import Path
from web_provenance import resolve_identity

def git(cwd,*args,check=True):return subprocess.run(['git',*args],cwd=cwd,capture_output=True,check=check,timeout=45)
def bounded_log(data,limit=100000):
 if len(data)<=limit:return data
 marker=b'\n[... middle of oversized log omitted; beginning and end preserved ...]\n'
 size=(limit-len(marker))//2-8
 head=data[:size].decode('utf-8',errors='replace').encode('utf-8')
 tail=data[-size:].decode('utf-8',errors='replace').encode('utf-8')
 return head+marker+tail
def main():
 w=Path(os.environ['GITHUB_WORKSPACE']);run=os.environ['GITHUB_RUN_ID'];ref='refs/heads/build/web-run-'+run
 old={};old_commit=None;found=git(w,'ls-remote','origin',ref).stdout
 if found:
  git(w,'fetch','origin',ref);old_commit=git(w,'rev-parse','FETCH_HEAD').stdout.decode().strip();old=json.loads(git(w,'show',old_commit+':status.json').stdout)
  if old.get('commit')!=os.environ['GITHUB_SHA'] or old.get('run_id')!=run:raise ValueError('Web receipt source/run mismatch')
 terminal=os.environ.get('WEB_TERMINAL')=='1';status=os.environ.get('WEB_RESULT','running') if terminal else 'running';phase=os.environ.get('WEB_PHASE','starting')
 url=os.environ.get('PAGE_URL') or None
 current=json.loads(os.environ['WEB_PROVENANCE']) if os.environ.get('WEB_PROVENANCE') else None
 identity=resolve_identity(current,old.get('provenance'),os.environ['GITHUB_SHA'])
 d={'commit':os.environ['GITHUB_SHA'],'built_commit':identity['built_commit'] if identity else None,'provenance':identity,'run_id':run,'run_url':f"https://github.com/{os.environ['GITHUB_REPOSITORY']}/actions/runs/{run}",'reported_at':datetime.now(timezone.utc).isoformat(),'status':status,'terminal':terminal,'phase':phase,'page_url':url,'facts':json.loads(os.environ.get('WEB_FACTS') or '{}'),'independent_qa':'SEPARATE_REVIEW_REQUIRED; preview only','phases':(old.get('phases',[])+[{'phase':phase,'at':datetime.now(timezone.utc).isoformat()}])[-40:]}
 with tempfile.TemporaryDirectory(dir=os.environ['RUNNER_TEMP']) as temp:
  p=Path(temp);(p/'status.json').write_text(json.dumps(d,indent=2))
  for name in ('web-build.log','web-tests.log','web-browser.log','web-access.log','pages-config.log','pages-config.json','portable-build.log','portable-browser.log','browser-manifest.json'):
   f=w/name
   if old_commit:
    prior=git(w,'show',old_commit+':'+name,check=False)
    if prior.returncode==0:(p/name).write_bytes(prior.stdout)
   if f.exists():(p/name).write_bytes(bounded_log(f.read_bytes()))
  git(p,'init','-b','receipt');git(p,'config','user.name','github-actions[bot]');git(p,'config','user.email','41898282+github-actions[bot]@users.noreply.github.com');git(p,'add','.');git(p,'commit','-m',f'Web preview {run}: {phase} {status}')
  git(w,'fetch',str(p),'receipt');commit=git(w,'rev-parse','FETCH_HEAD').stdout.decode().strip();git(w,'push','origin',commit+':'+ref,'--force')
  # Latest is just an index; older workflow finalizers must not replace newer runs.
  for _ in range(3):
   remote=git(w,'ls-remote','origin','refs/heads/build/web-status').stdout.decode().split();lease=remote[0] if remote else ''
   if remote:
    git(w,'fetch','origin','refs/heads/build/web-status');latest=json.loads(git(w,'show','FETCH_HEAD:status.json').stdout)
    if int(latest['run_id'])>int(run):break
   r=git(w,'push','origin',commit+':refs/heads/build/web-status','--force-with-lease=refs/heads/build/web-status:'+lease,check=False)
   if r.returncode==0:break
  else:raise RuntimeError('Latest web receipt publication failed')
 print(json.dumps(d))
if __name__=='__main__':main()
