"""Reject non-public source locators without rewriting data or fetching evidence.

The pure ``metadata_errors`` function accepts an explicit public-file inventory.
The CLI inventories only publication directories, then checks either inputs before
generation (``preflight``) or the complete generated tree (``final``). Code is not
grepped: defensive rules and synthetic negative tests are not published facts.
All JSON fixtures, including historical source contracts, are checked.
"""
import argparse
import csv
import json
import pathlib
import posixpath
import re
import xml.etree.ElementTree as ET
from urllib.parse import unquote, urlsplit
from zipfile import ZipFile


PUBLIC_DIRS = {'data', 'progress', 'research', 'tests', 'scripts', 'site', 'schema', 'docs', '.github'}
ROOT_FILES = {'README.md', 'CONTRIBUTING.md', 'CONTRIBUTORS.md', 'index.html',
              'package.json', 'requirements.txt', 'requirements-dev.txt', '.gitignore', '.nojekyll'}
SKIP_PARTS = {'.git', '__pycache__', 'node_modules', '.pytest_cache'}
TOOL_REFERENCE = re.compile(r'(?<![A-Za-z0-9_])turn\d+(?:search|view|fetch|open|click|find|image|news|finance|weather|sports|calculator)\d+(?![A-Za-z0-9_])', re.I)
LOCAL_PATH = re.compile(r'(?<![A-Za-z0-9_])file\s*:(?:/{0,3}|\\)|(?<![A-Za-z0-9])[A-Za-z]:[\\/]|\\\\[^\\\s]+\\|(?<![:/A-Za-z0-9])~[/\\]|(?<![:/A-Za-z0-9])/(?:workspace|home|Users|tmp|private|var|opt|mnt|media|Volumes|etc|root|run|proc|sys|dev|usr|Library)(?:/|\b)', re.I)
TOOL_LINE = re.compile(r'(?<![A-Za-z0-9_])L\d+(?:\s*[-–—:]\s*L?\d+)?(?![A-Za-z0-9_])')
FILE_SHAPE = re.compile(r'^[\w./@+%-]+\.(?:json|jsonl|xlsx|xls|csv|tsv|pdf|html?|md|txt|log|ya?ml|png|jpe?g|svg|py|js|css)(?:[?#][^\s]*)?$', re.I)
LOCATOR_KEYS = {'source_locator', 'source_locators', 'source_location', 'evidence_locator',
                'evidence_location', 'location', 'evidence_note', 'access_note'}
POINTER_KEYS = {'path', 'pointer', 'json_pointer', 'object_path', 'preserved_at'}
CELL_KEYS = {'cell', 'cells', 'range', 'cell_range', 'xlsx_range', 'coordinate', 'coordinates'}
CELL_RANGE = re.compile(r"^(?:(?:'[^']+'|[^!\s]+)!)?\$?[A-Z]{1,3}\$?[1-9]\d*(?::\$?[A-Z]{1,3}\$?[1-9]\d*)?$")
SYNTHETIC_EXPORTS = {'exports/hit-test-computing.xlsx', 'exports/pku-test-department.xlsx'}


def _pointer_part(value):
    return str(value).replace('~', '~0').replace('/', '~1')


def _http_url(value):
    try:
        value = value.strip()  # Raw roster observations preserve surrounding whitespace.
        parsed = urlsplit(value)
        parsed.port
        return (parsed.scheme in {'http', 'https'} and bool(parsed.hostname)
                and not any(c.isspace() for c in value) and not parsed.username and not parsed.password)
    except ValueError:
        return False


def _json_pointer(value):
    return value.startswith('/') and not re.search(r'~(?![01])', value)


def _file_key(key):
    return key in {'file', 'files', 'path', 'paths', 'artifact', 'artifacts', 'report', 'reports'} or key.endswith(('_file', '_files', '_path', '_paths', '_artifact', '_artifacts', '_report', '_reports'))


def _url_key(key):
    return key in {'url', 'urls', 'body_endpoint'} or key.endswith(('_url', '_urls'))


def _public_target(value, source, public_files):
    """Resolve explicit repository or document-relative links, never basename search."""
    path = unquote(value.split('#', 1)[0].split('?', 1)[0])
    try:
        scheme = urlsplit(path).scheme
    except ValueError:
        return False
    if not path or path.startswith(('/', '\\')) or '\\' in path or scheme:
        return False
    candidates = [path, posixpath.join(posixpath.dirname(source), path)]
    if path.startswith('exports/'):
        candidates.append('site/' + path)
    for candidate in candidates:
        normalized = posixpath.normpath(candidate)
        if normalized == '..' or normalized.startswith('../'):
            continue
        if normalized in public_files or (path.endswith('/') and normalized + '/index.html' in public_files):
            return True
    return False


def _lexical_errors(value):
    errors = []
    value = unquote(value)
    if TOOL_REFERENCE.search(value):
        errors.append('private tool reference')
    if LOCAL_PATH.search(value):
        errors.append('local path or file URI')
    return errors


def metadata_errors(value, *, source, public_files, pointer='', field=''):
    """Return diagnostics, without mutating inputs or reading the filesystem.

    HTTP(S) syntax is checked, not reachability. SHA values and their stated audit
    scope are retained; this check does not certify the underlying facts or bytes.
    """
    errors = []

    def error(at, message):
        errors.append(f'{source}#{at or "/"}: {message}')

    def text_value(text, at, key, is_key=False):
        for message in _lexical_errors(text):
            error(at, message)
        if is_key:
            if text == 'web_reference':
                error(at, 'private tool-reference field')
            if FILE_SHAPE.fullmatch(text) and not _http_url(text) and not _public_target(text, source, public_files):
                error(at, 'unresolved public file used as a key')
            return
        if _http_url(text):
            return
        if key in LOCATOR_KEYS and TOOL_LINE.search(text):
            error(at, 'tool line number is not a public source locator')
        if key in LOCATOR_KEYS and re.match(r'^[A-Za-z][A-Za-z0-9+.-]*:/', text) and not _http_url(text):
            error(at, 'non-public locator URI')
        if key in CELL_KEYS and CELL_RANGE.fullmatch(text):
            return
        if text.startswith('/'):
            if key in POINTER_KEYS and _json_pointer(text) and not LOCAL_PATH.search(text):
                return
            error(at, 'absolute path is not a public repository link')
            return
        describes_fields = any(part.endswith(('field_provenance', 'field_status')) for part in at.split('/')[:-1])
        if _url_key(key) and not describes_fields:
            error(at, 'evidence URL must be an absolute HTTP(S) URL')
            return
        if text.startswith('#/') and _json_pointer(text[1:]):
            return
        if _file_key(key) or FILE_SHAPE.fullmatch(text):
            # Exactly two fictional export descriptors, not any evidence locator.
            synthetic_export = (source == 'tests/fixtures/multischool.json'
                                and re.fullmatch(r'/exports/\d+/path', at)
                                and text in SYNTHETIC_EXPORTS)
            if not synthetic_export and not _public_target(text, source, public_files):
                error(at, 'unresolved or non-public repository file')

    def walk(node, at, key):
        if isinstance(node, dict):
            for name, child in node.items():
                child_at = at + '/' + _pointer_part(name)
                text_value(name, child_at, '', is_key=True)
                walk(child, child_at, name)
        elif isinstance(node, list):
            for index, child in enumerate(node):
                walk(child, at + '/' + str(index), key)
        elif isinstance(node, str):
            text_value(node, at, key)
            if node.lstrip().startswith(('{', '[')):
                try:
                    embedded = json.loads(node)
                except json.JSONDecodeError:
                    pass
                else:
                    walk(embedded, at, '')
        # Numeric audit counts, booleans, and null are not locator strings.

    walk(value, pointer, field)
    return errors


def publication_files(root):
    """An explicit publication boundary; outside files and escaping symlinks fail."""
    root = pathlib.Path(root).resolve()
    result = set()
    for path in root.rglob('*'):
        rel = path.relative_to(root)
        if any(part in SKIP_PARTS for part in rel.parts):
            continue
        if not (rel.parts[0] in PUBLIC_DIRS or rel.as_posix() in ROOT_FILES):
            raise ValueError(f'{rel.as_posix()}: outside the reviewed publication boundary; explicitly review new public entries')
        if path.is_symlink() or not path.resolve().is_relative_to(root):
            raise ValueError(f'{rel.as_posix()}: publication files must not be symlinks')
        if path.is_file():
            result.add(rel.as_posix())
    return frozenset(result)


def _cell_errors(value, source, public_files, pointer, field=''):
    if not isinstance(value, str):
        return []
    candidate = value[1:] if value.startswith("'") else value
    if candidate.lstrip().startswith(('{', '[')):
        try:
            parsed = json.loads(candidate)
        except json.JSONDecodeError:
            pass
        else:
            return metadata_errors(parsed, source=source, public_files=public_files, pointer=pointer)
    return metadata_errors(value, source=source, public_files=public_files, pointer=pointer, field=field)


def _xlsx_errors(path, source, public_files):
    """Inspect XML text, relationships, and JSON cells without modifying the ZIP."""
    errors = []
    ns = '{http://schemas.openxmlformats.org/spreadsheetml/2006/main}'
    with ZipFile(path) as archive:
        shared = []
        if 'xl/sharedStrings.xml' in archive.namelist():
            shared = [''.join(part.text or '' for part in cell.iter(ns + 't'))
                      for cell in ET.fromstring(archive.read('xl/sharedStrings.xml')).iter(ns + 'si')]
        for name in sorted(archive.namelist()):
            if not name.endswith(('.xml', '.rels')):
                continue
            element = ET.fromstring(archive.read(name))
            for index, node in enumerate(element.iter()):
                at = f'/{name}/{index}'
                for text in list(node.attrib.values()) + ([node.text] if node.text else []):
                    for message in _lexical_errors(text):
                        errors.append(f'{source}#{at}: {message}')
                # Rich-text runs are combined so split tokens cannot hide in XLSX.
                if node.tag in {ns + 'is', ns + 'si'}:
                    text = ''.join(part.text or '' for part in node.iter(ns + 't'))
                    errors.extend(_cell_errors(text, source, public_files, at))
                if node.tag.endswith('Relationship') and node.get('TargetMode') == 'External':
                    errors.extend(metadata_errors(node.get('Target', ''), source=source,
                                                   public_files=public_files, pointer=at, field='url'))
            # Dedicated locator columns need their header context as well as the
            # generic string/JSON scan above. Ordinary XML cell refs are not data.
            headers = {}
            for row in element.iter(ns + 'row'):
                for cell in row.findall(ns + 'c'):
                    coordinate = cell.get('r', '')
                    column = re.sub(r'\d+', '', coordinate)
                    inline = cell.find(ns + 'is')
                    raw = cell.find(ns + 'v')
                    value = ''.join(part.text or '' for part in inline.iter(ns + 't')) if inline is not None else None
                    if cell.get('t') == 's' and raw is not None:
                        value = shared[int(raw.text)]
                    elif cell.get('t') == 'str' and raw is not None:
                        value = raw.text
                    if row.get('r') == '1':
                        headers[column] = value
                    elif isinstance(value, str) and headers.get(column) in LOCATOR_KEYS | CELL_KEYS:
                        errors.extend(metadata_errors(value, source=source, public_files=public_files,
                                                      pointer=f'/{name}/{coordinate}', field=headers[column]))
    return errors


def _document_errors(text, source, public_files):
    errors = []
    for line_number, line in enumerate(text.splitlines(), 1):
        at = '/line/' + str(line_number)
        for message in _lexical_errors(line):
            errors.append(f'{source}#{at}: {message}')
        # Explicit Markdown links and HTML src/href targets are public locators.
        links = re.findall(r'\]\(([^\s)]+)\)', line)
        links += re.findall(r'(?:href|src)=["\']([^"\']+)["\']', line)
        links += [value for value in re.findall(r'`([^`]+)`', line) if FILE_SHAPE.fullmatch(value)]
        for link in links:
            if link.startswith('#') or _http_url(link) or link.startswith('mailto:'):
                continue
            if not _public_target(link, source, public_files):
                errors.append(f'{source}#{at}: unresolved document link')
    return errors


def tree_errors(root, *, phase='final', include_workbooks=True):
    """Check publication inputs or final output. Never cleans, writes, or fetches."""
    if phase not in {'preflight', 'final'}:
        raise ValueError('phase must be preflight or final')
    root = pathlib.Path(root)
    public_files = publication_files(root)
    errors = []
    for source in sorted(public_files):
        if phase == 'preflight' and source.startswith('site/'):
            continue  # Old generated copies must not block the first legal migration.
        path = root / source
        suffix = path.suffix.lower()
        try:
            if suffix == '.json':
                errors.extend(metadata_errors(json.loads(path.read_text()), source=source, public_files=public_files))
            elif suffix in {'.md', '.html', '.txt', '.yml', '.yaml'}:
                errors.extend(_document_errors(path.read_text(), source, public_files))
            elif phase == 'final' and suffix in {'.csv', '.tsv'}:
                with path.open(newline='') as handle:
                    rows = csv.reader(handle, delimiter='\t' if suffix == '.tsv' else ',')
                    headers = next(rows, [])
                    for number, row in enumerate(rows, 2):
                        for column, cell in enumerate(row):
                            key = headers[column] if column < len(headers) else ''
                            errors.extend(_cell_errors(cell, source, public_files, f'/row/{number}/column/{column + 1}', key))
            elif phase == 'final' and suffix == '.xlsx' and include_workbooks:
                errors.extend(_xlsx_errors(path, source, public_files))
        except (ValueError, OSError, ET.ParseError) as exc:
            errors.append(f'{source}#/: cannot validate: {exc}')
    return errors


def check_public_tree(root, *, phase='final', include_workbooks=True):
    errors = tree_errors(root, phase=phase, include_workbooks=include_workbooks)
    if errors:
        raise ValueError('Public source metadata rejected:\n' + '\n'.join(errors))
    return True


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=pathlib.Path, default=pathlib.Path(__file__).resolve().parents[1])
    parser.add_argument('--phase', choices=['preflight', 'final'], default='final')
    args = parser.parse_args()
    try:
        check_public_tree(args.root, phase=args.phase)
    except ValueError as exc:
        parser.exit(1, str(exc) + '\n')
    print('Public source metadata passed: ' + ('canonical preflight (generated site excluded)' if args.phase == 'preflight'
                                              else 'final publication tree (JSON, documents, CSV, XLSX)'))


if __name__ == '__main__':
    main()
