import {test} from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {createHash} from 'node:crypto';
import {stages,matches,mentorEvent,mentorProfileRoute,mentorOfficialUrl,mentorNavigationNotice,schoolStats,escapeHtml,safeUrl} from '../site/model.js';

const read=path=>JSON.parse(fs.readFileSync(new URL(path,import.meta.url)));
const db=read('../data/atlas.json'),rosters=read('../data/rosters.json'),progress=read('../progress/multischool-second-coverage.json');
db.rosters=rosters;
// This release's five reviewed new-person packages, not a suffix/prefix match for later 003 packages.
const BATCHES=new Map([
  ['faculty-batch-zju-ic-002',['zju',3,2,'zju-selected-roster-ic-002']],
  ['faculty-batch-zju-ic-003',['zju',2,3,'zju-selected-roster-ic-003']],
  ['faculty-batch-sjtu-ic-002',['sjtu',5,0,'sjtu-selected-roster-ic-002']],
  ['faculty-batch-tsinghua-ee-002',['thu',5,0,'thu-selected-roster-faculty-batch-tsinghua-ee-002']],
  ['pku-ic-002',['pku',5,0,'pku-selected-roster-pku-ic-002']]
]);
const UPDATE='faculty-update-zju-chengran-001';
// Freeze the second-release scope explicitly; later non-HIT batches must not
// change the audited historical totals below, even when their IDs share a prefix.
const FIRST_PROFILE_BATCHES=new Set(['pku-ic-001','tsinghua-ee-001','faculty-batch-zju-ic-001','faculty-batch-sjtu-ic-001']);
const FIRST_ROSTER_BATCHES=new Set(['pku-selected-roster-pku-ic-001','thu-selected-roster-tsinghua-ee-001','zju-selected-roster-ic-001','sjtu-selected-roster-ic-001']);
const SECOND_RELEASE_PROFILE_BATCHES=new Set([...FIRST_PROFILE_BATCHES,...BATCHES.keys(),UPDATE]);
const SECOND_RELEASE_ROSTER_BATCHES=new Set([...FIRST_ROSTER_BATCHES,...[...BATCHES.values()].map(v=>v[3])]);
function secondReleaseView(current,currentRosters){
  const profile=p=>p.school_id==='hit'||SECOND_RELEASE_PROFILE_BATCHES.has(p.data_batch_id);
  const roster=r=>r.school_id==='hit'||SECOND_RELEASE_ROSTER_BATCHES.has(r.batch_id);
  return {...current,people:current.people.filter(profile),pending_people:current.pending_people.filter(profile),rosters:{...currentRosters,entries:currentRosters.entries.filter(roster),source_observations:currentRosters.source_observations.filter(roster)}};
}
const historical=secondReleaseView(db,rosters);
const fresh=db.people.filter(p=>BATCHES.has(p.data_batch_id)),pending=db.pending_people.filter(p=>BATCHES.has(p.data_batch_id));
const person=id=>{const row=db.people.find(p=>p.person_id===id);assert(row,`Missing established person ${id}`);return row};
const waiting=id=>{const row=db.pending_people.find(p=>p.person_id===id);assert(row,`Missing pending person ${id}`);return row};
const fields=['education','appointments','mentors','publications','sources'];
const counts=rows=>fields.map(k=>rows.reduce((n,p)=>n+(p[k]||[]).length,0));
const canonical=v=>Array.isArray(v)?v.map(canonical):v&&typeof v==='object'?Object.fromEntries(Object.keys(v).sort().map(k=>[k,canonical(v[k])])):v;
const digest=v=>createHash('sha256').update(JSON.stringify(canonical(v))).digest('hex');
const SOURCES=[
  ['faculty-batch-zju-ic-002','1301a2cad0a85d7eee64fb0494b433edb461f774cc94229e9a3c9e8d47ea3ba4','cd04dd4c290230e1022ad0f162a4ad9b6902c103ff29a7fbb70ba2f49a9fd558'],
  ['faculty-batch-zju-ic-003','23f7334f8960f1e9f44f8e7d44fa96f4558fb3ec1edcf3285cd50284e5b1edbc','0da4da3715ccdabd9bffc324bcc5fcb782b053fb3497acb4babeba132c7357a2'],
  ['faculty-batch-sjtu-ic-002','013edd8ad089169921bd7ccec195e8adc94f7f29420c74885d1ae4a652f848e0','e3d9fe283c37be7a9cc87740013fe7e15d218b509c62857d22ab72255fd91ef9'],
  ['faculty-batch-tsinghua-ee-002','1af9dec6300ba4490c6a20d527360c97998418bbb2837eb422a1a1405071fe1f','779dcf18971d701d515abfc01bb1741727bb8b346b682d8c0a579d434ac3d08c'],
  ['pku-ic-002','c13d0057441893604ea10717651c356af6ac469950b3ebc9197a3d3e0d1b10ea','e91917e533da5912e39f0a4205efb5764661a18fd62c2771ac8c601490cd453b'],
  [UPDATE,'408cd959c8cde6b3ef88f89c56a5eb5c269bb71061b7efab15ae887e6ca0ec10','baf2ac64880e711a139f25b58f76a5235bbab0118f1bf877fd661290f9a3c25c']
];

test('second release retains all six exact audited source and independent-review hashes',()=>{
  assert.equal(progress.source_references.length,6);
  assert.equal(progress.baseline_commit,'b0f45a454a70f33bd92fc206e4cba3bb96b7896d');
  assert.equal(progress.coverage_complete,false);assert.equal(progress.fields_complete,false);
  for(const [batch,sha,review] of SOURCES){
    const refs=progress.source_references.filter(r=>r.sha256===sha);assert.equal(refs.length,1,batch);const ref=refs[0];
    assert.equal(ref.sha256,sha);assert.equal(ref.independent_review_sha256,review);
    assert.deepEqual(ref,{sha256:sha,independent_review_sha256:review});
    const record=db.profile_batches.find(b=>b.batch_id===batch);assert(record,batch);
    assert.deepEqual(record.source_files,[{sha256:sha}]);
    assert.equal(record.complete_profiles,0);assert.equal(record.coverage_complete,false);assert.equal(record.fields_complete,false);
  }
});

test('explicit second-release historical view is 296 established plus48 pending and1426 roster records plus1464 observations',()=>{
  assert.deepEqual([historical.people.length,historical.pending_people.length,historical.rosters.entries.length,historical.rosters.source_observations.length],[296,48,1426,1464]);
  assert.equal(new Set([...historical.people,...historical.pending_people].map(p=>p.person_id)).size,344);
  assert.deepEqual(counts(historical.people),[900,1097,123,622,1155]);
  assert.deepEqual([progress.counts.new_people,progress.counts.new_professional_profiles,progress.counts.new_pending_profiles,progress.counts.promoted_existing_pending_profiles,progress.counts.net_professional_profiles_delta,progress.counts.net_pending_profiles_delta,progress.counts.complete_profiles],[25,20,5,1,21,4,0]);
  for(const [sid,ps,qs,rs] of [['hit',257,42,1381],['zju',9,6,15],['thu',10,0,10],['pku',10,0,10],['sjtu',10,0,10]]){
    const stats=schoolStats(historical,sid);assert.deepEqual([stats.people,stats.pending,stats.rosters],[ps,qs,rs]);assert.equal(stats.status,'部分收录');
  }
});

test('current full library has unique identities, actual school statistics and actual roster totals',()=>{
  const people=[...db.people,...db.pending_people],ids=people.map(p=>p.person_id);
  assert(ids.every(id=>typeof id==='string'&&id.length>0));
  assert.equal(new Set(ids).size,people.length);
  const schoolIds=new Set([...db.institutions.map(s=>s.id),...[...people,...db.org_units,...rosters.entries].map(r=>r.school_id)]);
  for(const sid of schoolIds){
    const stats=schoolStats(db,sid),sameSchool=rows=>rows.filter(r=>r.school_id===sid).length;
    assert.equal(stats.people,sameSchool(db.people),`${sid}: established people`);
    assert.equal(stats.pending,sameSchool(db.pending_people),`${sid}: pending people`);
    assert.equal(stats.units,sameSchool(db.org_units),`${sid}: organizational units`);
    assert.equal(stats.rosters,sameSchool(rosters.entries),`${sid}: roster records`);
    assert.equal(stats.published,stats.people>0);
    assert.equal(stats.hasData,Boolean(stats.people||stats.pending||stats.units||stats.rosters));
    assert.equal(stats.status,stats.people?'部分收录':stats.hasData?'仅目录／资料待核':'待收录');
  }
  assert.equal(rosters.totals.record_count,rosters.entries.length);
  assert.equal(rosters.totals.raw_observation_count,rosters.source_observations.length);
  assert.equal(rosters.totals.roster_records,rosters.entries.length);
  assert.equal(rosters.totals.raw_source_observations,rosters.source_observations.length);
  assert.equal(rosters.totals.source_record_grouping_reduction,rosters.source_observations.length-rosters.entries.length);
});

test('current site snapshot matches canonical collection identities and raw-observation totals',()=>{
  const siteDb=read('../site/atlas.json'),siteRosters=read('../site/rosters.json');
  for(const [name,canonicalRows,siteRows,key] of [
    ['people',db.people,siteDb.people,'person_id'],
    ['pending people',db.pending_people,siteDb.pending_people,'person_id'],
    ['roster records',rosters.entries,siteRosters.entries,'id']
  ]){
    assert.equal(siteRows.length,canonicalRows.length,`${name}: current collection count`);
    assert.deepEqual(siteRows.map(r=>r[key]).sort(),canonicalRows.map(r=>r[key]).sort(),`${name}: current collection identities`);
  }
  // The compact site snapshot intentionally omits raw observation payloads.
  assert.equal(siteRosters.totals.record_count,rosters.entries.length);
  assert.equal(siteRosters.totals.roster_records,rosters.entries.length);
  assert.equal(siteRosters.totals.raw_observation_count,rosters.source_observations.length);
  assert.equal(siteRosters.totals.raw_source_observations,rosters.source_observations.length);
});

test('later non-HIT batches do not leak into the explicit second-release historical view',()=>{
  const laterBatch='faculty-batch-zju-ic-002-later',laterRoster='zju-selected-roster-ic-002-later';
  const laterPerson={...fresh[0],person_id:'test-later-person',school_id:'zju',data_batch_id:laterBatch};
  const laterPending={...pending[0],person_id:'test-later-pending',school_id:'zju',data_batch_id:laterBatch};
  const laterEntry={...rosters.entries.find(r=>r.school_id==='zju'),id:'test-later-roster',school_id:'zju',batch_id:laterRoster};
  const laterObservation={...rosters.source_observations.find(r=>r.school_id==='zju'),observation_id:'test-later-observation',record_id:laterEntry.id,school_id:'zju',batch_id:laterRoster};
  const expandedDb={...db,people:[...db.people,laterPerson],pending_people:[...db.pending_people,laterPending]};
  const expandedRosters={...rosters,entries:[...rosters.entries,laterEntry],source_observations:[...rosters.source_observations,laterObservation]};
  assert.equal(expandedDb.people.length,db.people.length+1);assert.equal(expandedDb.pending_people.length,db.pending_people.length+1);
  assert.equal(expandedRosters.entries.length,rosters.entries.length+1);assert.equal(expandedRosters.source_observations.length,rosters.source_observations.length+1);
  assert.deepEqual(secondReleaseView(expandedDb,expandedRosters),historical);
});

test('25 new people remain20 partial professional records and5 pending, separate from the existing-person update',()=>{
  assert.equal(fresh.length,20);assert.equal(pending.length,5);
  assert.deepEqual(counts(fresh),[61,81,8,37,104]);assert.deepEqual(counts(pending),[0,6,0,0,10]);
  for(const [batch,[sid,ps,qs]] of BATCHES){
    assert.equal(fresh.filter(p=>p.data_batch_id===batch).length,ps);
    assert.equal(pending.filter(p=>p.data_batch_id===batch).length,qs);
    for(const p of [...fresh,...pending].filter(p=>p.data_batch_id===batch)){assert.equal(p.school_id,sid);assert.deepEqual(p.campus_ids,[]);assert.equal(p.complete_profile_count_eligible,false)}
  }
  assert(!fresh.some(p=>p.person_id==='zju-chengran'));
  for(const p of fresh){assert.equal(p.profile_status,'partial_professional_source_checked');assert.equal(p.detail_count_eligible,true);assert.equal(p.established_professional_count_eligible,true);assert(p.profile_coverage_label.includes('部分'))}
});

test('25 new selected roster rows remain separate observations rather than verified identity or full coverage',()=>{
  const batchIds=new Set([...BATCHES.values()].map(v=>v[3]));
  const entries=rosters.entries.filter(e=>batchIds.has(e.batch_id));
  assert.equal(entries.length,25);assert.equal(rosters.source_observations.filter(o=>batchIds.has(o.batch_id)).length,25);
  for(const [,[sid,,,batch]] of BATCHES){
    const rows=entries.filter(e=>e.batch_id===batch);assert.equal(rows.length,5);
    assert(rows.every(e=>e.school_id===sid));
  }
  for(const e of entries){assert.equal(e.profile_identity_verified,false);assert.equal(e.verified_person_id,null)}
  const update=db.profile_batches.find(b=>b.batch_id===UPDATE);
  assert.equal(update.people_count,0);assert.equal(update.selected_roster_observations,0);assert.equal(update.promoted_pending_profiles,1);
});

test('main degree filters use45 new confirmed awards, not47 source-level flags or preserved pending evidence',()=>{
  const es=fresh.flatMap(p=>p.education);
  assert.deepEqual([true,false,null].map(v=>es.filter(e=>e.degree_awarded===v).length),[45,10,6]);
  assert(es.filter(e=>e.degree_awarded===true).every(e=>e.event_kind==='degree'));
  const all=historical.people.flatMap(p=>p.education);
  assert.deepEqual([true,false,null].map(v=>all.filter(e=>e.degree_awarded===v).length),[480,164,256]);
  assert.deepEqual(progress.counts.new_batch_source_award_counts,{degree_awarded_true:47,degree_awarded_false:10,degree_awarded_null:7,confirmed_degree_events:33});
  assert.deepEqual(progress.counts.new_pending_preserved_evidence,{education:3,mentors:0,publications:1});
  for(const p of pending){assert.equal(stages(p,'doctor').length,0);assert(!matches(p,{doctor:'overseas'}));assert(!matches(p,{doctor:'unknown'}))}
});

test('Chengran promotion preserves one identity, old index evidence and old sources while counting two direct-source awards once',()=>{
  const p=person('zju-chengran');assert(!db.pending_people.some(x=>x.person_id===p.person_id));
  assert.equal(p.data_batch_id,UPDATE);assert.equal(p.previous_profile_evidence.data_batch_id,'faculty-batch-zju-ic-001');
  assert.equal(p.previous_profile_evidence.profile_status,'profile_details_pending');
  assert.equal(digest(p.biography_evidence),'28c2a7e6e566fb6f6e75bf7be498d723d1edfd8ca9cd070702d0593b632ddd60');
  assert.equal(digest(p.sources.slice(0,2)),'6c03ac29df65c491d7cd27d2018afcd6235d824dc3bb1d51316ff9704c6692f3');
  assert.equal(p.biography_evidence.count_eligible,false);assert.equal(p.biography_evidence_supersession.count_eligible,false);
  assert.equal(p.biography_evidence_supersession.superseded_by_batch_id,UPDATE);
  assert(p.profile_update_history.some(h=>h.batch_id===UPDATE&&h.from_collection==='pending_people'&&h.to_collection==='people'&&h.prior_record_sha256==='fb79ee876f1cac67f80f254258831023b04ef24a08aa7dfa42fcf1cef7ff303e'));
  assert.deepEqual(counts([p]),[2,2,0,1,3]);
  assert.deepEqual(p.education.map(e=>e.event_id),p.biography_evidence.education.map(e=>e.event_id));
  assert(p.biography_evidence.education.every(e=>e.degree_awarded===null&&e.source_id==='chengran-source-2'));
  assert(p.education.every(e=>e.degree_awarded===true&&e.event_kind==='degree'&&e.source_id==='chengran-source-3'));
  assert.equal(stages(p,'bachelor').length,1);assert.equal(stages(p,'doctor').length,1);assert.equal(stages(p,'master').length,0);
  assert.equal(p.publications[0].doi,'10.1088/1674-4926/42/2/023101');assert.equal(p.publications[0].source_id,'chengran-source-3');
  assert.equal(rosters.entries.filter(e=>e.id===p.roster_entry_id).length,1);
  assert.equal(p.complete_profile_count_eligible,false);
});

test('PKU seven direct relationships stay two doctoral and five postdoctoral with exact event identities',()=>{
  const rows=fresh.filter(p=>p.data_batch_id==='pku-ic-002').flatMap(p=>p.mentors.map(m=>[p,m]));
  assert.equal(rows.length,7);
  assert.equal(rows.filter(([,m])=>m.relationship_kind==='doctoral_advisor').length,2);
  assert.equal(rows.filter(([,m])=>m.relationship_kind==='postdoctoral_advisor').length,5);
  assert.deepEqual(rows.map(([p,m])=>[p.person_id,m.name,m.relationship_kind,m.education_event_id]),[
    ['pku-huang-qianqian','王阳元','doctoral_advisor','pku-huang-qianqian-education-2'],
    ['pku-huang-qianqian','黄如','postdoctoral_advisor','pku-huang-qianqian-education-3'],
    ['pku-huang-xiaoxi','Ramamoorthy Ramesh','doctoral_advisor','pku-huang-xiaoxi-education-2'],
    ['pku-huang-xiaoxi','Ramamoorthy Ramesh','postdoctoral_advisor','pku-huang-xiaoxi-education-3'],
    ['pku-huang-xiaoxi','Dan Ralph','postdoctoral_advisor','pku-huang-xiaoxi-education-4'],
    ['pku-huang-xiaoxi','Jie Shan','postdoctoral_advisor','pku-huang-xiaoxi-education-5'],
    ['pku-huang-xiaoxi','Kin Fai Mak','postdoctoral_advisor','pku-huang-xiaoxi-education-5']
  ]);
  for(const [p,m] of rows){
    const event=mentorEvent(p,m);assert.equal(event.event_id,m.education_event_id);
    if(m.relationship_kind==='postdoctoral_advisor'){assert.equal(event.event_kind,'postdoctoral');assert.equal(event.degree_awarded,false)}
    assert(p.sources.some(s=>s.id===m.source_id));assert(m.source_url);assert.equal(m.include_in_mentorship_graph,true);
  }
});

test('PKU guidance and overseas postdocs never turn uncertain study periods into awarded doctorates',()=>{
  for(const id of ['pku-huang-xiaoxi','pku-jia-rundong']){const p=person(id);assert.equal(stages(p,'doctor').length,0);assert(!matches(p,{doctor:'overseas'}));assert(!matches(p,{doctor:'mainland'}))}
  const he=person('pku-he-ming');assert.equal(stages(he,'doctor').length,1);assert(matches(he,{doctor:'mainland'}));assert(!matches(he,{doctor:'overseas'}));
  assert(he.education.some(e=>e.event_kind==='joint_training'&&e.degree_awarded===false));
  assert.equal(mentorEvent(person('pku-huang-xiaoxi'),person('pku-huang-xiaoxi').mentors[0]).degree_awarded,null);
});

function renderMentorCard(p){
  const app=fs.readFileSync(new URL('../site/app.js',import.meta.url),'utf8');
  const labelExpression=app.match(/const statusLabel=s=>([^;]+);/)[1],statusLabel=new Function('s',`return (${labelExpression});`);
  const source=app.match(/function lineage\(p\)\{[\s\S]*?\n(?=function makeMind)/)?.[0];assert(source);
  const elements=new Map(),$=key=>{if(!elements.has(key))elements.set(key,{innerHTML:'',clientWidth:960,dataset:{height:'320'},style:{},addEventListener(){},click(){this.onclick?.()}});return elements.get(key)};
  const link=(url,label,cls='')=>safeUrl(url)?`<a class="${cls}" href="${escapeHtml(safeUrl(url))}">${escapeHtml(label)}</a>`:'';
  const src=(url,label)=>link(url,label,'source-link');
  const render=new Function('db','$','esc','statusLabel','src','mentorProfileRoute','mentorOfficialUrl','mentorNavigationNotice','safeUrl','link','makeMind',`let zoom=1;${app.match(/^const sourceLink=.*$/m)?.[0]||''}return (${source});`)(db,$,escapeHtml,statusLabel,src,mentorProfileRoute,mentorOfficialUrl,mentorNavigationNotice,safeUrl,link,()=>'<svg></svg>');
  render(p);return $('#profile-content').innerHTML;
}

test('SJTU Zhang Jianfu retains indexed role and thesis evidence but both false flags forbid shortcuts',()=>{
  const p=person('sjtu-jizhigang');assert.equal(p.mentors.length,1);const m=p.mentors[0];
  assert.equal(m.name,'张建福');assert.equal(m.relationship_kind,'doctoral_advisor');
  assert.equal(m.employment_status,'official_profile_indexed_current_role');
  assert.equal(m.source_employment_status,'official_profile_indexed_current_role');
  assert.equal(m.navigation_verified,false);assert.equal(m.quick_link_eligible,false);assert.equal(m.person_id,null);
  assert.equal(m.official_url,'https://ic.seu.edu.cn/zjf/main.htm');assert.equal(m.profile_source_url,m.official_url);
  assert.equal(m.source_url,'https://researchonline.ljmu.ac.uk/id/eprint/5975/1/518399.pdf');
  assert.equal(mentorEvent(p,m).event_id,'sjtu-jizhigang-education-3');
  assert.equal(mentorOfficialUrl(m),'');assert.equal(mentorProfileRoute(m,db.people),'');
  const role=p.sources.find(s=>s.id===m.profile_source_id);assert.equal(role.direct_http_status,403);assert.equal(role.retry_after_denial,false);
  assert.equal(role.evidence_status,'official_indexed_profile_read_before_direct_http403');
  assert(m.employment_status_note.includes('退休状态未知'));
  const html=renderMentorCard(p);
  assert(!html.includes('查看导师个人主页'));assert(!html.includes('查看本库个人档案'));
  assert(html.includes('href="'+m.source_url+'"'));assert(html.includes('href="'+m.profile_source_url+'"'));
  assert(html.includes('官方索引列现职，正文未直接核验'));
  assert.equal(mentorOfficialUrl({...m,navigation_verified:true,quick_link_eligible:true}),'','An indexed-role label must not promote employment to active');
  assert(html.includes(escapeHtml(m.employment_status_note)));assert(html.includes('关系证据'));assert(html.includes('简介与任职依据'));
});

test('ZJU five new pending people retain distinct roster-only, header-confirmed and index-only evidence levels',()=>{
  assert.deepEqual(pending.map(p=>p.person_id).sort(),['zju-liyunlong','zju-nidong','zju-songyi','zju-wangtao','zju-zhangda']);
  for(const p of pending){
    assert.equal(p.profile_status,'profile_details_pending');assert.equal(p.detail_count_eligible,false);assert.equal(p.established_professional_count_eligible,false);
    assert.deepEqual(p.education,[]);assert.deepEqual(p.mentors,[]);assert.deepEqual(p.publications,[]);
  }
  for(const id of ['zju-liyunlong','zju-zhangda'])assert(!waiting(id).biography_evidence);
  for(const id of ['zju-songyi','zju-wangtao']){
    const p=waiting(id),e=p.biography_evidence.education[0];assert.equal(p.biography_evidence.count_eligible,false);
    assert.equal(e.degree_awarded,true);assert.equal(e.institution,null);assert.equal(e.region,'unknown');
    assert.equal(p.sources.find(s=>s.id===e.source_id).evidence_status,'official_profile_header_web_read_local_403_stopped');
  }
  const ni=waiting('zju-nidong'),e=ni.biography_evidence.education[0];
  assert.equal(e.degree_awarded,null);assert.equal(e.evidence_level,'official_search_index_only');
  assert.equal(ni.biography_evidence.count_eligible,false);assert.equal(ni.biography_evidence.publications.length,1);assert.deepEqual(ni.publications,[]);
  assert.equal(ni.sources.find(s=>s.id===e.source_id).evidence_status,'official_search_index_only_direct_403_stopped');
});

test('ZJU partial biographies keep unknown award institutions and years instead of inferring from employment',()=>{
  for(const id of ['zju-caozizheng','zju-hanyan']){
    const p=person(id);assert(matches(p,{doctor:'unknown'}));assert(!matches(p,{doctor:'mainland'}));assert(!matches(p,{doctor:'overseas'}));
    const e=stages(p,'doctor')[0];assert.equal(e.institution,null);assert.equal(e.country,null);assert.equal(e.continent_code,'unknown');
  }
  const han=person('zju-hanyan');assert.equal(stages(han,'bachelor').length,0);assert.equal(han.education[0].degree,null);assert.equal(han.education[0].degree_awarded,null);
  const cao=person('zju-caozizheng');assert.equal(cao.own_profile_academic_body_read,false);assert.equal(cao.professional_evidence_body_read,true);
});

test('Tsinghua award geography, missing degrees and historical school names are not replaced by assumptions',()=>{
  const lu=person('thu-lujianhua');assert(matches(lu,{doctor:'hmt'}));assert(!matches(lu,{doctor:'overseas'}));assert(!matches(lu,{doctor:'mainland'}));
  assert.equal(stages(person('thu-guyuantao'),'master').length,0);
  const su=person('thu-suxin');assert.equal(su.education[0].institution,'西南师范大学');assert.equal(su.education[0].institution_985,'unknown');
  for(const e of su.education.slice(1)){assert.equal(e.degree_awarded,true);assert.equal(e.start,null);assert.equal(e.end,null)}
  const niu=person('thu-niuzhisheng');assert.equal(niu.education[0].institution,'北方交通大学');assert.equal(niu.education[0].institution_985,'unknown');
  for(const p of fresh.filter(p=>p.school_id==='thu')){assert.deepEqual(p.mentors,[]);assert.equal(p.education.filter(e=>e.degree_awarded===true).length,p.education.length)}
});

test('second-batch source references and mentor event bindings close on the same person without mutating evidence',()=>{
  for(const p of [...fresh,...pending,person('zju-chengran')]){
    const before=JSON.stringify(p),sourceIds=new Set(p.sources.map(s=>s.id));
    assert.equal(sourceIds.size,p.sources.length);
    const mainIds=p.education.map(e=>e.event_id);assert.equal(new Set(mainIds).size,mainIds.length);
    for(const key of ['education','appointments','mentors','publications'])for(const row of p[key]){
      if(row.source_id)assert(sourceIds.has(row.source_id),`${p.person_id}: ${row.source_id}`);
      if(row.profile_source_id)assert(sourceIds.has(row.profile_source_id));
      for(const id of row.additional_source_ids||[])assert(sourceIds.has(id));
    }
    for(const m of p.mentors)assert.equal(mentorEvent(p,m).event_id,m.education_event_id);
    for(const type of ['bachelor','master','doctor'])stages(p,type);
    assert.equal(JSON.stringify(p),before);
  }
});
