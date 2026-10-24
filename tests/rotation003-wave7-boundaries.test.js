// Generic current-consumer boundaries driven by a reviewed source contract, not names.
import {test} from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {createHash} from 'node:crypto';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..'),read=f=>JSON.parse(fs.readFileSync(path.join(root,f),'utf8'));
const raw=fs.readFileSync(path.join(root,'tests/fixtures/rotation003-wave7-source-contract.json'));
assert.equal(createHash('sha256').update(raw).digest('hex'),'fcf3cf741770fe5933aebab13e21b9c25b57d42e1f27356c0b4d3ac80b7b0d40');
const contract=JSON.parse(raw),db=read('site/atlas.json');db.rosters=read('site/rosters.json');
const model=await import(pathToFileURL(path.join(root,'site/model.js'))),roster=await import(pathToFileURL(path.join(root,'site/rosters.js')));
test('combined source relationships retain every event without splitting or inventing current navigation',()=>{
 let combined=0;
 for(const row of contract.people){const source=row.original,p=db.people.find(p=>p.person_id===source.person_id);assert(p);assert.equal(p.mentors.length,source.mentors.length);
  for(const [i,original]of source.mentors.entries()){const m=p.mentors[i];assert.equal(m.name,original.name);assert.deepEqual(model.mentorEvents(p,m).map(e=>e.event_id),original.education_event_ids||[original.education_event_id]);
   if(original.education_event_ids){combined++;assert.equal(m.education_event_id,null);assert.deepEqual(model.mentorEvent(p,m),{});assert.equal(p.mentors.filter(x=>x.name===m.name&&x.source_url===m.source_url).length,1);const broken={...m,education_event_ids:[...m.education_event_ids,m.education_event_ids[0]]};assert.deepEqual(model.mentorEvents(p,broken),[]);}
   if(!original.navigation_verified){assert.equal(model.mentorOfficialUrl(m),'');assert.equal(model.mentorProfileRoute(m,db.people),'');}
  }
 }assert.equal(combined,contract.combined_relationship_count);
});
test('explicit non-personal sources never become personal homepages or current-personnel proof',()=>{
 let blocked=0;
 for(const row of contract.people){const source=row.original,p=db.people.find(p=>p.person_id===source.person_id);
  if(source.official_profile_navigation_eligible!==false)continue;blocked++;
  assert.equal(p.official_url,source.official_url);assert.equal(model.officialProfileUrl(p),'');assert.equal(p.employment_status,source.employment_status);assert.deepEqual(p.current_personnel_observation,source.current_personnel_observation);
  const entry=db.rosters.entries.find(e=>e.id===p.roster_entry_id);assert(entry);assert(roster.rosterHomepageUnavailable(db,entry));assert(!roster.rosterProfileLinks(db,entry).includes('href="'+source.official_url+'"'));
 }assert.equal(blocked,contract.non_personal_source_count);
});
