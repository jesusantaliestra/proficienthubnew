"""
CRM (Customer Relationship Management) Models for ProficientHub B2B Platform.

This module provides comprehensive CRM functionality including:
- Lead and contact management
- Customer lifecycle tracking
- Sales pipeline management
- Communication history
- Automated workflows and campaigns
- External CRM integration support
"""

import uuid
import enum
from datetime import datetime, date, timedelta
from decimal import Decimal
from typing import Optional, List, Dict, Any

from sqlalchemy import (
    String, Text, Boolean, Integer, Numeric, DateTime, Date, JSON,
    ForeignKey, Index, CheckConstraint, UniqueConstraint, Enum as SAEnum
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, ARRAY

from app.db.base import Base, TimestampMixin, SoftDeleteMixin


# ===================== ENUMS =====================

class LeadSource(str, enum.Enum):
    """Source of lead acquisition."""
    WEBSITE = "website"
    REFERRAL = "referral"
    ADVERTISEMENT = "advertisement"
    SOCIAL_MEDIA = "social_media"
    EMAIL_CAMPAIGN = "email_campaign"
    COLD_OUTREACH = "cold_outreach"
    PARTNER = "partner"
    EVENT = "event"
    CONTENT_MARKETING = "content_marketing"
    ORGANIC_SEARCH = "organic_search"
    PAID_SEARCH = "paid_search"
    MARKETPLACE = "marketplace"
    API_INTEGRATION = "api_integration"
    MANUAL_ENTRY = "manual_entry"
    IMPORT = "import"


class LeadStatus(str, enum.Enum):
    """Lead lifecycle status."""
    NEW = "new"
    CONTACTED = "contacted"
    QUALIFIED = "qualified"
    PROPOSAL_SENT = "proposal_sent"
    NEGOTIATION = "negotiation"
    WON = "won"
    LOST = "lost"
    NURTURING = "nurturing"
    UNQUALIFIED = "unqualified"
    INACTIVE = "inactive"


class ContactType(str, enum.Enum):
    """Type of contact within an organization."""
    PRIMARY = "primary"
    BILLING = "billing"
    TECHNICAL = "technical"
    DECISION_MAKER = "decision_maker"
    INFLUENCER = "influencer"
    END_USER = "end_user"
    CHAMPION = "champion"


class CommunicationType(str, enum.Enum):
    """Type of communication interaction."""
    EMAIL = "email"
    PHONE_CALL = "phone_call"
    VIDEO_CALL = "video_call"
    IN_PERSON = "in_person"
    CHAT = "chat"
    SMS = "sms"
    SOCIAL_MEDIA = "social_media"
    SUPPORT_TICKET = "support_ticket"
    NOTE = "note"
    AUTOMATED = "automated"


class CommunicationDirection(str, enum.Enum):
    """Direction of communication."""
    INBOUND = "inbound"
    OUTBOUND = "outbound"
    INTERNAL = "internal"


class TaskPriority(str, enum.Enum):
    """Priority level for CRM tasks."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class TaskStatus(str, enum.Enum):
    """Status of CRM tasks."""
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    DEFERRED = "deferred"


class DealStage(str, enum.Enum):
    """Sales pipeline stages."""
    PROSPECTING = "prospecting"
    QUALIFICATION = "qualification"
    NEEDS_ANALYSIS = "needs_analysis"
    VALUE_PROPOSITION = "value_proposition"
    PROPOSAL = "proposal"
    NEGOTIATION = "negotiation"
    CLOSED_WON = "closed_won"
    CLOSED_LOST = "closed_lost"


class CampaignType(str, enum.Enum):
    """Marketing campaign types."""
    EMAIL = "email"
    SMS = "sms"
    SOCIAL_MEDIA = "social_media"
    WEBINAR = "webinar"
    EVENT = "event"
    CONTENT = "content"
    REFERRAL = "referral"
    RETARGETING = "retargeting"
    ONBOARDING = "onboarding"
    UPSELL = "upsell"
    REACTIVATION = "reactivation"


class CampaignStatus(str, enum.Enum):
    """Marketing campaign status."""
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class WorkflowTrigger(str, enum.Enum):
    """Workflow automation triggers."""
    LEAD_CREATED = "lead_created"
    LEAD_STATUS_CHANGED = "lead_status_changed"
    DEAL_CREATED = "deal_created"
    DEAL_STAGE_CHANGED = "deal_stage_changed"
    DEAL_WON = "deal_won"
    DEAL_LOST = "deal_lost"
    STUDENT_ENROLLED = "student_enrolled"
    EXAM_COMPLETED = "exam_completed"
    CREDITS_LOW = "credits_low"
    PLAN_EXPIRING = "plan_expiring"
    INACTIVITY = "inactivity"
    CUSTOM_EVENT = "custom_event"


class WorkflowActionType(str, enum.Enum):
    """Types of workflow actions."""
    SEND_EMAIL = "send_email"
    SEND_SMS = "send_sms"
    CREATE_TASK = "create_task"
    UPDATE_FIELD = "update_field"
    ADD_TAG = "add_tag"
    REMOVE_TAG = "remove_tag"
    ASSIGN_USER = "assign_user"
    NOTIFY_USER = "notify_user"
    WEBHOOK = "webhook"
    DELAY = "delay"
    CONDITION = "condition"


class ExternalCRMType(str, enum.Enum):
    """Supported external CRM systems."""
    SALESFORCE = "salesforce"
    HUBSPOT = "hubspot"
    ZOHO = "zoho"
    PIPEDRIVE = "pipedrive"
    MONDAY = "monday"
    DYNAMICS_365 = "dynamics_365"
    FRESHSALES = "freshsales"
    INSIGHTLY = "insightly"
    CUSTOM_WEBHOOK = "custom_webhook"


# ===================== MODELS =====================

class CRMLead(Base, TimestampMixin, SoftDeleteMixin):
    """
    Lead/Prospect management for B2B sales.

    Tracks potential institutional customers from first contact
    through conversion to paying customer.
    """
    __tablename__ = "crm_leads"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Organization info
    organization_name: Mapped[str] = mapped_column(String(255))
    organization_type: Mapped[Optional[str]] = mapped_column(String(100))  # academy, university, corporate
    website: Mapped[Optional[str]] = mapped_column(String(500))
    industry: Mapped[Optional[str]] = mapped_column(String(100))
    employee_count: Mapped[Optional[int]] = mapped_column(Integer)
    annual_revenue: Mapped[Optional[Decimal]] = mapped_column(Numeric(15, 2))

    # Primary contact
    contact_name: Mapped[str] = mapped_column(String(255))
    contact_email: Mapped[str] = mapped_column(String(255))
    contact_phone: Mapped[Optional[str]] = mapped_column(String(50))
    contact_title: Mapped[Optional[str]] = mapped_column(String(100))

    # Lead details
    source: Mapped[LeadSource] = mapped_column(SAEnum(LeadSource), default=LeadSource.MANUAL_ENTRY)
    source_details: Mapped[Optional[str]] = mapped_column(Text)  # Campaign name, referrer, etc.
    status: Mapped[LeadStatus] = mapped_column(SAEnum(LeadStatus), default=LeadStatus.NEW)

    # Scoring and qualification
    lead_score: Mapped[int] = mapped_column(Integer, default=0)  # 0-100
    is_qualified: Mapped[bool] = mapped_column(Boolean, default=False)
    qualification_notes: Mapped[Optional[str]] = mapped_column(Text)

    # Interest details
    interested_exams: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String), default=list)
    estimated_students: Mapped[Optional[int]] = mapped_column(Integer)
    estimated_deal_value: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 2))
    budget_range: Mapped[Optional[str]] = mapped_column(String(100))  # e.g., "5k-10k"
    timeline: Mapped[Optional[str]] = mapped_column(String(100))  # e.g., "Q2 2026"

    # Assignment
    assigned_to_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    assigned_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    # Dates
    first_contact_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    last_contact_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    next_followup_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    converted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    # Conversion
    converted_to_academy_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("academies.id"))
    lost_reason: Mapped[Optional[str]] = mapped_column(String(255))

    # Tags and custom fields
    tags: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String), default=list)
    custom_fields: Mapped[Optional[Dict]] = mapped_column(JSON, default=dict)

    # External CRM sync
    external_crm_id: Mapped[Optional[str]] = mapped_column(String(255))
    external_crm_type: Mapped[Optional[ExternalCRMType]] = mapped_column(SAEnum(ExternalCRMType))
    last_synced_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    # Relationships
    contacts: Mapped[List["CRMContact"]] = relationship("CRMContact", back_populates="lead")
    communications: Mapped[List["CRMCommunication"]] = relationship("CRMCommunication", back_populates="lead")
    tasks: Mapped[List["CRMTask"]] = relationship("CRMTask", back_populates="lead")
    deals: Mapped[List["CRMDeal"]] = relationship("CRMDeal", back_populates="lead")

    __table_args__ = (
        Index('ix_crm_lead_status', 'status'),
        Index('ix_crm_lead_source', 'source'),
        Index('ix_crm_lead_assigned', 'assigned_to_id'),
        Index('ix_crm_lead_score', 'lead_score'),
        Index('ix_crm_lead_next_followup', 'next_followup_date'),
        Index('ix_crm_lead_external', 'external_crm_type', 'external_crm_id'),
    )


class CRMContact(Base, TimestampMixin, SoftDeleteMixin):
    """
    Individual contacts within organizations.

    Multiple contacts can be associated with a lead or academy.
    """
    __tablename__ = "crm_contacts"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Associations
    lead_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("crm_leads.id"))
    academy_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("academies.id"))

    # Contact info
    first_name: Mapped[str] = mapped_column(String(100))
    last_name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(255))
    phone: Mapped[Optional[str]] = mapped_column(String(50))
    mobile: Mapped[Optional[str]] = mapped_column(String(50))

    # Role
    title: Mapped[Optional[str]] = mapped_column(String(100))
    department: Mapped[Optional[str]] = mapped_column(String(100))
    contact_type: Mapped[ContactType] = mapped_column(SAEnum(ContactType), default=ContactType.PRIMARY)
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False)

    # Preferences
    preferred_contact_method: Mapped[Optional[str]] = mapped_column(String(50))
    preferred_language: Mapped[str] = mapped_column(String(10), default="en")
    timezone: Mapped[Optional[str]] = mapped_column(String(50))

    # Social
    linkedin_url: Mapped[Optional[str]] = mapped_column(String(500))
    twitter_handle: Mapped[Optional[str]] = mapped_column(String(100))

    # Marketing
    email_opt_in: Mapped[bool] = mapped_column(Boolean, default=True)
    sms_opt_in: Mapped[bool] = mapped_column(Boolean, default=False)
    last_email_sent_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    last_email_opened_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    # Notes
    notes: Mapped[Optional[str]] = mapped_column(Text)
    tags: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String), default=list)
    custom_fields: Mapped[Optional[Dict]] = mapped_column(JSON, default=dict)

    # External sync
    external_crm_id: Mapped[Optional[str]] = mapped_column(String(255))

    # Relationships
    lead: Mapped[Optional["CRMLead"]] = relationship("CRMLead", back_populates="contacts")
    communications: Mapped[List["CRMCommunication"]] = relationship("CRMCommunication", back_populates="contact")

    __table_args__ = (
        Index('ix_crm_contact_lead', 'lead_id'),
        Index('ix_crm_contact_academy', 'academy_id'),
        Index('ix_crm_contact_email', 'email'),
    )


class CRMCommunication(Base, TimestampMixin):
    """
    Communication history with leads and customers.

    Tracks all interactions: emails, calls, meetings, notes.
    """
    __tablename__ = "crm_communications"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Associations
    lead_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("crm_leads.id"))
    academy_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("academies.id"))
    contact_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("crm_contacts.id"))
    deal_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("crm_deals.id"))

    # User who logged this
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))

    # Communication details
    type: Mapped[CommunicationType] = mapped_column(SAEnum(CommunicationType))
    direction: Mapped[CommunicationDirection] = mapped_column(SAEnum(CommunicationDirection))

    subject: Mapped[Optional[str]] = mapped_column(String(500))
    content: Mapped[Optional[str]] = mapped_column(Text)
    summary: Mapped[Optional[str]] = mapped_column(Text)  # AI-generated or manual summary

    # For calls/meetings
    duration_minutes: Mapped[Optional[int]] = mapped_column(Integer)
    outcome: Mapped[Optional[str]] = mapped_column(String(255))

    # For emails
    email_message_id: Mapped[Optional[str]] = mapped_column(String(255))
    email_thread_id: Mapped[Optional[str]] = mapped_column(String(255))
    email_opened_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    email_clicked_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    # Scheduling
    scheduled_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    # Attachments
    attachments: Mapped[Optional[List[Dict]]] = mapped_column(JSON, default=list)  # [{name, url, size}]

    # Sentiment (AI-analyzed)
    sentiment_score: Mapped[Optional[Decimal]] = mapped_column(Numeric(3, 2))  # -1.0 to 1.0
    sentiment_label: Mapped[Optional[str]] = mapped_column(String(20))  # positive, neutral, negative

    # Relationships
    lead: Mapped[Optional["CRMLead"]] = relationship("CRMLead", back_populates="communications")
    contact: Mapped[Optional["CRMContact"]] = relationship("CRMContact", back_populates="communications")
    deal: Mapped[Optional["CRMDeal"]] = relationship("CRMDeal", back_populates="communications")

    __table_args__ = (
        Index('ix_crm_comm_lead', 'lead_id'),
        Index('ix_crm_comm_academy', 'academy_id'),
        Index('ix_crm_comm_type', 'type'),
        Index('ix_crm_comm_created', 'created_at'),
    )


class CRMDeal(Base, TimestampMixin, SoftDeleteMixin):
    """
    Sales pipeline deals/opportunities.

    Tracks potential revenue through the sales process.
    """
    __tablename__ = "crm_deals"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Associations
    lead_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("crm_leads.id"))
    academy_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("academies.id"))

    # Deal info
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[Optional[str]] = mapped_column(Text)

    # Pipeline
    stage: Mapped[DealStage] = mapped_column(SAEnum(DealStage), default=DealStage.PROSPECTING)
    probability: Mapped[int] = mapped_column(Integer, default=10)  # 0-100%

    # Value
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    currency: Mapped[str] = mapped_column(String(3), default="USD")
    recurring_revenue: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 2))  # Monthly
    contract_length_months: Mapped[Optional[int]] = mapped_column(Integer)

    # Products/services
    products: Mapped[Optional[List[Dict]]] = mapped_column(JSON, default=list)
    # [{product_id, name, quantity, unit_price, total}]

    # Assignment
    owner_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))

    # Dates
    expected_close_date: Mapped[Optional[date]] = mapped_column(Date)
    actual_close_date: Mapped[Optional[date]] = mapped_column(Date)

    # Win/Loss
    won_reason: Mapped[Optional[str]] = mapped_column(String(255))
    lost_reason: Mapped[Optional[str]] = mapped_column(String(255))
    competitor: Mapped[Optional[str]] = mapped_column(String(255))

    # Notes and history
    notes: Mapped[Optional[str]] = mapped_column(Text)
    stage_history: Mapped[Optional[List[Dict]]] = mapped_column(JSON, default=list)
    # [{stage, entered_at, exited_at, duration_days}]

    tags: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String), default=list)
    custom_fields: Mapped[Optional[Dict]] = mapped_column(JSON, default=dict)

    # External sync
    external_crm_id: Mapped[Optional[str]] = mapped_column(String(255))

    # Relationships
    lead: Mapped["CRMLead"] = relationship("CRMLead", back_populates="deals")
    communications: Mapped[List["CRMCommunication"]] = relationship("CRMCommunication", back_populates="deal")
    tasks: Mapped[List["CRMTask"]] = relationship("CRMTask", back_populates="deal")

    __table_args__ = (
        Index('ix_crm_deal_lead', 'lead_id'),
        Index('ix_crm_deal_stage', 'stage'),
        Index('ix_crm_deal_owner', 'owner_id'),
        Index('ix_crm_deal_close_date', 'expected_close_date'),
        CheckConstraint('probability >= 0 AND probability <= 100', name='ck_deal_probability'),
    )


class CRMTask(Base, TimestampMixin, SoftDeleteMixin):
    """
    CRM tasks and reminders.

    Follow-ups, meetings, calls to schedule.
    """
    __tablename__ = "crm_tasks"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Associations
    lead_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("crm_leads.id"))
    academy_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("academies.id"))
    deal_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("crm_deals.id"))

    # Task details
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[Optional[str]] = mapped_column(Text)
    task_type: Mapped[str] = mapped_column(String(50))  # call, email, meeting, follow_up, demo, other

    # Priority and status
    priority: Mapped[TaskPriority] = mapped_column(SAEnum(TaskPriority), default=TaskPriority.MEDIUM)
    status: Mapped[TaskStatus] = mapped_column(SAEnum(TaskStatus), default=TaskStatus.TODO)

    # Assignment
    assigned_to_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    created_by_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))

    # Scheduling
    due_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    reminder_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    # Recurrence
    is_recurring: Mapped[bool] = mapped_column(Boolean, default=False)
    recurrence_pattern: Mapped[Optional[str]] = mapped_column(String(100))  # daily, weekly, monthly
    recurrence_end_date: Mapped[Optional[date]] = mapped_column(Date)

    # Results
    outcome: Mapped[Optional[str]] = mapped_column(Text)

    # Relationships
    lead: Mapped[Optional["CRMLead"]] = relationship("CRMLead", back_populates="tasks")
    deal: Mapped[Optional["CRMDeal"]] = relationship("CRMDeal", back_populates="tasks")

    __table_args__ = (
        Index('ix_crm_task_assigned', 'assigned_to_id'),
        Index('ix_crm_task_status', 'status'),
        Index('ix_crm_task_due', 'due_date'),
        Index('ix_crm_task_lead', 'lead_id'),
    )


class CRMCampaign(Base, TimestampMixin, SoftDeleteMixin):
    """
    Marketing campaigns for lead nurturing and customer engagement.
    """
    __tablename__ = "crm_campaigns"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Campaign info
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[Optional[str]] = mapped_column(Text)
    type: Mapped[CampaignType] = mapped_column(SAEnum(CampaignType))
    status: Mapped[CampaignStatus] = mapped_column(SAEnum(CampaignStatus), default=CampaignStatus.DRAFT)

    # Targeting
    target_audience: Mapped[Optional[Dict]] = mapped_column(JSON)
    # {lead_status: [], tags: [], sources: [], min_score: 0}

    # Schedule
    start_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    end_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    # Budget
    budget: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 2))
    actual_cost: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 2))

    # Goals
    goal_leads: Mapped[Optional[int]] = mapped_column(Integer)
    goal_conversions: Mapped[Optional[int]] = mapped_column(Integer)
    goal_revenue: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 2))

    # Results
    leads_generated: Mapped[int] = mapped_column(Integer, default=0)
    conversions: Mapped[int] = mapped_column(Integer, default=0)
    revenue_generated: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)

    # Email metrics (for email campaigns)
    emails_sent: Mapped[int] = mapped_column(Integer, default=0)
    emails_opened: Mapped[int] = mapped_column(Integer, default=0)
    emails_clicked: Mapped[int] = mapped_column(Integer, default=0)
    emails_bounced: Mapped[int] = mapped_column(Integer, default=0)
    unsubscribes: Mapped[int] = mapped_column(Integer, default=0)

    # Content
    content_template: Mapped[Optional[Dict]] = mapped_column(JSON)
    # {subject, body_html, body_text, from_name, from_email}

    # Owner
    owner_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))

    # Relationships
    campaign_members: Mapped[List["CRMCampaignMember"]] = relationship("CRMCampaignMember", back_populates="campaign")

    __table_args__ = (
        Index('ix_crm_campaign_status', 'status'),
        Index('ix_crm_campaign_type', 'type'),
        Index('ix_crm_campaign_dates', 'start_date', 'end_date'),
    )


class CRMCampaignMember(Base, TimestampMixin):
    """
    Members (leads/contacts) enrolled in campaigns.
    """
    __tablename__ = "crm_campaign_members"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    campaign_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("crm_campaigns.id"))
    lead_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("crm_leads.id"))
    contact_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("crm_contacts.id"))

    # Status
    status: Mapped[str] = mapped_column(String(50), default="enrolled")  # enrolled, sent, opened, clicked, converted, unsubscribed

    # Engagement
    first_sent_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    first_opened_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    first_clicked_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    converted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    unsubscribed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    # Relationships
    campaign: Mapped["CRMCampaign"] = relationship("CRMCampaign", back_populates="campaign_members")

    __table_args__ = (
        UniqueConstraint('campaign_id', 'lead_id', name='uq_campaign_lead'),
        Index('ix_crm_campaign_member_campaign', 'campaign_id'),
        Index('ix_crm_campaign_member_status', 'status'),
    )


class CRMWorkflow(Base, TimestampMixin, SoftDeleteMixin):
    """
    Automated workflow definitions.

    Define triggers and actions for automated CRM processes.
    """
    __tablename__ = "crm_workflows"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Workflow info
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[Optional[str]] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Trigger
    trigger: Mapped[WorkflowTrigger] = mapped_column(SAEnum(WorkflowTrigger))
    trigger_conditions: Mapped[Optional[Dict]] = mapped_column(JSON)
    # e.g., {field: "status", operator: "equals", value: "qualified"}

    # Actions (ordered list)
    actions: Mapped[List[Dict]] = mapped_column(JSON, default=list)
    # [{type: "send_email", template_id: "", delay_minutes: 0}, ...]

    # Execution stats
    execution_count: Mapped[int] = mapped_column(Integer, default=0)
    last_executed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    # Owner
    created_by_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))

    __table_args__ = (
        Index('ix_crm_workflow_trigger', 'trigger'),
        Index('ix_crm_workflow_active', 'is_active'),
    )


class CRMWorkflowExecution(Base, TimestampMixin):
    """
    Log of workflow executions for audit and debugging.
    """
    __tablename__ = "crm_workflow_executions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    workflow_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("crm_workflows.id"))

    # Target entity
    lead_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("crm_leads.id"))
    deal_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("crm_deals.id"))
    academy_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("academies.id"))

    # Execution details
    trigger_data: Mapped[Optional[Dict]] = mapped_column(JSON)
    actions_executed: Mapped[List[Dict]] = mapped_column(JSON, default=list)
    # [{action_type, status, result, executed_at}]

    status: Mapped[str] = mapped_column(String(50))  # success, partial, failed
    error_message: Mapped[Optional[str]] = mapped_column(Text)

    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    __table_args__ = (
        Index('ix_crm_workflow_exec_workflow', 'workflow_id'),
        Index('ix_crm_workflow_exec_status', 'status'),
        Index('ix_crm_workflow_exec_started', 'started_at'),
    )


class ExternalCRMIntegration(Base, TimestampMixin, SoftDeleteMixin):
    """
    External CRM integration configuration per academy.

    Allows academies to sync their data with external CRM systems.
    """
    __tablename__ = "external_crm_integrations"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    academy_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("academies.id"))

    # CRM type and credentials
    crm_type: Mapped[ExternalCRMType] = mapped_column(SAEnum(ExternalCRMType))

    # OAuth tokens (encrypted in production)
    access_token: Mapped[Optional[str]] = mapped_column(Text)
    refresh_token: Mapped[Optional[str]] = mapped_column(Text)
    token_expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    # API key auth (for some CRMs)
    api_key: Mapped[Optional[str]] = mapped_column(String(500))
    api_secret: Mapped[Optional[str]] = mapped_column(String(500))
    instance_url: Mapped[Optional[str]] = mapped_column(String(500))  # For Salesforce, etc.

    # Webhook for custom integrations
    webhook_url: Mapped[Optional[str]] = mapped_column(String(500))
    webhook_secret: Mapped[Optional[str]] = mapped_column(String(255))

    # Sync configuration
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    sync_direction: Mapped[str] = mapped_column(String(20), default="bidirectional")  # to_external, from_external, bidirectional
    sync_interval_minutes: Mapped[int] = mapped_column(Integer, default=15)

    # Field mappings
    field_mappings: Mapped[Optional[Dict]] = mapped_column(JSON, default=dict)
    # {local_field: external_field, ...}

    # Sync settings
    sync_leads: Mapped[bool] = mapped_column(Boolean, default=True)
    sync_contacts: Mapped[bool] = mapped_column(Boolean, default=True)
    sync_deals: Mapped[bool] = mapped_column(Boolean, default=True)
    sync_communications: Mapped[bool] = mapped_column(Boolean, default=False)

    # Last sync info
    last_sync_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    last_sync_status: Mapped[Optional[str]] = mapped_column(String(50))
    last_sync_error: Mapped[Optional[str]] = mapped_column(Text)
    records_synced: Mapped[int] = mapped_column(Integer, default=0)

    __table_args__ = (
        UniqueConstraint('academy_id', 'crm_type', name='uq_academy_crm'),
        Index('ix_external_crm_academy', 'academy_id'),
        Index('ix_external_crm_active', 'is_active'),
    )


class CRMEmailTemplate(Base, TimestampMixin, SoftDeleteMixin):
    """
    Email templates for CRM communications.
    """
    __tablename__ = "crm_email_templates"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Template info
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[Optional[str]] = mapped_column(Text)
    category: Mapped[str] = mapped_column(String(100))  # sales, onboarding, nurturing, support

    # Content
    subject: Mapped[str] = mapped_column(String(500))
    body_html: Mapped[str] = mapped_column(Text)
    body_text: Mapped[Optional[str]] = mapped_column(Text)

    # Variables (for personalization)
    available_variables: Mapped[List[str]] = mapped_column(ARRAY(String), default=list)
    # [{{first_name}}, {{organization}}, {{exam_type}}, ...]

    # Ownership
    is_system: Mapped[bool] = mapped_column(Boolean, default=False)
    academy_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("academies.id"))
    created_by_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))

    # Usage stats
    times_used: Mapped[int] = mapped_column(Integer, default=0)
    open_rate: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2))
    click_rate: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2))

    __table_args__ = (
        Index('ix_crm_email_template_category', 'category'),
        Index('ix_crm_email_template_academy', 'academy_id'),
    )


# ===================== LEAD SCORING CONFIGURATION =====================

LEAD_SCORING_RULES = {
    "demographic": {
        "employee_count": {
            "1-49": 5,
            "50-199": 10,
            "200-499": 15,
            "500-999": 20,
            "1000+": 25
        },
        "industry": {
            "education": 20,
            "corporate_training": 15,
            "government": 15,
            "healthcare": 10,
            "other": 5
        }
    },
    "interest": {
        "interested_exams_count": {
            "1": 5,
            "2": 10,
            "3+": 15
        },
        "estimated_students": {
            "1-49": 5,
            "50-99": 10,
            "100-499": 20,
            "500+": 30
        }
    },
    "engagement": {
        "website_visits": {
            "1-2": 5,
            "3-5": 10,
            "6+": 15
        },
        "email_opens": {
            "1-2": 5,
            "3-5": 10,
            "6+": 15
        },
        "demo_requested": 25,
        "pricing_page_viewed": 15,
        "trial_started": 30
    },
    "timeline": {
        "immediate": 25,
        "this_quarter": 15,
        "next_quarter": 10,
        "later": 5
    }
}

DEAL_STAGE_PROBABILITIES = {
    DealStage.PROSPECTING: 10,
    DealStage.QUALIFICATION: 20,
    DealStage.NEEDS_ANALYSIS: 40,
    DealStage.VALUE_PROPOSITION: 60,
    DealStage.PROPOSAL: 75,
    DealStage.NEGOTIATION: 90,
    DealStage.CLOSED_WON: 100,
    DealStage.CLOSED_LOST: 0
}


# ===================== HELPER FUNCTIONS =====================

def calculate_lead_score(lead: CRMLead) -> int:
    """Calculate lead score based on scoring rules."""
    score = 0

    # Demographic scoring
    if lead.employee_count:
        if lead.employee_count >= 1000:
            score += 25
        elif lead.employee_count >= 500:
            score += 20
        elif lead.employee_count >= 200:
            score += 15
        elif lead.employee_count >= 50:
            score += 10
        else:
            score += 5

    # Interest scoring
    if lead.interested_exams:
        exam_count = len(lead.interested_exams)
        if exam_count >= 3:
            score += 15
        elif exam_count >= 2:
            score += 10
        else:
            score += 5

    if lead.estimated_students:
        if lead.estimated_students >= 500:
            score += 30
        elif lead.estimated_students >= 100:
            score += 20
        elif lead.estimated_students >= 50:
            score += 10
        else:
            score += 5

    # Engagement (from communications)
    # This would need to query communications in actual implementation

    # Timeline scoring
    if lead.timeline:
        if "immediate" in lead.timeline.lower():
            score += 25
        elif "quarter" in lead.timeline.lower():
            score += 15

    return min(score, 100)  # Cap at 100


def get_next_deal_stage(current_stage: DealStage) -> Optional[DealStage]:
    """Get the next stage in the sales pipeline."""
    stages = list(DealStage)
    try:
        current_index = stages.index(current_stage)
        if current_index < len(stages) - 2:  # Exclude closed stages
            return stages[current_index + 1]
    except ValueError:
        pass
    return None
