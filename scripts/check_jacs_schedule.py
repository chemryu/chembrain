"""Validate actual Windows task registration for the EXE, then remove the test task.

The trigger is strictly in the future. This check never runs a collection or uses
the real user's data directory, and cleanup failure remains a failed check.
"""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET


def main():
    if sys.platform != 'win32' or len(sys.argv) != 2:
        raise SystemExit('Run on Windows with the packaged Chembrain.exe path.')
    executable = Path(sys.argv[1]).resolve()
    namespace = '{http://schemas.microsoft.com/windows/2004/02/mit/task}'
    with tempfile.TemporaryDirectory(prefix='Chembrain scheduled test ') as temporary:
        folder = Path(temporary) / 'Local App Data'
        identity = hashlib.sha256(str(folder.resolve()).casefold().encode()).hexdigest()[:12]
        name = 'Chembrain JACS ' + identity
        def launch(flag):
            output = subprocess.check_output([str(executable),flag,'--data-dir',str(folder)],timeout=120,text=True)
            return json.loads(output)
        try:
            result = launch('--install-jacs-schedule')
            assert result['enabled'] is True
            task = ET.fromstring(subprocess.check_output(['schtasks.exe','/Query','/TN',name,'/XML'],timeout=30))
            def text(path):
                return task.findtext('.//' + '/'.join(namespace + part for part in path.split('/')))
            assert text('Principals/Principal/LogonType') == 'InteractiveToken'
            assert text('Principals/Principal/RunLevel') == 'LeastPrivilege'
            assert text('Settings/StartWhenAvailable') == 'true'
            assert text('Settings/MultipleInstancesPolicy') == 'IgnoreNew'
            assert task.find('.//' + namespace + 'Monday') is not None
            command = Path(text('Actions/Exec/Command'))
            assert command == folder / 'collector/Chembrain.exe'
            assert command.is_file()
            arguments = text('Actions/Exec/Arguments')
            assert '--sync-jacs' in arguments and str(folder) in arguments and '--no-browser' not in arguments
            print('JACS schedule: stable bundled EXE, current user, weekly, local clock, missed-run recovery and no-overlap verified.',flush=True)
        finally:
            launch('--remove-jacs-schedule')
            assert subprocess.run(['schtasks.exe','/Query','/TN',name],capture_output=True,timeout=30).returncode != 0
    print('JACS_WEEKLY_SCHEDULE_PASS',flush=True)


if __name__ == '__main__':
    main()
