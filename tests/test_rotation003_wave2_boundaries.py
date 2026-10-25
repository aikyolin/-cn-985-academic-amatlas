from published_fixture import published_root
"""General append, provenance-alias and conservative-navigation boundaries.
No per-person fixture duplication; historical goldens remain in earlier suites.
"""
import copy,hashlib,json,pathlib,unittest
from release26_history import release26_view
from release_history import CONTRACT,release25_view
ROOT=pathlib.Path(__file__).resolve().parents[1]
read=lambda name,root=ROOT:release26_view(json.loads((root/name).read_text()),name)
PINS={'data/atlas.json':'07d31cc1627dc341802a99c1e57d6ef8d29c82fd115ee0c882ffa9e29830a68d','data/rosters.json':'bdc4f7a400bb2b983d341b434b636aaf2f1beeb5f3aa070486a0aa44920fe27a','site/atlas.json':'8ce7435afda1486a9850ac8ffed16018b542e23c2fc337b71598cc2417fc4e80','site/rosters.json':'f11f1e1a40fd1b28211654fb1a2db4da83e78f28b1fcd96d9cb7e277ff0ae306','progress/work-queue.json':'829169fdf8815ddff328d1a3d324ad102bd52b0220a6025277e8d9fef8ebdaff'}
class Rotation003Wave2Boundaries(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.a=read('data/atlas.json');cls.r=read('data/rosters.json');cls.new=cls.a['people'][555:]
 def test_live_endpoint_and_generated_projection_are_exact(self):
  actual_site=json.loads((ROOT/'site/atlas.json').read_text());actual_data=json.loads((ROOT/'data/atlas.json').read_text())
  self.assertEqual(actual_site['people'],actual_data['people']);self.assertEqual(actual_site['pending_people'],actual_data['pending_people'])
  self.assertEqual(actual_site['build_id'],json.loads((ROOT/'site/rosters.json').read_text())['build_id'])
  for name,pin in PINS.items():self.assertEqual(hashlib.sha256((json.dumps(read(name,published_root() if name=='site/atlas.json' else ROOT),ensure_ascii=False,indent=2)+'\n').encode()).hexdigest(),pin,name)
  site=read('site/atlas.json',published_root());self.assertEqual(site['people'],self.a['people']);self.assertEqual(site['pending_people'],self.a['pending_people']);self.assertEqual(site['build_id'],read('site/rosters.json')['build_id']);self.assertEqual(len(site['exports']),114)
 def test_append_scope_is_exact_and_never_complete(self):
  self.assertEqual((len(self.a['people']),len(self.a['pending_people']),len(self.a['org_units']),len(self.r['entries']),len(self.r['source_observations'])),(564,84,234,1730,1768))
  self.assertEqual([p['school_id']for p in self.new],['lzu']*3+['nwsuaf']*3+['xjtu']*3)
  for p in self.new:self.assertTrue(p['detail_count_eligible']);self.assertFalse(p['fields_complete']);self.assertFalse(p['complete_profile_count_eligible']);self.assertFalse(p['include_in_current_faculty_count'])
  tasks=read('progress/work-queue.json')['tasks'];self.assertEqual(len(tasks),225)
  for t in tasks[222:]:self.assertEqual(t['status'],'partial');self.assertFalse(t['scope']['university_complete'])
 def test_historical_public_v1_json_bytes_reconstruct_from_current_prefixes(self):
  for rel,contract in CONTRACT.items():
   historical=release25_view(read(rel,published_root() if rel=='site/atlas.json' else ROOT),rel);raw=(json.dumps(historical,ensure_ascii=False,indent=2)+'\n').encode();self.assertEqual(hashlib.sha256(raw).hexdigest(),contract['byte_sha256'],rel)
 def test_projection_rejects_historical_leaf_and_unchanged_metadata_tampering(self):
  for rel in CONTRACT:
   raw=read(rel,published_root() if rel=='site/atlas.json' else ROOT);key='people'if 'people'in raw else 'entries'if 'entries'in raw else 'tasks';raw[key][0]['name']='unexpected alteration'
   with self.assertRaises(AssertionError):release25_view(raw,rel)
  raw=copy.deepcopy(self.a);raw['updated_at']='2099-01-01'
  with self.assertRaises(AssertionError):release25_view(raw,'data/atlas.json')
 def test_event_date_notes_are_source_bound_without_invented_intervals(self):
  dates=[(p,e)for p in self.new for e in p['education']if e.get('event_date')];self.assertEqual(len(dates),7)
  for p,e in dates:
   self.assertIsNone(e['start']);self.assertIsNone(e['end']);self.assertEqual(e['note'],'；'.join(x for x in [e['source_note'],'来源事件时点：'+e['event_date']+'（不是学习或任职起止区间）']if x));self.assertEqual(e['note_derivation_source_ids'],[e['field_provenance']['event_date']]);self.assertIn(e['field_provenance']['event_date'],{s['id']for s in p['sources']})
 def test_nondegree_and_unknown_awards_never_become_confirmed_degrees(self):
  events=[e for p in self.new for e in p['education']];self.assertEqual(len(events),44)
  self.assertEqual([sum(e['degree_awarded']is v for e in events)for v in [True,None,False]],[17,2,25])
  for e in events:
   if e['degree_awarded']is False:self.assertFalse(e['include_in_education_filters']);self.assertFalse(e['include_in_degree_filters'])
   if e['degree_awarded']is True:self.assertEqual(e['event_kind'],'degree')
   if e['degree_awarded']is None:self.assertFalse(e['include_in_degree_filters'])
 def test_candidate_layers_and_historical_mentor_navigation_remain_separate(self):
  mentors=[m for p in self.new for m in p['mentors']];self.assertEqual(len(mentors),1)
  self.assertEqual(sum(len(p.get('pending_mentor_candidates',[]))for p in self.new),2);self.assertEqual(sum(len(p.get('pending_education_candidates',[]))for p in self.new),1)
  for m in mentors:self.assertFalse(m['navigation_verified']);self.assertFalse(m['quick_link_eligible']);self.assertIsNone(m['official_url'])
 def test_unlinked_sampling_does_not_claim_direct_profile_or_current_department_match(self):
  rows=self.r['entries'][1721:];unlinked=[e for e in rows if e['official_profile_url']is None];self.assertEqual(len(unlinked),3)
  for e in unlinked:self.assertFalse(e['profile_identity_verified']);self.assertIsNone(e['verified_person_id']);self.assertTrue(e['independent_person_identity_reviewed']);self.assertTrue(e['profile_candidate_url']);self.assertNotEqual(e['profile_identity_evidence']['status'],'independent_current_official_profile_name_department_match');self.assertIn('本采样名录没有个人链接',''.join(e['notes']))
if __name__=='__main__':unittest.main()
