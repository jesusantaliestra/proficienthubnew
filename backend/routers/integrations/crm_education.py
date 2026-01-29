"""
CRM Supreme - Enhanced for Education Niche
Premium CRM specifically designed for educational institutions
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone, timedelta
import uuid

import sys
sys.path.append('/app/backend')
from database import db
from utils.auth import get_current_user

router = APIRouter(prefix="/crm-edu", tags=["CRM - Education Niche"])

# ==================== EDUCATION-SPECIFIC PIPELINE STAGES ====================

EDU_PIPELINE_STAGES = [
    {"id": "lead", "name": "Lead", "order": 1, "color": "#6366f1", "description": "Initial contact/inquiry"},
    {"id": "qualified", "name": "Qualified", "order": 2, "color": "#8b5cf6", "description": "Verified as decision maker"},
    {"id": "demo_scheduled", "name": "Demo Scheduled", "order": 3, "color": "#a855f7", "description": "Platform demo booked"},
    {"id": "demo_completed", "name": "Demo Completed", "order": 4, "color": "#d946ef", "description": "Demo delivered"},
    {"id": "trial", "name": "Trial", "order": 5, "color": "#ec4899", "description": "Free trial active"},
    {"id": "proposal", "name": "Proposal Sent", "order": 6, "color": "#f43f5e", "description": "Quote/proposal delivered"},
    {"id": "negotiation", "name": "Negotiation", "order": 7, "color": "#f97316", "description": "Discussing terms"},
    {"id": "onboarding", "name": "Onboarding", "order": 8, "color": "#eab308", "description": "Contract signed, setup in progress"},
    {"id": "active", "name": "Active Customer", "order": 9, "color": "#22c55e", "description": "Fully onboarded and using platform"},
    {"id": "churned", "name": "Churned", "order": 10, "color": "#64748b", "description": "No longer a customer"},
    {"id": "lost", "name": "Lost", "order": 0, "color": "#ef4444", "description": "Did not convert"}
]

# ==================== EDUCATION SCORING FACTORS ====================

EDU_SCORING_FACTORS = {
    "institution_size": {
        "small": {"min": 1, "max": 100, "score": 10},
        "medium": {"min": 101, "max": 500, "score": 25},
        "large": {"min": 501, "max": 2000, "score": 40},
        "enterprise": {"min": 2001, "max": 999999, "score": 50}
    },
    "exam_types": {
        "single": 5,
        "multiple": 15,
        "comprehensive": 25  # All exam types
    },
    "engagement": {
        "opened_email": 5,
        "clicked_link": 10,
        "visited_site": 10,
        "requested_demo": 20,
        "started_trial": 25,
        "completed_onboarding": 30
    },
    "decision_maker": {
        "owner_director": 25,
        "department_head": 15,
        "teacher_instructor": 5,
        "admin_staff": 3
    },
    "budget_timeline": {
        "immediate": 30,
        "this_quarter": 20,
        "this_year": 10,
        "exploring": 5
    }
}

# ==================== MODELS ====================

class EduLeadCreate(BaseModel):
    institution_name: str
    contact_name: str
    contact_email: EmailStr
    contact_phone: Optional[str] = None
    contact_role: Optional[str] = None
    institution_type: Optional[str] = None  # language_school, university, corporate_training, etc.
    estimated_students: Optional[int] = None
    exam_types_interested: List[str] = []
    country: Optional[str] = None
    source: Optional[str] = None  # website, referral, ads, event, etc.
    notes: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class EduLeadUpdate(BaseModel):
    stage: Optional[str] = None
    contact_name: Optional[str] = None
    contact_email: Optional[EmailStr] = None
    contact_phone: Optional[str] = None
    contact_role: Optional[str] = None
    estimated_students: Optional[int] = None
    exam_types_interested: Optional[List[str]] = None
    budget_timeline: Optional[str] = None
    notes: Optional[str] = None
    assigned_to: Optional[str] = None

class TaskCreate(BaseModel):
    lead_id: str
    task_type: str  # call, email, demo, follow_up, onboarding
    title: str
    description: Optional[str] = None
    due_date: str
    priority: str = "medium"  # low, medium, high, urgent

class AutomationRule(BaseModel):
    name: str
    trigger_event: str
    trigger_conditions: Dict[str, Any]
    actions: List[Dict[str, Any]]
    is_active: bool = True

# ==================== HELPER FUNCTIONS ====================

def calculate_edu_lead_score(lead: dict) -> int:
    """Calculate lead score based on education-specific factors"""
    score = 0
    
    # Institution size
    students = lead.get("estimated_students", 0)
    for size, config in EDU_SCORING_FACTORS["institution_size"].items():
        if config["min"] <= students <= config["max"]:
            score += config["score"]
            break
    
    # Exam types
    exam_count = len(lead.get("exam_types_interested", []))
    if exam_count >= 5:
        score += EDU_SCORING_FACTORS["exam_types"]["comprehensive"]
    elif exam_count > 1:
        score += EDU_SCORING_FACTORS["exam_types"]["multiple"]
    elif exam_count == 1:
        score += EDU_SCORING_FACTORS["exam_types"]["single"]
    
    # Decision maker role
    role = lead.get("contact_role", "").lower()
    if "owner" in role or "director" in role or "principal" in role:
        score += EDU_SCORING_FACTORS["decision_maker"]["owner_director"]
    elif "head" in role or "manager" in role:
        score += EDU_SCORING_FACTORS["decision_maker"]["department_head"]
    elif "teacher" in role or "instructor" in role:
        score += EDU_SCORING_FACTORS["decision_maker"]["teacher_instructor"]
    
    # Budget timeline
    timeline = lead.get("budget_timeline", "")
    if timeline in EDU_SCORING_FACTORS["budget_timeline"]:
        score += EDU_SCORING_FACTORS["budget_timeline"][timeline]
    
    # Engagement scoring from activities
    engagement_score = lead.get("engagement_score", 0)
    score += engagement_score
    
    return min(score, 100)  # Cap at 100

async def trigger_automations(event: str, lead: dict, institution_id: str):
    """Trigger automation rules based on event"""
    rules = await db.crm_automations.find({
        "institution_id": institution_id,
        "trigger_event": event,
        "is_active": True
    }).to_list(100)
    
    for rule in rules:
        # Check conditions
        conditions_met = True
        for field, expected in rule.get("trigger_conditions", {}).items():
            if lead.get(field) != expected:
                conditions_met = False
                break
        
        if conditions_met:
            # Execute actions
            for action in rule.get("actions", []):
                action_type = action.get("type")
                
                if action_type == "send_email":
                    # Queue email
                    await db.crm_email_queue.insert_one({
                        "id": str(uuid.uuid4()),
                        "lead_id": lead["id"],
                        "template_id": action.get("template_id"),
                        "status": "pending",
                        "created_at": datetime.now(timezone.utc).isoformat()
                    })
                
                elif action_type == "create_task":
                    await db.crm_tasks.insert_one({
                        "id": str(uuid.uuid4()),
                        "lead_id": lead["id"],
                        "institution_id": institution_id,
                        "task_type": action.get("task_type"),
                        "title": action.get("title"),
                        "due_date": (datetime.now(timezone.utc) + timedelta(days=action.get("due_in_days", 1))).isoformat(),
                        "priority": action.get("priority", "medium"),
                        "status": "pending",
                        "created_at": datetime.now(timezone.utc).isoformat()
                    })
                
                elif action_type == "update_stage":
                    await db.crm_leads.update_one(
                        {"id": lead["id"]},
                        {"$set": {"stage": action.get("stage")}}
                    )
                
                elif action_type == "notify":
                    await db.notifications.insert_one({
                        "id": str(uuid.uuid4()),
                        "user_id": action.get("notify_user_id"),
                        "type": "crm_automation",
                        "title": action.get("title"),
                        "message": action.get("message"),
                        "lead_id": lead["id"],
                        "created_at": datetime.now(timezone.utc).isoformat()
                    })

# ==================== LEAD MANAGEMENT ====================

@router.get("/pipeline-stages")
async def get_pipeline_stages(
    current_user: dict = Depends(get_current_user)
):
    """Get education-specific pipeline stages"""
    return {"stages": EDU_PIPELINE_STAGES}

@router.post("/leads")
async def create_edu_lead(
    lead_data: EduLeadCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create a new education lead"""
    if current_user["user_type"] not in ["institution", "admin"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    lead_id = str(uuid.uuid4())
    
    lead_doc = {
        "id": lead_id,
        "institution_id": current_user["id"],
        **lead_data.dict(),
        "stage": "lead",
        "lead_score": 0,
        "engagement_score": 0,
        "activities": [],
        "tags": [],
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "created_by": current_user["id"]
    }
    
    # Calculate initial score
    lead_doc["lead_score"] = calculate_edu_lead_score(lead_doc)
    
    await db.crm_leads.insert_one(lead_doc)
    
    # Trigger automations
    await trigger_automations("lead_created", lead_doc, current_user["id"])
    
    return {
        "id": lead_id,
        "lead_score": lead_doc["lead_score"],
        "stage": "lead"
    }

@router.get("/leads")
async def list_edu_leads(
    stage: Optional[str] = None,
    min_score: Optional[int] = None,
    assigned_to: Optional[str] = None,
    exam_type: Optional[str] = None,
    country: Optional[str] = None,
    source: Optional[str] = None,
    search: Optional[str] = None,
    sort_by: str = "created_at",
    sort_order: str = "desc",
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    current_user: dict = Depends(get_current_user)
):
    """List education leads with filtering"""
    query = {"institution_id": current_user["id"]}
    
    if stage:
        query["stage"] = stage
    if min_score:
        query["lead_score"] = {"$gte": min_score}
    if assigned_to:
        query["assigned_to"] = assigned_to
    if exam_type:
        query["exam_types_interested"] = exam_type
    if country:
        query["country"] = country
    if source:
        query["source"] = source
    if search:
        query["$or"] = [
            {"institution_name": {"$regex": search, "$options": "i"}},
            {"contact_name": {"$regex": search, "$options": "i"}},
            {"contact_email": {"$regex": search, "$options": "i"}}
        ]
    
    total = await db.crm_leads.count_documents(query)
    skip = (page - 1) * per_page
    
    sort_direction = -1 if sort_order == "desc" else 1
    leads = await db.crm_leads.find(
        query,
        {"_id": 0}
    ).sort(sort_by, sort_direction).skip(skip).limit(per_page).to_list(per_page)
    
    return {
        "leads": leads,
        "total": total,
        "page": page,
        "per_page": per_page,
        "total_pages": (total + per_page - 1) // per_page
    }

@router.get("/leads/{lead_id}")
async def get_edu_lead(
    lead_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get lead details"""
    lead = await db.crm_leads.find_one(
        {"id": lead_id, "institution_id": current_user["id"]},
        {"_id": 0}
    )
    
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    # Get associated tasks
    tasks = await db.crm_tasks.find(
        {"lead_id": lead_id},
        {"_id": 0}
    ).sort("due_date", 1).to_list(50)
    
    # Get activity history
    activities = await db.crm_activities.find(
        {"lead_id": lead_id},
        {"_id": 0}
    ).sort("created_at", -1).to_list(100)
    
    lead["tasks"] = tasks
    lead["activity_history"] = activities
    
    return lead

@router.patch("/leads/{lead_id}")
async def update_edu_lead(
    lead_id: str,
    update_data: EduLeadUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Update a lead"""
    lead = await db.crm_leads.find_one(
        {"id": lead_id, "institution_id": current_user["id"]},
        {"_id": 0}
    )
    
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    update_dict = {k: v for k, v in update_data.dict().items() if v is not None}
    
    if update_dict:
        update_dict["updated_at"] = datetime.now(timezone.utc).isoformat()
        
        # Check for stage change
        old_stage = lead.get("stage")
        new_stage = update_dict.get("stage")
        
        await db.crm_leads.update_one(
            {"id": lead_id},
            {"$set": update_dict}
        )
        
        # Recalculate score
        updated_lead = await db.crm_leads.find_one({"id": lead_id}, {"_id": 0})
        new_score = calculate_edu_lead_score(updated_lead)
        await db.crm_leads.update_one(
            {"id": lead_id},
            {"$set": {"lead_score": new_score}}
        )
        
        # Log activity
        if new_stage and new_stage != old_stage:
            await db.crm_activities.insert_one({
                "id": str(uuid.uuid4()),
                "lead_id": lead_id,
                "institution_id": current_user["id"],
                "type": "stage_change",
                "description": f"Stage changed from {old_stage} to {new_stage}",
                "old_value": old_stage,
                "new_value": new_stage,
                "created_by": current_user["id"],
                "created_at": datetime.now(timezone.utc).isoformat()
            })
            
            # Trigger automations
            await trigger_automations(f"stage_changed_to_{new_stage}", updated_lead, current_user["id"])
    
    return {"message": "Lead updated"}

# ==================== TASKS ====================

@router.post("/tasks")
async def create_task(
    task_data: TaskCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create a task for a lead"""
    # Verify lead exists
    lead = await db.crm_leads.find_one(
        {"id": task_data.lead_id, "institution_id": current_user["id"]},
        {"_id": 0, "id": 1}
    )
    
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    task_id = str(uuid.uuid4())
    
    task_doc = {
        "id": task_id,
        "institution_id": current_user["id"],
        **task_data.dict(),
        "status": "pending",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "created_by": current_user["id"]
    }
    
    await db.crm_tasks.insert_one(task_doc)
    
    return {"id": task_id}

@router.get("/tasks")
async def list_tasks(
    status: Optional[str] = None,
    lead_id: Optional[str] = None,
    task_type: Optional[str] = None,
    priority: Optional[str] = None,
    overdue_only: bool = False,
    current_user: dict = Depends(get_current_user)
):
    """List tasks"""
    query = {"institution_id": current_user["id"]}
    
    if status:
        query["status"] = status
    if lead_id:
        query["lead_id"] = lead_id
    if task_type:
        query["task_type"] = task_type
    if priority:
        query["priority"] = priority
    if overdue_only:
        query["due_date"] = {"$lt": datetime.now(timezone.utc).isoformat()}
        query["status"] = {"$ne": "completed"}
    
    tasks = await db.crm_tasks.find(query, {"_id": 0}).sort("due_date", 1).to_list(200)
    
    return {"tasks": tasks}

@router.patch("/tasks/{task_id}/complete")
async def complete_task(
    task_id: str,
    notes: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """Mark task as completed"""
    result = await db.crm_tasks.update_one(
        {"id": task_id, "institution_id": current_user["id"]},
        {
            "$set": {
                "status": "completed",
                "completed_at": datetime.now(timezone.utc).isoformat(),
                "completion_notes": notes
            }
        }
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Get task to log activity
    task = await db.crm_tasks.find_one({"id": task_id}, {"_id": 0})
    
    # Log activity on lead
    await db.crm_activities.insert_one({
        "id": str(uuid.uuid4()),
        "lead_id": task["lead_id"],
        "institution_id": current_user["id"],
        "type": "task_completed",
        "description": f"Task completed: {task['title']}",
        "task_id": task_id,
        "created_by": current_user["id"],
        "created_at": datetime.now(timezone.utc).isoformat()
    })
    
    return {"message": "Task completed"}

# ==================== AUTOMATIONS ====================

@router.post("/automations")
async def create_automation(
    automation: AutomationRule,
    current_user: dict = Depends(get_current_user)
):
    """Create an automation rule"""
    if current_user["user_type"] not in ["institution", "admin"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    automation_id = str(uuid.uuid4())
    
    automation_doc = {
        "id": automation_id,
        "institution_id": current_user["id"],
        **automation.dict(),
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.crm_automations.insert_one(automation_doc)
    
    return {"id": automation_id}

@router.get("/automations")
async def list_automations(
    current_user: dict = Depends(get_current_user)
):
    """List automation rules"""
    automations = await db.crm_automations.find(
        {"institution_id": current_user["id"]},
        {"_id": 0}
    ).to_list(100)
    
    return {"automations": automations}

# ==================== ANALYTICS ====================

@router.get("/analytics/pipeline")
async def get_pipeline_analytics(
    period_days: int = 30,
    current_user: dict = Depends(get_current_user)
):
    """Get pipeline analytics"""
    start_date = (datetime.now(timezone.utc) - timedelta(days=period_days)).isoformat()
    
    # Leads by stage
    pipeline = [
        {"$match": {"institution_id": current_user["id"]}},
        {"$group": {
            "_id": "$stage",
            "count": {"$sum": 1},
            "total_potential_value": {"$sum": "$estimated_value"}
        }}
    ]
    
    by_stage = await db.crm_leads.aggregate(pipeline).to_list(20)
    
    # Conversion rates
    total_leads = await db.crm_leads.count_documents({"institution_id": current_user["id"]})
    active_customers = await db.crm_leads.count_documents({
        "institution_id": current_user["id"],
        "stage": "active"
    })
    
    conversion_rate = (active_customers / total_leads * 100) if total_leads > 0 else 0
    
    # Average time in each stage
    # This would require tracking stage change timestamps
    
    # Lead sources
    source_pipeline = [
        {"$match": {"institution_id": current_user["id"]}},
        {"$group": {
            "_id": "$source",
            "count": {"$sum": 1}
        }},
        {"$sort": {"count": -1}}
    ]
    
    by_source = await db.crm_leads.aggregate(source_pipeline).to_list(20)
    
    return {
        "period_days": period_days,
        "total_leads": total_leads,
        "active_customers": active_customers,
        "conversion_rate": round(conversion_rate, 2),
        "by_stage": {s["_id"]: {"count": s["count"], "value": s.get("total_potential_value", 0)} for s in by_stage},
        "by_source": {s["_id"]: s["count"] for s in by_source if s["_id"]}
    }

@router.get("/analytics/forecasting")
async def get_revenue_forecast(
    current_user: dict = Depends(get_current_user)
):
    """Get revenue forecast based on pipeline"""
    # Get leads in negotiation stages
    pipeline_value = await db.crm_leads.aggregate([
        {
            "$match": {
                "institution_id": current_user["id"],
                "stage": {"$in": ["proposal", "negotiation", "trial"]}
            }
        },
        {
            "$group": {
                "_id": "$stage",
                "count": {"$sum": 1},
                "total_value": {"$sum": "$estimated_value"}
            }
        }
    ]).to_list(10)
    
    # Apply probability multipliers
    stage_probabilities = {
        "trial": 0.5,
        "proposal": 0.3,
        "negotiation": 0.6
    }
    
    weighted_forecast = 0
    pipeline_details = []
    
    for stage in pipeline_value:
        probability = stage_probabilities.get(stage["_id"], 0.1)
        weighted_value = stage.get("total_value", 0) * probability
        weighted_forecast += weighted_value
        
        pipeline_details.append({
            "stage": stage["_id"],
            "deals": stage["count"],
            "total_value": stage.get("total_value", 0),
            "probability": probability,
            "weighted_value": round(weighted_value, 2)
        })
    
    return {
        "weighted_forecast": round(weighted_forecast, 2),
        "pipeline_breakdown": pipeline_details,
        "assumptions": "Based on historical conversion rates per stage"
    }


# ==================== NOTIFICATION SETTINGS ====================

class NotificationSettingCreate(BaseModel):
    name: str
    trigger_stage: str  # Stage that triggers notification
    notify_on_enter: bool = True  # Notify when lead enters this stage
    notify_on_exit: bool = False  # Notify when lead exits this stage
    notification_channels: List[str] = ["in_app"]  # in_app, email, sms
    recipients: List[str] = []  # user_ids or "owner", "team"
    email_template: Optional[str] = None
    include_lead_details: bool = True
    is_active: bool = True

class NotificationSettingsUpdate(BaseModel):
    name: Optional[str] = None
    notify_on_enter: Optional[bool] = None
    notify_on_exit: Optional[bool] = None
    notification_channels: Optional[List[str]] = None
    recipients: Optional[List[str]] = None
    email_template: Optional[str] = None
    include_lead_details: Optional[bool] = None
    is_active: Optional[bool] = None

@router.post("/notification-settings")
async def create_notification_setting(
    setting: NotificationSettingCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create a stage notification setting"""
    if current_user["user_type"] not in ["institution", "admin"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    setting_id = str(uuid.uuid4())
    
    setting_doc = {
        "id": setting_id,
        "institution_id": current_user["id"],
        "name": setting.name,
        "trigger_stage": setting.trigger_stage,
        "notify_on_enter": setting.notify_on_enter,
        "notify_on_exit": setting.notify_on_exit,
        "notification_channels": setting.notification_channels,
        "recipients": setting.recipients,
        "email_template": setting.email_template,
        "include_lead_details": setting.include_lead_details,
        "is_active": setting.is_active,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.crm_notification_settings.insert_one(setting_doc)
    
    return {"id": setting_id, "message": "Notification setting created"}

@router.get("/notification-settings")
async def list_notification_settings(
    current_user: dict = Depends(get_current_user)
):
    """List all notification settings"""
    settings = await db.crm_notification_settings.find(
        {"institution_id": current_user["id"]},
        {"_id": 0}
    ).to_list(100)
    
    return {"settings": settings, "stages": EDU_PIPELINE_STAGES}

@router.get("/notification-settings/{setting_id}")
async def get_notification_setting(
    setting_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get a specific notification setting"""
    setting = await db.crm_notification_settings.find_one(
        {"id": setting_id, "institution_id": current_user["id"]},
        {"_id": 0}
    )
    
    if not setting:
        raise HTTPException(status_code=404, detail="Setting not found")
    
    return setting

@router.patch("/notification-settings/{setting_id}")
async def update_notification_setting(
    setting_id: str,
    updates: NotificationSettingsUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Update a notification setting"""
    update_dict = {k: v for k, v in updates.dict().items() if v is not None}
    update_dict["updated_at"] = datetime.now(timezone.utc).isoformat()
    
    result = await db.crm_notification_settings.update_one(
        {"id": setting_id, "institution_id": current_user["id"]},
        {"$set": update_dict}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Setting not found")
    
    return {"message": "Setting updated"}

@router.delete("/notification-settings/{setting_id}")
async def delete_notification_setting(
    setting_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete a notification setting"""
    result = await db.crm_notification_settings.delete_one(
        {"id": setting_id, "institution_id": current_user["id"]}
    )
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Setting not found")
    
    return {"message": "Setting deleted"}

@router.get("/notifications")
async def get_user_notifications(
    unread_only: bool = False,
    limit: int = 50,
    current_user: dict = Depends(get_current_user)
):
    """Get notifications for current user"""
    query = {"user_id": current_user["id"]}
    
    if unread_only:
        query["read"] = False
    
    notifications = await db.notifications.find(
        query,
        {"_id": 0}
    ).sort("created_at", -1).limit(limit).to_list(limit)
    
    unread_count = await db.notifications.count_documents({
        "user_id": current_user["id"],
        "read": False
    })
    
    return {
        "notifications": notifications,
        "unread_count": unread_count
    }

@router.patch("/notifications/{notification_id}/read")
async def mark_notification_read(
    notification_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Mark a notification as read"""
    await db.notifications.update_one(
        {"id": notification_id, "user_id": current_user["id"]},
        {"$set": {"read": True, "read_at": datetime.now(timezone.utc).isoformat()}}
    )
    
    return {"message": "Notification marked as read"}

@router.post("/notifications/mark-all-read")
async def mark_all_notifications_read(
    current_user: dict = Depends(get_current_user)
):
    """Mark all notifications as read"""
    await db.notifications.update_many(
        {"user_id": current_user["id"], "read": False},
        {"$set": {"read": True, "read_at": datetime.now(timezone.utc).isoformat()}}
    )
    
    return {"message": "All notifications marked as read"}
