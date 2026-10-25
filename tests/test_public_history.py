"""Public-v1 historical pins preserve every remaining leaf and reject tampering."""
from published_fixture import published_root
import ast
import copy
import hashlib
import importlib
import json
import pathlib
import unittest
from public_history import public_contract

ROOT = pathlib.Path(__file__).resolve().parents[1]

def load(release):
    module = importlib.import_module('release_history' if release == 25 else f'release{release}_history')
    return module.CONTRACT, getattr(module, f'release{release}_view')

class PublicHistoryContracts(unittest.TestCase):
    def test_all_six_versions_reconstruct_exact_public_historical_bytes(self):
        for release in range(25, 31):
            contract, view = load(release)
            for rel, rule in contract.items():
                with self.subTest(release=release, file=rel):
                    value = json.loads(((published_root() if rel == 'site/atlas.json' else ROOT) / rel).read_text())
                    historical = view(value, rel)
                    raw = (json.dumps(historical, ensure_ascii=False, indent=2) + '\n').encode()
                    self.assertEqual(hashlib.sha256(raw).hexdigest(), rule['byte_sha256'])

    def test_historical_public_view_rejects_fact_source_and_shape_mutations(self):
        rel = 'data/atlas.json'
        raw = json.loads((ROOT / rel).read_text())
        _, view = load(25)
        def person(value): return value['people'][0]
        def source(value): return person(value)['sources'][0]
        def education(value): return next(p for p in value['people'] if p['education'])['education'][0]
        mutations = {
            'name': lambda v: person(v).__setitem__('name', 'synthetic changed name'),
            'source_url': lambda v: source(v).__setitem__('url', 'https://example.invalid/changed'),
            'source_id': lambda v: source(v).__setitem__('id', 'synthetic-changed-source'),
            'award_tristate': lambda v: education(v).__setitem__('degree_awarded', 'synthetic-invalid-state'),
            'extra_root_sibling': lambda v: v.__setitem__('unexpected_sibling', []),
            'extra_source_sibling': lambda v: source(v).__setitem__('unexpected_sibling', 'synthetic'),
            'removed_retained_metadata': lambda v: source(v).pop('retrieved_at'),
            'changed_historical_order': lambda v: v['people'].__setitem__(slice(0, 2), list(reversed(v['people'][:2]))),
            'removed_historical_record': lambda v: v['people'].pop(0),
            'frozen_metadata': lambda v: v.__setitem__('updated_at', '2099-01-01'),
        }
        for name, change in mutations.items():
            with self.subTest(mutation=name):
                changed = copy.deepcopy(raw)
                change(changed)
                with self.assertRaises(AssertionError): view(changed, rel)
        # An audit fingerprint remains a required value, never a public-source URL.
        changed = copy.deepcopy(raw)
        target = next(s for p in changed['people'][:555] for s in p['sources'] if 'body_sha256' in s)
        target['body_sha256'] = '0' * 64
        with self.assertRaises(AssertionError): view(changed, rel)

    def test_fingerprint_migrations_and_retained_scalar_coverage_are_pinned(self):
        raw = (ROOT / 'tests/fixtures/public-fingerprint-migrations-v1.json').read_bytes()
        self.assertEqual(hashlib.sha256(raw).hexdigest(), 'e46c052da2262098a04695af1f25492558ab9949175da78cfa07c9ff594b9522')
        migration = json.loads(raw)
        self.assertEqual(migration['version'], 'public_metadata_v1')
        seen = set()
        for row in migration['fingerprint_migrations']:
            key = (row['file'], row['original_sha256'], row['public_sha256'])
            self.assertNotIn(key, seen)
            seen.add(key)
            self.assertNotEqual(row['original_sha256'], row['public_sha256'])
            self.assertIn(row['public_sha256'], (ROOT / row['file']).read_text())
        for row in migration['source_shape_migrations']:
            module = ast.parse((ROOT / row['file']).read_text())
            assignment = next(n for n in module.body if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'SOURCE_SHAPES' for t in n.targets))
            shape = ast.literal_eval(assignment.value)[row['node']]
            self.assertNotIn(row['removed_key'], [key for key, _ in shape[1]])
            digest = hashlib.sha256(json.dumps(shape, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
            self.assertEqual(digest, row['public_shape_sha256'])
        self.assertEqual(sum(row['approved_removed_locator_count'] for row in migration['source_scalar_coverage']), 27)
        self.assertEqual(sum(row['public_scalar_count'] for row in migration['source_scalar_coverage']), 4360)
        for row in migration['source_scalar_coverage']:
            self.assertEqual(row['original_scalar_count'], row['public_scalar_count'] + row['approved_removed_locator_count'])

    def test_original_fixture_and_public_mapping_byte_tampering_are_rejected(self):
        original = (ROOT / 'tests/fixtures/release25-history.json').read_bytes()
        mapping = (ROOT / 'tests/fixtures/public-history-v1.json').read_bytes()
        with self.assertRaises(AssertionError): public_contract(25, original + b' ')
        with self.assertRaises(AssertionError): public_contract(25, original, mapping + b' ')
        altered = json.loads(mapping)
        pair = altered['releases']['25']['files']['data/atlas.json']['lists']['people']
        pair['public_sha256'] = '0' * 64
        with self.assertRaises(AssertionError): public_contract(25, original, json.dumps(altered).encode())

if __name__ == '__main__': unittest.main()
