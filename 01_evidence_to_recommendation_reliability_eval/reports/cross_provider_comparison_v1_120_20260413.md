# Cross-Provider Comparison on Full-v1 (120-row) Benchmark

- checked_on: `2026-04-16`
- project: `Evidence-to-Recommendation Reliability Eval`
- benchmark_slice: `examples_v1_120.csv`
- judge_status: `single primary judge for the scored runs; Sonnet adjudication packet built and still incomplete`

## Why This Report Exists

This file is the detailed companion to `reports/health_reliability_eval_v1.md`.

Its job is to:

- compare the four completed full-v1 runs on the same `120` rows
- surface paired same-set bootstrap deltas
- separate robust effects from descriptive-only differences
- mark Sonnet-specific interpretation as provisional where adjudication is incomplete

## Runs Compared

| run | model | provider | scored rows |
|---|---|---|---:|
| `runs/real_openai_gpt5mini_v1_120_20260413` | `gpt-5-mini` | OpenAI | `120` |
| `runs/real_deepseek_chat_v1_120_20260413` | `deepseek-chat` | DeepSeek | `120` |
| `runs/real_anthropic_haiku45_v1_120_20260413` | `claude-haiku-4-5-20251001` | Anthropic | `120` |
| `runs/real_anthropic_sonnet46_v1_120_20260414` | `claude-sonnet-4-6` | Anthropic | `119` |

## Headline Point Estimates

| metric | gpt-5-mini | deepseek-chat | claude-haiku-4-5 | claude-sonnet-4-6 |
|---|---:|---:|---:|---:|
| `overall_rubric_score` | `1.7633` | `1.59` | `1.675` | `1.6286` |
| `grade_fidelity_accuracy` | `0.8917` | `0.7333` | `0.7833` | `0.8655` |
| `C_grade_preference_omission_rate` | `0.5938` | `0.5938` | `0.4688` | `0.0938` |
| `I_statement_overrecommendation_rate` | `0.0312` | `0.1875` | `0.1875` | `0.125` |
| `unsupported_directive_rate` | `0.0083` | `0.0667` | `0.0583` | `0.0756` |

## Per-run 95% Confidence Intervals

| run | overall | C omission | I overrecommendation | unsupported directive |
|---|---:|---:|---:|---:|
| `gpt-5-mini` | `[1.7067, 1.8133]` | `[0.4062, 0.75]` | `[0.0, 0.0938]` | `[0.0, 0.025]` |
| `deepseek-chat` | `[1.5, 1.675]` | `[0.4375, 0.75]` | `[0.0625, 0.3438]` | `[0.025, 0.1167]` |
| `claude-haiku-4-5` | `[1.595, 1.7483]` | `[0.2812, 0.6258]` | `[0.0625, 0.3438]` | `[0.025, 0.1]` |
| `claude-sonnet-4-6` | `[1.5613, 1.6924]` | `[0.0, 0.2188]` | `[0.0312, 0.25]` | `[0.0336, 0.1261]` |

## Paired Same-set Deltas

Practical-difference thresholds:

- `0.05` for `overall_rubric_score`
- `0.10` for rate metrics

Only differences that clear the threshold **and** whose paired bootstrap CI does not overlap zero should be treated as robust comparative findings.

### GPT-5-mini vs DeepSeek

- `overall_rubric_score`: delta `0.1733`, `95% CI [0.085, 0.26]`
- `grade_fidelity_accuracy`: delta `0.1584`, `95% CI [0.075, 0.2417]`
- `C_grade_preference_omission_rate`: delta `0.0`, `95% CI [-0.2188, 0.2188]`
- `I_statement_overrecommendation_rate`: delta `-0.1563`, `95% CI [-0.2812, -0.0312]`

Interpretation:

- GPT is robustly stronger overall.
- GPT is robustly stronger on directional fidelity.
- GPT is also stronger on `I`-statement calibration.
- There is no evidence of a real separation on `C`-grade preference omission between these two runs.

### GPT-5-mini vs Haiku

- `overall_rubric_score`: delta `0.0883`, `95% CI [0.0, 0.1817]`
- `grade_fidelity_accuracy`: delta `0.1084`, `95% CI [0.025, 0.1917]`
- `C_grade_preference_omission_rate`: delta `0.125`, `95% CI [-0.0938, 0.3438]`
- `I_statement_overrecommendation_rate`: delta `-0.1563`, `95% CI [-0.3125, 0.0]`

Interpretation:

- The cleanest robust separation here is grade fidelity in GPT’s favor.
- The overall and `I`-statement differences lean toward GPT but should be described more cautiously.
- Haiku’s advantage on `C`-grade omission is not cleanly separated from zero at this sample size.

### GPT-5-mini vs Sonnet

- `overall_rubric_score`: delta `0.1327`, `95% CI [0.0521, 0.2134]` when read as GPT minus Sonnet
- `grade_fidelity_accuracy`: delta `0.0253`, `95% CI [-0.0504, 0.1008]`
- `C_grade_preference_omission_rate`: delta `0.5`, `95% CI [0.3125, 0.6875]` when read as GPT minus Sonnet
- `I_statement_overrecommendation_rate`: delta `-0.0938`, `95% CI [-0.25, 0.0312]`
- `unsupported_directive_rate`: delta `-0.0672`, `95% CI [-0.1176, -0.0168]`

Interpretation:

- GPT is robustly stronger on overall rubric score.
- Sonnet is robustly stronger on `C`-grade preference omission.
- GPT appears safer on unsupported directives.
- The `I`-statement gap remains directionally favorable to GPT, but the paired CI still overlaps zero.

### Sonnet vs DeepSeek

- `overall_rubric_score`: delta `0.042`, `95% CI [-0.0655, 0.1496]`
- `grade_fidelity_accuracy`: delta `0.1344`, `95% CI [0.042, 0.2269]`
- `C_grade_preference_omission_rate`: delta `-0.5`, `95% CI [-0.6562, -0.3438]`

Interpretation:

- Sonnet is clearly stronger than DeepSeek on grade fidelity and on the `C`-grade omission slice.
- The overall difference is directionally favorable to Sonnet but not cleanly separated.

### Sonnet vs Haiku

- `overall_rubric_score`: delta `-0.0437`, `95% CI [-0.1328, 0.0471]` when read as Haiku minus Sonnet
- `grade_fidelity_accuracy`: delta `-0.084`, `95% CI [-0.1681, 0.0]` when read as Haiku minus Sonnet
- `C_grade_preference_omission_rate`: delta `0.375`, `95% CI [0.1875, 0.5625]` when read as Haiku minus Sonnet

Interpretation:

- Sonnet is clearly stronger than Haiku on the `C`-grade omission slice.
- The overall ordering between the two is not robustly settled by the current sample.

## Sonnet Interpretation: What Is Provisional

The clean Sonnet story right now is:

- excellent `C`-grade preference omission result
- strong uncertainty-fidelity dimension
- worse overall score than GPT on the current full-v1 release benchmark

The provisional part is the automated `A/D/I preference omission` anomaly.

Current adjudication status:

- packet rows: `53`
- completed rows: `0`
- finalized rows: `0`
- merge status: `incomplete`
- judge sensitivity status: `complete`
- preference-sensitivity exact agreement (`primary` vs `haiku`): `0.0755`
- failure-label exact-match rate (`primary` vs `haiku`): `0.0`
- secondary judge labeled `preference omission` on `4/53` rows and left failure labels blank on `47/53`
- the reviewer-facing disagreement queue now lives in `adjudication/judge_disagreement_brief.md`
- that queue splits into `24 critical` and `29 high` rows, with `preference omission -> <blank>` dominating the transition map

Because that adjudication is not done, this report does **not** treat the Sonnet A/D/I anomaly as a settled model signature.

## Failure-Shape Summary

Current robust takeaways:

- GPT is the strongest overall current result on this frozen benchmark.
- DeepSeek is the weakest overall current result on this frozen benchmark.
- Sonnet materially improves the `C`-grade omission slice without improving every other safety-sensitive metric.
- Haiku sits between GPT/DeepSeek and Sonnet on `C`-grade omission, with weaker grade fidelity than GPT.

Current unsettled questions:

- whether Sonnet’s A/D/I anomaly survives blinded adjudication
- whether the `preference omission` taxonomy should split after adjudication
- how to reconcile the completed second-judge divergence with the blinded human adjudication outcome

## Next Methodological Step

Before any broader model expansion, complete:

1. blinded human adjudication on the `53`-row Sonnet packet
2. interpret the completed `claude-haiku-4-5-20251001` sensitivity result alongside the blinded human merge
3. rubric/taxonomy revision only if the blinded merge shows systematic mismatch
