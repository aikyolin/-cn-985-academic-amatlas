"""All added people are in-memory synthetic fixtures, never public data or XLSX."""
import copy
import json
import pathlib
import sys
import unittest
from unittest import mock
from jsonschema.exceptions import ValidationError
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import build
import build_rosters
import validate_queue as queue

class NewSchoolGuards(unittest.TestCase):
 def setUp(self):
  self.atlas=json.loads((ROOT/'tests/fixtures/multischool.json').read_text())
  template=copy.deepcopy(self.atlas['people'][1]);r=self.atlas['rosters']
  for sid in ['fdu','nju','ustc','buaa','nku']:
   self.atlas['institutions'].append(dict(id=sid,official_name=sid+'测试学校（虚构）',official_url=f'https://{sid}.example.test/'))
   for suffix in (['cs','cyber'] if sid=='nku' else ['test']):
    oid=f'{sid}-synthetic-{suffix}'
    self.atlas['org_units'].append(dict(id=oid,school_id=sid,name='测试平级学院（虚构）',type='学院',parent_id=sid,campus_ids=[],source_url=f'https://{sid}.example.test/{suffix}'))
    p=copy.deepcopy(template);p.update(person_id=oid+'-person',school_id=sid,name=oid+'测试人物（虚构）',department_id=oid,department='测试平级学院（虚构）',campus_ids=[],official_url=f'https://{sid}.example.test/{suffix}/person');self.atlas['people'].append(p)
    e=copy.deepcopy(r['entries'][1]);e.update(id=oid+'-roster',school_id=sid,organization_id=oid,name=p['name'],campus_id=None,roster_source_url=f'https://{sid}.example.test/{suffix}/roster');r['entries'].append(e)
    r['coverage'].append(dict(school_id=sid,organization_id=oid,category='测试类别',visible_name_count=1,url=e['roster_source_url']))
    r['summary'].append(dict(school_id=sid,organization_id=oid,visible_roster_entries=1))
  r['totals'].update(record_count=len(r['entries']),raw_observation_count=len(r['entries']),entries_without_profile_link=len(r['entries']),entries_with_profile_link=0)
  task=dict(task_id='nku:synthetic:cs',institution_id='nku',organization_id='nku-synthetic-cs',campus_ids=[],stage='profile_research',status='pending',scope=dict(description='Synthetic test only',claim='listed_public_scope_only',university_complete=False),depends_on=[],source_urls=['https://nku.example.test/cs'],artifact_paths=[],review_status='pending_review',next_action='Review synthetic fixture')
  self.q=dict(schema_version='1.0',updated_at='2026-10-23T09:00:00Z',base_commit='a'*40,scope=dict(active_institution='hit',active_institutions=['nku'],target_university_count=39,registry_complete=False),tasks=[task])
 def check(self,q=None,root=None):
  # Serialize the synthetic atlas into its own complete transport; never borrow live chunks.
  import tempfile
  from atlas_test_io import write_atlas
  q=self.q if q is None else q;before=copy.deepcopy((q,self.atlas))
  with tempfile.TemporaryDirectory() as temp:
   actual_root=pathlib.Path(temp) if root is None else root
   write_atlas(actual_root/'data/atlas.json',self.atlas)
   result=queue.validate_queue(q,actual_root)
  self.assertEqual((q,self.atlas),before);return result
 def test_active_scope_optional_and_legacy_hit_field_is_not_a_school_default(self):
  self.assertEqual(self.check(),[])
  del self.q['scope']['active_institutions'];self.assertEqual(self.check(),[])
  self.assertEqual(self.q['tasks'][0]['institution_id'],'nku')
 def test_active_scope_requires_nonempty_unique_safe_string_ids(self):
  for value in [[],['nku','nku'],'nku',[None],[''],['../nku'],['nku/cs'],['nku x']]:
   with self.subTest(value=value):
    self.q['scope']['active_institutions']=value
    with self.assertRaises(ValidationError):self.check()
 def test_unknown_active_school_and_out_of_scope_task_are_rejected(self):
  self.q['scope']['active_institutions']=['missing']
  with self.assertRaisesRegex(ValueError,'Unknown active institution'):self.check()
  self.q['scope']['active_institutions']=['fdu']
  with self.assertRaisesRegex(ValueError,'outside active scope'):self.check()
 def test_unknown_task_school_is_not_filled_from_hit_compatibility(self):
  del self.q['scope']['active_institutions'];self.q['tasks'][0]['institution_id']='missing'
  with self.assertRaisesRegex(ValueError,'Unknown task institution'):self.check()
 def test_cross_school_or_missing_organization_rejected(self):
  for oid in ['hit-test-computing','fdu-synthetic-test','missing','']:
   with self.subTest(organization=oid):
    self.q['tasks'][0]['organization_id']=oid
    with self.assertRaisesRegex(ValueError,'task organization'):self.check()
 def test_null_organization_and_empty_campus_are_explicitly_allowed(self):
  self.q['tasks'][0]['organization_id']=None;self.assertEqual(self.check(),[])
 def test_cross_school_campus_and_hit_alias_are_rejected_for_new_school(self):
  for cid in ['harbin','hit-harbin','fdu-synthetic-campus','missing']:
   with self.subTest(campus=cid):
    self.q['tasks'][0]['campus_ids']=[cid]
    with self.assertRaisesRegex(ValueError,'task campus'):self.check()
 def test_new_campus_is_checked_against_its_actual_school(self):
  self.atlas['campuses'].append(dict(id='nku-synthetic-campus',school_id='nku',name='测试校区（虚构）'))
  self.q['tasks'][0]['campus_ids']=['nku-synthetic-campus'];self.assertEqual(self.check(),[])
  self.atlas['campuses'][-1]['school_id']='fdu'
  with self.assertRaisesRegex(ValueError,'task campus'):self.check()
 def test_legacy_hit_campus_aliases_remain_supported_without_mutation(self):
  self.q['scope']['active_institutions']=['hit'];t=self.q['tasks'][0];t.update(institution_id='hit',organization_id='hit-test-computing')
  for suffix in ['weihai','shenzhen']:self.atlas['campuses'].append(dict(id=suffix,school_id='hit',name='历史校区别名测试（虚构）'))
  for cid in ['harbin','weihai','shenzhen','hit-harbin','hit-weihai','hit-shenzhen']:
   t['campus_ids']=[cid];self.assertEqual(self.check(),[]);self.assertEqual(t['campus_ids'],[cid])
 def test_registry_is_loaded_from_the_passed_root_not_another_snapshot(self):
  import tempfile
  with tempfile.TemporaryDirectory() as temp:
   self.assertEqual(self.check(root=pathlib.Path(temp)),[])
 def test_peer_departments_in_one_school_keep_distinct_task_targets(self):
  second=copy.deepcopy(self.q['tasks'][0]);second.update(task_id='nku:synthetic:cyber',organization_id='nku-synthetic-cyber');self.q['tasks'].append(second)
  self.assertEqual(self.check(),[]);self.assertEqual([t['organization_id'] for t in self.q['tasks']],['nku-synthetic-cs','nku-synthetic-cyber'])
 def test_new_school_scope_and_peer_department_manifests_are_not_first_unit_based(self):
  before=copy.deepcopy(self.atlas);self.assertTrue(build.validate(self.atlas));self.assertTrue(build_rosters.validate_rosters(self.atlas['rosters'],self.atlas))
  exports=build.department_exports(self.atlas);nku=[e for e in exports if e['school_id']=='nku'];self.assertEqual({e['department_id'] for e in nku},{'nku-synthetic-cs','nku-synthetic-cyber'})
  with mock.patch.object(build,'Workbook',side_effect=AssertionError('XLSX forbidden')):
   for ex in exports:
    people=[p for p in self.atlas['people'] if p['department_id']==ex['department_id'] and p['school_id']==ex['school_id']]
    tables=dict(build.department_tables(people,self.atlas['updated_at'],self.atlas['institutions']))
    self.assertEqual(ex['people_count'],1);self.assertEqual(len(tables['总览']),2);self.assertEqual(tables['总览'][1][0],people[0]['name']);self.assertEqual(tables['总览'][1][-2:],[ex['school_id'],ex['school_name']])
  self.assertEqual(self.atlas,before)
 def test_same_school_mixed_departments_fail_with_actionable_error(self):
  people=[p for p in self.atlas['people'] if p['school_id']=='nku']
  with self.assertRaisesRegex(AssertionError,'cannot mix departments.*group people by department_id'):build.department_tables(people,self.atlas['updated_at'],self.atlas['institutions'])
 def test_missing_department_id_cannot_silently_enter_an_export(self):
  p=copy.deepcopy(self.atlas['people'][-1]);del p['department_id']
  with self.assertRaisesRegex(AssertionError,'omit department IDs'):build.department_tables([p],self.atlas['updated_at'],self.atlas['institutions'])


 def test_book_export_prefers_chinese_labels_and_preserves_raw_types_without_new_counts(self):
  p=copy.deepcopy(self.atlas['people'][-1]);labels={
   'official_profile_mentions_book_only':'官方个人页仅提及著作，未核出版商落地页或全文。',
   'official_author_book_metadata_verified':'作者官方职业页面的著作书目元数据已核，不表示出版商页面或全文已读。'}
  p['publications']=[dict(title='合成测试著作',type='book',type_label='学术著作（非期刊或会议论文）',link_status=status,link_status_label=label,source_url='https://nku.example.test/books') for status,label in labels.items()]
  before=copy.deepcopy(p)
  with mock.patch.object(build,'Workbook',side_effect=AssertionError('XLSX forbidden')):tables=dict(build.department_tables([p],self.atlas['updated_at'],self.atlas['institutions']))
  self.assertEqual(list(tables),['总览','经历','导师','论文','来源']);self.assertEqual(len(tables['论文']),3)
  for row,(status,label) in zip(tables['论文'][1:],labels.items()):
   self.assertEqual(row[5],'学术著作（非期刊或会议论文）；book');self.assertEqual(row[8],label+'；'+status)
  self.assertEqual(p,before)
 def test_unlabelled_publication_export_preserves_legacy_values_and_does_not_invent_verification(self):
  for key in ['type','link_status','title']:
   for raw in [None,'','unknown_status','official_publication_list_only','book']:
    self.assertEqual(build.publication_value({key:raw},key),raw)
  self.assertEqual(build.publication_value(dict(type='book',type_label='book'),'type'),'book')
  self.assertEqual(build.publication_value(dict(type_label='著作'),'type'),'著作')

if __name__=='__main__':unittest.main()
