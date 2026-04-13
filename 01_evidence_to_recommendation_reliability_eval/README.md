# Evidence-to-Recommendation Reliability Eval

- checked_on: `2026-04-13`
- working_title: `Evidence-to-Recommendation Reliability Eval`
- parent_artifact_family: `Health Uncertainty and Reliability Eval`
- status: `full-v1 dataset scaffold built; four real runs completed; expanded same-set freeze review recorded`

## 목적

이 디렉터리는 `예방의학 권고 등급`, `불확실성 표현`, `환자 선호 민감성`을 모델이 얼마나 충실하게 보존하는지 평가하는 공개 benchmark artifact를 준비하기 위한 연구 패키지다.

핵심 질문은 단순히 "가이드라인을 맞히는가?"가 아니다. 더 중요한 질문은 아래와 같다.

- 모델이 `A/B/C/D/I` 권고의 강도를 과장하거나 약화시키지 않는가
- `I statement` 상황에서 근거 불충분을 솔직하게 전달하는가
- `C grade`처럼 선호와 가치 판단이 중요한 상황에서 환자 선호를 묻거나 인정하는가
- 환자 친화적 표현을 쓰더라도 근거 세기를 왜곡하지 않는가

## 왜 이 트랙인가

현재 공개된 health benchmark들은 대체로 아래 둘 중 하나에 집중한다.

- broad health conversation safety
- clinician-facing guideline adherence

반면 이 프로젝트는 아래 빈 공간을 겨냥한다.

- `recommendation-grade fidelity`
- `uncertainty disclosure fidelity`
- `preference-sensitive communication`

즉, `recommendation generation system`도 아니고 `clinical workflow agent`도 아니다. `공개 근거를 환자-facing 답변에서 얼마나 정직하게 전달하는지`를 재는 benchmark다.

## 디렉터리 구성

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
- `HANDOFF_FOR_NEW_SESSION.md`
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

## 소스 정책 요약

- `USPSTF`: paraphrase-first, short-quote-only when necessary, source URL required
- `AHRQ`: rubric derivation 중심, 원문 재배포 최소화
- `MedlinePlus`: public-domain으로 명시된 health topic summary와 medical test 정보만 사용

## 현재 결론

- 진행 가치가 충분하다.
- 가장 가까운 인접 작업은 `HealthBench`, `AMEGA`, `MedGUIDE`, `From Evidence to Recommendations...`, `Q2CRBench-3`다.
- 그러나 이들은 각각 `broad conversation`, `guideline adherence`, `recommendation generation` 쪽에 더 가깝고, 이 프로젝트의 중심인 `grade-preserving patient-facing reliability eval`과는 다르다.

## 현재 구현 상태

- research pack이 완료되어 있다.
- pilot dataset scaffold가 생성되어 있다.
- `20`개 pilot example 초안이 `A/B/C/D/I` 각 grade를 모두 포함하도록 작성되어 있다.
- `40`개 expanded candidate example set도 추가되어 다음 run 준비가 되어 있다.
- `120`개 full-v1 scaffold도 생성되어 canonical full-v1 run 준비가 되어 있다.
- annotation workflow scaffold가 생성되어 있다.
- prompt-pack export workflow가 생성되어 있다.
- smoke-test demo run workflow가 생성되어 있다.
- multi-run comparison report와 demo SVG figure workflow가 생성되어 있다.
- real-run comparison report와 real-run SVG figure workflow가 생성되어 있다.
- real-run initialization과 qualitative case extraction workflow가 생성되어 있다.
- run-centric prepare/finalize workflow가 생성되어 있다.
- OpenAI Responses API용 run script가 생성되어 있다.
- OpenAI judge script도 생성되어 있다.
- `runs/demo_handcrafted_reference`와 `runs/demo_overconfident_baseline`이 이미 생성되어 있다.
- `runs/real_run_template_20260410`와 `runs/real_openai_gpt5nano_20260410`이 이미 생성되어 있다.
- `runs/real_openai_gpt5nano_v1_40_20260412`가 expanded 40-row candidate set 기준으로 생성 및 채점 완료되어 있다.
- `runs/real_openai_gpt5mini_v1_40_20260412`도 same-set 기준으로 생성 및 채점 완료되어 있다.
- `runs/real_run_v1_120_template_20260413`이 full-v1 canonical run template로 초기화되어 있다.
- `response -> annotation sheet -> summary report` 흐름을 위한 script와 template이 포함되어 있다.
- real model run 네 개가 이미 완료되어 있다.
- expanded candidate set 기준 `gpt-5-mini`와 `gpt-5-nano` same-set head-to-head가 모두 완료되어 있다.
- expanded same-set 결과를 위한 annotation sanity-check queue도 생성되어 있다.
- residual `3`-row sanity-check queue는 final reread까지 끝났고, current official annotation sheet를 working frozen version으로 보고 있다.
- full-v1 dataset build summary는 `reports/full_v1_dataset_build_20260413.md`에 정리되어 있다.
- frozen `40`-row same-set 결과를 publication-style로 요약한 draft가 `reports/expanded_same_set_public_draft_20260413.md`에 있다.
- 더 짧은 external brief와 manuscript-style results section도 각각 `reports/expanded_same_set_external_brief_20260413.md`, `reports/expanded_same_set_results_section_20260413.md`에 정리했다.
- intro-methods-results-discussion-limits를 잇는 manuscript-style full draft도 `reports/expanded_same_set_manuscript_draft_20260413.md`에 추가했다.
- manuscript draft에는 이제 `Table 1`, `Table 2`, `Figure 1`, `Figure 2`, `Box 1` callout이 들어가고, copy-ready caption은 `reports/expanded_same_set_figure_legends_20260413.md`에 따로 정리했다.
- PNG figure는 아직 없지만 demo SVG와 real-run SVG는 생성되어 있다.
- 대신 pipeline 검증용 demo run 두 개를 seed할 수 있다.
- real run을 위한 run directory template도 바로 만들 수 있다.
- `outputs.csv`만 채우면 run 디렉터리 기준으로 annotation과 summary 산출을 이어갈 수 있다.
- `annotation_sheet.csv`도 OpenAI mini judge로 자동 채점할 수 있다.
- `OPENAI_API_KEY`가 있으면 run 디렉터리에 직접 `outputs.csv`를 채우는 흐름도 사용할 수 있다.

## 바로 다음 단계

1. `runs/real_run_v1_120_template_20260413`를 기준으로 canonical full-v1 model run 수행
2. `scripts/run_openai_responses.py`와 `scripts/judge_annotations_openai.py`로 full-v1 outputs와 annotation 채우기
3. `scripts/finalize_run_dir.py`로 full-v1 summary와 qualitative case 생성
4. `reports/health_reliability_eval_v1.md`를 full-v1 canonical result 중심으로 갱신
5. expanded `40`-row same-set 결과는 manuscript package와 stress-test reference로 유지
