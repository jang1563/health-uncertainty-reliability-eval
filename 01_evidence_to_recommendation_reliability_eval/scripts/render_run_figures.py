#!/usr/bin/env python3

import argparse
import json
from pathlib import Path


PALETTE = [
    "#0f766e",
    "#1d4ed8",
    "#b45309",
    "#b91c1c",
    "#7c3aed",
    "#475569",
]


def parse_args():
    parser = argparse.ArgumentParser(description="Render SVG comparison figures for selected runs.")
    parser.add_argument("--runs-root", required=True, help="Root directory containing run subdirectories.")
    parser.add_argument("--figures-dir", required=True, help="Directory to write SVG figures.")
    parser.add_argument(
        "--run-name",
        action="append",
        required=True,
        help="Run directory name to include. Pass multiple times to compare multiple runs.",
    )
    parser.add_argument(
        "--output-prefix",
        required=True,
        help="Prefix for output figure filenames, e.g. real_run or demo_selected.",
    )
    parser.add_argument(
        "--title-prefix",
        default="Run",
        help="Display prefix for figure titles, e.g. Real Run or Demo Run.",
    )
    parser.add_argument(
        "--subtitle",
        default="Higher is better for overall and grade fidelity. Lower is better for omission and overrecommendation metrics.",
        help="Subtitle shown under the figure title.",
    )
    return parser.parse_args()


def load_json(path):
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def load_runs(runs_root, run_names):
    runs = []
    root = Path(runs_root)
    for run_name in run_names:
        run_dir = root / run_name
        summary_path = run_dir / "summary.json"
        if not summary_path.exists():
            raise SystemExit(f"Missing summary.json for run: {run_name}")
        manifest_path = run_dir / "manifest.json"
        summary = load_json(summary_path)
        manifest = load_json(manifest_path) if manifest_path.exists() else {}
        label = manifest.get("model_name") or run_name
        runs.append(
            {
                "run_name": run_name,
                "label": label,
                "summary": summary,
            }
        )
    if not runs:
        raise SystemExit("No runs selected.")
    return runs


def svg_header(width, height):
    return [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        "<style>",
        ".bg { fill: #fffaf3; }",
        ".panel { fill: #fffdf8; stroke: #eadfce; stroke-width: 1; }",
        ".title { font: 700 22px Georgia, serif; fill: #1f2937; }",
        ".label { font: 12px Helvetica, Arial, sans-serif; fill: #374151; }",
        ".small { font: 11px Helvetica, Arial, sans-serif; fill: #6b7280; }",
        ".axis { stroke: #9ca3af; stroke-width: 1; }",
        ".grid { stroke: #ece7df; stroke-width: 1; }",
        "</style>",
    ]


def svg_footer():
    return ["</svg>"]


def build_colors(runs):
    colors = {}
    for idx, run in enumerate(runs):
        colors[run["run_name"]] = PALETTE[idx % len(PALETTE)]
    return colors


def metric_specs():
    return [
        ("overall_rubric_score", "overall", 2.0, "up"),
        ("grade_fidelity_accuracy", "grade fidelity", 1.0, "up"),
        ("C_grade_preference_omission_rate", "C omission", 1.0, "down"),
        ("I_statement_overrecommendation_rate", "I overrec", 1.0, "down"),
        ("unsupported_directive_rate", "unsupported", 1.0, "down"),
    ]


def render_metric_comparison(runs, output_path, title_prefix, subtitle):
    specs = metric_specs()
    colors = build_colors(runs)

    width = 980
    height = 440
    left = 80
    right = 40
    top = 86
    bottom = 88
    chart_h = height - top - bottom
    chart_w = width - left - right
    group_w = chart_w / len(specs)
    bar_w = min(34, (group_w - 32) / max(len(runs), 1))
    gap = 10

    parts = svg_header(width, height)
    parts.append('<rect width="100%" height="100%" class="bg"/>')
    parts.append('<rect x="20" y="18" width="940" height="404" rx="18" class="panel"/>')
    parts.append(f'<text x="44" y="48" class="title">{title_prefix} Metric Comparison</text>')
    parts.append(f'<text x="44" y="68" class="small">{subtitle}</text>')

    parts.append(f'<line x1="{left}" y1="{top}" x2="{left}" y2="{height-bottom}" class="axis"/>')
    parts.append(f'<line x1="{left}" y1="{height-bottom}" x2="{width-right}" y2="{height-bottom}" class="axis"/>')

    for i, (metric_key, metric_label, metric_max, direction) in enumerate(specs):
        group_center = left + group_w * i + group_w / 2
        total_group_width = len(runs) * bar_w + max(len(runs) - 1, 0) * gap
        start_x = group_center - total_group_width / 2
        marker = "higher better" if direction == "up" else "lower better"
        parts.append(
            f'<text x="{group_center}" y="{top-12}" text-anchor="middle" class="small">max {metric_max:.1f} | {marker}</text>'
        )
        parts.append(
            f'<text x="{group_center}" y="{height-bottom+24}" text-anchor="middle" class="label">{metric_label}</text>'
        )
        parts.append(
            f'<line x1="{left + group_w * i + 10}" y1="{top}" x2="{left + group_w * (i + 1) - 10}" y2="{top}" class="grid"/>'
        )

        for j, run in enumerate(runs):
            raw_value = run["summary"].get(metric_key)
            value = 0.0 if raw_value is None else float(raw_value)
            normalized = value / metric_max if metric_max else 0
            bar_h = normalized * chart_h
            x = start_x + j * (bar_w + gap)
            y = top + chart_h - bar_h
            color = colors[run["run_name"]]
            parts.append(f'<rect x="{x}" y="{y}" width="{bar_w}" height="{bar_h}" fill="{color}" rx="4"/>')
            parts.append(f'<text x="{x + bar_w/2}" y="{y-7}" text-anchor="middle" class="small">{value:.2f}</text>')

    legend_y = height - 30
    legend_x = left
    legend_step = 230
    for idx, run in enumerate(runs):
        x = legend_x + idx * legend_step
        color = colors[run["run_name"]]
        legend_label = f"{run['label']} ({run['run_name']})"
        parts.append(f'<rect x="{x}" y="{legend_y-10}" width="14" height="14" fill="{color}" rx="2"/>')
        parts.append(f'<text x="{x+22}" y="{legend_y+2}" class="label">{legend_label}</text>')

    parts.extend(svg_footer())
    output_path.write_text("\n".join(parts) + "\n", encoding="utf-8")


def render_failure_comparison(runs, output_path, title_prefix):
    colors = build_colors(runs)
    failures = sorted(
        {
            failure
            for run in runs
            for failure in run["summary"].get("failure_count_overall", {}).keys()
        }
    )
    if not failures:
        failures = ["none"]

    width = 980
    height = 440
    left = 80
    right = 40
    top = 86
    bottom = 100
    chart_h = height - top - bottom
    chart_w = width - left - right
    max_value = 1
    for run in runs:
        for failure in failures:
            max_value = max(max_value, int(run["summary"].get("failure_count_overall", {}).get(failure, 0)))
    group_w = chart_w / len(failures)
    bar_w = min(34, (group_w - 32) / max(len(runs), 1))
    gap = 10

    parts = svg_header(width, height)
    parts.append('<rect width="100%" height="100%" class="bg"/>')
    parts.append('<rect x="20" y="18" width="940" height="404" rx="18" class="panel"/>')
    parts.append(f'<text x="44" y="48" class="title">{title_prefix} Failure Count Comparison</text>')
    parts.append('<text x="44" y="68" class="small">Failure counts are raw row-level totals from each run summary.</text>')

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
        total_group_width = len(runs) * bar_w + max(len(runs) - 1, 0) * gap
        start_x = group_center - total_group_width / 2

        parts.append(
            f'<text x="{group_center}" y="{height-bottom+24}" text-anchor="middle" class="label">{failure}</text>'
        )
        for j, run in enumerate(runs):
            value = int(run["summary"].get("failure_count_overall", {}).get(failure, 0))
            bar_h = (value / max_value * chart_h) if max_value else 0
            x = start_x + j * (bar_w + gap)
            y = top + chart_h - bar_h
            color = colors[run["run_name"]]
            parts.append(f'<rect x="{x}" y="{y}" width="{bar_w}" height="{bar_h}" fill="{color}" rx="4"/>')
            parts.append(f'<text x="{x + bar_w/2}" y="{y-7}" text-anchor="middle" class="small">{value}</text>')

    legend_y = height - 36
    legend_x = left
    legend_step = 230
    for idx, run in enumerate(runs):
        x = legend_x + idx * legend_step
        color = colors[run["run_name"]]
        legend_label = f"{run['label']} ({run['run_name']})"
        parts.append(f'<rect x="{x}" y="{legend_y-10}" width="14" height="14" fill="{color}" rx="2"/>')
        parts.append(f'<text x="{x+22}" y="{legend_y+2}" class="label">{legend_label}</text>')

    parts.extend(svg_footer())
    output_path.write_text("\n".join(parts) + "\n", encoding="utf-8")


def main():
    args = parse_args()
    runs = load_runs(args.runs_root, args.run_name)
    figures_dir = Path(args.figures_dir)
    figures_dir.mkdir(parents=True, exist_ok=True)

    metric_path = figures_dir / f"{args.output_prefix}_metric_comparison.svg"
    failure_path = figures_dir / f"{args.output_prefix}_failure_count_comparison.svg"

    render_metric_comparison(runs, metric_path, args.title_prefix, args.subtitle)
    render_failure_comparison(runs, failure_path, args.title_prefix)

    print(f"Wrote {metric_path}")
    print(f"Wrote {failure_path}")


if __name__ == "__main__":
    main()
