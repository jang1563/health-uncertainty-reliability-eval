import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from eval.comparison_report import (
    build_comparison_report,
    load_judge_sensitivity_summary,
    load_named_runs,
    parse_run_spec,
)


def make_result(
    case_id,
    drug_name,
    section,
    direction,
    update_uptake,
    stale_advice,
    total,
    model_name=None,
    judge_model=None,
    score_overrides=None,
):
    row = {
        "case_id": case_id,
        "drug_name": drug_name,
        "section_changed": section,
        "update_direction": direction,
        "severity_tier": "moderate",
        "prompt_variant": "patient_plain_language",
        "before_response": "before",
        "after_response": "after",
        "scores": {
            "update_uptake": update_uptake,
            "stale_advice_avoidance": stale_advice,
            "safety_severity_calibration": 2,
            "actionability_and_followup_guidance": 2,
            "source_grounded_communication": 2,
            "reasoning": "synthetic",
            "total": total,
            "judge_error": None,
        },
    }
    if score_overrides:
        row["scores"].update(score_overrides)
    if model_name is not None:
        row["model_name"] = model_name
    if judge_model is not None:
        row["judge_model"] = judge_model
    return row


class ComparisonReportTests(unittest.TestCase):
    def test_parse_run_spec_accepts_label_and_path(self):
        label, path = parse_run_spec("haiku=eval/output/haiku_v2/eval_results.jsonl")
        self.assertEqual(label, "haiku")
        self.assertEqual(path, Path("eval/output/haiku_v2/eval_results.jsonl"))

    def test_build_comparison_report_summarizes_failures_and_rankings(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            run_a_path = root / "haiku" / "eval_results.jsonl"
            run_b_path = root / "gpt4o_mini" / "eval_results.jsonl"
            run_a_path.parent.mkdir(parents=True)
            run_b_path.parent.mkdir(parents=True)

            run_a_results = [
                make_result(
                    "DSU-001-patient_plain_language",
                    "Drug A",
                    "boxed_warning_or_contraindication",
                    "risk_increase",
                    2,
                    2,
                    10,
                    model_name="haiku-model",
                    judge_model="shared-judge",
                ),
                make_result(
                    "DSU-002-patient_plain_language",
                    "Drug B",
                    "warnings_and_precautions",
                    "risk_increase",
                    0,
                    0,
                    6,
                    model_name="haiku-model",
                    judge_model="shared-judge",
                ),
                make_result(
                    "DSU-003-patient_plain_language",
                    "Drug C",
                    "adverse_reactions",
                    "risk_increase",
                    2,
                    2,
                    9,
                    model_name="haiku-model",
                    judge_model="shared-judge",
                    score_overrides={"source_grounded_communication": 1},
                ),
            ]
            run_b_results = [
                make_result(
                    "DSU-001-patient_plain_language",
                    "Drug A",
                    "boxed_warning_or_contraindication",
                    "risk_increase",
                    1,
                    1,
                    8,
                    model_name="gpt-model",
                    judge_model="shared-judge",
                ),
                make_result(
                    "DSU-002-patient_plain_language",
                    "Drug B",
                    "warnings_and_precautions",
                    "risk_increase",
                    0,
                    0,
                    6,
                    model_name="gpt-model",
                    judge_model="shared-judge",
                ),
                make_result(
                    "DSU-003-patient_plain_language",
                    "Drug C",
                    "adverse_reactions",
                    "risk_increase",
                    2,
                    2,
                    10,
                    model_name="gpt-model",
                    judge_model="shared-judge",
                ),
            ]

            run_a_path.write_text(
                "\n".join(json.dumps(row) for row in run_a_results) + "\n"
            )
            run_b_path.write_text(
                "\n".join(json.dumps(row) for row in run_b_results) + "\n"
            )

            runs = load_named_runs(
                [
                    f"haiku={run_a_path}",
                    f"gpt4o_mini={run_b_path}",
                ]
            )
            report = build_comparison_report(runs)

        self.assertIn("| Metric | haiku | gpt4o_mini |", report)
        self.assertIn("| Label | Target model | Judge | Metadata source | Results path | Total items |", report)
        self.assertIn("Overall update uptake", report)
        self.assertIn("Mean total (/10)", report)
        self.assertIn("## Key Takeaways", report)
        self.assertIn("Overall front-runner by mean total score", report)
        self.assertIn("haiku (3) = gpt4o_mini (3)", report)
        self.assertIn("haiku (66.7%) > gpt4o_mini (50.0%)", report)
        self.assertIn("Shared suboptimal cases across all models: `DSU-002-patient_plain_language`", report)
        self.assertIn("- **haiku**: None", report)
        self.assertIn("- **gpt4o_mini**: `DSU-001-patient_plain_language`", report)
        self.assertIn("| update_uptake | 1.33 | 1.00 |", report)
        self.assertIn("## Prompt Variant Comparison", report)
        self.assertIn("| patient_plain_language | 1.33 / 8.33 / 1 | 1.00 / 8.00 / 2 | 0.33 | 0.33 |", report)
        self.assertIn("| DSU-001-patient_plain_language | Drug A | boxed_warning_or_contraindication | risk_increase | 2.00/10.00 | 1.00/8.00 | update_uptake, stale_advice_avoidance, total |", report)
        self.assertIn("| DSU-003-patient_plain_language | Drug C | adverse_reactions | risk_increase | 2.00/9.00 | 2.00/10.00 | source_grounded_communication, total |", report)

    def test_build_comparison_report_includes_judge_sensitivity_summary(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            run_a_path = root / "haiku" / "eval_results.jsonl"
            run_b_path = root / "gpt4o_mini" / "eval_results.jsonl"
            judge_sensitivity_path = root / "judge_sensitivity.jsonl"
            run_a_path.parent.mkdir(parents=True)
            run_b_path.parent.mkdir(parents=True)

            run_a_path.write_text(
                json.dumps(
                    make_result(
                        "DSU-001-patient_plain_language",
                        "Drug A",
                        "boxed_warning_or_contraindication",
                        "risk_increase",
                        2,
                        2,
                        10,
                        model_name="haiku-model",
                        judge_model="shared-judge",
                    )
                )
                + "\n"
            )
            run_b_path.write_text(
                json.dumps(
                    make_result(
                        "DSU-001-patient_plain_language",
                        "Drug A",
                        "boxed_warning_or_contraindication",
                        "risk_increase",
                        1,
                        1,
                        8,
                        model_name="gpt-model",
                        judge_model="shared-judge",
                    )
                )
                + "\n"
            )
            judge_sensitivity_path.write_text(
                json.dumps(
                    {
                        "case_id": "DSU-001-patient_plain_language",
                        "run_label": "haiku",
                        "original_judge_model": "claude-haiku-4-5-20251001",
                        "new_judge_model": "claude-sonnet-4-6",
                        "dimension_deltas": {
                            "update_uptake": 1,
                            "stale_advice_avoidance": 0,
                            "safety_severity_calibration": 0,
                            "actionability_and_followup_guidance": 0,
                            "source_grounded_communication": 0,
                        },
                        "material_dimension_divergence": False,
                    }
                )
                + "\n"
            )

            runs = load_named_runs(
                [
                    f"haiku={run_a_path}",
                    f"gpt4o_mini={run_b_path}",
                ]
            )
            judge_sensitivity_summary = load_judge_sensitivity_summary(judge_sensitivity_path)
            report = build_comparison_report(
                runs,
                judge_sensitivity_summary=judge_sensitivity_summary,
            )

        self.assertIn("## Judge Sensitivity", report)
        self.assertIn("claude-sonnet-4-6", report)
        self.assertIn("Judge-sensitivity subset found no >1-point dimension divergences", report)
        self.assertIn("Sonnet re-judging found no >1-point dimension divergences", report)

    def test_script_wrapper_runs_from_repo_root(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            run_a_path = root / "haiku" / "eval_results.jsonl"
            run_b_path = root / "gpt4o_mini" / "eval_results.jsonl"
            output_path = root / "cross_model.md"
            run_a_path.parent.mkdir(parents=True)
            run_b_path.parent.mkdir(parents=True)

            run_a_path.write_text(
                json.dumps(
                    make_result(
                        "DSU-001-patient_plain_language",
                        "Drug A",
                        "boxed_warning_or_contraindication",
                        "risk_increase",
                        2,
                        2,
                        10,
                        model_name="haiku-model",
                        judge_model="shared-judge",
                    )
                )
                + "\n"
            )
            run_b_path.write_text(
                json.dumps(
                    make_result(
                        "DSU-001-patient_plain_language",
                        "Drug A",
                        "boxed_warning_or_contraindication",
                        "risk_increase",
                        1,
                        1,
                        8,
                        model_name="gpt-model",
                        judge_model="shared-judge",
                    )
                )
                + "\n"
            )

            completed = subprocess.run(
                [
                    "python3",
                    "scripts/build_comparison_report.py",
                    "--run",
                    f"haiku={run_a_path}",
                    "--run",
                    f"gpt4o_mini={run_b_path}",
                    "--output",
                    str(output_path),
                ],
                cwd=Path(__file__).resolve().parents[1],
                check=True,
                capture_output=True,
                text=True,
            )

            self.assertIn("Comparison report written to", completed.stdout)
            self.assertTrue(output_path.exists())

    def test_build_comparison_report_rejects_mismatched_case_sets(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            run_a_path = root / "haiku" / "eval_results.jsonl"
            run_b_path = root / "gpt4o_mini" / "eval_results.jsonl"
            run_a_path.parent.mkdir(parents=True)
            run_b_path.parent.mkdir(parents=True)

            run_a_path.write_text(
                json.dumps(
                    make_result(
                        "DSU-001-patient_plain_language",
                        "Drug A",
                        "boxed_warning_or_contraindication",
                        "risk_increase",
                        2,
                        2,
                        10,
                        model_name="haiku-model",
                        judge_model="shared-judge",
                    )
                )
                + "\n"
            )
            run_b_path.write_text(
                json.dumps(
                    make_result(
                        "DSU-002-patient_plain_language",
                        "Drug B",
                        "boxed_warning_or_contraindication",
                        "risk_increase",
                        2,
                        2,
                        10,
                        model_name="gpt-model",
                        judge_model="shared-judge",
                    )
                )
                + "\n"
            )

            runs = load_named_runs(
                [
                    f"haiku={run_a_path}",
                    f"gpt4o_mini={run_b_path}",
                ]
            )

            with self.assertRaisesRegex(ValueError, "same case IDs"):
                build_comparison_report(runs)

    def test_build_comparison_report_rejects_mismatched_judges(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            run_a_path = root / "haiku" / "eval_results.jsonl"
            run_b_path = root / "gpt4o_mini" / "eval_results.jsonl"
            run_a_path.parent.mkdir(parents=True)
            run_b_path.parent.mkdir(parents=True)

            run_a_path.write_text(
                json.dumps(
                    make_result(
                        "DSU-001-patient_plain_language",
                        "Drug A",
                        "boxed_warning_or_contraindication",
                        "risk_increase",
                        2,
                        2,
                        10,
                        model_name="haiku-model",
                        judge_model="judge-a",
                    )
                )
                + "\n"
            )
            run_b_path.write_text(
                json.dumps(
                    make_result(
                        "DSU-001-patient_plain_language",
                        "Drug A",
                        "boxed_warning_or_contraindication",
                        "risk_increase",
                        2,
                        2,
                        10,
                        model_name="gpt-model",
                        judge_model="judge-b",
                    )
                )
                + "\n"
            )

            runs = load_named_runs(
                [
                    f"haiku={run_a_path}",
                    f"gpt4o_mini={run_b_path}",
                ]
            )

            with self.assertRaisesRegex(ValueError, "different judge models"):
                build_comparison_report(runs)


if __name__ == "__main__":
    unittest.main()
