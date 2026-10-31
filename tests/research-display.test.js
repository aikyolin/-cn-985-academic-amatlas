import {test} from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {researchInterestsText,escapeHtml,matches} from '../site/model.js';
import {readAtlasFile} from './atlas-test-io.js';
import {createImmutableCohortRenderer} from './immutable-cohort-renderer.js';
const db=readAtlasFile(new URL('../site/atlas.json',import.meta.url));
const roster=JSON.parse(fs.readFileSync(new URL('../site/rosters.json',import.meta.url)));
const expected={
 'nwpu-chenqun':'渐进机器学习、人工智能风险分析、DB&AI融合',
 'sysu-chailihui':'应用数学、偏微分方程数值解',
 'sysu-chenpeng':'调和分析',
 'sysu-chenbinglong':'几何分析',
 'tongji-chenliang':'三维重建、物理AI、深度学习鲁棒性',
 'tongji-chensuqin':'偏微分方程数值算法',
 'tongji-chenxiongda':'非线性规划'
};
test('normalizer retains string bytes, handles absence and only declared text shapes',()=>{
 for(const s of ['plain','  spaced  ','','<img src=x onerror=alert(1)>'])assert.equal(researchInterestsText(s),s);
 for(const v of [null,undefined,0,false,{}, {text:'not an array'},[['nested']], [{text:{secret:'hidden'}}],[{source_url:'hidden',source_id:'hidden'}]])assert.equal(researchInterestsText(v),'');
 assert.equal(researchInterestsText(['A',{text:'B',source_url:'SECRET'},{note:'SECRET'},false,null,[],{text:3},'', '  ']),'A、B');
 assert.equal(researchInterestsText([Object.create({text:'inherited'})]),'');
});
test('HTML escaping remains at output boundary, with no object/provenance stringification',()=>{
 const value=[{text:'<script>"x" & \'y\'</script>',source_url:'SECRET'}];
 assert.equal(escapeHtml(researchInterestsText(value)),'&lt;script&gt;&quot;x&quot; &amp; &#39;y&#39;&lt;/script&gt;');
 assert(!researchInterestsText(value).includes('SECRET'));
});
test('all canonical scalar/null values preserved; exactly7 array records supported',()=>{
 assert.equal(db.people.length,1318);
 assert.deepEqual(db.people.filter(p=>Array.isArray(p.research_interests)).map(p=>p.person_id).sort(),Object.keys(expected).sort());
 for(const p of db.people){const old=p.research_interests;assert.equal(researchInterestsText(old),typeof old==='string'?old:Array.isArray(old)?expected[p.person_id]:'');}
});
for(const [id,text] of Object.entries(expected))test('real research text searchable: '+id,()=>{
 const p=db.people.find(p=>p.person_id===id),before=JSON.stringify(p);
 assert.equal(researchInterestsText(p.research_interests),text);
 for(const term of text.split('、'))assert(matches(p,{q:term},db.org_units));
 assert(!matches(p,{q:'[object Object]'},db.org_units));
 assert(!matches(p,{q:'source_id'},db.org_units));
 assert.equal(JSON.stringify(p),before);
});
const {render}=createImmutableCohortRenderer({db,roster,fixtureId:import.meta.url});
test('real table renderer displays7 exact text-only descriptions',async()=>{
 const nodes=await render('#/people');const html=nodes('#results').innerHTML;
 for(const [id,text] of Object.entries(expected)){assert(html.includes('href="#/person/'+id+'"'));assert(html.includes('<small>'+escapeHtml(text)+'</small>'));}
 assert(!html.includes('[object Object]'));
});
for(const [id,text] of Object.entries(expected))test('real profile research sidebar: '+id,async()=>{
 const nodes=await render('#/person/'+id);const html=nodes('#profile-content').innerHTML;
 assert(html.includes('<h3>研究方向</h3><p>'+escapeHtml(text)+'</p>'));assert(!html.includes('[object Object]'));
});
test('no search leakage of research provenance',()=>{
 for(const id of ['tongji-chensuqin','tongji-chenxiongda']){const p=db.people.find(p=>p.person_id===id);for(const item of p.research_interests){assert(!matches(p,{q:item.source_url},db.org_units));assert(!matches(p,{q:item.source_id},db.org_units));}}
});
