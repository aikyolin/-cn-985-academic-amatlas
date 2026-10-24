import {test} from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {createHash} from 'node:crypto';
import {execFileSync} from 'node:child_process';
import os from 'node:os';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
import {
  BASELINE_FIXTURE_SHA256,INVENTORY_FIXTURE_SHA256,APPEND_MANIFEST_SHA256,
  canonicalDigest,loadBaseline,publicAppendView,publicAppendBytes,
  ROOT,APPEND_MANIFEST_PATH,loadInventory,pinnedJson,validateAppendManifest,
  expectedFileInventory,validateTree,loadCurrentAppendManifest,endpointSha256,
  workbookEndpoints,validateReviewedSuffixes,
  reviewedScopeFromContract,SOURCE_CONTRACT_PATH,SOURCE_FIXTURE_PATH,
  BASELINE_PATH,INVENTORY_PATH,IMPLEMENTATION_ADDED_FILES,IMPLEMENTATION_MODIFIED_FILES,
} from './public-append-history.js';

const read=rel=>fs.readFileSync(new URL('../'+rel,import.meta.url));
const sha=value=>createHash('sha256').update(value).digest('hex');
const baseline=loadBaseline();
// Freeze current inputs through the pinned historical contract first. The suite
// must keep testing the same history after a separately reviewed append lands.
const originals=Object.fromEntries(Object.keys(baseline.files).map(rel=>[rel,publicAppendView(JSON.parse(read(rel)),rel)]));
const clone=rel=>structuredClone(originals[rel]);
const assertFrozenBytes=(bytes,rel)=>{
  assert.equal(bytes.length,baseline.files[rel].byte_length);
  assert.equal(sha(bytes),baseline.files[rel].byte_sha256);
};

test('append baseline and inventory are independently pinned; no append endpoint is invented',()=>{
  assert.equal(sha(read('tests/fixtures/release32-public-baseline.json')),BASELINE_FIXTURE_SHA256);
  assert.equal(sha(read('tests/fixtures/release32-public-file-manifest.json')),INVENTORY_FIXTURE_SHA256);
  assert.ok(APPEND_MANIFEST_SHA256===null||/^[0-9a-f]{64}$/.test(APPEND_MANIFEST_SHA256));
  const bytes=read('tests/fixtures/release32-public-baseline.json');
  assert.throws(()=>loadBaseline(Buffer.concat([bytes,Buffer.from(' ')])),/fixture bytes changed/);
  const changed=JSON.parse(bytes);changed.files['data/atlas.json'].lists.people.sha256='0'.repeat(64);
  assert.throws(()=>loadBaseline(Buffer.from(JSON.stringify(changed))),/fixture bytes changed/);
  assert.throws(()=>{baseline.files['data/atlas.json'].lists.people.ordered_ids.push('tamper');},TypeError);
  assert.equal(loadBaseline().files['data/atlas.json'].lists.people.length,606);
});

for(const rel of Object.keys(baseline.files))test(rel+': all frozen objects and original JSON bytes round-trip exactly',()=>{
  const before=JSON.stringify(originals[rel]);
  const view=publicAppendView(originals[rel],rel);
  assert.deepEqual(view,originals[rel]);
  assert.equal(canonicalDigest(view),baseline.files[rel].object_sha256);
  const bytes=publicAppendBytes(originals[rel],rel);
  assert.ok(Buffer.isBuffer(bytes));
  assertFrozenBytes(bytes,rel);
  assert.equal(JSON.stringify(originals[rel]),before,'validation must not mutate the input');
  // Views must not alias either the input or the shared fixture.
  const key=Object.keys(baseline.files[rel].lists)[0];view[key].push('detached view only');
  assert.equal(JSON.stringify(originals[rel]),before);
});

function advanceMetadata(value){
  if(typeof value==='string')return value+' synthetic append';
  if(typeof value==='number')return value+1;
  if(Array.isArray(value))return value.map(advanceMetadata);
  if(value!==null&&typeof value==='object')return Object.fromEntries(Object.entries(value).map(([key,item])=>[key,advanceMetadata(item)]));
  return value;
}

for(const rel of Object.keys(baseline.files))test(rel+': in-memory append and declared metadata changes recover the full frozen prefix',()=>{
  const value=clone(rel),rule=baseline.files[rel];
  for(const [key,list] of Object.entries(rule.lists)){
    let added={synthetic_append_only:true};
    if(list.identity_key){
      added=structuredClone(value[key][0]);
      added[list.identity_key]='synthetic-new-'+key;
    }
    if(list.selection==='identity_set')value[key].splice(1,0,added);
    else value[key].push(added);
  }
  for(const key of rule.mutable_metadata)value[key]=advanceMetadata(value[key]);
  const before=JSON.stringify(value);
  assertFrozenBytes(publicAppendBytes(value,rel),rel);
  assert.equal(JSON.stringify(value),before,'append projection must not sanitize or mutate live input');
});

const atlasMutations={
  'unknown root sibling':value=>value.unreviewed_sibling=[],
  'missing root key':value=>delete value.scope_note,
  'root key order':value=>{const old=value.schema_version;delete value.schema_version;value.schema_version=old;},
  'root array replaced by object':value=>value.people={},
  'root object replaced by array':value=>value.institution=[],
  'root metadata type changed':value=>value.scope_note=null,
  'immutable metadata value':value=>value.updated_at='2099-01-01',
  'immutable metadata nested sibling':value=>value.institution.unreviewed_sibling=true,
  'frozen person leaf':value=>value.people[0].name='synthetic changed name',
  'frozen source URL':value=>value.people[0].sources[0].url='https://example.invalid/changed',
  'frozen source identity':value=>value.people[0].sources[0].id='changed-source-id',
  'unknown source sibling':value=>value.people[0].sources[0].unreviewed_sibling=true,
  'missing source retrieval date':value=>delete value.people[0].sources[0].retrieved_at,
  'audit digest leaf':value=>value.people.flatMap(person=>person.sources).find(source=>source.body_sha256).body_sha256='0'.repeat(64),
  'true award changed to false':value=>value.people.flatMap(person=>person.education).find(event=>event.degree_awarded===true).degree_awarded=false,
  'false award changed to null':value=>value.people.flatMap(person=>person.education).find(event=>event.degree_awarded===false).degree_awarded=null,
  'null award changed to false':value=>value.people.flatMap(person=>person.education).find(event=>event.degree_awarded===null).degree_awarded=false,
  'frozen row order':value=>value.people.splice(0,2,value.people[1],value.people[0]),
  'frozen row deletion':value=>value.people.shift(),
  'duplicate appended old identity':value=>value.people.push(structuredClone(value.people[0])),
  'duplicate appended new identities':value=>value.people.push({person_id:'new-duplicate'},{person_id:'new-duplicate'}),
  'missing appended identity':value=>value.people.push({name:'no identity'}),
  'non-string appended identity':value=>value.people.push({person_id:false}),
  'appended unsupported value':value=>value.people.push({person_id:'new-person',invalid:undefined}),
  'short non-identity list':value=>value.limitations.pop(),
  'changed non-identity frozen list':value=>value.limitations[0]+=' changed',
};
for(const [name,mutate] of Object.entries(atlasMutations))test('append view rejects '+name,()=>{
  const value=clone('data/atlas.json');mutate(value);
  assert.throws(()=>publicAppendView(value,'data/atlas.json'),{name:'AssertionError'});
});

test('unknown domains and invalid root values are rejected rather than passed through',()=>{
  assert.throws(()=>publicAppendView({},'data/unreviewed.json'),/Unknown public append/);
  for(const value of [null,false,[],42,'{}'])assert.throws(()=>publicAppendView(value,'data/atlas.json'),/root must be an object/);
});

const exportMutations={
  'duplicate frozen export':value=>value.exports.push(structuredClone(value.exports[0])),
  'duplicate new export':value=>value.exports.push({department_id:'synthetic-new'},{department_id:'synthetic-new'}),
  'removed frozen export':value=>value.exports.shift(),
  'changed frozen export count':value=>value.exports[0].people_count++,
  'changed frozen export sibling':value=>value.exports[0].unreviewed_sibling=true,
  'reordered frozen exports':value=>value.exports.splice(0,2,value.exports[1],value.exports[0]),
  'missing new export identity':value=>value.exports.push({people_count:1}),
};
for(const [name,mutate] of Object.entries(exportMutations))test('identity-set selection rejects '+name,()=>{
  const value=clone('site/atlas.json');mutate(value);
  assert.throws(()=>publicAppendView(value,'site/atlas.json'),{name:'AssertionError'});
});

test('identity-set exports permit new rows at the beginning, middle and end, never sorting old rows',()=>{
  const value=clone('site/atlas.json');
  value.exports.unshift({department_id:'synthetic-a',people_count:1});
  value.exports.splice(50,0,{department_id:'synthetic-middle',people_count:1});
  value.exports.push({department_id:'synthetic-z',people_count:1});
  assertFrozenBytes(publicAppendBytes(value,'site/atlas.json'),'site/atlas.json');
});

const metadataMutations={
  'unknown mutable object sibling':value=>value.scope.unreviewed_sibling=true,
  'missing mutable object key':value=>delete value.scope.registry_complete,
  'mutable boolean changed to null':value=>value.scope.registry_complete=null,
  'mutable boolean changed to number':value=>value.scope.registry_complete=0,
  'mutable integer changed to boolean':value=>value.scope.target_university_count=false,
  'mutable integer changed to string':value=>value.scope.target_university_count='39',
  'mutable integer changed to float':value=>value.scope.target_university_count=39.5,
  'mutable nested array grows':value=>value.scope.active_institutions.push('new-school'),
  'mutable nested array shrinks':value=>value.scope.active_institutions.pop(),
  'mutable nested element type':value=>value.scope.active_institutions[0]=false,
  'mutable array becomes object':value=>value.scope.active_institutions={},
  'mutable object becomes array':value=>value.scope=[],
  'undeclared metadata value':value=>value.updated_at='2099-01-01',
  'duplicate appended task identity':value=>value.tasks.push(structuredClone(value.tasks[0])),
};
for(const [name,mutate] of Object.entries(metadataMutations))test('recursive mutable metadata guard rejects '+name,()=>{
  const value=clone('progress/work-queue.json');mutate(value);
  assert.throws(()=>publicAppendView(value,'progress/work-queue.json'),{name:'AssertionError'});
});

test('roster totals are mutable only with their exact primitive types and structure',()=>{
  for(const rel of ['data/rosters.json','site/rosters.json']){
    const value=clone(rel);value.totals.record_count++;
    assertFrozenBytes(publicAppendBytes(value,rel),rel);
    value.totals.current_employment_count_verified=0;
    assert.throws(()=>publicAppendView(value,rel),/primitive type changed/);
    const sourceMutation=clone(rel);sourceMutation.entries[0].unreviewed_source='https://example.invalid/';
    assert.throws(()=>publicAppendView(sourceMutation,rel),/frozen list content changed/);
  }
});

test('reconstructed-byte validation detects nested insertion-order changes, not just semantic hash changes',()=>{
  const value=clone('data/atlas.json'),person=value.people[0];
  const name=person.name;delete person.name;person.name=name;
  assert.equal(canonicalDigest(value),baseline.files['data/atlas.json'].object_sha256);
  assert.throws(()=>publicAppendView(value,'data/atlas.json'),/reconstructed byte hash changed/);
  assert.throws(()=>publicAppendBytes(value,'data/atlas.json'),/reconstructed byte hash changed/);
});

test('canonical digests match Python for Unicode codepoint and numeric-looking keys, null and booleans',()=>{
  const values=[
    null,false,true,0,9007199254740991,-9007199254740991,
    {'\u{10000}':'astral','\uE000':'BMP',z:'中文😀\n\t\u0000\u2028','10':false,'2':null},
    [{true:true,false:false,null:null},'é','e\u0301'],
  ];
  const python=JSON.parse(execFileSync('python',['-c',
    "import json,hashlib,sys; values=json.load(sys.stdin); print(json.dumps([hashlib.sha256(json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode('utf-8')).hexdigest() for v in values]))",
  ],{input:JSON.stringify(values),encoding:'utf8',env:{...process.env,PYTHONDONTWRITEBYTECODE:'1'}}));
  assert.deepEqual(values.map(canonicalDigest),python);
  assert.equal(new Set([canonicalDigest(null),canonicalDigest(false),canonicalDigest(0)]).size,3);
  assert.notEqual(canonicalDigest('é'),canonicalDigest('e\u0301'),'Unicode normalization is not allowed');
});

test('canonical encoding rejects non-JSON values and unsupported numeric representations rather than normalizing them',()=>{
  const sparse=[];sparse.length=1;
  const augmented=[];augmented.unreviewed=true;
  const cycle={};cycle.self=cycle;
  for(const value of [undefined,NaN,Infinity,-Infinity,-0,1.5,Number.MAX_SAFE_INTEGER+1,1n,()=>{},new Date(),sparse,augmented,cycle,'\uD800','\uDC00',{bad:undefined}]){
    assert.throws(()=>canonicalDigest(value),{name:'AssertionError'});
  }
});

function syntheticCase(){
  // Explicit synthetic bytes only. These do not describe any candidate facts.
  const old={
    'data/atlas.json':'old atlas\n',
    'site/exports/old-department.xlsx':'old workbook\n',
    'site/exports/待核对名录.xlsx':'old roster workbook\n',
    'tests/test_old.py':'old test\n',
  };
  const files={...old,
    'data/atlas.json':'new atlas\n',
    'site/exports/待核对名录.xlsx':'new roster workbook\n',
    'site/exports/new-department.xlsx':'new workbook\n',
    'progress/synthetic-coverage.json':'{"synthetic":true}\n',
    'tests/test_old.py':'reviewed IO seam\n',
    'tests/helper.py':'reviewed helper\n',
  };
  const baseline={source_commit:'synthetic-immutable-anchor'};
  const inventory={source_commit:baseline.source_commit,files:Object.fromEntries(Object.entries(old).map(([name,raw])=>[name,{bytes:Buffer.byteLength(raw),sha256:sha(raw)}]))};
  const reviewedScope={
    source_contract:{path:'tests/fixtures/synthetic-source.json',sha256:sha('synthetic reviewed source\n')},
    audit_digests:{source_input_sha256:sha('synthetic reviewed input\n'),review_result_sha256:sha('synthetic independent review\n')},
    added_output_paths:['site/exports/new-department.xlsx','progress/synthetic-coverage.json'],
  };
  const manifest={
    version:'public_append_manifest_v1',baseline_fixture_sha256:BASELINE_FIXTURE_SHA256,
    baseline_inventory_sha256:INVENTORY_FIXTURE_SHA256,baseline_commit:baseline.source_commit,
    source_contract:structuredClone(reviewedScope.source_contract),audit_digests:structuredClone(reviewedScope.audit_digests),
    changed_existing:Object.fromEntries(['data/atlas.json','site/exports/待核对名录.xlsx'].map(name=>[name,{before_sha256:sha(old[name]),after_sha256:sha(files[name]),byte_length:Buffer.byteLength(files[name])}])),
    deleted_existing:[],
    allowed_added_outputs:Object.fromEntries(reviewedScope.added_output_paths.map(name=>[name,{sha256:sha(files[name]),byte_length:Buffer.byteLength(files[name])}])),
    implementation_added_files:['tests/helper.py'],
    implementation_modified_files:{'tests/test_old.py':{before_sha256:sha(old['tests/test_old.py'])}},
  };
  return {manifest,files,options:{baseline,inventory,reviewedScope,implementationAddedFiles:['tests/helper.py'],implementationModifiedFiles:['tests/test_old.py']}};
}
const encoded=value=>Buffer.from(JSON.stringify(value,null,2)+'\n');
// Shared static synthetic golden, deliberately not a production manifest pin.
const SYNTHETIC_MANIFEST_SHA256='22a4924322aac83e40631744347324767bb6e5a46549706a41c7acd01319aee0';
function syntheticTree(files,work){
  const root=fs.mkdtempSync(path.join(os.tmpdir(),'public-append-contract-'));
  try{
    for(const [rel,raw] of Object.entries(files)){
      const filename=path.join(root,rel);fs.mkdirSync(path.dirname(filename),{recursive:true});fs.writeFileSync(filename,raw);
    }
    return work(root);
  }finally{fs.rmSync(root,{recursive:true,force:true});}
}

test('static synthetic manifest passes its independent pin and complete file-tree contract',()=>{
  const {manifest,files,options}=syntheticCase(),raw=encoded(manifest);
  assert.equal(sha(raw),SYNTHETIC_MANIFEST_SHA256);
  const parsed=validateAppendManifest(raw,SYNTHETIC_MANIFEST_SHA256,options);
  assert.deepEqual(parsed,manifest);
  syntheticTree(files,root=>{
    const actual=validateTree(root,parsed,options.inventory);
    assert.deepEqual(Object.keys(actual).sort(),Object.keys(files).sort());
  });
  assert.equal(expectedFileInventory(parsed,options.inventory)['tests/helper.py'],null,'implementation hashes must not introduce a manifest/helper hash cycle');
});

const manifestMutations={
  'unknown manifest sibling':value=>value.unreviewed=true,
  'missing manifest field':value=>delete value.audit_digests,
  'wrong baseline fixture pin':value=>value.baseline_fixture_sha256='0'.repeat(64),
  'wrong inventory fixture pin':value=>value.baseline_inventory_sha256='0'.repeat(64),
  'wrong predecessor anchor':value=>value.baseline_commit='unreviewed-anchor',
  'changed source-contract pin':value=>value.source_contract.sha256='0'.repeat(64),
  'changed review audit':value=>value.audit_digests.review_result_sha256='0'.repeat(64),
  'deleted existing endpoint':value=>value.deleted_existing=['data/atlas.json'],
  'unknown changed endpoint':value=>value.changed_existing['site/exports/old-department.xlsx']={before_sha256:sha('old workbook\n'),after_sha256:sha('changed workbook\n'),byte_length:17},
  'wrong before hash':value=>value.changed_existing['data/atlas.json'].before_sha256='0'.repeat(64),
  'unchanged endpoint claimed changed':value=>value.changed_existing['data/atlas.json'].after_sha256=value.changed_existing['data/atlas.json'].before_sha256,
  'boolean byte length':value=>value.changed_existing['data/atlas.json'].byte_length=true,
  'negative byte length':value=>value.changed_existing['data/atlas.json'].byte_length=-1,
  'extra endpoint sibling':value=>value.changed_existing['data/atlas.json'].unreviewed=true,
  'unknown added export':value=>value.allowed_added_outputs['site/exports/extra.xlsx']={sha256:'0'.repeat(64),byte_length:0},
  'missing reviewed added export':value=>delete value.allowed_added_outputs['site/exports/new-department.xlsx'],
  'expanded implementation additions':value=>value.implementation_added_files.push('tests/extra.js'),
  'duplicate implementation addition':value=>value.implementation_added_files.push('tests/helper.py'),
  'expanded implementation edits':value=>value.implementation_modified_files['app.js']={before_sha256:'0'.repeat(64)},
  'wrong implementation before hash':value=>value.implementation_modified_files['tests/test_old.py'].before_sha256='0'.repeat(64),
};
for(const [name,mutate] of Object.entries(manifestMutations))test('manifest rejects '+name+' even with a synthetic schema-test pin',()=>{
  const {manifest,options}=syntheticCase();mutate(manifest);
  // Re-pin only this explicit in-memory synthetic mutant to exercise schema defenses.
  const raw=encoded(manifest);
  assert.throws(()=>validateAppendManifest(raw,sha(raw),options),{name:'AssertionError'});
});

test('manifest byte pins and duplicate-key checks fail closed',()=>{
  const {manifest,options}=syntheticCase(),raw=encoded(manifest);
  for(const changed of [Buffer.concat([raw,Buffer.from(' ')]),Buffer.from(raw.toString().replace('new-department','bad-department'))])assert.throws(()=>validateAppendManifest(changed,SYNTHETIC_MANIFEST_SHA256,options),/pinned JSON bytes changed/);
  for(const pin of [null,'0'.repeat(64),'not-a-hash'])assert.throws(()=>validateAppendManifest(raw,pin,options));
  for(const text of ['{"a":1,"a":2}','{"nested":{"a":1,"\\u0061":2}}','[{"same":null,"same":false}]']){
    const bytes=Buffer.from(text);assert.throws(()=>pinnedJson(bytes,sha(bytes)),/duplicate JSON key/);
  }
});

test('complete tree rejects additions, omissions, altered old workbooks and symlinks',()=>{
  const {manifest,files,options}=syntheticCase();
  const changes=[
    root=>fs.writeFileSync(path.join(root,'site/exports/extra.xlsx'),'extra'),
    root=>fs.unlinkSync(path.join(root,'site/exports/old-department.xlsx')),
    root=>fs.writeFileSync(path.join(root,'site/exports/old-department.xlsx'),'Old workbook\n'),
    root=>fs.writeFileSync(path.join(root,'data/atlas.json'),'wrong endpoint\n'),
    root=>fs.writeFileSync(path.join(root,'extra.txt'),'extra'),
    root=>fs.writeFileSync(path.join(root,'__proto__'),'must not disappear from exact path set'),
    root=>fs.symlinkSync('data/atlas.json',path.join(root,'alias')),
  ];
  for(const change of changes)syntheticTree(files,root=>{
    change(root);assert.throws(()=>validateTree(root,manifest,options.inventory),{name:'AssertionError'});
  });
});

test('without a reviewed append pin the endpoint seam retains old exact hashes and exact workbook membership',()=>{
  const manifest=loadCurrentAppendManifest();
  if(APPEND_MANIFEST_SHA256===null){
    assert.equal(manifest,null);
    assert.equal(endpointSha256('data/atlas.json','literal-historical-hash'),'literal-historical-hash');
  }else assert.equal(endpointSha256('data/atlas.json','literal-historical-hash'),manifest.changed_existing['data/atlas.json']?.after_sha256??'literal-historical-hash');
  const inventory=loadInventory();
  const frozen=Object.fromEntries(Object.entries(inventory.files).filter(([rel])=>rel.startsWith('site/exports/')&&rel.endsWith('.xlsx')).map(([rel,item])=>[rel,item.sha256]));
  assert.equal(Object.keys(frozen).length,132);
  const expected={...frozen};
  if(manifest){
    for(const [rel,item] of Object.entries(manifest.changed_existing))if(Object.hasOwn(expected,rel))expected[rel]=item.after_sha256;
    for(const [rel,item] of Object.entries(manifest.allowed_added_outputs))if(rel.startsWith('site/exports/')&&rel.endsWith('.xlsx'))expected[rel]=item.sha256;
  }
  assert.deepEqual(workbookEndpoints(frozen),expected);
  const missing={...frozen};delete missing[Object.keys(missing)[0]];
  assert.throws(()=>workbookEndpoints(missing),/old workbook expectations differ/);
  assert.throws(()=>workbookEndpoints({...frozen,'site/exports/extra.xlsx':'0'.repeat(64)}),/old workbook expectations differ/);
});

test('an unpinned append manifest is rejected, not silently adopted',async()=>{
  const root=fs.mkdtempSync(path.join(os.tmpdir(),'public-append-unpinned-'));
  try{
    const helper=path.join(root,'tests/public-append-history.mjs');
    fs.mkdirSync(path.dirname(helper),{recursive:true});
    const source=fs.readFileSync(new URL('./public-append-history.js',import.meta.url),'utf8');
    fs.writeFileSync(helper,source.replace(/^export const APPEND_MANIFEST_SHA256=.*;$/m,'export const APPEND_MANIFEST_SHA256=null;'));
    const isolated=await import(pathToFileURL(helper).href);
    assert.equal(isolated.loadCurrentAppendManifest(),null);
    const manifestPath=path.join(root,APPEND_MANIFEST_PATH);
    fs.mkdirSync(path.dirname(manifestPath),{recursive:true});fs.writeFileSync(manifestPath,'{}\n');
    assert.throws(()=>isolated.loadCurrentAppendManifest(),/has no reviewed static pin/);
    assert.throws(()=>isolated.endpointSha256('data/atlas.json','old-hash'),/has no reviewed static pin/);
  }finally{fs.rmSync(root,{recursive:true,force:true});}
});

test('Python and JavaScript share the synthetic manifest result and rejection boundary',()=>{
  const {manifest,options}=syntheticCase();
  const vectors=[manifest,...Object.values(manifestMutations).map(mutate=>{const next=structuredClone(manifest);mutate(next);return next;})];
  const accepted=vectors.map(value=>{
    const raw=encoded(value);try{validateAppendManifest(raw,sha(raw),options);return true;}catch{return false;}
  });
  const python=JSON.parse(execFileSync('python',['-c',
    "import sys,json; sys.path.insert(0,'tests'); import public_append_history as h; p=json.load(sys.stdin); o=p['options']; kw=dict(baseline=o['baseline'],inventory=o['inventory'],reviewed_scope=o['reviewedScope'],implementation_added_files=o['implementationAddedFiles'],implementation_modified_files=o['implementationModifiedFiles']); outcomes=[]\nfor value in p['vectors']:\n raw=(json.dumps(value,ensure_ascii=False,indent=2)+'\\n').encode()\n try: h.validate_append_manifest(raw,h.sha256(raw),**kw); outcomes.append(True)\n except (ValueError,KeyError,TypeError): outcomes.append(False)\nprint(json.dumps({'accepted':outcomes,'inventory':h.expected_file_inventory(p['vectors'][0],o['inventory'])}))",
  ],{cwd:ROOT,input:JSON.stringify({vectors,options}),encoding:'utf8',env:{...process.env,PYTHONDONTWRITEBYTECODE:'1'}}));
  assert.deepEqual(python.accepted,accepted);
  assert.deepEqual(python.inventory,expectedFileInventory(manifest,options.inventory));
  assert.equal(accepted.filter(Boolean).length,1);
});

test('the independent empty-suffix contract rejects an extra person or export',()=>{
  const scope={
    file_suffixes:Object.fromEntries(Object.entries(baseline.files).map(([rel,spec])=>[rel,Object.fromEntries(Object.keys(spec.lists).map(key=>[key,{length:0,sha256:'4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945'}]))])),
    approved_department_ids:[],held_school_ids:['synthetic-held'],
  };
  validateReviewedSuffixes(originals,scope);
  for(const [rel,key,row] of [
    ['data/atlas.json','people',{person_id:'synthetic-new',school_id:'synthetic-held'}],
    ['site/atlas.json','exports',{department_id:'synthetic-extra'}],
  ]){
    const values={...originals,[rel]:clone(rel)};values[rel][key].push(row);
    assert.throws(()=>validateReviewedSuffixes(values,scope),/unreviewed suffix/);
  }
});

function syntheticSourceContract(){
  return {
    baseline_commit:baseline.source_commit,
    document_objects:[{file:'progress/synthetic-reviewed.json'},{file:'research/synthetic-reviewed.json'}],
    whole_holds:[{school_id:'synthetic-held',whole_scope_hold:true}],
    append_scope:{
      approved_department_ids:['synthetic-new-department'],
      added_report_paths:['progress/synthetic-reviewed.json'],
      added_context_paths:['research/synthetic-reviewed.json'],
      file_suffixes:Object.fromEntries(Object.entries(baseline.files).map(([rel,spec])=>[rel,Object.fromEntries(Object.entries(spec.lists).map(([key,rule])=>[key,{
        baseline_length:rule.length,length:0,sha256:'4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945',
        ...(rule.selection==='identity_set'?{mode:'new_department_rows'}:{}),
      }]))])),
      derived_site_expectation:'Explicit synthetic adapter input, not generated candidate facts.',
    },
  };
}

test('reviewed source adapter derives only reviewed namespaces and exact baseline boundaries with Python parity',()=>{
  const contract=syntheticSourceContract(),sourceRef={path:SOURCE_CONTRACT_PATH,sha256:sha('synthetic source bytes')};
  const auditDigests={source_input_sha256:sha('synthetic input'),review_result_sha256:sha('synthetic review')};
  const scope=reviewedScopeFromContract(contract,sourceRef,auditDigests);
  assert.deepEqual(scope.added_output_paths,['progress/synthetic-reviewed.json','research/synthetic-reviewed.json','site/exports/synthetic-new-department.xlsx']);
  assert.deepEqual(scope.held_school_ids,['synthetic-held']);
  assert.deepEqual(scope.file_suffixes['site/atlas.json'].exports,{length:0,sha256:'4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945'});
  const python=JSON.parse(execFileSync('python',['-c',
    "import sys,json; sys.path.insert(0,'tests'); import public_append_history as h; p=json.load(sys.stdin); print(json.dumps(h.reviewed_scope_from_contract(p['contract'],p['sourceRef'],p['auditDigests'])))",
  ],{cwd:ROOT,input:JSON.stringify({contract,sourceRef,auditDigests}),encoding:'utf8',env:{...process.env,PYTHONDONTWRITEBYTECODE:'1'}}));
  assert.deepEqual(scope,python);
  const mutations=[
    value=>value.baseline_commit='different',
    value=>value.append_scope.unreviewed=true,
    value=>value.append_scope.approved_department_ids.push('synthetic-new-department'),
    value=>value.append_scope.approved_department_ids.push(baseline.files['site/atlas.json'].lists.exports.ordered_ids[0]),
    value=>value.append_scope.added_report_paths[0]='progress/../escape.json',
    value=>value.append_scope.added_context_paths[0]='app/forbidden.json',
    value=>value.document_objects.push({file:'progress/extra.json'}),
    value=>value.append_scope.derived_site_expectation='',
    value=>value.append_scope.file_suffixes['data/atlas.json'].people.baseline_length++,
    value=>value.append_scope.file_suffixes['site/atlas.json'].exports.mode='prefix',
    value=>value.append_scope.file_suffixes['data/atlas.json'].people.mode='unreviewed',
    value=>value.append_scope.file_suffixes['data/atlas.json'].people.length=false,
    value=>value.whole_holds[0].whole_scope_hold=false,
    value=>value.whole_holds.push({school_id:'synthetic-held',whole_scope_hold:true}),
  ];
  for(const mutate of mutations){const value=structuredClone(contract);mutate(value);assert.throws(()=>reviewedScopeFromContract(value,sourceRef,auditDigests),{name:'AssertionError'});}
});

test('isolated synthetic final loader binds manifest, source contract and source fixture pins without touching candidate files',async()=>{
  const root=fs.mkdtempSync(path.join(os.tmpdir(),'public-append-reviewed-loader-'));
  try{
    const write=(rel,raw)=>{const filename=path.join(root,rel);fs.mkdirSync(path.dirname(filename),{recursive:true});fs.writeFileSync(filename,raw);};
    write(BASELINE_PATH,read(BASELINE_PATH));write(INVENTORY_PATH,read(INVENTORY_PATH));
    const sourceFixture=encoded({synthetic:'explicit reviewed fixture bytes'});
    const source=syntheticSourceContract();source.source_fixture={path:SOURCE_FIXTURE_PATH,sha256:sha(sourceFixture)};
    const sourceRaw=encoded(source),sourceRef={path:SOURCE_CONTRACT_PATH,sha256:sha(sourceRaw)};
    const auditDigests={source_input_sha256:sha('synthetic source input'),review_result_sha256:sha('synthetic independent review')};
    const scope=reviewedScopeFromContract(source,sourceRef,auditDigests),inventory=loadInventory();
    const manifest={
      version:'public_append_manifest_v1',baseline_fixture_sha256:BASELINE_FIXTURE_SHA256,baseline_inventory_sha256:INVENTORY_FIXTURE_SHA256,
      baseline_commit:baseline.source_commit,source_contract:sourceRef,audit_digests:auditDigests,
      changed_existing:{},deleted_existing:[],
      allowed_added_outputs:Object.fromEntries(scope.added_output_paths.map(rel=>[rel,{sha256:sha('synthetic output'),byte_length:16}])),
      implementation_added_files:[...IMPLEMENTATION_ADDED_FILES],
      implementation_modified_files:Object.fromEntries(IMPLEMENTATION_MODIFIED_FILES.map(rel=>[rel,{before_sha256:inventory.files[rel].sha256}])),
    };
    const manifestRaw=encoded(manifest);
    write(APPEND_MANIFEST_PATH,manifestRaw);write(SOURCE_CONTRACT_PATH,sourceRaw);write(SOURCE_FIXTURE_PATH,sourceFixture);
    const helper=path.join(root,'tests/public-append-history.mjs');
    const helperSource=fs.readFileSync(new URL('./public-append-history.js',import.meta.url),'utf8');
    // This pin exists only in the disposable synthetic test module, never production.
    fs.writeFileSync(helper,helperSource.replace(/^export const APPEND_MANIFEST_SHA256=.*;$/m,"export const APPEND_MANIFEST_SHA256='"+sha(manifestRaw)+"';"));
    const isolated=await import(pathToFileURL(helper).href);
    assert.deepEqual(isolated.loadCurrentAppendManifest(),manifest);
    write(SOURCE_FIXTURE_PATH,Buffer.concat([sourceFixture,Buffer.from(' ')]));
    assert.throws(()=>isolated.loadCurrentAppendManifest(),/pinned JSON bytes changed/);
    write(SOURCE_FIXTURE_PATH,sourceFixture);write(SOURCE_CONTRACT_PATH,Buffer.concat([sourceRaw,Buffer.from(' ')]));
    assert.throws(()=>isolated.loadCurrentAppendManifest(),/pinned JSON bytes changed/);
    write(SOURCE_CONTRACT_PATH,sourceRaw);write(APPEND_MANIFEST_PATH,Buffer.concat([manifestRaw,Buffer.from(' ')]));
    assert.throws(()=>isolated.loadCurrentAppendManifest(),/pinned JSON bytes changed/);
  }finally{fs.rmSync(root,{recursive:true,force:true});}
});
