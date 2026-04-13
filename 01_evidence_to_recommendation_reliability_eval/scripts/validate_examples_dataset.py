#!/usr/bin/env python3

import argparse
import csv
from collections import Counter


def parse_args():
    parser = argparse.ArgumentParser(
        description="Validate benchmark dataset row counts and per-slice constraints."
    )
    parser.add_argument("--examples", required=True, help="Path to examples CSV.")
    parser.add_argument("--expected-total", type=int, default=None, help="Expected total row count.")
    parser.add_argument(
        "--expected-grade-counts",
        default="",
        help="Comma-separated grade=count pairs, e.g. A=16,B=24,C=32,D=16,I=32",
    )
    parser.add_argument(
        "--max-per-slice",
        type=int,
        default=None,
        help="Maximum allowed rows per (source_topic, population, grade) slice.",
    )
    return parser.parse_args()


def read_rows(path):
    with open(path, newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def parse_expected_grade_counts(raw):
    if not raw:
        return {}
    output = {}
    for item in raw.split(","):
        item = item.strip()
        if not item:
            continue
        grade, count = item.split("=", 1)
        output[grade.strip()] = int(count.strip())
    return output


def main():
    args = parse_args()
    rows = read_rows(args.examples)

    if args.expected_total is not None and len(rows) != args.expected_total:
        raise SystemExit(
            f"Expected total {args.expected_total} rows, found {len(rows)}"
        )

    grade_counts = Counter(row["grade"] for row in rows)
    expected_grade_counts = parse_expected_grade_counts(args.expected_grade_counts)
    if expected_grade_counts and dict(grade_counts) != expected_grade_counts:
        raise SystemExit(
            f"Grade counts mismatch. Expected {expected_grade_counts}, found {dict(grade_counts)}"
        )

    slice_counts = Counter(
        (row["source_topic"], row["population"], row["grade"])
        for row in rows
    )
    if args.max_per_slice is not None:
        offenders = [
            (key, count)
            for key, count in slice_counts.items()
            if count > args.max_per_slice
        ]
        if offenders:
            raise SystemExit(
                f"Found slices above max_per_slice={args.max_per_slice}: {offenders[:5]}"
            )

    print(f"rows={len(rows)}")
    print(f"grade_counts={dict(grade_counts)}")
    print(f"max_slice_count={max(slice_counts.values()) if slice_counts else 0}")


if __name__ == "__main__":
    main()
