"""Persist only compact metadata replay anchors/checkpoints, never PDF work.

Legacy snapshots containing pending PDF/provider data fail closed.
"""
import argparse,hashlib,json,os,re,subprocess,tempfile
from pathlib import Path
from datetime import datetime

REF='refs/heads/build/paper-state'
MAX_BYTES=10*1024*1024

def git(root,*args,check=True):
    return subprocess.run(['git',*args],cwd=root,capture_output=True,text=True,check=check,timeout=45)

def checked(snapshot):
    if not isinstance(snapshot,dict) or snapshot.get('version')!=1 or not isinstance(snapshot.get('journals'),dict):
        raise ValueError('Invalid processor state snapshot')
    if set(snapshot)-{'version','journals','run_id','source','feed'}:raise ValueError('Unexpected processor snapshot field')
    if len(json.dumps(snapshot).encode())>MAX_BYTES:raise ValueError('Processor state exceeds bound')
    if 'run_id' in snapshot and (not isinstance(snapshot['run_id'],str) or not re.fullmatch(r'[0-9]{1,30}',snapshot['run_id'])):raise ValueError('Invalid state run ID')
    if 'source' in snapshot and (not isinstance(snapshot['source'],str) or not re.fullmatch(r'[a-f0-9]{40}',snapshot['source'])):raise ValueError('Invalid state source')
    if 'feed' in snapshot:
        feed=snapshot['feed']
        if not isinstance(feed,dict) or set(feed)!={'ref','commit','library_sha256'}:raise ValueError('Invalid feed acknowledgment')
        if not isinstance(feed['ref'],str) or not re.fullmatch(r'refs/heads/[a-zA-Z0-9_./-]{1,200}',feed['ref']):raise ValueError('Invalid feed ref')
        for field,size in (('commit',40),('library_sha256',64)):
            if not isinstance(feed[field],str) or not re.fullmatch('[a-f0-9]{'+str(size)+'}',feed[field]):raise ValueError('Invalid feed identity')
    def timestamp(value):
        if not isinstance(value,str) or len(value)>50 or datetime.fromisoformat(value).tzinfo is None:raise ValueError('Invalid checkpoint timestamp')
    for slug,files in snapshot['journals'].items():
        if not re.fullmatch('[a-z0-9-]+',slug) or not isinstance(files,dict) or set(files)-{'state'}:
            raise ValueError('Unexpected processor state file')
        if 'state' in files:
            state=files['state']
            if not isinstance(state,dict) or set(state)-{'last_success','resume'} or len(json.dumps(state))>256_000:
                raise ValueError('Invalid processor checkpoint')
            if 'last_success' in state:timestamp(state['last_success'])
            if 'resume' in state:
                resume=state['resume']
                if not isinstance(resume,dict) or set(resume)!={'cursor','start','until','processed','started_at'}:raise ValueError('Invalid metadata replay anchor')
                if not isinstance(resume['cursor'],str) or not 0<len(resume['cursor'])<=200_000:raise ValueError('Invalid metadata cursor')
                if type(resume['processed']) is not int or resume['processed']<0:raise ValueError('Invalid processed count')
                for field in ('start','until'):
                    value=resume[field]
                    if not isinstance(value,str) or not re.fullmatch(r'\d{4}-\d{2}-\d{2}',value):raise ValueError('Invalid replay date')
                    datetime.fromisoformat(value)
                if resume['start']>resume['until']:raise ValueError('Invalid replay order')
                timestamp(resume['started_at'])
    return snapshot

def read_remote(root):
    remote=git(root,'ls-remote','origin',REF).stdout.split()
    if not remote:return None,None
    git(root,'fetch','origin',REF)
    commit=git(root,'rev-parse','FETCH_HEAD').stdout.strip()
    return commit,checked(json.loads(git(root,'show',commit+':state.json').stdout))

def restore(root,work):
    _,snapshot=read_remote(root)
    journals=snapshot['journals'] if snapshot else {}
    # Cached advancing progress is never authoritative. A cancelled publication
    # may have left it ahead of the feed; only the durable index can restore it.
    work=Path(work)
    if work.exists():
        for directory in work.iterdir():
            if directory.is_dir() and re.fullmatch('[a-z0-9-]+',directory.name) and 'state' not in journals.get(directory.name,{}):
                (directory/'state.json').unlink(missing_ok=True)
    if snapshot is None:return 'NO_DURABLE_STATE_YET'
    for slug,files in journals.items():
        directory=Path(work)/slug;directory.mkdir(parents=True,exist_ok=True)
        for name,value in files.items():
            path=directory/(name+'.json');temporary=path.with_suffix('.tmp')
            temporary.write_text(json.dumps(value,separators=(',',':')));temporary.replace(path)
    return 'RESTORED_METADATA_CHECKPOINTS'

def acknowledged_feed(root,feed_ref,feed_commit,library_sha256):
    """A local commit is insufficient: require the advertised origin and bytes."""
    if not isinstance(feed_ref,str) or not feed_ref.startswith('refs/heads/') or feed_ref==REF:
        raise ValueError('Expected the published feed branch ref')
    if git(root,'check-ref-format',feed_ref,check=False).returncode:
        raise ValueError('Invalid feed ref')
    if not isinstance(feed_commit,str) or not re.fullmatch('[0-9a-f]{40}',feed_commit):
        raise ValueError('Invalid feed commit')
    if not isinstance(library_sha256,str) or not re.fullmatch('[0-9a-f]{64}',library_sha256):
        raise ValueError('Invalid library digest')
    path=Path(root)/'public/library.json'
    if path.stat().st_size>5_000_000:raise ValueError('Public library exceeds bound')
    if hashlib.sha256(path.read_bytes()).hexdigest()!=library_sha256:
        raise ValueError('Local library digest differs from expected publication')
    blob=subprocess.run(['git','show',feed_commit+':public/library.json'],cwd=root,capture_output=True,check=True,timeout=45).stdout
    if hashlib.sha256(blob).hexdigest()!=library_sha256:
        raise ValueError('Feed commit library digest differs from local output')
    advertised=git(root,'ls-remote','origin',feed_ref).stdout.split()
    if advertised!=[feed_commit,feed_ref]:
        raise ValueError('Origin has not acknowledged this exact feed commit/ref')
    return {'ref':feed_ref,'commit':feed_commit,'library_sha256':library_sha256}


def save(root,work,run_id,source,*,feed_ref,feed_commit,library_sha256):
    publication=acknowledged_feed(root,feed_ref,feed_commit,library_sha256)
    snapshot={'version':1,'run_id':str(run_id),'source':source,'feed':publication,'journals':{}}
    work=Path(work)
    if work.exists():
        for folder in work.iterdir():
            if not folder.is_dir() or not re.fullmatch('[a-z0-9-]+',folder.name):continue
            files={}
            for name in ('state',):
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
        git(directory,'add','state.json');git(directory,'commit','-m','Preserve compact paper metadata checkpoints '+str(run_id))
        git(root,'fetch',str(directory),'state');commit=git(root,'rev-parse','FETCH_HEAD').stdout.strip()
        git(root,'push','origin',commit+':'+REF,'--force-with-lease='+REF+':'+(old or ''))
    return 'SAVED_METADATA_CHECKPOINTS'

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('operation',choices=['restore','save']);parser.add_argument('--work-dir',type=Path,required=True)
    parser.add_argument('--feed-ref');parser.add_argument('--feed-commit');parser.add_argument('--library-sha256')
    args=parser.parse_args();root=Path(os.environ['GITHUB_WORKSPACE'])
    if args.operation=='save' and not all((args.feed_ref,args.feed_commit,args.library_sha256)):
        parser.error('save requires --feed-ref, --feed-commit and --library-sha256')
    result=restore(root,args.work_dir) if args.operation=='restore' else save(root,args.work_dir,os.environ['GITHUB_RUN_ID'],os.environ['GITHUB_SHA'],feed_ref=args.feed_ref,feed_commit=args.feed_commit,library_sha256=args.library_sha256)
    print(result)

if __name__=='__main__':main()
