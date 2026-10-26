import {readAtlasFile} from './atlas-test-io.js';
import {createImmutableCohortRenderer} from './immutable-cohort-renderer.js';
import {test} from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {matches,escapeHtml,mentorEvents,mentorOfficialUrl,mentorProfileRoute} from '../site/model.js';
const nkuSecondMapping=JSON.parse(fs.readFileSync(new URL('./fixtures/independent-nku11-second-source-mapping.json',import.meta.url)));
const db=readAtlasFile(new URL('../site/atlas.json',import.meta.url));
const roster=JSON.parse(fs.readFileSync(new URL('../site/rosters.json',import.meta.url)));
const mapping=JSON.parse(fs.readFileSync(new URL('./fixtures/independent-seu11-second-source-mapping.json',import.meta.url)));
const ids=["seu-sunzhengming", "seu-jintanhua", "seu-libeilei", "seu-sunguiju", "seu-shenyang-wave208", "seu-zhengdedong-wave208", "seu-yemaoxin", "seu-huhanhui", "seu-bianshaobin", "seu-liyinan", "seu-zhangjingjing-sociology"];
test('actual SEU second cohort preserves all independently reviewed identities and complete fields',()=>{
 assert.equal(db.people.length,1004+mapping.people.length+nkuSecondMapping.people.length);assert.equal(db.build_id,roster.build_id);assert.deepEqual(mapping.people.map(p=>p.person_id),ids);
 for(const expected of mapping.people){const actual=db.people.find(p=>p.person_id===expected.person_id);assert.deepEqual(actual,expected);assert.equal(actual.data_batch_id,'faculty-batch-seu11-second-independent-20261026');assert(matches(actual,{q:actual.name},db.org_units));assert(matches(actual,{school:'seu',org:actual.department_id},db.org_units));assert(!matches(actual,{school:'lzu'},db.org_units));}
});
const {render}=createImmutableCohortRenderer({db,roster,fixtureId:import.meta.url});
for(const expected of mapping.people)test('actual SEU second profile and lineage preserve '+expected.name,async()=>{
 const nodes=await render('#/person/'+expected.person_id),html=nodes('#main').innerHTML+'\n'+nodes('#profile-content').innerHTML;assert(html.includes(expected.name));assert(html.includes('东南大学'));
 const graph=await render('#/person/'+expected.person_id+'/lineage'),relationHtml=['#main','#profile-content','#mind-stage'].map(k=>graph(k).innerHTML).join('\n');
 for(const mentor of expected.mentors||[]){assert(relationHtml.includes(escapeHtml(mentor.name)));assert(relationHtml.includes(escapeHtml(mentor.type_label||mentor.type)));}
});
test('SEU second non-null research fields are renderable strings',()=>{
 for(const expected of mapping.people){const p=db.people.find(x=>x.person_id===expected.person_id);if(p.research_interests!==undefined&&p.research_interests!==null)assert.equal(typeof p.research_interests,'string',p.person_id);}
});
test('SEU second actual research sidebar displays exact reviewed text and never object stringification',async()=>{
 for(const p of mapping.people){const n=await render('#/person/'+p.person_id),html=n('#profile-content').innerHTML,aside=html.match(/<aside class="profile-info"[\s\S]*?<\/aside>/)?.[0];assert(aside,p.person_id);const text=p.research_interests||'待补录';assert.equal(typeof text,'string');assert(aside.includes('<h3>研究方向</h3><p>'+escapeHtml(text)+'</p>'),p.person_id+' exact research panel');assert(!html.includes('[object Object]'),p.person_id);}
});
test('SEU second reviewed uncertainty text remains visible on each actual profile',async()=>{
 for(const p of mapping.people){const n=await render('#/person/'+p.person_id),html=n('#main').innerHTML+'\n'+n('#profile-content').innerHTML;for(const note of p.unknowns||[])assert(html.includes(escapeHtml(note)),p.person_id+' '+note);}
});

// Final groups 1 and 3 source-specific expectations; group 2 remains pending.
const semanticCases={"seu-sunzhengming": {"phrases": ["2024-08-23页面发布时间与2026年作品不等人事更新", "联合培养博士为单一培养事件", "JSPS与美国Drexel研究仅泛述"], "awards": [null, true, false, false], "dates": [null, null, null, null], "years": [null, null, null, null], "mentors": []}, "seu-jintanhua": {"phrases": ["空书目仅本批没有选定条目", "两博士后机构先后顺序不推日期", "不独立认证当前人事状态"], "awards": [true, true, true, false, false, false, false], "dates": ["2016", "2019", "2023", null, null, null, null], "years": [2016, 2019, 2023, null, null, null, null], "mentors": [["Frank Witlox", "stage_specific_study_under"]]}, "seu-libeilei": {"phrases": ["职业别名李倍雷", "首屏C/D范围", "原职业与博士时间重叠不调和"], "awards": [true, true, true], "dates": [null, null, null], "years": [null, null, null], "mentors": [["谌北新", "stage_specific_study_under"], ["张道一", "stage_specific_study_under"]]}, "seu-sunguiju": {"phrases": ["未把新闻中一次美国进修再加成第五次", "正式论文导师与具体学位阶段未核", "仅列参编孙桂菊"], "awards": [null, null, true, false, false, false, false], "dates": [null, null, "2001-07", null, null, null, null], "years": [null, null, 2001, null, null, null, null], "mentors": [["陈学存", "graduate_research_guidance"]]}, "seu-bianshaobin": {"phrases": ["未读取下一页", "2019-04-24", "2024", "完整作者、出版者元数据及全文未核"], "awards": [], "dates": [], "years": [], "mentors": []}, "seu-liyinan": {"phrases": ["1990-09至1997-03学习区间", "不推同时授位", "工作坊结业证书保留"], "awards": [true, true, true, false, false], "dates": [null, null, null, null, null], "years": [null, null, null, null, null], "mentors": []}, "seu-zhangjingjing-sociology": {"phrases": ["不能据此认定副院长所属学院", "2018年入选", "老年移民生活质量、老龄化社会与文化变迁、数字化技术与养老服务模式"], "awards": [true, true, true], "dates": [null, null, null], "years": [null, null, null], "mentors": []}};
Object.assign(semanticCases,{"seu-shenyang-wave208": {"phrases": ["不拆造各阶段起止或授位日期", "2009任教不是教授/所长起年", "不是两份已核原论文导师证明"], "awards": [null, null, true], "dates": [null, null, null], "years": [null, null, null], "mentors": [["陈薇", "master_supervisor"], ["陈薇", "doctoral_supervisor"]]}, "seu-zhengdedong-wave208": {"phrases": ["联合培养博士只计一个事件", "具体授位学校未知", "齐康仅合作博士后阶段导师"], "awards": [true, true, true, false], "dates": [null, null, null, null], "years": [2004, 2007, 2010, null], "mentors": [["齐康", "postdoctoral_mentor"]]}, "seu-yemaoxin": {"phrases": ["同期国际安全学项目不能累加第二博士", "与日本东北大学不是同一机构", "两作品保原章节/译者类型"], "awards": [true, null, true, false], "dates": [null, null, null, null], "years": [null, null, null, null], "mentors": []}, "seu-huhanhui": {"phrases": ["不能据未见推退休", "不自动将历史校名归并东南大学", "普费弗为原著作者"], "awards": [null, null], "dates": [null, null], "years": [null, null], "mentors": []}});
for(const [id,x] of Object.entries(semanticCases))test('SEU second independent source semantics '+id,async()=>{
 const p=mapping.people.find(p=>p.person_id===id);assert.deepEqual(p.education.map(e=>e.degree_awarded),x.awards);assert.deepEqual(p.education.map(e=>e.degree_awarded_date),x.dates);assert.deepEqual(p.education.map(e=>e.degree_awarded_year),x.years);assert.deepEqual(p.mentors.map(m=>[m.name,m.type]),x.mentors);
 const n=await render('#/person/'+id),html=n('#main').innerHTML+n('#profile-content').innerHTML;for(const term of x.phrases)assert(html.includes(escapeHtml(term)),id+' '+term);
 if(id==='seu-shenyang-wave208'){assert.equal(p.appointments[0].start,'2009');assert.equal(p.appointments[1].start,null);assert.equal(p.education[1].start,null);assert.equal(p.education[2].end,null);}
 if(id==='seu-zhengdedong-wave208'){assert.equal(p.education.filter(e=>e.degree_awarded===true&&e.degree==='博士').length,1);assert.equal(p.education[2].institution,null);assert.equal(p.education[2].degree_awarded_year,2010);assert.equal(p.mentors[0].type,'postdoctoral_mentor');}
 if(id==='seu-yemaoxin'){assert.equal(p.education[0].institution,'日本东北大学');assert.equal(p.education[3].institution,'美国Northeastern University');assert.equal(p.education[1].degree_awarded,null);assert.equal(p.education[0].start,p.education[1].start);assert.equal(p.education[0].end,p.education[1].end);}
 if(id==='seu-huhanhui'){assert.deepEqual(p.education.map(e=>e.institution),['南京工学院','南京工学院']);assert.deepEqual(p.mentors,[]);}
 if(id==='seu-sunzhengming'){assert.equal(p.department_id,'seu-materials-metal');assert.equal(p.education.length,4);assert.equal(p.education[2].institution,null);assert.equal(p.education[2].degree_awarded,false);}
 if(id==='seu-libeilei'){assert.equal(p.department_id,'seu-arts');assert.notEqual(p.department_id,'seu-arts-theory');assert.equal(p.education[2].start,'2001');assert.equal(p.education[2].end,'2004');assert.equal(p.appointments[2].start,'2002');assert.equal(p.appointments[2].end,'2010');}
 if(id==='seu-sunguiju'){assert.equal(p.education[2].degree_awarded_date,'2001-07');assert.equal(p.education.filter(e=>e.degree_awarded===false).length,4);const m=p.mentors[0];assert.equal(m.type,'graduate_research_guidance');assert.equal(m.education_event_id,null);assert.equal(m.formal_dissertation_advisor_verified,false);assert.equal(m.include_in_verified_mentor_count,false);assert.deepEqual(mentorEvents(p,m),[]);assert.equal(mentorOfficialUrl(m),'');assert.equal(mentorProfileRoute(m,db.people),'');const g=await render('#/person/'+id+'/lineage');assert(g('#profile-content').innerHTML.includes('具体学位阶段未知'));assert(g('#mind-stage').innerHTML.includes('陈学存'));}
 if(id==='seu-bianshaobin'){assert.deepEqual(p.education,[]);assert.deepEqual(p.mentors,[]);}
 if(id==='seu-liyinan'){assert.equal(p.education[0].start,null);assert.equal(p.education[1].end,null);assert.equal(p.education[4].degree_awarded,false);assert.equal(p.education[4].degree,'全英文工作坊培训并获结业证书');}
 if(id==='seu-zhangjingjing-sociology'){assert.equal(p.appointments.length,1);assert.equal(p.appointments[0].start,null);assert.equal(p.appointments[0].title,'副教授；副院长');}
});

test('SEU second all event work and teaching notes remain actually visible',async()=>{
 for(const p of mapping.people){const n=await render('#/person/'+p.person_id),html=n('#main').innerHTML+n('#profile-content').innerHTML;for(const key of ['education','appointments','publications','teaching'])for(const item of p[key]||[])if(item.note)assert(html.includes(escapeHtml(item.note)),p.person_id+' '+key+' '+item.note);}
});
