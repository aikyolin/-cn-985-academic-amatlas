"""Exact historical projection for release30 regressions, not the live release31 view.
Every original list leaf is hash-checked before appends are removed. Metadata that
is permitted to advance is restored only from the frozen baseline fixture.
"""
import copy,hashlib,json,pathlib
FIXTURE=pathlib.Path(__file__).parent/'fixtures/release30-history.json'
assert hashlib.sha256(FIXTURE.read_bytes()).hexdigest()=='de597e5f93243275b591495729bfe5de29181e2993574e9472489bdf1de65cea','Historical fixture bytes changed'
CONTRACT=json.loads(FIXTURE.read_text())
def object_sha(v):return hashlib.sha256(json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def release30_view(value,rel):
    c=CONTRACT[rel];out=copy.deepcopy(value)
    assert set(out)==set(c['lists'])|set(c['metadata']),rel
    for key,rule in c['lists'].items():
        rows=out[key]
        if 'selected_ids'in rule:
            ids=rule['selected_ids'];rows=[x for x in rows if x['department_id']in ids]
        else:rows=rows[:rule['length']]
        assert len(rows)==rule['length'] and object_sha(rows)==rule['sha256'],(rel,key,'historical leaves changed')
        out[key]=rows
    for key,original in c['metadata'].items():
        if key not in c['mutable_metadata']:assert out[key]==original,(rel,key)
        out[key]=copy.deepcopy(original)
    assert object_sha(out)==c['object_sha256'],rel
    return out
