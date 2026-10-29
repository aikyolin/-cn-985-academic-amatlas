// Exact two-person source-reviewed cohort; real router, no workbook I/O.
import {test} from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {readJSONFile} from './atlas-test-io.js';
import {createImmutableCohortRenderer} from './immutable-cohort-renderer.js';
import {stages,mentorEvents,mentorProfileRoute,mentorOfficialUrl} from '../site/model.js';
const raw=readFileSync(new URL('./fixtures/hit-energy2-source-mapping.json',import.meta.url));
assert.equal(createHash('sha256').update(raw).digest('hex'),'5a41bb46ed311be7754576b313669f67626f5b44b0f1bf9f9c92fde4fe67ad9e');
const fixed=JSON.parse(raw),ids=['hit-zhaozhiyuan','hit-yanhan-energy'];
const db=readJSONFile(new URL('../site/atlas.json',import.meta.url)),roster=readJSONFile(new URL('../site/rosters.json',import.meta.url));
const renderer=createImmutableCohortRenderer({db,roster,fixtureId:'HIT_ENERGY2_SOURCE_REVIEWED_20261028'});
const esc=s=>String(s).replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;').replaceAll('"','&quot;').replaceAll("'",'&#39;');
const html=p=>Object.values(p.snapshot).map(v=>v.innerHTML).join('\n');
const visible=(s,v,label)=>{if(typeof v==='string'&&v)assert(s.includes(esc(v)),label);};
const actual=id=>{const rows=db.people.filter(p=>p.person_id===id);assert.equal(rows.length,1);return rows[0];};
test('two exact identities append, with no unreviewed third person or new department',()=>{
 assert.equal(db.people.slice(0,1151).length,1151);assert.equal(db.pending_people.length,84);
 assert.deepEqual(fixed.people.map(p=>p.person_id),ids);assert.deepEqual(db.people.slice(1149,1151),fixed.people);
 assert.equal(fixed.profile_batches.length,1);assert.deepEqual(db.profile_batches.slice(223,224),fixed.profile_batches);
 for(const p of fixed.people){assert.equal(p.school_id,'hit');assert.equal(p.department_id,'hit-energy');assert.deepEqual(p.campus_ids,['harbin']);}
 assert(!db.people.some(p=>p.person_id==='hit-luoyuxi'));
});
test('seven education records retain two source-awarded doctorates, three unknown and two joint-training non-awards',()=>{
 const e=fixed.people.flatMap(p=>p.education);assert.equal(e.length,7);
 assert.deepEqual([true,null,false].map(v=>e.filter(x=>x.degree_awarded===v).length),[2,3,2]);
 for(const p of fixed.people){assert.equal(stages(actual(p.person_id),'doctor').length,1);assert.equal(stages(actual(p.person_id),'bachelor').length,0);assert.equal(stages(actual(p.person_id),'master').length,0);}
 for(const x of e.filter(x=>x.event_kind==='joint_training'))assert.equal(x.degree_awarded,false);
 for(const x of e){assert.equal(x.degree_awarded_date,null);assert(Object.hasOwn(x,'degree_awarded_date'));}
});
test('all event date own-properties, values and types match the fixed source projection',()=>{
 for(const p of fixed.people)for(const table of ['education','appointments','mentors','publications','teaching'])for(const [i,row] of (p[table]||[]).entries()){
  const got=actual(p.person_id)[table][i];const keys=new Set([...Object.keys(row),...Object.keys(got)].filter(k=>/(date|year|month|start|end|period)/i.test(k)));
  for(const k of keys){assert.equal(Object.hasOwn(got,k),Object.hasOwn(row,k));assert.deepEqual(got[k],row[k]);}
 }
});
test('three stated mentors retain doctoral versus joint-training stage and no identity navigation',()=>{
 const z=actual(ids[0]),y=actual(ids[1]);assert.equal(z.mentors.length,0);assert.equal(y.mentors.length,3);
 assert.deepEqual(y.mentors.map(m=>m.name),['王松涛','罗磊','Hyung Hee Cho']);
 for(const m of y.mentors){assert.equal(mentorProfileRoute(m,db.people),'');assert.equal(mentorOfficialUrl(m),'');assert.equal(m.employment_status,'unknown');assert.equal(m.person_id,null);assert.equal(m.formal_dissertation_advisor_verified,null);}
 for(const m of y.mentors.slice(0,2)){const events=mentorEvents(y,m);assert.equal(events.length,1);assert.equal(events[0].event_id,'hit-yanhan-energy-education-2');assert.equal(events[0].degree_awarded,true);}
 const joint=y.mentors[2],events=mentorEvents(y,joint);assert.equal(events.length,1);assert.equal(events[0].event_id,'hit-yanhan-energy-education-3');assert.equal(events[0].degree_awarded,false);assert.equal(events[0].event_kind,'joint_training');
});
test('supervision qualifications and bibliographic details are retained without creating personal mentor edges',()=>{
 const z=actual(ids[0]),y=actual(ids[1]);assert(z.appointments[0].note.includes('硕士生导师'));assert(z.appointments[0].note.includes('2025-06'));assert(y.appointments[1].note.includes('硕士研究生导师'));assert(y.appointments[1].note.includes('起始时间未披露'));
 assert.equal(z.mentors.length,0);assert.equal(y.mentors.length,3);assert.equal(z.publications.length,2);
 for(const w of z.publications){assert.equal(w.publisher_metadata_verified,null);assert.equal(w.doi,null);assert.equal(w.individual_article_link_verified,false);assert.deepEqual(w.authors,w.authors_as_source);for(const author of w.authors)assert(w.note.includes(author));assert(w.note.includes(w.volume));assert(w.note.includes(w.pages_or_article_number));}
 assert.deepEqual(z.publications.map(w=>[w.year,w.volume,w.pages_or_article_number]),[[2025,'160','110047'],[2025,'137','367-379']]);
});
test('negative changes cannot promote unknown awards, invent dates or turn supervisor qualifications into personal mentorship',()=>{
 const p=structuredClone(fixed.people[0]);p.education[0].degree_awarded=false;assert.throws(()=>assert.deepEqual(p,fixed.people[0]));
 const q=structuredClone(fixed.people[0]);q.education[2].degree_awarded_date=q.education[2].end;assert.throws(()=>assert.deepEqual(q,fixed.people[0]));
 const r=structuredClone(fixed.people[1]);r.mentors[2].person_id=ids[0];assert.throws(()=>assert.deepEqual(r,fixed.people[1]));
 const e={...fixed.people[0].education[3],event_kind:'degree',degree:'博士'};assert.equal(stages({education:[e]},'doctor').length,0);
});
for(const p of fixed.people)test('real profile and all-stage lineage preserve full visible source facts: '+p.person_id,async()=>{
 const profile=html(await renderer.render('#/person/'+encodeURIComponent(p.person_id)));
 const lineage=html(await renderer.render('#/person/'+encodeURIComponent(p.person_id)+'/lineage'));
 visible(profile,p.name,'name');assert(profile.includes('<h3>来源说明与待核事项</h3>'));assert(profile.includes('href="'+esc(p.official_url)+'"'));
 for(const [i,v] of p.unknowns.entries())visible(profile,v,p.person_id+'/unknown/'+i);
 for(const table of ['education','appointments','publications','teaching'])for(const [i,row]of(p[table]||[]).entries())visible(profile,row.note,p.person_id+'/'+table+'/'+i+'/note');
 for(const [i,m]of p.mentors.entries()){visible(lineage,m.name,'mentor/name');for(const k of ['description','employment_status_note'])visible(lineage,m[k],'mentor/'+i+'/'+k);}
 for(const w of p.publications){visible(profile,w.title,'work/title');visible(profile,w.note,'work/full-bibliographic-note');}
 assert(profile.includes('硕士'),'supervision qualification remains visible');
 if(p.person_id===ids[1]){visible(lineage,'Hyung Hee Cho','joint-stage-guide');assert(lineage.includes('联合培养'),'joint-training label must remain on all-stage lineage');}
});
test('all four profile/lineage renders use the registered real app handler',()=>{
 assert.equal(renderer.stats.renders,4);assert.equal(renderer.stats.imports,1);assert.equal(renderer.stats.handlerRegistrations,1);assert.equal(renderer.stats.handlerCalls,3);
});
