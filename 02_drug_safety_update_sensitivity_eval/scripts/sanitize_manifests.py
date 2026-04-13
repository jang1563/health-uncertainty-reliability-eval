#!/usr/bin/env python3
"""Sanitize absolute paths in run_manifest.json files to be project-relative.

Rewrites any absolute path that starts with the project root into a project-relative
path (e.g. `data/benchmark_items.jsonl`) before committing to a public repo.
"""

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PROJECT_ROOT_STR = str(PROJECT_ROOT)

PATH_FIELDS = ["data_path", "figures_dir", "output_dir", "report_path"]


def relativize(value):
    """Convert an absolute path under the project root to a project-relative path."""
    if not isinstance(value, str):
        return value
    if value.startswith(PROJECT_ROOT_STR + "/"):
        return value[len(PROJECT_ROOT_STR) + 1:]
    if value == PROJECT_ROOT_STR:
        return "."
    return value


def sanitize_manifest(path: Path) -> bool:
    """Return True if the manifest was modified."""
    with path.open("r") as f:
        data = json.load(f)

    changed = False
    for field in PATH_FIELDS:
        if field in data:
            new_value = relativize(data[field])
            if new_value != data[field]:
                data[field] = new_value
                changed = True

    if changed:
        with path.open("w") as f:
            json.dump(data, f, indent=2)
            f.write("\n")
    return changed


def main():
    manifests = list(PROJECT_ROOT.glob("eval/output/**/run_manifest.json"))
    print(f"Found {len(manifests)} manifest(s)")
    modified = 0
    for m in sorted(manifests):
        if sanitize_manifest(m):
            modified += 1
            print(f"  sanitized: {m.relative_to(PROJECT_ROOT)}")
    print(f"Total modified: {modified}/{len(manifests)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
