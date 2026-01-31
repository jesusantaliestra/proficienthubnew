"""Institution Sales Configuration Router

This module handles:
- Sales mode configuration (ProficientHub, External, Both)
- Whitelabel domain settings
- API key generation for external integrations
- Custom add-on services management
- Student access creation via API
"""

from fastapi import APIRouter, HTTPException, Depends, Header
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timezone
import os
import uuid
import secrets
import hashlib

router = APIRouter(prefix="/institution", tags=["Institution Sales"])

# Database
from motor.motor_asyncio import AsyncIOMotorClient
mongo_client = AsyncIOMotorClient(os.environ.get("MONGO_URL"))
db = mongo_client[os.environ.get("DB_NAME", "eduplat")]

# Auth dependency
from server import get_current_user


# =============================================
# Models
# =============================================

class SalesConfig(BaseModel):
    sales_mode: str = "external"  # proficient | external | both
    whitelabel_domain: Optional[str] = ""
    api_key: Optional[str] = ""
    webhook_url: Optional[str] = ""
    auto_create_access: bool = True
    send_welcome_email: bool = True


class CustomService(BaseModel):
    name: str
    description: str
    type: str = "addon"  # addon | service | material


class CreateAccessRequest(BaseModel):
    email: str
    name: str
    plan_id: str
    custom_addons: Optional[List[str]] = []
    send_welcome: bool = True


# Base plans (fixed by ProficientHub - not editable)
BASE_PLANS = [
    {
        "id": "STARTER",
        "name": "Plan Starter",
        "mock_exams": 3,
        "ai_tutor_minutes": 30,
        "speaking_sessions": 2,
        "validity_days": 30,
        "features_fixed": [
            "3 Mock Exams completos",
            "30 minutos de Tutor IA",
            "2 sesiones de Speaking",
            "Feedback detallado"
        ]
    },
    {
        "id": "STANDARD",
        "name": "Plan Standard",
        "mock_exams": 5,
        "ai_tutor_minutes": -1,
        "speaking_sessions": -1,
        "validity_days": 60,
        "features_fixed": [
            "5 Mock Exams completos",
            "Tutor IA ilimitado",
            "Speaking ilimitado",
            "Evaluación de Writing",
            "Analytics avanzados"
        ]
    },
    {
        "id": "PREMIUM",
        "name": "Plan Premium",
        "mock_exams": 10,
        "ai_tutor_minutes": -1,
        "speaking_sessions": -1,
        "validity_days": 90,
        "features_fixed": [
            "10 Mock Exams completos",
            "Tutor IA ilimitado",
            "Speaking ilimitado",
            "Evaluación de Writing con IA",
            "Plan de estudio personalizado",
            "Soporte prioritario"
        ]
    }
]


# =============================================
# Sales Configuration Endpoints
# =============================================

@router.get("/sales-config")
async def get_sales_config(current_user: dict = Depends(get_current_user)):
    """Get institution's sales configuration"""
    
    if current_user.get("user_type") not in ["institution", "admin"]:
        raise HTTPException(status_code=403, detail="Institution access required")
    
    institution_id = current_user.get("institution_id") or current_user.get("id")
    
    config = await db.institution_sales_config.find_one(
        {"institution_id": institution_id},
        {"_id": 0}
    )
    
    if not config:
        return SalesConfig().dict()
    
    return config


@router.put("/sales-config")
async def update_sales_config(
    config: SalesConfig,
    current_user: dict = Depends(get_current_user)
):
    """Update institution's sales configuration"""
    
    if current_user.get("user_type") not in ["institution", "admin"]:
        raise HTTPException(status_code=403, detail="Institution access required")
    
    institution_id = current_user.get("institution_id") or current_user.get("id")
    
    # Don't overwrite API key if not provided
    existing = await db.institution_sales_config.find_one(
        {"institution_id": institution_id}
    )
    
    update_data = {
        **config.dict(),
        "institution_id": institution_id,
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    
    if existing and not config.api_key:
        update_data["api_key"] = existing.get("api_key", "")
    
    await db.institution_sales_config.update_one(
        {"institution_id": institution_id},
        {"$set": update_data},
        upsert=True
    )
    
    return {"message": "Configuration updated", "config": update_data}


@router.post("/generate-api-key")
async def generate_api_key(current_user: dict = Depends(get_current_user)):
    """Generate a new API key for external integrations"""
    
    if current_user.get("user_type") not in ["institution", "admin"]:
        raise HTTPException(status_code=403, detail="Institution access required")
    
    institution_id = current_user.get("institution_id") or current_user.get("id")
    
    # Generate secure API key
    raw_key = secrets.token_urlsafe(32)
    api_key = f"ph_{raw_key}"
    
    # Store hashed version for verification
    hashed_key = hashlib.sha256(api_key.encode()).hexdigest()
    
    await db.institution_sales_config.update_one(
        {"institution_id": institution_id},
        {
            "$set": {
                "api_key": api_key,
                "api_key_hash": hashed_key,
                "api_key_created_at": datetime.now(timezone.utc).isoformat()
            }
        },
        upsert=True
    )
    
    # Also store in api_keys collection for lookup
    await db.api_keys.update_one(
        {"institution_id": institution_id},
        {
            "$set": {
                "institution_id": institution_id,
                "key_hash": hashed_key,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "active": True
            }
        },
        upsert=True
    )
    
    return {"api_key": api_key, "message": "API key generated successfully"}


# =============================================
# Base Plans (Read-only)
# =============================================

@router.get("/base-plans")
async def get_base_plans():
    """Get base plans (fixed by ProficientHub)"""
    return {"plans": BASE_PLANS}


# =============================================
# Custom Services/Add-ons
# =============================================

@router.get("/custom-plans")
async def get_custom_plans(current_user: dict = Depends(get_current_user)):
    """Get institution's custom services/add-ons"""
    
    if current_user.get("user_type") not in ["institution", "admin"]:
        raise HTTPException(status_code=403, detail="Institution access required")
    
    institution_id = current_user.get("institution_id") or current_user.get("id")
    
    plans = await db.institution_custom_services.find(
        {"institution_id": institution_id},
        {"_id": 0}
    ).to_list(100)
    
    return {"plans": plans}


@router.post("/custom-plans")
async def create_custom_plan(
    service: CustomService,
    current_user: dict = Depends(get_current_user)
):
    """Create a custom service/add-on"""
    
    if current_user.get("user_type") not in ["institution", "admin"]:
        raise HTTPException(status_code=403, detail="Institution access required")
    
    institution_id = current_user.get("institution_id") or current_user.get("id")
    
    new_service = {
        "id": str(uuid.uuid4()),
        "institution_id": institution_id,
        **service.dict(),
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.institution_custom_services.insert_one(new_service)
    
    return {"message": "Service created", "service": new_service}


@router.delete("/custom-plans/{plan_id}")
async def delete_custom_plan(
    plan_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete a custom service/add-on"""
    
    if current_user.get("user_type") not in ["institution", "admin"]:
        raise HTTPException(status_code=403, detail="Institution access required")
    
    institution_id = current_user.get("institution_id") or current_user.get("id")
    
    result = await db.institution_custom_services.delete_one(
        {"id": plan_id, "institution_id": institution_id}
    )
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Service not found")
    
    return {"message": "Service deleted"}


# =============================================
# External API Integration
# =============================================

async def verify_api_key(authorization: str = Header(None)):
    """Verify API key from external request"""
    
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header")
    
    api_key = authorization.replace("Bearer ", "")
    key_hash = hashlib.sha256(api_key.encode()).hexdigest()
    
    key_record = await db.api_keys.find_one({"key_hash": key_hash, "active": True})
    
    if not key_record:
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    return key_record


@router.post("/api/v1/access/create")
async def create_student_access_via_api(
    request: CreateAccessRequest,
    key_record: dict = Depends(verify_api_key)
):
    """
    External API endpoint for creating student access.
    Called by institution's own website after a sale.
    """
    
    institution_id = key_record["institution_id"]
    
    # Validate plan
    valid_plans = [p["id"] for p in BASE_PLANS]
    if request.plan_id not in valid_plans:
        raise HTTPException(status_code=400, detail=f"Invalid plan_id. Must be one of: {valid_plans}")
    
    plan = next(p for p in BASE_PLANS if p["id"] == request.plan_id)
    
    # Check if user exists
    existing_user = await db.users.find_one({"email": request.email.lower()})
    
    if existing_user:
        user_id = existing_user["id"]
    else:
        # Create new user
        user_id = str(uuid.uuid4())
        temp_password = secrets.token_urlsafe(12)
        
        new_user = {
            "id": user_id,
            "email": request.email.lower(),
            "name": request.name,
            "password": hashlib.sha256(temp_password.encode()).hexdigest(),
            "user_type": "student",
            "institution_id": institution_id,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "created_via": "external_api"
        }
        
        await db.users.insert_one(new_user)
    
    # Create access record
    access_id = str(uuid.uuid4())
    from datetime import timedelta
    
    access_record = {
        "id": access_id,
        "user_id": user_id,
        "institution_id": institution_id,
        "plan_id": request.plan_id,
        "plan_name": plan["name"],
        "mock_exams_total": plan["mock_exams"],
        "mock_exams_remaining": plan["mock_exams"],
        "ai_tutor_minutes": plan["ai_tutor_minutes"],
        "speaking_sessions": plan["speaking_sessions"],
        "custom_addons": request.custom_addons,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "expires_at": (datetime.now(timezone.utc) + timedelta(days=plan["validity_days"])).isoformat(),
        "status": "active"
    }
    
    await db.student_access.insert_one(access_record)
    
    # TODO: Send welcome email if request.send_welcome
    
    return {
        "success": True,
        "user_id": user_id,
        "access_id": access_id,
        "plan": plan["name"],
        "expires_at": access_record["expires_at"],
        "login_url": f"https://app.proficienthub.com/login?email={request.email}"
    }


@router.get("/api/v1/students/{email}/status")
async def get_student_status_via_api(
    email: str,
    key_record: dict = Depends(verify_api_key)
):
    """
    External API endpoint for checking student status.
    """
    
    institution_id = key_record["institution_id"]
    
    user = await db.users.find_one(
        {"email": email.lower(), "institution_id": institution_id},
        {"_id": 0, "password": 0}
    )
    
    if not user:
        raise HTTPException(status_code=404, detail="Student not found")
    
    # Get access records
    access = await db.student_access.find(
        {"user_id": user["id"], "status": "active"},
        {"_id": 0}
    ).to_list(10)
    
    # Get progress
    exams_completed = await db.exam_results.count_documents(
        {"user_id": user["id"]}
    )
    
    return {
        "email": email,
        "name": user.get("name"),
        "active_access": access,
        "exams_completed": exams_completed,
        "last_activity": user.get("last_login")
    }


# =============================================
# Webhook Configuration
# =============================================

@router.post("/test-webhook")
async def test_webhook(current_user: dict = Depends(get_current_user)):
    """Send a test webhook to verify configuration"""
    
    if current_user.get("user_type") not in ["institution", "admin"]:
        raise HTTPException(status_code=403, detail="Institution access required")
    
    institution_id = current_user.get("institution_id") or current_user.get("id")
    
    config = await db.institution_sales_config.find_one(
        {"institution_id": institution_id}
    )
    
    if not config or not config.get("webhook_url"):
        raise HTTPException(status_code=400, detail="No webhook URL configured")
    
    import httpx
    
    test_payload = {
        "event": "test",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "message": "This is a test webhook from ProficientHub"
    }
    
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.post(
                config["webhook_url"],
                json=test_payload,
                headers={"Content-Type": "application/json"}
            )
            
            return {
                "success": response.status_code < 400,
                "status_code": response.status_code,
                "message": "Webhook test sent"
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
