import copy,hashlib,json,pathlib,sys,unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from build import department_tables,validate
from build_rosters import validate_rosters
class InformationFinalTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.data=json.loads((ROOT/'data/atlas.json').read_text());cls.rosters=json.loads((ROOT/'data/rosters.json').read_text());cls.batch=[p for p in cls.data['people'] if p.get('data_batch_id')=='faculty-batch-harbin-eie-fourth-003'];cls.pending=[p for p in cls.data['pending_people'] if p.get('data_batch_id')=='faculty-batch-harbin-eie-fourth-003']
 def test_final_counts_and_pending_separation(self):
  self.assertTrue(validate(self.data));self.assertEqual([len(self.data['people']),len(self.data['pending_people'])],[197,9]);self.assertEqual([sum(len(p.get(k,[])) for p in self.data['people']) for k in ['education','appointments','mentors','committee_members','publications']],[618,762,91,9,388]);self.assertEqual(len(self.batch),12);self.assertEqual(len(self.pending),1);p=self.pending[0];self.assertEqual(p['name'],'李冬冬');self.assertEqual([len(p[k])for k in ['education','appointments','mentors','publications']],[0,0,0,0]);self.assertEqual(len(p['sources']),3)
 def test_frozen_coverage_hash_and_exact_strata(self):
  f=ROOT/'progress/harbin-information-coverage.json';self.assertEqual(hashlib.sha256(f.read_bytes()).hexdigest(),'8e3fee8f2e9017209dde8e98dcfad384012bf2178ca6628ad096c8c90f52893f');c=json.loads(f.read_text());self.assertEqual([c[k]for k in ['official_roster_count','first_pass_attempted','own_profile_academic_body_read','official_professional_evidence_read','substantive_professional_body','sparse_academic_history','name_only_extended_identity_pending']],[33,33,30,32,27,5,1]);self.assertTrue(all(not e['fields_complete']for e in c['entries']));self.assertEqual(c['review_status'],'all_three_batches_passed');self.assertTrue(all(b['review_status']=='passed_with_documented_limits'for b in c['batches']))
 def test_alternate_roster_links_are_independently_verified_not_redirects(self):
  self.assertTrue(validate_rosters(self.rosters,self.data));self.assertEqual(sum(e['profile_identity_verified']for e in self.rosters['entries']),191)
  for name in ['庄迪','李大森']:
   p=next(p for p in self.batch if p['name']==name);e=next(e for e in self.rosters['entries']if e['id']==p['roster_entry_id']);ev=e['profile_identity_evidence'];self.assertEqual(e['verified_person_id'],p['person_id']);self.assertEqual(ev['status'],'independent_current_official_profile_name_department_match');self.assertEqual(ev['independent_profile_verification']['roster_url'],e['official_profile_url']);self.assertEqual(ev['independent_profile_verification']['official_url'],p['official_url']);self.assertNotIn('redirect_chain',ev);self.assertNotIn('verified_alias_urls',ev);self.assertEqual(ev['original_roster_landing_observation']['requested_url'],ev['original_roster_landing_observation']['final_url'])
  e=next(e for e in self.rosters['entries']if e['name']=='李冬冬'and e['organization_id']=='hit-seie');self.assertFalse(e['profile_identity_verified']);self.assertFalse(e.get('verified_person_id'))
 def test_exact_internal_entities_and_non_promoted_candidates(self):
  people={p['person_id']:p for p in self.data['people']}
  for pid,mid in [('hit-lipeng','hit-huyue'),('hit-zhuangdi','hit-zhanglm')]:
   p=people[pid];m=p['mentors'][0];self.assertEqual(m['person_id'],mid);self.assertEqual(m['name'],people[mid]['name']);self.assertEqual(m['education_event_id'],p['education'][m['education_event_index']]['event_id']);self.assertNotEqual(m['employment_status'],'active_officially_listed')
  p=people['hit-zhaoyanlong'];self.assertEqual(p['mentors'],[]);self.assertFalse(p['pending_mentor_candidates'][0]['include_in_mentorship_graph'])
 def test_wuhan_classification_url_export_is_deduplicated_and_nonmutating(self):
  p=next(p for p in self.data['people']if p['name']=='肖傲然');before=copy.deepcopy(p);url='https://www.whu.edu.cn/xxgk/xxjj.htm';self.assertEqual(sum(e.get('classification_source')==url for e in p['education']),2);t=dict(department_tables([p],self.data['updated_at']));rows=[r for r in t['来源'][1:]if r[2]==url];self.assertEqual(len(rows),1);self.assertIn('非个人授位',rows[0][3]);self.assertEqual(p,before)
  duplicated=copy.deepcopy(p);duplicated['education'].append(copy.deepcopy(p['education'][0]));t=dict(department_tables([duplicated],self.data['updated_at']));self.assertEqual(sum(r[2]==url for r in t['来源'][1:]),1)
  existing=copy.deepcopy(p);existing['sources'].append({'id':'classification-in-existing-sources','url':url,'evidence_status':'official_university_introduction','retrieved_at':'2026-10-23'});t=dict(department_tables([existing],self.data['updated_at']));self.assertEqual(sum(r[2]==url for r in t['来源'][1:]),1)
 def test_ambiguous_985_unknown_stays_unknown_and_invalid_url_not_exported(self):
  p=copy.deepcopy(next(p for p in self.data['people']if p['name']=='张钧萍'));p['education']=p['education'][:1];before=copy.deepcopy(p);t=dict(department_tables([p],self.data['updated_at']));self.assertEqual(p,before);self.assertEqual(p['education'][0]['institution_985'],'unknown');self.assertEqual(len(t['来源']),len(p['sources'])+1);self.assertEqual(t['经历'][1][10],'unknown')
  p['education'][0]['institution_985']='yes';p['education'][0]['classification_source']='javascript:alert(1)';t=dict(department_tables([p],self.data['updated_at']));self.assertFalse(any(r[2]=='javascript:alert(1)'for r in t['来源'][1:]))
 def test_added_classification_rows_do_not_change_original_sources_or_academic_counts(self):
  for batch,expected in [('001',[11,82,1,26,62]),('002',[11,73,9,23,63]),('003',[13,59,6,27,63])]:
   ps=[p for p in self.data['people']if p.get('data_batch_id')=='faculty-batch-harbin-eie-fourth-'+batch];before=copy.deepcopy(ps);t=dict(department_tables(ps,self.data['updated_at']));self.assertEqual([len(t[k])for k in ['总览','经历','导师','论文','来源']],expected);self.assertEqual(ps,before)
  p=next(p for p in self.batch if p['name']=='何胜阳');self.assertEqual(p['appointments'][0]['status'],'historical_snapshot');self.assertEqual(p['appointments'][0]['evidence_as_of'],'2015-12-14')
 def test_source_and_event_references_close(self):
  for p in self.batch+self.pending:
   ids={s['id']for s in p['sources']};events={e['event_id']for e in p['education']}
   def walk(v):
    if isinstance(v,dict):
     for k,x in v.items():
      if (k=='source_id'or k.endswith('_source_id'))and x is not None:self.assertIn(x,ids)
      if k=='source_ids'or k.endswith('_source_ids'):self.assertTrue(set(x)<=ids)
      if k=='field_provenance':self.assertTrue(all(y is None or y in ids for y in x.values()))
      if k=='education_event_id'and x:self.assertIn(x,events)
      walk(x)
    elif isinstance(v,list):
     for x in v:walk(x)
   walk(p)
 def test_progress_records_full_first_pass_without_complete_biography_claim(self):
  pg=json.loads((ROOT/'progress/harbin-information-progress.json').read_text());self.assertTrue(pg['first_pass_complete']);self.assertFalse(pg['coverage_complete']);self.assertFalse(pg['all_fields_complete']);self.assertEqual([pg['detailed_profiles'],pg['pending_profiles']],[32,1]);self.assertEqual(pg['detailed_source_entries'],152);self.assertEqual(pg['pending_source_entries'],3);self.assertEqual(pg['batches'][-1]['normalized_package_sha256'],'9f926f3a940585ad7d32d876e8ece2a4656057eb54d540f49ad01d51ba4fd640');q=json.loads((ROOT/'progress/work-queue.json').read_text());self.assertEqual(q['base_commit'],'293677be17c182cfb7c7c42fc777a28a5f53dab6');task=next(t for t in q['tasks']if t['task_id']=='hit-seie:profiles');self.assertEqual(task['next_cursor'],'seie:first-pass-complete:uncertainty-review');self.assertEqual(task['status'],'partial');self.assertFalse(task['scope']['university_complete'])
