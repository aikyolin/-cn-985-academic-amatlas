// Independent display-only regression. Golden hashes are from immutable release24,
// not recomputed from the candidate. Runtime is offline and writes no build files.
import {test} from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {createHash} from 'node:crypto';
import {fileURLToPath,pathToFileURL} from 'node:url';

const root=process.env.ACADEMIC_ATLAS_TEST_ROOT||path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const {educationStageLabel,stages,matches,mentorEvents}=await import(pathToFileURL(path.join(root,'site/model.js')));
const read=name=>fs.readFileSync(path.join(root,name));
const digest=value=>createHash('sha256').update(value).digest('hex');
const objectDigest=value=>digest(JSON.stringify(value));
const db=JSON.parse(read('data/atlas.json'));
db.rosters=JSON.parse(read('data/rosters.json'));
const person=id=>db.people.find(p=>p.person_id===id);
const event=id=>db.people.flatMap(p=>p.education||[]).find(e=>e.event_id===id);
const UNDERGRADUATE='本科阶段学习（学位及授位未核实）';
const GRADUATE='研究生阶段学习（硕博层次及授位未核实）';
const EXPECTED_CHANGED_LABELS={
  'sysu-liuzhiwei-education-1':UNDERGRADUATE,
  'sysu-liuzhiwei-education-2':GRADUATE,
  'sysu-wutao-education-1':UNDERGRADUATE,
  'scu-yangjieren-education-1':UNDERGRADUATE,
};
const RELEASE25_DATA_SHA256={"data/atlas.json": "0b0fd57d534c40d6ee022fba99ce1958e0acb475404096cda1609287dff85f9f", "data/rosters.json": "fc08f82cf0a161d7ca8882151afcad6a0a7d5be88a8b56b936a6d055e997045a", "site/atlas.json": "a45a2d32578ad53a76b91599ca63c2e82b94eb098879ee967f8ff21b2b78defe", "site/rosters.json": "9e2360b5741d98d0cd9db41efa128bad73c4510b9797c40ed2b1a749f0295c52"};
const RELEASE25_ROLE_DISPLAY_DATA_SHA256={"data/atlas.json": "c091ec997338745db522e4e5434836359223fde281b29c0d7bbf1ee0f4856df8", "site/atlas.json": "b53c075a6e4113c6d82957835d85d6733cb9ba45c42e2a5c72cb9fcc414499c0", "site/rosters.json": "c9ee602e74636e0253cdffc0df814c1048e26784a8954a4c42c67d9a826053ad"};
const RELEASE25_CHANGED_LABEL_IDS=new Set(["nwsuaf-gengnan-education-1", "nudt-hudewen-education-1", "nudt-lixiang-education-1", "nudt-lidongxu-education-1"]);
const RELEASE24_DATA_SHA256={
  'data/atlas.json':'3cc08cd4c3db2651d94e599335809c581357e45335cbd4f8b8283a056d5d54f5',
  'data/rosters.json':'1b90fa0e5f0624a2f6f508161fd40c0fce33d64508db5c6d89a899f01fbb6d17',
  'site/atlas.json':'270290ff41799dac341564ed2340d905b24ff0f2a2d1703c8c005f859affd974',
  'site/rosters.json':'863fb63ca7bda67de8c4b39bf0004c2b4b28601d076263542f9dbf494be78ba6',
};

let fixturePromise;
async function fixture(){
  return fixturePromise??=(async()=>{
    const view=JSON.parse(read('site/atlas.json')),nodes=new Map(),listeners={};
    view.rosters=JSON.parse(read('site/rosters.json'));
    const node=key=>{
      if(!nodes.has(key))nodes.set(key,{innerHTML:'',textContent:'',value:'',style:{},dataset:{height:'320'},clientWidth:960,
        addEventListener(){},click(){this.onclick?.()},scrollIntoView(){},querySelector(selector){return node(selector)}});
      return nodes.get(key);
    };
    const document={querySelector:node,querySelectorAll:()=>[],getElementById:id=>node('#'+id)};
    const location={hash:'#/'},window={scrollTo(){},addEventListener(name,fn){listeners[name]=fn}};
    const fetch=async request=>{
      assert.match(String(request),/^(atlas|rosters)\.json(?:\?|$)/,'Network requests are prohibited');
      return {ok:true,json:async()=>structuredClone(String(request).startsWith('atlas.json')?view:view.rosters)};
    };
    const activate=()=>Object.assign(globalThis,{document,location,window,fetch});activate();
    await import(pathToFileURL(path.join(root,'site/app.js')).href+'?rotation002-wave3-display-fix');
    assert.equal(typeof listeners.hashchange,'function','The actual app must initialize');
    return {node,nodes,listeners,location,activate};
  })();
}
async function render(id,mode='profile'){
  const f=await fixture();f.activate();for(const node of f.nodes.values())node.innerHTML='';
  f.location.hash=`#/person/${id}${mode==='lineage'?'/lineage':''}`;f.listeners.hashchange();
  assert(!f.node('#main').innerHTML.includes('资料暂未加载'));
  return {main:f.node('#main').innerHTML,content:f.node('#profile-content').innerHTML,graph:f.node('#mind-stage').innerHTML};
}
function educationRows(html){
  const section=html.content.split('<h2>任职经历</h2>')[0];
  return [...section.matchAll(/<article>([\s\S]*?)<\/article>/g)].map(match=>match[1]);
}

test('reviewed release25 append endpoint pins all four canonical and generated data files exactly',()=>{
  for(const [file,hash] of Object.entries(RELEASE24_DATA_SHA256))assert.equal(digest(read(file)),RELEASE25_ROLE_DISPLAY_DATA_SHA256[file]||RELEASE25_DATA_SHA256[file]||hash,file);
});

test('exactly four previously generic event fallbacks acquire uncertainty-preserving labels',()=>{
  const affected=db.people.flatMap(p=>p.education||[]).filter(e=>!e.degree&&['undergraduate_study','graduate_study'].includes(e.event_kind));
  assert.deepEqual(affected.map(e=>e.event_id),Object.keys(EXPECTED_CHANGED_LABELS));
  for(const e of affected){
    assert.equal(educationStageLabel(e),EXPECTED_CHANGED_LABELS[e.event_id]);
    assert.equal(e.degree,null);assert.equal(e.degree_awarded,null);assert.equal(e.degree_awarded_date,null);
  }
});

for(const [id,eventIds] of Object.entries({
  'sysu-liuzhiwei':['sysu-liuzhiwei-education-1','sysu-liuzhiwei-education-2'],
  'sysu-wutao':['sysu-wutao-education-1'],
  'scu-yangjieren':['scu-yangjieren-education-1'],
}))test(`actual profile displays reviewed study labels without fabricating awards: ${id}`,async()=>{
  const p=person(id),rows=educationRows(await render(id));
  assert.equal(rows.length,p.education.length,'No source event may be split or added');
  for(const eventId of eventIds){
    const i=p.education.findIndex(e=>e.event_id===eventId),row=rows[i];
    assert(row.includes(EXPECTED_CHANGED_LABELS[eventId]),eventId);
    assert(!row.includes('<p>研究经历'),'Generic fallback must not replace a known study stage');
    assert(row.includes('非确证授位事件，不参与学历筛选'));
    assert(!row.includes('授位日期：'));
  }
});

test('actual lineage renders three undergraduate labels and preserves the unsplit graduate mentor stage',async()=>{
  for(const id of ['sysu-liuzhiwei','sysu-wutao','scu-yangjieren']){
    const html=await render(id,'lineage');
    assert.equal(html.graph.split(UNDERGRADUATE).length-1,1,id);
  }
  const p=person('sysu-liuzhiwei'),html=await render(p.person_id,'lineage');
  assert.equal(p.education.filter(e=>e.event_kind==='graduate_study').length,1);
  assert.equal(p.mentors.length,1);
  assert.deepEqual(mentorEvents(p,p.mentors[0]).map(e=>e.event_id),['sysu-liuzhiwei-education-2']);
  assert(html.graph.includes('研究生（直接正文未细分硕士或博士）'));
  assert(!html.graph.includes(GRADUATE),'An explicit mentor-stage statement stays authoritative');
});

test('explicit Yang combined degree remains unchanged and is never inferred to be an awarded master or doctorate',async()=>{
  const p=person('scu-yangjieren'),e=event('scu-yangjieren-education-2');
  assert.equal(e.event_kind,'graduate_study');assert.equal(e.degree,'硕士、博士');assert.equal(e.degree_awarded,null);
  assert.equal(educationStageLabel(e),'硕士、博士');
  const rows=educationRows(await render(p.person_id));
  assert.equal(rows.length,3);assert(rows[1].includes('<p>硕士、博士 · 材料加工工程</p>'));
  assert(!rows[1].includes(GRADUATE));assert(rows[1].includes('非确证授位事件，不参与学历筛选'));
  for(const type of ['bachelor','master','doctor'])assert.deepEqual(stages(p,type),[]);
  const graph=(await render(p.person_id,'lineage')).graph;
  assert.equal(graph.split('硕士、博士合并阶段（未细分）').length-1,2);
  assert.deepEqual(p.mentors.map(m=>mentorEvents(p,m).map(e=>e.event_id)),[['scu-yangjieren-education-2'],['scu-yangjieren-education-2']]);
});

test('actual doctoral postdoctoral and visiting profile labels retain their reviewed meanings',async()=>{
  const expected={
    'sysu-liuzhiwei':['本科阶段学习（学位及授位未核实）','研究生阶段学习（硕博层次及授位未核实）','学术访问（非学位）'],
    'sysu-wutao':[UNDERGRADUATE,'硕士','历史学博士','博士后研究'],
    'sysu-caotianzhong':['博士'],
    'scu-dutian':['学士','硕士','博士','博士后研究','博士后研究'],
    'scu-chenpan':['工学学士','工学硕士','工学博士','博士后研究','博士后研究'],
    'scu-yangjieren':[UNDERGRADUATE,'硕士、博士','学术访问（非学位）'],
  };
  for(const [id,labels] of Object.entries(expected)){
    assert.deepEqual(person(id).education.map(educationStageLabel),labels);
    const rows=educationRows(await render(id));assert.equal(rows.length,labels.length);
    for(const [i,label] of labels.entries())assert(rows[i].includes(`<p>${label}${person(id).education[i].field?' · ':'</p>'}`),`${id}/${i}`);
  }
});

test('all 1695 unaffected education labels match the immutable predecessor, including provisional degrees',()=>{
  for(const id of RELEASE25_CHANGED_LABEL_IDS){const e=event(id);assert.equal(e.event_kind,'education_level_unknown');assert.equal(e.degree,null);assert.equal(educationStageLabel(e),'学习经历（层次与授位未核实）')}
  const labels=db.people.slice(0,547).flatMap(p=>(p.education||[])
    .map((e,i)=>[p.person_id,i,e.event_id??null,RELEASE25_CHANGED_LABEL_IDS.has(e.event_id)?'研究经历':educationStageLabel(e)])
    .filter(row=>!Object.hasOwn(EXPECTED_CHANGED_LABELS,row[2])));
  assert.equal(labels.length,1695);
  assert.equal(objectDigest(labels),'29b663515dbdbdb42284a5fb402fb6c4c35a636765322fdb7cebdd039006ab23');
});

test('confirmed-degree membership and 122 education filters stay identical for all 547 people',()=>{
  const regions=['mainland','hmt','overseas','unknown','not_recorded'];
  const continents=['asia','europe','north_america','south_america','africa','oceania','antarctica','unknown','not_recorded'];
  const filters=[...['yes','no','unknown','not_recorded'].map(v=>({ug:v})),
    ...['master','doctor'].flatMap(key=>regions.map(v=>({[key]:v}))),
    ...['master_continent','continent'].flatMap(key=>continents.map(v=>({[key]:v}))),
    ...regions.flatMap(r=>continents.flatMap(c=>[{master:r,master_continent:c},{doctor:r,continent:c}]))];
  const outcomes=db.people.slice(0,547).map(p=>[p.person_id,
    ['bachelor','master','doctor'].map(k=>stages(p,k).map(e=>e.event_id??null)),
    filters.map(f=>matches(p,f,db.org_units))]);
  assert.equal(outcomes.length,547);assert.equal(filters.length,122);
  assert.equal(objectDigest(outcomes),'aba4379cde86a609983c49c63b03f6e6166fbf795105d8f5f8de05f58e70719d');
  for(const id of ['sysu-liuzhiwei','sysu-wutao','scu-yangjieren']){
    assert.deepEqual(stages(person(id),'bachelor'),[]);assert(matches(person(id),{ug:'not_recorded'},db.org_units));
  }
  assert.deepEqual(stages(person('sysu-wutao'),'doctor').map(e=>e.event_id),['sysu-wutao-education-3']);
});

test('the six existing asset references move together to the exact reviewed rotation003 token',()=>{
  const counts={'site/app.js':3,'site/rosters.js':1,'site/index.html':2};
  for(const [file,count] of Object.entries(counts)){
    const source=read(file).toString();
    assert.equal((source.match(/rotation003-20261023-w2/g)||[]).length,count,file);
    assert(!source.includes('rotation002-20261023-w1'),file);
  }
});

test('real consumers and model projections do not mutate the canonical source scalars',async()=>{
  const before=JSON.stringify(db);
  for(const id of ['sysu-liuzhiwei','sysu-wutao','sysu-caotianzhong','scu-dutian','scu-chenpan','scu-yangjieren']){
    for(const mode of ['profile','lineage'])await render(id,mode);
    for(const e of person(id).education)educationStageLabel(e);
    for(const type of ['bachelor','master','doctor'])stages(person(id),type);
  }
  assert.equal(JSON.stringify(db),before);
  for(const [file,hash] of Object.entries(RELEASE24_DATA_SHA256))assert.equal(digest(read(file)),RELEASE25_ROLE_DISPLAY_DATA_SHA256[file]||RELEASE25_DATA_SHA256[file]||hash,file);
});
