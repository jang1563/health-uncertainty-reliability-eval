# Drug Safety Update Sensitivity Eval

**Does the model's answer change in the right direction after a new FDA safety update?**

This benchmark evaluates whether AI models appropriately shift their answers to the same user question when provided with updated FDA post-market safety information. It measures *update sensitivity* — not drug knowledge accuracy.

## What This Is

A benchmark-style evaluation package with 90 items (30 FDA safety events x 3 prompt variants). Each event includes:

1. A **before_packet** — curated summary of the drug's safety profile *before* an FDA update
2. An **after_packet** — curated summary reflecting the *new* FDA safety update
3. Three **user_question** variants (patient, caregiver, medication-use decision)
4. Scoring annotations for directional answer shift

The model is prompted twice per item — once with the before_packet, once with the after_packet — and the answer pair is scored on whether the after-answer shifts appropriately relative to the before-answer.

## What This Is NOT

- A generic drug QA benchmark
- A label search product
- A pharmacovigilance mining engine
- A regulatory-grade deployment tool

## Novelty

To our review as of April 10, 2026, we did not find a public benchmark focused on whether model answers appropriately change after new FDA post-market safety updates.

Existing medication benchmarks (LabelComp, AskFDALabel, Rx-LLM, FDARxBench) address label diff detection, label QA, medication task accuracy, or document-grounded reasoning — but none use a paired before/after protocol to measure same-question answer shift after regulatory updates.

Temporal knowledge benchmarks (EvolveBench, DyKnow) evaluate parametric knowledge staleness — whether models recall time-sensitive facts from training. This benchmark evaluates a different capability: context-mediated response shift — whether models appropriately change answers when given different evidence packets at inference time, independent of knowledge cutoff.

## Core Evaluation Questions

1. Does the model distinguish regulatory posture before and after updates?
2. Does it avoid **stale reassurance** when new boxed warnings or warning strengthening occurs?
3. Does it avoid **stale alarmism** when warnings are relaxed or removed?
4. Does it reflect new safety signals with appropriate follow-up guidance?

## Results at a Glance (v1)

Three cost-tiered models evaluated on the 90-item benchmark. Judge: `claude-haiku-4-5-20251001`. Judge-sensitivity validated with a 10-case Sonnet re-judge subset.

| Model | Overall update uptake | Mean total (/10) | Boxed warning sensitivity | Stale reassurance | Stale alarmism |
|---|---:|---:|---:|---:|---:|
| `gpt-5-nano` | 100.0% | 10.00 | 100.0% | 0.0% | 0.0% |
| `claude-haiku-4-5-20251001` | 99.4% | 9.97 | 100.0% | 0.0% | 0.0% |
| `gpt-4o-mini` | 98.9% | 9.81 | 97.2% | 0.0% | 0.0% |

See [reports/v1_results_summary.md](reports/v1_results_summary.md) for the full topline and [reports/cross_model_comparison.md](reports/cross_model_comparison.md) for the detailed analysis.

## Dataset Shape (v1)

| Metric | Value |
|---|---:|
| Total benchmark items | 90 |
| Distinct safety events | 30 |
| Prompt variants per event | 3 |
| Update-positive events | 24 |
| Stable control events | 6 |
| Source window | 2024-01-01 to 2026-03-31 |

### Section Mix

| Section | Count |
|---|---:|
| Boxed warning / contraindication | 6 |
| Warnings and precautions | 6 |
| Adverse reactions | 4 |
| Drug interactions | 3 |
| Specific populations / patient counseling | 5 |
| Stable control | 6 |

### Direction Mix

| Direction | Count | Measures |
|---|---:|---|
| Risk increase / warning strengthening | 17 | Stale reassurance failures |
| Risk decrease / warning removal | 7 | Stale alarmism failures |
| Stable control | 6 | False update sensitivity |

## Rubric Dimensions

| Dimension | What it scores |
|---|---|
| `update_uptake` | Did the after-answer change appropriately relative to the before-answer? |
| `stale_advice_avoidance` | Did the after-answer avoid carrying forward outdated claims from the before-state? |
| `safety_severity_calibration` | Is the after-answer's updated warning intensity proportional? |
| `actionability_and_followup_guidance` | Did the after-answer update next steps appropriately? |
| `source_grounded_communication` | Did the after-answer stay within the after-packet while making the needed shift? |

## Source Policy

| Source | Usage |
|---|---|
| FDA Drug Safety Communications | Paraphrase only — no long-copy |
| FDA SrLC | Paraphrase only — source-linked event reference |
| openFDA | Metadata and query linkage |
| DailyMed | Link only — not a text source |

All benchmark packets are human-authored normalized summaries. No verbatim FDA or DailyMed text is redistributed.

## Eligibility

- NDA/BLA human prescription products only
- ANDA/generic-focused evaluation excluded in v1

## Repository Structure

```
data/
  benchmark_items.jsonl    # 90 benchmark items (30 events x 3 variants)
  schema.json              # JSON Schema for row validation
  event_shortlist.json     # Source metadata for the 30 events
docs/
  methodology.md           # Evaluation protocol and rubric
  limitations.md           # Known limitations
eval/
  run_eval.py              # Evaluation runner
  run_mock_eval.py         # Synthetic scoring without API calls
  run_metadata.py          # Run manifests and metadata validation
  prompts.py               # Target and judge prompt construction
  scoring.py               # Rubric scoring logic
  report_generator.py      # Report and figure generation
  comparison_report.py     # Cross-model comparison reporting
  judge_sensitivity.py     # Re-judge stored answer pairs with an alternate judge
  requirements.txt
  output/                  # Per-model eval_results.jsonl + run_manifest.json
scripts/
  build_comparison_report.py
  run_judge_sensitivity.py # Sonnet judge-sensitivity validation subset
  sanitize_manifests.py    # Dev helper: rewrite manifest paths to project-relative
  generate_remaining_events.py  # Dataset-build helper used during v1 construction
tests/
  test_scoring.py          # Judge prompt/parser coverage
  test_dataset_audit.py    # Dataset and documentation audits
  test_runners.py          # Output-path smoke tests
  test_judge_sensitivity.py
  test_comparison_report.py
  test_report_generator.py
reports/
  v1_results_summary.md                     # Top-level summary of all runs
  cross_model_comparison.md                 # Detailed side-by-side analysis
  haiku_v2.md                               # claude-haiku-4-5-20251001
  gpt4o_mini.md                             # gpt-4o-mini
  gpt5_nano.md                              # gpt-5-nano
  judge_sensitivity_sonnet_subset.md        # Sonnet re-judging validation
figures/
  haiku_v2/                # Per-model figures
  gpt4o_mini/
  gpt5_nano/
research/                  # Research pack (8 documents)
```

## Running the Evaluation

```bash
# Install dependencies
pip install -r eval/requirements.txt

# Run full evaluation (90 items)
python eval/run_eval.py --model claude-sonnet-4-20250514 --judge claude-sonnet-4-20250514

# Run pilot only (18 items, for testing)
python eval/run_eval.py --model claude-sonnet-4-20250514 --judge claude-sonnet-4-20250514 --items 18

# Write artifacts to a custom directory instead of tracked repo files
python eval/run_eval.py --model claude-sonnet-4-20250514 --judge claude-sonnet-4-20250514 --output runs/demo

# Generate report from existing results (defaults to the results directory)
python eval/report_generator.py eval/output/eval_results.jsonl

# Generate synthetic outputs without API calls
python eval/run_mock_eval.py --output eval/output/mock_run

# Re-judge a curated 10-item subset with Sonnet for judge-sensitivity validation
.venv/bin/python3 scripts/run_judge_sensitivity.py \
  --run "haiku_v2=eval/output/haiku_v2/eval_results.jsonl" \
  --run "gpt-4o-mini=eval/output/gpt4o_mini/eval_results.jsonl" \
  --run "gpt-5-nano=eval/output/gpt5_nano/eval_results.jsonl" \
  --judge claude-sonnet-4-6
```

Set `ANTHROPIC_API_KEY` or `OPENAI_API_KEY` environment variables before running.
By default, raw results, markdown reports, and figures are written under the chosen `--output` directory so tracked artifacts in `reports/` and `figures/` are not overwritten.
Each evaluation run also writes `run_manifest.json` into the chosen output directory so later comparisons can verify judge/model/dataset consistency.

## Documentation

- [v1 Results Summary](reports/v1_results_summary.md) — compact topline benchmark outcomes and judge-sensitivity summary
- [Cross-Model Comparison](reports/cross_model_comparison.md) — detailed side-by-side analysis across the three evaluated models
- [Methodology](docs/methodology.md) — evaluation protocol, packet templates, rubric definitions
- [Limitations](docs/limitations.md) — known limitations and scope boundaries
- [Judge Sensitivity Report](reports/judge_sensitivity_sonnet_subset.md) — 10-case Sonnet re-judging subset across completed model runs

## Citing

If you use this benchmark, please cite this repository.

## License

Released under the [MIT License](LICENSE). FDA source documents referenced in the benchmark are public U.S. government information; benchmark packets are human-authored paraphrases with source URLs preserved (see [Source Policy](#source-policy)).
