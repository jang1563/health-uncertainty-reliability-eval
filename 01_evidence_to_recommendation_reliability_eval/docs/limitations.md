# Limitations

- checked_on: `2026-04-17`
- project: `Evidence-to-Recommendation Reliability Eval`
- scope: `release-candidate limitations after canonical full-v1 completion`

## Current Limits

- The canonical full-v1 run exists, but some cross-provider interpretation is still judge-bound.
- The Sonnet 4.6 `A/D/I preference omission` pattern is still provisional because blinded adjudication is not complete.
- The current public comparison still depends on a single primary judge model (`gpt-5-mini`) for the scored runs.
- A completed secondary-judge rerating now shows strong judge dependence on the Sonnet anomaly slice, but blinded human adjudication is still pending.
- `medlineplus_url` coverage is still partial and not central to the current release.

## Benchmark Design Limits

- The benchmark is deliberately narrow: `USPSTF`-anchored, one-turn, patient-facing, and preventive-care specific.
- `C` and `I` are oversampled because they are the main posture-sensitive cases; this is a feature of the design, but it narrows generalizability.
- Paraphrase-first row construction can compress source nuance.
- One-turn answers may understate a model's longitudinal shared-decision-making ability.

## Interpretation Limits

- High scores do **not** imply deployment readiness.
- Low scores do **not** imply pure knowledge failure; some misses may reflect instruction style or judge behavior.
- Point estimates on `120` rows should not be treated like definitive vendor rankings without the accompanying confidence intervals and paired-delta context.
- A clean result on the `40`-row supporting stress test does not replace the `120`-row canonical benchmark.

## Source Limits

- USPSTF topics come from statements published at different times; “current published” does not mean one uniform source year.
- Some valuable `D`-grade topics remain older but are still current final statements.
- The source family is intentionally narrow for methodological clarity; it is not yet a multi-guideline benchmark.

## Active Mitigations

- A blinded `53`-row adjudication packet is built for the Sonnet anomaly.
- The release check now separates development consistency audits from the strict final release gate.
- Run summaries now include bootstrap confidence intervals and provisional flags.
- Cross-provider comparison now uses paired same-set deltas rather than point estimates alone.
- Public-facing docs avoid deployment claims and treat unresolved Sonnet behavior as an open adjudication question.
- The tracked adversarial review note in `docs/red_team_review_20260417.md` records the workflow hardening findings and follow-up fixes.
