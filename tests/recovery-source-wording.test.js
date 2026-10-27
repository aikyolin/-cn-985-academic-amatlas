// Actual thin-router wording check; no generator, archive or workbook I/O.
import {test} from 'node:test';
import assert from 'node:assert/strict';
import {readJSONFile} from './atlas-test-io.js';
import {createImmutableCohortRenderer} from './immutable-cohort-renderer.js';
import {stages,mentorEvents} from '../site/model.js';
const db=readJSONFile(new URL('../site/atlas.json',import.meta.url));
const roster=readJSONFile(new URL('../site/rosters.json',import.meta.url));
const renderer=createImmutableCohortRenderer({db,roster,fixtureId:'NEW_RECOVERY-source-wording-public-baseline-cohort'});
const person=id=>{const p=db.people.find(p=>p.person_id===id);assert(p,id);return p;};
test('actual about distinguishes source statements from original-document certification',async()=>{
 const page=await renderer.render('#/about');const html=page('#main').innerHTML;
 assert(html.includes('来源明确记载本人获授或持有学位'));
 assert(html.includes('不表示本轮独立证书认证或重新读取原网页'));
 assert(html.includes('关系记载不等同于学位论文原件核验，证据类型与限制以各条来源说明为准'));
});
test('actual directory exposes source-qualified degree-filter wording',async()=>{
 const page=await renderer.render('#/people');const html=page('#main').innerHTML;
 assert(html.includes('学历筛选仅显示来源明确记载的学位'));
 assert(!html.includes('仅确证授位参与学历筛选'));
});
test('source-reported true degree still participates in unchanged filter',async()=>{
 const p=person('hit-zhaotiejun');assert(p.education.some(e=>e.degree_awarded===true));
 assert(['bachelor','master','doctor'].some(type=>stages(p,type).length));
 const page=await renderer.render('#/person/'+p.person_id);assert(page('#profile-content').innerHTML.includes('求学与研究经历'));
});
test('unknown degree event keeps unknown and actual visible non-filter label',async()=>{
 const p=person('hit-maxing');assert(p.education.some(e=>e.degree_awarded===null));
 const page=await renderer.render('#/person/'+p.person_id);assert(page('#profile-content').innerHTML.includes('本事件未明确记载获授学位，不参与学历筛选'));
});
test('actual lineage states source-reported relation and retained-summary limit',async()=>{
 const p=person('hit-lihuan');assert(p.mentors.length);
 const page=await renderer.render('#/person/'+p.person_id+'/lineage');const html=page('#profile-content').innerHTML;
 assert(html.includes('来源记载的导师关系'));
 assert(html.includes('关系可能依据保留的来源摘要，不等同于论文原件认证'));
 assert(html.includes('阶段未明确时不推定学位阶段'));
 for(const m of p.mentors)assert(html.includes(m.name));
 assert.deepEqual(mentorEvents(p,{education_stage:null,education_event_id:null}),[]);
});

test('actual profile labels positive source notes and unresolved questions together',async()=>{
 const p=person('hit-zhaotiejun');const page=await renderer.render('#/person/'+p.person_id);
 const html=page('#profile-content').innerHTML;
 assert(html.includes('<h3>来源说明与待核事项</h3>'));
 assert(!html.includes('<h3>核验与缺项</h3>'));
 for(const note of p.unknowns)assert(html.includes(note.replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;')));
});
