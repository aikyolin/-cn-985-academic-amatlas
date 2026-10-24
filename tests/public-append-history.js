// Pinned clean-public append history. This is validation, never runtime cleansing.
import fs from 'node:fs';
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import path from 'node:path';
import {fileURLToPath} from 'node:url';

export const BASELINE_FIXTURE_SHA256='034470bc2d40294199f60051f0619d095ebd47aa882acf0652b5e20a47fb2526';
export const INVENTORY_FIXTURE_SHA256='c35c0512ff5a147a4d412da6abed4bd7fbe61cd8193893b90db57c394b798af9';
// Independently reviewed literal; never inferred or derived from live files.
export const APPEND_MANIFEST_SHA256='04d468e8c9393ceae148f0b5c6200172173f5c8ddaf12841cc6e47a690cc44ae';
export const ROOT=fileURLToPath(new URL('../',import.meta.url));
export const BASELINE_PATH='tests/fixtures/release32-public-baseline.json';
export const INVENTORY_PATH='tests/fixtures/release32-public-file-manifest.json';
export const APPEND_MANIFEST_PATH='tests/fixtures/rotation003-wave8-append-manifest.json';
export const SOURCE_CONTRACT_PATH='tests/fixtures/rotation003-wave8-source-contract.json';
export const SOURCE_FIXTURE_PATH='tests/fixtures/rotation003-wave8-clean-public-sources.json';
export const MUTABLE_ENDPOINTS=Object.freeze([
  'data/atlas.json','data/rosters.json','site/atlas.json','site/rosters.json',
  'progress/work-queue.json','progress/README.md','progress/current-coverage.md',
  'site/exports/待核对名录.csv','site/exports/待核对名录.xlsx',
]);
export const IMPLEMENTATION_MODIFIED_FILES=Object.freeze([
  'tests/test_rotation003_wave7_boundaries.py',
  'tests/rotation002-wave3-display-fix.test.js',
  'tests/rotation003-wave1-display-fix.test.js',
  'tests/test_rotation003_wave1_display_fix.py',
  'tests/test_rotation003_wave1_layout_fix.py',
]);
export const IMPLEMENTATION_ADDED_FILES=Object.freeze([
  BASELINE_PATH,INVENTORY_PATH,APPEND_MANIFEST_PATH,
  'tests/public_append_history.py','tests/public-append-history.js',
  'scripts/validate_source_contract.py','tests/test_rotation003_wave8_source_contract.py',
  'tests/fixtures/rotation003-wave8-source-contract.json',
  'tests/fixtures/rotation003-wave8-clean-public-sources.json',
  'tests/test_public_append_history.py','tests/public-append-history.test.js',
]);

const sha=value=>createHash('sha256').update(value).digest('hex');
const own=(value,key)=>Object.hasOwn(value,key);
const setOwn=(value,key,item)=>Object.defineProperty(value,key,{value:item,enumerable:true,writable:true,configurable:true});
const isObject=value=>value!==null && typeof value==='object' && !Array.isArray(value)
  && [Object.prototype,null].includes(Object.getPrototypeOf(value));
const codepointCompare=(left,right)=>{
  const a=Array.from(left,character=>character.codePointAt(0));
  const b=Array.from(right,character=>character.codePointAt(0));
  for(let i=0;i<Math.min(a.length,b.length);i++)if(a[i]!==b[i])return a[i]-b[i];
  return a.length-b.length;
};
const keys=value=>Object.keys(value).sort(codepointCompare);
const assertString=value=>assert.ok(!/[\uD800-\uDBFF](?![\uDC00-\uDFFF])|(?<![\uD800-\uDBFF])[\uDC00-\uDFFF]/u.test(value),'JSON strings must contain Unicode scalar values');

// Emit sorted keys directly: constructing a sorted object would silently reorder
// integer-looking keys, and JS's default sort uses UTF-16 rather than Python codepoints.
function canonicalJson(value,ancestors=new Set()){
  if(value===null)return 'null';
  if(typeof value==='boolean')return value?'true':'false';
  if(typeof value==='string'){assertString(value);return JSON.stringify(value);}
  if(typeof value==='number'){
    // These pinned public domains contain no floats. An explicit bounded numeric
    // contract avoids silently disagreeing with Python's float JSON representation.
    assert.ok(Number.isSafeInteger(value) && !Object.is(value,-0),'Canonical numbers must be safe integers, not floats or negative zero');
    return String(value);
  }
  assert.ok(Array.isArray(value)||isObject(value),'Only plain JSON values are supported');
  assert.ok(!ancestors.has(value),'Cyclic values are not JSON');
  ancestors.add(value);
  let result;
  if(Array.isArray(value)){
    assert.deepEqual(Object.keys(value),Array.from({length:value.length},(_,i)=>String(i)),'Sparse or augmented arrays are not JSON');
    assert.equal(Object.getOwnPropertySymbols(value).length,0,'Symbol keys are not JSON');
    result='['+value.map(item=>canonicalJson(item,ancestors)).join(',')+']';
  }else{
    assert.equal(Reflect.ownKeys(value).length,Object.keys(value).length,'Only enumerable string object keys are JSON');
    result='{'+keys(value).map(key=>{
      assertString(key);
      assert.ok(own(Object.getOwnPropertyDescriptor(value,key),'value'),'JSON properties cannot be accessors');
      return JSON.stringify(key)+':'+canonicalJson(value[key],ancestors);
    }).join(',')+'}';
  }
  ancestors.delete(value);
  return result;
}

export function canonicalDigest(value){return sha(Buffer.from(canonicalJson(value),'utf8'));}

function deepFreeze(value){
  if(value!==null && typeof value==='object'){
    for(const child of Object.values(value))deepFreeze(child);
    Object.freeze(value);
  }
  return value;
}

export function loadBaseline(bytes=fs.readFileSync(new URL('./fixtures/release32-public-baseline.json',import.meta.url))){
  assert.equal(sha(bytes),BASELINE_FIXTURE_SHA256,'Public append baseline fixture bytes changed');
  const baseline=JSON.parse(bytes);
  assert.equal(baseline.version,'public_append_baseline_v1');
  assert.equal(baseline.baseline_label,'release32-clean-public-606');
  for(const [rel,rule] of Object.entries(baseline.files)){
    assert.deepEqual(keys(rule),['byte_length','byte_sha256','lists','metadata','mutable_metadata','object_sha256','root_key_order']);
    assert.deepEqual([...rule.root_key_order].sort(codepointCompare),[...Object.keys(rule.lists),...Object.keys(rule.metadata)].sort(codepointCompare),rel+': fixture root keys');
    assert.equal(new Set(rule.root_key_order).size,rule.root_key_order.length,rel+': fixture duplicate root key');
    for(const key of rule.mutable_metadata)assert.ok(own(rule.metadata,key),rel+': unknown mutable metadata key');
    for(const [key,list] of Object.entries(rule.lists)){
      assert.ok(Number.isSafeInteger(list.length)&&list.length>=0,rel+'/'+key+': fixture length');
      assert.ok(['prefix','identity_set'].includes(list.selection),rel+'/'+key+': fixture selection');
      assert.match(list.sha256,/^[0-9a-f]{64}$/);
      if(list.identity_key){
        assert.equal(list.ordered_ids.length,list.length,rel+'/'+key+': fixture identity length');
        assert.equal(new Set(list.ordered_ids).size,list.length,rel+'/'+key+': duplicate fixture identity');
        assert.equal(canonicalDigest(list.ordered_ids),list.ordered_ids_sha256,rel+'/'+key+': fixture identity hash');
      }else assert.equal(list.selection,'prefix',rel+'/'+key+': identity-set selection needs identities');
    }
  }
  return deepFreeze(baseline);
}

function sameShape(value,baseline,label){
  if(baseline===null){assert.equal(value,null,label+': null type changed');return;}
  if(Array.isArray(baseline)){
    assert.ok(Array.isArray(value),label+': array type changed');
    assert.equal(value.length,baseline.length,label+': metadata array length changed');
    for(let i=0;i<baseline.length;i++)sameShape(value[i],baseline[i],label+'/'+i);
    return;
  }
  if(isObject(baseline)){
    assert.ok(isObject(value),label+': object type changed');
    assert.deepEqual(Object.keys(value),Object.keys(baseline),label+': metadata object structure or key order changed');
    for(const key of Object.keys(baseline))sameShape(value[key],baseline[key],label+'/'+key);
    return;
  }
  assert.equal(typeof value,typeof baseline,label+': primitive type changed');
  if(typeof baseline==='number')assert.ok(Number.isSafeInteger(value)&&!Object.is(value,-0),label+': integer type changed');
}

export function publicAppendView(value,rel){
  const baseline=loadBaseline();
  assert.ok(own(baseline.files,rel),'Unknown public append history domain: '+rel);
  const rule=baseline.files[rel];
  assert.ok(isObject(value),rel+': root must be an object');
  assert.deepEqual(Object.keys(value),rule.root_key_order,rel+': root keys or insertion order changed');
  // Also reject unsupported values in appended rows; never omit or repair them.
  canonicalJson(value);
  const result={};
  for(const key of rule.root_key_order){
    const label=rel+'/'+key;
    if(own(rule.lists,key)){
      const list=rule.lists[key],live=value[key];
      assert.ok(Array.isArray(live),label+': list type changed');
      assert.ok(live.length>=list.length,label+': frozen list shortened');
      let selected;
      if(list.identity_key){
        const allIds=live.map(row=>{
          assert.ok(isObject(row)&&own(row,list.identity_key),label+': missing row identity');
          const id=row[list.identity_key];
          assert.ok(typeof id==='string'&&id.length>0,label+': identity must be a nonempty string');
          return id;
        });
        assert.equal(new Set(allIds).size,allIds.length,label+': duplicate row identity');
        if(list.selection==='identity_set'){
          const frozenIds=new Set(list.ordered_ids);
          // Preserve live order. Sorting would conceal a reordered frozen export.
          selected=live.filter(row=>frozenIds.has(row[list.identity_key]));
        }else selected=live.slice(0,list.length);
        const selectedIds=selected.map(row=>row[list.identity_key]);
        assert.deepEqual(selectedIds,list.ordered_ids,label+': frozen identity order changed');
        assert.equal(canonicalDigest(selectedIds),list.ordered_ids_sha256,label+': frozen identity hash changed');
      }else selected=live.slice(0,list.length);
      assert.equal(selected.length,list.length,label+': frozen selection length changed');
      assert.equal(canonicalDigest(selected),list.sha256,label+': frozen list content changed');
      result[key]=structuredClone(selected);
    }else{
      sameShape(value[key],rule.metadata[key],label);
      if(rule.mutable_metadata.includes(key))result[key]=structuredClone(rule.metadata[key]);
      else{
        assert.equal(canonicalDigest(value[key]),canonicalDigest(rule.metadata[key]),label+': immutable metadata changed');
        result[key]=structuredClone(value[key]);
      }
    }
  }
  assert.equal(canonicalDigest(result),rule.object_sha256,rel+': reconstructed object changed');
  assertHistoricalBytes(result,rule,rel);
  return result;
}

function assertHistoricalBytes(result,rule,rel){
  const bytes=Buffer.from(JSON.stringify(result,null,2)+'\n','utf8');
  assert.equal(bytes.length,rule.byte_length,rel+': reconstructed byte length changed');
  assert.equal(sha(bytes),rule.byte_sha256,rel+': reconstructed byte hash changed');
  return bytes;
}

export function publicAppendBytes(value,rel){
  return Buffer.from(JSON.stringify(publicAppendView(value,rel),null,2)+'\n','utf8');
}

// JSON.parse alone would silently collapse duplicate keys. Parse the known-valid
// JSON text a second time for duplicate detection before using any manifest field.
function noDuplicateKeys(text){
  let offset=0;
  const whitespace=()=>{while(/\s/u.test(text[offset]??'')&&offset<text.length)offset++;};
  const string=()=>{
    const start=offset++;
    while(text[offset]!=='"'){if(text[offset]==='\\')offset++;offset++;}
    offset++;
    return JSON.parse(text.slice(start,offset));
  };
  const value=()=>{
    whitespace();
    if(text[offset]==='{'){
      offset++;whitespace();const seen=new Set();
      if(text[offset]==='}'){offset++;return;}
      while(true){
        whitespace();const key=string();
        assert.ok(!seen.has(key),'duplicate JSON key: '+key);seen.add(key);
        whitespace();offset++;value();whitespace();
        if(text[offset++]==='}')return;
      }
    }
    if(text[offset]==='['){
      offset++;whitespace();if(text[offset]===']'){offset++;return;}
      while(true){value();whitespace();if(text[offset++]===']')return;}
    }
    if(text[offset]==='"'){string();return;}
    while(offset<text.length&&!/[\s,}\]]/u.test(text[offset]))offset++;
  };
  value();
}

export function pinnedJson(raw,expectedSha256){
  assert.ok(typeof expectedSha256==='string'&&/^[0-9a-f]{64}$/.test(expectedSha256),'missing static SHA256 pin');
  assert.equal(sha(raw),expectedSha256,'pinned JSON bytes changed');
  const text=new TextDecoder('utf-8',{fatal:true}).decode(Buffer.from(raw));
  const value=JSON.parse(text);noDuplicateKeys(text);canonicalJson(value);
  return value;
}

export function loadInventory(){
  const inventory=pinnedJson(fs.readFileSync(path.join(ROOT,INVENTORY_PATH)),INVENTORY_FIXTURE_SHA256);
  assert.equal(inventory.version,'public_snapshot_inventory_v1','wrong inventory version');
  assert.equal(canonicalDigest(inventory.files),inventory.files_object_sha256,'inventory object hash');
  assert.equal(inventory.source_commit,loadBaseline().source_commit,'inventory anchor mismatch');
  return inventory;
}

const exactKeys=(value,expected,label)=>{
  assert.ok(isObject(value),'unknown/missing '+label+' fields');
  assert.deepEqual(keys(value),[...expected].sort(codepointCompare),'unknown/missing '+label+' fields');
};
const validPath=rel=>{
  assert.ok(typeof rel==='string'&&rel.length>0&&!rel.includes('\\')&&!rel.startsWith('/'),'invalid relative path');
  assert.ok(path.posix.normalize(rel)===rel&&!rel.endsWith('/')&&!rel.split('/').some(part=>part==='.'||part==='..'),'unsafe relative path');
  return rel;
};
const digest=value=>assert.ok(typeof value==='string'&&/^[0-9a-f]{64}$/.test(value),'invalid SHA256');
const endpoint=(value,changed=false)=>{
  exactKeys(value,changed?['before_sha256','after_sha256','byte_length']:['sha256','byte_length'],'endpoint');
  digest(value[changed?'after_sha256':'sha256']);
  assert.ok(Number.isSafeInteger(value.byte_length)&&value.byte_length>=0,'invalid byte length');
  if(changed){digest(value.before_sha256);assert.notEqual(value.before_sha256,value.after_sha256,'unchanged file claimed as changed');}
};
const sameSet=(left,right,label)=>assert.deepEqual([...new Set(left)].sort(codepointCompare),[...new Set(right)].sort(codepointCompare),label);

export function validateAppendManifest(raw,expectedSha256,{
  baseline,inventory,reviewedScope,
  implementationAddedFiles=IMPLEMENTATION_ADDED_FILES,
  implementationModifiedFiles=IMPLEMENTATION_MODIFIED_FILES,
}){
  const manifest=pinnedJson(raw,expectedSha256);
  exactKeys(manifest,['version','baseline_fixture_sha256','baseline_inventory_sha256','baseline_commit',
    'source_contract','audit_digests','changed_existing','deleted_existing','allowed_added_outputs',
    'implementation_added_files','implementation_modified_files'],'manifest');
  assert.equal(manifest.version,'public_append_manifest_v1','wrong manifest version');
  assert.equal(manifest.baseline_fixture_sha256,BASELINE_FIXTURE_SHA256,'wrong baseline pin');
  assert.equal(manifest.baseline_inventory_sha256,INVENTORY_FIXTURE_SHA256,'wrong inventory pin');
  assert.equal(manifest.baseline_commit,baseline.source_commit,'wrong baseline anchor');
  assert.equal(manifest.baseline_commit,inventory.source_commit,'wrong inventory anchor');
  exactKeys(manifest.source_contract,['path','sha256'],'source contract');
  validPath(manifest.source_contract.path);digest(manifest.source_contract.sha256);
  assert.deepEqual(manifest.source_contract,reviewedScope.source_contract,'source contract differs from reviewed scope');
  exactKeys(manifest.audit_digests,['source_input_sha256','review_result_sha256'],'audit digests');
  for(const hash of Object.values(manifest.audit_digests))digest(hash);
  assert.deepEqual(manifest.audit_digests,reviewedScope.audit_digests,'review audit differs');
  assert.deepEqual(manifest.deleted_existing,[],'deletion is not an append');
  const changed=manifest.changed_existing;
  assert.ok(isObject(changed)&&Object.keys(changed).every(rel=>MUTABLE_ENDPOINTS.includes(rel)),'unapproved changed endpoint');
  for(const [rel,item] of Object.entries(changed)){
    validPath(rel);endpoint(item,true);
    assert.ok(own(inventory.files,rel)&&item.before_sha256===inventory.files[rel].sha256,'before endpoint differs from frozen inventory');
  }
  const added=manifest.allowed_added_outputs;
  assert.ok(isObject(added),'added outputs must be a mapping');
  sameSet(Object.keys(added),reviewedScope.added_output_paths,'added outputs differ from reviewed scope');
  for(const [rel,item] of Object.entries(added)){
    validPath(rel);endpoint(item);
    assert.ok(!own(inventory.files,rel),'added output already exists');
  }
  const addedCode=manifest.implementation_added_files;
  assert.ok(Array.isArray(addedCode)&&addedCode.length===new Set(addedCode).size,'implementation additions differ from reviewed patch');
  sameSet(addedCode,implementationAddedFiles,'implementation additions differ from reviewed patch');
  for(const rel of addedCode){
    validPath(rel);
    assert.ok(!own(inventory.files,rel)&&!own(added,rel),'invalid implementation addition');
  }
  const modifiedCode=manifest.implementation_modified_files;
  assert.ok(isObject(modifiedCode),'implementation edits differ from reviewed patch');
  sameSet(Object.keys(modifiedCode),implementationModifiedFiles,'implementation edits differ from reviewed patch');
  for(const [rel,item] of Object.entries(modifiedCode)){
    exactKeys(item,['before_sha256'],'implementation edit');
    assert.ok(own(inventory.files,rel)&&item.before_sha256===inventory.files[rel].sha256,'implementation before hash differs');
  }
  return manifest;
}

export function expectedFileInventory(manifest,inventory){
  const expected=structuredClone(inventory.files);
  for(const [rel,item] of Object.entries(manifest.changed_existing))setOwn(expected,rel,{bytes:item.byte_length,sha256:item.after_sha256});
  for(const [rel,item] of Object.entries(manifest.allowed_added_outputs))setOwn(expected,rel,{bytes:item.byte_length,sha256:item.sha256});
  for(const rel of manifest.implementation_added_files)setOwn(expected,rel,null);
  for(const rel of Object.keys(manifest.implementation_modified_files))setOwn(expected,rel,null);
  return expected;
}

export function validateTree(root,manifest,inventory){
  const actual={},ignored=new Set(['.git','__pycache__','node_modules','.pytest_cache']);
  const visit=(directory,prefix='')=>{
    for(const entry of fs.readdirSync(directory,{withFileTypes:true})){
      if(ignored.has(entry.name))continue;
      const rel=prefix+entry.name,target=path.join(directory,entry.name);
      assert.ok(!entry.isSymbolicLink(),'symlink in candidate: '+rel);
      if(entry.isDirectory())visit(target,rel+'/');
      else if(entry.isFile()){
        const raw=fs.readFileSync(target);setOwn(actual,rel,{bytes:raw.length,sha256:sha(raw)});
      }
    }
  };
  visit(root);
  const expected=expectedFileInventory(manifest,inventory);
  sameSet(Object.keys(actual),Object.keys(expected),'candidate file set differs');
  for(const [rel,item] of Object.entries(expected))if(item!==null)assert.deepEqual(actual[rel],item,'candidate endpoint bytes differ: '+rel);
  const changed=Object.keys(inventory.files).filter(rel=>!own(manifest.implementation_modified_files,rel)&&canonicalDigest(actual[rel])!==canonicalDigest(inventory.files[rel]));
  sameSet(changed,Object.keys(manifest.changed_existing),'actual changed set differs');
  return actual;
}

export function loadCurrentAppendManifest(){
  if(APPEND_MANIFEST_SHA256===null){
    assert.ok(!fs.existsSync(path.join(ROOT,APPEND_MANIFEST_PATH)),'append manifest is present but has no reviewed static pin');
    return null;
  }
  const raw=fs.readFileSync(path.join(ROOT,APPEND_MANIFEST_PATH));
  const pinned=pinnedJson(raw,APPEND_MANIFEST_SHA256),sourceRef=pinned.source_contract;
  exactKeys(sourceRef,['path','sha256'],'source contract');
  assert.equal(sourceRef.path,SOURCE_CONTRACT_PATH,'unexpected source contract path');
  const source=pinnedJson(fs.readFileSync(path.join(ROOT,SOURCE_CONTRACT_PATH)),sourceRef.sha256);
  assert.equal(source.source_fixture.path,SOURCE_FIXTURE_PATH,'unexpected reviewed source fixture path');
  pinnedJson(fs.readFileSync(path.join(ROOT,SOURCE_FIXTURE_PATH)),source.source_fixture.sha256);
  const reviewedScope=reviewedScopeFromContract(source,sourceRef,pinned.audit_digests);
  return validateAppendManifest(raw,APPEND_MANIFEST_SHA256,{baseline:loadBaseline(),inventory:loadInventory(),reviewedScope});
}

export function endpointSha256(rel,historicalSha256){
  const manifest=loadCurrentAppendManifest();
  return manifest&&own(manifest.changed_existing,rel)?manifest.changed_existing[rel].after_sha256:historicalSha256;
}

export function workbookEndpoints(historical){
  const inventory=loadInventory().files;
  const frozen=Object.fromEntries(Object.entries(inventory).filter(([rel])=>rel.startsWith('site/exports/')&&rel.endsWith('.xlsx')).map(([rel,item])=>[rel,item.sha256]));
  assert.deepEqual(historical,frozen,'old workbook expectations differ from frozen 132-file inventory');
  const manifest=loadCurrentAppendManifest();
  const expected=Object.fromEntries(Object.entries(historical).map(([rel,hash])=>[rel,endpointSha256(rel,hash)]));
  if(manifest)for(const [rel,item] of Object.entries(manifest.allowed_added_outputs))if(rel.startsWith('site/exports/')&&rel.endsWith('.xlsx'))expected[rel]=item.sha256;
  return expected;
}

export function validateReviewedSuffixes(liveFiles,reviewedScope){
  const baseline=loadBaseline();
  exactKeys(liveFiles,Object.keys(baseline.files),'live JSON domain');
  exactKeys(reviewedScope.file_suffixes,Object.keys(baseline.files),'reviewed suffix domain');
  const suffixes={};
  for(const [rel,spec] of Object.entries(baseline.files)){
    publicAppendView(liveFiles[rel],rel);
    const suffixSpec=reviewedScope.file_suffixes[rel];
    exactKeys(suffixSpec,Object.keys(spec.lists),'reviewed suffix list');
    suffixes[rel]={};
    for(const [key,frozen] of Object.entries(spec.lists)){
      const rows=liveFiles[rel][key],oldIds=new Set(frozen.ordered_ids);
      const added=frozen.selection==='identity_set'?rows.filter(row=>!oldIds.has(row[frozen.identity_key])):rows.slice(frozen.length);
      const rule=suffixSpec[key];
      exactKeys(rule,['length','sha256'],'suffix');
      assert.ok(Number.isSafeInteger(rule.length)&&rule.length>=0,'invalid suffix length');digest(rule.sha256);
      assert.ok(added.length===rule.length&&canonicalDigest(added)===rule.sha256,'unreviewed suffix: '+rel+':'+key);
      suffixes[rel][key]=added;
    }
  }
  const people=suffixes['data/atlas.json'].people;
  const departments=[...new Set(people.map(person=>person.department_id))].sort(codepointCompare);
  assert.deepEqual(departments,[...reviewedScope.approved_department_ids].sort(codepointCompare),'approved departments differ from source people');
  assert.equal(departments.length,reviewedScope.approved_department_ids.length,'duplicate approved department');
  assert.ok(departments.every(id=>typeof id==='string'&&/^[A-Za-z0-9_-]+$/.test(id)),'invalid approved department ID');
  const oldDepartments=new Set(baseline.files['site/atlas.json'].lists.exports.ordered_ids);
  assert.ok(!departments.some(id=>oldDepartments.has(id)),'existing department append requires separately reviewed export projection');
  sameSet(suffixes['site/atlas.json'].exports.map(row=>row.department_id),departments,'exports differ from reviewed departments');
  const held=new Set(reviewedScope.held_school_ids);
  for(const lists of Object.values(suffixes))for(const key of ['people','pending_people','org_units','entries','source_observations']){
    for(const row of lists[key]??[])assert.ok(!held.has(row.school_id),'held school promoted in new scope');
  }
  const orgs=new Map(liveFiles['data/atlas.json'].org_units.map(row=>[row.id,row]));
  for(const person of people)assert.ok(orgs.has(person.department_id)&&orgs.get(person.department_id).school_id===person.school_id,'new person department/school mismatch');
  assert.deepEqual(liveFiles['data/atlas.json'].people,liveFiles['site/atlas.json'].people,'canonical/site people mismatch');
  assert.deepEqual(liveFiles['data/atlas.json'].pending_people,liveFiles['site/atlas.json'].pending_people,'canonical/site pending mismatch');
  assert.equal(liveFiles['site/atlas.json'].build_id,liveFiles['site/rosters.json'].build_id,'live build IDs differ');
  return suffixes;
}

export function reviewedScopeFromContract(contract,sourceRef,auditDigests){
  const baseline=loadBaseline(),inventory=loadInventory().files;
  assert.equal(contract.baseline_commit,baseline.source_commit,'source contract baseline differs');
  const scope=contract.append_scope;
  exactKeys(scope,['approved_department_ids','added_report_paths','added_context_paths','file_suffixes','derived_site_expectation'],'reviewed append scope');
  const departments=scope.approved_department_ids;
  assert.ok(Array.isArray(departments)&&departments.every(id=>typeof id==='string'&&/^[A-Za-z0-9_-]+$/.test(id)),'invalid reviewed department IDs');
  assert.equal(new Set(departments).size,departments.length,'duplicate reviewed department');
  const oldDepartments=new Set(baseline.files['site/atlas.json'].lists.exports.ordered_ids);
  assert.ok(!departments.some(id=>oldDepartments.has(id)),'existing department append needs a different reviewed projection');
  const reports=scope.added_report_paths,contexts=scope.added_context_paths;
  for(const [paths,prefix] of [[reports,'progress/'],[contexts,'research/']]){
    assert.ok(Array.isArray(paths)&&paths.every(rel=>typeof rel==='string'),'invalid reviewed document paths');
    assert.equal(new Set(paths).size,paths.length,'duplicate reviewed document path');
    for(const rel of paths){
      validPath(rel);
      assert.ok(rel.startsWith(prefix)&&rel.endsWith('.json')&&!own(inventory,rel),'invalid added document namespace');
    }
  }
  const documentPaths=contract.document_objects.map(row=>row.file);
  assert.equal(new Set(documentPaths).size,documentPaths.length,'duplicate reviewed document');
  sameSet([...reports,...contexts],documentPaths.filter(rel=>!own(inventory,rel)),'new documents differ from reviewed report/context scope');
  assert.ok(typeof scope.derived_site_expectation==='string'&&scope.derived_site_expectation.length>0,'missing generated expectation provenance');
  const fileSuffixes=scope.file_suffixes,normalized={};
  exactKeys(fileSuffixes,Object.keys(baseline.files),'source scope JSON domains');
  for(const [rel,spec] of Object.entries(baseline.files)){
    exactKeys(fileSuffixes[rel],Object.keys(spec.lists),'source scope arrays');
    normalized[rel]={};
    for(const [key,frozen] of Object.entries(spec.lists)){
      const row=fileSuffixes[rel][key],fields=['baseline_length','length','sha256'];
      if(frozen.selection==='identity_set')fields.push('mode');
      exactKeys(row,fields,'source scope suffix');
      assert.ok(Number.isSafeInteger(row.baseline_length)&&row.baseline_length===frozen.length,'source scope frozen boundary differs');
      if(frozen.selection==='identity_set')assert.equal(row.mode,'new_department_rows','source scope export selection differs');
      assert.ok(Number.isSafeInteger(row.length)&&row.length>=0,'source scope suffix length invalid');digest(row.sha256);
      normalized[rel][key]={length:row.length,sha256:row.sha256};
    }
  }
  const held=[];
  for(const row of contract.whole_holds){
    assert.ok(row.whole_scope_hold===true&&typeof row.school_id==='string','invalid whole-scope hold');held.push(row.school_id);
  }
  assert.equal(new Set(held).size,held.length,'duplicate held school');
  return {
    source_contract:structuredClone(sourceRef),audit_digests:structuredClone(auditDigests),
    added_output_paths:[...reports,...contexts,...departments.map(id=>'site/exports/'+id+'.xlsx')].sort(codepointCompare),
    file_suffixes:normalized,approved_department_ids:structuredClone(departments),held_school_ids:held,
  };
}
