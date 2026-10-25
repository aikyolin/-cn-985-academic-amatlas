import {test} from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {matches, stages, officialProfileUrl} from '../site/model.js';
const db=JSON.parse(fs.readFileSync(new URL('../site/atlas.json',import.meta.url)));
const roster=JSON.parse(fs.readFileSync(new URL('../site/rosters.json',import.meta.url)));
const people=['nju-shiyini','nju-yangderui'].map(id=>db.people.find(p=>p.person_id===id));

test('current generated candidate exposes both new NJU identities and their own department',()=>{
 assert.equal(db.people.length,614);assert.equal(db.build_id,roster.build_id);
 for(const p of people){assert(p);assert(matches(p,{school:'nju',org:'nju-social-sciences'},db.org_units));assert(matches(p,{q:p.name},db.org_units));assert(!matches(p,{school:'hit'},db.org_units));assert.equal(p.quick_link_eligible,false);assert.equal(p.include_in_current_faculty_count,false);assert(officialProfileUrl(p).startsWith('https://sociology.nju.edu.cn/'));}
 const events=people.flatMap(p=>p.education);assert.equal(events.filter(e=>e.degree_awarded===true).length,4);assert.equal(events.filter(e=>e.degree_awarded===false).length,1);
 assert.equal(people.reduce((n,p)=>n+stages(p,'doctor').length,0),2);
 assert.equal(people.flatMap(p=>p.mentors).length,0);
});
let serial=0;
async function render(hash){
 const nodes=new Map(),node=k=>{if(!nodes.has(k))nodes.set(k,{innerHTML:'',textContent:'',value:'',style:{},events:{},dataset:{height:'320'},clientWidth:960,addEventListener(t,f){this.events[t]=f},click(){this.onclick?.()}});return nodes.get(k)};
 globalThis.document={querySelector:node,querySelectorAll:()=>[],getElementById:id=>node('#'+id)};
 globalThis.location={hash};globalThis.window={scrollTo(){},addEventListener(){}};
 globalThis.fetch=async p=>({ok:true,json:async()=>structuredClone(String(p).startsWith('atlas.json')?db:roster)});
 await import('../site/app.js?current-nju-release='+serial++);
 assert(!node('#main').innerHTML.includes('资料暂未加载'));return node;
}
for(const p of people)test('current app renders source-bound NJU profile '+p.name,async()=>{
 const nodes=await render('#/person/'+p.person_id);const html=[...['#main','#profile-content'].map(k=>nodes(k).innerHTML)].join('\n');
 assert(html.includes(p.name));assert(html.includes('南京大学'));assert(html.includes('未披露')||html.includes('未核实'));
 for(const e of p.education.filter(e=>e.degree_awarded===true))assert(html.includes(String(e.degree_awarded_year)));
});
