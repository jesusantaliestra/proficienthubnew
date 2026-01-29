"""
Public API v1 - Institutions Endpoints
Full CRUD operations for institutions via API
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
import uuid

import sys
sys.path.append('/app/backend')
from database import db
from .auth_middleware import require_read, require_write, require_admin

router = APIRouter(prefix="/institutions", tags=["Institutions API"])

# Models
class InstitutionBase(BaseModel):
    name: str
    contact_email: EmailStr
    contact_name: Optional[str] = None
    phone: Optional[str] = None
    country: Optional[str] = None
    timezone: Optional[str] = "UTC"
    metadata: Optional[Dict[str, Any]] = None

class InstitutionCreate(InstitutionBase):
    plan: str = "starter"  # starter, growth, scale, enterprise

class InstitutionUpdate(BaseModel):
    name: Optional[str] = None
    contact_email: Optional[EmailStr] = None
    contact_name: Optional[str] = None
    phone: Optional[str] = None
    country: Optional[str] = None
    timezone: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None

class InstitutionResponse(BaseModel):
    id: str
    name: str
    contact_email: str
    contact_name: Optional[str]
    phone: Optional[str]
    country: Optional[str]
    timezone: str
    plan: str
    is_active: bool
    student_count: int
    created_at: str
    updated_at: Optional[str]
    metadata: Optional[Dict[str, Any]]

class PaginatedResponse(BaseModel):
    data: List[InstitutionResponse]
    total: int
    page: int
    per_page: int
    total_pages: int

# Endpoints
@router.get("", response_model=PaginatedResponse)
async def list_institutions(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    country: Optional[str] = None,
    plan: Optional[str] = None,
    is_active: Optional[bool] = None,
    search: Optional[str] = None,
    api_auth: dict = Depends(require_read)
):
    """
    List all institutions with pagination and filtering.
    
    - **page**: Page number (default: 1)
    - **per_page**: Items per page (default: 20, max: 100)
    - **country**: Filter by country code
    - **plan**: Filter by plan type
    - **is_active**: Filter by active status
    - **search**: Search by name or email
    """
    query = {"user_type": "institution"}
    
    # Apply filters
    if country:
        query["country"] = country
    if plan:
        query["plan"] = plan
    if is_active is not None:
        query["is_active"] = is_active
    if search:
        query["$or"] = [
            {"name": {"$regex": search, "$options": "i"}},
            {"institution_name": {"$regex": search, "$options": "i"}},
            {"email": {"$regex": search, "$options": "i"}}
        ]
    
    # Count total
    total = await db.users.count_documents(query)
    total_pages = (total + per_page - 1) // per_page
    
    # Fetch page
    skip = (page - 1) * per_page
    institutions = await db.users.find(
        query,
        {"_id": 0, "password_hash": 0}
    ).skip(skip).limit(per_page).to_list(per_page)
    
    # Enrich with student counts
    result = []
    for inst in institutions:
        student_count = await db.users.count_documents({
            "institution_id": inst["id"],
            "user_type": "student"
        })
        
        result.append(InstitutionResponse(
            id=inst["id"],
            name=inst.get("institution_name", inst.get("name", "")),
            contact_email=inst["email"],
            contact_name=inst.get("name"),
            phone=inst.get("phone"),
            country=inst.get("country"),
            timezone=inst.get("timezone", "UTC"),
            plan=inst.get("plan", "starter"),
            is_active=inst.get("is_active", True),
            student_count=student_count,
            created_at=inst.get("created_at", ""),
            updated_at=inst.get("updated_at"),
            metadata=inst.get("metadata")
        ))
    
    return PaginatedResponse(
        data=result,
        total=total,
        page=page,
        per_page=per_page,
        total_pages=total_pages
    )

@router.get("/{institution_id}", response_model=InstitutionResponse)
async def get_institution(
    institution_id: str,
    api_auth: dict = Depends(require_read)
):
    """Get a single institution by ID"""
    institution = await db.users.find_one(
        {"id": institution_id, "user_type": "institution"},
        {"_id": 0, "password_hash": 0}
    )
    
    if not institution:
        raise HTTPException(status_code=404, detail="Institution not found")
    
    student_count = await db.users.count_documents({
        "institution_id": institution_id,
        "user_type": "student"
    })
    
    return InstitutionResponse(
        id=institution["id"],
        name=institution.get("institution_name", institution.get("name", "")),
        contact_email=institution["email"],
        contact_name=institution.get("name"),
        phone=institution.get("phone"),
        country=institution.get("country"),
        timezone=institution.get("timezone", "UTC"),
        plan=institution.get("plan", "starter"),
        is_active=institution.get("is_active", True),
        student_count=student_count,
        created_at=institution.get("created_at", ""),
        updated_at=institution.get("updated_at"),
        metadata=institution.get("metadata")
    )

@router.patch("/{institution_id}", response_model=InstitutionResponse)
async def update_institution(
    institution_id: str,
    update_data: InstitutionUpdate,
    api_auth: dict = Depends(require_write)
):
    """Update an institution's details"""
    # Build update dict
    update_dict = {k: v for k, v in update_data.dict().items() if v is not None}
    
    if not update_dict:
        raise HTTPException(status_code=400, detail="No fields to update")
    
    update_dict["updated_at"] = datetime.now(timezone.utc).isoformat()
    
    # Map fields
    if "name" in update_dict:
        update_dict["institution_name"] = update_dict.pop("name")
    if "contact_email" in update_dict:
        update_dict["email"] = update_dict.pop("contact_email")
    
    result = await db.users.update_one(
        {"id": institution_id, "user_type": "institution"},
        {"$set": update_dict}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Institution not found")
    
    return await get_institution(institution_id, api_auth)

@router.get("/{institution_id}/stats")
async def get_institution_stats(
    institution_id: str,
    api_auth: dict = Depends(require_read)
):
    """Get detailed statistics for an institution"""
    # Verify institution exists
    institution = await db.users.find_one(
        {"id": institution_id, "user_type": "institution"},
        {"_id": 0, "id": 1}
    )
    
    if not institution:
        raise HTTPException(status_code=404, detail="Institution not found")
    
    # Student stats
    student_count = await db.users.count_documents({
        "institution_id": institution_id,
        "user_type": "student"
    })
    
    active_students = await db.users.count_documents({
        "institution_id": institution_id,
        "user_type": "student",
        "is_active": True
    })
    
    # Exam stats
    exam_pipeline = [
        {"$match": {"institution_id": institution_id}},
        {"$group": {
            "_id": "$exam_type",
            "count": {"$sum": 1},
            "avg_score": {"$avg": "$score"}
        }}
    ]
    exam_stats = await db.exam_attempts.aggregate(exam_pipeline).to_list(20)
    
    total_exams = sum(e["count"] for e in exam_stats)
    avg_score = sum(e["avg_score"] * e["count"] for e in exam_stats) / max(total_exams, 1)
    
    # AI usage
    ai_usage = await db.ai_agent_history.count_documents({
        "institution_id": institution_id
    })
    
    # Credits
    credits = await db.ai_credits.find_one(
        {"user_id": institution_id},
        {"_id": 0}
    )
    
    return {
        "institution_id": institution_id,
        "students": {
            "total": student_count,
            "active": active_students,
            "inactive": student_count - active_students
        },
        "exams": {
            "total_attempts": total_exams,
            "average_score": round(avg_score, 2),
            "by_type": {e["_id"]: {"count": e["count"], "avg_score": round(e["avg_score"], 2)} for e in exam_stats}
        },
        "ai_usage": {
            "total_interactions": ai_usage,
            "credits_total": credits.get("total_credits", 0) if credits else 0,
            "credits_used": credits.get("used_credits", 0) if credits else 0,
            "credits_remaining": (credits.get("total_credits", 0) - credits.get("used_credits", 0)) if credits else 0
        }
    }
