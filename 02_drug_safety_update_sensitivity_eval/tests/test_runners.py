import json
import sys
import tempfile
import unittest
from pathlib import Path
from types import ModuleType, SimpleNamespace
from unittest.mock import patch

from eval import run_eval, run_mock_eval
from eval.run_metadata import MANIFEST_FILENAME


ROOT = Path(__file__).resolve().parents[1]
CANONICAL_ARTIFACTS = [
    ROOT / "reports" / "drug_safety_update_eval_v1.md",
    ROOT / "figures" / "update_uptake_summary.png",
    ROOT / "figures" / "stale_reassurance_breakdown.png",
]


class RunnerSmokeTests(unittest.TestCase):
    def _artifact_snapshot(self):
        snapshot = {}
        for path in CANONICAL_ARTIFACTS:
            snapshot[path] = path.read_bytes() if path.exists() else None
        return snapshot

    def _assert_snapshot_unchanged(self, snapshot):
        for path, original_bytes in snapshot.items():
            if original_bytes is None:
                self.assertFalse(path.exists(), f"{path} should not have been created")
            else:
                self.assertEqual(path.read_bytes(), original_bytes, f"{path} was unexpectedly modified")

    def _fake_call_model(self, _model_name, system_prompt, _user_message, api_key=None):
        del api_key
        if system_prompt.startswith("You are an expert evaluator"):
            return json.dumps(
                {
                    "update_uptake": 2,
                    "stale_advice_avoidance": 2,
                    "safety_severity_calibration": 2,
                    "actionability_and_followup_guidance": 2,
                    "source_grounded_communication": 2,
                    "reasoning": "The after-answer changes in the correct direction.",
                }
            )
        if "NO SAFETY UPDATE:" in system_prompt:
            return "There is no new FDA safety update, and the established safety profile remains the same."
        if "SAFETY UPDATE SUMMARY:" in system_prompt:
            return "There is a new FDA safety warning that should be highlighted clearly."
        return "This medicine has known warnings but no newly introduced regulatory change."

    def _fake_generate_figures(self, results, figures_dir):
        self.assertTrue(results)
        figures_path = Path(figures_dir)
        figures_path.mkdir(parents=True, exist_ok=True)
        (figures_path / "update_uptake_summary.png").write_bytes(b"fake-update-figure")
        (figures_path / "stale_reassurance_breakdown.png").write_bytes(b"fake-stale-figure")

    def test_run_eval_writes_artifacts_under_output_dir(self):
        snapshot = self._artifact_snapshot()

        with tempfile.TemporaryDirectory() as tmpdir:
            with patch("eval.run_eval.call_model", new=self._fake_call_model), \
                    patch("eval.run_eval.time.sleep", return_value=None), \
                    patch("eval.report_generator.generate_figures", new=self._fake_generate_figures):
                exit_code = run_eval.main(
                    [
                        "--model",
                        "stub-model",
                        "--judge",
                        "stub-judge",
                        "--items",
                        "2",
                        "--output",
                        tmpdir,
                    ]
                )

            self.assertEqual(exit_code, 0)
            output_root = Path(tmpdir)
            results_path = output_root / "eval_results.jsonl"
            report_path = output_root / "drug_safety_update_eval_v1.md"
            figures_dir = output_root / "figures"
            manifest_path = output_root / MANIFEST_FILENAME

            self.assertTrue(results_path.exists())
            self.assertTrue(report_path.exists())
            self.assertTrue((figures_dir / "update_uptake_summary.png").exists())
            self.assertTrue((figures_dir / "stale_reassurance_breakdown.png").exists())
            self.assertTrue(manifest_path.exists())

            first_result = json.loads(results_path.read_text().splitlines()[0])
            self.assertIsNone(first_result["scores"]["judge_error"])
            self.assertEqual(first_result["model_name"], "stub-model")
            self.assertEqual(first_result["judge_model"], "stub-judge")
            self.assertEqual(first_result["dataset_item_count"], 2)
            self.assertTrue(first_result["dataset_case_id_hash"])

            manifest = json.loads(manifest_path.read_text())
            self.assertEqual(manifest["model_name"], "stub-model")
            self.assertEqual(manifest["judge_model"], "stub-judge")
            self.assertEqual(manifest["dataset_item_count"], 2)
            self.assertEqual(manifest["dataset_case_id_hash"], first_result["dataset_case_id_hash"])

        self._assert_snapshot_unchanged(snapshot)

    def test_run_mock_eval_writes_artifacts_under_output_dir(self):
        snapshot = self._artifact_snapshot()

        with tempfile.TemporaryDirectory() as tmpdir:
            with patch("eval.report_generator.generate_figures", new=self._fake_generate_figures):
                exit_code = run_mock_eval.main(["--output", tmpdir])

            self.assertEqual(exit_code, 0)
            output_root = Path(tmpdir)
            self.assertTrue((output_root / "eval_results_mock.jsonl").exists())
            self.assertTrue((output_root / "drug_safety_update_eval_v1.md").exists())
            self.assertTrue((output_root / "figures" / "update_uptake_summary.png").exists())
            self.assertTrue((output_root / "figures" / "stale_reassurance_breakdown.png").exists())

        self._assert_snapshot_unchanged(snapshot)

    def test_call_openai_retries_with_max_completion_tokens(self):
        captured_calls = []

        class FakeBadRequestError(Exception):
            pass

        class FakeCompletions:
            def create(self, **kwargs):
                captured_calls.append(kwargs)
                if "max_tokens" in kwargs:
                    raise FakeBadRequestError(
                        "Unsupported parameter: 'max_tokens' is not supported with this model. "
                        "Use 'max_completion_tokens' instead."
                    )
                return SimpleNamespace(
                    choices=[SimpleNamespace(message=SimpleNamespace(content="ok"))]
                )

        class FakeOpenAIClient:
            def __init__(self, api_key=None):
                self.api_key = api_key
                self.chat = SimpleNamespace(completions=FakeCompletions())

        fake_openai = ModuleType("openai")
        fake_openai.BadRequestError = FakeBadRequestError
        fake_openai.OpenAI = FakeOpenAIClient

        with patch.dict(sys.modules, {"openai": fake_openai}):
            content = run_eval._call_openai(
                "gpt-5-nano",
                "system",
                "user",
                api_key="test-key",
            )

        self.assertEqual(content, "ok")
        self.assertEqual(len(captured_calls), 2)
        self.assertIn("max_tokens", captured_calls[0])
        self.assertIn("max_completion_tokens", captured_calls[1])
        self.assertEqual(captured_calls[0]["reasoning_effort"], "minimal")
        self.assertEqual(captured_calls[1]["reasoning_effort"], "minimal")

    def test_call_openai_extracts_text_from_content_blocks(self):
        class FakeCompletions:
            def create(self, **kwargs):
                del kwargs
                return SimpleNamespace(
                    choices=[
                        SimpleNamespace(
                            message=SimpleNamespace(
                                content=[
                                    {"type": "output_text", "text": "hello "},
                                    {"type": "output_text", "text": "world"},
                                ]
                            )
                        )
                    ]
                )

        class FakeOpenAIClient:
            def __init__(self, api_key=None):
                self.api_key = api_key
                self.chat = SimpleNamespace(completions=FakeCompletions())

        fake_openai = ModuleType("openai")
        fake_openai.BadRequestError = RuntimeError
        fake_openai.OpenAI = FakeOpenAIClient

        with patch.dict(sys.modules, {"openai": fake_openai}):
            content = run_eval._call_openai(
                "gpt-4o-mini",
                "system",
                "user",
                api_key="test-key",
            )

        self.assertEqual(content, "hello world")


if __name__ == "__main__":
    unittest.main()
