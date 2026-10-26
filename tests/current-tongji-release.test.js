import {createImmutableCohortRenderer} from './immutable-cohort-renderer.js';
import {readAtlasFile,createAtlasFetch} from './atlas-test-io.js';
import {test} from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {matches, stages, mentorOfficialUrl, mentorProfileRoute} from '../site/model.js';
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
const db=readAtlasFile(new URL('../site/atlas.json',import.meta.url));
const roster=JSON.parse(fs.readFileSync(new URL('../site/rosters.json',import.meta.url)));
const mapping=JSON.parse(fs.readFileSync(new URL('./fixtures/independent-tongji12-source-mapping.json',import.meta.url)));
test('actual Tongji cohort exactly preserves independently reviewed fields, identities and scope',()=>{
 assert.equal(db.people.length,814+mapping.people.length+bitMapping.people.length+nwpuMapping.people.length+scutMapping.people.length+ustcMapping.people.length+cauMapping.people.length+fduMapping.people.length+mucMapping.people.length+nwsuafMapping.people.length+oucMapping.people.length+lzuMapping.people.length+sjtuMapping.people.length+thuMapping.people.length);assert.equal(db.build_id,roster.build_id);
 for(const expected of mapping.people){
  const actual=db.people.find(p=>p.person_id===expected.person_id);assert.deepEqual(actual,expected);
  assert.equal(typeof actual.department,'string');assert(actual.department.length>0);
  assert(matches(actual,{q:actual.name},db.org_units));assert(matches(actual,{school:'tongji',org:actual.department_id},db.org_units));
  assert(!matches(actual,{school:'seu'},db.org_units));assert.equal(actual.quick_link_eligible,expected.quick_link_eligible);assert.equal(actual.include_in_current_faculty_count,expected.include_in_current_faculty_count);
  for(const stage of ['bachelor','master','doctor']) for(const event of stages(actual,stage)){assert.equal(event.event_kind,'degree');assert.equal(event.degree_awarded,true);}
 }
});
const {render}=createImmutableCohortRenderer({db,roster,fixtureId:import.meta.url});
for(const expected of mapping.people)test('actual Tongji profile and lineage preserve '+expected.name,async()=>{
 const nodes=await render('#/person/'+expected.person_id);const html=['#main','#profile-content'].map(k=>nodes(k).innerHTML).join('\n');
 assert(html.includes(expected.name));assert(html.includes('同济大学'));
 const lineage=await render('#/person/'+expected.person_id+'/lineage');
 const relationHtml=['#main','#profile-content','#mind-stage'].map(k=>lineage(k).innerHTML).join('\n');
 for(const mentor of expected.mentors){assert(relationHtml.includes(mentor.name));assert(relationHtml.includes(mentor.type_label||mentor.type));}
 if(expected.mentors.length===0)assert(relationHtml.includes('0条已收录关系'));
});
const person=id=>db.people.find(p=>p.person_id===id);
test('Tongji degree evidence, unknown funding category and occupational guidance stay separate',()=>{
 const all=mapping.people.flatMap(p=>p.education);assert.equal(all.length,39);assert.deepEqual([true,false,null].map(v=>all.filter(e=>e.degree_awarded===v).length),[27,8,4]);
 const y=person('tongji-yangweitao');assert.equal(y.education.filter(e=>e.degree_awarded===null).length,1);
 const x=person('tongji-xielihua');assert.equal(x.education.length,3);assert(x.education.every(e=>e.degree_awarded===true));assert.equal(x.appointments.length,1);assert.equal(x.appointments[0].start,'2012-10');assert.equal(x.appointments[0].title,null);
 const h=person('tongji-huominfeng');assert.equal(h.mentors.length,1);assert.equal(h.professional_research_advisors.length,1);
 assert.equal(mapping.people.flatMap(p=>p.mentors).length,17);
 assert.equal(person('tongji-wenxianghao').mentors.length,3);assert.equal(person('tongji-wenxianghao').education.filter(e=>e.degree_awarded===null).length,2);
});
for(const [id,terms] of [
 ['tongji-yangjie',['目录教授类别','特聘研究员','不以目录类别改本人职称','2023-03-21','2025–2026']],
 ['tongji-wenxianghao',['学位字段为博士','PhD/DMA','王小红','Joan Patenaude Yarnell','2024声乐教师工作']],
 ['tongji-huding',['1995','1999','2013','获授年','不推2004就是讲师','城乡特色文化与空间','讲授']],
 ['tongji-yangweitao',['2017年博士毕业','国家公派类别不明','不能补访问','常津','2022-03']],
 ['tongji-gexin',['耶鲁2010—2013明确工作','不推博士后','Horace H Loh','Ping-Yee Law','未造单项作品']],
 ['tongji-piyong',['2026-06-01 10:23','时区未知','非已核发布日期','特聘长聘教授（三级）']],
 ['tongji-xielihua',['2012年10月','不是教授起任日','一个教育事件','两种学位称谓','本科','研究生','企业实践']],
 ['tongji-huominfeng',['博士毕业','工学博士','M. Huo*','不认定通讯作者']]
])test('actual Tongji bounded source evidence visible '+id,async()=>{
 const n=await render('#/person/'+id),html=n('#main').innerHTML+'\n'+n('#profile-content').innerHTML;
 for(const term of terms)assert(html.includes(term),'missing visible '+term);
 if(id==='tongji-xielihua')assert.match(html,/2012-10[^<]*<\/div><h3>任职<\/h3>/);
});
test('actual Huo occupational guide is separately rendered from the one educational relation',async()=>{
 const n=await render('#/person/tongji-huominfeng/lineage'),html=['#main','#profile-content','#mind-stage'].map(k=>n(k).innerHTML).join('\n');
 const p=person('tongji-huominfeng');for(const a of p.professional_research_advisors){assert(html.includes(a.name));}assert(html.includes('职业'));
});
