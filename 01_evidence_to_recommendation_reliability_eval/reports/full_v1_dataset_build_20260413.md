# Full v1 Dataset Build

- checked_on: `2026-04-13`
- project: `Evidence-to-Recommendation Reliability Eval`
- build_status: `full-v1 dataset scaffold generated and validated`

## Generated artifacts

- `data/source_topic_pool_v1.csv`
- `data/examples_v1_120.csv`
- `data/model_outputs_template_v1_120.csv`
- `data/annotations_template_v1_120.csv`
- `data/examples_v1_120_prompt_pack.jsonl`
- `runs/real_run_v1_120_template_20260413/manifest.json`
- `runs/real_run_v1_120_template_20260413/outputs.csv`
- `runs/real_run_v1_120_template_20260413/annotation_sheet.csv`

## Validation snapshot

- total_examples: `120`
- grade_counts:
  - `A`: `16`
  - `B`: `24`
  - `C`: `32`
  - `D`: `16`
  - `I`: `32`
- task_family_counts:
  - `direct_recommendation`: `36`
  - `expert_explanation`: `48`
  - `preference_sensitive`: `16`
  - `uncertainty_elicitation`: `20`
- source_topic_slice_max: `4`
- source_topic_pool_v1_rows: `33`

## Newly added full-v1 source slices

- `Hypertension in Adults: Screening` / adults `18+` without known hypertension / `A`
- `Human Immunodeficiency Virus (HIV) Infection: Screening` / adolescents and adults `15-65` / `A`
- `Abdominal Aortic Aneurysm: Screening` / men `65-75` who have never smoked / `C`
- `Statin Use for the Primary Prevention of Cardiovascular Disease in Adults: Preventive Medication` / adults `40-75` with risk factors and `7.5%` to `<10%` 10-year CVD risk / `C`
- `Skin Cancer Prevention: Behavioral Counseling` / adults older than `24` with fair skin type / `C`
- `Healthy Diet and Physical Activity for Cardiovascular Disease Prevention in Adults Without Cardiovascular Disease Risk Factors: Behavioral Counseling Interventions` / adults without known CVD risk factors / `C`
- `Statin Use for the Primary Prevention of Cardiovascular Disease in Adults: Preventive Medication` / adults `76+` with no history of CVD / `I`
- `Food Insecurity: Screening` / children, adolescents, and adults in primary care / `I`
- `Depression and Suicide Risk in Adults: Screening` / suicide-risk screening in adults / `I`
- `Impaired Visual Acuity in Older Adults: Screening` / asymptomatic adults `65+` / `I`

## Build notes

- existing `examples_v1_40.csv` rows were preserved at the front of `examples_v1_120.csv`
- full-v1 expansion rows were appended as `e2r_v1_041` through `e2r_v1_120`
- the current `120`-row package should be read as a `full-v1 scaffold ready for canonical runs`, not yet as a completed full-v1 leaderboard
- the first natural next step is a canonical real run on `runs/real_run_v1_120_template_20260413`
