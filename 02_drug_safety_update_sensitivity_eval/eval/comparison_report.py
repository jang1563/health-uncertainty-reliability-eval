"""Cross-model comparison report generation for benchmark runs."""

import argparse
import json
from collections import Counter, OrderedDict, defaultdict
from pathlib import Path

from eval.report_generator import DIMENSIONS, compute_metrics, load_results_from_jsonl
from eval.run_metadata import (
    compute_case_id_hash_from_results,
    extract_row_metadata,
    load_run_manifest,
)

SUMMARY_METRICS = [
    ("scored_item_count", "Scored items", "count"),
    ("judge_error_count", "Judge errors", "count"),
    ("update_uptake_rate", "Overall update uptake", "ratio"),
    ("mean_total_score", "Mean total (/10)", "score"),
    ("partial_uptake_count", "Partial shifts", "count"),
    ("failed_uptake_count", "Failed shifts", "count"),
    ("stale_reassurance_rate", "Stale reassurance", "ratio"),
    ("stale_alarmism_rate", "Stale alarmism", "ratio"),
    ("boxed_warning_sensitivity", "Boxed warning sensitivity", "ratio"),
    (
        "false_update_sensitivity_on_controls",
        "False update sensitivity (controls)",
        "ratio",
    ),
]


def parse_run_spec(run_spec):
    """Parse a CLI run spec in the form label=path or just path."""
    if "=" in run_spec:
        label, path_str = run_spec.split("=", 1)
        label = label.strip()
        path = Path(path_str.strip())
    else:
        path = Path(run_spec.strip())
        label = path.parent.name or path.stem

    if not label:
        raise ValueError(f"Invalid run label in spec: {run_spec}")
    if not str(path):
        raise ValueError(f"Invalid run path in spec: {run_spec}")
    return label, path


def load_named_runs(run_specs):
    """Load results keyed by model label."""
    runs = OrderedDict()
    for run_spec in run_specs:
        label, path = parse_run_spec(run_spec)
        if label in runs:
            raise ValueError(f"Duplicate run label: {label}")
        results = load_results_from_jsonl(path)
        runs[label] = {
            "path": path,
            "results": results,
            "manifest": load_run_manifest(path),
            "row_metadata": extract_row_metadata(results),
        }
    if not runs:
        raise ValueError("At least one --run spec is required")
    return runs


def write_comparison_report(
    run_specs,
    output_path,
    title="Cross-Model Comparison",
    judge_sensitivity_path=None,
):
    """Generate and write the comparison report."""
    runs = load_named_runs(run_specs)
    judge_sensitivity_summary = load_judge_sensitivity_summary(judge_sensitivity_path)
    report_text = build_comparison_report(
        runs,
        title=title,
        judge_sensitivity_summary=judge_sensitivity_summary,
    )
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(report_text)
    return output_path


def build_comparison_report(
    runs,
    title="Cross-Model Comparison",
    judge_sensitivity_summary=None,
):
    """Build report markdown for multiple named runs."""
    comparability = validate_runs(runs)
    metrics_by_label = OrderedDict(
        (label, compute_metrics(payload["results"])) for label, payload in runs.items()
    )
    section_summary = compute_section_comparison(runs)
    prompt_variant_summary = compute_prompt_variant_comparison(runs)
    disagreement_rows = compute_case_disagreements(runs)
    shift_analysis = compute_shift_analysis(runs)

    labels = list(runs.keys())
    lines = [
        f"# {title}",
        "",
        "## Inputs",
        "",
        "| Label | Target model | Judge | Metadata source | Results path | Total items |",
        "|---|---|---|---|---|---:|",
    ]

    for label, payload in runs.items():
        run_metadata = payload["run_metadata"]
        lines.append(
            f"| {label} | {run_metadata.get('model_name') or 'unknown'} | "
            f"{run_metadata.get('judge_model') or 'unknown'} | "
            f"{run_metadata['metadata_source']} | `{payload['path']}` | {len(payload['results'])} |"
        )

    lines += [
        "",
        "## Comparability Checks",
        "",
        "| Check | Value |",
        "|---|---|",
        f"| Matching case sets across runs | yes ({comparability['dataset_item_count']} cases) |",
        f"| Shared judge model | {comparability.get('judge_model') or 'not fully verified'} |",
        f"| Shared dataset case-id hash | `{comparability['dataset_case_id_hash']}` |",
        "",
        "## Key Takeaways",
        "",
    ]
    for takeaway in build_key_takeaways(
        metrics_by_label,
        section_summary,
        prompt_variant_summary,
        judge_sensitivity_summary=judge_sensitivity_summary,
    ):
        lines.append(f"- {takeaway}")

    if judge_sensitivity_summary:
        lines += [
            "",
            "## Judge Sensitivity",
            "",
            "| Alternate judge | Original judge(s) | Re-judged rows | Rows with any delta | Material divergences |",
            "|---|---|---:|---:|---:|",
            f"| {judge_sensitivity_summary['new_judge_model'] or 'unknown'} | "
            f"{judge_sensitivity_summary['original_judges_text']} | "
            f"{judge_sensitivity_summary['row_count']} | "
            f"{judge_sensitivity_summary['rows_with_any_delta']} | "
            f"{judge_sensitivity_summary['material_divergence_count']} |",
            "",
            "| Model | Exact all-dim matches | Rows with any delta | Max absolute dimension delta |",
            "|---|---:|---:|---:|",
        ]
        for label, model_summary in judge_sensitivity_summary["models"].items():
            lines.append(
                f"| {label} | "
                f"{model_summary['exact_all_dim_matches']}/{model_summary['row_count']} | "
                f"{model_summary['rows_with_any_delta']} | "
                f"{model_summary['max_abs_dimension_delta']} |"
            )
        lines += [
            "",
            judge_sensitivity_summary["headline"],
        ]

    lines += [
        "",
        "## Summary Metrics",
        "",
        "| Metric | " + " | ".join(labels) + " |",
        "|---|"
        + "|".join("---:" for _ in labels)
        + "|",
    ]

    for metric_key, metric_label, metric_kind in SUMMARY_METRICS:
        formatted_values = [
            format_metric(metrics_by_label[label].get(metric_key), metric_kind)
            for label in labels
        ]
        lines.append(f"| {metric_label} | " + " | ".join(formatted_values) + " |")

    lines += [
        "",
        "## Metric Rankings",
        "",
        "| Metric | Ranking |",
        "|---|---|",
    ]

    for metric_key, metric_label, metric_kind in SUMMARY_METRICS:
        lines.append(
            f"| {metric_label} | {rank_metric(metrics_by_label, metric_key, metric_kind)} |"
        )

    lines += [
        "",
        "## Dimension Means",
        "",
        "| Dimension | " + " | ".join(labels) + " |",
        "|---|"
        + "|".join("---:" for _ in labels)
        + "|",
    ]

    for dimension in DIMENSIONS:
        metric_key = f"mean_{dimension}"
        lines.append(
            f"| {dimension} | "
            + " | ".join(
                format_metric(metrics_by_label[label].get(metric_key), "score")
                for label in labels
            )
            + " |"
        )

    lines += [
        f"| total | "
        + " | ".join(
            format_metric(metrics_by_label[label].get("mean_total_score"), "score")
            for label in labels
        )
        + " |",
        "",
        "## Per-Section Comparison",
        "",
        "| Section | "
        + " | ".join(f"{label} update / total / uptake<2" for label in labels)
        + " | Update spread | Total spread |",
        "|---|"
        + "|".join("---:" for _ in labels)
        + "|---:|---:|",
    ]

    for row in section_summary:
        per_model = []
        for label in labels:
            stats = row["models"][label]
            mean_uptake = format_metric(stats["mean_update_uptake"], "score")
            mean_total = format_metric(stats["mean_total_score"], "score")
            per_model.append(f"{mean_uptake} / {mean_total} / {stats['suboptimal_count']}")
        lines.append(
            f"| {row['section']} | "
            + " | ".join(per_model)
            + f" | {format_metric(row['update_spread'], 'score')} | {format_metric(row['total_spread'], 'score')} |"
        )

    lines += [
        "",
        "## Prompt Variant Comparison",
        "",
        "| Variant | "
        + " | ".join(f"{label} update / total / uptake<2" for label in labels)
        + " | Update spread | Total spread |",
        "|---|"
        + "|".join("---:" for _ in labels)
        + "|---:|---:|",
    ]

    for row in prompt_variant_summary:
        per_model = []
        for label in labels:
            stats = row["models"][label]
            mean_uptake = format_metric(stats["mean_update_uptake"], "score")
            mean_total = format_metric(stats["mean_total_score"], "score")
            per_model.append(f"{mean_uptake} / {mean_total} / {stats['suboptimal_count']}")
        lines.append(
            f"| {row['prompt_variant']} | "
            + " | ".join(per_model)
            + f" | {format_metric(row['update_spread'], 'score')} | {format_metric(row['total_spread'], 'score')} |"
        )

    lines += [
        "",
        "## Per-Case Disagreements",
        "",
    ]

    if disagreement_rows:
        lines += [
            "| Case | Drug | Section | Direction | "
            + " | ".join(f"{label} update/total" for label in labels)
            + " | Differing dimensions |",
            "|---|---|---|---|"
            + "|".join("---:" for _ in labels)
            + "|---|",
        ]
        for row in disagreement_rows:
            per_model_values = [
                format_case_score_summary(row["scores_by_model"].get(label))
                for label in labels
            ]
            lines.append(
                f"| {row['case_id']} | {row['drug_name']} | {row['section_changed']} | "
                f"{row['update_direction']} | "
                + " | ".join(per_model_values)
                + f" | {', '.join(row['difference_keys'])} |"
            )
    else:
        lines.append("No score disagreements across the supplied runs.")

    lines += [
        "",
        "## Suboptimal Shift Analysis",
        "",
        "| Model | Partial shifts (1) | Failed shifts (0) | Cases with update_uptake < 2 |",
        "|---|---:|---:|---|",
    ]

    for label in labels:
        partials = sorted(shift_analysis["partials_by_model"][label])
        failures = sorted(shift_analysis["failures_by_model"][label])
        suboptimal = sorted(shift_analysis["suboptimal_by_model"][label])
        case_list = format_case_list(suboptimal)
        lines.append(
            f"| {label} | {len(partials)} | {len(failures)} | {case_list} |"
        )

    shared_suboptimal = sorted(shift_analysis["shared_suboptimal"])
    lines += [
        "",
        f"Shared suboptimal cases across all models: {format_case_list(shared_suboptimal)}",
        "",
        "### Suboptimal Patterns by Section",
        "",
        "| Model | Section distribution among update_uptake < 2 cases |",
        "|---|---|",
    ]

    for label in labels:
        pattern_text = format_section_counter(shift_analysis["suboptimal_sections"][label])
        lines.append(f"| {label} | {pattern_text} |")

    lines += [
        "",
        "### Model-Unique Suboptimal Cases",
        "",
    ]

    for label in labels:
        unique_suboptimal = sorted(shift_analysis["unique_suboptimal"][label])
        lines.append(f"- **{label}**: {format_case_list(unique_suboptimal)}")

    lines += [
        "",
        "## Stale Rate Trade-Offs",
        "",
        "| Model | Stale reassurance | Stale alarmism | Difference |",
        "|---|---:|---:|---:|",
    ]

    for label in labels:
        stale_reassurance = metrics_by_label[label].get("stale_reassurance_rate")
        stale_alarmism = metrics_by_label[label].get("stale_alarmism_rate")
        difference = None
        if stale_reassurance is not None and stale_alarmism is not None:
            difference = stale_reassurance - stale_alarmism
        lines.append(
            f"| {label} | {format_metric(stale_reassurance, 'ratio')} | "
            f"{format_metric(stale_alarmism, 'ratio')} | {format_metric(difference, 'signed_ratio')} |"
        )

    lines += [
        "",
        build_tradeoff_summary(metrics_by_label),
        "",
        "---",
        "*Generated by Drug Safety Update Sensitivity Eval comparison tooling*",
    ]

    return "\n".join(lines) + "\n"


def compute_section_comparison(runs):
    """Compute mean update uptake and failures by section across runs."""
    section_names = sorted(
        {
            result["section_changed"]
            for payload in runs.values()
            for result in payload["results"]
        }
    )
    rows = []
    for section_name in section_names:
        row = {
            "section": section_name,
            "models": {},
            "update_spread": None,
            "total_spread": None,
        }
        scored_uptake_values = []
        scored_total_values = []
        for label, payload in runs.items():
            section_results = [
                result
                for result in payload["results"]
                if result["section_changed"] == section_name
            ]
            scored_results = [
                result
                for result in section_results
                if not result.get("scores", {}).get("judge_error")
            ]
            update_scores = [
                result["scores"]["update_uptake"]
                for result in scored_results
                if isinstance(result["scores"].get("update_uptake"), (int, float))
            ]
            total_scores = [
                result["scores"]["total"]
                for result in scored_results
                if isinstance(result["scores"].get("total"), (int, float))
            ]
            mean_uptake = mean(update_scores)
            mean_total = mean(total_scores)
            suboptimal_count = sum(
                1
                for result in scored_results
                if result["scores"].get("update_uptake") in {0, 1}
            )
            row["models"][label] = {
                "mean_update_uptake": mean_uptake,
                "mean_total_score": mean_total,
                "suboptimal_count": suboptimal_count,
            }
            if mean_uptake is not None:
                scored_uptake_values.append(mean_uptake)
            if mean_total is not None:
                scored_total_values.append(mean_total)

        row["update_spread"] = (
            max(scored_uptake_values) - min(scored_uptake_values)
            if len(scored_uptake_values) > 1
            else 0
        )
        row["total_spread"] = (
            max(scored_total_values) - min(scored_total_values)
            if len(scored_total_values) > 1
            else 0
        )
        rows.append(row)

    rows.sort(key=lambda row: (-row["update_spread"], -row["total_spread"], row["section"]))
    return rows


def compute_prompt_variant_comparison(runs):
    """Compute comparison summaries by prompt variant."""
    return compute_group_comparison(
        runs,
        group_key="prompt_variant",
        output_label_key="prompt_variant",
    )


def compute_group_comparison(runs, group_key, output_label_key):
    """Compute group comparisons for sections, variants, or other categorical fields."""
    group_names = sorted(
        {
            result[group_key]
            for payload in runs.values()
            for result in payload["results"]
        }
    )
    rows = []
    for group_name in group_names:
        row = {
            output_label_key: group_name,
            "models": {},
            "update_spread": None,
            "total_spread": None,
        }
        scored_uptake_values = []
        scored_total_values = []
        for label, payload in runs.items():
            grouped_results = [
                result
                for result in payload["results"]
                if result[group_key] == group_name
            ]
            scored_results = [
                result
                for result in grouped_results
                if not result.get("scores", {}).get("judge_error")
            ]
            update_scores = [
                result["scores"]["update_uptake"]
                for result in scored_results
                if isinstance(result["scores"].get("update_uptake"), (int, float))
            ]
            total_scores = [
                result["scores"]["total"]
                for result in scored_results
                if isinstance(result["scores"].get("total"), (int, float))
            ]
            mean_uptake = mean(update_scores)
            mean_total = mean(total_scores)
            suboptimal_count = sum(
                1
                for result in scored_results
                if result["scores"].get("update_uptake") in {0, 1}
            )
            row["models"][label] = {
                "mean_update_uptake": mean_uptake,
                "mean_total_score": mean_total,
                "suboptimal_count": suboptimal_count,
            }
            if mean_uptake is not None:
                scored_uptake_values.append(mean_uptake)
            if mean_total is not None:
                scored_total_values.append(mean_total)

        row["update_spread"] = (
            max(scored_uptake_values) - min(scored_uptake_values)
            if len(scored_uptake_values) > 1
            else 0
        )
        row["total_spread"] = (
            max(scored_total_values) - min(scored_total_values)
            if len(scored_total_values) > 1
            else 0
        )
        rows.append(row)

    rows.sort(
        key=lambda row: (-row["update_spread"], -row["total_spread"], row[output_label_key])
    )
    return rows


def compute_case_disagreements(runs):
    """Return case-level disagreements across scored dimensions."""
    by_case = defaultdict(dict)
    metadata = {}

    for label, payload in runs.items():
        for result in payload["results"]:
            by_case[result["case_id"]][label] = result
            metadata[result["case_id"]] = {
                "drug_name": result["drug_name"],
                "section_changed": result["section_changed"],
                "update_direction": result["update_direction"],
            }

    rows = []
    labels = list(runs.keys())
    for case_id, per_model in by_case.items():
        scores_by_model = {}
        total_scores = []
        difference_keys = []
        missing_or_error = False

        for label in labels:
            result = per_model.get(label)
            if not result:
                scores_by_model[label] = None
                missing_or_error = True
                continue

            if result.get("scores", {}).get("judge_error"):
                scores_by_model[label] = "judge_error"
                missing_or_error = True
                continue

            scores_by_model[label] = {
                key: result["scores"].get(key)
                for key in DIMENSIONS + ["total"]
            }
            total_value = result["scores"].get("total")
            if isinstance(total_value, (int, float)):
                total_scores.append(total_value)

        for key in DIMENSIONS + ["total"]:
            values = []
            for label in labels:
                entry = scores_by_model.get(label)
                if isinstance(entry, dict):
                    values.append(entry.get(key))
            if values and len(set(values)) > 1:
                difference_keys.append(key)

        total_spread = (
            max(total_scores) - min(total_scores)
            if len(total_scores) > 1
            else 0
        )
        if missing_or_error or difference_keys:
            row = {
                "case_id": case_id,
                "scores_by_model": scores_by_model,
                "difference_keys": difference_keys or ["missing_or_judge_error"],
                "total_spread": total_spread,
            }
            row.update(metadata[case_id])
            rows.append(row)

    rows.sort(
        key=lambda row: (
            -len(row["difference_keys"]),
            -row["total_spread"],
            row["case_id"],
        )
    )
    return rows


def compute_shift_analysis(runs):
    """Compute shared and unique partial/failure uptake cases."""
    partials_by_model = OrderedDict()
    failures_by_model = OrderedDict()
    suboptimal_by_model = OrderedDict()
    suboptimal_sections = OrderedDict()

    for label, payload in runs.items():
        partial_results = [
            result
            for result in payload["results"]
            if not result.get("scores", {}).get("judge_error")
            and result["scores"].get("update_uptake") == 1
        ]
        failed_results = [
            result
            for result in payload["results"]
            if not result.get("scores", {}).get("judge_error")
            and result["scores"].get("update_uptake") == 0
        ]
        partials_by_model[label] = {result["case_id"] for result in partial_results}
        failures_by_model[label] = {result["case_id"] for result in failed_results}
        suboptimal_results = partial_results + failed_results
        suboptimal_by_model[label] = {result["case_id"] for result in suboptimal_results}
        suboptimal_sections[label] = Counter(
            result["section_changed"] for result in suboptimal_results
        )

    suboptimal_sets = list(suboptimal_by_model.values())
    shared_suboptimal = set.intersection(*suboptimal_sets) if suboptimal_sets else set()

    unique_suboptimal = OrderedDict()
    for label, suboptimal in suboptimal_by_model.items():
        other_suboptimal = set().union(
            *[other for other_label, other in suboptimal_by_model.items() if other_label != label]
        )
        unique_suboptimal[label] = suboptimal - other_suboptimal

    return {
        "partials_by_model": partials_by_model,
        "failures_by_model": failures_by_model,
        "suboptimal_by_model": suboptimal_by_model,
        "shared_suboptimal": shared_suboptimal,
        "unique_suboptimal": unique_suboptimal,
        "suboptimal_sections": suboptimal_sections,
    }


def build_tradeoff_summary(metrics_by_label):
    """Summarize stale reassurance vs stale alarmism trade-offs."""
    labels = list(metrics_by_label.keys())
    if not labels:
        return "No runs supplied."

    best_reassurance_labels = best_labels(metrics_by_label, "stale_reassurance_rate")
    best_alarmism_labels = best_labels(metrics_by_label, "stale_alarmism_rate")
    best_reassurance_value = metrics_by_label[best_reassurance_labels[0]].get(
        "stale_reassurance_rate"
    )
    best_alarmism_value = metrics_by_label[best_alarmism_labels[0]].get(
        "stale_alarmism_rate"
    )

    sentences = [
        f"Lowest stale reassurance rate: {format_label_group(best_reassurance_labels)} ({format_metric(best_reassurance_value, 'ratio')}).",
        f"Lowest stale alarmism rate: {format_label_group(best_alarmism_labels)} ({format_metric(best_alarmism_value, 'ratio')}).",
    ]

    for label in labels:
        reassurance = metrics_by_label[label].get("stale_reassurance_rate")
        alarmism = metrics_by_label[label].get("stale_alarmism_rate")
        if reassurance is None or alarmism is None:
            continue
        if abs(reassurance - alarmism) >= 0.05:
            dominant = "stale reassurance" if reassurance > alarmism else "stale alarmism"
            sentences.append(
                f"**{label}** is more exposed to {dominant} ({format_metric(reassurance, 'ratio')} vs {format_metric(alarmism, 'ratio')})."
            )

    return " ".join(sentences)


def build_key_takeaways(
    metrics_by_label,
    section_summary,
    prompt_variant_summary,
    judge_sensitivity_summary=None,
):
    """Build short narrative takeaways for the comparison report."""
    labels = list(metrics_by_label.keys())
    if not labels:
        return ["No runs supplied."]

    takeaways = []
    best_total_labels = best_labels_desc(metrics_by_label, "mean_total_score")
    best_total_value = metrics_by_label[best_total_labels[0]].get("mean_total_score")
    takeaways.append(
        f"Overall front-runner by mean total score: {format_label_group(best_total_labels)} ({format_metric(best_total_value, 'score')}/10)."
    )

    best_uptake_labels = best_labels_desc(metrics_by_label, "update_uptake_rate")
    best_uptake_value = metrics_by_label[best_uptake_labels[0]].get("update_uptake_rate")
    takeaways.append(
        f"Best overall update uptake: {format_label_group(best_uptake_labels)} ({format_metric(best_uptake_value, 'ratio')})."
    )

    if section_summary:
        top_section = max(
            section_summary,
            key=lambda row: (row["update_spread"], row["total_spread"]),
        )
        if top_section["update_spread"] > 0 or top_section["total_spread"] > 0:
            takeaways.append(
                f"Largest section gap: **{top_section['section']}** "
                f"(update spread {format_metric(top_section['update_spread'], 'score')}, "
                f"total spread {format_metric(top_section['total_spread'], 'score')})."
            )

    if prompt_variant_summary:
        top_variant = max(
            prompt_variant_summary,
            key=lambda row: (row["update_spread"], row["total_spread"]),
        )
        if top_variant["update_spread"] > 0 or top_variant["total_spread"] > 0:
            takeaways.append(
                f"Largest prompt-variant gap: **{top_variant['prompt_variant']}** "
                f"(update spread {format_metric(top_variant['update_spread'], 'score')}, "
                f"total spread {format_metric(top_variant['total_spread'], 'score')})."
            )

    for label in labels:
        partials = metrics_by_label[label].get("partial_uptake_count") or 0
        failures = metrics_by_label[label].get("failed_uptake_count") or 0
        if partials or failures:
            takeaways.append(
                f"**{label}** recorded {partials} partial shift(s) and {failures} outright failure(s)."
            )

    if not any(metrics_by_label[label].get("failed_uptake_count") for label in labels):
        takeaways.append("Neither model produced an outright update_uptake=0 failure on this benchmark run.")

    if judge_sensitivity_summary:
        takeaways.append(judge_sensitivity_summary["takeaway"])

    return takeaways


def rank_metric(metrics_by_label, metric_key, metric_kind):
    """Rank models for one metric."""
    reverse = metric_key in {
        "scored_item_count",
        "update_uptake_rate",
        "boxed_warning_sensitivity",
        "mean_total_score",
    }
    items = []
    for label, metrics in metrics_by_label.items():
        value = metrics.get(metric_key)
        items.append((label, value))

    items.sort(
        key=lambda item: (
            _sort_value(item[1]),
            item[0],
        ),
        reverse=reverse,
    )
    rendered = []
    for index, (label, value) in enumerate(items):
        if index > 0:
            previous_value = items[index - 1][1]
            separator = " = " if values_equal(previous_value, value) else " > "
            rendered.append(separator)
        rendered.append(f"{label} ({format_metric(value, metric_kind)})")
    return "".join(rendered)


def format_metric(value, metric_kind):
    """Format a metric value for markdown tables."""
    if metric_kind == "count":
        return str(value) if value is not None else "N/A"
    if metric_kind == "ratio":
        return f"{value:.1%}" if value is not None else "N/A"
    if metric_kind == "signed_ratio":
        return f"{value:+.1%}" if value is not None else "N/A"
    if metric_kind == "score":
        return f"{value:.2f}" if value is not None else "N/A"
    if metric_kind == "score_or_error":
        if value == "judge_error":
            return "judge_error"
        return format_metric(value, "score")
    return str(value)


def format_case_list(case_ids):
    """Format a list of case IDs for markdown."""
    if not case_ids:
        return "None"
    return ", ".join(f"`{case_id}`" for case_id in case_ids)


def format_case_score_summary(score_entry):
    """Format one model's case-level update/total summary."""
    if score_entry is None:
        return "missing"
    if score_entry == "judge_error":
        return "judge_error"
    update = format_metric(score_entry.get("update_uptake"), "score")
    total = format_metric(score_entry.get("total"), "score")
    return f"{update}/{total}"


def format_section_counter(counter):
    """Format a section counter for markdown."""
    if not counter:
        return "None"
    return ", ".join(
        f"{section} ({count})"
        for section, count in sorted(counter.items(), key=lambda item: (-item[1], item[0]))
    )


def mean(values):
    return sum(values) / len(values) if values else None


def load_judge_sensitivity_summary(judge_sensitivity_path):
    """Load and summarize optional judge-sensitivity re-judging output."""
    if not judge_sensitivity_path:
        return None

    path = Path(judge_sensitivity_path)
    rows = []
    with open(path) as handle:
        for line in handle:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    if not rows:
        return None

    original_judges = sorted(
        {
            row.get("original_judge_model")
            for row in rows
            if row.get("original_judge_model")
        }
    )
    new_judge_models = sorted(
        {
            row.get("new_judge_model")
            for row in rows
            if row.get("new_judge_model")
        }
    )
    models = OrderedDict()
    for label in sorted({row["run_label"] for row in rows}):
        model_rows = [row for row in rows if row["run_label"] == label]
        rows_with_any_delta = sum(
            any(delta != 0 for delta in row["dimension_deltas"].values())
            for row in model_rows
        )
        max_abs_dimension_delta = 0
        for row in model_rows:
            if row["dimension_deltas"]:
                max_abs_dimension_delta = max(
                    max_abs_dimension_delta,
                    max(abs(delta) for delta in row["dimension_deltas"].values()),
                )
        models[label] = {
            "row_count": len(model_rows),
            "exact_all_dim_matches": sum(
                all(delta == 0 for delta in row["dimension_deltas"].values())
                for row in model_rows
            ),
            "rows_with_any_delta": rows_with_any_delta,
            "max_abs_dimension_delta": max_abs_dimension_delta,
        }

    row_count = len(rows)
    rows_with_any_delta = sum(
        any(delta != 0 for delta in row["dimension_deltas"].values())
        for row in rows
    )
    material_divergence_count = sum(
        1 for row in rows if row.get("material_dimension_divergence")
    )
    case_count = len({row["case_id"] for row in rows})
    new_judge_model = new_judge_models[0] if len(new_judge_models) == 1 else ", ".join(new_judge_models)
    original_judges_text = ", ".join(original_judges) if original_judges else "unknown"

    if material_divergence_count:
        headline = (
            f"Judge-sensitivity subset flagged {material_divergence_count} material divergence(s) "
            f"across {row_count} re-judged rows."
        )
        takeaway = (
            f"Sonnet re-judging found {material_divergence_count} material judge divergence(s) "
            f"across {case_count} curated cases ({row_count} rows)."
        )
    else:
        headline = (
            f"Judge-sensitivity subset found no >1-point dimension divergences; "
            f"{rows_with_any_delta}/{row_count} re-judged rows had only 1-point shifts."
        )
        takeaway = (
            f"Sonnet re-judging found no >1-point dimension divergences vs the Haiku judge; "
            f"{rows_with_any_delta}/{row_count} rows showed only 1-point shifts."
        )

    return {
        "path": path,
        "row_count": row_count,
        "case_count": case_count,
        "rows_with_any_delta": rows_with_any_delta,
        "material_divergence_count": material_divergence_count,
        "new_judge_model": new_judge_model,
        "original_judges_text": original_judges_text,
        "models": models,
        "headline": headline,
        "takeaway": takeaway,
    }


def _sort_value(value):
    return float("inf") if value is None else value


def validate_runs(runs):
    """Validate that supplied runs are comparable and enrich them with metadata."""
    reference_case_set = None
    judge_models = set()
    dataset_hashes = set()

    for label, payload in runs.items():
        manifest = payload.get("manifest") or {}
        row_metadata = payload.get("row_metadata") or {}
        results = payload["results"]

        run_metadata = {
            "model_name": _coalesce_metadata_value(manifest, row_metadata, "model_name"),
            "judge_model": _coalesce_metadata_value(manifest, row_metadata, "judge_model"),
            "dataset_item_count": _coalesce_metadata_value(
                manifest, row_metadata, "dataset_item_count"
            ) or len(results),
            "dataset_case_id_hash": _coalesce_metadata_value(
                manifest, row_metadata, "dataset_case_id_hash"
            ) or compute_case_id_hash_from_results(results),
            "case_ids": manifest.get("case_ids") or row_metadata.get("case_ids") or [
                result["case_id"] for result in results
            ],
            "metadata_source": describe_metadata_source(manifest, row_metadata),
        }

        result_case_set = set(result["case_id"] for result in results)
        metadata_case_set = set(run_metadata["case_ids"])
        if result_case_set != metadata_case_set:
            raise ValueError(
                f"Run {label} manifest metadata does not match results case IDs"
            )
        if run_metadata["dataset_item_count"] != len(result_case_set):
            raise ValueError(
                f"Run {label} dataset_item_count does not match results row count"
            )
        if run_metadata["dataset_case_id_hash"] != compute_case_id_hash_from_results(results):
            raise ValueError(
                f"Run {label} dataset_case_id_hash does not match results case IDs"
            )

        payload["run_metadata"] = run_metadata

        if reference_case_set is None:
            reference_case_set = result_case_set
        elif result_case_set != reference_case_set:
            raise ValueError("Run results do not contain the same case IDs")

        if run_metadata.get("judge_model"):
            judge_models.add(run_metadata["judge_model"])
        if run_metadata.get("dataset_case_id_hash"):
            dataset_hashes.add(run_metadata["dataset_case_id_hash"])

    if len(judge_models) > 1:
        raise ValueError(f"Runs use different judge models: {sorted(judge_models)}")
    if len(dataset_hashes) > 1:
        raise ValueError(f"Runs use different datasets: {sorted(dataset_hashes)}")

    reference_payload = next(iter(runs.values()))
    return {
        "dataset_item_count": len(reference_case_set or []),
        "dataset_case_id_hash": reference_payload["run_metadata"]["dataset_case_id_hash"],
        "judge_model": next(iter(judge_models), None),
    }


def best_labels(metrics_by_label, metric_key):
    """Return all labels tied for the minimum value of a metric."""
    values = {
        label: metrics.get(metric_key)
        for label, metrics in metrics_by_label.items()
    }
    best_value = min(_sort_value(value) for value in values.values())
    if best_value == float("inf"):
        return [label for label, value in values.items() if value is None]
    return [
        label
        for label, value in values.items()
        if values_equal(value, best_value)
    ]


def best_labels_desc(metrics_by_label, metric_key):
    """Return all labels tied for the maximum value of a metric."""
    values = {
        label: metrics.get(metric_key)
        for label, metrics in metrics_by_label.items()
    }
    present_values = [value for value in values.values() if value is not None]
    if not present_values:
        return [label for label, value in values.items() if value is None]
    best_value = max(present_values)
    return [
        label
        for label, value in values.items()
        if values_equal(value, best_value)
    ]


def format_label_group(labels):
    if not labels:
        return "None"
    if len(labels) == 1:
        return f"**{labels[0]}**"
    return "tie between " + " and ".join(f"**{label}**" for label in labels)


def values_equal(left, right):
    if left is None or right is None:
        return left is right
    return abs(left - right) < 1e-12


def describe_metadata_source(manifest, row_metadata):
    if manifest and any(row_metadata.get(field) is not None for field in ["model_name", "judge_model"]):
        return "manifest + rows"
    if manifest:
        return "manifest"
    if any(row_metadata.get(field) is not None for field in ["model_name", "judge_model"]):
        return "rows"
    return "results-only inference"


def _coalesce_metadata_value(manifest, row_metadata, key):
    manifest_value = manifest.get(key) if manifest else None
    row_value = row_metadata.get(key) if row_metadata else None
    if manifest_value is not None and row_value is not None and manifest_value != row_value:
        raise ValueError(
            f"Manifest and row metadata disagree for {key}: {manifest_value!r} != {row_value!r}"
        )
    return manifest_value if manifest_value is not None else row_value


def main(argv=None):
    parser = argparse.ArgumentParser(description="Build a cross-model comparison report")
    parser.add_argument(
        "--run",
        action="append",
        dest="runs",
        required=True,
        help="Run spec in the form label=path/to/eval_results.jsonl",
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Path to the markdown report to create",
    )
    parser.add_argument(
        "--title",
        default="Cross-Model Comparison",
        help="Markdown title for the report",
    )
    parser.add_argument(
        "--judge-sensitivity",
        default=None,
        help="Optional path to judge-sensitivity rejudged_scores.jsonl for summary inclusion",
    )
    args = parser.parse_args(argv)

    output_path = write_comparison_report(
        args.runs,
        args.output,
        title=args.title,
        judge_sensitivity_path=args.judge_sensitivity,
    )
    print(f"Comparison report written to: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
