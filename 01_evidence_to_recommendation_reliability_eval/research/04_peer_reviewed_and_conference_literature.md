# Peer-Reviewed And Conference Literature

- checked_on: `2026-04-10`
- project: `Evidence-to-Recommendation Reliability Eval`

## 요약

가장 가까운 peer-reviewed 문헌은 `AMEGA`, `Benchmarking Large Language Models in Evidence-Based Medicine`, `From Evidence to Recommendations...`, `Streamlining evidence based clinical recommendations with large language models`, `Large Language Models and Communication of Medical Probabilities`다. 이들은 모두 중요한 인접 작업이지만, 각각 broad guideline adherence, EBM pipeline, recommendation generation, probability wording에 더 가깝다.

## 핵심 문헌

| title | url | venue | publication_date | public_code | public_data | overlap | 판단 |
|---|---|---|---|---|---|---|---|
| `Autonomous medical evaluation for guideline adherence of large language models` | https://www.nature.com/articles/s41746-024-01356-6 | npj Digital Medicine | 2024-12-12 | yes mentioned | unknown | adjacent | guideline adherence benchmark이지만 patient-facing preventive recommendation fidelity는 직접 다루지 않음 |
| `Benchmarking Large Language Models in Evidence-Based Medicine` | https://pubmed.ncbi.nlm.nih.gov/39437276/ | IEEE Journal of Biomedical and Health Informatics | 2025-09-01 | unknown | unknown | adjacent | evidence retrieval, synthesis, dissemination 전반을 다루는 EBM pipeline benchmark |
| `From Evidence to Recommendations With Large Language Models: A Feasibility Study` | https://pubmed.ncbi.nlm.nih.gov/40936179/ | Journal of Evidence-Based Medicine | 2025-09-11 | unknown | unknown | adjacent | structured evidence에서 recommendation을 생성하는 feasibility study로 문제 설정이 다름 |
| `Streamlining evidence based clinical recommendations with large language models` | https://pubmed.ncbi.nlm.nih.gov/41423701/ | npj Digital Medicine | 2025-12-22 | partial via HF/Quicker | yes via HF with caveats | adjacent | guideline development acceleration과 recommendation generation 중심 |
| `Large Language Models and Communication of Medical Probabilities` | https://pubmed.ncbi.nlm.nih.gov/41405887/ | JAMA Network Open | 2025-12-01 | no | no | adjacent | verbal probability 해석 오류를 보여주지만 preventive recommendation fidelity benchmark는 아님 |
| `Knowledge-Practice Performance Gap in Clinical Large Language Models: Systematic Review of 39 Benchmarks` | https://pubmed.ncbi.nlm.nih.gov/41325597/ | Journal of Medical Internet Research | 2025-12-09 | no | no | background | 현재 benchmark 지형의 큰 그림을 보여주는 systematic review로 gap framing에 유용 |

## 문헌별 핵심 메모

### `AMEGA`

- 20 scenarios, 13 specialties, open-ended guideline adherence
- gap:
  - clinician-facing
  - diagnosis and treatment planning 중심
  - patient preference-sensitive preventive recommendation 전달과는 다름

### `Benchmarking Large Language Models in Evidence-Based Medicine`

- retrieval, synthesis, dissemination 세 단계 평가
- gap:
  - structured task pipeline 중심
  - recommendation grade fidelity를 직접 평가하지 않음

### `From Evidence to Recommendations...`

- structured evidence를 입력으로 recommendation을 생성
- gap:
  - guideline-development acceleration 맥락
  - 실제 사용자 질문에 대한 safe wording fidelity 문제와 다름

### `Streamlining evidence based clinical recommendations...`

- `Q2CRBench-3`와 연결되는 recommendation generation 작업
- gap:
  - generated recommendation quality가 중심
  - patient-facing answer reliability가 아님

### `Large Language Models and Communication of Medical Probabilities`

- 확률 표현 해석의 불안정성을 보여줘서 매우 유익한 인접 논문
- gap:
  - probability wording에 좁게 집중
  - `A/B/C/D/I` recommendation semantics 전체를 다루지 않음

## 프로젝트에 주는 시사점

- novelty claim은 `first benchmark in health`가 아니라 아래처럼 써야 한다.

`Prior work benchmarks broad health conversations, general guideline adherence, or recommendation generation. This project instead evaluates whether models preserve recommendation strength, uncertainty, and preference sensitivity when translating preventive-care guidance into patient-facing responses.`
