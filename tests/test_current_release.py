"""Current candidate checks, deliberately NOT run against historical fixtures.

The fixed published release is only the independent conservation reference.
"""
import copy
import hashlib
import json
from pathlib import Path
import sys
import unittest
from published_fixture import published_root
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import build
from build_rosters import validate_rosters
from public_metadata import check_public_tree

MAPPING_SHA256 = 'b08daade03c91c774ecda2bc9469f5d92497be873732c5bfb58c59ab9a244475'
EXPECTED_IDS = ['nju-shiyini', 'nju-yangderui']

def read(root, rel):
    return json.loads((root / rel).read_text())

def mapping():
    raw = (ROOT / 'tests/fixtures/independent-nju-source-mapping.json').read_bytes()
    assert hashlib.sha256(raw).hexdigest() == MAPPING_SHA256, 'Reviewed new-source mapping changed'
    return json.loads(raw)

def validate_append(current, previous, additions):
    assert set(current) == set(previous), 'Unlisted canonical root fields'
    for key, value in previous.items():
        if key in ('people', 'org_units', 'profile_batches'):
            assert current[key] == value + additions[key], 'Historical or new source fact changed: ' + key
        else:
            assert current[key] == value, 'Unlisted change: ' + key
    assert [x['person_id'] for x in current['people'][-2:]] == EXPECTED_IDS
    assert len({p['person_id'] for p in current['people']}) == len(current['people'])

class CurrentRelease(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.previous = read(published_root(), 'data/atlas.json')
        cls.actual = read(ROOT, 'data/atlas.json')
        cls.additions = mapping()

    def test_current_canonical_exact_append_conservation(self):
        validate_append(self.actual, self.previous, self.additions)
        self.assertEqual(len(self.actual['people']), 614)
        self.assertEqual(len(self.actual['pending_people']), 84)

    def test_old_fact_deletion_reordering_and_unknown_promotions_fail(self):
        mutations = [
            lambda d: d['people'][0].update(name='invented'),
            lambda d: d['people'].pop(0),
            lambda d: d['people'].reverse(),
            lambda d: d['people'][-1].update(quick_link_eligible=True),
            lambda d: d['people'][-1]['education'][0].update(degree_awarded=False),
            lambda d: d['people'][-1]['sources'][0].update(url='https://example.test/unapproved'),
            lambda d: d['people'].append(copy.deepcopy(d['people'][-1])),
            lambda d: d.update(unapproved=True),
            lambda d: d['pending_people'].clear(),
        ]
        for change in mutations:
            candidate = copy.deepcopy(self.actual); change(candidate)
            with self.subTest(change=change), self.assertRaises(AssertionError):
                validate_append(candidate, self.previous, self.additions)

    def test_current_schema_build_and_source_metadata(self):
        import jsonschema
        validator = jsonschema.Draft202012Validator(read(ROOT, 'schema/atlas.schema.json'), format_checker=jsonschema.FormatChecker())
        validator.validate(self.actual)
        self.assertTrue(build.validate(self.actual))
        self.assertTrue(validate_rosters(read(ROOT, 'data/rosters.json'), self.actual))
        check_public_tree(ROOT, phase='final', include_workbooks=True)

    def test_generated_live_data_is_actual_canonical_and_build_id(self):
        site = read(ROOT, 'site/atlas.json')
        for key, value in self.actual.items():
            self.assertEqual(site[key], value, key)
        expected = hashlib.sha256(b''.join((ROOT / rel).read_bytes() for rel in [
            'data/atlas.json', 'data/rosters.json', 'scripts/build.py',
            'scripts/build_rosters.py', 'scripts/deterministic_xlsx.py'])).hexdigest()[:16]
        self.assertEqual(site['build_id'], expected)
        self.assertEqual(read(ROOT, 'site/rosters.json')['build_id'], expected)
        self.assertEqual(site['exports'], build.department_exports(self.actual))
        new = next(x for x in site['exports'] if x['department_id'] == 'nju-social-sciences')
        self.assertEqual(new['people_count'], 2)

    def test_all_old_workbooks_and_roster_facts_are_unchanged(self):
        old = published_root()
        for file in (old / 'site/exports').glob('*'):
            if file.name == '待核对名录.xlsx':
                continue  # Sole global count cell is tested separately below.
            self.assertEqual((ROOT / 'site/exports' / file.name).read_bytes(), file.read_bytes(), file.name)
        self.assertEqual((ROOT / 'data/rosters.json').read_bytes(), (old / 'data/rosters.json').read_bytes())
        roster = read(ROOT, 'site/rosters.json'); previous = read(old, 'site/rosters.json')
        roster.pop('build_id'); previous.pop('build_id'); self.assertEqual(roster, previous)

    def test_roster_workbook_changes_only_global_profile_count_cell(self):
        from zipfile import ZipFile
        from xml.etree import ElementTree as ET
        rel = 'site/exports/待核对名录.xlsx'
        member = 'xl/worksheets/sheet2.xml'
        with ZipFile(published_root() / rel) as old, ZipFile(ROOT / rel) as new:
            self.assertEqual(old.namelist(), new.namelist())
            for name in old.namelist():
                before, after = old.read(name), new.read(name)
                if name != member:
                    self.assertEqual(before, after, name)
                else:
                    ns = {'s': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
                    a = ET.fromstring(before).find('.//s:c[@r="A39"]', ns)
                    b = ET.fromstring(after).find('.//s:c[@r="A39"]', ns)
                    self.assertIsNotNone(a); self.assertIsNotNone(b)
                    self.assertEqual(''.join(b.itertext()), ''.join(a.itertext()).replace('612份独立人物档案', '614份独立人物档案'))
                    self.assertEqual(after, before.replace(b'612&#20221;&#29420;&#31435;', b'614&#20221;&#29420;&#31435;'))

    def test_live_runtime_and_old_validation_engines_are_unchanged(self):
        for rel in ['site/app.js','site/model.js','site/rosters.js','site/styles.css','site/index.html',
                    'scripts/build.py','scripts/build_rosters.py','scripts/validate_source_contract.py',
                    'scripts/validate_metadata_transition.py','tests/source_date_history.py',
                    'tests/source-date-history.js']:
            self.assertEqual((ROOT / rel).read_bytes(), (published_root() / rel).read_bytes(), rel)

    def test_new_workbook_is_two_source_bound_people(self):
        from openpyxl import load_workbook
        wb = load_workbook(ROOT / 'site/exports/nju-social-sciences.xlsx', data_only=False)
        try:
            text = '\n'.join(str(c.value) for ws in wb for row in ws for c in row if c.value is not None)
            for value in ['施旖旎','杨德睿','2013','2020','未披露']:
                self.assertIn(value, text)
            self.assertNotIn('csu-wangmiao', text)
        finally:
            wb.close()

if __name__ == '__main__': unittest.main()
