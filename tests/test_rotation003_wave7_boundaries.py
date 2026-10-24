"""Generic reviewed append conservation and scope boundaries; factual expectations are frozen data."""
import copy,hashlib,json,pathlib,re,unittest
from release30_history import CONTRACT,release30_view
ROOT=pathlib.Path(__file__).resolve().parents[1]
def read(rel):return json.loads((ROOT/rel).read_text())
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
FIXTURE=ROOT/'tests/fixtures/rotation003-wave7-source-contract.json'
assert hashlib.sha256(FIXTURE.read_bytes()).hexdigest()=='7121c78c32a981666579046d397eb3383c124b6e90d31642b310ef80eb60a80d','Reviewed source contract bytes changed'
SOURCE=json.loads(FIXTURE.read_text())
# Public metadata guard is applied only to this append, never to frozen prior records.
PRIVATE_SOURCE_KEYS={'evidence_file','evidence_sha256','web_reference','selection_lock','source_file','source_sha256','review_sha256','reviewed_source_sha256','independent_review_sha256','data_file','data_sha256','scope_file','qa_file','review_file','manifest_file','manifest_sha256','source_references'}
def assert_public_metadata(value):
 if isinstance(value,dict):
  assert not PRIVATE_SOURCE_KEYS.intersection(value),'Private source locator or unverifiable artifact fingerprint in this append'
  if 'source_files'in value:assert value['source_files']==[],'Local source packages are not public evidence links'
  for item in value.values():assert_public_metadata(item)
 elif isinstance(value,list):
  for item in value:assert_public_metadata(item)
 elif isinstance(value,str):
  assert not value.startswith(('/workspace/','/home/','/tmp/','/private/','/Users/')),'Local absolute path in this append'
  assert not re.search(r'\bturn\d+(?:view|search|fetch|file)\d*\b',value),'Private tool reference in this append'
  assert not re.search(r'(?:research-rotation003-wave7-[^/]+|review-rotation003-wave7)/',value),'Unpublished review artifact path in this append'
def public_original_hash(record):
 if 'public_original_object_sha256' in record:
  assert record['original_view']=='public_metadata_v1'
  return record['public_original_object_sha256']
 assert 'original_view' not in record
 return record['original_object_sha256']
class ReviewedAppendBoundaries(unittest.TestCase):
 def test_exact_public_history_and_original_source_leaf_reversibility(self):
  for rel in CONTRACT:release30_view(read(rel),rel)
  assert_public_metadata(SOURCE)
  for rel,keys in [('data/atlas.json',['people','profile_batches','normalization_evidence']),('site/atlas.json',['people','profile_batches','normalization_evidence']),('data/rosters.json',['entries','batches','source_observations']),('site/rosters.json',['entries','batches'])]:
   data=read(rel)
   for key in keys:assert_public_metadata(data[key][CONTRACT[rel]['lists'][key]['length']:])
  schools={r['original']['school_id']for r in SOURCE['people']}|set(SOURCE['held_schools'])
  for sid in schools:assert_public_metadata(read('progress/'+sid+'-rotation003-wave7-coverage.json'))
  aggregate=read('progress/multischool-rotation003-wave7-coverage.json');assert_public_metadata(aggregate)
  for school in aggregate['schools']:self.assertNotIn('reference',school)
  people={p['person_id']:p for p in read('data/atlas.json')['people']};rosters=read('data/rosters.json');entries={e['id']:e for e in rosters['entries']}
  for record in SOURCE['people']:
   original=record['original'];current=people[original['person_id']];projection=copy.deepcopy(current)
   self.assertEqual(digest(original),public_original_hash(record))
   entry=record['original_roster_entry'];observations=[o for o in rosters['source_observations']if o['record_id']==entry['id']];self.assertEqual(len(observations),1);self.assertEqual(observations[0]['source_payload'],entry)
   for key,value in entry.items():self.assertEqual(entries[entry['id']][key],value)
   for rule in record['normalization_rules']:
    self.assertEqual(pointer(original,rule['path']),rule['before']);self.assertEqual(pointer(current,rule['path']),rule['after'])
    self.assertEqual(pointer(current,rule['preserved_at']),rule['before']);self.assertEqual(rule['source_projection_sha256'],record['original_object_sha256'])
    self.assertTrue(set(rule['source_ids'])<={s['id']for s in original['sources']});restore(projection,rule['path'],rule['before'])
   self.assertEqual(digest(original_projection(original,projection)),public_original_hash(record))
 def test_reviewed_batch_collections_and_held_scopes_remain_bounded(self):
  atlas=read('data/atlas.json');rosters=read('data/rosters.json');ids={row['original']['person_id']for row in SOURCE['people']}
  people=[p for p in atlas['people']if p['person_id']in ids];self.assertEqual(len(people),len(ids))
  self.assertEqual({p['person_id']for p in atlas['people'][CONTRACT['data/atlas.json']['lists']['people']['length']:]},ids)
  self.assertEqual([sum(e['degree_awarded']is v for p in people for e in p['education'])for v in [True,False,None]],SOURCE['awards_true_false_null'])
  for key,count in SOURCE['collection_counts'].items():self.assertEqual(sum(len(p.get(key,[]))for p in people),count,key)
  for sid in SOURCE['held_schools']:
   for rel,current,key in [('data/atlas.json',atlas,'people'),('data/atlas.json',atlas,'pending_people'),('data/atlas.json',atlas,'org_units'),('data/rosters.json',rosters,'entries'),('data/rosters.json',rosters,'source_observations')]:
    old=release30_view(current,rel);self.assertEqual([r for r in current[key]if r.get('school_id')==sid],[r for r in old[key]if r.get('school_id')==sid])
 def test_event_links_and_navigation_have_independent_evidence_boundaries(self):
  atlas=read('data/atlas.json');ids={r['original']['person_id']for r in SOURCE['people']}
  for p in [p for p in atlas['people']if p['person_id']in ids]:
   events={e['event_id']:e for e in p['education']}
   for e in events.values():
    self.assertIs(e['include_in_degree_filters'],e['event_kind']=='degree'and e['degree_awarded']is True)
    if e['degree_awarded']is not True:self.assertIs(e['include_in_education_filters'],False)
   for m in p['mentors']:
    linked=m.get('education_event_ids')
    if linked is not None:
     self.assertGreater(len(linked),1);self.assertEqual(len(linked),len(set(linked)));self.assertTrue(set(linked)<=set(events));self.assertIsNone(m['education_event_id'])
     self.assertEqual(sum(x['name']==m['name']and x['source_url']==m['source_url']for x in p['mentors']),1)
    else:self.assertIn(m['education_event_id'],events)
    if not m.get('navigation_verified'):self.assertIs(m['quick_link_eligible'],False)
   if p.get('official_profile_navigation_eligible')is False:
    self.assertIs(p['official_profile_navigation_eligible'],False);self.assertIs(p['navigation_verified'],False);self.assertEqual(p['employment_status'],'unknown')
    self.assertIs(p['current_personnel_observation']['personnel_status_verified'],False);self.assertIs(p['include_in_current_faculty_count'],False)
if __name__=='__main__':unittest.main()
