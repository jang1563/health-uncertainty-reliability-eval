# Hugging Face Landscape

- checked_on: `2026-04-10`
- project: `Evidence-to-Recommendation Reliability Eval`

## 요약

Hugging Face에서는 `HealthBench`와 `Q2CRBench-3`가 가장 중요한 인접 자산이다. 전자는 health conversation eval, 후자는 guideline recommendation generation 쪽이다. 이 둘 사이에 `patient-facing recommendation-grade fidelity`를 직접 benchmark한 dataset은 확인하지 못했다.

## 직접 확인한 dataset and paper pages

| title | url | platform | public_code | public_data | overlap | 판단 |
|---|---|---|---|---|---|---|
| `openai/healthbench` | https://huggingface.co/datasets/openai/healthbench | Hugging Face Dataset | yes via linked code | yes | adjacent | broad health conversations and physician rubrics 중심. 권고 등급 충실도에 특화되어 있지 않음 |
| `somewordstoolate/Q2CRBench-3` | https://huggingface.co/datasets/somewordstoolate/Q2CRBench-3 | Hugging Face Dataset | partial | yes, with copyright caveats | adjacent | guideline recommendation generation용 근거 자료셋. 환자-facing 응답 reliability benchmark는 아님 |

## 세부 메모

### `openai/healthbench`

- exact_url: `https://huggingface.co/datasets/openai/healthbench`
- checked_on: `2026-04-10`
- public_code: `yes`, OpenAI `simple-evals` reference implementation linked
- public_data: `yes`
- overlap: `adjacent`
- why_not_direct:
  - realistic health conversations를 다루지만 preventive recommendation grade fidelity를 핵심 문제로 두지 않는다
  - category span이 넓어서 `C grade preference-sensitive communication` 같은 좁고 중요한 축을 깊게 파기 어렵다

### `somewordstoolate/Q2CRBench-3`

- exact_url: `https://huggingface.co/datasets/somewordstoolate/Q2CRBench-3`
- checked_on: `2026-04-10`
- public_code: `partial`, dataset card에서 Quicker repository를 참조
- public_data: `yes`, 일부 source data는 copyright 이유로 직접 제공 제한
- overlap: `adjacent`
- why_not_direct:
  - clinical recommendation generation pipeline용 데이터다
  - 우리 프로젝트의 질문은 "evidence로 recommendation을 생성하는가"가 아니라 "권고 강도와 불확실성을 왜곡 없이 전달하는가"다

## negative scan

다음 성격의 HF dataset은 찾지 못했다.

- USPSTF current recommendation grade fidelity benchmark
- patient-facing preventive recommendation uncertainty benchmark
- preference-sensitive communication benchmark tied to `C` and `I` grades

## 프로젝트에 주는 시사점

- HF 기준으로도 `HealthBench`와 `Q2CRBench-3`의 중간 빈 공간을 노리는 전략이 맞다.
- public README에서 novelty 설명은 아래 구조가 가장 안전하다.

1. `HealthBench`와 달리 broad health safety eval이 아님
2. `Q2CRBench-3`와 달리 recommendation generation task가 아님
3. preventive-care recommendation을 patient-facing 답변으로 옮길 때의 `strength preservation`이 핵심임
