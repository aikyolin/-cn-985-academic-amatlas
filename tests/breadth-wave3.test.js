import {readJSONFile,createAtlasFetch} from './atlas-test-io.js';
import {test} from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {createHash} from 'node:crypto';
import {execFileSync} from 'node:child_process';
import {fileURLToPath} from 'node:url';
import {UNIVERSITIES} from '../site/universities.js';
import {stages,degreeType,matches,mentorEvent,mentorOfficialUrl,mentorProfileRoute,officialProfileUrl,schoolStats,schoolCampuses,normalizeSchoolFilters,escapeHtml,routeSchool} from '../site/model.js';
import {rosterProfileLinks} from '../site/rosters.js';

const read=path=>readJSONFile(new URL(path,import.meta.url));
const db=read('../data/atlas.json'),rosters=read('../data/rosters.json'),progress=read('../progress/breadth-wave3-coverage.json'),site=read('../site/atlas.json'),siteRosters=read('../site/rosters.json');
db.rosters=rosters;db.exports=site.exports;const original=JSON.stringify(db);
const FIELDS=['education','appointments','mentors','committee_members','publications','sources','research_collaborators','pending_mentor_candidates','pending_mentors','project_guidance','professional_research_advisors','pending_publications'];
const counts=ps=>Object.fromEntries(FIELDS.map(k=>[k,ps.reduce((n,p)=>n+(p[k]||[]).length,0)]));
const awards=es=>[true,false,null].map(v=>es.filter(e=>e.degree_awarded===v).length);
const digest=value=>createHash('sha256').update(JSON.stringify(value)).digest('hex');
// Independently read and SHA-checked against the frozen research files and passed reviews.
// Only these nineteen first packages and three supplement-001 packages define this history.
const BATCHES=[
 ["ecnu","faculty-batch-ecnu-first-001","ecnu-selected-roster-first-001",3,0,[11,7,4,3,12],[2,4,5],"1e371de16021e43918f0d21b19ec0b87f30bf2ce51d07a467a570702b6e0ba79","d118de82244bc7b1fb7640350ea2c9ec92c661a88e059775c858ed4fc652773b"],
 ["seu","faculty-batch-seu-first-001","seu-selected-roster-first-001",1,2,[2,1,0,1,5],[1,0,1],"1d24f53efcca470eca407932d0a29245f20bbe457e66eb23c0249cc3704de719","304a66af6c42d9fb31ab72f4b9d9043e0b08f69924e627a68b5bc17ba7fd5a9a"],
 ["xmu","faculty-batch-xmu-first-001","xmu-selected-roster-first-001",2,1,[2,3,1,2,6],[2,0,0],"9efaba65974a9d094a306f0e7d844426b70e072b8d3832b7a6cb3620b01af10e","e1ec49db42cdbeb801a3404a594a5ed9ccd92c00e8a4e6f25bcc2e48176cb79b"],
 ["sdu","faculty-batch-sdu-first-001","sdu-selected-roster-first-001",3,0,[11,9,0,2,6],[4,2,5],"9db10c21a935d3497eca82739feb726e6677da8371ccc6488a7271ace3f752a2","8f42e32e7b7784261ccf5bbdc282e856d7d43ae35c14763107d79df744af18dc"],
 ["ouc","faculty-batch-ouc-first-001","ouc-selected-roster-first-001",2,1,[9,5,2,2,9],[0,4,5],"ed7635af302f15ec34a6718a67ab50bfede9c97b467afb016489afbda5ee1ebe","410a195db4e319fc2f19b8108b6889f793182b150b5ba00c3e075c3ff8e4fe29"],
 ["whu","faculty-batch-whu-first-001","whu-selected-roster-first-001",2,1,[5,9,0,2,5],[3,1,1],"283666dad6a990ce40dd8da5fe26223e71e02edae877ce2afdaec1bd88e60799","fbeaa89146af0a0a9be3e2a62f6bc20146c22da9ecc492a4b80de4db0e359263"],
 ["hust","faculty-batch-hust-first-001","hust-selected-roster-first-001",1,2,[3,2,0,1,3],[1,2,0],"192451816625455d514d27e8fabbc9d067a03afa41d8900131c37211034ae644","2756d52c14ec1b0f5d5108ee963049deb781b54ea26bbcd61ace2828b8996c93"],
 ["hnu","faculty-batch-hnu-first-001","hnu-selected-roster-first-001",3,0,[9,3,0,3,6],[5,2,2],"55933bf14e5df98e23c5b6f61c2198f762c4deb42e9627c1e6e7b8cb334510e5","d20c7a3396743bacdb1fccbe641ad25497f341892d8a73d91ad76cb0ac8aaa5c"],
 ["csu","faculty-batch-csu-first-001","csu-selected-roster-first-001",3,0,[7,9,0,3,6],[0,1,6],"398773be003dab0237748266a8e9740f3d87d57e045048b5ec5340f8b17f2eef","0e867ec167e94cf339d5f6f4f4e147b4a0802f82d39eb632599069a93c38b611"],
 ["nudt","faculty-batch-nudt-first-001","nudt-selected-roster-first-001",0,3,[0,0,0,0,0],[0,0,0],"a125b40d5c0a4565daf680567151a498a07bc66805a60d12ecc04c86d5270fca","421dd01b3d63c0d5fa2ab3a4ff3e9c734f836e723d7cf7454e5fd0a576a15ccc"],
 ["sysu","faculty-batch-sysu-first-001","sysu-selected-roster-first-001",0,3,[0,0,0,0,0],[0,0,0],"0cf7f3206ddfebab6d0c9dcf46e4b74ea2826a3ea6a1fe066ae8485da01da317","495456a88057f62bd2f1c28b2bb3730b973f8cddb369c6d6141300732c45e3cd"],
 ["scut","faculty-batch-scut-first-001","scut-selected-roster-first-001",3,0,[8,13,0,2,10],[0,2,6],"a6fbfca14d92cf6b64b2c9057479e8aad2d35ae5a35c545947dca98bd7575d7c","a236875667fa99ecc3d6f474faabfb58ec1cf56408cc509608793042c37cf278"],
 ["scu","faculty-batch-scu-first-001","scu-selected-roster-first-001",0,3,[0,0,0,0,0],[0,0,0],"816f185deefd0f68dab4ead06c07426a22ec29d0e190e717998a102633bc2ab9","3bf19d1648296bb28caa25aea3a8e7e09ca8405d0215f5e6a72acefcfdd7cbdf"],
 ["uestc","faculty-batch-uestc-first-001","uestc-selected-roster-first-001",3,0,[12,11,0,3,7],[0,3,9],"8eefb705cf90cff707ae5511eb96670d2aea1cf7582b9cdaa763bc2df8470dd2","87b6c784d9e1945538a3e1bdf90c9691af4cf9d4fc39c9da0eba8dcf12dce115"],
 ["cqu","faculty-batch-cqu-first-001","cqu-selected-roster-first-001",2,1,[4,5,0,1,5],[0,0,4],"305d599e5e0fa52b98a4b6a9e6b95f0aa0864b87ab0a1896f9bc0ebcbc25e6a8","6475b999ff082e083b7f92f772c23732e30099c2e7b86f0f0fd008b5fdec81b3"],
 ["xjtu","faculty-batch-xjtu-first-001","xjtu-selected-roster-first-001",3,0,[9,8,0,1,8],[4,4,1],"ff3a875ef7d1268baa74e1af7579eec1832217f801ded813f273c3f04d63ecf4","2a6e2134cf53614e63aaa776d2a85561d9aadded0552bbe35b909156f8cddcbc"],
 ["nwpu","faculty-batch-nwpu-first-001","nwpu-selected-roster-first-001",2,1,[3,3,0,2,9],[0,1,2],"18ef2ec8eae53d617d9d70c9b74fb2af8c2f1a2315b2d030a6bd45079dd6ceba","bd65ce869a5088f18988ad40f454ea569a0de3c2aefec8652af7af775d54f61d"],
 ["nwsuaf","faculty-batch-nwsuaf-first-001","nwsuaf-selected-roster-first-001",3,0,[7,6,0,2,6],[1,4,2],"98149d7cebd1df54a14529680c08957b221c50a153d0764352e26c4b3472a280","9c2fe4c0240c2aa5aa56171c16bacd7fb42a7809b3189e827f519b7ab2228702"],
 ["lzu","faculty-batch-lzu-first-001","lzu-selected-roster-first-001",3,0,[5,6,0,3,6],[0,3,2],"32f02f005790ba97821d760838ce9b10087f5881d8ee7f6c39152d5e42b17252","568b7180a99dcbf91daeaa8bf17ee01c72a78aac39ba8c0995743624fc2156c4"],
 ["nudt","faculty-batch-nudt-supplement-001","nudt-selected-roster-supplement-001",1,0,[4,1,0,1,5],[2,1,1],"ab7c06380355cdc8c6e3deb575d1185748d7c7a03f1d1c93f968a20d174c7f1a","0b45abd076d12aecba576b69a45a3fb756c31bdb7126d9cbe38e26a2aafed91c"],
 ["scu","faculty-batch-scu-supplement-001","scu-selected-roster-supplement-001",1,0,[2,2,0,1,3],[1,1,0],"2dd6f2698f877235dc53db1f5e2641bb213b7984363a1202c39e7ddb1b291667","619023b97a653f86f5af544e7532cd34fa38d61035865fd2139368e6d645d676"],
 ["sysu","faculty-batch-sysu-supplement-001","sysu-selected-roster-supplement-001",1,0,[3,3,0,0,5],[0,2,1],"c39c701e520875453ead68e4eb2afd43301063d489acfeff86c862f794ebf643","fc73b1441993bc114dbc657ac5ed76e706e2733cf9a1345fba31a8a74e9ac61e"]
].map(([sid,batch,roster,people,pending,fields,awards,sha,review])=>({sid,batch,roster,people,pending,fields,awards,sha,review}));
const batchIds=new Set(BATCHES.map(b=>b.batch)),rosterIds=new Set(BATCHES.map(b=>b.roster));
const fresh=db.people.filter(p=>batchIds.has(p.data_batch_id)),pending=db.pending_people.filter(p=>batchIds.has(p.data_batch_id)),allFresh=[...fresh,...pending];
const person=id=>{const p=allFresh.find(p=>p.person_id===id);assert(p,`Missing third-wave person ${id}`);return p};
const entry=p=>{const e=rosters.entries.find(e=>e.id===p.roster_entry_id);assert(e);return e};
const source=(p,id)=>{const s=p.sources.find(s=>s.id===id);assert(s,`${p.person_id}: missing source ${id}`);return s};

// Immutable pre-wave3 record prefixes, not limits on future total collection sizes.
const BASELINE={"atlas":{"people":[368,"0c2d23cb13562ab3b68dd0907f1fc83b352bafe8bd4548fa8903aa085218dd2c"],"pending_people":[52,"5bbbc25e91c2f54e099b1b41362a9540fa323d38c2415bfa5e6ac86f5d24ab85"],"institutions":[20,"f4e45ee7efba32ca1c6afa615c440e11b0c4665566cc429f0e1f05c4ab84a7ac"],"org_units":[109,"5596c4abe6d8da921793fda3f708441e88caf758a6971bd1c7184d8fe3303b7c"],"campuses":[3,"c26de0b2bdf97e1ebe640f5231bc494c34566a34b7d1c291804aee8a5b77b9f1"],"profile_batches":[62,"422a389a581c42674e916e9503c43642edd616977ffc8edf3e4c33991ef84c19"],"normalization_evidence":[6,"fe46005372cc88e5193fe9886d88e30b36c5f28892b924adb765f59a9c37dcd0"]},"roster":{"entries":[1502,"945735149a56c4820fa809dad28596ec524f047ff6eebda2ab72101a35b8c3e9"],"source_observations":[1540,"9d85ad82d1c2270af040f9adad940be0be2c04dfa942474e2ff24a010f5d9ed4"],"coverage":[118,"f3f74825b1480d30b6535bb3c7c89b8ff3edea5ee970e7ab7a103e7745c4dfeb"],"summary":[48,"68f468196bc0a34490975e44d69f615ed494a3404051036ec9f7b9ebc4ea33da"],"batches":[35,"69da7350b8713d1b8a089ad045b4379bd8ddf6ef303adb0abbc5df7c812105eb"]}};

test('22 frozen source/review hashes remain exact in the ledger and both profile and roster batch provenance',()=>{
 assert.equal(progress.baseline_commit,'28cb033687fe25b3aa36517e205fd8e03bf2f4a4');assert.equal(progress.source_references.length,22);assert.equal(progress.coverage_complete,false);assert.equal(progress.fields_complete,false);assert(progress.scope.includes('不表示已核在职、完整履历或全院名录完成'));
 assert.equal(new Set(BATCHES.map(b=>b.sid)).size,19);assert.equal(BATCHES.filter(b=>b.batch.includes('supplement-001')).length,3);
 for(const b of BATCHES){const refs=progress.source_references.filter(r=>r.sha256===b.sha);assert.equal(refs.length,1,b.batch);const ref=refs[0];assert.equal(ref.sha256,b.sha);assert.deepEqual(ref,{sha256:b.sha,independent_review_sha256:b.review});assert.equal(ref.independent_review_sha256,b.review);
  for(const batch of [db.profile_batches.find(x=>x.batch_id===b.batch),rosters.batches.find(x=>x.batch_id===b.roster)]){assert(batch);assert.equal(batch.school_id,b.sid);assert.deepEqual(batch.source_files,[{sha256:b.sha}]);assert.equal(batch.coverage_complete,false)}
  const pb=db.profile_batches.find(x=>x.batch_id===b.batch);assert.deepEqual([pb.people_count,pb.established_professional_profiles,pb.pending_profiles,pb.complete_profiles],[b.people+b.pending,b.people,b.pending,0]);assert.equal(pb.fields_complete,false);
 }
});

test('the exact60 selected identities stay42 partial plus18 pending with immutable per-batch facts',()=>{
 assert.deepEqual([fresh.length,pending.length,new Set(allFresh.map(p=>p.person_id)).size],[42,18,60]);
 assert.deepEqual([progress.counts.source_batch_count,progress.counts.first_batch_people,progress.counts.supplement_people,progress.counts.new_schools,progress.counts.new_organization_nodes,progress.counts.new_campuses,progress.counts.new_professional_profiles,progress.counts.new_pending_profiles],[22,57,3,19,31,0,42,18]);
 assert.deepEqual(counts(fresh),progress.counts.effective_global_collection_delta);assert.deepEqual(counts(pending),progress.counts.pending_main_collections);
 for(const b of BATCHES){const ps=fresh.filter(p=>p.data_batch_id===b.batch),qs=pending.filter(p=>p.data_batch_id===b.batch);assert.deepEqual([ps.length,qs.length],[b.people,b.pending]);assert.deepEqual(['education','appointments','mentors','publications','sources'].map(k=>counts(ps)[k]),b.fields);assert.deepEqual(awards(ps.flatMap(p=>p.education)),b.awards);for(const p of [...ps,...qs]){assert.equal(p.school_id,b.sid);assert.equal(p.fields_complete,false);assert.equal(p.complete_profile_count_eligible,false)}}
 for(const p of fresh){assert.equal(p.profile_status,'partial_professional_source_checked');assert.equal(p.detail_count_eligible,true);assert.equal(p.established_professional_count_eligible,true);assert(p.profile_coverage_label)}
});

test('18 pending profiles keep14 education observations outside confirmed collections and degree filters',()=>{
 const evidence=pending.flatMap(p=>p.biography_evidence?.education||[]);assert.equal(evidence.length,14);assert.deepEqual(awards(evidence),[0,2,12]);assert.deepEqual(progress.counts.pending_biography_evidence_collections,{education:14,mentors:0,publications:0});
 for(const p of pending){for(const k of ['education','mentors','publications'])assert.deepEqual(p[k],[]);assert.equal(p.profile_status,'profile_details_pending');assert.equal(p.detail_count_eligible,false);assert.equal(p.established_professional_count_eligible,false);if(p.biography_evidence)assert.equal(p.biography_evidence.count_eligible,false);for(const stage of ['bachelor','master','doctor'])assert.equal(stages(p,stage).length,0);assert(!matches(p,{doctor:'overseas'}));assert(!matches(p,{doctor:'unknown'}));assert(matches(p,{doctor:'not_recorded'}));assert(!db.people.some(q=>q.person_id===p.person_id))}
});

test('three supplements add different people and never promote the original nine NUDT SCU SYSU pending identities',()=>{
 const ids=['nudt-qianxu','nudt-tanglingyan','nudt-linaijin','scu-caikui','scu-chaizhi','scu-chengyanhong','sysu-caisuihua','sysu-chenchuan','sysu-chengang'];assert(ids.every(id=>pending.some(p=>p.person_id===id)));
 for(const sid of ['nudt','scu','sysu']){assert.equal(pending.filter(p=>p.data_batch_id===`faculty-batch-${sid}-first-001`).length,3);assert.equal(fresh.filter(p=>p.data_batch_id===`faculty-batch-${sid}-supplement-001`).length,1)}
 assert.deepEqual(fresh.filter(p=>p.data_batch_id.includes('supplement')).map(p=>p.person_id).sort(),['nudt-hudewen','scu-chenhu','sysu-bianchidavide']);
});

test('historical39-school410plus70 projection stays fixed while live whole-library statistics remain data-derived',()=>{
 const p=progress.counts.projection;assert.deepEqual([p.schools_with_any_records,p.schools_with_professional_profiles,p.schools_with_only_pending_records,p.professional_records,p.pending_records,p.organization_nodes],[39,39,0,410,70,140]);assert.deepEqual([p.roster_totals.record_count,p.roster_totals.raw_observation_count,p.roster_totals.category_count,p.roster_totals.batch_category_count,p.roster_totals.coverage_unit_count],[1562,1600,125,137,144]);
 assert.equal(UNIVERSITIES.length,39);assert.equal(new Set([...db.people,...db.pending_people].map(p=>p.person_id)).size,db.people.length+db.pending_people.length);
 for(const s of db.institutions){const stats=schoolStats(db,s.id);assert.equal(stats.people,db.people.filter(p=>p.school_id===s.id).length);assert.equal(stats.pending,db.pending_people.filter(p=>p.school_id===s.id).length);assert.equal(stats.rosters,rosters.entries.filter(r=>r.school_id===s.id).length);assert.equal(stats.published,stats.people>0)}
 assert.equal(rosters.totals.record_count,rosters.entries.length);assert.equal(rosters.totals.raw_observation_count,rosters.source_observations.length);assert.equal(rosters.totals.category_count,new Set(rosters.coverage.map(c=>JSON.stringify([c.organization_id,c.category]))).size);assert.equal(rosters.totals.batch_category_count,new Set(rosters.coverage.map(c=>JSON.stringify([c.batch_id??null,c.organization_id,c.category]))).size);assert.equal(rosters.totals.coverage_unit_count,rosters.coverage.length);
 assert.deepEqual(site.people,db.people);assert.deepEqual(site.pending_people,db.pending_people);assert.equal(siteRosters.entries.length,rosters.entries.length);
});

test('60 roster observations and26 coverage rows are selected samples, never a whole-school completion or inferred identity join',()=>{
 const entries=rosters.entries.filter(e=>rosterIds.has(e.batch_id)),obs=rosters.source_observations.filter(e=>rosterIds.has(e.batch_id)),coverage=rosters.coverage.filter(e=>rosterIds.has(e.batch_id));assert.deepEqual([entries.length,obs.length,coverage.length],[60,60,26]);
 for(const b of BATCHES){const expected=b.people+b.pending;assert.equal(entries.filter(e=>e.batch_id===b.roster).length,expected);assert.equal(obs.filter(e=>e.batch_id===b.roster).length,expected);const cs=coverage.filter(c=>c.batch_id===b.roster);assert.equal(cs.reduce((n,c)=>n+c.selected_observation_count,0),expected);for(const c of cs){assert.equal(c.count_scope,'selected_subset_only');assert.equal(c.all_visible_entries_captured,false);assert.equal(c.coverage_complete,false);assert.equal(c.school_id,b.sid)}}
 for(const e of entries){const p=allFresh.find(p=>p.roster_entry_id===e.id);assert(p);assert.equal(e.profile_identity_verified,false);assert.equal(e.verified_person_id,null);assert.equal(e.school_id,p.school_id);assert.equal(e.organization_id,p.department_id);assert.equal(e.campus_id,null);assert.equal(e.source_observation_ids.length,1);const o=obs.find(o=>o.observation_id===e.source_observation_ids[0]);assert.equal(o.record_id,e.id);assert.equal(o.source_payload.organization_id,e.organization_id);assert.equal(siteRosters.entries.find(r=>r.id===e.id).verified_person_id,null)}
 const scu=coverage.filter(c=>c.school_id==='scu');assert.equal(scu.length,2);assert.equal(new Set(scu.map(c=>JSON.stringify([c.organization_id,c.category]))).size,1);
});

let serial=0;
async function app(hash='#/'){
 const d=structuredClone(db);d.build_id='breadth-wave3-read-only';d.rosters.build_id=d.build_id;const nodes=new Map(),listeners={},node=k=>{if(!nodes.has(k))nodes.set(k,{innerHTML:'',textContent:'',value:'',style:{},events:{},dataset:{height:'320'},clientWidth:960,querySelector:node,addEventListener(t,f){this.events[t]=f},click(){this.onclick?.()}});return nodes.get(k)};
 globalThis.document={querySelector:node,querySelectorAll:()=>[],getElementById:id=>node('#'+id)};globalThis.location={href:"https://atlas.test/site/index.html",hash};globalThis.window={scrollTo(){},addEventListener(t,f){listeners[t]=f}};globalThis.fetch=createAtlasFetch(d,d.rosters);await import('../site/app.js?breadth-wave3-real='+serial++);assert(!node('#main').innerHTML.includes('资料暂未加载'));return {node,navigate(hash){location.hash=hash;listeners.hashchange()}};
}

test('national cards and nineteen school views use actual school scope without defaulting empty campuses to HIT',async()=>{
 const ui=await app(),published=UNIVERSITIES.filter(u=>schoolStats(db,u.id).published).length,directory=UNIVERSITIES.filter(u=>schoolStats(db,u.id).hasData&&!schoolStats(db,u.id).published).length;assert(ui.node('#main').innerHTML.includes(`目前${published}所学校有部分人物资料`));assert(ui.node('#main').innerHTML.includes(`其余${39-published-directory}所待收录`));assert.equal((ui.node('#school-grid').innerHTML.match(/class="school-card /g)||[]).length,39);
 for(const sid of new Set(BATCHES.map(b=>b.sid))){ui.navigate('#/school/'+sid);assert(ui.node('#main').innerHTML.includes(db.institutions.find(s=>s.id===sid).official_name));assert(!ui.node('#sidebar').innerHTML.includes('#/campus/harbin'));if(!schoolCampuses(db,sid).length)assert(ui.node('#main').innerHTML.includes('本批资料未单列校区归属'));assert.deepEqual(normalizeSchoolFilters(db,{school:sid,campus:'harbin',org:'hit-aerospace'}),{school:sid,campus:'',org:''})}
 for(const p of allFresh){assert.deepEqual(p.campus_ids,[]);assert.equal(p.campus,null);assert.equal(db.org_units.find(o=>o.id===p.department_id).school_id,p.school_id);assert.equal(routeSchool(db,'person',p.person_id),p.school_id);assert(matches(p,{school:p.school_id,org:p.department_id},db.org_units));assert(!matches(p,{school:'hit'},db.org_units));assert(!matches(p,{campus:'harbin'},db.org_units))}
});

test('Bianchi coverage notice distinguishes historical external biography and current index/self-report evidence',async()=>{
 const p=person('sysu-bianchidavide');assert.equal(p.name,'Bianchi Davide');assert.deepEqual(p.aliases,['Davide Bianchi']);assert.equal(p.department,'数学学院（珠海）');assert.deepEqual(p.campus_ids,[]);assert.equal(p.current_affiliation_evidence_status,'official_index_and_self_report_crosschecked_not_current_employment_verified');assert(p.profile_coverage_label.includes('当前中大归属仅官方索引＋本人公开陈述互证'));assert(p.profile_coverage_label.includes('未核校内正文或人事在岗'));assert.equal(p.navigation_verified,false);assert.equal(p.official_profile_navigation_eligible,false);assert.equal(p.own_profile_academic_body_read,false);assert.equal(officialProfileUrl(p),'');assert.equal(p.appointments[0].start,null);assert(p.appointments[0].status.includes('current_employment_unverified'));
 assert.deepEqual(awards(p.education),[0,2,1]);assert.equal(stages(p,'doctor').length,0);assert(!matches(p,{doctor:'overseas',continent:'europe'}));assert.deepEqual(p.mentors,[]);assert.deepEqual(p.publications,[]);assert(p.education.every(e=>e.start===null));assert.equal(source(p,'bianchidavide-source-4').evidence_status,'direct_self_reported_public_profile_body_verified');assert(source(p,'bianchidavide-source-5').evidence_status_label.includes('不证明未来活动已举行'));
 const ui=await app('#/person/'+p.person_id),html=ui.node('#main').innerHTML;assert(html.includes(`<p class="notice">${escapeHtml(p.profile_coverage_label)}</p>`));assert(!html.includes('学校官方主页'));assert(html.includes('厦门大学官方历史职业简介（2021年，非当前中大任职证明）'));assert(ui.node('#profile-content').innerHTML.includes('非学校人事核验'));assert(rosterProfileLinks(db,entry(p)).includes('个人主页当前不可用或正文未核'));
});

test('NUDT admissions supervision is not the listed academics own mentorship or a personal homepage',()=>{
 for(const id of ['nudt-qianxu','nudt-tanglingyan','nudt-linaijin']){const p=person(id),e=entry(p);assert.equal(p.profile_status,'profile_details_pending');assert.deepEqual(p.mentors,[]);assert.deepEqual(p.education,[]);assert.equal(p.official_url_kind,'official_admissions_roster_not_personal_profile');assert.equal(p.official_profile_availability,'not_identified');assert.equal(p.official_profile_navigation_eligible,false);assert.equal(officialProfileUrl(p),'');assert.equal(e.official_profile_url,null);assert.equal(e.profile_candidate_url,null);assert(!rosterProfileLinks(db,e).includes('href="'+p.official_url+'"'))}
});

test('Hu Dewen1995 is an observed visiting year, not a fabricated start date, institution or country',async()=>{
 const p=person('nudt-hudewen'),study=p.education[0],visit=p.education[3];assert.deepEqual([study.degree,study.degree_awarded,study.end],[null,null,'1983']);assert.deepEqual([visit.start,visit.end,visit.institution,visit.country,visit.degree_awarded],[null,null,null,null,false]);assert.equal(visit.source_reported_year,'1995');assert.equal(visit.date_basis,'observed_visiting_during_year_not_start_date');assert.equal(visit.region,'unknown');assert.equal(visit.continent_code,'unknown');assert.equal(p.official_url_kind,'official_university_professional_feature_not_personal_profile');assert.equal(officialProfileUrl(p),'');assert.equal(stages(p,'doctor').length,1);
 assert.deepEqual(p.alternative_professional_sources.map(s=>s.title),['学校官方人物报道（非个人主页）','中国科学院官方院士简介（非学校个人主页）']);const ui=await app('#/person/'+p.person_id);for(const s of p.alternative_professional_sources)assert(ui.node('#main').innerHTML.includes(s.title));assert(ui.node('#profile-content').innerHTML.includes('只证明该年在访，不代表起始年'));
});

test('SCU Cai Kui remains a retired engineer and the separate Chen Hu supplement retains study/employment dates',async()=>{
 const p=person('scu-caikui');assert.equal(p.employment_status,'retired');assert.equal(p.listed_role,'工程师（退休）');assert.deepEqual(p.education,[]);assert.equal(p.appointments[0].start,'1983-07-01');assert.equal(p.appointments[0].end,null);assert.equal(p.appointments[0].status,'historical_retirement_explicit_end_date_unknown');assert.equal(p.appointments[1].status,'retired');assert(!p.appointments.some(a=>a.status==='active_officially_listed'));assert.equal(mentorOfficialUrl(p),'');assert.equal(mentorProfileRoute(p,db.people),'');assert((await app('#/person/'+p.person_id)).node('#main').innerHTML.includes('工程师（退休）'));
 const q=person('scu-chenhu');assert.deepEqual(q.education.map(e=>e.degree_awarded),[true,false]);assert.equal(q.education[1].event_kind,'joint_doctoral_training');assert.equal(q.appointments[0].start,'2011-12');assert.equal(q.appointments[1].start,null);assert.equal(q.publications[0].year,2017);assert(q.publications[0].note.includes('2021-04-13'));assert(matches(q,{doctor:'mainland'}));assert(!matches(q,{doctor:'overseas'}));
});

test('HUST selection for a joint program does not imply actual overseas attendance or a confirmed doctorate',()=>{
 const p=person('hust-wangchengning'),es=p.biography_evidence.education,e=es.find(e=>e.event_kind==='selected_joint_doctoral_training_program');assert.equal(e.program_selection_year,'2019');assert.equal(e.attendance_verified,null);assert.equal(e.include_in_actual_overseas_experience,false);assert.deepEqual([e.start,e.end,e.degree_awarded],[null,null,false]);assert.equal(p.biography_evidence.count_eligible,false);assert.deepEqual(p.education,[]);assert(!matches(p,{doctor:'overseas'}));assert(!matches(p,{continent:'north_america'}));assert.equal(es[0].degree_awarded,null);assert.equal(es[0].degree_awarded_status,'indexed_explicit_award_pending_direct_verification');assert(es[0].indexed_award_statement.includes('获博士'));
 const q=person('csu-chenyuedan');assert(!q.education.some(e=>e.country&&!['中国'].includes(e.country)));assert(q.unknowns.some(s=>s.includes('计划')));
});

test('SDU official-directory-linked self-authored website keeps exact labels and cannot bypass navigation safety',async()=>{
 const p=person('sdu-wanghuaijin'),e=entry(p);assert.equal(p.official_url,'https://whj0401.github.io/');assert.equal(p.official_url_kind,'self_authored_professional_profile_linked_by_official');assert.equal(p.official_profile_link_label,'官方名录关联的本人职业网站');assert.equal(p.official_profile_availability_label,'官方名录关联的本人职业网站（非学校域名官网）');for(const k of ['official_url_kind','official_profile_link_label','official_profile_availability_label'])assert.equal(e[k],p[k]);assert.equal(source(p,'wanghuaijin-source-2').evidence_status,'self_authored_professional_profile_linked_by_official');assert.equal(p.publications[0].link_status,'self_authored_publication_list_linked_by_official');assert(p.publications[0].link_status_label.includes('未核出版社落地页或全文'));
 const ui=await app('#/person/'+p.person_id),html=ui.node('#main').innerHTML;assert(html.includes(p.official_profile_link_label));assert(html.includes(p.official_profile_availability_label));assert(!html.includes('学校官方主页'));assert(rosterProfileLinks(db,e).includes(p.official_profile_link_label));assert.equal(officialProfileUrl(p),p.official_url);
 for(const change of [{official_profile_navigation_eligible:false},{official_profile_availability:'unavailable'},{official_url:'javascript:unsafe()'},{official_url:'https://example.test/_cms/editor'}])assert.equal(officialProfileUrl({...p,...change}),'');
 const malicious={...e,official_profile_link_label:'<script>bad()</script>',official_profile_availability_label:'<img src=x onerror=bad()>',official_profile_url:'javascript:bad()'};const escaped=rosterProfileLinks(db,malicious);assert(!escaped.includes('<script>'));assert(!escaped.includes('<img'));assert(!escaped.includes('href="javascript:'));
});

test('SEU joint-directory members are not assigned simultaneously to three academic schools',()=>{
 const org=db.org_units.find(o=>o.id==='seu-computing-joint-roster');assert.equal(org.type,'joint_school_directory');assert.equal(org.navigation_only,true);assert.equal(org.is_academic_department,false);
 for(const id of ['seu-adam-mohammed','seu-baoxianqiang']){const p=person(id);assert.equal(p.department_id,org.id);assert.equal(p.academic_department_id,null);assert.equal(p.academic_department,null);assert.equal(p.department_assignment_status,'joint_directory_only_specific_school_unknown');assert(p.navigation_scope_label.includes('不代表同时隶属三个学院'));assert.equal(entry(p).organization_id,org.id);assert(!matches(p,{school:'seu',org:'seu-cs'},db.org_units));assert.equal(officialProfileUrl(p),'')}
 assert.equal(person('seu-beilun-wang').department_id,'seu-cs');assert(person('seu-beilun-wang').alternative_professional_sources.length>0);
});

test('HNU and NWPU use explicit leaf departments while retaining the original college and assignment evidence',async()=>{
 const expected={'hnu-anjiyao':'hnu-cs-computer-engineering','hnu-baiyanfeng':'hnu-cs-communication-engineering','hnu-cailijun':'hnu-cs-software-engineering','nwpu-chenqun':'nwpu-cs-computer-science-software','nwpu-lizhanhuai':'nwpu-cs-computer-science-software','nwpu-huangyuan':'nwpu-cs-computer-science-software'};const ui=await app();
 for(const [id,dept] of Object.entries(expected)){const p=person(id),u=db.org_units.find(u=>u.id===dept);assert.equal(p.department_id,dept);assert.equal(p.organization_id,dept);assert.equal(p.source_department_id,p.school_id+'-cs');assert.equal(p.organization_assignment_source_url,u.source_url);assert.equal(entry(p).organization_id,dept);assert.equal(u.parent_id,p.source_department_id);assert(matches(p,{org:dept,school:p.school_id},db.org_units));for(const other of Object.values(expected))if(other!==dept)assert(!matches(p,{org:other},db.org_units));if(fresh.includes(p)){ui.navigate('#/person/'+id);assert(ui.node('#main').innerHTML.includes('href="#/org/'+dept+'"'))}}
 assert.equal(new Set(fresh.filter(p=>p.school_id==='hnu').map(p=>p.department_id)).size,3);
});

test('NWPU unavailable portals preserve CCF and school-news source levels rather than calling all alternatives university pages',async()=>{
 const p=person('nwpu-chenqun');assert.equal(p.alternative_professional_sources.length,1);assert.equal(p.alternative_professional_sources[0].title,'CCF 学会官方职业简介（非学校个人主页）');assert(!JSON.stringify(p.alternative_professional_sources).includes('chenbenben.org.cn'));const self=p.sources.find(s=>s.evidence_status==='self_authored_public_profile_body_read');assert(self);assert.equal(self.evidence_status_label,'本人职业网站正文已读（非学校域名官网）。');
 for(const id of ['nwpu-chenqun','nwpu-lizhanhuai','nwpu-huangyuan']){const q=person(id);assert.equal(q.official_profile_availability,'unavailable');assert.equal(q.official_profile_navigation_eligible,false);assert.equal(q.own_profile_academic_body_read,false);assert.equal(officialProfileUrl(q),'');for(const s of q.alternative_professional_sources)assert.equal(source(q,s.source_id).url,s.url);const roster=rosterProfileLinks(db,entry(q));assert(roster.includes(q.alternative_professional_sources[0].title));assert(!roster.includes('职业身份由官方名录与校方报道核验'))}
 const ui=await app('#/person/'+p.person_id);assert(ui.node('#main').innerHTML.includes(p.alternative_professional_sources[0].title));assert(ui.node('#profile-content').innerHTML.includes(self.evidence_status_label));
});

test('two NWPU person-work records share one DOI and an unbridged bilingual candidate stays outside publication totals',()=>{
 const qs=fresh.filter(p=>p.school_id==='nwpu').flatMap(p=>p.publications);assert.equal(qs.length,2);assert.equal(new Set(qs.map(q=>q.doi)).size,1);assert(qs.every(q=>q.doi));const p=person('nwpu-huangyuan');assert.deepEqual(p.publications,[]);assert.equal(p.pending_publications.length,1);assert.equal(p.pending_publications[0].include_in_publication_count,false);assert.equal(p.pending_publications[0].publication_count_eligible,false);assert.equal(p.pending_publications[0].status,'pending_bilingual_identity_bridge');
 const pubs=fresh.flatMap(p=>p.publications),withDoi=pubs.filter(q=>q.doi);assert.equal(pubs.length,35);assert.equal(withDoi.length,9);assert.equal(new Set(withDoi.map(q=>q.doi)).size,8);assert.deepEqual(progress.counts.publication_count_scope,{person_work_records:35,records_with_doi:9,unique_explicit_dois:8,no_global_unique_paper_count_claim:true,nwpu_person_work_records:2,nwpu_unique_explicit_dois:1});
});

test('editorial and doctoral dissertation retain Chinese types and reading-level limits, not journal/full-text upgrades',async()=>{
 const types={};for(const q of fresh.flatMap(p=>p.publications))types[q.type]=(types[q.type]||0)+1;assert.deepEqual(types,{journal_article:24,conference_paper:9,editorial:1,doctoral_dissertation:1});assert.deepEqual(types,progress.counts.publication_types);
 for(const id of ['uestc-nicola-liberati','lzu-liuguanghua']){const p=person(id),q=p.publications[0];assert(q.type_label);assert(q.link_status_label);assert(q.type_label.includes('非'));const ui=await app('#/person/'+id),html=ui.node('#profile-content').innerHTML;assert(html.includes(q.type_label));assert(html.includes(q.link_status_label));assert(q.link_status_label.includes('全文'))}
 assert.equal(person('uestc-nicola-liberati').publications[0].type,'editorial');assert.equal(person('lzu-liuguanghua').publications[0].type,'doctoral_dissertation');assert.equal(stages(person('lzu-liuguanghua'),'doctor').length,0);
});

test('only26 explicitly awarded events enter degree filters, with unknown institutions and contradictory dates kept unknown',()=>{
 const es=fresh.flatMap(p=>p.education);assert.deepEqual(awards(es),[26,37,53]);assert.deepEqual(progress.counts.effective_degree_counts,{degree_awarded_true:26,degree_awarded_false:37,degree_awarded_null:53,confirmed_degree_events:26});assert.deepEqual(progress.counts.source_degree_counts,{degree_awarded_true:26,degree_awarded_false:39,degree_awarded_null:65,confirmed_degree_events:26});
 for(const p of allFresh)for(const type of ['bachelor','master','doctor']){const expected=p.education.filter(e=>e.event_kind==='degree'&&e.degree_awarded===true&&!String(e.field_status?.degree||'').startsWith('provisional_')&&degreeType(e.degree)===type);assert.deepEqual(stages(p,type),expected);for(const e of stages(p,type))assert.equal(e.degree_awarded,true)}
 const p=person('xjtu-zhuli');assert(p.education.every(e=>e.degree_awarded===true&&e.institution===null&&e.country===null&&e.region==='unknown'&&e.institution_985==='unknown'));assert(matches(p,{doctor:'unknown'}));assert(!matches(p,{doctor:'mainland'}));assert(!matches(p,{ug:'yes'}));const e=person('xjtu-wangwei').education.find(e=>e.degree_awarded===true);assert.equal(e.degree_awarded_date,null);assert(JSON.stringify(e).includes('2005'));assert(JSON.stringify(e).includes('2006'));
 assert.deepEqual(person('nwsuaf-lishuqin').education,[]);assert.equal(person('nwsuaf-gengnan').education[0].degree,null);assert.equal(person('nwsuaf-gengnan').education[0].degree_awarded,null);
});

test('seven direct mentor edges retain exact educational bindings and conservative current-role navigation',()=>{
 const ms=fresh.flatMap(p=>p.mentors);assert.equal(ms.length,7);assert.deepEqual(progress.counts.direct_guidance_types,{doctoral_advisor:4,postdoctoral_advisor:2,joint_doctoral_training_advisor:1});const p=person('ecnu-huangyihao');assert.deepEqual(p.mentors.map(m=>m.relationship_kind),['doctoral_advisor','doctoral_advisor','postdoctoral_advisor','postdoctoral_advisor']);
 for(const q of fresh)for(const m of q.mentors){assert(m.education_event_id);const e=mentorEvent(q,m);assert.equal(e.event_id,m.education_event_id);assert.equal(source(q,m.source_id).url,m.source_url);assert.equal(source(q,m.profile_source_id).url,m.profile_source_url);assert.equal(m.start,null);assert.equal(m.end,null);if(m.relationship_kind==='postdoctoral_advisor'||m.relationship_kind==='joint_doctoral_training_advisor')assert.equal(e.degree_awarded,false);if(m.quick_link_eligible===false||m.navigation_verified===false||m.employment_status!=='active_officially_listed')assert.equal(mentorOfficialUrl(m),'');else assert.equal(mentorOfficialUrl(m),m.official_url)}
 assert.equal(p.mentors[1].name,'缪炜恺');assert.equal(p.mentors[1].quick_link_eligible,false);const x=person('xmu-aosheng').mentors[0];assert.equal(x.name,'郭裕兰');assert.equal(x.navigation_verified,false);assert.equal(x.quick_link_eligible,false);assert(x.official_url);const joint=person('ouc-caoyuan');assert.equal(joint.mentors[1].relationship_kind,'joint_doctoral_training_advisor');assert.equal(mentorEvent(joint,joint.mentors[1]).degree_awarded,false);assert.equal(stages(joint,'doctor').length,0);
 for(const q of fresh.filter(p=>p.school_id==='scut')){assert.deepEqual(q.mentors,[]);for(const c of q.pending_mentor_candidates||[]){assert.equal(c.include_in_mentorship_graph,false);assert.equal(c.include_in_verified_mentor_count,false)}}
});

let exported;
function tables(){if(exported)return exported;const code=`import json,sys,copy\nfrom unittest import mock\nsys.path.insert(0,'scripts')\nimport build,build_rosters\nfrom atlas_storage import load_atlas\nd=load_atlas('data/atlas.json');r=json.load(open('data/rosters.json'));before=copy.deepcopy(d);rb=copy.deepcopy(r)\nbatches=set(${JSON.stringify(BATCHES.map(b=>b.batch))})\nfresh=[p for p in d['people'] if p.get('data_batch_id') in batches]\nwith mock.patch.object(build,'Workbook',side_effect=AssertionError('No XLSX')),mock.patch.object(build,'build',side_effect=AssertionError('No build')),mock.patch.object(build_rosters,'build_rosters',side_effect=AssertionError('No roster build')):\n build.validate(d);build_rosters.validate_rosters(r,d)\n subset=copy.deepcopy(d);subset['people']=fresh\n out={'selected_manifest':build.department_exports(subset),'manifest':build.department_exports(d),'tables':{dept:dict(build.department_tables([p for p in fresh if p['department_id']==dept],d['updated_at'],d['institutions'])) for dept in sorted({p['department_id'] for p in fresh})}}\nassert d==before and r==rb\nprint(json.dumps(out,ensure_ascii=False))`;exported=JSON.parse(execFileSync('python',['-B','-c',code],{cwd:fileURLToPath(new URL('..',import.meta.url)),encoding:'utf8',maxBuffer:8*1024*1024}));return exported}

test('in-memory exports follow actual leaf departments, exclude all18 pending and preserve school columns',()=>{
 const out=tables(),expectedDepts=new Set(fresh.map(p=>p.department_id));assert.equal(out.selected_manifest.length,expectedDepts.size);assert.equal(out.selected_manifest.reduce((n,e)=>n+e.people_count,0),42);
 for(const selected of out.selected_manifest){const live=out.manifest.find(e=>e.department_id===selected.department_id),snapshot=site.exports.find(e=>e.department_id===selected.department_id);assert.deepEqual(snapshot,live);assert.equal(live.people_count,db.people.filter(p=>p.department_id===live.department_id&&p.school_id===live.school_id).length);const t=out.tables[selected.department_id],ps=fresh.filter(p=>p.department_id===selected.department_id);assert.equal(Object.keys(t).length,5);assert.equal(t['总览'].length,ps.length+1);assert.deepEqual(t['总览'].slice(1).map(r=>r[0]).sort(),ps.map(p=>p.name).sort());for(const rows of Object.values(t))for(const row of rows.slice(1))assert.deepEqual(row.slice(-2),[selected.school_id,db.institutions.find(s=>s.id===selected.school_id).official_name]);for(const p of pending)assert(!t['总览'].slice(1).some(r=>r[0]===p.name))}
 for(const p of fresh.filter(p=>p.school_id==='hnu'))assert.equal(out.selected_manifest.find(e=>e.department_id===p.department_id).people_count,1);assert.equal(out.selected_manifest.find(e=>e.department_id==='nwpu-cs-computer-science-software').people_count,2);assert(!out.selected_manifest.some(e=>['seu-computing-joint-roster','nudt-science','sysu-cse'].includes(e.department_id)));
});

test('Excel matrices preserve explicit source labels, publication classifications, alternatives and mentor navigation vetoes',()=>{
 const t=tables().tables,sdu=person('sdu-wanghuaijin'),row=t[sdu.department_id]['总览'].find(r=>r[0]===sdu.name);assert.equal(row[3],sdu.official_url);assert.equal(row[7],sdu.official_profile_availability_label);assert.equal(t[sdu.department_id]['总览'][0][3],'个人主页／职业网站（来源类型见说明）');
 for(const p of fresh){const overview=t[p.department_id]['总览'].find(r=>r[0]===p.name);assert.equal(overview[3],officialProfileUrl(p));for(const s of p.alternative_professional_sources||[]){assert(overview[8].includes(s.title));assert(overview[8].includes(s.url))}for(const q of p.publications){const r=t[p.department_id]['论文'].find(r=>r[0]===p.name&&r[1]===q.title);assert(r);assert(r[5].includes(q.type_label));assert(r[5].includes(q.type));assert(r[8].includes(q.link_status_label));assert(r[8].includes(q.link_status))}for(const m of p.mentors){const r=t[p.department_id]['导师'].find(r=>r[0]===p.name&&r[1]===m.name);assert(r);assert.equal(r[7],mentorOfficialUrl(m));assert.equal(r[8],m.source_url);assert.equal(r[9],m.profile_source_url)}}
});

test('the append-only release leaves every prior20-school record, source observation and historical evidence unchanged',()=>{
 for(const [key,[n,sha]] of Object.entries(BASELINE.atlas))assert.equal(digest(db[key].slice(0,n)),sha,'prior atlas '+key);
 for(const [key,[n,sha]] of Object.entries(BASELINE.roster))assert.equal(digest(rosters[key].slice(0,n)),sha,'prior roster '+key);
});

test('source and event ownership closes locally and these read-only checks leave canonical objects unchanged',()=>{
 const ids=new Set();for(const p of allFresh){const sources=new Set(p.sources.map(s=>s.id));for(const e of [...p.education,...(p.biography_evidence?.education||[])]){assert.equal(e.event_id,e.education_event_id);assert(!ids.has(e.event_id));ids.add(e.event_id);assert(sources.has(e.source_id));assert.equal(source(p,e.source_id).url,e.source_url)}for(const a of p.appointments){assert(sources.has(a.source_id));assert.equal(source(p,a.source_id).url,a.source_url)}}
 assert.equal(JSON.stringify(db),original);
});
