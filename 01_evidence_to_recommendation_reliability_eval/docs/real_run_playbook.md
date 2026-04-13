# Real Run Playbook

- checked_on: `2026-04-13`
- project: `Evidence-to-Recommendation Reliability Eval`
- audience: `future self or collaborator running the first real model benchmark`

## 목적

이 문서는 실제 외부 모델 run을 시작해서 결과를 benchmark artifact로 남길 때의 최소 작업 순서를 정리한다.

## 빠른 순서

1. 새 run 디렉터리 생성
2. `outputs.csv`에 실제 모델 응답 채우기
3. `annotation_sheet.csv` 생성
4. annotation 수행
5. summary와 qualitative case 생성
6. report에 real run 결과 반영
7. same-set head-to-head면 review queue 생성

## 1. run 디렉터리 생성

```bash
cd 01_evidence_to_recommendation_reliability_eval
python3 scripts/init_run_dir.py \
  --run-name real_PROVIDER_MODEL_YYYYMMDD \
  --runs-root runs
```

확장 benchmark set을 쓰고 싶다면 아래처럼 dataset을 함께 지정한다.

```bash
python3 scripts/init_run_dir.py \
  --run-name real_PROVIDER_MODEL_v1_40_YYYYMMDD \
  --runs-root runs \
  --examples data/examples_v1_40.csv \
  --prompt-pack data/examples_v1_40_prompt_pack.jsonl
```

full v1 `120`-row run을 시작할 때는 아래를 사용한다.

```bash
python3 scripts/init_run_dir.py \
  --run-name real_PROVIDER_MODEL_v1_120_YYYYMMDD \
  --runs-root runs \
  --examples data/examples_v1_120.csv \
  --prompt-pack data/examples_v1_120_prompt_pack.jsonl
```

생성 결과:

- `runs/<run_name>/manifest.json`
- `runs/<run_name>/outputs.csv`
- `runs/<run_name>/notes.md`

## 2. outputs.csv 채우기

필수 컬럼:

- `example_id`
- `model_name`
- `response_text`

원칙:

- row 순서는 바꿔도 되지만 `example_id`는 유지
- 동일 prompt set을 사용
- system prompt 변경 시 `manifest.json`에 기록

OpenAI Responses API를 쓸 경우 아래처럼 바로 채울 수 있다.

```bash
python3 scripts/run_openai_responses.py \
  --run-dir runs/<run_name> \
  --model gpt-5-mini
```

이 스크립트는 아래를 사용한다.

- `OPENAI_API_KEY`
- `manifest.json`의 `prompt_pack_source` 또는 override한 prompt pack
- `runs/<run_name>/outputs.csv`

## 3. annotation sheet 생성

```bash
python3 scripts/prepare_run_dir.py \
  --run-dir runs/<run_name>
```

생성 결과:

- `runs/<run_name>/annotation_sheet.csv`

기본적으로 `manifest.json`의 `examples_source`를 사용한다.
다른 파일을 강제로 쓰고 싶다면 `--examples`로 override할 수 있다.

## 4. annotation 수행

annotation은 아래를 기준으로 한다.

- `docs/annotation_guide.md`
- `prompts/judge_prompt.md`

score는 `0/1/2`만 사용한다.

## 5. summary와 qualitative case 생성

```bash
python3 scripts/finalize_run_dir.py \
  --run-dir runs/<run_name>
```

생성 결과:

- `runs/<run_name>/summary.json`
- `runs/<run_name>/summary.md`
- `runs/<run_name>/qualitative_cases.md`

## 6. report 반영

real run이 생기면 아래 문서를 업데이트한다.

- `reports/health_reliability_eval_v1.md`
- 필요시 `reports/demo_smoke_test_runs.md`는 그대로 두고, real run 전용 comparison report를 추가한다
- 비교 figure가 필요하면 `scripts/render_run_figures.py`로 real run SVG를 생성한다

예시:

```bash
python3 scripts/render_run_figures.py \
  --runs-root runs \
  --run-name real_run_template_20260410 \
  --run-name real_openai_gpt5nano_20260410 \
  --figures-dir figures \
  --output-prefix real_run \
  --title-prefix "Real Run"
```

## 7. same-set sanity-check queue

같은 benchmark set에서 두 run을 직접 비교할 때는 metric table만 보지 말고 review queue도 같이 만든다.

```bash
python3 scripts/find_annotation_review_targets.py \
  --left-annotations runs/<left_run>/annotation_sheet.csv \
  --right-annotations runs/<right_run>/annotation_sheet.csv \
  --left-label <left_model_label> \
  --right-label <right_model_label> \
  --max-targets 8 \
  --output-md reports/<comparison_name>_sanity_check.md \
  --output-csv reports/<comparison_name>_sanity_check.csv
```

우선 manual pass는 아래에 집중한다.

- `grade inflation` 또는 `unsupported directive`가 붙은 row
- `I` row의 large divergence
- `C` row의 preference omission disagreement
- evaluator note에 `truncated`가 반복 등장하는 ambiguous omission case

## 주의

- demo run과 real run을 섞지 않는다.
- real result를 발표할 때는 `manifest.json`의 model/provider 정보를 반드시 채운다.
- `C`와 `I` failure를 qualitative case로 꼭 같이 제시한다.
- full v1 canonical run을 시작하기 전에는 `reports/full_v1_dataset_build_20260413.md`와 `data/source_topic_pool_v1.csv`를 먼저 확인하는 편이 좋다.
