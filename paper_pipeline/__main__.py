"""Separate weekly paper processor. PDFs/review candidates never enter the web bundle."""
import argparse
from datetime import datetime,timedelta,timezone
import hashlib,json,re,sys,tempfile,urllib.parse
from pathlib import Path
import pymupdf
from .schema import doi,key,validate,normalize


def write_json(path,data):
 path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
 with tempfile.NamedTemporaryFile(mode='w',encoding='utf-8',dir=path.parent,delete=False) as f:
  json.dump(data,f,ensure_ascii=False,separators=(',',':'));temporary=Path(f.name)
 try:temporary.replace(path)
 finally:temporary.unlink(missing_ok=True)


def private_work(path):
 path=Path(path).resolve();root=Path(__file__).resolve().parent.parent
 if path==root or root in path.parents:raise ValueError("Keep PDF archives and review text outside the application repository")
 return path

def ingest(pdf,work,explicit_doi=None):
 pdf=Path(pdf);work=private_work(work);work.mkdir(parents=True,exist_ok=True)
 if pdf.stat().st_size>30*1024*1024:raise ValueError('PDF exceeds 30 MB')
 digest=hashlib.sha256(pdf.read_bytes()).hexdigest()
 with pymupdf.open(pdf) as doc:
  if doc.is_encrypted or not 0<len(doc)<=400:raise ValueError('Use an unencrypted PDF of 1–400 pages')
  found=[];candidates=[]
  for n,p in enumerate(doc,1):
   text=p.get_text()
   for value in re.findall(r'10\.\d{4,9}/[^\s<>]+',text):
    try:normalized=doi(value.rstrip('.,;)'))
    except ValueError:continue
    if normalized not in found:found.append(normalized)
   for block in re.split(r'\n\s*\n|(?<=[.!?])\s+(?=[A-Z])',text):
    if re.search(r'\b(yield|cyclization|oxidation|reduction|coupling|deprotection)\b',block,re.I):
     candidates.append({'page':n,'candidate_text':re.sub(r'\s+',' ',block)[:600],'status':'needs_review'})
  title=str(doc.metadata.get('title') or pdf.stem)
 result={'source_sha256':digest,'source_filename':pdf.name,'suggested_title':title,'doi':doi(explicit_doi) if explicit_doi else (found[0] if len(found)==1 else None),'doi_candidates':found,'metadata_status':'needs_review','candidates':candidates[:300],
         'instructions':'Review article identity, authors, scheme participants and each stage. Multiple DOIs may include adjacent articles or references. No candidate is a verified reaction. Export only a curated v1 package.'}
 write_json(work/(digest+'.review.json'),result)
 return result


# The download queue is separate from the metadata cursor/checkpoint. Limits apply
# to durable work as well as network attempts; a full queue leaves the current
# discovery page retryable instead of silently dropping its remaining articles.
PDF_WORK_LIMIT=10
PENDING_LIMIT=2000
PENDING_BYTES=8*1024*1024
SOURCE_BYTES=32*1024


def _queue_source(item):
 source={name:item[name] for name in ('DOI','type','ISSN','title','author','license','link') if name in item}
 if len(json.dumps(source).encode())>SOURCE_BYTES:raise ValueError('Pending article metadata exceeds bound')
 return source


def _save_pending(path,pending):
 payload={'version':1,'items':pending}
 if len(pending)>PENDING_LIMIT or len(json.dumps(payload).encode())>PENDING_BYTES:raise ValueError('Pending work bound reached')
 write_json(path,payload)


def _review_valid(folder,identifier,attachment):
 try:
  review=json.loads((folder/'review'/key('paper',identifier)/(attachment['sha256']+'.review.json')).read_text())
  return review.get('source_sha256')==attachment['sha256'] and review.get('doi')==identifier and review.get('metadata',{}).get('doi')==identifier
 except (OSError,ValueError,KeyError,TypeError,AttributeError):return False


def weekly(config,work,out,curated,max_pages=3):
 from server.jacs_collection import CrossrefClient,_licensed_pdf,_save_pdf,_utc,_attachment_valid
 from server.store import Store
 config=json.loads(Path(config).read_text());work=private_work(work);work.mkdir(parents=True,exist_ok=True)
 data=normalize(json.loads(Path(curated).read_text()))
 if Path(out).exists():
  previous=validate(json.loads(Path(out).read_text()))
  for table in ('papers','chemicals','solutions','reactions'):
   ids={r['id'] for r in data[table]};data[table].extend(r for r in previous[table] if r['id'] not in ids)
  data['generated_at']=previous.get('generated_at')
  data=normalize(data)
 known={p['doi'] for p in data['papers']};report={'journals':[],'pdf_policy':'explicit_open_license_only','failures':[]}
 for journal in config['journals']:
  if not journal.get('enabled',True):continue
  slug=journal['id'];issn=journal['issn']
  if not re.fullmatch(r'[a-z0-9-]+',slug) or not re.fullmatch(r'\d{4}-[\dX]{4}',issn):raise ValueError('Invalid journal configuration')
  folder=work/slug;folder.mkdir(exist_ok=True);statefile=folder/'state.json';state=json.loads(statefile.read_text()) if statefile.exists() else {}
  pendingfile=folder/'pending.json'
  if pendingfile.exists() and pendingfile.stat().st_size>PENDING_BYTES:raise ValueError('Pending work exceeds bound')
  pending=json.loads(pendingfile.read_text())['items'] if pendingfile.exists() else {}
  if not isinstance(pending,dict):raise ValueError('Invalid pending work')
  if len(pending)>PENDING_LIMIT:raise ValueError('Pending work exceeds bound')
  now=datetime.now(timezone.utc);start=now-timedelta(days=14)
  checkpoint=state.get('last_success') or data.get('generated_at')
  if checkpoint:start=min(start,datetime.fromisoformat(checkpoint)-timedelta(days=7))
  gateway=CrossrefClient();cursor='*';count=0;pdfs=0;complete=False;until=str(now.date());processed=0;crawl_started=now.isoformat()
  resume=state.get('resume')
  if resume:
   start=datetime.fromisoformat(resume['start']).replace(tzinfo=timezone.utc);until=resume['until'];cursor=resume['cursor'];processed=resume['processed'];crawl_started=resume['started_at']
  store=Store(folder/'archive');fresh={};attempts=0;reused=0;reviews=0;blocked=0;deferred=0
  def add_paper(item):
   identifier=doi(item['DOI'])
   if identifier not in known:
    paper={'id':key('paper',identifier),'doi':identifier,'title':str(item.get('title',['Untitled'])[0])[:1000],'journal':journal['name'],'authors':[' '.join(str(a.get(k,'')) for k in ('given','family')).strip() for a in item.get('author',[]) if isinstance(a,dict)],'notes':'Public Crossref bibliography. Reaction extraction and article identity require review.'}
    data['papers'].append(paper);known.add(identifier)
   return identifier
  try:
   for _ in range(max_pages):
    # Save the current page before processing it. Queue saturation/provider
    # interruption can replay this page safely without losing an eligible DOI.
    state['resume']={'cursor':cursor,'start':str(start.date()),'until':until,'processed':processed,'started_at':crawl_started}
    query=urllib.parse.urlencode({'filter':f'from-pub-date:{start.date()},until-pub-date:{until},type:journal-article','rows':100,'cursor':cursor})
    message=json.loads(gateway._get('https://api.crossref.org/journals/'+issn+'/works?'+query,{'api.crossref.org'},8*1024*1024))['message']
    items=message['items']
    if not isinstance(items,list) or len(items)>100:raise ValueError('Invalid provider page')
    # Only persist resume after a real page was received. Failed first discovery
    # leaves the prior metadata checkpoint untouched.
    for item in items:
     if item.get('type')!='journal-article' or issn not in item.get('ISSN',[]):continue
     identifier=add_paper(item);count+=1
     if slug!='jacs':continue
     attachment=store.get_metadata('jacs_collection_attachments',{}).get(identifier)
     valid=attachment and _attachment_valid(store,identifier,attachment)
     if valid and _review_valid(folder,identifier,attachment):continue
     candidate=_licensed_pdf(item,_utc())
     if candidate or identifier in pending or valid:
      source=_queue_source(item)
      entry={**pending.get(identifier,{}),'source':source,'status':'pending'}
      proposed={**pending,identifier:entry}
      _save_pending(pendingfile,proposed);pending=proposed;fresh[identifier]=source
    processed+=len(items)
    if not items or len(items)<100 or (isinstance(message.get('total-results'),int) and processed>=message['total-results']):complete=True;break
    next_cursor=message.get('next-cursor')
    if not next_cursor or next_cursor==cursor:raise ValueError('Provider cursor did not advance')
    cursor=next_cursor
    state['resume']={'cursor':cursor,'start':str(start.date()),'until':until,'processed':processed,'started_at':crawl_started};write_json(statefile,state)
   if complete:
    state.pop('resume',None);state['last_success']=crawl_started;write_json(statefile,state)
   else:
    write_json(statefile,state);report['failures'].append(slug+': page bound reached; metadata checkpoint retained')
  except Exception as error:
   # Keep a received/partially processed page retryable, including queue-bound
   # failures. An unavailable first provider request writes no new checkpoint.
   if count or processed:write_json(statefile,state)
   report['failures'].append(slug+' metadata: '+type(error).__name__)
  # Process insertion-ordered work independently of publication-date discovery.
  # Every refresh/download/review failure consumes an attempt; failures rotate
  # to the end so a blocked DOI cannot starve later eligible work indefinitely.
  for identifier in list(pending):
   entry=pending[identifier]
   attachment=store.get_metadata('jacs_collection_attachments',{}).get(identifier)
   valid=attachment and _attachment_valid(store,identifier,attachment)
   if valid and _review_valid(folder,identifier,attachment):
    reused+=1;pending.pop(identifier);_save_pending(pendingfile,pending);continue
   if attempts>=PDF_WORK_LIMIT:deferred+=1;continue
   attempts+=1
   try:
    add_paper(entry['source'])
    if not valid:
     # A stored source is provenance, never download authorization. Old work
     # must be re-resolved through the same public allowlisted gateway.
     item=fresh.get(identifier)
     if item is None:
      response=json.loads(gateway._get('https://api.crossref.org/works/'+urllib.parse.quote(identifier,safe='/'),{'api.crossref.org'},8*1024*1024))
      item=response['message']
     if not isinstance(item,dict) or doi(item['DOI'])!=identifier or item.get('type')!='journal-article' or issn not in item.get('ISSN',[]):raise ValueError('Pending DOI or journal mismatch')
     entry['source']=_queue_source(item);add_paper(item)
     candidate=_licensed_pdf(item,_utc()) if slug=='jacs' else None
     if candidate is None:
      blocked+=1;entry['status']='oa_unverified';report['failures'].append(slug+' PDF: current OA authorization unverified')
      pending.pop(identifier);pending[identifier]=entry;_save_pending(pendingfile,pending);continue
     # Persist refreshed license/link identity before any authorized fetch.
     pending[identifier]=entry;_save_pending(pendingfile,pending)
     _save_pdf(store,identifier,gateway.pdf(candidate),candidate,key('paper',identifier),now.isoformat());pdfs+=1
     attachment=store.get_metadata('jacs_collection_attachments')[identifier]
    else:reused+=1
    pdf=store.directory/'jacs_pdfs'/(hashlib.sha256(identifier.encode()).hexdigest()+'.pdf')
    reviewfolder=folder/'review'/key('paper',identifier)
    review=ingest(pdf,reviewfolder,identifier)
    review['metadata']=next(p for p in data['papers'] if p['doi']==identifier)
    write_json(reviewfolder/(review['source_sha256']+'.review.json'),review);reviews+=1
    pending.pop(identifier);_save_pending(pendingfile,pending)
   except Exception as error:
    entry['status']='failed';pending.pop(identifier,None);pending[identifier]=entry;_save_pending(pendingfile,pending)
    report['failures'].append(slug+' PDF/review: '+type(error).__name__)
  report['journals'].append({'journal':slug,'bibliographic_items':count,'pdfs_saved':pdfs,'pdf_work_attempted':attempts,'pdfs_reused':reused,'reviews_created':reviews,'pending':len(pending),'deferred':deferred,'oa_unverified':blocked,'window_start':start.date().isoformat(),'complete':complete,'metadata_complete':complete,'downloads_complete':not pending,'pdf_resolver':'ACS explicit CC license' if slug=='jacs' else 'DOI-only; local PDF ingestion available'})
 # Keep outputs compact. Neither archive paths nor review text are exported.
 if not report['failures']:data['generated_at']=datetime.now(timezone.utc).isoformat()
 write_json(out,validate(data));write_json(work/'weekly-report.json',report)
 return report


def main():
 p=argparse.ArgumentParser(description=__doc__);sub=p.add_subparsers(dest='command',required=True)
 a=sub.add_parser('ingest');a.add_argument('pdfs',nargs='+');a.add_argument('--work-dir',type=Path,required=True);a.add_argument('--doi')
 a=sub.add_parser('export');a.add_argument('--curated',type=Path,required=True);a.add_argument('--out',type=Path,required=True)
 a=sub.add_parser('weekly');a.add_argument('--config',default='paper_pipeline/journals.json');a.add_argument('--work-dir',type=Path,required=True);a.add_argument('--curated',default='examples/total-synthesis.json');a.add_argument('--out',type=Path,required=True);a.add_argument('--max-pages',type=int,default=3)
 args=p.parse_args()
 if args.command=='ingest':
  if args.doi and len(args.pdfs)!=1:p.error('--doi applies to a single PDF')
  for pdf in args.pdfs:
   result=ingest(pdf,args.work_dir,args.doi);print(json.dumps({'file':Path(pdf).name,'doi':result['doi'],'candidates':len(result['candidates']),'status':'needs_review'}))
 elif args.command=='export':write_json(args.out,normalize(json.loads(args.curated.read_text())))
 else:
  if not 1<=args.max_pages<=20:p.error('--max-pages must be 1–20')
  report=weekly(args.config,args.work_dir,args.out,args.curated,args.max_pages);print(json.dumps(report));return 1 if report['failures'] else 0
 return 0
if __name__=='__main__':raise SystemExit(main())
