"""
ProficientHub - B2B Models
Models for Academy/Institution management and exam credits system

SISTEMA DE CRÉDITOS:
- Una academia compra un plan (ej: 5 exámenes IELTS)
- Cada estudiante de la academia tiene acceso al examen contratado
- El estudiante puede usar 1 crédito de 2 formas:
  1. FULL MOCK: Simulacro completo (Reading + Writing + Listening + Speaking)
  2. SECTION MODE: 4 secciones individuales (1 Reading + 1 Writing + 1 Listening + 1 Speaking)
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import uuid4
import enum

from sqlalchemy import (
    String, Text, Integer, Float, Boolean, DateTime,
    ForeignKey, Enum, JSON, Index, CheckConstraint,
    UniqueConstraint, func
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY

from app.db.database import Base
from app.db.models import TimestampMixin, SoftDeleteMixin


# =============================================================================
# ENUMS
# =============================================================================

class AcademyTier(str, enum.Enum):
    """Academy subscription tiers"""
    STARTER = "starter"          # Up to 50 students
    PROFESSIONAL = "professional" # Up to 200 students
    ENTERPRISE = "enterprise"     # Unlimited students


class ExamPlanStatus(str, enum.Enum):
    """Status of an exam plan"""
    ACTIVE = "active"
    EXPIRED = "expired"
    EXHAUSTED = "exhausted"      # All credits used
    CANCELLED = "cancelled"


class MockExamMode(str, enum.Enum):
    """How to use exam credits"""
    FULL_MOCK = "full_mock"      # Complete exam with all 4 sections
    SECTION = "section"          # Individual section


class MockExamStatus(str, enum.Enum):
    """Status of a mock exam session"""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    PAUSED = "paused"
    COMPLETED = "completed"
    EXPIRED = "expired"


class SectionStatus(str, enum.Enum):
    """Status of an individual section within a mock"""
    LOCKED = "locked"            # Not yet available
    AVAILABLE = "available"      # Ready to start
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    SKIPPED = "skipped"


# =============================================================================
# ACADEMY MODEL
# =============================================================================

class Academy(Base, TimestampMixin, SoftDeleteMixin):
    """
    Academy/Institution that purchases exam plans for their students
    """
    __tablename__ = "academies"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid4())
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    
    # Contact info
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    website: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    # Address
    address: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    city: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    country: Mapped[str] = mapped_column(String(100), default="Spain")
    timezone: Mapped[str] = mapped_column(String(50), default="Europe/Madrid")
    
    # Subscription
    tier: Mapped[AcademyTier] = mapped_column(
        Enum(AcademyTier),
        default=AcademyTier.STARTER,
        nullable=False
    )
    max_students: Mapped[int] = mapped_column(Integer, default=50)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Branding
    logo_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    primary_color: Mapped[str] = mapped_column(String(7), default="#6366F1")  # Hex color
    
    # Settings
    settings: Mapped[Dict[str, Any]] = mapped_column(JSONB, default=dict)
    
    # Admin user (owner)
    admin_user_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True
    )
    
    # Relationships
    exam_plans: Mapped[List["AcademyExamPlan"]] = relationship(
        "AcademyExamPlan",
        back_populates="academy",
        lazy="dynamic"
    )
    students: Mapped[List["AcademyStudent"]] = relationship(
        "AcademyStudent",
        back_populates="academy",
        lazy="dynamic"
    )
    
    __table_args__ = (
        Index("idx_academies_active", "is_active"),
        Index("idx_academies_tier", "tier"),
    )

    def __repr__(self) -> str:
        return f"<Academy {self.name}>"


# =============================================================================
# ACADEMY EXAM PLAN MODEL
# =============================================================================

class AcademyExamPlan(Base, TimestampMixin):
    """
    An exam plan purchased by an academy
    
    Example: "English Excellence Academy" buys "5 IELTS Academic exams"
    - Each student can use credits from this plan
    - 1 credit = 1 full mock OR 4 individual sections
    """
    __tablename__ = "academy_exam_plans"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid4())
    )
    academy_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("academies.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # What exam type this plan covers
    exam_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    
    # Plan name (for display)
    plan_name: Mapped[str] = mapped_column(String(255), nullable=False)
    
    # Credits system
    total_credits: Mapped[int] = mapped_column(Integer, nullable=False)
    used_credits: Mapped[int] = mapped_column(Integer, default=0)
    
    @property
    def remaining_credits(self) -> int:
        return self.total_credits - self.used_credits
    
    # Status
    status: Mapped[ExamPlanStatus] = mapped_column(
        Enum(ExamPlanStatus),
        default=ExamPlanStatus.ACTIVE,
        nullable=False,
        index=True
    )
    
    # Validity period
    starts_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=func.now(),
        nullable=False
    )
    expires_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True
    )
    
    # Pricing info (for records)
    price_paid: Mapped[float] = mapped_column(Float, default=0.0)
    currency: Mapped[str] = mapped_column(String(3), default="EUR")
    
    # Settings for this plan
    settings: Mapped[Dict[str, Any]] = mapped_column(
        JSONB,
        default=dict,
        nullable=False
    )
    
    # Relationships
    academy: Mapped["Academy"] = relationship("Academy", back_populates="exam_plans")
    mock_exams: Mapped[List["StudentMockExam"]] = relationship(
        "StudentMockExam",
        back_populates="exam_plan",
        lazy="dynamic"
    )
    
    __table_args__ = (
        Index("idx_exam_plans_academy_type", "academy_id", "exam_type"),
        Index("idx_exam_plans_status", "status"),
        CheckConstraint("used_credits <= total_credits", name="check_credits_not_exceeded"),
    )

    def __repr__(self) -> str:
        return f"<AcademyExamPlan {self.plan_name}: {self.remaining_credits}/{self.total_credits} credits>"


# =============================================================================
# ACADEMY STUDENT MODEL
# =============================================================================

class AcademyStudent(Base, TimestampMixin):
    """
    Links a user to an academy as a student
    """
    __tablename__ = "academy_students"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid4())
    )
    academy_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("academies.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    user_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Student info within academy
    student_code: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    group_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)  # "IELTS Prep 2026"
    
    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    enrolled_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=func.now(),
        nullable=False
    )
    
    # Relationships
    academy: Mapped["Academy"] = relationship("Academy", back_populates="students")
    mock_exams: Mapped[List["StudentMockExam"]] = relationship(
        "StudentMockExam",
        back_populates="student",
        lazy="dynamic"
    )
    
    __table_args__ = (
        UniqueConstraint("academy_id", "user_id", name="uq_academy_student"),
        Index("idx_academy_students_active", "academy_id", "is_active"),
    )

    def __repr__(self) -> str:
        return f"<AcademyStudent {self.user_id} @ {self.academy_id}>"


# =============================================================================
# STUDENT MOCK EXAM MODEL
# =============================================================================

class StudentMockExam(Base, TimestampMixin):
    """
    A mock exam session for a student
    
    USAGE MODES:
    1. FULL_MOCK: Student does all 4 sections in sequence with global timer
       - Uses 1 credit
       - Sections must be done in order
       - Global time limit (e.g., 2h45m for IELTS)
    
    2. SECTION: Student does sections individually
       - Each section costs 0.25 credits
       - 4 sections = 1 credit
       - Can be done in any order, any time
    """
    __tablename__ = "student_mock_exams"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid4())
    )
    
    # Links
    student_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("academy_students.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    exam_plan_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("academy_exam_plans.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    user_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Exam info
    exam_type: Mapped[str] = mapped_column(String(100), nullable=False)
    exam_number: Mapped[int] = mapped_column(Integer, nullable=False)  # 1, 2, 3, 4, 5...
    
    # Mode
    mode: Mapped[MockExamMode] = mapped_column(
        Enum(MockExamMode),
        nullable=False
    )
    
    # Status
    status: Mapped[MockExamStatus] = mapped_column(
        Enum(MockExamStatus),
        default=MockExamStatus.NOT_STARTED,
        nullable=False,
        index=True
    )
    
    # Topic (can be custom or auto-generated)
    topic: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    # Timing (for full mock mode)
    total_time_limit_minutes: Mapped[int] = mapped_column(Integer, default=165)  # IELTS: 2h45m
    time_elapsed_seconds: Mapped[int] = mapped_column(Integer, default=0)
    
    # Timestamps
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Credits used (0.25 per section, max 1.0)
    credits_used: Mapped[float] = mapped_column(Float, default=0.0)
    
    # Overall results (calculated after completion)
    overall_band: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    overall_percentage: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Detailed results per section
    section_results: Mapped[Dict[str, Any]] = mapped_column(
        JSONB,
        default=dict,
        nullable=False
    )
    
    # Relationships
    student: Mapped["AcademyStudent"] = relationship("AcademyStudent", back_populates="mock_exams")
    exam_plan: Mapped["AcademyExamPlan"] = relationship("AcademyExamPlan", back_populates="mock_exams")
    sections: Mapped[List["MockExamSection"]] = relationship(
        "MockExamSection",
        back_populates="mock_exam",
        lazy="selectin",
        order_by="MockExamSection.order"
    )
    
    __table_args__ = (
        Index("idx_mock_exams_student", "student_id", "status"),
        Index("idx_mock_exams_plan", "exam_plan_id"),
        UniqueConstraint("student_id", "exam_plan_id", "exam_number", name="uq_student_exam_number"),
    )

    def __repr__(self) -> str:
        return f"<StudentMockExam #{self.exam_number} ({self.mode.value}) - {self.status.value}>"


# =============================================================================
# MOCK EXAM SECTION MODEL
# =============================================================================

class MockExamSection(Base, TimestampMixin):
    """
    Individual section within a mock exam
    
    Each mock exam has 4 sections:
    - Reading (order=1)
    - Writing (order=2)  
    - Listening (order=3)
    - Speaking (order=4)
    
    For FULL_MOCK mode, sections must be completed in order.
    For SECTION mode, any section can be done independently.
    """
    __tablename__ = "mock_exam_sections"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid4())
    )
    mock_exam_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("student_mock_exams.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Section info
    section_type: Mapped[str] = mapped_column(String(50), nullable=False)  # reading, writing, listening, speaking
    order: Mapped[int] = mapped_column(Integer, nullable=False)  # 1, 2, 3, 4
    
    # Status
    status: Mapped[SectionStatus] = mapped_column(
        Enum(SectionStatus),
        default=SectionStatus.LOCKED,
        nullable=False,
        index=True
    )
    
    # Timing
    time_limit_minutes: Mapped[int] = mapped_column(Integer, nullable=False)
    time_elapsed_seconds: Mapped[int] = mapped_column(Integer, default=0)
    
    # Timestamps
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Generated content (from exam engine)
    exam_session_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("exam_sessions.id", ondelete="SET NULL"),
        nullable=True
    )
    
    # Results
    raw_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    max_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    percentage_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    band_score: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    
    # Detailed feedback
    feedback: Mapped[Dict[str, Any]] = mapped_column(
        JSONB,
        default=dict,
        nullable=False
    )
    
    # Relationships
    mock_exam: Mapped["StudentMockExam"] = relationship("StudentMockExam", back_populates="sections")
    
    __table_args__ = (
        Index("idx_sections_mock", "mock_exam_id", "order"),
        UniqueConstraint("mock_exam_id", "section_type", name="uq_mock_section_type"),
    )

    def __repr__(self) -> str:
        return f"<MockExamSection {self.section_type} ({self.status.value})>"


# =============================================================================
# EXAM TIME CONFIGURATIONS
# =============================================================================

EXAM_TIME_CONFIG = {
    "ielts_academic": {
        "total_time_minutes": 165,  # 2h 45m
        "sections": {
            "listening": {"order": 1, "time_minutes": 40, "includes_transfer": True},
            "reading": {"order": 2, "time_minutes": 60},
            "writing": {"order": 3, "time_minutes": 60},
            "speaking": {"order": 4, "time_minutes": 15, "separate_day": True},
        }
    },
    "ielts_general": {
        "total_time_minutes": 165,
        "sections": {
            "listening": {"order": 1, "time_minutes": 40},
            "reading": {"order": 2, "time_minutes": 60},
            "writing": {"order": 3, "time_minutes": 60},
            "speaking": {"order": 4, "time_minutes": 15},
        }
    },
    "cambridge_b2_first": {
        "total_time_minutes": 209,  # ~3.5h
        "sections": {
            "reading": {"order": 1, "time_minutes": 75},  # Reading & Use of English
            "writing": {"order": 2, "time_minutes": 80},
            "listening": {"order": 3, "time_minutes": 40},
            "speaking": {"order": 4, "time_minutes": 14},
        }
    },
    "cambridge_c1_advanced": {
        "total_time_minutes": 235,
        "sections": {
            "reading": {"order": 1, "time_minutes": 90},
            "writing": {"order": 2, "time_minutes": 90},
            "listening": {"order": 3, "time_minutes": 40},
            "speaking": {"order": 4, "time_minutes": 15},
        }
    },
    "toefl_ibt": {
        "total_time_minutes": 180,  # 3h
        "sections": {
            "reading": {"order": 1, "time_minutes": 54},
            "listening": {"order": 2, "time_minutes": 41},
            "speaking": {"order": 3, "time_minutes": 17},
            "writing": {"order": 4, "time_minutes": 50},
        }
    },
    "pte_academic": {
        "total_time_minutes": 180,
        "sections": {
            "speaking": {"order": 1, "time_minutes": 54},  # Speaking & Writing combined
            "writing": {"order": 2, "time_minutes": 29},
            "reading": {"order": 3, "time_minutes": 29},
            "listening": {"order": 4, "time_minutes": 30},
        }
    },
    "oet_medicine": {
        "total_time_minutes": 165,
        "sections": {
            "listening": {"order": 1, "time_minutes": 45},
            "reading": {"order": 2, "time_minutes": 60},
            "writing": {"order": 3, "time_minutes": 45},
            "speaking": {"order": 4, "time_minutes": 20},
        }
    },
}


def get_exam_time_config(exam_type: str) -> Dict[str, Any]:
    """Get time configuration for an exam type"""
    return EXAM_TIME_CONFIG.get(exam_type, EXAM_TIME_CONFIG["ielts_academic"])
