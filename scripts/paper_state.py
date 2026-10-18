"""Persist public DOI retry/checkpoint metadata across best-effort Actions caches.

This branch contains no archives, review candidates or local file paths. Archive
bytes remain in the processor workspace/cache, not in this durable queue index.
"""
import argparse,hashlib,json,os,re,subprocess,tempfile
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
    return 'RESTORED_PUBLIC_PENDING_AND_CHECKPOINTS'

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
    parser.add_argument('--feed-ref');parser.add_argument('--feed-commit');parser.add_argument('--library-sha256')
    args=parser.parse_args();root=Path(os.environ['GITHUB_WORKSPACE'])
    if args.operation=='save' and not all((args.feed_ref,args.feed_commit,args.library_sha256)):
        parser.error('save requires --feed-ref, --feed-commit and --library-sha256')
    result=restore(root,args.work_dir) if args.operation=='restore' else save(root,args.work_dir,os.environ['GITHUB_RUN_ID'],os.environ['GITHUB_SHA'],feed_ref=args.feed_ref,feed_commit=args.feed_commit,library_sha256=args.library_sha256)
    print(result)

if __name__=='__main__':main()
