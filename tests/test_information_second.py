from school_scope import hit_atlas, hit_rosters
import copy,json,pathlib,sys,unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from build import department_tables,validate
from build_rosters import validate_rosters
class InformationSecondTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.data=hit_atlas(json.loads((ROOT/'data/atlas.json').read_text()));cls.rosters=hit_rosters(json.loads((ROOT/'data/rosters.json').read_text()));cls.batch=[p for p in cls.data['people'] if p.get('data_batch_id')=='faculty-batch-harbin-eie-fourth-002']
 def test_combined_counts_and_static_snapshot(self):
  self.assertEqual([len(self.data['people']),len(self.data['pending_people']),sum('harbin' in p['campus_ids'] for p in self.data['people'])],[257,42,159]);self.assertEqual([sum(len(p.get(k,[])) for p in self.data['people']) for k in ['education','mentors','committee_members','publications']],[789,109,9,545]);self.assertEqual(self.data['people'],hit_atlas(json.loads((ROOT/'site/atlas.json').read_text()))['people'])
 def test_batch_counts_and_in_memory_tables_without_xlsx_writes(self):
  self.assertEqual([sum(len(p[k]) for p in self.batch) for k in ['education','appointments','mentors','committee_members','publications','sources']],[33,39,4,4,22,52]);t=dict(department_tables(self.batch,self.data['updated_at']));self.assertEqual([len(t[k]) for k in ['总览','经历','导师','论文']],[11,73,9,23]);self.assertEqual(sum('委员会' in (r[2] or '') for r in t['导师'][1:]),4);self.assertTrue(all(not r[7] for r in t['导师'][1:]));m=next(r for r in t['导师'][1:] if r[1]=='Mathews Jacob');self.assertIn('University of Iowa',m[6]);self.assertIn('University of Rochester',m[6]);self.assertIn('University of Virginia',m[6])
 def test_precise_mentor_event_ids_reject_missing_reference(self):
  self.assertTrue(validate(self.data))
  for p in self.batch:
   events={e['event_id']:e for e in p['education']}
   for m in p['mentors']:
    self.assertEqual(events[m['education_event_id']],p['education'][m['education_event_index']]);self.assertIsNone(m['person_id']);self.assertIsNone(m['start']);self.assertIsNone(m['end'])
  d=copy.deepcopy(self.data);p=next(p for p in d['people'] if p['name']=='胡悦');p['mentors'][0]['education_event_id']='missing'
  with self.assertRaises(AssertionError):validate(d)
 def test_source_and_event_closure(self):
  for p in self.batch:
   ids={s['id'] for s in p['sources']};events={e['event_id'] for e in p['education']}
   def walk(v):
    if isinstance(v,dict):
     for k,x in v.items():
      if (k=='source_id' or k.endswith('_source_id')) and x is not None:self.assertIn(x,ids)
      if k=='source_ids' or k.endswith('_source_ids'):self.assertTrue(set(x)<=ids)
      if k=='field_provenance':self.assertTrue(all(y is None or y in ids for y in x.values()))
      if k=='education_event_id' and x:self.assertIn(x,events)
      walk(x)
    elif isinstance(v,list):
     for x in v:walk(x)
   walk(p)
 def test_roster_links_preserve_verified_person_and_http_observation(self):
  self.assertTrue(validate_rosters(self.rosters,self.data));self.assertEqual(sum(e['profile_identity_verified'] for e in self.rosters['entries']),252)
  for p in self.batch:
   e=next(e for e in self.rosters['entries'] if e['id']==p['roster_entry_id']);self.assertEqual(e['verified_person_id'],p['person_id']);ev=e['profile_identity_evidence'];self.assertEqual(ev['official_url'],p['official_url']);self.assertEqual(ev['roster_link_url'],e['official_profile_url']);self.assertEqual(ev['redirect_observation']['requested_url'],ev['redirect_observation']['final_url']);self.assertEqual(ev['redirect_observation']['name'],p['name'])
 def test_two_frozen_batches_partial_progress_and_queue_baseline(self):
  progress=json.loads((ROOT/'progress/harbin-information-progress.json').read_text());self.assertEqual(progress['first_pass_attempted'],33);self.assertEqual(progress['official_roster_count'],33);self.assertFalse(progress['coverage_complete']);self.assertEqual(len(progress['entries']),33);self.assertTrue(all(not e['fields_complete'] for e in progress['entries']));self.assertEqual([b['normalized_package_sha256'] for b in progress['batches'][:2]],['689dc6b4389d80a1ef72cd0f86a5880a8d9b0b66d045de946e3907b777d297a8','360dcf047339fc34f309959a492a558100061e11a1e7b6fe26339cde97e24569']);self.assertIsNone(progress['next_roster_name']);self.assertEqual(progress['degree_awarded_counts'],{'true':52,'false':25,'null':25});q=json.loads((ROOT/'progress/work-queue.json').read_text());self.assertEqual(next(t for t in q['tasks'] if t['task_id']=='hit-weihai-information:profiles')['last_verified_commit'],'d7719f6916c2e3ac06906dcc403181f3bdc374a8');t=next(t for t in q['tasks'] if t['task_id']=='hit-seie:profiles');self.assertEqual(t['next_cursor'],'seie:first-pass-complete:uncertainty-review');self.assertEqual(t['status'],'partial')
