// Six source-reviewed profiles; scoped real-router tests, no binary I/O.
import {test} from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {readJSONFile} from './atlas-test-io.js';
import {createImmutableCohortRenderer} from './immutable-cohort-renderer.js';
import {stages,mentorEvents,mentorProfileRoute,mentorOfficialUrl} from '../site/model.js';
const raw=readFileSync(new URL('./fixtures/hit-energy6-source-mapping.json',import.meta.url));
assert.equal(createHash('sha256').update(raw).digest('hex'),'40bc1424b511fbf76fbddcb664023c1067a3fbd2064a8ae9b6dc70304c41d6f0');
const fixed=JSON.parse(raw),ids=['hit-wanjie','hit-lanchaohui','hit-keyangguang','hit-zhaowenke','hit-wangwei36-energy','hit-wanglihit-energy'];
const db=readJSONFile(new URL('../site/atlas.json',import.meta.url)),roster=readJSONFile(new URL('../site/rosters.json',import.meta.url));
const renderer=createImmutableCohortRenderer({db,roster,fixtureId:'HIT_ENERGY6_SOURCE_REVIEWED_20261028'});
const esc=s=>String(s).replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;').replaceAll('"','&quot;').replaceAll("'",'&#39;');
const html=p=>Object.values(p.snapshot).map(v=>v.innerHTML).join('\n');
const visible=(s,v,label)=>{if(typeof v==='string'&&v)assert(s.includes(esc(v)),label);};
const actual=id=>{const rows=db.people.filter(p=>p.person_id===id);assert.equal(rows.length,1);return rows[0];};
const content=p=>[...(p.unknowns||[]),...(p.appointments||[]).map(x=>x.note||''),...(p.research_collaborators||[]).map(x=>x.description||'')].join('\n');
test('six exact identities append to frozen1151, without inaccessible profiles or new units',()=>{
 assert.equal(db.people.length,1157);assert.equal(db.pending_people.length,84);assert.deepEqual(fixed.people.map(p=>p.person_id),ids);assert.deepEqual(db.people.slice(1151),fixed.people);assert.deepEqual(db.profile_batches.slice(-fixed.profile_batches.length),fixed.profile_batches);
 for(const p of fixed.people){assert.equal(p.school_id,'hit');assert.equal(p.department_id,'hit-energy');assert.deepEqual(p.campus_ids,['harbin']);}
 for(const id of ['hit-luoyuxi','hit-zhangshuai','hit-epeng'])assert(!db.people.some(p=>p.person_id===id));
});
test('fourteen source education records retain 3 awarded, 2 nonaward and 9 unknown',()=>{
 const events=fixed.people.flatMap(p=>p.education);assert.equal(events.length,14);assert.deepEqual([true,false,null].map(v=>events.filter(e=>e.degree_awarded===v).length),[3,2,9]);
 assert.deepEqual(fixed.people.map(p=>stages(actual(p.person_id),'doctor').length),[0,1,1,1,0,0]);
 for(const p of fixed.people){assert.equal(stages(p,'master').length,0);assert.equal(stages(p,'bachelor').length,0);}
 for(const e of events){assert(Object.hasOwn(e,'degree_awarded_date'));assert.equal(e.degree_awarded_date,null);}
});
test('all source date presence, type, value and order remain exact',()=>{
 for(const p of fixed.people)for(const table of ['education','appointments','mentors','publications','teaching'])for(const [i,row]of(p[table]||[]).entries()){
  const got=actual(p.person_id)[table][i];const keys=new Set([...Object.keys(row),...Object.keys(got)].filter(k=>/(date|year|month|start|end|period)/i.test(k)));
  for(const k of keys){assert.equal(Object.hasOwn(got,k),Object.hasOwn(row,k));assert.deepEqual(got[k],row[k]);}
 }
 assert.equal(fixed.people.reduce((n,p)=>n+p.appointments.length,0),20);assert.equal(fixed.people.reduce((n,p)=>n+p.publications.length,0),12);
});
test('Wanjie composite careers and author order remain unsplit and not translator ranking',()=>{
 const p=actual(ids[0]);assert.equal(p.appointments.length,4);assert.equal(p.mentors.length,0);
 assert.deepEqual(p.appointments.map(a=>a.title),['助理研究员（博士后）/硕士生导师','研究助理（兼职）','助理研究员、副研究员','研究员/硕士生导师&博士生导师']);
 for(const e of [...p.education,...p.appointments]){assert.equal(e.start,null);assert.equal(e.end,null);}
 assert.deepEqual(p.publications.map(w=>[w.year,w.author_order_as_source]),[[2020,1],[2025,2]]);
 assert.deepEqual(p.publications.map(w=>w.type_label),['学术专著','学术译著']);
 for(const w of p.publications){assert.equal(w.publisher,'科学出版社');assert.equal(w.isbn,null);assert.equal(w.doi,null);assert(w.note.includes('作者排序'));assert(!w.note.includes('第二译者'));}
});
test('Lan doctoral guidance and Ke postdoctoral guidance retain distinct exact stage bindings and no navigation',()=>{
 const lan=actual(ids[1]),ke=actual(ids[2]);assert.equal(lan.mentors.length,1);assert.equal(ke.mentors.length,1);
 const lm=lan.mentors[0],km=ke.mentors[0];assert.equal(lm.name,'胡希伟');assert.equal(km.name,'陆全明');
 assert.deepEqual(mentorEvents(lan,lm).map(e=>e.event_id),['hit-lanchaohui-education-1']);
 assert.equal(km.education_event_id,null);assert.equal(km.education_stage,'博士后');assert.equal(km.related_event_id,'hit-keyangguang-career-3');assert.equal(km.include_in_degree_mentorship_graph,false);
 assert.deepEqual(mentorEvents(ke,km).map(e=>e.event_id),['hit-keyangguang-career-3']);
 for(const p of fixed.people)for(const m of p.mentors){assert.equal(mentorProfileRoute(m,db.people),'');assert.equal(mentorOfficialUrl(m),'');assert.equal(m.person_id,null);assert.equal(m.employment_status,'unknown');assert.equal(m.formal_dissertation_advisor_verified,null);}
 assert.equal(ke.education[1].institution,null);assert.equal(ke.education[1].field,null);assert.equal(ke.education[1].degree_awarded,false);
 assert.equal(ke.appointments[2].start,'2020-05');assert.equal(ke.education[0].end,'2020-06');
});
test('five supervision qualifications and seven other professional claims survive visible fields without extra mentor edges',()=>{
 const lan=content(actual(ids[1])),ke=content(actual(ids[2])),zhao=content(actual(ids[3])),wei=content(actual(ids[4])),li=content(actual(ids[5]));
 for(const value of ['博士生导师','Igor Kaganovich','省部级重点实验室PI','哈工大青年拔尖人才选聘计划','兼职研究员','300MeV质子重离子加速器离子源系统负责人'])assert(lan.includes(value),value);
 for(const value of ['博士生导师','新神舟青年学者'])assert(ke.includes(value),value);
 assert(zhao.includes('硕士生导师'));
 for(const value of ['博士生导师','2024-04','硕士生导师','2020-07'])assert(wei.includes(value),value);
 assert(li.includes('Ph.D.'));assert.equal(actual(ids[5]).education.length,0);assert(actual(ids[1]).education[0].note.includes('工学博士'));const qualifications=actual(ids[4]).unknowns.filter(v=>v.includes('来源记载指导资格'));assert.equal(qualifications.length,2);for(const q of qualifications){assert(q.includes('至今'));assert(q.includes('不是独立现职认证'));}
 assert(!actual(ids[1]).mentors.some(m=>m.name==='Igor Kaganovich'));const c=actual(ids[1]).research_collaborators;assert.equal(c.length,1);assert.equal(c[0].name,'Igor Kaganovich');assert.equal(c[0].appointment_event_id,'hit-lanchaohui-career-4');assert.equal(c[0].education_event_id,null);assert.equal(c[0].include_in_mentor_count,false);assert.equal(c[0].include_in_mentorship_graph,false);
});
test('Zhao distinct source titles remain visible and the combined masters-doctorate is one event',()=>{
 const p=actual(ids[3]);assert.equal(p.education.length,2);assert.equal(stages(p,'master').length,0);assert.equal(p.appointments.length,4);
 assert.equal(p.appointments[1].title,'讲师');assert.equal(p.appointments[1].source_title,'助理教授');assert(p.appointments[1].note.includes('助理教授'));assert(p.appointments[1].note.includes('讲师'));
 assert.equal(p.appointments[2].institution,null);
});
test('Wang Wei future bibliography and Wang Li standalone qualification do not become invented publications or schooling',()=>{
 const wei=actual(ids[4]),li=actual(ids[5]);assert.equal(wei.publications[1].year,2027);assert.equal(wei.publications[1].publication_status,'future_bibliographic_year_source_reported_status_unknown');assert(wei.publications[1].note.includes('2027'));assert(wei.publications[1].note.includes('未知'));
 assert.equal(li.education.length,0);assert.equal(li.appointments[0].institution,'哈尔滨工业大学');assert.equal(li.appointments[0].start,'2005-01');assert.equal(li.publications[1].unparsed_date_volume_as_source,'2017,01');assert.equal(li.publications[1].volume_as_source,null);
 for(const p of fixed.people)for(const w of p.publications){assert.equal(w.doi,null);assert.equal(w.publisher_metadata_verified,null);}
});
test('mutations of source uncertainty, year and advisor stage fail fixed-source equality',()=>{
 const a=structuredClone(fixed.people);a[0].education[0].degree_awarded=true;assert.throws(()=>assert.deepEqual(a,fixed.people));
 const b=structuredClone(fixed.people);b[2].mentors[0].education_event_id='hit-keyangguang-education-1';assert.throws(()=>assert.deepEqual(b,fixed.people));
 const c=structuredClone(fixed.people);c[4].publications[1].year=2026;assert.throws(()=>assert.deepEqual(c,fixed.people));
 const d=structuredClone(fixed.people);d[5].education.push({degree:'博士',institution:'哈尔滨工业大学',degree_awarded:true});assert.throws(()=>assert.deepEqual(d,fixed.people));
});
for(const p of fixed.people)test('real profile and all-stage lineage visibly retain source claims: '+p.person_id,async()=>{
 const profile=html(await renderer.render('#/person/'+encodeURIComponent(p.person_id)));const lineage=html(await renderer.render('#/person/'+encodeURIComponent(p.person_id)+'/lineage'));
 visible(profile,p.name,'name');assert(profile.includes('href="'+esc(p.official_url)+'"'));
 for(const [i,v]of p.unknowns.entries())visible(profile,v,p.person_id+'/unknown/'+i);
 for(const table of ['education','appointments','publications','teaching'])for(const [i,row]of(p[table]||[]).entries())visible(profile,row.note,p.person_id+'/'+table+'/'+i+'/note');
 for(const w of p.publications){visible(profile,w.title,'title');if(w.citation_as_source)visible(profile,w.citation_as_source,'full original citation');}
 for(const c of(p.research_collaborators||[])){visible(profile,c.name,'collaborator name');visible(profile,c.description,'collaborator description');visible(profile,c.employment_status_note,'collaborator limitation');}
 for(const m of p.mentors){visible(lineage,m.name,'mentor name');for(const k of ['description','employment_status_note'])visible(lineage,m[k],'mentor/'+k);}
 if(p.person_id===ids[2]){visible(lineage,'陆全明','postdoc guide');assert(lineage.includes('博士后'));}
});
test('all twelve profile/lineage renders use real registered app handler',()=>{
 assert.equal(renderer.stats.renders,12);assert.equal(renderer.stats.imports,1);assert.equal(renderer.stats.handlerRegistrations,1);assert.equal(renderer.stats.handlerCalls,11);
});
