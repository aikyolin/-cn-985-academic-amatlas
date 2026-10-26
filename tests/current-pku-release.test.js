import {readAtlasFile} from './atlas-test-io.js';
import {createImmutableCohortRenderer} from './immutable-cohort-renderer.js';
import {test} from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {matches,escapeHtml} from '../site/model.js';
const zjuMapping=JSON.parse(fs.readFileSync(new URL('./fixtures/independent-zju7-source-mapping.json',import.meta.url)));
const db=readAtlasFile(new URL('../site/atlas.json',import.meta.url));
const roster=JSON.parse(fs.readFileSync(new URL('../site/rosters.json',import.meta.url)));
const mapping=JSON.parse(fs.readFileSync(new URL('./fixtures/independent-pku11-source-mapping.json',import.meta.url)));
const ids=["pku-chaiweizhong", "pku-fanxing", "pku-zhangdong-math", "pku-wangjie", "pku-chendayue", "pku-chensongxi", "pku-zhangwu", "pku-huyonghua", "pku-liliming", "pku-chuming-basicmedicine", "pku-biwenjian-medicalgenetics"];
test('actual PKU cohort preserves all independently reviewed identities and complete fields',()=>{
 assert.equal(db.people.length,966+mapping.people.length+zjuMapping.people.length);assert.equal(db.build_id,roster.build_id);assert.deepEqual(mapping.people.map(p=>p.person_id),ids);
 for(const expected of mapping.people){const actual=db.people.find(p=>p.person_id===expected.person_id);assert.deepEqual(actual,expected);assert.equal(actual.data_batch_id,'faculty-batch-pku11-independent-20261026');assert(matches(actual,{q:actual.name},db.org_units));assert(matches(actual,{school:'pku',org:actual.department_id},db.org_units));assert(!matches(actual,{school:'lzu'},db.org_units));}
});
const {render}=createImmutableCohortRenderer({db,roster,fixtureId:import.meta.url});
for(const expected of mapping.people)test('actual PKU profile and lineage preserve '+expected.name,async()=>{
 const nodes=await render('#/person/'+expected.person_id),html=nodes('#main').innerHTML+'\n'+nodes('#profile-content').innerHTML;assert(html.includes(expected.name));assert(html.includes('北京大学'));
 const graph=await render('#/person/'+expected.person_id+'/lineage'),relationHtml=['#main','#profile-content','#mind-stage'].map(k=>graph(k).innerHTML).join('\n');
 for(const mentor of expected.mentors||[]){assert(relationHtml.includes(escapeHtml(mentor.name)));assert(relationHtml.includes(escapeHtml(mentor.type_label||mentor.type)));}
});
test('PKU non-null research fields are renderable strings',()=>{
 for(const expected of mapping.people){const p=db.people.find(x=>x.person_id===expected.person_id);if(p.research_interests!==undefined&&p.research_interests!==null)assert.equal(typeof p.research_interests,'string',p.person_id);}
});
test('PKU actual research sidebar displays exact reviewed text and never object stringification',async()=>{
 for(const p of mapping.people){const n=await render('#/person/'+p.person_id),html=n('#profile-content').innerHTML,aside=html.match(/<aside class="profile-info"[\s\S]*?<\/aside>/)?.[0];assert(aside,p.person_id);const text=p.research_interests||'待补录';assert.equal(typeof text,'string');assert(aside.includes('<h3>研究方向</h3><p>'+escapeHtml(text)+'</p>'),p.person_id+' exact research panel');assert(!html.includes('[object Object]'),p.person_id);}
});
test('PKU reviewed uncertainty text remains visible on each actual profile',async()=>{
 for(const p of mapping.people){const n=await render('#/person/'+p.person_id),html=n('#main').innerHTML+'\n'+n('#profile-content').innerHTML;for(const note of p.unknowns||[])assert(html.includes(escapeHtml(note)),p.person_id+' '+note);}
});
const person=id=>db.people.find(p=>p.person_id==='pku-'+id);
const visible=(html,terms)=>{for(const term of terms)assert(html.includes(escapeHtml(term)),term);};
async function profile(id){const n=await render('#/person/pku-'+id);return n('#main').innerHTML+'\n'+n('#profile-content').innerHTML;}
test('Chai Weizhong three postdocs preserve shared interval and original institutions',async()=>{
 const p=person('chaiweizhong');assert.equal(p.education.length,6);assert.deepEqual(p.education.map(e=>e.degree_awarded),[true,true,true,false,false,false]);assert.deepEqual(p.education.slice(0,3).map(e=>e.degree_awarded_year),[1983,1986,1995]);visible(await profile('chaiweizhong'),['1995－2001为三机构共同叙述范围','不逐机构复制为起止','瑞典国立农业大学','美国加州大学-戴维斯分校','荷兰瓦格宁根大学','目录明确旧版，仅历史归属','不作为副教授起任日期']);
});
test('Fan Xing translator authorship and doctorate year do not become July award date',async()=>{
 const p=person('fanxing');assert.equal(p.education[2].degree_awarded_year,2017);assert.equal(p.education[2].degree_awarded_date,null);assert.equal(p.education[2].end,'2017-07');assert.equal(p.teaching.length,8);visible(await profile('fanxing'),['2017年7月仅学习结束月','作品原作者、编者、第一译者分别保留','不能据本人页自动补独著','同名葡萄牙语阅读按两个层级保留']);
});
test('Zhang Dong official interview guidance does not claim original thesis verification',async()=>{
 const p=person('zhangdong-math');assert.equal(p.publications.length,0);assert.equal(p.mentors.length,1);assert.equal(p.mentors[0].name,'张恭庆');assert.equal(p.education[2].start,null);assert.equal(p.education[2].end,null);visible(await profile('zhangdong-math'),['来自官方工会采访','不称独立学籍或原论文验证','首次读取超时未接受任何搜索摘录','本批0作品不等于无论文','不能推2017至2019']);const n=await render('#/person/'+p.person_id+'/lineage');visible(n('#profile-content').innerHTML+n('#mind-stage').innerHTML,['张恭庆']);
});
test('Wang Jie original English unit and qualification records preserve unknown award timing',async()=>{
 const p=person('wangjie');assert.deepEqual(p.education.map(e=>e.degree_awarded),[true,true,false,false]);assert(p.education.slice(0,2).every(e=>e.degree_awarded_date===null&&e.degree_awarded_year===null));assert.equal(p.mentors.length,0);visible(await profile('wangjie'),['International Center for Quantum Materials','不额外推中文机构名','Flatiron研究所原名不扩写','保留摘录未含独立表头','不声称专门学位栏']);
});
test('Chen Dayue visiting assistant professor remains a job and with names are not complete authors',async()=>{
 const p=person('chendayue');assert.equal(p.appointments[0].title,'visiting assistant professor');assert.deepEqual([p.appointments[0].start,p.appointments[0].end],['1989','1991']);assert(p.education.slice(0,2).every(e=>e.degree_awarded_date===null&&e.degree_awarded_year===null));visible(await profile('chendayue'),['不改访问学习或博士后','两论文with合作者不是完整作者名单','不自行插入陈大岳','原报告年不补授位日期']);
});
test('Chen Songxi empty works do not deny publications or backdate chair appointment',async()=>{
 const p=person('chensongxi');assert.equal(p.publications.length,0);assert.deepEqual(p.education.map(e=>e.degree_awarded_date),['1983','1993']);assert.equal(p.appointments[0].start,'2008');visible(await profile('chensongxi'),['不把2008当讲席教授起任','本批无具名作品，不声称本人没有论文','页面更新时间2025年3月仅来源标签']);
});
test('Zhang Wu explicit held degrees do not invent a dated appointment',async()=>{
 const p=person('zhangwu');assert.equal(p.appointments.length,0);assert.deepEqual(p.education.map(e=>e.degree_awarded_year),[2008,2014]);assert.deepEqual(p.education.map(e=>e.degree_awarded_date),['2008','2014']);visible(await profile('zhangwu'),['起任年月未披露，不虚构任职事件','页面显示2019-03-04','《社会发展的全球审视》明确合著']);
});
test('Hu Yonghua empty education remains unknown and dean roles historical',async()=>{
 const p=person('huyonghua');assert.deepEqual(p.education,[]);assert.deepEqual(p.mentors,[]);assert.equal(p.appointments.length,2);assert(p.appointments.every(a=>a.start===null&&a.end===null));visible(await profile('huyonghua'),['空记录表示未知，不是没有教育经历','本人教授、博导称谓不是其本人学位或师承','原历任角色']);
});
test('Li Liming honors and present source language do not supply education or current verification',async()=>{
 const p=person('liliming');assert.deepEqual(p.education,[]);assert.deepEqual(p.mentors,[]);assert.equal(p.appointments.length,3);visible(await profile('liliming'),['原现任角色','原历任角色','博雅特聘教授','空记录表示未知','未用搜索片段补教育事实']);
});
test('Chu Ming two qualifications and historical teaching positions preserve undated deputy roles',async()=>{
 const p=person('chuming-basicmedicine');assert.deepEqual(p.education.map(e=>e.degree_awarded),[true,true]);assert(p.education.every(e=>e.degree_awarded_date===null&&e.degree_awarded_year===null));assert.deepEqual(p.appointments.map(a=>[a.title,a.start,a.end]),[['教授','2025-08',null],['讲师','2011-08','2019-07'],['副教授','2019-08','2025-07']]);assert.equal(p.publications.length,2);visible(await profile('chuming-basicmedicine'),['免疫学系副主任','基础医学院教师教学发展中心副主任','不挪用2025-08教授起任日','闭合历史任期']);
});
test('Bi Wenjian doctoral-stage and postdoc collaborators retain four explicit typed relations',async()=>{
 const p=person('biwenjian-medicalgenetics');assert.equal(p.education.length,4);assert.equal(p.education[0].degree_awarded,null);assert.equal(p.education[1].degree_awarded,true);assert.equal(p.education[1].degree_awarded_date,null);assert.equal(p.education[1].degree_awarded_year,null);assert.deepEqual(p.education.slice(2).map(e=>e.degree_awarded),[false,false]);assert.equal(p.mentors.length,4);assert.equal(p.mentors[0].name,'张纪峰');visible(await profile('biwenjian-medicalgenetics'),['张纪峰为博士阶段导师','Dr. Seunggeun (Shawn) Lee','Dr. Stanley Pounds','Dr. Guolian Kang','不升级论文认证','*共同第一作者','不能解释为共同通讯']);
});
test('all PKU consumed notes work contributions and teaching roles render on actual profiles',async()=>{
 for(const p of mapping.people){const html=await profile(p.person_id.slice(4));for(const e of p.education)if(e.note)visible(html,[e.note]);for(const a of p.appointments||[])if(a.note)visible(html,[a.note]);
 for(const w of p.publications||[]){visible(html,[w.title,w.type_label||w.type]);if(w.note)visible(html,[w.note]);}
 for(const t of p.teaching||[]){const name=t.name||t.course||t.title,rows=[...html.matchAll(/<li>[\s\S]*?<\/li>/g)].map(m=>m[0]);const row=rows.find(r=>r.includes('<strong>'+escapeHtml(name)+'</strong>')&&(!t.note||r.includes(escapeHtml(t.note))));assert(row,p.person_id+' '+name);if(t.role)visible(row,[t.role]);if(t.note)visible(row,[t.note]);}}
});
test('PKU final approved qualifications retain one undergraduate unknown and ten nondegree events',()=>{
 const es=mapping.people.flatMap(p=>p.education);assert.equal(es.length,30);assert.deepEqual([true,false,null].map(v=>es.filter(e=>e.degree_awarded===v).length),[19,10,1]);assert.equal(mapping.people.flatMap(p=>p.mentors||[]).length,5);assert.equal(mapping.people.flatMap(p=>p.appointments||[]).length,19);assert.equal(mapping.people.flatMap(p=>p.publications||[]).length,17);assert.equal(mapping.people.flatMap(p=>p.teaching||[]).length,8);
});
