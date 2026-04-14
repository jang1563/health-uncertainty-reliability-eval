# Recommendation-Posture Reliability in Patient-Facing Preventive Care Answers

- checked_on: `2026-04-13`
- artifact_type: `manuscript-style draft`
- benchmark_slice: `examples_v1_40.csv` (primary comparison) plus `examples_v1_120.csv` (full-v1 canonical extension)
- freeze_status: `working frozen after two adjudication refresh passes plus final residual reread; full-v1 canonical gpt-5-mini run complete`
- supporting_artifacts:
  - `reports/expanded_same_set_public_draft_20260413.md`
  - `reports/expanded_same_set_external_brief_20260413.md`
  - `reports/expanded_same_set_results_section_20260413.md`
  - `reports/annotation_freeze_notes_v1_40_20260413.md`
  - `reports/health_reliability_eval_v1.md`
  - `reports/full_v1_run_status_20260413.md`
  - `figures/real_v1_40_metric_comparison.svg`
  - `figures/real_v1_40_failure_count_comparison.svg`
  - `runs/real_openai_gpt5mini_v1_120_20260413/summary.md`

## Abstract

Large language model evaluation in health care often emphasizes factual correctness or broad safety behavior, but many patient-facing failures occur at a narrower layer: the model preserves the topic while distorting recommendation strength, uncertainty, or preference sensitivity. We built a small benchmark slice to stress this failure mode using preventive-care questions derived from `USPSTF + AHRQ` recommendation contexts. The frozen comparison slice contained `40` paraphrased prompts balanced across recommendation grades `A/B/C/D/I` and across task families including direct recommendation, expert explanation, uncertainty elicitation, and preference-sensitive framing. We compared `gpt-5-mini` and `gpt-5-nano` using a five-dimension rubric covering recommendation fidelity, evidence/uncertainty fidelity, preference sensitivity, action safety, and communication clarity.

On this slice, `gpt-5-nano` slightly outperformed `gpt-5-mini` on overall rubric score (`1.835` vs `1.805`) and was cleaner on the benchmark's most safety-sensitive posture metrics: `C`-grade preference omission (`0.0` vs `0.125`), `I`-statement overrecommendation (`0.0` vs `0.125`), and unsupported directive rate (`0.0` vs `0.025`). `gpt-5-mini` retained a small advantage on direct grade fidelity (`0.85` vs `0.80`). The largest split was a single older-adult anxiety-screening `I`-statement row where `gpt-5-mini` converted insufficient evidence into an affirmative recommendation. These results suggest that recommendation-posture fidelity is a distinct evaluation target and that model ordering can change materially when the benchmark emphasizes `C` and `I` recommendation contexts.

## Introduction

Patient-facing health communication is not only about whether a model recognizes the right topic. It is also about whether the model preserves the intended posture of the evidence. Preventive-care recommendations are especially useful for studying this problem because they encode explicit differences between strong recommendation, selective offering, recommend-against guidance, and insufficient-evidence statements.

This project focuses on a narrow reliability question: can a model answer preventive-care questions in a way that preserves recommendation direction, evidence strength, uncertainty disclosure, and patient preference sensitivity? The emphasis is deliberately different from general health QA, clinician-facing guideline adherence, and downstream care planning. The target artifact is a benchmark for patient-facing recommendation-posture reliability.

The distinction matters most for Grade `C` and Grade `I` contexts. A Grade `C` recommendation should not collapse into a default yes; it should preserve selective offering and acknowledge patient values, burdens, and tradeoffs. An `I` statement should not collapse into either a positive recommendation or a de facto recommendation against care; it should preserve that evidence is insufficient. These are plausible places for otherwise fluent models to fail.

## Methods

### Benchmark construction

Examples were derived from currently published `USPSTF` recommendation statements, with `AHRQ` materials used to support rubric and communication framing. Rows were constructed paraphrase-first rather than by copying source language. Each row fixed the target population, recommendation grade, expected posture, required meaning points, and forbidden moves. The expanded comparison slice contained `40` examples, with `8` rows each for grades `A`, `B`, `C`, `D`, and `I`.

The benchmark also spanned four task families:

- `15` direct-recommendation rows
- `9` expert-explanation rows
- `8` preference-sensitive rows
- `8` uncertainty-elicitation rows

This design intentionally oversamples recommendation situations where wording posture matters more than simple topic recall.

### Scoring rubric

Each model response was scored on five dimensions using a `0/1/2` scale:

- `recommendation_fidelity`
- `evidence_strength_and_uncertainty_fidelity`
- `preference_sensitivity`
- `action_safety`
- `communication_clarity`

We also tracked categorical failure labels:

- `grade inflation`
- `grade deflation`
- `missing uncertainty disclosure`
- `preference omission`
- `unsupported directive`
- `plausible but ungrounded claim`

The benchmark's primary aggregate outputs were overall rubric score, grade fidelity accuracy, `C`-grade preference omission rate, `I`-statement overrecommendation rate, and unsupported directive rate.

### Model runs and adjudication workflow

We compared two OpenAI models under the same patient-facing system prompt:

- `gpt-5-mini`
- `gpt-5-nano`

Both runs were completed on the same `40`-row slice and scored on all `40` rows. Initial scoring used the project judge workflow, then targeted rereads were applied to rows most likely to be distorted by truncation or high-impact disagreement. Two official annotation refresh passes were incorporated into the run summaries, and a final reread of the remaining `3` hard cases made no further score changes. The resulting annotation sheets were treated as a working frozen comparison set.

## Results

### Primary comparison

Table 1 summarizes the benchmark's headline metrics for the frozen `40`-row same-set comparison.

| model | overall_rubric_score | grade_fidelity_accuracy | C_preference_omission | I_overrecommendation | unsupported_directive |
|---|---:|---:|---:|---:|---:|
| `gpt-5-mini` | `1.805` | `0.85` | `0.125` | `0.125` | `0.025` |
| `gpt-5-nano` | `1.835` | `0.80` | `0.0` | `0.0` | `0.0` |

The main result is mixed rather than absolute. `gpt-5-nano` performed slightly better on overall rubric score and more clearly on the benchmark's most safety-sensitive posture metrics. `gpt-5-mini` performed slightly better on direct grade fidelity.
Figure 1 provides a compact visual summary of the same comparison and is the most efficient single figure for an external presentation.

### Dimension-level pattern

Table 2 shows the dimension-level averages.

| model | recommendation_fidelity | evidence_uncertainty | preference_sensitivity | action_safety | communication_clarity |
|---|---:|---:|---:|---:|---:|
| `gpt-5-mini` | `1.825` | `1.575` | `1.75` | `1.95` | `1.925` |
| `gpt-5-nano` | `1.800` | `1.575` | `1.875` | `2.000` | `1.925` |

The models were nearly identical on communication clarity and evidence/uncertainty fidelity. The more meaningful separation appeared in preference sensitivity and action safety, where `gpt-5-nano` was more likely to preserve shared-decision framing and less likely to drift into directive language.
Figure 2 complements this by showing failure-count differences rather than only average scores.

### Row-level concentration of disagreement

The single largest split came from `e2r_pilot_020`, an older-adult anxiety-screening prompt tied to an `I` statement. `gpt-5-mini` responded as though screening were affirmatively recommended for adults aged `65+`, whereas `gpt-5-nano` preserved the intended `insufficient evidence` posture. This row produced a `1` vs `10` total-dimension split and was the strongest driver of the final ordering.

After manual refresh passes, no other row differed by more than `2` points. The residual disagreement profile was concentrated in two Grade `C` falls-prevention framing cases, where the remaining question was not factual topic recall but how strongly a selective-offer recommendation should sound.

### Failure pattern

| failure label | gpt-5-mini | gpt-5-nano |
|---|---:|---:|
| `grade deflation` | `1` | `3` |
| `grade inflation` | `2` | `2` |
| `missing uncertainty disclosure` | `8` | `7` |
| `preference omission` | `5` | `5` |
| `unsupported directive` | `1` | `0` |
| `plausible but ungrounded claim` | `0` | `1` |

Both models mostly failed by losing nuance rather than by producing blatantly unsafe blanket advice. The difference was in the shape of that nuance loss. `gpt-5-mini` was more likely to break posture on the hardest `C/I` rows, while `gpt-5-nano` was more likely to exhibit mild grade deflation.

### Box 1. Qualitative stress-test cases

Box 1 highlights two row types that best explain the frozen comparison.

**Case 1: `I`-statement overrecommendation (`e2r_pilot_020`)**

- prompt: `For adults 65 and older is anxiety screening clearly recommended or not?`
- benchmark target: preserve that evidence is insufficient for adults `65+`
- `gpt-5-mini`: opened with an affirmative recommendation for screening adults of all ages, then added caveats
- `gpt-5-nano`: opened with `Not clearly` and explicitly preserved the `insufficient evidence` posture
- interpretation: this row captures the benchmark's central concern that a model can remain fluent while still converting uncertainty into a recommendation

**Case 2: selective-offer drift in Grade `C` counseling (`e2r_pilot_011`)**

- prompt: whether a multifactorial falls-prevention program is something an older adult at increased risk should do
- benchmark target: individualized, preference-sensitive framing that makes the limited net benefit explicit
- both models: included personalization, risk-factor tailoring, and practical burden
- remaining problem: both answers still sounded somewhat too positive, using language closer to `reasonable thing to try` than to a clearly selective-offer Grade `C` posture
- interpretation: this row shows that even when models mention preferences, they may still overshoot the intended recommendation strength

## Full-v1 canonical extension

The `40`-row same-set comparison above was designed as a stress-test slice. To produce a canonical baseline for external comparison, the benchmark was expanded to a `120`-row frozen set (`examples_v1_120.csv`) and run against `gpt-5-mini` with the same judge, prompt, and rubric. The full-v1 set contains `16` Grade `A`, `24` Grade `B`, `32` Grade `C`, `16` Grade `D`, and `32` Grade `I` rows, distributed across the four task families (`direct_recommendation` `36`, `expert_explanation` `48`, `preference_sensitive` `16`, `uncertainty_elicitation` `20`). All `120` rows were judged by `gpt-5-mini` (OpenAI Responses API) using `prompts/judge_prompt.md`.

### Canonical headline metrics (gpt-5-mini on examples_v1_120.csv)

| metric | value |
|---|---:|
| `overall_rubric_score` (0-2) | `1.7633` |
| `grade_fidelity_accuracy` | `0.8917` |
| `C_grade_preference_omission_rate` | `0.5938` |
| `I_statement_overrecommendation_rate` | `0.0312` |
| `unsupported_directive_rate` | `0.0083` |

### Dimension pattern (gpt-5-mini, full-v1)

| dimension | mean (0-2) |
|---|---:|
| `recommendation_fidelity` | `1.875` |
| `evidence_strength_and_uncertainty_fidelity` | `1.4917` |
| `preference_sensitivity` | `1.55` |
| `action_safety` | `1.975` |
| `communication_clarity` | `1.925` |

### Failure pattern (gpt-5-mini, full-v1, 120 rows)

| failure label | count | note |
|---|---:|---|
| `missing uncertainty disclosure` | `39` | concentrated in `B` (11), `C` (19), `I` (6) |
| `preference omission` | `33` | concentrated in `C` (19), `B` (8), `I` (4) |
| `plausible but ungrounded claim` | `2` | one on `A`, one on `I` |
| `grade deflation` | `1` | one `B` row |
| `unsupported directive` | `1` | one `I` row |

### Full-v1 interpretation

The full-v1 canonical confirms and sharpens the `40`-row same-set finding. Action safety is high (`action_safety` mean `1.975`, `unsupported_directive_rate` `0.0083`), and directional grade fidelity is strong (`0.8917`). The benchmark's central concern — preservation of the *flavor* of a recommendation, not just its direction — is where `gpt-5-mini` systematically underperforms:

- `C`-grade preference omission occurs on `19/32` rows (`59.4%`). On topics where patient values are decisive (shared decision-making), the model defaults to a declarative recommendation more often than not.
- `missing uncertainty disclosure` is the single largest failure type at `39` occurrences. It is spread across grades but heaviest in the `B` and `C` bands, i.e. in recommendations that should be preserved *with* qualifying language rather than delivered as flat directives.
- `I`-statement overrecommendation is contained (`1/32`, `3.1%`) — the model usually respects insufficient-evidence contexts.

These results show that the failure signature observed on the `40`-row slice is not an artifact of slice selection: the same two dimensions — `preference_sensitivity` and `evidence_strength_and_uncertainty_fidelity` — score lowest on the larger canonical set, and the same two failure modes dominate the count distribution.

### Why the full-v1 canonical matters

The `40`-row slice is a paired comparison between `gpt-5-mini` and `gpt-5-nano`; the `120`-row set is a larger single-model baseline intended for cross-provider comparison. The two are complementary: the `40`-row slice showed that ordering between similar models within the same family can flip based on how many `C` and `I` rows are preserved; the `120`-row set gives the magnitude of the underlying failure surface at scale, independent of the ordering question. Subsequent model runs (including cross-provider) are intended to be scored against this `120`-row frozen set.

## Cross-provider extension

To test whether the failure signature observed on `gpt-5-mini` is GPT-family-specific or structural, the same `120`-row benchmark was run against `deepseek-chat` (DeepSeek V3). Judge model (`gpt-5-mini`), judge prompt, rubric, and benchmark items are held constant — only the target model varies. `deepseek-chat` was chosen as the contrast because it is trained on a substantially different pipeline (different origin, safety tuning, and instruction corpus from OpenAI) while retaining strong general instruction-following.

### Cross-provider headline comparison

| metric | gpt-5-mini | deepseek-chat | delta |
|---|---:|---:|---:|
| `overall_rubric_score` (0-2) | `1.7633` | `1.59` | `-0.173` |
| `grade_fidelity_accuracy` | `0.8917` | `0.7333` | `-0.158` |
| `C_grade_preference_omission_rate` | `0.5938` | `0.5938` | `0.000` |
| `I_statement_overrecommendation_rate` | `0.0312` | `0.1875` | `+0.156` |
| `unsupported_directive_rate` | `0.0083` | `0.0667` | `+0.058` |

### Cross-provider failure-count comparison

| failure label | gpt-5-mini | deepseek-chat |
|---|---:|---:|
| `missing uncertainty disclosure` | `39` | `55` |
| `preference omission` | `33` | `32` |
| `grade inflation` | `0` | `7` |
| `grade deflation` | `1` | `3` |
| `unsupported directive` | `1` | `8` |
| `plausible but ungrounded claim` | `2` | `1` |

### Three cross-provider findings

**Finding 1 — The C-grade preference-omission pattern replicates exactly.** Both models miss preference on `19/32` C-grade rows (`59.4%`). Identical count, identical rate, on the same 120-row set, with two models from entirely different training pipelines. This is the single most externally-informative result: **preference omission on shared-decision rows is not a GPT-family tuning artifact** — it reproduces under a different pipeline with the same magnitude, which is consistent with a structural property of instruction-tuned LLMs rather than a vendor-specific choice. A plausible mechanism is generic RLHF reward shaping favoring confident declarative answers over preference-eliciting ones, but establishing that requires additional cross-provider data points.

**Finding 2 — I-statement handling is where GPT-family tuning provides a real advantage.** `gpt-5-mini` overrecommends on insufficient-evidence rows `3.1%` of the time; `deepseek-chat` overrecommends `18.8%` of the time (≈`6×` higher). DeepSeek misses uncertainty disclosure on `20/32` I-grade rows (`62.5%`) vs `6/32` (`18.8%`) for `gpt-5-mini`, and adds `4` grade inflations and `6` unsupported directives specifically on I rows. This suggests that the tuning pipeline that produces GPT-5-class behavior does meaningful work on evidence-insufficient contexts — work that a generic strong instruction-tuned model does not inherit automatically. This finding is narrower than Finding 1: it establishes that the difference exists, not that it generalizes to every non-OpenAI provider.

**Finding 3 — Unsupported-directive rate scales with uncertainty-disclosure failure.** DeepSeek's `8×` higher unsupported-directive rate tracks its `+16` higher missing-uncertainty-disclosure count. The two failures cluster on the same rows: when a model skips the uncertainty framing, it is more likely to also produce prescriptive action language. This is consistent with a single underlying failure mode — *posture flattening* — expressing itself as both missing hedges and overconfident directives.

### Generalization caveat

This is a two-provider comparison. Finding 1 is strongest because the identical-rate replication is striking even at n=2, but a third and fourth provider (Anthropic, Google, or an open Llama-family model) would meaningfully upgrade the claim from "consistent with a structural pattern" to "reproducible across four independent training pipelines." Findings 2 and 3 describe a gap between two specific models and should not be read as universal claims about OpenAI vs everyone else.



## Discussion

The first implication is methodological. Recommendation-posture fidelity appears to be a separable benchmark target. A model can remain fluent, plausible, and even superficially "helpful" while still changing the practical meaning of a recommendation. This is especially important in patient-facing settings, where the difference between "recommended," "reasonable depending on preferences," and "evidence is insufficient" is clinically consequential.

The second implication is empirical. The earlier `20`-row pilot favored `gpt-5-mini`, but the frozen `40`-row same-set comparison favored `gpt-5-nano` on the benchmark's central safety-sensitive metrics. This suggests that model ordering is slice-dependent and that benchmark design choices matter. In this project, expanding the slice and preserving more `C` and `I` stress rows changed the ordering.

The third implication concerns evaluation strategy. Generic accuracy or broad health-safety evaluation can miss the failure mode this benchmark is aimed at. The most revealing rows were not the easiest `A/B` rows, but the cases where the model needed to preserve shared decision-making or maintain honest uncertainty. That makes `C` and `I` rows disproportionately useful for model comparison.
The qualitative stress-test patterns in Box 1 illustrate why those rows are so informative: the critical difference is often not whether the answer sounds clinically plausible, but whether it preserves the correct level of recommendation force.

## Limitations

This draft reports a small slice, not a final benchmark leaderboard. A `40`-row frozen comparison is large enough to be informative but still too small to justify broad generalization. The source basis is intentionally narrow, centered on preventive-care recommendation contexts rather than the wider space of patient-facing medical communication.

The benchmark is also intentionally one-turn and text-only. It does not evaluate longitudinal shared decision-making, conversational repair, or real clinical workflow performance. High scores here should not be interpreted as deployment readiness, and low scores should not automatically be interpreted as pure knowledge failure rather than style or instruction-following mismatch.

Finally, the adjudication process is stronger than judge-only scoring but weaker than full dual-human review. The current frozen comparison incorporates targeted human rereads and explicit freeze notes, but a more formal release would benefit from dual-human adjudication on the remaining hard cases and possibly a broader rubric-stability study.

## Conclusion

On a frozen `40`-row preventive-care reliability slice, `gpt-5-nano` was more stable than `gpt-5-mini` on the benchmark's most safety-sensitive recommendation-posture metrics, while `gpt-5-mini` remained slightly better on direct grade fidelity. The most important result is not a universal model ranking. It is that recommendation-posture reliability is measurable, that `C` and `I` rows are the highest-yield stress test, and that model ordering can change once the evaluation slice is designed around those cases.

## Suggested Next Additions

- add a short introduction/discussion bridge if this draft is moved into a full paper
- convert the Table 1 / Table 2 / Figure 1 / Figure 2 / Box 1 placeholders into journal-specific formatting
- run a third model on the same `40`-row slice to test whether the current ordering is provider- or model-family-specific
