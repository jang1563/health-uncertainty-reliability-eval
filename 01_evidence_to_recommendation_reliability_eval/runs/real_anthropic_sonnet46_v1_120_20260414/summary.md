# Annotation Summary

- annotations: `runs/real_anthropic_sonnet46_v1_120_20260414/annotation_sheet.csv`
- total_rows: `120`
- scored_rows: `119`
- run_name: `real_anthropic_sonnet46_v1_120_20260414`
- model_name: `claude-sonnet-4-6`
- provider: `Anthropic`
- examples_source: `data/examples_v1_120.csv`

## Headline Metrics

- `overall_rubric_score`: `1.6286`
- `grade_fidelity_accuracy`: `0.8655`
- `C_grade_preference_omission_rate`: `0.0938`
- `I_statement_overrecommendation_rate`: `0.125`
- `unsupported_directive_rate`: `0.0756`

## Confidence Intervals

- `overall_rubric_score`: `[1.5613, 1.6924]` (`row_bootstrap`, samples=`10000`)
- `grade_fidelity_accuracy`: `[0.7983, 0.9244]` (`row_bootstrap`, samples=`10000`)
- `C_grade_preference_omission_rate`: `[0.0, 0.2188]` (`row_bootstrap`, samples=`10000`)
- `I_statement_overrecommendation_rate`: `[0.0312, 0.25]` (`row_bootstrap`, samples=`10000`)
- `unsupported_directive_rate`: `[0.0336, 0.1261]` (`row_bootstrap`, samples=`10000`)

## Average Score By Dimension

- `recommendation_fidelity`: `1.7815`
- `evidence_strength_and_uncertainty_fidelity`: `1.8319`
- `preference_sensitivity`: `0.8908`
- `action_safety`: `1.9412`
- `communication_clarity`: `1.6975`

## Provisional Flags

- `incomplete_scoring`
- `chair_reconciliation_pending`

## Adjudication Status

- `status`: `incomplete`
- `packet_rows`: `53`
- `completed_rows`: `0`
- `finalized_rows`: `0`
- `failure_label_exact_match_rate`: `None`
- `path`: `runs/real_anthropic_sonnet46_v1_120_20260414/adjudication/agreement_summary.json`

## Judge Sensitivity

- `status`: `complete`
- `judge_model`: `claude-haiku-4-5-20251001`
- `scored_rows`: `53`
- `changed_rows`: `53`
- `changed_score_rows`: `52`
- `changed_failure_rows`: `53`
- `preference_sensitivity_exact_agreement`: `0.0755`
- `failure_label_exact_match_rate`: `0.0`
- `path`: `runs/real_anthropic_sonnet46_v1_120_20260414/judge_sensitivity.json`

## Judge Disagreement

- `status`: `complete`
- `priority_rows`: `53`
- `priority_bucket_counts`: `{"critical": 24, "high": 29}`
- `secondary_blank_failure_rows`: `47`
- `primary_zero_to_secondary_positive_preference_rows`: `43`
- `top_priority_adjudication_ids`: `["adj_043", "adj_033", "adj_013", "adj_010", "adj_051", "adj_039", "adj_019", "adj_006", "adj_053", "adj_052"]`
- `path`: `runs/real_anthropic_sonnet46_v1_120_20260414/adjudication/judge_disagreement_summary.json`

## Chair Reconciliation

- `status`: `not_ready`
- `completed_rows`: `0`
- `incomplete_rows`: `53`
- `agreement_rows`: `0`
- `disagreement_rows`: `0`
- `priority_bucket_counts`: `{"blocked": 53}`
- `top_priority_adjudication_ids`: `["adj_053", "adj_052", "adj_051", "adj_050", "adj_049", "adj_048", "adj_047", "adj_046", "adj_045", "adj_044"]`
- `path`: `runs/real_anthropic_sonnet46_v1_120_20260414/adjudication/chair_reconciliation_summary.json`

## Failure Count Overall

- `grade deflation`: `3`
- `grade inflation`: `4`
- `missing uncertainty disclosure`: `6`
- `preference omission`: `61`
- `unsupported directive`: `9`
