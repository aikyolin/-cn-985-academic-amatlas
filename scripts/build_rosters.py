"""Keep consolidated roster records, raw observations and personal profiles distinct.

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
UNVERIFIED_BATCHES = {'harbin-002', 'weihai-003', 'shenzhen-004', 'shenzhen-005'}


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


def _official_news_identity_match(entry, person):
    """Verify a career-report identity, never an unavailable personal homepage."""
    evidence = entry.get('profile_identity_evidence') or {}
    news = evidence.get('official_news_identity_verification') or {}
    sources = {s.get('id'): s.get('url') for s in person.get('sources', [])}
    reports = person.get('alternative_professional_sources') or []
    report_ids = {r.get('source_id') for r in reports}
    source_ids = news.get('source_ids') or []
    news_ids = news.get('news_source_ids') or []
    return bool(
        entry.get('professional_identity_verified') is True
        and entry.get('official_profile_identity_verified') is False
        and entry.get('official_profile_availability') == 'unavailable'
        and entry.get('official_profile_navigation_eligible') is False
        and person.get('official_profile_availability') == 'unavailable'
        and person.get('official_profile_navigation_eligible') is False
        and person.get('own_profile_academic_body_read') is False
        and person.get('professional_evidence_body_read') is True
        and evidence.get('status') == 'official_roster_name_and_campus_news_verified_profile_unavailable'
        and news.get('status') == 'official_roster_name_and_campus_news_matched'
        and news.get('name') == person['name']
        and news.get('organization_id') == person['department_id']
        and news.get('roster_url') == entry['official_profile_url']
        and news.get('checked_on') and evidence.get('checked_on')
        and evidence.get('roster_source_url') == entry['roster_source_url']
        and source_ids and set(source_ids) <= set(sources)
        and set(source_ids) <= set(evidence.get('source_ids') or [])
        and entry['roster_source_url'] in {sources.get(i) for i in source_ids}
        and news_ids and set(news_ids) == report_ids
        and set(news_ids) <= set(source_ids)
        and entry.get('alternative_professional_sources') == reports
        and evidence.get('alternative_professional_sources') == reports
        and all(valid_url(r.get('url')) and sources.get(r.get('source_id')) == r['url']
                and urlparse(r['url']).hostname in {'news.hit.edu.cn', 'news.hitwh.edu.cn'}
                for r in reports)
    )


def _verified_profile_match(entry, person):
    """Accept cross-domain aliases only from explicit, source-backed identity evidence.

    verified_alias_urls is a list of independently verified equivalent URLs;
    redirect_chain is an ordered URL list beginning at the roster homepage and
    ending at the detailed profile. Neither is inferred from a shared URL slug.
    """
    if entry['name'] != person['name'] or entry['organization_id'] != person['department_id']:
        return False
    if entry.get('official_profile_availability') == 'unavailable' or person.get('official_profile_availability') == 'unavailable':
        # Must precede same-URL matching: a dead URL cannot prove profile identity.
        return _official_news_identity_match(entry, person)
    if _matches_profile(entry, person):
        return True
    # A missing directory link is not a missing identity: accept only an explicit,
    # independently reviewed name/organization/person match with closed evidence.
    if entry.get('official_profile_url') is None:
        evidence = entry.get('profile_identity_evidence') or {}
        independent = evidence.get('independent_profile_verification') or {}
        sources = {s.get('id'): s.get('url') for s in person.get('sources', [])}
        source_ids = independent.get('source_ids') or []
        return bool(
            entry.get('profile_identity_verified') is True
            and entry.get('verified_person_id') == person['person_id']
            and person.get('detail_count_eligible') is True
            and evidence.get('status') == 'independent_current_official_profile_name_department_match'
            and independent.get('status') == 'official_name_and_department_matched'
            and independent.get('identity_verified') is True
            and independent.get('person_id') == person['person_id']
            and independent.get('name') == person['name']
            and independent.get('organization_id') == person['department_id']
            and 'roster_url' in independent and independent['roster_url'] is None
            and 'roster_link_url' in evidence and evidence['roster_link_url'] is None
            and valid_url(person.get('official_url'))
            and independent.get('official_url') == person['official_url']
            and evidence.get('official_url') == person['official_url']
            and evidence.get('roster_source_url') == entry['roster_source_url']
            and evidence.get('checked_on')
            and isinstance(source_ids, list) and source_ids
            and set(source_ids) <= set(sources)
            and set(source_ids) <= set(evidence.get('source_ids') or [])
            and entry['roster_source_url'] in {sources.get(i) for i in source_ids}
            and person['official_url'] in {sources.get(i) for i in source_ids}
        )
    if not valid_url(entry.get('official_profile_url')) or not valid_url(person.get('official_url')):
        return False
    evidence = entry.get('profile_identity_evidence') or {}
    if not isinstance(evidence, dict):
        return False
    independent = evidence.get('independent_profile_verification')
    if (
        evidence.get('status') == 'independent_current_official_profile_name_department_match'
        and isinstance(independent, dict)
        and independent.get('status') == 'official_name_and_department_matched'
        and valid_url(independent.get('official_url'))
        and homepage_key(independent['official_url']) == homepage_key(person['official_url'])
        and independent.get('roster_url') == entry['official_profile_url']
        and isinstance(independent.get('source_ids'), list)
        and independent['source_ids']
        and all(isinstance(value, str) and value.strip() for value in independent['source_ids'])
    ):
        # A fresh official page checked for name and department is not a redirect
        # or an assertion that the obsolete directory-linked URL is an alias.
        return True
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
    """Validate records and their raw-source counts without merging people."""
    entries = rosters['entries']
    entry_ids = {entry['id'] for entry in entries}
    assert len(entry_ids) == len(entries), 'Duplicate roster record ID'
    people = {person['person_id']: person for person in atlas['people']}
    organizations = {org['id'] for org in atlas['org_units']}
    batch_ids = set()
    batch_entry_ids = set()
    unverified_batch_ids = set()
    entries_by_id = {entry['id']: entry for entry in entries}
    if 'source_observations' in rosters:
        raw_count = len(rosters['source_observations'])
    else:
        raw_count = rosters.get('totals', {}).get('raw_observation_count', len(entries))
        if raw_count != len(entries):
            assert rosters.get('raw_data_location'), 'Raw source observations missing without a disclosure'
    for batch in rosters.get('batches', []):
        assert batch['batch_id'] not in batch_ids, 'Duplicate roster batch ID'
        batch_ids.add(batch['batch_id'])
        ids = batch['entry_ids']
        record_count = batch.get('record_count', batch.get('observation_count'))
        assert len(ids) == len(set(ids)) == record_count, 'Batch record count mismatch'
        assert set(ids) <= entry_ids, 'Unknown batch observation ID'
        assert not batch_entry_ids.intersection(ids), 'Observation belongs to multiple batches'
        batch_entry_ids.update(ids)
        if batch['batch_id'] in UNVERIFIED_BATCHES:
            unverified_batch_ids.update(ids)
    if rosters.get('batches'):
        assert batch_entry_ids == entry_ids, 'Missing observation batch provenance'
    if 'source_observations' in rosters:
        observations = rosters['source_observations']
        observation_ids = {item['observation_id'] for item in observations}
        assert len(observation_ids) == len(observations), 'Duplicate source observation ID'
        for item in observations:
            assert item['record_id'] in entries_by_id, 'Unknown source observation record'
            assert item['organization_id'] == entries_by_id[item['record_id']]['organization_id'], 'Source observation organization mismatch'
            assert valid_url(item['source_url']), 'Unsafe source observation URL'
            assert isinstance(item['source_payload'], dict), 'Original source observation payload missing'
        for batch in rosters.get('batches', []):
            observed_ids = {item['observation_id'] for item in observations if item['batch_id'] == batch['batch_id']}
            assert observed_ids == set(batch['source_observation_ids']), 'Batch source observation references mismatch'
            assert len(observed_ids) == batch['raw_observation_count'] == batch['raw_count'], 'Batch raw observation count mismatch'
            assert all(item['record_id'] in batch['entry_ids'] for item in observations if item['batch_id'] == batch['batch_id']), 'Source observation belongs to a different batch'
        for entry in entries:
            if 'source_observation_ids' in entry:
                assert set(entry['source_observation_ids']) == {item['observation_id'] for item in observations if item['record_id'] == entry['id']}, 'Record source observation references mismatch'
        assert {item['record_id'] for item in observations} == entry_ids, 'Record is missing source observations'

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
    assert sum(item['visible_name_count'] for item in rosters['coverage']) == raw_count, 'Coverage raw observation count mismatch'
    assert sum(item['visible_roster_entries'] for item in rosters['summary']) == len(entries), 'Summary observation count mismatch'
    if rosters.get('totals'):
        totals = rosters['totals']
        assert totals.get('record_count', totals.get('roster_observations')) == len(entries), 'Total record count mismatch'
        if 'raw_observation_count' in totals:
            assert totals['raw_observation_count'] == raw_count, 'Total raw observation count mismatch'
        if 'count_unit' in totals:
            assert totals['count_unit'] == 'integrated_roster_records', 'Record count must not be labeled as raw observations'
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
        'source_observation_ids', 'additional_roster_sources', 'consolidation_basis',
        'listed_department', 'roster_data_source_url', 'roster_request_parameters',
        'profile_display_update_time', 'profile_update_time_status',
        'source_profile_identity_verified', 'profile_verification',
    ]
    headers = [
        '记录ID', '姓名', '校区', '组织ID', '原始分类', '官网列示职务',
        '原名录主页链接（身份以核验列为准）', '名录来源', '查阅日期',
        '核验状态', '职业身份关联已核（不代表个人主页可用）', '独立档案候选（未合并）', '备注',
        '名录原始姓名', '原始链接（含占位，仅证据）', '来源批次', '自动合并',
        '经独立核验的档案ID', '独立身份核验证据', '档案关联状态',
        '名录原始资格或身份附注（不是师承关系）', '名录声明更新日期（非本轮核验日期）',
        '原始来源观察ID', '多来源名录证据', '源记录整合依据（不代表人口去重）',
        '门户原列单位', '门户公开数据来源', '公开组织筛选参数',
        '门户个人资料显示更新时间（非在职核验）', '源时间状态及占位说明',
        '源批次原始主页核验值（不代表本项目档案关联）', '源批次主页归属证据',
    ]
    rows = [headers]
    for entry in entries:
        export_entry = dict(entry, batch_id=entry.get('batch_id') or batches.get(entry['id']), source_declared_update=source_dates.get((entry['organization_id'], entry['category'], entry['roster_source_url'])))
        rows.append([export_entry.get(key) for key in columns])
    tables = {'待核对名录': rows}
    tables['覆盖说明'] = [
        ['范围与限制'], [rosters['scope']],
        *[[limitation] for limitation in rosters['limitations']],
        [f"{len(entries)}条整合名录记录，另保存{len(rosters.get('source_observations', entries))}条原始来源观察；不是唯一人数或已核实在职人数，{len(atlas['people'])}份独立详细档案不自动合并。"],
        ['统计', rosters.get('totals', {})],
    ]
    tables['分类覆盖'] = [
        ['组织', '来源分类或分页', '原始来源观察条目数（非整合记录数）', '来源', '查阅日期', '原角色分类', '有效候选主页数', '批次', '来源声明更新日期（非现任核验）', '原角色分组计数'],
        *[[item['organization_id'], item['category'], item['visible_name_count'], item['url'], item['accessed_on'], item.get('role'), item.get('entries_with_valid_candidate_link'), item.get('batch_id', 'pilot-001'), item.get('source_declared_update'), item.get('role_counts')] for item in rosters['coverage']],
    ]
    tables['冲突记录'] = [['类型', '详情'], *[[item['type'], item] for item in rosters['conflicts']]]
    tables['消歧候选'] = [
        ['候选类型', '姓名或链接', '名录记录ID', '自动合并', '批次', '原始详情'],
        *[[item['kind'], item.get('name') or item.get('url'), item['entry_ids'], item['automatic_merge'], item.get('batch_id'), item] for item in rosters.get('dedup_candidates', [])],
    ]
    tables['批次来源'] = [
        ['批次', '整合名录记录数', '原始来源观察数', '类别数', '来源覆盖行数', '查阅日期', '来源文件及SHA256', '批次核对', '名录记录ID'],
        *[[batch['batch_id'], batch.get('record_count', batch.get('observation_count')), batch.get('raw_observation_count', batch.get('observation_count')), batch['category_count'], batch.get('coverage_unit_count', batch['category_count']), batch['accessed_on'], batch['source_files'], batch.get('validation'), batch['entry_ids']] for batch in rosters.get('batches', [])],
        ['源页面快照（文件名及SHA256）', rosters.get('source_snapshots', [])],
    ]
    tables['排除与待查'] = [
        ['类型', '详情'],
        *[['未并入当前主名录', item] for item in rosters.get('exclusions', [])],
        *[['待交叉核验', item] for item in rosters.get('pending_checks', [])],
        *[['原附注与角色解释（不推断师承）', {'name_or_group': name, 'detail': detail}] for name, detail in rosters.get('role_interpretation', {}).items()],
    ]
    tables['原始来源观察'] = [
        ['原始观察ID', '对应整合记录ID', '批次', '组织', '来源URL', '查阅日期', '原始观察内容', '历史本地观察解释', '本地映射订正（原值不改写）', '已撤回的本地附注'],
        *[[item['observation_id'], item['record_id'], item['batch_id'], item['organization_id'], item['source_url'], item['accessed_on'], item['source_payload'], item.get('source_payload_interpretation'), item.get('local_mapping_correction'), item.get('withdrawn_local_annotation')] for item in rosters.get('source_observations', [])],
    ]
    tables['整合依据'] = [
        ['批次', '原始观察数', '整合记录数', '源记录分组减少数（非人数减少）', '已执行身份合并数', '说明'],
        *[[item['batch_id'], item['raw_count'], item['record_count'], item['source_record_grouping_reduction'], item['identity_merges_performed'], item] for item in rosters.get('consolidations', [])],
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
    # The canonical dataset and XLSX matrices retain every raw observation.
    # Browser pages use the integrated records; avoid downloading the duplicate
    # source payloads on every page load and disclose where the evidence remains.
    snapshot = dict(rosters)
    if 'source_observations' in snapshot:
        snapshot.pop('source_observations')
        snapshot['raw_data_location'] = '完整原始来源观察保存在仓库 data/rosters.json，以及导出 Excel 的“原始来源观察”工作表；网站快照不重复加载这些原始内容。'
    (ROOT / 'site/rosters.json').write_text(json.dumps(snapshot, ensure_ascii=False, indent=2) + '\n')
    formats = 'JSON, CSV and XLSX' if generate_excel else 'JSON and CSV (XLSX not generated)'
    print(f'Built {len(rosters["entries"])} roster records with {len(rosters.get("source_observations", rosters["entries"]))} raw source observations: {formats}')
    return tables
