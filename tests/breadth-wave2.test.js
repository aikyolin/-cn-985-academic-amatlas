import {readJSONFile,createAtlasFetch} from './atlas-test-io.js';
import {test} from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {execFileSync} from 'node:child_process';
import {fileURLToPath} from 'node:url';
import {UNIVERSITIES} from '../site/universities.js';
import {stages,matches,mentorEvent,mentorOfficialUrl,mentorProfileRoute,officialProfileUrl,schoolStats,schoolCampuses,normalizeSchoolFilters,escapeHtml} from '../site/model.js';

const read=path=>readJSONFile(new URL(path,import.meta.url));
const db=read('../data/atlas.json'),rosters=read('../data/rosters.json'),progress=read('../progress/breadth-wave2-coverage.json'),site=read('../site/atlas.json'),siteRosters=read('../site/rosters.json');
db.rosters=rosters;db.exports=site.exports;const original=JSON.stringify(db);
const FIELDS=['education','appointments','mentors','committee_members','publications','sources','research_collaborators','pending_mentor_candidates','pending_mentors','project_guidance','professional_research_advisors'];
const counts=ps=>Object.fromEntries(FIELDS.map(k=>[k,ps.reduce((n,p)=>n+(p[k]||[]).length,0)]));
const awards=ps=>[true,false,null].map(v=>ps.flatMap(p=>p.education||[]).filter(e=>e.degree_awarded===v).length);
// Audited first packages only; later batches must not change this sample or cap live school totals.
const BATCHES=[
 ['bit',[9,9,0,0,10],[2,1,6],'5b0e3fe0eb1626d79ba542008f66643c850d2f33c0385f632b3b4a19b9d33b76','497c2cd2665552debc7d15fb591b046cbd509384b3a0bf8d996881131484c5ac'],
 ['bnu',[7,11,1,3,10],[2,1,4],'397e1a41d32d82f23f48ab1041a670b23324b96867ffcfdc4e0b30b3c31a92df','f26844b1c45488b3a75a3b444fecac9fc3dcc4a761e47e09e868ed77319ff56b'],
 ['cau',[6,3,0,2,8],[1,3,2],'739b1dcdf0014c983d7dc51e811426b231c153c48268b03890115a3dbec4bf22','1ac02b94f440c9eacd53b197ee1d109a2017be69771efabe9d1a45389f2d9b21'],
 ['muc',[5,10,2,2,11],[1,0,4],'266e5aa1193112debae40393646e1f391e08686cc18a3fbc7504cac7ffc06993','52c9090269856fa7b09806c8d88c79d82e724c43534381556294c9aff693f2a9'],
 ['nku',[4,10,0,2,11],[4,0,0],'85f6d10035ac4fa431456b8a6cf8fc897030fd10c5bfcca1db944e6f18414fb0','e983d35d2f8f31dedeed5787f05e2a2c48cffd58a60434d5a22881e839284133'],
 ['dlut',[10,7,0,2,11],[0,1,9],'5a549e6d733736785d089156f0f8cfe4e0a345c35448897fa9790b934f223fed','d8bfa0139a30d8523dedfd9c7304eb187e44fe58fc0a82e9fd03a0b5d9656124'],
 ['tju',[8,17,0,4,14],[3,1,4],'d5930bba30e6f7b808ad9e64d9e4f50096a4ac1ee8afce0dc25461daa596c57f','b53065c5a98327c112d2ae5d004523cbc5c44ad3577a86370830d72a0a47f654'],
 ['jlu',[12,10,1,2,10],[3,3,6],'92a47a38133eef620192419023288b6581ad4cab5082557ccc0971b60a6edaa2','033b8c88c53733d0a13e8ac9c27b18fdcd4955ab430b14388792481e013a69f0'],
 ['tongji',[2,6,0,1,7],[0,0,2],'63210a56397abcf247e177ee3a66db8b319add431320cb0c18c5f1d996dad89c','0c7599647554a850c98995f4a3dce964eefdd3307b98b548bc4de8f01fc93bc9'],
 ['ruc',[9,11,0,4,11],[1,2,6],'62e8875af172a20a8d5dc6c0fea05194bee888c7bd9061042c55042ff9f3a8b0','9142ec8efa1ac33b9253e64f8d6420eb9747d0000ca5d2d8f8c2187a79733b04'],
 ['neu',[12,10,0,3,12],[6,3,3],'54ab535e6e9248ffe40132719d2951fb578b9d293e138e99032dc74b6452b1aa','31516abd4a59728922d0807b2f5cef9662b430a08dfad6e27ede41b94fb256e1']
].map(([sid,fields,awards,sha,review])=>({sid,fields,awards,sha,review,batch:`faculty-batch-${sid}-first-001`,roster:`${sid}-selected-roster-first-001`}));
const batchIds=new Set(BATCHES.map(b=>b.batch)),rosterIds=new Set(BATCHES.map(b=>b.roster));
const fresh=db.people.filter(p=>batchIds.has(p.data_batch_id)),pending=db.pending_people.filter(p=>batchIds.has(p.data_batch_id));
const person=id=>{const p=fresh.find(p=>p.person_id===id);assert(p,`Missing second-wave person ${id}`);return p};
const source=(p,id)=>{const s=p.sources.find(s=>s.id===id);assert(s,`${p.person_id}: missing source ${id}`);return s};

test('eleven immutable source and independent-review hashes match the public ledger and profile/roster batches',()=>{
 assert.equal(progress.baseline_commit,'484fd39b303c182aab1fbf407992d4e3d62d3c9c');assert.equal(progress.source_references.length,11);assert.equal(progress.coverage_complete,false);assert.equal(progress.fields_complete,false);assert(progress.scope.includes('不代表全校全院或全部字段完整'));
 for(const b of BATCHES){const refs=progress.source_references.filter(s=>s.sha256===b.sha);assert.equal(refs.length,1,b.batch);const ref=refs[0];assert.equal(ref.sha256,b.sha);assert.deepEqual(ref,{sha256:b.sha,independent_review_sha256:b.review});assert.equal(ref.independent_review_sha256,b.review);
  for(const batch of [db.profile_batches.find(x=>x.batch_id===b.batch),rosters.batches.find(x=>x.batch_id===b.roster)]){assert(batch);assert.equal(batch.school_id,b.sid);assert.deepEqual(batch.source_files,[{sha256:b.sha}]);assert.equal(batch.coverage_complete,false)}
  const batch=db.profile_batches.find(x=>x.batch_id===b.batch);assert.equal(batch.complete_profiles,0);assert.equal(batch.fields_complete,false);
 }
});

test('eleven exact batches add33 identities as32 partial profiles plus1 pending with per-batch counts unchanged',()=>{
 assert.deepEqual([fresh.length,pending.length,new Set([...fresh,...pending].map(p=>p.person_id)).size],[32,1,33]);assert.deepEqual(pending.map(p=>p.person_id),['tongji-binyi']);
 assert.deepEqual([progress.counts.new_schools,progress.counts.new_organization_nodes,progress.counts.new_campuses,progress.counts.source_people,progress.counts.new_professional_profiles,progress.counts.new_pending_profiles],[11,19,0,33,32,1]);
 assert.deepEqual(counts(fresh),progress.counts.effective_global_collection_delta);assert.deepEqual(counts(pending),progress.counts.pending_main_collections);
 for(const b of BATCHES){const ps=fresh.filter(p=>p.data_batch_id===b.batch),qs=pending.filter(p=>p.data_batch_id===b.batch);assert.deepEqual([ps.length,qs.length],b.sid==='tongji'?[2,1]:[3,0]);assert.deepEqual(['education','appointments','mentors','publications','sources'].map(k=>counts(ps)[k]),b.fields);assert.deepEqual(awards(ps),b.awards);for(const p of [...ps,...qs]){assert.equal(p.school_id,b.sid);assert.deepEqual(p.campus_ids,[]);assert.equal(p.fields_complete,false);assert.equal(p.complete_profile_count_eligible,false)}}
 for(const p of fresh){assert.equal(p.profile_status,'partial_professional_source_checked');assert.equal(p.detail_count_eligible,true);assert.equal(p.established_professional_count_eligible,true);assert(p.profile_coverage_label.includes('部分'))}
});

test('23 awards,46 unknown and15 nondegree events stay distinct, including the explicit integrated-study normalization',()=>{
 assert.deepEqual(awards(fresh),[23,15,46]);assert.deepEqual(progress.counts.effective_degree_counts,{degree_awarded_true:23,degree_awarded_false:15,degree_awarded_null:46,confirmed_degree_events:23});
 assert.deepEqual(progress.counts.source_degree_counts,{degree_awarded_true:23,degree_awarded_false:15,degree_awarded_null:46,confirmed_degree_events:22});
 assert.deepEqual(progress.counts.normalized_event_kind_changes,[{person_id:'muc-chenbo',event_id:'muc-chenbo-education-2',source_event_kind:'integrated_masters_doctoral_study',event_kind:'degree',degree_awarded:true}]);
 assert(fresh.flatMap(p=>p.education).filter(e=>e.degree_awarded===true).every(e=>e.event_kind==='degree'));
 assert.equal(progress.counts.source_collections.mentors,5);assert.equal(counts(fresh).mentors,4);assert.equal(counts(fresh).professional_research_advisors,1);assert.equal(counts(fresh).research_collaborators,0);
});

test('historical20-school projection is368 plus52 while current totals and categories remain data-derived',()=>{
 const h=progress.counts.projection;assert.deepEqual([h.published_schools,h.professional_records,h.pending_records,h.organization_nodes,h.roster_totals.record_count,h.roster_totals.raw_observation_count],[20,368,52,109,1502,1540]);assert.deepEqual([h.roster_totals.category_count,h.roster_totals.batch_category_count,h.roster_totals.coverage_unit_count],[100,111,118]);
 const all=[...db.people,...db.pending_people];assert.equal(new Set(all.map(p=>p.person_id)).size,all.length);
 for(const s of db.institutions){const stats=schoolStats(db,s.id);assert.equal(stats.people,db.people.filter(p=>p.school_id===s.id).length);assert.equal(stats.pending,db.pending_people.filter(p=>p.school_id===s.id).length);assert.equal(stats.rosters,rosters.entries.filter(r=>r.school_id===s.id).length)}
 assert.equal(rosters.totals.record_count,rosters.entries.length);assert.equal(rosters.totals.raw_observation_count,rosters.source_observations.length);assert.equal(rosters.totals.category_count,new Set(rosters.coverage.map(c=>JSON.stringify([c.organization_id,c.category]))).size);assert.equal(rosters.totals.batch_category_count,new Set(rosters.coverage.map(c=>JSON.stringify([c.batch_id??null,c.organization_id,c.category]))).size);assert.equal(rosters.totals.coverage_unit_count,rosters.coverage.length);
});

test('33 roster entries and13 coverage rows are selected observations, not complete or verified-person joins',()=>{
 const entries=rosters.entries.filter(e=>rosterIds.has(e.batch_id)),obs=rosters.source_observations.filter(e=>rosterIds.has(e.batch_id)),coverage=rosters.coverage.filter(e=>rosterIds.has(e.batch_id));assert.deepEqual([entries.length,obs.length,coverage.length],[33,33,13]);
 for(const b of BATCHES){assert.equal(entries.filter(e=>e.batch_id===b.roster).length,3);assert.equal(obs.filter(e=>e.batch_id===b.roster).length,3);const rows=coverage.filter(c=>c.batch_id===b.roster);assert.equal(rows.reduce((n,c)=>n+c.selected_observation_count,0),3);for(const c of rows){assert.equal(c.count_scope,'selected_subset_only');assert.equal(c.all_visible_entries_captured,false);assert.equal(c.coverage_complete,false);assert.equal(c.school_id,b.sid)}}
 for(const e of entries){assert.equal(e.profile_identity_verified,false);assert.equal(e.verified_person_id,null);const p=[...fresh,...pending].find(p=>p.roster_entry_id===e.id);assert(p);assert.equal(e.school_id,p.school_id);assert.equal(e.organization_id,p.department_id);assert.equal(e.campus_id,null);const built=siteRosters.entries.find(r=>r.id===e.id);assert(built);assert.equal(built.verified_person_id,null)}
});

let serial=0;
async function app(hash='#/'){
 const d=structuredClone(db);d.build_id='breadth-wave2-read-only';d.rosters.build_id=d.build_id;const nodes=new Map(),listeners={},node=k=>{if(!nodes.has(k))nodes.set(k,{innerHTML:'',textContent:'',value:'',style:{},events:{},dataset:{height:'320'},clientWidth:960,querySelector:node,addEventListener(t,f){this.events[t]=f},click(){this.onclick?.()}});return nodes.get(k)};
 globalThis.document={querySelector:node,querySelectorAll:()=>[],getElementById:id=>node('#'+id)};globalThis.location={href:"https://atlas.test/site/index.html",hash};globalThis.window={scrollTo(){},addEventListener(t,f){listeners[t]=f}};globalThis.fetch=createAtlasFetch(d,d.rosters);await import('../site/app.js?breadth-wave2-real='+serial++);assert(!node('#main').innerHTML.includes('资料暂未加载'));return {node,navigate(hash){location.hash=hash;listeners.hashchange()}};
}

test('national school cards and no-campus school navigation stay dynamic beyond the20-school release',async()=>{
 const ui=await app(),published=UNIVERSITIES.filter(u=>schoolStats(db,u.id).published).length,directory=UNIVERSITIES.filter(u=>schoolStats(db,u.id).hasData&&!schoolStats(db,u.id).published).length;assert.equal(UNIVERSITIES.length,39);assert(ui.node('#main').innerHTML.includes(`目前${published}所学校有部分人物资料`));assert(ui.node('#main').innerHTML.includes(`其余${39-published-directory}所待收录`));assert.equal((ui.node('#school-grid').innerHTML.match(/class="school-card /g)||[]).length,39);
 for(const b of BATCHES){ui.navigate('#/school/'+b.sid);assert(ui.node('#main').innerHTML.includes(db.institutions.find(s=>s.id===b.sid).official_name));assert(!ui.node('#sidebar').innerHTML.includes('#/campus/harbin'));if(!schoolCampuses(db,b.sid).length){assert(ui.node('#main').innerHTML.includes('本批资料未单列校区归属'));assert(!ui.node('#sidebar').innerHTML.includes('campus-nav'))}assert.deepEqual(normalizeSchoolFilters(db,{school:b.sid,campus:'harbin',org:'hit-aerospace'}),{school:b.sid,campus:'',org:''})}
});

test('Nankai peer colleges and NEU child departments keep distinct people, school labels and export links',async()=>{
 const expected={'nku-cyber':['nku-chensen'],'nku-cs':['nku-chengmingming','nku-chengrenhong'],'neu-cse-cs':['neu-yuge','neu-wangdaling'],'neu-cse-communication-electronics':['neu-yuyao']},ui=await app();
 assert.equal(db.org_units.find(u=>u.id==='nku-cyber').parent_id,'nku');assert.equal(db.org_units.find(u=>u.id==='nku-cs').parent_id,'nku');
 for(const [dept,ids] of Object.entries(expected)){const sid=dept.split('-')[0],selected=fresh.filter(p=>p.department_id===dept);assert.deepEqual(selected.map(p=>p.person_id).sort(),[...ids].sort());ui.navigate('#/org/'+dept);assert(ui.node('#excel').innerHTML.includes(`exports/${dept}.xlsx`));for(const id of ids)assert(ui.node('#results').innerHTML.includes(`#/person/${id}`));for(const p of fresh.filter(p=>p.department_id!==dept))assert(!ui.node('#results').innerHTML.includes(`#/person/${p.person_id}`));for(const id of ids){ui.navigate('#/person/'+id);assert(ui.node('#main').innerHTML.includes(`href="#/school/${sid}"`));assert(ui.node('#main').innerHTML.includes(`href="#/org/${dept}"`));assert(ui.node('#main').innerHTML.includes('校区未单列／待核实'))}}
 assert.equal(db.org_units.find(u=>u.id==='neu-cse-cs').parent_id,'neu-cse');assert.equal(db.org_units.find(u=>u.id==='neu-cse-communication-electronics').parent_id,'neu-cse');
 for(const sid of ['nku','neu']){ui.navigate('#/rosters?school='+sid);for(const p of fresh.filter(p=>p.school_id===sid))assert(ui.node('#roster-results').innerHTML.includes(escapeHtml(p.name)));for(const p of fresh.filter(p=>p.school_id!==sid))assert(!ui.node('#roster-results').innerHTML.includes(p.roster_entry_id))}
});

test('Chen Bo integrated study produces one explicitly awarded doctorate, not a fabricated masters or undergraduate award',()=>{
 const p=person('muc-chenbo');assert.equal(p.education.length,2);assert.deepEqual(p.education.map(e=>e.degree_awarded),[null,true]);const e=p.education[1];assert.equal(e.event_id,'muc-chenbo-education-2');assert.equal(e.degree,'博士');assert.equal(e.event_kind,'degree');assert.equal(e.source_event_kind,'integrated_masters_doctoral_study');assert.equal(e.awarding_institution,'中国科学院大学');assert.equal(e.institution,'中国科学院软件研究所');assert(e.normalization_note.includes('不另造硕士'));assert.equal(stages(p,'doctor').length,1);assert.equal(stages(p,'master').length,0);assert.equal(stages(p,'bachelor').length,0);assert(matches(p,{doctor:'mainland'}));assert(!matches(p,{master:'mainland'}));assert.equal(source(p,e.source_id).url,e.source_url);
});

test('MUC undergraduate guidance and JLU joint doctoral training retain their exact roles without confirming degrees',()=>{
 const p=person('muc-chenyubo');assert.deepEqual(p.mentors.map(m=>m.relationship_kind),['undergraduate_advisor','doctoral_advisor']);assert.deepEqual(p.education.map(e=>e.degree_awarded),[null,null]);for(const m of p.mentors){assert.equal(mentorEvent(p,m).degree_awarded,null);assert.equal(source(p,m.source_id).url,m.source_url);assert.equal(mentorOfficialUrl(m),m.official_url)}assert.equal(stages(p,'doctor').length,0);assert.equal(stages(p,'bachelor').length,0);assert.equal(p.mentors[0].type_label,'本科导师（非博士指导）');
 const q=person('jlu-baitian'),m=q.mentors[0],e=mentorEvent(q,m);assert.equal(m.relationship_kind,'joint_doctoral_training_advisor');assert.equal(m.education_event_id,'jlu-baitian-education-4');assert.equal(e.event_kind,'joint_doctoral_training');assert.equal(e.degree_awarded,false);assert.equal(e.institution,'罗格斯大学');assert.equal(q.education[2].degree_awarded,null);assert.equal(q.education[2].awarding_institution,null);assert.equal(stages(q,'doctor').length,0);assert(!matches(q,{doctor:'overseas'}));assert(!matches(q,{continent:'north_america'}));assert(m.type_label.includes('非境外授位证明'));
 assert.deepEqual(progress.counts.direct_guidance_types,{doctoral_advisor:2,undergraduate_advisor:1,joint_doctoral_training_advisor:1});
});

test('Chen Sen explicit Yang Liu occupational guidance stays independent with no education or main mentor graph',async()=>{
 const p=person('nku-chensen');assert.deepEqual(p.education,[]);assert.deepEqual(p.mentors,[]);assert.equal((p.research_collaborators||[]).length,0);assert.equal(p.professional_research_advisors.length,1);const c=p.professional_research_advisors[0];assert.equal(c.name,'Yang Liu（刘杨）');assert.equal(c.type,'职业科研合作导师');assert.equal(c.relationship_kind,'professional_research_advisor');assert.equal(c.education_event_id,null);assert.equal(c.start,null);assert.equal(c.end,null);assert.equal(c.source_include_in_mentorship_graph,true);assert.equal(c.include_in_mentorship_graph,false);assert.equal(c.include_in_degree_mentorship_graph,false);assert.equal(c.include_in_verified_mentor_count,false);assert.equal(c.include_in_verified_professional_guidance_count,true);assert.equal(c.source_collection,'mentors');assert.equal(c.source_collection_index,0);assert.equal(source(p,c.source_id).url,c.source_url);assert.equal(source(p,c.profile_source_id).url,c.profile_source_url);assert.equal(mentorOfficialUrl(c),'https://personal.ntu.edu.sg/yangliu/');assert.equal(mentorProfileRoute(c,db.people),'');
 const ui=await app('#/person/'+p.person_id),html=ui.node('#profile-content').innerHTML.match(/<section class="info-panel professional-guidance">[\s\S]*?<\/section>/)?.[0];assert(html);for(const key of ['name','type','education_stage','description','scope_label'])assert(html.includes(escapeHtml(c[key])),key);assert(html.includes('已核职业指导：1 条'));assert(html.includes('查看指导者个人主页'));assert(!html.includes('非导师认定'));ui.navigate('#/person/'+p.person_id+'/lineage');assert(ui.node('#mind-stage').innerHTML.includes('0条已收录关系'));assert(!ui.node('#mind-stage').innerHTML.includes('Yang Liu'));assert.equal(stages(p,'doctor').length,0);
});

test('Tongji Bin Yi remains pending despite a readable sparse page, without merging a same-name doctorate',()=>{
 const p=pending[0];assert.equal(p.person_id,'tongji-binyi');assert.equal(p.profile_status,'profile_details_pending');assert.equal(p.detail_count_eligible,false);assert.equal(p.established_professional_count_eligible,false);assert.equal(p.complete_profile_count_eligible,false);assert.deepEqual(p.education,[]);assert.deepEqual(p.mentors,[]);assert.deepEqual(p.publications,[]);assert.equal(p.appointments.length,1);assert.equal(p.appointments[0].title,'研究员');assert(p.unknowns.some(s=>s.includes('同名')&&s.includes('不据')));assert.equal(source(p,'binyi-source-3').evidence_status,'official_profile_public_body_read');assert.equal(stages(p,'doctor').length,0);assert(!matches(p,{doctor:'unknown'}));assert(matches(p,{doctor:'not_recorded'}));assert(!db.people.some(x=>x.person_id===p.person_id));
});

test('CAU unidentified/timed-out and RUC403 profiles retain alternative evidence but never masquerade as available personal homepages',async()=>{
 for(const id of ['cau-zhangpan','cau-lishan','ruc-chengxusen']){const p=person(id);assert.equal(p.official_profile_navigation_eligible,false);assert.equal(p.own_profile_academic_body_read,false);assert.equal(p.professional_evidence_body_read,true);assert.equal(officialProfileUrl(p),'');assert.equal(p.official_profile_availability,id==='cau-zhangpan'?'not_identified':'unavailable');const html=(await app('#/person/'+id)).node('#main').innerHTML;assert(!html.includes('学校官方主页'));for(const s of p.alternative_professional_sources){assert.equal(source(p,s.source_id).url,s.url);assert(html.includes(escapeHtml(s.title)));assert(html.includes(escapeHtml(s.url)))}const e=rosters.entries.find(e=>e.id===p.roster_entry_id);assert.equal(e.profile_identity_verified,false);assert.equal(e.verified_person_id,null)}
 const z=person('cau-zhangpan');assert.equal(z.official_url_kind,'official_institutional_news_not_individual_profile');assert.equal(z.official_url,z.alternative_professional_sources[0].url);assert.equal(z.pending_mentor_candidates.length,2);for(const c of z.pending_mentor_candidates){assert.equal(c.include_in_mentorship_graph,false);assert.equal(c.include_in_verified_mentor_count,false);assert.equal(c.quick_link_eligible,false)}assert.deepEqual(z.mentors,[]);assert.equal(stages(z,'doctor').length,0);
 const r=person('ruc-chengxusen');assert(r.unknowns.some(s=>s.includes('403后已停止')));assert.equal(stages(r,'doctor').length,1);assert(matches(r,{doctor:'overseas',continent:'europe'}));assert.equal(stages(r,'doctor')[0].source_url,r.alternative_professional_sources[0].url);
});

test('NEU roster index evidence is distinct from readable personal biographies and never becomes a direct directory link',async()=>{
 for(const p of fresh.filter(p=>p.school_id==='neu')){const e=rosters.entries.find(e=>e.id===p.roster_entry_id);assert.equal(e.official_profile_url,null);assert.equal(e.profile_candidate_url,p.official_url);assert.equal(e.profile_link_basis,'independent_candidate_evidence_not_a_verified_roster_link');assert.equal(e.source_evidence_status,'official_roster_search_index_read');assert.equal(e.profile_identity_verified,false);assert.equal(e.verified_person_id,null);assert(e.selection_basis.includes('不声称名录直链已核'));const index=p.sources.find(s=>s.evidence_status==='official_roster_search_index_read'),body=p.sources.find(s=>s.evidence_status==='official_profile_public_body_read');assert(index);assert(body);assert.notEqual(index.url,body.url);const html=(await app('#/person/'+p.person_id)).node('#profile-content').innerHTML;assert(html.includes(index.evidence_status_label));assert(html.includes(body.evidence_status_label))}
 assert.deepEqual(progress.counts.source_counts_missing_but_independently_recomputed,['neu']);
});

let exported;
function tables(){if(exported)return exported;const code=`import json,sys,copy\nfrom unittest import mock\nsys.path.insert(0,'scripts')\nimport build,build_rosters\nfrom atlas_storage import load_atlas\nd=load_atlas('data/atlas.json'); r=json.load(open('data/rosters.json')); before=copy.deepcopy(d); rb=copy.deepcopy(r)\nbatches=set(${JSON.stringify(BATCHES.map(b=>b.batch))})\nfresh=[p for p in d['people'] if p.get('data_batch_id') in batches]\nwith mock.patch.object(build,'Workbook',side_effect=AssertionError('No XLSX')),mock.patch.object(build,'build',side_effect=AssertionError('No build')),mock.patch.object(build_rosters,'build_rosters',side_effect=AssertionError('No roster build')):\n build.validate(d); build_rosters.validate_rosters(r,d)\n subset=copy.deepcopy(d); subset['people']=fresh\n out={'selected_manifest':build.department_exports(subset),'manifest':build.department_exports(d),'tables':{dept:dict(build.department_tables([p for p in fresh if p['department_id']==dept],d['updated_at'],d['institutions'])) for dept in sorted({p['department_id'] for p in fresh})}}\nassert d==before and r==rb\nprint(json.dumps(out,ensure_ascii=False))`;exported=JSON.parse(execFileSync('python',['-B','-c',code],{cwd:fileURLToPath(new URL('..',import.meta.url)),encoding:'utf8'}));return exported}

test('thirteen selected department exports keep peer-unit boundaries and exclude pending records; live manifest counts stay dynamic',()=>{
 const out=tables();assert.equal(out.selected_manifest.length,13);assert.equal(out.selected_manifest.reduce((n,e)=>n+e.people_count,0),32);const expected={'nku-cs':2,'nku-cyber':1,'neu-cse-cs':2,'neu-cse-communication-electronics':1,'tongji-cs':2};for(const [dept,count] of Object.entries(expected))assert.equal(out.selected_manifest.find(e=>e.department_id===dept).people_count,count);
 for(const selected of out.selected_manifest){const live=out.manifest.find(e=>e.department_id===selected.department_id),snapshot=site.exports.find(e=>e.department_id===selected.department_id);assert.deepEqual(snapshot,live);assert.equal(live.people_count,db.people.filter(p=>p.department_id===live.department_id&&p.school_id===live.school_id).length);const t=out.tables[selected.department_id],ps=fresh.filter(p=>p.department_id===selected.department_id);assert.equal(t['总览'].length,ps.length+1);assert.deepEqual(t['总览'].slice(1).map(r=>r[0]).sort(),ps.map(p=>p.name).sort());for(const rows of Object.values(t))for(const row of rows.slice(1))assert.deepEqual(row.slice(-2),[selected.school_id,db.institutions.find(s=>s.id===selected.school_id).official_name]);assert(!t['总览'].slice(1).some(r=>r[0]==='宾燚'))}
});

test('real occupational export preserves original facts in its separate row and unavailable-profile exports retain alternatives',()=>{
 const t=tables().tables,c=person('nku-chensen').professional_research_advisors[0],rows=t['nku-cyber']['导师'];assert.equal(rows.length,2);const row=rows[1];assert.equal(row[1],c.name);assert.equal(row[2],'职业科研指导（非学位）');assert.equal(row[3],c.education_stage);assert.equal(row[4],c.description);for(const key of ['type','relationship_kind','scope_label'])assert(row[6].includes(c[key]));assert.equal(row[7],c.official_url);assert.equal(row[8],c.source_url);assert.equal(row[9],c.profile_source_url);assert(!row[6].includes('指导起止：'));assert.equal(t['nku-cyber']['经历'].slice(1).filter(r=>r[1]==='degree').length,0);
 assert.equal(Object.values(t).reduce((n,x)=>n+x['导师'].length-1,0),5);assert.equal(counts(fresh).mentors,4);
 for(const id of ['cau-zhangpan','cau-lishan','ruc-chengxusen']){const p=person(id),r=t[p.department_id]['总览'].find(r=>r[0]===p.name);assert.equal(r[3],'');for(const s of p.alternative_professional_sources)assert(r[8].includes(s.url));if(p.official_profile_availability_label)assert.equal(r[7],p.official_profile_availability_label)}
});

test('second-wave read-only checks leave all canonical data and evidence unchanged in memory',()=>assert.equal(JSON.stringify(db),original));
