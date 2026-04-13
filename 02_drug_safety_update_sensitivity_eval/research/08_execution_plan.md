# Execution Plan

- checked_on: `2026-04-10`
- project: `Drug Safety Update Sensitivity Eval`

## implementation order

1. `README` skeleton 작성
2. event universe 수집
3. 30 events shortlist 잠금
4. `before_packet / after_packet` template 고정
5. 6 events pilot 작성
6. pilot self-audit
7. full 30 events x 3 prompt variants 작성
8. canonical evaluation script and report 작성

## concrete deliverables for the next build turn

- `data/benchmark_items.jsonl`
- `data/schema.json`
- `docs/methodology.md`
- `docs/limitations.md`
- `reports/drug_safety_update_eval_v1.md`
- `figures/update_uptake_summary.png`
- `figures/stale_reassurance_breakdown.png`

## suggested implementation checkpoints

### checkpoint 1

- 6 pilot events complete
- at least one `strengthening`, one `removal`, one `control`
- rubric wording frozen

### checkpoint 2

- 30 events complete
- source links verified
- all packets are human-authored summaries, not copied label text

### checkpoint 3

- canonical model run complete
- markdown report complete
- README rewritten for external readers

## main risks

- event sourcing가 너무 어렵거나 불균형할 수 있음
- risk-decrease examples가 부족할 수 있음
- packet quality가 낮으면 benchmark가 source fidelity보다 summarization quality를 재게 될 수 있음

## mitigations

- v1 event window를 recent years로 제한
- stricter vs relaxed update 비율을 미리 잠금
- control events를 반드시 포함
- packet authoring guide를 먼저 만든 뒤 본문 작성을 시작
