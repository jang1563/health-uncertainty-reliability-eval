# Limitations

- checked_on: `2026-04-13`
- project: `Evidence-to-Recommendation Reliability Eval`
- scope: `post-full-v1-scaffold limitations`

## 현재 한계

- `120`-row full-v1 scaffold는 완성됐지만, canonical full-v1 real run은 아직 없다.
- source coverage는 넓지만, 각 grade 내부 변형은 아직 충분히 다양하지 않다.
- empirical failure pattern은 `20`-row와 `40`-row real run에서는 이미 보이지만, full-v1 canonical run 기준 pattern은 아직 없다.
- inter-annotator agreement 절차가 아직 없다.
- `medlineplus_url` mapping은 아직 부분적으로만 준비되어 있다.

## source-related limitations

- USPSTF 자체가 발행 시점이 다른 recommendation set으로 구성되어 있어, `current published`라고 해도 주제별 최신 연도가 다르다.
- 일부 매우 유용한 D-grade topic은 추천 statement가 오래되었지만 여전히 current final statement다.
- benchmark row는 paraphrase-first라서 source nuance가 줄어들 수 있다.

## benchmark design limitations

- patient-facing wording을 쓰기 때문에 너무 generic caution benchmark처럼 보일 위험이 있다.
- `C`와 `I`는 nuance-heavy category라 rubric drift가 생기기 쉽다.
- one-turn response만 보면 실제 longitudinal shared decision-making 능력을 과소평가할 수 있다.

## interpretation limitations

- 높은 점수가 clinical deployment readiness를 뜻하지 않는다.
- 낮은 점수는 반드시 knowledge deficiency만을 의미하지 않는다.
- 일부 failure는 source misunderstanding이 아니라 instruction-following style 차이에서 올 수 있다.

## 완화 계획

- full-v1 canonical run을 실제로 수행한다.
- pilot self-audit 후 row wording을 다시 정제한다.
- future report에서 qualitative failure examples를 함께 제시한다.
- public README에서 deployment claim을 명시적으로 피한다.
