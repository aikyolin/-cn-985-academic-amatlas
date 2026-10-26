import {readAtlasFile,createAtlasFetch} from './atlas-test-io.js';
import {test} from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {matches, stages, mentorOfficialUrl, mentorProfileRoute} from '../site/model.js';
const rucMapping=JSON.parse(fs.readFileSync(new URL('./fixtures/independent-ruc8-source-mapping.json',import.meta.url)));
const ecnuMapping=JSON.parse(fs.readFileSync(new URL('./fixtures/independent-ecnu12-source-mapping.json',import.meta.url)));
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
const mapping=JSON.parse(fs.readFileSync(new URL('./fixtures/independent-xjtu12-source-mapping.json',import.meta.url)));
test('actual XJTU cohort exactly preserves independently reviewed fields, identities and scope',()=>{
 assert.equal(db.people.length,770+mapping.people.length+rucMapping.people.length+ecnuMapping.people.length+buaaMapping.people.length+tongjiMapping.people.length+bitMapping.people.length+nwpuMapping.people.length+scutMapping.people.length+ustcMapping.people.length+cauMapping.people.length+fduMapping.people.length+mucMapping.people.length+nwsuafMapping.people.length+oucMapping.people.length);assert.equal(db.build_id,roster.build_id);
 for(const expected of mapping.people){
  const actual=db.people.find(p=>p.person_id===expected.person_id);assert.deepEqual(actual,expected);
  assert.equal(typeof actual.department,'string');assert(actual.department.length>0);
  assert(matches(actual,{q:actual.name},db.org_units));assert(matches(actual,{school:'xjtu',org:actual.department_id},db.org_units));
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
 await import('../site/app.js?current-xjtu-release='+serial++);
 assert(!node('#main').innerHTML.includes('资料暂未加载'));return node;
}
for(const expected of mapping.people)test('actual XJTU profile and lineage preserve '+expected.name,async()=>{
 const nodes=await render('#/person/'+expected.person_id);const html=['#main','#profile-content'].map(k=>nodes(k).innerHTML).join('\n');
 assert(html.includes(expected.name));assert(html.includes('西安交通大学'));
 const lineage=await render('#/person/'+expected.person_id+'/lineage');
 const relationHtml=['#main','#profile-content','#mind-stage'].map(k=>lineage(k).innerHTML).join('\n');
 for(const mentor of expected.mentors){assert(relationHtml.includes(mentor.name));assert(relationHtml.includes(mentor.type_label||mentor.type));}
 if(expected.mentors.length===0)assert(relationHtml.includes('0条已收录关系'));
});

const person=id=>db.people.find(p=>p.person_id===id);
const htmlOf=nodes=>['#main','#profile-content','#mind-stage'].map(k=>nodes(k).innerHTML).join('\n');
test('XJTU source-supported classification totals remain explicit, not completeness claims',()=>{
 const events=mapping.people.flatMap(p=>p.education);assert.equal(events.length,47);
 assert.equal(events.filter(e=>e.degree_awarded===true).length,26);assert.equal(events.filter(e=>e.degree_awarded===false).length,12);assert.equal(events.filter(e=>e.degree_awarded===null).length,9);
 assert.equal(mapping.people.reduce((n,p)=>n+p.mentors.length,0),13);
 assert.equal(mapping.people.reduce((n,p)=>n+p.teaching.length,0),7);
});
test('only five reviewed null classifications become source-reported awards with old value retained',()=>{
 const ids=['shan-sysu-bachelor','xjtu-peileilei-education-3','xjtu-zhoumi-education-1','xjtu-zhoumi-education-2','xjtu-zhoumi-education-3'];
 const events=mapping.people.flatMap(p=>p.education),changed=events.filter(e=>e.source_degree_awarded===null&&e.degree_awarded===true);
 assert.deepEqual(changed.map(e=>e.event_id).sort(),ids.sort());
 for(const e of changed){assert.equal(e.event_kind,'degree');for(const k of ['award_year','award_date','degree_awarded_year','degree_awarded_date'])if(k in e)assert.equal(e[k],null);}
});
test('Shan master remains reported study and two separately evidenced doctorates are not merged',async()=>{
 const p=person('xjtu-shan-wenhua'),e=p.education.find(e=>e.event_id==='shan-jinan-master');assert.equal(e.degree_awarded,null);assert.equal(e.event_kind,'degree_study');
 assert.equal(p.education.filter(e=>e.degree==='法学博士'&&e.degree_awarded===true).length,2);
 const html=htmlOf(await render('#/person/'+p.person_id));for(const text of ['暨南大学','授位未单独核实','剑桥大学','厦门大学','1996'])assert(html.includes(text),text);
});
test('Luo three thesis-specific relations remain source-reported, only one doctoral, not original-document verification',async()=>{
 const p=person('xjtu-luojiu');assert.equal(p.mentors.length,3);assert.equal(p.mentors.filter(m=>m.formal_dissertation_advisor===true).length,1);
 for(const m of p.mentors){assert.equal(m.formal_degree_thesis_advisor,true);assert.equal(m.original_thesis_document_verified,false);assert(m.thesis_title_as_source);}
 const html=htmlOf(await render('#/person/'+p.person_id+'/lineage'));for(const text of ['张汝伦','何卫平','苏树华','博士学位论文导师','硕士学位论文导师','本科学位论文导师'])assert(html.includes(text),text);
});
test('Yao university joining month does not backdate lecturer appointment on actual timeline',async()=>{
 const p=person('xjtu-yao-xiuying-wave168');assert.equal(p.appointments.length,1);const a=p.appointments[0];assert.equal(a.title,'讲师');assert.equal(a.start,null);assert.equal(a.university_employment_start,'2006-07');
 const html=htmlOf(await render('#/person/'+p.person_id));assert(html.includes('2006年7'));assert(html.includes('讲师'));const job=html.match(/<div class="time">([^<]*)<\/div><h3>讲师<\/h3>/);assert(job);assert(!job[1].includes('2006'));
});
test('Shang single years and grouped teaching remain visible without converting MBA training to degree',async()=>{
 const p=person('xjtu-shangyufan-organization');assert.equal(p.education.filter(e=>e.degree_awarded===null).length,3);assert.equal(p.education.filter(e=>e.degree_awarded===false).length,3);
 assert.equal(p.teaching.length,1);assert.equal(p.teaching[0].role,'讲授');assert.equal(p.teaching[0].courses.length,3);
 const html=htmlOf(await render('#/person/'+p.person_id));for(const text of ['1993','1996','2003','MBA','本科生和研究生','组织行为学','人力资源管理','管理思维与管理沟通'])assert(html.includes(text),text);
});
test('Yu explicit employment and four distinct study guidance relations retain source time limits and full role',async()=>{
 const p=person('xjtu-yuyan');assert.equal(p.mentors.length,4);assert.equal(p.appointments.length,5);
 assert(p.appointments.some(a=>a.start==='1991-07'));assert.equal(p.education.filter(e=>e.degree_awarded===false).length,2);
 const html=htmlOf(await render('#/person/'+p.person_id));for(const text of ['营养与食品安全系主任','博士生导师','2015','2018'])assert(html.includes(text),text);
 const lineage=htmlOf(await render('#/person/'+p.person_id+'/lineage'));for(const m of p.mentors)assert(lineage.includes(m.name));
});
test('Zhou degree-associated years remain visible and Zhu empty selected bibliography is not all-page absence',async()=>{
 const p=person('xjtu-zhoumi-organization');const html=htmlOf(await render('#/person/'+p.person_id));for(const text of ['1992','1998','2007','Pemplin'])assert(html.includes(text),text);
 const z=person('xjtu-zhuzhengwei');assert.equal(z.publications.length,0);const zhtml=htmlOf(await render('#/person/'+z.person_id));assert(zhtml.includes('不据此断言完整页面'));
});
test('Xu NUS ambiguity remains one nondegree event and lecturer versus assistant-professor conflict remains visible',async()=>{
 const p=person('xjtu-xu-yubin');assert.equal(p.education.length,3);assert.equal(p.education.filter(e=>e.degree_awarded===false).length,1);
 const html=htmlOf(await render('#/person/'+p.person_id));for(const text of ['讲师','助理教授','NUS','次数未知'])assert(html.includes(text),text);
});
test('Feng explicitly taught courses retain role while unsupported course levels stay unassigned',async()=>{
 const p=person('xjtu-fenggenfu');assert.equal(p.teaching.length,3);assert(p.teaching.every(t=>t.role==='主讲'));
 const html=htmlOf(await render('#/person/'+p.person_id));for(const t of p.teaching)assert(html.includes(t.course));assert(html.includes('主讲'));
});
