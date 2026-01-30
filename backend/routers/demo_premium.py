"""Demo Premium Router - 7-day full-access demo system"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timezone, timedelta
import uuid

from database import db
from utils.auth import get_current_user

router = APIRouter(prefix="/demo", tags=["Demo Premium"])

# Models
class DemoRequestCreate(BaseModel):
    institution_name: str
    contact_email: str
    contact_name: str
    phone: Optional[str] = None
    num_students: int = 10
    exam_types: List[str] = ["oet"]
    notes: Optional[str] = None

class DemoExtensionRequest(BaseModel):
    institution_id: str
    additional_days: int = 7

class DemoConfig(BaseModel):
    default_duration_days: int = 7
    max_students_demo: int = 50
    features_enabled: List[str] = ["mock_exams", "ai_tutor", "analytics", "pdf_feedback"]
    auto_extend_eligible: bool = True

# Default demo features
DEMO_FEATURES = [
    "mock_exams",        # Full mock exams
    "ai_tutor",          # AI Tutor access
    "analytics",         # Analytics dashboard
    "pdf_feedback",      # PDF feedback generation
    "speaking_practice", # Speaking practice
    "writing_evaluation",# Writing evaluation
    "progress_tracking", # Progress tracking
    "custom_branding"    # White-label preview
]

@router.post("/request")
async def request_demo(request: DemoRequestCreate):
    """Request a premium demo (public endpoint)"""
    
    # Check if already requested
    existing = await db.demo_requests.find_one({
        "contact_email": request.contact_email,
        "status": {"$in": ["pending", "active"]}
    })
    
    if existing:
        if existing["status"] == "active":
            return {
                "success": True,
                "message": "Ya tienes una demo activa",
                "demo_id": existing["demo_id"],
                "expires_at": existing["expires_at"],
                "login_url": f"/demo-login/{existing['demo_id']}"
            }
        else:
            return {
                "success": True,
                "message": "Tu solicitud está siendo procesada",
                "request_id": existing["request_id"]
            }
    
    # Get demo config
    config = await db.platform_config.find_one({"config_type": "demo_config"})
    duration_days = config.get("default_duration_days", 7) if config else 7
    
    # Create demo request
    request_id = str(uuid.uuid4())
    demo_id = str(uuid.uuid4())[:8].upper()  # Short demo ID
    
    now = datetime.now(timezone.utc)
    expires_at = now + timedelta(days=duration_days)
    
    demo_doc = {
        "request_id": request_id,
        "demo_id": demo_id,
        "institution_name": request.institution_name,
        "contact_email": request.contact_email,
        "contact_name": request.contact_name,
        "phone": request.phone,
        "num_students": min(request.num_students, 50),  # Max 50 for demo
        "exam_types": request.exam_types,
        "notes": request.notes,
        "status": "active",  # Auto-approve demos
        "features_enabled": DEMO_FEATURES,
        "duration_days": duration_days,
        "created_at": now.isoformat(),
        "activated_at": now.isoformat(),
        "expires_at": expires_at.isoformat(),
        "extended_count": 0,
        "conversion_status": "demo"
    }
    
    await db.demo_requests.insert_one(demo_doc)
    
    # Create temporary demo institution
    demo_institution = {
        "id": f"demo_{demo_id}",
        "email": request.contact_email,
        "institution_name": f"{request.institution_name} (Demo)",
        "institution_slug": f"demo-{demo_id.lower()}",
        "user_type": "institution",
        "is_demo": True,
        "demo_id": demo_id,
        "demo_expires_at": expires_at.isoformat(),
        "features_enabled": DEMO_FEATURES,
        "created_at": now.isoformat(),
        "settings": {
            "exam_types": request.exam_types,
            "max_students": min(request.num_students, 50)
        }
    }
    
    await db.users.insert_one(demo_institution)
    
    # Log conversion funnel
    await db.conversion_funnel.insert_one({
        "demo_id": demo_id,
        "stage": "demo_activated",
        "contact_email": request.contact_email,
        "created_at": now.isoformat()
    })
    
    return {
        "success": True,
        "message": f"¡Demo activada! Tienes {duration_days} días de acceso completo.",
        "demo_id": demo_id,
        "expires_at": expires_at.isoformat(),
        "duration_days": duration_days,
        "features": DEMO_FEATURES,
        "login_url": f"/demo-login/{demo_id}",
        "credentials": {
            "email": request.contact_email,
            "temporary_password": f"Demo{demo_id}!"
        }
    }

@router.get("/status/{demo_id}")
async def get_demo_status(demo_id: str):
    """Get demo status and remaining time"""
    
    demo = await db.demo_requests.find_one(
        {"demo_id": demo_id},
        {"_id": 0}
    )
    
    if not demo:
        raise HTTPException(status_code=404, detail="Demo not found")
    
    now = datetime.now(timezone.utc)
    expires_at = datetime.fromisoformat(demo["expires_at"].replace("Z", "+00:00"))
    
    remaining_seconds = (expires_at - now).total_seconds()
    remaining_days = max(0, remaining_seconds / 86400)
    
    return {
        "demo_id": demo_id,
        "status": demo["status"],
        "institution_name": demo["institution_name"],
        "expires_at": demo["expires_at"],
        "remaining_days": round(remaining_days, 1),
        "is_expired": remaining_seconds <= 0,
        "features_enabled": demo["features_enabled"],
        "extended_count": demo.get("extended_count", 0),
        "can_extend": demo.get("extended_count", 0) < 2  # Max 2 extensions
    }

@router.post("/extend")
async def extend_demo(
    request: DemoExtensionRequest,
    current_user: dict = Depends(get_current_user)
):
    """Extend demo period (superadmin only)"""
    
    if current_user.get("user_type") != "admin":
        raise HTTPException(status_code=403, detail="Solo superadmin puede extender demos")
    
    demo = await db.demo_requests.find_one({"demo_id": request.institution_id})
    
    if not demo:
        # Try by institution_id
        demo = await db.demo_requests.find_one({"request_id": request.institution_id})
    
    if not demo:
        raise HTTPException(status_code=404, detail="Demo no encontrada")
    
    # Calculate new expiration
    current_expires = datetime.fromisoformat(demo["expires_at"].replace("Z", "+00:00"))
    now = datetime.now(timezone.utc)
    
    # If already expired, extend from now
    base_date = max(current_expires, now)
    new_expires = base_date + timedelta(days=request.additional_days)
    
    # Update demo
    await db.demo_requests.update_one(
        {"demo_id": demo["demo_id"]},
        {
            "$set": {
                "expires_at": new_expires.isoformat(),
                "status": "active"
            },
            "$inc": {"extended_count": 1}
        }
    )
    
    # Update demo institution
    await db.users.update_one(
        {"demo_id": demo["demo_id"]},
        {"$set": {"demo_expires_at": new_expires.isoformat()}}
    )
    
    return {
        "success": True,
        "message": f"Demo extendida {request.additional_days} días",
        "demo_id": demo["demo_id"],
        "new_expires_at": new_expires.isoformat(),
        "total_extensions": demo.get("extended_count", 0) + 1
    }

# Superadmin endpoints
@router.get("/admin/list")
async def list_all_demos(
    status: Optional[str] = None,
    limit: int = 50,
    current_user: dict = Depends(get_current_user)
):
    """List all demo requests (superadmin only)"""
    
    if current_user.get("user_type") != "admin":
        raise HTTPException(status_code=403, detail="Access denied")
    
    query = {}
    if status:
        query["status"] = status
    
    demos = await db.demo_requests.find(
        query,
        {"_id": 0}
    ).sort("created_at", -1).limit(limit).to_list(limit)
    
    # Calculate remaining time for each
    now = datetime.now(timezone.utc)
    for demo in demos:
        expires_at = datetime.fromisoformat(demo["expires_at"].replace("Z", "+00:00"))
        remaining = (expires_at - now).total_seconds()
        demo["remaining_days"] = round(max(0, remaining / 86400), 1)
        demo["is_expired"] = remaining <= 0
    
    return {
        "demos": demos,
        "total": len(demos)
    }

@router.get("/admin/config")
async def get_demo_config(current_user: dict = Depends(get_current_user)):
    """Get demo configuration (superadmin only)"""
    
    if current_user.get("user_type") != "admin":
        raise HTTPException(status_code=403, detail="Access denied")
    
    config = await db.platform_config.find_one(
        {"config_type": "demo_config"},
        {"_id": 0}
    )
    
    if not config:
        config = {
            "config_type": "demo_config",
            "default_duration_days": 7,
            "max_students_demo": 50,
            "features_enabled": DEMO_FEATURES,
            "auto_approve": True,
            "max_extensions": 2,
            "extension_days": 7
        }
    
    return config

@router.put("/admin/config")
async def update_demo_config(
    config: DemoConfig,
    current_user: dict = Depends(get_current_user)
):
    """Update demo configuration (superadmin only)"""
    
    if current_user.get("user_type") != "admin":
        raise HTTPException(status_code=403, detail="Access denied")
    
    update_data = config.dict()
    update_data["config_type"] = "demo_config"
    update_data["updated_at"] = datetime.now(timezone.utc).isoformat()
    
    await db.platform_config.update_one(
        {"config_type": "demo_config"},
        {"$set": update_data},
        upsert=True
    )
    
    return {"message": "Configuración de demo actualizada"}

@router.post("/admin/convert/{demo_id}")
async def convert_demo_to_customer(
    demo_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Convert demo to paying customer (superadmin only)"""
    
    if current_user.get("user_type") != "admin":
        raise HTTPException(status_code=403, detail="Access denied")
    
    demo = await db.demo_requests.find_one({"demo_id": demo_id})
    
    if not demo:
        raise HTTPException(status_code=404, detail="Demo no encontrada")
    
    # Update demo status
    await db.demo_requests.update_one(
        {"demo_id": demo_id},
        {"$set": {
            "status": "converted",
            "converted_at": datetime.now(timezone.utc).isoformat(),
            "conversion_status": "customer"
        }}
    )
    
    # Update user to remove demo flag
    await db.users.update_one(
        {"demo_id": demo_id},
        {"$set": {
            "is_demo": False,
            "converted_at": datetime.now(timezone.utc).isoformat()
        },
        "$unset": {"demo_expires_at": ""}}
    )
    
    # Log conversion
    await db.conversion_funnel.insert_one({
        "demo_id": demo_id,
        "stage": "converted_to_customer",
        "contact_email": demo["contact_email"],
        "created_at": datetime.now(timezone.utc).isoformat()
    })
    
    return {
        "success": True,
        "message": "Demo convertida a cliente",
        "demo_id": demo_id,
        "institution_name": demo["institution_name"]
    }
