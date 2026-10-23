import {test} from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {rosterProfileLinks,rosterIdentityMatched,rosterStatusLabel} from '../site/rosters.js';
import {escapeHtml,officialProfileUrl} from '../site/model.js';

const read=path=>JSON.parse(fs.readFileSync(new URL(path,import.meta.url)));
const LABEL='官方名录关联的本人职业网站',AVAILABILITY=LABEL+'（非学校域名官网）';
function fixture(){const d=read('./fixtures/multischool.json'),p=d.people[1],e=d.rosters.entries.find(e=>e.school_id===p.school_id);Object.assign(p,{official_url:'https://synthetic-scholar.github.io/',official_url_kind:'self_authored_professional_profile_linked_by_official',official_profile_link_label:LABEL,official_profile_availability_label:AVAILABILITY});Object.assign(e,{name:p.name,organization_id:p.department_id,official_profile_url:p.official_url,official_url_kind:p.official_url_kind,official_profile_link_label:LABEL,official_profile_availability_label:AVAILABILITY,profile_identity_verified:false,verified_person_id:null});return {d,p,e}}
let serial=0;
async function app(d,id=d.people[1].person_id){const nodes=new Map(),node=k=>{if(!nodes.has(k))nodes.set(k,{innerHTML:'',textContent:'',value:'',style:{},events:{},dataset:{height:'320'},clientWidth:960,addEventListener(t,f){this.events[t]=f},click(){this.onclick?.()}});return nodes.get(k)};globalThis.document={querySelector:node,querySelectorAll:()=>[],getElementById:id=>node('#'+id)};globalThis.location={hash:'#/person/'+id};globalThis.window={scrollTo(){},addEventListener(){}};globalThis.fetch=async p=>({ok:true,json:async()=>structuredClone(String(p).startsWith('atlas.json')?d:d.rosters)});await import('../site/app.js?explicit-profile-source-label='+serial++);assert(!node('#main').innerHTML.includes('资料暂未加载'));return node}

test('an explicitly labelled official-directory-linked personal website is not called a university homepage',async()=>{
 const {d,p}=fixture(),before=JSON.stringify(d),node=await app(d),html=node('#main').innerHTML;assert(html.includes('href="'+p.official_url+'"'));assert(html.includes(LABEL));assert(html.includes(AVAILABILITY));assert(!html.includes('学校官方主页'));assert.equal(JSON.stringify(d),before);assert.equal(p.official_url_kind,'self_authored_professional_profile_linked_by_official');
});

test('an explicit roster link label preserves candidate identity rather than treating the personal website as university evidence',()=>{
 const {d,p,e}=fixture(),before=JSON.stringify(d),html=rosterProfileLinks(d,e);assert(html.includes('href="'+p.official_url+'"'));assert(html.includes(LABEL+'（身份待核对）'));assert(html.includes(AVAILABILITY));assert(!html.includes('独立核验的官方个人主页'));assert.equal(rosterIdentityMatched(d,e),false);assert.equal(rosterStatusLabel(d,e),'档案待建，身份待核对');assert.equal(JSON.stringify(d),before);
});

test('verified roster identity uses the matched persons explicit source label without changing the navigation URL',()=>{
 const {d,p,e}=fixture();e.verified_person_id=p.person_id;e.profile_identity_verified=true;delete e.official_profile_link_label;delete e.official_profile_availability_label;const html=rosterProfileLinks(d,e);assert(html.includes(LABEL+'（任职状态另核）'));assert(html.includes(AVAILABILITY));assert(!html.includes('独立核验的官方个人主页'));assert(html.includes('href="'+p.official_url+'"'));
});

test('matched sparse roster identities retain source labels and completeness limits without a detailed-person association',()=>{
 const {d,p,e}=fixture();d.pending_people=[{person_id:'pending-explicit-label-test',roster_entry_id:e.id,school_id:e.school_id,profile_status:'profile_details_pending'}];const html=rosterProfileLinks(d,e);assert(html.includes(LABEL+'（身份已匹配，资料完整性另核）'));assert.equal(e.verified_person_id,null);assert(!html.includes('独立核验的官方个人主页'));assert.equal(p.official_url,e.official_profile_url);
});

test('legacy records retain their prior labels and no label is inferred solely from an external hostname',async()=>{
 const {d,p,e}=fixture();for(const x of [p,e])for(const k of ['official_url_kind','official_profile_link_label','official_profile_availability_label'])delete x[k];const html=(await app(d))('#main').innerHTML;assert(html.includes('学校官方主页'));assert(!html.includes(LABEL));assert(rosterProfileLinks(d,e).includes('原名录提供的主页链接（身份待核对）'));e.verified_person_id=p.person_id;assert(rosterProfileLinks(d,e).includes('独立核验的官方个人主页（任职状态另核）'));
});

test('labels never bypass inaccessible-profile, unsafe-protocol or CMS editor navigation gates',async()=>{
 for(const change of [{official_profile_navigation_eligible:false},{official_profile_availability:'unavailable'},{official_url:'javascript:unsafe()'},{official_url:'https://example.test/_cms/editor'}]){const {d,p,e}=fixture();Object.assign(p,change);if(change.official_url)e.official_profile_url=change.official_url;else Object.assign(e,change);assert.equal(officialProfileUrl(p),'');const html=(await app(d))('#main').innerHTML;assert(!html.includes('href="'+p.official_url+'"'));assert(!rosterProfileLinks(d,e).includes('href="'+e.official_profile_url+'"'))}
});

test('CCF institutional biographies keep their own title and no new generic claim says they are university reports',async()=>{
 const {d,p,e}=fixture(),title='CCF 学会官方职业简介（非学校个人主页）',note='学校门户访问受限；可读职业资料来源另列',report={url:'https://www.ccf.org.cn/test-reviewed-profile',title};for(const x of [p,e])Object.assign(x,{official_profile_availability:'unavailable',official_profile_navigation_eligible:false,official_profile_availability_label:note,alternative_professional_sources:[report]});p.sources.push({id:'self-authored-test',url:'https://synthetic-scholar.github.io/about',evidence_status:'self_authored_professional_website',evidence_status_label:'本人职业网站正文已读（非学校域名官网）'});const node=await app(d),html=node('#main').innerHTML,roster=rosterProfileLinks(d,e);assert(html.includes(title));assert(roster.includes(title));assert(html.includes(note));assert(roster.includes(note));assert(roster.includes('职业资料来源按下列标签分别列示'));assert(!roster.includes('职业身份由官方名录与校方报道核验'));assert(!html.includes('学校官方主页'));assert(node('#profile-content').innerHTML.includes('本人职业网站正文已读（非学校域名官网）'));assert.equal(p.alternative_professional_sources.length,1);
});

test('school-news alternative titles remain exact instead of being relabelled as personal homepages',async()=>{
 const {d,p,e}=fixture(),s={url:'https://news.example.test/career',title:'学校官方职业报道（非个人主页）'};for(const x of [p,e])Object.assign(x,{official_profile_availability:'unavailable',official_profile_navigation_eligible:false,official_profile_availability_label:'学校门户访问受限',alternative_professional_sources:[s]});assert((await app(d))('#main').innerHTML.includes(s.title));assert(rosterProfileLinks(d,e).includes(s.title));
});

test('source labels, availability labels and alternative titles remain escaped and URLs protocol-safe',async()=>{
 const {d,p,e}=fixture(),payload='<script>unsafe()</script>';for(const x of [p,e])Object.assign(x,{official_profile_link_label:payload,official_profile_availability_label:payload,alternative_professional_sources:[{url:'javascript:bad()',title:payload}]});const html=(await app(d))('#main').innerHTML,roster=rosterProfileLinks(d,e);for(const text of [html,roster]){assert(text.includes(escapeHtml(payload)));assert(!text.includes(payload));assert(!text.includes('href="javascript:'))}
});
