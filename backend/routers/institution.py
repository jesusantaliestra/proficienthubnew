"""Institution router - Institution management and settings"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
import uuid
import base64

from database import db
from utils.auth import get_current_user

router = APIRouter(prefix="/institution", tags=["Institution"])

# Models
class InstitutionBrandingUpdate(BaseModel):
    name: str
    slug: Optional[str] = None
    logo_url: Optional[str] = None
    primary_color: Optional[str] = None
    secondary_color: Optional[str] = None
    accent_color: Optional[str] = None
    font_family: Optional[str] = None
    custom_domain: Optional[str] = None
    tagline: Optional[str] = None
    description: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    social_links: Optional[Dict[str, str]] = None

class InstitutionSettingsUpdate(BaseModel):
    ai_config: Optional[Dict[str, Any]] = None
    avatar_config: Optional[Dict[str, Any]] = None
    zoom_config: Optional[Dict[str, Any]] = None
    email_config: Optional[Dict[str, Any]] = None
    gamification_config: Optional[Dict[str, Any]] = None
    messaging_config: Optional[Dict[str, Any]] = None
    reports_config: Optional[Dict[str, Any]] = None

@router.get("/branding")
async def get_institution_branding(current_user: dict = Depends(get_current_user)):
    """Get institution branding settings"""
    if current_user["user_type"] not in ["institution", "student"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    institution_id = current_user.get("institution_id") or current_user.get("id")
    
    branding = await db.institution_branding.find_one(
        {"institution_id": institution_id},
        {"_id": 0}
    )
    
    if not branding:
        # Get institution name from user
        inst = await db.users.find_one(
            {"id": institution_id},
            {"_id": 0, "institution_name": 1, "name": 1}
        )
        branding = {
            "institution_id": institution_id,
            "name": inst.get("institution_name", inst.get("name", "Institution")),
            "primary_color": "#7c3aed",
            "secondary_color": "#4f46e5",
            "accent_color": "#10b981"
        }
    
    return branding

@router.put("/branding")
async def update_institution_branding(
    branding: InstitutionBrandingUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Update institution branding"""
    if current_user["user_type"] != "institution":
        raise HTTPException(status_code=403, detail="Only institutions can update branding")
    
    branding_data = branding.dict(exclude_none=True)
    branding_data["institution_id"] = current_user["id"]
    branding_data["updated_at"] = datetime.now(timezone.utc).isoformat()
    
    # Generate slug if not provided
    if not branding_data.get("slug"):
        branding_data["slug"] = branding.name.lower().replace(" ", "-").replace("'", "")
    
    await db.institution_branding.update_one(
        {"institution_id": current_user["id"]},
        {"$set": branding_data},
        upsert=True
    )
    
    return {"message": "Branding updated successfully", "slug": branding_data["slug"]}

@router.get("/branding/{slug}")
async def get_institution_branding_by_slug(slug: str):
    """Get institution branding by slug (public endpoint for white-label)"""
    branding = await db.institution_branding.find_one(
        {"slug": slug},
        {"_id": 0}
    )
    
    if not branding:
        raise HTTPException(status_code=404, detail="Institution not found")
    
    return branding

@router.get("/settings")
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
            "ai_config": {"enabled": True, "default_agent": "tutor"},
            "avatar_config": {"type": "animated", "avatar_id": "default"},
            "gamification_config": {"enabled": False},
            "zoom_config": {"zoom_enabled": False},
            "messaging_config": {"enabled": False},
            "reports_config": {"enabled": False}
        }
    
    # Hide sensitive credentials
    if settings.get("zoom_config"):
        settings["zoom_config"] = {
            k: v for k, v in settings["zoom_config"].items() 
            if k not in ["zoom_client_secret", "zoom_account_id"]
        }
        settings["zoom_config"]["has_credentials"] = bool(
            settings.get("zoom_config", {}).get("zoom_client_id")
        )
    
    if settings.get("messaging_config"):
        safe_msg = {
            "enabled": settings["messaging_config"].get("enabled", False),
            "provider": settings["messaging_config"].get("provider"),
            "sms_enabled": settings["messaging_config"].get("sms_enabled", False),
            "whatsapp_enabled": settings["messaging_config"].get("whatsapp_enabled", False),
            "has_credentials": bool(
                settings["messaging_config"].get("api_key") or 
                settings["messaging_config"].get("account_sid")
            )
        }
        settings["messaging_config"] = safe_msg
    
    return settings

@router.put("/settings")
async def update_institution_settings(
    settings: InstitutionSettingsUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Update institution settings"""
    if current_user["user_type"] != "institution":
        raise HTTPException(status_code=403, detail="Only institutions can update settings")
    
    update_data = {"updated_at": datetime.now(timezone.utc).isoformat()}
    
    settings_dict = settings.dict(exclude_none=True)
    for key, value in settings_dict.items():
        if value is not None:
            # Map to correct field names
            field_map = {
                "ai_config": "ai",
                "avatar_config": "avatar",
                "zoom_config": "zoom",
                "email_config": "email_templates",
                "gamification_config": "gamification",
                "messaging_config": "messaging",
                "reports_config": "reports"
            }
            field_name = field_map.get(key, key)
            update_data[field_name] = value
    
    await db.institution_settings.update_one(
        {"institution_id": current_user["id"]},
        {"$set": update_data},
        upsert=True
    )
    
    return {"message": "Settings updated successfully"}

@router.get("/students")
async def get_institution_students(
    limit: int = 50,
    skip: int = 0,
    search: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """Get students for the institution"""
    if current_user["user_type"] != "institution":
        raise HTTPException(status_code=403, detail="Only institutions can view students")
    
    query = {"institution_id": current_user["id"], "user_type": "student"}
    
    if search:
        query["$or"] = [
            {"name": {"$regex": search, "$options": "i"}},
            {"email": {"$regex": search, "$options": "i"}}
        ]
    
    students = await db.users.find(
        query,
        {"_id": 0, "password_hash": 0}
    ).skip(skip).limit(limit).to_list(limit)
    
    total = await db.users.count_documents(query)
    
    return {
        "students": students,
        "total": total,
        "limit": limit,
        "skip": skip
    }

@router.get("/stats")
async def get_institution_stats(current_user: dict = Depends(get_current_user)):
    """Get institution statistics"""
    if current_user["user_type"] != "institution":
        raise HTTPException(status_code=403, detail="Only institutions can view stats")
    
    inst_id = current_user["id"]
    
    # Student count
    student_count = await db.users.count_documents({
        "institution_id": inst_id,
        "user_type": "student"
    })
    
    # Exam attempts
    total_attempts = await db.exam_attempts.count_documents({"institution_id": inst_id})
    
    # Average score
    avg_pipeline = [
        {"$match": {"institution_id": inst_id}},
        {"$group": {"_id": None, "avg_score": {"$avg": "$score"}}}
    ]
    avg_result = await db.exam_attempts.aggregate(avg_pipeline).to_list(1)
    avg_score = avg_result[0]["avg_score"] if avg_result else 0
    
    # AI credits
    credits = await db.ai_credits.find_one({"user_id": inst_id}, {"_id": 0})
    
    # Active students (last 7 days)
    week_ago = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()
    active_students = await db.exam_attempts.distinct(
        "user_id",
        {"institution_id": inst_id, "created_at": {"$gte": week_ago}}
    )
    
    return {
        "student_count": student_count,
        "total_exam_attempts": total_attempts,
        "average_score": round(avg_score, 2) if avg_score else 0,
        "active_students_7d": len(active_students),
        "ai_credits": {
            "total": credits.get("total_credits", 0) if credits else 0,
            "used": credits.get("used_credits", 0) if credits else 0,
            "available": (credits.get("total_credits", 0) - credits.get("used_credits", 0)) if credits else 0
        }
    }

@router.post("/logo")
async def upload_institution_logo(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    """Upload institution logo"""
    if current_user["user_type"] != "institution":
        raise HTTPException(status_code=403, detail="Only institutions can upload logo")
    
    # Read file and convert to base64
    contents = await file.read()
    b64_content = base64.b64encode(contents).decode('utf-8')
    
    # Determine content type
    content_type = file.content_type or "image/png"
    data_url = f"data:{content_type};base64,{b64_content}"
    
    # Update branding
    await db.institution_branding.update_one(
        {"institution_id": current_user["id"]},
        {"$set": {"logo_url": data_url, "updated_at": datetime.now(timezone.utc).isoformat()}},
        upsert=True
    )
    
    return {"message": "Logo uploaded successfully", "logo_url": data_url}

# Import timedelta for stats
from datetime import timedelta
