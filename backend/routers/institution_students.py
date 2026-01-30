"""Institution Students Router - Student management by institutions"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timezone
import uuid
import secrets
import string

from database import db
from utils.auth import get_current_user, hash_password

router = APIRouter(prefix="/institution", tags=["Institution - Students"])

# Models
class StudentCreateWithCredits(BaseModel):
    email: str
    name: str
    credits: int = 10
    exam_type: str = "oet"

class StudentResponse(BaseModel):
    id: str
    email: str
    name: str
    user_type: str
    institution_id: str
    credits: Optional[int] = 0
    credits_used: Optional[int] = 0
    current_exam: Optional[str] = None
    status: Optional[str] = "active"

class StudentCreditsUpdate(BaseModel):
    credits: int

class StudentExamUpdate(BaseModel):
    exam_type: str
    additional_credits: int = 0

def generate_provisional_password():
    return ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(12))

@router.post("/students/create")
async def create_student_with_credentials(
    student_data: StudentCreateWithCredits,
    current_user: dict = Depends(get_current_user)
):
    """Create a student with provisional credentials and credits"""
    if current_user["user_type"] != "institution":
        raise HTTPException(status_code=403, detail="Only institutions can create students")
    
    existing = await db.users.find_one({"email": student_data.email})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    provisional_password = generate_provisional_password()
    student_id = str(uuid.uuid4())
    
    student_doc = {
        "id": student_id,
        "email": student_data.email,
        "name": student_data.name,
        "password_hash": hash_password(provisional_password),
        "user_type": "student",
        "institution_id": current_user["id"],
        "institution_slug": current_user.get("institution_slug"),
        "institution_name": current_user.get("institution_name"),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "requires_password_change": True,
        "provisional_password": provisional_password,
        "credits": student_data.credits,
        "credits_used": 0,
        "current_exam": student_data.exam_type,
        "exam_access": [student_data.exam_type],
        "status": "active",
        "language": "en",
        "settings": {}
    }
    
    await db.users.insert_one(student_doc)
    
    return {
        "id": student_id,
        "email": student_data.email,
        "name": student_data.name,
        "provisional_password": provisional_password,
        "credits": student_data.credits,
        "exam_type": student_data.exam_type,
        "message": "Student created. Share the provisional password with the student."
    }

@router.post("/students/bulk-create")
async def bulk_create_students(
    students: List[StudentCreateWithCredits],
    current_user: dict = Depends(get_current_user)
):
    """Create multiple students at once"""
    if current_user["user_type"] != "institution":
        raise HTTPException(status_code=403, detail="Only institutions can create students")
    
    created = []
    errors = []
    
    for student_data in students:
        try:
            existing = await db.users.find_one({"email": student_data.email})
            if existing:
                errors.append({"email": student_data.email, "error": "Email already exists"})
                continue
            
            provisional_password = generate_provisional_password()
            student_id = str(uuid.uuid4())
            
            student_doc = {
                "id": student_id,
                "email": student_data.email,
                "name": student_data.name,
                "password_hash": hash_password(provisional_password),
                "user_type": "student",
                "institution_id": current_user["id"],
                "institution_slug": current_user.get("institution_slug"),
                "institution_name": current_user.get("institution_name"),
                "created_at": datetime.now(timezone.utc).isoformat(),
                "requires_password_change": True,
                "provisional_password": provisional_password,
                "credits": student_data.credits,
                "credits_used": 0,
                "current_exam": student_data.exam_type,
                "exam_access": [student_data.exam_type],
                "status": "active",
                "language": "en",
                "settings": {}
            }
            
            await db.users.insert_one(student_doc)
            created.append({
                "email": student_data.email,
                "name": student_data.name,
                "provisional_password": provisional_password,
                "credits": student_data.credits
            })
        except Exception as e:
            errors.append({"email": student_data.email, "error": str(e)})
    
    return {
        "created_count": len(created),
        "error_count": len(errors),
        "created": created,
        "errors": errors
    }

@router.put("/students/{student_id}/credits")
async def update_student_credits(
    student_id: str,
    update: StudentCreditsUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Add or update student credits"""
    if current_user["user_type"] != "institution":
        raise HTTPException(status_code=403, detail="Only institutions can manage credits")
    
    student = await db.users.find_one({
        "id": student_id,
        "institution_id": current_user["id"]
    })
    
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    await db.users.update_one(
        {"id": student_id},
        {"$set": {"credits": update.credits}}
    )
    
    return {"message": "Credits updated", "new_credits": update.credits}

@router.put("/students/{student_id}/exam")
async def update_student_exam(
    student_id: str,
    update: StudentExamUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Update student's exam type and optionally add credits"""
    if current_user["user_type"] != "institution":
        raise HTTPException(status_code=403, detail="Only institutions can manage exams")
    
    student = await db.users.find_one({
        "id": student_id,
        "institution_id": current_user["id"]
    })
    
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    update_fields = {
        "current_exam": update.exam_type,
        "exam_access": [update.exam_type]
    }
    
    if update.additional_credits > 0:
        new_credits = student.get("credits", 0) + update.additional_credits
        update_fields["credits"] = new_credits
    
    await db.users.update_one(
        {"id": student_id},
        {"$set": update_fields}
    )
    
    return {
        "message": "Exam updated",
        "exam_type": update.exam_type,
        "credits": update_fields.get("credits", student.get("credits", 0))
    }

@router.post("/students")
async def create_student(
    student_data: StudentCreateWithCredits,
    current_user: dict = Depends(get_current_user)
):
    """Create a new student (alias for /students/create)"""
    return await create_student_with_credentials(student_data, current_user)

@router.get("/students")
async def get_institution_students(
    limit: int = 50,
    skip: int = 0,
    search: Optional[str] = None,
    exam_type: Optional[str] = None,
    status: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """Get all students for the institution with filters"""
    if current_user["user_type"] != "institution":
        raise HTTPException(status_code=403, detail="Only institutions can view students")
    
    query = {"institution_id": current_user["id"], "user_type": "student"}
    
    if search:
        query["$or"] = [
            {"name": {"$regex": search, "$options": "i"}},
            {"email": {"$regex": search, "$options": "i"}}
        ]
    
    if exam_type:
        query["current_exam"] = exam_type
    
    if status:
        query["status"] = status
    
    students = await db.users.find(
        query,
        {"_id": 0, "password_hash": 0}
    ).sort("created_at", -1).skip(skip).limit(limit).to_list(limit)
    
    total = await db.users.count_documents(query)
    
    return {
        "students": students,
        "total": total,
        "limit": limit,
        "skip": skip
    }

@router.get("/students/{student_id}")
async def get_student_details(
    student_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get detailed student information"""
    if current_user["user_type"] != "institution":
        raise HTTPException(status_code=403, detail="Access denied")
    
    student = await db.users.find_one(
        {"id": student_id, "institution_id": current_user["id"]},
        {"_id": 0, "password_hash": 0}
    )
    
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    # Get exam attempts
    attempts = await db.exam_attempts.find(
        {"user_id": student_id},
        {"_id": 0}
    ).sort("created_at", -1).limit(10).to_list(10)
    
    student["recent_attempts"] = attempts
    
    return student

@router.delete("/students/{student_id}")
async def deactivate_student(
    student_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Deactivate a student (soft delete)"""
    if current_user["user_type"] != "institution":
        raise HTTPException(status_code=403, detail="Only institutions can manage students")
    
    result = await db.users.update_one(
        {"id": student_id, "institution_id": current_user["id"]},
        {"$set": {"status": "inactive", "deactivated_at": datetime.now(timezone.utc).isoformat()}}
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Student not found")
    
    return {"message": "Student deactivated"}
