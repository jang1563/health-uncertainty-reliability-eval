"""Report and figure generation for the Drug Safety Update Sensitivity Eval."""

import argparse
import json
import os
from collections import defaultdict
from pathlib import Path

DIMENSIONS = [
    "update_uptake",
    "stale_advice_avoidance",
    "safety_severity_calibration",
    "actionability_and_followup_guidance",
    "source_grounded_communication",
]

DEFAULT_REPORT_NAME = "drug_safety_update_eval_v1.md"
DEFAULT_FIGURES_DIRNAME = "figures"


def resolve_artifact_paths(output_dir=None, report_path=None, figures_dir=None):
    """Resolve report and figure locations without overwriting tracked artifacts."""
    output_root = Path(output_dir) if output_dir else Path(__file__).parent / "output"
    resolved_report_path = Path(report_path) if report_path else output_root / DEFAULT_REPORT_NAME
    resolved_figures_dir = Path(figures_dir) if figures_dir else output_root / DEFAULT_FIGURES_DIRNAME
    return str(resolved_report_path), str(resolved_figures_dir)


def generate_report(results, report_path, figures_dir, model_name="unknown"):
    """Generate markdown report and figures from evaluation results."""
    report_dir = os.path.dirname(report_path) or "."
    os.makedirs(report_dir, exist_ok=True)
    os.makedirs(figures_dir, exist_ok=True)

    # Compute metrics
    metrics = compute_metrics(results)

    # Write markdown report
    write_report(metrics, results, report_path, figures_dir, model_name)

    # Generate figures
    try:
        generate_figures(results, figures_dir)
    except ImportError:
        print("matplotlib not available — skipping figure generation")


def compute_metrics(results):
    """Compute aggregate reporting metrics."""
    m = {}

    scored_results = [r for r in results if _is_scored_result(r)]
    judge_errors = [r for r in results if not _is_scored_result(r)]
    m["scored_item_count"] = len(scored_results)
    m["judge_error_count"] = len(judge_errors)
    m["judge_error_rate"] = len(judge_errors) / len(results) if results else 0
    m["judge_error_cases"] = [
        {
            "case_id": r["case_id"],
            "judge_error": r["scores"].get("judge_error", "unknown judge error"),
        }
        for r in judge_errors
    ]

    all_uptake = _score_values(scored_results, "update_uptake")
    m["update_uptake_rate"] = sum(all_uptake) / (2 * len(all_uptake)) if all_uptake else None
    m["mean_total_score"] = _mean(_score_values(scored_results, "total"))
    for dimension in DIMENSIONS:
        m[f"mean_{dimension}"] = _mean(_score_values(scored_results, dimension))
    m["failed_uptake_count"] = sum(
        1 for r in scored_results if r["scores"].get("update_uptake") == 0
    )
    m["partial_uptake_count"] = sum(
        1 for r in scored_results if r["scores"].get("update_uptake") == 1
    )
    m["suboptimal_uptake_count"] = sum(
        1 for r in scored_results if r["scores"].get("update_uptake") in {0, 1}
    )

    # Stale reassurance rate
    ri_items = [r for r in scored_results if r["update_direction"] == "risk_increase"]
    ri_stale = [r for r in ri_items if r["scores"]["stale_advice_avoidance"] == 0]
    m["stale_reassurance_rate"] = len(ri_stale) / len(ri_items) if ri_items else None

    # Stale alarmism rate
    rd_items = [r for r in scored_results if r["update_direction"] == "risk_decrease"]
    rd_stale = [r for r in rd_items if r["scores"]["stale_advice_avoidance"] == 0]
    m["stale_alarmism_rate"] = len(rd_stale) / len(rd_items) if rd_items else None

    # Boxed warning sensitivity
    bw_items = [
        r for r in scored_results if r["section_changed"] == "boxed_warning_or_contraindication"
    ]
    bw_uptake = _score_values(bw_items, "update_uptake")
    m["boxed_warning_sensitivity"] = sum(bw_uptake) / (2 * len(bw_uptake)) if bw_uptake else None

    # False update sensitivity on controls
    ctrl_items = [r for r in scored_results if r["update_direction"] == "stable"]
    ctrl_false = [r for r in ctrl_items if r["scores"]["update_uptake"] < 2]
    m["false_update_sensitivity_on_controls"] = len(ctrl_false) / len(ctrl_items) if ctrl_items else None

    # Failure counts
    m["failure_count_by_section"] = defaultdict(int)
    m["failure_count_by_direction"] = defaultdict(int)
    for r in scored_results:
        if r["scores"]["update_uptake"] == 0:
            m["failure_count_by_section"][r["section_changed"]] += 1
            m["failure_count_by_direction"][r["update_direction"]] += 1

    return m


def write_report(metrics, results, report_path, figures_dir, model_name):
    """Write the markdown report."""
    total = len(results)
    update_figure_path = os.path.relpath(
        os.path.join(figures_dir, "update_uptake_summary.png"),
        start=os.path.dirname(report_path) or ".",
    )
    stale_figure_path = os.path.relpath(
        os.path.join(figures_dir, "stale_reassurance_breakdown.png"),
        start=os.path.dirname(report_path) or ".",
    )

    lines = [
        "# Drug Safety Update Sensitivity Eval — v1 Report\n",
        f"## Summary\n",
        f"- **Model tested**: {model_name}",
        f"- **Total items**: {total} (30 events x 3 variants)",
        f"- **Scored items**: {metrics['scored_item_count']}",
        f"- **Judge errors excluded from metrics**: {metrics['judge_error_count']} ({_format_ratio(metrics['judge_error_rate'])})",
        f"- **Overall update_uptake_rate**: {_format_ratio(metrics['update_uptake_rate'])}",
        f"- **Mean total score (/10)**: {_format_number(metrics['mean_total_score'], 2)}",
        f"- **Partial shifts (update_uptake = 1)**: {metrics['partial_uptake_count']}",
        f"- **Failed shifts (update_uptake = 0)**: {metrics['failed_uptake_count']}",
        f"- **Stale reassurance rate**: {_format_ratio(metrics['stale_reassurance_rate'])}",
        f"- **Stale alarmism rate**: {_format_ratio(metrics['stale_alarmism_rate'])}",
        f"- **Boxed warning sensitivity**: {_format_ratio(metrics['boxed_warning_sensitivity'])}",
        f"- **False update sensitivity (controls)**: {_format_ratio(metrics['false_update_sensitivity_on_controls'])}",
        "",
        "## Results by Section\n",
        "| Section | Items | Scored | Judge errors | Mean update_uptake | Mean total (/10) |",
        "|---|---:|---:|---:|---:|---:|",
    ]

    # Group by section
    by_section = defaultdict(list)
    for r in results:
        by_section[r["section_changed"]].append(r)

    for section in sorted(by_section):
        items_in_section = by_section[section]
        scored = [r for r in items_in_section if _is_scored_result(r)]
        judge_errors = len(items_in_section) - len(scored)
        mean_uptake = _mean(_score_values(scored, "update_uptake"))
        mean_total = _mean(_score_values(scored, "total"))
        lines.append(
            f"| {section} | {len(items_in_section)} | {len(scored)} | {judge_errors} | "
            f"{_format_number(mean_uptake, 2)} | {_format_number(mean_total, 1)} |"
        )

    lines += [
        "",
        "## Results by Direction\n",
        "| Direction | Items | Scored | Judge errors | Mean update_uptake | Mean stale_advice_avoidance |",
        "|---|---:|---:|---:|---:|---:|",
    ]

    by_direction = defaultdict(list)
    for r in results:
        by_direction[r["update_direction"]].append(r)

    for direction in sorted(by_direction):
        items_in_dir = by_direction[direction]
        scored = [r for r in items_in_dir if _is_scored_result(r)]
        judge_errors = len(items_in_dir) - len(scored)
        mean_uptake = _mean(_score_values(scored, "update_uptake"))
        mean_stale = _mean(_score_values(scored, "stale_advice_avoidance"))
        lines.append(
            f"| {direction} | {len(items_in_dir)} | {len(scored)} | {judge_errors} | "
            f"{_format_number(mean_uptake, 2)} | {_format_number(mean_stale, 2)} |"
        )

    lines += [
        "",
        "## Results by Prompt Variant\n",
        "| Variant | Items | Scored | Judge errors | Mean update_uptake | Mean total (/10) |",
        "|---|---:|---:|---:|---:|---:|",
    ]

    by_variant = defaultdict(list)
    for r in results:
        by_variant[r["prompt_variant"]].append(r)

    for variant in sorted(by_variant):
        items_in_var = by_variant[variant]
        scored = [r for r in items_in_var if _is_scored_result(r)]
        judge_errors = len(items_in_var) - len(scored)
        mean_uptake = _mean(_score_values(scored, "update_uptake"))
        mean_total = _mean(_score_values(scored, "total"))
        lines.append(
            f"| {variant} | {len(items_in_var)} | {len(scored)} | {judge_errors} | "
            f"{_format_number(mean_uptake, 2)} | {_format_number(mean_total, 1)} |"
        )

    lines += [
        "",
        "## Suboptimal Shift Analysis\n",
        "Items where update_uptake < 2:\n",
    ]

    suboptimal_shifts = [
        r for r in results
        if _is_scored_result(r) and r["scores"]["update_uptake"] in {0, 1}
    ]
    if suboptimal_shifts:
        partials = [r for r in suboptimal_shifts if r["scores"]["update_uptake"] == 1]
        failures = [r for r in suboptimal_shifts if r["scores"]["update_uptake"] == 0]
        lines.append(f"- Partial shifts (update_uptake = 1): {len(partials)}")
        lines.append(f"- Failed shifts (update_uptake = 0): {len(failures)}")
        lines.append("")
        for result in sorted(
            suboptimal_shifts,
            key=lambda row: (row["scores"]["update_uptake"], row["case_id"]),
        ):
            lines.append(
                f"- **{result['case_id']}** "
                f"(update_uptake={result['scores']['update_uptake']}; "
                f"{result['drug_name']}, {result['section_changed']}, {result['update_direction']})"
            )
            lines.append(f"  - Reasoning: {result['scores'].get('reasoning', 'N/A')}")
    else:
        lines.append("No items with update_uptake < 2.")

    lines += [
        "",
        "## Judge Errors\n",
    ]

    if metrics["judge_error_cases"]:
        for case in metrics["judge_error_cases"]:
            lines.append(f"- **{case['case_id']}**: {case['judge_error']}")
    else:
        lines.append("No judge parsing errors.")

    lines += [
        "",
        "## Figures\n",
        f"- ![Update Uptake Summary]({update_figure_path})",
        f"- ![Stale Reassurance Breakdown]({stale_figure_path})",
        "",
        "---",
        "*Generated by Drug Safety Update Sensitivity Eval v1*",
    ]

    with open(report_path, "w") as f:
        f.write("\n".join(lines))


def generate_figures(results, figures_dir):
    """Generate matplotlib figures."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    scored_results = [r for r in results if _is_scored_result(r)]
    if not scored_results:
        print("No scored results available — skipping figure generation")
        return

    # Figure 1: Update Uptake Summary (grouped bar by section and direction)
    sections = sorted(set(r["section_changed"] for r in scored_results))
    directions = ["risk_increase", "risk_decrease", "stable"]

    fig, ax = plt.subplots(figsize=(12, 6))
    x_positions = range(len(sections))
    width = 0.25

    for i, direction in enumerate(directions):
        means = []
        for section in sections:
            items = [
                r for r in scored_results
                if r["section_changed"] == section and r["update_direction"] == direction
            ]
            if items:
                means.append(sum(r["scores"]["update_uptake"] for r in items) / len(items))
            else:
                means.append(0)
        offset = (i - 1) * width
        ax.bar([x + offset for x in x_positions], means, width, label=direction)

    ax.set_xlabel("Section Changed")
    ax.set_ylabel("Mean update_uptake (0-2)")
    ax.set_title("Update Uptake by Section and Direction")
    ax.set_xticks(x_positions)
    ax.set_xticklabels([s.replace("_", "\n") for s in sections], fontsize=8)
    ax.legend()
    ax.set_ylim(0, 2.2)
    plt.tight_layout()
    plt.savefig(os.path.join(figures_dir, "update_uptake_summary.png"), dpi=150)
    plt.close()

    # Figure 2: Stale Reassurance Breakdown (stacked bar for risk_increase items)
    ri_items = [r for r in scored_results if r["update_direction"] == "risk_increase"]
    if not ri_items:
        print("No scored risk_increase items available — skipping stale reassurance figure")
        return
    ri_sections = sorted(set(r["section_changed"] for r in ri_items))

    fig, ax = plt.subplots(figsize=(10, 6))
    score_labels = ["0 (stale)", "1 (partial)", "2 (clean)"]
    colors = ["#d32f2f", "#ffa000", "#388e3c"]

    bottoms = [0] * len(ri_sections)
    for score_val in range(3):
        counts = []
        for section in ri_sections:
            items = [r for r in ri_items if r["section_changed"] == section]
            count = sum(1 for r in items if r["scores"]["stale_advice_avoidance"] == score_val)
            counts.append(count)
        ax.bar(range(len(ri_sections)), counts, bottom=bottoms, label=score_labels[score_val], color=colors[score_val])
        bottoms = [b + c for b, c in zip(bottoms, counts)]

    ax.set_xlabel("Section Changed")
    ax.set_ylabel("Count")
    ax.set_title("Stale Reassurance Breakdown (Risk Increase Items Only)")
    ax.set_xticks(range(len(ri_sections)))
    ax.set_xticklabels([s.replace("_", "\n") for s in ri_sections], fontsize=8)
    ax.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(figures_dir, "stale_reassurance_breakdown.png"), dpi=150)
    plt.close()


def load_results_from_jsonl(path):
    """Load evaluation results from a JSONL file."""
    results = []
    with open(path) as f:
        for line in f:
            if line.strip():
                results.append(json.loads(line))
    return results


def _is_scored_result(result):
    return not result.get("scores", {}).get("judge_error")


def _score_values(results, key):
    values = []
    for result in results:
        value = result["scores"].get(key)
        if isinstance(value, (int, float)):
            values.append(value)
    return values


def _mean(values):
    return sum(values) / len(values) if values else None


def _format_ratio(value):
    return f"{value:.1%}" if value is not None else "N/A"


def _format_number(value, precision):
    if value is None:
        return "N/A"
    return f"{value:.{precision}f}"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate report and figures from evaluation results")
    parser.add_argument("results_path", help="Path to eval_results.jsonl")
    parser.add_argument("--output-dir", default=None, help="Base output directory for report and figures")
    parser.add_argument("--report-path", default=None, help="Optional explicit markdown report path")
    parser.add_argument("--figures-dir", default=None, help="Optional explicit directory for generated figures")
    args = parser.parse_args()

    results = load_results_from_jsonl(args.results_path)
    output_dir = args.output_dir or str(Path(args.results_path).resolve().parent)
    report_path, figures_dir = resolve_artifact_paths(
        output_dir=output_dir,
        report_path=args.report_path,
        figures_dir=args.figures_dir,
    )
    generate_report(results, report_path, figures_dir)
    print(f"Report generated: {report_path}")
    print(f"Figures generated under: {figures_dir}")
