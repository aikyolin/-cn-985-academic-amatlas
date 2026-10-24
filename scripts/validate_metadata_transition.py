"""Exact, reversible metadata transitions. No network, source rewriting, or inferred suffixes."""
import copy
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import re
from zipfile import ZipFile, ZIP_DEFLATED
from xml.sax.saxutils import escape
import xml.etree.ElementTree as ET


def require(value, message):
    if not value:
        raise ValueError(message)


def sha256(raw):
    return hashlib.sha256(raw).hexdigest()


def keys(value, expected, label):
    require(type(value) is dict and set(value) == set(expected), 'Unknown/missing ' + label + ' fields')


def safe_path(rel):
    require(type(rel) is str and rel and '\\' not in rel and not rel.startswith('/'), 'Invalid path')
    require(str(PurePosixPath(rel)) == rel and not any(x in {'.', '..'} for x in rel.split('/')), 'Unsafe path')
    return rel


def pinned_json(raw, pin):
    require(type(pin) is str and re.fullmatch('[0-9a-f]{64}', pin), 'Missing independent pin')
    require(sha256(raw) == pin, 'Pinned bytes changed')
    def pairs(rows):
        result = {}
        for key, value in rows:
            require(key not in result, 'Duplicate JSON key')
            result[key] = value
        return result
    return json.loads(raw, object_pairs_hook=pairs, parse_constant=lambda _: require(False, 'Non-JSON number'))


def reverse_text(raw, spec):
    require(sha256(raw) == spec['after_sha256'] and len(raw) == spec['byte_length'], 'Unreviewed current endpoint')
    result = raw
    last = len(raw) + 1
    for op in reversed(spec['patches']):
        keys(op, ['after_offset', 'before', 'after'], 'text patch')
        offset = op['after_offset']; before = op['before'].encode(); after = op['after'].encode()
        require(type(offset) is int and 0 <= offset <= len(raw) and offset + len(after) <= last, 'Overlapping/invalid text patch')
        require(raw[offset:offset + len(after)] == after, 'Current text patch differs')
        result = result[:offset] + before + result[offset + len(after):]
        last = offset
    require(sha256(result) == spec['before_sha256'], 'Historical source bytes changed')
    return result


def reverse_workbook(raw, spec):
    require(sha256(raw) == spec['after_sha256'] and len(raw) == spec['byte_length'], 'Unreviewed workbook endpoint')
    output = io.BytesIO()
    with ZipFile(io.BytesIO(raw)) as source, ZipFile(output, 'w', ZIP_DEFLATED, compresslevel=9) as target:
        names = source.namelist()
        require(len(names) == len(set(names)), 'Duplicate workbook ZIP member')
        require(set(spec['members']) <= set(names), 'Missing changed workbook member')
        for info in source.infolist():
            value = source.read(info.filename)
            if info.filename in spec['members']:
                member = spec['members'][info.filename]
                require(sha256(value) == member['after_sha256'], 'Unreviewed worksheet XML')
                for operation in reversed(member['replacements']):
                    after = operation['after'].encode(); before = operation['before'].encode()
                    require(value.count(after) == 1, 'Missing/ambiguous approved XML replacement')
                    value = value.replace(after, before)
                require(sha256(value) == member['before_sha256'], 'Non-whitelisted worksheet change')
            target.writestr(copy.copy(info), value, compress_type=info.compress_type, compresslevel=9)
    restored = output.getvalue()
    require(sha256(restored) == spec['before_sha256'], 'Workbook structure, styles, relations or other cells changed')
    return restored


def validate_policy(policy, baseline):
    keys(policy, ['version', 'baseline_commit', 'baseline_url', 'hash_scope', 'canonical_inputs', 'rules', 'workbooks', 'change_counts'], 'metadata policy')
    require(policy['version'] == 'source_date_metadata_policy_v1', 'Wrong metadata policy')
    require(policy['baseline_commit'] == baseline['source_commit'], 'Policy anchor differs')
    require(set(policy['canonical_inputs']) == {'data/atlas.json', 'data/rosters.json'}, 'Canonical input scope differs')
    for rel, digest in policy['canonical_inputs'].items():
        require(digest == baseline['files'][rel]['sha256'], 'Canonical input pin differs')
    expected = {rel for rel in baseline['files'] if rel.startswith('site/exports/') and rel.endswith('.xlsx') and rel != 'site/exports/待核对名录.xlsx'}
    require(set(policy['workbooks']) == expected, 'Workbook policy scope differs')
    require(policy['rules'] == {
        'overview_header': {'before': '核对日期', 'after': '已记录来源检索日期'},
        'overall_review_suffix': '；人物整体核验日期未单独记录',
        'classification_unrecorded': '未单独记录',
        'availability': {'before': '公开个人页（时效以核对日为准）', 'after': '公开个人页（访问与内容时效见来源记录）'},
    }, 'Metadata semantics differ from approved maintenance')
    for rel, workbook in policy['workbooks'].items():
        safe_path(rel)
        require(workbook['before_sha256'] == baseline['files'][rel]['sha256'], 'Workbook baseline differs')
        require(set(workbook['members']) <= {'xl/worksheets/sheet1.xml', 'xl/worksheets/sheet5.xml'}, 'Unapproved worksheet')
        for member, item in workbook['members'].items():
            for op in item['replacements']:
                kind = op['kind']; cell = op.get('cell', '')
                if kind == 'derived_column_width':
                    keys(op, ['kind', 'column', 'before', 'after'], 'width operation')
                    require(member.endswith('sheet1.xml') and op['column'] in {'G', 'H'}, 'Unapproved width')
                    for xml in (op['before'], op['after']):
                        element = ET.fromstring(xml)
                        require(element.tag == 'col' and list(element) == [] and element.attrib.get('min') == element.attrib.get('max') == str(ord(op['column']) - 64), 'Width operation targets another column')
                        require(0 < float(element.attrib['width']) <= 65, 'Invalid derived width')
                    require(re.sub(r'width="[^"]+"', 'width="*"', op['before']) == re.sub(r'width="[^"]+"', 'width="*"', op['after']), 'Width operation changes non-width data')
                    continue
                require(op['sheet'] == ('总览' if member.endswith('sheet1.xml') else '来源'), 'Wrong worksheet label')
                before, after = op['before_value'], op['after_value']
                require(type(before) is str and type(after) is str, 'Cell replacement changes value type')
                element = ET.fromstring(op['before'])
                require(element.tag == 'c' and element.attrib.get('r') == cell and element.attrib.get('t') == 'inlineStr', 'Operation does not target exact string cell')
                require(len(element) == 1 and element[0].tag == 'is' and len(element[0]) == 1 and element[0][0].tag == 't' and not list(element[0][0]), 'Unexpected cell structure')
                require(element[0][0].text == before, 'Cell operation before value differs from XML')
                text = re.search(r'(<t(?:\s[^>]*)?>)(.*?)(</t>)', op['before'])
                require(text is not None, 'Cell XML has no text value')
                expected_xml = op['before'][:text.start(2)] + escape(after).encode('ascii', 'xmlcharrefreplace').decode() + op['before'][text.end(2):]
                require(op['after'] == expected_xml, 'Cell operation changes non-value XML or another fact')
                if kind == 'overview_header':
                    require(op['sheet'] == '总览' and cell == 'E1' and {'before': before, 'after': after} == policy['rules'][kind], 'Unapproved header')
                elif kind == 'source_date_summary':
                    require(op['sheet'] == '总览' and re.fullmatch('E[2-9][0-9]*|E1[0-9]+', cell), 'Unapproved date cell')
                    dates = op['source_dates']
                    require(dates == sorted(set(dates)) and all(re.fullmatch(r'\d{4}-\d{2}-\d{2}', x) for x in dates), 'Invalid frozen source dates')
                    require(after == (dates[0] if len(dates) == 1 else dates[0] + ' 至 ' + dates[-1]), 'Date summary differs')
                elif kind == 'overall_review_notice':
                    require(op['sheet'] == '总览' and re.fullmatch('G[2-9][0-9]*|G1[0-9]+', cell) and after == before + policy['rules']['overall_review_suffix'], 'Unapproved overall-review notice')
                elif kind == 'availability_label':
                    rule = policy['rules']['availability']
                    require(op['sheet'] == '总览' and re.fullmatch('H[2-9][0-9]*|H1[0-9]+', cell) and before.count(rule['before']) == 1 and after == before.replace(rule['before'], rule['after']), 'Unapproved availability change')
                elif kind == 'classification_missing_date':
                    require(op['sheet'] == '来源' and re.fullmatch('E[2-9][0-9]*|E1[0-9]+', cell) and op['source_id'].startswith('institution-classification-') and after == policy['rules']['classification_unrecorded'], 'Unapproved classification change')
                else:
                    require(False, 'Unknown metadata operation')
    return policy


def validate_manifest(manifest, baseline, policy, source, *, expected_added, expected_modified, exempt):
    keys(manifest, ['version', 'baseline_commit', 'references', 'changed', 'added', 'implementation_patches', 'self_pinned_files', 'loader_integrity'], 'transition manifest')
    require(manifest['version'] == 'public_metadata_transition_v1', 'Wrong transition version')
    require(manifest['baseline_commit'] == baseline['source_commit'], 'Transition anchor differs')
    production = set(policy['workbooks']) | set(source['files'])
    require(set(source['files']) == {'site/app.js', 'site/model.js', 'site/rosters.js', 'site/index.html', 'scripts/build.py', 'site/atlas.json', 'site/rosters.json'}, 'Source transition scope differs')
    require(set(manifest['implementation_patches']) == set(expected_modified), 'Implementation edits differ')
    require(set(manifest['changed']) == production | set(expected_modified), 'Changed-file allowlist differs')
    require(set(manifest['added']) == set(expected_added) and not (set(expected_added) & set(baseline['files'])), 'Added-file allowlist differs')
    require(set(manifest['self_pinned_files']) == set(exempt) and set(exempt) <= set(expected_added), 'Self-pin scope differs')
    for rel, item in manifest['changed'].items():
        safe_path(rel)
        require(rel in baseline['files'] and item['before_sha256'] == baseline['files'][rel]['sha256'], 'Before endpoint differs')
        selected = policy['workbooks'].get(rel) or source['files'].get(rel) or manifest['implementation_patches'][rel]
        require(all(item[key] == selected[key] for key in ('before_sha256', 'after_sha256', 'byte_length')), 'Endpoint differs from pinned independent contract')
    keys(manifest['loader_integrity'], ['path', 'normalized_sha256', 'byte_length'], 'loader integrity')
    require(manifest['loader_integrity']['path'] == 'tests/source_date_history.py', 'Wrong normalized loader path')
    require(type(manifest['loader_integrity']['byte_length']) is int and manifest['loader_integrity']['byte_length'] > 0, 'Invalid loader length')
    for rel in manifest['added']:
        safe_path(rel)
    require(not ({'data/atlas.json', 'data/rosters.json', 'site/exports/待核对名录.csv', 'site/exports/待核对名录.xlsx'} & set(manifest['changed'])), 'Fact/roster mutation is not metadata maintenance')
    return manifest


def validate_tree(root, manifest, baseline, *, expected_manifest_sha256=None):
    root = Path(root)
    actual = {}
    for path in root.rglob('*'):
        rel = path.relative_to(root)
        if any(part in {'.git', '__pycache__', '.pytest_cache', 'node_modules'} for part in rel.parts):
            continue
        require(not path.is_symlink(), 'Symlink in current tree')
        if path.is_file():
            raw = path.read_bytes(); actual[rel.as_posix()] = {'bytes': len(raw), 'sha256': sha256(raw)}
    if manifest['self_pinned_files']:
        require(set(manifest['self_pinned_files']) == {'tests/fixtures/source-date-transition.json', 'tests/source_date_history.py'}, 'Unknown self-pin file')
        manifest_raw = (root / 'tests/fixtures/source-date-transition.json').read_bytes()
        pinned_json(manifest_raw, expected_manifest_sha256)
        integrity = manifest['loader_integrity']
        loader_raw = (root / integrity['path']).read_bytes()
        pattern = rb"(?m)^MANIFEST_SHA256 = '([0-9a-f]{64})'$"
        literals = list(re.finditer(pattern, loader_raw))
        require(len(literals) == 1 and literals[0].group(1).decode() == expected_manifest_sha256, 'Loader must contain exactly one matching manifest literal')
        normalized = re.sub(pattern, b"MANIFEST_SHA256 = '" + b'0' * 64 + b"'", loader_raw)
        require(len(loader_raw) == integrity['byte_length'] and sha256(normalized) == integrity['normalized_sha256'], 'Normalized loader source changed')
    expected = copy.deepcopy(baseline['files'])
    expected.update({rel: {'bytes': row['byte_length'], 'sha256': row['after_sha256']} for rel, row in manifest['changed'].items()})
    expected.update({rel: {'bytes': row['byte_length'], 'sha256': row['sha256']} for rel, row in manifest['added'].items() if rel not in manifest['self_pinned_files']})
    require(set(actual) == set(expected) | set(manifest['self_pinned_files']), 'Current full file set differs')
    for rel, row in expected.items():
        require(actual[rel] == row, 'Current final bytes differ: ' + rel)
    return actual


def historical_bytes(rel, raw, baseline, policy, source, manifest):
    require(rel in baseline['files'], 'Not a historical file')
    if rel in policy['workbooks']:
        result = reverse_workbook(raw, policy['workbooks'][rel])
    elif rel in source['files']:
        result = reverse_text(raw, source['files'][rel])
    elif rel in manifest['implementation_patches']:
        result = reverse_text(raw, manifest['implementation_patches'][rel])
    else:
        result = raw
    require(sha256(result) == baseline['files'][rel]['sha256'] and len(result) == baseline['files'][rel]['bytes'], 'Release33 historical endpoint differs: ' + rel)
    return result
