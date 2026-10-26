import {createImmutableCohortRenderer} from './immutable-cohort-renderer.js';
import {readAtlasFile,createAtlasFetch} from './atlas-test-io.js';
import {test} from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {matches, stages, officialProfileUrl} from '../site/model.js';
const uestcMapping=JSON.parse(fs.readFileSync(new URL('./fixtures/independent-uestc10-source-mapping.json',import.meta.url)));
const hnuMapping=JSON.parse(fs.readFileSync(new URL('./fixtures/independent-hnu10-source-mapping.json',import.meta.url)));
const bnuMapping=JSON.parse(fs.readFileSync(new URL('./fixtures/independent-bnu12-source-mapping.json',import.meta.url)));
const tjuMapping=JSON.parse(fs.readFileSync(new URL('./fixtures/independent-tju12-source-mapping.json',import.meta.url)));
const nkuMapping=JSON.parse(fs.readFileSync(new URL('./fixtures/independent-nku12-source-mapping.json',import.meta.url)));
const dlutMapping=JSON.parse(fs.readFileSync(new URL('./fixtures/independent-dlut12-source-mapping.json',import.meta.url)));
const jluMapping=JSON.parse(fs.readFileSync(new URL('./fixtures/independent-jlu12-source-mapping.json',import.meta.url)));
const sduMapping=JSON.parse(fs.readFileSync(new URL('./fixtures/independent-sdu12-source-mapping.json',import.meta.url)));
const csuMapping=JSON.parse(fs.readFileSync(new URL('./fixtures/independent-csu12-source-mapping.json',import.meta.url)));
const hustMapping=JSON.parse(fs.readFileSync(new URL('./fixtures/independent-hust12-source-mapping.json',import.meta.url)));
const whuMapping=JSON.parse(fs.readFileSync(new URL('./fixtures/independent-whu9-source-mapping.json',import.meta.url)));
const xjtuMapping=JSON.parse(fs.readFileSync(new URL('./fixtures/independent-xjtu12-source-mapping.json',import.meta.url)));
const rucMapping=JSON.parse(fs.readFileSync(new URL('./fixtures/independent-ruc8-source-mapping.json',import.meta.url)));
const ecnuMapping=JSON.parse(fs.readFileSync(new URL('./fixtures/independent-ecnu12-source-mapping.json',import.meta.url)));
const buaaMapping=JSON.parse(fs.readFileSync(new URL('./fixtures/independent-buaa12-source-mapping.json',import.meta.url)));
const tongjiMapping=JSON.parse(fs.readFileSync(new URL('./fixtures/independent-tongji12-source-mapping.json',import.meta.url)));
const bitMapping=JSON.parse(fs.readFileSync(new URL('./fixtures/independent-bit12-source-mapping.json',import.meta.url)));
const nwpuMapping=JSON.parse(fs.readFileSync(new URL('./fixtures/independent-nwpu12-source-mapping.json',import.meta.url)));
const scutMapping=JSON.parse(fs.readFileSync(new URL('./fixtures/independent-scut11-source-mapping.json',import.meta.url)));
const ustcMapping=JSON.parse(fs.readFileSync(new URL('./fixtures/independent-ustc12-source-mapping.json',import.meta.url)));
const cauMapping=JSON.parse(fs.readFileSync(new URL('./fixtures/independent-cau12-source-mapping.json',import.meta.url)));
const fduMapping=JSON.parse(fs.readFileSync(new URL('./fixtures/independent-fdu12-source-mapping.json',import.meta.url)));
const mucMapping=JSON.parse(fs.readFileSync(new URL('./fixtures/independent-muc12-source-mapping.json',import.meta.url)));
const nwsuafMapping=JSON.parse(fs.readFileSync(new URL('./fixtures/independent-nwsuaf12-source-mapping.json',import.meta.url)));
const oucMapping=JSON.parse(fs.readFileSync(new URL('./fixtures/independent-ouc12-source-mapping.json',import.meta.url)));
const lzuMapping=JSON.parse(fs.readFileSync(new URL('./fixtures/independent-lzu11-source-mapping.json',import.meta.url)));
const sjtuMapping=JSON.parse(fs.readFileSync(new URL('./fixtures/independent-sjtu11-source-mapping.json',import.meta.url)));
const thuMapping=JSON.parse(fs.readFileSync(new URL('./fixtures/independent-thu11-source-mapping.json',import.meta.url)));
const pkuMapping=JSON.parse(fs.readFileSync(new URL('./fixtures/independent-pku11-source-mapping.json',import.meta.url)));
const zjuMapping=JSON.parse(fs.readFileSync(new URL('./fixtures/independent-zju7-source-mapping.json',import.meta.url)));
const db=readAtlasFile(new URL('../site/atlas.json',import.meta.url));
const roster=JSON.parse(fs.readFileSync(new URL('../site/rosters.json',import.meta.url)));
const laterMapping=JSON.parse(fs.readFileSync(new URL('./fixtures/independent-scu11-source-mapping.json',import.meta.url)));
const mapping=JSON.parse(fs.readFileSync(new URL('./fixtures/independent-seu10-source-mapping.json',import.meta.url)));
test('live SEU profiles preserve the complete independently reviewed source-bound objects',()=>{
 assert.equal(db.people.length,624+mapping.people.length+laterMapping.people.length+uestcMapping.people.length+hnuMapping.people.length+bnuMapping.people.length+tjuMapping.people.length+nkuMapping.people.length+dlutMapping.people.length+jluMapping.people.length+sduMapping.people.length+csuMapping.people.length+hustMapping.people.length+whuMapping.people.length+xjtuMapping.people.length+rucMapping.people.length+ecnuMapping.people.length+buaaMapping.people.length+tongjiMapping.people.length+bitMapping.people.length+nwpuMapping.people.length+scutMapping.people.length+ustcMapping.people.length+cauMapping.people.length+fduMapping.people.length+mucMapping.people.length+nwsuafMapping.people.length+oucMapping.people.length+lzuMapping.people.length+sjtuMapping.people.length+thuMapping.people.length+pkuMapping.people.length+zjuMapping.people.length);assert.equal(db.build_id,roster.build_id);
 for(const expected of mapping.people){
  const actual=db.people.find(p=>p.person_id===expected.person_id);assert.deepEqual(actual,expected);
  assert(matches(actual,{q:actual.name},db.org_units));assert(matches(actual,{school:'seu',org:actual.department_id},db.org_units));
  assert(!matches(actual,{school:'nju'},db.org_units));assert.equal(actual.quick_link_eligible,false);assert.equal(actual.include_in_current_faculty_count,false);
  assert.equal(actual.mentors.length,0);
  for(const stage of ['bachelor','master','doctor']) for(const event of stages(actual,stage)){assert.equal(event.event_kind,'degree');assert.equal(event.degree_awarded,true);}
 }
});
const {render}=createImmutableCohortRenderer({db,roster,fixtureId:import.meta.url});
for(const expected of mapping.people)test('live profile and lineage preserve unknown mentor status for '+expected.name,async()=>{
 const nodes=await render('#/person/'+expected.person_id);const html=['#main','#profile-content'].map(k=>nodes(k).innerHTML).join('\n');
 assert(html.includes(expected.name));assert(html.includes('东南大学'));
 const lineage=await render('#/person/'+expected.person_id+'/lineage');
 const relationHtml=['#main','#profile-content','#mind-stage'].map(k=>lineage(k).innerHTML).join('\n');
 assert(relationHtml.includes('0条已收录关系'));assert(relationHtml.includes('未核实'));
});

const htmlEscape=value=>String(value).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
test('actual profiles never inherit appointment institutions from directory affiliation',async()=>{
 const affected=db.people.filter(p=>(p.appointments||[]).some(a=>!a.institution));
 for(const id of ['hit-jgeng','hit-fujiahui','hit-20070140','hit-wangcong1','hit-liw','seu-zhangjianqiong','seu-liupeidang'])assert(affected.some(p=>p.person_id===id));
 for(const person of affected){
  const nodes=await render('#/person/'+person.person_id);
  const section=nodes('#profile-content').innerHTML.split('<h2>任职经历</h2>')[1];assert(section);
  const articles=[...section.matchAll(/<article>([\s\S]*?)<\/article>/g)].slice(0,person.appointments.length);
  assert.equal(articles.length,person.appointments.length);
  person.appointments.forEach((appointment,index)=>{
   const displayed=articles[index][1].match(/<\/h3><p>([\s\S]*?)<\/p>/)?.[1];
   assert.equal(displayed,htmlEscape(appointment.institution||'任职机构未核实'),person.person_id+' '+appointment.title);
   if(!appointment.institution)assert.notEqual(displayed,htmlEscape(person.department));
  });
 }
});
