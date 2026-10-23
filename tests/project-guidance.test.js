import {test} from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {escapeHtml} from '../site/model.js';
const read=path=>JSON.parse(fs.readFileSync(new URL(path,import.meta.url)));
const guidance=()=>read('./fixtures/project-guidance.json');
function fixture(){
  const d=read('./fixtures/multischool.json'),g=guidance(),p=d.people[1];
  p.project_guidance=g.project_guidance;p.sources=g.sources;
  p.education=[{event_id:null,institution:'不得借用的学历机构',start:'1900-01',end:'1901-01',degree:'博士',event_kind:'degree_study',degree_awarded:null,region:'unknown',continent_code:'unknown',source_url:'https://b.example.test/education'}];
  p.appointments=[{title:'不得借用的任职',institution:'不得借用的任职机构',start:'1800-01',end:'1801-01',source_url:'https://b.example.test/employment'}];
  return d;
}
let serial=0;
async function app(d,hash='#/person/pku-synthetic-person'){
  const nodes=new Map(),listeners={};
  const node=key=>{if(!nodes.has(key))nodes.set(key,{innerHTML:'',textContent:'',value:'',events:{},style:{},dataset:{height:'320'},clientWidth:960,addEventListener(type,fn){this.events[type]=fn},click(){this.onclick?.()}});return nodes.get(key)};
  globalThis.document={querySelector:node,querySelectorAll:()=>[],getElementById:id=>node('#'+id)};
  globalThis.location={hash};globalThis.window={scrollTo(){},addEventListener(type,fn){listeners[type]=fn}};
  globalThis.fetch=async path=>({ok:true,json:async()=>structuredClone(String(path).startsWith('atlas.json')?d:d.rosters)});
  await import('../site/app.js?project-fixture='+serial++);
  return {node,navigate(hash){location.hash=hash;listeners.hashchange()}};
}
const section=ui=>ui.node('#profile-content').innerHTML.match(/<section class="info-panel project-guidance">[\s\S]*?<\/section>/)?.[0]||'';
const sourceList=ui=>ui.node('#profile-content').innerHTML.match(/<ol class="sources">[\s\S]*?<\/ol>/)?.[0]||'';

test('actual personal page preserves project adviser, project scope, biography and both source links separately',async()=>{
  const d=fixture(),c=d.people[1].project_guidance[0],ui=await app(d),html=section(ui);
  assert(html.includes('项目指导（非学位师承）'));
  for(const key of ['name','type_label','project_name','education_stage','relationship_scope','description','employment_status_note','note','scope_label'])assert(html.includes(escapeHtml(c[key])),key);
  assert(html.includes('href="'+c.source_url+'"'));assert(html.includes('href="'+c.profile_source_url+'"'));
  assert(html.includes('不进入师承关系图或导师统计'));
  assert(!html.includes('查看导师个人主页'));assert(!html.includes('查看本库个人档案'));
});

test('null or absent education identifiers never borrow degree or appointment details into project guidance',async()=>{
  for(const eventId of [null,undefined]){
    const d=fixture(),c=d.people[1].project_guidance[0];c.education_event_id=eventId;
    const html=section(await app(d));
    for(const forbidden of ['不得借用的学历机构','不得借用的任职机构','1900-01','1901-01','1800-01','1801-01','对应经历'])assert(!html.includes(forbidden),forbidden);
  }
});

test('project relationships do not create mentor cards, mind-map edges or teacher-list mentor counts',async()=>{
  const d=fixture(),before=JSON.stringify(d),name=d.people[1].project_guidance[0].name;
  const ui=await app(d);ui.navigate('#/person/pku-synthetic-person/lineage');
  assert(!ui.node('#profile-content').innerHTML.includes(name));assert(!ui.node('#mind-stage').innerHTML.includes(name));
  assert(ui.node('#mind-stage').innerHTML.includes('0条已收录关系'));
  ui.navigate('#/people?school=pku');assert(ui.node('#results').innerHTML.includes('0 条师承/指导记录'));
  assert.equal(JSON.stringify(d),before);
});

test('legacy people without project guidance keep the original layout and no empty project section',async()=>{
  const d=fixture();delete d.people[1].project_guidance;
  const ui=await app(d);assert.equal(section(ui),'');assert(ui.node('#profile-content').innerHTML.includes('论文与学术成果'));
});

test('project descriptions and labels are escaped, unsafe relationship links never become anchors',async()=>{
  const d=fixture(),c=d.people[1].project_guidance[0],payload='<script>unsafe()</script>';
  for(const key of ['name','type_label','project_name','education_stage','relationship_scope','description','employment_status_note','note','scope_label'])c[key]=payload;
  c.source_url='javascript:unsafe()';c.profile_source_url='data:text/html,unsafe';
  const html=section(await app(d));assert(html.includes('&lt;script&gt;unsafe()&lt;/script&gt;'));assert(!html.includes(payload));
  assert(!html.includes('href="javascript:'));assert(!html.includes('href="data:'));
});

test('self-reported professional sources show their Chinese evidence level without an official-site claim',async()=>{
  const d=fixture(),s=d.people[1].sources[2],ui=await app(d),html=sourceList(ui);
  assert(html.includes(s.evidence_status_label));assert(html.includes('非学校域名官网'));
  assert(html.includes('href="'+s.url+'"'));assert(!html.includes('学校官方主页'));
  // Both normalized label spellings are supported; neither rewrites the stored status.
  s.evidence_label='自述职业来源 <待复核>';delete s.evidence_status_label;
  const second=sourceList(await app(d));assert(second.includes('自述职业来源 &lt;待复核&gt;'));
  assert.equal(s.evidence_status,'self_reported_professional_website_identity_cross_checked');
});

test('source fallback is neutral public-source wording instead of inventing official provenance',async()=>{
  const d=fixture();d.people[1].sources=[{url:'https://professional.example.test/unknown'}];
  const html=sourceList(await app(d));assert(html.includes('公开来源'));assert(!html.includes('官方来源'));
});
