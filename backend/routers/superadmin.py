"""Superadmin dashboard router"""
from fastapi import APIRouter, Depends, HTTPException, Query
from datetime import datetime, timezone, timedelta
from typing import Optional

from database import db
from utils.auth import get_current_user

router = APIRouter(prefix="/superadmin", tags=["Superadmin"])

@router.get("/stats")
async def get_superadmin_stats(current_user: dict = Depends(get_current_user)):
    """Get platform-wide statistics for superadmin"""
    if current_user.get("user_type") != "admin" or not current_user.get("is_superadmin"):
        raise HTTPException(status_code=403, detail="Superadmin access required")
    
    # Count institutions
    institutions_count = await db.users.count_documents({"user_type": "institution"})
    
    # Count students
    students_count = await db.users.count_documents({"user_type": "student"})
    
    # Individual users
    individual_count = await db.users.count_documents({"user_type": "individual"})
    
    # Active users (last 7 days)
    week_ago = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()
    active_users = await db.exam_attempts.distinct("user_id", {"created_at": {"$gte": week_ago}})
    
    # Active users (last 30 days)
    month_ago = (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()
    monthly_active = await db.exam_attempts.distinct("user_id", {"created_at": {"$gte": month_ago}})
    
    # Total exams taken
    total_exams = await db.exam_attempts.count_documents({})
    exams_this_week = await db.exam_attempts.count_documents({"created_at": {"$gte": week_ago}})
    exams_this_month = await db.exam_attempts.count_documents({"created_at": {"$gte": month_ago}})
    
    # AI usage
    ai_interactions = await db.ai_agent_history.count_documents({})
    ai_this_week = await db.ai_agent_history.count_documents({"created_at": {"$gte": week_ago}})
    
    # Revenue / Credits
    credits_pipeline = [
        {"$group": {
            "_id": None, 
            "total_purchased": {"$sum": "$purchased_credits"},
            "total_used": {"$sum": "$used_credits"},
            "total_free": {"$sum": "$free_credits"}
        }}
    ]
    credits_stats = await db.ai_credits.aggregate(credits_pipeline).to_list(1)
    credits_data = credits_stats[0] if credits_stats else {"total_purchased": 0, "total_used": 0, "total_free": 0}
    
    # Exam distribution by type
    exam_distribution = await db.exam_attempts.aggregate([
        {"$group": {"_id": "$exam_type", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ]).to_list(20)
    
    # New registrations this week
    new_institutions_week = await db.users.count_documents({
        "user_type": "institution",
        "created_at": {"$gte": week_ago}
    })
    new_students_week = await db.users.count_documents({
        "user_type": "student", 
        "created_at": {"$gte": week_ago}
    })
    
    # Average score by exam type
    avg_scores = await db.exam_attempts.aggregate([
        {"$group": {"_id": "$exam_type", "avg_score": {"$avg": "$score"}}},
        {"$sort": {"avg_score": -1}}
    ]).to_list(20)
    
    return {
        "platform_stats": {
            "total_institutions": institutions_count,
            "total_students": students_count,
            "total_individuals": individual_count,
            "total_users": institutions_count + students_count + individual_count,
            "active_users_7d": len(active_users),
            "active_users_30d": len(monthly_active),
        },
        "exam_stats": {
            "total_exams_taken": total_exams,
            "exams_this_week": exams_this_week,
            "exams_this_month": exams_this_month,
            "exam_distribution": {item["_id"]: item["count"] for item in exam_distribution if item["_id"]},
            "average_scores": {item["_id"]: round(item["avg_score"], 2) for item in avg_scores if item["_id"]}
        },
        "ai_stats": {
            "total_ai_interactions": ai_interactions,
            "ai_interactions_this_week": ai_this_week,
            "total_credits_purchased": credits_data.get("total_purchased", 0),
            "total_credits_used": credits_data.get("total_used", 0),
            "total_free_credits_given": credits_data.get("total_free", 0)
        },
        "growth_stats": {
            "new_institutions_this_week": new_institutions_week,
            "new_students_this_week": new_students_week
        },
        "business_metrics": {
            "estimated_revenue_from_credits": credits_data.get("total_purchased", 0) * 0.10,  # $0.10 per credit
            "avg_credits_per_institution": round(credits_data.get("total_purchased", 0) / max(institutions_count, 1), 2),
            "student_to_institution_ratio": round(students_count / max(institutions_count, 1), 2),
            "platform_engagement_rate": round(len(monthly_active) / max(students_count + individual_count, 1) * 100, 2)
        },
        "generated_at": datetime.now(timezone.utc).isoformat()
    }

@router.get("/institutions")
async def get_all_institutions(
    limit: int = Query(default=50, le=100),
    skip: int = Query(default=0, ge=0),
    search: Optional[str] = None,
    sort_by: str = Query(default="created_at", enum=["created_at", "student_count", "name"]),
    current_user: dict = Depends(get_current_user)
):
    """Get all institutions for superadmin with advanced filtering"""
    if current_user.get("user_type") != "admin" or not current_user.get("is_superadmin"):
        raise HTTPException(status_code=403, detail="Superadmin access required")
    
    query = {"user_type": "institution"}
    
    if search:
        query["$or"] = [
            {"institution_name": {"$regex": search, "$options": "i"}},
            {"email": {"$regex": search, "$options": "i"}}
        ]
    
    institutions = await db.users.find(
        query,
        {"_id": 0, "password_hash": 0}
    ).skip(skip).limit(limit).to_list(limit)
    
    # Enrich with additional data
    for inst in institutions:
        # Student count
        student_count = await db.users.count_documents({"institution_id": inst["id"]})
        inst["student_count"] = student_count
        
        # Get AI credits
        credits = await db.ai_credits.find_one({"user_id": inst["id"]}, {"_id": 0})
        if credits:
            inst["ai_credits"] = {
                "total": credits.get("total_credits", 0),
                "used": credits.get("used_credits", 0),
                "available": credits.get("total_credits", 0) - credits.get("used_credits", 0)
            }
        else:
            inst["ai_credits"] = {"total": 0, "used": 0, "available": 0}
        
        # Exam attempts count
        week_ago = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()
        exam_attempts_week = await db.exam_attempts.count_documents({
            "institution_id": inst["id"],
            "created_at": {"$gte": week_ago}
        })
        inst["activity_this_week"] = exam_attempts_week
        
        # Settings status
        settings = await db.institution_settings.find_one({"institution_id": inst["id"]}, {"_id": 0})
        inst["has_zoom_configured"] = bool(settings and settings.get("zoom", {}).get("zoom_enabled"))
        inst["has_messaging_configured"] = bool(settings and settings.get("messaging", {}).get("enabled"))
        inst["gamification_enabled"] = bool(settings and settings.get("gamification", {}).get("enabled"))
    
    # Sort
    if sort_by == "student_count":
        institutions.sort(key=lambda x: x.get("student_count", 0), reverse=True)
    elif sort_by == "name":
        institutions.sort(key=lambda x: x.get("institution_name", "").lower())
    
    total = await db.users.count_documents(query)
    
    return {
        "institutions": institutions,
        "total": total,
        "limit": limit,
        "skip": skip,
        "has_more": skip + limit < total
    }

@router.get("/institutions/{institution_id}")
async def get_institution_details(
    institution_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get detailed information about a specific institution"""
    if current_user.get("user_type") != "admin" or not current_user.get("is_superadmin"):
        raise HTTPException(status_code=403, detail="Superadmin access required")
    
    institution = await db.users.find_one(
        {"id": institution_id, "user_type": "institution"},
        {"_id": 0, "password_hash": 0}
    )
    
    if not institution:
        raise HTTPException(status_code=404, detail="Institution not found")
    
    # Get students
    students = await db.users.find(
        {"institution_id": institution_id},
        {"_id": 0, "password_hash": 0, "id": 1, "name": 1, "email": 1, "created_at": 1, "current_exam": 1}
    ).limit(100).to_list(100)
    
    # Get settings
    settings = await db.institution_settings.find_one({"institution_id": institution_id}, {"_id": 0})
    
    # Get credits
    credits = await db.ai_credits.find_one({"user_id": institution_id}, {"_id": 0})
    
    # Get exam stats
    exam_stats = await db.exam_attempts.aggregate([
        {"$match": {"institution_id": institution_id}},
        {"$group": {
            "_id": "$exam_type",
            "count": {"$sum": 1},
            "avg_score": {"$avg": "$score"}
        }}
    ]).to_list(20)
    
    # Get AI usage history
    week_ago = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()
    ai_usage = await db.ai_agent_history.count_documents({
        "institution_id": institution_id,
        "created_at": {"$gte": week_ago}
    })
    
    return {
        "institution": institution,
        "students": students,
        "student_count": len(students),
        "settings": settings or {},
        "credits": credits or {"total_credits": 0, "used_credits": 0},
        "exam_stats": exam_stats,
        "ai_usage_this_week": ai_usage
    }

@router.post("/grant-credits")
async def grant_ai_credits(
    institution_id: str,
    credits: int,
    reason: str = "Promotional credits",
    current_user: dict = Depends(get_current_user)
):
    """Grant AI credits to an institution (superadmin only)"""
    if current_user.get("user_type") != "admin" or not current_user.get("is_superadmin"):
        raise HTTPException(status_code=403, detail="Superadmin access required")
    
    # Verify institution exists
    institution = await db.users.find_one({"id": institution_id, "user_type": "institution"})
    if not institution:
        raise HTTPException(status_code=404, detail="Institution not found")
    
    await db.ai_credits.update_one(
        {"user_id": institution_id},
        {
            "$inc": {"total_credits": credits, "free_credits": credits},
            "$push": {
                "credit_grants": {
                    "amount": credits,
                    "reason": reason,
                    "granted_by": current_user["id"],
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            }
        },
        upsert=True
    )
    
    return {"success": True, "message": f"Granted {credits} credits to {institution.get('institution_name', 'institution')}"}

@router.get("/activity-log")
async def get_platform_activity_log(
    limit: int = Query(default=50, le=200),
    activity_type: Optional[str] = Query(default=None, enum=["exam", "ai", "registration", "login"]),
    current_user: dict = Depends(get_current_user)
):
    """Get recent platform activity log"""
    if current_user.get("user_type") != "admin" or not current_user.get("is_superadmin"):
        raise HTTPException(status_code=403, detail="Superadmin access required")
    
    activities = []
    
    if activity_type in [None, "exam"]:
        exams = await db.exam_attempts.find(
            {},
            {"_id": 0, "id": 1, "user_id": 1, "exam_type": 1, "score": 1, "created_at": 1}
        ).sort("created_at", -1).limit(limit // 2 if activity_type is None else limit).to_list(limit)
        
        for exam in exams:
            activities.append({
                "type": "exam",
                "description": f"Exam attempt: {exam.get('exam_type')}",
                "score": exam.get("score"),
                "user_id": exam.get("user_id"),
                "timestamp": exam.get("created_at")
            })
    
    if activity_type in [None, "ai"]:
        ai_logs = await db.ai_agent_history.find(
            {},
            {"_id": 0, "user_id": 1, "agent": 1, "created_at": 1}
        ).sort("created_at", -1).limit(limit // 2 if activity_type is None else limit).to_list(limit)
        
        for log in ai_logs:
            activities.append({
                "type": "ai",
                "description": f"AI interaction: {log.get('agent', 'tutor')}",
                "user_id": log.get("user_id"),
                "timestamp": log.get("created_at")
            })
    
    if activity_type in [None, "registration"]:
        week_ago = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()
        registrations = await db.users.find(
            {"created_at": {"$gte": week_ago}},
            {"_id": 0, "id": 1, "user_type": 1, "name": 1, "created_at": 1}
        ).sort("created_at", -1).limit(limit // 4 if activity_type is None else limit).to_list(limit)
        
        for reg in registrations:
            activities.append({
                "type": "registration",
                "description": f"New {reg.get('user_type')}: {reg.get('name')}",
                "user_id": reg.get("id"),
                "timestamp": reg.get("created_at")
            })
    
    # Sort by timestamp
    activities.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
    
    return {"activities": activities[:limit]}

@router.get("/revenue-report")
async def get_revenue_report(
    period: str = Query(default="month", enum=["week", "month", "year"]),
    current_user: dict = Depends(get_current_user)
):
    """Get revenue report for superadmin"""
    if current_user.get("user_type") != "admin" or not current_user.get("is_superadmin"):
        raise HTTPException(status_code=403, detail="Superadmin access required")
    
    # Calculate date range
    now = datetime.now(timezone.utc)
    if period == "week":
        start_date = (now - timedelta(days=7)).isoformat()
    elif period == "month":
        start_date = (now - timedelta(days=30)).isoformat()
    else:
        start_date = (now - timedelta(days=365)).isoformat()
    
    # Get credit purchases in period
    credit_purchases = await db.ai_credits.aggregate([
        {"$unwind": {"path": "$purchase_history", "preserveNullAndEmptyArrays": False}},
        {"$match": {"purchase_history.timestamp": {"$gte": start_date}}},
        {"$group": {
            "_id": None,
            "total_credits": {"$sum": "$purchase_history.credits"},
            "total_revenue": {"$sum": "$purchase_history.amount"},
            "purchase_count": {"$sum": 1}
        }}
    ]).to_list(1)
    
    # Get subscription data (if any)
    subscriptions = await db.subscriptions.count_documents({
        "status": "active",
        "created_at": {"$gte": start_date}
    })
    
    purchases = credit_purchases[0] if credit_purchases else {"total_credits": 0, "total_revenue": 0, "purchase_count": 0}
    
    return {
        "period": period,
        "start_date": start_date,
        "end_date": now.isoformat(),
        "credits": {
            "total_purchased": purchases.get("total_credits", 0),
            "total_revenue": purchases.get("total_revenue", 0),
            "purchase_count": purchases.get("purchase_count", 0)
        },
        "subscriptions": {
            "new_active": subscriptions
        },
        "summary": {
            "total_revenue": purchases.get("total_revenue", 0),
            "avg_revenue_per_purchase": round(purchases.get("total_revenue", 0) / max(purchases.get("purchase_count", 1), 1), 2)
        }
    }
