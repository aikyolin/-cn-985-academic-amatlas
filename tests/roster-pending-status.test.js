import {readJSONFile} from './atlas-test-io.js';
import {test} from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {renderRosters,rosterIdentityMatched,rosterStatusLabel} from '../site/rosters.js';

const read=path=>readJSONFile(new URL(path,import.meta.url));
const db=read('../data/atlas.json');db.rosters=read('../data/rosters.json');
const render=(d,id)=>{const main={innerHTML:''};renderRosters(d,main,id);return main.innerHTML};

test('real Tongji Bin Yi matched sparse profile has consistent identity wording without promoting it to a person archive',()=>{
 const p=db.pending_people.find(p=>p.person_id==='tongji-binyi'),e=db.rosters.entries.find(e=>e.id===p.roster_entry_id);assert(p);assert(e);assert.equal(p.profile_status,'profile_details_pending');assert.equal(p.identity_evidence.status,'official_roster_explicit_profile_link');assert.equal(p.pending_reason_label,undefined);
 const before=JSON.stringify([p,e]),html=render(db,e.id);assert.equal(rosterIdentityMatched(db,e),true);assert.equal(rosterStatusLabel(db,e),'身份已匹配，资料待完善');assert(html.includes('官方主页（身份已匹配，资料完整性另核）'));assert(html.includes('人物身份已匹配，资料待完善'));assert(!html.includes('人物身份待核实'));assert(html.includes('尚未建立人物档案，候选成果不计正式统计'));assert(!html.includes('进入已核实身份的人物档案'));assert.equal(e.verified_person_id,null);assert.equal(e.profile_identity_verified,false);assert(!db.people.some(q=>q.person_id===p.person_id));assert.equal(JSON.stringify([p,e]),before);
});

test('real identity-pending Hamdi Barkaoui retains conservative identity and original-link wording',()=>{
 const p=db.pending_people.find(p=>p.person_id==='hit-hamdi-barkaoui'),e=db.rosters.entries.find(e=>e.id===p.roster_entry_id);assert.equal(p.profile_status,'roster_identity_pending');assert.equal(rosterIdentityMatched(db,e),false);assert.equal(rosterStatusLabel(db,e),'档案待建，身份待核对');const html=render(db,e.id);assert(html.includes('人物身份待核实'));assert(!html.includes('人物身份已匹配'));assert(!html.includes('进入已核实身份的人物档案'));
});

test('a matching roster link alone never upgrades an explicitly identity-pending record',()=>{
 const d=structuredClone(db),p=d.pending_people.find(p=>p.person_id==='tongji-binyi'),e=d.rosters.entries.find(e=>e.id===p.roster_entry_id);p.profile_status='roster_identity_pending';delete p.pending_reason_label;assert.equal(rosterIdentityMatched(d,e),false);const html=render(d,e.id);assert(html.includes('人物身份待核实'));assert(html.includes('原名录提供的主页链接（身份待核对）'));assert(!html.includes('人物身份已匹配'));
});

test('pending reason labels are preserved and escaped, not replaced by the new fallback',()=>{
 const d=structuredClone(db),p=d.pending_people.find(p=>p.person_id==='tongji-binyi');p.pending_reason_label='身份已匹配，<本人资料稀疏> & 待完善';const html=render(d,p.roster_entry_id);assert(html.includes('身份已匹配，&lt;本人资料稀疏&gt; &amp; 待完善'));assert(!html.includes('<本人资料稀疏>'));assert(html.includes('候选成果不计正式统计'));
});

test('a pending record from another school cannot supply a matched identity or detail notice',()=>{
 const d=structuredClone(db),p=d.pending_people.find(p=>p.person_id==='tongji-binyi'),e=d.rosters.entries.find(e=>e.id===p.roster_entry_id);p.school_id='hit';p.pending_reason_label='错误跨校身份提示';assert.equal(rosterIdentityMatched(d,e),false);const html=render(d,e.id);assert(!html.includes('错误跨校身份提示'));assert(!html.includes('人物身份已匹配'));assert(html.includes('原名录提供的主页链接（身份待核对）'));
});
