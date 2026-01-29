"""
Public API v1 - Exams Endpoints
Access exam data and results via API
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone, timedelta

import sys
sys.path.append('/app/backend')
from database import db
from .auth_middleware import require_read, require_write

router = APIRouter(prefix="/exams", tags=["Exams API"])

# Models
class ExamAttemptResponse(BaseModel):
    id: str
    student_id: str
    exam_type: str
    exam_number: int
    score: float
    section_scores: Dict[str, float]
    status: str
    created_at: str
    completed_at: Optional[str]
    time_spent_seconds: Optional[int]

class ExamStatsResponse(BaseModel):
    exam_type: str
    total_attempts: int
    average_score: float
    highest_score: float
    lowest_score: float
    pass_rate: float
    section_averages: Dict[str, float]

class PaginatedExamAttemptsResponse(BaseModel):
    data: List[ExamAttemptResponse]
    total: int
    page: int
    per_page: int
    total_pages: int

# Endpoints
@router.get("/attempts", response_model=PaginatedExamAttemptsResponse)
async def list_exam_attempts(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    student_id: Optional[str] = None,
    institution_id: Optional[str] = None,
    exam_type: Optional[str] = None,
    status: Optional[str] = None,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    api_auth: dict = Depends(require_read)
):
    """
    List exam attempts with filtering.
    
    - **student_id**: Filter by student
    - **institution_id**: Filter by institution
    - **exam_type**: Filter by exam type
    - **status**: Filter by status (completed, in_progress, abandoned)
    - **from_date**: Filter attempts after this date (ISO format)
    - **to_date**: Filter attempts before this date (ISO format)
    """
    query = {}
    
    if student_id:
        query["user_id"] = student_id
    if institution_id:
        query["institution_id"] = institution_id
    if exam_type:
        query["exam_type"] = exam_type
    if status:
        query["status"] = status
    if from_date:
        query["created_at"] = {"$gte": from_date}
    if to_date:
        if "created_at" in query:
            query["created_at"]["$lte"] = to_date
        else:
            query["created_at"] = {"$lte": to_date}
    
    total = await db.exam_attempts.count_documents(query)
    total_pages = (total + per_page - 1) // per_page
    
    skip = (page - 1) * per_page
    attempts = await db.exam_attempts.find(
        query,
        {"_id": 0}
    ).sort("created_at", -1).skip(skip).limit(per_page).to_list(per_page)
    
    result = [
        ExamAttemptResponse(
            id=a["id"],
            student_id=a.get("user_id", ""),
            exam_type=a.get("exam_type", ""),
            exam_number=a.get("exam_number", 1),
            score=a.get("score", 0),
            section_scores=a.get("section_scores", {}),
            status=a.get("status", "completed"),
            created_at=a.get("created_at", ""),
            completed_at=a.get("completed_at"),
            time_spent_seconds=a.get("time_spent")
        )
        for a in attempts
    ]
    
    return PaginatedExamAttemptsResponse(
        data=result,
        total=total,
        page=page,
        per_page=per_page,
        total_pages=total_pages
    )

@router.get("/attempts/{attempt_id}", response_model=ExamAttemptResponse)
async def get_exam_attempt(
    attempt_id: str,
    api_auth: dict = Depends(require_read)
):
    """Get a single exam attempt by ID"""
    attempt = await db.exam_attempts.find_one(
        {"id": attempt_id},
        {"_id": 0}
    )
    
    if not attempt:
        raise HTTPException(status_code=404, detail="Exam attempt not found")
    
    return ExamAttemptResponse(
        id=attempt["id"],
        student_id=attempt.get("user_id", ""),
        exam_type=attempt.get("exam_type", ""),
        exam_number=attempt.get("exam_number", 1),
        score=attempt.get("score", 0),
        section_scores=attempt.get("section_scores", {}),
        status=attempt.get("status", "completed"),
        created_at=attempt.get("created_at", ""),
        completed_at=attempt.get("completed_at"),
        time_spent_seconds=attempt.get("time_spent")
    )

@router.get("/stats", response_model=List[ExamStatsResponse])
async def get_exam_statistics(
    institution_id: Optional[str] = None,
    period_days: int = Query(30, ge=1, le=365),
    api_auth: dict = Depends(require_read)
):
    """
    Get exam statistics aggregated by exam type.
    
    - **institution_id**: Filter by institution
    - **period_days**: Period to analyze (default: 30 days)
    """
    start_date = (datetime.now(timezone.utc) - timedelta(days=period_days)).isoformat()
    
    match_stage = {"created_at": {"$gte": start_date}}
    if institution_id:
        match_stage["institution_id"] = institution_id
    
    pipeline = [
        {"$match": match_stage},
        {"$group": {
            "_id": "$exam_type",
            "total_attempts": {"$sum": 1},
            "avg_score": {"$avg": "$score"},
            "max_score": {"$max": "$score"},
            "min_score": {"$min": "$score"},
            "section_scores": {"$push": "$section_scores"}
        }}
    ]
    
    stats = await db.exam_attempts.aggregate(pipeline).to_list(20)
    
    result = []
    for s in stats:
        if not s["_id"]:
            continue
            
        # Calculate pass rate (assuming 60% is passing)
        pass_count = await db.exam_attempts.count_documents({
            "exam_type": s["_id"],
            "score": {"$gte": 60},
            "created_at": {"$gte": start_date},
            **({"institution_id": institution_id} if institution_id else {})
        })
        pass_rate = (pass_count / s["total_attempts"] * 100) if s["total_attempts"] > 0 else 0
        
        # Calculate section averages
        section_totals = {}
        section_counts = {}
        for scores in s["section_scores"]:
            if scores:
                for section, score in scores.items():
                    if section not in section_totals:
                        section_totals[section] = 0
                        section_counts[section] = 0
                    section_totals[section] += score
                    section_counts[section] += 1
        
        section_averages = {
            section: round(section_totals[section] / section_counts[section], 2)
            for section in section_totals
        }
        
        result.append(ExamStatsResponse(
            exam_type=s["_id"],
            total_attempts=s["total_attempts"],
            average_score=round(s["avg_score"], 2) if s["avg_score"] else 0,
            highest_score=round(s["max_score"], 2) if s["max_score"] else 0,
            lowest_score=round(s["min_score"], 2) if s["min_score"] else 0,
            pass_rate=round(pass_rate, 2),
            section_averages=section_averages
        ))
    
    return result

@router.get("/types")
async def get_exam_types(
    api_auth: dict = Depends(require_read)
):
    """Get list of available exam types with configuration"""
    exam_types = {
        "toefl": {
            "name": "TOEFL",
            "full_name": "Test of English as a Foreign Language",
            "sections": ["reading", "listening", "speaking", "writing"],
            "max_score": 120,
            "duration_minutes": 180
        },
        "ielts-academic": {
            "name": "IELTS Academic",
            "full_name": "International English Language Testing System - Academic",
            "sections": ["reading", "listening", "speaking", "writing"],
            "max_score": 9,
            "duration_minutes": 175
        },
        "ielts-general": {
            "name": "IELTS General",
            "full_name": "International English Language Testing System - General Training",
            "sections": ["reading", "listening", "speaking", "writing"],
            "max_score": 9,
            "duration_minutes": 175
        },
        "cambridge": {
            "name": "Cambridge",
            "full_name": "Cambridge English Qualifications",
            "sections": ["reading", "writing", "listening", "speaking", "use_of_english"],
            "max_score": 230,
            "duration_minutes": 240
        },
        "pte-academic": {
            "name": "PTE Academic",
            "full_name": "Pearson Test of English - Academic",
            "sections": ["speaking_writing", "reading", "listening"],
            "max_score": 90,
            "duration_minutes": 180
        },
        "pte-core": {
            "name": "PTE Core",
            "full_name": "Pearson Test of English - Core",
            "sections": ["speaking_writing", "reading", "listening"],
            "max_score": 90,
            "duration_minutes": 120
        },
        "oet": {
            "name": "OET",
            "full_name": "Occupational English Test",
            "sections": ["reading", "listening", "speaking", "writing"],
            "max_score": 500,
            "duration_minutes": 180
        },
        "toeic": {
            "name": "TOEIC",
            "full_name": "Test of English for International Communication",
            "sections": ["listening", "reading", "speaking", "writing"],
            "max_score": 990,
            "duration_minutes": 150
        },
        "celpip": {
            "name": "CELPIP",
            "full_name": "Canadian English Language Proficiency Index Program",
            "sections": ["listening", "reading", "writing", "speaking"],
            "max_score": 12,
            "duration_minutes": 180
        },
        "trinity": {
            "name": "Trinity",
            "full_name": "Trinity College London GESE/ISE",
            "sections": ["speaking", "listening", "reading", "writing"],
            "max_score": 4,
            "duration_minutes": 120
        }
    }
    
    return {"exam_types": exam_types}

@router.get("/student/{student_id}/progress")
async def get_student_exam_progress(
    student_id: str,
    api_auth: dict = Depends(require_read)
):
    """Get comprehensive exam progress for a student"""
    # Verify student exists
    student = await db.users.find_one(
        {"id": student_id, "user_type": "student"},
        {"_id": 0, "current_exam": 1}
    )
    
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    # Get all attempts
    attempts = await db.exam_attempts.find(
        {"user_id": student_id},
        {"_id": 0}
    ).sort("created_at", 1).to_list(1000)
    
    if not attempts:
        return {
            "student_id": student_id,
            "total_attempts": 0,
            "progress": [],
            "trend": "no_data",
            "strongest_section": None,
            "weakest_section": None,
            "recommendation": "Start practicing to see your progress!"
        }
    
    # Calculate progress over time
    progress = []
    for a in attempts:
        progress.append({
            "date": a.get("created_at", "")[:10],
            "score": a.get("score", 0),
            "exam_type": a.get("exam_type", "")
        })
    
    # Calculate trend
    recent_scores = [a.get("score", 0) for a in attempts[-5:]]
    if len(recent_scores) >= 2:
        trend = "improving" if recent_scores[-1] > recent_scores[0] else "declining" if recent_scores[-1] < recent_scores[0] else "stable"
    else:
        trend = "insufficient_data"
    
    # Find strongest/weakest sections
    section_scores = {}
    for a in attempts:
        for section, score in a.get("section_scores", {}).items():
            if section not in section_scores:
                section_scores[section] = []
            section_scores[section].append(score)
    
    section_averages = {s: sum(scores)/len(scores) for s, scores in section_scores.items() if scores}
    
    strongest = max(section_averages, key=section_averages.get) if section_averages else None
    weakest = min(section_averages, key=section_averages.get) if section_averages else None
    
    # Generate recommendation
    if weakest and section_averages.get(weakest, 100) < 60:
        recommendation = f"Focus on improving your {weakest} section. Consider using the AI Tutor for targeted practice."
    elif trend == "declining":
        recommendation = "Your scores have been declining. Try to maintain a consistent study schedule."
    elif trend == "improving":
        recommendation = "Great progress! Keep up the good work and maintain your study routine."
    else:
        recommendation = "Continue practicing regularly to improve your scores."
    
    return {
        "student_id": student_id,
        "current_exam": student.get("current_exam"),
        "total_attempts": len(attempts),
        "average_score": round(sum(a.get("score", 0) for a in attempts) / len(attempts), 2),
        "highest_score": max(a.get("score", 0) for a in attempts),
        "progress": progress,
        "trend": trend,
        "section_averages": {s: round(v, 2) for s, v in section_averages.items()},
        "strongest_section": strongest,
        "weakest_section": weakest,
        "recommendation": recommendation
    }
