import {test} from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {matches, stages, mentorOfficialUrl, mentorProfileRoute} from '../site/model.js';
const db=JSON.parse(fs.readFileSync(new URL('../site/atlas.json',import.meta.url)));
const roster=JSON.parse(fs.readFileSync(new URL('../site/rosters.json',import.meta.url)));
const mapping=JSON.parse(fs.readFileSync(new URL('./fixtures/independent-nwpu12-source-mapping.json',import.meta.url)));
test('actual NWPU cohort exactly preserves independently reviewed fields, identities and scope',()=>{
 assert.equal(db.people.length,838+mapping.people.length);assert.equal(db.build_id,roster.build_id);
 for(const expected of mapping.people){
  const actual=db.people.find(p=>p.person_id===expected.person_id);assert.deepEqual(actual,expected);
  assert.equal(typeof actual.department,'string');assert(actual.department.length>0);
  assert(matches(actual,{q:actual.name},db.org_units));assert(matches(actual,{school:'nwpu',org:actual.department_id},db.org_units));
  assert(!matches(actual,{school:'seu'},db.org_units));assert.equal(actual.quick_link_eligible,expected.quick_link_eligible);assert.equal(actual.include_in_current_faculty_count,expected.include_in_current_faculty_count);
  for(const stage of ['bachelor','master','doctor']) for(const event of stages(actual,stage)){assert.equal(event.event_kind,'degree');assert.equal(event.degree_awarded,true);}
 }
});
let serial=0;
async function render(hash){
 const nodes=new Map(),node=k=>{if(!nodes.has(k))nodes.set(k,{innerHTML:'',textContent:'',value:'',style:{},events:{},dataset:{height:'320'},clientWidth:960,addEventListener(t,f){this.events[t]=f},click(){this.onclick?.()}});return nodes.get(k)};
 globalThis.document={querySelector:node,querySelectorAll:()=>[],getElementById:id=>node('#'+id)};
 globalThis.location={hash};globalThis.window={scrollTo(){},addEventListener(){}};
 globalThis.fetch=async p=>({ok:true,json:async()=>structuredClone(String(p).startsWith('atlas.json')?db:roster)});
 await import('../site/app.js?current-nwpu-release='+serial++);
 assert(!node('#main').innerHTML.includes('资料暂未加载'));return node;
}
for(const expected of mapping.people)test('actual NWPU profile and lineage preserve '+expected.name,async()=>{
 const nodes=await render('#/person/'+expected.person_id);const html=['#main','#profile-content'].map(k=>nodes(k).innerHTML).join('\n');
 assert(html.includes(expected.name));assert(html.includes('西北工业大学'));
 const lineage=await render('#/person/'+expected.person_id+'/lineage');
 const relationHtml=['#main','#profile-content','#mind-stage'].map(k=>lineage(k).innerHTML).join('\n');
 for(const mentor of expected.mentors){assert(relationHtml.includes(mentor.name));assert(relationHtml.includes(mentor.type_label||mentor.type));}
 if(expected.mentors.length===0)assert(relationHtml.includes('0条已收录关系'));
});
const person=id=>db.people.find(p=>p.person_id===id);
const profile=async id=>{const n=await render('#/person/'+id);return n('#main').innerHTML+'\n'+n('#profile-content').innerHTML;};
test('NWPU seven source-supported event degrees do not upgrade eight ambiguous events',()=>{
 const yes=['nwpu-heyibai-bachelor','nwpu-heyibai-doctorate','nwpu-songdingbonan-本科','nwpu-songdingbonan-硕士','nwpu-songdingbonan-博士','nwpu-zhengye-education-1','nwpu-sunxiaodi-education-1'];
 const no=['nwpu-heyibai-master','nwpu-dai-study-2001','nwpu-dai-master-study','nwpu-zhaoxueai-本科','nwpu-zhaoxueai-研究生','nwpu-fupengyu-beijing-graduation','nwpu-sunhao-applied-statistics-education-2','nwpu-yangkunde-education-1'];
 const edu=mapping.people.flatMap(p=>person(p.person_id).education);
 for(const id of yes){const e=edu.find(e=>e.event_id===id);assert(e);assert.equal(e.degree_awarded,true);assert.equal(e.event_kind,'degree');assert.equal(e.degree_awarded_date??null,null);}
 for(const id of no){const e=edu.find(e=>e.event_id===id);assert(e);assert.equal(e.degree_awarded,null);}
});
test('NWPU unbound person credentials do not fabricate a degree event or awarding school',async()=>{
 const z=person('nwpu-zhaoxueai'),f=person('nwpu-fupengyu');assert.equal(z.education.length,3);assert.equal(f.education.length,2);
 for(const p of [z,f]){const c=p.credential_labels_as_source;assert.equal(c.degree_awarded,true);assert.equal(c.source_degree_awarded,null);assert.equal(c.institution,null);assert.equal(c.date,null);assert.equal(c.fact_scope,'person_level_degree_identity_without_event_institution_or_date_binding');}
 assert(z.education.slice(0,2).every(e=>e.degree_awarded===null));assert.equal(f.education[0].degree_awarded,null);assert.equal(f.education[1].degree_awarded,false);
 const zh=await profile(z.person_id),fh=await profile(f.person_id);
 for(const t of ['研究生班毕业','文学学士','未绑定'])assert(zh.includes(t),t);
 for(const t of ['北京体育大学','运动人体科学','博士后','不将其绑定'])assert(fh.includes(t),t);
});
test('NWPU Sun Hao preserves an explicit award month and rejects an unrealized postdoc',async()=>{
 const p=person('nwpu-sunhao-applied-statistics'),e=p.education.find(e=>e.event_id.endsWith('education-3'));
 assert.equal(e.degree_awarded_date,'2003-06');assert.equal(e.end,null);assert.equal(p.education.length,3);assert.equal(p.education[0].degree_awarded,false);assert.equal(p.education[1].degree_awarded,null);
 assert.equal(p.teaching.length,5);assert.equal(p.mentors.length,1);
 const html=await profile(p.person_id);for(const s of ['2003-06','未发生博士后'])assert(html.includes(s),s);
 const lineage=await render('#/person/'+p.person_id+'/lineage');const relationHtml=['#main','#profile-content','#mind-stage'].map(k=>lineage(k).innerHTML).join('\n');assert(relationHtml.includes('赵选民'));assert(relationHtml.includes('硕士阶段导师'));
 const org=db.org_units.find(o=>o.id===p.department_id);assert.equal(org.name,'应用概率统计系');assert.equal(org.parent_id,'nwpu-math-stat');assert.equal(org.source_parent_id,null);
});
test('NWPU Sun Xiaodi unknown-stage guidance is not bound to doctorate',async()=>{
 const p=person('nwpu-sunxiaodi');assert.equal(p.mentors.length,1);assert(p.mentors[0].type_label.includes('阶段未知'));assert.equal(p.appointments.length,0);
 const n=await render('#/person/'+p.person_id+'/lineage'),html=['#main','#profile-content','#mind-stage'].map(k=>n(k).innerHTML).join('\n');assert(html.includes('罗艺峰'));assert(html.includes('阶段未知'));
 const ph=await profile(p.person_id);for(const s of ['终南山','非论文','叶明春'])assert(ph.includes(s),s);
});
test('NWPU Zheng thesis-specific official claim does not claim original thesis authentication',async()=>{
 const p=person('nwpu-zhengye');assert.equal(p.mentors.length,1);assert.equal(p.mentors[0].name,'吴建南');assert(p.mentors[0].type_label.includes('博士论文'));
 assert.equal(p.teaching[0].role,'主持课程建设项目');const html=await profile(p.person_id);for(const t of ['原论文','2024','2025','课程建设'])assert(html.includes(t),t);
});
test('NWPU Yang preserves source degree years without inheriting an awarding institution',async()=>{
 const p=person('nwpu-yangkunde');assert.equal(p.education[0].degree_awarded,null);assert.equal(p.mentors.length,2);
 for(const e of p.education.slice(1)){assert.equal(e.degree_awarded,true);assert.equal(e.institution,null);}
 const html=await profile(p.person_id);for(const t of ['1999','2003','2004','不新造学位'])assert(html.includes(t),t);
});
test('NWPU Dai admitted study, doctorate and joint training preserve distinct evidence',async()=>{
 const p=person('nwpu-dai-yuchao');assert.equal(p.education.length,5);assert.equal(p.mentors.length,2);assert.equal(p.education[0].degree_awarded,null);assert.equal(p.education[1].degree_awarded,null);assert.equal(p.education[2].degree_awarded,true);assert.equal(p.education[3].degree_awarded,false);
 assert.equal(p.mentors[0].education_event_id,'nwpu-dai-master-study');assert.equal(p.mentors[1].education_event_id,'nwpu-dai-joint-training');
 const html=await profile(p.person_id);for(const t of ['2001','2005','联合培养'])assert(html.includes(t),t);
});
test('NWPU Fu textbooks remain contributions not sole authorship or invented publication year',async()=>{
 const p=person('nwpu-fupengyu');assert.equal(p.publications.length,2);for(const w of p.publications){assert(w.note.includes('参编'));assert.equal(w.year??null,null);}
 const html=await profile(p.person_id);for(const t of ['体育与健康','跆拳道教程','参编','全校本科生必修教材'])assert(html.includes(t),t);
});
