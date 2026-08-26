# Evidence-to-Recommendation Reliability Eval

- checked_on: `2026-04-18`
- working_title: `Evidence-to-Recommendation Reliability Eval`
- parent_artifact_family: `Health Uncertainty and Reliability Eval`
- status: `full-v1 canonical run complete on gpt-5-mini (120/120); four-model cross-provider comparison complete on the same 120 rows; Sonnet 4.6 anomaly adjudication packet built (53 rows, merge status incomplete); completed Haiku sensitivity re-judge now shows strong judge dependence on the anomaly slice; release-readiness tooling, PNG figures, and broader tests are included`

## Purpose

This repository is a benchmark artifact for a narrow but important patient-facing reliability question:

- does a model preserve preventive-care recommendation direction (`A/B/C/D/I`)?
- does it preserve uncertainty language honestly?
- does it preserve preference-sensitive framing where the source requires it?

This is **not** a general medical QA benchmark, a recommendation-generation system, or a deployment-ready clinical product. It is a curated stress test for **recommendation-posture fidelity**.

## Canonical Artifacts

Use these in this order:

1. `reports/health_reliability_eval_v1.md`
   - canonical public-facing report for the frozen `120`-row full-v1 benchmark
2. `reports/cross_provider_comparison_v1_120_20260413.md`
   - detailed four-model decomposition and paired-delta interpretation for the same `120` rows
3. `reports/expanded_same_set_public_draft_20260413.md`
   - supporting stress test on the frozen `40`-row same-set slice
4. `reports/expanded_same_set_manuscript_draft_20260413.md`
   - manuscript-style supporting narrative for the same supporting stress test package

The `40`-row package is a **supporting stress test**, not the primary benchmark release. The canonical release substrate is `data/examples_v1_120.csv`.

## Provenance And Positioning

The benchmark is derived from `USPSTF` recommendation statements, with `AHRQ` used primarily for rubric and shared-decision framing support. Rows are paraphrase-first and designed to preserve:

- recommendation strength
- uncertainty disclosure
- preference-sensitive communication

The intended novelty claim is narrow and auditable:

> To our review as of April 2026, we did not find a public benchmark centered on preserving preventive-care recommendation strength, uncertainty, and preference sensitivity in patient-facing model responses.

Closest adjacent work is summarized in `research/06_novelty_gap_and_positioning.md`. The important distinction is that this project targets **patient-facing transmission of evidence posture**, not clinician-facing guideline adherence or recommendation generation.

## Current Benchmark State

### Frozen benchmark substrates

- `data/examples.csv`
  - original `20`-row pilot
- `data/examples_v1_40.csv`
  - frozen same-set supporting stress test
- `data/examples_v1_120.csv`
  - canonical full-v1 benchmark release substrate

### Completed real runs

- `runs/real_openai_gpt5mini_v1_120_20260413`
  - canonical baseline, `120/120` scored
- `runs/real_deepseek_chat_v1_120_20260413`
  - cross-provider extension, `120/120` scored
- `runs/real_anthropic_haiku45_v1_120_20260413`
  - cross-provider extension, `120/120` scored
- `runs/real_anthropic_sonnet46_v1_120_20260414`
  - cross-provider extension, `119/120` scored
- `runs/real_openai_gpt5mini_v1_40_20260412`
  - supporting same-set stress test
- `runs/real_openai_gpt5nano_v1_40_20260412`
  - supporting same-set stress test

### Current headline metrics

Canonical `gpt-5-mini` on `120` rows:

- `overall_rubric_score`: `1.7633`
- `95% CI`: `[1.7067, 1.8133]`
- `grade_fidelity_accuracy`: `0.8917`
- `C_grade_preference_omission_rate`: `0.5938`
- `I_statement_overrecommendation_rate`: `0.0312`
- `unsupported_directive_rate`: `0.0083`

### Sonnet adjudication status

`claude-sonnet-4-6` remains the most methodologically sensitive result in the repo:

- `C_grade_preference_omission_rate`: `0.0938`
- `95% CI`: `[0.0, 0.2188]`
- automated `A/D/I preference omission` counts remain **provisional**
- a blinded adjudication packet is built at `runs/real_anthropic_sonnet46_v1_120_20260414/adjudication/`
- current packet size: `53` rows
- current merge status: `incomplete`
- a dedicated sensitivity-judge workflow is available through `scripts/run_judge_sensitivity.py`
- current sensitivity status: `complete`
- secondary `claude-haiku-4-5-20251001` re-judge exact agreement on `preference_sensitivity`: `0.0755`
- failure-label exact-match rate on the `53`-row packet: `0.0`
- the secondary judge left failure labels blank on `47/53` rows and labeled `preference omission` on only `4/53`
- the disagreement review queue is now staged at `runs/real_anthropic_sonnet46_v1_120_20260414/adjudication/judge_disagreement_brief.md`
- the panel handoff agenda is staged at `runs/real_anthropic_sonnet46_v1_120_20260414/adjudication/expert_panel_agenda.md`
- the packaged role-based handoff lives under `runs/real_anthropic_sonnet46_v1_120_20260414/adjudication/panel_handoff/` when built
- the reviewer queue currently flags `24` rows as `critical` and `29` as `high`
- the dominant failure transition is `preference omission -> <blank>` on `46/53` rows

Taken together, the completed sensitivity pass materially weakens any claim that the automated Sonnet A/D/I anomaly is already a settled model behavior. Human adjudication is now the deciding step.

## Release Workflow

The release-ready path is:

1. initialize a run directory with `scripts/init_run_dir.py`
2. generate model responses into `outputs.csv`
3. build `annotation_sheet.csv` with `scripts/prepare_run_dir.py`
4. score with `scripts/judge_annotations_openai.py`
   - full response text is the default judge path
   - fallback truncation is explicit and recorded in `judge_metadata.json`
5. finalize the run with `scripts/finalize_run_dir.py`
6. if a release-critical anomaly exists, build an adjudication packet with `scripts/build_adjudication_pack.py`
7. run a tracked sensitivity pass with `scripts/run_judge_sensitivity.py`
8. build a reviewer brief with `scripts/build_judge_disagreement_brief.py`
9. package role-specific expert-panel folders with `scripts/build_expert_panel_handoff.py`
10. after raters return, build a chair reconciliation brief with `scripts/build_reconciliation_brief.py`
11. merge blinded human review with `scripts/merge_adjudication.py`
12. render SVG and PNG figures with `scripts/render_run_figures.py`
13. validate the repo state with `scripts/check_release_readiness.py --consistency-only`

Example commands:

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

Use `python scripts/check_release_readiness.py` without `--consistency-only` only when the Sonnet human-review loop is actually complete and you want a strict release gate.

See `docs/red_team_review_20260417.md` for the tracked adversarial workflow review and the follow-up hardening actions.

## Directory Highlights

- `data/`
  - frozen benchmark substrates and blank templates
- `runs/`
  - real run directories, summaries, adjudication artifacts
- `reports/`
  - canonical report plus supporting stress-test drafts
- `figures/`
  - SVG source-of-truth figures plus release PNG companions
- `scripts/`
  - standard-library workflow scripts for build, scoring, adjudication, figures, and release checks
- `tests/`
  - workflow, adjudication, judge, dataset, and release-readiness coverage

## Current Implementation Status

- research landscape and rights memo complete
- frozen `120`-row canonical dataset complete
- frozen `40`-row supporting stress test complete
- four-model cross-provider full-v1 comparison complete
- bootstrap confidence intervals now emitted in run summaries
- paired bootstrap deltas now emitted in run-comparison outputs
- Sonnet adjudication packet, blinded rater sheets, final template, and merge summary scaffold are tracked
- Sonnet sensitivity-sheet preparation and summary workflow are tracked through `scripts/run_judge_sensitivity.py`
- full-response-first judge metadata is supported
- release PNG figures for canonical and cross-provider comparisons are tracked
- the packaged `panel_handoff/` artifact is tracked and now checked for freshness against its source adjudication files
- release-readiness validation script is included
- a tracked adversarial review note now documents resolved workflow hardening findings and the remaining human-review blockers
- unit tests now cover adjudication tooling, judge fallback behavior, dataset build regression, review-target selection, and release-check negative paths

## Immediate Next Steps

1. Complete the blinded `rater_a_sheet.csv`, `rater_b_sheet.csv`, and `final_adjudication_sheet.csv` files for the `53`-row Sonnet packet.
2. Distribute the existing `adjudication/panel_handoff/rater_a/` and `adjudication/panel_handoff/rater_b/` folders separately, and hold back `adjudication/panel_handoff/chair/` until both independent sheets are returned.
3. After the blinded sheets return, rebuild `adjudication/chair_reconciliation_brief.md` to focus the chair-led discussion.
4. Use `adjudication/judge_disagreement_brief.md` and `adjudication/judge_disagreement_rows.csv` to focus the blinded adjudication discussion on `preference_sensitivity` and failure-label semantics.
5. If the blinded merge confirms systematic misuse of `preference omission` on `A/D/I`, revise the rubric and label taxonomy before broad external claims.
6. Only after the adjudicated release candidate is stable should the project add new model lineages such as Llama or Gemini.

## License

This project uses a split license by asset type:

- **Code** (`scripts/`, all `.py` files) — [Apache License 2.0](LICENSE)
- **Data, prompts, rubrics, figures, reports** (`data/`, `prompts/`, `docs/`, `figures/`, `reports/`, `research/`, `runs/`, `.md`/`.csv`/`.jsonl`/`.json`/`.svg`/`.png`) — [CC BY-NC 4.0](LICENSE-DATA)
