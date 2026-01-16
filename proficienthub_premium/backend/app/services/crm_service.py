"""
CRM Service for ProficientHub B2B Platform.

Provides comprehensive CRM functionality including:
- Lead management and scoring
- Contact management
- Deal pipeline management
- Communication tracking
- Campaign management
- Workflow automation
- External CRM integration
"""

import uuid
import asyncio
from datetime import datetime, timedelta, date
from decimal import Decimal
from typing import Optional, List, Dict, Any, Tuple

import structlog
from sqlalchemy import select, update, delete, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.models_crm import (
    CRMLead, CRMContact, CRMCommunication, CRMDeal, CRMTask,
    CRMCampaign, CRMCampaignMember, CRMWorkflow, CRMWorkflowExecution,
    ExternalCRMIntegration, CRMEmailTemplate,
    LeadSource, LeadStatus, ContactType, CommunicationType, CommunicationDirection,
    TaskPriority, TaskStatus, DealStage, CampaignType, CampaignStatus,
    WorkflowTrigger, WorkflowActionType, ExternalCRMType,
    calculate_lead_score, get_next_deal_stage, DEAL_STAGE_PROBABILITIES
)

logger = structlog.get_logger()


class CRMService:
    """Main CRM service for managing leads, contacts, deals, and communications."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.workflow_service = WorkflowService(session)

    # ===================== LEAD MANAGEMENT =====================

    async def create_lead(
        self,
        organization_name: str,
        contact_name: str,
        contact_email: str,
        source: LeadSource = LeadSource.MANUAL_ENTRY,
        **kwargs
    ) -> CRMLead:
        """Create a new lead."""
        lead = CRMLead(
            organization_name=organization_name,
            contact_name=contact_name,
            contact_email=contact_email,
            source=source,
            status=LeadStatus.NEW,
            first_contact_date=datetime.utcnow(),
            **kwargs
        )

        # Calculate initial lead score
        lead.lead_score = calculate_lead_score(lead)

        self.session.add(lead)
        await self.session.commit()
        await self.session.refresh(lead)

        # Trigger workflow
        await self.workflow_service.trigger_workflow(
            WorkflowTrigger.LEAD_CREATED,
            lead_id=lead.id,
            data={"lead": lead}
        )

        logger.info("Lead created", lead_id=str(lead.id), organization=organization_name)
        return lead

    async def update_lead(self, lead_id: uuid.UUID, **updates) -> CRMLead:
        """Update a lead."""
        lead = await self.get_lead(lead_id)
        if not lead:
            raise ValueError(f"Lead {lead_id} not found")

        old_status = lead.status

        for key, value in updates.items():
            if hasattr(lead, key):
                setattr(lead, key, value)

        # Recalculate score if relevant fields changed
        score_fields = ['employee_count', 'interested_exams', 'estimated_students', 'timeline']
        if any(f in updates for f in score_fields):
            lead.lead_score = calculate_lead_score(lead)

        lead.last_contact_date = datetime.utcnow()

        await self.session.commit()
        await self.session.refresh(lead)

        # Trigger workflow if status changed
        if 'status' in updates and old_status != lead.status:
            await self.workflow_service.trigger_workflow(
                WorkflowTrigger.LEAD_STATUS_CHANGED,
                lead_id=lead.id,
                data={"old_status": old_status.value, "new_status": lead.status.value}
            )

        return lead

    async def get_lead(self, lead_id: uuid.UUID) -> Optional[CRMLead]:
        """Get a lead by ID."""
        result = await self.session.execute(
            select(CRMLead)
            .options(
                selectinload(CRMLead.contacts),
                selectinload(CRMLead.communications),
                selectinload(CRMLead.tasks),
                selectinload(CRMLead.deals)
            )
            .where(CRMLead.id == lead_id, CRMLead.deleted_at.is_(None))
        )
        return result.scalar_one_or_none()

    async def list_leads(
        self,
        status: Optional[LeadStatus] = None,
        source: Optional[LeadSource] = None,
        assigned_to_id: Optional[uuid.UUID] = None,
        min_score: Optional[int] = None,
        search: Optional[str] = None,
        page: int = 1,
        page_size: int = 20
    ) -> Tuple[List[CRMLead], int]:
        """List leads with filtering and pagination."""
        query = select(CRMLead).where(CRMLead.deleted_at.is_(None))

        if status:
            query = query.where(CRMLead.status == status)
        if source:
            query = query.where(CRMLead.source == source)
        if assigned_to_id:
            query = query.where(CRMLead.assigned_to_id == assigned_to_id)
        if min_score:
            query = query.where(CRMLead.lead_score >= min_score)
        if search:
            search_filter = or_(
                CRMLead.organization_name.ilike(f"%{search}%"),
                CRMLead.contact_name.ilike(f"%{search}%"),
                CRMLead.contact_email.ilike(f"%{search}%")
            )
            query = query.where(search_filter)

        # Count total
        count_query = select(func.count()).select_from(query.subquery())
        total = (await self.session.execute(count_query)).scalar()

        # Paginate
        query = query.order_by(CRMLead.created_at.desc())
        query = query.offset((page - 1) * page_size).limit(page_size)

        result = await self.session.execute(query)
        leads = list(result.scalars().all())

        return leads, total

    async def convert_lead_to_customer(
        self,
        lead_id: uuid.UUID,
        academy_id: uuid.UUID
    ) -> CRMLead:
        """Convert a lead to a customer (academy)."""
        lead = await self.get_lead(lead_id)
        if not lead:
            raise ValueError(f"Lead {lead_id} not found")

        lead.status = LeadStatus.WON
        lead.converted_at = datetime.utcnow()
        lead.converted_to_academy_id = academy_id

        await self.session.commit()
        await self.session.refresh(lead)

        logger.info("Lead converted", lead_id=str(lead_id), academy_id=str(academy_id))
        return lead

    async def mark_lead_lost(
        self,
        lead_id: uuid.UUID,
        reason: str
    ) -> CRMLead:
        """Mark a lead as lost."""
        lead = await self.get_lead(lead_id)
        if not lead:
            raise ValueError(f"Lead {lead_id} not found")

        lead.status = LeadStatus.LOST
        lead.lost_reason = reason

        await self.session.commit()
        await self.session.refresh(lead)

        return lead

    # ===================== CONTACT MANAGEMENT =====================

    async def create_contact(
        self,
        first_name: str,
        last_name: str,
        email: str,
        lead_id: Optional[uuid.UUID] = None,
        academy_id: Optional[uuid.UUID] = None,
        **kwargs
    ) -> CRMContact:
        """Create a new contact."""
        contact = CRMContact(
            first_name=first_name,
            last_name=last_name,
            email=email,
            lead_id=lead_id,
            academy_id=academy_id,
            **kwargs
        )

        self.session.add(contact)
        await self.session.commit()
        await self.session.refresh(contact)

        return contact

    async def get_contact(self, contact_id: uuid.UUID) -> Optional[CRMContact]:
        """Get a contact by ID."""
        result = await self.session.execute(
            select(CRMContact)
            .options(selectinload(CRMContact.communications))
            .where(CRMContact.id == contact_id, CRMContact.deleted_at.is_(None))
        )
        return result.scalar_one_or_none()

    async def list_contacts(
        self,
        lead_id: Optional[uuid.UUID] = None,
        academy_id: Optional[uuid.UUID] = None,
        contact_type: Optional[ContactType] = None,
        search: Optional[str] = None,
        page: int = 1,
        page_size: int = 20
    ) -> Tuple[List[CRMContact], int]:
        """List contacts with filtering."""
        query = select(CRMContact).where(CRMContact.deleted_at.is_(None))

        if lead_id:
            query = query.where(CRMContact.lead_id == lead_id)
        if academy_id:
            query = query.where(CRMContact.academy_id == academy_id)
        if contact_type:
            query = query.where(CRMContact.contact_type == contact_type)
        if search:
            search_filter = or_(
                CRMContact.first_name.ilike(f"%{search}%"),
                CRMContact.last_name.ilike(f"%{search}%"),
                CRMContact.email.ilike(f"%{search}%")
            )
            query = query.where(search_filter)

        count_query = select(func.count()).select_from(query.subquery())
        total = (await self.session.execute(count_query)).scalar()

        query = query.order_by(CRMContact.created_at.desc())
        query = query.offset((page - 1) * page_size).limit(page_size)

        result = await self.session.execute(query)
        contacts = list(result.scalars().all())

        return contacts, total

    # ===================== COMMUNICATION TRACKING =====================

    async def log_communication(
        self,
        user_id: uuid.UUID,
        type: CommunicationType,
        direction: CommunicationDirection,
        lead_id: Optional[uuid.UUID] = None,
        academy_id: Optional[uuid.UUID] = None,
        contact_id: Optional[uuid.UUID] = None,
        deal_id: Optional[uuid.UUID] = None,
        subject: Optional[str] = None,
        content: Optional[str] = None,
        **kwargs
    ) -> CRMCommunication:
        """Log a communication interaction."""
        communication = CRMCommunication(
            user_id=user_id,
            type=type,
            direction=direction,
            lead_id=lead_id,
            academy_id=academy_id,
            contact_id=contact_id,
            deal_id=deal_id,
            subject=subject,
            content=content,
            completed_at=datetime.utcnow(),
            **kwargs
        )

        self.session.add(communication)

        # Update last contact date on lead if applicable
        if lead_id:
            await self.session.execute(
                update(CRMLead)
                .where(CRMLead.id == lead_id)
                .values(last_contact_date=datetime.utcnow())
            )

        await self.session.commit()
        await self.session.refresh(communication)

        return communication

    async def get_communication_history(
        self,
        lead_id: Optional[uuid.UUID] = None,
        academy_id: Optional[uuid.UUID] = None,
        contact_id: Optional[uuid.UUID] = None,
        type: Optional[CommunicationType] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        page: int = 1,
        page_size: int = 50
    ) -> Tuple[List[CRMCommunication], int]:
        """Get communication history with filtering."""
        query = select(CRMCommunication)

        if lead_id:
            query = query.where(CRMCommunication.lead_id == lead_id)
        if academy_id:
            query = query.where(CRMCommunication.academy_id == academy_id)
        if contact_id:
            query = query.where(CRMCommunication.contact_id == contact_id)
        if type:
            query = query.where(CRMCommunication.type == type)
        if start_date:
            query = query.where(CRMCommunication.created_at >= start_date)
        if end_date:
            query = query.where(CRMCommunication.created_at <= end_date)

        count_query = select(func.count()).select_from(query.subquery())
        total = (await self.session.execute(count_query)).scalar()

        query = query.order_by(CRMCommunication.created_at.desc())
        query = query.offset((page - 1) * page_size).limit(page_size)

        result = await self.session.execute(query)
        communications = list(result.scalars().all())

        return communications, total

    # ===================== DEAL MANAGEMENT =====================

    async def create_deal(
        self,
        lead_id: uuid.UUID,
        owner_id: uuid.UUID,
        name: str,
        amount: Decimal,
        **kwargs
    ) -> CRMDeal:
        """Create a new deal in the pipeline."""
        deal = CRMDeal(
            lead_id=lead_id,
            owner_id=owner_id,
            name=name,
            amount=amount,
            stage=DealStage.PROSPECTING,
            probability=DEAL_STAGE_PROBABILITIES[DealStage.PROSPECTING],
            stage_history=[{
                "stage": DealStage.PROSPECTING.value,
                "entered_at": datetime.utcnow().isoformat()
            }],
            **kwargs
        )

        self.session.add(deal)
        await self.session.commit()
        await self.session.refresh(deal)

        # Trigger workflow
        await self.workflow_service.trigger_workflow(
            WorkflowTrigger.DEAL_CREATED,
            lead_id=lead_id,
            deal_id=deal.id,
            data={"deal": deal}
        )

        logger.info("Deal created", deal_id=str(deal.id), amount=str(amount))
        return deal

    async def update_deal_stage(
        self,
        deal_id: uuid.UUID,
        new_stage: DealStage,
        notes: Optional[str] = None
    ) -> CRMDeal:
        """Update deal stage in the pipeline."""
        deal = await self.get_deal(deal_id)
        if not deal:
            raise ValueError(f"Deal {deal_id} not found")

        old_stage = deal.stage

        # Update stage history
        stage_history = deal.stage_history or []
        if stage_history:
            # Mark exit time for previous stage
            stage_history[-1]["exited_at"] = datetime.utcnow().isoformat()
            entered_at = datetime.fromisoformat(stage_history[-1]["entered_at"])
            stage_history[-1]["duration_days"] = (datetime.utcnow() - entered_at).days

        # Add new stage
        stage_history.append({
            "stage": new_stage.value,
            "entered_at": datetime.utcnow().isoformat()
        })

        deal.stage = new_stage
        deal.probability = DEAL_STAGE_PROBABILITIES[new_stage]
        deal.stage_history = stage_history

        if notes:
            deal.notes = (deal.notes or "") + f"\n[{datetime.utcnow().isoformat()}] Stage changed: {notes}"

        # Handle won/lost
        if new_stage == DealStage.CLOSED_WON:
            deal.actual_close_date = date.today()
            await self.workflow_service.trigger_workflow(
                WorkflowTrigger.DEAL_WON,
                lead_id=deal.lead_id,
                deal_id=deal.id
            )
        elif new_stage == DealStage.CLOSED_LOST:
            deal.actual_close_date = date.today()
            await self.workflow_service.trigger_workflow(
                WorkflowTrigger.DEAL_LOST,
                lead_id=deal.lead_id,
                deal_id=deal.id
            )
        else:
            await self.workflow_service.trigger_workflow(
                WorkflowTrigger.DEAL_STAGE_CHANGED,
                lead_id=deal.lead_id,
                deal_id=deal.id,
                data={"old_stage": old_stage.value, "new_stage": new_stage.value}
            )

        await self.session.commit()
        await self.session.refresh(deal)

        return deal

    async def get_deal(self, deal_id: uuid.UUID) -> Optional[CRMDeal]:
        """Get a deal by ID."""
        result = await self.session.execute(
            select(CRMDeal)
            .options(
                selectinload(CRMDeal.communications),
                selectinload(CRMDeal.tasks)
            )
            .where(CRMDeal.id == deal_id, CRMDeal.deleted_at.is_(None))
        )
        return result.scalar_one_or_none()

    async def list_deals(
        self,
        stage: Optional[DealStage] = None,
        owner_id: Optional[uuid.UUID] = None,
        lead_id: Optional[uuid.UUID] = None,
        min_amount: Optional[Decimal] = None,
        max_amount: Optional[Decimal] = None,
        page: int = 1,
        page_size: int = 20
    ) -> Tuple[List[CRMDeal], int]:
        """List deals with filtering."""
        query = select(CRMDeal).where(CRMDeal.deleted_at.is_(None))

        if stage:
            query = query.where(CRMDeal.stage == stage)
        if owner_id:
            query = query.where(CRMDeal.owner_id == owner_id)
        if lead_id:
            query = query.where(CRMDeal.lead_id == lead_id)
        if min_amount:
            query = query.where(CRMDeal.amount >= min_amount)
        if max_amount:
            query = query.where(CRMDeal.amount <= max_amount)

        count_query = select(func.count()).select_from(query.subquery())
        total = (await self.session.execute(count_query)).scalar()

        query = query.order_by(CRMDeal.created_at.desc())
        query = query.offset((page - 1) * page_size).limit(page_size)

        result = await self.session.execute(query)
        deals = list(result.scalars().all())

        return deals, total

    async def get_pipeline_summary(self) -> Dict[str, Any]:
        """Get sales pipeline summary."""
        result = await self.session.execute(
            select(
                CRMDeal.stage,
                func.count(CRMDeal.id).label('count'),
                func.sum(CRMDeal.amount).label('total_value'),
                func.avg(CRMDeal.amount).label('avg_value')
            )
            .where(CRMDeal.deleted_at.is_(None))
            .group_by(CRMDeal.stage)
        )

        stages_data = {}
        for row in result:
            stages_data[row.stage.value] = {
                "count": row.count,
                "total_value": float(row.total_value or 0),
                "avg_value": float(row.avg_value or 0),
                "probability": DEAL_STAGE_PROBABILITIES[row.stage]
            }

        # Calculate weighted pipeline value
        weighted_value = sum(
            data["total_value"] * (data["probability"] / 100)
            for data in stages_data.values()
        )

        return {
            "stages": stages_data,
            "weighted_pipeline_value": weighted_value,
            "total_deals": sum(d["count"] for d in stages_data.values()),
            "total_pipeline_value": sum(d["total_value"] for d in stages_data.values())
        }

    # ===================== TASK MANAGEMENT =====================

    async def create_task(
        self,
        title: str,
        assigned_to_id: uuid.UUID,
        created_by_id: uuid.UUID,
        task_type: str = "follow_up",
        lead_id: Optional[uuid.UUID] = None,
        academy_id: Optional[uuid.UUID] = None,
        deal_id: Optional[uuid.UUID] = None,
        **kwargs
    ) -> CRMTask:
        """Create a CRM task."""
        task = CRMTask(
            title=title,
            assigned_to_id=assigned_to_id,
            created_by_id=created_by_id,
            task_type=task_type,
            lead_id=lead_id,
            academy_id=academy_id,
            deal_id=deal_id,
            **kwargs
        )

        self.session.add(task)
        await self.session.commit()
        await self.session.refresh(task)

        return task

    async def complete_task(
        self,
        task_id: uuid.UUID,
        outcome: Optional[str] = None
    ) -> CRMTask:
        """Mark a task as completed."""
        result = await self.session.execute(
            select(CRMTask).where(CRMTask.id == task_id)
        )
        task = result.scalar_one_or_none()

        if not task:
            raise ValueError(f"Task {task_id} not found")

        task.status = TaskStatus.COMPLETED
        task.completed_at = datetime.utcnow()
        if outcome:
            task.outcome = outcome

        await self.session.commit()
        await self.session.refresh(task)

        return task

    async def list_tasks(
        self,
        assigned_to_id: Optional[uuid.UUID] = None,
        status: Optional[TaskStatus] = None,
        lead_id: Optional[uuid.UUID] = None,
        deal_id: Optional[uuid.UUID] = None,
        due_before: Optional[datetime] = None,
        page: int = 1,
        page_size: int = 20
    ) -> Tuple[List[CRMTask], int]:
        """List tasks with filtering."""
        query = select(CRMTask).where(CRMTask.deleted_at.is_(None))

        if assigned_to_id:
            query = query.where(CRMTask.assigned_to_id == assigned_to_id)
        if status:
            query = query.where(CRMTask.status == status)
        if lead_id:
            query = query.where(CRMTask.lead_id == lead_id)
        if deal_id:
            query = query.where(CRMTask.deal_id == deal_id)
        if due_before:
            query = query.where(CRMTask.due_date <= due_before)

        count_query = select(func.count()).select_from(query.subquery())
        total = (await self.session.execute(count_query)).scalar()

        query = query.order_by(CRMTask.due_date.asc().nulls_last())
        query = query.offset((page - 1) * page_size).limit(page_size)

        result = await self.session.execute(query)
        tasks = list(result.scalars().all())

        return tasks, total

    # ===================== ANALYTICS =====================

    async def get_lead_analytics(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get lead analytics."""
        if not start_date:
            start_date = datetime.utcnow() - timedelta(days=30)
        if not end_date:
            end_date = datetime.utcnow()

        # Leads by status
        status_query = select(
            CRMLead.status,
            func.count(CRMLead.id).label('count')
        ).where(
            CRMLead.created_at >= start_date,
            CRMLead.created_at <= end_date,
            CRMLead.deleted_at.is_(None)
        ).group_by(CRMLead.status)

        status_result = await self.session.execute(status_query)
        leads_by_status = {row.status.value: row.count for row in status_result}

        # Leads by source
        source_query = select(
            CRMLead.source,
            func.count(CRMLead.id).label('count')
        ).where(
            CRMLead.created_at >= start_date,
            CRMLead.created_at <= end_date,
            CRMLead.deleted_at.is_(None)
        ).group_by(CRMLead.source)

        source_result = await self.session.execute(source_query)
        leads_by_source = {row.source.value: row.count for row in source_result}

        # Conversion rate
        total_leads = sum(leads_by_status.values())
        won_leads = leads_by_status.get(LeadStatus.WON.value, 0)
        conversion_rate = (won_leads / total_leads * 100) if total_leads > 0 else 0

        # Average lead score
        avg_score_result = await self.session.execute(
            select(func.avg(CRMLead.lead_score)).where(
                CRMLead.created_at >= start_date,
                CRMLead.created_at <= end_date,
                CRMLead.deleted_at.is_(None)
            )
        )
        avg_score = avg_score_result.scalar() or 0

        return {
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            },
            "total_leads": total_leads,
            "leads_by_status": leads_by_status,
            "leads_by_source": leads_by_source,
            "conversion_rate": round(conversion_rate, 2),
            "average_lead_score": round(avg_score, 1)
        }


class WorkflowService:
    """Service for managing CRM workflow automation."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def trigger_workflow(
        self,
        trigger: WorkflowTrigger,
        lead_id: Optional[uuid.UUID] = None,
        deal_id: Optional[uuid.UUID] = None,
        academy_id: Optional[uuid.UUID] = None,
        data: Optional[Dict] = None
    ) -> List[CRMWorkflowExecution]:
        """Trigger workflows for a specific event."""
        # Find active workflows for this trigger
        result = await self.session.execute(
            select(CRMWorkflow).where(
                CRMWorkflow.trigger == trigger,
                CRMWorkflow.is_active == True,
                CRMWorkflow.deleted_at.is_(None)
            )
        )
        workflows = list(result.scalars().all())

        executions = []
        for workflow in workflows:
            # Check conditions
            if not self._check_conditions(workflow.trigger_conditions, data):
                continue

            execution = await self._execute_workflow(
                workflow,
                lead_id=lead_id,
                deal_id=deal_id,
                academy_id=academy_id,
                trigger_data=data
            )
            executions.append(execution)

        return executions

    def _check_conditions(
        self,
        conditions: Optional[Dict],
        data: Optional[Dict]
    ) -> bool:
        """Check if workflow conditions are met."""
        if not conditions:
            return True

        if not data:
            return False

        # Simple condition evaluation
        for field, condition in conditions.items():
            if isinstance(condition, dict):
                operator = condition.get("operator", "equals")
                value = condition.get("value")

                actual_value = data.get(field)
                if operator == "equals" and actual_value != value:
                    return False
                elif operator == "not_equals" and actual_value == value:
                    return False
                elif operator == "contains" and value not in str(actual_value):
                    return False
                elif operator == "greater_than" and not (actual_value > value):
                    return False
                elif operator == "less_than" and not (actual_value < value):
                    return False

        return True

    async def _execute_workflow(
        self,
        workflow: CRMWorkflow,
        lead_id: Optional[uuid.UUID],
        deal_id: Optional[uuid.UUID],
        academy_id: Optional[uuid.UUID],
        trigger_data: Optional[Dict]
    ) -> CRMWorkflowExecution:
        """Execute a workflow."""
        execution = CRMWorkflowExecution(
            workflow_id=workflow.id,
            lead_id=lead_id,
            deal_id=deal_id,
            academy_id=academy_id,
            trigger_data=trigger_data,
            actions_executed=[],
            status="in_progress"
        )

        self.session.add(execution)

        try:
            for action in workflow.actions:
                action_result = await self._execute_action(
                    action,
                    lead_id=lead_id,
                    deal_id=deal_id,
                    academy_id=academy_id
                )
                execution.actions_executed.append({
                    "action_type": action.get("type"),
                    "status": "success" if action_result else "failed",
                    "executed_at": datetime.utcnow().isoformat()
                })

            execution.status = "success"
            execution.completed_at = datetime.utcnow()

            # Update workflow execution count
            workflow.execution_count += 1
            workflow.last_executed_at = datetime.utcnow()

        except Exception as e:
            execution.status = "failed"
            execution.error_message = str(e)
            execution.completed_at = datetime.utcnow()
            logger.error("Workflow execution failed", workflow_id=str(workflow.id), error=str(e))

        await self.session.commit()
        await self.session.refresh(execution)

        return execution

    async def _execute_action(
        self,
        action: Dict,
        lead_id: Optional[uuid.UUID],
        deal_id: Optional[uuid.UUID],
        academy_id: Optional[uuid.UUID]
    ) -> bool:
        """Execute a single workflow action."""
        action_type = action.get("type")

        if action_type == WorkflowActionType.SEND_EMAIL.value:
            # Would integrate with email service
            logger.info("Workflow action: send_email", template_id=action.get("template_id"))
            return True

        elif action_type == WorkflowActionType.CREATE_TASK.value:
            # Create a follow-up task
            task = CRMTask(
                title=action.get("title", "Follow-up task"),
                task_type=action.get("task_type", "follow_up"),
                assigned_to_id=action.get("assigned_to_id"),
                created_by_id=action.get("assigned_to_id"),
                lead_id=lead_id,
                deal_id=deal_id,
                academy_id=academy_id,
                due_date=datetime.utcnow() + timedelta(days=action.get("due_days", 1)),
                priority=TaskPriority(action.get("priority", "medium"))
            )
            self.session.add(task)
            return True

        elif action_type == WorkflowActionType.UPDATE_FIELD.value:
            # Update a field on the lead/deal
            field = action.get("field")
            value = action.get("value")

            if lead_id and field:
                await self.session.execute(
                    update(CRMLead)
                    .where(CRMLead.id == lead_id)
                    .values({field: value})
                )
            return True

        elif action_type == WorkflowActionType.ADD_TAG.value:
            tag = action.get("tag")
            if lead_id and tag:
                lead = await self.session.get(CRMLead, lead_id)
                if lead:
                    tags = lead.tags or []
                    if tag not in tags:
                        tags.append(tag)
                        lead.tags = tags
            return True

        elif action_type == WorkflowActionType.NOTIFY_USER.value:
            # Would integrate with notification service
            logger.info("Workflow action: notify_user", user_id=action.get("user_id"))
            return True

        elif action_type == WorkflowActionType.WEBHOOK.value:
            # Would make HTTP request to webhook URL
            logger.info("Workflow action: webhook", url=action.get("url"))
            return True

        elif action_type == WorkflowActionType.DELAY.value:
            # Delay is handled differently in production (job queue)
            delay_minutes = action.get("delay_minutes", 0)
            logger.info("Workflow action: delay", minutes=delay_minutes)
            return True

        return False

    async def create_workflow(
        self,
        name: str,
        trigger: WorkflowTrigger,
        actions: List[Dict],
        created_by_id: uuid.UUID,
        trigger_conditions: Optional[Dict] = None,
        description: Optional[str] = None
    ) -> CRMWorkflow:
        """Create a new workflow."""
        workflow = CRMWorkflow(
            name=name,
            trigger=trigger,
            actions=actions,
            trigger_conditions=trigger_conditions,
            description=description,
            created_by_id=created_by_id,
            is_active=True
        )

        self.session.add(workflow)
        await self.session.commit()
        await self.session.refresh(workflow)

        return workflow


class CampaignService:
    """Service for managing marketing campaigns."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_campaign(
        self,
        name: str,
        type: CampaignType,
        owner_id: uuid.UUID,
        **kwargs
    ) -> CRMCampaign:
        """Create a new campaign."""
        campaign = CRMCampaign(
            name=name,
            type=type,
            owner_id=owner_id,
            status=CampaignStatus.DRAFT,
            **kwargs
        )

        self.session.add(campaign)
        await self.session.commit()
        await self.session.refresh(campaign)

        return campaign

    async def add_members_to_campaign(
        self,
        campaign_id: uuid.UUID,
        lead_ids: List[uuid.UUID]
    ) -> int:
        """Add leads to a campaign."""
        added = 0
        for lead_id in lead_ids:
            # Check if already a member
            existing = await self.session.execute(
                select(CRMCampaignMember).where(
                    CRMCampaignMember.campaign_id == campaign_id,
                    CRMCampaignMember.lead_id == lead_id
                )
            )
            if existing.scalar_one_or_none():
                continue

            member = CRMCampaignMember(
                campaign_id=campaign_id,
                lead_id=lead_id,
                status="enrolled"
            )
            self.session.add(member)
            added += 1

        await self.session.commit()
        return added

    async def update_campaign_metrics(
        self,
        campaign_id: uuid.UUID,
        emails_sent: int = 0,
        emails_opened: int = 0,
        emails_clicked: int = 0
    ) -> CRMCampaign:
        """Update campaign metrics."""
        campaign = await self.session.get(CRMCampaign, campaign_id)
        if not campaign:
            raise ValueError(f"Campaign {campaign_id} not found")

        campaign.emails_sent += emails_sent
        campaign.emails_opened += emails_opened
        campaign.emails_clicked += emails_clicked

        await self.session.commit()
        await self.session.refresh(campaign)

        return campaign

    async def get_campaign_analytics(
        self,
        campaign_id: uuid.UUID
    ) -> Dict[str, Any]:
        """Get campaign analytics."""
        campaign = await self.session.get(CRMCampaign, campaign_id)
        if not campaign:
            raise ValueError(f"Campaign {campaign_id} not found")

        # Member stats
        members_result = await self.session.execute(
            select(
                CRMCampaignMember.status,
                func.count(CRMCampaignMember.id).label('count')
            )
            .where(CRMCampaignMember.campaign_id == campaign_id)
            .group_by(CRMCampaignMember.status)
        )
        member_stats = {row.status: row.count for row in members_result}

        total_members = sum(member_stats.values())

        return {
            "campaign_id": str(campaign_id),
            "name": campaign.name,
            "status": campaign.status.value,
            "metrics": {
                "total_members": total_members,
                "members_by_status": member_stats,
                "emails_sent": campaign.emails_sent,
                "emails_opened": campaign.emails_opened,
                "emails_clicked": campaign.emails_clicked,
                "open_rate": (campaign.emails_opened / campaign.emails_sent * 100) if campaign.emails_sent > 0 else 0,
                "click_rate": (campaign.emails_clicked / campaign.emails_sent * 100) if campaign.emails_sent > 0 else 0,
                "conversions": campaign.conversions,
                "revenue_generated": float(campaign.revenue_generated)
            },
            "goals": {
                "leads_goal": campaign.goal_leads,
                "leads_actual": campaign.leads_generated,
                "conversions_goal": campaign.goal_conversions,
                "conversions_actual": campaign.conversions,
                "revenue_goal": float(campaign.goal_revenue) if campaign.goal_revenue else None,
                "revenue_actual": float(campaign.revenue_generated)
            },
            "budget": {
                "allocated": float(campaign.budget) if campaign.budget else None,
                "spent": float(campaign.actual_cost) if campaign.actual_cost else None
            }
        }
