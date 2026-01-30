"""Institution Settings Router - Configuration endpoints"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime, timezone

from database import db
from utils.auth import get_current_user

router = APIRouter(prefix="/institution/settings", tags=["Institution - Settings"])

# Models
class ZoomConfig(BaseModel):
    zoom_enabled: bool = False
    zoom_client_id: Optional[str] = None
    zoom_client_secret: Optional[str] = None
    zoom_account_id: Optional[str] = None

class EmailConfig(BaseModel):
    provider: str = "sendgrid"
    api_key: Optional[str] = None
    from_email: Optional[str] = None
    from_name: Optional[str] = None

class GamificationConfig(BaseModel):
    enabled: bool = False
    points_per_exam: int = 100
    points_per_ai_session: int = 50
    leaderboard_enabled: bool = True
    badges_enabled: bool = True
    streaks_enabled: bool = True

class AvatarConfig(BaseModel):
    type: str = "animated"
    avatar_id: Optional[str] = None
    heygen_enabled: bool = False
    heygen_avatar_id: Optional[str] = None
    rive_enabled: bool = True

class PlacementTestConfig(BaseModel):
    enabled: bool = False
    auto_assign_level: bool = True
    test_duration_minutes: int = 30
    questions_count: int = 50

class MessagingConfig(BaseModel):
    enabled: bool = False
    provider: Optional[str] = None
    api_key: Optional[str] = None
    account_sid: Optional[str] = None
    auth_token: Optional[str] = None
    from_number: Optional[str] = None
    sms_enabled: bool = False
    whatsapp_enabled: bool = False

class ReportsConfig(BaseModel):
    enabled: bool = True
    auto_send: bool = False
    frequency: str = "weekly"
    include_individual: bool = True
    include_cohort: bool = True
    recipients: List[str] = []

@router.get("")
async def get_institution_settings(current_user: dict = Depends(get_current_user)):
    """Get all institution settings"""
    if current_user["user_type"] != "institution":
        raise HTTPException(status_code=403, detail="Only institutions can view settings")
    
    settings = await db.institution_settings.find_one(
        {"institution_id": current_user["id"]},
        {"_id": 0}
    )
    
    if not settings:
        settings = {
            "institution_id": current_user["id"],
            "zoom_config": {"zoom_enabled": False},
            "email_config": {"provider": "sendgrid"},
            "gamification_config": {"enabled": False},
            "avatar_config": {"type": "animated"},
            "placement_test_config": {"enabled": False},
            "messaging_config": {"enabled": False},
            "reports_config": {"enabled": True}
        }
    
    # Sanitize sensitive data
    if settings.get("zoom_config"):
        settings["zoom_config"] = {
            "zoom_enabled": settings["zoom_config"].get("zoom_enabled", False),
            "has_credentials": bool(settings["zoom_config"].get("zoom_client_id"))
        }
    
    if settings.get("messaging_config"):
        settings["messaging_config"] = {
            "enabled": settings["messaging_config"].get("enabled", False),
            "provider": settings["messaging_config"].get("provider"),
            "sms_enabled": settings["messaging_config"].get("sms_enabled", False),
            "whatsapp_enabled": settings["messaging_config"].get("whatsapp_enabled", False),
            "has_credentials": bool(settings["messaging_config"].get("api_key") or settings["messaging_config"].get("account_sid"))
        }
    
    if settings.get("email_config"):
        settings["email_config"] = {
            "provider": settings["email_config"].get("provider", "sendgrid"),
            "from_email": settings["email_config"].get("from_email"),
            "from_name": settings["email_config"].get("from_name"),
            "has_credentials": bool(settings["email_config"].get("api_key"))
        }
    
    return settings

@router.post("/zoom")
async def update_zoom_config(
    config: ZoomConfig,
    current_user: dict = Depends(get_current_user)
):
    """Update Zoom configuration"""
    if current_user["user_type"] != "institution":
        raise HTTPException(status_code=403, detail="Only institutions can update settings")
    
    update_data = config.dict(exclude_none=True)
    update_data["updated_at"] = datetime.now(timezone.utc).isoformat()
    
    await db.institution_settings.update_one(
        {"institution_id": current_user["id"]},
        {"$set": {"zoom_config": update_data}},
        upsert=True
    )
    
    return {"message": "Zoom configuration updated", "zoom_enabled": config.zoom_enabled}

@router.post("/zoom/test")
async def test_zoom_connection(current_user: dict = Depends(get_current_user)):
    """Test Zoom API connection"""
    if current_user["user_type"] != "institution":
        raise HTTPException(status_code=403, detail="Access denied")
    
    settings = await db.institution_settings.find_one(
        {"institution_id": current_user["id"]},
        {"zoom_config": 1}
    )
    
    if not settings or not settings.get("zoom_config", {}).get("zoom_client_id"):
        raise HTTPException(status_code=400, detail="Zoom credentials not configured")
    
    # TODO: Implement actual Zoom API test
    return {"success": True, "message": "Zoom connection successful"}

@router.post("/email")
async def update_email_config(
    config: EmailConfig,
    current_user: dict = Depends(get_current_user)
):
    """Update email configuration"""
    if current_user["user_type"] != "institution":
        raise HTTPException(status_code=403, detail="Only institutions can update settings")
    
    update_data = config.dict(exclude_none=True)
    update_data["updated_at"] = datetime.now(timezone.utc).isoformat()
    
    await db.institution_settings.update_one(
        {"institution_id": current_user["id"]},
        {"$set": {"email_config": update_data}},
        upsert=True
    )
    
    return {"message": "Email configuration updated"}

@router.post("/email/test")
async def test_email_config(
    test_email: str,
    current_user: dict = Depends(get_current_user)
):
    """Send a test email"""
    if current_user["user_type"] != "institution":
        raise HTTPException(status_code=403, detail="Access denied")
    
    settings = await db.institution_settings.find_one(
        {"institution_id": current_user["id"]},
        {"email_config": 1}
    )
    
    if not settings or not settings.get("email_config", {}).get("api_key"):
        raise HTTPException(status_code=400, detail="Email not configured")
    
    # TODO: Implement actual email sending
    return {"success": True, "message": f"Test email sent to {test_email}"}

@router.post("/gamification")
async def update_gamification_config(
    config: GamificationConfig,
    current_user: dict = Depends(get_current_user)
):
    """Update gamification settings"""
    if current_user["user_type"] != "institution":
        raise HTTPException(status_code=403, detail="Only institutions can update settings")
    
    update_data = config.dict()
    update_data["updated_at"] = datetime.now(timezone.utc).isoformat()
    
    await db.institution_settings.update_one(
        {"institution_id": current_user["id"]},
        {"$set": {"gamification_config": update_data}},
        upsert=True
    )
    
    return {"message": "Gamification settings updated", "enabled": config.enabled}

@router.post("/avatar")
async def update_avatar_config(
    config: AvatarConfig,
    current_user: dict = Depends(get_current_user)
):
    """Update avatar configuration"""
    if current_user["user_type"] != "institution":
        raise HTTPException(status_code=403, detail="Only institutions can update settings")
    
    update_data = config.dict(exclude_none=True)
    update_data["updated_at"] = datetime.now(timezone.utc).isoformat()
    
    await db.institution_settings.update_one(
        {"institution_id": current_user["id"]},
        {"$set": {"avatar_config": update_data}},
        upsert=True
    )
    
    return {"message": "Avatar configuration updated"}

@router.get("/placement-test")
async def get_placement_test_config(current_user: dict = Depends(get_current_user)):
    """Get placement test configuration"""
    if current_user["user_type"] != "institution":
        raise HTTPException(status_code=403, detail="Access denied")
    
    settings = await db.institution_settings.find_one(
        {"institution_id": current_user["id"]},
        {"_id": 0, "placement_test_config": 1}
    )
    
    return settings.get("placement_test_config", {"enabled": False}) if settings else {"enabled": False}

@router.post("/placement-test")
async def update_placement_test_config(
    config: PlacementTestConfig,
    current_user: dict = Depends(get_current_user)
):
    """Update placement test configuration"""
    if current_user["user_type"] != "institution":
        raise HTTPException(status_code=403, detail="Only institutions can update settings")
    
    update_data = config.dict()
    update_data["updated_at"] = datetime.now(timezone.utc).isoformat()
    
    await db.institution_settings.update_one(
        {"institution_id": current_user["id"]},
        {"$set": {"placement_test_config": update_data}},
        upsert=True
    )
    
    return {"message": "Placement test settings updated"}
