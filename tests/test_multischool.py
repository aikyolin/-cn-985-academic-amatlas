from atlas_test_io import read_live_json
"""Synthetic multi-school coverage; fixtures must never enter public snapshots."""
from atlas_test_io import load_atlas
import copy, hashlib, json, pathlib, sys, unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from build import validate, department_tables, department_exports
from build_rosters import validate_rosters, roster_tables, _verified_profile_match

class MultiSchoolTests(unittest.TestCase):
 def setUp(self): self.d=json.loads((ROOT/'tests/fixtures/multischool.json').read_text())
 def test_two_schools_same_name_units_and_no_campus(self):
  self.assertTrue(validate(self.d))
  self.assertTrue(validate_rosters(self.d['rosters'],self.d))
  import jsonschema
  jsonschema.Draft202012Validator(json.loads((ROOT/'schema/atlas.schema.json').read_text()),format_checker=jsonschema.FormatChecker()).validate(self.d)
  units=[o for o in self.d['org_units'] if o['name']=='同名测试学院（虚构）']
  self.assertEqual(len(units),2);self.assertEqual(len({o['id'] for o in units}),2)
  self.assertEqual(self.d['people'][1]['campus_ids'],[])
 def test_cross_school_person_department_rejected(self):
  self.d['people'][1]['department_id']='hit-test-computing'
  with self.assertRaisesRegex(AssertionError,'person department'):validate(self.d)
 def test_cross_school_org_parent_rejected(self):
  self.d['org_units'][-1]['parent_id']='hit-test-computing'
  with self.assertRaisesRegex(AssertionError,'organization parent'):validate(self.d)
 def test_cross_school_person_campus_rejected(self):
  self.d['people'][1]['campus_ids']=['harbin']
  with self.assertRaisesRegex(AssertionError,'campus reference'):validate(self.d)
 def test_new_school_campus_must_be_prefixed(self):
  self.d['campuses'].append({'id':'pku-test-campus','school_id':'pku','name':'乙测试校区（虚构）'})
  self.d['people'][1]['campus_ids']=['pku-test-campus'];self.assertTrue(validate(self.d))
  self.d['campuses'][-1]['id']='nonprefixed'
  with self.assertRaisesRegex(AssertionError,'school-prefixed'):validate(self.d)
 def test_duplicate_global_org_id_and_path_traversal_rejected(self):
  original=copy.deepcopy(self.d)
  self.d['org_units'][-1]['id']='hit-test-computing'
  with self.assertRaisesRegex(AssertionError,'Duplicate organization'):validate(self.d)
  for bad in ['../bad','unit/escape','..','evil.xlsx?x=1']:
   self.d=copy.deepcopy(original);self.d['org_units'][-1]['id']=bad
   with self.assertRaisesRegex(AssertionError,'Unsafe organization'):department_exports(self.d)
 def test_no_school_or_campus_is_silently_defaulted(self):
  del self.d['people'][1]['school_id']
  with self.assertRaisesRegex(AssertionError,'Unknown record school'):validate(self.d)
 def test_roster_school_mismatch_rejected(self):
  self.d['rosters']['entries'][1]['school_id']='hit'
  with self.assertRaisesRegex(AssertionError,'Cross-school roster organization'):validate_rosters(self.d['rosters'],self.d)
 def test_roster_campus_mismatch_rejected(self):
  self.d['rosters']['entries'][1]['campus_id']='hit-harbin'
  with self.assertRaisesRegex(AssertionError,'Cross-school roster campus'):validate_rosters(self.d['rosters'],self.d)
 def test_roster_identity_cannot_cross_schools(self):
  person=self.d['people'][1];entry=dict(self.d['rosters']['entries'][1],name=person['name'],official_profile_url=person['official_url'])
  self.assertTrue(_verified_profile_match(entry,person))
  entry['school_id']='hit';self.assertFalse(_verified_profile_match(entry,person))
 def test_department_exports_are_scoped_and_self_identifying(self):
  original=copy.deepcopy(self.d);exports=department_exports(self.d)
  self.assertEqual(len(exports),2);self.assertEqual([x['people_count'] for x in exports],[1,1])
  self.assertEqual({x['school_id'] for x in exports},{'hit','pku'})
  for e in exports:
   people=[p for p in self.d['people'] if p['department_id']==e['department_id']]
   tables=department_tables(people,self.d['updated_at'],self.d['institutions'])
   for _,rows in tables:
    self.assertEqual(rows[0][-2:],['所属学校ID','所属学校'])
    for row in rows[1:]:self.assertEqual(row[-2:],[e['school_id'],e['school_name']])
  self.assertEqual(self.d,original)
 def test_mixed_school_export_fails_closed(self):
  with self.assertRaisesRegex(AssertionError,'cannot mix schools'):department_tables(self.d['people'],self.d['updated_at'],self.d['institutions'])
 def test_export_without_registry_never_invents_school_label(self):
  rows=dict(department_tables([self.d['people'][1]],self.d['updated_at']))['总览']
  self.assertEqual(rows[1][-2:],['pku','pku']);self.assertIn('校区未标注',rows[1])
 def test_roster_export_school_columns_follow_each_record(self):
  rows=roster_tables(self.d['rosters'],self.d)['待核对名录']
  self.assertEqual(rows[0][-2:],['所属学校ID','所属学校'])
  self.assertEqual(rows[1][-2:],['hit','测试甲校（虚构）']);self.assertEqual(rows[2][-2:],['pku','测试乙校（虚构）'])
 def test_hit_migration_preserves_every_existing_fact_and_evidence(self):
  data=load_atlas(ROOT/'data/atlas.json')
  expected={
   'campuses':'85c2067edcd0bd8727fbd4dd1ec93c9c27bd45c30e209691164c328c06fbb6cd',
   'org_units':'a08b297daa383fd9c5409bb828e8bb3b3cb95187d0933ac0677d56d5dcf428ca',
   'people':'808e68b9dbf13375d7faa1d7ac899fc9596822c30e7419c9cd9c26cbfc158954',
   'pending_people':'89a71e4a33abc590a5ba085c88dd3a92ab067185b8c07bb16024ff812eac6d5b'
  }
  for key,digest in expected.items():
   rows=[{k:v for k,v in row.items() if k!='school_id'} for row in data[key] if row.get('school_id')=='hit']
   actual=hashlib.sha256(json.dumps(rows,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
   self.assertEqual(actual,digest,key)
 def test_test_people_never_enter_public_data(self):
  for file in ['data/atlas.json','site/atlas.json','data/rosters.json','site/rosters.json']:
   content=json.dumps(read_live_json(ROOT/file),ensure_ascii=False);self.assertNotIn('synthetic-person',content);self.assertNotIn('测试甲校（虚构）',content)

if __name__=='__main__':unittest.main()
