import { useEffect, useRef, useState } from 'react';
import { CanvasEditor, Molecule } from 'openchemlib';
import { inspectStructure } from './structureRenderer';
import './paper-sketcher.css';

export type PaperStructureSketcherProps = {
 smiles: string;
 onUseSmiles: (smiles: string) => void;
};

const MAX_FILE_BYTES = 200 * 1024;
const MAX_SMILES_LENGTH = 3000;
const MAX_ATOMS = 1000;

/** Only export complete graphs: a paper's R label is not a resolved chemical. */
function drawnSmiles(molecule: Molecule): string {
 if (!molecule.getAllAtoms()) throw new Error('Draw a structure before using it.');
 if (molecule.getAllAtoms() > MAX_ATOMS) throw new Error('The drawing exceeds the 1000-atom limit.');
 if (molecule.isFragment()) throw new Error('Expand R groups, wildcards and query atoms into a specific chemical before using this drawing.');
 for (let atom = 0; atom < molecule.getAllAtoms(); atom++) {
  const atomicNo = molecule.getAtomicNo(atom);
  if (atomicNo < 1 || atomicNo > 118 || molecule.getAtomCustomLabel(atom)
   || molecule.getAtomList(atom)?.length
   || Object.values(molecule.getAtomQueryFeaturesObject(atom)).some(Boolean)) {
   throw new Error('Expand every abbreviated label, R group and query atom into actual atoms before using this drawing.');
  }
 }
 for (let bond = 0; bond < molecule.getAllBonds(); bond++) {
  if (molecule.getBondQueryFeatures(bond)) throw new Error('Replace query bonds with specific bonds before using this drawing.');
 }
 molecule.validate();
 const smiles = molecule.toIsomericSmiles();
 if (!smiles || smiles.length > MAX_SMILES_LENGTH) throw new Error('The drawn structure must fit within 3000 SMILES characters.');
 // Includes stereo, isotopes, charges and all disconnected salt components.
 // Refuse unsupported features (for example enhanced relative stereo) instead
 // of silently turning them into a different absolute molecular identity.
 if (Molecule.fromSmiles(smiles).getIDCode() !== molecule.getIDCode()) {
  const relativeAtoms = Array.from({ length: molecule.getAllAtoms() }, (_, atom) => molecule.getAtomESRType(atom)).some(type => type !== Molecule.cESRTypeAbs);
  const relativeBonds = Array.from({ length: molecule.getAllBonds() }, (_, bond) => molecule.getBondESRType(bond)).some(type => type !== Molecule.cESRTypeAbs);
  if (relativeAtoms || relativeBonds) throw new Error('This drawing uses relative or racemic stereochemistry, which plain SMILES cannot preserve. A MOL file without an absolute chiral flag can cause this. Check the source: load a correctly declared absolute stereoisomer only if the paper supports it; otherwise keep the chemical unresolved. The SMILES field has not changed.');
  throw new Error('This drawing contains features that cannot be preserved in SMILES. Check its stereochemistry and labels before transferring it.');
 }
 return smiles;
}

/** A single MOL/SDF record only; do not quietly discard later SDF molecules. */
function readSingleMolfile(text: string): Molecule {
 const records = text.replace(/\r\n?/g, '\n').split(/^\$\$\$\$[ \t]*$/m).filter(record => record.trim());
 if (records.length !== 1 || (records[0].match(/^M  END[ \t]*$/gm)?.length ?? 0) !== 1) {
  throw new Error('Load a MOL file or an SDF containing exactly one molecule. Split multi-record files before loading.');
 }
 if (!/V(?:2000|3000)/.test(records[0])) throw new Error('This file is not a supported V2000 or V3000 MOL/SDF record.');
 const molecule = Molecule.fromMolfile(records[0]);
 if (!molecule.getAllAtoms()) throw new Error('The file does not contain a molecule.');
 if (molecule.getAllAtoms() > MAX_ATOMS) throw new Error('The file exceeds the 1000-atom limit.');
 return molecule;
}

export default function PaperStructureSketcher({ smiles, onUseSmiles }: PaperStructureSketcherProps) {
 const host = useRef<HTMLDivElement>(null);
 const editor = useRef<CanvasEditor | null>(null);
 const initialSmiles = useRef(smiles);
 const pending = useRef(0);
 const [ready, setReady] = useState(false);
 const [busy, setBusy] = useState(false);
 const [notice, setNotice] = useState('');
 const [error, setError] = useState(false);

 useEffect(() => {
  if (!host.current) return;
  let instance: CanvasEditor | undefined;
  try {
   instance = new CanvasEditor(host.current, { initialMode: 'molecule', initialFragment: false });
   editor.current = instance;
   if (initialSmiles.current.trim()) {
    try {
     if (initialSmiles.current.length > MAX_SMILES_LENGTH) throw new Error();
     instance.setMolecule(Molecule.fromSmiles(initialSmiles.current));
    } catch {
     setError(true);
     setNotice('The current SMILES could not be loaded. The SMILES field has not changed. Draw a structure or load a MOL/SDF file.');
    }
   }
   setReady(true);
  } catch {
   setError(true);
   setNotice('The drawing editor could not start. You can still enter a verified SMILES directly.');
  }
  return () => {
   pending.current++;
   editor.current = null;
   if (instance && !instance.isDestroyed) {
    instance.removeOnChangeListener();
    instance.destroy();
   }
  };
 }, []);

 function report(message: string, failed = false) {
  setNotice(message);
  setError(failed);
 }

 function loadCurrentSmiles() {
  try {
   if (!editor.current) throw new Error('The drawing editor is not available.');
   if (!smiles.trim() || smiles.length > MAX_SMILES_LENGTH) throw new Error('Enter a valid SMILES of at most 3000 characters first.');
   const molecule = Molecule.fromSmiles(smiles);
   if (!molecule.getAllAtoms()) throw new Error('The current SMILES does not contain a molecule.');
   editor.current.setMolecule(molecule);
   report('Loaded the current SMILES into the drawing. Check it against the paper before using it.');
  } catch (caught) {
   report(caught instanceof Error ? caught.message : 'The current SMILES could not be loaded.', true);
  }
 }

 async function loadFile(file: File) {
  const request = ++pending.current;
  setBusy(true);
  try {
   if (file.size > MAX_FILE_BYTES) throw new Error('MOL/SDF files must be 200 KB or smaller.');
   const molecule = readSingleMolfile(await file.text());
   if (request !== pending.current || !editor.current) return;
   editor.current.setMolecule(molecule);
   report('Loaded one MOL/SDF molecule into the drawing. The SMILES field has not changed. Check the drawing, then use it.');
  } catch (caught) {
   if (request === pending.current && editor.current) report(caught instanceof Error ? caught.message : 'The file could not be loaded.', true);
  } finally {
   if (request === pending.current && editor.current) setBusy(false);
  }
 }

 async function useDrawing() {
  if (!editor.current) return;
  const request = ++pending.current;
  setBusy(true);
  try {
   const current = editor.current.getMolecule();
   const nextSmiles = drawnSmiles(current);
   const identity = current.getIDCode();
   // Drawing is an encoding aid, not source verification. RDKit independently
   // checks that the transferred graph has a computable chemical identity.
   await inspectStructure(nextSmiles);
   if (request !== pending.current || !editor.current) return;
   if (editor.current.getMolecule().getIDCode() !== identity) throw new Error('The drawing changed during validation. Check it and choose Use drawn structure again.');
   onUseSmiles(nextSmiles);
   report('Copied the drawn structure to the SMILES field. This does not confirm agreement with the paper; check the atoms, stereochemistry and salt form.');
  } catch (caught) {
   if (request === pending.current && editor.current) report(caught instanceof Error ? caught.message : 'This drawing could not be transferred.', true);
  } finally {
   if (request === pending.current && editor.current) setBusy(false);
  }
 }

 return <section className="paper-sketcher" aria-label="Paper structure sketcher">
  <h3>Draw the paper structure</h3>
  <p>Copy the structure manually while checking the private PDF. This editor does not read images or verify the paper. Check every atom, bond, stereocenter, isotope, charge and salt component.</p>
  <div className="paper-sketcher-canvas" ref={host} aria-label="Molecule drawing area" />
  <div className="paper-sketcher-actions">
   <button type="button" disabled={!ready || busy} onClick={loadCurrentSmiles}>Load current SMILES</button>
   <label className="paper-sketcher-file">Load MOL/SDF
    <input type="file" accept=".mol,.sdf,chemical/x-mdl-molfile,chemical/x-mdl-sdfile" aria-label="Load MOL/SDF" disabled={!ready || busy} onChange={event => {
     const file = event.currentTarget.files?.[0];
     event.currentTarget.value = '';
     if (file) void loadFile(file);
    }} />
   </label>
   <button type="button" disabled={!ready || busy} onClick={() => void useDrawing()}>{busy ? 'Checking drawing…' : 'Use drawn structure'}</button>
  </div>
  <p className="paper-sketcher-help">The SMILES field changes only when you choose Use drawn structure. Loading a file replaces this drawing only. Single-record MOL/SDF files up to 200 KB are supported; files stay in this browser.</p>
  {notice && <p className={'paper-sketcher-notice' + (error ? ' paper-sketcher-error' : '')} aria-live="polite">{notice}</p>}
 </section>;
}
