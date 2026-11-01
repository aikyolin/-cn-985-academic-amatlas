"""Exact reviewed56 source-profile static build. No workbook generation or I/O."""
import copy,hashlib,json,pathlib,sys,tempfile,argparse
import build,build_rosters
from atlas_storage import load_atlas,write_atlas,storage_inputs,compute_build_id
from restricted_recovery_build import RestrictedIOGuard
ROOT=pathlib.Path(__file__).resolve().parents[1]
MAPPING_SHA='cfcf08fe8268411655b37a529991dea21de31676f7c70673772102a0f5dbf9dd'
BASE_MANIFEST_SHA='607cc425dca47edd23d802fb46b7173c6843b3c3bb2cf53a49767ddb21290d43'
BASE_TREE='ce4575fe30d7797893f27b04df52bd352141b9de'
BASE_METADATA_SHA='5ed6ac3e7b470a0930840e6b55bdca36a7f5b6d903dc92f67aabb4f238f45a3f'
sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
def pin(p,h):
 if sha(p)!=h:raise ValueError('Immutable input hash mismatch')
 return json.loads(pathlib.Path(p).read_text())
def project_base_metadata(base):
 spec=pin(ROOT/'tests/fixtures/supplemental56-baseline-metadata-projection.json',BASE_METADATA_SHA)
 projected=copy.deepcopy(base);by={p['person_id']:p for p in projected['people']};seen=set()
 for row in spec['leaves']:
  key=(row['person_id'],tuple(row['path']))
  if key in seen:raise ValueError('duplicate metadata projection path')
  seen.add(key);obj=by[row['person_id']]
  for k in row['path'][:-1]:obj=obj[k]
  old=obj[row['path'][-1]];new=row['value']
  if not isinstance(old,str)or not isinstance(new,str)or hashlib.sha256(old.encode()).hexdigest()!=row['before_sha256']or hashlib.sha256(new.encode()).hexdigest()!=row['after_sha256']:raise ValueError('exact metadata projection mismatch')
  obj[row['path'][-1]]=new
 if len(seen)!=31:raise ValueError('exact31 metadata leaves required')
 roots=set()
 for row in spec['root_leaves']:
  key=tuple(row['path'])
  if key in roots:raise ValueError('duplicate root metadata path')
  roots.add(key);obj=projected
  for k in row['path'][:-1]:obj=obj[k]
  old=obj[row['path'][-1]];new=row['value']
  if not isinstance(old,str)or not isinstance(new,str)or hashlib.sha256(old.encode()).hexdigest()!=row['before_sha256']or hashlib.sha256(new.encode()).hexdigest()!=row['after_sha256']:raise ValueError('exact root metadata projection mismatch')
  obj[row['path'][-1]]=new
 if len(roots)!=2:raise ValueError('exact2 root metadata leaves required')
 return projected
def validate_exact_delta(base,current,fixed):
 base=project_base_metadata(base)
 if len(base['people'])!=1318 or len(current['people'])!=1374 or len(fixed['people'])!=56:raise ValueError('exact1318+56 required')
 if current['people']!=base['people']+fixed['people']:raise ValueError('changed source people/order')
 if len({p['person_id']for p in current['people']})!=1374:raise ValueError('duplicate source identity')
 if len(current['pending_people'])!=84:raise ValueError('pending people changed')
 expected={'hnu-civil-source-directory':54,'uestc-foreign-languages-source-directory':1,'buaa-reliability-source-directory':1}
 if {d:sum(p['department_id']==d for p in fixed['people'])for d in expected}!=expected or {p['department_id']for p in fixed['people']}!=set(expected):raise ValueError('wrong department scope')
 if {p['school_id']for p in fixed['people']}!={'hnu','uestc','buaa'}:raise ValueError('wrong school scope')
 if any(p.get('roster_entry_id')is not None or p.get('campus')is not None or p['campus_ids']!=[] for p in fixed['people']):raise ValueError('no campus or roster merge')
 inverse=copy.copy(current)
 for k in ['people','profile_batches','org_units']:
  if current[k]!=base[k]+fixed[k]:raise ValueError('not exact approved append '+k)
  inverse[k]=base[k]
 if inverse!=base:raise ValueError('unrelated root changed')
 if len(fixed['org_units'])!=3 or len(fixed['profile_batches'])!=3:raise ValueError('wrong org/batch count')
 return set(expected)
def run(base_root,base_manifest,gate_path,gate_sha,receipt_path):
 guard=RestrictedIOGuard(ROOT);sys.addaudithook(guard)
 base_root=pathlib.Path(base_root).resolve();manifest=pin(base_manifest,BASE_MANIFEST_SHA)
 if manifest['tree_sha']!=BASE_TREE:raise ValueError('wrong base tree')
 fixed=pin(ROOT/'tests/fixtures/supplemental56-source-mapping.json',MAPPING_SHA);catalog={e['path']:e for e in manifest['files']}
 for name,b in storage_inputs(base_root/'data/atlas.json'):
  if hashlib.sha256(b).hexdigest()!=catalog['data/'+name]['sha256']:raise ValueError('base canonical not frozen')
 for rel in ['data/rosters.json','site/app.js','site/model.js','site/atlas-loader.js','site/rosters.js','scripts/build.py','scripts/build_rosters.py']:
  if sha(ROOT/rel)!=sha(base_root/rel) or sha(base_root/rel)!=catalog[rel]['sha256']:raise ValueError('unapproved runtime/exporter edit')
 current=load_atlas(ROOT/'data/atlas.json');base=load_atlas(base_root/'data/atlas.json');deps=validate_exact_delta(base,current,fixed);build.validate(current)
 gate=pin(gate_path,gate_sha);inputs={k:hashlib.sha256(v).hexdigest()for k,v in storage_inputs(ROOT/'data/atlas.json')};inputs['data/rosters.json']=sha(ROOT/'data/rosters.json')
 if gate['status']!='SOURCE56_INDEPENDENT_BOUNDARY_PASS' or gate['canonical_input_sha256']!=inputs:raise ValueError('independent canonical gate mismatch')
 receipt_path=pathlib.Path(receipt_path).resolve()
 if receipt_path.is_relative_to(ROOT) or receipt_path.exists():raise ValueError('new external receipt required')
 outputs={'site/people/'+p.name for p in (ROOT/'data/people').glob('*.json')}|{'site/atlas.json','site/rosters.json','site/exports/待核对名录.csv'}
 temp=receipt_path.parent/'source56-static-temp'
 if temp.exists()and any(temp.iterdir()):raise ValueError('nonempty temp')
 guard.configure([ROOT/p for p in outputs]+[receipt_path],temp);temp.mkdir(exist_ok=True);tempfile.tempdir=str(temp)
 current['build_id']=hashlib.sha256((compute_build_id(ROOT)+sha(__file__)+gate_sha).encode()).hexdigest()[:16]
 build_rosters.build_rosters(current,generate_excel=False)
 roster=json.loads((ROOT/'site/rosters.json').read_text());oldroster=json.loads((base_root/'site/rosters.json').read_text());comparison=copy.deepcopy(roster);comparison['build_id']=oldroster['build_id']
 if comparison!=oldroster:raise ValueError('Roster record payload changed beyond approved source-profile append')
 if(ROOT/'site/exports/待核对名录.csv').read_bytes()!=(base_root/'site/exports/待核对名录.csv').read_bytes():raise ValueError('Roster CSV changed')
 roster['build_id']=current['build_id'];(ROOT/'site/rosters.json').write_text(json.dumps(roster,ensure_ascii=False,indent=2)+'\n')
 current['exports']=build.department_exports(current);write_atlas(ROOT/'site/atlas.json',current)
 result={'status':'SOURCE56_STATIC_ONLY_BUILD_PASS_WORKBOOKS_PENDING','base_tree':BASE_TREE,'mapping_sha256':MAPPING_SHA,'canonical_gate_sha256':gate_sha,'build_id':current['build_id'],'generated_sha256':{r:sha(ROOT/r)for r in sorted(outputs)},'roster_payload_except_build_id':'UNCHANGED','roster_csv':'UNCHANGED','fresh_department_workbooks':'NOT_GENERATED_BY_THIS_DRIVER','future_roster_workbook':'SEPARATE_ARTIFACT_EDIT_REQUIRED_COVERAGE_A39_1318_TO1374','workbook_io':False,'full_suite':'NOT_RUN','gui':'NOT_RUN','publication':False}
 if any(temp.iterdir()):raise ValueError('temporary residue')
 temp.rmdir();receipt_path.write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__':
 p=argparse.ArgumentParser()
 for f in ['base-root','base-manifest','gate','gate-sha256','receipt']:p.add_argument('--'+f,required=True)
 a=p.parse_args();print(json.dumps(run(a.base_root,a.base_manifest,a.gate,a.gate_sha256,a.receipt)))
