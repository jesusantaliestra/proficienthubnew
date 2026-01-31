"""OET Exam System - Complete Mock Exam Platform

This module implements the complete OET exam system with:
- 12 Healthcare professions (Nursing, Medicine, Dentistry, etc.)
- Complete mock exams (Listening, Reading, Writing, Speaking)
- Placement test functionality
- Agent Planner integration
- Mock Exam Coach
"""

from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
import os
import uuid
from dotenv import load_dotenv

load_dotenv()

router = APIRouter(prefix="/oet-exam", tags=["OET Exam System"])

# Database
from motor.motor_asyncio import AsyncIOMotorClient
mongo_client = AsyncIOMotorClient(os.environ.get("MONGO_URL"))
db = mongo_client[os.environ.get("DB_NAME", "eduplat")]

# Auth dependency
from server import get_current_user

# OET Healthcare Professions
OET_PROFESSIONS = {
    "nursing": {
        "name": "Nursing",
        "code": "NUR",
        "description": "For registered nurses and nursing professionals",
        "icon": "stethoscope"
    },
    "medicine": {
        "name": "Medicine", 
        "code": "MED",
        "description": "For doctors and medical practitioners",
        "icon": "user-md"
    },
    "dentistry": {
        "name": "Dentistry",
        "code": "DEN",
        "description": "For dentists and dental professionals",
        "icon": "tooth"
    },
    "pharmacy": {
        "name": "Pharmacy",
        "code": "PHA",
        "description": "For pharmacists and pharmacy technicians",
        "icon": "pills"
    },
    "physiotherapy": {
        "name": "Physiotherapy",
        "code": "PHY",
        "description": "For physiotherapists",
        "icon": "walking"
    },
    "radiography": {
        "name": "Radiography",
        "code": "RAD",
        "description": "For radiographers and imaging professionals",
        "icon": "x-ray"
    },
    "occupational_therapy": {
        "name": "Occupational Therapy",
        "code": "OCC",
        "description": "For occupational therapists",
        "icon": "hands-helping"
    },
    "optometry": {
        "name": "Optometry",
        "code": "OPT",
        "description": "For optometrists and optical professionals",
        "icon": "eye"
    },
    "speech_pathology": {
        "name": "Speech Pathology",
        "code": "SPE",
        "description": "For speech pathologists and therapists",
        "icon": "comments"
    },
    "podiatry": {
        "name": "Podiatry",
        "code": "POD",
        "description": "For podiatrists",
        "icon": "shoe-prints"
    },
    "dietetics": {
        "name": "Dietetics",
        "code": "DIE",
        "description": "For dietitians and nutrition professionals",
        "icon": "apple-alt"
    },
    "veterinary_science": {
        "name": "Veterinary Science",
        "code": "VET",
        "description": "For veterinarians and veterinary nurses",
        "icon": "paw"
    }
}

# OET Exam Structure
OET_EXAM_STRUCTURE = {
    "listening": {
        "name": "Listening",
        "duration_minutes": 50,
        "parts": {
            "A": {"name": "Consultation Extracts", "questions": 24, "type": "note_completion"},
            "B": {"name": "Workplace Extracts", "questions": 6, "type": "multiple_choice"},
            "C": {"name": "Presentations/Interviews", "questions": 12, "type": "multiple_choice"}
        },
        "total_questions": 42
    },
    "reading": {
        "name": "Reading",
        "duration_minutes": 60,
        "parts": {
            "A": {"name": "Expeditious Reading", "questions": 20, "type": "mixed"},
            "B": {"name": "Short Workplace Texts", "questions": 6, "type": "multiple_choice"},
            "C": {"name": "Long Texts", "questions": 16, "type": "multiple_choice"}
        },
        "total_questions": 42
    },
    "writing": {
        "name": "Writing",
        "duration_minutes": 45,
        "parts": {
            "letter": {"name": "Professional Letter", "questions": 1, "type": "letter_writing"}
        },
        "total_questions": 1,
        "word_count": "180-200"
    },
    "speaking": {
        "name": "Speaking",
        "duration_minutes": 20,
        "parts": {
            "roleplay_1": {"name": "Role-Play 1", "prep_time": 3, "duration": 5},
            "roleplay_2": {"name": "Role-Play 2", "prep_time": 3, "duration": 5}
        },
        "total_roleplays": 2
    }
}

# Band Score Descriptions
OET_BANDS = {
    "A": {"score": "450-500", "description": "High level of performance", "cefr": "C2"},
    "B": {"score": "350-440", "description": "Good level of performance", "cefr": "C1"},
    "C+": {"score": "300-340", "description": "Satisfactory level", "cefr": "B2+"},
    "C": {"score": "200-290", "description": "Borderline level", "cefr": "B2"},
    "D": {"score": "100-190", "description": "Below required level", "cefr": "B1"},
    "E": {"score": "0-90", "description": "Very limited ability", "cefr": "A2/B1"}
}


# =============================================
# Pydantic Models
# =============================================

class InstitutionOETConfig(BaseModel):
    placement_test_enabled: bool = True
    placement_test_free: bool = False  # If False, student pays; if True, institution pays
    agent_planner_enabled: bool = True
    ai_tutor_enabled: bool = True
    mock_exam_coach_enabled: bool = True
    professions_offered: List[str] = ["nursing"]  # Which OET professions this institution offers


class StudentOETEnrollment(BaseModel):
    profession: str
    exam_date: Optional[str] = None  # Target exam date
    placement_completed: bool = False
    placement_score: Optional[Dict[str, Any]] = None
    study_plan_generated: bool = False


class StartExamRequest(BaseModel):
    exam_id: str
    section: str  # "listening", "reading", "writing", "speaking"
    part: Optional[str] = None  # "A", "B", "C" or None for full section


class SubmitAnswerRequest(BaseModel):
    session_id: str
    question_id: str
    answer: Any  # string, list, or dict depending on question type


class PlacementTestResult(BaseModel):
    listening_score: float
    reading_score: float
    writing_band: str
    speaking_band: str
    overall_band: str
    strengths: List[str]
    weaknesses: List[str]
    recommended_study_hours: int


# =============================================
# Institution Configuration Endpoints
# =============================================

@router.get("/professions")
async def get_oet_professions():
    """Get list of all OET healthcare professions"""
    return {
        "professions": [
            {
                "id": prof_id,
                **prof_data
            }
            for prof_id, prof_data in OET_PROFESSIONS.items()
        ],
        "total": len(OET_PROFESSIONS)
    }


@router.get("/exam-structure")
async def get_exam_structure():
    """Get OET exam structure and format"""
    return {
        "structure": OET_EXAM_STRUCTURE,
        "bands": OET_BANDS,
        "total_duration_minutes": sum(s["duration_minutes"] for s in OET_EXAM_STRUCTURE.values())
    }


@router.get("/institution/config")
async def get_institution_oet_config(current_user: dict = Depends(get_current_user)):
    """Get institution's OET configuration"""
    
    institution_id = current_user.get("institution_id")
    if not institution_id:
        raise HTTPException(status_code=403, detail="Not associated with an institution")
    
    config = await db.institution_oet_config.find_one(
        {"institution_id": institution_id},
        {"_id": 0}
    )
    
    if not config:
        # Return defaults
        config = {
            "institution_id": institution_id,
            "placement_test_enabled": True,
            "placement_test_free": False,
            "agent_planner_enabled": True,
            "ai_tutor_enabled": True,
            "mock_exam_coach_enabled": True,
            "professions_offered": ["nursing"]
        }
    
    return config


@router.put("/institution/config")
async def update_institution_oet_config(
    config: InstitutionOETConfig,
    current_user: dict = Depends(get_current_user)
):
    """Update institution's OET configuration (institution admin only)"""
    
    if current_user.get("user_type") not in ["institution", "admin"]:
        raise HTTPException(status_code=403, detail="Institution admin access required")
    
    institution_id = current_user.get("institution_id")
    if not institution_id:
        raise HTTPException(status_code=403, detail="Not associated with an institution")
    
    # Validate professions
    for prof in config.professions_offered:
        if prof not in OET_PROFESSIONS:
            raise HTTPException(status_code=400, detail=f"Invalid profession: {prof}")
    
    config_data = config.dict()
    config_data["institution_id"] = institution_id
    config_data["updated_at"] = datetime.now(timezone.utc).isoformat()
    
    await db.institution_oet_config.update_one(
        {"institution_id": institution_id},
        {"$set": config_data},
        upsert=True
    )
    
    return {"message": "Configuration updated", "config": config_data}


# =============================================
# Student Dashboard & Enrollment
# =============================================

@router.get("/student/dashboard")
async def get_student_oet_dashboard(current_user: dict = Depends(get_current_user)):
    """Get student's OET dashboard data"""
    
    user_id = current_user["id"]
    institution_id = current_user.get("institution_id")
    
    # Get student's enrollment
    enrollment = await db.student_oet_enrollment.find_one(
        {"user_id": user_id},
        {"_id": 0}
    )
    
    # Get institution config
    inst_config = await db.institution_oet_config.find_one(
        {"institution_id": institution_id},
        {"_id": 0}
    ) or {}
    
    # Get exam history
    exam_history = await db.oet_exam_attempts.find(
        {"user_id": user_id},
        {"_id": 0}
    ).sort("started_at", -1).limit(10).to_list(10)
    
    # Get study plan if exists
    study_plan = await db.oet_study_plans.find_one(
        {"user_id": user_id, "status": "active"},
        {"_id": 0}
    )
    
    # Get available mocks
    available_mocks = await db.oet_mock_exams.find(
        {
            "profession": enrollment.get("profession", "nursing") if enrollment else "nursing",
            "status": "published"
        },
        {"_id": 0, "questions": 0, "answers": 0}  # Don't send answers
    ).to_list(50)
    
    # Determine what the student needs to do next
    next_steps = []
    
    if not enrollment:
        next_steps.append({
            "action": "enroll",
            "title": "Select Your Profession",
            "description": "Choose your healthcare profession to start your OET preparation"
        })
    elif inst_config.get("placement_test_enabled") and not enrollment.get("placement_completed"):
        next_steps.append({
            "action": "placement_test",
            "title": "Take Placement Test",
            "description": "Complete the placement test to assess your current level",
            "free": inst_config.get("placement_test_free", False)
        })
    elif inst_config.get("agent_planner_enabled") and not enrollment.get("study_plan_generated"):
        next_steps.append({
            "action": "generate_plan",
            "title": "Generate Study Plan",
            "description": "Create a personalized study plan based on your target exam date"
        })
    else:
        next_steps.append({
            "action": "continue_studying",
            "title": "Continue Your Preparation",
            "description": "Access mock exams, materials, and your AI tutor"
        })
    
    return {
        "enrollment": enrollment,
        "institution_config": {
            "placement_test_enabled": inst_config.get("placement_test_enabled", True),
            "placement_test_free": inst_config.get("placement_test_free", False),
            "agent_planner_enabled": inst_config.get("agent_planner_enabled", True),
            "ai_tutor_enabled": inst_config.get("ai_tutor_enabled", True),
            "mock_exam_coach_enabled": inst_config.get("mock_exam_coach_enabled", True)
        },
        "exam_history": exam_history,
        "study_plan": study_plan,
        "available_mocks": available_mocks,
        "next_steps": next_steps,
        "profession_info": OET_PROFESSIONS.get(
            enrollment.get("profession", "nursing") if enrollment else "nursing"
        )
    }


@router.post("/student/enroll")
async def enroll_student_oet(
    profession: str,
    exam_date: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """Enroll student in OET preparation for a specific profession"""
    
    if profession not in OET_PROFESSIONS:
        raise HTTPException(status_code=400, detail=f"Invalid profession: {profession}")
    
    user_id = current_user["id"]
    
    # Check if already enrolled
    existing = await db.student_oet_enrollment.find_one({"user_id": user_id})
    if existing:
        # Update profession
        await db.student_oet_enrollment.update_one(
            {"user_id": user_id},
            {"$set": {
                "profession": profession,
                "exam_date": exam_date,
                "updated_at": datetime.now(timezone.utc).isoformat()
            }}
        )
        return {"message": "Enrollment updated", "profession": profession}
    
    enrollment = {
        "id": str(uuid.uuid4()),
        "user_id": user_id,
        "institution_id": current_user.get("institution_id"),
        "profession": profession,
        "exam_date": exam_date,
        "placement_completed": False,
        "placement_score": None,
        "study_plan_generated": False,
        "enrolled_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.student_oet_enrollment.insert_one(enrollment)
    
    return {
        "message": "Successfully enrolled",
        "enrollment": {k: v for k, v in enrollment.items() if k != "_id"},
        "profession_info": OET_PROFESSIONS[profession]
    }


# =============================================
# Placement Test
# =============================================

@router.post("/placement-test/start")
async def start_placement_test(current_user: dict = Depends(get_current_user)):
    """Start a placement test"""
    
    user_id = current_user["id"]
    institution_id = current_user.get("institution_id")
    
    # Check institution config
    inst_config = await db.institution_oet_config.find_one(
        {"institution_id": institution_id}
    )
    
    if inst_config and not inst_config.get("placement_test_enabled"):
        raise HTTPException(status_code=400, detail="Placement test not enabled for your institution")
    
    # Get student enrollment
    enrollment = await db.student_oet_enrollment.find_one({"user_id": user_id})
    if enrollment and enrollment.get("placement_completed"):
        raise HTTPException(status_code=400, detail="Placement test already completed")
    
    # Create placement test session
    session = {
        "id": str(uuid.uuid4()),
        "user_id": user_id,
        "institution_id": institution_id,
        "type": "placement_test",
        "profession": enrollment.get("profession", "nursing") if enrollment else "nursing",
        "status": "in_progress",
        "started_at": datetime.now(timezone.utc).isoformat(),
        "sections": {
            "listening": {"completed": False, "score": None},
            "reading": {"completed": False, "score": None},
            "writing": {"completed": False, "band": None},
            "speaking": {"completed": False, "band": None}
        },
        "answers": {}
    }
    
    await db.oet_placement_tests.insert_one(session)
    
    return {
        "session_id": session["id"],
        "profession": session["profession"],
        "sections": list(session["sections"].keys()),
        "message": "Placement test started. Complete all sections for your assessment."
    }


@router.post("/placement-test/{session_id}/complete")
async def complete_placement_test(
    session_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Complete placement test and get results"""
    
    user_id = current_user["id"]
    
    session = await db.oet_placement_tests.find_one({
        "id": session_id,
        "user_id": user_id
    })
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Calculate results (simplified scoring)
    sections = session.get("sections", {})
    listening_score = sections.get("listening", {}).get("score", 50)
    reading_score = sections.get("reading", {}).get("score", 50)
    
    # Determine overall band
    avg_score = (listening_score + reading_score) / 2
    if avg_score >= 85:
        overall_band = "A"
    elif avg_score >= 70:
        overall_band = "B"
    elif avg_score >= 55:
        overall_band = "C+"
    elif avg_score >= 40:
        overall_band = "C"
    elif avg_score >= 25:
        overall_band = "D"
    else:
        overall_band = "E"
    
    # Identify strengths and weaknesses
    strengths = []
    weaknesses = []
    
    if listening_score >= 70:
        strengths.append("Listening comprehension")
    else:
        weaknesses.append("Listening comprehension")
    
    if reading_score >= 70:
        strengths.append("Reading comprehension")
    else:
        weaknesses.append("Reading comprehension")
    
    # Calculate recommended study hours
    if overall_band in ["A", "B"]:
        study_hours = 40
    elif overall_band in ["C+", "C"]:
        study_hours = 80
    else:
        study_hours = 120
    
    result = {
        "listening_score": listening_score,
        "reading_score": reading_score,
        "writing_band": sections.get("writing", {}).get("band", "C"),
        "speaking_band": sections.get("speaking", {}).get("band", "C"),
        "overall_band": overall_band,
        "strengths": strengths,
        "weaknesses": weaknesses,
        "recommended_study_hours": study_hours,
        "band_info": OET_BANDS[overall_band]
    }
    
    # Update session
    await db.oet_placement_tests.update_one(
        {"id": session_id},
        {"$set": {
            "status": "completed",
            "completed_at": datetime.now(timezone.utc).isoformat(),
            "result": result
        }}
    )
    
    # Update student enrollment
    await db.student_oet_enrollment.update_one(
        {"user_id": user_id},
        {"$set": {
            "placement_completed": True,
            "placement_score": result,
            "placement_completed_at": datetime.now(timezone.utc).isoformat()
        }}
    )
    
    return {
        "message": "Placement test completed",
        "result": result
    }


# =============================================
# Agent Planner (Study Plan Generator)
# =============================================

@router.post("/study-plan/generate")
async def generate_study_plan(
    exam_date: str,
    current_user: dict = Depends(get_current_user)
):
    """Generate personalized study plan based on placement test and exam date"""
    
    user_id = current_user["id"]
    
    # Get enrollment and placement result
    enrollment = await db.student_oet_enrollment.find_one({"user_id": user_id})
    if not enrollment:
        raise HTTPException(status_code=400, detail="Please enroll first")
    
    placement_result = enrollment.get("placement_score")
    
    # Parse exam date
    try:
        target_date = datetime.fromisoformat(exam_date.replace("Z", "+00:00"))
    except:
        raise HTTPException(status_code=400, detail="Invalid exam date format")
    
    days_until_exam = (target_date - datetime.now(timezone.utc)).days
    if days_until_exam < 7:
        raise HTTPException(status_code=400, detail="Exam date must be at least 7 days away")
    
    # Calculate weekly hours needed
    total_hours = placement_result.get("recommended_study_hours", 80) if placement_result else 80
    weeks_available = max(1, days_until_exam // 7)
    hours_per_week = min(20, total_hours / weeks_available)  # Cap at 20 hours/week
    
    # Generate study plan
    weaknesses = placement_result.get("weaknesses", []) if placement_result else ["All sections"]
    
    plan = {
        "id": str(uuid.uuid4()),
        "user_id": user_id,
        "profession": enrollment.get("profession"),
        "exam_date": exam_date,
        "days_until_exam": days_until_exam,
        "total_study_hours": total_hours,
        "hours_per_week": round(hours_per_week, 1),
        "focus_areas": weaknesses,
        "status": "active",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "weekly_schedule": generate_weekly_schedule(hours_per_week, weaknesses),
        "milestones": generate_milestones(days_until_exam, weaknesses)
    }
    
    await db.oet_study_plans.insert_one(plan)
    
    # Update enrollment
    await db.student_oet_enrollment.update_one(
        {"user_id": user_id},
        {"$set": {
            "study_plan_generated": True,
            "exam_date": exam_date
        }}
    )
    
    return {
        "message": "Study plan generated",
        "plan": {k: v for k, v in plan.items() if k != "_id"}
    }


def generate_weekly_schedule(hours_per_week: float, focus_areas: List[str]) -> Dict[str, Any]:
    """Generate weekly study schedule"""
    
    sections = ["listening", "reading", "writing", "speaking"]
    
    # Allocate more time to weak areas
    schedule = {}
    base_hours = hours_per_week / 4
    
    for section in sections:
        is_weak = any(section.lower() in fa.lower() for fa in focus_areas)
        schedule[section] = {
            "hours": round(base_hours * 1.5 if is_weak else base_hours * 0.75, 1),
            "priority": "high" if is_weak else "normal",
            "activities": get_section_activities(section)
        }
    
    return schedule


def generate_milestones(days: int, focus_areas: List[str]) -> List[Dict[str, Any]]:
    """Generate study milestones"""
    
    milestones = []
    
    # Week 1
    milestones.append({
        "week": 1,
        "goal": "Complete diagnostic exercises for all sections",
        "activities": ["Review OET format", "Practice timing strategies", "Identify question types"]
    })
    
    # Middle weeks - focus on weaknesses
    if days > 14:
        milestones.append({
            "week": 2,
            "goal": f"Intensive practice on weak areas: {', '.join(focus_areas)}",
            "activities": ["Daily practice tests", "Review mistakes", "Build vocabulary"]
        })
    
    # Final week
    if days > 7:
        milestones.append({
            "week": days // 7,
            "goal": "Full mock exams under timed conditions",
            "activities": ["Complete 2 full mocks", "Review all answers", "Final revision"]
        })
    
    return milestones


def get_section_activities(section: str) -> List[str]:
    """Get recommended activities for each section"""
    
    activities = {
        "listening": [
            "Note-taking practice",
            "Medical terminology listening",
            "Speed comprehension drills",
            "Accent familiarization"
        ],
        "reading": [
            "Skimming and scanning practice",
            "Medical text analysis",
            "Time management exercises",
            "Vocabulary building"
        ],
        "writing": [
            "Letter structure practice",
            "Case note summarization",
            "Grammar and punctuation review",
            "Timed writing exercises"
        ],
        "speaking": [
            "Role-play practice",
            "Medical vocabulary pronunciation",
            "Communication strategies",
            "Recording and self-review"
        ]
    }
    
    return activities.get(section, [])


# =============================================
# Mock Exam Endpoints
# =============================================

@router.get("/mocks")
async def get_available_mocks(
    profession: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """Get available mock exams"""
    
    query = {"status": "published"}
    
    if profession:
        query["profession"] = profession
    else:
        # Get student's profession
        enrollment = await db.student_oet_enrollment.find_one(
            {"user_id": current_user["id"]}
        )
        if enrollment:
            query["profession"] = enrollment.get("profession", "nursing")
    
    mocks = await db.oet_mock_exams.find(
        query,
        {"_id": 0, "questions": 0, "answers": 0, "audio_scripts": 0}
    ).to_list(50)
    
    return {"mocks": mocks, "total": len(mocks)}


@router.post("/mock/{mock_id}/start")
async def start_mock_exam(
    mock_id: str,
    section: Optional[str] = None,  # None = full exam
    current_user: dict = Depends(get_current_user)
):
    """Start a mock exam (full or by section)"""
    
    user_id = current_user["id"]
    
    # Get mock exam
    mock = await db.oet_mock_exams.find_one({"id": mock_id})
    if not mock:
        raise HTTPException(status_code=404, detail="Mock exam not found")
    
    # Create attempt session
    session = {
        "id": str(uuid.uuid4()),
        "user_id": user_id,
        "mock_id": mock_id,
        "mock_name": mock.get("name"),
        "profession": mock.get("profession"),
        "mode": "section" if section else "full",
        "current_section": section or "listening",
        "status": "in_progress",
        "started_at": datetime.now(timezone.utc).isoformat(),
        "sections_completed": [],
        "answers": {},
        "scores": {}
    }
    
    await db.oet_exam_attempts.insert_one(session)
    
    return {
        "session_id": session["id"],
        "mock_id": mock_id,
        "mock_name": mock.get("name"),
        "mode": session["mode"],
        "current_section": session["current_section"],
        "exam_structure": OET_EXAM_STRUCTURE,
        "message": f"Mock exam started. {'Starting with ' + section if section else 'Full exam mode'}"
    }


@router.get("/mock/session/{session_id}")
async def get_exam_session(
    session_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get current exam session details"""
    
    session = await db.oet_exam_attempts.find_one(
        {"id": session_id, "user_id": current_user["id"]},
        {"_id": 0}
    )
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return session


@router.post("/mock/session/{session_id}/submit-section")
async def submit_exam_section(
    session_id: str,
    section: str,
    answers: Dict[str, Any],
    current_user: dict = Depends(get_current_user)
):
    """Submit answers for a section"""
    
    session = await db.oet_exam_attempts.find_one({
        "id": session_id,
        "user_id": current_user["id"]
    })
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Store answers
    session_answers = session.get("answers", {})
    session_answers[section] = answers
    
    # Mark section as completed
    sections_completed = session.get("sections_completed", [])
    if section not in sections_completed:
        sections_completed.append(section)
    
    # Update session
    await db.oet_exam_attempts.update_one(
        {"id": session_id},
        {"$set": {
            "answers": session_answers,
            "sections_completed": sections_completed,
            "last_activity": datetime.now(timezone.utc).isoformat()
        }}
    )
    
    return {
        "message": f"Section {section} submitted",
        "sections_completed": sections_completed,
        "sections_remaining": [s for s in ["listening", "reading", "writing", "speaking"] if s not in sections_completed]
    }


@router.post("/mock/session/{session_id}/complete")
async def complete_mock_exam(
    session_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Complete mock exam and get results"""
    
    session = await db.oet_exam_attempts.find_one({
        "id": session_id,
        "user_id": current_user["id"]
    })
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Get mock exam for answers
    mock = await db.oet_mock_exams.find_one({"id": session.get("mock_id")})
    
    # Calculate scores (simplified)
    scores = {
        "listening": {"raw": 0, "percentage": 0, "band": "C"},
        "reading": {"raw": 0, "percentage": 0, "band": "C"},
        "writing": {"band": "C", "feedback": ""},
        "speaking": {"band": "C", "feedback": ""}
    }
    
    # Update session
    await db.oet_exam_attempts.update_one(
        {"id": session_id},
        {"$set": {
            "status": "completed",
            "completed_at": datetime.now(timezone.utc).isoformat(),
            "scores": scores
        }}
    )
    
    return {
        "message": "Mock exam completed",
        "session_id": session_id,
        "scores": scores,
        "overall_feedback": "Review your answers and focus on areas needing improvement."
    }


# =============================================
# Mock Exam Coach (In-Exam Help)
# =============================================

@router.post("/mock/coach/ask")
async def ask_mock_coach(
    session_id: str,
    question: str,
    context: Optional[Dict[str, Any]] = None,
    current_user: dict = Depends(get_current_user)
):
    """Ask the Mock Exam Coach for help during an exam"""
    
    session = await db.oet_exam_attempts.find_one({
        "id": session_id,
        "user_id": current_user["id"]
    })
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Check if coach is enabled
    institution_id = current_user.get("institution_id")
    inst_config = await db.institution_oet_config.find_one({"institution_id": institution_id})
    
    if inst_config and not inst_config.get("mock_exam_coach_enabled", True):
        raise HTTPException(status_code=403, detail="Mock Exam Coach not enabled for your institution")
    
    # Generate coach response (would use LLM in production)
    coach_response = generate_coach_response(question, context, session.get("current_section"))
    
    # Log the interaction
    await db.oet_coach_interactions.insert_one({
        "id": str(uuid.uuid4()),
        "session_id": session_id,
        "user_id": current_user["id"],
        "question": question,
        "response": coach_response,
        "context": context,
        "timestamp": datetime.now(timezone.utc).isoformat()
    })
    
    return {
        "response": coach_response,
        "note": "The coach provides guidance but cannot give you answers directly."
    }


def generate_coach_response(question: str, context: Dict[str, Any], section: str) -> str:
    """Generate coach response (simplified - would use LLM in production)"""
    
    question_lower = question.lower()
    
    # Generic helpful responses based on keywords
    if "time" in question_lower or "how long" in question_lower:
        return f"For the {section} section, manage your time carefully. In Reading Part A, spend about 15 minutes. For multiple choice questions, aim for about 1 minute per question."
    
    elif "confused" in question_lower or "don't understand" in question_lower:
        return "Take a breath and read the question again carefully. Look for key words that indicate what type of answer is needed. If it's a multiple choice, eliminate obviously wrong options first."
    
    elif "listening" in question_lower and ("missed" in question_lower or "hear" in question_lower):
        return "In OET Listening, you only hear each recording once. If you missed something, make your best guess based on context and move on. Don't let one question affect the next."
    
    elif "writing" in question_lower or "letter" in question_lower:
        return "Remember the key elements: appropriate salutation, clear purpose statement, relevant clinical information organized logically, and professional closing. Stay within 180-200 words."
    
    elif "speaking" in question_lower or "role-play" in question_lower:
        return "In the speaking role-play, focus on building rapport, acknowledging the patient's concerns, providing clear information, and checking understanding. Use appropriate medical terminology but explain it if needed."
    
    else:
        return f"For the {section} section, read each question carefully, manage your time, and answer what is asked. If unsure, use elimination strategies for multiple choice, or make your best informed guess."


# =============================================
# Initialize Exam Data
# =============================================

@router.post("/admin/seed-exam-data")
async def seed_oet_exam_data(current_user: dict = Depends(get_current_user)):
    """Seed the database with OET exam data (admin only)"""
    
    if current_user.get("user_type") not in ["admin"]:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Import exam data
    from oet_exam_data import OET_NUR_013_EXAM, EXAM_METADATA
    
    # Check if exam already exists
    existing = await db.oet_mock_exams.find_one({"id": EXAM_METADATA["exam_id"]})
    if existing:
        return {"message": "Exam data already exists", "exam_id": EXAM_METADATA["exam_id"]}
    
    # Create mock exam document
    mock_exam = {
        "id": EXAM_METADATA["exam_id"],
        "name": EXAM_METADATA["title"],
        "profession": EXAM_METADATA["profession"],
        "version": EXAM_METADATA["version"],
        "description": EXAM_METADATA["description"],
        "status": "published",
        "difficulty": "Standard",
        "total_questions": EXAM_METADATA["total_questions"],
        "exam_data": OET_NUR_013_EXAM,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.oet_mock_exams.insert_one(mock_exam)
    
    return {
        "message": "OET exam data seeded successfully",
        "exam_id": EXAM_METADATA["exam_id"],
        "profession": EXAM_METADATA["profession"]
    }


@router.get("/mocks/available")
async def get_available_mocks_public():
    """Get list of available mock exams (public endpoint for dashboard)"""
    
    # Return hardcoded list of available mocks for the dashboard
    mocks = [
        {
            "id": "NUR-013-v2",
            "name": "OET Nursing Mock NUR-013",
            "version": "2.0",
            "status": "available",
            "difficulty": "Standard",
            "profession": "nursing",
            "description": "Complete OET mock exam for nursing professionals",
            "total_duration": 175,
            "sections": {
                "listening": {"duration": 50, "questions": 42},
                "reading": {"duration": 60, "questions": 42},
                "writing": {"duration": 45, "questions": 1},
                "speaking": {"duration": 20, "questions": 2}
            }
        },
        {
            "id": "NUR-014",
            "name": "OET Nursing Mock NUR-014",
            "version": "1.0",
            "status": "locked",
            "difficulty": "Standard",
            "profession": "nursing",
            "description": "Additional practice exam",
            "total_duration": 175
        },
        {
            "id": "NUR-015",
            "name": "OET Nursing Mock NUR-015",
            "version": "1.0",
            "status": "locked",
            "difficulty": "Advanced",
            "profession": "nursing",
            "description": "Challenging practice exam",
            "total_duration": 175
        }
    ]
    
    return {"mocks": mocks, "total": len(mocks)}


@router.get("/mock/{mock_id}/content")
async def get_mock_exam_content(
    mock_id: str,
    section: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """Get mock exam content for a specific section or full exam"""
    
    # Import exam data
    from oet_exam_data import OET_NUR_013_EXAM
    
    if mock_id != "NUR-013-v2":
        raise HTTPException(status_code=404, detail="Mock exam not found or locked")
    
    exam_data = OET_NUR_013_EXAM
    
    if section:
        if section not in ["listening", "reading", "writing", "speaking"]:
            raise HTTPException(status_code=400, detail="Invalid section")
        
        return {
            "mock_id": mock_id,
            "section": section,
            "content": exam_data.get(section)
        }
    
    # Return structure without full content for overview
    return {
        "mock_id": mock_id,
        "metadata": exam_data["metadata"],
        "sections": {
            "listening": {
                "parts": ["Part A", "Part B", "Part C"],
                "total_questions": 42,
                "duration": 50
            },
            "reading": {
                "parts": ["Part A", "Part B", "Part C"],
                "total_questions": 42,
                "duration": 60
            },
            "writing": {
                "parts": ["Professional Letter"],
                "total_questions": 1,
                "duration": 45
            },
            "speaking": {
                "parts": ["Role-Play 1", "Role-Play 2"],
                "total_questions": 2,
                "duration": 20
            }
        }
    }
