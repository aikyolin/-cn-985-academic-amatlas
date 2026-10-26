import {readAtlasFile,createAtlasFetch} from './atlas-test-io.js';
import {test} from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {matches, stages, mentorOfficialUrl, mentorProfileRoute} from '../site/model.js';
const sduMapping=JSON.parse(fs.readFileSync(new URL('./fixtures/independent-sdu12-source-mapping.json',import.meta.url)));
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
const db=readAtlasFile(new URL('../site/atlas.json',import.meta.url));
const roster=JSON.parse(fs.readFileSync(new URL('../site/rosters.json',import.meta.url)));
const mapping=JSON.parse(fs.readFileSync(new URL('./fixtures/independent-jlu12-source-mapping.json',import.meta.url)));
test('actual JLU cohort exactly preserves independently reviewed fields, identities and scope',()=>{
 assert.equal(db.people.length,713+mapping.people.length+sduMapping.people.length+csuMapping.people.length+hustMapping.people.length+whuMapping.people.length+xjtuMapping.people.length+rucMapping.people.length+ecnuMapping.people.length+buaaMapping.people.length+tongjiMapping.people.length+bitMapping.people.length+nwpuMapping.people.length+scutMapping.people.length+ustcMapping.people.length+cauMapping.people.length+fduMapping.people.length+mucMapping.people.length+nwsuafMapping.people.length);assert.equal(db.build_id,roster.build_id);
 for(const expected of mapping.people){
  const actual=db.people.find(p=>p.person_id===expected.person_id);assert.deepEqual(actual,expected);
  assert.equal(typeof actual.department,'string');assert(actual.department.length>0);
  assert(matches(actual,{q:actual.name},db.org_units));assert(matches(actual,{school:'jlu',org:actual.department_id},db.org_units));
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
 await import('../site/app.js?current-jlu-release='+serial++);
 assert(!node('#main').innerHTML.includes('资料暂未加载'));return node;
}
for(const expected of mapping.people)test('actual JLU profile and lineage preserve '+expected.name,async()=>{
 const nodes=await render('#/person/'+expected.person_id);const html=['#main','#profile-content'].map(k=>nodes(k).innerHTML).join('\n');
 assert(html.includes(expected.name));assert(html.includes('吉林大学'));
 const lineage=await render('#/person/'+expected.person_id+'/lineage');
 const relationHtml=['#main','#profile-content','#mind-stage'].map(k=>lineage(k).innerHTML).join('\n');
 for(const mentor of expected.mentors){assert(relationHtml.includes(mentor.name));assert(relationHtml.includes(mentor.type_label||mentor.type));}
 if(expected.mentors.length===0)assert(relationHtml.includes('0条已收录关系'));
});






test('combined doctoral study does not invent a masters degree or coauthor mentorship',async()=>{
 const p=db.people.find(p=>p.person_id==='jlu-anni');assert.equal(p.mentors.length,0);
 assert.equal(stages(p,'master').length,0);
 const nodes=await render('#/person/'+p.person_id);const h=nodes('#main').innerHTML+nodes('#profile-content').innerHTML;
 for(const phrase of ['硕博连读','不制造硕士学位','孙俊奇','共同作者'])assert(h.includes(phrase));
});
test('five source-reported courses retain known teaching role without invented student level',async()=>{
 const p=db.people.find(p=>p.person_id==='jlu-wangting-economics');assert.equal(p.teaching.length,5);
 const nodes=await render('#/person/'+p.person_id);const h=nodes('#main').innerHTML+nodes('#profile-content').innerHTML;
 for(const course of p.teaching){assert.equal(course.role,'讲授');assert(h.includes(course.name));assert(h.includes(course.note));}
 assert(h.includes('授课层级、具体学期与实时开课未披露'));
});
test('historical degree-stage advisors remain explicit but not thesis-original authentication',async()=>{
 const p=db.people.find(p=>p.person_id==='jlu-wangdehui');assert.equal(p.department_id,'jlu-math');assert.equal(p.mentors.length,2);
 assert.equal(p.publications.length,2);for(const work of p.publications)assert.equal(work.type,'journal_article');
 assert.deepEqual(p.mentors.map(m=>m.name),['宋立新','史宁中']);assert.deepEqual(p.mentors.map(m=>m.education_stage),['硕士','博士']);
 for(const m of p.mentors){assert.equal(m.source_explicit_degree_supervisor,true);assert.equal(m.original_thesis_document_verified,false);assert.equal(m.formal_dissertation_advisor_verified,false);}
 const nodes=await render('#/person/'+p.person_id);const h=nodes('#main').innerHTML+nodes('#profile-content').innerHTML;
 for(const phrase of ['2006-09-03','1998年7月','三项授位均未知','不依据未留存材料'])assert(h.includes(phrase));
});
test('malformed source DOI remains literal and never becomes a repaired or clickable DOI',async()=>{
 const p=db.people.find(p=>p.person_id==='jlu-jinlina'),w=p.publications[0];
 assert.equal(w.doi_as_source,'0.1002/gepi.20521');assert.equal(w.doi_normalized,null);assert.equal(w.doi_hyperlink_generation_allowed,false);assert.equal(w.source_reported_work_url,null);
 const n=await render('#/person/'+p.person_id),h=n('#main').innerHTML+n('#profile-content').innerHTML;
 assert(h.includes('0.1002/gepi.20521'));assert(!h.includes('10.1002/gepi.20521'));assert(!/href=["'][^"']*(?:0\.1002|gepi\.20521)/.test(h));
 assert(h.includes('不推首作或通讯角色'));
});
test('joint doctoral training, overlapping employment and deputy editorship remain distinct',async()=>{
 const p=db.people.find(p=>p.person_id==='jlu-wangjuan');assert.equal(p.mentors.length,0);
 const n=await render('#/person/'+p.person_id),h=n('#main').innerHTML+n('#profile-content').innerHTML;
 for(const phrase of ['联合培养博士研究生不是第二博士授位','2015-11','2015-09','副主编','第7版','第3版'])assert(h.includes(phrase));
});
test('current discipline is not backfilled into historical education and page dates are not silently repaired',async()=>{
 for(const [id,phrases] of [['jlu-liwenjun',['现学科专业不是历史学习专业','教授经历止期空白','页脚2017']],['jlu-lvxuanru',['2024-09-26','正文含2025年作品','实际最后更新时间']]]){
  const p=db.people.find(p=>p.person_id===id);assert.equal(p.mentors.length,0);const n=await render('#/person/'+id),h=n('#main').innerHTML+n('#profile-content').innerHTML;for(const phrase of phrases)assert(h.includes(phrase));
 }
});
test('postdoctoral end-date conflict remains visible and doctoral versus postdoctoral guidance stays separate',async()=>{
 const p=db.people.find(p=>p.person_id==='jlu-zhouxin');assert.equal(p.mentors.length,4);assert.deepEqual(p.mentors.map(m=>m.education_stage),['博士','博士','博士','博士后']);
 const n=await render('#/person/'+p.person_id),h=n('#main').innerHTML+n('#profile-content').innerHTML;
 for(const phrase of ['2019.06','2020年完成','两说未裁定','不计雇佣任职'])assert(h.includes(phrase));
});
test('professor directory and older associate-professor wording coexist without invented promotion or retirement',async()=>{
 const p=db.people.find(p=>p.person_id==='jlu-yuxianfeng');assert.equal(p.mentors.length,2);for(const m of p.mentors)assert.equal(m.education_stage,'访问学者');
 const n=await render('#/person/'+p.person_id),h=n('#main').innerHTML+n('#profile-content').innerHTML;
 for(const phrase of ['教授','2012.09至现在副教授','不推晋升','未观察本人退休标签'])assert(h.includes(phrase));
});
test('creative design credit and different historical institutional scopes are not collapsed into false authorship or mentorship',async()=>{
 const g=await render('#/person/jlu-guochunfang'),gh=g('#main').innerHTML+g('#profile-content').innerHTML;
 for(const phrase of ['雪容融','2019','总设计','不推唯一作者'])assert(gh.includes(phrase));
 const p=db.people.find(p=>p.person_id==='jlu-sunwanchun');assert.equal(p.mentors.length,1);assert.equal(p.mentors[0].name,'朱兴族');
 const n=await render('#/person/'+p.person_id),h=n('#main').innerHTML+n('#profile-content').innerHTML;
 for(const phrase of ['James N Moore','不新增导师','不猜行政树','1999/2004'])assert(h.includes(phrase));
});
test('every explicitly supported teaching role and student-level note is visible on its own course row',async()=>{
 let rowsChecked=0;
 for(const p of mapping.people){
  if(!p.teaching?.length)continue;const n=await render('#/person/'+p.person_id),h=n('#main').innerHTML+n('#profile-content').innerHTML;
  const section=h.split('<h2>公开教学事实</h2>')[1]?.split('</section>')[0]||'';
  for(const t of p.teaching){
   const name=t.name||t.course||(Array.isArray(t.courses)?t.courses.join('、'):null);assert(name,p.person_id+' needs visible teaching title');
   const row=(section.match(/<li>[\s\S]*?<\/li>/g)||[]).find(value=>value.includes(name));assert(row,p.person_id+' '+name);
   if(t.role){assert(row.includes(' · '+t.role));assert(!row.includes('具体教学角色未披露'));}
   if(t.note)assert(row.includes(t.note));rowsChecked++;
  }
 }
 assert.equal(rowsChecked,26);
 const lv=mapping.people.find(p=>p.person_id==='jlu-lvxuanru');assert.equal(lv.teaching.length,2);for(const t of lv.teaching){assert(!t.role);assert(!t.note.includes('来源讲授课程'));}
 for(const id of ['jlu-liwenjun','jlu-wangjuan','jlu-jinlina'])for(const t of mapping.people.find(p=>p.person_id===id).teaching)assert.equal(t.role,'讲授');
});
