import {hitAtlas,hitRosters} from './school-scope.js';
import fs from 'node:fs';
import assert from 'node:assert/strict';
import {test} from 'node:test';
import {schoolStats,schoolCampuses,schoolUnits,schoolName,campusId,campusLabel,routeSchool,normalizeSchoolFilters,matches,rosterMatches} from '../site/model.js';
const fixture=()=>JSON.parse(fs.readFileSync(new URL('./fixtures/multischool.json',import.meta.url)));
test('two schools with same-named colleges keep globally distinct IDs and real hierarchy',()=>{
 const d=fixture();assert.equal(schoolUnits(d,'hit').length,2);assert.equal(schoolUnits(d,'pku').length,2);
 assert.equal(schoolUnits(d,'hit')[1].name,schoolUnits(d,'pku')[0].name);
 assert.deepEqual(d.people.filter(p=>matches(p,{org:'pku-test-computing'},d.org_units)).map(p=>p.school_id),['pku']);
 assert.deepEqual(d.people.filter(p=>matches(p,{school:'hit',org:'pku-test-computing'},d.org_units)),[]);
});
test('empty campus data never falls back to HIT and school changes discard incompatible filters',()=>{
 const d=fixture();assert.deepEqual(schoolCampuses(d,'pku'),[]);assert.equal(campusLabel(d,'harbin','pku'),'校区未标注／待核实');
 assert.deepEqual(normalizeSchoolFilters(d,{school:'pku',campus:'harbin',org:'hit-test-computing'}),{school:'pku',campus:'',org:''});
 assert.equal(matches(d.people[1],{school:'pku'},d.org_units),true);assert.equal(matches(d.people[1],{campus:'harbin'},d.org_units),false);
});
test('legacy deep links resolve school from referenced entities, not prior navigation',()=>{
 const d=fixture();assert.equal(routeSchool(d,'campus','harbin'),'hit');assert.equal(routeSchool(d,'campus','all'),'hit');
 assert.equal(routeSchool(d,'org','hit-test-computing','pku'),'hit');assert.equal(routeSchool(d,'person','pku-synthetic-person','hit'),'pku');
 assert.equal(routeSchool(d,'roster','pku-test-roster'),'pku');assert.equal(routeSchool(d,'campus','unknown'),'');
});
test('roster school filter and labels do not conflate same-named units',()=>{
 const d=fixture();assert.equal(campusId(d.rosters.entries[0]),'harbin');assert.equal(campusId(d.rosters.entries[1]),'');
 assert.deepEqual(d.rosters.entries.filter(e=>rosterMatches(d,e,'pku')).map(e=>e.id),['pku-test-roster']);
 assert.equal(rosterMatches(d,d.rosters.entries[0],'pku'),false);assert.equal(rosterMatches(d,d.rosters.entries[1],'','测试乙校'),true);
 assert.equal(schoolName(d,d.people[1].school_id),'测试乙校（虚构）');
});
test('registry, directory-only coverage and detailed profiles are distinct states',()=>{
 const d=fixture();assert.equal(schoolStats(d,'pku').status,'部分收录');d.people=d.people.filter(p=>p.school_id!=='pku');
 assert.equal(schoolStats(d,'pku').published,false);assert.equal(schoolStats(d,'pku').status,'仅目录／资料待核');
 assert.equal(schoolStats(d,'thu').status,'待收录');assert.equal(schoolStats(d,'thu').hasData,false);
});

// Exercise the actual app renderer and route transitions without starting a browser.
let serial=0;
async function app(d=fixture(),hash='#/'){
 const nodes=new Map(),listeners={};
 const node=selector=>{if(!nodes.has(selector))nodes.set(selector,{innerHTML:'',textContent:'',value:'',events:{},style:{},dataset:{height:'320'},clientWidth:960,addEventListener(type,fn){this.events[type]=fn},querySelector:node,click(){this.onclick?.()}});return nodes.get(selector)};
 globalThis.document={querySelector:node,querySelectorAll:()=>[],getElementById:id=>node('#'+id)};
 globalThis.location={hash};globalThis.window={scrollTo(){},addEventListener(type,fn){listeners[type]=fn}};
 globalThis.fetch=async path=>({ok:true,json:async()=>structuredClone(String(path).startsWith('atlas.json')?d:d.rosters)});
 await import('../site/app.js?synthetic-test='+serial++);
 return {node,navigate(hash){location.hash=hash;listeners.hashchange()},change(selector,name,value){node(selector).events.input({target:{name,value}})}};
}
test('actual school pages isolate units and no-campus schools navigate straight to departments',async()=>{
 const ui=await app();ui.navigate('#/school/pku');const html=ui.node('#main').innerHTML,side=ui.node('#sidebar').innerHTML;
 assert(html.includes('测试乙校（虚构）'));assert(html.includes('本批资料未单列校区归属'));assert(html.includes('#/org/pku-test-computing'));
 assert(!html.includes('#/org/hit-test-computing'));assert(!html.includes('甲校测试校区'));assert(!side.includes('campus-nav'));
 ui.navigate('#/campus/harbin');assert(ui.node('#main').innerHTML.includes('测试甲校（虚构）'));assert(!ui.node('#main').innerHTML.includes('#/org/pku-test-computing'));
});
test('school scope notes are historical across schools and remain escaped through repeated navigation',async()=>{
 const d=fixture(),label='初始采样说明（历史范围，不代表当前全部收录）';
 d.institutions[0].scope_note='最初只采样一个单位 <script>unsafe()</script>';d.institutions[1].scope_note='首批仅选3人，不代表当前收录';
 const ui=await app(d,'#/school/hit');let html=ui.node('#main').innerHTML;
 assert(html.includes('<strong>'+label+'：</strong>最初只采样一个单位 &lt;script&gt;unsafe()&lt;/script&gt;'));assert(!html.includes('<script>unsafe()</script>'));
 for(const sid of ['pku','hit','pku']){ui.navigate('#/school/'+sid);html=ui.node('#main').innerHTML;assert.equal((html.match(/初始采样说明/g)||[]).length,1);assert(html.includes(label));assert(html.includes('<strong>1</strong>份已建人物档案'));assert(html.includes('<strong>2</strong>个已整理组织节点'));assert(html.includes('统计不代表全校教师或学院总数'));assert.equal(html.includes('首批仅选3人'),sid==='pku')}
});
test('legacy school scope fallback is historical but no-note schools retain neutral directory guidance',async()=>{
 const d=fixture(),label='初始采样说明（历史范围，不代表当前全部收录）';d.institution={id:'hit'};d.scope_note='旧版甲校首批范围';
 const ui=await app(d,'#/school/hit');assert(ui.node('#main').innerHTML.includes('<strong>'+label+'：</strong>'+d.scope_note));ui.navigate('#/school/pku');const html=ui.node('#main').innerHTML;assert(!html.includes(label));assert(!html.includes(d.scope_note));assert(html.includes('组织节点来自官方目录；合并与隶属关系以各条页面来源为准。'));
});
test('actual teacher filtering and school switches reset campus and org consistently',async()=>{
 const ui=await app(fixture(),'#/org/hit-test-computing');assert(ui.node('#results').innerHTML.includes('甲测试人物'));assert(!ui.node('#results').innerHTML.includes('乙测试人物'));
 ui.change('#filters','school','pku');assert(ui.node('#results').innerHTML.includes('乙测试人物'));assert(!ui.node('#results').innerHTML.includes('甲测试人物'));
 const main=ui.node('#main').innerHTML;assert(main.includes('value="pku" selected'));assert(!main.includes('value="harbin"'));assert(!main.includes('value="hit-test-computing"'));
 assert(ui.node('#sidebar').innerHTML.includes('测试乙校（虚构）'));
 ui.navigate('#/people?school=hit&org=pku-test-computing');assert(ui.node('#results').innerHTML.includes('甲测试人物'));assert(!ui.node('#results').innerHTML.includes('乙测试人物'));
});
test('actual personal breadcrumbs and old HIT routes retain the correct school',async()=>{
 const ui=await app(fixture(),'#/person/pku-synthetic-person');let html=ui.node('#main').innerHTML;assert(html.includes('href="#/school/pku">测试乙校（虚构）'));assert(!html.includes('哈尔滨工业大学'));assert(html.includes('校区未单列／待核实'));
 ui.navigate('#/person/hit-synthetic-person');html=ui.node('#main').innerHTML;assert(html.includes('href="#/school/hit">测试甲校（虚构）'));assert(ui.node('#sidebar').innerHTML.includes('#/campus/harbin'));
});
test('actual roster pages scope counts, rows and profile school breadcrumbs',async()=>{
 const ui=await app(fixture(),'#/rosters?school=pku');assert(ui.node('#main').innerHTML.includes('1个组织，1条整合名录记录 / 1条原始观察'));assert(ui.node('#roster-results').innerHTML.includes('乙名录测试'));assert(!ui.node('#roster-results').innerHTML.includes('甲名录测试'));assert(ui.node('#main').innerHTML.includes('下载全库名录 Excel'));
 ui.navigate('#/roster/pku-test-roster');assert(ui.node('#main').innerHTML.includes('href="#/school/pku">测试乙校（虚构）'));assert(!ui.node('#main').innerHTML.includes('甲校测试校区'));
});
test('actual national home derives school card states and counts only from real data',async()=>{
 const ui=await app();assert(ui.node('#main').innerHTML.includes('目前2所学校有部分人物资料'));assert(ui.node('#main').innerHTML.includes('其余37所待收录'));
 const d=fixture();d.people=d.people.filter(p=>p.school_id==='hit');const directory=await app(d);assert(directory.node('#main').innerHTML.includes('1所仅有目录或待核资料'));assert(directory.node('#school-grid').innerHTML.includes('仅目录／资料待核'));
 const canonical=hitAtlas(JSON.parse(fs.readFileSync(new URL('../site/atlas.json',import.meta.url))));canonical.rosters=hitRosters(JSON.parse(fs.readFileSync(new URL('../site/rosters.json',import.meta.url))));const real=await app(canonical);assert(real.node('#main').innerHTML.includes('目前1所学校有部分人物资料'));assert(real.node('#main').innerHTML.includes('其余38所待收录'));assert.equal((real.node('#school-grid').innerHTML.match(/部分收录/g)||[]).length,1);
});
test('dynamic school campus and department labels are escaped in actual rendering',async()=>{
 const d=fixture(),payload='<script>unsafe()</script>';d.institutions[0].official_name=payload;d.campuses[0].name=payload;d.org_units[1].name=payload;d.org_units[1].source_url='javascript:unsafe()';
 const ui=await app(d,'#/school/hit');for(const selector of ['#main','#sidebar']){assert(!ui.node(selector).innerHTML.includes(payload));assert(ui.node(selector).innerHTML.includes('&lt;script&gt;unsafe()&lt;/script&gt;'));assert(!ui.node(selector).innerHTML.includes('href="javascript:'))}
});
test('uncollected school filter shows its real registry label rather than HIT fallback',async()=>{
 const ui=await app(fixture(),'#/people?school=thu');assert(ui.node('#main').innerHTML.includes('清华大学'));assert(ui.node('#sidebar').innerHTML.includes('清华大学'));assert(!ui.node('#results').innerHTML.includes('甲测试人物'));
});
test('partial professional profiles show explicit coverage labels and never promise complete biographies',async()=>{
 const d=fixture();d.people[1].profile_status='partial_professional_source_checked';d.people[1].profile_coverage_label='仅部分职业履历；教育史与师承未核实 <测试>';
 const ui=await app(d,'#/person/pku-synthetic-person');assert(ui.node('#main').innerHTML.includes('仅部分职业履历；教育史与师承未核实 &lt;测试&gt;'));assert(!ui.node('#main').innerHTML.includes('完整档案'));
 ui.navigate('#/school/pku');assert(ui.node('#main').innerHTML.includes('已建人物档案 · 1'));assert(!ui.node('#main').innerHTML.includes('详细档案'));
});
test('about exposes the verified existing discussion link without a future-only promise',async()=>{
 const ui=await app(fixture(),'#/about');assert(ui.node('#main').innerHTML.includes('href="https://github.com/aikyolin/-cn-985-academic-amatlas/discussions"'));assert(!ui.node('#main').innerHTML.includes('公开发布前将设置纠错入口'));
});
