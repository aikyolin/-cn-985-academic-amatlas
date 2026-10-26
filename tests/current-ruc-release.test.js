import {createImmutableCohortRenderer} from './immutable-cohort-renderer.js';
import {readAtlasFile,createAtlasFetch} from './atlas-test-io.js';
import {test} from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {matches, stages, mentorOfficialUrl, mentorProfileRoute} from '../site/model.js';
const ecnuMapping=JSON.parse(fs.readFileSync(new URL('./fixtures/independent-ecnu12-source-mapping.json',import.meta.url)));
const buaaMapping=JSON.parse(fs.readFileSync(new URL('./fixtures/independent-buaa12-source-mapping.json',import.meta.url)));
const tongjiMapping=JSON.parse(fs.readFileSync(new URL('./fixtures/independent-tongji12-source-mapping.json',import.meta.url)));
const bitMapping=JSON.parse(fs.readFileSync(new URL('./fixtures/independent-bit12-source-mapping.json',import.meta.url)));
const nwpuMapping=JSON.parse(fs.readFileSync(new URL('./fixtures/independent-nwpu12-source-mapping.json',import.meta.url)));
const scutMapping=JSON.parse(fs.readFileSync(new URL('./fixtures/independent-scut11-source-mapping.json',import.meta.url)));
const ustcMapping=JSON.parse(fs.readFileSync(new URL('./fixtures/independent-ustc12-source-mapping.json',import.meta.url)));
const cauMapping=JSON.parse(fs.readFileSync(new URL('./fixtures/independent-cau12-source-mapping.json',import.meta.url)));
const fduMapping=JSON.parse(fs.readFileSync(new URL('./fixtures/independent-fdu12-source-mapping.json',import.meta.url)));
const mucMapping=JSON.parse(fs.readFileSync(new URL('./fixtures/independent-muc12-source-mapping.json',import.meta.url)));
const nwsuafMapping=JSON.parse(fs.readFileSync(new URL('./fixtures/independent-nwsuaf12-source-mapping.json',import.meta.url)));
const oucMapping=JSON.parse(fs.readFileSync(new URL('./fixtures/independent-ouc12-source-mapping.json',import.meta.url)));
const lzuMapping=JSON.parse(fs.readFileSync(new URL('./fixtures/independent-lzu11-source-mapping.json',import.meta.url)));
const sjtuMapping=JSON.parse(fs.readFileSync(new URL('./fixtures/independent-sjtu11-source-mapping.json',import.meta.url)));
const thuMapping=JSON.parse(fs.readFileSync(new URL('./fixtures/independent-thu11-source-mapping.json',import.meta.url)));
const pkuMapping=JSON.parse(fs.readFileSync(new URL('./fixtures/independent-pku11-source-mapping.json',import.meta.url)));
const zjuMapping=JSON.parse(fs.readFileSync(new URL('./fixtures/independent-zju7-source-mapping.json',import.meta.url)));
const mixedMapping=JSON.parse(fs.readFileSync(new URL('./fixtures/independent-neu4-cqu3-sysu2-source-mapping.json',import.meta.url)));
const njuSecondMapping=JSON.parse(fs.readFileSync(new URL('./fixtures/independent-nju11-second-source-mapping.json',import.meta.url)));
const seuSecondMapping=JSON.parse(fs.readFileSync(new URL('./fixtures/independent-seu11-second-source-mapping.json',import.meta.url)));
const db=readAtlasFile(new URL('../site/atlas.json',import.meta.url));
const roster=JSON.parse(fs.readFileSync(new URL('../site/rosters.json',import.meta.url)));
const mapping=JSON.parse(fs.readFileSync(new URL('./fixtures/independent-ruc8-source-mapping.json',import.meta.url)));
test('actual RUC cohort exactly preserves independently reviewed fields, identities and scope',()=>{
 assert.equal(db.people.length,782+mapping.people.length+ecnuMapping.people.length+buaaMapping.people.length+tongjiMapping.people.length+bitMapping.people.length+nwpuMapping.people.length+scutMapping.people.length+ustcMapping.people.length+cauMapping.people.length+fduMapping.people.length+mucMapping.people.length+nwsuafMapping.people.length+oucMapping.people.length+lzuMapping.people.length+sjtuMapping.people.length+thuMapping.people.length+pkuMapping.people.length+zjuMapping.people.length+mixedMapping.people.length+njuSecondMapping.people.length+seuSecondMapping.people.length);assert.equal(db.build_id,roster.build_id);
 for(const expected of mapping.people){
  const actual=db.people.find(p=>p.person_id===expected.person_id);assert.deepEqual(actual,expected);
  assert.equal(typeof actual.department,'string');assert(actual.department.length>0);
  assert(matches(actual,{q:actual.name},db.org_units));assert(matches(actual,{school:'ruc',org:actual.department_id},db.org_units));
  assert(!matches(actual,{school:'seu'},db.org_units));assert.equal(actual.quick_link_eligible,expected.quick_link_eligible);assert.equal(actual.include_in_current_faculty_count,expected.include_in_current_faculty_count);
  for(const stage of ['bachelor','master','doctor']) for(const event of stages(actual,stage)){assert.equal(event.event_kind,'degree');assert.equal(event.degree_awarded,true);}
 }
});
const {render}=createImmutableCohortRenderer({db,roster,fixtureId:import.meta.url});
for(const expected of mapping.people)test('actual RUC profile and lineage preserve '+expected.name,async()=>{
 const nodes=await render('#/person/'+expected.person_id);const html=['#main','#profile-content'].map(k=>nodes(k).innerHTML).join('\n');
 assert(html.includes(expected.name));assert(html.includes('中国人民大学'));
 const lineage=await render('#/person/'+expected.person_id+'/lineage');
 const relationHtml=['#main','#profile-content','#mind-stage'].map(k=>lineage(k).innerHTML).join('\n');
 for(const mentor of expected.mentors){assert(relationHtml.includes(mentor.name));assert(relationHtml.includes(mentor.type_label||mentor.type));}
 if(expected.mentors.length===0)assert(relationHtml.includes('0条已收录关系'));
});

const person=id=>db.people.find(p=>p.person_id===id);
const htmlOf=nodes=>['#main','#profile-content','#mind-stage'].map(k=>nodes(k).innerHTML).join('\n');
test('RUC reviewed scope distinguishes publications, creative works, stages and roles',()=>{
 const events=mapping.people.flatMap(p=>p.education);assert.equal(events.length,25);assert.equal(events.filter(e=>e.degree_awarded===true).length,13);assert.equal(events.filter(e=>e.degree_awarded===false).length,4);assert.equal(events.filter(e=>e.degree_awarded===null).length,8);
 assert.equal(mapping.people.reduce((n,p)=>n+p.appointments.length,0),8);assert.equal(mapping.people.reduce((n,p)=>n+p.publications.length,0),14);assert.equal(mapping.people.reduce((n,p)=>n+(p.creative_works||[]).length,0),2);assert.equal(mapping.people.reduce((n,p)=>n+p.mentors.length,0),3);
});
test('only Li three explicit source degree awards change from null and study endpoints do not become award dates',()=>{
 const changed=mapping.people.flatMap(p=>p.education).filter(e=>e.source_degree_awarded===null&&e.degree_awarded===true);
 assert.deepEqual(changed.map(e=>e.event_id).sort(),[1,2,3].map(i=>'ruc-lijingping-education-'+i));
 for(const e of changed){assert.equal(e.event_kind,'degree');for(const k of ['award_year','award_date','degree_awarded_year','degree_awarded_date'])if(k in e)assert.equal(e[k],null);}
 assert(person('ruc-xuwangli').education.every(e=>e.degree_awarded===null));
});
test('Qi joint doctoral label is one unknown-award event, not two degrees or UCLA award',async()=>{
 const p=person('ruc-qitianjiao');assert.equal(p.education.length,1);assert.equal(p.education[0].degree_awarded,null);assert.equal(p.education[0].event_kind,'degree_study');assert.equal(p.mentors.length,0);
 const html=htmlOf(await render('#/person/'+p.person_id));for(const t of ['UCLA','不拆两学位','授位机构'])assert(html.includes(t),t);
});
test('Qi four undergraduate core teaching courses retain explicit teaching role',async()=>{
 const p=person('ruc-qitianjiao');assert.equal(p.teaching.length,4);assert(p.teaching.every(t=>t.role==='讲授'&&t.note.includes('本科专业核心课')));assert.equal(p.appointments.length,2);assert(p.appointments.every(a=>a.start===null));
 const html=htmlOf(await render('#/person/'+p.person_id));for(const t of p.teaching)assert(html.includes(t.course));assert(html.includes('档案系系主任'));assert(html.includes('本科专业核心课'));
});
test('Liu three stage-specific relations preserve two Wei stages and one postdoctoral collaborator, never reviewer substitution',async()=>{
 const p=person('ruc-liu-danfeng');assert.equal(p.mentors.length,3);assert.equal(p.mentors.filter(m=>m.name==='魏德东').length,2);assert.equal(p.mentors.filter(m=>m.name==='乌云毕力格').length,1);assert(!p.mentors.some(m=>m.name==='张风雷'));
 assert.equal(p.education.find(e=>e.event_id==='ruc-liu-postdoc').end,'2024-07');assert.equal(p.education.find(e=>e.event_id==='ruc-liu-postdoc').degree_awarded,false);
 const html=htmlOf(await render('#/person/'+p.person_id));for(const t of ['2023-06-07','2024-07','弘教尊者'])assert(html.includes(t),t);
 const graph=htmlOf(await render('#/person/'+p.person_id+'/lineage'));for(const m of p.mentors){assert(graph.includes(m.name));assert(graph.includes(m.type_label));}
});
test('old three sociology identities remain ordered before the two new accepted profiles',()=>{
 assert.deepEqual(db.people.filter(p=>p.department_id==='ruc-sociology').map(p=>p.person_id),['ruc-chenjinsong','ruc-chennabo','ruc-fanglijie','ruc-wangshuixiong','ruc-zhaoyandong']);
 const w=person('ruc-wangshuixiong');assert.equal(w.education.filter(e=>e.degree_awarded===null).length,3);assert.equal(w.education.filter(e=>e.degree_awarded===false).length,1);
});
test('Zhao institution-page identity never creates an unsupported appointment',async()=>{
 const p=person('ruc-zhaoyandong');assert.equal(p.appointments.length,0);assert.equal(p.mentors.length,0);
 const html=htmlOf(await render('#/person/'+p.person_id));assert(html.includes('未留存明确本人任职句'));assert(html.includes('不产生雇佣或任职事件'));assert(html.includes('任职详情待核实'));
});
test('An two designs stay separate from bibliography and exact contributions remain visible',async()=>{
 const p=person('ruc-anyaoshun');assert.equal(p.publications.length,0);assert.equal(p.creative_works.length,2);assert.equal(p.education[0].degree_awarded,null);assert.equal(p.education[1].degree_awarded,true);
 const html=htmlOf(await render('#/person/'+p.person_id));for(const t of ['1996','2003','中国品牌日标识','中华艺文奖标识及视觉识别系统设计','最终选用方案设计者','主持设计','非连续语句'])assert(html.includes(t),t);
 for(const w of p.creative_works){assert.equal(w.work_type,'visual_identity_design');assert.equal(w.publication_date,null);assert.equal(w.independent_registration_or_authorship_verified,false);}
});
test('statistics bibliography preserves explicit Li compilation and unknown Xu role without transferring authorship',async()=>{
 const li=person('ruc-lijingping'),xu=person('ruc-xuwangli');assert.equal(li.publications.length,2);assert.equal(xu.publications.length,2);assert(li.publications.every(w=>w.note.includes('编著')));assert(xu.publications.every(w=>w.note.includes('具体著编角色未明示')));
 const html=htmlOf(await render('#/person/'+li.person_id));assert(html.includes('编著'));const xhtml=htmlOf(await render('#/person/'+xu.person_id));assert(xhtml.includes('具体著编角色未明示'));
});
