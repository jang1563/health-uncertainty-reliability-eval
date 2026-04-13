# Full V1 Run Status

- checked_on: `2026-04-13`
- run_dir: `runs/real_openai_gpt5mini_v1_120_20260413`
- model: `gpt-5-mini`
- generation_status: `120/120 complete`
- judge_status: `120/120 scored`
- status: **resolved — full-v1 canonical baseline complete**

This document is preserved as a historical record of the initial quota-blocked state and its resolution. The canonical full-v1 results now live in [`health_reliability_eval_v1.md`](health_reliability_eval_v1.md) and the run directory's `summary.md` / `summary.json`.

## Final headline metrics (120/120 scored)

- `overall_rubric_score`: `1.7633`
- `grade_fidelity_accuracy`: `0.8917`
- `C_grade_preference_omission_rate`: `0.5938`
- `I_statement_overrecommendation_rate`: `0.0312`
- `unsupported_directive_rate`: `0.0083`

## Provisional metrics (when only 106/120 were scored)

Retained for reference. Differences with the final values are small (driven by 14 additional rows):

- `overall_rubric_score`: `1.7566`
- `grade_fidelity_accuracy`: `0.8774`
- `C_grade_preference_omission_rate`: `0.6552`
- `I_statement_overrecommendation_rate`: `0.0357`
- `unsupported_directive_rate`: `0.0094`

## Resolution

The 14 rows that were blocked by `OpenAI 429 insufficient_quota` were rejudged after the quota was replenished:

- 12 of 14 rows scored on the first targeted retry (180s timeout).
- 2 rows (`e2r_v1_027`, `e2r_v1_083`) timed out on the first retry and scored cleanly on a second pass with a 360s timeout.
- `finalize_run_dir.py` was re-run to regenerate the final `summary.json`, `summary.md`, and `qualitative_cases.md`.

## Originally missing rows (all now scored)

- `e2r_pilot_019`
- `e2r_v1_027`
- `e2r_v1_058`
- `e2r_v1_065`
- `e2r_v1_066`
- `e2r_v1_075`
- `e2r_v1_082`
- `e2r_v1_083`
- `e2r_v1_086`
- `e2r_v1_089`
- `e2r_v1_099`
- `e2r_v1_101`
- `e2r_v1_110`
- `e2r_v1_111`

## Artifacts

- `runs/real_openai_gpt5mini_v1_120_20260413/outputs.csv`
- `runs/real_openai_gpt5mini_v1_120_20260413/annotation_sheet.csv`
- `runs/real_openai_gpt5mini_v1_120_20260413/summary.json`
- `runs/real_openai_gpt5mini_v1_120_20260413/summary.md`
- `runs/real_openai_gpt5mini_v1_120_20260413/qualitative_cases.md`
- `reports/health_reliability_eval_v1.md` — canonical full-v1 report, now centered on this run
