"""Second/third-batch integrity and export tests; no workbook is generated."""
import copy
import csv
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import build_rosters as roster_builder


def digest(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


class RosterBatchTwoTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rosters = json.loads((ROOT / 'data/rosters.json').read_text())
        cls.atlas = json.loads((ROOT / 'data/atlas.json').read_text())
        cls.new_entries = [entry for entry in cls.rosters['entries'] if entry.get('batch_id') == 'harbin-002']
        cls.weihai_entries = [entry for entry in cls.rosters['entries'] if entry.get('batch_id') == 'weihai-003']

    def test_observations_not_unique_or_verified_people(self):
        r = self.rosters
        self.assertEqual(len(r['entries']), 967)
        self.assertEqual(len({entry['id'] for entry in r['entries']}), 967)
        self.assertEqual(len(self.new_entries), 434)
        self.assertEqual(r['totals']['roster_observations'], 967)
        self.assertTrue(r['totals']['not_unique_people_count'])
        self.assertFalse(r['totals']['current_employment_count_verified'])
        self.assertEqual(r['totals']['organization_count'], 9)
        self.assertEqual(r['totals']['category_count'], 67)
        self.assertTrue(roster_builder.validate_rosters(r, self.atlas))

    def test_original_observation_fields_and_ids_are_stable(self):
        # An independently verified identity may be added, but the observation
        # itself (including its original links, spelling and organization) stays.
        fields = ['id', 'name', 'official_profile_url', 'campus_id', 'organization_id', 'category', 'listed_role', 'roster_source_url', 'accessed_on', 'notes']
        original = [{key: entry[key] for key in fields} for entry in self.rosters['entries'][:294]]
        self.assertEqual(digest(original), '9277524246155c7c32565c6bb972191a4ec71e10a9e29e12c748ed9b2d3d1c57')
        self.assertEqual(digest(self.rosters['summary'][:3]), '699032a23911b49a231ab7cd23dc5276701f640effcc9013bfcd3845363a221d')
        self.assertEqual(digest(self.rosters['coverage'][:16]), 'e40b00f67dd5f5b21b52b49ba9248c0c1edd3bc78ade53c845fc34570f28fa9d')
        self.assertEqual(digest(self.rosters['conflicts'][:8]), '361771393b78be54b5501c59c84b331862e11201e0f02052e7e903c0ec926632')

    def test_new_source_fields_are_preserved_exactly(self):
        original = [{key: value for key, value in entry.items() if key not in ('batch_id', 'automatic_merge')} for entry in self.new_entries]
        self.assertEqual(digest(original), '197fca0dcfd6acd35eb014ee9eb0d598469f65f3cf3ade700ce2f8ce01c738f5')
        self.assertTrue(all(entry['profile_identity_verified'] is False for entry in self.new_entries))
        self.assertTrue(all(entry['automatic_merge'] is False for entry in self.new_entries))
        self.assertTrue(all(not entry.get('verified_person_id') for entry in self.new_entries))

    def test_coverage_aliases_keep_original_evidence(self):
        coverage = self.rosters['coverage'][16:50]
        original = [{key: value for key, value in item.items() if key not in ('batch_id', 'url', 'visible_name_count')} for item in coverage]
        self.assertEqual(digest(original), 'e6ac3ae0318293880894a4e4aeca9ba4d9d7d924adb35189b5506337da02193f')
        self.assertEqual(len(coverage), 34)
        self.assertEqual(sum(item['visible_name_count'] for item in coverage), 434)
        for item in coverage:
            self.assertEqual(item['url'], item['source_url'])
            self.assertEqual(item['visible_name_count'], item['visible_entries'])

    def test_missing_links_include_not_add_to_placeholders(self):
        self.assertEqual(sum(not entry['official_profile_url'] for entry in self.new_entries), 76)
        self.assertEqual(sum(not entry['official_profile_url'] for entry in self.rosters['entries']), 162)
        placeholders = [item for item in self.rosters['conflicts'] if item['type'] == 'placeholder_profile_link' and item.get('batch_id') == 'harbin-002']
        self.assertEqual(len(placeholders), 9)
        by_id = {entry['id']: entry for entry in self.new_entries}
        for conflict in placeholders:
            entry = by_id[conflict['entry_id']]
            self.assertIsNone(entry['official_profile_url'])
            self.assertEqual(entry['source_link_raw'], conflict['source_link_raw'])
            self.assertTrue(entry['source_link_raw'])

    def test_candidate_groups_and_conflicts_remain_distinct(self):
        candidates = [item for item in self.rosters['dedup_candidates'] if item.get('batch_id') == 'harbin-002']
        self.assertEqual(len(candidates), 18)
        self.assertEqual(sum(item['kind'] == 'same_name_review_required' for item in candidates), 13)
        self.assertEqual(sum(item['kind'] == 'same_profile_path_review_required' for item in candidates), 5)
        self.assertTrue(all(item['automatic_merge'] is False for item in candidates))
        entry_ids = {entry['id'] for entry in self.rosters['entries']}
        for item in candidates:
            self.assertTrue(set(item['entry_ids']) <= entry_ids)
        original = [{key: value for key, value in item.items() if key not in ('batch_id', 'type')} for item in self.rosters['conflicts'][8:18]]
        self.assertEqual(digest(original), '19d14cc14564ee7593de83bd6d0277e7d76d354d5ff96235b6d15dd244bf99a6')
        historical = next(item for item in self.rosters['conflicts'] if item['type'] == 'historical_name_discrepancy')
        self.assertEqual((historical['current_listing'], historical['historical_listing']), ('刘峻峰', '刘俊峰'))
        self.assertEqual(sum(item['type'] == 'same_url_different_names' for item in self.rosters['conflicts']), 2)

    def test_batch_manifest_covers_each_observation_once(self):
        batches = self.rosters['batches']
        self.assertEqual([batch['batch_id'] for batch in batches], ['pilot-001', 'harbin-002', 'weihai-003'])
        self.assertEqual([batch['observation_count'] for batch in batches], [294, 434, 239])
        ids = [entry_id for batch in batches for entry_id in batch['entry_ids']]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(set(ids), {entry['id'] for entry in self.rosters['entries']})
        self.assertEqual(batches[1]['source_files'][0]['sha256'], 'c1288142f7394215c8eec620ae386a539ec75a53d111f8c0ef3a0aae931fab2d')
        self.assertEqual(batches[1]['validation']['dedup_candidate_groups'], 18)
        self.assertEqual(len(self.rosters['source_snapshots']), 24)
        self.assertEqual(len(self.rosters['exclusions']), 3)
        self.assertEqual(len(self.rosters['pending_checks']), 2)

    def test_role_labels_and_original_name_spelling_survive(self):
        entries = self.new_entries
        self.assertEqual(sum(entry['organization_id'] == 'hit-energy' for entry in entries), 172)
        self.assertEqual(sum(entry['organization_id'] == 'hit-environment' for entry in entries), 147)
        self.assertEqual(sum(entry['organization_id'] == 'hit-instrument' for entry in entries), 115)
        self.assertTrue(any(entry['listed_role'] == '博士后副研究员' for entry in entries))
        self.assertTrue(any(entry['listed_role'] == '实验教师' for entry in entries))
        entry = next(entry for entry in entries if entry['name'] == '刘丽艳')
        self.assertEqual(entry['name_as_listed'], '刘丽艳*')

    def test_weihai_source_rows_and_ids_are_preserved_exactly(self):
        entries = self.weihai_entries
        original = [{key: value for key, value in entry.items() if key not in ('batch_id', 'automatic_merge')} for entry in entries]
        self.assertEqual(digest(original), '43843d036d5eafa8d47e145a7d2233a7ba981ee5733d1f349e1344ba97b221a8')
        self.assertEqual(len(entries), 239)
        for org, expected in [('hit-weihai-computer', 72), ('hit-weihai-marine-engineering', 120), ('hit-weihai-automotive', 47)]:
            self.assertEqual(sum(entry['organization_id'] == org for entry in entries), expected)
        self.assertTrue(all(entry['profile_identity_verified'] is False and entry['automatic_merge'] is False for entry in entries))
        self.assertTrue(all(entry['campus_id'] == 'hit-weihai' for entry in entries))

    def test_weihai_coverage_keeps_source_dates_and_qualifiers(self):
        coverage = [item for item in self.rosters['coverage'] if item.get('batch_id') == 'weihai-003']
        original = [{key: value for key, value in item.items() if key not in ('batch_id', 'visible_name_count')} for item in coverage]
        self.assertEqual(digest(original), '4f93ddc1ad275f7ee5768b243e961087ba92cc89086e90c9367ac05971019e7a')
        self.assertEqual(len(coverage), 17)
        self.assertEqual(sum(item['visible_name_count'] for item in coverage), 239)
        dated = [item['source_declared_update'] for item in coverage if item['source_declared_update']]
        self.assertEqual(len(dated), 7)
        self.assertEqual(set(dated), {'2023年12月26日', '2024年3月21日', '2023年3月30日'})
        self.assertTrue(any(entry['listed_qualifiers'] for entry in self.weihai_entries))
        self.assertEqual(digest(self.rosters['role_interpretation']), '9c1098d16b8ae13b4ef55efb781195831efdc1be68fd601aa8c4d1db41cea7c0')
        self.assertTrue(any('2023至2024年' in text for text in self.rosters['limitations']))

    def test_weihai_conflicts_and_74_72_difference_are_not_filled(self):
        conflicts = [item for item in self.rosters['conflicts'] if item.get('batch_id') == 'weihai-003']
        original = [{key: value for key, value in item.items() if key not in ('batch_id', 'type')} for item in conflicts]
        self.assertEqual(digest(original), '86499b9b3934f3d51e939e520a9b9529ac35c530461cc7419976648b5d689f53')
        mismatch = next(item for item in conflicts if item['type'] == 'overview_count_not_reconciled')
        self.assertEqual(mismatch['overview_claimed_full_time_count'], 74)
        self.assertEqual(mismatch['visible_department_entries'], 72)
        self.assertIn('不虚构缺失2人', mismatch['resolution'])
        self.assertEqual(sum(not entry['official_profile_url'] for entry in self.weihai_entries), 51)
        placeholders = [item for item in conflicts if item['type'] == 'placeholder_profile_link']
        self.assertEqual(len(placeholders), 8)
        by_id = {entry['id']: entry for entry in self.weihai_entries}
        for item in placeholders:
            self.assertIsNone(by_id[item['entry_id']]['official_profile_url'])
            self.assertEqual(by_id[item['entry_id']]['source_link_raw'], item['source_link_raw'])

    def test_weihai_candidates_keep_34_unmerged_groups(self):
        candidates = [item for item in self.rosters['dedup_candidates'] if item.get('batch_id') == 'weihai-003']
        original = [{key: value for key, value in item.items() if key != 'batch_id'} for item in candidates]
        self.assertEqual(digest(original), '6cae8af33925c60720c756f5520b2c833bceda6ed56c67caf175b41405811f7a')
        self.assertEqual(len(candidates), 34)
        self.assertTrue(all(item['automatic_merge'] is False for item in candidates))
        self.assertEqual(len(self.rosters['dedup_candidates']), 52)
        self.assertEqual(self.rosters['batches'][2]['source_files'][0]['sha256'], '6856bfb1b7ac1d3fe8d66ed995ebb30a6f33edd4be5960efb556877e8942fc85')

    def fixture(self):
        entry = copy.deepcopy(self.rosters['entries'][0])
        entry.update(id='test-observation', name='测试姓名', official_profile_url='https://example.test/person/', roster_source_url='https://example.test/roster', profile_identity_verified=False)
        for key in ('batch_id', 'verified_person_id', 'profile_identity_evidence'):
            entry.pop(key, None)
        person = {'person_id': 'test-person', 'name': entry['name'], 'department_id': entry['organization_id'], 'official_url': 'http://example.test/person?lang=zh'}
        roster = {'scope': 'Synthetic fixture', 'entries': [entry], 'summary': [{'visible_roster_entries': 1}], 'coverage': [{'organization_id': entry['organization_id'], 'category': entry['category'], 'visible_name_count': 1, 'url': entry['roster_source_url'], 'accessed_on': entry['accessed_on']}], 'limitations': [], 'conflicts': []}
        atlas = {'people': [person], 'org_units': [{'id': entry['organization_id']}]}
        return roster, atlas

    def test_exact_name_org_and_homepage_still_only_candidate(self):
        roster, atlas = self.fixture()
        before = copy.deepcopy(roster)
        prepared = roster_builder.prepare_rosters(roster, atlas)
        entry = prepared['entries'][0]
        self.assertEqual(entry['candidate_person_ids'], ['test-person'])
        self.assertEqual(entry['candidate_match_status'], 'pending_identity_review')
        self.assertFalse(entry['profile_identity_verified'])
        self.assertFalse(entry['automatic_merge'])
        self.assertNotIn('verified_person_id', entry)
        self.assertEqual(roster, before)
        self.assertEqual(len(prepared['entries']), 1)

    def test_any_matching_component_mismatch_is_not_linked(self):
        for field, value in [('name', '另一个姓名'), ('department_id', 'different-unit'), ('official_url', 'https://example.test/another-person')]:
            with self.subTest(field=field):
                roster, atlas = self.fixture()
                atlas['people'][0][field] = value
                self.assertEqual(roster_builder.prepare_rosters(roster, atlas)['entries'][0]['candidate_person_ids'], [])

    def test_explicit_verified_relation_survives_without_candidate_promotion(self):
        roster, atlas = self.fixture()
        entry = roster['entries'][0]
        entry.update(profile_identity_verified=True, verified_person_id='test-person', profile_identity_evidence={'source_ids': ['source-test'], 'checked_on': '2026-10-23', 'official_url': atlas['people'][0]['official_url'], 'roster_source_url': entry['roster_source_url']})
        prepared = roster_builder.prepare_rosters(roster, atlas)['entries'][0]
        self.assertTrue(prepared['profile_identity_verified'])
        self.assertEqual(prepared['verified_person_id'], 'test-person')
        self.assertEqual(prepared['profile_identity_evidence'], entry['profile_identity_evidence'])
        self.assertEqual(prepared['candidate_match_status'], 'verified_separate_profile')
        self.assertEqual(prepared['candidate_person_ids'], [])
        self.assertFalse(prepared['automatic_merge'])

    def test_unsupported_verified_relation_is_rejected(self):
        roster, atlas = self.fixture()
        roster['entries'][0]['profile_identity_verified'] = True
        with self.assertRaisesRegex(AssertionError, 'explicit personal profile'):
            roster_builder.prepare_rosters(roster, atlas)

    def test_cross_domain_same_slug_is_not_an_automatic_candidate(self):
        roster, atlas = self.fixture()
        roster['entries'][0]['official_profile_url'] = 'https://other.example.test/person'
        entry = roster_builder.prepare_rosters(roster, atlas)['entries'][0]
        self.assertEqual(entry['candidate_person_ids'], [])
        self.assertEqual(entry['candidate_match_status'], 'not_linked')
        self.assertFalse(entry['profile_identity_verified'])

    def test_verified_aliases_or_redirects_need_both_exact_endpoints(self):
        for evidence_key in ('verified_alias_urls', 'redirect_chain'):
            with self.subTest(evidence_key=evidence_key):
                roster, atlas = self.fixture()
                entry = roster['entries'][0]
                entry['official_profile_url'] = 'https://other.example.test/person'
                entry.update(profile_identity_verified=True, verified_person_id='test-person', profile_identity_evidence={
                    'source_ids': ['source-test'], 'checked_on': '2026-10-23',
                    'official_url': atlas['people'][0]['official_url'],
                    'roster_source_url': entry['roster_source_url'],
                })
                with self.assertRaisesRegex(AssertionError, 'explicit personal profile'):
                    roster_builder.prepare_rosters(roster, atlas)
                entry['profile_identity_evidence'][evidence_key] = [entry['official_profile_url'], atlas['people'][0]['official_url']]
                prepared = roster_builder.prepare_rosters(roster, atlas)['entries'][0]
                self.assertEqual(prepared['verified_person_id'], 'test-person')
                self.assertEqual(prepared['candidate_person_ids'], [])
                self.assertFalse(prepared['automatic_merge'])
                entry['profile_identity_evidence'][evidence_key][-1] = 'https://unrelated.example.test/person'
                with self.assertRaisesRegex(AssertionError, 'explicit personal profile'):
                    roster_builder.prepare_rosters(roster, atlas)

    def test_new_batches_cannot_be_silently_promoted(self):
        for batch_id in ('harbin-002', 'weihai-003'):
            roster, atlas = self.fixture()
            roster['entries'][0].update(batch_id=batch_id, profile_identity_verified=True, verified_person_id='test-person')
            with self.assertRaisesRegex(AssertionError, 'remain unverified'):
                roster_builder.prepare_rosters(roster, atlas)

    def test_auto_merge_is_rejected(self):
        roster, atlas = self.fixture()
        roster['entries'][0]['automatic_merge'] = True
        with self.assertRaisesRegex(AssertionError, 'must not auto-merge'):
            roster_builder.prepare_rosters(roster, atlas)

    def test_worksheet_matrices_include_evidence_and_do_not_write_files(self):
        original = copy.deepcopy(self.rosters)
        tables = roster_builder.roster_tables(self.rosters, self.atlas)
        self.assertEqual(list(tables), ['待核对名录', '覆盖说明', '分类覆盖', '冲突记录', '消歧候选', '批次来源', '排除与待查'])
        self.assertEqual(len(tables['待核对名录']), 968)
        self.assertEqual(len(tables['分类覆盖']), 68)
        self.assertEqual(len(tables['冲突记录']), 28)
        self.assertEqual(len(tables['消歧候选']), 53)
        self.assertEqual(len(tables['排除与待查']), 12)
        self.assertIn('原始链接（含占位，仅证据）', tables['待核对名录'][0])
        self.assertIn('经独立核验的档案ID', tables['待核对名录'][0])
        self.assertIn('名录原始资格或身份附注（不是师承关系）', tables['待核对名录'][0])
        self.assertIn('名录声明更新日期（非本轮核验日期）', tables['待核对名录'][0])
        dates_column = tables['待核对名录'][0].index('名录声明更新日期（非本轮核验日期）')
        self.assertTrue(any(row[dates_column] == '2023年12月26日' for row in tables['待核对名录'][1:]))
        self.assertEqual(self.rosters, original)

    def test_data_only_build_never_constructs_xlsx(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'data').mkdir()
            (root / 'data/rosters.json').write_text(json.dumps(self.rosters, ensure_ascii=False))
            with mock.patch.object(roster_builder, 'ROOT', root), mock.patch('openpyxl.Workbook', side_effect=AssertionError('XLSX creation forbidden')):
                tables = roster_builder.build_rosters(self.atlas, generate_excel=False)
            self.assertEqual(len(tables['待核对名录']), 968)
            self.assertFalse(list(root.rglob('*.xlsx')))
            result = json.loads((root / 'site/rosters.json').read_text())
            self.assertEqual(len(result['entries']), 967)
            self.assertEqual(result['dedup_candidates'], self.rosters['dedup_candidates'])
            with (root / 'site/exports/待核对名录.csv').open(encoding='utf-8-sig') as file:
                self.assertEqual(len(list(csv.reader(file))), 968)


if __name__ == '__main__':
    unittest.main()
