# Runs

- checked_on: `2026-04-10`
- project: `Evidence-to-Recommendation Reliability Eval`

## 목적

이 디렉터리는 실제 또는 데모 run artifact를 저장한다.

## run 종류

- `demo_handcrafted_reference`
  - benchmark-aligned reference-style response
  - smoke test용
  - 실제 외부 모델 결과가 아님
- `demo_overconfident_baseline`
  - `C/I/D`에서 과신하거나 과권고하는 실패 패턴을 의도적으로 포함한 baseline
  - benchmark discrimination smoke test용
  - 실제 외부 모델 결과가 아님

## 원칙

- demo run과 real model run은 이름부터 명확히 구분한다.
- real run이 생기면 model name, prompt version, run date를 함께 기록한다.
- public-facing report에서는 demo run을 실제 benchmark leaderboard처럼 제시하지 않는다.

## real run 시작점

- `run_manifest_template.json`
  - 새 실제 run의 기본 metadata template
- `scripts/init_run_dir.py`
  - manifest, outputs template, notes file까지 포함한 새 run 디렉터리 생성
