import fs from 'node:fs';
import assert from 'node:assert/strict';
import {test} from 'node:test';
const read=p=>fs.readFileSync(new URL('../site/'+p,import.meta.url),'utf8');
test('changed application and static module dependencies share one release version',()=>{
 const html=read('index.html'),versions=[...html.matchAll(/(?:app\.js|styles\.css)\?v=([^"']+)/g)].map(m=>m[1]);
 for(const name of ['app.js','rosters.js'])for(const m of read(name).matchAll(/from '\.\/(?:model|rosters|universities|atlas-loader)\.js\?v=([^']+)'/g))versions.push(m[1]);
 assert.equal(versions.length,7);assert.equal(new Set(versions).size,1);assert.equal(versions[0],'school-chunks-20261026');
});
test('JSON loading bypasses browser cache and rejects inconsistent snapshot versions',()=>{
 const app=read('app.js');assert(app.includes("await loadAtlas()"));assert(read('atlas-loader.js').includes("readBytes(fetchImpl,url,'no-store',LIMITS.manifestBytes"));assert(app.includes("fetch(versionedPath('rosters.json',db.build_id),{cache:'no-store'})"));assert(app.includes('if(!sameBuild(db,db.rosters))throw Error'));
});
