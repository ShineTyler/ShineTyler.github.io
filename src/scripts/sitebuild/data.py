"""Content loading: JSON data files and Markdown entries with frontmatter."""
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple


@dataclass
class ContentEntry:
    meta: Dict[str, str]
    body: str
    source_path: Path


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def parse_front_matter(text: str) -> Tuple[Dict[str, str], str]:
    if not text.startswith("---\n"):
        return {}, text.strip()
    parts = text.split("---\n", 2)
    if len(parts) < 3:
        return {}, text.strip()
    _, front_matter, body = parts
    meta: Dict[str, str] = {}
    for line in front_matter.splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        meta[key.strip()] = value.strip()
    return meta, body.strip()


def infer_slug(path: Path) -> str:
    return path.stem


def load_entries(folder: Path) -> List[ContentEntry]:
    entries: List[ContentEntry] = []
    for path in sorted(folder.glob("*.md")):
        if path.name.startswith("_template"):
            continue
        meta, body = parse_front_matter(path.read_text(encoding="utf-8"))
        meta.setdefault("slug", infer_slug(path))
        entries.append(ContentEntry(meta=meta, body=body, source_path=path))
    return entries
