"""Targeted recovery checks, not the old full suite.

RESTRICTED_BUILD_RECEIPT is REQUIRED and must point to an external build receipt.
Only 98 fixed department workbooks are opened. Inherited bytes are never read.
"""
import hashlib
import json
import os
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from atlas_storage import load_atlas
import build
from openpyxl import load_workbook

FIXTURE_PINS = {
    'new-recovery123-source-attributed-mapping.json': '0d7362f37e2c883cc1e442f3fd6e2278bddba9e6090aeda3544135e6947b1418',
    'new-recovery123-public-conservation-pins.json': '991d893162b8a4c7b61be1411082eb14b989507c6a1b0b5b35ac465434f24be5',
}

def object_sha(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()).hexdigest()

def fixed(name):
    raw = (ROOT / 'tests/fixtures' / name).read_bytes()
    if hashlib.sha256(raw).hexdigest() != FIXTURE_PINS[name]:
        raise AssertionError('fixed public fixture changed: ' + name)
    return json.loads(raw)

class NewRecovery123TargetedTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        receipt = os.environ.get('RESTRICTED_BUILD_RECEIPT')
        if not receipt:
            raise RuntimeError('RESTRICTED_BUILD_RECEIPT is REQUIRED; no skip/pass without restricted build evidence')
        receipt_path = Path(receipt).resolve()
        if receipt_path.is_relative_to(ROOT):
            raise RuntimeError('RESTRICTED_BUILD_RECEIPT must be outside the publication root')
        cls.receipt = json.loads(receipt_path.read_text())
        cls.fixture = fixed('new-recovery123-source-attributed-mapping.json')
        cls.pins = fixed('new-recovery123-public-conservation-pins.json')
        cls.actual = load_atlas(ROOT / 'data/atlas.json')
        cls.site = load_atlas(ROOT / 'site/atlas.json')
        cls.new = {p['person_id']: p for p in cls.fixture['people']}
        cls.allowed_departments = {d['department_id']: d for d in cls.pins['departments']}
        if len(cls.allowed_departments) != 98 or any(d['school_id'] == 'xmu' for d in cls.allowed_departments.values()):
            raise AssertionError('restricted fixed department scope changed')

    def test_01_old_1026_whole_objects_order_root_and_199_batches_conserved(self):
        self.assertEqual(len(self.actual['people']), 1149)
        for p, pin in zip(self.actual['people'][:1026], self.pins['old_people'], strict=True):
            self.assertEqual(p['person_id'], pin['person_id'])
            self.assertEqual(object_sha(p), pin['sha256'], p['person_id'])
        self.assertEqual(sorted(self.actual), self.pins['canonical_root_keys'])
        for key, sha in self.pins['old_root_field_sha256'].items():
            self.assertEqual(object_sha(self.actual[key]), sha, key)
        n = self.pins['old_org_units_count']
        self.assertEqual(object_sha(self.actual['org_units'][:n]), self.pins['old_org_units_sha256'])
        self.assertEqual(object_sha(self.actual['profile_batches'][:199]), self.pins['old_profile_batches_sha256'])
        self.assertEqual(self.actual['org_units'][n:], self.fixture['org_units'])
        self.assertEqual(self.actual['people'][1026:], self.fixture['people'])
        self.assertEqual(self.site['people'], self.actual['people'])
        batches = self.actual['profile_batches'][199:]
        self.assertEqual([{k:b[k] for k in ('batch_id','school_id','people_count')} for b in batches], self.fixture['profile_batches'])
        for b in batches:
            self.assertTrue(b['integration_review_status'].startswith('NEW_RECOVERY'))
            self.assertNotIn('PENDING', b['integration_review_status'])

    def test_02_fixed_new_facts_tristates_slots_dates_and_guidance(self):
        people = self.actual['people'][1026:]
        events = [e for p in people for e in p['education']]
        self.assertEqual(len(events), 428)
        self.assertEqual([sum(e['degree_awarded'] is v for e in events) for v in (True, False, None)], [99,117,212])
        self.assertEqual(sum(len(p['mentors']) for p in people), 132)
        self.assertEqual(sum(len(p['appointments']) for p in people), 215)
        self.assertEqual(sum(len(p['publications']) for p in people), 184)
        self.assertEqual(len({s['id'] for p in people for s in p['sources']}), 249)
        current = {p['person_id']:p for p in people}
        for q in self.pins['exact_source_slots']:
            row = current[q['person_id']][q['table']][q['index']]
            self.assertIn(q['key'], row)
            self.assertEqual(row[q['key']], q['value'])
        for expected in self.fixture['people']:
            p=current[expected['person_id']]
            for table in ('education','appointments','mentors','publications','teaching'):
                for i, row in enumerate(expected.get(table, [])):
                    got=p[table][i]
                    keys={k for k in set(row)|set(got) if any(t in k.lower() for t in ('date','year','month','start','end','period'))}
                    for key in keys:
                        self.assertEqual(key in got, key in row)
                        self.assertEqual(got.get(key),row.get(key))
                        self.assertIs(type(got.get(key)),type(row.get(key)))
            self.assertFalse(p.get('professional_research_advisors'))
            for mentor in p['mentors']:
                self.assertEqual(mentor['employment_status'],'unknown')
                self.assertIsNone(mentor['person_id'])
        p=current['xjtu-she-gang']
        self.assertTrue(any('杜晓军' in text for text in p['unknowns']))
        self.assertFalse(any(m['name']=='杜晓军' for m in p['mentors']))

    def test_03_all_98_fixed_departments_preserve_members_and_all_five_sheet_values(self):
        # Do not glob/open inherited workbooks. This loop is the only XLSX reader.
        old_affected=0
        for dept, scope in self.allowed_departments.items():
            with self.subTest(department=dept):
                self.assertTrue(dept.startswith(scope['school_id']+'-'))
                members=[p for p in self.actual['people'] if p['department_id']==dept and p['school_id']==scope['school_id']]
                old_ids=scope['old_person_ids'];new_ids=scope['new_person_ids']
                self.assertEqual([p['person_id'] for p in members],old_ids+new_ids)
                self.assertEqual(hashlib.sha256(json.dumps(members[:len(old_ids)], ensure_ascii=False, separators=(',', ':')).encode()).hexdigest(),scope['old_people_object_sha256'])  # Frozen scope preserves source object-key order.
                old_affected+=bool(old_ids)
                self.assertEqual(len({p['name'] for p in members}),len(members),'fixed workbook name-row matching must be unambiguous')
                path=ROOT/'site/exports'/(dept+'.xlsx')
                self.assertFalse(path.is_symlink())
                wb=load_workbook(path,read_only=True,data_only=False)
                try:
                    tables=build.department_tables(members,self.actual['updated_at'],self.actual['institutions'])
                    self.assertEqual(wb.sheetnames,['总览','经历','导师','论文','来源'])
                    actual_tables={}
                    for name, rows in tables:
                        expected=[[build.clean(v) if build.clean(v)!='' else None for v in row] for row in rows]
                        actual_tables[name]=[list(row) for row in wb[name].iter_rows(values_only=True)]
                        self.assertEqual(actual_tables[name],expected,(dept,name))
                    self.assertEqual([row[0] for row in actual_tables['总览'][1:]],[p['name'] for p in members])
                    # Independent fixed-source assertions beyond the shared table implementation.
                    for pid in new_ids:
                        p=self.new[pid]
                        overview=[r for r in actual_tables['总览'][1:] if r[0]==p['name']]
                        self.assertEqual(len(overview),1)
                        self.assertEqual(overview[0][5], '；'.join(p['unknowns']) or None)
                        history=[r for r in actual_tables['经历'][1:] if r[0]==p['name']]
                        for i,e in enumerate(p['education']):
                            self.assertEqual(history[i][1],e.get('event_kind'))
                            self.assertEqual(history[i][4],e.get('start') or None)
                            self.assertEqual(history[i][5],e.get('end') or None)
                            self.assertIs(history[i][11],e['degree_awarded'])
                            self.assertEqual(history[i][14],e.get('note') or None)
                        mentoring=[r for r in actual_tables['导师'][1:] if r[0]==p['name']]
                        self.assertEqual(len(mentoring),len(p['mentors']))
                        for row,m in zip(mentoring,p['mentors'],strict=True):
                            self.assertEqual(row[1],m['name']);self.assertEqual(row[4],m.get('description') or None)
                        works=[r for r in actual_tables['论文'][1:] if r[0]==p['name']]
                        self.assertEqual(len(works),len(p['publications']))
                        for row,w in zip(works,p['publications'],strict=True):self.assertEqual(row[9],w.get('note') or None)
                finally:
                    wb.close()
        self.assertEqual(old_affected,38)

    def test_04_receipt_complete_output_inventory_hashes_and_inherited_git_refs_only(self):
        r=self.receipt
        self.assertEqual(r['status'],'NEW_RECOVERY_RESTRICTED_BUILD_ONLY')
        self.assertEqual(r['full_suite'],'NOT_RUN')
        self.assertEqual(r['base_commit'],self.pins['base_commit'])
        self.assertEqual(r['base_tree'],self.pins['base_tree'])
        self.assertEqual(r['build_id'],self.site['build_id'])
        workbooks={'site/exports/'+dept+'.xlsx' for dept in self.allowed_departments}|{'site/exports/待核对名录.xlsx'}
        outputs=workbooks|{'site/people/'+sid+'.json' for sid in self.pins['baseline_school_ids']}|{'site/atlas.json','site/rosters.json','site/exports/待核对名录.csv'}
        self.assertEqual(len(workbooks),99)
        self.assertEqual(set(r['generated_workbooks']),workbooks)
        self.assertEqual(set(r['generated_output_inventory']),outputs)
        self.assertEqual(set(r['generated_sha256']),outputs)
        # Only exact declared generated paths may be hashed, never inherited bytes.
        for rel in sorted(outputs):
            self.assertFalse((ROOT/rel).is_symlink())
            self.assertEqual(hashlib.sha256((ROOT/rel).read_bytes()).hexdigest(),r['generated_sha256'][rel],rel)
        inherited={p:v for p,v in r['inherited_content_not_rechecked'].items() if p.endswith('.xlsx')}
        self.assertEqual(inherited,self.pins['inherited_workbook_git_references'])
        self.assertEqual(len(inherited),385)
        self.assertFalse(workbooks & set(inherited))
        for rel in inherited:
            self.assertFalse((ROOT/rel).exists(),'inherited bytes must remain unmaterialized: '+rel)

if __name__=='__main__':
    unittest.main()
