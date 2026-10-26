from atlas_test_io import load_atlas
from school_scope import hit_atlas, hit_rosters
"""Associate first10: conservative fields, pending-layer boundaries and exact identity mapping."""
import json,pathlib,sys,unittest
ROOT=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from build import validate,department_tables
from build_rosters import validate_rosters
from validate_queue import validate_queue
class WeihaiAssociateTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.d=hit_atlas(load_atlas(ROOT/'data/atlas.json'));cls.r=hit_rosters(json.loads((ROOT/'data/rosters.json').read_text()));cls.pg=json.loads((ROOT/'progress/weihai-information-progress.json').read_text());cls.people={p['name']:p for p in cls.d['people']};cls.ps=[p for p in cls.d['people']if p.get('data_batch_id')=='faculty-batch-weihai-info-associate-001'];cls.pending=[p for p in cls.d['pending_people']if p.get('data_batch_id')=='faculty-batch-weihai-info-associate-001']
 def test_checkpoint_exact_counts_exclude_pending_career_facts(self):
  self.assertTrue(validate(self.d));self.assertEqual([len(self.d['people']),len(self.d['pending_people'])],[257,42]);self.assertEqual([sum(len(p.get(k,[]))for p in self.d['people'])for k in ['education','appointments','mentors','committee_members','publications','sources']],[789,953,109,9,545,951]);self.assertEqual(sum(e['profile_identity_verified']for e in self.r['entries']),252);self.assertEqual([len(self.ps),len(self.pending)],[8,2]);self.assertEqual(sum(len(p['appointments'])for p in self.pending),2)
 def test_exact_reviewed_source_and_normalized_hash(self):
  b=next(b for b in self.pg['batches']if b['batch_id']=='faculty-batch-weihai-info-associate-001');self.assertEqual(b['source_sha256'],'e72b3883ba7f3b5a97994472294891edf6ed0a896067c5414f0569d3c984c1ec');self.assertEqual(b['normalized_package_sha256'],'c076d2115e9b62d1b08e692969f7bea757361275192e109456247e50931dcc4e');self.assertEqual(b['independent_review_status'],'passed_with_documented_limits');self.assertEqual(b['source_embedded_review_status'],'pending_independent_review')
 def test_pending_identity_not_folded_into_near_homonym(self):
  w=next(p for p in self.pending if p['name']=='王新生');self.assertEqual(w['person_id'],'hit-weihai-wangxinsheng');self.assertEqual(self.people['王新胜']['person_id'],'hit-wangxinsheng')
  for p in self.pending:
   self.assertIsNone(p['official_url']);self.assertFalse(p['detail_count_eligible']);self.assertEqual(p['education'],[]);e=next(e for e in self.r['entries']if e['id']==p['roster_entry_id']);self.assertFalse(e['profile_identity_verified']);self.assertFalse(e.get('verified_person_id'))
 def test_eight_exact_name_and_official_profile_links_with_three_local_corrections(self):
  self.assertTrue(validate_rosters(self.r,self.d))
  for p in self.ps:
   e=next(e for e in self.r['entries']if e['id']==p['roster_entry_id']);self.assertEqual(e['verified_person_id'],p['person_id']);self.assertTrue(e['profile_identity_verified']);self.assertEqual(e['name'],p['name']);self.assertTrue(e['profile_identity_evidence']['redirect_observation']['name_matches_title'])
  for name in ['李剑锋','康文静','梅英杰']:
   p=self.people[name];e=next(e for e in self.r['entries']if e['id']==p['roster_entry_id']);self.assertEqual(e['official_profile_url'],p['identity_evidence']['corrected_roster_url']);self.assertEqual(e['local_mapping_correction']['previous_local_profile_url'],p['identity_evidence']['original_roster_url']);o=next(o for o in self.r['source_observations']if o['record_id']==e['id']);self.assertEqual(o['source_payload']['official_profile_url'],p['identity_evidence']['original_roster_url'])
 def test_guidance_export_exact_three_doctoral_and_one_postdoc(self):
  rows=dict(department_tables(self.ps,self.d['updated_at']))['导师'];self.assertEqual(len(rows),5);self.assertEqual([r[2]for r in rows[1:]],['博士导师','博士导师','博士导师','博士后合作导师']);self.assertTrue(all(m['education_event_id']=='hit-zhangjingyu-education-3'for m in self.people['张敬禹']['mentors']));self.assertTrue(all(e['degree_awarded']is None for e in self.people['张敬禹']['education'][1:]))
 def test_mentors_active_vs_listed_and_null_internal_entities(self):
  for m in self.people['张敬禹']['mentors']:self.assertEqual(m['employment_status'],'active_officially_listed');self.assertTrue(m['quick_link_eligible']);self.assertIsNone(m['person_id']);self.assertTrue(m['official_url'])
  m=self.people['梅英杰']['mentors'][0];self.assertEqual(m['employment_status'],'official_page_currently_listed');self.assertFalse(m['quick_link_eligible']);self.assertIsNone(m['official_url']);self.assertEqual(m['profile_source_url'],'https://www.ioisas.cn/ryxx/1374.html')
 def test_career_only_people_have_no_inferred_degrees(self):
  for n in ['黄海滨','庄宇飞','梅英杰']:self.assertEqual(len(self.people[n]['education']),1);self.assertFalse(self.people[n]['education'][0]['degree_awarded'])
  self.assertEqual(self.people['李剑锋']['publications'],[]);self.assertEqual(self.people['李剑锋']['education'][1]['institution_985'],'unknown');self.assertEqual(self.people['康文静']['education'][1]['start'],None)
 def test_scope94_first_pass_is_not_complete_profiles_and_associate35_is_split(self):
  p=self.pg;self.assertEqual([p['current_round_reviewed_entry_count'],p['department_detailed_profiles'],p['department_pending_profiles'],p['individual_profile_bodies_read'],p['remaining_visible_entries']],[94,61,33,60,0]);self.assertTrue(p['first_pass_complete']);self.assertFalse(p['all_fields_complete']);self.assertTrue(p['professor_researcher_category_first_pass_complete']);self.assertTrue(p['associate_professor_researcher_category_first_pass_complete']);c=json.loads((ROOT/'progress/weihai-information-associate-progress.json').read_text());self.assertEqual([c['category_roster_entries'],c['reviewed_entries'],c['new_detailed_profiles'],c['pending_profiles']],[35,35,28,7]);self.assertEqual(sum(p['remaining_role_counts'].values()),0)
 def test_queue_exact_next_anchor_and_release_baseline(self):
  q=json.loads((ROOT/'progress/work-queue.json').read_text());self.assertEqual(next(t for t in q['tasks'] if t['task_id']=='hit-weihai-information:profiles')['last_verified_commit'],'d7719f6916c2e3ac06906dcc403181f3bdc374a8');self.assertEqual(validate_queue(q,ROOT,True),[]);t=next(t for t in q['tasks']if t['task_id']=='hit-weihai-information:profiles');self.assertEqual(t['status'],'partial');self.assertEqual(t['next_cursor'],'weihai-information:first-pass-complete:uncertainty-review');self.assertIsNone(self.pg['next_roster_name']);self.assertIsNone(self.pg['next_roster_entry_id'])
 def test_public_progress_has_no_raw_cache_or_private_research_paths(self):
  c=json.loads((ROOT/'progress/weihai-information-associate-progress.json').read_text());s=json.dumps(c);self.assertNotIn('/workspace/',s);self.assertNotIn('body_cache',s);self.assertNotIn('text_cache',s);self.assertNotIn('retrieval_note',s);self.assertNotIn('257',(ROOT/'README.md').read_text());self.assertIn('257 位',(ROOT/'progress/current-coverage.md').read_text());self.assertIn('另 42 份身份或资料待完善记录',(ROOT/'progress/README.md').read_text())
if __name__=='__main__':unittest.main()
