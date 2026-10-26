import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {createAtlasFetch} from './atlas-test-io.js';
import {createImmutableCohortRenderer} from './immutable-cohort-renderer.js';
const fixture=()=>{const db=JSON.parse(fs.readFileSync(new URL('./fixtures/multischool.json',import.meta.url)));return {db,roster:db.rosters,fixtureId:'synthetic-immutable-contract'};};
let coldSerial=0;
async function cold(input,hash){
 const nodes=new Map(),node=key=>{if(!nodes.has(key))nodes.set(key,{innerHTML:'',textContent:'',value:'',style:{},events:{},dataset:{height:'320'},clientWidth:960,addEventListener(t,f){this.events[t]=f},click(){this.onclick?.()}});return nodes.get(key)};
 Object.assign(globalThis,{document:{querySelector:node,querySelectorAll:()=>[],getElementById:id=>node('#'+id)},location:{href:'https://atlas.test/site/index.html',hash},window:{scrollTo(){},addEventListener(){}},fetch:createAtlasFetch(input.db,input.roster)});
 await import('../site/app.js?immutable-contract-cold='+coldSerial++);assert(!node('#main').innerHTML.includes('资料暂未加载'));
 return Object.fromEntries([...nodes].map(([key,value])=>[key,{innerHTML:value.innerHTML,textContent:value.textContent}]));
}
test('single actual router equals cold full snapshots across profile, lineage, cross-school and revisit',async()=>{
 const input=fixture(),f=createImmutableCohortRenderer(input),routes=['#/person/hit-synthetic-person','#/person/hit-synthetic-person/lineage','#/person/pku-synthetic-person','#/person/hit-synthetic-person'];let main;
 for(const route of routes){const rendered=await f.render(route);main??=f.mainIdentity();assert.equal(f.mainIdentity(),main);assert.deepEqual(rendered.snapshot,await cold(input,route));assert(f.nodeAudit().inactiveBlank);assert(Object.isFrozen(rendered.snapshot));}
 assert.equal(f.stats.imports,1);assert.equal(f.stats.handlerRegistrations,1);assert.equal(f.stats.handlerCalls,3);assert.equal(f.stats.renders,4);assert.equal(f.stats.fetches.length,4);assert.equal(new Set(f.stats.routes).size,3);
});
test('immutable renderer rejects nested fixture mutation and replacement, without sharing concurrent globals',async()=>{
 const input=fixture(),f=createImmutableCohortRenderer(input),other=createImmutableCohortRenderer({...input,fixtureId:'other'}),route='#/person/hit-synthetic-person';
 const pending=f.render(route);await assert.rejects(f.render(route),/concurrent/);await assert.rejects(other.render(route),/concurrent/);await pending;
 input.db.people[0].name+=' changed';await assert.rejects(f.render(route),/immutable fixture changed/);input.db.people[0].name=input.db.people[0].name.replace(' changed','');
 input.roster.entries[0].name+=' changed';await assert.rejects(f.render(route),/immutable fixture changed/);input.roster.entries[0].name=input.roster.entries[0].name.replace(' changed','');
 await assert.rejects(f.render(route,{db:{...input.db},roster:input.roster}),/immutable fixture changed/);
 const snap=await f.render(route);assert.throws(()=>{snap.snapshot['#main'].innerHTML='changed'},TypeError);assert.equal(f.stats.imports,1);
});
test('same-build different factory/data retains independent real app and DOM identities',async()=>{
 const input=fixture(),f=createImmutableCohortRenderer(input),route='#/person/hit-synthetic-person',first=await f.render(route);const other=fixture();other.db.people[0].name='Second distinct fixture';assert.equal(other.db.build_id,input.db.build_id);
 const g=createImmutableCohortRenderer(other),second=await g.render(route);assert.notEqual(f.identity,g.identity);assert.notEqual(f.mainIdentity(),g.mainIdentity());assert.notDeepEqual(first.snapshot,second.snapshot);assert(second('#main').innerHTML.includes('Second distinct fixture'));assert.deepEqual((await f.render(route)).snapshot,first.snapshot);
});
test('missing or duplicate real handler fails without fallback and failed state is sticky',async()=>{
 for(const listenerFault of ['missing','duplicate']){const f=createImmutableCohortRenderer({...fixture(),listenerFault});await assert.rejects(f.render('#/person/hit-synthetic-person'),/missing or duplicate/);await assert.rejects(f.render('#/person/hit-synthetic-person'),/renderer failed/);assert.equal(f.stats.imports,1);}
});
test('actual cold loader failure propagates without a successful snapshot or retry',async()=>{
 const f=createImmutableCohortRenderer({...fixture(),fetchFactory:()=>async()=>{throw Error('EXACT IMMUTABLE CONTRACT FETCH FAILURE')}});await assert.rejects(f.render('#/person/hit-synthetic-person'),/EXACT IMMUTABLE CONTRACT FETCH FAILURE/);await assert.rejects(f.render('#/person/hit-synthetic-person'),/renderer failed/);assert.equal(f.stats.imports,1);assert.equal(f.stats.renders,0);
});
