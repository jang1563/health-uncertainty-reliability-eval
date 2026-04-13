# arXiv And Preprints

- checked_on: `2026-04-10`
- project: `Drug Safety Update Sensitivity Eval`

## 요약

preprint 층에서는 medication benchmark와 FDA label reasoning 쪽이 빠르게 형성되고 있다. 그러나 `새 regulatory safety update 이후 answer shift`를 직접 benchmark한 preprint는 확인하지 못했다.

## 확인한 preprint and non-journal works

| title | url | venue_or_platform | publication_date | public_code | public_data | overlap | 판단 |
|---|---|---|---|---|---|---|---|
| `FDARxBench: Benchmarking LLMs on FDA Drug Label Reasoning` | https://arxiv.org/abs/2603.19539 | arXiv | 2026-03-20 | unknown | unknown | adjacent | FDA label QA and regulatory reasoning 중심으로 보이며 update sensitivity protocol은 다르다 |
| `Rx-LLM: a benchmarking suite to evaluate safe LLM performance for medication-related tasks` | https://pubmed.ncbi.nlm.nih.gov/41404284/ | medRxiv / PubMed listing | 2025-12-02 | unknown | unknown | adjacent | medication tasks breadth는 넓지만 post-market update change detection은 중심이 아니다 |

## 세부 판단

### `FDARxBench`

- checked_on: `2026-04-10`
- overlap: `adjacent`
- why:
  - FDA label document reasoning은 매우 가깝다
  - 하지만 우리 benchmark는 같은 질문을 `before`와 `after` evidence packet에 대해 다시 물어보고 answer shift를 측정한다는 점에서 구조가 다르다

### `Rx-LLM`

- checked_on: `2026-04-10`
- overlap: `adjacent`
- why:
  - medication-related safety tasks 전반을 다루는 suite
  - 그러나 업데이트된 label state에 따른 directionally correct answer change를 중심 지표로 두지 않는다

## negative scan

직접 찾지 못한 것:

- `FDA Drug Safety Communication response shift benchmark`
- `SrLC paired benchmark`
- `warning removal / risk decrease`까지 포함한 update sensitivity preprint

## 프로젝트에 주는 시사점

- preprint 환경에서도 `generic drug safety`가 아니라 `temporal regulatory update sensitivity`를 전면에 둬야 한다.
- novelty 문장은 `drug safety benchmark`가 아니라 `benchmark for answer change after new FDA safety updates`가 맞다.
