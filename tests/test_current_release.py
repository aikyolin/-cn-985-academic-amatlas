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
FIRST_IDS = ['nju-shiyini', 'nju-yangderui']
NEXT_MAPPING_SHA256 = '6b7347159e025485837de10750b40e7af329f229db559e273f4f9145095a6079'
SEU_MAPPING_SHA256 = 'e628de5b926bc65288b908aa2c8fc85fd5ff55f156891e2ab573acacaaa86795'
SEU_IDS = ['seu-dinghui', 'seu-sushu', 'seu-zhangkaifeng', 'seu-zhangjianqiong', 'seu-liupeidang', 'seu-shan-pingji-wave171', 'seu-he-shaojin-wave171', 'seu-zhangxueyi', 'seu-dongqun', 'seu-longdiyong']
NEXT_IDS = ['nju-huxiaowu', 'nju-caipingqiang', 'nju-linzhaoyu', 'nju-huying', 'nju-zhangwei-linguistics', 'nju-lvlinhai-education', 'nju-liyougen-law', 'nju-chenbaojun', 'nju-jiangfei', 'nju-zhoujiaxin']

def read(root, rel):
    return json.loads((root / rel).read_text())

def mapping():
    raw = (ROOT / 'tests/fixtures/independent-nju-source-mapping.json').read_bytes()
    assert hashlib.sha256(raw).hexdigest() == MAPPING_SHA256, 'Reviewed new-source mapping changed'
    return json.loads(raw)

def next_mapping():
    raw = (ROOT / 'tests/fixtures/independent-nju10-source-mapping.json').read_bytes()
    assert hashlib.sha256(raw).hexdigest() == NEXT_MAPPING_SHA256, 'Reviewed new ten-person mapping changed'
    return json.loads(raw)

def seu_mapping():
    raw = (ROOT / 'tests/fixtures/independent-seu10-source-mapping.json').read_bytes()
    assert hashlib.sha256(raw).hexdigest() == SEU_MAPPING_SHA256, 'Reviewed SEU ten-person mapping changed'
    return json.loads(raw)

def reviewed_additions():
    first, second, third = mapping(), next_mapping(), seu_mapping()
    assert [p['person_id'] for p in first['people']] == FIRST_IDS
    assert [p['person_id'] for p in second['people']] == NEXT_IDS
    assert [p['person_id'] for p in third['people']] == SEU_IDS
    return {key: first[key] + second[key] + third[key] for key in ('people', 'org_units', 'profile_batches')}

def validate_append(current, previous, additions):
    assert set(current) == set(previous), 'Unlisted canonical root fields'
    for key, value in previous.items():
        if key in ('people', 'org_units', 'profile_batches'):
            assert current[key] == value + additions[key], 'Historical or new source fact changed: ' + key
        else:
            assert current[key] == value, 'Unlisted change: ' + key
    assert [x['person_id'] for x in current['people'][len(previous['people']):]] == FIRST_IDS + NEXT_IDS + SEU_IDS
    assert len({p['person_id'] for p in current['people']}) == len(current['people'])

class CurrentRelease(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.previous = read(published_root(), 'data/atlas.json')
        cls.actual = read(ROOT, 'data/atlas.json')
        cls.additions = reviewed_additions()

    def test_current_canonical_exact_append_conservation(self):
        validate_append(self.actual, self.previous, self.additions)
        self.assertEqual(len(self.actual['people']), len(self.previous['people']) + len(self.additions['people']))
        self.assertEqual(len(self.actual['pending_people']), 84)

    def test_published_614_prefix_is_independent_fixed_612_plus_first_mapping(self):
        first = mapping()
        self.assertEqual(len(self.previous['people']) + len(first['people']), 614)
        for key in ('people', 'org_units', 'profile_batches'):
            expected = self.previous[key] + first[key]
            self.assertEqual(self.actual[key][:len(expected)], expected, key)

    def test_published_624_prefix_is_independent_fixed_612_plus_reviewed_nju_mappings(self):
        first, second = mapping(), next_mapping()
        self.assertEqual(len(self.previous['people']) + len(first['people']) + len(second['people']), 624)
        for key in ('people', 'org_units', 'profile_batches'):
            expected = self.previous[key] + first[key] + second[key]
            self.assertEqual(self.actual[key][:len(expected)], expected, key)

    def test_old_fact_deletion_reordering_and_unknown_promotions_fail(self):
        # Mutate each independently protected era, not just whichever person is last.
        for index in (0, 612, 614, 624):
            for key, value in [('name', 'invented'), ('quick_link_eligible', True)]:
                candidate = copy.deepcopy(self.actual)
                if candidate['people'][index].get(key) == value:
                    value = 'invented replacement'
                candidate['people'][index][key] = value
                with self.subTest(index=index, key=key), self.assertRaises(AssertionError):
                    validate_append(candidate, self.previous, self.additions)
        mutations = [
            lambda d: d['people'].pop(0),
            lambda d: d['people'].reverse(),
            lambda d: d['people'][612]['education'][0].update(degree_awarded=False),
            lambda d: d['people'][614]['sources'][0].update(url='https://example.test/unapproved'),
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
        expected_members = [p for p in self.additions['people'] if p['department_id'] == 'nju-social-sciences']
        self.assertEqual(new['people_count'], len(expected_members))

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
                    self.assertEqual(''.join(b.itertext()), ''.join(a.itertext()).replace('612份独立人物档案', str(len(self.actual['people'])) + '份独立人物档案'))
                    self.assertEqual(after, before.replace(b'612&#20221;&#29420;&#31435;', str(len(self.actual['people'])).encode() + b'&#20221;&#29420;&#31435;'))

    def test_live_runtime_has_only_reviewed_institution_fix_and_old_engines_unchanged(self):
        for rel in ['site/app.js','site/model.js','site/rosters.js','site/styles.css','site/index.html',
                    'scripts/build.py','scripts/build_rosters.py','scripts/validate_source_contract.py',
                    'scripts/validate_metadata_transition.py','tests/source_date_history.py',
                    'tests/source-date-history.js']:
            expected = (published_root() / rel).read_bytes()
            # Sole approved runtime correction: unknown appointment institutions
            # must not inherit the person's directory affiliation; cache token follows.
            if rel == 'site/app.js':
                before = b"${esc(a.institution||p.department)}"
                after = "${esc(a.institution||'任职机构未核实')}".encode()
                self.assertEqual(expected.count(before), 1)
                expected = expected.replace(before, after)
            asset_token_counts = {'site/app.js': 3, 'site/rosters.js': 1, 'site/index.html': 2}
            if rel in asset_token_counts:
                before, after = b'source-dates-20261024', b'appointment-institution-20261025'
                self.assertEqual(expected.count(before), asset_token_counts[rel])
                expected = expected.replace(before, after)
            self.assertEqual((ROOT / rel).read_bytes(), expected, rel)

    def test_every_affected_workbook_exactly_matches_reviewed_members_and_fields(self):
        from openpyxl import load_workbook
        departments = {p['department_id'] for p in next_mapping()['people'] + seu_mapping()['people']}
        expected_people = self.previous['people'] + self.additions['people']
        for department in departments:
            members = [p for p in expected_people if p['department_id'] == department]
            self.assertEqual(len(members), len({p['person_id'] for p in members}))
            wb = load_workbook(ROOT / 'site/exports' / (department + '.xlsx'), data_only=False)
            try:
                tables = build.department_tables(members, self.actual['updated_at'], self.actual['institutions'])
                self.assertEqual(wb.sheetnames, [name for name, _ in tables])
                for name, rows in tables:
                    expected = [[build.clean(value) if build.clean(value) != '' else None for value in row] for row in rows]
                    actual = [list(row) for row in wb[name].iter_rows(values_only=True)]
                    self.assertEqual(actual, expected, (department, name))
                self.assertEqual([row[0] for row in wb['总览'].iter_rows(min_row=2, values_only=True)], [p['name'] for p in members])
            finally:
                wb.close()

    def test_live_social_workbook_preserves_first_two_source_bound_people(self):
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
