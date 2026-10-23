"""Synthetic mentor navigation boundaries; table generation only, never XLSX writes."""
import copy
import pathlib
import sys
import unittest
from unittest import mock

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / 'scripts'))
import build


class MentorNavigationTests(unittest.TestCase):
    def mentor(self, **changes):
        return dict({
            'name': '测试导师', 'type': 'doctoral_advisor', 'type_label': '博士导师',
            'employment_status': 'active_officially_listed',
            'employment_status_note': '任职来源保留原文。',
            'official_url': 'https://example.edu.test/profile',
            'source_url': 'https://example.edu.test/relationship',
            'profile_source_url': 'https://example.edu.test/employment',
        }, **changes)

    def export(self, mentor):
        person = {
            'name': '测试学生', 'school_id': 'test-school', 'department': '测试院系',
            'official_url': 'https://example.edu.test/student', 'unknowns': [],
            'education': [], 'appointments': [], 'mentors': [mentor],
            'publications': [], 'sources': [],
        }
        before = copy.deepcopy(person)
        with mock.patch.object(build, 'Workbook', side_effect=AssertionError('XLSX writing forbidden')):
            rows = dict(build.department_tables([person], '2026-10-23', [
                {'id': 'test-school', 'official_name': '测试学校'}
            ]))['导师']
        self.assertEqual(person, before)
        self.assertEqual(rows[0], ['姓名', '导师姓名', '关系类型', '阶段', '简介', '在职状态', '状态说明', '已核在职主页', '关系来源', '任职来源', '所属学校ID', '所属学校'])
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[1][2], '博士导师')
        self.assertEqual(rows[1][5], mentor['employment_status'])
        self.assertEqual(rows[1][8:10], [mentor['source_url'], mentor['profile_source_url']])
        self.assertEqual(rows[1][-2:], ['test-school', '测试学校'])
        return rows[1]

    def test_each_explicit_false_vetoes_active_shortcut(self):
        for flags in [
            {'navigation_verified': False}, {'quick_link_eligible': False},
            {'navigation_verified': False, 'quick_link_eligible': True},
            {'navigation_verified': True, 'quick_link_eligible': False},
            {'navigation_verified': False, 'quick_link_eligible': False},
        ]:
            with self.subTest(flags=flags):
                mentor = self.mentor(**flags)
                self.assertEqual(build.mentor_official_url(mentor), '')
                row = self.export(mentor)
                self.assertEqual(row[7], '')
                self.assertIn(mentor['employment_status_note'], row[6])
                self.assertIn('任职已核实；导师主页访问未核实，暂不提供快捷链接。', row[6])

    def test_legacy_absent_flags_and_explicit_true_keep_active_url(self):
        for flags in [{}, {'quick_link_eligible': True}, {'navigation_verified': True},
                      {'quick_link_eligible': True, 'navigation_verified': True}]:
            with self.subTest(flags=flags):
                mentor = self.mentor(**flags)
                self.assertEqual(build.mentor_official_url(mentor), mentor['official_url'])
                row = self.export(mentor)
                self.assertEqual(row[7], mentor['official_url'])
                self.assertEqual(row[6], mentor['employment_status_note'])
                self.assertEqual(build.mentor_navigation_notice(mentor), '')

    def test_active_403_keeps_employment_and_precise_reason_not_a_shortcut(self):
        mentor = self.mentor(navigation_verified=False, quick_link_eligible=False,
                            profile_navigation_unavailable_reason='个人主页访问返回 403，未核实公开导航可用性。')
        row = self.export(mentor)
        self.assertEqual(row[7], '')
        self.assertIn('任职已核实；' + mentor['profile_navigation_unavailable_reason'], row[6])
        self.assertEqual(mentor['official_url'], 'https://example.edu.test/profile')

    def test_retired_or_nonactive_never_gain_shortcuts_from_true_flags(self):
        for status in ['retired', 'retired_officially_listed', 'emeritus_officially_listed', 'unknown', 'deceased']:
            with self.subTest(status=status):
                mentor = self.mentor(employment_status=status, quick_link_eligible=True, navigation_verified=True)
                self.assertEqual(build.mentor_official_url(mentor), '')
                self.assertEqual(build.mentor_navigation_notice(mentor), '')
                row = self.export(mentor)
                self.assertEqual(row[7], '')
                self.assertEqual(row[6], mentor['employment_status_note'])

    def test_blank_reason_falls_back_and_same_url_employment_evidence_remains(self):
        for reason in [None, '', '   ']:
            mentor = self.mentor(navigation_verified=False, profile_navigation_unavailable_reason=reason)
            mentor['profile_source_url'] = mentor['official_url']
            row = self.export(mentor)
            self.assertEqual(row[7], '')
            self.assertEqual(row[9], mentor['official_url'])
            self.assertIn('任职已核实；导师主页访问未核实，暂不提供快捷链接。', row[6])

    def test_unsafe_or_malformed_url_fails_closed_even_with_true_flags(self):
        for url in [None, '', 'javascript:alert(1)', 'data:text/html,test', 'file:///etc/passwd',
                    'https://[invalid', 'https://exa mple.edu/p', 'https://example.edu:bad/p', 'https://user@:443/p']:
            with self.subTest(url=url):
                mentor = self.mentor(official_url=url, quick_link_eligible=True, navigation_verified=True)
                self.assertEqual(build.mentor_official_url(mentor), '')
                self.assertEqual(self.export(mentor)[7], '')
        self.assertEqual(build.mentor_official_url(None), '')


if __name__ == '__main__':
    unittest.main()
