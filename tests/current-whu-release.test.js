import {test} from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {matches, stages, mentorOfficialUrl, mentorProfileRoute} from '../site/model.js';
const xjtuMapping=JSON.parse(fs.readFileSync(new URL('./fixtures/independent-xjtu12-source-mapping.json',import.meta.url)));
const rucMapping=JSON.parse(fs.readFileSync(new URL('./fixtures/independent-ruc8-source-mapping.json',import.meta.url)));
const ecnuMapping=JSON.parse(fs.readFileSync(new URL('./fixtures/independent-ecnu12-source-mapping.json',import.meta.url)));
const db=JSON.parse(fs.readFileSync(new URL('../site/atlas.json',import.meta.url)));
const roster=JSON.parse(fs.readFileSync(new URL('../site/rosters.json',import.meta.url)));
const mapping=JSON.parse(fs.readFileSync(new URL('./fixtures/independent-whu9-source-mapping.json',import.meta.url)));
test('actual WHU cohort exactly preserves independently reviewed fields, identities and scope',()=>{
 assert.equal(db.people.length,761+mapping.people.length+xjtuMapping.people.length+rucMapping.people.length+ecnuMapping.people.length);assert.equal(db.build_id,roster.build_id);
 for(const expected of mapping.people){
  const actual=db.people.find(p=>p.person_id===expected.person_id);assert.deepEqual(actual,expected);
  assert.equal(typeof actual.department,'string');assert(actual.department.length>0);
  assert(matches(actual,{q:actual.name},db.org_units));assert(matches(actual,{school:'whu',org:actual.department_id},db.org_units));
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
 await import('../site/app.js?current-whu-release='+serial++);
 assert(!node('#main').innerHTML.includes('资料暂未加载'));return node;
}
for(const expected of mapping.people)test('actual WHU profile and lineage preserve '+expected.name,async()=>{
 const nodes=await render('#/person/'+expected.person_id);const html=['#main','#profile-content'].map(k=>nodes(k).innerHTML).join('\n');
 assert(html.includes(expected.name));assert(html.includes('武汉大学'));
 const lineage=await render('#/person/'+expected.person_id+'/lineage');
 const relationHtml=['#main','#profile-content','#mind-stage'].map(k=>lineage(k).innerHTML).join('\n');
 for(const mentor of expected.mentors){assert(relationHtml.includes(mentor.name));assert(relationHtml.includes(mentor.type_label||mentor.type));}
 if(expected.mentors.length===0)assert(relationHtml.includes('0条已收录关系'));
});






test('nine explicit source-reported degree corrections preserve old classification and unknown award dates',()=>{
 const corrected={'whu-yufeng':[1,2],'whu-wangliuquan':[1,2],'whu-wanghaowu':[1,2],'whu-weibin':[1,2],'whu-mazhaocheng':[2]};let count=0;
 for(const [id,indices] of Object.entries(corrected)){const p=db.people.find(p=>p.person_id===id);for(const i of indices){const e=p.education.find(e=>e.event_id===id+'-education-'+i);assert(e);assert.equal(e.degree_awarded,true);assert.equal(e.source_degree_awarded,null);assert.equal(e.event_kind,'degree');const keys=['degree_awarded_date','degree_award_date','award_date','degree_awarded_year','award_year'].filter(k=>k in e);assert(keys.length>0);for(const k of keys)assert.equal(e[k],null,id+' '+k);count++;}}
 assert.equal(count,9);
});
test('four ambiguous degree or study classifications remain unknown without denying reported stages',async()=>{
 for(const [id,indices] of [['whu-weibin',[3]],['whu-mazhaocheng',[1]],['whu-miaoxiaoping',[1,2]]]){const p=db.people.find(p=>p.person_id===id);for(const i of indices)assert.equal(p.education.find(e=>e.event_id===id+'-education-'+i).degree_awarded,null);}
 const p=db.people.find(p=>p.person_id==='whu-mazhaocheng');assert.equal(p.education.filter(e=>e.degree==='本科双学位').length,1);const n=await render('#/person/'+p.person_id),h=n('#main').innerHTML+n('#profile-content').innerHTML;assert(h.includes('研究生毕业'));assert(h.includes('双学位'));
});
test('math uses the existing department and preserves all three earlier members',()=>{
 assert.equal(db.org_units.filter(o=>o.id==='whu-math-stat').length,1);const members=db.people.filter(p=>p.department_id==='whu-math-stat').map(p=>p.person_id);assert.deepEqual(members,['whu-anfengwen','whu-aoweiwei','whu-chenguoxian','whu-wangliuquan','whu-wanghaowu']);
});
test('mixed doctoral subject labels and joint training do not create a second doctorate',async()=>{
 const p=db.people.find(p=>p.person_id==='whu-yufeng');assert.equal(stages(p,'doctor').length,1);assert.equal(p.education.find(e=>e.event_id==='whu-yufeng-education-4').degree_awarded,false);const n=await render('#/person/'+p.person_id),h=n('#main').innerHTML+n('#profile-content').innerHTML;for(const q of ['社会心理学','社会学','法学博士','联合培养'])assert(h.includes(q));
});
test('historical teaching and promotions remain distinct from doctoral-supervisor qualification',async()=>{
 const p=db.people.find(p=>p.person_id==='whu-zhaolin');assert.equal(p.appointments.length,4);assert.deepEqual(p.appointments.map(a=>a.start),['1985','1988','1993','1997']);assert.equal(p.mentors.length,0);const n=await render('#/person/'+p.person_id),h=n('#main').innerHTML+n('#profile-content').innerHTML;assert(h.includes('1999'));assert(h.includes('独立资格'));assert(h.includes('不分配'));
});
test('combined study range and unclassified Japan stay do not create precise award dates or visiting classification',async()=>{
 const p=db.people.find(p=>p.person_id==='whu-weibin');const e=p.education.find(e=>e.event_id==='whu-weibin-education-3');assert.equal(e.degree_awarded,null);const n=await render('#/person/'+p.person_id),h=n('#main').innerHTML+n('#profile-content').innerHTML;for(const q of ['1994–2004','2007–2009','德岛大学','不分配'])assert(h.includes(q));assert.equal(p.publications.find(w=>w.title==='古代长江中游社会研究').type,'edited_book');
});
test('three unknown institution intervals do not render as confirmed employment and remain fully visible',async()=>{
 const p=db.people.find(p=>p.person_id==='whu-miaoxiaoping');assert.equal(p.institutional_associations.length,3);assert.equal(p.appointments.length,1);assert.equal(p.appointments[0].title,'院长');const n=await render('#/person/'+p.person_id),h=n('#main').innerHTML+n('#profile-content').innerHTML;assert(!h.includes('<h3>任职</h3>'));
 const esc=v=>String(v).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
 for(const a of p.institutional_associations){assert.equal(a.title,null);const note=p.unknowns.find(u=>u.includes(a.start)&&u.includes(a.end)&&u.includes(a.institution));assert(note,a.start);assert(h.includes(esc(note)),a.start);assert(note.includes('未知')||note.includes('未核'));}
});
test('retained public-health history and truncated-source boundaries are not lost or inflated into full publications',async()=>{
 const p=db.people.find(p=>p.person_id==='whu-yuanbifeng-publichealth');assert.equal(p.publications.length,0);assert.equal(p.mentors.length,0);const n=await render('#/person/'+p.person_id),h=n('#main').innerHTML+n('#profile-content').innerHTML;assert(h.includes('2011'));assert(h.includes('2021'));assert(h.includes('化学'));assert(h.includes('编委'));assert(h.includes('截断'));assert(h.includes('不等'));
});
