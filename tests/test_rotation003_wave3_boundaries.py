"""Generic source-preserving event, mentor, and candidate isolation boundaries."""
import copy,hashlib,json,pathlib,unittest
from release26_history import CONTRACT,release26_view
ROOT=pathlib.Path(__file__).resolve().parents[1]
read=lambda rel:json.loads((ROOT/rel).read_text())
class Rotation003Wave3Boundaries(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.a=read('data/atlas.json');cls.r=read('data/rosters.json');cls.new=cls.a['people'][CONTRACT['data/atlas.json']['lists']['people']['length']:]
 def test_current_append_and_generated_view(self):
  self.assertEqual((len(self.a['people']),len(self.a['pending_people']),len(self.a['org_units']),len(self.r['entries']),len(self.r['source_observations'])),(573,84,237,1739,1777))
  site=read('site/atlas.json');self.assertEqual(site['people'],self.a['people']);self.assertEqual(site['pending_people'],self.a['pending_people']);self.assertEqual(site['build_id'],read('site/rosters.json')['build_id']);self.assertEqual(len(site['exports']),117)
  for p in self.new:self.assertFalse(p['fields_complete']);self.assertFalse(p['include_in_current_faculty_count']);self.assertFalse(p['complete_profile_count_eligible'])
 def test_exact_previous_history_and_tamper_detection(self):
  for rel,c in CONTRACT.items():
   raw=read(rel);hist=release26_view(raw,rel);self.assertEqual(hashlib.sha256((json.dumps(hist,ensure_ascii=False,indent=2)+'\n').encode()).hexdigest(),c['byte_sha256'])
   key=next(k for k in ['people','entries','tasks']if k in raw);raw[key][0]['name']='tamper'
   with self.assertRaises(AssertionError):release26_view(raw,rel)
 def test_display_aliases_do_not_invent_degree_or_time(self):
  mappings={'postdoc':'postdoctoral_research','graduation_degree_unspecified':'education_level_unknown'};found=[]
  for p in self.new:
   for e in p['education']:
    if e.get('source_event_kind')in mappings:
     found.append(e);self.assertEqual(e['event_kind'],mappings[e['source_event_kind']]);self.assertIsNone(e['degree']);self.assertIsNot(e['degree_awarded'],True);self.assertFalse(e['include_in_degree_filters']);self.assertTrue(e['event_kind_normalization_note'])
  self.assertEqual(len(found),5)
 def test_source_degree_labels_remain_visible_without_degree_inference(self):
  found=[]
  for p in self.new:
   for e in p['education']:
    label=e.get('source_reported_degree_label')
    if label and label!=e.get('degree'):
     found.append(e);self.assertIn('来源标注：'+label,e['note']);self.assertIn(e['field_provenance']['source_reported_degree_label'],e['note_derivation_source_ids']);self.assertIn('source_note',e);self.assertEqual(e['note_derivation'],'original_note_plus_verbatim_source_reported_degree_label')
  self.assertTrue(found)
 def test_stage_specific_mentors_keep_event_identity_and_navigation_off(self):
  kinds={'doctoral_supervisor':('doctoral_advisor',True),'masters_supervisor':('masters_advisor',True),'joint_training_supervisor':('joint_training_advisor',False),'postdoctoral_supervisor':('postdoctoral_advisor',False)};seen=set()
  for p in self.new:
   events={e['event_id']:e for e in p['education']}
   for m in p['mentors']:
    seen.add(m['type']);self.assertIn(m['education_event_id'],events);self.assertEqual((m['relationship_kind'],m['include_in_degree_mentorship_graph']),kinds[m['type']]);self.assertFalse(m['navigation_verified']);self.assertFalse(m['quick_link_eligible']);self.assertIsNone(m['official_url']);self.assertIsNone(m['start']);self.assertIsNone(m['end'])
  self.assertEqual(seen,set(kinds))
 def test_unknown_and_nondegree_events_are_not_confirmed(self):
  events=[e for p in self.new for e in p['education']];self.assertEqual(len(events),26);self.assertEqual([sum(e['degree_awarded']is v for e in events)for v in [True,None,False]],[6,13,7])
  for e in events:
   if e['degree_awarded']is not True:self.assertFalse(e['include_in_degree_filters'])
   else:self.assertEqual(e['event_kind'],'degree')
 def test_candidate_publication_is_not_verified_bibliography(self):
  total=0
  for p in self.new:
   for c in p.get('pending_professional_fact_candidates',[]):
    total+=1;self.assertNotIn(c,p['publications']);self.assertIs(c['include_in_verified_publications'],False);self.assertEqual(c['verification_status'],'held_pending_independent_source_access');self.assertNotIn(c['title'],[q['title']for q in p['publications']]);source=next(s for s in p['sources']if s['id']==c['source_id']);self.assertIs(source['navigation_available'],False);self.assertIs(source['navigation_enabled'],False);self.assertEqual(source['independent_review_status'],'not_passed_source_unavailable')
  self.assertEqual(total,1);self.assertEqual(sum(len(p['publications'])for p in self.new),8)
 def test_roster_identity_notes_and_payload_are_source_bound(self):
  entries={e['id']:e for e in self.r['entries']};obs={e['record_id']:e for e in self.r['source_observations']}
  for p in self.new:
   e=entries[p['roster_entry_id']];self.assertIn(p['identity_evidence']['note'],e['notes']);self.assertTrue(e['profile_identity_verified']);self.assertEqual(e['official_profile_url'],p['official_url']);self.assertEqual(obs[e['id']]['source_payload'],{k:v for k,v in e.items()if k!='source_observation_ids'})
if __name__=='__main__':unittest.main()
