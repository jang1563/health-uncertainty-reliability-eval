#!/usr/bin/env python3

import argparse
import csv
from pathlib import Path


TARGET_GRADES = ["C", "D", "I"]


def parse_args():
    parser = argparse.ArgumentParser(description="Extract representative qualitative cases from annotated CSV.")
    parser.add_argument("--annotations", required=True, help="Annotated CSV path.")
    parser.add_argument("--output-md", required=True, help="Output markdown path.")
    return parser.parse_args()


def read_rows(path):
    with open(path, newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def row_score(row):
    total = 0
    for key in [
        "recommendation_fidelity",
        "evidence_strength_and_uncertainty_fidelity",
        "preference_sensitivity",
        "action_safety",
        "communication_clarity",
    ]:
        value = row.get(key, "").strip()
        total += int(value) if value else 0
    return total


def first_matching(rows, predicate):
    for row in rows:
        if predicate(row):
            return row
    return None


def render_case(lines, title, row):
    if not row:
        return
    lines.extend(
        [
            f"## {title}",
            "",
            f"- `example_id`: `{row['example_id']}`",
            f"- `grade`: `{row['grade']}`",
            f"- `source_topic`: `{row['source_topic']}`",
            f"- `task_family`: `{row['task_family']}`",
            f"- `expected_posture`: `{row['expected_posture']}`",
            f"- `observed_failures`: `{row.get('observed_failures', '') or 'none'}`",
            "",
            "**Prompt**",
            "",
            row["user_prompt"],
            "",
            "**Response**",
            "",
            row["response_text"],
            "",
            "**Evaluator Notes**",
            "",
            row.get("evaluator_notes", ""),
            "",
        ]
    )


def main():
    args = parse_args()
    rows = read_rows(args.annotations)
    scored = [row for row in rows if row.get("recommendation_fidelity", "").strip()]
    if not scored:
        raise SystemExit("No scored rows found in annotations CSV.")

    for row in scored:
        row["_total_score"] = row_score(row)

    lines = [
        "# Qualitative Cases",
        "",
        f"- annotations: `{args.annotations}`",
        "",
        "This document collects representative cases from the annotated CSV that most clearly illustrate the benchmark's identity.",
        "",
    ]

    lowest = sorted(scored, key=lambda row: (row["_total_score"], row["example_id"]))[0]
    highest = sorted(scored, key=lambda row: (-row["_total_score"], row["example_id"]))[0]

    render_case(lines, "Lowest-Score Case", lowest)
    render_case(lines, "Highest-Score Case", highest)

    for grade in TARGET_GRADES:
        row = first_matching(
            scored,
            lambda candidate, g=grade: candidate["grade"] == g and candidate.get("observed_failures", "").strip(),
        )
        render_case(lines, f"Representative {grade}-Grade Failure", row)

    output_path = Path(args.output_md)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote qualitative cases to {output_path}")


if __name__ == "__main__":
    main()
