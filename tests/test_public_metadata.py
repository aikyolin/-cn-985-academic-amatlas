"""All negative examples here are synthetic code values, not real-source fixtures."""
import copy
import csv
import json
import pathlib
import sys
import tempfile
import unittest
from unittest.mock import patch
from zipfile import ZipFile

from openpyxl import Workbook

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / 'scripts'))
import build
from public_metadata import metadata_errors, publication_files, tree_errors, check_public_tree


class PublicMetadataTests(unittest.TestCase):
    files = frozenset({'data/atlas.json', 'research/public-review.json',
                       'site/exports/example.xlsx', 'docs/evidence.md'})

    def errors(self, value, source='data/atlas.json'):
        return metadata_errors(value, source=source, public_files=self.files)

    def test_preserves_real_locator_types_and_audit_scope(self):
        value = {
            'source_id': 'example-profile', 'education_event_id': 'example-phd',
            'source_ids': ['example-profile', 'example-thesis'],
            'field_provenance': {'official_url': 'example-profile'},
            'professional_field_provenance': {'official_url': ['example-profile']},
            'field_status': {'official_url': 'source_reported'},
            'source_url': 'https://example.test/thesis.pdf#page=5',
            'official_profile_url': ' https://example.test/profile ',
            'file': 'research/public-review.json', 'path': '/education/0/event_kind',
            'preserved_at': '/education/0/source_event_kind',
            'pointer': '/a~1b/~0escaped key',
            'source_locator': 'PDF page 5; printed page iv; Acknowledgements',
            'evidence_locator': '第5页，教育经历章节',
            'cell_range': 'L1:L30', 'coordinate': "'来源'!$A$1:$L$30",
            'source_snapshots': [{'sha256': 'a' * 64, 'hash_scope': 'reviewed package audit integrity, not source bytes'}],
            'tool_response_sha256': 'b' * 64,
            'cache_kind': 'serialized_web_tool_response_not_original_page_or_pdf_bytes',
            'public_raw_cache': False, 'file_count': 30, 'report': 2,
            'command': 'python scripts/build.py --data-only',
        }
        before = copy.deepcopy(value)
        self.assertEqual(self.errors(value), [])
        self.assertEqual(value, before)

    def test_public_paths_resolve_only_in_explicit_inventory(self):
        self.assertEqual(self.errors({'file': '../research/public-review.json'}), [])
        self.assertEqual(self.errors({'file': 'exports/example.xlsx'}), [])
        self.assertEqual(self.errors({'research/public-review.json': 'a' * 64}), [])
        for value in ['missing-review.json', 'private/review.json', '../../outside.json',
                      'site/../../../outside.json', '%2e%2e/%2e%2e/outside.json']:
            with self.subTest(value=value):
                self.assertTrue(self.errors({'evidence_file': value}))
        self.assertTrue(self.errors({'artifact_id': 'renamed-private-review.json'}))
        self.assertTrue(self.errors({'missing-review.json': 'a' * 64}))
        self.assertTrue(self.errors({'serialized': json.dumps({'evidence_file': 'private-review.json'})}))

    def test_prose_with_public_urls_is_not_a_relative_filename(self):
        value = '官方职业报道（非个人主页）：https://example.test/profile.html'
        self.assertEqual(self.errors({'note': value}), [])
        self.assertEqual(self.errors(value), [])
        self.assertEqual(self.errors({'properties': {'source_file': {'type': 'string', 'description': 'Public repository file.'}}}, 'schema/example.schema.json'), [])

    def test_private_tokens_are_rejected_in_nested_keys_and_values(self):
        cases = [
            {'sources': [{'web_reference': 'turn123view4'}]},
            {'note': 'Read failed (turn123search4); no bypass.'},
            {'note': 'turn123%76iew4'},
            {'turn123view4': 'synthetic'},
            {'note': '/workspace/synthetic-private/evidence.json'},
            {'file': '/home/example/evidence.json'},
            {'file': r'C:\Users\Example\evidence.json'},
            {'file': r'\\computer\private\evidence.json'},
            {'file': 'file:///tmp/synthetic.json'},
            {'note': 'file%3A%2F%2F%2Ftmp%2Fsynthetic.json'},
            {'source_locator': 'private://evidence/1'},
        ]
        for value in cases:
            with self.subTest(value=value):
                errors = self.errors(value)
                self.assertTrue(errors)
                self.assertTrue(all(e.startswith('data/atlas.json#/') for e in errors))

    def test_relative_evidence_urls_cannot_be_laundered_as_public_files(self):
        for value in ['research/public-review.json', '../research/public-review.json',
                      'review.json', 'https://', 'https://exa mple.test/evidence']:
            with self.subTest(value=value):
                self.assertTrue(self.errors({'source_url': value}))
        self.assertEqual(self.errors({'source_id': 'example-profile', 'event_id': 'example-phd'}), [])

    def test_tool_lines_are_not_pdf_pages_or_excel_columns(self):
        for key in ['source_locator', 'source_location', 'location', 'evidence_note', 'access_note']:
            self.assertTrue(self.errors({key: 'PDF page 5; L671, L673–L682'}))
        self.assertTrue(self.errors({'source_locators': ['L42-L54: identity']}))
        self.assertEqual(self.errors({'range': 'L1:L30', 'cell': 'L42', 'source_id': 'L42'}), [])
        self.assertEqual(self.errors({'source_locator': 'PDF page 5; Chapter 2; 第3行'}), [])
        self.assertEqual(self.errors({'source_locator': 'https://example.test/public/L42#L45'}), [])

    def test_synthetic_export_exception_cannot_hide_evidence_or_real_fixtures(self):
        value = {'exports': [{'path': 'exports/hit-test-computing.xlsx'}]}
        self.assertEqual(self.errors(value, 'tests/fixtures/multischool.json'), [])
        self.assertTrue(self.errors(value, 'tests/fixtures/real-source-contract.json'))
        value['fixture_notice'] = 'SYNTHETIC TEST DATA ONLY'
        self.assertTrue(self.errors(value, 'tests/fixtures/spoof.json'))
        value['sources'] = [{'evidence_file': 'exports/hit-test-computing.xlsx'}]
        self.assertTrue(self.errors(value, 'tests/fixtures/multischool.json'))
        value['exports'][0]['path'] = '/tmp/synthetic.xlsx'
        self.assertTrue(self.errors(value, 'tests/fixtures/multischool.json'))


class PublicTreeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = pathlib.Path(self.temp.name)
        self.addCleanup(self.temp.cleanup)
        self.write('data/atlas.json', '{}')

    def write(self, name, text):
        target = self.root / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text)
        return target

    def test_preflight_does_not_read_stale_site_but_final_does(self):
        site = self.write('site/atlas.json', '{"note":"turn123view4"}')
        self.assertEqual(tree_errors(self.root, phase='preflight'), [])
        self.assertTrue(tree_errors(self.root, phase='final'))
        site.write_text('{}')
        self.assertTrue(check_public_tree(self.root, phase='final'))

    def test_build_checks_inputs_before_writing_any_output(self):
        self.write('data/atlas.json', '{"note":"turn123view4"}')
        with patch.object(build, 'ROOT', self.root):
            with self.assertRaisesRegex(ValueError, 'private tool reference'):
                build.build(generate_excel=False)
        self.assertFalse((self.root / 'site').exists())

    def test_real_fixture_is_not_exempt_and_code_negatives_are_not_grepped(self):
        self.write('tests/test_synthetic.py', "negative = 'turn123view4'\n")
        self.assertEqual(tree_errors(self.root, phase='preflight'), [])
        self.write('tests/fixtures/real-source.json', '{"original":{"source_locator":"L42"}}')
        self.assertTrue(tree_errors(self.root, phase='preflight'))

    def test_file_outside_publication_set_does_not_count_even_if_it_exists(self):
        self.write('private/synthetic.json', '{}')
        self.write('data/atlas.json', '{"evidence_file":"private/synthetic.json"}')
        with self.assertRaisesRegex(ValueError, 'outside the reviewed publication boundary'):
            tree_errors(self.root, phase='preflight')

    def test_unknown_root_json_fails_closed(self):
        self.write('root_extra.json', '{"note":"turn123view4"}')
        for phase in ['preflight', 'final']:
            with self.subTest(phase=phase):
                with self.assertRaisesRegex(ValueError, 'root_extra.json: outside the reviewed publication boundary'):
                    tree_errors(self.root, phase=phase)

    def test_unknown_directory_fails_closed_but_caches_remain_excluded(self):
        for directory in ['.git', '__pycache__', 'node_modules', '.pytest_cache']:
            self.write(directory + '/synthetic.json', '{"note":"turn123view4"}')
        self.assertEqual(tree_errors(self.root, phase='final'), [])
        self.write('new_public_area/extra.json', '{"note":"turn123view4"}')
        for phase in ['preflight', 'final']:
            with self.subTest(phase=phase):
                with self.assertRaisesRegex(ValueError, 'outside the reviewed publication boundary'):
                    tree_errors(self.root, phase=phase)

    def test_publication_symlink_rejected(self):
        target = self.root / 'data' / 'atlas.json'
        (self.root / 'data' / 'linked.json').symlink_to(target)
        with self.assertRaisesRegex(ValueError, 'symlinks'):
            publication_files(self.root)

    def test_documents_and_csv_use_the_same_rules(self):
        self.write('docs/example.md', '[bad](private-review.json)')
        self.assertTrue(tree_errors(self.root, phase='final'))
        self.write('docs/example.md', '[atlas](../data/atlas.json)')
        csv_path = self.root / 'site' / 'exports' / 'example.csv'
        csv_path.parent.mkdir(parents=True)
        with csv_path.open('w', newline='') as handle:
            writer = csv.writer(handle)
            writer.writerow(['identity_evidence'])
            writer.writerow([json.dumps({'evidence_file': 'private-review.json'})])
        self.assertTrue(any('example.csv' in e for e in tree_errors(self.root, phase='final')))

    def test_xlsx_json_cells_are_checked_without_rewriting_zip(self):
        path = self.root / 'site' / 'exports' / 'example.xlsx'
        path.parent.mkdir(parents=True)
        workbook = Workbook()
        workbook.active.append(['identity_evidence'])
        workbook.active.append([json.dumps({'source_locator': 'L42', 'evidence_file': 'private-review.json'})])
        workbook.save(path)
        before = path.read_bytes()
        self.assertEqual(tree_errors(self.root, phase='preflight'), [])
        self.assertEqual(tree_errors(self.root, phase='final', include_workbooks=False), [])
        errors = tree_errors(self.root, phase='final')
        self.assertTrue(any('tool line number' in e for e in errors))
        self.assertTrue(any('non-public repository' in e for e in errors))
        self.assertEqual(path.read_bytes(), before)

    def test_xlsx_rich_text_cannot_split_a_private_tool_token(self):
        path = self.root / 'site' / 'exports' / 'example.xlsx'
        path.parent.mkdir(parents=True)
        with ZipFile(path, 'w') as archive:
            archive.writestr('xl/sharedStrings.xml', '<sst xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><si><r><t>turn123</t></r><r><t>view4</t></r></si></sst>')
        self.assertTrue(any('private tool reference' in e for e in tree_errors(self.root, phase='final')))

    def test_xlsx_locator_column_has_semantics_but_a1_range_does_not(self):
        path = self.root / 'site' / 'exports' / 'example.xlsx'
        path.parent.mkdir(parents=True)
        workbook = Workbook()
        workbook.active.append(['source_locator', 'range'])
        workbook.active.append(['L42', 'L1:L30'])
        workbook.save(path)
        errors = tree_errors(self.root, phase='final')
        self.assertEqual(len(errors), 1)
        self.assertIn('tool line number', errors[0])


if __name__ == '__main__':
    unittest.main()
