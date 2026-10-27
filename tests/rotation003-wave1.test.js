import {createAtlasFetch} from './atlas-test-io.js';
import {readJSONFile} from './atlas-test-io.js';
import {publishedRoot} from './published-fixture.js';
import {historicalBytes} from './source-date-history.js';
import {release25View} from './release-history.js';
// Independent release25 actual-consumer regression. Offline, no build writes.
// Fixture constants come from approved raw source packages, never normalization output.
import {test} from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {createHash} from 'node:crypto';
import {fileURLToPath,pathToFileURL} from 'node:url';
const root=process.env.ACADEMIC_ATLAS_TEST_ROOT||path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const read=name=>readJSONFile(path.join(root,name));
const db=release25View(read('data/atlas.json'),'data/atlas.json'); db.rosters=release25View(read('data/rosters.json'),'data/rosters.json');
const {stages,matches,educationStageLabel,mentorEvents,mentorOfficialUrl,mentorProfileRoute,officialProfileUrl,schoolStats}=await import(pathToFileURL(path.join(root,'site/model.js')));
const {rosterIdentityMatched,rosterStatusLabel,renderRosters,rosterSamplingIdentityMatched}=await import(pathToFileURL(path.join(root,'site/rosters.js')));
const digest=x=>createHash('sha256').update(JSON.stringify(x)).digest('hex');
const esc=x=>String(x??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const person=id=>[...db.people,...db.pending_people].find(p=>p.person_id===id);
const EXPECTED_IDS = {"cqu":["cqu-chenke","cqu-chenrenwei","cqu-chenxiaomeng"],"xmu":["xmu-chenhuang-economics","xmu-chenwanyi","xmu-dingchangfa"],"bit":["bit-chentian","bit-chenyuhui","bit-daiyunyun"]};
const PROFESSIONAL_IDS = ["cqu-chenke","cqu-chenxiaomeng","xmu-chenhuang-economics","xmu-chenwanyi","xmu-dingchangfa","bit-chentian","bit-chenyuhui","bit-daiyunyun"];
const EXPECTED_EDUCATION = {"cqu-chenke":[{"event_id":"cqu-chenke-education-1","degree":null,"institution":"重庆大学","start":null,"end":null,"event_kind":"education_level_unknown","degree_awarded":null,"degree_awarded_date":null}],"cqu-chenrenwei":[],"cqu-chenxiaomeng":[{"event_id":"cqu-chenxiaomeng-education-1","degree":"学士","institution":"同济大学","start":"2007-09","end":"2011-07","event_kind":"degree_study","degree_awarded":null,"degree_awarded_date":null},{"event_id":"cqu-chenxiaomeng-education-2","degree":"硕士","institution":"慕尼黑工业大学","start":"2011-09","end":"2014-09","event_kind":"degree_study","degree_awarded":null,"degree_awarded_date":null},{"event_id":"cqu-chenxiaomeng-education-3","degree":"博士","institution":"清华大学","start":"2017-08","end":"2022-06","event_kind":"degree_study","degree_awarded":null,"degree_awarded_date":null}],"xmu-chenhuang-economics":[{"event_id":"xmu-chenhuang-economics-education-1","degree":"学士","institution":"南京农业大学","start":"2005","end":"2009","event_kind":"degree_study","degree_awarded":null,"degree_awarded_date":null},{"event_id":"xmu-chenhuang-economics-education-2","degree":"硕士","institution":"中国科学院","start":"2009","end":"2012","event_kind":"degree_study","degree_awarded":null,"degree_awarded_date":null},{"event_id":"xmu-chenhuang-economics-education-3","degree":"博士","institution":"加州大学戴维斯分校","start":"2013","end":"2018","event_kind":"degree_study","degree_awarded":null,"degree_awarded_date":null}],"xmu-chenwanyi":[{"event_id":"xmu-chenwanyi-education-1","degree":"学士","institution":"武汉大学","start":null,"end":"2011","event_kind":"degree_study","degree_awarded":null,"degree_awarded_date":null},{"event_id":"xmu-chenwanyi-education-2","degree":"学士","institution":"武汉大学","start":null,"end":"2011","event_kind":"degree_study","degree_awarded":null,"degree_awarded_date":null},{"event_id":"xmu-chenwanyi-education-3","degree":"博士","institution":"威斯康星大学麦迪逊分校","start":null,"end":"2018","event_kind":"degree_study","degree_awarded":null,"degree_awarded_date":null}],"xmu-dingchangfa":[{"event_id":"xmu-dingchangfa-education-1","degree":"硕士","institution":"福建师范大学","start":"1994-08","end":"1997-07","event_kind":"degree_study","degree_awarded":null,"degree_awarded_date":null},{"event_id":"xmu-dingchangfa-education-2","degree":"博士","institution":"厦门大学","start":"1999-09","end":"2002-07","event_kind":"degree_study","degree_awarded":null,"degree_awarded_date":null},{"event_id":"xmu-dingchangfa-education-3","degree":null,"institution":"墨尔本皇家理工学院","start":"2007-07","end":"2007-08","event_kind":"academic_exchange_or_training","degree_awarded":false,"degree_awarded_date":null},{"event_id":"xmu-dingchangfa-education-4","degree":null,"institution":"康奈尔大学","start":"2008-08","end":"2009-06","event_kind":"academic_visit","degree_awarded":false,"degree_awarded_date":null}],"bit-chentian":[{"event_id":"bit-chentian-education-1","degree":"学士","institution":"南开大学","start":"2006","end":"2010","event_kind":"degree_study","degree_awarded":null,"degree_awarded_date":null},{"event_id":"bit-chentian-education-2","degree":"博士","institution":"清华大学","start":"2010","end":"2015","event_kind":"degree_study","degree_awarded":null,"degree_awarded_date":null},{"event_id":"bit-chentian-education-3","degree":null,"institution":"美国斯蒂文森理工学院","start":"2013","end":"2014","event_kind":"academic_visit","degree_awarded":false,"degree_awarded_date":null}],"bit-chenyuhui":[{"event_id":"bit-chenyuhui-education-1","degree":"理学学士","institution":"中山大学","start":"2004","end":"2008","event_kind":"degree_study","degree_awarded":true,"degree_awarded_date":"2008"},{"event_id":"bit-chenyuhui-education-2","degree":"博士","institution":"中国科学院物理研究所","start":null,"end":null,"event_kind":"degree_study","degree_awarded":true,"degree_awarded_date":"2013"},{"event_id":"bit-chenyuhui-education-3","degree":null,"institution":"新西兰奥塔哥大学","start":"2013","end":"2017","event_kind":"postdoctoral_research","degree_awarded":false,"degree_awarded_date":null}],"bit-daiyunyun":[{"event_id":"bit-daiyunyun-education-1","degree":"学士","institution":"南京大学","start":"2007","end":"2011","event_kind":"degree_study","degree_awarded":null,"degree_awarded_date":null},{"event_id":"bit-daiyunyun-education-2","degree":"博士","institution":"复旦大学","start":"2011","end":"2017","event_kind":"degree_study","degree_awarded":null,"degree_awarded_date":null},{"event_id":"bit-daiyunyun-education-3","degree":null,"institution":"丹麦科技大学","start":"2014","end":"2014","event_kind":"academic_visit","degree_awarded":false,"degree_awarded_date":null},{"event_id":"bit-daiyunyun-education-4","degree":null,"institution":"芬兰阿尔托大学（Aalto University）","start":"2017-04","end":"2021-12","event_kind":"postdoctoral_research","degree_awarded":false,"degree_awarded_date":null}]};
const EXPECTED_COUNTS = {"cqu-chenke":{"campus_ids":0,"sources":5,"unknowns":4,"appointments":2,"education":1,"mentors":0,"committee_members":0,"publications":0,"research_fields":0,"academic_service":0,"teaching":2,"honors":1,"research_projects":0,"pending_education_candidates":0,"pending_mentor_candidates":0,"pending_appointment_candidates":0,"pending_professional_fact_candidates":0},"cqu-chenrenwei":{"campus_ids":0,"sources":2,"unknowns":3,"appointments":0,"education":0,"mentors":0,"committee_members":0,"publications":0,"research_fields":0,"academic_service":0,"teaching":0,"honors":0,"research_projects":0,"pending_education_candidates":0,"pending_mentor_candidates":0,"pending_appointment_candidates":0,"pending_professional_fact_candidates":0},"cqu-chenxiaomeng":{"campus_ids":0,"sources":2,"unknowns":5,"appointments":1,"education":3,"mentors":0,"committee_members":0,"publications":0,"research_fields":3,"academic_service":2,"teaching":0,"honors":1,"research_projects":0,"pending_education_candidates":0,"pending_mentor_candidates":0,"pending_appointment_candidates":0,"pending_professional_fact_candidates":0},"xmu-chenhuang-economics":{"campus_ids":0,"appointments":1,"education":3,"mentors":0,"committee_members":0,"publications":1,"sources":3,"unknowns":4,"pending_education_candidates":0,"pending_mentor_candidates":0,"pending_appointment_candidates":0,"pending_professional_fact_candidates":0,"research_fields":5},"xmu-chenwanyi":{"campus_ids":0,"appointments":2,"education":3,"mentors":0,"committee_members":0,"publications":1,"sources":4,"unknowns":4,"pending_education_candidates":0,"pending_mentor_candidates":0,"pending_appointment_candidates":0,"pending_professional_fact_candidates":0,"research_fields":2},"xmu-dingchangfa":{"campus_ids":0,"appointments":2,"education":4,"mentors":0,"committee_members":0,"publications":0,"sources":3,"unknowns":5,"pending_education_candidates":0,"pending_mentor_candidates":0,"pending_appointment_candidates":0,"pending_professional_fact_candidates":0,"research_fields":3},"bit-chentian":{"campus_ids":0,"appointments":3,"education":3,"mentors":0,"committee_members":0,"publications":1,"sources":2,"unknowns":3,"pending_education_candidates":0,"pending_mentor_candidates":0,"pending_appointment_candidates":0,"pending_professional_fact_candidates":0,"research_fields":3},"bit-chenyuhui":{"campus_ids":0,"appointments":3,"education":3,"mentors":1,"committee_members":0,"publications":1,"sources":3,"unknowns":3,"pending_education_candidates":1,"pending_mentor_candidates":0,"pending_appointment_candidates":0,"pending_professional_fact_candidates":0,"research_fields":2},"bit-daiyunyun":{"campus_ids":0,"appointments":1,"education":4,"mentors":0,"committee_members":0,"publications":1,"sources":3,"unknowns":4,"pending_education_candidates":0,"pending_mentor_candidates":0,"pending_appointment_candidates":1,"pending_professional_fact_candidates":0,"research_fields":3}};
const BASELINE_PINS = {
  "people": 547,
  "education": 1699,
  "filters": 122,
  "labels_sha256": "d96b2bb34274f3520960d907b5a091e3b39adff5d5efb5549c945e6b0c2c1f34",
  "outcomes_sha256": "aba4379cde86a609983c49c63b03f6e6166fbf795105d8f5f8de05f58e70719d"
};
const ids=Object.values(EXPECTED_IDS).flat();
let serial=0;
const fixtures=new WeakMap();
async function fixture(input=db,appRoot=root){
  let byRoot=fixtures.get(input);if(!byRoot){byRoot=new Map();fixtures.set(input,byRoot)}
  if(byRoot.has(appRoot))return byRoot.get(appRoot);
  const pending=(async()=>{
    const view=structuredClone(input),nodes=new Map(),listeners={};
    view.build_id=view.rosters.build_id='rotation003-wave1-independent-fixture';view.exports||=[];
    const node=key=>{
      if(!nodes.has(key))nodes.set(key,{innerHTML:'',textContent:'',value:'',style:{},dataset:{height:'320'},clientWidth:960,
        addEventListener(){},click(){this.onclick?.()},scrollIntoView(){},querySelector(selector){return node(selector)}});
      return nodes.get(key);
    };
    const document={querySelector:node,querySelectorAll:()=>[],getElementById:id=>node('#'+id)};
    const location={href:"https://atlas.test/site/index.html",hash:'#/'},window={scrollTo(){},addEventListener(name,fn){listeners[name]=fn}};
    const fetch=process.env.ACADEMIC_ATLAS_NEGATIVE_CONTROL_ROOT && appRoot===process.env.ACADEMIC_ATLAS_NEGATIVE_CONTROL_ROOT ? async request=>{assert.match(String(request),/^(atlas|rosters)\.json(?:\?|$)/,'External fetch prohibited');return {ok:true,json:async()=>structuredClone(String(request).startsWith('atlas.json')?view:view.rosters)}} : createAtlasFetch(view,view.rosters);
    const activate=()=>Object.assign(globalThis,{document,location,window,fetch});activate();
    await import(pathToFileURL(path.join(appRoot,'site/app.js')).href+'?rotation003-wave1-independent='+serial++);
    assert.equal(typeof listeners.hashchange,'function','Actual app must initialize');
    return {node,nodes,listeners,location,activate};
  })();
  byRoot.set(appRoot,pending);return pending;
}
async function route(hash,input=db,appRoot=root){
  const f=await fixture(input,appRoot);f.activate();for(const n of f.nodes.values())n.innerHTML='';
  f.location.hash=hash;f.listeners.hashchange();
  return {main:f.node('#main').innerHTML,content:f.node('#profile-content').innerHTML,graph:f.node('#mind-stage').innerHTML,results:f.node('#results').innerHTML};
}
const render=(id,mode='profile',input=db,appRoot=root)=>route('#/person/'+id+(mode==='lineage'?'/lineage':''),input,appRoot);
const educationRows=html=>[...html.content.split('<h2>任职经历</h2>')[0].matchAll(/<article>([\s\S]*?)<\/article>/g)].map(m=>m[1]);
const hrefs=html=>[...html.matchAll(/\bhref="([^"]*)"/g)].map(m=>m[1]);
const cached=()=>person('cqu-chenke').sources.filter(s=>s.navigation_enabled===false);
const EXPECTED_LABELS={
 'cqu-chenke':['学习经历（层次与授位未核实）'],
 'cqu-chenxiaomeng':['学士','硕士','博士'],
 'xmu-chenhuang-economics':['学士','硕士','博士'],
 'xmu-chenwanyi':['学士','学士','博士'],
 'xmu-dingchangfa':['硕士','博士','学术交流或进修','学术访问（非学位）'],
 'bit-chentian':['学士','博士','学术访问（非学位）'],
 'bit-chenyuhui':['理学学士','博士','博士后研究'],
 'bit-daiyunyun':['学士','博士','学术访问（非学位）','博士后研究'],
};

test('release25 adds exactly eight professional records and the original sparse second selection stays pending',()=>{
  assert.deepEqual(db.people.slice(547).map(p=>p.person_id),PROFESSIONAL_IDS);
  assert.deepEqual(db.pending_people.slice(83).map(p=>p.person_id),['cqu-chenrenwei']);
  assert.deepEqual([db.people.length,db.pending_people.length,db.institutions.length,db.org_units.length],[555,84,39,229]);
  for(const id of ids)assert(person(id),id);
  for(const id of PROFESSIONAL_IDS){assert.equal(person(id).detail_count_eligible,true);assert.equal(person(id).complete_profile_count_eligible,false)}
});

for(const id of PROFESSIONAL_IDS)test(`actual profile preserves every event and exact uncertainty label: ${id}`,async()=>{
  const p=person(id),html=await render(id),rows=educationRows(html);
  assert.deepEqual(p.education.map(educationStageLabel),EXPECTED_LABELS[id]);
  assert.equal(rows.length,EXPECTED_EDUCATION[id].length);
  for(const [i,e]of p.education.entries()){
    assert(rows[i].includes(esc(EXPECTED_LABELS[id][i])),`${id}/${i}`);
    assert(rows[i].includes(esc(e.institution)));
    assert.equal(rows[i].includes('本事件未明确记载获授学位，不参与学历筛选'),e.degree_awarded!==true);
    assert.equal(rows[i].includes('授位日期：'),e.degree_awarded_date!==null);
  }
});

test('actual Chen Renwei route remains a pending roster detail and is absent from professional directory',async()=>{
  const p=person('cqu-chenrenwei'),e=db.rosters.entries.find(e=>e.id===p.roster_entry_id);
  assert.equal(p.profile_status,'profile_details_pending');assert.equal(p.detail_count_eligible,false);
  assert.equal(rosterIdentityMatched(db,e),true);assert.equal(rosterStatusLabel(db,e),'身份已匹配，资料待完善');
  assert(!e.verified_person_id);
  const html=await render(p.person_id);
  assert.equal(html.content,'');assert(html.main.includes('资料待完善'));assert(html.main.includes('尚未建立人物档案'));
  const directory=await route('#/people?school=cqu');assert(!directory.results.includes('#/person/'+p.person_id+'"'));
});

test('actual profile appointment teaching and source-list HTML show cached URLs as text without any active href',async()=>{
  const p=person('cqu-chenke'),html=await render(p.person_id),disabled=cached();assert.equal(disabled.length,2);
  for(const s of disabled){
    assert.equal(s.evidence_status,'official_cached_body_read_direct_404');assert.equal(s.ordinary_https_status,404);
    assert(html.content.includes(esc(s.url)),'Original evidence URL must remain visible');
    assert(!hrefs(html.main+html.content).includes(esc(s.url)),'Disabled URL must not be an anchor');
  }
  const appointments=html.content.split('<h2>任职经历</h2>')[1].split('<h2>公开教学事实</h2>')[0];
  const teaching=html.content.split('<h2>公开教学事实</h2>')[1].split('</section>')[0];
  const sources=html.content.split('<ol class="sources">')[1];
  for(const block of [appointments,teaching,sources]){assert(block.includes('缓存'));assert(block.includes('404'))}
  for(const s of disabled){assert(teaching.includes(esc(s.url)));assert(sources.includes(esc(s.url)))}
  assert(appointments.includes(esc(disabled.find(s=>s.id.endsWith('2025')).url)));
  assert(teaching.includes('2025-09-18'));assert(teaching.includes('不是本人求学学历')||html.content.includes('不是本人求学学历'));
});

test('unaffected available personal and source URLs still navigate in actual HTML',async()=>{
  for(const id of PROFESSIONAL_IDS){
    const p=person(id),html=await render(id),links=hrefs(html.main+html.content);
    assert(links.includes(esc(officialProfileUrl(p))),id);
    for(const s of p.sources.filter(s=>s.navigation_enabled!==false))assert(links.includes(esc(s.url)),`${id}/${s.id}`);
  }
});

test('fact-level disabled flag independently vetoes link when source-level flag is not set',async()=>{
  const changed=structuredClone(db),p=changed.people.find(p=>p.person_id==='cqu-chenke');
  for(const s of p.sources){delete s.navigation_enabled;delete s.navigation_available;}
  const html=await render(p.person_id,'profile',changed);
  const appointments=html.content.split('<h2>任职经历</h2>')[1].split('<h2>公开教学事实</h2>')[0];
  const teaching=html.content.split('<h2>公开教学事实</h2>')[1].split('</section>')[0];
  for(const s of cached())assert(!hrefs(appointments+teaching).includes(esc(s.url)));
});

test('source-level disabled flag independently vetoes fact links when per-fact flag is absent',async()=>{
  const changed=structuredClone(db),p=changed.people.find(p=>p.person_id==='cqu-chenke');
  for(const a of [...p.appointments,...p.teaching])delete a.source_navigation_enabled;
  const html=await render(p.person_id,'profile',changed);
  for(const s of cached())assert(!hrefs(html.main+html.content).includes(esc(s.url)));
});

test('all actual education filters only admit two explicit year-precision Chen Yuhui awards',()=>{
  const regions=['mainland','hmt','overseas','unknown','not_recorded'];
  const continents=['asia','europe','north_america','south_america','africa','oceania','antarctica','unknown','not_recorded'];
  for(const id of ids){
    const p=person(id),awarded=id==='bit-chenyuhui';
    assert.deepEqual(stages(p,'bachelor').map(e=>e.event_id),awarded?['bit-chenyuhui-education-1']:[]);
    assert.deepEqual(stages(p,'doctor').map(e=>e.event_id),awarded?['bit-chenyuhui-education-2']:[]);assert.deepEqual(stages(p,'master'),[]);
    for(const value of ['yes','no','unknown','not_recorded'])assert.equal(matches(p,{ug:value},db.org_units),value===(awarded?'yes':'not_recorded'),`${id}/ug/${value}`);
    for(const value of regions){assert.equal(matches(p,{doctor:value},db.org_units),value===(awarded?'mainland':'not_recorded'));assert.equal(matches(p,{master:value},db.org_units),value==='not_recorded')}
    for(const value of continents)assert.equal(matches(p,{continent:value},db.org_units),value===(awarded?'asia':'not_recorded'));
    for(const r of regions)for(const c of continents)assert.equal(matches(p,{doctor:r,continent:c},db.org_units),r===(awarded?'mainland':'not_recorded')&&c===(awarded?'asia':'not_recorded'));
  }
});

test('actual Chen Yuhui timeline keeps reversed study interval absent and renders only award years',async()=>{
  const p=person('bit-chenyuhui'),e=p.education[1],html=await render(p.person_id),rows=educationRows(html);
  assert.equal(e.start,null);assert.equal(e.end,null);assert.equal(e.degree_awarded_date,'2013');
  assert.equal(p.education[0].degree_awarded_date,'2008');
  assert(rows[1].includes('授位日期：2013 '));assert(rows[0].includes('授位日期：2008 '));
  assert(!html.content.includes('2013-2008'));assert(!html.content.includes('授位日期：2013-'));
});

test('actual lineage has one source-bound doctoral relation and no current mentor navigation',async()=>{
  const p=person('bit-chenyuhui'),m=p.mentors[0],html=await render(p.person_id,'lineage');
  assert.equal(m.type,'doctoral_supervisor');assert.equal(m.name,'李志远');
  assert.deepEqual(mentorEvents(p,m).map(e=>e.event_id),['bit-chenyuhui-education-2']);
  assert.equal(mentorOfficialUrl(m),'');assert.equal(mentorProfileRoute(m,db.people),'');
  assert.equal(m.start,null);assert.equal(m.end,null);assert(html.graph.includes('李志远'));
  assert.equal((html.content.match(/class="mentor-card"/g)||[]).length,1);
  assert(!html.content.includes('查看导师个人主页'));assert(!html.content.includes('查看本库个人档案'));
  assert(!html.graph.includes('张向东'));assert(!html.graph.includes('Research Fellow'));
  for(const id of PROFESSIONAL_IDS.filter(id=>id!==p.person_id)){
    const other=await render(id,'lineage');assert(!other.content.includes('class="mentor-card"'));assert(other.content.includes('尚未取得可直接证明导师身份'));
  }
});

test('Dai employment filters and actual profile keep frontier institute separate from optical physics sampling',async()=>{
  const p=person('bit-daiyunyun'),html=await render(p.person_id);
  assert.equal(p.department_id,'bit-frontier-interdisciplinary-institute');assert.equal(p.sampling_affiliation.organization_id,'bit-physics-optical');
  assert.equal(matches(p,{school:'bit',org:'bit-frontier-interdisciplinary-institute'},db.org_units),true);
  assert.equal(matches(p,{school:'bit',org:'bit-physics-optical'},db.org_units),false);
  assert(html.main.includes(esc(p.display_affiliation_note)));assert(html.main.includes('未核物理学院任职或双聘'));
  const employment=html.content.split('<h2>任职经历</h2>')[1].split('<h2>论文')[0];
  assert(employment.includes('北京理工大学前沿交叉科学研究院'));assert(!employment.includes('准聘教授'));assert(!employment.includes('预聘副教授'));
  assert.equal(p.appointments.length,1);assert.equal(p.appointments[0].title,null);
});

test('removing all pending candidates changes no real profile graph filters or source links',async()=>{
  const changed=structuredClone(db);
  for(const p of changed.people.filter(p=>PROFESSIONAL_IDS.includes(p.person_id)))
    for(const key of ['pending_education_candidates','pending_appointment_candidates','pending_mentor_candidates','pending_professional_fact_candidates'])p[key]=[];
  for(const id of PROFESSIONAL_IDS){
    assert.deepEqual(await render(id,'profile',changed),await render(id));
    assert.deepEqual(await render(id,'lineage',changed),await render(id,'lineage'));
  }
});

test('research aliases and selected publication metadata appear in actual profile without fabricating verified article links',async()=>{
  for(const id of PROFESSIONAL_IDS){
    const p=person(id),html=await render(id);
    if(p.research_fields.length){const value=p.research_fields.map(f=>f.name).join('；');assert.equal(p.research_interests,value);assert(html.content.includes(esc(value)))}
    for(const pub of p.publications){assert(html.content.includes(esc(pub.title)));assert.equal(pub.individual_article_link_verified,false);assert.equal(pub.link_status,'official_publication_list_only');assert.equal(pub.doi,null)}
  }
});

test('547 original profiles retain 122-filter outputs and exact labels except four approved same-kind improvements',()=>{
  const people=db.people.slice(0,547),regions=['mainland','hmt','overseas','unknown','not_recorded'];
  const continents=['asia','europe','north_america','south_america','africa','oceania','antarctica','unknown','not_recorded'];
  const filters=[...['yes','no','unknown','not_recorded'].map(v=>({ug:v})),...['master','doctor'].flatMap(key=>regions.map(v=>({[key]:v}))),...['master_continent','continent'].flatMap(key=>continents.map(v=>({[key]:v}))),...regions.flatMap(r=>continents.flatMap(c=>[{master:r,master_continent:c},{doctor:r,continent:c}]))];
  assert.equal(filters.length,122);
  const approved=new Set(['nwsuaf-gengnan-education-1','nudt-hudewen-education-1','nudt-lixiang-education-1','nudt-lidongxu-education-1']);
  let changed=0;
  const labels=people.map(p=>[p.person_id,p.education.map(e=>{
    if(!approved.has(e.event_id))return educationStageLabel(e);
    changed++;assert.equal(e.event_kind,'education_level_unknown');assert.equal(e.degree,null);assert.equal(e.degree_awarded,null);
    assert.equal(educationStageLabel(e),'学习经历（层次与授位未核实）');return '研究经历';
  })]);
  assert.equal(changed,4);assert.equal(digest(labels),BASELINE_PINS.labels_sha256);
  assert.equal(digest(people.map(p=>[p.person_id,['bachelor','master','doctor'].map(k=>stages(p,k).map(e=>e.event_id??null)),filters.map(f=>matches(p,f,db.org_units))])),BASELINE_PINS.outcomes_sha256);
});

test('all six static asset references use the same exact release25 token',()=>{
  for(const [file,count]of Object.entries({'site/app.js':3,'site/rosters.js':1,'site/index.html':2})){
    const source=historicalBytes(file,publishedRoot()).toString('utf8');assert.equal((source.match(/rotation003-20261024-w2/g)||[]).length,count,file);
    assert(!source.includes('rotation002-20261023-w3'),file);
  }
});

test('actual consumers are read-only and school counts remain partial professional plus separate pending',async()=>{
  const before=JSON.stringify(db);
  for(const school of Object.keys(EXPECTED_IDS)){const stats=schoolStats(db,school);assert.equal(stats.status,'部分收录');assert.equal(stats.people,db.people.filter(p=>p.school_id===school).length)}
  for(const id of PROFESSIONAL_IDS){await render(id);await render(id,'lineage')}
  assert.equal(JSON.stringify(db),before);
});

// Optional audit-only controls run against a separately supplied immutable predecessor.
// Ordinary repository tests never depend on baseline or research directories.
if(process.env.ACADEMIC_ATLAS_NEGATIVE_CONTROL_ROOT){
  const baseline=process.env.ACADEMIC_ATLAS_NEGATIVE_CONTROL_ROOT;
  test('baseline negative control: actual old app wrongly exposes both cached source URLs as active links',async()=>{
    const html=await render('cqu-chenke','profile',db,baseline);
    for(const s of cached())assert(hrefs(html.content).includes(esc(s.url)),'Control must demonstrate original href leak');
  });
  test('baseline negative control: actual old app uses generic research fallback for unknown education level',async()=>{
    const html=await render('cqu-chenke','profile',db,baseline),rows=educationRows(html);
    assert(rows[0].includes('<p>研究经历</p>'));assert(!rows[0].includes('学习经历（层次与授位未核实）'));
  });
}

test('reviewed cross-unit roster identity retains sampling unit and shows explicit employment limitation',async()=>{
  const p=person('bit-daiyunyun'),e=db.rosters.entries.find(e=>e.id===p.roster_entry_id);
  assert.equal(rosterSamplingIdentityMatched(db,e,p),true);assert.equal(e.organization_id,'bit-physics-optical');
  assert.equal(e.profile_department_id,'bit-frontier-interdisciplinary-institute');
  const html=await route('#/roster/'+e.id);
  assert(html.main.includes(esc(p.display_affiliation_note)));assert(html.main.includes('独立核验的官方个人主页（任职状态另核）'));
  assert(hrefs(html.main).includes(esc(p.official_url)));assert(html.main.includes('光学物理系'));
});

test('actual cross-unit roster consumer rejects missing evidence and mismatched targets without inventing current employment',()=>{
  const original=person('bit-daiyunyun'),entry=db.rosters.entries.find(e=>e.id===original.roster_entry_id);
  const mutations={
    missing_sampling_unit:(e,p)=>delete p.sampling_affiliation.organization_id,
    missing_sampling_url:(e,p)=>delete p.sampling_affiliation.source_url,
    missing_profile_department:(e,p)=>delete e.profile_department_id,
    missing_profile_organization:(e,p)=>delete e.profile_organization_id,
    wrong_school:(e,p)=>e.school_id='cqu',wrong_name:(e,p)=>e.name='other-person',
    wrong_verified_person:(e,p)=>e.verified_person_id='bit-chentian',wrong_source_person:(e,p)=>e.source_person_id='bit-chentian',
    missing_review_pin:(e,p)=>delete e.profile_identity_evidence.independent_review_sha256,
    missing_source_pin:(e,p)=>delete e.profile_identity_evidence.reviewed_source_sha256,
    missing_sources:(e,p)=>p.sources=[],missing_identity:(e,p)=>p.identity_evidence={},
    missing_identity_date:(e,p)=>delete e.profile_identity_evidence.checked_on,
    unclosed_evidence_source:(e,p)=>e.profile_identity_evidence.source_ids.push('unknown-source'),
    candidate_only:(e,p)=>Object.assign(e,{profile_identity_verified:false,verified_person_id:null,candidate_person_ids:[p.person_id]}),
    pending_person:(e,p)=>p.detail_count_eligible=false,joint_appointment_claim:(e,p)=>p.sampling_affiliation.joint_appointment_verified=true,
    changed_profile_query:(e,p)=>e.official_profile_url+='?unreviewed_identity=other',
    unavailable_person:(e,p)=>p.official_profile_availability='unavailable',
  };
  for(const [name,mutate]of Object.entries(mutations)){
    const e=structuredClone(entry),p=structuredClone(original);mutate(e,p);
    assert.equal(rosterSamplingIdentityMatched(db,e,p),false,name);
    const scoped={...db,people:[p],rosters:{...db.rosters,entries:[e]}},main={innerHTML:''};
    renderRosters(scoped,main,e.id,p.school_id);
    assert(!main.innerHTML.includes('独立核验的官方个人主页（任职状态另核）'),name);
    if(name==='candidate_only'){
      assert(!main.innerHTML.includes('进入已核实身份的人物档案'));
      assert(main.innerHTML.includes('尚未合并'));
    }
  }
  const p=structuredClone(original),e=structuredClone(entry);
  delete p.sampling_affiliation.organization_id;delete e.sampling_affiliation.organization_id;delete e.organization_id;
  assert.equal(rosterSamplingIdentityMatched(db,e,p),false,'both sampling units absent');
});

if(process.env.ACADEMIC_ATLAS_NEGATIVE_CONTROL_ROOT){
  test('actual HTML for all 547 original profile and lineage routes is unchanged except four approved fallback labels',async()=>{
    const approved=new Set(['nwsuaf-gengnan','nudt-hudewen','nudt-lixiang','nudt-lidongxu']);
    for(const p of db.people.slice(0,547))for(const mode of ['profile','lineage']){
      const old=await render(p.person_id,mode,db,process.env.ACADEMIC_ATLAS_NEGATIVE_CONTROL_ROOT);
      const current=await render(p.person_id,mode);
      for(const key of ['main','content','graph']){
        const actual=approved.has(p.person_id)?current[key].replaceAll('学习经历（层次与授位未核实）','研究经历'):current[key];
        assert.equal(actual,old[key],`${p.person_id}/${mode}/${key}`);
      }
    }
  });
}
