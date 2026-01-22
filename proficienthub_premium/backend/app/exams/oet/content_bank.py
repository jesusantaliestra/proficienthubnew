"""
ProficientHub - OET Content Bank
Templates and example content for OET exam generation
"""

from typing import List, Dict, Any, Optional
from app.exams.oet.models import (
    OETProfession, OETSection, ListeningPart, ReadingPart,
    QuestionType, WritingTaskType, SpeakingScenarioType,
    PatientCaseNotes, OETWritingTask, OETSpeakingRolePlay,
    SpeakingRoleCard
)


class OETContentBank:
    """
    Content bank for OET exam generation
    Contains templates, examples, and generation prompts
    """

    # =========================================================================
    # LISTENING TEMPLATES
    # =========================================================================

    LISTENING_PART_A_TEMPLATE = {
        "description": "Consultation extracts - Note completion",
        "instructions": """
You will hear two recorded healthcare consultations. While you listen, complete the notes using the information you hear.

For each blank, write no more than THREE words.

You will hear each recording TWICE.
        """,
        "example_scenarios": [
            {
                "title": "Patient presenting with chest pain",
                "speakers": ["Doctor", "Patient"],
                "medical_context": "Cardiology consultation",
                "key_topics": ["chest pain characteristics", "risk factors", "family history", "examination findings"]
            },
            {
                "title": "Post-operative follow-up",
                "speakers": ["Surgeon", "Patient"],
                "medical_context": "Surgical follow-up",
                "key_topics": ["wound healing", "pain management", "activity restrictions", "follow-up plan"]
            },
            {
                "title": "Diabetes management review",
                "speakers": ["GP", "Patient"],
                "medical_context": "Chronic disease management",
                "key_topics": ["blood glucose control", "medication adherence", "lifestyle factors", "complications screening"]
            }
        ],
        "question_stems": [
            "Patient's main complaint: ___",
            "Duration of symptoms: ___",
            "Pain described as: ___",
            "Aggravating factors: ___",
            "Relieving factors: ___",
            "Past medical history includes: ___",
            "Current medications: ___",
            "Allergies: ___",
            "Family history: ___",
            "On examination, ___ was noted",
            "Investigation ordered: ___",
            "Working diagnosis: ___"
        ]
    }

    LISTENING_PART_B_TEMPLATE = {
        "description": "Workplace extracts - Multiple choice",
        "instructions": """
You will hear six short workplace extracts. For each extract, answer the multiple-choice question.

Choose the answer (A, B, or C) which fits best according to what you hear.

You will hear each extract ONCE only.
        """,
        "example_scenarios": [
            {
                "title": "Handover between nurses",
                "context": "Shift change on medical ward",
                "question_focus": "Priority patient concern"
            },
            {
                "title": "Multidisciplinary team meeting",
                "context": "Discussion about patient discharge",
                "question_focus": "Main barrier to discharge"
            },
            {
                "title": "Phone conversation with pharmacy",
                "context": "Medication query",
                "question_focus": "Outcome of conversation"
            },
            {
                "title": "Staff briefing",
                "context": "New protocol introduction",
                "question_focus": "Main change in practice"
            },
            {
                "title": "Conversation with relative",
                "context": "Family meeting about care plan",
                "question_focus": "Family's main concern"
            },
            {
                "title": "Peer discussion",
                "context": "Discussing difficult case",
                "question_focus": "Colleague's recommendation"
            }
        ]
    }

    LISTENING_PART_C_TEMPLATE = {
        "description": "Presentation extracts - Multiple choice and matching",
        "instructions": """
You will hear two presentations on healthcare topics.

For Questions 1-6, answer the multiple-choice questions.
For Questions 7-12, match each statement to the speaker.

You will hear each recording TWICE.
        """,
        "example_topics": [
            "Recent advances in stroke management",
            "Antibiotic stewardship in hospitals",
            "Managing chronic pain in primary care",
            "Update on diabetes guidelines",
            "Mental health in the workplace",
            "Pediatric vaccination controversies",
            "End-of-life care decision making",
            "Innovations in wound care"
        ]
    }

    # =========================================================================
    # READING TEMPLATES
    # =========================================================================

    READING_PART_A_TEMPLATE = {
        "description": "Expeditious reading - Scanning and skimming",
        "instructions": """
In this part of the test, you will read FOUR short texts about a healthcare topic.

For Questions 1-20, answer each question by choosing a text (A, B, C, or D).
You may use each text more than once.
        """,
        "text_types": [
            "Hospital policy document",
            "Clinical guideline summary",
            "Patient information leaflet",
            "Research abstract",
            "Drug monograph excerpt",
            "Professional body guidelines",
            "Health department advisory"
        ],
        "question_formats": [
            "Which text mentions [specific information]?",
            "In which text is [condition/treatment] described?",
            "Which text provides information about [topic]?",
            "According to which text, [statement]?"
        ]
    }

    READING_PART_B_TEMPLATE = {
        "description": "Careful reading - Short texts",
        "instructions": """
In this part of the test, you will read SIX short texts related to healthcare.

For Questions 21-26, choose the answer (A, B, C, or D) which best fits the text.
        """,
        "text_types": [
            "Internal memo",
            "Policy excerpt",
            "Patient case summary",
            "Email communication",
            "Notice or announcement",
            "Protocol extract"
        ],
        "text_length": "100-150 words each"
    }

    READING_PART_C_TEMPLATE = {
        "description": "Careful reading - Long texts",
        "instructions": """
You will read TWO texts on topics of interest to healthcare professionals.

For Questions 27-42, choose the answer (A, B, C, or D) which best completes the statement or answers the question.
        """,
        "text_types": [
            "Journal article excerpt",
            "Editorial or opinion piece",
            "Research report summary",
            "Healthcare policy analysis"
        ],
        "text_length": "600-800 words each",
        "question_types": [
            "Main idea identification",
            "Specific detail comprehension",
            "Inference and implication",
            "Author's purpose or tone",
            "Vocabulary in context",
            "Reference understanding"
        ]
    }

    # =========================================================================
    # WRITING TEMPLATES - MEDICINE
    # =========================================================================

    WRITING_CASE_TEMPLATES_MEDICINE = [
        {
            "scenario": "Referral to cardiologist",
            "template": PatientCaseNotes(
                patient_name="[PATIENT_NAME]",
                age=58,
                gender="Male",
                date_of_consultation="[DATE]",
                presenting_complaint="Chest pain on exertion for 3 weeks",
                history_of_present_illness="""
Patient reports central chest tightness occurring during physical activity,
particularly when climbing stairs or walking uphill. Pain radiates to left arm.
Each episode lasts 5-10 minutes and resolves with rest. No pain at rest.
Denies syncope, palpitations, or shortness of breath at rest.
Has noticed reduced exercise tolerance over past month.
                """.strip(),
                past_medical_history=[
                    "Type 2 Diabetes Mellitus - diagnosed 2018",
                    "Hypertension - 10 years",
                    "Hyperlipidaemia",
                    "Ex-smoker (quit 2020, 30 pack-year history)"
                ],
                medications=[
                    {"name": "Metformin", "dose": "1g", "frequency": "BD"},
                    {"name": "Lisinopril", "dose": "10mg", "frequency": "OD"},
                    {"name": "Atorvastatin", "dose": "20mg", "frequency": "nocte"},
                    {"name": "Aspirin", "dose": "100mg", "frequency": "OD"}
                ],
                allergies=["Penicillin - rash"],
                social_history={
                    "occupation": "Accountant (sedentary)",
                    "alcohol": "10 units/week",
                    "smoking": "Ex-smoker, quit 4 years ago",
                    "exercise": "Previously walked 30 min/day, now limited",
                    "lives_with": "Wife"
                },
                family_history=[
                    "Father - MI at age 55",
                    "Mother - Type 2 DM"
                ],
                examination_findings={
                    "general": "Comfortable at rest, BMI 32",
                    "cardiovascular": "Regular pulse, no murmurs, BP elevated",
                    "respiratory": "Clear",
                    "peripheral": "No oedema"
                },
                vital_signs={
                    "BP": "148/92 mmHg",
                    "HR": "78 bpm, regular",
                    "RR": "16/min",
                    "SpO2": "98% on room air",
                    "Temp": "36.8°C"
                },
                investigations=[
                    {"test": "ECG", "result": "Sinus rhythm, T wave flattening in V4-V6"},
                    {"test": "FBC", "result": "Normal"},
                    {"test": "U&E", "result": "Normal"},
                    {"test": "HbA1c", "result": "7.8% (above target)"},
                    {"test": "Lipid profile", "result": "Total cholesterol 5.8, LDL 3.9"},
                    {"test": "Troponin", "result": "Negative"}
                ],
                diagnosis="Suspected stable angina",
                differential_diagnoses=["Unstable angina", "GORD", "Musculoskeletal"],
                treatment_plan=[
                    "GTN spray prescribed - instructions given",
                    "Atorvastatin increased to 40mg",
                    "BP target <130/80",
                    "Lifestyle advice - weight loss, diet, exercise",
                    "Urgent cardiology referral for stress testing"
                ],
                referral_reason="For cardiac stress testing and assessment of coronary artery disease"
            ),
            "task_type": WritingTaskType.REFERRAL_LETTER,
            "recipient": "Dr. Sarah Chen, Cardiologist",
            "recipient_institution": "City Heart Centre",
            "required_points": [
                "Presenting complaint and symptom characteristics",
                "Significant cardiovascular risk factors",
                "Relevant investigation results",
                "Current management initiated",
                "Reason for referral and urgency"
            ]
        },
        {
            "scenario": "Discharge letter - Pneumonia",
            "template": PatientCaseNotes(
                patient_name="[PATIENT_NAME]",
                age=72,
                gender="Female",
                date_of_admission="[DATE_ADMISSION]",
                presenting_complaint="Productive cough, fever, shortness of breath for 5 days",
                history_of_present_illness="""
Patient presented via ED with 5-day history of worsening productive cough
with green sputum, fever, and increasing breathlessness. Unable to complete
sentences on admission. Confused on arrival (new onset). No chest pain.
Poor oral intake for 3 days. Lives alone, found by neighbour.
                """.strip(),
                past_medical_history=[
                    "COPD - moderate severity",
                    "Atrial fibrillation",
                    "Osteoporosis",
                    "Hypothyroidism"
                ],
                medications=[
                    {"name": "Tiotropium", "dose": "18mcg", "frequency": "OD inhaled"},
                    {"name": "Salbutamol", "dose": "100mcg", "frequency": "PRN inhaled"},
                    {"name": "Apixaban", "dose": "5mg", "frequency": "BD"},
                    {"name": "Levothyroxine", "dose": "75mcg", "frequency": "OD"},
                    {"name": "Alendronate", "dose": "70mg", "frequency": "weekly"}
                ],
                allergies=["NKDA"],
                social_history={
                    "occupation": "Retired teacher",
                    "alcohol": "Occasional",
                    "smoking": "Ex-smoker, quit 20 years ago",
                    "living": "Lives alone, independent prior to admission",
                    "mobility": "Walks with stick"
                },
                examination_findings={
                    "general": "Unwell, confused, using accessory muscles",
                    "respiratory": "Reduced air entry right base, coarse crackles",
                    "cardiovascular": "Irregular pulse (AF), no oedema"
                },
                vital_signs={
                    "BP": "102/68 mmHg",
                    "HR": "110 bpm, irregular",
                    "RR": "28/min",
                    "SpO2": "89% on room air",
                    "Temp": "38.9°C"
                },
                investigations=[
                    {"test": "CXR", "result": "Right lower lobe consolidation"},
                    {"test": "FBC", "result": "WCC 18.4, neutrophils elevated"},
                    {"test": "CRP", "result": "285 mg/L"},
                    {"test": "U&E", "result": "AKI stage 1, Cr 128 (baseline 85)"},
                    {"test": "Blood cultures", "result": "No growth"},
                    {"test": "Sputum culture", "result": "Strep pneumoniae - sensitive to amoxicillin"},
                    {"test": "CURB-65", "result": "Score 3 - severe"}
                ],
                diagnosis="Community-acquired pneumonia (severe) with AKI",
                treatment_plan=[
                    "IV fluids for 48 hours",
                    "IV Co-amoxiclav then switched to oral amoxicillin",
                    "Supplemental oxygen (target 88-92%)",
                    "VTE prophylaxis"
                ],
                discharge_medications=[
                    {"name": "Amoxicillin", "dose": "500mg", "frequency": "TDS for 5 more days"},
                    {"name": "Continue regular medications", "dose": "", "frequency": ""}
                ],
                follow_up_instructions=[
                    "GP review in 1 week",
                    "Repeat CXR in 6 weeks",
                    "Repeat U&E in 1 week",
                    "Pneumococcal and influenza vaccination",
                    "Contact GP if symptoms worsen"
                ]
            ),
            "task_type": WritingTaskType.DISCHARGE_LETTER,
            "recipient": "Dr. James Wilson, General Practitioner",
            "recipient_institution": "Oakwood Medical Centre",
            "required_points": [
                "Admission diagnosis and severity",
                "Key investigation findings",
                "Treatment provided during admission",
                "Discharge medications",
                "Follow-up requirements"
            ]
        }
    ]

    # =========================================================================
    # SPEAKING TEMPLATES - MEDICINE
    # =========================================================================

    SPEAKING_SCENARIOS_MEDICINE = [
        {
            "scenario_type": SpeakingScenarioType.EXPLANATION,
            "title": "Explaining a new diagnosis of Type 2 Diabetes",
            "setting": "GP consultation room",
            "candidate_card": SpeakingRoleCard(
                role="Doctor",
                setting="General Practice",
                context="A 52-year-old patient has been diagnosed with Type 2 Diabetes following routine blood tests. HbA1c is 58 mmol/mol.",
                tasks=[
                    "Explain the diagnosis and what it means",
                    "Discuss lifestyle modifications",
                    "Explain the role of medication",
                    "Address any concerns the patient may have",
                    "Arrange follow-up"
                ]
            ),
            "interlocutor_card": SpeakingRoleCard(
                role="Patient",
                setting="General Practice",
                context="You are a 52-year-old office worker. You had blood tests last week and have been asked to come in for results. You feel well.",
                emotional_state="Anxious about receiving unexpected news",
                concerns=[
                    "You don't feel unwell so question if there's an error",
                    "Your father had diabetes and lost his leg",
                    "You're worried about having to inject insulin",
                    "Your job involves a lot of business lunches"
                ],
                information_to_provide={
                    "diet": "Eat out frequently, large portions, enjoy desserts",
                    "exercise": "Very little - desk job, drive everywhere",
                    "family": "Father had Type 2 DM with complications",
                    "weight": "Have gained 10kg over past 5 years"
                }
            ),
            "interlocutor_prompts": [
                {"cue": "After diagnosis explained", "response": "But I feel absolutely fine. Are you sure there's no mistake?"},
                {"cue": "When medication mentioned", "response": "My father had diabetes. He ended up having to inject insulin and lost his leg. Is that going to happen to me?"},
                {"cue": "When lifestyle discussed", "response": "I have a lot of business lunches for work. I can't really change what I eat."},
                {"cue": "Near end", "response": "What happens if I just ignore this?"}
            ]
        },
        {
            "scenario_type": SpeakingScenarioType.BREAKING_BAD_NEWS,
            "title": "Discussing suspected cancer diagnosis",
            "setting": "Hospital outpatient clinic",
            "candidate_card": SpeakingRoleCard(
                role="Doctor",
                setting="Hospital outpatient clinic",
                context="A 65-year-old patient had a colonoscopy for rectal bleeding. Results show a suspicious mass. Biopsy confirms adenocarcinoma. CT staging pending.",
                tasks=[
                    "Sensitively deliver the diagnosis",
                    "Explain what happens next (staging, MDT)",
                    "Provide appropriate support",
                    "Assess patient's understanding",
                    "Arrange follow-up and support services"
                ]
            ),
            "interlocutor_card": SpeakingRoleCard(
                role="Patient",
                setting="Hospital outpatient clinic",
                context="You are 65 years old. You had a colonoscopy 2 weeks ago for blood in your stool. You've been called back for results.",
                emotional_state="Initially calm, then becoming distressed",
                concerns=[
                    "Initially hope it's just haemorrhoids",
                    "When told about cancer, become upset",
                    "Worried about telling your spouse",
                    "Concerned about whether it's treatable"
                ],
                information_to_provide={
                    "support": "Spouse waiting outside, adult children live nearby",
                    "priorities": "Want to see grandchildren grow up"
                }
            ),
            "interlocutor_prompts": [
                {"cue": "Initial greeting", "response": "I've been worried sick waiting for these results. Please tell me it's just haemorrhoids."},
                {"cue": "After diagnosis delivered", "response": "[Becomes tearful] Cancer? I can't believe it. Am I going to die?"},
                {"cue": "When treatment discussed", "response": "I don't know how I'm going to tell my wife. She's sitting outside."},
                {"cue": "When asked about support", "response": "Can it be cured? I need to be here for my grandchildren."}
            ]
        },
        {
            "scenario_type": SpeakingScenarioType.COUNSELING,
            "title": "Discussing smoking cessation",
            "setting": "GP consultation room",
            "candidate_card": SpeakingRoleCard(
                role="Doctor",
                setting="General Practice",
                context="A 45-year-old patient with COPD continues to smoke 20 cigarettes daily despite previous advice. FEV1 has declined over past year.",
                tasks=[
                    "Explore patient's smoking history and previous quit attempts",
                    "Discuss impact on COPD progression",
                    "Explore motivation and barriers",
                    "Offer support options (NRT, medication, counselling)",
                    "Agree on a plan"
                ]
            ),
            "interlocutor_card": SpeakingRoleCard(
                role="Patient",
                setting="General Practice",
                context="You are 45 with COPD and smoke 20 cigarettes daily. You've been called in after lung function tests.",
                emotional_state="Defensive initially, then more open",
                concerns=[
                    "Fed up with being 'lectured' about smoking",
                    "Previous quit attempts failed",
                    "Smoking helps with stress at work",
                    "Worried about weight gain if you quit"
                ],
                information_to_provide={
                    "quit_attempts": "Tried patches twice, cold turkey once, lasted max 2 weeks",
                    "triggers": "Stress at work, after meals, with morning coffee",
                    "motivation": "Daughter is pregnant, want to meet grandchild",
                    "barriers": "Partner also smokes"
                }
            ),
            "interlocutor_prompts": [
                {"cue": "When smoking brought up", "response": "I know, I know. You're going to tell me to quit again."},
                {"cue": "When asked about previous attempts", "response": "I've tried everything. Nothing works for me. I just don't have the willpower."},
                {"cue": "When motivation explored", "response": "Well, my daughter just told me she's pregnant. I would like to be around to see the baby grow up."},
                {"cue": "When support offered", "response": "The thing is, my partner smokes too. It's hard when there are cigarettes in the house."}
            ]
        },
        {
            "scenario_type": SpeakingScenarioType.HISTORY_TAKING,
            "title": "Assessing headache",
            "setting": "Emergency Department",
            "candidate_card": SpeakingRoleCard(
                role="Doctor",
                setting="Emergency Department",
                context="A 35-year-old patient presents with severe headache. Need to take a focused history to rule out serious causes.",
                tasks=[
                    "Take a focused headache history",
                    "Screen for red flag symptoms",
                    "Assess for meningism/SAH features",
                    "Determine appropriate investigations",
                    "Explain initial management plan"
                ],
                information_to_elicit=[
                    "Onset - sudden vs gradual",
                    "Character and severity",
                    "Location and radiation",
                    "Associated symptoms (visual, nausea, photophobia)",
                    "Red flags (worst headache ever, neck stiffness, fever, rash)",
                    "Previous headache history",
                    "Medications and recent illness"
                ]
            ),
            "interlocutor_card": SpeakingRoleCard(
                role="Patient",
                setting="Emergency Department",
                context="You are 35 with severe headache that started suddenly 2 hours ago while at the gym.",
                emotional_state="In pain, anxious",
                information_to_provide={
                    "onset": "Sudden, like a thunderclap, while lifting weights",
                    "severity": "10/10, worst headache of my life",
                    "location": "Back of head, into neck",
                    "associated": "Felt sick, light hurts eyes, slight neck stiffness",
                    "history": "Occasional tension headaches but nothing like this",
                    "medications": "No regular medications",
                    "family": "Mother had a 'brain bleed' at age 50"
                }
            ),
            "interlocutor_prompts": [
                {"cue": "Asked about onset", "response": "It came on suddenly while I was doing weights at the gym. Like someone hit me on the back of the head."},
                {"cue": "Asked about severity", "response": "This is the worst headache I've ever had. I've never felt anything like it."},
                {"cue": "Asked about other symptoms", "response": "I feel sick and the lights in here are hurting my eyes. My neck feels a bit stiff too."},
                {"cue": "Asked about family history", "response": "My mum had something burst in her brain when she was about 50. Is that what's happening to me?"}
            ]
        }
    ]

    # =========================================================================
    # AI GENERATION PROMPTS
    # =========================================================================

    AI_PROMPTS = {
        "listening_consultation": """
Generate an authentic medical consultation transcript for OET Listening Part A.

PROFESSION: {profession}
SCENARIO: {scenario}
SPEAKERS: {speakers}

Requirements:
1. Duration: 4-5 minutes when read at natural pace
2. Include realistic medical terminology appropriate to {profession}
3. Include natural speech patterns (hesitations, clarifications)
4. Cover: presenting complaint, history, examination findings, management plan
5. Include 12 questions that can be answered from the transcript

Format:
- Provide full transcript with speaker labels
- List 12 note-completion questions with answers
- Include key vocabulary list
        """,

        "listening_workplace": """
Generate a short workplace healthcare extract for OET Listening Part B.

PROFESSION: {profession}
CONTEXT: {context}

Requirements:
1. Duration: 30-45 seconds
2. Natural workplace communication
3. One clear main point for MCQ question

Format:
- Provide transcript
- One MCQ question with 3 options
- Correct answer with explanation
        """,

        "listening_presentation": """
Generate a healthcare presentation extract for OET Listening Part C.

TOPIC: {topic}
PROFESSION: {profession}

Requirements:
1. Duration: 4-5 minutes per speaker (2 speakers total)
2. Academic/professional register
3. Evidence-based content with statistics/studies
4. 6 MCQ questions per presentation

Format:
- Provide full presentation transcripts
- 12 questions total with answers
        """,

        "reading_part_a": """
Generate four short healthcare texts for OET Reading Part A.

TOPIC: {topic}
PROFESSION: {profession}

Requirements:
1. Each text 150-200 words
2. Different text types (guideline, policy, patient info, research summary)
3. Related but distinct content
4. 20 questions asking which text contains specific information

Format:
- Four labeled texts (A, B, C, D)
- 20 questions with answers
        """,

        "reading_part_b": """
Generate a short healthcare text for OET Reading Part B.

TEXT TYPE: {text_type}
PROFESSION: {profession}

Requirements:
1. 100-150 words
2. Clear main message
3. One MCQ question testing comprehension

Format:
- Text content
- MCQ question with 4 options
- Correct answer with explanation
        """,

        "reading_part_c": """
Generate a long healthcare text for OET Reading Part C.

TOPIC: {topic}
PROFESSION: {profession}

Requirements:
1. 600-800 words
2. Journal article or editorial style
3. Clear paragraph structure (labeled A-G)
4. 8 questions covering:
   - Main idea
   - Specific details
   - Inferences
   - Author's purpose
   - Vocabulary in context

Format:
- Full text with paragraph labels
- 8 MCQ questions with answers
        """,

        "writing_case_notes": """
Generate authentic patient case notes for an OET Writing task.

PROFESSION: {profession}
TASK TYPE: {task_type}
SCENARIO: {scenario}

Requirements:
1. Realistic patient demographics
2. Complete medical history
3. Relevant investigations and results
4. Clear diagnosis and management plan
5. Appropriate complexity for 45-minute writing task

Format:
- Complete case notes in OET format
- Task instructions
- Required content points
- Model answer (180-200 words)
        """,

        "speaking_roleplay": """
Generate an OET Speaking role-play scenario.

PROFESSION: {profession}
SCENARIO TYPE: {scenario_type}

Requirements:
1. Realistic clinical scenario
2. Clear candidate tasks
3. Patient/relative with specific concerns
4. Interlocutor prompts for natural conversation flow
5. Appropriate emotional complexity

Format:
- Complete role cards (candidate and interlocutor)
- Interlocutor script with prompts
- Evaluation criteria
        """
    }

    # =========================================================================
    # MEDICAL VOCABULARY BY PROFESSION
    # =========================================================================

    MEDICAL_VOCABULARY = {
        OETProfession.MEDICINE: {
            "general": [
                "presenting complaint", "differential diagnosis", "prognosis",
                "prophylaxis", "contraindication", "aetiology", "idiopathic",
                "asymptomatic", "symptomatic", "benign", "malignant"
            ],
            "cardiology": [
                "angina", "myocardial infarction", "arrhythmia", "fibrillation",
                "stenosis", "cardiomyopathy", "heart failure", "hypertension"
            ],
            "respiratory": [
                "dyspnoea", "tachypnoea", "consolidation", "effusion",
                "pneumothorax", "bronchospasm", "crepitations", "wheeze"
            ],
            "gastroenterology": [
                "dysphagia", "haematemesis", "melaena", "jaundice",
                "hepatomegaly", "splenomegaly", "ascites", "peritonitis"
            ],
            "neurology": [
                "aphasia", "dysarthria", "ataxia", "nystagmus",
                "hemiplegia", "paraesthesia", "meningism", "seizure"
            ]
        },
        OETProfession.NURSING: {
            "general": [
                "vital signs", "nursing assessment", "care plan", "handover",
                "documentation", "patient education", "discharge planning"
            ],
            "clinical": [
                "wound care", "medication administration", "fluid balance",
                "pressure area care", "catheter care", "aseptic technique"
            ]
        }
    }

    # =========================================================================
    # HELPER METHODS
    # =========================================================================

    @classmethod
    def get_writing_template(
        cls,
        profession: OETProfession,
        task_type: WritingTaskType
    ) -> Dict[str, Any]:
        """Get a writing task template for the given profession and type"""
        if profession == OETProfession.MEDICINE:
            templates = cls.WRITING_CASE_TEMPLATES_MEDICINE
        else:
            # Default to medicine templates, adapt for other professions
            templates = cls.WRITING_CASE_TEMPLATES_MEDICINE

        for template in templates:
            if template["task_type"] == task_type:
                return template

        return templates[0]  # Return first if no match

    @classmethod
    def get_speaking_scenario(
        cls,
        profession: OETProfession,
        scenario_type: SpeakingScenarioType
    ) -> Dict[str, Any]:
        """Get a speaking scenario for the given profession and type"""
        if profession == OETProfession.MEDICINE:
            scenarios = cls.SPEAKING_SCENARIOS_MEDICINE
        else:
            scenarios = cls.SPEAKING_SCENARIOS_MEDICINE

        for scenario in scenarios:
            if scenario["scenario_type"] == scenario_type:
                return scenario

        return scenarios[0]

    @classmethod
    def get_ai_prompt(
        cls,
        prompt_type: str,
        **kwargs
    ) -> str:
        """Get and format an AI generation prompt"""
        template = cls.AI_PROMPTS.get(prompt_type, "")
        return template.format(**kwargs)

    @classmethod
    def get_vocabulary(
        cls,
        profession: OETProfession,
        category: Optional[str] = None
    ) -> List[str]:
        """Get medical vocabulary for a profession"""
        vocab = cls.MEDICAL_VOCABULARY.get(profession, {})
        if category:
            return vocab.get(category, [])

        # Return all vocabulary for profession
        all_vocab = []
        for cat_vocab in vocab.values():
            all_vocab.extend(cat_vocab)
        return all_vocab
