const symbols=('? H He Li Be B C N O F Ne Na Mg Al Si P S Cl Ar K Ca Sc Ti V Cr Mn Fe Co Ni Cu Zn Ga Ge As Se Br Kr Rb Sr Y Zr Nb Mo Tc Ru Rh Pd Ag Cd In Sn Sb Te I Xe Cs Ba La Ce Pr Nd Pm Sm Eu Gd Tb Dy Ho Er Tm Yb Lu Hf Ta W Re Os Ir Pt Au Hg Tl Pb Bi Po At Rn Fr Ra Ac Th Pa U Np Pu Am Cm Bk Cf Es Fm Md No Lr Rf Db Sg Bh Hs Mt Ds Rg Cn Nh Fl Mc Lv Ts Og').split(' ');
/** Hill formula from RDKit's explicit graph and implicit H counts (isotopes aggregated). */
export function molecularFormula(json:string):string {
 const graph=JSON.parse(json),defaults=graph.defaults?.atom||{},counts=new Map<string,number>();let charge=0;
 if(!Array.isArray(graph.molecules)||graph.molecules.length!==1)throw new Error('Unsupported molecular graph.');
 const add=(symbol:string,n:number)=>counts.set(symbol,(counts.get(symbol)||0)+n);
 for(const atom of graph.molecules[0].atoms){
  const z=atom.z??defaults.z,h=atom.impHs??defaults.impHs??0;
  if(!Number.isInteger(z)||z<1||!symbols[z]||!Number.isInteger(h)||h<0)throw new Error('Unresolved atoms cannot be exported as a known structure.');
  add(symbols[z],1);if(h)add('H',h);charge+=atom.chg??defaults.chg??0;
 }
 const order=[...counts.keys()].sort();
 // RDKit's CalcMolFormula orders C, then H, then other elements, including
 // hydrogen first for carbon-free compounds such as HCl and H4Al-.
 if(counts.has('C'))order.splice(order.indexOf('C'),1);
 if(counts.has('H'))order.splice(order.indexOf('H'),1);
 order.unshift(...(counts.has('C')?['C']:[]),...(counts.has('H')?['H']:[]));
 return order.map(s=>s+(counts.get(s)!>1?counts.get(s):'')).join('')+(charge?(charge>0?'+':'-')+(Math.abs(charge)>1?Math.abs(charge):''):'');
}
