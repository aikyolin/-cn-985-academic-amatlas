import {test} from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {readJSONFile} from './atlas-test-io.js';
import {createImmutableCohortRenderer} from './immutable-cohort-renderer.js';
import {stages,mentorEvents,mentorProfileRoute,mentorOfficialUrl,officialProfileUrl} from '../site/model.js';
const raw=readFileSync(new URL('./fixtures/hit-tangtianqi1-source-mapping.json',import.meta.url));
assert.equal(createHash('sha256').update(raw).digest('hex'),'4e439e8dba8ee781a9ad5f25c87adb8198dccff68fadc320203e3677051708eb');
const fixed=JSON.parse(raw),p=fixed.people[0];
const db=readJSONFile(new URL('../site/atlas.json',import.meta.url)),roster=readJSONFile(new URL('../site/rosters.json',import.meta.url));
const renderer=createImmutableCohortRenderer({db,roster,fixtureId:'HIT_TANGTIANQI1_SOURCE_REVIEWED_20261030'});
const esc=s=>String(s).replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;').replaceAll('"','&quot;').replaceAll("'",'&#39;');
const html=p=>Object.values(p.snapshot).map(v=>v.innerHTML).join('\n');
const visible=(s,v,label)=>assert(s.includes(esc(v)),label);
test('exact one addition and batch with immutable reviewed fixture',()=>{
 assert.equal(db.people.length,1180);assert.equal(db.pending_people.length,84);assert.equal(p.person_id,'hit-tangtianqi');assert.deepEqual(db.people.slice(1179),fixed.people);assert.deepEqual(db.profile_batches.slice(226),fixed.profile_batches);assert.equal(p.department_id,'hit-energy');assert.deepEqual(p.campus_ids,['harbin']);
});
test('three study stages remain unknown awards and 2019 joint event does not create degree or interval',()=>{
 assert.equal(p.education.length,4);assert.deepEqual(p.education.map(e=>e.degree_awarded),[null,null,null,false]);
 for(const e of p.education){assert.equal(e.start,null);assert.equal(e.end,null);assert.equal(e.degree_awarded_date,null);assert.equal(e.field,null);}
 assert.equal(p.education[3].event_year,'2019');assert.equal(p.education[3].degree,null);assert.equal(p.education[3].education_stage,null);
 for(const stage of ['bachelor','master','doctor'])assert.equal(stages(p,stage).length,0);
});
test('2021 graduation/staying event date is not lecturer or postdoc start and 2024 title is source-as-of',()=>{
 assert.equal(p.appointments.length,2);assert.equal(p.appointments[0].source_as_of,'2024-03-26');assert.equal(p.appointments[1].event_date,'2021-07');
 for(const a of p.appointments){assert.equal(a.start,null);assert.equal(a.end,null);assert.equal(a.current_employment_verified,null);}
 assert.equal(p.publications.length,0);assert(p.unknowns.some(x=>x.includes('协助指导')&&x.includes('特等奖2项')));assert(p.unknowns.some(x=>x.includes('申请事件不是博士后入职')));assert(p.unknowns.some(x=>x.includes('非独立唯一身份认证')));
});
test('one stage-unknown He Yurong relationship has no education binding or identity navigation',()=>{
 assert.equal(p.mentors.length,1);const m=p.mentors[0];assert.equal(m.name,'何玉荣');assert.equal(m.stage,'unknown');assert.equal(m.education_event_id,null);assert.equal(m.formal_dissertation_advisor_verified,null);assert.equal(m.person_id,null);assert.equal(mentorProfileRoute(m,db.people),'');assert.equal(mentorOfficialUrl(m),'');
 assert.deepEqual(mentorEvents(p,m),[]);
});
test('official article and selection notice are alternatives, never an asserted personal homepage',()=>{
 assert.equal(officialProfileUrl(p),'');assert.equal(p.official_profile_availability,'unavailable');assert.equal(p.alternative_professional_sources.length,2);assert(p.alternative_professional_sources[0].title.includes('报道'));assert(p.alternative_professional_sources[1].title.includes('公示'));
});
test('real profile exposes every approved note, event qualifier and both accurate alternative source links',async()=>{
 const h=html(await renderer.render('#/person/'+p.person_id));visible(h,p.name,'name');for(const t of p.unknowns)visible(h,t,'source explanation');for(const e of p.education)visible(h,e.note,'education note');for(const a of p.appointments)visible(h,a.note,'career note');visible(h,p.official_profile_availability_label,'not a homepage');for(const s of p.alternative_professional_sources){visible(h,s.title,'alternative source label');assert(h.includes(s.url),'alternative source URL');}
});
test('real lineage retains unknown stage and full relationship limitation without identity navigation',async()=>{
 const h=html(await renderer.render('#/person/'+p.person_id+'/lineage'));const m=p.mentors[0];visible(h,m.name,'mentor');visible(h,m.description,'stage limitation');visible(h,m.employment_status_note,'identity limitation');assert.equal(m.education_stage,null);assert.equal(m.stage,'unknown');assert.equal(m.type,'来源导师（阶段未知）');assert(h.includes('>来源导师（阶段未知）</text>'));assert(!h.includes('source_stage_advisor'));
});
