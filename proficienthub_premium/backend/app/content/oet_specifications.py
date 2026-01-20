"""
OET (Occupational English Test) Complete Specifications
========================================================
Official format specifications for OET exam generation.
Covers all 12 healthcare professions with authentic formats.
"""

from enum import Enum
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import timedelta


class OETHealthcareProfession(str, Enum):
    """12 Official OET Healthcare Professions"""
    DENTISTRY = "dentistry"
    DIETETICS = "dietetics"
    MEDICINE = "medicine"
    NURSING = "nursing"
    OCCUPATIONAL_THERAPY = "occupational_therapy"
    OPTOMETRY = "optometry"
    PHARMACY = "pharmacy"
    PHYSIOTHERAPY = "physiotherapy"
    PODIATRY = "podiatry"
    RADIOGRAPHY = "radiography"
    SPEECH_PATHOLOGY = "speech_pathology"
    VETERINARY_SCIENCE = "veterinary_science"


class OETSection(str, Enum):
    """OET Test Sections"""
    LISTENING = "listening"
    READING = "reading"
    WRITING = "writing"
    SPEAKING = "speaking"


class OETBandScore(str, Enum):
    """OET Band Score Scale (A-E)"""
    A = "A"      # 450-500 - Very high
    B = "B"      # 350-440 - High
    C_PLUS = "C+"  # 300-340 - Good
    C = "C"      # 200-290 - Satisfactory
    D = "D"      # 100-190 - Below satisfactory
    E = "E"      # 0-90 - Basic


@dataclass
class OETListeningSpec:
    """OET Listening Test Specifications"""

    total_duration: timedelta = field(default_factory=lambda: timedelta(minutes=45))
    total_questions: int = 42

    # Part A: Consultation Extracts (Healthcare-specific)
    part_a_extracts: int = 2
    part_a_questions_per_extract: int = 12
    part_a_total_questions: int = 24
    part_a_question_type: str = "note_completion"
    part_a_description: str = "Healthcare professional-patient consultations"
    part_a_audio_plays: int = 1  # Audio played ONCE only

    # Part B: Short Workplace Extracts (Generic healthcare)
    part_b_extracts: int = 6
    part_b_questions_per_extract: int = 1
    part_b_total_questions: int = 6
    part_b_question_type: str = "multiple_choice"
    part_b_options: int = 3  # A, B, C
    part_b_description: str = "Short workplace extracts from healthcare settings"
    part_b_audio_plays: int = 1

    # Part C: Presentation/Interview Extracts (Generic healthcare)
    part_c_extracts: int = 2
    part_c_questions_per_extract: int = 6
    part_c_total_questions: int = 12
    part_c_question_type: str = "multiple_choice"
    part_c_options: int = 4  # A, B, C, D
    part_c_description: str = "Presentations and interviews on healthcare topics"
    part_c_audio_plays: int = 1

    # Scoring
    marks_per_question: int = 1
    total_marks: int = 42


@dataclass
class OETReadingSpec:
    """OET Reading Test Specifications"""

    total_duration: timedelta = field(default_factory=lambda: timedelta(minutes=60))
    total_questions: int = 42

    # Part A: Expeditious Reading (Skimming/Scanning)
    part_a_texts: int = 4
    part_a_text_length_words: tuple = (550, 700)  # Per text
    part_a_questions: int = 20
    part_a_time_limit: timedelta = field(default_factory=lambda: timedelta(minutes=15))
    part_a_question_types: List[str] = field(default_factory=lambda: [
        "matching_information",
        "sentence_completion"
    ])
    part_a_description: str = "Quick reading to locate specific information across multiple texts"

    # Part B: Careful Reading
    part_b_texts: int = 2
    part_b_text_length_words: tuple = (500, 800)  # Per text
    part_b_questions: int = 22
    part_b_time_limit: timedelta = field(default_factory=lambda: timedelta(minutes=45))
    part_b_question_types: List[str] = field(default_factory=lambda: [
        "multiple_choice",
        "matching",
        "short_answer"
    ])
    part_b_description: str = "Detailed comprehension of healthcare texts"

    # Text Types
    text_types: List[str] = field(default_factory=lambda: [
        "clinical_guidelines",
        "patient_information_leaflets",
        "hospital_policies",
        "medical_journal_extracts",
        "health_promotion_materials",
        "professional_development_articles"
    ])

    # Scoring
    marks_per_question: int = 1
    total_marks: int = 42


@dataclass
class OETWritingSpec:
    """OET Writing Test Specifications"""

    total_duration: timedelta = field(default_factory=lambda: timedelta(minutes=45))
    task_type: str = "letter"
    word_count: tuple = (180, 200)  # Minimum-Maximum

    # Letter Types by Profession
    letter_types: Dict[str, List[str]] = field(default_factory=lambda: {
        "medicine": ["referral", "discharge", "transfer"],
        "nursing": ["referral", "discharge", "transfer", "handover"],
        "dentistry": ["referral", "information", "advice"],
        "pharmacy": ["medication_review", "advice", "referral"],
        "physiotherapy": ["referral", "discharge", "progress_report"],
        "occupational_therapy": ["referral", "assessment_report", "discharge"],
        "dietetics": ["referral", "dietary_advice", "progress_report"],
        "optometry": ["referral", "information", "advice"],
        "podiatry": ["referral", "treatment_report", "advice"],
        "radiography": ["referral", "report", "information"],
        "speech_pathology": ["referral", "assessment_report", "progress_report"],
        "veterinary_science": ["referral", "treatment_report", "advice"]
    })

    # Recipients
    common_recipients: List[str] = field(default_factory=lambda: [
        "general_practitioner",
        "specialist",
        "patient",
        "carer_family",
        "healthcare_team_member",
        "social_worker",
        "allied_health_professional"
    ])

    # Assessment Criteria (6 criteria, each 0-7 scale)
    assessment_criteria: Dict[str, str] = field(default_factory=lambda: {
        "overall_task_fulfilment": "Does the letter achieve its purpose?",
        "appropriateness_of_language": "Is register and tone appropriate?",
        "comprehension_of_stimulus": "Are case notes accurately interpreted?",
        "linguistic_features_vocabulary": "Is vocabulary accurate and appropriate?",
        "linguistic_features_grammar": "Are grammar structures used correctly?",
        "presentation": "Is the letter organized and formatted correctly?"
    })

    # Format Requirements
    required_elements: List[str] = field(default_factory=lambda: [
        "date",
        "salutation",
        "patient_identification",
        "purpose_statement",
        "relevant_history",
        "current_condition",
        "treatment_recommendations",
        "closing"
    ])


@dataclass
class OETSpeakingSpec:
    """OET Speaking Test Specifications"""

    total_duration: timedelta = field(default_factory=lambda: timedelta(minutes=20))
    role_plays: int = 2
    preparation_time_per_roleplay: timedelta = field(default_factory=lambda: timedelta(minutes=3))
    roleplay_duration: timedelta = field(default_factory=lambda: timedelta(minutes=5))

    # Role-play Structure
    candidate_role: str = "healthcare_professional"
    interlocutor_role: str = "patient_or_carer"

    # Assessment Criteria (9 criteria)
    assessment_criteria: Dict[str, str] = field(default_factory=lambda: {
        "intelligibility": "Can the candidate be understood?",
        "fluency": "Is speech smooth and natural?",
        "appropriateness_of_language": "Is vocabulary appropriate for healthcare?",
        "resources_of_grammar": "Are grammar structures used effectively?",
        "expression_of_ideas": "Are ideas expressed clearly?",
        "relationship_building": "Does candidate establish rapport?",
        "understanding_patients_perspective": "Does candidate show empathy?",
        "providing_information": "Is information given clearly?",
        "information_gathering": "Does candidate ask appropriate questions?"
    })

    # Scenario Types
    scenario_types: List[str] = field(default_factory=lambda: [
        "explanation_of_diagnosis",
        "treatment_discussion",
        "lifestyle_advice",
        "medication_counseling",
        "breaking_bad_news",
        "addressing_concerns",
        "discharge_instructions",
        "consent_discussion",
        "referral_discussion",
        "follow_up_appointment"
    ])


@dataclass
class OETProfessionContext:
    """Profession-specific context for OET content generation"""

    profession: OETHealthcareProfession
    common_conditions: List[str]
    common_procedures: List[str]
    typical_settings: List[str]
    key_terminology: List[str]
    common_medications: List[str]
    typical_patient_demographics: List[str]


# Profession-specific contexts
OET_PROFESSION_CONTEXTS: Dict[OETHealthcareProfession, OETProfessionContext] = {

    OETHealthcareProfession.MEDICINE: OETProfessionContext(
        profession=OETHealthcareProfession.MEDICINE,
        common_conditions=[
            "type_2_diabetes", "hypertension", "coronary_artery_disease",
            "chronic_obstructive_pulmonary_disease", "asthma", "pneumonia",
            "urinary_tract_infection", "gastroesophageal_reflux_disease",
            "depression", "anxiety", "osteoarthritis", "lower_back_pain",
            "migraine", "hypothyroidism", "anaemia", "chronic_kidney_disease"
        ],
        common_procedures=[
            "physical_examination", "blood_pressure_measurement",
            "blood_test_ordering", "ecg_interpretation", "chest_xray_review",
            "medication_prescription", "referral_to_specialist",
            "vaccination_administration", "wound_assessment", "spirometry"
        ],
        typical_settings=[
            "general_practice", "hospital_ward", "emergency_department",
            "outpatient_clinic", "intensive_care_unit", "rehabilitation_unit"
        ],
        key_terminology=[
            "diagnosis", "prognosis", "differential_diagnosis", "etiology",
            "pathophysiology", "comorbidity", "contraindication", "adverse_effect",
            "therapeutic_intervention", "clinical_presentation", "symptomatology"
        ],
        common_medications=[
            "metformin", "lisinopril", "amlodipine", "atorvastatin",
            "omeprazole", "paracetamol", "ibuprofen", "amoxicillin",
            "salbutamol", "prednisolone", "levothyroxine", "aspirin"
        ],
        typical_patient_demographics=[
            "elderly_with_multiple_comorbidities", "middle_aged_chronic_disease",
            "young_adult_acute_illness", "pediatric", "pregnant_women"
        ]
    ),

    OETHealthcareProfession.NURSING: OETProfessionContext(
        profession=OETHealthcareProfession.NURSING,
        common_conditions=[
            "post_operative_care", "wound_infection", "pressure_ulcers",
            "falls_risk", "dehydration", "malnutrition", "confusion",
            "pain_management", "mobility_issues", "incontinence",
            "medication_non_compliance", "anxiety_in_hospital"
        ],
        common_procedures=[
            "vital_signs_monitoring", "medication_administration",
            "wound_dressing", "catheter_care", "nasogastric_tube_care",
            "patient_positioning", "fall_prevention_assessment",
            "pain_assessment", "discharge_planning", "patient_education",
            "handover_report", "documentation"
        ],
        typical_settings=[
            "medical_ward", "surgical_ward", "aged_care_facility",
            "community_nursing", "emergency_department", "intensive_care"
        ],
        key_terminology=[
            "nursing_care_plan", "patient_assessment", "clinical_observations",
            "handover", "escalation", "deterioration", "intervention",
            "nursing_diagnosis", "patient_outcomes", "care_coordination"
        ],
        common_medications=[
            "paracetamol", "morphine", "enoxaparin", "insulin",
            "antibiotics", "antiemetics", "laxatives", "diuretics",
            "antihypertensives", "bronchodilators"
        ],
        typical_patient_demographics=[
            "post_surgical_patients", "elderly_medical_patients",
            "chronic_disease_management", "palliative_care_patients"
        ]
    ),

    OETHealthcareProfession.PHARMACY: OETProfessionContext(
        profession=OETHealthcareProfession.PHARMACY,
        common_conditions=[
            "medication_interactions", "adverse_drug_reactions",
            "polypharmacy", "non_adherence", "therapeutic_drug_monitoring",
            "chronic_disease_medication_management", "pain_management",
            "anticoagulation_therapy", "diabetes_management"
        ],
        common_procedures=[
            "medication_review", "prescription_verification",
            "patient_counseling", "dose_calculation", "drug_interaction_check",
            "therapeutic_substitution", "compounding", "vaccination",
            "medication_reconciliation", "adverse_event_reporting"
        ],
        typical_settings=[
            "community_pharmacy", "hospital_pharmacy", "clinical_ward",
            "outpatient_dispensary", "oncology_pharmacy"
        ],
        key_terminology=[
            "pharmacokinetics", "pharmacodynamics", "bioavailability",
            "half_life", "drug_interaction", "contraindication",
            "therapeutic_range", "dose_titration", "formulation",
            "generic_substitution", "medication_adherence"
        ],
        common_medications=[
            "warfarin", "metformin", "statins", "ace_inhibitors",
            "proton_pump_inhibitors", "nsaids", "opioids", "antibiotics",
            "antidepressants", "antipsychotics", "chemotherapy_agents"
        ],
        typical_patient_demographics=[
            "elderly_polypharmacy", "chronic_disease_patients",
            "oncology_patients", "transplant_patients"
        ]
    ),

    OETHealthcareProfession.DENTISTRY: OETProfessionContext(
        profession=OETHealthcareProfession.DENTISTRY,
        common_conditions=[
            "dental_caries", "periodontal_disease", "gingivitis",
            "tooth_abscess", "impacted_wisdom_teeth", "malocclusion",
            "temporomandibular_disorder", "oral_cancer_screening",
            "dental_trauma", "tooth_sensitivity", "bruxism"
        ],
        common_procedures=[
            "dental_examination", "scaling_and_cleaning", "filling",
            "root_canal_treatment", "tooth_extraction", "crown_preparation",
            "dental_xray", "oral_hygiene_instruction", "local_anaesthesia",
            "denture_fitting", "orthodontic_assessment"
        ],
        typical_settings=[
            "dental_clinic", "hospital_dental_department",
            "community_dental_service", "orthodontic_practice"
        ],
        key_terminology=[
            "caries", "periodontitis", "occlusion", "pulpitis",
            "periapical", "restorative", "endodontic", "prosthodontic",
            "radiograph", "prophylaxis", "calculus"
        ],
        common_medications=[
            "lidocaine", "articaine", "amoxicillin", "metronidazole",
            "ibuprofen", "chlorhexidine", "fluoride"
        ],
        typical_patient_demographics=[
            "routine_check_up_adults", "pediatric_dentistry",
            "elderly_denture_wearers", "emergency_dental_patients"
        ]
    ),

    OETHealthcareProfession.PHYSIOTHERAPY: OETProfessionContext(
        profession=OETHealthcareProfession.PHYSIOTHERAPY,
        common_conditions=[
            "lower_back_pain", "neck_pain", "shoulder_impingement",
            "knee_osteoarthritis", "post_surgical_rehabilitation",
            "stroke_rehabilitation", "sports_injuries", "ankle_sprain",
            "frozen_shoulder", "carpal_tunnel_syndrome", "sciatica",
            "balance_disorders", "respiratory_conditions"
        ],
        common_procedures=[
            "manual_therapy", "exercise_prescription", "electrotherapy",
            "gait_assessment", "range_of_motion_assessment",
            "strength_testing", "balance_training", "hydrotherapy",
            "respiratory_physiotherapy", "postural_assessment",
            "ergonomic_advice", "home_exercise_program"
        ],
        typical_settings=[
            "private_practice", "hospital_outpatients", "rehabilitation_unit",
            "sports_clinic", "aged_care_facility", "community_health"
        ],
        key_terminology=[
            "range_of_motion", "muscle_strength", "proprioception",
            "gait_pattern", "weight_bearing", "mobilisation", "manipulation",
            "therapeutic_exercise", "functional_capacity", "rehabilitation"
        ],
        common_medications=[
            "nsaids", "muscle_relaxants", "analgesics", "corticosteroid_injections"
        ],
        typical_patient_demographics=[
            "sports_injury_patients", "post_operative_orthopaedic",
            "elderly_mobility_issues", "neurological_rehabilitation"
        ]
    ),

    OETHealthcareProfession.DIETETICS: OETProfessionContext(
        profession=OETHealthcareProfession.DIETETICS,
        common_conditions=[
            "type_2_diabetes", "obesity", "malnutrition", "coeliac_disease",
            "food_allergies", "irritable_bowel_syndrome", "renal_disease",
            "eating_disorders", "dysphagia", "cardiovascular_disease",
            "oncology_nutrition_support", "enteral_feeding"
        ],
        common_procedures=[
            "nutritional_assessment", "dietary_history_taking",
            "meal_planning", "calorie_counting", "bmi_calculation",
            "enteral_feeding_management", "dietary_counseling",
            "weight_management_program", "food_allergy_testing_referral"
        ],
        typical_settings=[
            "hospital_inpatient", "outpatient_clinic", "community_health",
            "private_practice", "aged_care", "renal_unit"
        ],
        key_terminology=[
            "macronutrients", "micronutrients", "glycaemic_index",
            "basal_metabolic_rate", "enteral_nutrition", "parenteral_nutrition",
            "dietary_reference_intake", "malabsorption", "anthropometry"
        ],
        common_medications=[
            "oral_nutritional_supplements", "vitamin_supplements",
            "iron_supplements", "laxatives", "antiemetics"
        ],
        typical_patient_demographics=[
            "diabetic_patients", "obese_patients", "elderly_malnourished",
            "oncology_patients", "renal_patients"
        ]
    ),

    OETHealthcareProfession.OCCUPATIONAL_THERAPY: OETProfessionContext(
        profession=OETHealthcareProfession.OCCUPATIONAL_THERAPY,
        common_conditions=[
            "stroke", "traumatic_brain_injury", "dementia", "arthritis",
            "hand_injuries", "mental_health_conditions", "autism_spectrum",
            "developmental_delay", "spinal_cord_injury", "parkinsons_disease",
            "multiple_sclerosis", "cerebral_palsy"
        ],
        common_procedures=[
            "functional_assessment", "activities_of_daily_living_training",
            "home_assessment", "equipment_prescription", "splinting",
            "cognitive_rehabilitation", "sensory_integration_therapy",
            "workplace_assessment", "driving_assessment", "hand_therapy"
        ],
        typical_settings=[
            "hospital_inpatient", "rehabilitation_unit", "community_health",
            "mental_health_services", "paediatric_services", "aged_care"
        ],
        key_terminology=[
            "occupational_performance", "activities_of_daily_living",
            "instrumental_activities", "adaptive_equipment", "splint",
            "environmental_modification", "cognitive_function", "sensory_processing"
        ],
        common_medications=[],  # OTs don't prescribe but need awareness
        typical_patient_demographics=[
            "stroke_rehabilitation", "elderly_community_dwelling",
            "paediatric_developmental", "mental_health_recovery"
        ]
    ),

    OETHealthcareProfession.OPTOMETRY: OETProfessionContext(
        profession=OETHealthcareProfession.OPTOMETRY,
        common_conditions=[
            "myopia", "hyperopia", "astigmatism", "presbyopia",
            "glaucoma", "cataracts", "macular_degeneration", "diabetic_retinopathy",
            "dry_eye_syndrome", "conjunctivitis", "blepharitis"
        ],
        common_procedures=[
            "visual_acuity_test", "refraction", "tonometry",
            "fundoscopy", "slit_lamp_examination", "visual_field_test",
            "contact_lens_fitting", "spectacle_prescription",
            "colour_vision_testing", "binocular_vision_assessment"
        ],
        typical_settings=[
            "optometry_practice", "hospital_eye_clinic",
            "community_screening", "low_vision_clinic"
        ],
        key_terminology=[
            "visual_acuity", "intraocular_pressure", "refractive_error",
            "accommodation", "convergence", "fundus", "cornea", "retina",
            "optic_nerve", "visual_field", "dioptre"
        ],
        common_medications=[
            "artificial_tears", "antibiotic_eye_drops",
            "antihistamine_eye_drops", "glaucoma_drops"
        ],
        typical_patient_demographics=[
            "routine_eye_examination", "elderly_vision_changes",
            "diabetic_screening", "paediatric_vision"
        ]
    ),

    OETHealthcareProfession.PODIATRY: OETProfessionContext(
        profession=OETHealthcareProfession.PODIATRY,
        common_conditions=[
            "diabetic_foot", "plantar_fasciitis", "ingrown_toenail",
            "bunion", "callus_corn", "fungal_nail_infection", "heel_pain",
            "flat_feet", "foot_ulcers", "peripheral_vascular_disease",
            "neuropathy", "gout_foot"
        ],
        common_procedures=[
            "foot_assessment", "nail_care", "debridement",
            "orthotic_prescription", "wound_dressing", "gait_analysis",
            "footwear_assessment", "nail_surgery", "biomechanical_assessment",
            "vascular_assessment", "neurological_assessment"
        ],
        typical_settings=[
            "private_practice", "hospital_podiatry", "diabetic_foot_clinic",
            "community_health", "aged_care"
        ],
        key_terminology=[
            "hallux_valgus", "onychocryptosis", "hyperkeratosis",
            "neuropathy", "ischaemia", "debridement", "orthosis",
            "plantar", "dorsal", "metatarsal", "phalanx"
        ],
        common_medications=[
            "antifungal_agents", "topical_antibiotics", "local_anaesthetics"
        ],
        typical_patient_demographics=[
            "diabetic_patients", "elderly_nail_care",
            "sports_related_injuries", "vascular_patients"
        ]
    ),

    OETHealthcareProfession.RADIOGRAPHY: OETProfessionContext(
        profession=OETHealthcareProfession.RADIOGRAPHY,
        common_conditions=[
            "fractures", "chest_pathology", "abdominal_pathology",
            "tumours", "stroke", "cardiac_conditions", "spinal_pathology",
            "joint_pathology", "screening_mammography"
        ],
        common_procedures=[
            "plain_radiography", "ct_scan", "mri_scan", "ultrasound",
            "mammography", "fluoroscopy", "contrast_studies",
            "interventional_procedures", "radiation_therapy",
            "patient_positioning", "image_quality_assessment"
        ],
        typical_settings=[
            "hospital_radiology", "private_imaging_centre",
            "emergency_department", "oncology_department"
        ],
        key_terminology=[
            "radiograph", "contrast_medium", "radiation_dose",
            "positioning", "projection", "artefact", "attenuation",
            "tomography", "resolution", "exposure"
        ],
        common_medications=[
            "contrast_agents", "sedation", "antiemetics"
        ],
        typical_patient_demographics=[
            "trauma_patients", "oncology_patients",
            "screening_patients", "emergency_presentations"
        ]
    ),

    OETHealthcareProfession.SPEECH_PATHOLOGY: OETProfessionContext(
        profession=OETHealthcareProfession.SPEECH_PATHOLOGY,
        common_conditions=[
            "dysphagia", "aphasia", "dysarthria", "voice_disorders",
            "stuttering", "language_delay", "articulation_disorders",
            "hearing_impairment_related", "dementia_communication",
            "autism_communication", "laryngectomy"
        ],
        common_procedures=[
            "swallowing_assessment", "language_assessment",
            "articulation_assessment", "voice_assessment",
            "modified_barium_swallow", "fibre_optic_endoscopy",
            "augmentative_communication_assessment", "therapy_session",
            "dysphagia_management", "communication_strategies"
        ],
        typical_settings=[
            "hospital_acute", "rehabilitation_unit", "community_health",
            "paediatric_services", "aged_care", "private_practice"
        ],
        key_terminology=[
            "dysphagia", "aspiration", "aphasia", "dysarthria",
            "phonation", "articulation", "fluency", "pragmatics",
            "augmentative_alternative_communication", "modified_diet"
        ],
        common_medications=[],  # Awareness needed for dysphagia
        typical_patient_demographics=[
            "stroke_patients", "head_and_neck_cancer",
            "paediatric_developmental", "neurological_conditions"
        ]
    ),

    OETHealthcareProfession.VETERINARY_SCIENCE: OETProfessionContext(
        profession=OETHealthcareProfession.VETERINARY_SCIENCE,
        common_conditions=[
            "vaccination", "desexing", "dental_disease", "skin_conditions",
            "gastrointestinal_disorders", "orthopaedic_conditions",
            "respiratory_infections", "parasitic_infections", "diabetes",
            "kidney_disease", "cancer", "trauma"
        ],
        common_procedures=[
            "physical_examination", "vaccination", "surgery",
            "dental_procedures", "blood_tests", "imaging",
            "anaesthesia", "euthanasia_counselling", "microchipping",
            "parasite_treatment", "wound_management"
        ],
        typical_settings=[
            "small_animal_clinic", "mixed_practice", "emergency_clinic",
            "specialist_referral", "rural_practice"
        ],
        key_terminology=[
            "species_specific_terms", "vaccination_protocol",
            "anaesthesia", "analgesia", "zoonotic", "prognosis",
            "palliative_care", "euthanasia"
        ],
        common_medications=[
            "antibiotics", "nsaids", "antiparasitics", "anaesthetics",
            "vaccines", "insulin", "corticosteroids"
        ],
        typical_patient_demographics=[
            "dogs", "cats", "rabbits", "birds",
            "farm_animals", "exotic_pets"
        ]
    )
}


@dataclass
class OETExamSpecification:
    """Complete OET Exam Specification"""

    exam_name: str = "Occupational English Test"
    exam_code: str = "OET"
    version: str = "2.0"

    # Overall Structure
    total_duration: timedelta = field(default_factory=lambda: timedelta(minutes=170))
    sections: int = 4

    # Section Specifications
    listening: OETListeningSpec = field(default_factory=OETListeningSpec)
    reading: OETReadingSpec = field(default_factory=OETReadingSpec)
    writing: OETWritingSpec = field(default_factory=OETWritingSpec)
    speaking: OETSpeakingSpec = field(default_factory=OETSpeakingSpec)

    # Available Professions
    professions: List[OETHealthcareProfession] = field(
        default_factory=lambda: list(OETHealthcareProfession)
    )

    # Scoring System
    scoring_scale: str = "A-E"
    minimum_passing_score: str = "B"  # Most regulatory bodies require B
    score_validity_years: int = 2

    # Registration Requirements
    accepted_score_for_registration: Dict[str, str] = field(default_factory=lambda: {
        "australia_nursing": "B",
        "australia_medicine": "B",
        "uk_nursing": "B",
        "uk_medicine": "B",
        "ireland_nursing": "B",
        "new_zealand_nursing": "B",
        "dubai_healthcare": "B",
        "singapore_nursing": "C+"
    })


# Singleton instance
OET_EXAM_SPEC = OETExamSpecification()


def get_profession_context(profession: OETHealthcareProfession) -> OETProfessionContext:
    """Get profession-specific context for content generation"""
    return OET_PROFESSION_CONTEXTS[profession]


def get_writing_letter_types(profession: OETHealthcareProfession) -> List[str]:
    """Get valid letter types for a profession"""
    return OET_EXAM_SPEC.writing.letter_types.get(
        profession.value,
        ["referral", "discharge", "advice"]
    )
