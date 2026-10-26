"""Strict versioned school-part transport; business facts and their order are untouched."""
import hashlib
import json
import math
import os
from pathlib import Path
import re
import tempfile

FORMAT = 'academic-atlas-school-parts-v1'
BUILD_VERSION = b'academic-atlas-build-school-parts-v1\0'
MAX_MANIFEST_BYTES = 16 * 1024 * 1024
MAX_PART_BYTES = 16 * 1024 * 1024
MAX_TOTAL_BYTES = 128 * 1024 * 1024
MAX_PARTS = 1024
MAX_PEOPLE = 100000
SCHOOL_ID = re.compile(r'[a-z][a-z0-9-]{0,63}\Z')
BUILD_FILES = ('data/rosters.json', 'scripts/build.py', 'scripts/build_rosters.py',
               'scripts/deterministic_xlsx.py', 'scripts/atlas_storage.py', 'site/atlas-loader.js')


def _require(ok, message):
    if not ok:
        raise ValueError(message)


def _pairs(pairs):
    result = {}
    for key, value in pairs:
        _require(key not in result, 'Duplicate JSON key: ' + key)
        result[key] = value
    return result


def _finite(value, depth=0):
    _require(depth <= 512, 'JSON nesting bound exceeded')
    if isinstance(value, dict):
        for key, item in value.items():
            _require(isinstance(key, str), 'JSON object key must be string')
            key.encode('utf-8')
            _finite(item, depth + 1)
    elif isinstance(value, list):
        for item in value:
            _finite(item, depth + 1)
    elif isinstance(value, str):
        value.encode('utf-8')
    elif isinstance(value, float):
        _require(math.isfinite(value), 'Nonfinite JSON number')
    else:
        _require(value is None or type(value) in (bool, int), 'Non-JSON value')


def strict_json(raw):
    """Decode original UTF-8 bytes, rejecting BOM, duplicates and nonfinite numbers."""
    _require(isinstance(raw, bytes), 'JSON input must be bytes')
    _require(not raw.startswith(b'\xef\xbb\xbf'), 'UTF-8 BOM is forbidden')
    def reject(value):
        raise ValueError('Nonfinite JSON constant: ' + value)
    try:
        value = json.loads(raw.decode('utf-8', errors='strict'), object_pairs_hook=_pairs,
                           parse_constant=reject)
        _finite(value)
        return value
    except (UnicodeError, RecursionError) as exc:
        raise ValueError('Invalid UTF-8/JSON nesting') from exc


def compact_bytes(value):
    _finite(value)
    return (json.dumps(value, ensure_ascii=False, separators=(',', ':'), allow_nan=False) + '\n').encode('utf-8')


def _shape(value, keys, label):
    _require(isinstance(value, dict) and set(value) == set(keys), 'Invalid ' + label + ' shape')


def _id(value):
    return isinstance(value, str) and SCHOOL_ID.fullmatch(value) is not None


def _person_id(value):
    return isinstance(value, str) and 0 < len(value) <= 256


def _integer(value, low, high):
    return type(value) is int and low <= value <= high


def validate_manifest(manifest):
    _shape(manifest, ('format', 'atlas', 'people_order', 'parts'), 'manifest')
    _require(manifest['format'] == FORMAT, 'Unsupported atlas transport format')
    atlas = manifest['atlas']
    _require(isinstance(atlas, dict) and atlas.get('people') == [] and type(atlas.get('people')) is list,
             'Manifest atlas.people must be empty')
    institutions = atlas.get('institutions')
    _require(isinstance(institutions, list), 'Missing institutions')
    schools = set()
    for row in institutions:
        _require(isinstance(row, dict) and _id(row.get('id')), 'Invalid institution ID')
        _require(row['id'] not in schools, 'Duplicate institution ID')
        schools.add(row['id'])
    order, parts = manifest['people_order'], manifest['parts']
    _require(isinstance(order, list) and len(order) <= MAX_PEOPLE, 'Invalid people_order')
    _require(all(_person_id(x) for x in order), 'Invalid person ID')
    _require(len(order) == len(set(order)), 'Duplicate people_order ID')
    _require(isinstance(parts, list) and len(parts) <= MAX_PARTS, 'Invalid parts')
    seen = set()
    for part in parts:
        _shape(part, ('school_id', 'path', 'sha256', 'bytes', 'count'), 'part entry')
        sid = part['school_id']
        _require(_id(sid) and sid in schools and sid not in seen, 'Unknown/duplicate part school')
        seen.add(sid)
        _require(part['path'] == 'people/' + sid + '.json', 'Unsafe part path')
        _require(isinstance(part['sha256'], str) and re.fullmatch('[0-9a-f]{64}', part['sha256']) is not None,
                 'Invalid part SHA256')
        _require(_integer(part['bytes'], 1, MAX_PART_BYTES), 'Invalid part byte bound')
        _require(_integer(part['count'], 1, MAX_PEOPLE), 'Invalid part count')
    _require(sum(p['count'] for p in parts) == len(order), 'Part counts/order length mismatch')
    _require(sum(p['bytes'] for p in parts) <= MAX_TOTAL_BYTES, 'Total part byte bound exceeded')
    return manifest


def assemble_atlas(manifest, parsed_parts):
    validate_manifest(manifest)
    _require(isinstance(parsed_parts, list) and len(parsed_parts) == len(manifest['parts']), 'Missing/extra parts')
    people = {}
    part_ids = []
    for spec, chunk in zip(manifest['parts'], parsed_parts):
        _shape(chunk, ('school_id', 'people'), 'chunk')
        _require(chunk['school_id'] == spec['school_id'], 'Chunk school mismatch')
        rows = chunk['people']
        _require(isinstance(rows, list) and len(rows) == spec['count'], 'Chunk count mismatch')
        ids = []
        for person in rows:
            _require(isinstance(person, dict), 'Invalid person object')
            pid = person.get('person_id')
            _require(_person_id(pid) and pid not in people, 'Invalid/duplicate person ID')
            _require(person.get('school_id') == spec['school_id'], 'Foreign-school person')
            people[pid] = person
            ids.append(pid)
        part_ids.append(ids)
    order = manifest['people_order']
    _require(set(order) == set(people), 'Missing/extra people_order ID')
    first_schools = list(dict.fromkeys(people[pid]['school_id'] for pid in order))
    _require(first_schools == [p['school_id'] for p in manifest['parts']], 'Parts not in first-school appearance order')
    for spec, ids in zip(manifest['parts'], part_ids):
        _require(ids == [pid for pid in order if people[pid]['school_id'] == spec['school_id']],
                 'Chunk relative person order mismatch')
    result = dict(manifest['atlas'])
    result['people'] = [people[pid] for pid in order]
    return result


def _safe_path(path):
    path = Path(os.path.abspath(os.fspath(path)))
    for item in (path, *path.parents):
        _require(not item.is_symlink(), 'Symlink is forbidden: ' + str(item))
    return path


def _read(path, limit):
    path = _safe_path(path)
    _require(path.is_file(), 'Missing regular file: ' + str(path))
    _require(path.stat().st_size <= limit, 'File byte bound exceeded')
    with path.open('rb') as handle:
        raw = handle.read(limit + 1)
    _require(len(raw) <= limit, 'File byte bound exceeded')
    return raw


def _read_storage(path):
    path = _safe_path(path)
    raw = _read(path, MAX_MANIFEST_BYTES)
    manifest = validate_manifest(strict_json(raw))
    directory = _safe_path(path.parent / 'people')
    expected = {Path(p['path']).name for p in manifest['parts']}
    if directory.exists():
        _require(directory.is_dir(), 'people must be a directory')
        entries = list(directory.iterdir())
        _require(all(not p.is_symlink() and p.is_file() for p in entries), 'Nonregular school part')
        _require({p.name for p in entries} == expected, 'Orphan/missing school part')
    else:
        _require(not expected, 'Missing people directory')
    inputs = [(path.name, raw)]
    parsed = []
    total = len(raw)
    for part in manifest['parts']:
        file = _safe_path(path.parent / part['path'])
        _require(file.parent == directory, 'Part outside storage directory')
        chunk = _read(file, MAX_PART_BYTES)
        _require(len(chunk) == part['bytes'], 'Part byte length mismatch')
        _require(hashlib.sha256(chunk).hexdigest() == part['sha256'], 'Part SHA256 mismatch')
        total += len(chunk)
        _require(total <= MAX_TOTAL_BYTES, 'Total storage byte bound exceeded')
        parsed.append(strict_json(chunk))
        inputs.append((part['path'], chunk))
    return assemble_atlas(manifest, parsed), inputs


def load_atlas(path):
    return _read_storage(path)[0]


def storage_inputs(path):
    """Ordered (manifest filename / relative chunk path, validated original bytes)."""
    return _read_storage(path)[1]


def _atomic_write(path, raw):
    path = _safe_path(path)
    fd, temporary = tempfile.mkstemp(prefix='.atlas-write-', dir=path.parent)
    try:
        with os.fdopen(fd, 'wb') as handle:
            handle.write(raw)
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def write_atlas(path, data):
    """Write compact stable chunks then manifest; manages only safe school JSON files."""
    path = _safe_path(path)
    _require(isinstance(data, dict) and isinstance(data.get('people'), list), 'Invalid business atlas')
    _require(len(data['people']) <= MAX_PEOPLE, 'Too many people')
    grouped = {}
    order = []
    for person in data['people']:
        _require(isinstance(person, dict) and _id(person.get('school_id')), 'Invalid person school')
        grouped.setdefault(person['school_id'], []).append(person)
        order.append(person.get('person_id'))
    root = dict(data)
    root['people'] = []
    parts, blobs, parsed = [], {}, []
    for sid, people in grouped.items():
        chunk = {'school_id': sid, 'people': people}
        raw = compact_bytes(chunk)
        name = 'people/' + sid + '.json'
        blobs[name] = raw
        parsed.append(chunk)
        parts.append({'school_id': sid, 'path': name, 'sha256': hashlib.sha256(raw).hexdigest(),
                      'bytes': len(raw), 'count': len(people)})
    manifest = {'format': FORMAT, 'atlas': root, 'people_order': order, 'parts': parts}
    assemble_atlas(manifest, parsed)
    raw = compact_bytes(manifest)
    _require(len(raw) <= MAX_MANIFEST_BYTES and len(raw) + sum(map(len, blobs.values())) <= MAX_TOTAL_BYTES,
             'Storage byte bound exceeded')
    directory = _safe_path(path.parent / 'people')
    old_files = []
    if directory.exists():
        _require(directory.is_dir(), 'people must be directory')
        old_files = list(directory.iterdir())
        _require(all(not p.is_symlink() and p.is_file() and p.suffix == '.json' and _id(p.stem)
                     for p in old_files), 'Unmanaged file in people directory')
    path.parent.mkdir(parents=True, exist_ok=True)
    directory.mkdir(exist_ok=True)
    for name, blob in blobs.items():
        _atomic_write(path.parent / name, blob)
    for file in old_files:
        if 'people/' + file.name not in blobs:
            file.unlink()
    _atomic_write(path, raw)
    return manifest


def compute_build_id(root):
    root = _safe_path(root)
    inputs = [('data/' + label, raw) for label, raw in storage_inputs(root / 'data/atlas.json')]
    inputs += [(label, _read(root / label, MAX_TOTAL_BYTES)) for label in BUILD_FILES]
    digest = hashlib.sha256(BUILD_VERSION)
    for label, raw in inputs:
        name = label.encode('utf-8')
        digest.update(len(name).to_bytes(8, 'big'))
        digest.update(name)
        digest.update(len(raw).to_bytes(8, 'big'))
        digest.update(raw)
    return digest.hexdigest()[:16]
