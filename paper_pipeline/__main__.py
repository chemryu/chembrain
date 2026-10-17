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
  now=datetime.now(timezone.utc);start=now-timedelta(days=14)
  checkpoint=state.get('last_success') or data.get('generated_at')
  if checkpoint:start=min(start,datetime.fromisoformat(checkpoint)-timedelta(days=7))
  gateway=CrossrefClient();cursor='*';count=0;pdfs=0;complete=False;failed=False;until=str(now.date());processed=0;crawl_started=now.isoformat()
  resume=state.get('resume')
  if resume:
   start=datetime.fromisoformat(resume['start']).replace(tzinfo=timezone.utc);until=resume['until'];cursor=resume['cursor'];processed=resume['processed'];crawl_started=resume['started_at'];failed=resume.get('failed',False)
  store=Store(folder/'archive')
  try:
   for _ in range(max_pages):
    query=urllib.parse.urlencode({'filter':f'from-pub-date:{start.date()},until-pub-date:{until},type:journal-article','rows':100,'cursor':cursor})
    message=json.loads(gateway._get('https://api.crossref.org/journals/'+issn+'/works?'+query,{'api.crossref.org'},8*1024*1024))['message']
    items=message['items']
    if not isinstance(items,list) or len(items)>100:raise ValueError('Invalid provider page')
    for item in items:
     if item.get('type')!='journal-article' or issn not in item.get('ISSN',[]):continue
     identifier=doi(item['DOI']);count+=1
     if identifier not in known:
      paper={'id':key('paper',identifier),'doi':identifier,'title':str(item.get('title',['Untitled'])[0])[:1000],'journal':journal['name'],'authors':[' '.join(str(a.get(k,'')) for k in ('given','family')).strip() for a in item.get('author',[]) if isinstance(a,dict)],'notes':'Public Crossref bibliography. Reaction extraction and article identity require review.'}
      data['papers'].append(paper);known.add(identifier)
     # ACS is the explicitly supported PDF resolver; other journals stay DOI-only.
     candidate=_licensed_pdf(item,_utc()) if slug=='jacs' else None
     if candidate and pdfs<10:
      attachments=store.get_metadata('jacs_collection_attachments',{})
      if identifier not in attachments or not _attachment_valid(store,identifier,attachments[identifier]):
       try:
        _save_pdf(store,identifier,gateway.pdf(candidate),candidate,key('paper',identifier),now.isoformat());pdfs+=1
        attachment=store.get_metadata('jacs_collection_attachments')[identifier]
        review=ingest(store.directory/attachment['filename'],folder/'review',identifier)
        review['metadata']=next(p for p in data['papers'] if p['doi']==identifier)
        write_json(folder/'review'/(review['source_sha256']+'.review.json'),review)
       except Exception as error:
        report['failures'].append(slug+' PDF: '+type(error).__name__);failed=True
    processed+=len(items)
    if not items or len(items)<100 or (isinstance(message.get('total-results'),int) and processed>=message['total-results']):complete=True;break
    next_cursor=message.get('next-cursor')
    if not next_cursor or next_cursor==cursor:raise ValueError('Provider cursor did not advance')
    cursor=next_cursor
    state['resume']={'cursor':cursor,'start':str(start.date()),'until':until,'processed':processed,'started_at':crawl_started,'failed':failed};write_json(statefile,state)
   if complete and failed and not report['failures']:report['failures'].append(slug+': prior PDF failure; checkpoint retained for retry')
   if complete:
    state.pop('resume',None)
    if not failed:state['last_success']=crawl_started
    write_json(statefile,state)
   if not complete:report['failures'].append(slug+': page bound reached; checkpoint retained')
  except Exception as error:report['failures'].append(slug+': '+type(error).__name__)
  report['journals'].append({'journal':slug,'bibliographic_items':count,'pdfs_saved':pdfs,'window_start':start.date().isoformat(),'complete':complete,'pdf_resolver':'ACS explicit CC license' if slug=='jacs' else 'DOI-only; local PDF ingestion available'})
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
