import {test} from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {matches, stages, mentorOfficialUrl, mentorProfileRoute} from '../site/model.js';
const jluMapping=JSON.parse(fs.readFileSync(new URL('./fixtures/independent-jlu12-source-mapping.json',import.meta.url)));
const sduMapping=JSON.parse(fs.readFileSync(new URL('./fixtures/independent-sdu12-source-mapping.json',import.meta.url)));
const csuMapping=JSON.parse(fs.readFileSync(new URL('./fixtures/independent-csu12-source-mapping.json',import.meta.url)));
const db=JSON.parse(fs.readFileSync(new URL('../site/atlas.json',import.meta.url)));
const roster=JSON.parse(fs.readFileSync(new URL('../site/rosters.json',import.meta.url)));
const mapping=JSON.parse(fs.readFileSync(new URL('./fixtures/independent-dlut12-source-mapping.json',import.meta.url)));
test('actual DLUT cohort exactly preserves independently reviewed fields, identities and scope',()=>{
 assert.equal(db.people.length,701+mapping.people.length+jluMapping.people.length+sduMapping.people.length+csuMapping.people.length);assert.equal(db.build_id,roster.build_id);
 for(const expected of mapping.people){
  const actual=db.people.find(p=>p.person_id===expected.person_id);assert.deepEqual(actual,expected);
  assert.equal(typeof actual.department,'string');assert(actual.department.length>0);
  assert(matches(actual,{q:actual.name},db.org_units));assert(matches(actual,{school:'dlut',org:actual.department_id},db.org_units));
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
 await import('../site/app.js?current-dlut-release='+serial++);
 assert(!node('#main').innerHTML.includes('资料暂未加载'));return node;
}
for(const expected of mapping.people)test('actual DLUT profile and lineage preserve '+expected.name,async()=>{
 const nodes=await render('#/person/'+expected.person_id);const html=['#main','#profile-content'].map(k=>nodes(k).innerHTML).join('\n');
 assert(html.includes(expected.name));assert(html.includes('大连理工大学'));
 const lineage=await render('#/person/'+expected.person_id+'/lineage');
 const relationHtml=['#main','#profile-content','#mind-stage'].map(k=>lineage(k).innerHTML).join('\n');
 for(const mentor of expected.mentors){assert(relationHtml.includes(mentor.name));assert(relationHtml.includes(mentor.type_label||mentor.type));}
 if(expected.mentors.length===0)assert(relationHtml.includes('0条已收录关系'));
});






test('emeritus listing and open-ended source employment coexist without inferred retirement date or re-employment',async()=>{
 const p=mapping.people.find(p=>p.person_id==='dlut-zhouwenjie-art');assert.equal(p.retirement_status,'emeritus_listed');assert.equal(p.quick_link_eligible,false);
 const nodes=await render('#/person/'+p.person_id);const html=['#main','#profile-content'].map(k=>nodes(k).innerHTML).join('\n');for(const value of ['荣休目录明确列名','2012.12至今教授同时保留','不推页面新旧、退休日期或返聘','不表示本人没有作品'])assert(html.includes(value),value);
});
test('empty education remains empty while source degree labels and teaching designation are visibly qualified',async()=>{
 const p=mapping.people.find(p=>p.person_id==='dlut-wanghuanming');assert.equal(p.education.length,0);
 const nodes=await render('#/person/'+p.person_id);const html=['#main','#profile-content'].map(k=>nodes(k).innerHTML).join('\n');assert(html.includes('不从标签拼造教育事件'));assert(html.includes('2025不是授课学期'));
 const section=html.split('<h2>公开教学事实</h2>')[1]?.split('</section>')[0]||'';for(const value of ['城市管理学','本科','负责人','2025','中国大学MOOC','学习强国'])assert(section.includes(value),value);
});
test('chapter contribution and unknown-stage mentorship do not become sole authorship or doctoral authentication',async()=>{
 const p=mapping.people.find(p=>p.person_id==='dlut-suyongjian-education');assert.equal(p.mentors.length,1);assert.equal(p.mentors[0].name,'张应强');assert(p.mentors[0].type.includes('阶段未明确'));
 const nodes=await render('#/person/'+p.person_id);const html=['#main','#profile-content'].map(k=>nodes(k).innerHTML).join('\n');for(const value of ['不挂接博士阶段','书级作者张应强等','第五章约3.5万字'])assert(html.includes(value),value);
});
test('history, editorship and undergraduate or postgraduate teaching roles remain visible',async()=>{
 const liu=await render('#/person/dlut-liumengyang');const html=['#main','#profile-content'].map(k=>liu(k).innerHTML).join('\n');assert(html.includes('副主编'));const teaching=html.split('<h2>公开教学事实</h2>')[1]?.split('</section>')[0]||'';assert(teaching.includes('本科生课程'));assert(teaching.includes('研究生课程'));
 const li=await render('#/person/dlut-lichong-higher-education');const details=['#main','#profile-content'].map(k=>li(k).innerHTML).join('\n');assert(details.includes('黑龙江省齐齐哈尔师范学院'));assert(details.includes('不替换现校名'));
 const ma=await render('#/person/dlut-mahui');const maHtml=['#main','#profile-content'].map(k=>ma(k).innerHTML).join('\n');assert(maHtml.includes('不代表本人没有作品'));assert(maHtml.includes('不独立认证整个区间职位连续性'));
 const math=mapping.people.find(p=>p.person_id==='dlut-lijunfeng');assert.equal(math.department_id,'dlut-math');
});

test('each reported teaching level and role is visible on its corresponding course row',async()=>{
 let checked=0;
 for(const p of mapping.people){
  if(!p.teaching?.length)continue;
  const nodes=await render('#/person/'+p.person_id);const html=['#main','#profile-content'].map(k=>nodes(k).innerHTML).join('\n');const section=html.split('<h2>公开教学事实</h2>')[1]?.split('</section>')[0]||'';
  for(const t of p.teaching){const level=t.level_as_source||t.student_level||t.level;if(!level)continue;const name=t.name||t.course||t.course_name;const row=(section.match(/<li>[\s\S]*?<\/li>/g)||[]).find(value=>value.includes(name));assert(row,p.person_id+' '+name);assert(row.includes(level),p.person_id+' '+name+' '+level);if(t.role_as_source)assert(row.includes(t.role_as_source));checked++;}
 }
 assert.equal(checked,6);
});

test('explicit teaching roles replace the unknown-role label on each of Liu Mengyang’s five course rows',async()=>{
 const p=mapping.people.find(p=>p.person_id==='dlut-liumengyang');assert.equal(p.teaching.length,5);
 const nodes=await render('#/person/'+p.person_id);const html=['#main','#profile-content'].map(k=>nodes(k).innerHTML).join('\n');const section=html.split('<h2>公开教学事实</h2>')[1]?.split('</section>')[0]||'';
 for(const [index,t] of p.teaching.entries()){
  const expected=index<4?'主讲':'承担教学工作';assert.equal(t.role,expected);
  const row=(section.match(/<li>[\s\S]*?<\/li>/g)||[]).find(value=>value.includes(t.name));assert(row,t.name);assert(row.includes(' · '+expected),t.name);assert(!row.includes('具体教学角色未披露'),t.name);assert(row.includes(index<4?'本科生':'研究生'),t.name);
 }
});
