// Targeted NEW_RECOVERY tests. No generator, historical archive, or workbook I/O.
import {test} from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {readJSONFile} from './atlas-test-io.js';
import {createImmutableCohortRenderer} from './immutable-cohort-renderer.js';
import {stages,mentorEvents,mentorProfileRoute,mentorOfficialUrl} from '../site/model.js';
function fixed(name,sha){const raw=readFileSync(new URL('./fixtures/'+name,import.meta.url));assert.equal(createHash('sha256').update(raw).digest('hex'),sha);return JSON.parse(raw);}
const fixture=fixed('new-recovery123-source-attributed-mapping.json','5fb669036912a9b00c601865b322d8359c6a5c2a62957249c1fafbe6829f10e5');
const pins=fixed('new-recovery123-public-conservation-pins.json','991d893162b8a4c7b61be1411082eb14b989507c6a1b0b5b35ac465434f24be5');
const db=readJSONFile(new URL('../site/atlas.json',import.meta.url)),roster=readJSONFile(new URL('../site/rosters.json',import.meta.url));
const renderer=createImmutableCohortRenderer({db,roster,fixtureId:'NEW_RECOVERY_123_FIXED_SOURCE_ATTRIBUTED_V8'});
const esc=s=>String(s).replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;').replaceAll('"','&quot;').replaceAll("'",'&#39;');
const html=p=>Object.values(p.snapshot).map(v=>v.innerHTML).join('\n');
const actual=id=>{const rows=db.people.filter(p=>p.person_id===id);assert.equal(rows.length,1,id);return rows[0];};
function visible(markup,value,label){if(typeof value==='string'&&value)assert(markup.includes(esc(value)),label);}
test('fixed exact 123 people, 53 new orgs and 24 school batch identities follow old prefix',()=>{
 assert.equal(db.people.slice(0,1149).length,1149);assert.equal(fixture.people.length,123);
 assert.deepEqual(db.people.slice(1026,1149),fixture.people);
 assert.deepEqual(db.org_units.slice(pins.old_org_units_count),fixture.org_units);
 assert.deepEqual(db.profile_batches.slice(199,223).map(b=>({batch_id:b.batch_id,school_id:b.school_id,people_count:b.people_count})),fixture.profile_batches);
 assert.equal(new Set(fixture.people.map(p=>p.school_id)).size,24);
 assert.equal(new Set(fixture.people.map(p=>p.department_id)).size,98);
});
test('fixed education tristates and all original date own-properties/types remain exact',()=>{
 let yes=0,no=0,unknown=0,education=0;
 for(const expected of fixture.people){const p=actual(expected.person_id);
  for(const table of ['education','appointments','mentors','publications','teaching'])for(const [i,row]of(expected[table]||[]).entries()){
   const got=p[table][i];const keys=new Set([...Object.keys(row),...Object.keys(got)].filter(k=>/(date|year|month|start|end|period)/i.test(k)));
   for(const k of keys){assert.equal(Object.hasOwn(got,k),Object.hasOwn(row,k),expected.person_id+'/'+table+'/'+i+'/'+k);assert.deepEqual(got[k],row[k]);}
  }
  for(const e of p.education){education++;if(e.degree_awarded===true)yes++;else if(e.degree_awarded===false)no++;else{assert.equal(e.degree_awarded,null);unknown++;}}
 }
 assert.deepEqual([education,yes,no,unknown],[428,99,117,212]);
});
test('23 explicit source slots are filled with their fixed source literal, not inferred dates',()=>{
 assert.equal(pins.exact_source_slots.length,23);
 for(const q of pins.exact_source_slots){const row=actual(q.person_id)[q.table][q.index];assert(Object.hasOwn(row,q.key));assert.equal(row[q.key],q.value);assert.notEqual(row[q.key],null);}
});
test('unknown and false events never enter source-awarded degree filters',()=>{
 for(const p of fixture.people)for(const type of ['bachelor','master','doctor'])for(const e of stages(p,type)){assert.equal(e.degree_awarded,true);assert.equal(e.event_kind,'degree');}
 const p=structuredClone(fixture.people.find(p=>p.education.some(e=>e.degree_awarded===false)));
 const e=p.education.find(e=>e.degree_awarded===false);e.degree='博士';e.event_kind='degree';
 assert(!stages(p,'doctor').includes(e));e.degree_awarded=null;assert(!stages(p,'doctor').includes(e));
});
test('all 132 source mentor identities stay non-navigable; occupational guidance is not verified degree guidance',()=>{
 assert.equal(fixture.people.reduce((n,p)=>n+p.mentors.length,0),132);
 for(const p of fixture.people){assert.deepEqual(p.professional_research_advisors||[],[]);for(const m of p.mentors){assert.equal(mentorProfileRoute(m,db.people),'');assert.equal(mentorOfficialUrl(m),'');}}
 const p=actual('xjtu-she-gang');assert(p.unknowns.some(v=>v.includes('杜晓军')));assert(!p.mentors.some(m=>m.name==='杜晓军'));
 assert.deepEqual(mentorEvents(p,{education_stage:null,education_event_id:null}),[]);
});
test('fixture comparison rejects lost date properties, altered tri-state and promoted mentor identity',()=>{
 const p=fixture.people.find(p=>p.education.some(e=>Object.hasOwn(e,'start')));const changed=structuredClone(p);delete changed.education.find(e=>Object.hasOwn(e,'start')).start;assert.throws(()=>assert.deepEqual(changed,p));
 const q=fixture.people.find(p=>p.education.some(e=>e.degree_awarded===null));const changed2=structuredClone(q);changed2.education.find(e=>e.degree_awarded===null).degree_awarded=false;assert.throws(()=>assert.deepEqual(changed2,q));
 const r=fixture.people.find(p=>p.mentors.length);const changed3=structuredClone(r);changed3.mentors[0].person_id='invented-person';assert.throws(()=>assert.deepEqual(changed3,r));
});
for(const p of fixture.people)test('real profile and lineage retain source facts: '+p.person_id,async()=>{
 const profile=html(await renderer.render('#/person/'+encodeURIComponent(p.person_id)));
 const lineage=html(await renderer.render('#/person/'+encodeURIComponent(p.person_id)+'/lineage'));
 visible(profile,p.name,p.person_id+'/name');assert(profile.includes('<h3>来源说明与待核事项</h3>'));
 for(const [i,v]of p.unknowns.entries())visible(profile,v,p.person_id+'/unknowns/'+i);
 for(const table of ['education','appointments','publications','teaching'])for(const [i,row]of(p[table]||[]).entries())visible(profile,row.note,p.person_id+'/'+table+'/'+i+'/note');
 visible(profile,p.research_interests,p.person_id+'/research_interests');
 for(const [i,m]of p.mentors.entries()){visible(lineage,m.name,p.person_id+'/mentor/'+i);for(const key of ['note','evidence_note','scope_label','description','employment_status_note'])visible(lineage,m[key],p.person_id+'/mentor/'+i+'/'+key);}
 visible(profile,p.official_profile_availability_label,p.person_id+'/official_availability');
 const alternatives=p.alternative_professional_sources||[];
 if(pins.special_official_entries.includes(p.person_id)){assert.equal(p.official_profile_navigation_eligible,false);assert(alternatives.length);}
 const entries=alternatives.length?alternatives:[{url:p.official_url}];
 for(const entry of entries){visible(profile,entry.title,p.person_id+'/entry_label');const blocked=entry.source_navigation_enabled===false||(p.sources||[]).some(s=>s.url===entry.url&&(s.navigation_enabled===false||s.navigation_available===false));if(!blocked)assert(profile.includes('href="'+esc(entry.url)+'"'),p.person_id+'/official-clickable');}
});
test('all 246 profile/lineage routes used the real registered handler',()=>{
 assert.equal(renderer.stats.renders,246);assert.equal(renderer.stats.imports,1);assert.equal(renderer.stats.handlerRegistrations,1);assert.equal(renderer.stats.handlerCalls,245);
});
