"""
ERM (Enterprise Resource Management) Models for ProficientHub B2B Platform.

This module provides comprehensive ERM functionality including:
- Employee and staff management
- Department and team structure
- Project and task management
- Resource allocation and scheduling
- Time tracking and attendance
- Performance management
- Asset management
- Budget and expense tracking
"""

import uuid
import enum
from datetime import datetime, date, time, timedelta
from decimal import Decimal
from typing import Optional, List, Dict, Any

from sqlalchemy import (
    String, Text, Boolean, Integer, Numeric, DateTime, Date, Time, JSON,
    ForeignKey, Index, CheckConstraint, UniqueConstraint, Enum as SAEnum
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, ARRAY

from app.db.base import Base, TimestampMixin, SoftDeleteMixin


# ===================== ENUMS =====================

class EmploymentType(str, enum.Enum):
    """Type of employment."""
    FULL_TIME = "full_time"
    PART_TIME = "part_time"
    CONTRACT = "contract"
    FREELANCE = "freelance"
    INTERN = "intern"
    TEMPORARY = "temporary"


class EmployeeStatus(str, enum.Enum):
    """Employee status."""
    ACTIVE = "active"
    ON_LEAVE = "on_leave"
    SUSPENDED = "suspended"
    PROBATION = "probation"
    NOTICE_PERIOD = "notice_period"
    TERMINATED = "terminated"
    RESIGNED = "resigned"


class ProjectStatus(str, enum.Enum):
    """Project lifecycle status."""
    PLANNING = "planning"
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    ON_HOLD = "on_hold"
    REVIEW = "review"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    ARCHIVED = "archived"


class ProjectPriority(str, enum.Enum):
    """Project priority levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class TaskStatus(str, enum.Enum):
    """Task status."""
    BACKLOG = "backlog"
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    IN_REVIEW = "in_review"
    BLOCKED = "blocked"
    DONE = "done"
    CANCELLED = "cancelled"


class LeaveType(str, enum.Enum):
    """Types of leave."""
    ANNUAL = "annual"
    SICK = "sick"
    PERSONAL = "personal"
    MATERNITY = "maternity"
    PATERNITY = "paternity"
    BEREAVEMENT = "bereavement"
    UNPAID = "unpaid"
    WORK_FROM_HOME = "work_from_home"
    COMPENSATORY = "compensatory"


class LeaveStatus(str, enum.Enum):
    """Leave request status."""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    CANCELLED = "cancelled"


class AssetType(str, enum.Enum):
    """Types of assets."""
    LAPTOP = "laptop"
    DESKTOP = "desktop"
    MONITOR = "monitor"
    PHONE = "phone"
    TABLET = "tablet"
    HEADSET = "headset"
    KEYBOARD = "keyboard"
    MOUSE = "mouse"
    FURNITURE = "furniture"
    SOFTWARE_LICENSE = "software_license"
    OTHER = "other"


class AssetStatus(str, enum.Enum):
    """Asset status."""
    AVAILABLE = "available"
    ASSIGNED = "assigned"
    IN_REPAIR = "in_repair"
    RETIRED = "retired"
    LOST = "lost"


class ExpenseCategory(str, enum.Enum):
    """Expense categories."""
    TRAVEL = "travel"
    ACCOMMODATION = "accommodation"
    MEALS = "meals"
    SUPPLIES = "supplies"
    SOFTWARE = "software"
    TRAINING = "training"
    MARKETING = "marketing"
    EQUIPMENT = "equipment"
    UTILITIES = "utilities"
    RENT = "rent"
    SALARY = "salary"
    CONTRACTOR = "contractor"
    OTHER = "other"


class ExpenseStatus(str, enum.Enum):
    """Expense request status."""
    DRAFT = "draft"
    SUBMITTED = "submitted"
    APPROVED = "approved"
    REJECTED = "rejected"
    PAID = "paid"
    CANCELLED = "cancelled"


class PerformanceRating(str, enum.Enum):
    """Performance rating scale."""
    EXCEPTIONAL = "exceptional"  # 5
    EXCEEDS_EXPECTATIONS = "exceeds_expectations"  # 4
    MEETS_EXPECTATIONS = "meets_expectations"  # 3
    NEEDS_IMPROVEMENT = "needs_improvement"  # 2
    UNSATISFACTORY = "unsatisfactory"  # 1


class ResourceType(str, enum.Enum):
    """Types of resources that can be scheduled."""
    EMPLOYEE = "employee"
    ROOM = "room"
    EQUIPMENT = "equipment"
    VEHICLE = "vehicle"


# ===================== MODELS =====================

class Department(Base, TimestampMixin, SoftDeleteMixin):
    """
    Organizational department structure.
    """
    __tablename__ = "erm_departments"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    academy_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("academies.id"))

    name: Mapped[str] = mapped_column(String(255))
    code: Mapped[str] = mapped_column(String(50))
    description: Mapped[Optional[str]] = mapped_column(Text)

    # Hierarchy
    parent_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("erm_departments.id"))

    # Leadership
    head_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("erm_employees.id"))

    # Budget
    annual_budget: Mapped[Optional[Decimal]] = mapped_column(Numeric(15, 2))
    budget_year: Mapped[Optional[int]] = mapped_column(Integer)

    # Settings
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    cost_center: Mapped[Optional[str]] = mapped_column(String(50))

    # Relationships
    children: Mapped[List["Department"]] = relationship("Department", back_populates="parent")
    parent: Mapped[Optional["Department"]] = relationship("Department", back_populates="children", remote_side=[id])
    employees: Mapped[List["Employee"]] = relationship("Employee", back_populates="department", foreign_keys="Employee.department_id")
    teams: Mapped[List["Team"]] = relationship("Team", back_populates="department")

    __table_args__ = (
        UniqueConstraint('academy_id', 'code', name='uq_dept_academy_code'),
        Index('ix_erm_dept_academy', 'academy_id'),
        Index('ix_erm_dept_parent', 'parent_id'),
    )


class Team(Base, TimestampMixin, SoftDeleteMixin):
    """
    Team within a department.
    """
    __tablename__ = "erm_teams"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    academy_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("academies.id"))
    department_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("erm_departments.id"))

    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[Optional[str]] = mapped_column(Text)

    # Leadership
    lead_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("erm_employees.id"))

    # Settings
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    max_members: Mapped[Optional[int]] = mapped_column(Integer)

    # Relationships
    department: Mapped["Department"] = relationship("Department", back_populates="teams")
    members: Mapped[List["TeamMember"]] = relationship("TeamMember", back_populates="team")

    __table_args__ = (
        Index('ix_erm_team_dept', 'department_id'),
        Index('ix_erm_team_academy', 'academy_id'),
    )


class Employee(Base, TimestampMixin, SoftDeleteMixin):
    """
    Employee/Staff member of an academy.
    """
    __tablename__ = "erm_employees"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    academy_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("academies.id"))
    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))

    # Personal info
    employee_number: Mapped[str] = mapped_column(String(50))
    first_name: Mapped[str] = mapped_column(String(100))
    last_name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(255))
    phone: Mapped[Optional[str]] = mapped_column(String(50))
    date_of_birth: Mapped[Optional[date]] = mapped_column(Date)
    gender: Mapped[Optional[str]] = mapped_column(String(20))
    nationality: Mapped[Optional[str]] = mapped_column(String(100))

    # Address
    address_line1: Mapped[Optional[str]] = mapped_column(String(255))
    address_line2: Mapped[Optional[str]] = mapped_column(String(255))
    city: Mapped[Optional[str]] = mapped_column(String(100))
    state: Mapped[Optional[str]] = mapped_column(String(100))
    postal_code: Mapped[Optional[str]] = mapped_column(String(20))
    country: Mapped[Optional[str]] = mapped_column(String(100))

    # Employment
    department_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("erm_departments.id"))
    job_title: Mapped[str] = mapped_column(String(255))
    employment_type: Mapped[EmploymentType] = mapped_column(SAEnum(EmploymentType), default=EmploymentType.FULL_TIME)
    status: Mapped[EmployeeStatus] = mapped_column(SAEnum(EmployeeStatus), default=EmployeeStatus.ACTIVE)

    # Reports to
    manager_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("erm_employees.id"))

    # Dates
    hire_date: Mapped[date] = mapped_column(Date)
    probation_end_date: Mapped[Optional[date]] = mapped_column(Date)
    termination_date: Mapped[Optional[date]] = mapped_column(Date)

    # Compensation
    salary: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 2))
    salary_currency: Mapped[str] = mapped_column(String(3), default="USD")
    pay_frequency: Mapped[str] = mapped_column(String(20), default="monthly")  # weekly, biweekly, monthly

    # Leave balances
    annual_leave_days: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=20)
    sick_leave_days: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=10)
    remaining_annual_leave: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=20)
    remaining_sick_leave: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=10)

    # Working hours
    work_hours_per_week: Mapped[Decimal] = mapped_column(Numeric(4, 1), default=40)
    timezone: Mapped[str] = mapped_column(String(50), default="UTC")

    # Skills and qualifications
    skills: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String), default=list)
    certifications: Mapped[Optional[List[Dict]]] = mapped_column(JSON, default=list)
    # [{name, issuer, date_obtained, expiry_date}]

    # Emergency contact
    emergency_contact_name: Mapped[Optional[str]] = mapped_column(String(255))
    emergency_contact_phone: Mapped[Optional[str]] = mapped_column(String(50))
    emergency_contact_relation: Mapped[Optional[str]] = mapped_column(String(50))

    # Documents
    documents: Mapped[Optional[List[Dict]]] = mapped_column(JSON, default=list)
    # [{name, type, url, uploaded_at}]

    # Notes
    notes: Mapped[Optional[str]] = mapped_column(Text)
    custom_fields: Mapped[Optional[Dict]] = mapped_column(JSON, default=dict)

    # Relationships
    department: Mapped[Optional["Department"]] = relationship("Department", back_populates="employees", foreign_keys=[department_id])
    manager: Mapped[Optional["Employee"]] = relationship("Employee", back_populates="direct_reports", remote_side=[id])
    direct_reports: Mapped[List["Employee"]] = relationship("Employee", back_populates="manager")
    team_memberships: Mapped[List["TeamMember"]] = relationship("TeamMember", back_populates="employee")
    time_entries: Mapped[List["TimeEntry"]] = relationship("TimeEntry", back_populates="employee")
    leave_requests: Mapped[List["LeaveRequest"]] = relationship("LeaveRequest", back_populates="employee")
    assigned_assets: Mapped[List["AssetAssignment"]] = relationship("AssetAssignment", back_populates="employee")
    expenses: Mapped[List["Expense"]] = relationship("Expense", back_populates="employee")
    performance_reviews: Mapped[List["PerformanceReview"]] = relationship("PerformanceReview", back_populates="employee", foreign_keys="PerformanceReview.employee_id")

    __table_args__ = (
        UniqueConstraint('academy_id', 'employee_number', name='uq_employee_number'),
        UniqueConstraint('academy_id', 'email', name='uq_employee_email'),
        Index('ix_erm_employee_academy', 'academy_id'),
        Index('ix_erm_employee_dept', 'department_id'),
        Index('ix_erm_employee_manager', 'manager_id'),
        Index('ix_erm_employee_status', 'status'),
    )


class TeamMember(Base, TimestampMixin):
    """
    Team membership - links employees to teams.
    """
    __tablename__ = "erm_team_members"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    team_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("erm_teams.id"))
    employee_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("erm_employees.id"))

    role: Mapped[str] = mapped_column(String(100), default="member")  # lead, member, contributor
    joined_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    left_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Relationships
    team: Mapped["Team"] = relationship("Team", back_populates="members")
    employee: Mapped["Employee"] = relationship("Employee", back_populates="team_memberships")

    __table_args__ = (
        UniqueConstraint('team_id', 'employee_id', name='uq_team_employee'),
        Index('ix_erm_team_member_team', 'team_id'),
        Index('ix_erm_team_member_employee', 'employee_id'),
    )


class Project(Base, TimestampMixin, SoftDeleteMixin):
    """
    Project management for academies.
    """
    __tablename__ = "erm_projects"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    academy_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("academies.id"))
    department_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("erm_departments.id"))

    # Project info
    name: Mapped[str] = mapped_column(String(255))
    code: Mapped[str] = mapped_column(String(50))
    description: Mapped[Optional[str]] = mapped_column(Text)

    # Status
    status: Mapped[ProjectStatus] = mapped_column(SAEnum(ProjectStatus), default=ProjectStatus.PLANNING)
    priority: Mapped[ProjectPriority] = mapped_column(SAEnum(ProjectPriority), default=ProjectPriority.MEDIUM)
    progress_percent: Mapped[int] = mapped_column(Integer, default=0)

    # Dates
    planned_start_date: Mapped[Optional[date]] = mapped_column(Date)
    planned_end_date: Mapped[Optional[date]] = mapped_column(Date)
    actual_start_date: Mapped[Optional[date]] = mapped_column(Date)
    actual_end_date: Mapped[Optional[date]] = mapped_column(Date)

    # Leadership
    project_manager_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("erm_employees.id"))

    # Budget
    budget: Mapped[Optional[Decimal]] = mapped_column(Numeric(15, 2))
    actual_cost: Mapped[Decimal] = mapped_column(Numeric(15, 2), default=0)
    currency: Mapped[str] = mapped_column(String(3), default="USD")

    # Hours
    estimated_hours: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2))
    actual_hours: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=0)

    # Client/external
    client_name: Mapped[Optional[str]] = mapped_column(String(255))
    client_contact: Mapped[Optional[str]] = mapped_column(String(255))
    is_billable: Mapped[bool] = mapped_column(Boolean, default=False)
    hourly_rate: Mapped[Optional[Decimal]] = mapped_column(Numeric(8, 2))

    # Tags and metadata
    tags: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String), default=list)
    custom_fields: Mapped[Optional[Dict]] = mapped_column(JSON, default=dict)

    # Relationships
    tasks: Mapped[List["ProjectTask"]] = relationship("ProjectTask", back_populates="project")
    team_members: Mapped[List["ProjectTeamMember"]] = relationship("ProjectTeamMember", back_populates="project")
    milestones: Mapped[List["ProjectMilestone"]] = relationship("ProjectMilestone", back_populates="project")

    __table_args__ = (
        UniqueConstraint('academy_id', 'code', name='uq_project_code'),
        Index('ix_erm_project_academy', 'academy_id'),
        Index('ix_erm_project_status', 'status'),
        Index('ix_erm_project_manager', 'project_manager_id'),
        CheckConstraint('progress_percent >= 0 AND progress_percent <= 100', name='ck_project_progress'),
    )


class ProjectTeamMember(Base, TimestampMixin):
    """
    Project team membership.
    """
    __tablename__ = "erm_project_team_members"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("erm_projects.id"))
    employee_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("erm_employees.id"))

    role: Mapped[str] = mapped_column(String(100))  # developer, designer, qa, analyst
    allocation_percent: Mapped[int] = mapped_column(Integer, default=100)  # 0-100%
    start_date: Mapped[Optional[date]] = mapped_column(Date)
    end_date: Mapped[Optional[date]] = mapped_column(Date)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Relationships
    project: Mapped["Project"] = relationship("Project", back_populates="team_members")

    __table_args__ = (
        UniqueConstraint('project_id', 'employee_id', name='uq_project_employee'),
        Index('ix_erm_project_team_project', 'project_id'),
        Index('ix_erm_project_team_employee', 'employee_id'),
        CheckConstraint('allocation_percent >= 0 AND allocation_percent <= 100', name='ck_allocation'),
    )


class ProjectMilestone(Base, TimestampMixin, SoftDeleteMixin):
    """
    Project milestones for tracking progress.
    """
    __tablename__ = "erm_project_milestones"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("erm_projects.id"))

    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[Optional[str]] = mapped_column(Text)

    due_date: Mapped[date] = mapped_column(Date)
    completed_date: Mapped[Optional[date]] = mapped_column(Date)
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False)

    deliverables: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String), default=list)

    # Relationships
    project: Mapped["Project"] = relationship("Project", back_populates="milestones")

    __table_args__ = (
        Index('ix_erm_milestone_project', 'project_id'),
        Index('ix_erm_milestone_due', 'due_date'),
    )


class ProjectTask(Base, TimestampMixin, SoftDeleteMixin):
    """
    Tasks within projects.
    """
    __tablename__ = "erm_project_tasks"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("erm_projects.id"))
    milestone_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("erm_project_milestones.id"))
    parent_task_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("erm_project_tasks.id"))

    # Task info
    title: Mapped[str] = mapped_column(String(500))
    description: Mapped[Optional[str]] = mapped_column(Text)

    # Status
    status: Mapped[TaskStatus] = mapped_column(SAEnum(TaskStatus), default=TaskStatus.TODO)
    priority: Mapped[ProjectPriority] = mapped_column(SAEnum(ProjectPriority), default=ProjectPriority.MEDIUM)

    # Assignment
    assignee_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("erm_employees.id"))
    reporter_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("erm_employees.id"))

    # Dates
    due_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    start_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    # Estimates
    estimated_hours: Mapped[Optional[Decimal]] = mapped_column(Numeric(8, 2))
    actual_hours: Mapped[Decimal] = mapped_column(Numeric(8, 2), default=0)

    # Dependencies
    blocked_by: Mapped[Optional[List[uuid.UUID]]] = mapped_column(ARRAY(UUID(as_uuid=True)), default=list)

    # Tags and labels
    tags: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String), default=list)
    labels: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String), default=list)

    # Checklist
    checklist: Mapped[Optional[List[Dict]]] = mapped_column(JSON, default=list)
    # [{text, is_completed}]

    # Attachments
    attachments: Mapped[Optional[List[Dict]]] = mapped_column(JSON, default=list)

    # Relationships
    project: Mapped["Project"] = relationship("Project", back_populates="tasks")
    subtasks: Mapped[List["ProjectTask"]] = relationship("ProjectTask", back_populates="parent_task")
    parent_task: Mapped[Optional["ProjectTask"]] = relationship("ProjectTask", back_populates="subtasks", remote_side=[id])
    time_entries: Mapped[List["TimeEntry"]] = relationship("TimeEntry", back_populates="task")
    comments: Mapped[List["TaskComment"]] = relationship("TaskComment", back_populates="task")

    __table_args__ = (
        Index('ix_erm_task_project', 'project_id'),
        Index('ix_erm_task_assignee', 'assignee_id'),
        Index('ix_erm_task_status', 'status'),
        Index('ix_erm_task_due', 'due_date'),
    )


class TaskComment(Base, TimestampMixin, SoftDeleteMixin):
    """
    Comments on tasks.
    """
    __tablename__ = "erm_task_comments"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    task_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("erm_project_tasks.id"))
    author_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("erm_employees.id"))

    content: Mapped[str] = mapped_column(Text)
    attachments: Mapped[Optional[List[Dict]]] = mapped_column(JSON, default=list)

    # Mentions
    mentioned_employee_ids: Mapped[Optional[List[uuid.UUID]]] = mapped_column(ARRAY(UUID(as_uuid=True)), default=list)

    # Relationships
    task: Mapped["ProjectTask"] = relationship("ProjectTask", back_populates="comments")

    __table_args__ = (
        Index('ix_erm_comment_task', 'task_id'),
        Index('ix_erm_comment_author', 'author_id'),
    )


class TimeEntry(Base, TimestampMixin, SoftDeleteMixin):
    """
    Time tracking entries.
    """
    __tablename__ = "erm_time_entries"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    academy_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("academies.id"))
    employee_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("erm_employees.id"))

    # Optional associations
    project_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("erm_projects.id"))
    task_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("erm_project_tasks.id"))

    # Time
    date: Mapped[date] = mapped_column(Date)
    start_time: Mapped[Optional[time]] = mapped_column(Time)
    end_time: Mapped[Optional[time]] = mapped_column(Time)
    duration_hours: Mapped[Decimal] = mapped_column(Numeric(6, 2))

    # Description
    description: Mapped[Optional[str]] = mapped_column(Text)
    activity_type: Mapped[Optional[str]] = mapped_column(String(100))  # development, meeting, review, admin

    # Billing
    is_billable: Mapped[bool] = mapped_column(Boolean, default=False)
    billing_rate: Mapped[Optional[Decimal]] = mapped_column(Numeric(8, 2))
    is_invoiced: Mapped[bool] = mapped_column(Boolean, default=False)
    invoice_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True))

    # Approval
    is_approved: Mapped[bool] = mapped_column(Boolean, default=False)
    approved_by_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("erm_employees.id"))
    approved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    # Relationships
    employee: Mapped["Employee"] = relationship("Employee", back_populates="time_entries", foreign_keys=[employee_id])
    task: Mapped[Optional["ProjectTask"]] = relationship("ProjectTask", back_populates="time_entries")

    __table_args__ = (
        Index('ix_erm_time_employee', 'employee_id'),
        Index('ix_erm_time_project', 'project_id'),
        Index('ix_erm_time_date', 'date'),
        Index('ix_erm_time_billable', 'is_billable', 'is_invoiced'),
        CheckConstraint('duration_hours > 0', name='ck_time_duration'),
    )


class LeaveRequest(Base, TimestampMixin, SoftDeleteMixin):
    """
    Employee leave requests.
    """
    __tablename__ = "erm_leave_requests"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    academy_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("academies.id"))
    employee_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("erm_employees.id"))

    # Leave details
    leave_type: Mapped[LeaveType] = mapped_column(SAEnum(LeaveType))
    status: Mapped[LeaveStatus] = mapped_column(SAEnum(LeaveStatus), default=LeaveStatus.PENDING)

    # Dates
    start_date: Mapped[date] = mapped_column(Date)
    end_date: Mapped[date] = mapped_column(Date)
    total_days: Mapped[Decimal] = mapped_column(Numeric(5, 2))

    # Half days
    is_half_day_start: Mapped[bool] = mapped_column(Boolean, default=False)
    is_half_day_end: Mapped[bool] = mapped_column(Boolean, default=False)

    # Reason
    reason: Mapped[Optional[str]] = mapped_column(Text)
    supporting_documents: Mapped[Optional[List[Dict]]] = mapped_column(JSON, default=list)

    # Approval
    approved_by_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("erm_employees.id"))
    approved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    rejection_reason: Mapped[Optional[str]] = mapped_column(Text)

    # Coverage
    coverage_employee_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("erm_employees.id"))
    handover_notes: Mapped[Optional[str]] = mapped_column(Text)

    # Relationships
    employee: Mapped["Employee"] = relationship("Employee", back_populates="leave_requests", foreign_keys=[employee_id])

    __table_args__ = (
        Index('ix_erm_leave_employee', 'employee_id'),
        Index('ix_erm_leave_status', 'status'),
        Index('ix_erm_leave_dates', 'start_date', 'end_date'),
        CheckConstraint('end_date >= start_date', name='ck_leave_dates'),
        CheckConstraint('total_days > 0', name='ck_leave_days'),
    )


class Attendance(Base, TimestampMixin):
    """
    Daily attendance tracking.
    """
    __tablename__ = "erm_attendance"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    academy_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("academies.id"))
    employee_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("erm_employees.id"))

    date: Mapped[date] = mapped_column(Date)

    # Check in/out
    check_in_time: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    check_out_time: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    # Location (for remote work tracking)
    check_in_location: Mapped[Optional[Dict]] = mapped_column(JSON)  # {lat, lng, address}
    check_out_location: Mapped[Optional[Dict]] = mapped_column(JSON)

    # Work type
    work_type: Mapped[str] = mapped_column(String(50), default="office")  # office, remote, hybrid, field

    # Hours
    total_hours: Mapped[Optional[Decimal]] = mapped_column(Numeric(6, 2))
    overtime_hours: Mapped[Decimal] = mapped_column(Numeric(6, 2), default=0)
    break_duration_minutes: Mapped[int] = mapped_column(Integer, default=0)

    # Status
    status: Mapped[str] = mapped_column(String(50), default="present")
    # present, absent, late, half_day, on_leave, holiday, weekend

    # Notes
    notes: Mapped[Optional[str]] = mapped_column(Text)
    late_reason: Mapped[Optional[str]] = mapped_column(String(500))

    __table_args__ = (
        UniqueConstraint('employee_id', 'date', name='uq_attendance_employee_date'),
        Index('ix_erm_attendance_employee', 'employee_id'),
        Index('ix_erm_attendance_date', 'date'),
        Index('ix_erm_attendance_academy_date', 'academy_id', 'date'),
    )


class Asset(Base, TimestampMixin, SoftDeleteMixin):
    """
    Company assets management.
    """
    __tablename__ = "erm_assets"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    academy_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("academies.id"))

    # Asset info
    asset_tag: Mapped[str] = mapped_column(String(100))
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[Optional[str]] = mapped_column(Text)
    asset_type: Mapped[AssetType] = mapped_column(SAEnum(AssetType))
    status: Mapped[AssetStatus] = mapped_column(SAEnum(AssetStatus), default=AssetStatus.AVAILABLE)

    # Details
    serial_number: Mapped[Optional[str]] = mapped_column(String(255))
    model: Mapped[Optional[str]] = mapped_column(String(255))
    manufacturer: Mapped[Optional[str]] = mapped_column(String(255))

    # Value
    purchase_date: Mapped[Optional[date]] = mapped_column(Date)
    purchase_price: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 2))
    current_value: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 2))
    currency: Mapped[str] = mapped_column(String(3), default="USD")

    # Warranty
    warranty_expiry_date: Mapped[Optional[date]] = mapped_column(Date)
    warranty_details: Mapped[Optional[str]] = mapped_column(Text)

    # Location
    location: Mapped[Optional[str]] = mapped_column(String(255))
    department_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("erm_departments.id"))

    # Software licenses
    license_key: Mapped[Optional[str]] = mapped_column(String(500))
    license_seats: Mapped[Optional[int]] = mapped_column(Integer)
    license_expiry_date: Mapped[Optional[date]] = mapped_column(Date)

    # Notes and documents
    notes: Mapped[Optional[str]] = mapped_column(Text)
    documents: Mapped[Optional[List[Dict]]] = mapped_column(JSON, default=list)

    # Relationships
    assignments: Mapped[List["AssetAssignment"]] = relationship("AssetAssignment", back_populates="asset")
    maintenance_logs: Mapped[List["AssetMaintenance"]] = relationship("AssetMaintenance", back_populates="asset")

    __table_args__ = (
        UniqueConstraint('academy_id', 'asset_tag', name='uq_asset_tag'),
        Index('ix_erm_asset_academy', 'academy_id'),
        Index('ix_erm_asset_type', 'asset_type'),
        Index('ix_erm_asset_status', 'status'),
    )


class AssetAssignment(Base, TimestampMixin):
    """
    Asset assignment history.
    """
    __tablename__ = "erm_asset_assignments"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    asset_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("erm_assets.id"))
    employee_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("erm_employees.id"))

    # Assignment details
    assigned_date: Mapped[date] = mapped_column(Date)
    returned_date: Mapped[Optional[date]] = mapped_column(Date)
    is_current: Mapped[bool] = mapped_column(Boolean, default=True)

    # Condition
    condition_on_assignment: Mapped[str] = mapped_column(String(50), default="good")  # new, good, fair, poor
    condition_on_return: Mapped[Optional[str]] = mapped_column(String(50))

    # Notes
    assignment_notes: Mapped[Optional[str]] = mapped_column(Text)
    return_notes: Mapped[Optional[str]] = mapped_column(Text)

    # Acknowledged
    acknowledged_by_employee: Mapped[bool] = mapped_column(Boolean, default=False)
    acknowledged_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    # Relationships
    asset: Mapped["Asset"] = relationship("Asset", back_populates="assignments")
    employee: Mapped["Employee"] = relationship("Employee", back_populates="assigned_assets")

    __table_args__ = (
        Index('ix_erm_asset_assign_asset', 'asset_id'),
        Index('ix_erm_asset_assign_employee', 'employee_id'),
        Index('ix_erm_asset_assign_current', 'is_current'),
    )


class AssetMaintenance(Base, TimestampMixin):
    """
    Asset maintenance and repair logs.
    """
    __tablename__ = "erm_asset_maintenance"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    asset_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("erm_assets.id"))

    # Maintenance info
    maintenance_type: Mapped[str] = mapped_column(String(100))  # repair, upgrade, cleaning, inspection
    description: Mapped[str] = mapped_column(Text)

    # Dates
    scheduled_date: Mapped[Optional[date]] = mapped_column(Date)
    started_date: Mapped[Optional[date]] = mapped_column(Date)
    completed_date: Mapped[Optional[date]] = mapped_column(Date)

    # Cost
    cost: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 2))
    vendor: Mapped[Optional[str]] = mapped_column(String(255))

    # Status
    status: Mapped[str] = mapped_column(String(50), default="scheduled")  # scheduled, in_progress, completed, cancelled

    # Notes
    notes: Mapped[Optional[str]] = mapped_column(Text)
    documents: Mapped[Optional[List[Dict]]] = mapped_column(JSON, default=list)

    # Relationships
    asset: Mapped["Asset"] = relationship("Asset", back_populates="maintenance_logs")

    __table_args__ = (
        Index('ix_erm_maintenance_asset', 'asset_id'),
        Index('ix_erm_maintenance_status', 'status'),
    )


class Budget(Base, TimestampMixin, SoftDeleteMixin):
    """
    Department/Project budgets.
    """
    __tablename__ = "erm_budgets"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    academy_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("academies.id"))

    # Budget info
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[Optional[str]] = mapped_column(Text)
    budget_year: Mapped[int] = mapped_column(Integer)
    budget_month: Mapped[Optional[int]] = mapped_column(Integer)  # For monthly budgets

    # Associations
    department_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("erm_departments.id"))
    project_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("erm_projects.id"))

    # Amounts
    total_amount: Mapped[Decimal] = mapped_column(Numeric(15, 2))
    allocated_amount: Mapped[Decimal] = mapped_column(Numeric(15, 2), default=0)
    spent_amount: Mapped[Decimal] = mapped_column(Numeric(15, 2), default=0)
    currency: Mapped[str] = mapped_column(String(3), default="USD")

    # Category breakdown
    category_allocations: Mapped[Optional[Dict]] = mapped_column(JSON, default=dict)
    # {category: amount, ...}

    # Status
    status: Mapped[str] = mapped_column(String(50), default="active")  # draft, active, closed, archived
    is_approved: Mapped[bool] = mapped_column(Boolean, default=False)
    approved_by_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("erm_employees.id"))

    # Relationships
    expenses: Mapped[List["Expense"]] = relationship("Expense", back_populates="budget")

    __table_args__ = (
        Index('ix_erm_budget_academy', 'academy_id'),
        Index('ix_erm_budget_year', 'budget_year'),
        Index('ix_erm_budget_dept', 'department_id'),
        CheckConstraint('spent_amount <= total_amount', name='ck_budget_spent'),
    )


class Expense(Base, TimestampMixin, SoftDeleteMixin):
    """
    Expense tracking and reimbursements.
    """
    __tablename__ = "erm_expenses"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    academy_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("academies.id"))
    employee_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("erm_employees.id"))

    # Associations
    budget_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("erm_budgets.id"))
    project_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("erm_projects.id"))
    department_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("erm_departments.id"))

    # Expense info
    expense_number: Mapped[str] = mapped_column(String(50))
    category: Mapped[ExpenseCategory] = mapped_column(SAEnum(ExpenseCategory))
    description: Mapped[str] = mapped_column(Text)

    # Amount
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    currency: Mapped[str] = mapped_column(String(3), default="USD")
    exchange_rate: Mapped[Decimal] = mapped_column(Numeric(10, 4), default=1)
    amount_in_base_currency: Mapped[Decimal] = mapped_column(Numeric(12, 2))

    # Date
    expense_date: Mapped[date] = mapped_column(Date)
    submitted_date: Mapped[Optional[date]] = mapped_column(Date)

    # Receipts
    receipts: Mapped[Optional[List[Dict]]] = mapped_column(JSON, default=list)
    # [{name, url, uploaded_at}]

    # Vendor
    vendor_name: Mapped[Optional[str]] = mapped_column(String(255))
    invoice_number: Mapped[Optional[str]] = mapped_column(String(100))

    # Status
    status: Mapped[ExpenseStatus] = mapped_column(SAEnum(ExpenseStatus), default=ExpenseStatus.DRAFT)

    # Approval
    approved_by_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("erm_employees.id"))
    approved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    rejection_reason: Mapped[Optional[str]] = mapped_column(Text)

    # Payment
    paid_date: Mapped[Optional[date]] = mapped_column(Date)
    payment_method: Mapped[Optional[str]] = mapped_column(String(50))
    payment_reference: Mapped[Optional[str]] = mapped_column(String(255))

    # Notes
    notes: Mapped[Optional[str]] = mapped_column(Text)

    # Relationships
    employee: Mapped["Employee"] = relationship("Employee", back_populates="expenses", foreign_keys=[employee_id])
    budget: Mapped[Optional["Budget"]] = relationship("Budget", back_populates="expenses")

    __table_args__ = (
        UniqueConstraint('academy_id', 'expense_number', name='uq_expense_number'),
        Index('ix_erm_expense_employee', 'employee_id'),
        Index('ix_erm_expense_status', 'status'),
        Index('ix_erm_expense_date', 'expense_date'),
        Index('ix_erm_expense_category', 'category'),
    )


class PerformanceReview(Base, TimestampMixin, SoftDeleteMixin):
    """
    Employee performance reviews.
    """
    __tablename__ = "erm_performance_reviews"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    academy_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("academies.id"))
    employee_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("erm_employees.id"))
    reviewer_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("erm_employees.id"))

    # Review period
    review_period_start: Mapped[date] = mapped_column(Date)
    review_period_end: Mapped[date] = mapped_column(Date)
    review_type: Mapped[str] = mapped_column(String(50))  # annual, mid_year, quarterly, probation

    # Rating
    overall_rating: Mapped[PerformanceRating] = mapped_column(SAEnum(PerformanceRating))
    rating_score: Mapped[int] = mapped_column(Integer)  # 1-5

    # Categories
    category_ratings: Mapped[Optional[Dict]] = mapped_column(JSON, default=dict)
    # {category: {rating, score, comments}}

    # Goals
    goals_achieved: Mapped[Optional[List[Dict]]] = mapped_column(JSON, default=list)
    # [{goal, status, comments}]
    goals_for_next_period: Mapped[Optional[List[Dict]]] = mapped_column(JSON, default=list)

    # Feedback
    strengths: Mapped[Optional[str]] = mapped_column(Text)
    areas_for_improvement: Mapped[Optional[str]] = mapped_column(Text)
    reviewer_comments: Mapped[Optional[str]] = mapped_column(Text)
    employee_comments: Mapped[Optional[str]] = mapped_column(Text)

    # Self-assessment
    self_assessment_rating: Mapped[Optional[int]] = mapped_column(Integer)
    self_assessment_comments: Mapped[Optional[str]] = mapped_column(Text)

    # Status
    status: Mapped[str] = mapped_column(String(50), default="draft")
    # draft, in_progress, pending_acknowledgment, completed

    # Dates
    review_meeting_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    submitted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    acknowledged_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    # Compensation
    salary_adjustment_percent: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2))
    bonus_amount: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 2))
    promotion_recommended: Mapped[bool] = mapped_column(Boolean, default=False)
    new_title: Mapped[Optional[str]] = mapped_column(String(255))

    # Relationships
    employee: Mapped["Employee"] = relationship("Employee", back_populates="performance_reviews", foreign_keys=[employee_id])

    __table_args__ = (
        Index('ix_erm_review_employee', 'employee_id'),
        Index('ix_erm_review_reviewer', 'reviewer_id'),
        Index('ix_erm_review_period', 'review_period_start', 'review_period_end'),
        CheckConstraint('rating_score >= 1 AND rating_score <= 5', name='ck_review_score'),
    )


class ResourceSchedule(Base, TimestampMixin, SoftDeleteMixin):
    """
    Resource scheduling (employees, rooms, equipment).
    """
    __tablename__ = "erm_resource_schedules"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    academy_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("academies.id"))

    # Resource
    resource_type: Mapped[ResourceType] = mapped_column(SAEnum(ResourceType))
    resource_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True))  # Employee, Room, or Asset ID

    # Schedule
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[Optional[str]] = mapped_column(Text)

    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    end_time: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    is_all_day: Mapped[bool] = mapped_column(Boolean, default=False)

    # Recurrence
    is_recurring: Mapped[bool] = mapped_column(Boolean, default=False)
    recurrence_rule: Mapped[Optional[str]] = mapped_column(String(255))  # iCal RRULE format
    recurrence_end_date: Mapped[Optional[date]] = mapped_column(Date)

    # Project/task association
    project_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("erm_projects.id"))

    # Booked by
    booked_by_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("erm_employees.id"))

    # Status
    status: Mapped[str] = mapped_column(String(50), default="confirmed")  # tentative, confirmed, cancelled

    __table_args__ = (
        Index('ix_erm_schedule_resource', 'resource_type', 'resource_id'),
        Index('ix_erm_schedule_time', 'start_time', 'end_time'),
        Index('ix_erm_schedule_academy', 'academy_id'),
        CheckConstraint('end_time > start_time', name='ck_schedule_time'),
    )


# ===================== CONFIGURATION =====================

PERFORMANCE_RATING_SCORES = {
    PerformanceRating.EXCEPTIONAL: 5,
    PerformanceRating.EXCEEDS_EXPECTATIONS: 4,
    PerformanceRating.MEETS_EXPECTATIONS: 3,
    PerformanceRating.NEEDS_IMPROVEMENT: 2,
    PerformanceRating.UNSATISFACTORY: 1
}

DEFAULT_LEAVE_POLICIES = {
    EmploymentType.FULL_TIME: {
        LeaveType.ANNUAL: 20,
        LeaveType.SICK: 10,
        LeaveType.PERSONAL: 3,
    },
    EmploymentType.PART_TIME: {
        LeaveType.ANNUAL: 10,
        LeaveType.SICK: 5,
        LeaveType.PERSONAL: 2,
    },
    EmploymentType.CONTRACT: {
        LeaveType.ANNUAL: 0,
        LeaveType.SICK: 5,
        LeaveType.PERSONAL: 0,
    }
}

TASK_STATUS_TRANSITIONS = {
    TaskStatus.BACKLOG: [TaskStatus.TODO],
    TaskStatus.TODO: [TaskStatus.IN_PROGRESS, TaskStatus.CANCELLED],
    TaskStatus.IN_PROGRESS: [TaskStatus.IN_REVIEW, TaskStatus.BLOCKED, TaskStatus.TODO],
    TaskStatus.IN_REVIEW: [TaskStatus.DONE, TaskStatus.IN_PROGRESS],
    TaskStatus.BLOCKED: [TaskStatus.IN_PROGRESS, TaskStatus.CANCELLED],
    TaskStatus.DONE: [],
    TaskStatus.CANCELLED: [TaskStatus.BACKLOG, TaskStatus.TODO]
}

PROJECT_STATUS_TRANSITIONS = {
    ProjectStatus.PLANNING: [ProjectStatus.NOT_STARTED, ProjectStatus.CANCELLED],
    ProjectStatus.NOT_STARTED: [ProjectStatus.IN_PROGRESS, ProjectStatus.CANCELLED],
    ProjectStatus.IN_PROGRESS: [ProjectStatus.ON_HOLD, ProjectStatus.REVIEW, ProjectStatus.CANCELLED],
    ProjectStatus.ON_HOLD: [ProjectStatus.IN_PROGRESS, ProjectStatus.CANCELLED],
    ProjectStatus.REVIEW: [ProjectStatus.COMPLETED, ProjectStatus.IN_PROGRESS],
    ProjectStatus.COMPLETED: [ProjectStatus.ARCHIVED],
    ProjectStatus.CANCELLED: [ProjectStatus.ARCHIVED],
    ProjectStatus.ARCHIVED: []
}


# ===================== HELPER FUNCTIONS =====================

def calculate_leave_balance(employee: Employee, leave_type: LeaveType) -> Decimal:
    """Calculate remaining leave balance for an employee."""
    # This would query leave requests in actual implementation
    if leave_type == LeaveType.ANNUAL:
        return employee.remaining_annual_leave
    elif leave_type == LeaveType.SICK:
        return employee.remaining_sick_leave
    return Decimal("0")


def can_transition_task(current_status: TaskStatus, new_status: TaskStatus) -> bool:
    """Check if task status transition is valid."""
    allowed = TASK_STATUS_TRANSITIONS.get(current_status, [])
    return new_status in allowed


def can_transition_project(current_status: ProjectStatus, new_status: ProjectStatus) -> bool:
    """Check if project status transition is valid."""
    allowed = PROJECT_STATUS_TRANSITIONS.get(current_status, [])
    return new_status in allowed
