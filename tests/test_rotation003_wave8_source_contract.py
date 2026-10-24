"""Generic exact replay and immutable public source-contract boundaries."""
import copy
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from validate_source_contract import exact, replay, validate_contract

CONTRACT = 'tests/fixtures/rotation003-wave8-source-contract.json'
CONTRACT_SHA256 = '65c2a67e2cb10893fc3d0b42c8bcc94cc0d8eb85741b7427e44133d34d7c2a95'
FIXTURE = 'tests/fixtures/rotation003-wave8-clean-public-sources.json'
FIXTURE_SHA256 = '4cd26e241f1293484af3d400288638484e0286f43ef0718ef5cbd7accb2d251a'


class SourceContractTests(unittest.TestCase):
    def setUp(self):
        self.original = {'name': 'Synthetic', 'status': 'pending', 'unknown': None, 'confirmed': False, 'ordered': [{'value': 1}, {'value': 2}], 'empty': [], 'extra_fact': {'value': 'preserve'}}
        self.binding = {'additions': [{'path': '/source_status', 'value': 'pending', 'before_exists': False}, {'path': '/compatibility', 'value': False, 'before_exists': False}], 'normalizations': [{'path': '/status', 'before': 'pending', 'after': 'reviewed', 'preserved_at': '/source_status', 'reason': 'Synthetic schema label only'}]}
        self.expected = copy.deepcopy(self.original)
        self.expected.update(status='reviewed', source_status='pending', compatibility=False)

    def test_frozen_source_fixture(self):
        self.assertEqual(hashlib.sha256((ROOT / FIXTURE).read_bytes()).hexdigest(), FIXTURE_SHA256)

    def test_frozen_candidate_contract(self):
        result = validate_contract(ROOT, CONTRACT, expected_contract_sha256=CONTRACT_SHA256)
        self.assertEqual(result['status'], 'passed')

    def test_replay_is_exact(self):
        self.assertTrue(exact(replay(self.original, self.binding), self.expected))

    def test_reported_qualification_labels_visible_without_date_inference(self):
        contract=json.loads((ROOT/CONTRACT).read_text())
        fixture=json.loads((ROOT/FIXTURE).read_text())
        atlas=json.loads((ROOT/'data/atlas.json').read_text())
        from validate_source_contract import pointer
        for binding in contract['objects']:
            if binding['target']['file'] != 'data/atlas.json' or not binding['target']['pointer'].startswith('/people/'):
                continue
            original=pointer(fixture,binding['source']['pointer'])
            actual=pointer(atlas,binding['target']['pointer'])
            for source_event,current in zip(original['education'],actual['education']):
                label=source_event.get('source_reported_degree_label')
                year=source_event.get('source_reported_year')
                if label and year is not None and label not in source_event.get('note',''):
                    self.assertEqual(current['note'],'来源资格标签：'+label+'。'+source_event['note'])
                    self.assertEqual(current['source_note_before_display_normalization'],source_event['note'])
                    for key in ('source_reported_degree_label','source_reported_year','start','end','degree_awarded','degree_awarded_date'):
                        self.assertTrue(exact(source_event.get(key),current.get(key)))

    def test_replay_does_not_mutate_original(self):
        old = copy.deepcopy(self.original)
        replay(self.original, self.binding)
        self.assertTrue(exact(old, self.original))

    def test_extra_sibling_rejected(self):
        modified=copy.deepcopy(self.expected);modified['extra_fact']['unapproved']=True
        self.assertFalse(exact(replay(self.original,self.binding),modified))

    def test_unknown_boolean_and_integer_are_distinct(self):
        for before,after in [(None,False),(False,0),(True,1),(1,1.0)]:
            with self.subTest(before=before,after=after):
                self.assertFalse(exact({'value':before},{'value':after}))

    def test_array_reordering_rejected(self):
        modified=copy.deepcopy(self.expected);modified['ordered'].reverse()
        self.assertFalse(exact(replay(self.original,self.binding),modified))

    def test_array_append_rejected(self):
        modified=copy.deepcopy(self.expected);modified['ordered'].append({'value':3})
        self.assertFalse(exact(replay(self.original,self.binding),modified))

    def test_empty_collection_deletion_rejected(self):
        modified=copy.deepcopy(self.expected);del modified['empty']
        self.assertFalse(exact(replay(self.original,self.binding),modified))

    def test_normalization_before_checked(self):
        bad=copy.deepcopy(self.binding);bad['normalizations'][0]['before']='other'
        with self.assertRaises(AssertionError):replay(self.original,bad)

    def test_normalization_after_does_not_change_expected(self):
        bad=copy.deepcopy(self.binding);bad['normalizations'][0]['after']='invented'
        self.assertFalse(exact(replay(self.original,bad),self.expected))

    def test_normalization_preserved_value_checked(self):
        bad=copy.deepcopy(self.binding);bad['additions'][0]['value']='invented'
        with self.assertRaises(AssertionError):replay(self.original,bad)

    def test_normalization_preserved_pointer_checked(self):
        bad=copy.deepcopy(self.binding);bad['normalizations'][0]['preserved_at']='/unknown'
        with self.assertRaises(AssertionError):replay(self.original,bad)

    def test_original_cannot_be_overwritten_by_addition(self):
        bad=copy.deepcopy(self.binding);bad['additions'][0]['path']='/unknown'
        with self.assertRaises(AssertionError):replay(self.original,bad)

    def test_duplicate_addition_rejected(self):
        bad=copy.deepcopy(self.binding);bad['additions'].append(copy.deepcopy(bad['additions'][0]))
        with self.assertRaises(AssertionError):replay(self.original,bad)

    def test_fact_normalization_rejected(self):
        for key in ['degree_awarded','event_kind','start','end','degree_awarded_date','institution_985','region','continent_code','current','employment_status']:
            with self.subTest(key=key):
                original={key:None}
                binding={'additions':[{'path':'/original','value':None,'before_exists':False}], 'normalizations':[{'path':'/'+key,'before':None,'after':True,'preserved_at':'/original','reason':'not allowed'}]}
                with self.assertRaises(AssertionError):replay(original,binding)

    def test_contract_cannot_resign_changed_fixture_or_candidate(self):
        # A caller supplies the independent frozen contract digest. Replacing both
        # fixture metadata and matching candidate digests cannot authorize edits.
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);path=root/CONTRACT;path.parent.mkdir(parents=True)
            contract=json.loads((ROOT/CONTRACT).read_text())
            contract['source_fixture']['sha256']='0'*64
            contract['source_packages'][0]['canonical_sha256']='0'*64
            contract['document_objects'][0]['canonical_sha256']='0'*64
            path.write_text(json.dumps(contract))
            with self.assertRaisesRegex(AssertionError,'Frozen contract bytes changed'):
                validate_contract(root,CONTRACT,expected_contract_sha256=CONTRACT_SHA256)


if __name__=='__main__':unittest.main()
