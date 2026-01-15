"""
OET (Occupational English Test) Official Exam Schema
Based on official OET specifications for healthcare professionals

Total Duration: ~3 hours
Target: Healthcare professionals (12 professions)
Professions: Nursing, Medicine, Dentistry, Pharmacy, Physiotherapy, 
             Occupational Therapy, Optometry, Podiatry, Radiography,
             Speech Pathology, Dietetics, Veterinary Science
"""

from typing import List, Dict, Optional
from pydantic import BaseModel
from enum import Enum
from datetime import datetime

# ==================== ENUMS ====================

class OETProfession(str, Enum):
    NURSING = "nursing"
    MEDICINE = "medicine"
    DENTISTRY = "dentistry"
    PHARMACY = "pharmacy"
    PHYSIOTHERAPY = "physiotherapy"
    OCCUPATIONAL_THERAPY = "occupational_therapy"
    OPTOMETRY = "optometry"
    PODIATRY = "podiatry"
    RADIOGRAPHY = "radiography"
    SPEECH_PATHOLOGY = "speech_pathology"
    DIETETICS = "dietetics"
    VETERINARY_SCIENCE = "veterinary_science"

class OETSection(str, Enum):
    LISTENING = "listening"
    READING = "reading"
    WRITING = "writing"
    SPEAKING = "speaking"

class OETListeningPart(str, Enum):
    PART_A = "part_a"  # Consultation extracts - 24 questions
    PART_B = "part_b"  # Workplace extracts - 6 questions
    PART_C = "part_c"  # Presentation extracts - 12 questions

class OETReadingPart(str, Enum):
    PART_A = "part_a"  # Expeditious reading - 20 questions, 15 min
    PART_B = "part_b"  # Short workplace texts - 6 questions
    PART_C = "part_c"  # Longer professional texts - 16 questions

class QuestionType(str, Enum):
    NOTE_COMPLETION = "note_completion"
    MULTIPLE_CHOICE = "multiple_choice"
    MATCHING = "matching"
    SHORT_ANSWER = "short_answer"
    GAP_FILL = "gap_fill"
    ROLE_PLAY = "role_play"
    LETTER_WRITING = "letter_writing"

class DifficultyLevel(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"

class ValidationStatus(str, Enum):
    DRAFT = "draft"
    AI_REVIEWED_1 = "ai_reviewed_1"
    AI_REVIEWED_2 = "ai_reviewed_2"
    PENDING_HUMAN_REVIEW = "pending_human_review"
    APPROVED = "approved"
    REJECTED = "rejected"

# ==================== OET EXAM STRUCTURE ====================

OET_EXAM_STRUCTURE = {
    "listening": {
        "total_duration_minutes": 45,
        "total_questions": 42,
        "parts": {
            "part_a": {
                "name": "Consultation Extracts",
                "description": "Two healthcare professional-patient consultations",
                "questions": 24,
                "question_type": "note_completion",
                "audio_plays": 1,
                "instructions": "Listen to the consultation and complete the notes using the exact words you hear.",
                "topics": ["patient_history", "symptoms", "diagnosis", "treatment_plan", "medication", "follow_up"]
            },
            "part_b": {
                "name": "Workplace Extracts",
                "description": "Six short workplace audio extracts (staff briefings, handovers, conversations)",
                "questions": 6,
                "question_type": "multiple_choice",
                "options_per_question": 3,
                "audio_plays": 1,
                "instructions": "Listen to the extract and choose the best answer from A, B, or C."
            },
            "part_c": {
                "name": "Presentation Extracts",
                "description": "Two professional presentations/interviews (~5 min each)",
                "questions": 12,
                "questions_per_extract": 6,
                "question_type": "multiple_choice",
                "options_per_question": 3,
                "audio_plays": 1,
                "instructions": "Listen to the presentation and answer the questions."
            }
        }
    },
    "reading": {
        "total_duration_minutes": 60,
        "total_questions": 42,
        "parts": {
            "part_a": {
                "name": "Expeditious Reading",
                "description": "Four short healthcare texts on one medical theme",
                "duration_minutes": 15,
                "questions": 20,
                "texts": 4,
                "question_types": ["matching", "short_answer", "gap_fill"],
                "instructions": "Read the texts quickly and answer using exact words from the texts.",
                "themes": ["patient_safety", "infection_control", "medication_management", "chronic_disease", "mental_health", "emergency_care"]
            },
            "part_b": {
                "name": "Short Workplace Texts",
                "description": "Six short workplace extracts (policies, manuals, notices)",
                "duration_minutes": 45,  # Combined with Part C
                "questions": 6,
                "texts": 6,
                "question_type": "multiple_choice",
                "options_per_question": 3,
                "instructions": "Read each text and choose the best answer."
            },
            "part_c": {
                "name": "Longer Professional Texts",
                "description": "Two detailed professional articles",
                "questions": 16,
                "questions_per_text": 8,
                "texts": 2,
                "question_type": "multiple_choice",
                "options_per_question": 3,
                "instructions": "Read the article and answer the questions."
            }
        }
    },
    "writing": {
        "total_duration_minutes": 45,
        "tasks": 1,
        "word_count": {"min": 180, "max": 200},
        "letter_types": ["referral", "discharge", "transfer"],
        "format": {
            "recipient_address": True,
            "date": True,
            "salutation": "Dear Dr/Mr/Ms [Name],",
            "reference_line": "Re: [Patient Name], DOB [Date]",
            "introduction": "State purpose, patient details, key issue",
            "body": "2-3 paragraphs with relevant history and current status",
            "conclusion": "Request action, polite close",
            "sign_off": "Yours sincerely,",
            "sender_name": True
        },
        "assessment_criteria": [
            {"name": "Purpose", "description": "Clear objective and relevance to task"},
            {"name": "Content", "description": "Appropriate selection and transformation of case notes"},
            {"name": "Conciseness", "description": "Clear and coherent without unnecessary details"},
            {"name": "Genre", "description": "Professional tone and appropriate style"},
            {"name": "Organization", "description": "Logical structure and paragraphing"},
            {"name": "Language", "description": "Grammar, vocabulary range, accuracy"}
        ]
    },
    "speaking": {
        "total_duration_minutes": 20,
        "role_plays": 2,
        "preparation_time_minutes": 3,
        "role_play_duration_minutes": 5,
        "includes_warmup": True,
        "warmup_assessed": False,
        "interlocutor_role": "patient_or_carer",
        "assessment_criteria": [
            {"name": "Intelligibility", "description": "Clear pronunciation and intonation"},
            {"name": "Fluency", "description": "Smooth delivery without excessive hesitation"},
            {"name": "Appropriateness", "description": "Suitable language for healthcare context"},
            {"name": "Resources", "description": "Range of grammar and vocabulary"},
            {"name": "Relationship Building", "description": "Empathy, rapport, patient-centered communication"}
        ]
    }
}

# ==================== MEDICAL TOPICS FOR OET ====================

OET_MEDICAL_TOPICS = {
    "conditions": [
        "diabetes_mellitus", "hypertension", "asthma", "copd", "heart_failure",
        "stroke", "dementia", "depression", "anxiety", "arthritis",
        "osteoporosis", "pneumonia", "urinary_tract_infection", "wound_infection",
        "fractures", "post_operative_care", "chronic_pain", "cancer_care",
        "renal_failure", "liver_disease", "gastrointestinal_disorders"
    ],
    "procedures": [
        "medication_administration", "wound_dressing", "catheter_care",
        "blood_pressure_monitoring", "blood_glucose_monitoring", "injection_technique",
        "patient_transfer", "fall_prevention", "infection_control", "pain_assessment"
    ],
    "settings": [
        "hospital_ward", "emergency_department", "outpatient_clinic",
        "nursing_home", "community_health", "rehabilitation_center",
        "mental_health_unit", "pediatric_ward", "surgical_unit", "icu"
    ],
    "communication_scenarios": [
        "patient_admission", "discharge_planning", "medication_counseling",
        "breaking_bad_news", "obtaining_consent", "handover_report",
        "family_consultation", "multidisciplinary_meeting", "patient_education"
    ]
}

# ==================== DATA MODELS ====================

class AudioScript(BaseModel):
    """Script for listening sections with timestamps"""
    text: str
    speaker: str  # "healthcare_professional", "patient", "narrator"
    timestamp_start: float
    timestamp_end: float

class ListeningQuestion(BaseModel):
    question_id: str
    part: OETListeningPart
    question_number: int
    question_type: QuestionType
    audio_script: List[AudioScript]
    question_text: str
    blank_text: Optional[str] = None  # For note completion
    options: Optional[List[str]] = None  # For multiple choice
    correct_answer: str
    acceptable_answers: List[str] = []  # Alternative correct spellings
    topic: str
    medical_context: str
    difficulty: DifficultyLevel
    validation_status: ValidationStatus = ValidationStatus.DRAFT
    validation_notes: List[str] = []
    created_at: datetime
    reviewed_by: List[str] = []

class ReadingText(BaseModel):
    text_id: str
    title: str
    content: str
    word_count: int
    source_type: str  # "case_study", "guideline", "research", "policy"
    medical_theme: str
    difficulty: DifficultyLevel

class ReadingQuestion(BaseModel):
    question_id: str
    part: OETReadingPart
    question_number: int
    question_type: QuestionType
    text_reference: str  # Which text(s) to use
    question_text: str
    options: Optional[List[str]] = None
    correct_answer: str
    acceptable_answers: List[str] = []
    explanation: str  # For feedback
    topic: str
    difficulty: DifficultyLevel
    validation_status: ValidationStatus = ValidationStatus.DRAFT
    validation_notes: List[str] = []

class CaseNotes(BaseModel):
    """Case notes for writing task"""
    patient_name: str
    date_of_birth: str
    age: int
    gender: str
    occupation: Optional[str]
    admission_date: Optional[str]
    discharge_date: Optional[str]
    presenting_complaint: str
    history_of_present_illness: str
    past_medical_history: List[str]
    medications: List[Dict[str, str]]
    allergies: List[str]
    vital_signs: Dict[str, str]
    examination_findings: str
    investigations: List[Dict[str, str]]
    diagnosis: str
    treatment_given: str
    discharge_plan: Optional[str]
    follow_up: str
    special_instructions: List[str]

class WritingTask(BaseModel):
    task_id: str
    profession: OETProfession
    letter_type: str  # referral, discharge, transfer
    task_instructions: str
    recipient_info: Dict[str, str]
    case_notes: CaseNotes
    sample_answer: str  # High-quality sample for comparison
    key_points_to_include: List[str]
    points_to_omit: List[str]  # Irrelevant details to test discernment
    assessment_focus: List[str]
    topic: str
    difficulty: DifficultyLevel
    validation_status: ValidationStatus = ValidationStatus.DRAFT

class SpeakingRolePlay(BaseModel):
    role_play_id: str
    profession: OETProfession
    scenario_title: str
    setting: str
    candidate_role: str
    interlocutor_role: str
    candidate_card: str  # Instructions for candidate
    interlocutor_card: str  # Instructions for role-player
    key_communication_points: List[str]
    expected_language_functions: List[str]  # e.g., "explaining", "reassuring"
    sample_dialogue: List[Dict[str, str]]
    assessment_criteria_notes: Dict[str, str]
    topic: str
    difficulty: DifficultyLevel
    validation_status: ValidationStatus = ValidationStatus.DRAFT

class OETFullExam(BaseModel):
    exam_id: str
    exam_number: int
    profession: OETProfession
    created_at: datetime
    validation_status: ValidationStatus
    
    # Sections
    listening_part_a: List[ListeningQuestion]
    listening_part_b: List[ListeningQuestion]
    listening_part_c: List[ListeningQuestion]
    
    reading_part_a_texts: List[ReadingText]
    reading_part_a_questions: List[ReadingQuestion]
    reading_part_b_texts: List[ReadingText]
    reading_part_b_questions: List[ReadingQuestion]
    reading_part_c_texts: List[ReadingText]
    reading_part_c_questions: List[ReadingQuestion]
    
    writing_task: WritingTask
    
    speaking_role_play_1: SpeakingRolePlay
    speaking_role_play_2: SpeakingRolePlay
    
    # Metadata for admin review
    topics_covered: List[str]
    difficulty_distribution: Dict[str, int]
    reviewer_notes: List[str] = []
    last_used: Optional[datetime] = None
    times_used: int = 0

# ==================== GRADING SCALES ====================

OET_GRADING = {
    "grades": {
        "A": {"min_score": 450, "max_score": 500, "description": "Expert user"},
        "B": {"min_score": 350, "max_score": 449, "description": "Very good user"},
        "C+": {"min_score": 300, "max_score": 349, "description": "Good user"},
        "C": {"min_score": 200, "max_score": 299, "description": "Competent user"},
        "D": {"min_score": 100, "max_score": 199, "description": "Modest user"},
        "E": {"min_score": 0, "max_score": 99, "description": "Basic user"}
    },
    "passing_grade": "B",
    "passing_score": 350,
    "listening_questions": 42,
    "reading_questions": 42
}
