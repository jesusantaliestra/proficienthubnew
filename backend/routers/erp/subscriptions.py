"""
ERP Premium Module - Subscriptions & MRR/ARR Tracking
Subscription management with revenue recognition
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone, timedelta
from dateutil.relativedelta import relativedelta
import uuid

import sys
sys.path.append('/app/backend')
from database import db
from utils.auth import get_current_user
from .config import SUPPORTED_CURRENCIES

router = APIRouter(prefix="/erp/subscriptions", tags=["ERP - Subscriptions"])

# ==================== MODELS ====================

class SubscriptionPlanCreate(BaseModel):
    name: str
    description: Optional[str] = None
    billing_cycle: str  # monthly, quarterly, annually
    price: float
    currency: str = "USD"
    features: List[str] = []
    limits: Optional[Dict[str, int]] = None  # e.g., {"students": 100, "ai_credits": 500}
    is_active: bool = True

class SubscriptionCreate(BaseModel):
    customer_id: str
    plan_id: str
    start_date: Optional[str] = None
    trial_days: int = 0
    discount_percent: float = 0
    metadata: Optional[Dict[str, Any]] = None

class SubscriptionUpdate(BaseModel):
    plan_id: Optional[str] = None
    discount_percent: Optional[float] = None
    cancel_at_period_end: Optional[bool] = None

# ==================== HELPER FUNCTIONS ====================

def calculate_next_billing_date(start_date: datetime, billing_cycle: str, periods: int = 1) -> datetime:
    """Calculate next billing date based on cycle"""
    if billing_cycle == "monthly":
        return start_date + relativedelta(months=periods)
    elif billing_cycle == "quarterly":
        return start_date + relativedelta(months=3 * periods)
    elif billing_cycle == "annually":
        return start_date + relativedelta(years=periods)
    return start_date

def calculate_mrr(price: float, billing_cycle: str) -> float:
    """Convert any billing cycle to MRR"""
    if billing_cycle == "monthly":
        return price
    elif billing_cycle == "quarterly":
        return price / 3
    elif billing_cycle == "annually":
        return price / 12
    return price

# ==================== SUBSCRIPTION PLANS ====================

@router.post("/plans")
async def create_subscription_plan(
    plan: SubscriptionPlanCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create a subscription plan"""
    if current_user["user_type"] not in ["admin"]:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    plan_id = str(uuid.uuid4())
    
    plan_doc = {
        "id": plan_id,
        **plan.dict(),
        "mrr_value": calculate_mrr(plan.price, plan.billing_cycle),
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.erp_subscription_plans.insert_one(plan_doc)
    
    return {"id": plan_id, "message": "Plan created"}

@router.get("/plans")
async def list_subscription_plans(
    is_active: Optional[bool] = None,
    current_user: dict = Depends(get_current_user)
):
    """List all subscription plans"""
    query = {}
    if is_active is not None:
        query["is_active"] = is_active
    
    plans = await db.erp_subscription_plans.find(query, {"_id": 0}).to_list(100)
    
    return {"plans": plans}

# ==================== SUBSCRIPTIONS ====================

@router.post("")
async def create_subscription(
    sub_data: SubscriptionCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create a new subscription for a customer"""
    if current_user["user_type"] not in ["institution", "admin"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Get plan details
    plan = await db.erp_subscription_plans.find_one({"id": sub_data.plan_id}, {"_id": 0})
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    
    # Get customer
    customer = await db.users.find_one({"id": sub_data.customer_id}, {"_id": 0})
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    sub_id = str(uuid.uuid4())
    start_date = datetime.fromisoformat(sub_data.start_date) if sub_data.start_date else datetime.now(timezone.utc)
    
    # Calculate dates
    if sub_data.trial_days > 0:
        trial_end = start_date + timedelta(days=sub_data.trial_days)
        billing_start = trial_end
    else:
        trial_end = None
        billing_start = start_date
    
    next_billing = calculate_next_billing_date(billing_start, plan["billing_cycle"])
    
    # Calculate effective price
    effective_price = plan["price"] * (1 - sub_data.discount_percent / 100)
    effective_mrr = calculate_mrr(effective_price, plan["billing_cycle"])
    
    sub_doc = {
        "id": sub_id,
        "institution_id": current_user["id"],
        "customer_id": sub_data.customer_id,
        "customer_name": customer.get("institution_name", customer.get("name", "")),
        "plan_id": sub_data.plan_id,
        "plan_name": plan["name"],
        "billing_cycle": plan["billing_cycle"],
        "price": effective_price,
        "currency": plan["currency"],
        "mrr": effective_mrr,
        "discount_percent": sub_data.discount_percent,
        "status": "trialing" if sub_data.trial_days > 0 else "active",
        "start_date": start_date.isoformat(),
        "trial_end_date": trial_end.isoformat() if trial_end else None,
        "current_period_start": billing_start.isoformat(),
        "current_period_end": next_billing.isoformat(),
        "next_billing_date": next_billing.isoformat(),
        "cancel_at_period_end": False,
        "canceled_at": None,
        "metadata": sub_data.metadata,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.erp_subscriptions.insert_one(sub_doc)
    
    return {
        "id": sub_id,
        "status": sub_doc["status"],
        "mrr": effective_mrr,
        "next_billing_date": next_billing.isoformat()
    }

@router.get("")
async def list_subscriptions(
    status: Optional[str] = None,
    customer_id: Optional[str] = None,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    current_user: dict = Depends(get_current_user)
):
    """List subscriptions"""
    query = {"institution_id": current_user["id"]}
    
    if status:
        query["status"] = status
    if customer_id:
        query["customer_id"] = customer_id
    
    total = await db.erp_subscriptions.count_documents(query)
    skip = (page - 1) * per_page
    
    subscriptions = await db.erp_subscriptions.find(
        query,
        {"_id": 0}
    ).sort("created_at", -1).skip(skip).limit(per_page).to_list(per_page)
    
    return {
        "subscriptions": subscriptions,
        "total": total,
        "page": page,
        "per_page": per_page
    }

@router.get("/{subscription_id}")
async def get_subscription(
    subscription_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get subscription details"""
    sub = await db.erp_subscriptions.find_one(
        {"id": subscription_id, "institution_id": current_user["id"]},
        {"_id": 0}
    )
    
    if not sub:
        raise HTTPException(status_code=404, detail="Subscription not found")
    
    return sub

@router.patch("/{subscription_id}")
async def update_subscription(
    subscription_id: str,
    update_data: SubscriptionUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Update subscription (change plan, cancel, etc.)"""
    sub = await db.erp_subscriptions.find_one(
        {"id": subscription_id, "institution_id": current_user["id"]},
        {"_id": 0}
    )
    
    if not sub:
        raise HTTPException(status_code=404, detail="Subscription not found")
    
    update_dict = {}
    
    if update_data.plan_id:
        # Get new plan
        new_plan = await db.erp_subscription_plans.find_one({"id": update_data.plan_id}, {"_id": 0})
        if not new_plan:
            raise HTTPException(status_code=404, detail="Plan not found")
        
        discount = update_data.discount_percent if update_data.discount_percent is not None else sub.get("discount_percent", 0)
        effective_price = new_plan["price"] * (1 - discount / 100)
        
        update_dict.update({
            "plan_id": new_plan["id"],
            "plan_name": new_plan["name"],
            "billing_cycle": new_plan["billing_cycle"],
            "price": effective_price,
            "mrr": calculate_mrr(effective_price, new_plan["billing_cycle"]),
            "plan_changed_at": datetime.now(timezone.utc).isoformat()
        })
    
    if update_data.discount_percent is not None:
        update_dict["discount_percent"] = update_data.discount_percent
        # Recalculate price if not changing plan
        if not update_data.plan_id:
            plan = await db.erp_subscription_plans.find_one({"id": sub["plan_id"]}, {"_id": 0})
            effective_price = plan["price"] * (1 - update_data.discount_percent / 100)
            update_dict["price"] = effective_price
            update_dict["mrr"] = calculate_mrr(effective_price, plan["billing_cycle"])
    
    if update_data.cancel_at_period_end is not None:
        update_dict["cancel_at_period_end"] = update_data.cancel_at_period_end
        if update_data.cancel_at_period_end:
            update_dict["canceled_at"] = datetime.now(timezone.utc).isoformat()
    
    if update_dict:
        update_dict["updated_at"] = datetime.now(timezone.utc).isoformat()
        await db.erp_subscriptions.update_one(
            {"id": subscription_id},
            {"$set": update_dict}
        )
    
    return {"message": "Subscription updated"}

@router.post("/{subscription_id}/cancel")
async def cancel_subscription(
    subscription_id: str,
    immediate: bool = False,
    reason: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """Cancel a subscription"""
    sub = await db.erp_subscriptions.find_one(
        {"id": subscription_id, "institution_id": current_user["id"]},
        {"_id": 0}
    )
    
    if not sub:
        raise HTTPException(status_code=404, detail="Subscription not found")
    
    update_dict = {
        "canceled_at": datetime.now(timezone.utc).isoformat(),
        "cancellation_reason": reason
    }
    
    if immediate:
        update_dict["status"] = "canceled"
        update_dict["ended_at"] = datetime.now(timezone.utc).isoformat()
    else:
        update_dict["cancel_at_period_end"] = True
        update_dict["status"] = "canceling"
    
    await db.erp_subscriptions.update_one(
        {"id": subscription_id},
        {"$set": update_dict}
    )
    
    return {
        "message": "Subscription canceled" if immediate else "Subscription will cancel at period end",
        "effective_date": update_dict.get("ended_at") or sub["current_period_end"]
    }

# ==================== MRR/ARR ANALYTICS ====================

@router.get("/metrics/mrr")
async def get_mrr_metrics(
    current_user: dict = Depends(get_current_user)
):
    """Get MRR (Monthly Recurring Revenue) metrics"""
    # Active subscriptions
    active_subs = await db.erp_subscriptions.find(
        {
            "institution_id": current_user["id"],
            "status": {"$in": ["active", "trialing"]}
        },
        {"_id": 0, "mrr": 1, "currency": 1, "customer_id": 1, "plan_name": 1}
    ).to_list(10000)
    
    # Calculate totals
    total_mrr = sum(s.get("mrr", 0) for s in active_subs)
    total_arr = total_mrr * 12
    
    # Group by plan
    mrr_by_plan = {}
    for s in active_subs:
        plan = s.get("plan_name", "Unknown")
        if plan not in mrr_by_plan:
            mrr_by_plan[plan] = {"count": 0, "mrr": 0}
        mrr_by_plan[plan]["count"] += 1
        mrr_by_plan[plan]["mrr"] += s.get("mrr", 0)
    
    # Get historical MRR (last 12 months)
    # This would track MRR changes over time
    
    return {
        "current_mrr": round(total_mrr, 2),
        "current_arr": round(total_arr, 2),
        "active_subscriptions": len(active_subs),
        "avg_mrr_per_subscription": round(total_mrr / len(active_subs), 2) if active_subs else 0,
        "mrr_by_plan": {k: {"count": v["count"], "mrr": round(v["mrr"], 2)} for k, v in mrr_by_plan.items()}
    }

@router.get("/metrics/churn")
async def get_churn_metrics(
    period_months: int = 12,
    current_user: dict = Depends(get_current_user)
):
    """Get churn metrics"""
    start_date = (datetime.now(timezone.utc) - relativedelta(months=period_months)).isoformat()
    
    # Churned subscriptions in period
    churned = await db.erp_subscriptions.count_documents({
        "institution_id": current_user["id"],
        "status": "canceled",
        "canceled_at": {"$gte": start_date}
    })
    
    # Active at start of period (approximate)
    active_start = await db.erp_subscriptions.count_documents({
        "institution_id": current_user["id"],
        "created_at": {"$lt": start_date},
        "$or": [
            {"status": {"$in": ["active", "trialing"]}},
            {"canceled_at": {"$gte": start_date}}
        ]
    })
    
    # Current active
    active_now = await db.erp_subscriptions.count_documents({
        "institution_id": current_user["id"],
        "status": {"$in": ["active", "trialing"]}
    })
    
    # Calculate churn rate
    churn_rate = (churned / active_start * 100) if active_start > 0 else 0
    
    # MRR churn
    churned_mrr = await db.erp_subscriptions.aggregate([
        {
            "$match": {
                "institution_id": current_user["id"],
                "status": "canceled",
                "canceled_at": {"$gte": start_date}
            }
        },
        {"$group": {"_id": None, "total": {"$sum": "$mrr"}}}
    ]).to_list(1)
    
    return {
        "period_months": period_months,
        "churned_subscriptions": churned,
        "churn_rate_percent": round(churn_rate, 2),
        "active_at_start": active_start,
        "active_now": active_now,
        "net_growth": active_now - active_start,
        "churned_mrr": round(churned_mrr[0]["total"], 2) if churned_mrr else 0
    }

@router.get("/metrics/cohort")
async def get_cohort_analysis(
    cohort_by: str = Query("month", enum=["month", "quarter"]),
    current_user: dict = Depends(get_current_user)
):
    """Get subscription cohort analysis"""
    subscriptions = await db.erp_subscriptions.find(
        {"institution_id": current_user["id"]},
        {"_id": 0, "id": 1, "created_at": 1, "status": 1, "mrr": 1, "canceled_at": 1}
    ).to_list(10000)
    
    # Group by cohort
    cohorts = {}
    for sub in subscriptions:
        created = sub.get("created_at", "")[:7] if cohort_by == "month" else sub.get("created_at", "")[:4] + "-Q" + str((int(sub.get("created_at", "")[5:7]) - 1) // 3 + 1)
        
        if created not in cohorts:
            cohorts[created] = {
                "total": 0,
                "active": 0,
                "churned": 0,
                "mrr": 0
            }
        
        cohorts[created]["total"] += 1
        if sub["status"] in ["active", "trialing"]:
            cohorts[created]["active"] += 1
            cohorts[created]["mrr"] += sub.get("mrr", 0)
        elif sub["status"] == "canceled":
            cohorts[created]["churned"] += 1
    
    # Calculate retention rates
    result = []
    for cohort, data in sorted(cohorts.items()):
        retention = (data["active"] / data["total"] * 100) if data["total"] > 0 else 0
        result.append({
            "cohort": cohort,
            "total_started": data["total"],
            "still_active": data["active"],
            "churned": data["churned"],
            "retention_rate": round(retention, 2),
            "current_mrr": round(data["mrr"], 2)
        })
    
    return {"cohorts": result, "cohort_by": cohort_by}
