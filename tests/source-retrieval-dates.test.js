import {test} from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {sourceRetrievalDateSummary,matches,mentorOfficialUrl,mentorProfileRoute,stages} from '../site/model.js';

const read=path=>JSON.parse(fs.readFileSync(new URL(path,import.meta.url)));
for(const c of read('./fixtures/source-retrieval-dates.json'))test('source retrieval summary: '+c.name,()=>{
 const before=structuredClone(c.person);
 assert.equal(sourceRetrievalDateSummary(c.person),c.expected);
 assert.deepEqual(c.person,before);
});
let serial=0;
async function render(d,hash){
 const nodes=new Map(),node=k=>{if(!nodes.has(k))nodes.set(k,{innerHTML:'',textContent:'',value:'',style:{},events:{},dataset:{height:'320'},clientWidth:960,addEventListener(t,f){this.events[t]=f},click(){this.onclick?.()}});return nodes.get(k)};
 globalThis.document={querySelector:node,querySelectorAll:()=>[],getElementById:id=>node('#'+id)};
 globalThis.location={hash};globalThis.window={scrollTo(){},addEventListener(){}};
 globalThis.fetch=async p=>({ok:true,json:async()=>structuredClone(String(p).startsWith('atlas.json')?d:d.rosters)});
 await import('../site/app.js?source-retrieval-dates-test='+serial++);
 assert(!node('#main').innerHTML.includes('资料暂未加载'));return node;
}

test('profile presents only recorded source dates and an explicit missing whole-person review date',async()=>{
 const d=read('./fixtures/multischool.json'),p=d.people[1];d.updated_at='2099-12-31';
 p.sources=[{id:'first',url:p.official_url,retrieved_at:'2026-10-23',evidence_status:'access_blocked'},{id:'second',url:'https://example.test/source-two',retrieved_at:'2026-10-24',evidence_status:'official_page_read'}];
 const before=structuredClone(d),node=await render(d,'#/person/'+p.person_id),html=node('#profile-content').innerHTML;
 assert(html.includes('已记录来源检索日期：2026-10-23 至 2026-10-24'));
 assert(html.includes('人物整体核验日期未单独记录'));
 assert(html.includes('来源检索日期不代表已读原文或现职持续有效'));
 assert(!html.includes(d.updated_at));assert(!html.includes('核对日期'));
 for(const s of p.sources)assert(html.includes(s.url));
 assert.deepEqual(d,before);
});

test('teacher search notice does not use the global update date as a review date',async()=>{
 const d=read('./fixtures/multischool.json');d.updated_at='2099-12-31';
 const html=(await render(d,'#/people'))('#main').innerHTML;
 assert(html.includes('来源检索日期以逐条来源记录为准'));
 assert(html.includes('不代表人物整体核验或现职持续有效'));
 assert(!html.includes(d.updated_at));assert(!html.includes('核对日期'));
});

test('the generated active-employment label does not imply a whole-person review date or real-time status',async()=>{
 const d=read('./fixtures/multischool.json'),p=d.people[1];
 p.professional_research_advisors=[{name:'合成指导者',employment_status:'active_officially_listed',official_url:'https://example.test/mentor',source_url:p.official_url,profile_source_url:p.official_url}];
 const before=structuredClone(d),html=(await render(d,'#/person/'+p.person_id))('#profile-content').innerHTML;
 assert(html.includes('官方来源列示在职（不代表实时状态）'));assert(!html.includes('官方仍列在职（截至核对日）'));assert(html.includes('href="https://example.test/mentor"'));assert.deepEqual(d,before);
});

test('retrieval summaries do not change facts, degree filters or navigation eligibility',()=>{
 const d=read('./fixtures/multischool.json'),before=structuredClone(d);
 for(const p of d.people){
  const filterResults=[{},{school:p.school_id},{school:'other'},{ug:'yes'},{master:'unknown'},{doctor:'overseas'}].map(f=>matches(p,f,d.org_units));
  const degrees=['bachelor','master','doctor'].map(k=>stages(p,k));
  const navigation=p.mentors.map(m=>[mentorOfficialUrl(m),mentorProfileRoute(m,d.people)]);
  sourceRetrievalDateSummary(p);
  assert.deepEqual([{},{school:p.school_id},{school:'other'},{ug:'yes'},{master:'unknown'},{doctor:'overseas'}].map(f=>matches(p,f,d.org_units)),filterResults);
  assert.deepEqual(['bachelor','master','doctor'].map(k=>stages(p,k)),degrees);
  assert.deepEqual(p.mentors.map(m=>[mentorOfficialUrl(m),mentorProfileRoute(m,d.people)]),navigation);
 }
 assert.deepEqual(d,before);
});
