"""Generic reviewed-append preservation, held-scope and conservative consumer boundaries."""
import copy,hashlib,json,pathlib,unittest
from release29_history import CONTRACT,release29_view
from release30_history import CONTRACT as RELEASE30_CONTRACT,release30_view
ROOT=pathlib.Path(__file__).resolve().parents[1]
def read(rel):
 value=json.loads((ROOT/rel).read_text());return release30_view(value,rel)if rel in RELEASE30_CONTRACT else value
def digest(value):return hashlib.sha256(json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def pointer(value,path):
 for part in path.split('/')[1:]:
  key=part.replace('~1','/').replace('~0','~');value=value[int(key)]if isinstance(value,list)else value[key]
 return value
def restore(value,path,replacement):
 parent,_,key=path.rpartition('/');target=pointer(value,parent);key=key.replace('~1','/').replace('~0','~');target[int(key)if isinstance(target,list)else key]=copy.deepcopy(replacement)
def original_projection(original,current):
 assert type(original)is type(current)
 if isinstance(original,dict):
  assert original.keys()<=current.keys()
  if not original:assert not current
  return {key:original_projection(value,current[key])for key,value in original.items()}
 if isinstance(original,list):
  assert len(original)==len(current)
  return [original_projection(left,right)for left,right in zip(original,current)]
 assert original==current
 return current
def public_original_hash(record):
 if 'public_original_object_sha256' in record:
  assert record['original_view']=='public_metadata_v1'
  return record['public_original_object_sha256']
 assert 'original_view' not in record
 return record['original_object_sha256']
class ReviewedAppendBoundaries(unittest.TestCase):
 def test_exact_public_original_snapshots_and_source_fields_remain_recoverable(self):
  for rel in CONTRACT:release29_view(read(rel),rel)
  contract=read('tests/fixtures/rotation003-wave6-source-contract.json');people={p['person_id']:p for p in read('data/atlas.json')['people']}
  for record in contract['people']:
   original=record['original'];self.assertEqual(digest(original),public_original_hash(record));current=people[original['person_id']];projection=copy.deepcopy(current)
   for rule in record['normalization_rules']:
    self.assertEqual(pointer(original,rule['path']),rule['before'])
    self.assertEqual(pointer(current,rule['path']),rule['after'])
    self.assertEqual(pointer(current,rule['preserved_at']),rule['before'])
    self.assertEqual(rule['review_sha256'],record['review_sha256'])
    self.assertTrue(set(rule['source_ids'])<={s['id']for s in original['sources']})
    restore(projection,rule['path'],rule['before'])
   self.assertEqual(digest(original_projection(original,projection)),public_original_hash(record))
 def test_original_selection_and_zero_profile_outcomes_do_not_promote_holds(self):
  atlas=read('data/atlas.json');rosters=read('data/rosters.json');aggregate=read('progress/multischool-rotation003-wave6-coverage.json')
  people=atlas['people'][CONTRACT['data/atlas.json']['lists']['people']['length']:]
  pending=atlas['pending_people'][CONTRACT['data/atlas.json']['lists']['pending_people']['length']:]
  entries=rosters['entries'][CONTRACT['data/rosters.json']['lists']['entries']['length']:]
  new_units=atlas['org_units'][CONTRACT['data/atlas.json']['lists']['org_units']['length']:]
  for school in aggregate['schools']:
   coverage=read(school['coverage_path']);sid=school['school_id'];selected=coverage['selected_roster_original_order']
   self.assertEqual([row['name']for row in sorted(selected,key=lambda row:row['order'])],coverage['selected_candidate_names'])
   actual=[p for p in people if p['school_id']==sid];self.assertEqual(len(actual),coverage['counts']['professional_profiles'])
   self.assertFalse(coverage['coverage_complete']);self.assertFalse(coverage['university_complete'])
   for held in coverage['held_candidates']:
    self.assertNotIn(held['name'],{p['name']for p in people+pending if p['school_id']==sid})
    self.assertNotIn(held['id'],{e['id']for e in entries})
   if not actual:
    self.assertFalse([p for p in pending if p['school_id']==sid]);self.assertFalse([u for u in new_units if u['school_id']==sid]);self.assertFalse([e for e in entries if e['school_id']==sid])
 def test_award_navigation_and_independent_fact_collections_remain_conservative(self):
  atlas=read('data/atlas.json');people=atlas['people'][CONTRACT['data/atlas.json']['lists']['people']['length']:]
  aggregate=read('progress/multischool-rotation003-wave6-coverage.json')
  for key,value in aggregate['counts']['source_collections'].items():self.assertEqual(sum(len(p.get(key,[]))for p in people),value,key)
  for person in people:
   for event in person['education']:
    self.assertIs(event['include_in_degree_filters'],event['event_kind']=='degree'and event['degree_awarded']is True)
    if event['degree_awarded']is False:self.assertIs(event['include_in_education_filters'],False)
    if event['degree_awarded']is True:
     sid=event['field_provenance']['degree_awarded'];self.assertEqual(event['degree_award_source_url'],next(s['url']for s in person['sources']if s['id']==sid))
   for mentor in person['mentors']:
    self.assertIn(mentor['education_event_id'],{e['event_id']for e in person['education']})
    self.assertFalse(mentor['quick_link_eligible']);self.assertFalse(mentor['navigation_verified'])
if __name__=='__main__':unittest.main()
