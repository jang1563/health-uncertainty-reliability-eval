# Evidence-to-Recommendation Reliability Eval

- checked_on: `2026-04-13`
- working_title: `Evidence-to-Recommendation Reliability Eval`
- parent_artifact_family: `Health Uncertainty and Reliability Eval`
- status: `full-v1 dataset scaffold built; four real runs completed; expanded same-set freeze review recorded`

## Purpose

This package is the research pack for a public benchmark artifact that evaluates how faithfully models preserve **preventive-care recommendation grade**, **uncertainty language**, and **patient-preference sensitivity** in patient-facing answers.

The central question is **not** "does the model match the guideline?" The more important questions are:

- Does the model exaggerate or weaken the strength of `A/B/C/D/I` recommendations?
- On `I statement` topics, does the model honestly convey that evidence is insufficient?
- On `C grade` topics — where patient values and tradeoffs are decisive — does the model invite or acknowledge patient preference?
- Even when using patient-friendly language, does the model avoid distorting the underlying evidence strength?

## Why this track

Most public health benchmarks focus on one of two things:

- broad health-conversation safety
- clinician-facing guideline adherence

This project targets the gap between those:

- `recommendation-grade fidelity`
- `uncertainty disclosure fidelity`
- `preference-sensitive communication`

That is, this is **not** a `recommendation generation system` and **not** a `clinical workflow agent`. It measures how honestly a model transmits public evidence in a patient-facing answer.

## Directory layout

- `data/README.md`
- `data/source_topic_pool.csv`
- `data/source_topic_pool_v1.csv`
- `data/examples.csv`
- `data/examples_v1_40.csv`
- `data/examples_v1_120.csv`
- `data/rubric_schema.json`
- `data/model_outputs_template.csv`
- `data/model_outputs_template_v1_40.csv`
- `data/model_outputs_template_v1_120.csv`
- `data/annotations_template.csv`
- `data/annotations_template_v1_40.csv`
- `data/annotations_template_v1_120.csv`
- `data/pilot_prompt_pack.jsonl`
- `data/examples_v1_40_prompt_pack.jsonl`
- `data/examples_v1_120_prompt_pack.jsonl`
- `docs/methodology.md`
- `docs/limitations.md`
- `docs/annotation_guide.md`
- `docs/real_run_playbook.md`
- `prompts/judge_prompt.md`
- `prompts/minimal_patient_facing_system_prompt.md`
- `runs/README.md`
- `runs/run_manifest_template.json`
- `scripts/README.md`
- `scripts/build_annotation_sheet.py`
- `scripts/compare_runs.py`
- `scripts/build_full_v1_dataset.py`
- `scripts/export_prompt_pack.py`
- `scripts/find_annotation_review_targets.py`
- `scripts/extract_case_examples.py`
- `scripts/finalize_run_dir.py`
- `scripts/init_run_dir.py`
- `scripts/judge_annotations_openai.py`
- `scripts/prepare_run_dir.py`
- `scripts/run_openai_responses.py`
- `scripts/render_demo_figures.py`
- `scripts/render_run_figures.py`
- `scripts/seed_demo_runs.py`
- `scripts/summarize_annotations.py`
- `scripts/validate_examples_dataset.py`
- `reports/health_reliability_eval_v1.md`
- `reports/expanded_same_set_public_draft_20260413.md`
- `reports/expanded_same_set_external_brief_20260413.md`
- `reports/expanded_same_set_results_section_20260413.md`
- `reports/expanded_same_set_manuscript_draft_20260413.md`
- `reports/expanded_same_set_figure_legends_20260413.md`
- `reports/demo_qualitative_cases.md`
- `reports/demo_smoke_test_runs.md`
- `reports/real_run_comparison_20260412.md`
- `reports/real_run_comparison_20260412.csv`
- `reports/real_run_comparison_v1_40_20260412.md`
- `reports/real_run_comparison_v1_40_20260412.csv`
- `reports/annotation_sanity_check_v1_40_20260412.md`
- `reports/annotation_sanity_check_v1_40_20260412.csv`
- `reports/annotation_second_pass_notes_v1_40_20260412.md`
- `reports/annotation_freeze_notes_v1_40_20260413.md`
- `reports/full_v1_dataset_build_20260413.md`
- `figures/README.md`
- `research/00_scope_and_research_questions.md`
- `research/01_github_landscape.md`
- `research/02_huggingface_landscape.md`
- `research/03_arxiv_and_preprints.md`
- `research/04_peer_reviewed_and_conference_literature.md`
- `research/05_public_data_sources_and_usage_rights.md`
- `research/06_novelty_gap_and_positioning.md`
- `research/07_v1_dataset_and_rubric_spec.md`
- `research/08_execution_plan.md`

## Source policy (summary)

- `USPSTF`: paraphrase-first, short-quote-only when necessary, source URL required.
- `AHRQ`: used primarily for rubric derivation; verbatim redistribution minimized.
- `MedlinePlus`: only the explicitly public-domain health-topic summaries and medical-test information are used.

## Current conclusion

- The track is worth pursuing.
- The closest adjacent works are `HealthBench`, `AMEGA`, `MedGUIDE`, *From Evidence to Recommendations...*, and `Q2CRBench-3`.
- Those, however, sit closer to `broad conversation`, `guideline adherence`, or `recommendation generation` respectively, and are distinct from this project's core target: a `grade-preserving patient-facing reliability eval`.

## Current implementation status

- Research pack is complete.
- Pilot dataset scaffold is built.
- A `20`-item pilot draft is written and covers all of the `A/B/C/D/I` grades.
- A `40`-item expanded candidate set is added and ready for the next run.
- A `120`-item full-v1 scaffold is built and ready for the canonical full-v1 run.
- Annotation workflow scaffold is built.
- Prompt-pack export workflow is built.
- Smoke-test demo-run workflow is built.
- Multi-run comparison reporting and demo SVG figure workflow are built.
- Real-run comparison reporting and real-run SVG figure workflow are built.
- Real-run initialization and qualitative-case extraction workflow are built.
- Run-centric `prepare`/`finalize` workflow is built.
- A run script for the OpenAI Responses API is included.
- An OpenAI judge script is included.
- `runs/demo_handcrafted_reference` and `runs/demo_overconfident_baseline` are already seeded.
- `runs/real_run_template_20260410` and `runs/real_openai_gpt5nano_20260410` are already populated.
- `runs/real_openai_gpt5nano_v1_40_20260412` has been generated and scored against the expanded 40-row candidate set.
- `runs/real_openai_gpt5mini_v1_40_20260412` has also been generated and scored on the same-set.
- `runs/real_run_v1_120_template_20260413` is initialized as the full-v1 canonical run template.
- The `response -> annotation sheet -> summary report` pipeline has scripts and templates included.
- Four real model runs are complete.
- The `gpt-5-mini` vs `gpt-5-nano` same-set head-to-head on the expanded candidate set is complete.
- An annotation sanity-check queue has been produced for the expanded same-set results.
- The residual 3-row sanity-check queue is finished through final reread; the current official annotation sheet is treated as the working frozen version.
- The full-v1 dataset build summary is in `reports/full_v1_dataset_build_20260413.md`.
- A publication-style draft of the frozen 40-row same-set results is in `reports/expanded_same_set_public_draft_20260413.md`.
- Shorter external brief and manuscript-style results-section drafts are in `reports/expanded_same_set_external_brief_20260413.md` and `reports/expanded_same_set_results_section_20260413.md`.
- A manuscript-style full draft (intro → methods → results → discussion → limits) is in `reports/expanded_same_set_manuscript_draft_20260413.md`.
- The manuscript draft now contains `Table 1`, `Table 2`, `Figure 1`, `Figure 2`, and `Box 1` callouts; copy-ready captions are in `reports/expanded_same_set_figure_legends_20260413.md`.
- PNG figures are not yet generated; demo SVG and real-run SVG figures are available.
- Two pipeline-validation demo runs can be seeded at any time.
- A run-directory template is ready for immediate real-run use.
- Once `outputs.csv` is populated, annotation and summary artifacts can be produced from the run directory.
- `annotation_sheet.csv` can be auto-scored by the OpenAI `mini` judge.
- If `OPENAI_API_KEY` is set, `outputs.csv` can be filled directly inside the run directory.

## Immediate next steps

1. Execute the canonical full-v1 model run against `runs/real_run_v1_120_template_20260413`.
2. Fill full-v1 `outputs.csv` and annotations with `scripts/run_openai_responses.py` and `scripts/judge_annotations_openai.py`.
3. Generate the full-v1 summary and qualitative cases via `scripts/finalize_run_dir.py`.
4. Update `reports/health_reliability_eval_v1.md` to center on the full-v1 canonical result.
5. Keep the expanded `40`-row same-set results as the manuscript package and stress-test reference.

## License

This package is covered by the repository's top-level split license:

- **Code** (`scripts/`, all `.py` files) — [Apache License 2.0](../LICENSE).
- **Data, prompts, rubrics, figures, reports** (`data/`, `prompts/`, `docs/`, `figures/`, `reports/`, `research/`, `runs/`, all `.md`/`.csv`/`.jsonl`/`.json`/`.svg`) — [Creative Commons Attribution-NonCommercial 4.0 International (CC BY-NC 4.0)](../LICENSE-DATA). Commercial use of the dataset or prompts requires a separate license — see the repository root README for contact.
