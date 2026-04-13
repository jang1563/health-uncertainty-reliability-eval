#!/usr/bin/env python3

import argparse
import json
from pathlib import Path


def parse_args():
    parser = argparse.ArgumentParser(description="Render demo SVG figures from run summaries.")
    parser.add_argument("--runs-root", required=True, help="Root directory containing run subdirectories.")
    parser.add_argument("--figures-dir", required=True, help="Directory to write SVG figures.")
    return parser.parse_args()


def load_summary(path):
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def discover_runs(runs_root):
    summaries = {}
    for child in sorted(Path(runs_root).iterdir()):
        if not child.is_dir():
            continue
        summary_path = child / "summary.json"
        if summary_path.exists():
            summaries[child.name] = load_summary(summary_path)
    if not summaries:
        raise SystemExit("No run summaries found.")
    return summaries


def svg_header(width, height):
    return [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<style>',
        '.title { font: 700 20px sans-serif; fill: #1f2937; }',
        '.label { font: 12px sans-serif; fill: #374151; }',
        '.small { font: 11px sans-serif; fill: #6b7280; }',
        '.axis { stroke: #9ca3af; stroke-width: 1; }',
        '.grid { stroke: #e5e7eb; stroke-width: 1; }',
        '</style>',
    ]


def svg_footer():
    return ['</svg>']


def render_metric_comparison(summaries, output_path):
    metrics = [
        ("overall_rubric_score", "overall", 2.0),
        ("grade_fidelity_accuracy", "grade fidelity", 1.0),
        ("C_grade_preference_omission_rate", "C omission", 1.0),
        ("I_statement_overrecommendation_rate", "I overrec", 1.0),
        ("unsupported_directive_rate", "unsupported", 1.0),
    ]
    run_names = list(summaries.keys())
    colors = {
        "demo_handcrafted_reference": "#0f766e",
        "demo_overconfident_baseline": "#b91c1c",
    }

    width = 920
    height = 420
    left = 80
    right = 40
    top = 70
    bottom = 80
    chart_h = height - top - bottom
    chart_w = width - left - right
    group_w = chart_w / len(metrics)
    bar_w = 26
    gap = 10

    parts = svg_header(width, height)
    parts.append('<rect width="100%" height="100%" fill="#ffffff"/>')
    parts.append('<text x="40" y="38" class="title">Demo Run Metric Comparison</text>')
    parts.append('<text x="40" y="58" class="small">Smoke-test only. Each metric group is scaled to its own maximum. Labels above bars show raw values.</text>')

    parts.append(f'<line x1="{left}" y1="{top}" x2="{left}" y2="{height-bottom}" class="axis"/>')
    parts.append(f'<line x1="{left}" y1="{height-bottom}" x2="{width-right}" y2="{height-bottom}" class="axis"/>')

    for i, (metric_key, metric_label, metric_max) in enumerate(metrics):
        group_center = left + group_w * i + group_w / 2
        start_x = group_center - ((len(run_names) * bar_w + (len(run_names) - 1) * gap) / 2)
        parts.append(f'<line x1="{left + group_w * i + 8}" y1="{top}" x2="{left + group_w * (i + 1) - 8}" y2="{top}" class="grid"/>')
        parts.append(
            f'<text x="{group_center}" y="{top-8}" text-anchor="middle" class="small">max {metric_max:.1f}</text>'
        )

        parts.append(
            f'<text x="{group_center}" y="{height-bottom+24}" text-anchor="middle" class="label">{metric_label}</text>'
        )

        for j, run_name in enumerate(run_names):
            raw_value = summaries[run_name].get(metric_key)
            value = 0 if raw_value is None else float(raw_value)
            normalized = value / metric_max if metric_max else 0
            bar_h = normalized * chart_h
            x = start_x + j * (bar_w + gap)
            y = top + chart_h - bar_h
            color = colors.get(run_name, "#2563eb")
            parts.append(f'<rect x="{x}" y="{y}" width="{bar_w}" height="{bar_h}" fill="{color}" rx="3"/>')
            parts.append(f'<text x="{x + bar_w/2}" y="{y-6}" text-anchor="middle" class="small">{value:.2f}</text>')

    legend_y = height - 28
    legend_x = left
    for idx, run_name in enumerate(run_names):
        x = legend_x + idx * 240
        color = colors.get(run_name, "#2563eb")
        parts.append(f'<rect x="{x}" y="{legend_y-10}" width="14" height="14" fill="{color}" rx="2"/>')
        parts.append(f'<text x="{x+22}" y="{legend_y+2}" class="label">{run_name}</text>')

    parts.extend(svg_footer())
    output_path.write_text("\n".join(parts) + "\n", encoding="utf-8")


def render_failure_comparison(summaries, output_path):
    failures = sorted(
        {
            failure
            for summary in summaries.values()
            for failure in summary.get("failure_count_overall", {}).keys()
        }
    )
    if not failures:
        failures = ["none"]
    run_names = list(summaries.keys())
    colors = {
        "demo_handcrafted_reference": "#0f766e",
        "demo_overconfident_baseline": "#b91c1c",
    }

    width = 920
    height = 420
    left = 80
    right = 40
    top = 70
    bottom = 100
    chart_h = height - top - bottom
    chart_w = width - left - right
    max_value = 1
    for summary in summaries.values():
        for failure in failures:
            max_value = max(max_value, int(summary.get("failure_count_overall", {}).get(failure, 0)))
    group_w = chart_w / len(failures)
    bar_w = 26
    gap = 10

    parts = svg_header(width, height)
    parts.append('<rect width="100%" height="100%" fill="#ffffff"/>')
    parts.append('<text x="40" y="38" class="title">Demo Failure Count Comparison</text>')
    parts.append('<text x="40" y="58" class="small">Smoke-test failure counts by run. Reference run should remain near zero.</text>')

    tick_count = max_value if max_value <= 6 else 6
    for tick in range(tick_count + 1):
        value = (max_value / tick_count) * tick if tick_count else 0
        y = top + chart_h - (value / max_value * chart_h if max_value else 0)
        parts.append(f'<line x1="{left}" y1="{y}" x2="{width-right}" y2="{y}" class="grid"/>')
        parts.append(f'<text x="{left-10}" y="{y+4}" text-anchor="end" class="small">{int(round(value))}</text>')

    parts.append(f'<line x1="{left}" y1="{top}" x2="{left}" y2="{height-bottom}" class="axis"/>')
    parts.append(f'<line x1="{left}" y1="{height-bottom}" x2="{width-right}" y2="{height-bottom}" class="axis"/>')

    for i, failure in enumerate(failures):
        group_center = left + group_w * i + group_w / 2
        start_x = group_center - ((len(run_names) * bar_w + (len(run_names) - 1) * gap) / 2)

        parts.append(
            f'<text x="{group_center}" y="{height-bottom+24}" text-anchor="middle" class="label">{failure}</text>'
        )
        for j, run_name in enumerate(run_names):
            value = int(summaries[run_name].get("failure_count_overall", {}).get(failure, 0))
            bar_h = (value / max_value * chart_h) if max_value else 0
            x = start_x + j * (bar_w + gap)
            y = top + chart_h - bar_h
            color = colors.get(run_name, "#2563eb")
            parts.append(f'<rect x="{x}" y="{y}" width="{bar_w}" height="{bar_h}" fill="{color}" rx="3"/>')
            parts.append(f'<text x="{x + bar_w/2}" y="{y-6}" text-anchor="middle" class="small">{value}</text>')

    legend_y = height - 36
    legend_x = left
    for idx, run_name in enumerate(run_names):
        x = legend_x + idx * 240
        color = colors.get(run_name, "#2563eb")
        parts.append(f'<rect x="{x}" y="{legend_y-10}" width="14" height="14" fill="{color}" rx="2"/>')
        parts.append(f'<text x="{x+22}" y="{legend_y+2}" class="label">{run_name}</text>')

    parts.extend(svg_footer())
    output_path.write_text("\n".join(parts) + "\n", encoding="utf-8")


def main():
    args = parse_args()
    summaries = discover_runs(args.runs_root)
    figures_dir = Path(args.figures_dir)
    figures_dir.mkdir(parents=True, exist_ok=True)

    render_metric_comparison(summaries, figures_dir / "demo_run_metric_comparison.svg")
    render_failure_comparison(summaries, figures_dir / "demo_failure_count_comparison.svg")

    print(f"Wrote {figures_dir / 'demo_run_metric_comparison.svg'}")
    print(f"Wrote {figures_dir / 'demo_failure_count_comparison.svg'}")


if __name__ == "__main__":
    main()
