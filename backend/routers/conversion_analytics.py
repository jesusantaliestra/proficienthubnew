"""Conversion Analytics Router - Funnel tracking and metrics"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone, timedelta
import uuid

from database import db
from utils.auth import get_current_user

router = APIRouter(prefix="/conversion-analytics", tags=["Conversion Analytics"])

# Funnel stages
FUNNEL_STAGES = [
    "landing_visit",
    "chat_widget_opened",
    "chat_interaction",
    "demo_requested",
    "demo_activated",
    "demo_engaged",      # Used features
    "pricing_viewed",
    "checkout_started",
    "payment_completed",
    "converted_to_customer"
]

# Models
class FunnelEvent(BaseModel):
    stage: str
    session_id: Optional[str] = None
    demo_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class ConversionGoal(BaseModel):
    name: str
    description: Optional[str] = None
    target_stage: str
    target_count: int = 100
    period_days: int = 30

@router.post("/track")
async def track_funnel_event(event: FunnelEvent):
    """Track a conversion funnel event (public endpoint)"""
    
    if event.stage not in FUNNEL_STAGES:
        raise HTTPException(status_code=400, detail=f"Invalid stage. Valid: {FUNNEL_STAGES}")
    
    event_doc = {
        "id": str(uuid.uuid4()),
        "stage": event.stage,
        "session_id": event.session_id,
        "demo_id": event.demo_id,
        "metadata": event.metadata or {},
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.conversion_funnel.insert_one(event_doc)
    
    return {"success": True, "event_id": event_doc["id"]}

@router.get("/funnel")
async def get_funnel_metrics(
    days: int = 30,
    current_user: dict = Depends(get_current_user)
):
    """Get conversion funnel metrics (admin only)"""
    
    if current_user.get("user_type") != "admin":
        raise HTTPException(status_code=403, detail="Access denied")
    
    cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
    
    # Count events per stage
    pipeline = [
        {"$match": {"created_at": {"$gte": cutoff}}},
        {"$group": {"_id": "$stage", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ]
    
    stage_counts = await db.conversion_funnel.aggregate(pipeline).to_list(20)
    
    # Build funnel data with conversion rates
    funnel_data = []
    total_visits = 0
    
    for stage in FUNNEL_STAGES:
        stage_data = next((s for s in stage_counts if s["_id"] == stage), {"_id": stage, "count": 0})
        count = stage_data["count"]
        
        if stage == "landing_visit":
            total_visits = count
        
        conversion_rate = (count / total_visits * 100) if total_visits > 0 else 0
        
        funnel_data.append({
            "stage": stage,
            "count": count,
            "conversion_rate": round(conversion_rate, 2),
            "label": stage.replace("_", " ").title()
        })
    
    # Calculate stage-to-stage conversion rates
    for i, stage in enumerate(funnel_data[1:], 1):
        prev_count = funnel_data[i-1]["count"]
        if prev_count > 0:
            stage["step_conversion"] = round(stage["count"] / prev_count * 100, 2)
        else:
            stage["step_conversion"] = 0
    
    if funnel_data:
        funnel_data[0]["step_conversion"] = 100
    
    return {
        "period_days": days,
        "total_visits": total_visits,
        "funnel": funnel_data,
        "overall_conversion": round(
            funnel_data[-1]["count"] / total_visits * 100 if total_visits > 0 else 0, 2
        )
    }

@router.get("/trends")
async def get_conversion_trends(
    days: int = 30,
    current_user: dict = Depends(get_current_user)
):
    """Get daily conversion trends (admin only)"""
    
    if current_user.get("user_type") != "admin":
        raise HTTPException(status_code=403, detail="Access denied")
    
    cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
    
    # Daily aggregation
    pipeline = [
        {"$match": {"created_at": {"$gte": cutoff}}},
        {"$addFields": {
            "date": {"$substr": ["$created_at", 0, 10]}
        }},
        {"$group": {
            "_id": {"date": "$date", "stage": "$stage"},
            "count": {"$sum": 1}
        }},
        {"$sort": {"_id.date": 1}}
    ]
    
    daily_data = await db.conversion_funnel.aggregate(pipeline).to_list(1000)
    
    # Organize by date
    trends = {}
    for item in daily_data:
        date = item["_id"]["date"]
        stage = item["_id"]["stage"]
        
        if date not in trends:
            trends[date] = {"date": date}
            for s in FUNNEL_STAGES:
                trends[date][s] = 0
        
        trends[date][stage] = item["count"]
    
    # Convert to list sorted by date
    trend_list = sorted(trends.values(), key=lambda x: x["date"])
    
    return {
        "period_days": days,
        "trends": trend_list,
        "stages": FUNNEL_STAGES
    }

@router.get("/demo-analytics")
async def get_demo_analytics(
    days: int = 30,
    current_user: dict = Depends(get_current_user)
):
    """Get demo-specific analytics (admin only)"""
    
    if current_user.get("user_type") != "admin":
        raise HTTPException(status_code=403, detail="Access denied")
    
    cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
    
    # Demo stats
    total_demos = await db.demo_requests.count_documents({"created_at": {"$gte": cutoff}})
    active_demos = await db.demo_requests.count_documents({
        "status": "active",
        "expires_at": {"$gte": datetime.now(timezone.utc).isoformat()}
    })
    converted_demos = await db.demo_requests.count_documents({
        "created_at": {"$gte": cutoff},
        "conversion_status": "customer"
    })
    expired_demos = await db.demo_requests.count_documents({
        "created_at": {"$gte": cutoff},
        "status": "active",
        "expires_at": {"$lt": datetime.now(timezone.utc).isoformat()}
    })
    
    # Average demo engagement
    engagement_pipeline = [
        {"$match": {"demo_id": {"$exists": True}, "created_at": {"$gte": cutoff}}},
        {"$group": {"_id": "$demo_id", "events": {"$sum": 1}}},
        {"$group": {"_id": None, "avg_events": {"$avg": "$events"}}}
    ]
    engagement = await db.conversion_funnel.aggregate(engagement_pipeline).to_list(1)
    avg_engagement = engagement[0]["avg_events"] if engagement else 0
    
    # Conversion rate
    conversion_rate = (converted_demos / total_demos * 100) if total_demos > 0 else 0
    
    return {
        "period_days": days,
        "total_demos": total_demos,
        "active_demos": active_demos,
        "converted_demos": converted_demos,
        "expired_demos": expired_demos,
        "conversion_rate": round(conversion_rate, 2),
        "avg_engagement_events": round(avg_engagement, 1),
        "metrics": {
            "demo_to_conversion": f"{conversion_rate:.1f}%",
            "active_rate": f"{(active_demos / total_demos * 100) if total_demos > 0 else 0:.1f}%"
        }
    }

@router.get("/chat-widget-metrics")
async def get_chat_widget_metrics(
    days: int = 30,
    current_user: dict = Depends(get_current_user)
):
    """Get landing chat widget metrics (admin only)"""
    
    if current_user.get("user_type") != "admin":
        raise HTTPException(status_code=403, detail="Access denied")
    
    cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
    
    # Chat widget events
    chat_opened = await db.conversion_funnel.count_documents({
        "stage": "chat_widget_opened",
        "created_at": {"$gte": cutoff}
    })
    
    chat_interacted = await db.conversion_funnel.count_documents({
        "stage": "chat_interaction",
        "created_at": {"$gte": cutoff}
    })
    
    # Messages from landing agent logs
    total_messages = await db.landing_agent_logs.count_documents({
        "created_at": {"$gte": cutoff}
    })
    
    # Unique sessions
    sessions_pipeline = [
        {"$match": {"created_at": {"$gte": cutoff}}},
        {"$group": {"_id": "$session_id"}},
        {"$count": "total"}
    ]
    unique_sessions = await db.landing_agent_logs.aggregate(sessions_pipeline).to_list(1)
    session_count = unique_sessions[0]["total"] if unique_sessions else 0
    
    # Messages per session
    msgs_per_session = total_messages / session_count if session_count > 0 else 0
    
    return {
        "period_days": days,
        "chat_opened": chat_opened,
        "chat_interacted": chat_interacted,
        "total_messages": total_messages,
        "unique_sessions": session_count,
        "avg_messages_per_session": round(msgs_per_session, 2),
        "engagement_rate": round(
            chat_interacted / chat_opened * 100 if chat_opened > 0 else 0, 2
        )
    }

@router.get("/revenue-attribution")
async def get_revenue_attribution(
    days: int = 30,
    current_user: dict = Depends(get_current_user)
):
    """Get revenue attribution by conversion source (admin only)"""
    
    if current_user.get("user_type") != "admin":
        raise HTTPException(status_code=403, detail="Access denied")
    
    cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
    
    # Get converted demos with revenue
    pipeline = [
        {"$match": {
            "conversion_status": "customer",
            "created_at": {"$gte": cutoff}
        }},
        {"$lookup": {
            "from": "orders",
            "localField": "contact_email",
            "foreignField": "customer_email",
            "as": "orders"
        }},
        {"$unwind": {"path": "$orders", "preserveNullAndEmptyArrays": True}},
        {"$group": {
            "_id": None,
            "total_revenue": {"$sum": "$orders.amount"},
            "converted_count": {"$sum": 1}
        }}
    ]
    
    attribution = await db.demo_requests.aggregate(pipeline).to_list(1)
    
    return {
        "period_days": days,
        "from_demo": {
            "revenue": attribution[0]["total_revenue"] if attribution else 0,
            "conversions": attribution[0]["converted_count"] if attribution else 0
        },
        "attribution_note": "Revenue from customers who started as demos"
    }
