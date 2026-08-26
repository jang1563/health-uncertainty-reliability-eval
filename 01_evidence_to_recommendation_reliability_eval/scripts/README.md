# Scripts

- checked_on: `2026-04-16`
- project: `Evidence-to-Recommendation Reliability Eval`
- dependency_policy: `Python standard library only`

## Workflow Overview

The release candidate workflow is:

1. build or select a benchmark slice
2. create a run directory
3. generate `outputs.csv`
4. build `annotation_sheet.csv`
5. judge or annotate
6. summarize and finalize
7. adjudicate release-critical anomalies
8. render release figures
9. run release-readiness checks

## Core Run Scripts

- `build_full_v1_dataset.py`
  - rebuilds the `120`-row canonical dataset and related templates
- `export_prompt_pack.py`
  - exports a JSONL prompt pack from examples CSV rows
- `init_run_dir.py`
  - creates a run directory with `manifest.json`, `outputs.csv`, and `notes.md`
- `prepare_run_dir.py`
  - builds `annotation_sheet.csv` from run metadata
- `run_openai_responses.py`
  - fills `outputs.csv` from the OpenAI Responses API
- `run_chat_completions.py`
  - fills `outputs.csv` through an OpenAI-compatible chat-completions endpoint
- `judge_annotations_openai.py`
  - scores an annotation or adjudication CSV using an OpenAI-compatible judge model
  - full response text is the primary path
  - fallback truncation is explicit and recorded in `judge_metadata.json`
- `finalize_run_dir.py`
  - writes `summary.json`, `summary.md`, and `qualitative_cases.md`

## Adjudication And Comparison Scripts

- `build_adjudication_pack.py`
  - builds the blinded Sonnet anomaly review packet and rater sheets
- `merge_adjudication.py`
  - merges blinded raters plus final adjudication and computes agreement summaries
- `run_judge_sensitivity.py`
  - prepares a blinded sensitivity sheet, runs an OpenAI-compatible sensitivity judge, and writes `judge_sensitivity.json`
- `build_judge_disagreement_brief.py`
  - compares the primary adjudication packet with the sensitivity judge output and writes a ranked reviewer brief
- `build_expert_panel_handoff.py`
  - packages the Sonnet adjudication materials into separate `rater_a`, `rater_b`, and `chair` handoff folders
- `build_reconciliation_brief.py`
  - compares the two blinded rater sheets and writes a chair-facing reconciliation queue
- `summarize_annotations.py`
  - emits run-level metrics, confidence intervals, provisional flags, adjudication status, judge-sensitivity metadata, and judge-disagreement metadata
- `compare_runs.py`
  - compares run summaries and emits paired row-bootstrap deltas for same-set runs
- `find_annotation_review_targets.py`
  - identifies high-priority human reread targets from two same-set annotation sheets
- `extract_case_examples.py`
  - extracts representative qualitative cases from a scored sheet

## Figure And Release Scripts

- `render_demo_figures.py`
  - renders demo comparison SVGs and optional PNGs
- `render_run_figures.py`
  - renders real-run comparison SVGs and release PNG companions
- `check_release_readiness.py`
  - validates canonical links, required artifacts, manifest completeness, adjudication artifacts, packaged `panel_handoff/` freshness, and absence of stale release-state text

## Typical Commands

```bash
python scripts/init_run_dir.py \
  --run-name real_PROVIDER_MODEL_v1_120_YYYYMMDD \
  --runs-root runs \
  --examples data/examples_v1_120.csv \
  --prompt-pack data/examples_v1_120_prompt_pack.jsonl
```

```bash
python scripts/prepare_run_dir.py \
  --run-dir runs/real_PROVIDER_MODEL_v1_120_YYYYMMDD
```

```bash
python scripts/judge_annotations_openai.py \
  --run-dir runs/real_PROVIDER_MODEL_v1_120_YYYYMMDD \
  --model gpt-5-mini
```

```bash
python scripts/build_adjudication_pack.py \
  --run-dir runs/real_anthropic_sonnet46_v1_120_20260414
```

```bash
python scripts/run_judge_sensitivity.py \
  --run-dir runs/real_anthropic_sonnet46_v1_120_20260414 \
  --prepare-only
```

```bash
python scripts/run_judge_sensitivity.py \
  --run-dir runs/real_anthropic_sonnet46_v1_120_20260414
```

```bash
python scripts/build_judge_disagreement_brief.py \
  --run-dir runs/real_anthropic_sonnet46_v1_120_20260414
```

```bash
python scripts/build_expert_panel_handoff.py \
  --run-dir runs/real_anthropic_sonnet46_v1_120_20260414
```

```bash
python scripts/build_reconciliation_brief.py \
  --packet runs/real_anthropic_sonnet46_v1_120_20260414/adjudication/adjudication_packet.csv \
  --rater-a runs/real_anthropic_sonnet46_v1_120_20260414/adjudication/rater_a_sheet.csv \
  --rater-b runs/real_anthropic_sonnet46_v1_120_20260414/adjudication/rater_b_sheet.csv \
  --output-csv runs/real_anthropic_sonnet46_v1_120_20260414/adjudication/chair_reconciliation_queue.csv \
  --summary-json runs/real_anthropic_sonnet46_v1_120_20260414/adjudication/chair_reconciliation_summary.json \
  --summary-md runs/real_anthropic_sonnet46_v1_120_20260414/adjudication/chair_reconciliation_brief.md
```

```bash
python scripts/merge_adjudication.py \
  --packet runs/real_anthropic_sonnet46_v1_120_20260414/adjudication/adjudication_packet.csv \
  --rater-a runs/real_anthropic_sonnet46_v1_120_20260414/adjudication/rater_a_sheet.csv \
  --rater-b runs/real_anthropic_sonnet46_v1_120_20260414/adjudication/rater_b_sheet.csv \
  --final-adjudication runs/real_anthropic_sonnet46_v1_120_20260414/adjudication/final_adjudication_sheet.csv \
  --output-csv runs/real_anthropic_sonnet46_v1_120_20260414/adjudication/adjudication_merged.csv \
  --summary-json runs/real_anthropic_sonnet46_v1_120_20260414/adjudication/agreement_summary.json \
  --summary-md runs/real_anthropic_sonnet46_v1_120_20260414/adjudication/agreement_summary.md
```

```bash
python scripts/render_run_figures.py \
  --runs-root runs \
  --run-name real_openai_gpt5mini_v1_120_20260413 \
  --run-name real_deepseek_chat_v1_120_20260413 \
  --run-name real_anthropic_haiku45_v1_120_20260413 \
  --run-name real_anthropic_sonnet46_v1_120_20260414 \
  --figures-dir figures \
  --output-prefix full_v1_cross_provider \
  --title-prefix "Full-v1 Cross-Provider" \
  --require-png
```

```bash
python scripts/check_release_readiness.py --consistency-only
```

Run `python scripts/check_release_readiness.py` without `--consistency-only` only for a true release-candidate gate after the Sonnet adjudication workflow is complete.

## Notes

- `annotation_sheet.csv` remains the canonical scored table. Adjudication artifacts are separate.
- The reviewer-facing Sonnet disagreement artifacts live beside the adjudication packet as `judge_disagreement_rows.csv`, `judge_disagreement_summary.json`, and `judge_disagreement_brief.md`.
- The optional role-based package lives under `adjudication/panel_handoff/` when built.
- The optional chair reconciliation outputs live beside the packet as `chair_reconciliation_queue.csv`, `chair_reconciliation_summary.json`, and `chair_reconciliation_brief.md`.
- The repo stays script-first on purpose; this release pass does not require a package/module refactor.
- If the blinded Sonnet merge shows systematic label misuse, rubric changes happen after the adjudication packet is completed, not before.
