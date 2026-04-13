# Scope And Research Questions

- checked_on: `2026-04-10`
- project: `Evidence-to-Recommendation Reliability Eval`

## 한 줄 정의

공개 preventive care 근거를 바탕으로, 모델이 `권고 강도`, `근거 불확실성`, `환자 선호 중요성`을 환자-facing 응답에서 얼마나 충실하게 보존하는지 평가하는 benchmark를 설계한다.

## 목표 산출물

- 공개 GitHub repo 초안
- v1 benchmark spec
- public-data and rights memo
- novelty and overlap memo
- 이후 구현 턴에서 바로 dataset과 report를 만들 수 있는 decision-complete research pack

## 핵심 연구 질문

1. 현재 공개 benchmark 중 `recommendation-grade fidelity`를 직접 겨냥한 것이 이미 있는가?
2. `USPSTF + AHRQ + MedlinePlus` 조합이 라이선스와 재현성 측면에서 안전한가?
3. `A/B/C/D/I` 중 어느 등급이 benchmark 차별화에 가장 중요한가?
4. broad health safety eval과 구분되는 최소 novelty claim은 무엇인가?
5. patient-facing 표현을 허용하면서도 clinician-performance overclaim을 피하려면 어떤 rubric wording이 적절한가?

## 범위 포함

- `USPSTF` current recommendation statements
- `USPSTF grade definitions`
- `AHRQ` shared decision-making / SHARE approach
- `MedlinePlus` public-domain health topic summaries and medical test content
- 환자 질문 스타일의 prompts
- 평가 항목으로서의 uncertainty disclosure, preference sensitivity, unsupported directive detection

## 범위 제외

- diagnosis benchmark
- treatment selection benchmark
- EHR agent benchmark
- clinician workflow automation
- direct patient-specific advice generation system
- retrieval system 또는 recommendation-generation pipeline 자체 구현

## 잠근 결정

- artifact type: `benchmark-style evaluation package`
- evaluator focus: `response reliability`, not model fine-tuning
- core source of truth: `USPSTF`
- communication rubric support: `AHRQ`
- patient-friendly surface language support: `MedlinePlus` public-domain subset only
- novelty-safe framing: `We did not find a public benchmark centered on recommendation-grade fidelity and preference-sensitive uncertainty communication in patient-facing preventive-care responses.`

## 아직 구현 시 결정하면 되는 것

- 실제 v1 topic pool의 최종 topic list
- prompt wording의 exact templates
- first canonical model run 대상 모델
- 결과 시각화 방식
