import {test} from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {matches, stages, mentorOfficialUrl, mentorProfileRoute} from '../site/model.js';
const bnuMapping=JSON.parse(fs.readFileSync(new URL('./fixtures/independent-bnu12-source-mapping.json',import.meta.url)));
const tjuMapping=JSON.parse(fs.readFileSync(new URL('./fixtures/independent-tju12-source-mapping.json',import.meta.url)));
const nkuMapping=JSON.parse(fs.readFileSync(new URL('./fixtures/independent-nku12-source-mapping.json',import.meta.url)));
const dlutMapping=JSON.parse(fs.readFileSync(new URL('./fixtures/independent-dlut12-source-mapping.json',import.meta.url)));
const jluMapping=JSON.parse(fs.readFileSync(new URL('./fixtures/independent-jlu12-source-mapping.json',import.meta.url)));
const sduMapping=JSON.parse(fs.readFileSync(new URL('./fixtures/independent-sdu12-source-mapping.json',import.meta.url)));
const csuMapping=JSON.parse(fs.readFileSync(new URL('./fixtures/independent-csu12-source-mapping.json',import.meta.url)));
const hustMapping=JSON.parse(fs.readFileSync(new URL('./fixtures/independent-hust12-source-mapping.json',import.meta.url)));
const whuMapping=JSON.parse(fs.readFileSync(new URL('./fixtures/independent-whu9-source-mapping.json',import.meta.url)));
const xjtuMapping=JSON.parse(fs.readFileSync(new URL('./fixtures/independent-xjtu12-source-mapping.json',import.meta.url)));
const rucMapping=JSON.parse(fs.readFileSync(new URL('./fixtures/independent-ruc8-source-mapping.json',import.meta.url)));
const ecnuMapping=JSON.parse(fs.readFileSync(new URL('./fixtures/independent-ecnu12-source-mapping.json',import.meta.url)));
const buaaMapping=JSON.parse(fs.readFileSync(new URL('./fixtures/independent-buaa12-source-mapping.json',import.meta.url)));
const tongjiMapping=JSON.parse(fs.readFileSync(new URL('./fixtures/independent-tongji12-source-mapping.json',import.meta.url)));
const bitMapping=JSON.parse(fs.readFileSync(new URL('./fixtures/independent-bit12-source-mapping.json',import.meta.url)));
const nwpuMapping=JSON.parse(fs.readFileSync(new URL('./fixtures/independent-nwpu12-source-mapping.json',import.meta.url)));
const db=JSON.parse(fs.readFileSync(new URL('../site/atlas.json',import.meta.url)));
const roster=JSON.parse(fs.readFileSync(new URL('../site/rosters.json',import.meta.url)));
const mapping=JSON.parse(fs.readFileSync(new URL('./fixtures/independent-hnu10-source-mapping.json',import.meta.url)));
test('actual HNU cohort exactly preserves independently reviewed fields, identities and scope',()=>{
 assert.equal(db.people.length,655+mapping.people.length+bnuMapping.people.length+tjuMapping.people.length+nkuMapping.people.length+dlutMapping.people.length+jluMapping.people.length+sduMapping.people.length+csuMapping.people.length+hustMapping.people.length+whuMapping.people.length+xjtuMapping.people.length+rucMapping.people.length+ecnuMapping.people.length+buaaMapping.people.length+tongjiMapping.people.length+bitMapping.people.length+nwpuMapping.people.length);assert.equal(db.build_id,roster.build_id);
 for(const expected of mapping.people){
  const actual=db.people.find(p=>p.person_id===expected.person_id);assert.deepEqual(actual,expected);
  assert(matches(actual,{q:actual.name},db.org_units));assert(matches(actual,{school:'hnu',org:actual.department_id},db.org_units));
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
 await import('../site/app.js?current-hnu-release='+serial++);
 assert(!node('#main').innerHTML.includes('资料暂未加载'));return node;
}
for(const expected of mapping.people)test('actual HNU profile and lineage preserve '+expected.name,async()=>{
 const nodes=await render('#/person/'+expected.person_id);const html=['#main','#profile-content'].map(k=>nodes(k).innerHTML).join('\n');
 assert(html.includes(expected.name));assert(html.includes('湖南大学'));
 const lineage=await render('#/person/'+expected.person_id+'/lineage');
 const relationHtml=['#main','#profile-content','#mind-stage'].map(k=>lineage(k).innerHTML).join('\n');
 for(const mentor of expected.mentors){assert(relationHtml.includes(mentor.name));assert(relationHtml.includes(mentor.type_label||mentor.type));}
 if(expected.mentors.length===0)assert(relationHtml.includes('0条已收录关系'));
});


test('actual PDF evidence scope and work/promotion dates stay visibly separate',async()=>{
 const p=mapping.people.find(p=>p.person_id==='hnu-yuanzhaohui-architecture');
 const nodes=await render('#/person/'+p.person_id);const html=['#main','#profile-content'].map(k=>nodes(k).innerHTML).join('\n');
 assert(html.includes('无原PDF字节留存或视觉认证'));
 assert(html.includes('不能当PDF发布日期'));
 assert(html.includes('不造2014年教授任命'));
 assert(p.education.some(e=>e.degree_awarded===false));
 assert(p.mentors.every(m=>m.formal_thesis_advisor_verified===false));
});
test('official thesis statement does not claim original-paper reading or cross-date employment continuity',async()=>{
 const p=mapping.people.find(p=>p.person_id==='hnu-libing-education-history');
 assert.equal(p.mentors.length,1);assert(p.education.every(e=>e.degree_awarded!==true));
 const nodes=await render('#/person/'+p.person_id);const html=['#main','#profile-content'].map(k=>nodes(k).innerHTML).join('\n');
 for(const value of ['2022年个人页','2020年新书作者简介','不推转任','未读原论文'])assert(html.includes(value),value);
 const lineage=await render('#/person/'+p.person_id+'/lineage');const details=['#main','#profile-content'].map(k=>lineage(k).innerHTML).join('\n');
 assert(details.includes('刘海峰'));assert(details.includes('未读取原论文'));
});
test('visiting inviter never becomes a thesis mentor and research-supervision qualification is not an appointment',async()=>{
 const sun=mapping.people.find(p=>p.person_id==='hnu-sunqingjuan');assert.deepEqual(sun.mentors.map(m=>m.name),['李晨阳']);
 const nodes=await render('#/person/'+sun.person_id+'/lineage');const html=['#main','#profile-content'].map(k=>nodes(k).innerHTML).join('\n');
 assert(html.includes('沈清松'));assert(html.includes('访问邀请人'));
 const liu=mapping.people.find(p=>p.person_id==='hnu-liujie');assert(!liu.appointments.some(a=>a.title.includes('硕士研究生导师')));
 const profile=await render('#/person/'+liu.person_id);assert(profile('#profile-content').innerHTML.includes('2010年7月担任硕士研究生导师'));
});
