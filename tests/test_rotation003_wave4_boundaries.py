from atlas_test_io import read_live_json
from atlas_test_io import load_atlas
from published_fixture import published_root
"""Live append boundaries: source order, non-native identity, and unknown stages."""
import copy,json,pathlib,unittest
from release28_history import release28_view
from release27_history import CONTRACT,release27_view
ROOT=pathlib.Path(__file__).resolve().parents[1]
read=lambda rel,root=ROOT:release28_view((json.loads((root/rel).read_text()) if root == published_root() else read_live_json(root/rel)),rel) if rel in CONTRACT else (json.loads((root/rel).read_text()) if root == published_root() else read_live_json(root/rel))
class Rotation003Wave4Boundaries(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.a=read('data/atlas.json');cls.r=read('data/rosters.json');cls.new=cls.a['people'][CONTRACT['data/atlas.json']['lists']['people']['length']:]
 def test_live_append_preserves_historical_prefix_and_generated_views(self):
  actual_site=load_atlas(ROOT/'site/atlas.json');actual_data=load_atlas(ROOT/'data/atlas.json')
  self.assertEqual(actual_site['people'],actual_data['people']);self.assertEqual(actual_site['pending_people'],actual_data['pending_people'])
  self.assertEqual(actual_site['build_id'],json.loads((ROOT/'site/rosters.json').read_text())['build_id'])
  for rel in CONTRACT:release27_view(read(rel,published_root() if rel=='site/atlas.json' else ROOT),rel)
  self.assertEqual((len(self.a['people']),len(self.a['pending_people']),len(self.a['org_units']),len(self.r['entries']),len(self.r['source_observations'])),(580,84,240,1746,1784))
  s=read('site/atlas.json',published_root());self.assertEqual(s['people'],self.a['people']);self.assertEqual(s['pending_people'],self.a['pending_people']);self.assertEqual(s['build_id'],read('site/rosters.json')['build_id']);self.assertEqual(len(s['exports']),120)
 def test_held_candidates_keep_original_selection_without_person_promotion(self):
  for sid in ['buaa','muc','nku']:
   c=read(f'progress/{sid}-rotation003-wave4-coverage.json');entries=c['selected_roster_original_order'];held=c['held_candidates']
   positions=[(x['order'],x['name'])for x in entries+held];self.assertEqual([n for _,n in sorted(positions)],c['selected_candidate_names'])
   for h in held:self.assertNotIn(h['name'],{p['name']for p in self.a['people']+self.a['pending_people'] if p['school_id']==sid})
   self.assertFalse(c['coverage_complete']);self.assertEqual(c['status'],'partial')
 def test_independent_identity_never_invents_native_roster_navigation(self):
  es={e['id']:e for e in self.r['entries']};obs={o['record_id']:o for o in self.r['source_observations']}
  for p in self.new:
   e=es[p['roster_entry_id']];native=p['identity_evidence']['native_link_target']
   self.assertEqual(e['profile_identity_verified'],native is not None)
   if native is None:self.assertIsNone(e['verified_person_id']);self.assertIsNone(e['official_profile_url']);self.assertTrue(e['independent_person_identity_reviewed'])
   self.assertEqual(obs[e['id']]['source_payload'],{k:v for k,v in e.items()if k!='source_observation_ids'})
 def test_unknown_stage_alias_is_reversible_and_does_not_award_degree(self):
  aliases=[e for p in self.new for e in p['education']if e.get('source_event_kind')=='study_level_unspecified'];self.assertTrue(aliases)
  for e in aliases:
   self.assertEqual(e['event_kind'],'education_level_unknown');self.assertIsNone(e['degree']);self.assertIsNone(e['degree_awarded']);self.assertFalse(e['include_in_degree_filters']);self.assertIn(e['source_reported_degree_label'],e['note']);self.assertTrue(e['note_derivation_source_ids'])
 def test_three_state_awards_and_stage_edges_are_not_current_navigation(self):
  events=[e for p in self.new for e in p['education']];self.assertEqual([sum(e['degree_awarded']is v for e in events)for v in [True,None,False]],[6,12,8])
  for p in self.new:
   ids={e['event_id']for e in p['education']}
   for m in p['mentors']:
    self.assertIn(m['education_event_id'],ids);self.assertEqual(m['type'],m['source_type']);self.assertFalse(m['navigation_verified']);self.assertFalse(m['quick_link_eligible'])
   for e in p['education']:
    if e['degree_awarded']is False:self.assertFalse(e['include_in_education_filters']);self.assertFalse(e['include_in_degree_filters'])
if __name__=='__main__':unittest.main()
