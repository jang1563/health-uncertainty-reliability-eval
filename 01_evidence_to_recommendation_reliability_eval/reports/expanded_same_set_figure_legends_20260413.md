# Expanded Same-Set Figure and Table Legends

- checked_on: `2026-04-13`
- purpose: `copy-ready captions for manuscript or slide packaging`
- paired_draft: `reports/expanded_same_set_manuscript_draft_20260413.md`

## Table 1

Headline benchmark metrics for the frozen `40`-row same-set comparison between `gpt-5-mini` and `gpt-5-nano`. Higher is better for `overall_rubric_score` and `grade_fidelity_accuracy`; lower is better for `C_preference_omission`, `I_overrecommendation`, and `unsupported_directive`.

## Table 2

Average dimension-level rubric scores for the frozen `40`-row same-set comparison. Both models were similar on communication clarity and evidence/uncertainty fidelity, while the main separation appeared in preference sensitivity and action safety.

## Figure 1

Metric comparison for the frozen `40`-row same-set slice. `gpt-5-nano` slightly outperformed `gpt-5-mini` on overall rubric score and on the benchmark's most safety-sensitive posture metrics, while `gpt-5-mini` retained a small edge on direct grade fidelity. Source file: `figures/real_v1_40_metric_comparison.svg`.

## Figure 2

Failure-count comparison for the frozen `40`-row same-set slice. Both models mainly failed through nuance loss rather than through frequent overtly unsafe directives; `gpt-5-mini` showed more posture-breaking overrecommendation on hard `C/I` rows, whereas `gpt-5-nano` showed more mild grade deflation. Source file: `figures/real_v1_40_failure_count_comparison.svg`.

## Box 1

Qualitative stress-test cases from the frozen comparison. `e2r_pilot_020` illustrates `I`-statement overrecommendation when insufficient evidence is converted into affirmative screening language. `e2r_pilot_011` illustrates selective-offer drift, where both models mention personalization and preferences but still sound too positive for a Grade `C` recommendation.
