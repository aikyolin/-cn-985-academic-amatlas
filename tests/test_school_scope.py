"""School-scoped history must coexist with independent full-canonical validation."""
from atlas_test_io import load_atlas
import copy,json,pathlib,sys,unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from build import validate
from build_rosters import validate_rosters
from school_scope import hit_atlas,hit_rosters,hit_export_rows

class HistoricalSchoolScopeTests(unittest.TestCase):
 def setUp(self):
  self.atlas=load_atlas(ROOT/'data/atlas.json')
  self.rosters=json.loads((ROOT/'data/rosters.json').read_text())
 def test_full_canonical_is_still_validated_without_school_filter(self):
  self.assertTrue(validate(self.atlas));self.assertTrue(validate_rosters(self.rosters,self.atlas))
  import jsonschema
  validator=jsonschema.Draft202012Validator(json.loads((ROOT/'schema/atlas.schema.json').read_text()),format_checker=jsonschema.FormatChecker())
  validator.validate(self.atlas)
  site=load_atlas(ROOT/'site/atlas.json');rosters=json.loads((ROOT/'site/rosters.json').read_text())
  self.assertTrue(validate(site));self.assertTrue(validate_rosters(rosters,site));validator.validate(site)
  for key in ['institutions','campuses','org_units','people','pending_people']:
   self.assertEqual(self.atlas[key],site[key],key)
  self.assertEqual(site['build_id'],rosters['build_id']);self.assertTrue(site['build_id'])
 def test_global_roster_counters_remain_checked_separately(self):
  r=self.rosters;t=r['totals']
  self.assertEqual(t['record_count'],len(r['entries']))
  self.assertEqual(t['raw_observation_count'],len(r['source_observations']))
  self.assertEqual(t['organization_count'],len({e['organization_id'] for e in r['entries']}))
  self.assertEqual(t['category_count'],len({(c['organization_id'],c['category']) for c in r['coverage']}))
  self.assertEqual(t['coverage_unit_count'],len(r['coverage']))
  self.assertEqual(t['entries_with_profile_link'],sum(bool(e['official_profile_url']) for e in r['entries']))
  self.assertEqual(t['entries_without_profile_link'],sum(not e['official_profile_url'] for e in r['entries']))
 def test_foreign_school_same_names_cannot_change_hit_evidence_view(self):
  original=copy.deepcopy(self.atlas);baseline=hit_atlas(self.atlas);extra=copy.deepcopy(self.atlas)
  extra['institutions'].append({'id':'testscope','official_name':'测试专用虚构大学','official_url':'https://test.example/'})
  for key in ['campuses','org_units','people','pending_people']:
   row=copy.deepcopy(next(r for r in self.atlas[key] if r.get('school_id')=='hit'))
   row['school_id']='testscope'
   for id_key in ['id','person_id','department_id','organization_id']:
    if id_key in row:row[id_key]='testscope-'+row[id_key]
   extra[key].insert(0,row)
  self.assertEqual(hit_atlas(extra),baseline)
  self.assertEqual(self.atlas,original)
  self.assertEqual([len(baseline['people']),len(baseline['pending_people'])],[257,42])
 def test_foreign_roster_rows_and_counts_cannot_change_hit_evidence_view(self):
  baseline=hit_rosters(self.rosters);extra=copy.deepcopy(self.rosters)
  for key,rows in extra.items():
   if isinstance(rows,list) and rows and isinstance(rows[0],dict):
    row=copy.deepcopy(rows[0]);row['school_id']='testscope';rows.insert(0,row)
  # Simulate changed full-library totals. Scoped counters must derive from HIT
  # records and coverage, never take the foreign-inclusive global total.
  for key in ['record_count','raw_observation_count','entries_with_profile_link','organization_count','category_count','coverage_unit_count']:
   extra['totals'][key]+=1
  self.assertEqual(hit_rosters(extra),baseline)
  self.assertEqual(len(baseline['entries']),1381)
  self.assertEqual(len(baseline['source_observations']),1419)
 def test_export_scope_never_infers_school_from_name_or_prefix(self):
  rows=[['姓名','组织ID','所属学校ID'],['同名测试','hit-unit','hit'],['同名测试','hit-misleading-prefix','pku']]
  self.assertEqual(len(hit_export_rows(rows,{'hit-unit','hit-misleading-prefix'})),2)
  legacy=[['姓名','组织ID'],['同名测试','verified-hit-unit'],['同名测试','hit-not-a-known-unit']]
  self.assertEqual(hit_export_rows(legacy,{'verified-hit-unit'}),legacy[:2])

if __name__=='__main__':unittest.main()
