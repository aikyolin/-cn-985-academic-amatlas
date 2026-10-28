"""Fixed 146 project-registry classifications; restricted build, never full build.

The existing process-local I/O guard and deterministic build/table functions are
reused unchanged. Other workbooks remain inherited bytes, not fresh validation.
"""
import argparse,copy,csv,hashlib,json,pathlib,sys,tempfile
import build,build_rosters,public_metadata as metadata
from atlas_storage import load_atlas,write_atlas,storage_inputs,compute_build_id
from restricted_recovery_build import RestrictedIOGuard
ROOT=pathlib.Path(__file__).resolve().parents[1]
BASE_COMMIT='81d53cd966707bd4e0def84f5aa7b3b6681aaaf2'
BASE_TREE='075152638276dd78822d2acc68659f6e187dd483'
MAPPING_SHA='859d2d07b7ac22fc9420ac6754cd733e9d1d067579c1f6a4256e13a666a963dc'
BASE_MANIFEST_SHA='8685bc9525f0392d5cb151a9668d30e5c1243234609318eb4b29a70f4c098c15'
sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
def pinned(path,expected):
 if sha(path)!=expected:raise ValueError('immutable input hash mismatch')
 return json.loads(pathlib.Path(path).read_text())
def validate_exact_delta(base,current,fixed):
 operations=fixed['operations']
 if len(operations)!=146:raise ValueError('exact146 mapping required')
 restored=copy.deepcopy(current);seen=set()
 registry={i['id']:i['official_name'] for i in base['institutions']}
 for o in operations:
  key=(o['person_index'],o['education_index'])
  if key in seen:raise ValueError('duplicate event')
  seen.add(key);p=restored['people'][key[0]];e=p['education'][key[1]];old=base['people'][key[0]]['education'][key[1]]
  if o['school_id']!=p['school_id'] or o['department_id']!=p['department_id'] or o['pointer']!=f'/people/{key[0]}/education/{key[1]}/institution_985' or o['institution']!=e['institution'] or o['registry_official_name']!=e['institution'] or o['before']!='unknown' or o['after']!='yes':raise ValueError('fixed operation metadata differs from actual event/person')
  if p['person_id']!=o['person_id'] or e['event_id']!=o['event_id'] or e['institution']!=registry[o['registry_id']] or e['institution_985']!='yes' or old['institution_985']!='unknown':raise ValueError('event/registry identity or exact transition changed')
  e['institution_985']='unknown'
 if restored!=base:raise ValueError('change outside exact146 institution_985 fields')
 deps={o['department_id'] for o in operations};schools={o['school_id'] for o in operations}
 if len(deps)!=64 or len(schools)!=21 or 'xmu' in schools:raise ValueError('fixed scope mismatch')
 return deps,schools

def check_metadata(root,known,workbooks,final):
 checked=[];errors=[];skipped=[]
 for rel in sorted(metadata.publication_files(root)):
  if not final and rel.startswith('site/'):continue
  p=root/rel;suffix=p.suffix.lower()
  if suffix=='.xlsx':
   if not final or rel not in workbooks:skipped.append(rel);continue
   errors+=metadata._xlsx_errors(p,rel,known)
  elif suffix=='.json':errors+=metadata.metadata_errors(json.loads(p.read_text()),source=rel,public_files=known)
  elif suffix in {'.md','.html','.txt','.yml','.yaml'}:errors+=metadata._document_errors(p.read_text(),rel,known)
  elif final and suffix in {'.csv','.tsv'}:
   with p.open(newline='') as f:
    reader=csv.reader(f,delimiter='\t' if suffix=='.tsv' else ',');headers=next(reader,[])
    for i,row in enumerate(reader,2):
     for j,value in enumerate(row):errors+=metadata._cell_errors(value,rel,known,f'/row/{i}/column/{j}',headers[j] if j<len(headers) else '')
  else:continue
  checked.append(rel)
 if errors:raise ValueError('metadata errors: '+str(errors))
 return {'checked':checked,'unchanged_workbook_content_not_rechecked':skipped}

def run(plan_path,plan_sha,baseline_root,base_manifest,receipt_path):
 guard=RestrictedIOGuard(ROOT);sys.addaudithook(guard)
 plan=pinned(plan_path,plan_sha)
 if plan.get('status')!='CLASSIFICATION146_RESTRICTED_SCOPE_APPROVED' or plan.get('base_commit')!=BASE_COMMIT or plan.get('base_tree')!=BASE_TREE:raise ValueError('wrong explicit scope gate')
 manifest=pinned(base_manifest,BASE_MANIFEST_SHA)
 if manifest['tree_sha']!=BASE_TREE or manifest['complete_blob_count']!=1005:raise ValueError('wrong base tree')
 catalog={r['path']:r for r in manifest['files']}
 fixed=pinned(ROOT/'tests/fixtures/classification146-exact-project-registry.json',MAPPING_SHA)
 baseline_root=pathlib.Path(baseline_root).resolve()
 for label,raw in storage_inputs(baseline_root/'data/atlas.json'):
  rel='data/'+label;oid=hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
  if catalog[rel]['sha']!=oid:raise ValueError('baseline canonical Git blob differs')
 raw=(baseline_root/'data/rosters.json').read_bytes()
 if hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()!=catalog['data/rosters.json']['sha']:raise ValueError('base roster Git blob differs')
 if raw!=(ROOT/'data/rosters.json').read_bytes():raise ValueError('canonical roster changed')
 current=load_atlas(ROOT/'data/atlas.json');base=load_atlas(baseline_root/'data/atlas.json');deps,schools=validate_exact_delta(base,current,fixed)
 if len(plan['department_ids'])!=64 or len(plan['school_ids'])!=21 or set(plan['department_ids'])!=deps or set(plan['school_ids'])!=schools:raise ValueError('plan scope differs from exact operations or contains duplicates')
 gate=pinned(plan['source_gate_path'],plan['source_gate_sha256'])
 inputs={k:hashlib.sha256(v).hexdigest() for k,v in storage_inputs(ROOT/'data/atlas.json')};inputs['data/rosters.json']=sha(ROOT/'data/rosters.json')
 if gate.get('status')!='CLASSIFICATION146_INDEPENDENT_BOUNDARY_PASS' or gate['canonical_input_sha256']!=inputs:raise ValueError('canonical source gate differs')
 build.validate(current)
 exports=build.department_exports(current);selected=[e for e in exports if e['department_id'] in deps]
 if len(selected)!=64 or any(e['school_id'] not in schools for e in selected):raise ValueError('unsafe department selection')
 workbooks={'site/exports/'+e['department_id']+'.xlsx' for e in selected}|{'site/exports/待核对名录.xlsx'}
 outputs=workbooks|{'site/people/'+p.name for p in (ROOT/'data/people').glob('*.json')}|{'site/atlas.json','site/rosters.json','site/exports/待核对名录.csv'}
 receipt_path=pathlib.Path(receipt_path).resolve()
 if receipt_path.is_relative_to(ROOT) or receipt_path.exists():raise ValueError('receipt must be a new external file')
 temp=receipt_path.parent/('classification-tmp-'+plan_sha[:16])
 if temp.is_symlink() or (temp.exists() and (not temp.is_dir() or any(temp.iterdir()))):raise ValueError('unsafe or nonempty temporary directory')
 guard.configure([ROOT/p for p in outputs]+[receipt_path],temp);temp.mkdir(exist_ok=True);tempfile.tempdir=str(temp)
 known=frozenset(metadata.publication_files(ROOT)|set(catalog));pre=check_metadata(ROOT,known,workbooks,False)
 current['build_id']=hashlib.sha256((compute_build_id(ROOT)+sha(__file__)+plan_sha).encode()).hexdigest()[:16]
 for export in selected:
  people=[p for p in current['people'] if p['department_id']==export['department_id'] and p['school_id']==export['school_id']]
  book=build.Workbook();book.remove(book.active)
  for name,rows in build.department_tables(people,current['updated_at'],current['institutions']):build.sheet(book,name,rows,build.disabled_sources_by_person(people))
  build.save_deterministic_xlsx(book,ROOT/'site/exports'/(export['department_id']+'.xlsx'))
 build_rosters.build_rosters(current,generate_excel=True)
 rpath=ROOT/'site/rosters.json';roster=json.loads(rpath.read_text());roster['build_id']=current['build_id'];rpath.write_text(json.dumps(roster,ensure_ascii=False,indent=2)+'\n')
 current['exports']=exports;write_atlas(ROOT/'site/atlas.json',current)
 final=check_metadata(ROOT,known,workbooks,True)
 result={'status':'CLASSIFICATION146_RESTRICTED_BUILD_PASS','base_commit':BASE_COMMIT,'base_tree':BASE_TREE,'plan_sha256':plan_sha,'build_id':current['build_id'],'preflight':pre,'final_metadata':final,'generated_workbooks':sorted(workbooks),'generated_output_inventory':sorted(outputs),'generated_sha256':{p:sha(ROOT/p) for p in sorted(outputs)},'source_classification_basis':'本项目既有39校名单精确匹配派生分类，非新增来源核验。','old_full_suite':'NOT_RUN','inherited_content_not_rechecked':{p:{'mode':r['mode'],'sha':r['sha']} for p,r in catalog.items() if p not in metadata.publication_files(ROOT)}}
 if any(temp.iterdir()):raise ValueError('unexpected temporary residue')
 temp.rmdir();receipt_path.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');return result
if __name__=='__main__':
 p=argparse.ArgumentParser()
 for flag in ['plan','plan-sha256','baseline-root','base-manifest','receipt']:p.add_argument('--'+flag,required=True)
 a=p.parse_args();run(a.plan,a.plan_sha256,a.baseline_root,a.base_manifest,a.receipt)
