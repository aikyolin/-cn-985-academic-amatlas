import {test} from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {matches, stages, mentorOfficialUrl, mentorProfileRoute} from '../site/model.js';
const whuMapping=JSON.parse(fs.readFileSync(new URL('./fixtures/independent-whu9-source-mapping.json',import.meta.url)));
const xjtuMapping=JSON.parse(fs.readFileSync(new URL('./fixtures/independent-xjtu12-source-mapping.json',import.meta.url)));
const rucMapping=JSON.parse(fs.readFileSync(new URL('./fixtures/independent-ruc8-source-mapping.json',import.meta.url)));
const ecnuMapping=JSON.parse(fs.readFileSync(new URL('./fixtures/independent-ecnu12-source-mapping.json',import.meta.url)));
const buaaMapping=JSON.parse(fs.readFileSync(new URL('./fixtures/independent-buaa12-source-mapping.json',import.meta.url)));
const tongjiMapping=JSON.parse(fs.readFileSync(new URL('./fixtures/independent-tongji12-source-mapping.json',import.meta.url)));
const db=JSON.parse(fs.readFileSync(new URL('../site/atlas.json',import.meta.url)));
const roster=JSON.parse(fs.readFileSync(new URL('../site/rosters.json',import.meta.url)));
const mapping=JSON.parse(fs.readFileSync(new URL('./fixtures/independent-hust12-source-mapping.json',import.meta.url)));
test('actual HUST cohort exactly preserves independently reviewed fields, identities and scope',()=>{
 assert.equal(db.people.length,749+mapping.people.length+whuMapping.people.length+xjtuMapping.people.length+rucMapping.people.length+ecnuMapping.people.length+buaaMapping.people.length+tongjiMapping.people.length);assert.equal(db.build_id,roster.build_id);
 for(const expected of mapping.people){
  const actual=db.people.find(p=>p.person_id===expected.person_id);assert.deepEqual(actual,expected);
  assert.equal(typeof actual.department,'string');assert(actual.department.length>0);
  assert(matches(actual,{q:actual.name},db.org_units));assert(matches(actual,{school:'hust',org:actual.department_id},db.org_units));
  assert(!matches(actual,{school:'seu'},db.org_units));assert.equal(actual.quick_link_eligible,false);assert.equal(actual.include_in_current_faculty_count,false);
  for(const mentor of actual.mentors){assert.equal(mentorOfficialUrl(mentor),'');assert.equal(mentorProfileRoute(mentor,db.people),'');}
  for(const stage of ['bachelor','master','doctor']) for(const event of stages(actual,stage)){assert.equal(event.event_kind,'degree');assert.equal(event.degree_awarded,true);}
 }
});
let serial=0;
async function render(hash){
 const nodes=new Map(),node=k=>{if(!nodes.has(k))nodes.set(k,{innerHTML:'',textContent:'',value:'',style:{},events:{},dataset:{height:'320'},clientWidth:960,addEventListener(t,f){this.events[t]=f},click(){this.onclick?.()}});return nodes.get(k)};
 globalThis.document={querySelector:node,querySelectorAll:()=>[],getElementById:id=>node('#'+id)};
 globalThis.location={hash};globalThis.window={scrollTo(){},addEventListener(){}};
 globalThis.fetch=async p=>({ok:true,json:async()=>structuredClone(String(p).startsWith('atlas.json')?db:roster)});
 await import('../site/app.js?current-hust-release='+serial++);
 assert(!node('#main').innerHTML.includes('资料暂未加载'));return node;
}
for(const expected of mapping.people)test('actual HUST profile and lineage preserve '+expected.name,async()=>{
 const nodes=await render('#/person/'+expected.person_id);const html=['#main','#profile-content'].map(k=>nodes(k).innerHTML).join('\n');
 assert(html.includes(expected.name));assert(html.includes('华中科技大学'));
 const lineage=await render('#/person/'+expected.person_id+'/lineage');
 const relationHtml=['#main','#profile-content','#mind-stage'].map(k=>lineage(k).innerHTML).join('\n');
 for(const mentor of expected.mentors){assert(relationHtml.includes(mentor.name));assert(relationHtml.includes(mentor.type_label||mentor.type));}
 if(expected.mentors.length===0)assert(relationHtml.includes('0条已收录关系'));
});






test('each source-supported teaching name, role and level note stays on its exact rendered row',async()=>{
 let checked=0;
 const esc=v=>String(v).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
 for(const p of mapping.people){if(!p.teaching?.length)continue;const n=await render('#/person/'+p.person_id),h=n('#main').innerHTML+n('#profile-content').innerHTML,section=h.split('<h2>公开教学事实</h2>')[1]?.split('</section>')[0]||'';
  for(const t of p.teaching){const name=t.name||t.course||(Array.isArray(t.courses)?t.courses.join('、'):null);assert(name,p.person_id);const row=(section.match(/<li>[\s\S]*?<\/li>/g)||[]).find(r=>r.includes('<strong>'+esc(name)+'</strong>'));assert(row,p.person_id+' '+name);if(t.role){assert(row.includes(' · '+esc(t.role)));assert(!row.includes('具体教学角色未披露'));}if(t.note)assert(row.includes(esc(t.note)));checked++;}
 }
 assert.equal(checked,mapping.people.reduce((n,p)=>n+(p.teaching||[]).length,0));assert(checked>0);
});
test('only two reviewed stronger degree claims are promoted without inventing award dates',async()=>{
 for(const [id,eventId] of [['hust-liwei-education','hust-liwei-education-education-3'],['hust-dengshiming','hust-dengshiming-education-1']]){
  const p=db.people.find(p=>p.person_id===id),e=p.education.find(e=>e.event_id===eventId);assert.equal(e.degree_awarded,true);assert.equal(e.event_kind,'degree');assert.equal(e.source_degree_awarded,null);assert.equal(e.degree_awarded_year,null);assert.equal(e.degree_awarded_date,null);
  const n=await render('#/person/'+id),h=n('#main').innerHTML+n('#profile-content').innerHTML;assert(h.includes(id==='hust-liwei-education'?'教育学博士':'双学士'));assert(!h.includes('官网专门学位栏'));
 }
 const deng=db.people.find(p=>p.person_id==='hust-dengshiming');assert.equal(deng.education.find(e=>e.event_id==='hust-dengshiming-education-2').degree_awarded,null);assert.equal(deng.education.filter(e=>e.degree==='双学士').length,1);
});
test('ambiguous education labels and enrollment are not silently promoted',()=>{
 const ids=['hust-baoyukun','hust-baiyun','hust-xieruixiang'];for(const id of ids){const p=db.people.find(p=>p.person_id===id);for(const e of p.education)if(e.degree_awarded!==false)assert.equal(e.degree_awarded,null,id+' '+e.event_id);}
 const li=db.people.find(p=>p.person_id==='hust-liwei-education');assert.equal(li.education.find(e=>e.event_id==='hust-liwei-education-education-1').degree_awarded,null);assert.equal(li.education.find(e=>e.event_id==='hust-liwei-education-education-2').degree_awarded,null);
});
test('doctoral disclosure guidance does not authenticate the degree or add separate merged-stage degrees',async()=>{
 const p=db.people.find(p=>p.person_id==='hust-baiyun');assert.equal(p.mentors.length,1);assert.equal(p.mentors[0].name,'李福荔');assert.equal(p.education.find(e=>e.event_id==='hust-baiyun-xjtu-graduate').degree_awarded,null);const n=await render('#/person/'+p.person_id+'/lineage'),h=n('#main').innerHTML+n('#profile-content').innerHTML+n('#mind-stage').innerHTML;assert(h.includes('李福荔'));assert(h.includes('博士'));
});
test('translator and textbook editor roles do not become sole authorship',async()=>{
 const li=db.people.find(p=>p.person_id==='hust-liwei-education'),long=db.people.find(p=>p.person_id==='hust-longlirong');assert.equal(li.publications.find(p=>p.title==='有效教师素质手册').type,'translated_book');assert(long.publications.every(p=>p.type==='edited_textbook'));
 for(const p of [li,long]){const n=await render('#/person/'+p.person_id),h=n('#main').innerHTML+n('#profile-content').innerHTML;assert(h.includes(p===li?'译':'主编'));}
});
test('visiting collaborators are not turned into mentor edges or degrees',async()=>{
 const p=db.people.find(p=>p.person_id==='hust-dengshiming');assert.equal(p.mentors.length,0);assert.equal(p.education.filter(e=>e.event_kind==='visiting_scholar'&&e.degree_awarded===false).length,4);const n=await render('#/person/'+p.person_id),h=n('#main').innerHTML+n('#profile-content').innerHTML;assert(h.includes('Yinyu Ye'));assert(h.includes('Candace A. Yano'));const l=await render('#/person/'+p.person_id+'/lineage');assert((l('#main').innerHTML+l('#profile-content').innerHTML+l('#mind-stage').innerHTML).includes('0条已收录关系'));
});
test('integrated master-doctor study does not create an unsupported separate master award',()=>{
 const p=db.people.find(p=>p.person_id==='hust-zhangyanglei');assert.equal(p.education.length,3);assert.equal(stages(p,'master').length,0);assert.equal(stages(p,'doctor').length,1);assert.equal(p.education.find(e=>e.event_id==='hust-zhangyanglei-training-1').degree_awarded,false);
});
test('official bachelor and master thesis advisors remain specific without doctoral promotion',async()=>{
 const p=db.people.find(p=>p.person_id==='hust-xieruixiang');assert.deepEqual(p.mentors.map(m=>m.name),['朱旭峰','陈永杰']);assert.equal(p.committee_members.length,4);assert.equal(p.education.length,4);assert.equal(p.additional_education_programs.length,3);assert.equal(p.publications.length,2);
 for(const m of p.mentors){assert.equal(m.formal_thesis_advisor_verified,true);assert.equal(m.formal_doctoral_dissertation_advisor_verified,false);assert.equal(m.original_thesis_document_verified,false);assert(!Object.hasOwn(m,'formal_dissertation_advisor_verified'));assert(m.type.includes('毕业论文导师'));}
 const n=await render('#/person/'+p.person_id+'/lineage'),h=n('#main').innerHTML+n('#profile-content').innerHTML+n('#mind-stage').innerHTML;assert(h.includes('硕士毕业论文导师'));assert(h.includes('学士毕业论文导师'));assert(h.includes('朱旭峰'));assert(h.includes('陈永杰'));
 const profile=await render('#/person/'+p.person_id),ph=profile('#main').innerHTML+profile('#profile-content').innerHTML;for(const minor of ['Disaster Resilience and Risk Management','Future Professoriate','博雅教育计划'])assert(ph.includes(minor));
});
test('reversed visiting dates and reported reprint labels are retained without fabricated fulltext verification',async()=>{
 const p=db.people.find(p=>p.person_id==='hust-chenxianhong');assert.equal(p.mentors.length,0);assert.equal(p.publications.length,2);const n=await render('#/person/'+p.person_id),h=n('#main').innerHTML+n('#profile-content').innerHTML;for(const phrase of ['2006.04–2005.05','CSSCI','新华文摘','2017年06期全文转载','不代表本次阅读全文'])assert(h.includes(phrase),phrase);
});
test('conflicting appointment end months and editor roles are not resolved by invention',async()=>{
 const p=db.people.find(p=>p.person_id==='hust-kelan');assert.equal(p.appointments[0].end,null);const n=await render('#/person/'+p.person_id),h=n('#main').innerHTML+n('#profile-content').innerHTML;for(const phrase of ['2013年4月','2013年3月','第一主编','不是独著','高全喜'])assert(h.includes(phrase),phrase);
});
test('university joining date is not treated as professor promotion date',async()=>{
 const p=db.people.find(p=>p.person_id==='hust-liuchengbin');const professorship=p.appointments.find(a=>String(a.title||a.role||'').includes('教授')&&a.start===null);assert(professorship);const n=await render('#/person/'+p.person_id),h=n('#main').innerHTML+n('#profile-content').innerHTML;assert(h.includes('2011入校不是教授晋升日期'));assert(h.includes('独著'));
});
