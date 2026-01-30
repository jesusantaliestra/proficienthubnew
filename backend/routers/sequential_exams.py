"""Sequential Exams Router - Unique exam assignment per user"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
import uuid

from database import db
from utils.auth import get_current_user

router = APIRouter(prefix="/sequential-exams", tags=["Sequential Exams"])

# Configuration
EXAMS_PER_BANK = 100  # Each exam type has 100 unique exams

# Exam sections by type
EXAM_SECTIONS = {
    "ielts_academic": ["listening", "reading", "writing", "speaking"],
    "ielts_general": ["listening", "reading", "writing", "speaking"],
    "oet": ["listening", "reading", "writing", "speaking"],
    "toefl": ["reading", "listening", "speaking", "writing"],
    "cambridge": ["reading", "writing", "listening", "speaking"],
    "pte": ["speaking_writing", "reading", "listening"],
    "default": ["section_1", "section_2", "section_3", "section_4"]
}

# Models
class ExamPurchase(BaseModel):
    exam_type: str
    num_exams: int
    with_ai: bool = False

class StartExamRequest(BaseModel):
    exam_id: str
    mode: str  # "full" or "sections"

class CompleteSectionRequest(BaseModel):
    section: str
    score: float = 0
    answers: Optional[Dict[str, Any]] = None
    time_taken_seconds: int = 0

class ExamAccessResponse(BaseModel):
    exam_type: str
    available_exams: List[str]
    completed_exams: List[str]
    total_purchased: int
    next_exam: Optional[str]

def generate_exam_id(number: int) -> str:
    """Generate exam ID like '001', '002', etc."""
    return f"{number:03d}"

def get_next_exam_sequence(current_sequence: int, num_new_exams: int) -> List[str]:
    """
    Get the next sequence of exam IDs.
    If we exceed 100, we cycle back to 001.
    """
    new_exams = []
    for i in range(num_new_exams):
        # Calculate the next exam number (1-indexed, cycling at 100)
        next_num = ((current_sequence + i) % EXAMS_PER_BANK) + 1
        new_exams.append(generate_exam_id(next_num))
    return new_exams

def get_sections_for_exam_type(exam_type: str) -> List[str]:
    """Get sections for a given exam type"""
    return EXAM_SECTIONS.get(exam_type, EXAM_SECTIONS["default"])

@router.get("/my-access/{exam_type}")
async def get_my_exam_access(
    exam_type: str,
    current_user: dict = Depends(get_current_user)
):
    """Get user's exam access for a specific exam type"""
    
    user_id = current_user["id"]
    
    # Get or create exam access record
    access = await db.user_exam_access.find_one(
        {"user_id": user_id, "exam_type": exam_type},
        {"_id": 0}
    )
    
    if not access:
        return {
            "exam_type": exam_type,
            "available_exams": [],
            "completed_exams": [],
            "total_purchased": 0,
            "next_exam": None,
            "message": "No exams purchased for this type"
        }
    
    # Determine next exam to take
    completed = set(access.get("completed_exams", []))
    available = access.get("available_exams", [])
    next_exam = None
    
    for exam_id in available:
        if exam_id not in completed:
            next_exam = exam_id
            break
    
    return {
        "exam_type": exam_type,
        "available_exams": available,
        "completed_exams": list(completed),
        "total_purchased": access.get("total_purchased", 0),
        "current_sequence": access.get("current_sequence", 0),
        "next_exam": next_exam,
        "all_completed": len(completed) >= len(available)
    }

@router.post("/purchase")
async def purchase_exams(
    purchase: ExamPurchase,
    current_user: dict = Depends(get_current_user)
):
    """
    Purchase exams - assigns sequential unique exams to user.
    
    Logic:
    - First purchase of 5: gets exams 001-005
    - Upsell of 5 more: gets exams 006-010
    - Upsell of 5 more: gets exams 011-015
    - After 100 unique exams, cycles back to 001
    """
    
    user_id = current_user["id"]
    exam_type = purchase.exam_type
    num_exams = purchase.num_exams
    
    # Get current access record
    access = await db.user_exam_access.find_one(
        {"user_id": user_id, "exam_type": exam_type}
    )
    
    if access:
        current_sequence = access.get("current_sequence", 0)
        existing_exams = access.get("available_exams", [])
        total_purchased = access.get("total_purchased", 0)
    else:
        current_sequence = 0
        existing_exams = []
        total_purchased = 0
    
    # Generate new exam IDs
    new_exams = get_next_exam_sequence(current_sequence, num_exams)
    new_sequence = current_sequence + num_exams
    
    # Combine with existing (new exams are added at the end)
    all_exams = existing_exams + new_exams
    
    # Check if we're cycling (for informational purposes)
    is_cycling = new_sequence > EXAMS_PER_BANK
    
    # Update or create access record
    access_doc = {
        "user_id": user_id,
        "exam_type": exam_type,
        "available_exams": all_exams,
        "current_sequence": new_sequence,
        "total_purchased": total_purchased + num_exams,
        "with_ai": purchase.with_ai or (access.get("with_ai", False) if access else False),
        "completed_exams": access.get("completed_exams", []) if access else [],
        "last_purchase_at": datetime.now(timezone.utc).isoformat(),
        "purchase_history": (access.get("purchase_history", []) if access else []) + [{
            "date": datetime.now(timezone.utc).isoformat(),
            "num_exams": num_exams,
            "exams_assigned": new_exams,
            "with_ai": purchase.with_ai
        }]
    }
    
    if access:
        await db.user_exam_access.update_one(
            {"user_id": user_id, "exam_type": exam_type},
            {"$set": access_doc}
        )
    else:
        access_doc["created_at"] = datetime.now(timezone.utc).isoformat()
        await db.user_exam_access.insert_one(access_doc)
    
    return {
        "success": True,
        "exam_type": exam_type,
        "new_exams": new_exams,
        "total_available": len(all_exams),
        "message": f"Exams {new_exams[0]}-{new_exams[-1]} unlocked!",
        "is_cycling": is_cycling,
        "next_exam": new_exams[0] if not existing_exams else (
            # Find next uncompleted exam
            next((e for e in all_exams if e not in access_doc["completed_exams"]), new_exams[0])
        )
    }

@router.post("/complete/{exam_type}/{exam_id}")
async def complete_exam(
    exam_type: str,
    exam_id: str,
    score: float = 0,
    current_user: dict = Depends(get_current_user)
):
    """Mark an exam as completed"""
    
    user_id = current_user["id"]
    
    # Verify user has access to this exam
    access = await db.user_exam_access.find_one(
        {"user_id": user_id, "exam_type": exam_type}
    )
    
    if not access:
        raise HTTPException(status_code=403, detail="No access to this exam type")
    
    if exam_id not in access.get("available_exams", []):
        raise HTTPException(status_code=403, detail="Exam not unlocked")
    
    # Add to completed if not already
    completed = access.get("completed_exams", [])
    if exam_id not in completed:
        completed.append(exam_id)
        
        await db.user_exam_access.update_one(
            {"user_id": user_id, "exam_type": exam_type},
            {"$set": {"completed_exams": completed}}
        )
    
    # Record attempt
    await db.exam_attempts.insert_one({
        "id": str(uuid.uuid4()),
        "user_id": user_id,
        "exam_type": exam_type,
        "exam_id": exam_id,
        "score": score,
        "completed_at": datetime.now(timezone.utc).isoformat(),
        "institution_id": current_user.get("institution_id")
    })
    
    # Find next exam
    available = access.get("available_exams", [])
    next_exam = None
    for e in available:
        if e not in completed:
            next_exam = e
            break
    
    return {
        "success": True,
        "exam_id": exam_id,
        "score": score,
        "completed_count": len(completed),
        "total_available": len(available),
        "next_exam": next_exam,
        "all_completed": next_exam is None
    }

@router.get("/dashboard/{exam_type}")
async def get_exam_dashboard(
    exam_type: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Get comprehensive dashboard data for exam type.
    Shows all available exams with completion status.
    """
    
    user_id = current_user["id"]
    
    access = await db.user_exam_access.find_one(
        {"user_id": user_id, "exam_type": exam_type},
        {"_id": 0}
    )
    
    if not access:
        return {
            "exam_type": exam_type,
            "exams": [],
            "stats": {
                "total_purchased": 0,
                "completed": 0,
                "remaining": 0,
                "completion_rate": 0
            },
            "has_ai": False,
            "message": "No exams purchased. Purchase a plan to get started!"
        }
    
    available = access.get("available_exams", [])
    completed = set(access.get("completed_exams", []))
    
    # Build exam list with status
    exams = []
    for i, exam_id in enumerate(available):
        is_completed = exam_id in completed
        
        # Get attempt data if completed
        attempt = None
        if is_completed:
            attempt = await db.exam_attempts.find_one(
                {"user_id": user_id, "exam_type": exam_type, "exam_id": exam_id},
                {"_id": 0, "score": 1, "completed_at": 1}
            )
        
        exams.append({
            "exam_id": exam_id,
            "exam_number": i + 1,
            "display_name": f"{exam_type.upper()} Exam {exam_id}",
            "status": "completed" if is_completed else "available",
            "score": attempt.get("score") if attempt else None,
            "completed_at": attempt.get("completed_at") if attempt else None
        })
    
    # Calculate stats
    completed_count = len(completed)
    total = len(available)
    
    return {
        "exam_type": exam_type,
        "exams": exams,
        "stats": {
            "total_purchased": total,
            "completed": completed_count,
            "remaining": total - completed_count,
            "completion_rate": round(completed_count / total * 100, 1) if total > 0 else 0
        },
        "has_ai": access.get("with_ai", False),
        "purchase_history": access.get("purchase_history", []),
        "can_upsell": True,  # Can always buy more
        "next_exam": next((e["exam_id"] for e in exams if e["status"] == "available"), None)
    }

@router.post("/upsell")
async def upsell_exams(
    purchase: ExamPurchase,
    current_user: dict = Depends(get_current_user)
):
    """
    Upsell more exams to existing access.
    Simply calls purchase with existing context.
    """
    return await purchase_exams(purchase, current_user)

# Admin endpoint to check user's exam sequence
@router.get("/admin/user-access/{user_id}/{exam_type}")
async def admin_get_user_access(
    user_id: str,
    exam_type: str,
    current_user: dict = Depends(get_current_user)
):
    """Admin endpoint to view user's exam access"""
    
    if current_user.get("user_type") not in ["admin", "institution"]:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    access = await db.user_exam_access.find_one(
        {"user_id": user_id, "exam_type": exam_type},
        {"_id": 0}
    )
    
    if not access:
        return {"message": "No access record found"}
    
    return access

# Batch check for multiple exam types
@router.get("/my-access-all")
async def get_all_exam_access(current_user: dict = Depends(get_current_user)):
    """Get user's exam access for all exam types"""
    
    user_id = current_user["id"]
    
    access_records = await db.user_exam_access.find(
        {"user_id": user_id},
        {"_id": 0}
    ).to_list(20)
    
    result = {}
    for access in access_records:
        exam_type = access["exam_type"]
        completed = set(access.get("completed_exams", []))
        available = access.get("available_exams", [])
        
        result[exam_type] = {
            "total_purchased": len(available),
            "completed": len(completed),
            "remaining": len(available) - len(completed),
            "next_exam": next((e for e in available if e not in completed), None),
            "has_ai": access.get("with_ai", False)
        }
    
    return result
