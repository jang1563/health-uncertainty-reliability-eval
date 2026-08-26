# Real Run Playbook

- checked_on: `2026-04-16`
- project: `Evidence-to-Recommendation Reliability Eval`
- audience: `collaborator running or releasing a benchmark run`

## Goal

This document describes the canonical `clone -> run -> judge -> adjudicate -> summarize -> release` path for the current repository state.

## Fast Path

1. initialize a run directory
2. fill `outputs.csv`
3. build `annotation_sheet.csv`
4. score with the judge or a human reviewer
5. finalize the run
6. if needed, build a blinded adjudication packet
7. if needed, build a reviewer disagreement brief
8. render SVG + PNG figures
9. run release readiness checks

## 1. Initialize A Run

```bash
python scripts/init_run_dir.py \
  --run-name real_PROVIDER_MODEL_v1_120_YYYYMMDD \
  --runs-root runs \
  --examples data/examples_v1_120.csv \
  --prompt-pack data/examples_v1_120_prompt_pack.jsonl
```

Generated files:

- `manifest.json`
- `outputs.csv`
- `notes.md`

## 2. Fill `outputs.csv`

Required columns:

- `example_id`
- `model_name`
- `response_text`

You can fill the file manually or use an API runner.

OpenAI Responses example:

```bash
python scripts/run_openai_responses.py \
  --run-dir runs/<run_name> \
  --model gpt-5-mini
```

## 3. Build `annotation_sheet.csv`

```bash
python scripts/prepare_run_dir.py \
  --run-dir runs/<run_name>
```

This uses the run manifest by default.

## 4. Score The Run

Primary judge path:

```bash
python scripts/judge_annotations_openai.py \
  --run-dir runs/<run_name> \
  --model gpt-5-mini
```

Important release-candidate behavior:

- full response text is used first
- fallback truncation is only a recovery path
- `judge_metadata.json` records whether truncation happened

For the tracked sensitivity-judge workflow on an adjudication packet, run:

```bash
python scripts/run_judge_sensitivity.py \
  --run-dir runs/real_anthropic_sonnet46_v1_120_20260414
```

## 5. Finalize The Run

```bash
python scripts/finalize_run_dir.py \
  --run-dir runs/<run_name>
```

Generated files:

- `summary.json`
- `summary.md`
- `qualitative_cases.md`

The current summaries include:

- bootstrap confidence intervals
- provisional flags
- adjudication status
- judge-sensitivity status
- judge-disagreement status

## 6. Build Adjudication Artifacts When Needed

For release-critical anomalies:

```bash
python scripts/build_adjudication_pack.py \
  --run-dir runs/real_anthropic_sonnet46_v1_120_20260414
```

This creates:

- `adjudication_packet.csv`
- `rater_a_sheet.csv`
- `rater_b_sheet.csv`
- `final_adjudication_sheet.csv`

To stage the sensitivity artifacts without making API calls:

```bash
python scripts/run_judge_sensitivity.py \
  --run-dir runs/real_anthropic_sonnet46_v1_120_20260414 \
  --prepare-only
```

That workflow writes:

- `judge_sensitivity_sheet.csv`
- `judge_sensitivity_summary.md`
- `../judge_sensitivity.json`

To turn the completed sensitivity pass into a human-review queue:

```bash
python scripts/build_judge_disagreement_brief.py \
  --run-dir runs/real_anthropic_sonnet46_v1_120_20260414
```

That workflow writes:

- `judge_disagreement_rows.csv`
- `judge_disagreement_summary.json`
- `judge_disagreement_brief.md`

To package the current Sonnet materials for raters and the chair:

```bash
python scripts/build_expert_panel_handoff.py \
  --run-dir runs/real_anthropic_sonnet46_v1_120_20260414
```

That workflow writes:

- `panel_handoff/README.md`
- `panel_handoff/rater_a/`
- `panel_handoff/rater_b/`
- `panel_handoff/chair/`
- `panel_handoff/panel_handoff_manifest.json`

For the current Sonnet packet, the chair-facing session outline is tracked at:

- `runs/real_anthropic_sonnet46_v1_120_20260414/adjudication/expert_panel_agenda.md`

After raters complete their sheets, build the chair queue:

```bash
python scripts/build_reconciliation_brief.py \
  --packet runs/real_anthropic_sonnet46_v1_120_20260414/adjudication/adjudication_packet.csv \
  --rater-a runs/real_anthropic_sonnet46_v1_120_20260414/adjudication/rater_a_sheet.csv \
  --rater-b runs/real_anthropic_sonnet46_v1_120_20260414/adjudication/rater_b_sheet.csv \
  --output-csv runs/real_anthropic_sonnet46_v1_120_20260414/adjudication/chair_reconciliation_queue.csv \
  --summary-json runs/real_anthropic_sonnet46_v1_120_20260414/adjudication/chair_reconciliation_summary.json \
  --summary-md runs/real_anthropic_sonnet46_v1_120_20260414/adjudication/chair_reconciliation_brief.md
```

After raters complete their sheets:

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

## 7. Render Release Figures

Canonical baseline:

```bash
python scripts/render_run_figures.py \
  --runs-root runs \
  --run-name real_openai_gpt5mini_v1_120_20260413 \
  --figures-dir figures \
  --output-prefix full_v1_canonical \
  --title-prefix "Full-v1 Canonical" \
  --require-png
```

Cross-provider comparison:

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

## 8. Release Check

```bash
python scripts/check_release_readiness.py --consistency-only
```

This validates:

- required canonical reports
- required SVG + PNG figures
- adjudication packet artifacts
- reviewer disagreement artifacts when judge sensitivity is complete
- run manifest completeness
- annotation CSV integrity
- absence of stale release-state text

Run the same command without `--consistency-only` only when you want strict release gating and the Sonnet adjudication loop is actually complete.

## Notes

- Do not treat the `40`-row same-set package as the canonical release benchmark. It is a supporting stress test.
- Do not present the Sonnet `A/D/I preference omission` pattern as settled until blinded adjudication is complete.
- Do not mix demo runs into external result narratives.
