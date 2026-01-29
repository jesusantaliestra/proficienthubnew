"""
Admin Router - Admin panel endpoints
Handles admin settings, exam bank, trial requests, and analytics
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
import uuid

router = APIRouter(prefix="/admin", tags=["Admin"])

# Import shared dependencies
import sys
sys.path.append('/app/backend')
from motor.motor_asyncio import AsyncIOMotorClient
import os

client = AsyncIOMotorClient(os.environ.get('MONGO_URL'))
db = client[os.environ.get('DB_NAME', 'proficienthub')]

# Auth dependency - import from main server
from server import get_current_user

async def get_admin_user(current_user: dict = Depends(get_current_user)):
    if current_user.get("user_type") not in ["admin", "institution"]:
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user

# ==================== SETTINGS ====================

@router.get("/settings")
async def get_admin_settings(current_user: dict = Depends(get_admin_user)):
    """Get admin settings"""
    settings = await db.admin_settings.find_one(
        {"institution_id": current_user["id"]},
        {"_id": 0}
    )
    return settings or {}

@router.post("/settings")
async def update_admin_settings(
    settings: Dict[str, Any],
    current_user: dict = Depends(get_admin_user)
):
    """Update admin settings"""
    await db.admin_settings.update_one(
        {"institution_id": current_user["id"]},
        {"$set": {**settings, "updated_at": datetime.now(timezone.utc).isoformat()}},
        upsert=True
    )
    return {"message": "Settings updated"}

# ==================== STATS ====================

@router.get("/stats")
async def get_admin_stats(current_user: dict = Depends(get_admin_user)):
    """Get admin dashboard statistics"""
    institution_id = current_user["id"]
    
    # Count students
    total_students = await db.users.count_documents({
        "institution_id": institution_id,
        "user_type": "student"
    })
    
    # Count active students (logged in last 7 days)
    from datetime import timedelta
    week_ago = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()
    active_students = await db.users.count_documents({
        "institution_id": institution_id,
        "user_type": "student",
        "last_login": {"$gte": week_ago}
    })
    
    # Count exams
    total_exams = await db.exam_attempts.count_documents({
        "institution_id": institution_id
    })
    
    # Count library items
    library_items = await db.library_items.count_documents({
        "institution_id": institution_id
    })
    
    return {
        "total_students": total_students,
        "active_students": active_students,
        "total_exams": total_exams,
        "library_items": library_items
    }

# ==================== TRIAL REQUESTS ====================

@router.get("/trial-requests")
async def get_trial_requests(
    status: Optional[str] = None,
    page: int = 1,
    per_page: int = 20,
    current_user: dict = Depends(get_admin_user)
):
    """Get trial requests"""
    if current_user.get("user_type") != "admin":
        raise HTTPException(status_code=403, detail="Super admin access required")
    
    query = {}
    if status:
        query["status"] = status
    
    skip = (page - 1) * per_page
    
    requests = await db.trial_requests.find(
        query, {"_id": 0}
    ).sort("created_at", -1).skip(skip).limit(per_page).to_list(per_page)
    
    total = await db.trial_requests.count_documents(query)
    
    return {
        "requests": requests,
        "total": total,
        "page": page,
        "per_page": per_page
    }

# ==================== EXAM BANK ====================

@router.get("/exam-bank")
async def get_exam_bank(
    exam_type: Optional[str] = None,
    skill: Optional[str] = None,
    page: int = 1,
    per_page: int = 20,
    current_user: dict = Depends(get_admin_user)
):
    """Get exam bank items"""
    query = {"institution_id": current_user["id"]}
    
    if exam_type:
        query["exam_type"] = exam_type
    if skill:
        query["skill"] = skill
    
    skip = (page - 1) * per_page
    
    exams = await db.exam_bank.find(
        query, {"_id": 0}
    ).sort("created_at", -1).skip(skip).limit(per_page).to_list(per_page)
    
    total = await db.exam_bank.count_documents(query)
    
    return {
        "exams": exams,
        "total": total,
        "page": page,
        "per_page": per_page
    }

@router.get("/exam-bank/{exam_id}")
async def get_exam_bank_item(
    exam_id: str,
    current_user: dict = Depends(get_admin_user)
):
    """Get specific exam bank item"""
    exam = await db.exam_bank.find_one(
        {"id": exam_id, "institution_id": current_user["id"]},
        {"_id": 0}
    )
    
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found")
    
    return exam

@router.post("/exam-bank/validate/{exam_id}")
async def validate_exam(
    exam_id: str,
    current_user: dict = Depends(get_admin_user)
):
    """Validate exam content"""
    exam = await db.exam_bank.find_one(
        {"id": exam_id, "institution_id": current_user["id"]}
    )
    
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found")
    
    # Basic validation
    issues = []
    
    if not exam.get("questions"):
        issues.append("No questions found")
    else:
        for i, q in enumerate(exam.get("questions", [])):
            if not q.get("question_text"):
                issues.append(f"Question {i+1}: Missing question text")
            if not q.get("options") and exam.get("skill") not in ["speaking", "writing"]:
                issues.append(f"Question {i+1}: Missing options")
    
    return {
        "valid": len(issues) == 0,
        "issues": issues,
        "exam_id": exam_id
    }

# ==================== EXAM OVERVIEW ====================

@router.get("/exam-overview")
async def get_exam_overview(current_user: dict = Depends(get_admin_user)):
    """Get exam overview statistics"""
    institution_id = current_user["id"]
    
    # Aggregate exam stats by type
    pipeline = [
        {"$match": {"institution_id": institution_id}},
        {"$group": {
            "_id": "$exam_type",
            "total_attempts": {"$sum": 1},
            "avg_score": {"$avg": "$score"},
            "completed": {"$sum": {"$cond": [{"$eq": ["$status", "completed"]}, 1, 0]}}
        }}
    ]
    
    exam_stats = await db.exam_attempts.aggregate(pipeline).to_list(20)
    
    return {
        "by_exam_type": {
            stat["_id"]: {
                "total_attempts": stat["total_attempts"],
                "avg_score": round(stat.get("avg_score") or 0, 1),
                "completed": stat["completed"]
            }
            for stat in exam_stats if stat["_id"]
        }
    }

# ==================== PRICING ANALYSIS ====================

@router.get("/pricing-analysis")
async def get_pricing_analysis(current_user: dict = Depends(get_admin_user)):
    """Get pricing and revenue analysis"""
    institution_id = current_user["id"]
    
    # Get subscription data
    subscriptions = await db.erp_subscriptions.find(
        {"institution_id": institution_id},
        {"_id": 0}
    ).to_list(100)
    
    total_mrr = sum(s.get("mrr", 0) for s in subscriptions)
    
    # Get invoice data
    invoices = await db.erp_invoices.find(
        {"institution_id": institution_id, "status": "paid"},
        {"_id": 0, "totals": 1}
    ).to_list(1000)
    
    total_revenue = sum(i.get("totals", {}).get("total", 0) for i in invoices)
    
    return {
        "total_mrr": total_mrr,
        "total_arr": total_mrr * 12,
        "total_revenue": total_revenue,
        "active_subscriptions": len([s for s in subscriptions if s.get("status") == "active"])
    }
