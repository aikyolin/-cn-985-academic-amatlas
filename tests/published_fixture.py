"""Explicit immutable input for exact *historical release* assertions only.

Live runtime, build, schema and current-release tests must use their real ROOT.
This helper does not transform or approve a current candidate.
"""
import atexit
from functools import lru_cache
import hashlib
from pathlib import Path, PurePosixPath
import shutil
import tempfile
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = ROOT / 'tests/fixtures/released-1458f458.zip'
ARCHIVE_SHA256 = '63a3a43e9a7d794cb217122c0b3bb117ac9e5e8e1368268b681dc9bba90b9330'

@lru_cache(maxsize=1)
def published_root():
    raw = ARCHIVE.read_bytes()
    if hashlib.sha256(raw).hexdigest() != ARCHIVE_SHA256:
        raise ValueError('Published release fixture changed')
    root = Path(tempfile.mkdtemp(prefix='atlas-published-1458f458-'))
    atexit.register(shutil.rmtree, root, ignore_errors=True)
    with ZipFile(ARCHIVE) as z:
        if len(z.namelist()) != 410 or len(set(z.namelist())) != 410:
            raise ValueError('Published fixture inventory differs')
        for member in z.infolist():
            p = PurePosixPath(member.filename)
            if p.is_absolute() or '..' in p.parts or '\\' in member.filename or member.is_dir():
                raise ValueError('Invalid fixture member')
            target = root / member.filename
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(z.read(member))
    return root

if __name__ == '__main__':
    # The caller uses the path while this process is alive only in Python. JS
    # reads individual published files through this command instead.
    import sys
    if len(sys.argv) != 3 or sys.argv[1] != 'read':
        raise SystemExit('Use read RELATIVE_PATH')
    p = PurePosixPath(sys.argv[2])
    if p.is_absolute() or '..' in p.parts or '\\' in sys.argv[2]:
        raise ValueError('Invalid published path')
    sys.stdout.buffer.write((published_root() / p).read_bytes())
