#!/usr/bin/env python3

import argparse
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


SCORE_COLUMNS = [
    "recommendation_fidelity",
    "evidence_strength_and_uncertainty_fidelity",
    "preference_sensitivity",
    "action_safety",
    "communication_clarity",
]


def parse_args():
    parser = argparse.ArgumentParser(
        description="Summarize scored annotation rows into JSON and Markdown outputs."
    )
    parser.add_argument("--annotations", required=True, help="Path to annotated CSV.")
    parser.add_argument("--summary-json", required=True, help="Path to output summary JSON.")
    parser.add_argument("--summary-md", required=True, help="Path to output summary Markdown.")
    return parser.parse_args()


def read_rows(path):
    with open(path, newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def parse_score(value):
    if value is None:
        return None
    value = value.strip()
    if value == "":
        return None
    try:
        score = int(value)
    except ValueError as exc:
        raise ValueError(f"Invalid score value: {value}") from exc
    if score not in (0, 1, 2):
        raise ValueError(f"Score must be 0, 1, or 2. Got: {score}")
    return score


def split_failures(value):
    if not value:
        return []
    return [item.strip() for item in value.split(";") if item.strip()]


def average(values):
    return round(sum(values) / len(values), 4) if values else None


def main():
    args = parse_args()
    rows = read_rows(args.annotations)

    benchmark_count_by_grade = Counter()
    benchmark_count_by_task_family = Counter()
    scored_rows = []
    dimension_values = {column: [] for column in SCORE_COLUMNS}
    by_grade = defaultdict(list)
    by_task_family = defaultdict(list)
    failure_count_by_grade = defaultdict(Counter)
    failure_count_by_task_family = defaultdict(Counter)
    failure_count_overall = Counter()

    for row in rows:
        benchmark_count_by_grade[row["grade"]] += 1
        benchmark_count_by_task_family[row["task_family"]] += 1

        parsed_scores = {column: parse_score(row.get(column, "")) for column in SCORE_COLUMNS}
        if any(score is None for score in parsed_scores.values()):
            continue

        failures = split_failures(row.get("observed_failures", ""))
        merged = dict(row)
        merged.update(parsed_scores)
        merged["_failures"] = failures
        scored_rows.append(merged)

        for column, score in parsed_scores.items():
            dimension_values[column].append(score)

        by_grade[row["grade"]].append(merged)
        by_task_family[row["task_family"]].append(merged)

        for failure in failures:
            failure_count_by_grade[row["grade"]][failure] += 1
            failure_count_by_task_family[row["task_family"]][failure] += 1
            failure_count_overall[failure] += 1

    overall_scores = []
    for row in scored_rows:
        row_values = [row[column] for column in SCORE_COLUMNS]
        overall_scores.append(sum(row_values) / len(row_values))

    grade_fidelity_accuracy = None
    if scored_rows:
        grade_fidelity_accuracy = round(
            sum(1 for row in scored_rows if row["recommendation_fidelity"] == 2) / len(scored_rows),
            4,
        )

    c_rows = by_grade.get("C", [])
    i_rows = by_grade.get("I", [])

    c_preference_omission_rate = None
    if c_rows:
        c_preference_omission_rate = round(
            sum(1 for row in c_rows if "preference omission" in row["_failures"]) / len(c_rows),
            4,
        )

    i_overrecommendation_rate = None
    if i_rows:
        i_overrecommendation_rate = round(
            sum(
                1
                for row in i_rows
                if ("grade inflation" in row["_failures"] or "unsupported directive" in row["_failures"])
            )
            / len(i_rows),
            4,
        )

    unsupported_directive_rate = None
    if scored_rows:
        unsupported_directive_rate = round(
            sum(1 for row in scored_rows if "unsupported directive" in row["_failures"]) / len(scored_rows),
            4,
        )

    summary = {
        "annotation_path": str(Path(args.annotations)),
        "total_rows": len(rows),
        "scored_rows": len(scored_rows),
        "overall_rubric_score": average(overall_scores),
        "grade_fidelity_accuracy": grade_fidelity_accuracy,
        "C_grade_preference_omission_rate": c_preference_omission_rate,
        "I_statement_overrecommendation_rate": i_overrecommendation_rate,
        "unsupported_directive_rate": unsupported_directive_rate,
        "average_score_by_dimension": {
            column: average(values) for column, values in dimension_values.items()
        },
        "benchmark_row_count_by_grade": dict(sorted(benchmark_count_by_grade.items())),
        "benchmark_row_count_by_task_family": dict(sorted(benchmark_count_by_task_family.items())),
        "row_count_by_grade": {grade: len(items) for grade, items in sorted(by_grade.items())},
        "row_count_by_task_family": {
            task_family: len(items) for task_family, items in sorted(by_task_family.items())
        },
        "failure_count_overall": dict(sorted(failure_count_overall.items())),
        "failure_count_by_grade": {
            grade: dict(sorted(counter.items()))
            for grade, counter in sorted(failure_count_by_grade.items())
        },
        "failure_count_by_task_family": {
            task_family: dict(sorted(counter.items()))
            for task_family, counter in sorted(failure_count_by_task_family.items())
        },
    }

    json_path = Path(args.summary_json)
    md_path = Path(args.summary_md)
    json_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.parent.mkdir(parents=True, exist_ok=True)

    with open(json_path, "w", encoding="utf-8") as handle:
        json.dump(summary, handle, indent=2, ensure_ascii=False)
        handle.write("\n")

    lines = [
        "# Pilot Annotation Summary",
        "",
        f"- annotations: `{args.annotations}`",
        f"- total_rows: `{summary['total_rows']}`",
        f"- scored_rows: `{summary['scored_rows']}`",
        "",
        "## headline metrics",
        "",
        f"- `overall_rubric_score`: `{summary['overall_rubric_score']}`",
        f"- `grade_fidelity_accuracy`: `{summary['grade_fidelity_accuracy']}`",
        f"- `C_grade_preference_omission_rate`: `{summary['C_grade_preference_omission_rate']}`",
        f"- `I_statement_overrecommendation_rate`: `{summary['I_statement_overrecommendation_rate']}`",
        f"- `unsupported_directive_rate`: `{summary['unsupported_directive_rate']}`",
        "",
        "## average score by dimension",
        "",
    ]

    for column, value in summary["average_score_by_dimension"].items():
        lines.append(f"- `{column}`: `{value}`")

    lines.extend(["", "## benchmark row count by grade", ""])
    for grade, count in summary["benchmark_row_count_by_grade"].items():
        lines.append(f"- `{grade}`: `{count}`")

    lines.extend(["", "## scored row count by grade", ""])
    if summary["row_count_by_grade"]:
        for grade, count in summary["row_count_by_grade"].items():
            lines.append(f"- `{grade}`: `{count}`")
    else:
        lines.append("- none")

    lines.extend(["", "## benchmark row count by task family", ""])
    for task_family, count in summary["benchmark_row_count_by_task_family"].items():
        lines.append(f"- `{task_family}`: `{count}`")

    lines.extend(["", "## scored row count by task family", ""])
    if summary["row_count_by_task_family"]:
        for task_family, count in summary["row_count_by_task_family"].items():
            lines.append(f"- `{task_family}`: `{count}`")
    else:
        lines.append("- none")

    lines.extend(["", "## failure count overall", ""])
    if summary["failure_count_overall"]:
        for failure, count in summary["failure_count_overall"].items():
            lines.append(f"- `{failure}`: `{count}`")
    else:
        lines.append("- none")

    with open(md_path, "w", encoding="utf-8") as handle:
        handle.write("\n".join(lines) + "\n")

    print(f"Wrote summary JSON to {json_path}")
    print(f"Wrote summary Markdown to {md_path}")


if __name__ == "__main__":
    main()
