"""
ProficientHub - OET Exam Models
Complete data models for OET exam generation and evaluation
"""

from datetime import datetime
from typing import Optional, List, Dict, Any, Union
from uuid import uuid4
from enum import Enum
from pydantic import BaseModel, Field, validator

from sqlalchemy import (
    String, Text, Integer, Float, Boolean, DateTime,
    ForeignKey, Enum as SQLEnum, JSON, Index, CheckConstraint,
    UniqueConstraint, func
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY

from app.db.database import Base
from app.db.models import TimestampMixin


# =============================================================================
# ENUMS
# =============================================================================

class OETProfession(str, Enum):
    """Supported OET professions"""
    MEDICINE = "medicine"
    NURSING = "nursing"
    DENTISTRY = "dentistry"
    PHARMACY = "pharmacy"
    PHYSIOTHERAPY = "physiotherapy"
    RADIOGRAPHY = "radiography"
    OCCUPATIONAL_THERAPY = "occupational_therapy"
    DIETETICS = "dietetics"
    PODIATRY = "podiatry"
    SPEECH_PATHOLOGY = "speech_pathology"
    OPTOMETRY = "optometry"
    VETERINARY_SCIENCE = "veterinary_science"


class OETSection(str, Enum):
    """OET exam sections"""
    LISTENING = "listening"
    READING = "reading"
    WRITING = "writing"
    SPEAKING = "speaking"


class OETGrade(str, Enum):
    """OET grading scale (A-E)"""
    A = "A"  # 450-500 (Expert)
    B = "B"  # 350-440 (Very Good)
    C_PLUS = "C+"  # 300-340 (Good)
    C = "C"  # 200-290 (Satisfactory)
    D = "D"  # 100-190 (Developing)
    E = "E"  # 0-90 (Limited)


class ListeningPart(str, Enum):
    """OET Listening parts"""
    PART_A = "part_a"  # Consultation extracts (24 questions)
    PART_B = "part_b"  # Workplace extracts (6 questions)
    PART_C = "part_c"  # Presentation extracts (12 questions)


class ReadingPart(str, Enum):
    """OET Reading parts"""
    PART_A = "part_a"  # Expeditious reading (20 questions)
    PART_B = "part_b"  # Careful reading - short texts (6 questions)
    PART_C = "part_c"  # Careful reading - long texts (16 questions)


class QuestionType(str, Enum):
    """Question types for Listening/Reading"""
    MULTIPLE_CHOICE = "multiple_choice"
    GAP_FILL = "gap_fill"
    MATCHING = "matching"
    TRUE_FALSE = "true_false"
    SHORT_ANSWER = "short_answer"
    NOTE_COMPLETION = "note_completion"
    SENTENCE_COMPLETION = "sentence_completion"
    SUMMARY_COMPLETION = "summary_completion"


class WritingTaskType(str, Enum):
    """OET Writing task types"""
    REFERRAL_LETTER = "referral_letter"
    DISCHARGE_LETTER = "discharge_letter"
    TRANSFER_LETTER = "transfer_letter"
    ADVICE_LETTER = "advice_letter"


class SpeakingScenarioType(str, Enum):
    """OET Speaking scenario types"""
    HISTORY_TAKING = "history_taking"
    EXPLANATION = "explanation"
    COUNSELING = "counseling"
    PATIENT_EDUCATION = "patient_education"
    BREAKING_BAD_NEWS = "breaking_bad_news"
    REASSURANCE = "reassurance"


# =============================================================================
# PYDANTIC SCHEMAS (for API)
# =============================================================================

class AudioSegment(BaseModel):
    """Audio segment for listening section"""
    id: str = Field(default_factory=lambda: str(uuid4()))
    url: str
    duration_seconds: int
    transcript: Optional[str] = None
    speaker_labels: Optional[Dict[str, str]] = None  # {"speaker_1": "Doctor", "speaker_2": "Patient"}


class OETListeningQuestion(BaseModel):
    """Listening question model"""
    id: str = Field(default_factory=lambda: str(uuid4()))
    part: ListeningPart
    question_number: int
    question_type: QuestionType
    question_text: str
    audio_segment_id: str
    audio_timestamp_start: Optional[float] = None  # seconds
    audio_timestamp_end: Optional[float] = None
    options: Optional[List[str]] = None  # For MCQ
    correct_answer: str
    answer_explanation: Optional[str] = None
    max_words: Optional[int] = None  # For gap fill/short answer
    points: int = 1

    # Medical context
    medical_context: Optional[str] = None
    key_vocabulary: Optional[List[str]] = None


class OETReadingQuestion(BaseModel):
    """Reading question model"""
    id: str = Field(default_factory=lambda: str(uuid4()))
    part: ReadingPart
    question_number: int
    question_type: QuestionType
    question_text: str
    passage_id: str
    paragraph_reference: Optional[str] = None  # e.g., "Paragraph C"
    options: Optional[List[str]] = None
    correct_answer: str
    answer_explanation: Optional[str] = None
    points: int = 1

    # For matching questions
    matching_items: Optional[List[str]] = None
    matching_options: Optional[List[str]] = None


class ReadingPassage(BaseModel):
    """Reading passage model"""
    id: str = Field(default_factory=lambda: str(uuid4()))
    part: ReadingPart
    title: str
    content: str
    word_count: int
    source: Optional[str] = None  # e.g., "Adapted from BMJ, 2023"
    medical_specialty: str
    difficulty_level: int = Field(ge=1, le=5)

    # Part A specific
    texts: Optional[List[Dict[str, str]]] = None  # Multiple short texts for Part A

    # Paragraphs labeled for Part C
    paragraphs: Optional[Dict[str, str]] = None  # {"A": "content...", "B": "content..."}


class PatientCaseNotes(BaseModel):
    """Patient case notes for Writing task"""
    patient_name: str
    age: int
    gender: str
    date_of_admission: Optional[str] = None
    date_of_consultation: Optional[str] = None

    # Medical history
    presenting_complaint: str
    history_of_present_illness: str
    past_medical_history: List[str]
    medications: List[Dict[str, str]]  # [{"name": "Metformin", "dose": "500mg", "frequency": "BD"}]
    allergies: List[str]

    # Social history
    social_history: Dict[str, Any]
    family_history: Optional[List[str]] = None

    # Examination findings
    examination_findings: Dict[str, Any]
    vital_signs: Dict[str, str]

    # Investigations
    investigations: List[Dict[str, Any]]

    # Diagnosis and plan
    diagnosis: str
    differential_diagnoses: Optional[List[str]] = None
    treatment_plan: List[str]

    # Discharge/referral specific
    discharge_medications: Optional[List[Dict[str, str]]] = None
    follow_up_instructions: Optional[List[str]] = None
    referral_reason: Optional[str] = None


class OETWritingTask(BaseModel):
    """Writing task model"""
    id: str = Field(default_factory=lambda: str(uuid4()))
    task_type: WritingTaskType
    profession: OETProfession

    # Task instructions
    instructions: str
    recipient: str  # e.g., "Dr. Sarah Mitchell, Cardiologist"
    recipient_institution: str
    purpose: str

    # Case notes
    case_notes: PatientCaseNotes

    # Writing requirements
    word_limit_min: int = 180
    word_limit_max: int = 200
    time_limit_minutes: int = 45

    # Key points that must be included
    required_content_points: List[str]

    # Model answer for reference
    model_answer: Optional[str] = None

    # Evaluation criteria
    evaluation_criteria: Dict[str, List[str]] = Field(default_factory=lambda: {
        "purpose": ["Clear statement of purpose", "Appropriate register"],
        "content": ["All relevant information included", "Appropriate selection from notes"],
        "conciseness": ["No unnecessary information", "Within word limit"],
        "grammar": ["Accurate grammar", "Complex structures used appropriately"],
        "vocabulary": ["Appropriate medical terminology", "Accurate spelling"],
        "organization": ["Logical structure", "Clear paragraphing"],
        "layout": ["Appropriate letter format", "Date, salutation, closing"]
    })


class SpeakingRoleCard(BaseModel):
    """Role card for Speaking role-play"""
    role: str  # "Healthcare Professional" or "Patient/Relative"
    setting: str
    context: str
    tasks: List[str]
    information_to_elicit: Optional[List[str]] = None
    information_to_provide: Optional[Dict[str, str]] = None
    emotional_state: Optional[str] = None
    concerns: Optional[List[str]] = None


class OETSpeakingRolePlay(BaseModel):
    """Speaking role-play model"""
    id: str = Field(default_factory=lambda: str(uuid4()))
    role_play_number: int  # 1 or 2
    scenario_type: SpeakingScenarioType
    profession: OETProfession

    # Scenario details
    title: str
    setting: str  # e.g., "Hospital ward", "GP clinic"
    duration_minutes: int = 5
    preparation_time_minutes: int = 3

    # Role cards
    candidate_card: SpeakingRoleCard
    interlocutor_card: SpeakingRoleCard

    # Interlocutor script/prompts
    interlocutor_prompts: List[Dict[str, str]]

    # Evaluation criteria
    evaluation_criteria: Dict[str, List[str]] = Field(default_factory=lambda: {
        "linguistic_criteria": {
            "intelligibility": ["Clear pronunciation", "Appropriate stress and intonation"],
            "fluency": ["Natural pace", "Minimal hesitation"],
            "appropriateness": ["Suitable register", "Professional language"],
            "resources": ["Range of vocabulary", "Grammatical accuracy"]
        },
        "clinical_communication_criteria": {
            "relationship_building": ["Empathy shown", "Active listening"],
            "understanding": ["Checks patient understanding", "Clarifies as needed"],
            "information_gathering": ["Systematic approach", "Relevant questions"],
            "information_giving": ["Clear explanations", "Appropriate detail"]
        }
    })

    # Sample responses for training
    sample_good_responses: Optional[List[str]] = None


class OETSectionResult(BaseModel):
    """Result for one OET section"""
    section: OETSection
    raw_score: int
    max_score: int
    scaled_score: int  # 0-500
    grade: OETGrade

    # Detailed breakdown
    part_scores: Optional[Dict[str, Dict[str, int]]] = None

    # For Writing/Speaking
    criteria_scores: Optional[Dict[str, int]] = None
    feedback: Optional[Dict[str, str]] = None

    # Time tracking
    time_taken_seconds: int
    time_limit_seconds: int


class OETExamSession(BaseModel):
    """Complete OET exam session"""
    id: str = Field(default_factory=lambda: str(uuid4()))
    user_id: str
    profession: OETProfession

    # Sections
    listening: Optional[Dict[str, Any]] = None
    reading: Optional[Dict[str, Any]] = None
    writing: Optional[Dict[str, Any]] = None
    speaking: Optional[Dict[str, Any]] = None

    # Results
    results: Optional[Dict[OETSection, OETSectionResult]] = None
    overall_grade: Optional[OETGrade] = None

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    # Status
    status: str = "created"  # created, in_progress, completed, expired


# =============================================================================
# SQLALCHEMY MODELS (for persistence)
# =============================================================================

class OETExam(Base, TimestampMixin):
    """Persisted OET exam session"""
    __tablename__ = "oet_exams"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid4())
    )
    user_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    mock_exam_section_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("mock_exam_sections.id", ondelete="SET NULL"),
        nullable=True
    )

    profession: Mapped[str] = mapped_column(
        SQLEnum(OETProfession),
        nullable=False
    )
    section: Mapped[str] = mapped_column(
        SQLEnum(OETSection),
        nullable=False
    )

    # Content (JSON)
    content: Mapped[Dict[str, Any]] = mapped_column(JSONB, nullable=False)

    # Answers submitted
    answers: Mapped[Dict[str, Any]] = mapped_column(JSONB, default=dict)

    # Results
    raw_score: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    max_score: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    scaled_score: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    grade: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)

    detailed_results: Mapped[Dict[str, Any]] = mapped_column(JSONB, default=dict)
    feedback: Mapped[Dict[str, Any]] = mapped_column(JSONB, default=dict)

    # Timing
    time_limit_seconds: Mapped[int] = mapped_column(Integer, nullable=False)
    time_elapsed_seconds: Mapped[int] = mapped_column(Integer, default=0)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Status
    status: Mapped[str] = mapped_column(String(50), default="created", index=True)

    __table_args__ = (
        Index("idx_oet_exams_user_section", "user_id", "section"),
        Index("idx_oet_exams_status", "status"),
    )


class OETContentItem(Base, TimestampMixin):
    """Reusable OET content items (questions, passages, tasks)"""
    __tablename__ = "oet_content_items"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid4())
    )

    section: Mapped[str] = mapped_column(
        SQLEnum(OETSection),
        nullable=False,
        index=True
    )
    content_type: Mapped[str] = mapped_column(String(50), nullable=False)  # question, passage, task, roleplay
    profession: Mapped[str] = mapped_column(
        SQLEnum(OETProfession),
        nullable=False,
        index=True
    )

    # Content data
    content: Mapped[Dict[str, Any]] = mapped_column(JSONB, nullable=False)

    # Metadata
    difficulty_level: Mapped[int] = mapped_column(Integer, default=3)  # 1-5
    medical_specialty: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    tags: Mapped[List[str]] = mapped_column(ARRAY(String), default=list)

    # Usage tracking
    times_used: Mapped[int] = mapped_column(Integer, default=0)
    average_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Quality
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    __table_args__ = (
        Index("idx_oet_content_section_type", "section", "content_type"),
        Index("idx_oet_content_profession", "profession"),
        Index("idx_oet_content_active", "is_active"),
    )


class OETAudioContent(Base, TimestampMixin):
    """Audio content for Listening section"""
    __tablename__ = "oet_audio_content"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid4())
    )

    part: Mapped[str] = mapped_column(String(20), nullable=False)  # part_a, part_b, part_c
    profession: Mapped[str] = mapped_column(
        SQLEnum(OETProfession),
        nullable=False
    )

    # Audio file
    audio_url: Mapped[str] = mapped_column(String(500), nullable=False)
    duration_seconds: Mapped[int] = mapped_column(Integer, nullable=False)

    # Transcript
    transcript: Mapped[str] = mapped_column(Text, nullable=False)
    speaker_labels: Mapped[Dict[str, str]] = mapped_column(JSONB, default=dict)

    # Metadata
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    medical_scenario: Mapped[str] = mapped_column(String(255), nullable=False)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    __table_args__ = (
        Index("idx_oet_audio_part_profession", "part", "profession"),
    )


# =============================================================================
# SCORING CONFIGURATION
# =============================================================================

OET_SCORING_CONFIG = {
    "listening": {
        "total_questions": 42,
        "parts": {
            "part_a": {"questions": 24, "weight": 0.57},
            "part_b": {"questions": 6, "weight": 0.14},
            "part_c": {"questions": 12, "weight": 0.29}
        },
        "time_minutes": 45
    },
    "reading": {
        "total_questions": 42,
        "parts": {
            "part_a": {"questions": 20, "weight": 0.48},
            "part_b": {"questions": 6, "weight": 0.14},
            "part_c": {"questions": 16, "weight": 0.38}
        },
        "time_minutes": 60
    },
    "writing": {
        "criteria": {
            "purpose": {"weight": 0.2, "max_score": 7},
            "content": {"weight": 0.2, "max_score": 7},
            "conciseness_clarity": {"weight": 0.15, "max_score": 7},
            "genre_style": {"weight": 0.15, "max_score": 7},
            "organization": {"weight": 0.15, "max_score": 7},
            "language": {"weight": 0.15, "max_score": 7}
        },
        "time_minutes": 45,
        "word_limit": {"min": 180, "max": 200}
    },
    "speaking": {
        "role_plays": 2,
        "criteria": {
            "linguistic": {
                "intelligibility": {"weight": 0.125, "max_score": 6},
                "fluency": {"weight": 0.125, "max_score": 6},
                "appropriateness": {"weight": 0.125, "max_score": 6},
                "resources": {"weight": 0.125, "max_score": 6}
            },
            "clinical_communication": {
                "relationship_building": {"weight": 0.125, "max_score": 6},
                "understanding": {"weight": 0.125, "max_score": 6},
                "information_gathering_giving": {"weight": 0.125, "max_score": 6},
                "providing_structure": {"weight": 0.125, "max_score": 6}
            }
        },
        "preparation_time_minutes": 3,
        "role_play_time_minutes": 5
    }
}


def raw_to_scaled_score(raw_score: int, max_score: int) -> int:
    """Convert raw score to OET scaled score (0-500)"""
    if max_score == 0:
        return 0
    percentage = (raw_score / max_score) * 100
    # OET uses a complex scaling algorithm, this is a simplified version
    scaled = int((percentage / 100) * 500)
    return min(500, max(0, scaled))


def scaled_score_to_grade(scaled_score: int) -> OETGrade:
    """Convert scaled score to OET grade"""
    if scaled_score >= 450:
        return OETGrade.A
    elif scaled_score >= 350:
        return OETGrade.B
    elif scaled_score >= 300:
        return OETGrade.C_PLUS
    elif scaled_score >= 200:
        return OETGrade.C
    elif scaled_score >= 100:
        return OETGrade.D
    else:
        return OETGrade.E


def get_grade_description(grade: OETGrade) -> Dict[str, str]:
    """Get description for OET grade"""
    descriptions = {
        OETGrade.A: {
            "level": "Expert",
            "description": "Can communicate very fluently and effectively with patients and health professionals using appropriate register, tone and lexis.",
            "cefr": "C2"
        },
        OETGrade.B: {
            "level": "Very Good",
            "description": "Can communicate effectively with patients and health professionals using appropriate register, tone and lexis, with only occasional inaccuracies and hesitations.",
            "cefr": "C1"
        },
        OETGrade.C_PLUS: {
            "level": "Good",
            "description": "Can maintain communication with patients and health professionals using appropriate register and lexis, with some inaccuracies and hesitations which do not impede communication.",
            "cefr": "B2+"
        },
        OETGrade.C: {
            "level": "Satisfactory",
            "description": "Can maintain communication with patients and health professionals, with occasional breakdowns.",
            "cefr": "B2"
        },
        OETGrade.D: {
            "level": "Developing",
            "description": "Can maintain some communication with patients and health professionals, with frequent breakdowns.",
            "cefr": "B1"
        },
        OETGrade.E: {
            "level": "Limited",
            "description": "Has difficulty maintaining communication with patients and health professionals.",
            "cefr": "Below B1"
        }
    }
    return descriptions.get(grade, descriptions[OETGrade.E])
