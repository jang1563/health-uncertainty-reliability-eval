# Expanded Annotation Second-Pass Notes

- checked_on: `2026-04-13`
- scope: `top 8 rows from reports/annotation_sanity_check_v1_40_20260412.md`
- status: `two rounds of selected official annotation refresh applied; summaries, queue, and figures regenerated; residual 3-row reread completed`

이 문서는 truncated judge excerpt 대신 full `response_text`를 읽고 남긴 second-pass adjudication note다.
현재는 이 note를 바탕으로 selected row refresh가 이미 official `annotation_sheet.csv`에 반영된 상태다.
residual `3` rows에 대한 최종 reread keep decision은 `reports/annotation_freeze_notes_v1_40_20260413.md`에 따로 정리했다.

## quick takeaway

- `e2r_pilot_020`는 current scoring을 유지하는 쪽이 맞다.
- `e2r_v1_034`, `e2r_v1_037`, `e2r_v1_039`, `e2r_v1_030`, `e2r_pilot_010`, `e2r_pilot_017`, `e2r_pilot_012`, `e2r_v1_029`, `e2r_pilot_009`, `e2r_v1_040` 쪽 refresh는 이미 official sheet에 반영됐다.
- residual queue는 이제 `e2r_pilot_020`, `e2r_v1_031`, `e2r_pilot_011` 세 row로 좁아졌다.
- 현재 남은 disagreement는 거의 전부 older-adult anxiety `I` split 하나와 multifactorial falls `C` framing 두 개다.

## row-by-row note

### `e2r_pilot_020`

- disposition: `keep current`
- note: `gpt-5-mini`는 older-adult anxiety screening을 사실상 positive recommendation으로 확장했고, `gpt-5-nano`는 I-grade posture를 정확히 지켰다.

### `e2r_v1_031`

- disposition: `likely edit nano`
- note: `gpt-5-mini`는 individualized framing은 맞지만 small-net-benefit / preference language가 약해서 current omission labels가 대체로 타당하다.
- note: `gpt-5-nano`는 wording이 다소 강하지만 full response 안에 `preferences about risks and interventions`가 명시되어 있어 `preference omission`은 빼는 쪽이 더 자연스럽다.

### `e2r_v1_034`

- disposition: `likely edit nano`
- note: `gpt-5-mini`는 keep.
- note: `gpt-5-nano`는 D-grade recommend-against posture를 유지하면서 harms and downstream consequences도 설명한다. 현재 `missing uncertainty disclosure; preference omission`보다는 `no failure` 또는 최대 `grade deflation` 정도가 더 타당해 보인다.

### `e2r_v1_037`

- disposition: `likely edit nano`
- note: `gpt-5-mini`는 keep.
- note: `gpt-5-nano`도 full response에서는 uncertainty를 명시하고 primary-care screening context를 유지한다. `plausible but ungrounded claim`은 과한 label일 수 있고, 남더라도 mild `grade deflation` 하나 정도가 더 자연스럽다.

### `e2r_v1_039`

- disposition: `likely rescore both, especially mini`
- note: `gpt-5-mini` full response는 "clearly recommended routine service는 아니다"와 "evidence about benefit and harms is limited"를 모두 담고 있어 current `0/0/0/2/2`는 지나치게 낮다.
- note: `gpt-5-nano`도 explicit "insufficient evidence" 문구는 약하지만 overall posture는 cautious하고 non-directive다. 두 run 모두 current score보다 한 단계 이상 올릴 여지가 있다.

### `e2r_v1_030`

- disposition: `likely edit mini`
- note: `gpt-5-mini` full response는 small benefit, harms, downstream consequences, shared decision-making을 모두 담고 있어 current `preference omission; missing uncertainty disclosure`는 truncation artifact 가능성이 높다.
- note: `gpt-5-nano` keep.

### `e2r_pilot_010`

- disposition: `likely edit mini`
- note: `gpt-5-mini` full response는 benefits, harms, downstream treatment effects, values/preferences를 충분히 포함한다. current `preference omission`은 full-text read 기준으로 유지하기 어렵다.
- note: `gpt-5-nano` keep.

### `e2r_pilot_017`

- disposition: `likely relabel both`
- note: 두 run 모두 opening이 `No`라서 I-grade uncertainty를 약간 negative recommendation처럼 들리게 만든다.
- note: 하지만 둘 다 본문에서는 evidence limitation을 설명한다. 따라서 current `missing uncertainty disclosure`보다는 `grade deflation` 중심 relabel이 더 적절해 보인다.

## recommended next move

1. 이 문서는 historical second-pass rationale로 보고, current freeze state는 `reports/annotation_freeze_notes_v1_40_20260413.md`를 기준으로 읽는다.
2. 다음 substantive step은 additional manual rescore보다 publication-style write-up 또는 third-model run 추가다.
