"""
OET Sample Exam Reference System
================================
Authentic sample content for OET exam generation.
These serve as reference templates to guide AI generation.
"""

from typing import Dict, List, Any
from dataclasses import dataclass, field
from enum import Enum

from .oet_specifications import OETHealthcareProfession, OETSection


# ============================================================
# WRITING SAMPLES - CASE NOTES AND MODEL LETTERS
# ============================================================

@dataclass
class OETWritingSample:
    """Complete OET Writing sample with case notes and model letter"""
    profession: OETHealthcareProfession
    letter_type: str
    case_notes: str
    model_letter: str
    writing_tips: List[str]
    common_errors: List[str]


OET_WRITING_SAMPLES: Dict[str, OETWritingSample] = {

    "nursing_referral_1": OETWritingSample(
        profession=OETHealthcareProfession.NURSING,
        letter_type="referral",
        case_notes="""
PATIENT DETAILS
Name: Margaret Chen
DOB: 15/03/1952 (72 years old)
Address: 45 Riverside Drive, Eastwood
Hospital Number: MH-789456

ADMISSION DETAILS
Date of admission: 10/01/2026
Ward: Medical Ward 3B
Consultant: Dr. Sarah Williams

PRESENTING COMPLAINT
• Fall at home - found on floor by daughter
• Unable to weight-bear on right leg
• Confused on arrival

MEDICAL HISTORY
• Type 2 diabetes mellitus (15 years)
• Hypertension
• Mild cognitive impairment (diagnosed 2024)
• Osteoporosis
• Previous falls x2 in past 6 months

MEDICATIONS ON ADMISSION
• Metformin 500mg BD
• Lisinopril 10mg OD
• Amlodipine 5mg OD
• Vitamin D 1000IU OD

INVESTIGATIONS
• X-ray right hip: Intertrochanteric fracture
• Blood glucose on admission: 14.2 mmol/L
• HbA1c: 8.2%
• eGFR: 58 (Stage 3a CKD)

SURGICAL INTERVENTION
• 12/01/2026: Right hip hemiarthroplasty
• Procedure uneventful
• Post-op: Mobilising with frame + assistance of 2

CURRENT STATUS (18/01/2026)
• Wound healing well, clips intact
• Pain controlled with regular paracetamol
• Blood glucose stabilising (7-10 mmol/L)
• Requires assistance with ADLs
• Confusion improved but still disorientated to time
• Family concerned about future care needs

SOCIAL HISTORY
• Lives alone in two-storey house
• Daughter visits twice weekly
• Previously independent with shopping/cooking
• No formal care package

DISCHARGE PLAN
• Referral to rehabilitation unit for ongoing therapy
• Occupational therapy home assessment required
• Review of diabetes management
• Falls prevention programme

WRITING TASK
Using the information given in the case notes, write a referral letter to the Charge Nurse at Greenfield Rehabilitation Unit, requesting acceptance for rehabilitation following hip surgery. Address the letter to Ms. Patricia Morrison, Charge Nurse.
        """,
        model_letter="""
18 January 2026

Ms. Patricia Morrison
Charge Nurse
Greenfield Rehabilitation Unit
Eastwood General Hospital

Dear Ms. Morrison,

Re: Margaret Chen, DOB 15/03/1952
Hospital Number: MH-789456

I am writing to refer Mrs. Chen for rehabilitation following a right hip hemiarthroplasty performed on 12 January 2026 after an intertrochanteric fracture sustained in a fall at home.

Mrs. Chen is a 72-year-old woman with a background of type 2 diabetes, hypertension, osteoporosis, and mild cognitive impairment. She has experienced two previous falls in the past six months, and this latest incident has raised significant concerns regarding her safety at home.

Currently, Mrs. Chen is mobilising with a walking frame and requires assistance of two staff members. Her surgical wound is healing satisfactorily, and her pain is well controlled with regular paracetamol. Her blood glucose levels have stabilised between 7-10 mmol/L, although her HbA1c of 8.2% suggests her diabetes management may need review.

Cognitively, while her confusion has improved since admission, she remains disorientated to time. She requires assistance with all activities of daily living and will need a comprehensive occupational therapy assessment before returning home, where she currently lives alone in a two-storey house.

I would be grateful if you could accept Mrs. Chen for rehabilitation to optimise her mobility and functional independence. A falls prevention programme would also be beneficial given her history. Her daughter visits regularly and is engaged with discharge planning.

Please do not hesitate to contact me should you require any further information.

Yours sincerely,

[Nurse Name]
Registered Nurse
Medical Ward 3B
        """,
        writing_tips=[
            "Start with the reason for referral in the first paragraph",
            "Include relevant medical history that impacts rehabilitation",
            "Describe current functional status clearly",
            "Mention social circumstances affecting discharge",
            "End with a clear request and offer of further communication"
        ],
        common_errors=[
            "Including irrelevant information from case notes",
            "Using bullet points instead of flowing paragraphs",
            "Forgetting to include patient identifiers in Re: line",
            "Not stating the purpose of the referral clearly",
            "Exceeding the word limit significantly"
        ]
    ),

    "medicine_discharge_1": OETWritingSample(
        profession=OETHealthcareProfession.MEDICINE,
        letter_type="discharge",
        case_notes="""
PATIENT DETAILS
Name: Robert Thompson
DOB: 22/08/1965 (60 years old)
Address: 12 Oak Street, Northside
NHS Number: 485 293 7721

ADMISSION DETAILS
Date of admission: 05/01/2026
Date of discharge: 15/01/2026
Consultant: Dr. James Patel
Ward: Coronary Care Unit then Cardiology Ward

PRESENTING COMPLAINT
• Sudden onset central chest pain (crushing character)
• Radiating to left arm
• Associated with sweating and nausea
• Pain score 8/10 on arrival

DIAGNOSIS
ST-Elevation Myocardial Infarction (STEMI) - Anterior wall

MEDICAL HISTORY
• Hypercholesterolaemia (untreated - patient declined statins previously)
• Hypertension (poorly controlled)
• Current smoker: 30 pack-years
• BMI: 32
• No known diabetes
• Family history: Father died of MI age 58

INVESTIGATIONS
• ECG: ST elevation V1-V4, Q waves developing
• Troponin: Initial 45 ng/L, Peak 4500 ng/L
• Echocardiogram: EF 40%, anterior wall hypokinesis
• Angiogram: 95% LAD occlusion

TREATMENT
• Emergency PCI with drug-eluting stent to LAD
• Procedure successful, TIMI 3 flow achieved
• In-hospital: IV heparin, aspirin, ticagrelor loading

DISCHARGE MEDICATIONS
• Aspirin 75mg OD (lifelong)
• Ticagrelor 90mg BD (12 months)
• Atorvastatin 80mg nocte
• Ramipril 2.5mg OD (titrate up)
• Bisoprolol 2.5mg OD (titrate up)
• GTN spray PRN

DISCHARGE STATUS
• Chest pain free
• Mobilising independently on ward
• BP: 128/78 mmHg
• HR: 68 bpm, sinus rhythm
• Patient counselled on smoking cessation - given Quitline number
• Referred to cardiac rehabilitation

FOLLOW-UP
• Cardiology outpatients: 6 weeks
• GP review: 1 week for BP and medication titration
• Cardiac rehabilitation: Letter sent separately

WRITING TASK
Using the information in the case notes, write a discharge letter to Mr. Thompson's GP, Dr. Helen Fraser, at Northside Medical Centre.
        """,
        model_letter="""
15 January 2026

Dr. Helen Fraser
Northside Medical Centre
58 High Street
Northside

Dear Dr. Fraser,

Re: Robert Thompson, DOB 22/08/1965
NHS Number: 485 293 7721

I am writing to inform you of Mr. Thompson's recent admission to our cardiology unit following an ST-elevation myocardial infarction involving the anterior wall.

Mr. Thompson, a 60-year-old gentleman with a background of untreated hypercholesterolaemia and poorly controlled hypertension, presented on 5 January 2026 with acute crushing central chest pain radiating to his left arm. Emergency angiography revealed a 95% occlusion of the left anterior descending artery, which was successfully treated with primary percutaneous coronary intervention and insertion of a drug-eluting stent.

His post-procedural echocardiogram demonstrated an ejection fraction of 40% with anterior wall hypokinesis. He recovered well and has been discharged on dual antiplatelet therapy with aspirin 75mg once daily and ticagrelor 90mg twice daily, along with atorvastatin 80mg at night, ramipril 2.5mg once daily, and bisoprolol 2.5mg once daily. He also has GTN spray for use as required.

Given his significant cardiovascular risk factors, including a 30 pack-year smoking history and BMI of 32, intensive lifestyle modification has been discussed. He has been provided with smoking cessation resources and referred to our cardiac rehabilitation programme.

I would be grateful if you could review Mr. Thompson in one week to assess his blood pressure and consider uptitration of his ramipril and bisoprolol as tolerated. He has a cardiology outpatient appointment scheduled in six weeks.

Please contact us if you have any concerns.

Yours sincerely,

[Doctor Name]
Cardiology Registrar
Eastwood General Hospital
        """,
        writing_tips=[
            "State the diagnosis clearly and early in the letter",
            "Summarise the key interventions performed",
            "List discharge medications with dosages",
            "Clearly state what action is needed from the GP",
            "Include relevant follow-up arrangements"
        ],
        common_errors=[
            "Omitting the diagnosis or treatment details",
            "Not specifying which medications need titration",
            "Failing to mention lifestyle factors and advice given",
            "Forgetting follow-up arrangements",
            "Using excessive medical abbreviations without explanation"
        ]
    ),

    "pharmacy_medication_review_1": OETWritingSample(
        profession=OETHealthcareProfession.PHARMACY,
        letter_type="referral",
        case_notes="""
PATIENT DETAILS
Name: Dorothy Williams
DOB: 03/06/1940 (85 years old)
Address: Sunny View Aged Care Facility, Room 24
Medicare Number: 4856 29384 5

REASON FOR REVIEW
Nursing staff concerns about medication burden and recent confusion episodes

CURRENT MEDICATIONS (14 regular medications)
• Aspirin 100mg OD
• Atorvastatin 40mg nocte
• Metoprolol 50mg BD
• Perindopril 4mg OD
• Frusemide 40mg mane
• Spironolactone 25mg OD
• Digoxin 125mcg OD
• Warfarin (variable dose - INR target 2-3)
• Esomeprazole 20mg OD
• Paracetamol 1g QID
• Oxycodone 5mg PRN (using 2-3 times daily)
• Temazepam 10mg nocte
• Risperidone 0.5mg nocte
• Coloxyl with senna 2 nocte

MEDICAL HISTORY
• Atrial fibrillation
• Congestive heart failure (EF 35%)
• Hypertension
• Osteoarthritis (knees, hips)
• GORD
• Anxiety
• Chronic constipation
• Recurrent UTIs

RECENT ISSUES
• Three falls in past month (no injury)
• Episodes of confusion - worse in evenings
• INR unstable (range 1.8-4.2 over past month)
• Daytime drowsiness
• Poor appetite
• Recent UTI treated with trimethoprim

OBSERVATIONS
• BP sitting: 105/62 mmHg
• BP standing: 88/55 mmHg (symptomatic)
• HR: 52 bpm, irregular
• Weight: 52kg (down 3kg in 2 months)
• eGFR: 38 mL/min (Stage 3b CKD)

INVESTIGATIONS
• Digoxin level: 2.4 nmol/L (therapeutic 1.0-2.0)
• INR today: 3.8
• Potassium: 5.4 mmol/L
• Sodium: 132 mmol/L

WRITING TASK
Write a letter to Mrs. Williams' GP, Dr. Michael O'Brien, at Greenwood Medical Practice, regarding your medication review findings and recommendations.
        """,
        model_letter="""
16 January 2026

Dr. Michael O'Brien
Greenwood Medical Practice
120 Main Road
Greenwood

Dear Dr. O'Brien,

Re: Dorothy Williams, DOB 03/06/1940
Medicare Number: 4856 29384 5
Resident at Sunny View Aged Care Facility, Room 24

I am writing following a medication review requested due to nursing staff concerns about Mrs. Williams' medication burden, recent falls, and episodes of confusion.

Mrs. Williams is currently prescribed 14 regular medications. My review has identified several significant concerns requiring attention.

Firstly, her digoxin level of 2.4 nmol/L is above the therapeutic range and likely contributing to her bradycardia (heart rate 52 bpm), nausea, and confusion. Given her reduced renal function with eGFR of 38, I recommend withholding digoxin and rechecking levels in 5-7 days before considering a reduced dose.

Secondly, she demonstrates significant postural hypotension with symptomatic blood pressure drop from 105/62 sitting to 88/55 standing. This is likely contributing to her falls. Consider reducing or withholding frusemide temporarily, particularly given her recent weight loss and hypotension.

Thirdly, her combination of sedating medications - temazepam, risperidone, and regular oxycodone - significantly increases falls risk and likely contributes to her evening confusion. I recommend gradual withdrawal of temazepam and review of risperidone indication with consideration of deprescribing.

Additionally, her hyperkalaemia (potassium 5.4 mmol/L) on the combination of spironolactone and perindopril in the context of CKD requires monitoring. Consider reducing spironolactone if potassium remains elevated.

Finally, her unstable INR warrants review of warfarin indication given her falls risk. A HAS-BLED score assessment may support consideration of alternative anticoagulation strategies.

I am happy to discuss these recommendations further at your convenience.

Yours sincerely,

[Pharmacist Name]
Clinical Pharmacist
        """,
        writing_tips=[
            "Prioritise the most clinically significant issues",
            "Link medications to observed problems",
            "Provide specific, actionable recommendations",
            "Consider renal function when discussing dose adjustments",
            "Acknowledge complexity and offer to discuss further"
        ],
        common_errors=[
            "Listing all medications without prioritising concerns",
            "Not linking drug therapy to clinical problems",
            "Making recommendations without considering comorbidities",
            "Ignoring drug-drug interactions",
            "Being too vague about recommended actions"
        ]
    ),
}


# ============================================================
# LISTENING SAMPLES - CONSULTATION EXTRACTS
# ============================================================

@dataclass
class OETListeningSample:
    """OET Listening sample with transcript and questions"""
    part: str  # part_a, part_b, part_c
    profession: OETHealthcareProfession
    context: str
    audio_transcript: str
    questions: List[Dict[str, Any]]
    answers: List[str]


OET_LISTENING_SAMPLES: Dict[str, OETListeningSample] = {

    "nursing_part_a_consultation_1": OETListeningSample(
        part="part_a",
        profession=OETHealthcareProfession.NURSING,
        context="Nurse conducting admission assessment in Emergency Department",
        audio_transcript="""
NURSE: Good afternoon, I'm Sarah, one of the nurses here in Emergency. Can you tell me your full name and date of birth?

PATIENT: It's Peter Mitchell. Born 14th of May 1978.

NURSE: Thank you, Mr Mitchell. And what's brought you in today?

PATIENT: I've had this really bad pain in my stomach for the last, I don't know, maybe six hours or so. Started after lunch.

NURSE: Can you show me where exactly the pain is?

PATIENT: It started here, around my belly button, but now it's moved down to the right side, down here.

NURSE: And how would you describe the pain? Is it sharp, dull, cramping?

PATIENT: It's sharp, really sharp. It's constant but gets worse if I move or cough. I'd say it's about 8 out of 10 right now.

NURSE: Have you had any other symptoms? Nausea, vomiting, fever?

PATIENT: Yeah, I've felt really sick. I vomited twice on the way here. And I've had no appetite at all since this morning. I think I might have a temperature too because I've been feeling hot and cold.

NURSE: When did you last open your bowels?

PATIENT: Yesterday morning, I think. That was normal.

NURSE: Any blood in your stool or urine?

PATIENT: No, nothing like that.

NURSE: Have you had your appendix out or any other abdominal surgery?

PATIENT: No, never had any operations.

NURSE: Are you taking any regular medications?

PATIENT: Just blood pressure tablets. Ramipril, I think it's called. 5 milligrams once a day.

NURSE: Any allergies?

PATIENT: Penicillin. I came out in a rash when I was a kid.

NURSE: I'm just going to take your observations now. Your temperature is 38.2, blood pressure 145 over 88, pulse 96, and your oxygen levels are fine at 98%. The doctor will be in to see you shortly, but based on your symptoms, they'll likely want to do some blood tests and possibly a scan of your abdomen.
        """,
        questions=[
            {"number": 1, "question": "Time since pain started:", "answer_type": "note_completion"},
            {"number": 2, "question": "Original location of pain:", "answer_type": "note_completion"},
            {"number": 3, "question": "Current location of pain:", "answer_type": "note_completion"},
            {"number": 4, "question": "Character of pain:", "answer_type": "note_completion"},
            {"number": 5, "question": "Pain score:", "answer_type": "note_completion"},
            {"number": 6, "question": "Number of vomiting episodes:", "answer_type": "note_completion"},
            {"number": 7, "question": "Last bowel motion:", "answer_type": "note_completion"},
            {"number": 8, "question": "Regular medication:", "answer_type": "note_completion"},
            {"number": 9, "question": "Medication dose:", "answer_type": "note_completion"},
            {"number": 10, "question": "Allergy:", "answer_type": "note_completion"},
            {"number": 11, "question": "Type of allergic reaction:", "answer_type": "note_completion"},
            {"number": 12, "question": "Temperature:", "answer_type": "note_completion"},
        ],
        answers=[
            "six hours / 6 hours",
            "belly button / around belly button / umbilicus",
            "right side / right lower / lower right",
            "sharp / constant",
            "8 out of 10 / 8/10",
            "twice / two / 2",
            "yesterday morning",
            "ramipril",
            "5 milligrams / 5mg / 5 mg",
            "penicillin",
            "rash",
            "38.2 / 38.2°C"
        ]
    ),

    "pharmacy_part_b_workplace_1": OETListeningSample(
        part="part_b",
        profession=OETHealthcareProfession.PHARMACY,
        context="Pharmacist discussion with colleague about prescription issue",
        audio_transcript="""
PHARMACIST 1: Have you got a minute? I need a second opinion on this prescription.

PHARMACIST 2: Sure, what's the problem?

PHARMACIST 1: It's for a regular patient, Mrs. Davidson. She's been on methotrexate for her rheumatoid arthritis for years - 15 milligrams once weekly. But this new prescription from the hospital says 15 milligrams daily.

PHARMACIST 2: That's definitely an error. Daily methotrexate at that dose would be toxic. It has to be once weekly for RA.

PHARMACIST 1: That's what I thought. I've tried calling the hospital pharmacy but they're not answering. The rheumatology clinic is closed today.

PHARMACIST 2: Have you checked her previous dispensing history?

PHARMACIST 1: Yes, she's been on 15 milligrams once weekly for the past three years, always dispensed as weekly.

PHARMACIST 2: Right, so this is clearly a transcription error. I'd say dispense her usual weekly supply and flag this with the GP and hospital. Document everything.

PHARMACIST 1: Should I contact the GP today?

PHARMACIST 2: Absolutely. This needs to be corrected before someone else dispenses it incorrectly. Methotrexate errors have caused fatalities before.
        """,
        questions=[
            {
                "number": 1,
                "question": "What is the pharmacist's main concern?",
                "options": [
                    "A. The medication has been discontinued",
                    "B. The dosing frequency appears incorrect",
                    "C. The patient has developed an allergy"
                ],
                "answer_type": "multiple_choice"
            }
        ],
        answers=["B"]
    ),
}


# ============================================================
# READING SAMPLES - TEXT EXTRACTS
# ============================================================

@dataclass
class OETReadingSample:
    """OET Reading sample with text and questions"""
    part: str
    text_type: str
    title: str
    text_content: str
    questions: List[Dict[str, Any]]
    answers: List[str]


OET_READING_SAMPLES: Dict[str, OETReadingSample] = {

    "part_b_clinical_guideline_1": OETReadingSample(
        part="part_b",
        text_type="clinical_guideline",
        title="Management of Diabetic Foot Ulcers in Primary Care",
        text_content="""
Diabetic foot ulcers (DFUs) represent one of the most serious complications of diabetes mellitus, affecting approximately 15-25% of people with diabetes during their lifetime. The development of a foot ulcer significantly increases the risk of lower limb amputation, with studies indicating that 85% of diabetes-related amputations are preceded by a foot ulcer. Early identification, appropriate classification, and prompt management are therefore essential components of diabetes care.

The pathogenesis of diabetic foot ulcers is multifactorial, involving the interplay of peripheral neuropathy, peripheral vascular disease, and mechanical stress. Peripheral neuropathy, present in approximately 50% of patients with long-standing diabetes, results in loss of protective sensation, allowing minor trauma to go unnoticed. Autonomic neuropathy contributes through altered sweating patterns and skin changes, while motor neuropathy leads to foot deformities that create areas of abnormal pressure loading.

Assessment and Classification

When a patient presents with a diabetic foot ulcer, a systematic assessment should be conducted. This begins with a thorough history, including diabetes duration, glycaemic control (HbA1c), previous ulceration or amputation, and current footwear. The ulcer should be assessed for location, size (measured in centimetres), depth (superficial, down to tendon or capsule, or down to bone), and the presence of infection or necrosis.

The Wagner classification system, while widely used, has limitations as it combines ulcer depth with the presence of infection and ischaemia. The University of Texas classification system addresses this by separately grading wound depth (0-3) and staging infection and ischaemia (A-D), providing better prognostic information. For example, a Texas grade 1B ulcer indicates a superficial wound with infection, while grade 2D indicates an ulcer penetrating to tendon or capsule with both infection and ischaemia.

Vascular assessment is critical, as peripheral arterial disease is present in up to 50% of patients with DFUs. This should include palpation of pedal pulses, measurement of ankle-brachial pressure index (ABPI), and assessment of toe pressures or transcutaneous oxygen measurements where available. An ABPI below 0.9 suggests peripheral arterial disease, while values above 1.3 may indicate arterial calcification, commonly seen in diabetes, which can give falsely elevated readings.

Management Principles

The management of diabetic foot ulcers rests on several key principles: offloading, wound care, infection management, vascular assessment and intervention, and metabolic control.

Offloading, or pressure redistribution, is perhaps the most important yet often neglected aspect of treatment. Total contact casting remains the gold standard for plantar forefoot ulcers, achieving healing rates of 80-90% in appropriate patients. However, it requires specialist expertise and is contraindicated in the presence of untreated infection or significant ischaemia. Alternative offloading devices include removable cast walkers, therapeutic footwear, and felted foam dressings, though adherence is often problematic with removable devices.

Wound care involves regular debridement of non-viable tissue, appropriate dressing selection, and maintenance of a moist wound environment. Sharp debridement should be performed by trained practitioners and is contraindicated in ischaemic wounds without prior vascular assessment. Modern wound dressings should be selected based on wound characteristics: hydrogels for dry wounds, alginates or foams for exudating wounds, and antimicrobial dressings where there is evidence of critical colonisation.

Infection management requires careful clinical assessment, as the classical signs of infection may be blunted in the diabetic foot due to neuropathy and impaired immune responses. The Infectious Diseases Society of America (IDSA) classification grades infection as mild (superficial with limited cellulitis), moderate (deeper infection or more extensive cellulitis), or severe (systemic signs of infection). Mild infections may be treated with oral antibiotics targeting gram-positive organisms, while moderate to severe infections typically require hospitalisation, intravenous antibiotics, and surgical assessment.

When to Refer

Prompt specialist referral is indicated in several circumstances: all newly identified ulcers for baseline assessment, ulcers not showing improvement after two weeks of appropriate treatment, all infected ulcers (moderate or severe), any ulcer with suspected osteomyelitis (probe to bone test positive, or visible bone), ulcers with significant ischaemia (absent pulses, ABPI <0.5, or rest pain), and rapidly deteriorating wounds or spreading infection. The multidisciplinary diabetic foot team, including vascular surgery, orthopaedics, podiatry, diabetes specialist nursing, and orthotics, provides the coordinated care necessary for complex cases.

Prevention

Perhaps most importantly, prevention of initial and recurrent ulceration should be a priority. This includes patient education about daily foot inspection, appropriate footwear, avoidance of barefoot walking, and prompt reporting of any foot problems. Healthcare providers should conduct annual foot examinations including monofilament testing for neuropathy and pulse palpation for vascular disease, with more frequent assessment in high-risk individuals. Patients identified as high-risk should receive podiatry input for nail care and callus management, as well as provision of therapeutic footwear.
        """,
        questions=[
            {
                "number": 1,
                "question": "According to the passage, what percentage of diabetes-related amputations follow a foot ulcer?",
                "answer_type": "short_answer"
            },
            {
                "number": 2,
                "question": "The author mentions that the Wagner classification system has limitations because it:",
                "options": [
                    "A. does not assess wound depth accurately",
                    "B. combines different assessment factors together",
                    "C. cannot be used for infected ulcers",
                    "D. requires specialist training to apply"
                ],
                "answer_type": "multiple_choice"
            },
            {
                "number": 3,
                "question": "What does an ABPI reading above 1.3 potentially indicate?",
                "answer_type": "short_answer"
            },
            {
                "number": 4,
                "question": "Total contact casting is described as the gold standard for plantar forefoot ulcers because:",
                "options": [
                    "A. it is the most cost-effective treatment option",
                    "B. it achieves the highest healing rates",
                    "C. it can be used in all patient groups",
                    "D. it does not require specialist expertise"
                ],
                "answer_type": "multiple_choice"
            },
            {
                "number": 5,
                "question": "According to the IDSA classification, which type of infection typically requires hospitalisation?",
                "answer_type": "short_answer"
            },
        ],
        answers=[
            "85% / 85 percent / eighty-five percent",
            "B",
            "arterial calcification",
            "B",
            "moderate to severe / moderate or severe"
        ]
    ),
}


# ============================================================
# SPEAKING SAMPLES - ROLEPLAY SCENARIOS
# ============================================================

@dataclass
class OETSpeakingSample:
    """OET Speaking roleplay sample"""
    profession: OETHealthcareProfession
    scenario_type: str
    setting: str
    candidate_card: str
    patient_card: str
    assessor_notes: List[str]


OET_SPEAKING_SAMPLES: Dict[str, OETSpeakingSample] = {

    "nursing_explanation_1": OETSpeakingSample(
        profession=OETHealthcareProfession.NURSING,
        scenario_type="explanation_of_diagnosis",
        setting="Hospital ward - patient newly diagnosed with Type 2 Diabetes",
        candidate_card="""
CANDIDATE CARD - NURSING

SETTING: Hospital medical ward

PATIENT: Mr. James Cooper, 58 years old, admitted with hyperglycaemic episode. Has been newly diagnosed with Type 2 Diabetes Mellitus. The doctor has explained the diagnosis, but the patient is still coming to terms with it. He is due for discharge tomorrow.

TASK:
• Explain what Type 2 Diabetes means in simple terms
• Discuss the importance of blood glucose monitoring
• Explain the prescribed medication (Metformin 500mg twice daily)
• Discuss necessary lifestyle modifications (diet, exercise)
• Address any concerns and provide reassurance
• Provide information about diabetes education classes and support groups

You have 5 minutes to complete this roleplay.
        """,
        patient_card="""
PATIENT CARD - MR. JAMES COOPER

You are James Cooper, a 58-year-old accountant. You were admitted to hospital after feeling very unwell - extremely thirsty, urinating frequently, and feeling exhausted. You have now been told you have Type 2 Diabetes.

BACKGROUND:
• You are shocked by the diagnosis - you thought diabetes only happened to overweight people, and while you could "lose a few kilos," you don't consider yourself obese
• You have a sedentary job and don't exercise much
• You enjoy a glass of wine with dinner most nights
• Your father had diabetes in his 70s and ended up with kidney problems and foot ulcers - this worries you greatly
• You're concerned about having to inject yourself with insulin

CONCERNS TO RAISE:
• Ask what caused this - "Why me?"
• Express fear about ending up like your father
• Ask if you'll have to give yourself injections
• Question whether you'll have to give up all the foods you enjoy
• Ask if diabetes can be cured

DEMEANOUR:
• Initially anxious and somewhat defensive
• Become more receptive as the nurse provides clear explanations and reassurance
• Ask questions throughout the conversation
        """,
        assessor_notes=[
            "Candidate should use clear, jargon-free language",
            "Should acknowledge patient's shock and concerns empathetically",
            "Must reassure about insulin - Type 2 often managed without",
            "Should explain lifestyle modifications positively, not punitively",
            "Should address the father's experience sensitively",
            "Must check understanding throughout"
        ]
    ),

    "medicine_breaking_bad_news_1": OETSpeakingSample(
        profession=OETHealthcareProfession.MEDICINE,
        scenario_type="breaking_bad_news",
        setting="Outpatient clinic - delivering cancer diagnosis",
        candidate_card="""
CANDIDATE CARD - MEDICINE

SETTING: Outpatient clinic room

PATIENT: Mrs. Patricia Morgan, 62 years old, has attended to receive results of investigations following her GP's referral for a persistent cough and weight loss. CT scan and bronchoscopy have confirmed lung cancer (non-small cell carcinoma). The cancer appears to be stage IIIA, meaning it may be treatable but not curable.

TASK:
• Establish what the patient already knows and expects
• Deliver the diagnosis sensitively using appropriate language
• Allow time for the patient to react and process the information
• Explain that further tests are needed to finalise staging
• Discuss that treatment options will be presented at the multidisciplinary team meeting
• Provide appropriate emotional support
• Arrange follow-up and provide contact information for support

You have 5 minutes to complete this roleplay.
        """,
        patient_card="""
PATIENT CARD - MRS. PATRICIA MORGAN

You are Patricia Morgan, a 62-year-old retired teacher. You have come to get the results of tests you had done two weeks ago for a cough that wouldn't go away and some weight loss you'd noticed.

BACKGROUND:
• You've had a nagging cough for about 4 months
• You've lost about 6 kg without trying
• You smoked for 30 years but quit 10 years ago
• You live with your husband who is waiting outside
• Deep down, you suspect it might be something serious, but you're hoping it's just an infection or something treatable

REACTIONS:
• When the doctor indicates they have serious news, become quiet and tense
• When you hear "cancer," you may need a moment - feel free to pause, become tearful, or ask "Are you sure?"
• Ask about your chances / survival
• Ask if the smoking caused this
• Ask if you should have come sooner - express guilt
• Ask what happens next

DEMEANOUR:
• Initially hopeful but increasingly anxious
• Emotional when receiving the diagnosis
• Want to know about treatment options and prognosis
        """,
        assessor_notes=[
            "Candidate should use a 'warning shot' before delivering diagnosis",
            "Must use clear language - say 'cancer', not just 'growth' or 'tumour'",
            "Should allow silence and emotional reaction",
            "Should not provide false reassurance about prognosis",
            "Must acknowledge patient's guilt about smoking sensitively",
            "Should offer to involve family member if patient wishes",
            "Must explain next steps clearly"
        ]
    ),

    "pharmacy_medication_counselling_1": OETSpeakingSample(
        profession=OETHealthcareProfession.PHARMACY,
        scenario_type="medication_counseling",
        setting="Community pharmacy - warfarin counselling for new patient",
        candidate_card="""
CANDIDATE CARD - PHARMACY

SETTING: Community pharmacy consultation room

PATIENT: Mr. David Chang, 70 years old, has been prescribed warfarin 5mg daily following a recent diagnosis of atrial fibrillation. He has come to collect his first prescription and requires counselling on this new medication.

TASK:
• Explain what warfarin is and why it has been prescribed
• Explain how to take the medication correctly
• Discuss the importance of regular INR monitoring
• Explain significant food and drug interactions
• Discuss signs of bleeding to watch for
• Ensure the patient understands the importance of informing all healthcare providers about warfarin
• Provide written information and contact details for queries

You have 5 minutes to complete this roleplay.
        """,
        patient_card="""
PATIENT CARD - MR. DAVID CHANG

You are David Chang, a 70-year-old retired chef. You've been told you have an irregular heartbeat and need to take a blood-thinning medication to prevent stroke.

BACKGROUND:
• You were diagnosed with atrial fibrillation last week
• You have never taken blood thinners before
• You take medication for high blood pressure and cholesterol
• You still enjoy cooking and eating a variety of foods, including lots of Asian vegetables and herbs
• You occasionally have a glass of wine or beer
• You're worried about the medication - you've heard it can cause bleeding

QUESTIONS/CONCERNS:
• Ask why you need a blood thinner
• Ask what happens if you miss a dose
• Ask about what foods you need to avoid - you've heard about vitamin K
• Ask if you can still have alcohol
• Express concern about bleeding - what if you cut yourself cooking?
• Ask how long you'll need to take this medication

DEMEANOUR:
• Cooperative but somewhat anxious about the new medication
• Keen to understand how to take it correctly
• Want practical advice about daily life with warfarin
        """,
        assessor_notes=[
            "Candidate should explain the purpose clearly (stroke prevention)",
            "Must emphasise consistent vitamin K intake rather than avoidance",
            "Should provide practical advice about green vegetables - consistency is key",
            "Must explain INR monitoring and its importance",
            "Should discuss alcohol in moderation",
            "Must explain what to do about missed doses",
            "Should explain bleeding signs without causing excessive alarm",
            "Must mention informing other healthcare providers, dentist, etc."
        ]
    ),
}


# ============================================================
# TOPIC BANK FOR CONTENT GENERATION
# ============================================================

OET_TOPICS_BY_PROFESSION: Dict[OETHealthcareProfession, List[Dict[str, Any]]] = {

    OETHealthcareProfession.NURSING: [
        {"topic": "Post-operative care", "subtopics": ["wound management", "pain assessment", "early mobilisation", "DVT prevention"], "difficulty": "intermediate"},
        {"topic": "Medication administration", "subtopics": ["IV therapy", "insulin administration", "controlled drugs", "medication errors"], "difficulty": "intermediate"},
        {"topic": "Patient deterioration", "subtopics": ["early warning scores", "escalation protocols", "sepsis recognition", "communication tools"], "difficulty": "advanced"},
        {"topic": "Discharge planning", "subtopics": ["patient education", "medication reconciliation", "community referrals", "carer support"], "difficulty": "intermediate"},
        {"topic": "Falls prevention", "subtopics": ["risk assessment", "environmental factors", "patient factors", "post-fall protocol"], "difficulty": "basic"},
        {"topic": "Pressure injury prevention", "subtopics": ["risk assessment", "skin inspection", "repositioning", "nutrition"], "difficulty": "intermediate"},
        {"topic": "Infection control", "subtopics": ["hand hygiene", "PPE", "isolation precautions", "outbreak management"], "difficulty": "basic"},
        {"topic": "End of life care", "subtopics": ["symptom management", "family support", "communication", "cultural considerations"], "difficulty": "advanced"},
    ],

    OETHealthcareProfession.MEDICINE: [
        {"topic": "Acute coronary syndrome", "subtopics": ["STEMI", "NSTEMI", "unstable angina", "risk stratification"], "difficulty": "advanced"},
        {"topic": "Diabetes management", "subtopics": ["type 1", "type 2", "complications", "insulin therapy"], "difficulty": "intermediate"},
        {"topic": "Respiratory conditions", "subtopics": ["COPD", "asthma", "pneumonia", "pulmonary embolism"], "difficulty": "intermediate"},
        {"topic": "Stroke", "subtopics": ["ischaemic", "haemorrhagic", "TIA", "rehabilitation"], "difficulty": "advanced"},
        {"topic": "Mental health", "subtopics": ["depression", "anxiety", "risk assessment", "medication"], "difficulty": "intermediate"},
        {"topic": "Chronic kidney disease", "subtopics": ["staging", "management", "complications", "dialysis"], "difficulty": "advanced"},
        {"topic": "Cancer", "subtopics": ["screening", "staging", "treatment options", "palliative care"], "difficulty": "advanced"},
        {"topic": "Infectious diseases", "subtopics": ["antibiotic stewardship", "sepsis", "hospital-acquired", "immunisation"], "difficulty": "intermediate"},
    ],

    OETHealthcareProfession.PHARMACY: [
        {"topic": "Anticoagulation", "subtopics": ["warfarin", "DOACs", "monitoring", "reversal"], "difficulty": "advanced"},
        {"topic": "Polypharmacy", "subtopics": ["medication review", "deprescribing", "drug interactions", "falls risk"], "difficulty": "advanced"},
        {"topic": "Antimicrobial stewardship", "subtopics": ["guidelines", "resistance", "duration", "IV to oral switch"], "difficulty": "intermediate"},
        {"topic": "Pain management", "subtopics": ["opioids", "adjuvants", "neuropathic pain", "dependence"], "difficulty": "intermediate"},
        {"topic": "Medicines reconciliation", "subtopics": ["admission", "transfer", "discharge", "errors"], "difficulty": "basic"},
        {"topic": "Therapeutic drug monitoring", "subtopics": ["gentamicin", "vancomycin", "digoxin", "lithium"], "difficulty": "advanced"},
        {"topic": "Patient counselling", "subtopics": ["adherence", "side effects", "storage", "interactions"], "difficulty": "basic"},
        {"topic": "Medication safety", "subtopics": ["high-risk medicines", "look-alike sound-alike", "error reporting", "incident analysis"], "difficulty": "intermediate"},
    ],
}


def get_writing_sample(profession: OETHealthcareProfession, letter_type: str) -> Optional[OETWritingSample]:
    """Get a writing sample matching the profession and letter type"""
    for key, sample in OET_WRITING_SAMPLES.items():
        if sample.profession == profession and sample.letter_type == letter_type:
            return sample
    return None


def get_speaking_sample(profession: OETHealthcareProfession, scenario_type: str) -> Optional[OETSpeakingSample]:
    """Get a speaking sample matching the profession and scenario type"""
    for key, sample in OET_SPEAKING_SAMPLES.items():
        if sample.profession == profession and sample.scenario_type == scenario_type:
            return sample
    return None


def get_topics_for_profession(profession: OETHealthcareProfession) -> List[Dict[str, Any]]:
    """Get topic bank for a specific profession"""
    return OET_TOPICS_BY_PROFESSION.get(profession, [])
