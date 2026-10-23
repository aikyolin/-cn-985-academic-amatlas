"""Validate canonical data and derive static data + departmental Excel workbooks."""
import json,pathlib,sys
from urllib.parse import urlparse
from openpyxl import Workbook
from openpyxl.styles import Font,PatternFill,Alignment
ROOT=pathlib.Path(__file__).resolve().parents[1]
def valid_url(v):return isinstance(v,str) and urlparse(v).scheme in ('http','https') and bool(urlparse(v).netloc)
def validate(d):
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
  for m in p['mentors']:
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
 tables=[('总览',[['姓名','校区','院系','官方主页','核对日期','缺项与冲突','范围'],*[[p['name'],p['campus'],p['department'],p['official_url'],updated_at,'；'.join(p['unknowns']),'分批核实资料，不是完整名录'] for p in people]])]
 fields=['event_kind','degree','institution','start','end','field','country','source_region','continent','institution_985','degree_awarded','degree_awarded_date','degree_award_source_url','note','geography_basis','source_url']
 rows=[['姓名','事件类型','阶段/职位','机构','开始','结束','专业','国家','地区','洲','历史985分类','确证授位','授位日期','授位来源','备注及冲突','地域口径','来源']]
 for p in people:
  events=p['education']+[dict(a,event_kind='employment',degree=a.get('title')) for a in p['appointments']]
  rows.extend([[p['name'],*[e.get(k) for k in fields]] for e in events])
 tables.append(('经历',rows))
 mentor_fields=['name','type','education_stage','description','employment_status','employment_status_note','official_url','source_url','profile_source_url']
 rows=[['姓名','导师姓名','关系类型','阶段','简介','在职状态','状态说明','已核在职主页','关系来源','任职来源']]
 for p in people:
  mentors=[dict(m,official_url=m.get('official_url') if m.get('employment_status')=='active_officially_listed' else '') for m in p['mentors']]+[dict(c,type=c.get('label','博士指导委员会成员（非师承）'),official_url='') for c in p.get('committee_members',[])]
  rows.extend([[p['name'],*[m.get(k) for k in mentor_fields]] for m in mentors])
 tables.append(('导师',rows))
 for label,key,fields,headers in [('论文','publications',['title','year','doi','url','type','source_url','identity_evidence','link_status','note'],['标题','年份','DOI','链接','类型','收录来源','作者归属依据','链接核验范围','备注']),('来源','sources',['id','url','evidence_status','retrieved_at'],['来源ID','链接','核验方式','查阅日期'])]:
  tables.append((label,[['姓名',*headers],*[[p['name'],*[r.get(k) for k in fields]] for p in people for r in p[key]]]))
 return tables

def build(generate_excel=True):
 d=json.loads((ROOT/'data/atlas.json').read_text());validate(d);exports=[]
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
 d['exports']=exports;(ROOT/'site/atlas.json').write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n');print(f'Validated {len(d["people"])} detailed profiles; prepared {len(exports)} department exports and website snapshot')
if __name__=='__main__':
 import argparse
 parser=argparse.ArgumentParser();parser.add_argument('--data-only',action='store_true');args=parser.parse_args();build(generate_excel=not args.data_only)
