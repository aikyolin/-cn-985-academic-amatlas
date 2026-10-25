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
SCU_MAPPING_SHA256 = 'c865a6548faf84d525bf2d42c2f6df1584a1e27e6a4298f845180fe3c656addf'
UESTC_MAPPING_SHA256 = '3237a4596f84af20c149ac69f9e30917fe7f7df31fce021c5005a11cab18d1c3'
HNU_MAPPING_SHA256 = '5415b445dde9ab09dd38a97fc0f1d0136c08b2fa8c2667d32ee35b4301dff4c6'
BNU_MAPPING_SHA256 = '9c3004d31ae1327e5c7ffec1251fc71be3b6417606b0fdc6fe583f6d7e4b36d3'
TJU_MAPPING_SHA256 = 'f82df77db84d07c64b594b46047ed775c45a1001734a06493035094e2473bc1f'
NKU_MAPPING_SHA256 = '6b999966d28b6396f31074ececc75c7e152e1dcedcd22a3d7b77b82ccde41aae'
DLUT_MAPPING_SHA256 = 'a579968911068d28b5371ff96d3ba4557d18725d0401d32ae236df092f359909'
JLU_MAPPING_SHA256 = 'f010fb82e3ad522830c7c79b49fc06a0042e1e47daf1d424d3c9359641dc4856'
SDU_MAPPING_SHA256 = 'ea4ea15f0fa0a691d113aac302779bde3aa2be5589d6a5b33751006581619743'
CSU_MAPPING_SHA256 = '0c227fdedfe70344f92db0fb32e905a57e60979fb28f35a00a70a29effe76609'
CSU_IDS = ['csu-zhangligang', 'csu-daiyu', 'csu-yanlei', 'csu-wangmiao', 'csu-fenghui', 'csu-denglu', 'csu-yiqiao', 'csu-guocan', 'csu-wenyu', 'csu-yaohailin', 'csu-yanjiexiong', 'csu-fengjie']
SDU_IDS = ['sdu-zhangna', 'sdu-wangliping', 'sdu-zhanghaiyan', 'sdu-sunlixin', 'sdu-yidonglan', 'sdu-wangkefang', 'sdu-liyuli', 'sdu-fanghui', 'sdu-lijing-nursing', 'sdu-lichaofan-policy', 'sdu-luhaobin', 'sdu-liusenlin']
JLU_IDS = ['jlu-anni', 'jlu-anshengji', 'jlu-wangting-economics', 'jlu-lvxuanru', 'jlu-liwenjun', 'jlu-guochunfang', 'jlu-zhouxin', 'jlu-wangjuan', 'jlu-jinlina', 'jlu-yuxianfeng', 'jlu-sunwanchun', 'jlu-wangdehui']
DLUT_IDS = ['dlut-zhangjialiang', 'dlut-zhangrui', 'dlut-cuimiao', 'dlut-wanghuanming', 'dlut-zhangwei1', 'dlut-liulinlin-law', 'dlut-suyongjian-education', 'dlut-liumengyang', 'dlut-zhouwenjie-art', 'dlut-lichong-higher-education', 'dlut-lijunfeng', 'dlut-mahui']
NKU_IDS = ['nku-lingfeng', 'nku-zhangjiayu-philosophy', 'nku-luzhaoyong', 'nku-xuexue', 'nku-yangzhenhong', 'nku-zhangzhihong', 'nku-caishengxia', 'nku-maodaqing-medical', 'nku-guanyongqiang-economic-history', 'nankai-haolan', 'nankai-luozhenya', 'nankai-liulili']
TJU_IDS = ['tju-xuchunjian', 'tju-zhaobohang', 'tju-wenxiaotong', 'tju-mawenchao', 'tju-shizhiyuan', 'tju-tanhao', 'tju-zhaokuo', 'tju-chentong', 'tju-liuconghong', 'tju-zhaoyanjun-pharmaceutics', 'tju-daisong', 'tju-hanzhongjie']
BNU_IDS = ['bnu-hanxue', 'bnu-hufengqin', 'bnu-liushaomin', 'bnu-sudianna', 'bnu-wangchen-music', 'bnu-guo-jia-wave169', 'bnu-wang-cixiao-wave190', 'bnu-zeng-xianglong-wave190', 'bnu-lichong', 'bnu-luoxinhui', 'bnu-nitengda', 'bnu-zhanglu']
HNU_IDS = ['hnu-huyueqiang', 'hnu-liujie', 'hnu-libing-education-history', 'hnu-hubicheng', 'hnu-yuanxiang-design', 'hnu-yuanzhaohui-architecture', 'hnu-yanjianfei', 'hnu-sunqingjuan', 'hnu-tanhaibo', 'hnu-huying']
UESTC_IDS = ['uestc-shangjizheng', 'uestc-shenhua', 'uestc-fangjiaming', 'uestc-kangjian', 'uestc-qianhao', 'uestc-liangjian', 'uestc-nidebing', 'uestc-dengchenliang', 'uestc-zhouguanyu', 'uestc-zhupeiyong']
SCU_IDS = ['scu-baishibing', 'scu-baojianjun', 'scu-caoya', 'scu-longbingwei', 'scu-fanzhenxin', 'scu-xuliang', 'scu-fengxianqiong', 'scu-penghua-classics', 'scu-lifei', 'scu-huangzongxian', 'scu-wuyongqiang']
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

def scu_mapping():
    raw = (ROOT / 'tests/fixtures/independent-scu11-source-mapping.json').read_bytes()
    assert hashlib.sha256(raw).hexdigest() == SCU_MAPPING_SHA256, 'Reviewed SCU eleven-person mapping changed'
    return json.loads(raw)

def uestc_mapping():
    raw = (ROOT / 'tests/fixtures/independent-uestc10-source-mapping.json').read_bytes()
    assert hashlib.sha256(raw).hexdigest() == UESTC_MAPPING_SHA256, 'Reviewed UESTC ten-person mapping changed'
    return json.loads(raw)

def hnu_mapping():
    raw = (ROOT / 'tests/fixtures/independent-hnu10-source-mapping.json').read_bytes()
    assert hashlib.sha256(raw).hexdigest() == HNU_MAPPING_SHA256, 'Reviewed HNU ten-person mapping changed'
    return json.loads(raw)

def bnu_mapping():
    raw = (ROOT / 'tests/fixtures/independent-bnu12-source-mapping.json').read_bytes()
    assert hashlib.sha256(raw).hexdigest() == BNU_MAPPING_SHA256, 'Reviewed BNU twelve-person mapping changed'
    return json.loads(raw)

def tju_mapping():
    raw = (ROOT / 'tests/fixtures/independent-tju12-source-mapping.json').read_bytes()
    assert hashlib.sha256(raw).hexdigest() == TJU_MAPPING_SHA256, 'Reviewed TJU twelve-person mapping changed'
    return json.loads(raw)

def nku_mapping():
    raw = (ROOT / 'tests/fixtures/independent-nku12-source-mapping.json').read_bytes()
    assert hashlib.sha256(raw).hexdigest() == NKU_MAPPING_SHA256, 'Reviewed NKU twelve-person mapping changed'
    return json.loads(raw)

def dlut_mapping():
    raw = (ROOT / 'tests/fixtures/independent-dlut12-source-mapping.json').read_bytes()
    assert hashlib.sha256(raw).hexdigest() == DLUT_MAPPING_SHA256, 'Reviewed DLUT twelve-person mapping changed'
    return json.loads(raw)

def jlu_mapping():
    raw = (ROOT / 'tests/fixtures/independent-jlu12-source-mapping.json').read_bytes()
    assert hashlib.sha256(raw).hexdigest() == JLU_MAPPING_SHA256, 'Reviewed JLU twelve-person mapping changed'
    return json.loads(raw)

def sdu_mapping():
    raw = (ROOT / 'tests/fixtures/independent-sdu12-source-mapping.json').read_bytes()
    assert hashlib.sha256(raw).hexdigest() == SDU_MAPPING_SHA256, 'Reviewed SDU twelve-person mapping changed'
    return json.loads(raw)

def csu_mapping():
    raw = (ROOT / 'tests/fixtures/independent-csu12-source-mapping.json').read_bytes()
    assert hashlib.sha256(raw).hexdigest() == CSU_MAPPING_SHA256, 'Reviewed CSU twelve-person mapping changed'
    return json.loads(raw)

def reviewed_additions():
    first, second, third, fourth, fifth, sixth, seventh, eighth, ninth, tenth, eleventh, twelfth, thirteenth = mapping(), next_mapping(), seu_mapping(), scu_mapping(), uestc_mapping(), hnu_mapping(), bnu_mapping(), tju_mapping(), nku_mapping(), dlut_mapping(), jlu_mapping(), sdu_mapping(), csu_mapping()
    assert [p['person_id'] for p in first['people']] == FIRST_IDS
    assert [p['person_id'] for p in second['people']] == NEXT_IDS
    assert [p['person_id'] for p in third['people']] == SEU_IDS
    assert [p['person_id'] for p in fourth['people']] == SCU_IDS
    assert [p['person_id'] for p in fifth['people']] == UESTC_IDS
    assert [p['person_id'] for p in sixth['people']] == HNU_IDS
    assert [p['person_id'] for p in seventh['people']] == BNU_IDS
    assert [p['person_id'] for p in eighth['people']] == TJU_IDS
    assert [p['person_id'] for p in ninth['people']] == NKU_IDS
    assert [p['person_id'] for p in tenth['people']] == DLUT_IDS
    assert [p['person_id'] for p in eleventh['people']] == JLU_IDS
    assert [p['person_id'] for p in twelfth['people']] == SDU_IDS
    assert [p['person_id'] for p in thirteenth['people']] == CSU_IDS
    return {key: first[key] + second[key] + third[key] + fourth[key] + fifth[key] + sixth[key] + seventh[key] + eighth[key] + ninth[key] + tenth[key] + eleventh[key] + twelfth[key] + thirteenth[key] for key in ('people', 'org_units', 'profile_batches')}

def validate_append(current, previous, additions):
    assert set(current) == set(previous), 'Unlisted canonical root fields'
    for key, value in previous.items():
        if key in ('people', 'org_units', 'profile_batches'):
            assert current[key] == value + additions[key], 'Historical or new source fact changed: ' + key
        else:
            assert current[key] == value, 'Unlisted change: ' + key
    assert [x['person_id'] for x in current['people'][len(previous['people']):]] == FIRST_IDS + NEXT_IDS + SEU_IDS + SCU_IDS + UESTC_IDS + HNU_IDS + BNU_IDS + TJU_IDS + NKU_IDS + DLUT_IDS + JLU_IDS + SDU_IDS + CSU_IDS
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

    def test_published_634_prefix_is_independent_fixed_612_plus_reviewed_previous_mappings(self):
        first, second, third = mapping(), next_mapping(), seu_mapping()
        self.assertEqual(len(self.previous['people']) + len(first['people']) + len(second['people']) + len(third['people']), 634)
        for key in ('people', 'org_units', 'profile_batches'):
            expected = self.previous[key] + first[key] + second[key] + third[key]
            self.assertEqual(self.actual[key][:len(expected)], expected, key)

    def test_published_645_prefix_preserves_independent_previous_source_mappings(self):
        previous_mappings = (mapping(), next_mapping(), seu_mapping(), scu_mapping())
        self.assertEqual(len(self.previous['people']) + sum(len(m['people']) for m in previous_mappings), 645)
        for key in ('people', 'org_units', 'profile_batches'):
            expected = self.previous[key] + [item for m in previous_mappings for item in m[key]]
            self.assertEqual(self.actual[key][:len(expected)], expected, key)

    def test_published_655_prefix_preserves_all_previous_source_mappings(self):
        previous_mappings = (mapping(), next_mapping(), seu_mapping(), scu_mapping(), uestc_mapping())
        self.assertEqual(len(self.previous['people']) + sum(len(m['people']) for m in previous_mappings), 655)
        for key in ('people', 'org_units', 'profile_batches'):
            expected = self.previous[key] + [item for m in previous_mappings for item in m[key]]
            self.assertEqual(self.actual[key][:len(expected)], expected, key)

    def test_published_665_prefix_preserves_all_previous_source_mappings(self):
        previous_mappings = (mapping(), next_mapping(), seu_mapping(), scu_mapping(), uestc_mapping(), hnu_mapping())
        self.assertEqual(len(self.previous['people']) + sum(len(m['people']) for m in previous_mappings), 665)
        for key in ('people', 'org_units', 'profile_batches'):
            expected = self.previous[key] + [item for m in previous_mappings for item in m[key]]
            self.assertEqual(self.actual[key][:len(expected)], expected, key)

    def test_published_677_prefix_preserves_all_previous_source_mappings(self):
        previous_mappings = (mapping(), next_mapping(), seu_mapping(), scu_mapping(), uestc_mapping(), hnu_mapping(), bnu_mapping())
        self.assertEqual(len(self.previous['people']) + sum(len(m['people']) for m in previous_mappings), 677)
        for key in ('people', 'org_units', 'profile_batches'):
            expected = self.previous[key] + [item for m in previous_mappings for item in m[key]]
            self.assertEqual(self.actual[key][:len(expected)], expected, key)

    def test_published_689_prefix_preserves_all_previous_source_mappings(self):
        previous_mappings = (mapping(), next_mapping(), seu_mapping(), scu_mapping(), uestc_mapping(), hnu_mapping(), bnu_mapping(), tju_mapping())
        self.assertEqual(len(self.previous['people']) + sum(len(m['people']) for m in previous_mappings), 689)
        for key in ('people', 'org_units', 'profile_batches'):
            expected = self.previous[key] + [item for m in previous_mappings for item in m[key]]
            self.assertEqual(self.actual[key][:len(expected)], expected, key)

    def test_published_701_prefix_preserves_all_previous_source_mappings(self):
        previous_mappings = (mapping(), next_mapping(), seu_mapping(), scu_mapping(), uestc_mapping(), hnu_mapping(), bnu_mapping(), tju_mapping(), nku_mapping())
        self.assertEqual(len(self.previous['people']) + sum(len(m['people']) for m in previous_mappings), 701)
        for key in ('people', 'org_units', 'profile_batches'):
            expected = self.previous[key] + [item for m in previous_mappings for item in m[key]]
            self.assertEqual(self.actual[key][:len(expected)], expected, key)

    def test_published_713_prefix_preserves_all_previous_source_mappings(self):
        previous_mappings = (mapping(), next_mapping(), seu_mapping(), scu_mapping(), uestc_mapping(), hnu_mapping(), bnu_mapping(), tju_mapping(), nku_mapping(), dlut_mapping())
        self.assertEqual(len(self.previous['people']) + sum(len(m['people']) for m in previous_mappings), 713)
        for key in ('people', 'org_units', 'profile_batches'):
            expected = self.previous[key] + [item for m in previous_mappings for item in m[key]]
            self.assertEqual(self.actual[key][:len(expected)], expected, key)

    def test_published_725_prefix_preserves_all_previous_source_mappings(self):
        previous_mappings = (mapping(), next_mapping(), seu_mapping(), scu_mapping(), uestc_mapping(), hnu_mapping(), bnu_mapping(), tju_mapping(), nku_mapping(), dlut_mapping(), jlu_mapping())
        self.assertEqual(len(self.previous['people']) + sum(len(m['people']) for m in previous_mappings), 725)
        for key in ('people', 'org_units', 'profile_batches'):
            expected = self.previous[key] + [item for m in previous_mappings for item in m[key]]
            self.assertEqual(self.actual[key][:len(expected)], expected, key)

    def test_published_737_prefix_preserves_all_previous_source_mappings(self):
        previous_mappings = (mapping(), next_mapping(), seu_mapping(), scu_mapping(), uestc_mapping(), hnu_mapping(), bnu_mapping(), tju_mapping(), nku_mapping(), dlut_mapping(), jlu_mapping(), sdu_mapping())
        self.assertEqual(len(self.previous['people']) + sum(len(m['people']) for m in previous_mappings), 737)
        for key in ('people', 'org_units', 'profile_batches'):
            expected = self.previous[key] + [item for m in previous_mappings for item in m[key]]
            self.assertEqual(self.actual[key][:len(expected)], expected, key)

    def test_old_fact_deletion_reordering_and_unknown_promotions_fail(self):
        # Mutate each independently protected era, not just whichever person is last.
        for index in (0, 612, 614, 624, 634, 645, 655, 665, 677, 689, 701, 713, 725, 737):
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

    def test_unaffected_old_workbooks_and_roster_facts_are_unchanged(self):
        old = published_root()
        affected = {p['department_id'] for p in self.additions['people']}
        for file in (old / 'site/exports').glob('*'):
            if file.name == '待核对名录.xlsx':
                continue  # Sole global count cell is tested separately below.
            if file.stem in affected:
                continue  # Changed membership: full old/new source-derived tables tested below.
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

    def test_live_runtime_and_engines_have_only_reviewed_changes(self):
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
            # Approved representation-only optimization: the actual builder's
            # site atlas writer is compact UTF-8. Every other engine byte stays pinned.
            if rel == 'scripts/build.py':
                before = b"json.dumps(d,ensure_ascii=False,indent=2)+'\\n')"
                after = b"json.dumps(d,ensure_ascii=False,separators=(',',':'),allow_nan=False)+'\\n',encoding='utf-8')"
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
        departments = {p['department_id'] for p in next_mapping()['people'] + seu_mapping()['people'] + scu_mapping()['people'] + uestc_mapping()['people'] + hnu_mapping()['people'] + bnu_mapping()['people'] + tju_mapping()['people'] + nku_mapping()['people'] + dlut_mapping()['people'] + jlu_mapping()['people'] + sdu_mapping()['people'] + csu_mapping()['people']}
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

    def test_existing_department_old_rows_survive_member_append(self):
        from openpyxl import load_workbook
        existing = {p['department_id'] for p in self.previous['people']}
        affected = existing & {p['department_id'] for p in uestc_mapping()['people'] + tju_mapping()['people'] + nku_mapping()['people']}
        self.assertEqual(affected, {'uestc-public-administration', 'uestc-applied-math-center', 'tju-math', 'nku-economics'})
        for department in affected:
            old_people = [p for p in self.previous['people'] if p['department_id'] == department]
            for old_person in old_people:
                self.assertEqual(next(p for p in self.actual['people'] if p['person_id'] == old_person['person_id']), old_person)
            wb = load_workbook(ROOT / 'site/exports' / (department + '.xlsx'), data_only=False)
            try:
                for name, rows in build.department_tables(old_people, self.previous['updated_at'], self.previous['institutions']):
                    actual = [list(row) for row in wb[name].iter_rows(min_row=2, values_only=True)]
                    cursor = 0
                    for row in rows[1:]:
                        expected = [build.clean(value) if build.clean(value) != '' else None for value in row]
                        while cursor < len(actual) and actual[cursor] != expected:
                            cursor += 1
                        self.assertLess(cursor, len(actual), (department, name, expected))
                        cursor += 1
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
