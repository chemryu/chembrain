"""Curated reaction facts and reference molecular structures; not automatic OCSR."""
import json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
from paper_pipeline.schema import validate
from server.chemistry import describe_molecule,molecule_svg

from rdkit import Chem, rdBase

ROOT = Path(__file__).resolve().parents[1]


def load_verified_structures(path=ROOT / 'examples/verified-structures.json'):
    """Check the checked-in reference representation before making its diagrams.

    Source-observed names/IDs/SMILES and locally computed checks remain distinct.
    This does not fetch a registry or infer paper-specific intermediate structures.
    """
    package = json.loads(Path(path).read_text())
    if package.get('schema_version') != 1:
        raise ValueError('Unsupported verified structure package.')
    if package['computed_with']['version'] != rdBase.rdkitVersion:
        raise ValueError('Reference checks require the recorded RDKit version.')
    structures = package['structures']
    if len(structures) != 2 or {item['id'] for item in structures} != {'paclitaxel', 'doxycycline'}:
        raise ValueError('Only the two explicitly verified parent structures are accepted.')
    for item in structures:
        mol = Chem.MolFromSmiles(item['source_smiles'])
        if mol is None:
            raise ValueError('Invalid reference SMILES: ' + item['id'])
        described = describe_molecule(item['source_smiles'])
        checks = {
            'canonical_isomeric_smiles': described['smiles'],
            'formula': described['formula'],
            'inchikey': described['inchikey'],
            'molecular_weight': described['molecular_weight'],
            'assigned_stereocenters': sum(label != '?' for _, label in Chem.FindMolChiralCenters(mol, includeUnassigned=True)),
            'unassigned_stereocenters': sum(label == '?' for _, label in Chem.FindMolChiralCenters(mol, includeUnassigned=True)),
            'formal_charge': Chem.GetFormalCharge(mol),
            'fragments': len(Chem.GetMolFrags(mol)),
        }
        if any(item.get(key) != value for key, value in checks.items()):
            raise ValueError('Reference structure checks do not match: ' + item['id'])
        if checks['unassigned_stereocenters'] or checks['formal_charge'] != 0 or checks['fragments'] != 1:
            raise ValueError('Reference must be a fully assigned neutral parent: ' + item['id'])
    return {item['id']: item for item in structures}


def main():
    verified = load_verified_structures()
    D={'schema_version':1,'papers':[],'chemicals':[],'solutions':[],'reactions':[]}
    def paper(id,doi,authors):
     D['papers'].append(dict(id=id,doi=doi,authors=authors.split(';')))
    def chem(id,name,kind='compound',smiles=None,aliases=None,formula=None):
     c=dict(id=id,name=name,kind=kind,smiles=smiles,aliases=aliases or [],notes='' if smiles else 'Structure not encoded; compound label is local to the cited paper.')
     if formula:c['formula']=formula
     if smiles:
      c.update(describe_molecule(smiles));p=Path('public/structures');p.mkdir(parents=True,exist_ok=True);(p/(id+'.svg')).write_text(molecule_svg(smiles))
      if id in verified:
       reference=verified[id];c['notes']='Reference parent structure: '+reference['source_id']+' in the official RDKit tutorials ChEMBL snapshot. '+reference['representation']
     D['chemicals'].append(c);return id
    paper('holton','10.1021/ja00083a067','Robert A. Holton;Hyeong-Baik Kim;Carmen Somoza;Feng Liang;Ronald J. Biediger;P. Douglas Boatman;Mitsuru Shindo;Chase C. Smith;Soekchan Kim;Hossain Nadizadeh;Yukio Suzuki;Chunlin Tao;Phong Vu;Suhan Tang;Pingsheng Zhang;Krishna K. Murthi;Lisa N. Gentile;Jyanwei H. Liu')
    paper('charest','10.1126/science.1109755','Mark G. Charest;Christian D. Lerner;Jason D. Brubaker;Dionicio R. Siegel;Andrew G. Myers')
    paper('baran','10.1021/jacs.0c03592','Yuzuru Kanda;Hugh Nakamura;Shigenobu Umemiya;Ravi Kumar Puthukanoori;Venkata Ramana Murthy Appala;Gopi Krishna Gaddamanugu;Bheema Rao Paraselli;Phil S. Baran')
    chem('paclitaxel','Paclitaxel (Taxol)',aliases=['Taxol','(-)-Taxol'],smiles=verified['paclitaxel']['canonical_isomeric_smiles'])
    chem('doxycycline','Doxycycline',aliases=['(-)-Doxycycline'],smiles=verified['doxycycline']['canonical_isomeric_smiles'])
    chem('benzoic-acid','Benzoic acid',smiles='O=C(O)c1ccccc1')
    for prefix,labels in [('holton',['5','6','17','18','20b','20c','21','24b','25']),('baran',['19','20','21','22','34','35']),('charest',['5','13','14','15','16','20','21'])]:
     for label in labels:chem(prefix+'-'+label,prefix.title()+' compound '+label)
    for id,name,smiles in [('thf','Tetrahydrofuran','C1CCOC1'),('dcm','Dichloromethane','ClCCl'),('toluene','Toluene','Cc1ccccc1'),('ethanol','Ethanol','CCO'),('acetonitrile','Acetonitrile','CC#N'),('methanol','Methanol','CO'),('pyridine','Pyridine','c1ccncc1')]:chem(id,name,'solvent',smiles)
    for id,name,kind in [('lda','Lithium diisopropylamide','reagent'),('hoac','Acetic acid','reagent'),('memgbr','Methylmagnesium bromide','reagent'),('dbu','DBU','reagent'),('lhmds','Lithium hexamethyldisilazide','reagent'),('hf','Hydrogen fluoride','reagent'),('hydrogen','Hydrogen','reagent'),('pdc','Palladium on carbon','catalyst'),('pd','Palladium (support unspecified)','catalyst'),('nahmds','Sodium hexamethyldisilazide','reagent'),('tbscl','tert-Butyldimethylsilyl chloride','reagent'),('dmdo','Dimethyldioxirane','reagent'),('tpap','Tetrapropylammonium perruthenate','catalyst'),('nmo','N-Methylmorpholine N-oxide','reagent'),('liotf','Lithium triflate','catalyst'),('tfa','Trifluoroacetic acid','reagent'),('tmeda','TMEDA','reagent')]:chem(id,name,kind)
    def step(solvents,solutes,temp=None,time=None,note=''):
     id='solution-'+str(len(D['solutions'])+1)
     D['solutions'].append(dict(id=id,solvents=solvents,solutes=[dict(chemical_id=c,role=('reactant' if next(x['kind'] for x in D['chemicals'] if x['id']==c)=='compound' else next(x['kind'] for x in D['chemicals'] if x['id']==c)),amount=None,unit=None) for c in solutes],concentration=None,concentration_unit=None))
     return dict(solution_id=id,temperature=temp,time=time,notes=note)
    def rx(id,paper,reactants,products,name,y,steps,page,locator,target,notes=''):
     for i,s in enumerate(steps):
      old=s['solution_id'];new='solution-'+id+'-'+str(i+1);next(x for x in D['solutions'] if x['id']==old)['id']=new;s['solution_id']=new
     D['reactions'].append(dict(id=id,name=name,reactants=reactants,products=products,targets=[target],yield_percent=y,yield_basis='Reported isolated yield for the stated operation; see notes for sequences.',steps=steps,status='draft',evidence=[dict(paper_id=paper,page=page,locator=locator)],notes=notes+' Draft curation from main article; check SI and structures before experimental use.'))
    rx('h-dieckmann','holton',['holton-5'],['holton-6'],'Dieckmann C-ring closure',93,[step(['thf'],['holton-5','lda'],'-78 °C','0.5 h'),step(['thf'],['hoac'])],1,'Printed p.1599, conversion 5 → 6','paclitaxel','93% yield at 90% conversion, as reported; do not multiply conversion and yield as separate steps.')
    rx('h-methyl','holton',['holton-17'],['holton-18'],'Methylmagnesium addition',95,[step(['dcm'],['holton-17','memgbr'],'-45 °C','15 h','MeMgBr: 10 molar equivalents')],2,'Printed p.1600, conversion 17 → 18','paclitaxel')
    rx('h-oxetane','holton',['holton-20b'],['holton-21'],'Oxetane ring closure',None,[step(['toluene'],['holton-20b','dbu'],'105 °C','2 h')],2,'Printed p.1600, 20b or 20c → 21','paclitaxel','Reported range 80–85%; alternate precursor 20c also reported. No invented midpoint yield.')
    rx('h-taxol','holton',['holton-24b','holton-25'],['paclitaxel'],'Taxol side-chain coupling and deprotection sequence',93,[step(['thf'],['holton-24b','holton-25','lhmds'],'0 °C','1 h'),step(['acetonitrile','pyridine'],['hf'],'0 °C','1 h'),step(['ethanol'],['hydrogen','pdc'],'reflux','1 h')],2,'Printed p.1600, final paragraph: 24b + β-lactam 25 → Taxol','paclitaxel','93% overall from 24b over the stated sequence, not a single-step yield.')
    rx('b-silyl','baran',['baran-19'],['baran-20'],'Enol-silane formation',94,[step(['thf'],['baran-19','nahmds','tbscl'],'0 °C to room temperature')],3,'Scheme 1, step f: 19 → 20','paclitaxel')
    rx('b-dmdo','baran',['baran-20'],['baran-21'],'DMDO oxidation',49,[step([],['baran-20','dmdo'],'0 °C',note='Solvent not specified in Scheme 1 caption; not inferred from optimization table.')],3,'Scheme 1, step g: 20 → 21','paclitaxel')
    rx('b-tpap','baran',['baran-21'],['baran-22'],'TPAP oxidation',81,[step(['dcm'],['baran-21','tpap','nmo'],'room temperature')],3,'Scheme 1, step h: 21 → 22','paclitaxel')
    rx('b-taxol','baran',['baran-34','baran-35'],['paclitaxel'],'Taxol coupling and hydrogenolysis sequence',85,[step(['thf'],['baran-34','baran-35','lhmds'],'-78 °C to room temperature'),step(['ethanol'],['hydrogen','pdc'],'80 °C')],3,'Scheme 1, step s: 34 + β-lactam 35 → Taxol (1)','paclitaxel','85% over the coupling/deprotection sequence shown; durations absent from caption.')
    rx('c-addition','charest',['charest-13','charest-14'],['charest-15'],'AB-fragment organolithium addition',73,[step(['thf'],['charest-13','charest-14'],'-78 °C')],2,'Figure 2: 13 + 14 → 15','doxycycline')
    rx('c-ab','charest',['charest-15'],['charest-16'],'AB-ring rearrangement and desilylation',62,[step(['toluene'],['charest-15','liotf'],'60 °C',note='LiOTf 5 mol % in article text'),step(['dcm'],['tfa'])],2,'Figure 2: 15 → 16','doxycycline','62% for the two-operation sequence.')
    rx('c-coupling','charest',['charest-5','charest-20'],['charest-21'],'Michael–Dieckmann C-ring construction',79,[step(['thf'],['charest-5','charest-20','lda','tmeda'],'-78 °C to 0 °C')],2,'Scheme 1: enone 5 + D-ring precursor 20 → 21; explanation on PDF p.3','doxycycline')
    rx('c-doxy','charest',['charest-21'],['doxycycline'],'Doxycycline deprotection sequence',90,[step(['acetonitrile'],['charest-21','hf']),step(['thf','methanol'],['hydrogen','pd'])],2,'Scheme 1: 21 → (-)-doxycycline; PDF p.3 identifies hydrochloride isolate','doxycycline','90% over two steps; product isolated as hydrochloride. Parent molecule indexed, salt form preserved in this note. Time/temperature not inferred.')
    validate(D)
    p=Path('public/library.json');p.write_text(json.dumps(D,separators=(',',':'),ensure_ascii=False))
    Path('examples/total-synthesis.json').write_text(json.dumps(D,indent=2,ensure_ascii=False)+'\n')
    print('Library',len(D['chemicals']),'chemicals,',len(D['reactions']),'draft reactions,',p.stat().st_size,'bytes; no PDF text or figures')


if __name__ == '__main__':
    main()
