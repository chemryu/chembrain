/** Bundle a separate private workbench, never a selected paper or user workspace. */
import {readFile,readdir,mkdir,writeFile} from 'node:fs/promises';
import {execFileSync} from 'node:child_process';
import {createHash} from 'node:crypto';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {inlinePortableHtml} from './package_browser.mjs';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const hash=x=>createHash('sha256').update(x).digest('hex');
const assert=(test,message)=>{if(!test)throw new Error(message);};
const build=path.join(root,'dist-paper'),out=path.join(root,'release');
const html=await readFile(path.join(build,'paper.html'),'utf8');
const script=[...html.matchAll(/<script\b[^>]*src="([^"]+)"[^>]*>/g)];
const styles=[...html.matchAll(/<link\b[^>]*rel="stylesheet"[^>]*href="([^"]+)"[^>]*>/g)];
assert(script.length===1,'Expected exactly one Paper Workbench entry.');
function asset(ref){assert(!/^(?:[a-z]+:|\/|\.\.\/)/i.test(ref),'Unexpected nonlocal workbench asset.');const file=path.resolve(build,ref);assert(file.startsWith(build+path.sep),'Asset escapes build.');return file;}
const jsfile=asset(script[0][1]),cssfiles=styles.map(m=>asset(m[1]));
const allowed=new Set([jsfile,...cssfiles]);
for(const file of await readdir(path.join(build,'assets'),{withFileTypes:true}))assert(file.isFile()&&allowed.has(path.join(build,'assets',file.name)),'Unexpected external workbench chunk: '+file.name);
const js=await readFile(jsfile,'utf8'),css=await Promise.all(cssfiles.map(p=>readFile(p,'utf8')));
const notices=await readFile(path.join(root,'packaging/Paper-Third-Party-Notices.txt'),'utf8');
const output=Buffer.from(inlinePortableHtml(html,js,css)+'\n<!-- Bundled workbench dependencies\n'+notices.replaceAll('--','—')+'\n-->\n');
const source=process.env.CHEMBRAIN_SOURCE_SHA||execFileSync('git',['rev-parse','HEAD'],{cwd:root,encoding:'utf8'}).trim();assert(/^[a-f0-9]{40}$/.test(source),'Record a full source SHA.');
const engines={};for(const p of ['@rdkit/rdkit','pdfjs-dist','openchemlib']){const meta=JSON.parse(await readFile(path.join(root,'node_modules',p,'package.json'),'utf8'));engines[p]=meta.version;}
const manifest={schema_version:1,source_commit:source,preview:true,format:'single-html-base64-utf8-module',file:'Chembrain-Paper-Workbench.html',bytes:output.length,sha256:hash(output),javascript_sha256:hash(Buffer.from(js)),styles_sha256:css.map(x=>hash(Buffer.from(x))),engines,rdkit_wasm_sha256:hash(await readFile(path.join(root,'node_modules/@rdkit/rdkit/dist/RDKit_minimal.wasm'))),pdf_worker_sha256:hash(await readFile(path.join(root,'node_modules/pdfjs-dist/build/pdf.worker.min.mjs'))),private_source_documents_included:false};
await mkdir(out,{recursive:true});await writeFile(path.join(out,manifest.file),output);await writeFile(path.join(out,'paper-manifest.json'),JSON.stringify(manifest,null,2)+'\n');await writeFile(path.join(out,'README-Paper-Workbench.txt'),await readFile(path.join(root,'packaging/README-Paper-Workbench.txt')));
const sums=[];for(const file of [manifest.file,'README-Paper-Workbench.txt','paper-manifest.json'])sums.push(hash(await readFile(path.join(out,file)))+'  '+file);await writeFile(path.join(out,'SHA256SUMS-Paper.txt'),sums.join('\n')+'\n');
process.stdout.write('PAPER_PACKAGE_PASS '+manifest.bytes+' bytes sha256='+manifest.sha256+' source='+source+'\n');
