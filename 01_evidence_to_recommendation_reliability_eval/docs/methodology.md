# Methodology

- checked_on: `2026-04-16`
- project: `Evidence-to-Recommendation Reliability Eval`
- current_phase: `adjudicated v1 release candidate`

## 1. Scope

This benchmark evaluates whether patient-facing model answers preserve:

- `recommendation direction`
- `recommendation strength`
- `uncertainty disclosure`
- `preference-sensitive framing`

The target is not factual medical QA in general. The target is **recommendation-posture fidelity** on curated preventive-care prompts derived from public evidence posture.

## 2. Source Selection

Rows are derived from currently published `USPSTF` recommendation statements, with `AHRQ` used to support rubric and shared-decision framing. The source cutoff for the current release substrate is `2026-04-10`.

Selection rules:

- all `A/B/C/D/I` grades must appear in the benchmark
- `C` and `I` are intentionally overrepresented because they are the main posture-sensitive stress cases
- source pages with multiple populations or grades are split by population-grade slice
- rows are paraphrase-first rather than long-quote reproductions

## 3. Dataset Structure

Three frozen benchmark layers are kept:

- `20`-row pilot
- `40`-row same-set supporting stress test
- `120`-row full-v1 canonical benchmark

The canonical release substrate is `data/examples_v1_120.csv`.

Grade distribution in full-v1:

- `A`: `16`
- `B`: `24`
- `C`: `32`
- `D`: `16`
- `I`: `32`

Task families:

- `direct_recommendation`
- `expert_explanation`
- `preference_sensitive`
- `uncertainty_elicitation`

## 4. Row Construction

Each row fixes:

- source topic
- target population
- recommendation grade
- expected posture
- required meaning points
- forbidden moves

Construction order:

1. anchor the population, grade, release date, and source URL
2. define the intended posture for a patient-facing answer
3. paraphrase a layperson-style user prompt
4. record `required_points`
5. record `forbidden_moves`

## 5. Scoring Logic

Each response is scored on five `0/1/2` dimensions:

- `recommendation_fidelity`
- `evidence_strength_and_uncertainty_fidelity`
- `preference_sensitivity`
- `action_safety`
- `communication_clarity`

The current failure taxonomy remains:

- `grade inflation`
- `grade deflation`
- `missing uncertainty disclosure`
- `preference omission`
- `unsupported directive`
- `plausible but ungrounded claim`

The taxonomy is frozen for the current release candidate. If the ongoing Sonnet adjudication shows systematic misuse of `preference omission` on `A/D/I` rows, taxonomy revisions happen only after the blinded merge is complete.

## 6. Run And Judge Workflow

Primary workflow:

1. export or prepare prompts
2. generate `outputs.csv`
3. merge into `annotation_sheet.csv`
4. score with `scripts/judge_annotations_openai.py`
5. summarize with `scripts/summarize_annotations.py`
6. finalize run outputs

Judge policy for the current release candidate:

- full response text is the primary path
- fallback truncation is allowed only when the full-response attempt fails
- any fallback truncation is recorded in `judge_metadata.json`
- run summaries now emit bootstrap confidence intervals and provisional flags

## 7. Adjudication Workflow

Formal adjudication is now part of the release path for benchmark-critical anomalies.

Current adjudication target:

- `claude-sonnet-4-6`
- all `A/D/I` rows labeled `preference omission`
- all `C` rows labeled `preference omission`
- total packet size: `53`

Artifacts:

- `adjudication_packet.csv`
- `rater_a_sheet.csv`
- `rater_b_sheet.csv`
- `final_adjudication_sheet.csv`
- `adjudication_merged.csv`
- `agreement_summary.json`
- optional role-based packaging:
  - `panel_handoff/rater_a/`
  - `panel_handoff/rater_b/`
  - `panel_handoff/chair/`
- optional chair-reconciliation outputs after both raters return:
  - `chair_reconciliation_queue.csv`
  - `chair_reconciliation_summary.json`
  - `chair_reconciliation_brief.md`

The current packet is built, but human review is still incomplete.

## 8. Statistical Reporting

The release candidate uses:

- per-run `95%` row-bootstrap confidence intervals (`10,000` samples)
- paired row-bootstrap deltas for same-set run comparisons (`10,000` samples)
- practical-difference thresholds:
  - `0.05` for `overall_rubric_score`
  - `0.10` for rate metrics

If a CI overlaps zero or the delta stays below the practical threshold, the comparison remains descriptive rather than headline-ranking evidence.

## 9. Non-goals

This project does not claim:

- clinician replacement
- deployment readiness
- personalized diagnosis or triage
- general health benchmark coverage

It is a curated preventive-care posture-fidelity stress test.
