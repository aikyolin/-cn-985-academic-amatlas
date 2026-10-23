"""Preserve truthful date precision without inventing a midnight timestamp."""
import copy,json,pathlib,sys,unittest
from jsonschema.exceptions import ValidationError
ROOT=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from validate_queue import validate_queue
class QueueDatePrecisionTests(unittest.TestCase):
 def fixture(self):
  return {'schema_version':'1.0','updated_at':'2026-10-23','base_commit':'a'*40,'scope':{'active_institution':'hit','target_university_count':39,'registry_complete':False},'tasks':[{'task_id':'hit:date-fixture','institution_id':'hit','organization_id':'hit-aerospace','campus_ids':[],'stage':'roster_enumeration','status':'partial','scope':{'description':'Synthetic date precision fixture','claim':'listed_public_scope_only','university_complete':False},'depends_on':[],'source_urls':['https://example.test/roster'],'artifact_paths':[],'review_status':'pending_review','next_action':'Review fixture','attempted_at':'2026-10-23'}]}
 def test_date_only_is_valid_and_not_rewritten(self):
  d=self.fixture();before=copy.deepcopy(d);self.assertEqual(validate_queue(d),[]);self.assertEqual(d,before)
 def test_explicit_datetime_retains_timezone_precision(self):
  d=self.fixture();d['updated_at']='2026-10-23T20:00:01Z';d['tasks'][0]['attempted_at']='2026-10-23T22:00:01+02:00';self.assertEqual(validate_queue(d),[])
 def test_invalid_date_time_or_type_is_rejected(self):
  for v in ('2026-02-30','2026-13-01','2026-10','2026-10-23T25:00:00Z','2026-10-23T12:00:00+01:99','2026-10-23T12:00:00-00:60','2026-10-23T12:00:00+24:00','2026-10-23T12:00:00-99:01','yesterday',123):
   for target in ('root','task'):
    with self.subTest(value=v,target=target):
     d=self.fixture()
     if target=='root':d['updated_at']=v
     else:d['tasks'][0]['attempted_at']=v
     with self.assertRaises(ValidationError):validate_queue(d)
if __name__=='__main__':unittest.main()
