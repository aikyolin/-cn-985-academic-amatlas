import {test} from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {execFileSync} from 'node:child_process';
import {fileURLToPath} from 'node:url';
import {UNIVERSITIES} from '../site/universities.js';
import {stages,matches,mentorEvent,mentorProfileRoute,mentorOfficialUrl,schoolStats,schoolCampuses,normalizeSchoolFilters,routeSchool,escapeHtml} from '../site/model.js';

const read=path=>JSON.parse(fs.readFileSync(new URL(path,import.meta.url)));
const db=read('../data/atlas.json'),rosters=read('../data/rosters.json'),progress=read('../progress/breadth-wave1-coverage.json'),site=read('../site/atlas.json');
db.rosters=rosters;db.exports=site.exports;
const original=JSON.stringify(db);
const FIELDS=['education','appointments','mentors','committee_members','publications','sources','research_collaborators','pending_mentor_candidates','pending_mentors','project_guidance'];
const counts=rows=>Object.fromEntries(FIELDS.map(k=>[k,rows.reduce((n,p)=>n+(p[k]||[]).length,0)]));
const awards=rows=>[true,false,null].map(v=>rows.flatMap(p=>p.education||[]).filter(e=>e.degree_awarded===v).length);
// Exact audited first-wave IDs: later people at the same schools are not part of this historical sample.
const BATCHES=[
  {sid:'fdu',department:'fdu-icmne',ids:['fdu-bianlifeng','fdu-zengxuan','fdu-zengxiaoyang'],fields:[9,17,0,3,10],awards:[2,6,1],sha:'92f100f58a2774fd622c6da5e12797d8f360ee6cbb12e5153b7d1fdb9215e7d8',review:'e75c8f2922fd3c53856ff3ab9cfc6030cf9001ec72717efb5d9fe2927b6bd942'},
  {sid:'nju',department:'nju-cs',ids:['nju-lvjian','nju-tantieniu','nju-zhouzhihua'],fields:[10,7,1,3,16],awards:[8,1,1],sha:'acde5b544752822bd99afdae359073cd8588f3e016c232026af65098012ceece',review:'c40016a6924b74332eeaa325c994ecc0b1b0d5bf43d8e92da36e09488aecf883'},
  {sid:'ustc',department:'ustc-ic',ids:['ustc-longshibing','ustc-chenglin','ustc-yangshu'],fields:[10,11,1,6,10],awards:[0,2,8],sha:'838f69732426459c4962e6f820acbeaf619e79f7fba4b2f621721fc432cacb00',review:'9696a789cfced2024f8a09e42ce103250df89585545349534130a7621fb4750e'},
  {sid:'buaa',department:'buaa-cs',ids:['buaa-liwei','buaa-zhengzhiming','buaa-qiandepei'],fields:[6,8,0,2,10],awards:[3,1,2],sha:'dbcbaf051fc310be1bd70304e74c66a0d93e25ad9bbf2607e8e113cff5d9ba65',review:'1954fb41ce60bf8fe2358dc6b2fa5224af842dd4cbcefea635bac47c865c41ad'}
].map(b=>({...b,batch:`faculty-batch-${b.sid}-first-001`,roster:`${b.sid}-selected-roster-first-001`}));
const batchIds=new Set(BATCHES.map(b=>b.batch)),rosterIds=new Set(BATCHES.map(b=>b.roster));
const fresh=db.people.filter(p=>batchIds.has(p.data_batch_id));
const person=id=>{const p=fresh.find(p=>p.person_id===id);assert(p,`Missing first-wave person ${id}`);return p};
const source=(p,id)=>{const s=p.sources.find(s=>s.id===id);assert(s,`${p.person_id}: missing source ${id}`);return s};

test('first breadth wave preserves four source hashes and independent reviews, not a complete-school claim',()=>{
  assert.equal(progress.baseline_commit,'1604775583c7ea6634d3242d7c8fb72689d74b4a');
  assert.equal(progress.source_references.length,4);assert.equal(progress.coverage_complete,false);assert.equal(progress.fields_complete,false);
  assert(progress.scope.includes('各3份部分职业资料'));assert(progress.scope.includes('不代表全校全院或全部职级完整'));
  for(const b of BATCHES){
    const file=b.batch+'.json',ref=progress.source_references.find(s=>s.file===file);assert(ref);
    assert.equal(ref.sha256,b.sha);assert.equal(ref.independent_review_file,b.batch+'-independent-review.json');assert.equal(ref.independent_review_sha256,b.review);
    for(const batch of [db.profile_batches.find(x=>x.batch_id===b.batch),rosters.batches.find(x=>x.batch_id===b.roster)]){
      assert(batch,b.batch);assert.equal(batch.school_id,b.sid);assert(batch.source_files.some(s=>s.file===file&&s.sha256===b.sha));assert.equal(batch.coverage_complete,false);
    }
    const p=db.profile_batches.find(x=>x.batch_id===b.batch);assert.deepEqual([p.people_count,p.established_professional_profiles,p.pending_profiles,p.complete_profiles],[3,3,0,0]);assert.equal(p.fields_complete,false);
  }
});

test('four exact first batches retain twelve partial profiles, per-batch fields and 13 confirmed,10 nondegree,12 unknown events',()=>{
  assert.equal(fresh.length,12);assert.equal(db.pending_people.filter(p=>batchIds.has(p.data_batch_id)).length,0);
  assert.deepEqual([progress.counts.new_schools,progress.counts.new_organization_nodes,progress.counts.new_campuses,progress.counts.source_people,progress.counts.new_professional_profiles,progress.counts.new_pending_profiles,progress.counts.complete_profiles],[4,4,0,12,12,0,0]);
  assert.deepEqual(counts(fresh),progress.counts.source_collections);assert.deepEqual(counts(fresh),progress.counts.effective_global_collection_delta);
  assert.deepEqual(awards(fresh),[13,10,12]);
  const degreeCounts={degree_awarded_true:13,degree_awarded_false:10,degree_awarded_null:12,confirmed_degree_events:13};
  assert.deepEqual(progress.counts.source_degree_counts,degreeCounts);assert.deepEqual(progress.counts.effective_degree_counts,degreeCounts);
  for(const b of BATCHES){const ps=fresh.filter(p=>p.data_batch_id===b.batch);assert.deepEqual(ps.map(p=>p.person_id).sort(),[...b.ids].sort());assert.deepEqual(['education','appointments','mentors','publications','sources'].map(k=>counts(ps)[k]),b.fields);assert.deepEqual(awards(ps),b.awards)}
  for(const p of fresh){assert.equal(p.profile_status,'partial_professional_source_checked');assert.equal(p.fields_complete,false);assert.equal(p.detail_count_eligible,true);assert.equal(p.established_professional_count_eligible,true);assert.equal(p.complete_profile_count_eligible,false);assert(p.profile_coverage_label.includes('部分'))}
  assert(fresh.flatMap(p=>p.education).filter(e=>e.degree_awarded===true).every(e=>e.event_kind==='degree'));
  assert(fresh.flatMap(p=>p.education).filter(e=>e.degree_awarded===false).every(e=>e.event_kind!=='degree'));
});

test('historical first-wave projection stays336 plus51 while live counts remain derived from the current database',()=>{
  const h=progress.counts.projection;
  assert.deepEqual([h.published_schools,h.professional_records,h.pending_records,h.organization_nodes,h.roster_totals.record_count,h.roster_totals.raw_observation_count],[9,336,51,90,1469,1507]);
  assert.deepEqual(h.collections,{education:1016,appointments:1237,mentors:133,committee_members:9,publications:667,sources:1296,research_collaborators:4,pending_mentor_candidates:12,pending_mentors:7,project_guidance:1});
  assert.deepEqual(h.degree_counts,{degree_awarded_true:537,degree_awarded_false:188,degree_awarded_null:291,confirmed_degree_events:537});
  const all=[...db.people,...db.pending_people];assert.equal(new Set(all.map(p=>p.person_id)).size,all.length);
  for(const u of db.institutions){const stats=schoolStats(db,u.id),same=rows=>rows.filter(p=>p.school_id===u.id).length;assert.equal(stats.people,same(db.people));assert.equal(stats.pending,same(db.pending_people));assert.equal(stats.rosters,same(rosters.entries));assert.equal(stats.status,stats.people?'部分收录':stats.hasData?'仅目录／资料待核':'待收录')}
  assert.equal(rosters.totals.record_count,rosters.entries.length);assert.equal(rosters.totals.raw_observation_count,rosters.source_observations.length);
});

test('twelve selected roster observations retain explicit school/department scope and never imply all-visible coverage',()=>{
  const entries=rosters.entries.filter(r=>rosterIds.has(r.batch_id)),observations=rosters.source_observations.filter(r=>rosterIds.has(r.batch_id)),coverage=rosters.coverage.filter(r=>rosterIds.has(r.batch_id));
  assert.deepEqual([entries.length,observations.length,coverage.length],[12,12,4]);
  for(const b of BATCHES){
    const rows=entries.filter(e=>e.batch_id===b.roster),obs=observations.filter(e=>e.batch_id===b.roster),c=coverage.find(c=>c.batch_id===b.roster),batch=rosters.batches.find(c=>c.batch_id===b.roster);
    assert.deepEqual([rows.length,obs.length,batch.record_count,batch.raw_observation_count,c.selected_observation_count],[3,3,3,3,3]);assert.equal(batch.count_scope,'selected_subset_only');
    assert.equal(c.school_id,b.sid);assert.equal(c.organization_id,b.department);assert.equal(c.coverage_complete,false);assert.equal(c.all_visible_entries_captured,false);assert.equal(c.count_scope,'selected_subset_only');assert.equal(c.full_source_visible_name_count,null);
    for(const e of rows){assert.equal(e.school_id,b.sid);assert.equal(e.organization_id,b.department);assert.equal(e.department_id,b.department);assert.equal(e.campus_id,null);assert.deepEqual(e.campus_ids,[]);assert.equal(e.profile_identity_verified,false);assert.equal(e.verified_person_id,null);assert.equal(person(e.source_person_id).roster_entry_id,e.id);assert.equal(person(e.source_person_id).department_id,e.organization_id)}
    for(const o of obs){assert.equal(o.school_id,b.sid);assert.equal(o.organization_id,b.department)}
  }
});

let serial=0;
async function app(hash='#/'){
  const d=structuredClone(db);d.build_id='breadth-wave1-read-only';d.rosters.build_id=d.build_id;
  const nodes=new Map(),listeners={},node=k=>{if(!nodes.has(k))nodes.set(k,{innerHTML:'',textContent:'',value:'',style:{},events:{},dataset:{height:'320'},clientWidth:960,querySelector:node,addEventListener(t,f){this.events[t]=f},click(){this.onclick?.()}});return nodes.get(k)};
  globalThis.document={querySelector:node,querySelectorAll:()=>[],getElementById:id=>node('#'+id)};globalThis.location={hash};globalThis.window={scrollTo(){},addEventListener(t,f){listeners[t]=f}};
  globalThis.fetch=async p=>({ok:true,json:async()=>structuredClone(String(p).startsWith('atlas.json')?d:d.rosters)});
  await import('../site/app.js?breadth-wave1-real='+serial++);assert(!node('#main').innerHTML.includes('资料暂未加载'));
  return {node,navigate(hash){location.hash=hash;listeners.hashchange()}};
}

test('national cards use live school counts: first-wave history is9 plus30, not a cap on later schools',async()=>{
  assert.equal(UNIVERSITIES.length,39);assert.equal(39-progress.counts.projection.published_schools,30);
  const ui=await app(),published=UNIVERSITIES.filter(u=>schoolStats(db,u.id).published).length,directory=UNIVERSITIES.filter(u=>schoolStats(db,u.id).hasData&&!schoolStats(db,u.id).published).length;
  assert(ui.node('#main').innerHTML.includes(`目前${published}所学校有部分人物资料`));assert(ui.node('#main').innerHTML.includes(`其余${39-published-directory}所待收录`));
  const cards=ui.node('#school-grid').innerHTML.match(/<article class="school-card[\s\S]*?<\/article>/g)||[];assert.equal(cards.length,39);
  for(const b of BATCHES){const card=cards.find(c=>c.includes(`href="#/school/${b.sid}"`));assert(card);assert(card.includes('部分收录'));assert(card.includes(`${schoolStats(db,b.sid).people} 份人物资料`))}
});

test('new schools with unassigned campuses keep their own units, people, breadcrumbs and roster filters',async()=>{
  const ui=await app();
  for(const b of BATCHES){
    const u=db.org_units.find(u=>u.id===b.department);assert(u);assert.equal(u.school_id,b.sid);assert.equal(u.parent_id,b.sid);assert.deepEqual(u.campus_ids,[]);
    ui.navigate('#/school/'+b.sid);assert(ui.node('#sidebar').innerHTML.includes('#/org/'+b.department));assert(!ui.node('#sidebar').innerHTML.includes('#/campus/harbin'));
    if(!schoolCampuses(db,b.sid).length){assert(ui.node('#main').innerHTML.includes('本批资料未单列校区归属'));assert(!ui.node('#sidebar').innerHTML.includes('campus-nav'))}
    ui.navigate('#/org/'+b.department);assert(ui.node('#excel').innerHTML.includes(`exports/${b.department}.xlsx`));
    for(const p of fresh.filter(p=>p.school_id===b.sid)){assert.deepEqual(p.campus_ids,[]);assert.equal(p.campus,null);assert.equal(p.department_id,b.department);assert(ui.node('#results').innerHTML.includes(escapeHtml(p.name)))}
    for(const p of fresh.filter(p=>p.school_id!==b.sid))assert(!ui.node('#results').innerHTML.includes(`#/person/${p.person_id}`));
    for(const pid of b.ids){ui.navigate('#/person/'+pid);assert(ui.node('#main').innerHTML.includes(`href="#/school/${b.sid}"`));assert(ui.node('#main').innerHTML.includes(`href="#/org/${b.department}"`));assert(ui.node('#main').innerHTML.includes('校区未单列／待核实'));assert(!ui.node('#main').innerHTML.includes('哈尔滨工业大学'))}
    ui.navigate('#/rosters?school='+b.sid);for(const p of fresh.filter(p=>p.school_id===b.sid))assert(ui.node('#roster-results').innerHTML.includes(escapeHtml(p.name)));for(const p of fresh.filter(p=>p.school_id!==b.sid))assert(!ui.node('#roster-results').innerHTML.includes(p.roster_entry_id));
    assert.deepEqual(normalizeSchoolFilters(db,{school:b.sid,campus:'harbin',org:'hit-aerospace'}),{school:b.sid,campus:'',org:''});
    assert.equal(db.people.filter(p=>matches(p,{school:b.sid,org:b.department},db.org_units)).length,db.people.filter(p=>p.school_id===b.sid&&p.department_id===b.department).length);
  }
  assert.equal(routeSchool(db,'campus','harbin'),'hit');
});

test('both direct doctoral relationships bind exactly their reviewed events without fabricating supervision dates',()=>{
  const edges=fresh.flatMap(p=>p.mentors.map(m=>[p,m]));assert.equal(edges.length,2);assert.deepEqual(progress.counts.direct_guidance_types,{doctoral_advisor:2});
  assert.deepEqual(edges.map(([p,m])=>[p.person_id,m.name,m.education_event_id]),[['nju-lvjian','徐家福','nju-lvjian-education-3'],['ustc-yangshu','Kevin J. Chen','ustc-yangshu-education-2']]);
  for(const [p,m] of edges){assert.equal(m.relationship_kind,'doctoral_advisor');assert.equal(m.relationship_status,'verified_direct_statement');assert.equal(m.include_in_mentorship_graph,true);assert.equal(m.include_in_verified_mentor_count,true);assert.equal(m.start,null);assert.equal(m.end,null);assert.equal(mentorEvent(p,m).event_id,m.education_event_id);assert.equal(source(p,m.source_id).url,m.source_url);assert.equal(source(p,m.profile_source_id).url,m.profile_source_url)}
});

test('Xu Jiafu remains deceased with relationship and obituary evidence but no current-employment shortcut',async()=>{
  const p=person('nju-lvjian'),m=p.mentors[0];assert.equal(m.employment_status,'deceased');assert.equal(m.navigation_verified,false);assert.equal(m.quick_link_eligible,false);assert.equal(m.person_id,null);
  assert.equal(m.official_url,'https://www.nju.edu.cn/info/3181/60231.htm');assert.equal(mentorOfficialUrl(m),'');assert.equal(mentorProfileRoute(m,db.people),'');assert(m.employment_status_note.includes('2018年逝世'));
  const ui=await app('#/person/'+p.person_id+'/lineage'),html=ui.node('#profile-content').innerHTML;assert(html.includes('任职状态：已故'));assert(html.includes(escapeHtml(m.source_url)));assert(html.includes(escapeHtml(m.profile_source_url)));assert(!html.includes('查看导师个人主页'));assert(!html.includes('查看本库个人档案'));assert(ui.node('#mind-stage').innerHTML.includes('1条已收录关系'));
});

test('Yang Shu direct supervision proof does not turn a labelled doctorate into a confirmed award',async()=>{
  const p=person('ustc-yangshu'),e=p.education[1],m=p.mentors[0];assert.deepEqual(p.education.map(e=>e.degree_awarded),[null,null,false]);assert.equal(e.institution,'香港科技大学');assert.equal(e.degree,'博士');assert.equal(e.degree_awarded,null);assert.equal(mentorEvent(p,m),e);
  assert(m.evidence_note.includes('Student Supervision > Ph.D students graduated'));assert(m.evidence_note.includes('Shu Yang2014'));assert(m.evidence_note.includes('非一般团队名单'));
  assert.equal(stages(p,'doctor').length,0);assert(!matches(p,{doctor:'hmt'}));assert(matches(p,{doctor:'not_recorded'}));assert.equal(m.employment_status,'active_officially_listed');assert.equal(m.quick_link_eligible,true);assert.equal(m.navigation_verified,true);assert.equal(mentorOfficialUrl(m),'https://eekjchen.people.ust.hk/people/');assert.equal(mentorProfileRoute(m,db.people),'');
  const ui=await app('#/person/'+p.person_id+'/lineage');assert(ui.node('#profile-content').innerHTML.includes('查看导师个人主页'));assert(ui.node('#mind-stage').innerHTML.includes('1条已收录关系'));
  for(const q of fresh.filter(p=>p.school_id==='ustc')){assert.equal(stages(q,'doctor').length,0);assert.equal(stages(q,'master').length,0);assert.equal(stages(q,'bachelor').length,0)}
});

test('Qian Depei keeps the confirmed masters and German visit without inferring a doctorate or undergraduate award',()=>{
  const p=person('buaa-qiandepei');assert.deepEqual(p.education.map(e=>e.degree_awarded),[null,true,false]);assert.equal(p.education[1].institution,'北德州立大学');assert.equal(p.education[1].end,'1984-05');assert.equal(p.education[2].event_kind,'visiting_research');assert.equal(p.education[2].institution,'汉诺威大学');
  assert(!p.education.some(e=>e.degree==='博士'));assert(p.unknowns.some(s=>s.includes('不能因博士生导师身份补博士')));assert.equal(stages(p,'bachelor').length,0);assert.equal(stages(p,'doctor').length,0);assert.equal(stages(p,'master').length,1);assert(matches(p,{master:'overseas',master_continent:'north_america'}));assert(!matches(p,{doctor:'overseas'}));assert(!matches(p,{continent:'europe'}));assert.deepEqual(p.mentors,[]);
});

test('FDU inverted lecturer dates remain unknown with original conflict, and postdoctoral work does not confirm the doctorate',async()=>{
  const p=person('fdu-zengxiaoyang'),a=p.appointments.find(a=>a.status==='historical_conflicting_dates');assert(a);assert.equal(a.title,'讲师');assert.equal(a.start,null);assert.equal(a.end,null);assert.equal(a.current,false);assert.equal(a.source_reported_period,'2003-04–2003-01');assert(a.note.includes('不自动修成12月'));assert.equal(source(p,a.source_id).url,a.source_url);
  assert.deepEqual(p.education.map(e=>e.degree_awarded),[null,false]);assert.equal(stages(p,'doctor').length,0);assert(!matches(p,{doctor:'mainland'}));assert(matches(p,{doctor:'not_recorded'}));assert.equal(p.education[1].event_kind,'postdoctoral_research');
  const html=(await app('#/person/'+p.person_id)).node('#profile-content').innerHTML;assert(html.includes(escapeHtml(a.note)));assert(html.includes('起始时间未披露 — 结束时间未披露'));
  const b=person('fdu-bianlifeng');assert.equal(stages(b,'doctor')[0].institution,'中国科学院半导体研究所');assert(!matches(b,{doctor:'overseas'}));
});

const BOOK_LABEL='学术著作（非期刊或会议论文）';
const BOOK_STATUS={official_profile_mentions_book_only:'官方个人页仅提及著作，未核出版商落地页或全文。',official_author_book_metadata_verified:'作者官方职业页面的著作书目元数据已核，不表示出版商页面或全文已读。',official_publication_list_only:'仅官方精选书目已核，未逐篇核实出版社落地页或全文。'};
test('four books retain distinct metadata evidence levels, original titles and no inferred DOI or complete publication corpus',async()=>{
  const pubs=fresh.flatMap(p=>p.publications),books=pubs.filter(p=>p.type==='book');assert.equal(books.length,4);
  assert.deepEqual(Object.fromEntries(['journal_article','book','conference_paper'].map(type=>[type,pubs.filter(p=>p.type===type).length])),{journal_article:8,book:4,conference_paper:2});assert.deepEqual(progress.counts.publication_types,{journal_article:8,book:4,conference_paper:2});
  assert.deepEqual(books.map(b=>b.title),['软件自动化','机器学习','机器学习理论导引','数理逻辑——基本原理与形式演算']);
  assert.deepEqual(books.map(b=>b.link_status),['official_profile_mentions_book_only','official_author_book_metadata_verified','official_author_book_metadata_verified','official_publication_list_only']);
  for(const p of fresh.filter(p=>p.publications.some(b=>b.type==='book'))){const html=(await app('#/person/'+p.person_id)).node('#profile-content').innerHTML;for(const b of p.publications.filter(b=>b.type==='book')){assert.equal(b.type_label,BOOK_LABEL);assert.equal(b.link_status_label,BOOK_STATUS[b.link_status]);assert.equal(b.doi,null);assert.notEqual(b.individual_article_link_verified,true);source(p,b.source_id);assert(html.includes(escapeHtml(b.title)));assert(html.includes(BOOK_LABEL));assert(html.includes(b.link_status_label))}assert(html.includes('不代表完整成果清单'))}
  assert.equal(books[0].year,null);assert.equal(books[0].venue,null);assert.equal(books[2].alternate_title_on_book_page,'机器学习理论研究导引');assert(books[2].note.includes('不另造第二本书'));
});

let exported;
function tables(){
  if(exported)return exported;
  // Pure in-memory table/manifest functions only; prohibit workbooks and build entrypoints.
  const code=`import json,sys,copy\nfrom unittest import mock\nsys.path.insert(0,'scripts')\nimport build\nd=json.load(open('data/atlas.json')); original=copy.deepcopy(d)\nbatches=set(${JSON.stringify(BATCHES.map(b=>b.batch))})\nfresh=[p for p in d['people'] if p.get('data_batch_id') in batches]\nwith mock.patch.object(build,'Workbook',side_effect=AssertionError('No XLSX allowed')), mock.patch.object(build,'build',side_effect=AssertionError('No build allowed')):\n build.validate(d)\n manifest=build.department_exports(d)\n subset=copy.deepcopy(d); subset['people']=fresh\n selected_manifest=build.department_exports(subset)\n out={dept:dict(build.department_tables([p for p in fresh if p['department_id']==dept],d['updated_at'],d['institutions'])) for dept in sorted({p['department_id'] for p in fresh})}\nassert d==original\nprint(json.dumps({'tables':out,'manifest':manifest,'selected_manifest':selected_manifest},ensure_ascii=False))`;
  exported=JSON.parse(execFileSync('python',['-B','-c',code],{cwd:fileURLToPath(new URL('..',import.meta.url)),encoding:'utf8'}));return exported;
}

test('department manifests keep three selected profiles per real unit and live export totals match current school/department scope',()=>{
  const out=tables();assert.equal(out.selected_manifest.length,4);
  for(const b of BATCHES){const selected=out.selected_manifest.find(e=>e.department_id===b.department),live=out.manifest.find(e=>e.department_id===b.department),snapshot=site.exports.find(e=>e.department_id===b.department);assert(selected);assert(live);assert(snapshot);assert.equal(selected.people_count,3);assert.equal(selected.school_id,b.sid);assert.equal(selected.path,`exports/${b.department}.xlsx`);assert.equal(live.people_count,db.people.filter(p=>p.department_id===b.department&&p.school_id===b.sid).length);assert.deepEqual(snapshot,live);
    const t=out.tables[b.department];assert.deepEqual(Object.keys(t),['总览','经历','导师','论文','来源']);assert.equal(t['总览'].length,4);for(const row of t['总览'].slice(1)){assert.equal(row[1],'校区未标注');assert.equal(row[6],'分批核实资料，不是完整名录')}for(const rows of Object.values(t))for(const row of rows.slice(1))assert.deepEqual(row.slice(-2),[b.sid,db.institutions.find(s=>s.id===b.sid).official_name]);
  }
});

test('in-memory Excel rows preserve book labels and raw statuses, deceased no-shortcut, direct mentor evidence and null awards/dates',()=>{
  const out=tables().tables;
  for(const p of fresh)for(const b of p.publications.filter(b=>b.type==='book')){const row=out[p.department_id]['论文'].find(r=>r[0]===p.name&&r[1]===b.title);assert(row);assert.equal(row[5],b.type_label+'；book');assert.equal(row[8],b.link_status_label+'；'+b.link_status)}
  const deceased=out['nju-cs']['导师'].find(r=>r[1]==='徐家福');assert(deceased);assert.equal(deceased[5],'deceased');assert.equal(deceased[7],'');assert.equal(deceased[8],person('nju-lvjian').mentors[0].source_url);assert.equal(deceased[9],'https://www.nju.edu.cn/info/3181/60231.htm');
  const active=out['ustc-ic']['导师'].find(r=>r[1]==='Kevin J. Chen');assert(active);assert.equal(active[7],person('ustc-yangshu').mentors[0].official_url);
  const doctor=out['ustc-ic']['经历'].find(r=>r[0]==='杨树'&&r[2]==='博士');assert(doctor);assert.equal(doctor[11],null);
  const conflict=out['fdu-icmne']['经历'].find(r=>r[0]==='曾晓洋'&&r[2]==='讲师');assert(conflict);assert.deepEqual(conflict.slice(4,6),[null,null]);assert(conflict[14].includes('不自动修成12月'));
  assert.equal(Object.values(out).reduce((n,t)=>n+t['导师'].length-1,0),2);
});

test('all first-wave checks are read-only and preserve every canonical evidence collection in memory',()=>{
  assert.equal(JSON.stringify(db),original);
});
