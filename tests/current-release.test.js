import {createImmutableCohortRenderer} from './immutable-cohort-renderer.js';
import {readAtlasFile,createAtlasFetch} from './atlas-test-io.js';
import {test} from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {matches, stages, officialProfileUrl, mentorOfficialUrl, mentorProfileRoute} from '../site/model.js';
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
const firstMapping=JSON.parse(fs.readFileSync(new URL('./fixtures/independent-nju-source-mapping.json',import.meta.url)));
const nextMapping=JSON.parse(fs.readFileSync(new URL('./fixtures/independent-nju10-source-mapping.json',import.meta.url)));
const seuMapping=JSON.parse(fs.readFileSync(new URL('./fixtures/independent-seu10-source-mapping.json',import.meta.url)));
const scuMapping=JSON.parse(fs.readFileSync(new URL('./fixtures/independent-scu11-source-mapping.json',import.meta.url)));
const people=['nju-shiyini','nju-yangderui'].map(id=>db.people.find(p=>p.person_id===id));

test('current generated candidate exposes both new NJU identities and their own department',()=>{
 assert.equal(db.people.length,612+firstMapping.people.length+nextMapping.people.length+seuMapping.people.length+scuMapping.people.length+uestcMapping.people.length+hnuMapping.people.length+bnuMapping.people.length+tjuMapping.people.length+nkuMapping.people.length+dlutMapping.people.length+jluMapping.people.length+sduMapping.people.length+csuMapping.people.length+hustMapping.people.length+whuMapping.people.length+xjtuMapping.people.length+rucMapping.people.length+ecnuMapping.people.length+buaaMapping.people.length+tongjiMapping.people.length+bitMapping.people.length+nwpuMapping.people.length+scutMapping.people.length+ustcMapping.people.length+cauMapping.people.length+fduMapping.people.length+mucMapping.people.length+nwsuafMapping.people.length+oucMapping.people.length+lzuMapping.people.length+sjtuMapping.people.length+thuMapping.people.length+pkuMapping.people.length+zjuMapping.people.length);assert.equal(db.build_id,roster.build_id);
 for(const p of people){assert(p);assert(matches(p,{school:'nju',org:'nju-social-sciences'},db.org_units));assert(matches(p,{q:p.name},db.org_units));assert(!matches(p,{school:'hit'},db.org_units));assert.equal(p.quick_link_eligible,false);assert.equal(p.include_in_current_faculty_count,false);assert(officialProfileUrl(p).startsWith('https://sociology.nju.edu.cn/'));}
 const events=people.flatMap(p=>p.education);assert.equal(events.filter(e=>e.degree_awarded===true).length,4);assert.equal(events.filter(e=>e.degree_awarded===false).length,1);
 assert.equal(people.reduce((n,p)=>n+stages(p,'doctor').length,0),2);
 assert.equal(people.flatMap(p=>p.mentors).length,0);
});
const {render}=createImmutableCohortRenderer({db,roster,fixtureId:import.meta.url});
for(const p of people)test('current app renders source-bound NJU profile '+p.name,async()=>{
 const nodes=await render('#/person/'+p.person_id);const html=[...['#main','#profile-content'].map(k=>nodes(k).innerHTML)].join('\n');
 assert(html.includes(p.name));assert(html.includes('南京大学'));assert(html.includes('未披露')||html.includes('未核实'));
 for(const e of p.education.filter(e=>e.degree_awarded===true))assert(html.includes(String(e.degree_awarded_year)));
});

test('current generated candidate retains all reviewed ten-person facts and functional search',()=>{
 for(const expected of nextMapping.people){
  const actual=db.people.find(p=>p.person_id===expected.person_id);
  assert.deepEqual(actual,expected);
  assert(matches(actual,{q:actual.name},db.org_units));
  assert(matches(actual,{school:'nju',org:actual.department_id},db.org_units));
  assert.equal(actual.quick_link_eligible,false);
  assert.equal(actual.include_in_current_faculty_count,false);
  for(const mentor of actual.mentors){
   assert.equal(mentorOfficialUrl(mentor),'');assert.equal(mentorProfileRoute(mentor,db.people),'');
   if(mentor.formal_dissertation_advisor_verified===false) assert((mentor.type_label||mentor.type).includes('非'));
  }
 }
});
for(const expected of nextMapping.people)test('current app renders reviewed next NJU profile '+expected.name,async()=>{
 const nodes=await render('#/person/'+expected.person_id);
 const html=['#main','#profile-content'].map(k=>nodes(k).innerHTML).join('\n');
 assert(html.includes(expected.name));assert(html.includes('南京大学'));
 assert(!html.includes('资料暂未加载'));
 const lineage=await render('#/person/'+expected.person_id+'/lineage');
 const relationHtml=['#main','#profile-content','#mind-stage'].map(k=>lineage(k).innerHTML).join('\n');
 for(const mentor of expected.mentors){assert(relationHtml.includes(mentor.name));assert(relationHtml.includes(mentor.type_label||mentor.type));}
});
