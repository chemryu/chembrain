import json
from pathlib import Path

import pytest

from workflowkit import cli
from workflowkit.runner import controller_lock


@pytest.mark.parametrize('name', ['workspace', 'changes', 'reviews', 'runs', 'deliverables',
                                  'agents', 'requests', '_controller'])
def test_initialization_refuses_redirected_owned_folders(tmp_path, name):
    root = tmp_path / 'Box'
    root.mkdir()
    outside = tmp_path / 'outside'
    outside.mkdir()
    (root / name).symlink_to(outside, target_is_directory=True)
    with pytest.raises(ValueError, match='symlinks or junctions'):
        cli.initialize(root)
    assert not list(outside.iterdir())


def test_initialization_refuses_symlink_parent_and_template_file(tmp_path):
    outside = tmp_path / 'outside'
    outside.mkdir()
    linked = tmp_path / 'linked'
    linked.symlink_to(outside, target_is_directory=True)
    with pytest.raises(ValueError, match='symlinks or junctions'):
        cli.initialize(linked / 'project')
    assert not list(outside.iterdir())
    root = tmp_path / 'Box'
    root.mkdir()
    victim = outside / 'victim'
    victim.write_text('keep')
    (root / 'wiki.md').symlink_to(victim)
    with pytest.raises(ValueError, match='symlinks or junctions'):
        cli.initialize(root)
    assert victim.read_text() == 'keep'


def test_install_frozen_controller_and_launchers_without_powershell(tmp_path, monkeypatch):
    executable = tmp_path / 'download' / 'ChembrainWorkflow.exe'
    executable.parent.mkdir()
    executable.write_bytes(b'test frozen executable')
    monkeypatch.setattr(cli.sys, 'frozen', True, raising=False)
    monkeypatch.setattr(cli.sys, 'executable', str(executable))
    root = tmp_path / 'Box folder with spaces'
    cli.install(root)
    assert (root / '_controller/ChembrainWorkflow.exe').read_bytes() == executable.read_bytes()
    for name, command in [('Start-Workflow.cmd', 'menu'), ('Watch-Workflow.cmd', 'watch')]:
        text = (root / name).read_text()
        assert 'powershell' not in text.casefold()
        assert f'{command} --root "%~dp0."' in text
    (root / 'wiki.md').write_text('User notes')
    cli.install(root)
    assert (root / 'wiki.md').read_text() == 'User notes'
    monkeypatch.setattr(cli.sys, 'executable', str(root / '_controller/ChembrainWorkflow.exe'))
    cli.install(root)  # Running the installed executable must not copy over itself.


def test_unfrozen_install_does_not_create_files(tmp_path):
    root = tmp_path / 'Box'
    with pytest.raises(ValueError, match='packaged'):
        cli.install(root)
    assert not root.exists()


def test_install_refuses_redirected_launcher(tmp_path, monkeypatch):
    monkeypatch.setattr(cli.sys, 'frozen', True, raising=False)
    root = cli.initialize(tmp_path / 'Box')
    outside = tmp_path / 'outside'
    outside.write_text('keep')
    (root / 'Start-Workflow.cmd').symlink_to(outside)
    with pytest.raises(ValueError):
        cli.install(root)
    assert outside.read_text() == 'keep'


def test_watcher_owns_lifetime_lock_independent_of_run_lock(tmp_path, monkeypatch):
    monkeypatch.setenv('LOCALAPPDATA', str(tmp_path / 'Local'))
    root = cli.initialize(tmp_path / 'Box')
    config_path = root / 'config.json'
    config = json.loads(config_path.read_text())
    config.update(author_model='author', reviewer_model='reviewer')
    config_path.write_text(json.dumps(config))
    monkeypatch.setattr(cli.credentials, 'load', lambda: {})
    visited = []

    def watcher_body(selected):
        assert selected == root
        # A second watcher is rejected even while the first watcher is idle.
        with pytest.raises(RuntimeError):
            with controller_lock(root, purpose='watch'):
                pass
        # The watcher can run work under the separate execution lock.
        with controller_lock(root):
            visited.append(True)

    monkeypatch.setattr(cli, '_watch_locked', watcher_body)
    cli.watch(root)
    assert visited == [True]
