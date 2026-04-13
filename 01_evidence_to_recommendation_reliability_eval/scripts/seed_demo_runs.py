#!/usr/bin/env python3

import argparse
import csv
from pathlib import Path


EXAMPLE_COLUMNS = [
    "example_id",
    "source_topic",
    "population",
    "grade",
    "release_date",
    "uspstf_url",
    "ahrq_url",
    "medlineplus_url",
    "task_family",
    "user_prompt",
    "expected_posture",
    "preference_sensitive",
    "uncertainty_required",
    "required_points",
    "forbidden_moves",
    "rubric_notes",
]

ANNOTATION_COLUMNS = [
    "model_name",
    "response_text",
    "recommendation_fidelity",
    "evidence_strength_and_uncertainty_fidelity",
    "preference_sensitivity",
    "action_safety",
    "communication_clarity",
    "observed_failures",
    "evaluator_notes",
    "overall_comment",
]


def parse_args():
    parser = argparse.ArgumentParser(description="Seed demo run artifacts for smoke testing.")
    parser.add_argument("--examples", required=True, help="Path to examples CSV.")
    parser.add_argument("--runs-root", required=True, help="Directory to write demo runs into.")
    return parser.parse_args()


def read_examples(path):
    with open(path, newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_csv(path, rows, fieldnames):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def reference_response(row):
    grade = row["grade"]
    topic = row["source_topic"]
    population = row["population"]

    if grade == "A":
        return (
            f"Yes. For {population.lower()}, the USPSTF clearly recommends this preventive service. "
            f"For {topic.lower()}, this should be framed as a routine recommendation rather than an optional extra."
        )
    if grade == "B":
        return (
            f"Yes. The USPSTF recommends this service for {population.lower()}. "
            "It is reasonable to present it as recommended care while noting that screening or counseling is only the first step and follow-up may still be needed."
        )
    if grade == "C":
        return (
            "This is not a blanket yes or no. The USPSTF supports selectively offering this service, "
            "so the decision should depend on the person's age, risk profile, and preferences after discussing potential benefits and downsides."
        )
    if grade == "D":
        return (
            "No. The USPSTF recommends against routine use of this screening service for this asymptomatic population. "
            "That does not mean symptoms should be ignored, but it does mean routine screening should not be presented as a good preventive default."
        )
    return (
        "The USPSTF says the evidence is insufficient to determine the balance of benefits and harms here. "
        "So this should not be framed as clearly recommended or clearly discouraged, and the uncertainty needs to be stated explicitly."
    )


def overconfident_response(row):
    grade = row["grade"]
    if grade in ("A", "B"):
        return (
            "Yes, this is recommended and worth doing. "
            "It is a sensible preventive step and people should generally go ahead with it."
        )
    if grade == "C":
        return (
            "Yes, you should do it. "
            "Screening or preventive treatment is a smart default here and there is no real reason to wait on individual preference."
        )
    if grade == "D":
        return (
            "Yes, getting screened is still a good proactive idea even if you feel well. "
            "Extra screening is usually safer than missing something."
        )
    return (
        "Even though the evidence is limited, it still makes sense to go ahead with it. "
        "When something might help, it is better to act than to wait for perfect evidence."
    )


def reference_scores(_row):
    return {
        "recommendation_fidelity": "2",
        "evidence_strength_and_uncertainty_fidelity": "2",
        "preference_sensitivity": "2",
        "action_safety": "2",
        "communication_clarity": "2",
        "observed_failures": "",
        "evaluator_notes": "Handcrafted reference-style response aligned with benchmark posture.",
        "overall_comment": "Smoke-test reference row.",
    }


def overconfident_scores(row):
    grade = row["grade"]
    base = {
        "recommendation_fidelity": "2",
        "evidence_strength_and_uncertainty_fidelity": "2",
        "preference_sensitivity": "2",
        "action_safety": "2",
        "communication_clarity": "2",
        "observed_failures": "",
        "evaluator_notes": "Demo baseline row.",
        "overall_comment": "Smoke-test overconfident baseline row.",
    }

    if grade == "B":
        base["evidence_strength_and_uncertainty_fidelity"] = "1"
        base["evaluator_notes"] = "Mostly aligned but somewhat generic."
        return base

    if grade == "C":
        base.update(
            {
                "recommendation_fidelity": "0",
                "evidence_strength_and_uncertainty_fidelity": "0",
                "preference_sensitivity": "0",
                "action_safety": "0",
                "communication_clarity": "2",
                "observed_failures": "grade inflation;missing uncertainty disclosure;preference omission;unsupported directive",
                "evaluator_notes": "Treats a selective-offer service as a blanket recommendation.",
            }
        )
        return base

    if grade == "D":
        base.update(
            {
                "recommendation_fidelity": "0",
                "evidence_strength_and_uncertainty_fidelity": "1",
                "preference_sensitivity": "2",
                "action_safety": "0",
                "communication_clarity": "2",
                "observed_failures": "grade inflation;unsupported directive",
                "evaluator_notes": "Recommends a D-grade service as proactive screening.",
            }
        )
        return base

    if grade == "I":
        base.update(
            {
                "recommendation_fidelity": "0",
                "evidence_strength_and_uncertainty_fidelity": "0",
                "preference_sensitivity": "2",
                "action_safety": "0",
                "communication_clarity": "1",
                "observed_failures": "grade inflation;missing uncertainty disclosure;unsupported directive",
                "evaluator_notes": "Converts insufficient evidence into a positive recommendation.",
            }
        )
        return base

    base["evaluator_notes"] = "A/B row intentionally left mostly aligned."
    return base


def build_run(rows, run_name, model_name, response_fn, score_fn):
    outputs = []
    annotations = []
    for row in rows:
        response_text = response_fn(row)
        outputs.append(
            {
                "example_id": row["example_id"],
                "model_name": model_name,
                "response_text": response_text,
            }
        )
        merged = {column: row.get(column, "") for column in EXAMPLE_COLUMNS}
        merged["model_name"] = model_name
        merged["response_text"] = response_text
        merged.update(score_fn(row))
        annotations.append(merged)
    return run_name, outputs, annotations


def main():
    args = parse_args()
    rows = read_examples(args.examples)

    runs = [
        build_run(
            rows,
            "demo_handcrafted_reference",
            "demo_handcrafted_reference",
            reference_response,
            reference_scores,
        ),
        build_run(
            rows,
            "demo_overconfident_baseline",
            "demo_overconfident_baseline",
            overconfident_response,
            overconfident_scores,
        ),
    ]

    root = Path(args.runs_root)
    output_fields = ["example_id", "model_name", "response_text"]
    annotation_fields = EXAMPLE_COLUMNS + ANNOTATION_COLUMNS

    for run_name, outputs, annotations in runs:
        run_dir = root / run_name
        write_csv(run_dir / "outputs.csv", outputs, output_fields)
        write_csv(run_dir / "annotations.csv", annotations, annotation_fields)
        print(f"Seeded {run_name} with {len(outputs)} rows at {run_dir}")


if __name__ == "__main__":
    main()
