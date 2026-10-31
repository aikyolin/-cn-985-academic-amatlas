"""DRAFT. Exact reviewed delta + all affected generated tables; no inherited workbook reads."""
import copy,hashlib,json,os,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from atlas_storage import load_atlas
from restricted_hit_ai14_build import validate_exact_delta,MAPPING_SHA,BASE_MANIFEST_SHA,BASE_TREE
import build,build_rosters
from openpyxl import load_workbook
class HitAI14Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  if MAPPING_SHA is None:raise ValueError('independent mapping gate not bound')
  cls.parent=Path(os.environ['HIT_AI14_BASELINE_ROOT']).resolve()
  cls.receipt=json.loads(Path(os.environ['HIT_AI14_BUILD_RECEIPT']).read_text())
  if cls.parent==ROOT:raise ValueError('separate frozen baseline required')
  raw=(ROOT/'tests/fixtures/hit-ai14-source-mapping.json').read_bytes()
  if hashlib.sha256(raw).hexdigest()!=MAPPING_SHA:raise ValueError('mapping mismatch')
  cls.fixed=json.loads(raw);cls.base=load_atlas(cls.parent/'data/atlas.json');cls.actual=load_atlas(ROOT/'data/atlas.json');cls.site=load_atlas(ROOT/'site/atlas.json')
 def test_01_exact_old_objects_roots_and_reviewed_additions(self):
  validate_exact_delta(self.base,self.actual,self.fixed)
  for k,v in self.actual.items():self.assertEqual(self.site[k],v,k)
  self.assertEqual((ROOT/'data/rosters.json').read_bytes(),(self.parent/'data/rosters.json').read_bytes())
  others=[p for p in (ROOT/'site/people').glob('*.json') if p.name!='hit.json'];self.assertEqual(len(others),38)
  for p in others:self.assertEqual(p.read_bytes(),(self.parent/'site/people'/p.name).read_bytes(),p.name)
 def test_02_reject_old_new_unknown_or_extra_root_mutations(self):
  for key in ('people','pending_people','profile_batches','org_units'):
   bad=copy.deepcopy(self.actual);bad[key]=bad[key][1:]
   with self.assertRaises(ValueError):validate_exact_delta(self.base,bad,self.fixed)
  bad=copy.deepcopy(self.actual);bad['unexpected_root']='unreviewed'
  with self.assertRaises(ValueError):validate_exact_delta(self.base,bad,self.fixed)
  for i,p in enumerate(self.fixed['people'],1199):
   bad=copy.deepcopy(self.actual);bad['people'][i]['name']+='unreviewed'
   with self.assertRaises(ValueError):validate_exact_delta(self.base,bad,self.fixed)
   for j,e in enumerate(p['education']):
    if e['degree_awarded'] is None:
     bad=copy.deepcopy(self.actual);bad['people'][i]['education'][j]['degree_awarded']=True
     with self.assertRaises(ValueError):validate_exact_delta(self.base,bad,self.fixed)
 def test_05_source_specific_semantics(self):
  people=self.actual['people'][1199:];by={p['person_id']:p for p in people};events=[e for p in people for e in p['education']]
  self.assertEqual(len(events),26);self.assertEqual([sum(e['degree_awarded'] is v for e in events)for v in (True,None,False)],[15,7,4])
  self.assertEqual(sum(len(p['appointments'])for p in people),41);self.assertEqual(sum(len(p['mentors'])for p in people),2);self.assertEqual(sum(len(p['publications'])for p in people),0)
  for p in people:
   self.assertIsNone(p['roster_entry_id']);self.assertTrue(p['directory_grouping_only'])
   for e in p['education']:
    for k in ('institution_985','region','continent_code'):self.assertEqual(e[k],'unknown')
   for a in p['appointments']:self.assertIsNone(a['current_employment_verified'])
  liu=by['hit-liuxianming-ai14'];self.assertEqual([e['degree']for e in liu['education'][:2]],['学士（B.S.）','硕士（M.S.）']);self.assertEqual([e['degree_as_source']for e in liu['education'][:2]],['B.S.','M.S.'])
  for m in liu['mentors']:
   self.assertEqual(m['stage'],'unknown');self.assertIsNone(m['education_event_id']);self.assertIsNone(m['person_id']);self.assertFalse(m['navigation_verified']);self.assertFalse(m['quick_link_eligible']);self.assertIsNone(m['formal_dissertation_advisor_verified'])
  wang=by['hit-wangjinghua-ai14'];self.assertEqual([e['event_kind']for e in wang['education']],['study']*3);self.assertEqual([e['degree_awarded']for e in wang['education']],[None]*3);self.assertEqual([e['degree_as_source']for e in wang['education']],[None]*3)
  self.assertEqual(by['hit-yechenfei-ai14']['appointments'][0]['organization_as_source'],'国际人工智能学院')
  zheng=by['hit-zhengweijie-ai14']['appointments'][-1];self.assertEqual(zheng['employment_start'],'2022-06');self.assertIsNone(zheng['start']);self.assertIsNone(zheng['role_start_date'])
 def assert_tables(self,path,tables):
  book=load_workbook(path,read_only=True,data_only=False)
  try:
   self.assertEqual(book.sheetnames,list(tables))
   for name,rows in tables.items():
    expected=[[build.clean(v) if build.clean(v)!='' else None for v in row]for row in rows]
    width=max(map(len,expected),default=0);expected=[row+[None]*(width-len(row))for row in expected]
    self.assertEqual([list(row) for row in book[name].iter_rows(values_only=True)],expected,name)
  finally:book.close()
 def test_03_only_authorized_workbooks_full_tables_and_source_unknowns(self):
  deps,_=validate_exact_delta(self.base,self.actual,self.fixed)
  for dep in sorted(deps):
   members=[p for p in self.actual['people'] if p['department_id']==dep]
   old=[p for p in self.base['people'] if p['department_id']==dep]
   self.assertEqual(members[:len(old)],old)
   tables=dict(build.department_tables(members,self.actual['updated_at'],self.actual['institutions']))
   self.assertEqual(list(tables),['总览','经历','导师','论文','来源'])
   self.assert_tables(ROOT/'site/exports'/(dep+'.xlsx'),tables)
   headers=tables['经历'][0]
   for person in self.fixed['people']:
    if person['department_id']!=dep:continue
    rows=[r for r in tables['经历'][1:] if r[0]==person['name']]
    for row,event in zip(rows[:len(person['education'])],person['education'],strict=True):
     for header,key in [('事件类型','event_kind'),('阶段/职位','degree'),('开始','start'),('结束','end'),('备注及冲突','note')]:self.assertEqual(row[headers.index(header)],event[key])
     self.assertIs(row[headers.index('来源记载学位')],event['degree_awarded'])
  rosters=json.loads((ROOT/'data/rosters.json').read_text())
  self.assert_tables(ROOT/'site/exports/待核对名录.xlsx',build_rosters.roster_tables(build_rosters.prepare_rosters(rosters,self.actual),self.actual))
 def test_04_receipt_exact_scope_and_hashes(self):
  deps,_=validate_exact_delta(self.base,self.actual,self.fixed)
  workbooks={'site/exports/'+d+'.xlsx' for d in deps}|{'site/exports/待核对名录.xlsx'}
  outputs=workbooks|{'site/people/'+p.name for p in (ROOT/'data/people').glob('*.json')}|{'site/atlas.json','site/rosters.json','site/exports/待核对名录.csv'}
  r=self.receipt;self.assertEqual(r['status'],'HIT_AI14_RESTRICTED_BUILD_PASS');self.assertEqual(r['base_tree'],BASE_TREE);self.assertEqual(r['build_id'],self.site['build_id']);self.assertEqual(r['old_full_suite'],'NOT_RUN')
  self.assertEqual(set(r['generated_workbooks']),workbooks);self.assertEqual(set(r['generated_output_inventory']),outputs);self.assertEqual(set(r['generated_sha256']),outputs)
  for rel in outputs:self.assertEqual(hashlib.sha256((ROOT/rel).read_bytes()).hexdigest(),r['generated_sha256'][rel])
if __name__=='__main__':unittest.main()
