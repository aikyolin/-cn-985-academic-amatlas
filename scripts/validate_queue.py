"""Validate public task checkpoints, dependencies and reviewed completion evidence."""
import argparse,json,pathlib
from jsonschema import Draft202012Validator,FormatChecker
ROOT=pathlib.Path(__file__).resolve().parents[1]
def validate_queue(data,root=ROOT,check_artifacts=False):
 schema=json.loads((ROOT/'schema/work-queue.schema.json').read_text())
 Draft202012Validator(schema,format_checker=FormatChecker()).validate(data)
 tasks=data['tasks'];ids=[t['task_id'] for t in tasks]
 if len(ids)!=len(set(ids)):raise ValueError('Duplicate task ID')
 by_id={t['task_id']:t for t in tasks};warnings=[]
 for t in tasks:
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
