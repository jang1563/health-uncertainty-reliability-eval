#!/usr/bin/env python3

import argparse
import json
import subprocess
import sys
from pathlib import Path


def parse_args():
    parser = argparse.ArgumentParser(description="Create annotation_sheet.csv for a run directory.")
    parser.add_argument("--run-dir", required=True, help="Run directory containing outputs.csv.")
    parser.add_argument(
        "--examples",
        default="",
        help="Optional override for examples CSV. Defaults to manifest examples_source or project data/examples.csv.",
    )
    return parser.parse_args()


def resolve_project_path(project_root, raw_path):
    path = Path(raw_path)
    if not path.is_absolute():
        path = project_root / path
    return path.resolve()


def main():
    args = parse_args()
    run_dir = Path(args.run_dir).resolve()
    project_root = Path(__file__).resolve().parent.parent
    outputs_csv = run_dir / "outputs.csv"
    annotation_csv = run_dir / "annotation_sheet.csv"
    manifest_path = run_dir / "manifest.json"
    script_path = project_root / "scripts" / "build_annotation_sheet.py"

    if not outputs_csv.exists():
        raise SystemExit(f"Missing outputs.csv in run directory: {outputs_csv}")

    manifest = {}
    if manifest_path.exists():
        with open(manifest_path, encoding="utf-8") as handle:
            manifest = json.load(handle)

    if args.examples:
        examples_csv = resolve_project_path(project_root, args.examples)
    elif manifest.get("examples_source"):
        examples_csv = resolve_project_path(project_root, manifest["examples_source"])
    else:
        examples_csv = project_root / "data" / "examples.csv"

    if not examples_csv.exists():
        raise SystemExit(f"Examples CSV not found: {examples_csv}")

    cmd = [
        sys.executable,
        str(script_path),
        "--examples",
        str(examples_csv),
        "--responses",
        str(outputs_csv),
        "--output",
        str(annotation_csv),
    ]
    subprocess.run(cmd, check=True)
    print(f"Prepared annotation sheet at {annotation_csv}")


if __name__ == "__main__":
    main()
