import copy,json,pathlib,sys,unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from build import department_tables,validate
from build_rosters import validate_rosters
class InformationFirstTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.data=json.loads((ROOT/'data/atlas.json').read_text());cls.rosters=json.loads((ROOT/'data/rosters.json').read_text());cls.batch=[p for p in cls.data['people'] if p.get('data_batch_id')=='faculty-batch-harbin-eie-fourth-001']
 def test_source_and_static_profiles_match(self):
  public=json.loads((ROOT/'site/atlas.json').read_text());self.assertEqual(self.data['people'],public['people']);self.assertEqual(self.data['pending_people'],public['pending_people'])
 def test_exact_collection_counts(self):
  self.assertEqual(len(self.batch),10);self.assertEqual([sum(len(p[k]) for p in self.batch) for k in ['education','appointments','mentors','publications','sources']],[38,43,0,25,51])
 def test_roster_identity_evidence_and_counts(self):
  self.assertTrue(validate_rosters(self.rosters,self.data));self.assertEqual(sum(e['profile_identity_verified'] for e in self.rosters['entries']),223)
  for p in self.batch:
   e=next(e for e in self.rosters['entries'] if e['id']==p['roster_entry_id']);self.assertEqual(e['verified_person_id'],p['person_id']);self.assertEqual(e['profile_identity_evidence']['source_ids'],p['identity_evidence']['source_ids']);self.assertEqual(e['profile_identity_evidence']['roster_source_url'],e['roster_source_url'])
 def test_profile_and_event_source_closure(self):
  for p in self.batch:
   ids={s['id'] for s in p['sources']}
   def walk(v):
    if isinstance(v,dict):
     for k,x in v.items():
      if (k=='source_id' or k.endswith('_source_id')) and x is not None:self.assertIn(x,ids)
      if k=='source_ids' or k.endswith('_source_ids'):self.assertTrue(set(x)<=ids)
      if k=='field_provenance':self.assertTrue(all(y is None or y in ids for y in x.values()))
      walk(x)
    elif isinstance(v,list):
     for x in v:walk(x)
   walk(p)
 def test_in_memory_table_uncertainties(self):
  t=dict(department_tables(self.batch,self.data['updated_at']));self.assertEqual([len(t[k]) for k in ['总览','经历','导师','论文']],[11,82,1,26])
  z=next(r for r in t['经历'] if r[0]=='张钧萍' and r[2]=='学士');self.assertEqual(z[3],'哈尔滨工程大学/哈尔滨医科大学');self.assertEqual(z[10],'unknown');self.assertIs(z[11],True)
  h=next(r for r in t['经历'] if r[0]=='侯成宇' and r[2]=='博士');self.assertIsNone(h[11]);self.assertIn('历史在读',h[14])
 def test_queue_baseline_and_partial_scope(self):
  q=json.loads((ROOT/'progress/work-queue.json').read_text());self.assertEqual(q['base_commit'],'69469d6d80e5f686dbc9867c67d176ce8f1efce6');t=next(t for t in q['tasks'] if t['task_id']=='hit-seie:profiles');self.assertEqual(t['status'],'partial');self.assertFalse(t['scope']['university_complete']);self.assertIn('progress/harbin-information-progress.json',t['artifact_paths'])
