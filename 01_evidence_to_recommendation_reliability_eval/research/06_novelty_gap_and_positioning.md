# Novelty Gap And Positioning

- checked_on: `2026-04-10`
- project: `Evidence-to-Recommendation Reliability Eval`

## 한 문장 포지셔닝

이 프로젝트는 `patient-facing preventive-care answers`에서 모델이 `recommendation strength`, `uncertainty`, `preference sensitivity`를 얼마나 보존하는지 평가하는 benchmark다.

## 가장 가까운 겹침과 차이

| neighbor | url | type | overlap | one-line difference |
|---|---|---|---|---|
| `HealthBench` | https://openai.com/index/healthbench/ | broad benchmark | adjacent | broad health conversation benchmark이지 preventive recommendation grade fidelity benchmark는 아니다 |
| `AMEGA` | https://www.nature.com/articles/s41746-024-01356-6 | peer-reviewed benchmark | adjacent | clinician-facing guideline adherence benchmark이지 patient-facing preventive communication benchmark는 아니다 |
| `MedGUIDE` | https://openreview.net/forum?id=Si6BICL2J9 | conference poster benchmark | adjacent | structured diagnostic decision tree adherence 중심이며 `A/B/C/D/I` 권고 semantics를 평가하지 않는다 |
| `From Evidence to Recommendations...` | https://pubmed.ncbi.nlm.nih.gov/40936179/ | peer-reviewed feasibility study | adjacent | structured evidence에서 recommendation을 생성하는 문제이며 patient-facing response reliability와 다르다 |
| `Q2CRBench-3` | https://huggingface.co/datasets/somewordstoolate/Q2CRBench-3 | HF dataset | adjacent | guideline recommendation generation dataset이지 recommendation-strength preservation benchmark는 아니다 |
| `Large Language Models and Communication of Medical Probabilities` | https://pubmed.ncbi.nlm.nih.gov/41405887/ | peer-reviewed diagnostic study | adjacent | 확률 표현 해석이라는 narrower axis를 다루며 preventive recommendation fidelity 전체를 덮지 않는다 |

## 이 프로젝트가 노리는 빈 공간

현재 확인한 범위에서 비어 있는 조합은 아래다.

- preventive-care recommendation
- patient-facing answer
- explicit grade fidelity
- explicit uncertainty fidelity
- explicit preference-sensitive communication

즉, `guideline을 만들 수 있는가`가 아니라 `guideline strength를 왜곡 없이 전달하는가`가 gap이다.

## README에서 써야 하는 claim

권장 claim:

`To our review as of April 10, 2026, we did not find a public benchmark centered on preserving preventive-care recommendation strength, uncertainty, and preference sensitivity in patient-facing model responses.`

## README에서 쓰면 안 되는 claim

- `the first health benchmark`
- `the first benchmark for preventive care`
- `doctor-level recommendation benchmark`
- `clinical deployment-grade`

## 채용 포지셔닝 관점의 장점

- OpenAI Health AI role에 맞는 `evaluation design` 역량을 직접 보여준다.
- medical assistant demo보다 더 안전하고 recruiter-legible하다.
- 기존 `BioEval`, `BioReview`, `BioThreat-Eval`과 결이 맞으면서도 health-native framing이 더 선명하다.
