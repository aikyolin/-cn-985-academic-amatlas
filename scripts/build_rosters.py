"""Keep roster observations separate from independently researched personal profiles.

Importing this module, validation, preparation and table generation have no file
side effects. Only build_rosters writes exports; generate_excel=False avoids XLSX.
"""
import copy
import csv
import json
from urllib.parse import urlparse

from build import ROOT, clean, sheet, valid_url


ENTRY_FIELDS = (
    'id', 'name', 'campus_id', 'organization_id', 'category', 'listed_role',
    'official_profile_url', 'roster_source_url', 'accessed_on', 'notes',
    'verification_status', 'profile_identity_verified',
)
UNVERIFIED_BATCHES = {'harbin-002', 'weihai-003'}


def homepage_key(url):
    parsed = urlparse(url or '')
    return (parsed.hostname or '', parsed.path.rstrip('/'))


def _matches_profile(entry, person):
    return (
        entry['name'] == person['name']
        and entry['organization_id'] == person['department_id']
        and valid_url(entry.get('official_profile_url'))
        and valid_url(person.get('official_url'))
        and homepage_key(entry['official_profile_url']) == homepage_key(person['official_url'])
    )


def _verified_profile_match(entry, person):
    """Accept cross-domain aliases only from explicit, source-backed identity evidence.

    verified_alias_urls is a list of independently verified equivalent URLs;
    redirect_chain is an ordered URL list beginning at the roster homepage and
    ending at the detailed profile. Neither is inferred from a shared URL slug.
    """
    if entry['name'] != person['name'] or entry['organization_id'] != person['department_id']:
        return False
    if _matches_profile(entry, person):
        return True
    if not valid_url(entry.get('official_profile_url')) or not valid_url(person.get('official_url')):
        return False
    evidence = entry.get('profile_identity_evidence') or {}
    if not isinstance(evidence, dict):
        return False
    start, end = homepage_key(entry['official_profile_url']), homepage_key(person['official_url'])
    aliases = evidence.get('verified_alias_urls', [])
    if isinstance(aliases, list) and aliases and all(valid_url(url) for url in aliases):
        keys = {homepage_key(url) for url in aliases}
        if start in keys and end in keys:
            return True
    chain = evidence.get('redirect_chain', [])
    return (
        isinstance(chain, list) and len(chain) >= 2
        and all(valid_url(url) for url in chain)
        and homepage_key(chain[0]) == start and homepage_key(chain[-1]) == end
    )


def validate_rosters(rosters, atlas):
    """Validate references, evidence and observation counts without merging people."""
    entries = rosters['entries']
    entry_ids = {entry['id'] for entry in entries}
    assert len(entry_ids) == len(entries), 'Duplicate roster record ID'
    people = {person['person_id']: person for person in atlas['people']}
    organizations = {org['id'] for org in atlas['org_units']}
    batch_ids = set()
    batch_entry_ids = set()
    unverified_batch_ids = set()
    for batch in rosters.get('batches', []):
        assert batch['batch_id'] not in batch_ids, 'Duplicate roster batch ID'
        batch_ids.add(batch['batch_id'])
        ids = batch['entry_ids']
        assert len(ids) == len(set(ids)) == batch['observation_count'], 'Batch observation count mismatch'
        assert set(ids) <= entry_ids, 'Unknown batch observation ID'
        assert not batch_entry_ids.intersection(ids), 'Observation belongs to multiple batches'
        batch_entry_ids.update(ids)
        if batch['batch_id'] in UNVERIFIED_BATCHES:
            unverified_batch_ids.update(ids)
    if rosters.get('batches'):
        assert batch_entry_ids == entry_ids, 'Missing observation batch provenance'

    for entry in entries:
        assert all(key in entry for key in ENTRY_FIELDS), 'Missing roster field'
        assert isinstance(entry['name'], str) and entry['name'].strip(), 'Empty roster name'
        assert entry['organization_id'] in organizations, 'Unknown roster organization'
        assert valid_url(entry['roster_source_url']), 'Unsafe roster source URL'
        assert not entry['official_profile_url'] or valid_url(entry['official_profile_url']), 'Unsafe candidate profile URL'
        assert isinstance(entry['notes'], list) and all(isinstance(note, str) for note in entry['notes']), 'Invalid roster notes'
        assert isinstance(entry.get('listed_qualifiers', []), list) and all(isinstance(value, str) for value in entry.get('listed_qualifiers', [])), 'Invalid original roster qualifiers'
        assert entry.get('automatic_merge', False) is False, 'Roster observations must not auto-merge'
        assert type(entry['profile_identity_verified']) is bool, 'Identity verification must be explicit'
        if entry['id'] in unverified_batch_ids or entry.get('batch_id') in UNVERIFIED_BATCHES:
            assert entry['profile_identity_verified'] is False, 'New-batch identities remain unverified'
        if entry['profile_identity_verified']:
            person = people.get(entry.get('verified_person_id'))
            assert person and _verified_profile_match(entry, person), 'Verified identity must match its explicit personal profile'
            evidence = entry.get('profile_identity_evidence')
            assert isinstance(evidence, dict) and evidence, 'Verified identity requires independent evidence'
            assert evidence.get('source_ids') and evidence.get('checked_on'), 'Verified identity evidence needs sources and a date'
            assert evidence.get('roster_source_url') == entry['roster_source_url'], 'Identity evidence roster source mismatch'
            assert valid_url(evidence.get('official_url')) and homepage_key(evidence['official_url']) == homepage_key(person['official_url']), 'Identity evidence homepage mismatch'
        else:
            assert not entry.get('verified_person_id'), 'Unverified observation cannot claim a verified person'

    for candidate in rosters.get('dedup_candidates', []):
        assert candidate['automatic_merge'] is False, 'Dedup groups must remain candidates'
        assert set(candidate['entry_ids']) <= entry_ids, 'Unknown dedup candidate observation'
    for conflict in rosters.get('conflicts', []):
        referenced_ids = conflict.get('entry_ids', []) + ([conflict['entry_id']] if conflict.get('entry_id') else [])
        assert set(referenced_ids) <= entry_ids, 'Unknown conflict observation'
        if conflict.get('kind'):
            assert conflict['type'] == conflict['kind'], 'Conflict compatibility alias changed meaning'
    for coverage in rosters['coverage']:
        assert coverage['organization_id'] in organizations, 'Unknown coverage organization'
        assert valid_url(coverage['url']), 'Unsafe coverage source URL'
        if 'source_url' in coverage:
            assert coverage['url'] == coverage['source_url'], 'Coverage URL alias mismatch'
        if 'visible_entries' in coverage:
            assert coverage['visible_name_count'] == coverage['visible_entries'], 'Coverage count alias mismatch'
    assert sum(item['visible_name_count'] for item in rosters['coverage']) == len(entries), 'Coverage observation count mismatch'
    assert sum(item['visible_roster_entries'] for item in rosters['summary']) == len(entries), 'Summary observation count mismatch'
    if rosters.get('totals'):
        totals = rosters['totals']
        assert totals['roster_observations'] == len(entries), 'Total observation count mismatch'
        assert totals['entries_without_profile_link'] == sum(not entry['official_profile_url'] for entry in entries), 'Missing-link count mismatch'
        assert totals['entries_with_profile_link'] == sum(bool(entry['official_profile_url']) for entry in entries), 'Candidate-link count mismatch'
        assert totals['not_unique_people_count'] is True, 'Observations are not unique people'
        assert totals['current_employment_count_verified'] is False, 'Roster count is not verified current employment'
    return True


def prepare_rosters(rosters, atlas):
    """Return a copy with candidate links only; never promote identity or merge rows."""
    validate_rosters(rosters, atlas)
    prepared = copy.deepcopy(rosters)
    for entry in prepared['entries']:
        entry['automatic_merge'] = False
        if entry['profile_identity_verified']:
            # This relation was explicitly checked upstream, not inferred here.
            entry['candidate_person_ids'] = []
            entry['candidate_match_status'] = 'verified_separate_profile'
        else:
            entry['candidate_person_ids'] = [
                person['person_id'] for person in atlas['people']
                if _matches_profile(entry, person)
            ]
            entry['candidate_match_status'] = (
                'pending_identity_review' if entry['candidate_person_ids'] else 'not_linked'
            )
    return prepared


def roster_tables(rosters, atlas):
    """Return ordered worksheet-name -> row matrices, without creating a workbook."""
    rosters = prepare_rosters(rosters, atlas)
    entries = rosters['entries']
    batches = {entry_id: batch['batch_id'] for batch in rosters.get('batches', []) for entry_id in batch['entry_ids']}
    source_dates = {(item['organization_id'], item['category'], item['url']): item.get('source_declared_update') for item in rosters['coverage']}
    columns = [
        'id', 'name', 'campus_id', 'organization_id', 'category', 'listed_role',
        'official_profile_url', 'roster_source_url', 'accessed_on',
        'verification_status', 'profile_identity_verified', 'candidate_person_ids',
        'notes', 'name_as_listed', 'source_link_raw', 'batch_id', 'automatic_merge',
        'verified_person_id', 'profile_identity_evidence', 'candidate_match_status',
        'listed_qualifiers', 'source_declared_update',
    ]
    headers = [
        '记录ID', '姓名', '校区', '组织ID', '原始分类', '官网列示职务',
        '原名录主页链接（身份以核验列为准）', '名录来源', '查阅日期',
        '核验状态', '主页身份已核实', '独立档案候选（未合并）', '备注',
        '名录原始姓名', '原始链接（含占位，仅证据）', '来源批次', '自动合并',
        '经独立核验的档案ID', '独立身份核验证据', '档案关联状态',
        '名录原始资格或身份附注（不是师承关系）', '名录声明更新日期（非本轮核验日期）',
    ]
    rows = [headers]
    for entry in entries:
        export_entry = dict(entry, batch_id=entry.get('batch_id') or batches.get(entry['id']), source_declared_update=source_dates.get((entry['organization_id'], entry['category'], entry['roster_source_url'])))
        rows.append([export_entry.get(key) for key in columns])
    tables = {'待核对名录': rows}
    tables['覆盖说明'] = [
        ['范围与限制'], [rosters['scope']],
        *[[limitation] for limitation in rosters['limitations']],
        [f"{len(entries)}条为名录观察，不是唯一人数或已核实在职人数；{len(atlas['people'])}份独立详细档案不与观察自动合并。"],
        ['统计', rosters.get('totals', {})],
    ]
    tables['分类覆盖'] = [
        ['组织', '分类', '可见观察条目数', '来源', '查阅日期', '原角色分类', '有效候选主页数', '批次', '来源声明更新日期（非现任核验）', '原角色分组计数'],
        *[[item['organization_id'], item['category'], item['visible_name_count'], item['url'], item['accessed_on'], item.get('role'), item.get('entries_with_valid_candidate_link'), item.get('batch_id', 'pilot-001'), item.get('source_declared_update'), item.get('role_counts')] for item in rosters['coverage']],
    ]
    tables['冲突记录'] = [['类型', '详情'], *[[item['type'], item] for item in rosters['conflicts']]]
    tables['消歧候选'] = [
        ['候选类型', '姓名或链接', '观察记录ID', '自动合并', '批次', '原始详情'],
        *[[item['kind'], item.get('name') or item.get('url'), item['entry_ids'], item['automatic_merge'], item.get('batch_id'), item] for item in rosters.get('dedup_candidates', [])],
    ]
    tables['批次来源'] = [
        ['批次', '观察条目数', '分类数', '查阅日期', '来源文件及SHA256', '批次核对', '原始观察ID'],
        *[[batch['batch_id'], batch['observation_count'], batch['category_count'], batch['accessed_on'], batch['source_files'], batch.get('validation'), batch['entry_ids']] for batch in rosters.get('batches', [])],
        ['源页面快照（文件名及SHA256）', rosters.get('source_snapshots', [])],
    ]
    tables['排除与待查'] = [
        ['类型', '详情'],
        *[['未并入当前主名录', item] for item in rosters.get('exclusions', [])],
        *[['待交叉核验', item] for item in rosters.get('pending_checks', [])],
        *[['原附注与角色解释（不推断师承）', {'name_or_group': name, 'detail': detail}] for name, detail in rosters.get('role_interpretation', {}).items()],
    ]
    return tables


def build_rosters(atlas, generate_excel=True):
    rosters = prepare_rosters(json.loads((ROOT / 'data/rosters.json').read_text()), atlas)
    tables = roster_tables(rosters, atlas)
    output = ROOT / 'site/exports'
    output.mkdir(parents=True, exist_ok=True)
    with (output / '待核对名录.csv').open('w', encoding='utf-8-sig', newline='') as file:
        csv.writer(file).writerows([[clean(value) for value in row] for row in tables['待核对名录']])
    if generate_excel:
        from openpyxl import Workbook
        workbook = Workbook()
        workbook.remove(workbook.active)
        for name, rows in tables.items():
            sheet(workbook, name, rows)
        workbook.save(output / '待核对名录.xlsx')
    (ROOT / 'site/rosters.json').write_text(json.dumps(rosters, ensure_ascii=False, indent=2) + '\n')
    formats = 'JSON, CSV and XLSX' if generate_excel else 'JSON and CSV (XLSX not generated)'
    print(f'Built {len(rosters["entries"])} separate roster observations: {formats}')
    return tables
