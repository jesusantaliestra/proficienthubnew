"""
CRM API Endpoints for ProficientHub B2B Platform.

Provides REST API for CRM functionality including:
- Lead management
- Contact management
- Deal pipeline
- Communication tracking
- Task management
- Campaign management
- External CRM integration
"""

import uuid
from datetime import datetime, date
from decimal import Decimal
from typing import Optional, List, Dict, Any

from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models_crm import (
    LeadSource, LeadStatus, ContactType, CommunicationType, CommunicationDirection,
    TaskPriority, TaskStatus, DealStage, CampaignType, CampaignStatus,
    WorkflowTrigger, ExternalCRMType
)
from app.services.crm_service import CRMService, WorkflowService, CampaignService
from app.services.external_crm_connector import CRMSyncService


router = APIRouter(prefix="/crm", tags=["CRM"])


# ===================== REQUEST/RESPONSE MODELS =====================

class CreateLeadRequest(BaseModel):
    organization_name: str = Field(..., min_length=1, max_length=255)
    contact_name: str = Field(..., min_length=1, max_length=255)
    contact_email: EmailStr
    contact_phone: Optional[str] = None
    contact_title: Optional[str] = None
    website: Optional[str] = None
    industry: Optional[str] = None
    employee_count: Optional[int] = Field(None, ge=1)
    annual_revenue: Optional[Decimal] = Field(None, ge=0)
    source: LeadSource = LeadSource.MANUAL_ENTRY
    source_details: Optional[str] = None
    interested_exams: Optional[List[str]] = None
    estimated_students: Optional[int] = Field(None, ge=1)
    estimated_deal_value: Optional[Decimal] = Field(None, ge=0)
    budget_range: Optional[str] = None
    timeline: Optional[str] = None
    assigned_to_id: Optional[uuid.UUID] = None
    tags: Optional[List[str]] = None
    custom_fields: Optional[Dict[str, Any]] = None


class UpdateLeadRequest(BaseModel):
    organization_name: Optional[str] = Field(None, min_length=1, max_length=255)
    contact_name: Optional[str] = Field(None, min_length=1, max_length=255)
    contact_email: Optional[EmailStr] = None
    contact_phone: Optional[str] = None
    contact_title: Optional[str] = None
    website: Optional[str] = None
    industry: Optional[str] = None
    employee_count: Optional[int] = Field(None, ge=1)
    annual_revenue: Optional[Decimal] = Field(None, ge=0)
    status: Optional[LeadStatus] = None
    source_details: Optional[str] = None
    is_qualified: Optional[bool] = None
    qualification_notes: Optional[str] = None
    interested_exams: Optional[List[str]] = None
    estimated_students: Optional[int] = Field(None, ge=1)
    estimated_deal_value: Optional[Decimal] = Field(None, ge=0)
    budget_range: Optional[str] = None
    timeline: Optional[str] = None
    assigned_to_id: Optional[uuid.UUID] = None
    next_followup_date: Optional[datetime] = None
    tags: Optional[List[str]] = None
    custom_fields: Optional[Dict[str, Any]] = None


class LeadResponse(BaseModel):
    id: uuid.UUID
    organization_name: str
    contact_name: str
    contact_email: str
    contact_phone: Optional[str]
    contact_title: Optional[str]
    website: Optional[str]
    industry: Optional[str]
    employee_count: Optional[int]
    annual_revenue: Optional[Decimal]
    source: str
    status: str
    lead_score: int
    is_qualified: bool
    interested_exams: Optional[List[str]]
    estimated_students: Optional[int]
    estimated_deal_value: Optional[Decimal]
    assigned_to_id: Optional[uuid.UUID]
    first_contact_date: Optional[datetime]
    last_contact_date: Optional[datetime]
    next_followup_date: Optional[datetime]
    tags: Optional[List[str]]
    created_at: datetime

    class Config:
        from_attributes = True


class CreateContactRequest(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    phone: Optional[str] = None
    mobile: Optional[str] = None
    title: Optional[str] = None
    department: Optional[str] = None
    contact_type: ContactType = ContactType.PRIMARY
    is_primary: bool = False
    preferred_contact_method: Optional[str] = None
    preferred_language: str = "en"
    timezone: Optional[str] = None
    linkedin_url: Optional[str] = None
    twitter_handle: Optional[str] = None
    email_opt_in: bool = True
    sms_opt_in: bool = False
    notes: Optional[str] = None
    tags: Optional[List[str]] = None
    lead_id: Optional[uuid.UUID] = None
    academy_id: Optional[uuid.UUID] = None


class ContactResponse(BaseModel):
    id: uuid.UUID
    first_name: str
    last_name: str
    email: str
    phone: Optional[str]
    mobile: Optional[str]
    title: Optional[str]
    department: Optional[str]
    contact_type: str
    is_primary: bool
    preferred_language: str
    lead_id: Optional[uuid.UUID]
    academy_id: Optional[uuid.UUID]
    created_at: datetime

    class Config:
        from_attributes = True


class LogCommunicationRequest(BaseModel):
    type: CommunicationType
    direction: CommunicationDirection
    lead_id: Optional[uuid.UUID] = None
    academy_id: Optional[uuid.UUID] = None
    contact_id: Optional[uuid.UUID] = None
    deal_id: Optional[uuid.UUID] = None
    subject: Optional[str] = None
    content: Optional[str] = None
    summary: Optional[str] = None
    duration_minutes: Optional[int] = Field(None, ge=0)
    outcome: Optional[str] = None
    scheduled_at: Optional[datetime] = None
    attachments: Optional[List[Dict]] = None


class CommunicationResponse(BaseModel):
    id: uuid.UUID
    type: str
    direction: str
    subject: Optional[str]
    content: Optional[str]
    summary: Optional[str]
    duration_minutes: Optional[int]
    outcome: Optional[str]
    lead_id: Optional[uuid.UUID]
    academy_id: Optional[uuid.UUID]
    contact_id: Optional[uuid.UUID]
    deal_id: Optional[uuid.UUID]
    created_at: datetime

    class Config:
        from_attributes = True


class CreateDealRequest(BaseModel):
    lead_id: uuid.UUID
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    amount: Decimal = Field(..., ge=0)
    currency: str = "USD"
    recurring_revenue: Optional[Decimal] = Field(None, ge=0)
    contract_length_months: Optional[int] = Field(None, ge=1)
    products: Optional[List[Dict]] = None
    expected_close_date: Optional[date] = None
    tags: Optional[List[str]] = None
    custom_fields: Optional[Dict[str, Any]] = None


class UpdateDealStageRequest(BaseModel):
    stage: DealStage
    notes: Optional[str] = None


class DealResponse(BaseModel):
    id: uuid.UUID
    lead_id: uuid.UUID
    academy_id: Optional[uuid.UUID]
    name: str
    description: Optional[str]
    stage: str
    probability: int
    amount: Decimal
    currency: str
    recurring_revenue: Optional[Decimal]
    contract_length_months: Optional[int]
    expected_close_date: Optional[date]
    actual_close_date: Optional[date]
    won_reason: Optional[str]
    lost_reason: Optional[str]
    tags: Optional[List[str]]
    created_at: datetime

    class Config:
        from_attributes = True


class CreateTaskRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    task_type: str = "follow_up"
    priority: TaskPriority = TaskPriority.MEDIUM
    lead_id: Optional[uuid.UUID] = None
    academy_id: Optional[uuid.UUID] = None
    deal_id: Optional[uuid.UUID] = None
    due_date: Optional[datetime] = None
    reminder_at: Optional[datetime] = None
    is_recurring: bool = False
    recurrence_pattern: Optional[str] = None


class TaskResponse(BaseModel):
    id: uuid.UUID
    title: str
    description: Optional[str]
    task_type: str
    priority: str
    status: str
    lead_id: Optional[uuid.UUID]
    academy_id: Optional[uuid.UUID]
    deal_id: Optional[uuid.UUID]
    assigned_to_id: uuid.UUID
    due_date: Optional[datetime]
    completed_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


class CreateCampaignRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    type: CampaignType
    target_audience: Optional[Dict] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    budget: Optional[Decimal] = Field(None, ge=0)
    goal_leads: Optional[int] = Field(None, ge=0)
    goal_conversions: Optional[int] = Field(None, ge=0)
    goal_revenue: Optional[Decimal] = Field(None, ge=0)
    content_template: Optional[Dict] = None


class CampaignResponse(BaseModel):
    id: uuid.UUID
    name: str
    description: Optional[str]
    type: str
    status: str
    start_date: Optional[datetime]
    end_date: Optional[datetime]
    budget: Optional[Decimal]
    leads_generated: int
    conversions: int
    revenue_generated: Decimal
    created_at: datetime

    class Config:
        from_attributes = True


class SetupIntegrationRequest(BaseModel):
    crm_type: ExternalCRMType
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    api_key: Optional[str] = None
    api_secret: Optional[str] = None
    instance_url: Optional[str] = None
    webhook_url: Optional[str] = None
    webhook_secret: Optional[str] = None
    sync_direction: str = "bidirectional"
    sync_interval_minutes: int = 15
    sync_leads: bool = True
    sync_contacts: bool = True
    sync_deals: bool = True


class IntegrationResponse(BaseModel):
    id: uuid.UUID
    academy_id: uuid.UUID
    crm_type: str
    is_active: bool
    sync_direction: str
    sync_interval_minutes: int
    last_sync_at: Optional[datetime]
    last_sync_status: Optional[str]
    records_synced: int
    created_at: datetime

    class Config:
        from_attributes = True


# ===================== DEPENDENCY INJECTION =====================

async def get_session():
    """Get database session - mock for now."""
    # In production, this would get from dependency injection
    pass


async def get_current_user_id():
    """Get current user ID - mock for now."""
    return uuid.uuid4()


# ===================== LEAD ENDPOINTS =====================

@router.post("/leads", response_model=LeadResponse)
async def create_lead(
    request: CreateLeadRequest,
    # session: AsyncSession = Depends(get_session),
    # user_id: uuid.UUID = Depends(get_current_user_id)
):
    """Create a new lead."""
    # service = CRMService(session)
    # lead = await service.create_lead(**request.dict())
    # return lead
    return {"message": "Lead creation endpoint - implement with actual session"}


@router.get("/leads", response_model=Dict[str, Any])
async def list_leads(
    status: Optional[LeadStatus] = None,
    source: Optional[LeadSource] = None,
    assigned_to_id: Optional[uuid.UUID] = None,
    min_score: Optional[int] = Query(None, ge=0, le=100),
    search: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100)
    # session: AsyncSession = Depends(get_session)
):
    """List leads with filtering and pagination."""
    # service = CRMService(session)
    # leads, total = await service.list_leads(
    #     status=status, source=source, assigned_to_id=assigned_to_id,
    #     min_score=min_score, search=search, page=page, page_size=page_size
    # )
    return {
        "items": [],
        "total": 0,
        "page": page,
        "page_size": page_size,
        "total_pages": 0
    }


@router.get("/leads/{lead_id}", response_model=LeadResponse)
async def get_lead(
    lead_id: uuid.UUID
    # session: AsyncSession = Depends(get_session)
):
    """Get a lead by ID."""
    # service = CRMService(session)
    # lead = await service.get_lead(lead_id)
    # if not lead:
    #     raise HTTPException(status_code=404, detail="Lead not found")
    # return lead
    raise HTTPException(status_code=404, detail="Lead not found")


@router.patch("/leads/{lead_id}", response_model=LeadResponse)
async def update_lead(
    lead_id: uuid.UUID,
    request: UpdateLeadRequest
    # session: AsyncSession = Depends(get_session)
):
    """Update a lead."""
    # service = CRMService(session)
    # updates = request.dict(exclude_unset=True)
    # lead = await service.update_lead(lead_id, **updates)
    # return lead
    raise HTTPException(status_code=404, detail="Lead not found")


@router.post("/leads/{lead_id}/convert")
async def convert_lead(
    lead_id: uuid.UUID,
    academy_id: uuid.UUID
    # session: AsyncSession = Depends(get_session)
):
    """Convert a lead to a customer (academy)."""
    # service = CRMService(session)
    # lead = await service.convert_lead_to_customer(lead_id, academy_id)
    return {"message": "Lead converted", "lead_id": str(lead_id), "academy_id": str(academy_id)}


@router.post("/leads/{lead_id}/lost")
async def mark_lead_lost(
    lead_id: uuid.UUID,
    reason: str
    # session: AsyncSession = Depends(get_session)
):
    """Mark a lead as lost."""
    # service = CRMService(session)
    # lead = await service.mark_lead_lost(lead_id, reason)
    return {"message": "Lead marked as lost", "lead_id": str(lead_id)}


# ===================== CONTACT ENDPOINTS =====================

@router.post("/contacts", response_model=ContactResponse)
async def create_contact(
    request: CreateContactRequest
    # session: AsyncSession = Depends(get_session)
):
    """Create a new contact."""
    return {"message": "Contact creation endpoint"}


@router.get("/contacts", response_model=Dict[str, Any])
async def list_contacts(
    lead_id: Optional[uuid.UUID] = None,
    academy_id: Optional[uuid.UUID] = None,
    contact_type: Optional[ContactType] = None,
    search: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100)
):
    """List contacts with filtering."""
    return {
        "items": [],
        "total": 0,
        "page": page,
        "page_size": page_size
    }


@router.get("/contacts/{contact_id}", response_model=ContactResponse)
async def get_contact(contact_id: uuid.UUID):
    """Get a contact by ID."""
    raise HTTPException(status_code=404, detail="Contact not found")


# ===================== COMMUNICATION ENDPOINTS =====================

@router.post("/communications", response_model=CommunicationResponse)
async def log_communication(
    request: LogCommunicationRequest
    # session: AsyncSession = Depends(get_session),
    # user_id: uuid.UUID = Depends(get_current_user_id)
):
    """Log a communication interaction."""
    return {"message": "Communication logged"}


@router.get("/communications", response_model=Dict[str, Any])
async def get_communication_history(
    lead_id: Optional[uuid.UUID] = None,
    academy_id: Optional[uuid.UUID] = None,
    contact_id: Optional[uuid.UUID] = None,
    type: Optional[CommunicationType] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100)
):
    """Get communication history."""
    return {
        "items": [],
        "total": 0,
        "page": page,
        "page_size": page_size
    }


# ===================== DEAL ENDPOINTS =====================

@router.post("/deals", response_model=DealResponse)
async def create_deal(
    request: CreateDealRequest
    # session: AsyncSession = Depends(get_session),
    # user_id: uuid.UUID = Depends(get_current_user_id)
):
    """Create a new deal."""
    return {"message": "Deal creation endpoint"}


@router.get("/deals", response_model=Dict[str, Any])
async def list_deals(
    stage: Optional[DealStage] = None,
    owner_id: Optional[uuid.UUID] = None,
    lead_id: Optional[uuid.UUID] = None,
    min_amount: Optional[Decimal] = None,
    max_amount: Optional[Decimal] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100)
):
    """List deals with filtering."""
    return {
        "items": [],
        "total": 0,
        "page": page,
        "page_size": page_size
    }


@router.get("/deals/{deal_id}", response_model=DealResponse)
async def get_deal(deal_id: uuid.UUID):
    """Get a deal by ID."""
    raise HTTPException(status_code=404, detail="Deal not found")


@router.patch("/deals/{deal_id}/stage", response_model=DealResponse)
async def update_deal_stage(
    deal_id: uuid.UUID,
    request: UpdateDealStageRequest
):
    """Update deal stage."""
    return {"message": "Deal stage updated"}


@router.get("/deals/pipeline/summary")
async def get_pipeline_summary():
    """Get sales pipeline summary."""
    return {
        "stages": {},
        "weighted_pipeline_value": 0,
        "total_deals": 0,
        "total_pipeline_value": 0
    }


# ===================== TASK ENDPOINTS =====================

@router.post("/tasks", response_model=TaskResponse)
async def create_task(
    request: CreateTaskRequest
    # session: AsyncSession = Depends(get_session),
    # user_id: uuid.UUID = Depends(get_current_user_id)
):
    """Create a CRM task."""
    return {"message": "Task creation endpoint"}


@router.get("/tasks", response_model=Dict[str, Any])
async def list_tasks(
    assigned_to_id: Optional[uuid.UUID] = None,
    status: Optional[TaskStatus] = None,
    lead_id: Optional[uuid.UUID] = None,
    deal_id: Optional[uuid.UUID] = None,
    due_before: Optional[datetime] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100)
):
    """List tasks with filtering."""
    return {
        "items": [],
        "total": 0,
        "page": page,
        "page_size": page_size
    }


@router.post("/tasks/{task_id}/complete")
async def complete_task(
    task_id: uuid.UUID,
    outcome: Optional[str] = None
):
    """Mark a task as completed."""
    return {"message": "Task completed", "task_id": str(task_id)}


# ===================== CAMPAIGN ENDPOINTS =====================

@router.post("/campaigns", response_model=CampaignResponse)
async def create_campaign(
    request: CreateCampaignRequest
    # session: AsyncSession = Depends(get_session),
    # user_id: uuid.UUID = Depends(get_current_user_id)
):
    """Create a new campaign."""
    return {"message": "Campaign creation endpoint"}


@router.get("/campaigns", response_model=Dict[str, Any])
async def list_campaigns(
    status: Optional[CampaignStatus] = None,
    type: Optional[CampaignType] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100)
):
    """List campaigns."""
    return {
        "items": [],
        "total": 0,
        "page": page,
        "page_size": page_size
    }


@router.get("/campaigns/{campaign_id}", response_model=CampaignResponse)
async def get_campaign(campaign_id: uuid.UUID):
    """Get a campaign by ID."""
    raise HTTPException(status_code=404, detail="Campaign not found")


@router.post("/campaigns/{campaign_id}/members")
async def add_campaign_members(
    campaign_id: uuid.UUID,
    lead_ids: List[uuid.UUID]
):
    """Add leads to a campaign."""
    return {"message": "Members added", "count": len(lead_ids)}


@router.get("/campaigns/{campaign_id}/analytics")
async def get_campaign_analytics(campaign_id: uuid.UUID):
    """Get campaign analytics."""
    return {
        "campaign_id": str(campaign_id),
        "metrics": {
            "total_members": 0,
            "emails_sent": 0,
            "emails_opened": 0,
            "open_rate": 0,
            "click_rate": 0,
            "conversions": 0
        }
    }


# ===================== ANALYTICS ENDPOINTS =====================

@router.get("/analytics/leads")
async def get_lead_analytics(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
):
    """Get lead analytics."""
    return {
        "period": {},
        "total_leads": 0,
        "leads_by_status": {},
        "leads_by_source": {},
        "conversion_rate": 0,
        "average_lead_score": 0
    }


@router.get("/analytics/sales")
async def get_sales_analytics(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
):
    """Get sales analytics."""
    return {
        "period": {},
        "total_deals": 0,
        "total_value": 0,
        "won_deals": 0,
        "won_value": 0,
        "lost_deals": 0,
        "average_deal_size": 0,
        "win_rate": 0,
        "average_sales_cycle_days": 0
    }


# ===================== INTEGRATION ENDPOINTS =====================

@router.post("/integrations/{academy_id}", response_model=IntegrationResponse)
async def setup_integration(
    academy_id: uuid.UUID,
    request: SetupIntegrationRequest
):
    """Set up a new CRM integration."""
    return {"message": "Integration setup endpoint"}


@router.get("/integrations/{academy_id}")
async def get_integrations(academy_id: uuid.UUID):
    """Get CRM integrations for an academy."""
    return {"integrations": []}


@router.post("/integrations/{academy_id}/sync")
async def run_sync(
    academy_id: uuid.UUID,
    background_tasks: BackgroundTasks,
    crm_type: Optional[ExternalCRMType] = None
):
    """Run CRM synchronization."""
    # background_tasks.add_task(sync_service.run_sync, academy_id, crm_type)
    return {"message": "Sync started", "academy_id": str(academy_id)}


@router.delete("/integrations/{academy_id}/{crm_type}")
async def delete_integration(
    academy_id: uuid.UUID,
    crm_type: ExternalCRMType
):
    """Delete a CRM integration."""
    return {"message": "Integration deleted"}


# ===================== WORKFLOW ENDPOINTS =====================

@router.post("/workflows")
async def create_workflow(
    name: str,
    trigger: WorkflowTrigger,
    actions: List[Dict],
    trigger_conditions: Optional[Dict] = None,
    description: Optional[str] = None
    # session: AsyncSession = Depends(get_session),
    # user_id: uuid.UUID = Depends(get_current_user_id)
):
    """Create a new workflow."""
    return {"message": "Workflow creation endpoint"}


@router.get("/workflows")
async def list_workflows(
    is_active: Optional[bool] = None,
    trigger: Optional[WorkflowTrigger] = None
):
    """List workflows."""
    return {"workflows": []}


@router.get("/workflows/{workflow_id}")
async def get_workflow(workflow_id: uuid.UUID):
    """Get a workflow by ID."""
    raise HTTPException(status_code=404, detail="Workflow not found")


@router.patch("/workflows/{workflow_id}/toggle")
async def toggle_workflow(workflow_id: uuid.UUID):
    """Toggle workflow active status."""
    return {"message": "Workflow toggled"}


@router.get("/workflows/{workflow_id}/executions")
async def get_workflow_executions(
    workflow_id: uuid.UUID,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100)
):
    """Get workflow execution history."""
    return {
        "executions": [],
        "total": 0,
        "page": page,
        "page_size": page_size
    }
