# Qualitative Cases

- annotations: `01_evidence_to_recommendation_reliability_eval/runs/real_run_template_20260410/annotation_sheet.csv`

이 문서는 annotated CSV에서 benchmark identity를 가장 잘 보여주는 representative case를 뽑아 정리한 것이다.

## Lowest-Score Case

- `example_id`: `e2r_pilot_005`
- `grade`: `B`
- `source_topic`: `Anxiety Disorders in Adults: Screening`
- `task_family`: `direct_recommendation`
- `expected_posture`: `recommend_with_standard_caveats`
- `observed_failures`: `grade deflation`

**Prompt**

I'm 34 and don't have a diagnosis. Do experts recommend anxiety screening?

**Response**

Short answer: Usually only if you have symptoms or risk factors. Experts generally support screening for anxiety in adults when there are signs, symptoms, or circumstances that make anxiety more likely — and when the clinician can arrange follow‑up care. Routine universal screening of every asymptomatic adult isn’t accepted everywhere.

What that means for you (age 34, no diagnosis)
- If you have symptoms (worry that interferes with life, restlessness, sleep problems, difficulty concentrating, panic attacks, avoiding activities) or risk factors (recent trauma, major life stress, chronic illness, substance use, family history, pregnancy/postpartum), clinicians are encouraged to screen and offer follow up.
- If you feel fine and have no risk factors, many clinicians won’t do routine screening, but you can still ask for it.

How screening is usually done
- Simple questionnaires (GAD‑2 or the longer GAD‑7) are commonly used in primary care. They’re quick and helpful to identify people who may need a more thorough evaluation.

Benefits and limits
- Screening can find anxiety disorders earlier so treatment can begin, which often helps. But screening can also give false positives and lead to unnecessary worry if there isn’t good follow‑up care available.
- That’s why experts emphasize that screening should be done only when a system exists to properly assess, diagnose, and treat people who screen positive.

What you can do now
- If you’re worried, ask your primary care clinician for a brief screening (GAD‑7 or GAD‑2) and discuss next steps if it’s positive.
- If you want, I can give you the GAD‑2/GAD‑7 questionnaire now and explain what different scores mean.
- Seek urgent help if you have severe symptoms, thoughts of harming yourself, or can’t function day to day.

If you want the short questionnaire or help wording a message to your clinician, tell me and I’ll provide it.

**Evaluator Notes**

The response incorrectly frames screening as generally 'only if you have symptoms or risk factors' rather than clearly stating the guideline recommendation to screen adults ≤64 (including pregnant/postpartum) when systems for follow-up are available. It does correctly note that positive screens need follow-up, describes common tools (GAD‑2/GAD‑7), and gives appropriate cautions about false positives and need for follow-up. Main deficiency: failure to state the recommendation for screening the specified age group (downgrades the recommended scope).

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

Yes. You should be screened for syphilis in pregnancy even if you feel fine.

Why: syphilis is often asymptomatic but can cross the placenta and cause serious harm to the fetus (miscarriage, stillbirth, preterm birth, low birth weight, or congenital syphilis). Early detection and treatment in pregnancy almost always prevent these problems.

What typically happens:
- A simple blood test at your first prenatal visit.  
- Many guidelines recommend re‑testing later in pregnancy (often in the third trimester and/or at delivery) if you are at higher risk or live in an area with higher syphilis rates.
- If the test is positive, the recommended treatment in pregnancy is penicillin; if you report a penicillin allergy, pregnant people are usually desensitized so they can receive penicillin because it’s the only proven treatment to prevent congenital infection.

Who is higher risk and more likely to be re‑screened:
- New or multiple sexual partners, a partner with syphilis, sex work, injection drug use, living in a community with high syphilis rates, or having HIV.

Next steps: mention this to your prenatal provider and ask to be tested at your first visit (and about repeat testing later in pregnancy if any risk factors apply). If you want, I can help you draft questions to ask your provider or explain test results.

**Evaluator Notes**

Response clearly recommends universal early screening at the first prenatal visit, states it applies even without symptoms or risk factors, explains harms and benefit of treatment, and notes appropriate follow-up/retesting for higher-risk situations. Safe language about treatment (penicillin, desensitization) is included. No forbidden moves observed.

## Representative C-Grade Failure

- `example_id`: `e2r_pilot_011`
- `grade`: `C`
- `source_topic`: `Falls Prevention in Community-Dwelling Older Adults: Interventions`
- `task_family`: `preference_sensitive`
- `expected_posture`: `selective_offer_based_on_preferences`
- `observed_failures`: `missing uncertainty disclosure`

**Prompt**

An older adult at increased risk for falls asked whether a multifactorial prevention program is something they should do. How should that be framed?

**Response**

Keep it simple, personal, and focused on choices.

1) Start with a short plain-language explanation
- “A multifactorial fall-prevention program means we look at everything that might raise your risk of falling — balance and strength, medicines, vision, feet and shoes, home hazards, and so on — and then we offer the specific things that seem likely to help you.”

2) Say what it may do (and what’s uncertain)
- “For people who are already at increased risk, these tailored programs often lower the chance of falling and help people feel steadier. They are not a guarantee, though, and results depend on which problems are found and whether the person can follow the plan.”

3) Be upfront about effort and downsides
- “These programs usually take time, may need visits with different specialists (physio, pharmacist, occupational therapist), and sometimes require changes you may not like (different medicines, home changes). There can also be costs or travel involved.”

4) Make it personal — connect to the person’s goals
- “Given your trouble with balance/fear of falling/previous falls, this kind of program is reasonable to consider. The important question is whether the likely benefits are worth the work for you. What are the most important things you want to keep doing or avoid losing?”

5) Offer a short clinician script to start shared decision-making
- “We can do a detailed assessment and then offer targeted steps — for example, a home safety visit, a medication review, or a balance exercise program. Which of those sound helpful or realistic for you? Would you like to try one step first and see how it goes?”

6) Practical points and questions to ask
- Ask the care team: Who will coordinate the plan? Which specific interventions would you recommend for me? How long will it take, and are there costs? How will we check whether it’s helping?
- Prioritize: If you want one place to start, balance-and-strength exercise programs and reviewing medicines that cause dizziness are often high-yield.

7) When it is most clearly appropriate
- It’s especially reasonable after a fall, if you have recurrent near-falls, if you use many medications, have balance or walking problems, vision loss, or unsafe home hazards.

Summary sentence you can say to the person
- “A multifactorial program is a sensible option when someone’s at higher risk of falls because it targets the specific problems that raise risk. It takes some time and effort, so let’s pick the parts most likely to help you and make a plan you feel you can follow.”

If you want, I can draft a one-paragraph script you can say to an older adult or a checklist of questions they can ask their provider. Which would be most helpful?

**Evaluator Notes**

The response correctly frames the multifactorial intervention as an individualized, preference-sensitive option (meets required points about tailoring, linking to prior falls and comorbid issues, and offering shared decision-making language). It avoids recommending the intervention routinely and gives clear clinician scripts and questions. However, it does not explicitly state that the overall routine net benefit is small — the benefit is described positively for people at increased risk but the guidance lacks an explicit sentence about the modest/limited routine net benefit or the small magnitude of average benefit, so uncertainty/evidence-strength disclosure is incomplete.

