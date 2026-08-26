# Health Reliability Eval v1

- checked_on: `2026-04-16`
- project: `Evidence-to-Recommendation Reliability Eval`
- report_status: `release candidate with canonical 120-row benchmark complete, four-model comparison complete, and Sonnet adjudication packet built but not yet completed`

## Report Intent

This is the canonical public report for the current repository state.

- primary benchmark substrate: `data/examples_v1_120.csv`
- canonical baseline: `runs/real_openai_gpt5mini_v1_120_20260413`
- cross-provider comparison: `gpt-5-mini`, `deepseek-chat`, `claude-haiku-4-5-20251001`, `claude-sonnet-4-6`
- supporting stress test only: the frozen `40`-row same-set package in `reports/expanded_same_set_public_draft_20260413.md`

The benchmark evaluates **recommendation-posture fidelity** in patient-facing preventive-care answers. It is not a deployment claim and not a general medical QA benchmark.

## Provenance And Scope

Rows are derived from `USPSTF` recommendation statements, with `AHRQ` used for rubric and shared-decision framing support. The benchmark is designed to measure whether models preserve:

- recommendation direction
- recommendation strength
- uncertainty disclosure
- preference-sensitive framing

The closest neighboring work is summarized in `research/06_novelty_gap_and_positioning.md`. The intended contribution here is narrower: a public stress test for **preventive-care recommendation strength, uncertainty, and preference sensitivity in patient-facing model responses**.

## Canonical Full-v1 Result

- run: `runs/real_openai_gpt5mini_v1_120_20260413`
- model: `gpt-5-mini`
- provider: `OpenAI`
- judge: `gpt-5-mini`
- scored rows: `120/120`

### Headline Metrics

| metric | value | 95% CI |
|---|---:|---:|
| `overall_rubric_score` | `1.7633` | `[1.7067, 1.8133]` |
| `grade_fidelity_accuracy` | `0.8917` | `[0.8333, 0.9417]` |
| `C_grade_preference_omission_rate` | `0.5938` | `[0.4062, 0.75]` |
| `I_statement_overrecommendation_rate` | `0.0312` | `[0.0, 0.0938]` |
| `unsupported_directive_rate` | `0.0083` | `[0.0, 0.025]` |

### Dimension Means

| dimension | mean |
|---|---:|
| `recommendation_fidelity` | `1.875` |
| `evidence_strength_and_uncertainty_fidelity` | `1.4917` |
| `preference_sensitivity` | `1.55` |
| `action_safety` | `1.975` |
| `communication_clarity` | `1.925` |

### Canonical Takeaway

The canonical result is strong on directional fidelity and action safety, but not on posture nuance:

- `unsupported_directive_rate` is low
- overt grade reversal is rare
- the dominant misses are `missing uncertainty disclosure` and `preference omission`
- `C`-grade shared-decision framing remains the single clearest weak surface

This supports the original benchmark hypothesis: modern models often preserve the topic and the rough direction of a recommendation while still flattening the parts of the answer that carry uncertainty or patient preference.

## Cross-Provider Extension

All four models were run on the same `120` rows with the same primary judge prompt and rubric.

| metric | gpt-5-mini | deepseek-chat | claude-haiku-4-5 | claude-sonnet-4-6 |
|---|---:|---:|---:|---:|
| `overall_rubric_score` | `1.7633` | `1.59` | `1.675` | `1.6286` |
| `grade_fidelity_accuracy` | `0.8917` | `0.7333` | `0.7833` | `0.8655` |
| `C_grade_preference_omission_rate` | `0.5938` | `0.5938` | `0.4688` | `0.0938` |
| `I_statement_overrecommendation_rate` | `0.0312` | `0.1875` | `0.1875` | `0.125` |
| `unsupported_directive_rate` | `0.0083` | `0.0667` | `0.0583` | `0.0756` |

### Calibrated Findings

**Finding 1 — GPT-5 remains the strongest overall result on the current frozen benchmark.**

- `gpt-5-mini` vs `deepseek-chat`: overall delta `-0.1733`, `95% CI [-0.26, -0.085]`
- `gpt-5-mini` vs `claude-sonnet-4-6`: overall delta `-0.1327`, `95% CI [-0.2134, -0.0521]`
- `gpt-5-mini` vs `claude-haiku-4-5`: overall delta `-0.0883`, `95% CI [-0.1817, 0.0]`

The GPT lead is clearly supported against DeepSeek and Sonnet on overall rubric score. The GPT-vs-Haiku overall difference is smaller and should be described more cautiously.

**Finding 2 — Sonnet is still the strongest observed model on `C`-grade preference omission, but that result should be read as slice-specific rather than globally “best”.**

- Sonnet vs GPT on `C_grade_preference_omission_rate`: delta `-0.5`, `95% CI [-0.6875, -0.3125]`
- Sonnet vs DeepSeek on the same metric: delta `-0.5`, `95% CI [-0.6562, -0.3438]`
- Sonnet vs Haiku on the same metric: delta `-0.375`, `95% CI [0.1875, 0.5625]` when read as Haiku minus Sonnet

This is the cleanest replicated Sonnet advantage in the current release candidate.

**Finding 3 — GPT’s `I`-statement advantage remains directionally strongest, but not every pairwise difference is cleanly separated at this sample size.**

- GPT vs DeepSeek on `I_statement_overrecommendation_rate`: delta `0.1563`, `95% CI [0.0312, 0.2812]`
- GPT vs Sonnet on the same metric: delta `0.0938`, `95% CI [-0.0312, 0.25]`
- GPT vs Haiku on the same metric: delta `0.1563`, `95% CI [0.0, 0.3125]`

The qualitative story still favors GPT on insufficient-evidence calibration, but the Sonnet gap should not be overstated as a settled separation yet.

**Finding 4 — Sonnet’s A/D/I anomaly remains provisional.**

Automated scoring still assigns Sonnet very high `preference omission` counts on `A/D/I` rows. But:

- the benchmark taxonomy was originally designed around when preference framing is explicitly required
- the same report family now carries a blinded adjudication packet for this anomaly
- current adjudication state is `incomplete`

So the A/D/I Sonnet anomaly should be described as an unresolved adjudication question, not a final model signature.

## Sonnet Adjudication Status

Packet location:

- `runs/real_anthropic_sonnet46_v1_120_20260414/adjudication/`

Current scaffold:

- `adjudication_packet.csv`
- `rater_a_sheet.csv`
- `rater_b_sheet.csv`
- `final_adjudication_sheet.csv`
- `adjudication_merged.csv`
- `agreement_summary.json`
- `judge_sensitivity_sheet.csv`
- `judge_sensitivity_summary.md`
- `../judge_sensitivity.json`
- `judge_disagreement_rows.csv`
- `judge_disagreement_summary.json`
- `judge_disagreement_brief.md`

Current state:

- packet rows: `53`
- completed rows: `0`
- finalized rows: `0`
- status: `incomplete`
- judge sensitivity status: `complete`
- preference-sensitivity exact agreement (`primary` vs `haiku`): `0.0755`
- failure-label exact-match rate (`primary` vs `haiku`): `0.0`
- secondary judge labeled `preference omission` on only `4/53` rows and left failure labels blank on `47/53`
- a reviewer-facing disagreement queue now ranks the same packet for adjudication focus
- reviewer queue buckets: `24 critical`, `29 high`
- dominant failure transition: `preference omission -> <blank>` on `46/53` rows

The completed sensitivity pass does not resolve the Sonnet anomaly in favor of the original automated interpretation. Instead, it sharpens the methodological concern: recommendation direction, uncertainty fidelity, and action safety stay relatively aligned across judges, but `preference_sensitivity` and failure-label assignment diverge sharply on this packet. Until the blinded human sheets are filled and merged, the Sonnet-specific `A/D/I preference omission` interpretation remains provisional.

## Supporting 40-row Same-set Stress Test

The frozen `40`-row comparison between `gpt-5-mini` and `gpt-5-nano` remains useful as a **supporting stress test**, not as the primary release benchmark.

Headline values on that slice:

| run | overall_rubric_score | grade_fidelity_accuracy | C_preference_omission | I_overrecommendation | unsupported_directive |
|---|---:|---:|---:|---:|---:|
| `gpt-5-mini` | `1.805` | `0.85` | `0.125` | `0.125` | `0.025` |
| `gpt-5-nano` | `1.835` | `0.80` | `0.0` | `0.0` | `0.0` |

This slice remains useful because it shows that ordering can flip when the benchmark becomes more concentrated in `C/I` posture-sensitive cases. It should not replace the `120`-row canonical result in release messaging.

## Current Release-Candidate View

The repo now supports a more calibrated claim set than earlier drafts:

- the benchmark cleanly surfaces posture-sensitive failure modes
- GPT currently looks strongest overall on the frozen `120` rows
- Sonnet looks strongest on the `C`-grade omission slice
- the strongest unresolved question is how much of Sonnet’s `A/D/I preference omission` spike is genuine model behavior versus judge/taxonomy artifact

That last question is now explicitly carried as an adjudication task rather than hidden inside prose.

## Outstanding Work

1. Complete the blinded Sonnet adjudication sheets and merge the final dispositions.
2. Use `adjudication/judge_disagreement_brief.md` and `adjudication/judge_disagreement_rows.csv` to focus adjudication on the `preference_sensitivity` rubric and failure-label semantics.
3. If the blinded merge confirms taxonomy misuse, revise `preference omission` before making broader claims.
4. After the adjudicated v1 release candidate is stable, consider new provider lineages such as Llama or Gemini.
