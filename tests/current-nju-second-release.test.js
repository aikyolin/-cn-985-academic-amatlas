import {readAtlasFile} from './atlas-test-io.js';
import {createImmutableCohortRenderer} from './immutable-cohort-renderer.js';
import {test} from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {matches,escapeHtml,mentorEvents,mentorOfficialUrl,mentorProfileRoute} from '../site/model.js';
const db=readAtlasFile(new URL('../site/atlas.json',import.meta.url));
const roster=JSON.parse(fs.readFileSync(new URL('../site/rosters.json',import.meta.url)));
const mapping=JSON.parse(fs.readFileSync(new URL('./fixtures/independent-nju11-second-source-mapping.json',import.meta.url)));
const ids=["nju-cuizhiqing", "nju-caijiahe", "nju-chendezhi", "nju-zhuchengjian", "nju-chenxuezhang", "nju-sunleqiang", "nju-huxingliang", "nju-zhouanhua", "nju-caodachen-history", "nju-shiquansheng-history", "nju-baolei-philosophy"];
test('actual NJU second cohort preserves all independently reviewed identities and complete fields',()=>{
 assert.equal(db.people.length,993+mapping.people.length);assert.equal(db.build_id,roster.build_id);assert.deepEqual(mapping.people.map(p=>p.person_id),ids);
 for(const expected of mapping.people){const actual=db.people.find(p=>p.person_id===expected.person_id);assert.deepEqual(actual,expected);assert.equal(actual.data_batch_id,'faculty-batch-nju11-second-independent-20261026');assert(matches(actual,{q:actual.name},db.org_units));assert(matches(actual,{school:'nju',org:actual.department_id},db.org_units));assert(!matches(actual,{school:'lzu'},db.org_units));}
});
const {render}=createImmutableCohortRenderer({db,roster,fixtureId:import.meta.url});
for(const expected of mapping.people)test('actual NJU second profile and lineage preserve '+expected.name,async()=>{
 const nodes=await render('#/person/'+expected.person_id),html=nodes('#main').innerHTML+'\n'+nodes('#profile-content').innerHTML;assert(html.includes(expected.name));assert(html.includes('南京大学'));
 const graph=await render('#/person/'+expected.person_id+'/lineage'),relationHtml=['#main','#profile-content','#mind-stage'].map(k=>graph(k).innerHTML).join('\n');
 for(const mentor of expected.mentors||[]){assert(relationHtml.includes(escapeHtml(mentor.name)));assert(relationHtml.includes(escapeHtml(mentor.type_label||mentor.type)));}
});
test('NJU second non-null research fields are renderable strings',()=>{
 for(const expected of mapping.people){const p=db.people.find(x=>x.person_id===expected.person_id);if(p.research_interests!==undefined&&p.research_interests!==null)assert.equal(typeof p.research_interests,'string',p.person_id);}
});
test('NJU second actual research sidebar displays exact reviewed text and never object stringification',async()=>{
 for(const p of mapping.people){const n=await render('#/person/'+p.person_id),html=n('#profile-content').innerHTML,aside=html.match(/<aside class="profile-info"[\s\S]*?<\/aside>/)?.[0];assert(aside,p.person_id);const text=p.research_interests||'待补录';assert.equal(typeof text,'string');assert(aside.includes('<h3>研究方向</h3><p>'+escapeHtml(text)+'</p>'),p.person_id+' exact research panel');assert(!html.includes('[object Object]'),p.person_id);}
});
test('NJU second reviewed uncertainty text remains visible on each actual profile',async()=>{
 for(const p of mapping.people){const n=await render('#/person/'+p.person_id),html=n('#main').innerHTML+'\n'+n('#profile-content').innerHTML;for(const note of p.unknowns||[])assert(html.includes(escapeHtml(note)),p.person_id+' '+note);}
});

// Independently checked source-specific expectations; dates retain their source types.
const semanticCases={"nju-cuizhiqing": {"phrases": ["退休年月未知", "授位机构及日期未知", "独立历史学硕士资格"], "awards": [null, true], "awardDates": [null, null], "awardYears": [null, null], "mentors": []}, "nju-caijiahe": {"phrases": ["1985是机构任教起点", "“至今”仅属2014年原文", "另未读PDF摘要学校名不同"], "awards": [true, false, false], "awardDates": ["1992", null, null], "awardYears": [1992, null, null], "mentors": []}, "nju-chendezhi": {"phrases": ["1960不是教授晋升时间", "不推为硕士或博士论文导师", "不启用人物关系导航"], "awards": [null, null], "awardDates": [null, null], "awardYears": [null, null], "mentors": ["韩儒林"]}, "nju-zhuchengjian": {"phrases": ["Baudry、Halterman、Kochi", "不计为三位明确个人导师", "明确1996博士授位年"], "awards": [null, true, false, false, false], "awardDates": [null, null, null, null, null], "awardYears": [null, 1996, null, null, null], "mentors": ["钱长涛"]}, "nju-chenxuezhang": {"phrases": ["博士学习终2011-06与北京大学博士后始2011-04重叠", "不认证数学系与学院法律同一", "本人导师未披露"], "awards": [true, true, true, false, false], "awardDates": [null, null, null, null, null], "awardYears": [null, null, null, null, null], "mentors": []}, "nju-sunleqiang": {"phrases": ["法学博士", "2008–2009访问师从特瑞尔·卡弗不作学位论文导师", "0不等于本人没有论文或著作"], "awards": [true, true, true, false], "awardDates": ["2004", "2007", "2010", null], "awardYears": [null, null, null, null], "mentors": ["特瑞尔·卡弗"]}, "nju-baolei-philosophy": {"phrases": ["原2020年12月至今", "不造任职记录", "杨维中仅博士后合作导师"], "awards": [true, true, true, false], "awardDates": [null, null, null, null], "awardYears": [null, null, null, null], "mentors": ["杨维中"]}, "nju-huxingliang": {"phrases": ["历史杭州大学名称不改为现校名", "1988讲师、1992副教授、1997教授", "不推返聘"], "awards": [null, null, null], "awardDates": [null, null, null], "awardYears": [null, null, null], "mentors": []}, "nju-zhouanhua": {"phrases": ["1982/1987/1989为原毕业年", "不将毕业年当授位年", "不认证现任或返聘"], "awards": [true, true, true], "awardDates": [null, null, null], "awardYears": [null, null, null], "mentors": []}, "nju-caodachen-history": {"phrases": ["1997至2002范围", "不拆个别授位年份", "客座/特聘研究员，不改成求学"], "awards": [true, true, false], "awardDates": [null, null, null], "awardYears": [null, null, null], "mentors": []}, "nju-shiquansheng-history": {"phrases": ["退休日期未知", "不等1964年起任教授", "具体课程未披露"], "awards": [null], "awardDates": [null], "awardYears": [null], "mentors": []}};
for(const [id,x] of Object.entries(semanticCases))test('NJU second source semantics '+id,async()=>{
 const p=mapping.people.find(p=>p.person_id===id);assert.deepEqual(p.education.map(e=>e.degree_awarded),x.awards);assert.deepEqual(p.education.map(e=>e.degree_awarded_date),x.awardDates);assert.deepEqual(p.education.map(e=>e.degree_awarded_year),x.awardYears);assert.deepEqual((p.mentors||[]).map(m=>m.name),x.mentors);
 const n=await render('#/person/'+id),html=n('#main').innerHTML+n('#profile-content').innerHTML;for(const term of x.phrases)assert(html.includes(escapeHtml(term)),id+' '+term);
 if(id==='nju-chendezhi'){const m=p.mentors[0];assert.equal(m.type,'academic_guidance_stage_unknown');assert.equal(m.education_event_id,null);assert.equal(m.stage,null);assert.equal(m.include_in_verified_mentor_count,false);assert.equal(m.include_in_mentorship_graph,true);assert.deepEqual(mentorEvents(p,m),[]);assert.equal(mentorOfficialUrl(m),'');assert.equal(mentorProfileRoute(m,db.people),'');const g=await render('#/person/'+id+'/lineage');assert(g('#mind-stage').innerHTML.includes('1条已收录关系'));assert(g('#mind-stage').innerHTML.includes('阶段机构待核实'));assert(g('#profile-content').innerHTML.includes('非学位导师认证'));}
 if(id==='nju-zhuchengjian'){assert.equal(p.education.filter(e=>e.degree_awarded===false).length,3);assert.equal(p.mentors.length,1);}
 if(id==='nju-baolei-philosophy'){assert.equal(p.appointments.length,0);assert.equal(Object.hasOwn(p,'institutional_associations'),false);assert.equal(p.unclassified_professional_events.length,1);assert.equal(p.unclassified_professional_events[0].institution_as_source,'南京大学哲学系（宗教学系）宗教学学科');assert.equal(p.unclassified_professional_events[0].period_as_source,'2020年12月至今');assert.equal(p.unclassified_professional_events[0].role_as_source,null);assert.equal(p.education[0].degree,'哲学学士、法学学士（双学位）');assert.equal(p.mentors[0].type,'postdoctoral_mentor');}
 if(id==='nju-sunleqiang')assert.equal(p.mentors[0].type,'visiting_study_mentor');
});
test('NJU second every education employment work and teaching qualification note is actually visible',async()=>{
 for(const p of mapping.people){const n=await render('#/person/'+p.person_id),html=n('#main').innerHTML+n('#profile-content').innerHTML;for(const key of ['education','appointments','publications','teaching'])for(const item of p[key]||[])if(item.note)assert(html.includes(escapeHtml(item.note)),p.person_id+' '+key+' '+item.note);}
});
