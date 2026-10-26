import {createImmutableCohortRenderer} from './immutable-cohort-renderer.js';
import {readAtlasFile,createAtlasFetch} from './atlas-test-io.js';
import {test} from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {matches, stages, mentorOfficialUrl, mentorProfileRoute} from '../site/model.js';
const csuMapping=JSON.parse(fs.readFileSync(new URL('./fixtures/independent-csu12-source-mapping.json',import.meta.url)));
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
const cauMapping=JSON.parse(fs.readFileSync(new URL('./fixtures/independent-cau12-source-mapping.json',import.meta.url)));
const fduMapping=JSON.parse(fs.readFileSync(new URL('./fixtures/independent-fdu12-source-mapping.json',import.meta.url)));
const mucMapping=JSON.parse(fs.readFileSync(new URL('./fixtures/independent-muc12-source-mapping.json',import.meta.url)));
const nwsuafMapping=JSON.parse(fs.readFileSync(new URL('./fixtures/independent-nwsuaf12-source-mapping.json',import.meta.url)));
const oucMapping=JSON.parse(fs.readFileSync(new URL('./fixtures/independent-ouc12-source-mapping.json',import.meta.url)));
const lzuMapping=JSON.parse(fs.readFileSync(new URL('./fixtures/independent-lzu11-source-mapping.json',import.meta.url)));
const sjtuMapping=JSON.parse(fs.readFileSync(new URL('./fixtures/independent-sjtu11-source-mapping.json',import.meta.url)));
const thuMapping=JSON.parse(fs.readFileSync(new URL('./fixtures/independent-thu11-source-mapping.json',import.meta.url)));
const pkuMapping=JSON.parse(fs.readFileSync(new URL('./fixtures/independent-pku11-source-mapping.json',import.meta.url)));
const zjuMapping=JSON.parse(fs.readFileSync(new URL('./fixtures/independent-zju7-source-mapping.json',import.meta.url)));
const mixedMapping=JSON.parse(fs.readFileSync(new URL('./fixtures/independent-neu4-cqu3-sysu2-source-mapping.json',import.meta.url)));
const njuSecondMapping=JSON.parse(fs.readFileSync(new URL('./fixtures/independent-nju11-second-source-mapping.json',import.meta.url)));
const db=readAtlasFile(new URL('../site/atlas.json',import.meta.url));
const roster=JSON.parse(fs.readFileSync(new URL('../site/rosters.json',import.meta.url)));
const mapping=JSON.parse(fs.readFileSync(new URL('./fixtures/independent-sdu12-source-mapping.json',import.meta.url)));
test('actual SDU cohort exactly preserves independently reviewed fields, identities and scope',()=>{
 assert.equal(db.people.length,725+mapping.people.length+csuMapping.people.length+hustMapping.people.length+whuMapping.people.length+xjtuMapping.people.length+rucMapping.people.length+ecnuMapping.people.length+buaaMapping.people.length+tongjiMapping.people.length+bitMapping.people.length+nwpuMapping.people.length+scutMapping.people.length+ustcMapping.people.length+cauMapping.people.length+fduMapping.people.length+mucMapping.people.length+nwsuafMapping.people.length+oucMapping.people.length+lzuMapping.people.length+sjtuMapping.people.length+thuMapping.people.length+pkuMapping.people.length+zjuMapping.people.length+mixedMapping.people.length+njuSecondMapping.people.length);assert.equal(db.build_id,roster.build_id);
 for(const expected of mapping.people){
  const actual=db.people.find(p=>p.person_id===expected.person_id);assert.deepEqual(actual,expected);
  assert.equal(typeof actual.department,'string');assert(actual.department.length>0);
  assert(matches(actual,{q:actual.name},db.org_units));assert(matches(actual,{school:'sdu',org:actual.department_id},db.org_units));
  assert(!matches(actual,{school:'seu'},db.org_units));assert.equal(actual.quick_link_eligible,false);assert.equal(actual.include_in_current_faculty_count,false);
  for(const mentor of actual.mentors){assert.equal(mentorOfficialUrl(mentor),'');assert.equal(mentorProfileRoute(mentor,db.people),'');}
  for(const stage of ['bachelor','master','doctor']) for(const event of stages(actual,stage)){assert.equal(event.event_kind,'degree');assert.equal(event.degree_awarded,true);}
 }
});
const {render}=createImmutableCohortRenderer({db,roster,fixtureId:import.meta.url});
for(const expected of mapping.people)test('actual SDU profile and lineage preserve '+expected.name,async()=>{
 const nodes=await render('#/person/'+expected.person_id);const html=['#main','#profile-content'].map(k=>nodes(k).innerHTML).join('\n');
 assert(html.includes(expected.name));assert(html.includes('山东大学'));
 const lineage=await render('#/person/'+expected.person_id+'/lineage');
 const relationHtml=['#main','#profile-content','#mind-stage'].map(k=>lineage(k).innerHTML).join('\n');
 for(const mentor of expected.mentors){assert(relationHtml.includes(mentor.name));assert(relationHtml.includes(mentor.type_label||mentor.type));}
 if(expected.mentors.length===0)assert(relationHtml.includes('0条已收录关系'));
});






test('selected publisher metadata remains distinct from official bibliography and unread full text',async()=>{
 const p=db.people.find(p=>p.person_id==='sdu-zhangna');assert.equal(p.publications.length,2);
 assert.equal(p.publications[0].publisher_metadata_verified,false);assert.equal(p.publications[1].publisher_metadata_verified,true);for(const w of p.publications)assert.equal(w.full_text_read,false);
 const n=await render('#/person/'+p.person_id),h=n('#main').innerHTML+n('#profile-content').innerHTML;
 for(const phrase of ['2020-10-27','2021','通讯作者Na Zhang','星号未据此解释'])assert(h.includes(phrase));
});
test('study institution and degree-awarding institution are not conflated',async()=>{
 const p=db.people.find(p=>p.person_id==='sdu-wangliping');const e=p.education.find(e=>e.awarding_institution==='厦门大学');assert(e);assert.equal(e.institution,'山东大学');assert.equal(e.degree_awarded,true);
 const n=await render('#/person/'+p.person_id),h=n('#main').innerHTML+n('#profile-content').innerHTML;
 for(const phrase of ['学习单位山东大学','授位大学厦门大学','不得统一改成一个单位'])assert(h.includes(phrase));
});
test('law department label does not invent a historical major and doctoral guidance is not thesis authentication',async()=>{
 const n=await render('#/person/sdu-zhanghaiyan'),h=n('#main').innerHTML+n('#profile-content').innerHTML;assert(h.includes('专业与法学学位类别未据院系猜填'));
 const p=db.people.find(p=>p.person_id==='sdu-yidonglan');assert.equal(p.mentors.length,1);assert.equal(p.mentors[0].name,'杨国荣');assert.equal(p.mentors[0].education_stage,'博士');
 const e=await render('#/person/'+p.person_id),eh=e('#main').innerHTML+e('#profile-content').innerHTML;for(const phrase of ['合编','未证明正式论文导师','版权年份'])assert(eh.includes(phrase));
});
test('scholarship provider does not become an unverified visiting host and incomplete publication coverage stays bounded',async()=>{
 const p=db.people.find(p=>p.person_id==='sdu-sunlixin');const visit=p.education.find(e=>e.event_kind==='visiting_scholar');assert(visit);assert.equal(visit.institution,'接收机构未披露');assert.equal(visit.degree_awarded,false);
 const n=await render('#/person/'+p.person_id),h=n('#main').innerHTML+n('#profile-content').innerHTML;assert(h.includes('美因兹仅奖学金提供者'));
 const f=db.people.find(p=>p.person_id==='sdu-fanghui');assert.equal(f.publications.length,1);assert.equal(f.mentors.length,2);const fn=await render('#/person/'+f.person_id),fh=fn('#main').innerHTML+fn('#profile-content').innerHTML;for(const phrase of ['仅收录1条','院长/馆长无日期','不认为当前仍任','Linda Nichals'])assert(fh.includes(phrase));
});
test('translation and coauthorship remain visible without treating joint training as a second degree',async()=>{
 const p=db.people.find(p=>p.person_id==='sdu-luhaobin');assert.equal(p.mentors.length,3);assert.equal(stages(p,'doctor').length,1);
 assert.equal(p.publications[0].type,'translated_book');assert.equal(p.publications[1].type,'coauthored_book');
 const n=await render('#/person/'+p.person_id),h=n('#main').innerHTML+n('#profile-content').innerHTML;for(const phrase of ['哈罗德·戈达德','本人角色为译','不是原著作者','两共著作者不改独著','不另增博士授位'])assert(h.includes(phrase));
});
test('historical dean interval, graduation dates and unresolved publication labels remain distinct',async()=>{
 const p=db.people.find(p=>p.person_id==='sdu-liusenlin');assert.equal(p.mentors.length,0);assert.equal(p.education[0].degree_awarded,null);assert.equal(p.education[1].degree_awarded,null);assert.equal(p.education[2].degree_awarded,true);
 const n=await render('#/person/'+p.person_id),h=n('#main').innerHTML+n('#profile-content').innerHTML;for(const phrase of ['2018-04至2023-12','非当前院长','2001-06','不作授位日期','人民出版社2022','江苏人民出版社2013','不增加第二作品'])assert(h.includes(phrase));
});
test('former dean term and conflicting historical school names do not imply current appointment or corrected degree title',async()=>{
 const p=db.people.find(p=>p.person_id==='sdu-wangkefang');assert.equal(p.mentors.length,0);
 const n=await render('#/person/'+p.person_id),h=n('#main').innerHTML+n('#profile-content').innerHTML;for(const phrase of ['曾任2016–2026','不推仍任院长或已退休','北京医科大学/北京大学','护医学博士学位','不擅自纠错'])assert(h.includes(phrase));
});
test('missing undergraduate history and unnamed appointment unit are not filled from current profile',async()=>{
 const p=db.people.find(p=>p.person_id==='sdu-liyuli');assert.equal(stages(p,'bachelor').length,0);assert.equal(p.mentors.length,0);
 const n=await render('#/person/'+p.person_id),h=n('#main').innerHTML+n('#profile-content').innerHTML;for(const phrase of ['本科求学及授位未知不填事件','2019“山东大学学院副研究员”','不补为护理与康复学院','独立通讯作者'])assert(h.includes(phrase));
});
test('textbook chief-editorship and nursing qualification do not become journal authorship or employment',async()=>{
 const p=db.people.find(p=>p.person_id==='sdu-lijing-nursing');assert.equal(p.mentors.length,0);const n=await render('#/person/'+p.person_id),h=n('#main').innerHTML+n('#profile-content').innerHTML;
 for(const phrase of ['健康评估数字课程','数字教材','主编','不把主编改成论文作者','注册护士','不额外生成雇佣任职'])assert(h.includes(phrase));
 const c=await render('#/person/sdu-lichaofan-policy'),ch=c('#main').innerHTML+c('#profile-content').innerHTML;for(const phrase of ['博士后非学位','完整作者未知','不是已证首作或通讯'])assert(ch.includes(phrase));
});
test('all teaching records retain titles, roles and level notes on their own actual course rows',async()=>{
 let checked=0;
 for(const p of mapping.people){if(!p.teaching?.length)continue;const n=await render('#/person/'+p.person_id),h=n('#main').innerHTML+n('#profile-content').innerHTML,section=h.split('<h2>公开教学事实</h2>')[1]?.split('</section>')[0]||'';
  for(const t of p.teaching){const name=t.name||t.course||(Array.isArray(t.courses)?t.courses.join('、'):null);assert(name);const escaped=value=>String(value).replace(/[&<>"']/g,char=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[char]));const row=(section.match(/<li>[\s\S]*?<\/li>/g)||[]).find(r=>r.includes('<strong>'+escaped(name)+'</strong>'));assert(row,p.person_id+' '+name);if(t.role){assert(row.includes(' · '+t.role));assert(!row.includes('具体教学角色未披露'));}if(t.note)assert(row.includes(escaped(t.note)));checked++;}
 }
 assert.equal(checked,16);
});
