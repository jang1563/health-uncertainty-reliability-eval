# Demo Smoke Test Runs

이 문서는 smoke-test 목적의 demo run 비교 결과를 요약한다.
실제 외부 모델 leaderboard로 해석하면 안 된다.

| run | scored_rows | overall_rubric_score | grade_fidelity_accuracy | C_preference_omission | I_overrecommendation | unsupported_directive |
|---|---:|---:|---:|---:|---:|---:|
| demo_handcrafted_reference | 20 | 2.0 | 1.0 | 0.0 | 0.0 | 0.0 |
| demo_overconfident_baseline | 20 | 1.16 | 0.4 | 1.0 | 1.0 | 0.6 |

## interpretation

- `demo_handcrafted_reference`는 benchmark upper-bound smoke test 역할을 한다.
- `demo_overconfident_baseline`는 `C`, `D`, `I`에서 과권고와 과신을 유도해 benchmark discrimination을 확인하는 역할을 한다.
- 실제 모델 비교는 이 문서가 아니라 future real-run report에서 수행해야 한다.
