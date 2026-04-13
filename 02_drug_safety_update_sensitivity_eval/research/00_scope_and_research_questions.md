# Scope And Research Questions

- checked_on: `2026-04-10`
- project: `Drug Safety Update Sensitivity Eval`

## 한 줄 정의

모델이 FDA post-market safety update 전후의 regulatory evidence packet을 읽고, 같은 질문에 대해 적절한 방향으로 답변을 수정하는지 평가하는 benchmark를 설계한다.

## 목표 산출물

- 공개 GitHub repo 초안
- v1 update-sensitivity benchmark spec
- public-data and rights memo
- prior work overlap memo
- 이후 구현 턴에서 바로 paired benchmark item을 만들 수 있는 decision-complete research pack

## 핵심 연구 질문

1. 기존 medication benchmark 중 `update sensitivity`를 직접 측정하는 것이 이미 있는가?
2. `FDA Drug Safety Communications + SrLC + openFDA` 조합이 paired benchmark를 만들기에 충분한가?
3. 모델의 hidden knowledge cutoff와 무관하게 benchmark를 설계하려면 어떤 protocol이 필요한가?
4. 업데이트 강화와 업데이트 완화 둘 다 다뤄야 하는가?
5. public repo에서 DailyMed를 어디까지 conservative하게 사용할 것인가?

## 범위 포함

- FDA human prescription `NDA/BLA` products
- `2024-01-01` to `2026-03-31` safety update window
- boxed warning, contraindication, warnings and precautions, adverse reactions, drug interactions, specific populations/patient counseling
- paired `before_packet` / `after_packet`
- stale reassurance, stale alarmism, boxed-warning salience failures

## 범위 제외

- generic drug QA benchmark
- medication recommendation system
- pharmacovigilance signal mining engine
- spontaneous reporting causality model
- DDI extraction benchmark as primary framing
- label diff UI/tool product

## 잠근 결정

- artifact type: `benchmark-style evaluation package`
- core evaluation protocol: same question asked against two curated evidence packets
- novelty-safe framing: `public benchmark for answer change after new FDA safety updates`
- eligibility: `NDA/BLA only in v1`
- DailyMed role: `link-only / identifier-only`

## 아직 구현 시 결정하면 되는 것

- exact drug/event list
- stable control set
- severity tier mapping details
- first canonical model run 대상 모델
