from published_fixture import published_root
from source_date_history import historical_bytes
"""Independent release25 CQU/XMU/BIT source and export regressions.
Pins derive only from hash-approved original packages and immutable release24.
Runtime is repository-self-contained and offline; it does not fetch source pages,
import normalization code, read the research directory, or write build outputs.
"""
from release_history import release25_view
import copy, hashlib, json, os, pathlib, subprocess, sys, unittest
from collections import Counter
from unittest import mock
sys.dont_write_bytecode = True
ROOT = pathlib.Path(os.environ.get('ACADEMIC_ATLAS_TEST_ROOT', pathlib.Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(ROOT / 'scripts'))
import build
from build_rosters import validate_rosters

def object_sha(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()).hexdigest()

SOURCE_PACKAGE_SHA256 = {'cqu': '74c7d1f2908c6fed3fca29f0e577de03465e66c0da54e639299fa5caa70ac7fc',
 'xmu': '2452bed0e40e522e27800abf450c530bd072f55a42d9264305b21d2ae5eb33f8',
 'bit': '8da78ce1206282aff85380ab2831dc73efd0ffc0c9a07a8eb1abf454c6e62477'}

REVIEW_SHA256 = {'cqu': '0317f6e539c923722bc72e5ac3ca6e9a1ac2b7b03a663da3a8b70a97623195eb',
 'xmu': '8cc9848196b2c81933e395661768fd27343644b8cadf981839b02cb4156b23bc',
 'bit': '2525d7a90408f4d99159326dc514b60a6fb1b37213094fa05ae0b1cb6fbfef79'}

# Ordered digests from the release25 source-review gate audit. These are audit
# identities, not public source URLs or inferred person/batch identities.
REVIEWED_AUDIT_SHA256 = ['74c7d1f2908c6fed3fca29f0e577de03465e66c0da54e639299fa5caa70ac7fc',
 '9b4ade648e6f98b2824f893349a257c60eadccba5c03d3391318908c23c6bec1',
 '9d615fbb0a3f60542286ff3fe8e20cee8a359be8c20419c4aa706b054e8ed630',
 '0317f6e539c923722bc72e5ac3ca6e9a1ac2b7b03a663da3a8b70a97623195eb',
 '1ef06e86335bb49dc0993c0ca846373a7b1523c4f6b4bcded61431f1242d1445',
 '4ca72ccc9566b64097a79bebee40ed1d4861b854cd6d3d5d7780dc173a3166e2',
 '8271d529dd296e475791c03644e1c2d232263c333f9640ef5e486a20ac3c0d50',
 '1ad0ad1f34dc83b1473eaa6c925b1e3f68c2ae132fbf8c9d15bc09355b272bf2',
 '6d260b4701b7d76321d3930b78fd741a4a9a5dadb03e8a7fb13d127ee7158662',
 '61a7d0fd9f5db4b54e9d497cf5131a55292c5c9f5f198b4b0ce61c966cda7097',
 'edd94a91e3efd0e6ff1a8c14d1bd01cf095562b192e2b0a1f694faf9ea81144d',
 '4cd4503d03541e23fb4ebe65f2225f661b52ba4e56815701153431eaea3ae48a',
 'f8ae7f3ab58442bf42003d8b19dcd5f38a8d049b8353993493d7589b1a77e8e5',
 '8d6f87fd550952e534e3d35be6e86df2131b5b2a258d81cd189b5f78f39e3be6',
 'b71f8a55aa3918390bcefd2c690d0da041d040daeb3695c3363e2d28611cd068',
 '566796cfea63506bf5294d4eb27198169997263f16f998477a2b025585579ef6',
 'd9f130628bcb0f8db2bc6cfcf6fc741157a53479b59cf6ddb67f722184437b47',
 '72d0a080e390d36076d7da18bc4765aa120cdb0c206f945189bcd6c0711de6ef',
 '2452bed0e40e522e27800abf450c530bd072f55a42d9264305b21d2ae5eb33f8',
 'a8235186a33f1507758f1132d2546f41fc4321d14ea9566d3706efda6b66aa6c',
 'abb6f98c0ca80f9cc4bddd28e75d708cb560cba28ca4bcc3925c81caae779124',
 '8cc9848196b2c81933e395661768fd27343644b8cadf981839b02cb4156b23bc',
 'feeaf23ea7003ef2928cb8d474674a954acc460bfd9a3f012e4f787cb53234d2',
 '49faae45b02fc5bc626daf879d7a6316da6f0a89ee1c3fbffebf553ae9449ee4',
 '7817f1d686abc23cb86a4d70f35ca4126d51d250f1f48f0715683acae1b4828c',
 '96d020ee0eb7f9e26e604354debdbab1014329a7d31156e7585183682f34bd86',
 '494c6f4012f1dfad40f48312ca5e6a2ef5bf576c07f912f2885650bc7879701b',
 '8146b9ff1579a0771543aeab7e48b7f78d6174831ae3a85f85d848eeb854b2c3',
 '8da78ce1206282aff85380ab2831dc73efd0ffc0c9a07a8eb1abf454c6e62477',
 '9368934ce21c4187cc799afdf22d04b51a4a3383a8a5ce53837f55c87cce3123',
 'e42b53ac5007e2a6749067ba8d576c17c737fbd32ee66a7a1838f4c5bc5654dc',
 '2525d7a90408f4d99159326dc514b60a6fb1b37213094fa05ae0b1cb6fbfef79',
 '8e2b9466b32655fd6be2d6a4a72cc298e9628cc40ff254673294028784e23d7f',
 'fc4da6c1453fda6a06a35952ac6136a9dbb24e7841781ebaab53cbd398cfabb8',
 '63bb823c42fb7c23e2ccb0d8d3ee80dd26d853a57a5ff6aeb97baed2604a6937',
 '060cd94936166e8c3cc983f6688ac10f797f0008674b795c7369a16f6e017082',
 'bf67bfbaa5d07d7575f3f15d69c23adc5ac510530a4701a17a5f57156bece00d',
 '9a41ca7d080e0d35f70362acc1a02aa70ab155a6105c311dedc9fc16bf8012fa']

# School and audit roles are fixed by the existing school coverage ledgers.
REVIEWED_COMPANION_SHA256 = {'cqu': {'scope': '9b4ade648e6f98b2824f893349a257c60eadccba5c03d3391318908c23c6bec1',
         'qa': '9d615fbb0a3f60542286ff3fe8e20cee8a359be8c20419c4aa706b054e8ed630'},
 'xmu': {'scope': 'a8235186a33f1507758f1132d2546f41fc4321d14ea9566d3706efda6b66aa6c',
         'qa': 'abb6f98c0ca80f9cc4bddd28e75d708cb560cba28ca4bcc3925c81caae779124'},
 'bit': {'scope': '9368934ce21c4187cc799afdf22d04b51a4a3383a8a5ce53837f55c87cce3123',
         'qa': 'e42b53ac5007e2a6749067ba8d576c17c737fbd32ee66a7a1838f4c5bc5654dc'}}

BASELINE_ATLAS_PREFIXES = {'limitations': (6, 'a49996988d143a02303ec539cb493667cdc9b28a287271ae141f6cfd7b95021a'),
 'campuses': (4, 'a29d9956fbbc284b9cdafc640ac9057dd4512c2181d89780a92a6a8bf01e6505'),
 'org_units': (223, '3ceb45d689ae3198f17add4b27d4375875d1c799584194088d7bc1cc6e7c42e9'),
 'people': (547, '6c2bab0dd914c22e91e4cce78fbcbc5395bee3f2a1014983621bc1e5466c718e'),
 'profile_batches': (134, 'b27b18eff5232ab03afd3c6a344f9b85d4a5aca126ec7be775c4c2ec99472cf5'),
 'pending_people': (83, '7bf2a61c24b2737d8d175bc65545de28d54f65214313881144efaa43dcc89bb5'),
 'normalization_evidence': (14, '64318a251e1155ca272bc828f8bfd1ac215deb7a749ef05afe3dda14745d2923'),
 'institutions': (39, '8234ea78331d931b8a54c5f40d4427a7844e7fcd621d0832a69e5f2df1b41848')}

BASELINE_ATLAS_UNCHANGED = {'schema_version': '5a4747fcdafec66d8d8812022e3b7d2666d886ec0e0ee7926ec8c50db40f29d5',
 'institution': '9b9fab8a1164afafcf855e8d6ccea17a09e973b8ea2fd8a4831ad681490e8d01',
 'coverage': '8301d88ec52e91fd40964298ce12e179dc0c4ca513b3a0cefa9ad57db895f597'}

BASELINE_ROSTER_PREFIXES = {'summary': (141, '28d5a081ac89603d986517ab567533c5306dc3a51bc6d7fefefa8734340f14f6'),
 'coverage': (212, '4eda3747cbca915587085b0438b61e05b50cbb7bca7ad2b952d84d15255736bf'),
 'entries': (1712, '4f39dd834f4dd3468a1e0354ff5b5abdaf312859b7eb86966c5b4dc6a720813f'),
 'conflicts': (30, '0f809e3a2c4ef1857b03479230f35a342b703ccf5f8a99ef032271d150c44c09'),
 'limitations': (35, '4fe8dea8da59fb3789194955a1b22aac4453cbf0e6a4d1cc2e82d172ba77c116'),
 'dedup_candidates': (60, '0a1adbff0d7b0ae2fe42cceff9a89e5e9eb6d164044456f319cfab6c9d1b1653'),
 'exclusions': (3, '89dc768c034efe9de60bb4199c92be749ea7f1bb1405daceff0e3ca88fa5228d'),
 'pending_checks': (2, '143ba1254ce843007ed487ca7f7ef2c684912b54c0580c6bb3f7157b7bc61048'),
 'source_snapshots': (36, 'bae26c4aa31edf9ee3212a7723508241f475441863f03f69a8058264ad3b81c2'),
 'batches': (107, '9ed2cf5d1a7302dfa70733e257cc4290b592ea38f19db4d33ce86756986705d7'),
 'source_observations': (1750, 'a33dc278373f5d6ceab25b0540d2404c22b6e7ac228827e51776979c6d757f4b'),
 'consolidations': (2, '094423def9986b8e47457a6592e143f75d67eaa7647c2c346df93d54b983e4e0'),
 'supporting_method_evidence': (4, 'db4e111a865957df036ada510d96050eb5c2b39ed6635c628d48a9a2717ec547'),
 'local_mapping_corrections': (4, '9a1ccc7df1e46b7e8240c3963456fcaf0177d07ad31c051db7d1d5334a1aca1d'),
 'withdrawn_local_conflicts': (1, '8b54b3a107c8f050e3c33cc2125a710a4084b1be287fdb20db8ca392c093ed05')}

BASELINE_ROSTER_UNCHANGED = {'schema_version': '5a4747fcdafec66d8d8812022e3b7d2666d886ec0e0ee7926ec8c50db40f29d5',
 'role_interpretation': '9c1098d16b8ae13b4ef55efb781195831efdc1be68fd601aa8c4d1db41cea7c0'}

BASELINE_QUEUE_PREFIX = (219, 'fa8e5964fc279cc7a8308aff80e2c47a23afd1459af5bb489bda91085be9f8ce')

UNCHANGED_APPLICATION_SHA256 = {'site/styles.css': '6063be4c04726d2dcf01a0442d5dc4d763b99c835a4110bd943799582c14fc34',
 'site/universities.js': '9323dad42fc2c35808ad92888cdffb0ad41edaefaee88c3b57ebb798349c2d62',
 'scripts/build_rosters.py': 'bc00cde087ec2ba1065b4ac2332fda16918885ec497c2c34dbd319d16f96a7bf',
 'scripts/deterministic_xlsx.py': '65158f54d001eebb2ac586fd820cd69deed8e5c96ed5b117668ced51c11dc300'}

SOURCE_CONTEXT_FINGERPRINTS = {'cqu': (120, '754d8404c5044156c7beb30090c7beb80771e5f9aff66a2174e329d044caa7a8'),
 'xmu': (125, '75355ae7f654af82e2bb14e66c547e82ac9782effc93a285d94a6bd33ebea150'),
 'bit': (128, 'e3aa4fb9c8cbacad2a8989993d131ca86c287b67d24ac0f6d2a4d01162a593d6')}

SOURCE_FINGERPRINTS = {'cqu-chenke': (27, '6a01db50b8333897fc12e8c865711281e13aaea78ce37dd43ec203e36e74e799'),
 'cqu-chenrenwei': (30, '7d9fa14ff549f5a37c9168aa3fe03098f62cb3c1f625873cccfafa8c0f0f5a3b'),
 'cqu-chenxiaomeng': (47, '68c274575fb66e52e17799d672a08b97f0d80c3c752483c4d5f0bfa4c43cc1dc'),
 'xmu-chenhuang-economics': (61, 'd9ce542ed698299d8b05e38f448cff50849840ab89ed2a47f73221637d18e39f'),
 'xmu-chenwanyi': (69, '7d60e2db31114ccfd772c4f325adb54b5142b816ba453653b95ea004d7fb5320'),
 'xmu-dingchangfa': (78, '9d0113ed88a63d367c017b707f1fbbdb61f86857ad78c12bfecab0b1671c8056'),
 'bit-chentian': (86, '9e558810816c94697b8c3eb87ce45fadc5761ccb4cc8e278b52c8ad98ca21b21'),
 'bit-chenyuhui': (98, '3b4e80f831fe9d0854ed1157a7bda83d156f4194e69057ded145541ad5be8dc1'),
 'bit-daiyunyun': (111, '887097633a155c3b21ef259d2dfa338131d6e192ecb403b0dc0313da2a60ea08')}

ORG_FINGERPRINTS = {'cqu-architecture-urban-planning': (112, '5ca980b5afd17e66d7626fa23bd8d70319678cfd6727b7ad932627e74ba83e41'),
 'xmu-economics-school': (112, '4b0b37c6b3eb089b5e085f49f1184a30cc21ee15f538f207c218a8f3f5bcf082'),
 'xmu-economics-department': (112, '7aa9c6fbfad09c29ba9d3aaa61d895fafdbc5ace6a09f1b3c8e3d97833c21c55'),
 'bit-physics': (113, '439ad7dbc15206d391b98fa24f354ee6657b2322030127ff166b936a2cd783da'),
 'bit-physics-optical': (113, 'c30374c0cca101021f5c0f46de85ed6b686ba2dcf800c99e67b456311a45a986'),
 'bit-frontier-interdisciplinary-institute': (114, '9d896cea97612caf2ec8580707f1c58272327be1edcd8a21b880c73a12de8f4a')}

SOURCE_LEAF_COUNTS = {'cqu-chenke': 217,
 'cqu-chenrenwei': 53,
 'cqu-chenxiaomeng': 270,
 'xmu-chenhuang-economics': 240,
 'xmu-chenwanyi': 251,
 'xmu-dingchangfa': 260,
 'bit-chentian': 268,
 'bit-chenyuhui': 310,
 'bit-daiyunyun': 307}

EXPECTED_IDS = {'cqu': ['cqu-chenke', 'cqu-chenrenwei', 'cqu-chenxiaomeng'],
 'xmu': ['xmu-chenhuang-economics', 'xmu-chenwanyi', 'xmu-dingchangfa'],
 'bit': ['bit-chentian', 'bit-chenyuhui', 'bit-daiyunyun']}

PROFESSIONAL_IDS = ['cqu-chenke',
 'cqu-chenxiaomeng',
 'xmu-chenhuang-economics',
 'xmu-chenwanyi',
 'xmu-dingchangfa',
 'bit-chentian',
 'bit-chenyuhui',
 'bit-daiyunyun']

PENDING_IDS = ['cqu-chenrenwei']

EXPECTED_COUNTS = {'cqu-chenke': {'campus_ids': 0,
                'sources': 5,
                'unknowns': 4,
                'appointments': 2,
                'education': 1,
                'mentors': 0,
                'committee_members': 0,
                'publications': 0,
                'research_fields': 0,
                'academic_service': 0,
                'teaching': 2,
                'honors': 1,
                'research_projects': 0,
                'pending_education_candidates': 0,
                'pending_mentor_candidates': 0,
                'pending_appointment_candidates': 0,
                'pending_professional_fact_candidates': 0},
 'cqu-chenrenwei': {'campus_ids': 0,
                    'sources': 2,
                    'unknowns': 3,
                    'appointments': 0,
                    'education': 0,
                    'mentors': 0,
                    'committee_members': 0,
                    'publications': 0,
                    'research_fields': 0,
                    'academic_service': 0,
                    'teaching': 0,
                    'honors': 0,
                    'research_projects': 0,
                    'pending_education_candidates': 0,
                    'pending_mentor_candidates': 0,
                    'pending_appointment_candidates': 0,
                    'pending_professional_fact_candidates': 0},
 'cqu-chenxiaomeng': {'campus_ids': 0,
                      'sources': 2,
                      'unknowns': 5,
                      'appointments': 1,
                      'education': 3,
                      'mentors': 0,
                      'committee_members': 0,
                      'publications': 0,
                      'research_fields': 3,
                      'academic_service': 2,
                      'teaching': 0,
                      'honors': 1,
                      'research_projects': 0,
                      'pending_education_candidates': 0,
                      'pending_mentor_candidates': 0,
                      'pending_appointment_candidates': 0,
                      'pending_professional_fact_candidates': 0},
 'xmu-chenhuang-economics': {'campus_ids': 0,
                             'appointments': 1,
                             'education': 3,
                             'mentors': 0,
                             'committee_members': 0,
                             'publications': 1,
                             'sources': 3,
                             'unknowns': 4,
                             'pending_education_candidates': 0,
                             'pending_mentor_candidates': 0,
                             'pending_appointment_candidates': 0,
                             'pending_professional_fact_candidates': 0,
                             'research_fields': 5},
 'xmu-chenwanyi': {'campus_ids': 0,
                   'appointments': 2,
                   'education': 3,
                   'mentors': 0,
                   'committee_members': 0,
                   'publications': 1,
                   'sources': 4,
                   'unknowns': 4,
                   'pending_education_candidates': 0,
                   'pending_mentor_candidates': 0,
                   'pending_appointment_candidates': 0,
                   'pending_professional_fact_candidates': 0,
                   'research_fields': 2},
 'xmu-dingchangfa': {'campus_ids': 0,
                     'appointments': 2,
                     'education': 4,
                     'mentors': 0,
                     'committee_members': 0,
                     'publications': 0,
                     'sources': 3,
                     'unknowns': 5,
                     'pending_education_candidates': 0,
                     'pending_mentor_candidates': 0,
                     'pending_appointment_candidates': 0,
                     'pending_professional_fact_candidates': 0,
                     'research_fields': 3},
 'bit-chentian': {'campus_ids': 0,
                  'appointments': 3,
                  'education': 3,
                  'mentors': 0,
                  'committee_members': 0,
                  'publications': 1,
                  'sources': 2,
                  'unknowns': 3,
                  'pending_education_candidates': 0,
                  'pending_mentor_candidates': 0,
                  'pending_appointment_candidates': 0,
                  'pending_professional_fact_candidates': 0,
                  'research_fields': 3},
 'bit-chenyuhui': {'campus_ids': 0,
                   'appointments': 3,
                   'education': 3,
                   'mentors': 1,
                   'committee_members': 0,
                   'publications': 1,
                   'sources': 3,
                   'unknowns': 3,
                   'pending_education_candidates': 1,
                   'pending_mentor_candidates': 0,
                   'pending_appointment_candidates': 0,
                   'pending_professional_fact_candidates': 0,
                   'research_fields': 2},
 'bit-daiyunyun': {'campus_ids': 0,
                   'appointments': 1,
                   'education': 4,
                   'mentors': 0,
                   'committee_members': 0,
                   'publications': 1,
                   'sources': 3,
                   'unknowns': 4,
                   'pending_education_candidates': 0,
                   'pending_mentor_candidates': 0,
                   'pending_appointment_candidates': 1,
                   'pending_professional_fact_candidates': 0,
                   'research_fields': 3}}

EXPECTED_EDUCATION = {'cqu-chenke': [{'event_id': 'cqu-chenke-education-1',
                 'degree': None,
                 'institution': '重庆大学',
                 'start': None,
                 'end': None,
                 'event_kind': 'education_level_unknown',
                 'degree_awarded': None,
                 'degree_awarded_date': None}],
 'cqu-chenrenwei': [],
 'cqu-chenxiaomeng': [{'event_id': 'cqu-chenxiaomeng-education-1',
                       'degree': '学士',
                       'institution': '同济大学',
                       'start': '2007-09',
                       'end': '2011-07',
                       'event_kind': 'degree_study',
                       'degree_awarded': None,
                       'degree_awarded_date': None},
                      {'event_id': 'cqu-chenxiaomeng-education-2',
                       'degree': '硕士',
                       'institution': '慕尼黑工业大学',
                       'start': '2011-09',
                       'end': '2014-09',
                       'event_kind': 'degree_study',
                       'degree_awarded': None,
                       'degree_awarded_date': None},
                      {'event_id': 'cqu-chenxiaomeng-education-3',
                       'degree': '博士',
                       'institution': '清华大学',
                       'start': '2017-08',
                       'end': '2022-06',
                       'event_kind': 'degree_study',
                       'degree_awarded': None,
                       'degree_awarded_date': None}],
 'xmu-chenhuang-economics': [{'event_id': 'xmu-chenhuang-economics-education-1',
                              'degree': '学士',
                              'institution': '南京农业大学',
                              'start': '2005',
                              'end': '2009',
                              'event_kind': 'degree_study',
                              'degree_awarded': None,
                              'degree_awarded_date': None},
                             {'event_id': 'xmu-chenhuang-economics-education-2',
                              'degree': '硕士',
                              'institution': '中国科学院',
                              'start': '2009',
                              'end': '2012',
                              'event_kind': 'degree_study',
                              'degree_awarded': None,
                              'degree_awarded_date': None},
                             {'event_id': 'xmu-chenhuang-economics-education-3',
                              'degree': '博士',
                              'institution': '加州大学戴维斯分校',
                              'start': '2013',
                              'end': '2018',
                              'event_kind': 'degree_study',
                              'degree_awarded': None,
                              'degree_awarded_date': None}],
 'xmu-chenwanyi': [{'event_id': 'xmu-chenwanyi-education-1',
                    'degree': '学士',
                    'institution': '武汉大学',
                    'start': None,
                    'end': '2011',
                    'event_kind': 'degree_study',
                    'degree_awarded': None,
                    'degree_awarded_date': None},
                   {'event_id': 'xmu-chenwanyi-education-2',
                    'degree': '学士',
                    'institution': '武汉大学',
                    'start': None,
                    'end': '2011',
                    'event_kind': 'degree_study',
                    'degree_awarded': None,
                    'degree_awarded_date': None},
                   {'event_id': 'xmu-chenwanyi-education-3',
                    'degree': '博士',
                    'institution': '威斯康星大学麦迪逊分校',
                    'start': None,
                    'end': '2018',
                    'event_kind': 'degree_study',
                    'degree_awarded': None,
                    'degree_awarded_date': None}],
 'xmu-dingchangfa': [{'event_id': 'xmu-dingchangfa-education-1',
                      'degree': '硕士',
                      'institution': '福建师范大学',
                      'start': '1994-08',
                      'end': '1997-07',
                      'event_kind': 'degree_study',
                      'degree_awarded': None,
                      'degree_awarded_date': None},
                     {'event_id': 'xmu-dingchangfa-education-2',
                      'degree': '博士',
                      'institution': '厦门大学',
                      'start': '1999-09',
                      'end': '2002-07',
                      'event_kind': 'degree_study',
                      'degree_awarded': None,
                      'degree_awarded_date': None},
                     {'event_id': 'xmu-dingchangfa-education-3',
                      'degree': None,
                      'institution': '墨尔本皇家理工学院',
                      'start': '2007-07',
                      'end': '2007-08',
                      'event_kind': 'academic_exchange_or_training',
                      'degree_awarded': False,
                      'degree_awarded_date': None},
                     {'event_id': 'xmu-dingchangfa-education-4',
                      'degree': None,
                      'institution': '康奈尔大学',
                      'start': '2008-08',
                      'end': '2009-06',
                      'event_kind': 'academic_visit',
                      'degree_awarded': False,
                      'degree_awarded_date': None}],
 'bit-chentian': [{'event_id': 'bit-chentian-education-1',
                   'degree': '学士',
                   'institution': '南开大学',
                   'start': '2006',
                   'end': '2010',
                   'event_kind': 'degree_study',
                   'degree_awarded': None,
                   'degree_awarded_date': None},
                  {'event_id': 'bit-chentian-education-2',
                   'degree': '博士',
                   'institution': '清华大学',
                   'start': '2010',
                   'end': '2015',
                   'event_kind': 'degree_study',
                   'degree_awarded': None,
                   'degree_awarded_date': None},
                  {'event_id': 'bit-chentian-education-3',
                   'degree': None,
                   'institution': '美国斯蒂文森理工学院',
                   'start': '2013',
                   'end': '2014',
                   'event_kind': 'academic_visit',
                   'degree_awarded': False,
                   'degree_awarded_date': None}],
 'bit-chenyuhui': [{'event_id': 'bit-chenyuhui-education-1',
                    'degree': '理学学士',
                    'institution': '中山大学',
                    'start': '2004',
                    'end': '2008',
                    'event_kind': 'degree_study',
                    'degree_awarded': True,
                    'degree_awarded_date': '2008'},
                   {'event_id': 'bit-chenyuhui-education-2',
                    'degree': '博士',
                    'institution': '中国科学院物理研究所',
                    'start': None,
                    'end': None,
                    'event_kind': 'degree_study',
                    'degree_awarded': True,
                    'degree_awarded_date': '2013'},
                   {'event_id': 'bit-chenyuhui-education-3',
                    'degree': None,
                    'institution': '新西兰奥塔哥大学',
                    'start': '2013',
                    'end': '2017',
                    'event_kind': 'postdoctoral_research',
                    'degree_awarded': False,
                    'degree_awarded_date': None}],
 'bit-daiyunyun': [{'event_id': 'bit-daiyunyun-education-1',
                    'degree': '学士',
                    'institution': '南京大学',
                    'start': '2007',
                    'end': '2011',
                    'event_kind': 'degree_study',
                    'degree_awarded': None,
                    'degree_awarded_date': None},
                   {'event_id': 'bit-daiyunyun-education-2',
                    'degree': '博士',
                    'institution': '复旦大学',
                    'start': '2011',
                    'end': '2017',
                    'event_kind': 'degree_study',
                    'degree_awarded': None,
                    'degree_awarded_date': None},
                   {'event_id': 'bit-daiyunyun-education-3',
                    'degree': None,
                    'institution': '丹麦科技大学',
                    'start': '2014',
                    'end': '2014',
                    'event_kind': 'academic_visit',
                    'degree_awarded': False,
                    'degree_awarded_date': None},
                   {'event_id': 'bit-daiyunyun-education-4',
                    'degree': None,
                    'institution': '芬兰阿尔托大学（Aalto University）',
                    'start': '2017-04',
                    'end': '2021-12',
                    'event_kind': 'postdoctoral_research',
                    'degree_awarded': False,
                    'degree_awarded_date': None}]}

EXPECTED_SCOPES = {'cqu': '建筑城规学院官方教师列表原生7页共65条，原序首3陈科、陈仁伟、陈肖萌。只完成2人的部分职业资料，陈仁伟仅身份与学院归属待补；不替换稀疏人选。未按学历、海外或资料丰富度选人，非全院或全校覆盖；名录现列不等全职人事证明。',
 'xmu': '经济学院“师资队伍 > 教学科研人员 > 经济学系”单页名录29人，按官方原序首3陈煌、陈琬祎、丁长发。本批仅3条部分公开职业档案，不是该系、学院或全校完整覆盖；官方名录在列不等全职或正式人事在岗核验。',
 'bit': '物理学院·光学物理系“师资名录 > '
        'ALL”原序首3：陈天、陈宇辉、戴贇贇。同次直接GET两页20+13名且各显示33条；较早reader第一页34/第二页33差异另存，未宣称无争议类别总数。仅3人公开职业资料；戴贇贇的名录抽样归属与前沿交叉科学研究院任职正文分开，不是物理学院在岗或双聘证明。'}

EXPECTED_SCOPE_ENTRIES_SHA256 = {'cqu': '0b3248e2e11b1ea15a1d0c4f21642ff8879d5ea2d78096f664a5e1b2d58d64df',
 'xmu': '5205842e252e03958ba72bdeab1838707c3a0decc3aae548ff43f8001134320a',
 'bit': '43442bbfe5d07f5ea603dc493119080b97bd0e983fd9dac5e0eec8c9eb47719c'}

EXPECTED_REVIEW_LIMITS = {'cqu': ['严格2职业+1pending：陈仁伟原序第二必须进入待补层，不能换人、增加到职业统计或因包people数组而自动算完成。',
         '65人是该大学门户建筑城规学院当前观察名录，只有首3处理；不是全学院、全校或全部人事在岗核验。不得信旧搜索URL totalpage=4。',
         '陈科两新闻只支持有日期的历史事实，必须显示官方完整缓存正文已读、源站直连404的差异，并保留source_navigation_enabled=false及来源navigation_enabled=false；不可改为实时正文可访问、索引摘要或已核2026职称。',
         '4教育全degree_awarded=null；陈科毕业院校未知层次事件关闭教育筛选，不得补成学士或985本科。其他三段可作学习经历，但不能计明确获授。',
         '2020赛事年度、2021-03-31公布通知与授奖日不能合并；2025-09-18科普首讲不是持续任课。陈肖萌2025-03-05入职不等副教授晋升日期，两期刊编委2026-06已终止。',
         '具名本人导师0、当前导师导航0，校区未知；硕导资格、资助项目和刊物编委不可变师承。',
         '原先学院网站412路线已停止，审查没有访问或重试该路线。陈仁伟reader内部错误不等源站拒绝，普通公开HTTPS200验证与其区别已记录。',
         '本文件为原始研究包来源独审；原始地域/985及消费者字段规范化、pending迁移和缓存来源失效导航的消费者验证由独立整合流程执行。'],
 'xmu': ['仅经济学系29人中原序首3部分职业资料，不是全系、全院或全校完成。',
         '8条学位标签/攻读经历授位null，不得计为已核获授；2条进修访问为非学位，不得计海外学位。陈琬祎两个学士标签不支持推断双学位培养机制。',
         '陈煌历史任职双机构与当前经济学系名录、陈琬祎WISE履历与经济学系名录必须分层；2021新闻不证明2026双聘或全职人事状态。丁长发1997-10不等副教授晋升日期。',
         '无具名本人导师、博士后导师、委员会或访问指导关系可新增；校区未知，不能由办公室位置推定。',
         '仅2条精选本人官方书目，不声称出版社单篇与全文核验；原始成功证据只保留必要职业摘录，不扩展为公开原始网页缓存。',
         '本文件为原始研究包独立来源审查；地域、985与消费者字段的规范化及集成schema验证仍由独立整合流程执行。'],
 'bit': ['仅光学物理系ALL栏目首3观察，不是全系全院完成。两页reader34/33和研究者直接GET33/33快照均需保留；33是观察到的姓名数，不得显示为无条件完整在岗总数。',
         '陈宇辉博士学习start/end必须继续null，反向区间候选不得参与正常年表；独立获授2008/2013保持年精度，不代填学习入学/结束日期。',
         '2条获授true、4条null与4条非学位须分开；博士后与访问不计海外学位，部门名称不自动等专业。',
         '戴贇贇首要任职来源单位为前沿交叉科学研究院；物理学院·光学物理系只为抽样来源。当前职称null与2022-10晋升冲突候选不得在消费者中转为已核职称或双聘。页眉机构更名沿革未核。',
         '李志远1条博士导师关系可以作历史师承，但当前导航未核关闭。不得根据邀请、访问、项目、论文合著增导师；校区不能由通讯地址推定。',
         '仅3条官方精选书目，无出版社单篇与全文核验；非完整职业、人事或全职调查。',
         '本文件为原始研究包来源独审；地域、985和消费者规范化字段及集成schema验证仍由独立整合流程执行。']}

SOURCE_SHAPES = [['value'],
 ['array', []],
 ['array', [0, 0, 0, 0, 0, 0, 0]],
 ['object',
  [['id', 0],
   ['url', 0],
   ['evidence_status', 0],
   ['retrieved_at', 0],
   ['source_type', 0],
   ['access_note', 0],
   ['supporting_urls', 2]]],
 ['object', [['id', 0], ['url', 0], ['evidence_status', 0], ['retrieved_at', 0], ['source_type', 0], ['access_note', 0]]],
 ['object',
  [['id', 0],
   ['url', 0],
   ['evidence_status', 0],
   ['retrieved_at', 0],
   ['source_type', 0],
   ['access_note', 0],
   ['web_reader_status', 0],
   ['ordinary_https_status', 0],
   ['navigation_available', 0],
   ['navigation_enabled', 0],
   ['evidence_status_label', 0]]],
 ['array', [3, 4, 4, 5, 5]],
 ['array', [0, 0]],
 ['object', [['status', 0], ['source_url', 0], ['profile_url', 0], ['native_link_target', 0], ['source_ids', 7], ['note', 0]]],
 ['object',
  [['name', 0],
   ['school_id', 0],
   ['department_id', 0],
   ['organization_id', 0],
   ['department', 0],
   ['official_url', 0],
   ['listed_role', 0]]],
 ['array', [0, 0, 0, 0]],
 ['object', [['institution', 0], ['title', 0], ['start', 0], ['end', 0]]],
 ['object',
  [['institution', 0],
   ['title', 0],
   ['start', 0],
   ['end', 0],
   ['source_id', 0],
   ['source_url', 0],
   ['evidence_status', 0],
   ['field_provenance', 11],
   ['field_status', 11],
   ['current', 0],
   ['status', 0],
   ['as_of', 0],
   ['employment_type', 0],
   ['personnel_status_verified', 0],
   ['note', 0]]],
 ['object',
  [['institution', 0],
   ['title', 0],
   ['start', 0],
   ['end', 0],
   ['source_id', 0],
   ['source_url', 0],
   ['source_navigation_enabled', 0],
   ['source_availability', 0],
   ['evidence_status', 0],
   ['field_provenance', 11],
   ['field_status', 11],
   ['current', 0],
   ['status', 0],
   ['as_of', 0],
   ['employment_type', 0],
   ['personnel_status_verified', 0],
   ['note', 0]]],
 ['array', [12, 13]],
 ['object',
  [['degree', 0], ['institution', 0], ['start', 0], ['end', 0], ['field', 0], ['degree_awarded', 0], ['degree_awarded_date', 0]]],
 ['object',
  [['degree', 0],
   ['institution', 0],
   ['start', 0],
   ['end', 0],
   ['field', 0],
   ['degree_awarded', 0],
   ['degree_awarded_date', 0],
   ['source_id', 0],
   ['source_url', 0],
   ['evidence_status', 0],
   ['field_provenance', 15],
   ['field_status', 15],
   ['event_id', 0],
   ['event_kind', 0],
   ['country', 0],
   ['region', 0],
   ['continent', 0],
   ['geography_basis', 0],
   ['geography_status', 0],
   ['include_in_education_filters', 0],
   ['note', 0]]],
 ['array', [16]],
 ['object', [['course', 0], ['level', 0], ['period', 0]]],
 ['object',
  [['course', 0],
   ['level', 0],
   ['period', 0],
   ['source_id', 0],
   ['source_url', 0],
   ['source_navigation_enabled', 0],
   ['source_availability', 0],
   ['evidence_status', 0],
   ['field_provenance', 18],
   ['field_status', 18],
   ['as_of', 0],
   ['status', 0],
   ['note', 0]]],
 ['object',
  [['course', 0],
   ['level', 0],
   ['period', 0],
   ['source_id', 0],
   ['source_url', 0],
   ['source_navigation_enabled', 0],
   ['source_availability', 0],
   ['evidence_status', 0],
   ['field_provenance', 18],
   ['field_status', 18],
   ['activity_type', 0],
   ['status', 0],
   ['note', 0]]],
 ['array', [19, 20]],
 ['object', [['name', 0], ['year', 0], ['award_date', 0], ['announcement_date', 0]]],
 ['object',
  [['name', 0],
   ['year', 0],
   ['source_id', 0],
   ['source_url', 0],
   ['source_navigation_enabled', 0],
   ['source_availability', 0],
   ['evidence_status', 0],
   ['field_provenance', 22],
   ['field_status', 22],
   ['award_date', 0],
   ['announcement_date', 0],
   ['note', 0]]],
 ['array', [23]],
 ['object', [['role', 0]]],
 ['object',
  [['role', 0],
   ['source_id', 0],
   ['source_url', 0],
   ['evidence_status', 0],
   ['field_provenance', 25],
   ['field_status', 25],
   ['note', 0]]],
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
   ['profile_status', 0],
   ['sources', 6],
   ['identity_evidence', 8],
   ['professional_field_provenance', 9],
   ['unknowns', 10],
   ['appointments', 14],
   ['education', 17],
   ['mentors', 1],
   ['committee_members', 1],
   ['publications', 1],
   ['research_fields', 1],
   ['academic_service', 1],
   ['teaching', 21],
   ['honors', 24],
   ['research_projects', 1],
   ['pending_education_candidates', 1],
   ['pending_mentor_candidates', 1],
   ['pending_appointment_candidates', 1],
   ['pending_professional_fact_candidates', 1],
   ['supervision_eligibility', 26]]],
 ['array', [3, 4]],
 ['array', [0, 0, 0]],
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
   ['profile_status', 0],
   ['sources', 28],
   ['identity_evidence', 8],
   ['professional_field_provenance', 9],
   ['unknowns', 29],
   ['appointments', 1],
   ['education', 1],
   ['mentors', 1],
   ['committee_members', 1],
   ['publications', 1],
   ['research_fields', 1],
   ['academic_service', 1],
   ['teaching', 1],
   ['honors', 1],
   ['research_projects', 1],
   ['pending_education_candidates', 1],
   ['pending_mentor_candidates', 1],
   ['pending_appointment_candidates', 1],
   ['pending_professional_fact_candidates', 1],
   ['recommended_layer', 0]]],
 ['array', [0, 0, 0, 0, 0]],
 ['array', [12]],
 ['object',
  [['degree', 0],
   ['institution', 0],
   ['start', 0],
   ['end', 0],
   ['field', 0],
   ['degree_awarded', 0],
   ['degree_awarded_date', 0],
   ['source_reported_degree_label', 0]]],
 ['object',
  [['degree', 0],
   ['institution', 0],
   ['start', 0],
   ['end', 0],
   ['field', 0],
   ['degree_awarded', 0],
   ['degree_awarded_date', 0],
   ['source_id', 0],
   ['source_url', 0],
   ['evidence_status', 0],
   ['field_provenance', 33],
   ['field_status', 33],
   ['event_id', 0],
   ['event_kind', 0],
   ['country', 0],
   ['region', 0],
   ['continent', 0],
   ['geography_basis', 0],
   ['geography_status', 0],
   ['include_in_education_filters', 0],
   ['note', 0],
   ['source_reported_degree_label', 0]]],
 ['array', [34, 34, 34]],
 ['object', [['name', 0]]],
 ['object',
  [['name', 0], ['source_id', 0], ['source_url', 0], ['evidence_status', 0], ['field_provenance', 36], ['field_status', 36]]],
 ['array', [37, 37, 37]],
 ['object', [['organization', 0], ['role', 0], ['start', 0], ['end', 0]]],
 ['object',
  [['organization', 0],
   ['role', 0],
   ['start', 0],
   ['end', 0],
   ['source_id', 0],
   ['source_url', 0],
   ['evidence_status', 0],
   ['field_provenance', 39],
   ['field_status', 39],
   ['status', 0],
   ['current', 0],
   ['note', 0]]],
 ['array', [40, 40]],
 ['object', [['name', 0], ['year', 0], ['role', 0], ['award_date', 0]]],
 ['object',
  [['name', 0],
   ['year', 0],
   ['source_id', 0],
   ['source_url', 0],
   ['evidence_status', 0],
   ['field_provenance', 42],
   ['field_status', 42],
   ['role', 0],
   ['award_date', 0],
   ['note', 0]]],
 ['array', [43]],
 ['object', [['date', 0], ['source_label', 0]]],
 ['object',
  [['date', 0],
   ['source_label', 0],
   ['source_id', 0],
   ['source_url', 0],
   ['evidence_status', 0],
   ['field_provenance', 45],
   ['field_status', 45],
   ['note', 0]]],
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
   ['profile_status', 0],
   ['sources', 28],
   ['identity_evidence', 8],
   ['professional_field_provenance', 9],
   ['unknowns', 31],
   ['appointments', 32],
   ['education', 35],
   ['mentors', 1],
   ['committee_members', 1],
   ['publications', 1],
   ['research_fields', 38],
   ['academic_service', 41],
   ['teaching', 1],
   ['honors', 44],
   ['research_projects', 1],
   ['pending_education_candidates', 1],
   ['pending_mentor_candidates', 1],
   ['pending_appointment_candidates', 1],
   ['pending_professional_fact_candidates', 1],
   ['supervision_eligibility', 26],
   ['employment_join_date_evidence', 46]]],
 ['object',
  [['institution', 0],
   ['title', 0],
   ['start', 0],
   ['end', 0],
   ['source_id', 0],
   ['source_url', 0],
   ['evidence_status', 0],
   ['field_provenance', 11],
   ['field_status', 11],
   ['current', 0],
   ['status', 0],
   ['as_of', 0],
   ['note', 0],
   ['employment_type', 0],
   ['personnel_status_verified', 0]]],
 ['array', [48]],
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
   ['field_provenance', 33],
   ['field_status', 33],
   ['country', 0],
   ['region', 0],
   ['continent', 0],
   ['geography_basis', 0],
   ['geography_status', 0],
   ['event_kind', 0],
   ['note', 0],
   ['include_in_education_filters', 0],
   ['source_reported_degree_label', 0]]],
 ['array', [50, 50, 50]],
 ['object', [['title', 0], ['year', 0], ['venue', 0], ['volume', 0], ['pages_or_article_number', 0], ['doi', 0], ['type', 0]]],
 ['object',
  [['title', 0],
   ['year', 0],
   ['venue', 0],
   ['pages_or_article_number', 0],
   ['volume', 0],
   ['doi', 0],
   ['url', 0],
   ['type', 0],
   ['source_id', 0],
   ['source_url', 0],
   ['evidence_status', 0],
   ['field_provenance', 52],
   ['field_status', 52],
   ['identity_evidence', 0],
   ['link_status', 0],
   ['individual_article_link_verified', 0],
   ['note', 0]]],
 ['array', [53]],
 ['object', [['id', 0], ['url', 0], ['evidence_status', 0], ['retrieved_at', 0], ['source_type', 0]]],
 ['array', [55, 55, 55]],
 ['object', [['status', 0], ['source_url', 0], ['profile_url', 0], ['source_ids', 7], ['note', 0]]],
 ['object',
  [['name', 0],
   ['school_id', 0],
   ['department_id', 0],
   ['organization_id', 0],
   ['department', 0],
   ['official_url', 0],
   ['listed_role', 0],
   ['roster_category', 0]]],
 ['object',
  [['name', 0],
   ['field_provenance', 36],
   ['normalization_note', 0],
   ['source_id', 0],
   ['source_url', 0],
   ['evidence_status', 0]]],
 ['array', [59, 59, 59, 59, 59]],
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
   ['appointments', 49],
   ['education', 51],
   ['mentors', 1],
   ['committee_members', 1],
   ['publications', 54],
   ['sources', 56],
   ['unknowns', 10],
   ['identity_evidence', 57],
   ['professional_field_provenance', 58],
   ['profile_status', 0],
   ['pending_education_candidates', 1],
   ['pending_mentor_candidates', 1],
   ['pending_appointment_candidates', 1],
   ['pending_professional_fact_candidates', 1],
   ['research_fields', 60]]],
 ['array', [48, 48]],
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
   ['field_provenance', 52],
   ['field_status', 52],
   ['identity_evidence', 0],
   ['link_status', 0],
   ['individual_article_link_verified', 0],
   ['note', 0]]],
 ['array', [63]],
 ['object',
  [['id', 0],
   ['url', 0],
   ['evidence_status', 0],
   ['retrieved_at', 0],
   ['source_type', 0],
   ['page_date', 0]]],
 ['array', [55, 55, 55, 65]],
 ['object', [['status', 0], ['source_url', 0], ['profile_url', 0], ['source_ids', 29], ['note', 0]]],
 ['array', [59, 59]],
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
   ['education', 51],
   ['mentors', 1],
   ['committee_members', 1],
   ['publications', 64],
   ['sources', 66],
   ['unknowns', 10],
   ['identity_evidence', 67],
   ['professional_field_provenance', 58],
   ['profile_status', 0],
   ['pending_education_candidates', 1],
   ['pending_mentor_candidates', 1],
   ['pending_appointment_candidates', 1],
   ['pending_professional_fact_candidates', 1],
   ['research_fields', 68]]],
 ['object', [['institution', 0], ['title', 0], ['start', 0], ['end', 0], ['source_reported_duty', 0]]],
 ['object',
  [['institution', 0],
   ['title', 0],
   ['start', 0],
   ['end', 0],
   ['source_id', 0],
   ['source_url', 0],
   ['evidence_status', 0],
   ['field_provenance', 70],
   ['field_status', 70],
   ['current', 0],
   ['status', 0],
   ['as_of', 0],
   ['note', 0],
   ['employment_type', 0],
   ['personnel_status_verified', 0],
   ['source_reported_duty', 0]]],
 ['array', [71, 71]],
 ['object',
  [['degree', 0],
   ['institution', 0],
   ['start', 0],
   ['end', 0],
   ['field', 0],
   ['degree_awarded', 0],
   ['degree_awarded_date', 0],
   ['source_reported_unit', 0]]],
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
   ['source_reported_unit', 0]]],
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
   ['field_provenance', 15],
   ['field_status', 15],
   ['country', 0],
   ['region', 0],
   ['continent', 0],
   ['geography_basis', 0],
   ['geography_status', 0],
   ['event_kind', 0],
   ['note', 0],
   ['include_in_education_filters', 0]]],
 ['array', [74, 74, 75, 74]],
 ['array', [59, 59, 59]],
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
   ['education', 76],
   ['mentors', 1],
   ['committee_members', 1],
   ['publications', 1],
   ['sources', 56],
   ['unknowns', 31],
   ['identity_evidence', 57],
   ['professional_field_provenance', 58],
   ['profile_status', 0],
   ['pending_education_candidates', 1],
   ['pending_mentor_candidates', 1],
   ['pending_appointment_candidates', 1],
   ['pending_professional_fact_candidates', 1],
   ['research_fields', 77]]],
 ['array', [48, 48, 48]],
 ['object',
  [['degree', 0],
   ['institution', 0],
   ['start', 0],
   ['end', 0],
   ['field', 0],
   ['degree_awarded', 0],
   ['degree_awarded_date', 0],
   ['source_reported_educational_department', 0]]],
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
   ['field_provenance', 80],
   ['field_status', 80],
   ['country', 0],
   ['region', 0],
   ['continent', 0],
   ['geography_basis', 0],
   ['geography_status', 0],
   ['event_kind', 0],
   ['note', 0],
   ['include_in_education_filters', 0],
   ['source_reported_educational_department', 0]]],
 ['array', [81, 81, 75]],
 ['array', [55, 55]],
 ['object', [['name', 0], ['school_id', 0], ['department_id', 0], ['organization_id', 0], ['listed_role', 0]]],
 ['object',
  [['institution', 0],
   ['department', 0],
   ['organization_id', 0],
   ['category', 0],
   ['source_id', 0],
   ['source_url', 0],
   ['evidence_status', 0],
   ['basis', 0],
   ['personnel_status_verified', 0],
   ['joint_appointment_verified', 0],
   ['note', 0]]],
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
   ['appointments', 79],
   ['education', 82],
   ['mentors', 1],
   ['committee_members', 1],
   ['publications', 64],
   ['sources', 83],
   ['unknowns', 29],
   ['identity_evidence', 57],
   ['professional_field_provenance', 84],
   ['profile_status', 0],
   ['pending_education_candidates', 1],
   ['pending_mentor_candidates', 1],
   ['pending_appointment_candidates', 1],
   ['pending_professional_fact_candidates', 1],
   ['research_fields', 38],
   ['sampling_affiliation', 85]]],
 ['array', [0]],
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
   ['field_provenance', 80],
   ['field_status', 80],
   ['country', 0],
   ['region', 0],
   ['continent', 0],
   ['geography_basis', 0],
   ['geography_status', 0],
   ['event_kind', 0],
   ['note', 0],
   ['include_in_education_filters', 0],
   ['source_reported_educational_department', 0],
   ['supporting_source_ids', 87]]],
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
   ['field_provenance', 15],
   ['field_status', 15],
   ['country', 0],
   ['region', 0],
   ['continent', 0],
   ['geography_basis', 0],
   ['geography_status', 0],
   ['event_kind', 0],
   ['note', 0],
   ['include_in_education_filters', 0],
   ['supporting_source_ids', 87]]],
 ['array', [88, 89, 75]],
 ['object', [['name', 0], ['type', 0], ['education_stage', 0], ['education_event_id', 0], ['start', 0], ['end', 0]]],
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
   ['field_provenance', 91],
   ['field_status', 91],
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
 ['array', [92]],
 ['array', [55, 55, 65]],
 ['object',
  [['candidate_id', 0],
   ['education_event_id', 0],
   ['candidate_field', 0],
   ['source_reported_text', 0],
   ['source_id', 0],
   ['source_url', 0],
   ['evidence_status', 0],
   ['status', 0],
   ['include_in_education_filters', 0],
   ['include_in_mentorship_graph', 0],
   ['note', 0]]],
 ['array', [95]],
 ['array', [37, 37]],
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
   ['appointments', 79],
   ['education', 90],
   ['mentors', 93],
   ['committee_members', 1],
   ['publications', 64],
   ['sources', 94],
   ['unknowns', 29],
   ['identity_evidence', 57],
   ['professional_field_provenance', 84],
   ['profile_status', 0],
   ['pending_education_candidates', 96],
   ['pending_mentor_candidates', 1],
   ['pending_appointment_candidates', 1],
   ['pending_professional_fact_candidates', 1],
   ['research_fields', 97],
   ['sampling_affiliation', 85]]],
 ['object',
  [['institution', 0],
   ['title', 0],
   ['start', 0],
   ['end', 0],
   ['source_id', 0],
   ['source_url', 0],
   ['evidence_status', 0],
   ['field_provenance', 11],
   ['field_status', 11],
   ['current', 0],
   ['status', 0],
   ['as_of', 0],
   ['note', 0],
   ['employment_type', 0],
   ['personnel_status_verified', 0],
   ['supporting_source_ids', 87]]],
 ['array', [99]],
 ['array', [81, 81, 75, 88]],
 ['object',
  [['title', 0],
   ['year', 0],
   ['venue', 0],
   ['volume', 0],
   ['pages_or_article_number', 0],
   ['doi', 0],
   ['type', 0],
   ['issue', 0]]],
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
   ['field_provenance', 102],
   ['field_status', 102],
   ['issue', 0],
   ['identity_evidence', 0],
   ['link_status', 0],
   ['individual_article_link_verified', 0],
   ['note', 0],
   ['supporting_source_ids', 87]]],
 ['array', [103]],
 ['object',
  [['status', 0], ['source_url', 0], ['profile_url', 0], ['source_ids', 29], ['note', 0], ['supplementary_identity_basis', 0]]],
 ['object', [['source_id', 0], ['source_url', 0], ['institution', 0], ['title', 0], ['start', 0], ['end_label', 0]]],
 ['object', [['source_id', 0], ['source_url', 0], ['institution', 0], ['title', 0], ['start', 0], ['end', 0]]],
 ['array', [106, 107, 106]],
 ['object',
  [['candidate_id', 0],
   ['candidate_field', 0],
   ['source_claims', 108],
   ['evidence_status', 0],
   ['status', 0],
   ['include_in_appointment_filters', 0],
   ['note', 0]]],
 ['array', [109]],
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
   ['appointments', 100],
   ['education', 101],
   ['mentors', 1],
   ['committee_members', 1],
   ['publications', 104],
   ['sources', 56],
   ['unknowns', 10],
   ['identity_evidence', 105],
   ['professional_field_provenance', 84],
   ['profile_status', 0],
   ['pending_education_candidates', 1],
   ['pending_mentor_candidates', 1],
   ['pending_appointment_candidates', 110],
   ['pending_professional_fact_candidates', 1],
   ['research_fields', 38],
   ['sampling_affiliation', 85],
   ['department_source_id', 0],
   ['department_source_url', 0],
   ['department_status', 0],
   ['roster_listed_role', 0],
   ['roster_listed_role_source_id', 0],
   ['display_affiliation_note', 0]]],
 ['object',
  [['id', 0],
   ['name', 0],
   ['type', 0],
   ['school_id', 0],
   ['parent_id', 0],
   ['source_url', 0],
   ['source_id', 0],
   ['evidence_status', 0]]],
 ['object',
  [['id', 0],
   ['name', 0],
   ['type', 0],
   ['school_id', 0],
   ['parent_id', 0],
   ['source_id', 0],
   ['source_url', 0],
   ['evidence_status', 0]]],
 ['object',
  [['id', 0],
   ['name', 0],
   ['type', 0],
   ['school_id', 0],
   ['parent_id', 0],
   ['source_id', 0],
   ['source_url', 0],
   ['evidence_status', 0],
   ['scope_note', 0]]],
 ['object', [['id', 0], ['official_name', 0], ['official_url', 0], ['source_urls', 87], ['scope_note', 0]]],
 ['array', [112]],
 ['array', [3, 4, 4, 5, 5, 4, 4]],
 ['object',
  [['education', 0],
   ['appointments', 0],
   ['mentors', 0],
   ['committee_members', 0],
   ['publications', 0],
   ['sources', 0],
   ['research_fields', 0],
   ['academic_service', 0],
   ['teaching', 0],
   ['honors', 0],
   ['research_projects', 0],
   ['pending_mentor_candidates', 0],
   ['pending_education_candidates', 0],
   ['pending_appointment_candidates', 0],
   ['pending_professional_fact_candidates', 0],
   ['people', 0],
   ['professional_people', 0],
   ['pending_people', 0],
   ['unique_sources', 0],
   ['degree_awarded_true', 0],
   ['degree_awarded_null', 0],
   ['degree_awarded_false', 0]]],
 ['array', [0, 0, 0, 0, 0, 0]],
 ['object',
  [['schema_version', 0],
   ['batch_id', 0],
   ['institution', 115],
   ['org_units', 116],
   ['campuses', 1],
   ['scope', 0],
   ['retrieved_at', 0],
   ['coverage_complete', 0],
   ['review_status', 0],
   ['sources', 117],
   ['counts', 118],
   ['limitations', 119]]],
 ['array', [112, 112]],
 ['array', [55, 55, 55, 55, 55, 55, 55, 65]],
 ['object',
  [['education', 0],
   ['appointments', 0],
   ['mentors', 0],
   ['committee_members', 0],
   ['publications', 0],
   ['sources', 0],
   ['pending_mentor_candidates', 0],
   ['pending_education_candidates', 0],
   ['pending_appointment_candidates', 0],
   ['pending_professional_fact_candidates', 0],
   ['people', 0],
   ['unique_sources', 0],
   ['degree_awarded_true', 0],
   ['degree_awarded_null', 0],
   ['degree_awarded_false', 0]]],
 ['array', [0, 0, 0, 0, 0, 0, 0, 0]],
 ['object',
  [['schema_version', 0],
   ['batch_id', 0],
   ['institution', 115],
   ['org_units', 121],
   ['campuses', 1],
   ['scope', 0],
   ['retrieved_at', 0],
   ['coverage_complete', 0],
   ['review_status', 0],
   ['sources', 122],
   ['counts', 123],
   ['limitations', 124]]],
 ['array', [113, 113, 114]],
 ['array', [55, 55, 55, 55, 55, 65, 55]],
 ['object',
  [['schema_version', 0],
   ['batch_id', 0],
   ['institution', 115],
   ['org_units', 126],
   ['campuses', 1],
   ['scope', 0],
   ['retrieved_at', 0],
   ['coverage_complete', 0],
   ['review_status', 0],
   ['sources', 127],
   ['counts', 123],
   ['limitations', 124]]]]

# Narrow reviewed compatibility overlay; all historical pins above remain intact.
REVIEWED_COMPATIBILITY_SHA256 = {'site/app.js': '5d4efe8a3c85cbca0125b950a70d7494e3d34a2e67240e6043347903965c8d4b', 'site/model.js': '9dbc155288c1ee0a93fd5d11cd8a7c63724dc0bde6b117a2f71d327e34be3fef', 'site/rosters.js': 'e4bb3c53da7a4ff3c00c1109651d66cc479c20dc265e7705e41213e3019a3502', 'site/index.html': '3b5f7afdd4ac96aaca402884976bccb33cb9a1d2a1ad27793cf7cdd82e5970bf', 'scripts/build.py': '92b6ec03d18666503a7e890e09faffe2e3ac7be61b017ec85b291c1498addacb', 'scripts/build_rosters.py': '29c5dee611bfaef3fd6afd1df9480b254652c51b1c4ce1c9568d75cb799319fe'}

BASELINE_DEPARTMENT_WORKBOOK_SHA256 = {'site/exports/bit-cs-image-perception.xlsx': '8ecc8beff095f5f5d11220ad0b50ec47695fdae46b9869cd73e08d2f665b6732', 'site/exports/bit-sie-communications.xlsx': '92cd5ee427b093fb4b9760ef9ebab38b694a331139f9d2eccf54d61f81db4803', 'site/exports/bnu-ai.xlsx': '86f12f0f36ff3872324f1973ba9576a87a46166609f9702afce219e53ab2ab46', 'site/exports/bnu-math.xlsx': 'c70465e0d1860159cc254795a94c5d24c32b95c7aacb77fbbfd4623a45a1f3f1', 'site/exports/buaa-cs.xlsx': '0f33d60bb4e9c874de291915fe7f2df0038bb3583383a3f4cfc74e4343842467', 'site/exports/buaa-physics-applied.xlsx': '147b53eea044df39df75298e78bb35da3e023773641d721059c61971c2f73315', 'site/exports/buaa-physics-department.xlsx': '73cc282a3510574a41813c3fafd354658d1d9bc7a52f368a2fb342160585a9db', 'site/exports/buaa-physics-nuclear.xlsx': 'fc5ca475c896cde5528aab0c59ef682398c955e804e390f81e7cd794b4e0eca6', 'site/exports/cau-biology-plant-science.xlsx': '619ad8d84b8686eb1d1c9d21a7b3e8c6f8f64476a64443c63adf3f6bd15d5b31', 'site/exports/cau-ciee-computer.xlsx': '54b8579a0593a744dedf82dcc32c9d8e112dd402689e4a44d049abc11e30f4cf', 'site/exports/cau-science-math.xlsx': 'c03fc7faa75c7bb128f43effa033b3a55512b0fe5a4303d98d708677899834c4', 'site/exports/cqu-cs.xlsx': 'e67dd852d2efb14019ee1fed04ba3c2250da2b5bb5f22b61e0e8e83a853c237c', 'site/exports/cqu-mathematics-statistics.xlsx': '11e246f87cff7aef8d529706b854e39cb1a4a338570ccfe2d70dc02e519447e0', 'site/exports/csu-cse.xlsx': '3fc12ea5379b0c669a0b6855c513c8fb46cb0f432d8a882a220e4fe2ce20d44d', 'site/exports/csu-math-applied.xlsx': '7484e1fc254fa9987bc57bdb292e1efc5ecdf318e53b84e06d295792bd8f6847', 'site/exports/dlut-cs-software-theory.xlsx': '5dbde15b50dab984d986ec3493d78ad5c7d27d8fcdf0c30658d7d342f9aad06d', 'site/exports/dlut-math-institute.xlsx': '1625969239b59a8244f727a522eb83e957cacb64b3e4d465704a4816c496a5a3', 'site/exports/ecnu-geography.xlsx': 'bfc7480dde7dfa3ad263093384eb73c828e2359e4de331484aa0bdf2ebad4c0e', 'site/exports/ecnu-math-applied.xlsx': '4d657056812b4a89a8ce7c4e4b3a228c3a94eb5f29e9ed9d7fe474ffba2994cb', 'site/exports/ecnu-math-pure.xlsx': 'b35e580a30dd29f4a180843d078fc23dfdbb6229daebc40cdc97bf6e0f6d27a7', 'site/exports/ecnu-sei.xlsx': '73529cf6469491fb6fa8793ab5f0c54327cfa3617f671e3aaa5ba449e5212c1c', 'site/exports/fdu-icmne.xlsx': 'b6849ef1b1be24cca002bc0a0f915b6a8d4434ff8c09556d7b4568910c4d820e', 'site/exports/fdu-math-applied.xlsx': '8bed2e4e437b8426ddc39309946adaf02c3829b73d6e29f05d1a7ef176a0a23d', 'site/exports/fdu-math-probability-statistics-actuarial.xlsx': '193ff4457d1f269d3b7e9dce9a35dbf2c0195b3477f86b04aef633ed9f9b8e22', 'site/exports/hit-computing.xlsx': '958fbc68d19dcf3690a1087ade9da24287a56383536f06e684caad3cdc9fd172', 'site/exports/hit-seie.xlsx': '543c05288964285cc03152107b0682c4094c7ac14f5cdef2f80b8319ba0c0166', 'site/exports/hit-shenzhen-computer.xlsx': '58b222b67d96818aa52f16d201a8449bef5bb36e2302cf2bd5a68e9ae1aa8d53', 'site/exports/hit-shenzhen-ic.xlsx': '3744f412bbd5e7e21969cdb953040409d6720e385153fd1b7f1a3e43432c3b8f', 'site/exports/hit-shenzhen-robotics.xlsx': 'ab6d347fa8b292fb66cec686ad16dc974af9188acc435e6d2f8856009d70797b', 'site/exports/hit-weihai-information.xlsx': '7cb591f80874dfb4fe3ccce0259f28cd0c9a0c6fde49c1ab30d63eb6c328433d', 'site/exports/hit-weihai-materials.xlsx': '54d21c6da24008000fb4191e8bf2c4d5adc811eed95c33982669cc3696f5743a', 'site/exports/hnu-chemistry-department.xlsx': 'd868060f83ebce45609cd1446ceafcce5c4892478dc9a926dfc0afb0aeb1e040', 'site/exports/hnu-cs-communication-engineering.xlsx': 'e01ae98178c1caf20c1e18740e02db76998554dea745fc646c9e70939827d6b7', 'site/exports/hnu-cs-computer-engineering.xlsx': '7bb5394feca7c1986e877cfdddf7483b88a358d8c93ad35dd847199a03271c9f', 'site/exports/hnu-cs-software-engineering.xlsx': '4fdffd5a5f323dda2f212948be7a716d97581aa30820b467e45c49805e42a6c4', 'site/exports/hnu-math-basic.xlsx': '8d45b2063647a144c74c7f8e7d5ec33e848a5787e24a8dc8f26408501120a95c', 'site/exports/hust-cs-storage.xlsx': 'be5028ada1801939f2f53daa010249bc031a9a6a43f2555aee0aa7c5aac7a39d', 'site/exports/hust-math-center.xlsx': '958cd31af3a503ea4187fe4f6bfd42131be4d57d453f7fcbe5a02bdeb27533b5', 'site/exports/hust-math-interdisciplinary.xlsx': 'ec1f1fa56ac08e000b7808f0297d6814dbb9f744a4c42003da2b6c3fba39524f', 'site/exports/jlu-cs.xlsx': '4546f557b871c5e584dfdaac60affa8551bfa545cca0799018453e84e73a13a0', 'site/exports/jlu-math-applied.xlsx': '14536830ff485834b0e45603626ba94a72d6ed471cbc0162491479fb64dafa89', 'site/exports/jlu-math-computational.xlsx': '81d7218696de8a5dbbe215ea7a4e37ad9e166db36a2ad41093ada4d9d0bfc46f', 'site/exports/jlu-math-statistics.xlsx': '610cb4d6748821fd9e0f8b31dbfda3e04adea16e10c7ea0961a768f7cd9261b4', 'site/exports/lzu-basic-mathematics.xlsx': '6dc90c17aac81334fe036dceed021942ea587480215450eb04ed61cab8eba029', 'site/exports/lzu-law.xlsx': '8d62ec02ae35b737b04feb281ed89e0cc6cdacfcc83ae9b6f3eca2f891db294f', 'site/exports/muc-ise-cs.xlsx': 'b7642d209c8ada88bd470c37fe712191233031b8765402b6fd94400f039c305e', 'site/exports/muc-science-math.xlsx': '22ef1e1930c2c49eed629dceb1bbf0a12fd84e880494eb582ab3acf7fd628279', 'site/exports/neu-cse-communication-electronics.xlsx': 'bf487e818fd5e703b46b8f334baa28dea7b7790bd600b3a74a04f86c471164ae', 'site/exports/neu-cse-cs.xlsx': '6a9dfc9331ac2fc757122aa3d3bcff44d1736c91dcd32906bcbef0dd1c056079', 'site/exports/neu-mechanical-vehicle-engineering.xlsx': '51f430c8c53d29bdde2ef6f552c9ce74781440650e90a4009f61c0b0e45d1b1f', 'site/exports/neu-science-math.xlsx': '12f9dbeaf2b25a09049b5aa3a3489e9bce73006f7bab618d2de0e7489542f796', 'site/exports/nju-astronomy-space-science.xlsx': '477a5f1ca3a470e9fbe0392903c40dffc5adac2d1e16154b8ed9ed124a5d873a', 'site/exports/nju-cs.xlsx': 'e75ef1d05b07d7c34effe7abbacce42d088eff06a18fc6966366fc1c88d54785', 'site/exports/nju-math.xlsx': '221e7ff8f76efdde2fd3542aa979d75651dfd972655d8119a6a1ca6a8e071c58', 'site/exports/nju-sme.xlsx': '1a4af1c71eb2aaf3a18081db8653aee42c0879605eb5f0ed04b746cd007edf94', 'site/exports/nku-cs.xlsx': '129463d6106d689e4a416d343ed11d089dd9b98584178de4635c3a08a2382771', 'site/exports/nku-cyber.xlsx': '920978e9a9d5e45a57915c2c8ccc739ca5e928aad3f97df899f494df62e53d75', 'site/exports/nku-stat.xlsx': '227e4c232fc5efc3a5e6e087ed3282bdd56c9b20738ce3102dd715b95d75e4aa', 'site/exports/nudt-aerospace.xlsx': '4d422f6152bc4ef75d334a719e60a6eaff8bbc5903dc582c363e095814a6f256', 'site/exports/nudt-electronic-science.xlsx': '3260867dd2d0b5239a05c60c3167240c92ee65ce56b6935d7aaf9e56e0fc9c84', 'site/exports/nudt-electronics.xlsx': 'ad7a5b1686c3da6e73d2f680c41a9ed26fdc99b2d8847175b98012a37c70e92f', 'site/exports/nudt-foreign-languages.xlsx': '70f192adf64fe607676d7e3b78e9fff5a5674c1ffaea2032699957f13e4af4a5', 'site/exports/nudt-intelligence.xlsx': '9225f49a9da23e9a168158a4d02aaa0a98e6fc06aab75f02258dde270725bd80', 'site/exports/nudt-systems.xlsx': '417c343ecbc9917662df640ab2dffb3ec16b38a3f20c3618f009068c81c8bfb1', 'site/exports/nwpu-cs-computer-science-software.xlsx': '15f646eb84972804a67d0e7f2b763bc252822ce2f01a3bf7aaad89cf1511ac4d', 'site/exports/nwpu-mathematical-sciences.xlsx': 'c36069333720ebb5c0965eb0f27c37eb9b957c396010bc3dabf095ec7d4dba61', 'site/exports/nwsuaf-agronomy-agronomy-department.xlsx': '38ab9f806f741fc54bca7f42cd149662681de1573710e33385ccb31ab58a1aad', 'site/exports/nwsuaf-cie-cs.xlsx': '5a0a8e7b0dbc3dc0563bc8a131d0d0f7908c94baae45167d69f044ecdaf7db1c', 'site/exports/nwsuaf-cie-data.xlsx': 'c008f08177b0577eb59e985fe06ed84b756ebf969229af3d6d538e3a3e056bf8', 'site/exports/ouc-ise-cs.xlsx': 'bef4f4e5a5257b44251746e8e15162bd646857d088f6e294c8eeb4d1b203633a', 'site/exports/ouc-math-department.xlsx': 'a8b97ffaf5f340533da5a8d12b133a76a5b54c676dc8637a2459662dd7efe272', 'site/exports/pku-ic-microelectronics.xlsx': '7291ebe2cc688be153704102e39d3864df91bac5ad97259d16bd73a656554f42', 'site/exports/ruc-gsai.xlsx': '6b1429699da46c5f4fee3585c11721d2bd4023fd5d1fc063b533f690c5760b65', 'site/exports/ruc-info-eim.xlsx': '2ac362a53b5fbb1ff7580f04bba9d2c6fcec00a31540cfcde5cbe41c1c0c0119', 'site/exports/scu-chemical-engineering.xlsx': '60f80f78f8ecfa134b4957c0d2d04a16c78f2348a2c9ffb612784adcfd625186', 'site/exports/scu-cs.xlsx': '3cc913079af73ad9b667b2a7e248c9b693bee07aa6ccc49b954f96a93cd50d5d', 'site/exports/scu-materials-science-engineering.xlsx': '77501002ebe4b12fe264a9a47249b1f60e3456571442b195d567eaacd3f001c8', 'site/exports/scut-cs.xlsx': '6fc48b36e796167f01e0326b06812c3d7507e10a9585b36b18fabdff9009bdf0', 'site/exports/scut-math.xlsx': '4c461609c2f0e78b8be8cc0f3a020387c67a8f52a787245ef678df126db5f5ee', 'site/exports/sdu-cs.xlsx': '15065fcc41a9a0f5413cb6bf36a83ddb7b6dd8ef3b42e54a488929feb3c2653e', 'site/exports/sdu-math.xlsx': 'e9f056cb5a86693f16de85a93c3d50f3195140c34c87f75fa6e4580fd2232202', 'site/exports/seu-computing-joint-roster.xlsx': '48d5b9a81a28296fe5d265edcd4fc369d1c970fcaffd0c7df91b781f79d528fe', 'site/exports/seu-cs.xlsx': 'abe27d1aa51acf1275aa560931da66d82ffe22fb451f62dd8c46168b07c2d465', 'site/exports/seu-math-computational.xlsx': '52f2403373aba5dee463834813b9e7f8bd497c3760e6688e5de592964e869751', 'site/exports/seu-math-systems.xlsx': 'f54dc7088b8341fce7a57f31a6dc9b4c75bb49cb3bae428ef5a207552024f42f', 'site/exports/sjtu-ic-chipdesign.xlsx': 'b3fa394373ae7fcb6c84142d81637c22e5f8dfaa0d4f1df97c93163cecc89a11', 'site/exports/sysu-history-zhuhai.xlsx': 'dffc21bfb97d1ac8d1817c172370f6523b4a90535aabdc16cbd246f0e28cd115', 'site/exports/sysu-math-department.xlsx': 'ecc826f6e90603d05c17f6e7ed167f97974db04fbe3b175ca3e6ffbcbdc33111', 'site/exports/sysu-math.xlsx': '3edf48eda175bb96169ef9cd3d0960c5195ba3537d04431843b22e7f27cd2144', 'site/exports/sysu-mathzh.xlsx': 'cdebb1c4bdb74a374c17d7c0e7f68eb5fc596833d450098b28a9ccb64ffb37d9', 'site/exports/thu-ee-communications.xlsx': '8701a586cde1d10eec194b8eb20fd648f12af8620f1d6c0c9828ab00a88d36e9', 'site/exports/tju-math.xlsx': '399936224a993c995cfad6cbb80a6dc74486f21621fe5e6ae473aee4d939a20e', 'site/exports/tju-sme.xlsx': '4f963ba2740c54d0406764f9384a03733e5ecc406294c633290fb333fa6144c0', 'site/exports/tongji-civil-building-engineering.xlsx': '448632503151618b790da7adeb660b90b2fbd6bfaa8fa1e2d14d4f500e06b63c', 'site/exports/tongji-cs.xlsx': '99bd75bb420f58781e1b8a389e7d8ff72f5ccb97c4a77f09ed0af96da50c26d5', 'site/exports/tongji-math-teaching.xlsx': '84e40719460679f31b96cdda3cff6da20c17a10448c3e9ac89f92d5c4e351a3b', 'site/exports/uestc-aihss.xlsx': '3a4fabc60237a4ff3e854f764d4c4bbe92fe55c88977f7c7ce847b0d22838952', 'site/exports/uestc-applied-math-center.xlsx': '0d31c20c27bcf996526e01c573cf396f11f1fdfd3a888be34d8033d042148c31', 'site/exports/ustc-ic.xlsx': 'bba52cc29f384a3ccc4e6b582ab4cdf1e7be215e4b6059926e1f6809cfa0be7e', 'site/exports/ustc-math.xlsx': '60edd4e8f47842ca1ce0e5e64f874d9365bffb51e71a92c641f4b4969e811297', 'site/exports/whu-eis.xlsx': 'df7dfc47d4307136d341cbae96f731302c4414cd5e077b29dcb32968e63bf423', 'site/exports/whu-math-stat.xlsx': '4d45cfd5fd92a1f18a6d89cbe9112bd9da8c9faac6696c025e1d81b297725818', 'site/exports/xjtu-math-department.xlsx': '2bef8af7e2ac74764b31b651542b4f2547962c61d0a2ac95ee6530c45a2fc7f1', 'site/exports/xjtu-se.xlsx': '74dda6adf6cb6a0ae0a376b13ca98bcd6fc7c06dbe72037172b16df698da94d2', 'site/exports/xmu-informatics-cs.xlsx': '4975c6535af5ec76a4c5cf9ad40e78627739cabf40f422db69a443b09152b62a', 'site/exports/xmu-math-applied.xlsx': '080164257599a45cc2be8eb901fda292c3d9a233c10facd3319a4bb894379b55', 'site/exports/zju-ic-manufacturing.xlsx': 'e683c104495e43aec93846c5d8767bd1040e0a135592c1003526028ed03262f9'}

NODE_CONSUMERS = "\nimport fs from 'node:fs';\nimport {pathToFileURL} from 'node:url';\nconst input=JSON.parse(fs.readFileSync(0,'utf8')), root=input.root;\nconst model=await import(pathToFileURL(root+'/site/model.js'));\nconst roster=await import(pathToFileURL(root+'/site/rosters.js'));\nconst db=input.atlas, r=input.rosters, before=JSON.stringify([db,r]);\nconst people=new Map([...db.people,...db.pending_people].map(p=>[p.person_id,p]));\nconst scoped={...db,rosters:r}, out={people:{},rosters:{},schoolStats:{},schoolPages:{}};\nfor(const id of input.ids){\n const p=people.get(id),e=r.entries.find(e=>e.id===p.roster_entry_id),main={innerHTML:''};\n if(!p||!e)throw Error('Missing release record '+id);\n roster.renderRosters(scoped,main,e.id,p.school_id);\n out.rosters[id]={matched:roster.rosterIdentityMatched(scoped,e),status:roster.rosterStatusLabel(scoped,e),html:main.innerHTML};\n out.people[id]={\n  stages:Object.fromEntries(['bachelor','master','doctor'].map(s=>[s,model.stages(p,s).map(e=>e.event_id)])),\n  ug:Object.fromEntries(['yes','no','unknown','not_recorded'].map(v=>[v,model.matches(p,{ug:v},db.org_units)])),\n  doctorate:Object.fromEntries(['mainland','hmt','overseas','unknown','not_recorded'].map(v=>[v,model.matches(p,{doctor:v},db.org_units)])),\n  officialUrl:model.officialProfileUrl(p),\n  mentors:p.mentors.map(m=>({name:m.name,url:model.mentorOfficialUrl(m),route:model.mentorProfileRoute(m,db.people),events:model.mentorEvents(p,m).map(e=>e.event_id)})),\n  candidates:(p.pending_mentor_candidates||[]).map(m=>({name:m.name,url:model.mentorOfficialUrl(m),route:model.mentorProfileRoute(m,db.people)})),\n  labels:p.education.map(model.educationStageLabel)\n };\n}\nfor(const school of input.schools)out.schoolStats[school]=model.schoolStats(scoped,school);\nconst appAtlas=structuredClone(db),appRosters=structuredClone(r);\nappAtlas.build_id=appRosters.build_id='rotation003-wave1-in-memory-test';\nappAtlas.exports=input.exports;\nout.directories={};\nconst nodes=new Map(),listeners={};\nconst node=key=>{\n if(!nodes.has(key))nodes.set(key,{innerHTML:'',textContent:'',value:'',style:{},dataset:{height:'320'},clientWidth:960,addEventListener(){},click(){this.onclick?.()},querySelector(selector){return node(selector)},scrollIntoView(){}});\n return nodes.get(key);\n};\nglobalThis.document={querySelector:node,querySelectorAll:()=>[],getElementById:id=>node('#'+id)};\nglobalThis.location={hash:'#/'};\nglobalThis.window={scrollTo(){},addEventListener(name,handler){listeners[name]=handler}};\nglobalThis.fetch=async path=>{\n if(!/^(atlas|rosters)\\.json(?:\\?|$)/.test(String(path)))throw Error('External fetch prohibited: '+path);\n return {ok:true,json:async()=>structuredClone(String(path).startsWith('atlas.json')?appAtlas:appRosters)};\n};\nawait import(pathToFileURL(root+'/site/app.js'));\nif(!listeners.hashchange)throw Error('Actual app failed to initialize: '+node('#main').innerHTML);\nconst navigate=hash=>{for(const n of nodes.values())n.innerHTML='';location.hash=hash;listeners.hashchange()};\nfor(const id of input.ids){\n const p=people.get(id),row=out.people[id];\n navigate('#/person/'+encodeURIComponent(id));\n row.profileMain=node('#main').innerHTML;row.profileContent=node('#profile-content').innerHTML;\n if(p.detail_count_eligible){\n  navigate('#/person/'+encodeURIComponent(id)+'/lineage');\n  row.lineage=node('#profile-content').innerHTML;row.graph=node('#mind-stage').innerHTML;\n }\n}\nfor(const school of input.schools){\n navigate('#/school/'+school);out.schoolPages[school]=node('#main').innerHTML;\n navigate('#/people?school='+school);out.directories[school]=node('#results').innerHTML;\n}\nout.unchanged=JSON.stringify([db,r])===before;\nprocess.stdout.write(JSON.stringify(out));\n"

# Only these exact approved locator leaves left the public view; every retained scalar is still mutated.
PUBLIC_METADATA_REMOVED_LOCATOR_LEAF_COUNTS = {'cqu-chenke': 0,
 'cqu-chenrenwei': 0,
 'cqu-chenxiaomeng': 0,
 'xmu-chenhuang-economics': 3,
 'xmu-chenwanyi': 4,
 'xmu-dingchangfa': 3,
 'bit-chentian': 2,
 'bit-chenyuhui': 3,
 'bit-daiyunyun': 3}

def project_source_shape(value, node_id):
    node = SOURCE_SHAPES[node_id]
    if node[0] == 'value': return value
    if node[0] == 'object':
        assert isinstance(value, dict), 'Reviewed object changed type'
        return {key: project_source_shape(value[key], child) for key, child in node[1]}
    assert isinstance(value, list) and len(value) == len(node[1]), 'Reviewed collection changed length/type'
    return [project_source_shape(item, child) for item, child in zip(value, node[1])]


def source_view(person):
    p = copy.deepcopy(person)
    p['profile_status'] = p['source_profile_status']
    for event in p['education']:
        for key in ('region', 'institution_985', 'event_kind'):
            if 'source_' + key in event: event[key] = event['source_' + key]
    for mentor in p['mentors']:
        for key in ('employment_status', 'official_url'):
            if 'source_' + key in mentor: mentor[key] = mentor['source_' + key]
    for teaching in p.get('teaching', []):
        if 'source_note' in teaching: teaching['note'] = teaching['source_note']
    return p


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
                else: check(child, path + '/' + key)
        elif isinstance(value, list):
            for index, child in enumerate(value): check(child, path + '/' + str(index))
    check(person)
    for mentor in person['mentors']:
        bound = mentor.get('education_event_ids', [mentor.get('education_event_id')])
        assert len(bound) == len(set(bound)) and all(e in events for e in bound), 'Main mentor must bind main education only'
    for candidate in person.get('pending_education_candidates', []):
        assert candidate.get('include_in_education_filters') is False
        assert candidate.get('include_in_mentorship_graph') is False
    for candidate in person.get('pending_appointment_candidates', []):
        assert candidate.get('include_in_appointment_filters') is False
    return True


class Rotation003Wave1ReleaseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.d = release25_view(json.loads((ROOT/'data/atlas.json').read_text()), 'data/atlas.json')
        cls.r = release25_view(json.loads((ROOT/'data/rosters.json').read_text()), 'data/rosters.json')
        cls.q = release25_view(json.loads((ROOT/'progress/work-queue.json').read_text()), 'progress/work-queue.json')
        cls.ps = {p['person_id']:p for p in cls.d['people'] + cls.d['pending_people']}
        cls.new = [cls.ps[pid] for pid in SOURCE_FINGERPRINTS]
        cls.entries = {e['source_person_id']:e for e in cls.r['entries'] if e.get('source_person_id') in SOURCE_FINGERPRINTS}
        cls.js = None

    @classmethod
    def consumers(cls, atlas=None):
        if atlas is None and cls.js is not None: return cls.js
        run = subprocess.run(['node','--input-type=module','-e',NODE_CONSUMERS],
            input=json.dumps({'root':str(ROOT),'atlas':atlas or cls.d,'rosters':cls.r,'ids':list(SOURCE_FINGERPRINTS),
                             'schools':list(EXPECTED_IDS),'exports':build.department_exports(cls.d)}),
            text=True,capture_output=True,timeout=60,cwd=ROOT)
        if run.returncode: raise AssertionError('Actual consumers failed:\n'+run.stderr)
        output = json.loads(run.stdout)
        if atlas is None: cls.js = output
        return output

    def tables(self, pid, person=None):
        person = person or self.ps[pid]
        before = copy.deepcopy(person)
        with mock.patch.object(build,'Workbook',side_effect=AssertionError('Build writes prohibited')):
            result = dict(build.department_tables([person],self.d['updated_at'],self.d['institutions']))
        self.assertEqual(person,before)
        return result

    def test_01_every_original_source_leaf_shape_and_array_survives(self):
        self.assertEqual(len(SOURCE_FINGERPRINTS),9)
        for pid,(shape,digest) in SOURCE_FINGERPRINTS.items():
            self.assertEqual(object_sha(project_source_shape(source_view(self.ps[pid]),shape)),digest,pid)

    def test_02_all_six_original_org_objects_survive(self):
        orgs = {o['id']:o for o in self.d['org_units']}
        for oid,(shape,digest) in ORG_FINGERPRINTS.items():
            self.assertEqual(object_sha(project_source_shape(orgs[oid],shape)),digest,oid)

    def test_03_all_baseline_atlas_objects_remain_unchanged(self):
        for key,(n,digest) in BASELINE_ATLAS_PREFIXES.items():
            self.assertEqual(object_sha(self.d[key][:n]),digest,key)
        for key,digest in BASELINE_ATLAS_UNCHANGED.items(): self.assertEqual(object_sha(self.d[key]),digest,key)

    def test_04_all_baseline_roster_objects_remain_unchanged(self):
        for key,(n,digest) in BASELINE_ROSTER_PREFIXES.items():
            self.assertEqual(object_sha(self.r[key][:n]),digest,key)
        for key,digest in BASELINE_ROSTER_UNCHANGED.items(): self.assertEqual(object_sha(self.r[key]),digest,key)

    def test_05_exact_scope_and_original_queue_unchanged(self):
        n,digest = BASELINE_QUEUE_PREFIX
        self.assertEqual(n,219); self.assertEqual(object_sha(self.q['tasks'][:n]),digest)
        self.assertEqual(len(self.q['tasks']),222)
        self.assertEqual([t['institution_id'] for t in self.q['tasks'][n:]],['cqu','xmu','bit'])
        for t in self.q['tasks'][n:]:
            self.assertEqual(t['status'],'partial'); self.assertFalse(t['scope']['university_complete'])
        self.assertEqual([p['person_id'] for p in self.d['people'][547:]],PROFESSIONAL_IDS)
        self.assertEqual([p['person_id'] for p in self.d['pending_people'][83:]],PENDING_IDS)
        self.assertEqual([e['source_person_id'] for e in self.r['entries'][1712:]],list(SOURCE_FINGERPRINTS))
        self.assertEqual((len(self.d['people']),len(self.d['pending_people']),len(self.d['institutions']),len(self.d['org_units'])),(555,84,39,229))
        self.assertEqual((len(self.r['entries']),len(self.r['source_observations'])),(1721,1759))
        self.assertEqual(len(build.department_exports(self.d)),111)
        self.assertEqual({o['id'] for o in self.d['org_units'][223:]},set(ORG_FINGERPRINTS))

    def test_06_all_original_counts_and_award_tristates_preserved(self):
        for p in self.new:
            self.assertEqual({k:len(p.get(k,[])) for k in EXPECTED_COUNTS[p['person_id']]},EXPECTED_COUNTS[p['person_id']],p['person_id'])
        self.assertEqual(Counter(e['degree_awarded'] for p in self.new for e in p['education']),{True:2,False:6,None:16})
        self.assertEqual(sum(len(p['mentors']) for p in self.new),1)
        self.assertEqual(sum(len(p['publications']) for p in self.new),5)

    def test_07_dates_precisions_and_source_event_kinds_remain_exact(self):
        for p in self.new:
            source = source_view(p)
            expected = EXPECTED_EDUCATION[p['person_id']]
            self.assertEqual([{k:e.get(k) for k in row} for e,row in zip(source['education'],expected)],expected)
            for raw,e in zip(source['education'],p['education']):
                self.assertEqual(e['event_kind'],'degree' if raw['degree_awarded'] is True else raw['event_kind'])
                if e['degree_awarded'] is True:
                    self.assertEqual(e['degree_award_source_id'],e['field_provenance']['degree_awarded'])
                    self.assertRegex(e['degree_awarded_date'],r'^\d{4}$')

    def test_08_every_source_reference_and_candidate_boundary_closed(self):
        for p in self.new: self.assertTrue(assert_source_closure(p),p['person_id'])

    def test_09_only_two_confirmed_awards_enter_actual_filters(self):
        js = self.consumers()
        for pid in SOURCE_FINGERPRINTS:
            row = js['people'][pid]
            expected = {'bachelor':[],'master':[],'doctor':[]}
            if pid=='bit-chenyuhui':
                expected['bachelor']=['bit-chenyuhui-education-1']; expected['doctor']=['bit-chenyuhui-education-2']
            self.assertEqual(row['stages'],expected,pid)
            self.assertEqual(row['ug']['yes'],pid=='bit-chenyuhui')
            self.assertEqual(row['ug']['not_recorded'],pid!='bit-chenyuhui')
            self.assertEqual(row['doctorate']['mainland'],pid=='bit-chenyuhui')
            self.assertEqual(row['doctorate']['not_recorded'],pid!='bit-chenyuhui')
            self.assertFalse(row['doctorate']['overseas'])

    def test_10_renwei_remains_original_second_pending_selection(self):
        p = self.ps['cqu-chenrenwei']; e = self.entries[p['person_id']]
        self.assertEqual(EXPECTED_IDS['cqu'][1],p['person_id'])
        self.assertEqual(p['profile_status'],'profile_details_pending'); self.assertFalse(p['detail_count_eligible'])
        self.assertFalse(e.get('verified_person_id'))
        for field in ['education','appointments','mentors','publications','research_fields','teaching','honors','academic_service']:
            self.assertEqual(p[field],[])
        html = self.consumers()['people'][p['person_id']]
        self.assertEqual(html['profileContent'],'')
        self.assertIn('资料待完善',html['profileMain']); self.assertIn('尚未建立人物档案',html['profileMain'])
        self.assertNotIn('#/person/cqu-chenrenwei"',self.consumers()['directories']['cqu'])
        self.assertEqual(self.consumers()['rosters'][p['person_id']]['status'],'身份已匹配，资料待完善')

    def test_11_chenke_unknown_degree_label_and_no_year_inference(self):
        p = self.ps['cqu-chenke']; e = p['education'][0]
        for key in ['degree','degree_awarded','degree_awarded_date','start','end','field']: self.assertIsNone(e[key])
        self.assertFalse(e['include_in_education_filters']); self.assertEqual(e['event_kind'],'education_level_unknown')
        self.assertEqual(self.consumers()['people'][p['person_id']]['labels'],['学习经历（层次与授位未核实）'])
        self.assertIn('学习经历（层次与授位未核实）',self.consumers()['people'][p['person_id']]['profileContent'])
        self.assertIsNone(p['listed_role']); self.assertFalse(p['appointments'][1]['current'])
        self.assertEqual(p['appointments'][1]['as_of'],'2025-09-19')

    def test_12_cached_sources_never_become_clickable_in_actual_profile(self):
        from html import escape
        p = self.ps['cqu-chenke']; html = self.consumers()['people'][p['person_id']]['profileContent']
        inactive = [s for s in p['sources'] if s.get('navigation_enabled') is False]
        self.assertEqual(len(inactive),2)
        for s in inactive:
            self.assertEqual(s['evidence_status'],'official_cached_body_read_direct_404')
            self.assertEqual(s['ordinary_https_status'],404)
            self.assertIn(escape(s['url']),html)
            self.assertNotIn('href="'+escape(s['url'])+'"',html)
        self.assertIn('缓存',html); self.assertIn('404',html)
        for s in p['sources']:
            if s.get('navigation_enabled') is not False: self.assertIn('href="'+escape(s['url'])+'"',html)

    def test_13_teaching_alias_keeps_source_note_and_verbatim_date_not_education(self):
        p = self.ps['cqu-chenke']; html = self.consumers()['people'][p['person_id']]['profileContent']
        self.assertEqual(len(p['teaching']),2); self.assertEqual(len(p['education']),1)
        self.assertEqual(p['teaching'][1]['period'],'2025-09-18')
        self.assertIn('2025-09-18',p['teaching'][1]['note']); self.assertIn('2025-09-18',html)
        self.assertIn('不是本人求学学历',html)
        self.assertEqual(p['honors'][0]['year'],2020)
        self.assertEqual(p['honors'][0]['announcement_date'],'2021-03-31'); self.assertIsNone(p['honors'][0]['award_date'])
        self.assertEqual(p['mentors'],[])
        for t in p['teaching']:
            self.assertFalse(t['source_navigation_enabled']); self.assertIn(t['source_note'],t['note'])

    def test_14_chenxiaomeng_service_end_and_hire_promotion_separation(self):
        p = self.ps['cqu-chenxiaomeng']
        self.assertEqual(len(p['academic_service']),2)
        for row in p['academic_service']:
            self.assertEqual(row['end'],'2026-06'); self.assertFalse(row['current'])
        for e in p['education']: self.assertIsNone(e['degree_awarded'])
        self.assertEqual(p['mentors'],[])

    def test_15_xmu_labels_visits_and_study_are_not_awards(self):
        for pid in EXPECTED_IDS['xmu']:
            p=self.ps[pid]
            self.assertTrue(all(e['degree_awarded'] is not True for e in p['education']))
            self.assertEqual(p['mentors'],[])
        p=self.ps['xmu-chenwanyi']; self.assertEqual([e['end'] for e in p['education']],['2011','2011','2018'])
        self.assertTrue(all(e['start'] is None for e in p['education']))
        ding=self.ps['xmu-dingchangfa']
        self.assertEqual([e['degree_awarded'] for e in ding['education']],[None,None,False,False])
        self.assertEqual(self.consumers()['people'][ding['person_id']]['labels'][-2:],['学术交流或进修','学术访问（非学位）'])

    def test_16_chenyuhui_reverse_interval_and_year_awards_not_repaired(self):
        p=self.ps['bit-chenyuhui']; e=p['education'][1]; c=p['pending_education_candidates'][0]
        self.assertIsNone(e['start']); self.assertIsNone(e['end']); self.assertEqual(e['degree_awarded_date'],'2013')
        self.assertEqual(c['source_reported_text'],'2013-2008，中国科学院物理研究所，博士，导师：李志远教授')
        self.assertFalse(c['include_in_education_filters']); self.assertFalse(c['include_in_mentorship_graph'])
        rows=self.tables(p['person_id'])['经历']; self.assertIsNone(rows[2][4]); self.assertIsNone(rows[2][5])
        self.assertEqual(rows[2][12],'2013')
        html=self.consumers()['people'][p['person_id']]['profileContent']
        self.assertIn('授位日期：2008 ',html); self.assertIn('授位日期：2013 ',html)
        self.assertNotIn('2013-2008',html)

    def test_17_one_doctoral_edge_without_current_navigation(self):
        p=self.ps['bit-chenyuhui']; m=p['mentors'][0]; row=self.consumers()['people'][p['person_id']]
        self.assertEqual(m['name'],'李志远'); self.assertEqual(m['type'],'doctoral_supervisor')
        self.assertIsNone(m['start']); self.assertIsNone(m['end']); self.assertIsNone(m['person_id'])
        self.assertFalse(m['navigation_verified']); self.assertEqual(row['mentors'][0]['events'],['bit-chenyuhui-education-2'])
        self.assertEqual(row['mentors'][0]['url'],''); self.assertEqual(row['mentors'][0]['route'],'')
        self.assertIn('李志远',row['graph']); self.assertNotIn('查看导师个人主页',row['lineage'])
        self.assertNotIn('张向东',row['graph']); self.assertEqual(self.tables(p['person_id'])['导师'][1][7],'')

    def test_18_dai_employment_is_not_physics_sampling_or_double_appointment(self):
        p=self.ps['bit-daiyunyun']; row=self.consumers()['people'][p['person_id']]
        self.assertEqual(p['department_id'],'bit-frontier-interdisciplinary-institute')
        self.assertEqual(p['sampling_affiliation']['organization_id'],'bit-physics-optical')
        self.assertFalse(p['sampling_affiliation']['joint_appointment_verified'])
        self.assertIsNone(p['listed_role']); self.assertEqual(len(p['appointments']),1)
        self.assertEqual(p['appointments'][0]['institution'],'北京理工大学前沿交叉科学研究院')
        self.assertIsNone(p['appointments'][0]['title']); self.assertEqual(p['appointments'][0]['start'],'2022-02')
        self.assertEqual(len(p['pending_appointment_candidates']),1)
        self.assertIn(p['display_affiliation_note'],row['profileMain'])
        self.assertIn('未核物理学院任职或双聘',row['profileMain'])
        self.assertEqual(len([e for e in p['education'] if e['event_kind']=='postdoctoral_research']),1)
        self.assertNotIn('准聘教授',row['profileContent'].split('<h2>任职经历</h2>')[1].split('<h2>论文')[0])

    def test_19_candidates_do_not_affect_export_tables_or_actual_consumers(self):
        changed=copy.deepcopy(self.d)
        for p in changed['people']:
            if p['person_id'] in PROFESSIONAL_IDS:
                for key in ['pending_education_candidates','pending_appointment_candidates','pending_mentor_candidates','pending_professional_fact_candidates']: p[key]=[]
                self.assertEqual(self.tables(p['person_id'],p),self.tables(p['person_id']))
        other=self.consumers(changed); original=self.consumers()
        for pid in PROFESSIONAL_IDS:
            for key in ['stages','ug','doctorate','mentors','labels','profileMain','profileContent','lineage','graph']:
                self.assertEqual(other['people'][pid][key],original['people'][pid][key],(pid,key))

    def test_20_canonical_tables_event_counts_and_tristates_are_exact(self):
        for pid in PROFESSIONAL_IDS:
            p=self.ps[pid]; tables=self.tables(pid)
            self.assertEqual(list(tables),['总览','经历','导师','论文','来源'])
            self.assertEqual(len(tables['经历'])-1,len(p['education'])+len(p['appointments']))
            self.assertEqual([row[11] for row in tables['经历'][1:1+len(p['education'])]],[e['degree_awarded'] for e in p['education']])
            self.assertEqual(len(tables['导师'])-1,len(p['mentors']))
            self.assertEqual(len(tables['论文'])-1,len(p['publications']))

    def test_21_all_new_department_workbook_cells_and_hyperlinks_match_canonical(self):
        from openpyxl import load_workbook
        departments={self.ps[pid]['department_id'] for pid in PROFESSIONAL_IDS}
        blocked={s['url'] for p in self.new for s in p['sources'] if s.get('navigation_enabled') is False}
        checks=0
        for dept in departments:
            people=[p for p in self.d['people'] if p['department_id']==dept]
            tables=dict(build.department_tables(people,self.d['updated_at'],self.d['institutions']))
            book=load_workbook(ROOT/'site/exports'/(dept+'.xlsx'))
            self.assertEqual(book.sheetnames,list(tables))
            for name,rows in tables.items():
                ws=book[name]; self.assertEqual((ws.max_row,ws.max_column),(len(rows),len(rows[0])))
                for i,row in enumerate(rows,1):
                    for j,value in enumerate(row,1):
                        cell=ws.cell(i,j); expected=build.clean(value)
                        self.assertEqual(cell.value,expected if expected!='' else None,(dept,name,i,j))
                        self.assertNotEqual(cell.data_type,'f')
                        target=cell.hyperlink.target if cell.hyperlink else None
                        self.assertEqual(target,expected if i>1 and build.valid_url(expected) and expected not in blocked else None,(dept,name,i,j))
                        checks+=1
            book.close()
        self.assertGreater(checks,900)

    def test_22_research_direction_alias_preserves_order_and_rendered_source_content(self):
        from html import escape
        js=self.consumers()
        for pid in PROFESSIONAL_IDS:
            p=self.ps[pid]
            if not p.get('research_fields'): continue
            expected='；'.join(x['name'] for x in p['research_fields'])
            self.assertEqual(p['research_interests'],expected)
            self.assertTrue(p.get('research_interests_source_ids'))
            self.assertIn(escape(expected),js['people'][pid]['profileContent'])
            self.assertIn(escape(expected),js['directories'][p['school_id']])

    def test_23_ledgers_pin_exact_sources_reviews_scopes_and_partial_limits(self):
        audit=json.loads((ROOT/'progress/rotation003-wave1-release-validation.json').read_text())
        audit_digests=audit['source_review_gate']['approved_source_review_evidence_sha256']
        self.assertEqual(len(REVIEWED_AUDIT_SHA256),38)
        self.assertEqual(len(set(REVIEWED_AUDIT_SHA256)),38)
        self.assertEqual(audit_digests,REVIEWED_AUDIT_SHA256)
        for school in EXPECTED_IDS:
            ledger=json.loads((ROOT/f'progress/{school}-rotation003-wave1-coverage.json').read_text())
            self.assertEqual(ledger['batch_id'],f'faculty-batch-{school}-rotation-003')
            self.assertEqual(len(ledger['source_references']),1)
            ref=ledger['source_references'][0]
            self.assertEqual(set(ref),{'sha256','independent_review_sha256','scope_sha256','qa_sha256'})
            self.assertEqual(ref['sha256'],SOURCE_PACKAGE_SHA256[school]); self.assertEqual(ref['independent_review_sha256'],REVIEW_SHA256[school])
            for suffix in ['scope','qa']:
                self.assertEqual(ref[suffix+'_sha256'],REVIEWED_COMPANION_SHA256[school][suffix])
            shape,digest=SOURCE_CONTEXT_FINGERPRINTS[school]
            self.assertEqual(object_sha(project_source_shape(ledger['source_context'],shape)),digest,school)
            self.assertEqual(ledger['source_category_observed_count'],{'cqu':65,'xmu':29,'bit':33}[school])
            self.assertEqual(ledger['source_category_evidence_level'],'official_roster_body_read')
            if school=='bit':
                self.assertIn('34/33',ledger['source_category_count_basis'])
                self.assertIn('33/33',ledger['source_category_count_basis'])
            self.assertEqual(ledger['selection'],EXPECTED_SCOPES[school])
            self.assertEqual(object_sha(ledger['selected_roster_original_order']),EXPECTED_SCOPE_ENTRIES_SHA256[school])
            self.assertEqual(ledger['independent_source_review']['integration_limits'],EXPECTED_REVIEW_LIMITS[school])
            self.assertFalse(ledger['coverage_complete']); self.assertFalse(ledger['fields_complete']); self.assertFalse(ledger['university_complete'])

    def test_24_no_privacy_or_raw_cache_fields_in_additions(self):
        forbidden={'email','phone','mobile','telephone','birthdate','birthday','date_of_birth','student_names','students','raw_html','raw_body','raw_text','html','full_text','public_raw_cache'}
        def visit(value,path=''):
            if isinstance(value,dict):
                for key,child in value.items():
                    self.assertNotIn(key.lower(),forbidden,path+'/'+key)
                    visit(child,path+'/'+key)
            elif isinstance(value,list):
                for i,child in enumerate(value): visit(child,path+'/'+str(i))
        for p in self.new: visit(p,p['person_id'])
        for e in self.r['entries'][1712:]: visit(e,e['id'])

    def test_25_mutation_guard_catches_every_original_scalar_leaf(self):
        def paths(value,path=()):
            if isinstance(value,dict):
                for key,child in value.items(): yield from paths(child,path+(key,))
            elif isinstance(value,list):
                for i,child in enumerate(value): yield from paths(child,path+(i,))
            else: yield path
        for pid,(shape,digest) in SOURCE_FINGERPRINTS.items():
            original=project_source_shape(source_view(self.ps[pid]),shape); all_paths=list(paths(original))
            self.assertEqual(len(all_paths)+PUBLIC_METADATA_REMOVED_LOCATOR_LEAF_COUNTS[pid],SOURCE_LEAF_COUNTS[pid])
            for path in all_paths:
                changed=copy.deepcopy(original); target=changed
                for key in path[:-1]: target=target[key]
                target[path[-1]]={'unreviewed_mutation':True}
                self.assertNotEqual(object_sha(project_source_shape(changed,shape)),digest,(pid,path))

    def test_26_mutation_guard_catches_missing_keys_and_array_size_changes(self):
        def containers(value,path=()):
            if isinstance(value,(dict,list)):
                yield path,value
                for key,child in (value.items() if isinstance(value,dict) else enumerate(value)):
                    yield from containers(child,path+(key,))
        for pid,(shape,_) in SOURCE_FINGERPRINTS.items():
            original=project_source_shape(source_view(self.ps[pid]),shape)
            for path,value in containers(original):
                changed=copy.deepcopy(original); target=changed
                for key in path: target=target[key]
                if isinstance(target,list):
                    target.append(None)
                    with self.assertRaises(AssertionError,msg=(pid,path)): project_source_shape(changed,shape)
                elif target:
                    del target[next(iter(target))]
                    with self.assertRaises(KeyError,msg=(pid,path)): project_source_shape(changed,shape)

    def test_27_closure_guard_rejects_source_url_event_or_candidate_corruption(self):
        for mode in ['source','url','provenance','edge','education_filter','appointment_filter']:
            p=copy.deepcopy(self.ps['bit-daiyunyun' if mode=='appointment_filter' else 'bit-chenyuhui'])
            if mode=='source': p['education'][0]['source_id']='unknown-source'
            elif mode=='url': p['education'][0]['source_url']='https://wrong.example.test/'
            elif mode=='provenance': p['mentors'][0]['field_provenance']['name']='unknown-source'
            elif mode=='edge': p['mentors'][0]['education_event_id']='candidate-only-event'
            elif mode=='education_filter': p['pending_education_candidates'][0]['include_in_education_filters']=True
            else: p['pending_appointment_candidates'][0]['include_in_appointment_filters']=True
            with self.assertRaises(AssertionError,msg=mode): assert_source_closure(p)

    def test_28_generated_site_preserves_canonical_profiles_and_pending_layer(self):
        actual_site = json.loads((ROOT/'site/atlas.json').read_text())
        actual_data = json.loads((ROOT/'data/atlas.json').read_text())
        self.assertEqual(actual_site['people'], actual_data['people'])
        self.assertEqual(actual_site['pending_people'], actual_data['pending_people'])
        self.assertEqual(actual_site['build_id'], json.loads((ROOT/'site/rosters.json').read_text())['build_id'])
        site=release25_view(json.loads((published_root()/'site/atlas.json').read_text()), 'site/atlas.json'); roster=release25_view(json.loads((ROOT/'site/rosters.json').read_text()), 'site/rosters.json')
        self.assertEqual(site['people'],self.d['people']); self.assertEqual(site['pending_people'],self.d['pending_people'])
        self.assertEqual(site['build_id'],roster['build_id']); self.assertEqual(len(site['exports']),111)
        self.assertEqual(len(roster['entries']),1721)

    def test_29_unaffected_build_helpers_and_assets_remain_byte_identical(self):
        # Exact old release SHA/token assertions; current runtime is checked separately.
        for file,digest in UNCHANGED_APPLICATION_SHA256.items():
            self.assertEqual(hashlib.sha256(historical_bytes(file, root=published_root())).hexdigest(),LAYOUT_FIX_APPLICATION_SHA256.get(file,REVIEWED_COMPATIBILITY_SHA256.get(file,digest)),file)
        for file,digest in REVIEWED_COMPATIBILITY_SHA256.items():
            self.assertEqual(hashlib.sha256(historical_bytes(file, root=published_root())).hexdigest(),RELEASE26_DISPLAY_SHA256.get(file,LAYOUT_FIX_APPLICATION_SHA256.get(file,digest)),file)

    def test_30_actual_validators_consumers_and_exports_are_nonmutating(self):
        before=object_sha([self.d,self.r])
        build.validate(self.d); validate_rosters(self.r,self.d)
        self.assertTrue(self.consumers()['unchanged'])
        for pid in PROFESSIONAL_IDS: self.tables(pid)
        self.assertEqual(object_sha([self.d,self.r]),before)

    def test_31_disabled_workbook_hyperlinks_are_scoped_per_person_without_losing_raw_url(self):
        from openpyxl import Workbook
        url='https://official.example.test/evidence'
        people=[{'name':'blocked-person','sources':[{'url':url,'navigation_enabled':False}]},
                {'name':'available-person','sources':[{'url':url}]}]
        mapping=build.disabled_sources_by_person(people)
        wb=Workbook(); wb.remove(wb.active)
        ws=build.sheet(wb,'source-isolation',[['姓名','来源'],['blocked-person',url],['available-person',url]],mapping)
        self.assertEqual(ws.cell(2,2).value,url); self.assertIsNone(ws.cell(2,2).hyperlink)
        self.assertEqual(ws.cell(3,2).value,url); self.assertEqual(ws.cell(3,2).hyperlink.target,url)
        wb.close()

    def test_32_duplicate_names_with_a_disabled_source_reject_ambiguous_export_routing(self):
        people=[{'name':'same-name','sources':[{'url':'https://official.example.test/a','navigation_enabled':False}]},
                {'name':'same-name','sources':[{'url':'https://official.example.test/a'}]}]
        with self.assertRaises((AssertionError,ValueError)):
            build.disabled_sources_by_person(people)
        # A person's source veto must not be broadened by silent same-name union.
        self.assertEqual(people[1]['sources'][0],{'url':'https://official.example.test/a'})

    def test_33_crossunit_identity_links_only_the_reviewed_sampling_and_employment_pair(self):
        from build_rosters import _sampling_profile_match, _verified_profile_match
        p=self.ps['bit-daiyunyun']; e=self.entries[p['person_id']]
        self.assertTrue(_sampling_profile_match(e,p)); self.assertTrue(_verified_profile_match(e,p))
        self.assertEqual(e['organization_id'],'bit-physics-optical')
        self.assertEqual(e['profile_department_id'],'bit-frontier-interdisciplinary-institute')
        self.assertEqual(e['profile_identity_evidence']['reviewed_source_sha256'],SOURCE_PACKAGE_SHA256['bit'])
        self.assertEqual(e['profile_identity_evidence']['independent_review_sha256'],REVIEW_SHA256['bit'])
        coverage=[r for r in self.r['coverage'][212:] if r['school_id']=='bit']
        self.assertTrue(coverage); self.assertTrue(all(r['organization_id']=='bit-physics-optical' for r in coverage))

    def test_34_crossunit_identity_rejects_missing_evidence_and_mismatched_targets(self):
        from build_rosters import _sampling_profile_match, _verified_profile_match
        original_p=self.ps['bit-daiyunyun']; original_e=self.entries[original_p['person_id']]
        mutations={
            'missing_sampling_unit':lambda e,p:p['sampling_affiliation'].pop('organization_id'),
            'missing_sampling_url':lambda e,p:p['sampling_affiliation'].pop('source_url'),
            'missing_profile_department':lambda e,p:e.pop('profile_department_id'),
            'missing_profile_organization':lambda e,p:e.pop('profile_organization_id'),
            'wrong_school':lambda e,p:e.update(school_id='cqu'),
            'wrong_name':lambda e,p:e.update(name='other-person'),
            'wrong_verified_person':lambda e,p:e.update(verified_person_id='bit-chentian'),
            'wrong_source_person':lambda e,p:e.update(source_person_id='bit-chentian'),
            'missing_review_pin':lambda e,p:e['profile_identity_evidence'].pop('independent_review_sha256'),
            'missing_source_pin':lambda e,p:e['profile_identity_evidence'].pop('reviewed_source_sha256'),
            'missing_sources':lambda e,p:p.update(sources=[]),
            'missing_identity':lambda e,p:p.update(identity_evidence={}),
            'missing_identity_date':lambda e,p:e['profile_identity_evidence'].pop('checked_on'),
            'unclosed_evidence_source':lambda e,p:e['profile_identity_evidence']['source_ids'].append('unknown-source'),
            'candidate_only':lambda e,p:e.update(profile_identity_verified=False,verified_person_id=None,candidate_person_ids=[p['person_id']]),
            'pending_person':lambda e,p:p.update(detail_count_eligible=False),
            'joint_appointment_claim':lambda e,p:p['sampling_affiliation'].update(joint_appointment_verified=True),
            'changed_profile_query':lambda e,p:e.update(official_profile_url=e['official_profile_url']+'?unreviewed_identity=other'),
            'unavailable_person':lambda e,p:p.update(official_profile_availability='unavailable'),
        }
        for mode,mutate in mutations.items():
            p,e=copy.deepcopy(original_p),copy.deepcopy(original_e); mutate(e,p)
            with self.subTest(mutation=mode):
                self.assertFalse(_sampling_profile_match(e,p)); self.assertFalse(_verified_profile_match(e,p))
        # Missing in both representations must not turn undefined==undefined into identity evidence.
        p,e=copy.deepcopy(original_p),copy.deepcopy(original_e)
        p['sampling_affiliation'].pop('organization_id'); e['sampling_affiliation'].pop('organization_id'); e.pop('organization_id')
        self.assertFalse(_sampling_profile_match(e,p))

    def test_35_all_107_original_department_workbooks_stay_byte_identical(self):
        self.assertEqual(len(BASELINE_DEPARTMENT_WORKBOOK_SHA256),107)
        for file,digest in BASELINE_DEPARTMENT_WORKBOOK_SHA256.items():
            self.assertEqual(hashlib.sha256(historical_bytes(file,((published_root() if file in ('site/exports/uestc-public-administration.xlsx','site/exports/uestc-applied-math-center.xlsx') else ROOT)/file).read_bytes())).hexdigest(),digest,file)

    if os.environ.get('ACADEMIC_ATLAS_NEGATIVE_CONTROL_ROOT'):
        def test_36_baseline_real_workbook_writer_reproduces_disabled_source_hyperlink_defect(self):
            import importlib.util
            from openpyxl import Workbook
            baseline=pathlib.Path(os.environ['ACADEMIC_ATLAS_NEGATIVE_CONTROL_ROOT'])
            spec=importlib.util.spec_from_file_location('release24_negative_control_build',baseline/'scripts/build.py')
            old=importlib.util.module_from_spec(spec); spec.loader.exec_module(old)
            p=self.ps['cqu-chenke']; urls=[s['url'] for s in p['sources'] if s.get('navigation_enabled') is False]
            self.assertEqual(len(urls),2)
            wb=Workbook(); wb.remove(wb.active)
            ws=old.sheet(wb,'baseline-control',[['姓名','来源'],*[[p['name'],url] for url in urls]])
            for index,url in enumerate(urls,2):
                self.assertEqual(ws.cell(index,2).value,url)
                self.assertEqual(ws.cell(index,2).hyperlink.target,url,'Negative control must reproduce original live hyperlink')
            wb.close()


# Exact layout-only overlay; all original source/data/application pins remain above.
LAYOUT_FIX_APPLICATION_SHA256 = {'site/styles.css': '3b01ec6a5674982d048237e5426aa107bd622662d2758913c81bc6f5c4c0ceca', 'site/app.js': '5ce1dbc7161a048ab263cdff313bc904544b362c13d39cc5963886b409f037e2', 'site/rosters.js': '7536ef08c4032e05e1ad3c09532858dd42fd68c20968c82e2146481cf6d9c85f', 'site/index.html': '7e6331d4846c13d64f0a5b5b65a9d52539df537b2ce20ef26563669739f8f2a3'}

# Exact three-file heading/cache correction; all earlier golden constants remain.
RELEASE26_DISPLAY_SHA256={'site/index.html': 'a6e57e88a623157fd3103a6099b9e72b21a0435c9fa62530a41469814844242c', 'site/app.js': '19945c1392982e4b3a1df95d93c271e957bf16b2a238f8d63d24ed892c722dea', 'site/rosters.js': 'd060662fe29e2d5209ca7cabd89121f253c6df69878d776e652f2fe8f8eb45a9'}

if __name__=='__main__': unittest.main()
