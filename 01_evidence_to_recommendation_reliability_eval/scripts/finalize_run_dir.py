#!/usr/bin/env python3

import argparse
import subprocess
import sys
from pathlib import Path


def parse_args():
    parser = argparse.ArgumentParser(description="Finalize a scored run directory into summaries and cases.")
    parser.add_argument("--run-dir", required=True, help="Run directory containing annotation_sheet.csv.")
    return parser.parse_args()


def main():
    args = parse_args()
    run_dir = Path(args.run_dir).resolve()
    project_root = Path(__file__).resolve().parent.parent
    annotation_csv = run_dir / "annotation_sheet.csv"
    summary_json = run_dir / "summary.json"
    summary_md = run_dir / "summary.md"
    cases_md = run_dir / "qualitative_cases.md"

    if not annotation_csv.exists():
        raise SystemExit(f"Missing annotation_sheet.csv in run directory: {annotation_csv}")

    summarize_script = project_root / "scripts" / "summarize_annotations.py"
    extract_script = project_root / "scripts" / "extract_case_examples.py"

    subprocess.run(
        [
            sys.executable,
            str(summarize_script),
            "--annotations",
            str(annotation_csv),
            "--summary-json",
            str(summary_json),
            "--summary-md",
            str(summary_md),
        ],
        check=True,
    )

    subprocess.run(
        [
            sys.executable,
            str(extract_script),
            "--annotations",
            str(annotation_csv),
            "--output-md",
            str(cases_md),
        ],
        check=True,
    )

    print(f"Finalized run directory at {run_dir}")


if __name__ == "__main__":
    main()
