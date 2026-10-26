"""Third rotation release: independently pinned source and consumer boundaries.

Copy into a release's tests/. No research files, normalization scripts, browser,
network, or frozen baseline are needed at test time. To run this research copy,
set ACADEMIC_ATLAS_TEST_ROOT to the prepared release. The Node harness executes
real model, roster, profile, and graph consumers using only in-memory fixtures.
No build or workbook writes occur. Fingerprints were derived from the nine
independently reviewed 2026-10-23 source packages, not normalized output.
Private local_evidence_cache references are deliberately excluded, not published.
"""
from atlas_test_io import load_atlas
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

SCHOOLS = ('cqu', 'lzu', 'nwpu', 'nwsuaf', 'scu', 'scut', 'sysu', 'uestc', 'xjtu')

PENDING_IDS = ('scu-lianggemeng', 'sysu-gulinyan')

BASELINE_PREFIXES = {'limitations': (6, 'a49996988d143a02303ec539cb493667cdc9b28a287271ae141f6cfd7b95021a'),
 'campuses': (4, 'a29d9956fbbc284b9cdafc640ac9057dd4512c2181d89780a92a6a8bf01e6505'),
 'org_units': (199, '1dd61057cd7639a1d9a41e124bdc2fe65f14a67d7cac2add29a9abe6728293da'),
 'people': (499, '666d83e6cb01ebd028d9c58b32f6f0431009010e4f8fe225fad8c6a98ee5bd90'),
 'profile_batches': (117, '22b98f6ae34f6b77c3d7ab522e1728db72454f37fd63dd60105a9a9db35cb521'),
 'pending_people': (80, '3bb9f8a8eae95f1d35881fc383e02a84ce212bca04faee4267cdec31b87f0dfc'),
 'normalization_evidence': (10, '27f4a79ae5bcd7666015cfe5829c2dcd56b3a8e3c0452a678d7e1aa5f1b9421a'),
 'institutions': (39, '8234ea78331d931b8a54c5f40d4427a7844e7fcd621d0832a69e5f2df1b41848')}

BASELINE_UNCHANGED = {'schema_version': '5a4747fcdafec66d8d8812022e3b7d2666d886ec0e0ee7926ec8c50db40f29d5',
 'institution': '9b9fab8a1164afafcf855e8d6ccea17a09e973b8ea2fd8a4831ad681490e8d01',
 'coverage': '8301d88ec52e91fd40964298ce12e179dc0c4ca513b3a0cefa9ad57db895f597'}

BASELINE_ROSTER_PREFIXES = {'summary': (124, '0668ff0260e3f83565f42cea57e4eaca8b3d3eaafd9272cd7cf5a20e898b1519'),
 'coverage': (195, '4f91046bc35f91e70c45395d22199ae398e310e7d6cb9d12279d3d9abea1b40c'),
 'entries': (1661, '56b58e5ece330bffb71d3e0669ae619a8285e790bbb17d3ece2f3630baddec4d'),
 'conflicts': (30, '0f809e3a2c4ef1857b03479230f35a342b703ccf5f8a99ef032271d150c44c09'),
 'limitations': (35, '4fe8dea8da59fb3789194955a1b22aac4453cbf0e6a4d1cc2e82d172ba77c116'),
 'dedup_candidates': (60, '0a1adbff0d7b0ae2fe42cceff9a89e5e9eb6d164044456f319cfab6c9d1b1653'),
 'exclusions': (3, '89dc768c034efe9de60bb4199c92be749ea7f1bb1405daceff0e3ca88fa5228d'),
 'pending_checks': (2, '143ba1254ce843007ed487ca7f7ef2c684912b54c0580c6bb3f7157b7bc61048'),
 'source_snapshots': (36, 'bae26c4aa31edf9ee3212a7723508241f475441863f03f69a8058264ad3b81c2'),
 'batches': (90, '2ab9f28eee7f0c6b03c36a84db9693f3c3fc7a66c58b65f1ce5b879675e0c45f'),
 'source_observations': (1699, '25b6b3b0ed54b3364812dd1126533e568a19ebd33f7ba7be5a1dd52a443934a1'),
 'consolidations': (2, '094423def9986b8e47457a6592e143f75d67eaa7647c2c346df93d54b983e4e0'),
 'supporting_method_evidence': (4, 'db4e111a865957df036ada510d96050eb5c2b39ed6635c628d48a9a2717ec547'),
 'local_mapping_corrections': (4, '9a1ccc7df1e46b7e8240c3963456fcaf0177d07ad31c051db7d1d5334a1aca1d'),
 'withdrawn_local_conflicts': (1, '8b54b3a107c8f050e3c33cc2125a710a4084b1be287fdb20db8ca392c093ed05')}

BASELINE_ROSTER_UNCHANGED = {'schema_version': '5a4747fcdafec66d8d8812022e3b7d2666d886ec0e0ee7926ec8c50db40f29d5',
 'role_interpretation': '9c1098d16b8ae13b4ef55efb781195831efdc1be68fd601aa8c4d1db41cea7c0'}

REGISTRY_SHA256 = '9323dad42fc2c35808ad92888cdffb0ad41edaefaee88c3b57ebb798349c2d62'

EDUCATION_KEYS = ('event_id', 'degree', 'institution', 'start', 'end', 'event_kind', 'degree_awarded', 'degree_awarded_date')

MENTOR_KEYS = ('name',
 'type',
 'education_stage',
 'education_event_id',
 'start',
 'end',
 'date_basis',
 'employment_status',
 'navigation_verified')

SOURCE_FINGERPRINTS = {'cqu-gongqu': (14, 'ae9b25f28abaee36d4b1d43f3eaedac6080456a9819b3a550d7abff79001627b'),
 'cqu-hechuanjiang': (19, '10d3dabfa01b5a6ceac01085018c60e310d713188fe1e6cf0b0dfc042464499a'),
 'cqu-huangxiaojun': (23, '283a2ac89736b9a09ad3333642ee5558550d3223b32d30d899272f3fa2715968'),
 'lzu-changqingquan': (35, 'd6aa5a07140a1af6cd1e17712bc242e0196ea9d678d6bef991bd2c49b4377585'),
 'lzu-chenlizhi': (41, '4e196df4bacb768c6632a832382c6a211627b0d9186449bb72bdd67dc4bbd399'),
 'lzu-chengxiyou': (46, '60c158937b1338e816271ade2a2c1e3dd7c7dcbb7466947fb23010508dae2771'),
 'nwpu-baixueli': (54, '0fc4497628e809a1071794f72993a2bc0653fe37f9fe2685d5414188cd798c44'),
 'nwpu-guoqianqiao': (56, 'c53ba7531b12d0d53530a8b61b8dcd5516485d58500dabbd4fc7ef1ed278e712'),
 'nwpu-libinlong': (62, '054539dee12bb3c805571aa846562044cba95a662eb8aaab7f7fb660f06b9433'),
 'nwsuaf-fengbaili': (64, '9d756472caa76e9cb86a5f174b83ad37dccc4088af4b837ac44651750c3343a4'),
 'nwsuaf-fengyongzhong': (67, '39dc1e6d673ec766784a5cb61894aa9a1ee520f0e21567e7cc2f76854e0aeb9c'),
 'nwsuaf-gaojinfeng': (68, 'ee4dedf04b9c1916a01807a507cfa2a7f9d663b227a558df82435b1ec45311e1'),
 'scu-tangjianhua': (72, 'fcfbd6836b7738b06cc3b2c5220a8c68f71d579b5456fae638f62e0ab96404aa'),
 'scu-lianggemeng': (75, '569eecc05902faaf9bcb24114446ce93c9f8cf69370b845b02fce7936dda5426'),
 'scu-chuliangyin': (82, '691207c41f62c449fe385d334d12fd7b035f818f1c3a06de0f351e701db6553c'),
 'scut-chenbocong': (96, '8b1a9c64ef64b28966736735d61f9f73f68623c68ec981e0ee9f19b2751e2dfd'),
 'scut-chenpei': (105, 'f48b19c7639e7349ef9d25c56b06195b030fb2b5763e0578c92fdd2eed7d141a'),
 'scut-chenyingshan': (113, '1e7af2c5f2edb90bb647b691c30c71c5ffde9086db0adfa2ea5dbea3db85b029'),
 'sysu-gulinyan': (116, '822f45b147471d2d6976ce8753ee543ee73a65ad8e3bfbe8e998af18fb402724'),
 'sysu-chenbingyi': (124, '5813242ea16fc2f8fc207dc87ed0b6c8c041a6820bb7f204e036b0d21b9d75c7'),
 'sysu-chengcheng': (131, '66fad05bd2fc26f2f2b97ca041c8aebfc7f09194aebe76736d14a40e66aee452'),
 'uestc-guyiqi': (139, 'f56454e2afd6d19a5e0a4be28f2091f57628637d63d49d55c6f9b9e8ccc1ca29'),
 'uestc-jonas-kahn': (144, 'aa8ddc6774c24c03356ae18409ade6628e0dafb231e1c44ede56bca4c9e7913e'),
 'uestc-kongefang': (146, '29dcbbeaecb3b03217c5614f739a3ac06c73704840069931789ef510ee726f80'),
 'xjtu-yiyuan': (150, '657ed74110040b844aee782ad2271144b786ef86a3128f19b1b0f11329ed2d58'),
 'xjtu-lidongsheng': (155, 'bcb959ae316d43812d279be6887df3e2e00add62bb6dc9270b74a2ef606366c2'),
 'xjtu-zhangzhengce': (157, 'ba5a6af02a746800113b1004758c928b0d9320efb3c6d8254e48e08af9b185b4')}

EXPECTED_EDUCATION = {'cqu-gongqu': [('cqu-gongqu-education-1', '本科', '重庆大学', None, None, 'degree_study', None, None),
                ('cqu-gongqu-education-2', '硕士', '重庆大学', None, None, 'degree_study', None, None),
                ('cqu-gongqu-education-3', '博士', '重庆大学', None, None, 'degree_study', None, None),
                ('cqu-gongqu-education-4', None, '哥伦比亚大学统计系', None, None, 'education_background', None, None)],
 'cqu-hechuanjiang': [('cqu-hechuanjiang-education-1', '本科', '四川大学', '1981-09', '1985-07', 'degree_study', None, None),
                      ('cqu-hechuanjiang-education-2', '硕士', '四川大学', '1985-09', '1988-07', 'degree_study', None, None),
                      ('cqu-hechuanjiang-education-3', '工学博士', '重庆大学', None, '2004-06', 'degree', True, None)],
 'cqu-huangxiaojun': [('cqu-huangxiaojun-education-1', '本科', '重庆大学', '1993-09', '1997-06', 'degree_study', None, None),
                      ('cqu-huangxiaojun-education-2', '硕士', '重庆大学', '2000-09', '2003-06', 'degree_study', None, None),
                      ('cqu-huangxiaojun-education-3',
                       '理学博士',
                       '四川大学',
                       '2003-09',
                       '2006-07',
                       'degree_study',
                       None,
                       None),
                      ('cqu-huangxiaojun-education-4',
                       None,
                       '中国科学院数学研究所',
                       None,
                       None,
                       'postdoctoral_research',
                       False,
                       None)],
 'lzu-changqingquan': [('lzu-changqingquan-education-1',
                        '博士',
                        '兰州大学',
                        '2015-09',
                        '2019-12',
                        'degree_study',
                        None,
                        None),
                       ('lzu-changqingquan-education-2',
                        '硕士',
                        '兰州大学',
                        '2012-09',
                        '2015-07',
                        'degree_study',
                        None,
                        None),
                       ('lzu-changqingquan-education-3',
                        '本科',
                        '山西大学',
                        '2008-09',
                        '2012-07',
                        'degree_study',
                        None,
                        None),
                       ('lzu-changqingquan-education-4',
                        None,
                        '广州大学',
                        '2020-06',
                        '2025-06',
                        'postdoctoral_research',
                        False,
                        None)],
 'lzu-chenlizhi': [('lzu-chenlizhi-education-1', '博士', '俄克拉荷马州立大学', None, '2014', 'degree_study', None, None),
                   ('lzu-chenlizhi-education-2', '硕士', '兰州大学', None, '2008', 'degree_study', None, None),
                   ('lzu-chenlizhi-education-3', '学士', '兰州大学', None, '2006', 'degree_study', None, None),
                   ('lzu-chenlizhi-education-4',
                    None,
                    '罗格斯大学新布朗斯维克校区',
                    '2017-09',
                    '2018-02',
                    'academic_visit',
                    False,
                    None),
                   ('lzu-chenlizhi-education-5',
                    None,
                    '南开大学陈省身数学研究所',
                    '2014',
                    '2016',
                    'postdoctoral_research',
                    False,
                    None)],
 'lzu-chengxiyou': [('lzu-chengxiyou-education-1', '博士', '兰州大学', '2003-09', '2006-06', 'degree_study', None, None),
                    ('lzu-chengxiyou-education-2', '硕士', '兰州大学', '2001-09', '2003-06', 'degree_study', None, None),
                    ('lzu-chengxiyou-education-3', '学士', '安徽师范大学', '1997-09', '2001-06', 'degree_study', None, None),
                    ('lzu-chengxiyou-education-4',
                     None,
                     'University of New England',
                     '2014-01',
                     '2015-01',
                     'academic_visit',
                     False,
                     None),
                    ('lzu-chengxiyou-education-5',
                     None,
                     '中国科学院数学与系统科学研究院',
                     '2008-06',
                     '2011-03',
                     'postdoctoral_research',
                     False,
                     None)],
 'nwpu-baixueli': [('nwpu-baixueli-education-1', '博士', '大连理工大学', None, '2012', 'degree', True, '2012'),
                   ('nwpu-baixueli-education-2', None, '华东师范大学', '2012', '2015', 'postdoctoral_research', False, None)],
 'nwpu-guoqianqiao': [('nwpu-guoqianqiao-education-1', '硕士', '山东大学', None, '2004-06', 'degree', True, '2004-06'),
                      ('nwpu-guoqianqiao-education-2', '博士', '西北工业大学', None, '2009-12', 'degree', True, '2009-12'),
                      ('nwpu-guoqianqiao-education-3', None, '吉森大学', None, None, 'academic_visit', False, None),
                      ('nwpu-guoqianqiao-education-4', None, '俄克拉荷马大学', None, None, 'academic_visit', False, None)],
 'nwpu-libinlong': [('nwpu-libinlong-education-1', '学士', '西北工业大学', None, '2007', 'degree_study', None, None),
                    ('nwpu-libinlong-education-2', '硕士', '西北工业大学', None, '2010', 'degree_study', None, None),
                    ('nwpu-libinlong-education-3',
                     '博士',
                     'University of Twente',
                     None,
                     '2012',
                     'degree',
                     True,
                     '2012-09-20'),
                    ('nwpu-libinlong-education-4',
                     None,
                     '西波希米亚大学',
                     '2013',
                     '2015',
                     'postdoctoral_research',
                     False,
                     None),
                    ('nwpu-libinlong-education-5', None, '丹麦技术大学', '2016', '2017', 'academic_visit', False, None)],
 'nwsuaf-fengbaili': [('nwsuaf-fengbaili-education-1', '学士', '西北农业大学', None, '1990-07', 'degree', True, '1990-07'),
                      ('nwsuaf-fengbaili-education-2', '硕士', '西北农业大学', None, '1997-07', 'degree', True, '1997-07'),
                      ('nwsuaf-fengbaili-education-3', '博士', '西北农林科技大学', None, '2003-07', 'degree', True, '2003-07')],
 'nwsuaf-fengyongzhong': [('nwsuaf-fengyongzhong-education-1', '博士', None, None, None, 'degree_study', None, None)],
 'nwsuaf-gaojinfeng': [('nwsuaf-gaojinfeng-education-1', '农学学士', '西北农业大学', None, '1999-06', 'degree', True, '1999-06'),
                       ('nwsuaf-gaojinfeng-education-2', '硕士', '西北农林科技大学', None, '2008', 'degree', True, '2008'),
                       ('nwsuaf-gaojinfeng-education-3', '农学博士', '西北农林科技大学', None, '2014', 'degree', True, '2014'),
                       ('nwsuaf-gaojinfeng-education-4',
                        None,
                        '马里兰大学（University of Maryland）',
                        '2010-03',
                        '2011-06',
                        'academic_visit',
                        False,
                        None)],
 'scu-tangjianhua': [('scu-tangjianhua-education-1', None, '泸州化工学校', '1986-09', '1990-07', 'degree_study', None, None),
                     ('scu-tangjianhua-education-2', '硕士', '四川大学', '1995-09', '1998-06', 'degree_study', None, None),
                     ('scu-tangjianhua-education-3', '博士', '四川大学', '1998-09', '2002-06', 'degree_study', None, None)],
 'scu-lianggemeng': [],
 'scu-chuliangyin': [('scu-chuliangyin-education-1', '本科', '成都科技大学', '1985-09', '1989-07', 'degree_study', None, None),
                     ('scu-chuliangyin-education-2', '硕士', '成都科技大学', '1989-07', '1992-03', 'degree_study', None, None),
                     ('scu-chuliangyin-education-3', '博士', '东北大学', '1992-03', '1995-03', 'degree_study', None, None),
                     ('scu-chuliangyin-education-4',
                      None,
                      '四川大学',
                      '1995-04',
                      '1997-06',
                      'postdoctoral_research',
                      False,
                      None),
                     ('scu-chuliangyin-education-5',
                      None,
                      '东京大学',
                      '1999-10',
                      '2001-09',
                      'postdoctoral_research',
                      False,
                      None),
                     ('scu-chuliangyin-education-6', None, '哈佛大学', '2006-08', '2007-02', 'academic_visit', False, None),
                     ('scu-chuliangyin-education-7',
                      None,
                      '巴黎高等物理化工学院（ESPCI）',
                      '2007-12',
                      '2008-02',
                      'academic_visit',
                      False,
                      None),
                     ('scu-chuliangyin-education-8',
                      None,
                      '伯明翰大学',
                      '2011-11',
                      '2011-12',
                      'academic_visit',
                      False,
                      None)],
 'scut-chenbocong': [('scut-chenbocong-education-1', '博士', '华中师范大学', None, '2013-06', 'degree', True, '2013'),
                     ('scut-chenbocong-education-2',
                      None,
                      '南洋理工大学',
                      '2013-08',
                      '2015-09',
                      'postdoctoral_research',
                      False,
                      None)],
 'scut-chenpei': [('scut-chenpei-education-1', '学士', '北京大学', '2007-09', '2011-06', 'degree', True, None),
                  ('scut-chenpei-education-2', '硕士', '北京大学', '2011-09', '2014-06', 'degree', True, None),
                  ('scut-chenpei-education-3', '博士', '华南理工大学', '2015-09', '2018-07', 'degree', True, None),
                  ('scut-chenpei-education-4',
                   None,
                   '加利福尼亚大学洛杉矶分校',
                   '2017-10',
                   '2018-10',
                   'joint_doctoral_training',
                   False,
                   None),
                  ('scut-chenpei-education-5',
                   None,
                   '华南理工大学',
                   '2018-07',
                   '2021-07',
                   'postdoctoral_research',
                   False,
                   None)],
 'scut-chenyingshan': [('scut-chenyingshan-education-1',
                        '学士',
                        '华南师范大学',
                        '2002-09',
                        '2006-07',
                        'degree_study',
                        None,
                        None),
                       ('scut-chenyingshan-education-2',
                        '硕士',
                        '华南师范大学',
                        '2006-09',
                        '2009-07',
                        'degree_study',
                        None,
                        None),
                       ('scut-chenyingshan-education-3',
                        '博士',
                        '新加坡国立大学',
                        '2009-08',
                        '2013-08',
                        'degree_study',
                        None,
                        None),
                       ('scut-chenyingshan-education-4',
                        None,
                        '华南理工大学',
                        '2015-01',
                        '2017-01',
                        'postdoctoral_research',
                        False,
                        None)],
 'sysu-gulinyan': [],
 'sysu-chenbingyi': [('sysu-chenbingyi-education-1', '博士', '清华大学', '2016', None, 'degree_study', None, None),
                     ('sysu-chenbingyi-education-2',
                      None,
                      '清华大学丘成桐数学科学中心',
                      None,
                      None,
                      'postdoctoral_research',
                      False,
                      None)],
 'sysu-chengcheng': [('sysu-chengcheng-education-1',
                      '博士',
                      'University of Central Florida',
                      None,
                      '2017',
                      'degree_study',
                      None,
                      None),
                     ('sysu-chengcheng-education-2',
                      None,
                      'Duke University',
                      None,
                      None,
                      'postdoctoral_research',
                      False,
                      None)],
 'uestc-guyiqi': [('uestc-guyiqi-education-1', '学士', '浙江大学', '2008-09', '2012-06', 'degree_study', None, None),
                  ('uestc-guyiqi-education-2',
                   '硕士',
                   '华盛顿大学（University of Washington, Seattle）',
                   '2012-09',
                   '2014-03',
                   'degree_study',
                   None,
                   None),
                  ('uestc-guyiqi-education-3', '博士', '普渡大学', '2014-08', '2019-08', 'degree_study', None, None),
                  ('uestc-guyiqi-education-4', None, '新加坡国立大学', None, None, 'postdoctoral_research', False, None)],
 'uestc-jonas-kahn': [('uestc-jonas-kahn-education-1',
                       '博士',
                       '巴黎第十一大学（Paris-Sud/Orsay）',
                       None,
                       None,
                       'degree',
                       True,
                       None),
                      ('uestc-jonas-kahn-education-2', '博士', '莱顿大学', None, None, 'degree', True, None)],
 'uestc-kongefang': [('uestc-kongefang-education-1', '学士', '上海师范大学', '1995-09', '1999-06', 'degree_study', None, None),
                     ('uestc-kongefang-education-2', '硕士', '北京师范大学', '1999-09', '2002-06', 'degree_study', None, None),
                     ('uestc-kongefang-education-3', '博士', '新加坡国立大学', '2002-07', '2006-07', 'degree_study', None, None),
                     ('uestc-kongefang-education-4',
                      None,
                      '埃因霍温理工大学',
                      '2007-01',
                      '2008-12',
                      'postdoctoral_research',
                      False,
                      None)],
 'xjtu-yiyuan': [('xjtu-yiyuan-education-1', '博士', None, None, None, 'degree_study', None, None)],
 'xjtu-lidongsheng': [('xjtu-lidongsheng-education-1', '博士', '西安交通大学', None, '2000-06', 'degree', True, '2000-06'),
                      ('xjtu-lidongsheng-education-2',
                       None,
                       '爱荷华大学',
                       '2005-01',
                       '2005-05',
                       'academic_visit',
                       False,
                       None),
                      ('xjtu-lidongsheng-education-3',
                       None,
                       '爱荷华大学',
                       '2006-08',
                       '2007-05',
                       'academic_visit',
                       False,
                       None),
                      ('xjtu-lidongsheng-education-4',
                       None,
                       '香港中文大学数学科学研究所',
                       '2009-06',
                       '2009-08',
                       'academic_visit',
                       False,
                       None),
                      ('xjtu-lidongsheng-education-5',
                       None,
                       '爱荷华大学',
                       '2010-04',
                       '2010-05',
                       'academic_visit',
                       False,
                       None),
                      ('xjtu-lidongsheng-education-6',
                       None,
                       '华盛顿大学',
                       '2010-05',
                       '2010-06',
                       'academic_visit',
                       False,
                       None),
                      ('xjtu-lidongsheng-education-7',
                       None,
                       '澳大利亚国立大学',
                       '2011-07',
                       '2011-08',
                       'academic_visit',
                       False,
                       None),
                      ('xjtu-lidongsheng-education-8',
                       None,
                       '华盛顿大学',
                       '2011-12',
                       '2011-12',
                       'academic_visit',
                       False,
                       None),
                      ('xjtu-lidongsheng-education-9',
                       None,
                       '爱荷华大学',
                       '2012-04',
                       '2012-05',
                       'academic_visit',
                       False,
                       None),
                      ('xjtu-lidongsheng-education-10',
                       None,
                       '华盛顿大学',
                       '2012-05',
                       '2012-06',
                       'academic_visit',
                       False,
                       None),
                      ('xjtu-lidongsheng-education-11',
                       None,
                       'Albeta大学（原文拼写）',
                       '2015-10',
                       '2015-10',
                       'academic_visit',
                       False,
                       None),
                      ('xjtu-lidongsheng-education-12',
                       None,
                       'Georgia理工（原文机构名）',
                       '2015-10',
                       '2015-10',
                       'academic_visit',
                       False,
                       None),
                      ('xjtu-lidongsheng-education-13',
                       None,
                       '普林斯顿大学',
                       '2015-10',
                       '2015-10',
                       'academic_visit',
                       False,
                       None),
                      ('xjtu-lidongsheng-education-14',
                       None,
                       '华盛顿大学',
                       '2016-01',
                       '2016-01',
                       'academic_visit',
                       False,
                       None),
                      ('xjtu-lidongsheng-education-15',
                       None,
                       '首尔国立大学',
                       '2017-12',
                       '2017-12',
                       'academic_visit',
                       False,
                       None),
                      ('xjtu-lidongsheng-education-16',
                       None,
                       '首尔国立大学',
                       '2018-01',
                       '2018-01',
                       'academic_visit',
                       False,
                       None)],
 'xjtu-zhangzhengce': [('xjtu-zhangzhengce-education-1', '学士', '河南师范大学', None, '1997', 'degree_study', None, None),
                       ('xjtu-zhangzhengce-education-2', '硕士', '河南师范大学', None, '2000', 'degree', True, None),
                       ('xjtu-zhangzhengce-education-3', '博士', '西安交通大学', None, '2003', 'degree_study', None, None),
                       ('xjtu-zhangzhengce-education-4',
                        None,
                        '圣母大学（University of Notre Dame）',
                        '2008',
                        '2009',
                        'academic_visit',
                        False,
                        None),
                       ('xjtu-zhangzhengce-education-5',
                        None,
                        '圣母大学（University of Notre Dame）',
                        '2016-01',
                        '2016-07',
                        'academic_visit',
                        False,
                        None)]}

EXPECTED_MENTORS = {'lzu-changqingquan': [('孙春友',
                        'doctoral_supervisor',
                        '博士',
                        'lzu-changqingquan-education-1',
                        '2015-09',
                        '2019-12',
                        'education_period_not_independently_verified_supervision_dates',
                        'official_page_currently_listed',
                        True),
                       ('马闪',
                        'masters_supervisor',
                        '硕士',
                        'lzu-changqingquan-education-2',
                        '2012-09',
                        '2015-07',
                        'education_period_not_independently_verified_supervision_dates',
                        'official_page_currently_listed',
                        True),
                       ('曹道民',
                        'postdoctoral_supervisor',
                        '博士后',
                        'lzu-changqingquan-education-4',
                        '2020-06',
                        '2025-06',
                        'education_period_not_independently_verified_supervision_dates',
                        'unknown',
                        False)],
 'lzu-chengxiyou': [('钟承奎',
                     'doctoral_supervisor',
                     '博士',
                     'lzu-chengxiyou-education-1',
                     '2003-09',
                     '2006-06',
                     'education_period_not_independently_verified_supervision_dates',
                     'retired',
                     False),
                    ('钟承奎',
                     'masters_supervisor',
                     '硕士',
                     'lzu-chengxiyou-education-2',
                     '2001-09',
                     '2003-06',
                     'education_period_not_independently_verified_supervision_dates',
                     'retired',
                     False),
                    ('张志涛',
                     'postdoctoral_supervisor',
                     '博士后',
                     'lzu-chengxiyou-education-5',
                     '2008-06',
                     '2011-03',
                     'education_period_not_independently_verified_supervision_dates',
                     'unknown',
                     False)],
 'nwpu-baixueli': [('郑斯宁',
                    '博士导师',
                    '博士',
                    'nwpu-baixueli-education-1',
                    None,
                    None,
                    'supervision_dates_not_independently_verified',
                    'official_profile_listed_retirement_not_disclosed',
                    True),
                   ('倪维明',
                    '博士后合作导师',
                    '博士后',
                    'nwpu-baixueli-education-2',
                    None,
                    None,
                    'supervision_dates_not_independently_verified',
                    'active_officially_listed',
                    True)],
 'nwpu-guoqianqiao': [('郭大钧',
                       '硕士导师',
                       '硕士',
                       'nwpu-guoqianqiao-education-1',
                       None,
                       None,
                       'supervision_dates_not_independently_verified',
                       'retired',
                       False),
                      ('钮鹏程',
                       '博士导师',
                       '博士',
                       'nwpu-guoqianqiao-education-2',
                       None,
                       None,
                       'supervision_dates_not_independently_verified',
                       'retirement_reported_official_index',
                       False)],
 'nwpu-libinlong': [('张胜贵',
                     '博士导师',
                     '博士',
                     'nwpu-libinlong-education-3',
                     None,
                     None,
                     'supervision_dates_not_independently_verified',
                     'official_roster_currently_listed',
                     False),
                    ('Hajo Broersma',
                     '博士导师',
                     '博士',
                     'nwpu-libinlong-education-3',
                     None,
                     None,
                     'supervision_dates_not_independently_verified',
                     'emeritus',
                     False)],
 'scut-chenbocong': [('樊恽',
                      'doctoral_supervisor',
                      '博士',
                      'scut-chenbocong-education-1',
                      None,
                      None,
                      '指导关系明确，但具体指导起止日未单独披露；不复制整个学习区间。',
                      'unknown',
                      False),
                     ('San Ling',
                      'postdoctoral_co_supervisor',
                      '博士后',
                      'scut-chenbocong-education-2',
                      None,
                      None,
                      '指导关系明确，但具体指导起止日未单独披露；不复制整个学习区间。',
                      'unknown',
                      False)],
 'scut-chenyingshan': [('易法槐',
                        'masters_supervisor',
                        '硕士',
                        'scut-chenyingshan-education-2',
                        None,
                        None,
                        '指导关系明确，但具体指导起止日未单独披露；不复制整个学习区间。',
                        'official_profile_listed_retirement_not_disclosed',
                        True),
                       ('戴民',
                        'doctoral_supervisor',
                        '博士',
                        'scut-chenyingshan-education-3',
                        None,
                        None,
                        '指导关系明确，但具体指导起止日未单独披露；不复制整个学习区间。',
                        'official_faculty_page_currently_listed',
                        True),
                       ('朱长江',
                        'postdoctoral_co_supervisor',
                        '博士后',
                        'scut-chenyingshan-education-4',
                        None,
                        None,
                        '指导关系明确，但具体指导起止日未单独披露；不复制整个学习区间。',
                        'official_faculty_page_currently_listed',
                        True)],
 'sysu-chenbingyi': [('丘成栋（Stephen S.-T. Yau）',
                      '博士导师',
                      '博士',
                      'sysu-chenbingyi-education-1',
                      None,
                      None,
                      'supervision_start_end_not_disclosed',
                      'historically_listed_professor_current_status_unverified',
                      False)],
 'sysu-chengcheng': [('Xin Li（李欣）',
                      '博士导师',
                      '博士',
                      'sysu-chengcheng-education-1',
                      None,
                      None,
                      'supervision_start_end_not_disclosed',
                      'active_officially_listed',
                      True),
                     ('Qiyu Sun（孙颀彧）',
                      '博士导师',
                      '博士',
                      'sysu-chengcheng-education-1',
                      None,
                      None,
                      'supervision_start_end_not_disclosed',
                      'active_officially_listed',
                      True),
                     ('Ingrid Daubechies',
                      '博士后合作导师',
                      '博士后',
                      'sysu-chengcheng-education-2',
                      None,
                      None,
                      'supervision_start_end_not_disclosed',
                      'emeritus',
                      False)],
 'uestc-guyiqi': [('Jie Shen（沈捷）',
                   '博士导师',
                   '博士',
                   'uestc-guyiqi-education-3',
                   None,
                   None,
                   'supervision_dates_not_disclosed',
                   'current_position_at_another_institution_explicit',
                   True),
                  ('Xiaoliang Cheng',
                   '本科毕业论文导师',
                   '本科毕业论文',
                   'uestc-guyiqi-education-1',
                   None,
                   None,
                   'supervision_dates_not_disclosed',
                   'unknown',
                   False)],
 'uestc-jonas-kahn': [('Pascal Massart',
                       '博士导师',
                       '法国博士',
                       'uestc-jonas-kahn-education-1',
                       None,
                       None,
                       'supervision_dates_not_disclosed',
                       'unknown',
                       False)]}

EXPECTED_ROSTER_IDS = {'cqu-gongqu': 'roster-cqu-mathematics-statistics-gongqu',
 'cqu-hechuanjiang': 'roster-cqu-mathematics-statistics-hechuanjiang',
 'cqu-huangxiaojun': 'roster-cqu-mathematics-statistics-huangxiaojun',
 'lzu-changqingquan': 'roster-lzu-basic-math-changqingquan',
 'lzu-chenlizhi': 'roster-lzu-basic-math-chenlizhi',
 'lzu-chengxiyou': 'roster-lzu-basic-math-chengxiyou',
 'nwpu-baixueli': 'roster-nwpu-math-prof-baixueli',
 'nwpu-guoqianqiao': 'roster-nwpu-math-prof-guoqianqiao',
 'nwpu-libinlong': 'roster-nwpu-math-prof-libinlong',
 'nwsuaf-fengbaili': 'roster-nwsuaf-agronomy-prof-fengbaili',
 'nwsuaf-fengyongzhong': 'roster-nwsuaf-agronomy-prof-fengyongzhong',
 'nwsuaf-gaojinfeng': 'roster-nwsuaf-agronomy-prof-gaojinfeng',
 'scu-tangjianhua': 'roster-scu-chemical-tangjianhua',
 'scu-lianggemeng': 'roster-scu-chemical-lianggemeng',
 'scu-chuliangyin': 'roster-scu-chemical-chuliangyin',
 'scut-chenbocong': 'roster-scut-math-chenbocong',
 'scut-chenpei': 'roster-scut-math-chenpei',
 'scut-chenyingshan': 'roster-scut-math-chenyingshan',
 'sysu-gulinyan': 'roster-sysu-math-gulinyan',
 'sysu-chenbingyi': 'roster-sysu-math-chenbingyi',
 'sysu-chengcheng': 'roster-sysu-math-chengcheng',
 'uestc-guyiqi': 'roster-uestc-cam-guyiqi',
 'uestc-jonas-kahn': 'roster-uestc-cam-jonas-kahn',
 'uestc-kongefang': 'roster-uestc-cam-kongefang',
 'xjtu-yiyuan': 'roster-xjtu-math-prof-yiyuan',
 'xjtu-lidongsheng': 'roster-xjtu-math-prof-lidongsheng',
 'xjtu-zhangzhengce': 'roster-xjtu-math-prof-zhangzhengce'}

# A deduplicated structural mask makes the original-record hash check self-contained.
# Each node is an object field list, an array of node IDs, or a scalar. This masks
# newly added consumer metadata without masking any reviewed original leaf.
SOURCE_SHAPES = [
    ['value'],  # 0
    ['array', []],  # 1
    ['object', [['institution', 0], ['title', 0], ['start', 0], ['end', 0]]],  # 2
    ['object', [['institution', 0], ['title', 0], ['start', 0], ['end', 0], ['status', 0], ['source_id', 0], ['source_url', 0], ['note', 0], ['field_provenance', 2]]],  # 3
    ['array', [3]],  # 4
    ['object', [['degree', 0], ['institution', 0], ['start', 0], ['end', 0], ['field', 0], ['country', 0]]],  # 5
    ['object', [['degree', 0], ['institution', 0], ['start', 0], ['end', 0], ['field', 0], ['country', 0], ['region', 0], ['continent', 0], ['geography_basis', 0], ['event_kind', 0], ['degree_awarded', 0], ['degree_awarded_date', 0], ['source_url', 0], ['source_id', 0], ['note', 0], ['institution_985', 0], ['institution_985_status', 0], ['event_id', 0], ['field_provenance', 5], ['field_status', 5]]],  # 6
    ['array', [6, 6, 6, 6]],  # 7
    ['object', [['id', 0], ['url', 0], ['evidence_status', 0], ['retrieved_at', 0]]],  # 8
    ['object', [['id', 0], ['url', 0], ['evidence_status', 0], ['retrieved_at', 0], ['note', 0]]],  # 9
    ['array', [8, 8, 9]],  # 10
    ['array', [0, 0, 0, 0, 0]],  # 11
    ['object', [['status', 0], ['source_url', 0]]],  # 12
    ['object', [['name', 0], ['department', 0], ['listed_role', 0], ['official_url', 0]]],  # 13
    ['object', [['person_id', 0], ['name', 0], ['school_id', 0], ['department_id', 0], ['organization_id', 0], ['campus_ids', 1], ['campus', 0], ['department', 0], ['roster_entry_id', 0], ['official_url', 0], ['listed_role', 0], ['appointments', 4], ['education', 7], ['mentors', 1], ['committee_members', 1], ['publications', 1], ['sources', 10], ['unknowns', 11], ['profile_status', 0], ['identity_evidence', 12], ['navigation_verified', 0], ['field_provenance', 13], ['active_navigation_eligible', 0], ['employment_status', 0]]],  # 14
    ['array', [3, 3, 3, 3, 3, 3]],  # 15
    ['array', [0, 0]],  # 16
    ['object', [['degree', 0], ['institution', 0], ['start', 0], ['end', 0], ['field', 0], ['country', 0], ['region', 0], ['continent', 0], ['geography_basis', 0], ['event_kind', 0], ['degree_awarded', 0], ['degree_awarded_date', 0], ['source_url', 0], ['source_id', 0], ['note', 0], ['institution_985', 0], ['institution_985_status', 0], ['event_id', 0], ['field_provenance', 5], ['field_status', 5], ['start_conflicting_source_values', 16], ['degree_awarded_evidence', 0], ['degree_awarded_source_id', 0]]],  # 17
    ['array', [6, 6, 17]],  # 18
    ['object', [['person_id', 0], ['name', 0], ['school_id', 0], ['department_id', 0], ['organization_id', 0], ['campus_ids', 1], ['campus', 0], ['department', 0], ['roster_entry_id', 0], ['official_url', 0], ['listed_role', 0], ['appointments', 15], ['education', 18], ['mentors', 1], ['committee_members', 1], ['publications', 1], ['sources', 10], ['unknowns', 11], ['profile_status', 0], ['identity_evidence', 12], ['navigation_verified', 0], ['field_provenance', 13], ['active_navigation_eligible', 0], ['employment_status', 0]]],  # 19
    ['array', [3, 3]],  # 20
    ['array', [8, 8, 9, 9]],  # 21
    ['array', [0, 0, 0, 0]],  # 22
    ['object', [['person_id', 0], ['name', 0], ['school_id', 0], ['department_id', 0], ['organization_id', 0], ['campus_ids', 1], ['campus', 0], ['department', 0], ['roster_entry_id', 0], ['official_url', 0], ['listed_role', 0], ['appointments', 20], ['education', 7], ['mentors', 1], ['committee_members', 1], ['publications', 1], ['sources', 21], ['unknowns', 22], ['profile_status', 0], ['identity_evidence', 12], ['navigation_verified', 0], ['field_provenance', 13], ['active_navigation_eligible', 0], ['employment_status', 0], ['employment_status_source_id', 0]]],  # 23
    ['object', [['institution', 0], ['title', 0], ['start', 0], ['end', 0], ['status', 0], ['source_url', 0], ['source_id', 0], ['note', 0]]],  # 24
    ['array', [24]],  # 25
    ['object', [['degree', 0], ['institution', 0], ['start', 0], ['end', 0], ['field', 0]]],  # 26
    ['object', [['degree', 0], ['institution', 0], ['start', 0], ['end', 0], ['field', 0], ['country', 0], ['region', 0], ['continent', 0], ['geography_basis', 0], ['event_kind', 0], ['degree_awarded', 0], ['source_url', 0], ['source_id', 0], ['note', 0], ['event_id', 0], ['degree_awarded_date', 0], ['field_provenance', 26], ['field_status', 26]]],  # 27
    ['array', [27, 27, 27, 27]],  # 28
    ['object', [['name', 0], ['type', 0], ['education_stage', 0], ['description', 0], ['employment_status', 0], ['employment_status_note', 0], ['official_url', 0], ['source_url', 0], ['source_id', 0], ['profile_source_url', 0], ['person_id', 0], ['profile_source_id', 0], ['education_event_id', 0], ['navigation_verified', 0], ['navigation_status', 0], ['original_name', 0], ['identity_evidence_note', 0], ['start', 0], ['end', 0], ['include_in_mentorship_graph', 0], ['relationship_status', 0], ['date_basis', 0]]],  # 29
    ['array', [29, 29, 29]],  # 30
    ['object', [['title', 0], ['year', 0], ['venue', 0], ['doi', 0], ['url', 0], ['type', 0], ['source_url', 0], ['source_id', 0], ['identity_evidence', 0], ['link_status', 0], ['note', 0]]],  # 31
    ['array', [31, 31]],  # 32
    ['array', [8, 8, 8, 8, 8]],  # 33
    ['array', [0, 0, 0]],  # 34
    ['object', [['person_id', 0], ['name', 0], ['school_id', 0], ['department_id', 0], ['organization_id', 0], ['campus_ids', 1], ['campus', 0], ['department', 0], ['roster_entry_id', 0], ['official_url', 0], ['listed_role', 0], ['appointments', 25], ['education', 28], ['mentors', 30], ['committee_members', 1], ['publications', 32], ['sources', 33], ['unknowns', 34], ['profile_status', 0], ['identity_evidence', 12]]],  # 35
    ['array', [24, 24]],  # 36
    ['object', [['degree', 0], ['institution', 0], ['start', 0], ['end', 0], ['field', 0], ['degree_category', 0]]],  # 37
    ['object', [['degree', 0], ['institution', 0], ['start', 0], ['end', 0], ['field', 0], ['country', 0], ['region', 0], ['continent', 0], ['geography_basis', 0], ['event_kind', 0], ['degree_awarded', 0], ['source_url', 0], ['source_id', 0], ['note', 0], ['event_id', 0], ['degree_awarded_date', 0], ['field_provenance', 37], ['field_status', 26], ['degree_category', 0]]],  # 38
    ['array', [38, 38, 38, 27, 27]],  # 39
    ['array', [8, 8]],  # 40
    ['object', [['person_id', 0], ['name', 0], ['school_id', 0], ['department_id', 0], ['organization_id', 0], ['campus_ids', 1], ['campus', 0], ['department', 0], ['roster_entry_id', 0], ['official_url', 0], ['listed_role', 0], ['appointments', 36], ['education', 39], ['mentors', 1], ['committee_members', 1], ['publications', 32], ['sources', 40], ['unknowns', 22], ['profile_status', 0], ['identity_evidence', 12]]],  # 41
    ['array', [24, 24, 24, 24]],  # 42
    ['array', [27, 27, 27, 27, 27]],  # 43
    ['array', [8, 8, 8, 9]],  # 44
    ['object', [['status', 0], ['source_url', 0], ['note', 0]]],  # 45
    ['object', [['person_id', 0], ['name', 0], ['school_id', 0], ['department_id', 0], ['organization_id', 0], ['campus_ids', 1], ['campus', 0], ['department', 0], ['roster_entry_id', 0], ['official_url', 0], ['listed_role', 0], ['appointments', 42], ['education', 43], ['mentors', 30], ['committee_members', 1], ['publications', 32], ['sources', 44], ['unknowns', 34], ['profile_status', 0], ['identity_evidence', 45]]],  # 46
    ['object', [['degree', 0], ['institution', 0], ['start', 0], ['end', 0], ['field', 0], ['country', 0], ['region', 0], ['continent', 0], ['geography_basis', 0], ['event_kind', 0], ['degree_awarded', 0], ['source_url', 0], ['source_id', 0], ['field_provenance', 26], ['note', 0], ['event_id', 0], ['degree_awarded_date', 0], ['field_status', 26]]],  # 47
    ['array', [47, 47]],  # 48
    ['object', [['name', 0], ['type', 0], ['education_stage', 0], ['description', 0], ['employment_status', 0], ['employment_status_note', 0], ['official_url', 0], ['source_url', 0], ['source_id', 0], ['profile_source_url', 0], ['person_id', 0], ['profile_source_id', 0], ['education_event_index', 0], ['navigation_verified', 0], ['navigation_status', 0], ['date_basis', 0], ['start', 0], ['end', 0], ['include_in_mentorship_graph', 0], ['relationship_status', 0], ['education_event_id', 0]]],  # 49
    ['array', [49, 49]],  # 50
    ['object', [['title', 0], ['year', 0], ['venue', 0], ['doi', 0], ['url', 0], ['type', 0], ['source_url', 0], ['source_id', 0], ['identity_evidence', 0], ['link_status', 0], ['note', 0], ['individual_article_link_verified', 0]]],  # 51
    ['array', [51]],  # 52
    ['object', [['value', 0], ['source_id', 0], ['source_url', 0]]],  # 53
    ['object', [['person_id', 0], ['name', 0], ['school_id', 0], ['department_id', 0], ['organization_id', 0], ['campus_ids', 1], ['campus', 0], ['department', 0], ['roster_entry_id', 0], ['official_url', 0], ['listed_role', 0], ['appointments', 36], ['education', 48], ['mentors', 50], ['committee_members', 1], ['publications', 52], ['sources', 33], ['unknowns', 34], ['profile_status', 0], ['identity_evidence', 12], ['navigation_verified', 0], ['navigation_status', 0], ['institution_join_date', 53]]],  # 54
    ['array', [47, 47, 47, 47]],  # 55
    ['object', [['person_id', 0], ['name', 0], ['school_id', 0], ['department_id', 0], ['organization_id', 0], ['campus_ids', 1], ['campus', 0], ['department', 0], ['roster_entry_id', 0], ['official_url', 0], ['listed_role', 0], ['appointments', 25], ['education', 55], ['mentors', 50], ['committee_members', 1], ['publications', 1], ['sources', 33], ['unknowns', 34], ['profile_status', 0], ['identity_evidence', 12], ['navigation_verified', 0], ['navigation_status', 0]]],  # 56
    ['object', [['degree', 0], ['institution', 0], ['start', 0], ['end', 0], ['field', 0], ['country', 0], ['region', 0], ['continent', 0], ['geography_basis', 0], ['event_kind', 0], ['degree_awarded', 0], ['source_url', 0], ['source_id', 0], ['field_provenance', 26], ['note', 0], ['joint_training_institution', 0], ['joint_training_source_id', 0], ['event_id', 0], ['degree_awarded_date', 0], ['field_status', 26]]],  # 57
    ['array', [47, 47, 57, 47, 47]],  # 58
    ['object', [['name', 0], ['type', 0], ['education_stage', 0], ['description', 0], ['employment_status', 0], ['employment_status_note', 0], ['official_url', 0], ['source_url', 0], ['source_id', 0], ['profile_source_url', 0], ['person_id', 0], ['profile_source_id', 0], ['education_event_index', 0], ['navigation_verified', 0], ['navigation_status', 0], ['date_basis', 0], ['name_identity_source_id', 0], ['start', 0], ['end', 0], ['include_in_mentorship_graph', 0], ['relationship_status', 0], ['education_event_id', 0]]],  # 59
    ['array', [59, 49]],  # 60
    ['array', [8, 8, 8, 8, 8, 8, 8, 8]],  # 61
    ['object', [['person_id', 0], ['name', 0], ['school_id', 0], ['department_id', 0], ['organization_id', 0], ['campus_ids', 1], ['campus', 0], ['department', 0], ['roster_entry_id', 0], ['official_url', 0], ['listed_role', 0], ['appointments', 25], ['education', 58], ['mentors', 60], ['committee_members', 1], ['publications', 52], ['sources', 61], ['unknowns', 22], ['profile_status', 0], ['identity_evidence', 12], ['navigation_verified', 0], ['navigation_status', 0], ['institution_join_date', 53]]],  # 62
    ['array', [27, 27, 27]],  # 63
    ['object', [['person_id', 0], ['name', 0], ['school_id', 0], ['department_id', 0], ['organization_id', 0], ['campus_ids', 1], ['campus', 0], ['department', 0], ['roster_entry_id', 0], ['official_url', 0], ['listed_role', 0], ['appointments', 36], ['education', 63], ['mentors', 1], ['committee_members', 1], ['publications', 32], ['sources', 40], ['unknowns', 16], ['profile_status', 0], ['identity_evidence', 12], ['navigation_verified', 0]]],  # 64
    ['array', [27]],  # 65
    ['array', [8, 8, 8]],  # 66
    ['object', [['person_id', 0], ['name', 0], ['school_id', 0], ['department_id', 0], ['organization_id', 0], ['campus_ids', 1], ['campus', 0], ['department', 0], ['roster_entry_id', 0], ['official_url', 0], ['listed_role', 0], ['appointments', 36], ['education', 65], ['mentors', 1], ['committee_members', 1], ['publications', 32], ['sources', 66], ['unknowns', 34], ['profile_status', 0], ['identity_evidence', 12], ['navigation_verified', 0]]],  # 67
    ['object', [['person_id', 0], ['name', 0], ['school_id', 0], ['department_id', 0], ['organization_id', 0], ['campus_ids', 1], ['campus', 0], ['department', 0], ['roster_entry_id', 0], ['official_url', 0], ['listed_role', 0], ['appointments', 25], ['education', 28], ['mentors', 1], ['committee_members', 1], ['publications', 32], ['sources', 40], ['unknowns', 16], ['profile_status', 0], ['identity_evidence', 12], ['navigation_verified', 0]]],  # 68
    ['object', [['degree', 0], ['institution', 0], ['start', 0], ['end', 0], ['field', 0], ['country', 0], ['region', 0], ['continent', 0], ['geography_basis', 0], ['event_kind', 0], ['degree_awarded', 0], ['source_url', 0], ['source_id', 0], ['field_provenance', 26], ['note', 0], ['institution_985', 0], ['institution_985_status', 0], ['event_id', 0], ['degree_awarded_date', 0], ['field_status', 26]]],  # 69
    ['object', [['degree', 0], ['institution', 0], ['start', 0], ['end', 0], ['field', 0], ['country', 0], ['region', 0], ['continent', 0], ['geography_basis', 0], ['event_kind', 0], ['degree_awarded', 0], ['source_url', 0], ['source_id', 0], ['field_provenance', 26], ['note', 0], ['institution_history_note', 0], ['event_id', 0], ['degree_awarded_date', 0], ['field_status', 26]]],  # 70
    ['array', [69, 70, 47]],  # 71
    ['object', [['person_id', 0], ['name', 0], ['school_id', 0], ['department_id', 0], ['organization_id', 0], ['campus_ids', 1], ['campus', 0], ['department', 0], ['roster_entry_id', 0], ['official_url', 0], ['listed_role', 0], ['appointments', 42], ['education', 71], ['mentors', 1], ['committee_members', 1], ['publications', 32], ['sources', 40], ['unknowns', 16], ['profile_status', 0], ['identity_evidence', 12], ['navigation_verified', 0]]],  # 72
    ['object', [['id', 0], ['url', 0], ['evidence_status', 0], ['retrieved_at', 0], ['body_sha256', 0]]],  # 73
    ['array', [8, 8, 73]],  # 74
    ['object', [['person_id', 0], ['name', 0], ['school_id', 0], ['department_id', 0], ['organization_id', 0], ['campus_ids', 1], ['campus', 0], ['department', 0], ['roster_entry_id', 0], ['official_url', 0], ['listed_role', 0], ['appointments', 25], ['education', 1], ['mentors', 1], ['committee_members', 1], ['publications', 1], ['sources', 74], ['unknowns', 22], ['profile_status', 0], ['identity_evidence', 12], ['navigation_verified', 0], ['navigation_status', 0]]],  # 75
    ['array', [24, 24, 24, 24, 24, 24, 24, 24, 24, 24]],  # 76
    ['object', [['degree', 0], ['institution', 0], ['start', 0], ['end', 0], ['field', 0], ['country', 0], ['region', 0], ['continent', 0], ['geography_basis', 0], ['event_kind', 0], ['degree_awarded', 0], ['source_url', 0], ['source_id', 0], ['field_provenance', 26], ['note', 0], ['institution_985', 0], ['institution_985_status', 0], ['institution_history_note', 0], ['event_id', 0], ['degree_awarded_date', 0], ['field_status', 26]]],  # 77
    ['array', [77, 77, 47, 47, 47, 47, 47, 47]],  # 78
    ['array', [8, 8, 8, 8]],  # 79
    ['object', [['name', 0], ['source_url', 0], ['source_id', 0]]],  # 80
    ['array', [80]],  # 81
    ['object', [['person_id', 0], ['name', 0], ['school_id', 0], ['department_id', 0], ['organization_id', 0], ['campus_ids', 1], ['campus', 0], ['department', 0], ['roster_entry_id', 0], ['official_url', 0], ['listed_role', 0], ['appointments', 76], ['education', 78], ['mentors', 1], ['committee_members', 1], ['publications', 32], ['sources', 79], ['unknowns', 22], ['profile_status', 0], ['identity_evidence', 12], ['navigation_verified', 0], ['personal_homepage_url', 0], ['research_fields', 81]]],  # 82
    ['object', [['degree', 0], ['institution', 0], ['start', 0], ['end', 0], ['field', 0], ['degree_awarded', 0], ['degree_awarded_date', 0]]],  # 83
    ['object', [['start', 0], ['end', 0], ['stage_breakdown', 0], ['source_id', 0]]],  # 84
    ['object', [['event_id', 0], ['degree', 0], ['institution', 0], ['start', 0], ['end', 0], ['field', 0], ['country', 0], ['region', 0], ['continent', 0], ['geography_basis', 0], ['event_kind', 0], ['degree_awarded', 0], ['degree_awarded_date', 0], ['source_url', 0], ['source_id', 0], ['field_provenance', 83], ['field_status', 26], ['note', 0], ['reported_study_period', 84], ['degree_award_source_id', 0]]],  # 85
    ['object', [['degree', 0], ['institution', 0], ['start', 0], ['end', 0], ['field', 0], ['degree_awarded', 0], ['event_kind', 0]]],  # 86
    ['object', [['event_id', 0], ['degree', 0], ['institution', 0], ['start', 0], ['end', 0], ['field', 0], ['country', 0], ['region', 0], ['continent', 0], ['geography_basis', 0], ['event_kind', 0], ['degree_awarded', 0], ['degree_awarded_date', 0], ['source_url', 0], ['source_id', 0], ['field_provenance', 86], ['field_status', 26], ['note', 0], ['stage_source_id', 0]]],  # 87
    ['array', [85, 87]],  # 88
    ['object', [['name', 0], ['type', 0], ['education_stage', 0], ['education_event_id', 0], ['description', 0], ['employment_status', 0], ['employment_status_note', 0], ['official_url', 0], ['source_url', 0], ['source_id', 0], ['profile_source_url', 0], ['profile_source_id', 0], ['stage_source_id', 0], ['person_id', 0], ['navigation_verified', 0], ['navigation_status', 0], ['start', 0], ['end', 0], ['date_basis', 0], ['include_in_mentorship_graph', 0], ['include_in_current_faculty_count', 0], ['relationship_status', 0]]],  # 89
    ['array', [89, 89]],  # 90
    ['object', [['title', 0], ['year', 0], ['venue', 0], ['doi', 0], ['url', 0], ['type', 0], ['authors', 34], ['source_url', 0], ['source_id', 0], ['identity_evidence', 0], ['link_status', 0], ['individual_article_link_verified', 0], ['publication_status', 0], ['note', 0]]],  # 91
    ['object', [['title', 0], ['year', 0], ['venue', 0], ['doi', 0], ['url', 0], ['type', 0], ['authors', 22], ['source_url', 0], ['source_id', 0], ['identity_evidence', 0], ['link_status', 0], ['individual_article_link_verified', 0], ['publication_status', 0], ['note', 0], ['volume', 0], ['pages', 0]]],  # 92
    ['array', [91, 92]],  # 93
    ['object', [['id', 0], ['url', 0], ['evidence_status', 0], ['retrieved_at', 0], ['body_sha256', 0], ['access_note', 0]]],  # 94
    ['array', [94, 94, 94, 94]],  # 95
    ['object', [['person_id', 0], ['name', 0], ['school_id', 0], ['department_id', 0], ['organization_id', 0], ['campus_ids', 1], ['campus', 0], ['department', 0], ['roster_entry_id', 0], ['official_url', 0], ['listed_role', 0], ['appointments', 36], ['education', 88], ['mentors', 90], ['committee_members', 1], ['publications', 93], ['sources', 95], ['unknowns', 34], ['profile_status', 0], ['identity_evidence', 12]]],  # 96
    ['object', [['degree', 0], ['institution', 0], ['start', 0], ['end', 0], ['field', 0], ['degree_awarded', 0]]],  # 97
    ['object', [['event_id', 0], ['degree', 0], ['institution', 0], ['start', 0], ['end', 0], ['field', 0], ['country', 0], ['region', 0], ['continent', 0], ['geography_basis', 0], ['event_kind', 0], ['degree_awarded', 0], ['degree_awarded_date', 0], ['source_url', 0], ['source_id', 0], ['field_provenance', 97], ['field_status', 26], ['note', 0], ['reported_department', 0]]],  # 98
    ['object', [['event_id', 0], ['degree', 0], ['institution', 0], ['start', 0], ['end', 0], ['field', 0], ['country', 0], ['region', 0], ['continent', 0], ['geography_basis', 0], ['event_kind', 0], ['degree_awarded', 0], ['degree_awarded_date', 0], ['source_url', 0], ['source_id', 0], ['field_provenance', 97], ['field_status', 26], ['note', 0], ['reported_department', 0], ['institution_note', 0]]],  # 99
    ['object', [['event_id', 0], ['degree', 0], ['institution', 0], ['start', 0], ['end', 0], ['field', 0], ['country', 0], ['region', 0], ['continent', 0], ['geography_basis', 0], ['event_kind', 0], ['degree_awarded', 0], ['degree_awarded_date', 0], ['source_url', 0], ['source_id', 0], ['field_provenance', 97], ['field_status', 26], ['note', 0]]],  # 100
    ['array', [98, 98, 99, 100, 100]],  # 101
    ['object', [['title', 0], ['year', 0], ['venue', 0], ['doi', 0], ['url', 0], ['type', 0], ['authors', 22], ['source_url', 0], ['source_id', 0], ['identity_evidence', 0], ['link_status', 0], ['individual_article_link_verified', 0], ['publication_status', 0], ['note', 0], ['volume', 0], ['article_number', 0]]],  # 102
    ['array', [102, 102]],  # 103
    ['array', [94, 94]],  # 104
    ['object', [['person_id', 0], ['name', 0], ['school_id', 0], ['department_id', 0], ['organization_id', 0], ['campus_ids', 1], ['campus', 0], ['department', 0], ['roster_entry_id', 0], ['official_url', 0], ['listed_role', 0], ['appointments', 42], ['education', 101], ['mentors', 1], ['committee_members', 1], ['publications', 103], ['sources', 104], ['unknowns', 34], ['profile_status', 0], ['identity_evidence', 12]]],  # 105
    ['array', [24, 24, 24]],  # 106
    ['array', [100, 100, 100, 100]],  # 107
    ['array', [89, 89, 89]],  # 108
    ['object', [['title', 0], ['year', 0], ['venue', 0], ['doi', 0], ['url', 0], ['type', 0], ['authors', 34], ['source_url', 0], ['source_id', 0], ['identity_evidence', 0], ['link_status', 0], ['individual_article_link_verified', 0], ['publication_status', 0], ['note', 0], ['volume', 0], ['pages', 0]]],  # 109
    ['object', [['title', 0], ['year', 0], ['venue', 0], ['doi', 0], ['url', 0], ['type', 0], ['authors', 34], ['source_url', 0], ['source_id', 0], ['identity_evidence', 0], ['link_status', 0], ['individual_article_link_verified', 0], ['publication_status', 0], ['note', 0], ['volume', 0], ['article_number', 0]]],  # 110
    ['array', [109, 110]],  # 111
    ['array', [94, 94, 94, 94, 94]],  # 112
    ['object', [['person_id', 0], ['name', 0], ['school_id', 0], ['department_id', 0], ['organization_id', 0], ['campus_ids', 1], ['campus', 0], ['department', 0], ['roster_entry_id', 0], ['official_url', 0], ['listed_role', 0], ['appointments', 106], ['education', 107], ['mentors', 108], ['committee_members', 1], ['publications', 111], ['sources', 112], ['unknowns', 34], ['profile_status', 0], ['identity_evidence', 12]]],  # 113
    ['object', [['institution', 0], ['title', 0], ['start', 0], ['end', 0], ['status', 0], ['source_url', 0], ['source_id', 0], ['note', 0], ['evidence_status', 0]]],  # 114
    ['array', [114]],  # 115
    ['object', [['person_id', 0], ['name', 0], ['school_id', 0], ['department_id', 0], ['organization_id', 0], ['campus_ids', 1], ['campus', 0], ['department', 0], ['roster_entry_id', 0], ['official_url', 0], ['listed_role', 0], ['appointments', 115], ['education', 1], ['mentors', 1], ['committee_members', 1], ['publications', 1], ['sources', 40], ['unknowns', 22], ['profile_status', 0], ['identity_evidence', 12], ['navigation_verified', 0], ['navigation_status', 0]]],  # 116
    ['array', [24, 114]],  # 117
    ['object', [['year', 0], ['source_url', 0], ['status', 0]]],  # 118
    ['object', [['degree', 0], ['institution', 0], ['start', 0], ['end', 0], ['field', 0], ['country', 0], ['region', 0], ['continent', 0], ['geography_basis', 0], ['event_kind', 0], ['degree_awarded', 0], ['source_url', 0], ['source_id', 0], ['field_provenance', 26], ['note', 0], ['indexed_award_statement', 118], ['event_id', 0], ['degree_awarded_date', 0], ['field_status', 26]]],  # 119
    ['array', [119, 47]],  # 120
    ['object', [['name', 0], ['type', 0], ['education_stage', 0], ['description', 0], ['employment_status', 0], ['employment_status_note', 0], ['official_url', 0], ['source_url', 0], ['source_id', 0], ['profile_source_url', 0], ['person_id', 0], ['profile_source_id', 0], ['education_event_index', 0], ['navigation_verified', 0], ['navigation_status', 0], ['evidence_note', 0], ['start', 0], ['end', 0], ['include_in_mentorship_graph', 0], ['relationship_status', 0], ['education_event_id', 0], ['date_basis', 0]]],  # 121
    ['array', [121]],  # 122
    ['array', [31]],  # 123
    ['object', [['person_id', 0], ['name', 0], ['school_id', 0], ['department_id', 0], ['organization_id', 0], ['campus_ids', 1], ['campus', 0], ['department', 0], ['roster_entry_id', 0], ['official_url', 0], ['listed_role', 0], ['appointments', 117], ['education', 120], ['mentors', 122], ['committee_members', 1], ['publications', 123], ['sources', 33], ['unknowns', 16], ['profile_status', 0], ['identity_evidence', 12], ['navigation_verified', 0], ['navigation_status', 0]]],  # 124
    ['object', [['value', 0], ['source_url', 0], ['note', 0]]],  # 125
    ['object', [['degree', 0], ['institution', 0], ['start', 0], ['end', 0], ['field', 0], ['country', 0], ['region', 0], ['continent', 0], ['geography_basis', 0], ['event_kind', 0], ['degree_awarded', 0], ['source_url', 0], ['source_id', 0], ['field_provenance', 26], ['note', 0], ['conflicting_source_statement', 125], ['event_id', 0], ['degree_awarded_date', 0], ['field_status', 26]]],  # 126
    ['array', [126, 47]],  # 127
    ['object', [['name', 0], ['type', 0], ['education_stage', 0], ['description', 0], ['employment_status', 0], ['employment_status_note', 0], ['official_url', 0], ['source_url', 0], ['source_id', 0], ['profile_source_url', 0], ['person_id', 0], ['profile_source_id', 0], ['education_event_index', 0], ['navigation_verified', 0], ['navigation_status', 0], ['start', 0], ['end', 0], ['include_in_mentorship_graph', 0], ['relationship_status', 0], ['education_event_id', 0], ['date_basis', 0]]],  # 128
    ['array', [128, 128, 121]],  # 129
    ['array', [8, 8, 8, 8, 8, 8, 8, 8, 8]],  # 130
    ['object', [['person_id', 0], ['name', 0], ['school_id', 0], ['department_id', 0], ['organization_id', 0], ['campus_ids', 1], ['campus', 0], ['department', 0], ['roster_entry_id', 0], ['official_url', 0], ['listed_role', 0], ['appointments', 36], ['education', 127], ['mentors', 129], ['committee_members', 1], ['publications', 123], ['sources', 130], ['unknowns', 22], ['profile_status', 0], ['identity_evidence', 12], ['navigation_verified', 0], ['navigation_status', 0]]],  # 131
    ['object', [['institution', 0], ['title', 0], ['start', 0], ['end', 0], ['status', 0], ['source_url', 0], ['source_id', 0], ['note', 0], ['institution_join_date', 0]]],  # 132
    ['array', [24, 132]],  # 133
    ['object', [['degree', 0], ['institution', 0], ['start', 0], ['end', 0], ['field', 0], ['country', 0], ['region', 0], ['continent', 0], ['geography_basis', 0], ['event_kind', 0], ['degree_awarded', 0], ['source_url', 0], ['source_id', 0], ['field_provenance', 26], ['note', 0], ['start_basis', 0], ['event_id', 0], ['degree_awarded_date', 0], ['field_status', 26], ['source_reported_first_job_after_graduation_year', 0]]],  # 134
    ['array', [47, 47, 47, 134]],  # 135
    ['object', [['name', 0], ['type', 0], ['education_stage', 0], ['description', 0], ['employment_status', 0], ['employment_status_note', 0], ['official_url', 0], ['source_url', 0], ['source_id', 0], ['profile_source_url', 0], ['person_id', 0], ['profile_source_id', 0], ['navigation_verified', 0], ['navigation_status', 0], ['date_basis', 0], ['evidence_note', 0], ['start', 0], ['end', 0], ['include_in_mentorship_graph', 0], ['relationship_status', 0], ['education_event_id', 0]]],  # 136
    ['object', [['name', 0], ['type', 0], ['education_stage', 0], ['description', 0], ['employment_status', 0], ['employment_status_note', 0], ['official_url', 0], ['source_url', 0], ['source_id', 0], ['profile_source_url', 0], ['person_id', 0], ['profile_source_id', 0], ['navigation_verified', 0], ['navigation_status', 0], ['date_basis', 0], ['start', 0], ['end', 0], ['include_in_mentorship_graph', 0], ['relationship_status', 0], ['education_event_id', 0]]],  # 137
    ['array', [136, 137]],  # 138
    ['object', [['person_id', 0], ['name', 0], ['school_id', 0], ['department_id', 0], ['organization_id', 0], ['campus_ids', 1], ['campus', 0], ['department', 0], ['roster_entry_id', 0], ['official_url', 0], ['listed_role', 0], ['appointments', 133], ['education', 135], ['mentors', 138], ['committee_members', 1], ['publications', 32], ['sources', 61], ['unknowns', 22], ['profile_status', 0], ['identity_evidence', 12], ['navigation_verified', 0]]],  # 139
    ['object', [['degree', 0], ['institution', 0], ['start', 0], ['end', 0], ['field', 0], ['country', 0], ['region', 0], ['continent', 0], ['geography_basis', 0], ['event_kind', 0], ['degree_awarded', 0], ['source_url', 0], ['source_id', 0], ['field_provenance', 26], ['note', 0], ['thesis_defense_date', 0], ['thesis_defense_source_id', 0], ['event_id', 0], ['degree_awarded_date', 0], ['field_status', 26]]],  # 140
    ['array', [140, 47]],  # 141
    ['array', [136]],  # 142
    ['array', [0]],  # 143
    ['object', [['person_id', 0], ['name', 0], ['school_id', 0], ['department_id', 0], ['organization_id', 0], ['campus_ids', 1], ['campus', 0], ['department', 0], ['roster_entry_id', 0], ['official_url', 0], ['listed_role', 0], ['appointments', 106], ['education', 141], ['mentors', 142], ['committee_members', 1], ['publications', 123], ['sources', 79], ['unknowns', 22], ['profile_status', 0], ['identity_evidence', 12], ['aliases', 143], ['official_url_type', 0], ['navigation_verified', 0], ['navigation_status', 0]]],  # 144
    ['object', [['status', 0], ['source_url', 0], ['note', 0], ['source_urls', 34]]],  # 145
    ['object', [['person_id', 0], ['name', 0], ['school_id', 0], ['department_id', 0], ['organization_id', 0], ['campus_ids', 1], ['campus', 0], ['department', 0], ['roster_entry_id', 0], ['official_url', 0], ['listed_role', 0], ['appointments', 42], ['education', 55], ['mentors', 1], ['committee_members', 1], ['publications', 32], ['sources', 66], ['unknowns', 22], ['profile_status', 0], ['identity_evidence', 145], ['official_url_type', 0], ['navigation_verified', 0], ['navigation_status', 0]]],  # 146
    ['array', [47]],  # 147
    ['object', [['name', 0], ['source_id', 0], ['source_url', 0]]],  # 148
    ['array', [148]],  # 149
    ['object', [['person_id', 0], ['name', 0], ['school_id', 0], ['department_id', 0], ['organization_id', 0], ['campus_ids', 1], ['campus', 0], ['department', 0], ['roster_entry_id', 0], ['official_url', 0], ['listed_role', 0], ['appointments', 36], ['education', 147], ['mentors', 1], ['committee_members', 1], ['publications', 32], ['sources', 79], ['unknowns', 34], ['profile_status', 0], ['identity_evidence', 12], ['navigation_verified', 0], ['research_fields', 149]]],  # 150
    ['array', [47, 47, 47, 47, 47, 47, 47, 47, 47, 47, 47, 47, 47, 47, 47, 47]],  # 151
    ['array', [8, 8, 8, 8, 8, 8]],  # 152
    ['object', [['from', 0], ['to', 0], ['status', 0], ['source_url', 0]]],  # 153
    ['object', [['status', 0], ['source_url', 0], ['redirect_observation', 153]]],  # 154
    ['object', [['person_id', 0], ['name', 0], ['school_id', 0], ['department_id', 0], ['organization_id', 0], ['campus_ids', 1], ['campus', 0], ['department', 0], ['roster_entry_id', 0], ['official_url', 0], ['listed_role', 0], ['appointments', 42], ['education', 151], ['mentors', 1], ['committee_members', 1], ['publications', 32], ['sources', 152], ['unknowns', 22], ['profile_status', 0], ['identity_evidence', 154], ['navigation_verified', 0]]],  # 155
    ['array', [47, 47, 47, 47, 47]],  # 156
    ['object', [['person_id', 0], ['name', 0], ['school_id', 0], ['department_id', 0], ['organization_id', 0], ['campus_ids', 1], ['campus', 0], ['department', 0], ['roster_entry_id', 0], ['official_url', 0], ['listed_role', 0], ['appointments', 106], ['education', 156], ['mentors', 1], ['committee_members', 1], ['publications', 32], ['sources', 152], ['unknowns', 16], ['profile_status', 0], ['identity_evidence', 154], ['navigation_verified', 0], ['institution_join_date', 53]]],  # 157
]


def project_source_shape(value, node_id):
    """Select exactly the original keys; missing fields and changed lengths fail."""
    node = SOURCE_SHAPES[node_id]
    if node[0] == 'value':
        return value
    if node[0] == 'object':
        if not isinstance(value, dict):
            raise AssertionError('Reviewed object changed type')
        return {key: project_source_shape(value[key], child) for key, child in node[1]}
    if not isinstance(value, list) or len(value) != len(node[1]):
        raise AssertionError('Reviewed collection changed length/type')
    return [project_source_shape(v, child) for v, child in zip(value, node[1])]


def source_view(person):
    """Reverse only documented storage mappings, never repair substantive facts."""
    p = copy.deepcopy(person)
    p['profile_status'] = p['source_profile_status']
    for key in ('department_id', 'organization_id'):
        if 'source_' + key in p:
            p[key] = p['source_' + key]
    for key in ('education', 'mentors', 'publications'):
        if key in p.get('biography_evidence', {}):
            p[key] = p['biography_evidence'][key]
    for e in p['education']:
        if 'source_region' in e:
            e['region'] = e['source_region']
        if 'source_institution_985' in e:
            e['institution_985'] = e['source_institution_985']
    for m in p['mentors']:
        m['employment_status'] = m['source_employment_status']
        if 'source_official_url' in m:
            m['official_url'] = m['source_official_url']
    return p


# Real consumers, a minimal DOM, and local objects only. fetch never goes online.
NODE_CONSUMERS = "\nimport fs from 'node:fs';\nimport {pathToFileURL} from 'node:url';\nconst input = JSON.parse(fs.readFileSync(0, 'utf8'));\nconst root = input.root;\nconst model = await import(pathToFileURL(root + '/site/model.js'));\nconst roster = await import(pathToFileURL(root + '/site/rosters.js'));\nconst db = input.atlas, r = input.rosters;\nconst original = JSON.stringify([db, r]);\nconst people = new Map([...db.people, ...db.pending_people].map(p => [p.person_id, p]));\nconst out = {people:{}, pending:{}, schoolStats:{}, schoolPages:{}};\nfor (const id of input.ids) {\n  const p = people.get(id);\n  if (!p) throw Error('Missing release record: ' + id);\n  out.people[id] = {\n    stages: Object.fromEntries(['bachelor','master','doctor'].map(s => [s, model.stages(p,s).map(e => e.event_id)])),\n    ug: Object.fromEntries(['yes','no','unknown','not_recorded'].map(v => [v,model.matches(p,{ug:v},db.org_units)])),\n    doctorate: Object.fromEntries(['mainland','hmt','overseas','unknown','not_recorded'].map(v => [v,model.matches(p,{doctor:v},db.org_units)])),\n    labels: p.education.map(model.educationStageLabel),\n    officialUrl: model.officialProfileUrl(p),\n    mentors: p.mentors.map(m => ({name:m.name, url:model.mentorOfficialUrl(m), route:model.mentorProfileRoute(m,db.people), events:model.mentorEvents(p,m).map(e=>e.event_id)}))\n  };\n}\nconst scoped = {...db, rosters:r};\nfor (const id of input.pendingIds) {\n  const p=people.get(id), e=r.entries.find(e=>e.id===p.roster_entry_id), main={innerHTML:''};\n  roster.renderRosters(scoped,main,e.id,p.school_id);\n  out.pending[id]={matched:roster.rosterIdentityMatched(scoped,e),status:roster.rosterStatusLabel(scoped,e),html:main.innerHTML};\n}\nfor (const school of input.schools) out.schoolStats[school]=model.schoolStats(scoped,school);\nconst center=db.org_units.find(o=>o.id==='uestc-applied-math-center');\nout.center={parent:center?.parent_id, schoolContains:model.orgContains(db.org_units,'uestc',center?.id), falseCollegeParents:db.org_units.filter(o=>o.school_id==='uestc'&&o.id!==center?.id&&model.orgContains(db.org_units,o.id,center?.id)).map(o=>o.id)};\n// The actual app is loaded against cloned local inputs and a shared test build ID.\nconst appAtlas=structuredClone(db), appRosters=structuredClone(r);\nappAtlas.build_id=appRosters.build_id='third-wave-in-memory-consumer-test';\nconst nodes=new Map(), listeners={};\nconst node=key=>{\n  if (!nodes.has(key)) nodes.set(key,{innerHTML:'',textContent:'',value:'',style:{},dataset:{height:'320'},clientWidth:960,addEventListener(){},click(){this.onclick?.()},querySelector(selector){return node(selector)},scrollIntoView(){}});\n  return nodes.get(key);\n};\nglobalThis.document={querySelector:node,querySelectorAll:()=>[],getElementById:id=>node('#'+id)};\nglobalThis.location={hash:'#/',href:'https://atlas.test/site/index.html'};\nglobalThis.window={scrollTo(){},addEventListener(name,handler){listeners[name]=handler}};\nconst {createAtlasFetch}=await import(pathToFileURL(root+'/tests/atlas-test-io.js'));\nglobalThis.fetch=createAtlasFetch(appAtlas,appRosters);\nawait import(pathToFileURL(root+'/site/app.js'));\nif(!listeners.hashchange) throw Error('Actual app did not initialize: '+node('#main').innerHTML);\nconst navigate=hash=>{for(const n of nodes.values())n.innerHTML='';location.hash=hash;listeners.hashchange()};\nfor(const id of input.ids){\n  const p=people.get(id), row=out.people[id];\n  navigate('#/person/'+encodeURIComponent(id));\n  row.profileMain=node('#main').innerHTML;row.profileContent=node('#profile-content').innerHTML;\n  if(p.detail_count_eligible){\n    navigate('#/person/'+encodeURIComponent(id)+'/lineage');\n    row.lineage=node('#profile-content').innerHTML;row.graph=node('#mind-stage').innerHTML;\n  }\n}\nfor(const school of input.schools){navigate('#/school/'+school);out.schoolPages[school]=node('#main').innerHTML}\nout.unchanged=JSON.stringify([db,r])===original;\nprocess.stdout.write(JSON.stringify(out));\n"


class RotationThirdWaveReleaseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.d = load_atlas(ROOT / 'data/atlas.json')
        cls.r = json.loads((ROOT / 'data/rosters.json').read_text())
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
                                  'ids': list(SOURCE_FINGERPRINTS), 'pendingIds': PENDING_IDS, 'schools': SCHOOLS}),
                text=True, capture_output=True, timeout=45, cwd=ROOT,
            )
            if result.returncode:
                raise AssertionError('Actual JS consumers failed:\n' + result.stderr)
            cls.js = json.loads(result.stdout)
        return cls.js

    def event(self, pid, number):
        return next(e for e in self.ps[pid]['education'] if e['event_id'] == f'{pid}-education-{number}')

    def mentor(self, pid, name):
        rows = [m for m in self.ps[pid]['mentors'] if m['name'] == name]
        self.assertEqual(len(rows), 1, (pid, name))
        return rows[0]

    def tables(self, pid):
        p = self.ps[pid]
        before = copy.deepcopy(p)
        with mock.patch.object(build, 'Workbook', side_effect=AssertionError('No workbook writes')):
            rows = dict(build.department_tables([p], self.d['updated_at'], self.d['institutions']))
        self.assertEqual(p, before)
        return rows

    def test_01_every_reviewed_original_leaf_is_preserved(self):
        for pid, (shape_id, expected_sha) in SOURCE_FINGERPRINTS.items():
            with self.subTest(person=pid):
                original = project_source_shape(source_view(self.ps[pid]), shape_id)
                self.assertEqual(object_sha(original), expected_sha)

    def test_02_baseline_atlas_prefixes_and_nonmutable_metadata_unchanged(self):
        for key, (size, expected_sha) in BASELINE_PREFIXES.items():
            with self.subTest(collection=key):
                self.assertEqual(object_sha(self.d[key][:size]), expected_sha)
        for key, expected_sha in BASELINE_UNCHANGED.items():
            self.assertEqual(object_sha(self.d[key]), expected_sha, key)
        self.assertEqual(hashlib.sha256((ROOT / 'site/universities.js').read_bytes()).hexdigest(), REGISTRY_SHA256)

    def test_03_all_baseline_roster_records_and_exclusion_collections_unchanged(self):
        for key, (size, expected_sha) in BASELINE_ROSTER_PREFIXES.items():
            with self.subTest(collection=key):
                self.assertEqual(object_sha(self.r[key][:size]), expected_sha)
        for key, expected_sha in BASELINE_ROSTER_UNCHANGED.items():
            self.assertEqual(object_sha(self.r[key]), expected_sha, key)

    def test_04_exact_addition_layers_and_counts(self):
        self.assertEqual(len(self.new), 27)
        self.assertEqual(len(self.pro), 25)
        self.assertEqual(len(self.d['institutions']), 39)
        self.assertEqual({p['person_id'] for p in self.d['people'][499:524]}, set(SOURCE_FINGERPRINTS) - set(PENDING_IDS))
        self.assertEqual({p['person_id'] for p in self.d['pending_people'][80:82]}, set(PENDING_IDS))
        self.assertEqual(Counter(p['school_id'] for p in self.new), Counter({s: 3 for s in SCHOOLS}))
        self.assertEqual({k: sum(len(p.get(k, [])) for p in self.pro) for k in ('education','appointments','mentors','publications','sources')},
                         {'education':102,'appointments':70,'mentors':24,'publications':37,'sources':108})
        self.assertEqual(sum(len(p['appointments']) for p in self.new), 72)
        self.assertEqual(sum(len(p['sources']) for p in self.new), 113)
        for p in self.new:
            self.assertIs(p['fields_complete'], False)
            self.assertIs(p['complete_profile_count_eligible'], False)
            self.assertEqual(p['detail_count_eligible'], p['person_id'] not in PENDING_IDS)

    def test_05_all_102_education_chronologies_and_awards_match_reviewed_source(self):
        for pid, expected in EXPECTED_EDUCATION.items():
            with self.subTest(person=pid):
                actual = [tuple(e.get(k) for k in EDUCATION_KEYS) for e in self.ps[pid]['education']]
                self.assertEqual(actual, expected)
        events = [e for p in self.pro for e in p['education']]
        self.assertEqual(tuple(sum(e['degree_awarded'] is v for e in events) for v in (True, None, False)), (19, 41, 42))
        self.assertTrue(all(e['event_kind'] == 'degree' for e in events if e['degree_awarded'] is True))

    def test_06_actual_degree_filters_exclude_unknown_awards_and_nonaward_research(self):
        js = self.consumers()['people']
        for pid, expected in EXPECTED_EDUCATION.items():
            for kind, tokens in [('bachelor', ('本科','学士')), ('master', ('硕士',)), ('doctor', ('博士',))]:
                ids = [row[0] for row in expected if row[5] == 'degree' and row[6] is True and any(t in (row[1] or '') for t in tokens)]
                self.assertEqual(js[pid]['stages'][kind], ids, (pid, kind))
        for pid in ('lzu-changqingquan','lzu-chenlizhi','lzu-chengxiyou','scut-chenyingshan','sysu-chenbingyi','sysu-chengcheng','uestc-guyiqi','uestc-kongefang'):
            self.assertEqual(js[pid]['stages']['doctor'], [])
            self.assertTrue(js[pid]['doctorate']['not_recorded'])
            self.assertFalse(js[pid]['doctorate']['overseas'])
        self.assertEqual(js['scut-chenpei']['stages']['doctor'], ['scut-chenpei-education-3'])
        self.assertFalse(js['scut-chenpei']['doctorate']['overseas'])
        self.assertFalse(js['xjtu-lidongsheng']['doctorate']['overseas'])

    def test_07_historical_predecessors_never_inherit_modern_985(self):
        for pid, numbers, name in [('nwsuaf-fengbaili',(1,2),'西北农业大学'),('nwsuaf-gaojinfeng',(1,),'西北农业大学'),('scu-chuliangyin',(1,2),'成都科技大学')]:
            for n in numbers:
                e = self.event(pid, n)
                self.assertEqual(e['institution'], name)
                self.assertEqual(e['institution_985'], 'unknown')
        for pid in ('nwsuaf-fengbaili','nwsuaf-gaojinfeng'):
            row = self.consumers()['people'][pid]
            self.assertEqual(row['ug'], {'yes':False,'no':False,'unknown':True,'not_recorded':False})
        self.assertEqual(self.consumers()['people']['scu-chuliangyin']['ug'], {'yes':False,'no':False,'unknown':False,'not_recorded':True})

    def test_08_unknown_columbia_nature_is_not_a_visit_degree_or_research_claim(self):
        e = self.event('cqu-gongqu', 4)
        self.assertEqual(e['event_kind'], 'education_background')
        self.assertIsNone(e['degree'])
        self.assertIsNone(e['degree_awarded'])
        self.assertIsNone(e['start'])
        self.assertIsNone(e['end'])
        self.assertEqual(e['institution_985'], 'unknown')
        label = self.consumers()['people']['cqu-gongqu']['labels'][3]
        self.assertIn('未', label)
        self.assertNotEqual(label, '研究经历')
        self.assertNotIn('访问', label)
        self.assertIn(label, self.consumers()['people']['cqu-gongqu']['profileContent'])

    def test_09_cqu_conflicting_start_remains_null_and_end_is_not_award_date(self):
        p = self.ps['cqu-hechuanjiang']; e = self.event(p['person_id'], 3)
        self.assertIsNone(e['start'])
        self.assertEqual(e['start_conflicting_source_values'], ['1999-09','2000-09'])
        self.assertEqual(e['end'], '2004-06')
        self.assertIs(e['degree_awarded'], True)
        self.assertIsNone(e['degree_awarded_date'])
        self.assertEqual(len(p['education']), 3)
        self.assertIn('1999-09', e['note']); self.assertIn('2000-09', e['note'])
        for pid in ('cqu-gongqu','cqu-hechuanjiang'):
            self.assertIs(self.ps[pid]['include_in_current_faculty_count'], False)
            self.assertTrue(self.consumers()['people'][pid]['officialUrl'])
            self.assertIs(self.entries[pid]['include_in_current_faculty_count'], False)

    def test_10_unknown_degree_institution_and_category_do_not_borrow_current_role(self):
        for pid in ('xjtu-yiyuan','nwsuaf-fengyongzhong'):
            e = self.event(pid, 1)
            self.assertIsNone(e['institution']); self.assertIsNone(e['start']); self.assertIsNone(e['end'])
            self.assertIsNone(e['degree_awarded']); self.assertEqual(e['institution_985'], 'unknown')
        for e in self.ps['lzu-chenlizhi']['education'][:3]:
            self.assertIsNone(e['field']); self.assertEqual(e['degree_category'], '理学')
        self.assertEqual(self.event('lzu-changqingquan',3)['degree'], '本科')
        self.assertIsNone(self.event('scu-tangjianhua',1)['degree'])
        self.assertEqual(self.consumers()['people']['scu-tangjianhua']['stages']['bachelor'], [])

    def test_11_nwpu_joint_training_is_one_twente_doctorate_and_not_two_awards(self):
        p = self.ps['nwpu-libinlong']; e = self.event(p['person_id'],3)
        self.assertEqual(e['institution'], 'University of Twente')
        self.assertEqual(e['degree_awarded_date'], '2012-09-20')
        self.assertEqual(self.consumers()['people'][p['person_id']]['stages']['doctor'], [e['event_id']])
        self.assertEqual({m['education_event_id'] for m in p['mentors']}, {e['event_id']})
        self.assertEqual({m['name'] for m in p['mentors']}, {'张胜贵','Hajo Broersma'})

    def test_12_scut_combined_study_period_and_joint_training_overlap_preserved(self):
        e = self.event('scut-chenbocong',1)
        self.assertIsNone(e['start']); self.assertEqual(e['end'], '2013-06')
        self.assertEqual(e['reported_study_period']['start'], '2007-09')
        self.assertEqual(e['degree_awarded_date'], '2013')
        self.assertEqual(e['degree_award_source_id'], 'scut-chenbocong-source-3')
        p = self.ps['scut-chenpei']
        self.assertEqual((p['education'][2]['end'],p['education'][3]['start'],p['education'][3]['end']), ('2018-07','2017-10','2018-10'))
        self.assertEqual(p['education'][3]['event_kind'], 'joint_doctoral_training')
        self.assertIs(p['education'][3]['degree_awarded'], False)
        self.assertTrue(all(e['degree_awarded_date'] is None for e in p['education'][:3]))

    def test_13_sysu_enrolment_award_defense_and_news_conflicts_remain_distinct(self):
        e = self.event('sysu-chenbingyi',1)
        self.assertEqual(e['start'], '2016'); self.assertIsNone(e['end']); self.assertIsNone(e['degree_awarded'])
        self.assertEqual(e['indexed_award_statement']['year'], 2021)
        self.assertEqual(e['indexed_award_statement']['status'], 'official_search_index_only')
        e = self.event('sysu-chengcheng',1)
        self.assertEqual(e['end'], '2017'); self.assertIsNone(e['degree_awarded_date'])
        self.assertEqual(e['conflicting_source_statement']['value'], 'PhD, Summer 2016')
        self.assertIn('2017.07.06', e['conflicting_source_statement']['note'])
        for pid in ('sysu-chenbingyi','sysu-chengcheng'):
            e=self.event(pid,2); self.assertIsNone(e['start']); self.assertIsNone(e['end']); self.assertIs(e['degree_awarded'],False)

    def test_14_uestc_two_doctorates_do_not_borrow_defense_or_first_job_dates(self):
        p = self.ps['uestc-jonas-kahn']
        self.assertEqual(len(p['education']), 2)
        self.assertTrue(all(e['degree_awarded'] is True for e in p['education']))
        self.assertTrue(all(e['start'] is None and e['end'] is None and e['degree_awarded_date'] is None for e in p['education']))
        self.assertEqual(p['education'][0]['thesis_defense_date'], '2009-09')
        self.assertEqual(p['mentors'][0]['education_event_id'], p['education'][0]['event_id'])
        e = self.event('uestc-guyiqi',4)
        self.assertEqual(e['source_reported_first_job_after_graduation_year'], '2019')
        self.assertIsNone(e['start']); self.assertIsNone(e['end'])
        self.assertEqual(e['start_basis'], 'first_job_reported_year_not_exact_appointment_date')

    def test_15_xjtu_visits_keep_fifteen_rows_and_no_invented_order_or_duration(self):
        p = self.ps['xjtu-lidongsheng']; visits=p['education'][1:]
        self.assertEqual(len(visits),15)
        self.assertTrue(all(e['event_kind']=='academic_visit' and e['degree_awarded'] is False for e in visits))
        october=[e for e in visits if e['start']=='2015-10']
        self.assertEqual([e['institution'] for e in october], ['Albeta大学（原文拼写）','Georgia理工（原文机构名）','普林斯顿大学'])
        self.assertTrue(all(e['end']=='2015-10' for e in october))
        self.assertTrue(all('不推顺序' in e['note'] for e in october))
        e=self.event('xjtu-zhangzhengce',2)
        self.assertIsNone(e['start']); self.assertEqual(e['end'],'2000')
        self.assertIn('1995',e['note'])
        self.assertEqual(self.ps['xjtu-zhangzhengce']['institution_join_date']['value'],'2003')

    def test_16_all_mentor_dates_stages_and_source_statuses_preserved(self):
        for pid, expected in EXPECTED_MENTORS.items():
            original=source_view(self.ps[pid])
            self.assertEqual([tuple(m.get(k) for k in MENTOR_KEYS) for m in original['mentors']], expected, pid)
        kinds=Counter(m['relationship_kind'] for p in self.pro for m in p['mentors'])
        self.assertEqual(kinds, {'doctoral_advisor':13,'masters_advisor':4,'postdoctoral_advisor':4,'postdoctoral_co_advisor':2,'undergraduate_thesis_advisor':1})
        for p in self.pro:
            for m in p['mentors']:
                self.assertIs(m['include_in_mentorship_graph'],True)
                self.assertIs(m['include_in_verified_mentor_count'],True)
                self.assertEqual(m['relationship_status'],'verified_direct_statement')
                self.assertIsNone(m['person_id'])
                self.assertEqual(next(x for x in self.consumers()['people'][p['person_id']]['mentors'] if x['name']==m['name'] and x['events']==[m['education_event_id']])['events'],[m['education_event_id']])

    def test_17_lzu_degree_and_postdoctoral_relations_never_collapse(self):
        p=self.ps['lzu-changqingquan']
        self.assertEqual([(m['name'],m['relationship_kind'],m['education_event_id']) for m in p['mentors']], [
            ('孙春友','doctoral_advisor','lzu-changqingquan-education-1'),
            ('马闪','masters_advisor','lzu-changqingquan-education-2'),
            ('曹道民','postdoctoral_advisor','lzu-changqingquan-education-4')])
        self.assertTrue(all(m['date_basis']=='education_period_not_independently_verified_supervision_dates' for m in p['mentors']))
        p=self.ps['lzu-chengxiyou']
        self.assertEqual(len([m for m in p['mentors'] if m['name']=='钟承奎']),2)
        self.assertNotIn('杜一宏',[m['name'] for m in p['mentors']])
        self.assertEqual({m['education_event_id'] for m in p['mentors'] if m['name']=='钟承奎'}, {'lzu-chengxiyou-education-1','lzu-chengxiyou-education-2'})

    def test_18_undergraduate_thesis_and_postdoc_are_not_doctoral_degree_advisers(self):
        m=self.mentor('uestc-guyiqi','Xiaoliang Cheng')
        self.assertEqual(m['relationship_kind'],'undergraduate_thesis_advisor')
        self.assertEqual(m['education_event_id'],'uestc-guyiqi-education-1')
        self.assertIn('本科毕业论文',m['type_label'])
        self.assertIsNone(self.event('uestc-guyiqi',1)['degree_awarded'])
        for p in self.pro:
            for m in p['mentors']:
                if m['relationship_kind'].startswith('postdoctoral'):
                    e=next(e for e in p['education'] if e['event_id']==m['education_event_id'])
                    self.assertEqual(e['event_kind'],'postdoctoral_research')
                    self.assertIs(e['degree_awarded'],False)
                    self.assertIn('非学位',m['type_label'])
        self.assertEqual(self.mentor('scut-chenbocong','San Ling')['relationship_kind'],'postdoctoral_co_advisor')

    def test_19_retired_emeritus_and_unverified_profile_availability_cannot_navigate(self):
        blocked=[('nwpu-baixueli','郑斯宁'),('nwpu-guoqianqiao','郭大钧'),('nwpu-guoqianqiao','钮鹏程'),('nwpu-libinlong','Hajo Broersma'),('nwpu-libinlong','张胜贵'),('scut-chenyingshan','易法槐'),('sysu-chengcheng','Ingrid Daubechies'),('uestc-jonas-kahn','Pascal Massart')]
        js=self.consumers()['people']
        for pid,name in blocked:
            with self.subTest(person=pid,mentor=name):
                m=self.mentor(pid,name)
                self.assertFalse(m['quick_link_eligible'])
                self.assertEqual(build.mentor_official_url(m),'')
                row=next(x for x in js[pid]['mentors'] if x['name']==name)
                self.assertEqual((row['url'],row['route']),('',''))
                exported=next(x for x in self.tables(pid)['导师'][1:] if x[1]==name)
                self.assertEqual(exported[7],'')
                self.assertEqual(exported[8],m['source_url'])
                self.assertEqual(exported[9],m.get('profile_source_url'))
                self.assertIn(name,js[pid]['lineage'])
        self.assertTrue(self.mentor('nwpu-baixueli','郑斯宁')['navigation_verified'])
        self.assertTrue(self.mentor('scut-chenyingshan','易法槐')['navigation_verified'])

    def test_20_mixed_emeritus_and_separately_verified_current_employment_keeps_navigation(self):
        pid='uestc-guyiqi';m=self.mentor(pid,'Jie Shen（沈捷）')
        self.assertEqual(m['source_employment_status'],'current_position_at_another_institution_explicit')
        self.assertEqual(m['employment_status'],'active_officially_listed')
        self.assertIn('荣休',m['description']);self.assertIn('东方理工',m['description'])
        self.assertTrue(m['quick_link_eligible']);self.assertTrue(m['navigation_verified'])
        self.assertEqual(build.mentor_official_url(m),m['official_url'])
        row=next(x for x in self.consumers()['people'][pid]['mentors'] if x['name']==m['name'])
        self.assertEqual(row['url'],m['official_url']);self.assertEqual(row['route'],'')
        self.assertEqual(self.tables(pid)['导师'][1][7],m['official_url'])

    def test_21_exact_eight_eligible_mentor_shortcuts_agree_in_js_and_excel(self):
        expected={('lzu-changqingquan','孙春友'),('lzu-changqingquan','马闪'),('nwpu-baixueli','倪维明'),('scut-chenyingshan','戴民'),('scut-chenyingshan','朱长江'),('sysu-chengcheng','Xin Li（李欣）'),('sysu-chengcheng','Qiyu Sun（孙颀彧）'),('uestc-guyiqi','Jie Shen（沈捷）')}
        actual={(p['person_id'],m['name']) for p in self.pro for m in p['mentors'] if m['quick_link_eligible']}
        self.assertEqual(actual,expected)
        for p in self.pro:
            js=self.consumers()['people'][p['person_id']]['mentors']
            rows=self.tables(p['person_id'])['导师'][1:]
            for m,j,row in zip(p['mentors'],js,rows):
                self.assertEqual(j['url'],build.mentor_official_url(m))
                self.assertEqual(row[7],j['url'])
                self.assertEqual(j['route'],'')

    def test_22_unavailable_person_pages_are_not_unblocked_by_official_news_or_lectures(self):
        ids=('nwpu-baixueli','nwpu-guoqianqiao','nwpu-libinlong','sysu-gulinyan','sysu-chenbingyi','sysu-chengcheng','uestc-jonas-kahn','uestc-kongefang')
        js=self.consumers()['people']
        for pid in ids:
            p=self.ps[pid]
            self.assertFalse(p['official_profile_navigation_eligible'])
            self.assertEqual(js[pid]['officialUrl'],'')
            self.assertEqual(self.tables(pid)['总览'][1][3],'')
            self.assertFalse(self.entries[pid]['official_profile_navigation_eligible'])
        for pid in ('uestc-jonas-kahn','uestc-kongefang'):
            p=self.ps[pid]; alternatives=p['alternative_professional_sources']
            self.assertEqual(len(alternatives),1)
            self.assertEqual(alternatives[0]['url'],p['official_url'])
            self.assertIn('非个人主页',alternatives[0]['title'])
            self.assertIn(alternatives[0]['title'],self.tables(pid)['总览'][1][8])
            self.assertIn(alternatives[0]['title'],js[pid]['profileMain'])
            self.assertNotIn('学校官方主页',js[pid]['profileMain'])

    def test_23_pending_identity_distinction_and_actual_routes_do_not_create_profiles(self):
        self.assertEqual(self.ps['scu-lianggemeng']['profile_status'],'profile_details_pending')
        self.assertEqual(self.ps['sysu-gulinyan']['profile_status'],'roster_identity_pending')
        js=self.consumers()
        for pid in PENDING_IDS:
            p=self.ps[pid];e=self.entries[pid]
            self.assertIs(p['detail_count_eligible'],False)
            for key in ('education','mentors','publications'):self.assertEqual(p[key],[])
            self.assertIsNone(e['verified_person_id']);self.assertIs(e['profile_identity_verified'],False)
            self.assertIn('此名录记录尚未绑定个人档案',js['people'][pid]['profileMain'])
            self.assertNotIn('进入已核实身份的人物档案',js['pending'][pid]['html'])
            self.assertIn('候选成果不计正式统计',js['pending'][pid]['html'])
        self.assertTrue(js['pending']['scu-lianggemeng']['matched'])
        self.assertFalse(js['pending']['sysu-gulinyan']['matched'])
        self.assertEqual(js['pending']['sysu-gulinyan']['status'],'档案待建，身份待核对')
        self.assertNotIn('人物身份已匹配',js['pending']['sysu-gulinyan']['html'])
        p=self.ps['scu-lianggemeng']
        self.assertEqual(p['listed_role'],'教师（职称待核）')
        self.assertEqual((p['appointments'][0]['title'],p['appointments'][0]['start']),('教师','2026'))

    def test_24_uestc_center_is_a_root_unit_not_an_invented_math_school_child(self):
        units={o['id']:o for o in self.d['org_units']}
        center=units['uestc-applied-math-center']
        self.assertEqual(center['parent_id'],'uestc')
        self.assertEqual(center['type'],'research_center')
        self.assertEqual(self.consumers()['center'],{'parent':'uestc','schoolContains':True,'falseCollegeParents':[]})
        for p in self.new:
            if p['school_id']=='uestc':
                self.assertEqual(p['organization_id'],center['id'])
                self.assertEqual(p['department_id'],center['id'])
                self.assertTrue(any('数学科学学院' in a['institution'] for a in p['appointments']))
                self.assertIn('父子关系未核',p['organization_scope_label'])
        for p in self.new:
            self.assertEqual(p['campus_ids'],[])
            self.assertEqual(units[p['department_id']]['school_id'],p['school_id'])

    def test_25_selected_roster_counts_and_original_order_never_claim_school_totals(self):
        for sid in SCHOOLS:
            expected=[pid for pid in SOURCE_FINGERPRINTS if pid.startswith(sid+'-')]
            rows=[e for e in self.r['entries'] if e.get('source_person_id') in expected]
            self.assertEqual([e['source_person_id'] for e in rows],expected)
            self.assertEqual([e['id'] for e in rows],[EXPECTED_ROSTER_IDS[pid] for pid in expected])
            bid=sid+'-selected-roster-rotation-001'
            batch=next(b for b in self.r['batches'] if b['batch_id']==bid)
            self.assertEqual(batch['record_count'],3)
            self.assertEqual(batch['raw_observation_count'],3)
            self.assertEqual(batch['count_scope'],'selected_subset_only')
            self.assertIs(batch['coverage_complete'],False)
            coverage=[c for c in self.r['coverage'] if c.get('batch_id')==bid]
            self.assertEqual(sum(c['selected_observation_count'] for c in coverage),3)
            for c in coverage:
                self.assertEqual(c['count_scope'],'selected_subset_only')
                self.assertIsNone(c['full_source_visible_name_count'])
                self.assertIs(c['all_visible_entries_captured'],False)
                self.assertIs(c['coverage_complete'],False)
            for e in rows:
                self.assertEqual(e['selection_status'],'selected_subset')
                self.assertFalse(e['profile_identity_verified'])
                self.assertIsNone(e['verified_person_id'])
        self.assertIs(self.r['totals']['current_employment_count_verified'],False)
        self.assertIs(self.r['totals']['not_unique_people_count'],True)

    def test_26_school_consumer_statistics_use_records_not_selected_scope_or_full_staff(self):
        js=self.consumers()
        for sid in SCHOOLS:
            expected=sum(p['school_id']==sid for p in self.d['people'])
            self.assertEqual(js['schoolStats'][sid]['people'],expected)
            self.assertEqual(js['schoolStats'][sid]['pending'],sum(p['school_id']==sid for p in self.d['pending_people']))
            self.assertEqual(js['schoolStats'][sid]['status'],'部分收录')
            self.assertIn('统计不代表全校教师或学院总数',js['schoolPages'][sid])
            self.assertIn('非完整名录',js['schoolPages'][sid])
        xjtu=next(c for c in self.r['coverage'] if c.get('batch_id')=='xjtu-selected-roster-rotation-001')
        self.assertIn('19',xjtu['selection']);self.assertIn('25',xjtu['selection'])
        self.assertEqual(xjtu['visible_name_count'],3)

    def test_27_publication_types_do_not_turn_theses_news_or_conference_into_journal_articles(self):
        publications=[q for p in self.pro for q in p['publications']]
        self.assertEqual(Counter(q['type'] for q in publications),{'journal_article':32,'doctoral_dissertation':2,'doctoral_thesis':1,'book_chapter':1,'conference_paper':1})
        for pid in ('sysu-chenbingyi','sysu-chengcheng'):
            self.assertEqual(self.ps[pid]['publications'][0]['type'],'doctoral_dissertation')
        self.assertEqual(self.ps['nwpu-libinlong']['publications'][0]['type'],'doctoral_thesis')
        for p in self.pro:
            for q in p['publications']:
                self.assertTrue(q['type_label'])
                self.assertTrue(q['link_status_label'])
                self.assertNotEqual(q.get('link_status'),'full_text_verified')
            self.assertEqual(len(self.tables(p['person_id'])['论文']),len(p['publications'])+1)

    def test_28_sources_event_links_and_roster_observations_are_closed(self):
        observations={o['observation_id']:o for o in self.r['source_observations']}
        for p in self.new:
            sources={s['id']:s['url'] for s in p['sources']}
            self.assertEqual(len(sources),len(p['sources']))
            event_ids={e['event_id'] for e in p['education']}
            for collection in ('education','appointments','mentors','publications'):
                for row in p[collection]:
                    self.assertEqual(sources[row['source_id']],row['source_url'])
                    for key,url_key in [('profile_source_id','profile_source_url'),('degree_award_source_id','degree_award_source_url')]:
                        if row.get(key):
                            self.assertIn(row[key],sources)
                            if row.get(url_key):self.assertEqual(sources[row[key]],row[url_key])
                    for key in ('stage_source_id','thesis_defense_source_id','name_identity_source_id','degree_awarded_source_id'):
                        if row.get(key):self.assertIn(row[key],sources)
            for m in p['mentors']:self.assertIn(m['education_event_id'],event_ids)
            for alt in p.get('alternative_professional_sources',[]):self.assertEqual(sources[alt['source_id']],alt['url'])
            entry=self.entries[p['person_id']]
            self.assertEqual(entry['id'],p['roster_entry_id'])
            self.assertEqual(entry['school_id'],p['school_id'])
            self.assertEqual(entry['organization_id'],p['department_id'])
            self.assertEqual(len(entry['source_observation_ids']),1)
            observation=observations[entry['source_observation_ids'][0]]
            self.assertEqual(observation['record_id'],entry['id'])
            self.assertEqual(observation['source_payload']['source_person_id'],p['person_id'])

    def test_29_excel_keeps_all_tristates_source_notes_and_independent_sheets(self):
        for p in self.pro:
            t=self.tables(p['person_id'])
            self.assertEqual(list(t),['总览','经历','导师','论文','来源'])
            rows=t['经历'][1:1+len(p['education'])]
            self.assertEqual(len(t['经历']),1+len(p['education'])+len(p['appointments']))
            for e,row in zip(p['education'],rows):
                self.assertEqual(row[1],e['event_kind'])
                self.assertEqual(row[3],e['institution'])
                self.assertEqual(row[4:6],[e['start'],e['end']])
                self.assertEqual(row[10],e['institution_985'])
                self.assertIs(row[11],e['degree_awarded'])
                self.assertEqual(row[12],e['degree_awarded_date'])
                self.assertEqual(row[14],e.get('note'))
                self.assertEqual(row[16],e['source_url'])
            self.assertEqual(len(t['导师']),len(p['mentors'])+1)
            for name,rows in t.items():
                self.assertTrue(all(row[-2]==p['school_id'] for row in rows[1:]),name)

    def test_30_actual_graphs_keep_all_twentyfour_relations_without_new_candidates(self):
        js=self.consumers()['people']
        total=0
        for p in self.pro:
            graph=js[p['person_id']]['graph']
            self.assertIn(f"{len(p['mentors'])}条已收录关系",graph)
            self.assertEqual(graph.count('href="#mentor-'),len(p['mentors']))
            total+=len(p['mentors'])
            for m in p['mentors']:
                self.assertIn(m['type_label'],js[p['person_id']]['lineage'])
                self.assertIn(m['name'],graph)
            self.assertEqual(p.get('committee_members',[]),[])
            self.assertEqual(p.get('pending_mentor_candidates',[]),[])
        self.assertEqual(total,24)

    def test_31_existing_nine_teaching_facts_candidates_and_committees_stay_separate(self):
        original=self.d['people'][:499]
        self.assertEqual(sum(len(p.get('teaching') or []) for p in original),9)
        for p in original:
            for t in p.get('teaching') or []:
                self.assertIsNot(t.get('degree_awarded'),True)
                self.assertIsNot(t.get('include_in_mentorship_graph'),True)
            for c in p.get('pending_mentor_candidates',[]):
                self.assertIs(c.get('include_in_mentorship_graph'),False)
                self.assertIsNot(c.get('include_in_verified_mentor_count'),True)
        # Full baseline record fingerprints above also preserve all historical
        # committee, candidate and teaching fields, including absent legacy flags.
        self.assertTrue(any(p.get('committee_members') for p in original))
        self.assertTrue(any(p.get('pending_mentor_candidates') for p in original))

    def test_32_validators_and_consumers_do_not_mutate_release(self):
        before=copy.deepcopy((self.d,self.r))
        self.assertTrue(build.validate(self.d))
        self.assertTrue(validate_rosters(self.r,self.d))
        for p in self.pro:self.tables(p['person_id'])
        self.assertEqual((self.d,self.r),before)
        self.assertTrue(self.consumers()['unchanged'])

    def test_33_source_shape_guard_detects_changed_unknowns_lost_fields_and_dates(self):
        pid='cqu-hechuanjiang';shape_id,expected=SOURCE_FINGERPRINTS[pid]
        for mutation in ('award','date','source'):
            p=source_view(self.ps[pid])
            if mutation=='award':p['education'][0]['degree_awarded']=False
            elif mutation=='date':p['education'][2]['start']='1999-09'
            else:p['sources'][0]['evidence_status']='official_profile_body_read'
            self.assertNotEqual(object_sha(project_source_shape(p,shape_id)),expected)
        p=source_view(self.ps[pid]);del p['education'][2]['start_conflicting_source_values']
        with self.assertRaises(KeyError):project_source_shape(p,shape_id)

    def test_34_new_public_records_contain_no_private_source_cache_or_local_paths(self):
        forbidden={'local_evidence_cache','cache_path','raw_html','raw_pdf','pdf_bytes','raw_response'}
        def check(value):
            if isinstance(value,dict):
                self.assertFalse(forbidden.intersection(value))
                for child in value.values():check(child)
            elif isinstance(value,list):
                for child in value:check(child)
            elif isinstance(value,str):
                self.assertNotIn('/workspace/',value)
                self.assertNotIn('/home/agent/',value)
        check(self.new)
        check(list(self.entries.values()))

    def test_35_employment_canonicalization_cannot_upgrade_retirement_or_uncertainty(self):
        active={'active_officially_listed','official_page_currently_listed',
                'official_faculty_page_currently_listed','official_roster_currently_listed',
                'current_position_at_another_institution_explicit'}
        for p in self.pro:
            for m in p['mentors']:
                source=m['source_employment_status']
                expected=('active_officially_listed' if source in active else
                          {'retired':'retired_officially_listed','emeritus':'emeritus_officially_listed'}.get(source,source))
                self.assertEqual(m['employment_status'],expected,(p['person_id'],m['name']))
                if source not in active:
                    forged=dict(m,official_url='https://example.edu.test/profile',
                                navigation_verified=True,quick_link_eligible=True)
                    self.assertEqual(build.mentor_official_url(forged),'')


if __name__ == '__main__':
    unittest.main(verbosity=2)
