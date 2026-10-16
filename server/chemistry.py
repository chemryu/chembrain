from rdkit import Chem, RDLogger
from rdkit.Chem import Descriptors, rdMolDescriptors
from rdkit.Chem.Draw import rdMolDraw2D

RDLogger.DisableLog("rdApp.error")


def describe_molecule(smiles: str) -> dict:
    mol = Chem.MolFromSmiles(smiles)
    if mol is None or not mol.GetNumAtoms():
        raise ValueError("유효한 SMILES를 입력하세요.")
    canonical = Chem.MolToSmiles(mol, isomericSmiles=True)
    key = Chem.MolToInchiKey(mol)
    if not key:
        raise ValueError("이 구조의 InChIKey를 생성할 수 없습니다.")
    return {
        "smiles": canonical,
        "inchikey": key,
        "formula": rdMolDescriptors.CalcMolFormula(mol),
        "molecular_weight": round(Descriptors.MolWt(mol), 2),
    }


def molecule_svg(smiles: str) -> str:
    mol = Chem.MolFromSmiles(smiles)
    drawer = rdMolDraw2D.MolDraw2DSVG(300, 170)
    options = drawer.drawOptions()
    options.setBackgroundColour((0.95, 0.96, 0.93))
    drawer.DrawMolecule(mol)
    drawer.FinishDrawing()
    return drawer.GetDrawingText()
