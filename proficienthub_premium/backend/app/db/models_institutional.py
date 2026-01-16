"""
ProficientHub - Institutional Configuration Models

Complete configuration system for academies including:
- Exam selection (1, 2, 3, or all exams)
- Mock exam plans (5, 10, 20, 40, 60, 100 per student)
- AI Tutor credit plans
- Volume-based pricing
- White-label settings
- Gamification options
- Speaking practice matching
- Video class integration (Zoom)
- Configurable commissions
"""

import uuid
from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum
from typing import Any, Dict, List, Optional

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum as SQLEnum,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    Index,
)
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import relationship

from app.db.database import Base


# =============================================================================
# ENUMS
# =============================================================================

class MockExamPlan(str, Enum):
    """Available mock exam plans per student."""
    PLAN_5 = "5"
    PLAN_10 = "10"
    PLAN_20 = "20"
    PLAN_40 = "40"
    PLAN_60 = "60"
    PLAN_100 = "100"


class AITutorPlan(str, Enum):
    """AI Tutor credit plans."""
    NONE = "none"
    BASIC = "basic"           # 50 AI credits/month
    STANDARD = "standard"     # 200 AI credits/month
    PREMIUM = "premium"       # 500 AI credits/month
    UNLIMITED = "unlimited"   # Unlimited AI credits


class SpeakingMatchStatus(str, Enum):
    """Status for speaking practice matching."""
    AVAILABLE = "available"
    SEARCHING = "searching"
    MATCHED = "matched"
    IN_SESSION = "in_session"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class VideoSessionStatus(str, Enum):
    """Status for video sessions."""
    SCHEDULED = "scheduled"
    WAITING = "waiting"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"


# =============================================================================
# PRICING CONFIGURATION (Volume-based)
# =============================================================================

# Base prices for mock exam plans (per student)
MOCK_EXAM_PLAN_PRICING = {
    MockExamPlan.PLAN_5: {
        "base_price": Decimal("15.00"),
        "description": "5 Full Mock Exams per student",
        "includes_sections": True,  # Can also use as 20 individual sections
    },
    MockExamPlan.PLAN_10: {
        "base_price": Decimal("25.00"),
        "description": "10 Full Mock Exams per student",
        "includes_sections": True,
    },
    MockExamPlan.PLAN_20: {
        "base_price": Decimal("45.00"),
        "description": "20 Full Mock Exams per student",
        "includes_sections": True,
    },
    MockExamPlan.PLAN_40: {
        "base_price": Decimal("80.00"),
        "description": "40 Full Mock Exams per student",
        "includes_sections": True,
    },
    MockExamPlan.PLAN_60: {
        "base_price": Decimal("110.00"),
        "description": "60 Full Mock Exams per student",
        "includes_sections": True,
    },
    MockExamPlan.PLAN_100: {
        "base_price": Decimal("160.00"),
        "description": "100 Full Mock Exams per student",
        "includes_sections": True,
    },
}

# Volume discounts based on number of students
VOLUME_DISCOUNT_TIERS = [
    {"min_students": 1, "max_students": 49, "discount_percent": Decimal("0")},
    {"min_students": 50, "max_students": 99, "discount_percent": Decimal("5")},
    {"min_students": 100, "max_students": 249, "discount_percent": Decimal("10")},
    {"min_students": 250, "max_students": 499, "discount_percent": Decimal("15")},
    {"min_students": 500, "max_students": 999, "discount_percent": Decimal("20")},
    {"min_students": 1000, "max_students": 2499, "discount_percent": Decimal("25")},
    {"min_students": 2500, "max_students": 4999, "discount_percent": Decimal("30")},
    {"min_students": 5000, "max_students": None, "discount_percent": Decimal("35")},  # Enterprise
]

# Additional exam type pricing (per exam type added)
EXAM_TYPE_PRICING = {
    "single_exam": Decimal("0"),      # Base price includes 1 exam
    "two_exams": Decimal("5.00"),     # +$5 per student for 2nd exam
    "three_exams": Decimal("8.00"),   # +$8 per student for 3rd exam (cumulative)
    "all_exams": Decimal("12.00"),    # +$12 per student for all exams
}

# AI Tutor plan pricing (per academy per month)
AI_TUTOR_PRICING = {
    AITutorPlan.NONE: {
        "price": Decimal("0"),
        "credits_monthly": 0,
        "description": "No AI Tutor",
    },
    AITutorPlan.BASIC: {
        "price": Decimal("99.00"),
        "credits_monthly": 50,
        "description": "50 AI credits/month - Writing feedback, basic speaking analysis",
    },
    AITutorPlan.STANDARD: {
        "price": Decimal("249.00"),
        "credits_monthly": 200,
        "description": "200 AI credits/month - Full writing review, speaking analysis, personalized tips",
    },
    AITutorPlan.PREMIUM: {
        "price": Decimal("449.00"),
        "credits_monthly": 500,
        "description": "500 AI credits/month - Premium feedback, study plans, weakness analysis",
    },
    AITutorPlan.UNLIMITED: {
        "price": Decimal("799.00"),
        "credits_monthly": -1,  # Unlimited
        "description": "Unlimited AI credits - Full platform AI features",
    },
}


def calculate_volume_discount(num_students: int) -> Decimal:
    """Calculate discount percentage based on number of students."""
    for tier in VOLUME_DISCOUNT_TIERS:
        if tier["max_students"] is None or num_students <= tier["max_students"]:
            if num_students >= tier["min_students"]:
                return tier["discount_percent"]
    return Decimal("0")


def calculate_subscription_price(
    mock_plan: MockExamPlan,
    num_exams: int,
    num_students: int,
    ai_plan: AITutorPlan,
) -> Dict[str, Any]:
    """
    Calculate total subscription price for an academy.

    Returns detailed price breakdown.
    """
    # Base mock exam price per student
    mock_base = MOCK_EXAM_PLAN_PRICING[mock_plan]["base_price"]

    # Exam type surcharge
    if num_exams == 1:
        exam_surcharge = EXAM_TYPE_PRICING["single_exam"]
    elif num_exams == 2:
        exam_surcharge = EXAM_TYPE_PRICING["two_exams"]
    elif num_exams == 3:
        exam_surcharge = EXAM_TYPE_PRICING["three_exams"]
    else:
        exam_surcharge = EXAM_TYPE_PRICING["all_exams"]

    # Per student total
    per_student = mock_base + exam_surcharge

    # Subtotal for all students
    subtotal_students = per_student * num_students

    # Volume discount
    discount_percent = calculate_volume_discount(num_students)
    discount_amount = subtotal_students * (discount_percent / 100)
    discounted_students = subtotal_students - discount_amount

    # AI Tutor plan
    ai_price = AI_TUTOR_PRICING[ai_plan]["price"]

    # Total monthly
    total_monthly = discounted_students + ai_price

    return {
        "mock_plan": mock_plan.value,
        "num_exams": num_exams,
        "num_students": num_students,
        "ai_plan": ai_plan.value,
        "breakdown": {
            "mock_base_per_student": float(mock_base),
            "exam_surcharge_per_student": float(exam_surcharge),
            "per_student_total": float(per_student),
            "subtotal_students": float(subtotal_students),
            "volume_discount_percent": float(discount_percent),
            "volume_discount_amount": float(discount_amount),
            "discounted_students_total": float(discounted_students),
            "ai_tutor_monthly": float(ai_price),
        },
        "total_monthly": float(total_monthly),
        "total_yearly": float(total_monthly * 12 * Decimal("0.85")),  # 15% yearly discount
        "per_student_effective": float(discounted_students / num_students) if num_students > 0 else 0,
    }


# =============================================================================
# INSTITUTIONAL CONFIGURATION MODEL
# =============================================================================

class InstitutionalConfig(Base):
    """
    Main configuration for an academy's subscription.
    """
    __tablename__ = "institutional_configs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    academy_id = Column(UUID(as_uuid=True), ForeignKey("academies.id"), nullable=False, unique=True)

    # Exam Selection
    selected_exams = Column(ARRAY(String), nullable=False, default=[])  # e.g., ["ielts", "toefl", "oet_medicine"]
    oet_professions = Column(ARRAY(String), default=[])  # For OET: which professions

    # Mock Exam Plan
    mock_exam_plan = Column(SQLEnum(MockExamPlan), nullable=False, default=MockExamPlan.PLAN_10)

    # Student Configuration
    max_students = Column(Integer, nullable=False, default=100)
    current_students = Column(Integer, default=0)

    # AI Tutor Plan
    ai_tutor_plan = Column(SQLEnum(AITutorPlan), nullable=False, default=AITutorPlan.NONE)
    ai_credits_remaining = Column(Integer, default=0)
    ai_credits_reset_date = Column(DateTime(timezone=True))

    # Features Enabled
    enable_writing_review = Column(Boolean, default=False)
    enable_speaking_review = Column(Boolean, default=False)
    enable_speaking_practice = Column(Boolean, default=True)  # P2P speaking practice
    enable_video_classes = Column(Boolean, default=False)
    enable_gamification = Column(Boolean, default=False)
    enable_machine_learning = Column(Boolean, default=False)
    enable_marketplace_selling = Column(Boolean, default=False)
    enable_marketplace_buying = Column(Boolean, default=True)

    # White Label Settings
    is_white_label = Column(Boolean, default=False)
    white_label_config = Column(JSONB, default={})  # logo, colors, domain, etc.

    # Pricing (calculated and stored)
    monthly_price = Column(Numeric(10, 2), nullable=False, default=0)
    yearly_price = Column(Numeric(10, 2), nullable=False, default=0)
    price_per_student = Column(Numeric(10, 2), nullable=False, default=0)

    # Custom Commission Rates (overrides defaults)
    custom_commission_rates = Column(JSONB, default={})

    # Subscription Status
    subscription_status = Column(String(50), default="active")  # active, paused, cancelled, trial
    subscription_start_date = Column(DateTime(timezone=True))
    subscription_end_date = Column(DateTime(timezone=True))
    trial_end_date = Column(DateTime(timezone=True))

    # Timestamps
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc),
                       onupdate=lambda: datetime.now(timezone.utc))

    # Indexes
    __table_args__ = (
        Index("ix_institutional_configs_academy", "academy_id"),
        Index("ix_institutional_configs_status", "subscription_status"),
    )

    def recalculate_pricing(self):
        """Recalculate pricing based on current configuration."""
        pricing = calculate_subscription_price(
            mock_plan=self.mock_exam_plan,
            num_exams=len(self.selected_exams),
            num_students=self.max_students,
            ai_plan=self.ai_tutor_plan,
        )
        self.monthly_price = Decimal(str(pricing["total_monthly"]))
        self.yearly_price = Decimal(str(pricing["total_yearly"]))
        self.price_per_student = Decimal(str(pricing["per_student_effective"]))


# =============================================================================
# SPEAKING PRACTICE MATCHING
# =============================================================================

class SpeakingPracticeAvailability(Base):
    """
    Tracks students who are available for peer speaking practice.
    """
    __tablename__ = "speaking_practice_availability"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    academy_id = Column(UUID(as_uuid=True), ForeignKey("academies.id"), nullable=False)

    # Availability Status
    status = Column(SQLEnum(SpeakingMatchStatus), nullable=False, default=SpeakingMatchStatus.AVAILABLE)

    # Matching Criteria
    exam_type = Column(String(50), nullable=False)  # e.g., "ielts_academic", "toefl_ibt"
    target_band_score = Column(Numeric(3, 1))  # e.g., 6.5 for IELTS
    current_level = Column(String(20))  # beginner, intermediate, advanced
    preferred_topics = Column(ARRAY(String), default=[])
    native_language = Column(String(50))

    # Availability Window
    available_from = Column(DateTime(timezone=True), nullable=False)
    available_until = Column(DateTime(timezone=True), nullable=False)
    timezone = Column(String(50), default="UTC")

    # Matching preferences
    match_same_academy_only = Column(Boolean, default=False)  # Match only within same academy
    match_similar_level_only = Column(Boolean, default=True)  # Match only with similar level

    # Timestamps
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    last_active_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        Index("ix_speaking_availability_status", "status"),
        Index("ix_speaking_availability_exam", "exam_type"),
        Index("ix_speaking_availability_level", "current_level"),
        Index("ix_speaking_availability_time", "available_from", "available_until"),
    )


class SpeakingPracticeMatch(Base):
    """
    Records matched speaking practice sessions between two students.
    """
    __tablename__ = "speaking_practice_matches"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Participants
    user_1_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    user_2_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    academy_1_id = Column(UUID(as_uuid=True), ForeignKey("academies.id"))
    academy_2_id = Column(UUID(as_uuid=True), ForeignKey("academies.id"))

    # Session Details
    exam_type = Column(String(50), nullable=False)
    speaking_part = Column(String(20))  # e.g., "part1", "part2", "part3" for IELTS
    topic = Column(Text)
    instructions = Column(JSONB, default={})  # Exam-specific instructions

    # Video Session
    video_platform = Column(String(50), default="zoom")
    video_meeting_url = Column(Text)
    video_meeting_id = Column(String(100))
    video_meeting_password = Column(String(50))

    # Status
    status = Column(SQLEnum(VideoSessionStatus), nullable=False, default=VideoSessionStatus.SCHEDULED)
    scheduled_at = Column(DateTime(timezone=True), nullable=False)
    started_at = Column(DateTime(timezone=True))
    ended_at = Column(DateTime(timezone=True))
    duration_minutes = Column(Integer)

    # Feedback
    user_1_rating = Column(Integer)  # 1-5
    user_2_rating = Column(Integer)
    user_1_feedback = Column(Text)
    user_2_feedback = Column(Text)

    # Timestamps
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        Index("ix_speaking_match_users", "user_1_id", "user_2_id"),
        Index("ix_speaking_match_status", "status"),
        Index("ix_speaking_match_scheduled", "scheduled_at"),
    )


# =============================================================================
# VIDEO CLASS SESSIONS (Academy's own classes via Zoom)
# =============================================================================

class VideoClassSession(Base):
    """
    Academy's own video classes via Zoom integration.
    """
    __tablename__ = "video_class_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    academy_id = Column(UUID(as_uuid=True), ForeignKey("academies.id"), nullable=False)
    teacher_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))

    # Class Details
    title = Column(String(200), nullable=False)
    description = Column(Text)
    exam_type = Column(String(50))  # Related exam type
    class_type = Column(String(50))  # lecture, practice, review, qa_session
    max_participants = Column(Integer, default=30)

    # Video Session
    video_platform = Column(String(50), default="zoom")
    video_meeting_url = Column(Text)
    video_meeting_id = Column(String(100))
    video_meeting_password = Column(String(50))
    video_host_key = Column(String(50))  # For teacher to claim host

    # Schedule
    scheduled_at = Column(DateTime(timezone=True), nullable=False)
    duration_minutes = Column(Integer, default=60)
    timezone = Column(String(50), default="UTC")
    is_recurring = Column(Boolean, default=False)
    recurrence_rule = Column(String(200))  # iCal RRULE format

    # Status
    status = Column(SQLEnum(VideoSessionStatus), nullable=False, default=VideoSessionStatus.SCHEDULED)
    started_at = Column(DateTime(timezone=True))
    ended_at = Column(DateTime(timezone=True))
    actual_duration_minutes = Column(Integer)

    # Recording
    is_recorded = Column(Boolean, default=False)
    recording_url = Column(Text)
    recording_available_until = Column(DateTime(timezone=True))

    # Timestamps
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        Index("ix_video_class_academy", "academy_id"),
        Index("ix_video_class_scheduled", "scheduled_at"),
        Index("ix_video_class_status", "status"),
    )


class VideoClassAttendee(Base):
    """
    Students registered/attended a video class.
    """
    __tablename__ = "video_class_attendees"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("video_class_sessions.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    # Attendance
    registered_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    joined_at = Column(DateTime(timezone=True))
    left_at = Column(DateTime(timezone=True))
    attended = Column(Boolean, default=False)
    attendance_minutes = Column(Integer)

    # Feedback
    rating = Column(Integer)  # 1-5
    feedback = Column(Text)

    __table_args__ = (
        UniqueConstraint("session_id", "user_id", name="uq_video_attendee_session_user"),
        Index("ix_video_attendee_session", "session_id"),
        Index("ix_video_attendee_user", "user_id"),
    )


# =============================================================================
# GAMIFICATION
# =============================================================================

class GamificationConfig(Base):
    """
    Gamification settings for an academy.
    """
    __tablename__ = "gamification_configs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    academy_id = Column(UUID(as_uuid=True), ForeignKey("academies.id"), nullable=False, unique=True)

    # Features enabled
    enable_points = Column(Boolean, default=True)
    enable_badges = Column(Boolean, default=True)
    enable_leaderboards = Column(Boolean, default=True)
    enable_streaks = Column(Boolean, default=True)
    enable_challenges = Column(Boolean, default=True)
    enable_levels = Column(Boolean, default=True)

    # Point configuration
    points_per_mock_exam = Column(Integer, default=100)
    points_per_section = Column(Integer, default=25)
    points_per_practice = Column(Integer, default=10)
    points_per_streak_day = Column(Integer, default=15)
    bonus_multiplier_streak_7 = Column(Numeric(3, 2), default=Decimal("1.5"))
    bonus_multiplier_streak_30 = Column(Numeric(3, 2), default=Decimal("2.0"))

    # Leaderboard settings
    leaderboard_visibility = Column(String(20), default="academy")  # academy, global, none
    leaderboard_reset_period = Column(String(20), default="weekly")  # daily, weekly, monthly, never

    # Custom badges (JSON array of badge definitions)
    custom_badges = Column(JSONB, default=[])

    # Custom challenges
    custom_challenges = Column(JSONB, default=[])

    # Timestamps
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class StudentGamification(Base):
    """
    Individual student's gamification progress.
    """
    __tablename__ = "student_gamification"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    academy_id = Column(UUID(as_uuid=True), ForeignKey("academies.id"), nullable=False)

    # Points
    total_points = Column(Integer, default=0)
    weekly_points = Column(Integer, default=0)
    monthly_points = Column(Integer, default=0)
    lifetime_points = Column(Integer, default=0)

    # Level
    current_level = Column(Integer, default=1)
    level_name = Column(String(50), default="Beginner")
    points_to_next_level = Column(Integer, default=500)

    # Streaks
    current_streak = Column(Integer, default=0)
    longest_streak = Column(Integer, default=0)
    last_activity_date = Column(DateTime(timezone=True))

    # Badges (JSON array of earned badge IDs)
    badges = Column(JSONB, default=[])

    # Achievements
    mock_exams_completed = Column(Integer, default=0)
    sections_completed = Column(Integer, default=0)
    speaking_practices_completed = Column(Integer, default=0)
    writing_reviews_received = Column(Integer, default=0)

    # Rankings
    academy_rank = Column(Integer)
    global_rank = Column(Integer)

    # Timestamps
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        UniqueConstraint("user_id", "academy_id", name="uq_student_gamification_user_academy"),
        Index("ix_student_gamification_points", "total_points"),
        Index("ix_student_gamification_level", "current_level"),
        Index("ix_student_gamification_academy", "academy_id"),
    )


# =============================================================================
# WHITE LABEL CONFIGURATION
# =============================================================================

class WhiteLabelConfig(Base):
    """
    White label customization for an academy.
    """
    __tablename__ = "white_label_configs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    academy_id = Column(UUID(as_uuid=True), ForeignKey("academies.id"), nullable=False, unique=True)

    # Branding
    brand_name = Column(String(200))
    logo_url = Column(Text)
    favicon_url = Column(Text)
    primary_color = Column(String(20), default="#3B82F6")  # Blue
    secondary_color = Column(String(20), default="#10B981")  # Green
    accent_color = Column(String(20), default="#F59E0B")  # Amber

    # Custom Domain
    custom_domain = Column(String(200))
    domain_verified = Column(Boolean, default=False)
    ssl_certificate_id = Column(String(200))

    # Custom Content
    welcome_message = Column(Text)
    footer_text = Column(Text)
    terms_of_service_url = Column(Text)
    privacy_policy_url = Column(Text)
    support_email = Column(String(200))
    support_phone = Column(String(50))

    # Feature Visibility
    hide_proficienthub_branding = Column(Boolean, default=False)
    show_academy_logo_only = Column(Boolean, default=False)
    custom_email_templates = Column(JSONB, default={})

    # Social Links
    social_links = Column(JSONB, default={})  # {"facebook": "...", "twitter": "...", etc.}

    # Custom CSS
    custom_css = Column(Text)

    # Analytics
    google_analytics_id = Column(String(50))
    facebook_pixel_id = Column(String(50))

    # Timestamps
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


# =============================================================================
# CONFIGURABLE COMMISSION RATES
# =============================================================================

class AcademyCommissionConfig(Base):
    """
    Custom commission rates for an academy.
    Allows overriding default platform commission rates.
    """
    __tablename__ = "academy_commission_configs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    academy_id = Column(UUID(as_uuid=True), ForeignKey("academies.id"), nullable=False, unique=True)

    # Commission rates (as percentages)
    platform_fee_percent = Column(Numeric(5, 2), default=Decimal("3.00"))  # 3% platform fee
    marketplace_sale_percent = Column(Numeric(5, 2), default=Decimal("15.00"))  # 15% on marketplace sales
    referral_percent = Column(Numeric(5, 2), default=Decimal("5.00"))  # 5% referral commission
    resale_percent = Column(Numeric(5, 2), default=Decimal("0.00"))  # 0% on resale to students (they keep 100%)

    # Special rates
    is_enterprise_rate = Column(Boolean, default=False)
    enterprise_notes = Column(Text)  # Negotiated terms

    # Rate validity
    valid_from = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    valid_until = Column(DateTime(timezone=True))  # Null = no expiry

    # Approval
    approved_by = Column(String(200))  # Admin who approved custom rates
    approved_at = Column(DateTime(timezone=True))

    # Timestamps
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    def get_commission_rate(self, commission_type: str) -> Decimal:
        """Get commission rate for a specific type."""
        rates = {
            "platform_fee": self.platform_fee_percent,
            "marketplace_sale": self.marketplace_sale_percent,
            "referral": self.referral_percent,
            "resale": self.resale_percent,
        }
        return rates.get(commission_type, Decimal("0"))


# =============================================================================
# EXAM-SPECIFIC SPEAKING PRACTICE INSTRUCTIONS
# =============================================================================

SPEAKING_PRACTICE_INSTRUCTIONS = {
    "ielts_academic": {
        "part1": {
            "name": "Introduction and Interview",
            "duration_minutes": 5,
            "instructions": [
                "Student A will be the examiner, Student B will be the candidate",
                "Ask 3-4 questions about 2-3 familiar topics (home, work, studies, hobbies)",
                "Questions should be about personal experience and opinions",
                "After 4-5 minutes, switch roles",
            ],
            "sample_topics": ["Your hometown", "Your work or studies", "Free time activities", "Family"]
        },
        "part2": {
            "name": "Long Turn (Cue Card)",
            "duration_minutes": 4,
            "instructions": [
                "Student A gives Student B a cue card topic",
                "Student B has 1 minute to prepare (use paper to make notes)",
                "Student B speaks for 1-2 minutes on the topic",
                "Student A may ask 1-2 follow-up questions",
                "Switch roles and repeat",
            ],
            "sample_topics": [
                "Describe a memorable trip you took",
                "Describe a person who has influenced you",
                "Describe a skill you would like to learn",
            ]
        },
        "part3": {
            "name": "Discussion",
            "duration_minutes": 5,
            "instructions": [
                "This is a two-way discussion related to the Part 2 topic",
                "Student A asks abstract questions about the topic",
                "Questions should explore broader issues, comparisons, and future implications",
                "Both students can share opinions and discuss",
            ],
            "sample_questions": [
                "How has travel changed in recent years?",
                "What qualities make a good mentor?",
                "Why do people want to learn new skills?",
            ]
        }
    },
    "toefl_ibt": {
        "independent": {
            "name": "Independent Speaking",
            "duration_minutes": 4,
            "instructions": [
                "Student A reads a prompt to Student B",
                "Student B has 15 seconds to prepare",
                "Student B speaks for 45 seconds",
                "Switch roles with a new prompt",
            ],
            "sample_prompts": [
                "Talk about a teacher who has influenced you",
                "Do you prefer studying alone or in groups?",
                "Describe a place you like to visit",
            ]
        },
        "integrated": {
            "name": "Integrated Speaking",
            "duration_minutes": 6,
            "instructions": [
                "Student A reads a short passage to Student B (30 seconds)",
                "Student A then describes a related scenario/lecture",
                "Student B has 30 seconds to prepare",
                "Student B speaks for 60 seconds integrating both sources",
            ],
        }
    },
    "pte_academic": {
        "describe_image": {
            "name": "Describe Image",
            "duration_minutes": 3,
            "instructions": [
                "Student A shows an image (graph, chart, picture) to Student B",
                "Student B has 25 seconds to study the image",
                "Student B describes the image for 40 seconds",
                "Switch roles",
            ],
        },
        "retell_lecture": {
            "name": "Re-tell Lecture",
            "duration_minutes": 4,
            "instructions": [
                "Student A reads a short lecture passage (1-2 minutes)",
                "Student B listens and takes notes",
                "Student B retells the main points in 40 seconds",
                "Switch roles",
            ],
        }
    },
    "oet": {
        "role_play": {
            "name": "Role Play",
            "duration_minutes": 10,
            "instructions": [
                "One student plays the healthcare professional, one plays the patient/carer",
                "Read the role card carefully (2-3 minutes preparation)",
                "The 'patient' has specific concerns and questions on their card",
                "The 'professional' must gather information and provide appropriate advice",
                "Speak for 5 minutes",
                "Switch roles with a new scenario",
            ],
            "scenario_types": [
                "Patient presenting with symptoms",
                "Explaining a diagnosis",
                "Discussing treatment options",
                "Giving lifestyle advice",
                "Addressing patient concerns",
            ]
        }
    },
    "toeic": {
        "opinion": {
            "name": "Express Opinion",
            "duration_minutes": 4,
            "instructions": [
                "Student A reads a business scenario/question to Student B",
                "Student B has 45 seconds to prepare",
                "Student B speaks for 60 seconds expressing their opinion",
                "Student A can ask follow-up questions",
                "Switch roles",
            ],
            "sample_topics": [
                "Should companies allow remote work?",
                "Is it better to specialize or be a generalist?",
                "How should companies handle customer complaints?",
            ]
        }
    }
}


def get_speaking_instructions(exam_type: str, part: str = None) -> Dict[str, Any]:
    """Get speaking practice instructions for an exam type."""
    exam_base = exam_type.split("_")[0]  # Get base exam (e.g., "ielts" from "ielts_academic")

    if exam_type.startswith("oet"):
        return SPEAKING_PRACTICE_INSTRUCTIONS.get("oet", {})

    instructions = SPEAKING_PRACTICE_INSTRUCTIONS.get(exam_type) or \
                   SPEAKING_PRACTICE_INSTRUCTIONS.get(exam_base, {})

    if part and part in instructions:
        return {part: instructions[part]}

    return instructions
