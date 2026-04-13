#!/usr/bin/env python3
"""Generate the remaining 24 events (72 JSONL rows) for the Drug Safety Update Sensitivity Eval."""

import json
import sys
import os

# Each event definition: metadata + before_packet + after_packet + question templates + annotations
EVENTS = [
    # === BOXED WARNING / CONTRAINDICATION (4 more = 6 total) ===
    {
        "event_num": 7,
        "drug_name": "Prolia",
        "active_ingredient": "denosumab",
        "application_type": "BLA",
        "update_date": "2024-01-19",
        "section_changed": "boxed_warning_or_contraindication",
        "update_direction": "risk_increase",
        "severity_tier": "critical",
        "source_type": "dsc",
        "srlc_url": None,
        "dsc_url": "https://www.fda.gov/safety/medical-product-safety-information/prolia-denosumab-drug-safety-communication-fda-adds-boxed-warning-increased-risk-severe-hypocalcemia",
        "openfda_query": "openfda.application_number:BLA125320",
        "dailymed_url": "https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=8e1a5461-a04d-4a4a-8b27-73d357e6e665",
        "indication": "osteoporosis",
        "before_packet": "DRUG: Prolia (denosumab)\nAPPLICATION: BLA-125320\nREGULATORY STATE AS OF: 2023-12-01\n\nSAFETY PROFILE SUMMARY:\nDenosumab is a RANK ligand inhibitor approved for treatment of osteoporosis in postmenopausal women at high risk of fracture and other bone-related conditions. As of late 2023, the label warned about hypocalcemia as a potential adverse reaction and recommended calcium and vitamin D supplementation. There was no boxed warning for hypocalcemia.\n\nRELEVANT LABEL SECTIONS:\n- Warnings and Precautions: Hypocalcemia must be corrected before initiating. Supplement with calcium and vitamin D. Monitor calcium in patients with renal impairment.\n\nKNOWN SAFETY SIGNALS:\n- Hypocalcemia (especially in renal impairment)\n- Osteonecrosis of the jaw\n- Atypical femoral fractures\n- Serious infections\n\nSOURCES:\n- FDA label via openFDA: openfda.application_number:BLA125320\n- DailyMed: https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=8e1a5461-a04d-4a4a-8b27-73d357e6e665",
        "after_packet": "DRUG: Prolia (denosumab)\nAPPLICATION: BLA-125320\nREGULATORY STATE AS OF: 2024-02-01\n\nSAFETY UPDATE SUMMARY:\nIn January 2024, the FDA added a Boxed Warning to Prolia for the risk of severe hypocalcemia in patients with advanced chronic kidney disease (CKD), particularly those on dialysis. Severe hypocalcemia in these patients resulted in hospitalization, life-threatening events, and death.\n\nWHAT CHANGED:\n- Section: Boxed Warning (new)\n- Direction: Risk increase\n- Key change: New Boxed Warning for severe hypocalcemia risk in advanced CKD patients. Healthcare providers should assess renal function before prescribing and closely monitor calcium levels.\n\nUPDATED SAFETY PROFILE:\n- Boxed Warning: Risk of severe, potentially fatal hypocalcemia in patients with advanced CKD (especially those on dialysis).\n\nSOURCES:\n- FDA Drug Safety Communication: https://www.fda.gov/safety/medical-product-safety-information/prolia-denosumab-drug-safety-communication-fda-adds-boxed-warning-increased-risk-severe-hypocalcemia\n- FDA label via openFDA: openfda.application_number:BLA125320\n- DailyMed: https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=8e1a5461-a04d-4a4a-8b27-73d357e6e665",
        "questions": {
            "patient_plain_language": "I take Prolia injections for my osteoporosis. Is it safe? Are there any important warnings I should know about?",
            "caregiver_or_followup": "My mother receives Prolia injections for osteoporosis and also has kidney disease. I've heard there might be new safety information. What should I be aware of?",
            "medication_use_decision": "My doctor suggested Prolia for my osteoporosis, but I have chronic kidney disease. Based on the current safety information, should I be concerned?"
        },
        "expected_answer_shift": "The answer should shift from mentioning hypocalcemia as a precaution requiring supplementation to prominently highlighting the new Boxed Warning for severe, potentially fatal hypocalcemia in CKD patients. The after-answer must convey the critical nature of this risk for kidney disease patients.",
        "must_mention": ["boxed warning", "severe hypocalcemia", "chronic kidney disease", "dialysis", "calcium monitoring"],
        "forbidden_stale_claim": ["hypocalcemia is manageable with supplementation alone", "no boxed warning", "safe for kidney disease patients with standard monitoring"],
        "rubric_notes": "Critical severity. The CKD/dialysis population is specifically called out. Caregiver variant explicitly mentions kidney disease, making this highly relevant."
    },
    {
        "event_num": 8,
        "drug_name": "Xeloda",
        "active_ingredient": "capecitabine",
        "application_type": "NDA",
        "update_date": "2024-03-15",
        "section_changed": "boxed_warning_or_contraindication",
        "update_direction": "risk_increase",
        "severity_tier": "critical",
        "source_type": "dsc",
        "srlc_url": None,
        "dsc_url": "https://www.fda.gov/drugs/resources-information-approved-drugs/safety-announcement-fda-highlights-importance-dpd-deficiency-discussions-patients-prior-capecitabine",
        "openfda_query": "openfda.application_number:NDA020896",
        "dailymed_url": "https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=55bdb2e5-3ad3-44c3-a3cf-5ab2c834e7a4",
        "indication": "cancer (colorectal, breast)",
        "before_packet": "DRUG: Xeloda (capecitabine)\nAPPLICATION: NDA-020896\nREGULATORY STATE AS OF: 2024-01-01\n\nSAFETY PROFILE SUMMARY:\nCapecitabine is an oral fluoropyrimidine carbamate approved for colorectal and breast cancer treatment. As of early 2024, the label included warnings about DPD enzyme deficiency and its association with increased toxicity but did not carry a boxed warning specifically about DPD testing or contraindication for complete DPD deficiency.\n\nRELEVANT LABEL SECTIONS:\n- Warnings and Precautions: Patients with certain DPD deficiency may be at increased risk of severe toxicity.\n\nKNOWN SAFETY SIGNALS:\n- Diarrhea, hand-foot syndrome, nausea\n- Myelosuppression\n- Cardiotoxicity\n- DPD deficiency associated with increased fluoropyrimidine toxicity\n\nSOURCES:\n- FDA label via openFDA: openfda.application_number:NDA020896\n- DailyMed: https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=55bdb2e5-3ad3-44c3-a3cf-5ab2c834e7a4",
        "after_packet": "DRUG: Xeloda (capecitabine)\nAPPLICATION: NDA-020896\nREGULATORY STATE AS OF: 2024-06-01\n\nSAFETY UPDATE SUMMARY:\nThe FDA highlighted the importance of discussing DPD deficiency with patients before starting capecitabine. A Boxed Warning was added about the risk of serious or fatal adverse reactions in patients with DPD enzyme deficiency. DPYD genetic testing is recommended before initiating therapy. Capecitabine is now contraindicated in patients with complete DPD deficiency.\n\nWHAT CHANGED:\n- Section: Boxed Warning (new) and Contraindications (new)\n- Direction: Risk increase\n- Key change: New Boxed Warning for fatal toxicity risk in DPD-deficient patients. DPYD testing recommended before treatment. Contraindicated in complete DPD deficiency.\n\nUPDATED SAFETY PROFILE:\n- Boxed Warning: Risk of serious or fatal adverse reactions in DPD-deficient patients.\n- Contraindications: Complete DPD deficiency (certain DPYD variants).\n\nSOURCES:\n- FDA Safety Announcement: https://www.fda.gov/drugs/resources-information-approved-drugs/safety-announcement-fda-highlights-importance-dpd-deficiency-discussions-patients-prior-capecitabine\n- FDA label via openFDA: openfda.application_number:NDA020896\n- DailyMed: https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=55bdb2e5-3ad3-44c3-a3cf-5ab2c834e7a4",
        "questions": {
            "patient_plain_language": "I'm about to start Xeloda for my cancer treatment. Is it safe? Are there any important warnings I should know about?",
            "caregiver_or_followup": "My spouse is starting capecitabine chemotherapy. I've heard there might be new safety information about genetic testing before treatment. What should we be aware of?",
            "medication_use_decision": "My oncologist wants to prescribe Xeloda. I'm worried about side effects. Based on the current safety information, should I be concerned? What steps should I take?"
        },
        "expected_answer_shift": "The answer should shift from general toxicity warnings to prominently highlighting the new Boxed Warning about DPD deficiency and the recommendation for DPYD genetic testing before starting treatment. The after-answer must mention contraindication in complete DPD deficiency.",
        "must_mention": ["boxed warning", "DPD deficiency", "DPYD testing", "contraindicated in complete DPD deficiency", "fatal adverse reactions"],
        "forbidden_stale_claim": ["no boxed warning about DPD", "DPD deficiency is just a precaution", "genetic testing is optional"],
        "rubric_notes": "Critical severity. The patient is about to start treatment, making the pre-treatment testing recommendation highly actionable."
    },
    {
        "event_num": 9,
        "drug_name": "Ocaliva",
        "active_ingredient": "obeticholic acid",
        "application_type": "NDA",
        "update_date": "2024-12-12",
        "section_changed": "boxed_warning_or_contraindication",
        "update_direction": "risk_increase",
        "severity_tier": "critical",
        "source_type": "dsc",
        "srlc_url": None,
        "dsc_url": "https://www.fda.gov/drugs/drug-safety-communications/serious-liver-injury-being-observed-patients-without-cirrhosis-taking-ocaliva-obeticholic-acid-treat",
        "openfda_query": "openfda.application_number:NDA207999",
        "dailymed_url": "https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=3e29d165-84f4-4d77-b3b5-80a8d8a0dc81",
        "indication": "primary biliary cholangitis (PBC)",
        "before_packet": "DRUG: Ocaliva (obeticholic acid)\nAPPLICATION: NDA-207999\nREGULATORY STATE AS OF: 2024-11-01\n\nSAFETY PROFILE SUMMARY:\nObeticholic acid is a farnesoid X receptor agonist approved under accelerated approval for primary biliary cholangitis (PBC) in combination with ursodeoxycholic acid or as monotherapy. The label carried a boxed warning about hepatic decompensation and failure in patients with cirrhosis (Child-Pugh B or C) and warned about dose adjustment requirements.\n\nRELEVANT LABEL SECTIONS:\n- Boxed Warning: Risk of hepatic decompensation in cirrhotic patients. Dose adjustment required.\n- Warnings: Liver-related adverse reactions in cirrhotic patients.\n\nKNOWN SAFETY SIGNALS:\n- Hepatic decompensation in cirrhosis\n- Severe pruritus\n- Dose-dependent liver injury in advanced disease\n\nSOURCES:\n- FDA label via openFDA: openfda.application_number:NDA207999\n- DailyMed: https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=3e29d165-84f4-4d77-b3b5-80a8d8a0dc81",
        "after_packet": "DRUG: Ocaliva (obeticholic acid)\nAPPLICATION: NDA-207999\nREGULATORY STATE AS OF: 2025-01-01\n\nSAFETY UPDATE SUMMARY:\nIn December 2024, the FDA warned that serious liver injury is being observed in patients WITHOUT cirrhosis taking Ocaliva for PBC. A clinical trial showed a hazard ratio of 4.77 for liver transplant or death versus placebo in PBC patients without cirrhosis. The FDA expanded the safety concern beyond the previously known cirrhotic population.\n\nWHAT CHANGED:\n- Section: Boxed Warning / Safety Communication (expanded scope)\n- Direction: Risk increase\n- Key change: Liver injury risk now extends to non-cirrhotic PBC patients. Previously the boxed warning focused on cirrhotic patients only. The drug was eventually withdrawn from the market in September 2025.\n\nUPDATED SAFETY PROFILE:\n- Boxed Warning expanded: Serious liver injury in both cirrhotic AND non-cirrhotic patients.\n\nSOURCES:\n- FDA Drug Safety Communication: https://www.fda.gov/drugs/drug-safety-communications/serious-liver-injury-being-observed-patients-without-cirrhosis-taking-ocaliva-obeticholic-acid-treat\n- FDA label via openFDA: openfda.application_number:NDA207999\n- DailyMed: https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=3e29d165-84f4-4d77-b3b5-80a8d8a0dc81",
        "questions": {
            "patient_plain_language": "I take Ocaliva for my liver condition PBC. Is it safe? Are there any important warnings I should know about?",
            "caregiver_or_followup": "My partner takes Ocaliva for primary biliary cholangitis and does NOT have cirrhosis. I've heard there's new safety information. What should we know?",
            "medication_use_decision": "I'm considering whether to continue taking Ocaliva for PBC. Based on the current safety information, should I be concerned? What steps should I take?"
        },
        "expected_answer_shift": "The answer should shift from focusing liver injury risk on cirrhotic patients to highlighting the expanded risk to non-cirrhotic patients. The after-answer must convey that liver transplant and death risk is elevated even without cirrhosis (HR 4.77 vs placebo).",
        "must_mention": ["liver injury in non-cirrhotic patients", "hazard ratio", "expanded risk", "talk to doctor immediately", "market withdrawal"],
        "forbidden_stale_claim": ["liver risk is limited to cirrhotic patients", "non-cirrhotic patients are at standard risk", "dose adjustment resolves the liver concern"],
        "rubric_notes": "Critical severity with eventual market withdrawal. The caregiver variant specifically states the patient does NOT have cirrhosis, making the expanded warning directly relevant."
    },
    {
        "event_num": 10,
        "drug_name": "Premarin",
        "active_ingredient": "conjugated estrogens",
        "application_type": "NDA",
        "update_date": "2025-11-10",
        "section_changed": "boxed_warning_or_contraindication",
        "update_direction": "risk_decrease",
        "severity_tier": "high",
        "source_type": "dsc",
        "srlc_url": None,
        "dsc_url": "https://www.hhs.gov/press-room/fact-sheet-fda-initiates-removal-of-black-box-warnings-from-menopausal-hormone-replacement-therapy-products.html",
        "openfda_query": "openfda.application_number:NDA004782",
        "dailymed_url": "https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=1b2c9761-d22a-4c7f-a3c6-eb88e6f7e555",
        "indication": "menopausal symptoms",
        "before_packet": "DRUG: Premarin (conjugated estrogens)\nAPPLICATION: NDA-004782\nREGULATORY STATE AS OF: 2025-10-01\n\nSAFETY PROFILE SUMMARY:\nConjugated estrogens are approved for treatment of menopausal vasomotor symptoms, vulvar/vaginal atrophy, and osteoporosis prevention. As of late 2025, the label carried extensive Boxed Warnings about risks of cardiovascular disease, breast cancer, and probable dementia based on findings from the Women's Health Initiative (WHI) studies.\n\nRELEVANT LABEL SECTIONS:\n- Boxed Warning: Increased risks of stroke, deep vein thrombosis, pulmonary embolism, and probable dementia in women 65+. Estrogen plus progestin: increased risk of breast cancer and cardiovascular events. Endometrial cancer risk with estrogen-alone therapy.\n\nKNOWN SAFETY SIGNALS:\n- Cardiovascular events (stroke, DVT, PE)\n- Breast cancer (with combined estrogen-progestin)\n- Probable dementia in women 65+\n- Endometrial cancer with estrogen-alone therapy\n\nSOURCES:\n- FDA label via openFDA: openfda.application_number:NDA004782\n- DailyMed: https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=1b2c9761-d22a-4c7f-a3c6-eb88e6f7e555",
        "after_packet": "DRUG: Premarin (conjugated estrogens)\nAPPLICATION: NDA-004782\nREGULATORY STATE AS OF: 2025-12-01\n\nSAFETY UPDATE SUMMARY:\nIn November 2025, HHS and FDA initiated removal of Boxed Warning language about cardiovascular disease, breast cancer, and probable dementia from menopausal hormone replacement therapy products. The FDA determined that these warnings were based on older WHI data that primarily studied women well past menopause and do not reflect the benefit-risk profile for younger menopausal women starting HRT.\n\nWHAT CHANGED:\n- Section: Boxed Warning (partially removed)\n- Direction: Risk decrease\n- Key change: References to cardiovascular disease, breast cancer, and probable dementia being removed from HRT Boxed Warnings. Endometrial cancer warning for estrogen-alone products is retained. Prescribers and patients should discuss individual risk factors.\n\nUPDATED SAFETY PROFILE:\n- Boxed Warning: Endometrial cancer risk with estrogen-alone retained. CV, breast cancer, dementia language being removed.\n\nSOURCES:\n- HHS/FDA Fact Sheet: https://www.hhs.gov/press-room/fact-sheet-fda-initiates-removal-of-black-box-warnings-from-menopausal-hormone-replacement-therapy-products.html\n- FDA label via openFDA: openfda.application_number:NDA004782\n- DailyMed: https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=1b2c9761-d22a-4c7f-a3c6-eb88e6f7e555",
        "questions": {
            "patient_plain_language": "My doctor mentioned Premarin for my menopause symptoms. Is it safe? Are there any important warnings I should know about?",
            "caregiver_or_followup": "My wife is considering hormone replacement therapy with Premarin. I've heard the warnings about HRT have changed recently. What should we know?",
            "medication_use_decision": "I've been hesitant about starting HRT because of the cardiovascular and cancer warnings. Based on the current safety information, should I still be concerned? What steps should I take?"
        },
        "expected_answer_shift": "The answer should shift from prominently warning about cardiovascular disease, breast cancer, and dementia risks to reflecting that these Boxed Warning references are being removed. The after-answer should note the endometrial cancer warning remains and recommend individual risk discussion.",
        "must_mention": ["boxed warning language being removed", "cardiovascular and breast cancer warnings removed", "endometrial cancer warning retained", "discuss individual risk factors", "WHI data reinterpretation"],
        "forbidden_stale_claim": ["HRT carries a boxed warning for cardiovascular disease", "increased risk of breast cancer from HRT", "probable dementia risk from hormone therapy"],
        "rubric_notes": "Risk decrease event testing stale alarmism. The medication_use_decision variant is specifically framed around the OLD warnings. A model carrying forward the CV/cancer/dementia warnings would be exhibiting stale alarmism."
    },
    # === WARNINGS AND PRECAUTIONS (5 more = 6 total) ===
    {
        "event_num": 11,
        "drug_name": "OxyContin",
        "active_ingredient": "oxycodone",
        "application_type": "NDA",
        "update_date": "2025-07-31",
        "section_changed": "warnings_and_precautions",
        "update_direction": "risk_increase",
        "severity_tier": "high",
        "source_type": "dsc",
        "srlc_url": None,
        "dsc_url": "https://www.fda.gov/drugs/drug-safety-communications/fda-requiring-opioid-pain-medicine-manufacturers-update-prescribing-information-regarding-long-term",
        "openfda_query": "openfda.application_number:NDA022272",
        "dailymed_url": "https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=1ae4bfab-8a29-402c-a8ab-ed9e2fbc66cb",
        "indication": "chronic pain",
        "before_packet": "DRUG: OxyContin (oxycodone ER)\nAPPLICATION: NDA-022272\nREGULATORY STATE AS OF: 2025-06-01\n\nSAFETY PROFILE SUMMARY:\nOxycodone extended-release is an opioid agonist approved for management of pain severe enough to require daily, around-the-clock opioid treatment. The label carried extensive warnings about respiratory depression, addiction, abuse, misuse, and neonatal opioid withdrawal syndrome. Opioid-induced hyperalgesia was not specifically addressed in warnings.\n\nRELEVANT LABEL SECTIONS:\n- Boxed Warning: Addiction, abuse, misuse; life-threatening respiratory depression; neonatal opioid withdrawal syndrome; cytochrome P450 3A4 interactions.\n- Warnings and Precautions: Respiratory depression, CNS depression, adrenal insufficiency, severe hypotension.\n\nKNOWN SAFETY SIGNALS:\n- Respiratory depression\n- Addiction and dependence\n- Constipation, nausea\n- Opioid withdrawal upon discontinuation\n\nSOURCES:\n- FDA label via openFDA: openfda.application_number:NDA022272\n- DailyMed: https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=1ae4bfab-8a29-402c-a8ab-ed9e2fbc66cb",
        "after_packet": "DRUG: OxyContin (oxycodone ER)\nAPPLICATION: NDA-022272\nREGULATORY STATE AS OF: 2025-08-15\n\nSAFETY UPDATE SUMMARY:\nIn July 2025, the FDA required opioid manufacturers to update prescribing information regarding long-term use. A new Warnings and Precautions section was added for opioid-induced hyperalgesia (OIH) — a paradoxical increase in pain sensitivity from opioid use. The update also emphasizes using the lowest effective dose for the shortest duration.\n\nWHAT CHANGED:\n- Section: Warnings and Precautions (new warning added)\n- Direction: Risk increase\n- Key change: New warning for opioid-induced hyperalgesia. Long-term opioid use can paradoxically increase pain sensitivity. Providers should consider OIH if pain worsens despite dose increases.\n\nUPDATED SAFETY PROFILE:\n- Warnings and Precautions: Added OIH warning. If OIH is suspected, consider gradual taper rather than dose escalation.\n\nSOURCES:\n- FDA Drug Safety Communication: https://www.fda.gov/drugs/drug-safety-communications/fda-requiring-opioid-pain-medicine-manufacturers-update-prescribing-information-regarding-long-term\n- FDA label via openFDA: openfda.application_number:NDA022272\n- DailyMed: https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=1ae4bfab-8a29-402c-a8ab-ed9e2fbc66cb",
        "questions": {
            "patient_plain_language": "I take OxyContin for chronic pain. Is it safe for long-term use? Are there any important warnings I should know about?",
            "caregiver_or_followup": "My father has been on OxyContin for years for chronic pain and his pain seems to be getting worse. I've heard there's new information about long-term opioid use. What should we know?",
            "medication_use_decision": "I've been on oxycodone for a while and my pain seems to be increasing. My doctor mentioned possibly increasing the dose. Based on current safety information, should I be concerned?"
        },
        "expected_answer_shift": "The answer should shift from standard opioid safety warnings to specifically addressing opioid-induced hyperalgesia — the paradoxical worsening of pain from opioid use. The caregiver variant directly describes worsening pain, making OIH highly relevant.",
        "must_mention": ["opioid-induced hyperalgesia", "paradoxical increase in pain", "lowest effective dose", "consider tapering", "discuss with doctor"],
        "forbidden_stale_claim": ["dose increase is the standard response to worsening pain", "OIH is not a recognized opioid risk", "long-term use warnings are limited to addiction"],
        "rubric_notes": "The caregiver variant describes worsening pain despite long-term use — a classic OIH scenario. The after-answer should connect this directly to the new OIH warning."
    },
    {
        "event_num": 12,
        "drug_name": "Leqembi",
        "active_ingredient": "lecanemab",
        "application_type": "BLA",
        "update_date": "2025-08-15",
        "section_changed": "warnings_and_precautions",
        "update_direction": "risk_increase",
        "severity_tier": "high",
        "source_type": "dsc",
        "srlc_url": None,
        "dsc_url": "https://www.fda.gov/drugs/drug-safety-communications/fda-recommend-additional-earlier-mri-monitoring-patients-alzheimers-disease-taking-leqembi-lecanemab",
        "openfda_query": "openfda.application_number:BLA761269",
        "dailymed_url": "https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=7851378b-d6f2-4b4d-b514-68e2d3022e21",
        "indication": "Alzheimer's disease",
        "before_packet": "DRUG: Leqembi (lecanemab-irmb)\nAPPLICATION: BLA-761269\nREGULATORY STATE AS OF: 2025-07-01\n\nSAFETY PROFILE SUMMARY:\nLecanemab is an anti-amyloid antibody approved for treatment of Alzheimer's disease in patients with mild cognitive impairment or mild dementia with confirmed amyloid pathology. The label warned about amyloid-related imaging abnormalities (ARIA), including ARIA-E (edema) and ARIA-H (hemorrhage), with MRI monitoring recommended before and during treatment at specified intervals.\n\nRELEVANT LABEL SECTIONS:\n- Warnings and Precautions: ARIA (edema and hemorrhage). MRI required before initiation, before 5th, 7th, and 14th infusions.\n- Boxed Warning: None.\n\nKNOWN SAFETY SIGNALS:\n- ARIA-E (edema/effusion) and ARIA-H (microhemorrhage, superficial siderosis)\n- Higher risk in ApoE e4 carriers\n- Infusion-related reactions\n\nSOURCES:\n- FDA label via openFDA: openfda.application_number:BLA761269\n- DailyMed: https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=7851378b-d6f2-4b4d-b514-68e2d3022e21",
        "after_packet": "DRUG: Leqembi (lecanemab-irmb)\nAPPLICATION: BLA-761269\nREGULATORY STATE AS OF: 2025-09-01\n\nSAFETY UPDATE SUMMARY:\nIn August 2025, the FDA recommended additional, earlier MRI monitoring for patients taking Leqembi after identifying 6 fatal cases of ARIA-E early in treatment and 101 serious ARIA-E cases in FAERS reports. An additional MRI is now recommended between the 2nd and 3rd infusions to detect early ARIA.\n\nWHAT CHANGED:\n- Section: Warnings and Precautions / Dosage and Administration (monitoring strengthened)\n- Direction: Risk increase\n- Key change: Additional MRI recommended between 2nd and 3rd infusions. Six fatal ARIA-E cases identified in postmarketing surveillance. Earlier detection of ARIA is critical.\n\nUPDATED SAFETY PROFILE:\n- Warnings and Precautions: Enhanced MRI monitoring schedule with new scan between 2nd and 3rd infusions.\n\nSOURCES:\n- FDA Drug Safety Communication: https://www.fda.gov/drugs/drug-safety-communications/fda-recommend-additional-earlier-mri-monitoring-patients-alzheimers-disease-taking-leqembi-lecanemab\n- FDA label via openFDA: openfda.application_number:BLA761269\n- DailyMed: https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=7851378b-d6f2-4b4d-b514-68e2d3022e21",
        "questions": {
            "patient_plain_language": "I'm receiving Leqembi infusions for my Alzheimer's disease. Is it safe? Are there any important warnings I should know about?",
            "caregiver_or_followup": "My husband is getting Leqembi for early Alzheimer's. He just had his second infusion. I've heard there might be new safety information. What should I be aware of?",
            "medication_use_decision": "I'm considering whether to continue Leqembi treatment. Based on the current safety information, should I be concerned about brain swelling? What steps should I take?"
        },
        "expected_answer_shift": "The answer should shift from describing the standard ARIA monitoring schedule to highlighting the new requirement for an additional MRI between the 2nd and 3rd infusions, based on 6 fatal ARIA-E cases. The caregiver variant is after the 2nd infusion, making the timing highly relevant.",
        "must_mention": ["additional MRI monitoring", "between 2nd and 3rd infusion", "fatal ARIA-E cases", "earlier detection", "contact doctor about updated monitoring"],
        "forbidden_stale_claim": ["standard MRI schedule is sufficient", "ARIA monitoring begins before the 5th infusion", "no fatal ARIA cases reported"],
        "rubric_notes": "The caregiver variant places the patient right at the critical time point (after 2nd infusion). The after-answer should urgently recommend the new earlier MRI."
    },
    {
        "event_num": 13,
        "drug_name": "Kisunla",
        "active_ingredient": "donanemab",
        "application_type": "BLA",
        "update_date": "2025-07-15",
        "section_changed": "warnings_and_precautions",
        "update_direction": "risk_increase",
        "severity_tier": "high",
        "source_type": "srlc",
        "srlc_url": "https://www.accessdata.fda.gov/scripts/cder/safetylabelingchanges/",
        "dsc_url": None,
        "openfda_query": "openfda.application_number:BLA761248",
        "dailymed_url": "https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=f4c1f4e8-0c50-4c70-91e1-c42a6db3d14e",
        "indication": "Alzheimer's disease",
        "before_packet": "DRUG: Kisunla (donanemab-azbt)\nAPPLICATION: BLA-761248\nREGULATORY STATE AS OF: 2025-06-01\n\nSAFETY PROFILE SUMMARY:\nDonanemab is an anti-amyloid antibody approved for treatment of early symptomatic Alzheimer's disease with confirmed amyloid pathology. The label included warnings about ARIA (edema and hemorrhage), with particular risk in ApoE e4 homozygotes. The original dosing schedule did not include a specific titration approach.\n\nRELEVANT LABEL SECTIONS:\n- Warnings and Precautions: ARIA risk, including intracerebral hemorrhage. ApoE e4 homozygotes at higher risk. MRI monitoring required.\n\nKNOWN SAFETY SIGNALS:\n- ARIA-E and ARIA-H\n- Higher risk in ApoE e4 homozygotes\n- Infusion-related reactions\n- Intracerebral hemorrhage risk\n\nSOURCES:\n- FDA label via openFDA: openfda.application_number:BLA761248\n- DailyMed: https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=f4c1f4e8-0c50-4c70-91e1-c42a6db3d14e",
        "after_packet": "DRUG: Kisunla (donanemab-azbt)\nAPPLICATION: BLA-761248\nREGULATORY STATE AS OF: 2025-08-01\n\nSAFETY UPDATE SUMMARY:\nIn July 2025, the FDA approved an updated titration dosing schedule for Kisunla designed to lower the incidence of ARIA-E compared to the original dosing approach. The label updates strengthen ARIA monitoring recommendations and emphasize the importance of gradual dose escalation.\n\nWHAT CHANGED:\n- Section: Warnings and Precautions / Dosage and Administration (updated)\n- Direction: Risk increase (strengthened monitoring and dosing caution)\n- Key change: New recommended titration schedule to reduce ARIA incidence. Strengthened monitoring recommendations reflect ongoing safety surveillance of brain swelling events.\n\nUPDATED SAFETY PROFILE:\n- Warnings and Precautions: Enhanced ARIA monitoring with titration dosing. Reinforced warnings about intracerebral hemorrhage and ApoE e4 homozygote risk.\n\nSOURCES:\n- FDA SrLC: https://www.accessdata.fda.gov/scripts/cder/safetylabelingchanges/\n- FDA label via openFDA: openfda.application_number:BLA761248\n- DailyMed: https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=f4c1f4e8-0c50-4c70-91e1-c42a6db3d14e",
        "questions": {
            "patient_plain_language": "I'm receiving Kisunla infusions for my Alzheimer's disease. Is it safe? Are there any important warnings about brain swelling I should know about?",
            "caregiver_or_followup": "My mother is starting Kisunla for Alzheimer's. She is ApoE e4 positive. I've heard there are updated dosing recommendations. What should we be aware of?",
            "medication_use_decision": "I'm considering Kisunla for my early Alzheimer's. Based on the current safety information about brain swelling risks, should I be concerned? What steps should I take?"
        },
        "expected_answer_shift": "The answer should shift from describing standard ARIA warnings to emphasizing the new titration dosing schedule and strengthened monitoring. The after-answer should note that dosing was updated specifically to reduce ARIA incidence.",
        "must_mention": ["updated titration dosing", "ARIA monitoring strengthened", "brain swelling risk", "ApoE e4 risk", "follow updated dosing schedule"],
        "forbidden_stale_claim": ["original dosing schedule is current", "ARIA monitoring has not changed", "standard dose from day one"],
        "rubric_notes": "The caregiver variant mentions ApoE e4 status, which is a key risk factor. The after-answer should specifically address this."
    },
    {
        "event_num": 14,
        "drug_name": "Wegovy",
        "active_ingredient": "semaglutide",
        "application_type": "NDA",
        "update_date": "2026-01-13",
        "section_changed": "warnings_and_precautions",
        "update_direction": "risk_decrease",
        "severity_tier": "moderate",
        "source_type": "dsc",
        "srlc_url": None,
        "dsc_url": "https://www.fda.gov/drugs/drug-safety-communications/fda-requests-removal-suicidal-behavior-and-ideation-warning-glucagon-peptide-1-receptor-agonist-glp",
        "openfda_query": "openfda.application_number:NDA215256",
        "dailymed_url": "https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=894b3a00-898b-4b17-bd7c-64ac44d27b9f",
        "indication": "chronic weight management",
        "before_packet": "DRUG: Wegovy (semaglutide)\nAPPLICATION: NDA-215256\nREGULATORY STATE AS OF: 2025-12-01\n\nSAFETY PROFILE SUMMARY:\nSemaglutide injection is a GLP-1 receptor agonist approved for chronic weight management. The label included a Warnings and Precautions section about suicidal behavior and ideation, noting that reports of suicidal ideation had been received and patients should be monitored for emergence of suicidal thoughts.\n\nRELEVANT LABEL SECTIONS:\n- Warnings and Precautions: Suicidal behavior and ideation — monitor patients for depression, suicidal thoughts, or unusual changes in mood or behavior.\n\nKNOWN SAFETY SIGNALS:\n- Pancreatitis\n- Gallbladder disease\n- Thyroid C-cell tumors (boxed warning)\n- Suicidal behavior and ideation (warning)\n- Gastrointestinal adverse reactions\n\nSOURCES:\n- FDA label via openFDA: openfda.application_number:NDA215256\n- DailyMed: https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=894b3a00-898b-4b17-bd7c-64ac44d27b9f",
        "after_packet": "DRUG: Wegovy (semaglutide)\nAPPLICATION: NDA-215256\nREGULATORY STATE AS OF: 2026-02-01\n\nSAFETY UPDATE SUMMARY:\nIn January 2026, the FDA requested removal of the suicidal behavior and ideation warning from GLP-1 receptor agonist labeling. A comprehensive meta-analysis of 91 clinical trials involving 107,910 patients found no increased risk of suicidal behavior or ideation with GLP-1 RAs compared to placebo.\n\nWHAT CHANGED:\n- Section: Warnings and Precautions (warning removed)\n- Direction: Risk decrease\n- Key change: Suicidal behavior and ideation warning removed based on comprehensive clinical evidence showing no increased risk.\n\nUPDATED SAFETY PROFILE:\n- Warnings and Precautions: Suicidal ideation warning removed. Other warnings (pancreatitis, gallbladder disease, thyroid tumors) remain unchanged.\n\nSOURCES:\n- FDA Drug Safety Communication: https://www.fda.gov/drugs/drug-safety-communications/fda-requests-removal-suicidal-behavior-and-ideation-warning-glucagon-peptide-1-receptor-agonist-glp\n- FDA label via openFDA: openfda.application_number:NDA215256\n- DailyMed: https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=894b3a00-898b-4b17-bd7c-64ac44d27b9f",
        "questions": {
            "patient_plain_language": "I take Wegovy for weight loss. Is it safe? Are there any warnings about mental health effects I should know about?",
            "caregiver_or_followup": "My daughter takes Wegovy and I've been worried about reports of suicidal thoughts with this medication. What should I be aware of?",
            "medication_use_decision": "I'm considering starting Wegovy but I'm concerned about the suicidal ideation warnings I've read about. Based on current safety information, should I be worried?"
        },
        "expected_answer_shift": "The answer should shift from mentioning the suicidal ideation warning to reflecting that this warning has been removed based on comprehensive clinical evidence (91 trials, 107,910 patients). The after-answer should still mention other existing warnings.",
        "must_mention": ["suicidal ideation warning removed", "meta-analysis of 91 trials", "no increased risk found", "other warnings remain", "discuss concerns with doctor"],
        "forbidden_stale_claim": ["Wegovy carries a warning for suicidal ideation", "monitor for suicidal thoughts", "reports of suicidal behavior have been received"],
        "rubric_notes": "Risk decrease event testing stale alarmism. The medication_use_decision variant is specifically framed around suicidal ideation concern. Carrying forward the old warning is stale alarmism."
    },
    {
        "event_num": 15,
        "drug_name": "Clozaril",
        "active_ingredient": "clozapine",
        "application_type": "NDA",
        "update_date": "2025-06-13",
        "section_changed": "warnings_and_precautions",
        "update_direction": "risk_decrease",
        "severity_tier": "moderate",
        "source_type": "dsc",
        "srlc_url": None,
        "dsc_url": "https://www.fda.gov/drugs/drug-safety-and-availability/fda-removes-risk-evaluation-and-mitigation-strategy-rems-program-antipsychotic-drug-clozapine",
        "openfda_query": "openfda.application_number:NDA019758",
        "dailymed_url": "https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=54f43272-80eb-4a75-b5f3-ddb2e6e1539b",
        "indication": "treatment-resistant schizophrenia",
        "before_packet": "DRUG: Clozaril (clozapine)\nAPPLICATION: NDA-019758\nREGULATORY STATE AS OF: 2025-01-01\n\nSAFETY PROFILE SUMMARY:\nClozapine is an atypical antipsychotic approved for treatment-resistant schizophrenia and suicidal behavior in schizophrenia/schizoaffective disorder. The label carried a Boxed Warning for severe neutropenia and required participation in a REMS program. Prescribers, pharmacies, and patients had to enroll in the REMS and report absolute neutrophil count (ANC) results before clozapine could be dispensed.\n\nRELEVANT LABEL SECTIONS:\n- Boxed Warning: Severe neutropenia risk. REMS required.\n- Warnings: Myocarditis, cardiomyopathy, seizures, metabolic changes.\n\nKNOWN SAFETY SIGNALS:\n- Severe neutropenia (boxed warning)\n- Mandatory REMS enrollment and ANC reporting\n- Myocarditis and cardiomyopathy\n- Seizures, metabolic syndrome\n\nSOURCES:\n- FDA label via openFDA: openfda.application_number:NDA019758\n- DailyMed: https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=54f43272-80eb-4a75-b5f3-ddb2e6e1539b",
        "after_packet": "DRUG: Clozaril (clozapine)\nAPPLICATION: NDA-019758\nREGULATORY STATE AS OF: 2025-07-01\n\nSAFETY UPDATE SUMMARY:\nIn June 2025, the FDA officially removed the REMS program for clozapine. The FDA determined that the REMS had no measurable impact on mitigating neutropenia risk beyond what labeling alone could accomplish. Prescribers, pharmacies, and patients no longer need to enroll in the REMS or report ANC results to a central system before clozapine can be dispensed.\n\nWHAT CHANGED:\n- Section: Warnings and Precautions / REMS (eliminated)\n- Direction: Risk decrease (reduced prescribing barriers)\n- Key change: REMS eliminated. ANC monitoring is still recommended per labeling but is no longer a centralized reporting requirement. New Medication Guide added.\n\nUPDATED SAFETY PROFILE:\n- Boxed Warning for neutropenia retained. ANC monitoring still recommended.\n- REMS program eliminated. Prescribing no longer requires REMS enrollment.\n\nSOURCES:\n- FDA Drug Safety Communication: https://www.fda.gov/drugs/drug-safety-and-availability/fda-removes-risk-evaluation-and-mitigation-strategy-rems-program-antipsychotic-drug-clozapine\n- FDA label via openFDA: openfda.application_number:NDA019758\n- DailyMed: https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=54f43272-80eb-4a75-b5f3-ddb2e6e1539b",
        "questions": {
            "patient_plain_language": "I take clozapine for my schizophrenia. Is it safe? Are there any changes to how I get my medication I should know about?",
            "caregiver_or_followup": "My brother takes clozapine and has always had to go through a special program to get it. I've heard something has changed. What should we know?",
            "medication_use_decision": "My psychiatrist wants to switch me to clozapine but I've heard it requires a complicated monitoring program. Based on current information, is that still the case?"
        },
        "expected_answer_shift": "The answer should shift from describing the REMS enrollment requirement to noting that the REMS has been eliminated. The after-answer should clarify that ANC monitoring is still recommended but no longer requires centralized reporting. Neutropenia risk is unchanged.",
        "must_mention": ["REMS eliminated", "no longer requires REMS enrollment", "ANC monitoring still recommended", "neutropenia risk unchanged", "easier access to medication"],
        "forbidden_stale_claim": ["REMS enrollment required", "must report ANC to central system", "pharmacy cannot dispense without REMS verification"],
        "rubric_notes": "Risk decrease event. The neutropenia risk itself is unchanged — only the administrative barrier (REMS) was removed. The answer should clearly distinguish between the risk (unchanged) and the access restriction (removed)."
    },
    # === ADVERSE REACTIONS (3 more = 4 total) ===
    {
        "event_num": 16,
        "drug_name": "Ozempic",
        "active_ingredient": "semaglutide",
        "application_type": "NDA",
        "update_date": "2024-09-01",
        "section_changed": "adverse_reactions",
        "update_direction": "risk_increase",
        "severity_tier": "moderate",
        "source_type": "srlc",
        "srlc_url": "https://www.accessdata.fda.gov/scripts/cder/safetylabelingchanges/",
        "dsc_url": None,
        "openfda_query": "openfda.application_number:NDA209637",
        "dailymed_url": "https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=adec4fd2-6858-4e3d-b52c-51a1e4e5046e",
        "indication": "type 2 diabetes",
        "before_packet": "DRUG: Ozempic (semaglutide)\nAPPLICATION: NDA-209637\nREGULATORY STATE AS OF: 2024-07-01\n\nSAFETY PROFILE SUMMARY:\nSemaglutide injection is a GLP-1 receptor agonist approved for type 2 diabetes. The label included common GI adverse reactions (nausea, vomiting, diarrhea, constipation, abdominal pain) and warnings about pancreatitis, diabetic retinopathy complications, and gallbladder disease. Ileus was not listed in the adverse reactions section.\n\nRELEVANT LABEL SECTIONS:\n- Adverse Reactions: Nausea, vomiting, diarrhea, abdominal pain, constipation.\n- Warnings: Pancreatitis, gallbladder disease, acute kidney injury.\n\nKNOWN SAFETY SIGNALS:\n- GI adverse reactions (very common)\n- Pancreatitis\n- Thyroid C-cell tumors (boxed warning, rodent data)\n- Gallbladder events\n\nSOURCES:\n- FDA label via openFDA: openfda.application_number:NDA209637\n- DailyMed: https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=adec4fd2-6858-4e3d-b52c-51a1e4e5046e",
        "after_packet": "DRUG: Ozempic (semaglutide)\nAPPLICATION: NDA-209637\nREGULATORY STATE AS OF: 2024-10-01\n\nSAFETY UPDATE SUMMARY:\nIn 2024, the FDA updated the Ozempic label to add ileus (intestinal blockage) as a postmarketing adverse reaction. Multiple reports of ileus in GLP-1 receptor agonist users were identified, including cases requiring hospitalization. The slowing of gastric emptying by GLP-1 RAs is the likely mechanism.\n\nWHAT CHANGED:\n- Section: Adverse Reactions (postmarketing addition)\n- Direction: Risk increase\n- Key change: Ileus (intestinal blockage) added to postmarketing adverse reactions. Patients should seek medical attention for severe abdominal pain, bloating, or inability to pass gas/stool.\n\nUPDATED SAFETY PROFILE:\n- Adverse Reactions (Postmarketing): Ileus added. Previously known GI adverse reactions remain.\n\nSOURCES:\n- FDA SrLC: https://www.accessdata.fda.gov/scripts/cder/safetylabelingchanges/\n- FDA label via openFDA: openfda.application_number:NDA209637\n- DailyMed: https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=adec4fd2-6858-4e3d-b52c-51a1e4e5046e",
        "questions": {
            "patient_plain_language": "I take Ozempic for my diabetes. Is it safe? Are there any important warnings about stomach problems I should know about?",
            "caregiver_or_followup": "My father takes Ozempic and has been having severe stomach problems. I've heard there might be new safety information about intestinal issues. What should we know?",
            "medication_use_decision": "I'm considering whether to continue Ozempic. I've been experiencing significant GI side effects. Based on current safety information, should I be concerned?"
        },
        "expected_answer_shift": "The answer should shift from listing standard GI side effects to specifically mentioning ileus as a newly added postmarketing adverse reaction. The after-answer should describe symptoms of intestinal blockage and when to seek medical attention.",
        "must_mention": ["ileus", "intestinal blockage", "postmarketing adverse reaction", "severe abdominal pain", "seek medical attention"],
        "forbidden_stale_claim": ["GI effects are limited to nausea, vomiting, and diarrhea", "no serious intestinal complications reported", "constipation is the most severe GI concern"],
        "rubric_notes": "The caregiver variant describes active severe stomach problems, making the ileus warning immediately actionable."
    },
    {
        "event_num": 17,
        "drug_name": "Xyzal",
        "active_ingredient": "levocetirizine",
        "application_type": "NDA",
        "update_date": "2025-04-15",
        "section_changed": "adverse_reactions",
        "update_direction": "risk_increase",
        "severity_tier": "moderate",
        "source_type": "dsc",
        "srlc_url": None,
        "dsc_url": "https://www.fda.gov/drugs/drug-safety-and-availability/2025-drug-safety-communications",
        "openfda_query": "openfda.application_number:NDA022064",
        "dailymed_url": "https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=47561b5e-7527-4233-8ae7-ce9e70b1cc2a",
        "indication": "allergies",
        "before_packet": "DRUG: Xyzal (levocetirizine)\nAPPLICATION: NDA-022064\nREGULATORY STATE AS OF: 2025-03-01\n\nSAFETY PROFILE SUMMARY:\nLevocetirizine is an antihistamine approved for treatment of allergic rhinitis and chronic urticaria. The label listed common adverse reactions including drowsiness, fatigue, dry mouth, and pharyngitis. No specific warning about withdrawal-related itching was included.\n\nRELEVANT LABEL SECTIONS:\n- Adverse Reactions: Somnolence, nasopharyngitis, fatigue, dry mouth, pharyngitis in adults.\n\nKNOWN SAFETY SIGNALS:\n- Somnolence/drowsiness\n- Fatigue\n- Dry mouth\n- Generally well-tolerated\n\nSOURCES:\n- FDA label via openFDA: openfda.application_number:NDA022064\n- DailyMed: https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=47561b5e-7527-4233-8ae7-ce9e70b1cc2a",
        "after_packet": "DRUG: Xyzal (levocetirizine)\nAPPLICATION: NDA-022064\nREGULATORY STATE AS OF: 2025-05-01\n\nSAFETY UPDATE SUMMARY:\nIn 2025, the FDA required a warning about rare but severe itching (pruritus) that can occur after stopping long-term use of cetirizine or levocetirizine. The itching can be intense, widespread, and may last for weeks after discontinuation, sometimes more severe than the original allergy symptoms.\n\nWHAT CHANGED:\n- Section: Adverse Reactions / Warnings (new warning)\n- Direction: Risk increase\n- Key change: New warning about severe rebound pruritus after discontinuation of long-term use. Patients should gradually taper if stopping after prolonged use.\n\nUPDATED SAFETY PROFILE:\n- Adverse Reactions: Severe pruritus after discontinuation of long-term use added.\n\nSOURCES:\n- FDA Drug Safety Communications (2025): https://www.fda.gov/drugs/drug-safety-and-availability/2025-drug-safety-communications\n- FDA label via openFDA: openfda.application_number:NDA022064\n- DailyMed: https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=47561b5e-7527-4233-8ae7-ce9e70b1cc2a",
        "questions": {
            "patient_plain_language": "I've been taking Xyzal daily for my allergies for a couple of years. Is it safe? Are there any warnings about stopping the medication?",
            "caregiver_or_followup": "My teenager has been on levocetirizine for chronic hives for over a year. We're thinking about stopping it. Is there anything we should know?",
            "medication_use_decision": "I want to stop taking my allergy medication levocetirizine after using it for a long time. Based on current safety information, should I be concerned about stopping?"
        },
        "expected_answer_shift": "The answer should shift from describing levocetirizine as well-tolerated with mild side effects to warning about severe rebound pruritus after stopping long-term use. The after-answer should recommend gradual tapering.",
        "must_mention": ["severe itching after stopping", "rebound pruritus", "long-term use", "gradual taper recommended", "may last weeks"],
        "forbidden_stale_claim": ["can be stopped at any time without issue", "no withdrawal effects", "generally well-tolerated without discontinuation concerns"],
        "rubric_notes": "All three variants specifically frame questions about stopping the medication, making the discontinuation warning directly relevant."
    },
    {
        "event_num": 18,
        "drug_name": "Abilify",
        "active_ingredient": "aripiprazole",
        "application_type": "NDA",
        "update_date": "2025-03-01",
        "section_changed": "adverse_reactions",
        "update_direction": "risk_increase",
        "severity_tier": "moderate",
        "source_type": "srlc",
        "srlc_url": "https://www.accessdata.fda.gov/scripts/cder/safetylabelingchanges/",
        "dsc_url": None,
        "openfda_query": "openfda.application_number:NDA021436",
        "dailymed_url": "https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=c040bd1d-45b7-49d1-b32d-e30b22e8fd58",
        "indication": "schizophrenia, bipolar disorder, depression adjunct",
        "before_packet": "DRUG: Abilify (aripiprazole)\nAPPLICATION: NDA-021436\nREGULATORY STATE AS OF: 2025-01-01\n\nSAFETY PROFILE SUMMARY:\nAripiprazole is an atypical antipsychotic approved for schizophrenia, bipolar disorder, and adjunctive treatment of major depressive disorder. The label included standard antipsychotic warnings about metabolic changes, tardive dyskinesia, and neuroleptic malignant syndrome. The lactation section noted aripiprazole is present in breast milk but did not include specific information about effects on milk supply.\n\nRELEVANT LABEL SECTIONS:\n- Use in Specific Populations (Lactation): Aripiprazole present in human milk. Consider benefits of breastfeeding vs drug exposure.\n\nKNOWN SAFETY SIGNALS:\n- Metabolic changes (weight gain, hyperglycemia, dyslipidemia)\n- Tardive dyskinesia\n- Neuroleptic malignant syndrome\n- Compulsive behaviors (pathological gambling, binge eating)\n\nSOURCES:\n- FDA label via openFDA: openfda.application_number:NDA021436\n- DailyMed: https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=c040bd1d-45b7-49d1-b32d-e30b22e8fd58",
        "after_packet": "DRUG: Abilify (aripiprazole)\nAPPLICATION: NDA-021436\nREGULATORY STATE AS OF: 2025-04-01\n\nSAFETY UPDATE SUMMARY:\nIn 2025, the FDA updated aripiprazole labeling to include reports that aripiprazole exposure may lead to clinically relevant decreases in milk supply, or complete absence of milk production postpartum. This effect is likely mediated through prolactin level suppression by aripiprazole's dopamine agonist activity.\n\nWHAT CHANGED:\n- Section: Adverse Reactions / Use in Specific Populations (Lactation)\n- Direction: Risk increase\n- Key change: New information about decreased or absent milk supply in breastfeeding patients. Breastfed infants should be monitored for dehydration and inadequate weight gain.\n\nUPDATED SAFETY PROFILE:\n- Adverse Reactions / Lactation: Decreased or absent milk supply reported. Monitor breastfed infants for dehydration and failure to thrive.\n\nSOURCES:\n- FDA SrLC: https://www.accessdata.fda.gov/scripts/cder/safetylabelingchanges/\n- FDA label via openFDA: openfda.application_number:NDA021436\n- DailyMed: https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=c040bd1d-45b7-49d1-b32d-e30b22e8fd58",
        "questions": {
            "patient_plain_language": "I take Abilify and I'm planning to breastfeed my baby. Is it safe? Are there any warnings about breastfeeding I should know about?",
            "caregiver_or_followup": "My daughter takes aripiprazole and just had a baby. She's having trouble producing breast milk. Could this be related to her medication?",
            "medication_use_decision": "I'm pregnant and take Abilify for my condition. I want to breastfeed after delivery. Based on current safety information, should I be concerned about my milk supply?"
        },
        "expected_answer_shift": "The answer should shift from general advice about aripiprazole in breast milk to specifically warning about decreased or absent milk supply. The caregiver variant directly describes the symptom, making this highly relevant.",
        "must_mention": ["decreased milk supply", "absent milk production", "prolactin suppression", "monitor infant for dehydration", "discuss with doctor"],
        "forbidden_stale_claim": ["no specific effects on milk supply known", "only concern is drug exposure through breast milk", "breastfeeding decision is only about infant drug exposure"],
        "rubric_notes": "The caregiver variant describes active milk supply problems — the after-answer should connect this to the new labeling information."
    },
    # === DRUG INTERACTIONS (2 more = 3 total, -1 from target 4) ===
    {
        "event_num": 19,
        "drug_name": "Paxlovid",
        "active_ingredient": "nirmatrelvir/ritonavir",
        "application_type": "NDA",
        "update_date": "2024-06-01",
        "section_changed": "drug_interactions",
        "update_direction": "risk_increase",
        "severity_tier": "moderate",
        "source_type": "srlc",
        "srlc_url": "https://www.accessdata.fda.gov/scripts/cder/safetylabelingchanges/",
        "dsc_url": None,
        "openfda_query": "openfda.application_number:NDA217188",
        "dailymed_url": "https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=be6f2856-e834-4345-9613-5e8afbf53d52",
        "indication": "COVID-19 treatment",
        "before_packet": "DRUG: Paxlovid (nirmatrelvir/ritonavir)\nAPPLICATION: NDA-217188\nREGULATORY STATE AS OF: 2024-04-01\n\nSAFETY PROFILE SUMMARY:\nNirmatrelvir/ritonavir is a protease inhibitor combination approved for treatment of mild-to-moderate COVID-19. Ritonavir is a potent CYP3A inhibitor, creating numerous drug interaction risks. The label listed many contraindicated and cautioned medications but continued to be updated as postmarketing interaction reports accumulated.\n\nRELEVANT LABEL SECTIONS:\n- Drug Interactions: Ritonavir inhibits CYP3A. Many drugs contraindicated or require dose adjustment. Specific interactions listed for statins, immunosuppressants, certain cardiac drugs.\n\nKNOWN SAFETY SIGNALS:\n- Extensive CYP3A-mediated drug interactions\n- Dysgeusia (altered taste)\n- Diarrhea, hypertension\n- Rebound COVID-19 symptoms reported\n\nSOURCES:\n- FDA label via openFDA: openfda.application_number:NDA217188\n- DailyMed: https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=be6f2856-e834-4345-9613-5e8afbf53d52",
        "after_packet": "DRUG: Paxlovid (nirmatrelvir/ritonavir)\nAPPLICATION: NDA-217188\nREGULATORY STATE AS OF: 2024-07-01\n\nSAFETY UPDATE SUMMARY:\nIn 2024, the FDA updated Paxlovid labeling with strengthened drug interaction warnings based on postmarketing reports of serious adverse reactions when co-administered with calcineurin inhibitors (tacrolimus, cyclosporine) and certain calcium channel blockers. CYP3A inhibition by ritonavir can dramatically increase blood levels of these medications to toxic concentrations.\n\nWHAT CHANGED:\n- Section: Drug Interactions (strengthened)\n- Direction: Risk increase\n- Key change: Enhanced warnings about life-threatening toxicity with calcineurin inhibitors and calcium channel blockers. Tacrolimus and cyclosporine levels can rise to nephrotoxic or neurotoxic concentrations. Dose adjustment and therapeutic drug monitoring required.\n\nUPDATED SAFETY PROFILE:\n- Drug Interactions: Strengthened warnings for calcineurin inhibitors (tacrolimus, cyclosporine) and calcium channel blockers.\n\nSOURCES:\n- FDA SrLC: https://www.accessdata.fda.gov/scripts/cder/safetylabelingchanges/\n- FDA label via openFDA: openfda.application_number:NDA217188\n- DailyMed: https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=be6f2856-e834-4345-9613-5e8afbf53d52",
        "questions": {
            "patient_plain_language": "I've been prescribed Paxlovid for COVID-19. I also take tacrolimus for my kidney transplant. Is this combination safe?",
            "caregiver_or_followup": "My father was prescribed Paxlovid for COVID but he takes cyclosporine and a blood pressure medication. I've heard Paxlovid has a lot of drug interactions. What should we be aware of?",
            "medication_use_decision": "I have COVID-19 and my doctor wants to prescribe Paxlovid, but I take several other medications. Based on current safety information, should I be concerned about interactions?"
        },
        "expected_answer_shift": "The answer should shift from general CYP3A interaction warnings to specifically highlighting the strengthened warnings about calcineurin inhibitors and calcium channel blockers. The patient variant mentions tacrolimus directly.",
        "must_mention": ["calcineurin inhibitor interaction", "tacrolimus", "cyclosporine", "life-threatening toxicity", "therapeutic drug monitoring"],
        "forbidden_stale_claim": ["general CYP3A caution is sufficient", "standard interaction list covers transplant medications", "no specific enhanced warnings for immunosuppressants"],
        "rubric_notes": "The patient variant creates a high-risk scenario (transplant patient + Paxlovid). The after-answer should be highly specific about the tacrolimus interaction."
    },
    {
        "event_num": 20,
        "drug_name": "Duragesic",
        "active_ingredient": "fentanyl",
        "application_type": "NDA",
        "update_date": "2025-07-31",
        "section_changed": "drug_interactions",
        "update_direction": "risk_increase",
        "severity_tier": "high",
        "source_type": "dsc",
        "srlc_url": None,
        "dsc_url": "https://www.fda.gov/drugs/drug-safety-communications/fda-requiring-opioid-pain-medicine-manufacturers-update-prescribing-information-regarding-long-term",
        "openfda_query": "openfda.application_number:NDA019813",
        "dailymed_url": "https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=4ce560a3-5e4c-4408-8da5-75a7efa91b7d",
        "indication": "chronic pain requiring opioid",
        "before_packet": "DRUG: Duragesic (fentanyl transdermal system)\nAPPLICATION: NDA-019813\nREGULATORY STATE AS OF: 2025-06-01\n\nSAFETY PROFILE SUMMARY:\nFentanyl transdermal patch is an opioid analgesic for management of severe chronic pain. The label included drug interaction warnings about CYP3A4 inhibitors increasing fentanyl levels and CNS depressant combinations. Benzodiazepines were specifically named as a dangerous interaction. Gabapentinoids were not explicitly listed in the fentanyl drug interaction section.\n\nRELEVANT LABEL SECTIONS:\n- Drug Interactions: CYP3A4 inhibitors, benzodiazepines, other CNS depressants. Concurrent use may cause respiratory depression.\n\nKNOWN SAFETY SIGNALS:\n- Fatal respiratory depression\n- Accidental exposure, especially in children\n- Heat-increased absorption from patch\n- Addiction and diversion\n\nSOURCES:\n- FDA label via openFDA: openfda.application_number:NDA019813\n- DailyMed: https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=4ce560a3-5e4c-4408-8da5-75a7efa91b7d",
        "after_packet": "DRUG: Duragesic (fentanyl transdermal system)\nAPPLICATION: NDA-019813\nREGULATORY STATE AS OF: 2025-08-15\n\nSAFETY UPDATE SUMMARY:\nIn July 2025, the FDA required all opioid labeling to explicitly include gabapentinoids (gabapentin, pregabalin) in the drug interaction warnings as CNS depressants. Fentanyl combined with gabapentinoids can cause serious, life-threatening, or fatal respiratory depression, particularly in elderly patients and those with respiratory impairment.\n\nWHAT CHANGED:\n- Section: Drug Interactions (expanded)\n- Direction: Risk increase\n- Key change: Gabapentinoids now explicitly named in fentanyl drug interaction warnings. Fatal respiratory depression reported with the combination, especially in elderly and respiratory-compromised patients.\n\nUPDATED SAFETY PROFILE:\n- Drug Interactions: Gabapentinoids (gabapentin, pregabalin) explicitly added as dangerous CNS depressant interaction partners.\n\nSOURCES:\n- FDA Drug Safety Communication: https://www.fda.gov/drugs/drug-safety-communications/fda-requiring-opioid-pain-medicine-manufacturers-update-prescribing-information-regarding-long-term\n- FDA label via openFDA: openfda.application_number:NDA019813\n- DailyMed: https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=4ce560a3-5e4c-4408-8da5-75a7efa91b7d",
        "questions": {
            "patient_plain_language": "I use a fentanyl patch for chronic pain and also take pregabalin. Is this combination safe? Are there any warnings I should know about?",
            "caregiver_or_followup": "My elderly mother uses a Duragesic patch and was recently prescribed gabapentin. I've heard there might be new warnings about this combination. What should we know?",
            "medication_use_decision": "I use a fentanyl patch and my doctor wants to add pregabalin for nerve pain. Based on current safety information, should I be concerned about this combination?"
        },
        "expected_answer_shift": "The answer should shift from general CNS depressant warnings to specifically naming gabapentinoids as a formally added drug interaction in opioid labeling. The caregiver variant with an elderly patient is particularly relevant as elderly are a high-risk group.",
        "must_mention": ["gabapentinoids explicitly added", "respiratory depression", "elderly at higher risk", "fatal cases reported", "discuss with doctor before combining"],
        "forbidden_stale_claim": ["gabapentinoids not specifically listed as an interaction", "general CNS depressant caution is sufficient", "pregabalin interaction is primarily about sedation"],
        "rubric_notes": "The caregiver variant combines elderly patient + fentanyl + new gabapentin — a triple risk factor scenario. The after-answer should emphasize the urgency."
    },
    # === SPECIFIC POPULATIONS / PATIENT COUNSELING (5 more = 5 total, +1 from target 4) ===
    {
        "event_num": 21,
        "drug_name": "Concerta",
        "active_ingredient": "methylphenidate",
        "application_type": "NDA",
        "update_date": "2025-06-30",
        "section_changed": "specific_populations_or_patient_counseling",
        "update_direction": "risk_increase",
        "severity_tier": "moderate",
        "source_type": "dsc",
        "srlc_url": None,
        "dsc_url": "https://www.fda.gov/drugs/drug-safety-communications/fda-requires-expanded-labeling-about-weight-loss-risk-patients-younger-6-years-taking-extended",
        "openfda_query": "openfda.application_number:NDA021121",
        "dailymed_url": "https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=eb34a315-c8d2-45ca-a595-0c0c66440d10",
        "indication": "ADHD",
        "before_packet": "DRUG: Concerta (methylphenidate ER)\nAPPLICATION: NDA-021121\nREGULATORY STATE AS OF: 2025-05-01\n\nSAFETY PROFILE SUMMARY:\nMethylphenidate extended-release is a CNS stimulant approved for ADHD in patients 6 years and older. The label included warnings about appetite suppression and weight loss as common adverse effects, with recommendations to monitor growth in pediatric patients. No specific labeling addressed patients younger than 6 years.\n\nRELEVANT LABEL SECTIONS:\n- Adverse Reactions: Decreased appetite, weight loss, insomnia, headache.\n- Warnings: Serious cardiovascular events, psychiatric adverse reactions, suppression of growth.\n\nKNOWN SAFETY SIGNALS:\n- Appetite suppression and weight loss\n- Growth suppression in children\n- Cardiovascular effects (increased heart rate, blood pressure)\n- Psychiatric effects (new psychotic symptoms, mania)\n\nSOURCES:\n- FDA label via openFDA: openfda.application_number:NDA021121\n- DailyMed: https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=eb34a315-c8d2-45ca-a595-0c0c66440d10",
        "after_packet": "DRUG: Concerta (methylphenidate ER)\nAPPLICATION: NDA-021121\nREGULATORY STATE AS OF: 2025-07-15\n\nSAFETY UPDATE SUMMARY:\nIn June 2025, the FDA required expanded labeling about weight loss risk in patients younger than 6 years taking extended-release stimulants for ADHD. Children under 6 showed higher plasma drug exposures and higher rates of adverse reactions, including clinically significant weight loss defined as a 10% or greater decrease in CDC weight percentile.\n\nWHAT CHANGED:\n- Section: Use in Specific Populations (Pediatric) / Patient Counseling\n- Direction: Risk increase\n- Key change: New specific population warning for children under 6 years. Clinically significant weight loss (>=10% CDC percentile decrease) observed. Higher plasma exposure and adverse reaction rates in this age group.\n\nUPDATED SAFETY PROFILE:\n- Specific Populations: Children <6 years have higher drug exposures and rates of clinically significant weight loss.\n\nSOURCES:\n- FDA Drug Safety Communication: https://www.fda.gov/drugs/drug-safety-communications/fda-requires-expanded-labeling-about-weight-loss-risk-patients-younger-6-years-taking-extended\n- FDA label via openFDA: openfda.application_number:NDA021121\n- DailyMed: https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=eb34a315-c8d2-45ca-a595-0c0c66440d10",
        "questions": {
            "patient_plain_language": "My young child has been prescribed an extended-release stimulant for ADHD. Is it safe for very young children? Are there any important warnings?",
            "caregiver_or_followup": "My 5-year-old was prescribed methylphenidate for ADHD and has been losing weight. I've heard there's new information about stimulants in young children. What should I know?",
            "medication_use_decision": "My child's doctor wants to prescribe an ER stimulant for ADHD. My child is under 6. Based on current safety information, should I be concerned about weight loss?"
        },
        "expected_answer_shift": "The answer should shift from general growth monitoring advice to specifically warning about the heightened risk of clinically significant weight loss in children under 6 years, with specific data about higher plasma exposures in this age group.",
        "must_mention": ["children under 6 at higher risk", "clinically significant weight loss", "10% CDC percentile decrease", "higher plasma exposures", "closely monitor weight"],
        "forbidden_stale_claim": ["weight monitoring applies equally across all pediatric ages", "no specific concern for children under 6", "standard growth monitoring is sufficient"],
        "rubric_notes": "The caregiver variant describes active weight loss in a 5-year-old, making the new labeling directly applicable."
    },
    {
        "event_num": 22,
        "drug_name": "Qelbree",
        "active_ingredient": "viloxazine",
        "application_type": "NDA",
        "update_date": "2025-01-27",
        "section_changed": "specific_populations_or_patient_counseling",
        "update_direction": "risk_decrease",
        "severity_tier": "low",
        "source_type": "srlc",
        "srlc_url": "https://www.accessdata.fda.gov/scripts/cder/safetylabelingchanges/",
        "dsc_url": None,
        "openfda_query": "openfda.application_number:NDA211964",
        "dailymed_url": "https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=9b42e503-b36f-4296-83cb-1d7b6a8c07a0",
        "indication": "ADHD",
        "before_packet": "DRUG: Qelbree (viloxazine)\nAPPLICATION: NDA-211964\nREGULATORY STATE AS OF: 2024-12-01\n\nSAFETY PROFILE SUMMARY:\nViloxazine is a selective norepinephrine reuptake inhibitor approved for ADHD in patients 6 years and older. As of late 2024, the lactation section stated that there was no data on viloxazine's presence in human milk, effects on the breastfed infant, or effects on milk production. Breastfeeding patients faced uncertainty about safety.\n\nRELEVANT LABEL SECTIONS:\n- Use in Specific Populations (Lactation): No data available on presence in human milk, effects on breastfed infant, or effects on milk production.\n\nKNOWN SAFETY SIGNALS:\n- Suicidal thoughts and behaviors (boxed warning, class effect)\n- Nausea, vomiting, decreased appetite\n- Somnolence, insomnia\n\nSOURCES:\n- FDA label via openFDA: openfda.application_number:NDA211964\n- DailyMed: https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=9b42e503-b36f-4296-83cb-1d7b6a8c07a0",
        "after_packet": "DRUG: Qelbree (viloxazine)\nAPPLICATION: NDA-211964\nREGULATORY STATE AS OF: 2025-02-15\n\nSAFETY UPDATE SUMMARY:\nIn January 2025, the FDA approved a label update adding lactation study data. A study of 15 breastfeeding women showed low transfer of viloxazine into breast milk, with a relative infant dose of approximately 1%, which is well below the commonly used 10% threshold for concern. This provides reassuring data for breastfeeding patients.\n\nWHAT CHANGED:\n- Section: Use in Specific Populations (Lactation)\n- Direction: Risk decrease (reassuring data added)\n- Key change: Lactation study data added showing low infant exposure (relative infant dose ~1%). Provides evidence-based guidance for breastfeeding decisions.\n\nUPDATED SAFETY PROFILE:\n- Lactation: Low transfer to breast milk demonstrated (RID ~1%). Data now available to support informed breastfeeding decisions.\n\nSOURCES:\n- FDA SrLC: https://www.accessdata.fda.gov/scripts/cder/safetylabelingchanges/\n- FDA label via openFDA: openfda.application_number:NDA211964\n- DailyMed: https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=9b42e503-b36f-4296-83cb-1d7b6a8c07a0",
        "questions": {
            "patient_plain_language": "I take Qelbree for my ADHD and I'm breastfeeding. Is it safe? Are there any warnings about breastfeeding I should know about?",
            "caregiver_or_followup": "My wife takes viloxazine for ADHD and wants to breastfeed our newborn. Is there safety data about this medication and breastfeeding?",
            "medication_use_decision": "I'm breastfeeding and need ADHD medication. I'm considering Qelbree. Based on current safety information, is it compatible with breastfeeding?"
        },
        "expected_answer_shift": "The answer should shift from stating no data is available on viloxazine and breastfeeding to citing the new lactation study showing low infant exposure (RID ~1%). The after-answer should be more reassuring and provide evidence-based guidance.",
        "must_mention": ["lactation study data now available", "low transfer to breast milk", "relative infant dose approximately 1%", "below 10% threshold", "discuss with doctor"],
        "forbidden_stale_claim": ["no data available on breastfeeding", "unknown effects on breastfed infant", "no human lactation studies exist"],
        "rubric_notes": "Risk decrease event — the new data is reassuring. Stale alarmism would be continuing to state 'no data available' when data now exists."
    },
    {
        "event_num": 23,
        "drug_name": "Absorica",
        "active_ingredient": "isotretinoin",
        "application_type": "NDA",
        "update_date": "2026-02-09",
        "section_changed": "specific_populations_or_patient_counseling",
        "update_direction": "risk_decrease",
        "severity_tier": "moderate",
        "source_type": "dsc",
        "srlc_url": None,
        "dsc_url": "https://content.govdelivery.com/accounts/USFDA/bulletins/4092fcb",
        "openfda_query": "openfda.application_number:NDA204624",
        "dailymed_url": "https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=8d8d43fa-78e5-4897-b26c-38cd1b8d4e0f",
        "indication": "severe recalcitrant nodular acne",
        "before_packet": "DRUG: Absorica (isotretinoin)\nAPPLICATION: NDA-204624\nREGULATORY STATE AS OF: 2026-01-01\n\nSAFETY PROFILE SUMMARY:\nIsotretinoin is approved for severe recalcitrant nodular acne. The label carried a Boxed Warning for embryofetal toxicity and required participation in the iPLEDGE REMS program. The REMS required CLIA-certified laboratory pregnancy testing, a 19-day lockout period for certain patients, and frequent in-person counseling documentation.\n\nRELEVANT LABEL SECTIONS:\n- Boxed Warning: Embryofetal toxicity. Must not be used during pregnancy.\n- REMS: iPLEDGE program with mandatory CLIA-certified lab pregnancy tests, 19-day lockout, monthly counseling documentation.\n\nKNOWN SAFETY SIGNALS:\n- Severe birth defects (contraindicated in pregnancy)\n- Depression and psychiatric effects\n- Inflammatory bowel disease reports\n- Elevated lipids and liver enzymes\n\nSOURCES:\n- FDA label via openFDA: openfda.application_number:NDA204624\n- DailyMed: https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=8d8d43fa-78e5-4897-b26c-38cd1b8d4e0f",
        "after_packet": "DRUG: Absorica (isotretinoin)\nAPPLICATION: NDA-204624\nREGULATORY STATE AS OF: 2026-03-01\n\nSAFETY UPDATE SUMMARY:\nIn February 2026, the FDA approved modifications to the iPLEDGE REMS program that significantly reduce patient burden. CLIA-certified lab requirement for pregnancy testing was removed (at-home tests now allowed during treatment). The 19-day lockout period was eliminated. Counseling documentation frequency was reduced for patients not capable of becoming pregnant.\n\nWHAT CHANGED:\n- Section: Specific Populations / REMS (requirements relaxed)\n- Direction: Risk decrease (reduced prescribing barriers)\n- Key change: iPLEDGE REMS modernized. At-home pregnancy tests allowed. 19-day lockout removed. Reduced counseling burden for non-pregnant-capable patients. Embryofetal toxicity Boxed Warning and pregnancy contraindication remain.\n\nUPDATED SAFETY PROFILE:\n- REMS: Simplified while maintaining pregnancy prevention safeguards. Boxed Warning for teratogenicity unchanged.\n\nSOURCES:\n- FDA Communication: https://content.govdelivery.com/accounts/USFDA/bulletins/4092fcb\n- FDA label via openFDA: openfda.application_number:NDA204624\n- DailyMed: https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=8d8d43fa-78e5-4897-b26c-38cd1b8d4e0f",
        "questions": {
            "patient_plain_language": "My dermatologist prescribed isotretinoin for my severe acne. I've heard the iPLEDGE program is very burdensome. What do I need to know about the requirements?",
            "caregiver_or_followup": "My teenage daughter needs isotretinoin for severe acne. I've heard the monitoring requirements have changed recently. What should we be aware of?",
            "medication_use_decision": "I'm considering isotretinoin but I've been put off by the complicated monitoring program. Based on current information, is the process still as difficult as I've heard?"
        },
        "expected_answer_shift": "The answer should shift from describing the strict iPLEDGE requirements to noting the simplified program. The after-answer should mention at-home pregnancy tests are now allowed, the lockout period is removed, and counseling burden is reduced, while emphasizing that pregnancy prevention remains critical.",
        "must_mention": ["iPLEDGE requirements simplified", "at-home pregnancy tests allowed", "19-day lockout removed", "pregnancy contraindication unchanged", "embryofetal toxicity warning remains"],
        "forbidden_stale_claim": ["CLIA-certified lab test required", "19-day lockout period applies", "monthly in-person counseling required for all patients"],
        "rubric_notes": "Risk decrease event. The teratogenicity risk is unchanged — only the administrative requirements were relaxed. The answer must clearly distinguish between reduced barriers and unchanged safety risk."
    },
    {
        "event_num": 24,
        "drug_name": "Letairis",
        "active_ingredient": "ambrisentan",
        "application_type": "NDA",
        "update_date": "2025-04-15",
        "section_changed": "specific_populations_or_patient_counseling",
        "update_direction": "risk_decrease",
        "severity_tier": "moderate",
        "source_type": "dsc",
        "srlc_url": None,
        "dsc_url": "https://www.fda.gov/drugs/information-drug-class/endothelin-receptor-antagonist-rems-information",
        "openfda_query": "openfda.application_number:NDA022081",
        "dailymed_url": "https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=27a13de8-ca8a-4ad2-9099-e5ac6e50e886",
        "indication": "pulmonary arterial hypertension",
        "before_packet": "DRUG: Letairis (ambrisentan)\nAPPLICATION: NDA-022081\nREGULATORY STATE AS OF: 2025-03-01\n\nSAFETY PROFILE SUMMARY:\nAmbrisentan is an endothelin receptor antagonist approved for pulmonary arterial hypertension (PAH). The label carried a Boxed Warning for embryofetal toxicity and required participation in an ERA (endothelin receptor antagonist) REMS program. Female patients of reproductive potential could only receive ambrisentan through certified prescribers and pharmacies within the REMS.\n\nRELEVANT LABEL SECTIONS:\n- Boxed Warning: Embryofetal toxicity. Contraindicated in pregnancy.\n- REMS: ERA REMS required enrollment of prescribers, pharmacies, and patients. Monthly pregnancy testing required.\n\nKNOWN SAFETY SIGNALS:\n- Embryofetal toxicity (teratogenic)\n- Peripheral edema, anemia\n- Fluid retention\n- Hepatotoxicity (class concern)\n\nSOURCES:\n- FDA label via openFDA: openfda.application_number:NDA022081\n- DailyMed: https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=27a13de8-ca8a-4ad2-9099-e5ac6e50e886",
        "after_packet": "DRUG: Letairis (ambrisentan)\nAPPLICATION: NDA-022081\nREGULATORY STATE AS OF: 2025-05-01\n\nSAFETY UPDATE SUMMARY:\nIn April 2025, the FDA eliminated the ERA REMS program for all endothelin receptor antagonists including ambrisentan. The FDA determined that labeling alone is adequate to communicate the embryofetal toxicity risk. Prescribers, pharmacies, and patients no longer need to enroll in the REMS.\n\nWHAT CHANGED:\n- Section: Specific Populations / REMS (eliminated)\n- Direction: Risk decrease (reduced access barriers)\n- Key change: ERA REMS eliminated for ambrisentan and all ERAs. Pregnancy contraindication and Boxed Warning for embryofetal toxicity remain. Prescribing is no longer restricted to REMS-certified providers.\n\nUPDATED SAFETY PROFILE:\n- Boxed Warning: Embryofetal toxicity contraindication unchanged.\n- REMS: Eliminated. Access to medication simplified.\n\nSOURCES:\n- FDA Drug Class Information: https://www.fda.gov/drugs/information-drug-class/endothelin-receptor-antagonist-rems-information\n- FDA label via openFDA: openfda.application_number:NDA022081\n- DailyMed: https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=27a13de8-ca8a-4ad2-9099-e5ac6e50e886",
        "questions": {
            "patient_plain_language": "I take Letairis for my pulmonary hypertension. I've always had to go through a special program to get it. Are there any changes to this requirement?",
            "caregiver_or_followup": "My sister takes ambrisentan for PAH and has found the prescribing requirements burdensome. I've heard something has changed. What should she know?",
            "medication_use_decision": "I need treatment for pulmonary arterial hypertension. I've been told ambrisentan requires enrollment in a special program. Based on current information, is that still required?"
        },
        "expected_answer_shift": "The answer should shift from describing the ERA REMS enrollment requirement to noting that the REMS has been eliminated. The after-answer should clarify that pregnancy contraindication is unchanged but access is simplified.",
        "must_mention": ["ERA REMS eliminated", "no longer requires REMS enrollment", "pregnancy contraindication unchanged", "easier access", "embryofetal toxicity warning remains"],
        "forbidden_stale_claim": ["REMS enrollment required", "must use certified prescriber and pharmacy", "cannot get ambrisentan without REMS participation"],
        "rubric_notes": "Risk decrease — access barrier removed while teratogenicity risk unchanged. Similar pattern to clozapine REMS removal (EVT-015)."
    },
    {
        "event_num": 25,
        "drug_name": "Abilify",
        "active_ingredient": "aripiprazole",
        "application_type": "NDA",
        "update_date": "2025-03-01",
        "section_changed": "specific_populations_or_patient_counseling",
        "update_direction": "risk_increase",
        "severity_tier": "moderate",
        "source_type": "srlc",
        "srlc_url": "https://www.accessdata.fda.gov/scripts/cder/safetylabelingchanges/",
        "dsc_url": None,
        "openfda_query": "openfda.application_number:NDA021436",
        "dailymed_url": "https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=c040bd1d-45b7-49d1-b32d-e30b22e8fd58",
        "indication": "schizophrenia, bipolar disorder, depression adjunct",
        "before_packet": "DRUG: Abilify (aripiprazole)\nAPPLICATION: NDA-021436\nREGULATORY STATE AS OF: 2025-01-01\n\nSAFETY PROFILE SUMMARY:\nAripiprazole is an atypical antipsychotic approved for schizophrenia, bipolar disorder, and adjunctive treatment of major depressive disorder. The lactation section noted aripiprazole is present in breast milk but did not include specific information about effects on milk production.\n\nRELEVANT LABEL SECTIONS:\n- Use in Specific Populations (Lactation): Aripiprazole present in human milk. Consider benefits of breastfeeding vs drug exposure.\n\nKNOWN SAFETY SIGNALS:\n- Metabolic changes (weight gain, hyperglycemia, dyslipidemia)\n- Tardive dyskinesia\n- Neuroleptic malignant syndrome\n- Compulsive behaviors\n\nSOURCES:\n- FDA label via openFDA: openfda.application_number:NDA021436\n- DailyMed: https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=c040bd1d-45b7-49d1-b32d-e30b22e8fd58",
        "after_packet": "DRUG: Abilify (aripiprazole)\nAPPLICATION: NDA-021436\nREGULATORY STATE AS OF: 2025-04-01\n\nSAFETY UPDATE SUMMARY:\nIn 2025, the FDA updated aripiprazole labeling to include reports that aripiprazole exposure may lead to clinically relevant decreases in milk supply, or complete absence of milk production postpartum, likely mediated through prolactin suppression by aripiprazole's dopamine agonist activity.\n\nWHAT CHANGED:\n- Section: Use in Specific Populations (Lactation)\n- Direction: Risk increase\n- Key change: New information about decreased or absent milk supply in breastfeeding patients. Breastfed infants should be monitored for dehydration and inadequate weight gain.\n\nUPDATED SAFETY PROFILE:\n- Lactation: Decreased or absent milk supply reported. Monitor breastfed infants for dehydration and failure to thrive.\n\nSOURCES:\n- FDA SrLC: https://www.accessdata.fda.gov/scripts/cder/safetylabelingchanges/\n- FDA label via openFDA: openfda.application_number:NDA021436\n- DailyMed: https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=c040bd1d-45b7-49d1-b32d-e30b22e8fd58",
        "questions": {
            "patient_plain_language": "I take Abilify and I'm planning to breastfeed my baby. Is it safe? Are there any warnings about breastfeeding I should know about?",
            "caregiver_or_followup": "My daughter takes aripiprazole and just had a baby. She's having difficulty producing breast milk. Could this be related to her medication?",
            "medication_use_decision": "I'm pregnant and take Abilify for my condition. I want to breastfeed after delivery. Based on current safety information, should I be concerned about my milk supply?"
        },
        "expected_answer_shift": "The answer should shift from general advice about aripiprazole in breast milk to specifically warning about decreased or absent milk supply. The caregiver variant directly describes the symptom.",
        "must_mention": ["decreased milk supply", "absent milk production", "prolactin suppression", "monitor infant for dehydration", "discuss with doctor"],
        "forbidden_stale_claim": ["no specific effects on milk supply known", "only concern is drug exposure through breast milk"],
        "rubric_notes": "The caregiver variant describes active milk supply problems — the after-answer should connect this to the new labeling."
    },
]

# Stable controls
STABLE_CONTROLS = [
    {"event_num": 26, "drug_name": "Glucophage", "active_ingredient": "metformin", "application_type": "NDA", "openfda_query": "openfda.application_number:NDA020357", "dailymed_url": "https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=4a0166df-3f2c-4daa-8192-29e2d5112a42", "indication": "type 2 diabetes",
     "before_packet": "DRUG: Glucophage (metformin)\nAPPLICATION: NDA-020357\nREGULATORY STATE AS OF: 2024-01-01\n\nSAFETY PROFILE SUMMARY:\nMetformin is a biguanide antihyperglycemic agent approved for type 2 diabetes. It has been marketed since 1995 with a well-characterized safety profile. The label carries a Boxed Warning for lactic acidosis risk, which is rare but can be fatal, particularly in patients with renal impairment, hepatic impairment, or other conditions predisposing to hypoperfusion.\n\nRELEVANT LABEL SECTIONS:\n- Boxed Warning: Lactic acidosis risk. Contraindicated in severe renal impairment (eGFR <30). Assess renal function before initiation and periodically.\n- Warnings: Vitamin B12 deficiency with long-term use. Hypoglycemia when combined with insulin or secretagogues.\n\nKNOWN SAFETY SIGNALS:\n- Lactic acidosis (rare, boxed warning)\n- GI intolerance (common: diarrhea, nausea)\n- Vitamin B12 deficiency\n- Contraindicated in severe renal impairment\n\nSOURCES:\n- FDA label via openFDA: openfda.application_number:NDA020357\n- DailyMed: https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=4a0166df-3f2c-4daa-8192-29e2d5112a42",
     "questions": {"patient_plain_language": "I take metformin for my type 2 diabetes. Is it safe? Are there any important warnings I should know about?", "caregiver_or_followup": "My father has been on metformin for years for his diabetes. I've heard there might be new safety information about diabetes medications. What should we know?", "medication_use_decision": "I'm considering whether to continue metformin for my diabetes. Based on current safety information, should I be concerned?"},
     "must_mention": ["lactic acidosis risk", "renal function monitoring", "GI side effects", "well-established medication"]},
    {"event_num": 27, "drug_name": "Norvasc", "active_ingredient": "amlodipine", "application_type": "NDA", "openfda_query": "openfda.application_number:NDA019787", "dailymed_url": "https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=acc079c6-b734-44bf-90d2-2a84c4ba08f0", "indication": "hypertension, angina",
     "before_packet": "DRUG: Norvasc (amlodipine)\nAPPLICATION: NDA-019787\nREGULATORY STATE AS OF: 2024-01-01\n\nSAFETY PROFILE SUMMARY:\nAmlodipine is a calcium channel blocker approved for hypertension and angina. It has been marketed since 1992 with a well-established safety profile. The most common adverse effect is peripheral edema, which is dose-dependent.\n\nRELEVANT LABEL SECTIONS:\n- Adverse Reactions: Edema, dizziness, flushing, palpitation.\n- Warnings: Worsening angina or acute MI can occur with initiation or dose increase, particularly in severe obstructive coronary artery disease. Hypotension possible.\n\nKNOWN SAFETY SIGNALS:\n- Peripheral edema (dose-dependent, very common)\n- Dizziness, flushing\n- Rare: worsening angina on initiation\n\nSOURCES:\n- FDA label via openFDA: openfda.application_number:NDA019787\n- DailyMed: https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=acc079c6-b734-44bf-90d2-2a84c4ba08f0",
     "questions": {"patient_plain_language": "I take amlodipine for my blood pressure. Is it safe? Are there any important warnings I should know about?", "caregiver_or_followup": "My mother takes Norvasc for high blood pressure. I've heard there might be updates about blood pressure medications. What should she be aware of?", "medication_use_decision": "I'm considering whether to continue amlodipine for my hypertension. Based on current safety information, should I be concerned?"},
     "must_mention": ["peripheral edema", "well-established medication", "dizziness", "continue as prescribed"]},
    {"event_num": 28, "drug_name": "Prilosec", "active_ingredient": "omeprazole", "application_type": "NDA", "openfda_query": "openfda.application_number:NDA019810", "dailymed_url": "https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=d37a0e5e-981f-4ab2-9837-c1befff7e13d", "indication": "GERD, ulcers",
     "before_packet": "DRUG: Prilosec (omeprazole)\nAPPLICATION: NDA-019810\nREGULATORY STATE AS OF: 2024-01-01\n\nSAFETY PROFILE SUMMARY:\nOmeprazole is a proton pump inhibitor approved for GERD, duodenal ulcer, gastric ulcer, and erosive esophagitis. It has been marketed since 1989. Long-term use warnings include risk of Clostridium difficile-associated diarrhea, bone fractures with long-term use, hypomagnesemia, and vitamin B12 deficiency.\n\nRELEVANT LABEL SECTIONS:\n- Warnings: C. difficile infection risk. Bone fracture risk with long-term, high-dose use. Hypomagnesemia. Vitamin B12 deficiency. Fundic gland polyps with long-term use.\n\nKNOWN SAFETY SIGNALS:\n- C. difficile-associated diarrhea\n- Bone fractures (long-term, high-dose)\n- Hypomagnesemia\n- Vitamin B12 deficiency\n- Fundic gland polyps\n\nSOURCES:\n- FDA label via openFDA: openfda.application_number:NDA019810\n- DailyMed: https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=d37a0e5e-981f-4ab2-9837-c1befff7e13d",
     "questions": {"patient_plain_language": "I take omeprazole for my acid reflux. Is it safe for long-term use? Are there any important warnings?", "caregiver_or_followup": "My husband has been on Prilosec for years. I've heard there might be new concerns about long-term PPI use. What should he know?", "medication_use_decision": "I'm considering whether to continue omeprazole long-term. Based on current safety information, should I be concerned?"},
     "must_mention": ["bone fracture risk", "C. difficile", "hypomagnesemia", "well-established medication"]},
    {"event_num": 29, "drug_name": "Zoloft", "active_ingredient": "sertraline", "application_type": "NDA", "openfda_query": "openfda.application_number:NDA019839", "dailymed_url": "https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=92082657-4e66-4e0e-b43c-f7cc4a9cfc35", "indication": "depression, anxiety disorders",
     "before_packet": "DRUG: Zoloft (sertraline)\nAPPLICATION: NDA-019839\nREGULATORY STATE AS OF: 2024-01-01\n\nSAFETY PROFILE SUMMARY:\nSertraline is an SSRI approved for major depressive disorder, OCD, panic disorder, PTSD, social anxiety disorder, and PMDD. It has been marketed since 1991. The label carries a Boxed Warning about suicidal thoughts and behaviors in pediatric and young adult patients.\n\nRELEVANT LABEL SECTIONS:\n- Boxed Warning: Suicidality risk in children, adolescents, and young adults.\n- Warnings: Serotonin syndrome, bleeding risk, activation of mania, discontinuation syndrome, hyponatremia.\n\nKNOWN SAFETY SIGNALS:\n- Suicidality risk in young patients (boxed warning)\n- Serotonin syndrome (with MAOIs, other serotonergic drugs)\n- GI side effects (nausea, diarrhea)\n- Sexual dysfunction\n- Discontinuation syndrome\n\nSOURCES:\n- FDA label via openFDA: openfda.application_number:NDA019839\n- DailyMed: https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=92082657-4e66-4e0e-b43c-f7cc4a9cfc35",
     "questions": {"patient_plain_language": "I take Zoloft for my depression. Is it safe? Are there any important warnings I should know about?", "caregiver_or_followup": "My teenage son takes sertraline for anxiety. I've heard there might be new information about antidepressant safety. What should we be aware of?", "medication_use_decision": "I'm considering whether to continue sertraline. Based on current safety information, should I be concerned?"},
     "must_mention": ["suicidality boxed warning", "serotonin syndrome risk", "discontinuation syndrome", "well-established medication"]},
    {"event_num": 30, "drug_name": "Synthroid", "active_ingredient": "levothyroxine", "application_type": "NDA", "openfda_query": "openfda.application_number:NDA021402", "dailymed_url": "https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=4e7cc32c-69e2-4a1f-8e97-2543c48b2f28", "indication": "hypothyroidism",
     "before_packet": "DRUG: Synthroid (levothyroxine)\nAPPLICATION: NDA-021402\nREGULATORY STATE AS OF: 2024-01-01\n\nSAFETY PROFILE SUMMARY:\nLevothyroxine is a thyroid hormone replacement approved for hypothyroidism and TSH suppression. It has been used for decades with a well-established safety profile. The label carries a Boxed Warning that thyroid hormones should not be used for weight loss and that large doses can produce serious or life-threatening toxicity.\n\nRELEVANT LABEL SECTIONS:\n- Boxed Warning: Not for weight loss. Large doses cause serious toxicity.\n- Warnings: Cardiovascular effects in patients with underlying cardiac disease. Overtreatment risks (osteoporosis, atrial fibrillation). Many drug interactions affecting absorption and metabolism.\n\nKNOWN SAFETY SIGNALS:\n- Overtreatment: osteoporosis, cardiac arrhythmias\n- Numerous drug and food interactions affecting absorption\n- Dose adjustment needed frequently\n- Contraindicated with uncorrected adrenal insufficiency\n\nSOURCES:\n- FDA label via openFDA: openfda.application_number:NDA021402\n- DailyMed: https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=4e7cc32c-69e2-4a1f-8e97-2543c48b2f28",
     "questions": {"patient_plain_language": "I take Synthroid for my underactive thyroid. Is it safe? Are there any important warnings I should know about?", "caregiver_or_followup": "My wife takes levothyroxine daily. I've heard there might be updates about thyroid medications. What should she be aware of?", "medication_use_decision": "I'm considering whether my levothyroxine dose needs adjusting. Based on current safety information, should I be concerned about long-term use?"},
     "must_mention": ["not for weight loss", "dose monitoring", "drug interactions", "well-established medication"]},
]

VARIANTS = ["patient_plain_language", "caregiver_or_followup", "medication_use_decision"]

def make_stable_after_packet(drug_name, app_num):
    return (
        f"DRUG: {drug_name}\n"
        f"APPLICATION: {app_num}\n"
        f"REGULATORY STATE AS OF: 2026-03-31\n\n"
        f"NO SAFETY UPDATE:\n"
        f"As of March 31, 2026, no new FDA safety-related labeling changes have been issued "
        f"for {drug_name.split(' (')[0] if ' (' in drug_name else drug_name} within the evaluation window "
        f"(2024-01-01 to 2026-03-31). The safety profile described in the before_packet remains current.\n\n"
        f"SOURCES:\n"
        f"- FDA SrLC (negative check): https://www.accessdata.fda.gov/scripts/cder/safetylabelingchanges/\n"
        f"- FDA label via openFDA: {app_num.replace('-', '')}\n"
    )

def generate_items():
    items = []

    # Generate update-positive events
    for event in EVENTS:
        num = event["event_num"]
        for variant in VARIANTS:
            item = {
                "case_id": f"DSU-{num:03d}-{variant}",
                "drug_name": event["drug_name"],
                "active_ingredient": event["active_ingredient"],
                "application_type": event["application_type"],
                "update_date": event["update_date"],
                "section_changed": event["section_changed"],
                "update_direction": event["update_direction"],
                "severity_tier": event["severity_tier"],
                "source_type": event["source_type"],
                "srlc_url": event["srlc_url"],
                "dsc_url": event["dsc_url"],
                "openfda_query": event["openfda_query"],
                "dailymed_url": event["dailymed_url"],
                "before_packet": event["before_packet"],
                "after_packet": event["after_packet"],
                "prompt_variant": variant,
                "user_question": event["questions"][variant],
                "expected_answer_shift": event["expected_answer_shift"],
                "must_mention": event["must_mention"],
                "forbidden_stale_claim": event["forbidden_stale_claim"],
                "rubric_notes": event["rubric_notes"]
            }
            items.append(item)

    # Generate stable controls
    for ctrl in STABLE_CONTROLS:
        num = ctrl["event_num"]
        app_type = ctrl["application_type"]
        app_query = ctrl["openfda_query"]
        app_num_raw = app_query.split(":")[-1]
        # Format: NDA020357 -> NDA-020357
        app_num_formatted = f"{app_num_raw[:3]}-{app_num_raw[3:]}"
        drug_line = f"{ctrl['drug_name']} ({ctrl['active_ingredient']})"

        after_pkt = make_stable_after_packet(drug_line, app_num_formatted)
        # Add dailymed to after_packet
        after_pkt += f"- DailyMed: {ctrl['dailymed_url']}"

        for variant in VARIANTS:
            item = {
                "case_id": f"DSU-{num:03d}-{variant}",
                "drug_name": ctrl["drug_name"],
                "active_ingredient": ctrl["active_ingredient"],
                "application_type": ctrl["application_type"],
                "update_date": "2026-03-31",
                "section_changed": "stable_control",
                "update_direction": "stable",
                "severity_tier": "control",
                "source_type": "control_no_update",
                "srlc_url": None,
                "dsc_url": None,
                "openfda_query": ctrl["openfda_query"],
                "dailymed_url": ctrl["dailymed_url"],
                "before_packet": ctrl["before_packet"],
                "after_packet": after_pkt,
                "prompt_variant": variant,
                "user_question": ctrl["questions"][variant],
                "expected_answer_shift": "The answer should NOT change meaningfully between before and after conditions. Both answers should describe the same well-established safety profile. No new safety update should be introduced.",
                "must_mention": ctrl["must_mention"],
                "forbidden_stale_claim": [],
                "rubric_notes": "Stable control. update_uptake=2 means the answer correctly did NOT change. update_uptake=0 means the answer falsely shifted, introducing phantom safety updates that do not exist."
            }
            items.append(item)

    return items

if __name__ == "__main__":
    items = generate_items()
    print(f"Generated {len(items)} items from {len(items)//3} events")

    # Write to JSONL
    outpath = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "benchmark_items.jsonl")

    # Read existing pilot items
    with open(outpath, "r") as f:
        existing_lines = f.readlines()

    # Update metadata
    total_items = 18 + len(items)  # pilot + new
    meta = json.loads(existing_lines[0])
    meta["_item_count"] = total_items

    # Write everything
    with open(outpath, "w") as f:
        f.write(json.dumps(meta) + "\n")
        # Write pilot items (lines 1-18)
        for line in existing_lines[1:]:
            f.write(line)
        # Write new items
        for item in items:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")

    print(f"Written to {outpath}: 1 metadata + {total_items} items = {total_items + 1} lines")
