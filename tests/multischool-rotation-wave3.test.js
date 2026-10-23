import {test} from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {educationStageLabel,stages,mentorOfficialUrl,mentorEvents,officialProfileUrl} from '../site/model.js';
import {rosterProfileLinks,rosterIdentityMatched,rosterStatusLabel,renderRosters} from '../site/rosters.js';
const db=JSON.parse(fs.readFileSync(new URL('../data/atlas.json',import.meta.url)));db.rosters=JSON.parse(fs.readFileSync(new URL('../data/rosters.json',import.meta.url)));
const p=id=>[...db.people,...db.pending_people].find(p=>p.person_id===id),r=id=>db.rosters.entries.find(e=>e.source_person_id===id);
const schoolIds=['cqu','lzu','nwpu','nwsuaf','scu','scut','sysu','uestc','xjtu'];
const added=[...db.people,...db.pending_people].filter(p=>schoolIds.some(s=>p.data_batch_id===`faculty-batch-${s}-rotation-001`));
let serial=0;
async function app(id,mode='profile'){const view=structuredClone(db);view.build_id=view.rosters.build_id='rotation-wave3-render-fixture';const nodes=new Map(),node=k=>{if(!nodes.has(k))nodes.set(k,{innerHTML:'',textContent:'',value:'',style:{},events:{},dataset:{height:'320'},clientWidth:960,addEventListener(t,f){this.events[t]=f},click(){this.onclick?.()}});return nodes.get(k)};globalThis.document={querySelector:node,querySelectorAll:()=>[],getElementById:id=>node('#'+id)};globalThis.location={hash:'#/person/'+id+(mode==='lineage'?'/lineage':'')};globalThis.window={scrollTo(){},addEventListener(){}};globalThis.fetch=async path=>({ok:true,json:async()=>structuredClone(String(path).startsWith('atlas.json')?view:view.rosters)});await import('../site/app.js?rotation-third-wave='+serial++);assert(!node('#main').innerHTML.includes('资料暂未加载'),node('#main').innerHTML);return node}

test('nine new selected batches have25 partial profiles and2 pending, not full-school coverage',()=>{
 assert.equal(added.length,27);assert.equal(added.filter(p=>p.detail_count_eligible).length,25);assert.equal(db.institutions.length,39);
 for(const id of schoolIds){const batch=db.profile_batches.find(b=>b.batch_id===`faculty-batch-${id}-rotation-001`);assert.equal(batch.people_count,3);assert.equal(batch.coverage_complete,false);assert.equal(batch.fields_complete,false)}
});
test('unknown-nature Columbia education renders unknown, never a degree or visit conclusion',async()=>{
 const person=p('cqu-gongqu'),e=person.education[3];assert.equal(e.event_kind,'education_background');assert.equal(e.degree_awarded,null);assert.equal(e.degree,null);assert.equal(educationStageLabel(e),'教育背景（层次与性质未核实）');assert.equal(stages(person,'doctor').length,0);const node=await app(person.person_id);assert(node('#profile-content').innerHTML.includes('教育背景（层次与性质未核实）'));
});
test('all degree filters count only19 explicitly awarded new events',()=>{
 const counts=added.flatMap(p=>p.education).reduce((c,e)=>(c[e.degree_awarded===true?'yes':e.degree_awarded===false?'no':'unknown']++,c),{yes:0,no:0,unknown:0});assert.deepEqual(counts,{yes:19,no:42,unknown:41});
 for(const person of added)for(const type of ['bachelor','master','doctor'])for(const e of stages(person,type)){assert.equal(e.degree_awarded,true);assert.equal(e.event_kind,'degree')}
});
test('index-only Gu identity stays pending while Liang matched sparse identity is distinct',()=>{
 assert.equal(p('sysu-gulinyan').profile_status,'roster_identity_pending');assert.equal(rosterIdentityMatched(db,r('sysu-gulinyan')),false);assert.equal(rosterStatusLabel(db,r('sysu-gulinyan')),'档案待建，身份待核对');
 assert.equal(p('scu-lianggemeng').profile_status,'profile_details_pending');assert.equal(rosterIdentityMatched(db,r('scu-lianggemeng')),true);
 for(const id of ['sysu-gulinyan','scu-lianggemeng']){assert(!db.people.some(p=>p.person_id===id));assert.equal(p(id).mentors.length,0);assert.equal(p(id).education.length,0);assert.equal(p(id).publications.length,0)}
});
test('all eight blocked or nonpersonal pages suppress personal homepage shortcuts including rosters',()=>{
 const unavailable=added.filter(p=>p.navigation_verified===false);assert.equal(unavailable.length,8);
 for(const person of unavailable){assert.equal(officialProfileUrl(person),'');const entry=r(person.person_id);assert(!rosterProfileLinks(db,entry).includes('href="'+entry.official_profile_url+'"'));assert.equal(entry.official_profile_navigation_eligible,false)}
});
test('UESTC research news and visiting-speaker biography render accurate alternatives, not homepages',async()=>{
 for(const id of ['uestc-jonas-kahn','uestc-kongefang']){const person=p(id),node=await app(id),html=node('#main').innerHTML;assert.equal(officialProfileUrl(person),'');assert(!html.includes('学校官方主页'));assert(html.includes(person.alternative_professional_sources[0].title));assert(html.includes('非个人主页'));assert(!r(id).official_profile_url);assert(!r(id).profile_candidate_url)}
});
test('uncertain active status is not rescued merely by a readable mentor webpage',()=>{
 for(const [id,name]of [['nwpu-baixueli','郑斯宁'],['scut-chenyingshan','易法槐']]){const mentor=p(id).mentors.find(m=>m.name===name);assert.equal(mentor.navigation_verified,true);assert.equal(mentor.quick_link_eligible,false);assert.equal(mentorOfficialUrl(mentor),'');assert.equal(mentor.source_employment_status,'official_profile_listed_retirement_not_disclosed')}
});
test('mixed Purdue emeritus and explicit current other-employer status retains usable evidence and safe shortcut',async()=>{
 const person=p('uestc-guyiqi'),m=person.mentors[0];assert.equal(m.source_employment_status,'current_position_at_another_institution_explicit');assert.equal(m.employment_status,'active_officially_listed');assert.equal(mentorOfficialUrl(m),m.official_url);assert(m.description.includes('荣休'));assert(m.description.includes('东方理工'));const node=await app(person.person_id,'lineage');assert(node('#profile-content').innerHTML.includes('东方理工'));
});
test('retired and emeritus guidance retains biographies without active shortcuts',()=>{
 const mentors=added.flatMap(p=>p.mentors);assert.equal(mentors.filter(m=>m.quick_link_eligible).length,8);
 for(const m of mentors.filter(m=>['retired','emeritus','retirement_reported_official_index'].includes(m.source_employment_status))){assert.equal(mentorOfficialUrl(m),'');assert.equal(m.quick_link_eligible,false);assert(m.description)}
});
test('bachelor thesis and postdoctoral co-guidance remain distinct stages and labels',async()=>{
 const person=p('uestc-guyiqi'),m=person.mentors[1];assert.equal(m.relationship_kind,'undergraduate_thesis_advisor');assert.equal(mentorEvents(person,m).length,1);assert.equal(mentorEvents(person,m)[0].degree_awarded,null);assert(m.type_label.includes('本科毕业论文'));assert(m.type_label.includes('不据此认定学士授位'));
 for(const id of ['scut-chenbocong','scut-chenyingshan']){const person=p(id),m=person.mentors.find(m=>m.relationship_kind==='postdoctoral_co_advisor');assert(m);assert.equal(mentorEvents(person,m)[0].degree_awarded,false);assert.equal(m.start,null);assert.equal(m.end,null);const node=await app(id,'lineage');assert(node('#profile-content').innerHTML.includes('博士后共同指导'))}
});
test('center organization stays school-rooted while independent math-school appointment is retained',()=>{
 const o=db.org_units.find(o=>o.id==='uestc-applied-math-center');assert.equal(o.parent_id,'uestc');assert.equal(o.type,'research_center');for(const person of added.filter(p=>p.school_id==='uestc')){assert.equal(person.department_id,o.id);assert(person.appointments.some(a=>a.institution.includes('数学科学学院')));assert.equal(person.campus_ids.length,0)}
});
test('selected publications retain chapter, dissertation, conference and source-link limits',()=>{
 const pubs=added.flatMap(p=>p.publications);assert.equal(pubs.length,37);for(const q of pubs){assert(q.type_label);assert(q.link_status_label)}assert.equal(pubs.filter(q=>q.type==='book_chapter').length,1);assert.equal(pubs.filter(q=>q.type==='conference_paper').length,1);assert.equal(pubs.filter(q=>['doctoral_thesis','doctoral_dissertation'].includes(q.type)).length,3)
});
test('SCU and SYSU pending routes render roster evidence without a fabricated profile',async()=>{
 for(const id of ['sysu-gulinyan','scu-lianggemeng']){const node=await app(id),html=node('#main').innerHTML;assert(html.includes(p(id).name));assert(html.includes('尚未建立人物档案'));assert(!html.includes('进入已核实身份的人物档案'))}
});
