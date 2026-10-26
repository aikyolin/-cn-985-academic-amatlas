"""Actual temporary-file transport tests; no candidate data or generated outputs touched."""
import copy
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import atlas_storage as storage


class AtlasStorageTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.path = self.root / 'data/atlas.json'
        self.data = {'schema_version': 'test', 'institutions': [{'id': 'a'}, {'id': 'b'}, {'id': 'empty'}],
                     'people': [{'person_id': 'a-one', 'school_id': 'a', 'note': ' 中文 é e\u0301 😀 \n\t ', 'values': [None, False, 0, 1.0, -0.0]},
                                {'person_id': 'b-one', 'school_id': 'b'},
                                {'person_id': 'a-two', 'school_id': 'a'}], 'org_units': [], 'last': True}
        self.manifest = storage.write_atlas(self.path, self.data)

    def save_manifest(self, manifest):
        self.path.write_bytes(storage.compact_bytes(manifest))

    def replace_chunk(self, index, value=None, raw=None):
        part = self.manifest['parts'][index]
        if raw is None:
            raw = storage.compact_bytes(value)
        (self.path.parent / part['path']).write_bytes(raw)
        part.update(bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest())
        self.save_manifest(self.manifest)

    def rejects_manifest(self, mutate):
        m = copy.deepcopy(self.manifest)
        mutate(m)
        self.save_manifest(m)
        with self.assertRaises((ValueError, OSError)):
            storage.load_atlas(self.path)

    def test_roundtrip_exact_types_order_unicode_and_global_interleave(self):
        before = storage.compact_bytes(self.data)
        value = storage.load_atlas(self.path)
        self.assertEqual(storage.compact_bytes(value), before)
        self.assertEqual(list(value), list(self.data))
        self.assertEqual([x['person_id'] for x in value['people']], ['a-one', 'b-one', 'a-two'])
        self.assertEqual([x['school_id'] for x in self.manifest['parts']], ['a', 'b'])
        self.assertEqual(self.manifest['atlas']['people'], [])
        self.assertEqual(storage.compact_bytes(self.data), before)

    def test_deterministic_writer_and_validated_input_order(self):
        one = storage.storage_inputs(self.path)
        storage.write_atlas(self.path, self.data)
        self.assertEqual(one, storage.storage_inputs(self.path))
        self.assertEqual([x[0] for x in one], ['atlas.json', 'people/a.json', 'people/b.json'])
        for _, raw in one:
            self.assertEqual(raw.count(b'\n'), 1)
            self.assertEqual(storage.compact_bytes(storage.strict_json(raw)), raw)

    def test_empty_population_has_no_empty_school_chunks(self):
        self.data['people'] = []
        storage.write_atlas(self.path, self.data)
        self.assertEqual(storage.load_atlas(self.path), self.data)
        self.assertEqual(list((self.path.parent / 'people').iterdir()), [])

    def test_no_monolithic_fallback(self):
        self.path.write_bytes(storage.compact_bytes(self.data))
        with self.assertRaises(ValueError): storage.load_atlas(self.path)

    def test_manifest_shape_and_occupied_people(self):
        for change in [lambda m:m.update(extra=1), lambda m:m.update(format='other'),
                       lambda m:m['atlas'].update(people=[{}]), lambda m:m.update(parts={})]:
            with self.subTest(change=change): self.rejects_manifest(change)

    def test_unsafe_paths(self):
        for bad in ['../a.json', '/a.json', 'https://example.test/a.json', 'people/a.json?x',
                    'people/a.json#x', 'people\\a.json', 'people/%61.json', 'people/../a.json']:
            with self.subTest(path=bad): self.rejects_manifest(lambda m:m['parts'][0].update(path=bad))

    def test_part_school_and_duplicate_institutions(self):
        for change in [lambda m:m['parts'][0].update(school_id='unknown'),
                       lambda m:m['parts'].append(copy.deepcopy(m['parts'][0])),
                       lambda m:m['atlas']['institutions'].append({'id':'a'}),
                       lambda m:m['parts'][0].update(extra=0)]:
            with self.subTest(change=change): self.rejects_manifest(change)

    def test_invalid_counts_hash_and_bytes(self):
        for key, val in [('count', True), ('count', 0), ('count', 1.0), ('count', 100001),
                         ('bytes', False), ('bytes', 0), ('bytes', storage.MAX_PART_BYTES+1),
                         ('sha256', 'A'*64), ('sha256', 'x')]:
            with self.subTest(key=key,val=val): self.rejects_manifest(lambda m:m['parts'][0].update({key:val}))

    def test_order_duplicate_missing_extra(self):
        for order in [['a-one','a-one','a-two'], ['a-one','b-one'], ['a-one','b-one','unknown']]:
            with self.subTest(order=order): self.rejects_manifest(lambda m:m.update(people_order=order))

    def test_first_school_order_and_chunk_relative_order(self):
        self.rejects_manifest(lambda m:m['parts'].reverse())
        self.save_manifest(self.manifest)
        p=self.path.parent/self.manifest['parts'][0]['path'];chunk=storage.strict_json(p.read_bytes());chunk['people'].reverse()
        self.replace_chunk(0,chunk)
        with self.assertRaises(ValueError): storage.load_atlas(self.path)

    def test_raw_byte_hash_before_json(self):
        path=self.path.parent/self.manifest['parts'][0]['path'];path.write_bytes(path.read_bytes().replace(b'a-one',b'x-one'))
        with self.assertRaisesRegex(ValueError,'SHA256'): storage.load_atlas(self.path)

    def test_raw_length(self):
        path=self.path.parent/self.manifest['parts'][0]['path'];path.write_bytes(path.read_bytes()+b' ')
        with self.assertRaisesRegex(ValueError,'length'): storage.load_atlas(self.path)

    def test_chunk_unknown_shape_and_foreign_school(self):
        base=storage.strict_json((self.path.parent/self.manifest['parts'][0]['path']).read_bytes())
        for change in [lambda c:c.update(extra=1),lambda c:c.update(school_id='b'),
                       lambda c:c['people'][0].update(school_id='b'),
                       lambda c:c['people'][1].update(person_id='a-one'),
                       lambda c:c.update(people=[])]:
            chunk=copy.deepcopy(base);change(chunk);self.replace_chunk(0,chunk)
            with self.assertRaises(ValueError): storage.load_atlas(self.path)

    def test_strict_json_invalid_utf8_bom_duplicates_nonfinite_surrogates(self):
        for raw in [b'\xff', b'\xef\xbb\xbf{}', b'{"a":1,"a":2}', b'{"a":{"b":1,"b":2}}',
                    b'NaN', b'Infinity', b'1e999', b'"\\ud800"', b'['*514+b'0'+b']'*514]:
            with self.subTest(raw=raw[:40]):
                with self.assertRaises(ValueError): storage.strict_json(raw)

    def test_valid_hash_does_not_allow_invalid_json(self):
        self.replace_chunk(0,raw=b'{"school_id":"a","school_id":"a","people":[]}\n')
        with self.assertRaisesRegex(ValueError,'Duplicate'): storage.load_atlas(self.path)

    def test_missing_and_orphan_chunks(self):
        directory=self.path.parent/'people';extra=directory/'other.json';extra.write_text('{}')
        with self.assertRaisesRegex(ValueError,'Orphan'): storage.load_atlas(self.path)
        extra.unlink();(directory/'a.json').unlink()
        with self.assertRaises(ValueError): storage.load_atlas(self.path)

    def test_manifest_chunk_and_directory_symlinks(self):
        part=self.path.parent/'people/a.json';target=self.root/'outside.json';target.write_bytes(part.read_bytes());part.unlink();part.symlink_to(target)
        with self.assertRaises(ValueError):storage.load_atlas(self.path)
        with self.assertRaises(ValueError):storage.write_atlas(self.path,self.data)
        part.unlink();part.write_bytes(target.read_bytes())
        alias=self.root/'alias';alias.symlink_to(self.path.parent,target_is_directory=True)
        with self.assertRaises(ValueError):storage.load_atlas(alias/'atlas.json')
        manifest=self.root/'manifest.json';manifest.symlink_to(self.path)
        with self.assertRaises(ValueError):storage.load_atlas(manifest)

    def test_bounds_checked_before_reading_parts(self):
        with patch.object(storage,'MAX_MANIFEST_BYTES',2):
            with self.assertRaises(ValueError):storage.load_atlas(self.path)
        with patch.object(storage,'MAX_TOTAL_BYTES',10):
            with self.assertRaises(ValueError):storage.load_atlas(self.path)
        with patch.object(storage,'MAX_PEOPLE',2):
            with self.assertRaises(ValueError):storage.load_atlas(self.path)

    def test_environment_root_never_falls_back(self):
        other=self.root/'other/atlas.json';other.parent.mkdir();other.write_bytes(self.path.read_bytes())
        with self.assertRaises(ValueError):storage.load_atlas(other)

    def test_writer_rejects_invalid_data_without_replacing_manifest(self):
        before=self.path.read_bytes();bad=copy.deepcopy(self.data);bad['people'][1]['person_id']='a-one'
        with self.assertRaises(ValueError):storage.write_atlas(self.path,bad)
        self.assertEqual(self.path.read_bytes(),before)
        for value in [float('nan'),float('inf'),object(),{1:'bad'}]:
            with self.assertRaises((ValueError,TypeError)):storage.compact_bytes(value)

    def test_build_id_independent_framing_and_real_inputs(self):
        for name in storage.BUILD_FILES:
            p=self.root/name;p.parent.mkdir(exist_ok=True,parents=True);p.write_bytes(name.encode())
        inputs=[('data/'+label,raw)for label,raw in storage.storage_inputs(self.path)]
        inputs += [(label,(self.root/label).read_bytes())for label in storage.BUILD_FILES]
        payload=b'academic-atlas-build-school-parts-v1\0'
        for label,raw in inputs:
            name=label.encode();payload+=len(name).to_bytes(8,'big')+name+len(raw).to_bytes(8,'big')+raw
        expected=hashlib.sha256(payload).hexdigest()[:16];self.assertEqual(storage.compute_build_id(self.root),expected)
        for label in storage.BUILD_FILES:
            p=self.root/label;before=p.read_bytes();p.write_bytes(before+b'changed')
            self.assertNotEqual(storage.compute_build_id(self.root),expected);p.write_bytes(before)
        self.data['people'][0]['note']='changed';storage.write_atlas(self.path,self.data)
        self.assertNotEqual(storage.compute_build_id(self.root),expected)

if __name__=='__main__': unittest.main()
