import copy,json,pathlib,sys,unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import build
class TeachingFactsTests(unittest.TestCase):
 def setUp(self):
  self.d=json.loads((ROOT/'tests/fixtures/multischool.json').read_text());self.p=self.d['people'][1]
  self.fact={'name':'公开教学测试','role':'主讲课程','start':'2002','source_id':'teaching-test','source_url':'https://b.example.test/teaching','note':'教学开设非任职起点'}
  self.p['sources'].append({'id':'teaching-test','url':self.fact['source_url']});self.p['teaching']=[self.fact]
 def test_valid_teaching_does_not_change_existing_collections(self):
  before={k:copy.deepcopy(self.p.get(k)) for k in ['education','appointments','mentors','publications']};self.assertTrue(build.validate(self.d));self.assertEqual(before,{k:self.p.get(k) for k in before})
 def test_teaching_summary_only_existing_overview_scope_cell(self):
  before=copy.deepcopy(self.p);tables=build.department_tables([self.p],self.d['updated_at'],self.d['institutions']);self.assertEqual(len(tables),5);self.assertIn('公开教学事实',tables[0][1][1][6]);self.assertIn('2002',tables[0][1][1][6]);self.assertIn('不是入学',tables[0][1][1][6]);self.assertEqual(self.p,before)
 def test_invalid_evidence_rejected(self):
  for patch in [{'source_id':'missing'},{'source_url':'https://b.example.test/wrong'},{'source_url':'javascript:alert(1)'},{'name':''},{'role':''}]:
   d=copy.deepcopy(self.d);d['people'][1]['teaching'][0].update(patch)
   with self.assertRaises(AssertionError):build.validate(d)
 def test_teaching_cannot_bind_degrees_or_mentor_edges(self):
  for key,value in [('degree_awarded',True),('include_in_mentorship_graph',True),('include_in_verified_mentor_count',True),('include_in_education_count',True),('include_in_appointment_count',True),('include_in_publication_count',True),('education_event_id','degree-1'),('appointment_event_id','job-1')]:
   d=copy.deepcopy(self.d);d['people'][1]['teaching'][0][key]=value
   with self.assertRaises(AssertionError):build.validate(d)
 def test_absent_and_null_teaching_are_compatible(self):
  self.p['teaching']=None;self.assertTrue(build.validate(self.d));self.assertEqual(build.teaching_summary(self.p),'');del self.p['teaching'];self.assertTrue(build.validate(self.d))

 def test_historical_affiliation_in_existing_overview_cell(self):
  self.p['sampling_affiliation_label']='历史名录关联非当前在职'
  self.p['current_employment']={'institution':'其他已核单位','source_url':'https://current.example.test/person','note':'是否兼任未知'}
  tables=build.department_tables([self.p],self.d['updated_at'],self.d['institutions'])
  self.assertEqual(len(tables),5)
  for value in ['历史名录关联非当前在职','其他已核单位','https://current.example.test/person','是否兼任未知']:self.assertIn(value,tables[0][1][1][6])
