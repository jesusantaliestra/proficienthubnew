"""
Public API v1 - Students Endpoints
Full CRUD operations for students via API
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
import uuid
import secrets
import string
import bcrypt

import sys
sys.path.append('/app/backend')
from database import db
from .auth_middleware import require_read, require_write, require_admin

router = APIRouter(prefix="/students", tags=["Students API"])

# Models
class StudentCreate(BaseModel):
    email: EmailStr
    name: str
    institution_id: str
    exam_type: str
    credits: int = 100
    metadata: Optional[Dict[str, Any]] = None

class StudentBulkCreate(BaseModel):
    students: List[StudentCreate]

class StudentUpdate(BaseModel):
    name: Optional[str] = None
    exam_type: Optional[str] = None
    credits: Optional[int] = None
    is_active: Optional[bool] = None
    metadata: Optional[Dict[str, Any]] = None

class StudentResponse(BaseModel):
    id: str
    email: str
    name: str
    institution_id: str
    exam_type: str
    credits: int
    credits_used: int
    is_active: bool
    created_at: str
    last_activity: Optional[str]
    exam_attempts: int
    average_score: Optional[float]
    metadata: Optional[Dict[str, Any]]

class StudentCreatedResponse(StudentResponse):
    provisional_password: str  # Only returned on creation

class PaginatedStudentsResponse(BaseModel):
    data: List[StudentResponse]
    total: int
    page: int
    per_page: int
    total_pages: int

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def generate_password() -> str:
    return ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(12))

# Endpoints
@router.get("", response_model=PaginatedStudentsResponse)
async def list_students(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    institution_id: Optional[str] = None,
    exam_type: Optional[str] = None,
    is_active: Optional[bool] = None,
    search: Optional[str] = None,
    api_auth: dict = Depends(require_read)
):
    """
    List all students with pagination and filtering.
    
    - **institution_id**: Filter by institution
    - **exam_type**: Filter by exam type (ielts, toefl, etc.)
    - **is_active**: Filter by active status
    - **search**: Search by name or email
    """
    query = {"user_type": "student"}
    
    if institution_id:
        query["institution_id"] = institution_id
    if exam_type:
        query["current_exam"] = exam_type
    if is_active is not None:
        query["is_active"] = is_active
    if search:
        query["$or"] = [
            {"name": {"$regex": search, "$options": "i"}},
            {"email": {"$regex": search, "$options": "i"}}
        ]
    
    total = await db.users.count_documents(query)
    total_pages = (total + per_page - 1) // per_page
    
    skip = (page - 1) * per_page
    students = await db.users.find(
        query,
        {"_id": 0, "password_hash": 0, "provisional_password": 0}
    ).skip(skip).limit(per_page).to_list(per_page)
    
    result = []
    for student in students:
        # Get exam stats
        exam_count = await db.exam_attempts.count_documents({"user_id": student["id"]})
        avg_score_result = await db.exam_attempts.aggregate([
            {"$match": {"user_id": student["id"]}},
            {"$group": {"_id": None, "avg": {"$avg": "$score"}}}
        ]).to_list(1)
        avg_score = avg_score_result[0]["avg"] if avg_score_result else None
        
        result.append(StudentResponse(
            id=student["id"],
            email=student["email"],
            name=student["name"],
            institution_id=student.get("institution_id", ""),
            exam_type=student.get("current_exam", ""),
            credits=student.get("credits", 0),
            credits_used=student.get("credits_used", 0),
            is_active=student.get("is_active", True),
            created_at=student.get("created_at", ""),
            last_activity=student.get("last_activity"),
            exam_attempts=exam_count,
            average_score=round(avg_score, 2) if avg_score else None,
            metadata=student.get("metadata")
        ))
    
    return PaginatedStudentsResponse(
        data=result,
        total=total,
        page=page,
        per_page=per_page,
        total_pages=total_pages
    )

@router.post("", response_model=StudentCreatedResponse)
async def create_student(
    student_data: StudentCreate,
    api_auth: dict = Depends(require_write)
):
    """
    Create a new student with provisional credentials.
    Returns the provisional password - store it securely!
    """
    # Check if email exists
    existing = await db.users.find_one({"email": student_data.email})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Verify institution exists
    institution = await db.users.find_one({
        "id": student_data.institution_id,
        "user_type": "institution"
    })
    if not institution:
        raise HTTPException(status_code=400, detail="Institution not found")
    
    # Generate credentials
    student_id = str(uuid.uuid4())
    provisional_password = generate_password()
    
    student_doc = {
        "id": student_id,
        "email": student_data.email,
        "name": student_data.name,
        "password_hash": hash_password(provisional_password),
        "user_type": "student",
        "institution_id": student_data.institution_id,
        "institution_name": institution.get("institution_name"),
        "current_exam": student_data.exam_type,
        "exam_access": [student_data.exam_type],
        "credits": student_data.credits,
        "credits_used": 0,
        "is_active": True,
        "requires_password_change": True,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "metadata": student_data.metadata
    }
    
    await db.users.insert_one(student_doc)
    
    return StudentCreatedResponse(
        id=student_id,
        email=student_data.email,
        name=student_data.name,
        institution_id=student_data.institution_id,
        exam_type=student_data.exam_type,
        credits=student_data.credits,
        credits_used=0,
        is_active=True,
        created_at=student_doc["created_at"],
        last_activity=None,
        exam_attempts=0,
        average_score=None,
        metadata=student_data.metadata,
        provisional_password=provisional_password
    )

@router.post("/bulk", response_model=Dict[str, Any])
async def bulk_create_students(
    bulk_data: StudentBulkCreate,
    api_auth: dict = Depends(require_write)
):
    """
    Create multiple students at once.
    Returns list of created students with their provisional passwords.
    """
    created = []
    errors = []
    
    for student_data in bulk_data.students:
        try:
            # Check email
            existing = await db.users.find_one({"email": student_data.email})
            if existing:
                errors.append({"email": student_data.email, "error": "Email already exists"})
                continue
            
            # Get institution
            institution = await db.users.find_one({
                "id": student_data.institution_id,
                "user_type": "institution"
            })
            if not institution:
                errors.append({"email": student_data.email, "error": "Institution not found"})
                continue
            
            student_id = str(uuid.uuid4())
            provisional_password = generate_password()
            
            student_doc = {
                "id": student_id,
                "email": student_data.email,
                "name": student_data.name,
                "password_hash": hash_password(provisional_password),
                "user_type": "student",
                "institution_id": student_data.institution_id,
                "institution_name": institution.get("institution_name"),
                "current_exam": student_data.exam_type,
                "exam_access": [student_data.exam_type],
                "credits": student_data.credits,
                "credits_used": 0,
                "is_active": True,
                "requires_password_change": True,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "metadata": student_data.metadata
            }
            
            await db.users.insert_one(student_doc)
            
            created.append({
                "id": student_id,
                "email": student_data.email,
                "name": student_data.name,
                "provisional_password": provisional_password
            })
            
        except Exception as e:
            errors.append({"email": student_data.email, "error": str(e)})
    
    return {
        "created_count": len(created),
        "error_count": len(errors),
        "created": created,
        "errors": errors
    }

@router.get("/{student_id}", response_model=StudentResponse)
async def get_student(
    student_id: str,
    api_auth: dict = Depends(require_read)
):
    """Get a single student by ID"""
    student = await db.users.find_one(
        {"id": student_id, "user_type": "student"},
        {"_id": 0, "password_hash": 0, "provisional_password": 0}
    )
    
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    exam_count = await db.exam_attempts.count_documents({"user_id": student_id})
    avg_score_result = await db.exam_attempts.aggregate([
        {"$match": {"user_id": student_id}},
        {"$group": {"_id": None, "avg": {"$avg": "$score"}}}
    ]).to_list(1)
    avg_score = avg_score_result[0]["avg"] if avg_score_result else None
    
    return StudentResponse(
        id=student["id"],
        email=student["email"],
        name=student["name"],
        institution_id=student.get("institution_id", ""),
        exam_type=student.get("current_exam", ""),
        credits=student.get("credits", 0),
        credits_used=student.get("credits_used", 0),
        is_active=student.get("is_active", True),
        created_at=student.get("created_at", ""),
        last_activity=student.get("last_activity"),
        exam_attempts=exam_count,
        average_score=round(avg_score, 2) if avg_score else None,
        metadata=student.get("metadata")
    )

@router.patch("/{student_id}", response_model=StudentResponse)
async def update_student(
    student_id: str,
    update_data: StudentUpdate,
    api_auth: dict = Depends(require_write)
):
    """Update a student's details"""
    update_dict = {k: v for k, v in update_data.dict().items() if v is not None}
    
    if not update_dict:
        raise HTTPException(status_code=400, detail="No fields to update")
    
    # Map fields
    if "exam_type" in update_dict:
        update_dict["current_exam"] = update_dict.pop("exam_type")
    
    update_dict["updated_at"] = datetime.now(timezone.utc).isoformat()
    
    result = await db.users.update_one(
        {"id": student_id, "user_type": "student"},
        {"$set": update_dict}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Student not found")
    
    return await get_student(student_id, api_auth)

@router.delete("/{student_id}")
async def delete_student(
    student_id: str,
    api_auth: dict = Depends(require_admin)
):
    """
    Delete a student (admin scope required).
    This is a soft delete - sets is_active to False.
    """
    result = await db.users.update_one(
        {"id": student_id, "user_type": "student"},
        {"$set": {"is_active": False, "deleted_at": datetime.now(timezone.utc).isoformat()}}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Student not found")
    
    return {"message": "Student deleted successfully"}

@router.post("/{student_id}/credits")
async def add_student_credits(
    student_id: str,
    credits: int,
    api_auth: dict = Depends(require_write)
):
    """Add credits to a student's account"""
    if credits <= 0:
        raise HTTPException(status_code=400, detail="Credits must be positive")
    
    result = await db.users.update_one(
        {"id": student_id, "user_type": "student"},
        {"$inc": {"credits": credits}}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Student not found")
    
    # Get updated student
    student = await db.users.find_one({"id": student_id}, {"_id": 0, "credits": 1, "credits_used": 1})
    
    return {
        "message": f"Added {credits} credits",
        "credits_total": student["credits"],
        "credits_used": student.get("credits_used", 0),
        "credits_remaining": student["credits"] - student.get("credits_used", 0)
    }
