import {createImmutableCohortRenderer} from './immutable-cohort-renderer.js';
import {readAtlasFile,createAtlasFetch} from './atlas-test-io.js';
import {test} from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {matches, stages, mentorEvent, mentorEvents, mentorOfficialUrl, mentorProfileRoute, escapeHtml} from '../site/model.js';
const nwsuafMapping=JSON.parse(fs.readFileSync(new URL('./fixtures/independent-nwsuaf12-source-mapping.json',import.meta.url)));
const oucMapping=JSON.parse(fs.readFileSync(new URL('./fixtures/independent-ouc12-source-mapping.json',import.meta.url)));
const lzuMapping=JSON.parse(fs.readFileSync(new URL('./fixtures/independent-lzu11-source-mapping.json',import.meta.url)));
const sjtuMapping=JSON.parse(fs.readFileSync(new URL('./fixtures/independent-sjtu11-source-mapping.json',import.meta.url)));
const thuMapping=JSON.parse(fs.readFileSync(new URL('./fixtures/independent-thu11-source-mapping.json',import.meta.url)));
const pkuMapping=JSON.parse(fs.readFileSync(new URL('./fixtures/independent-pku11-source-mapping.json',import.meta.url)));
const zjuMapping=JSON.parse(fs.readFileSync(new URL('./fixtures/independent-zju7-source-mapping.json',import.meta.url)));
const mixedMapping=JSON.parse(fs.readFileSync(new URL('./fixtures/independent-neu4-cqu3-sysu2-source-mapping.json',import.meta.url)));
const njuSecondMapping=JSON.parse(fs.readFileSync(new URL('./fixtures/independent-nju11-second-source-mapping.json',import.meta.url)));
const seuSecondMapping=JSON.parse(fs.readFileSync(new URL('./fixtures/independent-seu11-second-source-mapping.json',import.meta.url)));
const nkuSecondMapping=JSON.parse(fs.readFileSync(new URL('./fixtures/independent-nku11-second-source-mapping.json',import.meta.url)));
const db=readAtlasFile(new URL('../site/atlas.json',import.meta.url));
const roster=JSON.parse(fs.readFileSync(new URL('../site/rosters.json',import.meta.url)));
const mapping=JSON.parse(fs.readFileSync(new URL('./fixtures/independent-muc12-source-mapping.json',import.meta.url)));
test('actual MUC cohort exactly preserves independently reviewed fields, identities and scope',()=>{
 assert.deepEqual(mapping.people.map(p=>p.person_id),["muc-zhangbufeng","muc-fanxiaoqing","muc-wutianyu","muc-linweili","muc-lichengming","muc-yangchunqiang","muc-mujing","muc-zhangliang","muc-chailing","muc-zhangmin-anthropology","muc-wuda","muc-qinlili"]);
 assert(mapping.people.every(p=>p.data_batch_id==='faculty-batch-muc12-independent-20261026'));
 assert.equal(db.people.length,897+mapping.people.length+nwsuafMapping.people.length+oucMapping.people.length+lzuMapping.people.length+sjtuMapping.people.length+thuMapping.people.length+pkuMapping.people.length+zjuMapping.people.length+mixedMapping.people.length+njuSecondMapping.people.length+seuSecondMapping.people.length+nkuSecondMapping.people.length);assert.equal(db.build_id,roster.build_id);
 for(const expected of mapping.people){
  const actual=db.people.find(p=>p.person_id===expected.person_id);assert.deepEqual(actual,expected);
  assert.equal(typeof actual.department,'string');assert(actual.department.length>0);
  assert(matches(actual,{q:actual.name},db.org_units));assert(matches(actual,{school:'muc',org:actual.department_id},db.org_units));
  assert(!matches(actual,{school:'seu'},db.org_units));assert.equal(actual.quick_link_eligible,expected.quick_link_eligible);assert.equal(actual.include_in_current_faculty_count,expected.include_in_current_faculty_count);
  for(const stage of ['bachelor','master','doctor']) for(const event of stages(actual,stage)){assert.equal(event.event_kind,'degree');assert.equal(event.degree_awarded,true);}
 }
});
const {render}=createImmutableCohortRenderer({db,roster,fixtureId:import.meta.url});
for(const expected of mapping.people)test('actual MUC profile and lineage preserve '+expected.name,async()=>{
 const nodes=await render('#/person/'+expected.person_id);const html=['#main','#profile-content'].map(k=>nodes(k).innerHTML).join('\n');
 assert(html.includes(expected.name));assert(html.includes('中央民族大学'));
 const lineage=await render('#/person/'+expected.person_id+'/lineage');
 const relationHtml=['#main','#profile-content','#mind-stage'].map(k=>lineage(k).innerHTML).join('\n');
 for(const mentor of expected.mentors){assert(relationHtml.includes(mentor.name));assert(relationHtml.includes(mentor.type_label||mentor.type));}
 if(expected.mentors.length===0)assert(relationHtml.includes('0条已收录关系'));
});
const person=id=>db.people.find(p=>p.person_id===id);
const profile=async id=>{const n=await render('#/person/'+id);return n('#main').innerHTML+'\n'+n('#profile-content').innerHTML;};
const visible=(html,terms)=>{for(const term of terms)assert(html.includes(escapeHtml(term)),term);};
test('MUC exact ten evidence-supported corrections retain six unknown stages without guessed award dates',()=>{
 const yes=['muc-yangchunqiang-bachelor',...Array.from({length:5},(_,i)=>'muc-zhangmin-anthropology-education-'+(i+1)),'muc-wuda-education-3',...Array.from({length:3},(_,i)=>'muc-qinlili-education-'+(i+1))];
 const no=['muc-yangchunqiang-master-scu','muc-yangchunqiang-master-paris','muc-yangchunqiang-doctor','muc-wuda-education-1','muc-wuda-education-2','muc-chailing-joint-doctoral-training'];
 const es=mapping.people.flatMap(p=>person(p.person_id).education);
 assert.deepEqual(es.filter(e=>e.degree_awarded===null).map(e=>e.event_id).sort(),[...no].sort());assert.deepEqual(es.filter(e=>e.source_degree_awarded===null&&e.degree_awarded===true).map(e=>e.event_id).sort(),[...yes].sort());
 for(const id of yes){const e=es.find(e=>e.event_id===id);assert.equal(e.event_kind,'degree');for(const k of ['degree_awarded_date','degree_awarded_year','degree_awarded_month'])assert.equal(e[k]??null,null);}
});
test('Every MUC evidence limitation, education and work note, and teaching role survives actual rendering',async()=>{
 for(const p of mapping.people){const html=await profile(p.person_id);for(const text of p.unknowns||[])visible(html,[text]);for(const e of p.education)if(e.note)visible(html,[e.note]);for(const w of p.publications||[])if(w.note)visible(html,[w.note]);
 const rows=[...html.matchAll(/<li>[\s\S]*?<\/li>/g)].map(m=>m[0]);for(const t of p.teaching||[]){const title=t.name||t.course||(t.courses||[]).join('、');assert(title,p.person_id);const row=rows.find(r=>r.includes('<strong>'+escapeHtml(title)+'</strong>'));assert(row,p.person_id+' '+title);if(t.role)visible(row,[t.role]);if(t.note)visible(row,[t.note]);}}
});
test('Zhang Bufeng shared study period is not divided into invented award intervals or professor start',async()=>{
 const p=person('muc-zhangbufeng');assert.equal(p.education.length,3);for(const e of p.education){assert.equal(e.degree_awarded,true);assert.equal(e.start,null);assert.equal(e.end,null);assert.equal(e.institution,null);}assert.equal(p.appointments.length,1);assert.equal(p.appointments[0].start,'2007');
 visible(await profile(p.person_id),['1997–2007','中国人民大学','不将共同区间分给各阶段','不把2007当教授晋升年']);
});
test('Fan and Wu retain unknown award dates and department or title conflicts rather than fabricated appointments',async()=>{
 const fan=person('muc-fanxiaoqing');for(const e of fan.education){assert.equal(e.degree_awarded_date,null);assert.equal(e.degree_awarded_year??null,null);}visible(await profile(fan.person_id),['广告与传媒经济系','广告系','不推更名','2004','不拆两次聘用']);
 const p=person('muc-wutianyu');assert.equal(p.appointments.length,0);for(const e of p.education.slice(0,2)){assert.equal(e.start,null);assert.equal(e.end,null);}assert.equal(p.education.find(e=>e.event_id==='muc-wutianyu-visit-kanagawa').degree,'交流访问');assert.equal(p.education.find(e=>e.event_id==='muc-wutianyu-visit-kanagawa').event_kind,'exchange_visit');
 visible(await profile(p.person_id),['讲师','准聘副教授','未载晋升日期','2009–2015','不推访问学者具体职衔']);
});
test('Lin explicit award years remain separate from study dates and 2017 institutional joining',async()=>{
 const p=person('muc-linweili');assert.deepEqual(p.education.filter(e=>e.degree_awarded===true).map(e=>e.degree_awarded_year),[1997,2003]);assert.equal(p.education.length,3);assert.equal(stages(p,'master').length,0);assert.equal(p.appointments[0].start,'2017-09');assert(!/^教授$/.test(p.appointments[0].title));
 visible(await profile(p.person_id),['1997','2003','不据此另造硕士','不把教授或实验室副主任起任回溯']);
});
test('Li explicit minor qualification and two-institution visit do not certify a dual-degree legal regime or two trips',async()=>{
 const p=person('muc-lichengming'),minor=p.education.find(e=>e.event_id==='muc-lichengming-bachelor-minor');assert.equal(minor.degree_awarded,true);assert(minor.degree.includes('辅修'));assert.equal(p.education.filter(e=>e.degree_awarded===false).length,1);assert.equal(p.appointments.length,0);
 visible(await profile(p.person_id),['不推法律双学位','同一2019.09—2020.09','不拆成两段全期访问','2021-09-27','2026书目']);
});
test('Yang remaining graduate stages and Mu graduation years do not become invented awards or journal metadata',async()=>{
 const yang=person('muc-yangchunqiang');assert.equal(yang.education.filter(e=>e.degree_awarded===null).length,3);assert.equal(yang.mentors.length,0);visible(await profile(yang.person_id),['两硕士与博士','2016-08-11','巴黎第七大学']);
 const p=person('muc-mujing');assert.deepEqual(p.education.map(e=>e.end),['2005','2007']);for(const e of p.education){assert.equal(e.start,null);assert.equal(e.degree_awarded_year??null,null);}visible(await profile(p.person_id),['2005、2007','原毕业年','未披露刊物、日期、正式作者名单及DOI']);
});
test('Zhang Liang zero selected works and single June state do not imply no output or open-ended tenure',async()=>{
 const p=person('muc-zhangliang');assert.equal(p.publications.length,0);const a=p.appointments.find(a=>(a.note||'').includes('2022年6月单月'));assert(a);assert.equal(a.start,null);assert.equal(a.end,null);assert.equal(p.mentors.length,0);
 visible(await profile(p.person_id),['书目0不是终生无作品','20余篇','2022年6月','未给起止或至今','民族学系第三页']);
});
test('Chai overlapping masters, awarded doctorate with open study label, and competing titles remain unresolved',async()=>{
 const p=person('muc-chailing');assert.equal(stages(p,'master').length,2);const d=p.education.find(e=>e.event_id==='muc-chailing-education-115');assert.equal(d.degree_awarded,true);assert.equal(d.start,'2005-09');assert.equal(d.end,null);assert.equal(p.education.find(e=>e.event_id==='muc-chailing-joint-doctoral-training').degree_awarded,null);
 visible(await profile(p.person_id),['副教授','讲师','双硕区间重叠','2005.9至今','获博士学位','不推法律双学位安排','不证明弗莱堡另授博士']);
});
test('Zhang Min missing master institution and bare years are not backfilled from Harvard or treated as award dates',async()=>{
 const p=person('muc-zhangmin-anthropology');const es=p.education.slice(0,5);assert.equal(es[1].institution,null);for(const e of es){assert.equal(e.degree_awarded,true);assert.equal(e.start,null);assert.equal(e.end,null);assert.equal(e.degree_awarded_year??null,null);}assert(es[4].degree.includes('辅修'));assert.equal(p.appointments[0].start,'2019-09');assert.equal(p.appointments[0].title,null);
 visible(await profile(p.person_id),['2010','2014','2005','2002','不继承上一哈佛博士行','不认证第二完整主修本科','2019-09仅入校工作']);
});
test('Wu Da inverted source dates and Qin phase guidance preserve exact uncertainty in profiles and lineage',async()=>{
 const p=person('muc-wuda'),a=p.appointments.find(a=>a.title==='副院长');assert.equal(a.start,null);assert.equal(a.end,null);assert.equal(p.education[0].degree_awarded,null);assert.equal(p.education[1].degree_awarded,null);visible(await profile(p.person_id),['2020年7月-2020年3月','不交换月份','1998年9月-2004年12月','合段月份不拆配']);
 const q=person('muc-qinlili');assert.equal(q.education.find(e=>e.event_id==='muc-qinlili-education-3').degree,'本科学位');assert.deepEqual(q.mentors.map(m=>[m.name,m.education_event_id]),[['王克非','muc-qinlili-education-1'],['李德凤','muc-qinlili-training-1'],['Kirsten Malmkjaer','muc-qinlili-training-2']]);
 const n=await render('#/person/'+q.person_id+'/lineage');visible(n('#profile-content').innerHTML,['王克非','李德凤','Kirsten Malmkjaer']);visible(await profile(q.person_id),['均非正式论文导师认证','本科学位','不编法学/文学等学位门类']);
});

test('MUC non-null research_interests are display strings for all twelve canonical profiles',()=>{
 for(const p of mapping.people){const actual=person(p.person_id);if(actual.research_interests!==undefined&&actual.research_interests!==null)assert.equal(typeof actual.research_interests,'string',p.person_id);}
});
test('Yang and Mu render exact original research text in the research sidebar, not object stringification',async()=>{
 const cases=[['muc-yangchunqiang','宗教与精神分析，精神分析与中国文化思想，宗教心理学，无意识结构与汉字结构。'],['muc-mujing','视觉传达设计、海报设计、信息图表设计、设计创意、书籍设计']];
 for(const [id,text] of cases){const p=person(id);assert.equal(p.research_interests,text);assert.equal(p.source_research_interests.source_reported_text,text);
  const nodes=await render('#/person/'+id),html=nodes('#profile-content').innerHTML;const aside=html.match(/<aside class="profile-info"[\s\S]*?<\/aside>/)?.[0];assert(aside,id+' profile sidebar');assert(aside.includes('<h3>研究方向</h3><p>'+escapeHtml(text)+'</p>'),id+' exact research panel');assert(!html.includes('[object Object]'),id+' object stringification');
 }
});
