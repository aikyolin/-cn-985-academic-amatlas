"""Validate canonical data and derive static data + departmental Excel workbooks."""
import json,pathlib,sys,hashlib,re
from urllib.parse import urlparse
from openpyxl import Workbook
from openpyxl.styles import Font,PatternFill,Alignment
ROOT=pathlib.Path(__file__).resolve().parents[1]
def valid_url(v):return isinstance(v,str) and urlparse(v).scheme in ('http','https') and bool(urlparse(v).netloc)
def mentor_official_url(mentor):
 # Explicit false flags veto shortcuts without weakening verified employment evidence.
 if not mentor or mentor.get('employment_status')!='active_officially_listed' or mentor.get('quick_link_eligible') is False or mentor.get('navigation_verified') is False:return ''
 url=mentor.get('official_url')
 try:
  if not valid_url(url):return ''
  parsed=urlparse(url)
  if not parsed.hostname or any(c.isspace() for c in parsed.hostname):return ''
  parsed.port  # Access validates the numeric port and range, like the browser URL parser.
  return url
 except ValueError:return ''
def mentor_navigation_notice(mentor):
 if not mentor or mentor.get('employment_status')!='active_officially_listed' or mentor_official_url(mentor):return ''
 reason=mentor.get('profile_navigation_unavailable_reason')
 return '任职已核实；'+((reason.strip() if isinstance(reason,str) else '') or '导师主页访问未核实，暂不提供快捷链接。')

def safe_id(value):return isinstance(value,str) and bool(re.fullmatch(r'[A-Za-z0-9_-]+',value))
def school_index(d):
 schools={row['id']:row for row in d['institutions']}
 assert len(schools)==len(d['institutions']), 'Duplicate school ID'
 assert all(safe_id(sid) for sid in schools), 'Unsafe school ID'
 assert all(valid_url(row.get('official_url')) and row.get('official_name') for row in schools.values()), 'School identity needs a name and official URL'
 return schools

def validate_school_scope(d):
 schools=school_index(d)
 campuses={c['id']:c for c in d['campuses']}
 assert len(campuses)==len(d['campuses']), 'Duplicate campus ID'
 orgs={o['id']:o for o in d['org_units']}
 assert len(orgs)==len(d['org_units']), 'Duplicate organization ID'
 assert all(safe_id(oid) for oid in orgs), 'Unsafe organization ID'
 legacy={'harbin','weihai','shenzhen'}
 for c in campuses.values():
  assert c.get('school_id') in schools, 'Unknown campus school'
  assert safe_id(c['id']), 'Unsafe campus ID'
  assert (c['school_id']=='hit' and c['id'] in legacy) or c['id'].startswith(c['school_id']+'-'), 'New campus IDs must be school-prefixed'
 for key in ['org_units','people','pending_people']:
  for row in d.get(key,[]):
   sid=row.get('school_id');assert sid in schools, 'Unknown record school'
   assert isinstance(row.get('campus_ids'),list), 'Campus associations must be explicit; empty is allowed'
   for cid in row['campus_ids']:
    assert cid in campuses and campuses[cid]['school_id']==sid, 'Cross-school or unknown campus reference'
   if key=='org_units':
    assert row.get('name') and row.get('type') and valid_url(row.get('source_url')), 'Organization needs a name, type and source URL'
    parent=row.get('parent_id')
    if parent in orgs:assert orgs[parent]['school_id']==sid, 'Cross-school organization parent'
    elif parent:
     # Preserve historical HIT parent aliases without creating synthetic org nodes.
     legacy_parent=sid=='hit' and parent in {'hit-'+c for c in legacy}
     assert parent==sid or (parent in campuses and campuses[parent]['school_id']==sid) or legacy_parent, 'Unknown or cross-school organization parent'
   else:
    oid=row.get('department_id') or row.get('organization_id')
    assert oid in orgs and orgs[oid]['school_id']==sid, 'Cross-school or unknown person department'
 return True

def validate(d):
 validate_school_scope(d)
 pending=d.get('pending_people',[])
 assert all(p.get('profile_status') in ('roster_identity_pending','profile_details_pending') and not p.get('education') and not p.get('mentors') and not p.get('publications') for p in pending),'Pending identities must stay outside confirmed collections'
 assert not ({p['person_id'] for p in pending}&{p['person_id'] for p in d['people']}),'Pending identity duplicated as detailed profile'
 ids=[u['id'] for u in d['org_units']]; assert len(ids)==len(set(ids)), 'Duplicate organization ID'
 people=d['people']; assert len({p['person_id'] for p in people})==len(people),'Duplicate person ID'
 for p in people:
  assert p['department_id'] in ids,'Unknown department'
  assert valid_url(p['official_url']),'Unsafe profile URL'
  for collection in ['education','mentors','appointments','publications','committee_members']:
   for row in p.get(collection,[]):
    assert valid_url(row.get('source_url')),'Missing evidence URL'
  for e in p['education']:
   assert e['institution_985'] in ('yes','no','unknown')
   assert e['region'] in ('mainland','hmt','overseas','unknown')
   assert 'event_kind' in e and e.get('degree_awarded') in (True,False,None),'Missing event/award semantics'
   assert e.get('degree_awarded') is not True or e['event_kind']=='degree','Only degree events may confirm an award'
  event_ids=[e['event_id'] for e in p['education'] if e.get('event_id')]
  assert len(event_ids)==len(set(event_ids)),'Duplicate education event ID'
  for c in p.get('research_collaborators',[]):
   assert c.get('include_in_mentorship_graph') is False,'Collaborator must not be promoted to mentorship'
   if c.get('relationship_kind')=='visiting_research_collaborator':
    assert c.get('education_event_id') in event_ids,'Collaborator references unknown education event'
    event=next(e for e in p['education'] if e.get('event_id')==c['education_event_id'])
    assert event.get('degree_awarded') is False,'Visiting collaborator must bind a non-award event'
   if c.get('appointment_event_id'):
    assert any(a.get('event_id')==c['appointment_event_id'] for a in p['appointments']),'Collaborator references unknown appointment'
   assert not(c.get('education_event_id') and c.get('appointment_event_id')),'Collaborator cannot bind two event kinds'
   assert valid_url(c.get('source_url')),'Collaborator requires evidence'

  for c in p.get('project_guidance',[]):
   assert c.get('include_in_mentorship_graph') is False,'Project guidance must stay outside the mentorship graph'
   assert c.get('include_in_verified_mentor_count') is False,'Project guidance must stay outside mentor counts'
   assert c.get('education_event_id') is None,'Project guidance must not imply a degree-event binding'
   assert c.get('name') and valid_url(c.get('source_url')),'Project guidance requires a name and direct evidence URL'
   source_ids={row.get('id') for row in p['sources']}
   for key in ['source_id','profile_source_id']:
    assert not c.get(key) or c[key] in source_ids,'Project guidance references unknown source'

  for m in p['mentors']:
   assert m.get('type')!='research_project_advisor' and m.get('relationship_kind')!='research_project_advisor','Project guidance must stay separate from mentors'
   assert not m.get('education_event_id') or m['education_event_id'] in event_ids,'Mentor references unknown education event'
   if m['employment_status']=='active_officially_listed':
    assert valid_url(m.get('profile_source_url')),'Active mentor needs public employment evidence'
    unavailable = (m.get('official_url') is None and m.get('quick_link_eligible') is False and m.get('navigation_verified') is False and isinstance(m.get('profile_navigation_unavailable_reason'), str) and bool(m['profile_navigation_unavailable_reason'].strip()))
    assert valid_url(m.get('official_url')) or unavailable,'Active mentor needs homepage or explicit verified navigation limitation'
 for u in d['org_units']:
  seen=set();cur=u
  while cur['parent_id'] in ids:
   assert cur['id'] not in seen,'Organization cycle';seen.add(cur['id']);cur=next(v for v in d['org_units'] if v['id']==cur['parent_id'])
 return True
def clean(v):
 if isinstance(v,(list,dict)):v=json.dumps(v,ensure_ascii=False)
 if v is None:return ''
 if isinstance(v,str) and v and v[:1] in '=+-@\t\r':return "'"+v
 return v
def sheet(wb,name,rows):
 ws=wb.create_sheet(name)
 for row in rows:ws.append([clean(v) for v in row])
 ws.freeze_panes='A2';ws.auto_filter.ref=ws.dimensions
 for cell in ws[1]:cell.fill=PatternFill('solid',fgColor='102A42');cell.font=Font(color='FFFFFF',bold=True)
 for row in ws.iter_rows(min_row=2):
  for cell in row:
   cell.alignment=Alignment(vertical='top',wrap_text=True)
   if valid_url(cell.value):cell.hyperlink=cell.value;cell.font=Font(color='078B92',underline='single')
 for col in ws.columns:ws.column_dimensions[col[0].column_letter].width=min(65,max(16,max(len(str(c.value or '')) for c in col)*1.4))
 return ws
def source_evidence_text(source):
 label=source.get('evidence_label') or source.get('evidence_status_label')
 status=source.get('evidence_status')
 return '；'.join(str(v) for v in [label,status] if v) if label and label!=status else status or label

def publication_value(publication,key):
 raw=publication.get(key);label=publication.get(key+'_label') if key in ('type','link_status') else None
 return '；'.join(str(v) for v in [label,raw] if v) if label and label!=raw else raw if raw is not None else label

def department_tables(people,updated_at,institutions=None):
 schools={p.get("school_id") for p in people}
 assert len(schools)<=1 and None not in schools, "Department export cannot mix schools or omit school IDs"
 departments={p.get("department_id") for p in people}
 assert len(departments)<=1 and all(safe_id(dept) for dept in departments), "Department export cannot mix departments or omit department IDs; group people by department_id"
 school_id=next(iter(schools),"")
 names={s["id"]:s["official_name"] for s in (institutions or [])}
 school_name=names.get(school_id,school_id)
 tables=[('总览',[['姓名','校区','院系','官方主页','核对日期','缺项与冲突','范围','主页可用性','替代官方职业报道（非个人主页）'],*[[p['name'],p.get('campus') or '校区未标注',p['department'],'' if p.get('official_profile_availability')=='unavailable' or p.get('official_profile_navigation_eligible') is False else p['official_url'],updated_at,'；'.join(p['unknowns']),'分批核实资料，不是完整名录','个人主页当前不可用' if p.get('official_profile_availability')=='unavailable' or p.get('official_profile_navigation_eligible') is False else '公开个人页（时效以核对日为准）','；'.join(str(s.get('title','官方职业报道'))+'：'+str(s.get('url','')) for s in p.get('alternative_professional_sources',[]))] for p in people]])]
 fields=['event_kind','degree','institution','start','end','field','country','source_region','continent','institution_985','degree_awarded','degree_awarded_date','degree_award_source_url','note','geography_basis','source_url']
 rows=[['姓名','事件类型','阶段/职位','机构','开始','结束','专业','国家','地区','洲','历史985分类','确证授位','授位日期','授位来源','备注及冲突','地域口径','来源']]
 for p in people:
  events=p['education']+[dict(a,event_kind='employment',degree=a.get('title')) for a in p['appointments']]
  rows.extend([[p['name'],*[str(e.get(k) or '')+'（层次暂对应，未核实）' if k=='degree' and str(e.get('field_status',{}).get('degree','')).startswith('provisional_') else e.get(k) for k in fields]] for e in events])
  for c in p.get('research_collaborators',[]):
   event_id=c.get('education_event_id') or c.get('appointment_event_id')
   events=p['education'] if c.get('education_event_id') else p['appointments']
   e=next((e for e in events if event_id and e.get('event_id')==event_id), {})
   row=dict(event_kind=c.get('relationship_kind','research_collaborator'),degree=c.get('type'),institution=c.get('institution'),start=e.get('start'),end=e.get('end'),source_url=c.get('source_url'),note='；'.join(str(v) for v in [c.get('name'),c.get('description'),c.get('employment_status_note'),c.get('note') or c.get('evidence_note'),'非导师认定，不计师承',c.get('profile_source_url')] if v))
   rows.append([p['name'],*[row.get(k) for k in fields]])
  for c in p.get('project_guidance',[]):
   # Project context is not a degree event. Never join null/missing education IDs.
   row=dict(event_kind='project_guidance',degree='项目指导（非学位师承）',institution=c.get('institution'),start=c.get('start'),end=c.get('end'),degree_awarded=False,source_url=c.get('source_url'),note='；'.join(str(v) for v in [c.get('name'),c.get('type_label') or c.get('type'),c.get('project_name'),c.get('education_stage'),c.get('relationship_scope'),c.get('description'),c.get('employment_status_note'),c.get('note'),c.get('scope_label'),'非学位师承，不计入导师统计或师承关系图',c.get('profile_source_url')] if v))
   rows.append([p['name'],*[row.get(k) for k in fields]])
 tables.append(('经历',rows))
 mentor_fields=['name','type','education_stage','description','employment_status','employment_status_note','official_url','source_url','profile_source_url']
 rows=[['姓名','导师姓名','关系类型','阶段','简介','在职状态','状态说明','已核在职主页','关系来源','任职来源']]
 for p in people:
  mentors=[dict(m,type=m.get('type_label') or m.get('type'),official_url=mentor_official_url(m),employment_status_note='；'.join(v for v in [m.get('employment_status_note'),mentor_navigation_notice(m)] if v) if mentor_navigation_notice(m) else m.get('employment_status_note')) for m in p['mentors']]+[dict(c,type=c.get('label','博士指导委员会成员（非师承）'),official_url='') for c in p.get('committee_members',[])]
  rows.extend([[p['name'],*[m.get(k) for k in mentor_fields]] for m in mentors])
 tables.append(('导师',rows))
 for label,key,fields,headers in [('论文','publications',['title','year','doi','url','type','source_url','identity_evidence','link_status','note'],['标题','年份','DOI','链接','类型','收录来源','作者归属依据','链接核验范围','备注']),('来源','sources',['id','url','evidence_status','retrieved_at'],['来源ID','链接','核验方式','查阅日期'])]:
  rows=[['姓名',*headers],*[[p['name'],*[source_evidence_text(r) if k=='evidence_status' else publication_value(r,k) if key=='publications' else r.get(k) for k in fields]] for p in people for r in p[key]]]
  if key=='sources':
   for p in people:
    seen={row.get('url') for row in p['sources']}
    for e in p['education']:
     url=e.get('classification_source')
     if e.get('institution_985') in ('yes','no') and valid_url(url) and url not in seen:
      rows.append([p['name'],'institution-classification-'+str(len(seen)),url,'历史985院校分类参考；非个人授位或就读当年建设身份的证明',updated_at]);seen.add(url)
  tables.append((label,rows))
 for _,rows in tables:
  rows[0].extend(['所属学校ID','所属学校'])
  for row in rows[1:]:row.extend([school_id,school_name])
 return tables

def department_exports(d):
 validate_school_scope(d)
 units={u['id']:u for u in d['org_units']}
 names={s['id']:s['official_name'] for s in d['institutions']}
 result=[]
 for dept in sorted({p['department_id'] for p in d['people']}):
  school_id=units[dept]['school_id']
  people=[p for p in d['people'] if p['department_id']==dept and p['school_id']==school_id]
  result.append({'department_id':dept,'school_id':school_id,'school_name':names[school_id],'path':'exports/'+dept+'.xlsx','people_count':len(people)})
 return result

def build(generate_excel=True):
 d=json.loads((ROOT/'data/atlas.json').read_text());validate(d);exports=department_exports(d)
 d['build_id']=hashlib.sha256((ROOT/'data/atlas.json').read_bytes()+(ROOT/'data/rosters.json').read_bytes()+pathlib.Path(__file__).read_bytes()+(ROOT/'scripts/build_rosters.py').read_bytes()).hexdigest()[:16]
 out=ROOT/'site/exports';out.mkdir(exist_ok=True)
 for export in exports:
  dept=export['department_id'];people=[p for p in d['people'] if p['department_id']==dept and p['school_id']==export['school_id']];path=out/(dept+'.xlsx')
  if generate_excel:
   wb=Workbook();wb.remove(wb.active)
   for name,rows in department_tables(people,d['updated_at'],d['institutions']):sheet(wb,name,rows)
   wb.save(path)
 from build_rosters import build_rosters
 build_rosters(d,generate_excel=generate_excel)
 roster_path=ROOT/'site/rosters.json';roster_snapshot=json.loads(roster_path.read_text());roster_snapshot['build_id']=d['build_id'];roster_path.write_text(json.dumps(roster_snapshot,ensure_ascii=False,indent=2)+'\n')
 d['exports']=exports;(ROOT/'site/atlas.json').write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n');print(f'Validated {len(d["people"])} detailed profiles; prepared {len(exports)} department exports and website snapshot')
if __name__=='__main__':
 import argparse
 parser=argparse.ArgumentParser();parser.add_argument('--data-only',action='store_true');args=parser.parse_args();build(generate_excel=not args.data_only)
