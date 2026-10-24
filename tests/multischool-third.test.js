import {test} from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {execFileSync} from 'node:child_process';
import {fileURLToPath} from 'node:url';
import {stages,matches,mentorEvent,mentorProfileRoute,mentorOfficialUrl,schoolStats,escapeHtml} from '../site/model.js';

const read=path=>JSON.parse(fs.readFileSync(new URL(path,import.meta.url)));
const db=read('../data/atlas.json'),rosters=read('../data/rosters.json'),progress=read('../progress/multischool-third-coverage.json');
db.rosters=rosters;
const original=JSON.stringify(db);
const FIELDS=['education','appointments','mentors','committee_members','publications','sources','research_collaborators','pending_mentor_candidates','pending_mentors','project_guidance'];
const counts=rows=>Object.fromEntries(FIELDS.map(k=>[k,rows.reduce((n,p)=>n+(p[k]||[]).length,0)]));
const awards=rows=>{const es=rows.flatMap(p=>p.education||[]);return [true,false,null].map(v=>es.filter(e=>e.degree_awarded===v).length)};
// Exact audited package IDs, never a prefix match that admits a later batch.
const BATCHES=new Map([
  ['faculty-batch-tsinghua-ee-003',['thu',5,1,'thu-selected-roster-faculty-batch-tsinghua-ee-003',[12,23,1,5,16],[12,0,0]]],
  ['faculty-batch-sjtu-ic-003',['sjtu',4,1,'sjtu-selected-roster-ic-003',[8,13,0,3,16],[8,0,0]]],
  ['faculty-batch-pku-ic-003',['pku',5,0,'pku-selected-roster-ic-003',[16,15,0,3,11],[13,2,1]]],
  ['faculty-batch-pku-ic-004',['pku',5,0,'pku-selected-roster-ic-004',[18,18,0,7,14],[3,5,10]]],
  ['faculty-batch-zju-ic-004',['zju',4,1,'zju-selected-roster-ic-004',[10,11,7,2,22],[5,3,2]]],
  ['faculty-batch-sjtu-ic-004',['sjtu',5,0,'sjtu-selected-roster-ic-004',[17,17,0,11,16],[3,4,10]]]
]);
const PREVIOUS_PROFILES=['pku-ic-001','tsinghua-ee-001','faculty-batch-zju-ic-001','faculty-batch-sjtu-ic-001','faculty-batch-zju-ic-002','faculty-batch-zju-ic-003','faculty-batch-sjtu-ic-002','faculty-batch-tsinghua-ee-002','pku-ic-002','faculty-update-zju-chengran-001'];
const PREVIOUS_ROSTERS=['pku-selected-roster-pku-ic-001','thu-selected-roster-tsinghua-ee-001','zju-selected-roster-ic-001','sjtu-selected-roster-ic-001','zju-selected-roster-ic-002','zju-selected-roster-ic-003','sjtu-selected-roster-ic-002','thu-selected-roster-faculty-batch-tsinghua-ee-002','pku-selected-roster-pku-ic-002'];
const RELEASE_PROFILES=new Set([...PREVIOUS_PROFILES,...BATCHES.keys()]);
const RELEASE_ROSTERS=new Set([...PREVIOUS_ROSTERS,...[...BATCHES.values()].map(v=>v[3])]);
const inRelease=p=>p.school_id==='hit'||RELEASE_PROFILES.has(p.data_batch_id);
const inRosterRelease=r=>r.school_id==='hit'||RELEASE_ROSTERS.has(r.batch_id);
const historical={...db,people:db.people.filter(inRelease),pending_people:db.pending_people.filter(inRelease),rosters:{...rosters,entries:rosters.entries.filter(inRosterRelease),source_observations:rosters.source_observations.filter(inRosterRelease)}};
const fresh=db.people.filter(p=>BATCHES.has(p.data_batch_id)),pending=db.pending_people.filter(p=>BATCHES.has(p.data_batch_id));
const person=id=>{const p=db.people.find(p=>p.person_id===id);assert(p,`Missing established person ${id}`);return p};
const waiting=id=>{const p=db.pending_people.find(p=>p.person_id===id);assert(p,`Missing pending person ${id}`);return p};
const source=(p,id)=>{const s=p.sources.find(s=>s.id===id);assert(s,`${p.person_id}: missing source ${id}`);return s};
const SOURCES=[
  ['faculty-batch-tsinghua-ee-003','66f78d53e12ca574d907d25dc165d79b27a62da8f3dde4f609fb3d59a1d9d9ad','5aba78837d275b02b755aac58d28da09353fa6dd1d5cfc97bea6471dff3418d4'],
  ['faculty-batch-sjtu-ic-003','6741c909ec141c5041959c2d229432b61bfe2ac4a71e22accfb92b475b8a49cc','f1990080336652cf54f8c1d963b03390658e82642460a232328b437ce11a6586'],
  ['faculty-batch-pku-ic-003','2455556896789759390c11ac7f70f3dcca8059428e8d761c21ee0ee1237df4ae','253795715fdbe5439f2b8f9ef4b69d06cbbd12661073560eb974ff8af04f696b'],
  ['faculty-batch-pku-ic-004','b7b152b77387ef33321add9ea44e08f8c88d5b5480b92cd64fb23d3a7f38bb98','5a0b4a7c375c00252669a581ef0bea8c81f5c5c194d8c2ee18c6103dc4708199'],
  ['faculty-batch-zju-ic-004','e8483887653d17a99688e118d6f124f417aabcea731108cb41ddf9af63318d3d','afcdcb7fcd2f4dbcccc320a37c2c22298f3dd8a84ae8503a51cd4795d4fa1eb0'],
  ['faculty-batch-sjtu-ic-004','6ec048b191cefb1a60966735209962d5ffa888f4dab4bc4688b4f6cd283b1e08','5e3325bad9dce91189c035af50c3a89757bda937908f0b6be20334d95fcf0171']
];

test('third release keeps six immutable source and independent-review hashes and incomplete coverage',()=>{
  assert.equal(progress.baseline_commit,'1fb625112ac7031b88f8f3e0c30ffacb3ead7342');
  assert.equal(progress.source_references.length,6);assert.equal(progress.coverage_complete,false);assert.equal(progress.fields_complete,false);
  for(const [batch,sha,review] of SOURCES){
    const refs=progress.source_references.filter(s=>s.sha256===sha);assert.equal(refs.length,1,batch);const ref=refs[0];
    assert.equal(ref.sha256,sha);assert.equal(ref.independent_review_sha256,review);assert.deepEqual(ref,{sha256:sha,independent_review_sha256:review});
    const profileBatch=db.profile_batches.find(b=>b.batch_id===batch);assert(profileBatch,batch);
    assert.deepEqual(profileBatch.source_files,[{sha256:sha}]);
    assert.equal(profileBatch.complete_profiles,0);assert.equal(profileBatch.coverage_complete,false);assert.equal(profileBatch.fields_complete,false);
    const rosterBatch=rosters.batches.find(b=>b.batch_id===BATCHES.get(batch)[3]);assert(rosterBatch);
    assert.deepEqual(rosterBatch.source_files,[{sha256:sha}]);assert.equal(rosterBatch.coverage_complete,false);
  }
});

test('six selected packages add31 identities as28 partial professional profiles plus3 pending, with exact per-batch fields',()=>{
  assert.deepEqual([fresh.length,pending.length,new Set([...fresh,...pending].map(p=>p.person_id)).size],[28,3,31]);
  assert.deepEqual([progress.counts.new_people,progress.counts.new_professional_profiles,progress.counts.new_pending_profiles,progress.counts.complete_profiles],[31,28,3,0]);
  assert.deepEqual(counts(fresh),progress.counts.effective_global_collection_delta);
  assert.deepEqual(counts(pending),progress.counts.new_pending_main_collections);
  for(const [batch,[sid,ps,qs,,expectedFields,expectedAwards]] of BATCHES){
    const rows=fresh.filter(p=>p.data_batch_id===batch),wait=pending.filter(p=>p.data_batch_id===batch);
    assert.deepEqual([rows.length,wait.length],[ps,qs],batch);
    assert.deepEqual(['education','appointments','mentors','publications','sources'].map(k=>counts(rows)[k]),expectedFields,batch);
    assert.deepEqual(awards(rows),expectedAwards,batch);
    for(const p of [...rows,...wait]){assert.equal(p.school_id,sid);assert.deepEqual(p.campus_ids,[]);assert.equal(p.complete_profile_count_eligible,false);assert.equal(p.fields_complete,false)}
  }
  for(const p of fresh){assert.equal(p.profile_status,'partial_professional_source_checked');assert.equal(p.detail_count_eligible,true);assert.equal(p.established_professional_count_eligible,true);assert(p.profile_coverage_label.includes('部分'))}
  assert.deepEqual(pending.map(p=>p.person_id).sort(),['sjtu-liuting','thu-xuxibin','zju-renkun']);
});

test('explicit third-release history is324 plus51 and1457 roster records plus1495 observations, without a future school cap',()=>{
  const h=historical;
  assert.deepEqual([h.people.length,h.pending_people.length,h.rosters.entries.length,h.rosters.source_observations.length],[324,51,1457,1495]);
  assert.equal(new Set([...h.people,...h.pending_people].map(p=>p.person_id)).size,375);
  assert.deepEqual(counts(h.people),progress.counts.projection.collections);assert.deepEqual(awards(h.people),[524,178,279]);
  assert.deepEqual([progress.counts.projection.professional_records,progress.counts.projection.pending_records],[324,51]);
  for(const [sid,ps,qs,rs] of [['hit',257,42,1381],['thu',15,1,16],['pku',20,0,20],['zju',13,7,20],['sjtu',19,1,20]]){
    const stats=schoolStats(h,sid);assert.deepEqual([stats.people,stats.pending,stats.rosters],[ps,qs,rs]);assert.equal(stats.status,'部分收录');
  }
  const all=[...db.people,...db.pending_people];assert.equal(new Set(all.map(p=>p.person_id)).size,all.length);
  for(const sid of new Set([...db.institutions.map(s=>s.id),...all.map(p=>p.school_id)])){
    const stats=schoolStats(db,sid),same=rows=>rows.filter(p=>p.school_id===sid).length;
    assert.equal(stats.people,same(db.people));assert.equal(stats.pending,same(db.pending_people));assert.equal(stats.rosters,same(rosters.entries));
    assert.equal(stats.status,stats.people?'部分收录':stats.hasData?'仅目录／资料待核':'待收录');
  }
});

test('31 selected roster records retain31 independent observations and7 incomplete coverage rows, not verified person joins',()=>{
  const batchIds=new Set([...BATCHES.values()].map(v=>v[3]));
  const entries=rosters.entries.filter(e=>batchIds.has(e.batch_id)),observations=rosters.source_observations.filter(o=>batchIds.has(o.batch_id)),coverage=rosters.coverage.filter(c=>batchIds.has(c.batch_id));
  assert.deepEqual([entries.length,observations.length,coverage.length],[31,31,7]);
  assert.deepEqual([progress.counts.new_roster_records,progress.counts.new_source_observations,progress.counts.new_coverage_rows],[31,31,7]);
  for(const [,[sid,ps,qs,batch]] of BATCHES){
    const rows=entries.filter(e=>e.batch_id===batch);assert.equal(rows.length,ps+qs);assert(rows.every(e=>e.school_id===sid));
    assert.equal(observations.filter(o=>o.batch_id===batch).length,ps+qs);
    const saved=rosters.batches.find(b=>b.batch_id===batch);assert.equal(saved.record_count,ps+qs);assert.equal(saved.count_scope,'selected_subset_only');
  }
  for(const e of entries){assert.equal(e.profile_identity_verified,false);assert.equal(e.verified_person_id,null)}
  for(const c of coverage){assert.equal(c.coverage_complete,false);assert.equal(c.all_visible_entries_captured,false);assert.equal(c.count_scope,'selected_subset_only')}
  const thu=coverage.filter(c=>c.school_id==='thu');assert.equal(thu.length,2);assert.equal(thu.reduce((n,c)=>n+c.selected_observation_count,0),6);
});

test('coverage keeps83 distinct organization-category pairs separate from94 batch categories and101 source rows',()=>{
  const coverage=rosters.coverage.filter(inRosterRelease),pair=c=>JSON.stringify([c.organization_id,c.category]);
  assert.equal(coverage.length,101);assert.equal(new Set(coverage.map(pair)).size,83);
  assert.equal(new Set(coverage.map(c=>JSON.stringify([c.batch_id??null,c.organization_id,c.category]))).size,94);
  const totals=progress.counts.projection.roster_totals;
  assert.deepEqual([totals.category_count,totals.unique_organization_category_pairs,totals.batch_category_count,totals.coverage_unit_count],[83,83,94,101]);
  assert.equal(totals.category_count_basis,'unique_organization_category_pairs');assert.equal(totals.not_unique_people_count,true);assert.equal(totals.current_employment_count_verified,false);
  assert.equal(rosters.totals.category_count,new Set(rosters.coverage.map(pair)).size);
  assert.equal(rosters.totals.batch_category_count,new Set(rosters.coverage.map(c=>JSON.stringify([c.batch_id??null,c.organization_id,c.category]))).size);
  assert.equal(rosters.totals.coverage_unit_count,rosters.coverage.length);
  assert.equal(rosters.totals.record_count,rosters.entries.length);assert.equal(rosters.totals.raw_observation_count,rosters.source_observations.length);
});

test('44 main confirmed awards exclude the45th source-level fact retained only as sparse pending evidence',()=>{
  assert.deepEqual(awards(fresh),[44,14,23]);
  assert.deepEqual(progress.counts.source_degree_counts,{degree_awarded_true:45,degree_awarded_false:14,degree_awarded_null:23,confirmed_degree_events:45});
  assert.deepEqual(progress.counts.effective_degree_counts,{degree_awarded_true:44,degree_awarded_false:14,degree_awarded_null:23,confirmed_degree_events:44});
  assert.deepEqual(progress.counts.new_pending_preserved_evidence,{education:1,mentors:0,publications:0});
  assert(fresh.flatMap(p=>p.education).filter(e=>e.degree_awarded===true).every(e=>e.event_kind==='degree'));
  for(const p of pending){assert.deepEqual(p.education,[]);assert.deepEqual(p.mentors,[]);assert.deepEqual(p.publications,[]);assert.equal(p.detail_count_eligible,false);assert.equal(stages(p,'doctor').length,0);assert(!matches(p,{doctor:'unknown'}));assert(matches(p,{doctor:'not_recorded'}))}
});

let serial=0;
async function app(id,mode='profile'){
  const d=structuredClone(db);d.build_id='third-regression-read-only';d.rosters.build_id=d.build_id;
  const nodes=new Map(),listeners={};
  const node=key=>{if(!nodes.has(key))nodes.set(key,{innerHTML:'',textContent:'',value:'',style:{},events:{},dataset:{height:'320'},clientWidth:960,addEventListener(type,fn){this.events[type]=fn},click(){this.onclick?.()}});return nodes.get(key)};
  globalThis.document={querySelector:node,querySelectorAll:()=>[],getElementById:id=>node('#'+id)};
  globalThis.location={hash:`#/person/${id}${mode==='lineage'?'/lineage':''}`};globalThis.window={scrollTo(){},addEventListener(type,fn){listeners[type]=fn}};
  globalThis.fetch=async path=>({ok:true,json:async()=>structuredClone(String(path).startsWith('atlas.json')?d:d.rosters)});
  await import('../site/app.js?third-real-regression='+serial++);
  assert(!node('#main').innerHTML.includes('资料暂未加载'));
  return {node,navigate(hash){location.hash=hash;listeners.hashchange()}};
}
const projectSection=ui=>ui.node('#profile-content').innerHTML.match(/<section class="info-panel project-guidance">[\s\S]*?<\/section>/)?.[0]||'';

test('Tao Xiaoming reuses existing Lu Jianhua identity and exactly the doctoral event, with verified active navigation',async()=>{
  const p=person('thu-taoxiaoming');assert.equal(p.mentors.length,1);const m=p.mentors[0];
  assert.equal(m.name,'陆建华');assert.equal(m.person_id,'thu-lujianhua');assert.equal(person(m.person_id).school_id,'thu');
  assert.equal(db.people.filter(p=>p.person_id===m.person_id).length,1);assert(!fresh.some(p=>p.person_id===m.person_id));
  assert.equal(m.person_reference_basis,'independent_review_confirmed_existing_same_school_person_entity');
  assert.equal(m.relationship_kind,'doctoral_advisor');assert.equal(m.education_event_id,'thu-taoxiaoming-education-2');assert.equal(mentorEvent(p,m),p.education[1]);
  assert.equal(m.start,null);assert.equal(m.end,null);assert.equal(m.navigation_verified,true);assert.equal(m.quick_link_eligible,true);
  assert.equal(mentorProfileRoute(m,db.people),'#/person/thu-lujianhua');assert.equal(mentorOfficialUrl(m),'https://www.tsinghua.edu.cn/info/1167/93854.htm');
  assert.equal(source(p,m.source_id).url,m.source_url);assert.equal(source(p,m.profile_source_id).url,m.profile_source_url);
  const ui=await app(p.person_id,'lineage'),html=ui.node('#profile-content').innerHTML;
  assert(html.includes('href="#/person/thu-lujianhua"'));assert(html.includes('查看导师个人主页'));assert(ui.node('#mind-stage').innerHTML.includes('1条已收录关系'));
  assert(p.appointments.some(a=>a.title==='博士后'));assert.equal(p.mentors.filter(m=>m.relationship_kind==='postdoctoral_advisor').length,0);
  const conflict=p.appointments.find(a=>a.field_status?.start==='conflicting_official_sections');assert(conflict);assert.equal(conflict.start,'2020-08');assert.equal(conflict.conflicting_start,'2018-12');
  assert(p.appointments.some(a=>a.institution==='新疆大学计算机科学与技术学院'&&a.end===null));
});

test('existing THU retired and active mentor navigation remain distinct and retirement evidence is retained',async()=>{
  const p=person('thu-dailinglong'),retired=p.mentors.find(m=>m.name==='杨知行'),active=p.mentors.find(m=>m.name==='龚克');assert(retired);assert(active);
  assert.equal(retired.employment_status,'retired_officially_listed');assert.equal(retired.quick_link_eligible,false);assert.equal(retired.navigation_verified,false);
  assert.equal(mentorOfficialUrl(retired),'');assert.equal(mentorProfileRoute(retired,db.people),'');assert(retired.description_source_ids.includes('thu-ee-retired-roster'));source(p,'thu-ee-retired-roster');
  assert.equal(active.employment_status,'active_officially_listed');assert.equal(mentorOfficialUrl(active),active.official_url);
  const html=(await app(p.person_id,'lineage')).node('#profile-content').innerHTML;
  const cards=html.match(/<article class="mentor-card"[\s\S]*?<\/article>/g)||[];
  const retiredCard=cards.find(c=>c.includes('杨知行')),activeCard=cards.find(c=>c.includes('龚克'));assert(retiredCard);assert(activeCard);
  assert(retiredCard.includes('官方列已退休'));assert(retiredCard.includes(escapeHtml(retired.source_url)));assert(!retiredCard.includes('查看导师个人主页'));assert(activeCard.includes('查看导师个人主页'));
});

test('Jane Gu competition guidance retains its own facts but never enters degree mentorship, internal navigation or the graph',async()=>{
  const p=person('sjtu-lijinbo');assert.deepEqual(p.mentors,[]);assert.equal(p.project_guidance.length,1);const c=p.project_guidance[0];
  assert.equal(c.name,'Qun Jane Gu');assert.equal(c.type,'research_project_advisor');assert.equal(c.relationship_kind,'research_project_advisor');
  assert.equal(c.education_event_id,null);assert.equal(c.person_id,null);assert.equal(c.start,null);assert.equal(c.end,null);assert.equal(c.institution,undefined);
  assert.equal(c.include_in_mentorship_graph,false);assert.equal(c.include_in_verified_mentor_count,false);assert.equal(c.quick_link_eligible,false);
  assert.equal(mentorOfficialUrl(c),'');assert.equal(mentorProfileRoute(c,db.people),'');assert.equal(c.source_collection,'mentors');assert.equal(c.source_collection_index,0);
  assert.equal(source(p,c.source_id).url,c.source_url);assert.equal(source(p,c.profile_source_id).url,c.profile_source_url);
  const ui=await app(p.person_id),section=projectSection(ui);assert(section.includes('项目指导（非学位师承）'));
  for(const key of ['name','type_label','education_stage','relationship_scope','description','note','scope_label'])assert(section.includes(escapeHtml(c[key])),key);
  assert(section.includes(escapeHtml(c.source_url)));assert(section.includes(escapeHtml(c.profile_source_url)));assert(!section.includes('对应经历'));
  assert(!section.includes('查看导师个人主页'));assert(!section.includes('查看本库个人档案'));
  ui.navigate('#/person/'+p.person_id+'/lineage');assert(!ui.node('#profile-content').innerHTML.includes(c.name));assert(!ui.node('#mind-stage').innerHTML.includes(c.name));assert(ui.node('#mind-stage').innerHTML.includes('0条已收录关系'));
});

test('real Jane project export has blank institution and dates, false award and no mentor row; Sun Qi keeps source level in memory',()=>{
  // -B prevents bytecode writes; Workbook is forbidden, so no XLSX is generated.
  const code=`import json,sys,copy\nfrom unittest import mock\nsys.path.insert(0,'scripts')\nimport build\nd=json.load(open('data/atlas.json')); out={}\nfor pid in ['sjtu-lijinbo','zju-sunqi']:\n p=next(p for p in d['people'] if p['person_id']==pid); before=copy.deepcopy(p)\n with mock.patch.object(build,'Workbook',side_effect=AssertionError('XLSX writing forbidden')):\n  out[pid]=dict(build.department_tables([p],d['updated_at'],d['institutions']))\n assert p==before\nprint(json.dumps(out,ensure_ascii=False))`;
  const tables=JSON.parse(execFileSync('python',['-B','-c',code],{cwd:fileURLToPath(new URL('..',import.meta.url)),encoding:'utf8'}));
  const t=tables['sjtu-lijinbo'];assert.deepEqual(Object.keys(t),['总览','经历','导师','论文','来源']);assert.equal(t['导师'].length,1);
  const projects=t['经历'].slice(1).filter(r=>r[1]==='project_guidance');assert.equal(projects.length,1);const row=projects[0],c=person('sjtu-lijinbo').project_guidance[0];
  assert.equal(row[2],'项目指导（非学位师承）');assert.deepEqual(row.slice(3,6),[null,null,null]);assert.equal(row[11],false);assert.equal(row[16],c.source_url);
  for(const k of ['name','type_label','education_stage','relationship_scope','description','profile_source_url'])assert(row[14].includes(c[k]),k);
  assert(row[14].includes('非学位师承，不计入导师统计或师承关系图'));assert.deepEqual(row.slice(-2),['sjtu','上海交通大学']);
  for(const s of person('zju-sunqi').sources.filter(s=>s.source_kind==='self_reported_personal_professional_website')){
    const r=tables['zju-sunqi']['来源'].find(r=>r[1]===s.id);assert(r);assert.equal(r[2],s.url);assert(r[3].includes(s.evidence_status_label));assert(r[3].includes(s.evidence_status));assert(!r[3].includes(s.source_evidence_status));
  }
});

test('Sun Qi personal professional website is visibly self-reported, never relabelled as a university website',async()=>{
  const p=person('zju-sunqi'),privateSources=p.sources.filter(s=>s.source_kind==='self_reported_personal_professional_website');
  assert.equal(p.official_url,'https://person.zju.edu.cn/0023146');assert.equal(privateSources.length,2);
  assert.deepEqual(privateSources.map(s=>s.url),['https://qisunchn.top/index.html','https://qisunchn.top/experience.html']);
  const ui=await app(p.person_id),list=ui.node('#profile-content').innerHTML.match(/<ol class="sources">[\s\S]*?<\/ol>/)?.[0];assert(list);
  for(const s of privateSources){assert.equal(s.evidence_status,'self_reported_professional_website_identity_cross_checked');assert.equal(s.source_evidence_status,'official_publisher_or_institution_metadata');assert.equal(s.evidence_status_label,'本人自述职业网站（已有官方身份交叉核验，非学校域名官网）');assert(list.includes(s.url));assert(list.includes(s.evidence_status_label))}
  assert(ui.node('#main').innerHTML.includes('href="'+p.official_url+'"'));assert(!list.includes('学校官方主页'));
});

test('Liang Ling source typo leaves the USC masters unconfirmed and indexed committee co-chairs remain only candidates',async()=>{
  const p=person('pku-liangling'),e=p.education.find(e=>e.event_id==='pku-liangling-education-2');assert(e);
  assert.equal(e.degree,'硕士');assert.equal(e.institution,'南加州大学');assert.equal(e.degree_awarded,null);assert(e.note.includes('获得硕士专业'));assert(e.note.includes('疑似笔误'));
  assert.equal(stages(p,'master').length,0);assert(!matches(p,{master:'overseas'}));assert(matches(p,{doctor:'overseas'}));assert.deepEqual(p.mentors,[]);assert.deepEqual(p.committee_members,[]);
  assert.deepEqual(p.pending_mentor_candidates.map(m=>m.name),['Yuan Xie','Peng Li']);
  for(const c of p.pending_mentor_candidates){assert.equal(c.relationship_type,'doctoral_committee_cochair_indexed');assert.equal(c.education_event_id,'pku-liangling-education-3');assert.equal(c.include_in_mentorship_graph,false);assert.equal(c.include_in_verified_mentor_count,false);assert.equal(c.quick_link_eligible,false)}
  const s=source(p,'liangling-source-3');assert.equal(s.evidence_status,'official_search_index_only');assert.equal(s.access_status,'direct_fetch_429_stopped');
  const ui=await app(p.person_id,'lineage');assert(ui.node('#mind-stage').innerHTML.includes('0条已收录关系'));assert(!ui.node('#mind-stage').innerHTML.includes('Yuan Xie'));assert(!ui.node('#mind-stage').innerHTML.includes('Peng Li'));
});

test('McIntyre explicit news-index wording and live faculty profile do not upgrade an unread migrated article into a verified advisor',()=>{
  const p=person('pku-tangkechao');assert.deepEqual(p.mentors,[]);assert.equal(p.pending_mentor_candidates.length,1);const c=p.pending_mentor_candidates[0];
  assert.equal(c.name,'Paul McIntyre');assert.equal(c.relationship_type,'doctoral_advisor_explicit_in_official_news_index');assert.equal(c.education_event_id,'pku-tangkechao-education-2');
  assert.equal(c.employment_status,'official_current_faculty_listing');assert.equal(c.include_in_mentorship_graph,false);assert.equal(c.include_in_verified_mentor_count,false);assert.equal(c.quick_link_eligible,false);assert.equal(mentorOfficialUrl(c),'');assert.equal(mentorProfileRoute(c,db.people),'');
  const s=source(p,c.source_id);assert.equal(s.evidence_status,'official_search_index_explicit_mentor_statement_only');assert.equal(s.access_status,'original_200_contains_javascript_redirect_target_404');assert.equal(s.redirect_target,'https://news.pku.edu.cn/info/3391/705511.htm');
  assert.equal(source(p,c.profile_source_id).url,'https://profiles.stanford.edu/paul-mcintyre');assert.equal(source(p,c.profile_source_id).evidence_status,'official_public_body_read');
  assert.equal(stages(p,'doctor').length,1);assert(matches(p,{doctor:'overseas',continent:'north_america'}));assert(p.education.some(e=>e.event_kind==='postdoctoral_research'&&e.degree_awarded===false));
});

test('Ren Pengpeng degree labels remain null and a Belgian visit cannot become an overseas doctorate',()=>{
  const p=person('sjtu-renpengpeng');assert.deepEqual(p.education.map(e=>e.degree_awarded),[null,null,false]);
  for(const e of p.education.slice(0,2)){assert.equal(e.field_status.degree_awarded,'not_independently_confirmed');assert(e.note.includes('不将其计为已确证授位'))}
  assert.equal(p.education[1].institution,'北京大学');assert.equal(p.education[1].region,'mainland');
  assert.equal(p.education[2].event_kind,'visiting_scholar');assert.equal(p.education[2].region,'overseas');assert.equal(p.education[2].continent_code,'europe');
  assert.equal(stages(p,'bachelor').length,0);assert.equal(stages(p,'doctor').length,0);assert(!matches(p,{doctor:'mainland'}));assert(!matches(p,{doctor:'overseas'}));assert(!matches(p,{continent:'europe'}));assert(matches(p,{doctor:'not_recorded'}));
});

test('Ren Kun remains pending with explicit doctorate evidence preserved but unknown institution, dates and count exclusion',()=>{
  const p=waiting('zju-renkun');assert(!db.people.some(x=>x.person_id===p.person_id));assert.equal(p.profile_status,'profile_details_pending');assert.deepEqual(p.education,[]);
  assert.equal(p.biography_evidence.count_eligible,false);assert.equal(p.biography_evidence.education.length,1);const e=p.biography_evidence.education[0];
  assert.equal(e.event_id,'zju-renkun-education-1');assert.equal(e.degree,'博士');assert.equal(e.degree_awarded,true);assert.equal(e.institution,null);assert.equal(e.start,null);assert.equal(e.end,null);assert.equal(e.region,'unknown');assert.equal(e.continent_code,'unknown');assert.equal(e.institution_985,'unknown');
  assert.equal(source(p,e.source_id).url,e.source_url);assert(p.unknowns.some(n=>n.includes('同名Kun Ren不合并')));assert.equal(stages(p,'doctor').length,0);assert(!matches(p,{doctor:'unknown'}));
  assert.equal(waiting('thu-xuxibin').appointments[0].title,'研究员');assert.equal(waiting('sjtu-liuting').appointments[0].title,'工程师');
});

test('Li Junkang doctoral guidance is real but does not establish an awarded ZJU doctorate or convert a Purdue visit',()=>{
  const p=person('zju-lijunkang'),m=p.mentors[0];assert.equal(p.mentors.length,1);assert.equal(m.name,'张睿');assert.equal(m.person_id,'zju-zhangrui');
  assert.equal(m.education_event_id,'zju-lijunkang-education-1');assert.equal(mentorEvent(p,m).degree_awarded,null);assert.equal(mentorEvent(p,m).institution,'浙江大学');assert.equal(mentorEvent(p,m).start,null);assert.equal(mentorEvent(p,m).end,null);
  assert.equal(mentorProfileRoute(m,db.people),'#/person/zju-zhangrui');assert.equal(mentorOfficialUrl(m),m.official_url);
  assert.equal(stages(p,'doctor').length,0);assert(!matches(p,{doctor:'mainland'}));assert(!matches(p,{doctor:'overseas'}));assert.equal(p.education[1].event_kind,'visiting_scholar');assert.equal(p.education[1].degree_awarded,false);
});

test('eight new main edges are five doctoral and three postdoctoral, with stable event IDs and no project or candidate leakage',()=>{
  const rows=fresh.flatMap(p=>(p.mentors||[]).map(m=>[p,m]));assert.equal(rows.length,8);
  assert.deepEqual(rows.map(([p,m])=>[p.person_id,m.name,m.relationship_kind,m.education_event_id]),[
    ['thu-taoxiaoming','陆建华','doctoral_advisor','thu-taoxiaoming-education-2'],
    ['zju-sunqi','Bei Yu','doctoral_advisor','zju-sunqi-education-2'],
    ['zju-sunqi','Zhiru Zhang','postdoctoral_advisor','zju-sunqi-education-3'],
    ['zju-lijunkang','张睿','doctoral_advisor','zju-lijunkang-education-1'],
    ['zju-yanzheyu','Yiyu Shi','doctoral_advisor','zju-yanzheyu-education-2'],
    ['zju-yanzheyu','Xiaobo Sharon Hu','doctoral_advisor','zju-yanzheyu-education-2'],
    ['zju-yanzheyu','Yiyu Shi','postdoctoral_advisor','zju-yanzheyu-education-3'],
    ['zju-yanzheyu','Xiaobo Sharon Hu','postdoctoral_advisor','zju-yanzheyu-education-3']
  ]);
  assert.deepEqual(progress.counts.main_guidance_types,{doctoral_advisor:5,postdoctoral_advisor:3});assert.equal(rows.filter(([p])=>p.school_id==='zju').length,7);
  for(const [p,m] of rows){assert.equal(m.include_in_mentorship_graph,true);assert.equal(m.include_in_verified_mentor_count,true);const e=mentorEvent(p,m);assert.equal(e.event_id,m.education_event_id);source(p,m.source_id);source(p,m.profile_source_id);if(m.relationship_kind==='postdoctoral_advisor'){assert.equal(e.degree_awarded,false);assert.equal(e.event_kind,'postdoctoral_research')}}
  assert.equal(counts(fresh).project_guidance,1);assert.equal(counts(fresh).pending_mentor_candidates,5);assert.equal(progress.counts.independent_project_guidance,1);assert.equal(progress.counts.pending_mentor_candidates_excluded_from_graph,5);
  for(const p of fresh)for(const c of p.pending_mentor_candidates||[]){assert.equal(c.include_in_mentorship_graph,false);assert.equal(c.include_in_verified_mentor_count,false);assert.equal(c.quick_link_eligible,false);assert(!p.mentors.some(m=>m.name===c.name))}
  assert.equal(person('sjtu-liuyan').pending_mentor_candidates[0].name,'Chris Toumazou');assert.equal(person('sjtu-qiliang').pending_mentor_candidates[0].name,'Rui P. Martins');
  const yan=person('zju-yanzheyu');assert.equal(yan.education[1].end,null);assert.equal(yan.education[1].field_status.end,'conflicting_sources');assert.equal(yan.education[2].start,null);assert.equal(yan.education[2].field_status.start,'conflicting_sources');
});

test('third-release real-data checks and renderers leave the source collections unmodified',()=>{
  assert.equal(JSON.stringify(db),original);
});
