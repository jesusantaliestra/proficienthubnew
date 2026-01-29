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
