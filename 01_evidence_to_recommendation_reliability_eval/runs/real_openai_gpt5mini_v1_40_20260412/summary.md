# Annotation Summary

- annotations: `runs/real_openai_gpt5mini_v1_40_20260412/annotation_sheet.csv`
- total_rows: `40`
- scored_rows: `40`
- run_name: `real_openai_gpt5mini_v1_40_20260412`
- model_name: `gpt-5-mini`
- provider: `OpenAI`
- examples_source: `data/examples_v1_40.csv`

## Headline Metrics

- `overall_rubric_score`: `1.805`
- `grade_fidelity_accuracy`: `0.85`
- `C_grade_preference_omission_rate`: `0.125`
- `I_statement_overrecommendation_rate`: `0.125`
- `unsupported_directive_rate`: `0.025`

## Confidence Intervals

- `overall_rubric_score`: `[1.7, 1.885]` (`row_bootstrap`, samples=`10000`)
- `grade_fidelity_accuracy`: `[0.725, 0.95]` (`row_bootstrap`, samples=`10000`)
- `C_grade_preference_omission_rate`: `[0.0, 0.375]` (`row_bootstrap`, samples=`10000`)
- `I_statement_overrecommendation_rate`: `[0.0, 0.375]` (`row_bootstrap`, samples=`10000`)
- `unsupported_directive_rate`: `[0.0, 0.075]` (`row_bootstrap`, samples=`10000`)

## Average Score By Dimension

- `recommendation_fidelity`: `1.825`
- `evidence_strength_and_uncertainty_fidelity`: `1.575`
- `preference_sensitivity`: `1.75`
- `action_safety`: `1.95`
- `communication_clarity`: `1.925`

## Provisional Flags

- none

## Adjudication Status

- `status`: `not_applicable`
- `path`: `runs/real_openai_gpt5mini_v1_40_20260412/adjudication`

## Judge Sensitivity

- `status`: `not_run`
- `default_model`: `claude-haiku-4-5-20251001`
- `default_api_base`: `https://api.anthropic.com/v1`
- `path`: `runs/real_openai_gpt5mini_v1_40_20260412/judge_sensitivity.json`

## Failure Count Overall

- `grade deflation`: `1`
- `grade inflation`: `2`
- `missing uncertainty disclosure`: `8`
- `preference omission`: `5`
- `unsupported directive`: `1`
