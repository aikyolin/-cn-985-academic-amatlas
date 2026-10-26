import {readAtlasFile} from './atlas-test-io.js';
import {createImmutableCohortRenderer} from './immutable-cohort-renderer.js';
import {test} from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {matches,escapeHtml} from '../site/model.js';
const thuMapping=JSON.parse(fs.readFileSync(new URL('./fixtures/independent-thu11-source-mapping.json',import.meta.url)));
const db=readAtlasFile(new URL('../site/atlas.json',import.meta.url));
const roster=JSON.parse(fs.readFileSync(new URL('../site/rosters.json',import.meta.url)));
const mapping=JSON.parse(fs.readFileSync(new URL('./fixtures/independent-sjtu11-source-mapping.json',import.meta.url)));
const ids=['sjtu-wanglijuan','sjtu-chenlingjun','sjtu-lijuan-philosophy','sjtu-zhujun-law','sjtu-zhoumingchuan-law','sjtu-zhangyi','sjtu-wanghan','sjtu-maoxiaojun','sjtu-houliyang','sjtu-fanjinxue','sjtu-wanghui-publichealth'];
test('actual SJTU cohort preserves all independently reviewed identities and complete fields',()=>{
 assert.equal(db.people.length,944+mapping.people.length+thuMapping.people.length);assert.equal(db.build_id,roster.build_id);assert.deepEqual(mapping.people.map(p=>p.person_id),ids);
 for(const expected of mapping.people){const actual=db.people.find(p=>p.person_id===expected.person_id);assert.deepEqual(actual,expected);assert.equal(actual.data_batch_id,'faculty-batch-sjtu11-independent-20261026');assert(matches(actual,{q:actual.name},db.org_units));assert(matches(actual,{school:'sjtu',org:actual.department_id},db.org_units));assert(!matches(actual,{school:'lzu'},db.org_units));}
});
const {render}=createImmutableCohortRenderer({db,roster,fixtureId:import.meta.url});
for(const expected of mapping.people)test('actual SJTU profile and lineage preserve '+expected.name,async()=>{
 const nodes=await render('#/person/'+expected.person_id),html=nodes('#main').innerHTML+'\n'+nodes('#profile-content').innerHTML;assert(html.includes(expected.name));assert(html.includes('上海交通大学'));
 const graph=await render('#/person/'+expected.person_id+'/lineage'),relationHtml=['#main','#profile-content','#mind-stage'].map(k=>graph(k).innerHTML).join('\n');
 for(const mentor of expected.mentors||[]){assert(relationHtml.includes(escapeHtml(mentor.name)));assert(relationHtml.includes(escapeHtml(mentor.type_label||mentor.type)));}
});
test('SJTU non-null research fields are renderable strings',()=>{
 for(const expected of mapping.people){const p=db.people.find(x=>x.person_id===expected.person_id);if(p.research_interests!==undefined&&p.research_interests!==null)assert.equal(typeof p.research_interests,'string',p.person_id);}
});
test('SJTU actual research sidebar displays exact reviewed text and never object stringification',async()=>{
 for(const p of mapping.people){const n=await render('#/person/'+p.person_id),html=n('#profile-content').innerHTML,aside=html.match(/<aside class="profile-info"[\s\S]*?<\/aside>/)?.[0];assert(aside,p.person_id);const text=p.research_interests||'待补录';assert.equal(typeof text,'string');assert(aside.includes('<h3>研究方向</h3><p>'+escapeHtml(text)+'</p>'),p.person_id+' exact research panel');assert(!html.includes('[object Object]'),p.person_id);}
});
const person=id=>db.people.find(p=>p.person_id==='sjtu-'+id);
const visible=(html,terms)=>{for(const term of terms)assert(html.includes(escapeHtml(term)),term);};
async function profile(id){const n=await render('#/person/sjtu-'+id);return n('#main').innerHTML+'\n'+n('#profile-content').innerHTML;}
async function graph(id){const n=await render('#/person/sjtu-'+id+'/lineage');return n('#profile-content').innerHTML+'\n'+n('#mind-stage').innerHTML;}
test('SJTU approved ten source-reported corrections preserve ten unknown events and original date precision',()=>{
 const events=mapping.people.flatMap(p=>p.education);assert.equal(events.length,42);assert.deepEqual([true,false,null].map(v=>events.filter(e=>e.degree_awarded===v).length),[24,8,10]);
 const corrected=events.filter(e=>e.source_degree_awarded===null&&e.degree_awarded===true);assert.equal(corrected.length,10);for(const e of corrected){assert.equal(e.event_kind,'degree');assert.equal(e.degree_awarded_date,null);assert.equal(e.degree_awarded_year,null);}
});
test('Wang Lijuan three study claims stay unknown and only undergraduate thesis relationship is explicit',async()=>{
 const p=person('wanglijuan');assert.deepEqual(p.education.map(e=>e.degree_awarded),[null,null,null,false,false]);assert.equal(p.mentors.length,3);assert.deepEqual(p.mentors.map(m=>m.formal_degree_thesis_advisor),[false,false,true]);
 visible(await profile('wanglijuan'),['攻读理学博士','攻读理学硕士','攻读教育学学士','王小英仅本科学位论文指导','不把资格另计任职']);visible(await graph('wanglijuan'),['杨治良','金志成','王小英']);
});
test('Chen Lingjun double bachelor is one event and original course audiences and time strings remain visible',async()=>{
 const p=person('chenlingjun');assert.equal(p.education.length,4);assert.deepEqual(p.education.map(e=>e.degree_awarded),[true,true,true,false]);assert.equal(p.education[0].degree,'哲学和心理学双学士');assert(p.education.slice(0,3).every(e=>e.degree_awarded_date===null));assert.equal(p.mentors.length,0);
 visible(await profile('chenlingjun'),['同一区间仅一个教育事件','不补英文缩写或法律双学位制度','教育专硕生','本科辅修生','2022-26','20 24','2024-25','德州大学MD安德森癌症中心']);
});
test('Li Juan four exact award months preserve unknown second-master institution and three distinct thesis relations',async()=>{
 const p=person('lijuan-philosophy');assert.deepEqual(p.education.map(e=>e.degree_awarded_date),['2004-06','2008-01','2010-07','2014-07']);assert(p.education.every(e=>e.start===null&&e.end===null));assert.equal(p.education[2].institution,null);assert.equal(p.mentors.length,3);
 visible(await profile('lijuan-philosophy'),['Erasmus Mundus Europhilosophie Program为项目','Bochum不填授位校','不重复计6条','2015起讲师与页头副教授','沃尔夫为原著者','不推独译']);visible(await graph('lijuan-philosophy'),['丁耘','Walter Jaeschke','Winfried Schröder']);
});
test('Zhu Jun overlapping masters remain separate unknown awards and stage guidance is not thesis certification',async()=>{
 const p=person('zhujun-law');assert.deepEqual(p.education.map(e=>e.degree_awarded),[null,null,null,true]);assert.deepEqual(p.education.slice(1,3).map(e=>[e.start,e.end]),[['2006-10','2007-09'],['2004-09','2008-03']]);assert.equal(p.mentors.length,4);assert(p.mentors.every(m=>m.formal_thesis_advisor_verified===false&&m.formal_dissertation_advisor_verified===false&&m.original_dissertation_read===false));
 visible(await profile('zhujun-law'),['中德两个硕士区间重叠原样保留','不推联授或双学位制度','文学学士']);visible(await graph('zhujun-law'),['Rüdiger Krause','Christiane Wendehorst','邵建东','孔德明','非原论文核验']);
});
test('Zhou Mingchuan directory contrast does not imply departure and graduation years are not award years',async()=>{
 const p=person('zhoumingchuan-law');assert(p.education.every(e=>e.degree_awarded===true&&e.degree_awarded_year===null));assert.deepEqual(p.education.map(e=>e.end),['2007','2003','1999']);assert.equal(p.appointments.length,2);assert.equal(p.publications.length,0);
 visible(await profile('zhoumingchuan-law'),['同批法学院目录可见范围未见周铭川','不推离职、退休或当前聘任','两个来源角色不合并为一个劳动关系','毕业年份与授位年份分开']);
});
test('Zhang Yi explicit credentials remain undated and alternate book editions do not duplicate works',async()=>{
 const p=person('zhangyi');assert.deepEqual(p.education.map(e=>e.degree_awarded),[true,true,true]);assert(p.education.every(e=>e.start===null&&e.end===null&&e.degree_awarded_date===null));assert.equal(p.publications.length,2);assert.equal(p.mentors.length,0);
 visible(await profile('zhangyi'),['华东师范大学文学学士、硕士','香港中文大学历史学博士','博士生导师是本人指导资格','2017年','2013年','按一部作品计','章毅等著']);
});
test('Wang Han shared graduate interval is not allocated to separate stages or continuous current employment',async()=>{
 const p=person('wanghan');assert.deepEqual(p.education.map(e=>e.degree_awarded),[true,null,null,false,false]);assert(p.education.slice(1,3).every(e=>e.start===null&&e.end===null));assert.equal(p.appointments.length,0);
 visible(await profile('wanghan'),['硕士博士共用2002年9月至2008年6月','不能拆具体阶段日期','2025年9月—','长聘副教授、博士生导师','不擅补著编角色']);
});
test('Mao Xiaojun doctoral graduation stays unknown award and output page dates are not publication dates',async()=>{
 const p=person('maoxiaojun');assert.equal(p.education.length,1);assert.equal(p.education[0].degree_awarded,null);assert.equal(p.publications.length,2);assert.equal(p.mentors.length,0);
 visible(await profile('maoxiaojun'),['博士毕业于爱荷华州立大学','授位未单独核实','2024-08-21','2024-04-11','不填出版年','作者表、刊名和贡献角色未知']);
});
test('Hou Liyang LLM honors and Chinese credentials stay distinct without inventing another doctorate or postdoc',async()=>{
 const p=person('houliyang');assert.equal(p.education.length,4);assert(p.education.every(e=>e.degree_awarded===true&&e.degree_awarded_date===null));assert.equal(p.education[1].degree,'LLM');assert.equal(p.appointments[0].title,'助理研究员');assert.equal(p.mentors.length,0);
 visible(await profile('houliyang'),['LLM (magna cum laude, first in class)','Doctor of Law (no grading system for this degree)','法学硕士（优秀毕业生）','不能套于LLM或另造博士','不当博士后','未独立核证书或荣誉']);
});
test('Fan Jinxue explicit awards do not infer schools from mentors and combined visits are not continuous stays',async()=>{
 const p=person('fanjinxue');assert.deepEqual(p.education.map(e=>e.degree_awarded),[true,true,true,false,false]);assert(p.education.slice(1,3).every(e=>e.institution===null));assert.equal(p.mentors.length,3);assert.equal(p.education[4].institution,null);
 visible(await profile('fanjinxue'),['不从徐显明或李龙任职推学校','逐机构日期未知','不称连续访问','具体职务未知，不补教授或晋升时间','authors空，不推独著']);visible(await graph('fanjinxue'),['徐显明','李龙','韩大元','博士后阶段导师']);
});
test('Wang Hui biography credentials do not promote undergraduate stage or Research fellow to a postdoc',async()=>{
 const p=person('wanghui-publichealth');assert.deepEqual(p.education.map(e=>e.degree_awarded),[null,true,true,false]);assert.equal(p.appointments[0].title,'Research fellow');assert.equal(p.education[3].start,null);assert.equal(p.education[3].end,null);assert.deepEqual(p.education[3].years_as_source,[2018,2019]);assert.equal(p.mentors.length,0);
 visible(await profile('wanghui-publichealth'),['中山大学医学本科和硕士，香港大学流行病学博士','Research fellow为职业角色，不推博士后','不推连续区间','Wang H*为通讯作者','仅列名Wang H，不推通讯作者','BMC Med i cine']);
});
test('all SJTU consumed evidence limits, career and work notes, teaching roles and audience qualifiers render on actual profiles',async()=>{
 let works=0,teaching=0;
 for(const p of mapping.people){const html=await profile(p.person_id.slice(5));visible(html,p.unknowns||[]);for(const e of p.education)if(e.note)visible(html,[e.note]);for(const a of p.appointments||[])if(a.note)visible(html,[a.note]);
  for(const w of p.publications||[]){visible(html,[w.title,w.type_label||w.type]);if(w.note)visible(html,[w.note]);works++;}
  for(const t of p.teaching||[]){const name=t.name||t.course||t.title,rows=[...html.matchAll(/<li>[\s\S]*?<\/li>/g)].map(m=>m[0]);const row=rows.find(r=>r.includes('<strong>'+escapeHtml(name)+'</strong>')&&(!t.note||r.includes(escapeHtml(t.note))));assert(row,p.person_id+' '+name);if(t.role)visible(row,[t.role]);if(t.note)visible(row,[t.note]);teaching++;}
 }
 assert.equal(works,16);assert.equal(teaching,8);
});
