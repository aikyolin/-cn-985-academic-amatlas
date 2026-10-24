"""Pinned clean-public append history. No sanitizer or live-derived expectations.

Prefix projection preserves historical facts, not approval of a new suffix. An
append endpoint must separately bind its reviewed source scope and exact tree.
"""
import copy
import hashlib
import json
from pathlib import Path, PurePosixPath
import re

ROOT = Path(__file__).resolve().parents[1]
BASELINE_FIXTURE_SHA256 = '034470bc2d40294199f60051f0619d095ebd47aa882acf0652b5e20a47fb2526'
INVENTORY_FIXTURE_SHA256 = 'c35c0512ff5a147a4d412da6abed4bd7fbe61cd8193893b90db57c394b798af9'
# Independently reviewed literal; never derived from candidate bytes at runtime.
APPEND_MANIFEST_SHA256 = '04d468e8c9393ceae148f0b5c6200172173f5c8ddaf12841cc6e47a690cc44ae'
BASELINE_PATH = 'tests/fixtures/release32-public-baseline.json'
INVENTORY_PATH = 'tests/fixtures/release32-public-file-manifest.json'
APPEND_MANIFEST_PATH = 'tests/fixtures/rotation003-wave8-append-manifest.json'
SOURCE_CONTRACT_PATH = 'tests/fixtures/rotation003-wave8-source-contract.json'
SOURCE_FIXTURE_PATH = 'tests/fixtures/rotation003-wave8-clean-public-sources.json'
MUTABLE_ENDPOINTS = frozenset({
    'data/atlas.json', 'data/rosters.json', 'site/atlas.json', 'site/rosters.json',
    'progress/work-queue.json', 'progress/README.md', 'progress/current-coverage.md',
    'site/exports/待核对名录.csv', 'site/exports/待核对名录.xlsx',
})
IMPLEMENTATION_MODIFIED_FILES = frozenset({
    'tests/test_rotation003_wave7_boundaries.py',
    'tests/rotation002-wave3-display-fix.test.js',
    'tests/rotation003-wave1-display-fix.test.js',
    'tests/test_rotation003_wave1_display_fix.py',
    'tests/test_rotation003_wave1_layout_fix.py',
})
IMPLEMENTATION_ADDED_FILES = frozenset({
    BASELINE_PATH, INVENTORY_PATH, APPEND_MANIFEST_PATH,
    'tests/public_append_history.py', 'tests/public-append-history.js',
    'scripts/validate_source_contract.py', 'tests/test_rotation003_wave8_source_contract.py',
    'tests/fixtures/rotation003-wave8-source-contract.json',
    'tests/fixtures/rotation003-wave8-clean-public-sources.json',
    'tests/test_public_append_history.py', 'tests/public-append-history.test.js',
})
_HASH = re.compile(r'^[0-9a-f]{64}$')
_ID = re.compile(r'^[A-Za-z0-9_-]+$')


def require(ok, message):
    if not ok:
        raise ValueError(message)


def sha256(raw):
    return hashlib.sha256(raw).hexdigest()


def _canonical_domain(value):
    if isinstance(value, dict):
        require(all(type(key) is str for key in value), 'non-string JSON key')
        for key, item in value.items():
            key.encode('utf-8'); _canonical_domain(item)
    elif isinstance(value, list):
        for item in value:
            _canonical_domain(item)
    elif type(value) is str:
        value.encode('utf-8')
    elif type(value) is int:
        require(abs(value) <= 9007199254740991, 'JSON number outside safe integer domain')
    else:
        require(value is None or type(value) is bool, 'JSON number/type outside shared canonical domain')


def canonical_digest(value):
    _canonical_domain(value)
    return sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
                            separators=(',', ':'), allow_nan=False).encode('utf-8'))


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, 'duplicate JSON key: ' + key)
        result[key] = value
    return result


def pinned_json(raw, expected_sha256):
    """The caller supplies an independent reviewed literal, never the live hash."""
    require(isinstance(expected_sha256, str) and _HASH.fullmatch(expected_sha256), 'missing static SHA256 pin')
    require(sha256(raw) == expected_sha256, 'pinned JSON bytes changed')
    return json.loads(raw, object_pairs_hook=_unique_object,
                      parse_constant=lambda value: (_ for _ in ()).throw(ValueError('non-JSON number')))


def load_baseline():
    baseline = pinned_json((ROOT / BASELINE_PATH).read_bytes(), BASELINE_FIXTURE_SHA256)
    require(baseline['version'] == 'public_append_baseline_v1', 'wrong baseline version')
    require(baseline['baseline_label'] == 'release32-clean-public-606', 'wrong baseline label')
    return baseline


def load_inventory():
    inventory = pinned_json((ROOT / INVENTORY_PATH).read_bytes(), INVENTORY_FIXTURE_SHA256)
    require(inventory['version'] == 'public_snapshot_inventory_v1', 'wrong inventory version')
    require(canonical_digest(inventory['files']) == inventory['files_object_sha256'], 'inventory object hash')
    require(inventory['source_commit'] == load_baseline()['source_commit'], 'inventory anchor mismatch')
    return inventory


def _same_shape(value, old):
    """Mutable metadata may advance values, never add siblings or change types."""
    require(type(value) is type(old), 'metadata type changed')
    if isinstance(old, dict):
        require(list(value) == list(old), 'metadata keys/order changed')
        for key in old:
            _same_shape(value[key], old[key])
    elif isinstance(old, list):
        require(len(value) == len(old), 'metadata list length changed')
        for new_item, old_item in zip(value, old):
            _same_shape(new_item, old_item)


def public_append_view(value, rel):
    baseline = load_baseline()
    require(rel in baseline['files'], 'unknown historical JSON path: ' + rel)
    spec = baseline['files'][rel]
    _canonical_domain(value)
    require(type(value) is dict and list(value) == spec['root_key_order'], 'root keys/order changed')
    result = {}
    for key in spec['root_key_order']:
        if key in spec['lists']:
            rule = spec['lists'][key]
            rows = value[key]
            require(type(rows) is list and len(rows) >= rule['length'], 'historical array shortened/type changed: ' + key)
            identity = rule.get('identity_key')
            if identity:
                require(all(type(row) is dict and type(row.get(identity)) is str and row[identity] for row in rows), 'missing list identity: ' + key)
                ids = [row[identity] for row in rows]
                require(len(ids) == len(set(ids)), 'duplicate list identity: ' + key)
            if rule['selection'] == 'prefix':
                selected = rows[:rule['length']]
            else:
                require(rule['selection'] == 'identity_set' and identity, 'unknown selection')
                frozen_ids = set(rule['ordered_ids'])
                selected = [row for row in rows if row[identity] in frozen_ids]
            require(len(selected) == rule['length'], 'missing frozen list row: ' + key)
            if identity:
                selected_ids = [row[identity] for row in selected]
                require(selected_ids == rule['ordered_ids'], 'historical identity order changed: ' + key)
                require(canonical_digest(selected_ids) == rule['ordered_ids_sha256'], 'historical identity hash changed')
            require(canonical_digest(selected) == rule['sha256'], 'historical array changed: ' + key)
            result[key] = copy.deepcopy(selected)
        else:
            old = spec['metadata'][key]
            _same_shape(value[key], old)
            if key not in spec['mutable_metadata']:
                require(canonical_digest(value[key]) == canonical_digest(old), 'immutable metadata changed: ' + key)
            result[key] = copy.deepcopy(old)
    require(canonical_digest(result) == spec['object_sha256'], 'historical object hash changed')
    # Also protect nested key insertion order; canonical hashes alone cannot do so.
    raw = (json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False) + '\n').encode('utf-8')
    require(len(raw) == spec['byte_length'] and sha256(raw) == spec['byte_sha256'], 'historical JSON bytes changed')
    return result


def public_append_bytes(value, rel):
    return (json.dumps(public_append_view(value, rel), ensure_ascii=False, indent=2) + '\n').encode('utf-8')


def _keys(value, keys, label):
    require(type(value) is dict and set(value) == set(keys), 'unknown/missing ' + label + ' fields')


def _path(rel):
    require(type(rel) is str and rel and '\\' not in rel and not rel.startswith('/'), 'invalid relative path')
    require(str(PurePosixPath(rel)) == rel and all(x not in {'.', '..'} for x in rel.split('/')), 'unsafe relative path')
    return rel


def _digest(value):
    require(type(value) is str and _HASH.fullmatch(value), 'invalid SHA256')


def _endpoint(value, changed=False):
    _keys(value, ['before_sha256', 'after_sha256', 'byte_length'] if changed else ['sha256', 'byte_length'], 'endpoint')
    _digest(value['after_sha256' if changed else 'sha256'])
    require(type(value['byte_length']) is int and value['byte_length'] >= 0, 'invalid byte length')
    if changed:
        _digest(value['before_sha256'])
        require(value['before_sha256'] != value['after_sha256'], 'unchanged file claimed as changed')


def validate_append_manifest(raw, expected_sha256, *, baseline, inventory, reviewed_scope,
                             implementation_added_files=IMPLEMENTATION_ADDED_FILES,
                             implementation_modified_files=IMPLEMENTATION_MODIFIED_FILES):
    """Pure contract, also usable with explicitly synthetic test inputs.

    reviewed_scope must be derived from independently pinned source-contract
    bytes, not from live files or the append manifest's proposed allowlist.
    """
    manifest = pinned_json(raw, expected_sha256)
    _keys(manifest, ['version', 'baseline_fixture_sha256', 'baseline_inventory_sha256',
                     'baseline_commit', 'source_contract', 'audit_digests',
                     'changed_existing', 'deleted_existing', 'allowed_added_outputs',
                     'implementation_added_files', 'implementation_modified_files'], 'manifest')
    require(manifest['version'] == 'public_append_manifest_v1', 'wrong manifest version')
    require(manifest['baseline_fixture_sha256'] == BASELINE_FIXTURE_SHA256, 'wrong baseline pin')
    require(manifest['baseline_inventory_sha256'] == INVENTORY_FIXTURE_SHA256, 'wrong inventory pin')
    require(manifest['baseline_commit'] == baseline['source_commit'] == inventory['source_commit'], 'wrong baseline anchor')
    _keys(manifest['source_contract'], ['path', 'sha256'], 'source contract')
    _path(manifest['source_contract']['path']); _digest(manifest['source_contract']['sha256'])
    require(manifest['source_contract'] == reviewed_scope['source_contract'], 'source contract differs from reviewed scope')
    _keys(manifest['audit_digests'], ['source_input_sha256', 'review_result_sha256'], 'audit digests')
    for digest in manifest['audit_digests'].values():
        _digest(digest)
    require(manifest['audit_digests'] == reviewed_scope['audit_digests'], 'review audit differs')
    require(manifest['deleted_existing'] == [], 'deletion is not an append')
    changed = manifest['changed_existing']
    require(type(changed) is dict and set(changed) <= MUTABLE_ENDPOINTS, 'unapproved changed endpoint')
    for rel, endpoint in changed.items():
        _path(rel); _endpoint(endpoint, changed=True)
        require(rel in inventory['files'] and endpoint['before_sha256'] == inventory['files'][rel]['sha256'], 'before endpoint differs from frozen inventory')
    added = manifest['allowed_added_outputs']
    require(type(added) is dict, 'added outputs must be a mapping')
    require(set(added) == set(reviewed_scope['added_output_paths']), 'added outputs differ from reviewed scope')
    for rel, endpoint in added.items():
        _path(rel); _endpoint(endpoint)
        require(rel not in inventory['files'], 'added output already exists')
    added_code = manifest['implementation_added_files']
    require(type(added_code) is list and len(added_code) == len(set(added_code)) and set(added_code) == set(implementation_added_files), 'implementation additions differ from reviewed patch')
    for rel in added_code:
        _path(rel)
        require(rel not in inventory['files'] and rel not in added, 'invalid implementation addition')
    modified_code = manifest['implementation_modified_files']
    require(type(modified_code) is dict and set(modified_code) == set(implementation_modified_files), 'implementation edits differ from reviewed patch')
    for rel, endpoint in modified_code.items():
        _keys(endpoint, ['before_sha256'], 'implementation edit')
        require(rel in inventory['files'] and endpoint['before_sha256'] == inventory['files'][rel]['sha256'], 'implementation before hash differs')
    return manifest


def expected_file_inventory(manifest, inventory):
    """No code after-hashes: that would introduce the manifest/loader SHA cycle."""
    expected = copy.deepcopy(inventory['files'])
    for rel, item in manifest['changed_existing'].items():
        expected[rel] = {'bytes': item['byte_length'], 'sha256': item['after_sha256']}
    for rel, item in manifest['allowed_added_outputs'].items():
        expected[rel] = {'bytes': item['byte_length'], 'sha256': item['sha256']}
    for rel in manifest['implementation_added_files']:
        expected[rel] = None
    for rel in manifest['implementation_modified_files']:
        expected[rel] = None
    return expected


def validate_tree(root, manifest, inventory):
    """Check complete public paths and bytes, not a subset/glob allowlist."""
    root = Path(root)
    actual = {}
    for path in root.rglob('*'):
        rel = path.relative_to(root)
        if any(part in {'.git', '__pycache__', 'node_modules', '.pytest_cache'} for part in rel.parts):
            continue
        require(not path.is_symlink(), 'symlink in candidate: ' + rel.as_posix())
        if path.is_file():
            raw = path.read_bytes()
            actual[rel.as_posix()] = {'bytes': len(raw), 'sha256': sha256(raw)}
    expected = expected_file_inventory(manifest, inventory)
    require(set(actual) == set(expected), 'candidate file set differs: ' + str(sorted(set(actual) ^ set(expected))))
    for rel, item in expected.items():
        if item is not None:
            require(actual[rel] == item, 'candidate endpoint bytes differ: ' + rel)
    changed = {rel for rel, item in inventory['files'].items()
               if rel not in manifest['implementation_modified_files'] and actual[rel] != item}
    require(changed == set(manifest['changed_existing']), 'actual changed set differs')
    return actual


def load_current_append_manifest():
    path = ROOT / APPEND_MANIFEST_PATH
    if APPEND_MANIFEST_SHA256 is None:
        require(not path.exists(), 'append manifest is present but has no reviewed static pin')
        return None
    raw = path.read_bytes()
    pinned = pinned_json(raw, APPEND_MANIFEST_SHA256)
    source_ref = pinned['source_contract']
    _keys(source_ref, ['path', 'sha256'], 'source contract')
    require(source_ref['path'] == SOURCE_CONTRACT_PATH, 'unexpected source contract path')
    source = pinned_json((ROOT / SOURCE_CONTRACT_PATH).read_bytes(), source_ref['sha256'])
    require(source['source_fixture']['path'] == SOURCE_FIXTURE_PATH, 'unexpected reviewed source fixture path')
    pinned_json((ROOT / SOURCE_FIXTURE_PATH).read_bytes(), source['source_fixture']['sha256'])
    scope = reviewed_scope_from_contract(source, source_ref, pinned['audit_digests'])
    return validate_append_manifest(raw, APPEND_MANIFEST_SHA256, baseline=load_baseline(),
                                    inventory=load_inventory(), reviewed_scope=scope)


def endpoint_sha256(rel, historical_sha256):
    """Central old-test I/O seam. Without reviewed append, retain exact old pin."""
    manifest = load_current_append_manifest()
    if manifest and rel in manifest['changed_existing']:
        return manifest['changed_existing'][rel]['after_sha256']
    return historical_sha256


def workbook_endpoints(historical):
    inventory = load_inventory()['files']
    frozen = {rel: item['sha256'] for rel, item in inventory.items()
              if rel.startswith('site/exports/') and rel.endswith('.xlsx')}
    require(historical == frozen, 'old workbook expectations differ from frozen 132-file inventory')
    manifest = load_current_append_manifest()
    expected = {rel: endpoint_sha256(rel, digest) for rel, digest in historical.items()}
    if manifest:
        expected.update({rel: item['sha256'] for rel, item in manifest['allowed_added_outputs'].items()
                         if rel.startswith('site/exports/') and rel.endswith('.xlsx')})
    return expected


def validate_reviewed_suffixes(live_files, reviewed_scope):
    """New facts are exact reviewed suffixes, not mere counts or ID membership.

    The independent source contract pins every list (including empty suffixes).
    Leaf/source normalization checks remain in the batch's source-contract tests.
    """
    baseline = load_baseline()
    require(set(live_files) == set(baseline['files']), 'missing/unknown live JSON domain')
    require(set(reviewed_scope['file_suffixes']) == set(baseline['files']), 'missing/unknown reviewed suffix domain')
    suffixes = {}
    for rel, spec in baseline['files'].items():
        public_append_view(live_files[rel], rel)
        suffix_spec = reviewed_scope['file_suffixes'][rel]
        require(set(suffix_spec) == set(spec['lists']), 'missing/unknown reviewed suffix list')
        suffixes[rel] = {}
        for key, frozen in spec['lists'].items():
            rows = live_files[rel][key]
            if frozen['selection'] == 'identity_set':
                old_ids = set(frozen['ordered_ids'])
                new = [row for row in rows if row[frozen['identity_key']] not in old_ids]
            else:
                new = rows[frozen['length']:]
            rule = suffix_spec[key]
            _keys(rule, ['length', 'sha256'], 'suffix')
            require(type(rule['length']) is int and rule['length'] >= 0, 'invalid suffix length')
            _digest(rule['sha256'])
            require(len(new) == rule['length'] and canonical_digest(new) == rule['sha256'], 'unreviewed suffix: ' + rel + ':' + key)
            suffixes[rel][key] = new
    people = suffixes['data/atlas.json']['people']
    departments = sorted({person['department_id'] for person in people})
    require(departments == sorted(reviewed_scope['approved_department_ids']), 'approved departments differ from source people')
    require(len(departments) == len(reviewed_scope['approved_department_ids']), 'duplicate approved department')
    require(all(type(item) is str and _ID.fullmatch(item) for item in departments), 'invalid approved department ID')
    old_departments = set(baseline['files']['site/atlas.json']['lists']['exports']['ordered_ids'])
    # This initial contract intentionally supports only genuinely new departments.
    require(not (set(departments) & old_departments), 'existing department append requires separately reviewed export projection')
    new_exports = suffixes['site/atlas.json']['exports']
    require({row['department_id'] for row in new_exports} == set(departments), 'exports differ from reviewed departments')
    held = set(reviewed_scope['held_school_ids'])
    for rel, lists in suffixes.items():
        for key in ('people', 'pending_people', 'org_units', 'entries', 'source_observations'):
            for row in lists.get(key, []):
                require(row.get('school_id') not in held, 'held school promoted in new scope')
    orgs = {row['id']: row for row in live_files['data/atlas.json']['org_units']}
    for person in people:
        require(person['department_id'] in orgs and orgs[person['department_id']]['school_id'] == person['school_id'], 'new person department/school mismatch')
    require(live_files['data/atlas.json']['people'] == live_files['site/atlas.json']['people'], 'canonical/site people mismatch')
    require(live_files['data/atlas.json']['pending_people'] == live_files['site/atlas.json']['pending_people'], 'canonical/site pending mismatch')
    require(live_files['site/atlas.json']['build_id'] == live_files['site/rosters.json']['build_id'], 'live build IDs differ')
    return suffixes


def reviewed_scope_from_contract(contract, source_ref, audit_digests):
    """Adapt pinned, independently reviewed source scope, never the live tree."""
    baseline = load_baseline()
    inventory = load_inventory()['files']
    require(contract['baseline_commit'] == baseline['source_commit'], 'source contract baseline differs')
    scope = contract['append_scope']
    _keys(scope, ['approved_department_ids', 'added_report_paths', 'added_context_paths',
                  'file_suffixes', 'derived_site_expectation'], 'reviewed append scope')
    departments = scope['approved_department_ids']
    require(type(departments) is list and all(type(item) is str and _ID.fullmatch(item) for item in departments), 'invalid reviewed department IDs')
    require(len(departments) == len(set(departments)), 'duplicate reviewed department')
    old_departments = set(baseline['files']['site/atlas.json']['lists']['exports']['ordered_ids'])
    require(not (set(departments) & old_departments), 'existing department append needs a different reviewed projection')
    reports, contexts = scope['added_report_paths'], scope['added_context_paths']
    for paths, prefix in ((reports, 'progress/'), (contexts, 'research/')):
        require(type(paths) is list and all(type(rel) is str for rel in paths), 'invalid reviewed document paths')
        require(len(paths) == len(set(paths)), 'duplicate reviewed document path')
        for rel in paths:
            _path(rel)
            require(rel.startswith(prefix) and rel.endswith('.json') and rel not in inventory, 'invalid added document namespace')
    document_paths = [row['file'] for row in contract['document_objects']]
    require(len(document_paths) == len(set(document_paths)), 'duplicate reviewed document')
    require(set(reports + contexts) == {rel for rel in document_paths if rel not in inventory}, 'new documents differ from reviewed report/context scope')
    require(type(scope['derived_site_expectation']) is str and scope['derived_site_expectation'], 'missing generated expectation provenance')
    file_suffixes = scope['file_suffixes']
    require(set(file_suffixes) == set(baseline['files']), 'source scope JSON domains differ')
    normalized = {}
    for rel, spec in baseline['files'].items():
        require(set(file_suffixes[rel]) == set(spec['lists']), 'source scope arrays differ')
        normalized[rel] = {}
        for key, frozen in spec['lists'].items():
            row = file_suffixes[rel][key]
            fields = ['baseline_length', 'length', 'sha256']
            if frozen['selection'] == 'identity_set': fields.append('mode')
            _keys(row, fields, 'source scope suffix')
            require(type(row['baseline_length']) is int and row['baseline_length'] == frozen['length'], 'source scope frozen boundary differs')
            if frozen['selection'] == 'identity_set':
                require(row['mode'] == 'new_department_rows', 'source scope export selection differs')
            require(type(row['length']) is int and row['length'] >= 0, 'source scope suffix length invalid')
            _digest(row['sha256'])
            normalized[rel][key] = {'length': row['length'], 'sha256': row['sha256']}
    held = []
    for row in contract['whole_holds']:
        require(row['whole_scope_hold'] is True and type(row['school_id']) is str, 'invalid whole-scope hold')
        held.append(row['school_id'])
    require(len(held) == len(set(held)), 'duplicate held school')
    return {'source_contract': copy.deepcopy(source_ref), 'audit_digests': copy.deepcopy(audit_digests),
            'added_output_paths': sorted(reports + contexts + ['site/exports/' + department + '.xlsx' for department in departments]),
            'file_suffixes': normalized, 'approved_department_ids': copy.deepcopy(departments),
            'held_school_ids': held}
