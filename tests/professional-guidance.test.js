import {test} from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {spawnSync} from 'node:child_process';
const read=path=>JSON.parse(fs.readFileSync(new URL(path,import.meta.url)));
function fixture(){const d=read('./fixtures/multischool.json'),p=d.people[1];p.education=[];p.appointments=[{title:'NO_NULL_JOIN',event_id:null,start:'1900-01'}];p.mentors=[];p.professional_research_advisors=[{name:'职业指导者',type:'职业科研合作导师',relationship_kind:'professional_research_advisor',relationship_status:'verified_direct_statement',include_in_mentorship_graph:false,include_in_verified_mentor_count:false,include_in_degree_mentorship_graph:false,include_in_verified_professional_guidance_count:true,education_event_id:null,source_url:'https://example.edu/relation',profile_source_url:'https://example.edu/employment',description:'有直接证据的职业指导',employment_status:'unknown',official_url:'https://example.edu/profile'}];return d;}
let serial=0;
async function app(d,hash='#/person/pku-synthetic-person'){
  const nodes=new Map(),listeners={};
  const node=key=>{if(!nodes.has(key))nodes.set(key,{innerHTML:'',textContent:'',value:'',events:{},style:{},dataset:{height:'320'},clientWidth:960,addEventListener(type,fn){this.events[type]=fn},click(){this.onclick?.()}});return nodes.get(key)};
  globalThis.document={querySelector:node,querySelectorAll:()=>[],getElementById:id=>node('#'+id)};
  globalThis.location={hash};globalThis.window={scrollTo(){},addEventListener(type,fn){listeners[type]=fn}};
  globalThis.fetch=async path=>({ok:true,json:async()=>structuredClone(String(path).startsWith('atlas.json')?d:d.rosters)});
  await import('../site/app.js?professional-fixture='+serial++);
  return {node,navigate(hash){location.hash=hash;listeners.hashchange()}};
}

const section=ui=>ui.node('#profile-content').innerHTML.match(/<section class="info-panel professional-guidance">[\s\S]*?<\/section>/)?.[0]||'';
test('professional guidance preserves explicit role independently without null-ID joins',async()=>{const d=fixture(),ui=await app(d),html=section(ui);assert(html.includes('职业科研指导（非学位）'));assert(html.includes('有直接证据的职业指导'));assert(html.includes('已核职业指导：1 条'));assert(!html.includes('NO_NULL_JOIN'));assert(!html.includes('1900-01'));assert(!html.includes('查看指导者个人主页'));assert(!html.includes('非导师认定'));ui.navigate('#/person/pku-synthetic-person/lineage');assert(!ui.node('#mind-stage').innerHTML.includes('职业指导者'));assert(ui.node('#mind-stage').innerHTML.includes('0条已收录关系'));});
test('professional guidance navigation obeys verified active and explicit veto',async()=>{for(const status of ['unknown','retired','deceased','active_officially_listed']){const d=fixture(),c=d.people[1].professional_research_advisors[0];c.employment_status=status;let html=section(await app(d));assert.equal(html.includes('查看指导者个人主页'),status==='active_officially_listed');c.navigation_verified=false;html=section(await app(d));assert(!html.includes('查看指导者个人主页'));}});
test('professional guidance labels and source links remain escaped and protocol safe',async()=>{const d=fixture(),c=d.people[1].professional_research_advisors[0];c.name='<script>bad()</script>';c.source_url='javascript:bad()';const html=section(await app(d));assert(html.includes('&lt;script&gt;'));assert(!html.includes('<script>'));assert(!html.includes('href="javascript:'));});
test('professional guidance optional module does not alter legacy profiles',async()=>{const d=fixture();delete d.people[1].professional_research_advisors;assert.equal(section(await app(d)),'');});
test('professional guidance exports separate typed role without borrowing education dates',()=>{const d=fixture();const py="import sys,json;sys.path.insert(0,'scripts');import build;d=json.load(sys.stdin);t=dict(build.department_tables([d['people'][1]],'2026-10-23',d['institutions']));print(json.dumps(t,ensure_ascii=False))";const r=spawnSync('python',['-B','-c',py],{cwd:new URL('..',import.meta.url),input:JSON.stringify(d),encoding:'utf8'});assert.equal(r.status,0,r.stderr);const t=JSON.parse(r.stdout),m=t['导师'];assert.equal(m.length,2);assert.equal(m[1][2],'职业科研指导（非学位）');assert.equal(m[1][3],'职业科研阶段（非学历绑定）');assert.equal(m[1][7],'');assert(!JSON.stringify(m).includes('1900-01'));});

test('professional module preserves the original role, stage, both notes and only explicitly supplied dates',async()=>{
 const d=fixture(),c=d.people[1].professional_research_advisors[0];Object.assign(c,{type_label:'职业科研指导（非学位）',education_stage:'科研助理教授任职阶段（非学位）',institution:'明确职业指导机构',start:'2020-01',end:'2021-12',relationship_scope:'职业阶段指导范围',note:'关系备注',evidence_note:'独立证据说明',scope_label:'已核职业指导，非学位导师',source_include_in_mentorship_graph:true});const before=JSON.stringify(d),html=section(await app(d));
 for(const key of ['type','type_label','education_stage','institution','start','end','relationship_scope','note','evidence_note','scope_label'])assert(html.includes(c[key]),key);assert(!html.includes('1900-01'));assert.equal(JSON.stringify(d),before);
});

test('professional shortcuts preserve active internal identity rules and independently veto external navigation',async()=>{
 for(const person_id of [null,'','null','unknown','not-in-library']){const d=fixture(),c=d.people[1].professional_research_advisors[0];Object.assign(c,{employment_status:'active_officially_listed',person_id,navigation_verified:false,profile_navigation_unavailable_reason:'主页403，不继续请求。'});const html=section(await app(d));assert(!html.includes('查看本库个人档案'));assert(!html.includes('查看指导者个人主页'));assert(html.includes('任职已核实；主页403，不继续请求。'));assert(html.includes(c.profile_source_url))}
 const d=fixture(),c=d.people[1].professional_research_advisors[0];Object.assign(c,{employment_status:'active_officially_listed',person_id:d.people[0].person_id,navigation_verified:false});let html=section(await app(d));assert(html.includes('查看本库个人档案'));assert(!html.includes('查看指导者个人主页'));c.quick_link_eligible=false;html=section(await app(d));assert(!html.includes('查看本库个人档案'));
});

test('unidentified news and blocked individual profiles retain separate alternatives without a homepage shortcut',async()=>{
 for(const state of ['not_identified','unavailable']){const d=fixture(),p=d.people[1];Object.assign(p,{official_profile_availability:state,official_profile_navigation_eligible:false,official_profile_availability_label:state==='not_identified'?'未确认独立个人主页，原URL为官方职业报道':undefined,alternative_professional_sources:[{url:'https://ciee.cau.edu.cn/reviewed-news',title:'官方职业报道（非个人主页）'}]});const html=(await app(d)).node('#main').innerHTML;assert(!html.includes('学校官方主页'));assert(html.includes('官方职业报道（非个人主页）'));assert(html.includes('https://ciee.cau.edu.cn/reviewed-news'));assert(html.includes(p.official_profile_availability_label||'学校个人主页当前不可用'))}
});

test('professional context labels, dates and availability explanations are escaped',async()=>{
 const d=fixture(),p=d.people[1],c=p.professional_research_advisors[0],payload='<img src=x onerror=bad()> ';for(const key of ['type_label','education_stage','institution','start','end','relationship_scope','note','evidence_note','scope_label'])c[key]=payload;p.official_profile_navigation_eligible=false;p.official_profile_availability_label=payload;const ui=await app(d);assert(!section(ui).includes('<img'));assert(section(ui).includes('&lt;img'));assert(!ui.node('#main').innerHTML.includes('<img'));assert(ui.node('#main').innerHTML.includes('&lt;img'));
});
