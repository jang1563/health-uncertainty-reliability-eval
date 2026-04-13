# Data

- checked_on: `2026-04-13`
- project: `Evidence-to-Recommendation Reliability Eval`
- status: `pilot plus 40-row same-set slice plus full-v1 120-row scaffold created`

## 목적

이 디렉터리는 benchmark row와 rubric definition을 담는다. 현재는 `20`-row pilot, `40`-row same-set comparison slice, 그리고 `120`-row full-v1 scaffold가 모두 준비된 상태다.

## 파일 설명

- `source_topic_pool.csv`
  - current USPSTF source topic 후보군
  - population slice와 grade를 분리해 적어 두어 이후 example 확장에 바로 사용할 수 있도록 설계
- `source_topic_pool_v1.csv`
  - full v1용 확장 source topic pool
  - `33`개 source-topic slice와 full-v1 grade mix를 담는다
- `examples.csv`
  - frozen 20-row pilot benchmark rows used by the first completed real runs
  - 각 row는 paraphrase-first 원칙을 따른다
- `examples_v1_40.csv`
  - expanded 40-row candidate benchmark set for the next run
  - 기존 20-row pilot을 보존하면서 grade-balanced expansion을 추가한 파일
- `examples_v1_120.csv`
  - full v1 benchmark scaffold
  - `40`-row frozen slice를 보존하면서 `120` rows까지 확장한 canonical next-run dataset
- `rubric_schema.json`
  - expected posture, rubric dimensions, failure taxonomy, scoring scale 정의
- `model_outputs_template.csv`
  - example_id별 response 입력용 템플릿
- `model_outputs_template_v1_40.csv`
  - expanded 40-row candidate set용 response 입력 템플릿
- `model_outputs_template_v1_120.csv`
  - full v1 `120`-row set용 response 입력 템플릿
- `annotations_template.csv`
  - response와 benchmark row를 합친 review/annotation sheet
- `annotations_template_v1_40.csv`
  - expanded 40-row candidate set용 review/annotation sheet
- `annotations_template_v1_120.csv`
  - full v1 `120`-row set용 review/annotation sheet
- `pilot_prompt_pack.jsonl`
  - model run용 JSONL prompt pack
- `examples_v1_40_prompt_pack.jsonl`
  - expanded 40-row candidate set용 JSONL prompt pack
- `examples_v1_120_prompt_pack.jsonl`
  - full v1 `120`-row set용 JSONL prompt pack

## 현재 원칙

- source text를 길게 복사하지 않는다.
- `required_points`와 `forbidden_moves`는 모두 human-authored derived fields다.
- `medlineplus_url`은 현재 pilot 단계에서 비어 있을 수 있다.
- `C`와 `I`는 benchmark center이므로 pilot에서도 반드시 포함한다.

## pilot 범위

- total_examples: `20`
- grade coverage:
  - `A`: 4
  - `B`: 4
  - `C`: 4
  - `D`: 4
  - `I`: 4

## expanded candidate 범위

- total_examples: `40`
- grade coverage:
  - `A`: 8
  - `B`: 8
  - `C`: 8
  - `D`: 8
  - `I`: 8
- `examples.csv`는 reproducibility를 위해 그대로 유지하고, 다음 확장 run은 `examples_v1_40.csv`를 사용한다

## full v1 범위

- total_examples: `120`
- grade coverage:
  - `A`: `16`
  - `B`: `24`
  - `C`: `32`
  - `D`: `16`
  - `I`: `32`
- `source_topic_pool_v1.csv`는 `33` source-topic slice를 담고, slice당 최대 `4` row 원칙을 유지한다
- full-v1 scaffold summary는 `reports/full_v1_dataset_build_20260413.md`에 정리되어 있다

## 이후 확장 방향

- canonical full-v1 real run을 실행
- source-topic slice(`source_topic + population + grade`)당 최대 `4` example 원칙 유지
- MedlinePlus mapping은 public-domain scope가 분명한 topic에 한해 후속 추가
- annotation workflow는 script 기반으로 유지해, later-stage model run 결과를 같은 schema로 누적 가능하게 한다
- model input은 JSONL prompt pack으로도 내보낼 수 있어 later-stage batch run에 바로 연결 가능하다
