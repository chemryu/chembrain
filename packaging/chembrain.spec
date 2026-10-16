# Build on the target OS: python -m PyInstaller packaging/chembrain.spec --noconfirm
from pathlib import Path
from PyInstaller.utils.hooks import collect_all, collect_submodules

root = Path(SPECPATH).parent
rdkit_data, rdkit_bins, rdkit_hidden = collect_all('rdkit')
pymupdf_data, pymupdf_bins, pymupdf_hidden = collect_all('pymupdf')
a = Analysis(
    [str(root / 'scripts/desktop.py')], pathex=[str(root)],
    binaries=rdkit_bins + pymupdf_bins,
    datas=rdkit_data + pymupdf_data + [(str(root / 'dist'), 'dist'), (str(root / 'examples'), 'examples')],
    hiddenimports=rdkit_hidden + pymupdf_hidden + collect_submodules('uvicorn') + ['server.app'],
    excludes=['pytest', 'IPython', 'tkinter', 'matplotlib', 'pandas', 'notebook'],
    noarchive=False,
)
pyz = PYZ(a.pure)
exe = EXE(pyz, a.scripts, a.binaries, a.datas, [], name='Chembrain',
          debug=False, bootloader_ignore_signals=False, strip=False, upx=False, console=True)
