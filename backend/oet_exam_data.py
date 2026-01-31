"""OET Nursing Mock Exam Data - NUR-013-v2

Complete mock exam content extracted from the official document.
This module contains all questions, answers, and audio scripts.
"""

# EXAM METADATA
EXAM_METADATA = {
    "exam_id": "NUR-013-v2",
    "profession": "nursing",
    "version": "2.0",
    "title": "OET Nursing Mock NUR-013",
    "description": "Complete OET mock exam for nursing professionals",
    "total_questions": {
        "listening": 42,
        "reading": 42,
        "writing": 1,
        "speaking": 2
    }
}

# ============================================================
# LISTENING SUB-TEST (42 questions, ~50 minutes)
# ============================================================

LISTENING_PART_A = {
    "name": "Part A: Consultation Extracts",
    "instructions": "Complete the notes using information from the audio. Use 1-3 words per gap.",
    "questions": 24,
    "extracts": [
        {
            "id": "extract_1",
            "title": "Community Nurse Home Visit",
            "context": "Consultation between a community nurse and an elderly patient",
            "duration": "4 minutes 45 seconds",
            "speakers": [
                {"name": "Nurse Siobhan O'Brien", "role": "Community Mental Health Nurse", "accent": "Irish"},
                {"name": "Mrs Dorothy Thornton", "role": "Patient", "age": 82, "accent": "British RP"}
            ],
            "questions": [
                {"id": 1, "text": "Duration of symptoms:", "answer": "one to two weeks"},
                {"id": 2, "text": "Type of experience reported (visual):", "answer": "hallucinations"},
                {"id": 3, "text": "Frequency of night-time toilet visits:", "answer": "six to eight times"},
                {"id": 4, "text": "Day of week patient initially stated incorrectly:", "answer": "Wednesday"},
                {"id": 5, "text": "Current heart medication and dose:", "answer": "bisoprolol 5mg twice daily"},
                {"id": 6, "text": "New medication started recently:", "answer": "amitriptyline"},
                {"id": 7, "text": "Reason medication was prescribed:", "answer": "low mood"},
                {"id": 8, "text": "Medication dose:", "answer": "25 milligrams"},
                {"id": 9, "text": "Who fills patient's dosette box:", "answer": "Margaret"},
                {"id": 10, "text": "Location of soreness after stumble:", "answer": "left hip"},
                {"id": 11, "text": "Number of proper meals per day:", "answer": "one"},
                {"id": 12, "text": "Safety device patient forgets to wear:", "answer": "emergency pendant"}
            ],
            "audio_script": """NURSE O'BRIEN: Good afternoon, Mrs Thornton. I'm Siobhan O'Brien, the community mental health nurse. Your daughter Margaret contacted us because she's been worried about you. How are you feeling today?

MRS THORNTON: Oh... hello dear. I'm... I'm quite well, thank you. Well, perhaps a little tired. Margaret does fuss so.

NURSE O'BRIEN: I understand. Can you tell me, do you know what day it is today?

MRS THORNTON: It's... Wednesday? No, wait... Thursday. Yes, Thursday. I had my hair done on Tuesday, so it must be Thursday now.

NURSE O'BRIEN: That's right, it is Thursday. And Mrs Thornton, when did you first start feeling not quite yourself? Margaret mentioned you've seemed a bit confused lately.

MRS THORNTON: Confused? I don't think I've been confused exactly. But I have felt rather peculiar for... oh, it must be one to two weeks now. Or perhaps ten days. It started quite gradually.

NURSE O'BRIEN: I see. And can you describe what you mean by "peculiar"?

MRS THORNTON: Well... sometimes I see things that Margaret says aren't there. Like yesterday, I was certain I saw my late husband Harold sitting in his chair. But he passed away three years ago.

NURSE O'BRIEN: That must have been distressing for you. Are these visions something new, or have you experienced them before?

MRS THORNTON: New, I think. Though sometimes I'm not sure what's real anymore. I mean, I know Harold's gone, but he seemed so real sitting there.

NURSE O'BRIEN: Mrs Thornton, have you had any problems with going to the toilet recently? Any burning sensation when you pass urine, or needing to go more often?

MRS THORNTON: Now you mention it... yes. I've been to the bathroom six or seven times last night. Maybe eight times. And there is a bit of stinging. I thought it was just my age.

NURSE O'BRIEN: That's very helpful information. We should get a urine sample to check for an infection. UTIs can often cause confusion in older adults. What medications are you currently taking?

MRS THORNTON: Let me think... There's the blood pressure tablet... amlodipine, I think. And something for my heart... bis-something. Bisoprolol? Five milligrams, twice daily.

NURSE O'BRIEN: And have any of your medications changed recently?

MRS THORNTON: The doctor added a new one... about two weeks ago for sleeping. No, for my mood - I was feeling low after losing my cat. Amitriptyline, I believe. Twenty-five milligrams at night.

NURSE O'BRIEN: I see. That's quite important to know. Amitriptyline can sometimes cause confusion in older people, especially when combined with other medications. Who usually helps you with your tablets?

MRS THORNTON: I manage myself mostly. Margaret fills my dosette box on Sundays. Though I'll admit, I did get muddled last week and took my morning tablets twice.

NURSE O'BRIEN: When was that exactly?

MRS THORNTON: I think it was... last Monday? Or was it Tuesday? Definitely early last week. Margaret was quite cross with me.

NURSE O'BRIEN: That's understandable - it can be difficult to keep track. Now, Mrs Thornton, have you had any falls recently?

MRS THORNTON: I did stumble getting out of bed the night before last. I didn't fall properly - I grabbed the bedside table. But my hip is still a bit sore.

NURSE O'BRIEN: Which hip is painful?

MRS THORNTON: The left one. It's not too bad unless I twist suddenly.

NURSE O'BRIEN: I'd like to examine that if you don't mind. But first, can you tell me - have you been eating and drinking normally?

MRS THORNTON: Margaret says I haven't been eating enough. I just don't feel very hungry. I suppose I've only been having one proper meal a day, plus some tea and biscuits.

NURSE O'BRIEN: And how much fluid would you say you're drinking each day?

MRS THORNTON: Oh... perhaps three or four cups of tea. And maybe a glass of water with my tablets.

NURSE O'BRIEN: That's probably not quite enough - we should aim for about six to eight cups of fluid daily. Dehydration can also contribute to confusion. Mrs Thornton, is there anyone who stays with you at night?

MRS THORNTON: No, I live alone. Margaret visits most days, but she has her own family. Her husband Derek works shifts, so she can't always come.

NURSE O'BRIEN: And how do you manage with getting dressed and bathing?

MRS THORNTON: I can dress myself, though buttons are a bit fiddly now. Bathing - I use the shower with a seat. Margaret suggested I use the emergency pendant, but I keep forgetting to wear it.

NURSE O'BRIEN: It's really important to wear that pendant. Especially as you've mentioned feeling unsteady. I'm going to arrange for a few things today: a urine test, some blood tests, and I'll speak to your GP about reviewing your medications - particularly the amitriptyline."""
        },
        {
            "id": "extract_2", 
            "title": "Practice Nurse Consultation",
            "context": "Consultation between a practice nurse and a patient with knee pain",
            "duration": "4 minutes 30 seconds",
            "speakers": [
                {"name": "Nurse Fiona MacLeod", "role": "Practice Nurse", "accent": "Scottish"},
                {"name": "Mr Kevin Barnett", "role": "Patient", "age": 54, "accent": "London"}
            ],
            "questions": [
                {"id": 13, "text": "Duration of knee problems:", "answer": "six weeks"},
                {"id": 14, "text": "Duration of morning stiffness:", "answer": "twenty to thirty minutes"},
                {"id": 15, "text": "Activity that causes sharp pain:", "answer": "going down stairs"},
                {"id": 16, "text": "Occupation:", "answer": "delivery driver"},
                {"id": 17, "text": "Number of daily vehicle entries:", "answer": "forty to fifty"},
                {"id": 18, "text": "Maximum daily paracetamol intake:", "answer": "six tablets"},
                {"id": 19, "text": "Previous knee surgery type:", "answer": "cartilage operation"},
                {"id": 20, "text": "Time since surgery:", "answer": "twenty-five years"},
                {"id": 21, "text": "Father's joint procedure:", "answer": "knee replacement"},
                {"id": 22, "text": "Current weight:", "answer": "ninety-two kilos"},
                {"id": 23, "text": "Target weight loss percentage:", "answer": "five to ten percent"},
                {"id": 24, "text": "Recommended exercise type:", "answer": "swimming or cycling"}
            ],
            "audio_script": """NURSE MACLEOD: Good morning, Mr Barnett. I'm Fiona, one of the practice nurses. I can see from your notes you've come about some knee trouble. Tell me what's been happening.

MR BARNETT: Morning. Yeah, it's me right knee. Been playing up for about six weeks now - maybe a bit longer actually. Started quite gradually.

NURSE MACLEOD: Six weeks or so. And what sort of symptoms are you experiencing exactly?

MR BARNETT: Well, it's mainly stiffness in the mornings. And pain - a sort of dull ache most of the time, but sometimes it's sharper. Especially going down stairs.

NURSE MACLEOD: How long does the morning stiffness last typically?

MR BARNETT: Maybe... twenty to thirty minutes? It eases up once I get moving. Though by the end of the day it's sore again.

NURSE MACLEOD: And the sharp pain on stairs - is that going up, coming down, or both?

MR BARNETT: Definitely worse going down. Going up's not too bad, but coming down - that really catches me.

NURSE MACLEOD: Have you noticed any swelling around the knee?

MR BARNETT: Yeah, it does puff up a bit. Not massively, but more than the other one. The left knee's fine - it's just this right one.

NURSE MACLEOD: Any giving way or locking sensations? Times when the knee suddenly buckles or gets stuck?

MR BARNETT: Not locking, no. But it has given way once or twice. Not completely - just felt unstable for a second. Made me grab the handrail quickly.

NURSE MACLEOD: That must have been worrying. Now, what's your occupation, Mr Barnett?

MR BARNETT: I'm a delivery driver. Parcels mainly. So I'm in and out of the van forty or fifty times a day, climbing up into the cab.

NURSE MACLEOD: And how's the knee affecting your work?

MR BARNETT: It's getting harder, to be honest. The constant climbing in and out - by lunchtime it's really throbbing. I've been taking paracetamol just to get through the shift.

NURSE MACLEOD: How many paracetamol would you say you're taking daily?

MR BARNETT: Four... sometimes six tablets. Two in the morning, two at lunch, sometimes another two when I get home.

NURSE MACLEOD: And is that helping much?

MR BARNETT: Takes the edge off, but doesn't get rid of it completely. I've tried ibuprofen gel as well - that helps a bit more actually.

NURSE MACLEOD: Any previous injuries to this knee? Sports injuries, accidents?

MR BARNETT: I played football when I was younger. Had a cartilage operation on this knee about twenty-five years ago. Keyhole surgery - recovered fine at the time.

NURSE MACLEOD: And is there any family history of arthritis?

MR BARNETT: My mum had it in her hands. And my dad had a knee replacement in his seventies. So I suppose it runs in the family.

NURSE MACLEOD: Given your history and symptoms, this does sound like it could be osteoarthritis. What's your weight at the moment?

MR BARNETT: About ninety-two kilos, I think. I know I could lose a bit - my wife keeps telling me.

NURSE MACLEOD: What's your height?

MR BARNETT: One seventy-five. About five foot nine in old money.

NURSE MACLEOD: That puts your BMI around thirty. The good news is that even modest weight loss can help. We'd recommend aiming for around five to ten percent reduction initially. Along with some specific exercises.

MR BARNETT: What sort of exercises?

NURSE MACLEOD: Strengthening exercises for the quadriceps. Swimming or cycling are also excellent as they're low-impact. I'll refer you to our physio team who can design a programme."""
        }
    ]
}

LISTENING_PART_B = {
    "name": "Part B: Workplace Extracts",
    "instructions": "Choose the best answer A, B, or C.",
    "questions": 6,
    "extracts": [
        {
            "id": 25,
            "context": "You hear a ward sister speaking to a nurse at the start of a shift.",
            "question": "What does the ward sister want the nurse to do?",
            "options": [
                "A. Ensure the overnight events are properly recorded",
                "B. Conduct a comprehensive pain assessment", 
                "C. Arrange an urgent medical review"
            ],
            "answer": "A"
        },
        {
            "id": 26,
            "context": "You hear two nurses discussing a medication administration issue.",
            "question": "What do the nurses agree was the main problem?",
            "options": [
                "A. The verification procedure wasn't correctly followed",
                "B. The ward layout caused patient confusion",
                "C. There were insufficient staff for medication rounds"
            ],
            "answer": "A"
        },
        {
            "id": 27,
            "context": "You hear a clinical educator leaving a voicemail for nursing students.",
            "question": "What is the main purpose of this message?",
            "options": [
                "A. To change the time and location of the session",
                "B. To list required preparation materials",
                "C. To outline what the simulation will involve"
            ],
            "answer": "C"
        },
        {
            "id": 28,
            "context": "You hear an occupational therapist updating a nurse about a patient.",
            "question": "What is the occupational therapist's main concern?",
            "options": [
                "A. The patient's physical mobility has deteriorated",
                "B. The home environment poses safety risks",
                "C. The family is unwilling to provide support"
            ],
            "answer": "B"
        },
        {
            "id": 29,
            "context": "You hear a charge nurse speaking at a team huddle.",
            "question": "What is the charge nurse mainly communicating?",
            "options": [
                "A. Concerns about medication safety procedures",
                "B. Instructions for managing current resource constraints",
                "C. Requirements for new staff supervision"
            ],
            "answer": "B"
        },
        {
            "id": 30,
            "context": "You hear a nurse specialist speaking to a colleague about a patient.",
            "question": "What does the nurse specialist believe about the wound?",
            "options": [
                "A. The healing has been slower than expected",
                "B. The dressing choice was originally incorrect",
                "C. The condition has become infected"
            ],
            "answer": "C"
        }
    ]
}

LISTENING_PART_C = {
    "name": "Part C: Presentations and Interviews",
    "instructions": "Choose the best answer A, B, or C.",
    "questions": 12,
    "extracts": [
        {
            "id": "interview_1",
            "title": "Interview with Pain Management Specialist",
            "context": "Interview with Dr Amira Hassan, a consultant in pain management",
            "duration": "5 minutes",
            "questions": [
                {
                    "id": 31,
                    "question": "According to Dr Hassan, what is the main limitation of the traditional approach to pain?",
                    "options": [
                        "A. It fails to explain pain that persists after healing",
                        "B. It ignores the role of medication in treatment",
                        "C. It doesn't consider patient preferences"
                    ],
                    "answer": "A"
                },
                {
                    "id": 32,
                    "question": "What point does Dr Hassan emphasise about chronic pain?",
                    "options": [
                        "A. It cannot be detected through standard tests",
                        "B. It usually resolves without treatment",
                        "C. It represents genuine patient suffering"
                    ],
                    "answer": "C"
                },
                {
                    "id": 33,
                    "question": "What does Dr Hassan suggest about opioids in chronic pain management?",
                    "options": [
                        "A. They should be used with careful dose escalation",
                        "B. They are appropriate for palliative situations",
                        "C. They are underutilised in current practice"
                    ],
                    "answer": "B"
                },
                {
                    "id": 34,
                    "question": "According to Dr Hassan, what should be the primary aim of pain treatment?",
                    "options": [
                        "A. Improving the patient's daily functioning",
                        "B. Reducing reliance on healthcare services",
                        "C. Achieving complete pain elimination"
                    ],
                    "answer": "A"
                },
                {
                    "id": 35,
                    "question": "How does Dr Hassan recommend communicating with patients about their pain?",
                    "options": [
                        "A. By providing detailed neurological explanations",
                        "B. By emphasising the role of positive thinking",
                        "C. By validating their experience while offering education"
                    ],
                    "answer": "C"
                },
                {
                    "id": 36,
                    "question": "What does Dr Hassan say about patient involvement in treatment?",
                    "options": [
                        "A. Patients should direct their own medication choices",
                        "B. Patient education leads to better engagement",
                        "C. Patients often prefer passive treatment approaches"
                    ],
                    "answer": "B"
                }
            ]
        },
        {
            "id": "presentation_1",
            "title": "Presentation on Healthcare-Associated Infections",
            "context": "Part of a presentation by Dr James Okonjo, an infection prevention specialist",
            "duration": "5 minutes",
            "questions": [
                {
                    "id": 37,
                    "question": "What did the initial audit reveal about catheter use?",
                    "options": [
                        "A. A significant proportion lacked clinical justification",
                        "B. Insertion techniques varied widely between wards",
                        "C. Documentation of catheter care was inadequate"
                    ],
                    "answer": "A"
                },
                {
                    "id": 38,
                    "question": "What unexpected outcome resulted from the catheter reduction programme?",
                    "options": [
                        "A. Reduced need for antimicrobial treatment",
                        "B. Decreased patient mobility initially",
                        "C. Patients recovered more quickly"
                    ],
                    "answer": "C"
                },
                {
                    "id": 39,
                    "question": "According to Dr Okonjo, what helped overcome staff resistance?",
                    "options": [
                        "A. Introducing financial penalties for poor performance",
                        "B. Allowing staff to compare their ward's data with others",
                        "C. Simplifying the catheter documentation process"
                    ],
                    "answer": "B"
                },
                {
                    "id": 40,
                    "question": "What does Dr Okonjo say about hand hygiene and catheter care?",
                    "options": [
                        "A. Catheter reduction automatically improves hand hygiene",
                        "B. Hand hygiene training should precede catheter protocols",
                        "C. Both issues need simultaneous attention"
                    ],
                    "answer": "C"
                },
                {
                    "id": 41,
                    "question": "What does Dr Okonjo identify as the main barrier to guideline adherence?",
                    "options": [
                        "A. Insufficient training and education",
                        "B. Work pressures and belief in patient exceptions",
                        "C. Deliberate disregard for safety protocols"
                    ],
                    "answer": "B"
                },
                {
                    "id": 42,
                    "question": "What overall message does Dr Okonjo convey about infection prevention?",
                    "options": [
                        "A. It requires sustained cultural change rather than quick fixes",
                        "B. It depends primarily on implementing new technologies",
                        "C. It is best led by infection control specialists alone"
                    ],
                    "answer": "A"
                }
            ]
        }
    ]
}

# ============================================================
# READING SUB-TEST (42 questions, 60 minutes)
# ============================================================

READING_PART_A = {
    "name": "Part A: Expeditious Reading",
    "topic": "Sepsis Recognition and Response Protocols",
    "time": "15 minutes",
    "questions": 20,
    "texts": [
        {
            "id": "A",
            "title": "Trust Policy: Sepsis Recognition and Management",
            "content": """ROYAL METROPOLITAN HOSPITAL NHS TRUST POLICY: SEPSIS RECOGNITION AND MANAGEMENT
Version 4.2 | Effective: March 2024

1. SCOPE
This policy applies to all clinical staff involved in patient assessment and care within acute and community settings.

2. BACKGROUND
Sepsis is a life-threatening organ dysfunction caused by a dysregulated host response to infection. Early recognition and treatment significantly improve outcomes. The Trust aims to achieve antibiotic administration within ONE HOUR of sepsis recognition for all confirmed cases.

3. RECOGNITION CRITERIA
Sepsis should be suspected when a patient has:
- Known or suspected infection, AND
- Any of the following "red flag" indicators:
  - Systolic blood pressure ≤90 mmHg (or drop of >40 mmHg from baseline)
  - Heart rate >130 beats per minute
  - Respiratory rate ≥25 breaths per minute
  - Oxygen saturation <92% on air (or requiring oxygen to maintain SpO₂ ≥92%)
  - Altered mental state (new confusion, drowsiness, or decreased responsiveness)
  - Non-blanching rash or mottled skin
  - Urine output <0.5 ml/kg/hour for more than 2 hours

4. ESCALATION REQUIREMENTS
Any patient meeting sepsis criteria must be reviewed by a senior clinician (ST3 or above, or Advanced Clinical Practitioner) within 30 MINUTES. The Sepsis Response Team can be contacted via extension 2222.

5. DOCUMENTATION
All sepsis assessments must be documented using the Trust Sepsis Screening Tool (Form SS-01) and entered into the electronic patient record within 2 hours of assessment.

6. AUDIT AND GOVERNANCE
Compliance with sepsis protocols is monitored monthly by the Patient Safety Team. Performance data is reported to the Clinical Effectiveness Committee quarterly."""
        },
        {
            "id": "B",
            "title": "Staff Alert: Updated Sepsis Pathway",
            "content": """URGENT STAFF ALERT
To: All Clinical Staff
From: Dr Margaret Chen, Medical Director
Date: 15 March 2024
Re: Changes to Sepsis Pathway

Following recent national guidance updates and our internal mortality review, we are implementing IMMEDIATE changes to our sepsis pathway:

KEY CHANGES:
1. LACTATE TESTING: All patients with suspected sepsis must now have a blood lactate level measured BEFORE antibiotic administration where possible, but this must NOT delay treatment. If lactate cannot be obtained within 15 minutes, proceed with antibiotics.

2. FLUID RESUSCITATION: The initial fluid bolus has been REDUCED from 30ml/kg to 20ml/kg crystalloid, to be given over 30-60 minutes rather than 15-30 minutes. This change follows evidence of harm from aggressive fluid resuscitation in certain patient groups.

3. NEWS2 INTEGRATION: Sepsis screening is now triggered automatically when a patient's NEWS2 score reaches 5 or above, or 3 in a single parameter. The electronic system will prompt staff to complete a sepsis screen.

4. PAEDIATRIC PATHWAY: Children under 16 now have a separate pathway using PEWS (Paediatric Early Warning Score). The adult sepsis criteria should NOT be applied to this age group.

TRAINING: Mandatory e-learning (30 minutes) must be completed by ALL clinical staff by 31 March 2024. Access via the Trust Learning Portal.

QUESTIONS: Contact the Sepsis Lead Nurse, James McCarthy (james.mccarthy@rmh.nhs.uk) or ext. 4455."""
        }
    ],
    "questions_section_1": {
        "type": "text_matching",
        "instruction": "Which text (A, B, C or D) contains the following information?",
        "questions": [
            {"id": 1, "text": "explains who has authority to initiate certain interventions", "answer": "D"},
            {"id": 2, "text": "specifies which score system should not be used for younger patients", "answer": "B"},
            {"id": 3, "text": "identifies the department that collates performance information", "answer": "A"},
            {"id": 4, "text": "provides contact details for queries about drug sensitivities", "answer": "B"},
            {"id": 5, "text": "clarifies when to use the screening tool despite uncertainty", "answer": "D"},
            {"id": 6, "text": "describes a change in the amount of initial fluid given", "answer": "B"},
            {"id": 7, "text": "states the maximum time allowed before antibiotics must be given", "answer": "A"}
        ]
    },
    "questions_section_2": {
        "type": "gap_fill",
        "instruction": "Complete the notes using information from the texts.",
        "questions": [
            {"id": 8, "text": "The Trust aims to give antibiotics within _______ of identifying sepsis.", "answer": "one hour"},
            {"id": 9, "text": "A senior clinician review is required within _______ of meeting sepsis criteria.", "answer": "30 minutes"},
            {"id": 10, "text": "If lactate results cannot be obtained quickly, antibiotics should be given after a maximum of _______ delay.", "answer": "15 minutes"},
            {"id": 11, "text": "The updated fluid resuscitation protocol recommends an initial bolus of _______.", "answer": "20ml/kg"},
            {"id": 12, "text": "Automatic sepsis screening is triggered when NEWS2 score reaches _______ or above.", "answer": "5"},
            {"id": 13, "text": "A lactate level above _______ requires immediate Critical Care referral.", "answer": "4 mmol/L"},
            {"id": 14, "text": "Staff must complete mandatory e-learning by _______.", "answer": "31 March 2024"}
        ]
    },
    "questions_section_3": {
        "type": "short_answer",
        "instruction": "Answer the questions using information from the texts.",
        "questions": [
            {"id": 15, "text": "According to Text A, what telephone extension connects to the Sepsis Response Team?", "answer": "2222"},
            {"id": 16, "text": "In Text C, what is the target oxygen saturation range for patients with COPD?", "answer": "88-92%"},
            {"id": 17, "text": "According to Text B, what score system should be used for patients under 16?", "answer": "PEWS"},
            {"id": 18, "text": "In Text A, what form number is the Sepsis Screening Tool?", "answer": "SS-01"},
            {"id": 19, "text": "According to Text D, what alternatives to catheterisation are mentioned for monitoring urine output?", "answer": "weighing pads"},
            {"id": 20, "text": "In Text B, who is named as the Sepsis Lead Nurse?", "answer": "James McCarthy"}
        ]
    }
}

READING_PART_B = {
    "name": "Part B: Short Workplace Texts",
    "questions": 6,
    "texts": [
        {
            "id": 21,
            "title": "Staff Notice",
            "content": """Following last week's medication incident, we are reinforcing the two-nurse verification protocol for ALL high-risk medications. This is not about assigning blame - we know pressures are high. However, near-miss data shows that time pressure is frequently cited as the reason for shortcut-taking. We need to be clear: there is ALWAYS time to do a proper check. If you feel you cannot complete verification safely, escalate to the nurse in charge immediately. Your professional registration depends on safe practice, not speed.""",
            "question": "What is the writer's main intention?",
            "options": [
                "A. To describe a recent medication incident",
                "B. To announce changes to staff rotas",
                "C. To reinforce existing safety procedures"
            ],
            "answer": "C"
        },
        {
            "id": 22,
            "title": "Email to Ward Staff",
            "content": """Hi all, I know the new electronic observation system has been frustrating - the tablets are slow and the interface isn't intuitive. IT are aware and working on it. In the meantime, please DON'T revert to paper charts. The whole point of the system is real-time visibility for the site team. If we're all documenting on paper, they can't see emerging problems. Yes, it takes longer, but patient safety monitoring depends on it. I've asked for additional devices for the busier areas. Thanks for your patience. Sarah""",
            "question": "What does Sarah want staff to understand?",
            "options": [
                "A. The technical issues will be fixed imminently",
                "B. Paper documentation defeats the monitoring aim",
                "C. Staff should attend additional system training"
            ],
            "answer": "B"
        },
        {
            "id": 23,
            "title": "HR Update",
            "content": """MANDATORY DISCLOSURE REMINDER
All staff are reminded of their obligation to disclose any cautions, convictions, or ongoing police investigations to HR within 72 hours. This applies whether or not the matter relates to your work. Failure to disclose may be treated as a disciplinary matter. If you are unsure whether something needs to be disclosed, please seek confidential advice from HR. We are here to support you through any difficulties, and early disclosure usually results in better outcomes for all involved.""",
            "question": "What does the notice require of staff?",
            "options": [
                "A. Report relevant personal legal matters promptly",
                "B. Attend a meeting with HR about disclosure requirements",
                "C. Complete an online declaration form"
            ],
            "answer": "A"
        },
        {
            "id": 24,
            "title": "Audit Feedback",
            "content": """Hand Hygiene Audit Results - February 2024
Ward compliance: 73% (Trust target: 85%)
While this represents an improvement from January (68%), we remain below target. The most common gap identified was failure to decontaminate hands BEFORE patient contact - "gloves on, hands not cleaned." Remember: gloves are not a substitute for hand hygiene. They protect YOU; hand hygiene protects PATIENTS. Focus for March: Pre-contact compliance""",
            "question": "What does the audit suggest about current practice?",
            "options": [
                "A. Compliance has been steadily declining",
                "B. Cleaning hands before patient contact is a weakness",
                "C. Staff are resisting the monitoring process"
            ],
            "answer": "B"
        },
        {
            "id": 25,
            "title": "Proposal Document",
            "content": """Proposed Change: Extended Visiting Hours Pilot
We propose extending afternoon visiting from 14:00-16:00 to 14:00-19:00 on the medical ward as a three-month pilot. Evidence suggests family presence improves patient nutrition, reduces anxiety, and supports cognitive function in older patients. Staff concerns about interruptions during medication rounds can be addressed through protected times (17:30-18:30 blocked).
Request: Feedback from ward staff by 20th March before proceeding to approval committee.""",
            "question": "What is the purpose of this document?",
            "options": [
                "A. To gather staff opinions on a potential service change",
                "B. To explain why visiting hours are being extended",
                "C. To respond to staff complaints about visitors"
            ],
            "answer": "A"
        },
        {
            "id": 26,
            "title": "Facilities Notice",
            "content": """CAR PARK CLOSURE - ESSENTIAL INFORMATION
The staff car park will be closed 4-8 March for resurfacing. Temporary parking is available at St Mark's Church Hall (5-minute walk). Shuttle buses will run from the church hall to main entrance every 15 minutes from 06:30. IMPORTANT: Do NOT park on surrounding residential streets. Residents have complained and illegally parked vehicles may be ticketed. Consider car-sharing or public transport during this period.""",
            "question": "What does the notice emphasise staff should avoid?",
            "options": [
                "A. Using the alternative parking location",
                "B. Taking the shuttle bus during peak hours",
                "C. Using streets near the hospital for parking"
            ],
            "answer": "C"
        }
    ]
}

READING_PART_C = {
    "name": "Part C: Long Texts",
    "questions": 12,
    "texts": [
        {
            "id": "text_1",
            "title": "Building a Culture of Patient Safety",
            "content": """The concept of "safety culture" has become ubiquitous in healthcare discourse, yet its practical implementation remains frustratingly elusive for many organisations. After two decades of patient safety initiatives, why do preventable harms persist at unacceptable levels?

Part of the answer lies in our fundamental misunderstanding of what culture actually means. Safety culture is not a policy that can be written, a training programme that can be completed, or a poster that can be displayed. It is the accumulation of shared assumptions, values, and behaviours that determine how an organisation actually functions when nobody is watching.

This distinction between "work as imagined" and "work as done" is crucial. Consider medication administration. The written policy might require two nurses to independently check high-risk drugs. The espoused value might be that safety always comes first. But the lived reality—the culture—emerges from daily practice: Do staff feel able to challenge a senior colleague who skips the check? Is there time built into staffing models for proper verification? Are near-misses reported without fear, or quietly covered up?

The most dangerous organisations are often those that believe they have strong safety cultures while simultaneously punishing those who speak up. Research consistently shows that psychological safety—the belief that one will not be humiliated or punished for raising concerns—is the single most important predictor of team performance and error detection.

What, then, does genuine safety culture transformation require? First, visible leadership commitment that goes beyond rhetoric. Leaders must model vulnerability, acknowledge their own errors, and visibly respond to concerns raised by others. Second, investment in reporting systems that are genuinely non-punitive and that feed back learning to frontline staff. Third, and perhaps most challenging, a willingness to examine the fundamental structures—staffing levels, equipment design, communication systems—that create the conditions for error.""",
            "questions": [
                {
                    "id": 27,
                    "question": "What point does the writer make about safety culture in the first two paragraphs?",
                    "options": [
                        "A. Recent initiatives have successfully embedded it",
                        "B. It depends primarily on staff training quality",
                        "C. It cannot be created through formal procedures alone"
                    ],
                    "answer": "C"
                },
                {
                    "id": 28,
                    "question": "According to the writer, what does the medication administration example illustrate?",
                    "options": [
                        "A. The contrast between procedures and how work actually happens",
                        "B. The failure of current staff training methods",
                        "C. The need for additional resources for checking"
                    ],
                    "answer": "A"
                },
                {
                    "id": 29,
                    "question": "What does the writer suggest about psychological safety?",
                    "options": [
                        "A. It develops automatically in well-managed teams",
                        "B. It is essential for error detection and reporting",
                        "C. It is mainly relevant for junior staff members"
                    ],
                    "answer": "B"
                },
                {
                    "id": 30,
                    "question": "What is the writer's view on individual accountability?",
                    "options": [
                        "A. It should be removed from safety frameworks",
                        "B. It should be the primary focus of improvement",
                        "C. It has a place for deliberate harmful behaviour"
                    ],
                    "answer": "C"
                },
                {
                    "id": 31,
                    "question": "According to the writer, what is required for genuine culture change?",
                    "options": [
                        "A. Focus mainly on improving reporting systems",
                        "B. Active demonstration of vulnerability by leaders",
                        "C. Strict enforcement of existing protocols"
                    ],
                    "answer": "B"
                },
                {
                    "id": 32,
                    "question": "What is the overall tone of the passage?",
                    "options": [
                        "A. Analytical while acknowledging challenges",
                        "B. Dismissive of current safety efforts",
                        "C. Highly optimistic about rapid progress"
                    ],
                    "answer": "A"
                }
            ]
        },
        {
            "id": "text_2",
            "title": "Moral Distress in Healthcare Professionals",
            "content": """Moral distress occurs when healthcare professionals believe they know the ethically appropriate action to take but feel constrained from taking it. Unlike ethical dilemmas, where the right course is genuinely uncertain, moral distress involves clarity about what should be done coupled with powerlessness to act accordingly.

The sources of moral distress are varied and often systemic. Inadequate staffing may force clinicians to provide care they know to be substandard. Institutional policies may conflict with professional judgement about individual patient needs. Hierarchical structures may prevent nurses from halting treatments they believe to be futile or harmful.

The consequences extend far beyond individual discomfort. Prolonged exposure to moral distress has been linked to burnout, compassion fatigue, and intention to leave the profession. Some researchers describe a "crescendo effect," where repeated episodes of unresolved moral distress accumulate, ultimately leading to what has been termed "moral residue"—a lasting sense of having compromised one's integrity that can never fully be resolved.

What makes moral distress particularly pernicious is that it often affects the most conscientious professionals most severely. Those who care deeply about ethical practice are precisely those who suffer most when forced to act against their values. There is bitter irony in a healthcare system that selectively drives out its most ethically committed members.

Addressing moral distress requires action at multiple levels. At the individual level, professionals need opportunities to process and discuss ethically challenging situations in supportive environments. At the team level, creating genuine forums for moral deliberation can help distribute the burden and reduce individual isolation. At the organisational level, attention must be paid to the structural factors that create morally distressing situations in the first place.""",
            "questions": [
                {
                    "id": 33,
                    "question": "How does the writer distinguish moral distress from ethical dilemmas?",
                    "options": [
                        "A. Moral distress involves less emotional impact",
                        "B. Moral distress involves certainty about the right action",
                        "C. Ethical dilemmas are easier to resolve than moral distress"
                    ],
                    "answer": "B"
                },
                {
                    "id": 34,
                    "question": "According to the writer, what characterises the sources of moral distress?",
                    "options": [
                        "A. They are primarily caused by individual incompetence",
                        "B. They result mainly from poor communication",
                        "C. They frequently have institutional origins"
                    ],
                    "answer": "C"
                },
                {
                    "id": 35,
                    "question": "What does the term 'moral residue' refer to?",
                    "options": [
                        "A. Relief felt after discussing ethical concerns",
                        "B. The ethical sensitivity that develops over time",
                        "C. Persistent harm from accumulated ethical compromises"
                    ],
                    "answer": "C"
                },
                {
                    "id": 36,
                    "question": "What point does the writer make about which professionals are most affected?",
                    "options": [
                        "A. The most ethically sensitive clinicians are hardest hit",
                        "B. Professionals with less experience cope better",
                        "C. Support staff are largely unaffected"
                    ],
                    "answer": "A"
                },
                {
                    "id": 37,
                    "question": "According to the writer, what often happens when professionals voice ethical concerns?",
                    "options": [
                        "A. They receive additional support and resources",
                        "B. They are categorised as unrealistic or difficult",
                        "C. They are directed to formal ethics committees"
                    ],
                    "answer": "B"
                },
                {
                    "id": 38,
                    "question": "What does the writer suggest about ethics services and debriefings?",
                    "options": [
                        "A. They should be reserved for serious incidents only",
                        "B. They are optional additions when resources permit",
                        "C. They are essential for maintaining ethical practice"
                    ],
                    "answer": "C"
                }
            ]
        }
    ]
}

# ============================================================
# WRITING SUB-TEST (1 letter, 45 minutes)
# ============================================================

WRITING_TASK = {
    "topic_id": "W-016-B",
    "title": "Fall - Home Assessment Needed",
    "letter_type": "Referral to Community Occupational Therapy Team",
    "time": "45 minutes",
    "word_count": "180-200 words",
    "case_notes": {
        "patient": {
            "name": "Mrs Doreen Whitfield",
            "dob": "15 March 1940",
            "age": 84,
            "address": "27 Pemberton Close, Highfield",
            "hospital_number": "HN 447892",
            "consultant": "Mr A. Blackwood (Orthopaedics)",
            "ward": "Maple Rehabilitation Unit"
        },
        "social_background": [
            "Lives alone in two-storey terraced house",
            "Stairs to first floor (bedroom and bathroom upstairs)",
            "Husband deceased 2019",
            "Daughter (Margaret) lives 45 minutes away - works full-time",
            "Neighbour checks in most days",
            "Previously independent with all ADLs",
            "Manages own shopping with occasional help from daughter",
            "Uses reading glasses - good vision",
            "No hearing difficulties"
        ],
        "admission_details": {
            "date": "8 January 2026",
            "presenting_complaint": "Mechanical fall at home - tripped on rug in hallway",
            "injury": "Left neck of femur fracture",
            "surgery": "Dynamic hip screw (DHS) 9 January 2026",
            "post_operative_course": "Uncomplicated",
            "transferred_to_rehab": "15 January 2026"
        },
        "current_status": [
            "Mobilising with wheeled zimmer frame - supervision required on stairs",
            "Needs verbal prompting for safety awareness",
            "Can manage transfers independently",
            "Personal care: Independent with washing/dressing (takes longer than before)",
            "Managing toilet independently",
            "Appetite good - eating full diet",
            "Sleep occasionally disrupted - anxious about going home",
            "Cognition intact - MMSE 28/30"
        ],
        "therapy_progress": {
            "physiotherapy": [
                "Good strength returning to left leg",
                "Hip precautions being observed",
                "Can walk 50 metres with frame before needing rest",
                "Stairs: Manages with rail and supervision (step-to pattern)"
            ],
            "kitchen_assessment": "Safe with meal preparation",
            "balance": "Mild unsteadiness on turning - improving"
        },
        "medications_on_discharge": [
            "Paracetamol 1g QDS PRN",
            "Calcium + Vitamin D 1 tablet daily",
            "Rivaroxaban 10mg OD (VTE prophylaxis - 5 more days)",
            "Amlodipine 5mg OD (existing)",
            "Atorvastatin 20mg ON (existing)"
        ],
        "concerns": [
            "Patient anxious about return home",
            "High step into bathroom (8 inches) - potential hazard",
            "Narrow staircase with single rail (right side only)",
            "Multiple rugs throughout house - trip hazards",
            "Daughter concerned about mother's safety",
            "Patient reluctant to accept care package or alterations"
        ],
        "planned_discharge": "Within 7-10 days if home assessment satisfactory",
        "discharge_goals": [
            "Safe independent mobility at home",
            "Ability to manage stairs safely",
            "Maintained independence with ADLs",
            "Falls prevention strategies in place"
        ],
        "follow_up": [
            "Fracture clinic 6 weeks",
            "Community physiotherapy arranged"
        ]
    },
    "task_instructions": """Using the information in the case notes, write a letter of referral to the Community Occupational Therapy Team requesting an urgent home assessment prior to discharge.

In your letter:
- Explain the reason for the referral and urgency
- Describe the patient's current functional abilities and mobility status
- Outline the specific home environmental concerns identified
- Request assessment and recommendations for safe discharge"""
}

# ============================================================
# SPEAKING SUB-TEST (2 role-plays, ~20 minutes)
# ============================================================

SPEAKING_ROLE_PLAYS = [
    {
        "id": "S-012-B",
        "topic": "Medication Change - Treatment Fatigue",
        "setting": "Diabetes Outpatient Clinic",
        "prep_time": "3 minutes",
        "roleplay_time": "5 minutes",
        "candidate_card": {
            "patient": "Mr Graham Webb, 58 years old",
            "setting": "Diabetes Outpatient Clinic",
            "task": [
                "Explain why the additional medication (empagliflozin) is being recommended",
                "Explore the patient's feelings about his current diabetes management",
                "Address any concerns about side effects",
                "Negotiate a plan that the patient is willing to accept"
            ],
            "patient_notes": {
                "diagnosis": "Type 2 diabetes - 12 years",
                "current_medications": "Metformin 1g BD, Gliclazide 80mg BD",
                "recent_hba1c": "72 mmol/mol (target <58)",
                "bmi": 31,
                "notes": "Previous dietary counselling - some improvement. Doctor has recommended adding empagliflozin 10mg."
            }
        },
        "interlocutor_card": {
            "role": "Graham Webb, 58 years old, warehouse supervisor",
            "situation": """You have had diabetes for 12 years and feel you have done everything asked of you. You changed your diet, lost some weight, and take your tablets regularly. Now you're being told your diabetes isn't controlled well enough and you need ANOTHER tablet.

You feel frustrated and somewhat defeated. You thought you were doing well. Your wife has been on your case about your health, and now this feels like confirmation that you're failing despite your efforts.""",
            "concerns": [
                "Frustrated that dietary changes haven't been enough",
                "Worried about 'how many tablets' you'll end up on",
                "Concerned about side effects - heard this drug 'makes you pee a lot'",
                "Feeling blamed for poor control despite efforts"
            ],
            "responses": {
                "if_asked_about_feelings": "Admit frustration: 'I've done everything I was told, and it's still not good enough.'",
                "if_given_information": "Listen, but express concern: 'My mate Dave said these new tablets gave him terrible thrush.'",
                "if_reassured_about_efforts": "Become slightly more receptive: 'I suppose I have tried... it's just disheartening.'",
                "if_given_choice": "Respond positively to autonomy: 'Well, if we could try it for a few months and see...'",
                "if_pressured": "Become defensive: 'I don't want to just keep adding tablets forever.'"
            },
            "behaviour_notes": "Start frustrated but not angry. Respond well to acknowledgment of your efforts. Become more engaged if given genuine choice. Ultimately willing to try medication if concerns addressed sensitively."
        },
        "avatar_config": {
            "patient_name": "Graham Webb",
            "patient_gender": "male",
            "patient_age": 58,
            "avatar_id": "Aditya_public_4",
            "voice_id": "2eca0d3dd5ec4a1ea6efa6194b19eb78",
            "opening_line": "Oh, hello nurse. I suppose you're here to talk about these new tablets they want me to take. *sighs* I've just about had enough of all this, to be honest."
        }
    },
    {
        "id": "S-046-C",
        "topic": "Patient Education - Warning Signs Recognition",
        "setting": "Surgical Ward - Pre-discharge Education",
        "prep_time": "3 minutes",
        "roleplay_time": "5 minutes",
        "candidate_card": {
            "patient": "Mrs Patricia Holloway, 71 years old",
            "setting": "Surgical Ward - Pre-discharge Education",
            "task": [
                "Explain the warning signs of pulmonary embolism that require immediate medical attention",
                "Provide information about bleeding risks while on rivaroxaban",
                "Ensure the patient understands when to seek help without causing excessive anxiety",
                "Check understanding using teach-back technique"
            ],
            "patient_notes": {
                "surgery": "Right total knee replacement - 4 days ago",
                "discharge_planned": "Tomorrow",
                "anticoagulation": "Rivaroxaban 10mg OD for 14 days (DVT prophylaxis)",
                "relevant_history": "No previous clots, no bleeding disorders",
                "notes": "Patient seems anxious about going home"
            }
        },
        "interlocutor_card": {
            "role": "Patricia Holloway, 71 years old, retired teacher",
            "situation": """You are being discharged tomorrow after knee replacement surgery. The doctors have mentioned blood clots as a risk and you're taking a blood-thinning tablet. You're quite anxious about this - your neighbour's husband died of a pulmonary embolism last year, which has made you worried.

You want to understand what symptoms to look out for but are also worried about becoming paranoid about every little symptom. You tend to be quite health-anxious.""",
            "concerns": [
                "Worried about blood clots - neighbour's husband died of PE",
                "Anxious about taking 'blood thinners' - scared of bleeding",
                "Want clear information but don't want to become paranoid",
                "Wondering if every leg pain or breathlessness could be a clot"
            ],
            "responses": {
                "if_asked_about_worries": "Share your neighbour's story: 'My neighbour Margaret's husband died suddenly from a clot last year. I can't stop thinking about it.'",
                "if_given_symptoms": "Ask clarifying questions: 'But I get breathless sometimes anyway - how will I know the difference?'",
                "if_reassured_about_risk": "Somewhat relieved: 'So it's not as common as I thought?'",
                "if_asked_to_repeat": "Try to remember but may get some details wrong: 'So... sudden breathing trouble, chest pain, and... was there something about the leg?'",
                "if_overwhelmed": "Express concern: 'This is a lot to remember. What if I forget something important?'"
            },
            "behaviour_notes": "Anxious but intellectually engaged. Ask questions for clarification. Appreciate written information to take home. Need reassurance that medication risk is worth it. Respond well to calm, clear explanations."
        },
        "avatar_config": {
            "patient_name": "Patricia Holloway",
            "patient_gender": "female",
            "patient_age": 71,
            "avatar_id": "Abigail_expressive_2024112501",
            "voice_id": "M2WosQ2Ju3f2b7jdddsj",
            "opening_line": "Oh, hello nurse. I'm so glad someone's come to explain things before I go home. I must admit, I'm feeling a bit nervous about leaving. My neighbour, you see, she had something similar and it went to her lungs..."
        }
    }
]

# Complete exam data structure
OET_NUR_013_EXAM = {
    "metadata": EXAM_METADATA,
    "listening": {
        "part_a": LISTENING_PART_A,
        "part_b": LISTENING_PART_B,
        "part_c": LISTENING_PART_C
    },
    "reading": {
        "part_a": READING_PART_A,
        "part_b": READING_PART_B,
        "part_c": READING_PART_C
    },
    "writing": WRITING_TASK,
    "speaking": SPEAKING_ROLE_PLAYS
}
