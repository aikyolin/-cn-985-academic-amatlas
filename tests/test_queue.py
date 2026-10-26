"""Synthetic fixtures only; these are not real progress claims."""
from atlas_test_io import load_atlas
import unittest,sys,pathlib,copy
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]/'scripts'))
from validate_queue import validate_queue
from jsonschema.exceptions import ValidationError
class QueueTests(unittest.TestCase):
 def setUp(self):
  self.d={'schema_version':'1.0','updated_at':'2026-10-23T09:00:00Z','base_commit':'a'*40,'scope':{'active_institution':'hit','target_university_count':39,'registry_complete':False},'tasks':[{'task_id':'hit:test:roster','institution_id':'hit','organization_id':'hit-aerospace','campus_ids':[],'stage':'roster_enumeration','status':'pending','scope':{'description':'Synthetic test scope','claim':'listed_public_scope_only','university_complete':False},'depends_on':[],'source_urls':['https://example.test/roster'],'artifact_paths':[],'review_status':'pending_review','next_action':'Review test fixture'}]}
 def test_valid_pending(self):self.assertEqual(validate_queue(self.d),[])
 def test_unreviewed_done_rejected(self):
  self.d['tasks'][0]['status']='done'
  with self.assertRaises(ValidationError):validate_queue(self.d)
 def test_duplicate_rejected(self):
  self.d['tasks'].append(copy.deepcopy(self.d['tasks'][0]))
  with self.assertRaises(ValueError):validate_queue(self.d)
 def test_unknown_dependency_rejected(self):
  self.d['tasks'][0]['depends_on']=['missing']
  with self.assertRaises(ValueError):validate_queue(self.d)
 def test_cycle_rejected(self):
  self.d['tasks'][0]['depends_on']=[self.d['tasks'][0]['task_id']]
  with self.assertRaises(ValueError):validate_queue(self.d)
 def test_absolute_artifact_rejected(self):
  self.d['tasks'][0]['artifact_paths']=['/private/file']
  with self.assertRaises(ValidationError):validate_queue(self.d)
 def test_whole_university_claim_rejected(self):
  self.d['tasks'][0]['scope']['university_complete']=True
  with self.assertRaises(ValidationError):validate_queue(self.d)
 def test_blocked_requires_reason(self):
  self.d['tasks'][0]['status']='blocked'
  with self.assertRaises(ValidationError):validate_queue(self.d)
 def test_real_checkpoint(self):
  import json
  root=pathlib.Path(__file__).resolve().parents[1]
  d=json.loads((root/'progress/work-queue.json').read_text());self.assertEqual(validate_queue(d,root,True),[])
  hit_tasks=[t for t in d['tasks'] if t['institution_id']=='hit'];self.assertEqual(len(hit_tasks),94);self.assertEqual(sum(t['status']=='done' for t in hit_tasks),16)
 def test_original_hit_tasks_preserve_all_evidence_with_new_school_tasks(self):
  import json,hashlib
  root=pathlib.Path(__file__).resolve().parents[1];q=json.loads((root/'progress/work-queue.json').read_text())
  tasks=[t for t in q['tasks'] if t['institution_id']=='hit']
  digest=hashlib.sha256(json.dumps(tasks,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
  self.assertEqual(digest,'1f16ada0ae6f60a29f5fd721897454390728bde9b05e5e87ecf4b1f071f05ca6')
 def test_campus_evidence_scope(self):
  import json,collections
  root=pathlib.Path(__file__).resolve().parents[1];d=load_atlas(root/'data/atlas.json');d['org_units']=[o for o in d['org_units'] if o.get('school_id')=='hit']
  self.assertEqual(collections.Counter(o['campus_id'] for o in d['org_units']),{'hit-harbin':28,'hit-shenzhen':27,'hit-weihai':13,None:10})
  self.assertTrue(all(o['is_complete'] is False for o in d['org_units']))
if __name__=='__main__':unittest.main()
