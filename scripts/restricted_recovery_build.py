"""Explicit NEW_RECOVERY driver; never calls the unrestricted build entry point.

This is not a replacement for full-suite or inherited-workbook content review.
Scope/source approvals are immutable external JSON artifacts, not CLI defaults.
"""
import argparse
import csv
import hashlib
import json
import pathlib
import os
import tempfile
import sys

import build
import build_rosters
import public_metadata as metadata
from atlas_storage import load_atlas, write_atlas, compute_build_id, storage_inputs

BASE_COMMIT = '019f6a9809011785983a2305b41b7720dc8e8b1e'
BASE_TREE = '206e0f9f8f6952146894217f8962fd9ac5e9e70f'
BASE_TREE_RECEIPT_SHA256 = 'a8ae97f2115672f5fe3ae2c36bec02a9d5d0fc61bc18633dc57b8ad03b8e4525'
APPROVED_SCHOOLS = frozenset(('bnu scu hnu dlut hust uestc tongji sdu ecnu tju muc jlu csu bit xjtu fdu nwpu ustc nwsuaf buaa cau ouc seu nju').split())
ROOT = pathlib.Path(__file__).resolve().parents[1]


def sha256(path):
    return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()


def pinned_json(path, expected_sha):
    if not isinstance(expected_sha, str) or len(expected_sha) != 64 or sha256(path) != expected_sha:
        raise ValueError('artifact SHA-256 mismatch')
    return json.loads(pathlib.Path(path).read_text())


def unique_strings(values, label):
    if not isinstance(values, list) or not values or any(not isinstance(v, str) or not v for v in values) or len(set(values)) != len(values):
        raise ValueError(label + ' must be a nonempty unique string list')
    return set(values)


def validate_scope(plan, atlas, baseline):
    if plan.get('status') != 'NEW_RECOVERY_RESTRICTED_SCOPE_APPROVED':
        raise ValueError('explicit restricted-scope approval required')
    if plan.get('base_commit') != BASE_COMMIT or plan.get('base_tree') != BASE_TREE:
        raise ValueError('wrong immutable baseline')
    schools = unique_strings(plan.get('school_ids'), 'school_ids')
    if schools != APPROVED_SCHOOLS:
        raise ValueError('school scope must equal the approved 24 schools')
    ids = plan.get('person_ids')
    unique_strings(ids, 'person_ids')
    old, people = baseline['people'], atlas['people']
    if len(old) != 1026 or len(people) != 1149 or len(ids) != 123:
        raise ValueError('expected exact 1026 + 123 population')
    if people[:1026] != old or [p['person_id'] for p in people[1026:]] != ids:
        raise ValueError('old objects/order or exact new order changed')
    if {p['school_id'] for p in people[1026:]} != schools:
        raise ValueError('new people do not cover the exact approved schools')
    # Old root facts remain unchanged; only append-only org/batch lists can grow.
    for key, value in baseline.items():
        if key == 'people':
            continue
        if key in ('org_units', 'profile_batches'):
            if atlas.get(key, [])[:len(value)] != value:
                raise ValueError('old root prefix changed: ' + key)
        elif atlas.get(key) != value:
            raise ValueError('old root value changed: ' + key)
    departments = unique_strings(plan.get('department_ids'), 'department_ids')
    actual = {p['department_id'] for p in people[1026:]}
    if departments != actual:
        raise ValueError('fixed reviewed department list does not match new people')
    exports = build.department_exports(atlas)
    selected = [e for e in exports if e['department_id'] in departments]
    if len(selected) != len(departments) or any(e['school_id'] not in schools or not e['department_id'].startswith(e['school_id'] + '-') for e in selected):
        raise ValueError('department scope is missing, ambiguous, or crosses schools')
    return exports, selected


def inheritance_catalog(tree_response):
    if tree_response.get('sha') != BASE_TREE or tree_response.get('truncated') is not False:
        raise ValueError('incomplete or wrong baseline Git tree')
    paths = {}
    for entry in tree_response['tree']:
        if entry['type'] != 'blob':
            continue
        path = entry['path']
        if path.startswith('/') or '..' in pathlib.PurePosixPath(path).parts or path in paths:
            raise ValueError('unsafe or duplicate baseline path')
        paths[path] = {'mode': entry['mode'], 'sha': entry['sha']}
    if len(paths) != 936:
        raise ValueError('incomplete baseline catalog')
    return paths


def check_materialized(root, inherited_paths, *, phase):
    """Same pure per-format checks, but inherited bytes explicitly NOT reviewed."""
    materialized = metadata.publication_files(root)
    known = frozenset(materialized | set(inherited_paths))
    errors = []
    checked = []
    for source in sorted(materialized):
        if phase == 'preflight' and source.startswith('site/'):
            continue
        path = root / source
        suffix = path.suffix.lower()
        if suffix == '.json':
            errors.extend(metadata.metadata_errors(json.loads(path.read_text()), source=source, public_files=known))
        elif suffix in {'.md', '.html', '.txt', '.yml', '.yaml'}:
            errors.extend(metadata._document_errors(path.read_text(), source, known))
        elif phase == 'final' and suffix in {'.csv', '.tsv'}:
            with path.open(newline='') as handle:
                rows = csv.reader(handle, delimiter='\t' if suffix == '.tsv' else ',')
                headers = next(rows, [])
                for number, row in enumerate(rows, 2):
                    for column, cell in enumerate(row):
                        errors.extend(metadata._cell_errors(cell, source, known, f'/row/{number}/column/{column + 1}', headers[column] if column < len(headers) else ''))
        elif phase == 'final' and suffix == '.xlsx':
            errors.extend(metadata._xlsx_errors(path, source, known))
        else:
            continue
        checked.append(source)
    if errors:
        raise ValueError('Restricted materialized metadata rejected:\n' + '\n'.join(errors))
    return checked


class RestrictedIOGuard:
    """Process-local audit guard for this driver, not an OS security sandbox.

    Exact final paths and narrowly registered temporary paths are the only write
    destinations. No workbook is read before its exact path is authorized.
    """
    def __init__(self, root):
        self.root = pathlib.Path(root).resolve()
        self.outputs = set()
        self.temporary = set()
        self.temp_dir = None
        self.enabled = True
        self.configured = False

    def path(self, value):
        if isinstance(value, bytes):
            value = os.fsdecode(value)
        if not isinstance(value, (str, os.PathLike)):
            return None  # fdopen reuses a descriptor opened through this guard.
        return pathlib.Path(value).absolute()

    def configure(self, outputs, temp_dir):
        self.outputs = {self.path(p) for p in outputs}
        self.temp_dir = self.path(temp_dir)
        self.configured = True
        if any(p.is_symlink() for p in self.outputs):
            raise PermissionError('output cannot be symlink')

    def permitted(self, path):
        return path in self.outputs or path in self.temporary

    def __call__(self, event, args):
        if not self.enabled:
            return
        dir_fd_index = {'os.remove': 1, 'os.unlink': 1, 'os.rmdir': 1, 'os.mkdir': 2, 'os.chmod': 2, 'os.chown': 3, 'os.utime': 3}.get(event)
        if dir_fd_index is not None and len(args) > dir_fd_index and args[dir_fd_index] not in (None, -1):
            raise PermissionError('directory-relative mutation is not allowed')
        if event == 'tempfile.mkstemp':
            if not self.configured:
                raise PermissionError('temporary registration requires an approved output scope')
            path = self.path(args[0])
            permitted_parent = path.parent in {self.root / 'site', self.root / 'site/people'}
            if (self.temp_dir and path.parent == self.temp_dir) or (path.parent == self.root / 'site/exports' and path.name.endswith('.xlsx.tmp')) or (permitted_parent and path.name.startswith('.atlas-write-')):
                self.temporary.add(path)
            else:
                raise PermissionError('temporary path outside restricted build scope')
        elif event == 'open':
            path = self.path(args[0])
            if path is None:
                return
            mode, flags = args[1:3]
            # NamedTemporaryFile first audits its exact directory as an opener
            # placeholder; the real file open follows mkstemp registration.
            preopen_flags = os.O_RDWR | os.O_CREAT | os.O_TRUNC | getattr(os, 'O_CLOEXEC', 0)
            if self.configured and path in {self.temp_dir, self.root / 'site/exports'} and mode == 'w+' and flags == preopen_flags:
                return
            writing = bool(flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC | os.O_APPEND)) if isinstance(flags, int) else any(c in (mode or '') for c in 'wax+')
            workbook = any(ext in path.name.lower() for ext in ('.xlsx', '.xlsm', '.xlsb', '.xls'))
            if (writing or workbook) and not self.permitted(path):
                raise PermissionError('file I/O outside exact restricted output paths')
        elif event in {'os.rename', 'os.link', 'os.symlink'}:
            if event != 'os.rename':
                raise PermissionError('links are not part of restricted build')
            if any(fd not in (None, -1) for fd in args[2:]):
                raise PermissionError('directory-relative rename is not allowed')
            source, target = self.path(args[0]), self.path(args[1])
            if source not in self.temporary or target not in self.outputs:
                raise PermissionError('rename is not a registered temporary to exact output')
        elif event in {'os.remove', 'os.unlink', 'os.rmdir', 'os.mkdir'}:
            path = self.path(args[0])
            if event == 'os.mkdir':
                if path not in {self.root / 'site', self.root / 'site/exports', self.root / 'site/people', self.temp_dir}:
                    raise PermissionError('directory creation outside restricted scope')
            elif event == 'os.rmdir':
                if path != self.temp_dir:
                    raise PermissionError('directory removal outside restricted scope')
            elif not self.permitted(path):
                raise PermissionError('remove outside restricted scope')
        elif event in {'os.truncate', 'os.chmod', 'os.chown', 'os.utime'}:
            path = self.path(args[0])
            if path is not None and not self.permitted(path):
                raise PermissionError('mutation outside restricted scope')


def run(plan_path, plan_sha, baseline_root, tree_path, receipt_path):
    # Process lifetime guard: install before any plan/candidate reads or writes.
    guard = RestrictedIOGuard(ROOT)
    sys.addaudithook(guard)
    plan = pinned_json(plan_path, plan_sha)
    if plan.get('base_tree_receipt_sha256') != BASE_TREE_RECEIPT_SHA256:
        raise ValueError('scope must bind the independently verified real tree receipt')
    tree = pinned_json(tree_path, BASE_TREE_RECEIPT_SHA256)
    catalog = inheritance_catalog(tree)
    source_gate = pinned_json(plan['source_gate_path'], plan['source_gate_sha256'])
    if source_gate.get('status') != 'NEW_RECOVERY_SOURCE_ATTRIBUTED_MAPPING_PASS' or source_gate.get('person_ids') != plan['person_ids']:
        raise ValueError('exact new independent source gate required')
    baseline_root = pathlib.Path(baseline_root).resolve()
    if baseline_root == ROOT:
        raise ValueError('baseline must be immutable and separate')
    # Verify every canonical baseline input against the real pinned tree.
    for path in sorted((baseline_root / 'data').rglob('*.json')):
        rel = path.relative_to(baseline_root).as_posix()
        if rel in {'data/atlas.json', 'data/rosters.json'} or rel.startswith('data/people/'):
            raw = path.read_bytes()
            oid = hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
            if catalog.get(rel, {}).get('sha') != oid:
                raise ValueError('baseline canonical blob mismatch: ' + rel)
    receipt_path = pathlib.Path(receipt_path).resolve()
    if receipt_path.is_relative_to(ROOT):
        raise ValueError('private receipt must be outside publication root')
    actual_inputs = {label: hashlib.sha256(raw).hexdigest() for label, raw in storage_inputs(ROOT / 'data/atlas.json')}
    actual_inputs['data/rosters.json'] = sha256(ROOT / 'data/rosters.json')
    if (ROOT / 'data/rosters.json').read_bytes() != (baseline_root / 'data/rosters.json').read_bytes():
        raise ValueError('canonical roster changes need separate approval; not part of this scope')
    if source_gate.get('canonical_input_sha256') != actual_inputs:
        raise ValueError('source gate is not bound to these exact canonical bytes')
    baseline = load_atlas(baseline_root / 'data/atlas.json')
    atlas = load_atlas(ROOT / 'data/atlas.json')
    build.validate(atlas)
    exports, selected = validate_scope(plan, atlas, baseline)
    before_files = metadata.publication_files(ROOT)
    allowed_workbooks = {'site/exports/' + e['department_id'] + '.xlsx' for e in selected} | {'site/exports/待核对名录.xlsx'}
    if {p for p in before_files if p.endswith('.xlsx')} - allowed_workbooks:
        raise ValueError('materialized workbooks outside the exact generated scope')
    site_parts = {'site/people/' + part.name for part in (ROOT / 'data/people').glob('*.json')}
    all_outputs = allowed_workbooks | site_parts | {'site/atlas.json', 'site/rosters.json', 'site/exports/待核对名录.csv'}
    if receipt_path.exists() and receipt_path.is_symlink():
        raise ValueError('private receipt cannot be symlink')
    # Private worksheet temporary directory is an explicit sibling of the receipt.
    temporary_root = receipt_path.parent / ('restricted-tmp-' + plan_sha[:16])
    if temporary_root.exists() and (temporary_root.is_symlink() or any(temporary_root.iterdir())):
        raise ValueError('temporary directory must be absent or empty, never reused populated')
    guard.configure([ROOT / rel for rel in all_outputs] + [receipt_path], temporary_root)
    temporary_root.mkdir(exist_ok=True)
    tempfile.tempdir = str(temporary_root)
    preflight = check_materialized(ROOT, catalog, phase='preflight')
    # Bind the new driver and immutable scope as well as original build inputs.
    base_build_id = compute_build_id(ROOT)
    atlas['build_id'] = hashlib.sha256((base_build_id + sha256(__file__) + plan_sha).encode()).hexdigest()[:16]
    output = ROOT / 'site/exports'
    output.mkdir(parents=True, exist_ok=True)
    generated = []
    for export in selected:
        dept, sid = export['department_id'], export['school_id']
        people = [p for p in atlas['people'] if p['department_id'] == dept and p['school_id'] == sid]
        workbook = build.Workbook()
        workbook.remove(workbook.active)
        for name, rows in build.department_tables(people, atlas['updated_at'], atlas['institutions']):
            build.sheet(workbook, name, rows, build.disabled_sources_by_person(people))
        path = output / (dept + '.xlsx')
        build.save_deterministic_xlsx(workbook, path)
        generated.append(path.relative_to(ROOT).as_posix())
    build_rosters.build_rosters(atlas, generate_excel=True)
    generated += ['site/exports/待核对名录.xlsx', 'site/exports/待核对名录.csv']
    roster_path = ROOT / 'site/rosters.json'
    roster = json.loads(roster_path.read_text())
    roster['build_id'] = atlas['build_id']
    roster_path.write_text(json.dumps(roster, ensure_ascii=False, indent=2) + '\n')
    atlas['exports'] = exports
    write_atlas(ROOT / 'site/atlas.json', atlas)
    checked = check_materialized(ROOT, catalog, phase='final')
    local = metadata.publication_files(ROOT)
    receipt = {'status': 'NEW_RECOVERY_RESTRICTED_BUILD_ONLY', 'full_suite': 'NOT_RUN',
               'base_commit': BASE_COMMIT, 'base_tree': BASE_TREE, 'scope_sha256': plan_sha,
               'build_id': atlas['build_id'], 'preflight_checked': preflight, 'final_checked': checked,
               'generated_workbooks': [p for p in generated if p.endswith('.xlsx')],
               'generated_sha256': {p: sha256(ROOT / p) for p in sorted(all_outputs)},
               'generated_output_inventory': sorted(all_outputs),
               'inherited_content_not_rechecked': {p: v for p, v in catalog.items() if p not in local}}
    receipt_path = pathlib.Path(receipt_path).resolve()
    if receipt_path.is_relative_to(ROOT):
        raise ValueError('private receipt must be outside publication root')
    if any(temporary_root.iterdir()):
        raise ValueError('unexpected residual temporary files')
    temporary_root.rmdir()
    receipt_path.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n')
    return receipt


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    for flag in ('plan', 'plan-sha256', 'baseline-root', 'tree-json', 'receipt'):
        parser.add_argument('--' + flag, required=True)
    args = parser.parse_args()
    run(args.plan, args.plan_sha256, args.baseline_root, args.tree_json, args.receipt)
