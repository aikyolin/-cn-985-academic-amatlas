// Fixed 22-profile reviewed source projection; real router, no workbook/source-page I/O.
import {test} from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {readJSONFile} from './atlas-test-io.js';
import {createImmutableCohortRenderer} from './immutable-cohort-renderer.js';
import {stages,mentorEvents,mentorProfileRoute,mentorOfficialUrl} from '../site/model.js';
const raw=readFileSync(new URL('./fixtures/hit-energy22-source-mapping.json',import.meta.url));
assert.equal(createHash('sha256').update(raw).digest('hex'),'e0f0332c428b1eb7038cf3f0a1de2029676bb343e0031dca1f9ac161923657bc');
const fixed=JSON.parse(raw),ids=["hit-wangsongtao-energy", "hit-luolei-energy", "hit-chenshaowen", "hit-zhouxun-energy", "hit-duxin-energy", "hit-fengbo", "hit-songyanping", "hit-yujianyang", "hit-huanghongyan", "hit-guzhonghua", "hit-gaojihui", "hit-wxf6046516", "hit-lizhangqi", "hit-zhanglinyao", "hit-liuhui", "hit-burning", "hit-qiuph", "hit-hitzhangyu-energy", "hit-wangzhaolong", "hit-luoxiaoping", "hit-yejianhuai", "hit-yanliming"];
const db=readJSONFile(new URL('../site/atlas.json',import.meta.url)),roster=readJSONFile(new URL('../site/rosters.json',import.meta.url));
const renderer=createImmutableCohortRenderer({db,roster,fixtureId:'HIT_ENERGY22_SOURCE_REVIEWED_20261029'});
const esc=s=>String(s).replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;').replaceAll('"','&quot;').replaceAll("'",'&#39;');
const html=p=>Object.values(p.snapshot).map(v=>v.innerHTML).join('\n');
const visible=(s,v,label)=>{if(typeof v==='string'&&v.trim())assert(s.includes(esc(v.trim())),label);};
const actual=id=>{const rows=db.people.filter(p=>p.person_id===id);assert.equal(rows.length,1);return rows[0];};
const content=p=>[...(p.unknowns||[]),...(p.education||[]).map(x=>x.note||''),...(p.appointments||[]).map(x=>x.note||''),...(p.publications||[]).map(x=>x.note||''),...(p.research_collaborators||[]).map(x=>x.description||'')].join('\n');
test('exact 22 identities, one batch and old1157 boundary',()=>{
 assert.equal(db.people.slice(0,1179).length,1179);assert.equal(db.pending_people.length,84);assert.deepEqual(fixed.people.map(p=>p.person_id),ids);assert.deepEqual(db.people.slice(1157,1179),fixed.people);assert.equal(fixed.profile_batches.length,1);assert.deepEqual(db.profile_batches.slice(225,226),fixed.profile_batches);
 for(const p of fixed.people){assert.equal(p.school_id,'hit');assert.equal(p.department_id,'hit-energy');assert.deepEqual(p.campus_ids,['harbin']);}
});
test('59 education records preserve 7 source awards, 7 non-awards, 45 unknown; 97 source career rows are not certified current jobs',()=>{
 const e=fixed.people.flatMap(p=>p.education);assert.equal(e.length,59);assert.deepEqual([true,false,null].map(v=>e.filter(x=>x.degree_awarded===v).length),[7,7,45]);assert.equal(fixed.people.flatMap(p=>p.appointments).length,97);assert.equal(fixed.people.flatMap(p=>p.mentors).length,6);assert.equal(fixed.people.flatMap(p=>p.publications).length,25);
 for(const p of fixed.people)for(const type of ['bachelor','master','doctor'])for(const x of stages(actual(p.person_id),type)){assert.equal(x.degree_awarded,true);assert.equal(x.event_kind,'degree');}
 for(const p of fixed.people)for(const e of p.education.filter(e=>e.degree_awarded!==true)){const q=structuredClone(p);q.education=[e];for(const type of ['bachelor','master','doctor'])assert.equal(stages(q,type).length,0);}
});
test('nine independent-body reviews and thirteen saved-body semantic reviews stay explicitly distinguished',()=>{
 const saved=fixed.people.filter(p=>p.evidence_tier==='saved_public_body_independent_semantic_review_not_independent_live_full_body');assert.equal(saved.length,13);assert.equal(fixed.people.length-saved.length,9);
 for(const p of fixed.people){assert(p.unknowns.some(v=>v.includes('本条证据层级')));if(saved.includes(p)){assert(p.profile_coverage_label.includes('保存'));assert(p.profile_coverage_label.includes('未另行复读'));}else assert(p.profile_coverage_label.includes('另行复读核对'));}
});
test('all source dates retain exact own-properties, type, precision and order',()=>{
 for(const p of fixed.people){const got=actual(p.person_id);for(const k of ['education','appointments','mentors','publications'])for(const [i,row]of(p[k]||[]).entries()){const a=got[k][i];for(const key of new Set([...Object.keys(row),...Object.keys(a)].filter(x=>/(date|year|month|period|start|end)/i.test(x)))){assert.equal(Object.hasOwn(a,key),Object.hasOwn(row,key));assert.deepEqual(a[key],row[key]);}}}
});
test('Chen two held image transcriptions remain excluded from approved works',()=>{assert.deepEqual(actual('hit-chenshaowen').publications,[]);assert(content(actual('hit-chenshaowen')).includes('作品')||content(actual('hit-chenshaowen')).includes('论文'));});
test('new Wang Songtao and Luo Lei profiles do not retroactively identity-link Yan Han mentors',()=>{
 const yan=actual('hit-yanhan-energy');for(const name of ['王松涛','罗磊']){const m=yan.mentors.find(x=>x.name===name);assert(m);assert.equal(m.person_id,null);assert.equal(mentorProfileRoute(m,db.people),'');assert.equal(mentorOfficialUrl(m),'');}
});
test('all six source guidance relations remain unverified identity navigation and separately linked',()=>{
 for(const p of fixed.people)for(const m of p.mentors){assert.equal(m.person_id,null);assert.equal(m.employment_status,'unknown');assert.equal(m.formal_dissertation_advisor_verified,null);assert.equal(mentorProfileRoute(m,db.people),'');assert.equal(mentorOfficialUrl(m),'');}
 const p=actual('hit-wangzhaolong');assert.equal(p.mentors.length,4);assert.equal(new Set(p.mentors.map(m=>m.education_event_id)).size,4);for(const m of p.mentors)assert(p.education.some(e=>e.event_id===m.education_event_id));
 for(const name of ['郑平','Zhuomin Zhang','Thome John Rechard','黄素逸'])assert(p.mentors.some(m=>m.name===name),name);
 const han=fixed.people.flatMap(p=>p.mentors).filter(m=>m.name==='Han Wanjin');assert.equal(han.length,2);assert.equal(new Set(han.map(m=>m.education_event_id)).size,2);
});
for(const p of fixed.people)test('actual profile/lineage retains full professional notes and source limitations: '+p.person_id,async()=>{
 const a=actual(p.person_id);for(const suffix of ['', '/lineage']){const result=await renderer.render('#/person/'+p.person_id+suffix);const markup=html(result);visible(markup,p.name,p.person_id+'/name');
  if(!suffix){for(const v of p.unknowns||[])visible(markup,v,p.person_id+'/source-note');for(const e of p.education){visible(markup,e.institution,p.person_id+'/institution');visible(markup,e.note,p.person_id+'/education-note');}for(const x of p.appointments)visible(markup,x.note,p.person_id+'/career-note');for(const w of p.publications){visible(markup,w.title,p.person_id+'/work-title');visible(markup,w.note,p.person_id+'/work-note');}for(const x of p.research_collaborators||[]){visible(markup,x.name,p.person_id+'/collaborator');visible(markup,x.description,p.person_id+'/collaborator-limit');}}
  if(suffix==='/lineage')for(const m of p.mentors){visible(markup,m.name,p.person_id+'/mentor');visible(markup,m.description,p.person_id+'/guidance-limit');visible(markup,m.employment_status_note,p.person_id+'/navigation-limit');}
 }
});
