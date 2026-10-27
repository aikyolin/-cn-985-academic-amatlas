// Exact single-event regression; no new source access or workbook I/O.
import {test} from 'node:test';
import assert from 'node:assert/strict';
import {readJSONFile} from './atlas-test-io.js';
import {createImmutableCohortRenderer} from './immutable-cohort-renderer.js';
import {stages,educationStageLabel,matchEducation} from '../site/model.js';
const db=readJSONFile(new URL('../site/atlas.json',import.meta.url));
const rows=db.people.filter(p=>p.person_id==='fdu-xubo');assert.equal(rows.length,1);
const p=rows[0],e=p.education[2];
test('shared bachelor level preserves both source qualifications in one unchanged event',()=>{
 assert.equal(e.event_id,'xu-ba');assert.equal(e.degree,'学士');assert.equal(e.degree_awarded,true);
 assert.deepEqual(e.degrees,['哲学学士','管理学学士']);assert.equal(p.education.filter(x=>x.event_id==='xu-ba').length,1);
 assert.equal(e.start,'2003');assert.equal(e.end,'2007');assert.equal(e.degree_award_date,null);assert.equal(e.degree_award_year,null);
 for(const label of e.degrees)assert(e.note.includes(label));
 assert(stages(p,'bachelor').includes(e));assert.equal(educationStageLabel(e),'学士');
 assert.equal(matchEducation(p,'bachelor','region','not_recorded'),false);
});
test('the regression detects original missing level and does not promote unknown or false awards',()=>{
 for(const award of [null,false]){const q=structuredClone(p);q.education[2].degree_awarded=award;assert(!stages(q,'bachelor').includes(q.education[2]));}
 const q=structuredClone(p);q.education[2].degree=null;assert(!stages(q,'bachelor').includes(q.education[2]));assert.equal(educationStageLabel(q.education[2]),'研究经历');
});
test('actual profile and lineage retain dual bachelor labels after exact normalization',async()=>{
 const roster=readJSONFile(new URL('../site/rosters.json',import.meta.url));
 const renderer=createImmutableCohortRenderer({db,roster,fixtureId:'NEW_RECOVERY_XUBO_SINGLE_EVENT_V9'});
 for(const route of ['#/person/fdu-xubo','#/person/fdu-xubo/lineage']){
  const result=await renderer.render(route);const markup=Object.values(result.snapshot).map(v=>v.innerHTML).join('\n');
  assert(markup.includes('学士'));if(route==='#/person/fdu-xubo')for(const label of e.degrees)assert(markup.includes(label));
 }
});
