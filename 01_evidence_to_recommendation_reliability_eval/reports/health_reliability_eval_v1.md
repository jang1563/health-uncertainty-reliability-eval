# Health Reliability Eval v1

- checked_on: `2026-04-13`
- project: `Evidence-to-Recommendation Reliability Eval`
- report_status: `full-v1 canonical run complete on gpt-5-mini (120/120); cross-provider extension complete on deepseek-chat (120/120, same judge); expanded 40-row same-set comparison retained as stress test`

## Report intent

This document is the working public-facing report for the Evidence-to-Recommendation Reliability Eval. It centers on the canonical **full-v1 run** (`gpt-5-mini` on `examples_v1_120.csv`, 120/120 rows judged) and retains the earlier pilot and expanded same-set runs as methodological context and stability stress tests.

## Benchmark question

Can a model answer preventive-care questions in a way that preserves:

- recommendation direction (A / B / C / D / I)
- evidence strength
- uncertainty disclosure
- patient preference sensitivity

The benchmark targets **recommendation-posture fidelity** — not general medical QA accuracy. It measures whether the model faithfully transmits the evidence posture it has been given, including honest uncertainty on `I statements` and preference-aware framing on `C grades`.

## Current artifact status

- Research landscape complete
- Source-rights memo complete
- Rubric schema drafted and frozen
- Source topic pool drafted (v1)
- Example sets: pilot (20), expanded (40), full-v1 (120)
- Annotation workflow scaffolded
- Demo smoke-test runs complete
- Real model runs completed:
  - `gpt-5-mini` (2026-04-10, 20-row pilot)
  - `gpt-5-nano` (2026-04-10, finalized 2026-04-12, 20-row pilot)
  - `gpt-5-mini` (2026-04-12, 40-row expanded same-set)
  - `gpt-5-nano` (2026-04-12, 40-row expanded same-set)
  - **`gpt-5-mini` (2026-04-13, full-v1 canonical, 120 rows) — headline result**

## Canonical full-v1 result

- run: `runs/real_openai_gpt5mini_v1_120_20260413`
- dataset: `data/examples_v1_120.csv` (120 rows)
- provider: `OpenAI`
- model: `gpt-5-mini`
- judge: `gpt-5-mini` (OpenAI Responses API)
- prompt version: `minimal_patient_facing_system_prompt_v1`
- scored rows: `120/120`

### Headline metrics

| metric | value |
|---|---:|
| `overall_rubric_score` (0-2 scale) | `1.7633` |
| `grade_fidelity_accuracy` | `0.8917` |
| `C_grade_preference_omission_rate` | `0.5938` |
| `I_statement_overrecommendation_rate` | `0.0312` |
| `unsupported_directive_rate` | `0.0083` |

### Average score by rubric dimension (0-2 scale)

| dimension | score |
|---|---:|
| `recommendation_fidelity` | `1.875` |
| `evidence_strength_and_uncertainty_fidelity` | `1.4917` |
| `preference_sensitivity` | `1.55` |
| `action_safety` | `1.975` |
| `communication_clarity` | `1.925` |

### Benchmark composition (full-v1)

| grade | count | | task family | count |
|---|---:|---|---|---:|
| `A` | 16 | | `direct_recommendation` | 36 |
| `B` | 24 | | `expert_explanation` | 48 |
| `C` | 32 | | `preference_sensitive` | 16 |
| `D` | 16 | | `uncertainty_elicitation` | 20 |
| `I` | 32 | | | |

### Observed failure counts (full-v1)

| failure type | count |
|---|---:|
| `missing uncertainty disclosure` | 39 |
| `preference omission` | 33 |
| `plausible but ungrounded claim` | 2 |
| `grade deflation` | 1 |
| `unsupported directive` | 1 |

### Failures by grade

| grade | dominant failure modes |
|---|---|
| `A` | preference omission (1), plausible but ungrounded claim (1) |
| `B` | missing uncertainty disclosure (11), preference omission (8), grade deflation (1) |
| `C` | missing uncertainty disclosure (19), preference omission (19) |
| `D` | missing uncertainty disclosure (3), preference omission (1) |
| `I` | missing uncertainty disclosure (6), preference omission (4), plausible but ungrounded claim (1), unsupported directive (1) |

## Full-v1 takeaway

- **Action safety is high.** `unsupported_directive_rate` is `0.0083` (1/120) and `action_safety` averages `1.975/2.0`. Overtly unsafe directive language is rare.
- **Grade fidelity is strong.** `0.8917` of rows preserve the intended A/B/C/D/I posture. Only 1 grade deflation and 0 grade inflations in the scored set.
- **The core failure surface is posture *flavor*, not posture direction.** The two largest failure modes — `missing uncertainty disclosure` (39) and `preference omission` (33) — are both *omissions of nuance*, not directional errors.
- **`C grade` is the single weakest dimension.** `C_grade_preference_omission_rate` is `0.5938` (19/32 rows). On topics where patient values are load-bearing, the model defaults to a declarative posture over half the time.
- **`I statement` overrecommendation is contained but non-zero.** `I_statement_overrecommendation_rate` is `0.0312` (1/32). The model generally respects evidence insufficiency, with one exception.
- **The `preference_sensitivity` dimension (1.55) and `evidence_strength_and_uncertainty_fidelity` dimension (1.4917) are the lowest-scoring rubric dimensions**, consistent with the failure-count distribution.

## Cross-provider extension (same 120-row benchmark, different target model)

To test whether the canonical failure signature is GPT-family-specific or structural, the 120-row benchmark was re-run against `deepseek-chat` (DeepSeek V3) with the same judge (`gpt-5-mini`), same prompt, and same rubric.

- run: `runs/real_deepseek_chat_v1_120_20260413`
- model: `deepseek-chat` (DeepSeek V3)
- judge: `gpt-5-mini` (OpenAI Responses API)
- scored rows: `120/120`

### Cross-provider headline comparison

| metric | gpt-5-mini | deepseek-chat |
|---|---:|---:|
| `overall_rubric_score` | `1.7633` | `1.59` |
| `grade_fidelity_accuracy` | `0.8917` | `0.7333` |
| `C_grade_preference_omission_rate` | `0.5938` | **`0.5938`** (identical) |
| `I_statement_overrecommendation_rate` | `0.0312` | `0.1875` (≈6× higher) |
| `unsupported_directive_rate` | `0.0083` | `0.0667` (≈8× higher) |

### Cross-provider headline finding

**C-grade preference omission is identical on both models (`19/32` rows = `59.4%`)**, despite `gpt-5-mini` and `deepseek-chat` having entirely different training pipelines. When two models from different providers hit the same rate on the same rows, that is consistent with a structural failure mode of instruction-tuned LLMs on shared-decision-making content, not a GPT-family tuning artifact. This is the most externally-informative result of the cross-provider extension.

DeepSeek is materially worse on `I`-statement handling (`6×` overrecommendation rate) and produces grade inflations (`7` cases) that `gpt-5-mini` does not. The detailed comparison is in [`reports/cross_provider_comparison_v1_120_20260413.md`](cross_provider_comparison_v1_120_20260413.md).

## Expanded 40-row same-set stress test

The canonical result is accompanied by an independent 40-row same-set head-to-head (`examples_v1_40.csv`) between `gpt-5-mini` and `gpt-5-nano`. This slice was annotation-frozen after two adjudication refreshes and a final residual reread.

| run | overall_rubric_score | grade_fidelity_accuracy | C_preference_omission | I_overrecommendation | unsupported_directive |
|---|---:|---:|---:|---:|---:|
| `gpt-5-mini` (40-row) | `1.805` | `0.85` | `0.125` | `0.125` | `0.025` |
| `gpt-5-nano` (40-row) | `1.835` | `0.80` | `0.0` | `0.0` | `0.0` |

Key observations:

- The 40-row slice is *not* a strict subset of the 120-row full-v1, so metric values are not directly comparable row-for-row. It serves as an independent stress test of which model is more stable under the same prompts.
- On the 40-row same-set, `gpt-5-nano` slightly outperformed `gpt-5-mini` on `overall_rubric_score` and was clean on all three safety-sensitive posture metrics (`C_preference_omission`, `I_overrecommendation`, `unsupported_directive` all `0.0`).
- `gpt-5-mini` retained a small edge on `grade_fidelity_accuracy` (0.85 vs 0.80).
- The flip relative to the 20-row pilot survived two adjudication refreshes and a final reread, and `gpt-5-nano`'s advantage is concentrated on the benchmark's posture-sensitive rows (`C` and `I`).

See `reports/expanded_same_set_public_draft_20260413.md` for the manuscript-style narrative and `reports/annotation_freeze_notes_v1_40_20260413.md` for the freeze record.

## Prior pilot (20-row) and smoke-test results

Retained as methodological context. These were useful for establishing rubric discrimination but are superseded by the full-v1 and expanded same-set runs as evaluation evidence.

### Smoke-test discrimination check

| run | overall_rubric_score | grade_fidelity_accuracy | C_preference_omission | I_overrecommendation | unsupported_directive |
|---|---:|---:|---:|---:|---:|
| `demo_handcrafted_reference` | `2.0` | `1.0` | `0.0` | `0.0` | `0.0` |
| `demo_overconfident_baseline` | `1.16` | `0.4` | `1.0` | `1.0` | `0.6` |

The rubric separates a handcrafted reference from an intentionally overconfident baseline on the posture-sensitive metrics. See `reports/demo_smoke_test_runs.md` and `reports/demo_qualitative_cases.md`.

### 20-row pilot real-run snapshot

| run | overall_rubric_score | grade_fidelity_accuracy | C_preference_omission | I_overrecommendation | unsupported_directive |
|---|---:|---:|---:|---:|---:|
| `gpt-5-mini` (20-row pilot) | `1.93` | `0.95` | `0.0` | `0.0` | `0.0` |
| `gpt-5-nano` (20-row pilot) | `1.79` | `0.85` | `0.75` | `0.0` | `0.0` |

On the original 20-row pilot, `gpt-5-mini` led. The flip on the expanded 40-row set is the most informative observation from this progression — which motivated running the full-v1 canonical.

## Observed failure pattern across runs

Across the 20-row pilot, 40-row expanded same-set, and 120-row full-v1 canonical, the dominant failure modes are consistently:

1. **`missing uncertainty disclosure`** — the model states a recommendation without flagging the strength of evidence behind it.
2. **`preference omission`** — on `C grade` and `preference_sensitive` task rows, the model delivers a declarative recommendation rather than framing the decision around patient values.

Directional failures (`grade inflation`, `grade deflation`, `unsupported directive`, `I_statement overrecommendation`) are rare in every run. This is consistent with the benchmark hypothesis that modern production models rarely produce overtly unsafe directives on well-curated preventive-care prompts — but do systematically *flatten nuance* in posture-sensitive contexts.

## First-read takeaway for external readers

The point of this benchmark is **not** to rank models on medical-fact accuracy. It is to ask whether a model, given a well-specified evidence posture, preserves:

- the strength of the recommendation
- the honest disclosure of uncertainty
- the acknowledgment that some decisions depend on patient values

The full-v1 result on `gpt-5-mini` shows high action safety and strong directional fidelity, but a clear and reproducible weakness on **preference-sensitive framing** (`C grade`) and **uncertainty phrasing** (across grades). These are the two dimensions that this benchmark was designed to surface, and the v1 run surfaces them cleanly.

## Outstanding work

1. Add a third provider (Anthropic `claude-haiku-4-5` or `claude-sonnet-4`) to test whether the identical C-grade preference-omission rate survives a third independent training pipeline. With three providers at ~59% C-grade omission, the structural-pattern claim becomes publishable.
2. Add a fourth provider, ideally an open Llama-family model via Together or Groq, to establish whether the pattern survives training pipelines without vendor-specific health safety tuning.
3. Generate publication-ready PNG figures for the full-v1 canonical and cross-provider comparison (metric bars, failure-count breakdown, per-grade heatmap).
4. Consider dual-human adjudication on the 14 rows re-judged after the quota-blocked retry, to confirm no systematic judge drift relative to the first-pass 106.
5. Decide whether to freeze v1 at the current 120-item set or expand to v1.1 (adjacent guideline sources, e.g. AAFP, ACP) before external release.
