"""Exercise the actual TypeScript presentation helper, without a browser or API."""
import subprocess
from pathlib import Path


def test_paper_grouping_keeps_all_provenance_without_changing_records():
    root = Path(__file__).resolve().parents[1]
    result = subprocess.run(["node", "--experimental-strip-types", "--input-type=module", "-e", r"""
import assert from 'node:assert/strict';
import {groupPaperReferences, normalizeReferenceDoi} from './src/references.ts';
assert.equal(normalizeReferenceDoi(' HTTPS://DX.DOI.ORG/10.1000/ABC '), '10.1000/abc');
assert.equal(normalizeReferenceDoi(' doi: 10.1000/ABC '), '10.1000/abc');
assert.equal(normalizeReferenceDoi(undefined), '');
const sources = [
  {id:'si',title:'Supporting information',doi:' HTTPS://doi.org/10.1000/ABC ',document_role:'supplement'},
  {id:'main',title:'Main article',doi:'10.1000/abc',document_role:'main'},
  {id:'different',title:'Different paper',doi:'10.1000/def',document_role:'main'},
  {id:'no-doi',title:'No DOI',document_role:'notes'},
];
const evidence = [
  {source_id:'si',page:3,locator:'Procedure A',page_numbering:'pdf'},
  {source_id:'si',page:5,locator:'Entry 3',page_numbering:'pdf'},
  {source_id:'main',page:79,locator:'Table 1',page_numbering:'printed'},
  {source_id:'different',page:1,locator:'Scheme 2'},
  {source_id:'no-doi',page:1,locator:'Notebook A'},
  {source_id:'no-doi',page:2,locator:'Notebook B'},
  {source_id:'missing-a',page:1},
  {source_id:'missing-b',page:1},
];
const before = JSON.stringify({sources,evidence});
const groups = groupPaperReferences(evidence,sources);
assert.equal(groups.length,5);
assert.equal(groups[0].doi,'10.1000/abc');
assert.equal(groups[0].source.title,'Main article');
assert.deepEqual(groups[0].citations.map(x=>x.evidence.locator),['Procedure A','Entry 3','Table 1']);
assert.deepEqual(groups[0].citations.map(x=>x.source.document_role),['supplement','supplement','main']);
assert.equal(groups[0].citations[0].evidence,evidence[0]);
assert.equal(groups[2].citations.length,2);
assert.notEqual(groups[3].key,groups[4].key);
assert.equal(JSON.stringify({sources,evidence}),before);
assert.deepEqual(groupPaperReferences([],sources),[]);
"""], cwd=root, capture_output=True, text=True)
    assert result.returncode == 0, result.stdout + result.stderr
