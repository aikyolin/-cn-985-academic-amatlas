"""Validate public task checkpoints, dependencies and reviewed completion evidence."""
import argparse,json,pathlib,datetime,re
from jsonschema import Draft202012Validator,FormatChecker
ROOT=pathlib.Path(__file__).resolve().parents[1]
FORMATS=FormatChecker()
@FORMATS.checks('date-time', raises=ValueError)
def explicit_datetime(value):
 # jsonschema's optional RFC3339 dependency is not guaranteed to be installed.
 # Require an actual, timezone-qualified timestamp rather than silently accepting any text.
 if not isinstance(value,str):return True
 if not re.fullmatch(r'\d{4}-\d{2}-\d{2}[Tt]\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:[Zz]|[+-](?:[01]\d|2[0-3]):[0-5]\d)',value):return False
 stamp=datetime.datetime.fromisoformat(value.upper().replace('Z','+00:00'))
 return stamp.tzinfo is not None

def validate_queue(data,root=ROOT,check_artifacts=False):
 root=pathlib.Path(root)
 schema=json.loads((ROOT/'schema/work-queue.schema.json').read_text())
 Draft202012Validator(schema,format_checker=FORMATS).validate(data)
 atlas=json.loads((root/'data/atlas.json').read_text())
 schools={s['id'] for s in atlas['institutions']}
 organizations={o['id']:o for o in atlas['org_units']}
 campuses={c['id']:c for c in atlas['campuses']}
 active=data['scope'].get('active_institutions')
 if active is not None and not set(active)<=schools:raise ValueError('Unknown active institution')
 tasks=data['tasks'];ids=[t['task_id'] for t in tasks]
 if len(ids)!=len(set(ids)):raise ValueError('Duplicate task ID')
 by_id={t['task_id']:t for t in tasks};warnings=[]
 for t in tasks:
  sid=t['institution_id'];oid=t['organization_id']
  if sid not in schools:raise ValueError('Unknown task institution: '+sid)
  if active is not None and sid not in active:raise ValueError('Task institution outside active scope: '+sid)
  if oid is not None and (oid not in organizations or organizations[oid]['school_id']!=sid):raise ValueError('Unknown or cross-school task organization: '+oid)
  for original in t['campus_ids']:
   # These three aliases remain valid only for historical HIT queue records.
   cid=original[4:] if sid=='hit' and original in {'hit-harbin','hit-weihai','hit-shenzhen'} else original
   if cid not in campuses or campuses[cid]['school_id']!=sid:raise ValueError('Unknown or cross-school task campus: '+original)
  for dep in t['depends_on']:
   if dep not in by_id:raise ValueError('Unknown dependency: '+dep)
   if t['status']=='done' and by_id[dep]['status']!='done':raise ValueError('Done task has unfinished dependency')
  for artifact in t['artifact_paths']:
   target=(root/artifact).resolve()
   if not target.is_relative_to(root.resolve()):raise ValueError('Artifact outside repository')
   if check_artifacts and t['status']=='done' and not target.is_file():raise ValueError('Completion artifact missing: '+artifact)
 def visit(task_id,stack,done):
  if task_id in stack:raise ValueError('Dependency cycle')
  if task_id in done:return
  for dep in by_id[task_id]['depends_on']:visit(dep,stack|{task_id},done)
  done.add(task_id)
 seen=set()
 for task_id in ids:visit(task_id,set(),seen)
 return warnings
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('queue');p.add_argument('--check-artifacts',action='store_true');a=p.parse_args()
 data=json.loads(pathlib.Path(a.queue).read_text());warnings=validate_queue(data,check_artifacts=a.check_artifacts)
 print(f'Validated {len(data["tasks"])} scoped tasks; {len(warnings)} warnings')
 for w in warnings:print(w)
