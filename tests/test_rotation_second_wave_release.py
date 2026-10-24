"""Self-contained batch-20 regression. Copy this file into the project's tests/.
No research directory, source cache, network, or normalization helper dependency.
"""
import copy, hashlib, json, pathlib, sys, unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import build
from build_rosters import validate_rosters
D=R=None

def object_sha(x):return hashlib.sha256(json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
EXPECTED_NEW_PEOPLE = {'fdu-aidekonelie': '39e993f5074c2829b57396020605610396b9758c29534d5c6789cc2479ee1081', 'fdu-caiyuan': '686bf1e4e2c00b86ef2612683f0eda349137a5aedaf89c4ebbe79b4975aa6de4', 'fdu-caizhijie': '323fd5c40184424d64f77515c4928414c9137967a4218f489226dd32b506d59d', 'seu-simone-baldi': '5de4ab5316fcc3c5b93e0f579eb700d2984715de6b9ce452cae9b65429135a2f', 'seu-caowanrong': '9a1a3ffdc577c134cae4cc1de78f12f787e798b7d40cdc977a9fee4284a9f828', 'seu-caojinde': 'f9c36849ecdc976699add39375d95a1632657eeba2008da339bd5328d88797dd', 'xmu-chenfulin': '87b359e8a5cf5dc05dec77db1b313e7a3f88332a3c159d0c167a9b4a8f2eb6b0', 'xmu-chenjianmin': '5c658fe558c4572688ae827122335948306607b59974d57fef017c7737379728', 'xmu-chenluping': '55d7fe8ee3541532b7071d0ec6cf78ee2aeb3a09ae89121446b077cdc76ab6d6', 'sdu-liujianya': '3d5f740be21839c7d487489ad0da4187bb424dc4cb764f30063625f9430981e4', 'sdu-huxijun': 'feff50ff936a880f78699d3f69b03c9e945c1e9c935ca9b03cf8e0278c7c2f42', 'sdu-zhangxiaoyan': '2ac4696404a7158a87a691c7c4c62222b6f6df0265dd97cda8b963f671b97b71', 'ustc-bolijun': 'a871e416e2ae39c9578d3f891d7291b1173dc6256119a7b610eadd4bc0acefc2', 'ustc-caopeigen': '608828f3917397e3286426ddb3301d75f2a93bac039a3af3f90d2f05c4d3c73a', 'ustc-chenqing': 'dca8b8248826e4a7849f3b89a8f1465e908a4eb50886761be27aa14b9ff6bebe', 'ouc-sunyifan': 'fb381afbf4e9172a058223da0597398e57dd63fa4ce1a558c308675656b8142b', 'ouc-xuejie': 'ef231eb23f077cfacab68943e2780e6ce0b04ee04fe5731ed9a5d0fccc7399de', 'ouc-yujunche': '46df3b5ac6df0ba75bca6ba7bc3c133055190e8b58fabb23140e1cc8789400d9', 'hust-chaizhenhua': '6cd938b9fa541de0a8434118f3f2691705b33fa7dbddd3374f8713b1d50e68e8', 'hust-duanjinqiao': 'f6d894b1bfdfe992a201ffba1288b897dd5584b4618a44bcc48ee0f4b0844720', 'hnu-huangyong2': '44979d44f7274fb916fe5e28b29a7630b6a9afe6202b9325f86c7cd4d4ccfc1e', 'hnu-liqingguo': 'de1b0ce9faf42b99da12158628b54c8153df4f68bdb6b5e975493ef0cb281f60', 'whu-anfengwen': '61e8a914565c4fb00319051531a63966574528fef50c045c1e143e3624669678', 'whu-aoweiwei': 'f5f368a156e08b795860bf77a302e354b4b249363608affeee0ce1b9b952933a', 'whu-chenguoxian': '921c7ec27c3e2247875c665ad128c992535cc3f1919a70379e2e226397e5381e', 'nudt-weiyingmei': 'b6cb4d5999f65f74b1c0cb8a02bab35d05e9486420ea681e2bedea752deb770b', 'nudt-huyamin': '8abf513c5266fad643aba9af64e099c9b5f44d0b8d3381d6355fc00e19da955a', 'nudt-zhangwenming': '3dd1d13dfde06a287e7fa3a487122e75b9ce07c177ed5908c73fbd24a1b5ef7b', 'csu-cenxiuli': '91b155dee321b9fdf978c2c5007ab57f1aa2ab81d77fa55a90c57d44ae72cf9f', 'csu-chenhaibo': 'e1a12fb2bec2274c54807fabafdc11c24dede61e71f1f63f5f7723675549e932', 'csu-chenhebai': '18a81d5ecd6a4c788c4a3c3604429bfc25e2c56a99c5cdf9034b97b2a4d22814', 'hust-duanzhiwen': 'b2e490aabbbaa2337a0ac75c548554bbd028fdf90a5b9f710440f76413770b46', 'hnu-jiangyueping': 'cfb4bbf8cb520ca8b97dd575d9bb2edadefda836651ac1f6f75047441066f689'}
BASELINE_PREFIXES = {'people': (468, '9cef7703879f111a20e60eebf754a5a244703f9a275cafa74bd9a5f520db0125'), 'pending_people': (78, '1e3390b5b178471679f43c8f081f3dae4e0bb06c6ca9b2a092e230a1c49dacc5'), 'org_units': (175, '24db28ec325a1b7a0ef009f2157ab15c982068920d1a8f9cb9d11356b9b345ca'), 'campuses': (4, 'a29d9956fbbc284b9cdafc640ac9057dd4512c2181d89780a92a6a8bf01e6505'), 'profile_batches': (106, 'b49beb864d2472765ec321117602c9515406d94ef619fdbb172e777557043e83')}
BASELINE_ROSTER_PREFIXES = {'entries': (1628, '6b5279162b54d4ef3e6d325fc87875a650da78795a0ac9d53939a9bf95d2dff5'), 'source_observations': (1666, 'ac074736caed060bf86a65849902eb3d14766b06888485a6f2f3b17e636d8d25'), 'coverage': (177, '528a49581386340a32a0f872a4c2b25d3b133baf6ee512c04fb7bc4b485a23d9'), 'summary': (107, '368d862bb790da87280a66e9d72c0aee8db68b542071c8554cb17cb8bbf63e57'), 'batches': (79, 'aa8eb936184a780fc3a196483e99cf19fa50c493893c722d0f1e9c8643dc3e21')}

class RotationSecondWaveReleaseTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  global D,R
  if D is None:D=json.loads((ROOT/'data/atlas.json').read_text())
  if R is None:R=json.loads((ROOT/'data/rosters.json').read_text())
  cls.d,cls.r=D,R;cls.ps={p['person_id']:p for p in D['people']+D['pending_people']};cls.new=[cls.ps[pid]for pid in EXPECTED_NEW_PEOPLE];cls.pro=[p for p in cls.new if p['detail_count_eligible']]
 def tables(self,pid):return dict(build.department_tables([self.ps[pid]],self.d['updated_at'],self.d['institutions']))
 def test_01_exact_new_records_and_all_original_leaf_values(self):
  self.assertEqual(len(self.new),33)
  for pid,sha in EXPECTED_NEW_PEOPLE.items():self.assertEqual(object_sha(self.ps[pid]),sha,pid)
 def test_02_original_nineteenth_records_unchanged(self):
  for k,(size,sha)in BASELINE_PREFIXES.items():self.assertEqual(object_sha(self.d[k][:size]),sha,k)
  for k,(size,sha)in BASELINE_ROSTER_PREFIXES.items():self.assertEqual(object_sha(self.r[k][:size]),sha,k)
 def test_03_layers_and_counts(self):
  self.assertEqual(len(self.pro),31);self.assertEqual({p['person_id']for p in self.new if not p['detail_count_eligible']},{'hust-duanzhiwen','hnu-jiangyueping'})
  self.assertEqual({k:sum(len(p.get(k,[]))for p in self.pro)for k in ('education','appointments','mentors','publications','teaching','sources')},{'education':101,'appointments':83,'mentors':10,'publications':31,'teaching':6,'sources':119})
  self.assertEqual(len(self.d['institutions']),39)
 def test_04_pending_sparse_publication_excluded(self):
  p=self.ps['hust-duanzhiwen'];self.assertEqual(p['publications'],[]);self.assertEqual(len(p['biography_evidence']['publications']),1);self.assertFalse(p['biography_evidence']['count_eligible']);self.assertEqual(self.ps['hnu-jiangyueping']['education'],[])
 def test_05_teaching_independent_and_source_closed(self):
  ps=[p for p in self.pro if p['school_id']=='nudt'];self.assertEqual(sum(len(p['teaching'])for p in ps),6)
  for p in ps:
   for key in ('education','mentors','publications'):self.assertEqual(p[key],[])
   sources={s['id']:s['url']for s in p['sources']}
   for t in p['teaching']:
    self.assertEqual(sources[t['source_id']],t['source_url'])
    for key in ('include_in_education_count','include_in_appointment_count','include_in_verified_mentor_count','include_in_publication_count'):self.assertFalse(t[key])
 def test_06_teaching_export_and_non_homepage_navigation(self):
  for p in [p for p in self.pro if p['school_id']=='nudt']:
   t=self.tables(p['person_id']);self.assertFalse(p['official_profile_navigation_eligible']);self.assertEqual(t['总览'][1][3],'');self.assertIn('非个人主页',t['总览'][1][8]);self.assertIn('非本人求学学历',t['总览'][1][6])
   for f in p['teaching']:self.assertIn(f['name'],t['总览'][1][6]);self.assertIn(f['source_id'],t['总览'][1][6])
   self.assertEqual(len(t['经历']),len(p['appointments'])+1);self.assertEqual(len(t['导师']),1);self.assertEqual(len(t['论文']),1)
 def test_07_historical_sampling_not_current_985(self):
  for pid,current in [('ustc-bolijun','西安电子科技大学'),('hust-duanjinqiao','大湾区大学')]:
   p=self.ps[pid];self.assertFalse(p['include_in_current_faculty_count']);self.assertEqual(p['current_employment']['institution'],current);self.assertIn('非该校现职',p['sampling_affiliation_label'])
   entry=next(e for e in self.r['entries']if e.get('source_person_id')==pid);self.assertFalse(entry['include_in_current_faculty_count']);self.assertEqual(entry['current_employment'],p['current_employment'])
 def test_08_no_award_learning_not_visit(self):
  for e in self.ps['hnu-liqingguo']['education'][:2]:self.assertIs(e['degree_awarded'],False);self.assertEqual(e['event_kind'],'degree_study');self.assertEqual(e['region'],'mainland');self.assertIn('非访问',e['event_kind_label'])
 def test_09_executive_and_visiting_guidance_not_phd_main(self):
  m=self.ps['sdu-liujianya']['mentors'][2];self.assertEqual(m['name'],'展涛');self.assertEqual(m['relationship_kind'],'doctoral_dissertation_executive_advisor');self.assertIn('非共同主导师',m['type_label'])
  m=self.ps['csu-chenhaibo']['mentors'][0];self.assertEqual(m['relationship_kind'],'visiting_supervisor');self.assertFalse(m['quick_link_eligible']);self.assertEqual(m['date_basis'],'education_period_not_independently_verified_supervision_dates')
 def test_10_candidate_and_retired_navigation_boundaries(self):
  for pid in ('seu-simone-baldi','xmu-chenluping'):
   p=self.ps[pid];self.assertEqual(p['mentors'],[]);self.assertEqual(len(p['pending_mentor_candidates']),3)
   for m in p['pending_mentor_candidates']:self.assertFalse(m['include_in_mentorship_graph']);self.assertFalse(m['include_in_verified_mentor_count'])
  for pid in ('sdu-liujianya','hust-duanjinqiao','csu-chenhaibo','ustc-caopeigen','whu-chenguoxian'):self.assertTrue(all(row[7]==''for row in self.tables(pid)['导师'][1:]))
 def test_11_report_not_journal_and_awards_tristate(self):
  qs=[q for p in self.pro for q in p['publications']];self.assertEqual(sum(q['type']=='journal_article'for q in qs),30);self.assertEqual(sum(q['type']=='research_report'for q in qs),1)
  es=[e for p in self.pro for e in p['education']];self.assertEqual((sum(e['degree_awarded']is True for e in es),sum(e['degree_awarded']is False for e in es),sum(e['degree_awarded']is None for e in es)),(21,37,43))
 def test_12_leaf_organizations_campus_and_alias(self):
  for p in [p for p in self.new if p['school_id']=='fdu']:self.assertEqual(p['source_organization_id'],'fdu-math');self.assertEqual(p['organization_id'],p['department_id'])
  for p in self.new:self.assertEqual(p['campus_ids'],[])
  self.assertEqual(self.ps['seu-simone-baldi']['raw_roster_name'],'BALDI SIMONE')
 def test_13_sources_and_events_close(self):
  for p in self.new:
   src={s['id']:s['url']for s in p['sources']};events={e['event_id']for e in p['education']}
   for k in ('education','appointments','mentors','publications','teaching'):
    for row in p.get(k,[]):
     if row.get('source_id'):self.assertEqual(src[row['source_id']],row['source_url'])
   for m in p['mentors']:self.assertIn(m['education_event_id'],events)
 def test_14_actual_validators_and_table_no_mutation(self):
  before=copy.deepcopy(self.d);self.assertTrue(build.validate(self.d));self.assertTrue(validate_rosters(self.r,self.d))
  for p in self.pro:self.assertEqual(len(self.tables(p['person_id'])),5)
  self.assertEqual(self.d,before)

if __name__=='__main__':unittest.main(verbosity=2)
