"""Alerts system for Superadmin Dashboard"""
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from datetime import datetime, timezone, timedelta
from typing import Optional, List
import uuid

from database import db
from utils.auth import get_current_user

router = APIRouter(prefix="/superadmin/alerts", tags=["Superadmin Alerts"])

class Alert(BaseModel):
    id: str
    alert_type: str  # low_credits, inactive_institution, milestone, revenue, error_rate
    severity: str  # critical, warning, info, success
    title: str
    description: str
    institution_id: Optional[str] = None
    institution_name: Optional[str] = None
    data: Optional[dict] = None
    created_at: str
    read: bool = False
    dismissed: bool = False

# Alert thresholds
THRESHOLDS = {
    "low_credits_percent": 20,  # Alert when < 20% credits remaining
    "inactive_days": 7,  # Alert after 7 days of inactivity
    "student_milestones": [50, 100, 250, 500, 1000],  # Celebrate these milestones
    "significant_purchase": 500,  # Credits purchase >= 500
    "error_rate_threshold": 30  # Alert if >30% exam failures
}

async def generate_alerts() -> List[dict]:
    """Generate current alerts based on platform data"""
    alerts = []
    now = datetime.now(timezone.utc)
    week_ago = (now - timedelta(days=THRESHOLDS["inactive_days"])).isoformat()
    
    # Get all institutions
    institutions = await db.users.find(
        {"user_type": "institution"},
        {"_id": 0, "id": 1, "institution_name": 1, "email": 1, "created_at": 1}
    ).to_list(1000)
    
    for inst in institutions:
        inst_id = inst["id"]
        inst_name = inst.get("institution_name", inst.get("email", "Unknown"))
        
        # Check 1: Low Credits Alert
        credits = await db.ai_credits.find_one({"user_id": inst_id}, {"_id": 0})
        if credits:
            total = credits.get("total_credits", 0)
            used = credits.get("used_credits", 0)
            remaining = total - used
            if total > 0:
                percent_remaining = (remaining / total) * 100
                if percent_remaining < THRESHOLDS["low_credits_percent"]:
                    alerts.append({
                        "id": f"low_credits_{inst_id}",
                        "alert_type": "low_credits",
                        "severity": "warning" if percent_remaining > 10 else "critical",
                        "title": "Créditos Bajos",
                        "description": f"{inst_name} tiene solo {remaining} créditos restantes ({percent_remaining:.0f}%)",
                        "institution_id": inst_id,
                        "institution_name": inst_name,
                        "data": {"remaining": remaining, "total": total, "percent": percent_remaining},
                        "created_at": now.isoformat(),
                        "read": False,
                        "dismissed": False
                    })
        
        # Check 2: Inactive Institution Alert
        recent_activity = await db.exam_attempts.count_documents({
            "institution_id": inst_id,
            "created_at": {"$gte": week_ago}
        })
        recent_ai = await db.ai_agent_history.count_documents({
            "institution_id": inst_id,
            "created_at": {"$gte": week_ago}
        })
        
        if recent_activity == 0 and recent_ai == 0:
            # Check if institution has students
            student_count = await db.users.count_documents({"institution_id": inst_id})
            if student_count > 0:
                alerts.append({
                    "id": f"inactive_{inst_id}",
                    "alert_type": "inactive_institution",
                    "severity": "warning",
                    "title": "Institución Inactiva",
                    "description": f"{inst_name} no ha tenido actividad en los últimos {THRESHOLDS['inactive_days']} días",
                    "institution_id": inst_id,
                    "institution_name": inst_name,
                    "data": {"days_inactive": THRESHOLDS["inactive_days"], "student_count": student_count},
                    "created_at": now.isoformat(),
                    "read": False,
                    "dismissed": False
                })
        
        # Check 3: Student Milestone Alert
        student_count = await db.users.count_documents({"institution_id": inst_id})
        for milestone in THRESHOLDS["student_milestones"]:
            if student_count >= milestone and student_count < milestone + 5:
                alerts.append({
                    "id": f"milestone_{inst_id}_{milestone}",
                    "alert_type": "milestone",
                    "severity": "success",
                    "title": "¡Nuevo Milestone!",
                    "description": f"🎉 {inst_name} alcanzó {milestone} estudiantes",
                    "institution_id": inst_id,
                    "institution_name": inst_name,
                    "data": {"milestone": milestone, "current_count": student_count},
                    "created_at": now.isoformat(),
                    "read": False,
                    "dismissed": False
                })
                break
        
        # Check 4: High Error Rate Alert
        total_exams = await db.exam_attempts.count_documents({"institution_id": inst_id})
        if total_exams >= 10:  # Only check if there's enough data
            low_scores = await db.exam_attempts.count_documents({
                "institution_id": inst_id,
                "score": {"$lt": 50}
            })
            error_rate = (low_scores / total_exams) * 100
            if error_rate > THRESHOLDS["error_rate_threshold"]:
                alerts.append({
                    "id": f"error_rate_{inst_id}",
                    "alert_type": "error_rate",
                    "severity": "warning",
                    "title": "Alta Tasa de Errores",
                    "description": f"{inst_name} tiene {error_rate:.0f}% de exámenes con score bajo (<50)",
                    "institution_id": inst_id,
                    "institution_name": inst_name,
                    "data": {"error_rate": error_rate, "total_exams": total_exams, "low_scores": low_scores},
                    "created_at": now.isoformat(),
                    "read": False,
                    "dismissed": False
                })
    
    # Check 5: Recent Large Purchases (Platform-wide)
    recent_purchases = await db.ai_credits.aggregate([
        {"$unwind": {"path": "$purchase_history", "preserveNullAndEmptyArrays": False}},
        {"$match": {"purchase_history.timestamp": {"$gte": week_ago}}},
        {"$match": {"purchase_history.credits": {"$gte": THRESHOLDS["significant_purchase"]}}},
        {"$lookup": {
            "from": "users",
            "localField": "user_id",
            "foreignField": "id",
            "as": "institution"
        }},
        {"$unwind": {"path": "$institution", "preserveNullAndEmptyArrays": True}},
        {"$project": {
            "user_id": 1,
            "credits": "$purchase_history.credits",
            "amount": "$purchase_history.amount",
            "timestamp": "$purchase_history.timestamp",
            "institution_name": "$institution.institution_name"
        }}
    ]).to_list(50)
    
    for purchase in recent_purchases:
        alerts.append({
            "id": f"revenue_{purchase.get('user_id')}_{purchase.get('timestamp')}",
            "alert_type": "revenue",
            "severity": "info",
            "title": "Compra Significativa",
            "description": f"💰 {purchase.get('institution_name', 'Institución')} compró {purchase.get('credits')} créditos",
            "institution_id": purchase.get("user_id"),
            "institution_name": purchase.get("institution_name"),
            "data": {"credits": purchase.get("credits"), "amount": purchase.get("amount")},
            "created_at": purchase.get("timestamp", now.isoformat()),
            "read": False,
            "dismissed": False
        })
    
    # Sort by severity and date
    severity_order = {"critical": 0, "warning": 1, "info": 2, "success": 3}
    alerts.sort(key=lambda x: (severity_order.get(x["severity"], 99), x["created_at"]), reverse=False)
    
    return alerts

@router.get("")
async def get_alerts(
    severity: Optional[str] = Query(default=None, enum=["critical", "warning", "info", "success"]),
    alert_type: Optional[str] = Query(default=None, enum=["low_credits", "inactive_institution", "milestone", "revenue", "error_rate"]),
    limit: int = Query(default=50, le=200),
    current_user: dict = Depends(get_current_user)
):
    """Get current platform alerts"""
    if current_user.get("user_type") != "admin" or not current_user.get("is_superadmin"):
        raise HTTPException(status_code=403, detail="Superadmin access required")
    
    alerts = await generate_alerts()
    
    # Filter by severity
    if severity:
        alerts = [a for a in alerts if a["severity"] == severity]
    
    # Filter by type
    if alert_type:
        alerts = [a for a in alerts if a["alert_type"] == alert_type]
    
    # Get dismissed alerts from DB
    dismissed = await db.superadmin_dismissed_alerts.find(
        {"superadmin_id": current_user["id"]},
        {"_id": 0, "alert_id": 1}
    ).to_list(1000)
    dismissed_ids = {d["alert_id"] for d in dismissed}
    
    # Mark dismissed alerts
    for alert in alerts:
        alert["dismissed"] = alert["id"] in dismissed_ids
    
    # Filter out dismissed unless specifically requested
    alerts = [a for a in alerts if not a["dismissed"]]
    
    return {
        "alerts": alerts[:limit],
        "total": len(alerts),
        "summary": {
            "critical": len([a for a in alerts if a["severity"] == "critical"]),
            "warning": len([a for a in alerts if a["severity"] == "warning"]),
            "info": len([a for a in alerts if a["severity"] == "info"]),
            "success": len([a for a in alerts if a["severity"] == "success"])
        }
    }

@router.post("/{alert_id}/dismiss")
async def dismiss_alert(
    alert_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Dismiss an alert"""
    if current_user.get("user_type") != "admin" or not current_user.get("is_superadmin"):
        raise HTTPException(status_code=403, detail="Superadmin access required")
    
    await db.superadmin_dismissed_alerts.update_one(
        {"superadmin_id": current_user["id"], "alert_id": alert_id},
        {
            "$set": {
                "dismissed_at": datetime.now(timezone.utc).isoformat()
            },
            "$setOnInsert": {
                "superadmin_id": current_user["id"],
                "alert_id": alert_id
            }
        },
        upsert=True
    )
    
    return {"success": True, "message": "Alert dismissed"}

@router.delete("/dismissed")
async def clear_dismissed_alerts(current_user: dict = Depends(get_current_user)):
    """Clear all dismissed alerts to show them again"""
    if current_user.get("user_type") != "admin" or not current_user.get("is_superadmin"):
        raise HTTPException(status_code=403, detail="Superadmin access required")
    
    result = await db.superadmin_dismissed_alerts.delete_many({"superadmin_id": current_user["id"]})
    
    return {"success": True, "cleared": result.deleted_count}

@router.get("/summary")
async def get_alerts_summary(current_user: dict = Depends(get_current_user)):
    """Get quick summary of alerts for dashboard badge"""
    if current_user.get("user_type") != "admin" or not current_user.get("is_superadmin"):
        raise HTTPException(status_code=403, detail="Superadmin access required")
    
    alerts = await generate_alerts()
    
    # Get dismissed
    dismissed = await db.superadmin_dismissed_alerts.find(
        {"superadmin_id": current_user["id"]},
        {"_id": 0, "alert_id": 1}
    ).to_list(1000)
    dismissed_ids = {d["alert_id"] for d in dismissed}
    
    # Filter out dismissed
    active_alerts = [a for a in alerts if a["id"] not in dismissed_ids]
    
    return {
        "total_active": len(active_alerts),
        "critical": len([a for a in active_alerts if a["severity"] == "critical"]),
        "warning": len([a for a in active_alerts if a["severity"] == "warning"]),
        "has_critical": any(a["severity"] == "critical" for a in active_alerts)
    }
