"""Check tracked/build payloads; audit reachable history without printing paper text."""
import argparse
import json
from pathlib import Path
import subprocess

ROOT=Path(__file__).resolve().parents[1]
DOCUMENT_KEYS={'quote','excerpt','abstract','full_text','candidate_text','page_text','document_text'}

def document_json(value):
    if isinstance(value,dict):
        return any(k in DOCUMENT_KEYS and v not in (None,'',[],{}) or document_json(v) for k,v in value.items())
    if isinstance(value,list):return any(document_json(v) for v in value)
    return False

def pdf_bytes(data):
    return data.lstrip(b'\xef\xbb\xbf\t\r\n ').startswith(b'%PDF-')

def check_files(root,dist=None):
    root=Path(root)
    if dist is not None:
        base=Path(dist).resolve();files=[p for p in base.rglob('*') if p.is_file()]
    else:
        base=root;names=subprocess.check_output(['git','ls-files','-z'],cwd=root).decode().split('\0');files=[root/n for n in names if n and (root/n).is_file()]
    problems=[]
    for path in files:
        relative=path.relative_to(base).as_posix();data=path.read_bytes()
        if path.suffix.lower() in {'.pdf','.zip','.tar','.gz','.tgz','.7z','.rar'} or pdf_bytes(data) or data.startswith((b'PK\x03\x04',b'\x1f\x8b')) or path.name.endswith('.review.json'):
            problems.append({'path':relative,'reason':'document payload'})
        if 'structures/' in relative and (path.suffix.lower() in {'.png','.jpg','.jpeg','.gif','.tif','.tiff','.webp'} or (path.suffix.lower()=='.svg' and (b'<image' in data.lower() or b'data:image' in data.lower()))):
            problems.append({'path':relative,'reason':'paper image payload; use generated structure SVGs only'})
        if path.suffix.lower()=='.json' and (dist is not None or relative.startswith(('public/','examples/'))):
            try:value=json.loads(data)
            except (ValueError,UnicodeError):continue
            if document_json(value):problems.append({'path':relative,'reason':'paper text field'})
    # The public contract is checked independently of filename/content heuristics.
    library=(Path(dist) if dist is not None else root/'public')/'library.json'
    if library.exists():
        from paper_pipeline.schema import validate
        validate(json.loads(library.read_bytes()))
    if problems:raise ValueError(json.dumps(problems))
    return {'status':'PASS','files_checked':len(files),'scope':'dist' if dist is not None else 'tracked working files'}

def audit_history(root):
    lines=subprocess.check_output(['git','rev-list','--objects','--all'],cwd=root,text=True).splitlines()
    names={line.split(' ',1)[0]:line.split(' ',1)[1] for line in lines if ' ' in line}
    ids=[line.split(' ',1)[0] for line in lines]
    output=subprocess.check_output(['git','cat-file','--batch'],cwd=root,input=('\n'.join(ids)+'\n').encode())
    position=0;blobs=0;documents=[];text_fields=[];crops=[]
    for _ in ids:
        end=output.index(b'\n',position);header=output[position:end].decode().split();size=int(header[2]);start=end+1;data=output[start:start+size];position=start+size+1
        if header[1]!='blob':continue
        blobs+=1;oid=header[0];name=names.get(oid,'(unnamed blob)')
        if name.lower().endswith('.pdf') or pdf_bytes(data):documents.append({'object':oid,'path':name})
        if name.endswith('.json'):
            try:value=json.loads(data)
            except (ValueError,UnicodeError):continue
            if document_json(value):text_fields.append({'object':oid,'path':name})
        if name in ('public/structures/paclitaxel.png','public/structures/doxycycline.png'):crops.append({'object':oid,'path':name})
    return {'scope':'locally reachable commits and fetched remote heads; not GitHub caches/artifacts/deleted server refs','objects':len(ids),'blobs':blobs,'pdf_blobs':documents,'paper_text_json_blobs':text_fields,'known_paper_crop_blobs':crops,'history_rewritten':False}

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--dist',type=Path);parser.add_argument('--history',action='store_true');args=parser.parse_args()
    if args.history:result=audit_history(ROOT)
    else:result=check_files(ROOT,args.dist)
    print(json.dumps(result,indent=2))

if __name__=='__main__':
    import sys
    sys.path.insert(0,str(ROOT))
    main()
