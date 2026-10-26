from atlas_test_io import load_atlas
from atlas_storage import storage_inputs, compact_bytes
"""Live representation contract; historical pins and source fixtures stay immutable."""
import ast
import json
import math
from pathlib import Path
import unittest
from published_fixture import published_root
from test_current_release import reviewed_additions

ROOT = Path(__file__).resolve().parents[1]

def unique_pairs(items):
    result = {}
    for key, value in items:
        if key in result:
            raise ValueError('Duplicate JSON key: ' + key)
        result[key] = value
    return result

def reject_constant(value):
    raise ValueError('Non-finite JSON constant: ' + value)

def finite_values(value):
    if isinstance(value, dict):
        for item in value.values():
            finite_values(item)
    elif isinstance(value, list):
        for item in value:
            finite_values(item)
    elif isinstance(value, float) and not math.isfinite(value):
        raise ValueError('Non-finite JSON number')

def strict_loads(text):
    value = json.loads(text, object_pairs_hook=unique_pairs, parse_constant=reject_constant)
    finite_values(value)
    return value

def assert_typed_ordered(actual, expected, path='$'):
    assert type(actual) is type(expected), path + ': type changed'
    if isinstance(actual, dict):
        assert list(actual) == list(expected), path + ': object keys/order changed'
        for key in actual:
            assert_typed_ordered(actual[key], expected[key], path + '/' + key)
    elif isinstance(actual, list):
        assert len(actual) == len(expected), path + ': array length changed'
        for index, (left, right) in enumerate(zip(actual, expected)):
            assert_typed_ordered(left, right, path + '/' + str(index))
    elif isinstance(actual, float):
        assert actual.hex() == expected.hex(), path + ': float changed'
    else:
        assert actual == expected, path + ': scalar/code points changed'

def atlas_writer_options():
    module = ast.parse((ROOT / 'scripts/atlas_storage.py').read_text(encoding='utf-8'))
    tree = next(n for n in module.body if isinstance(n, ast.FunctionDef) and n.name == 'compact_bytes')
    calls = [node for node in ast.walk(tree) if isinstance(node, ast.Call)
             and isinstance(node.func, ast.Attribute) and node.func.attr == 'dumps'
             and isinstance(node.func.value, ast.Name) and node.func.value.id == 'json'
             and node.args and isinstance(node.args[0], ast.Name) and node.args[0].id == 'value']
    assert len(calls) == 1, 'Actual atlas serialization call must be unique'
    return {item.arg: ast.literal_eval(item.value) for item in calls[0].keywords}

def actual_writer_bytes(value):
    return compact_bytes(value)

class CompactJson(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.canonical = load_atlas(ROOT / 'data/atlas.json')
        cls.site = load_atlas(ROOT / 'site/atlas.json')

    def test_live_canonical_matches_independent_history_and_sources_including_types_and_order(self):
        expected = strict_loads((published_root() / 'data/atlas.json').read_text(encoding='utf-8'))
        additions = reviewed_additions()
        for key in ('people', 'org_units', 'profile_batches'):
            expected[key] += additions[key]
        assert_typed_ordered(self.canonical, expected)

    def test_both_live_atlases_use_exact_compact_utf8_with_one_terminal_lf(self):
        self.assertEqual(atlas_writer_options(), {'ensure_ascii': False, 'separators': (',', ':'), 'allow_nan': False})
        for path, raw in [(folder + '/' + label, raw) for folder in ('data', 'site')
                          for label, raw in storage_inputs(ROOT / folder / 'atlas.json')]:
            value = strict_loads(raw.decode('utf-8'))
            self.assertEqual(raw, actual_writer_bytes(value), path)
            self.assertEqual(raw.count(b'\n'), 1, path)
            self.assertTrue(raw.endswith(b'\n'), path)
            self.assertFalse(raw.startswith(b'\xef\xbb\xbf'), path)

    def test_site_has_only_derived_fields_beyond_identical_canonical_fields(self):
        self.assertEqual(list(self.site), list(self.canonical) + ['build_id', 'exports'])
        for key in self.canonical:
            assert_typed_ordered(self.site[key], self.canonical[key], key)
        self.assertEqual(len(self.site['build_id']), 16)

    def test_actual_writer_roundtrips_string_whitespace_unicode_and_json_types(self):
        sample = {'spaces': '  left  right\t\n\r  ', 'unicode': ['中文', 'é', 'e\u0301', '😀', '\u2028'],
                  'escaped': '"quoted" \\ slash /', 'values': [None, False, 0, True, 1, -0.0, 1.25],
                  'ordered': {'second': [2, 1], 'first': {'z': 0, 'a': False}}}
        raw = actual_writer_bytes(sample)
        assert_typed_ordered(strict_loads(raw.decode('utf-8')), sample)
        self.assertIn('中文'.encode('utf-8'), raw)
        self.assertEqual(raw.count(b'\n'), 1)

    def test_strict_reader_rejects_duplicate_keys_and_nonfinite_values(self):
        for value in ['{"a":1,"a":2}', '{"nested":{"x":0,"x":0}}', 'NaN', 'Infinity', '-Infinity', '1e999', '{"v":NaN}']:
            with self.subTest(value=value), self.assertRaises(ValueError):
                strict_loads(value)

    def test_actual_writer_rejects_nonfinite_numbers(self):
        for value in [float('nan'), float('inf'), -float('inf')]:
            with self.subTest(value=value), self.assertRaises(ValueError):
                actual_writer_bytes({'value': value})

    def test_typed_ordered_guard_rejects_semantic_and_order_mutations(self):
        pairs = [(False, 0), (1, 1.0), (-0.0, 0.0), ('é', 'e\u0301'),
                 ({'a': 1, 'b': 2}, {'b': 2, 'a': 1}), ([1, 2], [2, 1]),
                 (' x  y ', 'x y'), ({'a': []}, {'a': {}})]
        for actual, expected in pairs:
            with self.subTest(actual=actual, expected=expected), self.assertRaises(AssertionError):
                assert_typed_ordered(actual, expected)

if __name__ == '__main__':
    unittest.main()
