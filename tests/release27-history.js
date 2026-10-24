// Exact hash-checked historical public-v1 view; live release28 checks remain separate.
import fs from 'node:fs';
import {publicContract} from './public-history.js';
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
const CONTRACT=publicContract(27,fs.readFileSync(new URL('./fixtures/release27-history.json',import.meta.url)));
const sorted=x=>Array.isArray(x)?x.map(sorted):x&&typeof x==='object'?Object.fromEntries(Object.keys(x).sort().map(k=>[k,sorted(x[k])])):x;
const hash=x=>createHash('sha256').update(JSON.stringify(sorted(x))).digest('hex');
export function release27View(value,rel){
 const c=CONTRACT[rel],out=structuredClone(value);
 assert.deepEqual(Object.keys(out).sort(),[...Object.keys(c.lists),...Object.keys(c.metadata)].sort(),rel);
 for(const [key,rule]of Object.entries(c.lists)){
  const rows=rule.selected_ids?out[key].filter(x=>rule.selected_ids.includes(x.department_id)):out[key].slice(0,rule.length);
  assert.equal(rows.length,rule.length);assert.equal(hash(rows),rule.sha256,rel+'/'+key);out[key]=rows;
 }
 for(const [key,original]of Object.entries(c.metadata)){if(!c.mutable_metadata.includes(key))assert.deepEqual(out[key],original,rel+'/'+key);out[key]=structuredClone(original);}
 assert.equal(hash(out),c.object_sha256,rel);return out;
}
