import {readAtlasFile,createAtlasFetch} from './atlas-test-io.js';
import {test} from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {matches, stages, mentorOfficialUrl, mentorProfileRoute} from '../site/model.js';
const hustMapping=JSON.parse(fs.readFileSync(new URL('./fixtures/independent-hust12-source-mapping.json',import.meta.url)));
const whuMapping=JSON.parse(fs.readFileSync(new URL('./fixtures/independent-whu9-source-mapping.json',import.meta.url)));
const xjtuMapping=JSON.parse(fs.readFileSync(new URL('./fixtures/independent-xjtu12-source-mapping.json',import.meta.url)));
const rucMapping=JSON.parse(fs.readFileSync(new URL('./fixtures/independent-ruc8-source-mapping.json',import.meta.url)));
const ecnuMapping=JSON.parse(fs.readFileSync(new URL('./fixtures/independent-ecnu12-source-mapping.json',import.meta.url)));
const buaaMapping=JSON.parse(fs.readFileSync(new URL('./fixtures/independent-buaa12-source-mapping.json',import.meta.url)));
const tongjiMapping=JSON.parse(fs.readFileSync(new URL('./fixtures/independent-tongji12-source-mapping.json',import.meta.url)));
const bitMapping=JSON.parse(fs.readFileSync(new URL('./fixtures/independent-bit12-source-mapping.json',import.meta.url)));
const nwpuMapping=JSON.parse(fs.readFileSync(new URL('./fixtures/independent-nwpu12-source-mapping.json',import.meta.url)));
const scutMapping=JSON.parse(fs.readFileSync(new URL('./fixtures/independent-scut11-source-mapping.json',import.meta.url)));
const ustcMapping=JSON.parse(fs.readFileSync(new URL('./fixtures/independent-ustc12-source-mapping.json',import.meta.url)));
const db=readAtlasFile(new URL('../site/atlas.json',import.meta.url));
const roster=JSON.parse(fs.readFileSync(new URL('../site/rosters.json',import.meta.url)));
const mapping=JSON.parse(fs.readFileSync(new URL('./fixtures/independent-csu12-source-mapping.json',import.meta.url)));
test('actual CSU cohort exactly preserves independently reviewed fields, identities and scope',()=>{
 assert.equal(db.people.length,737+mapping.people.length+hustMapping.people.length+whuMapping.people.length+xjtuMapping.people.length+rucMapping.people.length+ecnuMapping.people.length+buaaMapping.people.length+tongjiMapping.people.length+bitMapping.people.length+nwpuMapping.people.length+scutMapping.people.length+ustcMapping.people.length);assert.equal(db.build_id,roster.build_id);
 for(const expected of mapping.people){
  const actual=db.people.find(p=>p.person_id===expected.person_id);assert.deepEqual(actual,expected);
  assert.equal(typeof actual.department,'string');assert(actual.department.length>0);
  assert(matches(actual,{q:actual.name},db.org_units));assert(matches(actual,{school:'csu',org:actual.department_id},db.org_units));
  assert(!matches(actual,{school:'seu'},db.org_units));assert.equal(actual.quick_link_eligible,false);assert.equal(actual.include_in_current_faculty_count,false);
  for(const mentor of actual.mentors){assert.equal(mentorOfficialUrl(mentor),'');assert.equal(mentorProfileRoute(mentor,db.people),'');}
  for(const stage of ['bachelor','master','doctor']) for(const event of stages(actual,stage)){assert.equal(event.event_kind,'degree');assert.equal(event.degree_awarded,true);}
 }
});
let serial=0;
async function render(hash){
 const nodes=new Map(),node=k=>{if(!nodes.has(k))nodes.set(k,{innerHTML:'',textContent:'',value:'',style:{},events:{},dataset:{height:'320'},clientWidth:960,addEventListener(t,f){this.events[t]=f},click(){this.onclick?.()}});return nodes.get(k)};
 globalThis.document={querySelector:node,querySelectorAll:()=>[],getElementById:id=>node('#'+id)};
 globalThis.location={href:"https://atlas.test/site/index.html",hash};globalThis.window={scrollTo(){},addEventListener(){}};
 globalThis.fetch=createAtlasFetch(db,roster);
 await import('../site/app.js?current-csu-release='+serial++);
 assert(!node('#main').innerHTML.includes('资料暂未加载'));return node;
}
for(const expected of mapping.people)test('actual CSU profile and lineage preserve '+expected.name,async()=>{
 const nodes=await render('#/person/'+expected.person_id);const html=['#main','#profile-content'].map(k=>nodes(k).innerHTML).join('\n');
 assert(html.includes(expected.name));assert(html.includes('中南大学'));
 const lineage=await render('#/person/'+expected.person_id+'/lineage');
 const relationHtml=['#main','#profile-content','#mind-stage'].map(k=>lineage(k).innerHTML).join('\n');
 for(const mentor of expected.mentors){assert(relationHtml.includes(mentor.name));assert(relationHtml.includes(mentor.type_label||mentor.type));}
 if(expected.mentors.length===0)assert(relationHtml.includes('0条已收录关系'));
});






test('unsupported executive-director role and coauthor mentorship are not inferred',async()=>{
 const p=db.people.find(p=>p.person_id==='csu-fenghui');assert.equal(p.mentors.length,0);
 const n=await render('#/person/'+p.person_id),h=n('#main').innerHTML+n('#profile-content').innerHTML;for(const phrase of ['主任、教授','执行主任未留原句','不新增角色'])assert(h.includes(phrase));
 assert(!p.appointments.some(a=>String(a.role||a.title||'').includes('执行主任')));
});
test('named course and teaching duties remain separate without invented lecturer roles',async()=>{
 const d=db.people.find(p=>p.person_id==='csu-denglu');assert.equal(d.teaching.length,1);assert.equal(d.teaching[0].name,'外科护理学');assert(!d.teaching[0].role);
 const y=db.people.find(p=>p.person_id==='csu-yiqiao');assert.equal(y.teaching.length,1);assert.equal(y.teaching[0].include_in_named_course_count,false);assert.equal(y.teaching[0].role,'从事教学工作');assert.equal(y.publications.length,0);assert.equal(y.mentors.length,2);
 const n=await render('#/person/'+y.person_id),h=n('#main').innerHTML+n('#profile-content').innerHTML;for(const phrase of ['具体课程未披露','不推教授/专任教师身份','作品库存0不代表没有成果','口腔正畸科'])assert(h.includes(phrase));
});
test('unretained search-index advisors do not become accepted mentorship and textbook participation stays bounded',async()=>{
 const p=db.people.find(p=>p.person_id==='csu-guocan');assert.equal(p.mentors.length,0);assert.equal(p.publications.length,1);
 const n=await render('#/person/'+p.person_id),h=n('#main').innerHTML+n('#profile-content').innerHTML;for(const phrase of ['索引仅发现线索','不接受这两条师承','参编教材','未列职称','不能倒推2006年起已为教授'])assert(h.includes(phrase));
});
test('expired appointment listing and older lecturer title coexist without inferred retirement or institutional merger',async()=>{
 const p=db.people.find(p=>p.person_id==='csu-wenyu');assert.equal(p.department_id,'csu-furong-laboratory');assert.equal(p.mentors.length,2);
 const n=await render('#/person/'+p.person_id),h=n('#main').innerHTML+n('#profile-content').innerHTML;for(const phrase of ['2025/01/15','讲师','聘期到期','不推退休/终止雇佣','不能导入药学院现任专任','2018硕士/2023博士'])assert(h.includes(phrase));
});
test('unknown mentorship stage does not attach to a degree and postdoctoral completion is not a new award',async()=>{
 const p=db.people.find(p=>p.person_id==='csu-yaohailin');assert.equal(p.mentors.length,1);const m=p.mentors[0];assert.equal(m.name,'王珺');assert(!m.education_event_id);assert(String(m.type).includes('阶段未明'));
 const n=await render('#/person/'+p.person_id),h=n('#main').innerHTML+n('#profile-content').innerHTML;for(const phrase of ['不挂任一本硕博/博士后事件','出站叙述年','不扩写成经济学硕士','国家企业中心认定'])assert(h.includes(phrase));
});
test('historical unit names and visible professional facts survive empty appointment arrays without invented employment',async()=>{
 for(const [id,phrases] of [['csu-yanjiexiong',['人文学院教授','文学与新闻传播学院','不推更名','鲁迅文学院高研班','陈晓明']],['csu-fengjie',['人文学院副教授','硕导是本人资格','完整作者和贡献未列']]]){
 const p=db.people.find(p=>p.person_id===id);const n=await render('#/person/'+id),h=n('#main').innerHTML+n('#profile-content').innerHTML;for(const phrase of phrases)assert(h.includes(phrase));
 }
 assert.equal(db.people.find(p=>p.person_id==='csu-fengjie').mentors.length,0);
});
test('official explicit degrees paired with graduation stay source-reported awards rather than certificate authentication',async()=>{
 const p=db.people.find(p=>p.person_id==='csu-daiyu');const degrees=p.education.filter(e=>e.event_kind==='degree');assert.equal(degrees.length,3);for(const e of degrees){assert.equal(e.degree_awarded,true);assert.equal(e.award_date,null);assert.equal(e.degree_awarded_date,null);assert.equal(e.degree_awarded_year,null);}
 const n=await render('#/person/'+p.person_id),h=n('#main').innerHTML+n('#profile-content').innerHTML;for(const phrase of ['具体学位及毕业标签','来源报告获授','未核学位证','授位日期均未知','不是生涯零成果'])assert(h.includes(phrase));
});
test('conflicting professor labels and source-specific teaching roles are not normalized to a guessed current title',async()=>{
 const p=db.people.find(p=>p.person_id==='csu-yanlei');assert.equal(p.mentors.length,2);assert.equal(p.publications.length,0);assert.deepEqual(p.teaching.map(t=>t.role),['主讲','参与讲授','讲授']);
 const n=await render('#/person/'+p.person_id),h=n('#main').innerHTML+n('#profile-content').innerHTML;for(const phrase of ['教授','副教授','不选当前职称赢家','2018-2019','2022-2023','2019-2020'])assert(h.includes(phrase));
});
test('chemistry Wang Miao stays separate from the different arts identity and joining month does not date professorship',async()=>{
 const p=db.people.find(p=>p.person_id==='csu-wangmiao');assert.equal(p.name,'王淼');assert.equal(p.department_id,'csu-chemistry-organic-polymer');assert.equal(p.mentors.length,1);assert.equal(p.mentors[0].name,'胡鹏');
 const n=await render('#/person/'+p.person_id),h=n('#main').innerHTML+n('#profile-content').innerHTML;for(const phrase of ['不与艺术王苗混同','2024-11仅入职','不另证该职称起任月','不能变授位月'])assert(h.includes(phrase));
});
test('historical college labels and publication dates remain distinct rather than silently corrected',async()=>{
 const p=db.people.find(p=>p.person_id==='csu-zhangligang');assert.equal(p.publications.length,2);const n=await render('#/person/'+p.person_id),h=n('#main').innerHTML+n('#profile-content').innerHTML;for(const phrase of ['料科学','不推历史更名','2026-01-01','2026-07-23','国家首批一流课程'])assert(h.includes(phrase));
});
test('each teaching row retains its exact title, role and scope without counting unlisted duties as a named course',async()=>{
 let checked=0;
 for(const p of mapping.people){if(!p.teaching?.length)continue;const n=await render('#/person/'+p.person_id),h=n('#main').innerHTML+n('#profile-content').innerHTML,section=h.split('<h2>公开教学事实</h2>')[1]?.split('</section>')[0]||'';
  for(const t of p.teaching){const name=t.name||t.course||(Array.isArray(t.courses)?t.courses.join('、'):null);assert(name);const esc=v=>String(v).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));const row=(section.match(/<li>[\s\S]*?<\/li>/g)||[]).find(r=>r.includes('<strong>'+esc(name)+'</strong>'));assert(row,p.person_id+' '+name);if(t.role){assert(row.includes(' · '+esc(t.role)));assert(!row.includes('具体教学角色未披露'));}if(t.note)assert(row.includes(esc(t.note)));checked++;}
 }
 assert.equal(checked,7);
});
test('ten independently reviewed degree corrections follow specific official evidence while ambiguous labels remain unknown',async()=>{
 const corrected={
  'csu-yanlei':['csu-yanlei-bachelor'],
  'csu-fenghui':['csu-fenghui-education-5','csu-fenghui-education-6','csu-fenghui-education-7'],
  'csu-guocan':['csu-guocan-education-1','csu-guocan-education-2','csu-guocan-education-3'],
  'csu-yanjiexiong':['csu-yanjiexiong-education-1','csu-yanjiexiong-education-2'],
  'csu-fengjie':['csu-fengjie-education-1']
 };
 let count=0;
 for(const [id,ids] of Object.entries(corrected)){
  const p=db.people.find(p=>p.person_id===id);
  for(const eventId of ids){const e=p.education.find(e=>e.event_id===eventId);assert(e,eventId);assert.equal(e.degree_awarded,true,eventId);assert.equal(e.event_kind,'degree',eventId);assert.equal(e.source_degree_awarded,null,eventId);const dates=['award_date','degree_award_date','degree_awarded_date','degree_awarded_year','award_year'].filter(key=>key in e);assert(dates.length>0,eventId);for(const key of dates)assert.equal(e[key],null,eventId+' '+key);count++;}
  const n=await render('#/person/'+id),h=n('#main').innerHTML+n('#profile-content').innerHTML;assert(!h.includes('保留原源审保守'));assert(!h.includes('沿用原源审保守'));
 }
 assert.equal(count,10);
 const d=db.people.find(p=>p.person_id==='csu-denglu');assert.equal(d.education.length,3);for(const e of d.education)assert.equal(e.degree_awarded,null);
});
