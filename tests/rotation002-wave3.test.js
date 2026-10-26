import {createAtlasFetch} from './atlas-test-io.js';
import {readJSONFile} from './atlas-test-io.js';
import {release25View} from './release-history.js';
// Independent release24 SYSU/SCU consumer regressions. No source fetch, browser,
// build writes, normalizer dependency, or research-folder dependency at runtime.
import {test} from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
const root = process.env.ACADEMIC_ATLAS_TEST_ROOT || path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const {stages,matches,educationStageLabel,mentorOfficialUrl,mentorProfileRoute,mentorEvents,mentorEvent,officialProfileUrl,schoolStats} = await import(pathToFileURL(path.join(root,'site/model.js')));
const {rosterIdentityMatched,rosterStatusLabel,renderRosters} = await import(pathToFileURL(path.join(root,'site/rosters.js')));
const read = name => readJSONFile(path.join(root,name));
const db = release25View(read('data/atlas.json'),'data/atlas.json');
db.rosters = release25View(read('data/rosters.json'),'data/rosters.json');
const EXPECTED_IDS = {"sysu":["sysu-liuzhiwei","sysu-wutao","sysu-caotianzhong"],"scu":["scu-dutian","scu-chenpan","scu-yangjieren"]};
const EXPECTED_COUNTS = {"sysu-liuzhiwei":{"education":3,"appointments":3,"mentors":1,"publications":1,"sources":4,"pending_education_candidates":0,"pending_mentor_candidates":0,"pending_appointment_candidates":4,"pending_professional_fact_candidates":0,"academic_service":0,"honors":0,"research_projects":0,"teaching":0,"research_fields":2,"committee_members":0},"sysu-wutao":{"education":4,"appointments":3,"mentors":1,"publications":1,"sources":5,"pending_education_candidates":0,"pending_mentor_candidates":0,"pending_appointment_candidates":4,"pending_professional_fact_candidates":0,"academic_service":0,"honors":0,"research_projects":0,"teaching":0,"research_fields":3,"committee_members":0},"sysu-caotianzhong":{"education":1,"appointments":2,"mentors":0,"publications":1,"sources":5,"pending_education_candidates":0,"pending_mentor_candidates":0,"pending_appointment_candidates":1,"pending_professional_fact_candidates":0,"academic_service":0,"honors":0,"research_projects":0,"teaching":0,"research_fields":4,"committee_members":0},"scu-dutian":{"education":5,"appointments":2,"mentors":6,"publications":1,"sources":4,"pending_education_candidates":1,"pending_mentor_candidates":0,"pending_appointment_candidates":0,"pending_professional_fact_candidates":0,"academic_service":0,"honors":0,"research_projects":0,"teaching":0,"research_fields":4,"committee_members":0},"scu-chenpan":{"education":5,"appointments":4,"mentors":0,"publications":1,"sources":3,"pending_education_candidates":0,"pending_mentor_candidates":0,"pending_appointment_candidates":1,"pending_professional_fact_candidates":0,"academic_service":0,"honors":0,"research_projects":0,"teaching":0,"research_fields":4,"committee_members":0},"scu-yangjieren":{"education":3,"appointments":3,"mentors":2,"publications":1,"sources":2,"pending_education_candidates":0,"pending_mentor_candidates":0,"pending_appointment_candidates":0,"pending_professional_fact_candidates":0,"academic_service":0,"honors":0,"research_projects":0,"teaching":0,"research_fields":4,"committee_members":0}};
const EXPECTED_FILTERS = {"sysu-liuzhiwei":{"stages":{"bachelor":[],"master":[],"doctor":[]},"ug":{"yes":false,"no":false,"unknown":false,"not_recorded":true},"doctorate":{"mainland":false,"hmt":false,"overseas":false,"unknown":false,"not_recorded":true}},"sysu-wutao":{"stages":{"bachelor":[],"master":[],"doctor":["sysu-wutao-education-3"]},"ug":{"yes":false,"no":false,"unknown":false,"not_recorded":true},"doctorate":{"mainland":true,"hmt":false,"overseas":false,"unknown":false,"not_recorded":false}},"sysu-caotianzhong":{"stages":{"bachelor":[],"master":[],"doctor":[]},"ug":{"yes":false,"no":false,"unknown":false,"not_recorded":true},"doctorate":{"mainland":false,"hmt":false,"overseas":false,"unknown":false,"not_recorded":true}},"scu-dutian":{"stages":{"bachelor":[],"master":[],"doctor":[]},"ug":{"yes":false,"no":false,"unknown":false,"not_recorded":true},"doctorate":{"mainland":false,"hmt":false,"overseas":false,"unknown":false,"not_recorded":true}},"scu-chenpan":{"stages":{"bachelor":[],"master":[],"doctor":[]},"ug":{"yes":false,"no":false,"unknown":false,"not_recorded":true},"doctorate":{"mainland":false,"hmt":false,"overseas":false,"unknown":false,"not_recorded":true}},"scu-yangjieren":{"stages":{"bachelor":[],"master":[],"doctor":[]},"ug":{"yes":false,"no":false,"unknown":false,"not_recorded":true},"doctorate":{"mainland":false,"hmt":false,"overseas":false,"unknown":false,"not_recorded":true}}};
const EXPECTED_MENTORS = {"sysu-liuzhiwei":[{"name":"汤明檖","type":"graduate_supervisor","education_stage":"研究生（直接正文未细分硕士或博士）","start":null,"end":null,"bound_event_ids":["sysu-liuzhiwei-education-2"]}],"sysu-wutao":[{"name":"葛剑雄","type":"doctoral_supervisor","education_stage":"博士","start":null,"end":null,"bound_event_ids":["sysu-wutao-education-3"]}],"sysu-caotianzhong":[],"scu-dutian":[{"name":"Martyn McLachlan","type":"masters_supervisor","education_stage":"硕士（MRes）","start":null,"end":null,"bound_event_ids":["scu-dutian-education-2"]},{"name":"Martin Heeney","type":"masters_supervisor","education_stage":"硕士（MRes）","start":null,"end":null,"bound_event_ids":["scu-dutian-education-2"]},{"name":"Martyn McLachlan","type":"doctoral_co_supervisor","education_stage":"博士","start":null,"end":null,"bound_event_ids":["scu-dutian-education-3"]},{"name":"James Durrant","type":"doctoral_co_supervisor","education_stage":"博士","start":null,"end":null,"bound_event_ids":["scu-dutian-education-3"]},{"name":"Joe Briscoe","type":"postdoctoral_supervisor","education_stage":"博士后","start":null,"end":null,"bound_event_ids":["scu-dutian-education-4"]},{"name":"Christoph Brabec","type":"postdoctoral_supervisor","education_stage":"博士后","start":null,"end":null,"bound_event_ids":["scu-dutian-education-5"]}],"scu-chenpan":[],"scu-yangjieren":[{"name":"傅恒志","type":"postgraduate_supervisor","education_stage":"硕士、博士合并阶段（未细分）","start":null,"end":null,"bound_event_ids":["scu-yangjieren-education-2"]},{"name":"陈瑞润","type":"postgraduate_supervisor","education_stage":"硕士、博士合并阶段（未细分）","start":null,"end":null,"bound_event_ids":["scu-yangjieren-education-2"]}]};
const EXPECTED_FINAL_TOTALS = {"atlas":[555,84,229,39],"exports":111};
const EXPECTED_ROSTER_STATUS = {"sysu":"official_search_index_only","scu":"official_roster_body_read"};
const SOURCE_PACKAGE_SHA256 = {"sysu":"005d3d3f0c33c71b7bc45f2cbf20718e19ff07b5c3abc0ae2eff9bea941787cf","scu":"9847ea52ba380cc5d81bb8a7e5b6353dc33dfe2fd3c036de8dae17edea9a5088"};
const REVIEW_SHA256 = {"sysu":"8483cafd43e013489dfc28ef020e2d37796c82af7db5512058517935df2bf1b1","scu":"1cd89b87e3520869b36438d4c0510939ca2a9c99e501c86b52500120f3554aec"};
const EXPECTED_AWARDS = {"true":1,"null":13,"false":7};
const EXPECTED_MENTOR_TYPES = ["doctoral_co_supervisor","doctoral_supervisor","graduate_supervisor","masters_supervisor","postdoctoral_supervisor","postgraduate_supervisor"];
const ids = Object.values(EXPECTED_IDS).flat();
const person = id => db.people.find(p=>p.person_id===id);
const added = ids.map(person);
const escape = value => String(value).replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;').replaceAll('"','&quot;');
let serial = 0;
const renderFixtures = new WeakMap();
async function fixture(input) {
  if(renderFixtures.has(input))return renderFixtures.get(input);
  const pending=(async()=>{
    const view=structuredClone(input),nodes=new Map(),listeners={};
    view.build_id=view.rosters.build_id='rotation002-wave3-consumer-fixture';view.exports||=[];
    const node=key=>{
      if(!nodes.has(key))nodes.set(key,{innerHTML:'',textContent:'',value:'',style:{},dataset:{height:'320'},clientWidth:960,
        addEventListener(){},click(){this.onclick?.()},scrollIntoView(){},querySelector(selector){return node(selector)}});
      return nodes.get(key);
    };
    const document={querySelector:node,querySelectorAll:()=>[],getElementById:id=>node('#'+id)},location={href:"https://atlas.test/site/index.html",hash:'#/'},window={scrollTo(){},addEventListener(name,fn){listeners[name]=fn}};
    const fetch=createAtlasFetch(view,view.rosters);
    const activate=()=>Object.assign(globalThis,{document,location,window,fetch});activate();
    await import(pathToFileURL(path.join(root,'site/app.js')).href+'?rotation002-wave3='+serial++);
    assert(listeners.hashchange,'Actual app must initialize');
    return {nodes,node,location,listeners,activate};
  })();
  renderFixtures.set(input,pending);return pending;
}
async function render(id,mode='profile',input=db){
  const f=await fixture(input);f.activate();for(const node of f.nodes.values())node.innerHTML='';
  f.location.hash=mode==='directory'?`#/people?school=${id}`:`#/person/${id}${mode==='lineage'?'/lineage':''}`;
  f.listeners.hashchange();
  assert(!f.node('#main').innerHTML.includes('资料暂未加载'));
  return {main:f.node('#main').innerHTML,content:f.node('#profile-content').innerHTML,graph:f.node('#mind-stage').innerHTML,results:f.node('#results').innerHTML};
}

test('release24 adds exactly six SYSU/SCU profiles and no HUST or pending identity',()=>{
  assert.deepEqual([db.people.length,db.pending_people.length,db.org_units.length,db.institutions.length],EXPECTED_FINAL_TOTALS.atlas);
  assert.deepEqual([db.rosters.entries.length,db.rosters.source_observations.length],[1721,1759]);
  assert.deepEqual(db.people.slice(541,547).map(p=>p.person_id),ids);
  assert.deepEqual(db.rosters.entries.slice(1706,1712).map(e=>e.source_person_id),ids);
  assert.deepEqual(db.profile_batches.slice(132,134).map(b=>b.batch_id),['faculty-batch-sysu-rotation-002','faculty-batch-scu-rotation-002']);
  for (const p of added) {
    assert.equal(p.detail_count_eligible,true);assert.equal(p.complete_profile_count_eligible,false);
    assert.equal(p.fields_complete,false);assert.deepEqual(p.campus_ids,[]);assert.equal(p.campus,null);
  }
});

test('original main and candidate collection counts cannot be inflated',()=>{
  for (const p of added) for (const [key,count] of Object.entries(EXPECTED_COUNTS[p.person_id])) assert.equal((p[key]||[]).length,count,p.person_id+'/'+key);
  const awards = added.flatMap(p=>p.education).reduce((out,e)=>(out[String(e.degree_awarded)]++,out),{true:0,null:0,false:0});
  assert.deepEqual(awards,EXPECTED_AWARDS);
});

test('actual education filters preserve independently pinned explicit award membership',()=>{
  for (const p of added) {
    const expected=EXPECTED_FILTERS[p.person_id];
    for (const stage of ['bachelor','master','doctor']) assert.deepEqual(stages(p,stage).map(e=>e.event_id),expected.stages[stage]);
    for (const [key,value] of Object.entries(expected.ug)) assert.equal(matches(p,{ug:key},db.org_units),value,p.person_id+'/'+key);
    for (const [key,value] of Object.entries(expected.doctorate)) assert.equal(matches(p,{doctor:key},db.org_units),value,p.person_id+'/'+key);
  }
});

test('all source-specific adviser types and bindings remain distinct in actual consumers',async()=>{
  const kinds=new Set();
  for (const p of added) {
    const html=await render(p.person_id,'lineage');
    assert.equal(p.mentors.length,EXPECTED_MENTORS[p.person_id].length);
    for (const [i,m] of p.mentors.entries()) {
      const expected=EXPECTED_MENTORS[p.person_id][i];kinds.add(m.type);
      for (const key of ['name','type','education_stage','start','end']) assert.deepEqual(m[key]??null,expected[key]??null,p.person_id+'/'+key);
      assert.deepEqual(mentorEvents(p,m).map(e=>e.event_id),expected.bound_event_ids);
      assert(html.content.includes(escape(m.type_label||m.type)));
      assert(html.graph.includes(escape(m.education_stage)));
      assert.equal(html.graph.split(`aria-label="查看${escape(m.name)}简介"`).length-1,p.mentors.filter(x=>x.name===m.name).length);
      assert.equal(m.include_in_mentorship_graph,true);assert.equal(m.include_in_verified_mentor_count,true);
    }
  }
  assert.deepEqual([...kinds].sort(),[...EXPECTED_MENTOR_TYPES].sort());
});

test('current mentor employment unknown never exposes shortcuts or stored profile routes',async()=>{
  for (const p of added) {
    for (const m of p.mentors) {
      assert.equal(m.employment_status,p.school_id==='sysu'?'not_checked':'not_verified');assert.equal(m.navigation_verified,false);assert.equal(m.quick_link_eligible,false);
      assert.equal(mentorOfficialUrl(m),'');assert.equal(mentorProfileRoute(m,db.people),'');
    }
    assert(!(await render(p.person_id,'lineage')).content.includes('查看导师个人主页'));
  }
});

test('pending candidates cannot change degrees, profiles, lineage graphs or school statistics',async()=>{
  const mutated=structuredClone(db);
  for (const p of mutated.people.filter(p=>ids.includes(p.person_id))) {
    p.pending_education_candidates=[{event_id:'unreviewed-education-sentinel',degree:'博士',event_kind:'degree',degree_awarded:true,region:'overseas',institution:'Unreviewed candidate institute',include_in_education_filters:false}];
    p.pending_mentor_candidates=[{name:'Unreviewed candidate adviser',relationship_kind:'doctoral_advisor',education_event_id:p.education[0]?.event_id,include_in_mentorship_graph:false,include_in_verified_mentor_count:false,quick_link_eligible:false,navigation_verified:false}];
    p.pending_appointment_candidates=[{title:'Unreviewed current professor',current:true,institution:'Unreviewed employment'}];
    p.pending_professional_fact_candidates=[{name:'Unreviewed publication',type:'journal_article'}];
  }
  for (const p of mutated.people.filter(p=>ids.includes(p.person_id))) {
    for (const stage of ['bachelor','master','doctor']) assert.deepEqual(stages(p,stage),stages(person(p.person_id),stage));
    for (const mode of ['profile','lineage']) assert.deepEqual(await render(p.person_id,mode,mutated),await render(p.person_id,mode));
  }
  for (const school of Object.keys(EXPECTED_IDS)) assert.deepEqual(schoolStats(mutated,school),schoolStats(db,school));
});

test('structured teaching service honors and project candidates cannot fabricate study or mentorship',async()=>{
  const mutated=structuredClone(db);
  for (const p of mutated.people.filter(p=>ids.includes(p.person_id))) {
    const original=person(p.person_id);
    for (const key of ['academic_service','honors','research_projects']) p[key]=[{name:'Independent-fact sentinel adviser',degree:'博士',event_kind:'degree',degree_awarded:true,region:'overseas'}];
  }
  for (const p of mutated.people.filter(p=>ids.includes(p.person_id))) {
    const original=person(p.person_id);
    for (const stage of ['bachelor','master','doctor']) assert.deepEqual(stages(p,stage),stages(original,stage));
    assert.deepEqual(p.mentors,original.mentors);
    for (const mode of ['profile','lineage']) assert.deepEqual(await render(p.person_id,mode,mutated),await render(p.person_id,mode));
  }
});

test('three SCU roster identity links do not claim current employment',()=>{
  for (const p of added) {
    if(p.school_id!=='scu')continue;
    const e=db.rosters.entries.find(e=>e.source_person_id===p.person_id),main={innerHTML:''};
    assert.equal(e.profile_identity_verified,true);assert.equal(e.verified_person_id,p.person_id);
    assert.equal(e.name,p.name);assert.equal(e.school_id,p.school_id);assert.equal(e.department_id,p.department_id);
    assert.equal(e.source_evidence_status,EXPECTED_ROSTER_STATUS[p.school_id]);
    assert.equal(e.profile_identity_evidence.reviewed_source_sha256,SOURCE_PACKAGE_SHA256[p.school_id]);
    assert.equal(e.profile_identity_evidence.independent_review_sha256,REVIEW_SHA256[p.school_id]);
    assert.equal(rosterIdentityMatched(db,e),true);assert.equal(rosterStatusLabel(db,e),'身份已关联人物档案（任职状态另核）');
    renderRosters(db,main,e.id,p.school_id);
    assert(main.innerHTML.includes(`#/person/${p.person_id}`));assert(main.innerHTML.includes('任职状态另核'));
  }
});

test('research direction aliases preserve exact original source order in profile and directory',async()=>{
  const directories={};
  for (const school of Object.keys(EXPECTED_IDS)) directories[school]=(await render(school,'directory')).results;
  for (const p of added) {
    const expected=p.research_fields.map(f=>f.name).join('；'),sourceIds=[...new Set(p.research_fields.map(f=>f.source_id))];
    assert(expected);assert.equal(p.research_interests,expected);assert.deepEqual(p.research_interests_source_ids,sourceIds);
    assert.deepEqual(p.professional_field_provenance.research_interests,sourceIds);
    assert.equal(p.research_interests_derivation,'verbatim_original_research_fields_names_in_source_order_for_existing_consumer');
    assert((await render(p.person_id)).content.includes(`<h3>研究方向</h3><p>${escape(expected)}</p>`));
    const row=directories[p.school_id].split('<tr>').find(row=>row.includes(`#/person/${p.person_id}"`));
    assert(row);assert(row.includes(`<small>${escape(expected)}</small>`));assert(!row.includes('研究方向待补录'));
  }
});

test('actual profile lineage and roster renders are nonmutating',async()=>{
  const before=JSON.stringify(db);
  for (const p of added) {
    await render(p.person_id);await render(p.person_id,'lineage');
    const e=db.rosters.entries.find(e=>e.source_person_id===p.person_id),main={innerHTML:''};
    renderRosters(db,main,e.id,p.school_id);assert(main.innerHTML.includes(p.name));
  }
  assert.equal(JSON.stringify(db),before);
});

test('SYSU index-only affiliations and separate profile discoveries never masquerade as verified roster hrefs',async()=>{
  for (const p of added.filter(p=>p.school_id==='sysu')) {
    const e=db.rosters.entries.find(e=>e.source_person_id===p.person_id),main={innerHTML:''};
    assert.equal(p.identity_evidence.official_roster_profile_link_verified,false);
    assert.equal(p.department_basis,'official_index_only_sampling_affiliation_not_current_personnel_verification');
    assert.equal(e.source_evidence_status,'official_search_index_only');assert.equal(e.profile_identity_verified,false);
    assert(!e.verified_person_id);assert.equal(rosterIdentityMatched(db,e),false);
    assert.equal(officialProfileUrl(p),'');assert.equal(p.official_profile_navigation_eligible,false);
    assert.equal(p.current_faculty_status,'not_verified_official_index_only');assert.equal(p.include_in_current_faculty_count,false);
    assert(!p.current_employment);assert(p.sampling_affiliation_label.includes('索引'));
    renderRosters(db,main,e.id,p.school_id);assert(!main.innerHTML.includes(`href="${p.official_url}"`));
    const html=await render(p.person_id);assert(html.content.includes(escape(p.sampling_affiliation_label))||html.main.includes(escape(p.sampling_affiliation_label)));
    assert(!html.main.includes(`href="${p.official_url}"`));
  }
});

test('SYSU nine index-only appointment candidates never become eight historical main roles',()=>{
  const sysu=added.filter(p=>p.school_id==='sysu');
  assert.equal(sysu.flatMap(p=>p.pending_appointment_candidates).length,9);
  assert.equal(sysu.flatMap(p=>p.appointments).length,8);
  for(const p of sysu){
    for(const a of p.appointments){assert.equal(a.current,false);assert.equal(a.status,'historical_source_reported');assert.equal(a.evidence_status,'official_public_body_read')}
    for(const c of p.pending_appointment_candidates){assert.equal(c.current,null);assert.equal(c.include_in_appointment_count,false);assert.equal(c.include_in_verified_appointment_count,false);assert.equal(c.evidence_status,'official_search_index_only')}
  }
  assert.equal(person('sysu-wutao').appointments[0].institution,'中山大学历史学系');
  assert.equal(person('sysu-wutao').appointments[2].as_of,'2022-06-11');assert.equal(person('sysu-wutao').appointments[2].start,null);
});

test('Liu Zhiwei graduate adviser retains an undifferentiated graduate stage in graph and card',async()=>{
  const p=person('sysu-liuzhiwei'),m=p.mentors[0],e=p.education[1],html=await render(p.person_id,'lineage');
  assert.equal(m.name,'汤明檖');assert.equal(m.type,'graduate_supervisor');assert.equal(m.relationship_kind,'graduate_advisor_unspecified_stage');
  assert.equal(m.type_label,'研究生导师（硕博阶段未细分）');assert.equal(e.event_kind,'graduate_study');assert.equal(e.degree,null);assert.equal(e.degree_awarded,null);
  assert.deepEqual(mentorEvents(p,m).map(e=>e.event_id),['sysu-liuzhiwei-education-2']);
  assert(html.graph.includes(escape(m.education_stage)));assert(html.content.includes(m.type_label));
  assert(!html.content.includes('博士导师'));assert(!html.content.includes('硕士导师'));
});

test('Wu Tao lone confirmed doctoral award remains year-only while the postdoc end stays unknown',async()=>{
  const p=person('sysu-wutao'),e=p.education[2],postdoc=p.education[3];
  assert.deepEqual([e.start,e.end,e.degree_awarded,e.degree_awarded_date],['2000','2003',true,'2003']);
  assert.equal(e.degree_award_source_id,'usts-wutao-bio-2015');assert.equal(p.mentors[0].type,'doctoral_supervisor');
  assert.equal(postdoc.event_kind,'postdoctoral_research');assert.equal(postdoc.start,'2003');assert.equal(postdoc.end,null);assert.equal(postdoc.degree_awarded,false);
  assert.equal(p.appointments[0].start,'2005');assert((await render(p.person_id)).content.includes('授位日期：2003 '));
});

test('Cao Tianzhong qualification label 1999 is never an award or graduation date',()=>{
  const p=person('sysu-caotianzhong'),e=p.education[0];assert.equal(e.qualification_label_year,'1999');
  for(const key of ['start','end','degree_awarded','degree_awarded_date'])assert.equal(e[key],null);
  assert.deepEqual(stages(p,'doctor'),[]);assert.equal(matches(p,{doctor:'not_recorded'},db.org_units),true);
});

test('SCU professor category never overwrites Du Tian special researcher title',async()=>{
  const p=person('scu-dutian'),html=await render(p.person_id);
  assert.equal(p.roster_category,'教授');assert.equal(p.listed_role,'特聘研究员');assert.equal(p.appointments[0].title,'特聘研究员');
  assert.equal(p.appointments[0].start,'2025');assert.equal(p.listed_role_basis,'explicit_individual_profile_title');
  assert.notEqual(p.listed_role_source_id,p.roster_category_source_id);assert(html.content.includes('特聘研究员')||html.main.includes('特聘研究员'));
});

test('Du Tian MRes and doctoral co-advisers stay distinct even when a name occurs at both stages',async()=>{
  const p=person('scu-dutian'),html=await render(p.person_id,'lineage');
  assert.equal(p.mentors.length,6);assert.equal(new Set(p.mentors.map(m=>m.name)).size,5);
  assert.deepEqual(p.mentors.slice(0,2).map(m=>[m.name,m.type,m.education_event_id]),[
    ['Martyn McLachlan','masters_supervisor','scu-dutian-education-2'],['Martin Heeney','masters_supervisor','scu-dutian-education-2']]);
  assert.deepEqual(p.mentors.slice(2,4).map(m=>[m.name,m.type,m.education_event_id]),[
    ['Martyn McLachlan','doctoral_co_supervisor','scu-dutian-education-3'],['James Durrant','doctoral_co_supervisor','scu-dutian-education-3']]);
  assert.equal(html.graph.split('aria-label="查看Martyn McLachlan简介"').length-1,2);
  for(const m of p.mentors.slice(0,2))assert(m.type_label.includes('硕士'));
  for(const m of p.mentors.slice(2,4)){assert.equal(m.relationship_kind,'doctoral_co_advisor');assert(m.type_label.includes('博士'));assert(!m.type_label.includes('博士后'))}
  assert.deepEqual([p.education[1].start,p.education[1].end,p.education[1].degree_awarded,p.education[1].degree_awarded_date],['2014','2015',null,null]);
  assert(p.education[1].note.includes('2017'));
});

test('Du Tian postdoctoral supervisors bind non-degree events and never create overseas degree eligibility',async()=>{
  const p=person('scu-dutian'),html=await render(p.person_id,'lineage');
  for(const m of p.mentors.slice(4)){
    assert.equal(m.type,'postdoctoral_supervisor');assert.equal(m.include_in_degree_mentorship_graph,false);
    const events=mentorEvents(p,m);assert.equal(events.length,1);assert.equal(events[0].event_kind,'postdoctoral_research');assert.equal(events[0].degree_awarded,false);
    assert(m.type_label.includes('博士后'));assert(html.content.includes(escape(m.type_label)));
  }
  assert.deepEqual([p.education[3].institution,p.education[3].start,p.education[3].end],['帝国理工学院 & 玛丽女王大学','2021','2021']);
  assert.equal(matches(p,{doctor:'overseas'},db.org_units),false);assert.deepEqual(stages(p,'doctor'),[]);
});

test('Du Tian denied-body PhD candidate cannot transfer explicit award to main event',()=>{
  const p=person('scu-dutian'),c=p.pending_education_candidates[0],e=p.education[2];
  assert.equal(c.candidate_value,true);assert.equal(c.status,'pending_body_verification_access_denied');assert.equal(c.evidence_status,'search_index_only');
  assert.equal(c.include_in_education_filters,false);assert.equal(c.include_in_mentorship_graph,false);assert.equal(c.education_event_id,e.event_id);
  assert.equal(e.degree_awarded,null);assert.equal(e.degree_awarded_date,null);assert.deepEqual(stages(p,'doctor'),[]);
});

test('Yang Jieren combined masters-doctoral event stays unsplit and each supervisor creates exactly one edge',async()=>{
  const p=person('scu-yangjieren'),e=p.education[1],html=await render(p.person_id,'lineage');
  assert.equal(p.education.length,3);assert.equal(e.event_kind,'graduate_study');assert.equal(e.degree,'硕士、博士');assert.equal(e.degree_awarded,null);
  assert.deepEqual([e.start,e.end],['2007-09','2013-07']);assert.equal(p.mentors.length,2);
  for(const m of p.mentors){
    assert.equal(m.type,'postgraduate_supervisor');assert.equal(m.relationship_kind,'postgraduate_advisor');
    assert.equal(m.stage_scope,'combined_masters_doctoral_statement_not_separate_edges');
    assert.equal(m.type_label,'硕博合述导师（未拆分阶段）');assert.deepEqual(mentorEvents(p,m).map(e=>e.event_id),[e.event_id]);
    assert.equal(m.start,null);assert.equal(m.end,null);assert.equal(html.graph.split(`aria-label="查看${m.name}简介"`).length-1,1);
    assert(html.content.includes(m.type_label));assert(html.graph.includes(m.education_stage));
  }
  assert.deepEqual(stages(p,'master'),[]);assert.deepEqual(stages(p,'doctor'),[]);
});

test('Yang Jieren institution start never becomes professor promotion and unknown titles remain null',()=>{
  const p=person('scu-yangjieren');
  assert.equal(p.appointments[0].start,'2020-12');assert.equal(p.appointments[0].title,null);
  assert.equal(p.appointments[1].title,'教授、博士生导师');assert.equal(p.appointments[1].start,null);assert.equal(p.appointments[2].title,null);
  assert.equal(p.education[0].degree,null);assert.equal(p.education[0].education_level,'本科');assert.equal(p.education[2].event_kind,'academic_visit');assert.equal(p.education[2].degree_awarded,false);
});

test('Chen Pan contradictory transition dates stay null and open historical postdoc is not current employment',async()=>{
  const p=person('scu-chenpan'),c=p.pending_appointment_candidates[0];
  assert.equal(p.appointments[1].start,null);assert.equal(p.appointments[3].end,null);assert.equal(p.appointments[3].current,false);
  assert.deepEqual(c.source_claims.map(s=>s.scu_special_researcher_start),['2022','2023-03']);assert.equal(c.include_in_appointment_filters,false);
  assert.equal(p.education[4].end,null);assert.equal(p.education[4].current_status,'historical_open_ended_source_not_current_verified');assert.deepEqual(p.mentors,[]);
  const html=await render(p.person_id);assert(html.content.includes(escape(p.appointments[1].note)));assert(html.content.includes(escape(p.appointments[3].note)));
});

test('three books and three articles remain selected source metadata with literal angle-bracket titles safely rendered',async()=>{
  assert.deepEqual(added.map(p=>p.publications[0].type),['book','book','book','journal_article','journal_article','journal_article']);
  for(const p of added){const pub=p.publications[0];assert.equal(pub.individual_article_link_verified,false);assert.equal(pub.link_status,'official_publication_list_only');assert.equal(pub.doi,null);assert.equal(pub.url,pub.source_url);assert((await render(p.person_id)).content.includes(escape(pub.title)))}
  assert.equal(person('sysu-liuzhiwei').publications[0].year,null);assert.equal(person('sysu-liuzhiwei').publications[0].venue,null);
  const html=(await render('scu-yangjieren')).content;assert(html.includes('&lt;a&gt;'));assert(html.includes('&lt;c+a&gt;'));
});

