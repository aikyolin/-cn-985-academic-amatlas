"""Reviewed Weihai boundaries and explicit news-backed roster identity; no exports written."""
import copy,json,pathlib,sys,unittest
ROOT=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from build import validate,department_tables
from build_rosters import validate_rosters,roster_tables,_verified_profile_match
from validate_queue import validate_queue
class WeihaiFirstTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.data=json.loads((ROOT/'data/atlas.json').read_text());cls.rosters=json.loads((ROOT/'data/rosters.json').read_text());cls.people={p['name']:p for p in cls.data['people']};cls.batch=[p for p in cls.data['people']if p.get('data_batch_id')=='faculty-batch-weihai-info-001'];cls.pg=json.loads((ROOT/'progress/weihai-information-progress.json').read_text())
 def entry(self,name):return next(e for e in self.rosters['entries']if e['name']==name)
 def test_global_counts(self):
  d=self.data;self.assertTrue(validate(d));self.assertEqual([len(d['people']),len(d['pending_people'])],[228,11]);self.assertEqual([sum(c in p['campus_ids']for p in d['people'])for c in ['harbin','weihai','shenzhen']],[159,33,36]);self.assertEqual([sum(len(p.get(k,[]))for p in d['people'])for k in ['education','appointments','mentors','committee_members','publications','sources']],[711,882,104,9,472,872]);self.assertEqual(sum(e['profile_identity_verified']for e in self.rosters['entries']),223)
 def test_first10_stays_separate_and_jintao_is_updated_not_duplicated(self):
  self.assertEqual(len(self.batch),10);self.assertEqual(sum(p['person_id']=='hit-jintao'for p in self.data['people']),1);self.assertFalse(any(p['name']=='金涛'for p in self.batch));self.assertFalse(any(p.get('data_batch_id')!='faculty-batch-weihai-info-001'for p in self.batch));self.assertTrue(self.entry('金涛')['profile_identity_verified']);self.assertEqual(self.pg['department_detailed_profiles'],32)
 def test_approved_exact_hash_and_partial_scope(self):
  p=self.pg;b=p['batches'][0];self.assertEqual(b['source_sha256'],'7b1abbc558efd867e5669ef2c92b7ccd627a0eb40b6aed398feab4316e06850a');self.assertEqual(b['normalized_package_sha256'],'de8998249f31c4fac59da104418371842afdd8528e213268dce10181b1356982');self.assertEqual(b['independent_review_status'],'passed_with_documented_limits');self.assertEqual(b['source_embedded_review_status'],'pending_independent_review');self.assertEqual([p['scope'][k]for k in ['visible_roster_entries','academic_role_entries','experimental_center_engineering_role_entries']],[94,81,13]);self.assertFalse(p['first_pass_complete']);self.assertFalse(p['all_fields_complete']);self.assertTrue(all(not x['fields_complete']for x in p['entries']))
 def test_roster_identity_associations_are_closed(self):
  self.assertTrue(validate_rosters(self.rosters,self.data))
  for p in self.batch:
   e=self.entry(p['name']);self.assertEqual(e['verified_person_id'],p['person_id']);self.assertEqual(e['id'],p['roster_entry_id']);self.assertTrue(_verified_profile_match(e,p));self.assertTrue(set(e['profile_identity_evidence']['source_ids'])<={s['id']for s in p['sources']})
 def test_yu_news_identity_is_not_homepage_identity(self):
  p=self.people['于长军'];e=self.entry('于长军');ev=e['profile_identity_evidence'];self.assertFalse(e['official_profile_identity_verified']);self.assertTrue(e['professional_identity_verified']);self.assertEqual(e['identity_evidence_basis'],'official_university_news');self.assertEqual(ev['official_news_identity_verification']['news_source_ids'],['yuchangjun-source-3','yuchangjun-source-4']);self.assertEqual(ev['redirect_observation']['final_url'],'https://homepage.hit.edu.cn/noFound.html');self.assertFalse(ev['redirect_observation']['name_matches_title']);self.assertFalse(p['official_profile_navigation_eligible'])
 def test_matching_dead_url_cannot_replace_news_identity_evidence(self):
  e=copy.deepcopy(self.entry('于长军'));p=self.people['于长军'];e['profile_identity_evidence'].pop('official_news_identity_verification');self.assertFalse(_verified_profile_match(e,p))
  for key in ['professional_identity_verified','official_profile_identity_verified','official_profile_navigation_eligible']:
   e=copy.deepcopy(self.entry('于长军'));e.pop(key);self.assertFalse(_verified_profile_match(e,p))
 def test_news_source_ids_urls_and_organization_cannot_be_fabricated(self):
  p=self.people['于长军']
  for key,value in [('name','他人'),('organization_id','wrong'),('news_source_ids',['missing']),('source_ids',['yuchangjun-source-3']),('roster_url','https://example.test/')]:
   e=copy.deepcopy(self.entry('于长军'));e['profile_identity_evidence']['official_news_identity_verification'][key]=value;self.assertFalse(_verified_profile_match(e,p))
  e=copy.deepcopy(self.entry('于长军'));e['alternative_professional_sources'][0]['url']='https://example.test/';self.assertFalse(_verified_profile_match(e,p))
 def test_liuaijun_independent_identity_keeps_wrong_libo_url(self):
  p=self.people['刘爱军'];e=self.entry('刘爱军');self.assertEqual(e['official_profile_url'],'http://homepage.hit.edu.cn/libo?lang=zh');self.assertEqual(e['profile_identity_evidence']['incorrect_roster_landing_name'],'李博');self.assertNotEqual(e['verified_person_id'],self.entry('李博')['verified_person_id']);self.assertNotIn('redirect_chain',e['profile_identity_evidence']);self.assertNotIn('verified_alias_urls',e['profile_identity_evidence']);broken=copy.deepcopy(e);broken['profile_identity_evidence'].pop('independent_profile_verification');self.assertFalse(_verified_profile_match(broken,p))
 def test_news_overview_export_has_blank_homepage_and_explicit_alternative_reports(self):
  p=self.people['于长军'];before=copy.deepcopy(p);tables=dict(department_tables([p],self.data['updated_at']));head=tables['总览'][0];row=tables['总览'][1];self.assertEqual(row[head.index('官方主页')],'');self.assertIn('不可用',row[head.index('主页可用性')]);self.assertIn('news.hitwh.edu.cn',row[-1]);self.assertIn('news.hit.edu.cn',row[-1]);self.assertEqual(p,before)
  rt=roster_tables(self.rosters,self.data)['待核对名录'];self.assertIn('职业身份关联已核（不代表个人主页可用）',rt[0]);r=next(row for row in rt[1:]if row[1]=='于长军');self.assertEqual(r[6],'http://homepage.hit.edu.cn/yuchangjun?lang=zh');self.assertTrue(r[10]);self.assertIn('official_profile_identity_verified',str(r))
 def test_four_confirmed_advisors_and_indexed_candidate_are_separate(self):
  self.assertEqual(sum(len(p['mentors'])for p in self.batch),4);self.assertEqual(sum(len(p.get('pending_mentor_candidates',[]))for p in self.batch),1);rows=dict(department_tables(self.batch,self.data['updated_at']))['导师'];self.assertEqual(len(rows),5);self.assertFalse(any('洪奕光'in str(r)for r in rows));self.assertTrue(all('非独立核实的精确指导起讫'in str(r)for r in rows[1:]))
 def test_source_and_event_references_closed_without_internal_paths(self):
  for p in self.batch:
   ss={s['id']for s in p['sources']};es={e['event_id']for e in p['education']}
   def walk(v):
    if isinstance(v,dict):
     for k,x in v.items():
      self.assertFalse(k.endswith('_cache'));self.assertNotIn(k,{'body_cache','text_cache','retrieval_note','birth_date','birthday','students','student_list','email','phone'})
      if (k=='source_id'or k.endswith('_source_id'))and x is not None:self.assertIn(x,ss)
      if k=='source_ids'or k.endswith('_source_ids'):self.assertTrue(set(x)<=ss)
      if k=='education_event_id'and x:self.assertIn(x,es)
      walk(x)
    elif isinstance(v,list):
     for x in v:walk(x)
   walk(p);self.assertNotIn('/workspace/',json.dumps(p))
 def test_queue_and_national_readme_boundary(self):
  q=json.loads((ROOT/'progress/work-queue.json').read_text());self.assertEqual(q['base_commit'],'69469d6d80e5f686dbc9867c67d176ce8f1efce6');self.assertEqual(validate_queue(q,ROOT,True),[]);t=next(t for t in q['tasks']if t['task_id']=='hit-weihai-information:profiles');self.assertEqual(t['status'],'partial');self.assertEqual(t['next_cursor'],'weihai-information:associate-professor-researcher:position:11');self.assertEqual(self.pg['next_roster_name'],'孙烽豪');readme=(ROOT/'README.md').read_text();self.assertIn('全国',readme);self.assertNotIn('220',readme);coverage=(ROOT/'progress/current-coverage.md').read_text();self.assertIn('228 位',coverage);self.assertIn('81条学术岗位与13条实验技术岗位',coverage)
 def test_exact_full_name_anchor_href_corrections_are_not_guessed_slugs(self):
  report=json.loads((ROOT/'progress/weihai-roster-corrections.json').read_text());self.assertEqual(report['entries_checked'],94);self.assertEqual(report['corrected_local_mapping_count'],4);self.assertEqual(report['source_link_changes'],0)
  expected={'李剑锋':('roster-a536f2ea74f19323','lijianfeng','sunzhengnai'),'康文静':('roster-3b8d1cda9026fd1b','kangwenjing','renxiuyun'),'梅英杰':('roster-26e200666f5745b7','meiyingjie','lijianfeng'),'孙烽豪':('roster-b7a90d44c5bc9ffa','sunfenghao','kangwenjing')}
  for name,(entry_id,new,old)in expected.items():
   e=self.entry(name);self.assertEqual(e['id'],entry_id);self.assertEqual(e['official_profile_url'],f'http://homepage.hit.edu.cn/{new}?lang=zh');self.assertEqual(e['profile_identity_verified'],name!='孙烽豪');c=e['local_mapping_correction'];self.assertEqual(c['name'],name);self.assertEqual(c['previous_local_profile_url'],f'http://homepage.hit.edu.cn/{old}?lang=zh');self.assertFalse(c['source_changed']);self.assertEqual(c['basis'],'exact_full_anchor_name_and_href_alignment_original_and_current_source_agree');self.assertEqual(c['corrected_source_profile_url'],e['official_profile_url'])
 def test_historical_local_source_payloads_preserved_with_explicit_correction(self):
  for name in ['李剑锋','康文静','梅英杰','孙烽豪']:
   e=self.entry(name);o=next(o for o in self.rosters['source_observations']if o['record_id']==e['id']);self.assertEqual(o['source_payload']['official_profile_url'],e['local_mapping_correction']['previous_local_profile_url']);self.assertEqual(o['local_mapping_correction'],e['local_mapping_correction']);self.assertIn('不代表原始HTML实际锚链接',o['source_payload_interpretation'])
 def test_original_observation_export_shows_correction_without_overwriting_original(self):
  rows=roster_tables(self.rosters,self.data)['原始来源观察'];head=rows[0];row=next(r for r in rows[1:]if r[1]=='roster-3b8d1cda9026fd1b');self.assertEqual(row[6]['official_profile_url'],'http://homepage.hit.edu.cn/renxiuyun?lang=zh');self.assertIn('不代表原始HTML',row[head.index('历史本地观察解释')]);self.assertEqual(row[head.index('本地映射订正（原值不改写）')]['corrected_source_profile_url'],'http://homepage.hit.edu.cn/kangwenjing?lang=zh');ren=next(r for r in rows[1:]if r[1]=='roster-be0ee25c269c0c65');self.assertEqual(ren[head.index('已撤回的本地附注')]['names'],['任秀云','康文静'])
 def test_false_conflict_withdrawn_true_libo_conflict_and_entities_preserved(self):
  cs=[c for c in self.rosters['conflicts']if c['type']=='same_url_different_names'];self.assertEqual(len(cs),1);self.assertEqual(cs[0]['names'],['刘爱军','李博']);self.assertNotEqual(self.entry('任秀云')['official_profile_url'],self.entry('康文静')['official_profile_url']);self.assertTrue(all('共用，需身份核验'not in n for name in ['任秀云','康文静']for n in self.entry(name)['notes']));self.assertEqual(len(self.rosters['dedup_candidates']),60);self.assertEqual(self.pg['unresolved_name_pair'],[]);self.assertEqual(self.pg['scope_source_sha256'],'6db5f228384835723a800cf32756916ad6f36d51cca7949e49cc4ffdf2d7ddbe')
  report=json.loads((ROOT/'progress/weihai-roster-corrections.json').read_text());self.assertNotIn('/workspace/',json.dumps(report));self.assertNotIn('html_sha256',json.dumps(report));self.assertNotIn('_cache',json.dumps(report))
if __name__=='__main__':unittest.main()
