import {test} from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {spawnSync} from 'node:child_process';

const site=new URL('../site/',import.meta.url);
const origin=new URL('https://academic-atlas.invalid/');
const previousRelease='rotation-20261023-w3';
const moduleNames=['app.js','model.js','rosters.js','universities.js'];
const read=name=>fs.readFileSync(new URL(name,site),'utf8');

function attributes(tag){
 const attrs={};
 for(const match of tag.matchAll(/([^\s=<>/]+)\s*=\s*(?:"([^"]*)"|'([^']*)'|([^\s>]+))/g))attrs[match[1].toLowerCase()]=match[2]??match[3]??match[4];
 return attrs;
}
function entrypoints(){
 const html=read('index.html').replace(/<!--[\s\S]*?-->/g,'');
 const scripts=[...html.matchAll(/<script\b[^>]*>/gi)].map(m=>attributes(m[0]));
 const links=[...html.matchAll(/<link\b[^>]*>/gi)].map(m=>attributes(m[0]));
 const app=scripts.filter(a=>a.type==='module'&&a.src&&new URL(a.src,origin).pathname==='/app.js');
 const styles=links.filter(a=>a.rel?.split(/\s+/).includes('stylesheet')&&a.href&&new URL(a.href,origin).pathname==='/styles.css');
 assert.equal(app.length,1,'HTML must load exactly one app.js module');
 assert.equal(styles.length,1,'HTML must load exactly one styles.css stylesheet');
 return [new URL(app[0].src,origin),new URL(styles[0].href,origin)];
}
function localFile(url){
 assert.equal(url.origin,origin.origin,`${url.href} must be a local asset`);
 const file=new URL('.'+url.pathname,site);
 assert(file.href.startsWith(site.href),`${url.href} must stay inside site/`);
 assert(fs.statSync(file).isFile(),`${url.href} must resolve to an existing file`);
 return file;
}
function releaseToken(url){
 const versions=url.searchParams.getAll('v');
 assert.equal(versions.length,1,`${url.href} must have exactly one v query parameter`);
 assert(versions[0].trim(),`${url.href} must have a nonempty release token`);
 assert.equal(versions[0],versions[0].trim(),'Release tokens must not have surrounding whitespace');
 return versions[0];
}

// Let Node parse static imports and re-exports, including multiline declarations
// and side-effect imports, instead of relying on quote-sensitive source regexes.
// Parsing never links or evaluates these browser modules and makes no requests.
function moduleImports(){
 const sources=Object.fromEntries(moduleNames.map(name=>[name,read(name)]));
 const parsed=spawnSync(process.execPath,['--experimental-vm-modules','--input-type=module','-e',`
  import fs from 'node:fs';
  import {SourceTextModule} from 'node:vm';
  const sources=JSON.parse(fs.readFileSync(0,'utf8'));
  const imports=Object.fromEntries(Object.entries(sources).map(([name,source])=>[
   name,new SourceTextModule(source,{identifier:name}).dependencySpecifiers
  ]));
  process.stdout.write(JSON.stringify(imports));
 `],{input:JSON.stringify(sources),encoding:'utf8',timeout:10000});
 assert.ifError(parsed.error);
 assert.equal(parsed.status,0,`Module parsing failed: ${parsed.stderr}`);
 return JSON.parse(parsed.stdout);
}
function localImports(){
 return Object.entries(moduleImports()).flatMap(([from,specifiers])=>specifiers
  .filter(specifier=>/^(?:\.{1,2}\/|\/(?!\/))/.test(specifier))
  .map(specifier=>({from,specifier,url:new URL(specifier,new URL(from,origin))})));
}

test('HTML app and stylesheet assets exist and share a nonempty current release token',()=>{
 const [app,styles]=entrypoints();
 localFile(app);localFile(styles);
 assert.equal(releaseToken(app),releaseToken(styles));
});

test('every local module dependency exists and uses the HTML current release token',()=>{
 const [app]=entrypoints(),current=releaseToken(app),imports=localImports();
 assert(imports.length>0,'The application import graph must not be empty');
 for(const {from,specifier,url} of imports){
  localFile(url);
  assert.equal(releaseToken(url),current,`${from} imports ${specifier} from a different release`);
 }
});

test('HTML and module asset references never reuse the stale pre-retirement release tag',()=>{
 const references=[...entrypoints(),...localImports().map(edge=>edge.url)];
 for(const url of references){
  assert(!decodeURIComponent(url.href).includes(previousRelease),`Stale asset reference: ${url.href}`);
 }
});

test('the versioned import graph retains the application and roster dependency edges',()=>{
 const edges=new Set(localImports().map(({from,url})=>`${from}->${url.pathname.slice(1)}`));
 for(const edge of ['app.js->universities.js','app.js->rosters.js','app.js->model.js','rosters.js->model.js']){
  assert(edges.has(edge),`Missing required import edge: ${edge}`);
 }
});

test('the current HTML-selected app contains the explicit retired or emeritus non-active label',()=>{
 const [app]=entrypoints(),source=fs.readFileSync(localFile(app),'utf8');
 assert.match(source,/retired_or_emeritus_officially_listed\s*:\s*(['"])官方离退休／荣休名录（非在职）\1/);
});
