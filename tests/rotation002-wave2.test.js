// Offline release23 consumer regressions. Only reviewed NJU/HNU additions;
// no source fetch, browser, build writes, or dependency on the research folder.
import {test} from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {stages,matches,educationStageLabel,mentorOfficialUrl,mentorEvents,officialProfileUrl,schoolStats} from '../site/model.js';
import {rosterIdentityMatched,rosterStatusLabel,renderRosters} from '../site/rosters.js';

const read = path => JSON.parse(fs.readFileSync(new URL(path, import.meta.url)));
const db = read('../data/atlas.json');
db.rosters = read('../data/rosters.json');
const ids = ['nju-chengxin','nju-chenpengfei','nju-chenyang','hnu-chenzengping','hnu-chuxia','hnu-huanshuangyan'];
const person = id => db.people.find(p => p.person_id === id);
const added = ids.map(person);
const event = (id,number) => person(id).education.find(e => e.event_id === `${id}-education-${number}`);
const escape = value => String(value).replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;').replaceAll('"','&quot;');
let serial = 0;

async function render(id, mode='profile', input=db) {
  const view = structuredClone(input), nodes = new Map();
  view.build_id = view.rosters.build_id = 'rotation002-wave2-consumer-fixture';
  view.exports ||= []; // Directory export buttons are outside this rendering fixture.
  const node = key => {
    if (!nodes.has(key)) nodes.set(key, {
      innerHTML:'',textContent:'',value:'',style:{},dataset:{height:'320'},clientWidth:960,
      addEventListener(){}, click(){this.onclick?.()}, scrollIntoView(){},
      querySelector(selector){return node(selector)},
    });
    return nodes.get(key);
  };
  globalThis.document = {querySelector:node,querySelectorAll:()=>[],getElementById:id=>node('#'+id)};
  globalThis.location = {hash:mode === 'directory' ? `#/people?school=${id}` : `#/person/${id}${mode === 'lineage' ? '/lineage' : ''}`};
  globalThis.window = {scrollTo(){},addEventListener(){}};
  globalThis.fetch = async path => {
    assert.match(String(path), /^(atlas|rosters)\.json(?:\?|$)/, 'External fetch prohibited');
    return {ok:true,json:async()=>structuredClone(String(path).startsWith('atlas.json') ? view : view.rosters)};
  };
  await import('../site/app.js?rotation002-wave2='+serial++);
  assert(!node('#main').innerHTML.includes('资料暂未加载'),node('#main').innerHTML);
  return {main:node('#main').innerHTML,content:node('#profile-content').innerHTML,graph:node('#mind-stage').innerHTML,results:node('#results').innerHTML};
}

test('release23 six selected NJU/HNU profiles remain unchanged at the release24 endpoint', () => {
  assert.equal(db.people.length,555);assert.equal(db.pending_people.length,84);
  assert.equal(db.org_units.length,229);assert.equal(db.institutions.length,39);
  assert.equal(db.rosters.entries.length,1721);assert.equal(db.rosters.source_observations.length,1759);
  assert.deepEqual(db.people.slice(535,541).map(p=>p.person_id),ids);
  assert.deepEqual(db.rosters.entries.slice(1700,1706).map(e=>e.source_person_id),ids);
  assert.deepEqual(db.profile_batches.slice(130,132).map(b=>b.batch_id),['faculty-batch-nju-rotation-002','faculty-batch-hnu-rotation-002']);
  for (const p of added) {
    assert.equal(p.detail_count_eligible,true);assert.equal(p.complete_profile_count_eligible,false);
    assert.equal(p.fields_complete,false);assert.deepEqual(p.campus_ids,[]);assert.equal(p.campus,null);
  }
});

test('main event totals and award tristates are not inflated by candidates or service facts', () => {
  const counts = Object.fromEntries(['education','appointments','mentors','publications','teaching','academic_service','honors','research_projects'].map(k=>[k,added.reduce((n,p)=>n+(p[k]||[]).length,0)]));
  assert.deepEqual(counts,{education:29,appointments:23,mentors:3,publications:8,teaching:10,academic_service:29,honors:19,research_projects:11});
  const countsAward = added.flatMap(p=>p.education).reduce((out,e)=>(out[String(e.degree_awarded)]++,out),{true:0,null:0,false:0});
  assert.deepEqual(countsAward,{true:4,null:10,false:15});
  for (const p of added) for (const key of ['professional_research_advisors','project_guidance','research_collaborators','committee_members']) assert.deepEqual(p[key]||[],[]);
});

test('only the four explicit mainland doctorates enter actual filters', () => {
  const doctor = new Map([['nju-chengxin',2],['nju-chenpengfei',1],['nju-chenyang',2],['hnu-chenzengping',3]]);
  for (const p of added) {
    assert.deepEqual(stages(p,'bachelor'),[]);assert.deepEqual(stages(p,'master'),[]);
    assert.deepEqual(stages(p,'doctor').map(e=>e.event_id),doctor.has(p.person_id)?[`${p.person_id}-education-${doctor.get(p.person_id)}`]:[]);
    assert.equal(matches(p,{ug:'not_recorded'},db.org_units),true);
    assert.equal(matches(p,{doctor:'mainland'},db.org_units),doctor.has(p.person_id));
    assert.equal(matches(p,{doctor:'overseas'},db.org_units),false);
    assert.equal(matches(p,{doctor:'not_recorded'},db.org_units),!doctor.has(p.person_id));
  }
});

test('ID-less candidate with an explicit award never transfers to conflicting main institution', async () => {
  const p=person('nju-chengxin'), c=p.pending_education_candidates[0], main=p.education[0];
  assert.equal(c.degree_awarded,true);assert.equal(c.institution,'Zhejiang University of Science and Technology');
  assert.equal('event_id' in c,false);assert.equal(c.include_in_education_filters,false);
  assert.equal(main.degree_awarded,null);assert.equal(main.include_in_education_filters,false);
  assert.equal(main.institution,'浙江工业大学（CV原文 Zhejiang University of Technology）');
  assert.deepEqual(stages(p,'bachelor'),[]);
  const html=(await render(p.person_id)).content;
  assert(!html.includes(`<h3>${c.institution}</h3>`));
  assert(html.includes(escape(main.institution)));
  assert(html.includes('CV列B.S. Physics，没有明确授位动词'));
  const cy=person('nju-chenyang').pending_education_candidates[0];
  assert.equal('event_id' in cy,false);assert.equal(cy.institution,null);assert.equal(cy.degree_awarded,null);
  assert.deepEqual(stages(person('nju-chenyang'),'master'),[]);
});

test('Cheng Xin joint-training conflicting month stays explicit and never becomes a foreign degree', async () => {
  const e=event('nju-chengxin',3);
  assert.deepEqual([e.start,e.end],['2010-10','2011-12']);
  assert.equal(e.event_kind,'joint_training');assert.equal(e.degree_awarded,false);
  assert(e.note.includes('英文为9月'));assert(e.note.includes('10月'));
  const html=(await render('nju-chengxin')).content;
  assert(html.includes(e.note));assert.equal(matches(person('nju-chengxin'),{doctor:'overseas'},db.org_units),false);
});

test('four combined host events keep unknown per-institution dates in actual profile timelines', async () => {
  const html=(await render('nju-chenpengfei')).content;
  for (const n of [4,5,6,7]) {
    const e=event('nju-chenpengfei',n), combined=e.source_combined_period;
    assert.equal(e.start,null);assert.equal(e.end,null);assert.equal(e.degree_awarded,false);
    assert.equal(combined.scope,'combined_multi_institution_visit_only');assert.equal(combined.individual_institution_period_known,false);
    assert(combined.institutions.includes(e.institution));
    const article=html.split('<article>').find(part=>part.includes(`<h3>${escape(e.institution)}</h3>`));
    assert(article,e.institution);
    const timeline=article.split('</div>')[0];
    assert(!timeline.includes(combined.start));assert(!timeline.includes(combined.end));
    assert(article.includes(escape(e.note)));
  }
});

test('four award dates remain year-only and HNU award cites supplemental direct award source', async () => {
  for (const e of added.flatMap(p=>p.education).filter(e=>e.degree_awarded===true)) {
    assert.match(e.degree_awarded_date,/^\d{4}$/);assert.equal(e.event_kind,'degree');
    assert.equal(e.degree_award_source_id,e.field_provenance.degree_awarded);
  }
  const e=event('hnu-chenzengping',3);
  assert.equal(e.source_event_kind,'degree_study');assert.equal(e.end,'2001-05');assert.equal(e.degree_awarded_date,'2001');
  assert.notEqual(e.degree_award_source_url,e.source_url);
  const html=(await render('hnu-chenzengping')).content;
  assert(html.includes('授位日期：2001 '));assert(html.includes(`href="${escape(e.degree_award_source_url)}"`));
  assert(!html.includes('授位日期：2001-05'));
});

test('HNU historical director end and undergraduate level are not upgraded to current role or awarded bachelor', async () => {
  const role=person('hnu-chuxia').appointments.find(a=>a.title==='副主任');
  assert.equal(role.end,'2021-12');assert.equal(role.current,false);assert.equal(role.status,'historical_source_reported');
  assert((await render('hnu-chuxia')).content.includes('2021-12'));
  const e=event('hnu-huanshuangyan',1);
  assert.equal(e.degree,null);assert.equal(e.degree_awarded,null);assert.equal(e.education_level,'本科');assert.equal(e.institution,'中南民族学院');
  assert.equal(educationStageLabel(e),'学习经历（学位层次未披露）');
  for (const p of added.filter(p=>p.school_id==='hnu')) assert.deepEqual(p.mentors,[]);
});

test('two verified current NJU mentor links retain raw status and bind only explicit doctoral event', async () => {
  const p=person('nju-chengxin'), html=await render(p.person_id,'lineage');
  assert.equal(p.mentors.length,2);
  for (const m of p.mentors) {
    assert.equal(m.source_employment_status,'official_currently_listed_not_personnel_verified');
    assert.equal(m.employment_status,'active_officially_listed');assert.equal(m.navigation_verified,true);assert.equal(m.quick_link_eligible,true);
    assert.equal(mentorOfficialUrl(m),m.official_url);assert.deepEqual(mentorEvents(p,m).map(e=>e.event_id),['nju-chengxin-education-2']);
    assert.equal(m.start,null);assert.equal(m.end,null);
    assert(html.content.includes(`href="${escape(m.official_url)}"`));assert(html.graph.includes(m.name));
    assert(html.content.includes('不是独立全职、人事在岗或编制核验'));
  }
});

test('Fang Cheng keeps the direct doctoral edge but never gets an unverified shortcut', async () => {
  const p=person('nju-chenpengfei'),m=p.mentors[0],html=await render(p.person_id,'lineage');
  assert.equal(m.name,'方成');assert.equal(m.employment_status,'unknown');
  assert.equal(m.navigation_verified,false);assert.equal(m.quick_link_eligible,false);assert.equal(mentorOfficialUrl(m),'');
  assert.deepEqual(mentorEvents(p,m).map(e=>e.event_id),['nju-chenpengfei-education-1']);
  assert(html.graph.includes('方成'));assert(!html.content.includes('查看导师个人主页'));
});

test('teaching retains exact Level 3 and graduate-year precision in rendered note, not education or graph', async () => {
  assert.deepEqual(person('nju-chengxin').teaching.slice(2).map(t=>t.level),['Level 3, Spring','Level 3, Fall']);
  assert.equal(person('nju-chenpengfei').teaching[1].level,'研究生一年级');
  for (const p of added.filter(p=>p.teaching?.length)) {
    const profile=await render(p.person_id),lineage=await render(p.person_id,'lineage');
    assert(profile.content.includes('公开教学事实'));assert(profile.content.includes('不是本人求学学历'));
    for (const t of p.teaching) {
      assert(profile.content.includes(escape(t.course)));assert(profile.content.includes(escape(t.level)));
      if (t.period) assert(profile.content.includes(escape(t.period)));
      assert(!lineage.graph.includes(escape(t.course)));assert(!lineage.content.includes(escape(t.course)));
    }
  }
});

test('structured-only service honors and projects do not alter UI, graph, filters or counts', async () => {
  const stripped=structuredClone(db);
  for (const p of stripped.people.filter(p=>ids.includes(p.person_id))) {
    for (const key of ['academic_service','honors','research_projects']) delete p[key];
    const original=person(p.person_id);
    for (const stage of ['bachelor','master','doctor']) assert.deepEqual(stages(p,stage),stages(original,stage));
    for (const mode of ['profile','lineage']) assert.deepEqual(await render(p.person_id,mode,stripped),await render(p.person_id,mode));
  }
  for (const school of ['nju','hnu']) assert.deepEqual(schoolStats(stripped,school),schoolStats(db,school));
});

test('selected sources and publication links retain distinct publisher verification boundaries', async () => {
  assert.equal(added.flatMap(p=>p.publications).filter(p=>p.individual_article_link_verified).length,3);
  for (const p of added) {
    assert.equal(officialProfileUrl(p),p.official_url);
    const html=(await render(p.person_id)).content;
    for (const pub of p.publications) {
      assert(html.includes(escape(pub.title)));assert(html.includes(escape(pub.link_status_label)));
      if (p.school_id==='hnu') {assert.equal(pub.doi,null);assert.equal(pub.individual_article_link_verified,false);assert.equal(pub.link_status,'official_publication_list_only')}
    }
  }
});

test('teaching, candidate and independent-array mutations cannot fabricate a degree or mentor', () => {
  for (const original of added) {
    const p=structuredClone(original);
    p.pending_education_candidates=[{event_id:'unreviewed',degree:'博士',event_kind:'degree',degree_awarded:true,region:'overseas',institution:'Candidate-only sentinel'}];
    for (const key of ['academic_service','honors','research_projects','teaching']) p[key]=[{name:'Unreviewed mentor sentinel',degree:'博士',event_kind:'degree',degree_awarded:true,region:'overseas'}];
    for (const stage of ['bachelor','master','doctor']) assert.deepEqual(stages(p,stage),stages(original,stage));
    assert.equal(matches(p,{doctor:'overseas'},db.org_units),false);
    assert.deepEqual(p.mentors,original.mentors);
  }
});

test('actual selected profile and lineage rendering never mutates canonical input', async () => {
  const before=JSON.stringify(db);
  for (const p of added) {
    await render(p.person_id);await render(p.person_id,'lineage');
    const entry=db.rosters.entries.find(e=>e.source_person_id===p.person_id),main={innerHTML:''};
    renderRosters(db,main,entry.id,p.school_id);
    assert(main.innerHTML.includes(p.name));
  }
  assert.equal(JSON.stringify(db),before);
});

test('six separately reviewed roster identities expose matched profile routes without claiming current employment', () => {
  const sourceHashes={nju:'141e34961e4b39300cd05e1e32fe4de0af5676e20601153d0e1d6d8ff50fe471',hnu:'7ad107b353fa4da5a549cfbe89e14fbb3ec6500014d0c6d782abda41b5253a54'};
  const reviewHashes={nju:'1b7966ee9adeeb3db35592723f5db4c1d3ca12bfde62655ccd4612d4122e4147',hnu:'746275376c7b6df96457535630128e0923246417a9ff43a0841ae5d3093a83b7'};
  for (const p of added) {
    const e=db.rosters.entries.find(e=>e.source_person_id===p.person_id), main={innerHTML:''};
    assert.equal(e.profile_identity_verified,true);assert.equal(e.verified_person_id,p.person_id);
    assert.equal(e.name,p.name);assert.equal(e.school_id,p.school_id);assert.equal(e.department_id,p.department_id);
    assert.equal(e.official_profile_url,p.official_url);
    assert.equal(e.profile_identity_evidence.reviewed_source_sha256,sourceHashes[p.school_id]);
    assert.equal(e.profile_identity_evidence.independent_review_sha256,reviewHashes[p.school_id]);
    assert.equal(rosterIdentityMatched(db,e),true);
    assert.equal(rosterStatusLabel(db,e),'身份已关联人物档案（任职状态另核）');
    renderRosters(db,main,e.id,p.school_id);
    assert(main.innerHTML.includes(`#/person/${p.person_id}`));
    assert(main.innerHTML.includes('任职状态另核'));
  }
});


test('verbatim research-field names retain source order and provenance in profile and directory table', async () => {
  const directories = {};
  for (const school of ['nju','hnu']) directories[school]=(await render(school,'directory')).results;
  for (const p of added) {
    const expected=p.research_fields.map(field=>field.name).join('；');
    const sourceIds=[...new Set(p.research_fields.map(field=>field.source_id))];
    assert(expected);assert.equal(p.research_interests,expected);
    assert.deepEqual(p.research_interests_source_ids,sourceIds);
    assert.deepEqual(p.professional_field_provenance.research_interests,sourceIds);
    assert.equal(p.research_interests_derivation,'verbatim_original_research_fields_names_in_source_order_for_existing_consumer');
    const html=(await render(p.person_id)).content;
    assert(html.includes(`<h3>研究方向</h3><p>${escape(expected)}</p>`));
    const row=directories[p.school_id].split('<tr>').find(row=>row.includes(`#/person/${p.person_id}"`));
    assert(row,p.person_id);assert(row.includes(`<small>${escape(expected)}</small>`));
    assert(!row.includes('研究方向待补录'));
  }
});
