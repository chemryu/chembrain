"""Initialize the user's Box Drive folder and run bounded API agents."""
import argparse
import getpass
import hashlib
import json
import os
import platform
import shutil
import sys
import time
from pathlib import Path

from . import credentials
from .policy import atomic_json, atomic_text
from .runner import Workflow, config_for, controller_lock
from .providers import AIProviders
from .github import GitHub

DEFAULT_ROOT = r'C:\Users\Ren Lab\Box\AIWorkflow\ChemBrainProject'
INACTIVE = '<!-- WORKFLOW_REQUEST_INACTIVE -->'


def reject_link_components(path):
    """Reject symlinks and Windows junctions before any controller-owned write."""
    path = Path(path).absolute()
    for component in (*reversed(path.parents), path):
        junction = getattr(component, 'is_junction', lambda: False)
        if component.is_symlink() or junction():
            raise ValueError(f'Workflow paths must not contain symlinks or junctions: {component.name}')


def initialize(root):
    root = Path(root)
    reject_link_components(root)
    for directory in ('workspace','changes','reviews','runs','deliverables','agents',
                      'requests','_controller'):
        reject_link_components(root / directory)
    root.mkdir(parents=True, exist_ok=True)
    templates = Path(__file__).parent / 'templates'
    for source in templates.rglob('*'):
        if not source.is_file():
            continue
        relative = source.relative_to(templates)
        destination = root / relative
        if source.name == 'config.example.json':
            destination = root / 'config.json'
        reject_link_components(destination)
        if not destination.resolve().is_relative_to(root.resolve()):
            raise ValueError('Initialization path escapes the selected folder.')
        if destination.is_symlink():
            raise ValueError('Refusing to initialize over a symlink.')
        if not destination.exists():
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, destination)
    for directory in ('workspace','changes','reviews','runs','deliverables'):
        (root / directory).mkdir(exist_ok=True)
    config_path = root / 'config.json'
    config = json.loads(config_path.read_text(encoding='utf-8-sig'))
    if not config.get('owner_host'):
        config['owner_host'] = platform.node()
        atomic_json(config_path, config)
    return root


def configure(root):
    root = initialize(root)
    config = json.loads((root / 'config.json').read_text(encoding='utf-8-sig'))
    print('API agents use separate OpenAI/Anthropic billing. Keys stay outside Box, encrypted for this Windows user.')
    for key, label in [('author_model','OpenAI API model name'),('reviewer_model','Anthropic API model name')]:
        value = input(f'{label} [{config.get(key, "")}]: ').strip() or config.get(key, '')
        if not value:
            raise ValueError('Both model names must be configured explicitly.')
        config[key] = value
    values = {name:getpass.getpass(label).strip() for name,label in [
        ('openai_key','OpenAI API key (hidden): '),('anthropic_key','Anthropic API key (hidden): '),
        ('github_token','GitHub fine-grained token for chemryu/chembrain (hidden): ')]}
    if credentials.credentials_path().resolve().is_relative_to(root.resolve()):
        raise ValueError('Credential storage must be outside the shared workflow folder.')
    credentials.save(values)
    atomic_json(root / 'config.json', config)
    print('Credential settings saved outside Box. Role permissions are enforced by the controller; OS ACLs were not changed.')


def install(root):
    """Install the frozen controller and CMD launchers without PowerShell scripts."""
    if not getattr(sys, 'frozen', False):
        raise ValueError('Install requires the packaged ChembrainWorkflow.exe.')
    root = initialize(root)
    target = root / '_controller' / 'ChembrainWorkflow.exe'
    launchers = {root / 'Start-Workflow.cmd': 'menu', root / 'Watch-Workflow.cmd': 'watch'}
    for path in (target, *launchers):
        reject_link_components(path)
    target.parent.mkdir(exist_ok=True)
    source = Path(sys.executable)
    if source.resolve() != target.resolve():
        temporary = target.with_suffix('.exe.part')
        reject_link_components(temporary)
        try:
            shutil.copyfile(source, temporary)
            temporary.replace(target)
        finally:
            temporary.unlink(missing_ok=True)
    for path, command in launchers.items():
        atomic_text(path, '@echo off\r\n"%~dp0_controller\\ChembrainWorkflow.exe" '
                    + command + ' --root "%~dp0."\r\npause\r\n')
    print(f'Created rulebook, wiki, agent files and launchers in: {root}')
    print('Open Start-Workflow.cmd to configure credentials. No paid API calls were made. OS ACLs were not changed.')
    return root


def run_once(root, request_text=None):
    root = initialize(root)
    config = config_for(root)
    request = request_text if request_text is not None else (root / 'requests/current.md').read_text(encoding='utf-8-sig')
    if not request.strip() or INACTIVE in request:
        raise ValueError('Edit requests/current.md and remove the inactive marker before starting a paid API run.')
    if len(request.encode('utf-8')) > 100_000:
        raise ValueError('The request exceeds 100 KB.')
    keys = credentials.load()
    with controller_lock(root):
        github = GitHub(keys['github_token'], config['repository'], config['branch'])
        providers = AIProviders(keys['openai_key'], keys['anthropic_key'], config['author_model'], config['reviewer_model'])
        state = Workflow(root, github, providers, config, secrets=keys.values()).run(request)
    print(f"Status: {state['status']}\nWiki: {root / 'wiki.md'}")
    return state


def watch(root):
    root = initialize(root)
    config_for(root)
    credentials.load()
    # A watcher owns its entire lifetime, separately from each individual run.
    # This prevents two idle launchers from later spending on the same request.
    with controller_lock(root, purpose='watch'):
        return _watch_locked(root)


def _watch_locked(root):
    seen = None
    last = root / 'runs/last-request.json'
    if last.exists():
        seen = json.loads(last.read_text(encoding='utf-8'))['sha256']
    print('Watching requests/current.md. Keep this controller running; Ctrl+C stops it.')
    while True:
        request = (root / 'requests/current.md').read_text(encoding='utf-8-sig')
        digest = hashlib.sha256(request.encode('utf-8')).hexdigest()
        if request.strip() and INACTIVE not in request and digest != seen:
            state = run_once(root, request)
            # Failed and blocked tasks do not silently spend another paid run.
            seen = digest
            atomic_json(last, {'sha256':digest,'run_id':state['run_id'],'status':state['status']})
        time.sleep(5)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['init','install','configure','run','watch','status','menu'], nargs='?', default='menu')
    parser.add_argument('--root', type=Path, default=Path(DEFAULT_ROOT) if os.name == 'nt' else None)
    args = parser.parse_args(argv)
    if args.root is None:
        parser.error('Pass --root outside Windows; the configured Box Drive path is on the Windows PC.')
    root = args.root.absolute()
    if args.command == 'init':
        initialize(root); print(f'Created rulebook, wiki and role files in {root}. Nothing is running yet.')
    elif args.command == 'install':
        install(root)
    elif args.command == 'configure':
        configure(root)
    elif args.command == 'run':
        return 0 if run_once(root)['status'] == 'READY' else 2
    elif args.command == 'watch':
        watch(root)
    elif args.command == 'status':
        path = root / 'state.json'
        print(path.read_text(encoding='utf-8') if path.exists() else 'Not started. Configure credentials and an active request first.')
    else:
        initialize(root)
        print(f'Chembrain workflow controller\nRoot: {root}\n1. Configure API credentials\n2. Run current request\n3. Watch for new requests\n4. Status\n0. Exit')
        choice = input('Select: ').strip()
        commands = {'1':'configure','2':'run','3':'watch','4':'status'}
        if choice in commands:
            return main([commands[choice],'--root',str(root)])
    return 0


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        print('Controller stopped.')
    except Exception as error:
        # Provider/gateway errors are sanitized; no environment dump or credential values.
        print(f'Workflow stopped: {error}', file=sys.stderr)
        raise SystemExit(1)
