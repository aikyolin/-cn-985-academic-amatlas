import {createImmutableCohortRenderer} from './immutable-cohort-renderer.js';
import {readAtlasFile,createAtlasFetch} from './atlas-test-io.js';
import {test} from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {matches, stages, mentorEvent, mentorEvents, mentorOfficialUrl, mentorProfileRoute, escapeHtml} from '../site/model.js';
const mucMapping=JSON.parse(fs.readFileSync(new URL('./fixtures/independent-muc12-source-mapping.json',import.meta.url)));
const nwsuafMapping=JSON.parse(fs.readFileSync(new URL('./fixtures/independent-nwsuaf12-source-mapping.json',import.meta.url)));
const oucMapping=JSON.parse(fs.readFileSync(new URL('./fixtures/independent-ouc12-source-mapping.json',import.meta.url)));
const lzuMapping=JSON.parse(fs.readFileSync(new URL('./fixtures/independent-lzu11-source-mapping.json',import.meta.url)));
const db=readAtlasFile(new URL('../site/atlas.json',import.meta.url));
const roster=JSON.parse(fs.readFileSync(new URL('../site/rosters.json',import.meta.url)));
const mapping=JSON.parse(fs.readFileSync(new URL('./fixtures/independent-fdu12-source-mapping.json',import.meta.url)));
test('actual FDU cohort exactly preserves independently reviewed fields, identities and scope',()=>{
 assert.deepEqual(mapping.people.map(p=>p.person_id),["fdu-huanning","fdu-fengping","fdu-zhaodongyuan","fdu-penghuisheng","fdu-huyan","fdu-suntao","fdu-anjiesheng","fdu-zhangmingjun","fdu-jiangyixuan","fdu-jiangping","fdu-zhangnaigen","fdu-zhuxiuping"]);
 assert(mapping.people.every(p=>p.data_batch_id==='faculty-batch-fdu12-independent-20261026'));
 assert.equal(db.people.length,885+mapping.people.length+mucMapping.people.length+nwsuafMapping.people.length+oucMapping.people.length+lzuMapping.people.length);assert.equal(db.build_id,roster.build_id);
 for(const expected of mapping.people){
  const actual=db.people.find(p=>p.person_id===expected.person_id);assert.deepEqual(actual,expected);
  assert.equal(typeof actual.department,'string');assert(actual.department.length>0);
  assert(matches(actual,{q:actual.name},db.org_units));assert(matches(actual,{school:'fdu',org:actual.department_id},db.org_units));
  assert(!matches(actual,{school:'seu'},db.org_units));assert.equal(actual.quick_link_eligible,expected.quick_link_eligible);assert.equal(actual.include_in_current_faculty_count,expected.include_in_current_faculty_count);
  for(const stage of ['bachelor','master','doctor']) for(const event of stages(actual,stage)){assert.equal(event.event_kind,'degree');assert.equal(event.degree_awarded,true);}
 }
});
const {render}=createImmutableCohortRenderer({db,roster,fixtureId:import.meta.url});
for(const expected of mapping.people)test('actual FDU profile and lineage preserve '+expected.name,async()=>{
 const nodes=await render('#/person/'+expected.person_id);const html=['#main','#profile-content'].map(k=>nodes(k).innerHTML).join('\n');
 assert(html.includes(expected.name));assert(html.includes('复旦大学'));
 const lineage=await render('#/person/'+expected.person_id+'/lineage');
 const relationHtml=['#main','#profile-content','#mind-stage'].map(k=>lineage(k).innerHTML).join('\n');
 for(const mentor of expected.mentors){assert(relationHtml.includes(mentor.name));assert(relationHtml.includes(mentor.type_label||mentor.type));}
 if(expected.mentors.length===0)assert(relationHtml.includes('0条已收录关系'));
});
const person=id=>db.people.find(p=>p.person_id===id);
const profile=async id=>{const n=await render('#/person/'+id);return n('#main').innerHTML+'\n'+n('#profile-content').innerHTML;};
const visible=(html,terms)=>{for(const term of terms)assert(html.includes(escapeHtml(term)),term);};
test('FDU eight precise supported corrections retain six unknowns and no inferred conferral dates',()=>{
 const yes=['fdu-huanning-bachelor-label','fdu-huanning-master-sociology-label','fdu-huanning-master-statistics-label','fdu-huanning-doctorate-label','fdu-zhangmingjun-education-1','fdu-jiangyixuan-education-1','fdu-jiangyixuan-education-2','fdu-jiangping-education-1'];
 const no=['fdu-fengping-undergraduate','fdu-fengping-master','fdu-suntao-undergraduate','fdu-suntao-integrated-study','fdu-zhangmingjun-education-2','fdu-zhuxiuping-education-1'];
 const es=mapping.people.flatMap(p=>person(p.person_id).education);
 assert.deepEqual(es.filter(e=>e.degree_awarded===null).map(e=>e.event_id).sort(),[...no].sort());
 assert.deepEqual(es.filter(e=>e.source_degree_awarded===null&&e.degree_awarded===true).map(e=>e.event_id).sort(),[...yes].sort());
 for(const id of yes){const e=es.find(e=>e.event_id===id);assert.equal(e.event_kind,'degree');assert.equal(e.degree_awarded_date??null,null);assert.equal(e.degree_awarded_year??null,null);assert.equal(e.degree_awarded_month??null,null);}
});
test('FDU evidence limits, work contributions and course roles are consumed in actual HTML',async()=>{
 for(const p of mapping.people){const html=await profile(p.person_id);
  for(const text of p.unknowns||[])visible(html,[text]);
  for(const e of p.education)if(e.note)visible(html,[e.note]);
  for(const w of p.publications||[])if(w.note)visible(html,[w.note]);
  const rows=[...html.matchAll(/<li>[\s\S]*?<\/li>/g)].map(m=>m[0]);
  for(const t of p.teaching||[]){const title=t.name||t.course||(t.courses||[]).join('、');assert(title,p.person_id);const row=rows.find(r=>r.includes('<strong>'+escapeHtml(title)+'</strong>'));assert(row,p.person_id+' '+title);if(t.role)visible(row,[t.role]);if(t.note)visible(row,[t.note]);}
 }
});
test('Hu four qualifications have no study or award dates and Feng retirement category does not become a retirement date',async()=>{
 const hu=person('fdu-huanning');assert.equal(hu.education.length,4);assert.equal(hu.mentors.length,0);for(const e of hu.education){assert.equal(e.degree_awarded,true);assert.equal(e.start,null);assert.equal(e.end,null);}
 visible(await profile(hu.person_id),['复旦社会学学士/硕士','普度统计学硕士/社会学博士','所有学习区间与授位日期未知']);
 const p=person('fdu-fengping');assert.equal(p.retirement_date,null);assert.equal(p.education.filter(e=>e.degree_awarded===null).length,2);assert.equal(p.mentors.length,1);assert.equal(p.mentors[0].education_event_id,'fdu-fengping-doctoral');
 visible(await profile(p.person_id),['离退休教师目录','退休日期未知','不转为当前任职','2011-07-01','马哲']);
});
test('Zhao four conflicting overseas intervals remain unknown and joint doctorate is one award',async()=>{
 const p=person('fdu-zhaodongyuan');const conflictIDs=['regina-visit','weizmann-postdoc','houston-postdoc','ucsb-postdoc'];
 for(const suffix of conflictIDs){const e=p.education.find(e=>e.event_id==='fdu-zhaodongyuan-'+suffix);assert.equal(e.start,null);assert.equal(e.end,null);assert.equal(e.degree_awarded,false);}
 assert.equal(stages(p,'doctor').length,1);const d=stages(p,'doctor')[0];assert.equal(d.degree_awarded_year,1990);assert.equal(d.degree_awarded_date,null);
 visible(await profile(p.person_id),['1993至1993','1992至1993','访问学者','访问教授','1993至1995','1993至1994','1996至1997','1995至1996','1997至1998','1996至1998','不拆两次']);
});
test('Peng Director Fellow is not inferred postdoc and Hu Yan page label is not latest update',async()=>{
 const p=person('fdu-penghuisheng'),e=p.education.find(e=>e.event_id==='fdu-penghuisheng-los-alamos-fellowship');assert.equal(e.degree_awarded,false);assert(!/postdoc|博士后/i.test(e.event_kind));assert.equal(p.mentors.length,0);
 visible(await profile(p.person_id),['Director’s Fellow','不推博士后','不补DOI','纤维电子材料与器件研究院']);
 const hu=person('fdu-huyan');assert.deepEqual(hu.education.map(e=>e.degree_awarded_year),[1989,1996,2003]);visible(await profile(hu.person_id),['2023-03-21','2024作品','上海医科大学']);
});
test('Sun Tao unattached education label cannot establish a school-specific doctorate or duplicate postdoc',async()=>{
 const p=person('fdu-suntao');assert.equal(p.qualification_label_source_text,'学历：博士');assert.equal(p.education.filter(e=>e.degree_awarded===true).length,0);assert.equal(p.education.length,4);assert.equal(p.mentors.length,0);
 const e=p.education.find(e=>e.event_id==='fdu-suntao-postdoctoral'),a=p.appointments.find(a=>a.title==='博士后');assert.equal(a.start,e.start);assert.equal(a.end,e.end);
 visible(await profile(p.person_id),['独立学历标签“博士”','不绑定山东大学或海外机构','同一来源活动的两种视图','药剂学教研室','药剂学系']);
});
test('An institutional employment starts before his assistant title and secretarial work is not postdoc education',async()=>{
 const p=person('fdu-anjiesheng'),a=p.appointments.find(a=>a.start==='1987');assert(a);assert.equal(a.end,'1991');assert.equal(a.title,'机构工作');assert(!p.appointments.some(a=>/助教/.test(a.title||'')&&a.start==='1987'));
 assert.deepEqual(p.education.filter(e=>e.degree_awarded===true).map(e=>e.degree_awarded_year),[1987,1993,1996]);assert(!p.education.some(e=>/博士后/.test(e.degree||'')));
 assert.deepEqual(p.mentors.map(m=>[m.name,m.education_event_id]),[['葛剑雄','fdu-anjiesheng-education-2'],['葛剑雄','fdu-anjiesheng-education-3']]);
 visible(await profile(p.person_id),['1988','助教','博士后站秘书不是本人博士后经历','2013年7月至8月','为期1个月','一九九六年春季仅毕业季']);
});
test('Zhang Mingjun has two actual stage mentors and a still unknown master award',async()=>{
 const p=person('fdu-zhangmingjun');assert.equal(p.education[0].degree_awarded,true);assert.equal(p.education[1].degree_awarded,null);assert.equal(p.education[2].degree_awarded_year,2021);assert.deepEqual(p.mentors.map(m=>m.name),['王巍','Michael Weisberg']);
 const n=await render('#/person/'+p.person_id+'/lineage');visible(n('#profile-content').innerHTML,['王巍','Michael Weisberg']);visible(await profile(p.person_id),['化学系机构不能自动成为本科专业','硕士阶段导师','博士阶段导师']);
});
test('Jiang Yixuan bilingual degrees and two Haidong Kan stages do not certify a dissertation advisor',async()=>{
 const p=person('fdu-jiangyixuan');assert.equal(p.education[0].start,'2013-09');assert.equal(p.education[1].end,'2023-06');assert.equal(p.mentors.length,2);assert(p.mentors.every(m=>m.name==='Prof. Haidong Kan'));assert.deepEqual(p.mentors.map(m=>m.education_event_id),['fdu-jiangyixuan-education-2','fdu-jiangyixuan-nondegree-1']);
 visible(await profile(p.person_id),['Bachelor Degree','Ph.D.','Environmental Health','劳动卫生与环境卫生学','非正式论文导师','Updated 2025/10/14']);
});
test('Jiang Ping keeps explicit doctorate year but not July award and is not labelled honorary professor',async()=>{
 const p=person('fdu-jiangping'),e=p.education.find(e=>e.event_id==='fdu-jiangping-education-2');assert.equal(e.degree_awarded_year,2010);assert.equal(e.end,'2010-07');assert.equal(e.degree_awarded_date,null);assert.equal(e.degree_awarded_month??null,null);assert(!p.appointments.some(a=>/名誉/.test(a.title||'')));
 visible(await profile(p.person_id),['全职教师栏','名誉教授不套用于本人','2010-07仅学习终月']);
});
test('Zhang Naigen repeated visits are not continuous jobs and Zhu Xiuping preserves dual-page provenance',async()=>{
 const z=person('fdu-zhangnaigen');for(const suffix of ['8','11']){const e=z.education.find(e=>e.event_id==='fdu-zhangnaigen-training-'+suffix);assert.equal(e.start,null);assert.equal(e.end,null);assert.equal(e.degree_awarded,false);}
 visible(await profile(z.person_id),['华东政法学院','2005、2006年','1996年至2008年多次','不作连续任期']);
 const p=person('fdu-zhuxiuping'),e=p.education.find(e=>e.event_id==='fdu-zhuxiuping-education-2');assert.equal(e.degree_awarded_year,2011);assert.equal(e.degree_awarded_month,7);assert(e.source_url.includes('c30984'));assert.equal(p.education.filter(e=>/硕士/.test(e.degree||'')).length,0);assert.deepEqual(p.mentors.map(m=>m.name),['倪晋仁']);
 assert(p.publications.every(w=>w.source_url.includes('c26241')));assert(p.teaching.every(t=>t.source_url.includes('c26241')));
 visible(await profile(p.person_id),['c30984','c26241','Bruce Logan仅课题组背景','不生成人际导师边','不宣称同字节']);
});
