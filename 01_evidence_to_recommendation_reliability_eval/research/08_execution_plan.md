# Execution Plan

- checked_on: `2026-04-10`
- project: `Evidence-to-Recommendation Reliability Eval`

## implementation order

1. `README` skeleton 작성
2. source topic pool 잠금
3. rubric schema와 failure taxonomy JSON 초안 작성
4. 20 examples pilot 작성
5. pilot self-audit
6. full 120 examples 작성
7. canonical evaluation notebook or script 작성
8. report and figure 생성

## concrete deliverables for the next build turn

- `data/examples.csv`
- `data/rubric_schema.json`
- `docs/methodology.md`
- `docs/limitations.md`
- `reports/health_reliability_eval_v1.md`
- `figures/grade_fidelity_summary.png`
- `figures/failure_taxonomy_breakdown.png`

## suggested implementation checkpoints

### checkpoint 1

- 20 pilot examples complete
- at least one `A`, `B`, `C`, `D`, `I` example each
- rubric wording frozen

### checkpoint 2

- 120 examples complete
- source links and dates verified
- all benchmark rows are paraphrase-first

### checkpoint 3

- canonical model run complete
- markdown report complete
- README rewritten for external readers

## main risks

- `USPSTF` topic sampling이 너무 한정되면 breadth가 약해 보일 수 있음
- `C`와 `I` examples의 wording이 나쁘면 그냥 generic caution benchmark처럼 보일 수 있음
- source paraphrase가 너무 느슨하면 fidelity artifact라는 정체성이 약해질 수 있음

## mitigations

- grade 분포를 미리 잠금
- source topic 당 최대 4개로 제한
- `C` and `I`를 benchmark center로 유지
- README에서 `broad health safety eval`과의 차이를 첫 화면에서 설명
