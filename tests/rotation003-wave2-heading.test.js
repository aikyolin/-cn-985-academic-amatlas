import test from 'node:test';
import assert from 'node:assert/strict';
import {renderRosters} from '../site/rosters.js';

test('unlinked roster title describes the missing identity link, never absence of independent research or an authorized profile route',()=>{
 const entry={id:'sample-roster',school_id:'sample-school',organization_id:'sample-department',name:'示例教师',category:'教师',roster_source_url:'https://example.edu/roster',accessed_on:'2026-10-24',notes:[]};
 const independent={person_id:'sample-person',school_id:entry.school_id,department_id:entry.organization_id,name:entry.name,official_url:'https://example.edu/profile'};
 for(const people of [[],[independent]]){
  const db={people,pending_people:[],institutions:[],org_units:[],rosters:{entries:[entry],totals:{raw_observation_count:1}}};
  const before=JSON.stringify(db),main={innerHTML:''};renderRosters(db,main,entry.id);
  assert(main.innerHTML.includes('<h2>此名录记录尚未绑定个人档案</h2>'));
  assert(!main.innerHTML.includes('个人档案尚未建立'));
  assert(!main.innerHTML.includes('href="#/person/'));
  assert.equal(JSON.stringify(db),before);
 }
 const linked={...entry,verified_person_id:independent.person_id},main={innerHTML:''};
 renderRosters({people:[independent],pending_people:[],institutions:[],org_units:[],rosters:{entries:[linked],totals:{raw_observation_count:1}}},main,entry.id);
 assert(main.innerHTML.includes('<h2>已有核实身份关联的人物档案</h2>'));
 assert(main.innerHTML.includes('href="#/person/sample-person"'));
 assert(!main.innerHTML.includes('此名录记录尚未绑定个人档案'));
});
