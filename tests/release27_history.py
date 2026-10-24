"""Exact historical projection for release27 regressions, not the live release28 view.
Every original list leaf is hash-checked before appends are removed. Metadata that
is permitted to advance is restored only from the frozen baseline fixture.
"""
import copy,hashlib,json,pathlib
CONTRACT=json.loads((pathlib.Path(__file__).parent/'fixtures/release27-history.json').read_text())
def object_sha(v):return hashlib.sha256(json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def release27_view(value,rel):
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
