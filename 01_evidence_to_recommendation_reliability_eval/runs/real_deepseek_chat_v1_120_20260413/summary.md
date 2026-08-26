# Annotation Summary

- annotations: `runs/real_deepseek_chat_v1_120_20260413/annotation_sheet.csv`
- total_rows: `120`
- scored_rows: `120`
- run_name: `real_deepseek_chat_v1_120_20260413`
- model_name: `deepseek-chat`
- provider: `DeepSeek`
- examples_source: `data/examples_v1_120.csv`

## Headline Metrics

- `overall_rubric_score`: `1.59`
- `grade_fidelity_accuracy`: `0.7333`
- `C_grade_preference_omission_rate`: `0.5938`
- `I_statement_overrecommendation_rate`: `0.1875`
- `unsupported_directive_rate`: `0.0667`

## Confidence Intervals

- `overall_rubric_score`: `[1.5, 1.675]` (`row_bootstrap`, samples=`10000`)
- `grade_fidelity_accuracy`: `[0.65, 0.8083]` (`row_bootstrap`, samples=`10000`)
- `C_grade_preference_omission_rate`: `[0.4375, 0.75]` (`row_bootstrap`, samples=`10000`)
- `I_statement_overrecommendation_rate`: `[0.0625, 0.3438]` (`row_bootstrap`, samples=`10000`)
- `unsupported_directive_rate`: `[0.025, 0.1167]` (`row_bootstrap`, samples=`10000`)

## Average Score By Dimension

- `recommendation_fidelity`: `1.6333`
- `evidence_strength_and_uncertainty_fidelity`: `1.275`
- `preference_sensitivity`: `1.4333`
- `action_safety`: `1.775`
- `communication_clarity`: `1.8333`

## Provisional Flags

- none

## Adjudication Status

- `status`: `not_applicable`
- `path`: `runs/real_deepseek_chat_v1_120_20260413/adjudication`

## Judge Sensitivity

- `status`: `not_run`
- `default_model`: `claude-haiku-4-5-20251001`
- `default_api_base`: `https://api.anthropic.com/v1`
- `path`: `runs/real_deepseek_chat_v1_120_20260413/judge_sensitivity.json`

## Failure Count Overall

- `grade deflation`: `3`
- `grade inflation`: `7`
- `missing uncertainty disclosure`: `55`
- `plausible but ungrounded claim`: `1`
- `preference omission`: `32`
- `unsupported directive`: `8`
