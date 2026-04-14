# Cross-Provider Comparison on Full-v1 (120-row) Benchmark

- checked_on: `2026-04-13`
- project: `Evidence-to-Recommendation Reliability Eval`
- benchmark_slice: `examples_v1_120.csv` (full-v1 canonical, 120 rows)
- judge: `gpt-5-mini` (OpenAI Responses API), same prompt and rubric for all runs
- providers compared (3):
  - `runs/real_openai_gpt5mini_v1_120_20260413` — `gpt-5-mini`, OpenAI
  - `runs/real_deepseek_chat_v1_120_20260413` — `deepseek-chat`, DeepSeek
  - `runs/real_anthropic_haiku45_v1_120_20260413` — `claude-haiku-4-5-20251001`, Anthropic

## Why three providers

The full-v1 canonical (`gpt-5-mini`) surfaced two dominant failure modes: missing uncertainty disclosure (39 cases) and preference omission on C-grade rows (59.4%). The two-provider extension against `deepseek-chat` produced a striking initial finding — identical 59.4% C-grade preference-omission rate on both models, suggesting a structural failure mode independent of training pipeline. Adding a third independent training pipeline (Anthropic) tests whether that "identical rate" finding replicates or is a two-provider coincidence.

Judge model, judge prompt, rubric, and 120 benchmark items are held constant across all three runs. Only the target model varies.

## Three-way headline comparison

| metric | gpt-5-mini | deepseek-chat | claude-haiku-4-5 |
|---|---:|---:|---:|
| `overall_rubric_score` (0-2) | **`1.7633`** | `1.59` | `1.675` |
| `grade_fidelity_accuracy` | **`0.8917`** | `0.7333` | `0.7833` |
| `C_grade_preference_omission_rate` | `0.5938` | `0.5938` | **`0.4688`** |
| `I_statement_overrecommendation_rate` | **`0.0312`** | `0.1875` | `0.1875` |
| `unsupported_directive_rate` | **`0.0083`** | `0.0667` | `0.0583` |

Bold = best value in each row.

## Three-way dimension comparison (mean 0-2)

| dimension | gpt-5-mini | deepseek-chat | claude-haiku-4-5 |
|---|---:|---:|---:|
| `recommendation_fidelity` | **`1.875`** | `1.6333` | `1.7167` |
| `evidence_strength_and_uncertainty_fidelity` | **`1.4917`** | `1.275` | `1.4167` |
| `preference_sensitivity` | `1.55` | `1.4333` | `1.5083` |
| `action_safety` | **`1.975`** | `1.775` | `1.8417` |
| `communication_clarity` | **`1.925`** | `1.8333` | `1.8917` |

`gpt-5-mini` is the best single model on every dimension. `claude-haiku-4-5` sits between `gpt-5-mini` and `deepseek-chat` on most dimensions, with a notable edge over DeepSeek on `evidence_strength_and_uncertainty_fidelity` and `preference_sensitivity`.

## Three-way failure-count comparison

| failure label | gpt-5-mini | deepseek-chat | claude-haiku-4-5 |
|---|---:|---:|---:|
| `missing uncertainty disclosure` | `39` | `55` | `39` |
| `preference omission` | `33` | `32` | `28` |
| `grade inflation` | `0` | `7` | `7` |
| `grade deflation` | `1` | `3` | `4` |
| `unsupported directive` | `1` | `8` | `7` |
| `plausible but ungrounded claim` | `2` | `1` | `0` |

## Per-grade C-row failure comparison

C-grade rows are the benchmark's central preference-sensitive test (32 rows).

| C-grade failure mode | gpt-5-mini | deepseek-chat | claude-haiku-4-5 |
|---|---:|---:|---:|
| `preference omission` | `19` | `19` | `15` |
| `missing uncertainty disclosure` | `19` | `22` | `18` |
| `grade inflation` | `0` | `3` | `1` |
| `grade deflation` | `0` | `1` | `0` |
| `unsupported directive` | `0` | `2` | `1` |

`claude-haiku-4-5` has `4` fewer C-grade preference omissions than the other two (`15/32` vs `19/32`).

## Per-grade I-row failure comparison

I-grade rows test insufficient-evidence posture (32 rows).

| I-grade failure mode | gpt-5-mini | deepseek-chat | claude-haiku-4-5 |
|---|---:|---:|---:|
| `missing uncertainty disclosure` | `6` | `20` | `10` |
| `preference omission` | `4` | `6` | `5` |
| `grade inflation` | `0` | `4` | `5` |
| `unsupported directive` | `1` | `6` | `4` |
| `grade deflation` | `0` | `1` | `0` |
| `plausible but ungrounded claim` | `1` | `1` | `0` |

On I rows, `deepseek-chat` and `claude-haiku-4-5` perform similarly — both overrecommend at `18.75%` vs `gpt-5-mini`'s `3.12%`. Haiku's distribution is shifted (fewer missing-uncertainty-disclosure failures, more grade-inflation failures) but the net safety-relevant rate is the same.

## Four findings from three providers

### Finding 1 — C-grade preference omission is high on every provider, with Anthropic tuning providing a partial mitigation (revised from the two-provider version)

All three models miss preference sensitivity on between `47%` and `59%` of C-grade rows. `gpt-5-mini` and `deepseek-chat` sit at an *identical* `59.4%` (`19/32`), while `claude-haiku-4-5` scores `46.9%` (`15/32`) — a `12.5`-percentage-point improvement.

The two-provider version of this report emphasized the identical `59.4%` rate as evidence of a structural failure mode. With three providers, the finding revises to:

> **Preference omission on shared-decision C-grade rows is a high-frequency failure across every current instruction-tuned model tested (`47-59%`), but the magnitude varies. Anthropic's `claude-haiku-4-5` reduces the rate by about a quarter relative to the `gpt-5-mini`/`deepseek-chat` baseline, suggesting the failure mode is partially addressable through tuning — but even the best of three providers still omits preference on nearly half of preference-sensitive rows.**

The updated interpretation is stronger, not weaker. The original "identical across providers" framing was a two-provider coincidence. The three-provider result shows (a) the failure is clearly not provider-specific — it replicates with similar magnitude across three entirely different training pipelines — and (b) it is partially tractable. `gpt-5-mini` and `deepseek-chat` converging at exactly the same rate is now the anomaly that needs explanation, not a universal truth.

### Finding 2 — GPT-5's I-statement calibration is distinctive, not generic "western safety tuning"

A pre-test hypothesis would have been that any mainstream US-trained safety-tuned model would do better than DeepSeek on insufficient-evidence rows. That hypothesis is falsified by Haiku: `claude-haiku-4-5` has the same `18.75%` I-statement overrecommendation rate as `deepseek-chat`, `6×` worse than `gpt-5-mini`.

The failure *shapes* differ — DeepSeek misses uncertainty disclosure heavily (20/32 I rows), while Haiku shows more grade inflation (5/32 I rows) and unsupported directive (4/32 I rows) — but the bottom-line rate of converting insufficient-evidence contexts into affirmative recommendations is the same. Whatever `gpt-5-mini` does on I rows, neither `claude-haiku-4-5` nor `deepseek-chat` inherits.

This is worth further testing with a larger Claude model (`claude-sonnet-4` or `claude-opus-4`) — the gap may narrow with scale, or it may be specifically related to OpenAI's post-training data for insufficient-evidence contexts.

### Finding 3 — Haiku uniquely over-hedges on Grade A rows

`claude-haiku-4-5` is the only model that produced grade deflations on Grade A rows (`2/16`). `gpt-5-mini` produced zero, `deepseek-chat` produced zero on Grade A. This is a distinctive Haiku failure: on rows where evidence is strongest and the USPSTF-style grade is most unambiguous, Haiku sometimes under-recommends.

This is the mirror of Finding 2. GPT-5 is best-calibrated on insufficient-evidence contexts but not meaningfully safer than Haiku overall. Haiku is best-calibrated on preference sensitivity but over-hedges on strong recommendations. The "right" calibration profile depends on what the benchmark rewards.

### Finding 4 — Unsupported-directive rate still tracks missing-uncertainty rate, but not strictly

Across the three models:

| model | unsupported directive | missing uncertainty |
|---|---:|---:|
| `gpt-5-mini` | `1` | `39` |
| `deepseek-chat` | `8` | `55` |
| `claude-haiku-4-5` | `7` | `39` |

The two-provider extension suggested these cluster on the same rows (one underlying failure mode — posture flattening). The three-provider comparison complicates that: Haiku has the same missing-uncertainty count as `gpt-5-mini` (both `39`) but the unsupported-directive count of DeepSeek-ish range (`7` vs `8`). So the two failure types can decouple. Haiku's unsupported-directive failures concentrate on I-rows (4/7) and preference-sensitive rows, not simply on rows that also lacked uncertainty framing.

## Ranking summary

If the benchmark were to produce a single ranking, the three models order as:

1. **`gpt-5-mini`** — best overall, strongest I-statement calibration, lowest unsupported-directive rate, cleanest action safety.
2. **`claude-haiku-4-5`** — best preference-sensitivity handling, comparable uncertainty fidelity to `gpt-5-mini`, but worse on I-rows and on high-evidence (A-grade) rows.
3. **`deepseek-chat`** — weakest on directional fidelity, uncertainty disclosure, and grade inflation. Matches Haiku on I-statement failures.

But the benchmark is not primarily a ranking tool. The more useful takeaway is that each model has a *different shape of failure*, and the dominant failure mode (preference omission on C) replicates across all three with meaningful frequency.

## What three providers cannot yet settle

- **Whether the Grade A over-hedging is a Haiku-specific quirk or a general Anthropic trait.** A `claude-sonnet-4` run would disambiguate.
- **Whether model scale within Anthropic closes the I-statement gap vs GPT-5-mini.** Again, Sonnet would help.
- **Whether an open Llama-family model without vendor-specific health safety tuning lands near the high end (~59%) or the low end (~47%) of the C-grade preference-omission range.** Adding a Llama run via Together or Groq would indicate whether the Anthropic-vs-GPT gap is vendor-tuning-driven or architecture-driven.

## Artifacts

- `runs/real_openai_gpt5mini_v1_120_20260413/` — full run directory
- `runs/real_deepseek_chat_v1_120_20260413/` — full run directory
- `runs/real_anthropic_haiku45_v1_120_20260413/` — full run directory
- `scripts/run_chat_completions.py` — the chat-completions runner used for both DeepSeek and Anthropic (Anthropic exposes an OpenAI-compatible endpoint at `/v1/chat/completions`; the runner requires no Anthropic-specific code path)

## Suggested next cross-provider runs

Ordered by expected informational yield:

1. **`claude-sonnet-4-20250514`** on the same 120 items. Tests whether the Haiku I-statement gap is scale-sensitive within Anthropic, and whether the Haiku A-grade over-hedging persists at larger scale.
2. **An open Llama-family model (`Llama-3.3-70B-Instruct` via Together or Groq)**. Tests whether a model without vendor-specific health safety post-training lands near `47%` or `59%` on C-grade preference omission.
3. **Gemini 2.5 Flash (Google)**. Fourth independent lineage; useful for confirming the generality of the three-way pattern.
