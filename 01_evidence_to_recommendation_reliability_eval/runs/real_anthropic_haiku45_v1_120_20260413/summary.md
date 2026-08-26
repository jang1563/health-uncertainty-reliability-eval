# Annotation Summary

- annotations: `runs/real_anthropic_haiku45_v1_120_20260413/annotation_sheet.csv`
- total_rows: `120`
- scored_rows: `120`
- run_name: `real_anthropic_haiku45_v1_120_20260413`
- model_name: `claude-haiku-4-5-20251001`
- provider: `Anthropic`
- examples_source: `data/examples_v1_120.csv`

## Headline Metrics

- `overall_rubric_score`: `1.675`
- `grade_fidelity_accuracy`: `0.7833`
- `C_grade_preference_omission_rate`: `0.4688`
- `I_statement_overrecommendation_rate`: `0.1875`
- `unsupported_directive_rate`: `0.0583`

## Confidence Intervals

- `overall_rubric_score`: `[1.595, 1.7483]` (`row_bootstrap`, samples=`10000`)
- `grade_fidelity_accuracy`: `[0.7083, 0.8583]` (`row_bootstrap`, samples=`10000`)
- `C_grade_preference_omission_rate`: `[0.2812, 0.6258]` (`row_bootstrap`, samples=`10000`)
- `I_statement_overrecommendation_rate`: `[0.0625, 0.3438]` (`row_bootstrap`, samples=`10000`)
- `unsupported_directive_rate`: `[0.025, 0.1]` (`row_bootstrap`, samples=`10000`)

## Average Score By Dimension

- `recommendation_fidelity`: `1.7167`
- `evidence_strength_and_uncertainty_fidelity`: `1.4167`
- `preference_sensitivity`: `1.5083`
- `action_safety`: `1.8417`
- `communication_clarity`: `1.8917`

## Provisional Flags

- none

## Adjudication Status

- `status`: `not_applicable`
- `path`: `runs/real_anthropic_haiku45_v1_120_20260413/adjudication`

## Judge Sensitivity

- `status`: `not_run`
- `default_model`: `claude-haiku-4-5-20251001`
- `default_api_base`: `https://api.anthropic.com/v1`
- `path`: `runs/real_anthropic_haiku45_v1_120_20260413/judge_sensitivity.json`

## Failure Count Overall

- `grade deflation`: `4`
- `grade inflation`: `7`
- `missing uncertainty disclosure`: `39`
- `preference omission`: `28`
- `unsupported directive`: `7`
