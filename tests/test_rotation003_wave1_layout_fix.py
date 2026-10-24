"""Offline exact-boundary tests for the source-unavailable wrapping-only patch.
No network, browser, build, or output writes. All prior source/Excel bytes are pinned.
"""
from release27_history import release27_view
from release26_history import release26_view
import hashlib,json,os,pathlib,re,unittest
ROOT=pathlib.Path(os.environ.get('ACADEMIC_ATLAS_TEST_ROOT',pathlib.Path(__file__).resolve().parents[1]))
OLD_TOKEN='rotation003-20261023-w1'
NEW_TOKEN='rotation003-20261023-w2'
CURRENT_TOKEN='rotation003-20261024-w2'
RULE='.source-unavailable{white-space:normal;overflow-wrap:anywhere;max-width:100%}'
TOKEN_FILES={'site/app.js':3,'site/index.html':2,'site/rosters.js':1}
def sha(data): return hashlib.sha256(data).hexdigest()
def read(name): return (ROOT/name).read_bytes()
BASELINE_FILES={'.github/pull_request_template.md': '01cd056e32e38dbae95c832514c767794de5f3d622ccd87c562206fe6d2e4dc1',
 '.gitignore': '7a367ba9154c09a2e6024ae5bd47fd53f007a3b14fa921148f2a61bdcac0a980',
 '.nojekyll': 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
 'CONTRIBUTING.md': 'ef6c454d1ac0cc703740a114aaeb6702d935d73a09068cbee02a02b5668b2eeb',
 'CONTRIBUTORS.md': '83000cb356c73a64da6662f1d562c9630a6b8b3dbec4c8e57b0766b467c44a1e',
 'README.md': '918d28a28aa41a9455b82c2032721b421d0f3b3fae62d1200b0dbbdde6b9431c',
 'data/atlas.json': 'c091ec997338745db522e4e5434836359223fde281b29c0d7bbf1ee0f4856df8',
 'data/rosters.json': 'fc08f82cf0a161d7ca8882151afcad6a0a7d5be88a8b56b936a6d055e997045a',
 'docs/ai-contributor-prompt.md': '60230dd1ef9babaf12163f3dec45d0b67d569a7e3dca0f8de3ce96013e4dda11',
 'docs/architecture.md': '6151806b5fdc1de092c6313a44acbce476b3d33fa42387c2182d5613757b40a6',
 'docs/continuation.md': '66df6a3efb29bafe22cca7d684a466e2dea4c20c27e7c78689d29cff0553f06d',
 'docs/data-policy.md': 'b9833d739f4c0c21cda591f58663a05437c2665dc71ec2a003a99a6e6c07376b',
 'docs/multischool-data-contract.md': '07d32e75f5f2c9ea3b6a0510b87526c63deea1cc5547bd4b89a4dd1599ac4eec',
 'index.html': 'c6df387c9b91b29fba682334a6147aedbfd279685690d5521c6dc3b678298d17',
 'package.json': 'eae4ec92d1be1f7aefb06be1dfc57f7659520e869ae4fb817c7702d1f57b78ac',
 'progress/README.md': '02b814d9388f0290c7599bc320568edbda05e5262375e9e80a93c0e0310e52e7',
 'progress/bit-rotation003-wave1-coverage.json': '1b4d18aa73eab058c4caafa229874ec1a5227e04df4862e374776038f9b407bc',
 'progress/breadth-wave1-coverage.json': 'f1e9a5b08e579f8cd4539f627581a8db963af4c8ac3c48fe05da1cdf4170cb6a',
 'progress/breadth-wave2-coverage.json': '49ccf0a7eb577c5347aa6d0b3cfbf5a9d48d1cb881d0f3610fa9988b43e42b5e',
 'progress/breadth-wave3-coverage.json': 'fc016bbbeb901f4ac1ecf1930d0fac91411815c6fe08615315f0224d91ee1562',
 'progress/cau-rotation002-coverage.json': '40372503c3956a40c271ab38fc7a8a90630680150566e04b5910e9769b0e82c7',
 'progress/cqu-rotation-wave3-coverage.json': '7ec5cdfb192985f503acb7e4c3068905335dd4dbfcfdcea2aeee35b16c61730f',
 'progress/cqu-rotation003-wave1-coverage.json': '2888295c4c423303025d979b53497ef1e66ebbb92d14d5bca84dce8f5990e446',
 'progress/current-coverage.md': '1b228011e7f1b3823c18d8a771ed46d2e03a5318cd5a662f0cfbb1bfea710807',
 'progress/ecnu-rotation002-coverage.json': '15e34271e854cf1324d59958e4d4ee0e4b5d8ca44fb569a9888561285f537c8c',
 'progress/harbin-communication-coverage.json': '2472ca03ce368e06cd9535de8a164ccc93e607a7e34f0507b500f478a5929bc5',
 'progress/harbin-electronic-engineering-coverage.json': 'e588cde0c2ca5fe9fdf304e3c28a1a656e43d4580c59130dac3c49bff31c66ae',
 'progress/harbin-information-coverage.json': '8e3fee8f2e9017209dde8e98dcfad384012bf2178ca6628ad096c8c90f52893f',
 'progress/harbin-information-progress.json': '269ecf28236b67e188b1cb51d24ab23bc8f75551ca65043d84ed490d98a9544a',
 'progress/harbin-measurement-coverage.json': 'cd2564341781dfbc8cc0323f2b10a74dc4977962fb8e8bac8536c843057a268d',
 'progress/harbin-microwave-coverage.json': '670bfed6ebbd0a86a57b18726e10e1a6688c1f03b355d3af1f7017ef66161821',
 'progress/harbin-microwave-progress.json': '97dc4937aa435371207950089d05f8cb656513b11c5cfc174aa51340746becad',
 'progress/harbin-seie-coverage.json': '13f65496a340f7ee61044f9ac1a4f98eda3afedb9cb2e1e8d71621e47765c23d',
 'progress/hnu-rotation002-wave2-coverage.json': '82d63d6ad3ba1bdea1f38f0725d6416ebff647f5226ea2351a3516a94d456437',
 'progress/lzu-rotation-wave3-coverage.json': 'ab34fd56ea55a98f25dfaaabc150a951ec37f4d83a40086304dff6bdf77f26df',
 'progress/multischool-first-coverage.json': '1753e1f6576e8b7d905756bfc5832f4ee3b1a1fee8c6eda1b43b0ff7c2efd171',
 'progress/multischool-followup-wave1-coverage.json': 'cc8563cf87b065041743a292803bc1e9ca8b25f56325188758b3a0f0b36167c8',
 'progress/multischool-rotation-wave1-coverage.json': 'a1d557d578bd553cc2aec4ec3075157f526f1e224af9592a592e110feb285aba',
 'progress/multischool-rotation-wave2-coverage.json': 'e3c9113ebe5d33542d3cc758e5cd32202f0fdd2cefed4160ac2c4256e5124fdd',
 'progress/multischool-rotation-wave3-coverage.json': 'f2af83a8d823f7e0fe1937016d6ee6b49123dd8b001d358c8f64585c8bd3ecd1',
 'progress/multischool-rotation-wave3-release-validation.json': 'c51cc1e0397d2d555c537f6825835b8bf7f4839eaf375dfff5e324404169c9b0',
 'progress/multischool-rotation002-coverage.json': '8d8fce3fbbe8d69bbceeb8cdf34f832971bbdc974af975168c6e467460015dda',
 'progress/multischool-rotation002-wave2-coverage.json': '056a9ffa47b7880c6912cc0643fa763dbcc45bf7be1d7eb0b1bef0166db79fe6',
 'progress/multischool-rotation002-wave3-coverage.json': '9fcc7e9acfa22e8404b738399bfd50a28de43da5e26d370533c57cd19c345eb2',
 'progress/multischool-rotation003-wave1-coverage.json': '3d33a0116dd2718076feb4dff5b33106ecf5d61be048d605914a9ff96b87b633',
 'progress/multischool-second-coverage.json': '586e36d2a5cd100e02650a14216417ad95287e5125b8bef783fc8f2dc3be47d9',
 'progress/multischool-third-coverage.json': '9cef7746388d35e0bb2098b3259b9368af6b2991218b2d246412399f4eff2222',
 'progress/neu-rotation002-coverage.json': '6ee1b42f2ce944b681491fb83a2b5ec97d6afecb77f89c74d17578e2637643c9',
 'progress/nju-rotation002-wave2-coverage.json': '8b64607127148e3c454fc9111e7ca14170b9f41e6fa1416c0b6e2b1b3c46aea8',
 'progress/nwpu-rotation-wave3-coverage.json': '0292c35fb287e81295426192e74bb5397d65614523b931de328ee85b06675bcb',
 'progress/nwsuaf-rotation-wave3-coverage.json': '7a7d24641b082e04b10a72d1c01cce92ceb0ad3bb37523406772b66c327f44b1',
 'progress/rotation002-release-validation.json': '886b1ca01924f6da6d68828422efe7b4108de70b3639e9abb349a334c447feb2',
 'progress/rotation002-wave2-release-validation.json': 'f2982840353e29dfb875548efd8d4388112d75e79ecd92218aa1ae74be7b47b2',
 'progress/rotation002-wave3-display-fix-release-validation.json': 'abed7e0cca027a6c0be651392cd375300631e84afb0f55590d5a54a588365c78',
 'progress/rotation002-wave3-release-validation.json': '7bb729c22fb9707f1980d34a8516197392df953d070380b0753c90c1e9a0d2a1',
 'progress/rotation003-wave1-display-fix-release-validation.json': '7343e982aecd8d3a00e3ed75599715929ab66b0b29908536034a2f1b20365491',
 'progress/rotation003-wave1-release-validation.json': '95ce2d22b9c2ed388a915623d9c633902522b013ee60fdf2cbb162fddd3c4787',
 'progress/scu-rotation-wave3-coverage.json': '0898cd9be33ff67f9ab42f8fa03b5e06d97cc3dd59c7a0db9fbfdf6dfad783b8',
 'progress/scu-rotation002-wave3-coverage.json': '6163aa9ad0ff21e057ea4c532493c017a3c3eeefa94f9c5c804c5d6d9c641266',
 'progress/scut-rotation-wave3-coverage.json': 'edcf4f766e66517d100ee529213e2da9c6707fa02f74e9e8ffabfa2e0f666200',
 'progress/sysu-rotation-wave3-coverage.json': '3cb6ec3ace6cd350146a6c6998cc5e06674a06c884f7f4ceedb3bb4aabaca50b',
 'progress/sysu-rotation002-wave3-coverage.json': 'bad43a636a993c3fa7c91f4458af623dcb7f4a7b486ebc85f69ccb538972bf97',
 'progress/tongji-rotation002-coverage.json': '2d8a260951fdef8c50f395b1b0c5bffd07f59a4025e91b4098f061d52da431af',
 'progress/uestc-rotation-wave3-coverage.json': 'd1a482424a906fddf5f0b2e7e2f8ddc9a44db2ac0b11d242deeeb0d66f6d0649',
 'progress/weihai-information-associate-progress.json': '76f5d4c76db39005008949a8e60c42a4ce80c73ab1c16ef1e8fe3eb515b0da83',
 'progress/weihai-information-college-coverage.json': '0547fc6b5b5084fe150de234a43ba9f7407fafdb6a34d6d9f4ec9fafe340f736',
 'progress/weihai-information-lecturer-progress.json': '1e7d6adbcff351536560da0c27e34ec660473a57baf5ff0e65cee7d0ae81b127',
 'progress/weihai-information-professor-coverage.json': '1de2a227fb08a1c1a8a103037b6596fb297423aff6c947ee675dab4a1a531696',
 'progress/weihai-information-progress.json': '968892c7e11a38ccf61ed5e4af2107e980293f1e741ea94d49fb13513a952822',
 'progress/weihai-roster-corrections.json': 'c4564d3bbf2ea657a51833597f3ee36cfc609de50e291a229556751c90be57f2',
 'progress/work-queue.json': '8a5ef9905b30747157ecb120a80f12eff23f410d098bc97cf95012ca781a154a',
 'progress/xjtu-rotation-wave3-coverage.json': '130d3f48d17e6865c92ffd1392bee7baff5ac334a5b20e6069ed8fcdf779ebed',
 'progress/xmu-rotation003-wave1-coverage.json': 'b090533c8230d5d1474b994e862b048a0b12d51706680ace549fc968cb7bf639',
 'requirements-dev.txt': '87458aa5a1a141cede454586ef064335252f0ce11ce7fe9d677eee06ee851bb4',
 'requirements.txt': '9bba605fd7b6ea23038de15e5a1ae6714b3d3fb14ed2d6e6bedbfb0665ca2122',
 'research/coverage-work-queue.json': '31ca96320088db15b00505c868af511f71ce9d5683bb7f91a6d3ea1e350a690b',
 'research/coverage-work-queue.md': 'aee4b58f8cdb8a11c9290f850523a5ba573e6efae1377e7d63383d873b1c2402',
 'research/multischool-rotation-wave3-build-export-report.json': '28c82e33ceec7849ad3b1cbdc51ade378387632e0762547ebc1549fc3af0ff3c',
 'research/rotation002-build-export-report.json': '38d7b1cdfefd9a02ad3dee35c3562d5c2b08f6dc1269a0fd23b25b44d0789b1d',
 'research/rotation002-wave2-build-export-report.json': '1fb8915979ef64cb9a9ce535598c68e9528020fd24b5192fbddc870fc8270d43',
 'research/rotation002-wave3-build-export-report.json': 'de5c02d7e8e8b8fffaaaa8097717f863624c0767e95c24fb31ac4e561027c06a',
 'research/rotation002-wave3-display-fix-build-export-report.json': '37fb600b820f0be2cd47853fafbde70193762e251e2668539e94389e5a787580',
 'research/rotation003-wave1-build-export-report.json': 'aa92df54da60fd7ce0643e474d9907479dd8474cf03937be3ebc9382c90c7e1e',
 'research/rotation003-wave1-display-fix-build-export-report.json': '72f7327707be2ee55130c57623aee00da5d79724c55a2a0467be527a8237a735',
 'schema/atlas.schema.json': 'd6e4a49fa200cce94e5b1da8e70e1ab30a9f2bf6aad8e7203a6c0626f06eccae',
 'schema/work-queue.schema.json': '2f4676b2993b8f472f86e3e777ebcd381c8f22b4b62ce2ee5ed382ad4a33cc8a',
 'scripts/build.py': '1bcd28d7c0f3766a54c2cae980add674f1eb0603df8b9dd8958d1c59634b6bb7',
 'scripts/build_rosters.py': '29c5dee611bfaef3fd6afd1df9480b254652c51b1c4ce1c9568d75cb799319fe',
 'scripts/deterministic_xlsx.py': '65158f54d001eebb2ac586fd820cd69deed8e5c96ed5b117668ced51c11dc300',
 'scripts/validate_queue.py': '613b769a1612e274921284aa52bdd12742dc3fb140b94e3b98fa005a3f3fe60f',
 'site/app.js': '5d4efe8a3c85cbca0125b950a70d7494e3d34a2e67240e6043347903965c8d4b',
 'site/atlas.json': 'b53c075a6e4113c6d82957835d85d6733cb9ba45c42e2a5c72cb9fcc414499c0',
 'site/exports/bit-cs-image-perception.xlsx': '8ecc8beff095f5f5d11220ad0b50ec47695fdae46b9869cd73e08d2f665b6732',
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
 'site/exports/cqu-architecture-urban-planning.xlsx': 'b8b861aae0f7e2a090a473c18eab98af431c571ce126a6d285cac42623a676a5',
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
 'site/exports/zju-ic-manufacturing.xlsx': 'e683c104495e43aec93846c5d8767bd1040e0a135592c1003526028ed03262f9',
 'site/exports/待核对名录.csv': '998bf7df5b41722203dedefa7952fac38119815f50a562209b9624eea5805934',
 'site/exports/待核对名录.xlsx': '5e3dbea0ad5139f5cc180f4084de942375c89d63b92c0e8d5a6aa0c1c146582b',
 'site/index.html': '3b5f7afdd4ac96aaca402884976bccb33cb9a1d2a1ad27793cf7cdd82e5970bf',
 'site/model.js': '9dbc155288c1ee0a93fd5d11cd8a7c63724dc0bde6b117a2f71d327e34be3fef',
 'site/rosters.js': 'e4bb3c53da7a4ff3c00c1109651d66cc479c20dc265e7705e41213e3019a3502',
 'site/rosters.json': 'c9ee602e74636e0253cdffc0df814c1048e26784a8954a4c42c67d9a826053ad',
 'site/styles.css': '6063be4c04726d2dcf01a0442d5dc4d763b99c835a4110bd943799582c14fc34',
 'site/universities.js': '9323dad42fc2c35808ad92888cdffb0ad41edaefaee88c3b57ebb798349c2d62',
 'tests/asset-version.test.js': '62b123873590b48ef158516ca2d571c977a99dc0c8cf97aed8c3783c8f8ac427',
 'tests/breadth-wave1.test.js': '689aae907ab672c444aae5c0981b5c28c890ee6818be4dc01e78427591fd0f5d',
 'tests/breadth-wave2.test.js': 'c06c00b94b18685bca1a98b6cd584ea414a7b83b3bea0343e80af9c9e6322269',
 'tests/breadth-wave3.test.js': '95fb6970715b05bc4522bc7cde140cff4bae3f06a2647241a3d0d2d559effc91',
 'tests/combined-mentorship.test.js': '6c24b5f1852bf614f7682b4934fc590546900d0e692ca54fdcbd8451ef03ee24',
 'tests/fixtures/multischool.json': '527af50bb527afc0f1a2631d4c55d78939b99bff3a54196954a3eb1330df916b',
 'tests/fixtures/project-guidance.json': '051e8e7617bbd42c2cd2fb335a805f74087b6730922ef03ae598a937a3ee0504',
 'tests/information-final.test.js': '0650e06c242093657c2f7264c58eabcbb742d313975aa04c1d18d2d3dc8e34b4',
 'tests/information-first.test.js': '2cac68199b6abd2fc75d893d49656caede409660a93e43860e46ac7df42d72a7',
 'tests/information-second.test.js': '773ce9bc63b39353647fab8a2ddd98056e1f917bfd11e4bfc76706dc06853ec3',
 'tests/mentor-navigation.test.js': 'e5db96af50b9a6b17be1dcc5dd4cab6b67d1c161af85df8b4fface7aca311075',
 'tests/microwave-first.test.js': 'f4a3a61086f38848dfc18c64179d72eb4b35bb192f0993f963c64a7c585a7f59',
 'tests/microwave-second.test.js': '5c8be980152bac8c9bee55fabf1080c9495d02f3040cf09934882beef3095245',
 'tests/model.test.js': 'dcfd2cffaf8474b80ff7b8c84df0c7839c167b598830b5c46ec86be4af4ae959',
 'tests/multischool-first.test.js': '01e3daecc20e0b91af344066207a30e79bcfdf102b115d33f8ecf5faf13da509',
 'tests/multischool-followup-wave1.test.js': '9625405be807bedbf3f1766dc83860ddea11bc7a7e6113a91504ef90c9d99169',
 'tests/multischool-rotation-wave1.test.js': '07dca0ea62b7b3062cde40c131c18c474a6ba2807e339ddf89cd35f03ab045ec',
 'tests/multischool-rotation-wave3.test.js': '2694aaa40238c85f9794345ef536db144fe5936c5f6b97de639c7019e9117aba',
 'tests/multischool-second.test.js': 'a8f759eb0cb50f3bb6fb7fb1f3bc5bb4a51aef55ff5a2e6fef866aa697ecb739',
 'tests/multischool-third.test.js': '090a0c29c9166177da1312565fca5764cb41fccde5b393a728deab85326b447a',
 'tests/multischool.test.js': '7693abc87905db7f516db88b31ec9d6ad5e76398ed423bb59247504a8738691c',
 'tests/new-schools.test.js': '91ed26d8146771d00cde211b6b7de296e6481e146a1e643a8c4f0949a73f161f',
 'tests/professional-guidance.test.js': 'e435f716352a859504b491af156b0bc712eb572d4a0a18eb189f722cf0ed82b3',
 'tests/profile-mobile.test.js': '837692822b7735bd3cbf281c026872a277254191f1ab0a46915e5629d5dae6ec',
 'tests/profile-source-labels.test.js': 'ea4f0efd929c734155675bc60bb831e70ce9c03c7319589b66968243b26a1332',
 'tests/project-guidance.test.js': 'e9e6a79358c2de41111a4a5d02f3aaf3722117e6b37d113f735eee5d4886002c',
 'tests/release-assets.test.js': 'f8f034602cd4759d5a4e5d161b6dfe421bbd0c8435c5e89f4af61f3854987a3a',
 'tests/roster-pending-status.test.js': 'b02be5d85dd1660f6b1980c5418b9a48660e4c817d74c6db076d208c93749420',
 'tests/rotation002-wave2.test.js': 'b3b4600dc9407bf091d6c4057b65d65944f8151c551825e7c9c2aac1be6478c6',
 'tests/rotation002-wave3-display-fix.test.js': '0ef350bfca0e1e8a0e8779d346e69d4be3832eb4c9591ead415a2dd60cbbd908',
 'tests/rotation002-wave3.test.js': '2339096aa87b004b71ab14b16480fb2af314022ea172f8b370ff1f143b76bb28',
 'tests/rotation003-wave1-display-fix.test.js': '6be6cec6025535066ba941ca366a8d482975f9cdbbb014caa7611382ecdb96a3',
 'tests/rotation003-wave1.test.js': '330958c53c65bd30d8b9cf1ff3745643c185b87c7123e784114207770dc1ea42',
 'tests/school-scope.js': '1eb5aa52bafc2fceb1e7679c721bb0d7f0a47e1a886823ffff4b149b691d9fdc',
 'tests/school-scope.test.js': '496c886d92d5f8f8ccd7bf093b803fe5795add4b6a09e23692ccafa947f86046',
 'tests/school_scope.py': '24809fb70c05ac6e37a40812f89fea6926c5b2e6662f2db28f4c633157336ce8',
 'tests/teaching-facts.test.js': 'fa7f54b1549fa12b032ff1d02e68e09a85f43fbc1f597eae34075bf2f4da061f',
 'tests/test_build.py': 'f3e3c2ac3475a744ca660000b44c6aab3e16ba6951166205ef7f4efe7643ddb4',
 'tests/test_combined_mentorship.py': '129c16b8b81bdca57f032e333a84c76bbce81aee6872a68445467ee92fc3ef65',
 'tests/test_deterministic_exports.py': '9ad44d0c3feff81f259ed9ad156b4c1430bb6a70e82627cd09331c6998d97743',
 'tests/test_information_final.py': 'a67415e8b69b66c1ed52b29f15a0dae01f546a290532e92547196dfb6bc20c50',
 'tests/test_information_first.py': '3c65b5729ee33bffc3a8f3155bf8cb8bd5a79722c473a66bca4b792109612159',
 'tests/test_information_second.py': 'b2856979ea264687674ffc70dc31fbd517fc43e529d60ba56e38c2b59c80a614',
 'tests/test_mentor_navigation.py': '92f9ceb2ea0965548e665c8440a8cfe908ed4dd141af58cc808c542abc6bbfae',
 'tests/test_microwave.py': '55ee09c4758ed8f3efc6fba72a50cb8b7184a4d75afba459d3424ea37b655432',
 'tests/test_multischool.py': '0eb8ffdae2e5cc68b3ca1d943d34adfbf884afc29808d7d2edc9ac15301268b7',
 'tests/test_new_school_guards.py': '583de5c747877592fca03d4693876393d643eb169ad4a32c1f3b4135055d3784',
 'tests/test_professional_guidance.py': '4be210539dab312cddf1aebb20861c36c9522570dbdecfd241610014099daf19',
 'tests/test_profile_source_labels.py': '5f16f3ca6663f932a6e60a4c7313e017bd29c153fc6519125708c246f0a92dcc',
 'tests/test_project_guidance.py': '99d9f8d2b54d7fcf26ce168ffaef71b241255da0854e581cacf5df8abe52f309',
 'tests/test_queue.py': 'a91db82089298a8394ee0718d915b3d806c3154a384d1c12923cf2dcd508283b',
 'tests/test_queue_date_precision.py': '6217aa6e0c648e5f849560a090648a2083b660c30a75968de0271da7d05acbc2',
 'tests/test_roster_batch_two.py': '932c740208a48ef467f27a5a7a59415ad643ffd1d26a6f4a846751623462a01a',
 'tests/test_rotation002_release.py': '522c100ee1cccd206552fffc8d091d43c39dbf497e6adbd9116c8ccabbeba931',
 'tests/test_rotation002_wave2_release.py': 'e9467990020cee0dd37263d1b2d9d8569d15980b0ad8c7d64a585e6588461399',
 'tests/test_rotation002_wave3_release.py': 'e9dab1811d8d34b62a131b9dcfd6ddb026fca47b92b400b6d88e4ac80344cdea',
 'tests/test_rotation003_wave1_display_fix.py': 'd91cbe4558dd80a2b473952b3719d1c325168df839be61f4f332c5e1b6c4a695',
 'tests/test_rotation003_wave1_release.py': 'dc84db2fcb64636e3590a9fa85f07cd67c6801ac00582f9032aefc7b5dde4de0',
 'tests/test_rotation_second_wave_release.py': '965610ed8b8603a6d799ff350632eb700b7cc83de2ec519c2787782a18123eba',
 'tests/test_rotation_third_wave_release.py': 'fe674134399cff9e759c691b49d997070bbeb8686291d8979a6b5046dd95f631',
 'tests/test_school_scope.py': '41b4ad240a4f87c0df0fad8872462f2e090ebc20f55ffd4ef3fc75b8b053d487',
 'tests/test_teaching_facts.py': 'a217a2ef1e9d0222f6d45564739a3c50f92aa36910dac80060725f0bb4e34836',
 'tests/test_weihai_associate.py': '17b4334d04efeaaff00fd63f251c727e37aeda2dae9a6ba9d2cdce207bd26a3e',
 'tests/test_weihai_final.py': 'cf80e25c8b7adcf5dfc8f21f79d59cec99cd5c3e1a61e45eb1fa7d17a35e7b47',
 'tests/test_weihai_first.py': '36e3d20a68d941773ac0190247fa4cb004736333d85a36f06f7e8a062084ccdd',
 'tests/test_weihai_professors.py': '862d294d821cf03e53cea103c017192501fa55ff2a98d7060c86a1b4403c4356',
 'tests/universities.test.js': 'b782fb1fd4eb91551c1e077bfd36aac449fd201dbe6a9b4431861599d0fcf65e',
 'tests/weihai-associate-first.test.js': 'f3a2e5fdf6afee067a6a50367f8033efb62eb4176339b43b943b13edd0d77e1d',
 'tests/weihai-final.test.js': '9f8aa4218df66dc9ec5503f48de11001388b3ac61f15cc59a2e5bdb6556da4a1',
 'tests/weihai-first.test.js': '8609b99af6651cc907ff6927571d98e2ba03db68acbbc812a567ab7f87a759ee',
 'tests/weihai-second.test.js': 'f79850bf9faa391687e12b2eed65f9ecd6eea1dafb03d392c1fec65ee53adc62',
 'tests/weihai-third.test.js': '031074839c6c59ee56b9f76279bee0595fbb2b2eaa7f397b7052347edaaba216'}

# Exact data/coverage/export-only release26 endpoint; all historical pins above remain.
RELEASE26_PIN_OVERLAY={'site/atlas.json': 'f0f46d4cba67eec805f944e2bef431120b38016465afcdd1227cf6e7fd4a6861', 'site/rosters.json': '509f98b11edd2fdfe3a80ef1b0de0d07d46d2f186ed29c363e3e8ebe293168b0', 'data/atlas.json': '4a2caaf803967d671bf0bb6b3aeb7c661eecaa40e7bf74e31c214215a3fecc93', 'data/rosters.json': '0bcddfc6661b2926ef1560b9ffa689fe37e818e1c821abf54dd0de962f1a834f', 'progress/README.md': '3226f9521575934bf9d3a193994414280f654e41bf61d56826ceaff127cebfea', 'progress/current-coverage.md': 'f0a89a29a14b88781880555e01df0ac280d4a59a6051363638725d46cd1d0c44', 'progress/work-queue.json': '829169fdf8815ddff328d1a3d324ad102bd52b0220a6025277e8d9fef8ebdaff', 'site/exports/待核对名录.xlsx': '6e01fe76a8b3620f51e3a0ec68b27d1fa5a81ff3427ddfb266efd2e03235176a', 'site/exports/待核对名录.csv': 'b8d625c46e68bc8ed171c6184a760dda8943ecdb323e70db025ca7f1f9507338'}
RELEASE26_ADDED_WORKBOOKS={'site/exports/lzu-civil-engineering-mechanics.xlsx': '6332c787a78aafee8b83c18768fb99fee29b6c8f121d182ebd1dca22bb86efa3', 'site/exports/nwsuaf-life-sciences.xlsx': 'ecbce0ff91b5f0e626ec1e2062e971aab36e51c7bc1724c67e515f8b763e443b', 'site/exports/xjtu-modern-physics-astronomy-preparatory.xlsx': 'f73df1a620894c105fd452b3e29742e66b0c8f25d8d277ec8cee3778f9286ddb'}
# Exact release27 endpoint overlay; all earlier golden constants remain unchanged.
RELEASE27_PIN_OVERLAY={'site/atlas.json': '1d2e8210a0ca6d60b874d793bd77e49de7da6f845493eb6912b0f4861e57afa2', 'site/rosters.json': '4971f6b3812c6f8d133fd0aba909e65f2209b72cfb0d37e668c62531ec0446cc', 'data/atlas.json': '602e459ef4bc62aa839e8eff7475819f5a6672e1492b1181ac9188372fe9d1c5', 'data/rosters.json': '217716511dc290970fd8708af5cacebaf5f1343b1ec671515b5048e5f81dabec', 'progress/README.md': '08617604707fff4e8121cdd13b08ef3a92e96aa1df2b38cc9cad9f91cc5b1cc6', 'progress/current-coverage.md': 'f92a7728e5c329e0c203fa1c04910d485b496c83f1756728bf9bbd5dc7b55d4a', 'progress/work-queue.json': '88037ab5e76bb2744eaa5b5dc9601d5e1e375b31e3c3f33116e8eeb3a1fd1f60', 'site/exports/待核对名录.xlsx': '9100c6cf6a1a5b6128737e49ef0f79efa49779739efd11bafbf12dfa05917972', 'site/exports/待核对名录.csv': '2e14625fd76a04d5fa29ee4621669dd8b496ca26fbabb41df20043169f1fa78c'}
# Exact release28 endpoint overlay; all earlier golden constants remain unchanged.
RELEASE28_PIN_OVERLAY={'site/atlas.json': '36fe06b748feef6919e105ce3fa81c58426b43d8374ccb03b2d828960462ed8b', 'site/rosters.json': '84edc29d2a70ef04d809effe8b3757cba2d614d469691bb16a8ce9f711b052cc', 'data/atlas.json': '184d94676b19b55d24d00b9c6056748a3a778754dd920a1a126be21685168d61', 'data/rosters.json': 'eefa9fe9add7c8dd9aaa49b81deeda73e51a8a1b214a9a6b3a26a2429110de29', 'progress/README.md': '7db1b1af415d5ea1086b76c6253dd91bce89abb330cfaa39ce63bae45f2f2045', 'progress/current-coverage.md': 'ddd946e215da974b867a2da0816b9fc4d36758b18d2a4f99085e1800978665cd', 'progress/work-queue.json': '157958452c461dee7d1fced71e8c8260d09ac2548fcc262ebd7d01c34b4f4d7e', 'site/exports/待核对名录.xlsx': '0482a9b49535e69a633ac7e4a25920232525e1fa34a5c770b53bd8757aa55c1b', 'site/exports/待核对名录.csv': '62ead57bd26f1d29fa26ade92aa5f021937354f31427867b1b433ba25d15bd32'}
# Exact release29 endpoint overlay; original constants preserved.
RELEASE29_PIN_OVERLAY={'site/atlas.json': '4b976d4c2e4a5b0beb1c838263ade37ece4fd8b5561ab8517d8ad83e13ca0996', 'site/rosters.json': 'e9ac62ce2ff63201b443717af9da4468d449521238dcde53c79fad7e9676c904', 'data/atlas.json': 'e2cbfcde9c8f96ebc9e96a0829fe95698428b672fd611ab6dff1078eafa75303', 'data/rosters.json': '854ff13b8c352b68a51a20c1cd322f638664de68fdf4996bb922dc344250d11b', 'progress/README.md': '943924d756b71e5c0bb3b6057faf1bcc30193b0bdd1733cf5fe986e6bf1466cb', 'progress/current-coverage.md': '467b5664162ff2a1fbb17b9c71b80038be3bffbc24602cbae9c84dc0b63add5f', 'progress/work-queue.json': '6ce290b467650489cfc260a27ece315a6efd86442af058f4a8558f8a3dfca359', 'site/exports/待核对名录.xlsx': 'efc5aaeaefb8c9e73f726619db2a09cc8d17f4ee1807be879cb5f16cf1e3eaa5', 'site/exports/待核对名录.csv': '99ef76904dd171f877c9a442e9d338badb15ac68e4b3ec145b71462234eb9017'}
# Exact release30 current endpoint pins; all historical constants and assertions remain below.
RELEASE30_PIN_OVERLAY={'data/atlas.json': '7bcbb58ea605ea73fec2a51412850550533ba5617d3f200d3812d10551c534fe', 'data/rosters.json': '8be8881d52699b7417e5ae7e542629d64156744d524c581c856faf6172878313', 'progress/README.md': '83b8119bb351cc5fd50905314aed93d62d1d1e72b74b91a4c0d4afd9b6e916fc', 'progress/current-coverage.md': '5c7f1f00dadf7a6622c90ea9e677127e4dcf3b9416819ee09700087af870b0c7', 'progress/work-queue.json': 'be961acbf8eb14435379eb9a3fd61da45cab3cddce0f95593f00bf57837f861b', 'site/atlas.json': '8a2fe871c7262ffc0a2f3edddb5b970a27382b9f5b85797c44f29f3be7582e4b', 'site/exports/待核对名录.csv': '9b0ca81c0420ef1fbe844b63d99684ee8b2bfb1beafb873cfcb40185158a9dd0', 'site/exports/待核对名录.xlsx': '75ad1f8c73e2add290a15de5e4aafa82d857dada4352af0cd7089a6ba2e4a25d', 'site/rosters.json': 'c837c259317159de566137c0227866a1fd7224020afbe1e37ab515ffb8a4f0a2'}
RELEASE30_ADDED_WORKBOOKS={'site/exports/csu-physics.xlsx': '81f45e692615983a4b9df4a6e99091ae633684adc87e1e0930f8feb13a457e74', 'site/exports/scut-architecture-department.xlsx': '27192205f8f5328110ef96c83895901b305f73b32d9e16e29d9a4c2788604cbe', 'site/exports/uestc-public-administration.xlsx': '730cdea4fd471759930479e75d48f584967bad7e2f0f3f2eeef568e484c18b12'}
class SourceUnavailableLayoutFix(unittest.TestCase):
    def test_all_four_data_payloads_are_byte_identical(self):
        for name in ['data/atlas.json','data/rosters.json','site/atlas.json','site/rosters.json']:
            with self.subTest(name=name): self.assertEqual(sha(read(name)),dict(dict(RELEASE28_PIN_OVERLAY,**RELEASE29_PIN_OVERLAY),**RELEASE30_PIN_OVERLAY).get(name,RELEASE27_PIN_OVERLAY.get(name,RELEASE26_PIN_OVERLAY.get(name,BASELINE_FILES[name]))))
    def test_all_112_workbooks_are_byte_identical(self):
        expected={n:h for n,h in BASELINE_FILES.items() if n.startswith('site/exports/') and n.endswith('.xlsx')}
        self.assertEqual(len(expected),112)
        actual={str(p.relative_to(ROOT)):sha(p.read_bytes()) for p in (ROOT/'site/exports').glob('*.xlsx')}
        expected={n:dict(dict(RELEASE28_PIN_OVERLAY,**RELEASE29_PIN_OVERLAY),**RELEASE30_PIN_OVERLAY).get(n,RELEASE27_PIN_OVERLAY.get(n,RELEASE26_PIN_OVERLAY.get(n,h)))for n,h in expected.items()};expected.update(RELEASE26_ADDED_WORKBOOKS);expected.update(RELEASE30_ADDED_WORKBOOKS);expected.update({'site/exports/jlu-physics.xlsx': '72bd6f13e9d7576afbabc3926c93bffc2105a48cab88b915c0d698360e08abfb', 'site/exports/seu-physics-department.xlsx': '41a983710b89306cf43bc73cf13feb907183fa47003a967ac83819a1edd120d6', 'site/exports/tju-mechanical-engineering.xlsx': '6c9f91649b0bac6ddbf258d5179c2c21ac251033474771425902e138e2ab0ab2', 'site/exports/ruc-sociology.xlsx': '42c021eb9d2f354762f5749a4f0b562b76784fa95b7abccc4135946126bf970c', 'site/exports/sdu-physics.xlsx': '47f46e8811b9a1b6fc1912f2e9a82cd1dd4a8d792ebc3576f9f15906c27ccf65', 'site/exports/dlut-chemistry.xlsx': 'd83351e6072948a3bd4e025d426acaa30fef40a7ee9ddc67f0469d04d9f8932d'});expected.update({'site/exports/buaa-aeronautic-science-engineering.xlsx': 'a32e62eef8448d0799b42f464f613841f72a578a66c073c44f30fbe9e63eb34b', 'site/exports/muc-education.xlsx': '5fd10b35753001aac54db16064c7ff55cf9b8f759bc47b3729acd61976feb21f', 'site/exports/nku-economics.xlsx': '230487cc31b92196664a6b67d268064bfd4d03fd76a1ff6b57cbaea9e79a7969'});expected.update({'site/exports/bnu-sociology.xlsx': '753ba9690453605f0860ae97ae13d9348f8ec72ad3f1ffae9480a620839e8914', 'site/exports/fdu-marxism.xlsx': 'db33026a377539a55c154f80adf1670f4c48588380e3f3297b5fc3fffdec0a2e', 'site/exports/ustc-chemistry.xlsx': '166064516591b881dbd8942e74c234185742a12b811acc93be50157bf7b2ad13'})
        self.assertEqual(actual,expected)
    def test_all_other_non_test_baseline_files_are_byte_identical(self):
        allow=set(TOKEN_FILES)|{'site/styles.css'}
        checked=0
        for name,digest in BASELINE_FILES.items():
            if name in allow or name.startswith('tests/'): continue
            with self.subTest(name=name): self.assertEqual(sha(read(name)),dict(dict(RELEASE28_PIN_OVERLAY,**RELEASE29_PIN_OVERLAY),**RELEASE30_PIN_OVERLAY).get(name,RELEASE27_PIN_OVERLAY.get(name,RELEASE26_PIN_OVERLAY.get(name,digest))))
            checked+=1
        self.assertGreater(checked,170)
    def test_stylesheet_adds_only_the_exact_scoped_wrapping_rule(self):
        css=read('site/styles.css').decode()
        self.assertEqual(css.count(RULE),1)
        self.assertTrue(css.endswith('\n'+RULE+'\n'))
        self.assertEqual(sha(css[:-len('\n'+RULE+'\n')].encode()),BASELINE_FILES['site/styles.css'])
        self.assertNotRegex(RULE,r'(?:hidden|clip|ellipsis|display|position|height|min-width|inline-block)')
    def test_exactly_six_asset_tokens_change_and_no_app_code(self):
        total=0
        for name,count in TOKEN_FILES.items():
            content=read(name)
            self.assertEqual(content.count(CURRENT_TOKEN.encode()),count,name)
            self.assertNotIn(OLD_TOKEN.encode(),content,name)
            self.assertEqual(sha(content.replace(CURRENT_TOKEN.encode(),OLD_TOKEN.encode()).replace('此名录记录尚未绑定个人档案'.encode(),'个人档案尚未建立'.encode())),BASELINE_FILES[name],name)
            total+=count
        self.assertEqual(total,6)
    def test_roles_and_historical_source_boundaries_remain(self):
        db=release26_view(json.loads(read('data/atlas.json')),'data/atlas.json')
        self.assertEqual((len(db['people']),len(db['pending_people']),len(db['institutions'])),(564,84,39))
        p=next(p for p in db['people'] if p['person_id']=='cqu-chenke')
        self.assertEqual(len(p['teaching']),2)
        for row in p['teaching']:
            self.assertEqual(row['role'],'主讲')
            self.assertEqual(row['role_source_note'],row['source_note'])
            self.assertEqual(row['role_source_id'],row['source_id'])
            self.assertEqual(row['role_source_url'],row['source_url'])
            self.assertEqual(row['status'],'historical_source_reported')
            self.assertIs(row['source_navigation_enabled'],False)
            self.assertEqual(row['source_availability'],'direct_404_cached_body_only')
            self.assertIsNone(row['level'])
    def test_pending_and_unknown_education_are_not_promoted(self):
        db=release26_view(json.loads(read('data/atlas.json')),'data/atlas.json')
        self.assertNotIn('cqu-chenrenwei',{p['person_id'] for p in db['people']})
        self.assertIn('cqu-chenrenwei',{p['person_id'] for p in db['pending_people']})
        p=next(p for p in db['people'] if p['person_id']=='cqu-chenke')
        self.assertIsNone(p['education'][0]['degree'])
        self.assertIsNone(p['education'][0]['degree_awarded'])
        self.assertEqual(p['mentors'],[])
    def test_common_build_id_remains_the_frozen_display_fix_id(self):
        for name in ['site/atlas.json','site/rosters.json']:
            self.assertEqual(release26_view(json.loads(read(name)),name)['build_id'],'c0d2d19978fa88dd')

if os.environ.get('ACADEMIC_ATLAS_NEGATIVE_CONTROL_ROOT'):
    class FrozenBaselineControl(unittest.TestCase):
        def test_every_baseline_file_remains_immutable(self):
            base=pathlib.Path(os.environ['ACADEMIC_ATLAS_NEGATIVE_CONTROL_ROOT'])
            actual={str(p.relative_to(base)):sha(p.read_bytes()) for p in base.rglob('*') if p.is_file() and '.git' not in p.parts and '__pycache__' not in p.parts}
            self.assertEqual(actual,BASELINE_FILES)

if __name__=='__main__': unittest.main()
