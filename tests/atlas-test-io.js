// Test IO only: business assertions consume the production validated transport.
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {createHash} from 'node:crypto';
import {validateManifest,assembleAtlas,parseStrictJSON,LIMITS} from '../site/atlas-loader.js';
const sha=bytes=>createHash('sha256').update(bytes).digest('hex');
const parse=bytes=>parseStrictJSON(new TextDecoder('utf-8',{fatal:true,ignoreBOM:true}).decode(bytes));
export function readAtlasFile(file){
 const filename=file instanceof URL?fileURLToPath(file):file;
 if(fs.lstatSync(filename).isSymbolicLink())throw Error('symlink manifest');
 if(fs.realpathSync(filename)!==path.resolve(filename))throw Error('symlink storage ancestry');
 const rawManifest=fs.readFileSync(filename);if(rawManifest.length>LIMITS.manifestBytes)throw Error('manifest too large');
 const manifest=parse(rawManifest);validateManifest(manifest);
 if(rawManifest.length+manifest.parts.reduce((n,p)=>n+p.bytes,0)>LIMITS.totalBytes)throw Error('storage too large');
 const base=path.dirname(filename),directory=path.join(base,'people');
 if(fs.lstatSync(directory).isSymbolicLink())throw Error('symlink people directory');
 const expected=new Set(manifest.parts.map(p=>path.basename(p.path)));
 if(fs.readdirSync(directory).some(name=>!expected.has(name)))throw Error('orphan chunk');
 const parts=manifest.parts.map(part=>{
  const filename=path.join(base,part.path);
  if(fs.lstatSync(filename).isSymbolicLink())throw Error('symlink chunk');
  const raw=fs.readFileSync(filename);
  if(raw.length!==part.bytes||sha(raw)!==part.sha256)throw Error('chunk bytes/hash mismatch');
  return parse(raw);
 });
 return assembleAtlas(manifest,parts);
}
export function readJSONFile(file){
 const filename=file instanceof URL?fileURLToPath(file):file;
 return path.basename(filename)==='atlas.json'?readAtlasFile(file):JSON.parse(fs.readFileSync(file,'utf8'));
}
// Encode projected/mutated fixtures, not a bypass: the real browser loader still
// fetches raw manifest/chunk bytes, hashes and validates every response.
export function createAtlasFetch(db,rosters){
 const groups=new Map();for(const person of db.people){if(!groups.has(person.school_id))groups.set(person.school_id,[]);groups.get(person.school_id).push(person);}
 const encode=value=>Buffer.from(JSON.stringify(value)+'\n');
 const files=new Map(),parts=[];
 for(const [school_id,people]of groups){const pathname=`people/${school_id}.json`,bytes=encode({school_id,people});files.set(pathname,bytes);parts.push({school_id,path:pathname,sha256:sha(bytes),bytes:bytes.length,count:people.length});}
 files.set('atlas.json',encode({format:'academic-atlas-school-parts-v1',atlas:{...db,people:[]},people_order:db.people.map(p=>p.person_id),parts}));
 files.set('rosters.json',encode(rosters));
 return async request=>{
  const url=new URL(String(request),'https://atlas.test/site/index.html');
  if(url.origin!=='https://atlas.test'||!url.pathname.startsWith('/site/'))throw Error('External fetch prohibited');
  const key=url.pathname.slice('/site/'.length),bytes=files.get(key);
  if(!bytes)throw Error(`Unexpected fixture fetch: ${request}`);
  return new Response(bytes,{status:200,headers:{'Content-Type':'application/json'}});
 };
}
