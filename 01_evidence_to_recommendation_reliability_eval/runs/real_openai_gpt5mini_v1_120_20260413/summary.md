# Annotation Summary

- annotations: `runs/real_openai_gpt5mini_v1_120_20260413/annotation_sheet.csv`
- total_rows: `120`
- scored_rows: `120`
- run_name: `real_openai_gpt5mini_v1_120_20260413`
- model_name: `gpt-5-mini`
- provider: `OpenAI`
- examples_source: `data/examples_v1_120.csv`

## Headline Metrics

- `overall_rubric_score`: `1.7633`
- `grade_fidelity_accuracy`: `0.8917`
- `C_grade_preference_omission_rate`: `0.5938`
- `I_statement_overrecommendation_rate`: `0.0312`
- `unsupported_directive_rate`: `0.0083`

## Confidence Intervals

- `overall_rubric_score`: `[1.7067, 1.8133]` (`row_bootstrap`, samples=`10000`)
- `grade_fidelity_accuracy`: `[0.8333, 0.9417]` (`row_bootstrap`, samples=`10000`)
- `C_grade_preference_omission_rate`: `[0.4062, 0.75]` (`row_bootstrap`, samples=`10000`)
- `I_statement_overrecommendation_rate`: `[0.0, 0.0938]` (`row_bootstrap`, samples=`10000`)
- `unsupported_directive_rate`: `[0.0, 0.025]` (`row_bootstrap`, samples=`10000`)

## Average Score By Dimension

- `recommendation_fidelity`: `1.875`
- `evidence_strength_and_uncertainty_fidelity`: `1.4917`
- `preference_sensitivity`: `1.55`
- `action_safety`: `1.975`
- `communication_clarity`: `1.925`

## Provisional Flags

- none

## Adjudication Status

- `status`: `not_applicable`
- `path`: `runs/real_openai_gpt5mini_v1_120_20260413/adjudication`

## Judge Sensitivity

- `status`: `not_run`
- `default_model`: `claude-haiku-4-5-20251001`
- `default_api_base`: `https://api.anthropic.com/v1`
- `path`: `runs/real_openai_gpt5mini_v1_120_20260413/judge_sensitivity.json`

## Failure Count Overall

- `grade deflation`: `1`
- `missing uncertainty disclosure`: `39`
- `plausible but ungrounded claim`: `2`
- `preference omission`: `33`
- `unsupported directive`: `1`
