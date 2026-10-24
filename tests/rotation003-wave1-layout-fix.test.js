import {release25View} from './release-history.js';
// Offline actual-app HTML and scoped CSS-cascade regression, not a browser geometry test.
import {test} from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {createHash} from 'node:crypto';
import {fileURLToPath,pathToFileURL} from 'node:url';
const root=process.env.ACADEMIC_ATLAS_TEST_ROOT||path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const read=name=>JSON.parse(fs.readFileSync(path.join(root,name),'utf8'));
const db=release25View(read('data/atlas.json'),'data/atlas.json');db.rosters=release25View(read('data/rosters.json'),'data/rosters.json');
const css=fs.readFileSync(path.join(root,'site/styles.css'),'utf8');
const RULE='.source-unavailable{white-space:normal;overflow-wrap:anywhere;max-width:100%}';
const sha=x=>createHash('sha256').update(x).digest('hex');
const person=db.people.find(p=>p.person_id==='cqu-chenke');
const esc=x=>String(x??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const BASELINE_CSS_SHA256="6063be4c04726d2dcf01a0442d5dc4d763b99c835a4110bd943799582c14fc34";
const BASELINE_ROUTE_SHA256="64e62185c96b4c795d0f8087bc95ac994310f81fb441c28df817f2c22862ca8a";
const BASELINE_SPANS=["<span class=\"source-link source-unavailable\">查看来源（来源导航不可用）<br><small>官方旧文完整缓存正文已读；原地址直连404，仅支持历史事实，关闭失效来源导航。 原始地址：https://news.cqu.edu.cn/archives/news2/content/2025/09/19/6bab3d43eb9c2f730772541ee4d983ff5aced5f3.html</small></span>", "<span class=\"source-link source-unavailable\">教学事实来源（来源导航不可用）<br><small>官方旧文完整缓存正文已读；原地址直连404，仅支持历史事实，关闭失效来源导航。 原始地址：https://news.cqu.edu.cn/archives/news2/content/2021/04/01/eeab4ef47653f3eca46265fa0c4a0a4d4a1eb0e4.html</small></span>", "<span class=\"source-link source-unavailable\">教学事实来源（来源导航不可用）<br><small>官方旧文完整缓存正文已读；原地址直连404，仅支持历史事实，关闭失效来源导航。 原始地址：https://news.cqu.edu.cn/archives/news2/content/2025/09/19/6bab3d43eb9c2f730772541ee4d983ff5aced5f3.html</small></span>", "<span class=\" source-unavailable\">cqu-chenke-teaching-2021（来源导航不可用）<br><small>官方旧文完整缓存正文已读；原地址直连404，仅支持历史事实，关闭失效来源导航。 原始地址：https://news.cqu.edu.cn/archives/news2/content/2021/04/01/eeab4ef47653f3eca46265fa0c4a0a4d4a1eb0e4.html</small></span>", "<span class=\" source-unavailable\">cqu-chenke-lecture-2025（来源导航不可用）<br><small>官方旧文完整缓存正文已读；原地址直连404，仅支持历史事实，关闭失效来源导航。 原始地址：https://news.cqu.edu.cn/archives/news2/content/2025/09/19/6bab3d43eb9c2f730772541ee4d983ff5aced5f3.html</small></span>"];
let serial=0;
async function fixture(input,root){
 const view=structuredClone(input),nodes=new Map(),listeners={};
 view.build_id=view.rosters.build_id='display-fix-independent-fixture';view.exports||=[];
 const node=key=>{if(!nodes.has(key))nodes.set(key,{innerHTML:'',textContent:'',value:'',style:{},dataset:{height:'320'},clientWidth:960,addEventListener(){},click(){this.onclick?.()},scrollIntoView(){},querySelector(selector){return node(selector)}});return nodes.get(key)};
 const document={querySelector:node,querySelectorAll:()=>[],getElementById:id=>node('#'+id)},location={hash:'#/'},window={scrollTo(){},addEventListener(name,fn){listeners[name]=fn}};
 const fetch=async request=>{assert.match(String(request),/^(atlas|rosters)\.json(?:\?|$)/,'External fetch prohibited');return {ok:true,json:async()=>structuredClone(String(request).startsWith('atlas.json')?view:view.rosters)}};
 const activate=()=>Object.assign(globalThis,{document,location,window,fetch});activate();
 await import(pathToFileURL(path.join(root,'site/app.js')).href+'?layoutfix-independent='+serial++);
 assert.equal(typeof listeners.hashchange,'function');
 return {render(id,mode='profile'){activate();for(const n of nodes.values())n.innerHTML='';location.hash='#/person/'+id+(mode==='lineage'?'/lineage':'');listeners.hashchange();return {main:node('#main').innerHTML,content:node('#profile-content').innerHTML,graph:node('#mind-stage').innerHTML}}};
}
const teachingSection=html=>(html.content.match(/<section class="info-panel"><h2>公开教学事实<\/h2>([\s\S]*?)<\/section>/)||[])[0]||'';
// Small explicit HTML-tree/CSS-cascade model. It resolves this page's type/class,
// descendant/child selectors and max-width media rules, not browser line geometry.
function tree(html){
 const root={tag:'root',classes:[],children:[],parent:null,text:''},stack=[root],all=[];
 const voids=new Set(['br','hr','img','input','link','meta','area','base','embed','source','wbr']);
 for(const chunk of html.match(/<[^>]*>|[^<]+/g)||[]){
  if(chunk.startsWith('</')){const tag=chunk.slice(2,-1).trim();while(stack.length>1){const node=stack.pop();if(node.tag===tag)break;}}
  else if(/^<[a-z]/i.test(chunk)){
   const tag=chunk.match(/^<([\w-]+)/)[1].toLowerCase(),attrs={};
   for(const m of chunk.matchAll(/([\w-]+)="([^"]*)"/g))attrs[m[1]]=m[2];
   const node={tag,attrs,classes:(attrs.class||'').trim().split(/\s+/).filter(Boolean),parent:stack.at(-1),children:[],text:''};
   node.parent.children.push(node);all.push(node);if(!voids.has(tag)&&!chunk.endsWith('/>'))stack.push(node);
  }else if(!chunk.startsWith('<'))for(const n of stack)n.text+=chunk;
 }
 return all;
}
function rules(css,width){
 let cursor=0,out=[];
 while(cursor<css.length){
  const start=css.indexOf('{',cursor);if(start<0)break;const selector=css.slice(cursor,start).trim();let level=1,end=start+1;
  while(end<css.length&&level){if(css[end]==='{')level++;if(css[end]==='}')level--;end++;}
  const body=css.slice(start+1,end-1);cursor=end;
  if(selector.startsWith('@media')){const max=selector.match(/max-width:\s*(\d+)px/);if(max&&width<=Number(max[1]))out.push(...rules(body,width));continue;}
  if(selector.startsWith('@'))continue;
  const declarations=Object.fromEntries(body.split(';').filter(x=>x.includes(':')).map(x=>{const i=x.indexOf(':');return[x.slice(0,i).trim(),x.slice(i+1).trim()]}));
  for(const item of selector.split(','))out.push({selector:item.trim(),declarations});
 }
 return out;
}
function matchesSimple(node,selector){
 if(!node||selector.includes(':')||selector.includes('[')||selector.includes('+')||selector.includes('~'))return false;
 const tag=selector.match(/^[\w-]+/);if(tag&&node.tag!==tag[0])return false;
 const id=selector.match(/#([\w-]+)/);if(id&&node.attrs?.id!==id[1])return false;
 return [...selector.matchAll(/\.([\w-]+)/g)].every(m=>node.classes.includes(m[1]));
}
function selectorMatches(node,selector){
 const parts=selector.replaceAll('>',' > ').trim().split(/\s+/);
 function visit(n,i){if(i<0)return true;if(!matchesSimple(n,parts[i]))return false;if(i===0)return true;
  if(parts[i-1]==='>')return visit(n.parent,i-2);
  for(let p=n.parent;p;p=p.parent)if(visit(p,i-1))return true;return false;
 }
 return visit(node,parts.length-1);
}
function styles(nodes,css,width=1164){
 const parsed=rules(css,width),result=new Map();
 for(const node of nodes){
  const parent=result.get(node.parent)||{},style={'white-space':parent['white-space']||'normal','overflow-wrap':parent['overflow-wrap']||'normal',display:['span','small','a','strong'].includes(node.tag)?'inline':'block','max-width':'none'},winners={};
  parsed.forEach((rule,index)=>{if(!selectorMatches(node,rule.selector))return;
   const weight=(rule.selector.match(/#/g)||[]).length*100+(rule.selector.match(/\./g)||[]).length*10+(rule.selector.match(/(?:^|[\s>])\w[\w-]*/g)||[]).length;
   for(const [key,value]of Object.entries(rule.declarations))if(!winners[key]||weight>winners[key][0]||(weight===winners[key][0]&&index>winners[key][1])){style[key]=value;winners[key]=[weight,index];}
  });result.set(node,style);
 }
 return result;
}
const ancestor=(node,cls)=>{for(let p=node.parent;p;p=p.parent)if(p.classes.includes(cls))return true;return false;};
const unavailable=nodes=>nodes.filter(n=>n.classes.includes('source-unavailable'));
const baselineCss=()=>{assert(css.endsWith('\n'+RULE+'\n'));return css.slice(0,-('\n'+RULE+'\n').length)};
let fixturePromise;const current=()=>fixturePromise??=fixture(db,root);
const hrefs=html=>[...html.matchAll(/\bhref="([^"]*)"/g)].map(m=>m[1]);

test('the only style delta is one append-only rule after the original nowrap rule',()=>{
 assert.equal(css.split(RULE).length-1,1);assert.equal(sha(baselineCss()),BASELINE_CSS_SHA256);
 assert(css.indexOf('.source-link{font-size:11px;white-space:nowrap}')<css.indexOf(RULE));
 assert(!/(hidden|clip|ellipsis|display|position|height|inline-block|min-width)/.test(RULE));
});

test('actual profile preserves all five complete inert source spans byte-for-byte',async()=>{
 const html=(await current()).render(person.person_id).content;
 const spans=[...html.matchAll(/<span class="[^"]*source-unavailable">[\s\S]*?<\/span>/g)].map(m=>m[0]);
 assert.deepEqual(spans,BASELINE_SPANS);assert.equal(spans.length,5);
 const nodes=tree(html),blocked=unavailable(nodes);assert.equal(blocked.length,5);
 assert.equal(blocked.filter(n=>ancestor(n,'timeline')).length,1);
 assert.equal(blocked.filter(n=>ancestor(n,'info-panel')).length,2);
 assert.equal(blocked.filter(n=>ancestor(n,'sources')).length,2);
 for(const node of blocked){assert.equal(node.tag,'span');assert(!node.attrs.href);assert(node.text.includes('404'));assert(node.text.includes('缓存'));assert(node.text.includes('https://news.cqu.edu.cn/'));}
});

test('all five source spans and nested URL small elements receive wrapping styles in the actual CSS cascade',async()=>{
 const nodes=tree((await current()).render(person.person_id).content),blocked=unavailable(nodes);
 for(const width of [360,680,1000,1164,1440]){
  const computed=styles(nodes,css,width);
  for(const node of blocked){const small=node.children.find(n=>n.tag==='small');assert(small);
   for(const target of [node,small]){assert.equal(computed.get(target)['white-space'],'normal',`${width}/${target.tag}/${node.text}`);assert.equal(computed.get(target)['overflow-wrap'],'anywhere');}
   assert.equal(computed.get(node).display,'inline');assert.equal(computed.get(node)['max-width'],'100%');
  }
 }
});

test('frozen CSS negative control reproduces teaching nowrap while timeline already wraps',async()=>{
 const nodes=tree((await current()).render(person.person_id).content),computed=styles(nodes,baselineCss());
 const teaching=unavailable(nodes).filter(n=>ancestor(n,'info-panel')),timeline=unavailable(nodes).filter(n=>ancestor(n,'timeline'));
 assert.equal(teaching.length,2);assert.equal(timeline.length,1);
 for(const node of teaching){assert.equal(computed.get(node)['white-space'],'nowrap');assert.equal(computed.get(node.children.find(n=>n.tag==='small'))['white-space'],'nowrap');}
 assert.equal(computed.get(timeline[0])['white-space'],'normal');
});

test('unaffected source links keep their original cascade and remain clickable',async()=>{
 const rendered=(await current()).render(person.person_id),nodes=tree(rendered.main+rendered.content);
 const before=styles(nodes,baselineCss()),after=styles(nodes,css),links=nodes.filter(n=>n.tag==='a'&&n.classes.includes('source-link'));
 assert(links.length>0);
 for(const node of links){assert.deepEqual(after.get(node),before.get(node));assert(node.attrs.href);}
 assert(hrefs(rendered.main+rendered.content).includes(esc(person.official_url)));
});

test('disabled evidence URLs are never anchors and all original raw URL text stays visible',async()=>{
 const html=(await current()).render(person.person_id),nodes=tree(html.content),links=hrefs(html.main+html.content),blocked=unavailable(nodes);
 for(const row of person.teaching){assert(!links.includes(esc(row.source_url)));assert(blocked.some(n=>n.text.includes(row.source_url)));assert.equal(row.source_navigation_enabled,false);}
 assert.equal(blocked.filter(n=>n.text.includes(person.teaching[0].source_url)).length,2);
 assert.equal(blocked.filter(n=>n.text.includes(person.teaching[1].source_url)).length,3);
 for(const node of blocked){assert(!node.attrs.hidden);assert(!node.attrs.style);assert(!node.attrs['aria-hidden']);}
});

test('teaching role labels and historical caveats remain exact',async()=>{
 const section=teachingSection((await current()).render(person.person_id));
 assert.equal((section.match(/<\/strong> · 主讲/g)||[]).length,2);assert(!section.includes('具体教学角色未披露'));
 assert(section.includes('未声称2026仍授课'));assert(section.includes('不是学期课程或长期任课'));assert(section.includes('不是本人求学学历'));
 for(const row of person.teaching)assert(section.includes(esc(row.note)));
});

test('all 1110 actual profile and lineage renders are byte-identical to frozen display-fix output',async()=>{
 const f=await current(),renders=db.people.flatMap(p=>['profile','lineage'].map(mode=>[p.person_id,mode,f.render(p.person_id,mode)]));
 assert.equal(renders.length,1110);assert.equal(sha(JSON.stringify(renders)),BASELINE_ROUTE_SHA256);
});

test('six asset references are synchronized to the new wrapping CSS generation',()=>{
 for(const [file,count]of [['site/app.js',3],['site/rosters.js',1],['site/index.html',2]]){
  const text=fs.readFileSync(path.join(root,file),'utf8');assert.equal(text.split('rotation003-20261024-w2').length-1,count);assert(!text.includes('rotation003-20261023-w1'));
 }
 const index=fs.readFileSync(path.join(root,'site/index.html'),'utf8');assert(index.includes('styles.css?v=rotation003-20261024-w2'));assert(index.includes('app.js?v=rotation003-20261024-w2'));
});

test('rendering stays read-only and does not turn pending or unknown degrees into profiles',async()=>{
 const before=JSON.stringify(db),f=await current();f.render(person.person_id);const pending=f.render('cqu-chenrenwei');
 assert.equal(pending.content,'');assert(pending.main.includes('资料待完善'));assert.equal(JSON.stringify(db),before);
 assert.equal(db.people.length,555);assert.equal(db.pending_people.length,84);assert.equal(person.education[0].degree,null);assert.equal(person.education[0].degree_awarded,null);assert.equal(person.mentors.length,0);
});

if(process.env.ACADEMIC_ATLAS_NEGATIVE_CONTROL_ROOT){
 test('immutable baseline actual app and CSS independently reproduce the two teaching nowrap cases',async()=>{
  const base=process.env.ACADEMIC_ATLAS_NEGATIVE_CONTROL_ROOT,input=JSON.parse(fs.readFileSync(path.join(base,'data/atlas.json')));input.rosters=JSON.parse(fs.readFileSync(path.join(base,'data/rosters.json')));
  const oldCss=fs.readFileSync(path.join(base,'site/styles.css'),'utf8');assert.equal(sha(oldCss),BASELINE_CSS_SHA256);
  const f=await fixture(input,base),html=f.render('cqu-chenke'),nodes=tree(html.content),computed=styles(nodes,oldCss),blocked=unavailable(nodes);
  assert.equal(blocked.length,5);assert.equal(blocked.filter(n=>ancestor(n,'info-panel')&&computed.get(n)['white-space']==='nowrap').length,2);
  assert.deepEqual([...html.content.matchAll(/<span class="[^"]*source-unavailable">[\s\S]*?<\/span>/g)].map(m=>m[0]),BASELINE_SPANS);
 });
}
