import {test} from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {UNIVERSITIES} from '../site/universities.js';
import {matches,normalizeSchoolFilters,routeSchool,escapeHtml} from '../site/model.js';
// In-memory synthetic people only; never persist these records to data/ or site/.
function fixture(){
 const d=JSON.parse(fs.readFileSync(new URL('./fixtures/multischool.json',import.meta.url))),template=structuredClone(d.people[1]),entry=structuredClone(d.rosters.entries[1]);
 for(const sid of ['fdu','nju','ustc','buaa','nku']){
  assert(UNIVERSITIES.some(s=>s.id===sid));d.institutions.push({id:sid,official_name:sid+'范围测试（虚构）',official_url:`https://${sid}.example.test/`});
  for(const suffix of sid==='nku'?['cs','cyber']:['test']){
   const id=`${sid}-synthetic-${suffix}`;d.org_units.push({id,school_id:sid,name:'同名测试学院（虚构）',type:'学院',parent_id:sid,campus_ids:[],source_url:`https://${sid}.example.test/${suffix}`});
   const p={...structuredClone(template),person_id:id+'-person',school_id:sid,department_id:id,department:'同名测试学院（虚构）',name:id+'测试人物（虚构）',campus_ids:[],official_url:`https://${sid}.example.test/${suffix}/person`};d.people.push(p);d.exports.push({department_id:id,school_id:sid,path:`exports/${id}.xlsx`,people_count:1});
   d.rosters.entries.push({...structuredClone(entry),id:id+'-roster',school_id:sid,name:p.name,organization_id:id,campus_id:null});d.rosters.coverage.push({school_id:sid,organization_id:id,visible_name_count:1});
  }
 }
 return d;
}
let serial=0;
async function app(d=fixture(),hash='#/'){
 const nodes=new Map(),listeners={};const node=k=>{if(!nodes.has(k))nodes.set(k,{innerHTML:'',textContent:'',value:'',style:{},events:{},dataset:{height:'320'},clientWidth:960,querySelector:node,addEventListener(t,f){this.events[t]=f},click(){this.onclick?.()}});return nodes.get(k)};
 globalThis.document={querySelector:node,querySelectorAll:()=>[],getElementById:id=>node('#'+id)};globalThis.location={hash};globalThis.window={scrollTo(){},addEventListener(t,f){listeners[t]=f}};
 globalThis.fetch=async p=>({ok:true,json:async()=>structuredClone(String(p).startsWith('atlas.json')?d:d.rosters)});
 await import('../site/app.js?new-school-fixture='+serial++);
 assert(!node('#main').innerHTML.includes('资料暂未加载'));
 return {node,navigate(hash){location.hash=hash;listeners.hashchange()}};
}
test('seven synthetic registry schools render dynamically without a five-school cap or HIT campus fallback',async()=>{
 const d=fixture(),before=JSON.stringify(d),ui=await app(d);
 assert(ui.node('#main').innerHTML.includes('目前7所学校有部分人物资料'));assert(ui.node('#main').innerHTML.includes('其余32所待收录'));
 for(const sid of ['fdu','nju','ustc','buaa','nku']){ui.navigate('#/school/'+sid);assert(ui.node('#main').innerHTML.includes(sid+'范围测试（虚构）'));assert(ui.node('#main').innerHTML.includes('本批资料未单列校区归属'));assert(!ui.node('#sidebar').innerHTML.includes('campus-nav'));assert(!ui.node('#main').innerHTML.includes('甲校测试校区'))}
 assert.equal(JSON.stringify(d),before);
});
test('two peer departments keep their own people, export links and school breadcrumbs, not the first unit',async()=>{
 const ui=await app();ui.navigate('#/school/nku');for(const unit of ['nku-synthetic-cs','nku-synthetic-cyber'])assert(ui.node('#sidebar').innerHTML.includes('#/org/'+unit));
 for(const suffix of ['cs','cyber']){const id='nku-synthetic-'+suffix;ui.navigate('#/org/'+id);assert(ui.node('#results').innerHTML.includes(id+'测试人物'));assert(!ui.node('#results').innerHTML.includes('nku-synthetic-'+(suffix==='cs'?'cyber':'cs')+'测试人物'));assert(ui.node('#excel').innerHTML.includes('exports/'+id+'.xlsx'));ui.navigate('#/person/'+id+'-person');assert(ui.node('#main').innerHTML.includes('href="#/school/nku"'));assert(ui.node('#main').innerHTML.includes('href="#/org/'+id+'"'))}
});
test('new-school roster and cross-school filter scope stay separate with empty campuses and old HIT routes',async()=>{
 const d=fixture(),ui=await app(d);ui.navigate('#/rosters?school=nku');assert(ui.node('#main').innerHTML.includes('2个组织，2条整合名录记录 / 2条原始观察'));assert(!ui.node('#roster-results').innerHTML.includes('fdu-synthetic'));assert(ui.node('#roster-results').innerHTML.includes('nku-synthetic-cs'));assert(ui.node('#roster-results').innerHTML.includes('nku-synthetic-cyber'));
 assert.deepEqual(normalizeSchoolFilters(d,{school:'nku',campus:'harbin',org:'fdu-synthetic-test'}),{school:'nku',campus:'',org:''});assert.equal(d.people.filter(p=>matches(p,{school:'nku',org:'nku-synthetic-cyber'},d.org_units)).length,1);assert.equal(routeSchool(d,'campus','harbin'),'hit');
});
const LABELS={official_profile_mentions_book_only:'官方个人页仅提及著作，未核出版商落地页或全文。',official_author_book_metadata_verified:'作者官方职业页面的著作书目元数据已核，不表示出版商页面或全文已读。'};
test('book and both metadata-only evidence levels show Chinese labels without claiming article or full-text verification',async()=>{
 const d=fixture(),p=d.people[1];p.publications=Object.entries(LABELS).map(([link_status,link_status_label],i)=>({title:'合成测试著作'+i,type:'book',type_label:'学术著作（非期刊或会议论文）',link_status,link_status_label,source_url:'https://b.example.test/books'}));const before=JSON.stringify(p);
 const html=(await app(d,'#/person/'+p.person_id)).node('#profile-content').innerHTML;
 assert.equal((html.match(/成果类型：学术著作（非期刊或会议论文）/g)||[]).length,2);for(const label of Object.values(LABELS))assert(html.includes(label));assert(!html.includes('成果类型：book'));assert.equal(JSON.stringify(p),before);assert(p.publications.every(p=>p.type==='book'));
});
test('publication labels are escaped and unknown link states stay uncertain while legacy list-only wording remains',async()=>{
 const d=fixture(),p=d.people[1],payload='<script>unsafe()</script>';p.publications=[{title:'测试成果',type:'unknown_type',link_status:'unrecognized_status',source_url:'https://b.example.test/p'},{title:'旧测试列表',type:'paper',link_status:'official_publication_list_only'},{title:'标签转义',type:'book',type_label:payload,link_status:'metadata',link_status_label:payload}];
 const html=(await app(d,'#/person/'+p.person_id)).node('#profile-content').innerHTML;
 assert(html.includes('成果类型：unknown_type'));assert(html.includes('链接核验状态：unrecognized_status（不代表全文已核）'));assert(html.includes('仅官网成果列表，未核独立论文页/DOI'));assert(html.includes(escapeHtml(payload)));assert(!html.includes(payload));
});
