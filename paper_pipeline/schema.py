"""Shared portable v1 package contract; no PDF, full text or embedded structures."""
import hashlib
import json
import re
import math

KINDS = ('papers', 'chemicals', 'solutions', 'reactions')

def key(namespace, value):
    return namespace + '-' + hashlib.sha256(value.encode()).hexdigest()[:20]

def doi(value):
    value = re.sub(r'^(?:https?://(?:dx\.)?doi\.org/|doi:\s*)', '', value.strip(), flags=re.I).lower()
    if not re.fullmatch(r'10\.\d{4,9}/[^\s<>?#]+', value):
        raise ValueError('Invalid DOI')
    return value

def validate(data):
    if not isinstance(data, dict) or (isinstance(data.get('schema_version'),bool) or data.get('schema_version') != 1):
        raise ValueError('Expected Chembrain package schema_version 1')
    if len(json.dumps(data).encode()) > 5_000_000:
        raise ValueError('Package exceeds 5 MB; split the import')
    allowed = {'schema_version', 'generated_at', 'papers', 'chemicals', 'solutions', 'reactions'}
    if set(data) - allowed:
        raise ValueError('Only normalized library fields may be transferred')
    for kind in KINDS:
        if not isinstance(data.get(kind), list):
            raise ValueError('Missing entity table: ' + kind)
        ids = set()
        for row in data[kind]:
            if not isinstance(row, dict) or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9._:-]{0,120}', row.get('id', '')) or row['id'] in ids:
                raise ValueError('Invalid or duplicate entity ID in ' + kind)
            ids.add(row['id'])
    papers={p['id'] for p in data['papers']}; chemicals={c['id'] for c in data['chemicals']}; solutions={s['id'] for s in data['solutions']}
    seen=set()
    for p in data['papers']:
        p['doi']=doi(p['doi'])
        if p['doi'] in seen or not p.get('title') or not isinstance(p.get('authors'),list) or not all(isinstance(a,str) for a in p['authors']):
            raise ValueError('Paper DOI must be unique with title/authors')
        seen.add(p['doi'])
    for c in data['chemicals']:
        if not isinstance(c.get('aliases'),list) or not all(isinstance(x,str) for x in c['aliases']):raise ValueError('Chemical aliases must be a string array')
        if not c.get('name') or c.get('kind') not in ('compound','reagent','solvent','catalyst'):
            raise ValueError('Chemical name and kind required')
    for s in data['solutions']:
        for value in [s.get('concentration')]+[c.get('amount') for c in s.get('solutes',[])]:
            if value is not None and (isinstance(value,bool) or not isinstance(value,(int,float)) or not math.isfinite(value) or value<0):raise ValueError('Invalid solution amount/concentration')
        if any(c not in chemicals for c in s.get('solvents', [])) or any(c.get('chemical_id') not in chemicals for c in s.get('solutes', [])):
            raise ValueError('Unresolved solution chemical')
    for r in data['reactions']:
        if not r.get('name') or r.get('status') not in ('draft','reviewed') or not r.get('products') or not r.get('reactants'):
            raise ValueError('Reaction name, status and participants required')
        if any(c not in chemicals for c in r['reactants']+r['products']+r.get('targets', [])):
            raise ValueError('Unresolved reaction participant')
        for step in r.get('steps', []):
            if step.get('solution_id') and step['solution_id'] not in solutions:
                raise ValueError('Unresolved reaction solution')
        if not r.get('evidence') or any(e.get('paper_id') not in papers or not isinstance(e.get('page'),int) or isinstance(e.get('page'),bool) or e['page']<1 or not e.get('locator') for e in r['evidence']):
            raise ValueError('Reaction requires source DOI and 1-based PDF page/locator')
        y=r.get('yield_percent')
        if y is not None and (isinstance(y,bool) or not isinstance(y,(float,int)) or not math.isfinite(y) or not 0<=y<=100):
            raise ValueError('Invalid yield')
    for table,fields in [('papers',['title','journal','notes']),('chemicals',['name','smiles','inchikey','formula','notes']),('reactions',['name','notes','yield_basis'])]:
        for row in data[table]:
            if any(row.get(f) is not None and not isinstance(row[f],str) for f in fields):raise ValueError('Invalid text metadata')
    # Block document bodies and unbounded free-text even inside entity metadata.
    def compact(value):
        if isinstance(value,dict):
            if set(value) & {'pdf','pages','full_text','text','quote','candidate_text','svg','image','base64'}:
                raise ValueError('Document text/images belong in the processor, not the library package')
            for v in value.values():compact(v)
        elif isinstance(value,list):
            for v in value:compact(v)
        elif isinstance(value,str) and len(value)>3000:raise ValueError('Text field exceeds compact package limit')
    compact(data)
    return data


def normalize(data):
    """Canonical known structures/DOIs, deduplicate and relink all foreign keys."""
    import copy
    from server.chemistry import describe_molecule
    data=copy.deepcopy(data)
    if not isinstance(data,dict) or data.get('schema_version')!=1:raise ValueError('Expected v1 package')
    paper_map={};chemical_map={};papers=[];chemicals=[]
    for p in data.get('papers',[]):
        p['doi']=doi(p['doi']);existing=next((x for x in papers if x['doi']==p['doi']),None)
        paper_map[p['id']]=existing['id'] if existing else p['id']
        if not existing:papers.append(p)
    for c in data.get('chemicals',[]):
        if c.get('smiles'):c.update(describe_molecule(c['smiles']))
        existing=next((x for x in chemicals if c.get('inchikey') and x.get('inchikey')==c['inchikey']),None)
        chemical_map[c['id']]=existing['id'] if existing else c['id']
        if existing:existing['aliases']=list(dict.fromkeys(existing.get('aliases',[])+c.get('aliases',[])+([c['name']] if c['name']!=existing['name'] else [])))
        else:chemicals.append(c)
    for s in data.get('solutions',[]):
        s['solvents']=[chemical_map.get(x,x) for x in s.get('solvents',[])]
        for c in s.get('solutes',[]):c['chemical_id']=chemical_map.get(c['chemical_id'],c['chemical_id'])
    for r in data.get('reactions',[]):
        for field in ('reactants','products','targets'):r[field]=[chemical_map.get(x,x) for x in r.get(field,[])]
        for e in r.get('evidence',[]):e['paper_id']=paper_map.get(e['paper_id'],e['paper_id'])
    data['papers']=papers;data['chemicals']=chemicals
    return validate(data)
