# Pilot Annotation Summary

- annotations: `01_evidence_to_recommendation_reliability_eval/runs/demo_overconfident_baseline/annotations.csv`
- total_rows: `20`
- scored_rows: `20`

## headline metrics

- `overall_rubric_score`: `1.16`
- `grade_fidelity_accuracy`: `0.4`
- `C_grade_preference_omission_rate`: `1.0`
- `I_statement_overrecommendation_rate`: `1.0`
- `unsupported_directive_rate`: `0.6`

## average score by dimension

- `recommendation_fidelity`: `0.8`
- `evidence_strength_and_uncertainty_fidelity`: `0.8`
- `preference_sensitivity`: `1.6`
- `action_safety`: `0.8`
- `communication_clarity`: `1.8`

## benchmark row count by grade

- `A`: `4`
- `B`: `4`
- `C`: `4`
- `D`: `4`
- `I`: `4`

## scored row count by grade

- `A`: `4`
- `B`: `4`
- `C`: `4`
- `D`: `4`
- `I`: `4`

## benchmark row count by task family

- `direct_recommendation`: `9`
- `expert_explanation`: `3`
- `preference_sensitive`: `4`
- `uncertainty_elicitation`: `4`

## scored row count by task family

- `direct_recommendation`: `9`
- `expert_explanation`: `3`
- `preference_sensitive`: `4`
- `uncertainty_elicitation`: `4`

## failure count overall

- `grade inflation`: `12`
- `missing uncertainty disclosure`: `8`
- `preference omission`: `4`
- `unsupported directive`: `12`
