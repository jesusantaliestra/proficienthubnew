"""Institution Custom Exam Packs Router

This module handles:
- Full custom exam pack creation by institutions
- Pack includes: mocks, AI tutor, exam type, custom services
- Institution sets final price
- Student purchases and access management
"""

from fastapi import APIRouter, HTTPException, Depends, Header
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timezone
import os
import uuid
import secrets
import hashlib

router = APIRouter(prefix="/institution-packs", tags=["Institution Custom Packs"])

# Database
from motor.motor_asyncio import AsyncIOMotorClient
mongo_client = AsyncIOMotorClient(os.environ.get("MONGO_URL"))
db = mongo_client[os.environ.get("DB_NAME", "eduplat")]

# Auth dependency
from server import get_current_user


# =============================================
# Models
# =============================================

class CustomServiceItem(BaseModel):
    """Custom service added by institution"""
    name: str
    description: Optional[str] = ""
    type: str = "service"  # service | material | class | other


class CustomExamPack(BaseModel):
    """Full custom exam pack created by institution"""
    name: str
    description: Optional[str] = ""
    exam_type: str  # OET, IELTS, TOEFL, PTE, CAMBRIDGE, etc.
    profession: Optional[str] = None  # For OET: nursing, medicine, etc.
    
    # Core features (institution decides)
    num_mocks: int = 0
    include_ai_tutor: bool = False
    ai_tutor_minutes: int = 0  # -1 = unlimited
    include_speaking: bool = False
    speaking_sessions: int = 0  # -1 = unlimited
    include_writing_evaluation: bool = False
    writing_evaluations: int = 0  # -1 = unlimited
    
    # Validity
    validity_days: int = 30
    
    # Custom services added by institution
    custom_services: List[CustomServiceItem] = []
    
    # Pricing (institution sets this)
    price: float
    currency: str = "EUR"
    
    # Display settings
    is_popular: bool = False
    badge_text: Optional[str] = None  # "Más Popular", "Mejor Valor", etc.
    sort_order: int = 0


class PackPurchaseRequest(BaseModel):
    """Request to purchase a pack"""
    pack_id: str
    student_email: str
    student_name: str
    payment_reference: Optional[str] = None  # External payment reference


# Supported exam types
EXAM_TYPES = [
    {"id": "OET", "name": "OET - Occupational English Test", "has_professions": True},
    {"id": "IELTS_ACADEMIC", "name": "IELTS Academic", "has_professions": False},
    {"id": "IELTS_GENERAL", "name": "IELTS General Training", "has_professions": False},
    {"id": "TOEFL", "name": "TOEFL iBT", "has_professions": False},
    {"id": "PTE", "name": "PTE Academic", "has_professions": False},
    {"id": "CAMBRIDGE_FCE", "name": "Cambridge B2 First (FCE)", "has_professions": False},
    {"id": "CAMBRIDGE_CAE", "name": "Cambridge C1 Advanced (CAE)", "has_professions": False},
    {"id": "CAMBRIDGE_CPE", "name": "Cambridge C2 Proficiency (CPE)", "has_professions": False},
    {"id": "CELPIP", "name": "CELPIP", "has_professions": False},
    {"id": "TOEIC", "name": "TOEIC", "has_professions": False},
]

# OET Professions
OET_PROFESSIONS = [
    {"id": "nursing", "name": "Enfermería", "name_en": "Nursing"},
    {"id": "medicine", "name": "Medicina", "name_en": "Medicine"},
    {"id": "dentistry", "name": "Odontología", "name_en": "Dentistry"},
    {"id": "pharmacy", "name": "Farmacia", "name_en": "Pharmacy"},
    {"id": "physiotherapy", "name": "Fisioterapia", "name_en": "Physiotherapy"},
    {"id": "radiography", "name": "Radiografía", "name_en": "Radiography"},
    {"id": "optometry", "name": "Optometría", "name_en": "Optometry"},
    {"id": "dietetics", "name": "Dietética", "name_en": "Dietetics"},
    {"id": "occupational_therapy", "name": "Terapia Ocupacional", "name_en": "Occupational Therapy"},
    {"id": "speech_pathology", "name": "Logopedia", "name_en": "Speech Pathology"},
    {"id": "veterinary_science", "name": "Veterinaria", "name_en": "Veterinary Science"},
    {"id": "podiatry", "name": "Podología", "name_en": "Podiatry"},
]


# =============================================
# Reference Data Endpoints
# =============================================

@router.get("/exam-types")
async def get_exam_types():
    """Get list of supported exam types"""
    return {"exam_types": EXAM_TYPES}


@router.get("/oet-professions")
async def get_oet_professions():
    """Get list of OET professions"""
    return {"professions": OET_PROFESSIONS}


# =============================================
# Pack Management Endpoints
# =============================================

@router.get("/packs")
async def get_institution_packs(current_user: dict = Depends(get_current_user)):
    """Get all custom packs created by institution"""
    
    if current_user.get("user_type") not in ["institution", "admin"]:
        raise HTTPException(status_code=403, detail="Institution access required")
    
    institution_id = current_user.get("institution_id") or current_user.get("id")
    
    packs = await db.institution_custom_packs.find(
        {"institution_id": institution_id, "deleted": {"$ne": True}},
        {"_id": 0}
    ).sort("sort_order", 1).to_list(100)
    
    return {"packs": packs, "count": len(packs)}


@router.post("/packs")
async def create_pack(
    pack: CustomExamPack,
    current_user: dict = Depends(get_current_user)
):
    """Create a new custom exam pack"""
    
    if current_user.get("user_type") not in ["institution", "admin"]:
        raise HTTPException(status_code=403, detail="Institution access required")
    
    institution_id = current_user.get("institution_id") or current_user.get("id")
    
    # Validate exam type
    valid_types = [e["id"] for e in EXAM_TYPES]
    if pack.exam_type not in valid_types:
        raise HTTPException(status_code=400, detail=f"Invalid exam_type. Must be one of: {valid_types}")
    
    # For OET, validate profession
    if pack.exam_type == "OET" and pack.profession:
        valid_professions = [p["id"] for p in OET_PROFESSIONS]
        if pack.profession not in valid_professions:
            raise HTTPException(status_code=400, detail=f"Invalid profession. Must be one of: {valid_professions}")
    
    new_pack = {
        "id": str(uuid.uuid4()),
        "institution_id": institution_id,
        **pack.dict(),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "deleted": False,
        "total_sold": 0
    }
    
    await db.institution_custom_packs.insert_one(new_pack)
    
    # Remove _id before returning
    new_pack.pop("_id", None)
    
    return {"message": "Pack created successfully", "pack": new_pack}


@router.get("/packs/{pack_id}")
async def get_pack(
    pack_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get a specific pack"""
    
    if current_user.get("user_type") not in ["institution", "admin"]:
        raise HTTPException(status_code=403, detail="Institution access required")
    
    institution_id = current_user.get("institution_id") or current_user.get("id")
    
    pack = await db.institution_custom_packs.find_one(
        {"id": pack_id, "institution_id": institution_id, "deleted": {"$ne": True}},
        {"_id": 0}
    )
    
    if not pack:
        raise HTTPException(status_code=404, detail="Pack not found")
    
    return {"pack": pack}


@router.put("/packs/{pack_id}")
async def update_pack(
    pack_id: str,
    pack: CustomExamPack,
    current_user: dict = Depends(get_current_user)
):
    """Update an existing pack"""
    
    if current_user.get("user_type") not in ["institution", "admin"]:
        raise HTTPException(status_code=403, detail="Institution access required")
    
    institution_id = current_user.get("institution_id") or current_user.get("id")
    
    # Check pack exists
    existing = await db.institution_custom_packs.find_one(
        {"id": pack_id, "institution_id": institution_id, "deleted": {"$ne": True}}
    )
    
    if not existing:
        raise HTTPException(status_code=404, detail="Pack not found")
    
    # Update
    update_data = {
        **pack.dict(),
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.institution_custom_packs.update_one(
        {"id": pack_id},
        {"$set": update_data}
    )
    
    return {"message": "Pack updated successfully"}


@router.delete("/packs/{pack_id}")
async def delete_pack(
    pack_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete a pack (soft delete)"""
    
    if current_user.get("user_type") not in ["institution", "admin"]:
        raise HTTPException(status_code=403, detail="Institution access required")
    
    institution_id = current_user.get("institution_id") or current_user.get("id")
    
    result = await db.institution_custom_packs.update_one(
        {"id": pack_id, "institution_id": institution_id},
        {"$set": {"deleted": True, "deleted_at": datetime.now(timezone.utc).isoformat()}}
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Pack not found")
    
    return {"message": "Pack deleted successfully"}


@router.post("/packs/reorder")
async def reorder_packs(
    pack_orders: List[dict],  # [{"pack_id": "...", "sort_order": 0}, ...]
    current_user: dict = Depends(get_current_user)
):
    """Reorder packs for display"""
    
    if current_user.get("user_type") not in ["institution", "admin"]:
        raise HTTPException(status_code=403, detail="Institution access required")
    
    institution_id = current_user.get("institution_id") or current_user.get("id")
    
    for item in pack_orders:
        await db.institution_custom_packs.update_one(
            {"id": item["pack_id"], "institution_id": institution_id},
            {"$set": {"sort_order": item["sort_order"]}}
        )
    
    return {"message": "Packs reordered successfully"}


# =============================================
# Public Pack Endpoints (for students)
# =============================================

@router.get("/public/{institution_id}")
async def get_public_packs(institution_id: str):
    """Get public packs for an institution (for students to view)"""
    
    packs = await db.institution_custom_packs.find(
        {"institution_id": institution_id, "deleted": {"$ne": True}},
        {"_id": 0, "institution_id": 0}
    ).sort("sort_order", 1).to_list(100)
    
    # Get institution info
    institution = await db.users.find_one(
        {"id": institution_id},
        {"_id": 0, "name": 1, "institution_name": 1}
    )
    
    return {
        "institution_name": institution.get("institution_name") or institution.get("name") if institution else "Unknown",
        "packs": packs,
        "count": len(packs)
    }


@router.get("/public/{institution_id}/by-exam/{exam_type}")
async def get_public_packs_by_exam(institution_id: str, exam_type: str):
    """Get public packs for an institution filtered by exam type"""
    
    packs = await db.institution_custom_packs.find(
        {
            "institution_id": institution_id,
            "exam_type": exam_type,
            "deleted": {"$ne": True}
        },
        {"_id": 0, "institution_id": 0}
    ).sort("sort_order", 1).to_list(100)
    
    return {"exam_type": exam_type, "packs": packs, "count": len(packs)}


# =============================================
# Purchase & Access Management
# =============================================

@router.post("/purchase")
async def purchase_pack(
    request: PackPurchaseRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Purchase a pack for a student.
    Called by institution after receiving payment through their channels.
    """
    
    if current_user.get("user_type") not in ["institution", "admin"]:
        raise HTTPException(status_code=403, detail="Institution access required")
    
    institution_id = current_user.get("institution_id") or current_user.get("id")
    
    # Get pack
    pack = await db.institution_custom_packs.find_one(
        {"id": request.pack_id, "institution_id": institution_id, "deleted": {"$ne": True}},
        {"_id": 0}
    )
    
    if not pack:
        raise HTTPException(status_code=404, detail="Pack not found")
    
    # Find or create student
    student = await db.users.find_one({"email": request.student_email.lower()})
    
    if not student:
        # Create new student account
        temp_password = secrets.token_urlsafe(12)
        student_id = str(uuid.uuid4())
        
        new_student = {
            "id": student_id,
            "email": request.student_email.lower(),
            "name": request.student_name,
            "password": hashlib.sha256(temp_password.encode()).hexdigest(),
            "user_type": "student",
            "institution_id": institution_id,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "created_via": "pack_purchase",
            "requires_password_change": True
        }
        
        await db.users.insert_one(new_student)
        student_id = student_id
        is_new_student = True
        temp_password_to_send = temp_password
    else:
        student_id = student["id"]
        is_new_student = False
        temp_password_to_send = None
    
    # Create access record
    from datetime import timedelta
    
    access_id = str(uuid.uuid4())
    expires_at = datetime.now(timezone.utc) + timedelta(days=pack["validity_days"])
    
    access_record = {
        "id": access_id,
        "pack_id": pack["id"],
        "pack_name": pack["name"],
        "student_id": student_id,
        "institution_id": institution_id,
        "exam_type": pack["exam_type"],
        "profession": pack.get("profession"),
        
        # Allocated credits
        "mocks_total": pack["num_mocks"],
        "mocks_remaining": pack["num_mocks"],
        "ai_tutor_minutes_total": pack["ai_tutor_minutes"],
        "ai_tutor_minutes_remaining": pack["ai_tutor_minutes"],
        "speaking_sessions_total": pack["speaking_sessions"],
        "speaking_sessions_remaining": pack["speaking_sessions"],
        "writing_evaluations_total": pack["writing_evaluations"],
        "writing_evaluations_remaining": pack["writing_evaluations"],
        
        # Features
        "include_ai_tutor": pack["include_ai_tutor"],
        "include_speaking": pack["include_speaking"],
        "include_writing_evaluation": pack["include_writing_evaluation"],
        "custom_services": pack.get("custom_services", []),
        
        # Dates
        "purchased_at": datetime.now(timezone.utc).isoformat(),
        "expires_at": expires_at.isoformat(),
        "status": "active",
        
        # Payment reference
        "payment_reference": request.payment_reference,
        "price_paid": pack["price"],
        "currency": pack["currency"]
    }
    
    await db.student_pack_access.insert_one(access_record)
    
    # Update pack sold count
    await db.institution_custom_packs.update_one(
        {"id": pack["id"]},
        {"$inc": {"total_sold": 1}}
    )
    
    return {
        "success": True,
        "access_id": access_id,
        "student_id": student_id,
        "is_new_student": is_new_student,
        "temp_password": temp_password_to_send,
        "expires_at": access_record["expires_at"],
        "message": f"Access granted to {pack['name']}"
    }


@router.get("/student-access")
async def get_student_access(current_user: dict = Depends(get_current_user)):
    """Get current user's pack access"""
    
    user_id = current_user["id"]
    
    access_list = await db.student_pack_access.find(
        {"student_id": user_id, "status": "active"},
        {"_id": 0}
    ).to_list(50)
    
    # Filter expired
    now = datetime.now(timezone.utc).isoformat()
    active_access = [a for a in access_list if a.get("expires_at", "") > now]
    
    return {"access": active_access, "count": len(active_access)}


@router.get("/institution-sales")
async def get_institution_sales(
    current_user: dict = Depends(get_current_user),
    days: int = 30
):
    """Get sales analytics for institution"""
    
    if current_user.get("user_type") not in ["institution", "admin"]:
        raise HTTPException(status_code=403, detail="Institution access required")
    
    institution_id = current_user.get("institution_id") or current_user.get("id")
    
    from datetime import timedelta
    start_date = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
    
    # Get sales
    sales = await db.student_pack_access.find(
        {"institution_id": institution_id, "purchased_at": {"$gte": start_date}},
        {"_id": 0}
    ).to_list(1000)
    
    # Calculate totals
    total_revenue = sum(s.get("price_paid", 0) for s in sales)
    total_sales = len(sales)
    
    # Group by pack
    by_pack = {}
    for sale in sales:
        pack_name = sale.get("pack_name", "Unknown")
        if pack_name not in by_pack:
            by_pack[pack_name] = {"count": 0, "revenue": 0}
        by_pack[pack_name]["count"] += 1
        by_pack[pack_name]["revenue"] += sale.get("price_paid", 0)
    
    return {
        "period_days": days,
        "total_sales": total_sales,
        "total_revenue": total_revenue,
        "by_pack": by_pack,
        "recent_sales": sales[:20]
    }


# =============================================
# Duplicate Pack
# =============================================

@router.post("/packs/{pack_id}/duplicate")
async def duplicate_pack(
    pack_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Duplicate an existing pack"""
    
    if current_user.get("user_type") not in ["institution", "admin"]:
        raise HTTPException(status_code=403, detail="Institution access required")
    
    institution_id = current_user.get("institution_id") or current_user.get("id")
    
    # Get original pack
    original = await db.institution_custom_packs.find_one(
        {"id": pack_id, "institution_id": institution_id, "deleted": {"$ne": True}},
        {"_id": 0}
    )
    
    if not original:
        raise HTTPException(status_code=404, detail="Pack not found")
    
    # Create copy
    new_pack = {
        **original,
        "id": str(uuid.uuid4()),
        "name": f"{original['name']} (Copia)",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "total_sold": 0,
        "is_popular": False
    }
    
    await db.institution_custom_packs.insert_one(new_pack)
    new_pack.pop("_id", None)
    
    return {"message": "Pack duplicated successfully", "pack": new_pack}
