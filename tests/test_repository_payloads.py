import json,subprocess,zipfile
from pathlib import Path

import pytest
from scripts.check_repository_payloads import check_files,audit_history

def test_gate_rejects_renamed_pdf_archives_and_unknown_library_fields(tmp_path):
    library=json.loads((Path(__file__).resolve().parents[1]/'public/library.json').read_text())
    (tmp_path/'library.json').write_text(json.dumps(library))
    (tmp_path/'molecule.svg').write_text('<svg/>')
    assert check_files(tmp_path,dist=tmp_path)['status']=='PASS'
    path=tmp_path/'renamed.dat';path.write_bytes(b'%PDF-1.7\noriginal document')
    with pytest.raises(ValueError,match='document payload'):check_files(tmp_path,dist=tmp_path)
    path.unlink()
    with zipfile.ZipFile(path,'w') as bundle:bundle.writestr('paper.pdf',b'%PDF-1.7\npaper')
    with pytest.raises(ValueError,match='document payload'):check_files(tmp_path,dist=tmp_path)
    path.unlink();library['papers'][0]['abstract']='Unapproved original text'
    (tmp_path/'library.json').write_text(json.dumps(library))
    with pytest.raises(ValueError):check_files(tmp_path,dist=tmp_path)


def test_history_audit_detects_removed_document_without_dumping_contents(tmp_path):
    def git(*args):return subprocess.check_output(['git',*args],cwd=tmp_path,text=True)
    git('init','-b','source');git('config','user.name','Fixture');git('config','user.email','fixture@example.test')
    p=tmp_path/'original.pdf';p.write_bytes(b'%PDF-1.7\nPRIVATE PAPER SENTINEL')
    data=tmp_path/'data.json';data.write_text(json.dumps({'quote':'PRIVATE TEXT SENTINEL'}))
    git('add','.');git('commit','-m','Old documents');p.unlink();data.unlink();git('add','-u');git('commit','-m','Remove from current tree')
    report=audit_history(tmp_path)
    assert len(report['pdf_blobs'])==len(report['paper_text_json_blobs'])==1
    assert 'PRIVATE' not in json.dumps(report) and report['history_rewritten'] is False
