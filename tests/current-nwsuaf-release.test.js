import {createImmutableCohortRenderer} from './immutable-cohort-renderer.js';
import {readAtlasFile,createAtlasFetch} from './atlas-test-io.js';
import {test} from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {matches, stages, mentorEvent, mentorEvents, mentorOfficialUrl, mentorProfileRoute, escapeHtml} from '../site/model.js';
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
const mapping=JSON.parse(fs.readFileSync(new URL('./fixtures/independent-nwsuaf12-source-mapping.json',import.meta.url)));
test('actual NWSUAF cohort exactly preserves independently reviewed fields, identities and scope',()=>{
 assert.deepEqual(mapping.people.map(p=>p.person_id),["nwsuaf-chengzhihui","nwsuaf-dinglong","nwsuaf-wufuyong","nwsuaf-xuchenyang","nwsuaf-chenhuatao","nwsuaf-gaolexi","nwsuaf-xugong","nwsuaf-yangzhaofu","nwsuaf-yaoliuyang","nwsuaf-liuweiguo","nwsuaf-lironghua","nwsuaf-hailijuan"]);
 assert(mapping.people.every(p=>p.data_batch_id==='faculty-batch-nwsuaf12-independent-20261026'));
 assert.equal(db.people.length,909+mapping.people.length+oucMapping.people.length+lzuMapping.people.length+sjtuMapping.people.length+thuMapping.people.length+pkuMapping.people.length+zjuMapping.people.length+mixedMapping.people.length+njuSecondMapping.people.length+seuSecondMapping.people.length+nkuSecondMapping.people.length);assert.equal(db.build_id,roster.build_id);
 for(const expected of mapping.people){
  const actual=db.people.find(p=>p.person_id===expected.person_id);assert.deepEqual(actual,expected);
  assert.equal(typeof actual.department,'string');assert(actual.department.length>0);
  assert(matches(actual,{q:actual.name},db.org_units));assert(matches(actual,{school:'nwsuaf',org:actual.department_id},db.org_units));
  assert(!matches(actual,{school:'seu'},db.org_units));assert.equal(actual.quick_link_eligible,expected.quick_link_eligible);assert.equal(actual.include_in_current_faculty_count,expected.include_in_current_faculty_count);
  for(const stage of ['bachelor','master','doctor']) for(const event of stages(actual,stage)){assert.equal(event.event_kind,'degree');assert.equal(event.degree_awarded,true);}
 }
});
const {render}=createImmutableCohortRenderer({db,roster,fixtureId:import.meta.url});
for(const expected of mapping.people)test('actual NWSUAF profile and lineage preserve '+expected.name,async()=>{
 const nodes=await render('#/person/'+expected.person_id);const html=['#main','#profile-content'].map(k=>nodes(k).innerHTML).join('\n');
 assert(html.includes(expected.name));assert(html.includes('西北农林科技大学'));
 const lineage=await render('#/person/'+expected.person_id+'/lineage');
 const relationHtml=['#main','#profile-content','#mind-stage'].map(k=>lineage(k).innerHTML).join('\n');
 for(const mentor of expected.mentors){assert(relationHtml.includes(mentor.name));assert(relationHtml.includes(mentor.type_label||mentor.type));}
 if(expected.mentors.length===0)assert(relationHtml.includes('0条已收录关系'));
});

test('NWSUAF all non-null research_interests are renderable strings, not nested source objects',()=>{
 for(const p of mapping.people){const actual=db.people.find(x=>x.person_id===p.person_id);if(actual.research_interests!==undefined&&actual.research_interests!==null)assert.equal(typeof actual.research_interests,'string',p.person_id);}
});
test('NWSUAF research sidebar displays each reviewed research text exactly without object stringification',async()=>{
 for(const p of mapping.people){const nodes=await render('#/person/'+p.person_id),html=nodes('#profile-content').innerHTML,aside=html.match(/<aside class="profile-info"[\s\S]*?<\/aside>/)?.[0];assert(aside,p.person_id);const text=p.research_interests||'待补录';assert.equal(typeof text,'string',p.person_id);assert(aside.includes('<h3>研究方向</h3><p>'+escapeHtml(text)+'</p>'),p.person_id+' exact research panel');assert(!html.includes('[object Object]'),p.person_id+' object stringification');}
});

const person=id=>db.people.find(p=>p.person_id==='nwsuaf-'+id);
const event=(p,suffix)=>p.education.find(e=>e.event_id===p.person_id+'-'+suffix);
const visible=(html,terms)=>{for(const term of terms)assert(html.includes(escapeHtml(term)),term);};
async function profile(id){const n=await render('#/person/nwsuaf-'+id);return n('#profile-content').innerHTML;}
async function graph(id){const n=await render('#/person/nwsuaf-'+id+'/lineage');return n('#mind-stage').innerHTML;}
test('NWSUAF all source limits, work qualifiers and teaching roles survive actual rendering',async()=>{
 for(const p of mapping.people){const html=await profile(p.person_id.slice(7));
  visible(html,p.unknowns);for(const list of [p.education,p.appointments,p.publications])for(const row of list)if(row.note)visible(html,[row.note]);
  for(const t of p.teaching){const title=t.name||t.course||(t.courses||[]).join('、');const rows=[...html.matchAll(/<li>[\s\S]*?<\/li>/g)].map(m=>m[0]);const row=rows.find(r=>r.includes('<strong>'+escapeHtml(title)+'</strong>'));assert(row,p.person_id+' '+title);if(t.note)visible(row,[t.note]);if(t.role)visible(row,[t.role]);}
 }
});
test('Cheng official retirement overrides old present title and combined degrees remain one event',async()=>{
 const p=person('chengzhihui'),e=event(p,'bachelor-master-combined');assert.equal(p.retirement_month,'2025-06');assert.equal(p.current_employment_status,'retired_or_emeritus_officially_listed');assert.equal(p.include_in_current_faculty_count,false);assert.equal(e.degree_awards_explicit_count,2);assert.deepEqual(e.degree_levels,['bachelor','master']);assert.equal(p.education.length,3);assert.equal(e.degree_awarded_date,null);visible(await profile('chengzhihui'),['离退时间2025年6月','不推退休原因、返聘','1合并教育记录/2原明确学位']);
});
test('Ding identity-based doctorate is distinct from non-award Alberta training',async()=>{
 const p=person('dinglong');assert.deepEqual(p.education.map(e=>e.degree_awarded),[null,null,true,false]);assert.equal(event(p,'alberta-joint').underlying_doctoral_degree_awarded,true);assert.equal(event(p,'doctor').degree,'博士');visible(await profile('dinglong'),['官网独立本人简介','未核原学位证','非另获该校博士']);assert.equal(p.mentors.length,0);
});
test('Wu two stage guides do not gain a third postdoctoral mentor from a professor parenthesis',async()=>{
 const p=person('wufuyong');assert.deepEqual(p.education.map(e=>e.degree_awarded),[true,null,null,false,false]);assert.deepEqual(p.mentors.map(m=>m.name),['毕银丽','黄铭洪']);assert.deepEqual(p.mentors.map(m=>m.education_event_id),[p.person_id+'-master',p.person_id+'-doctor']);visible(await profile('wufuyong'),['括号黄铭洪教授仅原背景关联','不增加第三条导师关系']);visible(await graph('wufuyong'),['毕银丽','黄铭洪']);
});
test('Xu Chenyang keeps four explicit award months and two different same-month bachelors',async()=>{
 const p=person('xuchenyang');assert.deepEqual(p.education.map(e=>e.degree_awarded_date),['2010-06','2010-06','2013-06','2017-01']);assert.deepEqual(p.education.slice(0,2).map(e=>e.degree),['农学学士','文学学士']);assert(p.education.every(e=>e.start===null&&e.end===null));visible(await profile('xuchenyang'),['不推法律双学位制度','原明确2010-06获农学学士','原明确2010-06获文学学士','原明确2017-01获农学博士']);
});
test('Chen keeps three degree-stage guides and two non-degree postdoctoral collaborators',async()=>{
 const p=person('chenhuatao');assert.equal(p.mentors.length,5);assert.equal(p.mentors.filter(m=>m.type==='postdoctoral_mentor').length,2);for(const m of p.mentors.filter(m=>m.type==='postdoctoral_mentor'))assert.equal(p.education.find(e=>e.event_id===m.education_event_id).degree_awarded,false);visible(await profile('chenhuatao'),['3阶段导师','2合作导师','在职博士后','非原论文认证']);visible(await graph('chenhuatao'),['宋晓平','靳亚平','服部真彰','冈村均']);
});
test('Gao uncertain Capital master and Ghent training do not inherit postdoctoral guidance',async()=>{
 const p=person('gaolexi');assert.equal(event(p,'master_capital').degree_awarded,null);assert.equal(event(p,'joint_training').degree_awarded,false);assert.equal(p.mentors.length,1);assert.equal(p.mentors[0].education_event_id,p.person_id+'-postdoc');assert.equal(p.mentors[0].type,'postdoctoral_mentor');visible(await profile('gaolexi'),['首都医科大学仅硕士研究生学习，授位未知','不挂博士学位事件或原论文']);visible(await graph('gaolexi'),['张涌']);
});
test('Xu Gong upper four courses stay four despite a conflicting lower biography',async()=>{
 const p=person('xugong');assert.deepEqual(p.teaching.map(t=>t.name),['仪器分析','专业英语','农药研发策略与技术进展','现代农药分子设计原理及方法']);const html=await profile('xugong');visible(html,['结构化只采用上段4门，不合并为同时5门','药物合成','更新于2026年3月','原明确角色：博士后']);assert(!html.includes('<strong>药物合成</strong>'));
});
test('Yang preserves historical source names and contributor role without inventing mentors',async()=>{
 const p=person('yangzhaofu');assert.equal(p.mentors.length,0);visible(await profile('yangzhaofu'),['加拿大圭儿夫大学','不回填历史前身','参编不是独著或主编','鼠害防治','原明确角色：访问学者']);assert.equal(p.education.filter(e=>e.degree_awarded===false).length,2);
});
test('Yao integrated education does not create a master and Clark remains a non-degree visit',async()=>{
 const p=person('yaoliuyang');assert.equal(p.education.length,3);assert.deepEqual(p.education.map(e=>e.degree_awarded),[true,true,false]);assert.equal(stages(p,'master').length,0);visible(await profile('yaoliuyang'),['不另造硕士','国家留学基金委是资助方，不是接收单位','美国克拉克大学']);
});
test('Liu preserves separate unit labels and explicit award years without rebuilding hierarchy',async()=>{
 const p=person('liuweiguo');assert.deepEqual(p.education.map(e=>e.degree_awarded_year),[2007,2010,2015]);visible(await profile('liuweiguo'),['森林资源管理（原森林经理）教研室','智慧林业与森林生态系','不推更名或上下级重构','职称开始时间未知']);
});
test('Li keeps unknown graduate awards and absent work author lists',async()=>{
 const p=person('lironghua');assert.deepEqual(p.education.map(e=>e.degree_awarded),[true,null,null]);assert(p.publications.every(w=>w.authors_as_source===null));visible(await profile('lironghua'),['两篇书目没有作者表','不凭本人页面归属补本人为作者','授位未单独核实']);
});
test('Hai parallel lecturer and associate-professor claims do not invent promotion dates',async()=>{
 const p=person('hailijuan');assert(p.education.every(e=>e.degree_awarded===true));assert.equal(p.appointments[0].title,null);assert.equal(p.appointments[0].start,'2016-11');visible(await profile('hailijuan'),['个人页讲师、目录副教授两来源并列','不推更新先后或晋升日期','2016.11仅工作区间起点']);
});
