from datetime import datetime
from pathlib import Path
import subprocess
import sys
import xml.etree.ElementTree as ET

import pytest
from fastapi.testclient import TestClient

from server.app import create_app
from server import collection_schedule
from scripts import desktop


def test_task_xml_uses_current_user_future_local_trigger_stable_command_and_safe_arguments(tmp_path):
    folder = tmp_path / 'A & B' / 'Local App Data'
    executable = folder / 'collector/Chembrain.exe'
    raw = collection_schedule.task_xml(executable,folder,'Monday','09:00','S-1-5-21-123-456',datetime(2026,10,19,9,0))
    task = ET.fromstring(raw)
    ns = {'t':collection_schedule.NAMESPACE}
    assert task.findtext('.//t:StartBoundary',namespaces=ns) == '2026-10-26T09:00:00'
    assert task.find('.//t:Monday',ns) is not None
    assert task.findtext('.//t:LogonType',namespaces=ns) == 'InteractiveToken'
    assert task.findtext('.//t:RunLevel',namespaces=ns) == 'LeastPrivilege'
    assert task.findtext('.//t:StartWhenAvailable',namespaces=ns) == 'true'
    assert task.findtext('.//t:MultipleInstancesPolicy',namespaces=ns) == 'IgnoreNew'
    assert task.findtext('.//t:Command',namespaces=ns) == str(executable.resolve())
    args=task.findtext('.//t:Arguments',namespaces=ns)
    assert '--sync-jacs' in args and str(folder.resolve()) in args
    assert 'password' not in raw.decode('utf-16').lower()


@pytest.mark.parametrize('weekday,time',[('Monday','25:00'),('noday','09:00'),('Friday','9:00'),('Sunday','10:99')])
def test_invalid_schedules_never_reach_windows_commands(weekday,time):
    with pytest.raises(ValueError):
        collection_schedule.task_xml(Path('app.exe'),Path('data'),weekday,time,'S-1-5-21-123')


def test_sync_cli_is_noninteractive_and_does_not_start_web_server(tmp_path,monkeypatch,capsys):
    from server import jacs_collection
    calls=[]
    monkeypatch.setattr(sys,'argv',['Chembrain.exe','--sync-jacs','--metadata-only','--days','7','--max-pages','1','--data-dir',str(tmp_path)])
    monkeypatch.setattr(jacs_collection,'collect_jacs',lambda store,**options: calls.append((store.directory,options)) or {'status':'success'})
    monkeypatch.setattr(desktop,'run',lambda *args,**kwargs: pytest.fail('Collector started the app UI'))
    assert desktop.main()==0
    assert calls==[(tmp_path,{'metadata_only':True,'days':7,'max_pages':1})]
    assert 'success' in capsys.readouterr().out


def test_collection_status_has_local_policy_and_weekly_controls(tmp_path):
    client=TestClient(create_app(tmp_path,demo=False))
    result=client.get('/api/collection/jacs')
    assert result.status_code==200
    body=result.json()
    assert body['policy']=='open_access_only' and body['running'] is False
    assert body['totals']=={'articles':0,'pdfs':0}
    assert body['schedule']['weekday']=='Monday' and body['schedule']['time']=='09:00'


def test_schedule_api_validates_types_and_sanitizes_windows_failure(tmp_path,monkeypatch):
    client=TestClient(create_app(tmp_path,demo=False))
    assert client.post('/api/collection/jacs/schedule',json={'enabled':'yes'}).status_code==422
    def broken(*args,**kwargs):
        raise subprocess.TimeoutExpired('private-machine-details',1)
    monkeypatch.setattr(collection_schedule,'configure_schedule',broken)
    response=client.post('/api/collection/jacs/schedule',json={'enabled':True,'weekday':'Monday','time':'09:00'})
    assert response.status_code==503 and 'private-machine-details' not in response.text


def test_manual_collection_updates_same_local_database_without_network(tmp_path,monkeypatch):
    from server import jacs_collection
    import threading
    app=create_app(tmp_path,demo=False)
    finished=threading.Event()
    def fake_collection(store):
        store.set_metadata(jacs_collection.STATE,{'status':'success','started_at':'fixture','finished_at':'fixture-done','discovered':0,'added':0,'existing':0,'pdfs_saved':0,'errors':[]})
        finished.set()
    monkeypatch.setattr(jacs_collection,'collect_jacs',fake_collection)
    client=TestClient(app)
    assert client.post('/api/collection/jacs/run',json={}).status_code==202
    assert finished.wait(3)
    assert client.get('/api/collection/jacs').json()['last_run']['status']=='success'
