from published_fixture import published_root
"""Generic live-release boundaries for native roster aliases and source-access holds."""
import json,pathlib,unittest
from release28_history import CONTRACT,release28_view
from release30_history import CONTRACT as RELEASE30_CONTRACT,release30_view
ROOT=pathlib.Path(__file__).resolve().parents[1]
def read(rel,root=ROOT):
 value=json.loads((root/rel).read_text());return release30_view(value,rel)if rel in RELEASE30_CONTRACT else value
class ReviewedAppendBoundaries(unittest.TestCase):
 def test_original_prefixes_and_actual_generated_views_are_preserved(self):
  actual_site=json.loads((ROOT/'site/atlas.json').read_text());actual_data=json.loads((ROOT/'data/atlas.json').read_text())
  self.assertEqual(actual_site['people'],actual_data['people']);self.assertEqual(actual_site['pending_people'],actual_data['pending_people'])
  self.assertEqual(actual_site['build_id'],json.loads((ROOT/'site/rosters.json').read_text())['build_id'])
  for rel in CONTRACT:release28_view(read(rel,published_root() if rel=='site/atlas.json' else ROOT),rel)
  a=read('data/atlas.json');s=read('site/atlas.json',published_root());r=read('site/rosters.json')
  self.assertEqual(a['people'],s['people']);self.assertEqual(a['pending_people'],s['pending_people']);self.assertEqual(s['build_id'],r['build_id'])
 def test_native_identity_alias_requires_exact_target_and_closed_source_observation(self):
  a=read('data/atlas.json');r=read('data/rosters.json');es={e['id']:e for e in r['entries']};obs={o['record_id']:o for o in r['source_observations']}
  new=a['people'][CONTRACT['data/atlas.json']['lists']['people']['length']:]
  for p in new:
   e=es[p['roster_entry_id']];identity=p['identity_evidence'];native=identity.get('native_link_target')
   if identity['status']=='official_roster_native_link':
    self.assertEqual(native,p['official_url']);self.assertEqual(identity['profile_url'],native);self.assertTrue(e['profile_identity_verified']);self.assertEqual(e['verified_person_id'],p['person_id'])
   self.assertEqual(e['source_identity_evidence'],identity);self.assertEqual(obs[e['id']]['source_payload'],{k:v for k,v in e.items()if k!='source_observation_ids'})
 def test_held_source_candidates_never_promote_to_person_or_expand_selected_order(self):
  a=read('data/atlas.json')
  for school in read('progress/multischool-rotation003-wave5-coverage.json')['schools']:
   c=read(school['coverage_path']);held=c['held_candidates'];positions={}
   for x in c['selected_roster_original_order']+held:
    if x['order']in positions:self.assertEqual(positions[x['order']],x['name'])
    positions[x['order']]=x['name']
   self.assertEqual([positions[k]for k in sorted(positions)],c['selected_candidate_names'])
   names={p['name']for p in a['people']+a['pending_people']if p['school_id']==school['school_id']}
   for x in held:self.assertNotIn(x['name'],names)
   self.assertFalse(c['coverage_complete']);self.assertFalse(c['university_complete'])
if __name__=='__main__':unittest.main()
