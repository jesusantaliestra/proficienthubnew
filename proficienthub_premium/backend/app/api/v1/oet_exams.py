"""
ProficientHub - OET Exam API Endpoints
Complete REST API for OET exam generation, submission, and evaluation
"""

from fastapi import APIRouter, HTTPException, Query, Depends, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
from sqlalchemy.ext.asyncio import AsyncSession
import structlog

from app.db.database import get_session as get_db_session
from app.db.models import User
from app.auth.dependencies import get_current_user
from app.exams.oet.models import (
    OETProfession, OETSection, OETGrade, OETExam,
    OET_SCORING_CONFIG, get_grade_description
)
from app.exams.oet.generator import OETExamGenerator
from app.exams.oet.evaluator import OETEvaluator

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/oet", tags=["OET Exams"])


# =============================================================================
# SCHEMAS
# =============================================================================

class ProfessionEnum(str, Enum):
    MEDICINE = "medicine"
    NURSING = "nursing"
    DENTISTRY = "dentistry"
    PHARMACY = "pharmacy"
    PHYSIOTHERAPY = "physiotherapy"
    RADIOGRAPHY = "radiography"
    OCCUPATIONAL_THERAPY = "occupational_therapy"
    DIETETICS = "dietetics"
    PODIATRY = "podiatry"
    SPEECH_PATHOLOGY = "speech_pathology"
    OPTOMETRY = "optometry"
    VETERINARY_SCIENCE = "veterinary_science"


class SectionEnum(str, Enum):
    LISTENING = "listening"
    READING = "reading"
    WRITING = "writing"
    SPEAKING = "speaking"


class GenerateExamRequest(BaseModel):
    """Request to generate a new OET exam"""
    profession: ProfessionEnum = Field(..., description="OET profession")
    sections: Optional[List[SectionEnum]] = Field(
        None,
        description="Specific sections to generate (default: all)"
    )
    mock_exam_section_id: Optional[str] = Field(
        None,
        description="Link to mock exam section if part of mock exam"
    )


class GenerateSectionRequest(BaseModel):
    """Request to generate a single section"""
    profession: ProfessionEnum
    section: SectionEnum


class StartSectionRequest(BaseModel):
    """Request to start an exam section"""
    exam_id: str


class SubmitAnswersRequest(BaseModel):
    """Request to submit answers for evaluation"""
    exam_id: str = Field(..., description="OET exam ID")
    answers: Dict[str, Any] = Field(..., description="User's answers")
    time_elapsed_seconds: int = Field(..., ge=0, description="Time taken in seconds")


class WritingSubmitRequest(BaseModel):
    """Request to submit writing response"""
    exam_id: str
    letter: str = Field(..., min_length=50, description="Written letter response")
    time_elapsed_seconds: int = Field(..., ge=0)


class SpeakingSubmitRequest(BaseModel):
    """Request to submit speaking response"""
    exam_id: str
    role_play_1: Optional[Dict[str, Any]] = Field(None, description="Role play 1 transcript/recording")
    role_play_2: Optional[Dict[str, Any]] = Field(None, description="Role play 2 transcript/recording")
    time_elapsed_seconds: int = Field(..., ge=0)


# =============================================================================
# EXAM GENERATION ENDPOINTS
# =============================================================================

@router.post("/generate")
async def generate_oet_exam(
    request: GenerateExamRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session)
) -> Dict[str, Any]:
    """
    Generate a complete OET exam or specific sections

    Returns exam with all content for the requested sections.
    Supports all OET professions: medicine, nursing, dentistry, etc.
    """
    logger.info(
        "generating_oet_exam_request",
        user_id=current_user.id,
        profession=request.profession.value,
        sections=[s.value for s in request.sections] if request.sections else "all"
    )

    try:
        generator = OETExamGenerator(session)

        profession = OETProfession(request.profession.value)
        sections = [OETSection(s.value) for s in request.sections] if request.sections else None

        exam_session = await generator.generate_complete_exam(
            user_id=current_user.id,
            profession=profession,
            sections=sections
        )

        logger.info(
            "oet_exam_generated_api",
            user_id=current_user.id,
            exam_id=exam_session.id
        )

        return {
            "exam_id": exam_session.id,
            "profession": profession.value,
            "status": exam_session.status,
            "sections": {
                "listening": exam_session.listening is not None,
                "reading": exam_session.reading is not None,
                "writing": exam_session.writing is not None,
                "speaking": exam_session.speaking is not None
            },
            "created_at": exam_session.created_at.isoformat()
        }

    except Exception as e:
        logger.error("oet_exam_generation_failed", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to generate exam: {str(e)}")


@router.post("/generate/section")
async def generate_oet_section(
    request: GenerateSectionRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session)
) -> Dict[str, Any]:
    """
    Generate a single OET section

    Useful for practice or when only one section is needed.
    """
    logger.info(
        "generating_oet_section",
        user_id=current_user.id,
        profession=request.profession.value,
        section=request.section.value
    )

    try:
        generator = OETExamGenerator(session)

        profession = OETProfession(request.profession.value)
        section = OETSection(request.section.value)

        content = await generator.generate_section(
            user_id=current_user.id,
            profession=profession,
            section=section
        )

        # Get the created exam record
        exams = await generator.get_user_exams(
            user_id=current_user.id,
            section=section,
            status="created"
        )

        exam_id = exams[0].id if exams else None

        return {
            "exam_id": exam_id,
            "section": section.value,
            "profession": profession.value,
            "content": content,
            "time_limit_minutes": OET_SCORING_CONFIG.get(
                section.value, {}
            ).get("time_minutes", 60)
        }

    except Exception as e:
        logger.error("oet_section_generation_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# EXAM RETRIEVAL ENDPOINTS
# =============================================================================

@router.get("/exam/{exam_id}")
async def get_oet_exam(
    exam_id: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session)
) -> Dict[str, Any]:
    """
    Get OET exam details and content

    Returns full exam content if not yet started.
    Returns progress and results if completed.
    """
    generator = OETExamGenerator(session)
    exam = await generator.get_exam_by_id(exam_id)

    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found")

    if exam.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    response = {
        "exam_id": exam.id,
        "section": exam.section,
        "profession": exam.profession,
        "status": exam.status,
        "time_limit_seconds": exam.time_limit_seconds,
        "time_elapsed_seconds": exam.time_elapsed_seconds,
        "created_at": exam.created_at.isoformat() if exam.created_at else None,
        "started_at": exam.started_at.isoformat() if exam.started_at else None,
        "completed_at": exam.completed_at.isoformat() if exam.completed_at else None
    }

    # Include content if not completed
    if exam.status != "completed":
        response["content"] = exam.content

    # Include results if completed
    if exam.status == "completed":
        response["results"] = {
            "raw_score": exam.raw_score,
            "max_score": exam.max_score,
            "scaled_score": exam.scaled_score,
            "grade": exam.grade,
            "detailed_results": exam.detailed_results,
            "feedback": exam.feedback
        }

    return response


@router.get("/exams")
async def list_oet_exams(
    section: Optional[SectionEnum] = Query(None),
    status: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session)
) -> Dict[str, Any]:
    """
    List all OET exams for the current user

    Supports filtering by section and status.
    """
    generator = OETExamGenerator(session)

    section_enum = OETSection(section.value) if section else None

    exams = await generator.get_user_exams(
        user_id=current_user.id,
        section=section_enum,
        status=status
    )

    # Apply pagination
    total = len(exams)
    paginated = exams[skip:skip + limit]

    return {
        "exams": [
            {
                "exam_id": e.id,
                "section": e.section,
                "profession": e.profession,
                "status": e.status,
                "grade": e.grade,
                "scaled_score": e.scaled_score,
                "created_at": e.created_at.isoformat() if e.created_at else None,
                "completed_at": e.completed_at.isoformat() if e.completed_at else None
            }
            for e in paginated
        ],
        "total": total,
        "skip": skip,
        "limit": limit,
        "has_more": (skip + limit) < total
    }


# =============================================================================
# EXAM INTERACTION ENDPOINTS
# =============================================================================

@router.post("/start/{exam_id}")
async def start_oet_exam(
    exam_id: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session)
) -> Dict[str, Any]:
    """
    Start an OET exam section

    Marks the exam as in_progress and records start time.
    Returns the full content to begin the exam.
    """
    from sqlalchemy import update

    generator = OETExamGenerator(session)
    exam = await generator.get_exam_by_id(exam_id)

    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found")

    if exam.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    if exam.status != "created":
        raise HTTPException(
            status_code=400,
            detail=f"Exam cannot be started. Current status: {exam.status}"
        )

    # Update status
    from datetime import timezone
    now = datetime.now(timezone.utc)

    await session.execute(
        update(OETExam)
        .where(OETExam.id == exam_id)
        .values(status="in_progress", started_at=now)
    )
    await session.commit()

    logger.info(
        "oet_exam_started",
        exam_id=exam_id,
        user_id=current_user.id,
        section=exam.section
    )

    return {
        "exam_id": exam_id,
        "section": exam.section,
        "status": "in_progress",
        "started_at": now.isoformat(),
        "time_limit_seconds": exam.time_limit_seconds,
        "content": exam.content
    }


@router.post("/submit")
async def submit_oet_answers(
    request: SubmitAnswersRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session)
) -> Dict[str, Any]:
    """
    Submit answers for evaluation

    Evaluates the submitted answers and returns results.
    For Listening/Reading: Automatic scoring
    For Writing/Speaking: AI-assisted evaluation (may take longer)
    """
    logger.info(
        "submitting_oet_answers",
        exam_id=request.exam_id,
        user_id=current_user.id,
        time_elapsed=request.time_elapsed_seconds
    )

    generator = OETExamGenerator(session)
    exam = await generator.get_exam_by_id(request.exam_id)

    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found")

    if exam.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    if exam.status == "completed":
        raise HTTPException(status_code=400, detail="Exam already completed")

    # Evaluate
    evaluator = OETEvaluator(session)

    try:
        result = await evaluator.evaluate_section(
            exam_id=request.exam_id,
            answers=request.answers,
            time_elapsed_seconds=request.time_elapsed_seconds
        )

        logger.info(
            "oet_answers_evaluated",
            exam_id=request.exam_id,
            grade=result.grade.value,
            scaled_score=result.scaled_score
        )

        return {
            "exam_id": request.exam_id,
            "section": result.section.value,
            "raw_score": result.raw_score,
            "max_score": result.max_score,
            "scaled_score": result.scaled_score,
            "grade": result.grade.value,
            "grade_description": get_grade_description(result.grade),
            "part_scores": result.part_scores,
            "criteria_scores": result.criteria_scores,
            "feedback": result.feedback,
            "time_taken_seconds": result.time_taken_seconds,
            "time_limit_seconds": result.time_limit_seconds
        }

    except Exception as e:
        logger.error("oet_evaluation_failed", error=str(e))
        raise HTTPException(status_code=500, detail=f"Evaluation failed: {str(e)}")


@router.post("/submit/writing")
async def submit_oet_writing(
    request: WritingSubmitRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session)
) -> Dict[str, Any]:
    """
    Submit writing response for evaluation

    Specialized endpoint for Writing section submission.
    Uses AI for detailed evaluation of the letter.
    """
    answers = {"letter": request.letter}

    # Use the general submit endpoint
    submit_request = SubmitAnswersRequest(
        exam_id=request.exam_id,
        answers=answers,
        time_elapsed_seconds=request.time_elapsed_seconds
    )

    generator = OETExamGenerator(session)
    exam = await generator.get_exam_by_id(request.exam_id)

    if not exam or exam.section != "writing":
        raise HTTPException(status_code=400, detail="Invalid writing exam")

    evaluator = OETEvaluator(session)

    result = await evaluator.evaluate_section(
        exam_id=request.exam_id,
        answers=answers,
        time_elapsed_seconds=request.time_elapsed_seconds
    )

    return {
        "exam_id": request.exam_id,
        "section": "writing",
        "word_count": len(request.letter.split()),
        "raw_score": result.raw_score,
        "max_score": result.max_score,
        "scaled_score": result.scaled_score,
        "grade": result.grade.value,
        "criteria_scores": result.criteria_scores,
        "feedback": result.feedback
    }


@router.post("/submit/speaking")
async def submit_oet_speaking(
    request: SpeakingSubmitRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session)
) -> Dict[str, Any]:
    """
    Submit speaking responses for evaluation

    Accepts transcripts or audio references for each role-play.
    AI evaluation for transcript-based submission.
    """
    answers = {}
    if request.role_play_1:
        answers["role_play_1"] = request.role_play_1
    if request.role_play_2:
        answers["role_play_2"] = request.role_play_2

    generator = OETExamGenerator(session)
    exam = await generator.get_exam_by_id(request.exam_id)

    if not exam or exam.section != "speaking":
        raise HTTPException(status_code=400, detail="Invalid speaking exam")

    evaluator = OETEvaluator(session)

    result = await evaluator.evaluate_section(
        exam_id=request.exam_id,
        answers=answers,
        time_elapsed_seconds=request.time_elapsed_seconds
    )

    return {
        "exam_id": request.exam_id,
        "section": "speaking",
        "raw_score": result.raw_score,
        "max_score": result.max_score,
        "scaled_score": result.scaled_score,
        "grade": result.grade.value,
        "criteria_scores": result.criteria_scores,
        "feedback": result.feedback
    }


# =============================================================================
# RESULTS ENDPOINTS
# =============================================================================

@router.get("/results/{exam_id}")
async def get_oet_results(
    exam_id: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session)
) -> Dict[str, Any]:
    """
    Get detailed results for a completed exam
    """
    generator = OETExamGenerator(session)
    exam = await generator.get_exam_by_id(exam_id)

    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found")

    if exam.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    if exam.status != "completed":
        raise HTTPException(status_code=400, detail="Exam not yet completed")

    grade = OETGrade(exam.grade) if exam.grade else None

    return {
        "exam_id": exam_id,
        "section": exam.section,
        "profession": exam.profession,
        "raw_score": exam.raw_score,
        "max_score": exam.max_score,
        "scaled_score": exam.scaled_score,
        "grade": exam.grade,
        "grade_info": get_grade_description(grade) if grade else None,
        "detailed_results": exam.detailed_results,
        "feedback": exam.feedback,
        "time_taken_seconds": exam.time_elapsed_seconds,
        "completed_at": exam.completed_at.isoformat() if exam.completed_at else None
    }


@router.get("/results/summary")
async def get_oet_results_summary(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session)
) -> Dict[str, Any]:
    """
    Get summary of all completed OET exams

    Returns overall performance across all sections.
    """
    evaluator = OETEvaluator(session)

    summary = await evaluator.get_complete_results(user_id=current_user.id)

    return summary


# =============================================================================
# REFERENCE ENDPOINTS
# =============================================================================

@router.get("/config")
async def get_oet_config() -> Dict[str, Any]:
    """
    Get OET exam configuration and scoring information

    Returns time limits, question counts, and grading scale.
    """
    return {
        "sections": {
            section: {
                "time_minutes": config.get("time_minutes"),
                "total_questions": config.get("total_questions"),
                "parts": config.get("parts"),
                "criteria": config.get("criteria")
            }
            for section, config in OET_SCORING_CONFIG.items()
        },
        "grading_scale": {
            grade.value: get_grade_description(grade)
            for grade in OETGrade
        },
        "professions": [p.value for p in OETProfession]
    }


@router.get("/professions")
async def get_oet_professions() -> Dict[str, Any]:
    """
    Get list of supported OET professions
    """
    return {
        "professions": [
            {
                "code": p.value,
                "name": p.value.replace("_", " ").title()
            }
            for p in OETProfession
        ]
    }


@router.get("/grade-info/{grade}")
async def get_grade_info(grade: str) -> Dict[str, Any]:
    """
    Get detailed information about an OET grade
    """
    try:
        grade_enum = OETGrade(grade.upper())
        return get_grade_description(grade_enum)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid grade. Valid grades: A, B, C+, C, D, E"
        )
