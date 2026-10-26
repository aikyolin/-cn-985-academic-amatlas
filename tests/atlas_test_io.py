"""Thin live IO adapter; historical bytes require an explicit caller decision."""
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from atlas_storage import load_atlas, write_atlas


def read_live_json(path):
    path = Path(path)
    if path.name == 'atlas.json':
        return load_atlas(path)
    return json.loads(path.read_text(encoding='utf-8'))
