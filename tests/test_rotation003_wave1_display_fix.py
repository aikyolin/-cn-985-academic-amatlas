from source_date_history import historical_bytes
from published_fixture import published_root
"""Two evidence-bound Chen Ke teaching-role aliases, with no implementation change.
Self-contained offline regression; no research/baseline dependency or output writes.
"""
from release_history import release25_view
from public_append_history import endpoint_sha256
import copy,hashlib,json,os,pathlib,sys,unittest
sys.dont_write_bytecode=True
ROOT=pathlib.Path(os.environ.get('ACADEMIC_ATLAS_TEST_ROOT',pathlib.Path(__file__).resolve().parents[1]))
sys.path.insert(0,str(ROOT/'scripts'))
import build

def object_sha(value):
    return hashlib.sha256(json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def json_bytes_sha(value):
    return hashlib.sha256((json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode()).hexdigest()

BASELINE_ATLAS_SHA256 = '96d98129c6d68768083733019ade3e9514361a773c420f8a5d3244cd09da5ab5'

BASELINE_ATLAS_OBJECT_SHA256 = '37876eea56b0f11f92c95cc99f132991b9ebda2c8c4b526887f39aeaa70e821f'

BASELINE_SITE_ATLAS_SHA256 = 'e3bb17bc6493e5e54a7893606065e350e98ff7ae1de22b6ee2bdc4473048d760'

BASELINE_SITE_ROSTERS_SHA256 = '8cc0217da1f664c1425c5fe49f9acb91d063772e21e3e5a5dd103d4d244e746e'

BASELINE_BUILD_ID = 'bd358f2fcbb8afe8'

BASELINE_TEACHING = [{'course': '建筑设计(1)+(2)',
  'level': None,
  'period': None,
  'source_id': 'cqu-chenke-teaching-2021',
  'source_url': 'https://news.cqu.edu.cn/archives/news2/content/2021/04/01/eeab4ef47653f3eca46265fa0c4a0a4d4a1eb0e4.html',
  'source_navigation_enabled': False,
  'source_availability': 'direct_404_cached_body_only',
  'evidence_status': 'official_cached_body_read_direct_404',
  'field_provenance': {'course': 'cqu-chenke-teaching-2021', 'level': None, 'period': None, 'note': ['cqu-chenke-teaching-2021']},
  'field_status': {'course': 'source_reported', 'level': 'not_disclosed', 'period': 'not_disclosed'},
  'as_of': '2021-04-01',
  'status': 'historical_source_reported',
  'note': '报道明确主讲课程；未声称2026仍授课。',
  'source_note': '报道明确主讲课程；未声称2026仍授课。',
  'note_derivation': 'verbatim_original_note_level_and_period_for_existing_teaching_consumers'},
 {'course': '泛设计思维',
  'level': None,
  'period': '2025-09-18',
  'source_id': 'cqu-chenke-lecture-2025',
  'source_url': 'https://news.cqu.edu.cn/archives/news2/content/2025/09/19/6bab3d43eb9c2f730772541ee4d983ff5aced5f3.html',
  'source_navigation_enabled': False,
  'source_availability': 'direct_404_cached_body_only',
  'evidence_status': 'official_cached_body_read_direct_404',
  'field_provenance': {'course': 'cqu-chenke-lecture-2025',
                       'level': None,
                       'period': 'cqu-chenke-lecture-2025',
                       'note': ['cqu-chenke-lecture-2025']},
  'field_status': {'course': 'source_reported', 'level': 'not_disclosed', 'period': 'source_reported'},
  'activity_type': 'public_science_lecture',
  'status': 'historical_source_reported',
  'note': '系列讲座首场、18日晚由本人主讲；不是学期课程或长期任课。；来源教学时期：2025-09-18',
  'source_note': '系列讲座首场、18日晚由本人主讲；不是学期课程或长期任课。',
  'note_derivation': 'verbatim_original_note_level_and_period_for_existing_teaching_consumers'}]

BASELINE_TEACHING_SHA256 = '5281a6be9884dabc8cbff18298c2b3eaff8e8c277a6f6242badc4fe815b13012'

BASELINE_OTHER_TEACHING_SHA256 = '306ff9682224028c50c512a9826190dc07c9034ef4e87439195a4b3ee28020d1'

# Exact evidence subset of the release25 source-review gate audit, in reviewed order.
SOURCE_AUDIT_SHA256 = ['74c7d1f2908c6fed3fca29f0e577de03465e66c0da54e639299fa5caa70ac7fc',
 '0317f6e539c923722bc72e5ac3ca6e9a1ac2b7b03a663da3a8b70a97623195eb',
 '1ad0ad1f34dc83b1473eaa6c925b1e3f68c2ae132fbf8c9d15bc09355b272bf2',
 '4ca72ccc9566b64097a79bebee40ed1d4861b854cd6d3d5d7780dc173a3166e2']

UNCHANGED_FILES = {'data/rosters.json': '593f845e1688780d2dab562883048383e80e0f5921689ef6446df444dac7a396',
 'site/app.js': '5d4efe8a3c85cbca0125b950a70d7494e3d34a2e67240e6043347903965c8d4b',
 'site/model.js': '9dbc155288c1ee0a93fd5d11cd8a7c63724dc0bde6b117a2f71d327e34be3fef',
 'site/rosters.js': 'e4bb3c53da7a4ff3c00c1109651d66cc479c20dc265e7705e41213e3019a3502',
 'site/styles.css': '6063be4c04726d2dcf01a0442d5dc4d763b99c835a4110bd943799582c14fc34',
 'site/universities.js': '9323dad42fc2c35808ad92888cdffb0ad41edaefaee88c3b57ebb798349c2d62',
 'site/index.html': '3b5f7afdd4ac96aaca402884976bccb33cb9a1d2a1ad27793cf7cdd82e5970bf',
 'scripts/build.py': '92b6ec03d18666503a7e890e09faffe2e3ac7be61b017ec85b291c1498addacb',
 'scripts/build_rosters.py': '29c5dee611bfaef3fd6afd1df9480b254652c51b1c4ce1c9568d75cb799319fe',
 'scripts/deterministic_xlsx.py': '65158f54d001eebb2ac586fd820cd69deed8e5c96ed5b117668ced51c11dc300'}

UNCHANGED_DEPARTMENT_WORKBOOKS = {'site/exports/bit-cs-image-perception.xlsx': '8ecc8beff095f5f5d11220ad0b50ec47695fdae46b9869cd73e08d2f665b6732',
 'site/exports/bit-frontier-interdisciplinary-institute.xlsx': '3354cfe01171db2404b63e0ad8647ec7af93f75594b98ef895209f085c789f07',
 'site/exports/bit-physics-optical.xlsx': 'd8f38ddc33d62b132a30cde81d43706bf36d495f62bf4b1e9bb143c7033ec163',
 'site/exports/bit-sie-communications.xlsx': '92cd5ee427b093fb4b9760ef9ebab38b694a331139f9d2eccf54d61f81db4803',
 'site/exports/bnu-ai.xlsx': '86f12f0f36ff3872324f1973ba9576a87a46166609f9702afce219e53ab2ab46',
 'site/exports/bnu-math.xlsx': 'c70465e0d1860159cc254795a94c5d24c32b95c7aacb77fbbfd4623a45a1f3f1',
 'site/exports/buaa-cs.xlsx': '0f33d60bb4e9c874de291915fe7f2df0038bb3583383a3f4cfc74e4343842467',
 'site/exports/buaa-physics-applied.xlsx': '147b53eea044df39df75298e78bb35da3e023773641d721059c61971c2f73315',
 'site/exports/buaa-physics-department.xlsx': '73cc282a3510574a41813c3fafd354658d1d9bc7a52f368a2fb342160585a9db',
 'site/exports/buaa-physics-nuclear.xlsx': 'fc5ca475c896cde5528aab0c59ef682398c955e804e390f81e7cd794b4e0eca6',
 'site/exports/cau-biology-plant-science.xlsx': '619ad8d84b8686eb1d1c9d21a7b3e8c6f8f64476a64443c63adf3f6bd15d5b31',
 'site/exports/cau-ciee-computer.xlsx': '54b8579a0593a744dedf82dcc32c9d8e112dd402689e4a44d049abc11e30f4cf',
 'site/exports/cau-science-math.xlsx': 'c03fc7faa75c7bb128f43effa033b3a55512b0fe5a4303d98d708677899834c4',
 'site/exports/cqu-cs.xlsx': 'e67dd852d2efb14019ee1fed04ba3c2250da2b5bb5f22b61e0e8e83a853c237c',
 'site/exports/cqu-mathematics-statistics.xlsx': '11e246f87cff7aef8d529706b854e39cb1a4a338570ccfe2d70dc02e519447e0',
 'site/exports/csu-cse.xlsx': '3fc12ea5379b0c669a0b6855c513c8fb46cb0f432d8a882a220e4fe2ce20d44d',
 'site/exports/csu-math-applied.xlsx': '7484e1fc254fa9987bc57bdb292e1efc5ecdf318e53b84e06d295792bd8f6847',
 'site/exports/dlut-cs-software-theory.xlsx': '5dbde15b50dab984d986ec3493d78ad5c7d27d8fcdf0c30658d7d342f9aad06d',
 'site/exports/dlut-math-institute.xlsx': '1625969239b59a8244f727a522eb83e957cacb64b3e4d465704a4816c496a5a3',
 'site/exports/ecnu-geography.xlsx': 'bfc7480dde7dfa3ad263093384eb73c828e2359e4de331484aa0bdf2ebad4c0e',
 'site/exports/ecnu-math-applied.xlsx': '4d657056812b4a89a8ce7c4e4b3a228c3a94eb5f29e9ed9d7fe474ffba2994cb',
 'site/exports/ecnu-math-pure.xlsx': 'b35e580a30dd29f4a180843d078fc23dfdbb6229daebc40cdc97bf6e0f6d27a7',
 'site/exports/ecnu-sei.xlsx': '73529cf6469491fb6fa8793ab5f0c54327cfa3617f671e3aaa5ba449e5212c1c',
 'site/exports/fdu-icmne.xlsx': 'b6849ef1b1be24cca002bc0a0f915b6a8d4434ff8c09556d7b4568910c4d820e',
 'site/exports/fdu-math-applied.xlsx': '8bed2e4e437b8426ddc39309946adaf02c3829b73d6e29f05d1a7ef176a0a23d',
 'site/exports/fdu-math-probability-statistics-actuarial.xlsx': '193ff4457d1f269d3b7e9dce9a35dbf2c0195b3477f86b04aef633ed9f9b8e22',
 'site/exports/hit-computing.xlsx': '958fbc68d19dcf3690a1087ade9da24287a56383536f06e684caad3cdc9fd172',
 'site/exports/hit-seie.xlsx': '543c05288964285cc03152107b0682c4094c7ac14f5cdef2f80b8319ba0c0166',
 'site/exports/hit-shenzhen-computer.xlsx': '58b222b67d96818aa52f16d201a8449bef5bb36e2302cf2bd5a68e9ae1aa8d53',
 'site/exports/hit-shenzhen-ic.xlsx': '3744f412bbd5e7e21969cdb953040409d6720e385153fd1b7f1a3e43432c3b8f',
 'site/exports/hit-shenzhen-robotics.xlsx': 'ab6d347fa8b292fb66cec686ad16dc974af9188acc435e6d2f8856009d70797b',
 'site/exports/hit-weihai-information.xlsx': '7cb591f80874dfb4fe3ccce0259f28cd0c9a0c6fde49c1ab30d63eb6c328433d',
 'site/exports/hit-weihai-materials.xlsx': '54d21c6da24008000fb4191e8bf2c4d5adc811eed95c33982669cc3696f5743a',
 'site/exports/hnu-chemistry-department.xlsx': 'd868060f83ebce45609cd1446ceafcce5c4892478dc9a926dfc0afb0aeb1e040',
 'site/exports/hnu-cs-communication-engineering.xlsx': 'e01ae98178c1caf20c1e18740e02db76998554dea745fc646c9e70939827d6b7',
 'site/exports/hnu-cs-computer-engineering.xlsx': '7bb5394feca7c1986e877cfdddf7483b88a358d8c93ad35dd847199a03271c9f',
 'site/exports/hnu-cs-software-engineering.xlsx': '4fdffd5a5f323dda2f212948be7a716d97581aa30820b467e45c49805e42a6c4',
 'site/exports/hnu-math-basic.xlsx': '8d45b2063647a144c74c7f8e7d5ec33e848a5787e24a8dc8f26408501120a95c',
 'site/exports/hust-cs-storage.xlsx': 'be5028ada1801939f2f53daa010249bc031a9a6a43f2555aee0aa7c5aac7a39d',
 'site/exports/hust-math-center.xlsx': '958cd31af3a503ea4187fe4f6bfd42131be4d57d453f7fcbe5a02bdeb27533b5',
 'site/exports/hust-math-interdisciplinary.xlsx': 'ec1f1fa56ac08e000b7808f0297d6814dbb9f744a4c42003da2b6c3fba39524f',
 'site/exports/jlu-cs.xlsx': '4546f557b871c5e584dfdaac60affa8551bfa545cca0799018453e84e73a13a0',
 'site/exports/jlu-math-applied.xlsx': '14536830ff485834b0e45603626ba94a72d6ed471cbc0162491479fb64dafa89',
 'site/exports/jlu-math-computational.xlsx': '81d7218696de8a5dbbe215ea7a4e37ad9e166db36a2ad41093ada4d9d0bfc46f',
 'site/exports/jlu-math-statistics.xlsx': '610cb4d6748821fd9e0f8b31dbfda3e04adea16e10c7ea0961a768f7cd9261b4',
 'site/exports/lzu-basic-mathematics.xlsx': '6dc90c17aac81334fe036dceed021942ea587480215450eb04ed61cab8eba029',
 'site/exports/lzu-law.xlsx': '8d62ec02ae35b737b04feb281ed89e0cc6cdacfcc83ae9b6f3eca2f891db294f',
 'site/exports/muc-ise-cs.xlsx': 'b7642d209c8ada88bd470c37fe712191233031b8765402b6fd94400f039c305e',
 'site/exports/muc-science-math.xlsx': '22ef1e1930c2c49eed629dceb1bbf0a12fd84e880494eb582ab3acf7fd628279',
 'site/exports/neu-cse-communication-electronics.xlsx': 'bf487e818fd5e703b46b8f334baa28dea7b7790bd600b3a74a04f86c471164ae',
 'site/exports/neu-cse-cs.xlsx': '6a9dfc9331ac2fc757122aa3d3bcff44d1736c91dcd32906bcbef0dd1c056079',
 'site/exports/neu-mechanical-vehicle-engineering.xlsx': '51f430c8c53d29bdde2ef6f552c9ce74781440650e90a4009f61c0b0e45d1b1f',
 'site/exports/neu-science-math.xlsx': '12f9dbeaf2b25a09049b5aa3a3489e9bce73006f7bab618d2de0e7489542f796',
 'site/exports/nju-astronomy-space-science.xlsx': '477a5f1ca3a470e9fbe0392903c40dffc5adac2d1e16154b8ed9ed124a5d873a',
 'site/exports/nju-cs.xlsx': 'e75ef1d05b07d7c34effe7abbacce42d088eff06a18fc6966366fc1c88d54785',
 'site/exports/nju-math.xlsx': '221e7ff8f76efdde2fd3542aa979d75651dfd972655d8119a6a1ca6a8e071c58',
 'site/exports/nju-sme.xlsx': '1a4af1c71eb2aaf3a18081db8653aee42c0879605eb5f0ed04b746cd007edf94',
 'site/exports/nku-cs.xlsx': '129463d6106d689e4a416d343ed11d089dd9b98584178de4635c3a08a2382771',
 'site/exports/nku-cyber.xlsx': '920978e9a9d5e45a57915c2c8ccc739ca5e928aad3f97df899f494df62e53d75',
 'site/exports/nku-stat.xlsx': '227e4c232fc5efc3a5e6e087ed3282bdd56c9b20738ce3102dd715b95d75e4aa',
 'site/exports/nudt-aerospace.xlsx': '4d422f6152bc4ef75d334a719e60a6eaff8bbc5903dc582c363e095814a6f256',
 'site/exports/nudt-electronic-science.xlsx': '3260867dd2d0b5239a05c60c3167240c92ee65ce56b6935d7aaf9e56e0fc9c84',
 'site/exports/nudt-electronics.xlsx': 'ad7a5b1686c3da6e73d2f680c41a9ed26fdc99b2d8847175b98012a37c70e92f',
 'site/exports/nudt-foreign-languages.xlsx': '70f192adf64fe607676d7e3b78e9fff5a5674c1ffaea2032699957f13e4af4a5',
 'site/exports/nudt-intelligence.xlsx': '9225f49a9da23e9a168158a4d02aaa0a98e6fc06aab75f02258dde270725bd80',
 'site/exports/nudt-systems.xlsx': '417c343ecbc9917662df640ab2dffb3ec16b38a3f20c3618f009068c81c8bfb1',
 'site/exports/nwpu-cs-computer-science-software.xlsx': '15f646eb84972804a67d0e7f2b763bc252822ce2f01a3bf7aaad89cf1511ac4d',
 'site/exports/nwpu-mathematical-sciences.xlsx': 'c36069333720ebb5c0965eb0f27c37eb9b957c396010bc3dabf095ec7d4dba61',
 'site/exports/nwsuaf-agronomy-agronomy-department.xlsx': '38ab9f806f741fc54bca7f42cd149662681de1573710e33385ccb31ab58a1aad',
 'site/exports/nwsuaf-cie-cs.xlsx': '5a0a8e7b0dbc3dc0563bc8a131d0d0f7908c94baae45167d69f044ecdaf7db1c',
 'site/exports/nwsuaf-cie-data.xlsx': 'c008f08177b0577eb59e985fe06ed84b756ebf969229af3d6d538e3a3e056bf8',
 'site/exports/ouc-ise-cs.xlsx': 'bef4f4e5a5257b44251746e8e15162bd646857d088f6e294c8eeb4d1b203633a',
 'site/exports/ouc-math-department.xlsx': 'a8b97ffaf5f340533da5a8d12b133a76a5b54c676dc8637a2459662dd7efe272',
 'site/exports/pku-ic-microelectronics.xlsx': '7291ebe2cc688be153704102e39d3864df91bac5ad97259d16bd73a656554f42',
 'site/exports/ruc-gsai.xlsx': '6b1429699da46c5f4fee3585c11721d2bd4023fd5d1fc063b533f690c5760b65',
 'site/exports/ruc-info-eim.xlsx': '2ac362a53b5fbb1ff7580f04bba9d2c6fcec00a31540cfcde5cbe41c1c0c0119',
 'site/exports/scu-chemical-engineering.xlsx': '60f80f78f8ecfa134b4957c0d2d04a16c78f2348a2c9ffb612784adcfd625186',
 'site/exports/scu-cs.xlsx': '3cc913079af73ad9b667b2a7e248c9b693bee07aa6ccc49b954f96a93cd50d5d',
 'site/exports/scu-materials-science-engineering.xlsx': '77501002ebe4b12fe264a9a47249b1f60e3456571442b195d567eaacd3f001c8',
 'site/exports/scut-cs.xlsx': '6fc48b36e796167f01e0326b06812c3d7507e10a9585b36b18fabdff9009bdf0',
 'site/exports/scut-math.xlsx': '4c461609c2f0e78b8be8cc0f3a020387c67a8f52a787245ef678df126db5f5ee',
 'site/exports/sdu-cs.xlsx': '15065fcc41a9a0f5413cb6bf36a83ddb7b6dd8ef3b42e54a488929feb3c2653e',
 'site/exports/sdu-math.xlsx': 'e9f056cb5a86693f16de85a93c3d50f3195140c34c87f75fa6e4580fd2232202',
 'site/exports/seu-computing-joint-roster.xlsx': '48d5b9a81a28296fe5d265edcd4fc369d1c970fcaffd0c7df91b781f79d528fe',
 'site/exports/seu-cs.xlsx': 'abe27d1aa51acf1275aa560931da66d82ffe22fb451f62dd8c46168b07c2d465',
 'site/exports/seu-math-computational.xlsx': '52f2403373aba5dee463834813b9e7f8bd497c3760e6688e5de592964e869751',
 'site/exports/seu-math-systems.xlsx': 'f54dc7088b8341fce7a57f31a6dc9b4c75bb49cb3bae428ef5a207552024f42f',
 'site/exports/sjtu-ic-chipdesign.xlsx': 'b3fa394373ae7fcb6c84142d81637c22e5f8dfaa0d4f1df97c93163cecc89a11',
 'site/exports/sysu-history-zhuhai.xlsx': 'dffc21bfb97d1ac8d1817c172370f6523b4a90535aabdc16cbd246f0e28cd115',
 'site/exports/sysu-math-department.xlsx': 'ecc826f6e90603d05c17f6e7ed167f97974db04fbe3b175ca3e6ffbcbdc33111',
 'site/exports/sysu-math.xlsx': '3edf48eda175bb96169ef9cd3d0960c5195ba3537d04431843b22e7f27cd2144',
 'site/exports/sysu-mathzh.xlsx': 'cdebb1c4bdb74a374c17d7c0e7f68eb5fc596833d450098b28a9ccb64ffb37d9',
 'site/exports/thu-ee-communications.xlsx': '8701a586cde1d10eec194b8eb20fd648f12af8620f1d6c0c9828ab00a88d36e9',
 'site/exports/tju-math.xlsx': '399936224a993c995cfad6cbb80a6dc74486f21621fe5e6ae473aee4d939a20e',
 'site/exports/tju-sme.xlsx': '4f963ba2740c54d0406764f9384a03733e5ecc406294c633290fb333fa6144c0',
 'site/exports/tongji-civil-building-engineering.xlsx': '448632503151618b790da7adeb660b90b2fbd6bfaa8fa1e2d14d4f500e06b63c',
 'site/exports/tongji-cs.xlsx': '99bd75bb420f58781e1b8a389e7d8ff72f5ccb97c4a77f09ed0af96da50c26d5',
 'site/exports/tongji-math-teaching.xlsx': '84e40719460679f31b96cdda3cff6da20c17a10448c3e9ac89f92d5c4e351a3b',
 'site/exports/uestc-aihss.xlsx': '3a4fabc60237a4ff3e854f764d4c4bbe92fe55c88977f7c7ce847b0d22838952',
 'site/exports/uestc-applied-math-center.xlsx': '0d31c20c27bcf996526e01c573cf396f11f1fdfd3a888be34d8033d042148c31',
 'site/exports/ustc-ic.xlsx': 'bba52cc29f384a3ccc4e6b582ab4cdf1e7be215e4b6059926e1f6809cfa0be7e',
 'site/exports/ustc-math.xlsx': '60edd4e8f47842ca1ce0e5e64f874d9365bffb51e71a92c641f4b4969e811297',
 'site/exports/whu-eis.xlsx': 'df7dfc47d4307136d341cbae96f731302c4414cd5e077b29dcb32968e63bf423',
 'site/exports/whu-math-stat.xlsx': '4d45cfd5fd92a1f18a6d89cbe9112bd9da8c9faac6696c025e1d81b297725818',
 'site/exports/xjtu-math-department.xlsx': '2bef8af7e2ac74764b31b651542b4f2547962c61d0a2ac95ee6530c45a2fc7f1',
 'site/exports/xjtu-se.xlsx': '74dda6adf6cb6a0ae0a376b13ca98bcd6fc7c06dbe72037172b16df698da94d2',
 'site/exports/xmu-economics-department.xlsx': '85c03296b5dce754f54306b70492a9e37ece071b966abe1dbfdfe659d93e9dcc',
 'site/exports/xmu-informatics-cs.xlsx': '4975c6535af5ec76a4c5cf9ad40e78627739cabf40f422db69a443b09152b62a',
 'site/exports/xmu-math-applied.xlsx': '080164257599a45cc2be8eb901fda292c3d9a233c10facd3319a4bb894379b55',
 'site/exports/zju-ic-manufacturing.xlsx': 'e683c104495e43aec93846c5d8767bd1040e0a135592c1003526028ed03262f9'}

BASELINE_ROSTER_WORKBOOK_SHA256 = '5e3dbea0ad5139f5cc180f4084de942375c89d63b92c0e8d5a6aa0c1c146582b'

ROLE_KEYS=('role','role_source_id','role_source_url','role_source_note','role_derivation')
SOURCE_IDS=['cqu-chenke-teaching-2021','cqu-chenke-lecture-2025']

def strip_aliases(atlas):
    restored=copy.deepcopy(atlas)
    p=next(p for p in restored['people'] if p['person_id']=='cqu-chenke')
    for row in p['teaching']:
        for key in ROLE_KEYS: row.pop(key)
        row['field_provenance'].pop('role');row['field_status'].pop('role')
    return restored


def assert_alias_contract(person):
    assert person['person_id']=='cqu-chenke'
    assert len(person['teaching'])==2
    for row,original in zip(person['teaching'],BASELINE_TEACHING):
        assert row['source_id']==original['source_id']
        assert row['role']=='主讲'
        assert row['role_source_id']==original['source_id']
        assert row['role_source_url']==original['source_url']
        assert row['role_source_note']==original['source_note']
        assert row['role_derivation']=='consumer_alias_from_explicit_reviewed_source_note'
        assert row['field_provenance']['role']==original['source_id']
        assert row['field_status']['role']=='explicit_source_note_normalized'
        restored=copy.deepcopy(row)
        for key in ROLE_KEYS:restored.pop(key)
        restored['field_provenance'].pop('role');restored['field_status'].pop('role')
        assert restored==original,'No original teaching field may change'
    return True



# Exact live release26 overlays; original golden constants remain above.
RELEASE26_PIN_OVERLAY={'data/rosters.json': 'bdc4f7a400bb2b983d341b434b636aaf2f1beeb5f3aa070486a0aa44920fe27a', 'site/exports/待核对名录.xlsx': '6e01fe76a8b3620f51e3a0ec68b27d1fa5a81ff3427ddfb266efd2e03235176a', 'site/index.html': 'a6e57e88a623157fd3103a6099b9e72b21a0435c9fa62530a41469814844242c', 'site/app.js': '19945c1392982e4b3a1df95d93c271e957bf16b2a238f8d63d24ed892c722dea', 'site/rosters.js': 'd060662fe29e2d5209ca7cabd89121f253c6df69878d776e652f2fe8f8eb45a9'}
# Exact release27 endpoint overlay; all earlier golden constants remain unchanged.
RELEASE27_PIN_OVERLAY={'site/atlas.json': '1d2e8210a0ca6d60b874d793bd77e49de7da6f845493eb6912b0f4861e57afa2', 'site/rosters.json': '4971f6b3812c6f8d133fd0aba909e65f2209b72cfb0d37e668c62531ec0446cc', 'data/atlas.json': '602e459ef4bc62aa839e8eff7475819f5a6672e1492b1181ac9188372fe9d1c5', 'data/rosters.json': '217716511dc290970fd8708af5cacebaf5f1343b1ec671515b5048e5f81dabec', 'progress/README.md': '08617604707fff4e8121cdd13b08ef3a92e96aa1df2b38cc9cad9f91cc5b1cc6', 'progress/current-coverage.md': 'f92a7728e5c329e0c203fa1c04910d485b496c83f1756728bf9bbd5dc7b55d4a', 'progress/work-queue.json': '88037ab5e76bb2744eaa5b5dc9601d5e1e375b31e3c3f33116e8eeb3a1fd1f60', 'site/exports/待核对名录.xlsx': '9100c6cf6a1a5b6128737e49ef0f79efa49779739efd11bafbf12dfa05917972', 'site/exports/待核对名录.csv': '2e14625fd76a04d5fa29ee4621669dd8b496ca26fbabb41df20043169f1fa78c'}
# Exact release28 endpoint overlay; all earlier golden constants remain unchanged.
RELEASE28_PIN_OVERLAY={'site/atlas.json': '36fe06b748feef6919e105ce3fa81c58426b43d8374ccb03b2d828960462ed8b', 'site/rosters.json': '84edc29d2a70ef04d809effe8b3757cba2d614d469691bb16a8ce9f711b052cc', 'data/atlas.json': '184d94676b19b55d24d00b9c6056748a3a778754dd920a1a126be21685168d61', 'data/rosters.json': 'eefa9fe9add7c8dd9aaa49b81deeda73e51a8a1b214a9a6b3a26a2429110de29', 'progress/README.md': '7db1b1af415d5ea1086b76c6253dd91bce89abb330cfaa39ce63bae45f2f2045', 'progress/current-coverage.md': 'ddd946e215da974b867a2da0816b9fc4d36758b18d2a4f99085e1800978665cd', 'progress/work-queue.json': '157958452c461dee7d1fced71e8c8260d09ac2548fcc262ebd7d01c34b4f4d7e', 'site/exports/待核对名录.xlsx': '0482a9b49535e69a633ac7e4a25920232525e1fa34a5c770b53bd8757aa55c1b', 'site/exports/待核对名录.csv': '62ead57bd26f1d29fa26ade92aa5f021937354f31427867b1b433ba25d15bd32'}
# Exact release29 endpoint overlay; original constants preserved.
RELEASE29_PIN_OVERLAY={'site/atlas.json': '4b976d4c2e4a5b0beb1c838263ade37ece4fd8b5561ab8517d8ad83e13ca0996', 'site/rosters.json': 'e9ac62ce2ff63201b443717af9da4468d449521238dcde53c79fad7e9676c904', 'data/atlas.json': 'e2cbfcde9c8f96ebc9e96a0829fe95698428b672fd611ab6dff1078eafa75303', 'data/rosters.json': '854ff13b8c352b68a51a20c1cd322f638664de68fdf4996bb922dc344250d11b', 'progress/README.md': '943924d756b71e5c0bb3b6057faf1bcc30193b0bdd1733cf5fe986e6bf1466cb', 'progress/current-coverage.md': '467b5664162ff2a1fbb17b9c71b80038be3bffbc24602cbae9c84dc0b63add5f', 'progress/work-queue.json': '6ce290b467650489cfc260a27ece315a6efd86442af058f4a8558f8a3dfca359', 'site/exports/待核对名录.xlsx': 'efc5aaeaefb8c9e73f726619db2a09cc8d17f4ee1807be879cb5f16cf1e3eaa5', 'site/exports/待核对名录.csv': '99ef76904dd171f877c9a442e9d338badb15ac68e4b3ec145b71462234eb9017'}
# Exact release30 current endpoint pins; all historical constants and assertions remain below.
# Exact release31 current endpoint pins; previous release assertions remain intact.
# Exact public-metadata endpoint overlay; previous hashes and all fact assertions are retained.
RELEASE31_PUBLIC_METADATA_PIN_OVERLAY={'data/atlas.json': '2f843a600ef79f9b6d24ee98b702ed17dc335c776c4893f0316b5064ba3474fb', 'data/rosters.json': 'fa3fd547a59c10a5e6285523fbcd5e3215b6076f59f0a9246554fedbf2e3a83e', 'site/atlas.json': '7d712a1f1e7d83d6093242dd0e9e12bb9d39d2183c33e4f7ffdecb2846caa327', 'site/rosters.json': '35cad326388607f1abac4e9efbd05dbefa1eb4a1a7b7ffbc1ed194a1ee56dc27', 'site/exports/待核对名录.csv': 'aa21299c3f87de06b9427dffad265e1f6de15a2a22d79be4199e41008592c350', 'site/exports/待核对名录.xlsx': 'a51eb8fa7b9f13d8e03849f6fab02121df894a2b81e560e435cc855c69d19047'}
RELEASE31_PIN_OVERLAY={'data/atlas.json': '28643e5c9a1d67007146dba8a2e6d410008deba5a5a1fcabdd10979f408fd679', 'data/rosters.json': '3e47fc6836bde53790d63b6c2c6347fad614ecff63c8548051398ef8bd7eb3ca', 'progress/README.md': '08db02455222e2e99629cca4c56490300d3f1df64733291b33f3f6567cf25aaf', 'progress/current-coverage.md': '375f389c9d889c6c3cbf6e7f0e9b025b4eee97d7a930fad1b7ebac4e23c602c3', 'progress/work-queue.json': 'd22c628ade740a72f063d7f0fe3570374ebdd881ef2d787330c4b39e5b51ea37', 'site/atlas.json': '47e92ca3f762d8921aa8bc6ab8f150c6d20d509d29bdee307cf5fecd6d263470', 'site/exports/待核对名录.csv': '0fba9ecbafaa02974d5af4d8c165ed6a4b135812e19f74d1dd3000cffaaf5231', 'site/exports/待核对名录.xlsx': '93736f1b3a20451a5622e99a42abc50c710af5322ea6c00fd582afc69f46969d', 'site/rosters.json': 'fd18bd4a98d291c4a441d4f1ac2ec7f7e4e684cf1e406965fa2c6a6cbd8fe4b1'}
RELEASE30_PIN_OVERLAY={'data/atlas.json': '7bcbb58ea605ea73fec2a51412850550533ba5617d3f200d3812d10551c534fe', 'data/rosters.json': '8be8881d52699b7417e5ae7e542629d64156744d524c581c856faf6172878313', 'progress/README.md': '83b8119bb351cc5fd50905314aed93d62d1d1e72b74b91a4c0d4afd9b6e916fc', 'progress/current-coverage.md': '5c7f1f00dadf7a6622c90ea9e677127e4dcf3b9416819ee09700087af870b0c7', 'progress/work-queue.json': 'be961acbf8eb14435379eb9a3fd61da45cab3cddce0f95593f00bf57837f861b', 'site/atlas.json': '8a2fe871c7262ffc0a2f3edddb5b970a27382b9f5b85797c44f29f3be7582e4b', 'site/exports/待核对名录.csv': '9b0ca81c0420ef1fbe844b63d99684ee8b2bfb1beafb873cfcb40185158a9dd0', 'site/exports/待核对名录.xlsx': '75ad1f8c73e2add290a15de5e4aafa82d857dada4352af0cd7089a6ba2e4a25d', 'site/rosters.json': 'c837c259317159de566137c0227866a1fd7224020afbe1e37ab515ffb8a4f0a2'}
class Rotation003Wave1DisplayFixTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.db=release25_view(json.loads((ROOT/'data/atlas.json').read_text()), 'data/atlas.json')
        cls.person=next(p for p in cls.db['people']if p['person_id']=='cqu-chenke')
        cls.original=strip_aliases(cls.db)
        cls.old_person=next(p for p in cls.original['people']if p['person_id']=='cqu-chenke')

    def test_01_only_two_exact_evidence_bound_role_aliases_added(self):
        audit=json.loads((ROOT/'progress/rotation003-wave1-release-validation.json').read_text())
        audit_digests=audit['source_review_gate']['approved_source_review_evidence_sha256']
        self.assertIsInstance(audit_digests,list)
        self.assertEqual(len(SOURCE_AUDIT_SHA256),4)
        self.assertEqual(len(set(SOURCE_AUDIT_SHA256)),4)
        for digest in SOURCE_AUDIT_SHA256:
            self.assertEqual(audit_digests.count(digest),1)
        self.assertTrue(assert_alias_contract(self.person))
        self.assertEqual([r['source_id']for r in self.person['teaching']],SOURCE_IDS)
        self.assertEqual(object_sha(self.old_person['teaching']),BASELINE_TEACHING_SHA256)

    def test_02_removing_only_fourteen_alias_leaves_restores_entire_original_atlas(self):
        self.assertEqual(object_sha(self.original),BASELINE_ATLAS_OBJECT_SHA256)
        self.assertEqual(json_bytes_sha(self.original),BASELINE_ATLAS_SHA256)
        self.assertEqual((len(self.db['people']),len(self.db['pending_people']),len(self.db['institutions'])),(555,84,39))

    def test_03_all_other_teaching_and_original_notes_remain_exact(self):
        self.assertEqual(object_sha([[p['person_id'],p.get('teaching')]for p in self.db['people']if p['person_id']!='cqu-chenke']),BASELINE_OTHER_TEACHING_SHA256)
        for row,old in zip(self.person['teaching'],BASELINE_TEACHING):
            for key in ['note','source_note','note_derivation','period','level','status','source_id','source_url']:
                self.assertEqual(row.get(key),old.get(key),key)
            self.assertEqual(row['role_source_note'],row['source_note'])
        self.assertEqual(self.person['teaching'][1]['period'],'2025-09-18')
        self.assertNotIn('来源教学时期',self.person['teaching'][1]['role_source_note'])

    def test_04_application_exporter_and_tokens_have_only_reviewed_layout_overlay(self):
        for file,digest in UNCHANGED_FILES.items():
            self.assertEqual(hashlib.sha256(historical_bytes(file,(ROOT/file).read_bytes())).hexdigest(),endpoint_sha256(file,dict(dict(dict(dict(RELEASE28_PIN_OVERLAY,**RELEASE29_PIN_OVERLAY),**RELEASE30_PIN_OVERLAY),**RELEASE31_PIN_OVERLAY),**RELEASE31_PUBLIC_METADATA_PIN_OVERLAY).get(file,RELEASE27_PIN_OVERLAY.get(file,RELEASE26_PIN_OVERLAY.get(file,LAYOUT_FIX_APPLICATION_SHA256.get(file,digest))))),file)
        for file,count in [('site/app.js',3),('site/rosters.js',1),('site/index.html',2)]:
            self.assertEqual(historical_bytes(file, root=ROOT).decode().count('rotation003-20261024-w2'),count)

    def test_05_generated_snapshots_recover_exactly_after_aliases_and_derived_build_id_removed(self):
        site=release25_view(json.loads((ROOT/'site/atlas.json').read_text()), 'site/atlas.json');roster=release25_view(json.loads((ROOT/'site/rosters.json').read_text()), 'site/rosters.json')
        self.assertEqual(site['people'],self.db['people']);self.assertEqual(site['pending_people'],self.db['pending_people'])
        self.assertEqual(site['build_id'],roster['build_id']);self.assertNotEqual(site['build_id'],BASELINE_BUILD_ID)
        site=strip_aliases(site);site['build_id']=BASELINE_BUILD_ID;roster['build_id']=BASELINE_BUILD_ID
        self.assertEqual(json_bytes_sha(site),BASELINE_SITE_ATLAS_SHA256)
        self.assertEqual(json_bytes_sha(roster),BASELINE_SITE_ROSTERS_SHA256)

    def test_06_roles_do_not_change_education_appointments_mentors_or_candidates(self):
        for key in ['education','appointments','mentors','committee_members','publications','research_fields','pending_education_candidates','pending_mentor_candidates','pending_appointment_candidates','pending_professional_fact_candidates']:
            self.assertEqual(self.person[key],self.old_person[key],key)
        self.assertEqual(len(self.person['education']),1);self.assertIsNone(self.person['education'][0]['degree'])
        self.assertIsNone(self.person['education'][0]['degree_awarded']);self.assertFalse(self.person['education'][0]['include_in_education_filters'])
        self.assertEqual(self.person['mentors'],[]);self.assertIsNone(self.person['listed_role'])
        self.assertEqual([p['person_id']for p in self.db['pending_people'][83:]],['cqu-chenrenwei'])

    def test_07_roles_preserve_cached404_navigation_and_historical_scope(self):
        sources={s['id']:s for s in self.person['sources']}
        for row in self.person['teaching']:
            self.assertFalse(row['source_navigation_enabled']);self.assertEqual(row['status'],'historical_source_reported')
            self.assertEqual(row['evidence_status'],'official_cached_body_read_direct_404')
            source=sources[row['role_source_id']]
            self.assertEqual(source['url'],row['role_source_url']);self.assertFalse(source['navigation_enabled']);self.assertEqual(source['ordinary_https_status'],404)
        self.assertIn('未声称2026仍授课',self.person['teaching'][0]['note'])
        self.assertIn('不是学期课程或长期任课',self.person['teaching'][1]['note'])

    def test_08_actual_export_summary_replaces_only_two_role_placeholders(self):
        now=build.teaching_summary(self.person);old=build.teaching_summary(self.old_person)
        self.assertEqual(old.count('角色未披露'),2);self.assertNotIn('角色未披露',now)
        self.assertEqual(now,old.replace('角色未披露','主讲'))
        self.assertIn('2025-09-18',now);self.assertIn('404',now);self.assertIn('缓存',now)
        current=dict(build.department_tables([self.person],self.db['updated_at'],self.db['institutions']))
        baseline=dict(build.department_tables([self.old_person],self.original['updated_at'],self.original['institutions']))
        self.assertNotEqual(current['总览'][1][6],baseline['总览'][1][6])
        current['总览'][1][6]=current['总览'][1][6].replace('；主讲；','；角色未披露；')
        self.assertEqual(current,baseline)

    def test_09_changed_department_workbook_every_cell_matches_unchanged_canonical_exporter(self):
        from openpyxl import load_workbook
        people=[p for p in self.db['people']if p['department_id']=='cqu-architecture-urban-planning']
        tables=dict(build.department_tables(people,self.db['updated_at'],self.db['institutions']))
        blocked=build.disabled_sources_by_person(people)
        book=load_workbook(ROOT/'site/exports/cqu-architecture-urban-planning.xlsx')
        self.assertEqual(book.sheetnames,list(tables));checked=0
        for name,rows in tables.items():
            ws=book[name];self.assertEqual((ws.max_row,ws.max_column),(len(rows),len(rows[0])))
            for i,row in enumerate(rows,1):
                for j,value in enumerate(row,1):
                    cell=ws.cell(i,j);value=build.clean(value);self.assertEqual(cell.value,value if value!='' else None,(name,i,j))
                    expected=value if i>1 and build.valid_url(value) and value not in blocked.get(ws.cell(i,1).value,set())else None
                    self.assertEqual(cell.hyperlink.target if cell.hyperlink else None,expected,(name,i,j));self.assertNotEqual(cell.data_type,'f');checked+=1
        self.assertGreater(checked,250);book.close()

    def test_10_all_110_other_department_and_roster_workbooks_remain_byte_identical(self):
        self.assertEqual(len(UNCHANGED_DEPARTMENT_WORKBOOKS),110)
        for file,digest in UNCHANGED_DEPARTMENT_WORKBOOKS.items():
            self.assertEqual(hashlib.sha256(historical_bytes(file,(ROOT/file).read_bytes())).hexdigest(),digest,file)
        self.assertEqual(hashlib.sha256((published_root()/'site/exports/待核对名录.xlsx').read_bytes()).hexdigest(),endpoint_sha256('site/exports/待核对名录.xlsx',RELEASE31_PUBLIC_METADATA_PIN_OVERLAY['site/exports/待核对名录.xlsx']))

    def test_11_alias_guard_rejects_every_added_leaf_mutation_and_cross_source_swap(self):
        paths=[(key,)for key in ROLE_KEYS]+[('field_provenance','role'),('field_status','role')]
        for index in range(2):
            for path in paths:
                changed=copy.deepcopy(self.person);target=changed['teaching'][index]
                for key in path[:-1]:target=target[key]
                target[path[-1]]='unreviewed-role-or-source'
                with self.assertRaises(AssertionError,msg=(index,path)):assert_alias_contract(changed)
        changed=copy.deepcopy(self.person);changed['teaching'][0]['role_source_id']=SOURCE_IDS[1]
        with self.assertRaises(AssertionError):assert_alias_contract(changed)

    def test_12_validators_and_export_consumers_do_not_mutate_inputs(self):
        before=object_sha(self.db);build.validate(self.db)
        build.teaching_summary(self.person);build.department_tables([self.person],self.db['updated_at'],self.db['institutions'])
        self.assertEqual(object_sha(self.db),before)


# Exact layout-only overlay; all original source/data/application pins remain above.
LAYOUT_FIX_APPLICATION_SHA256 = {'site/styles.css': '3b01ec6a5674982d048237e5426aa107bd622662d2758913c81bc6f5c4c0ceca', 'site/app.js': '5ce1dbc7161a048ab263cdff313bc904544b362c13d39cc5963886b409f037e2', 'site/rosters.js': '7536ef08c4032e05e1ad3c09532858dd42fd68c20968c82e2146481cf6d9c85f', 'site/index.html': '7e6331d4846c13d64f0a5b5b65a9d52539df537b2ce20ef26563669739f8f2a3'}

if __name__=='__main__':unittest.main()
