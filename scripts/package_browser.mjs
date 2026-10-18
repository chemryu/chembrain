/** Package the portable Vite build as one offline, UTF-8-safe HTML file. */
import { createHash } from 'node:crypto';
import { execFileSync } from 'node:child_process';
import { mkdir, readFile, readdir, writeFile } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const sha256 = value => createHash('sha256').update(value).digest('hex');
const assert = (condition, message) => { if (!condition) throw new Error(message); };

function attribute(tag, name) {
  const found = tag.match(new RegExp(`\\b${name}\\s*=\\s*(["'])(.*?)\\1`, 'i'));
  return found?.[2];
}

function localAsset(buildDir, reference) {
  assert(reference && !/[?#]/.test(reference), 'Portable assets must be plain local file references.');
  assert(!/^(?:[a-z][a-z\d+.-]*:|\/\/|\/)/i.test(reference), 'Portable assets must be relative to index.html.');
  const absolute = path.resolve(buildDir, reference);
  assert(absolute.startsWith(path.resolve(buildDir) + path.sep), 'Asset escapes portable build directory.');
  return absolute;
}

/** Data never enters HTML raw-text context: decode into textContent after parsing. */
export function inlinePortableHtml(html, javascript, styles) {
  const scripts = [...html.matchAll(/<script\b[^>]*>[\s\S]*?<\/script\s*>/gi)];
  assert(scripts.length === 1, 'Expected exactly one Vite entry script.');
  const entry = scripts[0][0];
  assert(attribute(entry, 'type') === 'module' && attribute(entry, 'src'), 'Expected one external module entry.');
  assert(!/\bimport\s*\(/.test(javascript), 'Unexpected dynamic import in portable entry.');
  assert(!/(?:^|[;\n])\s*(?:import\s*(?:["'{*]|[A-Za-z_$][\w$]*\s*(?:,|from\b))|export\s+[^;]*\sfrom\s*["'])/m.test(javascript), 'Unexpected module dependency in portable entry.');
  for (const css of styles) {
    assert(!/@import\b/i.test(css), 'CSS imports are not supported in a single HTML package.');
    for (const match of css.matchAll(/url\(\s*(["']?)(.*?)\1\s*\)/gi)) {
      assert(/^(?:data:|#)/i.test(match[2]), 'Unexpected external CSS asset in portable build.');
    }
  }
  const links = [...html.matchAll(/<link\b[^>]*>/gi)];
  let packaged = html;
  for (const [tag] of links) {
    const rel = attribute(tag, 'rel');
    if (rel === 'stylesheet') packaged = packaged.replace(tag, '');
    else assert(rel === 'icon' && attribute(tag, 'href')?.startsWith('data:'), 'Unexpected linked asset in portable HTML.');
  }
  assert(!/<(?:img|iframe|video|audio|source|object|embed)\b/i.test(packaged), 'Unexpected HTML resource in portable shell.');
  const css64 = Buffer.from(styles.join('\n'), 'utf8').toString('base64');
  const js64 = Buffer.from(javascript, 'utf8').toString('base64');
  const bootstrap = `<script type="module" data-chembrain-inline="base64-utf8">\n` +
    `const decode=(value)=>new TextDecoder().decode(Uint8Array.from(atob(value),x=>x.charCodeAt(0)));\n` +
    `const style=document.createElement('style');style.textContent=decode('${css64}');document.head.append(style);\n` +
    `const app=document.createElement('script');app.type='module';app.textContent=decode('${js64}');document.body.append(app);\n` +
    `</script>`;
  packaged = packaged.replace(entry, () => bootstrap);
  assert(!/<script\b[^>]*\bsrc\s*=/i.test(packaged), 'An external script remains in package.');
  return packaged;
}

export async function packageBrowser({ buildDir = path.join(root, 'dist-portable'), outputDir = path.join(root, 'release'), sourceCommit } = {}) {
  const html = await readFile(path.join(buildDir, 'index.html'), 'utf8');
  const entries = [...html.matchAll(/<script\b[^>]*>[\s\S]*?<\/script\s*>/gi)];
  assert(entries.length === 1, 'Expected exactly one Vite entry script.');
  const scriptFile = localAsset(buildDir, attribute(entries[0][0], 'src'));
  const styles = [...html.matchAll(/<link\b[^>]*>/gi)].map(([tag]) => tag).filter(tag => attribute(tag, 'rel') === 'stylesheet');
  const cssFiles = styles.map(tag => localAsset(buildDir, attribute(tag, 'href')));
  const allowed = new Set([scriptFile, ...cssFiles]);
  const assetDir = path.join(buildDir, 'assets');
  for (const asset of await readdir(assetDir, { withFileTypes: true })) {
    assert(asset.isFile() && allowed.has(path.join(assetDir, asset.name)), `Unexpected portable build asset: ${asset.name}`);
  }
  const javascript = await readFile(scriptFile, 'utf8');
  const css = await Promise.all(cssFiles.map(file => readFile(file, 'utf8')));
  const notice = await readFile(path.join(root, 'packaging', 'RDKit-LICENSE.txt'), 'utf8');
  const packaged = inlinePortableHtml(html, javascript, css) + '\n<!-- Bundled RDKit MinimalLib 2026.9.1\n' + notice.replaceAll('--', '—') + '\n-->\n';
  const commit = sourceCommit || process.env.CHEMBRAIN_SOURCE_SHA || execFileSync('git', ['rev-parse', 'HEAD'], { cwd: root, encoding: 'utf8' }).trim();
  assert(/^[a-f\d]{40}$/i.test(commit), 'Portable source commit must be a full Git SHA.');
  const version = JSON.parse(await readFile(path.join(root, 'package.json'), 'utf8')).version;
  const library = await readFile(path.join(root, 'public', 'library.json'));
  const output = Buffer.from(packaged, 'utf8');
  const provenance = {
    schema_version: 1,
    source_commit: commit,
    app_version: version,
    preview: true,
    format: 'single-html-base64-utf8-module',
    file: 'Chembrain.html',
    bytes: output.length,
    sha256: sha256(output),
    library_sha256: sha256(library),
    javascript_sha256: sha256(Buffer.from(javascript, 'utf8')),
    structure_renderer: {package:'@rdkit/rdkit',version:JSON.parse(await readFile(path.join(root,'node_modules/@rdkit/rdkit/package.json'),'utf8')).version,wasm_sha256:sha256(await readFile(path.join(root,'node_modules/@rdkit/rdkit/dist/RDKit_minimal.wasm')))},
    styles_sha256: css.map(text => sha256(Buffer.from(text, 'utf8'))),
  };
  await mkdir(outputDir, { recursive: true });
  await writeFile(path.join(outputDir, 'Chembrain.html'), output);
  await writeFile(path.join(outputDir, 'browser-manifest.json'), JSON.stringify(provenance, null, 2) + '\n');
  const instructions = await readFile(path.join(root, 'packaging', 'README-Browser.txt'));
  await writeFile(path.join(outputDir, 'README-Browser.txt'), instructions);
  const checksums = [];
  for (const name of ['Chembrain.html', 'README-Browser.txt', 'browser-manifest.json']) checksums.push(`${sha256(await readFile(path.join(outputDir, name)))}  ${name}`);
  await writeFile(path.join(outputDir, 'SHA256SUMS.txt'), checksums.join('\n') + '\n');
  return provenance;
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  const result = await packageBrowser();
  process.stdout.write(`PORTABLE_PACKAGE_PASS ${result.file} ${result.bytes} bytes sha256=${result.sha256} source=${result.source_commit}\n`);
}
