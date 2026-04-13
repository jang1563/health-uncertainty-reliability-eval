# Limitations

- version: v1
- last_updated: 2026-04-13

## Known Limitations

1. **Small event count.** v1 contains 30 events (90 items). This is sufficient for signal detection but not for robust statistical power across all section types.

2. **Source window bias.** Events are drawn from 2024-01-01 to 2026-03-31. Drugs with safety updates outside this window are excluded.

3. **NDA/BLA only.** Generic (ANDA) products are excluded in v1. This limits applicability to branded prescription products.

4. **Human-authored packets.** The before_packet and after_packet are human-authored summaries, not verbatim FDA text. Summary quality may influence benchmark results independently of update sensitivity.

5. **No model knowledge cutoff interaction.** This benchmark does not test whether a model "knows" about an update from training data. It tests whether the model responds appropriately to two different evidence packets provided at inference time.

6. **Prompt variant coverage.** Three prompt styles (patient, caregiver, medication-use decision) may not capture all real-world question patterns.

7. **Single-turn evaluation.** The benchmark tests single-turn responses only. Multi-turn dialogue behavior is not assessed.

8. **Rubric subjectivity and judge sensitivity.** Some rubric dimensions (e.g., safety_severity_calibration and actionability_and_followup_guidance) require judgment on edge cases. A 10-case Sonnet re-judging pass across all three completed model runs (30 scored pairs total) found no >1-point dimension divergences versus the Haiku judge, but 7/30 rows did show 1-point shifts. Full inter-rater reliability is still not established in v1.

9. **English only.** All items are in English. Multilingual update sensitivity is not tested.

10. **No dose-specific granularity.** Events are tracked at the drug/section level, not at the dose or formulation level.
