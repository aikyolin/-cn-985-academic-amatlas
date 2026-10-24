// Exact hash-checked historical view; live release30 checks remain separate.
import fs from 'node:fs';
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
const fixture=fs.readFileSync(new URL('./fixtures/release29-history.json',import.meta.url));
assert.equal(createHash('sha256').update(fixture).digest('hex'),'57c463058fbe0e4078ee34426d006324999df5acafd86c70fbf59a428fd081c6','Historical fixture bytes changed');
const CONTRACT=JSON.parse(fixture);
const sorted=x=>Array.isArray(x)?x.map(sorted):x&&typeof x==='object'?Object.fromEntries(Object.keys(x).sort().map(k=>[k,sorted(x[k])])):x;
const hash=x=>createHash('sha256').update(JSON.stringify(sorted(x))).digest('hex');
export function release29View(value,rel){
 const c=CONTRACT[rel],out=structuredClone(value);
 assert.deepEqual(Object.keys(out).sort(),[...Object.keys(c.lists),...Object.keys(c.metadata)].sort(),rel);
 for(const [key,rule]of Object.entries(c.lists)){
  const rows=rule.selected_ids?out[key].filter(x=>rule.selected_ids.includes(x.department_id)):out[key].slice(0,rule.length);
  assert.equal(rows.length,rule.length);assert.equal(hash(rows),rule.sha256,rel+'/'+key);out[key]=rows;
 }
 for(const [key,original]of Object.entries(c.metadata)){if(!c.mutable_metadata.includes(key))assert.deepEqual(out[key],original,rel+'/'+key);out[key]=structuredClone(original);}
 assert.equal(hash(out),c.object_sha256,rel);return out;
}
