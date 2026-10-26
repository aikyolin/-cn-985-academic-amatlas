from atlas_test_io import read_live_json
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
HUST_MAPPING_SHA256 = '5cccae4a6117af0caec63da48e6fd196f393c30090e2f203d3ab7ae0e0f8dff0'
WHU_MAPPING_SHA256 = '5b2a4e707631c45919bd8aa8b711285e2699989b630dd50148c8002c2c558e4c'
XJTU_MAPPING_SHA256 = 'e5a81ca95e85f6cc81e7fb4a16984dfecdf1e8089538cd6b315dcafeb09c369d'
RUC_MAPPING_SHA256 = '39d6b531ba6c3e4a72ec1f6a6f8173b6582dac29f047187949556e55fae1683c'
ECNU_MAPPING_SHA256 = 'b35c42f95987f63bdd18773349270e8f7b289965f7923519776a9cc89b64c609'
BUAA_MAPPING_SHA256 = '8bbe4870f6c43131d5f4c9ca08dad0f25940cbb001491b3f3151435c96d07f24'
TONGJI_MAPPING_SHA256 = 'f337b168e9987b41d07704cbbbdc34ff904cece594eabe1551b625bf0614e09d'
BIT_MAPPING_SHA256 = 'bdb9ad4df6079b40b8b2d5ff0038aa3536abda806ef1feb42d73a1178d35a7a4'
NWPU_MAPPING_SHA256 = '5a569c0898261557784e824a3f49c3fd9f29850ae2d6959ee2d33070d38ce5b8'
SCUT_MAPPING_SHA256 = '7198a55982b7e8926997a1e52963c35a420aa9458e6e2ca2312a818c1de49d80'
USTC_MAPPING_SHA256 = '6b931ee702f8d3335fc341900e55256f271c3be033c4a0b0b8837e36ce412e3d'
CAU_MAPPING_SHA256 = 'd8c1919b7ec8584ba83541b06e3a079ded19713228cd9f4e7d06124b83d0b7c5'
FDU_MAPPING_SHA256 = 'd372c76a76377a489c611fd545d4159a7c2b6303fa51e8e5fea2ae37124cc22c'
MUC_MAPPING_SHA256 = 'c17381fd33baf667f456db11bb6609db73420c0aefa4f0fd656a639e659be562'
NWSUAF_MAPPING_SHA256 = '67645fcbc20b2fe6041f45e87fa1756acf6bfc077506561669e293670dc8f3e3'
OUC_MAPPING_SHA256 = '06612e3ad85c9a5820088f83fc4fa185f5b61ba9f1ba17f2dd54f107c5e5d22a'
LZU_MAPPING_SHA256 = '7d7611d422214538ca8f6ecc2ffc6d15f1146b45cc19227597ccfdaa51c9b47d'
SJTU_MAPPING_SHA256 = 'df52bd6b97ef4cb103c6a3a49a8641fa496b420ae891837703c9b2af2bb6c9fa'
THU_MAPPING_SHA256 = 'cdbfd02b748c4e2cca4dca2776e5c62e547d601efccd57653d5acdb24db41fe0'
PKU_MAPPING_SHA256 = 'b30f0bd80a640d8e3e89277827b34210a8f0ce31c3a02c9486b2d964d0302938'
ZJU_MAPPING_SHA256 = '3955bc5ec1a7b7610affb01c32b2d29effe8b810f97e7f5a3b2977cca1df6eab'
MIXED_MAPPING_SHA256 = '9d273a746415ca5df06d099f775f323abf89b1c6e662eba72a9449b0c0858816'
NJU_SECOND_MAPPING_SHA256 = '65d18b5c4a3097ec19ccba77073f0d1ce862b22cb25831e58a8042e6ff7b4da1'
SEU_SECOND_MAPPING_SHA256 = '3f0168e35e89936e25efcbaae7eda029804d85179f88e07c5ece9bb9fe1322e6'
NKU_SECOND_MAPPING_SHA256 = '4f65f7c9b333e245c3f925a604779fcb636f4e68f9dcb996f1206d038875adfe'
NKU_SECOND_IDS = ['nku-miaozhiwei', 'nku-longjiafu', 'nku-chenpeng-communication', 'nku-wanglihua', 'nku-zhangwenhong-sociology', 'nankai-xingxiaolong-publichealth', 'nankai-zhangminying-publichealth', 'nankai-guofenghua-publichealth', 'nankai-wanglifeng-basicmedicine', 'nku-jiangpei-history', 'nku-fanguangxin-philosophy']
SEU_SECOND_IDS = ['seu-sunzhengming', 'seu-jintanhua', 'seu-libeilei', 'seu-sunguiju', 'seu-shenyang-wave208', 'seu-zhengdedong-wave208', 'seu-yemaoxin', 'seu-huhanhui', 'seu-bianshaobin', 'seu-liyinan', 'seu-zhangjingjing-sociology']
NJU_SECOND_IDS = ['nju-cuizhiqing', 'nju-caijiahe', 'nju-chendezhi', 'nju-zhuchengjian', 'nju-chenxuezhang', 'nju-sunleqiang', 'nju-huxingliang', 'nju-zhouanhua', 'nju-caodachen-history', 'nju-shiquansheng-history', 'nju-baolei-philosophy']
MIXED_IDS = ['neu-angang', 'neu-yanjiaqi', 'neu-chengfu', 'neu-maomuran', 'cqu-liyamei-art', 'cqu-yanfugang', 'cqu-kongguangyao-medicine', 'sysu-xiali', 'sysu-gaoru-accounting']
ZJU_IDS = ['zju-baozehua', 'zju-jinweifeng', 'zju-zhoujia', 'zju-zuhui', 'zju-liudonghong', 'zju-louhansong-literature', 'zju-wuxifeng']
PKU_IDS = ['pku-chaiweizhong', 'pku-fanxing', 'pku-zhangdong-math', 'pku-wangjie', 'pku-chendayue', 'pku-chensongxi', 'pku-zhangwu', 'pku-huyonghua', 'pku-liliming', 'pku-chuming-basicmedicine', 'pku-biwenjian-medicalgenetics']
THU_IDS = ['thu-lishoukui', 'thu-dingsixin', 'thu-qiaoweifeng', 'thu-zhouyuan', 'thu-chenguoqing', 'thu-xuguoyi', 'thu-liangzongxia', 'thu-luxiaobo', 'thu-zhanggan', 'thu-liangwannian-publichealth', 'thu-jisihan-publichealth']
SJTU_IDS = ['sjtu-wanglijuan', 'sjtu-chenlingjun', 'sjtu-lijuan-philosophy', 'sjtu-zhujun-law', 'sjtu-zhoumingchuan-law', 'sjtu-zhangyi', 'sjtu-wanghan', 'sjtu-maoxiaojun', 'sjtu-houliyang', 'sjtu-fanjinxue', 'sjtu-wanghui-publichealth']
LZU_IDS = ['lzu-anjunhong', 'lzu-caojiangwei', 'lzu-chaiguozhi', 'lzu-huangjianping', 'lzu-gelong', 'lzu-shilei', 'lzu-wangdaqiao', 'lzu-zhangjin', 'lzu-zhengbing', 'lzu-liwantong', 'lzu-zhangtongsheng']
OUC_IDS = ['ouc-tongsiyou', 'ouc-wuyaxin', 'ouc-liqintong', 'ouc-chenyitong', 'ouc-aiqinghui', 'ouc-zhangwenbing', 'ouc-duanxiaolin', 'ouc-jinyaqi', 'ouc-chenchen', 'ouc-xieyangbin', 'ouc-lipihong', 'ouc-suitiankai']
NWSUAF_IDS = ['nwsuaf-chengzhihui', 'nwsuaf-dinglong', 'nwsuaf-wufuyong', 'nwsuaf-xuchenyang', 'nwsuaf-chenhuatao', 'nwsuaf-gaolexi', 'nwsuaf-xugong', 'nwsuaf-yangzhaofu', 'nwsuaf-yaoliuyang', 'nwsuaf-liuweiguo', 'nwsuaf-lironghua', 'nwsuaf-hailijuan']
MUC_IDS = ['muc-zhangbufeng', 'muc-fanxiaoqing', 'muc-wutianyu', 'muc-linweili', 'muc-lichengming', 'muc-yangchunqiang', 'muc-mujing', 'muc-zhangliang', 'muc-chailing', 'muc-zhangmin-anthropology', 'muc-wuda', 'muc-qinlili']
FDU_IDS = ['fdu-huanning', 'fdu-fengping', 'fdu-zhaodongyuan', 'fdu-penghuisheng', 'fdu-huyan', 'fdu-suntao', 'fdu-anjiesheng', 'fdu-zhangmingjun', 'fdu-jiangyixuan', 'fdu-jiangping', 'fdu-zhangnaigen', 'fdu-zhuxiuping']
CAU_IDS = ['cau-chenjingyu', 'cau-rendongyang', 'cau-ma-chao', 'cau-xu-guangyuan', 'cau-li-guangyao', 'cau-pengchen-wave98', 'cau-malingjun', 'cau-guojie', 'cau-yinyiyong', 'cau-gaoyu', 'cau-sunqingzhong', 'cau-yangdong-foodbiochemistry']
USTC_IDS = ['ustc-liubin-earth', 'ustc-jixiang', 'ustc-qianhongwu', 'ustc-liujing-life', 'ustc-jijiaojiao', 'ustc-zhangying-public-policy', 'ustc-zhuxiuli', 'ustc-shiyunli', 'ustc-niuweixing', 'ustc-zhumengxiao', 'ustc-wangchengwei', 'ustc-jinzhengyao']
SCUT_IDS = ['scut-chenguangxu', 'scut-heping', 'scut-chewenquan', 'scut-caoyufei', 'scut-zhongzhiheng', 'scut-yangxiongwen', 'scut-yangwei', 'scut-liuxiaoni', 'scut-guodifan', 'scut-qilili', 'scut-zhongyouliang-mathematics']
NWPU_IDS = ['nwpu-chenkaijie', 'nwpu-heyibai', 'nwpu-dai-yuchao', 'nwpu-zhao-ruiqin', 'nwpu-songdingbonan', 'nwpu-zhaoxueai', 'nwpu-zhangyi', 'nwpu-fupengyu', 'nwpu-zhengye', 'nwpu-sunhao-applied-statistics', 'nwpu-yangkunde', 'nwpu-sunxiaodi']
BIT_IDS = ['bit-songtian', 'bit-shifugui', 'bit-guanlei', 'bit-xiaenjun', 'bit-shanjiefei', 'bit-tongxuguang', 'bit-sunmiao', 'bit-lumingfei', 'bit-yangkuan', 'bit-liuning', 'bit-wanglang', 'bit-xuejin']
TONGJI_IDS = ['tongji-liuhuajie', 'tongji-yangjie', 'tongji-zhaoqianfan', 'tongji-wenxianghao', 'tongji-huding', 'tongji-yangweitao', 'tongji-gexin', 'tongji-leikewen', 'tongji-piyong', 'tongji-xielihua', 'tongji-huominfeng', 'tongji-sunxiaoting']
BUAA_IDS = ['buaa-quanquan', 'buaa-daiwei', 'buaa-dingchuan', 'buaa-zhou-xuefeng', 'buaa-tang-bin', 'buaa-jinhao', 'buaa-niuchaohui', 'buaa-wangtianhua', 'buaa-wuruilin', 'buaa-chenyan-sportstraining', 'buaa-zhouronggang-engineeringpsychology', 'buaa-yuehanwei']
ECNU_IDS = ['ecnu-yinyaling', 'ecnu-guanshuguang', 'ecnu-jiangxuefeng', 'ecnu-wangxuena', 'ecnu-liangchaoqun', 'ecnu-huangchenxi', 'ecnu-yinzhihua', 'ecnu-xijuzhe', 'ecnu-xusheng', 'ecnu-yinguoming', 'ecnu-zhuhu-art', 'ecnu-gejun']
RUC_IDS = ['ruc-yaohaifang', 'ruc-liu-danfeng', 'ruc-qitianjiao', 'ruc-xuwangli', 'ruc-lijingping', 'ruc-wangshuixiong', 'ruc-zhaoyandong', 'ruc-anyaoshun']
XJTU_IDS = ['xjtu-fenggenfu', 'xjtu-cui-chenhui', 'xjtu-shan-wenhua', 'xjtu-xu-yubin', 'xjtu-luojiu', 'xjtu-yao-xiuying-wave168', 'xjtu-xuhaoran-chinese', 'xjtu-shangyufan-organization', 'xjtu-yuyan', 'xjtu-peileilei', 'xjtu-zhoumi-organization', 'xjtu-zhuzhengwei']
WHU_IDS = ['whu-yufeng', 'whu-zhaolin', 'whu-wangliuquan', 'whu-wanghaowu', 'whu-weibin', 'whu-mazhaocheng', 'whu-miaoxiaoping', 'whu-yuanbifeng-publichealth', 'whu-yanhong-publichealth']
HUST_IDS = ['hust-baoyukun', 'hust-baiyun', 'hust-changyaping', 'hust-hongmin', 'hust-chenxianhong', 'hust-liuchengbin', 'hust-kelan', 'hust-xieruixiang', 'hust-liwei-education', 'hust-longlirong', 'hust-dengshiming', 'hust-zhangyanglei']
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
    return (json.loads((root / rel).read_text()) if root == published_root() else read_live_json(root / rel))

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

def hust_mapping():
    raw = (ROOT / 'tests/fixtures/independent-hust12-source-mapping.json').read_bytes()
    assert hashlib.sha256(raw).hexdigest() == HUST_MAPPING_SHA256, 'Reviewed HUST twelve-person mapping changed'
    return json.loads(raw)

def whu_mapping():
    raw = (ROOT / 'tests/fixtures/independent-whu9-source-mapping.json').read_bytes()
    assert hashlib.sha256(raw).hexdigest() == WHU_MAPPING_SHA256, 'Reviewed WHU nine-person mapping changed'
    return json.loads(raw)

def xjtu_mapping():
    raw = (ROOT / 'tests/fixtures/independent-xjtu12-source-mapping.json').read_bytes()
    assert hashlib.sha256(raw).hexdigest() == XJTU_MAPPING_SHA256, 'Reviewed XJTU twelve-person mapping changed'
    return json.loads(raw)

def ruc_mapping():
    raw = (ROOT / 'tests/fixtures/independent-ruc8-source-mapping.json').read_bytes()
    assert hashlib.sha256(raw).hexdigest() == RUC_MAPPING_SHA256, 'Reviewed RUC eight-person mapping changed'
    return json.loads(raw)

def ecnu_mapping():
    raw = (ROOT / 'tests/fixtures/independent-ecnu12-source-mapping.json').read_bytes()
    assert hashlib.sha256(raw).hexdigest() == ECNU_MAPPING_SHA256, 'Reviewed independent ECNU twelve-person mapping changed'
    return json.loads(raw)

def buaa_mapping():
    raw = (ROOT / 'tests/fixtures/independent-buaa12-source-mapping.json').read_bytes()
    assert hashlib.sha256(raw).hexdigest() == BUAA_MAPPING_SHA256, 'Reviewed independent BUAA twelve-person mapping changed'
    return json.loads(raw)

def tongji_mapping():
    raw = (ROOT / 'tests/fixtures/independent-tongji12-source-mapping.json').read_bytes()
    assert hashlib.sha256(raw).hexdigest() == TONGJI_MAPPING_SHA256, 'Reviewed independent Tongji twelve-person mapping changed'
    return json.loads(raw)

def bit_mapping():
    raw = (ROOT / 'tests/fixtures/independent-bit12-source-mapping.json').read_bytes()
    assert hashlib.sha256(raw).hexdigest() == BIT_MAPPING_SHA256, 'Reviewed independent BIT twelve-person mapping changed'
    return json.loads(raw)

def nwpu_mapping():
    raw = (ROOT / 'tests/fixtures/independent-nwpu12-source-mapping.json').read_bytes()
    assert hashlib.sha256(raw).hexdigest() == NWPU_MAPPING_SHA256, 'Reviewed independent NWPU twelve-person mapping changed'
    return json.loads(raw)

def scut_mapping():
    raw = (ROOT / 'tests/fixtures/independent-scut11-source-mapping.json').read_bytes()
    assert hashlib.sha256(raw).hexdigest() == SCUT_MAPPING_SHA256, 'Reviewed independent SCUT eleven-person mapping changed'
    return json.loads(raw)

def ustc_mapping():
    raw = (ROOT / 'tests/fixtures/independent-ustc12-source-mapping.json').read_bytes()
    assert hashlib.sha256(raw).hexdigest() == USTC_MAPPING_SHA256, 'Reviewed independent USTC twelve-person mapping changed'
    return json.loads(raw)

def cau_mapping():
    raw = (ROOT / 'tests/fixtures/independent-cau12-source-mapping.json').read_bytes()
    assert hashlib.sha256(raw).hexdigest() == CAU_MAPPING_SHA256, 'Reviewed independent CAU twelve-person mapping changed'
    return json.loads(raw)

def fdu_mapping():
    raw = (ROOT / 'tests/fixtures/independent-fdu12-source-mapping.json').read_bytes()
    assert hashlib.sha256(raw).hexdigest() == FDU_MAPPING_SHA256, 'Reviewed independent FDU twelve-person mapping changed'
    return json.loads(raw)

def muc_mapping():
    raw = (ROOT / 'tests/fixtures/independent-muc12-source-mapping.json').read_bytes()
    assert hashlib.sha256(raw).hexdigest() == MUC_MAPPING_SHA256, 'Reviewed independent MUC twelve-person mapping changed'
    return json.loads(raw)

def nwsuaf_mapping():
    raw = (ROOT / 'tests/fixtures/independent-nwsuaf12-source-mapping.json').read_bytes()
    assert hashlib.sha256(raw).hexdigest() == NWSUAF_MAPPING_SHA256, 'Reviewed independent NWSUAF twelve-person mapping changed'
    return json.loads(raw)

def ouc_mapping():
    raw = (ROOT / 'tests/fixtures/independent-ouc12-source-mapping.json').read_bytes()
    assert hashlib.sha256(raw).hexdigest() == OUC_MAPPING_SHA256, 'Reviewed independent OUC twelve-person mapping changed'
    return json.loads(raw)

def lzu_mapping():
    raw = (ROOT / 'tests/fixtures/independent-lzu11-source-mapping.json').read_bytes()
    assert hashlib.sha256(raw).hexdigest() == LZU_MAPPING_SHA256, 'Reviewed independent LZU eleven-person mapping changed'
    return json.loads(raw)

def sjtu_mapping():
    raw = (ROOT / 'tests/fixtures/independent-sjtu11-source-mapping.json').read_bytes()
    assert hashlib.sha256(raw).hexdigest() == SJTU_MAPPING_SHA256, 'Reviewed independent SJTU eleven-person mapping changed'
    return json.loads(raw)

def thu_mapping():
    raw = (ROOT / 'tests/fixtures/independent-thu11-source-mapping.json').read_bytes()
    assert hashlib.sha256(raw).hexdigest() == THU_MAPPING_SHA256, 'Reviewed independent THU eleven-person mapping changed'
    return json.loads(raw)

def pku_mapping():
    raw = (ROOT / 'tests/fixtures/independent-pku11-source-mapping.json').read_bytes()
    assert hashlib.sha256(raw).hexdigest() == PKU_MAPPING_SHA256, 'Reviewed independent PKU eleven-person mapping changed'
    return json.loads(raw)

def zju_mapping():
    raw = (ROOT / 'tests/fixtures/independent-zju7-source-mapping.json').read_bytes()
    assert hashlib.sha256(raw).hexdigest() == ZJU_MAPPING_SHA256, 'Reviewed independent ZJU seven-person mapping changed'
    return json.loads(raw)

def mixed_mapping():
    raw = (ROOT / 'tests/fixtures/independent-neu4-cqu3-sysu2-source-mapping.json').read_bytes()
    assert hashlib.sha256(raw).hexdigest() == MIXED_MAPPING_SHA256, 'Reviewed independent MIXED nine-person three-school mapping changed'
    return json.loads(raw)

def nju_second_mapping():
    raw = (ROOT / 'tests/fixtures/independent-nju11-second-source-mapping.json').read_bytes()
    assert hashlib.sha256(raw).hexdigest() == NJU_SECOND_MAPPING_SHA256, 'Reviewed independent NJU_SECOND eleven-person second NJU mapping changed'
    return json.loads(raw)

def seu_second_mapping():
    raw = (ROOT / 'tests/fixtures/independent-seu11-second-source-mapping.json').read_bytes()
    assert hashlib.sha256(raw).hexdigest() == SEU_SECOND_MAPPING_SHA256, 'Reviewed independent SEU_SECOND eleven-person second SEU mapping changed'
    return json.loads(raw)

def nku_second_mapping():
    raw = (ROOT / 'tests/fixtures/independent-nku11-second-source-mapping.json').read_bytes()
    assert hashlib.sha256(raw).hexdigest() == NKU_SECOND_MAPPING_SHA256, 'Reviewed independent NKU_SECOND eleven-person second NKU mapping changed'
    return json.loads(raw)

def reviewed_additions():
    first, second, third, fourth, fifth, sixth, seventh, eighth, ninth, tenth, eleventh, twelfth, thirteenth, fourteenth, fifteenth, sixteenth, seventeenth, eighteenth, nineteenth, twentieth, twenty_first, twenty_second, twenty_third, twenty_fourth, twenty_fifth, twenty_sixth, twenty_seventh, twenty_eighth, twenty_ninth, thirtieth, thirty_first, thirty_second, thirty_third, thirty_fourth, thirty_fifth, thirty_sixth, thirty_seventh, thirty_eighth = mapping(), next_mapping(), seu_mapping(), scu_mapping(), uestc_mapping(), hnu_mapping(), bnu_mapping(), tju_mapping(), nku_mapping(), dlut_mapping(), jlu_mapping(), sdu_mapping(), csu_mapping(), hust_mapping(), whu_mapping(), xjtu_mapping(), ruc_mapping(), ecnu_mapping(), buaa_mapping(), tongji_mapping(), bit_mapping(), nwpu_mapping(), scut_mapping(), ustc_mapping(), cau_mapping(), fdu_mapping(), muc_mapping(), nwsuaf_mapping(), ouc_mapping(), lzu_mapping(), sjtu_mapping(), thu_mapping(), pku_mapping(), zju_mapping(), mixed_mapping(), nju_second_mapping(), seu_second_mapping(), nku_second_mapping()
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
    assert [p['person_id'] for p in fourteenth['people']] == HUST_IDS
    assert [p['person_id'] for p in fifteenth['people']] == WHU_IDS
    assert [p['person_id'] for p in sixteenth['people']] == XJTU_IDS
    assert [p['person_id'] for p in seventeenth['people']] == RUC_IDS
    assert [p['person_id'] for p in eighteenth['people']] == ECNU_IDS
    assert [p['person_id'] for p in nineteenth['people']] == BUAA_IDS
    assert [p['person_id'] for p in twentieth['people']] == TONGJI_IDS
    assert [p['person_id'] for p in twenty_first['people']] == BIT_IDS
    assert [p['person_id'] for p in twenty_second['people']] == NWPU_IDS
    assert [p['person_id'] for p in twenty_third['people']] == SCUT_IDS
    assert [p['person_id'] for p in twenty_fourth['people']] == USTC_IDS
    assert [p['person_id'] for p in twenty_fifth['people']] == CAU_IDS
    assert [p['person_id'] for p in twenty_sixth['people']] == FDU_IDS
    assert [p['person_id'] for p in twenty_seventh['people']] == MUC_IDS
    assert [p['person_id'] for p in twenty_eighth['people']] == NWSUAF_IDS
    assert [p['person_id'] for p in twenty_ninth['people']] == OUC_IDS
    assert [p['person_id'] for p in thirtieth['people']] == LZU_IDS
    assert [p['person_id'] for p in thirty_first['people']] == SJTU_IDS
    assert [p['person_id'] for p in thirty_second['people']] == THU_IDS
    assert [p['person_id'] for p in thirty_third['people']] == PKU_IDS
    assert [p['person_id'] for p in thirty_fourth['people']] == ZJU_IDS
    assert [p['person_id'] for p in thirty_fifth['people']] == MIXED_IDS
    assert [p['person_id'] for p in thirty_sixth['people']] == NJU_SECOND_IDS
    assert [p['person_id'] for p in thirty_seventh['people']] == SEU_SECOND_IDS
    assert [p['person_id'] for p in thirty_eighth['people']] == NKU_SECOND_IDS
    return {key: first[key] + second[key] + third[key] + fourth[key] + fifth[key] + sixth[key] + seventh[key] + eighth[key] + ninth[key] + tenth[key] + eleventh[key] + twelfth[key] + thirteenth[key] + fourteenth[key] + fifteenth[key] + sixteenth[key] + seventeenth[key] + eighteenth[key] + nineteenth[key] + twentieth[key] + twenty_first[key] + twenty_second[key] + twenty_third[key] + twenty_fourth[key] + twenty_fifth[key] + twenty_sixth[key] + twenty_seventh[key] + twenty_eighth[key] + twenty_ninth[key] + thirtieth[key] + thirty_first[key] + thirty_second[key] + thirty_third[key] + thirty_fourth[key] + thirty_fifth[key] + thirty_sixth[key] + thirty_seventh[key] + thirty_eighth[key] for key in ('people', 'org_units', 'profile_batches')}

def validate_append(current, previous, additions):
    assert set(current) == set(previous), 'Unlisted canonical root fields'
    for key, value in previous.items():
        if key in ('people', 'org_units', 'profile_batches'):
            assert current[key] == value + additions[key], 'Historical or new source fact changed: ' + key
        else:
            assert current[key] == value, 'Unlisted change: ' + key
    assert [x['person_id'] for x in current['people'][len(previous['people']):]] == FIRST_IDS + NEXT_IDS + SEU_IDS + SCU_IDS + UESTC_IDS + HNU_IDS + BNU_IDS + TJU_IDS + NKU_IDS + DLUT_IDS + JLU_IDS + SDU_IDS + CSU_IDS + HUST_IDS + WHU_IDS + XJTU_IDS + RUC_IDS + ECNU_IDS + BUAA_IDS + TONGJI_IDS + BIT_IDS + NWPU_IDS + SCUT_IDS + USTC_IDS + CAU_IDS + FDU_IDS + MUC_IDS + NWSUAF_IDS + OUC_IDS + LZU_IDS + SJTU_IDS + THU_IDS + PKU_IDS + ZJU_IDS + MIXED_IDS + NJU_SECOND_IDS + SEU_SECOND_IDS + NKU_SECOND_IDS
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

    def test_published_749_prefix_preserves_all_previous_source_mappings(self):
        previous_mappings = (mapping(), next_mapping(), seu_mapping(), scu_mapping(), uestc_mapping(), hnu_mapping(), bnu_mapping(), tju_mapping(), nku_mapping(), dlut_mapping(), jlu_mapping(), sdu_mapping(), csu_mapping())
        self.assertEqual(len(self.previous['people']) + sum(len(m['people']) for m in previous_mappings), 749)
        for key in ('people', 'org_units', 'profile_batches'):
            expected = self.previous[key] + [item for m in previous_mappings for item in m[key]]
            self.assertEqual(self.actual[key][:len(expected)], expected, key)

    def test_published_761_prefix_preserves_all_previous_source_mappings(self):
        previous_mappings = (mapping(), next_mapping(), seu_mapping(), scu_mapping(), uestc_mapping(), hnu_mapping(), bnu_mapping(), tju_mapping(), nku_mapping(), dlut_mapping(), jlu_mapping(), sdu_mapping(), csu_mapping(), hust_mapping())
        self.assertEqual(len(self.previous['people']) + sum(len(m['people']) for m in previous_mappings), 761)
        for key in ('people', 'org_units', 'profile_batches'):
            expected = self.previous[key] + [item for m in previous_mappings for item in m[key]]
            self.assertEqual(self.actual[key][:len(expected)], expected, key)

    def test_published_770_prefix_preserves_all_previous_source_mappings(self):
        previous_mappings = (mapping(), next_mapping(), seu_mapping(), scu_mapping(), uestc_mapping(), hnu_mapping(), bnu_mapping(), tju_mapping(), nku_mapping(), dlut_mapping(), jlu_mapping(), sdu_mapping(), csu_mapping(), hust_mapping(), whu_mapping())
        self.assertEqual(len(self.previous['people']) + sum(len(m['people']) for m in previous_mappings), 770)
        for key in ('people', 'org_units', 'profile_batches'):
            expected = self.previous[key] + [item for m in previous_mappings for item in m[key]]
            self.assertEqual(self.actual[key][:len(expected)], expected, key)

    def test_published_782_prefix_preserves_all_previous_source_mappings(self):
        previous_mappings = (mapping(), next_mapping(), seu_mapping(), scu_mapping(), uestc_mapping(), hnu_mapping(), bnu_mapping(), tju_mapping(), nku_mapping(), dlut_mapping(), jlu_mapping(), sdu_mapping(), csu_mapping(), hust_mapping(), whu_mapping(), xjtu_mapping())
        self.assertEqual(len(self.previous['people']) + sum(len(m['people']) for m in previous_mappings), 782)
        for key in ('people', 'org_units', 'profile_batches'):
            expected = self.previous[key] + [item for m in previous_mappings for item in m[key]]
            self.assertEqual(self.actual[key][:len(expected)], expected, key)

    def test_published_790_prefix_preserves_all_previous_source_mappings(self):
        previous_mappings = (mapping(), next_mapping(), seu_mapping(), scu_mapping(), uestc_mapping(), hnu_mapping(), bnu_mapping(), tju_mapping(), nku_mapping(), dlut_mapping(), jlu_mapping(), sdu_mapping(), csu_mapping(), hust_mapping(), whu_mapping(), xjtu_mapping(), ruc_mapping())
        self.assertEqual(len(self.previous['people']) + sum(len(m['people']) for m in previous_mappings), 790)
        for key in ('people', 'org_units', 'profile_batches'):
            expected = self.previous[key] + [item for m in previous_mappings for item in m[key]]
            self.assertEqual(self.actual[key][:len(expected)], expected, key)

    def test_published_802_prefix_preserves_all_previous_source_mappings(self):
        previous_mappings = (mapping(), next_mapping(), seu_mapping(), scu_mapping(), uestc_mapping(), hnu_mapping(), bnu_mapping(), tju_mapping(), nku_mapping(), dlut_mapping(), jlu_mapping(), sdu_mapping(), csu_mapping(), hust_mapping(), whu_mapping(), xjtu_mapping(), ruc_mapping(), ecnu_mapping())
        self.assertEqual(len(self.previous['people']) + sum(len(m['people']) for m in previous_mappings), 802)
        for key in ('people', 'org_units', 'profile_batches'):
            expected = self.previous[key] + [item for m in previous_mappings for item in m[key]]
            self.assertEqual(self.actual[key][:len(expected)], expected, key)

    def test_published_814_prefix_preserves_all_previous_source_mappings(self):
        previous_mappings = (mapping(), next_mapping(), seu_mapping(), scu_mapping(), uestc_mapping(), hnu_mapping(), bnu_mapping(), tju_mapping(), nku_mapping(), dlut_mapping(), jlu_mapping(), sdu_mapping(), csu_mapping(), hust_mapping(), whu_mapping(), xjtu_mapping(), ruc_mapping(), ecnu_mapping(), buaa_mapping())
        self.assertEqual(len(self.previous['people']) + sum(len(m['people']) for m in previous_mappings), 814)
        for key in ('people', 'org_units', 'profile_batches'):
            expected = self.previous[key] + [item for m in previous_mappings for item in m[key]]
            self.assertEqual(self.actual[key][:len(expected)], expected, key)

    def test_published_826_prefix_preserves_all_previous_source_mappings(self):
        previous_mappings = (mapping(), next_mapping(), seu_mapping(), scu_mapping(), uestc_mapping(), hnu_mapping(), bnu_mapping(), tju_mapping(), nku_mapping(), dlut_mapping(), jlu_mapping(), sdu_mapping(), csu_mapping(), hust_mapping(), whu_mapping(), xjtu_mapping(), ruc_mapping(), ecnu_mapping(), buaa_mapping(), tongji_mapping())
        self.assertEqual(len(self.previous['people']) + sum(len(m['people']) for m in previous_mappings), 826)
        for key in ('people', 'org_units', 'profile_batches'):
            expected = self.previous[key] + [item for m in previous_mappings for item in m[key]]
            self.assertEqual(self.actual[key][:len(expected)], expected, key)

    def test_published_838_prefix_preserves_all_previous_source_mappings(self):
        previous_mappings = (mapping(), next_mapping(), seu_mapping(), scu_mapping(), uestc_mapping(), hnu_mapping(), bnu_mapping(), tju_mapping(), nku_mapping(), dlut_mapping(), jlu_mapping(), sdu_mapping(), csu_mapping(), hust_mapping(), whu_mapping(), xjtu_mapping(), ruc_mapping(), ecnu_mapping(), buaa_mapping(), tongji_mapping(), bit_mapping())
        self.assertEqual(len(self.previous['people']) + sum(len(m['people']) for m in previous_mappings), 838)
        for key in ('people', 'org_units', 'profile_batches'):
            expected = self.previous[key] + [item for m in previous_mappings for item in m[key]]
            self.assertEqual(self.actual[key][:len(expected)], expected, key)

    def test_published_850_prefix_preserves_all_previous_source_mappings(self):
        previous_mappings = (mapping(), next_mapping(), seu_mapping(), scu_mapping(), uestc_mapping(), hnu_mapping(), bnu_mapping(), tju_mapping(), nku_mapping(), dlut_mapping(), jlu_mapping(), sdu_mapping(), csu_mapping(), hust_mapping(), whu_mapping(), xjtu_mapping(), ruc_mapping(), ecnu_mapping(), buaa_mapping(), tongji_mapping(), bit_mapping(), nwpu_mapping())
        self.assertEqual(len(self.previous['people']) + sum(len(m['people']) for m in previous_mappings), 850)
        for key in ('people', 'org_units', 'profile_batches'):
            expected = self.previous[key] + [item for m in previous_mappings for item in m[key]]
            self.assertEqual(self.actual[key][:len(expected)], expected, key)

    def test_published_861_prefix_preserves_all_previous_source_mappings(self):
        previous_mappings = (mapping(), next_mapping(), seu_mapping(), scu_mapping(), uestc_mapping(), hnu_mapping(), bnu_mapping(), tju_mapping(), nku_mapping(), dlut_mapping(), jlu_mapping(), sdu_mapping(), csu_mapping(), hust_mapping(), whu_mapping(), xjtu_mapping(), ruc_mapping(), ecnu_mapping(), buaa_mapping(), tongji_mapping(), bit_mapping(), nwpu_mapping(), scut_mapping())
        self.assertEqual(len(self.previous['people']) + sum(len(m['people']) for m in previous_mappings), 861)
        for key in ('people', 'org_units', 'profile_batches'):
            expected = self.previous[key] + [item for m in previous_mappings for item in m[key]]
            self.assertEqual(self.actual[key][:len(expected)], expected, key)

    def test_published_873_prefix_preserves_all_previous_source_mappings(self):
        previous_mappings = (mapping(), next_mapping(), seu_mapping(), scu_mapping(), uestc_mapping(), hnu_mapping(), bnu_mapping(), tju_mapping(), nku_mapping(), dlut_mapping(), jlu_mapping(), sdu_mapping(), csu_mapping(), hust_mapping(), whu_mapping(), xjtu_mapping(), ruc_mapping(), ecnu_mapping(), buaa_mapping(), tongji_mapping(), bit_mapping(), nwpu_mapping(), scut_mapping(), ustc_mapping())
        self.assertEqual(len(self.previous['people']) + sum(len(m['people']) for m in previous_mappings), 873)
        for key in ('people', 'org_units', 'profile_batches'):
            expected = self.previous[key] + [item for m in previous_mappings for item in m[key]]
            self.assertEqual(self.actual[key][:len(expected)], expected, key)

    def test_published_885_prefix_preserves_all_previous_source_mappings(self):
        previous_mappings = (mapping(), next_mapping(), seu_mapping(), scu_mapping(), uestc_mapping(), hnu_mapping(), bnu_mapping(), tju_mapping(), nku_mapping(), dlut_mapping(), jlu_mapping(), sdu_mapping(), csu_mapping(), hust_mapping(), whu_mapping(), xjtu_mapping(), ruc_mapping(), ecnu_mapping(), buaa_mapping(), tongji_mapping(), bit_mapping(), nwpu_mapping(), scut_mapping(), ustc_mapping(), cau_mapping())
        self.assertEqual(len(self.previous['people']) + sum(len(m['people']) for m in previous_mappings), 885)
        for key in ('people', 'org_units', 'profile_batches'):
            expected = self.previous[key] + [item for m in previous_mappings for item in m[key]]
            self.assertEqual(self.actual[key][:len(expected)], expected, key)

    def test_published_897_prefix_preserves_all_previous_source_mappings(self):
        previous_mappings = (mapping(), next_mapping(), seu_mapping(), scu_mapping(), uestc_mapping(), hnu_mapping(), bnu_mapping(), tju_mapping(), nku_mapping(), dlut_mapping(), jlu_mapping(), sdu_mapping(), csu_mapping(), hust_mapping(), whu_mapping(), xjtu_mapping(), ruc_mapping(), ecnu_mapping(), buaa_mapping(), tongji_mapping(), bit_mapping(), nwpu_mapping(), scut_mapping(), ustc_mapping(), cau_mapping(), fdu_mapping())
        self.assertEqual(len(self.previous['people']) + sum(len(m['people']) for m in previous_mappings), 897)
        for key in ('people', 'org_units', 'profile_batches'):
            expected = self.previous[key] + [item for m in previous_mappings for item in m[key]]
            self.assertEqual(self.actual[key][:len(expected)], expected, key)

    def test_published_909_prefix_preserves_all_previous_source_mappings(self):
        previous_mappings = (mapping(), next_mapping(), seu_mapping(), scu_mapping(), uestc_mapping(), hnu_mapping(), bnu_mapping(), tju_mapping(), nku_mapping(), dlut_mapping(), jlu_mapping(), sdu_mapping(), csu_mapping(), hust_mapping(), whu_mapping(), xjtu_mapping(), ruc_mapping(), ecnu_mapping(), buaa_mapping(), tongji_mapping(), bit_mapping(), nwpu_mapping(), scut_mapping(), ustc_mapping(), cau_mapping(), fdu_mapping(), muc_mapping())
        self.assertEqual(len(self.previous['people']) + sum(len(m['people']) for m in previous_mappings), 909)
        for key in ('people', 'org_units', 'profile_batches'):
            expected = self.previous[key] + [item for m in previous_mappings for item in m[key]]
            self.assertEqual(self.actual[key][:len(expected)], expected, key)

    def test_published_921_prefix_preserves_all_previous_source_mappings(self):
        previous_mappings = (mapping(), next_mapping(), seu_mapping(), scu_mapping(), uestc_mapping(), hnu_mapping(), bnu_mapping(), tju_mapping(), nku_mapping(), dlut_mapping(), jlu_mapping(), sdu_mapping(), csu_mapping(), hust_mapping(), whu_mapping(), xjtu_mapping(), ruc_mapping(), ecnu_mapping(), buaa_mapping(), tongji_mapping(), bit_mapping(), nwpu_mapping(), scut_mapping(), ustc_mapping(), cau_mapping(), fdu_mapping(), muc_mapping(), nwsuaf_mapping())
        self.assertEqual(len(self.previous['people']) + sum(len(m['people']) for m in previous_mappings), 921)
        for key in ('people', 'org_units', 'profile_batches'):
            expected = self.previous[key] + [item for m in previous_mappings for item in m[key]]
            self.assertEqual(self.actual[key][:len(expected)], expected, key)

    def test_published_933_prefix_preserves_all_previous_source_mappings(self):
        previous_mappings = (mapping(), next_mapping(), seu_mapping(), scu_mapping(), uestc_mapping(), hnu_mapping(), bnu_mapping(), tju_mapping(), nku_mapping(), dlut_mapping(), jlu_mapping(), sdu_mapping(), csu_mapping(), hust_mapping(), whu_mapping(), xjtu_mapping(), ruc_mapping(), ecnu_mapping(), buaa_mapping(), tongji_mapping(), bit_mapping(), nwpu_mapping(), scut_mapping(), ustc_mapping(), cau_mapping(), fdu_mapping(), muc_mapping(), nwsuaf_mapping(), ouc_mapping())
        self.assertEqual(len(self.previous['people']) + sum(len(m['people']) for m in previous_mappings), 933)
        for key in ('people', 'org_units', 'profile_batches'):
            expected = self.previous[key] + [item for m in previous_mappings for item in m[key]]
            self.assertEqual(self.actual[key][:len(expected)], expected, key)

    def test_published_944_prefix_preserves_all_previous_source_mappings(self):
        previous_mappings = (mapping(), next_mapping(), seu_mapping(), scu_mapping(), uestc_mapping(), hnu_mapping(), bnu_mapping(), tju_mapping(), nku_mapping(), dlut_mapping(), jlu_mapping(), sdu_mapping(), csu_mapping(), hust_mapping(), whu_mapping(), xjtu_mapping(), ruc_mapping(), ecnu_mapping(), buaa_mapping(), tongji_mapping(), bit_mapping(), nwpu_mapping(), scut_mapping(), ustc_mapping(), cau_mapping(), fdu_mapping(), muc_mapping(), nwsuaf_mapping(), ouc_mapping(), lzu_mapping())
        self.assertEqual(len(self.previous['people']) + sum(len(m['people']) for m in previous_mappings), 944)
        for key in ('people', 'org_units', 'profile_batches'):
            expected = self.previous[key] + [item for m in previous_mappings for item in m[key]]
            self.assertEqual(self.actual[key][:len(expected)], expected, key)

    def test_published_955_prefix_preserves_all_previous_source_mappings(self):
        previous_mappings = (mapping(), next_mapping(), seu_mapping(), scu_mapping(), uestc_mapping(), hnu_mapping(), bnu_mapping(), tju_mapping(), nku_mapping(), dlut_mapping(), jlu_mapping(), sdu_mapping(), csu_mapping(), hust_mapping(), whu_mapping(), xjtu_mapping(), ruc_mapping(), ecnu_mapping(), buaa_mapping(), tongji_mapping(), bit_mapping(), nwpu_mapping(), scut_mapping(), ustc_mapping(), cau_mapping(), fdu_mapping(), muc_mapping(), nwsuaf_mapping(), ouc_mapping(), lzu_mapping(), sjtu_mapping())
        self.assertEqual(len(self.previous['people']) + sum(len(m['people']) for m in previous_mappings), 955)
        for key in ('people', 'org_units', 'profile_batches'):
            expected = self.previous[key] + [item for m in previous_mappings for item in m[key]]
            self.assertEqual(self.actual[key][:len(expected)], expected, key)

    def test_published_966_prefix_preserves_all_previous_source_mappings(self):
        previous_mappings = (mapping(), next_mapping(), seu_mapping(), scu_mapping(), uestc_mapping(), hnu_mapping(), bnu_mapping(), tju_mapping(), nku_mapping(), dlut_mapping(), jlu_mapping(), sdu_mapping(), csu_mapping(), hust_mapping(), whu_mapping(), xjtu_mapping(), ruc_mapping(), ecnu_mapping(), buaa_mapping(), tongji_mapping(), bit_mapping(), nwpu_mapping(), scut_mapping(), ustc_mapping(), cau_mapping(), fdu_mapping(), muc_mapping(), nwsuaf_mapping(), ouc_mapping(), lzu_mapping(), sjtu_mapping(), thu_mapping())
        self.assertEqual(len(self.previous['people']) + sum(len(m['people']) for m in previous_mappings), 966)
        for key in ('people', 'org_units', 'profile_batches'):
            expected = self.previous[key] + [item for m in previous_mappings for item in m[key]]
            self.assertEqual(self.actual[key][:len(expected)], expected, key)

    def test_published_977_prefix_preserves_all_previous_source_mappings(self):
        previous_mappings = (mapping(), next_mapping(), seu_mapping(), scu_mapping(), uestc_mapping(), hnu_mapping(), bnu_mapping(), tju_mapping(), nku_mapping(), dlut_mapping(), jlu_mapping(), sdu_mapping(), csu_mapping(), hust_mapping(), whu_mapping(), xjtu_mapping(), ruc_mapping(), ecnu_mapping(), buaa_mapping(), tongji_mapping(), bit_mapping(), nwpu_mapping(), scut_mapping(), ustc_mapping(), cau_mapping(), fdu_mapping(), muc_mapping(), nwsuaf_mapping(), ouc_mapping(), lzu_mapping(), sjtu_mapping(), thu_mapping(), pku_mapping())
        self.assertEqual(len(self.previous['people']) + sum(len(m['people']) for m in previous_mappings), 977)
        for key in ('people', 'org_units', 'profile_batches'):
            expected = self.previous[key] + [item for m in previous_mappings for item in m[key]]
            self.assertEqual(self.actual[key][:len(expected)], expected, key)

    def test_published_984_prefix_preserves_all_previous_source_mappings(self):
        previous_mappings = (mapping(), next_mapping(), seu_mapping(), scu_mapping(), uestc_mapping(), hnu_mapping(), bnu_mapping(), tju_mapping(), nku_mapping(), dlut_mapping(), jlu_mapping(), sdu_mapping(), csu_mapping(), hust_mapping(), whu_mapping(), xjtu_mapping(), ruc_mapping(), ecnu_mapping(), buaa_mapping(), tongji_mapping(), bit_mapping(), nwpu_mapping(), scut_mapping(), ustc_mapping(), cau_mapping(), fdu_mapping(), muc_mapping(), nwsuaf_mapping(), ouc_mapping(), lzu_mapping(), sjtu_mapping(), thu_mapping(), pku_mapping(), zju_mapping())
        self.assertEqual(len(self.previous['people']) + sum(len(m['people']) for m in previous_mappings), 984)
        for key in ('people', 'org_units', 'profile_batches'):
            expected = self.previous[key] + [item for m in previous_mappings for item in m[key]]
            self.assertEqual(self.actual[key][:len(expected)], expected, key)

    def test_published_993_prefix_preserves_all_previous_source_mappings(self):
        previous_mappings = (mapping(), next_mapping(), seu_mapping(), scu_mapping(), uestc_mapping(), hnu_mapping(), bnu_mapping(), tju_mapping(), nku_mapping(), dlut_mapping(), jlu_mapping(), sdu_mapping(), csu_mapping(), hust_mapping(), whu_mapping(), xjtu_mapping(), ruc_mapping(), ecnu_mapping(), buaa_mapping(), tongji_mapping(), bit_mapping(), nwpu_mapping(), scut_mapping(), ustc_mapping(), cau_mapping(), fdu_mapping(), muc_mapping(), nwsuaf_mapping(), ouc_mapping(), lzu_mapping(), sjtu_mapping(), thu_mapping(), pku_mapping(), zju_mapping(), mixed_mapping())
        self.assertEqual(len(self.previous['people']) + sum(len(m['people']) for m in previous_mappings), 993)
        for key in ('people', 'org_units', 'profile_batches'):
            expected = self.previous[key] + [item for m in previous_mappings for item in m[key]]
            self.assertEqual(self.actual[key][:len(expected)], expected, key)

    def test_published_1004_prefix_preserves_all_previous_source_mappings(self):
        previous_mappings = (mapping(), next_mapping(), seu_mapping(), scu_mapping(), uestc_mapping(), hnu_mapping(), bnu_mapping(), tju_mapping(), nku_mapping(), dlut_mapping(), jlu_mapping(), sdu_mapping(), csu_mapping(), hust_mapping(), whu_mapping(), xjtu_mapping(), ruc_mapping(), ecnu_mapping(), buaa_mapping(), tongji_mapping(), bit_mapping(), nwpu_mapping(), scut_mapping(), ustc_mapping(), cau_mapping(), fdu_mapping(), muc_mapping(), nwsuaf_mapping(), ouc_mapping(), lzu_mapping(), sjtu_mapping(), thu_mapping(), pku_mapping(), zju_mapping(), mixed_mapping(), nju_second_mapping())
        self.assertEqual(len(self.previous['people']) + sum(len(m['people']) for m in previous_mappings), 1004)
        for key in ('people', 'org_units', 'profile_batches'):
            expected = self.previous[key] + [item for m in previous_mappings for item in m[key]]
            self.assertEqual(self.actual[key][:len(expected)], expected, key)

    def test_published_1015_prefix_preserves_all_previous_source_mappings(self):
        previous_mappings = (mapping(), next_mapping(), seu_mapping(), scu_mapping(), uestc_mapping(), hnu_mapping(), bnu_mapping(), tju_mapping(), nku_mapping(), dlut_mapping(), jlu_mapping(), sdu_mapping(), csu_mapping(), hust_mapping(), whu_mapping(), xjtu_mapping(), ruc_mapping(), ecnu_mapping(), buaa_mapping(), tongji_mapping(), bit_mapping(), nwpu_mapping(), scut_mapping(), ustc_mapping(), cau_mapping(), fdu_mapping(), muc_mapping(), nwsuaf_mapping(), ouc_mapping(), lzu_mapping(), sjtu_mapping(), thu_mapping(), pku_mapping(), zju_mapping(), mixed_mapping(), nju_second_mapping(), seu_second_mapping())
        self.assertEqual(len(self.previous['people']) + sum(len(m['people']) for m in previous_mappings), 1015)
        for key in ('people', 'org_units', 'profile_batches'):
            expected = self.previous[key] + [item for m in previous_mappings for item in m[key]]
            self.assertEqual(self.actual[key][:len(expected)], expected, key)

    def test_old_fact_deletion_reordering_and_unknown_promotions_fail(self):
        # Mutate each independently protected era, not just whichever person is last.
        for index in (0, 612, 614, 624, 634, 645, 655, 665, 677, 689, 701, 713, 725, 737, 749, 761, 770, 782, 790, 802, 814, 826, 838, 850, 861, 873, 885, 897, 909, 921, 933, 944, 955, 966, 977, 984, 993, 1004, 1015):
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
        from atlas_storage import storage_inputs, compute_build_id
        # Independent implementation of the reviewed versioned length-framed contract.
        inputs = [('data/' + label, raw) for label, raw in storage_inputs(ROOT / 'data/atlas.json')]
        inputs += [(rel, (ROOT / rel).read_bytes()) for rel in (
            'data/rosters.json', 'scripts/build.py', 'scripts/build_rosters.py',
            'scripts/deterministic_xlsx.py', 'scripts/atlas_storage.py', 'site/atlas-loader.js')]
        digest = hashlib.sha256(b'academic-atlas-build-school-parts-v1\0')
        for label, raw in inputs:
            name = label.encode('utf-8')
            digest.update(len(name).to_bytes(8, 'big')); digest.update(name)
            digest.update(len(raw).to_bytes(8, 'big')); digest.update(raw)
        expected = digest.hexdigest()[:16]
        self.assertEqual(compute_build_id(ROOT), expected)
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
            # Approved UI-only notice: exact helper and two insertion sites; data unchanged.
            if rel == 'site/app.js':
                before = 'function nationalHome(){'.encode()
                after = 'function dataVersionNotice(){return `<p class="notice data-version">当前已收录 ${(db.people||[]).length} 份人物资料 · ${(db.pending_people||[]).length} 条待完善记录。数据版本：${esc(db.build_id||\'版本未标注\')}。具体来源检索时间见各记录；版本编号不是检索日期或发布时间。</p>`}\nfunction nationalHome(){'.encode()
                self.assertEqual(expected.count(before), 1)
                expected = expected.replace(before, after)
                before = '从学校与院系，走进学者的求学经历与师承关系。</p>'.encode()
                after = '从学校与院系，走进学者的求学经历与师承关系。</p>${dataVersionNotice()}'.encode()
                self.assertEqual(expected.count(before), 1)
                expected = expected.replace(before, after)
                before = '可追溯，比填满每一个空格更重要。</p>'.encode()
                after = '可追溯，比填满每一个空格更重要。</p>${dataVersionNotice()}'.encode()
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
                before, after = b'source-dates-20261024', b'data-version-clarity-20261025'
                self.assertEqual(expected.count(before), asset_token_counts[rel])
                expected = expected.replace(before, after)
            actual = (ROOT / rel).read_bytes()
            # Inverse the storage-only delta: every original business byte stays pinned.
            if rel == 'site/app.js':
                added = b"import {loadAtlas} from './atlas-loader.js?v=school-chunks-20261026';\n"
                self.assertEqual(actual.count(added), 1)
                self.assertTrue(actual.startswith(added))
                actual = actual[len(added):]
                after = b"try{db=await loadAtlas();"
                before = "try{const r=await fetch('atlas.json',{cache:'no-store'});if(!r.ok)throw Error('数据文件无法加载');db=await r.json();".encode()
                self.assertEqual(actual.count(after), 1)
                actual = actual.replace(after, before)
            if rel in asset_token_counts:
                self.assertEqual(actual.count(b'school-chunks-20261026'), asset_token_counts[rel])
                actual = actual.replace(b'school-chunks-20261026', b'data-version-clarity-20261025')
            if rel == 'scripts/build.py':
                added = b'from atlas_storage import load_atlas, write_atlas, compute_build_id\n'
                self.assertEqual(actual.count(added), 1)
                actual = actual.replace(added, b'')
                inverse = [
                    (b"d=load_atlas(ROOT/'data/atlas.json')", b"d=json.loads((ROOT/'data/atlas.json').read_text())"),
                    (b"d['build_id']=compute_build_id(ROOT)", b"d['build_id']=hashlib.sha256((ROOT/'data/atlas.json').read_bytes()+(ROOT/'data/rosters.json').read_bytes()+pathlib.Path(__file__).read_bytes()+(ROOT/'scripts/build_rosters.py').read_bytes()+(ROOT/'scripts/deterministic_xlsx.py').read_bytes()).hexdigest()[:16]"),
                    (b"write_atlas(ROOT/'site/atlas.json',d)", b"(ROOT/'site/atlas.json').write_text(json.dumps(d,ensure_ascii=False,separators=(',',':'),allow_nan=False)+'\\n',encoding='utf-8')")]
                for after, before in inverse:
                    self.assertEqual(actual.count(after), 1)
                    actual = actual.replace(after, before)
            self.assertEqual(actual, expected, rel)

    def test_fdu_overview_preserves_independent_semantic_limits(self):
        from openpyxl import load_workbook
        cases = {
            'fdu-fengping': ['离退休教师目录', '退休日期未知', '不转为当前任职'],
            'fdu-zhaodongyuan': ['四段海外经历', '联合机构博士为一学位'],
            'fdu-suntao': ['独立学历标签“博士”', '不绑定山东大学或海外机构', '同一来源活动的两种视图'],
            'fdu-anjiesheng': ['博士后站秘书不是本人博士后经历', '为期1个月'],
            'fdu-jiangping': ['全职教师栏', '2010-07仅学习终月'],
            'fdu-zhuxiuping': ['c30984', 'c26241', 'Bruce Logan仅博士后课题组背景'],
        }
        people = {p['person_id']: p for p in fdu_mapping()['people']}
        for person_id, terms in cases.items():
            person = people[person_id]
            wb = load_workbook(ROOT / 'site/exports' / (person['department_id'] + '.xlsx'), data_only=False)
            try:
                rows = [row for row in wb['总览'].iter_rows(min_row=2, values_only=True) if row[0] == person['name']]
                self.assertEqual(len(rows), 1, person_id)
                text = '\n'.join(str(value) for value in rows[0] if value is not None)
                for term in terms:
                    self.assertIn(term, text, (person_id, term))
            finally:
                wb.close()

    def test_muc_overview_preserves_independent_semantic_limits(self):
        from openpyxl import load_workbook
        cases = {
            'muc-wutianyu': ['讲师', '准聘副教授', '未载晋升日期'],
            'muc-zhangliang': ['2022年6月', '书目0不是终生无作品', '不补至今'],
            'muc-chailing': ['双硕区间重叠', '2005.9至今', '副教授', '讲师'],
            'muc-zhangmin-anthropology': ['2010文化人类学硕士行未列学校', '五条裸年份不作授位年', '辅修学士'],
            'muc-wuda': ['2020年7月—2020年3月倒置', 'start/end保持null', '合并攻读硕博月份不拆配'],
            'muc-qinlili': ['王克非', '李德凤', 'Kirsten Malmkjaer', '均非正式论文导师认证'],
        }
        people = {p['person_id']: p for p in muc_mapping()['people']}
        for person_id, terms in cases.items():
            person = people[person_id]
            wb = load_workbook(ROOT / 'site/exports' / (person['department_id'] + '.xlsx'), data_only=False)
            try:
                rows = [row for row in wb['总览'].iter_rows(min_row=2, values_only=True) if row[0] == person['name']]
                self.assertEqual(len(rows), 1, person_id)
                text = '\n'.join(str(value) for value in rows[0] if value is not None)
                for term in terms:
                    self.assertIn(term, text, (person_id, term))
            finally:
                wb.close()

    def test_nwsuaf_overview_preserves_independent_semantic_limits(self):
        from openpyxl import load_workbook
        cases = {'nwsuaf-chengzhihui': ['离退时间2025年6月', '不推退休原因、返聘', '历史叙述'], 'nwsuaf-xuchenyang': ['2010-06农学学士与文学学士', '不推法律双学位制度'], 'nwsuaf-chenhuatao': ['3阶段导师', '2合作导师', '非原论文认证'], 'nwsuaf-gaolexi': ['首都医科大学仅硕士研究生学习，授位未知', '张涌仅博士后阶段导师'], 'nwsuaf-xugong': ['结构化只采用上段4门，不合并为同时5门', '药物合成'], 'nwsuaf-yangzhaofu': ['加拿大圭儿夫大学', '参编不是独著或主编'], 'nwsuaf-yaoliuyang': ['仅明示学士与博士两学位，不另造硕士', '资助方，不是接收单位'], 'nwsuaf-liuweiguo': ['森林资源管理（原森林经理）教研室', '智慧林业与森林生态系'], 'nwsuaf-lironghua': ['两篇书目没有作者表', '不凭本人页面归属补本人为作者'], 'nwsuaf-hailijuan': ['个人页讲师、目录副教授两来源并列', '不推更新先后或晋升日期']}
        people = {p['person_id']: p for p in nwsuaf_mapping()['people']}
        for person_id, terms in cases.items():
            person = people[person_id]
            wb = load_workbook(ROOT / 'site/exports' / (person['department_id'] + '.xlsx'), data_only=False)
            try:
                rows = [row for row in wb['总览'].iter_rows(min_row=2, values_only=True) if row[0] == person['name']]
                self.assertEqual(len(rows), 1, person_id)
                text = '\n'.join(str(value) for value in rows[0] if value is not None)
                for term in terms:
                    self.assertIn(term, text, (person_id, term))
            finally:
                wb.close()

    def test_nwsuaf_non_degree_roles_survive_actual_experience_worksheets(self):
        from openpyxl import load_workbook
        people = {p['person_id']: p for p in nwsuaf_mapping()['people']}
        cases = [('nwsuaf-xugong', '原明确角色：博士后。', 1),
                 ('nwsuaf-yangzhaofu', '原明确角色：访问学者。', 2)]
        for person_id, phrase, count in cases:
            person = people[person_id]
            wb = load_workbook(ROOT / 'site/exports' / (person['department_id'] + '.xlsx'), data_only=False)
            try:
                rows = [row for row in wb['经历'].iter_rows(min_row=2, values_only=True) if row[0] == person['name']]
                matched = [row for row in rows if phrase in str(row[14])]
                self.assertEqual(len(matched), count, person_id)
                for row in matched:
                    self.assertIs(row[11], False, person_id)
            finally:
                wb.close()

    def test_ouc_overview_preserves_independent_semantic_limits(self):
        from openpyxl import load_workbook
        cases = {'ouc-wuyaxin': ['官网23–35，原刊2022年45(6)21–33', 'Merran Toerien仅括号具名，角色未知'], 'ouc-aiqinghui': ['原新闻2025-04-08、转载2025-04-10', '不称学校学籍独证或独立交叉认证'], 'ouc-zhangwenbing': ['学籍或授位机构未知', '65小时旅行不当入学事件', '不计已核授课'], 'ouc-chenchen': ['visiting professor', '不拆重复事件', '不追溯为2021年教师起点'], 'ouc-xieyangbin': ['具体阶段未知', '多伦多联合培养级别未知', '教材副主编和主编为编辑角色'], 'ouc-lipihong': ['2011年获得硕士文凭另列资格', '不自动等同授位', '具体学位阶段未知'], 'ouc-suitiankai': ['2006学士、2011硕士、2013博士', '不认证法国文凭法律类型、授位权、跨国等同性']}
        people = {p['person_id']: p for p in ouc_mapping()['people']}
        for person_id, terms in cases.items():
            person = people[person_id]
            wb = load_workbook(ROOT / 'site/exports' / (person['department_id'] + '.xlsx'), data_only=False)
            try:
                rows = [row for row in wb['总览'].iter_rows(min_row=2, values_only=True) if row[0] == person['name']]
                self.assertEqual(len(rows), 1, person_id)
                text = '\n'.join(str(value) for value in rows[0] if value is not None)
                for term in terms:
                    self.assertIn(term, text, (person_id, term))
            finally:
                wb.close()

    def test_ouc_course_listing_and_music_qualification_export_boundaries(self):
        from openpyxl import load_workbook
        people = {p['person_id']: p for p in ouc_mapping()['people']}
        cases = {
            'ouc-chenchen': ['官网课程列目', '本科生', '学术英语与国际交流', '专业英语', '组织行为学', '科研选题与写作', '公共政策分析', '公共事业管理学'],
            'ouc-lipihong': ['2011年获得硕士文凭', '不把文凭自动认定为硕士学位或法律等价'],
            'ouc-suitiankai': ['2011获得硕士学位按官网原称', '2013获得博士学位按官网原称', '不认证法定博士授予权'],
        }
        for person_id, terms in cases.items():
            person = people[person_id]
            wb = load_workbook(ROOT / 'site/exports' / (person['department_id'] + '.xlsx'), data_only=False)
            try:
                sheet = wb['总览' if person_id == 'ouc-chenchen' else '经历']
                rows = [row for row in sheet.iter_rows(min_row=2, values_only=True) if row[0] == person['name']]
                self.assertTrue(rows, person_id)
                text = '\n'.join(str(value) for row in rows for value in row if value is not None)
                for term in terms:
                    self.assertIn(term, text, (person_id, term))
            finally:
                wb.close()

    def test_mixed_overview_preserves_independent_semantic_limits(self):
        from openpyxl import load_workbook
        cases = {
            'neu-angang': ['2007-06-26', '2016获评副教授', '2023获博士生指导教师资格', '不把2007作为副教授或博导起始'],
            'neu-yanjiaqi': ['学习末月不是授位月', '联合培养是同济博士期间一个非另授位事件', 'MBA', '具体讲授角色'],
            'neu-chengfu': ['会计学是学科', '保博士阶段指导，不认证原论文导师'],
            'neu-maomuran': ['简介2009.7–2010.7', '列表2009.08–2010.08', '未拆两事件', '第一作者与唯一作者角色不同'],
            'cqu-liyamei-art': ['教育经历栏目空不等于未受教育', '不推本人独著或作者顺序'],
            'cqu-yanfugang': ['博士毕业月2020-06与实际授位日期分开', '2024及to appear保持原状态'],
            'cqu-kongguangyao-medicine': ['本硕仍单事件', '不推双聘、离任', 'Kong G#标记含义未知'],
            'sysu-xiali': ['香港科技大学博士生联合培养非第二博士', '曹希仁仅博士联合培养阶段导师', 'Peter Glynn为访问阶段合作导师', '本人博导资格自2018年'],
            'sysu-gaoru-accounting': ['两者组织关系、是否等同或改名未知', '会计学学士、英语双学士保留同一本科条目', '页面博士后招生是招收角色', 'Gao, R.均原列第2作者'],
        }
        people = {p['person_id']: p for p in mixed_mapping()['people']}
        for person_id, terms in cases.items():
            p = people[person_id]
            wb = load_workbook(ROOT / 'site/exports' / (p['department_id'] + '.xlsx'), data_only=False)
            try:
                rows = [row for row in wb['总览'].iter_rows(min_row=2, values_only=True) if row[0] == p['name']]
                self.assertEqual(len(rows), 1, person_id)
                text = '\n'.join(str(v) for v in rows[0] if v is not None)
                for term in terms:
                    self.assertIn(term, text, (person_id, term))
            finally:
                wb.close()

    def test_mixed_actual_education_guidance_association_and_all_five_export_tables(self):
        from openpyxl import load_workbook
        expected_schools = {'neu-angang': 'neu', 'neu-yanjiaqi': 'neu', 'neu-chengfu': 'neu', 'neu-maomuran': 'neu', 'cqu-liyamei-art': 'cqu', 'cqu-yanfugang': 'cqu', 'cqu-kongguangyao-medicine': 'cqu', 'sysu-xiali': 'sysu', 'sysu-gaoru-accounting': 'sysu'}
        selected = mixed_mapping()['people']
        self.assertEqual({p['person_id']: p['school_id'] for p in selected}, expected_schools)
        self.assertEqual([sum(p['school_id'] == school for p in selected) for school in ['neu', 'cqu', 'sysu']], [4, 3, 2])
        expected_awards = {'neu-angang': [True, True, True, False, False], 'neu-yanjiaqi': [True, True, True, False], 'neu-chengfu': [True]*3, 'neu-maomuran': [True, True, True, False], 'cqu-liyamei-art': [True], 'cqu-yanfugang': [True, True, False, False], 'cqu-kongguangyao-medicine': [None, True, False], 'sysu-xiali': [True, True, False, False, False], 'sysu-gaoru-accounting': [True]*4}
        for p in selected:
            wb = load_workbook(ROOT / 'site/exports' / (p['department_id'] + '.xlsx'), data_only=False)
            try:
                rows = [row for row in wb['经历'].iter_rows(min_row=2, values_only=True) if row[0] == p['name']]
                kinds = {e['event_kind'] for e in p['education']}
                self.assertNotIn('employment', kinds)
                education = [row for row in rows if row[1] in kinds]
                employment = [row for row in rows if row[1] == 'employment']
                self.assertEqual(len(education), len(p['education']))
                self.assertEqual(len(employment), len(p['appointments']))
                self.assertEqual(len(rows), len(education) + len(employment))
                self.assertEqual([row[11] for row in education], expected_awards[p['person_id']])
                mentors = [row for row in wb['导师'].iter_rows(min_row=2, values_only=True) if row[0] == p['name']]
                self.assertEqual(len(mentors), {'neu-angang': 3, 'neu-yanjiaqi': 3, 'neu-chengfu': 1, 'sysu-xiali': 2}.get(p['person_id'], 0))
                text = str(education + employment + mentors)
                if p['person_id'] == 'neu-angang':
                    self.assertEqual([row[12] for row in education[:3]], ['1994', '2003', '2007'])
                    for term in ['金凤德', '李凯', 'Steven Tadelis']:
                        self.assertIn(term, text)
                if p['person_id'] == 'neu-maomuran':
                    self.assertEqual(education[3][4:6], (None, None))
                    self.assertIn('两日期并存，未调和', text)
                if p['person_id'] == 'cqu-yanfugang':
                    self.assertIsNone(education[0][12])
                    self.assertIsNone(employment[0][4])
                    self.assertIn('不把博士后结束月当入职或讲师起任', text)
                if p['person_id'] == 'cqu-kongguangyao-medicine':
                    self.assertEqual(education[0][2], '本硕')
                    self.assertIn('不推双聘、离任', text)
                if p['person_id'] == 'sysu-gaoru-accounting':
                    self.assertEqual(len(education), 4)
                    self.assertIsNone(education[0][12])
                    self.assertIn('2014.06仅学习终点', text)
            finally:
                wb.close()
        reviewed = self.previous['people'] + self.additions['people']
        departments = {p['department_id'] for p in selected}
        old_math = [p for p in self.previous['people'] if p['department_id'] == 'cqu-mathematics-statistics']
        self.assertEqual(len(old_math), 3)
        current_math = [p for p in self.actual['people'] if p['department_id'] == 'cqu-mathematics-statistics']
        self.assertEqual(len(current_math), 4)
        self.assertEqual(current_math[:3], old_math)
        self.assertEqual(current_math[3]['person_id'], 'cqu-yanfugang')
        for department in departments:
            members = [p for p in reviewed if p['department_id'] == department]
            wb = load_workbook(ROOT / 'site/exports' / (department + '.xlsx'), data_only=False)
            try:
                tables = build.department_tables(members, self.actual['updated_at'], self.actual['institutions'])
                self.assertEqual(wb.sheetnames, [name for name, _ in tables])
                for name, rows in tables:
                    expected = [[build.clean(v) if build.clean(v) != '' else None for v in row] for row in rows]
                    self.assertEqual([list(row) for row in wb[name].iter_rows(values_only=True)], expected, (department, name))
                if department == 'cqu-mathematics-statistics':
                    self.assertEqual([row[0] for row in wb['总览'].iter_rows(min_row=2, values_only=True)], [p['name'] for p in old_math] + ['晏福刚'])
            finally:
                wb.close()

    def test_zju_overview_preserves_independent_semantic_limits(self):
        from openpyxl import load_workbook
        cases = {
            'zju-baozehua': ['独立目录只核杭州国际科创中心', '不推哈佛任职', '不认证正式论文导师', '细胞工程', '认识实习', '蛋白质工程', '本科生课程', '研究生课程', '不推主讲'],
            'zju-liudonghong': ['仅已读个人页1/7及2/7', '重复教育只记一次', '2006仅保留博士条目关联年'],
            'zju-jinweifeng': ['兼职研究员目录具名', '不能改全职', '三条授位学校/时间未知'],
            'zju-zhoujia': ['2003浙江大学汉语言文学学士', '2006浙江大学古典文献硕士', '2010北京大学历史学博士'],
            'zju-zuhui': ['1987是浙江大学（原杭州大学）历史系文博专业毕业年', '1989是合并研究生入学语境', '不组合为现在历史学院教授起任'],
            'zju-louhansong-literature': ['1983年9月仅来校年月', '不推当年法律学校名称或教授起任', '不据候选身份认定获奖者', '分别作者与主编'],
            'zju-wuxifeng': ['空数组表示未知，不表示没有学历或师承', '2026研究进展句称数智健康研究院院长', '不擅合并或认证改名', '不冒连续原句'],
        }
        people = {p['person_id']: p for p in zju_mapping()['people']}
        for person_id, terms in cases.items():
            p = people[person_id]
            wb = load_workbook(ROOT / 'site/exports' / (p['department_id'] + '.xlsx'), data_only=False)
            try:
                rows = [row for row in wb['总览'].iter_rows(min_row=2, values_only=True) if row[0] == p['name']]
                self.assertEqual(len(rows), 1, person_id)
                text = '\n'.join(str(v) for v in rows[0] if v is not None)
                for term in terms:
                    self.assertIn(term, text, (person_id, term))
            finally:
                wb.close()

    def test_zju_actual_education_guidance_association_and_all_five_export_tables(self):
        from openpyxl import load_workbook
        for p in zju_mapping()['people']:
            wb = load_workbook(ROOT / 'site/exports' / (p['department_id'] + '.xlsx'), data_only=False)
            try:
                rows = [row for row in wb['经历'].iter_rows(min_row=2, values_only=True) if row[0] == p['name']]
                kinds = {e['event_kind'] for e in p['education']}
                self.assertNotIn('employment', kinds)
                education = [row for row in rows if row[1] in kinds]
                employment = [row for row in rows if row[1] == 'employment']
                self.assertEqual(len(education), len(p['education']))
                self.assertEqual(len(employment), len(p['appointments']))
                self.assertEqual(len(rows), len(education) + len(employment))
                mentors = [row for row in wb['导师'].iter_rows(min_row=2, values_only=True) if row[0] == p['name']]
                self.assertEqual(len(mentors), 3 if p['person_id'] == 'zju-baozehua' else 0)
                if p['person_id'] == 'zju-baozehua':
                    text = '\n'.join(str(v) for row in mentors for v in row if v is not None)
                    for name in ['饶子和', 'Huimin Zhao', 'Ahmad S. Khalil']:
                        self.assertIn(name, text)
                    self.assertEqual([row[11] for row in education], [True, True, False])
                if p['person_id'] == 'zju-liudonghong':
                    self.assertEqual([row[11] for row in education], [True, True, True])
                    self.assertEqual([row[12] for row in education], [None, None, None])
                    self.assertIn('2006为博士条目关联年', str(education))
                if p['person_id'] in ('zju-zhoujia', 'zju-zuhui'):
                    works = [r for r in wb['论文'].iter_rows(min_row=2, values_only=True) if r[0] == p['name']]
                    self.assertEqual(len(works), 1)
                    self.assertEqual(works[0][1], '浙江历代进士录（清代卷）')
                    self.assertIn('两人物引用同一作品，非两本书', str(works))
                    self.assertIn('主编龚延明，编著祖慧、周佳', str(works))
                if p['person_id'] == 'zju-jinweifeng':
                    self.assertEqual([row[3] for row in education], [None, None, None])
                if p['person_id'] == 'zju-zhoujia':
                    self.assertEqual([row[4:6] for row in education], [(None, None)]*3)
                    for year, row in zip([2003, 2006, 2010], education):
                        self.assertIn(str(year), row[14])
                if p['person_id'] == 'zju-louhansong-literature':
                    self.assertEqual(len(employment), 1)
                    self.assertEqual(employment[0][2], '教授')
                    self.assertIsNone(employment[0][4])
                    overview = [r for r in wb['总览'].iter_rows(min_row=2, values_only=True) if r[0] == p['name']]
                    self.assertIn('1983年9月', str(overview[0]))
                    self.assertIn('来校', str(overview[0]))
                    works = [r for r in wb['论文'].iter_rows(min_row=2, values_only=True) if r[0] == p['name']]
                    self.assertEqual(len(works), 2)
                    self.assertIn('主编', str(works))
            finally:
                wb.close()
        reviewed = self.previous['people'] + self.additions['people']
        old_members = [p for p in self.previous['people'] if p['department_id'] == 'zju-ic-manufacturing']
        self.assertEqual(len(old_members), 13)
        self.assertEqual([p for p in self.actual['people'] if p['department_id'] == 'zju-ic-manufacturing'], old_members)
        departments = {p['department_id'] for p in zju_mapping()['people']} | {'zju-ic-manufacturing'}
        for department in departments:
            members = [p for p in reviewed if p['department_id'] == department]
            wb = load_workbook(ROOT / 'site/exports' / (department + '.xlsx'), data_only=False)
            try:
                tables = build.department_tables(members, self.actual['updated_at'], self.actual['institutions'])
                self.assertEqual(wb.sheetnames, [name for name, _ in tables])
                for name, rows in tables:
                    expected = [[build.clean(v) if build.clean(v) != '' else None for v in row] for row in rows]
                    self.assertEqual([list(row) for row in wb[name].iter_rows(values_only=True)], expected, (department, name))
            finally:
                wb.close()

    def test_pku_overview_preserves_independent_semantic_limits(self):
        from openpyxl import load_workbook
        cases = {
            'pku-chaiweizhong': ['目录明确旧版，仅历史归属', '3博士后共同1995－2001范围不拆分个别起止'],
            'pku-fanxing': ['7月仅学习结束月', '作品原作者、编者、第一译者分别保留', '同名葡萄牙语阅读按两个层级保留'],
            'pku-zhangdong-math': ['来自官方工会采访', '不称独立学籍或原论文验证', '本批0作品不等于无论文'],
            'pku-wangjie': ['International Center for Quantum Materials', 'Flatiron研究所原名不扩写'],
            'pku-chendayue': ['两论文with合作者不是完整作者名单', '原报告年不补授位日期'],
            'pku-chensongxi': ['不把2008当讲席教授起任', '本批无具名作品，不声称本人没有论文'],
            'pku-zhangwu': ['起任年月未披露，不虚构任职事件', '《社会发展的全球审视》明确合著'],
            'pku-huyonghua': ['空记录表示未知，不是没有教育经历', '本人教授、博导称谓不是其本人学位或师承'],
            'pku-liliming': ['空记录表示未知，不是没有教育经历', '未用搜索片段补教育事实'],
            'pku-chuming-basicmedicine': ['医学学士、医学博士两具体资格', '原学习区间不是授位日期'],
            'pku-biwenjian-medicalgenetics': ['张纪峰为博士阶段导师', '博士后合作导师，不升级论文认证', '*共同第一作者'],
        }
        people = {p['person_id']: p for p in pku_mapping()['people']}
        for person_id, terms in cases.items():
            p = people[person_id]
            wb = load_workbook(ROOT / 'site/exports' / (p['department_id'] + '.xlsx'), data_only=False)
            try:
                rows = [row for row in wb['总览'].iter_rows(min_row=2, values_only=True) if row[0] == p['name']]
                self.assertEqual(len(rows), 1, person_id)
                text = '\n'.join(str(v) for v in rows[0] if v is not None)
                for term in terms:
                    self.assertIn(term, text, (person_id, term))
            finally:
                wb.close()

    def test_pku_actual_education_employment_guidance_and_new_facts_exports(self):
        from openpyxl import load_workbook
        expected_awards = {
            'pku-huyonghua': [], 'pku-liliming': [],
            'pku-chaiweizhong': [True, True, True, False, False, False],
            'pku-fanxing': [True, True, True],
            'pku-wangjie': [True, True, False, False],
            'pku-chuming-basicmedicine': [True, True],
            'pku-zhangwu': [True, True],
            'pku-biwenjian-medicalgenetics': [None, True, False, False],
        }
        for p in pku_mapping()['people']:
            wb = load_workbook(ROOT / 'site/exports' / (p['department_id'] + '.xlsx'), data_only=False)
            try:
                rows = [row for row in wb['经历'].iter_rows(min_row=2, values_only=True) if row[0] == p['name']]
                kinds = {e['event_kind'] for e in p['education']}
                self.assertNotIn('employment', kinds)
                education = [row for row in rows if row[1] in kinds]
                employment = [row for row in rows if row[1] == 'employment']
                self.assertEqual(len(education), len(p['education']))
                self.assertEqual(len(employment), len(p['appointments']))
                self.assertEqual(len(rows), len(education) + len(employment))
                mentors = [row for row in wb['导师'].iter_rows(min_row=2, values_only=True) if row[0] == p['name']]
                self.assertEqual(len(mentors), {'pku-zhangdong-math': 1, 'pku-biwenjian-medicalgenetics': 4}.get(p['person_id'], 0))
                if p['person_id'] in expected_awards:
                    self.assertEqual([row[11] for row in education], expected_awards[p['person_id']])
                mentor_text = '\n'.join(str(v) for row in mentors for v in row if v is not None)
                if p['person_id'] == 'pku-zhangdong-math':
                    self.assertIn('张恭庆', mentor_text)
                    self.assertIn('博士', mentor_text)
                if p['person_id'] == 'pku-biwenjian-medicalgenetics':
                    for name in ['张纪峰', 'Dr. Seunggeun (Shawn) Lee', 'Dr. Stanley Pounds', 'Dr. Guolian Kang']:
                        self.assertIn(name, mentor_text)
                    self.assertIn('博士后合作导师', mentor_text)
                text = '\n'.join(str(v) for row in rows for v in row if v is not None)
                if p['person_id'] == 'pku-fanxing':
                    self.assertIsNone(education[2][12])
                    self.assertIn('2017年7月仅学习结束月', text)
                if p['person_id'] == 'pku-chuming-basicmedicine':
                    for term in ['免疫学系副主任', '基础医学院教师教学发展中心副主任', '不挪用2025-08教授起任日']:
                        self.assertIn(term, text)
                    self.assertEqual([row[2] for row in employment], ['教授', '讲师', '副教授'])
                    works = [row for row in wb['论文'].iter_rows(min_row=2, values_only=True) if row[0] == p['name']]
                    self.assertEqual(len(works), 2)
                    self.assertTrue(any('2022' in str(value) for row in works for value in row))
                if p['person_id'] == 'pku-chaiweizhong':
                    self.assertIn('1995－2001为三机构共同叙述范围', text)
                if p['person_id'] == 'pku-chendayue':
                    self.assertIn('visiting assistant professor', text)
                    self.assertIn('不改访问学习或博士后', text)
            finally:
                wb.close()

        # All five sheets for every affected PKU department, plus the unchanged old twenty.
        reviewed = self.previous['people'] + self.additions['people']
        old_members = [p for p in self.previous['people'] if p['department_id'] == 'pku-ic-microelectronics']
        self.assertEqual(len(old_members), 20)
        self.assertEqual([p for p in self.actual['people'] if p['department_id'] == 'pku-ic-microelectronics'], old_members)
        departments = {p['department_id'] for p in pku_mapping()['people']} | {'pku-ic-microelectronics'}
        for department in departments:
            members = [p for p in reviewed if p['department_id'] == department]
            wb = load_workbook(ROOT / 'site/exports' / (department + '.xlsx'), data_only=False)
            try:
                tables = build.department_tables(members, self.actual['updated_at'], self.actual['institutions'])
                self.assertEqual(wb.sheetnames, [name for name, _ in tables])
                for name, rows in tables:
                    expected = [[build.clean(v) if build.clean(v) != '' else None for v in row] for row in rows]
                    self.assertEqual([list(row) for row in wb[name].iter_rows(values_only=True)], expected, (department, name))
            finally:
                wb.close()

    def test_thu_overview_preserves_independent_semantic_limits(self):
        from openpyxl import load_workbook
        cases = {
            'thu-lishoukui': ['2015汉语言文字学资格年份', '本批仅硕士与博士记录'],
            'thu-dingsixin': ['不改哈佛大学授位或博士后', '原空教学不等本人没有授课'],
            'thu-qiaoweifeng': ['不推法律更名时间', '甘肃工业大学原历史院校名'],
            'thu-zhouyuan': ['晋升时间未知', '题名2035不当出版年'],
            'thu-chenguoqing': ['1982中国人民大学学士', '1988及1992比利时鲁汶大学(KUL)', '不是完整作者串'],
            'thu-xuguoyi': ['2010—2013访问助理教授为岗位', '外部索引未打开'],
            'thu-liangzongxia': ['不从北大博士后时间推授位日期', '首尔大学与MIT客座研究员为职业记录'],
            'thu-luxiaobo': ['1982年毕业层次未知', '原院长为历史身份', '主持设计'],
            'thu-zhanggan': ['不从清华任职推授位校', '不混主编与作者'],
            'thu-liangwannian-publichealth': ['2020至2025年8月，已结束', '不当作2025事实核验时点'],
            'thu-jisihan-publichealth': ['不据网页域名合并机构', '不冒万科独立目录认证', 'BA、ScM、ScD'],
        }
        people = {p['person_id']: p for p in thu_mapping()['people']}
        for person_id, terms in cases.items():
            p = people[person_id]
            wb = load_workbook(ROOT / 'site/exports' / (p['department_id'] + '.xlsx'), data_only=False)
            try:
                rows = [row for row in wb['总览'].iter_rows(min_row=2, values_only=True) if row[0] == p['name']]
                self.assertEqual(len(rows), 1, person_id)
                text = '\n'.join(str(v) for v in rows[0] if v is not None)
                for term in terms:
                    self.assertIn(term, text, (person_id, term))
            finally:
                wb.close()

    def test_thu_actual_education_employment_and_empty_guidance_exports(self):
        from openpyxl import load_workbook
        expected = {
            'thu-lishoukui': ([True, True], [None, None], [1993, 1998]),
            'thu-dingsixin': ([True, True, True, False], [None]*4, [None]*4),
            'thu-qiaoweifeng': ([True, True, True], [None, None, '2016-06'], [None, None, 2016]),
            'thu-chenguoqing': ([True]*3, [None]*3, [1982, 1988, 1992]),
            'thu-xuguoyi': ([True], ['2010'], [None]),
            'thu-liangzongxia': ([True, False], [None]*2, [None]*2),
            'thu-luxiaobo': ([None, None], [None]*2, [None]*2),
            'thu-zhanggan': ([True], [None], [None]),
            'thu-liangwannian-publichealth': ([True, None, True], [None]*3, [None]*3),
            'thu-jisihan-publichealth': ([True]*3, [None]*3, [None]*3),
        }
        for p in thu_mapping()['people']:
            wb = load_workbook(ROOT / 'site/exports' / (p['department_id'] + '.xlsx'), data_only=False)
            try:
                person_rows = [row for row in wb['经历'].iter_rows(min_row=2, values_only=True) if row[0] == p['name']]
                education_kinds = {e['event_kind'] for e in p['education']}
                self.assertNotIn('employment', education_kinds)
                education = [row for row in person_rows if row[1] in education_kinds]
                employment = [row for row in person_rows if row[1] == 'employment']
                self.assertEqual(len(education), len(p['education']), p['person_id'])
                self.assertEqual(len(employment), len(p['appointments']), p['person_id'])
                self.assertTrue(all(row[1] == 'employment' for row in employment))
                self.assertEqual(len(person_rows), len(education) + len(employment))
                mentors = [row for row in wb['导师'].iter_rows(min_row=2, values_only=True) if row[0] == p['name']]
                self.assertEqual(mentors, [], p['person_id'])
                if p['person_id'] in expected:
                    awards, dates, years = expected[p['person_id']]
                    self.assertEqual([row[11] for row in education], awards)
                    self.assertEqual([row[12] for row in education], dates)
                    self.assertEqual([e.get('degree_awarded_year') for e in p['education']], years)
                    for year in years:
                        if year is not None:
                            self.assertTrue(any(str(year) in str(row[14]) for row in education))
                text = '\n'.join(str(v) for row in education + employment for v in row if v is not None)
                if p['person_id'] == 'thu-lishoukui':
                    self.assertIn('1997是学习终年、1998是授位年', text)
                if p['person_id'] == 'thu-qiaoweifeng':
                    self.assertIn('received his Ph.D. ... in June 2016', text)
                if p['person_id'] == 'thu-zhouyuan':
                    self.assertIn('不追溯为2010年即长聘教授', text)
            finally:
                wb.close()

    def test_sjtu_overview_preserves_independent_semantic_limits(self):
        from openpyxl import load_workbook
        cases = {
            'sjtu-wanglijuan': ['三段均原文攻读', '王小英仅本科学位论文指导', '博士杨治良、硕士金志成仅阶段师从'],
            'sjtu-chenlingjun': ['教育专硕生与本科辅修生', '2022-26/20 24/2024-25', '本人博导资格不生成师承'],
            'sjtu-lijuan-philosophy': ['不重复计6条', '2015起讲师与页头副教授', '欧洲文化高等研究院法律/行政上级未知'],
            'sjtu-zhoumingchuan-law': ['不推离职、退休或当前聘任', '两个来源角色不合并为一个劳动关系', '1999、2003、2007为原毕业年'],
            'sjtu-zhangyi': ['博士生导师是本人指导资格', '同一作品，不重复计数', '章毅等著'],
            'sjtu-wanghan': ['硕士博士共用2002年9月至2008年6月学习区间', '2025年9月—', '不擅补著编角色'],
            'sjtu-maoxiaojun': ['博士毕业于爱荷华州立大学', '2024-08-21、2024-04-11语义未核', '类型、作者名单、期刊和贡献角色未核'],
            'sjtu-houliyang': ['LLM magna cum laude、first in class', '不额外新增学位或法律等价证明', '不当博士后'],
            'sjtu-fanjinxue': ['硕博授位学校及博士后机构未知', '无逐机构日期、不称连续访问', '未给对应起任日期'],
            'sjtu-wanghui-publichealth': ['Research fellow是职业角色，非推定博士后', '2018和2019年奥胡斯访问不推连续驻留或次数', '第二作仅Wang H列名'],
        }
        people = {p['person_id']: p for p in sjtu_mapping()['people']}
        for person_id, terms in cases.items():
            person = people[person_id]
            wb = load_workbook(ROOT / 'site/exports' / (person['department_id'] + '.xlsx'), data_only=False)
            try:
                rows = [row for row in wb['总览'].iter_rows(min_row=2, values_only=True) if row[0] == person['name']]
                self.assertEqual(len(rows), 1, person_id)
                text = '\n'.join(str(value) for value in rows[0] if value is not None)
                for term in terms:
                    self.assertIn(term, text, (person_id, term))
            finally:
                wb.close()

    def test_sjtu_actual_education_and_mentor_exports_preserve_dates_unknowns_and_deduplication(self):
        from openpyxl import load_workbook
        people = {p['person_id']: p for p in sjtu_mapping()['people']}
        for person_id, count in [('sjtu-wanglijuan', 3), ('sjtu-lijuan-philosophy', 3), ('sjtu-zhujun-law', 4)]:
            p = people[person_id]
            wb = load_workbook(ROOT / 'site/exports' / (p['department_id'] + '.xlsx'), data_only=False)
            try:
                person_rows = [row for row in wb['经历'].iter_rows(min_row=2, values_only=True) if row[0] == p['name']]
                education_kinds = {e['event_kind'] for e in p['education']}
                self.assertNotIn('employment', education_kinds)
                education = [row for row in person_rows if row[1] in education_kinds]
                employment = [row for row in person_rows if row[1] == 'employment']
                self.assertEqual(len(education), len(p['education']), person_id)
                self.assertEqual(len(employment), len(p['appointments']), person_id)
                self.assertTrue(all(row[1] == 'employment' for row in employment))
                self.assertEqual(len(person_rows), len(education) + len(employment), person_id)
                mentors = [row for row in wb['导师'].iter_rows(min_row=2, values_only=True) if row[0] == p['name']]
                self.assertEqual(len(mentors), count, person_id)
                text = '\n'.join(str(value) for row in education for value in row if value is not None)
                if person_id == 'sjtu-lijuan-philosophy':
                    self.assertEqual([row[12] for row in education], ['2004-06', '2008-01', '2010-07', '2014-07'])
                    for term in ['Erasmus Mundus Europhilosophie Program为项目', 'Bochum不填授位校', '学习起止未知']:
                        self.assertIn(term, text)
                elif person_id == 'sjtu-wanglijuan':
                    self.assertEqual([row[11] for row in education], [None, None, None, False, False])
                    self.assertIn('官网明确本科论文指导教师王小英', text)
                else:
                    self.assertEqual([row[11] for row in education], [None, None, None, True])
                    self.assertIn('中德两个硕士区间重叠原样保留', text)
                    self.assertIn('不推联授或双学位制度', text)
            finally:
                wb.close()

    def test_lzu_overview_preserves_independent_semantic_limits(self):
        from openpyxl import load_workbook
        cases = {'lzu-anjunhong': ['兰州大学任职与海外研究原区间重叠', '照录不顺平'], 'lzu-chaiguozhi': ['讲师待遇，不改成已任讲师', '博士后、博士学习与兰大任职原区间重叠'], 'lzu-shilei': ['Dr.rer.nat原资格称谓', 'Cancer Research UK Manchester Institute/英国曼彻斯特大学', '全英文主讲人'], 'lzu-wangdaqiao': ['1994、2001', '2008', '作者列表未知', '参编教材'], 'lzu-zhangjin': ['三阶段机构/日期保持未知，不按顺序分配', '陕西师范大学与中国人民大学'], 'lzu-zhengbing': ['1989年7月硕士、2003年7月博士', '计算数学研究所', '不与基础数学研究所合并'], 'lzu-liwantong': ['Wan-Tong Li与Wan-Tog Li', 'Shigui Ruan、辛周平仅访问邀请人', '应用数学研究所'], 'lzu-zhangtongsheng': ['2007至2009山东师范大学博士后与2008年7月入校工作原区间并存', '本人指导资格不变为本人师承']}
        people = {p['person_id']: p for p in lzu_mapping()['people']}
        for person_id, terms in cases.items():
            person = people[person_id]
            wb = load_workbook(ROOT / 'site/exports' / (person['department_id'] + '.xlsx'), data_only=False)
            try:
                rows = [row for row in wb['总览'].iter_rows(min_row=2, values_only=True) if row[0] == person['name']]
                self.assertEqual(len(rows), 1, person_id)
                text = '\n'.join(str(value) for value in rows[0] if value is not None)
                for term in terms:
                    self.assertIn(term, text, (person_id, term))
            finally:
                wb.close()

    def test_lzu_math_college_export_keeps_old_basic_unit_separate(self):
        from openpyxl import load_workbook
        people = {p['person_id']: p for p in lzu_mapping()['people']}
        for person_id in ('lzu-zhengbing', 'lzu-liwantong'):
            self.assertEqual(people[person_id]['department_id'], 'lzu-math-stat')
        wb = load_workbook(ROOT / 'site/exports/lzu-math-stat.xlsx', data_only=False)
        try:
            names = [row[0] for row in wb['总览'].iter_rows(min_row=2, values_only=True)]
            self.assertEqual(names, ['郑兵', '李万同'])
            rows = [row for row in wb['经历'].iter_rows(min_row=2, values_only=True) if row[0] == '郑兵']
            dates = [row[12] for row in rows if row[11] is True]
            self.assertEqual(dates, [None, '1989-07', '2003-07'])
        finally:
            wb.close()
        wb = load_workbook(ROOT / 'site/exports/lzu-basic-mathematics.xlsx', data_only=False)
        try:
            self.assertEqual([row[0] for row in wb['总览'].iter_rows(min_row=2, values_only=True)], ['常清泉', '陈立志', '程锡友'])
        finally:
            wb.close()

    def test_nju_second_overview_preserves_independent_semantic_limits(self):
        from openpyxl import load_workbook
        cases = {'nju-cuizhiqing': ['退休年月未知', '授位机构及日期未知', '独立历史学硕士资格'], 'nju-caijiahe': ['1985是机构任教起点', '“至今”仅属2014年原文', '另未读PDF摘要学校名不同'], 'nju-chendezhi': ['1960不是教授晋升时间', '不推为硕士或博士论文导师', '不启用人物关系导航'], 'nju-zhuchengjian': ['Baudry、Halterman、Kochi', '不计为三位明确个人导师', '明确1996博士授位年'], 'nju-chenxuezhang': ['博士学习终2011-06与北京大学博士后始2011-04重叠', '不认证数学系与学院法律同一', '本人导师未披露'], 'nju-sunleqiang': ['法学博士', '2008–2009访问师从特瑞尔·卡弗不作学位论文导师', '0不等于本人没有论文或著作'], 'nju-baolei-philosophy': ['原2020年12月至今', '不造任职记录', '杨维中仅博士后合作导师'], 'nju-huxingliang': ['历史杭州大学名称不改为现校名', '1988讲师、1992副教授、1997教授', '不推返聘'], 'nju-zhouanhua': ['1982/1987/1989为原毕业年', '不将毕业年当授位年', '不认证现任或返聘'], 'nju-caodachen-history': ['1997至2002范围', '不拆个别授位年份', '客座/特聘研究员，不改成求学'], 'nju-shiquansheng-history': ['退休日期未知', '不等1964年起任教授', '具体课程未披露']}
        people = {p['person_id']: p for p in nju_second_mapping()['people']}
        for person_id, terms in cases.items():
            p = people[person_id]
            wb = load_workbook(ROOT / 'site/exports' / (p['department_id'] + '.xlsx'), data_only=False)
            try:
                rows = [r for r in wb['总览'].iter_rows(min_row=2, values_only=True) if r[0] == p['name']]
                self.assertEqual(len(rows), 1, person_id)
                text = '\n'.join(str(v) for v in rows[0] if v is not None)
                for term in terms:
                    self.assertIn(term, text, (person_id, term))
            finally:
                wb.close()

    def test_nju_second_actual_education_guidance_association_and_all_five_export_tables(self):
        from openpyxl import load_workbook
        people = nju_second_mapping()['people']
        prior_mappings = (mapping(), next_mapping(), seu_mapping(), scu_mapping(), uestc_mapping(), hnu_mapping(), bnu_mapping(), tju_mapping(), nku_mapping(), dlut_mapping(), jlu_mapping(), sdu_mapping(), csu_mapping(), hust_mapping(), whu_mapping(), xjtu_mapping(), ruc_mapping(), ecnu_mapping(), buaa_mapping(), tongji_mapping(), bit_mapping(), nwpu_mapping(), scut_mapping(), ustc_mapping(), cau_mapping(), fdu_mapping(), muc_mapping(), nwsuaf_mapping(), ouc_mapping(), lzu_mapping(), sjtu_mapping(), thu_mapping(), pku_mapping(), zju_mapping(), mixed_mapping(),)
        old993 = self.previous['people'] + [p for m in prior_mappings for p in m['people']]
        self.assertEqual(len(old993), 993)
        expected_people = old993 + people
        for department in {p['department_id'] for p in people}:
            members = [p for p in expected_people if p['department_id'] == department]
            wb = load_workbook(ROOT / 'site/exports' / (department + '.xlsx'), data_only=False)
            try:
                self.assertEqual(wb.sheetnames, ['总览', '经历', '导师', '论文', '来源'])
                for name, rows in build.department_tables(members, self.actual['updated_at'], self.actual['institutions']):
                    expected = [[build.clean(v) if build.clean(v) != '' else None for v in row] for row in rows]
                    self.assertEqual([list(r) for r in wb[name].iter_rows(values_only=True)], expected, (department, name))
                for p in [x for x in people if x['department_id'] == department]:
                    rows = [r for r in wb['经历'].iter_rows(min_row=2, values_only=True) if r[0] == p['name']]
                    kinds = {e['event_kind'] for e in p['education']}
                    self.assertNotIn('employment', kinds)
                    edu = [r for r in rows if r[1] in kinds]
                    jobs = [r for r in rows if r[1] == 'employment']
                    self.assertEqual(len(edu), len(p['education']))
                    self.assertEqual(len(jobs), len(p['appointments']))
                    self.assertEqual([r[11] for r in edu], [e['degree_awarded'] for e in p['education']])
                    self.assertEqual([r[12] for r in edu], [e.get('degree_awarded_date') for e in p['education']])
                    guides = [r for r in wb['导师'].iter_rows(min_row=2, values_only=True) if r[0] == p['name']]
                    self.assertEqual(len(guides), len(p.get('mentors', [])))
                    if p['person_id'] == 'nju-chendezhi':
                        self.assertEqual(len(guides), 1)
                        text = '\n'.join(str(v) for v in guides[0] if v is not None)
                        self.assertIn('韩儒林', text)
                        self.assertIn('阶段未知', text)
                        self.assertIn('非学位导师认证', text)
                if department in ('nju-math', 'nju-philosophy'):
                    expected_ids = {'nju-math': ['nju-caoliyuan', 'nju-chenxuezhang'], 'nju-philosophy': ['nju-zhoujiaxin', 'nju-sunleqiang', 'nju-baolei-philosophy']}[department]
                    self.assertEqual([p['person_id'] for p in members], expected_ids)
                    for old in [p for p in old993 if p['department_id'] == department]:
                        self.assertEqual(next(p for p in self.actual['people'] if p['person_id'] == old['person_id']), old)
                    self.assertEqual([r[0] for r in wb['总览'].iter_rows(min_row=2, values_only=True)], [p['name'] for p in members])
            finally:
                wb.close()

    def test_seu_second_overview_preserves_independent_semantic_limits(self):
        from openpyxl import load_workbook
        cases = {'seu-sunzhengming': ['2024-08-23页面发布时间与2026年作品不等人事更新', '联合培养博士为单一培养事件', 'JSPS与美国Drexel研究仅泛述'], 'seu-jintanhua': ['空书目仅本批没有选定条目', '两博士后机构先后顺序不推日期', '不独立认证当前人事状态'], 'seu-libeilei': ['职业别名李倍雷', '首屏C/D范围', '原职业与博士时间重叠不调和'], 'seu-sunguiju': ['未把新闻中一次美国进修再加成第五次', '正式论文导师与具体学位阶段未核', '仅列参编孙桂菊'], 'seu-bianshaobin': ['未读取下一页', '2019-04-24', '2024', '完整作者、出版者元数据及全文未核'], 'seu-liyinan': ['1990-09至1997-03学习区间', '不推同时授位', '工作坊结业证书保留'], 'seu-zhangjingjing-sociology': ['不能据此认定副院长所属学院', '2018年入选', '老年移民生活质量、老龄化社会与文化变迁、数字化技术与养老服务模式'], 'seu-shenyang-wave208': ['不拆造各阶段起止或授位日期', '2009任教不是教授/所长起年', '不是两份已核原论文导师证明'], 'seu-zhengdedong-wave208': ['联合培养博士只计一个事件', '具体授位学校未知', '齐康仅合作博士后阶段导师'], 'seu-yemaoxin': ['同期国际安全学项目不能累加第二博士', '与日本东北大学不是同一机构', '两作品保原章节/译者类型'], 'seu-huhanhui': ['不能据未见推退休', '不自动将历史校名归并东南大学', '普费弗为原著作者']}
        people = {p['person_id']: p for p in seu_second_mapping()['people']}
        for person_id, terms in cases.items():
            p = people[person_id]
            wb = load_workbook(ROOT / 'site/exports' / (p['department_id'] + '.xlsx'), data_only=False)
            try:
                rows = [r for r in wb['总览'].iter_rows(min_row=2, values_only=True) if r[0] == p['name']]
                self.assertEqual(len(rows), 1, person_id)
                text = '\n'.join(str(v) for v in rows[0] if v is not None)
                for term in terms:
                    self.assertIn(term, text, (person_id, term))
            finally:
                wb.close()

    def test_seu_second_actual_education_guidance_association_and_all_five_export_tables(self):
        from openpyxl import load_workbook
        people = seu_second_mapping()['people']
        prior_mappings = (mapping(), next_mapping(), seu_mapping(), scu_mapping(), uestc_mapping(), hnu_mapping(), bnu_mapping(), tju_mapping(), nku_mapping(), dlut_mapping(), jlu_mapping(), sdu_mapping(), csu_mapping(), hust_mapping(), whu_mapping(), xjtu_mapping(), ruc_mapping(), ecnu_mapping(), buaa_mapping(), tongji_mapping(), bit_mapping(), nwpu_mapping(), scut_mapping(), ustc_mapping(), cau_mapping(), fdu_mapping(), muc_mapping(), nwsuaf_mapping(), ouc_mapping(), lzu_mapping(), sjtu_mapping(), thu_mapping(), pku_mapping(), zju_mapping(), mixed_mapping(), nju_second_mapping(),)
        old1004 = self.previous['people'] + [p for m in prior_mappings for p in m['people']]
        self.assertEqual(len(old1004), 1004)
        expected_people = old1004 + people
        for department in {p['department_id'] for p in people}:
            members = [p for p in expected_people if p['department_id'] == department]
            wb = load_workbook(ROOT / 'site/exports' / (department + '.xlsx'), data_only=False)
            try:
                self.assertEqual(wb.sheetnames, ['总览', '经历', '导师', '论文', '来源'])
                for name, rows in build.department_tables(members, self.actual['updated_at'], self.actual['institutions']):
                    expected = [[build.clean(v) if build.clean(v) != '' else None for v in row] for row in rows]
                    self.assertEqual([list(r) for r in wb[name].iter_rows(values_only=True)], expected, (department, name))
                for p in [x for x in people if x['department_id'] == department]:
                    rows = [r for r in wb['经历'].iter_rows(min_row=2, values_only=True) if r[0] == p['name']]
                    kinds = {e['event_kind'] for e in p['education']}
                    self.assertNotIn('employment', kinds)
                    edu = [r for r in rows if r[1] in kinds]
                    jobs = [r for r in rows if r[1] == 'employment']
                    self.assertEqual(len(edu), len(p['education']))
                    self.assertEqual(len(jobs), len(p['appointments']))
                    self.assertEqual([r[11] for r in edu], [e['degree_awarded'] for e in p['education']])
                    self.assertEqual([r[12] for r in edu], [e.get('degree_awarded_date') for e in p['education']])
                    guides = [r for r in wb['导师'].iter_rows(min_row=2, values_only=True) if r[0] == p['name']]
                    self.assertEqual(len(guides), len(p.get('mentors', [])))
                    if p['person_id'] == 'seu-sunguiju':
                        self.assertEqual(len(guides), 1)
                        text = '\n'.join(str(v) for v in guides[0] if v is not None)
                        self.assertIn('陈学存', text)
                        self.assertIn('具体学位阶段未知', text)
                        self.assertIn('非正式论文导师认证', text)
                        self.assertEqual(edu[2][12], '2001-07')
                for old in [p for p in old1004 if p['department_id'] == department]:
                    self.assertEqual(next(p for p in self.actual['people'] if p['person_id'] == old['person_id']), old)
                self.assertEqual([r[0] for r in wb['总览'].iter_rows(min_row=2, values_only=True)], [p['name'] for p in members])
                old_member_order = {
                    'seu-materials-metal': ['seu-dinghui', 'seu-sunzhengming'],
                    'seu-humanities': ['seu-dongqun', 'seu-yemaoxin', 'seu-zhangjingjing-sociology'],
                    'seu-humanities-philosophy-science': ['seu-he-shaojin-wave171', 'seu-zhangxueyi', 'seu-bianshaobin'],
                }
                if department in old_member_order:
                    self.assertEqual([p['person_id'] for p in members], old_member_order[department])
                if department == 'seu-arts':
                    self.assertNotIn('seu-longdiyong', [p['person_id'] for p in members])
            finally:
                wb.close()

    def test_nku_second_overview_preserves_independent_semantic_limits(self):
        from openpyxl import load_workbook
        cases = {'nku-miaozhiwei': ['ACE站点', '副教授起任2004与2002-10冲突未解', '不是两位博士论文导师'], 'nku-longjiafu': ['学士1999-06、博士2004-08为原文明确授位月', '2004-09（简介）/2004-08（工作经历）冲突保留', '原http链接与读取https网址跳转等价未核', '生物化学（化学伯苓班）', '未单独注明此课受众'], 'nku-chenpeng-communication': ['新闻与传播学院', '信息与传播学院', '北京广播学院原校名', '联合博士后为一个非学位事件'], 'nankai-xingxiaolong-publichealth': ['研究者事实提取及最短引文', '所选作品题名未知', '不由复合标签推行政父子关系'], 'nankai-zhangminying-publichealth': ['未保留完整原文', '职称栏教授与工作段副教授并存', '未推晋升日期'], 'nankai-guofenghua-publichealth': ['仅留存必要职业原文行', '未核出版者元数据或全文'], 'nankai-wanglifeng-basicmedicine': ['仅留存必要职业原文行', '本人求学导师未核'], 'nku-wanglihua': ['1990-01学习终点和1989毕业', '原2012/04-2005/05倒置不纠正', '不计王利华作品'], 'nku-zhangwenhong-sociology': ['1987授位分别保留', '2003-11答辩分别保留', '仅导师组成员不另升论文导师'], 'nku-jiangpei-history': ['1989起任教不回溯为教授职称起任', '不拆分学段边界或授位日期', '2000年6月博士授位明确保留'], 'nku-fanguangxin-philosophy': ['202 5至今', '两项博士学校不同，不合并事件', '两段旁听共十门课程', '仅委员，不新增导师关系']}
        people = {p['person_id']: p for p in nku_second_mapping()['people']}
        for person_id, terms in cases.items():
            p = people[person_id]
            wb = load_workbook(ROOT / 'site/exports' / (p['department_id'] + '.xlsx'), data_only=False)
            try:
                rows = [r for r in wb['总览'].iter_rows(min_row=2, values_only=True) if r[0] == p['name']]
                self.assertEqual(len(rows), 1, person_id)
                text = '\n'.join(str(v) for v in rows[0] if v is not None)
                for term in terms:
                    self.assertIn(term, text, (person_id, term))
            finally:
                wb.close()

    def test_nku_second_actual_education_guidance_association_and_all_five_export_tables(self):
        from openpyxl import load_workbook
        people = nku_second_mapping()['people']
        prior_mappings = (mapping(), next_mapping(), seu_mapping(), scu_mapping(), uestc_mapping(), hnu_mapping(), bnu_mapping(), tju_mapping(), nku_mapping(), dlut_mapping(), jlu_mapping(), sdu_mapping(), csu_mapping(), hust_mapping(), whu_mapping(), xjtu_mapping(), ruc_mapping(), ecnu_mapping(), buaa_mapping(), tongji_mapping(), bit_mapping(), nwpu_mapping(), scut_mapping(), ustc_mapping(), cau_mapping(), fdu_mapping(), muc_mapping(), nwsuaf_mapping(), ouc_mapping(), lzu_mapping(), sjtu_mapping(), thu_mapping(), pku_mapping(), zju_mapping(), mixed_mapping(), nju_second_mapping(), seu_second_mapping(),)
        old1015 = self.previous['people'] + [p for m in prior_mappings for p in m['people']]
        self.assertEqual(len(old1015), 1015)
        expected_people = old1015 + people
        for department in {p['department_id'] for p in people}:
            members = [p for p in expected_people if p['department_id'] == department]
            wb = load_workbook(ROOT / 'site/exports' / (department + '.xlsx'), data_only=False)
            try:
                self.assertEqual(wb.sheetnames, ['总览', '经历', '导师', '论文', '来源'])
                for name, rows in build.department_tables(members, self.actual['updated_at'], self.actual['institutions']):
                    expected = [[build.clean(v) if build.clean(v) != '' else None for v in row] for row in rows]
                    self.assertEqual([list(r) for r in wb[name].iter_rows(values_only=True)], expected, (department, name))
                for p in [x for x in people if x['department_id'] == department]:
                    rows = [r for r in wb['经历'].iter_rows(min_row=2, values_only=True) if r[0] == p['name']]
                    kinds = {e['event_kind'] for e in p['education']}
                    self.assertNotIn('employment', kinds)
                    edu = [r for r in rows if r[1] in kinds]
                    jobs = [r for r in rows if r[1] == 'employment']
                    self.assertEqual(len(edu), len(p['education']))
                    self.assertEqual(len(jobs), len(p['appointments']))
                    self.assertEqual([r[11] for r in edu], [e['degree_awarded'] for e in p['education']])
                    self.assertEqual([r[12] for r in edu], [e.get('degree_awarded_date') for e in p['education']])
                    guides = [r for r in wb['导师'].iter_rows(min_row=2, values_only=True) if r[0] == p['name']]
                    self.assertEqual(len(guides), len(p.get('mentors', [])))
                    if p['person_id'] == 'nku-longjiafu':
                        text = '\n'.join(str(v) for r in edu for v in r if v is not None)
                        self.assertIn('1999年06月获学士', text)
                        self.assertIn('2004年08月获香港科技大学', text)
                    if p['person_id'] == 'nku-jiangpei-history':
                        self.assertEqual(edu[2][12], '2000-06')
                for old in [p for p in old1015 if p['department_id'] == department]:
                    self.assertEqual(next(p for p in self.actual['people'] if p['person_id'] == old['person_id']), old)
                self.assertEqual([r[0] for r in wb['总览'].iter_rows(min_row=2, values_only=True)], [p['name'] for p in members])
                old_member_order = {
                    'nku-medical': ['nku-maodaqing-medical', 'nankai-xingxiaolong-publichealth', 'nankai-zhangminying-publichealth', 'nankai-guofenghua-publichealth', 'nankai-wanglifeng-basicmedicine'],
                    'nku-history': ['nku-yangzhenhong', 'nku-wanglihua', 'nku-jiangpei-history'],
                    'nku-philosophy': ['nku-zhangjiayu-philosophy', 'nku-fanguangxin-philosophy'],
                }
                if department in old_member_order:
                    self.assertEqual([p['person_id'] for p in members], old_member_order[department])
            finally:
                wb.close()

    def test_every_affected_workbook_exactly_matches_reviewed_members_and_fields(self):
        from openpyxl import load_workbook
        departments = {p['department_id'] for p in next_mapping()['people'] + seu_mapping()['people'] + scu_mapping()['people'] + uestc_mapping()['people'] + hnu_mapping()['people'] + bnu_mapping()['people'] + tju_mapping()['people'] + nku_mapping()['people'] + dlut_mapping()['people'] + jlu_mapping()['people'] + sdu_mapping()['people'] + csu_mapping()['people'] + hust_mapping()['people'] + whu_mapping()['people'] + xjtu_mapping()['people'] + ruc_mapping()['people'] + ecnu_mapping()['people'] + buaa_mapping()['people'] + tongji_mapping()['people'] + bit_mapping()['people'] + nwpu_mapping()['people'] + scut_mapping()['people'] + ustc_mapping()['people'] + cau_mapping()['people'] + fdu_mapping()['people'] + muc_mapping()['people'] + nwsuaf_mapping()['people'] + ouc_mapping()['people'] + lzu_mapping()['people'] + sjtu_mapping()['people'] + thu_mapping()['people'] + pku_mapping()['people'] + zju_mapping()['people'] + mixed_mapping()['people'] + nju_second_mapping()['people'] + seu_second_mapping()['people'] + nku_second_mapping()['people']}
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
        affected = existing & {p['department_id'] for p in uestc_mapping()['people'] + tju_mapping()['people'] + nku_mapping()['people'] + whu_mapping()['people'] + xjtu_mapping()['people'] + ruc_mapping()['people'] + ecnu_mapping()['people'] + buaa_mapping()['people'] + tongji_mapping()['people'] + bit_mapping()['people'] + nwpu_mapping()['people'] + scut_mapping()['people'] + ustc_mapping()['people'] + cau_mapping()['people'] + fdu_mapping()['people'] + muc_mapping()['people'] + nwsuaf_mapping()['people'] + ouc_mapping()['people'] + lzu_mapping()['people'] + sjtu_mapping()['people'] + thu_mapping()['people'] + pku_mapping()['people'] + zju_mapping()['people'] + mixed_mapping()['people'] + nju_second_mapping()['people'] + seu_second_mapping()['people'] + nku_second_mapping()['people']}
        self.assertEqual(affected, {'uestc-public-administration', 'uestc-applied-math-center', 'tju-math', 'nku-economics', 'whu-math-stat', 'ruc-sociology', 'scut-math', 'cqu-mathematics-statistics', 'nju-math'})
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

    def test_whu_unknown_institution_associations_preserve_full_exported_facts(self):
        from openpyxl import load_workbook
        p = next(p for p in whu_mapping()['people'] if p['person_id'] == 'whu-miaoxiaoping')
        actual = next(x for x in self.actual['people'] if x['person_id'] == p['person_id'])
        self.assertEqual(actual['institutional_associations'], p['institutional_associations'])
        self.assertEqual(len(actual['institutional_associations']), 3)
        self.assertEqual(len(actual['appointments']), 1)
        self.assertEqual(actual['appointments'][0]['title'], '院长')
        wb = load_workbook(ROOT / 'site/exports/whu-public-health.xlsx', data_only=False)
        try:
            rows = [row for row in wb['总览'].iter_rows(values_only=True) if p['person_id'] in row or p['name'] in row]
            self.assertEqual(len(rows), 1)
            text = '\n'.join(str(value) for value in rows[0] if value is not None)
            for association in p['institutional_associations']:
                notes = [note for note in p['unknowns'] if all(str(association[key]) in note for key in ('institution', 'start', 'end'))]
                self.assertEqual(len(notes), 1, association)
                self.assertIn(build.clean(notes[0]), text, association)
        finally:
            wb.close()

    def test_xjtu_source_time_and_role_facts_survive_real_workbook_export(self):
        from openpyxl import load_workbook
        people = {p['person_id']: p for p in xjtu_mapping()['people']}
        for person_id in ('xjtu-yao-xiuying-wave168', 'xjtu-yuyan', 'xjtu-shangyufan-organization'):
            p = people[person_id]
            wb = load_workbook(ROOT / ('site/exports/' + p['department_id'] + '.xlsx'), data_only=False)
            try:
                text = '\n'.join(str(value) for ws in wb for row in ws.iter_rows(values_only=True) for value in row if value is not None)
                self.assertIn(p['name'], text)
                if person_id == 'xjtu-yao-xiuying-wave168':
                    a = p['appointments'][0]
                    self.assertIsNone(a['start'])
                    self.assertEqual(a['university_employment_start'], '2006-07')
                    self.assertIn(build.clean(a['note']), text)
                elif person_id == 'xjtu-yuyan':
                    notes = [n for n in p['unknowns'] if '营养与食品安全系主任' in n]
                    self.assertTrue(notes)
                    for note in notes: self.assertIn(build.clean(note), text)
                else:
                    for year in ('1993', '1996', '2003'):
                        notes = [e['note'] for e in p['education'] if year in e.get('note', '')]
                        self.assertTrue(notes, year)
                        for note in notes: self.assertIn(build.clean(note), text)
            finally:
                wb.close()

    def test_ruc_creative_design_facts_remain_complete_in_actual_overview_export(self):
        from openpyxl import load_workbook
        p = next(p for p in ruc_mapping()['people'] if p['person_id'] == 'ruc-anyaoshun')
        self.assertEqual(len(p['creative_works']), 2)
        self.assertEqual(p['publications'], [])
        wb = load_workbook(ROOT / 'site/exports/ruc-art.xlsx', data_only=False)
        try:
            rows = [row for row in wb['总览'].iter_rows(values_only=True) if p['person_id'] in row or p['name'] in row]
            self.assertEqual(len(rows), 1)
            text = '\n'.join(str(v) for v in rows[0] if v is not None)
            for work in p['creative_works']:
                notes = [note for note in p['unknowns'] if work['title'] in note]
                self.assertEqual(len(notes), 1, work['title'])
                self.assertIn(build.clean(notes[0]), text)
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

    def test_buaa_associations_retirement_and_publication_details_remain_visible_in_real_exports(self):
        from openpyxl import load_workbook
        people = {p['person_id']: p for p in buaa_mapping()['people']}
        for person_id in ('buaa-zhou-xuefeng', 'buaa-yuehanwei', 'buaa-jinhao', 'buaa-quanquan'):
            p = people[person_id]
            wb = load_workbook(ROOT / ('site/exports/' + p['department_id'] + '.xlsx'), data_only=False)
            try:
                text = '\n'.join(str(value) for ws in wb for row in ws.iter_rows(values_only=True) for value in row if value is not None)
                self.assertIn(p['name'], text)
                if person_id == 'buaa-zhou-xuefeng':
                    self.assertEqual(len(p['institutional_associations']), 2)
                    self.assertEqual(len(p['appointments']), 2)
                    notes = [n for n in p['unknowns'] if '独立保留不计任职' in n]
                    self.assertEqual(len(notes), 1)
                    for value in ('2004-06', '北京航空航天大学法学院', '1998-07', '2001-04', '山东省高级人民法院'): self.assertIn(value, notes[0])
                    self.assertIn(build.clean(notes[0]), text)
                    for appointment in p['appointments']:
                        self.assertIsNone(appointment['start'])
                        self.assertIn(build.clean(appointment['note']), text)
                elif person_id == 'buaa-yuehanwei':
                    self.assertEqual(p['retirement_year'], 2024)
                    notes = [n for n in p['unknowns'] if '2024' in n]
                    self.assertTrue(notes)
                    for note in notes: self.assertIn(build.clean(note), text)
                    self.assertFalse(p['quick_link_eligible'])
                elif person_id == 'buaa-jinhao':
                    for work in p['publications']: self.assertIn(build.clean(work['note']), text)
                    for value in ('with Chen Xiong', 'with Hewei Shen', 'March 2021', 'January 2020', 'Pages 54-73'): self.assertIn(value, text)
                else:
                    notes = [a['note'] for a in p['appointments'] if '在职信息：在职' in a.get('note', '')]
                    self.assertTrue(notes)
                    for note in notes: self.assertIn(build.clean(note), text)
                    self.assertFalse(p['quick_link_eligible'])
            finally:
                wb.close()

    def test_tongji_composite_degrees_source_dates_and_professional_guidance_survive_real_exports(self):
        from openpyxl import load_workbook
        people = {p['person_id']: p for p in tongji_mapping()['people']}
        for person_id in ('tongji-xielihua', 'tongji-piyong', 'tongji-huominfeng', 'tongji-huding'):
            p = people[person_id]
            wb = load_workbook(ROOT / ('site/exports/' + p['department_id'] + '.xlsx'), data_only=False)
            try:
                text = '\n'.join(str(value) for ws in wb for row in ws.iter_rows(values_only=True) for value in row if value is not None)
                self.assertIn(p['name'], text)
                if person_id == 'tongji-xielihua':
                    self.assertEqual(len(p['education']), 3)
                    self.assertEqual(p['appointments'][0]['start'], '2012-10')
                    self.assertIsNone(p['appointments'][0]['title'])
                    notes = [n for n in p['unknowns'] if '一个教育事件' in n or '不是教授起任日' in n]
                    self.assertEqual(len(notes), 2)
                    for note in notes: self.assertIn(build.clean(note), text)
                elif person_id == 'tongji-piyong':
                    notes = [n for n in p['unknowns'] if '2026-06-01 10:23' in n]
                    self.assertEqual(len(notes), 1)
                    self.assertIn(build.clean(notes[0]), text)
                    for source in p['sources']:
                        if source.get('displayed_date') or source.get('displayed_date_text'):
                            self.assertIsNone(source.get('published_at'))
                elif person_id == 'tongji-huominfeng':
                    self.assertEqual(len(p['mentors']), 1)
                    self.assertEqual(len(p['professional_research_advisors']), 1)
                    relation = p['professional_research_advisors'][0]
                    self.assertFalse(relation['include_in_degree_mentorship_graph'])
                    self.assertIn(build.clean(relation['type_label']), text)
                    self.assertIn(build.clean(relation['note']), text)
                else:
                    notes = [n for n in p['unknowns'] if '1995学士、1999硕士、2013博士获授年' in n]
                    self.assertEqual(len(notes), 1)
                    self.assertIn(build.clean(notes[0]), text)
            finally:
                wb.close()

    def test_bit_source_limits_teaching_and_dates_survive_real_exports(self):
        from openpyxl import load_workbook
        people = {p['person_id']: p for p in bit_mapping()['people']}
        for person_id in ('bit-shifugui', 'bit-shanjiefei', 'bit-sunmiao', 'bit-lumingfei', 'bit-wanglang', 'bit-xiaenjun'):
            p = people[person_id]
            wb = load_workbook(ROOT / ('site/exports/' + p['department_id'] + '.xlsx'), data_only=False)
            try:
                self.assertEqual(len(wb.sheetnames), 5)
                text = '\n'.join(str(value) for ws in wb for row in ws.iter_rows(values_only=True) for value in row if value is not None)
                self.assertIn(p['name'], text)
                for note in p['unknowns']: self.assertIn(build.clean(note), text)
                for work in p['publications']:
                    if work.get('note'): self.assertIn(build.clean(work['note']), text)
                if person_id == 'bit-shifugui':
                    self.assertIsNone(p['publications'][0]['article_number'])
                    self.assertEqual(p['publications'][0]['locator_as_source'], '1190')
                    self.assertIn('1190', text)
                    self.assertIn('退休', text)
                elif person_id == 'bit-shanjiefei':
                    self.assertEqual(p['appointments'][0]['start'], '2013-07')
                    self.assertIsNone(p['appointments'][0]['title'])
                elif person_id == 'bit-sunmiao':
                    self.assertEqual(p['appointments'], [])
                    for value in ('2002', '2019', '设计构成'): self.assertIn(value, text)
                elif person_id == 'bit-lumingfei':
                    self.assertIsNone(p['education'][0]['degree_awarded'])
                    self.assertFalse(p['education'][3]['degree_awarded'])
                    self.assertEqual(len(p['teaching']), 5)
                    for value in ('旁听', '译文', '大学专科'): self.assertIn(value, text)
                elif person_id == 'bit-wanglang':
                    self.assertTrue(all(a['start'] is None for a in p['appointments']))
                    self.assertEqual(p['teaching'][0]['name'], '大学法语')
                    for value in ('2015', '2019', '大学法语'): self.assertIn(value, text)
                else:
                    for value in ('1996-06', '1997-06', '1997-01'): self.assertIn(value, text)
            finally:
                wb.close()

    def test_nwpu_unbound_credentials_dates_guidance_and_creative_limits_survive_real_exports(self):
        from openpyxl import load_workbook
        people = {p['person_id']: p for p in nwpu_mapping()['people']}
        for person_id in ('nwpu-zhaoxueai', 'nwpu-fupengyu', 'nwpu-sunhao-applied-statistics', 'nwpu-sunxiaodi', 'nwpu-zhengye'):
            p = people[person_id]
            wb = load_workbook(ROOT / ('site/exports/' + p['department_id'] + '.xlsx'), data_only=False)
            try:
                self.assertEqual(len(wb.sheetnames), 5)
                text = '\n'.join(str(value) for ws in wb for row in ws.iter_rows(values_only=True) for value in row if value is not None)
                self.assertIn(p['name'], text)
                for note in p['unknowns']: self.assertIn(build.clean(note), text)
                for work in p['publications']:
                    if work.get('note'): self.assertIn(build.clean(work['note']), text)
                if person_id in ('nwpu-zhaoxueai', 'nwpu-fupengyu'):
                    credential = p['credential_labels_as_source']
                    self.assertTrue(credential['degree_awarded'])
                    self.assertIsNone(credential['institution'])
                    self.assertIsNone(credential['date'])
                    self.assertIn('来源报告本人', text)
                if person_id == 'nwpu-zhaoxueai':
                    self.assertEqual(len(p['education']), 3)
                    for value in ('研究生班毕业', '文学学士', '未绑定'): self.assertIn(value, text)
                    self.assertTrue(all(e['degree_awarded'] is None for e in p['education'][:2]))
                elif person_id == 'nwpu-fupengyu':
                    self.assertEqual(len(p['education']), 2)
                    self.assertIsNone(p['education'][0]['degree_awarded'])
                    for value in ('运动人体科学', '北京体育大学', '参编', '全校本科生必修教材'): self.assertIn(value, text)
                elif person_id == 'nwpu-sunhao-applied-statistics':
                    self.assertEqual(p['education'][2]['degree_awarded_date'], '2003-06')
                    self.assertIsNone(p['education'][2]['end'])
                    for value in ('2003-06', '未发生博士后', '赵选民'): self.assertIn(value, text)
                elif person_id == 'nwpu-sunxiaodi':
                    for value in ('终南山', '非论文', '阶段未知', '叶明春'): self.assertIn(value, text)
                    self.assertEqual(p['appointments'], [])
                else:
                    self.assertEqual(p['mentors'][0]['name'], '吴建南')
                    self.assertIn(build.clean(p['mentors'][0]['type_label']), text)
                    self.assertEqual(p['teaching'][0]['role'], '主持课程建设项目')
                    self.assertIn('未读原论文', text)
            finally:
                wb.close()

if __name__ == '__main__': unittest.main()
