import unittest

from eval.judge_sensitivity import (
    DEFAULT_SUBSET_CASE_IDS,
    build_judge_sensitivity_report,
    parse_run_spec,
)


def make_row(run_label, case_id, drug_name="Drug A", original_total=10, rejudged_total=10, deltas=None):
    deltas = deltas or {
        "update_uptake": 0,
        "stale_advice_avoidance": 0,
        "safety_severity_calibration": 0,
        "actionability_and_followup_guidance": 0,
        "source_grounded_communication": 0,
    }
    original_scores = {
        "update_uptake": 2,
        "stale_advice_avoidance": 2,
        "safety_severity_calibration": 2,
        "actionability_and_followup_guidance": 2,
        "source_grounded_communication": 2,
        "total": original_total,
    }
    rejudged_scores = {
        "update_uptake": original_scores["update_uptake"] + deltas["update_uptake"],
        "stale_advice_avoidance": original_scores["stale_advice_avoidance"] + deltas["stale_advice_avoidance"],
        "safety_severity_calibration": original_scores["safety_severity_calibration"] + deltas["safety_severity_calibration"],
        "actionability_and_followup_guidance": original_scores["actionability_and_followup_guidance"] + deltas["actionability_and_followup_guidance"],
        "source_grounded_communication": original_scores["source_grounded_communication"] + deltas["source_grounded_communication"],
        "total": rejudged_total,
    }
    return {
        "case_id": case_id,
        "run_label": run_label,
        "model_name": run_label,
        "drug_name": drug_name,
        "section_changed": "drug_interactions",
        "update_direction": "risk_increase",
        "severity_tier": "high",
        "prompt_variant": "patient_plain_language",
        "original_judge_model": "claude-haiku-4-5-20251001",
        "new_judge_model": "claude-sonnet-4-6",
        "original_scores": original_scores,
        "rejudged_scores": rejudged_scores,
        "dimension_deltas": deltas,
        "total_delta": rejudged_total - original_total,
        "material_dimension_divergence": any(abs(delta) > 1 for delta in deltas.values()),
    }


class JudgeSensitivityTests(unittest.TestCase):
    def test_parse_run_spec_accepts_label_and_path(self):
        parsed = parse_run_spec("demo=eval/output/demo/eval_results.jsonl")
        self.assertEqual(
            parsed,
            {"label": "demo", "path": "eval/output/demo/eval_results.jsonl"},
        )

    def test_default_subset_has_10_unique_case_ids(self):
        self.assertEqual(len(DEFAULT_SUBSET_CASE_IDS), 10)
        self.assertEqual(len(DEFAULT_SUBSET_CASE_IDS), len(set(DEFAULT_SUBSET_CASE_IDS)))

    def test_report_surfaces_material_divergence(self):
        rows = [
            make_row("model-a", "DSU-001", deltas={
                "update_uptake": -2,
                "stale_advice_avoidance": 0,
                "safety_severity_calibration": 0,
                "actionability_and_followup_guidance": 0,
                "source_grounded_communication": 0,
            }, original_total=10, rejudged_total=8),
            make_row("model-b", "DSU-001"),
        ]
        report = build_judge_sensitivity_report(rows, ["DSU-001"], "claude-sonnet-4-6")
        self.assertIn("Material divergence (>1 point on any dimension)**: yes", report)
        self.assertIn("model-a / DSU-001", report)
        self.assertIn("update_uptake -2", report)

    def test_report_notes_when_no_deltas_exist(self):
        rows = [
            make_row("model-a", "DSU-001"),
            make_row("model-b", "DSU-001"),
        ]
        report = build_judge_sensitivity_report(rows, ["DSU-001"], "claude-sonnet-4-6")
        self.assertIn("Material divergence (>1 point on any dimension)**: no", report)
        self.assertIn("No judge deltas on this subset.", report)
        self.assertIn("No material judge divergences detected on this subset.", report)


if __name__ == "__main__":
    unittest.main()
