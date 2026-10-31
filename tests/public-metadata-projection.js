// Exact metadata compatibility for historical fixture comparisons only.
// Every differing leaf must match its full path and both immutable value hashes.
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
const raw=readFileSync(new URL('./fixtures/public-metadata-projection-hashes.json',import.meta.url));
const hash=s=>createHash('sha256').update(s).digest('hex');
assert.equal(hash(raw),'aabfaca5e80e290ff600238db33890600ccef087eb63ac1c608ac76168ecefe6');
const leaves=new Map(JSON.parse(raw).leaves.map(r=>[JSON.stringify(r.path),r]));
export function assertExactMetadataProjection(actual,expected,prefix,offset=0){
 function visit(a,b,path,root=false){
  if(Object.is(a,b))return;
  if(typeof a==='string'&&typeof b==='string'){
   const rule=leaves.get(JSON.stringify(path));assert(rule,'unlisted metadata difference '+JSON.stringify(path));
   assert.equal(hash(a),rule.after_sha256);assert.equal(hash(b),rule.before_sha256);return;
  }
  assert.equal(Array.isArray(a),Array.isArray(b));assert.equal(typeof a,typeof b);
  if(a===null||b===null||typeof a!=='object'){assert.deepEqual(a,b);return;}
  assert.deepEqual(Object.keys(a),Object.keys(b));
  for(const k of Object.keys(a))visit(a[k],b[k],path.concat(Array.isArray(a)?Number(k)+(root?offset:0):k));
 }
 visit(actual,expected,prefix,true);
}
