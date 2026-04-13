#!/usr/bin/env python3

import argparse
import csv
import json
from pathlib import Path


METRICS = [
    "overall_rubric_score",
    "grade_fidelity_accuracy",
    "C_grade_preference_omission_rate",
    "I_statement_overrecommendation_rate",
    "unsupported_directive_rate",
]


def parse_args():
    parser = argparse.ArgumentParser(description="Compare multiple run summaries.")
    parser.add_argument("--runs-root", required=True, help="Root directory containing run subdirectories.")
    parser.add_argument("--output-md", required=True, help="Path to write markdown comparison.")
    parser.add_argument("--output-csv", required=True, help="Path to write csv comparison.")
    return parser.parse_args()


def load_summary(summary_path):
    with open(summary_path, encoding="utf-8") as handle:
        return json.load(handle)


def discover_runs(runs_root):
    runs = []
    for child in sorted(Path(runs_root).iterdir()):
        if not child.is_dir():
            continue
        summary_path = child / "summary.json"
        if summary_path.exists():
            runs.append((child.name, load_summary(summary_path)))
    return runs


def format_metric(value):
    if value is None:
        return ""
    return f"{value}"


def main():
    args = parse_args()
    runs = discover_runs(args.runs_root)
    if not runs:
        raise SystemExit("No run summaries found.")

    output_md = Path(args.output_md)
    output_csv = Path(args.output_csv)
    output_md.parent.mkdir(parents=True, exist_ok=True)
    output_csv.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = ["run_name", "scored_rows"] + METRICS
    with open(output_csv, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for run_name, summary in runs:
            row = {"run_name": run_name, "scored_rows": summary.get("scored_rows")}
            for metric in METRICS:
                row[metric] = summary.get(metric)
            writer.writerow(row)

    lines = [
        "# Demo Smoke Test Runs",
        "",
        "이 문서는 smoke-test 목적의 demo run 비교 결과를 요약한다.",
        "실제 외부 모델 leaderboard로 해석하면 안 된다.",
        "",
        "| run | scored_rows | overall_rubric_score | grade_fidelity_accuracy | C_preference_omission | I_overrecommendation | unsupported_directive |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]

    for run_name, summary in runs:
        lines.append(
            "| "
            + run_name
            + " | "
            + str(summary.get("scored_rows"))
            + " | "
            + str(summary.get("overall_rubric_score"))
            + " | "
            + str(summary.get("grade_fidelity_accuracy"))
            + " | "
            + str(summary.get("C_grade_preference_omission_rate"))
            + " | "
            + str(summary.get("I_statement_overrecommendation_rate"))
            + " | "
            + str(summary.get("unsupported_directive_rate"))
            + " |"
        )

    lines.extend(
        [
            "",
            "## interpretation",
            "",
            "- `demo_handcrafted_reference`는 benchmark upper-bound smoke test 역할을 한다.",
            "- `demo_overconfident_baseline`는 `C`, `D`, `I`에서 과권고와 과신을 유도해 benchmark discrimination을 확인하는 역할을 한다.",
            "- 실제 모델 비교는 이 문서가 아니라 future real-run report에서 수행해야 한다.",
        ]
    )

    with open(output_md, "w", encoding="utf-8") as handle:
        handle.write("\n".join(lines) + "\n")

    print(f"Wrote run comparison markdown to {output_md}")
    print(f"Wrote run comparison csv to {output_csv}")


if __name__ == "__main__":
    main()
