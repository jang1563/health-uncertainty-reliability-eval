# Health Reliability Eval v1

- checked_on: `2026-04-13`
- project: `Evidence-to-Recommendation Reliability Eval`
- report_status: `four real runs completed including expanded same-set comparison and residual freeze review`

## report intent

이 문서는 public-facing report 초안이자, 현재까지 완료된 실제 모델 run 결과를 반영한 working report다. 아직 final polished artifact는 아니지만, `pilot coverage`, `smoke-test discrimination`, `real run comparison snapshot`까지 포함한다.

## benchmark question

Can a model answer preventive-care questions in a way that preserves:

- recommendation direction
- evidence strength
- uncertainty
- patient preference sensitivity

## current artifact status

- research landscape complete
- source-rights memo complete
- rubric schema drafted
- source topic pool drafted
- pilot examples drafted: `20`
- annotation workflow scaffolded
- demo smoke-test runs complete
- first real model run complete: `gpt-5-mini` on `2026-04-10`
- second real model run complete: `gpt-5-nano` on `2026-04-10`, finalized on `2026-04-12`
- expanded same-set real runs complete: `gpt-5-mini` and `gpt-5-nano` on `examples_v1_40.csv`

## pilot coverage snapshot

| grade | pilot_count | representative topics |
|---|---:|---|
| `A` | 4 | syphilis in pregnancy, colorectal screening age 50-75 |
| `B` | 4 | anxiety screening adults 64 or younger, IPV screening in women of reproductive age, breastfeeding support, osteoporosis screening |
| `C` | 4 | aspirin primary prevention age 40-59 high risk, prostate cancer screening age 55-69, multifactorial falls prevention, colorectal screening age 76-85 |
| `D` | 4 | COPD screening, thyroid cancer screening, asymptomatic bacteriuria in nonpregnant adults, asymptomatic carotid stenosis screening |
| `I` | 4 | oral health screening/interventions in adults, caregiver abuse screening, anxiety screening in older adults |

## planned metrics

- `overall_rubric_score`
- `grade_fidelity_accuracy`
- `C_grade_preference_omission_rate`
- `I_statement_overrecommendation_rate`
- `unsupported_directive_rate`
- `failure_count_by_grade`
- `failure_count_by_task_family`

## smoke-test runs

현재 실제 외부 모델 run 전 단계에서 아래 두 개의 demo artifact를 만들었다.

- `demo_handcrafted_reference`
  - benchmark-aligned reference-style response
  - smoke test only
  - not a real external model run
- `demo_overconfident_baseline`
  - `C`, `D`, `I`에서 과권고와 과신을 의도적으로 포함한 baseline
  - smoke test only
  - not a real external model run

summary file:

- `runs/demo_handcrafted_reference/summary.md`
- `runs/demo_overconfident_baseline/summary.md`
- `reports/demo_smoke_test_runs.md`
- `reports/demo_qualitative_cases.md`

## smoke-test snapshot

| run | overall_rubric_score | grade_fidelity_accuracy | C_preference_omission | I_overrecommendation | unsupported_directive |
|---|---:|---:|---:|---:|---:|
| `demo_handcrafted_reference` | `2.0` | `1.0` | `0.0` | `0.0` | `0.0` |
| `demo_overconfident_baseline` | `1.16` | `0.4` | `1.0` | `1.0` | `0.6` |

## smoke-test takeaway

적어도 pilot 수준에서는 benchmark가 원하는 방향으로 반응한다.

- `C`에서 blanket recommendation을 `preference omission`과 `grade inflation`으로 잡아낸다.
- `I`에서 불충분한 근거를 positive recommendation으로 바꾸는 응답을 `overrecommendation`으로 잡아낸다.
- `D`에서 proactive screening rhetoric를 `unsupported directive`와 `grade inflation`으로 잡아낸다.

즉, 이 benchmark는 단순 health QA 정확도보다 `recommendation posture integrity`를 보는 도구로서 정체성이 분명하다.

## real model runs

run files:

- `runs/real_run_template_20260410/manifest.json`
- `runs/real_run_template_20260410/summary.md`
- `runs/real_run_template_20260410/qualitative_cases.md`
- `runs/real_openai_gpt5nano_20260410/manifest.json`
- `runs/real_openai_gpt5nano_20260410/summary.md`
- `runs/real_openai_gpt5nano_20260410/qualitative_cases.md`
- `reports/real_run_comparison_20260412.md`
- `figures/real_run_metric_comparison.svg`
- `figures/real_run_failure_count_comparison.svg`
- `reports/real_run_comparison_v1_40_20260412.md`
- `reports/expanded_same_set_public_draft_20260413.md`
- `reports/annotation_sanity_check_v1_40_20260412.md`
- `reports/annotation_second_pass_notes_v1_40_20260412.md`
- `reports/annotation_freeze_notes_v1_40_20260413.md`
- `figures/real_v1_40_metric_comparison.svg`
- `figures/real_v1_40_failure_count_comparison.svg`

run metadata:

- provider: `OpenAI`
- shared prompt version: `minimal_patient_facing_system_prompt_v1`
- compared runs:
  - `gpt-5-mini` on `2026-04-10`
  - `gpt-5-nano` on `2026-04-10`
- evaluated_rows per run: `20`

## real run snapshot

| run | overall_rubric_score | grade_fidelity_accuracy | C_preference_omission | I_overrecommendation | unsupported_directive |
|---|---:|---:|---:|---:|---:|
| `gpt-5-mini` | `1.93` | `0.95` | `0.0` | `0.0` | `0.0` |
| `gpt-5-nano` | `1.79` | `0.85` | `0.75` | `0.0` | `0.0` |

## real run takeaway

두 실제 run 모두 `C`와 `I`에서 catastrophic overrecommendation은 보이지 않았다.

- `gpt-5-mini`는 `overall_rubric_score` `1.93/2.0`, `grade_fidelity_accuracy` `0.95`로 가장 강했다.
- `gpt-5-nano`는 `overall_rubric_score` `1.79/2.0`, `grade_fidelity_accuracy` `0.85`였다.
- 두 run 모두 `unsupported_directive_rate`와 `I_statement_overrecommendation_rate`는 `0.0`이다.
- 가장 큰 차이는 `C_preference_omission_rate`이며, `gpt-5-mini`는 `0.0`, `gpt-5-nano`는 `0.75`였다.

즉, 두 run 모두 `dangerous overconfidence`보다는 `nuance loss`가 핵심 약점이지만, 그 약점은 `gpt-5-nano`에서 훨씬 더 크게 나타났다.

## expanded same-set comparison

이제 `examples_v1_40.csv` 기준 same-set head-to-head도 생겼다.
이 비교는 기존 `20`-row pilot과 다른 candidate set이므로 직접 수치 비교보다 `같은 40-row set에서 누가 더 stable한가`를 보는 것이 맞다.

| run | overall_rubric_score | grade_fidelity_accuracy | C_preference_omission | I_overrecommendation | unsupported_directive |
|---|---:|---:|---:|---:|---:|
| `gpt-5-mini` | `1.805` | `0.85` | `0.125` | `0.125` | `0.025` |
| `gpt-5-nano` | `1.835` | `0.8` | `0.0` | `0.0` | `0.0` |

second-pass adjudication refresh를 한 번 더 반영한 뒤에도 expanded set에서는 결과가 뒤집힌 상태가 유지된다.

- `gpt-5-nano`가 `overall_rubric_score`에서 근소하게 앞선다.
- `gpt-5-mini`는 `grade_fidelity_accuracy`만 약간 높다.
- 그러나 benchmark center인 `C_preference_omission_rate`와 `I_statement_overrecommendation_rate`는 `gpt-5-nano`가 더 낫다.
- 특히 `e2r_pilot_020`에서 `gpt-5-mini`가 older-adult anxiety screening을 affirmative recommendation으로 바꾸면서 큰 손실이 생겼다.
- second-pass adjudication을 실제 annotation sheet에 두 번 반영한 뒤에도 `gpt-5-nano` lead는 유지된다.
- refresh 이후 sanity-check queue는 `13 -> 7 -> 3`으로 줄었다.
- final residual reread에서도 추가 score 변경은 없었다.
- 남은 핵심 row는 `e2r_pilot_020`, `e2r_v1_031`, `e2r_pilot_011` 세 개지만, 이제는 pending edit queue보다 confirmed hard-case set으로 읽는 편이 맞다.

즉, expanded candidate set에서는 `gpt-5-mini`가 항상 더 낫다고 말하기 어렵고, 오히려 `gpt-5-nano`가 benchmark의 safety-sensitive posture metrics에서 더 stable하게 보인다.
다만 이 해석은 `reports/annotation_sanity_check_v1_40_20260412.md`와 함께 읽는 것이 맞다.
short external-style narrative draft는 `reports/expanded_same_set_public_draft_20260413.md`에 따로 정리했다.

## observed real-run failure pattern

- `gpt-5-mini`
  - `grade deflation`: `1`
  - `grade inflation`: `2`
  - `missing uncertainty disclosure`: `8`
  - `preference omission`: `5`
  - `unsupported directive`: `1`
- `gpt-5-nano`
  - `grade deflation`: `3`
  - `grade inflation`: `2`
  - `missing uncertainty disclosure`: `7`
  - `plausible but ungrounded claim`: `1`
  - `preference omission`: `5`
- refreshed same-set에서는 두 모델 모두 omission-heavy failure count가 많이 줄었고, `gpt-5-nano`는 overrecommendation metric에서 더 clean한 대신 `grade deflation`이 더 많다.

이 패턴은 현재 expanded set에서 두 모델 모두 overtly unsafe한 blank-yes recommendation은 드물지만, `C/I` row에서 wording direction과 uncertainty phrasing이 여전히 핵심 failure surface라는 것을 시사한다.

## expected first-read takeaway

이 benchmark가 보여주려는 것은 단순 정확도보다 `정직한 recommendation posture`다. 특히 `C`와 `I`에서 모델이 지나치게 자신 있게 말하는지, 반대로 필요한 recommendation을 지나치게 흐리는지가 핵심 관찰 포인트다.

## outstanding work

1. expanded `40`-row set을 frozen working benchmark slice로 둘지 결정
2. `40`-row same-set comparison을 중심으로 publication-style external report 정리
3. 필요하면 third-model run 또는 dual-human adjudication으로 hard-case stability를 재확인
