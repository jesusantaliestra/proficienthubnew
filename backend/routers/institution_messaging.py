"""Institution Messaging & Reports Router"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone, timedelta
import uuid

from database import db
from utils.auth import get_current_user

router = APIRouter(prefix="/institution", tags=["Institution - Messaging & Reports"])

# Models
class MessagingConfig(BaseModel):
    enabled: bool = False
    provider: Optional[str] = None
    api_key: Optional[str] = None
    account_sid: Optional[str] = None
    auth_token: Optional[str] = None
    from_number: Optional[str] = None
    sms_enabled: bool = False
    whatsapp_enabled: bool = False

class BulkMessageRequest(BaseModel):
    message: str
    recipients: List[str]  # Student IDs
    channel: str = "email"  # email, sms, whatsapp

class EmailTemplate(BaseModel):
    name: str
    subject: str
    body: str
    template_type: str = "custom"
    variables: List[str] = []

class ReportsConfig(BaseModel):
    enabled: bool = True
    auto_send: bool = False
    frequency: str = "weekly"
    include_individual: bool = True
    include_cohort: bool = True
    recipients: List[str] = []

class ReportGenerateRequest(BaseModel):
    report_type: str = "overview"
    date_from: Optional[str] = None
    date_to: Optional[str] = None
    student_ids: Optional[List[str]] = None
    format: str = "pdf"

# Messaging Endpoints
@router.get("/messaging/config")
async def get_messaging_config(current_user: dict = Depends(get_current_user)):
    """Get messaging configuration"""
    if current_user["user_type"] != "institution":
        raise HTTPException(status_code=403, detail="Access denied")
    
    settings = await db.institution_settings.find_one(
        {"institution_id": current_user["id"]},
        {"_id": 0, "messaging_config": 1}
    )
    
    config = settings.get("messaging_config", {}) if settings else {}
    
    return {
        "enabled": config.get("enabled", False),
        "provider": config.get("provider"),
        "sms_enabled": config.get("sms_enabled", False),
        "whatsapp_enabled": config.get("whatsapp_enabled", False),
        "has_credentials": bool(config.get("api_key") or config.get("account_sid"))
    }

@router.get("/messaging/providers")
async def get_messaging_providers():
    """Get available messaging providers"""
    return {
        "providers": [
            {"id": "twilio", "name": "Twilio", "supports": ["sms", "whatsapp"]},
            {"id": "sendgrid", "name": "SendGrid", "supports": ["email"]},
            {"id": "messagebird", "name": "MessageBird", "supports": ["sms", "whatsapp"]},
            {"id": "vonage", "name": "Vonage", "supports": ["sms"]}
        ]
    }

@router.post("/messaging/config")
async def update_messaging_config(
    config: MessagingConfig,
    current_user: dict = Depends(get_current_user)
):
    """Update messaging configuration"""
    if current_user["user_type"] != "institution":
        raise HTTPException(status_code=403, detail="Only institutions can update settings")
    
    update_data = config.dict(exclude_none=True)
    update_data["updated_at"] = datetime.now(timezone.utc).isoformat()
    
    await db.institution_settings.update_one(
        {"institution_id": current_user["id"]},
        {"$set": {"messaging_config": update_data}},
        upsert=True
    )
    
    return {"message": "Messaging configuration updated"}

@router.post("/messaging/test")
async def test_messaging(
    channel: str = "email",
    test_recipient: str = None,
    current_user: dict = Depends(get_current_user)
):
    """Send a test message"""
    if current_user["user_type"] != "institution":
        raise HTTPException(status_code=403, detail="Access denied")
    
    # TODO: Implement actual message sending
    return {"success": True, "message": f"Test {channel} sent to {test_recipient}"}

@router.post("/messaging/send-bulk")
async def send_bulk_message(
    request: BulkMessageRequest,
    current_user: dict = Depends(get_current_user)
):
    """Send message to multiple students"""
    if current_user["user_type"] != "institution":
        raise HTTPException(status_code=403, detail="Only institutions can send bulk messages")
    
    # Get students
    students = await db.users.find(
        {"id": {"$in": request.recipients}, "institution_id": current_user["id"]},
        {"email": 1, "phone": 1, "name": 1}
    ).to_list(len(request.recipients))
    
    sent_count = 0
    errors = []
    
    for student in students:
        try:
            # TODO: Implement actual sending
            sent_count += 1
        except Exception as e:
            errors.append({"student": student.get("email"), "error": str(e)})
    
    # Log the bulk message
    await db.message_logs.insert_one({
        "id": str(uuid.uuid4()),
        "institution_id": current_user["id"],
        "channel": request.channel,
        "message": request.message[:200],
        "recipients_count": len(request.recipients),
        "sent_count": sent_count,
        "error_count": len(errors),
        "created_at": datetime.now(timezone.utc).isoformat()
    })
    
    return {
        "sent_count": sent_count,
        "error_count": len(errors),
        "errors": errors[:10]  # Limit errors returned
    }

# Email Templates Endpoints
@router.get("/email-templates")
async def get_email_templates(current_user: dict = Depends(get_current_user)):
    """Get all email templates for institution"""
    if current_user["user_type"] != "institution":
        raise HTTPException(status_code=403, detail="Access denied")
    
    templates = await db.email_templates.find(
        {"institution_id": current_user["id"]},
        {"_id": 0}
    ).to_list(100)
    
    # Add default templates if none exist
    if not templates:
        templates = [
            {
                "id": "default_welcome",
                "name": "Welcome Email",
                "subject": "Welcome to {{institution_name}}!",
                "body": "Dear {{student_name}},\n\nWelcome to our learning platform...",
                "template_type": "system",
                "variables": ["student_name", "institution_name", "login_url"]
            },
            {
                "id": "default_reminder",
                "name": "Study Reminder",
                "subject": "Don't forget to practice!",
                "body": "Hi {{student_name}},\n\nIt's been a while since your last practice...",
                "template_type": "system",
                "variables": ["student_name", "days_inactive"]
            }
        ]
    
    return {"templates": templates}

@router.post("/email-templates")
async def create_email_template(
    template: EmailTemplate,
    current_user: dict = Depends(get_current_user)
):
    """Create a new email template"""
    if current_user["user_type"] != "institution":
        raise HTTPException(status_code=403, detail="Only institutions can create templates")
    
    template_doc = template.dict()
    template_doc["id"] = str(uuid.uuid4())
    template_doc["institution_id"] = current_user["id"]
    template_doc["created_at"] = datetime.now(timezone.utc).isoformat()
    
    await db.email_templates.insert_one(template_doc)
    
    return {"message": "Template created", "id": template_doc["id"]}

@router.post("/email-templates/preview")
async def preview_email_template(
    template_id: str,
    sample_data: Dict[str, str] = {},
    current_user: dict = Depends(get_current_user)
):
    """Preview an email template with sample data"""
    if current_user["user_type"] != "institution":
        raise HTTPException(status_code=403, detail="Access denied")
    
    template = await db.email_templates.find_one(
        {"id": template_id, "institution_id": current_user["id"]},
        {"_id": 0}
    )
    
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    # Replace variables with sample data
    subject = template["subject"]
    body = template["body"]
    
    for var, value in sample_data.items():
        subject = subject.replace(f"{{{{{var}}}}}", value)
        body = body.replace(f"{{{{{var}}}}}", value)
    
    return {"subject": subject, "body": body}

# Reports Endpoints
@router.get("/reports/config")
async def get_reports_config(current_user: dict = Depends(get_current_user)):
    """Get reports configuration"""
    if current_user["user_type"] != "institution":
        raise HTTPException(status_code=403, detail="Access denied")
    
    settings = await db.institution_settings.find_one(
        {"institution_id": current_user["id"]},
        {"_id": 0, "reports_config": 1}
    )
    
    return settings.get("reports_config", {"enabled": True}) if settings else {"enabled": True}

@router.post("/reports/config")
async def update_reports_config(
    config: ReportsConfig,
    current_user: dict = Depends(get_current_user)
):
    """Update reports configuration"""
    if current_user["user_type"] != "institution":
        raise HTTPException(status_code=403, detail="Only institutions can update settings")
    
    update_data = config.dict()
    update_data["updated_at"] = datetime.now(timezone.utc).isoformat()
    
    await db.institution_settings.update_one(
        {"institution_id": current_user["id"]},
        {"$set": {"reports_config": update_data}},
        upsert=True
    )
    
    return {"message": "Reports configuration updated"}

@router.get("/reports/generate")
async def generate_report(
    report_type: str = "overview",
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """Generate a report"""
    if current_user["user_type"] != "institution":
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Set default date range
    if not date_to:
        date_to = datetime.now(timezone.utc).isoformat()
    if not date_from:
        date_from = (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()
    
    inst_id = current_user["id"]
    
    # Get metrics
    student_count = await db.users.count_documents({
        "institution_id": inst_id,
        "user_type": "student"
    })
    
    exam_attempts = await db.exam_attempts.count_documents({
        "institution_id": inst_id,
        "created_at": {"$gte": date_from, "$lte": date_to}
    })
    
    # Average score
    avg_pipeline = [
        {"$match": {
            "institution_id": inst_id,
            "created_at": {"$gte": date_from, "$lte": date_to}
        }},
        {"$group": {"_id": None, "avg_score": {"$avg": "$score"}}}
    ]
    avg_result = await db.exam_attempts.aggregate(avg_pipeline).to_list(1)
    avg_score = avg_result[0]["avg_score"] if avg_result else 0
    
    # Top performers
    top_pipeline = [
        {"$match": {"institution_id": inst_id}},
        {"$group": {
            "_id": "$user_id",
            "avg_score": {"$avg": "$score"},
            "attempt_count": {"$sum": 1}
        }},
        {"$sort": {"avg_score": -1}},
        {"$limit": 10}
    ]
    top_performers = await db.exam_attempts.aggregate(top_pipeline).to_list(10)
    
    return {
        "report_type": report_type,
        "date_range": {"from": date_from, "to": date_to},
        "summary": {
            "total_students": student_count,
            "exam_attempts": exam_attempts,
            "average_score": round(avg_score, 2) if avg_score else 0
        },
        "top_performers": top_performers,
        "generated_at": datetime.now(timezone.utc).isoformat()
    }

@router.get("/reports/history")
async def get_reports_history(
    limit: int = 20,
    current_user: dict = Depends(get_current_user)
):
    """Get report generation history"""
    if current_user["user_type"] != "institution":
        raise HTTPException(status_code=403, detail="Access denied")
    
    reports = await db.generated_reports.find(
        {"institution_id": current_user["id"]},
        {"_id": 0}
    ).sort("created_at", -1).limit(limit).to_list(limit)
    
    return {"reports": reports}
