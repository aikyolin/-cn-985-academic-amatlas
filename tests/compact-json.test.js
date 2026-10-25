import {test} from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import crypto from 'node:crypto';
const read=p=>fs.readFileSync(new URL('../'+p,import.meta.url));
const canonical=JSON.parse(read('data/atlas.json').toString('utf8'));
const site=JSON.parse(read('site/atlas.json').toString('utf8'));
const roster=JSON.parse(read('site/rosters.json').toString('utf8'));
function sameOrder(actual,expected){
 if(Array.isArray(actual)){assert(Array.isArray(expected));assert.equal(actual.length,expected.length);actual.forEach((value,index)=>sameOrder(value,expected[index]));}
 else if(actual!==null&&typeof actual==='object'){assert.deepEqual(Object.keys(actual),Object.keys(expected));for(const key of Object.keys(actual))sameOrder(actual[key],expected[key]);}
 else assert(Object.is(actual,expected));
}
test('native client JSON parsing preserves every canonical field and key or array order',()=>{
 assert.deepEqual(Object.keys(site),[...Object.keys(canonical),'build_id','exports']);
 for(const key of Object.keys(canonical)){assert.deepStrictEqual(site[key],canonical[key]);sameOrder(site[key],canonical[key]);}
 assert.equal(site.people.length,canonical.people.length);assert.equal(site.pending_people.length,canonical.pending_people.length);
});
test('actual compact UTF-8 atlases have valid byte roundtrips and only one LF outside strings',()=>{
 for(const path of ['data/atlas.json','site/atlas.json']){
  const raw=read(path),text=raw.toString('utf8');assert.deepEqual(Buffer.from(text,'utf8'),raw);assert(!text.startsWith('\uFEFF'));assert.equal(text.match(/\n/g)?.length,1);assert(text.endsWith('\n'));assert(text.startsWith('{'));JSON.parse(text);
 }
});
test('new build identifier is independently derived from unchanged rule and shared with rosters',()=>{
 const inputs=['data/atlas.json','data/rosters.json','scripts/build.py','scripts/build_rosters.py','scripts/deterministic_xlsx.py'];
 const expected=crypto.createHash('sha256').update(Buffer.concat(inputs.map(read))).digest('hex').slice(0,16);
 assert.equal(site.build_id,expected);assert.equal(roster.build_id,expected);
});
