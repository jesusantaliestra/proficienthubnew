"""
Agent Planner - AI-Powered Study Plan Generator

Creates personalized study plans based on:
- Placement test results
- Target exam date
- Student's availability
- Specific weaknesses identified
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime, timezone, timedelta
import os
import json

router = APIRouter(prefix="/agent-planner", tags=["Agent Planner"])

# Database
from motor.motor_asyncio import AsyncIOMotorClient
mongo_client = AsyncIOMotorClient(os.environ.get("MONGO_URL"))
db = mongo_client[os.environ.get("DB_NAME", "eduplat")]

# Auth
from server import get_current_user


# =============================================
# Models
# =============================================

class StudyPlanRequest(BaseModel):
    """Request to generate a study plan"""
    exam_type: str  # OET, IELTS, TOEFL, etc.
    profession: Optional[str] = None  # For OET
    target_date: str  # ISO date format
    hours_per_week: int = 10
    placement_test_id: Optional[str] = None
    focus_areas: List[str] = []  # listening, reading, writing, speaking
    current_level: Optional[str] = None  # A1, A2, B1, B2, C1, C2


class StudyPlanDay(BaseModel):
    """A single day in the study plan"""
    date: str
    day_name: str
    tasks: List[dict]
    total_minutes: int
    focus_skill: str


class StudyPlan(BaseModel):
    """Complete study plan"""
    id: str
    student_id: str
    exam_type: str
    target_date: str
    current_level: str
    target_level: str
    total_weeks: int
    hours_per_week: int
    weekly_plans: List[dict]
    milestones: List[dict]
    recommendations: List[str]


# Skill areas by exam type
EXAM_SKILLS = {
    "OET": ["listening", "reading", "writing", "speaking"],
    "IELTS_ACADEMIC": ["listening", "reading", "writing", "speaking"],
    "IELTS_GENERAL": ["listening", "reading", "writing", "speaking"],
    "TOEFL": ["listening", "reading", "writing", "speaking"],
    "PTE": ["listening", "reading", "writing", "speaking"],
    "CAMBRIDGE_FCE": ["reading_use", "writing", "listening", "speaking"],
    "CAMBRIDGE_CAE": ["reading_use", "writing", "listening", "speaking"],
}

# Activity templates
ACTIVITIES = {
    "listening": [
        {"name": "Práctica de escucha activa", "duration": 30, "type": "practice"},
        {"name": "Dictado médico", "duration": 20, "type": "exercise"},
        {"name": "Transcripción de conversaciones", "duration": 25, "type": "exercise"},
        {"name": "Mock listening test", "duration": 45, "type": "mock"},
    ],
    "reading": [
        {"name": "Lectura de casos clínicos", "duration": 30, "type": "practice"},
        {"name": "Skimming y scanning", "duration": 20, "type": "technique"},
        {"name": "Vocabulario médico", "duration": 25, "type": "vocabulary"},
        {"name": "Mock reading test", "duration": 60, "type": "mock"},
    ],
    "writing": [
        {"name": "Carta de referencia", "duration": 45, "type": "practice"},
        {"name": "Notas de alta", "duration": 30, "type": "practice"},
        {"name": "Revisión de gramática", "duration": 20, "type": "grammar"},
        {"name": "Mock writing test", "duration": 45, "type": "mock"},
    ],
    "speaking": [
        {"name": "Roleplay con paciente", "duration": 20, "type": "practice"},
        {"name": "Expresiones médicas comunes", "duration": 15, "type": "vocabulary"},
        {"name": "Pronunciación", "duration": 15, "type": "pronunciation"},
        {"name": "Mock speaking test", "duration": 20, "type": "mock"},
    ]
}


# =============================================
# Plan Generation
# =============================================

async def generate_study_plan_with_ai(request: StudyPlanRequest, student_id: str) -> dict:
    """Generate a personalized study plan using AI"""
    from emergentintegrations.llm.chat import LlmChat, UserMessage
    
    api_key = os.environ.get("EMERGENT_LLM_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="AI service not configured")
    
    # Calculate weeks until exam
    target = datetime.fromisoformat(request.target_date.replace('Z', '+00:00'))
    now = datetime.now(timezone.utc)
    weeks_until_exam = max(1, (target - now).days // 7)
    
    # Get placement test results if available
    placement_results = None
    if request.placement_test_id:
        placement = await db.placement_tests.find_one(
            {"id": request.placement_test_id, "student_id": student_id},
            {"_id": 0}
        )
        if placement:
            placement_results = placement.get("results", {})
    
    # Build context for AI
    context = {
        "exam_type": request.exam_type,
        "profession": request.profession,
        "weeks_available": weeks_until_exam,
        "hours_per_week": request.hours_per_week,
        "current_level": request.current_level or "B1",
        "focus_areas": request.focus_areas or ["all"],
        "placement_results": placement_results,
        "skills": EXAM_SKILLS.get(request.exam_type, ["listening", "reading", "writing", "speaking"])
    }
    
    chat = LlmChat(
        api_key=api_key,
        session_id=f"planner-{student_id}",
        system_message="""You are an expert English exam preparation coach.
Create a detailed, realistic study plan based on the student's context.
Be specific with activities and time allocations.
Consider the student's current level and target exam requirements.
Return your response as valid JSON."""
    ).with_model("openai", "gpt-4.1-mini")
    
    prompt = f"""Create a study plan for a student preparing for {request.exam_type}.

Context:
- Weeks until exam: {weeks_until_exam}
- Hours per week available: {request.hours_per_week}
- Current level: {request.current_level or 'B1'}
- Focus areas: {', '.join(request.focus_areas) if request.focus_areas else 'All skills'}
{f"- Profession (OET): {request.profession}" if request.profession else ""}
{f"- Placement test weaknesses: {json.dumps(placement_results)}" if placement_results else ""}

Return a JSON object with this structure:
{{
    "target_level": "B2 or C1",
    "weekly_focus": ["skill for each week"],
    "milestones": [
        {{"week": 1, "goal": "description", "assessment": "how to verify"}}
    ],
    "recommendations": ["3-5 specific recommendations"],
    "intensity": "low/medium/high",
    "estimated_improvement": "description of expected progress"
}}"""
    
    try:
        response = await chat.send_message(UserMessage(text=prompt))
        
        # Parse JSON response
        response_text = response.strip()
        if response_text.startswith("```"):
            lines = response_text.split("\n")
            response_text = "\n".join(lines[1:-1])
        
        ai_plan = json.loads(response_text)
        return ai_plan
        
    except Exception as e:
        # Return default plan if AI fails
        return {
            "target_level": "B2",
            "weekly_focus": ["Foundation"] * min(4, weeks_until_exam) + ["Practice"] * max(0, weeks_until_exam - 4),
            "milestones": [
                {"week": weeks_until_exam // 2, "goal": "Complete 50% of practice materials", "assessment": "Mock test"},
                {"week": weeks_until_exam, "goal": "Ready for exam", "assessment": "Final mock"}
            ],
            "recommendations": [
                "Practice daily for better retention",
                "Focus on your weakest skill first",
                "Take mock tests every 2 weeks"
            ],
            "intensity": "medium",
            "estimated_improvement": "1 CEFR level improvement expected"
        }


def generate_weekly_schedule(
    week_number: int,
    hours_per_week: int,
    focus_skill: str,
    exam_type: str
) -> List[dict]:
    """Generate a weekly schedule with specific activities"""
    
    skills = EXAM_SKILLS.get(exam_type, ["listening", "reading", "writing", "speaking"])
    minutes_per_week = hours_per_week * 60
    
    # Distribute time across skills (focus skill gets 40%, others share 60%)
    skill_minutes = {}
    for skill in skills:
        if skill == focus_skill:
            skill_minutes[skill] = int(minutes_per_week * 0.4)
        else:
            skill_minutes[skill] = int(minutes_per_week * 0.6 / (len(skills) - 1))
    
    # Generate daily tasks
    days = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
    study_days = days[:5] if hours_per_week <= 10 else days[:6]  # 5-6 study days
    
    daily_schedule = []
    remaining_minutes = dict(skill_minutes)
    
    for day in study_days:
        day_tasks = []
        day_minutes = 0
        target_daily = minutes_per_week // len(study_days)
        
        for skill in skills:
            if remaining_minutes.get(skill, 0) <= 0:
                continue
                
            activities = ACTIVITIES.get(skill, [])
            if activities:
                activity = activities[week_number % len(activities)]
                duration = min(activity["duration"], remaining_minutes[skill])
                
                day_tasks.append({
                    "skill": skill,
                    "activity": activity["name"],
                    "duration": duration,
                    "type": activity["type"]
                })
                
                remaining_minutes[skill] -= duration
                day_minutes += duration
                
                if day_minutes >= target_daily:
                    break
        
        daily_schedule.append({
            "day": day,
            "tasks": day_tasks,
            "total_minutes": day_minutes
        })
    
    return daily_schedule


# =============================================
# API Endpoints
# =============================================

@router.post("/generate")
async def generate_plan(
    request: StudyPlanRequest,
    current_user: dict = Depends(get_current_user)
):
    """Generate a personalized study plan"""
    import uuid
    
    student_id = current_user["id"]
    
    # Generate AI-powered plan
    ai_plan = await generate_study_plan_with_ai(request, student_id)
    
    # Calculate weeks
    target = datetime.fromisoformat(request.target_date.replace('Z', '+00:00'))
    now = datetime.now(timezone.utc)
    weeks_until_exam = max(1, (target - now).days // 7)
    
    # Generate weekly schedules
    weekly_plans = []
    skills = EXAM_SKILLS.get(request.exam_type, ["listening", "reading", "writing", "speaking"])
    
    for week in range(weeks_until_exam):
        focus_index = week % len(skills)
        focus_skill = request.focus_areas[focus_index % len(request.focus_areas)] if request.focus_areas else skills[focus_index]
        
        weekly_schedule = generate_weekly_schedule(
            week,
            request.hours_per_week,
            focus_skill,
            request.exam_type
        )
        
        weekly_plans.append({
            "week_number": week + 1,
            "focus_skill": focus_skill,
            "theme": ai_plan.get("weekly_focus", ["General"])[min(week, len(ai_plan.get("weekly_focus", [])) - 1)],
            "daily_schedule": weekly_schedule
        })
    
    # Create plan document
    plan_id = str(uuid.uuid4())
    plan = {
        "id": plan_id,
        "student_id": student_id,
        "exam_type": request.exam_type,
        "profession": request.profession,
        "target_date": request.target_date,
        "current_level": request.current_level or "B1",
        "target_level": ai_plan.get("target_level", "B2"),
        "total_weeks": weeks_until_exam,
        "hours_per_week": request.hours_per_week,
        "weekly_plans": weekly_plans,
        "milestones": ai_plan.get("milestones", []),
        "recommendations": ai_plan.get("recommendations", []),
        "intensity": ai_plan.get("intensity", "medium"),
        "estimated_improvement": ai_plan.get("estimated_improvement", ""),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "status": "active"
    }
    
    # Save to database
    await db.study_plans.insert_one(plan)
    plan.pop("_id", None)
    
    return {"plan": plan}


@router.get("/my-plans")
async def get_my_plans(current_user: dict = Depends(get_current_user)):
    """Get all study plans for current user"""
    
    plans = await db.study_plans.find(
        {"student_id": current_user["id"]},
        {"_id": 0}
    ).sort("created_at", -1).to_list(20)
    
    return {"plans": plans, "count": len(plans)}


@router.get("/plans/{plan_id}")
async def get_plan(plan_id: str, current_user: dict = Depends(get_current_user)):
    """Get a specific study plan"""
    
    plan = await db.study_plans.find_one(
        {"id": plan_id, "student_id": current_user["id"]},
        {"_id": 0}
    )
    
    if not plan:
        raise HTTPException(status_code=404, detail="Plan no encontrado")
    
    return {"plan": plan}


@router.put("/plans/{plan_id}/progress")
async def update_progress(
    plan_id: str,
    week: int,
    day: str,
    completed_tasks: List[str],
    current_user: dict = Depends(get_current_user)
):
    """Update progress on a study plan"""
    
    result = await db.study_plans.update_one(
        {"id": plan_id, "student_id": current_user["id"]},
        {
            "$push": {
                "progress": {
                    "week": week,
                    "day": day,
                    "completed_tasks": completed_tasks,
                    "completed_at": datetime.now(timezone.utc).isoformat()
                }
            }
        }
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Plan no encontrado")
    
    return {"message": "Progreso actualizado"}


@router.delete("/plans/{plan_id}")
async def delete_plan(plan_id: str, current_user: dict = Depends(get_current_user)):
    """Delete a study plan"""
    
    result = await db.study_plans.delete_one(
        {"id": plan_id, "student_id": current_user["id"]}
    )
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Plan no encontrado")
    
    return {"message": "Plan eliminado"}
