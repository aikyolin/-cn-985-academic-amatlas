import {test} from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {hitAtlas,hitRosters} from './school-scope.js';
const read=path=>JSON.parse(fs.readFileSync(new URL(path,import.meta.url)));
test('historical HIT views keep exact counts and ignore foreign same-name records without mutating data',()=>{
 const atlas=read('../site/atlas.json'),rosters=read('../site/rosters.json'),aBefore=JSON.stringify(atlas),rBefore=JSON.stringify(rosters);
 const hit=hitAtlas(atlas),ro=hitRosters(rosters),mixed=structuredClone(atlas),mixedRoster=structuredClone(rosters);
 for(const key of ['people','pending_people','org_units','campuses']){const row=structuredClone(hit[key][0]);row.school_id='testscope';mixed[key].unshift(row)}
 for(const key of ['entries','coverage','summary']){const row=structuredClone(ro[key][0]);row.school_id='testscope';mixedRoster[key].unshift(row)}
 assert.deepEqual(hitAtlas(mixed),hit);assert.deepEqual(hitRosters(mixedRoster),ro);
 assert.equal(hit.people.length,257);assert.equal(hit.pending_people.length,42);assert.equal(ro.entries.length,1381);
 assert.equal(JSON.stringify(atlas),aBefore);assert.equal(JSON.stringify(rosters),rBefore);
});
