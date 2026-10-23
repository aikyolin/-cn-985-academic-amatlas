import fs from 'node:fs';
import assert from 'node:assert/strict';
import {test} from 'node:test';
import {mentorProfileRoute,escapeHtml,safeUrl} from '../site/model.js';

const db=JSON.parse(fs.readFileSync(new URL('../site/atlas.json',import.meta.url)));
const app=fs.readFileSync(new URL('../site/app.js',import.meta.url),'utf8');
const person=name=>db.people.find(p=>p.name===name);
const relation=(name,mentor)=>person(name).mentors.find(m=>m.name===mentor);
const lineageSource=app.match(/function lineage\(p\)\{[\s\S]*?\n(?=function makeMind)/)?.[0];
assert(lineageSource,'Test must exercise the actual mentor-card renderer');

function renderCards(p,people=db.people){
  const elements=new Map();
  const $=key=>{
    if(!elements.has(key))elements.set(key,{innerHTML:'',clientWidth:960,dataset:{height:'320'},style:{},addEventListener(){},click(){this.onclick?.()}});
    return elements.get(key);
  };
  const link=(url,label,cls='')=>safeUrl(url)?`<a class="${cls}" href="${escapeHtml(safeUrl(url))}" target="_blank" rel="noopener noreferrer">${escapeHtml(label)} ↗</a>`:`<span>${escapeHtml(label)}</span>`;
  const src=(url,label)=>url?link(url,label,'source-link'):'';
  const render=new Function('db','$','esc','statusLabel','src','mentorProfileRoute','safeUrl','link','makeMind',`let zoom=1;return (${lineageSource});`)(
    {people},$,escapeHtml,value=>value,src,mentorProfileRoute,safeUrl,link,()=>'<svg></svg>'
  );
  render(p);
  return $('#profile-content').innerHTML;
}

for(const [mentee,mentor,id] of [
  ['曲歌扬','宋清海','hit-songqinghai'],
  ['黄灿','宋清海','hit-songqinghai'],
  ['李志强','韩帅','hit-hanshuai']
])test(`${mentee} → ${mentor}: active matched mentor opens the stored profile`,()=>{
  const m=relation(mentee,mentor);
  assert.equal(m.employment_status,'active_officially_listed');
  assert.notEqual(m.quick_link_eligible,false);
  assert.equal(m.person_id,id);
  assert.equal(mentorProfileRoute(m,db.people),`#/person/${id}`);
  const html=renderCards(person(mentee));
  assert(html.includes(`href="#/person/${id}">查看本库个人档案</a>`));
  assert(html.includes('本库资料档案，非在职快捷链接'));
});

for(const [mentee,mentor,id] of [
  ['庄迪','张腊梅','hit-zhanglm'],
  ['李鹏','胡悦','hit-huyue'],
  ['彭宇','彭喜元','hit-pengxiyuan'],
  ['孟升卫','付平','hit-fuping']
])test(`${mentee} → ${mentor}: official listing with false eligibility remains biography-only`,()=>{
  const rows=person(mentee).mentors.filter(m=>m.name===mentor);
  assert.equal(rows.length,mentee==='彭宇'?2:1);
  for(const m of rows){
    assert.equal(m.person_id,id);
    assert(db.people.some(p=>p.person_id===id));
    assert.equal(m.employment_status,'official_page_currently_listed');
    assert.equal(m.quick_link_eligible,false);
    assert.equal(mentorProfileRoute(m,db.people),'');
  }
  const html=renderCards(person(mentee));
  assert(!html.includes(`href="#/person/${id}"`));
  assert(html.includes(mentor));
  assert(html.includes('关系证据'));
});

test('unknown, emeritus, retired, inactive and deceased cannot navigate even with a matching ID',()=>{
  const m=relation('曲歌扬','宋清海');
  for(const status of [null,undefined,'unknown','unknown_conflicting','emeritus_officially_listed','retired','inactive','deceased','active_institutional_report','official_page_currently_listed_retirement_not_disclosed']){
    const row={...m,employment_status:status,quick_link_eligible:true};
    assert.equal(mentorProfileRoute(row,db.people),'',String(status));
    const html=renderCards({mentors:[row]});
    assert(!html.includes('查看本库个人档案'));
    assert(!html.includes('查看导师个人主页'));
    assert(html.includes('关系证据'));
  }
});

test('null, blank, unknown and non-string IDs never join similarly empty entities',()=>{
  for(const id of [null,undefined,'','   ','unknown','null','undefined',0,{},[]]){
    const row={employment_status:'active_officially_listed',person_id:id};
    assert.equal(mentorProfileRoute(row,[{person_id:id}]),'');
    assert(!renderCards({mentors:[row]},[{person_id:id}]).includes('查看本库个人档案'));
  }
  assert.equal(mentorProfileRoute(null,db.people),'');
  assert.equal(mentorProfileRoute(undefined,db.people),'');
});

test('nonexistent or pending-only entity IDs never create a detailed-profile route',()=>{
  for(const id of ['hit-unrecorded-person',db.pending_people[0].person_id]){
    const m={employment_status:'active_officially_listed',person_id:id,quick_link_eligible:true};
    assert.equal(mentorProfileRoute(m,db.people),'');
    assert(!renderCards({mentors:[m]}).includes('查看本库个人档案'));
  }
  assert.equal(mentorProfileRoute(relation('曲歌扬','宋清海'),null),'');
});

test('explicit false vetoes internal navigation without changing the existing external-link rule',()=>{
  const m={...relation('曲歌扬','宋清海'),quick_link_eligible:false};
  assert.equal(mentorProfileRoute(m,db.people),'');
  const html=renderCards({mentors:[m]});
  assert(!html.includes('查看本库个人档案'));
  assert(html.includes('查看导师个人主页'));
  assert(html.includes(`href="${escapeHtml(safeUrl(m.official_url))}"`));
});

test('missing eligibility remains compatible with already reviewed active legacy mentors',()=>{
  const m={...relation('曲歌扬','宋清海')};
  delete m.quick_link_eligible;
  assert.equal(mentorProfileRoute(m,db.people),'#/person/hit-songqinghai');
  assert.equal(mentorProfileRoute({...m,quick_link_eligible:true},db.people),'#/person/hit-songqinghai');
});

test('matched profile IDs are encoded rather than interpolated as raw routes or attributes',()=>{
  const id='test/person ?#"<tag>',people=[{person_id:id}];
  const m={employment_status:'active_officially_listed',person_id:id};
  const route='#/person/'+encodeURIComponent(id);
  assert.equal(mentorProfileRoute(m,people),route);
  const html=renderCards({mentors:[m]},people);
  assert(html.includes(`href="${route}"`));
  assert(!html.includes('<tag>'));
});

test('helper and card rendering leave all stored employment and eligibility evidence unchanged',()=>{
  const before=JSON.stringify(db);
  for(const p of db.people){
    for(const m of p.mentors)mentorProfileRoute(m,db.people);
    if(p.mentors.length)renderCards(p);
  }
  assert.equal(JSON.stringify(db),before);
});

test('malformed UTF-16 identifiers fail closed without breaking the mentor card',()=>{
  for(const id of ['\ud800','\udfff','hit-\ud800-profile']){
    const people=[{person_id:id}],m={employment_status:'active_officially_listed',person_id:id};
    assert.equal(mentorProfileRoute(m,people),'');
    assert(!renderCards({mentors:[m]},people).includes('查看本库个人档案'));
  }
});

test('external mentor navigation still requires active status and a safe official URL',()=>{
  assert(app.includes("a.employment_status==='active_officially_listed'&&safeUrl(a.official_url)"));
  const m={...relation('曲歌扬','宋清海'),official_url:'javascript:alert(1)'};
  const html=renderCards({mentors:[m]});
  assert(html.includes('查看本库个人档案'));
  assert(!html.includes('查看导师个人主页'));
  assert(html.includes('导师主页待核实'));
});

test('Wu Ligang retains active evidence but renders the authentication limitation instead of a homepage link',()=>{
  const x=person('林欣魄'),m=x.mentors[0],html=renderCards(x);
  assert.equal(m.employment_status,'active_officially_listed');
  assert.equal(m.official_url,null);
  assert.equal(m.quick_link_eligible,false);
  assert(html.includes(escapeHtml(m.profile_navigation_unavailable_reason)));
  assert(html.includes('简介与任职依据'));
  assert(!html.includes('查看导师个人主页'));
  assert(!html.includes('查看本库个人档案'));
  assert(!html.includes('导师主页待核实'));
});

test('explicit unavailable-navigation message is escaped, never rendered as raw HTML',()=>{
  const m={...relation('林欣魄','吴立刚'),profile_navigation_unavailable_reason:'认证 <script>unsafe()</script>'};
  const html=renderCards({mentors:[m]});
  assert(html.includes('认证 &lt;script&gt;unsafe()&lt;/script&gt;'));
  assert(!html.includes('<script>unsafe()</script>'));
});
