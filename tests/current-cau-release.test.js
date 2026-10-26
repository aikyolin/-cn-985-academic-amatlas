import {createImmutableCohortRenderer} from './immutable-cohort-renderer.js';
import {readAtlasFile,createAtlasFetch} from './atlas-test-io.js';
import {test} from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {matches, stages, mentorEvent, mentorEvents, mentorOfficialUrl, mentorProfileRoute, escapeHtml} from '../site/model.js';
const fduMapping=JSON.parse(fs.readFileSync(new URL('./fixtures/independent-fdu12-source-mapping.json',import.meta.url)));
const mucMapping=JSON.parse(fs.readFileSync(new URL('./fixtures/independent-muc12-source-mapping.json',import.meta.url)));
const nwsuafMapping=JSON.parse(fs.readFileSync(new URL('./fixtures/independent-nwsuaf12-source-mapping.json',import.meta.url)));
const oucMapping=JSON.parse(fs.readFileSync(new URL('./fixtures/independent-ouc12-source-mapping.json',import.meta.url)));
const lzuMapping=JSON.parse(fs.readFileSync(new URL('./fixtures/independent-lzu11-source-mapping.json',import.meta.url)));
const sjtuMapping=JSON.parse(fs.readFileSync(new URL('./fixtures/independent-sjtu11-source-mapping.json',import.meta.url)));
const thuMapping=JSON.parse(fs.readFileSync(new URL('./fixtures/independent-thu11-source-mapping.json',import.meta.url)));
const db=readAtlasFile(new URL('../site/atlas.json',import.meta.url));
const roster=JSON.parse(fs.readFileSync(new URL('../site/rosters.json',import.meta.url)));
const mapping=JSON.parse(fs.readFileSync(new URL('./fixtures/independent-cau12-source-mapping.json',import.meta.url)));
test('actual CAU cohort exactly preserves independently reviewed fields, identities and scope',()=>{
 assert.deepEqual(mapping.people.map(p=>p.person_id),["cau-chenjingyu","cau-rendongyang","cau-ma-chao","cau-xu-guangyuan","cau-li-guangyao","cau-pengchen-wave98","cau-malingjun","cau-guojie","cau-yinyiyong","cau-gaoyu","cau-sunqingzhong","cau-yangdong-foodbiochemistry"]);
 assert(mapping.people.every(p=>p.data_batch_id==='faculty-batch-cau12-independent-20261026'));
 assert.equal(db.people.length,873+mapping.people.length+fduMapping.people.length+mucMapping.people.length+nwsuafMapping.people.length+oucMapping.people.length+lzuMapping.people.length+sjtuMapping.people.length+thuMapping.people.length);assert.equal(db.build_id,roster.build_id);
 for(const expected of mapping.people){
  const actual=db.people.find(p=>p.person_id===expected.person_id);assert.deepEqual(actual,expected);
  assert.equal(typeof actual.department,'string');assert(actual.department.length>0);
  assert(matches(actual,{q:actual.name},db.org_units));assert(matches(actual,{school:'cau',org:actual.department_id},db.org_units));
  assert(!matches(actual,{school:'seu'},db.org_units));assert.equal(actual.quick_link_eligible,expected.quick_link_eligible);assert.equal(actual.include_in_current_faculty_count,expected.include_in_current_faculty_count);
  for(const stage of ['bachelor','master','doctor']) for(const event of stages(actual,stage)){assert.equal(event.event_kind,'degree');assert.equal(event.degree_awarded,true);}
 }
});
const {render}=createImmutableCohortRenderer({db,roster,fixtureId:import.meta.url});
for(const expected of mapping.people)test('actual CAU profile and lineage preserve '+expected.name,async()=>{
 const nodes=await render('#/person/'+expected.person_id);const html=['#main','#profile-content'].map(k=>nodes(k).innerHTML).join('\n');
 assert(html.includes(expected.name));assert(html.includes('中国农业大学'));
 const lineage=await render('#/person/'+expected.person_id+'/lineage');
 const relationHtml=['#main','#profile-content','#mind-stage'].map(k=>lineage(k).innerHTML).join('\n');
 for(const mentor of expected.mentors){assert(relationHtml.includes(mentor.name));assert(relationHtml.includes(mentor.type_label||mentor.type));}
 if(expected.mentors.length===0)assert(relationHtml.includes('0条已收录关系'));
});
const person=id=>db.people.find(p=>p.person_id===id);
const profile=async id=>{const n=await render('#/person/'+id);return n('#main').innerHTML+'\n'+n('#profile-content').innerHTML;};
const visible=(html,terms)=>{for(const term of terms)assert(html.includes(escapeHtml(term)),term);};
test('CAU eleven precise source-supported corrections preserve four unknown stages and do not invent award dates',()=>{
 const yes=['cau-ma-bachelor','cau-ma-doctoral','cau-peng-doctoral','cau-guojie-本科','cau-guojie-博士','cau-yinyiyong-education-1','cau-yinyiyong-education-2','cau-gaoyu-education-1','cau-gaoyu-education-3','cau-yangdong-foodbiochemistry-education-1','cau-yangdong-foodbiochemistry-education-2'];
 const no=['cau-ma-master-context','cau-guojie-硕士','cau-gaoyu-education-2','cau-sunqingzhong-education-1'];
 const es=mapping.people.flatMap(p=>person(p.person_id).education);
 assert.deepEqual(es.filter(e=>e.degree_awarded===null).map(e=>e.event_id).sort(),[...no].sort());
 assert.deepEqual(es.filter(e=>e.source_degree_awarded===null&&e.degree_awarded===true).map(e=>e.event_id).sort(),[...yes].sort());
 for(const id of yes){const e=es.find(e=>e.event_id===id);assert.equal(e.event_kind,'degree');assert.equal(e.degree_awarded_date??null,null);assert.equal(e.degree_awarded_year??null,null);assert(e.note);}
});
test('CAU all source limitations, education evidence and 22 publication qualifiers are actual visible HTML',async()=>{
 let works=0;
 for(const p of mapping.people){const html=await profile(p.person_id);
  for(const text of p.unknowns||[])visible(html,[text]);
  for(const e of p.education)if(e.note)visible(html,[e.note]);
  for(const w of p.publications||[]){works++;if(w.note)visible(html,[w.note]);}
 }assert.equal(works,22);
});
test('CAU all 19 teaching rows preserve explicit roles and source audience and schedule notes',async()=>{
 let count=0;
 for(const p of mapping.people){const html=await profile(p.person_id),rows=[...html.matchAll(/<li>[\s\S]*?<\/li>/g)].map(m=>m[0]);
  for(const t of p.teaching||[]){count++;const title=t.name||t.course||(t.courses||[]).join('、');assert(title,p.person_id);const row=rows.find(r=>r.includes('<strong>'+escapeHtml(title)+'</strong>'));assert(row,p.person_id+' '+title);if(t.role)visible(row,[t.role]);if(t.note)visible(row,[t.note]);}
 }assert.equal(count,19);
});
test('Ma Chao early doctorate and merged master context do not acquire invented dates or course roles',async()=>{
 const p=person('cau-ma-chao'),master=p.education.find(e=>e.event_id==='cau-ma-master-context');assert.equal(master.degree_awarded,null);assert.equal(master.start,null);assert.equal(master.end,null);
 assert.equal(p.teaching.length,2);for(const t of p.teaching){assert.equal(t.source_academic_year,'2026-2027');assert.equal(t.role??null,null);assert.equal(t.start??null,null);assert.equal(t.end??null,null);}
 visible(await profile(p.person_id),['提前攻博','2004–2009','硕士、博士','第一学期','2026-2027']);
});
test('Ren dual college labels and Chen and Xu dated-page limitations stay distinct from title or department proof',async()=>{
 const ren=person('cau-rendongyang');assert.equal(db.org_units.find(o=>o.id===ren.department_id).parent_id,null);
 visible(await profile(ren.person_id),['水利与土木工程学院','水利与智能工程学院','不推更名']);
 const chen=person('cau-chenjingyu');assert.equal(chen.appointments.find(a=>a.title==='教授').start,null);visible(await profile(chen.person_id),['2017-01-09','2020作品','不推晋升时间']);
 visible(await profile('cau-xu-guangyuan'),['多个系重复列名','不独立推系别或职称','2024-02-24','2026任职']);
});
test('Li talent selection is not appointment start and Peng postdoc guidance cannot become doctoral supervision',async()=>{
 const li=person('cau-li-guangyao');assert.equal(li.appointments.find(a=>a.title==='副教授').start,null);assert.equal(li.mentors[0].education_event_id,'cau-li-postdoc');assert.equal(li.mentors[0].type,'postdoctoral_supervisor');
 visible(await profile(li.person_id),['2026年','不是副教授起任','朱文武','博士后']);
 const p=person('cau-pengchen-wave98');assert.equal(p.education.filter(e=>e.degree_awarded===true).length,1);assert.equal(p.mentors[0].name,'Bernard Moss');assert.equal(p.mentors[0].type,'postdoctoral_supervisor');assert.equal(Object.hasOwn(p.mentors[0],'education_event_id'),false);assert.equal(p.mentors[0].specific_host_event_link,null);assert.deepEqual(mentorEvents(p,p.mentors[0]),[]);assert.deepEqual(mentorEvent(p,p.mentors[0]),{});
 visible(await profile(p.person_id),['2010.08.10–2016.05.13','不唯一绑定某一机构及日期','不挂博士阶段']);
 const lineage=await render('#/person/'+p.person_id+'/lineage');visible(lineage('#profile-content').innerHTML,['Bernard Moss','博士后阶段师从（非已核原论文导师）','未唯一绑定某一博士后机构或区间，不挂博士学位经历']);
 const graph=lineage('#mind-stage').innerHTML,row=graph.match(/<path d="M300 [\s\S]*?<\/a>/)?.[0];assert(row);visible(row,['Bernard Moss','博士后','阶段机构待核实','起止时间未核实']);for(const e of p.education)assert(!row.includes(escapeHtml(e.institution)),e.institution);
});
test('Yin conflicting doctoral institutions and mandatory unknown course levels preserve original schedule without personal campus inference',async()=>{
 const p=person('cau-yinyiyong'),e=p.education.find(e=>e.event_id==='cau-yinyiyong-education-1');assert.equal(e.start,null);assert.equal(e.end,null);assert.equal(p.teaching.length,2);
 for(const t of p.teaching){assert.equal(t.level??null,null);assert.equal(t.student_level??null,null);assert(t.note.includes('层级未知'));assert(t.note.includes('东校区'));}
 assert(!JSON.stringify(p.campus||p.campus_id||null).includes('东校区'));
 visible(await profile(p.person_id),['2006.09.01–2012.01.01','2008.09–2012.01','清华大学与北京科技大学','星期三星期五','星期一星期四','东校区']);
});
test('Gao two doctoral labels are one source-reported qualification not legal equivalence or an invented second degree',async()=>{
 const p=person('cau-gaoyu');assert.equal(p.education.length,3);assert.equal(p.education.find(e=>e.event_id==='cau-gaoyu-education-2').degree_awarded,null);
 visible(await profile(p.person_id),['Doctor of Veterinary Medicine','Dr.med.vet.','不作两称谓法律学位等价','不新增第二学位','Summa Cum Laude']);
});
test('Ma Lingjun title and doctorate discipline conflicts and Guo single doctorate remain unresolved in actual HTML',async()=>{
 const ma=person('cau-malingjun');assert.equal(ma.appointments[0].title,'副教授');assert(!ma.publications[0].authors_as_source.includes('Ma'));
 visible(await profile(ma.person_id),['教授','副教授至今','农业与环境化学','分析化学','作者字段不含Ma','不据个人页归属补作者']);
 const guo=person('cau-guojie');assert.equal(guo.education.length,3);assert.equal(guo.education.find(e=>e.event_id==='cau-guojie-硕士').degree_awarded,null);
 visible(await profile(guo.person_id),['哲学博士学位','医学博士','不拆两学位','不裁定名称等价']);
});
test('Sun original award years and unknown 1991 level survive without inferred study intervals or renamed historical department',async()=>{
 const p=person('cau-sunqingzhong'),es=p.education;assert.equal(es[0].degree_awarded,null);assert.equal(es[1].degree_awarded_year_as_source,'1997年');assert.equal(es[2].degree_awarded_year_as_source,'2001年');assert.equal(es[1].institution,'辽宁大学');assert.equal(es[2].institution,'中山大学');for(const e of es.slice(0,3)){assert.equal(e.start,null);assert.equal(e.end,null);}
 visible(await profile(p.person_id),['1991年','层级未知','1997年获辽宁大学','2001年获中山大学','1998年','社会学系','社会学与人类学系','2009-02-07','2021作品']);
 assert(!p.appointments.some(a=>a.title==='教授'&&a.start==='2003'));
});
test('Yang independent doctoral identity matches one stage and George guidance is not certified thesis or Yale guidance',async()=>{
 const p=person('cau-yangdong-foodbiochemistry'),e=p.education.find(e=>e.event_id==='cau-yangdong-foodbiochemistry-education-2');assert.equal(e.degree_awarded,true);assert(e.note.includes('独立职业简介'));
 assert.equal(p.mentors.length,1);const m=p.mentors[0];assert.equal(m.name,'George H. Lorimer');assert.equal(m.education_event_id,e.event_id);assert.equal(m.formal_thesis_advisor_verified,false);assert.equal(m.formal_doctoral_dissertation_advisor_verified,false);
 visible(await profile(p.person_id),['不是仅据“博士毕业”','George H. Lorimer','不作正式博士论文导师','耶鲁研究起止未知']);
});
