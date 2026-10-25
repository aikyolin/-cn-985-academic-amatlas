"""Exact metadata migration and adversarial non-metadata changes, offline only."""
import copy
import io
import json
from pathlib import Path
import sys
import tempfile
import shutil
import unittest
from zipfile import ZipFile, ZIP_DEFLATED, ZipInfo
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import validate_metadata_transition as engine
import source_date_history as history
from published_fixture import published_root


def archive(members):
    output = io.BytesIO()
    with ZipFile(output, 'w', ZIP_DEFLATED, compresslevel=9) as z:
        for name, raw in sorted(members.items()):
            info = ZipInfo(name, (2000, 1, 1, 0, 0, 0)); info.compress_type = ZIP_DEFLATED
            info.create_system = 0; info.external_attr = 0o600 << 16
            z.writestr(info, raw, compress_type=ZIP_DEFLATED, compresslevel=9)
    return output.getvalue()


class SyntheticMetadataNegatives(unittest.TestCase):
    def setUp(self):
        self.before = b'<sheet><c r="A2" t="s">fact</c><c r="E1" t="s">old label</c><c r="F2" t="b">0</c><url>https://example.test/source</url></sheet>'
        self.after = self.before.replace(b'old label', b'new label')
        self.member = 'xl/worksheets/sheet1.xml'
        self.old = archive({self.member: self.before, 'xl/relationships.xml': b'<relations unchanged="true"/>'})
        self.new = archive({self.member: self.after, 'xl/relationships.xml': b'<relations unchanged="true"/>'})
        self.spec = {'before_sha256': engine.sha256(self.old), 'after_sha256': engine.sha256(self.new), 'byte_length': len(self.new), 'members': {
            self.member: {'before_sha256': engine.sha256(self.before), 'after_sha256': engine.sha256(self.after), 'replacements': [
                {'kind': 'overview_header', 'before': '<c r="E1" t="s">old label</c>', 'after': '<c r="E1" t="s">new label</c>'}]}}}

    def test_exact_reverse_recovers_original_zip_bytes(self):
        self.assertEqual(engine.reverse_workbook(self.new, self.spec), self.old)

    def test_fact_url_type_style_relationship_and_extra_member_cannot_hide_behind_new_hashes(self):
        cases = [
            {self.member: self.after.replace(b'>fact<', b'>invented<')},
            {self.member: self.after.replace(b'example.test/source', b'example.test/wrong')},
            {self.member: self.after.replace(b't="b">0', b't="n">0')},
            {self.member: self.after.replace(b'r="A2"', b'r="A2" s="5"')},
            {'xl/relationships.xml': b'<relations unchanged="false"/>'},
            {'xl/unreviewed.xml': b'<extra/>'},
        ]
        for changes in cases:
            members = {self.member: self.after, 'xl/relationships.xml': b'<relations unchanged="true"/>'}; members.update(changes)
            raw = archive(members)
            with self.subTest(changes=list(changes)), self.assertRaises(ValueError):
                engine.reverse_workbook(raw, self.spec)
            # Even dishonestly updating outer/inner current hashes cannot change
            # the independently fixed old bytes or expand reversible cell scope.
            dishonest = copy.deepcopy(self.spec)
            dishonest.update(after_sha256=engine.sha256(raw), byte_length=len(raw))
            dishonest['members'][self.member]['after_sha256'] = engine.sha256(members[self.member])
            with self.subTest(resigned=list(changes)), self.assertRaises(ValueError):
                engine.reverse_workbook(raw, dishonest)

    def test_missing_changed_cell_or_duplicate_xml_is_rejected(self):
        for data in (self.after.replace(b'new label', b'other label'), self.after + self.after):
            raw = archive({self.member: data, 'xl/relationships.xml': b'<relations unchanged="true"/>'})
            spec = copy.deepcopy(self.spec); spec.update(after_sha256=engine.sha256(raw), byte_length=len(raw)); spec['members'][self.member]['after_sha256'] = engine.sha256(data)
            with self.assertRaises(ValueError): engine.reverse_workbook(raw, spec)

    def test_text_reverse_exact_context_and_predecessor_hash(self):
        old, new = b'fact=false; label=old; url=same', b'fact=false; label=new; url=same'
        spec = {'before_sha256': engine.sha256(old), 'after_sha256': engine.sha256(new), 'byte_length': len(new), 'patches': [{'after_offset': 18, 'before': 'old', 'after': 'new'}]}
        self.assertEqual(engine.reverse_text(new, spec), old)
        corrupt = new.replace(b'false', b'true '); dishonest = dict(spec, after_sha256=engine.sha256(corrupt))
        with self.assertRaises(ValueError): engine.reverse_text(corrupt, dishonest)
        corrupt = copy.deepcopy(spec); corrupt['patches'][0]['after_offset'] = 0
        with self.assertRaises(ValueError): engine.reverse_text(new, corrupt)

    def test_pins_reject_forged_expected_and_duplicate_keys(self):
        raw = b'{"approved":true}'
        # An explicit synthetic test golden, not a live-derived production pin.
        pin = '20ec2f38fc96bc7d416a9af537493ae0bae26c5ad4c5a0f2d94f56f9c3e04958'
        self.assertEqual(engine.pinned_json(raw, pin), {"approved": True})
        with self.assertRaises(ValueError): engine.pinned_json(raw + b" ", pin)
        for value in (None, '0' * 64):
            with self.assertRaises(ValueError): engine.pinned_json(raw, value)
        duplicate = b'{"a":1,"a":2}'
        with self.assertRaises(ValueError): engine.pinned_json(duplicate, engine.sha256(duplicate))

    def test_exact_tree_rejects_future_append_unknown_file_missing_file_and_symlink(self):
        original = {'data/atlas.json': b'{"people":[]}', 'old.xlsx': self.old}
        baseline = {'files': {p: {'bytes': len(raw), 'sha256': engine.sha256(raw)} for p, raw in original.items()}}
        manifest = {'changed': {}, 'added': {}, 'self_pinned_files': []}
        changes = [lambda root: (root / 'data/atlas.json').write_bytes(b'{"people":[{"person_id":"unapproved"}]}'),
                   lambda root: (root / 'extra.json').write_bytes(b'{}'),
                   lambda root: (root / 'old.xlsx').unlink(),
                   lambda root: (root / 'alias').symlink_to('old.xlsx')]
        for change in changes:
            with tempfile.TemporaryDirectory() as name:
                root = Path(name)
                for rel, raw in original.items():
                    file = root / rel; file.parent.mkdir(parents=True, exist_ok=True); file.write_bytes(raw)
                self.assertEqual(len(engine.validate_tree(root, manifest, baseline)), 2)
                change(root)
                with self.assertRaises(ValueError): engine.validate_tree(root, manifest, baseline)


class ReviewedMetadataTransition(unittest.TestCase):
    def test_published_transition_tree_and_every_changed_file_are_independently_strict(self):
        actual = history.validate_current_tree(published_root())
        baseline = history.load_transition()[1]
        self.assertEqual(len(baseline['files']), 398)
        self.assertEqual(set(actual), set(baseline['files']) | history.IMPLEMENTATION_ADDED_FILES)

    def test_all_398_historical_bytes_reconstruct_exactly(self):
        engine_, baseline, policy, source, manifest = history.load_transition()
        for rel, expected in baseline['files'].items():
            raw = history.historical_bytes(rel, root=published_root())
            self.assertEqual(engine.sha256(raw), expected['sha256'], rel)
            self.assertEqual(len(raw), expected['bytes'], rel)
        self.assertEqual(policy['change_counts'], {'overview_header': 133, 'overall_review_notice': 612, 'availability_label': 568, 'classification_missing_date': 488, 'derived_column_width': 225, 'source_date_summary': 48})

    def test_resigned_policy_cannot_disguise_non_whitelisted_cells_or_xml(self):
        engine_, baseline, policy, source, manifest = history.load_transition()
        first = next(iter(policy['workbooks']))
        for mode in ['coordinate', 'xml', 'kind', 'canonical', 'extra_workbook']:
            altered = copy.deepcopy(policy)
            op = altered['workbooks'][first]['members']['xl/worksheets/sheet1.xml']['replacements'][0]
            if mode == 'coordinate': op['cell'] = 'A1'
            elif mode == 'xml': op['after'] = op['after'].replace('r="E1"', 'r="A1"')
            elif mode == 'kind': op['kind'] = 'arbitrary_fact_change'
            elif mode == 'canonical': altered['canonical_inputs']['data/atlas.json'] = '0' * 64
            else: altered['workbooks']['site/exports/unapproved.xlsx'] = copy.deepcopy(altered['workbooks'][first])
            with self.subTest(mode=mode), self.assertRaises(ValueError):
                engine.validate_policy(altered, baseline)

    def test_actual_external_root_is_not_replaced_by_clean_local_bytes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); (root / 'site').mkdir()
            (root / 'site/app.js').write_bytes(b'WRONG')
            with self.assertRaises(ValueError):
                history.historical_bytes('site/app.js', root=root)

    def test_loader_and_cached_manifest_bytes_are_rechecked_on_every_full_tree_call(self):
        history.load_transition()  # Deliberately populate the parser cache first.
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            shutil.copytree(published_root(), root, dirs_exist_ok=True, ignore=shutil.ignore_patterns('__pycache__', '.git', '.pytest_cache', 'node_modules'))
            history.validate_current_tree(root)
            loader = root / 'tests/source_date_history.py'; original_loader = loader.read_bytes()
            for changed in (original_loader + b'\n# unapproved comment\n', original_loader.replace(b'one explicit', b'one changed!')):
                loader.write_bytes(changed)
                with self.assertRaisesRegex(ValueError, 'Normalized loader'):
                    history.validate_current_tree(root)
            loader.write_bytes(original_loader)
            manifest = root / history.MANIFEST_PATH
            manifest.write_bytes(manifest.read_bytes() + b' ')
            with self.assertRaisesRegex(ValueError, 'Pinned bytes changed'):
                history.validate_current_tree(root)

    def test_original_canonical_people_and_source_contracts_match_published_bytes(self):
        for rel in ['data/atlas.json', 'data/rosters.json', 'tests/fixtures/rotation003-wave8-source-contract.json', 'tests/fixtures/rotation003-wave8-clean-public-sources.json']:
            self.assertEqual(history.historical_bytes(rel, root=published_root()), (published_root() / rel).read_bytes(), rel)


if __name__ == '__main__': unittest.main()
