import {test} from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {matches, stages, mentorOfficialUrl, mentorProfileRoute} from '../site/model.js';
const dlutMapping=JSON.parse(fs.readFileSync(new URL('./fixtures/independent-dlut12-source-mapping.json',import.meta.url)));
const jluMapping=JSON.parse(fs.readFileSync(new URL('./fixtures/independent-jlu12-source-mapping.json',import.meta.url)));
const sduMapping=JSON.parse(fs.readFileSync(new URL('./fixtures/independent-sdu12-source-mapping.json',import.meta.url)));
const csuMapping=JSON.parse(fs.readFileSync(new URL('./fixtures/independent-csu12-source-mapping.json',import.meta.url)));
const hustMapping=JSON.parse(fs.readFileSync(new URL('./fixtures/independent-hust12-source-mapping.json',import.meta.url)));
const whuMapping=JSON.parse(fs.readFileSync(new URL('./fixtures/independent-whu9-source-mapping.json',import.meta.url)));
const xjtuMapping=JSON.parse(fs.readFileSync(new URL('./fixtures/independent-xjtu12-source-mapping.json',import.meta.url)));
const rucMapping=JSON.parse(fs.readFileSync(new URL('./fixtures/independent-ruc8-source-mapping.json',import.meta.url)));
const db=JSON.parse(fs.readFileSync(new URL('../site/atlas.json',import.meta.url)));
const roster=JSON.parse(fs.readFileSync(new URL('../site/rosters.json',import.meta.url)));
const mapping=JSON.parse(fs.readFileSync(new URL('./fixtures/independent-nku12-source-mapping.json',import.meta.url)));
test('actual NKU cohort exactly preserves independently reviewed fields, identities and scope',()=>{
 assert.equal(db.people.length,689+mapping.people.length+dlutMapping.people.length+jluMapping.people.length+sduMapping.people.length+csuMapping.people.length+hustMapping.people.length+whuMapping.people.length+xjtuMapping.people.length+rucMapping.people.length);assert.equal(db.build_id,roster.build_id);
 for(const expected of mapping.people){
  const actual=db.people.find(p=>p.person_id===expected.person_id);assert.deepEqual(actual,expected);
  assert.equal(typeof actual.department,'string');assert(actual.department.length>0);
  assert(matches(actual,{q:actual.name},db.org_units));assert(matches(actual,{school:'nku',org:actual.department_id},db.org_units));
  assert(!matches(actual,{school:'seu'},db.org_units));assert.equal(actual.quick_link_eligible,false);assert.equal(actual.include_in_current_faculty_count,false);
  for(const mentor of actual.mentors){assert.equal(mentorOfficialUrl(mentor),'');assert.equal(mentorProfileRoute(mentor,db.people),'');}
  for(const stage of ['bachelor','master','doctor']) for(const event of stages(actual,stage)){assert.equal(event.event_kind,'degree');assert.equal(event.degree_awarded,true);}
 }
});
let serial=0;
async function render(hash){
 const nodes=new Map(),node=k=>{if(!nodes.has(k))nodes.set(k,{innerHTML:'',textContent:'',value:'',style:{},events:{},dataset:{height:'320'},clientWidth:960,addEventListener(t,f){this.events[t]=f},click(){this.onclick?.()}});return nodes.get(k)};
 globalThis.document={querySelector:node,querySelectorAll:()=>[],getElementById:id=>node('#'+id)};
 globalThis.location={hash};globalThis.window={scrollTo(){},addEventListener(){}};
 globalThis.fetch=async p=>({ok:true,json:async()=>structuredClone(String(p).startsWith('atlas.json')?db:roster)});
 await import('../site/app.js?current-nku-release='+serial++);
 assert(!node('#main').innerHTML.includes('资料暂未加载'));return node;
}
for(const expected of mapping.people)test('actual NKU profile and lineage preserve '+expected.name,async()=>{
 const nodes=await render('#/person/'+expected.person_id);const html=['#main','#profile-content'].map(k=>nodes(k).innerHTML).join('\n');
 assert(html.includes(expected.name));assert(html.includes('南开大学'));
 const lineage=await render('#/person/'+expected.person_id+'/lineage');
 const relationHtml=['#main','#profile-content','#mind-stage'].map(k=>lineage(k).innerHTML).join('\n');
 for(const mentor of expected.mentors){assert(relationHtml.includes(mentor.name));assert(relationHtml.includes(mentor.type_label||mentor.type));}
 if(expected.mentors.length===0)assert(relationHtml.includes('0条已收录关系'));
});





test('explicit retirement and historical Chinese department remain visible without present affiliation invention',async()=>{
 const p=mapping.people.find(p=>p.person_id==='nankai-liulili');assert.equal(p.retirement_status,'retired_as_source');assert.equal(p.department_id,'nku-chinese-historical');
 const nodes=await render('#/person/'+p.person_id);const html=['#main','#profile-content'].map(k=>nodes(k).innerHTML).join('\n');
 for(const value of ['2018年退休','中文系为历史任教单位','不认证现行中文系或文学院归属','出版年和出版社未知','不从博导资格造博士'])assert(html.includes(value),value);
});
test('literary roles and stage-specific guidance do not manufacture authorship or dissertation authentication',async()=>{
 const hao=await render('#/person/nankai-haolan');const html=['#main','#profile-content'].map(k=>hao(k).innerHTML).join('\n');assert(html.includes('主编不填作者'));assert(html.includes('博士后出站及四处访问'));
 const p=mapping.people.find(p=>p.person_id==='nankai-luozhenya');assert.deepEqual(p.mentors.map(m=>m.name),['田仲济','吕家乡','龙泉明']);
 const luo=await render('#/person/'+p.person_id);const details=['#main','#profile-content'].map(k=>luo(k).innerHTML).join('\n');assert(details.includes('不添加中国语言文学系'));assert(details.includes('均非已核原论文导师'));
});

test('professional research guidance stays visible without promotion to degree mentorship',async()=>{
 for(const [id,name,qualifier] of [['nku-lingfeng','Srinivas Bettadpur','最后一项只属职业指导'],['nku-xuexue','张宏','助理研究员不改写为博士后']]){
  const p=mapping.people.find(p=>p.person_id===id);assert.equal(p.professional_research_advisors.length,1);assert(p.professional_research_advisors[0].name.includes(name));assert(!p.mentors.some(m=>m.name.includes(name)));
  assert.equal(p.professional_research_advisors[0].include_in_degree_mentorship_graph,false);
  const nodes=await render('#/person/'+id);const html=['#main','#profile-content'].map(k=>nodes(k).innerHTML).join('\n');assert(html.includes(name),name);assert(html.includes(qualifier),qualifier);
 }
 const p=mapping.people.find(p=>p.person_id==='nku-luzhaoyong');assert.deepEqual(p.mentors.map(m=>m.name),['翟宏斌','李昂']);assert(p.mentors.every(m=>m.type.includes('阶段未知')));
 const nodes=await render('#/person/'+p.person_id);const html=['#main','#profile-content'].map(k=>nodes(k).innerHTML).join('\n');assert(html.includes('课题组负责人不提升为明确个人指导关系'));
});

test('shared postgraduate intervals and unverified degree labels remain conservative in actual profiles',async()=>{
 const guan=await render('#/person/nku-guanyongqiang-economic-history');const html=['#main','#profile-content'].map(k=>guan(k).innerHTML).join('\n');for(const value of ['共一事件','不拆造两段日期或两获授','两访学为非学位事件','不升级学位论文关系'])assert(html.includes(value),value);
 const p=mapping.people.find(p=>p.person_id==='nku-guanyongqiang-economic-history');assert.equal(p.department_id,'nku-economics');assert.equal(p.mentors.length,3);
 const mao=await render('#/person/nku-maodaqing-medical');const details=['#main','#profile-content'].map(k=>mao(k).innerHTML).join('\n');assert(details.includes('四学习/学位标签都未明确获授'));assert(details.includes('鲁汶大学不强行映射英文法定实体'));assert(details.includes('第7位'));
});

test('each source-reported teaching level is visible on its own course row, not inferred from biography',async()=>{
 for(const [id,course,level] of [['nku-zhangzhihong','中国政府与政治','本科生课程'],['nku-zhangzhihong','政府间关系研究','硕士生课程'],['nku-guanyongqiang-economic-history','中国经济史','本科']]){
  const nodes=await render('#/person/'+id);const html=['#main','#profile-content'].map(k=>nodes(k).innerHTML).join('\n');const section=html.split('<h2>公开教学事实</h2>')[1]?.split('</section>')[0]||'';
  const row=(section.match(/<li>[\s\S]*?<\/li>/g)||[]).find(value=>value.includes(course));assert(row,course);assert(row.includes(level),id+' '+course+' '+level);
 }
});
