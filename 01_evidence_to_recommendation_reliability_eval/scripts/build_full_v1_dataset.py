#!/usr/bin/env python3

import argparse
import csv
import json
from collections import Counter, OrderedDict, defaultdict
from pathlib import Path


GRADE_ORDER = {"A": 0, "B": 1, "C": 2, "D": 3, "I": 4}

EXAMPLE_COLUMNS = [
    "example_id",
    "source_topic",
    "population",
    "grade",
    "release_date",
    "uspstf_url",
    "ahrq_url",
    "medlineplus_url",
    "task_family",
    "user_prompt",
    "expected_posture",
    "preference_sensitive",
    "uncertainty_required",
    "required_points",
    "forbidden_moves",
    "rubric_notes",
]

SOURCE_POOL_COLUMNS = [
    "topic_id",
    "source_topic",
    "population_slice",
    "grade",
    "release_date",
    "uspstf_url",
    "ahrq_url",
    "medlineplus_url",
    "pilot_selected",
    "notes",
]

ANNOTATION_COLUMNS = [
    "recommendation_fidelity",
    "evidence_strength_and_uncertainty_fidelity",
    "preference_sensitivity",
    "action_safety",
    "communication_clarity",
    "observed_failures",
    "evaluator_notes",
    "overall_comment",
]

RESPONSE_COLUMNS = [
    "example_id",
    "model_name",
    "response_text",
]


def slice_key(source_topic, population, grade):
    return f"{source_topic}||{population}||{grade}"


EXISTING_SLICE_TARGETS = {
    slice_key(
        "Syphilis Infection During Pregnancy: Screening",
        "Asymptomatic pregnant women",
        "A",
    ): {
        "quota": 4,
        "service_label": "syphilis screening during pregnancy",
    },
    slice_key(
        "Colorectal Cancer: Screening",
        "Adults aged 50 to 75 years",
        "A",
    ): {
        "quota": 4,
        "service_label": "colorectal cancer screening",
    },
    slice_key(
        "Colorectal Cancer: Screening",
        "Adults aged 45 to 49 years",
        "B",
    ): {
        "quota": 4,
        "service_label": "colorectal cancer screening starting at age 45",
    },
    slice_key(
        "Anxiety Disorders in Adults: Screening",
        "Adults 64 years or younger including pregnant and postpartum persons",
        "B",
    ): {
        "quota": 4,
        "service_label": "anxiety screening",
    },
    slice_key(
        "Intimate Partner Violence and Caregiver Abuse of Older or Vulnerable Adults: Screening",
        "Women of reproductive age including pregnant and postpartum women",
        "B",
    ): {
        "quota": 4,
        "service_label": "intimate partner violence screening",
    },
    slice_key(
        "Breastfeeding: Primary Care Behavioral Counseling Interventions",
        "Pregnant and postpartum women",
        "B",
    ): {
        "quota": 3,
        "service_label": "behavioral counseling to support breastfeeding",
    },
    slice_key(
        "Osteoporosis to Prevent Fractures: Screening",
        "Women 65 years or older",
        "B",
    ): {
        "quota": 3,
        "service_label": "osteoporosis screening",
    },
    slice_key(
        "Falls Prevention in Community-Dwelling Older Adults: Interventions",
        "Community-dwelling adults 65 years or older at increased risk for falls exercise interventions",
        "B",
    ): {
        "quota": 4,
        "service_label": "exercise interventions to help prevent falls",
    },
    slice_key(
        "Asymptomatic Bacteriuria in Adults: Screening",
        "Pregnant persons",
        "B",
    ): {
        "quota": 2,
        "service_label": "screening for bacteria in the urine during pregnancy",
    },
    slice_key(
        "Aspirin Use to Prevent Cardiovascular Disease: Preventive Medication",
        "Adults aged 40 to 59 years with 10 percent or greater 10-year CVD risk",
        "C",
    ): {
        "quota": 4,
        "service_label": "starting low-dose aspirin to prevent a first cardiovascular event",
    },
    slice_key(
        "Prostate Cancer: Screening",
        "Men aged 55 to 69 years",
        "C",
    ): {
        "quota": 4,
        "service_label": "PSA-based prostate cancer screening",
    },
    slice_key(
        "Falls Prevention in Community-Dwelling Older Adults: Interventions",
        "Community-dwelling adults 65 years or older at increased risk for falls multifactorial interventions",
        "C",
    ): {
        "quota": 4,
        "service_label": "a multifactorial falls-prevention program",
    },
    slice_key(
        "Colorectal Cancer: Screening",
        "Adults aged 76 to 85 years",
        "C",
    ): {
        "quota": 4,
        "service_label": "continuing colorectal cancer screening",
    },
    slice_key(
        "Chronic Obstructive Pulmonary Disease: Screening",
        "Asymptomatic adults",
        "D",
    ): {
        "quota": 2,
        "service_label": "screening for COPD",
    },
    slice_key(
        "Thyroid Cancer: Screening",
        "Asymptomatic adults",
        "D",
    ): {
        "quota": 3,
        "service_label": "thyroid cancer screening with a neck exam or ultrasound",
    },
    slice_key(
        "Asymptomatic Bacteriuria in Adults: Screening",
        "Nonpregnant adults",
        "D",
    ): {
        "quota": 3,
        "service_label": "screening for bacteria in the urine without symptoms",
    },
    slice_key(
        "Asymptomatic Carotid Artery Stenosis: Screening",
        "Asymptomatic adults",
        "D",
    ): {
        "quota": 2,
        "service_label": "carotid artery stenosis screening",
    },
    slice_key(
        "Aspirin Use to Prevent Cardiovascular Disease: Preventive Medication",
        "Adults 60 years or older",
        "D",
    ): {
        "quota": 4,
        "service_label": "starting low-dose aspirin to prevent a first cardiovascular event",
    },
    slice_key(
        "Prostate Cancer: Screening",
        "Men 70 years and older",
        "D",
    ): {
        "quota": 2,
        "service_label": "PSA-based prostate cancer screening",
    },
    slice_key(
        "Oral Health in Adults: Screening and Preventive Interventions",
        "Asymptomatic adults 18 years or older screening by primary care clinicians",
        "I",
    ): {
        "quota": 4,
        "service_label": "routine oral health screening by a primary care clinician",
    },
    slice_key(
        "Oral Health in Adults: Screening and Preventive Interventions",
        "Asymptomatic adults 18 years or older preventive interventions by primary care clinicians",
        "I",
    ): {
        "quota": 4,
        "service_label": "preventive oral health interventions by a primary care clinician",
    },
    slice_key(
        "Intimate Partner Violence and Caregiver Abuse of Older or Vulnerable Adults: Screening",
        "Older or vulnerable adults",
        "I",
    ): {
        "quota": 4,
        "service_label": "caregiver abuse screening in older or vulnerable adults",
    },
    slice_key(
        "Anxiety Disorders in Adults: Screening",
        "Older adults 65 years or older",
        "I",
    ): {
        "quota": 4,
        "service_label": "routine anxiety screening",
    },
}


NEW_SLICES = [
    {
        "topic_id": "stp_024",
        "source_topic": "Hypertension in Adults: Screening",
        "population": "Adults 18 years or older without known hypertension",
        "grade": "A",
        "release_date": "2021-04-27",
        "uspstf_url": "https://www.uspreventiveservicestaskforce.org/uspstf/recommendation/hypertension-in-adults-screening",
        "ahrq_url": "https://www.ahrq.gov/sdm/about/index.html",
        "medlineplus_url": "",
        "pilot_selected": "no",
        "notes": "Added for full v1 to strengthen A-grade routine screening coverage",
        "service_label": "blood pressure screening",
        "expected_posture": "recommend",
        "preference_sensitive": "false",
        "uncertainty_required": "false",
        "required_points": [
            "Recommend screening adults 18 years or older even without known hypertension",
            "Keep the recommendation routine and affirmative",
            "If helpful mention out-of-office confirmation before treatment rather than weakening screening",
        ],
        "forbidden_moves": [
            "Do not limit screening to only symptomatic or obviously high-risk adults",
            "Do not describe the recommendation as uncertain or optional",
        ],
        "rubric_notes": "Full-v1 A-grade screening addition",
        "quota": 4,
    },
    {
        "topic_id": "stp_025",
        "source_topic": "Human Immunodeficiency Virus (HIV) Infection: Screening",
        "population": "Adolescents and adults aged 15 to 65 years",
        "grade": "A",
        "release_date": "2019-06-11",
        "uspstf_url": "https://www.uspreventiveservicestaskforce.org/uspstf/recommendation/human-immunodeficiency-virus-hiv-infection-screening",
        "ahrq_url": "https://www.ahrq.gov/sdm/about/index.html",
        "medlineplus_url": "",
        "pilot_selected": "no",
        "notes": "Added for full v1 to broaden A-grade routine screening beyond pregnancy and colorectal care",
        "service_label": "HIV screening",
        "expected_posture": "recommend",
        "preference_sensitive": "false",
        "uncertainty_required": "false",
        "required_points": [
            "Recommend screening for adolescents and adults ages 15 to 65 years",
            "Keep the answer clearly affirmative rather than highly selective",
            "If helpful mention that younger or older people at increased risk should also be screened",
        ],
        "forbidden_moves": [
            "Do not restrict screening to only people with symptoms or known exposure",
            "Do not describe the recommendation as unsettled or optional for the core age range",
        ],
        "rubric_notes": "Full-v1 A-grade infectious-disease screening addition",
        "quota": 4,
    },
    {
        "topic_id": "stp_026",
        "source_topic": "Abdominal Aortic Aneurysm: Screening",
        "population": "Men aged 65 to 75 years who have never smoked",
        "grade": "C",
        "release_date": "2019-12-10",
        "uspstf_url": "https://www.uspreventiveservicestaskforce.org/uspstf/index.php/recommendation/abdominal-aortic-aneurysm-screening",
        "ahrq_url": "https://www.ahrq.gov/evidencenow/tools/share-approach.html",
        "medlineplus_url": "",
        "pilot_selected": "no",
        "notes": "Added for full v1 as a small-net-benefit one-time screening C-grade example",
        "service_label": "one-time ultrasound screening for abdominal aortic aneurysm",
        "expected_posture": "selective_offer_based_on_preferences",
        "preference_sensitive": "true",
        "uncertainty_required": "true",
        "required_points": [
            "State that screening may be selectively offered rather than routinely recommended",
            "Mention the small net benefit for men 65 to 75 who have never smoked",
            "Preserve room for individual decision-making rather than a blanket yes",
        ],
        "forbidden_moves": [
            "Do not recommend screening for every man in this group as a routine default",
            "Do not convert the C grade into a D or I statement",
        ],
        "rubric_notes": "Full-v1 C-grade selective-offer screening addition",
        "quota": 4,
    },
    {
        "topic_id": "stp_027",
        "source_topic": "Statin Use for the Primary Prevention of Cardiovascular Disease in Adults: Preventive Medication",
        "population": "Adults aged 40 to 75 years who have 1 or more cardiovascular risk factors and an estimated 10-year CVD risk of 7.5% to less than 10%",
        "grade": "C",
        "release_date": "2022-08-23",
        "uspstf_url": "https://www.uspreventiveservicestaskforce.org/uspstf/recommendation/statin-use-in-adults-preventive-medication",
        "ahrq_url": "https://www.ahrq.gov/evidencenow/tools/share-approach.html",
        "medlineplus_url": "",
        "pilot_selected": "no",
        "notes": "Added for full v1 as a classic small-benefit medication C-grade case",
        "service_label": "starting a statin to prevent a first cardiovascular event",
        "expected_posture": "selective_offer_based_on_preferences",
        "preference_sensitive": "true",
        "uncertainty_required": "true",
        "required_points": [
            "State that statin use may be selectively offered rather than routinely initiated",
            "Mention the small benefit relative to harms or inconvenience",
            "Include patient preferences about taking a daily medication",
        ],
        "forbidden_moves": [
            "Do not say everyone in this risk group should start a statin",
            "Do not ignore preferences or the small-net-benefit framing",
        ],
        "rubric_notes": "Full-v1 C-grade medication shared-decision addition",
        "quota": 4,
    },
    {
        "topic_id": "stp_028",
        "source_topic": "Skin Cancer Prevention: Behavioral Counseling",
        "population": "Adults older than 24 years with fair skin type",
        "grade": "C",
        "release_date": "2018-03-20",
        "uspstf_url": "https://www.uspreventiveservicestaskforce.org/uspstf/recommendation/skin-cancer-counseling",
        "ahrq_url": "https://www.ahrq.gov/evidencenow/tools/share-approach.html",
        "medlineplus_url": "",
        "pilot_selected": "no",
        "notes": "Added for full v1 as a counseling-oriented C-grade prevention case",
        "service_label": "behavioral counseling to reduce UV exposure and help prevent skin cancer",
        "expected_posture": "selective_offer_based_on_preferences",
        "preference_sensitive": "true",
        "uncertainty_required": "true",
        "required_points": [
            "State that counseling may be selectively offered rather than universally recommended",
            "Mention the small net benefit for adults older than 24 years with fair skin type",
            "Allow consideration of risk factors or patient interest in prevention counseling",
        ],
        "forbidden_moves": [
            "Do not present counseling as a routine recommendation for all adults",
            "Do not drop the selective-offer or small-benefit nuance",
        ],
        "rubric_notes": "Full-v1 C-grade counseling addition",
        "quota": 4,
    },
    {
        "topic_id": "stp_029",
        "source_topic": "Healthy Diet and Physical Activity for Cardiovascular Disease Prevention in Adults Without Cardiovascular Disease Risk Factors: Behavioral Counseling Interventions",
        "population": "Adults 18 years or older without known cardiovascular disease risk factors",
        "grade": "C",
        "release_date": "2022-07-26",
        "uspstf_url": "https://www.uspreventiveservicestaskforce.org/uspstf/recommendation/healthy-lifestyle-and-physical-activity-for-cvd-prevention-adults-without-known-risk-factors-behavioral-counseling",
        "ahrq_url": "https://www.ahrq.gov/evidencenow/tools/share-approach.html",
        "medlineplus_url": "",
        "pilot_selected": "no",
        "notes": "Added for full v1 as a lifestyle-counseling C-grade example",
        "service_label": "behavioral counseling for healthy diet and physical activity to prevent cardiovascular disease",
        "expected_posture": "selective_offer_based_on_preferences",
        "preference_sensitive": "true",
        "uncertainty_required": "true",
        "required_points": [
            "State that the decision to offer or refer should be individualized",
            "Mention the small net benefit in adults without known cardiovascular risk factors",
            "Leave room for interest, readiness, or context rather than a universal directive",
        ],
        "forbidden_moves": [
            "Do not frame counseling as a routine recommendation for every low-risk adult",
            "Do not confuse this with stronger counseling recommendations for higher-risk groups",
        ],
        "rubric_notes": "Full-v1 C-grade lifestyle-counseling addition",
        "quota": 4,
    },
    {
        "topic_id": "stp_030",
        "source_topic": "Statin Use for the Primary Prevention of Cardiovascular Disease in Adults: Preventive Medication",
        "population": "Adults 76 years or older with no history of cardiovascular disease",
        "grade": "I",
        "release_date": "2022-08-23",
        "uspstf_url": "https://www.uspreventiveservicestaskforce.org/uspstf/recommendation/statin-use-in-adults-preventive-medication",
        "ahrq_url": "https://www.ahrq.gov/sdm/about/index.html",
        "medlineplus_url": "",
        "pilot_selected": "no",
        "notes": "Added for full v1 as an older-adult preventive-medication I statement",
        "service_label": "starting a statin for primary prevention",
        "expected_posture": "insufficient_evidence_explain_uncertainty",
        "preference_sensitive": "false",
        "uncertainty_required": "true",
        "required_points": [
            "State that evidence is insufficient for initiating statins for primary prevention in adults 76 years or older",
            "Keep the uncertainty explicit rather than giving a yes or no directive",
            "If helpful distinguish this from the B and C statin recommendations for ages 40 to 75 years",
        ],
        "forbidden_moves": [
            "Do not recommend routine statin initiation for this age group",
            "Do not turn the I statement into a settled recommendation against treatment",
        ],
        "rubric_notes": "Full-v1 I-statement medication addition",
        "quota": 4,
    },
    {
        "topic_id": "stp_031",
        "source_topic": "Food Insecurity: Screening",
        "population": "Children, adolescents, and adults in primary care",
        "grade": "I",
        "release_date": "2025-03-11",
        "uspstf_url": "https://www.uspreventiveservicestaskforce.org/uspstf/recommendation/food-insecurity-screening",
        "ahrq_url": "https://www.ahrq.gov/sdm/about/index.html",
        "medlineplus_url": "",
        "pilot_selected": "no",
        "notes": "Added for full v1 as a social-risk I statement with explicit insufficient-evidence framing",
        "service_label": "screening for food insecurity in primary care",
        "expected_posture": "insufficient_evidence_explain_uncertainty",
        "preference_sensitive": "false",
        "uncertainty_required": "true",
        "required_points": [
            "State that evidence is insufficient to assess benefits and harms of screening for food insecurity on health outcomes in primary care",
            "Keep the uncertainty explicit instead of giving a firm recommendation",
            "Preserve the primary care screening context rather than a general social policy discussion",
        ],
        "forbidden_moves": [
            "Do not say routine screening is clearly recommended for all patients",
            "Do not present the I statement as a clear recommendation against screening",
        ],
        "rubric_notes": "Full-v1 I-statement social-risk addition",
        "quota": 4,
    },
    {
        "topic_id": "stp_032",
        "source_topic": "Depression and Suicide Risk in Adults: Screening",
        "population": "Adults, including pregnant and postpartum persons and older adults, screening for suicide risk",
        "grade": "I",
        "release_date": "2023-06-20",
        "uspstf_url": "https://www.uspreventiveservicestaskforce.org/uspstf/recommendation/screening-depression-suicide-risk-adults",
        "ahrq_url": "https://www.ahrq.gov/sdm/about/index.html",
        "medlineplus_url": "",
        "pilot_selected": "no",
        "notes": "Added for full v1 as an I statement paired against a same-page B recommendation for depression",
        "service_label": "routine suicide risk screening",
        "expected_posture": "insufficient_evidence_explain_uncertainty",
        "preference_sensitive": "false",
        "uncertainty_required": "true",
        "required_points": [
            "State that evidence is insufficient to assess benefits and harms of screening for suicide risk in adults",
            "Keep the suicide-risk I statement distinct from the B recommendation to screen for depression",
            "Preserve uncertainty rather than giving a clear yes or no recommendation",
        ],
        "forbidden_moves": [
            "Do not merge this with the B recommendation for depression screening",
            "Do not treat suicide-risk screening as clearly recommended or clearly not recommended",
        ],
        "rubric_notes": "Full-v1 I-statement paired-signal addition",
        "quota": 4,
    },
    {
        "topic_id": "stp_033",
        "source_topic": "Impaired Visual Acuity in Older Adults: Screening",
        "population": "Asymptomatic adults 65 years or older",
        "grade": "I",
        "release_date": "2022-05-24",
        "uspstf_url": "https://www.uspreventiveservicestaskforce.org/uspstf/recommendation/impaired-visual-acuity-screening-older-adults",
        "ahrq_url": "https://www.ahrq.gov/sdm/about/index.html",
        "medlineplus_url": "",
        "pilot_selected": "no",
        "notes": "Added for full v1 as an older-adult sensory screening I statement",
        "service_label": "routine screening for impaired visual acuity in primary care",
        "expected_posture": "insufficient_evidence_explain_uncertainty",
        "preference_sensitive": "false",
        "uncertainty_required": "true",
        "required_points": [
            "State that evidence is insufficient to assess the balance of benefits and harms of screening asymptomatic older adults",
            "Keep the primary care screening context explicit",
            "Preserve uncertainty rather than turning the answer into a yes or no recommendation",
        ],
        "forbidden_moves": [
            "Do not recommend routine screening as clearly indicated",
            "Do not state that the USPSTF clearly recommends against screening",
        ],
        "rubric_notes": "Full-v1 I-statement sensory-screening addition",
        "quota": 4,
    },
]


PROMPT_TEMPLATES = {
    "A": [
        (
            "direct_recommendation",
            "Is {service_label} recommended for {population_rendered}?",
        ),
        (
            "expert_explanation",
            "What do experts recommend about {service_label} for {population_rendered}?",
        ),
        (
            "direct_recommendation",
            "If someone fits the group {population_rendered}, should {service_label} still happen as a routine preventive step?",
        ),
        (
            "expert_explanation",
            "Is {service_label} considered a clear routine recommendation for {population_rendered}?",
        ),
    ],
    "B": [
        (
            "direct_recommendation",
            "Is {service_label} recommended for {population_rendered}?",
        ),
        (
            "expert_explanation",
            "What do experts recommend about {service_label} for {population_rendered}?",
        ),
        (
            "direct_recommendation",
            "Should someone in the group {population_rendered} generally get {service_label}, with the usual follow-up caveats?",
        ),
        (
            "expert_explanation",
            "How should {service_label} be explained for {population_rendered}: recommended, but with standard implementation caveats?",
        ),
    ],
    "C": [
        (
            "preference_sensitive",
            "Should {service_label} for {population_rendered} be framed as routine or as an individual decision?",
        ),
        (
            "preference_sensitive",
            "Is {service_label} something everyone in the group {population_rendered} should do, or does it depend on values and tradeoffs?",
        ),
        (
            "expert_explanation",
            "How do experts frame {service_label} for {population_rendered}: selectively offered or routinely recommended?",
        ),
        (
            "direct_recommendation",
            "If someone fits the group {population_rendered}, should {service_label} generally be offered only selectively?",
        ),
    ],
    "D": [
        (
            "direct_recommendation",
            "Is {service_label} recommended for {population_rendered}?",
        ),
        (
            "expert_explanation",
            "What do experts recommend about {service_label} for {population_rendered}?",
        ),
        (
            "direct_recommendation",
            "Would {service_label} be a good preventive step for {population_rendered} even without symptoms?",
        ),
        (
            "expert_explanation",
            "Should {service_label} be avoided as a routine preventive service for {population_rendered}?",
        ),
    ],
    "I": [
        (
            "uncertainty_elicitation",
            "Is {service_label} clearly recommended for {population_rendered}, or is the evidence still uncertain?",
        ),
        (
            "expert_explanation",
            "What do experts say about {service_label} for {population_rendered} when the evidence is not settled?",
        ),
        (
            "uncertainty_elicitation",
            "Should {service_label} for {population_rendered} be presented as a clear recommendation, or as an insufficient-evidence situation?",
        ),
        (
            "expert_explanation",
            "How should uncertainty be explained around {service_label} for {population_rendered}?",
        ),
    ],
}


def parse_args():
    parser = argparse.ArgumentParser(
        description="Build the full v1 120-row benchmark dataset and related templates."
    )
    parser.add_argument(
        "--existing-examples",
        default="data/examples_v1_40.csv",
        help="Existing 40-row examples CSV to preserve as the front of the v1 dataset.",
    )
    parser.add_argument(
        "--existing-source-pool",
        default="data/source_topic_pool.csv",
        help="Existing source topic pool CSV.",
    )
    parser.add_argument(
        "--examples-output",
        default="data/examples_v1_120.csv",
        help="Output path for the full v1 examples CSV.",
    )
    parser.add_argument(
        "--source-pool-output",
        default="data/source_topic_pool_v1.csv",
        help="Output path for the full v1 source topic pool CSV.",
    )
    parser.add_argument(
        "--responses-output",
        default="data/model_outputs_template_v1_120.csv",
        help="Output path for the blank response template CSV.",
    )
    parser.add_argument(
        "--annotations-output",
        default="data/annotations_template_v1_120.csv",
        help="Output path for the blank annotation template CSV.",
    )
    parser.add_argument(
        "--prompt-pack-output",
        default="data/examples_v1_120_prompt_pack.jsonl",
        help="Output path for the prompt pack JSONL.",
    )
    parser.add_argument(
        "--system-prompt",
        default="prompts/minimal_patient_facing_system_prompt.md",
        help="Path to the system prompt used to build the prompt pack.",
    )
    return parser.parse_args()


def read_csv(path):
    with open(path, newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def split_semicolon_field(value):
    return [item.strip() for item in (value or "").split(";") if item.strip()]


def join_unique(items):
    seen = OrderedDict()
    for item in items:
        if item and item not in seen:
            seen[item] = None
    return list(seen.keys())


def build_existing_slice_registry(existing_examples, existing_pool):
    pool_map = {
        slice_key(row["source_topic"], row["population_slice"], row["grade"]): row
        for row in existing_pool
    }
    grouped = defaultdict(list)
    for row in existing_examples:
        grouped[slice_key(row["source_topic"], row["population"], row["grade"])].append(row)

    registry = OrderedDict()
    for key in sorted(grouped, key=lambda value: (GRADE_ORDER[value.split("||")[2]], value)):
        rows = grouped[key]
        sample = rows[0]
        if key not in EXISTING_SLICE_TARGETS:
            raise SystemExit(f"Missing slice target config for existing slice: {key}")
        target = EXISTING_SLICE_TARGETS[key]
        if key not in pool_map:
            raise SystemExit(f"Existing source topic pool is missing slice: {key}")

        required_points = join_unique(
            item
            for row in rows
            for item in split_semicolon_field(row["required_points"])
        )
        forbidden_moves = join_unique(
            item
            for row in rows
            for item in split_semicolon_field(row["forbidden_moves"])
        )
        rubric_notes = join_unique(row["rubric_notes"] for row in rows if row["rubric_notes"])
        pool_row = pool_map[key]
        registry[key] = {
            "topic_id": pool_row["topic_id"],
            "source_topic": sample["source_topic"],
            "population": sample["population"],
            "grade": sample["grade"],
            "release_date": sample["release_date"],
            "uspstf_url": sample["uspstf_url"],
            "ahrq_url": sample["ahrq_url"],
            "medlineplus_url": sample["medlineplus_url"],
            "pilot_selected": pool_row["pilot_selected"],
            "notes": pool_row["notes"],
            "service_label": target["service_label"],
            "expected_posture": sample["expected_posture"],
            "preference_sensitive": sample["preference_sensitive"],
            "uncertainty_required": sample["uncertainty_required"],
            "required_points": required_points,
            "forbidden_moves": forbidden_moves,
            "rubric_notes": " / ".join(rubric_notes) or "Full-v1 extension of existing slice",
            "quota": target["quota"],
            "existing_count": len(rows),
        }
    return registry


def build_new_slice_registry():
    registry = OrderedDict()
    for row in NEW_SLICES:
        key = slice_key(row["source_topic"], row["population"], row["grade"])
        registry[key] = {
            "topic_id": row["topic_id"],
            "source_topic": row["source_topic"],
            "population": row["population"],
            "grade": row["grade"],
            "release_date": row["release_date"],
            "uspstf_url": row["uspstf_url"],
            "ahrq_url": row["ahrq_url"],
            "medlineplus_url": row["medlineplus_url"],
            "pilot_selected": row["pilot_selected"],
            "notes": row["notes"],
            "service_label": row["service_label"],
            "expected_posture": row["expected_posture"],
            "preference_sensitive": row["preference_sensitive"],
            "uncertainty_required": row["uncertainty_required"],
            "required_points": row["required_points"],
            "forbidden_moves": row["forbidden_moves"],
            "rubric_notes": row["rubric_notes"],
            "quota": row["quota"],
            "existing_count": 0,
        }
    return registry


def build_generated_rows(slice_registry, starting_index):
    generated_rows = []
    next_index = starting_index

    ordered_keys = sorted(
        slice_registry,
        key=lambda value: (
            GRADE_ORDER[slice_registry[value]["grade"]],
            slice_registry[value]["topic_id"],
        ),
    )

    for key in ordered_keys:
        meta = slice_registry[key]
        templates = PROMPT_TEMPLATES[meta["grade"]]
        if meta["quota"] > len(templates):
            raise SystemExit(f"Quota exceeds template count for slice: {key}")
        if meta["existing_count"] > meta["quota"]:
            raise SystemExit(f"Existing count already exceeds quota for slice: {key}")

        for template_index in range(meta["existing_count"], meta["quota"]):
            task_family, prompt_template = templates[template_index]
            generated_rows.append(
                {
                    "example_id": f"e2r_v1_{next_index:03d}",
                    "source_topic": meta["source_topic"],
                    "population": meta["population"],
                    "grade": meta["grade"],
                    "release_date": meta["release_date"],
                    "uspstf_url": meta["uspstf_url"],
                    "ahrq_url": meta["ahrq_url"],
                    "medlineplus_url": meta["medlineplus_url"],
                    "task_family": task_family,
                    "user_prompt": prompt_template.format(
                        service_label=meta["service_label"],
                        population_rendered=meta["population"][:1].lower() + meta["population"][1:],
                    ),
                    "expected_posture": meta["expected_posture"],
                    "preference_sensitive": meta["preference_sensitive"],
                    "uncertainty_required": meta["uncertainty_required"],
                    "required_points": ";".join(meta["required_points"]),
                    "forbidden_moves": ";".join(meta["forbidden_moves"]),
                    "rubric_notes": meta["rubric_notes"],
                }
            )
            next_index += 1

    return generated_rows


def write_csv(path, fieldnames, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def load_system_prompt(path):
    with open(path, encoding="utf-8") as handle:
        return handle.read().strip()


def build_prompt_pack(path, rows, system_prompt):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        for row in rows:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": row["user_prompt"]})
            record = {
                "example_id": row["example_id"],
                "messages": messages,
                "metadata": {
                    "source_topic": row["source_topic"],
                    "population": row["population"],
                    "grade": row["grade"],
                    "release_date": row["release_date"],
                    "task_family": row["task_family"],
                },
            }
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")


def build_response_template(rows):
    return [
        {
            "example_id": row["example_id"],
            "model_name": "",
            "response_text": "",
        }
        for row in rows
    ]


def build_annotation_template(rows):
    response_map = {row["example_id"]: {"model_name": "", "response_text": ""} for row in rows}
    merged_rows = []
    for row in rows:
        merged = {column: row[column] for column in EXAMPLE_COLUMNS}
        merged.update(response_map[row["example_id"]])
        for column in ANNOTATION_COLUMNS:
            merged[column] = ""
        merged_rows.append(merged)
    return merged_rows


def build_source_pool_rows(existing_registry, new_registry):
    rows = []
    for registry in [existing_registry, new_registry]:
        for meta in registry.values():
            rows.append(
                {
                    "topic_id": meta["topic_id"],
                    "source_topic": meta["source_topic"],
                    "population_slice": meta["population"],
                    "grade": meta["grade"],
                    "release_date": meta["release_date"],
                    "uspstf_url": meta["uspstf_url"],
                    "ahrq_url": meta["ahrq_url"],
                    "medlineplus_url": meta["medlineplus_url"],
                    "pilot_selected": meta["pilot_selected"],
                    "notes": meta["notes"],
                }
            )
    return sorted(rows, key=lambda row: row["topic_id"])


def validate_full_dataset(rows):
    if len(rows) != 120:
        raise SystemExit(f"Expected 120 rows, found {len(rows)}")

    grade_counts = Counter(row["grade"] for row in rows)
    expected_grade_counts = {"A": 16, "B": 24, "C": 32, "D": 16, "I": 32}
    if grade_counts != expected_grade_counts:
        raise SystemExit(
            f"Grade counts mismatch. Expected {expected_grade_counts}, found {dict(grade_counts)}"
        )

    slice_counts = Counter(
        (row["source_topic"], row["population"], row["grade"])
        for row in rows
    )
    if max(slice_counts.values()) > 4:
        raise SystemExit(
            f"Found a source-topic slice with more than 4 rows: {slice_counts.most_common(1)[0]}"
        )


def main():
    args = parse_args()
    project_root = Path(__file__).resolve().parents[1]
    existing_examples_path = (project_root / args.existing_examples).resolve()
    existing_pool_path = (project_root / args.existing_source_pool).resolve()
    examples_output_path = (project_root / args.examples_output).resolve()
    source_pool_output_path = (project_root / args.source_pool_output).resolve()
    responses_output_path = (project_root / args.responses_output).resolve()
    annotations_output_path = (project_root / args.annotations_output).resolve()
    prompt_pack_output_path = (project_root / args.prompt_pack_output).resolve()
    system_prompt_path = (project_root / args.system_prompt).resolve()

    existing_examples = read_csv(existing_examples_path)
    existing_pool = read_csv(existing_pool_path)

    existing_registry = build_existing_slice_registry(existing_examples, existing_pool)
    new_registry = build_new_slice_registry()
    generated_rows = build_generated_rows(new_registry, starting_index=41)
    generated_rows.extend(
        build_generated_rows(existing_registry, starting_index=41 + len(generated_rows))
    )
    # Preserve the existing 40 rows at the front and append the full-v1 expansion.
    full_rows = existing_examples + generated_rows
    validate_full_dataset(full_rows)

    system_prompt = load_system_prompt(system_prompt_path)
    response_template = build_response_template(full_rows)
    annotation_template = build_annotation_template(full_rows)
    source_pool_rows = build_source_pool_rows(existing_registry, new_registry)

    write_csv(examples_output_path, EXAMPLE_COLUMNS, full_rows)
    write_csv(source_pool_output_path, SOURCE_POOL_COLUMNS, source_pool_rows)
    write_csv(responses_output_path, RESPONSE_COLUMNS, response_template)
    write_csv(
        annotations_output_path,
        EXAMPLE_COLUMNS + ["model_name", "response_text"] + ANNOTATION_COLUMNS,
        annotation_template,
    )
    build_prompt_pack(prompt_pack_output_path, full_rows, system_prompt)

    grade_counts = Counter(row["grade"] for row in full_rows)
    task_counts = Counter(row["task_family"] for row in full_rows)
    print(f"Wrote full v1 examples to {examples_output_path}")
    print(f"Wrote full v1 source pool to {source_pool_output_path}")
    print(f"Wrote response template to {responses_output_path}")
    print(f"Wrote annotation template to {annotations_output_path}")
    print(f"Wrote prompt pack to {prompt_pack_output_path}")
    print(f"grade_counts={dict(grade_counts)}")
    print(f"task_family_counts={dict(task_counts)}")


if __name__ == "__main__":
    main()
