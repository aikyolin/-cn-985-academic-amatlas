// Pinned public-metadata-v1 domains; no runtime cleansing or live-derived expectations.
import fs from 'node:fs';
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
const PUBLIC_MAPPING_SHA256='9a535022e0e3652714600db1654bd279058176c7239f1120980e630c6571b0da';
const sha=x=>createHash('sha256').update(x).digest('hex');
const keys=x=>Object.keys(x).sort();
export function publicContract(release,originalBytes,mappingBytes=fs.readFileSync(new URL('./fixtures/public-history-v1.json',import.meta.url))){
 assert.equal(sha(mappingBytes),PUBLIC_MAPPING_SHA256,'Public history mapping bytes changed');
 const mapping=JSON.parse(mappingBytes);
 assert.deepEqual(keys(mapping),['hash_scope','releases','version']);
 assert.equal(mapping.version,'public_metadata_v1');
 assert.equal(mapping.hash_scope,'metadata-clean historical JSON views; not original source-page or private artifact bytes');
 const migration=mapping.releases[String(release)];
 assert.deepEqual(keys(migration),['files','source_fixture_sha256']);
 assert.equal(sha(originalBytes),migration.source_fixture_sha256,'Original historical fixture bytes changed');
 const original=JSON.parse(originalBytes),result=structuredClone(original);
 assert.deepEqual(keys(migration.files),keys(original));
 const migrated=(pair,old)=>{
  assert.deepEqual(keys(pair),['original_sha256','public_sha256']);
  assert.equal(pair.original_sha256,old,'Historical-to-public predecessor mismatch');
  assert.match(pair.public_sha256,/^[0-9a-f]{64}$/);return pair.public_sha256;
 };
 for(const [rel,rule] of Object.entries(migration.files)){
  assert.deepEqual(keys(rule),['byte_sha256','lists','object_sha256']);
  assert.deepEqual(keys(rule.lists),keys(original[rel].lists));
  for(const [key,pair] of Object.entries(rule.lists))result[rel].lists[key].sha256=migrated(pair,original[rel].lists[key].sha256);
  for(const key of ['object_sha256','byte_sha256'])result[rel][key]=migrated(rule[key],original[rel][key]);
 }
 return result;
}
