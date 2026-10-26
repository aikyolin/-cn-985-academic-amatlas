import {readAtlasFile} from './atlas-test-io.js';
import {test} from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {execFileSync} from 'node:child_process';
import {fileURLToPath} from 'node:url';
import {publicContract} from './public-history.js';
import {release25View} from './release-history.js';
const root=fileURLToPath(new URL('../',import.meta.url));
const read=rel=>fs.readFileSync(new URL('../'+rel,import.meta.url));
test('Python and JavaScript load exactly the same six pinned public-history contracts',()=>{
 const js=Object.fromEntries([25,26,27,28,29,30].map(n=>[n,publicContract(n,read(`tests/fixtures/release${n}-history.json`))]));
 const py=JSON.parse(execFileSync('python',['-c',"import sys,json,pathlib;sys.path.insert(0,'tests');from public_history import public_contract;print(json.dumps({n:public_contract(n,pathlib.Path(f'tests/fixtures/release{n}-history.json').read_bytes())for n in range(25,31)}))"],{cwd:root,encoding:'utf8',env:{...process.env,PYTHONDONTWRITEBYTECODE:'1'}}));
 assert.deepEqual(js,py);
});
test('public history rejects changed facts, source leaves, array boundaries and unknown siblings',()=>{
 const original=readAtlasFile(new URL('../data/atlas.json',import.meta.url));
 const mutations={
  name:v=>v.people[0].name='synthetic changed name',
  sourceUrl:v=>v.people[0].sources[0].url='https://example.invalid/changed',
  sourceId:v=>v.people[0].sources[0].id='synthetic-changed-source',
  award:v=>v.people.find(p=>p.education.length).education[0].degree_awarded='synthetic-invalid-state',
  extraRoot:v=>v.unexpected_sibling=[],
  extraSource:v=>v.people[0].sources[0].unexpected_sibling='synthetic',
  removedMetadata:v=>delete v.people[0].sources[0].retrieved_at,
  arrayOrder:v=>v.people.splice(0,2,...v.people.slice(0,2).reverse()),
  arrayLength:v=>v.people.shift(),
  frozenMetadata:v=>v.updated_at='2099-01-01',
  auditDigest:v=>v.people.slice(0,555).flatMap(p=>p.sources).find(s=>s.body_sha256).body_sha256='0'.repeat(64)
 };
 for(const [name,mutate]of Object.entries(mutations)){const changed=structuredClone(original);mutate(changed);assert.throws(()=>release25View(changed,'data/atlas.json'),{name:'AssertionError'},name);}
});
test('original fixtures and public mapping cannot be silently repinned or reformatted',()=>{
 const original=read('tests/fixtures/release25-history.json'),mapping=read('tests/fixtures/public-history-v1.json');
 assert.throws(()=>publicContract(25,Buffer.concat([original,Buffer.from(' ')])),{name:'AssertionError'});
 assert.throws(()=>publicContract(25,original,Buffer.concat([mapping,Buffer.from(' ')])),{name:'AssertionError'});
 const changed=JSON.parse(mapping);changed.releases['25'].files['data/atlas.json'].lists.people.public_sha256='0'.repeat(64);
 assert.throws(()=>publicContract(25,original,Buffer.from(JSON.stringify(changed))),{name:'AssertionError'});
});
