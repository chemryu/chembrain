"""Regression coverage for the zero-argument, double-click entry point."""
import sys

from scripts import desktop


def test_no_arguments_starts_normal_mode_with_browser_enabled(tmp_path, monkeypatch):
    monkeypatch.setattr(sys, 'argv', ['Chembrain.exe'])
    monkeypatch.setattr(desktop, 'default_data_dir', lambda: tmp_path / 'Local App Data' / 'Chembrain')
    for name in ('CHEMBRAIN_DATA_DIR', 'CHEMBRAIN_SEED_DEMO', 'CHEMBRAIN_SEED_LITERATURE'):
        monkeypatch.setenv(name, '')
    calls = []
    monkeypatch.setattr(desktop, 'serve', lambda data_dir, no_browser, smoke_test: calls.append((data_dir, no_browser, smoke_test)))
    desktop.main()
    assert calls == [(tmp_path / 'Local App Data' / 'Chembrain', False, False)]
    # The normal entry point also releases the log before the folder can be removed on Windows.
    (calls[0][0] / 'chembrain.log').unlink()
