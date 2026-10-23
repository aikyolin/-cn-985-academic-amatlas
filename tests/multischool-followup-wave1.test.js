import {test} from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {createHash} from 'node:crypto';
import {execFileSync} from 'node:child_process';
import {fileURLToPath} from 'node:url';
import {stages,degreeType,matches,mentorEvent,mentorEvents,professionalGuidanceEvent,mentorOfficialUrl,mentorProfileRoute,officialProfileUrl,schoolStats} from '../site/model.js';
import {rosterProfileLinks} from '../site/rosters.js';

const read=path=>JSON.parse(fs.readFileSync(new URL(path,import.meta.url)));
const db=read('../data/atlas.json'),rosters=read('../data/rosters.json'),progress=read('../progress/multischool-followup-wave1-coverage.json');
const before=JSON.stringify([db,rosters]);
const FIELDS=['education','appointments','mentors','committee_members','publications','sources','research_collaborators','pending_mentor_candidates','pending_mentors','project_guidance','professional_research_advisors','pending_publications'];
const counts=ps=>Object.fromEntries(FIELDS.map(k=>[k,ps.reduce((n,p)=>n+(p[k]||[]).length,0)]));
const awards=es=>[true,false,null].map(v=>es.filter(e=>e.degree_awarded===v).length);
const digest=value=>createHash('sha256').update(JSON.stringify(value)).digest('hex');
// Frozen source/review digests independently checked against all eighteen reviewed files.
// These constants define this release only; future batches and global growth remain allowed.
const BATCHES=[
  {
    "sid": "scu",
    "batch": "faculty-batch-scu-supplement-002",
    "roster": "scu-selected-roster-supplement-002",
    "ids": [
      "scu-chenli12",
      "scu-chenliangyin"
    ],
    "pending_ids": [
      "scu-chenjie",
      "scu-chenkaimin"
    ],
    "fields": [
      5,
      4,
      1,
      1,
      4,
      1
    ],
    "awards": [
      0,
      1,
      4
    ],
    "sha": "c72d61d3943af579e97265c4de0a97050d64c45cf1d4930f4b23f7f66ec2d5c2",
    "review": "f69ed3453976cd4682afeb9e6124636885db78b185e09a4968f7e0d52662b482"
  },
  {
    "sid": "nudt",
    "batch": "faculty-batch-nudt-supplement-002",
    "roster": "nudt-selected-roster-supplement-002",
    "ids": [
      "nudt-lixiang",
      "nudt-lidongxu"
    ],
    "pending_ids": [],
    "fields": [
      6,
      4,
      0,
      0,
      6,
      0
    ],
    "awards": [
      4,
      0,
      2
    ],
    "sha": "ebd208c30de74d1aa4bb2e7aa15d2e0f8858acdf5fb50d37b6bb6cff798e1f8a",
    "review": "5fb9c4e383a7d7c956c02280d4c44e7cf5593d7c914d310dedb21bc91688248b"
  },
  {
    "sid": "seu",
    "batch": "faculty-batch-seu-supplement-001",
    "roster": "seu-selected-roster-supplement-001",
    "ids": [
      "seu-bairufan",
      "seu-chongzhihong"
    ],
    "pending_ids": [
      "seu-chau-vincent"
    ],
    "fields": [
      5,
      3,
      2,
      1,
      9,
      0
    ],
    "awards": [
      2,
      2,
      1
    ],
    "sha": "f554588a9fc67da1373b92d1744620478cab344216d480d24730c2d2bd444172",
    "review": "7f9040018bdef5b6a1615e66df33615e5007c6002c228319571994928b5d9932"
  },
  {
    "sid": "sysu",
    "batch": "faculty-batch-sysu-supplement-002",
    "roster": "sysu-selected-roster-supplement-002",
    "ids": [
      "sysu-chailihui",
      "sysu-chenpeng",
      "sysu-chenbinglong"
    ],
    "pending_ids": [],
    "fields": [
      10,
      7,
      1,
      1,
      13,
      0
    ],
    "awards": [
      2,
      4,
      4
    ],
    "sha": "d2f087c95a4f4f1b1cdd134f3ae1840d2213d02736fea7888cfb54f28b96020a",
    "review": "3330fb71b11f02fed986a084ac7d26b3925875e13d80393927f4b7f4197fc32a"
  },
  {
    "sid": "hust",
    "batch": "faculty-batch-hust-supplement-001",
    "roster": "hust-selected-roster-supplement-001",
    "ids": [
      "hust-chenjiazhong",
      "hust-zhouyou",
      "hust-liuyu"
    ],
    "pending_ids": [],
    "fields": [
      11,
      4,
      6,
      3,
      10,
      0
    ],
    "awards": [
      4,
      4,
      3
    ],
    "sha": "29ef7a280ce0b04b5b04905e8f867676b3f082034ce059eee386460aac396c29",
    "review": "8a8b551dd019a2dedd622f91528315e7e1d51c9eb6363d2706cef0bfc8697624"
  },
  {
    "sid": "ouc",
    "batch": "faculty-batch-ouc-supplement-001",
    "roster": "ouc-selected-roster-supplement-001",
    "ids": [
      "ouc-chenxin",
      "ouc-caojingchao",
      "ouc-chenshuzhen"
    ],
    "pending_ids": [],
    "fields": [
      6,
      5,
      2,
      3,
      8,
      0
    ],
    "awards": [
      1,
      0,
      5
    ],
    "sha": "7ac3b53f31b1ab6ce1989c2fc30ed1778623362999f7e56eb70bb26229afc498",
    "review": "659736ef5505f1fd9e942fdea7835b6a8dd652e8f7d27f0b1e71296fed7d6be5"
  },
  {
    "sid": "nwpu",
    "batch": "faculty-batch-nwpu-supplement-001",
    "roster": "nwpu-selected-roster-supplement-001",
    "ids": [
      "nwpu-liuzhaowen",
      "nwpu-pengjiajie",
      "nwpu-shangxuequn"
    ],
    "pending_ids": [],
    "fields": [
      6,
      8,
      0,
      1,
      11,
      0
    ],
    "awards": [
      2,
      3,
      1
    ],
    "sha": "aa164dd3c76429d2ec1e67396807ca71a6cd0013fefb574ffa4366aef966cac0",
    "review": "3ffdded06575ec4741312d515f583f57eae60eb43a9df4a96678676ed616dd4f"
  },
  {
    "sid": "ruc",
    "batch": "faculty-batch-ruc-rotation-001",
    "roster": "ruc-selected-roster-rotation-001",
    "ids": [
      "ruc-wenjirong",
      "ruc-luzhiwu",
      "ruc-zhaoxin"
    ],
    "pending_ids": [],
    "fields": [
      11,
      11,
      0,
      3,
      10,
      0
    ],
    "awards": [
      6,
      3,
      2
    ],
    "sha": "70f733d4ce8e201fb8c76a1ff814c11fa6c1638d5b58c3cf9fe50dc43649fdfe",
    "review": "b9ae11fca2e51be17e02236565857ecdb53f87ee99f77b61b2418358fc867841"
  },
  {
    "sid": "whu",
    "batch": "faculty-batch-whu-supplement-001",
    "roster": "whu-selected-roster-supplement-001",
    "ids": [
      "whu-chenshuzhen",
      "whu-daiyonghong",
      "whu-hepingan"
    ],
    "pending_ids": [],
    "fields": [
      3,
      3,
      0,
      3,
      11,
      0
    ],
    "awards": [
      0,
      0,
      3
    ],
    "sha": "31970f1f7969510ca9b8d29065401b1cba11e282b42e9651eca6d87705ed2c4c",
    "review": "2f68e936d39d85167fde5c825b57e9e75eaa93956cbcaeb212cc0026895ea063"
  }
];
const batchIds=new Set(BATCHES.map(b=>b.batch)),rosterIds=new Set(BATCHES.map(b=>b.roster));
const fresh=db.people.filter(p=>batchIds.has(p.data_batch_id)),pending=db.pending_people.filter(p=>batchIds.has(p.data_batch_id)),allFresh=[...fresh,...pending];
const person=id=>{const p=allFresh.find(p=>p.person_id===id);assert(p,`Missing followup-wave1 person ${id}`);return p};
const entry=p=>{const e=rosters.entries.find(e=>e.id===p.roster_entry_id);assert(e);return e};
const source=(p,id)=>{const s=p.sources.find(s=>s.id===id);assert(s,`${p.person_id}: missing source ${id}`);return s};
// Immutable seventeenth-release prefixes, not maximum current-library sizes.
const BASELINE={"atlas":{"people":[410,"f0f7726eb21c357e1b6cce2906b8870c55482e85fc48e1b701771ef9f635c0ca"],"pending_people":[70,"0caccceb8185cff72bf94ff3853c1ded457334669154f9588526914869a8b1c2"],"institutions":[39,"69a6dd2fd04d253c59840b6330fda8122818478184b9e04e595e0bb730eb1312"],"org_units":[140,"7a609dd2e423b1bac37aee21e5e0361b0087301154a2daa92c32f0f1f1848a89"],"campuses":[3,"c26de0b2bdf97e1ebe640f5231bc494c34566a34b7d1c291804aee8a5b77b9f1"],"profile_batches":[84,"ca3de2c137ee2abe7d8346481d5f593be5bf4af52f7f28085e641a26d4446ea0"],"normalization_evidence":[7,"bea4f3a5c0010f72878452468a1f6b869e37782eac30c6fb8d38f1c510a2d5e6"]},"roster":{"entries":[1562,"b8e3edc4154feb725c2a7be8f2b803622c4f65a02c9705c366c6e3b33c5a2de3"],"source_observations":[1600,"3f05c829f83448cfd3b443cc3fb5930523f605fa87c528c7820952741472e1e2"],"coverage":[144,"c241bf530ce3765a96366f9e51c34f1ae4389925fe4d4cde25216fc1c64809b7"],"summary":[74,"1a1d32530c5d02460c3f94d22f79fd267abe687513751dd7b0514c36e362f09a"],"batches":[57,"f5ca609f41f4c26cd1a8c0f27de3b2de22640857a67b401e990d64825ae3e610"]}};

test('nine reviewed source hashes close through coverage and both canonical batch ledgers',()=>{
 assert.equal(progress.baseline_commit,'4a4bbf0d303a9a2b0880a44a75e4dc5542bb2edb');assert.equal(progress.source_references.length,9);assert.equal(progress.coverage_complete,false);assert.equal(progress.fields_complete,false);assert(progress.scope.includes('不代表完整履历'));
 for(const b of BATCHES){const ref=progress.source_references.find(r=>r.file===b.batch+'.json');assert(ref);assert.equal(ref.sha256,b.sha);assert.equal(ref.independent_review_file,b.batch+'-independent-review.json');assert.equal(ref.independent_review_sha256,b.review);
  for(const batch of [db.profile_batches.find(x=>x.batch_id===b.batch),rosters.batches.find(x=>x.batch_id===b.roster)]){assert(batch);assert.equal(batch.school_id,b.sid);assert(batch.source_files.some(s=>s.file===ref.file&&s.sha256===b.sha));assert.equal(batch.coverage_complete,false)}
  const pb=db.profile_batches.find(x=>x.batch_id===b.batch);assert.deepEqual([pb.people_count,pb.established_professional_profiles,pb.pending_profiles,pb.complete_profiles],[b.ids.length+b.pending_ids.length,b.ids.length,b.pending_ids.length,0]);assert.equal(pb.fields_complete,false);
 }
});
test('all seventeenth-release prefixes remain byte-equivalent as objects while future appended batches are allowed',()=>{
 for(const [key,[n,sha]] of Object.entries(BASELINE.atlas))assert.equal(digest(db[key].slice(0,n)),sha,'prior atlas '+key);
 for(const [key,[n,sha]] of Object.entries(BASELINE.roster))assert.equal(digest(rosters[key].slice(0,n)),sha,'prior roster '+key);
});
test('the selected27 identities stay24 partial plus3 pending with frozen per-batch facts',()=>{
 assert.deepEqual([fresh.length,pending.length,new Set(allFresh.map(p=>p.person_id)).size],[24,3,27]);assert.deepEqual(counts(fresh),progress.counts.effective_global_collection_delta);assert.deepEqual(counts(pending),progress.counts.pending_main_collections);
 assert.deepEqual([progress.counts.source_batch_count,progress.counts.source_people,progress.counts.new_schools,progress.counts.new_organization_nodes,progress.counts.new_campuses,progress.counts.new_professional_profiles,progress.counts.new_pending_profiles,progress.counts.complete_profiles],[9,27,0,5,0,24,3,0]);
 for(const b of BATCHES){const ps=fresh.filter(p=>p.data_batch_id===b.batch),qs=pending.filter(p=>p.data_batch_id===b.batch);assert.deepEqual(ps.map(p=>p.person_id).sort(),[...b.ids].sort());assert.deepEqual(qs.map(p=>p.person_id).sort(),[...b.pending_ids].sort());assert.deepEqual(['education','appointments','mentors','publications','sources','professional_research_advisors'].map(k=>counts(ps)[k]),b.fields);assert.deepEqual(awards(ps.flatMap(p=>p.education)),b.awards);
  for(const p of [...ps,...qs]){assert.equal(p.school_id,b.sid);assert.equal(p.fields_complete,false);assert.equal(p.complete_profile_count_eligible,false);assert.deepEqual(p.campus_ids,[]);assert.equal(db.org_units.find(o=>o.id===p.department_id).school_id,p.school_id)}
 }
 for(const p of fresh){assert.equal(p.profile_status,'partial_professional_source_checked');assert.equal(p.detail_count_eligible,true);assert.equal(p.established_professional_count_eligible,true)}
});
test('pending source observations never become detailed biographies or degree-filter evidence',()=>{
 assert.deepEqual(pending.map(p=>p.person_id).sort(),['scu-chenjie','scu-chenkaimin','seu-chau-vincent']);
 const evidence=pending.flatMap(p=>p.biography_evidence?.education||[]);assert.equal(evidence.length,2);assert.deepEqual(awards(evidence),[0,0,2]);assert.equal(progress.counts.pending_biography_education_events,2);
 for(const p of pending){for(const k of ['education','mentors','publications'])assert.deepEqual(p[k],[]);assert.equal(p.profile_status,'profile_details_pending');assert.equal(p.detail_count_eligible,false);assert.equal(p.established_professional_count_eligible,false);assert(!db.people.some(q=>q.person_id===p.person_id));for(const stage of ['bachelor','master','doctor'])assert.equal(stages(p,stage).length,0)}
 for(const id of ['nudt-qianxu','nudt-tanglingyan','nudt-linaijin','scu-caikui','scu-chaizhi','scu-chengyanhong','sysu-caisuihua','sysu-chenchuan','sysu-chengang','nwpu-huangyuan']){assert(db.pending_people.slice(0,70).some(p=>p.person_id===id));assert(!db.people.some(p=>p.person_id===id))}
});
test('historical434plus73 projection stays fixed but live totals remain data-derived',()=>{
 const p=progress.counts.projection;assert.deepEqual([p.schools_with_any_records,p.schools_with_professional_profiles,p.professional_records,p.pending_records,p.organization_nodes],[39,39,434,73,145]);assert.deepEqual([p.roster_totals.record_count,p.roster_totals.raw_observation_count,p.roster_totals.category_count,p.roster_totals.batch_category_count,p.roster_totals.coverage_unit_count],[1589,1627,130,149,156]);
 assert.equal(new Set([...db.people,...db.pending_people].map(p=>p.person_id)).size,db.people.length+db.pending_people.length);assert.equal(rosters.totals.record_count,rosters.entries.length);assert.equal(rosters.totals.raw_observation_count,rosters.source_observations.length);
 for(const sid of new Set(BATCHES.map(b=>b.sid))){const stats=schoolStats({...db,rosters},sid);assert.equal(stats.people,db.people.filter(p=>p.school_id===sid).length);assert.equal(stats.pending,db.pending_people.filter(p=>p.school_id===sid).length);assert.equal(stats.rosters,rosters.entries.filter(p=>p.school_id===sid).length)}
});
test('27 roster records and observations retain selected-only coverage and no guessed detailed-profile joins',()=>{
 const entries=rosters.entries.filter(e=>rosterIds.has(e.batch_id)),obs=rosters.source_observations.filter(e=>rosterIds.has(e.batch_id)),coverage=rosters.coverage.filter(e=>rosterIds.has(e.batch_id));assert.deepEqual([entries.length,obs.length,coverage.length],[27,27,12]);
 for(const b of BATCHES){const expected=b.ids.length+b.pending_ids.length;assert.equal(entries.filter(e=>e.batch_id===b.roster).length,expected);assert.equal(obs.filter(e=>e.batch_id===b.roster).length,expected);const cs=coverage.filter(c=>c.batch_id===b.roster);assert.equal(cs.reduce((n,c)=>n+c.selected_observation_count,0),expected);for(const c of cs){assert.equal(c.count_scope,'selected_subset_only');assert.equal(c.all_visible_entries_captured,false);assert.equal(c.coverage_complete,false)}}
 for(const e of entries){const p=allFresh.find(p=>p.roster_entry_id===e.id);assert(p);assert.equal(e.profile_identity_verified,false);assert.equal(e.verified_person_id,null);assert.equal(e.organization_id,p.department_id);assert.equal(e.school_id,p.school_id);assert.equal(e.campus_id,null);assert.equal(e.source_observation_ids.length,1);const o=obs.find(o=>o.observation_id===e.source_observation_ids[0]);assert.equal(o.record_id,e.id);assert.equal(o.source_payload.organization_id,e.organization_id)}
});
let serial=0;
async function app(hash){
 const d=structuredClone(db);d.build_id='followup-wave1-read-only';d.rosters=structuredClone(rosters);d.rosters.build_id=d.build_id;d.exports=[];
 const nodes=new Map(),listeners={},node=k=>{if(!nodes.has(k))nodes.set(k,{innerHTML:'',textContent:'',value:'',style:{},events:{},dataset:{height:'320'},clientWidth:960,querySelector:node,addEventListener(t,f){this.events[t]=f},click(){this.onclick?.()}});return nodes.get(k)};
 globalThis.document={querySelector:node,querySelectorAll:()=>[],getElementById:id=>node('#'+id)};globalThis.location={hash};globalThis.window={scrollTo(){},addEventListener(t,f){listeners[t]=f}};globalThis.fetch=async p=>({ok:true,json:async()=>structuredClone(String(p).startsWith('atlas.json')?d:d.rosters)});
 await import('../site/app.js?followup-wave1-real='+serial++);assert(!node('#main').innerHTML.includes('资料暂未加载'));return {node,navigate(hash){location.hash=hash;listeners.hashchange()}};
}
test('Cao Jingchao retains one Sam Kwong relation covering exactly two unknown-award stages without duplicate unknown mentors',async()=>{
 const p=person('ouc-caojingchao'),m=p.mentors[0];assert.equal(p.mentors.length,1);assert.equal(m.name,'Sam Kwong');assert.equal(m.relationship_kind,'postgraduate_advisor');assert.equal(m.stage_scope,'combined_masters_doctoral_statement_not_separate_edges');assert.deepEqual(m.education_event_ids,['ouc-caojingchao-education-2','ouc-caojingchao-education-3']);assert(!m.education_event_id);assert.deepEqual(mentorEvents(p,m),p.education.slice(1));assert.deepEqual(mentorEvent(p,m),{});assert(p.education.every(e=>e.degree_awarded===null));assert.equal(m.start,null);assert.equal(m.end,null);assert.equal(m.person_id,null);
 const ui=await app('#/person/'+p.person_id+'/lineage'),g=ui.node('#mind-stage').innerHTML,html=ui.node('#profile-content').innerHTML;assert(g.includes('1条已收录关系'));assert.equal((g.match(/href="#mentor-/g)||[]).length,1);assert.equal((g.match(/>导师未核实</g)||[]).length,1);assert(g.includes('合述机构未单独披露'));assert(g.includes('起始时间未披露 至 结束时间未披露'));assert(html.includes(m.stage_scope));assert(html.includes('合述仅计一条关系，不拆分阶段导师认定'));for(const id of m.education_event_ids)assert(html.includes(id));assert(!html.includes('查看本库个人档案'));
});
test('Chen Liangyin Tian He remains one independent occupational relationship with explicit non-award research context',async()=>{
 const p=person('scu-chenliangyin'),c=p.professional_research_advisors[0],e=professionalGuidanceEvent(p,c);assert.equal(p.mentors.length,1);assert.equal(p.mentors[0].name,'李志蜀');assert.equal(p.professional_research_advisors.length,1);assert.equal(c.name,'Tian He');assert.equal(c.source_collection,'mentors');assert.equal(c.source_collection_index,1);assert.equal(c.source_type,'research_supervisor');assert.equal(c.relationship_kind,'professional_research_advisor');assert.equal(c.education_event_id,'scu-chenliangyin-education-2');assert.equal(e.event_kind,'professional_research');assert.equal(e.degree_awarded,false);assert.equal(e.degree,null);assert.deepEqual([e.start,e.end],['2009-08','2010-09']);assert.equal(c.start,null);assert.equal(c.end,null);
 for(const k of ['include_in_mentorship_graph','include_in_degree_mentorship_graph','include_in_verified_mentor_count','quick_link_eligible','navigation_verified'])assert.equal(c[k],false);assert.equal(c.include_in_verified_professional_guidance_count,true);assert.equal(c.employment_status,'unknown');assert.equal(mentorOfficialUrl(c),'');assert.equal(mentorProfileRoute(c,db.people),'');
 const ui=await app('#/person/'+p.person_id),s=ui.node('#profile-content').innerHTML.match(/<section class="info-panel professional-guidance">[\s\S]*?<\/section>/)[0];assert(s.includes('Tian He'));assert(s.includes('起始时间未披露'));assert(s.includes('2009-08'));assert(s.includes('经历区间，不等于指导起止；非博士后认定'));ui.navigate('#/person/'+p.person_id+'/lineage');assert(!ui.node('#mind-stage').innerHTML.includes('Tian He'));assert(ui.node('#mind-stage').innerHTML.includes('1条已收录关系'));assert(!ui.node('#mind-stage').innerHTML.includes('明尼苏达大学'));assert(!ui.node('#mind-stage').innerHTML.includes('>导师未核实<'));assert(!ui.node('#mind-stage').innerHTML.includes('缺少明确来源，不推断导师'));
 const prior=db.people.find(p=>p.person_id==='nku-chensen');assert.equal(prior.professional_research_advisors[0].education_event_id,null);assert.deepEqual(professionalGuidanceEvent(prior,prior.professional_research_advisors[0]),{});
});
test('Yu Dongxiao reuses one existing verified entity and keeps all previous navigation veto rules',async()=>{
 const p=person('ouc-chenshuzhen'),m=p.mentors[0];assert.equal(m.name,'于东晓');assert.equal(m.person_id,'sdu-yudongxiao');assert.equal(db.people.filter(p=>p.person_id===m.person_id).length,1);assert(db.people.slice(0,410).some(p=>p.person_id===m.person_id));assert(!fresh.some(p=>p.person_id===m.person_id));assert.equal(m.employment_status,'active_officially_listed');assert.equal(mentorProfileRoute(m,db.people),'#/person/sdu-yudongxiao');assert.equal(mentorOfficialUrl(m),m.official_url);assert.equal(mentorEvent(p,m),p.education[1]);
 const html=(await app('#/person/'+p.person_id+'/lineage')).node('#profile-content').innerHTML;assert(html.includes('href="#/person/sdu-yudongxiao"'));for(const patch of [{person_id:null},{person_id:'missing'},{employment_status:'retired'},{employment_status:'unknown'},{quick_link_eligible:false}])assert.equal(mentorProfileRoute({...m,...patch},db.people),'');assert.equal(mentorProfileRoute({...m,navigation_verified:false},db.people),'#/person/sdu-yudongxiao');assert.equal(mentorOfficialUrl({...m,navigation_verified:false}),'');
});
test('WHU explicitly retired profiles remain retired with unknown retirement dates and no fabricated degree institutions',()=>{
 for(const id of ['whu-chenshuzhen','whu-hepingan']){const p=person(id),e=entry(p);assert.equal(p.employment_status,'retired');assert.equal(e.employment_status,'retired');assert.equal(e.role_category,'faculty_retired');assert(p.appointments.every(a=>a.status==='retired'&&a.end===null));assert.equal(mentorProfileRoute(p,db.people),'');assert.equal(mentorOfficialUrl(p),'')}
 assert.equal(person('whu-daiyonghong').employment_status,'employed');assert.equal(person('whu-daiyonghong').appointments[0].status,'official_profile_explicitly_employed');
 for(const p of fresh.filter(p=>p.school_id==='whu')){assert.deepEqual(p.mentors,[]);assert.equal(p.education.length,1);const e=p.education[0];assert.equal(e.degree_awarded,null);assert.equal(e.institution,null);assert.equal(e.country,null);assert.equal(e.start,null);assert.equal(e.end,null);assert.equal(e.region,'unknown');assert.equal(e.institution_985,'unknown');assert.equal(stages(p,'doctor').length,0);assert(!matches(p,{ug:'yes'}));assert.equal(p.official_profile_navigation_eligible,false)}
 assert.equal(person('whu-hepingan').education[0].degree,null);assert.equal(person('whu-hepingan').publications[0].link_status,'official_coauthor_publication_list_only');assert.equal(person('whu-hepingan').publications[0].individual_article_link_verified,false);
});
test('SYSU restriction and historical evidence labels never turn403 pages or old biographies into current employment verification',async()=>{
 for(const p of fresh.filter(p=>p.school_id==='sysu')){assert.equal(p.own_profile_academic_body_read,false);assert.equal(p.official_profile_availability,'unavailable');assert.equal(p.official_profile_navigation_eligible,false);assert.equal(officialProfileUrl(p),'');assert.equal(p.current_affiliation_evidence_status,'official_index_plus_historical_direct_bodies_not_current_employment_verified');assert(p.sources.some(s=>s.evidence_status==='official_search_index_only_direct_403'));assert(p.alternative_professional_sources.length);const html=(await app('#/person/'+p.person_id)).node('#main').innerHTML;assert(!html.includes('>学校官方主页'));assert(html.includes(p.profile_coverage_label));assert(html.includes(p.official_profile_availability_label));for(const a of p.alternative_professional_sources){assert.equal(source(p,a.source_id).url,a.url);assert(html.includes(a.title))}assert(!rosterProfileLinks({...db,rosters},entry(p)).includes('已核个人主页'))}
 const p=person('sysu-chailihui');assert.deepEqual(awards(p.education),[2,4,0]);assert.equal(p.mentors.length,1);assert.equal(p.mentors[0].name,'Shi Jin');assert.equal(mentorOfficialUrl(p.mentors[0]),'');assert(p.education[2].note.includes('不一致'));for(const id of ['sysu-chenpeng','sysu-chenbinglong']){const p=person(id);assert(p.education.every(e=>e.degree_awarded===null));assert.equal(stages(p,'doctor').length,0)}
});
test('HUST Liu Yu self-authored source and six stage relationships retain source level, original college and uncertain awards',async()=>{
 const ps=fresh.filter(p=>p.school_id==='hust'),p=person('hust-liuyu'),self=source(p,'liuyu-source-3');assert.equal(p.official_url,'https://lightyear416.github.io/liuyu/');assert.equal(p.official_url_kind,'self_authored_professional_profile_crosslinked_with_official_identity');assert.equal(p.own_profile_academic_body_read,false);assert.equal(self.evidence_status,'self_authored_professional_profile_read');assert.equal(source(p,'liuyu-source-2').evidence_status,'timeout_not_read');assert.equal(p.education[0].institution,'College of Post and Telecommunication of WIT');assert.equal(p.education[0].institution_985,'unknown');assert(p.education[1].note.includes('three-year'));assert.deepEqual(awards(p.education),[0,1,3]);assert.equal(stages(p,'doctor').length,0);
 const ms=ps.flatMap(p=>p.mentors);assert.equal(ms.length,6);assert.equal(new Set(ms.map(m=>m.name)).size,5);assert.deepEqual(p.mentors.filter(m=>m.name==='Ke Zhou').map(m=>m.relationship_kind),['doctoral_advisor','postdoctoral_advisor']);assert.notEqual(p.mentors[1].education_event_id,p.mentors[3].education_event_id);for(const m of ms){assert.equal(m.employment_status,'unknown');assert.equal(mentorOfficialUrl(m),'');assert.equal(mentorProfileRoute(m,db.people),'');assert.equal(m.start,null);assert.equal(m.end,null)}
 const ui=await app('#/person/'+p.person_id);assert(ui.node('#main').innerHTML.includes(p.official_profile_link_label));assert(!ui.node('#main').innerHTML.includes('>学校官方主页'));assert(ui.node('#profile-content').innerHTML.includes(self.evidence_status_label));
});
test('all direct relationships and educational filters preserve exact events rather than source-record counts or titles',()=>{
 const mentors=fresh.flatMap(p=>p.mentors),types={};for(const m of mentors)types[m.relationship_kind]=(types[m.relationship_kind]||0)+1;assert.equal(mentors.length,12);assert.deepEqual(types,{doctoral_advisor:9,masters_advisor:1,postdoctoral_advisor:1,postgraduate_advisor:1});assert.deepEqual(types,progress.counts.direct_guidance_types);assert.equal(progress.counts.source_collections.mentors,13);assert.equal(progress.counts.non_degree_professional_guidance_records,1);assert.equal(progress.counts.combined_stage_guidance_records,1);assert.deepEqual(awards(fresh.flatMap(p=>p.education)),[21,17,25]);
 for(const p of fresh)for(const type of ['bachelor','master','doctor'])assert.deepEqual(stages(p,type),p.education.filter(e=>e.event_kind==='degree'&&e.degree_awarded===true&&!String(e.field_status?.degree||'').startsWith('provisional_')&&degreeType(e.degree)===type));
 for(const p of fresh)for(const m of p.mentors){assert(mentorEvents(p,m).length);assert.equal(m.relationship_status,'verified_direct_statement');assert.equal(m.include_in_mentorship_graph,true);assert.equal(m.include_in_verified_mentor_count,true);assert.equal(m.start,null);assert.equal(m.end,null)}
 const chen=person('ouc-chenxin');assert.equal(chen.education[0].institution,null);assert.equal(chen.education[0].country,null);assert.equal(chen.education[0].degree_awarded,null);
});
let exported;
function tables(){if(exported)return exported;const code=`import json,sys,copy\nfrom unittest import mock\nsys.path.insert(0,'scripts')\nimport build,build_rosters\nd=json.load(open('data/atlas.json'));r=json.load(open('data/rosters.json'));before=copy.deepcopy(d);rb=copy.deepcopy(r)\nbatches=set(${JSON.stringify(BATCHES.map(b=>b.batch))})\nfresh=[p for p in d['people'] if p.get('data_batch_id') in batches]\nwith mock.patch.object(build,'Workbook',side_effect=AssertionError('No XLSX')),mock.patch.object(build,'build',side_effect=AssertionError('No build')),mock.patch.object(build_rosters,'build_rosters',side_effect=AssertionError('No roster build')):\n build.validate(d);build_rosters.validate_rosters(r,d)\n out={dept:dict(build.department_tables([p for p in fresh if p['department_id']==dept],d['updated_at'],d['institutions'])) for dept in sorted({p['department_id'] for p in fresh})}\nassert d==before and r==rb\nprint(json.dumps(out,ensure_ascii=False))`;exported=JSON.parse(execFileSync('python',['-B','-c',code],{cwd:fileURLToPath(new URL('..',import.meta.url)),encoding:'utf8',maxBuffer:8*1024*1024}));return exported}
test('real in-memory exports retain one Sam row, independent Tian context, unknown dates and blocked source navigation',()=>{
 const t=tables(),sam=person('ouc-caojingchao'),m=sam.mentors[0],rows=t[sam.department_id]['导师'].filter(r=>r[0]===sam.name);assert.equal(rows.length,1);for(const text of [m.stage_scope,...m.education_event_ids,'起始时间未披露','结束时间未披露'])assert(rows[0][6].includes(text));
 const chen=person('scu-chenliangyin'),tr=t[chen.department_id]['导师'].find(r=>r[0]===chen.name&&r[1]==='Tian He');assert.equal(tr[2],'职业科研指导（非学位）');for(const text of ['scu-chenliangyin-education-2','指导起止：起始时间未披露 至 结束时间未披露','2009-08 至 2010-09','经历区间，不等于指导起止；非博士后认定'])assert(tr[6].includes(text));assert.equal(tr[7],'');
 for(const p of fresh){const row=t[p.department_id]['总览'].find(r=>r[0]===p.name);assert.equal(row[3],officialProfileUrl(p));for(const m of p.mentors){const r=t[p.department_id]['导师'].find(r=>r[0]===p.name&&r[1]===m.name&&r[2]===(m.type_label||m.type));assert(r);assert.equal(r[7],mentorOfficialUrl(m));assert.equal(r[8],m.source_url)}for(const q of p.publications){const r=t[p.department_id]['论文'].find(r=>r[0]===p.name&&r[1]===q.title);assert(r[5].includes(q.type_label));assert(r[8].includes(q.link_status_label))}}
 assert.equal(Object.values(t).reduce((n,x)=>n+x['总览'].length-1,0),24);assert.equal(Object.values(t).reduce((n,x)=>n+x['导师'].length-1,0),13);
});
test('local source and event ownership stay closed, sensitive caches absent and all checks remain read-only',()=>{
 const allIds=new Set();for(const p of allFresh){const sources=new Set(p.sources.map(s=>s.id)),events=new Set([...p.education,...(p.biography_evidence?.education||[])].map(e=>e.event_id));assert.equal(sources.size,p.sources.length);
  for(const e of [...p.education,...(p.biography_evidence?.education||[])]){assert.equal(e.event_id,e.education_event_id);assert(!allIds.has(e.event_id));allIds.add(e.event_id);assert.equal(source(p,e.source_id).url,e.source_url)}
  for(const a of p.appointments){assert(sources.has(a.source_id));assert.equal(source(p,a.source_id).url,a.source_url)}
  function walk(v){if(Array.isArray(v))return v.forEach(walk);if(!v||typeof v!=='object')return;for(const [k,x] of Object.entries(v)){assert(!k.endsWith('_cache'));assert(!['body_cache','text_cache','retrieval_note','email','phone','birth_date','student_list','students'].includes(k));if(k==='field_provenance'){for(const r of Object.values(x))if(r!==null)for(const id of Array.isArray(r)?r:[r])assert(sources.has(id));continue}if((k==='source_id'||k.endsWith('_source_id'))&&x!==null)assert(sources.has(x),p.person_id+' '+k+' '+x);if(k==='source_ids'||k.endsWith('_source_ids'))assert(x.every(id=>sources.has(id)));if(k==='education_event_id'&&x!==null)assert(events.has(x));if(k==='education_event_ids')assert(x.every(id=>events.has(id)));walk(x)}}walk(p);assert(!JSON.stringify(p).includes('/workspace/'));
 }
 assert.equal(allIds.size,65);assert.equal(JSON.stringify([db,rosters]),before);
});
