# Peer-Reviewed And Conference Literature

- checked_on: `2026-04-10`
- project: `Drug Safety Update Sensitivity Eval`

## 요약

가장 가까운 peer-reviewed 문헌은 `LabelComp`, `AskFDALabel`, 그리고 broader medication safety benchmark 계열이다. 이들은 label comparison, adverse-event extraction, medication-task accuracy에는 강하지만, 업데이트 전후 answer shift benchmark와는 다르다.

## 핵심 문헌

| title | url | venue | publication_date | public_code | public_data | overlap | 판단 |
|---|---|---|---|---|---|---|---|
| `Large language model as clinical decision support system augments medication safety in 16 clinical specialties` | https://pubmed.ncbi.nlm.nih.gov/40997804/ | Cell Reports Medicine | 2025-10-21 | no | no | background | medication safety CDSS 평가이지만 post-market regulatory update answer shift benchmark는 아님 |
| `Performance of large language models in identifying clinically relevant drug-drug interactions and providing pharmacotherapeutic recommendations` | https://pubmed.ncbi.nlm.nih.gov/40189962/ | Frontiers in Drug Safety and Regulation | 2025-03-31 | no | no | background | DDI reasoning 평가이지만 regulatory update response shift는 아님 |
| `Leveraging FDA Labeling Documents and Large Language Model to Enhance Annotation, Profiling, and Classification of Drug Adverse Events with AskFDALabel` | https://pubmed.ncbi.nlm.nih.gov/39979771/ | Drug Safety | 2025-02-20 | yes via GitHub | no | adjacent | label-based AE profiling 및 classification으로 benchmark protocol이 다름 |
| `LabelComp: Detecting and Characterizing Drug Adverse Event Changes in Labeling via Large Language Models` | https://link.springer.com/article/10.1007/s40264-024-01468-8 | Drug Safety | 2024-07-31 | unknown | no | adjacent | label version 차이를 감지하지만 patient-facing answer change를 평가하지는 않음 |

## 문헌별 핵심 메모

### `LabelComp`

- 핵심 강점:
  - label version 차이를 adverse event 중심으로 구조화
  - safety-related change detection이라는 문제 정의 자체는 매우 가깝다
- gap:
  - label-to-label diff detection이지 same-question answer shift benchmark가 아님
  - patient-facing salience나 follow-up guidance는 주된 평가 축이 아니다

### `AskFDALabel`

- 핵심 강점:
  - FDA labeling documents 활용
  - AE profiling, classification, toxicity support
- gap:
  - application/system 성격이 강함
  - new update가 생긴 뒤 답변 posture가 바뀌는지에 대한 benchmark는 아님

### DDI and medication-support studies

- broader medication safety landscape를 보여주는 참고문헌으로는 유익하다
- 그러나 대부분 `knowledge correctness` 또는 `recommendation quality` 중심이다
- temporal regulatory update sensitivity와는 문제 정의가 다르다

## 프로젝트에 주는 시사점

- public paper comparison에서 가장 위험한 overlap은 `LabelComp`다.
- 따라서 README에서 아래 차이를 명시해야 한다.

`LabelComp asks whether label changes can be detected. This benchmark asks whether a model's answer to the same user question changes appropriately after a new FDA safety update is introduced.`
