# Drug Safety Update Sensitivity Eval — v1 Results Summary

- updated_on: 2026-04-13
- dataset: 90 items (30 FDA safety events x 3 prompt variants)
- primary judge: `claude-haiku-4-5-20251001`
- judge-sensitivity validation: `claude-sonnet-4-6` on a curated 10-case subset across all completed model runs

## Final Model Comparison

| Model | Overall update uptake | Mean total (/10) | Partial shifts | Failed shifts | Boxed warning sensitivity | Stale reassurance | Stale alarmism |
|---|---:|---:|---:|---:|---:|---:|---:|
| `gpt-5-nano` | 100.0% | 10.00 | 0 | 0 | 100.0% | 0.0% | 0.0% |
| `claude-haiku-4-5-20251001` | 99.4% | 9.97 | 1 | 0 | 100.0% | 0.0% | 0.0% |
| `gpt-4o-mini` | 98.9% | 9.81 | 2 | 0 | 97.2% | 0.0% | 0.0% |

## Main Takeaways

- `gpt-5-nano` was the strongest model in this benchmark run, reaching perfect scores on all reported topline metrics.
- `claude-haiku-4-5-20251001` remained very strong, with a single partial case under the tightened rubric: `DSU-019-patient_plain_language`.
- `gpt-4o-mini` stayed competitive overall but had more edge-case weakness in `medication_use_decision` prompts and in `drug_interactions` / `boxed_warning_or_contraindication` cases.
- No model showed stale reassurance, stale alarmism, or false update sensitivity on the stable controls in the completed benchmark runs.

## Where Models Differed Most

- Largest section gap: `drug_interactions`
- Largest prompt-variant gap: `medication_use_decision`
- Most notable disagreement cases:
  - `DSU-009-medication_use_decision` (`Ocaliva`)
  - `DSU-004-medication_use_decision` (`Neurontin`)
  - `DSU-019-patient_plain_language` (`Paxlovid`)

## Judge Sensitivity

The benchmark runs used `claude-haiku-4-5-20251001` as the consistent primary judge. To test judge robustness, a curated 10-case subset was re-judged with `claude-sonnet-4-6` across all three completed model runs (30 scored pairs total).

| Validation result | Value |
|---|---:|
| Re-judged rows | 30 |
| Rows with any judge delta | 7 |
| Rows with >1-point dimension divergence | 0 |

- No material judge divergence was observed on the Sonnet subset.
- All Sonnet-vs-Haiku differences were limited to 1-point edge-case shifts.
- `gpt-5-nano` matched exactly on all 10 re-judged subset rows.

## Artifact Index

- Cross-model comparison: [cross_model_comparison.md](reports/cross_model_comparison.md)
- Haiku report: [haiku_v2.md](reports/haiku_v2.md)
- GPT-4o-mini report: [gpt4o_mini.md](reports/gpt4o_mini.md)
- GPT-5-nano report: [gpt5_nano.md](reports/gpt5_nano.md)
- Sonnet judge-sensitivity report: [judge_sensitivity_sonnet_subset.md](reports/judge_sensitivity_sonnet_subset.md)
