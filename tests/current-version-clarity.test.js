import {readAtlasFile,createAtlasFetch} from './atlas-test-io.js';
import {test} from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {escapeHtml} from '../site/model.js';
const atlas=readAtlasFile(new URL('../site/atlas.json',import.meta.url));
const rosters=JSON.parse(fs.readFileSync(new URL('../site/rosters.json',import.meta.url)));
const app=fs.readFileSync(new URL('../site/app.js',import.meta.url),'utf8');
let serial=0;
async function render(hash,db=structuredClone(atlas),r=structuredClone(rosters)){
 const nodes=new Map(),node=k=>{if(!nodes.has(k))nodes.set(k,{innerHTML:'',textContent:'',value:'',style:{},events:{},dataset:{height:'320'},clientWidth:960,addEventListener(t,f){this.events[t]=f}});return nodes.get(k)};
 globalThis.document={querySelector:node,querySelectorAll:()=>[],getElementById:id=>node('#'+id)};
 globalThis.location={href:"https://atlas.test/site/index.html",hash};globalThis.window={scrollTo(){},addEventListener(){}};
 globalThis.fetch=createAtlasFetch(db,r);
 await import('../site/app.js?version-clarity='+serial++);
 return node('#main').innerHTML;
}
function notice(html){const m=html.match(/<p class="notice data-version">([\s\S]*?)<\/p>/g);assert.equal(m?.length,1);return m[0]}
for(const route of ['#/','#/about'])test('actual '+route+' shows current full database count and exact data version',async()=>{
 const h=notice(await render(route));assert(h.includes(`当前已收录 ${atlas.people.length} 份人物资料 · ${atlas.pending_people.length} 条待完善记录`));assert(h.includes(`数据版本：${atlas.build_id}`));assert(h.includes('具体来源检索时间见各记录；版本编号不是检索日期或发布时间'));assert(!h.includes(atlas.updated_at));
});
test('about retains full-database counts even after a school scope query',async()=>{
 const h=notice(await render('#/about?school=csu'));assert(h.includes(`当前已收录 ${atlas.people.length} 份人物资料`));assert(h.includes(`${atlas.pending_people.length} 条待完善记录`));
});
test('actual rendered data version is HTML escaped rather than interpreted',async()=>{
 const db=structuredClone(atlas),r=structuredClone(rosters);db.build_id=r.build_id='<img src=x onerror="alert(1)">&\'';const h=notice(await render('#/about',db,r));assert(h.includes(escapeHtml(db.build_id)));assert(!h.includes('<img'));assert(!h.includes('onerror="'));
});
test('actual notice helper has safe missing-version and missing-array fallbacks',()=>{
 const match=app.match(/^function dataVersionNotice\(\)\{.*\}$/m);assert(match);const call=new Function('db','esc',match[0]+';return dataVersionNotice();');const h=call({},escapeHtml);assert(h.includes('当前已收录 0 份人物资料 · 0 条待完善记录'));assert(h.includes('数据版本：版本未标注'));assert(!h.includes('undefined'));
});
test('missing build still triggers existing mixed-snapshot protection before rendering',async()=>{
 const db=structuredClone(atlas),r=structuredClone(rosters);delete db.build_id;delete r.build_id;const h=await render('#/',db,r);assert(h.includes('资料暂未加载'));assert(h.includes('暂不显示混合统计'));assert(!h.includes('data-version'));
});
test('version notice does not replace source-date metadata or profile evidence',async()=>{
 const h=await render('#/person/csu-yanlei');assert(h.includes('严磊'));assert(!h.includes('notice data-version'));assert(app.includes('sourceRetrievalDateSummary'));assert(app.includes('来源检索日期以逐条来源记录为准'));
});
test('all seven asset cache references consistently name the school-chunk runtime version',()=>{
 for(const [name,n] of [['app.js',4],['index.html',2],['rosters.js',1]]){const s=fs.readFileSync(new URL('../site/'+name,import.meta.url),'utf8');assert.equal(s.split('school-chunks-20261026').length-1,n);assert(!s.includes('appointment-institution-20261025'));}
 assert.match(atlas.build_id,/^[a-f0-9]{16}$/);assert.equal(rosters.build_id,atlas.build_id);
});
