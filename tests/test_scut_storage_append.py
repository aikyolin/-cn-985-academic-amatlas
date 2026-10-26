"""First school-cohort append after chunk migration: actual physical and parsed IO."""
import hashlib
import json
from pathlib import Path
import sys
import unittest
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from atlas_storage import load_atlas
from test_current_release import reviewed_additions
from published_fixture import published_root

BASELINE_SHA256 = '99ed8cdc26a5a2a00525e8d38b956603de19ed666f8295aa5c56883fe69686cd'
BASELINE_COMMIT = 'ac3264cf35d7b1bf99077db170f50e027dd54847'

def assert_declared_school_chunk_changes(baseline_hashes, actual_hashes, post850_people):
    """Pure guard: only independently pinned post850 people authorize school changes."""
    assert set(actual_hashes) == set(baseline_hashes), 'Missing/unknown/extra school chunk path'
    schools = {path.split('/')[2][:-5] for path in baseline_hashes}
    assert all(path in {side + '/people/' + sid + '.json' for side in ('data', 'site') for sid in schools}
               for path in baseline_hashes), 'Invalid baseline chunk path'
    assert len(baseline_hashes) == 2 * len(schools), 'Incomplete baseline school pair'
    allowed = {person['school_id'] for person in post850_people}
    assert allowed <= schools, 'Declared school not in fixed baseline school set'
    for sid in schools:
        paths = [side + '/people/' + sid + '.json' for side in ('data', 'site')]
        assert actual_hashes[paths[0]] == actual_hashes[paths[1]], 'Canonical/site people bytes differ'
        for path in paths:
            if sid in allowed:
                assert actual_hashes[path] != baseline_hashes[path], 'Declared school chunk did not change'
            else:
                assert actual_hashes[path] == baseline_hashes[path], 'Undeclared school chunk changed: ' + path
    return allowed


class ScutStorageAppend(unittest.TestCase):
    def test_only_independently_declared_post850_school_bytes_can_change(self):
        raw = (ROOT / 'tests/fixtures/independent-scut11-storage-baseline.json').read_bytes()
        self.assertEqual(hashlib.sha256(raw).hexdigest(), BASELINE_SHA256)
        baseline = json.loads(raw)
        self.assertEqual(baseline['baseline_commit'], BASELINE_COMMIT)
        self.assertEqual(baseline['baseline_profiles'], 850)
        self.assertEqual(len(baseline['unchanged_school_chunks']), 76)
        baseline_hashes = {**baseline['unchanged_school_chunks'], **baseline['target_school_chunks_before']}
        self.assertEqual(len(baseline_hashes), 78)
        # This boundary is derived from immutable published612 and pinned additions,
        # never from live people, live changed hashes or current manifest schools.
        published = json.loads((published_root() / 'data/atlas.json').read_bytes())
        self.assertEqual(len(published['people']), 612)
        offset = 850 - len(published['people'])
        additions = reviewed_additions()['people']
        self.assertGreaterEqual(len(additions), offset)
        post850_people = additions[offset:]
        canonical = load_atlas(ROOT / 'data/atlas.json')
        site = load_atlas(ROOT / 'site/atlas.json')
        self.assertEqual(len(canonical['people']), 850 + len(post850_people))
        self.assertEqual(site['people'], canonical['people'])
        actual_hashes = {}
        for side in ('data', 'site'):
            manifest = json.loads((ROOT / side / 'atlas.json').read_bytes())
            expected_paths = {p[len(side)+1:] for p in baseline_hashes if p.startswith(side+'/')}
            self.assertEqual({p['path'] for p in manifest['parts']}, expected_paths)
            self.assertEqual(len(manifest['parts']), 39)
            for part in manifest['parts']:
                rel = side + '/' + part['path']
                digest = hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()
                self.assertEqual(part['sha256'], digest)
                actual_hashes[rel] = digest
        assert_declared_school_chunk_changes(baseline_hashes, actual_hashes, post850_people)

    def test_unlisted_school_hash_and_unknown_paths_are_rejected(self):
        baseline = {side + '/people/' + sid + '.json': ('a' if sid == 'declared' else 'b') * 64
                    for side in ('data', 'site') for sid in ('declared', 'untouched')}
        actual = dict(baseline)
        for side in ('data', 'site'):
            actual[side + '/people/declared.json'] = 'c' * 64
        declared = [{'person_id': 'synthetic-new', 'school_id': 'declared'}]
        self.assertEqual(assert_declared_school_chunk_changes(baseline, actual, declared), {'declared'})
        # Even a perfectly matching data/site mutation of an undeclared school fails.
        mutant = dict(actual)
        for side in ('data', 'site'):
            mutant[side + '/people/untouched.json'] = 'd' * 64
        with self.assertRaisesRegex(AssertionError, 'Undeclared'):
            assert_declared_school_chunk_changes(baseline, mutant, declared)
        mutant = dict(actual); mutant['data/people/untouched.json'] = 'd' * 64
        with self.assertRaises(AssertionError):
            assert_declared_school_chunk_changes(baseline, mutant, declared)
        mutant = dict(actual); mutant['data/people/extra.json'] = 'e' * 64
        with self.assertRaisesRegex(AssertionError, 'Missing/unknown/extra'):
            assert_declared_school_chunk_changes(baseline, mutant, declared)
        mutant = dict(actual); del mutant['site/people/untouched.json']
        with self.assertRaisesRegex(AssertionError, 'Missing/unknown/extra'):
            assert_declared_school_chunk_changes(baseline, mutant, declared)
        with self.assertRaisesRegex(AssertionError, 'Undeclared'):
            assert_declared_school_chunk_changes(baseline, actual, [])

if __name__ == '__main__': unittest.main()
