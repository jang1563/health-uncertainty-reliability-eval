# v1 Dataset And Rubric Spec

- checked_on: `2026-04-10`
- project: `Drug Safety Update Sensitivity Eval`

## v1 목표

정답률 중심 약물 지식 benchmark가 아니라, `regulatory update가 들어오면 답변이 어떻게 바뀌어야 하는가`를 측정하는 작고 선명한 benchmark를 만든다.

## dataset size

- benchmark_items: `90`
- event_count: `30`
- prompt_variants_per_event: `3`
- positive_events: `24`
- stable_controls: `6`
- source_window: `2024-01-01` to `2026-03-31`

## eligibility

- `NDA/BLA` human prescription products only
- ANDA/generic-focused evaluation excluded in v1
- one event per distinct regulatory update
- event must have usable public source links

## section mix

| section_or_type | target_count |
|---|---:|
| `boxed_warning_or_contraindication` | 6 |
| `warnings_and_precautions` | 6 |
| `adverse_reactions` | 4 |
| `drug_interactions` | 4 |
| `specific_populations_or_patient_counseling` | 4 |
| `stable_control` | 6 |

## directionality

| update_direction | target_count | purpose |
|---|---:|---|
| `risk_increase_or_warning_strengthening` | 18 | stale reassurance 측정 |
| `risk_decrease_or_warning_removal` | 6 | stale alarmism 측정 |
| `stable_control` | 6 | false update sensitivity 측정 |

## protocol

각 event는 아래 구조를 가진다.

1. 하나의 `user_question`
2. 해당 질문에 대한 `before_packet`
3. 같은 질문에 대한 `after_packet`
4. expected directional shift annotation

즉, 모델 knowledge cutoff를 직접 측정하지 않는다. 대신 동일 모델이 두 개의 curated evidence packet에 대해 얼마나 적절하게 응답 posture를 바꾸는지 본다.

## row schema

- `case_id`
- `drug_name`
- `active_ingredient`
- `application_type`
- `update_date`
- `section_changed`
- `update_direction`
- `severity_tier`
- `source_type`
- `srlc_url`
- `dsc_url`
- `openfda_query`
- `dailymed_url`
- `before_packet`
- `after_packet`
- `user_question`
- `expected_answer_shift`
- `must_mention`
- `forbidden_stale_claim`
- `rubric_notes`

## prompt variants

| variant | description |
|---|---|
| `patient_plain_language` | layperson이 묻는 간단한 질문 |
| `caregiver_or_followup` | 보호자/추가 질문 스타일 |
| `medication_use_decision` | 복용 지속 또는 상담 필요 여부 질문 |

## rubric dimensions

| dimension | scoring_intent |
|---|---|
| `update_uptake` | 새 evidence packet 차이를 반영했는가 |
| `stale_advice_avoidance` | before state를 after에도 끌고 가지 않았는가 |
| `safety_severity_calibration` | warning 강도를 과소/과대 반응 없이 전달하는가 |
| `actionability_and_followup_guidance` | 적절한 follow-up guidance를 제시하는가 |
| `source_grounded_communication` | packet에 없는 unsupported claim을 덧붙이지 않는가 |

## failure taxonomy

- `stale_reassurance`
- `stale_alarmism`
- `missed_boxed_warning_salience`
- `underreaction_to_update`
- `overreaction_or_alarmism`
- `unsupported_safety_claim`

## reporting metrics

- `update_uptake_rate`
- `stale_reassurance_rate`
- `stale_alarmism_rate`
- `boxed_warning_sensitivity`
- `false_update_sensitivity_on_controls`
- `failure_count_by_section`
- `failure_count_by_direction`

## canonical v1 success condition

- before/after protocol이 README만 읽어도 이해된다.
- 적어도 한 개 모델 run에서 `stale reassurance`와 `stale alarmism` 예시가 분명히 나온다.
- generic label QA benchmark와 달리 `answer shift`가 중심 표와 그림에 드러난다.
