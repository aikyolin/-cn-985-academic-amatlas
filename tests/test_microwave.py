"""Regression boundaries for the reviewed microwave checkpoint; never writes exports."""
import copy,hashlib,json,pathlib,sys,unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from build import validate,department_tables
from build_rosters import validate_rosters
from validate_queue import validate_queue
class MicrowaveTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.data=json.loads((ROOT/'data/atlas.json').read_text());cls.rosters=json.loads((ROOT/'data/rosters.json').read_text());cls.people={p['name']:p for p in cls.data['people']};cls.batch=[p for p in cls.data['people']if p.get('data_batch_id','').startswith('faculty-batch-harbin-eie-fifth-')]
 def test_global_counts_and_unchanged_pending_layer(self):
  d=self.data;self.assertTrue(validate(d));self.assertEqual([len(d['people']),len(d['pending_people']),sum('harbin'in p['campus_ids']for p in d['people'])],[228,11,159]);self.assertEqual([sum(len(p.get(k,[]))for p in d['people'])for k in ['education','appointments','mentors','committee_members','research_collaborators','publications']],[711,882,104,9,4,472]);self.assertEqual(self.data['people'],json.loads((ROOT/'site/atlas.json').read_text())['people'])
 def test_exact_reviewed_microwave_coverage_hash_and_strata(self):
  f=ROOT/'progress/harbin-microwave-coverage.json';self.assertEqual(hashlib.sha256(f.read_bytes()).hexdigest(),'670bfed6ebbd0a86a57b18726e10e1a6688c1f03b355d3af1f7017ef66161821');c=json.loads(f.read_text());self.assertEqual([c[k]for k in ['official_roster_count','first_pass_attempted','substantive_professional_body','sparse_academic_history','name_only_no_academic_body','own_profile_academic_body_read']],[22,22,17,5,0,21]);self.assertTrue(all(not e['fields_complete']for e in c['entries']));self.assertEqual(c['review_status'],'all_two_batches_passed')
 def test_exact_college_coverage_does_not_claim_unique_verified_identities_or_complete_fields(self):
  f=ROOT/'progress/harbin-seie-coverage.json';self.assertEqual(hashlib.sha256(f.read_bytes()).hexdigest(),'13f65496a340f7ee61044f9ac1a4f98eda3afedb9cb2e1e8d71621e47765c23d');c=json.loads(f.read_text());self.assertEqual(c['official_roster_entry_count'],165);self.assertEqual(c['first_pass_attempted_entry_count'],165);self.assertIsNone(c['verified_unique_individual_count']);self.assertEqual(c['coverage_totals'],{'substantive_professional_history':143,'sparse_professional_history':17,'name_only_or_extended_identity_unresolved':5});self.assertTrue(all(not e['fields_complete']for e in c['entries']));self.assertEqual(c['review_status'],'all_16_batches_passed')
 def test_both_pending_mentor_keys_count_without_confirmed_edges(self):
  ps=[p for p in self.data['people']+self.data['pending_people']if p['department_id']=='hit-seie'];old=sum(len(p.get('pending_mentors',[]))for p in ps);new=sum(len(p.get('pending_mentor_candidates',[]))for p in ps);self.assertEqual([old,new,old+new],[5,3,8]);self.assertEqual(sum(len(p['mentors'])for p in ps),55)
  for p in ps:
   for key in ['pending_mentors','pending_mentor_candidates']:
    for m in p.get(key,[]):self.assertNotIn(m,p['mentors'])
  self.assertEqual(len([p for p in self.data['people']if p['department_id']=='hit-seie']),157);self.assertEqual(len([p for p in self.data['pending_people']if p['department_id']=='hit-seie']),8)
 def test_all_twenty_two_roster_links_resolve_and_lijinxing_keeps_independent_link_bridge(self):
  self.assertTrue(validate_rosters(self.rosters,self.data));self.assertEqual(sum(e['profile_identity_verified']for e in self.rosters['entries']),223)
  for p in self.batch:
   entry=next(e for e in self.rosters['entries']if e['id']==p['roster_entry_id']);self.assertTrue(entry['profile_identity_verified']);self.assertEqual(entry['verified_person_id'],p['person_id'])
  p=self.people['李金星'];entry=next(e for e in self.rosters['entries']if e['id']==p['roster_entry_id']);ev=entry['profile_identity_evidence'];self.assertEqual(ev['source_status'],'official_roster_and_supervisor_faculty_link_and_same_department_profile_cross_checked');self.assertEqual(ev['status'],'independent_current_official_profile_name_department_match');self.assertEqual(ev['independent_profile_verification']['official_url'],p['official_url']);self.assertEqual(ev['independent_profile_verification']['roster_url'],entry['official_profile_url']);self.assertIn('张狂',ev['independent_profile_verification']['note']);self.assertNotIn('verified_alias_urls',ev);self.assertNotIn('redirect_chain',ev)
 def test_original_event_ids_and_cross_batch_internal_entities(self):
  ids={p['person_id']:p for p in self.data['people']};events=[];internal=[]
  for p in self.batch:
   for e in p['education']:self.assertEqual(e['event_id'],e['education_event_id']);events.append(e['event_id'])
   for m in p['mentors']:
    self.assertEqual(p['education'][m['education_event_index']]['event_id'],m['education_event_id']);self.assertFalse(m['quick_link_eligible'])
    if m['person_id']:self.assertEqual(ids[m['person_id']]['name'],m['name']);internal.append(m)
  self.assertEqual(len(events),65);self.assertEqual(len(set(events)),65);self.assertEqual(len(internal),7)
 def test_collaborator_export_row_is_non_mentor_and_binds_only_postdoc_event(self):
  p=self.people['杨海棠'];before=copy.deepcopy(p);tables=dict(department_tables([p],self.data['updated_at']));mentor_rows=tables['导师'];self.assertEqual(len(mentor_rows),3);self.assertFalse(any('Lihong Wang'in str(row)for row in mentor_rows));rows=[row for row in tables['经历']if 'Lihong Wang'in str(row)];self.assertEqual(len(rows),1);self.assertEqual(rows[0][1],'postdoctoral_research_collaborator');self.assertEqual(rows[0][3],'California Institute of Technology');self.assertEqual(rows[0][4:6],['2024-05','2025-05']);self.assertIn('非导师认定',str(rows[0]));self.assertEqual(p,before)
 def test_source_references_closed_and_private_cache_fields_removed(self):
  forbidden={'body_cache','text_cache','retrieval_note','birthday','birth_date','phone','email','contact','student_list','students'}
  for p in self.batch:
   ids={s['id']for s in p['sources']}
   def walk(v):
    if isinstance(v,dict):
     for k,x in v.items():
      self.assertNotIn(k.lower(),forbidden);self.assertFalse(k.endswith('_cache'))
      if(k=='source_id'or k.endswith('_source_id'))and x is not None:self.assertIn(x,ids)
      if k=='source_ids'or k.endswith('_source_ids'):self.assertTrue(set(x)<=ids)
      if k=='field_provenance':self.assertTrue(all(z is None or z in ids for z in x.values()))
      walk(x)
    elif isinstance(v,list):
     for x in v:walk(x)
   walk(p);self.assertNotIn('/workspace/',json.dumps(p))
 def test_first_pass_complete_stays_distinct_from_partial_profile_research(self):
  pg=json.loads((ROOT/'progress/harbin-microwave-progress.json').read_text());self.assertTrue(pg['first_pass_complete']);self.assertFalse(pg['coverage_complete']);self.assertFalse(pg['all_fields_complete']);self.assertEqual([pg['detailed_profiles'],pg['pending_profiles']],[22,0]);self.assertEqual(pg['college_transport_counts'],{'detailed_profiles':157,'pending_profiles':8});self.assertEqual([b['normalized_package_sha256']for b in pg['normalized_batches']],['00429ad3226e2ea3eabebba05d2e94efbd55d1dc5c9c54215586bf1bf4ee08da','ab3c0aaabb207e919a060cd93d04bc7739a35765d3e0a096609286123d8aa48d']);q=json.loads((ROOT/'progress/work-queue.json').read_text());self.assertEqual(q['base_commit'],'69469d6d80e5f686dbc9867c67d176ce8f1efce6');self.assertEqual(validate_queue(q,check_artifacts=True),[]);t=next(t for t in q['tasks']if t['task_id']=='hit-seie:profiles');self.assertEqual(t['status'],'partial');self.assertEqual(t['next_cursor'],'seie:first-pass-complete:uncertainty-review');self.assertFalse(t['scope']['university_complete'])
 def test_unknown_awards_and_missing_institutions_never_become_historical_985_yes(self):
  for name in ['李红梅','陈立甲']:
   e=self.people[name]['education'][0];self.assertTrue(e['degree_awarded']);self.assertIsNone(e['institution']);self.assertEqual(e['institution_985'],'unknown');self.assertEqual(e['region'],'unknown')
  e=self.people['张狂']['education'][0];self.assertIsNone(e['degree_awarded']);self.assertEqual(e['event_kind'],'doctoral_study');self.assertIsNone(e['end'])
if __name__=='__main__':unittest.main()
