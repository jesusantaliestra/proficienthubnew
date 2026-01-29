"""
Community Router - Forums, Study Groups, and Social Features
Enables peer-to-peer learning and community engagement
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timezone
import uuid

router = APIRouter(prefix="/community", tags=["Community"])

import sys
sys.path.append('/app/backend')
from motor.motor_asyncio import AsyncIOMotorClient
import os

client = AsyncIOMotorClient(os.environ.get('MONGO_URL'))
db = client[os.environ.get('DB_NAME', 'proficienthub')]

from server import get_current_user

# ==================== MODELS ====================

class ForumPostCreate(BaseModel):
    title: str
    content: str
    category: str  # general, exam_tips, study_partners, resources, questions
    exam_type: Optional[str] = None
    tags: List[str] = []

class ForumReplyCreate(BaseModel):
    content: str

class StudyGroupCreate(BaseModel):
    name: str
    description: Optional[str] = None
    exam_type: str
    target_date: Optional[str] = None  # Target exam date
    max_members: int = 20
    is_private: bool = False

# ==================== FORUM CATEGORIES ====================

FORUM_CATEGORIES = [
    {"id": "general", "name": "General Discussion", "icon": "MessageSquare", "color": "#6366f1"},
    {"id": "exam_tips", "name": "Exam Tips & Strategies", "icon": "Target", "color": "#22c55e"},
    {"id": "study_partners", "name": "Find Study Partners", "icon": "Users", "color": "#f59e0b"},
    {"id": "resources", "name": "Study Resources", "icon": "BookOpen", "color": "#3b82f6"},
    {"id": "questions", "name": "Q&A", "icon": "HelpCircle", "color": "#ec4899"},
    {"id": "success_stories", "name": "Success Stories", "icon": "Trophy", "color": "#eab308"}
]

@router.get("/forum/categories")
async def get_forum_categories():
    """Get forum categories"""
    return {"categories": FORUM_CATEGORIES}

# ==================== FORUM POSTS ====================

@router.post("/forum/posts")
async def create_forum_post(
    post: ForumPostCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create a new forum post"""
    post_id = str(uuid.uuid4())
    
    post_doc = {
        "id": post_id,
        "author_id": current_user["id"],
        "author_name": current_user.get("name", "Anonymous"),
        "author_type": current_user.get("user_type"),
        "institution_id": current_user.get("institution_id") or current_user["id"],
        "title": post.title,
        "content": post.content,
        "category": post.category,
        "exam_type": post.exam_type,
        "tags": post.tags,
        "views": 0,
        "likes": 0,
        "liked_by": [],
        "reply_count": 0,
        "is_pinned": False,
        "is_solved": False,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.forum_posts.insert_one(post_doc)
    
    # Award community points if gamification enabled
    institution_id = current_user.get("institution_id") or current_user["id"]
    await award_community_points(current_user["id"], institution_id, "post")
    
    return {"id": post_id, "message": "Post created successfully"}

@router.get("/forum/posts")
async def list_forum_posts(
    category: Optional[str] = None,
    exam_type: Optional[str] = None,
    search: Optional[str] = None,
    sort_by: str = "created_at",  # created_at, likes, views, reply_count
    page: int = 1,
    per_page: int = 20,
    current_user: dict = Depends(get_current_user)
):
    """List forum posts"""
    institution_id = current_user.get("institution_id") or current_user["id"]
    
    query = {"institution_id": institution_id}
    
    if category:
        query["category"] = category
    if exam_type:
        query["exam_type"] = exam_type
    if search:
        query["$or"] = [
            {"title": {"$regex": search, "$options": "i"}},
            {"content": {"$regex": search, "$options": "i"}},
            {"tags": {"$in": [search.lower()]}}
        ]
    
    skip = (page - 1) * per_page
    sort_dir = -1
    
    # Pinned posts first
    posts = await db.forum_posts.find(
        query, {"_id": 0}
    ).sort([("is_pinned", -1), (sort_by, sort_dir)]).skip(skip).limit(per_page).to_list(per_page)
    
    total = await db.forum_posts.count_documents(query)
    
    return {
        "posts": posts,
        "total": total,
        "page": page,
        "per_page": per_page
    }

@router.get("/forum/posts/{post_id}")
async def get_forum_post(
    post_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get a forum post with replies"""
    post = await db.forum_posts.find_one({"id": post_id}, {"_id": 0})
    
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    # Increment views
    await db.forum_posts.update_one(
        {"id": post_id},
        {"$inc": {"views": 1}}
    )
    
    # Get replies
    replies = await db.forum_replies.find(
        {"post_id": post_id},
        {"_id": 0}
    ).sort("created_at", 1).to_list(100)
    
    post["replies"] = replies
    post["user_has_liked"] = current_user["id"] in post.get("liked_by", [])
    
    return post

@router.post("/forum/posts/{post_id}/like")
async def like_forum_post(
    post_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Like/unlike a forum post"""
    post = await db.forum_posts.find_one({"id": post_id})
    
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    liked_by = post.get("liked_by", [])
    
    if current_user["id"] in liked_by:
        # Unlike
        await db.forum_posts.update_one(
            {"id": post_id},
            {
                "$pull": {"liked_by": current_user["id"]},
                "$inc": {"likes": -1}
            }
        )
        return {"action": "unliked", "likes": post["likes"] - 1}
    else:
        # Like
        await db.forum_posts.update_one(
            {"id": post_id},
            {
                "$push": {"liked_by": current_user["id"]},
                "$inc": {"likes": 1}
            }
        )
        return {"action": "liked", "likes": post["likes"] + 1}

@router.post("/forum/posts/{post_id}/reply")
async def reply_to_post(
    post_id: str,
    reply: ForumReplyCreate,
    current_user: dict = Depends(get_current_user)
):
    """Reply to a forum post"""
    post = await db.forum_posts.find_one({"id": post_id})
    
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    reply_id = str(uuid.uuid4())
    
    reply_doc = {
        "id": reply_id,
        "post_id": post_id,
        "author_id": current_user["id"],
        "author_name": current_user.get("name", "Anonymous"),
        "author_type": current_user.get("user_type"),
        "content": reply.content,
        "likes": 0,
        "liked_by": [],
        "is_solution": False,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.forum_replies.insert_one(reply_doc)
    
    # Update reply count
    await db.forum_posts.update_one(
        {"id": post_id},
        {"$inc": {"reply_count": 1}}
    )
    
    # Award community points if gamification enabled
    institution_id = current_user.get("institution_id") or current_user["id"]
    await award_community_points(current_user["id"], institution_id, "reply")
    
    return {"id": reply_id, "message": "Reply posted"}

@router.post("/forum/posts/{post_id}/solve/{reply_id}")
async def mark_solution(
    post_id: str,
    reply_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Mark a reply as the solution (post author only)"""
    post = await db.forum_posts.find_one({"id": post_id})
    
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    if post["author_id"] != current_user["id"]:
        raise HTTPException(status_code=403, detail="Only post author can mark solution")
    
    # Unmark any previous solution
    await db.forum_replies.update_many(
        {"post_id": post_id},
        {"$set": {"is_solution": False}}
    )
    
    # Mark new solution
    await db.forum_replies.update_one(
        {"id": reply_id},
        {"$set": {"is_solution": True}}
    )
    
    # Mark post as solved
    await db.forum_posts.update_one(
        {"id": post_id},
        {"$set": {"is_solved": True}}
    )
    
    # Award solution points to reply author
    reply = await db.forum_replies.find_one({"id": reply_id})
    if reply:
        institution_id = current_user.get("institution_id") or current_user["id"]
        await award_community_points(reply["author_id"], institution_id, "solution")
    
    return {"message": "Solution marked"}

# ==================== STUDY GROUPS ====================

@router.post("/groups")
async def create_study_group(
    group: StudyGroupCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create a study group"""
    group_id = str(uuid.uuid4())
    
    group_doc = {
        "id": group_id,
        "creator_id": current_user["id"],
        "institution_id": current_user.get("institution_id") or current_user["id"],
        "name": group.name,
        "description": group.description,
        "exam_type": group.exam_type,
        "target_date": group.target_date,
        "max_members": group.max_members,
        "is_private": group.is_private,
        "member_count": 1,
        "members": [current_user["id"]],
        "admins": [current_user["id"]],
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.study_groups.insert_one(group_doc)
    
    return {"id": group_id, "message": "Study group created"}

@router.get("/groups")
async def list_study_groups(
    exam_type: Optional[str] = None,
    search: Optional[str] = None,
    my_groups: bool = False,
    page: int = 1,
    per_page: int = 20,
    current_user: dict = Depends(get_current_user)
):
    """List study groups"""
    institution_id = current_user.get("institution_id") or current_user["id"]
    
    query = {"institution_id": institution_id}
    
    if my_groups:
        query["members"] = current_user["id"]
    else:
        query["is_private"] = False
    
    if exam_type:
        query["exam_type"] = exam_type
    if search:
        query["name"] = {"$regex": search, "$options": "i"}
    
    skip = (page - 1) * per_page
    
    groups = await db.study_groups.find(
        query, {"_id": 0}
    ).sort("created_at", -1).skip(skip).limit(per_page).to_list(per_page)
    
    # Add membership status
    for group in groups:
        group["is_member"] = current_user["id"] in group.get("members", [])
        group["is_admin"] = current_user["id"] in group.get("admins", [])
    
    total = await db.study_groups.count_documents(query)
    
    return {
        "groups": groups,
        "total": total,
        "page": page,
        "per_page": per_page
    }

@router.get("/groups/{group_id}")
async def get_study_group(
    group_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get study group details"""
    group = await db.study_groups.find_one({"id": group_id}, {"_id": 0})
    
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    
    # Check access for private groups
    if group.get("is_private") and current_user["id"] not in group.get("members", []):
        raise HTTPException(status_code=403, detail="This is a private group")
    
    # Get member details
    member_ids = group.get("members", [])
    members = await db.users.find(
        {"id": {"$in": member_ids}},
        {"_id": 0, "id": 1, "name": 1, "avatar": 1}
    ).to_list(100)
    
    group["member_details"] = members
    group["is_member"] = current_user["id"] in member_ids
    group["is_admin"] = current_user["id"] in group.get("admins", [])
    
    # Get recent messages
    messages = await db.group_messages.find(
        {"group_id": group_id},
        {"_id": 0}
    ).sort("created_at", -1).limit(50).to_list(50)
    
    group["recent_messages"] = list(reversed(messages))
    
    return group

@router.post("/groups/{group_id}/join")
async def join_study_group(
    group_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Join a study group"""
    group = await db.study_groups.find_one({"id": group_id})
    
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    
    if current_user["id"] in group.get("members", []):
        raise HTTPException(status_code=400, detail="Already a member")
    
    if group.get("member_count", 0) >= group.get("max_members", 20):
        raise HTTPException(status_code=400, detail="Group is full")
    
    if group.get("is_private"):
        raise HTTPException(status_code=403, detail="This is a private group. Request an invite.")
    
    await db.study_groups.update_one(
        {"id": group_id},
        {
            "$push": {"members": current_user["id"]},
            "$inc": {"member_count": 1}
        }
    )
    
    return {"message": "Joined group successfully"}

@router.post("/groups/{group_id}/leave")
async def leave_study_group(
    group_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Leave a study group"""
    group = await db.study_groups.find_one({"id": group_id})
    
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    
    if current_user["id"] not in group.get("members", []):
        raise HTTPException(status_code=400, detail="Not a member")
    
    if current_user["id"] == group.get("creator_id"):
        raise HTTPException(status_code=400, detail="Creator cannot leave. Transfer ownership or delete group.")
    
    await db.study_groups.update_one(
        {"id": group_id},
        {
            "$pull": {"members": current_user["id"], "admins": current_user["id"]},
            "$inc": {"member_count": -1}
        }
    )
    
    return {"message": "Left group"}

@router.post("/groups/{group_id}/message")
async def send_group_message(
    group_id: str,
    content: str,
    current_user: dict = Depends(get_current_user)
):
    """Send a message to a study group"""
    group = await db.study_groups.find_one({"id": group_id})
    
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    
    if current_user["id"] not in group.get("members", []):
        raise HTTPException(status_code=403, detail="Not a member of this group")
    
    message_id = str(uuid.uuid4())
    
    message_doc = {
        "id": message_id,
        "group_id": group_id,
        "author_id": current_user["id"],
        "author_name": current_user.get("name", "Anonymous"),
        "content": content,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.group_messages.insert_one(message_doc)
    
    return {"id": message_id, "message": "Message sent"}

# ==================== COMMUNITY STATS ====================

@router.get("/stats")
async def get_community_stats(current_user: dict = Depends(get_current_user)):
    """Get community statistics"""
    institution_id = current_user.get("institution_id") or current_user["id"]
    
    total_posts = await db.forum_posts.count_documents({"institution_id": institution_id})
    total_replies = await db.forum_replies.count_documents({})
    total_groups = await db.study_groups.count_documents({"institution_id": institution_id})
    
    # Active contributors this week
    from datetime import timedelta
    week_ago = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()
    
    active_users = await db.forum_posts.distinct(
        "author_id",
        {"institution_id": institution_id, "created_at": {"$gte": week_ago}}
    )
    
    return {
        "total_posts": total_posts,
        "total_replies": total_replies,
        "total_groups": total_groups,
        "active_contributors_this_week": len(active_users)
    }


# ==================== COMMUNITY GAMIFICATION ====================

class CommunityGamificationConfig(BaseModel):
    community_gamification_enabled: bool = False
    points_per_post: int = 10
    points_per_reply: int = 5
    points_per_solution: int = 50  # When reply is marked as solution
    points_per_like_received: int = 2
    points_per_group_created: int = 25
    points_per_group_joined: int = 5
    show_contributor_leaderboard: bool = True
    show_reputation_badges: bool = True
    weekly_top_contributor_reward: int = 100  # Bonus XP for top contributor

# Community Badges
COMMUNITY_BADGES = [
    {"id": "first_post", "name": "First Steps", "description": "Created your first forum post", "icon": "MessageSquare", "requirement": 1, "type": "posts"},
    {"id": "helpful_10", "name": "Helpful Member", "description": "Had 10 replies marked as solutions", "icon": "CheckCircle", "requirement": 10, "type": "solutions"},
    {"id": "popular_post", "name": "Trending", "description": "Got 50 likes on a single post", "icon": "TrendingUp", "requirement": 50, "type": "single_post_likes"},
    {"id": "community_star", "name": "Community Star", "description": "Earned 500 community reputation", "icon": "Star", "requirement": 500, "type": "reputation"},
    {"id": "group_leader", "name": "Group Leader", "description": "Created a study group with 10+ members", "icon": "Users", "requirement": 10, "type": "group_size"},
    {"id": "mentor", "name": "Mentor", "description": "Had 50 replies marked as solutions", "icon": "Award", "requirement": 50, "type": "solutions"},
    {"id": "influencer", "name": "Influencer", "description": "Earned 2000 community reputation", "icon": "Crown", "requirement": 2000, "type": "reputation"},
]

@router.get("/gamification/config")
async def get_community_gamification_config(current_user: dict = Depends(get_current_user)):
    """Get community gamification configuration for institution"""
    institution_id = current_user.get("institution_id") or current_user["id"]
    
    config = await db.community_gamification_config.find_one(
        {"institution_id": institution_id},
        {"_id": 0}
    )
    
    if not config:
        # Return default config
        config = {
            "institution_id": institution_id,
            "community_gamification_enabled": False,
            "points_per_post": 10,
            "points_per_reply": 5,
            "points_per_solution": 50,
            "points_per_like_received": 2,
            "points_per_group_created": 25,
            "points_per_group_joined": 5,
            "show_contributor_leaderboard": True,
            "show_reputation_badges": True,
            "weekly_top_contributor_reward": 100
        }
    
    return {"config": config, "badges": COMMUNITY_BADGES}

@router.put("/gamification/config")
async def update_community_gamification_config(
    config: CommunityGamificationConfig,
    current_user: dict = Depends(get_current_user)
):
    """Update community gamification configuration (institution admins only)"""
    if current_user["user_type"] != "institution":
        raise HTTPException(status_code=403, detail="Only institutions can configure community gamification")
    
    config_doc = {
        "institution_id": current_user["id"],
        **config.dict(),
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.community_gamification_config.update_one(
        {"institution_id": current_user["id"]},
        {"$set": config_doc},
        upsert=True
    )
    
    return {"message": "Community gamification settings updated"}

@router.get("/gamification/profile")
async def get_community_profile(current_user: dict = Depends(get_current_user)):
    """Get user's community gamification profile"""
    institution_id = current_user.get("institution_id") or current_user["id"]
    
    # Check if gamification is enabled
    config = await db.community_gamification_config.find_one(
        {"institution_id": institution_id},
        {"_id": 0, "community_gamification_enabled": 1}
    )
    
    if not config or not config.get("community_gamification_enabled"):
        return {"enabled": False}
    
    # Get or create profile
    profile = await db.community_profiles.find_one(
        {"user_id": current_user["id"]},
        {"_id": 0}
    )
    
    if not profile:
        profile = {
            "user_id": current_user["id"],
            "institution_id": institution_id,
            "reputation": 0,
            "posts_count": 0,
            "replies_count": 0,
            "solutions_count": 0,
            "likes_received": 0,
            "groups_created": 0,
            "groups_joined": 0,
            "badges": [],
            "rank": "Newcomer",
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        await db.community_profiles.insert_one(profile)
        profile.pop("_id", None)
    
    # Calculate rank based on reputation
    rep = profile.get("reputation", 0)
    if rep >= 2000:
        profile["rank"] = "Legend"
    elif rep >= 1000:
        profile["rank"] = "Expert"
    elif rep >= 500:
        profile["rank"] = "Pro"
    elif rep >= 100:
        profile["rank"] = "Regular"
    else:
        profile["rank"] = "Newcomer"
    
    return {"enabled": True, "profile": profile}

@router.get("/gamification/leaderboard")
async def get_community_leaderboard(
    period: str = "all_time",  # all_time, weekly, monthly
    limit: int = 10,
    current_user: dict = Depends(get_current_user)
):
    """Get community contributor leaderboard"""
    institution_id = current_user.get("institution_id") or current_user["id"]
    
    # Check if gamification is enabled
    config = await db.community_gamification_config.find_one(
        {"institution_id": institution_id},
        {"_id": 0}
    )
    
    if not config or not config.get("community_gamification_enabled"):
        return {"enabled": False, "leaderboard": []}
    
    if not config.get("show_contributor_leaderboard"):
        return {"enabled": True, "leaderboard": [], "hidden": True}
    
    # Get top contributors
    leaderboard = await db.community_profiles.find(
        {"institution_id": institution_id},
        {"_id": 0, "user_id": 1, "reputation": 1, "posts_count": 1, "solutions_count": 1, "rank": 1}
    ).sort("reputation", -1).limit(limit).to_list(limit)
    
    # Add user names
    for i, entry in enumerate(leaderboard):
        user = await db.users.find_one(
            {"id": entry["user_id"]},
            {"_id": 0, "name": 1}
        )
        entry["name"] = user.get("name", "Anonymous") if user else "Anonymous"
        entry["position"] = i + 1
        entry["is_current_user"] = entry["user_id"] == current_user["id"]
    
    return {"enabled": True, "leaderboard": leaderboard}

@router.get("/gamification/badges")
async def get_available_badges():
    """Get all available community badges"""
    return {"badges": COMMUNITY_BADGES}

async def award_community_points(user_id: str, institution_id: str, action: str, amount: int = None):
    """Helper function to award community points"""
    # Get config
    config = await db.community_gamification_config.find_one(
        {"institution_id": institution_id}
    )
    
    if not config or not config.get("community_gamification_enabled"):
        return
    
    # Determine points based on action
    if amount is None:
        points_map = {
            "post": config.get("points_per_post", 10),
            "reply": config.get("points_per_reply", 5),
            "solution": config.get("points_per_solution", 50),
            "like_received": config.get("points_per_like_received", 2),
            "group_created": config.get("points_per_group_created", 25),
            "group_joined": config.get("points_per_group_joined", 5),
        }
        amount = points_map.get(action, 0)
    
    if amount <= 0:
        return
    
    # Update profile
    update_fields = {"$inc": {"reputation": amount}}
    
    if action == "post":
        update_fields["$inc"]["posts_count"] = 1
    elif action == "reply":
        update_fields["$inc"]["replies_count"] = 1
    elif action == "solution":
        update_fields["$inc"]["solutions_count"] = 1
    elif action == "like_received":
        update_fields["$inc"]["likes_received"] = 1
    elif action == "group_created":
        update_fields["$inc"]["groups_created"] = 1
    elif action == "group_joined":
        update_fields["$inc"]["groups_joined"] = 1
    
    await db.community_profiles.update_one(
        {"user_id": user_id},
        update_fields,
        upsert=True
    )
    
    # Check for badge awards
    await check_community_badges(user_id, institution_id)

async def check_community_badges(user_id: str, institution_id: str):
    """Check and award community badges"""
    profile = await db.community_profiles.find_one({"user_id": user_id})
    if not profile:
        return
    
    earned_badges = profile.get("badges", [])
    new_badges = []
    
    for badge in COMMUNITY_BADGES:
        if badge["id"] in earned_badges:
            continue
        
        earned = False
        if badge["type"] == "posts" and profile.get("posts_count", 0) >= badge["requirement"]:
            earned = True
        elif badge["type"] == "solutions" and profile.get("solutions_count", 0) >= badge["requirement"]:
            earned = True
        elif badge["type"] == "reputation" and profile.get("reputation", 0) >= badge["requirement"]:
            earned = True
        
        if earned:
            new_badges.append(badge["id"])
    
    if new_badges:
        await db.community_profiles.update_one(
            {"user_id": user_id},
            {"$addToSet": {"badges": {"$each": new_badges}}}
        )

