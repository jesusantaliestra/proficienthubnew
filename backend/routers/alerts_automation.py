"""
Automated Alerts Router - Configurable alert system for institutions
Monetizable feature: Institutions can enable/configure alerts for stale leads, 
student engagement, and other triggers. Charged per alert or subscription tier.
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone, timedelta
from enum import Enum
import uuid
import os

from motor.motor_asyncio import AsyncIOMotorClient

router = APIRouter(prefix="/alerts-automation", tags=["Automated Alerts"])

# Database connection
client = AsyncIOMotorClient(os.environ.get('MONGO_URL'))
db = client[os.environ.get('DB_NAME', 'proficienthub')]

# Auth utility
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt

JWT_SECRET = os.environ.get('JWT_SECRET', 'proficienthub-secret-key')
security = HTTPBearer(auto_error=False)

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if not credentials:
        raise HTTPException(status_code=401, detail="Authentication required")
    try:
        payload = jwt.decode(credentials.credentials, JWT_SECRET, algorithms=["HS256"])
        user = await db.users.find_one({"id": payload["user_id"]}, {"_id": 0})
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        return user
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

# ==================== PRICING TIERS ====================

ALERT_PRICING = {
    "free": {
        "name": "Gratis",
        "price_monthly": 0,
        "alerts_per_month": 10,
        "channels": ["email"],
        "alert_types": ["stale_lead"],
        "features": ["Basic email alerts", "10 alerts/month"]
    },
    "starter": {
        "name": "Starter",
        "price_monthly": 29,
        "alerts_per_month": 100,
        "channels": ["email", "webhook"],
        "alert_types": ["stale_lead", "student_inactive", "payment_due"],
        "features": ["Email + Webhook", "100 alerts/month", "Custom templates"]
    },
    "professional": {
        "name": "Professional",
        "price_monthly": 79,
        "alerts_per_month": 500,
        "channels": ["email", "webhook", "sms", "whatsapp"],
        "alert_types": ["stale_lead", "student_inactive", "payment_due", "exam_reminder", "goal_achieved"],
        "features": ["All channels", "500 alerts/month", "Priority support", "Custom schedules"]
    },
    "enterprise": {
        "name": "Enterprise",
        "price_monthly": 199,
        "alerts_per_month": -1,  # Unlimited
        "channels": ["email", "webhook", "sms", "whatsapp", "slack", "teams"],
        "alert_types": ["all"],
        "features": ["Unlimited alerts", "All channels", "API access", "Custom integrations", "SLA guarantee"]
    }
}

# ==================== MODELS ====================

class AlertChannel(str, Enum):
    EMAIL = "email"
    SMS = "sms"
    WHATSAPP = "whatsapp"
    WEBHOOK = "webhook"
    SLACK = "slack"
    TEAMS = "teams"

class AlertType(str, Enum):
    STALE_LEAD = "stale_lead"
    STUDENT_INACTIVE = "student_inactive"
    PAYMENT_DUE = "payment_due"
    EXAM_REMINDER = "exam_reminder"
    GOAL_ACHIEVED = "goal_achieved"
    CUSTOM = "custom"

class AlertRuleCreate(BaseModel):
    name: str
    alert_type: AlertType
    is_enabled: bool = True
    
    # Trigger conditions
    trigger_days: int = 7  # Days before trigger (e.g., 7 days stale)
    trigger_condition: str = "days_inactive"  # days_inactive, score_below, etc.
    trigger_value: Optional[float] = None
    
    # Channels
    channels: List[AlertChannel] = [AlertChannel.EMAIL]
    
    # Recipients
    recipient_type: str = "assigned_user"  # assigned_user, admin, custom_emails
    custom_emails: Optional[List[str]] = []
    
    # Message templates
    email_subject: Optional[str] = None
    email_body: Optional[str] = None
    sms_message: Optional[str] = None
    webhook_url: Optional[str] = None
    
    # Schedule
    check_frequency: str = "daily"  # hourly, daily, weekly
    quiet_hours_start: Optional[int] = None  # 0-23
    quiet_hours_end: Optional[int] = None

class AlertRuleUpdate(BaseModel):
    name: Optional[str] = None
    is_enabled: Optional[bool] = None
    trigger_days: Optional[int] = None
    trigger_condition: Optional[str] = None
    trigger_value: Optional[float] = None
    channels: Optional[List[AlertChannel]] = None
    recipient_type: Optional[str] = None
    custom_emails: Optional[List[str]] = None
    email_subject: Optional[str] = None
    email_body: Optional[str] = None
    sms_message: Optional[str] = None
    webhook_url: Optional[str] = None
    check_frequency: Optional[str] = None
    quiet_hours_start: Optional[int] = None
    quiet_hours_end: Optional[int] = None

class AlertSubscriptionUpdate(BaseModel):
    tier: str  # free, starter, professional, enterprise
    
class ChannelConfigUpdate(BaseModel):
    channel: AlertChannel
    config: Dict[str, Any]  # Channel-specific configuration

# ==================== SUBSCRIPTION MANAGEMENT ====================

@router.get("/pricing")
async def get_alert_pricing():
    """Get all available alert pricing tiers"""
    return {
        "tiers": ALERT_PRICING,
        "currency": "USD",
        "billing_cycle": "monthly"
    }

@router.get("/subscription")
async def get_alert_subscription(current_user: dict = Depends(get_current_user)):
    """Get institution's current alert subscription"""
    if current_user["user_type"] != "institution":
        raise HTTPException(status_code=403, detail="Only institutions can manage alert subscriptions")
    
    subscription = await db.alert_subscriptions.find_one(
        {"institution_id": current_user["id"]},
        {"_id": 0}
    )
    
    if not subscription:
        # Return default free tier
        subscription = {
            "institution_id": current_user["id"],
            "tier": "free",
            "tier_details": ALERT_PRICING["free"],
            "alerts_used_this_month": 0,
            "alerts_remaining": ALERT_PRICING["free"]["alerts_per_month"],
            "billing_cycle_start": datetime.now(timezone.utc).replace(day=1).isoformat(),
            "is_active": True
        }
    else:
        tier = subscription.get("tier", "free")
        tier_details = ALERT_PRICING.get(tier, ALERT_PRICING["free"])
        alerts_limit = tier_details["alerts_per_month"]
        alerts_used = subscription.get("alerts_used_this_month", 0)
        subscription["tier_details"] = tier_details
        subscription["alerts_remaining"] = "unlimited" if alerts_limit == -1 else max(0, alerts_limit - alerts_used)
    
    return subscription

@router.put("/subscription")
async def update_alert_subscription(
    update: AlertSubscriptionUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Upgrade or change alert subscription tier"""
    if current_user["user_type"] != "institution":
        raise HTTPException(status_code=403, detail="Only institutions can manage subscriptions")
    
    if update.tier not in ALERT_PRICING:
        raise HTTPException(status_code=400, detail="Invalid tier")
    
    tier_details = ALERT_PRICING[update.tier]
    
    subscription_doc = {
        "institution_id": current_user["id"],
        "tier": update.tier,
        "price_monthly": tier_details["price_monthly"],
        "alerts_per_month": tier_details["alerts_per_month"],
        "channels_available": tier_details["channels"],
        "alert_types_available": tier_details["alert_types"],
        "alerts_used_this_month": 0,
        "billing_cycle_start": datetime.now(timezone.utc).replace(day=1).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "is_active": True
    }
    
    await db.alert_subscriptions.update_one(
        {"institution_id": current_user["id"]},
        {"$set": subscription_doc},
        upsert=True
    )
    
    return {
        "message": f"Subscription updated to {tier_details['name']}",
        "tier": update.tier,
        "price": tier_details["price_monthly"],
        "features": tier_details["features"]
    }

# ==================== CHANNEL CONFIGURATION ====================

@router.get("/channels")
async def get_channel_configs(current_user: dict = Depends(get_current_user)):
    """Get all channel configurations for institution"""
    if current_user["user_type"] != "institution":
        raise HTTPException(status_code=403, detail="Access denied")
    
    configs = await db.alert_channel_configs.find(
        {"institution_id": current_user["id"]},
        {"_id": 0}
    ).to_list(20)
    
    # Get subscription to know available channels
    subscription = await db.alert_subscriptions.find_one(
        {"institution_id": current_user["id"]},
        {"_id": 0, "tier": 1}
    )
    tier = subscription.get("tier", "free") if subscription else "free"
    available_channels = ALERT_PRICING[tier]["channels"]
    
    return {
        "configs": configs,
        "available_channels": available_channels,
        "channel_info": {
            "email": {"name": "Email", "requires_config": False, "description": "Send alerts via email"},
            "sms": {"name": "SMS", "requires_config": True, "description": "Twilio SMS integration", "config_fields": ["twilio_sid", "twilio_token", "twilio_phone"]},
            "whatsapp": {"name": "WhatsApp", "requires_config": True, "description": "WhatsApp Business API", "config_fields": ["whatsapp_api_key", "whatsapp_phone_id"]},
            "webhook": {"name": "Webhook", "requires_config": True, "description": "Custom HTTP webhook", "config_fields": ["webhook_url", "webhook_secret"]},
            "slack": {"name": "Slack", "requires_config": True, "description": "Slack workspace integration", "config_fields": ["slack_webhook_url"]},
            "teams": {"name": "Microsoft Teams", "requires_config": True, "description": "Teams channel integration", "config_fields": ["teams_webhook_url"]}
        }
    }

@router.put("/channels/{channel}")
async def update_channel_config(
    channel: str,
    config: ChannelConfigUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Configure a specific alert channel"""
    if current_user["user_type"] != "institution":
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Check if channel is available in subscription
    subscription = await db.alert_subscriptions.find_one(
        {"institution_id": current_user["id"]},
        {"_id": 0, "tier": 1}
    )
    tier = subscription.get("tier", "free") if subscription else "free"
    available_channels = ALERT_PRICING[tier]["channels"]
    
    if channel not in available_channels:
        raise HTTPException(
            status_code=403, 
            detail=f"Channel '{channel}' not available in your subscription tier. Upgrade to access this channel."
        )
    
    config_doc = {
        "institution_id": current_user["id"],
        "channel": channel,
        "config": config.config,
        "is_configured": True,
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.alert_channel_configs.update_one(
        {"institution_id": current_user["id"], "channel": channel},
        {"$set": config_doc},
        upsert=True
    )
    
    return {"message": f"Channel '{channel}' configured successfully"}

@router.post("/channels/{channel}/test")
async def test_channel(
    channel: str,
    current_user: dict = Depends(get_current_user)
):
    """Send a test alert through a specific channel"""
    if current_user["user_type"] != "institution":
        raise HTTPException(status_code=403, detail="Access denied")
    
    config = await db.alert_channel_configs.find_one(
        {"institution_id": current_user["id"], "channel": channel},
        {"_id": 0}
    )
    
    if not config or not config.get("is_configured"):
        raise HTTPException(status_code=400, detail=f"Channel '{channel}' not configured")
    
    # Simulate sending test (in production, actually send)
    test_result = {
        "channel": channel,
        "status": "sent",
        "message": f"Test alert sent via {channel}",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    
    # Log test
    await db.alert_logs.insert_one({
        "id": str(uuid.uuid4()),
        "institution_id": current_user["id"],
        "type": "test",
        "channel": channel,
        "status": "sent",
        "created_at": datetime.now(timezone.utc).isoformat()
    })
    
    return test_result

# ==================== ALERT RULES CRUD ====================

@router.post("/rules")
async def create_alert_rule(
    rule: AlertRuleCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create a new alert rule"""
    if current_user["user_type"] != "institution":
        raise HTTPException(status_code=403, detail="Only institutions can create alert rules")
    
    # Check subscription allows this alert type and channels
    subscription = await db.alert_subscriptions.find_one(
        {"institution_id": current_user["id"]},
        {"_id": 0}
    )
    tier = subscription.get("tier", "free") if subscription else "free"
    tier_details = ALERT_PRICING[tier]
    
    # Validate alert type
    if tier_details["alert_types"] != ["all"] and rule.alert_type.value not in tier_details["alert_types"]:
        raise HTTPException(
            status_code=403,
            detail=f"Alert type '{rule.alert_type.value}' not available in {tier_details['name']} tier. Please upgrade."
        )
    
    # Validate channels
    for channel in rule.channels:
        if channel.value not in tier_details["channels"]:
            raise HTTPException(
                status_code=403,
                detail=f"Channel '{channel.value}' not available in {tier_details['name']} tier. Please upgrade."
            )
    
    rule_id = str(uuid.uuid4())
    rule_doc = {
        "id": rule_id,
        "institution_id": current_user["id"],
        **rule.dict(),
        "channels": [c.value for c in rule.channels],
        "alert_type": rule.alert_type.value,
        "alerts_sent": 0,
        "last_triggered": None,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.alert_rules.insert_one(rule_doc)
    rule_doc.pop("_id", None)
    
    return {"id": rule_id, "message": "Alert rule created", "rule": rule_doc}

@router.get("/rules")
async def get_alert_rules(current_user: dict = Depends(get_current_user)):
    """Get all alert rules for institution"""
    if current_user["user_type"] != "institution":
        raise HTTPException(status_code=403, detail="Access denied")
    
    rules = await db.alert_rules.find(
        {"institution_id": current_user["id"]},
        {"_id": 0}
    ).to_list(100)
    
    return {"rules": rules}

@router.get("/rules/{rule_id}")
async def get_alert_rule(rule_id: str, current_user: dict = Depends(get_current_user)):
    """Get a specific alert rule"""
    if current_user["user_type"] != "institution":
        raise HTTPException(status_code=403, detail="Access denied")
    
    rule = await db.alert_rules.find_one(
        {"id": rule_id, "institution_id": current_user["id"]},
        {"_id": 0}
    )
    
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    
    return rule

@router.put("/rules/{rule_id}")
async def update_alert_rule(
    rule_id: str,
    update: AlertRuleUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Update an alert rule"""
    if current_user["user_type"] != "institution":
        raise HTTPException(status_code=403, detail="Access denied")
    
    rule = await db.alert_rules.find_one(
        {"id": rule_id, "institution_id": current_user["id"]}
    )
    
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    
    update_dict = {k: v for k, v in update.dict().items() if v is not None}
    
    # Convert channels enum to strings if present
    if "channels" in update_dict:
        update_dict["channels"] = [c.value for c in update_dict["channels"]]
    
    update_dict["updated_at"] = datetime.now(timezone.utc).isoformat()
    
    await db.alert_rules.update_one(
        {"id": rule_id},
        {"$set": update_dict}
    )
    
    return {"message": "Rule updated"}

@router.delete("/rules/{rule_id}")
async def delete_alert_rule(rule_id: str, current_user: dict = Depends(get_current_user)):
    """Delete an alert rule"""
    if current_user["user_type"] != "institution":
        raise HTTPException(status_code=403, detail="Access denied")
    
    result = await db.alert_rules.delete_one(
        {"id": rule_id, "institution_id": current_user["id"]}
    )
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Rule not found")
    
    return {"message": "Rule deleted"}

# ==================== ALERT EXECUTION ====================

@router.post("/rules/{rule_id}/trigger")
async def manually_trigger_rule(
    rule_id: str,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user)
):
    """Manually trigger an alert rule (for testing)"""
    if current_user["user_type"] != "institution":
        raise HTTPException(status_code=403, detail="Access denied")
    
    rule = await db.alert_rules.find_one(
        {"id": rule_id, "institution_id": current_user["id"]},
        {"_id": 0}
    )
    
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    
    # Check alert quota
    subscription = await db.alert_subscriptions.find_one(
        {"institution_id": current_user["id"]},
        {"_id": 0}
    )
    tier = subscription.get("tier", "free") if subscription else "free"
    alerts_limit = ALERT_PRICING[tier]["alerts_per_month"]
    alerts_used = subscription.get("alerts_used_this_month", 0) if subscription else 0
    
    if alerts_limit != -1 and alerts_used >= alerts_limit:
        raise HTTPException(
            status_code=429,
            detail=f"Monthly alert limit reached ({alerts_used}/{alerts_limit}). Please upgrade your subscription."
        )
    
    # Log alert
    alert_log = {
        "id": str(uuid.uuid4()),
        "institution_id": current_user["id"],
        "rule_id": rule_id,
        "rule_name": rule["name"],
        "alert_type": rule["alert_type"],
        "channels": rule["channels"],
        "status": "sent",
        "triggered_by": "manual",
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.alert_logs.insert_one(alert_log)
    
    # Increment usage
    await db.alert_subscriptions.update_one(
        {"institution_id": current_user["id"]},
        {"$inc": {"alerts_used_this_month": 1}},
        upsert=True
    )
    
    # Update rule stats
    await db.alert_rules.update_one(
        {"id": rule_id},
        {
            "$inc": {"alerts_sent": 1},
            "$set": {"last_triggered": datetime.now(timezone.utc).isoformat()}
        }
    )
    
    return {
        "message": "Alert triggered",
        "alert_id": alert_log["id"],
        "channels": rule["channels"]
    }

# ==================== ALERT LOGS & ANALYTICS ====================

@router.get("/logs")
async def get_alert_logs(
    limit: int = 50,
    alert_type: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """Get alert history/logs"""
    if current_user["user_type"] != "institution":
        raise HTTPException(status_code=403, detail="Access denied")
    
    query = {"institution_id": current_user["id"]}
    if alert_type:
        query["alert_type"] = alert_type
    
    logs = await db.alert_logs.find(
        query,
        {"_id": 0}
    ).sort("created_at", -1).limit(limit).to_list(limit)
    
    return {"logs": logs}

@router.get("/analytics")
async def get_alert_analytics(current_user: dict = Depends(get_current_user)):
    """Get alert usage analytics"""
    if current_user["user_type"] != "institution":
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Get subscription info
    subscription = await db.alert_subscriptions.find_one(
        {"institution_id": current_user["id"]},
        {"_id": 0}
    )
    tier = subscription.get("tier", "free") if subscription else "free"
    tier_details = ALERT_PRICING[tier]
    alerts_used = subscription.get("alerts_used_this_month", 0) if subscription else 0
    alerts_limit = tier_details["alerts_per_month"]
    
    # Get logs for analytics
    logs = await db.alert_logs.find(
        {"institution_id": current_user["id"]}
    ).to_list(1000)
    
    # Analytics by type
    by_type = {}
    by_channel = {}
    for log in logs:
        t = log.get("alert_type", "unknown")
        by_type[t] = by_type.get(t, 0) + 1
        
        for ch in log.get("channels", []):
            by_channel[ch] = by_channel.get(ch, 0) + 1
    
    # Get active rules count
    rules_count = await db.alert_rules.count_documents(
        {"institution_id": current_user["id"], "is_enabled": True}
    )
    
    return {
        "subscription": {
            "tier": tier,
            "tier_name": tier_details["name"],
            "price": tier_details["price_monthly"],
            "alerts_used": alerts_used,
            "alerts_limit": "unlimited" if alerts_limit == -1 else alerts_limit,
            "alerts_remaining": "unlimited" if alerts_limit == -1 else max(0, alerts_limit - alerts_used),
            "usage_percentage": 0 if alerts_limit == -1 else round(alerts_used / alerts_limit * 100, 1)
        },
        "stats": {
            "total_alerts_sent": len(logs),
            "active_rules": rules_count,
            "by_type": by_type,
            "by_channel": by_channel
        },
        "recommendations": get_upgrade_recommendations(tier, alerts_used, alerts_limit)
    }

def get_upgrade_recommendations(tier: str, used: int, limit: int) -> List[str]:
    """Generate upgrade recommendations based on usage"""
    recommendations = []
    
    if limit != -1:
        usage_pct = used / limit * 100 if limit > 0 else 0
        
        if usage_pct >= 80:
            recommendations.append(f"You've used {usage_pct:.0f}% of your monthly alerts. Consider upgrading to avoid interruptions.")
        
        if tier == "free":
            recommendations.append("Upgrade to Starter for SMS, Webhook alerts and 100 alerts/month.")
        elif tier == "starter":
            recommendations.append("Upgrade to Professional for WhatsApp, custom schedules and 500 alerts/month.")
        elif tier == "professional":
            recommendations.append("Upgrade to Enterprise for unlimited alerts and Slack/Teams integration.")
    
    return recommendations

# ==================== STALE LEAD CHECKER ====================

@router.get("/check-stale-leads")
async def check_stale_leads(current_user: dict = Depends(get_current_user)):
    """Check for stale leads that would trigger alerts"""
    if current_user["user_type"] != "institution":
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Get stale lead rules
    rules = await db.alert_rules.find({
        "institution_id": current_user["id"],
        "alert_type": "stale_lead",
        "is_enabled": True
    }).to_list(20)
    
    if not rules:
        return {"message": "No stale lead rules configured", "stale_leads": []}
    
    # Get all leads
    leads = await db.crm_leads.find({
        "$or": [
            {"created_by": current_user["id"]},
            {"assigned_to": current_user["id"]}
        ],
        "stage": {"$nin": ["won", "lost"]}
    }).to_list(1000)
    
    stale_leads = []
    now = datetime.now(timezone.utc)
    
    for lead in leads:
        updated = lead.get("updated_at", lead.get("created_at", ""))
        if updated:
            try:
                updated_dt = datetime.fromisoformat(updated.replace("Z", "+00:00"))
                days_stale = (now - updated_dt).days
                
                for rule in rules:
                    if days_stale >= rule.get("trigger_days", 7):
                        stale_leads.append({
                            "lead_id": lead["id"],
                            "lead_name": lead.get("institution_name", ""),
                            "stage": lead.get("stage", ""),
                            "days_stale": days_stale,
                            "rule_name": rule["name"],
                            "would_trigger": True
                        })
                        break
            except:
                pass
    
    return {
        "rules_active": len(rules),
        "stale_leads_count": len(stale_leads),
        "stale_leads": stale_leads[:20]
    }

# ==================== DEFAULT TEMPLATES ====================

@router.get("/templates")
async def get_alert_templates():
    """Get default alert message templates"""
    return {
        "templates": {
            "stale_lead": {
                "email_subject": "⚠️ Lead Estancado: {{lead_name}}",
                "email_body": """
                <h2>Alerta de Lead Estancado</h2>
                <p>El lead <strong>{{lead_name}}</strong> lleva <strong>{{days_stale}} días</strong> sin actividad.</p>
                <p><strong>Etapa actual:</strong> {{stage}}</p>
                <p><strong>Último contacto:</strong> {{last_contact}}</p>
                <p><a href="{{crm_url}}">Ver en CRM</a></p>
                """,
                "sms_message": "⚠️ Lead {{lead_name}} estancado por {{days_stale}} días. Etapa: {{stage}}",
                "variables": ["lead_name", "days_stale", "stage", "last_contact", "crm_url"]
            },
            "student_inactive": {
                "email_subject": "📚 Estudiante Inactivo: {{student_name}}",
                "email_body": """
                <h2>Alerta de Estudiante Inactivo</h2>
                <p>El estudiante <strong>{{student_name}}</strong> no ha realizado actividad en <strong>{{days_inactive}} días</strong>.</p>
                <p><strong>Último examen:</strong> {{last_exam}}</p>
                <p><strong>Progreso:</strong> {{progress}}%</p>
                """,
                "sms_message": "📚 {{student_name}} inactivo por {{days_inactive}} días. Considere contactarlo.",
                "variables": ["student_name", "days_inactive", "last_exam", "progress"]
            },
            "payment_due": {
                "email_subject": "💰 Pago Pendiente - {{institution_name}}",
                "email_body": """
                <h2>Recordatorio de Pago</h2>
                <p>Tiene un pago pendiente de <strong>{{amount}}</strong>.</p>
                <p><strong>Fecha límite:</strong> {{due_date}}</p>
                <p><a href="{{payment_url}}">Realizar Pago</a></p>
                """,
                "sms_message": "💰 Pago pendiente: {{amount}}. Vence: {{due_date}}",
                "variables": ["institution_name", "amount", "due_date", "payment_url"]
            }
        }
    }
