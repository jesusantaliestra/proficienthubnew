"""Exams router - Exam types, mock tests, and exam sessions"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
import uuid

from database import db
from utils.auth import get_current_user

# Import exam utilities from main module
import sys
sys.path.insert(0, '/app/backend')
from exam_questions import get_exam_questions, get_mock_test_config, get_full_exam, get_available_exams, SPEAKING_PROMPTS, WRITING_TASKS, MOCK_TESTS

router = APIRouter(prefix="/exams", tags=["Exams"])

# Exam configuration
EXAM_TYPES = ["toefl", "ielts-academic", "ielts-general", "cambridge", "trinity", "pte-academic", "pte-core", "oet", "toeic", "celpip"]
EXAM_SECTIONS = {
    "toefl": ["reading", "listening", "speaking", "writing"],
    "ielts-academic": ["reading", "listening", "speaking", "writing"],
    "ielts-general": ["reading", "listening", "speaking", "writing"],
    "ielts": ["reading", "listening", "speaking", "writing"],
    "cambridge": ["reading", "writing", "listening", "speaking", "use_of_english"],
    "trinity": ["speaking", "listening", "reading", "writing"],
    "pte-academic": ["speaking_writing", "reading", "listening"],
    "pte-core": ["speaking_writing", "reading", "listening"],
    "pte": ["speaking_writing", "reading", "listening"],
    "oet": ["reading", "listening", "speaking", "writing"],
    "toeic": ["listening", "reading", "speaking", "writing"],
    "celpip": ["listening", "reading", "writing", "speaking"]
}

EXAM_DESCRIPTIONS = {
    "toefl": "Test of English as a Foreign Language - Academic English proficiency",
    "ielts-academic": "IELTS Academic - For university admissions and professional registration",
    "ielts-general": "IELTS General Training - For migration and work experience",
    "cambridge": "Cambridge English Qualifications - Comprehensive assessment",
    "trinity": "Trinity College London GESE/ISE - Communicative English assessment",
    "pte-academic": "PTE Academic - For study abroad and immigration",
    "pte-core": "PTE Core - For Canadian immigration and citizenship",
    "oet": "Occupational English Test - Healthcare professionals",
    "toeic": "Test of English for International Communication - Business English",
    "celpip": "Canadian English Language Proficiency Index Program"
}

# Models
class ExamSubmission(BaseModel):
    section: str
    answers: Dict[str, Any]
    time_spent: int

class ExamAttemptCreate(BaseModel):
    exam_type: str
    section: str
    score: float
    answers: Optional[Dict[str, Any]] = None
    time_spent: Optional[int] = None

@router.get("/types")
async def get_exam_types():
    """Get all available exam types and their configurations"""
    return {
        "exam_types": EXAM_TYPES,
        "sections": EXAM_SECTIONS,
        "total_exams_per_type": 20,
        "descriptions": EXAM_DESCRIPTIONS,
        "mock_tests": {exam: get_mock_test_config(exam) for exam in EXAM_TYPES}
    }

@router.get("/{exam_type}/available")
async def get_available_exam_list(exam_type: str):
    """Get list of all 20 available exams for an exam type"""
    if exam_type not in EXAM_TYPES and not exam_type.startswith(tuple(EXAM_TYPES)):
        raise HTTPException(status_code=400, detail="Invalid exam type")
    base_type = exam_type.split("-")[0] if "-" in exam_type else exam_type
    return get_available_exams(base_type)

@router.get("/{exam_type}/full/{exam_number}")
async def get_complete_exam(
    exam_type: str, 
    exam_number: int, 
    current_user: dict = Depends(get_current_user)
):
    """Get a complete exam (1-20) with all sections"""
    if exam_type not in EXAM_TYPES:
        raise HTTPException(status_code=400, detail="Invalid exam type")
    if exam_number < 1 or exam_number > 20:
        raise HTTPException(status_code=400, detail="Exam number must be between 1 and 20")
    
    exam_data = get_full_exam(exam_type, exam_number)
    
    # Create exam session
    session_id = str(uuid.uuid4())
    await db.exam_sessions.insert_one({
        "id": session_id,
        "user_id": current_user["id"],
        "institution_id": current_user.get("institution_id"),
        "exam_type": exam_type,
        "exam_number": exam_number,
        "started_at": datetime.now(timezone.utc).isoformat(),
        "status": "in_progress",
        "sections_completed": []
    })
    
    exam_data["session_id"] = session_id
    return exam_data

@router.get("/{exam_type}/mock-test")
async def get_full_mock_test(
    exam_type: str, 
    exam_number: int = 1, 
    current_user: dict = Depends(get_current_user)
):
    """Get a complete mock test with all sections"""
    if exam_type not in EXAM_TYPES:
        raise HTTPException(status_code=400, detail="Invalid exam type")
    
    if exam_number < 1 or exam_number > 20:
        exam_number = 1
    
    config = get_mock_test_config(exam_type)
    sections_data = {}
    
    for section_info in config["sections"]:
        section_name = section_info["name"].lower().replace(" ", "_").replace("&", "and")
        simple_section = section_name.split("_")[0] if "_" in section_name else section_name
        
        if simple_section in ["reading", "listening", "writing", "speaking"]:
            sections_data[section_name] = {
                "info": section_info,
                "questions": get_exam_questions(exam_type, simple_section, 5, exam_number)
            }
    
    # Create mock test session
    session_id = str(uuid.uuid4())
    await db.mock_test_sessions.insert_one({
        "id": session_id,
        "user_id": current_user["id"],
        "institution_id": current_user.get("institution_id"),
        "exam_type": exam_type,
        "exam_number": exam_number,
        "started_at": datetime.now(timezone.utc).isoformat(),
        "status": "in_progress",
        "sections_completed": []
    })
    
    return {
        "session_id": session_id,
        "exam_type": exam_type,
        "exam_number": exam_number,
        "config": config,
        "sections": sections_data
    }

@router.get("/{exam_type}/{section}")
async def get_section_questions(
    exam_type: str, 
    section: str, 
    count: int = 10, 
    exam_number: int = 1
):
    """Get questions for a specific exam section"""
    if exam_type not in EXAM_TYPES:
        raise HTTPException(status_code=400, detail="Invalid exam type")
    
    base_type = exam_type.split("-")[0] if "-" in exam_type else exam_type
    valid_sections = EXAM_SECTIONS.get(exam_type, EXAM_SECTIONS.get(base_type, []))
    
    if section not in valid_sections and section not in ["reading", "listening", "writing", "speaking"]:
        raise HTTPException(status_code=400, detail=f"Invalid section for {exam_type}")
    
    return {
        "exam_type": exam_type,
        "section": section,
        "exam_number": exam_number,
        "questions": get_exam_questions(exam_type, section, count, exam_number)
    }

@router.post("/attempt")
async def submit_exam_attempt(
    attempt: ExamAttemptCreate,
    current_user: dict = Depends(get_current_user)
):
    """Submit an exam attempt with score"""
    attempt_doc = {
        "id": str(uuid.uuid4()),
        "user_id": current_user["id"],
        "institution_id": current_user.get("institution_id"),
        "exam_type": attempt.exam_type,
        "section": attempt.section,
        "score": attempt.score,
        "answers": attempt.answers,
        "time_spent": attempt.time_spent,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.exam_attempts.insert_one(attempt_doc)
    
    # Update user progress
    await db.users.update_one(
        {"id": current_user["id"]},
        {
            "$inc": {f"exam_progress.{attempt.exam_type}.{attempt.section}.attempts": 1},
            "$max": {f"exam_progress.{attempt.exam_type}.{attempt.section}.best_score": attempt.score},
            "$set": {f"exam_progress.{attempt.exam_type}.{attempt.section}.last_attempt": datetime.now(timezone.utc).isoformat()}
        }
    )
    
    return {"id": attempt_doc["id"], "message": "Attempt recorded successfully"}

@router.get("/history")
async def get_exam_history(
    exam_type: Optional[str] = None,
    limit: int = 20,
    current_user: dict = Depends(get_current_user)
):
    """Get user's exam history"""
    query = {"user_id": current_user["id"]}
    if exam_type:
        query["exam_type"] = exam_type
    
    attempts = await db.exam_attempts.find(
        query,
        {"_id": 0}
    ).sort("created_at", -1).limit(limit).to_list(limit)
    
    return {"attempts": attempts, "total": len(attempts)}

@router.get("/progress")
async def get_exam_progress(current_user: dict = Depends(get_current_user)):
    """Get user's overall exam progress"""
    user = await db.users.find_one(
        {"id": current_user["id"]},
        {"_id": 0, "exam_progress": 1}
    )
    
    progress = user.get("exam_progress", {}) if user else {}
    
    # Calculate stats
    total_attempts = await db.exam_attempts.count_documents({"user_id": current_user["id"]})
    
    avg_pipeline = [
        {"$match": {"user_id": current_user["id"]}},
        {"$group": {"_id": "$exam_type", "avg_score": {"$avg": "$score"}, "count": {"$sum": 1}}}
    ]
    averages = await db.exam_attempts.aggregate(avg_pipeline).to_list(20)
    
    return {
        "progress": progress,
        "total_attempts": total_attempts,
        "averages_by_exam": {a["_id"]: {"avg_score": round(a["avg_score"], 2), "attempts": a["count"]} for a in averages}
    }

@router.get("/{exam_type}/speaking-prompts")
async def get_speaking_prompts_endpoint(exam_type: str, current_user: dict = Depends(get_current_user)):
    """Get speaking prompts for an exam type"""
    if exam_type not in EXAM_TYPES:
        raise HTTPException(status_code=400, detail="Invalid exam type")
    
    base_type = exam_type.split("-")[0] if "-" in exam_type else exam_type
    prompts = SPEAKING_PROMPTS.get(base_type, SPEAKING_PROMPTS.get("ielts", []))
    
    return {"exam_type": exam_type, "prompts": prompts}

@router.get("/{exam_type}/writing-tasks")
async def get_writing_tasks_endpoint(exam_type: str, current_user: dict = Depends(get_current_user)):
    """Get writing tasks for an exam type"""
    if exam_type not in EXAM_TYPES:
        raise HTTPException(status_code=400, detail="Invalid exam type")
    
    base_type = exam_type.split("-")[0] if "-" in exam_type else exam_type
    tasks = WRITING_TASKS.get(base_type, WRITING_TASKS.get("ielts", []))
    
    return {"exam_type": exam_type, "tasks": tasks}
