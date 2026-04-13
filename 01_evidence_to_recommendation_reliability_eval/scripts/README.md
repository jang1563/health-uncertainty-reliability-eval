# Scripts

- checked_on: `2026-04-13`
- project: `Evidence-to-Recommendation Reliability Eval`
- dependency_policy: `Python standard library only`

## 목적

이 디렉터리는 pilot evaluation workflow를 최소한의 의존성으로 돌리기 위한 스크립트를 담는다.

## workflow

1. `data/model_outputs_template.csv`를 복사하거나 실제 model output CSV를 준비한다.
2. 필요하면 `export_prompt_pack.py`로 JSONL prompt pack을 만든다.
3. `build_annotation_sheet.py`로 benchmark row와 response를 합친 annotation sheet를 만든다.
4. 사람이 직접 또는 LLM-as-judge로 annotation sheet를 채운다.
5. `summarize_annotations.py`로 metric summary와 markdown report를 만든다.
6. demo 또는 multi-run 비교가 필요하면 `compare_runs.py`, `render_demo_figures.py`, `render_run_figures.py`를 사용한다.
7. same-set 두 annotation sheet에서 human review queue를 뽑고 싶으면 `find_annotation_review_targets.py`를 사용한다.
8. 대표 qualitative case가 필요하면 `extract_case_examples.py`를 사용한다.
9. 새 실제 모델 run을 시작할 때는 `init_run_dir.py`로 run 디렉터리를 만든다.
10. run 디렉터리 기준으로 작업할 때는 `prepare_run_dir.py`와 `finalize_run_dir.py`를 우선 사용한다.
11. OpenAI Responses API를 사용할 때는 `run_openai_responses.py`가 `outputs.csv`를 직접 채운다.
12. OpenAI judge가 필요할 때는 `judge_annotations_openai.py`가 `annotation_sheet.csv`를 직접 채운다.
13. full v1 `120`-row scaffold를 다시 생성하거나 template를 갱신할 때는 `build_full_v1_dataset.py`를 사용한다.
14. dataset 제약 검증이 필요할 때는 `validate_examples_dataset.py`를 사용한다.

## expected response CSV columns

- `example_id`
- `model_name`
- `response_text`

## generated annotation sheet columns

- benchmark context columns
- response columns
- five rubric score columns
- `observed_failures`
- `evaluator_notes`
- `overall_comment`

## commands

```bash
python3 scripts/export_prompt_pack.py \
  --examples data/examples.csv \
  --output data/pilot_prompt_pack.jsonl \
  --system-prompt prompts/minimal_patient_facing_system_prompt.md
```

```bash
python3 scripts/build_annotation_sheet.py \
  --examples data/examples.csv \
  --responses data/model_outputs_template.csv \
  --output data/annotations_template.csv
```

```bash
python3 scripts/summarize_annotations.py \
  --annotations data/annotations_template.csv \
  --summary-json reports/pilot_summary.json \
  --summary-md reports/pilot_summary.md
```

```bash
python3 scripts/compare_runs.py \
  --runs-root runs \
  --output-md reports/demo_smoke_test_runs.md \
  --output-csv reports/demo_smoke_test_runs.csv
```

```bash
python3 scripts/render_demo_figures.py \
  --runs-root runs \
  --figures-dir figures
```

```bash
python3 scripts/render_run_figures.py \
  --runs-root runs \
  --run-name real_run_template_20260410 \
  --run-name real_openai_gpt5nano_20260410 \
  --figures-dir figures \
  --output-prefix real_run \
  --title-prefix "Real Run"
```

```bash
python3 scripts/find_annotation_review_targets.py \
  --left-annotations runs/real_openai_gpt5mini_v1_40_20260412/annotation_sheet.csv \
  --right-annotations runs/real_openai_gpt5nano_v1_40_20260412/annotation_sheet.csv \
  --left-label gpt-5-mini \
  --right-label gpt-5-nano \
  --max-targets 8 \
  --output-md reports/annotation_sanity_check_v1_40_20260412.md \
  --output-csv reports/annotation_sanity_check_v1_40_20260412.csv
```

```bash
python3 scripts/extract_case_examples.py \
  --annotations runs/demo_overconfident_baseline/annotations.csv \
  --output-md reports/demo_qualitative_cases.md
```

```bash
python3 scripts/init_run_dir.py \
  --run-name real_openai_gpt5mini_20260410 \
  --runs-root runs
```

```bash
python3 scripts/init_run_dir.py \
  --run-name real_openai_gpt5mini_v1_40_20260412 \
  --runs-root runs \
  --examples data/examples_v1_40.csv \
  --prompt-pack data/examples_v1_40_prompt_pack.jsonl
```

```bash
python3 scripts/build_full_v1_dataset.py
```

```bash
python3 scripts/validate_examples_dataset.py \
  --examples data/examples_v1_120.csv \
  --expected-total 120 \
  --expected-grade-counts A=16,B=24,C=32,D=16,I=32 \
  --max-per-slice 4
```

```bash
python3 scripts/init_run_dir.py \
  --run-name real_run_v1_120_template_YYYYMMDD \
  --runs-root runs \
  --examples data/examples_v1_120.csv \
  --prompt-pack data/examples_v1_120_prompt_pack.jsonl
```

```bash
python3 scripts/prepare_run_dir.py \
  --run-dir runs/real_openai_gpt5mini_20260410
```

```bash
python3 scripts/finalize_run_dir.py \
  --run-dir runs/real_openai_gpt5mini_20260410
```

```bash
python3 scripts/run_openai_responses.py \
  --run-dir runs/real_openai_gpt5mini_20260410 \
  --model gpt-5-mini
```

```bash
python3 scripts/judge_annotations_openai.py \
  --run-dir runs/real_openai_gpt5mini_20260410 \
  --model gpt-5-mini
```

## note

`annotations_template.csv`는 비어 있는 response에도 생성 가능하다. 다만 meaningful metric은 score가 실제로 채워진 뒤에만 계산된다.

figure script는 현재 SVG를 생성한다. PNG가 필요하면 후속 단계에서 별도 렌더링 파이프라인을 추가하면 된다.

새 실제 run을 만들 때는 `init_run_dir.py`가 `manifest.json`, `outputs.csv`, `notes.md` 자리까지 함께 만든다.

그 다음에는 `prepare_run_dir.py`가 `annotation_sheet.csv`를 만들고, 점수 입력 후 `finalize_run_dir.py`가 `summary.json`, `summary.md`, `qualitative_cases.md`를 만든다.

`run_openai_responses.py`는 `OPENAI_API_KEY`를 읽어 OpenAI Responses API를 호출한다. 현재 환경에 key가 없으면 dry-run 검증만 가능하다.

`init_run_dir.py`는 선택한 `examples`와 `prompt_pack` 경로를 `manifest.json`에 기록한다.
`prepare_run_dir.py`와 `run_openai_responses.py`는 별도 override가 없으면 그 manifest 값을 따라간다.

`judge_annotations_openai.py`는 `prompts/judge_prompt.md`를 system prompt로 사용하고, score/failure/evaluator note를 JSON으로 받아 `annotation_sheet.csv`에 직접 반영한다.

`build_full_v1_dataset.py`는 `examples_v1_40.csv`를 앞부분에 보존하면서, full-v1용 추가 slice와 generated prompt row를 붙여 `examples_v1_120.csv` 및 관련 template/prompt-pack을 만든다.
