"""OET Exam Packs and Purchases Router

This module handles:
- Exam pack listings by profession
- Purchase processing
- Student access management
- Institution configuration (placement test, agent planner)
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timezone
import os
import uuid

router = APIRouter(prefix="/oet-packs", tags=["OET Exam Packs"])

# Database
from motor.motor_asyncio import AsyncIOMotorClient
mongo_client = AsyncIOMotorClient(os.environ.get("MONGO_URL"))
db = mongo_client[os.environ.get("DB_NAME", "eduplat")]

# Auth dependency
from server import get_current_user


# Exam Pack configurations
OET_EXAM_PACKS = {
    "nursing": [
        {
            "id": "NUR-STARTER",
            "name": "OET Nursing Starter Pack",
            "profession": "nursing",
            "num_mocks": 3,
            "price_usd": 29.99,
            "features": [
                "3 complete mock exams",
                "AI Speaking practice (2 sessions)",
                "Detailed scoring and feedback",
                "30-day access"
            ],
            "popular": False
        },
        {
            "id": "NUR-STANDARD",
            "name": "OET Nursing Standard Pack",
            "profession": "nursing",
            "num_mocks": 5,
            "price_usd": 49.99,
            "features": [
                "5 complete mock exams",
                "Unlimited AI Speaking practice",
                "Detailed scoring and feedback",
                "Writing task evaluation",
                "60-day access"
            ],
            "popular": True
        },
        {
            "id": "NUR-PREMIUM",
            "name": "OET Nursing Premium Pack",
            "profession": "nursing",
            "num_mocks": 10,
            "price_usd": 89.99,
            "features": [
                "10 complete mock exams",
                "Unlimited AI Speaking practice",
                "Detailed scoring and feedback",
                "Writing task evaluation with AI feedback",
                "Personalized study plan",
                "90-day access"
            ],
            "popular": False
        }
    ],
    "medicine": [
        {
            "id": "MED-STARTER",
            "name": "OET Medicine Starter Pack",
            "profession": "medicine",
            "num_mocks": 3,
            "price_usd": 34.99,
            "features": [
                "3 complete mock exams",
                "AI Speaking practice (2 sessions)",
                "Detailed scoring and feedback",
                "30-day access"
            ],
            "popular": False
        },
        {
            "id": "MED-STANDARD",
            "name": "OET Medicine Standard Pack",
            "profession": "medicine",
            "num_mocks": 5,
            "price_usd": 59.99,
            "features": [
                "5 complete mock exams",
                "Unlimited AI Speaking practice",
                "Detailed scoring and feedback",
                "Writing task evaluation",
                "60-day access"
            ],
            "popular": True
        }
    ]
}

# Generic packs for all professions
def get_generic_packs(profession: str):
    """Generate generic exam packs for professions without specific packs"""
    profession_name = profession.replace("_", " ").title()
    return [
        {
            "id": f"{profession.upper()[:3]}-STARTER",
            "name": f"OET {profession_name} Starter Pack",
            "profession": profession,
            "num_mocks": 3,
            "price_usd": 29.99,
            "features": [
                "3 complete mock exams",
                "AI Speaking practice (2 sessions)",
                "Detailed scoring and feedback",
                "30-day access"
            ],
            "popular": False
        },
        {
            "id": f"{profession.upper()[:3]}-STANDARD",
            "name": f"OET {profession_name} Standard Pack",
            "profession": profession,
            "num_mocks": 5,
            "price_usd": 49.99,
            "features": [
                "5 complete mock exams",
                "Unlimited AI Speaking practice",
                "Detailed scoring and feedback",
                "Writing task evaluation",
                "60-day access"
            ],
            "popular": True
        },
        {
            "id": f"{profession.upper()[:3]}-PREMIUM",
            "name": f"OET {profession_name} Premium Pack",
            "profession": profession,
            "num_mocks": 10,
            "price_usd": 89.99,
            "features": [
                "10 complete mock exams",
                "Unlimited AI Speaking practice",
                "Detailed scoring and feedback",
                "Writing task evaluation with AI feedback",
                "Personalized study plan",
                "90-day access"
            ],
            "popular": False
        }
    ]


class PurchaseRequest(BaseModel):
    pack_id: str
    profession: str
    payment_method: Optional[str] = "stripe"


class InstitutionOETConfig(BaseModel):
    enable_placement_test: bool = False
    placement_test_is_mandatory: bool = False
    placement_test_is_free: bool = True
    enable_agent_planner: bool = False
    target_exam_date: Optional[str] = None
    default_profession: Optional[str] = "nursing"


# =============================================
# Exam Pack Endpoints
# =============================================

@router.get("/packs/{profession}")
async def get_exam_packs(profession: str):
    """Get available exam packs for a profession"""
    
    if profession in OET_EXAM_PACKS:
        packs = OET_EXAM_PACKS[profession]
    else:
        packs = get_generic_packs(profession)
    
    return {
        "profession": profession,
        "packs": packs,
        "count": len(packs)
    }


@router.get("/packs")
async def get_all_packs():
    """Get all available exam packs for all professions"""
    
    all_packs = {}
    professions = [
        "nursing", "medicine", "dentistry", "pharmacy", "physiotherapy",
        "radiography", "optometry", "dietetics", "occupational_therapy",
        "speech_pathology", "veterinary_science", "podiatry"
    ]
    
    for prof in professions:
        if prof in OET_EXAM_PACKS:
            all_packs[prof] = OET_EXAM_PACKS[prof]
        else:
            all_packs[prof] = get_generic_packs(prof)
    
    return {"packs": all_packs}


@router.post("/purchase")
async def purchase_exam_pack(
    request: PurchaseRequest,
    current_user: dict = Depends(get_current_user)
):
    """Purchase an exam pack"""
    
    user_id = current_user["id"]
    
    # Get pack details
    packs = OET_EXAM_PACKS.get(request.profession, get_generic_packs(request.profession))
    pack = next((p for p in packs if p["id"] == request.pack_id), None)
    
    if not pack:
        raise HTTPException(status_code=404, detail="Exam pack not found")
    
    # Create purchase record
    purchase = {
        "id": str(uuid.uuid4()),
        "user_id": user_id,
        "pack_id": request.pack_id,
        "pack_name": pack["name"],
        "profession": request.profession,
        "num_mocks": pack["num_mocks"],
        "price_usd": pack["price_usd"],
        "payment_method": request.payment_method,
        "payment_status": "completed",  # In real app, would integrate with Stripe
        "purchased_at": datetime.now(timezone.utc).isoformat(),
        "access_expires_at": None,  # Calculate based on pack features
        "mocks_remaining": pack["num_mocks"],
        "speaking_sessions_remaining": -1 if "Unlimited" in str(pack["features"]) else 2
    }
    
    # Calculate expiry based on pack
    days = 30
    if "60-day" in str(pack["features"]):
        days = 60
    elif "90-day" in str(pack["features"]):
        days = 90
    
    from datetime import timedelta
    expires = datetime.now(timezone.utc) + timedelta(days=days)
    purchase["access_expires_at"] = expires.isoformat()
    
    await db.oet_purchases.insert_one(purchase)
    
    # Update or create student OET enrollment
    await db.student_oet_enrollment.update_one(
        {"user_id": user_id, "profession": request.profession},
        {
            "$set": {
                "user_id": user_id,
                "profession": request.profession,
                "enrolled_at": datetime.now(timezone.utc).isoformat(),
                "pack_id": request.pack_id,
                "pack_name": pack["name"]
            },
            "$inc": {
                "total_mocks_purchased": pack["num_mocks"]
            }
        },
        upsert=True
    )
    
    return {
        "purchase_id": purchase["id"],
        "pack": pack,
        "access_expires": purchase["access_expires_at"],
        "mocks_available": pack["num_mocks"],
        "message": f"Successfully purchased {pack['name']}!"
    }


@router.get("/my-purchases")
async def get_user_purchases(current_user: dict = Depends(get_current_user)):
    """Get user's purchase history"""
    
    purchases = await db.oet_purchases.find(
        {"user_id": current_user["id"]},
        {"_id": 0}
    ).sort("purchased_at", -1).to_list(50)
    
    return {"purchases": purchases, "count": len(purchases)}


@router.get("/my-access/{profession}")
async def get_user_access(
    profession: str,
    current_user: dict = Depends(get_current_user)
):
    """Get user's current access for a profession"""
    
    # Get enrollment
    enrollment = await db.student_oet_enrollment.find_one(
        {"user_id": current_user["id"], "profession": profession},
        {"_id": 0}
    )
    
    if not enrollment:
        return {
            "profession": profession,
            "has_access": False,
            "message": "No active enrollment for this profession"
        }
    
    # Get active purchases
    active_purchases = await db.oet_purchases.find(
        {
            "user_id": current_user["id"],
            "profession": profession,
            "access_expires_at": {"$gt": datetime.now(timezone.utc).isoformat()}
        },
        {"_id": 0}
    ).to_list(10)
    
    mocks_remaining = sum(p.get("mocks_remaining", 0) for p in active_purchases)
    
    return {
        "profession": profession,
        "has_access": mocks_remaining > 0,
        "mocks_remaining": mocks_remaining,
        "enrollment": enrollment,
        "active_purchases": active_purchases
    }


# =============================================
# Institution Configuration Endpoints
# =============================================

@router.get("/institution/config")
async def get_institution_oet_config(current_user: dict = Depends(get_current_user)):
    """Get institution's OET configuration"""
    
    institution_id = current_user.get("institution_id")
    if not institution_id:
        # Return defaults for individual users
        return InstitutionOETConfig().dict()
    
    config = await db.institution_oet_config.find_one(
        {"institution_id": institution_id},
        {"_id": 0}
    )
    
    if not config:
        return InstitutionOETConfig().dict()
    
    return config


@router.put("/institution/config")
async def update_institution_oet_config(
    config: InstitutionOETConfig,
    current_user: dict = Depends(get_current_user)
):
    """Update institution's OET configuration (institution admin only)"""
    
    if current_user.get("user_type") not in ["institution", "admin"]:
        raise HTTPException(status_code=403, detail="Institution admin access required")
    
    institution_id = current_user.get("institution_id") or current_user.get("id")
    
    await db.institution_oet_config.update_one(
        {"institution_id": institution_id},
        {
            "$set": {
                **config.dict(),
                "institution_id": institution_id,
                "updated_at": datetime.now(timezone.utc).isoformat(),
                "updated_by": current_user["id"]
            }
        },
        upsert=True
    )
    
    return {
        "message": "OET configuration updated",
        "config": config.dict()
    }


# =============================================
# Placement Test Endpoints
# =============================================

@router.get("/placement-test/config")
async def get_placement_test_config(current_user: dict = Depends(get_current_user)):
    """Check if placement test is required for user"""
    
    institution_id = current_user.get("institution_id")
    
    # Get institution config
    config = None
    if institution_id:
        config = await db.institution_oet_config.find_one(
            {"institution_id": institution_id},
            {"_id": 0}
        )
    
    if not config:
        config = InstitutionOETConfig().dict()
    
    # Check if user has already completed placement test
    user_placement = await db.oet_placement_results.find_one(
        {"user_id": current_user["id"]},
        {"_id": 0}
    )
    
    return {
        "placement_test_enabled": config.get("enable_placement_test", False),
        "placement_test_mandatory": config.get("placement_test_is_mandatory", False),
        "placement_test_free": config.get("placement_test_is_free", True),
        "user_completed": user_placement is not None,
        "user_result": user_placement
    }


@router.post("/placement-test/start")
async def start_placement_test(current_user: dict = Depends(get_current_user)):
    """Start a placement test session"""
    
    session_id = str(uuid.uuid4())
    
    session = {
        "id": session_id,
        "user_id": current_user["id"],
        "status": "in_progress",
        "started_at": datetime.now(timezone.utc).isoformat(),
        "sections": {
            "listening": {"status": "pending", "score": None},
            "reading": {"status": "pending", "score": None},
            "writing": {"status": "pending", "score": None},
            "speaking": {"status": "pending", "score": None}
        }
    }
    
    await db.oet_placement_sessions.insert_one(session)
    
    return {
        "session_id": session_id,
        "message": "Placement test started",
        "estimated_duration": "45 minutes"
    }


@router.post("/placement-test/{session_id}/complete")
async def complete_placement_test(
    session_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Complete placement test and get results"""
    
    session = await db.oet_placement_sessions.find_one(
        {"id": session_id, "user_id": current_user["id"]}
    )
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Calculate overall score (mock calculation for demo)
    sections = session.get("sections", {})
    scores = [s.get("score", 50) for s in sections.values() if s.get("score")]
    overall_score = sum(scores) / len(scores) if scores else 50
    
    # Determine estimated band
    if overall_score >= 80:
        estimated_band = "B"
    elif overall_score >= 65:
        estimated_band = "C+"
    elif overall_score >= 50:
        estimated_band = "C"
    else:
        estimated_band = "D"
    
    # Save results
    result = {
        "user_id": current_user["id"],
        "session_id": session_id,
        "overall_score": overall_score,
        "estimated_band": estimated_band,
        "section_scores": sections,
        "completed_at": datetime.now(timezone.utc).isoformat(),
        "recommendations": get_study_recommendations(overall_score, sections)
    }
    
    await db.oet_placement_results.update_one(
        {"user_id": current_user["id"]},
        {"$set": result},
        upsert=True
    )
    
    # Update session
    await db.oet_placement_sessions.update_one(
        {"id": session_id},
        {"$set": {"status": "completed", "completed_at": result["completed_at"]}}
    )
    
    return {
        "result": result,
        "message": "Placement test completed"
    }


def get_study_recommendations(score: float, sections: dict) -> List[str]:
    """Generate study recommendations based on placement test results"""
    
    recommendations = []
    
    if score < 50:
        recommendations.append("Focus on foundational English skills before attempting full mock exams")
        recommendations.append("Complete all section practices at least twice")
    elif score < 65:
        recommendations.append("Work on your weakest sections first")
        recommendations.append("Take 2-3 mock exams before your actual test date")
    else:
        recommendations.append("Maintain regular practice to keep skills sharp")
        recommendations.append("Focus on time management during mock exams")
    
    # Section-specific recommendations
    for section, data in sections.items():
        section_score = data.get("score", 0)
        if section_score < 60:
            recommendations.append(f"Extra practice recommended for {section.title()} section")
    
    return recommendations


# =============================================
# Agent Planner Endpoints
# =============================================

@router.post("/agent-planner/generate")
async def generate_study_plan(
    target_date: str,
    profession: str = "nursing",
    current_user: dict = Depends(get_current_user)
):
    """Generate personalized study plan based on placement test and target date"""
    
    # Get placement test results
    placement = await db.oet_placement_results.find_one(
        {"user_id": current_user["id"]},
        {"_id": 0}
    )
    
    if not placement:
        raise HTTPException(
            status_code=400, 
            detail="Complete placement test first to generate personalized study plan"
        )
    
    # Calculate days until exam
    from datetime import datetime
    try:
        target = datetime.fromisoformat(target_date.replace("Z", "+00:00"))
        days_remaining = (target - datetime.now(timezone.utc)).days
    except:
        days_remaining = 30
    
    # Generate study plan
    study_plan = {
        "id": str(uuid.uuid4()),
        "user_id": current_user["id"],
        "profession": profession,
        "target_date": target_date,
        "days_remaining": days_remaining,
        "placement_band": placement.get("estimated_band", "C"),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "weeks": generate_weekly_plan(days_remaining, placement),
        "daily_goals": {
            "study_hours": 2 if days_remaining > 14 else 3,
            "practice_questions": 20 if days_remaining > 14 else 30,
            "speaking_sessions": 1
        },
        "milestones": [
            {"week": 1, "goal": "Complete all section diagnostics"},
            {"week": 2, "goal": "First full mock exam"},
            {"week": 3, "goal": "Focus on weak areas"},
            {"week": 4, "goal": "Final mock exam and review"}
        ]
    }
    
    await db.oet_study_plans.update_one(
        {"user_id": current_user["id"], "profession": profession},
        {"$set": study_plan},
        upsert=True
    )
    
    return study_plan


def generate_weekly_plan(days: int, placement: dict) -> List[dict]:
    """Generate weekly study plan"""
    
    weeks = max(1, min(12, days // 7))
    plan = []
    
    weak_sections = []
    for section, data in placement.get("section_scores", {}).items():
        if data.get("score", 100) < 70:
            weak_sections.append(section)
    
    for week in range(1, weeks + 1):
        week_plan = {
            "week": week,
            "focus_areas": [],
            "tasks": []
        }
        
        if week == 1:
            week_plan["focus_areas"] = ["Assessment", "Familiarization"]
            week_plan["tasks"] = [
                "Review OET format and requirements",
                "Complete diagnostic tests for each section",
                "Identify personal strengths and weaknesses"
            ]
        elif week == weeks:
            week_plan["focus_areas"] = ["Full Practice", "Review"]
            week_plan["tasks"] = [
                "Take full mock exam under test conditions",
                "Review all answers and feedback",
                "Rest and mental preparation"
            ]
        else:
            if weak_sections:
                focus = weak_sections[week % len(weak_sections)]
                week_plan["focus_areas"] = [focus.title(), "Practice"]
            else:
                week_plan["focus_areas"] = ["General Practice"]
            
            week_plan["tasks"] = [
                "Daily vocabulary building (15 mins)",
                "Section practice (1 hour)",
                "Speaking practice session"
            ]
        
        plan.append(week_plan)
    
    return plan


@router.get("/agent-planner/my-plan")
async def get_my_study_plan(
    profession: str = "nursing",
    current_user: dict = Depends(get_current_user)
):
    """Get user's current study plan"""
    
    plan = await db.oet_study_plans.find_one(
        {"user_id": current_user["id"], "profession": profession},
        {"_id": 0}
    )
    
    if not plan:
        return {
            "has_plan": False,
            "message": "No study plan found. Complete placement test and generate a plan."
        }
    
    return {
        "has_plan": True,
        "plan": plan
    }
