# GitHub Landscape

- checked_on: `2026-04-10`
- project: `Drug Safety Update Sensitivity Eval`

## 요약

GitHub에서 가장 가까운 공개 repo들은 `AskFDALabel` 계열이다. 이들은 label QA, SPL comparison, adverse event profiling, regulatory review workflow에 강하지만, `after new safety update does the answer change appropriately?`라는 benchmark 질문과는 다르다.

## 직접 확인한 repo

| title | url | platform | public_code | public_data | overlap | 판단 |
|---|---|---|---|---|---|---|
| `seldas/askFDALabel` | https://github.com/seldas/askFDALabel | GitHub | yes | no | adjacent | RAG-based FDA label framework로 benchmark보다 application에 가깝다 |
| `seldas/AskFDALabel-v2` | https://github.com/seldas/AskFDALabel-v2 | GitHub | yes | no | adjacent | label QA와 SPL comparison 중심. update sensitivity benchmark는 아님 |
| `seldas/askFDALabel-Suite` | https://github.com/seldas/askFDALabel-Suite | GitHub | yes | no | adjacent | regulatory reviewer workflow suite이며 evaluation artifact와 문제 정의가 다름 |

## negative scan

`2026-04-10` 기준 명확한 canonical public GitHub repo를 확인하지 못한 것:

- `FDARxBench`
- `Rx-LLM`
- `LabelComp`

이 점은 두 가지 의미가 있다.

- public benchmark repo가 비어 있다는 뜻일 수 있다
- 반대로 논문 중심 비교가 필요하므로 README에서 비교 문장을 더 정교하게 써야 한다

## 프로젝트에 주는 시사점

- GitHub 기준 우리는 application repo와 다르게 보여야 한다.
- public repo 첫 화면은 `search`, `RAG`, `label comparison`이 아니라 `paired update benchmark`를 전면에 두는 것이 맞다.
