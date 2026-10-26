// Opt-in immutable cohort content assertions only. Never use for freshness,
// mutation, interactions, or cold-load failure tests. No route snapshot cache:
// every call after startup invokes the actual app's registered hashchange handler.
import {createHash} from 'node:crypto';
import {createAtlasFetch} from './atlas-test-io.js';
let active=null,serial=0;
const digest=value=>createHash('sha256').update(JSON.stringify(value)).digest('hex');
const defaults=()=>({innerHTML:'',textContent:'',value:'',style:{},events:{},dataset:{height:'320'},clientWidth:960,addEventListener(type,fn){this.events[type]=fn},click(){this.onclick?.()}});
export function createImmutableCohortRenderer({db,roster,appUrl=new URL('../site/app.js',import.meta.url),fixtureId,fetchFactory=createAtlasFetch,listenerFault=null}){
 if(!fixtureId)throw Error('explicit immutable fixture identity required');
 const owner=++serial,identity=digest([db,roster]),nodes=new Map(),listeners=new Map();
 let touched=new Set(),initialized=false,failed=null,main=null;
 const stats={fixtureId,imports:0,handlerRegistrations:0,handlerCalls:0,renders:0,fetches:[],routes:[]};
 const node=key=>{touched.add(key);if(!nodes.has(key))nodes.set(key,defaults());return nodes.get(key)};
 const location={href:'https://atlas.test/site/index.html',hash:''};
 const document={querySelector:node,querySelectorAll:()=>[],getElementById:id=>node('#'+id)};
 const window={scrollTo(){},addEventListener(type,fn){if(type==='hashchange'){stats.handlerRegistrations+=listenerFault==='duplicate'?2:1;if(listenerFault!=='missing')listeners.set(type,fn);}}};
 const rawFetch=fetchFactory(db,roster),fetch=async(...args)=>{stats.fetches.push(String(args[0]));return rawFetch(...args)};
 const empty=Object.freeze({innerHTML:'',textContent:''});
 async function render(hash,inputs={db,roster}){
  if(active!==null)throw Error('concurrent global renderer use rejected');
  if(inputs.db!==db||inputs.roster!==roster||digest([db,roster])!==identity)throw Error('immutable fixture changed');
  if(failed)throw Error('renderer failed: '+failed.message);
  active=owner;
  try{
   touched=new Set();for(const value of nodes.values()){for(const key of Object.keys(value))delete value[key];Object.assign(value,defaults());}
   Object.assign(globalThis,{document,location,window,fetch});location.hash=hash;
   const currentMain=node('#main');if(main&&main!==currentMain)throw Error('main identity changed');main=currentMain;
   if(!initialized){
    stats.imports++;const url=new URL(appUrl);url.searchParams.set('immutable-cohort-renderer',String(owner));await import(url.href);
    if(main.innerHTML.includes('资料暂未加载'))throw Error('actual app load failure: '+main.innerHTML);
    if(stats.handlerRegistrations!==1||typeof listeners.get('hashchange')!=='function')throw Error('missing or duplicate real hashchange handler');initialized=true;
   }else{stats.handlerCalls++;await listeners.get('hashchange')();}
   if(main.innerHTML.includes('资料暂未加载'))throw Error('actual app load failure: '+main.innerHTML);
   stats.renders++;stats.routes.push(hash);
   const snapshot=Object.freeze(Object.fromEntries([...touched].sort().map(key=>[key,Object.freeze({innerHTML:nodes.get(key).innerHTML,textContent:nodes.get(key).textContent})])));
   // Return strings, not mutable nodes/events. Prior snapshots cannot be altered
   // by subsequent navigation or by tests that only inspect content.
   return Object.freeze(Object.assign(key=>snapshot[key]||empty,{snapshot}));
  }catch(error){failed=error;throw error;}finally{active=null;}
 }
 if(process.env.ATLAS_RENDER_DIAGNOSTICS==='1')process.once('exit',()=>{
  process.stderr.write('[immutable-cohort] '+JSON.stringify({fixtureId,identity,imports:stats.imports,handlerRegistrations:stats.handlerRegistrations,handlerCalls:stats.handlerCalls,renders:stats.renders,uniqueRoutes:new Set(stats.routes).size,fetchCount:stats.fetches.length,chunkFetches:stats.fetches.filter(url=>String(url).includes('/people/')).length,resource:process.resourceUsage(),memory:process.memoryUsage()})+'\n');
 });
 return {render,stats,identity,mainIdentity:()=>main,nodeAudit:()=>({storedKeys:[...nodes.keys()].sort(),activeKeys:[...touched].sort(),inactiveBlank:[...nodes].filter(([key])=>!touched.has(key)).every(([,value])=>value.innerHTML===''&&value.textContent==='')})};
}
