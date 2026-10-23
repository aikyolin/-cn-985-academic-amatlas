"""Independent professional guidance contract; synthetic fixtures and in-memory tables only."""
import copy
import json
import pathlib
import sys
import unittest
from unittest import mock
from jsonschema import Draft202012Validator

ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import build
import build_rosters


class ProfessionalGuidanceTests(unittest.TestCase):
 def setUp(self):
  self.d=json.loads((ROOT/'tests/fixtures/multischool.json').read_text())
  self.p=self.d['people'][1];self.p['education']=[];self.p['mentors']=[]
  self.p['appointments']=[dict(event_id=None,institution='不得借用的机构',title='不得借用的任职',start='1900-01',end='1901-01',source_url='https://b.example.test/job')]
  self.c=dict(name='职业指导者（虚构测试）',type='来源明确职业科研合作导师',type_label='职业科研指导（非学位）',relationship_kind='professional_research_advisor',relationship_status='verified_direct_statement',education_stage='科研助理教授任职阶段（非学位）',education_event_id=None,appointment_event_id=None,include_in_mentorship_graph=False,include_in_degree_mentorship_graph=False,include_in_verified_mentor_count=False,include_in_verified_professional_guidance_count=True,source_include_in_mentorship_graph=True,source_url='https://b.example.test/relation',source_id='professional-relation',profile_source_url='https://b.example.test/employment',profile_source_id='professional-profile',description='明确职业指导，不是普通合作',employment_status='unknown',official_url='https://b.example.test/advisor',person_id=None,start=None,end=None,note='关系备注',evidence_note='直接证据说明',scope_label='独立职业模块，不计学位师承',relationship_scope='职业科研指导范围')
  self.p['professional_research_advisors']=[self.c]
  self.p['sources']=[{'id':self.c['source_id'],'url':self.c['source_url']},{'id':self.c['profile_source_id'],'url':self.c['profile_source_url']}]
  self.schema=Draft202012Validator(json.loads((ROOT/'schema/atlas.schema.json').read_text()))

 def tables(self):
  before=copy.deepcopy(self.d)
  with mock.patch.object(build,'Workbook',side_effect=AssertionError('No XLSX allowed')),mock.patch.object(build,'build',side_effect=AssertionError('No build allowed')):
   t=dict(build.department_tables([self.p],self.d['updated_at'],self.d['institutions']))
  self.assertEqual(self.d,before)
  return t

 def test_valid_contract_and_original_source_graph_are_preserved(self):
  before=copy.deepcopy(self.d);self.schema.validate(self.d);self.assertTrue(build.validate(self.d));self.assertEqual(self.d,before)
  self.assertTrue(self.c['source_include_in_mentorship_graph']);self.assertFalse(self.c['include_in_mentorship_graph'])

 def test_schema_rejects_missing_required_semantics_and_wrong_types(self):
  required=['name','relationship_kind','relationship_status','education_event_id','include_in_mentorship_graph','include_in_degree_mentorship_graph','include_in_verified_mentor_count','include_in_verified_professional_guidance_count','source_url']
  for key in required:
   d=copy.deepcopy(self.d);del d['people'][1]['professional_research_advisors'][0][key]
   with self.subTest(key=key):self.assertFalse(self.schema.is_valid(d))
  for value in [None,{},'guidance']:
   d=copy.deepcopy(self.d);d['people'][1]['professional_research_advisors']=value
   self.assertFalse(self.schema.is_valid(d))
   with self.assertRaises(AssertionError):build.validate(d)

 def test_build_rejects_graph_count_stage_and_direct_evidence_drift(self):
  changes=[{'relationship_kind':'research_collaborator'},{'relationship_status':'candidate'},{'include_in_mentorship_graph':True},{'include_in_degree_mentorship_graph':True},{'include_in_verified_mentor_count':True},{'include_in_verified_professional_guidance_count':False},{'education_event_id':''},{'education_event_id':'borrow-degree'},{'name':'  '},{'source_url':'javascript:unsafe()'}]
  for change in changes:
   d=copy.deepcopy(self.d);d['people'][1]['professional_research_advisors'][0].update(change)
   with self.subTest(change=change),self.assertRaises(AssertionError):build.validate(d)
  del self.c['education_event_id']
  with self.assertRaisesRegex(AssertionError,'explicitly have no degree binding'):build.validate(self.d)

 def test_source_ids_resolve_and_match_their_exact_urls(self):
  for change in [{'source_id':'missing'},{'profile_source_id':'missing'},{'source_id':'professional-profile'},{'profile_source_id':'professional-relation'},{'source_ids':['missing']},{'source_ids':'professional-relation'}]:
   d=copy.deepcopy(self.d);d['people'][1]['professional_research_advisors'][0].update(change)
   with self.subTest(change=change),self.assertRaises(AssertionError):build.validate(d)
  self.c['source_ids']=['professional-relation','professional-profile'];self.assertTrue(build.validate(self.d))

 def test_appointment_reference_must_be_nonempty_known_and_never_an_implicit_null_join(self):
  for value in ['', ' ', 'missing']:
   self.c['appointment_event_id']=value
   with self.subTest(value=value),self.assertRaises(AssertionError):build.validate(self.d)
  self.c['appointment_event_id']=None;self.assertTrue(build.validate(self.d))
  self.p['appointments'][0]['event_id']='reviewed-job';self.c['appointment_event_id']='reviewed-job';self.assertTrue(build.validate(self.d))
  self.assertNotIn('1900',str(self.tables()['导师']))

 def test_active_guidance_requires_employment_evidence_or_explicit_navigation_limitation(self):
  self.c['employment_status']='active_officially_listed';self.assertTrue(build.validate(self.d))
  self.c['profile_source_url']=None
  with self.assertRaises(AssertionError):build.validate(self.d)
  self.c['profile_source_url']=self.p['sources'][1]['url'];self.c['official_url']=None
  with self.assertRaises(AssertionError):build.validate(self.d)
  self.c.update(quick_link_eligible=False,navigation_verified=False,profile_navigation_unavailable_reason='公开主页返回403，未再请求。')
  self.assertTrue(build.validate(self.d));row=self.tables()['导师'][1];self.assertEqual(row[7],'');self.assertIn('403',row[6]);self.assertEqual(row[5],'active_officially_listed')

 def test_explicit_false_and_nonactive_states_veto_shortcuts_but_keep_evidence(self):
  for status,flags in [('active_officially_listed',{'quick_link_eligible':False}),('active_officially_listed',{'navigation_verified':False}),('retired',{}),('deceased',{}),('unknown',{})]:
   self.c.update(employment_status=status,quick_link_eligible=True,navigation_verified=True);self.c.update(flags)
   row=self.tables()['导师'][1];self.assertEqual(row[7],'');self.assertEqual(row[8:10],[self.c['source_url'],self.c['profile_source_url']])
  self.c.update(employment_status='active_officially_listed');self.c.pop('quick_link_eligible');self.c.pop('navigation_verified');self.assertEqual(self.tables()['导师'][1][7],self.c['official_url'])

 def test_five_sheets_preserve_original_role_stage_scope_notes_and_only_own_dates(self):
  self.c.update(start='2020-03',end='2022-07',institution='独立明确机构')
  t=self.tables();self.assertEqual(list(t),['总览','经历','导师','论文','来源']);self.assertEqual(len(t['导师']),2)
  row=t['导师'][1];self.assertEqual(row[2],'职业科研指导（非学位）');self.assertEqual(row[3],self.c['education_stage']);self.assertEqual(row[4],self.c['description'])
  for key in ['type','type_label','relationship_kind','institution','start','end','relationship_scope','note','evidence_note','scope_label']:self.assertIn(self.c[key],row[6])
  self.assertIn('已核职业指导计数：1',row[6]);self.assertEqual(row[-2:],['pku','测试乙校（虚构）']);self.assertNotIn('不得借用',str(row));self.assertNotIn('1900',str(row))

 def test_null_absent_or_invalid_education_ids_never_borrow_dates_even_without_validation(self):
  for value in [None,'','unknown']:
   self.c['education_event_id']=value
   row=self.tables()['导师'][1];self.assertNotIn('1900',str(row));self.assertNotIn('不得借用',str(row))
  del self.c['education_event_id'];self.assertNotIn('1900',str(self.tables()['导师']))

 def test_independent_guidance_cannot_be_moved_into_ordinary_collaborators_or_unbound_mentors(self):
  for key in ['research_collaborators','mentors']:
   d=copy.deepcopy(self.d);p=d['people'][1];p[key]=p.pop('professional_research_advisors')
   with self.subTest(key=key),self.assertRaises(AssertionError):build.validate(d)

 def test_legacy_zhengwei_non_award_event_bound_guidance_stays_unchanged(self):
  d=json.loads((ROOT/'data/atlas.json').read_text());p=next(p for p in d['people'] if p['person_id']=='hit-WeiZheng');before=copy.deepcopy(p)
  occupational=[m for m in p['mentors'] if m.get('relationship_kind')=='professional_research_advisor'];self.assertEqual(len(occupational),2)
  for m in occupational:
   self.assertEqual(m['relationship_kind'],'professional_research_advisor');e=next(e for e in p['education'] if e.get('event_id')==m['education_event_id']);self.assertIs(e['degree_awarded'],False);self.assertEqual(e['event_kind'],'professional_research')
  self.assertTrue(build.validate(d));self.assertEqual(p,before)

 def test_pending_profiles_cannot_count_verified_professional_guidance(self):
  pending=copy.deepcopy(self.p);pending.update(person_id='pending-professional-test',profile_status='profile_details_pending',roster_entry_id='pending-test');self.d['pending_people']=[pending]
  self.assertFalse(self.schema.is_valid(self.d))
  with self.assertRaisesRegex(AssertionError,'outside confirmed collections'):build.validate(self.d)

 def test_optional_empty_collection_keeps_legacy_tables(self):
  del self.p['professional_research_advisors'];self.assertTrue(build.validate(self.d));self.schema.validate(self.d);self.assertEqual(len(self.tables()['导师']),1)
  self.p['professional_research_advisors']=[];self.assertTrue(build.validate(self.d));self.assertEqual(len(self.tables()['导师']),1)

 def test_unavailable_or_unidentified_profiles_export_separate_reports_without_confirming_roster_identity(self):
  for state,label in [('not_identified','未确认独立个人主页，原URL为官方职业报道'),('unavailable',None)]:
   self.p.update(official_profile_availability=state,official_profile_navigation_eligible=False,own_profile_academic_body_read=False,professional_evidence_body_read=True,alternative_professional_sources=[dict(url='https://ciee.cau.edu.cn/reviewed-news',title='官方职业报道（非个人主页）',source_id='report')])
   if label:self.p['official_profile_availability_label']=label
   else:self.p.pop('official_profile_availability_label',None)
   self.p['sources'].append(dict(id='report',url='https://ciee.cau.edu.cn/reviewed-news'))
   row=self.tables()['总览'][1];self.assertEqual(row[3],'');self.assertEqual(row[7],label or '个人主页当前不可用');self.assertIn('官方职业报道（非个人主页）',row[8]);self.assertIn('ciee.cau.edu.cn',row[8])
   entry=dict(name=self.p['name'],school_id=self.p['school_id'],organization_id=self.p['department_id'],official_profile_url=None,profile_identity_verified=False,verified_person_id=None,roster_source_url='https://b.example.test/roster')
   self.assertFalse(build_rosters._verified_profile_match(entry,self.p))


if __name__=='__main__':unittest.main()
