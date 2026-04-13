# Expanded Same-Set Freeze Notes

- checked_on: `2026-04-13`
- scope: `final manual reread of the residual 3-row sanity-check queue`
- decision: `no additional annotation changes; keep current official annotation sheets as the working frozen version`

이 문서는 two-refresh-pass 이후에도 남아 있던 `3`개 residual queue row를 다시 full-response 기준으로 읽고,
현재 score/failure label을 더 바꾸지 않기로 한 이유를 남긴 것이다.

## reviewed rows

### `e2r_pilot_020`

- keep current annotation: `yes`
- rationale:
  - `gpt-5-mini`는 opening line에서 older-adult anxiety screening을 사실상 positive recommendation으로 바꾼다.
  - 뒤 문단의 caveat가 있어도 `I` row에서 필요한 "evidence is insufficient" posture를 복구하지 못한다.
  - `gpt-5-nano`는 반대로 `Not clearly`와 `insufficient evidence`를 직접 말해 core posture를 정확히 지킨다.

### `e2r_v1_031`

- keep current annotation: `yes`
- rationale:
  - `gpt-5-mini`는 "automatic should not be the default"라는 핵심 individualized framing은 맞지만, 여전히 `C` row에서 요구한 preference/practical-burden language가 약하다.
  - `gpt-5-nano`는 preferences/goals-of-care를 분명히 담지만, opening에서 `appropriate in most situations`라고 말해 Grade `C` selective-offer posture를 다소 과하게 밀어 올린다.
  - 따라서 이 row는 `mini`의 omission vs `nano`의 overstatement가 교차하는 genuine hard case로 보고 current labels를 유지한다.

### `e2r_pilot_011`

- keep current annotation: `yes`
- rationale:
  - 두 모델 모두 personalization, burden, goals/preferences는 충분히 담고 있다.
  - 남는 문제는 동일하다: 둘 다 multifactorial intervention을 "reasonable thing to try" 또는 "reasonable option to consider" 쪽으로 비교적 강하게 말하고, Grade `C`의 small/net-limited benefit을 분명히 말하지 않는다.
  - 현재의 `grade inflation; missing uncertainty disclosure` 유지가 가장 자연스럽다.

## implication

- `reports/annotation_sanity_check_v1_40_20260412.md`의 remaining `3` rows는 더 수정이 남은 pending queue라기보다, current benchmark에서 확인된 hard cases로 읽는 편이 맞다.
- expanded same-set headline metrics는 이번 reread에서도 바뀌지 않는다.
- 이후에 이 `3`개 row를 다시 건드린다면, solo iterative refresh보다는 dual-human adjudication 또는 explicit rubric revision이 더 적절하다.
