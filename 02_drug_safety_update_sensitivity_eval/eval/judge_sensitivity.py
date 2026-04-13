"""Judge-sensitivity validation utilities."""

import argparse
import json
import os
import time
from collections import Counter, defaultdict
from pathlib import Path

from eval.run_eval import PROJECT_ROOT, call_model, load_benchmark_items
from eval.scoring import DIMENSIONS, score_response_pair


DEFAULT_SUBSET_CASE_IDS = [
    "DSU-009-medication_use_decision",
    "DSU-019-patient_plain_language",
    "DSU-004-medication_use_decision",
    "DSU-016-patient_plain_language",
    "DSU-021-patient_plain_language",
    "DSU-005-patient_plain_language",
    "DSU-022-caregiver_or_followup",
    "DSU-012-caregiver_or_followup",
    "DSU-026-medication_use_decision",
    "DSU-028-caregiver_or_followup",
]


def parse_run_spec(spec):
    if "=" not in spec:
        raise ValueError(f"Run spec must be label=path, got: {spec}")
    label, path = spec.split("=", 1)
    label = label.strip()
    path = path.strip()
    if not label or not path:
        raise ValueError(f"Run spec must include non-empty label and path, got: {spec}")
    return {"label": label, "path": path}


def load_items_map(data_path):
    items = load_benchmark_items(data_path)
    return {item["case_id"]: item for item in items}


def load_results_map(results_path):
    rows = {}
    with open(results_path) as handle:
        for line in handle:
            row = json.loads(line)
            rows[row["case_id"]] = row
    return rows


def run_judge_sensitivity(run_specs, case_ids, judge_model, data_path, output_path, delay=0.3):
    items_by_case = load_items_map(data_path)
    runs = []

    for spec in run_specs:
        rows = load_results_map(spec["path"])
        missing = [case_id for case_id in case_ids if case_id not in rows]
        if missing:
            raise ValueError(f"Run {spec['label']} is missing case ids: {missing}")
        runs.append({"label": spec["label"], "path": spec["path"], "rows": rows})

    os.makedirs(Path(output_path).parent, exist_ok=True)
    if os.path.exists(output_path):
        os.remove(output_path)

    rejudged_rows = []
    total = len(case_ids) * len(runs)
    index = 0

    for run in runs:
        for case_id in case_ids:
            index += 1
            item = items_by_case[case_id]
            original_row = run["rows"][case_id]
            print(f"[{index}/{total}] {run['label']} {case_id}")
            sonnet_scores = score_response_pair(
                judge_model=judge_model,
                item=item,
                before_response=original_row["before_response"],
                after_response=original_row["after_response"],
                call_model_fn=call_model,
            )
            old_scores = original_row["scores"]
            dimension_deltas = {
                dim: sonnet_scores[dim] - old_scores[dim]
                for dim in DIMENSIONS
                if sonnet_scores.get(dim) is not None and old_scores.get(dim) is not None
            }
            total_delta = None
            if sonnet_scores.get("total") is not None and old_scores.get("total") is not None:
                total_delta = sonnet_scores["total"] - old_scores["total"]
            row = {
                "case_id": case_id,
                "run_label": run["label"],
                "model_name": original_row.get("model_name"),
                "drug_name": original_row["drug_name"],
                "section_changed": original_row["section_changed"],
                "update_direction": original_row["update_direction"],
                "severity_tier": original_row["severity_tier"],
                "prompt_variant": original_row["prompt_variant"],
                "original_judge_model": original_row.get("judge_model"),
                "new_judge_model": judge_model,
                "original_scores": old_scores,
                "rejudged_scores": sonnet_scores,
                "dimension_deltas": dimension_deltas,
                "total_delta": total_delta,
                "material_dimension_divergence": any(
                    abs(delta) > 1 for delta in dimension_deltas.values()
                ),
            }
            rejudged_rows.append(row)
            with open(output_path, "a") as handle:
                handle.write(json.dumps(row, ensure_ascii=False) + "\n")
            time.sleep(delay)

    return rejudged_rows


def summarize_rejudged_rows(rejudged_rows, case_ids):
    by_model = defaultdict(list)
    any_delta_cases = {}
    material_divergence_cases = {}

    for row in rejudged_rows:
        by_model[row["run_label"]].append(row)
        if any(delta != 0 for delta in row["dimension_deltas"].values()):
            any_delta_cases[(row["run_label"], row["case_id"])] = row
        if row["material_dimension_divergence"]:
            material_divergence_cases[(row["run_label"], row["case_id"])] = row

    summary = {
        "case_count": len(case_ids),
        "rejudged_count": len(rejudged_rows),
        "models": {},
        "any_delta_cases": list(any_delta_cases.values()),
        "material_divergence_cases": list(material_divergence_cases.values()),
        "section_mix": Counter(),
        "direction_mix": Counter(),
        "prompt_mix": Counter(),
    }

    case_meta_added = set()
    for row in rejudged_rows:
        if row["case_id"] not in case_meta_added:
            summary["section_mix"][row["section_changed"]] += 1
            summary["direction_mix"][row["update_direction"]] += 1
            summary["prompt_mix"][row["prompt_variant"]] += 1
            case_meta_added.add(row["case_id"])

    for run_label, rows in sorted(by_model.items()):
        exact_by_dimension = {}
        max_abs_by_dimension = {}
        mean_original = 0.0
        mean_rejudged = 0.0

        for dim in DIMENSIONS:
            deltas = [row["dimension_deltas"][dim] for row in rows if dim in row["dimension_deltas"]]
            exact_by_dimension[dim] = sum(delta == 0 for delta in deltas)
            max_abs_by_dimension[dim] = max(abs(delta) for delta in deltas) if deltas else 0

        original_totals = [row["original_scores"]["total"] for row in rows if row["original_scores"].get("total") is not None]
        rejudged_totals = [row["rejudged_scores"]["total"] for row in rows if row["rejudged_scores"].get("total") is not None]
        if original_totals:
            mean_original = sum(original_totals) / len(original_totals)
        if rejudged_totals:
            mean_rejudged = sum(rejudged_totals) / len(rejudged_totals)

        summary["models"][run_label] = {
            "rows": rows,
            "count": len(rows),
            "exact_match_all_dims": sum(all(delta == 0 for delta in row["dimension_deltas"].values()) for row in rows),
            "exact_by_dimension": exact_by_dimension,
            "max_abs_by_dimension": max_abs_by_dimension,
            "mean_original_total": mean_original,
            "mean_rejudged_total": mean_rejudged,
            "material_divergence_count": sum(row["material_dimension_divergence"] for row in rows),
        }

    return summary


def build_judge_sensitivity_report(rejudged_rows, case_ids, judge_model):
    summary = summarize_rejudged_rows(rejudged_rows, case_ids)
    original_judges = sorted(
        {
            row["original_judge_model"]
            for row in rejudged_rows
            if row.get("original_judge_model")
        }
    )
    lines = [
        "# Sonnet Judge Sensitivity Validation",
        "",
        "## Setup",
        "",
        f"- **New judge model**: {judge_model}",
        f"- **Original judge model(s)**: {', '.join(original_judges) or 'unknown'}",
        f"- **Benchmark items re-judged**: {summary['case_count']} case ids x {len(summary['models'])} model runs = {summary['rejudged_count']} scored pairs",
        f"- **Material divergence (>1 point on any dimension)**: {'yes' if summary['material_divergence_cases'] else 'no'}",
        "",
        "## Subset Composition",
        "",
        f"- **Case ids**: {', '.join(case_ids)}",
        f"- **Section mix**: {_format_counter(summary['section_mix'])}",
        f"- **Direction mix**: {_format_counter(summary['direction_mix'])}",
        f"- **Prompt mix**: {_format_counter(summary['prompt_mix'])}",
        "",
        "## Model-Level Agreement",
        "",
        "| Model | Mean total (original) | Mean total (Sonnet) | Exact all-dim matches | Material divergences |",
        "|---|---:|---:|---:|---:|",
    ]

    for run_label, model_summary in sorted(summary["models"].items()):
        lines.append(
            "| "
            f"{run_label} | "
            f"{model_summary['mean_original_total']:.2f} | "
            f"{model_summary['mean_rejudged_total']:.2f} | "
            f"{model_summary['exact_match_all_dims']}/{model_summary['count']} | "
            f"{model_summary['material_divergence_count']} |"
        )

    lines.extend(
        [
            "",
            "## Dimension-Level Agreement",
            "",
            "| Model | update_uptake | stale_advice_avoidance | safety_severity_calibration | actionability_and_followup_guidance | source_grounded_communication |",
            "|---|---:|---:|---:|---:|---:|",
        ]
    )

    for run_label, model_summary in sorted(summary["models"].items()):
        exact = model_summary["exact_by_dimension"]
        count = model_summary["count"]
        lines.append(
            "| "
            f"{run_label} | "
            f"{exact['update_uptake']}/{count} | "
            f"{exact['stale_advice_avoidance']}/{count} | "
            f"{exact['safety_severity_calibration']}/{count} | "
            f"{exact['actionability_and_followup_guidance']}/{count} | "
            f"{exact['source_grounded_communication']}/{count} |"
        )

    lines.extend(
        [
            "",
            "## Max Absolute Dimension Delta",
            "",
            "| Model | update_uptake | stale_advice_avoidance | safety_severity_calibration | actionability_and_followup_guidance | source_grounded_communication |",
            "|---|---:|---:|---:|---:|---:|",
        ]
    )

    for run_label, model_summary in sorted(summary["models"].items()):
        max_abs = model_summary["max_abs_by_dimension"]
        lines.append(
            "| "
            f"{run_label} | "
            f"{max_abs['update_uptake']} | "
            f"{max_abs['stale_advice_avoidance']} | "
            f"{max_abs['safety_severity_calibration']} | "
            f"{max_abs['actionability_and_followup_guidance']} | "
            f"{max_abs['source_grounded_communication']} |"
        )

    lines.extend(["", "## Rows With Any Judge Delta", ""])
    if not summary["any_delta_cases"]:
        lines.append("No judge deltas on this subset.")
    else:
        lines.extend(
            [
                "| Model | Case | Drug | Original total | Sonnet total | Dimension deltas |",
                "|---|---|---|---:|---:|---|",
            ]
        )
        for row in sorted(
            summary["any_delta_cases"],
            key=lambda row: (
                -max(abs(delta) for delta in row["dimension_deltas"].values()),
                row["run_label"],
                row["case_id"],
            ),
        ):
            lines.append(
                "| "
                f"{row['run_label']} | "
                f"{row['case_id']} | "
                f"{row['drug_name']} | "
                f"{row['original_scores']['total']} | "
                f"{row['rejudged_scores']['total']} | "
                f"{_format_dimension_deltas(row['dimension_deltas'])} |"
            )

    lines.extend(["", "## Material Divergences (>1 on any dimension)", ""])
    if not summary["material_divergence_cases"]:
        lines.append("No material judge divergences detected on this subset.")
    else:
        for row in sorted(summary["material_divergence_cases"], key=lambda row: (row["run_label"], row["case_id"])):
            lines.append(
                "- "
                f"**{row['run_label']} / {row['case_id']}**: {_format_dimension_deltas(row['dimension_deltas'])}"
            )

    lines.extend(["", "---", "*Generated by Drug Safety Update Sensitivity Eval judge-sensitivity tooling*"])
    return "\n".join(lines) + "\n"


def write_judge_sensitivity_report(report_text, output_path):
    os.makedirs(Path(output_path).parent, exist_ok=True)
    with open(output_path, "w") as handle:
        handle.write(report_text)
    return output_path


def _format_counter(counter):
    if not counter:
        return "None"
    return ", ".join(f"{key} ({value})" for key, value in sorted(counter.items()))


def _format_dimension_deltas(dimension_deltas):
    parts = []
    for dim in DIMENSIONS:
        delta = dimension_deltas.get(dim, 0)
        if delta:
            parts.append(f"{dim} {delta:+d}")
    return ", ".join(parts) if parts else "none"


def main(argv=None):
    parser = argparse.ArgumentParser(description="Run a Sonnet judge-sensitivity validation subset")
    parser.add_argument("--run", dest="runs", action="append", required=True, help="Run spec in the form label=path/to/eval_results.jsonl")
    parser.add_argument("--judge", default="claude-sonnet-4-6", help="Judge model for re-scoring")
    parser.add_argument("--data", default=str(PROJECT_ROOT / "data" / "benchmark_items.jsonl"), help="Path to benchmark data")
    parser.add_argument("--raw-output", default=str(PROJECT_ROOT / "eval" / "output" / "judge_sensitivity_sonnet_subset" / "rejudged_scores.jsonl"), help="Path to raw re-judged JSONL")
    parser.add_argument("--report-path", default=str(PROJECT_ROOT / "reports" / "judge_sensitivity_sonnet_subset.md"), help="Path to markdown report")
    parser.add_argument("--case-id", dest="case_ids", action="append", default=None, help="Case id to include; defaults to curated 10-item subset")
    parser.add_argument("--delay", type=float, default=0.3, help="Delay between judge API calls in seconds")
    args = parser.parse_args(argv)

    run_specs = [parse_run_spec(spec) for spec in args.runs]
    case_ids = args.case_ids or DEFAULT_SUBSET_CASE_IDS

    rejudged_rows = run_judge_sensitivity(
        run_specs=run_specs,
        case_ids=case_ids,
        judge_model=args.judge,
        data_path=args.data,
        output_path=args.raw_output,
        delay=args.delay,
    )
    report_text = build_judge_sensitivity_report(rejudged_rows, case_ids, args.judge)
    report_path = write_judge_sensitivity_report(report_text, args.report_path)
    print(f"Judge-sensitivity report written to: {report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
