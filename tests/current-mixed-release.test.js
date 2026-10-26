import {readAtlasFile} from './atlas-test-io.js';
import {createImmutableCohortRenderer} from './immutable-cohort-renderer.js';
import {test} from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {matches,escapeHtml} from '../site/model.js';
const njuSecondMapping=JSON.parse(fs.readFileSync(new URL('./fixtures/independent-nju11-second-source-mapping.json',import.meta.url)));
const seuSecondMapping=JSON.parse(fs.readFileSync(new URL('./fixtures/independent-seu11-second-source-mapping.json',import.meta.url)));
const db=readAtlasFile(new URL('../site/atlas.json',import.meta.url));
const roster=JSON.parse(fs.readFileSync(new URL('../site/rosters.json',import.meta.url)));
const mapping=JSON.parse(fs.readFileSync(new URL('./fixtures/independent-neu4-cqu3-sysu2-source-mapping.json',import.meta.url)));
const schools={neu:'东北大学',cqu:'重庆大学',sysu:'中山大学'};
const batches={neu:'faculty-batch-neu4-independent-20261026',cqu:'faculty-batch-cqu3-independent-20261026',sysu:'faculty-batch-sysu2-independent-20261026'};
const ids=["neu-angang", "neu-yanjiaqi", "neu-chengfu", "neu-maomuran", "cqu-liyamei-art", "cqu-yanfugang", "cqu-kongguangyao-medicine", "sysu-xiali", "sysu-gaoru-accounting"];
test('actual MIXED cohort preserves all independently reviewed identities and complete fields',()=>{
 assert.equal(db.people.length,984+mapping.people.length+njuSecondMapping.people.length+seuSecondMapping.people.length);assert.equal(db.build_id,roster.build_id);assert.deepEqual(mapping.people.map(p=>p.person_id),ids);assert.equal(mapping.profile_batches.length,3);assert.deepEqual(mapping.profile_batches.map(b=>b.school_id),['neu','cqu','sysu']);for(const b of mapping.profile_batches){assert.equal(b.batch_id,batches[b.school_id]);assert.equal(b.people_count,mapping.people.filter(p=>p.school_id===b.school_id).length);}
 for(const expected of mapping.people){const actual=db.people.find(p=>p.person_id===expected.person_id);assert.deepEqual(actual,expected);assert.equal(actual.data_batch_id,batches[actual.school_id]);assert(Object.hasOwn(schools,actual.school_id));assert(matches(actual,{q:actual.name},db.org_units));assert(matches(actual,{school:actual.school_id,org:actual.department_id},db.org_units));assert(!matches(actual,{school:'lzu'},db.org_units));}
});
const {render}=createImmutableCohortRenderer({db,roster,fixtureId:import.meta.url});
for(const expected of mapping.people)test('actual MIXED profile and lineage preserve '+expected.name,async()=>{
 const nodes=await render('#/person/'+expected.person_id),html=nodes('#main').innerHTML+'\n'+nodes('#profile-content').innerHTML;assert(html.includes(expected.name));assert(html.includes(schools[expected.school_id]));
 const graph=await render('#/person/'+expected.person_id+'/lineage'),relationHtml=['#main','#profile-content','#mind-stage'].map(k=>graph(k).innerHTML).join('\n');
 for(const mentor of expected.mentors||[]){assert(relationHtml.includes(escapeHtml(mentor.name)));assert(relationHtml.includes(escapeHtml(mentor.type_label||mentor.type)));}
});
test('MIXED non-null research fields are renderable strings',()=>{
 for(const expected of mapping.people){const p=db.people.find(x=>x.person_id===expected.person_id);if(p.research_interests!==undefined&&p.research_interests!==null)assert.equal(typeof p.research_interests,'string',p.person_id);}
});
test('MIXED actual research sidebar displays exact reviewed text and never object stringification',async()=>{
 for(const p of mapping.people){const n=await render('#/person/'+p.person_id),html=n('#profile-content').innerHTML,aside=html.match(/<aside class="profile-info"[\s\S]*?<\/aside>/)?.[0];assert(aside,p.person_id);const text=p.research_interests||'待补录';assert.equal(typeof text,'string');assert(aside.includes('<h3>研究方向</h3><p>'+escapeHtml(text)+'</p>'),p.person_id+' exact research panel');assert(!html.includes('[object Object]'),p.person_id);}
});
test('MIXED reviewed uncertainty text remains visible on each actual profile',async()=>{
 for(const p of mapping.people){const n=await render('#/person/'+p.person_id),html=n('#main').innerHTML+'\n'+n('#profile-content').innerHTML;for(const note of p.unknowns||[])assert(html.includes(escapeHtml(note)),p.person_id+' '+note);}
});
const person=id=>db.people.find(p=>p.person_id===id);
const visible=(html,terms)=>{for(const term of terms)assert(html.includes(escapeHtml(term)),term);};
async function profile(id){const n=await render('#/person/'+id);return n('#main').innerHTML+'\n'+n('#profile-content').innerHTML;}
test('nine independently selected IDs belong to exactly four NEU three CQU and two SYSU people',()=>{
 const expected={'neu-angang':'neu','neu-yanjiaqi':'neu','neu-chengfu':'neu','neu-maomuran':'neu','cqu-liyamei-art':'cqu','cqu-yanfugang':'cqu','cqu-kongguangyao-medicine':'cqu','sysu-xiali':'sysu','sysu-gaoru-accounting':'sysu'};assert.deepEqual(Object.fromEntries(mapping.people.map(p=>[p.person_id,p.school_id])),expected);assert.deepEqual(['neu','cqu','sysu'].map(s=>mapping.people.filter(p=>p.school_id===s).length),[4,3,2]);
});
test('An Gang appointment qualification and award precision remain separate with typed stage guidance',async()=>{
 const p=person('neu-angang');assert.equal(p.appointments.length,0);assert.deepEqual(p.education.map(e=>e.degree_awarded),[true,true,true,false,false]);assert.deepEqual(p.education.slice(0,3).map(e=>e.degree_awarded_date),['1994','2003','2007']);assert.deepEqual(p.mentors.map(m=>m.type),['doctoral','postdoc','visiting']);visible(await profile(p.person_id),['入职时间2007-06-26','2016获评副教授','2023获博士生指导教师资格','不把2007作为副教授或博导起始','系统研究生(博士后)标签不改作学位','只元数据，未读全文']);
});
test('Yan Jiaqi nondegree joint study and three course audience groups do not imply teaching role',async()=>{
 const p=person('neu-yanjiaqi');assert.deepEqual(p.education.map(e=>e.degree_awarded),[true,true,true,false]);assert.deepEqual(p.education.slice(1,3).map(e=>e.degree_awarded_year),[2017,2020]);assert.equal(p.mentors.length,3);assert.equal(p.teaching.length,3);assert(p.teaching.every(t=>t.role==='课程列示'));visible(await profile(p.person_id),['联合培养事件本身不计另一个博士学位','学习末月不是授位月','学术型硕士研究生/工程硕士（MEM）','MBA','具体讲授角色、学期和当前开课未知']);
});
test('Cheng Fu three reported degrees and doctoral stage guide retain source limits',async()=>{
 const p=person('neu-chengfu');assert.equal(p.education.length,3);assert(p.education.every(e=>e.degree_awarded===true&&e.degree_awarded_date===null&&e.degree_awarded_year===null));assert.equal(p.mentors.length,1);assert.equal(p.mentors[0].name,'王福胜');assert.deepEqual(p.appointments.map(a=>a.start),['2016-01','2022-01']);visible(await profile(p.person_id),['会计学是学科，不推会计学系行政机构','保博士阶段指导，不认证原论文导师','书目仅选原两篇已列刊卷期页作品，不代表完整成果']);
});
test('Mao Muran one visit retains conflicting intervals without inventing two events',async()=>{
 const p=person('neu-maomuran');assert.equal(p.education.length,4);assert.equal(p.education[3].degree_awarded,false);assert.equal(p.education[3].start,null);assert.equal(p.education[3].end,null);assert.equal(p.appointments.length,0);visible(await profile(p.person_id),['简介2009.7–2010.7','列表2009.08–2010.08','两日期并存，未调和','非两个访问或学位','第一作者与唯一作者角色不同']);
});
test('Li Yamei explicit doctoral field survives empty education section without fabricated school',async()=>{
 const p=person('cqu-liyamei-art');assert.equal(p.education.length,1);assert.equal(p.education[0].degree_awarded,true);assert.equal(p.education[0].institution,null);assert.equal(p.education[0].degree_awarded_date,null);visible(await profile(p.person_id),['教育经历栏目空不等于未受教育','硕导是指导他人的资格','不推本人独著或作者顺序']);
});
test('Yan Fugang graduation month and postdoc exit do not imply award or employment date',async()=>{
 const p=person('cqu-yanfugang');assert.equal(p.department_id,'cqu-mathematics-statistics');assert.deepEqual(p.education.map(e=>e.degree_awarded),[true,true,false,false]);assert.equal(p.education[0].degree_awarded_date,null);assert.equal(p.appointments[0].title,'机构工作');assert.equal(p.appointments[0].start,null);visible(await profile(p.person_id),['博士毕业月2020-06与实际授位日期分开','不把博士后结束月当入职或讲师起任','2024及to appear保持原状态']);
});
test('Kong Guangyao merged bachelor master and overlapping professorships remain unresolved',async()=>{
 const p=person('cqu-kongguangyao-medicine');assert.equal(p.education.length,3);assert.deepEqual(p.education.map(e=>e.degree_awarded),[null,true,false]);assert.equal(p.education[0].degree,'本硕');assert.deepEqual(p.appointments.map(a=>a.start),['2017-01','2024-07']);visible(await profile(p.person_id),['不拆两个授位事件','不推双聘、离任','西安交通大学第二附属医院','重庆大学附属涪陵医院','Kong G#标记含义未知']);
});
test('Xia Li joint doctorate visit and postdoc remain distinct nondegrees with stage collaborators',async()=>{
 const p=person('sysu-xiali');assert.deepEqual(p.education.map(e=>e.degree_awarded),[true,true,false,false,false]);assert.deepEqual(p.education.slice(0,2).map(e=>e.degree_awarded_year),[2002,2007]);assert.equal(p.mentors.length,2);assert.equal(p.teaching.length,9);assert.deepEqual(p.teaching.map(t=>t.level),['本科生','本科生','本科生','研究生','研究生','研究生','研究生','本科生','研究生']);visible(await profile(p.person_id),['博士生联合培养非第二博士','曹希仁仅博士联合培养阶段导师','Peter Glynn为访问阶段合作导师','清华副教授原2013至2019','本人博导资格自2018年','36:7不擅解释文章号']);
});
test('Gao Ru double-degree labels do not create extra events or award months and unit identities stay distinct',async()=>{
 const p=person('sysu-gaoru-accounting');assert.equal(p.education.length,4);assert(p.education.every(e=>e.degree_awarded===true&&e.degree_awarded_date===null));assert.equal(p.education[0].degree_awarded_year,2014);assert.equal(p.appointments[0].start,'2026-06');visible(await profile(p.person_id),['2014.06仅学习终点，不推授位月','国际贸易硕士（双学位）与会计学硕士分别原两个条目','会计学学士、英语双学士保留同一本科条目','两者组织关系、是否等同或改名未知','页面博士后招生是招收角色','Gao, R.均原列第2作者']);
});
test('all mixed-cohort evidence notes work types and course roles are rendered by the actual app',async()=>{
 for(const p of mapping.people){const html=await profile(p.person_id);for(const e of p.education)if(e.note)visible(html,[e.note]);for(const a of p.appointments||[])if(a.note)visible(html,[a.note]);
 for(const w of p.publications||[]){visible(html,[w.title,w.type_label||w.type]);if(w.note)visible(html,[w.note]);}
 for(const t of p.teaching||[]){const name=t.name||t.course||t.title,rows=[...html.matchAll(/<li>[\s\S]*?<\/li>/g)].map(m=>m[0]);const row=rows.find(r=>r.includes('<strong>'+escapeHtml(name)+'</strong>')&&(!t.note||r.includes(escapeHtml(t.note))));assert(row,p.person_id+' '+name);if(t.role)visible(row,[t.role]);if(t.note)visible(row,[t.note]);}}
});
test('final mixed cohort counts distinguish qualifications nondegrees jobs stage relations and teaching groups',()=>{
 const es=mapping.people.flatMap(p=>p.education);assert.equal(es.length,33);assert.deepEqual([true,false,null].map(v=>es.filter(e=>e.degree_awarded===v).length),[22,10,1]);assert.equal(mapping.people.flatMap(p=>p.appointments||[]).length,13);assert.equal(mapping.people.flatMap(p=>p.mentors||[]).length,9);assert.equal(mapping.people.flatMap(p=>p.publications||[]).length,17);assert.equal(mapping.people.flatMap(p=>p.teaching||[]).length,12);
});
