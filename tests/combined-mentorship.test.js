// Synthetic relationships only. Never copy these fixtures to public snapshots.
import {test} from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {mentorEvent,mentorEvents,mentorProfileRoute,professionalGuidanceEvent,stages} from '../site/model.js';
const read=path=>JSON.parse(fs.readFileSync(new URL(path,import.meta.url)));
function fixture(){
 const d=read('./fixtures/multischool.json'),p=d.people[1];
 p.education=['学士','硕士','博士'].map((degree,i)=>({event_id:'synthetic-stage-'+i,degree,event_kind:'degree',degree_awarded:null,institution:'独立学习机构'+i,start:'200'+i,end:'201'+i,region:'unknown',continent_code:'unknown',institution_985:'unknown',source_url:'https://b.example.test/stage'}));
 p.mentors=[{name:'合述导师（虚构）',type:'postgraduate_advisor',type_label:'硕博合述导师（未拆分阶段）',education_stage:'硕博合述，具体分别阶段未拆证',education_event_ids:p.education.slice(1).map(e=>e.event_id),stage_scope:'combined_masters_doctoral_statement_not_separate_edges',employment_status:'active_officially_listed',person_id:d.people[0].person_id,source_url:'https://b.example.test/relation',profile_source_url:'https://b.example.test/profile',official_url:'https://b.example.test/profile',start:null,end:null,include_in_mentorship_graph:true,relationship_status:'verified_direct_statement'}];
 return d;
}
let serial=0;
async function app(d,hash='#/person/pku-synthetic-person/lineage'){
 const nodes=new Map(),listeners={};
 const node=key=>{if(!nodes.has(key))nodes.set(key,{innerHTML:'',textContent:'',value:'',events:{},style:{},dataset:{height:'320'},clientWidth:960,addEventListener(type,fn){this.events[type]=fn},click(){this.onclick?.()}});return nodes.get(key)};
 globalThis.document={querySelector:node,querySelectorAll:()=>[],getElementById:id=>node('#'+id)};
 globalThis.location={hash};globalThis.window={scrollTo(){},addEventListener(type,fn){listeners[type]=fn}};
 globalThis.fetch=async path=>({ok:true,json:async()=>structuredClone(String(path).startsWith('atlas.json')?d:d.rosters)});
 await import('../site/app.js?combined-fixture='+serial++);
 return {node,navigate(hash){location.hash=hash;listeners.hashchange()}};
}
const professionalSection=ui=>ui.node('#profile-content').innerHTML.match(/<section class="info-panel professional-guidance">[\s\S]*?<\/section>/)?.[0]||'';

test('combined statement resolves two exact events but never one invented merged or selected event',()=>{
 const d=fixture(),p=d.people[1],m=p.mentors[0],before=JSON.stringify(d);
 assert.deepEqual(mentorEvents(p,m),p.education.slice(1));assert.deepEqual(mentorEvent(p,m,true),p.education.slice(1));assert.deepEqual(mentorEvent(p,m),{});
 assert.equal(stages(p,'master').length,0);assert.equal(stages(p,'doctor').length,0);assert.equal(JSON.stringify(d),before);
});
test('actual graph counts one combined relationship and suppresses unknowns only for its exact two events',async()=>{
 const d=fixture(),ui=await app(d),g=ui.node('#mind-stage').innerHTML,card=ui.node('#profile-content').innerHTML;
 assert(g.includes('1条已收录关系'));assert.equal((g.match(/href="#mentor-/g)||[]).length,1);assert.equal((g.match(/>导师未核实</g)||[]).length,1);
 assert(g.includes('合述机构未单独披露'));assert(g.includes('起始时间未披露 至 结束时间未披露'));
 for(const borrowed of ['独立学习机构1','独立学习机构2','2001','2002','2011','2012'])assert(!g.includes(borrowed));
 assert(card.includes('合述仅计一条关系，不拆分阶段导师认定'));assert(card.includes(d.people[1].mentors[0].stage_scope));
 for(const id of d.people[1].mentors[0].education_event_ids)assert(card.includes(id));
 assert(card.includes('起始时间未披露 至 结束时间未披露'));assert(card.includes('#/person/hit-synthetic-person'));
});
test('combined dates and institution come only from explicitly supplied relation fields',async()=>{
 const d=fixture(),m=d.people[1].mentors[0];Object.assign(m,{institution:'来源明确合述机构',start:null,end:'2020-07'});
 const ui=await app(d),g=ui.node('#mind-stage').innerHTML;assert(g.includes('来源明确合述机构'));assert(g.includes('起始时间未披露 至 2020-07'));assert(!g.includes('2001'));
});
test('malformed plural references fail closed without fallback stage matching or partial coverage',async()=>{
 for(const refs of [null,undefined,[],{},'synthetic-stage-1',[''],[' '],[null],['synthetic-stage-1','missing'],['synthetic-stage-1','synthetic-stage-1']]){
  const d=fixture(),p=d.people[1],m=p.mentors[0];m.education_event_ids=refs;m.education_stage='硕士';assert.deepEqual(mentorEvents(p,m),[]);assert.deepEqual(mentorEvent(p,m),{});
  const g=(await app(d)).node('#mind-stage').innerHTML;assert.equal((g.match(/>导师未核实</g)||[]).length,3);
 }
 const p=fixture().people[1],m=p.mentors[0];m.education_event_id=m.education_event_ids[0];assert.deepEqual(mentorEvents(p,m),[]);delete m.education_event_id;p.education.push({...p.education[1]});assert.deepEqual(mentorEvents(p,m),[]);
});
test('legacy single ID and unambiguous label behavior stays unchanged, including postdoc appointments',()=>{
 const p=fixture().people[1];assert.equal(mentorEvent(p,{education_event_id:p.education[1].event_id}),p.education[1]);assert.equal(mentorEvent(p,{education_stage:'硕士'}),p.education[1]);assert.deepEqual(mentorEvent(p,{education_stage:'硕博未细分'}),{});
 assert.equal(mentorEvent(p,{education_event_ids:[p.education[1].event_id],education_event_id:p.education[1].event_id}),p.education[1]);
 p.appointments=[{title:'博士后',institution:'明确博士后机构'}];assert.equal(mentorEvent(p,{education_stage:'博士后'}),p.appointments[0]);
});
test('combined relationships preserve existing internal navigation safety rather than infer identities',()=>{
 const d=fixture(),m=d.people[1].mentors[0];assert.equal(mentorProfileRoute(m,d.people),'#/person/hit-synthetic-person');
 for(const changes of [{person_id:null},{person_id:'missing'},{employment_status:'unknown'},{quick_link_eligible:false}])assert.equal(mentorProfileRoute({...m,...changes},d.people),'');
 assert.equal(mentorProfileRoute({...m,navigation_verified:false},d.people),'#/person/hit-synthetic-person');
});
test('new combined scope and date text is escaped',async()=>{
 const d=fixture(),m=d.people[1].mentors[0],payload='<script>bad()</script>';
 for(const k of ['education_stage','stage_scope','institution','start','end'])m[k]=payload;m.education_event_ids=[payload,'synthetic-stage-2'];
 const ui=await app(d);for(const k of ['#profile-content','#mind-stage']){assert(!ui.node(k).innerHTML.includes(payload));assert(ui.node(k).innerHTML.includes('&lt;script&gt;'))}
});
function professionalFixture(){
 const d=fixture(),p=d.people[1];p.mentors=[];
 p.education=[{...p.education[1],event_id:'explicit-research',degree:null,event_kind:'professional_research',degree_awarded:false,institution:'明确科研经历机构',start:'2009-08',end:'2010-09'}];
 p.professional_research_advisors=[{name:'职业导师（虚构）',relationship_kind:'professional_research_advisor',relationship_status:'verified_direct_statement',education_event_id:'explicit-research',start:null,end:null,include_in_mentorship_graph:false,include_in_degree_mentorship_graph:false,include_in_verified_mentor_count:false,include_in_verified_professional_guidance_count:true,source_url:'https://b.example.test/relation',employment_status:'unknown'}];return d;
}
test('explicit non-award research context stays independent and never becomes guidance dates or postdoc evidence',async()=>{
 const d=professionalFixture(),p=d.people[1],c=p.professional_research_advisors[0],before=JSON.stringify(d);assert.equal(professionalGuidanceEvent(p,c),p.education[0]);
 const ui=await app(d,'#/person/pku-synthetic-person'),s=professionalSection(ui);for(const value of ['explicit-research','明确科研经历机构','2009-08','2010-09','经历区间，不等于指导起止；非博士后认定','起始时间未披露','结束时间未披露'])assert(s.includes(value),value);
 assert(!s.includes('查看指导者个人主页'));ui.navigate('#/person/pku-synthetic-person/lineage');assert(ui.node('#mind-stage').innerHTML.includes('0条已收录关系'));assert(!ui.node('#mind-stage').innerHTML.includes(c.name));assert(!ui.node('#mind-stage').innerHTML.includes('明确科研经历机构'));assert(!ui.node('#mind-stage').innerHTML.includes('>导师未核实<'));assert(ui.node('#mind-stage').innerHTML.includes('已核职业科研指导在个人主页单列'));assert.equal(JSON.stringify(d),before);
});
test('null missing dangling true unknown award and non-research events never join professional context',async()=>{
 for(const changes of [{id:null},{id:undefined},{id:''},{id:'missing'},{award:true},{award:null},{award:undefined},{kind:'degree'},{kind:'postdoctoral'},{kind:'visiting_research'}]){
  const d=professionalFixture(),p=d.people[1],c=p.professional_research_advisors[0];if('id'in changes)c.education_event_id=changes.id;if('award'in changes)p.education[0].degree_awarded=changes.award;if('kind'in changes)p.education[0].event_kind=changes.kind;
  assert.deepEqual(professionalGuidanceEvent(p,c),{});const s=professionalSection(await app(d,'#/person/pku-synthetic-person'));assert(!s.includes('明确科研经历机构'));assert(!s.includes('2009-08'));assert(!s.includes('对应非学位科研经历：'));
 }
});

test('only an exact verified independent professional event suppresses an unknown-mentor placeholder',async()=>{
 for(const changes of [{id:null},{id:''},{id:'missing'},{award:true},{award:null},{kind:'degree'},{kind:'postdoctoral'},{status:'candidate'},{graph:true},{relationship:'research_collaborator'},{duplicate:true}]){
  const d=professionalFixture(),p=d.people[1],c=p.professional_research_advisors[0];if('id'in changes)c.education_event_id=changes.id;if('award'in changes)p.education[0].degree_awarded=changes.award;if('kind'in changes)p.education[0].event_kind=changes.kind;if('status'in changes)c.relationship_status=changes.status;if('graph'in changes)c.include_in_mentorship_graph=changes.graph;if('relationship'in changes)c.relationship_kind=changes.relationship;if(changes.duplicate)p.education.push({...p.education[0]});
  const g=(await app(d)).node('#mind-stage').innerHTML;assert(g.includes('>导师未核实<'),JSON.stringify(changes));assert(g.includes('明确科研经历机构'));assert(!g.includes('已核职业科研指导在个人主页单列'));assert(!g.includes('href="#mentor-'));
 }
 const d=professionalFixture(),p=d.people[1];p.education.push({...p.education[0],event_id:'unrelated-research',institution:'未绑定科研机构'});const g=(await app(d)).node('#mind-stage').innerHTML;assert.equal((g.match(/>导师未核实</g)||[]).length,1);assert(g.includes('未绑定科研机构'));assert(!g.includes('明确科研经历机构'));
});
