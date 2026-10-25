import {test} from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {matches, stages, mentorOfficialUrl, mentorProfileRoute} from '../site/model.js';
const hnuMapping=JSON.parse(fs.readFileSync(new URL('./fixtures/independent-hnu10-source-mapping.json',import.meta.url)));
const bnuMapping=JSON.parse(fs.readFileSync(new URL('./fixtures/independent-bnu12-source-mapping.json',import.meta.url)));
const tjuMapping=JSON.parse(fs.readFileSync(new URL('./fixtures/independent-tju12-source-mapping.json',import.meta.url)));
const nkuMapping=JSON.parse(fs.readFileSync(new URL('./fixtures/independent-nku12-source-mapping.json',import.meta.url)));
const dlutMapping=JSON.parse(fs.readFileSync(new URL('./fixtures/independent-dlut12-source-mapping.json',import.meta.url)));
const jluMapping=JSON.parse(fs.readFileSync(new URL('./fixtures/independent-jlu12-source-mapping.json',import.meta.url)));
const db=JSON.parse(fs.readFileSync(new URL('../site/atlas.json',import.meta.url)));
const roster=JSON.parse(fs.readFileSync(new URL('../site/rosters.json',import.meta.url)));
const mapping=JSON.parse(fs.readFileSync(new URL('./fixtures/independent-uestc10-source-mapping.json',import.meta.url)));
test('actual UESTC cohort exactly preserves independently reviewed fields, identities and scope',()=>{
 assert.equal(db.people.length,645+mapping.people.length+hnuMapping.people.length+bnuMapping.people.length+tjuMapping.people.length+nkuMapping.people.length+dlutMapping.people.length+jluMapping.people.length);assert.equal(db.build_id,roster.build_id);
 for(const expected of mapping.people){
  const actual=db.people.find(p=>p.person_id===expected.person_id);assert.deepEqual(actual,expected);
  assert(matches(actual,{q:actual.name},db.org_units));assert(matches(actual,{school:'uestc',org:actual.department_id},db.org_units));
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
 await import('../site/app.js?current-uestc-release='+serial++);
 assert(!node('#main').innerHTML.includes('资料暂未加载'));return node;
}
for(const expected of mapping.people)test('actual UESTC profile and lineage preserve '+expected.name,async()=>{
 const nodes=await render('#/person/'+expected.person_id);const html=['#main','#profile-content'].map(k=>nodes(k).innerHTML).join('\n');
 assert(html.includes(expected.name));assert(html.includes('电子科技大学'));
 for(const a of expected.appointments){assert(html.includes(a.title));if(!a.institution)assert(html.includes('任职机构未核实'));}
 assert.equal(expected.mentors.length,0);
 const lineage=await render('#/person/'+expected.person_id+'/lineage');
 const relationHtml=['#main','#profile-content','#mind-stage'].map(k=>lineage(k).innerHTML).join('\n');
 for(const mentor of expected.mentors){assert(relationHtml.includes(mentor.name));assert(relationHtml.includes(mentor.type_label||mentor.type));}
 if(expected.mentors.length===0)assert(relationHtml.includes('0条已收录关系'));
});


test('source career facts remain visible without inventing employer or professorship start',async()=>{
 const shang=mapping.people.find(p=>p.person_id==='uestc-shangjizheng');
 assert.deepEqual(shang.appointments.map(a=>[a.start,a.title,a.institution]),[['2006','副教授',null],['2013','教授',null]]);
 const fang=mapping.people.find(p=>p.person_id==='uestc-fangjiaming');
 assert(fang.appointments.some(a=>a.start==='2009-12'&&a.title.includes('任教')));
 assert(fang.appointments.some(a=>a.start==='2019-07'&&a.title==='教授'));
 assert(!fang.appointments.some(a=>a.start==='2009-12'&&a.title==='教授'));
 const nodes=await render('#/person/uestc-fangjiaming');const html=['#main','#profile-content'].map(k=>nodes(k).innerHTML).join('\n');
 assert(html.includes('此日期是任教起点，不当成教授任职起点'));
 assert.equal(fang.professional_qualifications[0].start,'2018-06');
 assert(!fang.appointments.some(a=>a.record_kind==='supervision_qualification'));
 assert(html.includes('2018年6月评为博士生导师'));assert(html.includes('不是任职或本人的师承'));
});

test('reviewed career dates, professional qualifications and research labels are actually visible',async()=>{
 for(const [id,labels] of [
  ['uestc-liangjian',['2023-07-14','不作为副教授职称晋升日期']],
  ['uestc-nidebing',['2010.12','不新增劳动任职、学位获授或本人的导师关系']],
  ['uestc-kangjian',['公共服务与共同富裕']]
 ]){
  const nodes=await render('#/person/'+id);const html=['#main','#profile-content'].map(k=>nodes(k).innerHTML).join('\n');
  for(const label of labels)assert(html.includes(label),id+': '+label);
 }
});
