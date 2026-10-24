"""Pinned public-metadata-v1 expectation domains, never runtime sanitization.
Original fixtures authenticate historical object versions. The separate public
mapping authenticates the metadata-clean view, not reconstruction of private bytes.
"""
import copy
import hashlib
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent
PUBLIC_MAPPING_SHA256 = '9a535022e0e3652714600db1654bd279058176c7239f1120980e630c6571b0da'

def _sha(value):
    return hashlib.sha256(value).hexdigest()

def public_contract(release, original_bytes, mapping_bytes=None):
    if mapping_bytes is None:
        mapping_bytes = (ROOT / 'fixtures/public-history-v1.json').read_bytes()
    assert _sha(mapping_bytes) == PUBLIC_MAPPING_SHA256, 'Public history mapping bytes changed'
    mapping = json.loads(mapping_bytes)
    assert set(mapping) == {'version', 'hash_scope', 'releases'}
    assert mapping['version'] == 'public_metadata_v1'
    assert mapping['hash_scope'] == 'metadata-clean historical JSON views; not original source-page or private artifact bytes'
    migration = mapping['releases'][str(release)]
    assert set(migration) == {'source_fixture_sha256', 'files'}
    assert _sha(original_bytes) == migration['source_fixture_sha256'], 'Original historical fixture bytes changed'
    original = json.loads(original_bytes)
    assert set(migration['files']) == set(original)
    result = copy.deepcopy(original)
    def migrated(pair, old):
        assert set(pair) == {'original_sha256', 'public_sha256'}
        assert pair['original_sha256'] == old, 'Historical-to-public predecessor mismatch'
        assert re.fullmatch(r'[0-9a-f]{64}', pair['public_sha256'])
        return pair['public_sha256']
    for rel, rule in migration['files'].items():
        assert set(rule) == {'lists', 'object_sha256', 'byte_sha256'}
        assert set(rule['lists']) == set(original[rel]['lists'])
        for key, pair in rule['lists'].items():
            result[rel]['lists'][key]['sha256'] = migrated(pair, original[rel]['lists'][key]['sha256'])
        for key in ('object_sha256', 'byte_sha256'):
            result[rel][key] = migrated(rule[key], original[rel][key])
    return result
