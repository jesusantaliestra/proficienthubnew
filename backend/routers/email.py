"""Email notifications router - Configurable email service per institution"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
import httpx
import os

from database import db
from utils.auth import get_current_user

router = APIRouter(prefix="/email", tags=["Email"])

# Models
class EmailConfig(BaseModel):
    provider: str  # sendgrid, resend, smtp, mailgun
    api_key: Optional[str] = None
    smtp_host: Optional[str] = None
    smtp_port: Optional[int] = None
    smtp_user: Optional[str] = None
    smtp_password: Optional[str] = None
    from_email: str
    from_name: Optional[str] = None
    enabled: bool = False

class EmailTemplate(BaseModel):
    template_id: str
    name: str
    subject: str
    html_content: str
    variables: List[str] = []

class SendEmailRequest(BaseModel):
    to_email: EmailStr
    to_name: Optional[str] = None
    template_id: str
    variables: Dict[str, str] = {}

class SendBulkEmailRequest(BaseModel):
    recipients: List[Dict[str, str]]  # [{email, name, ...variables}]
    template_id: str

# Email provider implementations
async def send_via_sendgrid(config: dict, to_email: str, to_name: str, subject: str, html_content: str):
    """Send email via SendGrid"""
    try:
        api_key = config.get("api_key")
        from_email = config.get("from_email")
        from_name = config.get("from_name", "ProficientHub")
        
        if not api_key or not from_email:
            return {"success": False, "error": "Missing SendGrid configuration"}
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.sendgrid.com/v3/mail/send",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "personalizations": [{"to": [{"email": to_email, "name": to_name}]}],
                    "from": {"email": from_email, "name": from_name},
                    "subject": subject,
                    "content": [{"type": "text/html", "value": html_content}]
                },
                timeout=15.0
            )
            
            if response.status_code in [200, 202]:
                return {"success": True, "provider": "sendgrid"}
            return {"success": False, "error": response.text}
    except Exception as e:
        return {"success": False, "error": str(e)}

async def send_via_resend(config: dict, to_email: str, to_name: str, subject: str, html_content: str):
    """Send email via Resend"""
    try:
        api_key = config.get("api_key")
        from_email = config.get("from_email")
        from_name = config.get("from_name", "ProficientHub")
        
        if not api_key or not from_email:
            return {"success": False, "error": "Missing Resend configuration"}
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.resend.com/emails",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "from": f"{from_name} <{from_email}>",
                    "to": [to_email],
                    "subject": subject,
                    "html": html_content
                },
                timeout=15.0
            )
            
            if response.status_code in [200, 201]:
                return {"success": True, "provider": "resend", "id": response.json().get("id")}
            return {"success": False, "error": response.text}
    except Exception as e:
        return {"success": False, "error": str(e)}

async def send_via_smtp(config: dict, to_email: str, to_name: str, subject: str, html_content: str):
    """Send email via SMTP"""
    try:
        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart
        
        smtp_host = config.get("smtp_host")
        smtp_port = config.get("smtp_port", 587)
        smtp_user = config.get("smtp_user")
        smtp_password = config.get("smtp_password")
        from_email = config.get("from_email")
        from_name = config.get("from_name", "ProficientHub")
        
        if not all([smtp_host, smtp_user, smtp_password, from_email]):
            return {"success": False, "error": "Missing SMTP configuration"}
        
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"{from_name} <{from_email}>"
        msg["To"] = to_email
        
        html_part = MIMEText(html_content, "html")
        msg.attach(html_part)
        
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.sendmail(from_email, to_email, msg.as_string())
        
        return {"success": True, "provider": "smtp"}
    except Exception as e:
        return {"success": False, "error": str(e)}

# Provider routing
EMAIL_PROVIDERS = {
    "sendgrid": send_via_sendgrid,
    "resend": send_via_resend,
    "smtp": send_via_smtp,
}

# Default email templates
DEFAULT_TEMPLATES = {
    "welcome": {
        "name": "Welcome Email",
        "subject": "Welcome to {{institution_name}}!",
        "html_content": """
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h1 style="color: #7c3aed;">Welcome, {{student_name}}!</h1>
            <p>You've been registered at <strong>{{institution_name}}</strong>.</p>
            <p>Your login credentials:</p>
            <ul>
                <li>Email: {{email}}</li>
                <li>Temporary Password: {{password}}</li>
            </ul>
            <p>Please login and change your password immediately.</p>
            <a href="{{login_url}}" style="background: #7c3aed; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px;">Login Now</a>
        </div>
        """,
        "variables": ["institution_name", "student_name", "email", "password", "login_url"]
    },
    "exam_reminder": {
        "name": "Exam Reminder",
        "subject": "Reminder: Your {{exam_type}} exam is approaching",
        "html_content": """
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h1 style="color: #7c3aed;">Exam Reminder</h1>
            <p>Hi {{student_name}},</p>
            <p>Your <strong>{{exam_type}}</strong> exam is scheduled for <strong>{{exam_date}}</strong>.</p>
            <p>Keep practicing to improve your score!</p>
            <a href="{{practice_url}}" style="background: #7c3aed; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px;">Practice Now</a>
        </div>
        """,
        "variables": ["student_name", "exam_type", "exam_date", "practice_url"]
    },
    "progress_report": {
        "name": "Weekly Progress Report",
        "subject": "Your Weekly Progress Report",
        "html_content": """
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h1 style="color: #7c3aed;">Weekly Progress Report</h1>
            <p>Hi {{student_name}},</p>
            <p>Here's your progress summary for this week:</p>
            <ul>
                <li>Practice Sessions: {{practice_count}}</li>
                <li>Average Score: {{avg_score}}%</li>
                <li>Time Practiced: {{time_practiced}}</li>
            </ul>
            <p>Pass Probability: <strong>{{pass_probability}}%</strong></p>
            <a href="{{dashboard_url}}" style="background: #7c3aed; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px;">View Full Report</a>
        </div>
        """,
        "variables": ["student_name", "practice_count", "avg_score", "time_practiced", "pass_probability", "dashboard_url"]
    },
    "critical_alert": {
        "name": "Critical Alert (Superadmin)",
        "subject": "⚠️ Critical Alert: {{alert_title}}",
        "html_content": """
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h1 style="color: #dc2626;">⚠️ Critical Alert</h1>
            <p><strong>{{alert_title}}</strong></p>
            <p>{{alert_description}}</p>
            <p>Institution: {{institution_name}}</p>
            <p>Time: {{timestamp}}</p>
            <a href="{{dashboard_url}}" style="background: #dc2626; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px;">View Dashboard</a>
        </div>
        """,
        "variables": ["alert_title", "alert_description", "institution_name", "timestamp", "dashboard_url"]
    }
}

def render_template(template: dict, variables: dict) -> tuple:
    """Render template with variables"""
    subject = template["subject"]
    html = template["html_content"]
    
    for key, value in variables.items():
        placeholder = "{{" + key + "}}"
        subject = subject.replace(placeholder, str(value))
        html = html.replace(placeholder, str(value))
    
    return subject, html

@router.get("/providers")
async def get_email_providers():
    """Get list of supported email providers"""
    return {
        "providers": [
            {"id": "sendgrid", "name": "SendGrid", "description": "Reliable email delivery service"},
            {"id": "resend", "name": "Resend", "description": "Modern email API for developers"},
            {"id": "smtp", "name": "SMTP", "description": "Generic SMTP server"},
            {"id": "mailgun", "name": "Mailgun", "description": "Email API service (coming soon)"}
        ]
    }

@router.get("/config")
async def get_email_config(current_user: dict = Depends(get_current_user)):
    """Get email configuration for institution"""
    if current_user["user_type"] != "institution":
        raise HTTPException(status_code=403, detail="Institution access required")
    
    settings = await db.institution_settings.find_one(
        {"institution_id": current_user["id"]},
        {"_id": 0, "email": 1}
    )
    
    config = settings.get("email", {}) if settings else {}
    
    # Hide sensitive data
    safe_config = {
        "provider": config.get("provider"),
        "from_email": config.get("from_email"),
        "from_name": config.get("from_name"),
        "enabled": config.get("enabled", False),
        "has_credentials": bool(config.get("api_key") or config.get("smtp_host"))
    }
    
    return safe_config

@router.post("/config")
async def update_email_config(
    config: EmailConfig,
    current_user: dict = Depends(get_current_user)
):
    """Update email configuration"""
    if current_user["user_type"] != "institution":
        raise HTTPException(status_code=403, detail="Institution access required")
    
    config_data = config.dict(exclude_none=True)
    config_data["updated_at"] = datetime.now(timezone.utc).isoformat()
    
    await db.institution_settings.update_one(
        {"institution_id": current_user["id"]},
        {"$set": {"email": config_data}},
        upsert=True
    )
    
    return {"success": True, "message": "Email configuration updated"}

@router.get("/templates")
async def get_email_templates(current_user: dict = Depends(get_current_user)):
    """Get email templates"""
    if current_user["user_type"] != "institution":
        raise HTTPException(status_code=403, detail="Institution access required")
    
    # Get custom templates
    custom = await db.email_templates.find(
        {"institution_id": current_user["id"]},
        {"_id": 0}
    ).to_list(100)
    
    # Merge with defaults
    templates = {**DEFAULT_TEMPLATES}
    for t in custom:
        templates[t["template_id"]] = t
    
    return {"templates": templates}

@router.post("/templates")
async def save_email_template(
    template: EmailTemplate,
    current_user: dict = Depends(get_current_user)
):
    """Save a custom email template"""
    if current_user["user_type"] != "institution":
        raise HTTPException(status_code=403, detail="Institution access required")
    
    template_data = template.dict()
    template_data["institution_id"] = current_user["id"]
    template_data["updated_at"] = datetime.now(timezone.utc).isoformat()
    
    await db.email_templates.update_one(
        {"institution_id": current_user["id"], "template_id": template.template_id},
        {"$set": template_data},
        upsert=True
    )
    
    return {"success": True, "message": f"Template {template.template_id} saved"}

@router.post("/send")
async def send_email(
    request: SendEmailRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user)
):
    """Send an email using configured provider"""
    if current_user["user_type"] != "institution":
        raise HTTPException(status_code=403, detail="Institution access required")
    
    # Get email config
    settings = await db.institution_settings.find_one({"institution_id": current_user["id"]})
    email_config = settings.get("email", {}) if settings else {}
    
    if not email_config.get("enabled"):
        raise HTTPException(status_code=400, detail="Email not configured")
    
    # Get template
    template = DEFAULT_TEMPLATES.get(request.template_id)
    if not template:
        custom = await db.email_templates.find_one({
            "institution_id": current_user["id"],
            "template_id": request.template_id
        })
        if custom:
            template = custom
        else:
            raise HTTPException(status_code=404, detail="Template not found")
    
    # Render template
    subject, html = render_template(template, request.variables)
    
    # Get provider handler
    provider = email_config.get("provider")
    handler = EMAIL_PROVIDERS.get(provider)
    
    if not handler:
        raise HTTPException(status_code=400, detail=f"Provider {provider} not supported")
    
    # Send email
    result = await handler(email_config, request.to_email, request.to_name or "", subject, html)
    
    # Log
    await db.email_logs.insert_one({
        "institution_id": current_user["id"],
        "to_email": request.to_email,
        "template_id": request.template_id,
        "provider": provider,
        "status": "sent" if result.get("success") else "failed",
        "result": result,
        "created_at": datetime.now(timezone.utc).isoformat()
    })
    
    return result

@router.post("/test")
async def test_email_config(current_user: dict = Depends(get_current_user)):
    """Test email configuration by sending a test email"""
    if current_user["user_type"] != "institution":
        raise HTTPException(status_code=403, detail="Institution access required")
    
    settings = await db.institution_settings.find_one({"institution_id": current_user["id"]})
    email_config = settings.get("email", {}) if settings else {}
    
    if not email_config.get("enabled"):
        return {"success": False, "error": "Email not enabled"}
    
    provider = email_config.get("provider")
    handler = EMAIL_PROVIDERS.get(provider)
    
    if not handler:
        return {"success": False, "error": f"Provider {provider} not supported"}
    
    # Send test email to institution's email
    result = await handler(
        email_config,
        current_user["email"],
        current_user.get("name", ""),
        "Test Email from ProficientHub",
        "<h1>Test Email</h1><p>Your email configuration is working correctly!</p>"
    )
    
    return result

@router.get("/logs")
async def get_email_logs(
    limit: int = 50,
    status: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """Get email sending logs"""
    if current_user["user_type"] != "institution":
        raise HTTPException(status_code=403, detail="Institution access required")
    
    query = {"institution_id": current_user["id"]}
    if status:
        query["status"] = status
    
    logs = await db.email_logs.find(
        query,
        {"_id": 0}
    ).sort("created_at", -1).limit(limit).to_list(limit)
    
    return {"logs": logs, "total": len(logs)}
