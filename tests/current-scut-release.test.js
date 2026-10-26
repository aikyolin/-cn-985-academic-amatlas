import {createImmutableCohortRenderer} from './immutable-cohort-renderer.js';
import {readAtlasFile,createAtlasFetch} from './atlas-test-io.js';
import {test} from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {matches, stages, mentorOfficialUrl, mentorProfileRoute} from '../site/model.js';
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
const db=readAtlasFile(new URL('../site/atlas.json',import.meta.url));
const roster=JSON.parse(fs.readFileSync(new URL('../site/rosters.json',import.meta.url)));
const mapping=JSON.parse(fs.readFileSync(new URL('./fixtures/independent-scut11-source-mapping.json',import.meta.url)));
test('actual SCUT cohort exactly preserves independently reviewed fields, identities and scope',()=>{
 assert.deepEqual(mapping.people.map(p=>p.person_id),["scut-chenguangxu","scut-heping","scut-chewenquan","scut-caoyufei","scut-zhongzhiheng","scut-yangxiongwen","scut-yangwei","scut-liuxiaoni","scut-guodifan","scut-qilili","scut-zhongyouliang-mathematics"]);
 assert(mapping.people.every(p=>p.data_batch_id==='faculty-batch-scut11-independent-20261026'));
 assert.equal(db.people.length,850+mapping.people.length+ustcMapping.people.length+cauMapping.people.length+fduMapping.people.length+mucMapping.people.length+nwsuafMapping.people.length+oucMapping.people.length+lzuMapping.people.length+sjtuMapping.people.length+thuMapping.people.length+pkuMapping.people.length+zjuMapping.people.length+mixedMapping.people.length);assert.equal(db.build_id,roster.build_id);
 for(const expected of mapping.people){
  const actual=db.people.find(p=>p.person_id===expected.person_id);assert.deepEqual(actual,expected);
  assert.equal(typeof actual.department,'string');assert(actual.department.length>0);
  assert(matches(actual,{q:actual.name},db.org_units));assert(matches(actual,{school:'scut',org:actual.department_id},db.org_units));
  assert(!matches(actual,{school:'seu'},db.org_units));assert.equal(actual.quick_link_eligible,expected.quick_link_eligible);assert.equal(actual.include_in_current_faculty_count,expected.include_in_current_faculty_count);
  for(const stage of ['bachelor','master','doctor']) for(const event of stages(actual,stage)){assert.equal(event.event_kind,'degree');assert.equal(event.degree_awarded,true);}
 }
});
const {render}=createImmutableCohortRenderer({db,roster,fixtureId:import.meta.url});
for(const expected of mapping.people)test('actual SCUT profile and lineage preserve '+expected.name,async()=>{
 const nodes=await render('#/person/'+expected.person_id);const html=['#main','#profile-content'].map(k=>nodes(k).innerHTML).join('\n');
 assert(html.includes(expected.name));assert(html.includes('华南理工大学'));
 const lineage=await render('#/person/'+expected.person_id+'/lineage');
 const relationHtml=['#main','#profile-content','#mind-stage'].map(k=>lineage(k).innerHTML).join('\n');
 for(const mentor of expected.mentors){assert(relationHtml.includes(mentor.name));assert(relationHtml.includes(mentor.type_label||mentor.type));}
 if(expected.mentors.length===0)assert(relationHtml.includes('0条已收录关系'));
});
const person=id=>db.people.find(p=>p.person_id===id);
test('SCUT ten precise source-reported qualifications do not infer award dates and seven ambiguous stages remain unknown',()=>{
 const trueEvents=['scut-chenguangxu-bachelor','scut-caoyufei-bachelor','scut-zhongzhiheng-bachelor','scut-zhongzhiheng-masters','scut-zhongzhiheng-doctorate','scut-yangxiongwen-bachelor','scut-yangxiongwen-master','scut-yangxiongwen-doctor','scut-yangwei-education-2','scut-guodifan-education-1'];
 const unknownEvents=['scut-chenguangxu-doctoral','scut-caoyufei-doctorate','scut-yangwei-education-1','scut-guodifan-training-1','scut-qilili-education-1','scut-zhongyouliang-mathematics-education-1','scut-zhongyouliang-mathematics-education-2'];
 const events=mapping.people.flatMap(p=>p.education);
 for(const id of trueEvents){const e=events.find(e=>e.event_id===id);assert(e,id);assert.equal(e.degree_awarded,true,id);assert(e.degree_awarded_date==null,id);assert(e.note.includes('来源')||e.note.includes('官网')||e.note.includes('本人'),id);}
 for(const id of unknownEvents){const e=events.find(e=>e.event_id===id);assert(e,id);assert.equal(e.degree_awarded,null,id);}
 assert.equal(events.filter(e=>e.degree_awarded===true).length,15);assert.equal(events.filter(e=>e.degree_awarded===false).length,8);assert.equal(events.filter(e=>e.degree_awarded===null).length,7);
});
test('SCUT Chen keeps four unnamed-role professor associations and historical career visible without mentor or employment promotion',async()=>{
 const p=person('scut-chenguangxu');assert.equal(p.mentors.length,0);assert.equal(p.stage_associated_professors.length,4);assert.equal(p.appointments.length,0);assert(p.career_facts_source_reported.length>0);
 const nodes=await render('#/person/'+p.person_id);const html=nodes('#profile-content').innerHTML;
 for(const word of ['吴杰颖','郑南峰','崔屹','角色','2019.09','教授','不认证当前在岗','不能认证缺席'])assert(html.includes(word),word);
 const lineage=await render('#/person/'+p.person_id+'/lineage');assert(lineage('#mind-stage').innerHTML.includes('0条已收录关系'));
});
test('SCUT He retains separate masters and doctoral guidance and unknown authorship of two books',async()=>{
 const p=person('scut-heping');assert.deepEqual(p.mentors.map(m=>m.education_event_id),['scut-heping-masters','scut-heping-doctorate']);assert.equal(p.education.at(-1).degree_awarded,false);
 const nodes=await render('#/person/'+p.person_id);const html=nodes('#profile-content').innerHTML;
 for(const word of ['1977/1987/1994','考入年','著/译角色','科普兰和他的音乐世界','外国作曲家及其音乐名作'])assert(html.includes(word),word);
});
test('SCUT Zhong title start is unknown independently of the explicit 2023-05 university employment start',async()=>{
 const p=person('scut-zhongzhiheng'),a=p.appointments.find(a=>a.title==='副教授');assert(a);assert.equal(a.start,null);assert.equal(a.source_start,'2023-05');assert.equal(a.university_employment_start,'2023-05');
 assert.equal(p.education.length,3);assert(p.education[0].degree.includes('B.Eng.'));assert(p.education[1].degree.includes('M.Phil.'));
 const nodes=await render('#/person/'+p.person_id);const html=nodes('#profile-content').innerHTML;for(const word of ['2023','副教授','职称','B.Eng.','M.Phil.'])assert(html.includes(word),word);
});
test('SCUT Cao doctoral supervision and joint-training supervision remain different while doctorate award stays unknown',()=>{
 const p=person('scut-caoyufei');assert.equal(p.education[1].degree_awarded,null);assert.equal(p.education[2].degree_awarded,false);assert.deepEqual(p.mentors.map(m=>m.education_event_id),['scut-caoyufei-doctorate','scut-caoyufei-joint-training']);assert.deepEqual(p.mentors.map(m=>m.name),['戈钧','Ted Sargent']);assert.notEqual(p.mentors[0].type,p.mentors[1].type);
});
test('SCUT communication directory display uses one observed department and does not duplicate Guo joint doctoral training as an award',async()=>{
 const school=db.org_units.find(o=>o.id==='scut-journalism-communication'),dept=db.org_units.find(o=>o.id==='scut-communication-news');assert(school);assert(dept);assert.equal(school.parent_id,null);assert.equal(dept.parent_id,school.id);assert.equal(dept.name,'新闻传播系');
 for(const id of ['scut-yangwei','scut-liuxiaoni','scut-guodifan','scut-qilili'])assert.equal(person(id).department_id,dept.id);
 const p=person('scut-guodifan');assert.equal(p.education.length,2);assert.equal(p.education[0].degree_awarded,true);assert.equal(p.education[1].degree_awarded,null);const nodes=await render('#/person/'+p.person_id);const html=nodes('#profile-content').innerHTML;for(const word of ['国家公派','联合培养','不另认定','南洋理工大学'])assert(html.includes(word),word);
 const qi=person('scut-qilili');assert.equal(qi.education[0].degree_awarded,null);assert.equal(qi.teaching.length,3);assert(qi.teaching.every(t=>t.role==='讲授'));
});
test('SCUT mathematics reuses the existing department and keeps combined study and postdocs distinct',async()=>{
 const p=person('scut-zhongyouliang-mathematics');assert.equal(p.department_id,'scut-math');assert.deepEqual(p.education.map(e=>e.degree_awarded),[null,null,false,false]);assert.equal(p.mentors.length,0);
 const nodes=await render('#/person/'+p.person_id);const html=nodes('#profile-content').innerHTML;for(const word of ['硕博不拆两个授位','基础数学','Teichmüller','不是副教授任期'])assert(html.includes(word),word);
 assert.equal(db.people.filter(p=>p.department_id==='scut-math').length,4);
});
