"""Keep unverified directory records separate from researched personal profiles."""
import json,csv
from urllib.parse import urlparse
from openpyxl import Workbook
from build import ROOT,sheet,clean,valid_url

def homepage_key(url):
 u=urlparse(url or '');return (u.hostname or '',u.path.rstrip('/'))
def build_rosters(d):
 r=json.loads((ROOT/'data/rosters.json').read_text());entries=r['entries']
 assert len({e['id'] for e in entries})==len(entries),'Duplicate roster record ID'
 for e in entries:
  assert e['profile_identity_verified'] is False,'Directory-only records cannot assert profile verification'
  assert valid_url(e['roster_source_url'])
  e['candidate_person_ids']=[p['person_id'] for p in d['people'] if e['name']==p['name'] and e['organization_id']==p['department_id'] and e['official_profile_url'] and homepage_key(e['official_profile_url'])==homepage_key(p['official_url'])]
  e['candidate_match_status']='pending_identity_review' if e['candidate_person_ids'] else 'not_linked'
 cols=['id','name','campus_id','organization_id','category','listed_role','official_profile_url','roster_source_url','accessed_on','verification_status','profile_identity_verified','candidate_person_ids','notes']
 headers=['记录ID','姓名','校区','组织ID','原始分类','官网列示职务','原名录主页链接（身份待核）','名录来源','查阅日期','核验状态','主页身份已核实','独立样板候选（未合并）','备注']
 rows=[headers,*[[e.get(k) for k in cols] for e in entries]]
 out=ROOT/'site/exports';out.mkdir(exist_ok=True)
 with (out/'待核对名录.csv').open('w',encoding='utf-8-sig',newline='') as f:csv.writer(f).writerows([[clean(v) for v in row] for row in rows])
 wb=Workbook();wb.remove(wb.active);sheet(wb,'待核对名录',rows)
 sheet(wb,'覆盖说明',[['范围与限制'],[r['scope']],*[[s] for s in r['limitations']],['不是已核实在职人数；不把技术人员统称为教师；不与6份详细样板自动合并。']])
 sheet(wb,'分类覆盖',[['组织','分类','可见记录数','来源','查阅日期'],*[[c['organization_id'],c['category'],c['visible_name_count'],c['url'],c['accessed_on']] for c in r['coverage']]])
 sheet(wb,'冲突记录',[['类型','详情'],*[[c['type'],c] for c in r['conflicts']]])
 wb.save(out/'待核对名录.xlsx');(ROOT/'site/rosters.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n');print(f'Built {len(entries)} separate roster records, XLSX and CSV')
