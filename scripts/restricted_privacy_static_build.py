"""Build static JSON/CSV from an independently gated, exact note-only projection.
No workbook I/O or unrestricted build entrypoint. Historical builders stay pinned.
"""
import copy,hashlib,json,pathlib,sys,tempfile,argparse
import build,build_rosters
from atlas_storage import load_atlas,write_atlas,storage_inputs,compute_build_id
from restricted_recovery_build import RestrictedIOGuard
ROOT=pathlib.Path(__file__).resolve().parents[1]
BASE_MANIFEST_SHA='be480911342e510dfea9aaeb8a0ecb9aecf243d34e9b949e43820b019e3c124f'
BASE_TREE='7b4005e392e06969cfac89ee3022574c6d274f28'
FIXTURE_PINS={'hit-ai14-source-mapping.json':'2c7bd124baf36cca8f058989adc713098b864ea455d629b9f9f6786b366fff8a','source64-source-mapping.json':'8611d32a613ba5ec10afd5d3321582951e32991dfc931b35b98c08a376232f3b','source36-source-mapping.json':'78d36f97845c6dfd4814880085a06633af7a24bd47eaf504f658a66a5a6665db','source5-lzu-source-mapping.json':'76b7f457a196f83ed68e73b4029a80b4be4c852ec0d5488b0d1b00a243d30c86'}
GATE_SHA='7a97a9427b38e1bf88d22ea2de7539fc94d40cedb81fc3c262091d7d44ba808c'
sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
def pin(p,h):
 if sha(p)!=h:raise ValueError('Immutable input hash mismatch')
 return json.loads(pathlib.Path(p).read_text())
def validate_exact_projection(base,current,fixed):
 if len(base['people'])!=1318 or len(current['people'])!=1318 or len(fixed)!=119:raise ValueError('exact1318 and119 projection required')
 if current['people']!=base['people'][:1199]+fixed:raise ValueError('nonapproved profile projection')
 inverse=copy.copy(current);inverse['people']=base['people']
 if inverse!=base:raise ValueError('unrelated atlas root changed')
 if len(current['pending_people'])!=84:raise ValueError('pending records changed')
 for old,new in zip(base['people'],current['people']):
  for k in ['education','appointments','teaching','publications','mentors','professional_research_advisors','unverified_professional_guidance','official_url','school_id','department_id','campus','campus_ids']:
   if old.get(k)!=new.get(k):raise ValueError('academic fact changed '+k)
def run(base_root,base_manifest,gate_path,receipt_path):
 guard=RestrictedIOGuard(ROOT);sys.addaudithook(guard)
 base_root=pathlib.Path(base_root).resolve();manifest=pin(base_manifest,BASE_MANIFEST_SHA)
 if manifest['tree_sha']!=BASE_TREE:raise ValueError('wrong baseline tree')
 catalog={e['path']:e for e in manifest['files']}
 for name,b in storage_inputs(base_root/'data/atlas.json'):
  if hashlib.sha256(b).hexdigest()!=catalog['data/'+name]['sha256']:raise ValueError('baseline canonical changed')
 for rel in ['data/rosters.json','site/app.js','site/model.js','site/atlas-loader.js','site/rosters.js','scripts/build.py','scripts/build_rosters.py']:
  if sha(base_root/rel)!=catalog[rel]['sha256']:raise ValueError('baseline changed')
  if rel!='data/rosters.json'and sha(ROOT/rel)!=sha(base_root/rel):raise ValueError('runtime or exporter changed')
 fixed=[]
 for f,h in FIXTURE_PINS.items():fixed+=pin(ROOT/'tests/fixtures'/f,h)['people']
 current=load_atlas(ROOT/'data/atlas.json');base=load_atlas(base_root/'data/atlas.json');validate_exact_projection(base,current,fixed);build.validate(current)
 gate=pin(gate_path,GATE_SHA);inputs={k:hashlib.sha256(v).hexdigest()for k,v in storage_inputs(ROOT/'data/atlas.json')};inputs['data/rosters.json']=sha(ROOT/'data/rosters.json')
 if gate['status']!='PENDING119_PRIVACY_INDEPENDENT_BOUNDARY_PASS' or gate['canonical_input_sha256']!=inputs:raise ValueError('independent final canonical gate mismatch')
 receipt_path=pathlib.Path(receipt_path).resolve()
 if receipt_path.is_relative_to(ROOT)or receipt_path.exists():raise ValueError('new external receipt required')
 outputs={'site/people/'+p.name for p in(ROOT/'data/people').glob('*.json')}|{'site/atlas.json','site/rosters.json','site/exports/待核对名录.csv'}
 temp=receipt_path.parent/'privacy-static-temp'
 if temp.exists()and any(temp.iterdir()):raise ValueError('nonempty temp')
 guard.configure([ROOT/p for p in outputs]+[receipt_path],temp);temp.mkdir(exist_ok=True);tempfile.tempdir=str(temp)
 current['build_id']=hashlib.sha256((compute_build_id(ROOT)+sha(__file__)+GATE_SHA).encode()).hexdigest()[:16]
 build_rosters.build_rosters(current,generate_excel=False)
 roster=json.loads((ROOT/'site/rosters.json').read_text());roster['build_id']=current['build_id'];(ROOT/'site/rosters.json').write_text(json.dumps(roster,ensure_ascii=False,indent=2)+'\n')
 current['exports']=build.department_exports(current);write_atlas(ROOT/'site/atlas.json',current)
 result={'status':'PRIVACY_STATIC_ONLY_BUILD_PASS_WORKBOOKS_PENDING','base_tree':BASE_TREE,'canonical_gate_sha256':GATE_SHA,'build_id':current['build_id'],'generated_sha256':{r:sha(ROOT/r)for r in sorted(outputs)},'roster_note_projection':'INDEPENDENTLY_GATED_NOT_BYTE_IDENTICAL','workbook_io':False,'full_suite':'NOT_RUN','gui':'NOT_RUN','publication':False}
 if any(temp.iterdir()):raise ValueError('temporary residue')
 temp.rmdir();receipt_path.write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__':
 p=argparse.ArgumentParser()
 for f in ['base-root','base-manifest','gate','receipt']:p.add_argument('--'+f,required=True)
 a=p.parse_args();print(json.dumps(run(a.base_root,a.base_manifest,a.gate,a.receipt)))
