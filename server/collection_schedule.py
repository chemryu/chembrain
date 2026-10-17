"""Current-user Windows weekly task for the packaged, keyless JACS collector."""
import hashlib
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timedelta
import xml.etree.ElementTree as ET

WEEKDAYS = ('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday')
NAMESPACE = 'http://schemas.microsoft.com/windows/2004/02/mit/task'


def supported():
    return sys.platform == 'win32' and bool(getattr(sys, 'frozen', False))


def task_name(data_dir):
    identity = hashlib.sha256(str(Path(data_dir).resolve()).casefold().encode()).hexdigest()[:12]
    return 'Chembrain JACS ' + identity


def validate_schedule(weekday, time):
    if weekday not in WEEKDAYS or not re.fullmatch(r'(?:[01]\d|2[0-3]):[0-5]\d', time):
        raise ValueError('Choose a valid weekday and local time (HH:MM).')


def task_xml(executable, data_dir, weekday, time, user_sid, now=None):
    validate_schedule(weekday, time)
    if not re.fullmatch(r'S-1-\d+(?:-\d+)+', user_sid):
        raise ValueError('Unable to identify the current Windows user.')
    now = now or datetime.now()
    hour, minute = map(int, time.split(':'))
    start = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
    start += timedelta(days=(WEEKDAYS.index(weekday) - start.weekday()) % 7)
    if start <= now + timedelta(minutes=1):
        start += timedelta(days=7)
    ET.register_namespace('', NAMESPACE)
    def child(parent, name, text=None, **attributes):
        element = ET.SubElement(parent, '{' + NAMESPACE + '}' + name, attributes)
        element.text = text
        return element
    root = ET.Element('{' + NAMESPACE + '}Task', version='1.2')
    registration = child(root, 'RegistrationInfo')
    child(registration, 'Description', 'Collect JACS bibliography and verified open-access PDFs. No subscription authentication or AI API keys.')
    triggers = child(root, 'Triggers')
    calendar = child(triggers, 'CalendarTrigger')
    child(calendar, 'StartBoundary', start.isoformat(timespec='seconds'))
    child(calendar, 'Enabled', 'true')
    weekly = child(calendar, 'ScheduleByWeek')
    child(weekly, 'WeeksInterval', '1')
    child(child(weekly, 'DaysOfWeek'), weekday)
    principal = child(child(root, 'Principals'), 'Principal', id='CurrentUser')
    child(principal, 'UserId', user_sid)
    child(principal, 'LogonType', 'InteractiveToken')
    child(principal, 'RunLevel', 'LeastPrivilege')
    settings = child(root, 'Settings')
    for name, value in [('MultipleInstancesPolicy','IgnoreNew'), ('DisallowStartIfOnBatteries','false'),
                        ('StopIfGoingOnBatteries','false'), ('AllowHardTerminate','true'),
                        ('StartWhenAvailable','true'), ('RunOnlyIfNetworkAvailable','true'),
                        ('AllowStartOnDemand','true'), ('Enabled','true'), ('Hidden','false'),
                        ('RunOnlyIfIdle','false'), ('WakeToRun','false'), ('ExecutionTimeLimit','PT30M'), ('Priority','7')]:
        child(settings, name, value)
    action = child(child(root, 'Actions', Context='CurrentUser'), 'Exec')
    child(action, 'Command', str(Path(executable).resolve()))
    child(action, 'Arguments', subprocess.list2cmdline(['--sync-jacs', '--data-dir', str(Path(data_dir).resolve())]))
    child(action, 'WorkingDirectory', str(Path(executable).resolve().parent))
    return ET.tostring(root, encoding='utf-16', xml_declaration=True)


def _query(data_dir):
    return subprocess.run(['schtasks.exe', '/Query', '/TN', task_name(data_dir), '/XML'],
                          capture_output=True, timeout=15)


def schedule_status(store):
    settings = store.get_metadata('jacs_schedule', {})
    result = {'supported':supported(), 'enabled':False, 'weekday':settings.get('weekday','Monday'),
              'time':settings.get('time','09:00')}
    if result['supported']:
        try:
            query = _query(store.directory)
            if query.returncode == 0:
                root = ET.fromstring(query.stdout)
                result['enabled'] = root.findtext('.//{' + NAMESPACE + '}Settings/{' + NAMESPACE + '}Enabled') == 'true'
        except (OSError, subprocess.TimeoutExpired, ET.ParseError):
            result['error'] = 'Unable to query the Windows weekly task.'
    return result


def configure_schedule(store, enabled, weekday='Monday', time='09:00'):
    if not supported():
        raise ValueError('Weekly scheduling is available in the packaged Windows app.')
    validate_schedule(weekday, time)
    name = task_name(store.directory)
    if not enabled:
        existing = _query(store.directory)
        if existing.returncode == 0:
            result = subprocess.run(['schtasks.exe','/Delete','/TN',name,'/F'],capture_output=True,timeout=30)
            if result.returncode:
                raise RuntimeError('Windows could not remove the weekly task.')
        store.set_metadata('jacs_schedule', {'enabled':False,'weekday':weekday,'time':time})
        return schedule_status(store)
    # Keep a stable executable location even if the downloaded ZIP is moved.
    directory = store.directory / 'collector'
    directory.mkdir(parents=True, exist_ok=True)
    executable = directory / 'Chembrain.exe'
    original = Path(sys.executable).resolve()
    if original != executable.resolve():
        temporary = executable.with_suffix('.exe.part')
        try:
            shutil.copyfile(original, temporary)
            temporary.replace(executable)
        finally:
            temporary.unlink(missing_ok=True)
    identity = subprocess.run(['whoami.exe','/user','/fo','csv','/nh'],capture_output=True,timeout=15,check=True)
    match = re.search(rb'S-1-\d+(?:-\d+)+', identity.stdout)
    if not match:
        raise RuntimeError('Unable to identify the current Windows user.')
    content = task_xml(executable, store.directory, weekday, time, match.group().decode('ascii'))
    fd, filename = tempfile.mkstemp(prefix='chembrain-jacs-task-', suffix='.xml')
    try:
        with os.fdopen(fd,'wb') as output:
            output.write(content)
        registration = subprocess.run(['schtasks.exe','/Create','/TN',name,'/XML',filename,'/F'],
                                      capture_output=True,timeout=30)
        if registration.returncode:
            raise RuntimeError('Windows could not register the current-user weekly task.')
    finally:
        Path(filename).unlink(missing_ok=True)
    store.set_metadata('jacs_schedule', {'enabled':True,'weekday':weekday,'time':time})
    status = schedule_status(store)
    if not status['enabled']:
        raise RuntimeError('The weekly task was not enabled after registration.')
    return status
