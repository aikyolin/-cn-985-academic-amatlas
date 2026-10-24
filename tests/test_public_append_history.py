from source_date_history import historical_root
"""Generic append conservation and independent synthetic endpoint negatives."""
import copy
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

import public_append_history as history

ROOT = Path(__file__).resolve().parents[1]


def encoded(value):
    return (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode()


def synthetic_case():
    """Only explicit synthetic bytes, never candidate-derived expectations."""
    old = {
        'data/atlas.json': b'old atlas\n',
        'site/exports/old-department.xlsx': b'old workbook\n',
        'site/exports/待核对名录.xlsx': b'old roster workbook\n',
        'tests/test_old.py': b'old test\n',
    }
    current = dict(old)
    current.update({'data/atlas.json': b'new atlas\n',
                    'site/exports/待核对名录.xlsx': b'new roster workbook\n',
                    'site/exports/new-department.xlsx': b'new workbook\n',
                    'progress/synthetic-coverage.json': b'{"synthetic":true}\n',
                    'tests/test_old.py': b'reviewed IO seam\n',
                    'tests/helper.py': b'reviewed helper\n'})
    baseline = {'source_commit': 'synthetic-immutable-anchor'}
    inventory = {'source_commit': baseline['source_commit'], 'files': {
        name: {'bytes': len(raw), 'sha256': history.sha256(raw)} for name, raw in old.items()}}
    reviewed_scope = {
        'source_contract': {'path': 'tests/fixtures/synthetic-source.json', 'sha256': history.sha256(b'synthetic reviewed source\n')},
        'audit_digests': {'source_input_sha256': history.sha256(b'synthetic reviewed input\n'),
                          'review_result_sha256': history.sha256(b'synthetic independent review\n')},
        'added_output_paths': ['site/exports/new-department.xlsx', 'progress/synthetic-coverage.json'],
    }
    manifest = {
        'version': 'public_append_manifest_v1',
        'baseline_fixture_sha256': history.BASELINE_FIXTURE_SHA256,
        'baseline_inventory_sha256': history.INVENTORY_FIXTURE_SHA256,
        'baseline_commit': baseline['source_commit'],
        'source_contract': copy.deepcopy(reviewed_scope['source_contract']),
        'audit_digests': copy.deepcopy(reviewed_scope['audit_digests']),
        'changed_existing': {
            name: {'before_sha256': history.sha256(old[name]), 'after_sha256': history.sha256(current[name]), 'byte_length': len(current[name])}
            for name in ('data/atlas.json', 'site/exports/待核对名录.xlsx')},
        'deleted_existing': [],
        'allowed_added_outputs': {
            name: {'sha256': history.sha256(current[name]), 'byte_length': len(current[name])}
            for name in reviewed_scope['added_output_paths']},
        'implementation_added_files': ['tests/helper.py'],
        'implementation_modified_files': {'tests/test_old.py': {'before_sha256': history.sha256(old['tests/test_old.py'])}},
    }
    options = dict(baseline=baseline, inventory=inventory, reviewed_scope=reviewed_scope,
                   implementation_added_files={'tests/helper.py'}, implementation_modified_files={'tests/test_old.py'})
    return manifest, options, current


class PublicAppendPrefix(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.baseline = history.load_baseline()
        cls.documents = {rel: history.public_append_view(json.loads((ROOT / rel).read_bytes()), rel)
                         for rel in cls.baseline['files']}

    def test_all_five_frozen_objects_and_exact_bytes_round_trip(self):
        for rel, document in self.documents.items():
            with self.subTest(rel=rel):
                raw = history.public_append_bytes(document, rel)
                self.assertEqual(len(raw), self.baseline['files'][rel]['byte_length'])
                self.assertEqual(history.sha256(raw), self.baseline['files'][rel]['byte_sha256'])

    def test_baseline_is_a_pinned_clean_public_fixture(self):
        self.assertEqual(history.sha256((ROOT / history.BASELINE_PATH).read_bytes()), history.BASELINE_FIXTURE_SHA256)
        self.assertEqual(history.load_inventory()['source_commit'], self.baseline['source_commit'])
        with self.assertRaises(ValueError):
            history.pinned_json((ROOT / history.BASELINE_PATH).read_bytes() + b' ', history.BASELINE_FIXTURE_SHA256)

    def test_real_baseline_append_and_mutable_metadata_restore_old_bytes(self):
        document = copy.deepcopy(self.documents['data/atlas.json'])
        document['people'].append({'person_id': 'synthetic-new-person'})
        document['scope_note'] = 'Synthetic append scope, not a factual record.'
        self.assertEqual(history.public_append_view(document, 'data/atlas.json'), self.documents['data/atlas.json'])
        self.assertEqual(document['people'][-1]['person_id'], 'synthetic-new-person')

    def test_exports_allow_new_identity_between_frozen_rows_but_never_sort_old_rows(self):
        document = copy.deepcopy(self.documents['site/atlas.json'])
        document['exports'].insert(1, {'department_id': 'synthetic-new-department'})
        self.assertEqual(history.public_append_view(document, 'site/atlas.json'), self.documents['site/atlas.json'])
        document['exports'][0], document['exports'][2] = document['exports'][2], document['exports'][0]
        with self.assertRaises(ValueError):
            history.public_append_view(document, 'site/atlas.json')

    def test_unknown_path_root_and_historical_sibling_fields_are_rejected(self):
        with self.assertRaises(ValueError):
            history.public_append_view({}, 'unknown.json')
        for mutate in (lambda d: d.update(unknown_sibling=True),
                       lambda d: d.pop('coverage'),
                       lambda d: d['people'][0].update(unknown_sibling=True),
                       lambda d: d['people'][0]['sources'][0].update(unknown_sibling=True)):
            document = copy.deepcopy(self.documents['data/atlas.json']); mutate(document)
            with self.assertRaises(ValueError):
                history.public_append_view(document, 'data/atlas.json')

    def test_history_values_order_length_source_and_award_are_frozen(self):
        def source_change(d):
            d['people'][0]['sources'][0]['url'] = 'https://example.org/changed'
        def source_missing_date(d):
            d['people'][0]['sources'][0].pop('retrieved_at')
        def award_change(d):
            d['people'][0]['education'][0]['degree_awarded'] = False
        def order_change(d):
            d['people'][0], d['people'][1] = d['people'][1], d['people'][0]
        def key_order_change(d):
            row = d['people'][0]; key = next(iter(row)); row[key] = row.pop(key)
        for mutate in (source_change, source_missing_date, award_change, order_change, key_order_change,
                       lambda d: d['people'].pop(),
                       lambda d: d['people'].append(copy.deepcopy(d['people'][0])),
                       lambda d: d.update(updated_at='2099-01-01'),
                       lambda d: d.update(people={})):
            document = copy.deepcopy(self.documents['data/atlas.json']); mutate(document)
            with self.subTest(mutation=mutate.__name__), self.assertRaises(ValueError):
                history.public_append_view(document, 'data/atlas.json')

    def test_metadata_whitelist_rejects_unknown_siblings_and_type_changes(self):
        for mutate in (lambda d: d['totals'].update(unreviewed=True),
                       lambda d: d['totals'].update(record_count=True),
                       lambda d: d.update(scope={'unexpected': 'object'})):
            document = copy.deepcopy(self.documents['data/rosters.json']); mutate(document)
            with self.assertRaises(ValueError):
                history.public_append_view(document, 'data/rosters.json')

    def test_export_duplicate_missing_or_modified_frozen_descriptor_fails(self):
        for mutate in (lambda rows: rows.pop(), lambda rows: rows.append(copy.deepcopy(rows[0])),
                       lambda rows: rows[0].update(people_count=999),
                       lambda rows: rows[0].update(unreviewed=True)):
            document = copy.deepcopy(self.documents['site/atlas.json']); mutate(document['exports'])
            with self.assertRaises(ValueError):
                history.public_append_view(document, 'site/atlas.json')

    def test_independent_suffix_contract_rejects_extra_person_export_and_hold_promotion(self):
        # Explicitly reviewed synthetic empty append, not computed from live suffixes.
        scope = {'file_suffixes': {rel: {key: {'length': 0, 'sha256': '4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945'}
                                                  for key in spec['lists']}
                                   for rel, spec in self.baseline['files'].items()},
                 'approved_department_ids': [], 'held_school_ids': ['synthetic-held']}
        history.validate_reviewed_suffixes(self.documents, scope)
        for rel, key, value in [('data/atlas.json', 'people', {'person_id': 'synthetic-new', 'school_id': 'synthetic-held'}),
                                ('site/atlas.json', 'exports', {'department_id': 'synthetic-extra'})]:
            documents = copy.deepcopy(self.documents); documents[rel][key].append(value)
            with self.assertRaises(ValueError):
                history.validate_reviewed_suffixes(documents, scope)

    def test_even_matching_synthetic_suffix_hashes_cannot_promote_a_held_school(self):
        documents = copy.deepcopy(self.documents)
        person = {'person_id': 'synthetic-held-person', 'school_id': 'synthetic-held',
                  'department_id': 'synthetic-new-department'}
        org = {'id': 'synthetic-new-department', 'school_id': 'synthetic-held'}
        export = {'department_id': 'synthetic-new-department'}
        additions = {rel: {key: [] for key in spec['lists']} for rel, spec in self.baseline['files'].items()}
        for rel in ('data/atlas.json', 'site/atlas.json'):
            additions[rel]['people'] = [person]
            additions[rel]['org_units'] = [org]
            documents[rel]['people'].append(copy.deepcopy(person))
            documents[rel]['org_units'].append(copy.deepcopy(org))
        additions['site/atlas.json']['exports'] = [export]
        documents['site/atlas.json']['exports'].append(export)
        scope = {'file_suffixes': {rel: {key: {'length': len(rows), 'sha256': history.canonical_digest(rows)}
                                         for key, rows in lists.items()} for rel, lists in additions.items()},
                 'approved_department_ids': ['synthetic-new-department'], 'held_school_ids': ['synthetic-held']}
        with self.assertRaisesRegex(ValueError, 'held school promoted'):
            history.validate_reviewed_suffixes(documents, scope)

    def test_old_workbook_map_is_exact_not_subset(self):
        frozen = {name: item['sha256'] for name, item in history.load_inventory()['files'].items()
                  if name.startswith('site/exports/') and name.endswith('.xlsx')}
        self.assertEqual(len(frozen), 132)
        expected = dict(frozen)
        manifest = history.load_current_append_manifest()
        if manifest:
            for rel, item in manifest['changed_existing'].items():
                if rel in expected: expected[rel] = item['after_sha256']
            expected.update({rel: item['sha256'] for rel, item in manifest['allowed_added_outputs'].items()
                             if rel.startswith('site/exports/') and rel.endswith('.xlsx')})
        self.assertEqual(history.workbook_endpoints(frozen), expected)
        for bad in (dict(frozen, **{'site/exports/extra.xlsx': '0' * 64}), dict(list(frozen.items())[1:])):
            with self.assertRaises(ValueError):
                history.workbook_endpoints(bad)


class SyntheticEndpointContract(unittest.TestCase):
    def setUp(self):
        self.manifest, self.options, self.files = synthetic_case()
        self.raw = encoded(self.manifest)
        # Static synthetic golden pin. It is not a production append-manifest pin.
        self.pin = '22a4924322aac83e40631744347324767bb6e5a46549706a41c7acd01319aee0'

    def parse(self, manifest=None):
        if manifest is None:
            raw, pin = self.raw, self.pin
        else:
            # Re-pin only a synthetic schema mutant, to test the second defense.
            raw = encoded(manifest); pin = history.sha256(raw)
        return history.validate_append_manifest(raw, pin, **self.options)

    def test_static_synthetic_manifest_and_exact_tree(self):
        manifest = self.parse()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for rel, raw in self.files.items():
                path = root / rel; path.parent.mkdir(parents=True, exist_ok=True); path.write_bytes(raw)
            self.assertEqual(set(history.validate_tree(root, manifest, self.options['inventory'])), set(self.files))

    def test_byte_pin_rejects_whitespace_and_digest_mutation(self):
        for raw in (self.raw + b' ', self.raw.replace(b'new-department', b'bad-department')):
            with self.assertRaises(ValueError):
                history.validate_append_manifest(raw, self.pin, **self.options)
        for pin in (None, '0' * 64):
            with self.assertRaises(ValueError):
                history.validate_append_manifest(self.raw, pin, **self.options)

    def test_manifest_unknown_fields_pin_anchor_source_review_and_deletion_fail(self):
        cases = []
        for key, value in [('unknown', True), ('baseline_fixture_sha256', '0' * 64),
                           ('baseline_inventory_sha256', '0' * 64), ('baseline_commit', 'different'),
                           ('deleted_existing', ['data/atlas.json'])]:
            mutant = copy.deepcopy(self.manifest); mutant[key] = value; cases.append(mutant)
        mutant = copy.deepcopy(self.manifest); mutant['source_contract']['sha256'] = '0' * 64; cases.append(mutant)
        mutant = copy.deepcopy(self.manifest); mutant['audit_digests']['review_result_sha256'] = '0' * 64; cases.append(mutant)
        for mutant in cases:
            with self.assertRaises(ValueError): self.parse(mutant)

    def test_existing_department_workbook_cannot_enter_change_allowlist(self):
        mutant = copy.deepcopy(self.manifest)
        mutant['changed_existing']['site/exports/old-department.xlsx'] = {
            'before_sha256': history.sha256(b'old workbook\n'), 'after_sha256': history.sha256(b'changed workbook\n'), 'byte_length': 17}
        with self.assertRaises(ValueError): self.parse(mutant)

    def test_unknown_added_export_and_implementation_expansion_fail(self):
        for key in ('allowed_added_outputs', 'implementation_modified_files'):
            mutant = copy.deepcopy(self.manifest)
            mutant[key]['site/exports/extra.xlsx'] = {'sha256': '0' * 64, 'byte_length': 0}
            with self.assertRaises(ValueError): self.parse(mutant)
        mutant = copy.deepcopy(self.manifest); mutant['implementation_added_files'].append('tests/unreviewed.py')
        with self.assertRaises(ValueError): self.parse(mutant)

    def test_before_hash_endpoint_shape_and_unchanged_claim_fail(self):
        for mutate in (lambda item: item.update(before_sha256='0' * 64),
                       lambda item: item.update(after_sha256=item['before_sha256']),
                       lambda item: item.update(byte_length=True),
                       lambda item: item.update(extra=True)):
            mutant = copy.deepcopy(self.manifest); mutate(mutant['changed_existing']['data/atlas.json'])
            with self.assertRaises(ValueError): self.parse(mutant)

    def test_exact_tree_rejects_extra_missing_and_single_byte_workbook_changes(self):
        manifest = self.parse()
        changes = [lambda root: (root / 'site/exports/extra.xlsx').write_bytes(b'extra'),
                   lambda root: (root / 'site/exports/old-department.xlsx').unlink(),
                   lambda root: (root / 'site/exports/old-department.xlsx').write_bytes(b'Old workbook\n'),
                   lambda root: (root / 'data/atlas.json').write_bytes(b'wrong endpoint\n'),
                   lambda root: (root / 'extra.txt').write_bytes(b'extra'),
                   lambda root: (root / 'alias').symlink_to('data/atlas.json')]
        for change in changes:
            with tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                for rel, raw in self.files.items():
                    path = root / rel; path.parent.mkdir(parents=True, exist_ok=True); path.write_bytes(raw)
                change(root)
                with self.assertRaises(ValueError): history.validate_tree(root, manifest, self.options['inventory'])

    def test_canonical_domain_is_shared_and_never_collapses_bool_null_and_int(self):
        value = {'𐀀': '中文', '\ue000': [None, False, True, 0], '10': 10, '2': 2}
        script = "import {canonicalDigest} from './tests/public-append-history.js'; console.log(canonicalDigest(JSON.parse(process.argv[1])));"
        result = subprocess.run(['node', '--input-type=module', '-e', script, json.dumps(value, ensure_ascii=False)],
                                cwd=ROOT, check=True, text=True, capture_output=True)
        self.assertEqual(result.stdout.strip(), history.canonical_digest(value))
        for value in (1.5, 9007199254740992, float('nan')):
            with self.assertRaises(ValueError): history.canonical_digest(value)

    def test_python_javascript_static_pins_and_parsed_baseline_are_identical(self):
        script = "import * as h from './tests/public-append-history.js'; console.log(JSON.stringify([h.BASELINE_FIXTURE_SHA256,h.INVENTORY_FIXTURE_SHA256,h.APPEND_MANIFEST_SHA256,h.loadBaseline()]));"
        result = subprocess.run(['node', '--input-type=module', '-e', script], cwd=ROOT,
                                check=True, text=True, capture_output=True)
        self.assertEqual(json.loads(result.stdout), [history.BASELINE_FIXTURE_SHA256, history.INVENTORY_FIXTURE_SHA256,
                                                    history.APPEND_MANIFEST_SHA256, history.load_baseline()])


class ReviewedSourceScopeAdapter(unittest.TestCase):
    def synthetic(self):
        baseline = history.load_baseline()
        suffixes = {}
        for rel, spec in baseline['files'].items():
            suffixes[rel] = {}
            for key, frozen in spec['lists'].items():
                row = {'baseline_length': frozen['length'], 'length': 0,
                       'sha256': '4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945'}
                if frozen['selection'] == 'identity_set': row['mode'] = 'new_department_rows'
                suffixes[rel][key] = row
        contract = {'baseline_commit': baseline['source_commit'],
                    'append_scope': {'approved_department_ids': ['synthetic-new-department'],
                                     'added_report_paths': ['progress/synthetic-coverage.json'],
                                     'added_context_paths': ['research/synthetic-context.json'],
                                     'file_suffixes': suffixes, 'derived_site_expectation': 'Synthetic independent expected projection.'},
                    'document_objects': [{'file': 'progress/synthetic-coverage.json'}, {'file': 'research/synthetic-context.json'}],
                    'whole_holds': [{'school_id': 'synthetic-held', 'whole_scope_hold': True}]}
        ref = {'path': history.SOURCE_CONTRACT_PATH, 'sha256': history.sha256(b'synthetic source contract')}
        audits = {'source_input_sha256': history.sha256(b'synthetic input'), 'review_result_sha256': history.sha256(b'synthetic review')}
        return contract, ref, audits

    def test_adapter_derives_exact_paths_and_keeps_every_suffix_boundary(self):
        contract, ref, audits = self.synthetic()
        scope = history.reviewed_scope_from_contract(contract, ref, audits)
        self.assertEqual(scope['added_output_paths'], ['progress/synthetic-coverage.json', 'research/synthetic-context.json',
                                                      'site/exports/synthetic-new-department.xlsx'])
        self.assertEqual(scope['held_school_ids'], ['synthetic-held'])
        self.assertEqual(scope['file_suffixes']['site/atlas.json']['exports'],
                         {'length': 0, 'sha256': '4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945'})

    def test_adapter_rejects_unknown_scope_old_department_extra_paths_and_changed_boundaries(self):
        mutations = [lambda c: c['append_scope'].update(extra=True),
                     lambda c: c.update(baseline_commit='wrong'),
                     lambda c: c['append_scope'].update(approved_department_ids=['hit-computing']),
                     lambda c: c['append_scope']['approved_department_ids'].append('synthetic-new-department'),
                     lambda c: c['append_scope']['added_report_paths'].append('site/unreviewed.json'),
                     lambda c: c['append_scope']['added_context_paths'].clear(),
                     lambda c: c['document_objects'].append({'file': 'research/extra.json'}),
                     lambda c: c['append_scope']['file_suffixes']['data/atlas.json']['people'].update(baseline_length=605),
                     lambda c: c['append_scope']['file_suffixes']['site/atlas.json']['exports'].update(mode='prefix'),
                     lambda c: c['append_scope']['file_suffixes']['data/atlas.json']['people'].update(extra=True),
                     lambda c: c['whole_holds'][0].update(whole_scope_hold=False)]
        for mutate in mutations:
            contract, ref, audits = self.synthetic(); mutate(contract)
            with self.assertRaises(ValueError): history.reviewed_scope_from_contract(contract, ref, audits)

    def test_pinned_candidate_has_complete_tree_suffix_and_source_closure(self):
        manifest = history.load_current_append_manifest()
        inventory = history.load_inventory()
        if manifest is None:
            # Preparation mode has exactly this implementation, no unpinned data append.
            pending = {history.APPEND_MANIFEST_PATH, history.SOURCE_CONTRACT_PATH, history.SOURCE_FIXTURE_PATH,
                       'scripts/validate_source_contract.py', 'tests/test_rotation003_wave8_source_contract.py'}
            preparation = {'changed_existing': {}, 'allowed_added_outputs': {},
                           'implementation_added_files': sorted(history.IMPLEMENTATION_ADDED_FILES - pending),
                           'implementation_modified_files': {rel: {'before_sha256': inventory['files'][rel]['sha256']}
                                                             for rel in history.IMPLEMENTATION_MODIFIED_FILES}}
            history.validate_tree(ROOT, preparation, inventory)
            return
        source_ref = manifest['source_contract']
        source = history.pinned_json((ROOT / source_ref['path']).read_bytes(), source_ref['sha256'])
        scope = history.reviewed_scope_from_contract(source, source_ref, manifest['audit_digests'])
        with historical_root(ROOT) as released_root:
            history.validate_tree(released_root, manifest, inventory)
        documents = {rel: json.loads((ROOT / rel).read_bytes()) for rel in history.load_baseline()['files']}
        history.validate_reviewed_suffixes(documents, scope)
        import importlib.util
        spec = importlib.util.spec_from_file_location('reviewed_source_contract_validator', ROOT / 'scripts/validate_source_contract.py')
        validator = importlib.util.module_from_spec(spec); spec.loader.exec_module(validator)
        result = validator.validate_contract(ROOT, source_ref['path'], check_generated=True,
                                             expected_contract_sha256=source_ref['sha256'])
        self.assertEqual(result['status'], 'passed')


if __name__ == '__main__':
    unittest.main()
