"""Pricing configuration router - Dynamic pricing management for Superadmin"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone

from database import db
from utils.auth import get_current_user

router = APIRouter(prefix="/pricing", tags=["Pricing"])

# Models
class ExamPlanConfig(BaseModel):
    plan_id: str
    exams: int
    base_cost: float
    price: float
    label: str
    enabled: bool = True

class VolumeTierConfig(BaseModel):
    tier_id: str
    min_licenses: int
    max_licenses: int
    price_multiplier: float
    discount_percent: int
    label: str
    enabled: bool = True

class AITutorOptionConfig(BaseModel):
    option_id: str
    minutes: int
    cost: float
    price: float
    label: str
    enabled: bool = True

class MobileAppPricingConfig(BaseModel):
    tier_id: str  # standard, premium, enterprise
    name: str
    description: str
    setup_fee: float
    monthly_fee: float
    features: List[str]
    enabled: bool = True

class CreditPackageConfig(BaseModel):
    package_id: str
    credits: int
    price: float
    bonus_credits: int = 0
    label: str
    popular: bool = False
    enabled: bool = True

class PricingUpdateRequest(BaseModel):
    exam_plans: Optional[List[ExamPlanConfig]] = None
    volume_tiers: Optional[List[VolumeTierConfig]] = None
    ai_tutor_options: Optional[List[AITutorOptionConfig]] = None
    mobile_app_pricing: Optional[List[MobileAppPricingConfig]] = None
    credit_packages: Optional[List[CreditPackageConfig]] = None

# Default pricing configurations
DEFAULT_EXAM_PLANS = [
    {"plan_id": "plan_5", "exams": 5, "base_cost": 4.70, "price": 9.40, "label": "5 Mock Exams", "enabled": True},
    {"plan_id": "plan_10", "exams": 10, "base_cost": 9.40, "price": 18.80, "label": "10 Mock Exams", "enabled": True},
    {"plan_id": "plan_20", "exams": 20, "base_cost": 18.80, "price": 37.60, "label": "20 Mock Exams", "enabled": True},
    {"plan_id": "plan_40", "exams": 40, "base_cost": 37.60, "price": 75.20, "label": "40 Mock Exams", "enabled": True},
    {"plan_id": "plan_60", "exams": 60, "base_cost": 56.40, "price": 112.80, "label": "60 Mock Exams", "enabled": True},
    {"plan_id": "plan_100", "exams": 100, "base_cost": 94.00, "price": 188.00, "label": "100 Mock Exams", "enabled": True},
]

DEFAULT_VOLUME_TIERS = [
    {"tier_id": "tier_100", "min_licenses": 1, "max_licenses": 100, "price_multiplier": 2.00, "discount_percent": 0, "label": "1-100 licenses", "enabled": True},
    {"tier_id": "tier_500", "min_licenses": 101, "max_licenses": 500, "price_multiplier": 1.85, "discount_percent": 7, "label": "101-500 licenses", "enabled": True},
    {"tier_id": "tier_1000", "min_licenses": 501, "max_licenses": 1000, "price_multiplier": 1.72, "discount_percent": 14, "label": "501-1,000 licenses", "enabled": True},
    {"tier_id": "tier_2000", "min_licenses": 1001, "max_licenses": 2000, "price_multiplier": 1.60, "discount_percent": 20, "label": "1,001-2,000 licenses", "enabled": True},
    {"tier_id": "tier_5000", "min_licenses": 2001, "max_licenses": 5000, "price_multiplier": 1.50, "discount_percent": 25, "label": "2,001-5,000 licenses", "enabled": True},
    {"tier_id": "tier_10000", "min_licenses": 5001, "max_licenses": 10000, "price_multiplier": 1.42, "discount_percent": 29, "label": "5,001-10,000 licenses", "enabled": True},
    {"tier_id": "tier_100000", "min_licenses": 10001, "max_licenses": 100000, "price_multiplier": 1.35, "discount_percent": 32, "label": "10,001+ licenses", "enabled": True},
]

DEFAULT_AI_TUTOR_OPTIONS = [
    {"option_id": "none", "minutes": 0, "cost": 0, "price": 0, "label": "No AI Tutor", "enabled": True},
    {"option_id": "basic", "minutes": 30, "cost": 1.80, "price": 5.00, "label": "30 min AI Tutor", "enabled": True},
    {"option_id": "standard", "minutes": 60, "cost": 3.60, "price": 9.00, "label": "60 min AI Tutor", "enabled": True},
    {"option_id": "premium", "minutes": 120, "cost": 7.20, "price": 15.00, "label": "120 min AI Tutor", "enabled": True},
    {"option_id": "unlimited", "minutes": 300, "cost": 18.00, "price": 35.00, "label": "300 min AI Tutor", "enabled": True},
]

DEFAULT_MOBILE_APP_PRICING = [
    {
        "tier_id": "standard",
        "name": "Standard",
        "description": "White-label en app compartida ProficientHub",
        "setup_fee": 0,
        "monthly_fee": 0,
        "features": [
            "Branding dinámico (logo, colores)",
            "Contenido separado por institución",
            "Push notifications",
            "Acceso offline",
            "Incluido en plan institucional"
        ],
        "enabled": True
    },
    {
        "tier_id": "premium",
        "name": "Premium App",
        "description": "App dedicada en App Store y Play Store",
        "setup_fee": 2000,
        "monthly_fee": 200,
        "features": [
            "Nombre propio en stores",
            "Ícono y splash screen personalizados",
            "URL de descarga propia",
            "Certificados y keys propios",
            "Build automatizado con cada release",
            "Soporte prioritario"
        ],
        "enabled": True
    },
    {
        "tier_id": "enterprise",
        "name": "Enterprise",
        "description": "App dedicada + backend dedicado + SLA",
        "setup_fee": 5000,
        "monthly_fee": 500,
        "features": [
            "Todo lo de Premium",
            "Backend dedicado",
            "Base de datos separada",
            "Dominio personalizado API",
            "SLA 99.9% uptime",
            "Soporte 24/7",
            "Integración personalizada"
        ],
        "enabled": True
    }
]

DEFAULT_CREDIT_PACKAGES = [
    {"package_id": "starter", "credits": 100, "price": 10.00, "bonus_credits": 0, "label": "100 Credits", "popular": False, "enabled": True},
    {"package_id": "basic", "credits": 500, "price": 45.00, "bonus_credits": 50, "label": "500 + 50 Bonus", "popular": False, "enabled": True},
    {"package_id": "standard", "credits": 1000, "price": 80.00, "bonus_credits": 150, "label": "1000 + 150 Bonus", "popular": True, "enabled": True},
    {"package_id": "pro", "credits": 2500, "price": 175.00, "bonus_credits": 500, "label": "2500 + 500 Bonus", "popular": False, "enabled": True},
    {"package_id": "enterprise", "credits": 5000, "price": 300.00, "bonus_credits": 1500, "label": "5000 + 1500 Bonus", "popular": False, "enabled": True},
]

async def get_pricing_config():
    """Get current pricing configuration from database or defaults"""
    config = await db.platform_config.find_one({"type": "pricing"}, {"_id": 0})
    
    if not config:
        config = {
            "type": "pricing",
            "exam_plans": DEFAULT_EXAM_PLANS,
            "volume_tiers": DEFAULT_VOLUME_TIERS,
            "ai_tutor_options": DEFAULT_AI_TUTOR_OPTIONS,
            "mobile_app_pricing": DEFAULT_MOBILE_APP_PRICING,
            "credit_packages": DEFAULT_CREDIT_PACKAGES,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        await db.platform_config.insert_one(config)
    
    return config

@router.get("/config")
async def get_pricing_configuration(current_user: dict = Depends(get_current_user)):
    """Get all pricing configuration (public for calculator, full for admin)"""
    config = await get_pricing_config()
    
    # Remove internal costs for non-admin users
    if current_user.get("user_type") != "admin" or not current_user.get("is_superadmin"):
        for plan in config.get("exam_plans", []):
            plan.pop("base_cost", None)
        for option in config.get("ai_tutor_options", []):
            option.pop("cost", None)
    
    return config

@router.get("/public")
async def get_public_pricing():
    """Get public pricing for landing page and calculator"""
    config = await get_pricing_config()
    
    # Remove internal costs and disabled items
    public_config = {
        "exam_plans": [
            {"plan_id": p["plan_id"], "exams": p["exams"], "price": p["price"], "label": p["label"]}
            for p in config.get("exam_plans", []) if p.get("enabled", True)
        ],
        "volume_tiers": [
            {"tier_id": t["tier_id"], "min_licenses": t["min_licenses"], "max_licenses": t["max_licenses"], 
             "discount_percent": t["discount_percent"], "label": t["label"]}
            for t in config.get("volume_tiers", []) if t.get("enabled", True)
        ],
        "ai_tutor_options": [
            {"option_id": o["option_id"], "minutes": o["minutes"], "price": o["price"], "label": o["label"]}
            for o in config.get("ai_tutor_options", []) if o.get("enabled", True)
        ],
        "mobile_app_pricing": [
            {"tier_id": m["tier_id"], "name": m["name"], "description": m["description"],
             "setup_fee": m["setup_fee"], "monthly_fee": m["monthly_fee"], "features": m["features"]}
            for m in config.get("mobile_app_pricing", []) if m.get("enabled", True)
        ],
        "credit_packages": [
            {"package_id": c["package_id"], "credits": c["credits"], "price": c["price"],
             "bonus_credits": c["bonus_credits"], "label": c["label"], "popular": c["popular"]}
            for c in config.get("credit_packages", []) if c.get("enabled", True)
        ]
    }
    
    return public_config

@router.put("/config")
async def update_pricing_configuration(
    update: PricingUpdateRequest,
    current_user: dict = Depends(get_current_user)
):
    """Update pricing configuration (Superadmin only)"""
    if current_user.get("user_type") != "admin" or not current_user.get("is_superadmin"):
        raise HTTPException(status_code=403, detail="Superadmin access required")
    
    update_data = {"updated_at": datetime.now(timezone.utc).isoformat()}
    
    if update.exam_plans is not None:
        update_data["exam_plans"] = [p.dict() for p in update.exam_plans]
    if update.volume_tiers is not None:
        update_data["volume_tiers"] = [t.dict() for t in update.volume_tiers]
    if update.ai_tutor_options is not None:
        update_data["ai_tutor_options"] = [o.dict() for o in update.ai_tutor_options]
    if update.mobile_app_pricing is not None:
        update_data["mobile_app_pricing"] = [m.dict() for m in update.mobile_app_pricing]
    if update.credit_packages is not None:
        update_data["credit_packages"] = [c.dict() for c in update.credit_packages]
    
    await db.platform_config.update_one(
        {"type": "pricing"},
        {"$set": update_data},
        upsert=True
    )
    
    # Log the change
    await db.admin_audit_log.insert_one({
        "action": "pricing_update",
        "admin_id": current_user["id"],
        "changes": list(update_data.keys()),
        "timestamp": datetime.now(timezone.utc).isoformat()
    })
    
    return {"success": True, "message": "Pricing configuration updated"}

@router.post("/exam-plan")
async def add_exam_plan(
    plan: ExamPlanConfig,
    current_user: dict = Depends(get_current_user)
):
    """Add a new exam plan"""
    if current_user.get("user_type") != "admin" or not current_user.get("is_superadmin"):
        raise HTTPException(status_code=403, detail="Superadmin access required")
    
    await db.platform_config.update_one(
        {"type": "pricing"},
        {"$push": {"exam_plans": plan.dict()}},
        upsert=True
    )
    
    return {"success": True, "message": f"Exam plan {plan.plan_id} added"}

@router.post("/mobile-app-tier")
async def add_mobile_app_tier(
    tier: MobileAppPricingConfig,
    current_user: dict = Depends(get_current_user)
):
    """Add a new mobile app pricing tier"""
    if current_user.get("user_type") != "admin" or not current_user.get("is_superadmin"):
        raise HTTPException(status_code=403, detail="Superadmin access required")
    
    await db.platform_config.update_one(
        {"type": "pricing"},
        {"$push": {"mobile_app_pricing": tier.dict()}},
        upsert=True
    )
    
    return {"success": True, "message": f"Mobile app tier {tier.tier_id} added"}

@router.post("/credit-package")
async def add_credit_package(
    package: CreditPackageConfig,
    current_user: dict = Depends(get_current_user)
):
    """Add a new credit package"""
    if current_user.get("user_type") != "admin" or not current_user.get("is_superadmin"):
        raise HTTPException(status_code=403, detail="Superadmin access required")
    
    await db.platform_config.update_one(
        {"type": "pricing"},
        {"$push": {"credit_packages": package.dict()}},
        upsert=True
    )
    
    return {"success": True, "message": f"Credit package {package.package_id} added"}

@router.delete("/exam-plan/{plan_id}")
async def delete_exam_plan(
    plan_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete an exam plan"""
    if current_user.get("user_type") != "admin" or not current_user.get("is_superadmin"):
        raise HTTPException(status_code=403, detail="Superadmin access required")
    
    await db.platform_config.update_one(
        {"type": "pricing"},
        {"$pull": {"exam_plans": {"plan_id": plan_id}}}
    )
    
    return {"success": True, "message": f"Exam plan {plan_id} deleted"}

@router.get("/calculator")
async def calculate_pricing(
    exam_plan: str,
    licenses: int,
    ai_tutor: str = "none"
):
    """Calculate total pricing for a configuration"""
    config = await get_pricing_config()
    
    # Find exam plan
    plan = next((p for p in config.get("exam_plans", []) if p["plan_id"] == exam_plan), None)
    if not plan:
        raise HTTPException(status_code=400, detail="Invalid exam plan")
    
    # Find volume tier
    tier = next((t for t in config.get("volume_tiers", []) 
                 if t["min_licenses"] <= licenses <= t["max_licenses"]), None)
    if not tier:
        tier = config.get("volume_tiers", [])[-1]  # Use highest tier
    
    # Find AI tutor option
    ai_option = next((o for o in config.get("ai_tutor_options", []) if o["option_id"] == ai_tutor), None)
    if not ai_option:
        ai_option = {"price": 0, "minutes": 0}
    
    # Calculate
    base_price = plan["price"]
    price_per_license = base_price * tier["price_multiplier"] + ai_option["price"]
    total_price = price_per_license * licenses
    savings = (base_price * 2.0 * licenses) - total_price  # Savings vs tier 1 pricing
    
    return {
        "exam_plan": plan,
        "volume_tier": tier,
        "ai_tutor": ai_option,
        "licenses": licenses,
        "price_per_license": round(price_per_license, 2),
        "total_price": round(total_price, 2),
        "savings": round(max(0, savings), 2),
        "discount_applied": tier["discount_percent"]
    }
