import {test} from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {matches, stages, mentorOfficialUrl, mentorProfileRoute} from '../site/model.js';
const tjuMapping=JSON.parse(fs.readFileSync(new URL('./fixtures/independent-tju12-source-mapping.json',import.meta.url)));
const nkuMapping=JSON.parse(fs.readFileSync(new URL('./fixtures/independent-nku12-source-mapping.json',import.meta.url)));
const db=JSON.parse(fs.readFileSync(new URL('../site/atlas.json',import.meta.url)));
const roster=JSON.parse(fs.readFileSync(new URL('../site/rosters.json',import.meta.url)));
const mapping=JSON.parse(fs.readFileSync(new URL('./fixtures/independent-bnu12-source-mapping.json',import.meta.url)));
test('actual BNU cohort exactly preserves independently reviewed fields, identities and scope',()=>{
 assert.equal(db.people.length,665+mapping.people.length+tjuMapping.people.length+nkuMapping.people.length);assert.equal(db.build_id,roster.build_id);
 for(const expected of mapping.people){
  const actual=db.people.find(p=>p.person_id===expected.person_id);assert.deepEqual(actual,expected);
  assert.equal(typeof actual.department,'string');assert(actual.department.length>0);
  assert(matches(actual,{q:actual.name},db.org_units));assert(matches(actual,{school:'bnu',org:actual.department_id},db.org_units));
  assert(!matches(actual,{school:'seu'},db.org_units));assert.equal(actual.quick_link_eligible,false);assert.equal(actual.include_in_current_faculty_count,false);
  for(const mentor of actual.mentors){assert.equal(mentorOfficialUrl(mentor),'');assert.equal(mentorProfileRoute(mentor,db.people),'');}
  for(const stage of ['bachelor','master','doctor']) for(const event of stages(actual,stage)){assert.equal(event.event_kind,'degree');assert.equal(event.degree_awarded,true);}
 }
});
let serial=0;
async function render(hash){
 const nodes=new Map(),node=k=>{if(!nodes.has(k))nodes.set(k,{innerHTML:'',textContent:'',value:'',style:{},events:{},dataset:{height:'320'},clientWidth:960,addEventListener(t,f){this.events[t]=f},click(){this.onclick?.()}});return nodes.get(k)};
 globalThis.document={querySelector:node,querySelectorAll:()=>[],getElementById:id=>node('#'+id)};
 globalThis.location={hash};globalThis.window={scrollTo(){},addEventListener(){}};
 globalThis.fetch=async p=>({ok:true,json:async()=>structuredClone(String(p).startsWith('atlas.json')?db:roster)});
 await import('../site/app.js?current-bnu-release='+serial++);
 assert(!node('#main').innerHTML.includes('资料暂未加载'));return node;
}
for(const expected of mapping.people)test('actual BNU profile and lineage preserve '+expected.name,async()=>{
 const nodes=await render('#/person/'+expected.person_id);const html=['#main','#profile-content'].map(k=>nodes(k).innerHTML).join('\n');
 assert(html.includes(expected.name));assert(html.includes('北京师范大学'));
 const lineage=await render('#/person/'+expected.person_id+'/lineage');
 const relationHtml=['#main','#profile-content','#mind-stage'].map(k=>lineage(k).innerHTML).join('\n');
 for(const mentor of expected.mentors){assert(relationHtml.includes(mentor.name));assert(relationHtml.includes(mentor.type_label||mentor.type));}
 if(expected.mentors.length===0)assert(relationHtml.includes('0条已收录关系'));
});



test('editor correction remains distinct from authorship in actual profile and canonical work',async()=>{
 const p=mapping.people.find(p=>p.person_id==='bnu-wang-cixiao-wave190');const work=p.publications.find(w=>w.title==='教育研究量表手册');
 assert.deepEqual(work.editors,['吴峰','吴红斌','王辞晓']);assert(!work.authors?.length);
 const nodes=await render('#/person/'+p.person_id);const html=['#main','#profile-content'].map(k=>nodes(k).innerHTML).join('\n');
 assert(html.includes('本书主编：吴峰、吴红斌、王辞晓'));assert(html.includes('非作者名单'));
});
test('emeritus directory fact and retained PDF limits remain visible without thesis authentication',async()=>{
 const p=mapping.people.find(p=>p.person_id==='bnu-lichong');assert.equal(p.retirement_status,'retired_or_emeritus_as_directory');assert.deepEqual(p.mentors.map(m=>m.name),['陶大镛']);
 const nodes=await render('#/person/'+p.person_id);const html=['#main','#profile-content'].map(k=>nodes(k).innerHTML).join('\n');
 for(const value of ['荣休教师目录','退休日期未知','未保留原PDF字节或核对页面视觉','总来源续读终点不代表李条目时刻'])assert(html.includes(value),value);
 const lineage=await render('#/person/'+p.person_id+'/lineage');const details=['#main','#profile-content'].map(k=>lineage(k).innerHTML).join('\n');assert(details.includes('博士阶段指导（非已核论文导师）'));
});
test('identity-held historical clue never creates a mentor and publisher metadata never claims full text',async()=>{
 const p=mapping.people.find(p=>p.person_id==='bnu-hufengqin');assert.equal(p.mentors.length,0);
 const nodes=await render('#/person/'+p.person_id);const html=['#main','#profile-content'].map(k=>nodes(k).innerHTML).join('\n');assert(html.includes('高明远'));assert(html.includes('不建师承边、不计导师'));
 const liu=await render('#/person/bnu-liushaomin');const content=['#main','#profile-content'].map(k=>liu(k).innerHTML).join('\n');assert(content.includes('HESS仅落地页元数据'));assert(content.includes('不声称重读成功或403'));assert(content.includes('2003-06仅工作起点，2007教授晋升另列'));
});
