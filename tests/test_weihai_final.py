from school_scope import hit_atlas, hit_rosters
"""Whole visible Weihai roster boundary, exact evidence, and defensive match tests."""
import copy,hashlib,json,pathlib,sys,unittest
from collections import Counter
ROOT=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from build import validate,department_tables
from build_rosters import validate_rosters,_verified_profile_match
from validate_queue import validate_queue
class WeihaiFinalTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.d=hit_atlas(json.loads((ROOT/'data/atlas.json').read_text()));cls.r=hit_rosters(json.loads((ROOT/'data/rosters.json').read_text()));cls.pg=json.loads((ROOT/'progress/weihai-information-progress.json').read_text());cls.people={p['name']:p for p in cls.d['people']if p['department_id']=='hit-weihai-information'};cls.pending={p['name']:p for p in cls.d['pending_people']if p.get('department_id')=='hit-weihai-information'}
 def entry(self,n):return next(e for e in self.r['entries']if e['name']==n and e['organization_id']=='hit-weihai-information')
 def test_exact_hit_counts_and_schema(self):
  self.assertTrue(validate(self.d));self.assertTrue(validate_rosters(self.r,self.d));self.assertEqual([len(self.d['people']),len(self.d['pending_people'])],[257,42]);self.assertEqual([sum(len(p.get(k,[]))for p in self.d['people'])for k in ['education','appointments','mentors','committee_members','publications','sources']],[789,953,109,9,545,951]);self.assertEqual(sum(e['profile_identity_verified']for e in self.r['entries']),252)
  import jsonschema
  jsonschema.Draft202012Validator(json.loads((ROOT/'schema/atlas.schema.json').read_text()),format_checker=jsonschema.FormatChecker()).validate(self.d)
 def test_exact_whole_roster_partition_is_not94_complete_profiles(self):
  self.assertEqual([len(self.people),len(self.pending)],[61,33]);self.assertEqual([self.pg[k]for k in ['current_round_reviewed_entry_count','individual_profile_bodies_read','header_only_empty_body','no_verified_individual_body','remaining_visible_entries']],[94,60,2,32,0]);self.assertTrue(self.pg['first_pass_complete']);self.assertFalse(self.pg['coverage_complete']);self.assertFalse(self.pg['all_fields_complete']);self.assertEqual(sum(p.get('own_profile_academic_body_read')is True for p in self.people.values()),60);self.assertFalse(self.people['于长军']['own_profile_academic_body_read']);self.assertTrue(self.people['于长军']['professional_evidence_body_read'])
 def test_source_counts_are_not_confirmed_counts(self):
  self.assertEqual(self.pg['integration_counts'],dict(education=174,appointments=192,mentors=18,committee_members=0,publications=158,sources=188));self.assertEqual(self.pg['source_record_collections']['appointments'],225);self.assertEqual(self.pg['source_record_collections']['publications'],159);self.assertEqual(self.pg['pending_collection_counts']['appointments'],33);self.assertEqual(self.pg['pending_collection_counts']['sources'],49);self.assertEqual(self.pg['pending_bibliography_evidence_count'],1)
 def test_reviewed_coverage_hashes_and_all11_batches(self):
  self.assertEqual(len(self.pg['batches']),11);self.assertEqual(self.pg['college_source_coverage_sha256'],'0cec46ac98fa24627fff0a6a475c651d1ab84575cb83f21e0e889b0030fed4a9');self.assertTrue(all(b['independent_review_status']=='passed_with_documented_limits'for b in self.pg['batches']));b=next(b for b in self.pg['batches']if b['batch_id'].endswith('associate-004'));self.assertEqual(b['source_embedded_review_status'],'self_checked_ready_for_independent_review')
 def test_exact_category_splits(self):
  for n,expected in [('associate',[35,28,7]),('lecturer',[22,9,13]),('college',[94,61,33])]:
   f=ROOT/('progress/weihai-information-'+n+('-coverage.json'if n=='college'else'-progress.json'));c=json.loads(f.read_text());self.assertEqual([c['reviewed_entries'],c['detailed_profiles'],c['pending_profiles']],expected);self.assertTrue(c['category_first_pass_complete']);self.assertFalse(c['fields_complete'])
 def test_pending_bibliography_and_sparse_teaching_preserved_not_promoted(self):
  p=self.pending['胡屏'];self.assertEqual(p['publications'],[]);self.assertEqual(len(p['bibliography_evidence']),1);self.assertEqual(p['bibliography_evidence'][0]['link_status'],'publisher_article_page_verified');self.assertFalse(p['bibliography_evidence_count_eligible']);self.assertFalse(p['detail_count_eligible']);self.assertEqual(self.pending['菅维乐']['teaching'][0]['courses'],['电路','模拟电子技术基础'])
  for p in self.pending.values():self.assertFalse(p['detail_count_eligible']);self.assertEqual(p['education'],[]);self.assertEqual(p['mentors'],[]);self.assertEqual(p['publications'],[])
 def test_empty_headers_stay_pending_and_original_missing_links_stay_null(self):
  for n in ['方琴','罗敏']:
   p=self.pending[n];self.assertEqual(p['profile_status'],'profile_details_pending');self.assertTrue(p['official_url']);self.assertFalse(p['own_profile_academic_body_read']);self.assertIsNone(self.entry(n)['official_profile_url']);self.assertFalse(self.entry(n)['profile_identity_verified'])
 def test_all13_engineers_pending_and_historical_roles_remain_evidence(self):
  ps=[p for p in self.pending.values()if p.get('role_group')=='engineering_technical_staff'];self.assertEqual(len(ps),13);self.assertEqual(Counter(p['appointments'][0]['title']for p in ps),{'高级工程师':7,'工程师':4,'助理工程师':2});self.assertEqual(sum(len(p['sources'])==2 for p in ps),4)
  for p in ps:self.assertIsNone(p['official_url']);self.assertEqual(p['appointments'][0]['status'],'official_roster_currently_listed');self.assertIsNone(p['appointments'][0]['start']);self.assertIsNone(p['appointments'][0]['end']);self.assertFalse(self.entry(p['name'])['profile_identity_verified'])
  x=self.pending['赖春露'];self.assertEqual(x['appointments'][0]['title'],'高级工程师');self.assertIn('2021',json.dumps(x,ensure_ascii=False));self.assertIn('工程师',json.dumps(x['identity_evidence'],ensure_ascii=False))
 def test_wang_ruisong_proposed_supervisor_not_approved(self):
  p=self.pending['王瑞松'];self.assertIn('讲师',p['appointments'][0]['title']);self.assertEqual(p['mentors'],[]);self.assertIn('拟',json.dumps(p,ensure_ascii=False));self.assertFalse(p['detail_count_eligible'])
 def test_two_verified_doctorates_keep_unknown_institution_and_geography(self):
  for n in ['焉晓贞','邵帅']:
   e=self.people[n]['education'][0];self.assertTrue(e['degree_awarded']);self.assertEqual(e['event_kind'],'degree');self.assertIsNone(e['institution']);self.assertIsNone(e['country']);self.assertIsNone(e['continent']);self.assertEqual(e['region'],'unknown');self.assertEqual(e['continent_code'],'unknown');self.assertEqual(e['institution_985'],'unknown');self.assertIsNone(e['start']);self.assertIsNone(e['end'])
 def test_placeholder_state_university_not_guessed_as_usa(self):
  e=self.people['赵万龙']['education'][-1];self.assertFalse(e['degree_awarded']);self.assertEqual(e['event_kind'],'visiting_scholar');self.assertIsNone(e['institution']);self.assertIsNone(e['country']);self.assertEqual(e['region'],'unknown');self.assertEqual(e['continent_code'],'unknown');self.assertIn('XXX',json.dumps(e,ensure_ascii=False))
 def test_source_true_awards_normalize_degree_kind_without_date_invention(self):
  for n in ['匡冀源','孙永进']:
   es=[e for e in self.people[n]['education']if e['degree_awarded']is True];self.assertEqual(len(es),1);e=es[0];self.assertEqual(e['source_event_kind'],'degree_study');self.assertEqual(e['event_kind'],'degree');self.assertNotIn('degree_awarded_date',e)
 def test_sun_joint_training_does_not_multiply_doctorates(self):
  p=self.people['孙永进'];self.assertEqual(len(p['education']),5);js=[e for e in p['education']if e['event_kind']=='joint_training'];self.assertEqual(len(js),2);self.assertTrue(all(e['degree_awarded']is False for e in js));self.assertEqual(p['mentors'],[])
 def test_tang_confirmed_advisor_does_not_confirm_award(self):
  p=self.people['唐帅'];self.assertIsNone(p['education'][0]['degree_awarded']);m=p['mentors'][0];self.assertEqual(m['name'],'姜永远');self.assertEqual(m['education_event_id'],p['education'][0]['event_id']);self.assertIsNone(m['start']);self.assertIsNone(m['end']);self.assertIsNone(m['person_id']);self.assertFalse(m['quick_link_eligible']);self.assertIsNone(m['official_url']);self.assertEqual(m['source_official_url'],'https://homepage.hit.edu.cn/yongyuan')
 def test_li_study_end_and_award_date_separate(self):
  e=self.people['李迎春']['education'][-1];self.assertEqual(e['end'],'2019-02');self.assertEqual(e['degree_awarded_date'],'2019-03');self.assertTrue(e['degree_awarded']);self.assertIsNone(e['start']);self.assertEqual(e['region'],'overseas')
 def test_combined_intervals_not_split_and_all_labels_unknown(self):
  for e in self.people['李洋']['education']:self.assertIsNone(e['start']);self.assertIsNone(e['end']);self.assertIsNone(e['degree_awarded']);self.assertEqual(e['shared_study_period'],{'start':'2007-09','end':'2019-04','degrees':['学士','硕士','博士']})
  p=self.people['刘志勇'];self.assertEqual(len(p['education']),2);self.assertEqual(p['education'][1]['degree'],'硕士/博士');self.assertIsNone(p['education'][1]['degree_awarded'])
 def test_publication_index_does_not_become_article_page(self):
  q=self.people['王好贤']['publications'][0];self.assertEqual(q['link_status'],'publisher_metadata_indexed_page_not_verified');self.assertFalse(q['individual_article_link_verified']);self.assertIn('原页未直接核实',q['link_status_label'])
 def test_ma_existing_advisors_exact_entity_identity(self):
  p=self.people['马一鸣'];self.assertEqual([m['person_id']for m in p['mentors']],[None,'hit-sunmingjian','hit-maly']);self.assertEqual([m['education_event_id']for m in p['mentors']],['hit-mayiming-education-2','hit-mayiming-education-3','hit-mayiming-education-3']);self.assertTrue(all(e['degree_awarded']is None for e in p['education']))
 def test_active_wu_keeps_employment_fact_but_no_navigation(self):
  m=self.people['林欣魄']['mentors'][0];self.assertEqual(m['employment_status'],'active_officially_listed');self.assertFalse(m['quick_link_eligible']);self.assertFalse(m['navigation_verified']);self.assertIsNone(m['official_url']);self.assertIn('认证',m['profile_navigation_unavailable_reason']);self.assertEqual(m['profile_source_url'],'https://www.hit.edu.cn/jbdh/list.htm');self.assertTrue(validate(self.d))
 def test_active_null_homepage_exception_fails_without_every_explicit_guard(self):
  for mutation in [lambda m:m.pop('profile_navigation_unavailable_reason'),lambda m:m.update(profile_navigation_unavailable_reason=' '),lambda m:m.update(quick_link_eligible=True),lambda m:m.pop('quick_link_eligible'),lambda m:m.update(navigation_verified=True),lambda m:m.pop('navigation_verified'),lambda m:m.update(profile_source_url=None),lambda m:m.update(official_url='javascript:alert(1)')]:
   d=copy.deepcopy(self.d);p=next(p for p in d['people']if p['name']=='林欣魄');mutation(p['mentors'][0])
   with self.assertRaises(AssertionError):validate(d)
 def test_independent_profile_exact_identity_without_fabricated_roster_link(self):
  for n in ['贾广乐','邵帅']:
   p=self.people[n];e=self.entry(n);self.assertIsNone(e['official_profile_url']);self.assertTrue(_verified_profile_match(e,p));self.assertEqual(e['verified_person_id'],p['person_id']);v=e['profile_identity_evidence']['independent_profile_verification'];self.assertTrue(v['identity_verified']);self.assertIsNone(v['roster_url']);self.assertEqual(v['name'],n);self.assertEqual(v['organization_id'],p['department_id'])
 def test_independent_profile_missing_link_fails_every_identity_or_source_gap(self):
  base=self.entry('贾广乐');p=self.people['贾广乐']
  mutations=[lambda e:e.update(profile_identity_verified=False),lambda e:e.update(verified_person_id='another-person'),lambda e:e.update(name='另一个人'),lambda e:e.update(organization_id='hit-seie'),lambda e:e['profile_identity_evidence'].update(source_ids=[]),lambda e:e['profile_identity_evidence'].pop('roster_link_url'),lambda e:e['profile_identity_evidence'].update(roster_source_url='https://example.com'),lambda e:e['profile_identity_evidence']['independent_profile_verification'].update(identity_verified=False),lambda e:e['profile_identity_evidence']['independent_profile_verification'].update(name='另一个人'),lambda e:e['profile_identity_evidence']['independent_profile_verification'].update(person_id='another-person'),lambda e:e['profile_identity_evidence']['independent_profile_verification'].update(organization_id='hit-seie'),lambda e:e['profile_identity_evidence']['independent_profile_verification'].update(source_ids=['missing']),lambda e:e['profile_identity_evidence']['independent_profile_verification'].update(source_ids=[]),lambda e:e['profile_identity_evidence']['independent_profile_verification'].pop('roster_url')]
  for f in mutations:
   e=copy.deepcopy(base);f(e);self.assertFalse(_verified_profile_match(e,p))
  for f in [lambda p:p.update(detail_count_eligible=False),lambda p:p.update(sources=[]),lambda p:p.update(official_url=None)]:
   q=copy.deepcopy(p);f(q);self.assertFalse(_verified_profile_match(base,q))
 def test_source_event_and_provenance_closure_and_public_privacy(self):
  ids=set();forbidden={'body_cache','text_cache','retrieval_note','existing_person_id_scan','birth_date','email','phone','students','student_list'}
  for p in list(self.people.values())+list(self.pending.values()):
   ss={s['id']for s in p['sources']};es={e['event_id']for e in p['education']}
   for e in p['education']:self.assertNotIn(e['event_id'],ids);ids.add(e['event_id'])
   def walk(v):
    if isinstance(v,dict):
     for k,x in v.items():
      self.assertNotIn(k,forbidden);self.assertFalse(k.endswith('_cache'))
      if k=='field_status':continue
      if k=='field_provenance':self.assertTrue(all(y is None or (set(y)<=ss if isinstance(y,list)else y in ss)for y in x.values()));continue
      if (k=='source_id'or k.endswith('_source_id'))and x is not None:self.assertIn(x,ss)
      if k=='source_ids'or k.endswith('_source_ids'):self.assertLessEqual(set(x),ss)
      if k=='education_event_id'and x:self.assertIn(x,es)
      walk(x)
    elif isinstance(v,list):
     for x in v:walk(x)
   walk(p);self.assertNotIn('/workspace/',json.dumps(p));self.assertNotIn('/tmp/',json.dumps(p))
 def test_queue_honest_completion_boundary_and_verified_release_baseline(self):
  q=json.loads((ROOT/'progress/work-queue.json').read_text());self.assertEqual(next(t for t in q['tasks'] if t['task_id']=='hit-weihai-information:profiles')['last_verified_commit'],'d7719f6916c2e3ac06906dcc403181f3bdc374a8');self.assertEqual(validate_queue(q,ROOT,True),[]);t=next(t for t in q['tasks']if t['task_id']=='hit-weihai-information:profiles');self.assertEqual(t['status'],'partial');self.assertEqual(t['next_cursor'],'weihai-information:first-pass-complete:uncertainty-review');self.assertIsNone(self.pg['next_roster_name']);self.assertFalse(t['scope']['university_complete']);self.assertEqual(self.pg['integration_baseline_commit'],t['last_verified_commit'])
if __name__=='__main__':unittest.main()
