"""Validate a public source contract by exact JSON pointers, without network or writes."""
import argparse
import copy
import hashlib
import json
from pathlib import Path
from collections import Counter


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False)


def digest(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest()


def exact(a, b):
    return type(a) is type(b) and canonical(a) == canonical(b)


def tokens(path):
    assert isinstance(path, str) and (path == '' or path.startswith('/')), 'Invalid pointer'
    return [part.replace('~1', '/').replace('~0', '~') for part in path.split('/')[1:]]


def pointer(value, path):
    for key in tokens(path):
        if isinstance(value, list):
            assert key.isdigit() and str(int(key)) == key, 'Noncanonical array index'
            value = value[int(key)]
        else:
            value = value[key]
    return value


def assign(value, path, item, *, absent=False):
    parts = tokens(path)
    assert parts, 'Root replacement not permitted'
    parent = value
    for key in parts[:-1]:
        parent = parent[int(key)] if isinstance(parent, list) else parent[key]
    key = parts[-1]
    if isinstance(parent, list):
        assert not absent, 'Array insertion not permitted'
        parent[int(key)] = copy.deepcopy(item)
    else:
        assert (key not in parent) if absent else (key in parent), 'Unexpected field presence'
        parent[key] = copy.deepcopy(item)


def leaves(value, path=''):
    """Empty containers are leaves too: deleting an empty fact must fail."""
    if isinstance(value, dict) and value:
        for key, item in value.items():
            yield from leaves(item, path + '/' + str(key).replace('~', '~0').replace('/', '~1'))
    elif isinstance(value, list) and value:
        for index, item in enumerate(value):
            yield from leaves(item, path + '/' + str(index))
    else:
        yield path, value


def added_fields(original, target, path=''):
    rows = []
    if isinstance(original, dict) and isinstance(target, dict):
        for key, value in target.items():
            loc = path + '/' + key.replace('~', '~0').replace('/', '~1')
            if key not in original:
                rows.append({'path': loc, 'value': copy.deepcopy(value), 'before_exists': False})
            else:
                rows.extend(added_fields(original[key], value, loc))
    elif isinstance(original, list) and isinstance(target, list):
        assert len(original) == len(target), 'Original source array length changed'
        for index, (left, right) in enumerate(zip(original, target)):
            rows.extend(added_fields(left, right, path + '/' + str(index)))
    return rows


def replay(original, binding):
    expected = copy.deepcopy(original)
    additions = binding.get('additions', [])
    assert len({r['path'] for r in additions}) == len(additions), 'Duplicate addition'
    for row in additions:
        assert row['before_exists'] is False, 'Additions require explicit absence'
        assign(expected, row['path'], row['value'], absent=True)
    rules = binding.get('normalizations', [])
    assert len({r['path'] for r in rules}) == len(rules), 'Duplicate normalization'
    for row in rules:
        assert row['path'] and row['preserved_at'] and row['reason'], 'Incomplete normalization'
        assert row['path'] != row['preserved_at'], 'Preservation cannot point to overwritten field'
        assert not set(tokens(row['path'])) & {'degree_awarded', 'event_kind', 'start', 'end', 'degree_awarded_date', 'institution_985', 'region', 'continent_code', 'current', 'employment_status'}, 'Fact-changing normalization prohibited'
        assert exact(pointer(original, row['path']), row['before']), 'Normalization before differs'
        assert exact(pointer(expected, row['preserved_at']), row['before']), 'Original value not preserved'
        assign(expected, row['path'], row['after'])
    return expected


def source_closure(person):
    sources = person['sources']
    known = {s['id']: s['url'] for s in sources}
    assert len(known) == len(sources), 'Duplicate source IDs'
    events = {e['event_id'] for e in person['education']}
    assert len(events) == len(person['education']), 'Duplicate education event IDs'
    def walk(value):
        if isinstance(value, dict):
            for key, ref in value.items():
                if (key == 'source_id' or key.endswith('_source_id')) and ref is not None:
                    urlkey = key[:-3] + '_url'
                    if urlkey in value:
                        assert known.get(ref) == value[urlkey], 'Source ID and URL disagree'
            for key, item in value.items():
                if key in ('field_provenance', 'professional_field_provenance'):
                    for ref in item.values():
                        assert ref is None or isinstance(ref, str) and ref in known or isinstance(ref, list) and all(x in known for x in ref), 'Unclosed field provenance'
                    continue
                if key == 'field_status':
                    continue
                if (key == 'source_id' or key.endswith('_source_id')) and item is not None:
                    assert isinstance(item, str) and item in known, 'Unclosed source ID'
                if (key == 'source_ids' or key.endswith('_source_ids')) and item is not None:
                    assert isinstance(item, list) and all(x in known for x in item), 'Unclosed source IDs'
                if key == 'education_event_id' and item is not None:
                    assert item in events, 'Unclosed education event'
                walk(item)
        elif isinstance(value, list):
            for item in value:
                walk(item)
    walk(person)
    for event in person['education']:
        assert event['degree_awarded'] is None or type(event['degree_awarded']) is bool
        assert event['degree_awarded'] is not True or event['event_kind'] == 'degree'
        if event['degree_awarded'] is not True:
            assert event.get('include_in_degree_filters') is False and event.get('include_in_education_filters') is False
    assert person['employment_status'] == 'unknown'
    assert person['quick_link_eligible'] is False and person['include_in_current_faculty_count'] is False


def validate_contract(root, contract_path, *, check_generated=False, expected_contract_sha256=None):
    root = Path(root)
    def load(rel):
        path = root / rel
        assert path.resolve().is_relative_to(root.resolve()), 'File outside root'
        return json.loads(path.read_text())
    if expected_contract_sha256 is not None:
        assert hashlib.sha256((root / contract_path).read_bytes()).hexdigest() == expected_contract_sha256, 'Frozen contract bytes changed'
    contract = load(contract_path)
    fixture = load(contract['source_fixture']['path'])
    assert hashlib.sha256((root / contract['source_fixture']['path']).read_bytes()).hexdigest() == contract['source_fixture']['sha256'], 'Source fixture bytes changed'
    assert contract['source_fixture']['hash_scope'] == 'public_structured_source_fixture_bytes_not_webpage_bytes'
    for spec in contract['source_packages']:
        raw = pointer(fixture, spec['pointer'])
        assert digest(raw) == spec['canonical_sha256'], 'Original package object changed'
        assert spec['audit_sha256_scope'] == 'approved_research_package_file_bytes_not_webpage_bytes'
    covered = set()
    cache = {}
    for obj in contract['objects']:
        original = pointer(fixture, obj['source']['pointer'])
        cache.setdefault(obj['target']['file'], load(obj['target']['file']))
        actual = pointer(cache[obj['target']['file']], obj['target']['pointer'])
        assert digest(original) == obj['source_object_sha256'], 'Source object digest changed'
        assert exact(replay(original, obj), actual), 'Unlisted change or dropped field: ' + obj['id']
        covered.update(obj['source']['pointer'] + loc for loc, _ in leaves(original))
    expected = {path for path, _ in leaves(fixture['packages'], '/packages')}
    assert expected <= covered, 'Original package values not all bound: ' + str(sorted(expected - covered)[:5])
    atlas = cache.get('data/atlas.json') or load('data/atlas.json')
    rosters = cache.get('data/rosters.json') or load('data/rosters.json')
    for spec in contract['new_collections']:
        current = cache.get(spec['file']) or load(spec['file'])
        values = pointer(current, spec['pointer'])
        suffix = values[spec['baseline_length']:]
        assert len(suffix) == spec['length'] and digest(suffix) == spec['sha256'], 'Unapproved appended collection'
        assert digest(values[:spec['baseline_length']]) == spec['baseline_sha256'], 'Historical prefix changed'
    for doc in contract['document_objects']:
        assert digest(load(doc['file'])) == doc['canonical_sha256'], 'Frozen document differs: ' + doc['file']
    assert sorted(x['file'] for x in contract['document_objects'] if x['file'].startswith('research/')) == contract['append_scope']['added_context_paths'], 'Context scope differs'
    approved_ids = []
    for selected in contract['selection']:
        people = [p for p in atlas['people'] if p.get('data_batch_id') in selected['profile_batch_ids']]
        assert [p['person_id'] for p in people] == selected['person_ids'], 'Original selection order changed'
        assert [p['roster_entry_id'] for p in people] == selected['roster_entry_ids']
        assert [p['selection_order'] for p in people] == list(range(1, len(people) + 1))
        for person in people:
            source_closure(person)
        approved_ids.extend(selected['person_ids'])
    for held in contract['whole_holds']:
        assert not held['selected_person_ids'] and not held['selected_roster_entry_ids']
        for spec in contract['new_collections']:
            current = cache.get(spec['file']) or load(spec['file'])
            suffix = pointer(current, spec['pointer'])[spec['baseline_length']:]
            if spec['file'] == 'data/atlas.json' and spec['pointer'] in ('/people', '/pending_people', '/org_units') or spec['file'] == 'data/rosters.json' and spec['pointer'] in ('/entries', '/source_observations'):
                assert not any(x.get('school_id') == held['school_id'] for x in suffix), 'Whole-scope hold gained records'
    approved_people = [p for p in atlas['people'] if p['person_id'] in approved_ids]
    counts = Counter({key: sum(len(p.get(key, [])) for p in approved_people) for key in ('education', 'appointments', 'mentors', 'committee_members', 'publications', 'teaching', 'research_fields', 'professional_qualifications')})
    suffix_lookup = {(x['file'], x['pointer']): x['length'] for x in contract['new_collections']}
    counts.update(people=len(approved_people), pending_people=suffix_lookup[('data/atlas.json','/pending_people')], org_units=suffix_lookup[('data/atlas.json','/org_units')], roster_entries=suffix_lookup[('data/rosters.json','/entries')], source_observations=suffix_lookup[('data/rosters.json','/source_observations')], held_scopes=len(contract['whole_holds']), held_candidates=0)
    for state, suffix in ((True,'true'),(False,'false'),(None,'null')):
        counts['degree_awarded_' + suffix] = sum(e['degree_awarded'] is state for p in approved_people for e in p['education'])
    assert exact(dict(counts), contract['collection_counts']), 'Derived counts differ'
    reports = sorted(x['file'] for x in contract['document_objects'] if x['file'].startswith('progress/') and x['file'] != 'progress/work-queue.json')
    assert reports == contract['append_scope']['added_report_paths'], 'Report scope differs'
    departments = sorted({p['department_id'] for p in approved_people})
    assert departments == contract['append_scope']['approved_department_ids']
    for file, collections in contract['append_scope']['file_suffixes'].items():
        if file.startswith('site/') and not check_generated:
            continue
        current = load(file)
        assert set(collections) == {k for k, value in current.items() if isinstance(value, list)}, 'Unbounded root array'
        for key, row in collections.items():
            values = current[key]
            if row.get('mode') == 'new_department_rows':
                suffix = [x for x in values if x['department_id'] in departments]
            else:
                suffix = values[row['baseline_length']:]
            assert len(suffix) == row['length'] and digest(suffix) == row['sha256'], 'Append-scope suffix differs'
    return {'status': 'passed', 'bound_objects': len(contract['objects']), 'source_leaf_values_bound': len(expected), 'normalizations': sum(len(x['normalizations']) for x in contract['objects']), 'new_people': len(approved_ids), 'generated_checked': check_generated}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('contract')
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--check-generated', action='store_true')
    args = parser.parse_args()
    print(json.dumps(validate_contract(args.root, args.contract, check_generated=args.check_generated), ensure_ascii=False))
