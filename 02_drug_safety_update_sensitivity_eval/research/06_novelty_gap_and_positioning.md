# Novelty Gap And Positioning

- checked_on: `2026-04-10`
- project: `Drug Safety Update Sensitivity Eval`

## 한 문장 포지셔닝

이 프로젝트는 `new FDA post-market safety update`가 주어졌을 때 모델 답변이 적절한 방향으로 바뀌는지 평가하는 benchmark다.

## 가장 가까운 겹침과 차이

| neighbor | url | type | overlap | one-line difference |
|---|---|---|---|---|
| `LabelComp` | https://link.springer.com/article/10.1007/s40264-024-01468-8 | peer-reviewed method | adjacent | label change detection이지 same-question answer shift benchmark는 아니다 |
| `AskFDALabel` | https://pubmed.ncbi.nlm.nih.gov/39979771/ | peer-reviewed system | adjacent | label-based AE profiling and QA system이지 update sensitivity benchmark는 아니다 |
| `Rx-LLM` | https://pubmed.ncbi.nlm.nih.gov/41404284/ | preprint benchmark | adjacent | medication-related task suite이지 post-market regulatory update answer shift를 중심 지표로 두지 않는다 |
| `FDARxBench` | https://arxiv.org/abs/2603.19539 | arXiv benchmark | adjacent | FDA label QA and reasoning benchmark로 보이며 paired before/after update protocol이 아니다 |

## 이 프로젝트가 노리는 빈 공간

현재 확인한 범위에서 비어 있는 조합은 아래다.

- FDA post-market safety update
- same user question
- before and after evidence packet
- directionally correct answer shift
- stale reassurance and stale alarmism detection

즉, `drug label을 읽을 수 있는가`가 아니라 `새 규제 업데이트가 등장했을 때 답을 바꿀 수 있는가`가 gap이다.

## README에서 써야 하는 claim

권장 claim:

`To our review as of April 10, 2026, we did not find a public benchmark focused on whether model answers appropriately change after new FDA post-market safety updates.`

## README에서 쓰면 안 되는 claim

- `the first drug safety benchmark`
- `the first FDA benchmark`
- `real-world pharmacovigilance system`
- `regulatory-grade deployment tool`

## 채용 포지셔닝 관점의 장점

- Health AI role에서 중요한 `time-sensitive reliability`를 직접 보여준다.
- static knowledge benchmark보다 더 현실적인 safety framing을 준다.
- 기존 biosecurity / eval portfolio와 자연스럽게 연결되면서도 distinctly health-facing이다.
