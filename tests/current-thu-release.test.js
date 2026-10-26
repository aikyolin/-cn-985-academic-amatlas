import {readAtlasFile} from './atlas-test-io.js';
import {createImmutableCohortRenderer} from './immutable-cohort-renderer.js';
import {test} from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {matches,escapeHtml} from '../site/model.js';
const pkuMapping=JSON.parse(fs.readFileSync(new URL('./fixtures/independent-pku11-source-mapping.json',import.meta.url)));
const db=readAtlasFile(new URL('../site/atlas.json',import.meta.url));
const roster=JSON.parse(fs.readFileSync(new URL('../site/rosters.json',import.meta.url)));
const mapping=JSON.parse(fs.readFileSync(new URL('./fixtures/independent-thu11-source-mapping.json',import.meta.url)));
const ids=["thu-lishoukui", "thu-dingsixin", "thu-qiaoweifeng", "thu-zhouyuan", "thu-chenguoqing", "thu-xuguoyi", "thu-liangzongxia", "thu-luxiaobo", "thu-zhanggan", "thu-liangwannian-publichealth", "thu-jisihan-publichealth"];
test('actual THU cohort preserves all independently reviewed identities and complete fields',()=>{
 assert.equal(db.people.length,955+mapping.people.length+pkuMapping.people.length);assert.equal(db.build_id,roster.build_id);assert.deepEqual(mapping.people.map(p=>p.person_id),ids);
 for(const expected of mapping.people){const actual=db.people.find(p=>p.person_id===expected.person_id);assert.deepEqual(actual,expected);assert.equal(actual.data_batch_id,'faculty-batch-thu11-independent-20261026');assert(matches(actual,{q:actual.name},db.org_units));assert(matches(actual,{school:'thu',org:actual.department_id},db.org_units));assert(!matches(actual,{school:'lzu'},db.org_units));}
});
const {render}=createImmutableCohortRenderer({db,roster,fixtureId:import.meta.url});
for(const expected of mapping.people)test('actual THU profile and lineage preserve '+expected.name,async()=>{
 const nodes=await render('#/person/'+expected.person_id),html=nodes('#main').innerHTML+'\n'+nodes('#profile-content').innerHTML;assert(html.includes(expected.name));assert(html.includes('清华大学'));
 const graph=await render('#/person/'+expected.person_id+'/lineage'),relationHtml=['#main','#profile-content','#mind-stage'].map(k=>graph(k).innerHTML).join('\n');
 for(const mentor of expected.mentors||[]){assert(relationHtml.includes(escapeHtml(mentor.name)));assert(relationHtml.includes(escapeHtml(mentor.type_label||mentor.type)));}
});
test('THU non-null research fields are renderable strings',()=>{
 for(const expected of mapping.people){const p=db.people.find(x=>x.person_id===expected.person_id);if(p.research_interests!==undefined&&p.research_interests!==null)assert.equal(typeof p.research_interests,'string',p.person_id);}
});
test('THU actual research sidebar displays exact reviewed text and never object stringification',async()=>{
 for(const p of mapping.people){const n=await render('#/person/'+p.person_id),html=n('#profile-content').innerHTML,aside=html.match(/<aside class="profile-info"[\s\S]*?<\/aside>/)?.[0];assert(aside,p.person_id);const text=p.research_interests||'待补录';assert.equal(typeof text,'string');assert(aside.includes('<h3>研究方向</h3><p>'+escapeHtml(text)+'</p>'),p.person_id+' exact research panel');assert(!html.includes('[object Object]'),p.person_id);}
});
const person=id=>db.people.find(p=>p.person_id==='thu-'+id);
const visible=(html,terms)=>{for(const term of terms)assert(html.includes(escapeHtml(term)),term);};
async function profile(id){const n=await render('#/person/thu-'+id);return n('#main').innerHTML+'\n'+n('#profile-content').innerHTML;}
test('THU exact reviewed classifications and absence of disclosed personal guidance remain distinct',()=>{
 const es=mapping.people.flatMap(p=>p.education);assert.equal(es.length,27);assert.deepEqual([true,false,null].map(v=>es.filter(e=>e.degree_awarded===v).length),[22,2,3]);for(const p of mapping.people){assert.equal((p.mentors||[]).length,0);assert.equal((p.professional_research_advisors||[]).length,0);}
});
test('Li Shoukui study end and independently reported award year are not conflated',async()=>{
 const p=person('lishoukui');assert.deepEqual(p.education.map(e=>e.degree_awarded_year),[1993,1998]);assert.equal(p.education[1].end,'1997');assert.equal(p.education[1].degree_awarded_date,null);visible(await profile('lishoukui'),['1997是学习终年、1998是授位年','不推延迟原因','1993仅工作序列起点','不另增任职或个人师承']);
});
test('Ding Sixin three explicit degrees do not acquire study-end award dates',async()=>{
 const p=person('dingsixin');assert.deepEqual(p.education.map(e=>e.degree_awarded),[true,true,true,false]);const degrees=p.education.filter(e=>e.event_kind==='degree');assert.equal(degrees.length,3);assert(degrees.every(e=>e.degree_awarded_date===null&&e.degree_awarded_year===null));const visit=p.education[3];assert.equal(visit.event_kind,'visiting_scholar');for(const k of ['degree_awarded_date','degree_awarded_year'])assert.equal(Object.hasOwn(visit,k),false);visible(await profile('dingsixin'),['哲学学士、硕士、博士','不替换为哈佛大学授位','讲师1999、副教授2001、教授2006','博导仅本人指导资格']);
});
test('Qiao Weifeng June 2016 award has independent received evidence',async()=>{
 const p=person('qiaoweifeng');assert.equal(p.education[2].degree_awarded_date,'2016-06');assert.equal(p.education[2].degree_awarded_year,2016);assert(p.education.slice(0,2).every(e=>e.degree_awarded_date===null&&e.degree_awarded_year===null));visible(await profile('qiaoweifeng'),['received his Ph.D. ... in June 2016','不仅取学习终月','不推法律更名时间','工程教育研究所是目录标签']);
});
test('Zhou Yuan 2010 teaching start is not tenured professor start',async()=>{
 const p=person('zhouyuan');assert.equal(p.appointments.length,1);assert.equal(p.appointments[0].start,'2010');assert.equal(p.appointments[0].title,'任教（职称起始未绑定）');assert(p.education.every(e=>e.start===null&&e.end===null));visible(await profile('zhouyuan'),['不追溯为2010年即长聘教授','非完整作者名单','题名2035不当出版年']);
});
test('Chen Guoqing KUL degrees preserve explicit years without a new 1985 event',async()=>{
 const p=person('chenguoqing');assert.equal(p.education.length,3);assert.deepEqual(p.education.map(e=>e.degree_awarded_year),[1982,1988,1992]);assert(p.education.every(e=>e.start===null&&e.end===null));assert.equal(p.education[1].institution,'比利时鲁汶大学(KUL)');visible(await profile('chenguoqing'),['1985留欧不增学位或访问事件','两作品只给合作者与个人成果归属','不是完整作者串','不把未知起止扩成同时任职事件']);
});
test('Xu Guoyi visiting assistant professor remains employment not postdoc study',async()=>{
 const p=person('xuguoyi');assert.equal(p.education.length,1);assert.equal(p.education[0].degree_awarded_date,'2010');assert.equal(p.appointments[0].title,'访问助理教授');assert.deepEqual([p.appointments[0].start,p.appointments[0].end],['2010','2013']);assert.equal(p.publications.length,0);visible(await profile('xuguoyi'),['访问助理教授为任职，不当访学或博士后','外部索引未打开','不能补作品或声称终身无作品']);
});
test('Liang Zongxia reported doctorate year is visible but not promoted to award date',async()=>{
 const p=person('liangzongxia');assert.deepEqual(p.education.map(e=>e.degree_awarded),[true,false]);assert.equal(p.education[0].degree_awarded_year,null);assert.equal(p.education[0].degree_awarded_date,null);assert.deepEqual(p.appointments.slice(1).map(a=>a.title),['客座研究员','客座研究员']);visible(await profile('liangzongxia'),['博士（中国科学院应用数学研究所，1996）','不将1998当教授起任','客座研究员为职业记录']);
});
test('Lu Xiaobo two uncertain study records do not invent degrees or split shared institutions',async()=>{
 const p=person('luxiaobo');assert.deepEqual(p.education.map(e=>e.degree_awarded),[null,null]);assert.equal(p.education.length,2);assert.equal(p.appointments[0].start,'2022');visible(await profile('luxiaobo'),['1982为原毕业年','德国两机构共用1987至1990学习区间','原院长为历史身份','上海世博会湖南馆为主持设计']);
});
test('Zhang Gan personal doctorate does not infer institution dates or a dated job',async()=>{
 const p=person('zhanggan');assert.equal(p.education.length,1);assert.equal(p.education[0].degree_awarded,true);for(const k of ['institution','start','end','degree_awarded_date','degree_awarded_year'])assert.equal(p.education[0][k],null);assert.equal(p.appointments.length,0);visible(await profile('zhanggan'),['官方具名职业身份明确文学博士','不从清华任职推授位校','不混主编与作者']);
});
test('Liang Wannian unknown master and closed 2025 office survive old page date',async()=>{
 const p=person('liangwannian-publichealth');assert.deepEqual(p.education.map(e=>e.degree_awarded),[true,null,true]);assert.equal(p.appointments[0].end,'2025-08');visible(await profile('liangwannian-publichealth'),['独立本人医学博士身份与唯一协和博士阶段匹配','2020至2025年8月，已结束','2020-11-06不当作2025事实核验时点','论文作者星号未获原栏目解释']);
});
test('Ji Sihan BA ScM ScD credentials and two institutional jobs keep separate scope',async()=>{
 const p=person('jisihan-publichealth');assert.deepEqual(p.education.map(e=>e.degree),['学士（BA）','硕士（ScM）','博士（ScD）']);assert(p.education.every(e=>e.degree_awarded===true&&e.degree_awarded_date===null&&e.degree_awarded_year===null));assert.deepEqual(p.appointments.map(a=>[a.title,a.start]),[['长聘副教授','2025'],['兼职副教授','2026']]);visible(await profile('jisihan-publichealth'),['不据网页域名合并机构','不冒万科独立目录认证','未认证原始学位证或法律等价']);
});
test('all THU evidence notes works and course roles are visible in real profiles',async()=>{
 let works=0,teaching=0;
 for(const p of mapping.people){const html=await profile(p.person_id.slice(4));visible(html,p.unknowns||[]);for(const e of p.education)if(e.note)visible(html,[e.note]);for(const a of p.appointments||[])if(a.note)visible(html,[a.note]);
 for(const w of p.publications||[]){visible(html,[w.title,w.type_label||w.type]);if(w.note)visible(html,[w.note]);works++;}
 for(const t of p.teaching||[]){const name=t.name||t.course||t.title,rows=[...html.matchAll(/<li>[\s\S]*?<\/li>/g)].map(m=>m[0]);const row=rows.find(r=>r.includes('<strong>'+escapeHtml(name)+'</strong>')&&(!t.note||r.includes(escapeHtml(t.note))));assert(row,p.person_id+' '+name);if(t.role)visible(row,[t.role]);if(t.note)visible(row,[t.note]);teaching++;}}
 assert.equal(works,18);assert.equal(teaching,4);
});
