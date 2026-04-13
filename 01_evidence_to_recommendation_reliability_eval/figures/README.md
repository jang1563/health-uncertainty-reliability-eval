# Figures

- checked_on: `2026-04-12`
- project: `Evidence-to-Recommendation Reliability Eval`
- status: `demo and real-run svg figures created`

## 예정 산출물

- `grade_fidelity_summary.png`
- `failure_taxonomy_breakdown.png`
- `c_vs_i_error_profile.png`
- `demo_run_metric_comparison.svg`
- `demo_failure_count_comparison.svg`
- `real_run_metric_comparison.svg`
- `real_failure_count_comparison.svg`
- `real_v1_40_metric_comparison.svg`
- `real_v1_40_failure_count_comparison.svg`

## 현재 상태

- 실제 external model PNG figure는 아직 생성되지 않았다.
- smoke-test demo run 기준 SVG figure와 real run 비교 SVG figure는 생성되어 저장된다.

## 권장 figure 내용

- `grade_fidelity_summary.png`
  - grade별 평균 rubric score
  - grade inflation / deflation count
- `failure_taxonomy_breakdown.png`
  - failure taxonomy stacked bar
  - task family별 분포
- `c_vs_i_error_profile.png`
  - `C`에서의 preference omission
  - `I`에서의 false certainty 또는 overrecommendation
- `demo_run_metric_comparison.svg`
  - reference run과 overconfident baseline의 핵심 metric 비교
- `demo_failure_count_comparison.svg`
  - demo run별 failure taxonomy count 비교
- `real_run_metric_comparison.svg`
  - `gpt-5-mini`와 `gpt-5-nano`의 핵심 metric 비교
- `real_failure_count_comparison.svg`
  - real run별 failure taxonomy count 비교
- `real_v1_40_metric_comparison.svg`
  - expanded `40`-row same-set `gpt-5-mini` vs `gpt-5-nano` metric 비교
- `real_v1_40_failure_count_comparison.svg`
  - expanded `40`-row same-set failure taxonomy count 비교
