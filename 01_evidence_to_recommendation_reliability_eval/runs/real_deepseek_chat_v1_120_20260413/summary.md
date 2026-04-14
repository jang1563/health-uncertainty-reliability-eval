# Pilot Annotation Summary

- annotations: `runs/real_deepseek_chat_v1_120_20260413/annotation_sheet.csv`
- total_rows: `120`
- scored_rows: `120`

## headline metrics

- `overall_rubric_score`: `1.59`
- `grade_fidelity_accuracy`: `0.7333`
- `C_grade_preference_omission_rate`: `0.5938`
- `I_statement_overrecommendation_rate`: `0.1875`
- `unsupported_directive_rate`: `0.0667`

## average score by dimension

- `recommendation_fidelity`: `1.6333`
- `evidence_strength_and_uncertainty_fidelity`: `1.275`
- `preference_sensitivity`: `1.4333`
- `action_safety`: `1.775`
- `communication_clarity`: `1.8333`

## benchmark row count by grade

- `A`: `16`
- `B`: `24`
- `C`: `32`
- `D`: `16`
- `I`: `32`

## scored row count by grade

- `A`: `16`
- `B`: `24`
- `C`: `32`
- `D`: `16`
- `I`: `32`

## benchmark row count by task family

- `direct_recommendation`: `36`
- `expert_explanation`: `48`
- `preference_sensitive`: `16`
- `uncertainty_elicitation`: `20`

## scored row count by task family

- `direct_recommendation`: `36`
- `expert_explanation`: `48`
- `preference_sensitive`: `16`
- `uncertainty_elicitation`: `20`

## failure count overall

- `grade deflation`: `3`
- `grade inflation`: `7`
- `missing uncertainty disclosure`: `55`
- `plausible but ungrounded claim`: `1`
- `preference omission`: `32`
- `unsupported directive`: `8`
