import {createImmutableCohortRenderer} from './immutable-cohort-renderer.js';
import {readAtlasFile,createAtlasFetch} from './atlas-test-io.js';
import {test} from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {matches, stages, mentorEvent, mentorEvents, mentorOfficialUrl, mentorProfileRoute, escapeHtml} from '../site/model.js';
const lzuMapping=JSON.parse(fs.readFileSync(new URL('./fixtures/independent-lzu11-source-mapping.json',import.meta.url)));
const sjtuMapping=JSON.parse(fs.readFileSync(new URL('./fixtures/independent-sjtu11-source-mapping.json',import.meta.url)));
const db=readAtlasFile(new URL('../site/atlas.json',import.meta.url));
const roster=JSON.parse(fs.readFileSync(new URL('../site/rosters.json',import.meta.url)));
const mapping=JSON.parse(fs.readFileSync(new URL('./fixtures/independent-ouc12-source-mapping.json',import.meta.url)));
test('actual OUC cohort exactly preserves independently reviewed fields, identities and scope',()=>{
 assert.deepEqual(mapping.people.map(p=>p.person_id),["ouc-tongsiyou", "ouc-wuyaxin", "ouc-liqintong", "ouc-chenyitong", "ouc-aiqinghui", "ouc-zhangwenbing", "ouc-duanxiaolin", "ouc-jinyaqi", "ouc-chenchen", "ouc-xieyangbin", "ouc-lipihong", "ouc-suitiankai"]);
 assert(mapping.people.every(p=>p.data_batch_id==='faculty-batch-ouc12-independent-20261026'));
 assert.equal(db.people.length,921+mapping.people.length+lzuMapping.people.length+sjtuMapping.people.length);assert.equal(db.build_id,roster.build_id);
 for(const expected of mapping.people){
  const actual=db.people.find(p=>p.person_id===expected.person_id);assert.deepEqual(actual,expected);
  assert.equal(typeof actual.department,'string');assert(actual.department.length>0);
  assert(matches(actual,{q:actual.name},db.org_units));assert(matches(actual,{school:'ouc',org:actual.department_id},db.org_units));
  assert(!matches(actual,{school:'seu'},db.org_units));assert.equal(actual.quick_link_eligible,expected.quick_link_eligible);assert.equal(actual.include_in_current_faculty_count,expected.include_in_current_faculty_count);
  for(const stage of ['bachelor','master','doctor']) for(const event of stages(actual,stage)){assert.equal(event.event_kind,'degree');assert.equal(event.degree_awarded,true);}
 }
});
const {render}=createImmutableCohortRenderer({db,roster,fixtureId:import.meta.url});
for(const expected of mapping.people)test('actual OUC profile and lineage preserve '+expected.name,async()=>{
 const nodes=await render('#/person/'+expected.person_id);const html=['#main','#profile-content'].map(k=>nodes(k).innerHTML).join('\n');
 assert(html.includes(expected.name));assert(html.includes('中国海洋大学'));
 const lineage=await render('#/person/'+expected.person_id+'/lineage');
 const relationHtml=['#main','#profile-content','#mind-stage'].map(k=>lineage(k).innerHTML).join('\n');
 for(const mentor of expected.mentors){assert(relationHtml.includes(mentor.name));assert(relationHtml.includes(mentor.type_label||mentor.type));}
 if(expected.mentors.length===0)assert(relationHtml.includes('0条已收录关系'));
});

test('OUC all non-null research_interests are renderable strings, not nested source objects',()=>{
 for(const p of mapping.people){const actual=db.people.find(x=>x.person_id===p.person_id);if(actual.research_interests!==undefined&&actual.research_interests!==null)assert.equal(typeof actual.research_interests,'string',p.person_id);}
});
test('OUC research sidebar displays each reviewed research text exactly without object stringification',async()=>{
 for(const p of mapping.people){const nodes=await render('#/person/'+p.person_id),html=nodes('#profile-content').innerHTML,aside=html.match(/<aside class="profile-info"[\s\S]*?<\/aside>/)?.[0];assert(aside,p.person_id);const text=p.research_interests||'待补录';assert.equal(typeof text,'string',p.person_id);assert(aside.includes('<h3>研究方向</h3><p>'+escapeHtml(text)+'</p>'),p.person_id+' exact research panel');assert(!html.includes('[object Object]'),p.person_id+' object stringification');}
});


const person=id=>db.people.find(p=>p.person_id==='ouc-'+id);
const visible=(html,terms)=>{for(const term of terms)assert(html.includes(escapeHtml(term)),term);};
async function profile(id){const n=await render('#/person/ouc-'+id);return n('#profile-content').innerHTML;}
async function graph(id){const n=await render('#/person/ouc-'+id+'/lineage');return n('#mind-stage').innerHTML;}
test('Tong bachelor evidence does not invent a master or certify doctoral award from stage guidance',async()=>{
 const p=person('tongsiyou');assert.deepEqual(p.education.map(e=>e.degree_awarded),[true,null]);assert.equal(p.education.length,2);assert.equal(stages(p,'master').length,0);assert.equal(p.mentors.length,1);assert.equal(p.mentors[0].name,'李庆忠');assert.equal(p.mentors[0].education_event_id,'ouc-tongsiyou-study-doctoral');visible(await profile('tongsiyou'),['未据两段教育补造硕士经历','不认证正式论文导师','首篇原刊元数据未取得，仅官网书目']);visible(await graph('tongsiyou'),['李庆忠']);
});
test('Wu retains four separate visits and conflicting published page ranges without upgrading Merran to mentor',async()=>{
 const p=person('wuyaxin');assert.deepEqual(p.education.map(e=>e.degree_awarded),[true,true,true,false,false,false,false]);assert.deepEqual(p.mentors.map(m=>m.name),['何自然','Robert E. Sanders','Paul Drew','John Heritage']);assert(!p.mentors.some(m=>m.name==='Merran Toerien'));visible(await profile('wuyaxin'),['官网23–35，原刊2022年45(6)21–33','Merran Toerien仅括号具名，角色未知','未读全文或PDF，未见DOI']);const html=await graph('wuyaxin');visible(html,['何自然','Robert E. Sanders','Paul Drew','John Heritage']);
});
test('Li Qintong preserves bachelor certainty, uncertain graduate awards and source-specific book contribution',async()=>{
 const p=person('liqintong');assert.deepEqual(p.education.map(e=>e.degree_awarded),[true,null,null]);assert.equal(p.mentors.length,1);assert.equal(p.mentors[0].name,'周东平');visible(await profile('liqintong'),['法学学位类型不擅扩为精确培养专业','周东平、李勤通合著署名','原“参与著作”','学位授予未单独核实']);visible(await graph('liqintong'),['周东平']);
});
test('Chen explicit award years and three distinct relationship scopes are preserved without a forced doctoral binding',async()=>{
 const p=person('chenyitong');assert.deepEqual(p.education.map(e=>e.degree_awarded),[true,true,true,false,false]);assert.deepEqual(p.education.slice(0,3).map(e=>e.degree_awarded_year),[2009,2011,2014]);const unknown=p.mentors.find(m=>m.name==='刘惠荣');assert.equal(unknown.type,'unknown');assert.equal(unknown.education_event_id,null);assert.deepEqual(mentorEvents(p,unknown),[]);assert.equal(p.teaching.length,6);assert(p.teaching.every(t=>t.role==='开设'));visible(await profile('chenyitong'),['具体学位阶段未明，不强归博士','Pace联合培养博士为单一非学位事件','上海交大博士后合作导师傅崐成']);visible(await graph('chenyitong'),['刘惠荣','Richard L. Ottinger','傅崐成']);
});

test('Ai identity-based doctorate does not upgrade reposted media to independent academic records',async()=>{
 const p=person('aiqinghui');assert.deepEqual(p.education.map(e=>e.degree_awarded),[null,null,true,false]);assert.deepEqual(p.mentors.map(m=>m.name),['谢小军','麦康森']);assert.deepEqual(p.mentors.map(m=>m.type),['doctoral_supervisor','postdoctoral_mentor']);visible(await profile('aiqinghui'),['原新闻2025-04-08、转载2025-04-10','未读媒体原页','不称学校学籍独证或独立交叉认证','原1991入学、1994本科毕业','原作者表含省略号，不补全']);visible(await graph('aiqinghui'),['谢小军','麦康森']);
});
test('Zhang doctorate identity retains unknown institution and interview-mentioned courses do not become teaching assignments',async()=>{
 const p=person('zhangwenbing'),d=p.education.find(e=>e.event_id==='ouc-zhangwenbing-doctoral');assert.equal(d.degree_awarded,true);assert.equal(d.institution,null);assert.equal(d.start,null);assert.equal(d.end,null);assert.deepEqual(p.mentors.map(m=>m.type),['masters_supervisor','doctoral_supervisor']);visible(await profile('zhangwenbing'),['学籍或授位机构未知','65小时旅行不当入学事件','留存摘录未明确归属张文兵授课/负责','不计已核授课','美国Auburn大学高级访问学者']);visible(await graph('zhangwenbing'),['谢小军','麦康森']);
});
test('Duan original award year and sole-writing roles are visible without an invented reprint work',async()=>{
 const p=person('duanxiaolin');assert.equal(p.education.length,1);assert.equal(p.education[0].degree_awarded,true);assert.equal(p.education[0].degree_awarded_year,'2019');assert.equal(p.publications.length,2);assert.equal(p.mentors.length,0);visible(await profile('duanxiaolin'),['2019年获南京大学文学博士','个人页段晓琳名下明确“独撰”','2020年第8期全文转载','不另计作品','不是外刊署名认证']);
});
test('Jin three explicit degree qualifications remain distinct from non-degree masters preparation',async()=>{
 const p=person('jinyaqi');assert.deepEqual(p.education.map(e=>e.degree_awarded),[true,true,true,false]);assert(p.education.every(e=>e.degree_awarded_date===null));assert.equal(p.mentors.length,0);visible(await profile('jinyaqi'),['神户硕士预科与随后硕士、博士分别保留','预科非学位','不推罗马字署名同一','歴史女性']);
});

test('Chen course listing retains six undergraduate topics without inferring a lecturing role',async()=>{
 const p=person('chenchen');assert.deepEqual(p.education.map(e=>e.degree_awarded),[true,null,true,false]);assert.equal(p.teaching.length,1);const t=p.teaching[0];assert.equal(t.role,'官网课程列目');assert.deepEqual(t.courses,['学术英语与国际交流','专业英语','组织行为学','科研选题与写作','公共政策分析','公共事业管理学']);assert.equal(p.education.filter(e=>e.degree_awarded===false).length,1);visible(await profile('chenchen'),['官网课程列目','本科生课程','visiting professor','不拆重复事件','He obtained a PhD']);visible(await graph('chenchen'),['Frank Vanclay','Terry van Dijk']);
});
test('Xie independent doctoral identity does not bind an unspecified guide or Toronto stage to the doctorate',async()=>{
 const p=person('xieyangbin');assert.deepEqual(p.education.map(e=>e.degree_awarded),[null,null,true,false,false]);const m=p.mentors.find(m=>m.name==='桑新民');assert.equal(m.education_event_id,null);assert.deepEqual(mentorEvents(p,m),[]);assert.equal(p.mentors.find(m=>m.name==='Marlen Scardamalia').education_event_id,'ouc-xieyangbin-nondegree-1');visible(await profile('xieyangbin'),['独立职业标签“博士/博士后、副教授、硕士生导师”','具体阶段未知','多伦多联合培养级别未知','哲学为研究领域','教材副主编和主编为编辑角色']);visible(await graph('xieyangbin'),['桑新民','Marlen Scardamalia']);
});
test('Li Pihong 2011 masters diploma is a qualification not a certified degree or equivalent credential',async()=>{
 const p=person('lipihong');assert.deepEqual(p.education.map(e=>e.degree_awarded),[null,null]);assert.equal(p.qualification_items.length,1);const q=p.qualification_items[0];assert.equal(q.qualification_as_source,'硕士文凭');assert.equal(q.award_year_as_source,2011);assert.equal(q.degree_awarded,null);assert.equal(q.degree_equivalence_verified,false);assert.equal(p.mentors.length,4);assert.equal(p.mentors.filter(m=>m.education_event_id===null).length,2);assert.equal(p.publications.length,0);visible(await profile('lipihong'),['2011年获得硕士文凭另列资格','不自动等同授位','演出不改为论文、作曲或作者身份']);visible(await graph('lipihong'),['刘新起','朱同德','韩国良','Richard Davis']);
});
test('Sui explicit source-reported qualifications retain original years without French legal-equivalence claims',async()=>{
 const p=person('suitiankai');assert.deepEqual(p.education.map(e=>e.degree_awarded),[true,true,true]);assert.deepEqual(p.education.map(e=>e.degree_awarded_year),[2006,2011,2013]);assert(p.education.every(e=>e.degree_awarded_date===null));assert.equal(p.mentors.length,4);assert.equal(p.publications.length,0);visible(await profile('suitiankai'),['不认证法国文凭法律类型、授位权、跨国等同性','不认证法定博士授予权','2013获得博士学位按官网原称记录']);visible(await graph('suitiankai'),['朱梅玲','杨列京','Stutzmann','Gael de kerret']);
});
test('OUC all reviewed limits, publication qualifiers and teaching roles appear in actual profile rows',async()=>{
 for(const p of mapping.people){const html=await profile(p.person_id.slice(4));visible(html,p.unknowns);
 for(const list of [p.education,p.appointments,p.publications])for(const item of list)if(item.note)visible(html,[item.note]);
 for(const t of p.teaching){const title=t.name||t.course||(t.courses||[]).join('、');const rows=[...html.matchAll(/<li>[\s\S]*?<\/li>/g)].map(m=>m[0]);const row=rows.find(r=>r.includes('<strong>'+escapeHtml(title)+'</strong>'));assert(row,p.person_id+' '+title);if(t.role)visible(row,[t.role]);if(t.note)visible(row,[t.note]);}
 }
});
