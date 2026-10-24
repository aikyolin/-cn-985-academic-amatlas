import {test} from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import {createHash} from 'node:crypto';
import {historicalBytes,validateCurrentTree} from './source-date-history.js';
const baseline=JSON.parse(fs.readFileSync(new URL('./fixtures/release33-public-file-manifest.json',import.meta.url)));
const sha=raw=>createHash('sha256').update(raw).digest('hex');
test('Python and JavaScript expose the identical exact published historical bytes',()=>{
  for(const rel of ['site/app.js','site/model.js','scripts/build.py','site/atlas.json','site/rosters.json','site/exports/bit-cs-image-perception.xlsx']){
    const raw=historicalBytes(rel);assert.equal(sha(raw),baseline.files[rel].sha256,rel);assert.equal(raw.length,baseline.files[rel].bytes,rel);
  }
});
test('historical adapter rejects unknown paths and never exposes an arbitrary file reader',()=>{
  for(const rel of ['../outside','/absolute','site/../data/atlas.json','unknown.json'])assert.throws(()=>historicalBytes(rel));
});
test('current full tree is checked independently from historical assertions',()=>{
  const result=validateCurrentTree();assert.equal(result.status,'passed');assert.equal(result.files,410);
});

test('an external test-root mutation is inspected rather than replaced with local baseline bytes',()=>{
  const root=fs.mkdtempSync(path.join(os.tmpdir(),'atlas-reader-root-'));
  const previous=process.env.ACADEMIC_ATLAS_TEST_ROOT;
  try{
    fs.mkdirSync(path.join(root,'site'));fs.writeFileSync(path.join(root,'site/app.js'),'WRONG');
    assert.throws(()=>historicalBytes('site/app.js',root));
    process.env.ACADEMIC_ATLAS_TEST_ROOT=root;
    assert.throws(()=>historicalBytes('site/app.js'));
  }finally{
    if(previous===undefined)delete process.env.ACADEMIC_ATLAS_TEST_ROOT;else process.env.ACADEMIC_ATLAS_TEST_ROOT=previous;
    fs.rmSync(root,{recursive:true,force:true});
  }
});
