#!/usr/bin/env python3
"""
Mock evaluation run — generates synthetic scores to demonstrate
the full report/figure pipeline without API calls.

Usage:
    python eval/run_mock_eval.py
"""

import json
import hashlib
import os
import random
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from eval.report_generator import generate_report, resolve_artifact_paths

DIMENSIONS = [
    "update_uptake",
    "stale_advice_avoidance",
    "safety_severity_calibration",
    "actionability_and_followup_guidance",
    "source_grounded_communication",
]


def generate_mock_scores(item):
    """Generate realistic mock scores based on item properties."""
    seed = int(hashlib.sha256(item["case_id"].encode("utf-8")).hexdigest()[:8], 16)
    rng = random.Random(seed)

    direction = item["update_direction"]
    severity = item["severity_tier"]

    if direction == "stable":
        # Controls: model usually gets it right (no change), sometimes hallucinates
        uptake = rng.choices([0, 1, 2], weights=[0.1, 0.15, 0.75])[0]
        stale = 2  # no stale claims for controls
        severity_cal = rng.choices([1, 2], weights=[0.3, 0.7])[0]
        action = rng.choices([1, 2], weights=[0.4, 0.6])[0]
        grounded = rng.choices([1, 2], weights=[0.3, 0.7])[0]
    elif direction == "risk_increase":
        # Risk increase: good models mostly catch it, sometimes stale reassurance
        if severity in ("critical", "high"):
            uptake = rng.choices([0, 1, 2], weights=[0.05, 0.2, 0.75])[0]
            stale = rng.choices([0, 1, 2], weights=[0.1, 0.2, 0.7])[0]
        else:
            uptake = rng.choices([0, 1, 2], weights=[0.1, 0.3, 0.6])[0]
            stale = rng.choices([0, 1, 2], weights=[0.15, 0.25, 0.6])[0]
        severity_cal = rng.choices([0, 1, 2], weights=[0.1, 0.3, 0.6])[0]
        action = rng.choices([0, 1, 2], weights=[0.1, 0.35, 0.55])[0]
        grounded = rng.choices([0, 1, 2], weights=[0.05, 0.25, 0.7])[0]
    else:  # risk_decrease
        # Risk decrease: models often exhibit stale alarmism
        uptake = rng.choices([0, 1, 2], weights=[0.15, 0.35, 0.5])[0]
        stale = rng.choices([0, 1, 2], weights=[0.25, 0.35, 0.4])[0]
        severity_cal = rng.choices([0, 1, 2], weights=[0.15, 0.35, 0.5])[0]
        action = rng.choices([0, 1, 2], weights=[0.15, 0.35, 0.5])[0]
        grounded = rng.choices([0, 1, 2], weights=[0.1, 0.3, 0.6])[0]

    scores = {
        "update_uptake": uptake,
        "stale_advice_avoidance": stale,
        "safety_severity_calibration": severity_cal,
        "actionability_and_followup_guidance": action,
        "source_grounded_communication": grounded,
        "reasoning": "Mock score for demonstration purposes.",
    }
    scores["total"] = sum(scores[d] for d in DIMENSIONS)
    return scores


def main(argv=None):
    import argparse

    parser = argparse.ArgumentParser(description="Generate synthetic evaluation outputs without API calls")
    parser.add_argument("--output", default=str(PROJECT_ROOT / "eval" / "output"), help="Output directory")
    parser.add_argument("--report-path", default=None, help="Optional explicit markdown report path")
    parser.add_argument("--figures-dir", default=None, help="Optional explicit directory for generated figures")
    args = parser.parse_args(argv)

    data_path = PROJECT_ROOT / "data" / "benchmark_items.jsonl"
    items = []
    with open(data_path) as f:
        for line in f:
            obj = json.loads(line.strip())
            if "_meta" in obj:
                continue
            items.append(obj)

    print(f"Loaded {len(items)} benchmark items")

    results = []
    for item in items:
        scores = generate_mock_scores(item)
        result = {
            "case_id": item["case_id"],
            "drug_name": item["drug_name"],
            "section_changed": item["section_changed"],
            "update_direction": item["update_direction"],
            "severity_tier": item["severity_tier"],
            "prompt_variant": item["prompt_variant"],
            "before_response": "[mock before response]",
            "after_response": "[mock after response]",
            "scores": scores,
        }
        results.append(result)

    # Save mock results
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    results_path = output_dir / "eval_results_mock.jsonl"
    with open(results_path, "w") as f:
        for r in results:
            f.write(json.dumps(r) + "\n")
    print(f"Mock results saved to: {results_path}")

    # Generate report and figures
    report_path, figures_dir = resolve_artifact_paths(
        output_dir=args.output,
        report_path=args.report_path,
        figures_dir=args.figures_dir,
    )
    generate_report(results, report_path, figures_dir, model_name="mock-model (synthetic scores)")
    print(f"Report saved to: {report_path}")
    print(f"Figures saved to: {figures_dir}/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
