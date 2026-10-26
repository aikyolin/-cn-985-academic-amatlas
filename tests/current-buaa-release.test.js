import {createImmutableCohortRenderer} from './immutable-cohort-renderer.js';
import {readAtlasFile,createAtlasFetch} from './atlas-test-io.js';
import {test} from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {matches, stages, mentorOfficialUrl, mentorProfileRoute} from '../site/model.js';
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
const mapping=JSON.parse(fs.readFileSync(new URL('./fixtures/independent-buaa12-source-mapping.json',import.meta.url)));
test('actual BUAA cohort exactly preserves independently reviewed fields, identities and scope',()=>{
 assert.equal(db.people.length,802+mapping.people.length+tongjiMapping.people.length+bitMapping.people.length+nwpuMapping.people.length+scutMapping.people.length+ustcMapping.people.length+cauMapping.people.length+fduMapping.people.length+mucMapping.people.length+nwsuafMapping.people.length+oucMapping.people.length+lzuMapping.people.length+sjtuMapping.people.length+thuMapping.people.length+pkuMapping.people.length+zjuMapping.people.length+mixedMapping.people.length+njuSecondMapping.people.length+seuSecondMapping.people.length);assert.equal(db.build_id,roster.build_id);
 for(const expected of mapping.people){
  const actual=db.people.find(p=>p.person_id===expected.person_id);assert.deepEqual(actual,expected);
  assert.equal(typeof actual.department,'string');assert(actual.department.length>0);
  assert(matches(actual,{q:actual.name},db.org_units));assert(matches(actual,{school:'buaa',org:actual.department_id},db.org_units));
  assert(!matches(actual,{school:'seu'},db.org_units));assert.equal(actual.quick_link_eligible,expected.quick_link_eligible);assert.equal(actual.include_in_current_faculty_count,expected.include_in_current_faculty_count);
  for(const stage of ['bachelor','master','doctor']) for(const event of stages(actual,stage)){assert.equal(event.event_kind,'degree');assert.equal(event.degree_awarded,true);}
 }
});
const {render}=createImmutableCohortRenderer({db,roster,fixtureId:import.meta.url});
for(const expected of mapping.people)test('actual BUAA profile and lineage preserve '+expected.name,async()=>{
 const nodes=await render('#/person/'+expected.person_id);const html=['#main','#profile-content'].map(k=>nodes(k).innerHTML).join('\n');
 assert(html.includes(expected.name));assert(html.includes('北京航空航天大学'));
 const lineage=await render('#/person/'+expected.person_id+'/lineage');
 const relationHtml=['#main','#profile-content','#mind-stage'].map(k=>lineage(k).innerHTML).join('\n');
 for(const mentor of expected.mentors){assert(relationHtml.includes(mentor.name));assert(relationHtml.includes(mentor.type_label||mentor.type));}
 if(expected.mentors.length===0)assert(relationHtml.includes('0条已收录关系'));
});
const person=id=>db.people.find(p=>p.person_id===id);
test('BUAA source-reported degrees, unknown stages, association and retirement are distinct',()=>{
 const all=mapping.people.flatMap(p=>p.education);assert.equal(all.length,45);assert.deepEqual([true,false,null].map(v=>all.filter(e=>e.degree_awarded===v).length),[19,11,15]);
 assert.equal(all.filter(e=>e.source_degree_awarded===null&&e.degree_awarded===true).length,9);
 const q=person('buaa-quanquan');assert.equal(q.current_employment_status,'unknown');assert.equal(q.quick_link_eligible,false);assert.equal(q.include_in_current_faculty_count,false);
 const z=person('buaa-zhou-xuefeng');assert.equal(z.institutional_associations.length,2);assert.equal(z.appointments.length,2);assert(z.appointments.every(e=>e.start===null));
 const y=person('buaa-yuehanwei');assert.equal(y.retirement_status,'source_reports_retired');assert.equal(y.retirement_year,2024);assert.equal(y.career_end_events.length,1);assert.equal(y.quick_link_eligible,false);assert.equal(y.include_in_current_faculty_count,false);
 assert.equal(person('buaa-jinhao').education.filter(e=>e.degree_awarded===null).length,4);assert.equal(person('buaa-chenyan-sportstraining').education.filter(e=>e.degree_awarded===null).length,3);
});
for(const [id,terms] of [
 ['buaa-quanquan',['在职信息：在职','独立人事核验']],
 ['buaa-zhou-xuefeng',['2004-06至今北京航空航天大学法学院','1998-07至2001-04山东省高级人民法院','独立保留不计任职','副院长','博士生导师','指导资格']],
 ['buaa-jinhao',['主要成员','不升级主讲','with Chen Xiong','with Hewei Shen','March 2021','January 2020','Pages 54-73','不是完整作者表']],
 ['buaa-yuehanwei',['2024年退休','2004年来北航工作','2007年晋升副教授','不证明现在在岗','主编非独著或原作者']],
 ['buaa-chenyan-sportstraining',['现代力量训练理论与方法','现代田径训练理论与方法','运动营养学','主讲','研究生课程','本科生课程','两处Zhou, J.']],
 ['buaa-wuruilin',['2019-03-02','2021译著','吴瑞林、彭雨晨为译者','Robert Kegan','Lisa Laskow Lahey']],
 ['buaa-niuchaohui',['微观经济学','所留成果缺具名作者而未选择书目','不等没有成果','未采GPA或排名不恢复']]
])test('actual BUAA precise source limitations visible '+id,async()=>{
 const n=await render('#/person/'+id),html=n('#main').innerHTML+'\n'+n('#profile-content').innerHTML;for(const term of terms)assert(html.includes(term),'missing visible '+term);
});
