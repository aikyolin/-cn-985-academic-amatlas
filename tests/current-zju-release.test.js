import {readAtlasFile} from './atlas-test-io.js';
import {createImmutableCohortRenderer} from './immutable-cohort-renderer.js';
import {test} from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {matches,escapeHtml} from '../site/model.js';
const mixedMapping=JSON.parse(fs.readFileSync(new URL('./fixtures/independent-neu4-cqu3-sysu2-source-mapping.json',import.meta.url)));
const db=readAtlasFile(new URL('../site/atlas.json',import.meta.url));
const roster=JSON.parse(fs.readFileSync(new URL('../site/rosters.json',import.meta.url)));
const mapping=JSON.parse(fs.readFileSync(new URL('./fixtures/independent-zju7-source-mapping.json',import.meta.url)));
const ids=["zju-baozehua", "zju-jinweifeng", "zju-zhoujia", "zju-zuhui", "zju-liudonghong", "zju-louhansong-literature", "zju-wuxifeng"];
test('actual ZJU cohort preserves all independently reviewed identities and complete fields',()=>{
 assert.equal(db.people.length,977+mapping.people.length+mixedMapping.people.length);assert.equal(db.build_id,roster.build_id);assert.deepEqual(mapping.people.map(p=>p.person_id),ids);
 for(const expected of mapping.people){const actual=db.people.find(p=>p.person_id===expected.person_id);assert.deepEqual(actual,expected);assert.equal(actual.data_batch_id,'faculty-batch-zju7-independent-20261026');assert(matches(actual,{q:actual.name},db.org_units));assert(matches(actual,{school:'zju',org:actual.department_id},db.org_units));assert(!matches(actual,{school:'lzu'},db.org_units));}
});
const {render}=createImmutableCohortRenderer({db,roster,fixtureId:import.meta.url});
for(const expected of mapping.people)test('actual ZJU profile and lineage preserve '+expected.name,async()=>{
 const nodes=await render('#/person/'+expected.person_id),html=nodes('#main').innerHTML+'\n'+nodes('#profile-content').innerHTML;assert(html.includes(expected.name));assert(html.includes('浙江大学'));
 const graph=await render('#/person/'+expected.person_id+'/lineage'),relationHtml=['#main','#profile-content','#mind-stage'].map(k=>graph(k).innerHTML).join('\n');
 for(const mentor of expected.mentors||[]){assert(relationHtml.includes(escapeHtml(mentor.name)));assert(relationHtml.includes(escapeHtml(mentor.type_label||mentor.type)));}
});
test('ZJU non-null research fields are renderable strings',()=>{
 for(const expected of mapping.people){const p=db.people.find(x=>x.person_id===expected.person_id);if(p.research_interests!==undefined&&p.research_interests!==null)assert.equal(typeof p.research_interests,'string',p.person_id);}
});
test('ZJU actual research sidebar displays exact reviewed text and never object stringification',async()=>{
 for(const p of mapping.people){const n=await render('#/person/'+p.person_id),html=n('#profile-content').innerHTML,aside=html.match(/<aside class="profile-info"[\s\S]*?<\/aside>/)?.[0];assert(aside,p.person_id);const text=p.research_interests||'待补录';assert.equal(typeof text,'string');assert(aside.includes('<h3>研究方向</h3><p>'+escapeHtml(text)+'</p>'),p.person_id+' exact research panel');assert(!html.includes('[object Object]'),p.person_id);}
});
test('ZJU reviewed uncertainty text remains visible on each actual profile',async()=>{
 for(const p of mapping.people){const n=await render('#/person/'+p.person_id),html=n('#main').innerHTML+'\n'+n('#profile-content').innerHTML;for(const note of p.unknowns||[])assert(html.includes(escapeHtml(note)),p.person_id+' '+note);}
});
const person=id=>db.people.find(p=>p.person_id==='zju-'+id);
const visible=(html,terms)=>{for(const term of terms)assert(html.includes(escapeHtml(term)),term);};
async function profile(id){const n=await render('#/person/zju-'+id);return n('#main').innerHTML+'\n'+n('#profile-content').innerHTML;}
test('Bao Zehua directory scope and three stage guides do not become verified thesis supervision',async()=>{
 const p=person('baozehua');assert.deepEqual(p.education.map(e=>e.degree_awarded),[true,true,false]);assert.deepEqual(p.education.slice(0,2).map(e=>e.degree_awarded_year),[2010,2017]);assert.equal(p.mentors.length,3);assert.deepEqual(p.mentors.map(m=>m.type),['undergraduate','doctoral','postdoc']);visible(await profile('baozehua'),['独立目录只核杭州国际科创中心','不冒称核过该学院当前独立师资名录','不能推断哈佛博士后','同一2018–2020经历','不认证正式论文导师']);const n=await render('#/person/'+p.person_id+'/lineage');visible(n('#profile-content').innerHTML+n('#mind-stage').innerHTML,['饶子和','Huimin Zhao','Ahmad S. Khalil']);
});
test('Liu Donghong two read pages do not duplicate degrees or assign the associated 2006 as award year',async()=>{
 const p=person('liudonghong');assert.equal(p.education.length,3);assert(p.education.every(e=>e.degree_awarded===true&&e.degree_awarded_date===null&&e.degree_awarded_year===null));assert.equal(p.publications.length,0);visible(await profile('liudonghong'),['仅已读个人页1/7及2/7','重复教育只记一次','2006为博士条目关联年','书目0不表示本人无作品','未造带时间任职']);
});
test('Jin Weifeng three degrees and two schools remain unallocated and part-time directory bounded',async()=>{
 const p=person('jinweifeng');assert.equal(p.education.length,3);assert(p.education.every(e=>e.degree_awarded===true&&e.institution===null&&e.degree_awarded_date===null&&e.degree_awarded_year===null));assert.equal(p.appointments.length,0);visible(await profile('jinweifeng'),['厦门大学、浙江大学与三学位仅共同列举','不按顺序猜配','兼职研究员目录具名','不能改全职','不能把光华法学院教授拼成研究院教授']);
});
test('Zhou Jia explicit award years do not supply study intervals',async()=>{
 const p=person('zhoujia');assert.deepEqual(p.education.map(e=>e.degree_awarded_year),[2003,2006,2010]);assert(p.education.every(e=>e.start===null&&e.end===null&&e.degree_awarded_date===null));visible(await profile('zhoujia'),['不补学习起止、毕业年或授位月日','两来源标签不强行替换','阅读器导航不是浏览器目录点击']);
});
test('Zu Hui graduation and combined graduate entry do not become stage or appointment start dates',async()=>{
 const p=person('zuhui');assert.equal(p.education.length,3);assert(p.education.every(e=>e.degree_awarded===true&&e.degree_awarded_year===null&&e.degree_awarded_date===null));assert(p.education.slice(1).every(e=>e.start===null&&e.end===null));assert.equal(p.appointments[0].start,null);assert.equal(p.appointments[1].start,'1995');visible(await profile('zuhui'),['1987仅毕业年不另填授位年','1989是共同研究生入学语境','不把1987当任职起年','不组合为现在历史学院教授起任']);
});
test('Lou Hansong arrival association is not a professorial appointment or an award win',async()=>{
 const p=person('louhansong-literature');assert.equal(p.education.length,1);assert.equal(p.education[0].degree_awarded,true);assert.equal(p.education[0].institution,null);assert.equal(p.education[0].degree_awarded_date,null);assert.equal(p.education[0].degree_awarded_year,null);assert.equal(p.appointments.length,1);assert.equal(p.appointments[0].title,'教授');assert.equal(p.appointments[0].start,null);visible(await profile('louhansong-literature'),['1983年9月仅来校年月','不推当年法律学校名称或教授起任','不据候选身份认定获奖者','两部作品分别作者与主编']);
});
test('Wu Xifeng empty education and differently dated units preserve source and excerpt limitations',async()=>{
 const p=person('wuxifeng');assert.deepEqual(p.education,[]);assert.deepEqual(p.mentors,[]);assert.equal(p.appointments.length,1);assert.equal(p.appointments[0].start,null);visible(await profile('wuxifeng'),['空数组表示未知，不表示没有学历或师承','2022年介绍所称现任','不是2026年现职认证','数智健康研究院','健康医疗大数据国家研究院','不擅合并或认证改名','不冒连续原句','未采用其搜索摘要补教育资料']);
});
test('all ZJU consumed evidence notes works and teaching roles remain visible',async()=>{
 for(const p of mapping.people){const html=await profile(p.person_id.slice(4));for(const e of p.education)if(e.note)visible(html,[e.note]);for(const a of p.appointments||[])if(a.note)visible(html,[a.note]);
 for(const w of p.publications||[]){visible(html,[w.title,w.type_label||w.type]);if(w.note)visible(html,[w.note]);}
 for(const t of p.teaching||[]){const name=t.name||t.course||t.title,rows=[...html.matchAll(/<li>[\s\S]*?<\/li>/g)].map(m=>m[0]);const row=rows.find(r=>r.includes('<strong>'+escapeHtml(name)+'</strong>')&&(!t.note||r.includes(escapeHtml(t.note))));assert(row,p.person_id+' '+name);if(t.role)visible(row,[t.role]);if(t.note)visible(row,[t.note]);}}
});
test('Bao four research topics and three named courses retain level but no invented teaching role',async()=>{
 const p=person('baozehua');assert.equal(p.research_interests,'合成生物学；基因编辑；人工转录因子；定向进化');assert.deepEqual(p.teaching.map(t=>[t.name,t.level_as_source]),[['细胞工程','本科生课程'],['认识实习','本科生课程'],['蛋白质工程','研究生课程']]);for(const t of p.teaching)assert.equal(Object.hasOwn(t,'role'),false);const n=await render('#/person/'+p.person_id),html=n('#profile-content').innerHTML,aside=html.match(/<aside class="profile-info"[\s\S]*?<\/aside>/)?.[0];assert(aside.includes('<h3>研究方向</h3><p>'+escapeHtml(p.research_interests)+'</p>'));visible(html,['细胞工程','认识实习','蛋白质工程','本科生课程','研究生课程','具体教学角色、学期及当前开课状态未披露，不推主讲']);
});
test('Lou original arrival object survives as an association and never creates a fake job institution',async()=>{
 const p=person('louhansong-literature');assert.equal(p.institutional_associations.length,1);const a=p.institutional_associations[0];assert.equal(a.event_id,p.source_arrival.event_id);assert.equal(a.start,'1983-09');assert.equal(a.date_as_source,'1983年9月');assert.equal(a.institution,null);assert.equal(a.source_institution_display,'来校');assert.equal(a.include_in_appointment_count,false);assert.equal(p.source_arrival.institution,'来校');assert.deepEqual(a.evidence,p.source_arrival.evidence);const html=await profile('louhansong-literature'),jobs=html.split('<h2>任职经历</h2>')[1]?.split('<h2>论文与学术成果</h2>')[0];assert(jobs);assert(!jobs.includes('来校'));assert(!jobs.includes('1983'));visible(html,['1983年9月仅来校年月','不推当年法律学校名称或教授起任']);
});
test('ZJU four approved corrections retain source nulls and shared edited work is not two distinct books',()=>{
 const es=mapping.people.flatMap(p=>p.education);assert.equal(es.length,16);assert.deepEqual([true,false,null].map(v=>es.filter(e=>e.degree_awarded===v).length),[15,1,0]);const revised=es.filter(e=>e.source_degree_awarded===null&&e.degree_awarded===true);assert.equal(revised.length,4);for(const e of revised){assert.equal(e.degree_awarded_date,null);assert.equal(e.degree_awarded_year,null);assert.equal(e.event_kind,'degree');}const a=person('zhoujia').publications[0],b=person('zuhui').publications[0];assert.equal(a.title,'浙江历代进士录（清代卷）');assert.equal(b.title,a.title);assert.equal(a.note,b.note);assert(a.note.includes('两人物引用同一作品，非两本书'));assert(a.note.includes('主编龚延明，编著祖慧、周佳'));assert.equal(mapping.people.flatMap(p=>p.publications||[]).length,7);assert.equal(mapping.people.flatMap(p=>p.appointments||[]).length,9);
});
