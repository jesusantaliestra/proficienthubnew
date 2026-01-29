"""
Gamification Router - Leaderboards, Badges, Achievements
Implements game mechanics to increase student engagement
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone, timedelta
import uuid

router = APIRouter(prefix="/gamification", tags=["Gamification"])

# Import shared dependencies
import sys
sys.path.append('/app/backend')
from motor.motor_asyncio import AsyncIOMotorClient
import os

client = AsyncIOMotorClient(os.environ.get('MONGO_URL'))
db = client[os.environ.get('DB_NAME', 'proficienthub')]

# Auth dependency - import from main server
from server import get_current_user

# ==================== BADGE DEFINITIONS ====================

BADGE_DEFINITIONS = {
    # Progress Badges
    "first_exam": {
        "id": "first_exam",
        "name": "First Steps",
        "description": "Complete your first practice exam",
        "icon": "Award",
        "category": "progress",
        "points": 10,
        "rarity": "common"
    },
    "ten_exams": {
        "id": "ten_exams",
        "name": "Dedicated Learner",
        "description": "Complete 10 practice exams",
        "icon": "Target",
        "category": "progress",
        "points": 50,
        "rarity": "uncommon"
    },
    "fifty_exams": {
        "id": "fifty_exams",
        "name": "Exam Master",
        "description": "Complete 50 practice exams",
        "icon": "Crown",
        "category": "progress",
        "points": 200,
        "rarity": "rare"
    },
    "hundred_exams": {
        "id": "hundred_exams",
        "name": "Exam Legend",
        "description": "Complete 100 practice exams",
        "icon": "Trophy",
        "category": "progress",
        "points": 500,
        "rarity": "legendary"
    },
    
    # Score Badges
    "perfect_reading": {
        "id": "perfect_reading",
        "name": "Reading Prodigy",
        "description": "Score 100% on a reading section",
        "icon": "BookOpen",
        "category": "achievement",
        "points": 100,
        "rarity": "rare"
    },
    "perfect_listening": {
        "id": "perfect_listening",
        "name": "Listening Ace",
        "description": "Score 100% on a listening section",
        "icon": "Headphones",
        "category": "achievement",
        "points": 100,
        "rarity": "rare"
    },
    "band_7": {
        "id": "band_7",
        "name": "Band 7 Achiever",
        "description": "Achieve IELTS Band 7 or equivalent",
        "icon": "Star",
        "category": "achievement",
        "points": 150,
        "rarity": "uncommon"
    },
    "band_8": {
        "id": "band_8",
        "name": "Band 8 Expert",
        "description": "Achieve IELTS Band 8 or equivalent",
        "icon": "Medal",
        "category": "achievement",
        "points": 300,
        "rarity": "rare"
    },
    "band_9": {
        "id": "band_9",
        "name": "Band 9 Master",
        "description": "Achieve IELTS Band 9 - Perfect Score!",
        "icon": "Crown",
        "category": "achievement",
        "points": 1000,
        "rarity": "legendary"
    },
    
    # Streak Badges
    "week_streak": {
        "id": "week_streak",
        "name": "Weekly Warrior",
        "description": "Study 7 days in a row",
        "icon": "Flame",
        "category": "streak",
        "points": 75,
        "rarity": "uncommon"
    },
    "month_streak": {
        "id": "month_streak",
        "name": "Monthly Champion",
        "description": "Study 30 days in a row",
        "icon": "Zap",
        "category": "streak",
        "points": 300,
        "rarity": "rare"
    },
    
    # Skill Badges
    "writing_expert": {
        "id": "writing_expert",
        "name": "Writing Expert",
        "description": "Complete 20 writing exercises with 7+ score",
        "icon": "Edit",
        "category": "skill",
        "points": 200,
        "rarity": "rare"
    },
    "speaking_fluent": {
        "id": "speaking_fluent",
        "name": "Fluent Speaker",
        "description": "Complete 20 speaking exercises with 7+ score",
        "icon": "Mic",
        "category": "skill",
        "points": 200,
        "rarity": "rare"
    },
    
    # Social Badges
    "helpful_peer": {
        "id": "helpful_peer",
        "name": "Helpful Peer",
        "description": "Help 10 fellow students in forums",
        "icon": "Users",
        "category": "social",
        "points": 100,
        "rarity": "uncommon"
    },
    "top_contributor": {
        "id": "top_contributor",
        "name": "Top Contributor",
        "description": "Reach top 10 on monthly leaderboard",
        "icon": "TrendingUp",
        "category": "social",
        "points": 250,
        "rarity": "rare"
    }
}

# ==================== LEADERBOARD ====================

@router.get("/leaderboard")
async def get_leaderboard(
    timeframe: str = "weekly",  # daily, weekly, monthly, all_time
    exam_type: Optional[str] = None,
    limit: int = 50,
    current_user: dict = Depends(get_current_user)
):
    """Get leaderboard rankings"""
    institution_id = current_user.get("institution_id") or current_user["id"]
    
    # Determine date range
    now = datetime.now(timezone.utc)
    if timeframe == "daily":
        start_date = (now - timedelta(days=1)).isoformat()
    elif timeframe == "weekly":
        start_date = (now - timedelta(days=7)).isoformat()
    elif timeframe == "monthly":
        start_date = (now - timedelta(days=30)).isoformat()
    else:
        start_date = None
    
    # Build query
    match_query = {"institution_id": institution_id}
    if start_date:
        match_query["updated_at"] = {"$gte": start_date}
    if exam_type:
        match_query["exam_type"] = exam_type
    
    # Aggregate points
    pipeline = [
        {"$match": match_query},
        {"$group": {
            "_id": "$user_id",
            "total_points": {"$sum": "$points"},
            "exams_completed": {"$sum": 1},
            "avg_score": {"$avg": "$score"}
        }},
        {"$sort": {"total_points": -1}},
        {"$limit": limit}
    ]
    
    rankings = await db.student_progress.aggregate(pipeline).to_list(limit)
    
    # Enrich with user data
    leaderboard = []
    for i, rank in enumerate(rankings):
        user = await db.users.find_one(
            {"id": rank["_id"]},
            {"_id": 0, "name": 1, "avatar": 1}
        )
        
        leaderboard.append({
            "rank": i + 1,
            "user_id": rank["_id"],
            "name": user.get("name", "Student") if user else "Student",
            "avatar": user.get("avatar") if user else None,
            "points": rank["total_points"],
            "exams_completed": rank["exams_completed"],
            "avg_score": round(rank.get("avg_score") or 0, 1),
            "is_current_user": rank["_id"] == current_user["id"]
        })
    
    # Get current user's rank if not in top
    current_user_rank = None
    if not any(r["is_current_user"] for r in leaderboard):
        # Find user's rank
        user_stats = await db.student_progress.aggregate([
            {"$match": {**match_query, "user_id": current_user["id"]}},
            {"$group": {
                "_id": "$user_id",
                "total_points": {"$sum": "$points"}
            }}
        ]).to_list(1)
        
        if user_stats:
            points = user_stats[0]["total_points"]
            higher_count = await db.student_progress.aggregate([
                {"$match": match_query},
                {"$group": {"_id": "$user_id", "total_points": {"$sum": "$points"}}},
                {"$match": {"total_points": {"$gt": points}}},
                {"$count": "count"}
            ]).to_list(1)
            
            current_user_rank = {
                "rank": (higher_count[0]["count"] if higher_count else 0) + 1,
                "points": points
            }
    
    return {
        "leaderboard": leaderboard,
        "timeframe": timeframe,
        "current_user_rank": current_user_rank
    }

# ==================== BADGES ====================

@router.get("/badges")
async def get_available_badges():
    """Get all available badges"""
    badges_by_category = {}
    
    for badge in BADGE_DEFINITIONS.values():
        category = badge["category"]
        if category not in badges_by_category:
            badges_by_category[category] = []
        badges_by_category[category].append(badge)
    
    return {
        "badges": list(BADGE_DEFINITIONS.values()),
        "by_category": badges_by_category
    }

@router.get("/badges/my")
async def get_my_badges(current_user: dict = Depends(get_current_user)):
    """Get badges earned by current user"""
    user_badges = await db.user_badges.find(
        {"user_id": current_user["id"]},
        {"_id": 0}
    ).to_list(100)
    
    # Enrich with badge definitions
    earned_badges = []
    for ub in user_badges:
        badge_def = BADGE_DEFINITIONS.get(ub["badge_id"])
        if badge_def:
            earned_badges.append({
                **badge_def,
                "earned_at": ub["earned_at"],
                "progress": 100
            })
    
    # Calculate progress for unearned badges
    in_progress = []
    earned_ids = {b["id"] for b in earned_badges}
    
    for badge_id, badge in BADGE_DEFINITIONS.items():
        if badge_id not in earned_ids:
            progress = await calculate_badge_progress(current_user["id"], badge_id)
            if progress > 0:
                in_progress.append({
                    **badge,
                    "progress": progress
                })
    
    # Total points
    total_points = sum(b["points"] for b in earned_badges)
    
    return {
        "earned": earned_badges,
        "in_progress": sorted(in_progress, key=lambda x: -x["progress"])[:5],
        "total_badges": len(earned_badges),
        "total_points": total_points
    }

@router.post("/badges/check")
async def check_and_award_badges(current_user: dict = Depends(get_current_user)):
    """Check for new badges to award based on user's activity"""
    user_id = current_user["id"]
    newly_earned = []
    
    # Get user's current badges
    existing = await db.user_badges.find(
        {"user_id": user_id},
        {"badge_id": 1, "_id": 0}
    ).to_list(100)
    existing_ids = {b["badge_id"] for b in existing}
    
    # Check each badge
    for badge_id, badge in BADGE_DEFINITIONS.items():
        if badge_id in existing_ids:
            continue
        
        earned = await check_badge_criteria(user_id, badge_id)
        
        if earned:
            await db.user_badges.insert_one({
                "id": str(uuid.uuid4()),
                "user_id": user_id,
                "badge_id": badge_id,
                "earned_at": datetime.now(timezone.utc).isoformat()
            })
            newly_earned.append(badge)
    
    return {
        "newly_earned": newly_earned,
        "points_earned": sum(b["points"] for b in newly_earned)
    }

# ==================== STREAKS ====================

@router.get("/streak")
async def get_streak(current_user: dict = Depends(get_current_user)):
    """Get user's current study streak"""
    user_id = current_user["id"]
    
    streak_data = await db.user_streaks.find_one(
        {"user_id": user_id},
        {"_id": 0}
    )
    
    if not streak_data:
        return {
            "current_streak": 0,
            "longest_streak": 0,
            "last_activity": None,
            "streak_frozen": False
        }
    
    # Check if streak is still valid (activity within last 24-48 hours)
    last_activity = streak_data.get("last_activity")
    if last_activity:
        last_date = datetime.fromisoformat(last_activity.replace('Z', '+00:00'))
        hours_since = (datetime.now(timezone.utc) - last_date).total_seconds() / 3600
        
        if hours_since > 48:  # Streak broken
            await db.user_streaks.update_one(
                {"user_id": user_id},
                {"$set": {"current_streak": 0}}
            )
            streak_data["current_streak"] = 0
    
    return {
        "current_streak": streak_data.get("current_streak", 0),
        "longest_streak": streak_data.get("longest_streak", 0),
        "last_activity": streak_data.get("last_activity"),
        "streak_frozen": streak_data.get("streak_frozen", False)
    }

@router.post("/streak/activity")
async def record_activity(current_user: dict = Depends(get_current_user)):
    """Record daily activity to maintain/extend streak"""
    user_id = current_user["id"]
    now = datetime.now(timezone.utc)
    today = now.date().isoformat()
    
    streak_data = await db.user_streaks.find_one({"user_id": user_id})
    
    if not streak_data:
        # First activity
        await db.user_streaks.insert_one({
            "user_id": user_id,
            "current_streak": 1,
            "longest_streak": 1,
            "last_activity": now.isoformat(),
            "last_activity_date": today,
            "streak_frozen": False
        })
        return {"current_streak": 1, "message": "Streak started!"}
    
    last_date = streak_data.get("last_activity_date")
    
    if last_date == today:
        # Already recorded today
        return {
            "current_streak": streak_data["current_streak"],
            "message": "Activity already recorded today"
        }
    
    # Check if continuing streak
    if last_date:
        last = datetime.fromisoformat(last_date)
        today_date = datetime.fromisoformat(today)
        days_diff = (today_date - last).days
        
        if days_diff == 1:
            # Continue streak
            new_streak = streak_data["current_streak"] + 1
            longest = max(new_streak, streak_data.get("longest_streak", 0))
        elif days_diff > 1:
            # Streak broken
            new_streak = 1
            longest = streak_data.get("longest_streak", 0)
        else:
            new_streak = streak_data["current_streak"]
            longest = streak_data.get("longest_streak", 0)
    else:
        new_streak = 1
        longest = 1
    
    await db.user_streaks.update_one(
        {"user_id": user_id},
        {"$set": {
            "current_streak": new_streak,
            "longest_streak": longest,
            "last_activity": now.isoformat(),
            "last_activity_date": today
        }}
    )
    
    return {
        "current_streak": new_streak,
        "longest_streak": longest,
        "message": f"Streak: {new_streak} days!"
    }

# ==================== POINTS ====================

@router.get("/points")
async def get_points(current_user: dict = Depends(get_current_user)):
    """Get user's total points breakdown"""
    user_id = current_user["id"]
    
    # Points from badges
    badges = await db.user_badges.find(
        {"user_id": user_id},
        {"badge_id": 1, "_id": 0}
    ).to_list(100)
    
    badge_points = sum(
        BADGE_DEFINITIONS.get(b["badge_id"], {}).get("points", 0)
        for b in badges
    )
    
    # Points from activities
    activity_points = await db.student_progress.aggregate([
        {"$match": {"user_id": user_id}},
        {"$group": {"_id": None, "total": {"$sum": "$points"}}}
    ]).to_list(1)
    
    activity_total = activity_points[0]["total"] if activity_points else 0
    
    return {
        "total_points": badge_points + activity_total,
        "badge_points": badge_points,
        "activity_points": activity_total,
        "badges_earned": len(badges)
    }

# ==================== HELPER FUNCTIONS ====================

async def calculate_badge_progress(user_id: str, badge_id: str) -> int:
    """Calculate progress towards a badge (0-100)"""
    if badge_id == "first_exam":
        count = await db.exam_attempts.count_documents({"user_id": user_id, "status": "completed"})
        return 100 if count >= 1 else 0
    
    elif badge_id == "ten_exams":
        count = await db.exam_attempts.count_documents({"user_id": user_id, "status": "completed"})
        return min(100, count * 10)
    
    elif badge_id == "fifty_exams":
        count = await db.exam_attempts.count_documents({"user_id": user_id, "status": "completed"})
        return min(100, count * 2)
    
    elif badge_id == "week_streak":
        streak = await db.user_streaks.find_one({"user_id": user_id})
        if streak:
            return min(100, (streak.get("current_streak", 0) / 7) * 100)
    
    return 0

async def check_badge_criteria(user_id: str, badge_id: str) -> bool:
    """Check if user has met criteria for a badge"""
    if badge_id == "first_exam":
        count = await db.exam_attempts.count_documents({"user_id": user_id, "status": "completed"})
        return count >= 1
    
    elif badge_id == "ten_exams":
        count = await db.exam_attempts.count_documents({"user_id": user_id, "status": "completed"})
        return count >= 10
    
    elif badge_id == "fifty_exams":
        count = await db.exam_attempts.count_documents({"user_id": user_id, "status": "completed"})
        return count >= 50
    
    elif badge_id == "hundred_exams":
        count = await db.exam_attempts.count_documents({"user_id": user_id, "status": "completed"})
        return count >= 100
    
    elif badge_id == "week_streak":
        streak = await db.user_streaks.find_one({"user_id": user_id})
        return streak and streak.get("current_streak", 0) >= 7
    
    elif badge_id == "month_streak":
        streak = await db.user_streaks.find_one({"user_id": user_id})
        return streak and streak.get("current_streak", 0) >= 30
    
    elif badge_id in ["perfect_reading", "perfect_listening"]:
        skill = "reading" if badge_id == "perfect_reading" else "listening"
        perfect = await db.exam_attempts.find_one({
            "user_id": user_id,
            "skill": skill,
            "score": 100,
            "status": "completed"
        })
        return perfect is not None
    
    return False
