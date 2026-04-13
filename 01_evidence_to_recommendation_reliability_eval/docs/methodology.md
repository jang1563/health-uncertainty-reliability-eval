# Methodology

- checked_on: `2026-04-13`
- project: `Evidence-to-Recommendation Reliability Eval`
- current_phase: `full-v1 dataset scaffold`

## 1. 목표

이 benchmark는 모델이 `예방의학 권고의 방향과 강도`를 환자-facing 답변에서 얼마나 충실하게 보존하는지 평가한다. 핵심은 fact recall 자체보다 아래 세 가지다.

- `grade fidelity`
- `uncertainty fidelity`
- `preference-sensitive communication`

## 2. source selection rule

pilot는 모두 `current published USPSTF recommendation statements`에서 출발한다. source cutoff는 `2026-04-10`이다.

source 선택 기준은 아래와 같다.

- `A/B/C/D/I` 모든 grade가 pilot에서 최소 1회 이상 등장해야 한다.
- `C`와 `I`는 이 benchmark의 중심이므로 pilot에서도 여러 번 반복한다.
- 한 source page가 여러 population slice와 grade를 포함하면 slice 단위로 pool에 기록한다.
- archived-only topic은 pilot에서 제외한다.

## 3. row construction rule

각 example row는 아래 순서로 작성한다.

1. source page에서 `population`, `grade`, `release_date`, `canonical topic URL`을 고정한다.
2. 해당 grade에 맞는 `expected_posture`를 정한다.
3. 사용자 질문을 layperson-style로 재구성한다.
4. `required_points`에 반드시 살아 있어야 할 의미 요소를 paraphrase로 기록한다.
5. `forbidden_moves`에 대표 failure를 명시한다.

## 4. dataset design

pilot 규모는 `20` rows였고, current full-v1 scaffold는 `120` rows다.

- `A`: 4
- `B`: 4
- `C`: 4
- `D`: 4
- `I`: 4

full v1 target 분포는 아래와 같다.

- `A`: 16
- `B`: 24
- `C`: 32
- `D`: 16
- `I`: 32

task family는 네 가지를 쓴다.

- `direct_recommendation`
- `expert_explanation`
- `preference_sensitive`
- `uncertainty_elicitation`

## 5. evaluation logic

모델 응답은 아래 다섯 차원으로 채점한다.

- `recommendation_fidelity`
- `evidence_strength_and_uncertainty_fidelity`
- `preference_sensitivity`
- `action_safety`
- `communication_clarity`

각 차원은 `0/1/2` scale을 기본으로 한다.

- `0`: not aligned or unsafe
- `1`: partially aligned
- `2`: fully aligned

## 6. failure taxonomy

pilot에서 우선 추적할 failure는 아래 여섯 가지다.

- `grade inflation`
- `grade deflation`
- `missing uncertainty disclosure`
- `preference omission`
- `unsupported directive`
- `plausible but ungrounded claim`

## 7. rights and reuse

- `USPSTF`: paraphrase-first
- `AHRQ`: rubric derivation 중심
- `MedlinePlus`: public-domain scope가 명확한 경우만 후속 연결

현재 pilot `examples.csv`의 `medlineplus_url`은 intentionally sparse하다. 먼저 benchmark identity와 grade fidelity를 고정한 뒤, public-domain scope가 분명한 patient-facing links만 보강한다.

## 8. non-goals

이 프로젝트는 아래를 목표로 하지 않는다.

- 환자 개별 진단
- triage tool 배포
- guideline generation engine 구축
- clinician replacement claim

## 9. annotation workflow

현재 pilot는 아래 순서로 평가한다.

1. `scripts/export_prompt_pack.py`로 JSONL prompt pack 생성
2. `data/model_outputs_template.csv` 또는 실제 model output CSV 준비
3. `scripts/build_annotation_sheet.py`로 merged annotation sheet 생성
4. evaluator 또는 LLM-as-judge가 각 row를 `0/1/2` scale로 채점
5. `scripts/summarize_annotations.py`로 aggregate metric과 failure breakdown 생성

annotation sheet에는 아래 정보가 함께 들어간다.

- benchmark row 핵심 context
- model response
- 다섯 rubric dimension 점수
- observed failure labels
- evaluator notes

## 10. next implementation step

- canonical full-v1 model output 수집
- `120`-row run annotation 수행
- metric summary와 qualitative case 생성
- full-v1 comparison report 반영
