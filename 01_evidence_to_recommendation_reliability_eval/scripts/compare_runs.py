#!/usr/bin/env python3

import argparse
import csv
from itertools import combinations
from pathlib import Path

from e2r_metrics import (
    DEFAULT_BOOTSTRAP_SAMPLES,
    DEFAULT_BOOTSTRAP_SEED,
    PRIMARY_METRICS,
    PRACTICAL_DIFFERENCE_THRESHOLDS,
    detect_adjudication_status,
    detect_chair_reconciliation,
    detect_judge_disagreement,
    detect_judge_sensitivity,
    load_annotation_rows,
    maybe_load_json,
    summarize_paired_metric,
)


def parse_args():
    parser = argparse.ArgumentParser(description="Compare multiple run summaries.")
    parser.add_argument("--runs-root", required=True, help="Root directory containing run subdirectories.")
    parser.add_argument("--output-md", required=True, help="Path to write markdown comparison.")
    parser.add_argument("--output-csv", required=True, help="Path to write csv comparison.")
    parser.add_argument(
        "--run-name",
        action="append",
        default=[],
        help="Optional run directory name to include. Repeat to select a subset.",
    )
    parser.add_argument(
        "--bootstrap-samples",
        type=int,
        default=DEFAULT_BOOTSTRAP_SAMPLES,
        help="Bootstrap samples used for paired run deltas.",
    )
    parser.add_argument(
        "--bootstrap-seed",
        type=int,
        default=DEFAULT_BOOTSTRAP_SEED,
        help="Random seed used for deterministic paired bootstrap intervals.",
    )
    return parser.parse_args()


def load_summary(summary_path):
    return maybe_load_json(summary_path) or {}


def discover_runs(runs_root, selected_run_names):
    selected = set(selected_run_names)
    runs = []
    for child in sorted(Path(runs_root).iterdir()):
        if not child.is_dir():
            continue
        if selected and child.name not in selected:
            continue
        summary_path = child / "summary.json"
        annotation_path = child / "annotation_sheet.csv"
        if summary_path.exists():
            manifest = maybe_load_json(child / "manifest.json") or {}
            annotation_rows = load_annotation_rows(annotation_path) if annotation_path.exists() else []
            runs.append(
                {
                    "run_name": child.name,
                    "run_dir": child,
                    "summary": load_summary(summary_path),
                    "manifest": manifest,
                    "annotation_rows": annotation_rows,
                    "status_snapshot": {
                        "adjudication_status": detect_adjudication_status(
                            child,
                            manifest=manifest,
                            rows=annotation_rows,
                        ),
                        "judge_sensitivity": detect_judge_sensitivity(child),
                        "judge_disagreement": detect_judge_disagreement(child),
                        "chair_reconciliation": detect_chair_reconciliation(child),
                    },
                }
            )
    return runs


def format_interval(interval):
    if not interval:
        return ""
    return f"[{interval['lower']}, {interval['upper']}]"


def build_pairwise_section(runs, bootstrap_samples, bootstrap_seed):
    comparisons = []
    for left, right in combinations(runs, 2):
        pair = {
            "left_run": left["run_name"],
            "right_run": right["run_name"],
            "metrics": {},
        }
        for metric_name in PRIMARY_METRICS:
            pair["metrics"][metric_name] = summarize_paired_metric(
                left["annotation_rows"],
                right["annotation_rows"],
                metric_name,
                samples=bootstrap_samples,
                seed=bootstrap_seed,
            )
        comparisons.append(pair)
    return comparisons


def write_csv(path, runs):
    fieldnames = [
        "run_name",
        "model_name",
        "provider",
        "scored_rows",
        "overall_rubric_score",
        "overall_rubric_score_ci",
        "grade_fidelity_accuracy",
        "grade_fidelity_accuracy_ci",
        "C_grade_preference_omission_rate",
        "C_grade_preference_omission_rate_ci",
        "I_statement_overrecommendation_rate",
        "I_statement_overrecommendation_rate_ci",
        "unsupported_directive_rate",
        "unsupported_directive_rate_ci",
        "provisional_flags",
        "adjudication_status",
        "judge_sensitivity_status",
        "judge_disagreement_status",
        "judge_disagreement_priority_rows",
        "judge_disagreement_critical_rows",
        "chair_reconciliation_status",
        "chair_reconciliation_incomplete_rows",
        "chair_reconciliation_disagreement_rows",
    ]
    with open(path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for run in runs:
            summary = run["summary"]
            row = {
                "run_name": run["run_name"],
                "model_name": run["manifest"].get("model_name", ""),
                "provider": run["manifest"].get("provider", ""),
                "scored_rows": summary.get("scored_rows"),
                "overall_rubric_score": summary.get("overall_rubric_score"),
                "overall_rubric_score_ci": format_interval(
                    summary.get("confidence_intervals", {}).get("overall_rubric_score")
                ),
                "grade_fidelity_accuracy": summary.get("grade_fidelity_accuracy"),
                "grade_fidelity_accuracy_ci": format_interval(
                    summary.get("confidence_intervals", {}).get("grade_fidelity_accuracy")
                ),
                "C_grade_preference_omission_rate": summary.get("C_grade_preference_omission_rate"),
                "C_grade_preference_omission_rate_ci": format_interval(
                    summary.get("confidence_intervals", {}).get("C_grade_preference_omission_rate")
                ),
                "I_statement_overrecommendation_rate": summary.get("I_statement_overrecommendation_rate"),
                "I_statement_overrecommendation_rate_ci": format_interval(
                    summary.get("confidence_intervals", {}).get("I_statement_overrecommendation_rate")
                ),
                "unsupported_directive_rate": summary.get("unsupported_directive_rate"),
                "unsupported_directive_rate_ci": format_interval(
                    summary.get("confidence_intervals", {}).get("unsupported_directive_rate")
                ),
                "provisional_flags": ";".join(summary.get("provisional_flags", [])),
                "adjudication_status": run["status_snapshot"]["adjudication_status"].get("status", ""),
                "judge_sensitivity_status": run["status_snapshot"]["judge_sensitivity"].get("status", ""),
                "judge_disagreement_status": run["status_snapshot"]["judge_disagreement"].get("status", ""),
                "judge_disagreement_priority_rows": run["status_snapshot"]["judge_disagreement"].get("priority_rows"),
                "judge_disagreement_critical_rows": run["status_snapshot"]["judge_disagreement"].get(
                    "priority_bucket_counts",
                    {},
                ).get("critical"),
                "chair_reconciliation_status": run["status_snapshot"]["chair_reconciliation"].get("status", ""),
                "chair_reconciliation_incomplete_rows": run["status_snapshot"]["chair_reconciliation"].get("incomplete_rows"),
                "chair_reconciliation_disagreement_rows": run["status_snapshot"]["chair_reconciliation"].get("disagreement_rows"),
            }
            writer.writerow(row)


def build_markdown(runs, comparisons, bootstrap_samples):
    lines = [
        "# Run Comparison",
        "",
        "This document compares run summaries and adds paired bootstrap deltas for same-set rows when available.",
        f"Paired delta intervals use `{bootstrap_samples}` row-bootstrap samples.",
        "",
        "| run | scored_rows | overall_rubric_score | grade_fidelity_accuracy | C_preference_omission | I_overrecommendation | unsupported_directive | adjudication | judge_sensitivity | judge_disagreement | chair_reconciliation | flags |",
        "|---|---:|---:|---:|---:|---:|---:|---|---|---|---|---|",
    ]

    for run in runs:
        summary = run["summary"]
        flags = ", ".join(summary.get("provisional_flags", [])) or "none"
        adjudication_status = run["status_snapshot"]["adjudication_status"].get("status", "") or "none"
        judge_sensitivity_status = run["status_snapshot"]["judge_sensitivity"].get("status", "") or "none"
        judge_disagreement_status = run["status_snapshot"]["judge_disagreement"].get("status", "") or "none"
        chair_reconciliation_status = run["status_snapshot"]["chair_reconciliation"].get("status", "") or "none"
        lines.append(
            "| "
            + run["run_name"]
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
            + " | "
            + adjudication_status
            + " | "
            + judge_sensitivity_status
            + " | "
            + judge_disagreement_status
            + " | "
            + chair_reconciliation_status
            + " | "
            + flags
            + " |"
        )

    lines.extend(["", "## Confidence Intervals", ""])
    for run in runs:
        lines.append(f"### `{run['run_name']}`")
        for metric_name in PRIMARY_METRICS:
            interval = run["summary"].get("confidence_intervals", {}).get(metric_name)
            lines.append(f"- `{metric_name}`: `{format_interval(interval) or 'none'}`")
        lines.append(
            f"- `adjudication_status`: `{run['status_snapshot']['adjudication_status'].get('status', '')}`"
        )
        lines.append(
            f"- `judge_sensitivity`: `{run['status_snapshot']['judge_sensitivity'].get('status', '')}`"
        )
        lines.append(
            f"- `judge_disagreement`: `{run['status_snapshot']['judge_disagreement'].get('status', '')}`"
        )
        lines.append(
            f"- `judge_disagreement_priority_rows`: `{run['status_snapshot']['judge_disagreement'].get('priority_rows', '')}`"
        )
        lines.append(
            f"- `chair_reconciliation`: `{run['status_snapshot']['chair_reconciliation'].get('status', '')}`"
        )
        lines.append(
            f"- `chair_reconciliation_incomplete_rows`: `{run['status_snapshot']['chair_reconciliation'].get('incomplete_rows', '')}`"
        )
        lines.append(
            f"- `provisional_flags`: `{', '.join(run['summary'].get('provisional_flags', [])) or 'none'}`"
        )
        lines.append("")

    lines.extend(["## Paired Deltas", ""])
    for pair in comparisons:
        lines.append(f"### `{pair['left_run']}` vs `{pair['right_run']}`")
        for metric_name in PRIMARY_METRICS:
            result = pair["metrics"][metric_name]
            threshold = PRACTICAL_DIFFERENCE_THRESHOLDS[metric_name]
            lines.append(
                f"- `{metric_name}`: delta=`{result['delta_left_minus_right']}` "
                f"CI=`{format_interval(result['confidence_interval']) or 'none'}` "
                f"paired_rows=`{result['paired_rows']}` "
                f"threshold=`{threshold}` "
                f"meaningful=`{result['practically_meaningful']}`"
            )
        lines.append("")

    return "\n".join(lines) + "\n"


def main():
    args = parse_args()
    runs = discover_runs(args.runs_root, args.run_name)
    if not runs:
        raise SystemExit("No run summaries found.")

    output_md = Path(args.output_md)
    output_csv = Path(args.output_csv)
    output_md.parent.mkdir(parents=True, exist_ok=True)
    output_csv.parent.mkdir(parents=True, exist_ok=True)

    comparisons = build_pairwise_section(
        runs,
        bootstrap_samples=args.bootstrap_samples,
        bootstrap_seed=args.bootstrap_seed,
    )
    write_csv(output_csv, runs)
    output_md.write_text(build_markdown(runs, comparisons, args.bootstrap_samples), encoding="utf-8")

    print(f"Wrote run comparison markdown to {output_md}")
    print(f"Wrote run comparison csv to {output_csv}")


if __name__ == "__main__":
    main()
