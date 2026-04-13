# GitHub Landscape

- checked_on: `2026-04-10`
- project: `Evidence-to-Recommendation Reliability Eval`

## 요약

GitHub에서 직접적으로 겹치는 공개 repo는 많지 않았다. 가장 가까운 것은 `HealthBench` reference implementation과 그 파생 구현들이다. 반대로 `USPSTF grade fidelity` 또는 `patient preference-sensitive recommendation reliability`를 중심에 둔 공개 repo는 찾지 못했다.

## 직접 확인한 repo

| title | url | platform | public_code | public_data | overlap | 판단 |
|---|---|---|---|---|---|---|
| `openai/simple-evals` | https://github.com/openai/simple-evals | GitHub | yes | partial | adjacent | `HealthBench` reference implementation이 있으나 broad health conversation eval이며 권고 등급 충실도 중심은 아님 |
| `m42-health/healthbench` | https://github.com/m42-health/healthbench | GitHub | yes | depends on HF dataset | adjacent | HealthBench stand-alone implementation으로 실행 편의성은 높지만 문제 설정은 여전히 broad |

## 확인 결과가 중요한 이유

- `HealthBench`는 public GitHub와 public HF dataset이 모두 있어서 가장 강한 인접 기준점이다.
- 따라서 이 프로젝트 README에서는 `HealthBench와 무엇이 다른가`를 가장 먼저 설명해야 한다.
- 반대로 GitHub 상에서 `USPSTF current recommendation grade fidelity`를 직접 benchmark한 repo를 찾지 못한 점은 white space 신호다.

## negative scan

아래 범주의 GitHub repo는 `2026-04-10` 검색 시점에 명확한 canonical public repo를 확인하지 못했다.

- `AMEGA`
- `MedGUIDE`
- `From Evidence to Recommendations With Large Language Models`
- `Q2CRBench-3`의 canonical GitHub repo

이 점은 두 가지로 해석해야 한다.

- novelty 측면에서는 유리하다.
- 재현성 비교 기준이 논문 또는 Hugging Face card 중심이 된다는 뜻이므로 README에서 비교 방식을 더 신중하게 써야 한다.

## 프로젝트에 주는 시사점

- GitHub 기준 가장 가까운 비교축은 `HealthBench`다.
- 따라서 우리 쪽 public repo 소개 문장은 아래처럼 잡는 것이 안전하다.

`This benchmark does not ask whether a model is broadly helpful in health conversations. It asks whether a model preserves recommendation strength, uncertainty, and patient-preference sensitivity when translating preventive-care guidance into patient-facing answers.`
