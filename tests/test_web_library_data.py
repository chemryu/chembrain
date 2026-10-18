import subprocess,json
from pathlib import Path

def test_browser_package_relations_and_non_destructive_import():
 root=Path(__file__).resolve().parents[1]
 script=f'''
 import fs from 'node:fs';import assert from 'node:assert/strict';
 import {{validateLibrary,mergeLibrary,relatedReactions,paperReferences}} from {json.dumps((root/'src/libraryData.ts').as_uri())};
 const d=validateLibrary(JSON.parse(fs.readFileSync({json.dumps(str(root/'examples/total-synthesis.json'))},'utf8')));
 assert.equal(relatedReactions(d,null).length,0);assert.equal(relatedReactions(d,'paclitaxel').length,2);assert.equal(relatedReactions(d,'paclitaxel',true).length,8);
 assert.ok(d.papers.every(p=>Object.keys(p).sort().join(',')==='authors,doi,id'));
 const original=structuredClone(d);original.papers[0].doi='HTTPS://DOI.ORG/'+original.papers[0].doi.toUpperCase();const before=JSON.stringify(original);validateLibrary(original);assert.equal(JSON.stringify(original),before);
 d.reactions[0].name='My preserved edit';const repeated=mergeLibrary(d,JSON.parse(fs.readFileSync({json.dumps(str(root/'examples/total-synthesis.json'))},'utf8')));assert.equal(repeated.reactions[0].name,'My preserved edit');assert.equal(repeated.reactions.length,12);
 const incoming=structuredClone(d);incoming.papers[0].id='duplicate-paper';incoming.reactions.forEach(r=>r.evidence.forEach(e=>{{if(e.paper_id==='holton')e.paper_id='duplicate-paper';}}));incoming.reactions[0].id='new-reaction';
 const merged=mergeLibrary(d,incoming);assert.equal(merged.papers.length,3);assert.equal(merged.reactions.find(r=>r.id==='new-reaction').evidence[0].paper_id,'holton');
 const r=structuredClone(d.reactions[0]);r.evidence.push({{...r.evidence[0],locator:'another supporting locator'}});assert.equal(paperReferences(d,r).length,1);assert.equal(paperReferences(d,r)[0].evidence.length,2);
 for(const mutate of [x=>x.solutions[0].concentration={{bad:1}},x=>x.solutions[0].solvents=['missing'],x=>x.chemicals[0].notes={{bad:1}},x=>x.papers[0].full_text='body',x=>x.reactions[0].yield_percent=101]){{const bad=structuredClone(d);mutate(bad);assert.throws(()=>validateLibrary(bad));}}
 console.log('Normalized browser relations/import checks passed');
 '''
 result=subprocess.run(['node','--experimental-strip-types','--input-type=module','-e',script],capture_output=True,text=True,timeout=15)
 assert result.returncode==0,result.stdout+result.stderr
