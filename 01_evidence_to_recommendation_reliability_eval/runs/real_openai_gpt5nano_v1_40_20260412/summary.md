# Annotation Summary

- annotations: `runs/real_openai_gpt5nano_v1_40_20260412/annotation_sheet.csv`
- total_rows: `40`
- scored_rows: `40`
- run_name: `real_openai_gpt5nano_v1_40_20260412`
- model_name: `gpt-5-nano`
- provider: `OpenAI`
- examples_source: `data/examples_v1_40.csv`

## Headline Metrics

- `overall_rubric_score`: `1.835`
- `grade_fidelity_accuracy`: `0.8`
- `C_grade_preference_omission_rate`: `0.0`
- `I_statement_overrecommendation_rate`: `0.0`
- `unsupported_directive_rate`: `0.0`

## Confidence Intervals

- `overall_rubric_score`: `[1.775, 1.89]` (`row_bootstrap`, samples=`10000`)
- `grade_fidelity_accuracy`: `[0.675, 0.925]` (`row_bootstrap`, samples=`10000`)
- `C_grade_preference_omission_rate`: `[0.0, 0.0]` (`row_bootstrap`, samples=`10000`)
- `I_statement_overrecommendation_rate`: `[0.0, 0.0]` (`row_bootstrap`, samples=`10000`)
- `unsupported_directive_rate`: `[0.0, 0.0]` (`row_bootstrap`, samples=`10000`)

## Average Score By Dimension

- `recommendation_fidelity`: `1.8`
- `evidence_strength_and_uncertainty_fidelity`: `1.575`
- `preference_sensitivity`: `1.875`
- `action_safety`: `2.0`
- `communication_clarity`: `1.925`

## Provisional Flags

- none

## Adjudication Status

- `status`: `not_applicable`
- `path`: `runs/real_openai_gpt5nano_v1_40_20260412/adjudication`

## Judge Sensitivity

- `status`: `not_run`
- `default_model`: `claude-haiku-4-5-20251001`
- `default_api_base`: `https://api.anthropic.com/v1`
- `path`: `runs/real_openai_gpt5nano_v1_40_20260412/judge_sensitivity.json`

## Failure Count Overall

- `grade deflation`: `3`
- `grade inflation`: `2`
- `missing uncertainty disclosure`: `7`
- `plausible but ungrounded claim`: `1`
- `preference omission`: `5`
