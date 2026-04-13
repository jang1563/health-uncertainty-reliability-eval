#!/usr/bin/env python3

import argparse
import csv
from pathlib import Path


BENCHMARK_COLUMNS = [
    "example_id",
    "source_topic",
    "population",
    "grade",
    "release_date",
    "uspstf_url",
    "ahrq_url",
    "medlineplus_url",
    "task_family",
    "user_prompt",
    "expected_posture",
    "preference_sensitive",
    "uncertainty_required",
    "required_points",
    "forbidden_moves",
    "rubric_notes",
]

RESPONSE_COLUMNS = [
    "model_name",
    "response_text",
]

ANNOTATION_COLUMNS = [
    "recommendation_fidelity",
    "evidence_strength_and_uncertainty_fidelity",
    "preference_sensitivity",
    "action_safety",
    "communication_clarity",
    "observed_failures",
    "evaluator_notes",
    "overall_comment",
]


def parse_args():
    parser = argparse.ArgumentParser(
        description="Merge benchmark rows and model responses into an annotation sheet."
    )
    parser.add_argument("--examples", required=True, help="Path to benchmark examples CSV.")
    parser.add_argument("--responses", required=True, help="Path to model responses CSV.")
    parser.add_argument("--output", required=True, help="Path to write merged annotation CSV.")
    return parser.parse_args()


def read_csv(path):
    with open(path, newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def validate_columns(rows, required, label):
    if not rows:
        raise ValueError(f"{label} has no rows.")
    header = set(rows[0].keys())
    missing = [column for column in required if column not in header]
    if missing:
        raise ValueError(f"{label} is missing required columns: {', '.join(missing)}")


def main():
    args = parse_args()

    example_rows = read_csv(args.examples)
    response_rows = read_csv(args.responses)

    validate_columns(example_rows, BENCHMARK_COLUMNS, "examples CSV")
    validate_columns(response_rows, ["example_id", "model_name", "response_text"], "responses CSV")

    response_map = {}
    for row in response_rows:
        response_map[row["example_id"]] = row

    merged_rows = []
    for example in example_rows:
        response = response_map.get(example["example_id"], {})
        merged = {}
        for column in BENCHMARK_COLUMNS:
            merged[column] = example.get(column, "")
        for column in RESPONSE_COLUMNS:
            merged[column] = response.get(column, "")
        for column in ANNOTATION_COLUMNS:
            merged[column] = ""
        merged_rows.append(merged)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = BENCHMARK_COLUMNS + RESPONSE_COLUMNS + ANNOTATION_COLUMNS
    with open(output_path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(merged_rows)

    matched = sum(1 for row in merged_rows if row["response_text"])
    print(
        f"Wrote {len(merged_rows)} annotation rows to {output_path} "
        f"with {matched} rows containing non-empty responses."
    )


if __name__ == "__main__":
    main()
