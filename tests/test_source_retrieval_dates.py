"""Source retrieval dates do not imply person-wide review or invent classification access."""
import copy
import json
from pathlib import Path
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import build

class SourceRetrievalDateTests(unittest.TestCase):
 def setUp(self):
  self.d=json.loads((ROOT/'tests/fixtures/multischool.json').read_text())
  self.p=self.d['people'][1]
 def tables(self,updated_at='2099-12-31'):
  before=copy.deepcopy(self.p)
  tables=dict(build.department_tables([self.p],updated_at,self.d['institutions']))
  self.assertEqual(self.p,before)
  return tables
 def test_shared_strict_date_fixtures(self):
  for case in json.loads((ROOT/'tests/fixtures/source-retrieval-dates.json').read_text()):
   with self.subTest(case=case['name']):
    before=copy.deepcopy(case['person'])
    self.assertEqual(build.source_retrieval_date_summary(case['person']),case['expected'])
    self.assertEqual(case['person'],before)
 def test_overview_uses_source_range_and_explicit_whole_person_review_unknown(self):
  self.p['sources']=[{'retrieved_at':'2026-10-24'},{'retrieved_at':'2026-10-23'}]
  tables=self.tables();header,row=tables['总览']
  self.assertEqual(header[4],'已记录来源检索日期')
  self.assertEqual(row[4],'2026-10-23 至 2026-10-24')
  self.assertTrue(row[6].endswith('；人物整体核验日期未单独记录'))
  self.assertIn('分批核实资料，不是完整名录',row[6])
  self.assertEqual(list(tables),['总览','经历','导师','论文','来源'])
  self.assertEqual(len(header),11)
  self.assertEqual(tables,self.tables(updated_at='1800-01-01'))
 def test_unknown_summary_does_not_claim_the_person_is_unverified(self):
  self.p['sources']=[]
  row=self.tables()['总览'][1]
  self.assertEqual(row[4],'未知（来源日期未单独记录）')
  self.assertIn('人物整体核验日期未单独记录',row[6])
  self.assertNotIn('人物未核验',row[6])
 def test_classification_fallback_retains_url_role_and_id_but_never_invents_a_date(self):
  self.p['sources']=[{'id':'actual-source','url':self.p['official_url'],'retrieved_at':'2026-10-23','evidence_status':'official_page_read'}]
  url='https://example.test/classification'
  self.p['education']=[{'event_kind':'degree','institution_985':'yes','classification_source':url,'classification_checked_at':'2026-10-24'}]
  self.p['education'].append(copy.deepcopy(self.p['education'][0]))
  rows=self.tables()['来源']
  generated=[row for row in rows[1:] if row[2]==url]
  self.assertEqual(len(generated),1)
  self.assertEqual(generated[0][:5],[self.p['name'],'institution-classification-1',url,'历史985院校分类参考；非个人授位或就读当年建设身份的证明','未单独记录'])
  self.assertEqual(rows[1][1:5],['actual-source',self.p['official_url'],'official_page_read','2026-10-23'])
  self.assertEqual(rows[0][4],'查阅日期')
 def test_existing_classification_source_keeps_its_own_date_and_is_not_duplicated(self):
  url='https://example.test/classification'
  self.p['education']=[{'event_kind':'degree','institution_985':'yes','classification_source':url}]
  self.p['sources']=[{'id':'classification-recorded','url':url,'retrieved_at':'2025-12-31','evidence_status':'classification_reference'}]
  rows=[row for row in self.tables()['来源'][1:] if row[2]==url]
  self.assertEqual(len(rows),1)
  self.assertEqual(rows[0][1:5],['classification-recorded',url,'classification_reference','2025-12-31'])
 def test_default_availability_is_source_scoped_and_explicit_labels_are_preserved(self):
  for key in ['official_profile_availability_label','official_profile_link_label','official_profile_availability','official_profile_navigation_eligible']:self.p.pop(key,None)
  self.assertEqual(self.tables()['总览'][1][7],'公开个人页（访问与内容时效见来源记录）')
  self.p['official_profile_link_label']='合成本人网站'
  self.assertEqual(self.tables()['总览'][1][7],'合成本人网站；公开个人页（访问与内容时效见来源记录）')
  self.p['official_profile_availability_label']='保留显式说明'
  self.assertEqual(self.tables()['总览'][1][7],'保留显式说明')
  del self.p['official_profile_availability_label'];self.p['official_profile_navigation_eligible']=False
  self.assertEqual(self.tables()['总览'][1][7],'合成本人网站；个人主页当前不可用')
 def test_non_date_tables_and_stored_source_dates_do_not_depend_on_global_update_date(self):
  before=copy.deepcopy(self.p);first=self.tables('2026-10-23');second=self.tables('2099-12-31')
  self.assertEqual(first,second);self.assertEqual(self.p,before)
  self.assertEqual(first['总览'][1][3],self.p['official_url'])
  self.assertEqual(first['总览'][1][-2:],[self.p['school_id'],'测试乙校（虚构）'])
  for source,row in zip(self.p['sources'],first['来源'][1:]):
   self.assertEqual(row[2],source.get('url'));self.assertEqual(row[4],source.get('retrieved_at'))

if __name__=='__main__':unittest.main()
