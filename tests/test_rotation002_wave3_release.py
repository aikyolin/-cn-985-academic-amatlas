from source_date_history import historical_bytes
"""Independent release24 SYSU/SCU offline source-boundary regression.

The original sanitized package leaves/shapes and immutable release23 prefixes
are pinned independently of integration output. Runtime requires only this
release repository and normal test dependencies, never research files, raw
packages, baseline directories, network, a browser, or writes to build outputs.
This tests the selected six-person sample, not live sources or school completion.
"""
from release_history import release25_view
import copy
import hashlib
import json
import os
import pathlib
import subprocess
import sys
import unittest
from collections import Counter
from unittest import mock

sys.dont_write_bytecode = True
ROOT = pathlib.Path(os.environ.get('ACADEMIC_ATLAS_TEST_ROOT', pathlib.Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(ROOT / 'scripts'))
import build
from build_rosters import validate_rosters


def object_sha(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()).hexdigest()

SOURCE_PACKAGE_SHA256 = {'sysu': '005d3d3f0c33c71b7bc45f2cbf20718e19ff07b5c3abc0ae2eff9bea941787cf',
 'scu': '9847ea52ba380cc5d81bb8a7e5b6353dc33dfe2fd3c036de8dae17edea9a5088'}

REVIEW_SHA256 = {'sysu': '8483cafd43e013489dfc28ef020e2d37796c82af7db5512058517935df2bf1b1',
 'scu': '1cd89b87e3520869b36438d4c0510939ca2a9c99e501c86b52500120f3554aec'}

# School and audit roles are fixed by the existing school coverage ledgers.
REVIEWED_COMPANION_SHA256 = {'sysu': {'scope': '498c30a9729f9d9ea97915fdc2011721484666fc279a0993e0eaa29eeb511722',
          'qa': 'e91b74e65a85398a940708971295ce0fe464e985b2b6ae82a423ba266aa731e1'},
 'scu': {'scope': '06b9571a366cdceff6c36c52b2b5922f0b62e6626ffb8fca4043a93c88aa4fd2',
         'qa': 'cc50ac7fe73861e87507b2287b55405a7eb37dd1449e106692ca59db51876b6e'}}

BASELINE_ATLAS_PREFIXES = {'limitations': [6, 'a49996988d143a02303ec539cb493667cdc9b28a287271ae141f6cfd7b95021a'],
 'campuses': [4, 'a29d9956fbbc284b9cdafc640ac9057dd4512c2181d89780a92a6a8bf01e6505'],
 'org_units': [221, '695553a4c955ddea2a315d32b81cacb4a58047f0506092e143590348c4f6071c'],
 'people': [541, 'aba94007625193b49e971a0f70fdbc76f3f694df5a391b93db17c8a8838343c0'],
 'profile_batches': [132, 'fe55e4b455c5d23d6aeeee55f4ad4224edb802d5a72e98102ce84fd0bdf790c5'],
 'pending_people': [83, '7bf2a61c24b2737d8d175bc65545de28d54f65214313881144efaa43dcc89bb5'],
 'normalization_evidence': [13, 'd401a9ff92a19228917845cbbef4cef255973b5c2c66b6b9233e517db7166021'],
 'institutions': [39, '8234ea78331d931b8a54c5f40d4427a7844e7fcd621d0832a69e5f2df1b41848']}

BASELINE_ATLAS_UNCHANGED = {'schema_version': '5a4747fcdafec66d8d8812022e3b7d2666d886ec0e0ee7926ec8c50db40f29d5',
 'institution': '9b9fab8a1164afafcf855e8d6ccea17a09e973b8ea2fd8a4831ad681490e8d01',
 'coverage': '8301d88ec52e91fd40964298ce12e179dc0c4ca513b3a0cefa9ad57db895f597'}

BASELINE_ROSTER_PREFIXES = {'summary': [139, 'af9ab1768c3e51d73a99baf30cf940db5a5bf94a2063e1f3ffaa9884e07a3c0d'],
 'coverage': [210, 'ae50b9787836606192edc56033c7b9c522d8f89f66d92f0ecf0902fb93b9a0ee'],
 'entries': [1706, 'aaf58e44074293c6d53dd8890d6aeaf59c374e5c0256d5fe79a6b2865d7dfce2'],
 'conflicts': [30, '0f809e3a2c4ef1857b03479230f35a342b703ccf5f8a99ef032271d150c44c09'],
 'limitations': [35, '4fe8dea8da59fb3789194955a1b22aac4453cbf0e6a4d1cc2e82d172ba77c116'],
 'dedup_candidates': [60, '0a1adbff0d7b0ae2fe42cceff9a89e5e9eb6d164044456f319cfab6c9d1b1653'],
 'exclusions': [3, '89dc768c034efe9de60bb4199c92be749ea7f1bb1405daceff0e3ca88fa5228d'],
 'pending_checks': [2, '143ba1254ce843007ed487ca7f7ef2c684912b54c0580c6bb3f7157b7bc61048'],
 'source_snapshots': [36, 'bae26c4aa31edf9ee3212a7723508241f475441863f03f69a8058264ad3b81c2'],
 'batches': [105, '1dc35bef97e100e4c6c613a017e1ebc9dc50b86993bbe39d034301e767b8419a'],
 'source_observations': [1744, '87f36a7e7e173932dc3bb3847c3032df5dd331285e5672d2985d7268f948144e'],
 'consolidations': [2, '094423def9986b8e47457a6592e143f75d67eaa7647c2c346df93d54b983e4e0'],
 'supporting_method_evidence': [4, 'db4e111a865957df036ada510d96050eb5c2b39ed6635c628d48a9a2717ec547'],
 'local_mapping_corrections': [4, '9a1ccc7df1e46b7e8240c3963456fcaf0177d07ad31c051db7d1d5334a1aca1d'],
 'withdrawn_local_conflicts': [1, '8b54b3a107c8f050e3c33cc2125a710a4084b1be287fdb20db8ca392c093ed05']}

BASELINE_ROSTER_UNCHANGED = {'schema_version': '5a4747fcdafec66d8d8812022e3b7d2666d886ec0e0ee7926ec8c50db40f29d5',
 'role_interpretation': '9c1098d16b8ae13b4ef55efb781195831efdc1be68fd601aa8c4d1db41cea7c0'}

BASELINE_QUEUE_PREFIX = [217, '9a759e7a9f1083560118904eab51ab516ae977fda11c6559583e3baca2408d64']

UNCHANGED_APPLICATION_SHA256 = {'site/app.js': '0e420fef54c0dae966d883bb0aeb0fb7af05f79e8803e366ea8ece7e95ed2cd6',
 'site/index.html': '42966eb1409ce029b90d64e77e2c02977971477bade4e2a79414b4a2aef1c571',
 'site/model.js': '087ddd9e9de963f6b4497b3ec50033b1012680057d106a57b490cda4697ec79e',
 'site/rosters.js': '114e47a44f0c4b5cd100eb786604818cacc36ff073f0ccf8e3a20a71cf6e9940',
 'site/styles.css': '6063be4c04726d2dcf01a0442d5dc4d763b99c835a4110bd943799582c14fc34',
 'site/universities.js': '9323dad42fc2c35808ad92888cdffb0ad41edaefaee88c3b57ebb798349c2d62',
 'scripts/build.py': '611d8aefb6e1a043a46426b47b0e35515a87815d1b312604a466c0d210a8e660',
 'scripts/build_rosters.py': 'bc00cde087ec2ba1065b4ac2332fda16918885ec497c2c34dbd319d16f96a7bf',
 'scripts/deterministic_xlsx.py': '65158f54d001eebb2ac586fd820cd69deed8e5c96ed5b117668ced51c11dc300'}

# Reviewed release24 display-only compatibility overlay. Preserve the historical
# pins above; only these four assets may differ after the two fallback labels and
# six shared cache tokens change. All source/data/field pins remain unchanged.
DISPLAY_FIX_APPLICATION_SHA256 = {
    'site/app.js': '5fec893a4b83318d4247299a545f34845d37e076d502bcc9100acec6f73e8f59',
    'site/index.html': '4dde40455944aacd2b3a0a463aee89a64ae2d81ad792a3740dd43c42f005e72f',
    'site/model.js': 'e932f5275311fc833c9ece21a82ade6713987e90e8c4269e199b1a3f07aaed8c',
    'site/rosters.js': 'c3db53692e71b9874be1c003fe6e29a92f4b607a67730d2263c61de62b4874bd',
}

SOURCE_FINGERPRINTS = {'sysu-liuzhiwei': (24, '5020c41e904d76799f5ef91582a4a32bfb66b13dbf32428a662917392bfe6430'),
 'sysu-wutao': (32, 'b103a0a54ba86f5e2ed3bd42f264d8d64791f146d2f32e6a90cd3f79b80300ba'),
 'sysu-caotianzhong': (40, '3161baad852dadeb86a27a3a170d44b19daa285a7878e706b5d2be9865f20ee8'),
 'scu-dutian': (61, 'c0adac66ca16e4b26a234f886ad1f77d50460bf95480898b34e73aef05b64f49'),
 'scu-chenpan': (71, 'c663461f3644894070c81e1fe314e2e91a4edb8a672e72947b473e72222d2ac1'),
 'scu-yangjieren': (78, '871e082d1504314b904975394dcda54e1294b86a6e5c92a86737e97b14e1e458')}

ORG_FINGERPRINTS = {'sysu-history-zhuhai': (79, 'cb38cea42048c91846d543105d2ee3c4f680c273369856afb2f0efcf4546f06d'),
 'scu-materials-science-engineering': (79,
                                       '34f7915d88bc8f66375aa33e417e73e386f32f39b6f693b27eda148fcc60357a')}

SOURCE_LEAF_COUNTS = {'sysu-liuzhiwei': 379,
 'sysu-wutao': 426,
 'sysu-caotianzhong': 214,
 'scu-dutian': 512,
 'scu-chenpan': 361,
 'scu-yangjieren': 319}

EXPECTED_IDS = {'sysu': ['sysu-liuzhiwei', 'sysu-wutao', 'sysu-caotianzhong'],
 'scu': ['scu-dutian', 'scu-chenpan', 'scu-yangjieren']}

EXPECTED_NAMES = {'sysu': ['刘志伟', '吴滔', '曹天忠'], 'scu': ['杜天', '陈攀', '杨劼人']}

EXPECTED_SCOPES = {'sysu': '历史学系（珠海）“教授”栏官方公开搜索索引连续8人，原序首3刘志伟、吴滔、曹天忠；首次进入历史学新院系。不按教育、海外经历或资料多少选人。名录正文403已停止，该顺序只属索引可见顺序，未核名录直链；3份外部正文部分职业档案，非全院全校完成。',
 'scu': '材料科学与工程学院“师资队伍 > '
        '教授”单页正文42人，原序前3杜天、陈攀、杨劼人。本批仅3人部分公开职业资料，不是全院或全校覆盖；教授是名录类别，杜天个人职称为特聘研究员；名录现列不等全职或人事在岗证明。'}

EXPECTED_LIMITATIONS = {'sysu': ['采样依据官方公开索引而非名录正文，三人当前校内任职均需正文复核；名录人数8仅教授栏目索引观察数。',
          '所有正文职业事实来自可读外校官方或学术机构资料，历史现职不延伸为2026在岗；不把现院系回填历史岗位。',
          '毕业、学习和学位标签不等明确授位；博士后与访问为非学位，标签年份单独记录。',
          '导师只取本人直接关系陈述，研究生层次不明确时保留一般研究生指导；不把合作、项目、委员会或课程作者变为师承。',
          '只有三份部分职业资料和每人一条精选书目，不是全院全校或完整履历；具体校区、全职人事状态及导师导航未知。',
          '资料仅含必要公开职业事实、摘录与响应元数据，无联系方式、出生、私人背景、学生名单、论文全文、整页或完整PDF缓存。'],
 'scu': ['材料科学与工程学院“师资队伍 > '
         '教授”单页正文42人，原序前3杜天、陈攀、杨劼人。本批仅3人部分公开职业资料，不是全院或全校覆盖；教授是名录类别，杜天个人职称为特聘研究员；名录现列不等全职或人事在岗证明。',
         '公开最小职业事实与每人1条书目；不保留联系方式、出生、学生名单、完整网页/API或论文全文。',
         '学位标签及毕业典礼不自动确认明确授位；博士后和访问为非学位false，本批其余degree_awarded为null。',
         '杜天博士获授只有索引，正文403已停止该路线，候选隔离不进入已核教育筛选。',
         '陈攀跨校转换年份冲突字段置null，完整双方说法留在独立待核候选。',
         '杨劼人硕博合并阶段导师不强拆为特定硕/博导师；当前教授称谓不回填历史职称。',
         '本批8条直接指导关系已核阶段证据，但导师导航与当前任职未核。',
         '出版者单篇链接、校区和全职人事状态未核。']}

EXPECTED_SCOPE_ENTRIES_SHA256 = {'sysu': '5bf892003241e05ac38a34403df27aa48e2537792b041408bb426c3c9cfd9bad',
 'scu': '2b76864ac93d0ec83d05fd5a27e20745958a300dd05f31a59f9bfa720f81fe1b'}

EXPECTED_REVIEW_LIMITS = {'sysu': ['本批只允许“官方搜索索引栏目原序首3”标签；8是索引观察数，不是当前正文已核总数。不得将scope提升为official_roster_body_read或将个人索引URL称名录直链。',
          '3份可读外部职业正文可支持部分历史档案；学校/现院系/教授抽样归属仍index-only，主体主页快速导航和人事现任未核。若消费者不能清楚分层，应先hold而非默默升级。',
          '9条索引候选不得进入已核任职计数或筛选；历史正文的现任语句只在其历史时点有效，不延伸2026，也不把原历史学系倒推成珠海。',
          '吴滔博士唯一明确授位且仅2003年；5条null不确授，2条博士后/客座非学位。曹天忠qualification_label_year=1999不进入授位/毕业日期筛选。',
          '刘志伟graduate_supervisor须显示研究生阶段未细分，不能默认硕士/博士；葛剑雄直接博士关系可保留。两人当前导师导航均禁用，委员会、课程作者、合著与学术影响不生成导师。',
          '书目为精选且非出版者单篇/全文；来源段落仅保留必要职业事实，不复制私事、学生名单或完整PDF。校区始终未知，不因组织名含珠海推校区。'],
 'scu': ['仅教授栏目42人中原序首3的部分职业事实，不是全院或全校完成；杜天不得因栏目名改为教授。',
         '8条导师是阶段关系边，不是8名不同导师；其中2条博士后不进入学位师承或已获学位统计，合并硕博2边不得拆成4边。全部导师当前导航未核禁用。',
         '授位true0；8条null不能转为确证获授，5条非学位不能计国外学位。MRes2017典礼不改写2014–2015学习期或授位日；博士索引候选不入已核事实筛选。',
         '陈攀跨校边界2022/2023-03仍冲突，候选隔离且正式对应日期null；旧开放结束博士后及历史职务不等2026现任。',
         '杨劼人2020-12为机构起点不是教授晋升；未知职称、日期及校区不能推补。当前页称谓不等全职/人事状态核验。',
         '仅精选本人页书目，出版者单篇未核；不得把来源最小摘录扩成含私人信息的完整网页缓存。']}

EXPECTED_COUNTS = {'sysu-liuzhiwei': {'education': 3,
                    'appointments': 3,
                    'mentors': 1,
                    'publications': 1,
                    'sources': 4,
                    'pending_education_candidates': 0,
                    'pending_mentor_candidates': 0,
                    'pending_appointment_candidates': 4,
                    'pending_professional_fact_candidates': 0,
                    'academic_service': 0,
                    'honors': 0,
                    'research_projects': 0,
                    'teaching': 0,
                    'research_fields': 2,
                    'committee_members': 0},
 'sysu-wutao': {'education': 4,
                'appointments': 3,
                'mentors': 1,
                'publications': 1,
                'sources': 5,
                'pending_education_candidates': 0,
                'pending_mentor_candidates': 0,
                'pending_appointment_candidates': 4,
                'pending_professional_fact_candidates': 0,
                'academic_service': 0,
                'honors': 0,
                'research_projects': 0,
                'teaching': 0,
                'research_fields': 3,
                'committee_members': 0},
 'sysu-caotianzhong': {'education': 1,
                       'appointments': 2,
                       'mentors': 0,
                       'publications': 1,
                       'sources': 5,
                       'pending_education_candidates': 0,
                       'pending_mentor_candidates': 0,
                       'pending_appointment_candidates': 1,
                       'pending_professional_fact_candidates': 0,
                       'academic_service': 0,
                       'honors': 0,
                       'research_projects': 0,
                       'teaching': 0,
                       'research_fields': 4,
                       'committee_members': 0},
 'scu-dutian': {'education': 5,
                'appointments': 2,
                'mentors': 6,
                'publications': 1,
                'sources': 4,
                'pending_education_candidates': 1,
                'pending_mentor_candidates': 0,
                'pending_appointment_candidates': 0,
                'pending_professional_fact_candidates': 0,
                'academic_service': 0,
                'honors': 0,
                'research_projects': 0,
                'teaching': 0,
                'research_fields': 4,
                'committee_members': 0},
 'scu-chenpan': {'education': 5,
                 'appointments': 4,
                 'mentors': 0,
                 'publications': 1,
                 'sources': 3,
                 'pending_education_candidates': 0,
                 'pending_mentor_candidates': 0,
                 'pending_appointment_candidates': 1,
                 'pending_professional_fact_candidates': 0,
                 'academic_service': 0,
                 'honors': 0,
                 'research_projects': 0,
                 'teaching': 0,
                 'research_fields': 4,
                 'committee_members': 0},
 'scu-yangjieren': {'education': 3,
                    'appointments': 3,
                    'mentors': 2,
                    'publications': 1,
                    'sources': 2,
                    'pending_education_candidates': 0,
                    'pending_mentor_candidates': 0,
                    'pending_appointment_candidates': 0,
                    'pending_professional_fact_candidates': 0,
                    'academic_service': 0,
                    'honors': 0,
                    'research_projects': 0,
                    'teaching': 0,
                    'research_fields': 4,
                    'committee_members': 0}}

EXPECTED_AWARDS = {True: 1, None: 13, False: 7}

EXPECTED_EDUCATION = {'sysu-liuzhiwei': [('sysu-liuzhiwei-education-1',
                     None,
                     '中山大学',
                     None,
                     '1977',
                     'undergraduate_study',
                     None,
                     None),
                    ('sysu-liuzhiwei-education-2',
                     None,
                     '中山大学',
                     '1980',
                     '1983',
                     'graduate_study',
                     None,
                     None),
                    ('sysu-liuzhiwei-education-3',
                     None,
                     '台湾大学',
                     '2015-09',
                     '2016-01',
                     'academic_visit',
                     False,
                     None)],
 'sysu-wutao': [('sysu-wutao-education-1', None, '苏州铁道师范学院', None, None, 'undergraduate_study', None, None),
                ('sysu-wutao-education-2', '硕士', '南京农业大学', None, None, 'degree_study', None, None),
                ('sysu-wutao-education-3', '历史学博士', '复旦大学', '2000', '2003', 'degree', True, '2003'),
                ('sysu-wutao-education-4', None, '中山大学', '2003', None, 'postdoctoral_research', False, None)],
 'sysu-caotianzhong': [('sysu-caotianzhong-education-1',
                        '博士',
                        '中山大学',
                        None,
                        None,
                        'degree_study',
                        None,
                        None)],
 'scu-dutian': [('scu-dutian-education-1', '学士', '北京航空航天大学', '2009', '2013', 'degree_study', None, None),
                ('scu-dutian-education-2', '硕士', '帝国理工学院', '2014', '2015', 'degree_study', None, None),
                ('scu-dutian-education-3', '博士', '帝国理工学院', '2015', '2020', 'degree_study', None, None),
                ('scu-dutian-education-4',
                 None,
                 '帝国理工学院 & 玛丽女王大学',
                 '2021',
                 '2021',
                 'postdoctoral_research',
                 False,
                 None),
                ('scu-dutian-education-5',
                 None,
                 '德国埃尔朗根-纽伦堡大学',
                 '2021',
                 '2023',
                 'postdoctoral_research',
                 False,
                 None)],
 'scu-chenpan': [('scu-chenpan-education-1',
                  '工学学士',
                  '中南大学',
                  '2003-09',
                  '2007-07',
                  'degree_study',
                  None,
                  None),
                 ('scu-chenpan-education-2',
                  '工学硕士',
                  '中南大学',
                  '2007-09',
                  '2010-07',
                  'degree_study',
                  None,
                  None),
                 ('scu-chenpan-education-3',
                  '工学博士',
                  '中南大学',
                  '2010-09',
                  '2013-12',
                  'degree_study',
                  None,
                  None),
                 ('scu-chenpan-education-4',
                  None,
                  '中南大学冶金与环境学院',
                  '2014-11',
                  '2017-10',
                  'postdoctoral_research',
                  False,
                  None),
                 ('scu-chenpan-education-5',
                  None,
                  '湖南有色金属研究院',
                  '2018-09',
                  None,
                  'postdoctoral_research',
                  False,
                  None)],
 'scu-yangjieren': [('scu-yangjieren-education-1',
                     None,
                     '上海大学',
                     '2003-09',
                     '2007-07',
                     'undergraduate_study',
                     None,
                     None),
                    ('scu-yangjieren-education-2',
                     '硕士、博士',
                     '哈尔滨工业大学',
                     '2007-09',
                     '2013-07',
                     'graduate_study',
                     None,
                     None),
                    ('scu-yangjieren-education-3',
                     None,
                     '京都大学材料工学部',
                     '2017-09',
                     '2018-09',
                     'academic_visit',
                     False,
                     None)]}

EXPECTED_MENTORS = {'sysu-liuzhiwei': [{'name': '汤明檖',
                     'type': 'graduate_supervisor',
                     'education_stage': '研究生（直接正文未细分硕士或博士）',
                     'start': None,
                     'end': None,
                     'bound_event_ids': ['sysu-liuzhiwei-education-2']}],
 'sysu-wutao': [{'name': '葛剑雄',
                 'type': 'doctoral_supervisor',
                 'education_stage': '博士',
                 'start': None,
                 'end': None,
                 'bound_event_ids': ['sysu-wutao-education-3']}],
 'sysu-caotianzhong': [],
 'scu-dutian': [{'name': 'Martyn McLachlan',
                 'type': 'masters_supervisor',
                 'education_stage': '硕士（MRes）',
                 'start': None,
                 'end': None,
                 'bound_event_ids': ['scu-dutian-education-2']},
                {'name': 'Martin Heeney',
                 'type': 'masters_supervisor',
                 'education_stage': '硕士（MRes）',
                 'start': None,
                 'end': None,
                 'bound_event_ids': ['scu-dutian-education-2']},
                {'name': 'Martyn McLachlan',
                 'type': 'doctoral_co_supervisor',
                 'education_stage': '博士',
                 'start': None,
                 'end': None,
                 'bound_event_ids': ['scu-dutian-education-3']},
                {'name': 'James Durrant',
                 'type': 'doctoral_co_supervisor',
                 'education_stage': '博士',
                 'start': None,
                 'end': None,
                 'bound_event_ids': ['scu-dutian-education-3']},
                {'name': 'Joe Briscoe',
                 'type': 'postdoctoral_supervisor',
                 'education_stage': '博士后',
                 'start': None,
                 'end': None,
                 'bound_event_ids': ['scu-dutian-education-4']},
                {'name': 'Christoph Brabec',
                 'type': 'postdoctoral_supervisor',
                 'education_stage': '博士后',
                 'start': None,
                 'end': None,
                 'bound_event_ids': ['scu-dutian-education-5']}],
 'scu-chenpan': [],
 'scu-yangjieren': [{'name': '傅恒志',
                     'type': 'postgraduate_supervisor',
                     'education_stage': '硕士、博士合并阶段（未细分）',
                     'start': None,
                     'end': None,
                     'bound_event_ids': ['scu-yangjieren-education-2']},
                    {'name': '陈瑞润',
                     'type': 'postgraduate_supervisor',
                     'education_stage': '硕士、博士合并阶段（未细分）',
                     'start': None,
                     'end': None,
                     'bound_event_ids': ['scu-yangjieren-education-2']}]}

EXPECTED_MENTOR_TYPES = {'doctoral_co_supervisor',
 'doctoral_supervisor',
 'graduate_supervisor',
 'masters_supervisor',
 'postdoctoral_supervisor',
 'postgraduate_supervisor'}

EXPECTED_FILTERS = {'sysu-liuzhiwei': {'stages': {'bachelor': [], 'master': [], 'doctor': []},
                    'ug': {'yes': False, 'no': False, 'unknown': False, 'not_recorded': True},
                    'doctorate': {'mainland': False,
                                  'hmt': False,
                                  'overseas': False,
                                  'unknown': False,
                                  'not_recorded': True}},
 'sysu-wutao': {'stages': {'bachelor': [], 'master': [], 'doctor': ['sysu-wutao-education-3']},
                'ug': {'yes': False, 'no': False, 'unknown': False, 'not_recorded': True},
                'doctorate': {'mainland': True,
                              'hmt': False,
                              'overseas': False,
                              'unknown': False,
                              'not_recorded': False}},
 'sysu-caotianzhong': {'stages': {'bachelor': [], 'master': [], 'doctor': []},
                       'ug': {'yes': False, 'no': False, 'unknown': False, 'not_recorded': True},
                       'doctorate': {'mainland': False,
                                     'hmt': False,
                                     'overseas': False,
                                     'unknown': False,
                                     'not_recorded': True}},
 'scu-dutian': {'stages': {'bachelor': [], 'master': [], 'doctor': []},
                'ug': {'yes': False, 'no': False, 'unknown': False, 'not_recorded': True},
                'doctorate': {'mainland': False,
                              'hmt': False,
                              'overseas': False,
                              'unknown': False,
                              'not_recorded': True}},
 'scu-chenpan': {'stages': {'bachelor': [], 'master': [], 'doctor': []},
                 'ug': {'yes': False, 'no': False, 'unknown': False, 'not_recorded': True},
                 'doctorate': {'mainland': False,
                               'hmt': False,
                               'overseas': False,
                               'unknown': False,
                               'not_recorded': True}},
 'scu-yangjieren': {'stages': {'bachelor': [], 'master': [], 'doctor': []},
                    'ug': {'yes': False, 'no': False, 'unknown': False, 'not_recorded': True},
                    'doctorate': {'mainland': False,
                                  'hmt': False,
                                  'overseas': False,
                                  'unknown': False,
                                  'not_recorded': True}}}

EXPECTED_FINAL_TOTALS = {'atlas': (555, 84, 229, 39), 'exports': 111}

EXPECTED_DEPARTMENTS = ['scu-materials-science-engineering', 'sysu-history-zhuhai']

EXPECTED_ROSTER_STATUS = {'sysu': 'official_search_index_only', 'scu': 'official_roster_body_read'}

SOURCE_SHAPES = [['value'],
 ['array', []],
 ['object', [['institution', 0], ['title', 0], ['start', 0], ['end', 0]]],
 ['object',
  [['institution', 0],
   ['title', 0],
   ['start', 0],
   ['end', 0],
   ['current', 0],
   ['status', 0],
   ['as_of', 0],
   ['source_url', 0],
   ['source_id', 0],
   ['evidence_status', 0],
   ['note', 0],
   ['employment_type', 0],
   ['personnel_status_verified', 0],
   ['field_provenance', 2],
   ['field_status', 2]]],
 ['array', [3, 3, 3]],
 ['object',
  [['degree', 0],
   ['institution', 0],
   ['start', 0],
   ['end', 0],
   ['field', 0],
   ['degree_awarded', 0],
   ['degree_awarded_date', 0]]],
 ['object',
  [['event_id', 0],
   ['degree', 0],
   ['institution', 0],
   ['start', 0],
   ['end', 0],
   ['field', 0],
   ['country', 0],
   ['region', 0],
   ['continent', 0],
   ['geography_basis', 0],
   ['geography_status', 0],
   ['event_kind', 0],
   ['degree_awarded', 0],
   ['degree_awarded_date', 0],
   ['source_url', 0],
   ['source_id', 0],
   ['evidence_status', 0],
   ['note', 0],
   ['include_in_education_filters', 0],
   ['field_provenance', 5],
   ['field_status', 5]]],
 ['array', [6, 6, 6]],
 ['object',
  [['name', 0], ['type', 0], ['education_stage', 0], ['education_event_id', 0], ['start', 0], ['end', 0]]],
 ['object',
  [['name', 0],
   ['type', 0],
   ['education_stage', 0],
   ['education_event_id', 0],
   ['start', 0],
   ['end', 0],
   ['source_url', 0],
   ['source_id', 0],
   ['evidence_status', 0],
   ['relationship_status', 0],
   ['include_in_mentorship_graph', 0],
   ['navigation_verified', 0],
   ['navigation_status', 0],
   ['employment_status', 0],
   ['current_institution', 0],
   ['official_url', 0],
   ['person_id', 0],
   ['note', 0],
   ['field_provenance', 8],
   ['field_status', 8]]],
 ['array', [9]],
 ['object',
  [['title', 0],
   ['year', 0],
   ['venue', 0],
   ['volume', 0],
   ['pages_or_article_number', 0],
   ['doi', 0],
   ['type', 0]]],
 ['object',
  [['title', 0],
   ['year', 0],
   ['venue', 0],
   ['volume', 0],
   ['pages_or_article_number', 0],
   ['doi', 0],
   ['url', 0],
   ['type', 0],
   ['source_url', 0],
   ['source_id', 0],
   ['evidence_status', 0],
   ['identity_evidence', 0],
   ['link_status', 0],
   ['individual_article_link_verified', 0],
   ['note', 0],
   ['field_provenance', 11],
   ['field_status', 11]]],
 ['array', [12]],
 ['object',
  [['id', 0],
   ['url', 0],
   ['evidence_status', 0],
   ['retrieved_at', 0],
   ['source_type', 0],
   ['access_note', 0]]],
 ['array', [14, 14, 14, 14]],
 ['array', [0, 0, 0]],
 ['array', [0, 0, 0, 0]],
 ['object',
  [['status', 0],
   ['source_url', 0],
   ['profile_url', 0],
   ['source_ids', 17],
   ['official_roster_profile_link_verified', 0],
   ['note', 0]]],
 ['object',
  [['name', 0], ['school_id', 0], ['department_id', 0], ['organization_id', 0], ['listed_role', 0]]],
 ['object',
  [['institution', 0],
   ['title', 0],
   ['start', 0],
   ['end', 0],
   ['current', 0],
   ['status', 0],
   ['as_of', 0],
   ['source_url', 0],
   ['source_id', 0],
   ['evidence_status', 0],
   ['note', 0],
   ['employment_type', 0],
   ['personnel_status_verified', 0],
   ['field_provenance', 2],
   ['field_status', 2],
   ['include_in_appointment_count', 0],
   ['include_in_verified_appointment_count', 0]]],
 ['array', [20, 20, 20, 20]],
 ['object', [['name', 0], ['source_url', 0], ['source_id', 0], ['evidence_status', 0]]],
 ['array', [22, 22]],
 ['object',
  [['person_id', 0],
   ['name', 0],
   ['school_id', 0],
   ['department_id', 0],
   ['organization_id', 0],
   ['campus_ids', 1],
   ['campus', 0],
   ['department', 0],
   ['department_basis', 0],
   ['roster_entry_id', 0],
   ['official_url', 0],
   ['listed_role', 0],
   ['listed_role_source_url', 0],
   ['listed_role_source_id', 0],
   ['listed_role_basis', 0],
   ['appointments', 4],
   ['education', 7],
   ['mentors', 10],
   ['committee_members', 1],
   ['publications', 13],
   ['sources', 15],
   ['unknowns', 16],
   ['identity_evidence', 18],
   ['professional_field_provenance', 19],
   ['profile_status', 0],
   ['navigation_verified', 0],
   ['navigation_status', 0],
   ['pending_education_candidates', 1],
   ['pending_mentor_candidates', 1],
   ['pending_appointment_candidates', 21],
   ['pending_professional_fact_candidates', 1],
   ['research_fields', 23]]],
 ['array', [0, 0]],
 ['object',
  [['event_id', 0],
   ['degree', 0],
   ['institution', 0],
   ['start', 0],
   ['end', 0],
   ['field', 0],
   ['country', 0],
   ['region', 0],
   ['continent', 0],
   ['geography_basis', 0],
   ['geography_status', 0],
   ['event_kind', 0],
   ['degree_awarded', 0],
   ['degree_awarded_date', 0],
   ['source_url', 0],
   ['source_id', 0],
   ['evidence_status', 0],
   ['note', 0],
   ['include_in_education_filters', 0],
   ['field_provenance', 5],
   ['field_status', 5],
   ['supporting_source_ids', 25]]],
 ['array', [6, 6, 26, 6]],
 ['array', [14, 14, 14, 14, 14]],
 ['array', [0, 0, 0, 0, 0]],
 ['object',
  [['status', 0],
   ['source_url', 0],
   ['profile_url', 0],
   ['source_ids', 29],
   ['official_roster_profile_link_verified', 0],
   ['note', 0]]],
 ['array', [22, 22, 22]],
 ['object',
  [['person_id', 0],
   ['name', 0],
   ['school_id', 0],
   ['department_id', 0],
   ['organization_id', 0],
   ['campus_ids', 1],
   ['campus', 0],
   ['department', 0],
   ['department_basis', 0],
   ['roster_entry_id', 0],
   ['official_url', 0],
   ['listed_role', 0],
   ['listed_role_source_url', 0],
   ['listed_role_source_id', 0],
   ['listed_role_basis', 0],
   ['appointments', 4],
   ['education', 27],
   ['mentors', 10],
   ['committee_members', 1],
   ['publications', 13],
   ['sources', 28],
   ['unknowns', 17],
   ['identity_evidence', 30],
   ['professional_field_provenance', 19],
   ['profile_status', 0],
   ['navigation_verified', 0],
   ['navigation_status', 0],
   ['pending_education_candidates', 1],
   ['pending_mentor_candidates', 1],
   ['pending_appointment_candidates', 21],
   ['pending_professional_fact_candidates', 1],
   ['research_fields', 31]]],
 ['array', [3, 3]],
 ['object',
  [['degree', 0],
   ['institution', 0],
   ['start', 0],
   ['end', 0],
   ['field', 0],
   ['degree_awarded', 0],
   ['degree_awarded_date', 0],
   ['qualification_label_year', 0]]],
 ['array', [0]],
 ['object',
  [['event_id', 0],
   ['degree', 0],
   ['institution', 0],
   ['start', 0],
   ['end', 0],
   ['field', 0],
   ['country', 0],
   ['region', 0],
   ['continent', 0],
   ['geography_basis', 0],
   ['geography_status', 0],
   ['event_kind', 0],
   ['degree_awarded', 0],
   ['degree_awarded_date', 0],
   ['source_url', 0],
   ['source_id', 0],
   ['evidence_status', 0],
   ['note', 0],
   ['include_in_education_filters', 0],
   ['field_provenance', 34],
   ['field_status', 34],
   ['qualification_label_year', 0],
   ['supporting_source_ids', 35]]],
 ['array', [36]],
 ['array', [20]],
 ['array', [22, 22, 22, 22]],
 ['object',
  [['person_id', 0],
   ['name', 0],
   ['school_id', 0],
   ['department_id', 0],
   ['organization_id', 0],
   ['campus_ids', 1],
   ['campus', 0],
   ['department', 0],
   ['department_basis', 0],
   ['roster_entry_id', 0],
   ['official_url', 0],
   ['listed_role', 0],
   ['listed_role_source_url', 0],
   ['listed_role_source_id', 0],
   ['listed_role_basis', 0],
   ['appointments', 33],
   ['education', 37],
   ['mentors', 1],
   ['committee_members', 1],
   ['publications', 13],
   ['sources', 28],
   ['unknowns', 29],
   ['identity_evidence', 30],
   ['professional_field_provenance', 19],
   ['profile_status', 0],
   ['navigation_verified', 0],
   ['navigation_status', 0],
   ['pending_education_candidates', 1],
   ['pending_mentor_candidates', 1],
   ['pending_appointment_candidates', 38],
   ['pending_professional_fact_candidates', 1],
   ['research_fields', 39]]],
 ['object',
  [['institution', 0],
   ['title', 0],
   ['start', 0],
   ['end', 0],
   ['source_id', 0],
   ['source_url', 0],
   ['evidence_status', 0],
   ['field_provenance', 2],
   ['field_status', 2],
   ['current', 0],
   ['status', 0],
   ['as_of', 0],
   ['note', 0],
   ['employment_type', 0],
   ['personnel_status_verified', 0]]],
 ['array', [41, 41]],
 ['object',
  [['event_id', 0],
   ['degree', 0],
   ['institution', 0],
   ['start', 0],
   ['end', 0],
   ['field', 0],
   ['degree_awarded', 0],
   ['degree_awarded_date', 0],
   ['source_id', 0],
   ['source_url', 0],
   ['evidence_status', 0],
   ['field_provenance', 5],
   ['field_status', 5],
   ['country', 0],
   ['region', 0],
   ['continent', 0],
   ['geography_basis', 0],
   ['geography_status', 0],
   ['event_kind', 0],
   ['note', 0],
   ['include_in_education_filters', 0]]],
 ['object',
  [['degree', 0],
   ['institution', 0],
   ['start', 0],
   ['end', 0],
   ['field', 0],
   ['degree_awarded', 0],
   ['degree_awarded_date', 0],
   ['source_reported_degree_label_supplement', 0]]],
 ['object',
  [['event_id', 0],
   ['degree', 0],
   ['institution', 0],
   ['start', 0],
   ['end', 0],
   ['field', 0],
   ['degree_awarded', 0],
   ['degree_awarded_date', 0],
   ['source_id', 0],
   ['source_url', 0],
   ['evidence_status', 0],
   ['field_provenance', 44],
   ['field_status', 5],
   ['country', 0],
   ['region', 0],
   ['continent', 0],
   ['geography_basis', 0],
   ['geography_status', 0],
   ['event_kind', 0],
   ['note', 0],
   ['include_in_education_filters', 0],
   ['supporting_source_ids', 35],
   ['source_reported_degree_label_supplement', 0]]],
 ['array', [43, 45, 43, 43, 43]],
 ['object',
  [['name', 0],
   ['type', 0],
   ['education_stage', 0],
   ['education_event_id', 0],
   ['start', 0],
   ['end', 0],
   ['source_id', 0],
   ['source_url', 0],
   ['evidence_status', 0],
   ['field_provenance', 8],
   ['field_status', 8],
   ['evidence_note', 0],
   ['relationship_status', 0],
   ['include_in_mentorship_graph', 0],
   ['navigation_verified', 0],
   ['navigation_status', 0],
   ['employment_status', 0],
   ['current_institution', 0],
   ['official_url', 0],
   ['person_id', 0],
   ['navigation_source_ids', 1],
   ['note', 0]]],
 ['array', [47, 47, 47, 47, 47, 47]],
 ['object',
  [['title', 0],
   ['year', 0],
   ['venue', 0],
   ['volume', 0],
   ['pages_or_article_number', 0],
   ['doi', 0],
   ['url', 0],
   ['type', 0],
   ['source_id', 0],
   ['source_url', 0],
   ['evidence_status', 0],
   ['field_provenance', 11],
   ['field_status', 11],
   ['identity_evidence', 0],
   ['link_status', 0],
   ['individual_article_link_verified', 0],
   ['note', 0]]],
 ['array', [49]],
 ['object',
  [['id', 0],
   ['url', 0],
   ['evidence_status', 0],
   ['retrieved_at', 0],
   ['source_type', 0]]],
 ['object',
  [['id', 0],
   ['url', 0],
   ['evidence_status', 0],
   ['retrieved_at', 0],
   ['source_type', 0],
   ['page_date', 0]]],
 ['object',
  [['id', 0],
   ['url', 0],
   ['evidence_status', 0],
   ['retrieved_at', 0],
   ['source_type', 0],
   ['page_date', 0],
   ['access_note', 0]]],
 ['object',
  [['id', 0],
   ['url', 0],
   ['evidence_status', 0],
   ['retrieved_at', 0],
   ['source_type', 0],
   ['access_note', 0],
   ['missing_proof', 0]]],
 ['array', [51, 52, 53, 54]],
 ['object', [['status', 0], ['source_url', 0], ['profile_url', 0], ['source_ids', 25], ['note', 0]]],
 ['object',
  [['candidate_id', 0],
   ['education_event_id', 0],
   ['candidate_field', 0],
   ['candidate_value', 0],
   ['source_id', 0],
   ['source_url', 0],
   ['evidence_status', 0],
   ['status', 0],
   ['include_in_education_filters', 0],
   ['include_in_mentorship_graph', 0],
   ['note', 0]]],
 ['array', [57]],
 ['object', [['name', 0], ['source_id', 0], ['source_url', 0], ['evidence_status', 0]]],
 ['array', [59, 59, 59, 59]],
 ['object',
  [['person_id', 0],
   ['name', 0],
   ['school_id', 0],
   ['department_id', 0],
   ['organization_id', 0],
   ['campus_ids', 1],
   ['campus', 0],
   ['department', 0],
   ['roster_entry_id', 0],
   ['official_url', 0],
   ['listed_role', 0],
   ['listed_role_source_url', 0],
   ['listed_role_source_id', 0],
   ['listed_role_basis', 0],
   ['roster_category', 0],
   ['roster_category_source_id', 0],
   ['appointments', 42],
   ['education', 46],
   ['mentors', 48],
   ['committee_members', 1],
   ['publications', 50],
   ['sources', 55],
   ['unknowns', 17],
   ['identity_evidence', 56],
   ['professional_field_provenance', 19],
   ['profile_status', 0],
   ['pending_education_candidates', 58],
   ['pending_mentor_candidates', 1],
   ['pending_appointment_candidates', 1],
   ['pending_professional_fact_candidates', 1],
   ['research_fields', 60]]],
 ['array', [41, 41, 41, 41]],
 ['object',
  [['event_id', 0],
   ['degree', 0],
   ['institution', 0],
   ['start', 0],
   ['end', 0],
   ['field', 0],
   ['degree_awarded', 0],
   ['degree_awarded_date', 0],
   ['source_id', 0],
   ['source_url', 0],
   ['evidence_status', 0],
   ['field_provenance', 5],
   ['field_status', 5],
   ['country', 0],
   ['region', 0],
   ['continent', 0],
   ['geography_basis', 0],
   ['geography_status', 0],
   ['event_kind', 0],
   ['note', 0],
   ['include_in_education_filters', 0],
   ['current_status', 0]]],
 ['array', [43, 43, 43, 43, 63]],
 ['array', [51, 52, 53]],
 ['object',
  [['source_id', 0],
   ['source_url', 0],
   ['scu_special_researcher_start', 0],
   ['csu_combined_appointment_end', 0]]],
 ['object',
  [['source_id', 0],
   ['source_url', 0],
   ['scu_special_researcher_start', 0],
   ['csu_associate_professor_end', 0]]],
 ['array', [66, 67]],
 ['object',
  [['candidate_id', 0],
   ['candidate_field', 0],
   ['source_claims', 68],
   ['evidence_status', 0],
   ['status', 0],
   ['include_in_appointment_filters', 0],
   ['note', 0]]],
 ['array', [69]],
 ['object',
  [['person_id', 0],
   ['name', 0],
   ['school_id', 0],
   ['department_id', 0],
   ['organization_id', 0],
   ['campus_ids', 1],
   ['campus', 0],
   ['department', 0],
   ['roster_entry_id', 0],
   ['official_url', 0],
   ['listed_role', 0],
   ['listed_role_source_url', 0],
   ['listed_role_source_id', 0],
   ['listed_role_basis', 0],
   ['roster_category', 0],
   ['roster_category_source_id', 0],
   ['appointments', 62],
   ['education', 64],
   ['mentors', 1],
   ['committee_members', 1],
   ['publications', 50],
   ['sources', 65],
   ['unknowns', 17],
   ['identity_evidence', 56],
   ['professional_field_provenance', 19],
   ['profile_status', 0],
   ['pending_education_candidates', 1],
   ['pending_mentor_candidates', 1],
   ['pending_appointment_candidates', 70],
   ['pending_professional_fact_candidates', 1],
   ['research_fields', 60]]],
 ['array', [41, 41, 41]],
 ['object',
  [['degree', 0],
   ['institution', 0],
   ['start', 0],
   ['end', 0],
   ['field', 0],
   ['degree_awarded', 0],
   ['degree_awarded_date', 0],
   ['education_level', 0]]],
 ['object',
  [['event_id', 0],
   ['degree', 0],
   ['institution', 0],
   ['start', 0],
   ['end', 0],
   ['field', 0],
   ['degree_awarded', 0],
   ['degree_awarded_date', 0],
   ['source_id', 0],
   ['source_url', 0],
   ['evidence_status', 0],
   ['field_provenance', 73],
   ['field_status', 73],
   ['country', 0],
   ['region', 0],
   ['continent', 0],
   ['geography_basis', 0],
   ['geography_status', 0],
   ['event_kind', 0],
   ['note', 0],
   ['include_in_education_filters', 0],
   ['education_level', 0]]],
 ['array', [74, 74, 43]],
 ['array', [47, 47]],
 ['array', [51, 52]],
 ['object',
  [['person_id', 0],
   ['name', 0],
   ['school_id', 0],
   ['department_id', 0],
   ['organization_id', 0],
   ['campus_ids', 1],
   ['campus', 0],
   ['department', 0],
   ['roster_entry_id', 0],
   ['official_url', 0],
   ['listed_role', 0],
   ['listed_role_source_url', 0],
   ['listed_role_source_id', 0],
   ['listed_role_basis', 0],
   ['roster_category', 0],
   ['roster_category_source_id', 0],
   ['appointments', 72],
   ['education', 75],
   ['mentors', 76],
   ['committee_members', 1],
   ['publications', 50],
   ['sources', 77],
   ['unknowns', 17],
   ['identity_evidence', 56],
   ['professional_field_provenance', 19],
   ['profile_status', 0],
   ['pending_education_candidates', 1],
   ['pending_mentor_candidates', 1],
   ['pending_appointment_candidates', 1],
   ['pending_professional_fact_candidates', 1],
   ['research_fields', 60]]],
 ['object',
  [['id', 0],
   ['name', 0],
   ['type', 0],
   ['school_id', 0],
   ['parent_id', 0],
   ['source_url', 0],
   ['source_id', 0],
   ['evidence_status', 0]]]]

NODE_CONSUMERS = ('\n'
 "import fs from 'node:fs';\n"
 "import {pathToFileURL} from 'node:url';\n"
 "const input=JSON.parse(fs.readFileSync(0,'utf8')), root=input.root;\n"
 "const model=await import(pathToFileURL(root+'/site/model.js'));\n"
 "const roster=await import(pathToFileURL(root+'/site/rosters.js'));\n"
 'const db=input.atlas, r=input.rosters, before=JSON.stringify([db,r]);\n'
 'const people=new Map([...db.people,...db.pending_people].map(p=>[p.person_id,p]));\n'
 'const scoped={...db,rosters:r}, out={people:{},rosters:{},schoolStats:{},schoolPages:{}};\n'
 'for(const id of input.ids){\n'
 " const p=people.get(id),e=r.entries.find(e=>e.id===p.roster_entry_id),main={innerHTML:''};\n"
 " if(!p||!e)throw Error('Missing release record '+id);\n"
 ' roster.renderRosters(scoped,main,e.id,p.school_id);\n'
 ' '
 'out.rosters[id]={matched:roster.rosterIdentityMatched(scoped,e),status:roster.rosterStatusLabel(scoped,e),html:main.innerHTML};\n'
 ' out.people[id]={\n'
 '  '
 "stages:Object.fromEntries(['bachelor','master','doctor'].map(s=>[s,model.stages(p,s).map(e=>e.event_id)])),\n"
 '  '
 "ug:Object.fromEntries(['yes','no','unknown','not_recorded'].map(v=>[v,model.matches(p,{ug:v},db.org_units)])),\n"
 '  '
 "doctorate:Object.fromEntries(['mainland','hmt','overseas','unknown','not_recorded'].map(v=>[v,model.matches(p,{doctor:v},db.org_units)])),\n"
 '  officialUrl:model.officialProfileUrl(p),\n'
 '  '
 'mentors:p.mentors.map(m=>({name:m.name,url:model.mentorOfficialUrl(m),route:model.mentorProfileRoute(m,db.people),events:model.mentorEvents(p,m).map(e=>e.event_id)})),\n'
 '  '
 'candidates:(p.pending_mentor_candidates||[]).map(m=>({name:m.name,url:model.mentorOfficialUrl(m),route:model.mentorProfileRoute(m,db.people)})),\n'
 '  labels:p.education.map(model.educationStageLabel)\n'
 ' };\n'
 '}\n'
 'for(const school of input.schools)out.schoolStats[school]=model.schoolStats(scoped,school);\n'
 'const appAtlas=structuredClone(db),appRosters=structuredClone(r);\n'
 "appAtlas.build_id=appRosters.build_id='rotation002-wave3-in-memory-test';\n"
 'appAtlas.exports=input.exports;\n'
 'out.directories={};\n'
 'const nodes=new Map(),listeners={};\n'
 'const node=key=>{\n'
 ' '
 "if(!nodes.has(key))nodes.set(key,{innerHTML:'',textContent:'',value:'',style:{},dataset:{height:'320'},clientWidth:960,addEventListener(){},click(){this.onclick?.()},querySelector(selector){return "
 'node(selector)},scrollIntoView(){}});\n'
 ' return nodes.get(key);\n'
 '};\n'
 "globalThis.document={querySelector:node,querySelectorAll:()=>[],getElementById:id=>node('#'+id)};\n"
 "globalThis.location={hash:'#/'};\n"
 'globalThis.window={scrollTo(){},addEventListener(name,handler){listeners[name]=handler}};\n'
 'globalThis.fetch=async path=>{\n'
 " if(!/^(atlas|rosters)\\.json(?:\\?|$)/.test(String(path)))throw Error('External fetch prohibited: "
 "'+path);\n"
 ' return '
 "{ok:true,json:async()=>structuredClone(String(path).startsWith('atlas.json')?appAtlas:appRosters)};\n"
 '};\n'
 "await import(pathToFileURL(root+'/site/app.js'));\n"
 "if(!listeners.hashchange)throw Error('Actual app failed to initialize: '+node('#main').innerHTML);\n"
 'const navigate=hash=>{for(const n of '
 "nodes.values())n.innerHTML='';location.hash=hash;listeners.hashchange()};\n"
 'for(const id of input.ids){\n'
 ' const p=people.get(id),row=out.people[id];\n'
 " navigate('#/person/'+encodeURIComponent(id));\n"
 " row.profileMain=node('#main').innerHTML;row.profileContent=node('#profile-content').innerHTML;\n"
 ' if(p.detail_count_eligible){\n'
 "  navigate('#/person/'+encodeURIComponent(id)+'/lineage');\n"
 "  row.lineage=node('#profile-content').innerHTML;row.graph=node('#mind-stage').innerHTML;\n"
 ' }\n'
 '}\n'
 'for(const school of input.schools){\n'
 " navigate('#/school/'+school);out.schoolPages[school]=node('#main').innerHTML;\n"
 " navigate('#/people?school='+school);out.directories[school]=node('#results').innerHTML;\n"
 '}\n'
 'out.unchanged=JSON.stringify([db,r])===before;\n'
 'process.stdout.write(JSON.stringify(out));\n')


# Only these exact approved locator leaves left the public view; every retained scalar is still mutated.
PUBLIC_METADATA_REMOVED_LOCATOR_LEAF_COUNTS = {'sysu-liuzhiwei': 0,
 'sysu-wutao': 0,
 'sysu-caotianzhong': 0,
 'scu-dutian': 4,
 'scu-chenpan': 3,
 'scu-yangjieren': 2}

def project_source_shape(value, node_id):
    """Check every original leaf and array length; allow additive compatibility fields."""
    node = SOURCE_SHAPES[node_id]
    if node[0] == 'value':
        return value
    if node[0] == 'object':
        assert isinstance(value, dict), 'Reviewed object changed type'
        return {key: project_source_shape(value[key], child) for key, child in node[1]}
    assert isinstance(value, list) and len(value) == len(node[1]), 'Reviewed collection changed length/type'
    return [project_source_shape(item, child) for item, child in zip(value, node[1])]


def source_view(person):
    """Reverse retained storage aliases only, without selecting or repairing facts."""
    person = copy.deepcopy(person)
    person['profile_status'] = person['source_profile_status']
    for event in person['education']:
        for key in ('region', 'institution_985', 'event_kind'):
            if 'source_' + key in event:
                event[key] = event['source_' + key]
    for mentor in person['mentors']:
        for key in ('employment_status', 'official_url'):
            if 'source_' + key in mentor:
                mentor[key] = mentor['source_' + key]
    return person


def assert_source_closure(person):
    sources = {row['id']: row['url'] for row in person['sources']}
    assert len(sources) == len(person['sources']), 'Duplicate source ID'
    events = {event['event_id'] for event in person['education']}
    candidates = {event['event_id'] for event in person.get('pending_education_candidates', []) if event.get('event_id')}
    assert not events & candidates, 'Candidate promoted into main events'
    def check(value, path='person'):
        if isinstance(value, dict):
            for key, child in value.items():
                if (key == 'source_id' or key.endswith('_source_id')) and child is not None:
                    assert child in sources, (path, key, 'unknown source', child)
                    url_key = key[:-3] + '_url'
                    if value.get(url_key) is not None:
                        assert value[url_key] == sources[child], (path, key, 'source URL mismatch')
                if (key == 'source_ids' or key.endswith('_source_ids')) and child is not None:
                    assert isinstance(child, list) and all(item in sources for item in child), (path, key)
                if key in ('field_provenance', 'professional_field_provenance'):
                    for ref in child.values():
                        refs = ref if isinstance(ref, list) else [ref]
                        assert all(item is None or isinstance(item, str) and item in sources for item in refs), (path, key)
                else:
                    check(child, path + '/' + key)
        elif isinstance(value, list):
            for index, child in enumerate(value):
                check(child, path + '/' + str(index))
    check(person)
    for mentor in person['mentors']:
        bound = mentor.get('education_event_ids', [mentor.get('education_event_id')])
        if any(bound):
            assert len(bound) == len(set(bound)) and all(e in events for e in bound), 'Main mentor must bind main education only'
    for candidate in person.get('pending_education_candidates', []):
        assert candidate.get('include_in_education_filters') is False, 'Candidate filter promotion'
    return True


class Rotation002Wave3ReleaseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.d = release25_view(json.loads((ROOT / 'data/atlas.json').read_text()), 'data/atlas.json')
        cls.r = release25_view(json.loads((ROOT / 'data/rosters.json').read_text()), 'data/rosters.json')
        cls.q = release25_view(json.loads((ROOT / 'progress/work-queue.json').read_text()), 'progress/work-queue.json')
        cls.ps = {p['person_id']: p for p in cls.d['people'] + cls.d['pending_people']}
        cls.new = [cls.ps[pid] for pid in SOURCE_FINGERPRINTS]
        cls.entries = {e['source_person_id']: e for e in cls.r['entries'] if e.get('source_person_id') in SOURCE_FINGERPRINTS}
        cls.js = None

    @classmethod
    def consumers(cls, atlas=None):
        if atlas is None and cls.js is not None:
            return cls.js
        result = subprocess.run(
            ['node', '--input-type=module', '-e', NODE_CONSUMERS],
            input=json.dumps({'root': str(ROOT), 'atlas': atlas or cls.d, 'rosters': cls.r,
                              'ids': list(SOURCE_FINGERPRINTS), 'schools': list(EXPECTED_IDS),
                              'exports': build.department_exports(cls.d)}),
            text=True, capture_output=True, timeout=45, cwd=ROOT,
        )
        if result.returncode:
            raise AssertionError('Actual JS consumers failed:\n' + result.stderr)
        output = json.loads(result.stdout)
        if atlas is None:
            cls.js = output
        return output

    def tables(self, pid, person=None):
        person = person or self.ps[pid]
        before = copy.deepcopy(person)
        with mock.patch.object(build, 'Workbook', side_effect=AssertionError('Workbook writes prohibited')):
            tables = dict(build.department_tables([person], self.d['updated_at'], self.d['institutions']))
        self.assertEqual(person, before)
        return tables

    def test_01_original_sanitized_person_leaves_shapes_and_array_lengths_survive(self):
        self.assertEqual(len(SOURCE_FINGERPRINTS), 6)
        for pid, (shape, digest) in SOURCE_FINGERPRINTS.items():
            with self.subTest(person=pid):
                self.assertEqual(object_sha(project_source_shape(source_view(self.ps[pid]), shape)), digest)

    def test_02_original_organization_leaves_and_shapes_survive(self):
        orgs = {o['id']: o for o in self.d['org_units']}
        for oid, (shape, digest) in ORG_FINGERPRINTS.items():
            self.assertEqual(object_sha(project_source_shape(orgs[oid], shape)), digest, oid)

    def test_03_every_release23_atlas_prefix_and_fixed_metadata_is_unchanged(self):
        for key, (count, digest) in BASELINE_ATLAS_PREFIXES.items():
            self.assertEqual(object_sha(self.d[key][:count]), digest, key)
        for key, digest in BASELINE_ATLAS_UNCHANGED.items():
            self.assertEqual(object_sha(self.d[key]), digest, key)

    def test_04_every_release23_roster_prefix_and_fixed_metadata_is_unchanged(self):
        for key, (count, digest) in BASELINE_ROSTER_PREFIXES.items():
            self.assertEqual(object_sha(self.r[key][:count]), digest, key)
        for key, digest in BASELINE_ROSTER_UNCHANGED.items():
            self.assertEqual(object_sha(self.r[key]), digest, key)

    def test_05_original_217_queue_tasks_unchanged_only_two_partial_appends(self):
        count, digest = BASELINE_QUEUE_PREFIX
        self.assertEqual(count, 217)
        self.assertEqual(object_sha(self.q['tasks'][:count]), digest)
        self.assertEqual(len(self.q['tasks']), 222)
        self.assertEqual([t['institution_id'] for t in self.q['tasks'][count:219]], ['sysu', 'scu'])
        for task in self.q['tasks'][count:219]:
            self.assertEqual(task['status'], 'partial')
            self.assertIs(task['scope']['university_complete'], False)
            self.assertEqual(task['campus_ids'], [])

    def test_06_exact_six_person_scope_no_hust_or_pending_identity_additions(self):
        self.assertEqual((len(self.d['people']), len(self.d['pending_people']), len(self.d['org_units']), len(self.d['institutions'])), EXPECTED_FINAL_TOTALS['atlas'])
        self.assertEqual((len(self.r['entries']), len(self.r['source_observations'])), (1721, 1759))
        self.assertEqual([p['person_id'] for p in self.d['people'][541:547]], list(SOURCE_FINGERPRINTS))
        self.assertFalse({p['person_id'] for p in self.d['pending_people']} & set(SOURCE_FINGERPRINTS))
        self.assertEqual([e['source_person_id'] for e in self.r['entries'][1706:1712]], list(SOURCE_FINGERPRINTS))
        self.assertEqual({o['id'] for o in self.d['org_units'][221:223]}, set(ORG_FINGERPRINTS))
        self.assertEqual([b['batch_id'] for b in self.d['profile_batches'][132:134]], ['faculty-batch-sysu-rotation-002', 'faculty-batch-scu-rotation-002'])
        self.assertEqual(len(build.department_exports(self.d)), EXPECTED_FINAL_TOTALS['exports'])
        for p in self.new:
            self.assertTrue(p['detail_count_eligible'])
            self.assertFalse(p['complete_profile_count_eligible'])
            self.assertFalse(p['fields_complete'])
            self.assertEqual(p['profile_status'], 'partial_professional_source_checked')
            self.assertEqual(p['campus_ids'], [])
            self.assertIsNone(p['campus'])

    def test_07_exact_original_main_and_candidate_collection_counts(self):
        for p in self.new:
            self.assertEqual({k: len(p.get(k, [])) for k in EXPECTED_COUNTS[p['person_id']]}, EXPECTED_COUNTS[p['person_id']], p['person_id'])
        self.assertEqual(Counter(e['degree_awarded'] for p in self.new for e in p['education']), EXPECTED_AWARDS)

    def test_08_every_original_chronology_degree_tristate_and_stage_survives(self):
        fields = ('event_id','degree','institution','start','end','event_kind','degree_awarded','degree_awarded_date')
        for p in self.new:
            original = source_view(p)
            self.assertEqual([tuple(e.get(k) for k in fields) for e in original['education']], EXPECTED_EDUCATION[p['person_id']])
            for e, raw in zip(p['education'], original['education']):
                self.assertEqual(e['event_kind'], 'degree' if raw['degree_awarded'] is True else raw['event_kind'])
                self.assertEqual(e['education_event_id'], e['event_id'])
                if e['degree_awarded'] is True:
                    self.assertEqual(e['degree_award_source_id'], e['field_provenance']['degree_awarded'])
                    self.assertEqual(e['degree_award_source_url'], next(s['url'] for s in p['sources'] if s['id']==e['degree_award_source_id']))
                else:
                    self.assertIsNone(e['degree_awarded_date'])

    def test_09_actual_education_filters_use_only_source_explicit_awards(self):
        js = self.consumers()['people']
        for pid, expected in EXPECTED_FILTERS.items():
            self.assertEqual(js[pid]['stages'], expected['stages'], pid)
            self.assertEqual(js[pid]['ug'], expected['ug'], pid)
            self.assertEqual(js[pid]['doctorate'], expected['doctorate'], pid)

    def test_10_every_source_reference_and_candidate_boundary_is_closed(self):
        for p in self.new:
            self.assertTrue(assert_source_closure(p))
            self.assertTrue(all(a.get('personnel_status_verified') is not True for a in p['appointments']))

    def test_11_stage_specific_relationships_bind_only_original_stage_events(self):
        js = self.consumers()['people']
        kinds = set()
        for p in self.new:
            expected = EXPECTED_MENTORS[p['person_id']]
            self.assertEqual(len(p['mentors']), len(expected))
            for m, consumer, raw in zip(p['mentors'], js[p['person_id']]['mentors'], expected):
                kinds.add(m['type'])
                for key in ('name','type','education_stage','start','end'):
                    self.assertEqual(m.get(key), raw.get(key), (p['person_id'], key))
                self.assertEqual(consumer['events'], raw['bound_event_ids'])
                self.assertTrue(m['include_in_mentorship_graph'])
                self.assertTrue(m['include_in_verified_mentor_count'])
                self.assertIn(m['name'], js[p['person_id']]['graph'])
                self.assertEqual(js[p['person_id']]['graph'].count('aria-label="查看'+m['name']+'简介"'), sum(x['name']==m['name'] for x in p['mentors']))
        self.assertEqual(kinds, EXPECTED_MENTOR_TYPES)

    def test_12_all_unknown_mentor_current_status_keeps_navigation_off(self):
        js = self.consumers()['people']
        for p in self.new:
            for m, consumer in zip(p['mentors'], js[p['person_id']]['mentors']):
                self.assertEqual(m['employment_status'], 'not_checked' if p['school_id']=='sysu' else 'not_verified')
                self.assertFalse(m['navigation_verified'])
                self.assertFalse(m['quick_link_eligible'])
                self.assertEqual(consumer['url'], '')
                self.assertEqual(consumer['route'], '')
                self.assertEqual(build.mentor_official_url(m), '')
            self.assertNotIn('查看导师个人主页', js[p['person_id']]['lineage'])

    def test_13_source_selection_review_hashes_and_partial_scope_are_pinned(self):
        for school, ids in EXPECTED_IDS.items():
            batch = next(b for b in self.d['profile_batches'] if b['batch_id']==f'faculty-batch-{school}-rotation-002')
            self.assertEqual(batch['selection'], EXPECTED_SCOPES[school])
            self.assertEqual(batch['limitations'][:len(EXPECTED_LIMITATIONS[school])], EXPECTED_LIMITATIONS[school])
            self.assertEqual(batch['source_files'], [{'sha256':SOURCE_PACKAGE_SHA256[school]}])
            self.assertEqual(batch['people_count'], 3)
            self.assertFalse(batch['coverage_complete'])
            self.assertFalse(batch['fields_complete'])
            entries = [e for e in self.r['entries'][1706:1712] if e['school_id']==school]
            self.assertEqual([e['source_person_id'] for e in entries], ids)
            self.assertEqual([e['name'] for e in entries], EXPECTED_NAMES[school])
            for entry in entries:
                self.assertEqual(entry['selection_basis'], EXPECTED_SCOPES[school])
                self.assertEqual(entry['source_evidence_status'], EXPECTED_ROSTER_STATUS[school])
                self.assertEqual(entry['campus_ids'], [])

    def test_14_canonical_tables_keep_main_event_counts_and_exact_tristates(self):
        for p in self.new:
            tables = self.tables(p['person_id'])
            self.assertEqual(list(tables), ['总览','经历','导师','论文','来源'])
            self.assertEqual(len(tables['经历']), len(p['education'])+len(p['appointments'])+1)
            self.assertEqual(len(tables['导师']), len(p['mentors'])+1)
            self.assertEqual(len(tables['论文']), len(p['publications'])+1)
            for e, row in zip(p['education'], tables['经历'][1:]):
                self.assertEqual(row[1:6], [e['event_kind'],e['degree'],e['institution'],e['start'],e['end']])
                self.assertIs(row[11], e['degree_awarded'])
                self.assertEqual(row[12], e['degree_awarded_date'])
                self.assertEqual(row[16], e['source_url'])
            for rows in tables.values():
                self.assertEqual(rows[0][-2:], ['所属学校ID','所属学校'])
                self.assertTrue(all(row[-2]==p['school_id'] for row in rows[1:]))

    def test_15_new_department_workbooks_reopen_equal_every_cell_and_hyperlink(self):
        from openpyxl import load_workbook
        for dept in EXPECTED_DEPARTMENTS:
            people = [p for p in self.d['people'] if p['department_id']==dept]
            tables = build.department_tables(people, self.d['updated_at'], self.d['institutions'])
            wb = load_workbook(ROOT / 'site/exports' / (dept+'.xlsx'))
            try:
                self.assertEqual(wb.sheetnames, [name for name,_ in tables])
                for name, rows in tables:
                    ws = wb[name]
                    self.assertEqual((ws.max_row,ws.max_column), (len(rows),len(rows[0])))
                    for ri, row in enumerate(rows,1):
                        for ci, value in enumerate(row,1):
                            expected = build.clean(value)
                            self.assertEqual(ws.cell(ri,ci).value, None if expected=='' else expected, (dept,name,ri,ci))
                            link = ws.cell(ri,ci).hyperlink
                            self.assertEqual(link.target if link else None, expected if isinstance(expected,str) and build.valid_url(expected) else None, (dept,name,ri,ci,'hyperlink'))
            finally:
                wb.close()

    def test_16_unchanged_application_registry_and_helpers(self):
        for path, digest in UNCHANGED_APPLICATION_SHA256.items():
            self.assertEqual(hashlib.sha256(historical_bytes(path,(ROOT/path).read_bytes())).hexdigest(), RELEASE26_DISPLAY_SHA256.get(path, LAYOUT_FIX_APPLICATION_SHA256.get(path, ROTATION003_APPLICATION_SHA256.get(path, DISPLAY_FIX_APPLICATION_SHA256.get(path,digest)))), path)

    def test_17_actual_statistics_are_partial_not_full_school_population(self):
        js = self.consumers()
        for school in EXPECTED_IDS:
            self.assertEqual(js['schoolStats'][school]['people'], sum(p['school_id']==school for p in self.d['people']))
            self.assertEqual(js['schoolStats'][school]['status'], '部分收录')
            self.assertIn('统计不代表全校教师或学院总数', js['schoolPages'][school])
            self.assertIn('非完整名录', js['schoolPages'][school])

    def test_18_validators_actual_consumers_and_canonical_exports_are_nonmutating(self):
        before = copy.deepcopy((self.d,self.r))
        self.assertTrue(build.validate(self.d))
        self.assertTrue(validate_rosters(self.r,self.d))
        for p in self.new:
            self.tables(p['person_id'])
        self.assertTrue(self.consumers()['unchanged'])
        self.assertEqual((self.d,self.r), before)

    def test_19_public_person_and_roster_additions_have_no_private_or_raw_fields(self):
        forbidden = {'public_raw_cache','local_evidence_cache','cache_path','raw_html','raw_pdf','pdf_bytes','raw_response','email','phone','mobile','birthday','date_of_birth','student_list','students'}
        def check(value):
            if isinstance(value, dict):
                self.assertFalse(forbidden.intersection(value), forbidden.intersection(value))
                for child in value.values():
                    check(child)
            elif isinstance(value, list):
                for child in value:
                    check(child)
            elif isinstance(value, str):
                for prefix in ('/workspace/','/home/agent/','file://'):
                    self.assertNotIn(prefix, value)
        check(self.new)
        check(list(self.entries.values()))

    def test_20_three_scu_reviewed_roster_identity_matches_are_not_current_employment(self):
        js = self.consumers()['rosters']
        snapshot = release25_view(json.loads((ROOT / 'site/rosters.json').read_text()), 'site/rosters.json')
        built = {e['source_person_id']:e for e in snapshot['entries'] if e.get('source_person_id') in SOURCE_FINGERPRINTS}
        for p in self.new:
            if p['school_id'] != 'scu':
                continue
            pid = p['person_id']
            entry = self.entries[pid]
            evidence = entry['profile_identity_evidence']
            self.assertTrue(entry['profile_identity_verified'])
            self.assertEqual(entry['verified_person_id'], pid)
            self.assertEqual(entry['name'], p['name'])
            self.assertEqual(entry['school_id'], p['school_id'])
            self.assertEqual(entry['department_id'], p['department_id'])
            self.assertEqual(evidence['reviewed_source_sha256'], SOURCE_PACKAGE_SHA256[p['school_id']])
            self.assertEqual(evidence['independent_review_sha256'], REVIEW_SHA256[p['school_id']])
            self.assertEqual(evidence['source_ids'], p['identity_evidence']['source_ids'])
            self.assertIn('不表示学历完整、全职或人事在岗已核', evidence['scope_note'])
            self.assertTrue(js[pid]['matched'])
            self.assertEqual(js[pid]['status'], '身份已关联人物档案（任职状态另核）')
            self.assertIn('#/person/'+pid, js[pid]['html'])
            self.assertEqual(built[pid]['profile_identity_evidence'], evidence)

    def test_21_verbatim_research_direction_source_order_and_provenance_render(self):
        from html import escape
        js = self.consumers()
        for p in self.new:
            names = [field['name'] for field in p.get('research_fields', [])]
            expected = '；'.join(names)
            source_ids = list(dict.fromkeys(field['source_id'] for field in p.get('research_fields', [])))
            self.assertTrue(names)
            self.assertEqual(p['research_interests'], expected)
            self.assertEqual(p['research_interests_source_ids'], source_ids)
            self.assertEqual(p['professional_field_provenance']['research_interests'], source_ids)
            self.assertEqual(p['research_interests_derivation'], 'verbatim_original_research_fields_names_in_source_order_for_existing_consumer')
            self.assertIn('<h3>研究方向</h3><p>'+escape(expected)+'</p>', js['people'][p['person_id']]['profileContent'])
            directory = js['directories'][p['school_id']]
            row = next(part for part in directory.split('<tr>') if '#/person/'+p['person_id']+'"' in part)
            self.assertIn('<small>'+escape(expected)+'</small>', row)
            self.assertNotIn('研究方向待补录', row)

    def test_22_fingerprint_guard_rejects_mutation_of_every_original_scalar_leaf(self):
        def leaves(value, path=()):
            if isinstance(value, dict):
                for key, child in value.items():
                    yield from leaves(child, path+(key,))
            elif isinstance(value, list):
                for index, child in enumerate(value):
                    yield from leaves(child, path+(index,))
            else:
                yield path
        for pid, (shape, digest) in SOURCE_FINGERPRINTS.items():
            original = project_source_shape(source_view(self.ps[pid]), shape)
            paths = list(leaves(original))
            self.assertEqual(len(paths) + PUBLIC_METADATA_REMOVED_LOCATOR_LEAF_COUNTS[pid], SOURCE_LEAF_COUNTS[pid])
            for path in paths:
                changed = copy.deepcopy(original)
                target = changed
                for key in path[:-1]:
                    target = target[key]
                target[path[-1]] = {'unreviewed_leaf_mutation': True}
                self.assertNotEqual(object_sha(project_source_shape(changed, shape)), digest, (pid, path))

    def test_23_shape_guard_rejects_missing_original_keys_and_changed_all_array_lengths(self):
        def objects_and_arrays(value, path=()):
            if isinstance(value, (dict, list)):
                yield path, value
                pairs = value.items() if isinstance(value, dict) else enumerate(value)
                for key, child in pairs:
                    yield from objects_and_arrays(child, path+(key,))
        for pid, (shape, _) in SOURCE_FINGERPRINTS.items():
            original = project_source_shape(source_view(self.ps[pid]), shape)
            for path, value in objects_and_arrays(original):
                changed = copy.deepcopy(original)
                target = changed
                for key in path:
                    target = target[key]
                if isinstance(target, list):
                    target.append(None)
                    with self.assertRaises(AssertionError, msg=(pid,path)):
                        project_source_shape(changed, shape)
                elif target:
                    del target[next(iter(target))]
                    with self.assertRaises(KeyError, msg=(pid,path)):
                        project_source_shape(changed, shape)

    def test_24_sysu_index_only_selection_is_not_roster_body_or_profile_href_evidence(self):
        js = self.consumers()
        for p in self.new:
            if p['school_id'] != 'sysu':
                continue
            entry = self.entries[p['person_id']]
            self.assertEqual(entry['source_evidence_status'], 'official_search_index_only')
            self.assertIs(entry.get('profile_identity_verified'), False)
            self.assertFalse(entry.get('verified_person_id'))
            self.assertIs(p['identity_evidence']['official_roster_profile_link_verified'], False)
            self.assertEqual(p['department_basis'], 'official_index_only_sampling_affiliation_not_current_personnel_verification')
            self.assertEqual(p['listed_role_basis'], 'explicit_official_professor_category_search_index_only')
            self.assertEqual(p['professional_field_provenance']['department_id'], 'sysu-historyzh-professor-roster-index')
            self.assertEqual(js['people'][p['person_id']]['officialUrl'], '')
            self.assertFalse(js['rosters'][p['person_id']]['matched'])
            self.assertEqual(js['rosters'][p['person_id']]['status'], '档案待建，身份待核对')
            self.assertNotIn('href="'+p['official_url']+'"', js['rosters'][p['person_id']]['html'])
            self.assertEqual(self.tables(p['person_id'])['总览'][1][3], '')
        org = next(o for o in self.d['org_units'] if o['id']=='sysu-history-zhuhai')
        self.assertEqual(org['evidence_status'], 'official_search_index_only')
        batch = next(b for b in self.d['profile_batches'] if b['batch_id']=='faculty-batch-sysu-rotation-002')
        self.assertIn('连续8人', batch['selection'])
        self.assertIn('名录正文403已停止', batch['selection'])
        self.assertIn('未核名录直链', batch['selection'])

    def test_25_sysu_nine_index_appointments_remain_candidates_and_eight_main_roles_historical(self):
        selected = [p for p in self.new if p['school_id']=='sysu']
        self.assertEqual(sum(len(p['pending_appointment_candidates']) for p in selected), 9)
        self.assertEqual(sum(len(p['appointments']) for p in selected), 8)
        for p in selected:
            for a in p['appointments']:
                self.assertIs(a['current'], False)
                self.assertEqual(a['status'], 'historical_source_reported')
                self.assertEqual(a['evidence_status'], 'official_public_body_read')
            for c in p['pending_appointment_candidates']:
                self.assertIsNone(c['current'])
                self.assertFalse(c['include_in_appointment_count'])
                self.assertFalse(c['include_in_verified_appointment_count'])
                self.assertEqual(c['evidence_status'], 'official_search_index_only')
            without = copy.deepcopy(p)
            without['pending_appointment_candidates'] = []
            self.assertEqual(self.tables(p['person_id'], without), self.tables(p['person_id']))
        liu = self.ps['sysu-liuzhiwei']
        self.assertEqual(liu['appointments'][0]['start'], '1983')
        self.assertEqual(liu['appointments'][0]['as_of'], '2016-01-09')
        wu = self.ps['sysu-wutao']
        self.assertEqual(wu['appointments'][0]['institution'], '中山大学历史学系')
        self.assertEqual(wu['appointments'][0]['start'], '2005')
        self.assertIsNone(wu['appointments'][2]['start'])
        self.assertEqual(wu['appointments'][2]['as_of'], '2022-06-11')

    def test_26_cao_qualification_label_year_never_becomes_graduation_or_award(self):
        p = self.ps['sysu-caotianzhong']
        e = p['education'][0]
        self.assertEqual(e['qualification_label_year'], '1999')
        self.assertEqual(e['event_kind'], 'degree_study')
        for key in ('start','end','degree_awarded','degree_awarded_date'):
            self.assertIsNone(e[key])
        row = self.tables(p['person_id'])['经历'][1]
        for index in (4,5,11,12):
            self.assertIsNone(row[index])
        self.assertEqual(self.consumers()['people'][p['person_id']]['stages']['doctor'], [])
        self.assertEqual(p['appointments'][0]['institution'], '中山大学人文学院历史系、孙中山研究所')
        self.assertEqual(p['appointments'][1]['institution'], '中山大学历史学系')

    def test_27_liu_graduate_supervisor_never_becomes_masters_or_doctoral_supervisor(self):
        p = self.ps['sysu-liuzhiwei']
        e = p['education'][1]
        m = p['mentors'][0]
        self.assertEqual((e['event_kind'],e['start'],e['end']), ('graduate_study','1980','1983'))
        self.assertIsNone(e['degree'])
        self.assertIsNone(e['degree_awarded'])
        self.assertEqual(m['type'], 'graduate_supervisor')
        self.assertEqual(m['name'], '汤明檖')
        self.assertIn('未细分', m['education_stage'])
        self.assertIn('研究生', m['type_label'])
        self.assertIn('未细分', m['type_label'])
        self.assertNotIn('博士导师', m['type_label'])
        self.assertNotIn('硕士导师', m['type_label'])
        self.assertIsNone(p['education'][0]['start'])
        self.assertEqual(p['education'][0]['end'], '1977')

    def test_28_wu_only_explicit_award_and_open_ended_postdoc_remain_year_precise(self):
        p = self.ps['sysu-wutao']
        e = p['education'][2]
        self.assertEqual((e['event_kind'],e['degree_awarded'],e['start'],e['end'],e['degree_awarded_date']), ('degree',True,'2000','2003','2003'))
        self.assertEqual(e['degree_award_source_id'], 'usts-wutao-bio-2015')
        postdoc = p['education'][3]
        self.assertEqual(postdoc['event_kind'], 'postdoctoral_research')
        self.assertFalse(postdoc['degree_awarded'])
        self.assertEqual(postdoc['start'], '2003')
        self.assertIsNone(postdoc['end'])
        self.assertEqual(p['appointments'][0]['start'], '2005')
        self.assertEqual(p['mentors'][0]['type'], 'doctoral_supervisor')
        self.assertEqual(p['mentors'][0]['name'], '葛剑雄')
        self.assertIn('授位日期：2003 ', self.consumers()['people'][p['person_id']]['profileContent'])

    def test_29_scu_42_body_roster_sample_preserves_dutian_actual_title_not_category(self):
        p = self.ps['scu-dutian']
        self.assertEqual(p['listed_role'], '特聘研究员')
        self.assertEqual(p['roster_category'], '教授')
        self.assertEqual(p['listed_role_basis'], 'explicit_individual_profile_title')
        self.assertEqual(p['appointments'][0]['title'], '特聘研究员')
        self.assertEqual(p['appointments'][0]['start'], '2025')
        self.assertNotEqual(p['listed_role_source_id'], p['roster_category_source_id'])
        batch = next(b for b in self.d['profile_batches'] if b['batch_id']=='faculty-batch-scu-rotation-002')
        self.assertIn('单页正文42人', batch['selection'])
        self.assertIn('原序前3杜天、陈攀、杨劼人', batch['selection'])
        for pid in EXPECTED_IDS['scu']:
            self.assertEqual(self.consumers()['people'][pid]['officialUrl'], self.ps[pid]['official_url'])
            self.assertEqual(self.entries[pid]['official_profile_url'], self.ps[pid]['official_url'])

    def test_30_dutian_403_award_candidate_and_mres_ceremony_cannot_promote_a_degree(self):
        p = self.ps['scu-dutian']
        c = p['pending_education_candidates'][0]
        self.assertEqual(c['candidate_value'], True)
        self.assertEqual(c['education_event_id'], 'scu-dutian-education-3')
        self.assertEqual(c['evidence_status'], 'search_index_only')
        self.assertEqual(c['status'], 'pending_body_verification_access_denied')
        self.assertFalse(c['include_in_education_filters'])
        self.assertFalse(c['include_in_mentorship_graph'])
        self.assertNotIn('event_id', c)
        e = p['education'][2]
        self.assertIsNone(e['degree_awarded'])
        self.assertIsNone(e['degree_awarded_date'])
        self.assertEqual((p['education'][1]['start'],p['education'][1]['end']), ('2014','2015'))
        self.assertIn('2017', p['education'][1]['note'])
        self.assertEqual(self.consumers()['people'][p['person_id']]['stages'], {'bachelor':[],'master':[],'doctor':[]})
        without = copy.deepcopy(p)
        without['pending_education_candidates'] = []
        self.assertEqual(self.tables(p['person_id'], without), self.tables(p['person_id']))

    def test_31_dutian_six_stage_edges_are_not_six_unique_people_or_six_degree_advisers(self):
        p = self.ps['scu-dutian']
        self.assertEqual(Counter(m['type'] for m in p['mentors']), {'masters_supervisor':2,'doctoral_co_supervisor':2,'postdoctoral_supervisor':2})
        self.assertEqual(len({m['name'] for m in p['mentors']}), 5)
        for m in p['mentors']:
            e = next(e for e in p['education'] if e['event_id']==m['education_event_id'])
            self.assertIsNone(m['start'])
            self.assertIsNone(m['end'])
            if m['type']=='masters_supervisor':
                self.assertEqual(e['event_id'], 'scu-dutian-education-2')
                self.assertIn('硕士', m['type_label'])
            elif m['type']=='doctoral_co_supervisor':
                self.assertEqual(e['event_id'], 'scu-dutian-education-3')
                self.assertIn('博士', m['type_label'])
                self.assertNotIn('博士后', m['type_label'])
            else:
                self.assertEqual(e['event_kind'], 'postdoctoral_research')
                self.assertFalse(e['degree_awarded'])
                self.assertIn('博士后', m['type_label'])
                self.assertIs(m['include_in_degree_mentorship_graph'], False)
        self.assertEqual((p['education'][3]['start'],p['education'][3]['end']), ('2021','2021'))
        self.assertEqual(p['education'][3]['institution'], '帝国理工学院 & 玛丽女王大学')

    def test_32_yang_unsplit_combined_stage_two_supervisors_and_unknown_promotion_date(self):
        p = self.ps['scu-yangjieren']
        self.assertEqual(len(p['education']), 3)
        e = p['education'][1]
        self.assertEqual((e['degree'],e['event_kind'],e['start'],e['end']), ('硕士、博士','graduate_study','2007-09','2013-07'))
        self.assertIsNone(e['degree_awarded'])
        self.assertEqual(len(p['mentors']), 2)
        for m in p['mentors']:
            self.assertEqual(m['type'], 'postgraduate_supervisor')
            self.assertEqual(m['education_event_id'], e['event_id'])
            self.assertIn('合并', m['education_stage'])
            self.assertIn('未细分', m['education_stage'])
            self.assertIsNone(m['start'])
            self.assertIsNone(m['end'])
        self.assertEqual(p['appointments'][0]['start'], '2020-12')
        self.assertIsNone(p['appointments'][0]['title'])
        self.assertEqual(p['appointments'][1]['title'], '教授、博士生导师')
        self.assertIsNone(p['appointments'][1]['start'])
        self.assertIsNone(p['appointments'][2]['title'])
        self.assertIsNone(p['education'][0]['degree'])
        self.assertEqual(p['education'][0]['education_level'], '本科')
        self.assertFalse(p['education'][2]['degree_awarded'])

    def test_33_chenpan_conflicting_transition_dates_and_open_postdoc_not_repaired(self):
        p = self.ps['scu-chenpan']
        self.assertIsNone(p['appointments'][1]['start'])
        self.assertIsNone(p['appointments'][3]['end'])
        self.assertFalse(p['appointments'][3]['current'])
        c = p['pending_appointment_candidates'][0]
        self.assertEqual(c['status'], 'unresolved_official_source_conflict')
        self.assertFalse(c['include_in_appointment_filters'])
        self.assertEqual([r['scu_special_researcher_start'] for r in c['source_claims']], ['2022','2023-03'])
        self.assertIsNone(p['education'][4]['end'])
        self.assertEqual(p['education'][4]['current_status'], 'historical_open_ended_source_not_current_verified')
        self.assertEqual(p['mentors'], [])
        self.assertTrue(all(e['degree_awarded'] is not True for e in p['education']))

    def test_34_six_selected_bibliographies_preserve_book_and_article_metadata_only(self):
        from html import escape
        self.assertEqual(Counter(pub['type'] for p in self.new for pub in p['publications']), {'book':3,'journal_article':3})
        for p in self.new:
            self.assertEqual(len(p['publications']), 1)
            pub = p['publications'][0]
            self.assertFalse(pub['individual_article_link_verified'])
            self.assertEqual(pub['link_status'], 'official_publication_list_only')
            self.assertIsNone(pub['doi'])
            self.assertEqual(pub['url'], pub['source_url'])
            self.assertIn(escape(pub['title']), self.consumers()['people'][p['person_id']]['profileContent'])
        pub = self.ps['sysu-liuzhiwei']['publications'][0]
        self.assertIsNone(pub['year'])
        self.assertIsNone(pub['venue'])
        title = self.ps['scu-yangjieren']['publications'][0]['title']
        self.assertIn('<a>', title)
        self.assertIn('<c+a>', title)


    def test_35_both_school_and_combined_ledgers_pin_source_review_scope_qa_and_sampling_order(self):
        combined = json.loads((ROOT/'progress/multischool-rotation002-wave3-coverage.json').read_text())
        expected_refs = []
        for school in EXPECTED_IDS:
            ledger = json.loads((ROOT/f'progress/{school}-rotation002-wave3-coverage.json').read_text())
            ref = {'sha256':SOURCE_PACKAGE_SHA256[school],
                   'scope_sha256':REVIEWED_COMPANION_SHA256[school]['scope'],
                   'qa_sha256':REVIEWED_COMPANION_SHA256[school]['qa'],
                   'independent_review_sha256':REVIEW_SHA256[school]}
            expected_refs.append(ref)
            self.assertEqual(ledger['source_references'], [ref])
            self.assertEqual(ledger['selection'], EXPECTED_SCOPES[school])
            self.assertEqual(object_sha(ledger['selected_roster_original_order']), EXPECTED_SCOPE_ENTRIES_SHA256[school])
            self.assertEqual(ledger['source_category_observed_count'], 8 if school=='sysu' else 42)
            self.assertEqual(ledger['source_category_evidence_level'], 'official_index_only' if school=='sysu' else 'official_roster_body_read')
            self.assertEqual(ledger['independent_source_review']['data_sha256'], SOURCE_PACKAGE_SHA256[school])
            self.assertEqual(ledger['independent_source_review']['review_status'], 'passed_with_documented_limits')
            self.assertEqual(ledger['independent_source_review']['integration_limits'], EXPECTED_REVIEW_LIMITS[school])
            self.assertEqual(ledger['independent_source_review']['blockers'], [])
            self.assertFalse(ledger['coverage_complete'])
            self.assertFalse(ledger['fields_complete'])
            self.assertFalse(ledger['university_complete'])
        self.assertEqual(combined['source_references'], expected_refs)
        self.assertEqual([r['school_id'] for r in combined['schools']], ['sysu','scu'])

    def test_36_closure_guard_rejects_source_url_event_and_candidate_filter_corruption(self):
        for mutation in ('source','url','provenance','edge','candidate_filter'):
            p = copy.deepcopy(self.ps['scu-dutian'])
            if mutation=='source':
                p['education'][0]['source_id'] = 'unreviewed-source'
            elif mutation=='url':
                p['pending_education_candidates'][0]['source_url'] = 'https://wrong.example.test/'
            elif mutation=='provenance':
                p['mentors'][0]['field_provenance']['name'] = 'unreviewed-source'
            elif mutation=='edge':
                p['mentors'][0]['education_event_id'] = 'candidate-only-event'
            else:
                p['pending_education_candidates'][0]['include_in_education_filters'] = True
            with self.assertRaises(AssertionError, msg=mutation):
                assert_source_closure(p)

    def test_37_built_site_selected_people_rosters_and_original_person_leaves_match_canonical(self):
        site = release25_view(json.loads((ROOT/'site/atlas.json').read_text()), 'site/atlas.json')
        roster = release25_view(json.loads((ROOT/'site/rosters.json').read_text()), 'site/rosters.json')
        self.assertEqual(len(site['people']), 555)
        self.assertEqual(len(site['pending_people']), 84)
        site_people = {p['person_id']:p for p in site['people']}
        site_entries = {e['source_person_id']:e for e in roster['entries'] if e.get('source_person_id') in SOURCE_FINGERPRINTS}
        for pid, (shape, digest) in SOURCE_FINGERPRINTS.items():
            self.assertEqual(site_people[pid], self.ps[pid])
            self.assertEqual(site_entries[pid], {**self.entries[pid], 'automatic_merge':False, 'candidate_person_ids':[], 'candidate_match_status':'not_linked' if self.ps[pid]['school_id']=='sysu' else 'verified_separate_profile'})
            self.assertEqual(object_sha(project_source_shape(source_view(site_people[pid]), shape)), digest)


# Release25 exact compatibility overlay; original historical pins above remain unchanged.
ROTATION003_APPLICATION_SHA256 = {'site/app.js': '5d4efe8a3c85cbca0125b950a70d7494e3d34a2e67240e6043347903965c8d4b', 'site/model.js': '9dbc155288c1ee0a93fd5d11cd8a7c63724dc0bde6b117a2f71d327e34be3fef', 'site/rosters.js': 'e4bb3c53da7a4ff3c00c1109651d66cc479c20dc265e7705e41213e3019a3502', 'site/index.html': '3b5f7afdd4ac96aaca402884976bccb33cb9a1d2a1ad27793cf7cdd82e5970bf', 'scripts/build.py': '92b6ec03d18666503a7e890e09faffe2e3ac7be61b017ec85b291c1498addacb', 'scripts/build_rosters.py': '29c5dee611bfaef3fd6afd1df9480b254652c51b1c4ce1c9568d75cb799319fe'}


# Exact layout-only overlay; all original source/data/application pins remain above.
LAYOUT_FIX_APPLICATION_SHA256 = {'site/styles.css': '3b01ec6a5674982d048237e5426aa107bd622662d2758913c81bc6f5c4c0ceca', 'site/app.js': '5ce1dbc7161a048ab263cdff313bc904544b362c13d39cc5963886b409f037e2', 'site/rosters.js': '7536ef08c4032e05e1ad3c09532858dd42fd68c20968c82e2146481cf6d9c85f', 'site/index.html': '7e6331d4846c13d64f0a5b5b65a9d52539df537b2ce20ef26563669739f8f2a3'}

# Exact three-file heading/cache correction; all earlier golden constants remain.
RELEASE26_DISPLAY_SHA256={'site/index.html': 'a6e57e88a623157fd3103a6099b9e72b21a0435c9fa62530a41469814844242c', 'site/app.js': '19945c1392982e4b3a1df95d93c271e957bf16b2a238f8d63d24ed892c722dea', 'site/rosters.js': 'd060662fe29e2d5209ca7cabd89121f253c6df69878d776e652f2fe8f8eb45a9'}

if __name__ == '__main__':
    unittest.main()
