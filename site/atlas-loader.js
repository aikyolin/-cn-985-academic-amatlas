// School-part transport is fully verified before any business data is returned.
export const LIMITS=Object.freeze({manifestBytes:16*1024*1024,chunkBytes:16*1024*1024,parts:1024,people:100000,depth:512,totalBytes:128*1024*1024});
const fail=message=>{throw new Error(`资料分片校验失败：${message}；请稍后刷新。`)};
const object=x=>x!==null&&typeof x==='object'&&!Array.isArray(x);
const exact=(x,keys)=>object(x)&&Object.keys(x).length===keys.length&&keys.every(k=>Object.hasOwn(x,k));
const safeSchool=x=>typeof x==='string'&&/^[a-z][a-z0-9-]{0,63}$/.test(x);
const positive=x=>Number.isSafeInteger(x)&&x>0;
// JSON.parse alone silently accepts duplicate members and overflowing numbers.
export function parseStrictJSON(text){
 let i=0;const ws=()=>{while(/[\x20\t\r\n]/.test(text[i]||'\0'))i++};
 function string(){const start=i++;while(i<text.length){const c=text[i++];if(c==='"'){try{const value=JSON.parse(text.slice(start,i));if(/[\uD800-\uDBFF](?![\uDC00-\uDFFF])|(?<![\uD800-\uDBFF])[\uDC00-\uDFFF]/u.test(value))fail('孤立Unicode代理项');return value}catch{fail('JSON字符串无效')}}if(c==='\\')i++;}fail('JSON字符串未闭合')}
 function value(depth){if(depth>LIMITS.depth)fail('JSON嵌套过深');ws();const c=text[i];
  if(c==='"')return string();
  if(c==='{'){i++;ws();const keys=new Set();if(text[i]==='}'){i++;return}while(true){ws();if(text[i]!=='"')fail('JSON对象键无效');const k=string();if(keys.has(k))fail('JSON重复键');keys.add(k);ws();if(text[i++]!==':')fail('JSON缺少冒号');value(depth+1);ws();const end=text[i++];if(end==='}')return;if(end!==',')fail('JSON对象无效')}}
  if(c==='['){i++;ws();if(text[i]===']'){i++;return}while(true){value(depth+1);ws();const end=text[i++];if(end===']')return;if(end!==',')fail('JSON数组无效')}}
  const m=/^(?:true|false|null|-?(?:0|[1-9]\d*)(?:\.\d+)?(?:[eE][+-]?\d+)?)/.exec(text.slice(i));if(!m)fail('JSON值无效');i+=m[0].length;if(!['true','false','null'].includes(m[0])&&!Number.isFinite(Number(m[0])))fail('JSON非有限数值');
 }
 value(0);ws();if(i!==text.length)fail('JSON尾随数据');try{return JSON.parse(text)}catch{fail('JSON无效')}
}
function finiteTree(x,depth=0){if(depth>LIMITS.depth)fail('JSON嵌套过深');if(typeof x==='string'&&/[\uD800-\uDBFF](?![\uDC00-\uDFFF])|(?<![\uD800-\uDBFF])[\uDC00-\uDFFF]/u.test(x))fail('孤立Unicode代理项');if(typeof x==='number'&&!Number.isFinite(x))fail('非有限数值');if(x&&typeof x==='object')for(const [k,v] of Object.entries(x)){finiteTree(k,depth+1);finiteTree(v,depth+1)}}
export function validateManifest(m){
 finiteTree(m);if(!exact(m,['format','atlas','people_order','parts'])||m.format!=='academic-atlas-school-parts-v1')fail('manifest格式不匹配');
 if(!object(m.atlas)||!Array.isArray(m.atlas.people)||m.atlas.people.length||!Array.isArray(m.atlas.institutions))fail('atlas占位或学校列表无效');
 const schools=new Set();for(const s of m.atlas.institutions){if(!object(s)||!safeSchool(s.id)||schools.has(s.id))fail('学校身份重复或无效');schools.add(s.id)}
 if(!Array.isArray(m.people_order)||m.people_order.length>LIMITS.people||m.people_order.some(id=>typeof id!=='string'||!id||Array.from(id).length>256)||new Set(m.people_order).size!==m.people_order.length)fail('人物顺序无效或重复');
 if(!Array.isArray(m.parts)||m.parts.length>LIMITS.parts)fail('分片列表过大或无效');const seen=new Set();let count=0;
 for(const p of m.parts){if(!exact(p,['school_id','path','sha256','bytes','count'])||!safeSchool(p.school_id)||!schools.has(p.school_id)||seen.has(p.school_id)||p.path!==`people/${p.school_id}.json`||typeof p.sha256!=='string'||!/^[a-f0-9]{64}$/.test(p.sha256)||!positive(p.bytes)||p.bytes>LIMITS.chunkBytes||!positive(p.count)||p.count>LIMITS.people)fail('分片声明无效');seen.add(p.school_id);count+=p.count}
 if(m.parts.reduce((n,p)=>n+p.bytes,0)>LIMITS.totalBytes)fail('总分片过大');if(count!==m.people_order.length)fail('声明人数不匹配');return m;
}
export function assembleAtlas(manifest,parsedParts){
 const m=validateManifest(manifest);if(!Array.isArray(parsedParts)||parsedParts.length!==m.parts.length)fail('缺少分片');const people=new Map();const perSchool=new Map();
 parsedParts.forEach((part,i)=>{finiteTree(part);const spec=m.parts[i];if(!exact(part,['school_id','people'])||part.school_id!==spec.school_id||!Array.isArray(part.people)||part.people.length!==spec.count)fail('分片形状或人数不匹配');const ids=[];for(const p of part.people){if(!object(p)||typeof p.person_id!=='string'||!p.person_id||Array.from(p.person_id).length>256||p.school_id!==spec.school_id||people.has(p.person_id))fail('跨校或重复人物');people.set(p.person_id,p);ids.push(p.person_id)}perSchool.set(spec.school_id,ids)});
 const restored=m.people_order.map(id=>{if(!people.has(id))fail('顺序中存在缺失人物');return people.get(id)});if(people.size!==restored.length)fail('多余人物');const order=[];const within=new Map();for(const p of restored){if(!within.has(p.school_id)){order.push(p.school_id);within.set(p.school_id,[])}within.get(p.school_id).push(p.person_id)}
 if(JSON.stringify(order)!==JSON.stringify(m.parts.map(p=>p.school_id)))fail('学校分片顺序错误');for(const [s,ids] of within)if(JSON.stringify(ids)!==JSON.stringify(perSchool.get(s)))fail('校内人物顺序错误');
 return {...m.atlas,people:restored};
}
function urlForManifest(input){let u;try{u=new URL(input,globalThis.location?.href)}catch{fail('manifest地址无效')}
 if(!['https:','http:'].includes(u.protocol)||u.username||u.password||u.hash)fail('manifest地址不安全');
 if(globalThis.location?.origin&&u.origin!==globalThis.location.origin)fail('manifest必须同源');return u;
}
async function readBytes(fetchImpl,url,cache,max,expected,onBytes){
 const response=await fetchImpl(url.href,{cache,redirect:'error'});if(!response?.ok)fail('数据请求失败');if(response.url){const final=new URL(response.url);if(final.origin!==url.origin||final.pathname!==url.pathname)fail('响应地址不匹配')}
 const length=response.headers?.get?.('content-length');if(length!==null&&length!==undefined&&(!/^\d+$/.test(length)||Number(length)>max))fail('响应过大或长度无效');
 const buffer=await response.arrayBuffer();if(buffer.byteLength>max)fail('响应过大');const bytes=new Uint8Array(buffer);onBytes?.(bytes.byteLength);
 if(expected){if(bytes.byteLength!==expected.bytes)fail('分片字节数不匹配');const digest=await globalThis.crypto.subtle.digest('SHA-256',bytes);const hash=Array.from(new Uint8Array(digest),n=>n.toString(16).padStart(2,'0')).join('');if(hash!==expected.sha256)fail('分片摘要不匹配（可能正在部署）')}
 let text;try{text=new TextDecoder('utf-8',{fatal:true,ignoreBOM:true}).decode(bytes)}catch{fail('UTF-8无效')}
 return parseStrictJSON(text);
}
export async function loadAtlas(fetchImpl=globalThis.fetch,manifestURL='atlas.json',options={concurrency:4}){
 if(!globalThis.crypto?.subtle)fail('需要HTTPS或localhost环境提供SHA-256校验');if(typeof fetchImpl!=='function')fail('fetch不可用');
 const concurrency=options.concurrency??4;if(!Number.isSafeInteger(concurrency)||concurrency<1||concurrency>16)fail('并发设置无效');const url=urlForManifest(manifestURL);
 let manifestBytes=0;const manifest=validateManifest(await readBytes(fetchImpl,url,'no-store',LIMITS.manifestBytes,undefined,n=>{manifestBytes=n}));if(manifestBytes+manifest.parts.reduce((n,p)=>n+p.bytes,0)>LIMITS.totalBytes)fail('总数据过大');const parsed=new Array(manifest.parts.length);let next=0,failed=false;
 async function worker(){while(!failed){const i=next++;if(i>=manifest.parts.length)return;const part=manifest.parts[i];const target=new URL(part.path,url);if(target.origin!==url.origin||target.pathname!==new URL('.',url).pathname+part.path)fail('分片路径不安全');target.searchParams.set('sha256',part.sha256);try{parsed[i]=await readBytes(fetchImpl,target,'default',LIMITS.chunkBytes,part)}catch(error){failed=true;throw error}}}
 await Promise.all(Array.from({length:Math.min(concurrency,manifest.parts.length)},worker));return assembleAtlas(manifest,parsed);
}
