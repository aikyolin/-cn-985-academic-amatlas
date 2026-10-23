import {test} from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {createHash} from 'node:crypto';
import {stages,matches,mentorEvent,schoolStats,schoolCampuses} from '../site/model.js';
const db=JSON.parse(fs.readFileSync(new URL('../data/atlas.json',import.meta.url)));db.rosters=JSON.parse(fs.readFileSync(new URL('../data/rosters.json',import.meta.url)));
const FIRST_PROFILE_BATCHES=new Set(['pku-ic-001','tsinghua-ee-001','faculty-batch-zju-ic-001','faculty-batch-sjtu-ic-001']);
const FIRST_ROSTER_BATCHES={thu:'thu-selected-roster-tsinghua-ee-001',pku:'pku-selected-roster-pku-ic-001',zju:'zju-selected-roster-ic-001',sjtu:'sjtu-selected-roster-ic-001'};
const history=JSON.parse(fs.readFileSync(new URL('../progress/multischool-first-coverage.json',import.meta.url)));
const fresh=db.people.filter(p=>FIRST_PROFILE_BATCHES.has(p.data_batch_id)),p=id=>db.people.find(p=>p.person_id===id);
const firstRoster=db.rosters.entries.filter(e=>Object.hasOwn(FIRST_ROSTER_BATCHES,e.school_id)&&e.batch_id===FIRST_ROSTER_BATCHES[e.school_id]);
test('four audited first-five samples preserve partial coverage and exact field counts',()=>{assert.equal(fresh.length,18);assert.equal(history.schools.reduce((n,s)=>n+s.pending_profiles,0),2);assert.equal(history.schools.reduce((n,s)=>n+s.established_profiles,0),18);assert.equal(history.coverage_complete,false);assert.deepEqual(new Set(history.source_packages.map(b=>b.batch_id)),FIRST_PROFILE_BATCHES);assert.deepEqual(['education','appointments','mentors','publications','sources'].map(k=>fresh.reduce((n,p)=>n+p[k].length,0)),[48,61,6,39,97]);for(const x of fresh){assert.equal(x.complete_profile_count_eligible,false);assert(x.profile_coverage_label.includes('部分'));assert.deepEqual(x.campus_ids,[])}});
test('school statistics follow current records while the first roster batches remain five selected samples',()=>{
  for(const [sid,n] of [['thu',5],['pku',5],['zju',3],['sjtu',5]]){
    const stats=schoolStats(db,sid),first=history.schools.find(s=>s.school_id===sid);
    assert.equal(stats.people,db.people.filter(x=>x.school_id===sid).length);
    assert.equal(stats.pending,db.pending_people.filter(x=>x.school_id===sid).length);
    assert.equal(stats.rosters,db.rosters.entries.filter(x=>x.school_id===sid).length);
    assert.equal(stats.units,db.org_units.filter(x=>x.school_id===sid).length);
    assert.equal(stats.status,'部分收录');
    assert.deepEqual(schoolCampuses(db,sid),db.campuses.filter(x=>x.school_id===sid));
    assert(schoolCampuses(db,sid).every(x=>!['harbin','weihai','shenzhen'].includes(x.id)));
    assert.equal(fresh.filter(x=>x.school_id===sid).length,n);
    assert.equal(first.established_profiles,n);
    assert.equal(first.selected_roster_records,5);
    assert.equal(first.complete_profiles,0);
    assert.equal(firstRoster.filter(x=>x.school_id===sid).length,5);
  }
});
test('new degree events retain16 verified11 nonaward21 unknown and original event types',()=>{const es=fresh.flatMap(x=>x.education);assert.equal(es.filter(e=>e.degree_awarded===true).length,16);assert.equal(es.filter(e=>e.degree_awarded===false).length,11);assert.equal(es.filter(e=>e.degree_awarded===null).length,21);for(const e of es.filter(e=>e.degree_awarded===true))assert.equal(e.event_kind,'degree')});
test('Chengran original two index-only events stay preserved and uncounted before or after an audited promotion',()=>{
  const current=db.people.filter(x=>x.person_id==='zju-chengran'),pending=db.pending_people.filter(x=>x.person_id==='zju-chengran');
  assert.equal(current.length+pending.length,1,'An update must move the same person, never duplicate the identity');
  const x=current[0]||pending[0],old=x.biography_evidence;
  const canonical=v=>Array.isArray(v)?v.map(canonical):v&&typeof v==='object'?Object.fromEntries(Object.keys(v).sort().map(k=>[k,canonical(v[k])])):v;
  const digest=v=>createHash('sha256').update(JSON.stringify(canonical(v))).digest('hex');
  assert.equal(digest(old),'28c2a7e6e566fb6f6e75bf7be498d723d1edfd8ca9cd070702d0593b632ddd60');
  assert.equal(digest(x.sources.slice(0,2)),'6c03ac29df65c491d7cd27d2018afcd6235d824dc3bb1d51316ff9704c6692f3');
  assert.equal(old.count_eligible,false);
  assert.equal(old.education.length,2);
  assert.deepEqual(old.education.map(e=>e.event_id),['zju-chengran-education-1','zju-chengran-education-2']);
  for(const e of old.education){assert.equal(e.degree_awarded,null);assert.equal(e.event_kind,'degree_study');assert.equal(e.verification_status,'official_search_index_only_pending_direct_body');assert.equal(e.source_id,'chengran-source-2')}
  const historicalView={education:old.education};
  assert.equal(stages(historicalView,'bachelor').length,0);
  assert.equal(stages(historicalView,'doctor').length,0);
  assert(!matches(historicalView,{ug:'no'}));
  assert(!matches(historicalView,{doctor:'overseas'}));
  if(x.data_batch_id==='faculty-batch-zju-ic-001'){
    assert.equal(current.length,0);assert.equal(pending.length,1);
    assert.equal(x.profile_status,'profile_details_pending');
    assert.deepEqual(x.education,[]);assert.deepEqual(x.mentors,[]);assert.deepEqual(x.publications,[]);
    assert.equal(x.detail_count_eligible,false);assert.equal(x.established_professional_count_eligible,false);
  }else{
    assert.equal(x.data_batch_id,'faculty-update-zju-chengran-001');
    assert.equal(current.length,1);assert.equal(pending.length,0);
    assert.equal(x.profile_status,'partial_professional_source_checked');
    assert.equal(x.previous_profile_evidence.data_batch_id,'faculty-batch-zju-ic-001');
    assert.equal(x.previous_profile_evidence.profile_status,'profile_details_pending');
    assert.equal(x.biography_evidence_supersession.count_eligible,false);
    assert.equal(x.biography_evidence_supersession.superseded_by_batch_id,x.data_batch_id);
    assert(x.profile_update_history.some(h=>h.batch_id===x.data_batch_id&&h.from_collection==='pending_people'&&h.to_collection==='people'&&h.prior_record_sha256==='fb79ee876f1cac67f80f254258831023b04ef24a08aa7dfa42fcf1cef7ff303e'));
    assert(x.education.every(e=>e.source_id!=='chengran-source-2'),'Retained index-only evidence must not become a confirmed main event source');
  }
  assert.equal(x.complete_profile_count_eligible,false);
});
test('GeNing conflicting Toronto label is not a verified overseas doctorate',()=>{const x=p('thu-gening');assert(!matches(x,{doctor:'overseas'}));assert.equal(stages(x,'doctor').length,0);assert(x.education.some(e=>e.event_kind==='uncertain_training'&&e.degree_awarded===null))});
test('Dai doctoral and postdoctoral advisors bind different exact events and retirement remains',()=>{const x=p('thu-dailinglong');assert.equal(mentorEvent(x,x.mentors[0]).event_id,'thu-dailinglong-education-3');assert.equal(mentorEvent(x,x.mentors[1]).event_id,'thu-dailinglong-education-5');assert.equal(mentorEvent(x,x.mentors[1]).degree_awarded,false);assert.notEqual(x.mentors[1].employment_status,'active_officially_listed')});
test('ChengZhe three relationships never upgrade unknown PhD award',()=>{const x=p('pku-cheng-zhe');assert.deepEqual(x.mentors.map(m=>mentorEvent(x,m).event_id),['pku-cheng-zhe-education-3','pku-cheng-zhe-education-4','pku-cheng-zhe-education-5']);assert.equal(stages(x,'doctor').length,0)});
test('GuoYuekang array event link survives canonical singular binding without2023 award invention',()=>{const x=p('sjtu-guoyuekang'),m=x.mentors[0];assert.deepEqual(m.education_event_ids,['sjtu-guoyuekang-education-1']);assert.equal(mentorEvent(x,m).event_id,m.education_event_ids[0]);assert.equal(mentorEvent(x,m).degree_awarded,null);assert.equal(stages(x,'doctor').length,0)});
test('unknown award institutions remain unknown geography despite verified doctorate',()=>{for(const id of ['zju-fuyali','sjtu-fuyuzhuo']){const x=p(id);assert(matches(x,{doctor:'unknown'}));assert(!matches(x,{doctor:'mainland'}));assert(!matches(x,{doctor:'overseas'}))}});
test('official selected roster links stay candidates without auto-promoting identity or employment',()=>{for(const e of firstRoster){assert.equal(e.profile_identity_verified,false);assert.equal(e.verified_person_id,null)}});

test('retired official status renders retirement rather than unknown and no repeated headline',()=>{const app=fs.readFileSync(new URL('../site/app.js',import.meta.url),'utf8');const expr=app.match(/const statusLabel=s=>([^;]+);/)[1];const label=new Function('s',`return (${expr});`);assert.equal(label('retired_officially_listed'),'官方列已退休');assert(!app.includes('已整理已建'));});

test('roster historical whole-library notes are distinct from filtered sample coverage',()=>{const src=fs.readFileSync(new URL('../site/rosters.js',import.meta.url),'utf8');assert(src.includes('全库各来源批次说明（不随学校筛选）'));assert(src.includes('四校首次接入各5条仅为选中样本'));});

test('person name touch targets never wrap into a click gap',()=>{const css=fs.readFileSync(new URL('../site/styles.css',import.meta.url),'utf8');assert.match(css,/\.person-link\{display:inline-block;white-space:nowrap;min-width:3em/);});
