import {createImmutableCohortRenderer} from './immutable-cohort-renderer.js';
import {readAtlasFile,createAtlasFetch} from './atlas-test-io.js';
import {test} from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {matches, stages, mentorEvent, mentorEvents, mentorOfficialUrl, mentorProfileRoute, escapeHtml} from '../site/model.js';
const sjtuMapping=JSON.parse(fs.readFileSync(new URL('./fixtures/independent-sjtu11-source-mapping.json',import.meta.url)));
const db=readAtlasFile(new URL('../site/atlas.json',import.meta.url));
const roster=JSON.parse(fs.readFileSync(new URL('../site/rosters.json',import.meta.url)));
const mapping=JSON.parse(fs.readFileSync(new URL('./fixtures/independent-lzu11-source-mapping.json',import.meta.url)));
test('actual LZU cohort exactly preserves independently reviewed fields, identities and scope',()=>{
 assert.deepEqual(mapping.people.map(p=>p.person_id),["lzu-anjunhong", "lzu-caojiangwei", "lzu-chaiguozhi", "lzu-huangjianping", "lzu-gelong", "lzu-shilei", "lzu-wangdaqiao", "lzu-zhangjin", "lzu-zhengbing", "lzu-liwantong", "lzu-zhangtongsheng"]);
 assert(mapping.people.every(p=>p.data_batch_id==='faculty-batch-lzu11-independent-20261026'));
 assert.equal(db.people.length,933+mapping.people.length+sjtuMapping.people.length);assert.equal(db.build_id,roster.build_id);
 for(const expected of mapping.people){
  const actual=db.people.find(p=>p.person_id===expected.person_id);assert.deepEqual(actual,expected);
  assert.equal(typeof actual.department,'string');assert(actual.department.length>0);
  assert(matches(actual,{q:actual.name},db.org_units));assert(matches(actual,{school:'lzu',org:actual.department_id},db.org_units));
  assert(!matches(actual,{school:'seu'},db.org_units));assert.equal(actual.quick_link_eligible,expected.quick_link_eligible);assert.equal(actual.include_in_current_faculty_count,expected.include_in_current_faculty_count);
  for(const stage of ['bachelor','master','doctor']) for(const event of stages(actual,stage)){assert.equal(event.event_kind,'degree');assert.equal(event.degree_awarded,true);}
 }
});
const {render}=createImmutableCohortRenderer({db,roster,fixtureId:import.meta.url});
for(const expected of mapping.people)test('actual LZU profile and lineage preserve '+expected.name,async()=>{
 const nodes=await render('#/person/'+expected.person_id);const html=['#main','#profile-content'].map(k=>nodes(k).innerHTML).join('\n');
 assert(html.includes(expected.name));assert(html.includes('兰州大学'));
 const lineage=await render('#/person/'+expected.person_id+'/lineage');
 const relationHtml=['#main','#profile-content','#mind-stage'].map(k=>lineage(k).innerHTML).join('\n');
 for(const mentor of expected.mentors){assert(relationHtml.includes(mentor.name));assert(relationHtml.includes(mentor.type_label||mentor.type));}
 if(expected.mentors.length===0)assert(relationHtml.includes('0条已收录关系'));
});

test('LZU all non-null research_interests are renderable strings, not nested source objects',()=>{
 for(const p of mapping.people){const actual=db.people.find(x=>x.person_id===p.person_id);if(actual.research_interests!==undefined&&actual.research_interests!==null)assert.equal(typeof actual.research_interests,'string',p.person_id);}
});
test('LZU research sidebar displays each reviewed research text exactly without object stringification',async()=>{
 for(const p of mapping.people){const nodes=await render('#/person/'+p.person_id),html=nodes('#profile-content').innerHTML,aside=html.match(/<aside class="profile-info"[\s\S]*?<\/aside>/)?.[0];assert(aside,p.person_id);const text=p.research_interests||'待补录';assert.equal(typeof text,'string',p.person_id);assert(aside.includes('<h3>研究方向</h3><p>'+escapeHtml(text)+'</p>'),p.person_id+' exact research panel');assert(!html.includes('[object Object]'),p.person_id+' object stringification');}
});



const person=id=>db.people.find(p=>p.person_id==='lzu-'+id);
const visible=(html,terms)=>{for(const term of terms)assert(html.includes(escapeHtml(term)),term);};
async function profile(id){const n=await render('#/person/lzu-'+id);return n('#profile-content').innerHTML;}
async function graph(id){const n=await render('#/person/lzu-'+id+'/lineage');return n('#mind-stage').innerHTML;}
test('An preserves overlapping appointments and intermittent research without resolving conflicting author identities',async()=>{
 const p=person('anjunhong');assert.deepEqual(p.education.map(e=>e.degree_awarded),[true,true,false,false]);assert.equal(p.mentors.length,0);visible(await profile('anjunhong'),['兰州大学任职与海外研究原区间重叠','每年4–6个月','非博士后、非学位','不视作全区间连续驻留','官网末作者Peng-Bo Li，二手索引Fuli Li不一致','明示发表2025-07-08']);
});
test('Cao source2024 stays2024 despite secondary volume metadata and unspecified promotion dates',async()=>{
 const p=person('caojiangwei');assert.deepEqual(p.education.map(e=>e.degree_awarded),[true,true,false,false]);assert.equal(p.publications[1].year,2024);assert.equal(p.appointments.length,1);assert.equal(p.appointments[0].start,'2009-11');visible(await profile('caojiangwei'),['不推2025卷年、不覆盖官方年份','各职称起止未知','博士生导师为本人资格','原刊2024-09-03发表']);
});
test('Chai unknown doctoral award retains thesis title and stage guidance while lecturer treatment is not a lecturer appointment',async()=>{
 const p=person('chaiguozhi');assert.deepEqual(p.education.map(e=>e.degree_awarded),[true,null,false]);assert.deepEqual(p.mentors.map(m=>m.name),['薛德胜','C. K. Ong']);assert.deepEqual(p.mentors.map(m=>m.education_event_id),['lzu-chaiguozhi-doctorate','lzu-chaiguozhi-postdoc']);assert.equal(p.appointments[0].title,'优博培育计划留校（讲师待遇）');visible(await profile('chaiguozhi'),['异质结构软磁材料的高频磁特性研究','非正式论文导师认证','不改成已任讲师','博士后、博士学习与兰大任职原区间重叠']);visible(await graph('chaiguozhi'),['薛德胜','C. K. Ong']);
});
test('Huang two bachelor labels remain one original stage without invented legal equivalence or two awards',async()=>{
 const p=person('huangjianping');assert.deepEqual(p.education.map(e=>e.degree_awarded),[true,true,true,false]);const e=p.education.find(e=>e.event_id==='huangjianping-nim-bachelor');assert.equal(e.degree,'双学士');assert.equal(p.education.length,4);assert(p.education.every(e=>e.degree_awarded_date===null));assert.equal(p.mentors.length,0);visible(await profile('huangjianping'),['院系双学士/团队学士双标签','大气探测、天气动力','不拆两授位事件、不推法律双学位制度','博士生导师为本人资格','作者星号与et al.原样']);
});

test('Ge unique integrated doctorate does not create a masters award or a McMaster degree',async()=>{
 const p=person('gelong');assert.deepEqual(p.education.map(e=>e.degree_awarded),[true,true,false]);assert.equal(p.education.length,3);assert.equal(stages(p,'master').length,0);assert.equal(p.mentors.length,0);visible(await profile('gelong'),['仍一条连读事件，不新增独立硕士授位或事件','不推McMaster授位或联授','不按路径推现职','无图例不自动推共同第一作者']);
});
test('Shi formal Dr.rer.nat credential stays one doctorate while master and slash affiliation stay unresolved',async()=>{
 const p=person('shilei');assert.deepEqual(p.education.map(e=>e.degree_awarded),[true,null,true,false]);assert.equal(p.education[2].degree,'博士（Dr.rer.nat）');assert.equal(p.mentors.length,4);assert.equal(p.mentors.filter(m=>m.type==='postdoctoral_mentor').length,2);visible(await profile('shilei'),['不据此推第二学位或法律等价','Cancer Research UK Manchester Institute/英国曼彻斯特大学','department空，不推上下级','全英文主讲人']);visible(await graph('shilei'),['郭爱珍','Heiko Hermeking','Michela Garofalo','Caroline Dive']);
});
test('Wang original award years and book contributions do not imply sole authorship',async()=>{
 const p=person('wangdaqiao');assert.deepEqual(p.education.map(e=>e.degree_awarded_year),[1994,2001,2008,null]);assert(p.publications.every(w=>w.authors===null));assert.equal(p.mentors.length,0);visible(await profile('wangdaqiao'),['不补入学、授位月日或精确专业','原角色：出版专著','原角色：参编教材','不推完整署名或独著']);
});
test('Zhang Jin two named schools cannot be assigned by order to three degree stages',async()=>{
 const p=person('zhangjin');assert.deepEqual(p.education.map(e=>e.degree_awarded),[true,true,true,false,false]);assert(p.education.slice(0,3).every(e=>e.institution===null));assert.equal(p.mentors.length,0);visible(await profile('zhangjin'),['陕西师范大学与中国人民大学并列','三阶段机构/日期保持未知，不按顺序分配','不新增联合培养或双学位','两图书作者串与本人具体作者角色未知']);
});
test('Zheng preserves explicit award months and merged career without populating old basic-mathematics unit',async()=>{
 const p=person('zhengbing');assert.equal(p.department_id,'lzu-math-stat');assert.deepEqual(p.education.slice(0,3).map(e=>e.degree_awarded_date),[null,'1989-07','2003-07']);assert.equal(p.appointments.length,2);assert.equal(p.publications.length,0);const e=p.education.find(e=>e.event_id==='lzu-zhengbing-training-5');assert.equal(e.degree_awarded,false);assert.equal(e.start,null);assert.equal(e.end,null);visible(await profile('zhengbing'),['2003年至今副教授（博士后）、教授是合并职业句','不赋整个区间','不与基础数学研究所合并','不是本人无作品']);
});
test('Li Wantong source spelling and invitation hosts remain distinct from three actual stage guides',async()=>{
 const p=person('liwantong');assert.equal(p.department_id,'lzu-math-stat');assert.deepEqual(p.mentors.map(m=>m.name),['叶其孝','陈文源','范先令']);assert(p.appointments.slice(1).every(a=>a.institution===null));visible(await profile('liwantong'),['Wan-Tong Li与Wan-Tog Li原拼写不同','Shigui Ruan、辛周平仅访问邀请人，不增导师','不与基础数学研究所合并','机构保持未知']);visible(await graph('liwantong'),['叶其孝','陈文源','范先令']);
});
test('Zhang Tongsheng joining date does not become professor or director start',async()=>{
 const p=person('zhangtongsheng');assert.deepEqual(p.education.map(e=>e.degree_awarded),[true,true,true,false,false]);assert.equal(p.appointments[0].start,'2008-07');assert.equal(p.appointments[0].title,null);assert.equal(p.appointments[1].start,null);assert.equal(p.mentors.length,0);visible(await profile('zhangtongsheng'),['2008年7月为入校工作时间，不追溯教授或所长起任','2007至2009山东师范大学博士后与2008年7月入校工作原区间并存','本人指导资格不变为本人师承']);
});
test('LZU actual profiles preserve all notes, source qualifications, teaching roles and no object/None placeholders',async()=>{
 for(const p of mapping.people){const html=await profile(p.person_id.slice(4));visible(html,p.unknowns);assert(!html.includes('[object Object]'));assert(!html.includes('卷None'));
 for(const list of [p.education,p.appointments,p.publications])for(const item of list)if(item.note)visible(html,[item.note]);
 for(const t of p.teaching){const title=t.name||t.course||(t.courses||[]).join('、');const rows=[...html.matchAll(/<li>[\s\S]*?<\/li>/g)].map(m=>m[0]);const row=rows.find(r=>r.includes('<strong>'+escapeHtml(title)+'</strong>'));assert(row,p.person_id+' '+title);if(t.role)visible(row,[t.role]);if(t.note)visible(row,[t.note]);}
 }
});
