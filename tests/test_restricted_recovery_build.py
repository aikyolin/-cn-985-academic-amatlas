"""Synthetic capability tests only. Never run normal build or real generators."""
import copy
import hashlib
import importlib.util
import pathlib
import sys
import unittest
import subprocess
import ast
from unittest.mock import patch

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import restricted_recovery_build as driver


class RestrictedScopeTests(unittest.TestCase):
    def setUp(self):
        schools = sorted(driver.APPROVED_SCHOOLS)
        self.old = [{'person_id': f'old-{i}'} for i in range(1026)]
        self.new = [{'person_id': f'new-{i}', 'school_id': schools[i % 24], 'department_id': schools[i % 24] + '-dept'} for i in range(123)]
        self.baseline = {'people': copy.deepcopy(self.old), 'org_units': [], 'profile_batches': [], 'fixed': 'unchanged'}
        self.atlas = {**copy.deepcopy(self.baseline), 'people': self.old + self.new}
        self.plan = {'status': 'NEW_RECOVERY_RESTRICTED_SCOPE_APPROVED', 'base_commit': driver.BASE_COMMIT, 'base_tree': driver.BASE_TREE,
                     'school_ids': schools, 'person_ids': [p['person_id'] for p in self.new], 'department_ids': [s + '-dept' for s in schools]}
        self.exports = [{'department_id': s + '-dept', 'school_id': s} for s in schools] + [{'department_id': 'xmu-untouched', 'school_id': 'xmu'}]

    def validate(self):
        # Stub pure export inventory, not file output or validation under test.
        with patch.object(driver.build, 'department_exports', return_value=self.exports):
            return driver.validate_scope(self.plan, self.atlas, self.baseline)

    def test_explicit_scope_selects_only_fixed_departments_keeps_all_exports(self):
        all_exports, selected = self.validate()
        self.assertEqual(all_exports, self.exports)
        self.assertEqual(len(selected), 24)
        self.assertNotIn('xmu', {e['school_id'] for e in selected})

    def test_empty_duplicate_unknown_or_missing_school_fails_closed(self):
        original = self.plan['school_ids'][:]
        for value in ([], original + [original[0]], original[:-1], original[:-1] + ['xmu'], None):
            with self.subTest(value=value):
                self.plan['school_ids'] = value
                with self.assertRaises(ValueError): self.validate()

    def test_no_implicit_approval_or_default_fallback(self):
        self.plan.pop('status')
        with self.assertRaises(ValueError): self.validate()

    def test_wrong_baseline_tree_fails(self):
        self.plan['base_tree'] = '0' * 40
        with self.assertRaises(ValueError): self.validate()

    def test_fixed_department_omission_or_addition_fails(self):
        original = self.plan['department_ids'][:]
        for value in (original[:-1], original + ['xmu-untouched'], original + [original[0]]):
            self.plan['department_ids'] = value
            with self.assertRaises(ValueError): self.validate()

    def test_old_fact_mutation_and_new_order_mutation_fail(self):
        self.atlas['people'][0] = {'person_id': 'modified'}
        with self.assertRaises(ValueError): self.validate()
        self.atlas['people'][0] = self.baseline['people'][0]
        self.plan['person_ids'] = list(reversed(self.plan['person_ids']))
        with self.assertRaises(ValueError): self.validate()

    def test_root_fact_mutation_fails(self):
        self.atlas['fixed'] = 'changed'
        with self.assertRaises(ValueError): self.validate()

    def test_department_cross_school_fails(self):
        self.exports[0]['school_id'] = 'xmu'
        with self.assertRaises(ValueError): self.validate()

    def guard(self):
        guard = driver.RestrictedIOGuard(ROOT)
        guard.configure([ROOT / 'site/exports/bnu-dept.xlsx'], ROOT / 'controlled-test-temporary')
        return guard

    def test_all_nonallowlisted_workbook_reads_writes_denied(self):
        guard = self.guard()
        for name in ('xmu-synthetic.xlsx', 'unlisted.xlsx', 'bnu-other.xlsx', 'unlisted.xlsm', 'unlisted.xlsb', 'unlisted.xls'):
            for flags in (0, 1, 2, 64, 512):
                with self.subTest(name=name, flags=flags), self.assertRaises(PermissionError):
                    guard('open', (str(ROOT / 'site/exports' / name), None, flags))
        guard('open', (str(ROOT / 'site/exports/bnu-dept.xlsx'), 'r', 0))
        guard('open', (str(ROOT / 'site/people/xmu.json'), 'r', 0))

    def test_rename_to_unlisted_workbook_denied_without_io(self):
        guard = self.guard()
        temp = ROOT / 'site/exports/synthetic.xlsx.tmp'
        guard('tempfile.mkstemp', (str(temp),))
        guard('open', (str(temp), 'w', 1))
        guard('os.rename', (str(temp), str(ROOT / 'site/exports/bnu-dept.xlsx'), -1, -1))
        for target in ('xmu-synthetic.xlsx', 'unlisted.xlsx'):
            with self.assertRaises(PermissionError):
                guard('os.rename', (str(temp), str(ROOT / 'site/exports' / target), -1, -1))

    def test_unregistered_temp_unlink_link_and_mutations_denied(self):
        guard = self.guard()
        forbidden = str(ROOT / 'site/exports/xmu-synthetic.xlsx')
        for event, args in [('os.remove', (forbidden, -1)), ('os.link', ('anything', forbidden, -1, -1)), ('os.symlink', ('anything', forbidden, -1)), ('os.chmod', (forbidden, 384, -1)), ('tempfile.mkstemp', (str(ROOT / 'unapproved.tmp'),)), ('os.rename', ('unregistered.tmp', str(ROOT / 'site/exports/bnu-dept.xlsx'), -1, -1))]:
            with self.subTest(event=event), self.assertRaises(PermissionError): guard(event, args)

    def test_approved_school_cannot_use_other_school_department_prefix(self):
        self.new[0]['department_id'] = 'xmu-synthetic'
        self.plan['department_ids'].append('xmu-synthetic')
        self.exports.append({'department_id': 'xmu-synthetic', 'school_id': self.new[0]['school_id']})
        with self.assertRaises(ValueError): self.validate()

    def test_real_open_denied_before_creation(self):
        code = "import sys;sys.path.insert(0, 'scripts');import restricted_recovery_build as d;sys.addaudithook(d.RestrictedIOGuard(d.ROOT));open('site/exports/xmu-forbidden-test.xlsx','wb')"
        result = subprocess.run([sys.executable, '-B', '-c', code], cwd=ROOT, text=True, capture_output=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('PermissionError', result.stderr)
        self.assertFalse((ROOT / 'site/exports/xmu-forbidden-test.xlsx').exists())

    def test_configure_required_before_temporary_registration(self):
        guard = driver.RestrictedIOGuard(ROOT)
        for path in ('site/exports/synthetic.xlsx.tmp', 'site/.atlas-write-test'):
            with self.assertRaises(PermissionError):
                guard('tempfile.mkstemp', (str(ROOT / path),))

    def test_directory_relative_mutations_fail_closed(self):
        guard = self.guard()
        path = str(ROOT / 'site/exports/bnu-dept.xlsx')
        events = [('os.remove', (path, 9)), ('os.mkdir', (str(ROOT / 'site'), 511, 9)), ('os.rmdir', (str(ROOT / 'controlled-test-temporary'), 9)), ('os.chmod', (path, 384, 9)), ('os.chown', (path, 1, 1, 9)), ('os.utime', (path, None, None, 9)), ('os.rename', (path, path, 9, -1))]
        for event, args in events:
            with self.subTest(event=event), self.assertRaises(PermissionError): guard(event, args)

    def test_storage_required_directories_only(self):
        guard = self.guard()
        for path in ('site', 'site/people', 'site/exports'):
            guard('os.mkdir', (str(ROOT / path), 511, -1))
        with self.assertRaises(PermissionError):
            guard('os.mkdir', (str(ROOT / 'not-approved'), 511, -1))

    def test_success_receipt_written_after_terminal_cleanup(self):
        source = (ROOT / 'scripts/restricted_recovery_build.py').read_text()
        self.assertLess(source.index('temporary_root.rmdir()'), source.index('receipt_path.write_text('))

    def test_driver_never_calls_unrestricted_build_entry(self):
        tree = ast.parse((ROOT / 'scripts/restricted_recovery_build.py').read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                self.assertNotEqual(ast.unparse(node.func), 'build.build')

    def test_department_table_degree_header_only_changes_wording(self):
        person = {'person_id': 'bnu-synthetic', 'school_id': 'bnu', 'department_id': 'bnu-dept',
                  'name': 'Synthetic', 'department': 'Synthetic department', 'official_url': 'https://example.org/person',
                  'unknowns': [], 'sources': [], 'appointments': [], 'mentors': [], 'publications': [],
                  'education': [{'event_kind': 'degree', 'degree': '博士', 'institution': 'Synthetic institution', 'degree_awarded': True}]}
        tables = dict(driver.build.department_tables([person], '2000-01-01', [{'id': 'bnu', 'official_name': 'Synthetic university'}]))
        header = tables['经历'][0]
        self.assertIn('来源记载学位', header)
        self.assertNotIn('确证授位', header)
        self.assertIs(tables['经历'][1][header.index('来源记载学位')], True)
        self.assertEqual(list(tables), ['总览', '经历', '导师', '论文', '来源'])
        self.assertEqual(tables['总览'][0][5], '来源说明与待核事项')

    def test_original_default_build_and_runtime_bytes_unchanged(self):
        # Exact public Git blob IDs, not hashes generated from the current candidate.
        pins = ORIGINAL_PINS
        for rel, expected in pins.items():
            raw = (ROOT / rel).read_bytes()
            if rel in REVIEWED_LITERAL_INVERSE:
                spec = REVIEWED_LITERAL_INVERSE[rel]
                self.assertEqual(hashlib.sha256(raw).hexdigest(), spec['proposed_sha256'], rel)
                text = raw.decode()
                for item in reversed(spec['changes']):
                    self.assertEqual(text.count(item['after']), item['count'], rel)
                    text = text.replace(item['after'], item['before'])
                raw = text.encode()
                self.assertEqual(hashlib.sha256(raw).hexdigest(), spec['original_sha256'], rel)
            self.assertEqual(hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest(), expected, rel)


REVIEWED_LITERAL_INVERSE = {'site/app.js': {'changes': [{'before': '未记录确证本科学位', 'after': '未记录来源明确记载的本科学位', 'count': 1}, {'before': '985 按历史39校名单；仅确证授位参与学历筛选，访问/攻读单列。', 'after': '985 按历史39校名单；学历筛选仅显示来源明确记载的学位，访问/攻读单列。', 'count': 1}, {'before': '未记录确证授位', 'after': '未记录来源明确记载的学位', 'count': 1}, {'before': '不参与确证学历筛选。', 'after': '不参与来源明确记载的学位筛选。', 'count': 1}, {'before': '非确证授位事件，不参与学历筛选', 'after': '本事件未明确记载获授学位，不参与学历筛选', 'count': 1}, {'before': '本人 → 学习／研究阶段 → 有直接来源的导师。虚线仅表示资料缺项，不是已确认师承；共同作者不自动视为导师。', 'after': '本人 → 学习／研究阶段 → 来源记载的导师关系。关系可能依据保留的来源摘要，不等同于论文原件认证；阶段未明确时不推定学位阶段。虚线仅表示资料缺项，不是关系认定；共同作者不自动视为导师。', 'count': 1}, {'before': '只有授位事件且授位已确证的记录参与筛选。未收录确证授位不等于没有硕士学位。', 'after': '只有来源明确记载本人获授或持有学位的记录参与筛选；不表示本轮独立证书认证或重新读取原网页。未收录该类记载不等于没有硕士学位。', 'count': 1}, {'before': '同一条确证授位记录', 'after': '同一条来源明确记载学位的记录', 'count': 1}, {'before': '仅保留有直接证据的指导关系。共同作者、通讯作者、同实验室均不能单独证明师承。', 'after': '保留来源明确记载的指导关系，可能依据保留摘要；关系记载不等同于学位论文原件核验，证据类型与限制以各条来源说明为准。共同作者、通讯作者、同实验室均不能单独证明师承。', 'count': 1}, {'before': '核验与缺项', 'after': '来源说明与待核事项', 'count': 1}], 'original_sha256': '2906bda613c1c5b660bbfc1b5495c3228c3f972fb1f84b8640f11c35dfacdbdb', 'proposed_sha256': '9fa99c47453ae9af839db6f9cf4774823c81175f1585085fc835ed87c38cf8c8'}, 'site/model.js': {'changes': [{'before': '未记录确证授位', 'after': '未记录来源明确记载的学位', 'count': 2}], 'original_sha256': '7ab0158271185d9945b4e32a73ceaddd055feede30049023acd3a974e1b021ce', 'proposed_sha256': '6b49ce4b71025ee16e1b22c8f7b28ef44e85274eaa06b6cf24ea79d3461d4fce'}, 'scripts/build.py': {'changes': [{'before': "'确证授位'", 'after': "'来源记载学位'", 'count': 1}, {'before': "'缺项与冲突'", 'after': "'来源说明与待核事项'", 'count': 1}], 'original_sha256': '96493bd5b27ea91a42a515a327f9ad110dfd36817a9f55f0f9f8d83cd1d3d971', 'proposed_sha256': '23de4e82dd248840724a318e5241b3024d8061a4713340b55bdc5eb4253b72b5'}}

ORIGINAL_PINS = {'schema/atlas.schema.json': '8f637202624cbda06bccd31111edc9ed5a5a4528', 'scripts/atlas_storage.py': '2a0e20b685a89d8cf4a731019a29bce59b5ff033', 'scripts/build.py': '0800ded234fa78ea4b1b18183eb70ac1d6076d52', 'scripts/build_rosters.py': '04b404215c38f80acf176dcfefca553254429c72', 'scripts/public_metadata.py': 'aed5ceef9f24cb12d828a64a7ee9530d5190172d', 'site/app.js': '5c36d65328a28e7583212b13be0bab00936a3ba3', 'site/atlas-loader.js': '387852ff0c764fb493f1bde097a95ad2645c9e18', 'site/model.js': '04bf8724f3aa091934e24c1a10f5d9d1980f29e1', 'site/rosters.js': '42f74f8955bec1ea5f0ee38aeba6a248f8690e99', 'site/universities.js': 'e54181e4f985466410e7c77db171b3e96fe80bbb', 'tests/published_fixture.py': 'cfeba24688943fc402cee40c397e44af9a0ba7bc'}

if __name__ == '__main__':
    unittest.main()
