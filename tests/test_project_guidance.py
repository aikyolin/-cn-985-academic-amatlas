"""Project relationships are not degree mentors; all fixtures are synthetic and exports stay in memory."""
import copy
import json
import pathlib
import sys
import unittest
from unittest import mock
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import build

class ProjectGuidanceTests(unittest.TestCase):
 def setUp(self):
  self.d=json.loads((ROOT/'tests/fixtures/multischool.json').read_text())
  fixture=json.loads((ROOT/'tests/fixtures/project-guidance.json').read_text())
  self.p=self.d['people'][1];self.p['project_guidance']=fixture['project_guidance'];self.p['sources']=fixture['sources']
  self.p['education']=[dict(event_id=None,institution='不得借用的学历机构',degree='博士',event_kind='degree_study',degree_awarded=None,institution_985='unknown',region='unknown',start='1900-01',end='1901-01',source_url='https://b.example.test/education')]
  self.p['appointments']=[dict(title='不得借用的任职',institution='不得借用的任职机构',start='1800-01',end='1801-01',source_url='https://b.example.test/employment')]
 def tables(self):
  before=copy.deepcopy(self.d)
  with mock.patch.object(build,'Workbook',side_effect=AssertionError('XLSX writing forbidden')):
   tables=dict(build.department_tables([self.p],self.d['updated_at'],self.d['institutions']))
  self.assertEqual(self.d,before)
  return tables
 def test_valid_project_relationship_stays_outside_mentor_sheet(self):
  self.assertTrue(build.validate(self.d))
  tables=self.tables();self.assertEqual(list(tables),['总览','经历','导师','论文','来源'])
  self.assertEqual(len(tables['导师']),1)
  rows=[r for r in tables['经历'][1:] if r[1]=='project_guidance'];self.assertEqual(len(rows),1)
  row=rows[0];self.assertEqual(row[2],'项目指导（非学位师承）');self.assertIs(row[11],False)
  self.assertEqual(row[-2:],['pku','测试乙校（虚构）'])
  c=self.p['project_guidance'][0]
  for key in ['name','type_label','project_name','education_stage','relationship_scope','description','employment_status_note','note','scope_label','profile_source_url']:self.assertIn(c[key],row[14])
  self.assertIn('非学位师承，不计入导师统计或师承关系图',row[14]);self.assertEqual(row[16],c['source_url'])
 def test_null_or_absent_education_id_never_borrows_dates_or_institution(self):
  for event_id in [None,'','missing']:
   self.p['project_guidance'][0]['education_event_id']=event_id
   row=next(r for r in self.tables()['经历'][1:] if r[1]=='project_guidance')
   self.assertEqual(row[3:6],[None,None,None]);self.assertNotIn('不得借用',str(row));self.assertNotIn('1900',str(row));self.assertNotIn('1800',str(row))
 def test_project_own_explicit_dates_and_institution_are_kept_without_degree_inference(self):
  self.p['project_guidance'][0].update(start='2020',end='2021',institution='测试项目主办机构')
  row=next(r for r in self.tables()['经历'][1:] if r[1]=='project_guidance')
  self.assertEqual(row[3:6],['测试项目主办机构','2020','2021']);self.assertIs(row[11],False)
 def test_project_graph_count_and_degree_binding_guards_are_required(self):
  original=copy.deepcopy(self.d)
  mutations=[lambda c:c.update(include_in_mentorship_graph=True),lambda c:c.pop('include_in_mentorship_graph'),lambda c:c.update(include_in_verified_mentor_count=True),lambda c:c.pop('include_in_verified_mentor_count'),lambda c:c.update(education_event_id='test-degree-event'),lambda c:c.update(name=''),lambda c:c.update(source_url='javascript:unsafe()'),lambda c:c.update(source_id='missing'),lambda c:c.update(profile_source_id='missing')]
  for mutation in mutations:
   d=copy.deepcopy(original);mutation(d['people'][1]['project_guidance'][0])
   with self.assertRaises(AssertionError):build.validate(d)
 def test_project_advisor_cannot_be_put_back_into_the_main_mentor_collection(self):
  self.p['mentors'].append(copy.deepcopy(self.p['project_guidance'][0]));self.p['project_guidance']=[]
  with self.assertRaisesRegex(AssertionError,'Project guidance must stay separate'):build.validate(self.d)
 def test_source_sheet_preserves_both_chinese_level_and_technical_status(self):
  s=self.p['sources'][2];row=next(r for r in self.tables()['来源'][1:] if r[1]==s['id'])
  self.assertEqual(row[2],s['url']);self.assertIn(s['evidence_status_label'],row[3]);self.assertIn(s['evidence_status'],row[3]);self.assertEqual(row[-2:],['pku','测试乙校（虚构）'])
  self.assertEqual(build.source_evidence_text({'evidence_status':'old_status'}),'old_status')
  self.assertEqual(build.source_evidence_text({'evidence_label':'自述来源','evidence_status':'raw_status'}),'自述来源；raw_status')
 def test_legacy_records_without_project_collection_keep_original_row_counts(self):
  del self.p['project_guidance'];self.assertTrue(build.validate(self.d))
  tables=self.tables();self.assertEqual(len(tables['经历']),3);self.assertEqual(len(tables['导师']),1)

if __name__=='__main__':unittest.main()
