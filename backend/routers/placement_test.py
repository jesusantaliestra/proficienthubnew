"""
Placement Test - Configurable Level Assessment

Allows institutions to configure and students to take placement tests
to determine their current English level before starting preparation.
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime, timezone
import os
import uuid
import random

router = APIRouter(prefix="/placement-test", tags=["Placement Test"])

# Database
from motor.motor_asyncio import AsyncIOMotorClient
mongo_client = AsyncIOMotorClient(os.environ.get("MONGO_URL"))
db = mongo_client[os.environ.get("DB_NAME", "eduplat")]

# Auth
from server import get_current_user


# =============================================
# Models
# =============================================

class PlacementTestConfig(BaseModel):
    """Configuration for placement test"""
    name: str
    exam_type: str  # OET, IELTS, etc.
    sections: List[str] = ["grammar", "vocabulary", "reading", "listening"]
    questions_per_section: int = 10
    time_limit_minutes: int = 30
    passing_score: int = 60
    is_required: bool = False  # Required before accessing content
    is_active: bool = True


class QuestionCreate(BaseModel):
    """Create a question for placement test"""
    section: str
    difficulty: str  # A1, A2, B1, B2, C1, C2
    question_type: str  # multiple_choice, fill_blank, true_false
    question_text: str
    options: Optional[List[str]] = None
    correct_answer: str
    explanation: Optional[str] = None
    audio_url: Optional[str] = None  # For listening questions


class TestAnswer(BaseModel):
    """Answer to a question"""
    question_id: str
    answer: str


class SubmitTestRequest(BaseModel):
    """Submit completed test"""
    test_session_id: str
    answers: List[TestAnswer]


# =============================================
# Default Questions (seed data)
# =============================================

DEFAULT_QUESTIONS = {
    "grammar": [
        {
            "difficulty": "A2",
            "question_type": "multiple_choice",
            "question_text": "The patient _____ in the hospital since Monday.",
            "options": ["is", "was", "has been", "had been"],
            "correct_answer": "has been",
            "explanation": "Present perfect is used for actions that started in the past and continue to the present."
        },
        {
            "difficulty": "B1",
            "question_type": "multiple_choice",
            "question_text": "If the symptoms _____, please contact your doctor immediately.",
            "options": ["persist", "persisted", "will persist", "persisting"],
            "correct_answer": "persist",
            "explanation": "First conditional uses present simple in the if-clause."
        },
        {
            "difficulty": "B2",
            "question_type": "multiple_choice",
            "question_text": "The medication _____ have been administered earlier.",
            "options": ["should", "would", "could", "might"],
            "correct_answer": "should",
            "explanation": "'Should have + past participle' expresses obligation in the past."
        },
        {
            "difficulty": "B1",
            "question_type": "multiple_choice",
            "question_text": "She asked me _____ I had taken the medication.",
            "options": ["that", "if", "what", "which"],
            "correct_answer": "if",
            "explanation": "Reported questions with yes/no questions use 'if' or 'whether'."
        },
        {
            "difficulty": "B2",
            "question_type": "multiple_choice",
            "question_text": "The surgery, _____ was scheduled for Tuesday, has been postponed.",
            "options": ["that", "which", "what", "who"],
            "correct_answer": "which",
            "explanation": "Non-defining relative clauses use 'which' for things, with commas."
        }
    ],
    "vocabulary": [
        {
            "difficulty": "B1",
            "question_type": "multiple_choice",
            "question_text": "The doctor prescribed some _____ for the infection.",
            "options": ["antibiotics", "antigens", "antiseptics", "antidotes"],
            "correct_answer": "antibiotics",
            "explanation": "Antibiotics are medications used to treat bacterial infections."
        },
        {
            "difficulty": "B2",
            "question_type": "multiple_choice",
            "question_text": "The patient was diagnosed with a _____ condition.",
            "options": ["chronic", "chronicle", "chronical", "chronicled"],
            "correct_answer": "chronic",
            "explanation": "Chronic means long-lasting or recurring."
        },
        {
            "difficulty": "B1",
            "question_type": "multiple_choice",
            "question_text": "Please take this medication _____ after meals.",
            "options": ["orally", "aurally", "verbally", "literally"],
            "correct_answer": "orally",
            "explanation": "Orally means by mouth."
        },
        {
            "difficulty": "B2",
            "question_type": "multiple_choice",
            "question_text": "The patient showed signs of respiratory _____.",
            "options": ["distress", "disease", "disorder", "discomfort"],
            "correct_answer": "distress",
            "explanation": "Respiratory distress indicates difficulty breathing."
        },
        {
            "difficulty": "C1",
            "question_type": "multiple_choice",
            "question_text": "The prognosis for recovery is _____.",
            "options": ["favorable", "flavored", "favored", "favourite"],
            "correct_answer": "favorable",
            "explanation": "Favorable prognosis means good chances of recovery."
        }
    ],
    "reading": [
        {
            "difficulty": "B1",
            "question_type": "multiple_choice",
            "question_text": "According to standard protocol, patients should fast for how many hours before surgery?",
            "options": ["4 hours", "6 hours", "8 hours", "12 hours"],
            "correct_answer": "8 hours",
            "explanation": "Standard pre-operative fasting is typically 8 hours for solids."
        },
        {
            "difficulty": "B2",
            "question_type": "true_false",
            "question_text": "Vital signs should be monitored every 4 hours for stable patients.",
            "options": ["True", "False"],
            "correct_answer": "True",
            "explanation": "Standard monitoring frequency for stable patients."
        },
        {
            "difficulty": "B1",
            "question_type": "multiple_choice",
            "question_text": "What is the primary purpose of a discharge summary?",
            "options": [
                "To bill the patient",
                "To communicate care details to the next provider",
                "To store in archives",
                "To satisfy legal requirements only"
            ],
            "correct_answer": "To communicate care details to the next provider",
            "explanation": "Discharge summaries ensure continuity of care."
        }
    ],
    "listening": [
        {
            "difficulty": "B1",
            "question_type": "multiple_choice",
            "question_text": "[Audio] What symptom is the patient describing?",
            "options": ["Headache", "Chest pain", "Nausea", "Fatigue"],
            "correct_answer": "Chest pain",
            "explanation": "Listen for key symptoms mentioned by the patient."
        },
        {
            "difficulty": "B2",
            "question_type": "multiple_choice",
            "question_text": "[Audio] What does the doctor recommend?",
            "options": [
                "Immediate surgery",
                "Further tests",
                "Medication change",
                "Lifestyle modifications"
            ],
            "correct_answer": "Further tests",
            "explanation": "Listen for the doctor's recommendations."
        }
    ]
}


# =============================================
# Institution Configuration Endpoints
# =============================================

@router.post("/config")
async def create_test_config(
    config: PlacementTestConfig,
    current_user: dict = Depends(get_current_user)
):
    """Create or update placement test configuration for institution"""
    
    if current_user.get("user_type") not in ["institution", "admin"]:
        raise HTTPException(status_code=403, detail="Institution access required")
    
    institution_id = current_user.get("institution_id") or current_user.get("id")
    
    config_doc = {
        "id": str(uuid.uuid4()),
        "institution_id": institution_id,
        **config.dict(),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    
    # Upsert config
    await db.placement_test_configs.update_one(
        {"institution_id": institution_id, "exam_type": config.exam_type},
        {"$set": config_doc},
        upsert=True
    )
    
    return {"message": "Configuración guardada", "config": config_doc}


@router.get("/config")
async def get_test_config(
    exam_type: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """Get placement test configuration"""
    
    institution_id = current_user.get("institution_id") or current_user.get("id")
    
    query = {"institution_id": institution_id}
    if exam_type:
        query["exam_type"] = exam_type
    
    configs = await db.placement_test_configs.find(
        query,
        {"_id": 0}
    ).to_list(20)
    
    return {"configs": configs}


@router.post("/questions")
async def add_question(
    question: QuestionCreate,
    exam_type: str,
    current_user: dict = Depends(get_current_user)
):
    """Add a custom question to the placement test"""
    
    if current_user.get("user_type") not in ["institution", "admin"]:
        raise HTTPException(status_code=403, detail="Institution access required")
    
    institution_id = current_user.get("institution_id") or current_user.get("id")
    
    question_doc = {
        "id": str(uuid.uuid4()),
        "institution_id": institution_id,
        "exam_type": exam_type,
        **question.dict(),
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.placement_questions.insert_one(question_doc)
    question_doc.pop("_id", None)
    
    return {"message": "Pregunta añadida", "question": question_doc}


@router.get("/questions")
async def get_questions(
    exam_type: str,
    section: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """Get questions for a placement test"""
    
    institution_id = current_user.get("institution_id") or current_user.get("id")
    
    query = {"institution_id": institution_id, "exam_type": exam_type}
    if section:
        query["section"] = section
    
    questions = await db.placement_questions.find(
        query,
        {"_id": 0, "correct_answer": 0}  # Don't expose answers
    ).to_list(100)
    
    return {"questions": questions}


# =============================================
# Student Test Taking Endpoints
# =============================================

@router.post("/start")
async def start_test(
    exam_type: str,
    current_user: dict = Depends(get_current_user)
):
    """Start a placement test session"""
    
    student_id = current_user["id"]
    institution_id = current_user.get("institution_id")
    
    # Get config (use default if none exists)
    config = await db.placement_test_configs.find_one(
        {"institution_id": institution_id, "exam_type": exam_type},
        {"_id": 0}
    )
    
    if not config:
        config = {
            "sections": ["grammar", "vocabulary", "reading"],
            "questions_per_section": 5,
            "time_limit_minutes": 20
        }
    
    # Get questions (custom + default)
    all_questions = []
    
    for section in config.get("sections", ["grammar", "vocabulary", "reading"]):
        # Get custom questions
        custom_qs = await db.placement_questions.find(
            {"institution_id": institution_id, "exam_type": exam_type, "section": section},
            {"_id": 0}
        ).to_list(50)
        
        # Add default questions if not enough custom
        default_qs = DEFAULT_QUESTIONS.get(section, [])
        
        section_questions = custom_qs + [
            {**q, "id": f"default_{section}_{i}", "section": section}
            for i, q in enumerate(default_qs)
        ]
        
        # Shuffle and select
        random.shuffle(section_questions)
        selected = section_questions[:config.get("questions_per_section", 5)]
        all_questions.extend(selected)
    
    # Create test session
    session_id = str(uuid.uuid4())
    session = {
        "id": session_id,
        "student_id": student_id,
        "institution_id": institution_id,
        "exam_type": exam_type,
        "config": config,
        "questions": all_questions,
        "started_at": datetime.now(timezone.utc).isoformat(),
        "expires_at": (datetime.now(timezone.utc) + timedelta(minutes=config.get("time_limit_minutes", 30))).isoformat(),
        "status": "in_progress"
    }
    
    await db.placement_test_sessions.insert_one(session)
    
    # Return questions without correct answers
    questions_for_student = [
        {k: v for k, v in q.items() if k not in ["correct_answer", "explanation"]}
        for q in all_questions
    ]
    
    return {
        "session_id": session_id,
        "exam_type": exam_type,
        "questions": questions_for_student,
        "time_limit_minutes": config.get("time_limit_minutes", 30),
        "total_questions": len(questions_for_student)
    }


@router.post("/submit")
async def submit_test(
    request: SubmitTestRequest,
    current_user: dict = Depends(get_current_user)
):
    """Submit completed placement test"""
    
    student_id = current_user["id"]
    
    # Get session
    session = await db.placement_test_sessions.find_one(
        {"id": request.test_session_id, "student_id": student_id}
    )
    
    if not session:
        raise HTTPException(status_code=404, detail="Sesión no encontrada")
    
    if session.get("status") == "completed":
        raise HTTPException(status_code=400, detail="Test ya completado")
    
    # Check if expired
    expires_at = datetime.fromisoformat(session["expires_at"].replace('Z', '+00:00'))
    if datetime.now(timezone.utc) > expires_at:
        await db.placement_test_sessions.update_one(
            {"id": request.test_session_id},
            {"$set": {"status": "expired"}}
        )
        raise HTTPException(status_code=400, detail="Test expirado")
    
    # Grade test
    questions = session.get("questions", [])
    answers_dict = {a.question_id: a.answer for a in request.answers}
    
    results = {
        "total_questions": len(questions),
        "correct": 0,
        "incorrect": 0,
        "by_section": {},
        "by_difficulty": {}
    }
    
    detailed_results = []
    
    for q in questions:
        q_id = q.get("id")
        correct_answer = q.get("correct_answer")
        student_answer = answers_dict.get(q_id)
        is_correct = student_answer == correct_answer
        
        section = q.get("section", "other")
        difficulty = q.get("difficulty", "B1")
        
        # Initialize section stats
        if section not in results["by_section"]:
            results["by_section"][section] = {"correct": 0, "total": 0}
        results["by_section"][section]["total"] += 1
        
        if difficulty not in results["by_difficulty"]:
            results["by_difficulty"][difficulty] = {"correct": 0, "total": 0}
        results["by_difficulty"][difficulty]["total"] += 1
        
        if is_correct:
            results["correct"] += 1
            results["by_section"][section]["correct"] += 1
            results["by_difficulty"][difficulty]["correct"] += 1
        else:
            results["incorrect"] += 1
        
        detailed_results.append({
            "question_id": q_id,
            "section": section,
            "difficulty": difficulty,
            "student_answer": student_answer,
            "correct_answer": correct_answer,
            "is_correct": is_correct,
            "explanation": q.get("explanation")
        })
    
    # Calculate scores and level
    total_score = (results["correct"] / results["total_questions"]) * 100 if results["total_questions"] > 0 else 0
    
    # Determine CEFR level based on difficulty performance
    level_scores = results["by_difficulty"]
    estimated_level = "A2"  # Default
    
    for level in ["C1", "B2", "B1", "A2"]:
        if level in level_scores:
            stats = level_scores[level]
            if stats["total"] > 0 and (stats["correct"] / stats["total"]) >= 0.6:
                estimated_level = level
                break
    
    # Calculate section percentages
    for section in results["by_section"]:
        stats = results["by_section"][section]
        stats["percentage"] = (stats["correct"] / stats["total"]) * 100 if stats["total"] > 0 else 0
    
    # Find weakest areas
    weak_areas = [
        section for section, stats in results["by_section"].items()
        if stats["percentage"] < 60
    ]
    
    # Update session
    completion_data = {
        "status": "completed",
        "completed_at": datetime.now(timezone.utc).isoformat(),
        "results": {
            "score": round(total_score, 1),
            "estimated_level": estimated_level,
            "correct": results["correct"],
            "total": results["total_questions"],
            "by_section": results["by_section"],
            "by_difficulty": results["by_difficulty"],
            "weak_areas": weak_areas
        },
        "detailed_results": detailed_results
    }
    
    await db.placement_test_sessions.update_one(
        {"id": request.test_session_id},
        {"$set": completion_data}
    )
    
    # Also save to placement_tests collection for easy lookup
    await db.placement_tests.insert_one({
        "id": request.test_session_id,
        "student_id": student_id,
        "exam_type": session["exam_type"],
        "results": completion_data["results"],
        "completed_at": completion_data["completed_at"]
    })
    
    return {
        "message": "Test completado",
        "score": round(total_score, 1),
        "estimated_level": estimated_level,
        "correct": results["correct"],
        "total": results["total_questions"],
        "by_section": results["by_section"],
        "weak_areas": weak_areas,
        "recommendations": [
            f"Enfócate en mejorar: {', '.join(weak_areas)}" if weak_areas else "¡Buen trabajo en todas las áreas!",
            f"Tu nivel estimado es {estimated_level}",
            "Considera crear un plan de estudio personalizado"
        ]
    }


@router.get("/my-results")
async def get_my_results(current_user: dict = Depends(get_current_user)):
    """Get all placement test results for current user"""
    
    results = await db.placement_tests.find(
        {"student_id": current_user["id"]},
        {"_id": 0}
    ).sort("completed_at", -1).to_list(20)
    
    return {"results": results}


@router.get("/results/{test_id}")
async def get_test_result(test_id: str, current_user: dict = Depends(get_current_user)):
    """Get detailed results for a specific test"""
    
    session = await db.placement_test_sessions.find_one(
        {"id": test_id, "student_id": current_user["id"]},
        {"_id": 0}
    )
    
    if not session:
        raise HTTPException(status_code=404, detail="Test no encontrado")
    
    return {"result": session}


# Import timedelta
from datetime import timedelta
