"""Scoped classification tests; inherited/XMU workbook bytes are never opened."""
import copy,hashlib,json,os,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from atlas_storage import load_atlas
import build,restricted_classification_build as driver
from openpyxl import load_workbook
class Classification146Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.baseline=Path(os.environ['CLASSIFICATION_BASELINE_ROOT']).resolve();cls.base=load_atlas(cls.baseline/'data/atlas.json');cls.current=load_atlas(ROOT/'data/atlas.json')
  cls.fixed=driver.pinned(ROOT/'tests/fixtures/classification146-exact-project-registry.json',driver.MAPPING_SHA);cls.ops=cls.fixed['operations'];cls.deps={o['department_id'] for o in cls.ops}
 def test_01_exact_inverse_and_all_original_objects(self):
  self.assertEqual(len(self.current['people']),1149);self.assertEqual(driver.validate_exact_delta(self.base,self.current,self.fixed),(self.deps,{o['school_id'] for o in self.ops}))
  self.assertEqual(len({o['person_id'] for o in self.ops}),72)
  for key in self.base:
   if key!='people':self.assertEqual(self.current[key],self.base[key])
 def test_02_excluded_event_geography_awards_and_source_claims(self):
  e=self.fixed['excluded'][0];p=next(p for p in self.current['people'] if p['person_id']==e['person_id']);event=next(x for x in p['education'] if x['event_id']==e['event_id']);self.assertEqual(event['institution_985'],'unknown')
  for o in self.ops:
   old=self.base['people'][o['person_index']]['education'][o['education_index']];new=self.current['people'][o['person_index']]['education'][o['education_index']]
   for key in set(old)|set(new):
    if key!='institution_985':self.assertEqual((key in old,old.get(key)),(key in new,new.get(key)))
  self.assertIn('非新增官网核验',self.fixed['label'])
 def test_03_negative_scope_and_no_alias_or_award_promotion(self):
  for key,value in [('region','mainland'),('degree_awarded',False),('source_url','https://example.invalid/new')]:
   changed=copy.deepcopy(self.current);o=self.ops[0];changed['people'][o['person_index']]['education'][o['education_index']][key]=value
   with self.assertRaises(ValueError):driver.validate_exact_delta(self.base,changed,self.fixed)
  duplicate=copy.deepcopy(self.fixed);duplicate['operations'][-1]=duplicate['operations'][0]
  with self.assertRaises(ValueError):driver.validate_exact_delta(self.base,self.current,duplicate)
  bad_scope=copy.deepcopy(self.fixed);bad_scope['operations'][0]['department_id']='xmu-not-authorized'
  with self.assertRaises(ValueError):driver.validate_exact_delta(self.base,self.current,bad_scope)
  alias=copy.deepcopy(self.current);o=self.ops[0];alias['people'][o['person_index']]['education'][o['education_index']]['institution']+=' '
  with self.assertRaises(ValueError):driver.validate_exact_delta(self.base,alias,self.fixed)
 def test_04_all64_five_tables_and_members_unchanged(self):
  for dep in sorted(self.deps):
   with self.subTest(department=dep):
    people=[p for p in self.current['people'] if p['department_id']==dep];old=[p for p in self.base['people'] if p['department_id']==dep];self.assertEqual([p['person_id'] for p in people],[p['person_id'] for p in old])
    book=load_workbook(ROOT/'site/exports'/(dep+'.xlsx'),read_only=True,data_only=False)
    try:
     self.assertEqual(book.sheetnames,['总览','经历','导师','论文','来源'])
     for name,rows in build.department_tables(people,self.current['updated_at'],self.current['institutions']):
      expected=[[build.clean(v) if build.clean(v)!='' else None for v in row] for row in rows];self.assertEqual([list(row) for row in book[name].iter_rows(values_only=True)],expected)
    finally:book.close()
 def test_05_current_receipt_and_unchanged_materialized_workbooks(self):
  receipt=json.loads(Path(os.environ['CLASSIFICATION_BUILD_RECEIPT']).read_text());self.assertEqual(receipt['status'],'CLASSIFICATION146_RESTRICTED_BUILD_PASS');self.assertEqual(receipt['old_full_suite'],'NOT_RUN');self.assertEqual(len(receipt['generated_workbooks']),65);self.assertEqual(len(receipt['generated_output_inventory']),107)
  for rel,sha in receipt['generated_sha256'].items():self.assertEqual(hashlib.sha256((ROOT/rel).read_bytes()).hexdigest(),sha)
  prior=json.loads((ROOT/'tests/fixtures/new-recovery123-public-conservation-pins.json').read_text());self.assertEqual(len(prior['departments']),98)
  for dep in prior['departments']:
   self.assertNotEqual(dep['school_id'],'xmu');rel=Path('site/exports')/(dep['department_id']+'.xlsx')
   if str(rel) not in receipt['generated_workbooks']:self.assertEqual((ROOT/rel).read_bytes(),(self.baseline/rel).read_bytes())
  self.assertFalse(list((ROOT/'site/exports').glob('xmu-*.xlsx')))
if __name__=='__main__':unittest.main()
