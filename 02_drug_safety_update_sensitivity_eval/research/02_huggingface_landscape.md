# Hugging Face Landscape

- checked_on: `2026-04-10`
- project: `Drug Safety Update Sensitivity Eval`

## 요약

Hugging Face에서 직접적으로 겹치는 canonical dataset은 찾지 못했다. 이 부재 자체가 white space 신호다. 반면 medication benchmark나 paper pages는 존재하지만, `post-market safety update sensitivity`를 전면에 둔 dataset card는 확인하지 못했다.

## 확인 결과

| title | url | platform | public_code | public_data | overlap | 판단 |
|---|---|---|---|---|---|---|
| `FDARxBench` paper mention only | https://arxiv.org/abs/2603.19539 | arXiv, no canonical HF dataset found | unknown | unknown | adjacent | FDA label QA benchmark로 보이며 HF dataset card는 확인하지 못함 |
| `Rx-LLM` paper mention only | https://pubmed.ncbi.nlm.nih.gov/41404284/ | medRxiv/PubMed, no canonical HF dataset found | unknown | unknown | adjacent | medication-related task benchmark이며 update sensitivity dataset은 아님 |

## negative scan

직접 찾지 못한 것:

- Hugging Face dataset for `FDA safety update sensitivity`
- Hugging Face dataset for `SrLC paired before/after benchmark`
- Hugging Face dataset for `stale reassurance after new FDA warning`

## 프로젝트에 주는 시사점

- HF landscape의 공백은 이 프로젝트에 유리하다.
- 추후 public release 시 HF dataset page를 만들면 `GitHub + HF` 조합에서 차별화가 더 강해질 가능성이 높다.
- 다만 v1은 rights와 normalization이 중요하므로 GitHub-first release가 여전히 안전하다.
