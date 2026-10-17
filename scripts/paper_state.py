"""Persist public DOI retry/checkpoint metadata across best-effort Actions caches.

This branch contains no archives, review candidates or local file paths. Archive
bytes remain in the processor workspace/cache, not in this durable queue index.
"""
import argparse,json,os,re,subprocess,tempfile
from pathlib import Path

REF='refs/heads/build/paper-state'
MAX_BYTES=10*1024*1024
SOURCE_FIELDS={'DOI','type','ISSN','title','author','license','link'}

def git(root,*args,check=True):
    return subprocess.run(['git',*args],cwd=root,capture_output=True,text=True,check=check,timeout=45)

def checked(snapshot):
    if not isinstance(snapshot,dict) or snapshot.get('version')!=1 or not isinstance(snapshot.get('journals'),dict):
        raise ValueError('Invalid processor state snapshot')
    if len(json.dumps(snapshot).encode())>MAX_BYTES:raise ValueError('Processor state exceeds bound')
    for slug,files in snapshot['journals'].items():
        if not re.fullmatch('[a-z0-9-]+',slug) or not isinstance(files,dict) or set(files)-{'state','pending'}:
            raise ValueError('Unexpected processor state file')
        if 'state' in files:
            state=files['state']
            if not isinstance(state,dict) or set(state)-{'last_success','resume'} or len(json.dumps(state))>256_000:
                raise ValueError('Invalid processor checkpoint')
        if 'pending' in files:
            pending=files['pending']
            if not isinstance(pending,dict) or pending.get('version')!=1 or not isinstance(pending.get('items'),dict) or len(pending['items'])>2000:
                raise ValueError('Invalid pending DOI queue')
            for identifier,entry in pending['items'].items():
                if not isinstance(identifier,str) or not isinstance(entry,dict) or set(entry)-{'source','status'}:
                    raise ValueError('Unexpected pending DOI metadata')
                source=entry.get('source')
                if not isinstance(source,dict) or set(source)-SOURCE_FIELDS or source.get('DOI','').lower()!=identifier:
                    raise ValueError('Unexpected pending DOI source')
                if entry.get('status') not in ('pending','failed','oa_unverified') or len(json.dumps(source).encode())>32*1024:
                    raise ValueError('Invalid pending DOI status')
    return snapshot

def read_remote(root):
    remote=git(root,'ls-remote','origin',REF).stdout.split()
    if not remote:return None,None
    git(root,'fetch','origin',REF)
    commit=git(root,'rev-parse','FETCH_HEAD').stdout.strip()
    return commit,checked(json.loads(git(root,'show',commit+':state.json').stdout))

def restore(root,work):
    _,snapshot=read_remote(root)
    if snapshot is None:return 'NO_DURABLE_STATE_YET'
    for slug,files in snapshot['journals'].items():
        directory=Path(work)/slug;directory.mkdir(parents=True,exist_ok=True)
        for name,value in files.items():
            path=directory/(name+'.json');temporary=path.with_suffix('.tmp')
            temporary.write_text(json.dumps(value,separators=(',',':')));temporary.replace(path)
    return 'RESTORED_PUBLIC_PENDING_AND_CHECKPOINTS'

def save(root,work,run_id,source):
    snapshot={'version':1,'run_id':str(run_id),'source':source,'journals':{}}
    work=Path(work)
    if work.exists():
        for folder in work.iterdir():
            if not folder.is_dir() or not re.fullmatch('[a-z0-9-]+',folder.name):continue
            files={}
            for name in ('state','pending'):
                path=folder/(name+'.json')
                if path.exists():
                    if path.stat().st_size>MAX_BYTES:raise ValueError('Processor state file exceeds bound')
                    files[name]=json.loads(path.read_text())
            if files:snapshot['journals'][folder.name]=files
    checked(snapshot)
    old,previous=read_remote(root)
    if previous and int(previous['run_id'])>int(run_id):raise ValueError('Refusing to overwrite a newer processor run')
    if previous:snapshot['journals']={**previous['journals'],**snapshot['journals']}
    checked(snapshot)
    with tempfile.TemporaryDirectory() as temporary:
        directory=Path(temporary)
        (directory/'state.json').write_text(json.dumps(snapshot,separators=(',',':')))
        git(directory,'init','-b','state');git(directory,'config','user.name','github-actions[bot]');git(directory,'config','user.email','41898282+github-actions[bot]@users.noreply.github.com')
        git(directory,'add','state.json');git(directory,'commit','-m','Preserve public paper retry state '+str(run_id))
        git(root,'fetch',str(directory),'state');commit=git(root,'rev-parse','FETCH_HEAD').stdout.strip()
        git(root,'push','origin',commit+':'+REF,'--force-with-lease='+REF+':'+(old or ''))
    return 'SAVED_PUBLIC_PENDING_AND_CHECKPOINTS'

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('operation',choices=['restore','save']);parser.add_argument('--work-dir',type=Path,required=True)
    args=parser.parse_args();root=Path(os.environ['GITHUB_WORKSPACE'])
    result=restore(root,args.work_dir) if args.operation=='restore' else save(root,args.work_dir,os.environ['GITHUB_RUN_ID'],os.environ['GITHUB_SHA'])
    print(result)

if __name__=='__main__':main()
