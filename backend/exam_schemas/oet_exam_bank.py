"""
OET Sample Exams - 5 Complete Exams for Nursing
Based on official OET format and healthcare scenarios
"""

OET_EXAM_BANK = {
    "exam_1": {
        "exam_id": "oet_nursing_001",
        "exam_number": 1,
        "profession": "nursing",
        "created_at": "2025-01-13T00:00:00Z",
        "validation_status": "pending_human_review",
        "topics_covered": ["diabetes_management", "wound_care", "medication_administration", "patient_discharge"],
        "difficulty_distribution": {"easy": 30, "medium": 50, "hard": 20},
        
        "listening": {
            "part_a": {
                "consultation_1": {
                    "scenario": "A nurse is admitting a 67-year-old male patient with Type 2 diabetes who has developed a foot ulcer.",
                    "duration_seconds": 240,
                    "dialogue": [
                        {"speaker": "nurse", "text": "Good morning, Mr Henderson. I'm Sarah, your admitting nurse. I'll be taking some details about your medical history today."},
                        {"speaker": "patient", "text": "Good morning. Yes, my GP sent me here because of this wound on my foot that won't heal."},
                        {"speaker": "nurse", "text": "I can see from your referral that you have Type 2 diabetes. How long have you had diabetes?"},
                        {"speaker": "patient", "text": "About fifteen years now. I was diagnosed when I was fifty-two."},
                        {"speaker": "nurse", "text": "And how do you manage your diabetes currently?"},
                        {"speaker": "patient", "text": "I take metformin twice a day, 500 milligrams each time. And I also inject insulin at night, about twenty units."},
                        {"speaker": "nurse", "text": "Do you monitor your blood sugar levels at home?"},
                        {"speaker": "patient", "text": "Yes, I check it every morning before breakfast. It's usually around eight or nine."},
                        {"speaker": "nurse", "text": "And when did you first notice the problem with your foot?"},
                        {"speaker": "patient", "text": "About three weeks ago. I noticed a small blister after wearing new shoes. It turned into an open sore."},
                        {"speaker": "nurse", "text": "Has there been any discharge from the wound?"},
                        {"speaker": "patient", "text": "Yes, there's been some yellowish fluid coming out for the past week."},
                        {"speaker": "nurse", "text": "Have you experienced any fever or chills?"},
                        {"speaker": "patient", "text": "I had a slight temperature two days ago, about thirty-seven point eight."}
                    ],
                    "questions": [
                        {"number": 1, "blank": "Patient has had diabetes for ___ years", "answer": "fifteen", "acceptable": ["15"]},
                        {"number": 2, "blank": "Patient was diagnosed at age ___", "answer": "fifty-two", "acceptable": ["52"]},
                        {"number": 3, "blank": "Takes metformin ___ daily", "answer": "twice", "acceptable": ["two times", "2 times"]},
                        {"number": 4, "blank": "Metformin dose: ___ milligrams", "answer": "500", "acceptable": ["five hundred"]},
                        {"number": 5, "blank": "Insulin dose at night: ___ units", "answer": "twenty", "acceptable": ["20"]},
                        {"number": 6, "blank": "Blood sugar usually ___ or nine", "answer": "eight", "acceptable": ["8"]},
                        {"number": 7, "blank": "Foot problem started ___ weeks ago", "answer": "three", "acceptable": ["3"]},
                        {"number": 8, "blank": "Initial injury caused by ___ shoes", "answer": "new", "acceptable": []},
                        {"number": 9, "blank": "Wound discharge color: ___", "answer": "yellowish", "acceptable": ["yellow"]},
                        {"number": 10, "blank": "Discharge present for past ___", "answer": "week", "acceptable": ["one week", "1 week"]},
                        {"number": 11, "blank": "Temperature two days ago: ___", "answer": "thirty-seven point eight", "acceptable": ["37.8"]},
                        {"number": 12, "blank": "Blood sugar checked every ___ before breakfast", "answer": "morning", "acceptable": []}
                    ]
                },
                "consultation_2": {
                    "scenario": "A nurse is providing discharge instructions to a patient who underwent knee replacement surgery.",
                    "duration_seconds": 240,
                    "dialogue": [
                        {"speaker": "nurse", "text": "Mrs Patterson, before you go home today, I need to go through your discharge instructions with you."},
                        {"speaker": "patient", "text": "Yes, I've been waiting for this. I'm a bit nervous about managing at home."},
                        {"speaker": "nurse", "text": "That's completely understandable. First, let's talk about your medications. You'll be taking paracetamol one gram four times a day for pain."},
                        {"speaker": "patient", "text": "Four times a day? What times should I take it?"},
                        {"speaker": "nurse", "text": "Take it at six in the morning, then midday, then six in the evening, and finally before bed at ten."},
                        {"speaker": "patient", "text": "And what about the blood thinning medication?"},
                        {"speaker": "nurse", "text": "You'll continue the enoxaparin injections for two more weeks. That's forty milligrams once daily, injected into your abdomen."},
                        {"speaker": "patient", "text": "I'm worried about the exercises. How often should I do them?"},
                        {"speaker": "nurse", "text": "The physiotherapist has given you a sheet with five exercises. Do each exercise ten times, three times a day."},
                        {"speaker": "patient", "text": "And when can I shower?"},
                        {"speaker": "nurse", "text": "Keep the wound dry for seven days. After that, you can shower but don't soak in a bath for four weeks."},
                        {"speaker": "patient", "text": "When do I come back to see the surgeon?"},
                        {"speaker": "nurse", "text": "Your follow-up appointment is in two weeks, on the twenty-eighth of January at nine-thirty."}
                    ],
                    "questions": [
                        {"number": 13, "blank": "Paracetamol dose: ___ gram", "answer": "one", "acceptable": ["1"]},
                        {"number": 14, "blank": "Paracetamol frequency: ___ times daily", "answer": "four", "acceptable": ["4"]},
                        {"number": 15, "blank": "First dose time: ___ in the morning", "answer": "six", "acceptable": ["6", "6am"]},
                        {"number": 16, "blank": "Last dose time: before bed at ___", "answer": "ten", "acceptable": ["10", "10pm"]},
                        {"number": 17, "blank": "Enoxaparin duration: ___ more weeks", "answer": "two", "acceptable": ["2"]},
                        {"number": 18, "blank": "Enoxaparin dose: ___ milligrams", "answer": "forty", "acceptable": ["40"]},
                        {"number": 19, "blank": "Injection site: ___", "answer": "abdomen", "acceptable": ["stomach", "tummy"]},
                        {"number": 20, "blank": "Number of exercises given: ___", "answer": "five", "acceptable": ["5"]},
                        {"number": 21, "blank": "Repetitions per exercise: ___", "answer": "ten", "acceptable": ["10"]},
                        {"number": 22, "blank": "Keep wound dry for ___ days", "answer": "seven", "acceptable": ["7"]},
                        {"number": 23, "blank": "No bath for ___ weeks", "answer": "four", "acceptable": ["4"]},
                        {"number": 24, "blank": "Follow-up appointment time: ___", "answer": "nine-thirty", "acceptable": ["9:30", "9.30"]}
                    ]
                }
            },
            "part_b": {
                "extracts": [
                    {
                        "number": 1,
                        "context": "Hospital announcement about visitor policy",
                        "audio_text": "Attention all staff and visitors. Due to the current flu outbreak, visiting hours have been restricted to two to four PM only. All visitors must sanitize their hands on entry and wear a surgical mask. Children under twelve are not permitted to visit until further notice. Thank you for your cooperation.",
                        "question": "What is the main reason for the restrictions?",
                        "options": ["A) Staff shortages", "B) Flu outbreak", "C) Building maintenance"],
                        "answer": "B"
                    },
                    {
                        "number": 2,
                        "context": "Nurse handover about patient",
                        "audio_text": "Mr Chen in bed four needs his dressing changed this afternoon. He's been complaining of increased pain around the wound site. His last dose of morphine was at eleven AM. He's due for his next dose at three PM, but if the pain is severe, you can give it earlier. Also, his family is coming at two, so try to do the dressing before then if possible.",
                        "question": "When should the dressing ideally be changed?",
                        "options": ["A) Before 2 PM", "B) At 3 PM", "C) After the family visit"],
                        "answer": "A"
                    },
                    {
                        "number": 3,
                        "context": "Pharmacy notification",
                        "audio_text": "This is a notification from pharmacy. The supply of amoxicillin 500mg capsules is currently limited. Please use amoxicillin suspension as an alternative where appropriate. For patients who cannot take the suspension, please contact pharmacy directly to arrange individual supplies. Normal stock levels are expected to resume by next Monday.",
                        "question": "What should nurses do if a patient cannot take the suspension?",
                        "options": ["A) Wait until Monday", "B) Contact pharmacy", "C) Use a different antibiotic"],
                        "answer": "B"
                    },
                    {
                        "number": 4,
                        "context": "Staff meeting announcement",
                        "audio_text": "Reminder that the mandatory hand hygiene training session is tomorrow at two PM in the education center. All nursing staff who haven't completed this training must attend. If you've already done the online module this month, you're exempt. Please bring your staff ID for registration. The session will take approximately forty-five minutes.",
                        "question": "Who does NOT need to attend the training?",
                        "options": ["A) New nursing staff", "B) Staff who completed online training", "C) Staff without ID"],
                        "answer": "B"
                    },
                    {
                        "number": 5,
                        "context": "Emergency department update",
                        "audio_text": "ED update: We're currently experiencing high patient volumes. Waiting time for triage category three patients is approximately three hours. Please inform patients in the waiting area. If any patient's condition deteriorates, they should inform the triage nurse immediately for reassessment. Ambulance arrivals continue to have priority.",
                        "question": "What should patients do if they feel worse while waiting?",
                        "options": ["A) Leave and return later", "B) Tell the triage nurse", "C) Wait for their turn"],
                        "answer": "B"
                    },
                    {
                        "number": 6,
                        "context": "Infection control notice",
                        "audio_text": "Attention ward six staff. The patient in room four has been confirmed with Clostridium difficile infection. Standard contact precautions are now in place. Please use dedicated equipment for this patient and ensure thorough hand washing with soap and water, as alcohol gel is not effective against C. diff. Gowns and gloves must be worn for all patient contact.",
                        "question": "Why is soap and water recommended instead of alcohol gel?",
                        "options": ["A) There's no alcohol gel available", "B) The patient is allergic to gel", "C) Alcohol gel doesn't kill C. diff"],
                        "answer": "C"
                    }
                ]
            },
            "part_c": {
                "presentation_1": {
                    "title": "Managing Chronic Pain in Elderly Patients",
                    "speaker": "Dr. Rebecca Morrison, Pain Management Specialist",
                    "duration_seconds": 300,
                    "transcript": """
Thank you for inviting me to speak today about chronic pain management in elderly patients. This is a topic that affects a significant proportion of our aging population, with studies showing that up to fifty percent of community-dwelling elderly people experience chronic pain.

One of the key challenges we face is the under-reporting of pain by elderly patients. Many older adults believe that pain is simply a normal part of aging and therefore don't mention it to healthcare providers. Others may fear that reporting pain will lead to unwanted interventions or a loss of independence.

Assessment of pain in the elderly requires particular attention. Standard pain scales may not be appropriate for all patients, especially those with cognitive impairment. In my practice, I find behavioral indicators such as facial expressions, body movements, and changes in activity patterns to be invaluable assessment tools.

When it comes to treatment, we need to consider the physiological changes that occur with aging. Elderly patients often have reduced kidney and liver function, which affects how medications are processed. This means we typically need to start with lower doses and increase gradually. The old saying 'start low and go slow' is particularly relevant here.

Non-pharmacological approaches should always be considered as part of a comprehensive pain management plan. Physical therapy, heat therapy, and cognitive behavioral techniques can all play important roles. I've seen remarkable improvements in patients who engage in regular, gentle exercise programs tailored to their abilities.

Finally, I want to emphasize the importance of regular reassessment. Pain management is not a 'set and forget' approach. We need to continually evaluate the effectiveness of our interventions and adjust as needed.
""",
                    "questions": [
                        {
                            "number": 1,
                            "question": "According to the speaker, what percentage of elderly people in the community experience chronic pain?",
                            "options": ["A) Up to 30%", "B) Up to 50%", "C) Up to 70%"],
                            "answer": "B"
                        },
                        {
                            "number": 2,
                            "question": "Why do some elderly patients not report their pain?",
                            "options": ["A) They forget to mention it", "B) They think it's a normal part of aging", "C) They don't trust healthcare providers"],
                            "answer": "B"
                        },
                        {
                            "number": 3,
                            "question": "What does the speaker find useful when assessing pain in cognitively impaired patients?",
                            "options": ["A) Standard pain scales", "B) Patient self-reports", "C) Behavioral indicators"],
                            "answer": "C"
                        },
                        {
                            "number": 4,
                            "question": "Why does medication dosing need to be adjusted for elderly patients?",
                            "options": ["A) They are more sensitive to pain", "B) Their organs process medications differently", "C) They take too many other medications"],
                            "answer": "B"
                        },
                        {
                            "number": 5,
                            "question": "What does the phrase 'start low and go slow' refer to?",
                            "options": ["A) Exercise intensity", "B) Medication dosing", "C) Pain assessment"],
                            "answer": "B"
                        },
                        {
                            "number": 6,
                            "question": "What does the speaker emphasize about pain management?",
                            "options": ["A) It requires ongoing reassessment", "B) Medication is always necessary", "C) It should be managed by specialists only"],
                            "answer": "A"
                        }
                    ]
                },
                "presentation_2": {
                    "title": "Preventing Hospital-Acquired Infections",
                    "speaker": "Nurse Manager Jane Wilson",
                    "duration_seconds": 300,
                    "transcript": """
Good afternoon everyone. Today I want to talk about something that should be at the forefront of every healthcare worker's mind: hospital-acquired infections, or HAIs.

The statistics are sobering. In Australia alone, approximately 165,000 hospital-acquired infections occur each year. These infections not only cause significant suffering for patients but also result in extended hospital stays, increased healthcare costs, and in some cases, death.

The most common types of HAIs we see are urinary tract infections related to catheter use, surgical site infections, bloodstream infections often associated with central lines, and pneumonia, particularly ventilator-associated pneumonia. Each of these is largely preventable with proper protocols.

Hand hygiene remains our most powerful weapon against infection transmission. The World Health Organization's Five Moments for Hand Hygiene should be second nature to all of us: before patient contact, before aseptic procedures, after body fluid exposure, after patient contact, and after contact with patient surroundings.

However, despite knowing this, compliance rates remain disappointingly low in many healthcare settings. Studies consistently show that healthcare workers perform hand hygiene less than fifty percent of the time when indicated. We need to do better.

Beyond hand hygiene, we need to focus on device-related infections. Every day, we should be asking: does this patient still need this catheter? Does this patient still need this central line? The longer these devices remain in place, the greater the risk of infection.

I also want to highlight the importance of environmental cleaning. Surfaces in patient rooms can harbor dangerous pathogens. High-touch surfaces like bed rails, door handles, and call buttons need to be cleaned multiple times daily.

Finally, I encourage everyone to speak up if you see a colleague not following infection control protocols. We all have a responsibility to protect our patients.
""",
                    "questions": [
                        {
                            "number": 7,
                            "question": "How many hospital-acquired infections occur in Australia annually?",
                            "options": ["A) About 65,000", "B) About 165,000", "C) About 265,000"],
                            "answer": "B"
                        },
                        {
                            "number": 8,
                            "question": "According to the speaker, what is the most effective method for preventing infection transmission?",
                            "options": ["A) Wearing gloves", "B) Hand hygiene", "C) Environmental cleaning"],
                            "answer": "B"
                        },
                        {
                            "number": 9,
                            "question": "What percentage of the time do healthcare workers perform hand hygiene when needed?",
                            "options": ["A) Less than 50%", "B) About 70%", "C) More than 80%"],
                            "answer": "A"
                        },
                        {
                            "number": 10,
                            "question": "What question does the speaker suggest asking daily about devices?",
                            "options": ["A) Is it functioning properly?", "B) Does the patient still need it?", "C) Has it been replaced recently?"],
                            "answer": "B"
                        },
                        {
                            "number": 11,
                            "question": "What does the speaker say about high-touch surfaces?",
                            "options": ["A) They should be avoided", "B) They need cleaning multiple times daily", "C) They are not a major concern"],
                            "answer": "B"
                        },
                        {
                            "number": 12,
                            "question": "What does the speaker encourage staff to do if they see protocol violations?",
                            "options": ["A) Report to management later", "B) Speak up immediately", "C) Document it in the notes"],
                            "answer": "B"
                        }
                    ]
                }
            }
        },
        
        "reading": {
            "part_a": {
                "theme": "Pressure Injury Prevention",
                "time_limit_minutes": 15,
                "texts": {
                    "A": {
                        "title": "Case Study: Mrs. Thompson",
                        "type": "case_study",
                        "content": """Mrs. Thompson, 82, was admitted following a fractured hip. She has limited mobility and is confined to bed. On admission, her Waterlow score was 18, indicating high risk for pressure injuries. The nursing team implemented a repositioning schedule of every two hours. Despite these measures, a Stage 1 pressure injury developed on her sacrum on day three. The wound care nurse recommended a pressure-redistributing mattress and increased repositioning frequency to every ninety minutes. Nutritional assessment revealed protein deficiency, and a dietitian consultation was requested. By day ten, the pressure injury had resolved with no skin breakdown."""
                    },
                    "B": {
                        "title": "Clinical Guideline: Pressure Injury Prevention",
                        "type": "guideline",
                        "content": """All patients should undergo pressure injury risk assessment within eight hours of admission using a validated tool such as the Waterlow or Braden scale. Patients scoring 'at risk' or above require a documented prevention care plan. Repositioning should occur at minimum every two hours for bed-bound patients and every hour for chair-bound patients. Skin inspection should be conducted at each repositioning, with particular attention to bony prominences. Pressure-redistributing devices should be considered for high-risk patients. Adequate nutrition and hydration are essential components of prevention. All pressure injuries must be reported and documented according to facility protocol."""
                    },
                    "C": {
                        "title": "Research Summary: Repositioning Frequency",
                        "type": "research",
                        "content": """A recent multicentre trial compared two-hourly and three-hourly repositioning schedules in 942 nursing home residents at moderate to high risk of pressure injuries. Over the four-week study period, the incidence of Stage 2 or greater pressure injuries was 3.2% in the two-hourly group versus 5.8% in the three-hourly group. However, the difference was not statistically significant (p=0.08). Interestingly, residents in the three-hourly group reported significantly better sleep quality. The researchers concluded that individual risk assessment should guide repositioning frequency rather than applying a standard schedule to all patients."""
                    },
                    "D": {
                        "title": "Ward Policy: Pressure Injury Documentation",
                        "type": "policy",
                        "content": """All newly identified pressure injuries must be photographed and documented within 24 hours of detection. Documentation must include: location, stage, dimensions (length x width x depth), wound bed description, exudate type and amount, surrounding skin condition, and pain assessment. The wound care nurse must be notified within 48 hours for Stage 2 and above injuries. Progress notes should be updated at each dressing change. For hospital-acquired pressure injuries, an incident report must be completed within 24 hours. Monthly audits are conducted to monitor compliance with prevention protocols."""
                    }
                },
                "questions": [
                    {"number": 1, "type": "matching", "question": "Which text describes a specific patient's experience with pressure injury?", "answer": "A"},
                    {"number": 2, "type": "matching", "question": "Which text provides evidence about optimal repositioning frequency?", "answer": "C"},
                    {"number": 3, "type": "matching", "question": "Which text outlines requirements for recording wound details?", "answer": "D"},
                    {"number": 4, "type": "matching", "question": "Which text specifies timeframes for risk assessment?", "answer": "B"},
                    {"number": 5, "type": "matching", "question": "Which text mentions patient-reported outcomes?", "answer": "C"},
                    {"number": 6, "type": "matching", "question": "Which text discusses the role of nutrition in prevention?", "answer": "B"},
                    {"number": 7, "type": "matching", "question": "Which text mentions involvement of a wound care specialist?", "answer": "A"},
                    {"number": 8, "type": "matching", "question": "Which text describes incident reporting requirements?", "answer": "D"},
                    {"number": 9, "type": "short_answer", "question": "What was Mrs. Thompson's Waterlow score on admission?", "answer": "18"},
                    {"number": 10, "type": "short_answer", "question": "How often should chair-bound patients be repositioned according to the guideline?", "answer": "every hour"},
                    {"number": 11, "type": "short_answer", "question": "How many residents participated in the repositioning study?", "answer": "942"},
                    {"number": 12, "type": "short_answer", "question": "Within what timeframe must Stage 2 injuries be reported to the wound care nurse?", "answer": "48 hours"},
                    {"number": 13, "type": "gap_fill", "question": "Mrs. Thompson's pressure injury was located on her ___", "answer": "sacrum"},
                    {"number": 14, "type": "gap_fill", "question": "The research study lasted for ___ weeks", "answer": "four"},
                    {"number": 15, "type": "gap_fill", "question": "Risk assessment must occur within ___ hours of admission", "answer": "eight"},
                    {"number": 16, "type": "gap_fill", "question": "New pressure injuries must be photographed within ___ hours", "answer": "24"},
                    {"number": 17, "type": "gap_fill", "question": "Mrs. Thompson was found to have ___ deficiency", "answer": "protein"},
                    {"number": 18, "type": "gap_fill", "question": "The incidence of pressure injuries in the two-hourly group was ___percent", "answer": "3.2"},
                    {"number": 19, "type": "gap_fill", "question": "Mrs. Thompson's repositioning was increased to every ___ minutes", "answer": "ninety"},
                    {"number": 20, "type": "gap_fill", "question": "Compliance audits are conducted ___", "answer": "monthly"}
                ]
            },
            "part_b": {
                "texts": [
                    {
                        "number": 1,
                        "title": "Medication Storage Notice",
                        "content": "Reminder: All Schedule 8 medications must be stored in the locked cupboard and double-signed when administered. The cupboard key is held by the nurse in charge. Random audits will be conducted weekly. Any discrepancies must be reported to pharmacy immediately. Do not leave the cupboard unlocked at any time, even briefly.",
                        "question": "What is required when giving Schedule 8 medications?",
                        "options": ["A) A pharmacy consultation", "B) Two signatures", "C) Manager approval"],
                        "answer": "B"
                    },
                    {
                        "number": 2,
                        "title": "Patient Transfer Protocol",
                        "content": "When transferring patients between wards, ensure all documentation accompanies the patient including: medication chart, observation chart, nursing care plan, and any relevant test results. The receiving ward must be contacted 30 minutes prior to transfer. The patient's allocated nurse must provide verbal handover to the receiving nurse, covering current status, pending tasks, and any concerns.",
                        "question": "What must happen before a patient is transferred?",
                        "options": ["A) All tests must be completed", "B) The receiving ward must be notified", "C) A doctor must give approval"],
                        "answer": "B"
                    },
                    {
                        "number": 3,
                        "title": "Blood Transfusion Safety",
                        "content": "Two registered nurses must verify patient identity and blood product details at the bedside before commencing any blood transfusion. Vital signs must be recorded: before starting, 15 minutes after starting, then hourly during the transfusion, and 30 minutes after completion. Any suspected transfusion reaction requires immediate cessation of the transfusion - do not discard the blood bag.",
                        "question": "If a transfusion reaction is suspected, what should be done with the blood bag?",
                        "options": ["A) Return it to the blood bank", "B) Keep it - don't throw it away", "C) Send it to the laboratory"],
                        "answer": "B"
                    },
                    {
                        "number": 4,
                        "title": "Falls Prevention Alert",
                        "content": "Patients identified as high falls risk (score 12 or above) must have: yellow falls risk identification band, yellow star on door, call bell within reach at all times, bed in lowest position, and hourly rounding documented. Non-slip footwear should be encouraged. Any patient who falls, regardless of injury, requires medical review within 2 hours and completion of an incident report.",
                        "question": "What indicates a high falls risk score?",
                        "options": ["A) Score of 10 or above", "B) Score of 12 or above", "C) Score of 15 or above"],
                        "answer": "B"
                    },
                    {
                        "number": 5,
                        "title": "Insulin Administration",
                        "content": "All insulin doses must be double-checked by two nurses before administration. When using insulin pens, a new needle must be used for each injection. Never mix different types of insulin in the same syringe unless specifically prescribed. Document the injection site and rotate sites to prevent lipohypertrophy. Blood glucose must be checked before meals for patients on rapid-acting insulin.",
                        "question": "When should blood glucose be checked for patients on rapid-acting insulin?",
                        "options": ["A) After meals", "B) Before meals", "C) At bedtime"],
                        "answer": "B"
                    },
                    {
                        "number": 6,
                        "title": "Discharge Medication Counselling",
                        "content": "Before discharge, patients must receive counselling on all new medications. This should include: purpose of each medication, correct dose and timing, potential side effects, interactions to avoid, and what to do if a dose is missed. Document the counselling in the discharge summary. Patients should be encouraged to ask questions and repeat back key information to confirm understanding.",
                        "question": "How should nurses confirm patient understanding of medications?",
                        "options": ["A) Give them written instructions", "B) Ask them to repeat back information", "C) Check with family members"],
                        "answer": "B"
                    }
                ]
            },
            "part_c": {
                "texts": [
                    {
                        "number": 1,
                        "title": "The Evolution of Nursing Documentation",
                        "word_count": 650,
                        "content": """
The transition from paper-based to electronic nursing documentation has transformed healthcare delivery in ways that extend far beyond simple record-keeping. While the primary goal of any documentation system is to provide accurate, accessible information about patient care, electronic health records (EHRs) have introduced capabilities that paper could never offer.

Early adopters of electronic documentation faced significant resistance from nursing staff. Many experienced nurses felt that computers created a barrier between themselves and their patients, forcing them to spend more time looking at screens than providing direct care. These concerns were not unfounded – initial implementations often increased documentation time rather than reducing it, as staff struggled with unfamiliar interfaces and workflows.

However, as systems have matured and nurses have become more technologically proficient, the benefits have become increasingly apparent. Real-time access to patient information means that nurses no longer need to hunt for paper charts or wait for results to be filed. Medication administration has become safer through built-in alerts that warn of potential allergies, interactions, or incorrect dosing. Clinical decision support tools prompt nurses to consider evidence-based interventions they might otherwise overlook.

Perhaps most significantly, electronic documentation has enabled data analysis that was simply impossible with paper records. Healthcare organizations can now identify patterns in patient outcomes, track quality indicators, and benchmark their performance against similar institutions. This data-driven approach has contributed to measurable improvements in patient safety and care quality across the healthcare sector.

Despite these advances, challenges remain. Many nurses report that EHR systems are designed primarily with billing and administrative requirements in mind, rather than clinical workflow. The phenomenon of 'alert fatigue' – where clinicians become desensitized to warnings due to their sheer volume – has emerged as a significant safety concern. There are also ongoing concerns about the impact of screen-focused documentation on nurse-patient relationships and the development of clinical judgment.

Looking forward, emerging technologies promise to address some of these limitations. Voice recognition software may allow nurses to document while maintaining eye contact with patients. Artificial intelligence could help filter alerts to show only the most clinically relevant warnings. Mobile devices enable documentation at the bedside rather than at a distant computer terminal.

The key lesson from two decades of electronic documentation is that technology alone cannot improve care – success depends on thoughtful implementation that considers the needs of clinicians, patients, and organizations. The most effective systems are those developed with significant nursing input, regularly refined based on user feedback, and supported by adequate training and technical resources.

As healthcare continues to evolve, so too will our documentation systems. The nurses of tomorrow will likely look back on current EHRs as primitive compared to the integrated, intelligent systems they will use. However, the fundamental purpose will remain unchanged: to support the delivery of safe, effective, patient-centered care.
""",
                        "questions": [
                            {"number": 1, "question": "What was a common concern among nurses when electronic documentation was first introduced?", "options": ["A) The systems were too expensive", "B) Computers created barriers with patients", "C) Paper records were more accurate"], "answer": "B"},
                            {"number": 2, "question": "According to the text, what has electronic documentation enabled that wasn't possible before?", "options": ["A) Faster patient discharge", "B) Better data analysis and pattern identification", "C) Reduced staffing requirements"], "answer": "B"},
                            {"number": 3, "question": "What does 'alert fatigue' refer to?", "options": ["A) Nurses getting tired from long shifts", "B) Clinicians becoming desensitized to warnings", "C) Systems crashing from too many alerts"], "answer": "B"},
                            {"number": 4, "question": "What criticism does the text make about current EHR systems?", "options": ["A) They are too focused on billing rather than clinical needs", "B) They are too complicated for nurses to learn", "C) They don't store enough patient information"], "answer": "A"},
                            {"number": 5, "question": "What does the author suggest is key to successful electronic documentation?", "options": ["A) Choosing the most advanced technology", "B) Mandatory training for all staff", "C) Thoughtful implementation with nursing input"], "answer": "C"},
                            {"number": 6, "question": "How does the author view future documentation systems?", "options": ["A) They will be similar to current systems", "B) They will be more integrated and intelligent", "C) They will return to paper-based records"], "answer": "B"},
                            {"number": 7, "question": "What is the author's overall tone regarding electronic documentation?", "options": ["A) Highly critical", "B) Cautiously optimistic", "C) Completely enthusiastic"], "answer": "B"},
                            {"number": 8, "question": "According to the text, what will remain unchanged despite technological advances?", "options": ["A) The documentation software used", "B) The purpose of supporting safe patient care", "C) The time spent on documentation"], "answer": "B"}
                        ]
                    },
                    {
                        "number": 2,
                        "title": "Understanding Antimicrobial Stewardship in Nursing Practice",
                        "word_count": 680,
                        "content": """
Antimicrobial resistance represents one of the most pressing public health challenges of our time. The World Health Organization has warned that without urgent action, we face a 'post-antibiotic era' where common infections could once again become killers. Within this context, nurses play a crucial but often underappreciated role in antimicrobial stewardship – the coordinated effort to optimize antimicrobial use and minimize resistance.

Traditionally, antimicrobial stewardship has been viewed as primarily the domain of doctors and pharmacists. Physicians make prescribing decisions; pharmacists monitor for appropriate dosing and interactions. Nurses, in this view, simply administer what is prescribed. This perspective fundamentally underestimates the nursing contribution to effective antimicrobial use.

Consider the daily realities of hospital care. Nurses are typically the first to recognize signs of infection – the subtle change in a patient's temperature, the unexpected confusion in an elderly patient, the wound that doesn't look quite right. Early recognition leads to earlier diagnosis, which in turn enables more targeted antimicrobial therapy rather than broad-spectrum empiric treatment.

Nurses also play a vital role in ensuring antimicrobials are administered correctly. Timing matters enormously for many antibiotics – some must be given at precise intervals to maintain therapeutic levels, others must be given with or without food to ensure proper absorption. A medication given four hours late or with a meal that impairs absorption may be significantly less effective. Nurses who understand these principles can advocate for administration times that optimize therapeutic effect.

Perhaps most importantly, nurses are essential to the prevention of infections in the first place. Every infection prevented is an antimicrobial that doesn't need to be prescribed. Meticulous hand hygiene, proper wound care, optimal catheter management, and vigilant monitoring all contribute to reducing the burden of healthcare-associated infections.

However, research suggests that nurses often feel inadequately prepared for stewardship roles. Studies have found that nursing education provides limited content on antimicrobial resistance and stewardship principles. Many nurses report feeling uncertain about when to question antimicrobial prescriptions or how to communicate concerns to prescribing doctors. There is clearly scope for improving both pre-registration education and ongoing professional development in this area.

Some healthcare organizations have begun to formally integrate nurses into stewardship teams, recognizing their unique contributions. Nurse stewardship champions can serve as clinical resources, role models, and change agents within their units. They can identify prescribing patterns that warrant review, ensure cultures are collected before antibiotics are started, and promote timely transition from intravenous to oral therapy.

The importance of nursing engagement in stewardship extends beyond the hospital setting. Community nurses caring for patients with complex conditions often manage long-term antimicrobial therapy. Nurses in aged care facilities, where antibiotic use is typically high and often inappropriate, can influence prescribing through their assessments and communications with medical staff.

For stewardship programs to achieve their full potential, nursing must be recognized as an equal partner alongside medicine and pharmacy. This requires organizational commitment to education, inclusion of nurses in governance structures, and creation of clear pathways for nurses to raise concerns about antimicrobial use. The future of effective infection management depends on harnessing the knowledge and proximity to patients that nurses uniquely possess.
""",
                        "questions": [
                            {"number": 9, "question": "According to the text, how has nursing's role in antimicrobial stewardship traditionally been viewed?", "options": ["A) As essential to decision-making", "B) As primarily about medication administration", "C) As more important than doctors' roles"], "answer": "B"},
                            {"number": 10, "question": "Why does the author emphasize the importance of timing in antibiotic administration?", "options": ["A) Because it affects staffing schedules", "B) Because it determines how effective the medication is", "C) Because patients prefer consistent timing"], "answer": "B"},
                            {"number": 11, "question": "What does the text suggest about nursing education regarding antimicrobial stewardship?", "options": ["A) It is comprehensive and adequate", "B) It provides limited content on this topic", "C) It focuses too much on stewardship"], "answer": "B"},
                            {"number": 12, "question": "What role can nurse stewardship champions play?", "options": ["A) Prescribe antibiotics independently", "B) Replace pharmacists on stewardship teams", "C) Identify prescribing patterns needing review"], "answer": "C"},
                            {"number": 13, "question": "According to the author, why is community and aged care nursing relevant to stewardship?", "options": ["A) Because these settings have low antibiotic use", "B) Because nurses manage long-term therapy in these settings", "C) Because doctors are not involved in these settings"], "answer": "B"},
                            {"number": 14, "question": "What does the author believe is necessary for stewardship programs to reach their potential?", "options": ["A) Reducing the number of antibiotics available", "B) Recognizing nursing as an equal partner", "C) Removing nurses from stewardship decisions"], "answer": "B"},
                            {"number": 15, "question": "What is the author's main argument in this text?", "options": ["A) Nurses should not be involved in antimicrobial decisions", "B) Antimicrobial stewardship is only a medical responsibility", "C) Nurses have an important but undervalued role in stewardship"], "answer": "C"},
                            {"number": 16, "question": "The phrase 'post-antibiotic era' suggests a future where:", "options": ["A) Better antibiotics will be available", "B) Common infections could be deadly again", "C) Antibiotics will no longer be needed"], "answer": "B"}
                        ]
                    }
                ]
            }
        },
        
        "writing": {
            "letter_type": "referral",
            "task_instructions": "Using the information in the case notes, write a letter of referral to Dr. James Mitchell, Endocrinologist, at Riverside Medical Centre, 45 Park Avenue, Westfield. Your letter should be approximately 180-200 words.",
            "recipient": {
                "name": "Dr. James Mitchell",
                "position": "Endocrinologist",
                "facility": "Riverside Medical Centre",
                "address": "45 Park Avenue, Westfield"
            },
            "case_notes": {
                "patient_name": "Margaret Sullivan",
                "dob": "15/03/1958",
                "age": 66,
                "gender": "Female",
                "occupation": "Retired teacher",
                "presenting_complaint": "Poor glycaemic control despite current treatment",
                "history_present_illness": "Type 2 diabetes diagnosed 8 years ago. Initially managed with diet, metformin added 6 years ago. HbA1c consistently above target (currently 9.2%). Experiencing increased thirst and urination over past 3 months. No ketones detected. Recent unintentional weight loss of 4kg over 2 months.",
                "past_medical_history": ["Hypertension (10 years)", "Hyperlipidaemia", "Osteoarthritis - knees", "Appendectomy 1985"],
                "current_medications": [
                    {"name": "Metformin", "dose": "1g", "frequency": "twice daily"},
                    {"name": "Gliclazide", "dose": "80mg", "frequency": "twice daily"},
                    {"name": "Lisinopril", "dose": "10mg", "frequency": "daily"},
                    {"name": "Atorvastatin", "dose": "20mg", "frequency": "at night"}
                ],
                "allergies": ["Sulfonamides - rash"],
                "social_history": "Lives alone, independent. Non-smoker, occasional alcohol. Daughter visits weekly.",
                "examination": {
                    "general": "Alert, appears well",
                    "weight": "78kg",
                    "height": "165cm",
                    "bmi": "28.6",
                    "bp": "138/82",
                    "foot_exam": "Sensation intact, pulses present, no ulcers"
                },
                "recent_investigations": [
                    {"test": "HbA1c", "result": "9.2%", "date": "02/01/2025"},
                    {"test": "Fasting glucose", "result": "11.8 mmol/L", "date": "02/01/2025"},
                    {"test": "eGFR", "result": "68 mL/min", "date": "02/01/2025"},
                    {"test": "Urine ACR", "result": "5.2 mg/mmol", "date": "02/01/2025"}
                ],
                "irrelevant_details": ["Patient recently returned from holiday in Spain", "Daughter getting married in June", "Patient enjoys gardening"],
                "reason_for_referral": "Specialist review for consideration of insulin therapy or other treatment intensification"
            },
            "key_points_to_include": [
                "Current poor glycaemic control (HbA1c 9.2%)",
                "Duration of diabetes and current treatment",
                "Recent symptoms (thirst, urination, weight loss)",
                "Renal function (mildly reduced eGFR, microalbuminuria)",
                "Sulfonamide allergy",
                "Request for treatment intensification/insulin consideration"
            ],
            "points_to_omit": [
                "Holiday in Spain",
                "Daughter's wedding",
                "Gardening hobby",
                "1985 appendectomy (not relevant)"
            ],
            "sample_answer": """Dear Dr. Mitchell,

Re: Margaret Sullivan, DOB 15/03/1958

I am writing to refer Mrs. Sullivan, a 66-year-old retired teacher, for endocrinology review regarding her poorly controlled Type 2 diabetes.

Mrs. Sullivan was diagnosed with Type 2 diabetes eight years ago. Despite maximum oral therapy with metformin 1g twice daily and gliclazide 80mg twice daily, her glycaemic control remains suboptimal with a recent HbA1c of 9.2%. Over the past three months, she has reported increased thirst and urination, along with unintentional weight loss of 4kg.

Her other medical history includes hypertension and hyperlipidaemia, both currently well controlled. Notably, she has a documented allergy to sulfonamides, which caused a rash.

Recent investigations show a fasting glucose of 11.8 mmol/L and mildly reduced renal function with an eGFR of 68 mL/min and microalbuminuria (urine ACR 5.2 mg/mmol). Foot examination was reassuring with intact sensation and no ulceration.

I would appreciate your review and recommendations for treatment intensification, potentially including insulin therapy.

Yours sincerely,

[Nurse Name]
Registered Nurse"""
        },
        
        "speaking": {
            "role_play_1": {
                "scenario_title": "Post-operative Pain Management",
                "setting": "Surgical ward, day 2 post-operation",
                "candidate_card": {
                    "role": "Registered Nurse",
                    "situation": "Mr. David Chen (65 years old) had a total hip replacement two days ago. He has been reluctant to take his prescribed pain medication and is now experiencing significant pain that is affecting his ability to participate in physiotherapy.",
                    "tasks": [
                        "Explore the patient's concerns about taking pain medication",
                        "Explain the importance of adequate pain control for recovery",
                        "Discuss the pain management options available",
                        "Develop a plan that addresses the patient's concerns"
                    ]
                },
                "interlocutor_card": {
                    "role": "Patient (Mr. David Chen)",
                    "background": "65-year-old retired accountant, 2 days post hip replacement surgery",
                    "concerns": [
                        "Worried about becoming addicted to strong painkillers",
                        "Father had addiction problems",
                        "Believes pain medication should only be taken when absolutely necessary",
                        "Has been trying to 'tough it out'"
                    ],
                    "responses": {
                        "if_asked_about_pain_level": "It's quite bad, especially when I try to move. Maybe 7 out of 10.",
                        "if_asked_about_medication_concerns": "I don't want to end up dependent on these drugs. My father had problems with addiction.",
                        "if_reassured_about_addiction": "Show some relief but still cautious. Ask how you can be sure."
                    }
                },
                "key_communication_points": [
                    "Active listening to patient concerns",
                    "Empathy regarding family history",
                    "Clear explanation of difference between dependence and addiction",
                    "Emphasis on short-term use for recovery",
                    "Collaborative approach to pain management"
                ]
            },
            "role_play_2": {
                "scenario_title": "Discharge Planning for Elderly Patient",
                "setting": "Medical ward, preparing for discharge",
                "candidate_card": {
                    "role": "Registered Nurse",
                    "situation": "Mrs. Rosa Martinez (78 years old) is being discharged after treatment for a urinary tract infection. She lives alone and her daughter, who usually helps, is overseas for a month. She seems anxious about going home.",
                    "tasks": [
                        "Assess the patient's concerns about discharge",
                        "Discuss what support services are available",
                        "Provide education about preventing future infections",
                        "Develop a safe discharge plan"
                    ]
                },
                "interlocutor_card": {
                    "role": "Patient (Mrs. Rosa Martinez)",
                    "background": "78-year-old widow, lives independently, daughter usually visits twice weekly but is currently overseas",
                    "concerns": [
                        "Worried about managing medications correctly",
                        "Uncertain about recognizing if infection returns",
                        "Anxious about being alone at home",
                        "Doesn't want to be a burden"
                    ],
                    "responses": {
                        "if_asked_about_home_situation": "I usually manage fine, but Maria helps me with my tablets and shopping. She's in Argentina for her niece's wedding.",
                        "if_support_services_offered": "Initially reluctant - 'I don't want strangers in my home.' Can be persuaded if nurse explains clearly.",
                        "if_asked_about_symptoms_to_watch": "What should I look out for? I don't want to end up back here."
                    }
                },
                "key_communication_points": [
                    "Respectful assessment of independence",
                    "Sensitivity to not wanting to be a burden",
                    "Clear explanation of warning signs",
                    "Practical suggestions for support",
                    "Written information to reinforce verbal advice"
                ]
            }
        }
    }
}

# Additional exam templates follow similar structure...
# Exams 2-5 would cover different topics:
# Exam 2: Respiratory conditions, oxygen therapy, COPD management
# Exam 3: Mental health, depression assessment, medication compliance  
# Exam 4: Pediatric care, childhood vaccinations, parent education
# Exam 5: Cardiac conditions, chest pain assessment, cardiac rehabilitation
