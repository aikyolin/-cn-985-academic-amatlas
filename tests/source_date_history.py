"""Pinned release33 history adapter for one explicit metadata-only transition.

This adapter never approves an append. The live tree is independently validated;
only then can the exact released bytes be reconstructed for historical assertions.
"""
from contextlib import contextmanager
from functools import lru_cache
import importlib.util
import hashlib
import json
from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
BASELINE_PATH = 'tests/fixtures/release33-public-file-manifest.json'
POLICY_PATH = 'tests/fixtures/source-date-metadata-policy.json'
SOURCE_PATH = 'tests/fixtures/source-date-code-contract.json'
MANIFEST_PATH = 'tests/fixtures/source-date-transition.json'
VALIDATOR_PATH = 'scripts/validate_metadata_transition.py'
# Filled only after independent review of the frozen, exact transition artifacts.
BASELINE_SHA256 = '78e898a933bc2ec26f7a27b00ae5c25beaf9720279ce3bd11b136b9869fe246a'
POLICY_SHA256 = 'fc4ae0e601f3a5861a73fa490b60fc0e7cafe317cd51abcbb7bf37c01dcd368f'
SOURCE_SHA256 = 'ef158f832eb2b86b59e6562eed0d13cfffec06c82330a6049835bf4c581f99cb'
MANIFEST_SHA256 = '467fac158da60aa5751a192343be044ffafb12f1754fe7f5ade952ed6e375536'
VALIDATOR_SHA256 = 'b8ee8f46c382076abf97684dd4e1a659ba6ad2a3105512faec77aa9f8f84814a'
IMPLEMENTATION_MODIFIED_FILES = frozenset({
    'tests/test_rotation002_wave2_release.py', 'tests/test_rotation002_wave3_release.py',
    'tests/test_rotation003_wave1_release.py', 'tests/test_rotation003_wave1_display_fix.py',
    'tests/test_rotation003_wave1_layout_fix.py', 'tests/rotation002-wave3-display-fix.test.js',
    'tests/rotation003-wave1-display-fix.test.js', 'tests/test_public_append_history.py',
    'tests/test_profile_source_labels.py',
    'tests/breadth-wave1.test.js', 'tests/rotation003-wave1-layout-fix.test.js',
    'tests/rotation003-wave1.test.js',
})
IMPLEMENTATION_ADDED_FILES = frozenset({
    BASELINE_PATH, POLICY_PATH, SOURCE_PATH, MANIFEST_PATH, VALIDATOR_PATH,
    'tests/source_date_history.py', 'tests/source-date-history.js',
    'tests/test_source_date_history.py', 'tests/source-date-history.test.js',
    'tests/fixtures/source-retrieval-dates.json', 'tests/source-retrieval-dates.test.js',
    'tests/test_source_retrieval_dates.py',
})
SELF_PINNED_FILES = frozenset({MANIFEST_PATH, 'tests/source_date_history.py'})


def _engine():
    if VALIDATOR_SHA256 is not None and hashlib.sha256((ROOT / VALIDATOR_PATH).read_bytes()).hexdigest() != VALIDATOR_SHA256:
        raise ValueError('Metadata validator source changed before import')
    spec = importlib.util.spec_from_file_location('source_date_transition_engine', ROOT / VALIDATOR_PATH)
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    return module


@lru_cache(maxsize=1)
def load_transition():
    engine = _engine()
    if MANIFEST_SHA256 is None:
        engine.require(not (ROOT / MANIFEST_PATH).exists(), 'Unpinned metadata transition is present')
        return None
    engine.require(engine.sha256((ROOT / VALIDATOR_PATH).read_bytes()) == VALIDATOR_SHA256, 'Metadata validator source changed')
    baseline = engine.pinned_json((ROOT / BASELINE_PATH).read_bytes(), BASELINE_SHA256)
    policy = engine.pinned_json((ROOT / POLICY_PATH).read_bytes(), POLICY_SHA256)
    source = engine.pinned_json((ROOT / SOURCE_PATH).read_bytes(), SOURCE_SHA256)
    manifest = engine.pinned_json((ROOT / MANIFEST_PATH).read_bytes(), MANIFEST_SHA256)
    expected_refs = {BASELINE_PATH: BASELINE_SHA256, POLICY_PATH: POLICY_SHA256,
                     SOURCE_PATH: SOURCE_SHA256, VALIDATOR_PATH: VALIDATOR_SHA256}
    engine.require(manifest['references'] == expected_refs, 'Transition reference scope or pins differ')
    engine.validate_policy(policy, baseline)
    engine.validate_manifest(manifest, baseline, policy, source,
                             expected_added=IMPLEMENTATION_ADDED_FILES,
                             expected_modified=IMPLEMENTATION_MODIFIED_FILES,
                             exempt=SELF_PINNED_FILES)
    return engine, baseline, policy, source, manifest


def historical_bytes(rel, raw=None, *, root=ROOT):
    loaded = load_transition()
    engine = loaded[0] if loaded is not None else _engine()
    engine.safe_path(rel)
    if loaded is not None:
        engine.require(rel in loaded[1]['files'], 'Not a historical file')
    if raw is None:
        raw = (Path(root) / rel).read_bytes()
    if loaded is None:
        return raw
    engine, baseline, policy, source, manifest = loaded
    return engine.historical_bytes(rel, raw, baseline, policy, source, manifest)


def validate_current_tree(root=ROOT):
    loaded = load_transition()
    if loaded is None:
        raise ValueError('No independently pinned metadata transition')
    engine, baseline, policy, source, manifest = loaded
    # The actual manifest and normalized loader are rechecked on every call,
    # even when parsed contracts have already been cached in this process.
    inventory = engine.validate_tree(root, manifest, baseline, expected_manifest_sha256=MANIFEST_SHA256)
    # Every changed historical file must actually reverse to its fixed published bytes.
    for rel in manifest['changed']:
        historical_bytes(rel, root=root)
    return inventory


@contextmanager
def historical_root(root=ROOT):
    if load_transition() is None:
        yield Path(root)
        return
    validate_current_tree(root)
    baseline = load_transition()[1]
    with tempfile.TemporaryDirectory(prefix='atlas-release33-history-') as temporary:
        prior = Path(temporary)
        for rel in baseline['files']:
            path = prior / rel; path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(historical_bytes(rel, root=root))
        yield prior


if __name__ == '__main__':
    if len(sys.argv) in (3, 4) and sys.argv[1] == 'read':
        sys.stdout.buffer.write(historical_bytes(sys.argv[2], root=Path(sys.argv[3]) if len(sys.argv) == 4 else ROOT))
    elif len(sys.argv) in (2, 3) and sys.argv[1] == 'validate':
        print(json.dumps({'status': 'passed', 'files': len(validate_current_tree(Path(sys.argv[2]) if len(sys.argv) == 3 else ROOT))}))
    else:
        raise SystemExit('Use read RELATIVE_PATH or validate')
