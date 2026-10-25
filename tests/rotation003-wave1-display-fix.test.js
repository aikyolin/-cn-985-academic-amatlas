import {publishedRoot} from './published-fixture.js';
import {historicalBytes} from './source-date-history.js';
import {endpointSha256} from './public-append-history.js';
const RELEASE31_PUBLIC_METADATA_PIN_OVERLAY={"data/atlas.json": "2f843a600ef79f9b6d24ee98b702ed17dc335c776c4893f0316b5064ba3474fb", "data/rosters.json": "fa3fd547a59c10a5e6285523fbcd5e3215b6076f59f0a9246554fedbf2e3a83e", "site/atlas.json": "7d712a1f1e7d83d6093242dd0e9e12bb9d39d2183c33e4f7ffdecb2846caa327", "site/rosters.json": "35cad326388607f1abac4e9efbd05dbefa1eb4a1a7b7ffbc1ed194a1ee56dc27"};
const RELEASE31_PIN_OVERLAY={"data/atlas.json": "28643e5c9a1d67007146dba8a2e6d410008deba5a5a1fcabdd10979f408fd679", "data/rosters.json": "3e47fc6836bde53790d63b6c2c6347fad614ecff63c8548051398ef8bd7eb3ca", "site/atlas.json": "47e92ca3f762d8921aa8bc6ab8f150c6d20d509d29bdee307cf5fecd6d263470", "site/rosters.json": "fd18bd4a98d291c4a441d4f1ac2ec7f7e4e684cf1e406965fa2c6a6cbd8fe4b1"};
const RELEASE30_PIN_OVERLAY={"data/atlas.json": "7bcbb58ea605ea73fec2a51412850550533ba5617d3f200d3812d10551c534fe", "data/rosters.json": "8be8881d52699b7417e5ae7e542629d64156744d524c581c856faf6172878313", "site/atlas.json": "8a2fe871c7262ffc0a2f3edddb5b970a27382b9f5b85797c44f29f3be7582e4b", "site/rosters.json": "c837c259317159de566137c0227866a1fd7224020afbe1e37ab515ffb8a4f0a2"};
const RELEASE29_PIN_OVERLAY={"data/atlas.json": "e2cbfcde9c8f96ebc9e96a0829fe95698428b672fd611ab6dff1078eafa75303", "data/rosters.json": "854ff13b8c352b68a51a20c1cd322f638664de68fdf4996bb922dc344250d11b", "site/atlas.json": "4b976d4c2e4a5b0beb1c838263ade37ece4fd8b5561ab8517d8ad83e13ca0996", "site/rosters.json": "e9ac62ce2ff63201b443717af9da4468d449521238dcde53c79fad7e9676c904"};
const RELEASE28_PIN_OVERLAY={"data/atlas.json": "184d94676b19b55d24d00b9c6056748a3a778754dd920a1a126be21685168d61", "data/rosters.json": "eefa9fe9add7c8dd9aaa49b81deeda73e51a8a1b214a9a6b3a26a2429110de29", "site/atlas.json": "36fe06b748feef6919e105ce3fa81c58426b43d8374ccb03b2d828960462ed8b", "site/rosters.json": "84edc29d2a70ef04d809effe8b3757cba2d614d469691bb16a8ce9f711b052cc"};
const RELEASE27_PIN_OVERLAY={"data/atlas.json": "602e459ef4bc62aa839e8eff7475819f5a6672e1492b1181ac9188372fe9d1c5", "data/rosters.json": "217716511dc290970fd8708af5cacebaf5f1343b1ec671515b5048e5f81dabec", "site/atlas.json": "1d2e8210a0ca6d60b874d793bd77e49de7da6f845493eb6912b0f4861e57afa2", "site/rosters.json": "4971f6b3812c6f8d133fd0aba909e65f2209b72cfb0d37e668c62531ec0446cc"};
const RELEASE26_PIN_OVERLAY={"data/rosters.json": "bdc4f7a400bb2b983d341b434b636aaf2f1beeb5f3aa070486a0aa44920fe27a", "site/index.html": "a6e57e88a623157fd3103a6099b9e72b21a0435c9fa62530a41469814844242c", "site/app.js": "19945c1392982e4b3a1df95d93c271e957bf16b2a238f8d63d24ed892c722dea", "site/rosters.js": "d060662fe29e2d5209ca7cabd89121f253c6df69878d776e652f2fe8f8eb45a9"};
import {release25View} from './release-history.js';
// Focused offline consumer tests for two evidence-bound teaching-role aliases.
// Frozen original teaching fixtures and unchanged real app provide negative controls.
import {test} from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {createHash} from 'node:crypto';
import {fileURLToPath,pathToFileURL} from 'node:url';
const LAYOUT_FIX_APPLICATION_SHA256={"site/styles.css": "3b01ec6a5674982d048237e5426aa107bd622662d2758913c81bc6f5c4c0ceca", "site/app.js": "5ce1dbc7161a048ab263cdff313bc904544b362c13d39cc5963886b409f037e2", "site/rosters.js": "7536ef08c4032e05e1ad3c09532858dd42fd68c20968c82e2146481cf6d9c85f", "site/index.html": "7e6331d4846c13d64f0a5b5b65a9d52539df537b2ce20ef26563669739f8f2a3"};
const root=process.env.ACADEMIC_ATLAS_TEST_ROOT||path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const read=name=>JSON.parse(fs.readFileSync(path.join(root,name),'utf8'));
const db=release25View(read('data/atlas.json'),'data/atlas.json');db.rosters=release25View(read('data/rosters.json'),'data/rosters.json');
const {stages,matches,educationStageLabel}=await import(pathToFileURL(path.join(root,'site/model.js')));
const sha=x=>createHash('sha256').update(x).digest('hex');
const objectSha=x=>sha(JSON.stringify(x));
const person=db.people.find(p=>p.person_id==='cqu-chenke');
const esc=x=>String(x??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const BASELINE_TEACHING = [{"course":"建筑设计(1)+(2)","level":null,"period":null,"source_id":"cqu-chenke-teaching-2021","source_url":"https://news.cqu.edu.cn/archives/news2/content/2021/04/01/eeab4ef47653f3eca46265fa0c4a0a4d4a1eb0e4.html","source_navigation_enabled":false,"source_availability":"direct_404_cached_body_only","evidence_status":"official_cached_body_read_direct_404","field_provenance":{"course":"cqu-chenke-teaching-2021","level":null,"period":null,"note":["cqu-chenke-teaching-2021"]},"field_status":{"course":"source_reported","level":"not_disclosed","period":"not_disclosed"},"as_of":"2021-04-01","status":"historical_source_reported","note":"报道明确主讲课程；未声称2026仍授课。","source_note":"报道明确主讲课程；未声称2026仍授课。","note_derivation":"verbatim_original_note_level_and_period_for_existing_teaching_consumers"},{"course":"泛设计思维","level":null,"period":"2025-09-18","source_id":"cqu-chenke-lecture-2025","source_url":"https://news.cqu.edu.cn/archives/news2/content/2025/09/19/6bab3d43eb9c2f730772541ee4d983ff5aced5f3.html","source_navigation_enabled":false,"source_availability":"direct_404_cached_body_only","evidence_status":"official_cached_body_read_direct_404","field_provenance":{"course":"cqu-chenke-lecture-2025","level":null,"period":"cqu-chenke-lecture-2025","note":["cqu-chenke-lecture-2025"]},"field_status":{"course":"source_reported","level":"not_disclosed","period":"source_reported"},"activity_type":"public_science_lecture","status":"historical_source_reported","note":"系列讲座首场、18日晚由本人主讲；不是学期课程或长期任课。；来源教学时期：2025-09-18","source_note":"系列讲座首场、18日晚由本人主讲；不是学期课程或长期任课。","note_derivation":"verbatim_original_note_level_and_period_for_existing_teaching_consumers"}];
const BASELINE_TEACHING_HTML = "<section class=\"info-panel\"><h2>公开教学事实</h2><p class=\"footnote\">以下是教师承担的教学或课程建设，不是本人求学学历。教学／课程开设时间不是入学、授位或任职起点；不计入教育、任职、论文、导师统计及师承图。</p><ul><li><strong>建筑设计(1)+(2)</strong> · 具体教学角色未披露<p>报道明确主讲课程；未声称2026仍授课。</p><span class=\"source-link source-unavailable\">教学事实来源（来源导航不可用）<br><small>官方旧文完整缓存正文已读；原地址直连404，仅支持历史事实，关闭失效来源导航。 原始地址：https://news.cqu.edu.cn/archives/news2/content/2021/04/01/eeab4ef47653f3eca46265fa0c4a0a4d4a1eb0e4.html</small></span></li><li><strong>泛设计思维</strong> · 具体教学角色未披露<p>系列讲座首场、18日晚由本人主讲；不是学期课程或长期任课。；来源教学时期：2025-09-18</p><span class=\"source-link source-unavailable\">教学事实来源（来源导航不可用）<br><small>官方旧文完整缓存正文已读；原地址直连404，仅支持历史事实，关闭失效来源导航。 原始地址：https://news.cqu.edu.cn/archives/news2/content/2025/09/19/6bab3d43eb9c2f730772541ee4d983ff5aced5f3.html</small></span></li></ul></section>";
const OTHER_TEACHING_HTML_SHA256 = "463770cb0e59e2c88beddef8a946e32f19df47b2637ac2c14159e93ed0ce387a";
const UNCHANGED_FILES = {"data/rosters.json":"593f845e1688780d2dab562883048383e80e0f5921689ef6446df444dac7a396","site/app.js":"5d4efe8a3c85cbca0125b950a70d7494e3d34a2e67240e6043347903965c8d4b","site/model.js":"9dbc155288c1ee0a93fd5d11cd8a7c63724dc0bde6b117a2f71d327e34be3fef","site/rosters.js":"e4bb3c53da7a4ff3c00c1109651d66cc479c20dc265e7705e41213e3019a3502","site/styles.css":"6063be4c04726d2dcf01a0442d5dc4d763b99c835a4110bd943799582c14fc34","site/universities.js":"9323dad42fc2c35808ad92888cdffb0ad41edaefaee88c3b57ebb798349c2d62","site/index.html":"3b5f7afdd4ac96aaca402884976bccb33cb9a1d2a1ad27793cf7cdd82e5970bf","scripts/build.py":"92b6ec03d18666503a7e890e09faffe2e3ac7be61b017ec85b291c1498addacb","scripts/build_rosters.py":"29c5dee611bfaef3fd6afd1df9480b254652c51b1c4ce1c9568d75cb799319fe","scripts/deterministic_xlsx.py":"65158f54d001eebb2ac586fd820cd69deed8e5c96ed5b117668ced51c11dc300"};
// Offline actual-app harness. No browser, external fetch, or output writes.
let serial=0;
async function fixture(input,root){
 const view=structuredClone(input),nodes=new Map(),listeners={};
 view.build_id=view.rosters.build_id='display-fix-independent-fixture';view.exports||=[];
 const node=key=>{if(!nodes.has(key))nodes.set(key,{innerHTML:'',textContent:'',value:'',style:{},dataset:{height:'320'},clientWidth:960,addEventListener(){},click(){this.onclick?.()},scrollIntoView(){},querySelector(selector){return node(selector)}});return nodes.get(key)};
 const document={querySelector:node,querySelectorAll:()=>[],getElementById:id=>node('#'+id)},location={hash:'#/'},window={scrollTo(){},addEventListener(name,fn){listeners[name]=fn}};
 const fetch=async request=>{assert.match(String(request),/^(atlas|rosters)\.json(?:\?|$)/,'External fetch prohibited');return {ok:true,json:async()=>structuredClone(String(request).startsWith('atlas.json')?view:view.rosters)}};
 const activate=()=>Object.assign(globalThis,{document,location,window,fetch});activate();
 await import(pathToFileURL(path.join(root,'site/app.js')).href+'?displayfix-independent='+serial++);
 assert.equal(typeof listeners.hashchange,'function');
 return {render(id,mode='profile'){activate();for(const n of nodes.values())n.innerHTML='';location.hash='#/person/'+id+(mode==='lineage'?'/lineage':'');listeners.hashchange();return {main:node('#main').innerHTML,content:node('#profile-content').innerHTML,graph:node('#mind-stage').innerHTML}}};
}
const teachingSection=html=>(html.content.match(/<section class="info-panel"><h2>公开教学事实<\/h2>([\s\S]*?)<\/section>/)||[])[0]||'';
const original=structuredClone(db);original.people.find(p=>p.person_id==='cqu-chenke').teaching=structuredClone(BASELINE_TEACHING);
let currentFixture,originalFixture;
const current=()=>currentFixture??=fixture(db,root);
const prior=()=>originalFixture??=fixture(original,root);
const hrefs=html=>[...html.matchAll(/\bhref="([^"]*)"/g)].map(m=>m[1]);
const restoreHeadings=html=>html.replaceAll('</strong> · 主讲','</strong> · 具体教学角色未披露');

test('exactly the two historical teaching facts acquire source-bound 主讲 aliases',()=>{
 assert.equal(person.teaching.length,2);
 for(const [i,row]of person.teaching.entries()){
  const raw=BASELINE_TEACHING[i];assert.equal(row.role,'主讲');assert.equal(row.role_source_id,raw.source_id);assert.equal(row.role_source_url,raw.source_url);
  assert.equal(row.role_source_note,raw.source_note);assert.equal(row.field_provenance.role,raw.source_id);assert.equal(row.field_status.role,'explicit_source_note_normalized');
  assert.equal(row.role_derivation,'consumer_alias_from_explicit_reviewed_source_note');
  const restored=structuredClone(row);
  for(const key of ['role','role_source_id','role_source_url','role_source_note','role_derivation'])delete restored[key];
  delete restored.field_provenance.role;delete restored.field_status.role;
  assert.deepEqual(restored,raw);
 }
});

test('actual teaching headings display 主讲 instead of contradicting their explicit source notes',async()=>{
 const html=(await current()).render(person.person_id),section=teachingSection(html);
 assert.equal((section.match(/<\/strong> · 主讲/g)||[]).length,2);
 assert(!section.includes('具体教学角色未披露'));
 for(const row of person.teaching){assert(section.includes('<strong>'+esc(row.course)+'</strong> · 主讲'));assert(section.includes(esc(row.note)))}
});

test('actual unchanged app with frozen original teaching reproduces both former contradictions',async()=>{
 const html=(await prior()).render(person.person_id),section=teachingSection(html);
 assert.equal(section,BASELINE_TEACHING_HTML);assert.equal((section.match(/具体教学角色未披露/g)||[]).length,2);
 assert(section.includes('报道明确主讲课程'));assert(section.includes('由本人主讲'));
});

test('actual teaching HTML changes only the two role headings and no surrounding text or source markup',async()=>{
 const html=(await current()).render(person.person_id),section=teachingSection(html);
 assert.equal(restoreHeadings(section),BASELINE_TEACHING_HTML);
 assert(section.includes('不是本人求学学历'));assert(section.includes('2025-09-18'));
 assert(section.includes('未声称2026仍授课'));assert(section.includes('不是学期课程或长期任课'));
});

test('both cached404 evidence URLs stay visible and nonclickable; unaffected official links stay active',async()=>{
 const f=await current(),html=f.render(person.person_id),section=teachingSection(html),links=hrefs(html.main+html.content);
 for(const row of person.teaching){assert.equal(row.source_navigation_enabled,false);assert.equal(row.status,'historical_source_reported');assert(section.includes(esc(row.source_url)));assert(!links.includes(esc(row.source_url)))}
 assert(section.includes('404'));assert(section.includes('缓存'));assert(links.includes(esc(person.official_url)));
 const old=(await prior()).render(person.person_id);assert.deepEqual(links,hrefs(old.main+old.content));
});

test('all nine other teaching displays remain exactly equal to the frozen release25 HTML',async()=>{
 const f=await current(),other=db.people.filter(p=>p.person_id!==person.person_id&&p.teaching?.length).map(p=>[p.person_id,teachingSection(f.render(p.person_id))]);
 assert.equal(other.length,9);assert.equal(objectSha(other),OTHER_TEACHING_HTML_SHA256);
});

test('all 555 actual profiles and lineage views remain unchanged except the two exact teaching headings',async()=>{
 const now=await current(),old=await prior();
 for(const p of db.people)for(const mode of ['profile','lineage']){
  const actual=now.render(p.person_id,mode),expected=old.render(p.person_id,mode);
  for(const key of ['main','content','graph'])assert.equal(p.person_id===person.person_id?restoreHeadings(actual[key]):actual[key],expected[key],`${p.person_id}/${mode}/${key}`);
 }
});

test('all degree-stage memberships and 122 filter combinations are unchanged by teaching aliases',()=>{
 const regions=['mainland','hmt','overseas','unknown','not_recorded'],continents=['asia','europe','north_america','south_america','africa','oceania','antarctica','unknown','not_recorded'];
 const filters=[...['yes','no','unknown','not_recorded'].map(v=>({ug:v})),...['master','doctor'].flatMap(k=>regions.map(v=>({[k]:v}))),...['master_continent','continent'].flatMap(k=>continents.map(v=>({[k]:v}))),...regions.flatMap(r=>continents.flatMap(c=>[{master:r,master_continent:c},{doctor:r,continent:c}]))];
 assert.equal(filters.length,122);
 for(const [i,p]of db.people.entries()){
  const old=original.people[i];assert.deepEqual(p.education.map(educationStageLabel),old.education.map(educationStageLabel));
  for(const stage of ['bachelor','master','doctor'])assert.deepEqual(stages(p,stage),stages(old,stage));
  assert.deepEqual(filters.map(f=>matches(p,f,db.org_units)),filters.map(f=>matches(old,f,original.org_units)));
 }
 assert.deepEqual(stages(person,'bachelor'),[]);assert.deepEqual(stages(person,'doctor'),[]);
 assert.equal(person.education[0].degree,null);assert.equal(person.education[0].degree_awarded,null);assert.equal(person.mentors.length,0);
});

test('application and exporter match original bytes or the exact reviewed layout-only overlay',()=>{
 for(const [file,digest]of Object.entries(UNCHANGED_FILES))assert.equal(sha(historicalBytes(file,publishedRoot())),endpointSha256(file,RELEASE31_PUBLIC_METADATA_PIN_OVERLAY[file]||RELEASE31_PIN_OVERLAY[file]||RELEASE30_PIN_OVERLAY[file]||RELEASE29_PIN_OVERLAY[file]||RELEASE28_PIN_OVERLAY[file]||RELEASE27_PIN_OVERLAY[file]||RELEASE26_PIN_OVERLAY[file]||LAYOUT_FIX_APPLICATION_SHA256[file]||digest),file);
 for(const [file,n]of [['site/app.js',3],['site/rosters.js',1],['site/index.html',2]])assert.equal(historicalBytes(file,publishedRoot()).toString('utf8').split('rotation003-20261024-w2').length-1,n);
});

test('actual rendering is read-only and does not promote the pending Chen Renwei selection',async()=>{
 const before=JSON.stringify(db),f=await current();f.render(person.person_id);f.render(person.person_id,'lineage');
 const pending=f.render('cqu-chenrenwei');assert.equal(pending.content,'');assert(pending.main.includes('资料待完善'));
 assert.equal(JSON.stringify(db),before);assert.equal(db.people.length,555);assert.equal(db.pending_people.length,84);
});

if(process.env.ACADEMIC_ATLAS_NEGATIVE_CONTROL_ROOT){
 test('immutable release25 actual app reproduces both undisclosed-role headings with original source notes',async()=>{
  const base=process.env.ACADEMIC_ATLAS_NEGATIVE_CONTROL_ROOT;
  const input=JSON.parse(fs.readFileSync(path.join(base,'data/atlas.json')));input.rosters=JSON.parse(fs.readFileSync(path.join(base,'data/rosters.json')));
  const f=await fixture(input,base),section=teachingSection(f.render('cqu-chenke'));
  assert.equal(section,BASELINE_TEACHING_HTML);assert.equal((section.match(/具体教学角色未披露/g)||[]).length,2);
 });
}
