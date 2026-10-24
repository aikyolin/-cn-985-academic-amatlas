"""General append, provenance-alias and conservative-navigation boundaries.
No per-person fixture duplication; historical goldens remain in earlier suites.
"""
import copy,hashlib,json,pathlib,unittest
from release_history import CONTRACT,release25_view
ROOT=pathlib.Path(__file__).resolve().parents[1]
read=lambda name:json.loads((ROOT/name).read_text())
PINS={'data/atlas.json':'4a2caaf803967d671bf0bb6b3aeb7c661eecaa40e7bf74e31c214215a3fecc93','data/rosters.json':'0bcddfc6661b2926ef1560b9ffa689fe37e818e1c821abf54dd0de962f1a834f','site/atlas.json':'f0f46d4cba67eec805f944e2bef431120b38016465afcdd1227cf6e7fd4a6861','site/rosters.json':'509f98b11edd2fdfe3a80ef1b0de0d07d46d2f186ed29c363e3e8ebe293168b0','progress/work-queue.json':'829169fdf8815ddff328d1a3d324ad102bd52b0220a6025277e8d9fef8ebdaff'}
class Rotation003Wave2Boundaries(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.a=read('data/atlas.json');cls.r=read('data/rosters.json');cls.new=cls.a['people'][555:]
 def test_live_endpoint_and_generated_projection_are_exact(self):
  for name,pin in PINS.items():self.assertEqual(hashlib.sha256((ROOT/name).read_bytes()).hexdigest(),pin,name)
  site=read('site/atlas.json');self.assertEqual(site['people'],self.a['people']);self.assertEqual(site['pending_people'],self.a['pending_people']);self.assertEqual(site['build_id'],read('site/rosters.json')['build_id']);self.assertEqual(len(site['exports']),114)
 def test_append_scope_is_exact_and_never_complete(self):
  self.assertEqual((len(self.a['people']),len(self.a['pending_people']),len(self.a['org_units']),len(self.r['entries']),len(self.r['source_observations'])),(564,84,234,1730,1768))
  self.assertEqual([p['school_id']for p in self.new],['lzu']*3+['nwsuaf']*3+['xjtu']*3)
  for p in self.new:self.assertTrue(p['detail_count_eligible']);self.assertFalse(p['fields_complete']);self.assertFalse(p['complete_profile_count_eligible']);self.assertFalse(p['include_in_current_faculty_count'])
  tasks=read('progress/work-queue.json')['tasks'];self.assertEqual(len(tasks),225)
  for t in tasks[222:]:self.assertEqual(t['status'],'partial');self.assertFalse(t['scope']['university_complete'])
 def test_all_historical_json_bytes_reconstruct_from_current_prefixes(self):
  for rel,contract in CONTRACT.items():
   historical=release25_view(read(rel),rel);raw=(json.dumps(historical,ensure_ascii=False,indent=2)+'\n').encode();self.assertEqual(hashlib.sha256(raw).hexdigest(),contract['byte_sha256'],rel)
 def test_projection_rejects_historical_leaf_and_unchanged_metadata_tampering(self):
  for rel in CONTRACT:
   raw=read(rel);key='people'if 'people'in raw else 'entries'if 'entries'in raw else 'tasks';raw[key][0]['name']='unexpected alteration'
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
