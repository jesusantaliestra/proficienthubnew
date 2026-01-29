"""
Student Router - Student-specific endpoints
Handles student profile, credits, classes, and placement tests
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timezone
import uuid

router = APIRouter(prefix="/student", tags=["Student"])

# Import shared dependencies
import sys
sys.path.append('/app/backend')
from motor.motor_asyncio import AsyncIOMotorClient
import os

client = AsyncIOMotorClient(os.environ.get('MONGO_URL'))
db = client[os.environ.get('DB_NAME', 'proficienthub')]

# Auth dependency
from server import get_current_user

# ==================== MODELS ====================

class CreditUsage(BaseModel):
    credits: int
    purpose: str  # exam, tutor, material

class PlacementTestSubmit(BaseModel):
    answers: List[dict]
    time_taken: int

# ==================== PROFILE ====================

@router.get("/profile")
async def get_student_profile(current_user: dict = Depends(get_current_user)):
    """Get student profile with progress data"""
    if current_user.get("user_type") != "student":
        raise HTTPException(status_code=403, detail="Student access required")
    
    user_id = current_user["id"]
    
    # Get exam history stats
    exam_stats = await db.exam_attempts.aggregate([
        {"$match": {"user_id": user_id, "status": "completed"}},
        {"$group": {
            "_id": None,
            "total_exams": {"$sum": 1},
            "avg_score": {"$avg": "$score"},
            "total_time": {"$sum": "$time_taken"}
        }}
    ]).to_list(1)
    
    stats = exam_stats[0] if exam_stats else {"total_exams": 0, "avg_score": 0, "total_time": 0}
    
    # Get badge count
    badges = await db.user_badges.count_documents({"user_id": user_id})
    
    # Get streak
    streak_data = await db.user_streaks.find_one({"user_id": user_id})
    
    return {
        "id": current_user["id"],
        "name": current_user.get("name"),
        "email": current_user.get("email"),
        "current_exam": current_user.get("current_exam") or current_user.get("exam_type"),
        "target_band": current_user.get("target_band"),
        "credits": current_user.get("credits", 0),
        "language": current_user.get("language", "en"),
        "gamification_enabled": current_user.get("gamification_enabled", True),
        "stats": {
            "exams_completed": stats.get("total_exams", 0),
            "avg_score": round(stats.get("avg_score") or 0, 1),
            "total_study_time": stats.get("total_time", 0),
            "badges_earned": badges
        },
        "streak": {
            "current": streak_data.get("current_streak", 0) if streak_data else 0,
            "longest": streak_data.get("longest_streak", 0) if streak_data else 0
        }
    }

# ==================== CREDITS ====================

@router.get("/credits")
async def get_student_credits(current_user: dict = Depends(get_current_user)):
    """Get student's remaining credits"""
    if current_user.get("user_type") != "student":
        raise HTTPException(status_code=403, detail="Student access required")
    
    return {
        "credits": current_user.get("credits", 0),
        "unlimited": current_user.get("unlimited_credits", False)
    }

@router.post("/use-credits")
async def use_credits(
    usage: CreditUsage,
    current_user: dict = Depends(get_current_user)
):
    """Use credits for exam, tutor, or material"""
    if current_user.get("user_type") != "student":
        raise HTTPException(status_code=403, detail="Student access required")
    
    current_credits = current_user.get("credits", 0)
    
    if current_credits < usage.credits and not current_user.get("unlimited_credits"):
        raise HTTPException(status_code=400, detail="Insufficient credits")
    
    # Deduct credits
    new_credits = max(0, current_credits - usage.credits)
    
    await db.users.update_one(
        {"id": current_user["id"]},
        {"$set": {"credits": new_credits}}
    )
    
    # Log usage
    await db.credit_transactions.insert_one({
        "id": str(uuid.uuid4()),
        "user_id": current_user["id"],
        "amount": -usage.credits,
        "purpose": usage.purpose,
        "balance_after": new_credits,
        "created_at": datetime.now(timezone.utc).isoformat()
    })
    
    return {
        "credits_used": usage.credits,
        "remaining_credits": new_credits
    }

# ==================== UPCOMING CLASSES ====================

@router.get("/upcoming-classes")
async def get_upcoming_classes(current_user: dict = Depends(get_current_user)):
    """Get student's upcoming video classes"""
    if current_user.get("user_type") != "student":
        raise HTTPException(status_code=403, detail="Student access required")
    
    now = datetime.now(timezone.utc).isoformat()
    
    # Get enrolled classes
    enrollments = await db.class_enrollments.find(
        {"student_id": current_user["id"]},
        {"class_id": 1, "_id": 0}
    ).to_list(100)
    
    class_ids = [e["class_id"] for e in enrollments]
    
    if not class_ids:
        return {"classes": []}
    
    classes = await db.video_classes.find(
        {
            "id": {"$in": class_ids},
            "scheduled_at": {"$gte": now},
            "status": {"$in": ["scheduled", "live"]}
        },
        {"_id": 0}
    ).sort("scheduled_at", 1).limit(10).to_list(10)
    
    return {"classes": classes}

# ==================== PLACEMENT TEST ====================

@router.get("/should-take-placement-test")
async def should_take_placement_test(current_user: dict = Depends(get_current_user)):
    """Check if student should take placement test"""
    if current_user.get("user_type") != "student":
        raise HTTPException(status_code=403, detail="Student access required")
    
    # Check if already taken
    existing = await db.placement_tests.find_one({
        "user_id": current_user["id"],
        "exam_type": current_user.get("current_exam")
    })
    
    if existing:
        return {
            "should_take": False,
            "reason": "already_completed",
            "previous_result": {
                "level": existing.get("level"),
                "score": existing.get("score"),
                "taken_at": existing.get("created_at")
            }
        }
    
    return {
        "should_take": True,
        "exam_type": current_user.get("current_exam")
    }

@router.post("/placement-test/submit")
async def submit_placement_test(
    submission: PlacementTestSubmit,
    current_user: dict = Depends(get_current_user)
):
    """Submit placement test answers"""
    if current_user.get("user_type") != "student":
        raise HTTPException(status_code=403, detail="Student access required")
    
    # Simple scoring (can be enhanced)
    correct = sum(1 for a in submission.answers if a.get("correct", False))
    total = len(submission.answers)
    score = (correct / total * 100) if total > 0 else 0
    
    # Determine level
    if score >= 80:
        level = "advanced"
    elif score >= 60:
        level = "intermediate"
    elif score >= 40:
        level = "pre-intermediate"
    else:
        level = "beginner"
    
    # Save result
    result_id = str(uuid.uuid4())
    await db.placement_tests.insert_one({
        "id": result_id,
        "user_id": current_user["id"],
        "exam_type": current_user.get("current_exam"),
        "answers": submission.answers,
        "score": score,
        "level": level,
        "time_taken": submission.time_taken,
        "created_at": datetime.now(timezone.utc).isoformat()
    })
    
    # Update user level
    await db.users.update_one(
        {"id": current_user["id"]},
        {"$set": {"proficiency_level": level}}
    )
    
    return {
        "id": result_id,
        "score": round(score, 1),
        "level": level,
        "correct_answers": correct,
        "total_questions": total
    }
