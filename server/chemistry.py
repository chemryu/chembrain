from rdkit import Chem, RDLogger
from rdkit.Chem import Descriptors, rdMolDescriptors
from rdkit.Chem.Draw import rdMolDraw2D

RDLogger.DisableLog("rdApp.error")


def describe_molecule(smiles: str) -> dict:
    mol = Chem.MolFromSmiles(smiles)
    if mol is None or not mol.GetNumAtoms():
        raise ValueError("Enter a valid SMILES string.")
    canonical = Chem.MolToSmiles(mol, isomericSmiles=True)
    key = Chem.MolToInchiKey(mol)
    if not key:
        raise ValueError("Unable to generate an InChIKey for this structure.")
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
