#!/usr/bin/env python3

import argparse
import json
from pathlib import Path

from e2r_metrics import (
    DEFAULT_BOOTSTRAP_SAMPLES,
    DEFAULT_BOOTSTRAP_SEED,
    PRIMARY_METRICS,
    compute_summary,
    detect_adjudication_status,
    detect_chair_reconciliation,
    detect_judge_disagreement,
    detect_judge_sensitivity,
    load_annotation_rows,
    load_judge_metadata,
    maybe_load_json,
    write_json,
)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Summarize scored annotation rows into JSON and Markdown outputs."
    )
    parser.add_argument("--annotations", required=True, help="Path to annotated CSV.")
    parser.add_argument("--summary-json", required=True, help="Path to output summary JSON.")
    parser.add_argument("--summary-md", required=True, help="Path to output summary Markdown.")
    parser.add_argument(
        "--judge-metadata",
        help="Optional path to judge_metadata.json. Defaults to <run_dir>/judge_metadata.json when available.",
    )
    parser.add_argument(
        "--adjudication-summary",
        help="Optional path to adjudication agreement_summary.json. Defaults to <run_dir>/adjudication/agreement_summary.json when available.",
    )
    parser.add_argument(
        "--judge-sensitivity",
        help="Optional path to judge_sensitivity.json. Defaults to <run_dir>/judge_sensitivity.json when available.",
    )
    parser.add_argument(
        "--judge-disagreement",
        help="Optional path to judge_disagreement_summary.json. Defaults to <run_dir>/adjudication/judge_disagreement_summary.json when available.",
    )
    parser.add_argument(
        "--chair-reconciliation",
        help="Optional path to chair_reconciliation_summary.json. Defaults to <run_dir>/adjudication/chair_reconciliation_summary.json when available.",
    )
    parser.add_argument(
        "--bootstrap-samples",
        type=int,
        default=DEFAULT_BOOTSTRAP_SAMPLES,
        help="Bootstrap samples used for per-run confidence intervals.",
    )
    parser.add_argument(
        "--bootstrap-seed",
        type=int,
        default=DEFAULT_BOOTSTRAP_SEED,
        help="Random seed used for deterministic bootstrap intervals.",
    )
    return parser.parse_args()


def format_interval(interval):
    if not interval:
        return ""
    return f"[{interval['lower']}, {interval['upper']}]"


def format_value(value):
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False, sort_keys=True)
    return value


def add_key_value_lines(lines, pairs):
    for key, value in pairs:
        lines.append(f"- `{key}`: `{format_value(value)}`")


def resolve_run_context(
    annotation_path,
    judge_metadata_arg,
    adjudication_arg,
    judge_sensitivity_arg,
    judge_disagreement_arg,
    chair_reconciliation_arg,
):
    run_dir = annotation_path.parent
    manifest = maybe_load_json(run_dir / "manifest.json")

    if judge_metadata_arg:
        judge_metadata = load_judge_metadata(judge_metadata_arg)
        if judge_metadata is not None:
            judge_metadata["path"] = str(Path(judge_metadata_arg))
    else:
        judge_metadata = load_judge_metadata(run_dir / "judge_metadata.json")
        if judge_metadata is not None:
            judge_metadata["path"] = str(run_dir / "judge_metadata.json")

    if adjudication_arg:
        adjudication_status = maybe_load_json(adjudication_arg)
        if adjudication_status is not None:
            adjudication_status["path"] = str(Path(adjudication_arg))
    else:
        adjudication_status = None

    if judge_sensitivity_arg:
        judge_sensitivity = maybe_load_json(judge_sensitivity_arg)
        if judge_sensitivity is not None:
            judge_sensitivity["path"] = str(Path(judge_sensitivity_arg))
    else:
        judge_sensitivity = None

    if judge_disagreement_arg:
        judge_disagreement = maybe_load_json(judge_disagreement_arg)
        if judge_disagreement is not None:
            judge_disagreement["path"] = str(Path(judge_disagreement_arg))
    else:
        judge_disagreement = None

    if chair_reconciliation_arg:
        chair_reconciliation = maybe_load_json(chair_reconciliation_arg)
        if chair_reconciliation is not None:
            chair_reconciliation["path"] = str(Path(chair_reconciliation_arg))
    else:
        chair_reconciliation = None

    return (
        run_dir,
        manifest,
        judge_metadata,
        adjudication_status,
        judge_sensitivity,
        judge_disagreement,
        chair_reconciliation,
    )


def build_markdown(summary, manifest):
    lines = [
        "# Annotation Summary",
        "",
        f"- annotations: `{summary['annotation_path']}`",
        f"- total_rows: `{summary['total_rows']}`",
        f"- scored_rows: `{summary['scored_rows']}`",
    ]

    if manifest:
        lines.extend(
            [
                f"- run_name: `{manifest.get('run_name', '')}`",
                f"- model_name: `{manifest.get('model_name', '')}`",
                f"- provider: `{manifest.get('provider', '')}`",
                f"- examples_source: `{manifest.get('examples_source', '')}`",
            ]
        )

    lines.extend(["", "## Headline Metrics", ""])
    for metric_name in PRIMARY_METRICS:
        lines.append(f"- `{metric_name}`: `{summary.get(metric_name)}`")

    lines.extend(["", "## Confidence Intervals", ""])
    for metric_name in PRIMARY_METRICS:
        interval = summary["confidence_intervals"].get(metric_name)
        if interval:
            lines.append(
                f"- `{metric_name}`: `{format_interval(interval)}` (`{interval['method']}`, samples=`{interval['samples']}`)"
            )
        else:
            lines.append(f"- `{metric_name}`: none")

    lines.extend(["", "## Average Score By Dimension", ""])
    for column, value in summary["average_score_by_dimension"].items():
        lines.append(f"- `{column}`: `{value}`")

    lines.extend(["", "## Provisional Flags", ""])
    if summary["provisional_flags"]:
        for flag in summary["provisional_flags"]:
            lines.append(f"- `{flag}`")
    else:
        lines.append("- none")

    lines.extend(["", "## Adjudication Status", ""])
    adjudication_status = summary["adjudication_status"]
    add_key_value_lines(
        lines,
        [
            ("status", adjudication_status.get("status")),
            ("packet_rows", adjudication_status.get("packet_rows")),
            ("completed_rows", adjudication_status.get("completed_rows")),
            ("finalized_rows", adjudication_status.get("finalized_rows")),
            ("failure_label_exact_match_rate", adjudication_status.get("failure_label_exact_match_rate")),
            ("path", adjudication_status.get("path")),
        ],
    )

    lines.extend(["", "## Judge Sensitivity", ""])
    judge_sensitivity = summary["judge_sensitivity"]
    add_key_value_lines(
        lines,
        [
            ("status", judge_sensitivity.get("status")),
            ("judge_model", judge_sensitivity.get("judge_model")),
            ("scored_rows", judge_sensitivity.get("scored_rows")),
            ("changed_rows", judge_sensitivity.get("changed_rows")),
            ("changed_score_rows", judge_sensitivity.get("changed_score_rows")),
            ("changed_failure_rows", judge_sensitivity.get("changed_failure_rows")),
            (
                "preference_sensitivity_exact_agreement",
                judge_sensitivity.get("exact_agreement_by_dimension", {}).get("preference_sensitivity"),
            ),
            ("failure_label_exact_match_rate", judge_sensitivity.get("failure_label_exact_match_rate")),
            ("path", judge_sensitivity.get("path")),
        ],
    )

    lines.extend(["", "## Judge Disagreement", ""])
    judge_disagreement = summary["judge_disagreement"]
    add_key_value_lines(
        lines,
        [
            ("status", judge_disagreement.get("status")),
            ("priority_rows", judge_disagreement.get("priority_rows")),
            ("priority_bucket_counts", judge_disagreement.get("priority_bucket_counts")),
            ("secondary_blank_failure_rows", judge_disagreement.get("secondary_blank_failure_rows")),
            (
                "primary_zero_to_secondary_positive_preference_rows",
                judge_disagreement.get("primary_zero_to_secondary_positive_preference_rows"),
            ),
            ("top_priority_adjudication_ids", judge_disagreement.get("top_priority_adjudication_ids")),
            ("path", judge_disagreement.get("path")),
        ],
    )

    lines.extend(["", "## Chair Reconciliation", ""])
    chair_reconciliation = summary["chair_reconciliation"]
    add_key_value_lines(
        lines,
        [
            ("status", chair_reconciliation.get("status")),
            ("completed_rows", chair_reconciliation.get("completed_rows")),
            ("incomplete_rows", chair_reconciliation.get("incomplete_rows")),
            ("agreement_rows", chair_reconciliation.get("agreement_rows")),
            ("disagreement_rows", chair_reconciliation.get("disagreement_rows")),
            ("priority_bucket_counts", chair_reconciliation.get("priority_bucket_counts")),
            ("top_priority_adjudication_ids", chair_reconciliation.get("top_priority_adjudication_ids")),
            ("path", chair_reconciliation.get("path")),
        ],
    )

    judge_metadata = summary.get("judge_metadata")
    if judge_metadata:
        lines.extend(["", "## Judge Metadata", ""])
        add_key_value_lines(lines, judge_metadata.items())

    lines.extend(["", "## Failure Count Overall", ""])
    if summary["failure_count_overall"]:
        for failure, count in summary["failure_count_overall"].items():
            lines.append(f"- `{failure}`: `{count}`")
    else:
        lines.append("- none")

    return "\n".join(lines) + "\n"


def main():
    args = parse_args()
    annotation_path = Path(args.annotations)
    rows = load_annotation_rows(annotation_path)

    (
        run_dir,
        manifest,
        judge_metadata,
        adjudication_status,
        judge_sensitivity,
        judge_disagreement,
        chair_reconciliation,
    ) = resolve_run_context(
        annotation_path,
        args.judge_metadata,
        args.adjudication_summary,
        args.judge_sensitivity,
        args.judge_disagreement,
        args.chair_reconciliation,
    )

    if adjudication_status is None:
        adjudication_status = detect_adjudication_status(run_dir, manifest=manifest, rows=rows)
    if judge_sensitivity is None:
        judge_sensitivity = detect_judge_sensitivity(run_dir)
    if judge_disagreement is None:
        judge_disagreement = detect_judge_disagreement(run_dir)
    if chair_reconciliation is None:
        chair_reconciliation = detect_chair_reconciliation(run_dir)

    summary = compute_summary(
        rows=rows,
        annotation_path=annotation_path,
        bootstrap_samples=args.bootstrap_samples,
        bootstrap_seed=args.bootstrap_seed,
        judge_metadata=judge_metadata,
        adjudication_status=adjudication_status,
        judge_sensitivity=judge_sensitivity,
        judge_disagreement=judge_disagreement,
        chair_reconciliation=chair_reconciliation,
    )
    if manifest:
        summary["run_manifest"] = {
            "run_name": manifest.get("run_name"),
            "model_name": manifest.get("model_name"),
            "provider": manifest.get("provider"),
            "examples_source": manifest.get("examples_source"),
            "prompt_version": manifest.get("prompt_version"),
        }

    write_json(args.summary_json, summary)
    Path(args.summary_md).write_text(build_markdown(summary, manifest), encoding="utf-8")

    print(f"Wrote summary JSON to {args.summary_json}")
    print(f"Wrote summary Markdown to {args.summary_md}")


if __name__ == "__main__":
    main()
