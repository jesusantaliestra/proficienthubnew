"""
CRM Router - Lead management, pipeline, automation, and email templates
Migrated from server.py for better code organization
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone, timedelta
import uuid
import os

from motor.motor_asyncio import AsyncIOMotorClient

router = APIRouter(prefix="/crm", tags=["CRM"])

# Database connection
client = AsyncIOMotorClient(os.environ.get('MONGO_URL'))
db = client[os.environ.get('DB_NAME', 'proficienthub')]

# Auth utility
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt

JWT_SECRET = os.environ.get('JWT_SECRET', 'proficienthub-secret-key')
security = HTTPBearer(auto_error=False)

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if not credentials:
        raise HTTPException(status_code=401, detail="Authentication required")
    try:
        payload = jwt.decode(credentials.credentials, JWT_SECRET, algorithms=["HS256"])
        user = await db.users.find_one({"id": payload["user_id"]}, {"_id": 0})
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        return user
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

# ==================== MODELS ====================

PIPELINE_STAGES = {
    "new": {"label": "New Lead", "color": "#94A3B8"},
    "contacted": {"label": "Contacted", "color": "#60A5FA"},
    "demo_scheduled": {"label": "Demo Scheduled", "color": "#A78BFA"},
    "demo_completed": {"label": "Demo Completed", "color": "#34D399"},
    "proposal_sent": {"label": "Proposal Sent", "color": "#FBBF24"},
    "negotiating": {"label": "Negotiating", "color": "#F97316"},
    "won": {"label": "Won", "color": "#22C55E"},
    "lost": {"label": "Lost", "color": "#EF4444"}
}

class LeadCreate(BaseModel):
    institution_name: str
    contact_name: str
    email: EmailStr
    phone: Optional[str] = None
    country: Optional[str] = None
    students_count: Optional[int] = None
    exam_types: Optional[List[str]] = []
    source: str = "organic"
    notes: Optional[str] = None
    estimated_value: Optional[float] = None

class LeadUpdate(BaseModel):
    stage: Optional[str] = None
    contact_name: Optional[str] = None
    phone: Optional[str] = None
    country: Optional[str] = None
    students_count: Optional[int] = None
    exam_types: Optional[List[str]] = None
    notes: Optional[str] = None
    estimated_value: Optional[float] = None
    next_follow_up: Optional[str] = None
    assigned_to: Optional[str] = None

class ActivityCreate(BaseModel):
    lead_id: str
    activity_type: str  # call, email, meeting, note, demo
    description: str
    outcome: Optional[str] = None

class EmailTemplate(BaseModel):
    name: str
    subject: str
    body_html: str
    category: str  # welcome, follow_up, reminder, proposal, custom
    variables: List[str] = []

class EmailSequence(BaseModel):
    name: str
    description: Optional[str] = None
    steps: List[dict]  # [{template_id, delay_days, condition}]
    is_active: bool = True

class AutomationRule(BaseModel):
    name: str
    trigger_type: str  # lead_created, stage_changed, inactivity, score_threshold
    trigger_config: dict = {}
    actions: List[dict]  # [{type, config}]
    is_active: bool = True

# Lead Scoring Rules
LEAD_SCORING_RULES = {
    "students_count": {"1-50": 10, "51-200": 20, "201-500": 30, "501-1000": 40, "1000+": 50},
    "exam_types_count": {"1": 5, "2-3": 15, "4+": 25},
    "source": {"referral": 30, "organic": 20, "paid_ad": 15, "cold_outreach": 5},
    "engagement": {"demo_attended": 25, "materials_downloaded": 15, "replied_email": 10},
    "stage_velocity": {"fast": 20, "normal": 10, "slow": -10}
}

# ==================== PIPELINE ENDPOINTS ====================

@router.get("/pipeline-stages")
async def get_pipeline_stages():
    """Get all available pipeline stages"""
    return {"stages": PIPELINE_STAGES}

# ==================== LEAD CRUD ====================

@router.post("/leads")
async def create_lead(lead_data: LeadCreate, current_user: dict = Depends(get_current_user)):
    """Create a new lead in the CRM"""
    if current_user["user_type"] not in ["admin", "institution"]:
        raise HTTPException(status_code=403, detail="Only admins and institutions can create leads")
    
    existing = await db.crm_leads.find_one({"email": lead_data.email})
    if existing:
        raise HTTPException(status_code=400, detail="Lead with this email already exists")
    
    lead_id = str(uuid.uuid4())
    lead_doc = {
        "id": lead_id,
        "institution_name": lead_data.institution_name,
        "contact_name": lead_data.contact_name,
        "email": lead_data.email,
        "phone": lead_data.phone,
        "country": lead_data.country,
        "students_count": lead_data.students_count,
        "exam_types": lead_data.exam_types or [],
        "source": lead_data.source,
        "notes": lead_data.notes,
        "estimated_value": lead_data.estimated_value or 0,
        "stage": "new",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "created_by": current_user["id"],
        "assigned_to": current_user["id"],
        "next_follow_up": None,
        "activities": [],
        "tags": []
    }
    
    await db.crm_leads.insert_one(lead_doc)
    # Remove MongoDB _id to avoid serialization issues
    if "_id" in lead_doc:
        del lead_doc["_id"]
    
    return {"id": lead_id, "message": "Lead created successfully", "lead": lead_doc}

@router.get("/leads")
async def get_all_leads(
    stage: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """Get all leads, optionally filtered by stage"""
    if current_user["user_type"] not in ["admin", "institution"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    query = {}
    if stage:
        query["stage"] = stage
    
    if current_user["user_type"] == "institution":
        query["$or"] = [
            {"created_by": current_user["id"]},
            {"assigned_to": current_user["id"]}
        ]
    
    leads = await db.crm_leads.find(query).sort("updated_at", -1).to_list(500)
    
    pipeline = {stage_key: [] for stage_key in PIPELINE_STAGES.keys()}
    for lead in leads:
        lead.pop("_id", None)
        lead_stage = lead.get("stage", "new")
        if lead_stage in pipeline:
            pipeline[lead_stage].append({
                "id": lead["id"],
                "institution_name": lead.get("institution_name", ""),
                "contact_name": lead.get("contact_name", ""),
                "email": lead.get("email", ""),
                "phone": lead.get("phone", ""),
                "country": lead.get("country", ""),
                "students_count": lead.get("students_count", 0),
                "exam_types": lead.get("exam_types", []),
                "estimated_value": lead.get("estimated_value", 0),
                "stage": lead_stage,
                "created_at": lead.get("created_at", ""),
                "updated_at": lead.get("updated_at", ""),
                "next_follow_up": lead.get("next_follow_up"),
                "source": lead.get("source", ""),
                "activities_count": len(lead.get("activities", []))
            })
    
    total_leads = len(leads)
    total_value = sum(l.get("estimated_value", 0) for l in leads)
    won_value = sum(l.get("estimated_value", 0) for l in leads if l.get("stage") == "won")
    
    return {
        "pipeline": pipeline,
        "stages": PIPELINE_STAGES,
        "stats": {
            "total_leads": total_leads,
            "total_value": total_value,
            "won_value": won_value,
            "conversion_rate": round(len([l for l in leads if l.get("stage") == "won"]) / total_leads * 100, 1) if total_leads > 0 else 0
        }
    }

@router.get("/leads/{lead_id}")
async def get_lead_detail(lead_id: str, current_user: dict = Depends(get_current_user)):
    """Get detailed information about a lead"""
    if current_user["user_type"] not in ["admin", "institution"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    lead = await db.crm_leads.find_one({"id": lead_id})
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    lead.pop("_id", None)
    return lead

@router.put("/leads/{lead_id}")
async def update_lead(lead_id: str, updates: LeadUpdate, current_user: dict = Depends(get_current_user)):
    """Update a lead's information or stage"""
    if current_user["user_type"] not in ["admin", "institution"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    lead = await db.crm_leads.find_one({"id": lead_id})
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    update_data = {"updated_at": datetime.now(timezone.utc).isoformat()}
    
    if updates.stage:
        if updates.stage not in PIPELINE_STAGES:
            raise HTTPException(status_code=400, detail="Invalid stage")
        update_data["stage"] = updates.stage
        
        activity = {
            "id": str(uuid.uuid4()),
            "type": "stage_change",
            "description": f"Stage changed from {lead.get('stage', 'new')} to {updates.stage}",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "user": current_user["email"]
        }
        await db.crm_leads.update_one(
            {"id": lead_id},
            {"$push": {"activities": activity}}
        )
    
    for field in ["contact_name", "phone", "country", "notes", "next_follow_up", "assigned_to"]:
        value = getattr(updates, field, None)
        if value is not None:
            update_data[field] = value
    
    if updates.students_count is not None:
        update_data["students_count"] = updates.students_count
    if updates.exam_types is not None:
        update_data["exam_types"] = updates.exam_types
    if updates.estimated_value is not None:
        update_data["estimated_value"] = updates.estimated_value
    
    await db.crm_leads.update_one({"id": lead_id}, {"$set": update_data})
    
    return {"message": "Lead updated successfully", "updated_fields": list(update_data.keys())}

@router.post("/leads/{lead_id}/activities")
async def add_lead_activity(lead_id: str, activity: ActivityCreate, current_user: dict = Depends(get_current_user)):
    """Add an activity to a lead (call, email, meeting, note)"""
    if current_user["user_type"] not in ["admin", "institution"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    lead = await db.crm_leads.find_one({"id": lead_id})
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    activity_doc = {
        "id": str(uuid.uuid4()),
        "type": activity.activity_type,
        "description": activity.description,
        "outcome": activity.outcome,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "user": current_user["email"]
    }
    
    await db.crm_leads.update_one(
        {"id": lead_id},
        {
            "$push": {"activities": activity_doc},
            "$set": {"updated_at": datetime.now(timezone.utc).isoformat()}
        }
    )
    
    return {"message": "Activity added", "activity": activity_doc}

@router.delete("/leads/{lead_id}")
async def delete_lead(lead_id: str, current_user: dict = Depends(get_current_user)):
    """Delete a lead"""
    if current_user["user_type"] != "admin":
        raise HTTPException(status_code=403, detail="Only admins can delete leads")
    
    result = await db.crm_leads.delete_one({"id": lead_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    return {"message": "Lead deleted successfully"}

# ==================== DASHBOARD ====================

@router.get("/dashboard")
async def get_crm_dashboard(current_user: dict = Depends(get_current_user)):
    """Get CRM dashboard with key metrics"""
    if current_user["user_type"] not in ["admin", "institution"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    query = {}
    if current_user["user_type"] == "institution":
        query["$or"] = [
            {"created_by": current_user["id"]},
            {"assigned_to": current_user["id"]}
        ]
    
    leads = await db.crm_leads.find(query).to_list(1000)
    
    total_leads = len(leads)
    new_leads = len([l for l in leads if l.get("stage") == "new"])
    won_deals = len([l for l in leads if l.get("stage") == "won"])
    lost_deals = len([l for l in leads if l.get("stage") == "lost"])
    
    total_value = sum(l.get("estimated_value", 0) for l in leads)
    won_value = sum(l.get("estimated_value", 0) for l in leads if l.get("stage") == "won")
    pipeline_value = sum(l.get("estimated_value", 0) for l in leads if l.get("stage") not in ["won", "lost"])
    
    by_stage = {}
    for stage in PIPELINE_STAGES.keys():
        stage_leads = [l for l in leads if l.get("stage") == stage]
        by_stage[stage] = {
            "count": len(stage_leads),
            "value": sum(l.get("estimated_value", 0) for l in stage_leads)
        }
    
    by_source = {}
    for lead in leads:
        source = lead.get("source", "unknown")
        by_source[source] = by_source.get(source, 0) + 1
    
    recent_activities = []
    for lead in sorted(leads, key=lambda x: x.get("updated_at", ""), reverse=True)[:10]:
        activities = lead.get("activities", [])
        if activities:
            latest = activities[-1]
            recent_activities.append({
                "lead_id": lead["id"],
                "lead_name": lead.get("institution_name", ""),
                "activity": latest
            })
    
    today = datetime.now(timezone.utc).date().isoformat()
    follow_ups_due = []
    for lead in leads:
        follow_up = lead.get("next_follow_up")
        if follow_up and follow_up <= today:
            follow_ups_due.append({
                "id": lead["id"],
                "institution_name": lead.get("institution_name", ""),
                "contact_name": lead.get("contact_name", ""),
                "follow_up_date": follow_up,
                "stage": lead.get("stage", "")
            })
    
    return {
        "metrics": {
            "total_leads": total_leads,
            "new_leads": new_leads,
            "won_deals": won_deals,
            "lost_deals": lost_deals,
            "conversion_rate": round(won_deals / (won_deals + lost_deals) * 100, 1) if (won_deals + lost_deals) > 0 else 0,
            "total_value": total_value,
            "won_value": won_value,
            "pipeline_value": pipeline_value,
            "avg_deal_size": round(won_value / won_deals, 2) if won_deals > 0 else 0
        },
        "by_stage": by_stage,
        "by_source": by_source,
        "recent_activities": recent_activities[:5],
        "follow_ups_due": follow_ups_due
    }

# ==================== EMAIL TEMPLATES ====================

@router.post("/email-templates")
async def create_email_template(template: EmailTemplate, current_user: dict = Depends(get_current_user)):
    """Create a reusable email template"""
    if current_user["user_type"] not in ["admin", "institution"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    template_id = str(uuid.uuid4())
    template_doc = {
        "id": template_id,
        "institution_id": current_user["id"],
        **template.dict(),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "usage_count": 0
    }
    
    await db.email_templates.insert_one(template_doc)
    return {"id": template_id, "message": "Email template created"}

@router.get("/email-templates")
async def get_email_templates(current_user: dict = Depends(get_current_user)):
    """Get all email templates"""
    templates = await db.email_templates.find({"institution_id": current_user["id"]}, {"_id": 0}).to_list(100)
    
    if not templates:
        default_templates = [
            {
                "id": str(uuid.uuid4()),
                "institution_id": current_user["id"],
                "name": "Welcome Lead",
                "subject": "Welcome to {{platform_name}} - Let's Get Started!",
                "body_html": "<h1>Hello {{contact_name}}!</h1><p>Thank you for your interest in {{platform_name}}.</p>",
                "category": "welcome",
                "variables": ["contact_name", "institution_name", "platform_name"],
                "is_default": True
            },
            {
                "id": str(uuid.uuid4()),
                "institution_id": current_user["id"],
                "name": "Demo Follow-up",
                "subject": "Thanks for attending the {{platform_name}} demo!",
                "body_html": "<h1>Hi {{contact_name}},</h1><p>Thank you for taking the time to see our platform in action!</p>",
                "category": "follow_up",
                "variables": ["contact_name", "institution_name", "platform_name"],
                "is_default": True
            }
        ]
        for t in default_templates:
            await db.email_templates.insert_one(t)
        templates = default_templates
    
    return {"templates": templates}

@router.put("/email-templates/{template_id}")
async def update_email_template(template_id: str, template: EmailTemplate, current_user: dict = Depends(get_current_user)):
    """Update an email template"""
    if current_user["user_type"] not in ["admin", "institution"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    result = await db.email_templates.update_one(
        {"id": template_id, "institution_id": current_user["id"]},
        {"$set": {**template.dict(), "updated_at": datetime.now(timezone.utc).isoformat()}}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Template not found")
    
    return {"message": "Template updated"}

@router.delete("/email-templates/{template_id}")
async def delete_email_template(template_id: str, current_user: dict = Depends(get_current_user)):
    """Delete an email template"""
    if current_user["user_type"] not in ["admin", "institution"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    result = await db.email_templates.delete_one(
        {"id": template_id, "institution_id": current_user["id"], "is_default": {"$ne": True}}
    )
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Template not found or is default")
    
    return {"message": "Template deleted"}

# ==================== EMAIL SEQUENCES ====================

@router.post("/email-sequences")
async def create_email_sequence(sequence: EmailSequence, current_user: dict = Depends(get_current_user)):
    """Create an automated email sequence"""
    if current_user["user_type"] not in ["admin", "institution"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    sequence_id = str(uuid.uuid4())
    sequence_doc = {
        "id": sequence_id,
        "institution_id": current_user["id"],
        **sequence.dict(),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "total_enrolled": 0,
        "total_completed": 0
    }
    
    await db.email_sequences.insert_one(sequence_doc)
    return {"id": sequence_id, "message": "Email sequence created"}

@router.get("/email-sequences")
async def get_email_sequences(current_user: dict = Depends(get_current_user)):
    """Get all email sequences"""
    sequences = await db.email_sequences.find(
        {"institution_id": current_user["id"]},
        {"_id": 0}
    ).to_list(50)
    return {"sequences": sequences}

@router.put("/email-sequences/{sequence_id}")
async def update_email_sequence(sequence_id: str, sequence: EmailSequence, current_user: dict = Depends(get_current_user)):
    """Update an email sequence"""
    if current_user["user_type"] not in ["admin", "institution"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    result = await db.email_sequences.update_one(
        {"id": sequence_id, "institution_id": current_user["id"]},
        {"$set": {**sequence.dict(), "updated_at": datetime.now(timezone.utc).isoformat()}}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Sequence not found")
    
    return {"message": "Sequence updated"}

@router.delete("/email-sequences/{sequence_id}")
async def delete_email_sequence(sequence_id: str, current_user: dict = Depends(get_current_user)):
    """Delete an email sequence"""
    result = await db.email_sequences.delete_one(
        {"id": sequence_id, "institution_id": current_user["id"]}
    )
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Sequence not found")
    
    return {"message": "Sequence deleted"}

# ==================== AUTOMATION RULES ====================

@router.post("/automation-rules")
async def create_automation_rule(rule: AutomationRule, current_user: dict = Depends(get_current_user)):
    """Create an automation rule"""
    if current_user["user_type"] not in ["admin", "institution"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    rule_id = str(uuid.uuid4())
    rule_doc = {
        "id": rule_id,
        "institution_id": current_user["id"],
        **rule.dict(),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "executions_count": 0,
        "last_executed": None
    }
    
    await db.automation_rules.insert_one(rule_doc)
    return {"id": rule_id, "message": "Automation rule created"}

@router.get("/automation-rules")
async def get_automation_rules(current_user: dict = Depends(get_current_user)):
    """Get all automation rules"""
    rules = await db.automation_rules.find({"institution_id": current_user["id"]}, {"_id": 0}).to_list(50)
    
    if not rules:
        default_rules = [
            {
                "id": str(uuid.uuid4()),
                "institution_id": current_user["id"],
                "name": "Welcome Email on Lead Creation",
                "trigger_type": "lead_created",
                "trigger_config": {},
                "actions": [{"type": "send_email", "template": "welcome"}],
                "is_active": True,
                "is_default": True
            },
            {
                "id": str(uuid.uuid4()),
                "institution_id": current_user["id"],
                "name": "7-Day Inactivity Follow-up",
                "trigger_type": "inactivity",
                "trigger_config": {"days": 7},
                "actions": [{"type": "send_email", "template": "reminder"}],
                "is_active": True,
                "is_default": True
            }
        ]
        for r in default_rules:
            await db.automation_rules.insert_one(r)
        rules = default_rules
    
    return {"rules": rules}

@router.put("/automation-rules/{rule_id}")
async def update_automation_rule(rule_id: str, rule: AutomationRule, current_user: dict = Depends(get_current_user)):
    """Update an automation rule"""
    if current_user["user_type"] not in ["admin", "institution"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    result = await db.automation_rules.update_one(
        {"id": rule_id, "institution_id": current_user["id"]},
        {"$set": {**rule.dict(), "updated_at": datetime.now(timezone.utc).isoformat()}}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Rule not found")
    
    return {"message": "Rule updated"}

@router.delete("/automation-rules/{rule_id}")
async def delete_automation_rule(rule_id: str, current_user: dict = Depends(get_current_user)):
    """Delete an automation rule"""
    result = await db.automation_rules.delete_one(
        {"id": rule_id, "institution_id": current_user["id"], "is_default": {"$ne": True}}
    )
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Rule not found or is default")
    
    return {"message": "Rule deleted"}

# ==================== LEAD SCORING ====================

def calculate_lead_score(lead: dict) -> dict:
    """Calculate lead score based on multiple factors"""
    score = 0
    breakdown = []
    
    students = lead.get("students_count", 0)
    if students >= 1000:
        score += 50
        breakdown.append({"factor": "Large institution (1000+ students)", "points": 50})
    elif students >= 501:
        score += 40
        breakdown.append({"factor": "Medium-large institution (501-1000)", "points": 40})
    elif students >= 201:
        score += 30
        breakdown.append({"factor": "Medium institution (201-500)", "points": 30})
    elif students >= 51:
        score += 20
        breakdown.append({"factor": "Small-medium institution (51-200)", "points": 20})
    elif students >= 1:
        score += 10
        breakdown.append({"factor": "Small institution (1-50)", "points": 10})
    
    exam_count = len(lead.get("exam_types", []))
    if exam_count >= 4:
        score += 25
        breakdown.append({"factor": "Multiple exam types (4+)", "points": 25})
    elif exam_count >= 2:
        score += 15
        breakdown.append({"factor": "Multiple exam types (2-3)", "points": 15})
    elif exam_count >= 1:
        score += 5
        breakdown.append({"factor": "Single exam type", "points": 5})
    
    source = lead.get("source", "")
    source_scores = {"referral": 30, "organic": 20, "free_trial_form": 25, "demo_request": 25, "paid_ad": 15, "cold_outreach": 5}
    if source in source_scores:
        score += source_scores[source]
        breakdown.append({"factor": f"Lead source: {source}", "points": source_scores[source]})
    
    stage = lead.get("stage", "new")
    stage_scores = {"new": 0, "contacted": 5, "demo_scheduled": 15, "demo_completed": 25, "proposal_sent": 35, "negotiating": 45}
    if stage in stage_scores:
        score += stage_scores[stage]
        breakdown.append({"factor": f"Pipeline stage: {stage}", "points": stage_scores[stage]})
    
    activities = lead.get("activities", [])
    if len(activities) >= 5:
        score += 15
        breakdown.append({"factor": "High engagement (5+ activities)", "points": 15})
    elif len(activities) >= 2:
        score += 10
        breakdown.append({"factor": "Medium engagement (2-4 activities)", "points": 10})
    
    grade = "hot" if score >= 80 else "warm" if score >= 50 else "cold"
    
    return {
        "score": min(score, 100),
        "grade": grade,
        "breakdown": breakdown
    }

@router.get("/leads/{lead_id}/score")
async def get_lead_score(lead_id: str, current_user: dict = Depends(get_current_user)):
    """Get calculated score for a lead"""
    if current_user["user_type"] not in ["admin", "institution"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    lead = await db.crm_leads.find_one({"id": lead_id})
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    score_data = calculate_lead_score(lead)
    
    await db.crm_leads.update_one(
        {"id": lead_id},
        {"$set": {"lead_score": score_data["score"], "lead_grade": score_data["grade"]}}
    )
    
    return score_data

@router.get("/analytics/scoring")
async def get_scoring_analytics(current_user: dict = Depends(get_current_user)):
    """Get lead scoring analytics"""
    if current_user["user_type"] not in ["admin", "institution"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    query = {}
    if current_user["user_type"] == "institution":
        query["$or"] = [
            {"created_by": current_user["id"]},
            {"assigned_to": current_user["id"]}
        ]
    
    leads = await db.crm_leads.find(query).to_list(1000)
    
    hot_leads = []
    warm_leads = []
    cold_leads = []
    
    for lead in leads:
        score_data = calculate_lead_score(lead)
        lead_summary = {
            "id": lead["id"],
            "institution_name": lead.get("institution_name", ""),
            "score": score_data["score"],
            "stage": lead.get("stage", "")
        }
        if score_data["grade"] == "hot":
            hot_leads.append(lead_summary)
        elif score_data["grade"] == "warm":
            warm_leads.append(lead_summary)
        else:
            cold_leads.append(lead_summary)
    
    return {
        "summary": {
            "hot_count": len(hot_leads),
            "warm_count": len(warm_leads),
            "cold_count": len(cold_leads)
        },
        "hot_leads": sorted(hot_leads, key=lambda x: x["score"], reverse=True)[:10],
        "warm_leads": sorted(warm_leads, key=lambda x: x["score"], reverse=True)[:10],
        "cold_leads": sorted(cold_leads, key=lambda x: x["score"], reverse=True)[:5]
    }
