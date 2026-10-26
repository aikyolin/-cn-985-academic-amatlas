import {createImmutableCohortRenderer} from './immutable-cohort-renderer.js';
import {readAtlasFile,createAtlasFetch} from './atlas-test-io.js';
import {test} from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {matches, stages, mentorOfficialUrl, mentorProfileRoute, escapeHtml} from '../site/model.js';
const cauMapping=JSON.parse(fs.readFileSync(new URL('./fixtures/independent-cau12-source-mapping.json',import.meta.url)));
const fduMapping=JSON.parse(fs.readFileSync(new URL('./fixtures/independent-fdu12-source-mapping.json',import.meta.url)));
const mucMapping=JSON.parse(fs.readFileSync(new URL('./fixtures/independent-muc12-source-mapping.json',import.meta.url)));
const nwsuafMapping=JSON.parse(fs.readFileSync(new URL('./fixtures/independent-nwsuaf12-source-mapping.json',import.meta.url)));
const oucMapping=JSON.parse(fs.readFileSync(new URL('./fixtures/independent-ouc12-source-mapping.json',import.meta.url)));
const lzuMapping=JSON.parse(fs.readFileSync(new URL('./fixtures/independent-lzu11-source-mapping.json',import.meta.url)));
const db=readAtlasFile(new URL('../site/atlas.json',import.meta.url));
const roster=JSON.parse(fs.readFileSync(new URL('../site/rosters.json',import.meta.url)));
const mapping=JSON.parse(fs.readFileSync(new URL('./fixtures/independent-ustc12-source-mapping.json',import.meta.url)));
test('actual USTC cohort exactly preserves independently reviewed fields, identities and scope',()=>{
 assert.deepEqual(mapping.people.map(p=>p.person_id),["ustc-liubin-earth","ustc-jixiang","ustc-qianhongwu","ustc-liujing-life","ustc-jijiaojiao","ustc-zhangying-public-policy","ustc-zhuxiuli","ustc-shiyunli","ustc-niuweixing","ustc-zhumengxiao","ustc-wangchengwei","ustc-jinzhengyao"]);
 assert(mapping.people.every(p=>p.data_batch_id==='faculty-batch-ustc12-independent-20261026'));
 assert.equal(db.people.length,861+mapping.people.length+cauMapping.people.length+fduMapping.people.length+mucMapping.people.length+nwsuafMapping.people.length+oucMapping.people.length+lzuMapping.people.length);assert.equal(db.build_id,roster.build_id);
 for(const expected of mapping.people){
  const actual=db.people.find(p=>p.person_id===expected.person_id);assert.deepEqual(actual,expected);
  assert.equal(typeof actual.department,'string');assert(actual.department.length>0);
  assert(matches(actual,{q:actual.name},db.org_units));assert(matches(actual,{school:'ustc',org:actual.department_id},db.org_units));
  assert(!matches(actual,{school:'seu'},db.org_units));assert.equal(actual.quick_link_eligible,expected.quick_link_eligible);assert.equal(actual.include_in_current_faculty_count,expected.include_in_current_faculty_count);
  for(const stage of ['bachelor','master','doctor']) for(const event of stages(actual,stage)){assert.equal(event.event_kind,'degree');assert.equal(event.degree_awarded,true);}
 }
});
const {render}=createImmutableCohortRenderer({db,roster,fixtureId:import.meta.url});
for(const expected of mapping.people)test('actual USTC profile and lineage preserve '+expected.name,async()=>{
 const nodes=await render('#/person/'+expected.person_id);const html=['#main','#profile-content'].map(k=>nodes(k).innerHTML).join('\n');
 assert(html.includes(expected.name));assert(html.includes('中国科学技术大学'));
 const lineage=await render('#/person/'+expected.person_id+'/lineage');
 const relationHtml=['#main','#profile-content','#mind-stage'].map(k=>lineage(k).innerHTML).join('\n');
 for(const mentor of expected.mentors){assert(relationHtml.includes(mentor.name));assert(relationHtml.includes(mentor.type_label||mentor.type));}
 if(expected.mentors.length===0)assert(relationHtml.includes('0条已收录关系'));
});
const person=id=>db.people.find(p=>p.person_id===id);
const profile=async id=>{const n=await render('#/person/'+id);return n('#main').innerHTML+'\n'+n('#profile-content').innerHTML;};
test('USTC exact eight evidence-supported corrections retain six unknown stages without invented award dates',()=>{
 const yes=['ustc-jijiaojiao-bachelor','ustc-jijiaojiao-doctor','ustc-zhangying-public-policy-doctor','ustc-niuweixing-education-1','ustc-niuweixing-education-2','ustc-niuweixing-education-3','ustc-wangchengwei-education-2','ustc-jinzhengyao-education-1'];
 const no=['ustc-liujing-life-study2012','ustc-liujing-life-doctorate','ustc-jijiaojiao-master','ustc-wangchengwei-education-1','ustc-jinzhengyao-education-2','ustc-jinzhengyao-education-3'];
 const education=mapping.people.flatMap(p=>person(p.person_id).education);
 assert.deepEqual(education.filter(e=>e.degree_awarded===null).map(e=>e.event_id).sort(),[...no].sort());
 for(const id of yes){const e=education.find(e=>e.event_id===id);assert(e,id);assert.equal(e.source_degree_awarded,null);assert.equal(e.degree_awarded,true);assert.equal(e.event_kind,'degree');assert.equal(e.degree_awarded_date??null,null);assert.equal(e.degree_awarded_year??null,null);}
});
test('USTC visible limitations and publication contributions survive actual HTML, not only raw JSON',async()=>{
 for(const expected of mapping.people){const p=person(expected.person_id),html=await profile(p.person_id);
  for(const note of p.unknowns||[])assert(html.includes(escapeHtml(note)),p.person_id+' unknown: '+note);
  for(const work of p.publications||[])if(work.note)assert(html.includes(escapeHtml(work.note)),p.person_id+' publication note');
 }
});
test('Ji Xiang postdoc education and employment are linked views of one event, not two degrees',async()=>{
 const p=person('ustc-jixiang'),e=p.education.find(e=>e.event_id==='ustc-jixiang-postdoc'),a=p.appointments.find(a=>a.same_event_as===e.event_id);
 assert(a);assert.equal(e.degree_awarded,false);assert.equal(a.start,e.start);assert.equal(a.end,e.end);
 assert.equal(p.education.filter(e=>e.degree_awarded===true).length,2);assert(!stages(p,'master').length);
 const html=await profile(p.person_id);for(const text of ['同一经历','非两次活动','MBA','2学分'])assert(html.includes(text),text);
});
test('Liu Jing Debby Silver is professional guidance and 2025 joining is not an undated title start',async()=>{
 const p=person('ustc-liujing-life'),r=p.professional_research_advisors.find(r=>r.name==='Debby Silver');assert(r);
 assert.equal(r.include_in_degree_mentorship_graph,false);assert.equal(r.include_in_verified_mentor_count,false);assert.equal(r.include_in_verified_professional_guidance_count,true);
 assert(!p.mentors.some(m=>m.name==='Debby Silver'));assert.equal(mentorOfficialUrl(r),'');
 const title=p.appointments.find(a=>a.title.includes('特任研究员'));assert.equal(title.start,null);
 assert(p.appointments.some(a=>a.title.includes('加入机构')&&a.start==='2025-09'));
 const html=await profile(p.person_id);for(const text of ['Debby Silver','2019','2025','博士后、副研究员','加入与职称起点分开'])assert(html.includes(text),text);
 const lineage=await render('#/person/'+p.person_id+'/lineage');assert(!lineage('#mind-stage').innerHTML.includes('Debby Silver'));
});
test('Ji Jiaojiao retains both reported end dates and Zhang Ying empty works do not mean no lifetime output',async()=>{
 const ji=await profile('ustc-jijiaojiao');for(const t of ['2023-12','2024-05','两说','副所长'])assert(ji.includes(t),t);
 const p=person('ustc-zhangying-public-policy');assert.equal(p.publications.length,0);assert.equal(p.education.length,3);
 const html=await profile(p.person_id);for(const t of ['0条书目','不代表一生没有作品','本科、硕士','联合培养'])assert(html.includes(t),t);
});
test('Explicit original award years and Liu Bin award months are not erased or replaced by study endpoints',async()=>{
 const liu=person('ustc-liubin-earth');assert.deepEqual(liu.education.filter(e=>e.degree_awarded).map(e=>e.degree_awarded_date),['1986-07','1991-12']);
 const zhu=person('ustc-zhuxiuli');assert.deepEqual(zhu.education.filter(e=>e.degree_awarded).map(e=>e.degree_awarded_year),[1996,1999,2002]);
 const meng=person('ustc-zhumengxiao');assert.deepEqual(meng.education.filter(e=>e.degree_awarded).map(e=>e.degree_awarded_year),[2001,2004,2007,2012]);
 assert.equal(meng.education.filter(e=>e.degree_awarded&&e.degree_awarded_year===2001).length,1);
 const html=await profile(meng.person_id);for(const t of ['单一学习事件','两项明确学士资格','2020年12月','不推教授自'])assert(html.includes(t),t);
});
test('Every USTC actual teaching row preserves explicit role, audience, dates and co-teachers',async()=>{
 for(const p of mapping.people.filter(p=>(p.teaching||[]).length)){
  const html=await profile(p.person_id),rows=[...html.matchAll(/<li>[\s\S]*?<\/li>/g)].map(m=>m[0]);
  for(const t of p.teaching){const title=t.name||t.course||(t.courses||[]).join('、');assert(title,p.person_id);const row=rows.find(r=>r.includes('<strong>'+escapeHtml(title)+'</strong>'));assert(row,p.person_id+' '+title);if(t.role)assert(row.includes(escapeHtml(t.role)),title+' role');if(t.note)assert(row.includes(escapeHtml(t.note)),title+' note');}
 }
 const p=person('ustc-wangchengwei');assert.deepEqual(p.teaching.map(t=>t.role),['开设课程','合开','合开']);assert.equal(p.mentors.length,0);
 const html=await profile(p.person_id);for(const t of ['2018','2025','褚龙飞','王安轶','石云里','钮卫星','丁兆君','共同开课者不是本人导师'])assert(html.includes(t),t);
});
test('Jin Zhengyao emeritus directory remains visible beside historical present-tense title without invented retirement date',async()=>{
 const p=person('ustc-jinzhengyao'),html=await profile(p.person_id);
 for(const t of ['荣休教授','退休日期未知','2016','历史陈述','科技考古实验室主任'])assert(html.includes(t),t);
 assert.equal(p.include_in_current_faculty_count,false);assert.equal(p.quick_link_eligible,false);
 assert(!p.appointments.some(a=>a.title.includes('副研究员')&&a.start==='1984'));
 assert.equal(p.mentors.length,3);
});
