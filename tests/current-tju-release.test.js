import {test} from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {matches, stages, mentorOfficialUrl, mentorProfileRoute} from '../site/model.js';
const nkuMapping=JSON.parse(fs.readFileSync(new URL('./fixtures/independent-nku12-source-mapping.json',import.meta.url)));
const db=JSON.parse(fs.readFileSync(new URL('../site/atlas.json',import.meta.url)));
const roster=JSON.parse(fs.readFileSync(new URL('../site/rosters.json',import.meta.url)));
const mapping=JSON.parse(fs.readFileSync(new URL('./fixtures/independent-tju12-source-mapping.json',import.meta.url)));
test('actual TJU cohort exactly preserves independently reviewed fields, identities and scope',()=>{
 assert.equal(db.people.length,677+mapping.people.length+nkuMapping.people.length);assert.equal(db.build_id,roster.build_id);
 for(const expected of mapping.people){
  const actual=db.people.find(p=>p.person_id===expected.person_id);assert.deepEqual(actual,expected);
  assert.equal(typeof actual.department,'string');assert(actual.department.length>0);
  assert(matches(actual,{q:actual.name},db.org_units));assert(matches(actual,{school:'tju',org:actual.department_id},db.org_units));
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
 await import('../site/app.js?current-tju-release='+serial++);
 assert(!node('#main').innerHTML.includes('资料暂未加载'));return node;
}
for(const expected of mapping.people)test('actual TJU profile and lineage preserve '+expected.name,async()=>{
 const nodes=await render('#/person/'+expected.person_id);const html=['#main','#profile-content'].map(k=>nodes(k).innerHTML).join('\n');
 assert(html.includes(expected.name));assert(html.includes('天津大学'));
 const lineage=await render('#/person/'+expected.person_id+'/lineage');
 const relationHtml=['#main','#profile-content','#mind-stage'].map(k=>lineage(k).innerHTML).join('\n');
 for(const mentor of expected.mentors){assert(relationHtml.includes(mentor.name));assert(relationHtml.includes(mentor.type_label||mentor.type));}
 if(expected.mentors.length===0)assert(relationHtml.includes('0条已收录关系'));
});




test('retirement report and directory conflict remain simultaneously visible without invented effective dates',async()=>{
 const p=mapping.people.find(p=>p.person_id==='tju-chentong');assert(p.unknowns.some(value=>value.includes('两来源并存')));assert.equal(p.quick_link_eligible,false);
 const nodes=await render('#/person/'+p.person_id);const html=['#main','#profile-content'].map(k=>nodes(k).innerHTML).join('\n');
 for(const value of ['2021官网荣休报道','全职教师目录仍列名','不推返聘','不等于退休生效日','不证明教授始任1987'])assert(html.includes(value),value);
});
test('stage-specific doctoral and postdoctoral relationships do not invent a postdoctoral institution or thesis authentication',async()=>{
 const p=mapping.people.find(p=>p.person_id==='tju-zhaobohang');assert.deepEqual(p.mentors.map(m=>m.name),['张兵','张兵']);assert(p.mentors.every(m=>m.formal_dissertation_advisor_verified===false));
 const nodes=await render('#/person/'+p.person_id);const html=['#main','#profile-content'].map(k=>nodes(k).innerHTML).join('\n');assert(html.includes('博士后所在机构未明示'));
 const lineage=await render('#/person/'+p.person_id+'/lineage');const details=['#main','#profile-content'].map(k=>lineage(k).innerHTML).join('\n');for(const value of ['博士阶段指导（非论文导师认证）','博士后合作指导（非论文导师认证）'])assert(details.includes(value));
});
test('researcher title and incomplete bibliographic authorship remain explicit',async()=>{
 const nodes=await render('#/person/tju-xuchunjian');const html=['#main','#profile-content'].map(k=>nodes(k).innerHTML).join('\n');assert(html.includes('官方职称为研究员'));assert(html.includes('第二作省略作者未明示Xu'));
 const han=await render('#/person/tju-hanzhongjie');const details=['#main','#profile-content'].map(k=>han(k).innerHTML).join('\n');assert(details.includes('2019-06-03 00:23'));assert(details.includes('2024作品并存'));
});
