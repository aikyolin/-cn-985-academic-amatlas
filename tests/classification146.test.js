import {test} from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {readJSONFile} from './atlas-test-io.js';
import {createImmutableCohortRenderer} from './immutable-cohort-renderer.js';
import {degreeType,stages,matchEducation} from '../site/model.js';
const raw=readFileSync(new URL('./fixtures/classification146-exact-project-registry.json',import.meta.url));assert.equal(createHash('sha256').update(raw).digest('hex'),'859d2d07b7ac22fc9420ac6754cd733e9d1d067579c1f6a4256e13a666a963dc');
const fixed=JSON.parse(raw),db=readJSONFile(new URL('../site/atlas.json',import.meta.url)),roster=readJSONFile(new URL('../site/rosters.json',import.meta.url));
const renderer=createImmutableCohortRenderer({db,roster,fixtureId:'EXACT146_PROJECT_REGISTRY_NO_NEW_SOURCE_RESEARCH'});
const ids=[...new Set(fixed.operations.map(o=>o.person_id))];
test('146 exact events use existing project registry, never geographic or award inference',()=>{
 assert.equal(fixed.operations.length,146);assert.equal(ids.length,72);
 for(const o of fixed.operations){const p=db.people[o.person_index],e=p.education[o.education_index];assert.equal(p.person_id,o.person_id);assert.equal(e.event_id,o.event_id);assert.equal(e.institution,o.registry_official_name);assert.equal(db.institutions.find(i=>i.id===o.registry_id).official_name,e.institution);assert.equal(e.institution_985,'yes');
  const type=degreeType(e.degree);if(e.event_kind==='degree'&&e.degree_awarded===true&&['bachelor','master','doctor'].includes(type)&&stages(p,type).includes(e))assert(matchEducation(p,type,'institution_985','yes'));
 }
});
test('original institution-name difference stays unknown',()=>{const x=fixed.excluded[0];assert.equal(x.person_id,'tongji-wanglei-oncology');const e=db.people.find(p=>p.person_id===x.person_id).education.find(e=>e.event_id===x.event_id);assert.equal(e.institution_985,'unknown');});
test('yes institution classification never promotes false/null awards into degree filters',()=>{for(const o of fixed.operations){const p=structuredClone(db.people[o.person_index]);p.education=p.education.filter(e=>e.event_id===o.event_id);p.education[0].degree='博士';for(const award of [false,null]){p.education[0].degree_awarded=award;assert.equal(stages(p,'doctor').length,0);}}});
const esc=s=>String(s).replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;').replaceAll('"','&quot;').replaceAll("'",'&#39;');
for(const id of ids)test('real profile and lineage preserve original facts after classification: '+id,async()=>{
 const p=db.people.find(p=>p.person_id===id);
 for(const suffix of ['', '/lineage']){const result=await renderer.render('#/person/'+id+suffix);const markup=Object.values(result.snapshot).map(v=>v.innerHTML).join('\n');assert(markup.includes(esc(p.name)));
  if(!suffix){for(const e of p.education){if(e.note)assert(markup.includes(esc(e.note)));if(e.institution)assert(markup.includes(esc(e.institution)));}for(const v of p.unknowns||[])assert(markup.includes(esc(v)));}
  else for(const m of p.mentors||[]){assert(markup.includes(esc(m.name)));if(m.description)assert(markup.includes(esc(m.description)));}
 }
});
