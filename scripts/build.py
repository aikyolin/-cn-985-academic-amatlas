"""Validate canonical data and derive static data + departmental Excel workbooks."""
import json,pathlib,sys,hashlib
from urllib.parse import urlparse
from openpyxl import Workbook
from openpyxl.styles import Font,PatternFill,Alignment
ROOT=pathlib.Path(__file__).resolve().parents[1]
def valid_url(v):return isinstance(v,str) and urlparse(v).scheme in ('http','https') and bool(urlparse(v).netloc)
def validate(d):
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

  for m in p['mentors']:
   assert not m.get('education_event_id') or m['education_event_id'] in event_ids,'Mentor references unknown education event'
   if m['employment_status']=='active_officially_listed':
    assert valid_url(m.get('official_url')) and valid_url(m.get('profile_source_url')),'Active mentor needs homepage evidence'
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
def department_tables(people,updated_at):
 tables=[('总览',[['姓名','校区','院系','官方主页','核对日期','缺项与冲突','范围','主页可用性','替代官方职业报道（非个人主页）'],*[[p['name'],p['campus'],p['department'],'' if p.get('official_profile_availability')=='unavailable' or p.get('official_profile_navigation_eligible') is False else p['official_url'],updated_at,'；'.join(p['unknowns']),'分批核实资料，不是完整名录','个人主页当前不可用' if p.get('official_profile_availability')=='unavailable' or p.get('official_profile_navigation_eligible') is False else '公开个人页（时效以核对日为准）','；'.join(str(s.get('title','官方职业报道'))+'：'+str(s.get('url','')) for s in p.get('alternative_professional_sources',[]))] for p in people]])]
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
 tables.append(('经历',rows))
 mentor_fields=['name','type','education_stage','description','employment_status','employment_status_note','official_url','source_url','profile_source_url']
 rows=[['姓名','导师姓名','关系类型','阶段','简介','在职状态','状态说明','已核在职主页','关系来源','任职来源']]
 for p in people:
  mentors=[dict(m,official_url=m.get('official_url') if m.get('employment_status')=='active_officially_listed' else '') for m in p['mentors']]+[dict(c,type=c.get('label','博士指导委员会成员（非师承）'),official_url='') for c in p.get('committee_members',[])]
  rows.extend([[p['name'],*[m.get(k) for k in mentor_fields]] for m in mentors])
 tables.append(('导师',rows))
 for label,key,fields,headers in [('论文','publications',['title','year','doi','url','type','source_url','identity_evidence','link_status','note'],['标题','年份','DOI','链接','类型','收录来源','作者归属依据','链接核验范围','备注']),('来源','sources',['id','url','evidence_status','retrieved_at'],['来源ID','链接','核验方式','查阅日期'])]:
  rows=[['姓名',*headers],*[[p['name'],*[r.get(k) for k in fields]] for p in people for r in p[key]]]
  if key=='sources':
   for p in people:
    seen={row.get('url') for row in p['sources']}
    for e in p['education']:
     url=e.get('classification_source')
     if e.get('institution_985') in ('yes','no') and valid_url(url) and url not in seen:
      rows.append([p['name'],'institution-classification-'+str(len(seen)),url,'历史985院校分类参考；非个人授位或就读当年建设身份的证明',updated_at]);seen.add(url)
  tables.append((label,rows))
 return tables

def build(generate_excel=True):
 d=json.loads((ROOT/'data/atlas.json').read_text());validate(d);exports=[]
 d['build_id']=hashlib.sha256((ROOT/'data/atlas.json').read_bytes()+(ROOT/'data/rosters.json').read_bytes()+pathlib.Path(__file__).read_bytes()).hexdigest()[:16]
 out=ROOT/'site/exports';out.mkdir(exist_ok=True)
 for dept in sorted({p['department_id'] for p in d['people']}):
  people=[p for p in d['people'] if p['department_id']==dept];path=out/(dept+'.xlsx')
  if generate_excel:
   wb=Workbook();wb.remove(wb.active)
   for name,rows in department_tables(people,d['updated_at']):sheet(wb,name,rows)
   wb.save(path)
  exports.append({'department_id':dept,'path':'exports/'+path.name,'people_count':len(people)})
 from build_rosters import build_rosters
 build_rosters(d,generate_excel=generate_excel)
 roster_path=ROOT/'site/rosters.json';roster_snapshot=json.loads(roster_path.read_text());roster_snapshot['build_id']=d['build_id'];roster_path.write_text(json.dumps(roster_snapshot,ensure_ascii=False,indent=2)+'\n')
 d['exports']=exports;(ROOT/'site/atlas.json').write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n');print(f'Validated {len(d["people"])} detailed profiles; prepared {len(exports)} department exports and website snapshot')
if __name__=='__main__':
 import argparse
 parser=argparse.ArgumentParser();parser.add_argument('--data-only',action='store_true');args=parser.parse_args();build(generate_excel=not args.data_only)
