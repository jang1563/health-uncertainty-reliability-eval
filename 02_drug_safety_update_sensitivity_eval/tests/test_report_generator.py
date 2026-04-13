import tempfile
import unittest
from pathlib import Path

from eval.report_generator import compute_metrics, write_report


def make_result(case_id, update_uptake, total, reasoning):
    return {
        "case_id": case_id,
        "drug_name": "Drug A",
        "section_changed": "boxed_warning_or_contraindication",
        "update_direction": "risk_increase",
        "severity_tier": "critical",
        "prompt_variant": "patient_plain_language",
        "before_response": "before",
        "after_response": "after",
        "scores": {
            "update_uptake": update_uptake,
            "stale_advice_avoidance": 2,
            "safety_severity_calibration": 2,
            "actionability_and_followup_guidance": 2,
            "source_grounded_communication": 2,
            "reasoning": reasoning,
            "total": total,
            "judge_error": None,
        },
    }


class ReportGeneratorTests(unittest.TestCase):
    def test_write_report_surfaces_partial_shifts(self):
        results = [
            make_result("DSU-001-patient_plain_language", 2, 10, "clean shift"),
            make_result("DSU-002-patient_plain_language", 1, 9, "partial shift"),
        ]
        metrics = compute_metrics(results)

        with tempfile.TemporaryDirectory() as tmpdir:
            report_path = Path(tmpdir) / "report.md"
            figures_dir = Path(tmpdir) / "figures"
            write_report(metrics, results, str(report_path), str(figures_dir), "test-model")
            report_text = report_path.read_text()

        self.assertIn("Mean total score (/10)", report_text)
        self.assertIn("Partial shifts (update_uptake = 1): 1", report_text)
        self.assertIn("Failed shifts (update_uptake = 0): 0", report_text)
        self.assertIn("Items where update_uptake < 2", report_text)
        self.assertIn("DSU-002-patient_plain_language", report_text)
        self.assertIn("partial shift", report_text)


if __name__ == "__main__":
    unittest.main()
