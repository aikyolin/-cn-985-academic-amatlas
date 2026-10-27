import {createAtlasFetch} from './atlas-test-io.js';
import {publishedRoot} from './published-fixture.js';
import {historicalBytes} from './source-date-history.js';
import {endpointSha256} from './public-append-history.js';
const RELEASE31_PUBLIC_METADATA_PIN_OVERLAY={"data/atlas.json": "2f843a600ef79f9b6d24ee98b702ed17dc335c776c4893f0316b5064ba3474fb", "data/rosters.json": "fa3fd547a59c10a5e6285523fbcd5e3215b6076f59f0a9246554fedbf2e3a83e", "site/atlas.json": "7d712a1f1e7d83d6093242dd0e9e12bb9d39d2183c33e4f7ffdecb2846caa327", "site/rosters.json": "35cad326388607f1abac4e9efbd05dbefa1eb4a1a7b7ffbc1ed194a1ee56dc27"};
const RELEASE31_PIN_OVERLAY={"data/atlas.json": "28643e5c9a1d67007146dba8a2e6d410008deba5a5a1fcabdd10979f408fd679", "data/rosters.json": "3e47fc6836bde53790d63b6c2c6347fad614ecff63c8548051398ef8bd7eb3ca", "site/atlas.json": "47e92ca3f762d8921aa8bc6ab8f150c6d20d509d29bdee307cf5fecd6d263470", "site/rosters.json": "fd18bd4a98d291c4a441d4f1ac2ec7f7e4e684cf1e406965fa2c6a6cbd8fe4b1"};
const RELEASE30_PIN_OVERLAY={"data/atlas.json": "7bcbb58ea605ea73fec2a51412850550533ba5617d3f200d3812d10551c534fe", "data/rosters.json": "8be8881d52699b7417e5ae7e542629d64156744d524c581c856faf6172878313", "site/atlas.json": "8a2fe871c7262ffc0a2f3edddb5b970a27382b9f5b85797c44f29f3be7582e4b", "site/rosters.json": "c837c259317159de566137c0227866a1fd7224020afbe1e37ab515ffb8a4f0a2"};
const RELEASE29_PIN_OVERLAY={"data/atlas.json": "e2cbfcde9c8f96ebc9e96a0829fe95698428b672fd611ab6dff1078eafa75303", "data/rosters.json": "854ff13b8c352b68a51a20c1cd322f638664de68fdf4996bb922dc344250d11b", "site/atlas.json": "4b976d4c2e4a5b0beb1c838263ade37ece4fd8b5561ab8517d8ad83e13ca0996", "site/rosters.json": "e9ac62ce2ff63201b443717af9da4468d449521238dcde53c79fad7e9676c904"};
const RELEASE28_PIN_OVERLAY={"data/atlas.json": "184d94676b19b55d24d00b9c6056748a3a778754dd920a1a126be21685168d61", "data/rosters.json": "eefa9fe9add7c8dd9aaa49b81deeda73e51a8a1b214a9a6b3a26a2429110de29", "site/atlas.json": "36fe06b748feef6919e105ce3fa81c58426b43d8374ccb03b2d828960462ed8b", "site/rosters.json": "84edc29d2a70ef04d809effe8b3757cba2d614d469691bb16a8ce9f711b052cc"};
const RELEASE27_PIN_OVERLAY={"data/atlas.json": "602e459ef4bc62aa839e8eff7475819f5a6672e1492b1181ac9188372fe9d1c5", "data/rosters.json": "217716511dc290970fd8708af5cacebaf5f1343b1ec671515b5048e5f81dabec", "site/atlas.json": "1d2e8210a0ca6d60b874d793bd77e49de7da6f845493eb6912b0f4861e57afa2", "site/rosters.json": "4971f6b3812c6f8d133fd0aba909e65f2209b72cfb0d37e668c62531ec0446cc"};
const RELEASE26_DATA_SHA256={"data/atlas.json": "07d31cc1627dc341802a99c1e57d6ef8d29c82fd115ee0c882ffa9e29830a68d", "data/rosters.json": "bdc4f7a400bb2b983d341b434b636aaf2f1beeb5f3aa070486a0aa44920fe27a", "site/atlas.json": "8ce7435afda1486a9850ac8ffed16018b542e23c2fc337b71598cc2417fc4e80", "site/rosters.json": "f11f1e1a40fd1b28211654fb1a2db4da83e78f28b1fcd96d9cb7e277ff0ae306"};
import {release25View} from './release-history.js';
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
// Exact historical inputs; model/app imports above and below remain LIVE.
const readPublished=name=>historicalBytes(name,publishedRoot());
const digest=value=>createHash('sha256').update(value).digest('hex');
const objectDigest=value=>digest(JSON.stringify(value));
const db=release25View(JSON.parse(readPublished('data/atlas.json')),'data/atlas.json');
db.rosters=release25View(JSON.parse(readPublished('data/rosters.json')),'data/rosters.json');
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
const RELEASE25_DATA_SHA256={"data/atlas.json": "96d98129c6d68768083733019ade3e9514361a773c420f8a5d3244cd09da5ab5", "data/rosters.json": "593f845e1688780d2dab562883048383e80e0f5921689ef6446df444dac7a396", "site/atlas.json": "a45a2d32578ad53a76b91599ca63c2e82b94eb098879ee967f8ff21b2b78defe", "site/rosters.json": "9e2360b5741d98d0cd9db41efa128bad73c4510b9797c40ed2b1a749f0295c52"};
const RELEASE25_ROLE_DISPLAY_DATA_SHA256={"data/atlas.json": "9ce25b398af89032b7f005b7cd67ad277664362e2821ec70cceecb6e602a93fe", "site/atlas.json": "026309acf50ca7d6f59e895bd5d317d856135c6cb257cda68c157a222a07bac7", "site/rosters.json": "8ca6b8ad9e8cffd80fc8bc9dd56fb3abb2f53daea8f57f42097ff8550a6eb719"};
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
    const view=JSON.parse(readPublished('site/atlas.json')),nodes=new Map(),listeners={};
    view.rosters=JSON.parse(readPublished('site/rosters.json'));
    const node=key=>{
      if(!nodes.has(key))nodes.set(key,{innerHTML:'',textContent:'',value:'',style:{},dataset:{height:'320'},clientWidth:960,
        addEventListener(){},click(){this.onclick?.()},scrollIntoView(){},querySelector(selector){return node(selector)}});
      return nodes.get(key);
    };
    const document={querySelector:node,querySelectorAll:()=>[],getElementById:id=>node('#'+id)};
    const location={href:"https://atlas.test/site/index.html",hash:'#/'},window={scrollTo(){},addEventListener(name,fn){listeners[name]=fn}};
    const fetch=createAtlasFetch(view,view.rosters);
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
  for(const [file,hash] of Object.entries(RELEASE24_DATA_SHA256))assert.equal(digest(readPublished(file)),endpointSha256(file,RELEASE31_PUBLIC_METADATA_PIN_OVERLAY[file]||RELEASE31_PIN_OVERLAY[file]||RELEASE30_PIN_OVERLAY[file]||RELEASE29_PIN_OVERLAY[file]||RELEASE28_PIN_OVERLAY[file]||RELEASE27_PIN_OVERLAY[file]||RELEASE26_DATA_SHA256[file]||RELEASE25_ROLE_DISPLAY_DATA_SHA256[file]||RELEASE25_DATA_SHA256[file]||hash),file);
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
    assert(row.includes('本事件未明确记载获授学位，不参与学历筛选'));
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
  assert(!rows[1].includes(GRADUATE));assert(rows[1].includes('本事件未明确记载获授学位，不参与学历筛选'));
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
    const source=readPublished(file).toString();
    assert.equal((source.match(/rotation003-20261024-w2/g)||[]).length,count,file);
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
  for(const [file,hash] of Object.entries(RELEASE24_DATA_SHA256))assert.equal(digest(readPublished(file)),endpointSha256(file,RELEASE31_PUBLIC_METADATA_PIN_OVERLAY[file]||RELEASE31_PIN_OVERLAY[file]||RELEASE30_PIN_OVERLAY[file]||RELEASE29_PIN_OVERLAY[file]||RELEASE28_PIN_OVERLAY[file]||RELEASE27_PIN_OVERLAY[file]||RELEASE26_DATA_SHA256[file]||RELEASE25_ROLE_DISPLAY_DATA_SHA256[file]||RELEASE25_DATA_SHA256[file]||hash),file);
});
