from pathlib import Path
root = Path(SPECPATH).parent
analysis = Analysis([str(root / 'workflowkit/entry.py')], pathex=[str(root)],
    datas=[(str(root / 'workflowkit/templates'),'workflowkit/templates')],
    hiddenimports=['workflowkit.cli','workflowkit.runner','workflowkit.policy','workflowkit.providers','workflowkit.github','workflowkit.credentials'],
    excludes=['pytest','rdkit','pymupdf','fastapi','numpy','PIL','tkinter','playwright'], noarchive=False)
pyz = PYZ(analysis.pure)
exe = EXE(pyz,analysis.scripts,analysis.binaries,analysis.datas,[],name='ChembrainWorkflow',console=True,upx=False)
