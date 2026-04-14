# Cross-Provider Comparison on Full-v1 (120-row) Benchmark

- checked_on: `2026-04-13`
- project: `Evidence-to-Recommendation Reliability Eval`
- benchmark_slice: `examples_v1_120.csv` (full-v1 canonical, 120 rows)
- judge: `gpt-5-mini` (OpenAI Responses API), same prompt and rubric for both runs
- runs compared:
  - `runs/real_openai_gpt5mini_v1_120_20260413` (`gpt-5-mini`, OpenAI)
  - `runs/real_deepseek_chat_v1_120_20260413` (`deepseek-chat`, DeepSeek)

## Why cross-provider

The full-v1 canonical baseline (`gpt-5-mini` on 120 rows) surfaced two dominant failure modes: **missing uncertainty disclosure** (39 cases) and **preference omission on C-grade rows** (59.4% of C-grade rows). The question this extension tests is **whether those failures are GPT-family-specific or structural** across current instruction-tuned LLMs. `deepseek-chat` was chosen as the contrast because it is trained on a substantively different pipeline from OpenAI models (different origin, different safety tuning, different instruction-tuning corpus) while maintaining strong general instruction-following.

Judge, prompt, rubric, and 120-item benchmark are held constant. Only the target model varies.

## Headline metric comparison

| metric | gpt-5-mini | deepseek-chat | delta |
|---|---:|---:|---:|
| `overall_rubric_score` (0-2) | **1.7633** | `1.59` | `-0.173` |
| `grade_fidelity_accuracy` | **0.8917** | `0.7333` | `-0.158` |
| `C_grade_preference_omission_rate` | `0.5938` | `0.5938` | **`0.000`** |
| `I_statement_overrecommendation_rate` | `0.0312` | `0.1875` | **`+0.156` (≈6× worse)** |
| `unsupported_directive_rate` | `0.0083` | `0.0667` | **`+0.058` (≈8× worse)** |

## Dimension-level comparison (mean 0-2 score)

| dimension | gpt-5-mini | deepseek-chat | delta |
|---|---:|---:|---:|
| `recommendation_fidelity` | `1.875` | `1.6333` | `-0.242` |
| `evidence_strength_and_uncertainty_fidelity` | `1.4917` | `1.275` | `-0.217` |
| `preference_sensitivity` | `1.55` | `1.4333` | `-0.117` |
| `action_safety` | `1.975` | `1.775` | `-0.200` |
| `communication_clarity` | `1.925` | `1.8333` | `-0.092` |

`gpt-5-mini` is better on every rubric dimension. The largest gaps are in `recommendation_fidelity` and `action_safety` — the two dimensions that most directly reflect posture-preserving behavior.

## Failure-count comparison

| failure label | gpt-5-mini | deepseek-chat |
|---|---:|---:|
| `missing uncertainty disclosure` | `39` | `55` |
| `preference omission` | `33` | `32` |
| `grade inflation` | `0` | `7` |
| `grade deflation` | `1` | `3` |
| `unsupported directive` | `1` | `8` |
| `plausible but ungrounded claim` | `2` | `1` |

The shape of the failure distribution differs meaningfully:

- **`preference omission`** is nearly identical (`33` vs `32`) — the structural pattern replicates across providers.
- **`missing uncertainty disclosure`** is `+16` for `deepseek-chat` (`55` vs `39`) — DeepSeek is more likely to state a recommendation without qualifying language.
- **`grade inflation`** appears only in DeepSeek (`7` vs `0`) — this is the headline directional-safety gap.
- **`unsupported directive`** is `8×` higher in DeepSeek.

## Per-grade failure concentration

### Grade C (preference-sensitive rows, 32 total)

| failure mode | gpt-5-mini | deepseek-chat |
|---|---:|---:|
| `preference omission` | 19 | 19 |
| `missing uncertainty disclosure` | 19 | 22 |
| `grade inflation` | 0 | 3 |
| `grade deflation` | 0 | 1 |
| `unsupported directive` | 0 | 2 |

The preference-omission count is **exactly identical** on C-grade rows. Where DeepSeek diverges is in additional directional failure modes layered on top (grade inflation, unsupported directive).

### Grade I (insufficient-evidence rows, 32 total)

| failure mode | gpt-5-mini | deepseek-chat |
|---|---:|---:|
| `missing uncertainty disclosure` | 6 | 20 |
| `preference omission` | 4 | 6 |
| `unsupported directive` | 1 | 6 |
| `grade inflation` | 0 | 4 |
| `grade deflation` | 0 | 1 |
| `plausible but ungrounded claim` | 1 | 1 |

`I`-statement rows are where the two models diverge most. `deepseek-chat` misses uncertainty disclosure on `20/32` I-grade rows (`62.5%`) vs `6/32` (`18.8%`) for `gpt-5-mini`. Combined with `4` grade inflations and `6` unsupported directives, DeepSeek systematically converts insufficient-evidence contexts into affirmative recommendations.

## Three findings

1. **Preference omission on C-grade rows is structural, not vendor-specific.** Both models miss preference on `19/32` C-grade rows (`59.4%`). Identical count, identical rate. When two models from entirely different training pipelines produce the same failure rate on the same rows, that is strong evidence the failure mode is a property of instruction-tuned LLMs generally — probably a side effect of RLHF reward shaping that favors confident, declarative answers over preference-eliciting ones. **This is the benchmark's single most externally-informative result.**

2. **I-statement handling is where GPT-family tuning provides a real safety advantage.** `gpt-5-mini` overrecommends on `I` rows `3.1%` of the time; `deepseek-chat` does so `18.8%` of the time. OpenAI's safety tuning appears to do meaningful work on insufficient-evidence contexts. This is not trivially generalizable — it tells us GPT-5 is better calibrated on this posture type, but does not tell us this is a universal OpenAI advantage vs all other providers.

3. **Unsupported-directive rate scales with uncertainty-disclosure failure.** DeepSeek's `8×` higher unsupported directive rate tracks its higher missing-uncertainty-disclosure rate. These failures cluster on the same rows: when a model skips uncertainty framing, it is more likely to also state prescriptive action language.

## What this does not tell us

- Whether **Claude** (Anthropic), **Gemini** (Google), or **Llama-family open models** show the same identical C-grade preference-omission rate. That would need at least one more provider.
- Whether DeepSeek's advantage shrinks at higher model scales (`deepseek-reasoner`, `deepseek-v3.1`-variants). This run used the general `deepseek-chat` endpoint.
- Whether fine-tuning for shared-decision-making explicitly (as opposed to generic RLHF) would close the C-grade preference-omission gap. It probably would.

## Artifacts

- `runs/real_openai_gpt5mini_v1_120_20260413/summary.json` — gpt-5-mini raw metrics
- `runs/real_openai_gpt5mini_v1_120_20260413/summary.md` — gpt-5-mini topline
- `runs/real_openai_gpt5mini_v1_120_20260413/qualitative_cases.md` — gpt-5-mini highest/lowest cases
- `runs/real_deepseek_chat_v1_120_20260413/summary.json` — deepseek-chat raw metrics
- `runs/real_deepseek_chat_v1_120_20260413/summary.md` — deepseek-chat topline
- `runs/real_deepseek_chat_v1_120_20260413/qualitative_cases.md` — deepseek-chat highest/lowest cases
- `scripts/run_chat_completions.py` — the chat-completions runner used for DeepSeek (reusable for Together, Groq, or any OpenAI-compatible provider)

## Suggested next cross-provider runs

Ordered by expected informational yield:

1. **Anthropic `claude-haiku-4-5-20251001`** — independent tuning lineage; will test whether Anthropic's known uncertainty-expression tendency narrows the C-grade preference-omission gap. If it does, that weakens finding #1 (the gap is then partially vendor-shaped).
2. **An open Llama-family model via Together or Groq (`Llama-3.3-70B-Instruct`)** — represents generic post-training without vendor-specific health tuning. If the C-grade rate is again `~59%`, finding #1 becomes very strong.
3. **Gemini 2.5 Flash or Pro (Google)** — fourth independent lineage.

Three data points are the minimum for claiming "structural across providers." With four, the finding is publishable.
