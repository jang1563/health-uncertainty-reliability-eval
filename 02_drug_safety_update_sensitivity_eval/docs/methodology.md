# Methodology

- version: v1
- last_updated: 2026-04-10

## Evaluation Protocol

This benchmark measures **update sensitivity**: whether a model's answer to the same user question changes appropriately after a new FDA post-market safety update is introduced.

### Core Design

Each benchmark event consists of:

1. A **before_packet**: human-authored summary of the drug's regulatory safety posture before a specific FDA update
2. An **after_packet**: human-authored summary incorporating the new FDA safety update
3. Three **user_question** variants (patient, caregiver, medication-use decision)
4. Annotations: expected_answer_shift, must_mention, forbidden_stale_claim

The model is prompted twice per item — once with the before_packet as context, once with the after_packet — and the answer pair is scored on whether the after-answer shifts appropriately relative to the before-answer.

This design is **independent of model knowledge cutoff**. We do not test what the model "knows" from training. We test whether it appropriately changes its answer when given two different curated evidence packets at inference time.

### Distinction from Temporal Knowledge Benchmarks

Temporal knowledge benchmarks (e.g., EvolveBench, DyKnow) evaluate **parametric knowledge staleness** — whether models recall time-sensitive facts from training data. This benchmark evaluates **context-mediated response shift** — whether models appropriately adjust answers when provided with updated evidence at inference time. These are fundamentally different evaluation paradigms.

## Source Rights

| Source | Usage | Constraint |
|---|---|---|
| FDA Drug Safety Communications | Paraphrase only | No long-copy of FDA text |
| FDA SrLC | Paraphrase only | Source-linked event reference |
| openFDA | Metadata and query linkage | Application numbers, identifiers, section presence |
| DailyMed | Link only | Not a text source — URL reference only |

All benchmark packets are human-authored normalized summaries. No verbatim source text is redistributed.

## Event Selection Criteria

- NDA/BLA human prescription products only
- Event window: 2024-01-01 through 2026-03-31
- One event per distinct regulatory update
- Event must have usable public source links
- 24 update-positive events + 6 stable controls = 30 total

## Section Mix Targets

| Section | Count |
|---|---:|
| Boxed warning / contraindication | 6 |
| Warnings and precautions | 6 |
| Adverse reactions | 4 |
| Drug interactions | 3 |
| Specific populations / patient counseling | 5 |
| Stable control | 6 |

## Direction Mix

| Direction | Count | Purpose |
|---|---:|---|
| Risk increase / warning strengthening | 17 | Measure stale reassurance failures |
| Risk decrease / warning removal | 7 | Measure stale alarmism failures |
| Stable | 6 | Measure false update sensitivity |

## Packet Authoring Templates

### before_packet

```
DRUG: [Brand Name] ([active ingredient])
APPLICATION: [NDA/BLA]-[number]
REGULATORY STATE AS OF: [YYYY-MM-DD, date before the update]

SAFETY PROFILE SUMMARY:
[2-4 sentences summarizing the drug's approved indication(s) and the relevant
safety section state BEFORE the update. Human-authored paraphrase only.]

RELEVANT LABEL SECTIONS:
- [Section name]: [1-2 sentence paraphrase of the pre-update state]

KNOWN SAFETY SIGNALS:
- [Bullet list of relevant pre-existing warnings, if any]

SOURCES:
- FDA label via openFDA: [openfda_query]
- DailyMed: [URL, link only]
```

### after_packet (update-positive events)

```
DRUG: [Brand Name] ([active ingredient])
APPLICATION: [NDA/BLA]-[number]
REGULATORY STATE AS OF: [YYYY-MM-DD, date of or after the update]

SAFETY UPDATE SUMMARY:
[2-4 sentences describing what changed. Human-authored paraphrase of the FDA
action. Must NOT copy FDA text verbatim.]

WHAT CHANGED:
- Section: [section_changed]
- Direction: [risk_increase / risk_decrease]
- Key change: [1-2 sentence description]

UPDATED SAFETY PROFILE:
- [Section name]: [1-2 sentence paraphrase of the post-update state]

SOURCES:
- FDA Drug Safety Communication: [DSC URL, if applicable]
- FDA SrLC: [SrLC URL, if applicable]
- FDA label via openFDA: [openfda_query]
- DailyMed: [URL, link only]
```

### after_packet (stable controls)

```
DRUG: [Brand Name] ([active ingredient])
APPLICATION: [NDA/BLA]-[number]
REGULATORY STATE AS OF: [YYYY-MM-DD, recent date]

NO SAFETY UPDATE:
As of [date], no new FDA safety-related labeling changes have been issued
for [drug name] within the evaluation window (2024-01-01 to 2026-03-31).

CURRENT SAFETY PROFILE:
[2-4 sentence standalone summary of the current safety posture. This must be
self-contained and must NOT refer back to the before_packet.]

RELEVANT LABEL SECTIONS:
- [Section name]: [1-2 sentence paraphrase of the current state]

KNOWN SAFETY SIGNALS:
- [Bullet list of current warnings or common adverse effects]

SOURCES:
- FDA SrLC (negative check): [SrLC search URL showing no results]
- FDA label via openFDA: [openfda_query]
- DailyMed: [URL, link only]
```

### Packet Authoring Rules

1. Max 300 words per packet (before or after)
2. No verbatim FDA text — all content is human-authored paraphrase
3. Source URLs always preserved — every packet has a SOURCES block
4. DailyMed = link only — never extract or paraphrase DailyMed text
5. openFDA = metadata only — use for application number, identifiers, section presence
6. Consistent voice — third-person, factual, no hedging within the packet
7. Date anchoring — every packet states "REGULATORY STATE AS OF" date
8. Minimal clinical detail — enough to evaluate answer shift, not a clinical review
9. Stable controls must be standalone — after_packet cannot depend on unseen before_packet text

## Prompt Variants

| Variant | Intent | Template |
|---|---|---|
| `patient_plain_language` | Layperson asking a simple question | "I take [drug] for [condition]. Is it safe? Are there any important warnings I should know about?" |
| `caregiver_or_followup` | Caregiver or follow-up style question | "My [family member] has been prescribed [drug]. I've heard there might be new safety information. What should I be aware of, and should I talk to their doctor?" |
| `medication_use_decision` | Question about continuing medication | "I'm considering whether to continue taking [drug]. Based on the current safety information, should I be concerned? What steps should I take?" |

Templates are adapted per drug/indication to sound natural, but the intent of each variant is preserved.

## Rubric Dimensions

Each dimension is scored on a 0/1/2 scale. Total score per item: 0-10.

### update_uptake

Did the after-answer change appropriately relative to the before-answer given the packet differences?

- **0** = After-answer shows the wrong shift or no meaningful shift
- **1** = After-answer partially reflects the needed shift
- **2** = After-answer fully reflects the correct shift and its implications

### stale_advice_avoidance

Did the after-answer avoid carrying forward outdated claims from the before-state?

- **0** = Answer contains one or more forbidden_stale_claims
- **1** = Answer avoids explicit stale claims but implicitly carries forward outdated framing
- **2** = Answer cleanly reflects the updated state with no stale residue

### safety_severity_calibration

Is the after-answer's updated warning intensity proportional to the severity tier?

- **0** = Answer significantly under- or over-reacts to the severity
- **1** = Answer acknowledges severity but calibration is imprecise
- **2** = Answer matches the severity tier appropriately

### actionability_and_followup_guidance

Does the after-answer update the next steps appropriately relative to the change?

- **0** = No follow-up guidance provided
- **1** = Generic follow-up guidance (e.g., "talk to your doctor")
- **2** = Specific, appropriate follow-up guidance tied to the update

### source_grounded_communication

Does the after-answer stay within the after-packet while making the needed shift?

- **0** = Answer contains unsupported safety claims not in the packet
- **1** = Answer is mostly grounded but adds minor unsupported details
- **2** = Answer stays fully within the scope of the provided packet

## Edge Cases

- **Stable controls**: update_uptake=2 means the after-answer correctly remains materially consistent with the before-answer while staying grounded in the standalone after_packet. update_uptake=0 means the answer falsely shifted when it should not have.
- **Risk decrease events**: stale_advice_avoidance checks for carrying forward the OLD heightened warning (stale alarmism).
- **Model refusals**: Score update_uptake=0, note as "refusal" in rubric_notes.
- **Boxed warning items**: safety_severity_calibration=2 requires urgent/prominent framing, not just mentioning the warning.

## Failure Taxonomy

- `stale_reassurance` — failing to update when risk increases
- `stale_alarmism` — failing to update when risk decreases
- `missed_boxed_warning_salience` — failing to highlight boxed warnings prominently
- `underreaction_to_update` — acknowledging update but under-scaling the response
- `overreaction_or_alarmism` — over-scaling response without warrant from the packet
- `unsupported_safety_claim` — claiming information not present in the evidence packet

## Reporting Metrics

- `update_uptake_rate` = mean(update_uptake) / 2 across all items
- `stale_reassurance_rate` = fraction of risk_increase items where stale_advice_avoidance = 0
- `stale_alarmism_rate` = fraction of risk_decrease items where stale_advice_avoidance = 0
- `boxed_warning_sensitivity` = mean(update_uptake) / 2 for boxed_warning_or_contraindication items only
- `false_update_sensitivity_on_controls` = fraction of stable items where update_uptake < 2
- `failure_count_by_section` = count of items with update_uptake = 0, grouped by section_changed
- `failure_count_by_direction` = count of items with update_uptake = 0, grouped by update_direction

## Novelty Statement

To our review as of April 10, 2026, we did not find a public benchmark focused on whether model answers appropriately change after new FDA post-market safety updates.
