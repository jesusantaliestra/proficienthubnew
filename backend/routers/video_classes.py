"""
Video Classes Router - Live and recorded video class management
Handles class creation, enrollment, and status management
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timezone
import uuid

router = APIRouter(prefix="/video-classes", tags=["Video Classes"])

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

class VideoClassCreate(BaseModel):
    title: str
    description: Optional[str] = None
    exam_type: str
    skill: str  # reading, writing, speaking, listening
    class_type: str = "live"  # live, recorded
    duration_minutes: int = 60
    scheduled_at: Optional[str] = None
    max_participants: int = 50
    meeting_url: Optional[str] = None
    recording_url: Optional[str] = None

class VideoClassUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None  # scheduled, live, completed, cancelled
    meeting_url: Optional[str] = None
    recording_url: Optional[str] = None

# ==================== CLASS MANAGEMENT ====================

@router.post("")
async def create_video_class(
    video_class: VideoClassCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create a new video class"""
    if current_user.get("user_type") not in ["institution", "admin"]:
        raise HTTPException(status_code=403, detail="Institution access required")
    
    class_id = str(uuid.uuid4())
    
    class_doc = {
        "id": class_id,
        "institution_id": current_user["id"],
        "title": video_class.title,
        "description": video_class.description,
        "exam_type": video_class.exam_type,
        "skill": video_class.skill,
        "class_type": video_class.class_type,
        "duration_minutes": video_class.duration_minutes,
        "scheduled_at": video_class.scheduled_at,
        "max_participants": video_class.max_participants,
        "meeting_url": video_class.meeting_url,
        "recording_url": video_class.recording_url,
        "status": "scheduled",
        "enrolled_count": 0,
        "created_by": current_user["id"],
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.video_classes.insert_one(class_doc)
    
    return {"id": class_id, "message": "Video class created"}

@router.get("")
async def list_video_classes(
    exam_type: Optional[str] = None,
    skill: Optional[str] = None,
    class_type: Optional[str] = None,
    status: Optional[str] = None,
    page: int = 1,
    per_page: int = 20,
    current_user: dict = Depends(get_current_user)
):
    """List video classes"""
    # Build query based on user type
    query = {}
    
    if current_user.get("user_type") == "student":
        query["institution_id"] = current_user.get("institution_id")
        query["status"] = {"$in": ["scheduled", "live"]}
    elif current_user.get("user_type") == "institution":
        query["institution_id"] = current_user["id"]
    
    if exam_type:
        query["exam_type"] = exam_type
    if skill:
        query["skill"] = skill
    if class_type:
        query["class_type"] = class_type
    if status and current_user.get("user_type") != "student":
        query["status"] = status
    
    skip = (page - 1) * per_page
    
    classes = await db.video_classes.find(
        query, {"_id": 0}
    ).sort("scheduled_at", 1).skip(skip).limit(per_page).to_list(per_page)
    
    total = await db.video_classes.count_documents(query)
    
    # Check enrollment status for students
    if current_user.get("user_type") == "student":
        enrollments = await db.class_enrollments.find(
            {"student_id": current_user["id"]},
            {"class_id": 1, "_id": 0}
        ).to_list(100)
        enrolled_ids = {e["class_id"] for e in enrollments}
        
        for cls in classes:
            cls["is_enrolled"] = cls["id"] in enrolled_ids
    
    return {
        "classes": classes,
        "total": total,
        "page": page,
        "per_page": per_page
    }

@router.get("/{class_id}")
async def get_video_class(
    class_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get video class details"""
    video_class = await db.video_classes.find_one(
        {"id": class_id},
        {"_id": 0}
    )
    
    if not video_class:
        raise HTTPException(status_code=404, detail="Class not found")
    
    # Check access
    if current_user.get("user_type") == "student":
        if video_class["institution_id"] != current_user.get("institution_id"):
            raise HTTPException(status_code=403, detail="Access denied")
    elif current_user.get("user_type") == "institution":
        if video_class["institution_id"] != current_user["id"]:
            raise HTTPException(status_code=403, detail="Access denied")
    
    # Check enrollment for students
    if current_user.get("user_type") == "student":
        enrollment = await db.class_enrollments.find_one({
            "student_id": current_user["id"],
            "class_id": class_id
        })
        video_class["is_enrolled"] = enrollment is not None
    
    return video_class

@router.post("/{class_id}/enroll")
async def enroll_in_class(
    class_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Enroll student in a video class"""
    if current_user.get("user_type") != "student":
        raise HTTPException(status_code=403, detail="Student access required")
    
    # Check class exists
    video_class = await db.video_classes.find_one({"id": class_id})
    if not video_class:
        raise HTTPException(status_code=404, detail="Class not found")
    
    # Check not already enrolled
    existing = await db.class_enrollments.find_one({
        "student_id": current_user["id"],
        "class_id": class_id
    })
    if existing:
        raise HTTPException(status_code=400, detail="Already enrolled")
    
    # Check capacity
    if video_class.get("enrolled_count", 0) >= video_class.get("max_participants", 50):
        raise HTTPException(status_code=400, detail="Class is full")
    
    # Create enrollment
    await db.class_enrollments.insert_one({
        "id": str(uuid.uuid4()),
        "student_id": current_user["id"],
        "class_id": class_id,
        "enrolled_at": datetime.now(timezone.utc).isoformat()
    })
    
    # Update count
    await db.video_classes.update_one(
        {"id": class_id},
        {"$inc": {"enrolled_count": 1}}
    )
    
    return {"message": "Enrolled successfully"}

@router.put("/{class_id}/status")
async def update_class_status(
    class_id: str,
    status: str,
    current_user: dict = Depends(get_current_user)
):
    """Update video class status"""
    if current_user.get("user_type") not in ["institution", "admin"]:
        raise HTTPException(status_code=403, detail="Institution access required")
    
    valid_statuses = ["scheduled", "live", "completed", "cancelled"]
    if status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of: {valid_statuses}")
    
    result = await db.video_classes.update_one(
        {"id": class_id, "institution_id": current_user["id"]},
        {"$set": {
            "status": status,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Class not found")
    
    return {"message": f"Status updated to {status}"}

@router.delete("/{class_id}")
async def delete_video_class(
    class_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete a video class"""
    if current_user.get("user_type") not in ["institution", "admin"]:
        raise HTTPException(status_code=403, detail="Institution access required")
    
    result = await db.video_classes.delete_one({
        "id": class_id,
        "institution_id": current_user["id"]
    })
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Class not found")
    
    # Delete enrollments
    await db.class_enrollments.delete_many({"class_id": class_id})
    
    return {"message": "Class deleted"}
