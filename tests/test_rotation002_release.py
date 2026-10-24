"""Independent rotation002 release regression, source-pinned and local-only.

Run in a release tests/ directory, or set ACADEMIC_ATLAS_TEST_ROOT to a prepared
release. No source-package, review, normalizer, frozen baseline, network, browser,
workbook generation, or writable release is required at test time. Original-leaf
fingerprints were derived independently from the reviewed raw source packages,
not from integration output. The non-factual public_raw_cache:false flag is
intentionally omitted from public source metadata and pinned projections; no raw
cache is ever admitted. Runtime consumers use cloned in-memory fixtures.

Approved scope covers CAU, NEU, Tongji, and the explicitly reviewed final ECNU
revision. Any further batch must be independently pinned before totals expand. This is not a
live-source re-review, personnel audit, complete school roster, or publisher check.
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

SCHOOLS = ('cau', 'neu', 'tongji', 'ecnu')

PENDING_IDS = ('neu-guolixin',)

SOURCE_PACKAGE_SHA256 = {'cau': 'c246a2efd4599d8a044fb790b20389b8e5a56eec36749546d48c8caedd323e01',
 'neu': '226bf8cf058ed295a9211e13be19e044ba36e7b866f7c08a5026ad2292e210e1',
 'tongji': '9f9ba91abf8715a43fe265cf0340b5657b7d58318bddfc6d43078de65bdef7e0',
 'ecnu': 'c14da5f35e262af10821f328114fcf497cb348c8c17dcd03254407e3b8fb02c0'}

REVIEW_SHA256 = {'cau': '513f84d2eaafbbf8a511e184df656ee160609776229952227c8a58bb2aca7321',
 'neu': 'a1814ac4f33f88ba1c8f96e5622631b9eb36c224f59f68874d5797fd511a1b5f',
 'tongji': '7f134c26bbf123cfa263f8e1a5f2c114a8937a8736f0ecdfbe9626c872233bcb',
 'ecnu': 'f970f4170264f778aaa70bb0194f4cd7dc27448d29269f3329ffa7eabfee1ea6'}

BASELINE_PREFIXES = {'limitations': (6, 'a49996988d143a02303ec539cb493667cdc9b28a287271ae141f6cfd7b95021a'),
 'campuses': (4, 'a29d9956fbbc284b9cdafc640ac9057dd4512c2181d89780a92a6a8bf01e6505'),
 'org_units': (211, 'a4129aa41b01ac29e1245c7ead39ef9b3e2a495b65febdd0a36e90f8d61a774f'),
 'people': (524, '9bea849ee3d6819b23fdf0c8d72e8780408074f43c9b8516ad0bc2e98b54a3a9'),
 'profile_batches': (126, 'ea067099e22ac926a99dfbb30499ecd7e389648078e16e0e95b9d47a45394bfb'),
 'pending_people': (82, '1b82bd92bf6a5f404ad26a12d2b3beac4aaf903ee32ff0c243aa270d494c1d4f'),
 'normalization_evidence': (11, 'ac5f41084864d18adfcfea4a151d88d92c1adfb9b2f33855eed4271745d82c00'),
 'institutions': (39, '8234ea78331d931b8a54c5f40d4427a7844e7fcd621d0832a69e5f2df1b41848')}

BASELINE_UNCHANGED = {'schema_version': '5a4747fcdafec66d8d8812022e3b7d2666d886ec0e0ee7926ec8c50db40f29d5',
 'institution': '9b9fab8a1164afafcf855e8d6ccea17a09e973b8ea2fd8a4831ad681490e8d01',
 'coverage': '8301d88ec52e91fd40964298ce12e179dc0c4ca513b3a0cefa9ad57db895f597'}

BASELINE_ROSTER_PREFIXES = {'summary': (133, '0078218f993ed768d0427cc1aaade579fe8efcb4a76fa1c0fb4ceac59f1650f5'),
 'coverage': (204, 'a8a23975c3bfc4bef79ea7740ca5407abb01983a70f9d5658e253af0f10b5196'),
 'entries': (1688, '9320e105e2887190d695b7db30647eb5f84b647005ca07866494244f053486e8'),
 'conflicts': (30, '0f809e3a2c4ef1857b03479230f35a342b703ccf5f8a99ef032271d150c44c09'),
 'limitations': (35, '4fe8dea8da59fb3789194955a1b22aac4453cbf0e6a4d1cc2e82d172ba77c116'),
 'dedup_candidates': (60, '0a1adbff0d7b0ae2fe42cceff9a89e5e9eb6d164044456f319cfab6c9d1b1653'),
 'exclusions': (3, '89dc768c034efe9de60bb4199c92be749ea7f1bb1405daceff0e3ca88fa5228d'),
 'pending_checks': (2, '143ba1254ce843007ed487ca7f7ef2c684912b54c0580c6bb3f7157b7bc61048'),
 'source_snapshots': (36, '64efd7679845995f5418bdfba501a5908717932d9c26ef812ae8987cc1a1d778'),
 'batches': (99, 'ea6d546b8490198c6af81cf349a50bdcbd4df6f4a5c6127cad2e76ff19bdae63'),
 'source_observations': (1726, '52cc5bb68252be6d38cfbd5f931f89bcd93cd1098d45bcc1b47609728c5f6721'),
 'consolidations': (2, '094423def9986b8e47457a6592e143f75d67eaa7647c2c346df93d54b983e4e0'),
 'supporting_method_evidence': (4, '499f5f2aa6250f9300c5953df9a10da6aeeb384aa2543a7c45862cb8539a1efa'),
 'local_mapping_corrections': (4, '9a1ccc7df1e46b7e8240c3963456fcaf0177d07ad31c051db7d1d5334a1aca1d'),
 'withdrawn_local_conflicts': (1, '8b54b3a107c8f050e3c33cc2125a710a4084b1be287fdb20db8ca392c093ed05')}

BASELINE_ROSTER_UNCHANGED = {'schema_version': '5a4747fcdafec66d8d8812022e3b7d2666d886ec0e0ee7926ec8c50db40f29d5',
 'role_interpretation': '9c1098d16b8ae13b4ef55efb781195831efdc1be68fd601aa8c4d1db41cea7c0'}

REGISTRY_SHA256 = '9323dad42fc2c35808ad92888cdffb0ad41edaefaee88c3b57ebb798349c2d62'

EXPECTED_EDUCATION = {'cau-wuweihua': [],
 'cau-chenliqun': [('cau-chenliqun-education-1',
                    '理学学士',
                    '哈尔滨师范大学',
                    '1987',
                    '1991',
                    'degree_study',
                    None,
                    None),
                   ('cau-chenliqun-education-2',
                    '理学硕士',
                    '哈尔滨师范大学',
                    '1991',
                    '1994',
                    'degree_study',
                    None,
                    None),
                   ('cau-chenliqun-education-3',
                    '理学博士',
                    '中国科学院植物研究所',
                    '1997',
                    '2000',
                    'degree',
                    True,
                    '2000'),
                   ('cau-chenliqun-education-4',
                    None,
                    '清华大学',
                    '2002',
                    '2004',
                    'postdoctoral_research',
                    False,
                    None),
                   ('cau-chenliqun-education-5',
                    None,
                    '佛罗里达大学',
                    '2009',
                    '2010',
                    'academic_visit',
                    False,
                    None)],
 'cau-chenlimei': [],
 'neu-chenzeyu': [('neu-chenzeyu-education-1',
                   '本科',
                   '吉林大学',
                   '2000-09',
                   '2004-06',
                   'degree_study',
                   None,
                   None),
                  ('neu-chenzeyu-education-2',
                   '硕士',
                   '吉林大学',
                   '2004-09',
                   '2007-06',
                   'degree_study',
                   None,
                   None),
                  ('neu-chenzeyu-education-3',
                   '博士',
                   '北京理工大学',
                   '2007-09',
                   '2010-06',
                   'degree_study',
                   None,
                   None),
                  ('neu-chenzeyu-education-4',
                   None,
                   '密歇根大学',
                   '2014-10',
                   '2015-10',
                   'academic_visit',
                   False,
                   None)],
 'neu-guolixin': [],
 'neu-liangzhongchao': [('neu-liangzhongchao-education-1',
                         '工学学士',
                         '东北大学',
                         '2003-09',
                         '2007-08',
                         'degree_study',
                         None,
                         None),
                        ('neu-liangzhongchao-education-2',
                         '工学硕士',
                         '哈尔滨工业大学',
                         '2009-09',
                         '2011-08',
                         'degree_study',
                         None,
                         None),
                        ('neu-liangzhongchao-education-3',
                         '工学博士',
                         '哈尔滨工业大学',
                         '2011-09',
                         '2015-01',
                         'degree',
                         True,
                         '2015-01'),
                        ('neu-liangzhongchao-education-4',
                         None,
                         '曼彻斯特大学',
                         '2019-03',
                         '2021-04',
                         'academic_visit',
                         False,
                         None)],
 'tongji-george-markou': [('tongji-george-markou-education-1',
                           '博士',
                           '雅典国立技术大学',
                           None,
                           '2011',
                           'degree_study',
                           None,
                           None),
                          ('tongji-george-markou-education-2',
                           '硕士',
                           '雅典国立技术大学',
                           None,
                           '2005',
                           'degree_study',
                           None,
                           None),
                          ('tongji-george-markou-education-3',
                           '土木工程五年制学位',
                           '雅典国立技术大学',
                           None,
                           '2004',
                           'degree_study',
                           None,
                           None),
                          ('tongji-george-markou-education-4',
                           None,
                           '谢菲尔德大学',
                           None,
                           None,
                           'academic_visit',
                           False,
                           None)],
 'tongji-chenjianbing': [('tongji-chenjianbing-education-1',
                          '本科',
                          '东北大学',
                          '1993-09',
                          '1997-07',
                          'degree_study',
                          None,
                          None),
                         ('tongji-chenjianbing-education-2',
                          '硕士',
                          '同济大学',
                          '1997-09',
                          '1999-03',
                          'degree_study',
                          None,
                          None),
                         ('tongji-chenjianbing-education-3',
                          '博士',
                          '同济大学',
                          '1999-04',
                          '2002-06',
                          'degree',
                          True,
                          '2002'),
                         ('tongji-chenjianbing-education-4',
                          None,
                          '南加州大学',
                          None,
                          None,
                          'academic_visit',
                          False,
                          None),
                         ('tongji-chenjianbing-education-5',
                          None,
                          '奥尔堡大学',
                          None,
                          None,
                          'academic_visit',
                          False,
                          None),
                         ('tongji-chenjianbing-education-6',
                          None,
                          '维也纳工业大学',
                          None,
                          None,
                          'academic_visit',
                          False,
                          None)],
 'tongji-chenjun': [('tongji-chenjun-education-1',
                     '本科',
                     '郑州工学院',
                     '1989-07',
                     '1993-09',
                     'degree_study',
                     None,
                     None),
                    ('tongji-chenjun-education-2',
                     '硕士',
                     '郑州工学院',
                     '1993-09',
                     '1996-09',
                     'degree_study',
                     None,
                     None),
                    ('tongji-chenjun-education-3',
                     '博士',
                     '同济大学',
                     '1996-09',
                     '1999-10',
                     'degree_study',
                     None,
                     None),
                    ('tongji-chenjun-education-4',
                     None,
                     '香港理工大学',
                     '2001-07',
                     '2004-07',
                     'academic_visit',
                     False,
                     None),
                    ('tongji-chenjun-education-5',
                     None,
                     '东京工艺大学',
                     '2007',
                     '2007',
                     'academic_visit',
                     False,
                     None),
                    ('tongji-chenjun-education-6',
                     None,
                     '伊利诺伊大学香槟分校',
                     '2011',
                     '2011',
                     'academic_visit',
                     False,
                     None),
                    ('tongji-chenjun-education-7',
                     None,
                     '曼彻斯特大学',
                     '2013',
                     '2013',
                     'academic_visit',
                     False,
                     None)],
 'ecnu-baikaixu': [('ecnu-baikaixu-education-1',
                    '学士',
                    '东北农业大学',
                    '2005-09',
                    '2009-07',
                    'degree_study',
                    None,
                    None),
                   ('ecnu-baikaixu-education-2',
                    '博士',
                    '华东师范大学',
                    '2009-09',
                    '2015-12',
                    'degree_study',
                    None,
                    None),
                   ('ecnu-baikaixu-education-3',
                    None,
                    '中佛罗里达大学',
                    '2013-09',
                    '2015-09',
                    'joint_training',
                    False,
                    None)],
 'ecnu-bichunjuan': [('ecnu-bichunjuan-education-1',
                      '学士',
                      '烟台师范学院',
                      '1994-09',
                      '1998-06',
                      'degree_study',
                      None,
                      None),
                     ('ecnu-bichunjuan-education-2',
                      '硕士',
                      '华东师范大学',
                      '1998-09',
                      '2001-06',
                      'degree_study',
                      None,
                      None),
                     ('ecnu-bichunjuan-education-3',
                      '博士',
                      '华东师范大学',
                      '2001-09',
                      '2004-06',
                      'degree_study',
                      None,
                      None),
                     ('ecnu-bichunjuan-education-4',
                      None,
                      'Grand Valley State University',
                      '2005-10',
                      '2005-12',
                      'academic_visit',
                      False,
                      None),
                     ('ecnu-bichunjuan-education-5',
                      None,
                      'North Carolina State University',
                      '2014-02',
                      '2015-02',
                      'academic_visit',
                      False,
                      None)],
 'ecnu-cuican': [('ecnu-cuican-education-1',
                  '学士',
                  '湖南师范大学',
                  '2004-09',
                  '2008-06',
                  'degree_study',
                  None,
                  None),
                 ('ecnu-cuican-education-2', '硕士', '南京大学', '2008-09', '2010-06', 'degree_study', None, None),
                 ('ecnu-cuican-education-3', '博士', '乌特勒支大学', '2010-11', '2015-03', 'degree', True, '2015'),
                 ('ecnu-cuican-education-4',
                  None,
                  '哈佛大学',
                  '2015-09',
                  '2016',
                  'postdoctoral_research',
                  False,
                  None)]}

EXPECTED_CANDIDATE_COUNTS = {'cau-wuweihua': {'pending_education_candidates': 5,
                  'pending_appointment_candidates': 1,
                  'pending_mentor_candidates': 1,
                  'pending_professional_fact_candidates': 0},
 'cau-chenliqun': {'pending_education_candidates': 0,
                   'pending_appointment_candidates': 0,
                   'pending_mentor_candidates': 0,
                   'pending_professional_fact_candidates': 0},
 'cau-chenlimei': {'pending_education_candidates': 3,
                   'pending_appointment_candidates': 3,
                   'pending_mentor_candidates': 0,
                   'pending_professional_fact_candidates': 1},
 'neu-chenzeyu': {'pending_education_candidates': 0,
                  'pending_appointment_candidates': 0,
                  'pending_mentor_candidates': 0,
                  'pending_professional_fact_candidates': 0},
 'neu-guolixin': {'pending_education_candidates': 2,
                  'pending_appointment_candidates': 5,
                  'pending_mentor_candidates': 0,
                  'pending_professional_fact_candidates': 0},
 'neu-liangzhongchao': {'pending_education_candidates': 0,
                        'pending_appointment_candidates': 0,
                        'pending_mentor_candidates': 0,
                        'pending_professional_fact_candidates': 0},
 'tongji-george-markou': {'pending_education_candidates': 1,
                          'pending_appointment_candidates': 0,
                          'pending_mentor_candidates': 1,
                          'pending_professional_fact_candidates': 0},
 'tongji-chenjianbing': {'pending_education_candidates': 0,
                         'pending_appointment_candidates': 0,
                         'pending_mentor_candidates': 0,
                         'pending_professional_fact_candidates': 0},
 'tongji-chenjun': {'pending_education_candidates': 0,
                    'pending_appointment_candidates': 0,
                    'pending_mentor_candidates': 0,
                    'pending_professional_fact_candidates': 0},
 'ecnu-baikaixu': {'pending_education_candidates': 0,
                   'pending_appointment_candidates': 0,
                   'pending_mentor_candidates': 0,
                   'pending_professional_fact_candidates': 0},
 'ecnu-bichunjuan': {'pending_education_candidates': 0,
                     'pending_appointment_candidates': 0,
                     'pending_mentor_candidates': 0,
                     'pending_professional_fact_candidates': 0},
 'ecnu-cuican': {'pending_education_candidates': 0,
                 'pending_appointment_candidates': 0,
                 'pending_mentor_candidates': 0,
                 'pending_professional_fact_candidates': 0}}

EXPECTED_ROSTER_IDS = {'cau-wuweihua': 'roster-cau-biology-plant-science-wuweihua',
 'cau-chenliqun': 'roster-cau-biology-plant-science-chenliqun',
 'cau-chenlimei': 'roster-cau-biology-plant-science-chenlimei',
 'neu-chenzeyu': 'roster-neu-me-vehicle-chenzeyu',
 'neu-guolixin': 'roster-neu-me-vehicle-guolixin',
 'neu-liangzhongchao': 'roster-neu-me-vehicle-liangzhongchao',
 'tongji-george-markou': 'roster-tongji-civil-building-engineering-george-markou',
 'tongji-chenjianbing': 'roster-tongji-civil-building-engineering-chenjianbing',
 'tongji-chenjun': 'roster-tongji-civil-building-engineering-chenjun',
 'ecnu-baikaixu': 'roster-ecnu-geography-baikaixu',
 'ecnu-bichunjuan': 'roster-ecnu-geography-bichunjuan',
 'ecnu-cuican': 'roster-ecnu-geography-cuican'}

EXPECTED_SCOPES = {'cau': '新增生物学院植物科学系官方教授独立栏目，保留页面原序27人中的前3人：武维华、陈立群、陈丽梅；按明确职称分类抽取，不按教育、师承、履历丰富度筛人。本包仅3人，不表示全系、全院或全校完成。',
 'neu': '机械工程与自动化学院教师名录中车辆工程研究所教授分类按拼音排列，原序5人陈泽宇、郭立新、梁忠超、王永富、赵晶，选前3人。选样不依据学历、师承或履历丰富度；名录正文超时/503，原序仅官方索引可见，需后续正文补核。仅3人，非全研究所、全院或全校完成。',
 'tongji': '新增土木工程学院建筑工程系官方“教授”栏目，按33人页面原序取前3人：George '
           'Markou、陈建兵、陈隽。不按教育、师承或履历丰富度筛人。本包不表示全系、全院或全校完成；教授名录不等于全职在岗的人事证明。',
 'ecnu': '地理科学学院教学科研名录“正高级”栏目正文61人，按原序选前3白开旭、毕春娟、崔璨，不按学历、海外经历或资料丰富度筛人。正高级是名录类别，不当作组织节点；仅3人的部分职业资料，非全院或全校完成，名录现列不等人事在岗证明。'}

EXPECTED_ORG_IDS = {'cau': ['cau-biology', 'cau-biology-plant-science'],
 'neu': ['neu-mechanical-engineering-automation', 'neu-mechanical-vehicle-engineering'],
 'tongji': ['tongji-civil-engineering', 'tongji-civil-building-engineering'],
 'ecnu': ['ecnu-geography']}

SOURCE_FINGERPRINTS = {'cau-wuweihua': (28, '1f4628e3d38e68d53f80e41a4c825ec34f14b36ff92cf337207a21c1e74b0472'),
 'cau-chenliqun': (34, '4af8f21a66315762ec2c2c49825b8de215d5a90c30f8bddcc7c9d21f138b3cf6'),
 'cau-chenlimei': (40, '3f3a0ff09b4d54bef82e55a78e9c672eb0ba4f7b58c27ab4cf6a9913b749b00b'),
 'neu-chenzeyu': (55, '029a2d0e2e1c71cebb2f1a7d44905985ee9b9d791e0ac1542d4d89526b091d72'),
 'neu-guolixin': (60, 'd6ea67f553190aa80c606d75f136edf19057dd173855a00fbfc8187db6bfd33e'),
 'neu-liangzhongchao': (62, '07ab09b5d374703ff6190a0b032668aa55eeeacbb5d41202a8e7c1cee989520e'),
 'tongji-george-markou': (71, '4a848d019810e930f84cf31c9780744570a0d8de94777043da00e20d4fe30ab8'),
 'tongji-chenjianbing': (75, 'ecfd413af36250a62c0aef9268f93025477584a78fb85edb357dae362d91c8cb'),
 'tongji-chenjun': (81, '53da6ea0eca19fc1217e27f622ad0516090ae59881d5ea5cc859b6440857f77b'),
 'ecnu-baikaixu': (95, 'e65c0c6df41331b4ffee329c31fd1fcfe72aa0b17fdf04b54773109c9d97c8be'),
 'ecnu-bichunjuan': (104, '9b9f7dee8fa07e90976c72f63323d99ef6de9aa11bc2c1786968c4bca1d99d83'),
 'ecnu-cuican': (110, '67495235ffff64cd6f8ecaabb0cd2422c2dcb2edee3424fd0e58f43c24f2bcdf')}

ORG_FINGERPRINTS = {'cau-biology': (111, '7b2f0aba7a4c59e3c4d0d619c9d16b9898d5ee2582bf8e1669f62f9ba3dbe486'),
 'cau-biology-plant-science': (112, '90fac24ec2795750f83ac7447fe2b669a332d20a324eec4d26be2ecded4387c9'),
 'neu-mechanical-engineering-automation': (113,
                                           '0c5606133879ffaf5a717027c74be12b5b5d25c6f123610505f9a74b50a1b14c'),
 'neu-mechanical-vehicle-engineering': (114,
                                        '80000501cf1134725fc06056a041bd51bfd7087ce32bb618be91114cf02da2f6'),
 'tongji-civil-engineering': (111, '138b5acba9ac7a13cfd7adbaad6710f26421483db6b15fd7d75e36532c8813aa'),
 'tongji-civil-building-engineering': (112,
                                       '0617b8bd28cfe9757c916b376f9130c44ef772dfab601536467db92bebe4dbcc'),
 'ecnu-geography': (113, '68516c5d80e84b6788b3eeb67d4fdd470bde13dc8cdacad5a247894403e9c0fb')}

EDUCATION_KEYS = ("event_id", "degree", "institution", "start", "end", "event_kind", "degree_awarded", "degree_awarded_date")

# Structural masks permit added consumer metadata but protect every original leaf.
SOURCE_SHAPES = [
    ['value'],  # 0
    ['array', []],  # 1
    ['object', [['institution', 0], ['title', 0], ['start', 0], ['end', 0], ['as_of', 0]]],  # 2
    ['object', [['institution', 0], ['title', 0], ['start', 0], ['end', 0], ['current', 0], ['status', 0], ['as_of', 0], ['source_url', 0], ['source_id', 0], ['evidence_status', 0], ['note', 0], ['field_provenance', 2], ['field_status', 2]]],  # 3
    ['array', [3]],  # 4
    ['object', [['title', 0], ['year', 0], ['venue', 0], ['type', 0]]],  # 5
    ['object', [['title', 0], ['year', 0], ['venue', 0], ['doi', 0], ['url', 0], ['type', 0], ['source_url', 0], ['source_id', 0], ['identity_evidence', 0], ['link_status', 0], ['individual_article_link_verified', 0], ['note', 0], ['field_provenance', 5]]],  # 6
    ['array', [6, 6]],  # 7
    ['object', [['id', 0], ['url', 0], ['evidence_status', 0], ['retrieved_at', 0], ['access_note', 0]]],  # 8
    ['object', [['id', 0], ['url', 0], ['evidence_status', 0], ['retrieved_at', 0]]],  # 9
    ['object', [['id', 0], ['url', 0], ['evidence_status', 0], ['retrieved_at', 0], ['access_note', 0], ['published_at', 0]]],  # 10
    ['array', [8, 9, 10, 10, 10]],  # 11
    ['array', [0, 0, 0, 0, 0]],  # 12
    ['array', [0]],  # 13
    ['object', [['status', 0], ['source_url', 0], ['profile_url', 0], ['source_ids', 13]]],  # 14
    ['object', [['name', 0], ['school_id', 0], ['department_id', 0], ['organization_id', 0], ['listed_role', 0]]],  # 15
    ['object', [['name', 0], ['type', 0], ['education_stage', 0], ['education_event_id', 0], ['source_url', 0], ['source_id', 0], ['relationship_status', 0], ['evidence_note', 0], ['include_in_mentorship_graph', 0], ['navigation_verified', 0], ['navigation_status', 0], ['employment_status', 0], ['current_institution', 0], ['profile_source_url', 0], ['profile_source_id', 0], ['official_url', 0], ['person_id', 0], ['employment_status_note', 0]]],  # 16
    ['array', [16]],  # 17
    ['object', [['degree', 0], ['institution', 0], ['start', 0], ['end', 0], ['field', 0], ['degree_awarded', 0], ['degree_awarded_date', 0]]],  # 18
    ['object', [['event_id', 0], ['degree', 0], ['institution', 0], ['start', 0], ['end', 0], ['field', 0], ['country', 0], ['region', 0], ['continent', 0], ['geography_basis', 0], ['geography_status', 0], ['event_kind', 0], ['degree_awarded', 0], ['degree_awarded_date', 0], ['source_url', 0], ['source_id', 0], ['evidence_status', 0], ['note', 0], ['field_provenance', 18], ['field_status', 18], ['candidate_status', 0], ['include_in_education_filters', 0]]],  # 19
    ['object', [['event_id', 0], ['degree', 0], ['institution', 0], ['start', 0], ['end', 0], ['field', 0], ['country', 0], ['region', 0], ['continent', 0], ['geography_basis', 0], ['geography_status', 0], ['event_kind', 0], ['degree_awarded', 0], ['degree_awarded_date', 0], ['source_url', 0], ['source_id', 0], ['evidence_status', 0], ['note', 0], ['field_provenance', 18], ['field_status', 18], ['candidate_status', 0], ['include_in_education_filters', 0], ['indexed_award_statement', 0], ['source_reported_award_date', 0]]],  # 20
    ['object', [['value', 0], ['source_id', 0]]],  # 21
    ['array', [21, 21]],  # 22
    ['object', [['status', 0], ['source_values', 22], ['note', 0]]],  # 23
    ['object', [['event_id', 0], ['degree', 0], ['institution', 0], ['start', 0], ['end', 0], ['field', 0], ['country', 0], ['region', 0], ['continent', 0], ['geography_basis', 0], ['geography_status', 0], ['event_kind', 0], ['degree_awarded', 0], ['degree_awarded_date', 0], ['source_url', 0], ['source_id', 0], ['evidence_status', 0], ['note', 0], ['field_provenance', 18], ['field_status', 18], ['candidate_status', 0], ['include_in_education_filters', 0], ['start_date_conflict', 23]]],  # 24
    ['array', [19, 20, 20, 24, 19]],  # 25
    ['object', [['institution', 0], ['title', 0], ['start', 0], ['end', 0], ['current', 0], ['status', 0], ['as_of', 0], ['source_url', 0], ['source_id', 0], ['evidence_status', 0], ['note', 0], ['field_provenance', 2], ['field_status', 2], ['candidate_status', 0], ['include_in_appointment_filters', 0]]],  # 26
    ['array', [26]],  # 27
    ['object', [['person_id', 0], ['name', 0], ['school_id', 0], ['department_id', 0], ['organization_id', 0], ['campus_ids', 1], ['campus', 0], ['department', 0], ['roster_entry_id', 0], ['official_url', 0], ['listed_role', 0], ['listed_role_source_url', 0], ['listed_role_source_id', 0], ['listed_role_basis', 0], ['appointments', 4], ['education', 1], ['mentors', 1], ['committee_members', 1], ['publications', 7], ['sources', 11], ['unknowns', 12], ['identity_evidence', 14], ['professional_field_provenance', 15], ['alternate_official_profile_urls', 13], ['pending_mentor_candidates', 17], ['research_areas', 13], ['profile_status', 0], ['pending_education_candidates', 25], ['pending_appointment_candidates', 27]]],  # 28
    ['array', [3, 3, 3, 3]],  # 29
    ['object', [['event_id', 0], ['degree', 0], ['institution', 0], ['start', 0], ['end', 0], ['field', 0], ['country', 0], ['region', 0], ['continent', 0], ['geography_basis', 0], ['geography_status', 0], ['event_kind', 0], ['degree_awarded', 0], ['degree_awarded_date', 0], ['source_url', 0], ['source_id', 0], ['evidence_status', 0], ['note', 0], ['field_provenance', 18], ['field_status', 18]]],  # 30
    ['array', [30, 30, 30, 30, 30]],  # 31
    ['array', [8, 10]],  # 32
    ['array', [0, 0, 0, 0]],  # 33
    ['object', [['person_id', 0], ['name', 0], ['school_id', 0], ['department_id', 0], ['organization_id', 0], ['campus_ids', 1], ['campus', 0], ['department', 0], ['roster_entry_id', 0], ['official_url', 0], ['listed_role', 0], ['listed_role_source_url', 0], ['listed_role_source_id', 0], ['listed_role_basis', 0], ['appointments', 29], ['education', 31], ['mentors', 1], ['committee_members', 1], ['publications', 7], ['sources', 32], ['unknowns', 33], ['identity_evidence', 14], ['professional_field_provenance', 15], ['research_areas', 13], ['profile_status', 0]]],  # 34
    ['array', [8, 10, 9]],  # 35
    ['array', [19, 19, 19]],  # 36
    ['array', [26, 26, 26]],  # 37
    ['object', [['field', 0], ['value', 0], ['institution', 0], ['title', 0], ['source_id', 0], ['source_url', 0], ['evidence_status', 0], ['include_in_appointment_filters', 0]]],  # 38
    ['array', [38]],  # 39
    ['object', [['person_id', 0], ['name', 0], ['school_id', 0], ['department_id', 0], ['organization_id', 0], ['campus_ids', 1], ['campus', 0], ['department', 0], ['roster_entry_id', 0], ['official_url', 0], ['listed_role', 0], ['listed_role_source_url', 0], ['listed_role_source_id', 0], ['listed_role_basis', 0], ['appointments', 4], ['education', 1], ['mentors', 1], ['committee_members', 1], ['publications', 7], ['sources', 35], ['unknowns', 12], ['identity_evidence', 14], ['professional_field_provenance', 15], ['alternate_official_profile_urls', 13], ['research_areas', 13], ['profile_status', 0], ['pending_education_candidates', 36], ['pending_appointment_candidates', 37], ['pending_professional_fact_candidates', 39]]],  # 40
    ['object', [['institution', 0], ['title', 0], ['start', 0], ['end', 0]]],  # 41
    ['object', [['institution', 0], ['title', 0], ['start', 0], ['end', 0], ['current', 0], ['status', 0], ['as_of', 0], ['source_url', 0], ['source_id', 0], ['evidence_status', 0], ['note', 0], ['field_provenance', 41], ['field_status', 41]]],  # 42
    ['array', [42, 42, 42]],  # 43
    ['object', [['event_id', 0], ['degree', 0], ['institution', 0], ['start', 0], ['end', 0], ['field', 0], ['country', 0], ['region', 0], ['continent', 0], ['geography_basis', 0], ['geography_status', 0], ['event_kind', 0], ['degree_awarded', 0], ['degree_awarded_date', 0], ['source_url', 0], ['source_id', 0], ['evidence_status', 0], ['note', 0], ['study_level', 0], ['field_provenance', 18], ['field_status', 18], ['include_in_education_filters', 0]]],  # 44
    ['object', [['event_id', 0], ['degree', 0], ['institution', 0], ['start', 0], ['end', 0], ['field', 0], ['country', 0], ['region', 0], ['continent', 0], ['geography_basis', 0], ['geography_status', 0], ['event_kind', 0], ['degree_awarded', 0], ['degree_awarded_date', 0], ['source_url', 0], ['source_id', 0], ['evidence_status', 0], ['note', 0], ['field_provenance', 18], ['field_status', 18], ['include_in_education_filters', 0]]],  # 45
    ['array', [44, 45, 45, 45]],  # 46
    ['object', [['title', 0], ['year', 0], ['venue', 0], ['volume', 0], ['pages_or_article_number', 0], ['type', 0]]],  # 47
    ['object', [['title', 0], ['year', 0], ['venue', 0], ['volume', 0], ['pages_or_article_number', 0], ['doi', 0], ['url', 0], ['type', 0], ['source_url', 0], ['source_id', 0], ['identity_evidence', 0], ['link_status', 0], ['individual_article_link_verified', 0], ['note', 0], ['field_provenance', 47]]],  # 48
    ['array', [48, 48]],  # 49
    ['array', [8, 9]],  # 50
    ['array', [0, 0, 0]],  # 51
    ['object', [['status', 0], ['source_url', 0], ['supporting_source_urls', 13], ['note', 0]]],  # 52
    ['object', [['name', 0], ['source_url', 0], ['source_id', 0]]],  # 53
    ['array', [53, 53, 53]],  # 54
    ['object', [['person_id', 0], ['name', 0], ['school_id', 0], ['department_id', 0], ['organization_id', 0], ['campus_ids', 1], ['campus', 0], ['department', 0], ['roster_entry_id', 0], ['official_url', 0], ['listed_role', 0], ['listed_role_source_url', 0], ['listed_role_source_id', 0], ['listed_role_basis', 0], ['appointments', 43], ['education', 46], ['mentors', 1], ['committee_members', 1], ['publications', 49], ['sources', 50], ['unknowns', 51], ['identity_evidence', 52], ['professional_field_provenance', 15], ['profile_status', 0], ['navigation_verified', 0], ['navigation_status', 0], ['employment_status', 0], ['research_fields', 54]]],  # 55
    ['array', [8, 8]],  # 56
    ['array', [19, 19]],  # 57
    ['object', [['institution', 0], ['title', 0], ['start', 0], ['end', 0], ['current', 0], ['status', 0], ['as_of', 0], ['source_url', 0], ['source_id', 0], ['evidence_status', 0], ['note', 0], ['field_provenance', 41], ['field_status', 41], ['candidate_status', 0], ['include_in_verified_appointments', 0]]],  # 58
    ['array', [58, 58, 58, 58, 58]],  # 59
    ['object', [['person_id', 0], ['name', 0], ['school_id', 0], ['department_id', 0], ['organization_id', 0], ['campus_ids', 1], ['campus', 0], ['department', 0], ['roster_entry_id', 0], ['official_url', 0], ['listed_role', 0], ['listed_role_source_url', 0], ['listed_role_source_id', 0], ['listed_role_basis', 0], ['appointments', 1], ['education', 1], ['mentors', 1], ['committee_members', 1], ['publications', 1], ['sources', 56], ['unknowns', 12], ['identity_evidence', 52], ['professional_field_provenance', 15], ['profile_status', 0], ['navigation_verified', 0], ['navigation_status', 0], ['employment_status', 0], ['pending_education_candidates', 57], ['pending_appointment_candidates', 59]]],  # 60
    ['array', [45, 45, 45, 45]],  # 61
    ['object', [['person_id', 0], ['name', 0], ['school_id', 0], ['department_id', 0], ['organization_id', 0], ['campus_ids', 1], ['campus', 0], ['department', 0], ['roster_entry_id', 0], ['official_url', 0], ['listed_role', 0], ['listed_role_source_url', 0], ['listed_role_source_id', 0], ['listed_role_basis', 0], ['appointments', 43], ['education', 61], ['mentors', 1], ['committee_members', 1], ['publications', 49], ['sources', 56], ['unknowns', 12], ['identity_evidence', 52], ['professional_field_provenance', 15], ['profile_status', 0], ['navigation_verified', 0], ['navigation_status', 0], ['employment_status', 0], ['research_fields', 54]]],  # 62
    ['object', [['institution', 0], ['title', 0], ['start', 0], ['end', 0], ['current', 0], ['status', 0], ['as_of', 0], ['source_url', 0], ['source_id', 0], ['evidence_status', 0], ['note', 0], ['employment_type', 0], ['personnel_status_verified', 0], ['field_provenance', 2], ['field_status', 2]]],  # 63
    ['array', [63, 63, 63, 63, 63]],  # 64
    ['array', [30, 30, 30, 30]],  # 65
    ['array', [9, 9, 9, 8]],  # 66
    ['object', [['马库乔治', 0]]],  # 67
    ['array', [19]],  # 68
    ['object', [['name', 0], ['type', 0], ['education_stage', 0], ['education_event_id', 0], ['source_url', 0], ['source_id', 0], ['relationship_status', 0], ['evidence_note', 0], ['include_in_mentorship_graph', 0], ['navigation_verified', 0], ['navigation_status', 0], ['employment_status', 0], ['current_institution', 0], ['profile_source_url', 0], ['profile_source_id', 0], ['official_url', 0], ['person_id', 0]]],  # 69
    ['array', [69]],  # 70
    ['object', [['person_id', 0], ['name', 0], ['school_id', 0], ['department_id', 0], ['organization_id', 0], ['campus_ids', 1], ['campus', 0], ['department', 0], ['roster_entry_id', 0], ['official_url', 0], ['listed_role', 0], ['listed_role_source_url', 0], ['listed_role_source_id', 0], ['listed_role_basis', 0], ['appointments', 64], ['education', 65], ['mentors', 1], ['committee_members', 1], ['publications', 1], ['sources', 66], ['unknowns', 12], ['identity_evidence', 14], ['professional_field_provenance', 15], ['profile_status', 0], ['aliases', 13], ['alias_provenance', 67], ['pending_education_candidates', 68], ['pending_mentor_candidates', 70], ['research_areas', 12]]],  # 71
    ['array', [63]],  # 72
    ['array', [30, 30, 30, 30, 30, 30]],  # 73
    ['array', [9, 9, 9, 9]],  # 74
    ['object', [['person_id', 0], ['name', 0], ['school_id', 0], ['department_id', 0], ['organization_id', 0], ['campus_ids', 1], ['campus', 0], ['department', 0], ['roster_entry_id', 0], ['official_url', 0], ['listed_role', 0], ['listed_role_source_url', 0], ['listed_role_source_id', 0], ['listed_role_basis', 0], ['appointments', 72], ['education', 73], ['mentors', 1], ['committee_members', 1], ['publications', 7], ['sources', 74], ['unknowns', 51], ['identity_evidence', 14], ['professional_field_provenance', 15], ['profile_status', 0], ['research_areas', 51]]],  # 75
    ['array', [63, 63]],  # 76
    ['object', [['field', 0], ['value', 0], ['meaning', 0], ['source_id', 0], ['source_url', 0], ['evidence_status', 0]]],  # 77
    ['array', [77]],  # 78
    ['object', [['event_id', 0], ['degree', 0], ['institution', 0], ['start', 0], ['end', 0], ['field', 0], ['country', 0], ['region', 0], ['continent', 0], ['geography_basis', 0], ['geography_status', 0], ['event_kind', 0], ['degree_awarded', 0], ['degree_awarded_date', 0], ['source_url', 0], ['source_id', 0], ['evidence_status', 0], ['note', 0], ['field_provenance', 18], ['field_status', 18], ['conflicting_evidence', 78]]],  # 79
    ['array', [79, 30, 30, 30, 30, 30, 30]],  # 80
    ['object', [['person_id', 0], ['name', 0], ['school_id', 0], ['department_id', 0], ['organization_id', 0], ['campus_ids', 1], ['campus', 0], ['department', 0], ['roster_entry_id', 0], ['official_url', 0], ['listed_role', 0], ['listed_role_source_url', 0], ['listed_role_source_id', 0], ['listed_role_basis', 0], ['appointments', 76], ['education', 80], ['mentors', 1], ['committee_members', 1], ['publications', 7], ['sources', 74], ['unknowns', 33], ['identity_evidence', 14], ['professional_field_provenance', 15], ['profile_status', 0], ['research_areas', 33]]],  # 81
    ['object', [['institution', 0], ['title', 0], ['start', 0], ['end', 0], ['current', 0], ['status', 0], ['as_of', 0], ['source_url', 0], ['source_id', 0], ['evidence_status', 0], ['note', 0], ['employment_type', 0], ['personnel_status_verified', 0], ['field_provenance', 41], ['field_status', 41]]],  # 82
    ['array', [82, 82, 82, 82, 82, 82]],  # 83
    ['object', [['event_id', 0], ['degree', 0], ['institution', 0], ['start', 0], ['end', 0], ['field', 0], ['country', 0], ['region', 0], ['continent', 0], ['geography_basis', 0], ['geography_status', 0], ['event_kind', 0], ['degree_awarded', 0], ['degree_awarded_date', 0], ['source_url', 0], ['source_id', 0], ['evidence_status', 0], ['note', 0], ['include_in_education_filters', 0], ['field_provenance', 18], ['field_status', 18]]],  # 84
    ['array', [84, 84, 84]],  # 85
    ['object', [['title', 0], ['year', 0], ['venue', 0], ['volume', 0], ['pages_or_article_number', 0], ['doi', 0], ['type', 0]]],  # 86
    ['object', [['title', 0], ['year', 0], ['venue', 0], ['volume', 0], ['pages_or_article_number', 0], ['doi', 0], ['url', 0], ['type', 0], ['source_url', 0], ['source_id', 0], ['evidence_status', 0], ['identity_evidence', 0], ['link_status', 0], ['individual_article_link_verified', 0], ['note', 0], ['field_provenance', 86]]],  # 87
    ['array', [87]],  # 88
    ['object', [['id', 0], ['url', 0], ['evidence_status', 0], ['retrieved_at', 0], ['source_type', 0]]],  # 89
    ['array', [89, 89]],  # 90
    ['array', [0, 0]],  # 91
    ['object', [['status', 0], ['source_url', 0], ['profile_url', 0], ['source_ids', 91]]],  # 92
    ['object', [['name', 0], ['source_url', 0], ['source_id', 0], ['evidence_status', 0]]],  # 93
    ['array', [93, 93, 93]],  # 94
    ['object', [['person_id', 0], ['name', 0], ['school_id', 0], ['department_id', 0], ['organization_id', 0], ['campus_ids', 1], ['campus', 0], ['department', 0], ['roster_entry_id', 0], ['official_url', 0], ['listed_role', 0], ['listed_role_source_url', 0], ['listed_role_source_id', 0], ['listed_role_basis', 0], ['appointments', 83], ['education', 85], ['mentors', 1], ['committee_members', 1], ['publications', 88], ['sources', 90], ['unknowns', 51], ['identity_evidence', 92], ['professional_field_provenance', 15], ['profile_status', 0], ['pending_education_candidates', 1], ['pending_mentor_candidates', 1], ['pending_appointment_candidates', 1], ['pending_professional_fact_candidates', 1], ['research_fields', 94]]],  # 95
    ['object', [['institution', 0], ['title', 0], ['start', 0], ['end', 0], ['current', 0], ['status', 0], ['as_of', 0], ['source_url', 0], ['source_id', 0], ['evidence_status', 0], ['note', 0], ['employment_type', 0], ['personnel_status_verified', 0], ['field_provenance', 41], ['field_status', 41], ['known_conflict', 0]]],  # 96
    ['array', [96, 96, 82]],  # 97
    ['array', [84, 84, 84, 84, 84]],  # 98
    ['object', [['name', 0], ['type', 0], ['education_stage', 0], ['education_event_id', 0], ['employment_status', 0], ['start', 0], ['end', 0]]],  # 99
    ['object', [['name', 0], ['type', 0], ['education_stage', 0], ['education_event_id', 0], ['source_url', 0], ['source_id', 0], ['evidence_status', 0], ['evidence_note', 0], ['relationship_status', 0], ['include_in_mentorship_graph', 0], ['start', 0], ['end', 0], ['navigation_verified', 0], ['navigation_status', 0], ['employment_status', 0], ['employment_status_note', 0], ['current_institution', 0], ['official_url', 0], ['person_id', 0], ['profile_source_url', 0], ['profile_source_id', 0], ['field_provenance', 99], ['note', 0]]],  # 100
    ['array', [100]],  # 101
    ['object', [['id', 0], ['url', 0], ['evidence_status', 0], ['retrieved_at', 0], ['source_type', 0], ['access_note', 0]]],  # 102
    ['array', [89, 89, 102, 102]],  # 103
    ['object', [['person_id', 0], ['name', 0], ['school_id', 0], ['department_id', 0], ['organization_id', 0], ['campus_ids', 1], ['campus', 0], ['department', 0], ['roster_entry_id', 0], ['official_url', 0], ['listed_role', 0], ['listed_role_source_url', 0], ['listed_role_source_id', 0], ['listed_role_basis', 0], ['appointments', 97], ['education', 98], ['mentors', 101], ['committee_members', 1], ['publications', 88], ['sources', 103], ['unknowns', 33], ['identity_evidence', 92], ['professional_field_provenance', 15], ['profile_status', 0], ['pending_education_candidates', 1], ['pending_mentor_candidates', 1], ['pending_appointment_candidates', 1], ['pending_professional_fact_candidates', 1], ['research_fields', 94]]],  # 104
    ['array', [82, 82, 82, 82, 82]],  # 105
    ['array', [84, 84, 84, 84]],  # 106
    ['array', [89, 102, 102, 102]],  # 107
    ['object', [['status', 0], ['source_url', 0], ['profile_url', 0], ['source_ids', 91], ['supporting_source_ids', 91], ['note', 0]]],  # 108
    ['object', [['Can Cui', 0]]],  # 109
    ['object', [['person_id', 0], ['name', 0], ['school_id', 0], ['department_id', 0], ['organization_id', 0], ['campus_ids', 1], ['campus', 0], ['department', 0], ['roster_entry_id', 0], ['official_url', 0], ['listed_role', 0], ['listed_role_source_url', 0], ['listed_role_source_id', 0], ['listed_role_basis', 0], ['appointments', 105], ['education', 106], ['mentors', 1], ['committee_members', 1], ['publications', 88], ['sources', 107], ['unknowns', 12], ['identity_evidence', 108], ['professional_field_provenance', 15], ['profile_status', 0], ['pending_education_candidates', 1], ['pending_mentor_candidates', 1], ['pending_appointment_candidates', 1], ['pending_professional_fact_candidates', 1], ['aliases', 13], ['alias_provenance', 109], ['research_fields', 94]]],  # 110
    ['object', [['id', 0], ['name', 0], ['type', 0], ['school_id', 0], ['parent_id', 0], ['source_url', 0], ['source_id', 0]]],  # 111
    ['object', [['id', 0], ['name', 0], ['type', 0], ['school_id', 0], ['parent_id', 0], ['source_url', 0], ['source_id', 0], ['note', 0]]],  # 112
    ['object', [['id', 0], ['name', 0], ['type', 0], ['school_id', 0], ['parent_id', 0], ['source_url', 0], ['source_id', 0], ['evidence_status', 0]]],  # 113
    ['object', [['id', 0], ['name', 0], ['type', 0], ['school_id', 0], ['parent_id', 0], ['source_url', 0], ['source_id', 0], ['evidence_status', 0], ['note', 0]]],  # 114
]

def project_source_shape(value, node_id):
    """Project original keys, refusing changed lengths, lost fields, or wrong types."""
    node = SOURCE_SHAPES[node_id]
    if node[0] == 'value':
        return value
    if node[0] == 'object':
        if not isinstance(value, dict):
            raise AssertionError('Reviewed object changed type')
        return {key: project_source_shape(value[key], child) for key, child in node[1]}
    if not isinstance(value, list) or len(value) != len(node[1]):
        raise AssertionError('Reviewed collection changed length/type')
    return [project_source_shape(value, child) for value, child in zip(value, node[1])]


def source_view(person):
    """Reverse documented storage mappings only; never repair substantive facts."""
    person = copy.deepcopy(person)
    person['profile_status'] = person['source_profile_status']
    for key in ('department_id', 'organization_id'):
        if 'source_' + key in person:
            person[key] = person['source_' + key]
    for key in ('education', 'mentors', 'publications'):
        if key in person.get('biography_evidence', {}):
            person[key] = person['biography_evidence'][key]
    for event in person['education']:
        for key in ('region', 'institution_985'):
            if 'source_' + key in event:
                event[key] = event['source_' + key]
    for mentor in person['mentors']:
        for key in ('employment_status', 'official_url'):
            if 'source_' + key in mentor:
                mentor[key] = mentor['source_' + key]
    return person


def assert_source_closure(person):
    """Candidate references may bind candidate events; main edges may not."""
    source_rows = person['sources']
    sources = {row['id']: row['url'] for row in source_rows}
    assert len(source_rows) == len(sources), 'Duplicate source ID'
    main_events = {event['event_id'] for event in person['education']}
    candidate_events = {event['event_id'] for event in person.get('pending_education_candidates', [])}
    assert not main_events.intersection(candidate_events), 'Candidate duplicated as main event'

    def check(value, path='person'):
        if isinstance(value, dict):
            for key, child in value.items():
                if (key == 'source_id' or key.endswith('_source_id')) and child is not None:
                    assert child in sources, (path, key, 'Unknown source ID', child)
                    url_key = key[:-3] + '_url'
                    if value.get(url_key) is not None:
                        assert value[url_key] == sources[child], (path, key, 'Source URL mismatch')
                if (key == 'source_ids' or key.endswith('_source_ids')) and child is not None:
                    assert isinstance(child, list) and all(item in sources for item in child), (path, key)
                if key in ('field_provenance', 'professional_field_provenance'):
                    for field, source_id in child.items():
                        assert source_id is None or source_id in sources, (path, field, source_id)
                    continue  # Provenance maps are terminal source-reference maps.
                check(child, path + '/' + key)
        elif isinstance(value, list):
            for index, child in enumerate(value):
                check(child, path + '/' + str(index))

    check(person)
    for mentor in person['mentors']:
        if mentor.get('education_event_id'):
            assert mentor['education_event_id'] in main_events, 'Main mentor bound to candidate event'
    for mentor in person.get('pending_mentor_candidates', []):
        if mentor.get('education_event_id'):
            assert mentor['education_event_id'] in main_events | candidate_events, 'Dangling candidate event'
        assert mentor.get('include_in_mentorship_graph') is False, 'Candidate promoted to graph'
        assert mentor.get('navigation_verified') is False, 'Candidate navigation upgraded'
    return True


# Actual app/model/roster/graph modules, with all fetches confined to cloned input.
NODE_CONSUMERS = r'''
import fs from 'node:fs';
import {pathToFileURL} from 'node:url';
const input=JSON.parse(fs.readFileSync(0,'utf8')), root=input.root;
const model=await import(pathToFileURL(root+'/site/model.js'));
const roster=await import(pathToFileURL(root+'/site/rosters.js'));
const db=input.atlas, r=input.rosters, before=JSON.stringify([db,r]);
const people=new Map([...db.people,...db.pending_people].map(p=>[p.person_id,p]));
const scoped={...db,rosters:r}, out={people:{},rosters:{},schoolStats:{},schoolPages:{}};
for(const id of input.ids){
 const p=people.get(id),e=r.entries.find(e=>e.id===p.roster_entry_id),main={innerHTML:''};
 if(!p||!e)throw Error('Missing release record '+id);
 roster.renderRosters(scoped,main,e.id,p.school_id);
 out.rosters[id]={matched:roster.rosterIdentityMatched(scoped,e),status:roster.rosterStatusLabel(scoped,e),html:main.innerHTML};
 out.people[id]={
  stages:Object.fromEntries(['bachelor','master','doctor'].map(s=>[s,model.stages(p,s).map(e=>e.event_id)])),
  ug:Object.fromEntries(['yes','no','unknown','not_recorded'].map(v=>[v,model.matches(p,{ug:v},db.org_units)])),
  doctorate:Object.fromEntries(['mainland','hmt','overseas','unknown','not_recorded'].map(v=>[v,model.matches(p,{doctor:v},db.org_units)])),
  officialUrl:model.officialProfileUrl(p),
  mentors:p.mentors.map(m=>({name:m.name,url:model.mentorOfficialUrl(m),route:model.mentorProfileRoute(m,db.people),events:model.mentorEvents(p,m).map(e=>e.event_id)})),
  candidates:(p.pending_mentor_candidates||[]).map(m=>({name:m.name,url:model.mentorOfficialUrl(m),route:model.mentorProfileRoute(m,db.people)})),
  labels:p.education.map(model.educationStageLabel)
 };
}
for(const school of input.schools)out.schoolStats[school]=model.schoolStats(scoped,school);
const appAtlas=structuredClone(db),appRosters=structuredClone(r);
appAtlas.build_id=appRosters.build_id='rotation002-in-memory-test';
const nodes=new Map(),listeners={};
const node=key=>{
 if(!nodes.has(key))nodes.set(key,{innerHTML:'',textContent:'',value:'',style:{},dataset:{height:'320'},clientWidth:960,addEventListener(){},click(){this.onclick?.()},querySelector(selector){return node(selector)},scrollIntoView(){}});
 return nodes.get(key);
};
globalThis.document={querySelector:node,querySelectorAll:()=>[],getElementById:id=>node('#'+id)};
globalThis.location={hash:'#/'};
globalThis.window={scrollTo(){},addEventListener(name,handler){listeners[name]=handler}};
globalThis.fetch=async path=>{
 if(!/^(atlas|rosters)\.json(?:\?|$)/.test(String(path)))throw Error('External fetch prohibited: '+path);
 return {ok:true,json:async()=>structuredClone(String(path).startsWith('atlas.json')?appAtlas:appRosters)};
};
await import(pathToFileURL(root+'/site/app.js'));
if(!listeners.hashchange)throw Error('Actual app failed to initialize: '+node('#main').innerHTML);
const navigate=hash=>{for(const n of nodes.values())n.innerHTML='';location.hash=hash;listeners.hashchange()};
for(const id of input.ids){
 const p=people.get(id),row=out.people[id];
 navigate('#/person/'+encodeURIComponent(id));
 row.profileMain=node('#main').innerHTML;row.profileContent=node('#profile-content').innerHTML;
 if(p.detail_count_eligible){
  navigate('#/person/'+encodeURIComponent(id)+'/lineage');
  row.lineage=node('#profile-content').innerHTML;row.graph=node('#mind-stage').innerHTML;
 }
}
for(const school of input.schools){navigate('#/school/'+school);out.schoolPages[school]=node('#main').innerHTML}
out.unchanged=JSON.stringify([db,r])===before;
process.stdout.write(JSON.stringify(out));
'''


class Rotation002ReleaseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.d = release25_view(json.loads((ROOT / 'data/atlas.json').read_text()), 'data/atlas.json')
        cls.r = release25_view(json.loads((ROOT / 'data/rosters.json').read_text()), 'data/rosters.json')
        cls.ps = {p['person_id']: p for p in cls.d['people'] + cls.d['pending_people']}
        cls.new = [cls.ps[pid] for pid in SOURCE_FINGERPRINTS]
        cls.pro = [p for p in cls.new if p['person_id'] not in PENDING_IDS]
        cls.entries = {e['source_person_id']: e for e in cls.r['entries'] if e.get('source_person_id') in SOURCE_FINGERPRINTS}
        cls.js = None

    @classmethod
    def consumers(cls):
        if cls.js is None:
            result = subprocess.run(
                ['node', '--input-type=module', '-e', NODE_CONSUMERS],
                input=json.dumps({'root': str(ROOT), 'atlas': cls.d, 'rosters': cls.r,
                                  'ids': list(SOURCE_FINGERPRINTS), 'schools': SCHOOLS}),
                text=True, capture_output=True, timeout=45, cwd=ROOT,
            )
            if result.returncode:
                raise AssertionError('Actual JS consumers failed:\n' + result.stderr)
            cls.js = json.loads(result.stdout)
        return cls.js

    def tables(self, pid):
        person = self.ps[pid]
        before = copy.deepcopy(person)
        with mock.patch.object(build, 'Workbook', side_effect=AssertionError('Workbook writes prohibited')):
            tables = dict(build.department_tables([person], self.d['updated_at'], self.d['institutions']))
        self.assertEqual(person, before)
        return tables

    def event(self, pid, number):
        return next(e for e in self.ps[pid]['education'] if e['event_id'] == f'{pid}-education-{number}')

    def test_01_every_reviewed_original_person_leaf_survives(self):
        for pid, (shape, expected) in SOURCE_FINGERPRINTS.items():
            with self.subTest(person=pid):
                self.assertEqual(object_sha(project_source_shape(source_view(self.ps[pid]), shape)), expected)

    def test_02_exact_baseline_atlas_records_and_metadata_are_preserved(self):
        for key, (size, expected) in BASELINE_PREFIXES.items():
            with self.subTest(collection=key):
                self.assertEqual(object_sha(self.d[key][:size]), expected)
        for key, expected in BASELINE_UNCHANGED.items():
            self.assertEqual(object_sha(self.d[key]), expected, key)
        self.assertEqual(hashlib.sha256((ROOT / 'site/universities.js').read_bytes()).hexdigest(), REGISTRY_SHA256)

    def test_03_exact_baseline_roster_and_exclusion_records_are_preserved(self):
        for key, (size, expected) in BASELINE_ROSTER_PREFIXES.items():
            with self.subTest(collection=key):
                self.assertEqual(object_sha(self.r[key][:size]), expected)
        for key, expected in BASELINE_ROSTER_UNCHANGED.items():
            self.assertEqual(object_sha(self.r[key]), expected, key)

    def test_04_exact_reviewed_additions_not_unknown_optional_batches(self):
        # Release24 endpoint; release23 NJU/HNU source assertions keep their bounded historical slice.
        self.assertEqual(len(self.d['people']), 555)
        self.assertEqual([p['person_id'] for p in self.d['people'][535:541]],
                         ['nju-chengxin','nju-chenpengfei','nju-chenyang','hnu-chenzengping','hnu-chuxia','hnu-huanshuangyan'])
        self.assertEqual([(b['batch_id'], b['source_files']) for b in self.d['profile_batches'][130:132]], [
            ('faculty-batch-nju-rotation-002', [{'file':'faculty-batch-nju-rotation-002.json','sha256':'141e34961e4b39300cd05e1e32fe4de0af5676e20601153d0e1d6d8ff50fe471'}]),
            ('faculty-batch-hnu-rotation-002', [{'file':'faculty-batch-hnu-rotation-002.json','sha256':'7ad107b353fa4da5a549cfbe89e14fbb3ec6500014d0c6d782abda41b5253a54'}]),
        ])
        self.assertEqual(len(self.d['pending_people']), 84)
        self.assertEqual(len(self.d['institutions']), 39)
        self.assertEqual(len(self.d['org_units']), 229)
        self.assertEqual([u['id'] for u in self.d['org_units'][218:221]], ['nju-astronomy-space-science','hnu-chemistry','hnu-chemistry-department'])
        self.assertEqual(len(self.d['campuses']), 4)
        self.assertEqual({p['person_id'] for p in self.d['people'][524:535]}, set(SOURCE_FINGERPRINTS) - set(PENDING_IDS))
        self.assertEqual([p['person_id'] for p in self.d['pending_people'][82:83]], list(PENDING_IDS))
        self.assertEqual(len(self.new), 12)
        self.assertEqual(len(self.pro), 11)
        self.assertEqual(Counter(p['school_id'] for p in self.new), Counter({school: 3 for school in SCHOOLS}))
        self.assertEqual(len(self.r['entries']), 1721)
        self.assertEqual(len(self.r['source_observations']), 1759)
        self.assertEqual(len(self.r['coverage']), 215)
        self.assertEqual(set(self.entries), set(SOURCE_FINGERPRINTS))
        for person in self.pro:
            self.assertIs(person['detail_count_eligible'], True)
            self.assertIs(person['complete_profile_count_eligible'], False)
            self.assertIs(person['fields_complete'], False)

    def test_05_all_main_event_and_candidate_counts_are_independent(self):
        self.assertEqual({key: sum(len(p.get(key, [])) for p in self.new) for key in ('education','appointments','mentors','committee_members','publications','sources')},
                         {'education':42,'appointments':34,'mentors':1,'committee_members':0,'publications':17,'sources':38})
        self.assertEqual(Counter(e['degree_awarded'] for p in self.new for e in p['education']), {True:4,None:22,False:16})
        for pid, expected in EXPECTED_CANDIDATE_COUNTS.items():
            self.assertEqual({key: len(self.ps[pid].get(key, [])) for key in expected}, expected, pid)
        self.assertEqual({key: sum(len(p.get(key, [])) for p in self.new) for key in ('pending_education_candidates','pending_appointment_candidates','pending_mentor_candidates','pending_professional_fact_candidates')},
                         {'pending_education_candidates':11,'pending_appointment_candidates':9,'pending_mentor_candidates':2,'pending_professional_fact_candidates':1})

    def test_06_exact_fortytwo_education_chronologies_and_award_tristates(self):
        for pid, expected in EXPECTED_EDUCATION.items():
            self.assertEqual([tuple(e.get(key) for key in EDUCATION_KEYS) for e in self.ps[pid]['education']], expected, pid)
        for person in self.new:
            for event in person['education']:
                if event['degree_awarded'] is True:
                    self.assertEqual(event['event_kind'], 'degree')
                if event['event_kind'] in ('academic_visit','postdoctoral_research','joint_training'):
                    self.assertIs(event['degree_awarded'], False)
                    self.assertIsNone(event['degree'])
                    self.assertIsNone(event['degree_awarded_date'])

    def test_07_actual_degree_filters_admit_only_four_explicit_doctorates(self):
        js = self.consumers()['people']
        mainland_doctors = {'cau-chenliqun','neu-liangzhongchao','tongji-chenjianbing'}
        overseas_doctors = {'ecnu-cuican'}
        doctors = mainland_doctors | overseas_doctors
        for person in self.new:
            pid = person['person_id']
            self.assertEqual(js[pid]['stages']['bachelor'], [])
            self.assertEqual(js[pid]['stages']['master'], [])
            self.assertEqual(js[pid]['stages']['doctor'], [f'{pid}-education-3'] if pid in doctors else [])
            self.assertEqual(js[pid]['ug'], {'yes':False,'no':False,'unknown':False,'not_recorded':True})
            self.assertEqual(js[pid]['doctorate'], {'mainland':pid in mainland_doctors,'hmt':False,'overseas':pid in overseas_doctors,'unknown':False,'not_recorded':pid not in doctors})

    def test_08_all_candidates_remain_outside_main_fields_filters_and_graphs(self):
        for person in self.new:
            main_ids = {e['event_id'] for e in person['education']}
            for event in person.get('pending_education_candidates', []):
                self.assertNotIn(event['event_id'], main_ids)
                self.assertIs(event['include_in_education_filters'], False)
                self.assertIsNot(event.get('degree_awarded'), True)
            for event in person.get('pending_appointment_candidates', []):
                self.assertIs(event.get('include_in_appointment_filters', event.get('include_in_verified_appointments')), False)
                self.assertNotIn(event, person['appointments'])
            for mentor in person.get('pending_mentor_candidates', []):
                self.assertIs(mentor['include_in_mentorship_graph'], False)
                self.assertIs(mentor['navigation_verified'], False)
                self.assertIsNot(mentor.get('include_in_verified_mentor_count'), True)
                self.assertEqual(build.mentor_official_url(mentor), '')
            self.assertEqual(len(person['mentors']), 1 if person['person_id']=='ecnu-bichunjuan' else 0)

    def test_09_cau_role_and_publications_do_not_confirm_index_education(self):
        for pid, count in [('cau-wuweihua',5),('cau-chenlimei',3)]:
            person = self.ps[pid]
            self.assertEqual(person['source_profile_status'], 'official_role_publications_verified_education_pending')
            self.assertEqual(person['education'], [])
            self.assertEqual(len(person['pending_education_candidates']), count)
            self.assertEqual(len(person['appointments']), 1)
            self.assertIsNone(person['appointments'][0]['start'])
            self.assertEqual(person['appointments'][0]['evidence_status'], 'official_public_body_read')
            self.assertEqual(len(person['publications']), 2)
        wu = self.ps['cau-wuweihua']
        self.assertEqual(wu['pending_mentor_candidates'][0]['education_event_id'], 'cau-wuweihua-education-2')
        self.assertEqual(wu['pending_mentor_candidates'][0]['employment_status'], 'deceased')
        self.assertEqual(wu['pending_education_candidates'][3]['start'], '1987-12')
        self.assertEqual([v['value'] for v in wu['pending_education_candidates'][3]['start_date_conflict']['source_values']], ['1987-12','1988-01'])
        self.assertIsNone(wu['pending_education_candidates'][2]['start'])
        self.assertEqual(wu['pending_education_candidates'][2]['source_reported_award_date'], '1991-11')
        self.assertIsNone(wu['pending_education_candidates'][2]['degree_awarded'])
        self.assertIsNone(wu['pending_education_candidates'][4]['start'])

    def test_10_all_cau_personal_page_shortcuts_respect_latest_denial(self):
        js = self.consumers()
        for pid in ('cau-wuweihua','cau-chenliqun','cau-chenlimei'):
            person = self.ps[pid]
            self.assertIs(person['official_profile_navigation_eligible'], False)
            self.assertEqual(person['official_profile_availability'], 'unavailable')
            self.assertEqual(js['people'][pid]['officialUrl'], '')
            self.assertEqual(self.tables(pid)['总览'][1][3], '')
            self.assertNotIn('href="' + person['official_url'] + '"', js['people'][pid]['profileMain'])
            self.assertNotIn('href="' + person['official_url'] + '"', js['rosters'][pid]['html'])
        for pid in ('cau-wuweihua','cau-chenlimei'):
            person = self.ps[pid]
            alts = person['alternative_professional_sources']
            self.assertEqual(len(alts), 1)
            self.assertEqual(alts[0]['url'], person['appointments'][0]['source_url'])
            self.assertIn(alts[0]['title'], self.tables(pid)['总览'][1][8])
            self.assertIn(alts[0]['url'], js['people'][pid]['profileMain'])

    def test_11_neu_guo_is_pending_no_main_profile_or_shortcut(self):
        pid = 'neu-guolixin'; person = self.ps[pid]; js = self.consumers()
        self.assertEqual(person['profile_status'], 'roster_identity_pending')
        self.assertEqual(person['source_profile_status'], 'pending_official_index_only')
        self.assertIs(person['detail_count_eligible'], False)
        self.assertIs(person['navigation_verified'], False)
        self.assertEqual(person['employment_status'], 'unknown')
        for key in ('education','appointments','mentors','publications'):
            self.assertEqual(person[key], [])
        self.assertEqual(len(person['pending_education_candidates']), 2)
        self.assertEqual(len(person['pending_appointment_candidates']), 5)
        self.assertEqual(js['people'][pid]['officialUrl'], '')
        self.assertIn('此名录记录尚未绑定个人档案', js['people'][pid]['profileMain'])
        self.assertFalse(js['rosters'][pid]['matched'])
        self.assertNotIn('进入已核实身份的人物档案', js['rosters'][pid]['html'])
        self.assertNotIn('人物身份已匹配', js['rosters'][pid]['html'])

    def test_12_neu_roster_index_never_upgrades_to_direct_profile_link(self):
        units = {u['id']:u for u in self.d['org_units']}
        institute = units['neu-mechanical-vehicle-engineering']
        self.assertEqual(institute['type'], 'institute')
        self.assertEqual(institute['parent_id'], 'neu-mechanical-engineering-automation')
        self.assertEqual(institute['evidence_status'], 'official_search_index_professional_excerpt_read')
        for pid in ('neu-chenzeyu','neu-guolixin','neu-liangzhongchao'):
            person = self.ps[pid]; entry = self.entries[pid]
            self.assertNotEqual(person['identity_evidence']['status'], 'official_roster_explicit_profile_link')
            self.assertEqual(entry['verification_status'], 'reviewed_official_index_only_no_direct_profile_link_verified')
            self.assertEqual(entry['source_evidence_status'], 'official_search_index_professional_excerpt_read')
            self.assertIsNone(entry['official_profile_url'])
            self.assertIsNot(entry.get('profile_link_from_roster_verified'), True)
            self.assertIsNone(entry['verified_person_id'])
            self.assertFalse(entry['profile_identity_verified'])
        for pid in ('neu-chenzeyu','neu-liangzhongchao'):
            self.assertEqual(self.ps[pid]['source_profile_status'], 'body_verified_profile_roster_index_only')
            self.assertEqual(self.consumers()['people'][pid]['officialUrl'], self.ps[pid]['official_url'])
            self.assertTrue(self.ps[pid]['navigation_verified'])

    def test_13_neu_award_precision_and_visits_are_not_inferred_degrees(self):
        self.assertEqual(self.event('neu-chenzeyu',1)['degree'], '本科')
        self.assertIsNone(self.event('neu-chenzeyu',1)['degree_awarded'])
        self.assertEqual(self.event('neu-liangzhongchao',3)['degree_awarded_date'], '2015-01')
        for pid in ('neu-chenzeyu','neu-liangzhongchao'):
            event = self.event(pid,4)
            self.assertEqual(event['event_kind'], 'academic_visit')
            self.assertIs(event['degree_awarded'], False)
            self.assertFalse(self.consumers()['people'][pid]['doctorate']['overseas'])
        self.assertEqual(self.ps['neu-chenzeyu']['appointments'][2]['start'], '2023-01')
        self.assertEqual(self.ps['neu-liangzhongchao']['appointments'][2]['start'], '2024-01')

    def test_14_markou_foreign_index_doctorate_and_adviser_stay_candidates(self):
        pid = 'tongji-george-markou'; person = self.ps[pid]
        self.assertEqual(person['publications'], [])
        self.assertEqual(person['mentors'], [])
        self.assertIsNone(self.event(pid,1)['start'])
        self.assertEqual(self.event(pid,1)['end'], '2011')
        self.assertIsNone(self.event(pid,1)['degree_awarded'])
        self.assertEqual(self.event(pid,3)['degree'], '土木工程五年制学位')
        self.assertNotIn(self.event(pid,3).get('degree_category'), ('bachelor','master','doctor'))
        candidate = person['pending_education_candidates'][0]
        self.assertEqual((candidate['start'],candidate['end']), ('2005','2011-01'))
        self.assertIsNone(candidate['degree_awarded'])
        self.assertEqual(person['pending_mentor_candidates'][0]['name'], 'Manolis Papadrakakis')
        self.assertEqual(person['pending_mentor_candidates'][0]['employment_status'], 'unknown')
        self.assertEqual(self.consumers()['people'][pid]['candidates'], [{'name':'Manolis Papadrakakis','url':'','route':''}])
        self.assertTrue(self.consumers()['people'][pid]['doctorate']['not_recorded'])

    def test_15_markou_research_associate_not_invented_second_full_time_post(self):
        person = self.ps['tongji-george-markou']
        self.assertEqual(person['appointments'][0]['start'], '2026-09')
        self.assertEqual(person['appointments'][2]['end'], '2024')
        self.assertIs(person['appointments'][2]['current'], False)
        affiliation = person['appointments'][4]
        self.assertEqual(affiliation['employment_type'], 'research_associate_affiliation')
        self.assertIsNone(affiliation['start'])
        self.assertIs(affiliation['personnel_status_verified'], False)
        self.assertNotEqual(affiliation['source_id'], 'up-georgemarkou-index')
        for row in person['appointments']:
            self.assertIs(row['personnel_status_verified'], False)
            self.assertNotEqual(row['employment_type'], 'full_time')

    def test_16_tongji_dates_conflicts_and_historical_institutions_are_preserved(self):
        doctorate = self.event('tongji-chenjianbing',3)
        self.assertEqual(doctorate['end'], '2002-06')
        self.assertEqual(doctorate['degree_awarded_date'], '2002')
        for number in (4,5,6):
            event = self.event('tongji-chenjianbing',number)
            self.assertIsNone(event['start']); self.assertIsNone(event['end'])
        bachelor = self.event('tongji-chenjun',1)
        self.assertEqual(bachelor['institution'], '郑州工学院')
        self.assertEqual(bachelor['end'], '1993-09')
        self.assertEqual(bachelor['conflicting_evidence'][0]['value'], '1993-07')
        self.assertEqual(bachelor['field_status']['end'], 'conflicting_official_sources')
        self.assertNotEqual(bachelor['institution_985'], 'yes')
        for number,year in ((5,'2007'),(6,'2011'),(7,'2013')):
            event = self.event('tongji-chenjun',number)
            self.assertEqual((event['start'],event['end']), (year,year))
            self.assertIs(event['degree_awarded'], False)
        person = self.ps['tongji-chenjun']
        self.assertIsNone(person['appointments'][0]['start'])
        self.assertEqual((person['appointments'][1]['title'],person['appointments'][1]['start']), ('留校任教','1999-10'))

    def test_17_original_organization_scope_no_fabricated_campus_or_professor_unit(self):
        units = {u['id']:u for u in self.d['org_units']}
        for oid,(shape,expected) in ORG_FINGERPRINTS.items():
            self.assertEqual(object_sha(project_source_shape(units[oid],shape)), expected, oid)
        self.assertEqual({u['id'] for u in self.d['org_units'][211:218]}, set(ORG_FINGERPRINTS))
        for person in self.new:
            self.assertEqual(person['campus_ids'], [])
            self.assertIsNone(person['campus'])
            self.assertEqual(person['department_id'], person['organization_id'])
            self.assertIn(person['department_id'], EXPECTED_ORG_IDS[person['school_id']])
            self.assertEqual(self.entries[person['person_id']]['campus_ids'], [])
            self.assertIsNone(self.entries[person['person_id']]['campus_id'])
        self.assertEqual(units['tongji-civil-building-engineering']['type'], 'department')
        self.assertEqual(units['cau-biology-plant-science']['type'], 'department')

    def test_18_selected_roster_order_and_exact_source_scope_are_not_complete_rosters(self):
        for school in SCHOOLS:
            expected = [pid for pid in SOURCE_FINGERPRINTS if pid.startswith(school+'-')]
            rows = [e for e in self.r['entries'] if e.get('source_person_id') in expected]
            self.assertEqual([e['source_person_id'] for e in rows], expected)
            self.assertEqual([e['id'] for e in rows], [EXPECTED_ROSTER_IDS[pid] for pid in expected])
            bid = school + '-selected-roster-rotation-002'
            batch = next(b for b in self.r['batches'] if b['batch_id']==bid)
            self.assertEqual(batch['selection'], EXPECTED_SCOPES[school])
            self.assertEqual(batch['record_count'], 3)
            self.assertEqual(batch['raw_observation_count'], 3)
            self.assertEqual(batch['count_scope'], 'selected_subset_only')
            self.assertIs(batch['coverage_complete'], False)
            coverage = [c for c in self.r['coverage'] if c.get('batch_id')==bid]
            self.assertEqual(sum(c['selected_observation_count'] for c in coverage), 3)
            for row in coverage:
                self.assertEqual(row['selection'], EXPECTED_SCOPES[school])
                self.assertEqual(row['count_scope'], 'selected_subset_only')
                self.assertIsNone(row['full_source_visible_name_count'])
                self.assertIs(row['all_visible_entries_captured'], False)
                self.assertIs(row['coverage_complete'], False)
            for entry in rows:
                self.assertEqual(entry['selection_status'], 'selected_subset')
        self.assertIs(self.r['totals']['current_employment_count_verified'], False)
        self.assertIs(self.r['totals']['not_unique_people_count'], True)

    def test_19_recursive_source_and_event_closure_includes_candidate_evidence(self):
        observations = {o['observation_id']:o for o in self.r['source_observations']}
        for person in self.new:
            self.assertTrue(assert_source_closure(person), person['person_id'])
            entry = self.entries[person['person_id']]
            self.assertEqual(entry['id'], person['roster_entry_id'])
            self.assertEqual(entry['school_id'], person['school_id'])
            self.assertEqual(entry['organization_id'], person['department_id'])
            self.assertEqual(len(entry['source_observation_ids']), 1)
            observation = observations[entry['source_observation_ids'][0]]
            self.assertEqual(observation['record_id'], entry['id'])
            self.assertEqual(observation['source_payload']['source_person_id'], person['person_id'])
            self.assertEqual(observation['source_payload']['source_evidence_status'], entry['source_evidence_status'])
            self.assertEqual(observation['source_payload']['source_identity_evidence'], person['identity_evidence'])

    def test_20_publications_are_seventeen_exact_official_selected_citations(self):
        publications = [q for p in self.pro for q in p['publications']]
        self.assertEqual(Counter(q['type'] for q in publications), {'journal_article':17})
        for person in self.new:
            self.assertLessEqual(len(person['publications']), 2)
            for publication in person['publications']:
                self.assertIs(publication['individual_article_link_verified'], False)
                self.assertNotEqual(publication['link_status'], 'full_text_verified')
                self.assertTrue(publication['type_label'])
                self.assertTrue(publication['link_status_label'])
                self.assertIsNone(publication['doi'])

    def test_21_excel_main_rows_exclude_candidates_keep_sources_and_tristates(self):
        for person in self.pro:
            tables = self.tables(person['person_id'])
            self.assertEqual(list(tables), ['总览','经历','导师','论文','来源'])
            self.assertEqual(len(tables['经历']), 1+len(person['education'])+len(person['appointments']))
            self.assertEqual(len(tables['导师']), 1+len(person['mentors']))
            self.assertEqual(len(tables['论文']), 1+len(person['publications']))
            for event,row in zip(person['education'], tables['经历'][1:]):
                self.assertEqual(row[1], event['event_kind'])
                self.assertEqual(row[3], event['institution'])
                self.assertEqual(row[4:6], [event['start'],event['end']])
                self.assertEqual(row[10], event['institution_985'])
                self.assertIs(row[11], event['degree_awarded'])
                self.assertEqual(row[12], event['degree_awarded_date'])
                self.assertEqual(row[14], event.get('note'))
                self.assertEqual(row[16], event['source_url'])
            for name,rows in tables.items():
                self.assertTrue(all(row[-2]==person['school_id'] for row in rows[1:]), name)

    def test_22_real_graphs_and_mentor_shortcuts_do_not_promote_candidates(self):
        js = self.consumers()['people']
        for person in self.pro:
            graph = js[person['person_id']]['graph']
            self.assertIn(f"{len(person['mentors'])}条已收录关系", graph)
            self.assertEqual(graph.count('href="#mentor-'), len(person['mentors']))
            for mentor in person['mentors']:
                self.assertIn(mentor['name'], graph)
            for mentor in person.get('pending_mentor_candidates', []):
                self.assertNotIn(mentor['name'], graph)
            for candidate in js[person['person_id']]['candidates']:
                self.assertEqual(candidate['url'], '')
                self.assertEqual(candidate['route'], '')

    def test_23_school_statistics_use_records_not_selected_or_full_staff(self):
        js = self.consumers()
        for school in SCHOOLS:
            self.assertEqual(js['schoolStats'][school]['people'], sum(p['school_id']==school for p in self.d['people']))
            self.assertEqual(js['schoolStats'][school]['pending'], sum(p['school_id']==school for p in self.d['pending_people']))
            self.assertEqual(js['schoolStats'][school]['status'], '部分收录')
            self.assertIn('统计不代表全校教师或学院总数', js['schoolPages'][school])
            self.assertIn('非完整名录', js['schoolPages'][school])

    def test_24_validators_exports_and_consumers_are_nonmutating(self):
        before = copy.deepcopy((self.d,self.r))
        self.assertTrue(build.validate(self.d))
        self.assertTrue(validate_rosters(self.r,self.d))
        for person in self.pro:
            self.tables(person['person_id'])
        self.assertEqual((self.d,self.r), before)
        self.assertTrue(self.consumers()['unchanged'])

    def test_25_source_guard_detects_lost_candidates_dates_and_index_upgrades(self):
        pid='cau-wuweihua'; shape,expected=SOURCE_FINGERPRINTS[pid]
        for mutation in ('award','date','tier','promote'):
            person=source_view(self.ps[pid])
            if mutation=='award': person['pending_education_candidates'][2]['degree_awarded']=True
            elif mutation=='date': person['pending_education_candidates'][2]['start']='1987-12'
            elif mutation=='tier': person['sources'][2]['evidence_status']='official_public_body_read'
            else: person['education']=[person['pending_education_candidates'][2]]
            if mutation=='promote':
                with self.assertRaises(AssertionError): project_source_shape(person,shape)
            else: self.assertNotEqual(object_sha(project_source_shape(person,shape)),expected)
        person=source_view(self.ps[pid]); del person['pending_education_candidates'][3]['start_date_conflict']
        with self.assertRaises(KeyError): project_source_shape(person,shape)

    def test_26_closure_guard_catches_candidate_and_provenance_corruption(self):
        pid='cau-wuweihua'
        for mutation in ('source','url','provenance','candidate_event','main_edge'):
            person=copy.deepcopy(self.ps[pid])
            if mutation=='source': person['pending_mentor_candidates'][0]['source_id']='unknown'
            elif mutation=='url': person['pending_education_candidates'][0]['source_url']='https://wrong.example.test/'
            elif mutation=='provenance': person['pending_education_candidates'][0]['field_provenance']['institution']='unknown'
            elif mutation=='candidate_event': person['pending_mentor_candidates'][0]['education_event_id']='unknown'
            else: person['mentors']=[person['pending_mentor_candidates'][0]]
            with self.assertRaises(AssertionError, msg=mutation): assert_source_closure(person)

    def test_27_public_new_records_have_no_private_caches_local_paths_or_contact_fields(self):
        forbidden={'public_raw_cache','local_evidence_cache','cache_path','raw_html','raw_pdf','pdf_bytes','raw_response','email','phone','mobile','birthday','date_of_birth','student_list','students'}
        def check(value):
            if isinstance(value,dict):
                self.assertFalse(forbidden.intersection(value), forbidden.intersection(value))
                for child in value.values(): check(child)
            elif isinstance(value,list):
                for child in value: check(child)
            elif isinstance(value,str):
                self.assertNotIn('/workspace/',value)
                self.assertNotIn('/home/agent/',value)
                self.assertFalse(value.startswith('file://'))
        check(self.new)
        check(list(self.entries.values()))


    def test_28_ecnu_bai_combined_study_joint_training_and_role_types_remain_distinct(self):
        person = self.ps['ecnu-baikaixu']
        self.assertEqual(len(person['education']), 3)
        self.assertEqual([e['degree'] for e in person['education']], ['学士','博士',None])
        self.assertEqual((person['education'][1]['start'], person['education'][1]['end']), ('2009-09','2015-12'))
        joint = self.event('ecnu-baikaixu',3)
        self.assertEqual(joint['event_kind'], 'joint_training')
        self.assertIs(joint['degree_awarded'], False)
        self.assertEqual((joint['start'],joint['end']), ('2013-09','2015-09'))
        self.assertTrue(all(e['field'] is None for e in person['education']))
        self.assertEqual(self.consumers()['people']['ecnu-baikaixu']['stages'], {'bachelor':[],'master':[],'doctor':[]})
        self.assertEqual([a['employment_type'] for a in person['appointments'][3:]], ['administrative_role','temporary_secondment','part_time_affiliation'])
        self.assertEqual(person['appointments'][4]['end'], '2025-12')
        self.assertIs(person['appointments'][4]['current'], False)
        for appointment in person['appointments']:
            self.assertIs(appointment['personnel_status_verified'], False)
            self.assertNotEqual(appointment['employment_type'], 'full_time')

    def test_29_ecnu_bi_overlapping_2009_roles_and_thesis_year_are_not_repaired(self):
        person = self.ps['ecnu-bichunjuan']
        lecturer, associate = person['appointments'][:2]
        self.assertEqual((lecturer['title'],lecturer['end']), ('讲师','2009-12'))
        self.assertEqual((associate['title'],associate['start']), ('副教授','2009-01'))
        self.assertEqual(lecturer['field_status']['end'], 'source_reported_with_internal_overlap')
        self.assertEqual(associate['field_status']['start'], 'source_reported_with_internal_overlap')
        doctorate = self.event('ecnu-bichunjuan',3)
        self.assertEqual(doctorate['end'], '2004-06')
        self.assertIsNone(doctorate['degree_awarded'])
        self.assertIsNone(doctorate['degree_awarded_date'])
        self.assertEqual(doctorate['event_kind'], 'degree_study')
        mentor = person['mentors'][0]
        self.assertIsNone(mentor['start']); self.assertIsNone(mentor['end'])
        self.assertIn('2005', mentor['note'])
        self.assertNotEqual(doctorate['source_id'], mentor['source_id'])
        self.assertEqual(mentor['education_event_id'], doctorate['event_id'])
        self.assertEqual(mentor['field_provenance']['education_event_id'], 'ecnu-graduate-thesis-author-supervisor-table')
        self.assertTrue(assert_source_closure(person))

    def test_30_ecnu_historical_xu_edge_has_honest_retirement_label_and_no_shortcut(self):
        pid='ecnu-bichunjuan'; mentor=self.ps[pid]['mentors'][0]; rendered=self.consumers()['people'][pid]
        self.assertEqual(mentor['name'], '许世远')
        self.assertEqual(mentor['source_employment_status'], 'retired_or_emeritus_officially_listed')
        self.assertEqual(mentor['employment_status'], 'retired_or_emeritus_officially_listed')
        self.assertEqual(mentor['relationship_status'], 'verified_direct_statement')
        self.assertIs(mentor['include_in_mentorship_graph'], True)
        self.assertIs(mentor['include_in_verified_mentor_count'], True)
        self.assertIs(mentor['navigation_verified'], False)
        self.assertIs(mentor['quick_link_eligible'], False)
        self.assertIsNone(mentor['official_url']); self.assertIsNone(mentor['person_id'])
        self.assertEqual(rendered['mentors'], [{'name':'许世远','url':'','route':'','events':['ecnu-bichunjuan-education-3']}])
        self.assertIn('1条已收录关系', rendered['graph'])
        self.assertIn('许世远', rendered['graph'])
        self.assertIn('官方离退休／荣休名录（非在职）', rendered['lineage'])
        self.assertEqual(build.mentor_official_url(mentor), '')
        self.assertEqual(self.tables(pid)['导师'][1][7], '')
        self.assertFalse(any(p['name']=='许世远' for p in self.new))
        forged=dict(mentor, official_url='https://example.edu.test/profile', navigation_verified=True, quick_link_eligible=True)
        self.assertEqual(build.mentor_official_url(forged), '')

    def test_31_ecnu_cui_explicit_award_year_does_not_borrow_cv_end_month(self):
        pid='ecnu-cuican'; doctorate=self.event(pid,3); postdoc=self.event(pid,4)
        self.assertEqual((doctorate['start'],doctorate['end']), ('2010-11','2015-03'))
        self.assertEqual(doctorate['degree_awarded_date'], '2015')
        self.assertIs(doctorate['degree_awarded'], True)
        self.assertEqual(doctorate['field_provenance']['end'], 'acsp-cuican-2015-cv')
        self.assertEqual(doctorate['field_provenance']['degree_awarded_date'], 'iacp-cuican-2021-member-update')
        self.assertEqual(postdoc['institution'], '哈佛大学')
        self.assertEqual((postdoc['start'],postdoc['end']), ('2015-09','2016'))
        self.assertIs(postdoc['degree_awarded'], False)
        self.assertEqual(postdoc['event_kind'], 'postdoctoral_research')
        self.assertEqual(self.consumers()['people'][pid]['stages']['doctor'], ['ecnu-cuican-education-3'])
        self.assertTrue(self.consumers()['people'][pid]['doctorate']['overseas'])
        self.assertEqual(self.ps[pid]['mentors'], [])
        for event in self.ps[pid]['education']:
            self.assertNotIn('uu.nl', event['source_url'])

    def test_32_ecnu_cui_current_geography_does_not_retroject_2021_organization(self):
        person=self.ps['ecnu-cuican']
        self.assertEqual(person['department_id'], 'ecnu-geography')
        self.assertEqual(person['department'], '地理科学学院')
        talent,professor,parttime,administration,research=person['appointments']
        self.assertEqual((talent['institution'],talent['title'],talent['start'],talent['end']), ('华东师范大学','紫江青年学者','2016','2021'))
        self.assertEqual((professor['institution'],professor['title'],professor['start']), ('华东师范大学','教授','2021'))
        self.assertEqual((parttime['institution'],parttime['start'],parttime['end'],parttime['employment_type']), ('中山大学城市化研究院','2015-06','2018','part_time_affiliation'))
        self.assertEqual(administration['employment_type'], 'concurrent_administrative_role')
        self.assertEqual(research['employment_type'], 'concurrent_research_affiliation')
        for appointment in (administration,research):
            self.assertIsNone(appointment['start']); self.assertIsNone(appointment['end'])
        for appointment in person['appointments']:
            self.assertEqual(appointment['source_id'], 'ecnu-cuican-profile')
            self.assertIs(appointment['personnel_status_verified'], False)
            self.assertNotEqual(appointment['employment_type'], 'full_time')
        self.assertEqual(parttime['field_provenance']['start'], 'acsp-cuican-2015-cv')

    def test_33_ecnu_only_three_selected_people_one_real_unit_and_historical_sources(self):
        people=[p for p in self.new if p['school_id']=='ecnu']
        self.assertEqual([p['name'] for p in people], ['白开旭','毕春娟','崔璨'])
        self.assertEqual(EXPECTED_ORG_IDS['ecnu'], ['ecnu-geography'])
        self.assertEqual({key:sum(len(p[key]) for p in people) for key in ('education','appointments','mentors','publications')}, {'education':12,'appointments':14,'mentors':1,'publications':3})
        self.assertEqual(Counter(e['degree_awarded'] for p in people for e in p['education']), {True:1,None:7,False:4})
        for person in people:
            self.assertEqual(person['source_profile_status'], 'body_verified_professional_profile')
            self.assertIs(person['complete_profile_count_eligible'], False)
            self.assertEqual(person['campus_ids'], [])
            self.assertIsNone(person['campus'])
            self.assertEqual(len(person['publications']), 1)
            self.assertEqual(self.entries[person['person_id']]['source_evidence_status'], 'official_roster_body_read')
        sources={s['id']:s for s in self.ps['ecnu-cuican']['sources']}
        self.assertEqual(sources['acsp-cuican-2015-cv']['source_type'], 'official_professional_association_hosted_primary_cv')
        self.assertEqual(sources['iacp-cuican-2021-member-update']['source_type'], 'official_professional_association_member_update')
        self.assertIn('2015', sources['acsp-cuican-2015-cv']['access_note'])
        self.assertEqual(SOURCE_PACKAGE_SHA256['ecnu'], 'c14da5f35e262af10821f328114fcf497cb348c8c17dcd03254407e3b8fb02c0')
        self.assertEqual(REVIEW_SHA256['ecnu'], 'f970f4170264f778aaa70bb0194f4cd7dc27448d29269f3329ffa7eabfee1ea6')


if __name__ == '__main__':
    unittest.main(verbosity=2)
