import {test} from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {matches, stages, mentorOfficialUrl, mentorProfileRoute} from '../site/model.js';
const uestcMapping=JSON.parse(fs.readFileSync(new URL('./fixtures/independent-uestc10-source-mapping.json',import.meta.url)));
const db=JSON.parse(fs.readFileSync(new URL('../site/atlas.json',import.meta.url)));
const roster=JSON.parse(fs.readFileSync(new URL('../site/rosters.json',import.meta.url)));
const mapping=JSON.parse(fs.readFileSync(new URL('./fixtures/independent-scu11-source-mapping.json',import.meta.url)));
test('actual SCU cohort exactly preserves independently reviewed fields, identities and scope',()=>{
 assert.equal(db.people.length,634+mapping.people.length+uestcMapping.people.length);assert.equal(db.build_id,roster.build_id);
 for(const expected of mapping.people){
  const actual=db.people.find(p=>p.person_id===expected.person_id);assert.deepEqual(actual,expected);
  assert(matches(actual,{q:actual.name},db.org_units));assert(matches(actual,{school:'scu',org:actual.department_id},db.org_units));
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
 await import('../site/app.js?current-scu-release='+serial++);
 assert(!node('#main').innerHTML.includes('资料暂未加载'));return node;
}
for(const expected of mapping.people)test('actual SCU profile and lineage preserve '+expected.name,async()=>{
 const nodes=await render('#/person/'+expected.person_id);const html=['#main','#profile-content'].map(k=>nodes(k).innerHTML).join('\n');
 assert(html.includes(expected.name));assert(html.includes('四川大学'));
 const lineage=await render('#/person/'+expected.person_id+'/lineage');
 const relationHtml=['#main','#profile-content','#mind-stage'].map(k=>lineage(k).innerHTML).join('\n');
 for(const mentor of expected.mentors){assert(relationHtml.includes(mentor.name));assert(relationHtml.includes(mentor.type_label||mentor.type));}
 if(expected.mentors.length===0)assert(relationHtml.includes('0条已收录关系'));
});

test('institution work range is visible without inventing a rank appointment date',async()=>{
 const person=db.people.find(p=>p.person_id==='scu-baishibing');assert(person);
 assert.equal(person.appointments[0].start,null);assert.equal(person.career_history[0].start,'2007-07');
 const nodes=await render('#/person/'+person.person_id);const html=nodes('#profile-content').innerHTML;
 for(const fact of ['2007-07','2007-09','2009-09','机构级工作区间','晋升日期未细分','不推定兼职'])assert(html.includes(fact),fact);
});

test('specific thesis adviser statements retain official-page scope without original-thesis authentication',async()=>{
 const person=db.people.find(p=>p.person_id==='scu-penghua-classics');assert.equal(person.mentors.length,2);
 for(const mentor of person.mentors){assert.equal(mentor.formal_thesis_advisor_verified,true);assert.equal(mentor.original_thesis_examined,false);assert.equal(mentor.original_dissertation_read,false);}
 assert.equal(person.mentors.filter(m=>m.formal_doctoral_dissertation_advisor_verified===true).length,1);
 for(const education of person.education)assert.equal(education.degree_awarded_year,null);
 const nodes=await render('#/person/'+person.person_id+'/lineage');const html=['#profile-content','#mind-stage'].map(k=>nodes(k).innerHTML).join('\n');
 assert(html.includes('官网具体论文说明'));assert(html.includes('原论文未读取'));assert(html.includes('谢维扬'));
});
