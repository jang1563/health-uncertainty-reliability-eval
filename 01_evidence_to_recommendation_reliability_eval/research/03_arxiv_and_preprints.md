# arXiv And Preprints

- checked_on: `2026-04-10`
- project: `Evidence-to-Recommendation Reliability Eval`

## 요약

preprint 층에서도 `clinical decision-making`이나 `guideline adherence` 쪽은 빠르게 쌓이고 있다. 다만 `patient-facing preventive recommendation reliability`를 명시적으로 benchmark한 preprint는 확인하지 못했다.

## 확인한 preprint and non-journal works

| title | url | venue_or_platform | publication_date | public_code | public_data | overlap | 판단 |
|---|---|---|---|---|---|---|---|
| `ClinicBench: Evaluating LLMs as Clinical Decision Makers` | https://doi.org/10.1101/2024.04.24.24306315 | medRxiv | 2024-04-24 | unknown | partial | background | clinical decision-maker benchmark로 폭이 넓고 patient-facing recommendation fidelity와는 거리 있음 |
| `MedGUIDE: Benchmarking Clinical Decision-Making in Large Language Models` | https://openreview.net/forum?id=Si6BICL2J9 | OpenReview, GenAI4Health 2025 Poster | 2025-10-12 | unknown | unknown | adjacent | guideline-consistent diagnostic decision benchmark이며 NCCN decision tree 중심 |

## 세부 판단

### `ClinicBench`

- checked_on: `2026-04-10`
- overlap: `background`
- why:
  - LLM을 clinical decision maker로 보는 넓은 framing
  - preventive recommendation의 등급 보존이나 patient preference sensitivity가 중심이 아님

### `MedGUIDE`

- checked_on: `2026-04-10`
- overlap: `adjacent`
- why:
  - guideline-following이라는 점에서는 가깝다
  - 그러나 multiple-choice diagnostic decision tree benchmark이며 patient-facing communication benchmark가 아니다

## negative scan

직접 찾지 못한 것:

- arXiv에 올라온 `USPSTF grade fidelity benchmark`
- `I statement overrecommendation`을 직접 측정하는 preprint
- `C grade preference omission` 중심 preprint

## 프로젝트에 주는 시사점

- preprint 층에서도 좁은 문제 정의로 차별화해야 한다.
- novelty 문장은 `new preventive-care benchmark`보다 `reliability benchmark for preserving recommendation strength and uncertainty`처럼 더 정교하게 써야 한다.
