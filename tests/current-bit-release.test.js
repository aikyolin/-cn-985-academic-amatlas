import {readAtlasFile,createAtlasFetch} from './atlas-test-io.js';
import {test} from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {matches, stages, mentorOfficialUrl, mentorProfileRoute} from '../site/model.js';
const nwpuMapping=JSON.parse(fs.readFileSync(new URL('./fixtures/independent-nwpu12-source-mapping.json',import.meta.url)));
const scutMapping=JSON.parse(fs.readFileSync(new URL('./fixtures/independent-scut11-source-mapping.json',import.meta.url)));
const ustcMapping=JSON.parse(fs.readFileSync(new URL('./fixtures/independent-ustc12-source-mapping.json',import.meta.url)));
const cauMapping=JSON.parse(fs.readFileSync(new URL('./fixtures/independent-cau12-source-mapping.json',import.meta.url)));
const fduMapping=JSON.parse(fs.readFileSync(new URL('./fixtures/independent-fdu12-source-mapping.json',import.meta.url)));
const db=readAtlasFile(new URL('../site/atlas.json',import.meta.url));
const roster=JSON.parse(fs.readFileSync(new URL('../site/rosters.json',import.meta.url)));
const mapping=JSON.parse(fs.readFileSync(new URL('./fixtures/independent-bit12-source-mapping.json',import.meta.url)));
test('actual BIT cohort exactly preserves independently reviewed fields, identities and scope',()=>{
 assert.equal(db.people.length,826+mapping.people.length+nwpuMapping.people.length+scutMapping.people.length+ustcMapping.people.length+cauMapping.people.length+fduMapping.people.length);assert.equal(db.build_id,roster.build_id);
 for(const expected of mapping.people){
  const actual=db.people.find(p=>p.person_id===expected.person_id);assert.deepEqual(actual,expected);
  assert.equal(typeof actual.department,'string');assert(actual.department.length>0);
  assert(matches(actual,{q:actual.name},db.org_units));assert(matches(actual,{school:'bit',org:actual.department_id},db.org_units));
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
 await import('../site/app.js?current-bit-release='+serial++);
 assert(!node('#main').innerHTML.includes('资料暂未加载'));return node;
}
for(const expected of mapping.people)test('actual BIT profile and lineage preserve '+expected.name,async()=>{
 const nodes=await render('#/person/'+expected.person_id);const html=['#main','#profile-content'].map(k=>nodes(k).innerHTML).join('\n');
 assert(html.includes(expected.name));assert(html.includes('北京理工大学'));
 const lineage=await render('#/person/'+expected.person_id+'/lineage');
 const relationHtml=['#main','#profile-content','#mind-stage'].map(k=>lineage(k).innerHTML).join('\n');
 for(const mentor of expected.mentors){assert(relationHtml.includes(mentor.name));assert(relationHtml.includes(mentor.type_label||mentor.type));}
 if(expected.mentors.length===0)assert(relationHtml.includes('0条已收录关系'));
});
const person=id=>db.people.find(p=>p.person_id===id);
const profile=async id=>{const n=await render('#/person/'+id);return n('#main').innerHTML+'\n'+n('#profile-content').innerHTML;};
test('BIT four explicit bachelor qualifications do not upgrade nine ambiguous stages',()=>{
 const approved=['bit-songtian-bachelor','bit-shanjiefei-本科','bit-liuning-education-1','bit-xuejin-education-1'];
 const unknown=['bit-songtian-doctorate','bit-shifugui-undergraduate','bit-shifugui-master','bit-shifugui-doctorate','bit-shanjiefei-硕士','bit-lumingfei-education-1','bit-liuning-education-2','bit-xuejin-education-2','bit-xuejin-education-3'];
 const edu=mapping.people.flatMap(p=>person(p.person_id).education);
 for(const id of approved){const e=edu.find(e=>e.event_id===id);assert(e);assert.equal(e.degree_awarded,true);assert.equal(e.event_kind,'degree');assert.equal(e.award_date??null,null);}
 for(const id of unknown){const e=edu.find(e=>e.event_id===id);assert(e);assert.equal(e.degree_awarded,null);}
});
test('BIT Shi preserves reviewed locator and historical workplace titles without guessing retirement',async()=>{
 const p=person('bit-shifugui');assert.equal(p.publications[0].article_number,null);assert.equal(p.publications[0].locator_as_source,'1190');
 assert(!p.appointments.slice(0,3).some(a=>String(a.title).includes('教授')));
 const html=await profile(p.person_id);assert(html.includes('1190'));assert(html.includes('退休'));assert(html.includes('至今'));
});
test('BIT actual employment sections keep institutional starts separate from undated rank',async()=>{
 const shan=person('bit-shanjiefei'),tong=person('bit-tongxuguang');
 assert.equal(shan.appointments[0].start,'2013-07');assert.equal(shan.appointments[0].title,null);
 assert.deepEqual(tong.appointments.map(a=>a.start),['2011','2018']);assert(tong.appointments.every(a=>a.title===null));
 const html=await profile(tong.person_id);assert(html.includes('具体职称未知'));assert(html.includes('教育研究院'));assert(html.includes('人文学院'));
});
test('BIT Sun explicit source award years and teaching survive with no invented job',async()=>{
 const p=person('bit-sunmiao');assert.deepEqual(p.appointments,[]);assert.equal(p.teaching[0].role,'主讲');
 const html=await profile(p.person_id);assert(html.includes('2002'));assert(html.includes('2019'));assert(html.includes('设计构成'));assert(html.includes('起点'));
});
test('BIT Lu preserves nondegree auditing, junior-college uncertainty and translated works',async()=>{
 const p=person('bit-lumingfei');assert.equal(p.education[0].degree_awarded,null);assert.equal(p.education[3].degree_awarded,false);
 assert.equal(p.teaching.length,5);assert(p.teaching.every(t=>t.role==='主讲'));assert(p.publications.every(w=>w.type==='translated_conference_paper'));
 const html=await profile(p.person_id);assert(html.includes('旁听'));assert(html.includes('译'));assert(html.includes('大学专科'));
});
test('BIT Wang teaching verb is not a professor appointment',async()=>{
 const p=person('bit-wanglang');assert.equal(p.teaching[0].name,'大学法语');assert.equal(p.teaching[0].role,'授课');
 assert(p.appointments.every(a=>a.start===null));assert(!p.appointments.some(a=>a.title==='教授'));
 const html=await profile(p.person_id);assert(html.includes('大学法语'));assert(html.includes('2015'));assert(html.includes('2019'));
});
test('BIT Liu broad civil-law coverage is not fabricated named courses',async()=>{
 const p=person('bit-liuning');assert.equal(p.teaching.length,1);assert.equal(p.teaching[0].name,'民法相关课程');assert.equal(p.education[1].degree_awarded,null);
 const html=await profile(p.person_id);assert(html.includes('民法相关课程'));assert(html.includes('硕博连读'));
});
test('BIT Xia defense, study and postdoctoral dates are not silently reconciled',async()=>{
 const p=person('bit-xiaenjun');assert.equal(p.education[2].degree_awarded,false);assert.equal(p.education[3].degree_awarded,false);
 const html=await profile(p.person_id);for(const value of ['1996-06','1997-06','1997-01','副教教授'])assert(html.includes(value),value);
});
