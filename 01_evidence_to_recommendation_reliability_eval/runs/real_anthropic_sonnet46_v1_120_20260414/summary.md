# Pilot Annotation Summary

- annotations: `runs/real_anthropic_sonnet46_v1_120_20260414/annotation_sheet.csv`
- total_rows: `120`
- scored_rows: `119`

## headline metrics

- `overall_rubric_score`: `1.6286`
- `grade_fidelity_accuracy`: `0.8655`
- `C_grade_preference_omission_rate`: `0.0938`
- `I_statement_overrecommendation_rate`: `0.125`
- `unsupported_directive_rate`: `0.0756`

## average score by dimension

- `recommendation_fidelity`: `1.7815`
- `evidence_strength_and_uncertainty_fidelity`: `1.8319`
- `preference_sensitivity`: `0.8908`
- `action_safety`: `1.9412`
- `communication_clarity`: `1.6975`

## benchmark row count by grade

- `A`: `16`
- `B`: `24`
- `C`: `32`
- `D`: `16`
- `I`: `32`

## scored row count by grade

- `A`: `15`
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
- `expert_explanation`: `47`
- `preference_sensitive`: `16`
- `uncertainty_elicitation`: `20`

## failure count overall

- `grade deflation`: `3`
- `grade inflation`: `4`
- `missing uncertainty disclosure`: `6`
- `preference omission`: `61`
- `unsupported directive`: `9`
