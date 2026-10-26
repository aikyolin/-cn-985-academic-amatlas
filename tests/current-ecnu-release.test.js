import {readAtlasFile,createAtlasFetch} from './atlas-test-io.js';
import {test} from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {matches, stages, mentorOfficialUrl, mentorProfileRoute} from '../site/model.js';
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
const db=readAtlasFile(new URL('../site/atlas.json',import.meta.url));
const roster=JSON.parse(fs.readFileSync(new URL('../site/rosters.json',import.meta.url)));
const mapping=JSON.parse(fs.readFileSync(new URL('./fixtures/independent-ecnu12-source-mapping.json',import.meta.url)));
test('actual ECNU cohort exactly preserves independently reviewed fields, identities and scope',()=>{
 assert.equal(db.people.length,790+mapping.people.length+buaaMapping.people.length+tongjiMapping.people.length+bitMapping.people.length+nwpuMapping.people.length+scutMapping.people.length+ustcMapping.people.length+cauMapping.people.length+fduMapping.people.length+mucMapping.people.length+nwsuafMapping.people.length+oucMapping.people.length);assert.equal(db.build_id,roster.build_id);
 for(const expected of mapping.people){
  const actual=db.people.find(p=>p.person_id===expected.person_id);assert.deepEqual(actual,expected);
  assert.equal(typeof actual.department,'string');assert(actual.department.length>0);
  assert(matches(actual,{q:actual.name},db.org_units));assert(matches(actual,{school:'ecnu',org:actual.department_id},db.org_units));
  assert(!matches(actual,{school:'seu'},db.org_units));assert.equal(actual.quick_link_eligible,expected.quick_link_eligible);assert.equal(actual.include_in_current_faculty_count,expected.include_in_current_faculty_count);
  for(const stage of ['bachelor','master','doctor']) for(const event of stages(actual,stage)){assert.equal(event.event_kind,'degree');assert.equal(event.degree_awarded,true);}
 }
});
let serial=0;
async function render(hash){
 const nodes=new Map(),node=k=>{if(!nodes.has(k))nodes.set(k,{innerHTML:'',textContent:'',value:'',style:{},events:{},dataset:{height:'320'},clientWidth:960,addEventListener(t,f){this.events[t]=f},click(){this.onclick?.()}});return nodes.get(k)};
 globalThis.document={querySelector:node,querySelectorAll:()=>[],getElementById:id=>node('#'+id)};
 globalThis.location={href:"https://atlas.test/site/index.html",hash};globalThis.window={scrollTo(){},addEventListener(){}};
 globalThis.fetch=createAtlasFetch(db,roster);
 await import('../site/app.js?current-ecnu-release='+serial++);
 assert(!node('#main').innerHTML.includes('资料暂未加载'));return node;
}
for(const expected of mapping.people)test('actual ECNU profile and lineage preserve '+expected.name,async()=>{
 const nodes=await render('#/person/'+expected.person_id);const html=['#main','#profile-content'].map(k=>nodes(k).innerHTML).join('\n');
 assert(html.includes(expected.name));assert(html.includes('华东师范大学'));
 const lineage=await render('#/person/'+expected.person_id+'/lineage');
 const relationHtml=['#main','#profile-content','#mind-stage'].map(k=>lineage(k).innerHTML).join('\n');
 for(const mentor of expected.mentors){assert(relationHtml.includes(mentor.name));assert(relationHtml.includes(mentor.type_label||mentor.type));}
 if(expected.mentors.length===0)assert(relationHtml.includes('0条已收录关系'));
});
const person=id=>db.people.find(p=>p.person_id===id);
test('ECNU explicit degree evidence is bounded to two new classifications and retains unknown dates',()=>{
 const all=mapping.people.flatMap(p=>p.education);assert.equal(all.length,43);
 assert.deepEqual([true,false,null].map(v=>all.filter(e=>e.degree_awarded===v).length),[18,12,13]);
 const j=person('ecnu-jiangxuefeng').education;assert.equal(j[0].degree_awarded,null);assert.equal(j[1].degree_awarded,true);assert.equal(j[1].degree_awarded_date,null);assert.equal(j[1].degree_awarded_year,null);
 const y=person('ecnu-yinzhihua').education;assert.deepEqual(y.map(e=>e.degree_awarded),[true,null,null,false,false,false]);assert.equal(y[0].degree_awarded_year,null);assert.equal(y[0].degree_awarded_date,null);
 assert.equal(person('ecnu-xusheng').education.filter(e=>e.degree_awarded===null).length,4);
});
for(const [id,terms] of [
 ['ecnu-jiangxuefeng',['学位：博士','未核原学位证','授位年/月/日未知']],
 ['ecnu-yinzhihua',['理学学士','硕博连读','教育学博士','2014-07','2017-12','2022-12']],
 ['ecnu-liangchaoqun',['1986','1993','单阶段起止未知','黄源深','费春放']],
 ['ecnu-guanshuguang',['Research Fellow','不自动认作博士后']],
 ['ecnu-wangxuena',['（筹）','明园晨晖']],
 ['ecnu-huangchenxi',['研究生硕士','社会项目评估','社会福利政策专题','未细分主讲']],
 ['ecnu-xusheng',['36学时','2020.09','2021.09','未确认现在仍开设']],
 ['ecnu-yinguoming',['钱谷融','华东大学出版社','退休状态未核']],
 ['ecnu-gejun',['2004.09','2015.06','不是已核博士学制','本人仅主编','东德篇']]
])test('actual ECNU evidence limits remain visible '+id,async()=>{
 const n=await render('#/person/'+id);const html=n('#main').innerHTML+'\n'+n('#profile-content').innerHTML;
 for(const term of terms)assert(html.includes(term),'missing visible fact '+term);
});
