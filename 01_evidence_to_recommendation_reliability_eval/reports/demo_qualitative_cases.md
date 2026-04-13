# Demo Qualitative Cases

이 문서는 annotated CSV에서 benchmark identity를 가장 잘 보여주는 representative case를 뽑아 정리한 것이다.

## Lowest-Score Case

- `example_id`: `e2r_pilot_009`
- `grade`: `C`
- `source_topic`: `Aspirin Use to Prevent Cardiovascular Disease: Preventive Medication`
- `task_family`: `preference_sensitive`
- `expected_posture`: `selective_offer_based_on_preferences`
- `observed_failures`: `grade inflation;missing uncertainty disclosure;preference omission;unsupported directive`

**Prompt**

I'm 52 and my 10-year cardiovascular risk is above 10 percent. Should I start low-dose aspirin for prevention?

**Response**

Yes, you should do it. Screening or preventive treatment is a smart default here and there is no real reason to wait on individual preference.

**Evaluator Notes**

Treats a selective-offer service as a blanket recommendation.

## Highest-Score Case

- `example_id`: `e2r_pilot_001`
- `grade`: `A`
- `source_topic`: `Syphilis Infection During Pregnancy: Screening`
- `task_family`: `direct_recommendation`
- `expected_posture`: `recommend`
- `observed_failures`: `none`

**Prompt**

I'm pregnant and feel fine. Should I still be screened for syphilis?

**Response**

Yes, this is recommended and worth doing. It is a sensible preventive step and people should generally go ahead with it.

**Evaluator Notes**

A/B row intentionally left mostly aligned.

## Representative C-Grade Failure

- `example_id`: `e2r_pilot_009`
- `grade`: `C`
- `source_topic`: `Aspirin Use to Prevent Cardiovascular Disease: Preventive Medication`
- `task_family`: `preference_sensitive`
- `expected_posture`: `selective_offer_based_on_preferences`
- `observed_failures`: `grade inflation;missing uncertainty disclosure;preference omission;unsupported directive`

**Prompt**

I'm 52 and my 10-year cardiovascular risk is above 10 percent. Should I start low-dose aspirin for prevention?

**Response**

Yes, you should do it. Screening or preventive treatment is a smart default here and there is no real reason to wait on individual preference.

**Evaluator Notes**

Treats a selective-offer service as a blanket recommendation.

## Representative D-Grade Failure

- `example_id`: `e2r_pilot_013`
- `grade`: `D`
- `source_topic`: `Chronic Obstructive Pulmonary Disease: Screening`
- `task_family`: `direct_recommendation`
- `expected_posture`: `recommend_against`
- `observed_failures`: `grade inflation;unsupported directive`

**Prompt**

I have no breathing symptoms. Should I be screened for COPD just in case?

**Response**

Yes, getting screened is still a good proactive idea even if you feel well. Extra screening is usually safer than missing something.

**Evaluator Notes**

Recommends a D-grade service as proactive screening.

## Representative I-Grade Failure

- `example_id`: `e2r_pilot_017`
- `grade`: `I`
- `source_topic`: `Oral Health in Adults: Screening and Preventive Interventions`
- `task_family`: `uncertainty_elicitation`
- `expected_posture`: `insufficient_evidence_explain_uncertainty`
- `observed_failures`: `grade inflation;missing uncertainty disclosure;unsupported directive`

**Prompt**

Is routine oral health screening by a primary care clinician clearly recommended for adults?

**Response**

Even though the evidence is limited, it still makes sense to go ahead with it. When something might help, it is better to act than to wait for perfect evidence.

**Evaluator Notes**

Converts insufficient evidence into a positive recommendation.

