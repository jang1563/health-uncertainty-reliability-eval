import json
import unittest
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "benchmark_items.jsonl"
README_PATH = ROOT / "README.md"
METHODOLOGY_PATH = ROOT / "docs" / "methodology.md"


def load_items():
    rows = []
    with DATA_PATH.open() as handle:
        for line in handle:
            if not line.strip():
                continue
            row = json.loads(line)
            if "_meta" in row:
                continue
            rows.append(row)
    return rows


class DatasetAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.items = load_items()
        cls.events = {
            item["case_id"].rsplit("-", 1)[0]: item
            for item in cls.items
        }
        cls.readme = README_PATH.read_text()
        cls.methodology = METHODOLOGY_PATH.read_text()

    def test_dataset_has_30_events_and_3_variants_each(self):
        self.assertEqual(len(self.items), 90)
        self.assertEqual(len(self.events), 30)

        by_variant = Counter(item["prompt_variant"] for item in self.items)
        self.assertEqual(
            by_variant,
            {
                "patient_plain_language": 30,
                "caregiver_or_followup": 30,
                "medication_use_decision": 30,
            },
        )

    def test_direction_mix_matches_docs(self):
        direction_counts = Counter(item["update_direction"] for item in self.events.values())
        self.assertEqual(
            direction_counts,
            {
                "risk_increase": 17,
                "risk_decrease": 7,
                "stable": 6,
            },
        )

        self.assertIn("| Risk increase / warning strengthening | 17 |", self.readme)
        self.assertIn("| Risk decrease / warning removal | 7 |", self.readme)
        self.assertIn("| Stable control | 6 |", self.readme)
        self.assertIn("| Risk increase / warning strengthening | 17 |", self.methodology)
        self.assertIn("| Risk decrease / warning removal | 7 |", self.methodology)
        self.assertIn("| Stable | 6 |", self.methodology)

    def test_section_mix_matches_docs(self):
        section_counts = Counter(item["section_changed"] for item in self.events.values())
        self.assertEqual(
            section_counts,
            {
                "boxed_warning_or_contraindication": 6,
                "warnings_and_precautions": 6,
                "adverse_reactions": 4,
                "drug_interactions": 3,
                "specific_populations_or_patient_counseling": 5,
                "stable_control": 6,
            },
        )

        self.assertIn("| Drug interactions | 3 |", self.readme)
        self.assertIn("| Specific populations / patient counseling | 5 |", self.readme)
        self.assertIn("| Drug interactions | 3 |", self.methodology)
        self.assertIn("| Specific populations / patient counseling | 5 |", self.methodology)

    def test_stable_after_packets_are_standalone_and_complete(self):
        stable_items = [item for item in self.items if item["update_direction"] == "stable"]
        self.assertEqual(len(stable_items), 18)

        for item in stable_items:
            after_packet = item["after_packet"]
            self.assertIn("NO SAFETY UPDATE:", after_packet)
            self.assertIn("CURRENT SAFETY PROFILE:", after_packet)
            self.assertIn("RELEVANT LABEL SECTIONS:", after_packet)
            self.assertIn("KNOWN SAFETY SIGNALS:", after_packet)
            self.assertIn(item["openfda_query"], after_packet)
            self.assertIn(item["dailymed_url"], after_packet)
            self.assertNotIn("before_packet", after_packet.lower())


if __name__ == "__main__":
    unittest.main()
