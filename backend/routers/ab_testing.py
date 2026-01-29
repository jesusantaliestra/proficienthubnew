"""
A/B Testing Framework Router
Enables creating experiments, variants, and tracking conversions
"""
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone, timedelta
import uuid
import random
import hashlib

router = APIRouter(prefix="/ab-testing", tags=["A/B Testing"])

# Import shared dependencies
import sys
sys.path.append('/app/backend')
from motor.motor_asyncio import AsyncIOMotorClient
import os

client = AsyncIOMotorClient(os.environ.get('MONGO_URL'))
db = client[os.environ.get('DB_NAME', 'proficienthub')]

# Auth dependency - import from main server
from server import get_current_user

async def get_admin_user(current_user: dict = Depends(get_current_user)):
    if current_user.get("user_type") not in ["admin", "institution"]:
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user

# ==================== MODELS ====================

class ExperimentCreate(BaseModel):
    name: str
    description: Optional[str] = None
    experiment_type: str  # pricing, feature, ui, content
    target_metric: str  # conversion, engagement, revenue, signup
    traffic_percentage: int = 100  # Percentage of traffic to include
    variants: List[Dict[str, Any]]  # [{name, config, weight}]
    targeting: Optional[Dict[str, Any]] = None  # {countries, user_types, etc}
    start_date: Optional[str] = None
    end_date: Optional[str] = None

class ExperimentUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    traffic_percentage: Optional[int] = None
    is_active: Optional[bool] = None
    end_date: Optional[str] = None

class ConversionEvent(BaseModel):
    experiment_id: str
    variant_id: str
    event_type: str  # signup, purchase, engagement, click
    value: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None

# ==================== EXPERIMENTS ====================

@router.post("/experiments")
async def create_experiment(
    experiment: ExperimentCreate,
    current_user: dict = Depends(get_admin_user)
):
    """Create a new A/B test experiment"""
    experiment_id = str(uuid.uuid4())
    
    # Process variants with IDs and initial stats
    variants = []
    total_weight = sum(v.get("weight", 1) for v in experiment.variants)
    
    for i, variant in enumerate(experiment.variants):
        variant_id = str(uuid.uuid4())
        variants.append({
            "id": variant_id,
            "name": variant.get("name", f"Variant {chr(65+i)}"),
            "config": variant.get("config", {}),
            "weight": variant.get("weight", 1) / total_weight,  # Normalize weights
            "impressions": 0,
            "conversions": 0,
            "revenue": 0,
            "is_control": i == 0  # First variant is control
        })
    
    experiment_doc = {
        "id": experiment_id,
        "institution_id": current_user["id"],
        "name": experiment.name,
        "description": experiment.description,
        "experiment_type": experiment.experiment_type,
        "target_metric": experiment.target_metric,
        "traffic_percentage": experiment.traffic_percentage,
        "variants": variants,
        "targeting": experiment.targeting or {},
        "is_active": True,
        "start_date": experiment.start_date or datetime.now(timezone.utc).isoformat(),
        "end_date": experiment.end_date,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "winner_variant_id": None,
        "statistical_significance": None
    }
    
    await db.ab_experiments.insert_one(experiment_doc)
    
    return {
        "id": experiment_id,
        "variants": [{"id": v["id"], "name": v["name"]} for v in variants],
        "message": "Experiment created successfully"
    }

@router.get("/experiments")
async def list_experiments(
    is_active: Optional[bool] = None,
    experiment_type: Optional[str] = None,
    page: int = 1,
    per_page: int = 20,
    current_user: dict = Depends(get_admin_user)
):
    """List all experiments"""
    query = {"institution_id": current_user["id"]}
    
    if is_active is not None:
        query["is_active"] = is_active
    if experiment_type:
        query["experiment_type"] = experiment_type
    
    skip = (page - 1) * per_page
    
    experiments = await db.ab_experiments.find(
        query, {"_id": 0}
    ).sort("created_at", -1).skip(skip).limit(per_page).to_list(per_page)
    
    total = await db.ab_experiments.count_documents(query)
    
    return {
        "experiments": experiments,
        "total": total,
        "page": page,
        "per_page": per_page
    }

@router.get("/experiments/{experiment_id}")
async def get_experiment(
    experiment_id: str,
    current_user: dict = Depends(get_admin_user)
):
    """Get experiment details with stats"""
    experiment = await db.ab_experiments.find_one(
        {"id": experiment_id, "institution_id": current_user["id"]},
        {"_id": 0}
    )
    
    if not experiment:
        raise HTTPException(status_code=404, detail="Experiment not found")
    
    # Calculate conversion rates and statistical significance
    for variant in experiment.get("variants", []):
        impressions = variant.get("impressions", 0)
        conversions = variant.get("conversions", 0)
        variant["conversion_rate"] = (conversions / impressions * 100) if impressions > 0 else 0
        variant["revenue_per_impression"] = (variant.get("revenue", 0) / impressions) if impressions > 0 else 0
    
    # Simple statistical significance calculation
    if len(experiment.get("variants", [])) >= 2:
        control = experiment["variants"][0]
        experiment["statistical_analysis"] = []
        
        for variant in experiment["variants"][1:]:
            # Z-test approximation for conversion rate comparison
            significance = calculate_significance(
                control.get("impressions", 0),
                control.get("conversions", 0),
                variant.get("impressions", 0),
                variant.get("conversions", 0)
            )
            experiment["statistical_analysis"].append({
                "variant_id": variant["id"],
                "variant_name": variant["name"],
                "vs_control_lift": round(
                    ((variant.get("conversion_rate", 0) - control.get("conversion_rate", 0)) / 
                     control.get("conversion_rate", 1)) * 100, 2
                ) if control.get("conversion_rate", 0) > 0 else 0,
                "confidence_level": significance,
                "is_significant": significance >= 95
            })
    
    return experiment

@router.patch("/experiments/{experiment_id}")
async def update_experiment(
    experiment_id: str,
    updates: ExperimentUpdate,
    current_user: dict = Depends(get_admin_user)
):
    """Update experiment settings"""
    update_dict = {k: v for k, v in updates.dict().items() if v is not None}
    update_dict["updated_at"] = datetime.now(timezone.utc).isoformat()
    
    result = await db.ab_experiments.update_one(
        {"id": experiment_id, "institution_id": current_user["id"]},
        {"$set": update_dict}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Experiment not found")
    
    return {"message": "Experiment updated"}

@router.post("/experiments/{experiment_id}/stop")
async def stop_experiment(
    experiment_id: str,
    winner_variant_id: Optional[str] = None,
    current_user: dict = Depends(get_admin_user)
):
    """Stop an experiment and optionally declare a winner"""
    result = await db.ab_experiments.update_one(
        {"id": experiment_id, "institution_id": current_user["id"]},
        {"$set": {
            "is_active": False,
            "end_date": datetime.now(timezone.utc).isoformat(),
            "winner_variant_id": winner_variant_id,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Experiment not found")
    
    return {"message": "Experiment stopped", "winner_variant_id": winner_variant_id}

@router.delete("/experiments/{experiment_id}")
async def delete_experiment(
    experiment_id: str,
    current_user: dict = Depends(get_admin_user)
):
    """Delete an experiment"""
    result = await db.ab_experiments.delete_one(
        {"id": experiment_id, "institution_id": current_user["id"]}
    )
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Experiment not found")
    
    # Also delete related events
    await db.ab_events.delete_many({"experiment_id": experiment_id})
    
    return {"message": "Experiment deleted"}

# ==================== VARIANT ASSIGNMENT ====================

@router.get("/assign")
async def assign_variant(
    experiment_id: str,
    user_id: Optional[str] = None,
    session_id: Optional[str] = None,
    request: Request = None
):
    """Assign a user to an experiment variant (deterministic)"""
    experiment = await db.ab_experiments.find_one(
        {"id": experiment_id, "is_active": True},
        {"_id": 0}
    )
    
    if not experiment:
        raise HTTPException(status_code=404, detail="Active experiment not found")
    
    # Check traffic percentage
    identifier = user_id or session_id or str(request.client.host if request else random.random())
    hash_value = int(hashlib.md5(f"{experiment_id}:{identifier}".encode()).hexdigest(), 16) % 100
    
    if hash_value >= experiment.get("traffic_percentage", 100):
        # User not in experiment, return control
        control = next((v for v in experiment["variants"] if v.get("is_control")), experiment["variants"][0])
        return {
            "in_experiment": False,
            "variant_id": control["id"],
            "variant_name": control["name"],
            "config": control.get("config", {})
        }
    
    # Deterministic variant assignment based on user/session
    variant_hash = int(hashlib.md5(f"{experiment_id}:variant:{identifier}".encode()).hexdigest(), 16)
    cumulative_weight = 0
    assigned_variant = experiment["variants"][0]
    
    for variant in experiment["variants"]:
        cumulative_weight += variant.get("weight", 0.5)
        if (variant_hash % 1000) / 1000 < cumulative_weight:
            assigned_variant = variant
            break
    
    # Record impression
    await db.ab_experiments.update_one(
        {"id": experiment_id, "variants.id": assigned_variant["id"]},
        {"$inc": {"variants.$.impressions": 1}}
    )
    
    # Store assignment for tracking
    await db.ab_assignments.update_one(
        {"experiment_id": experiment_id, "identifier": identifier},
        {"$set": {
            "variant_id": assigned_variant["id"],
            "assigned_at": datetime.now(timezone.utc).isoformat()
        }},
        upsert=True
    )
    
    return {
        "in_experiment": True,
        "variant_id": assigned_variant["id"],
        "variant_name": assigned_variant["name"],
        "config": assigned_variant.get("config", {}),
        "is_control": assigned_variant.get("is_control", False)
    }

# ==================== CONVERSION TRACKING ====================

@router.post("/convert")
async def track_conversion(
    event: ConversionEvent,
    user_id: Optional[str] = None,
    session_id: Optional[str] = None
):
    """Track a conversion event for an experiment"""
    experiment = await db.ab_experiments.find_one(
        {"id": event.experiment_id},
        {"_id": 0}
    )
    
    if not experiment:
        raise HTTPException(status_code=404, detail="Experiment not found")
    
    # Verify variant exists
    variant = next((v for v in experiment["variants"] if v["id"] == event.variant_id), None)
    if not variant:
        raise HTTPException(status_code=400, detail="Invalid variant ID")
    
    # Record event
    event_doc = {
        "id": str(uuid.uuid4()),
        "experiment_id": event.experiment_id,
        "variant_id": event.variant_id,
        "user_id": user_id,
        "session_id": session_id,
        "event_type": event.event_type,
        "value": event.value or 0,
        "metadata": event.metadata or {},
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.ab_events.insert_one(event_doc)
    
    # Update variant stats
    update_ops = {"$inc": {"variants.$.conversions": 1}}
    if event.value:
        update_ops["$inc"]["variants.$.revenue"] = event.value
    
    await db.ab_experiments.update_one(
        {"id": event.experiment_id, "variants.id": event.variant_id},
        update_ops
    )
    
    return {"message": "Conversion tracked", "event_id": event_doc["id"]}

# ==================== ANALYTICS ====================

@router.get("/experiments/{experiment_id}/analytics")
async def get_experiment_analytics(
    experiment_id: str,
    days: int = 30,
    current_user: dict = Depends(get_admin_user)
):
    """Get detailed analytics for an experiment"""
    experiment = await db.ab_experiments.find_one(
        {"id": experiment_id, "institution_id": current_user["id"]},
        {"_id": 0}
    )
    
    if not experiment:
        raise HTTPException(status_code=404, detail="Experiment not found")
    
    # Get events over time
    start_date = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
    
    # Daily breakdown pipeline
    pipeline = [
        {"$match": {
            "experiment_id": experiment_id,
            "created_at": {"$gte": start_date}
        }},
        {"$group": {
            "_id": {
                "date": {"$substr": ["$created_at", 0, 10]},
                "variant_id": "$variant_id"
            },
            "conversions": {"$sum": 1},
            "revenue": {"$sum": "$value"}
        }},
        {"$sort": {"_id.date": 1}}
    ]
    
    daily_stats = await db.ab_events.aggregate(pipeline).to_list(1000)
    
    # Format for chart
    dates = sorted(set(s["_id"]["date"] for s in daily_stats))
    chart_data = []
    
    for date in dates:
        day_data = {"date": date}
        for variant in experiment.get("variants", []):
            variant_stat = next(
                (s for s in daily_stats if s["_id"]["date"] == date and s["_id"]["variant_id"] == variant["id"]),
                None
            )
            day_data[f"{variant['name']}_conversions"] = variant_stat["conversions"] if variant_stat else 0
            day_data[f"{variant['name']}_revenue"] = variant_stat["revenue"] if variant_stat else 0
        chart_data.append(day_data)
    
    return {
        "experiment": experiment,
        "chart_data": chart_data,
        "summary": {
            "total_impressions": sum(v.get("impressions", 0) for v in experiment.get("variants", [])),
            "total_conversions": sum(v.get("conversions", 0) for v in experiment.get("variants", [])),
            "total_revenue": sum(v.get("revenue", 0) for v in experiment.get("variants", []))
        }
    }

# ==================== HELPER FUNCTIONS ====================

def calculate_significance(control_impressions: int, control_conversions: int,
                          variant_impressions: int, variant_conversions: int) -> float:
    """Calculate statistical significance using Z-test approximation"""
    import math
    
    if control_impressions < 30 or variant_impressions < 30:
        return 0  # Not enough data
    
    p1 = control_conversions / control_impressions if control_impressions > 0 else 0
    p2 = variant_conversions / variant_impressions if variant_impressions > 0 else 0
    
    if p1 == 0 and p2 == 0:
        return 0
    
    # Pooled probability
    p_pool = (control_conversions + variant_conversions) / (control_impressions + variant_impressions)
    
    if p_pool == 0 or p_pool == 1:
        return 0
    
    # Standard error
    se = math.sqrt(p_pool * (1 - p_pool) * (1/control_impressions + 1/variant_impressions))
    
    if se == 0:
        return 0
    
    # Z-score
    z = abs(p2 - p1) / se
    
    # Convert to confidence level (approximation)
    if z >= 2.576:
        return 99
    elif z >= 1.96:
        return 95
    elif z >= 1.645:
        return 90
    elif z >= 1.28:
        return 80
    else:
        return round(z * 40, 1)  # Rough approximation for lower values
