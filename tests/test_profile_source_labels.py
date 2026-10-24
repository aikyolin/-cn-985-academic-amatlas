"""Explicit source labels only; in-memory Excel matrices, no host-based evidence inference."""
import copy,json,pathlib,sys,unittest
from unittest import mock
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import build

class ProfileSourceLabelTests(unittest.TestCase):
 def setUp(self):
  self.d=json.loads((ROOT/'tests/fixtures/multischool.json').read_text());self.p=self.d['people'][1]
  self.p.update(official_url='https://synthetic-scholar.github.io/',official_url_kind='self_authored_professional_profile_linked_by_official',official_profile_link_label='官方名录关联的本人职业网站',official_profile_availability_label='官方名录关联的本人职业网站（非学校域名官网）')
 def tables(self):
  before=copy.deepcopy(self.d)
  with mock.patch.object(build,'Workbook',side_effect=AssertionError('No XLSX')),mock.patch.object(build,'build',side_effect=AssertionError('No build')):t=dict(build.department_tables([self.p],self.d['updated_at'],self.d['institutions']))
  self.assertEqual(self.d,before);return t
 def test_explicit_self_authored_profile_uses_neutral_heading_and_precise_availability_label(self):
  t=self.tables();header,row=t['总览'];self.assertEqual(list(t),['总览','经历','导师','论文','来源']);self.assertEqual(len(header),11);self.assertEqual(header[3],'个人主页／职业网站（来源类型见说明）');self.assertEqual(row[3],self.p['official_url']);self.assertEqual(row[7],self.p['official_profile_availability_label']);self.assertEqual(header[8],'替代职业资料来源（非已核个人主页）');self.assertEqual(row[-2:],['pku','测试乙校（虚构）'])
 def test_link_label_alone_is_preserved_in_availability_column(self):
  del self.p['official_profile_availability_label'];row=self.tables()['总览'][1];self.assertIn(self.p['official_profile_link_label'],row[7]);self.assertIn('访问与内容时效见来源记录',row[7])
 def test_legacy_no_label_keeps_old_headers_values_and_external_url_without_guessing_its_level(self):
  for k in ['official_profile_link_label','official_profile_availability_label']:self.p.pop(k)
  header,row=self.tables()['总览'];self.assertEqual(header[3],'官方主页');self.assertEqual(header[8],'替代官方职业报道（非个人主页）');self.assertEqual(row[7],'公开个人页（访问与内容时效见来源记录）');self.assertEqual(row[3],'https://synthetic-scholar.github.io/')
 def test_disabled_homepage_stays_blank_despite_explicit_labels(self):
  for flags in [{'official_profile_navigation_eligible':False},{'official_profile_availability':'unavailable'}]:
   self.p.update(flags);self.assertEqual(self.tables()['总览'][1][3],'')
 def test_ccf_and_school_news_keep_their_exact_separate_titles(self):
  self.p.update(official_profile_availability='unavailable',official_profile_navigation_eligible=False,official_profile_availability_label='学校门户访问受限',alternative_professional_sources=[{'url':'https://www.ccf.org.cn/test-profile','title':'CCF 学会官方职业简介（非学校个人主页）'},{'url':'https://news.example.test/reviewed-career','title':'学校官方职业报道（非个人主页）'}]);header,row=self.tables()['总览'];self.assertEqual(row[3],'');self.assertEqual(header[8],'替代职业资料来源（非已核个人主页）')
  for s in self.p['alternative_professional_sources']:self.assertIn(s['title']+'：'+s['url'],row[8])
 def test_self_authored_source_level_stays_in_source_sheet_not_alternative_university_reports(self):
  self.p['sources']=[{'id':'personal-source','url':'https://synthetic-scholar.github.io/about','evidence_status':'self_authored_professional_website','evidence_status_label':'本人职业网站正文已读（非学校域名官网）'}];t=self.tables();self.assertEqual(t['总览'][1][8],'');row=t['来源'][1];self.assertIn('本人职业网站正文已读（非学校域名官网）',row[3]);self.assertIn('self_authored_professional_website',row[3]);self.assertEqual(row[2],self.p['sources'][0]['url'])

if __name__=='__main__':unittest.main()
