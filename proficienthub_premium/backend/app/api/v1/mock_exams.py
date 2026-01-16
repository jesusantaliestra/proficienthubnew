"""
ProficientHub - Mock Exam API Endpoints
Endpoints for managing mock exams, credits, and section progression

FLOW:
1. GET /mock-exams/dashboard - Get student dashboard with credits and exams
2. POST /mock-exams/create - Create new mock exam (choose FULL_MOCK or SECTION mode)
3. POST /mock-exams/{id}/start-section - Start a section
4. POST /mock-exams/{id}/complete-section - Complete a section with results
5. GET /mock-exams/{id} - Get mock exam details
"""

from fastapi import APIRouter, HTTPException, Query, Depends, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_session as get_db_session
from app.db.models import User
from app.db.models_b2b import MockExamMode, MockExamStatus, SectionStatus
from app.auth.dependencies import get_current_user
from app.services.mock_exam_service import MockExamService

router = APIRouter(prefix="/mock-exams", tags=["Mock Exams"])


# =============================================================================
# SCHEMAS
# =============================================================================

class MockExamModeEnum(str, Enum):
    FULL_MOCK = "full_mock"
    SECTION = "section"


class CreateMockExamRequest(BaseModel):
    """Request to create a new mock exam"""
    exam_type: str = Field(
        ...,
        description="Type of exam (e.g., ielts_academic)",
        example="ielts_academic"
    )
    mode: MockExamModeEnum = Field(
        ...,
        description="FULL_MOCK for complete exam, SECTION for individual sections"
    )
    topic: Optional[str] = Field(
        None,
        max_length=500,
        description="Optional topic for exam content",
        example="Climate change and environmental policy"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "exam_type": "ielts_academic",
                "mode": "full_mock",
                "topic": "Technology and modern society"
            }
        }


class StartSectionRequest(BaseModel):
    """Request to start a section"""
    section_type: str = Field(
        ...,
        description="Section to start: reading, writing, listening, speaking"
    )


class CompleteSectionRequest(BaseModel):
    """Request to complete a section with results"""
    section_type: str = Field(..., description="Section being completed")
    time_elapsed_seconds: int = Field(..., ge=0, description="Time taken in seconds")
    results: Dict[str, Any] = Field(
        ...,
        description="Section results including scores and feedback"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "section_type": "reading",
                "time_elapsed_seconds": 3420,
                "results": {
                    "raw_score": 32,
                    "max_score": 40,
                    "percentage_score": 80.0,
                    "band_score": "7.5",
                    "feedback": {
                        "strengths": ["Good inference skills"],
                        "improvements": ["Work on vocabulary"]
                    }
                }
            }
        }


class CreditStatusResponse(BaseModel):
    """Response with credit status"""
    total_credits: int
    used_credits: float
    remaining_credits: float
    remaining_full_mocks: int
    remaining_sections: int
    exam_plan_id: str
    plan_name: str
    academy_name: str
    expires_at: Optional[str] = None


class MockExamSummary(BaseModel):
    """Summary of a mock exam"""
    id: str
    exam_number: int
    mode: str
    status: str
    topic: Optional[str]
    credits_used: float
    overall_band: Optional[str]
    overall_percentage: Optional[float]
    progress: Dict[str, Any]
    started_at: Optional[str]
    completed_at: Optional[str]


class DashboardResponse(BaseModel):
    """Complete dashboard response"""
    exam_type: str
    credits: Dict[str, Any]
    mock_exams: List[Dict[str, Any]]
    statistics: Dict[str, Any]
    section_averages: Dict[str, Any]
    time_config: Dict[str, Any]


# =============================================================================
# ENDPOINTS
# =============================================================================

@router.get("/dashboard/{exam_type}", response_model=DashboardResponse)
async def get_student_dashboard(
    exam_type: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session)
):
    """
    Get complete student dashboard for an exam type
    
    Returns:
    - Credit status (remaining credits, exams available)
    - All mock exams with progress
    - Statistics (average band, improvement trend)
    - Section-wise averages
    - Time configuration for the exam
    """
    service = MockExamService(session)
    dashboard = await service.get_student_dashboard(current_user.id, exam_type)
    
    if "error" in dashboard:
        raise HTTPException(status_code=400, detail=dashboard["error"])
    
    return dashboard


@router.get("/credits/{exam_type}")
async def get_credit_status(
    exam_type: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session)
) -> Dict[str, Any]:
    """
    Get credit status for a specific exam type
    
    Shows how many credits remain and how they can be used:
    - remaining_full_mocks: Number of complete exams available
    - remaining_sections: Number of individual sections available
    """
    service = MockExamService(session)
    credits = await service.get_student_credits(current_user.id, exam_type)
    
    if "error" in credits:
        raise HTTPException(status_code=400, detail=credits["error"])
    
    return credits


@router.get("/list/{exam_type}")
async def list_mock_exams(
    exam_type: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session)
) -> Dict[str, Any]:
    """
    List all mock exams for the student for a specific exam type
    
    Returns exams with their status and progress
    """
    service = MockExamService(session)
    exams = await service.get_student_mock_exams(current_user.id, exam_type)
    
    return {
        "exam_type": exam_type,
        "mock_exams": exams,
        "total": len(exams)
    }


@router.post("/create")
async def create_mock_exam(
    request: CreateMockExamRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session)
) -> Dict[str, Any]:
    """
    Create a new mock exam
    
    Choose mode:
    - FULL_MOCK: Complete exam with all 4 sections in sequence (uses 1 credit)
    - SECTION: Individual sections that can be done in any order (0.25 credit each)
    
    The mock exam is created with all sections, but:
    - FULL_MOCK: Only first section is available, rest unlock sequentially
    - SECTION: All sections available immediately
    """
    service = MockExamService(session)
    
    # Convert enum
    mode = MockExamMode.FULL_MOCK if request.mode == MockExamModeEnum.FULL_MOCK else MockExamMode.SECTION
    
    result = await service.create_mock_exam(
        user_id=current_user.id,
        exam_type=request.exam_type,
        mode=mode,
        topic=request.topic
    )
    
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result


@router.get("/{mock_exam_id}")
async def get_mock_exam(
    mock_exam_id: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session)
) -> Dict[str, Any]:
    """
    Get detailed information about a specific mock exam
    
    Includes all sections with their status and results
    """
    from sqlalchemy import select
    from sqlalchemy.orm import selectinload
    from app.db.models_b2b import StudentMockExam
    
    query = (
        select(StudentMockExam)
        .where(StudentMockExam.id == mock_exam_id)
        .options(selectinload(StudentMockExam.sections))
    )
    
    result = await session.execute(query)
    mock_exam = result.scalar_one_or_none()
    
    if not mock_exam:
        raise HTTPException(status_code=404, detail="Mock exam not found")
    
    if mock_exam.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    sections_data = [
        {
            "id": s.id,
            "section_type": s.section_type,
            "order": s.order,
            "status": s.status.value,
            "time_limit_minutes": s.time_limit_minutes,
            "time_elapsed_seconds": s.time_elapsed_seconds,
            "band_score": s.band_score,
            "percentage_score": s.percentage_score,
            "feedback": s.feedback,
            "started_at": s.started_at.isoformat() if s.started_at else None,
            "completed_at": s.completed_at.isoformat() if s.completed_at else None
        }
        for s in sorted(mock_exam.sections, key=lambda x: x.order)
    ]
    
    return {
        "id": mock_exam.id,
        "exam_type": mock_exam.exam_type,
        "exam_number": mock_exam.exam_number,
        "mode": mock_exam.mode.value,
        "status": mock_exam.status.value,
        "topic": mock_exam.topic,
        "total_time_limit_minutes": mock_exam.total_time_limit_minutes,
        "time_elapsed_seconds": mock_exam.time_elapsed_seconds,
        "credits_used": mock_exam.credits_used,
        "overall_band": mock_exam.overall_band,
        "overall_percentage": mock_exam.overall_percentage,
        "section_results": mock_exam.section_results,
        "sections": sections_data,
        "started_at": mock_exam.started_at.isoformat() if mock_exam.started_at else None,
        "completed_at": mock_exam.completed_at.isoformat() if mock_exam.completed_at else None,
        "created_at": mock_exam.created_at.isoformat()
    }


@router.post("/{mock_exam_id}/start-section")
async def start_section(
    mock_exam_id: str,
    request: StartSectionRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session)
) -> Dict[str, Any]:
    """
    Start a section of a mock exam
    
    - Validates section is available
    - Consumes credits (for SECTION mode only)
    - Triggers exam content generation
    - Returns section details with time limit
    
    For FULL_MOCK mode:
    - Sections must be done in order
    - Credits consumed when exam is fully completed
    
    For SECTION mode:
    - Any available section can be started
    - 0.25 credits consumed immediately
    """
    service = MockExamService(session)
    
    result = await service.start_section(
        mock_exam_id=mock_exam_id,
        section_type=request.section_type,
        user_id=current_user.id
    )
    
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    
    # TODO: Add background task to generate exam content
    # background_tasks.add_task(generate_section_content, result["id"])
    
    return result


@router.post("/{mock_exam_id}/complete-section")
async def complete_section(
    mock_exam_id: str,
    request: CompleteSectionRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session)
) -> Dict[str, Any]:
    """
    Complete a section and submit results
    
    - Records time taken and scores
    - Unlocks next section (for FULL_MOCK mode)
    - Calculates overall results if all sections complete
    - Consumes remaining credits (for FULL_MOCK mode)
    
    Returns:
    - Section results
    - Next section info (if applicable)
    - Overall results (if exam complete)
    """
    service = MockExamService(session)
    
    result = await service.complete_section(
        mock_exam_id=mock_exam_id,
        section_type=request.section_type,
        user_id=current_user.id,
        time_elapsed_seconds=request.time_elapsed_seconds,
        results=request.results
    )
    
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result


@router.post("/{mock_exam_id}/pause")
async def pause_mock_exam(
    mock_exam_id: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session)
) -> Dict[str, Any]:
    """
    Pause a mock exam (for SECTION mode only)
    
    FULL_MOCK exams cannot be paused - they must be completed in one sitting
    """
    from sqlalchemy import select
    from app.db.models_b2b import StudentMockExam, MockExamMode, MockExamStatus
    
    query = select(StudentMockExam).where(StudentMockExam.id == mock_exam_id)
    result = await session.execute(query)
    mock_exam = result.scalar_one_or_none()
    
    if not mock_exam:
        raise HTTPException(status_code=404, detail="Mock exam not found")
    
    if mock_exam.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    if mock_exam.mode == MockExamMode.FULL_MOCK:
        raise HTTPException(
            status_code=400, 
            detail="Full mock exams cannot be paused. They must be completed in one sitting."
        )
    
    if mock_exam.status != MockExamStatus.IN_PROGRESS:
        raise HTTPException(status_code=400, detail=f"Cannot pause exam in {mock_exam.status.value} status")
    
    mock_exam.status = MockExamStatus.PAUSED
    await session.commit()
    
    return {
        "id": mock_exam.id,
        "status": mock_exam.status.value,
        "message": "Mock exam paused. You can resume anytime."
    }


@router.post("/{mock_exam_id}/resume")
async def resume_mock_exam(
    mock_exam_id: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session)
) -> Dict[str, Any]:
    """
    Resume a paused mock exam
    """
    from sqlalchemy import select
    from sqlalchemy.orm import selectinload
    from app.db.models_b2b import StudentMockExam, MockExamStatus, SectionStatus
    
    query = (
        select(StudentMockExam)
        .where(StudentMockExam.id == mock_exam_id)
        .options(selectinload(StudentMockExam.sections))
    )
    result = await session.execute(query)
    mock_exam = result.scalar_one_or_none()
    
    if not mock_exam:
        raise HTTPException(status_code=404, detail="Mock exam not found")
    
    if mock_exam.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    if mock_exam.status != MockExamStatus.PAUSED:
        raise HTTPException(status_code=400, detail=f"Cannot resume exam in {mock_exam.status.value} status")
    
    mock_exam.status = MockExamStatus.IN_PROGRESS
    await session.commit()
    
    # Find next available section
    available_sections = [
        s for s in mock_exam.sections 
        if s.status in [SectionStatus.AVAILABLE, SectionStatus.IN_PROGRESS]
    ]
    
    next_section = None
    if available_sections:
        next_section = min(available_sections, key=lambda x: x.order)
    
    return {
        "id": mock_exam.id,
        "status": mock_exam.status.value,
        "message": "Mock exam resumed",
        "next_section": {
            "section_type": next_section.section_type,
            "status": next_section.status.value,
            "time_remaining_seconds": (next_section.time_limit_minutes * 60) - next_section.time_elapsed_seconds
        } if next_section else None
    }


# =============================================================================
# USAGE EXAMPLES (for documentation)
# =============================================================================

"""
EXAMPLE FLOW - FULL MOCK MODE:

1. Check credits:
   GET /api/v1/mock-exams/credits/ielts_academic
   Response: { "remaining_credits": 3, "remaining_full_mocks": 3 }

2. Create mock exam:
   POST /api/v1/mock-exams/create
   { "exam_type": "ielts_academic", "mode": "full_mock" }
   Response: { "id": "...", "exam_number": 1, "sections": [...] }

3. Start first section (Listening):
   POST /api/v1/mock-exams/{id}/start-section
   { "section_type": "listening" }
   Response: { "time_limit_minutes": 40, "status": "in_progress" }

4. Complete section:
   POST /api/v1/mock-exams/{id}/complete-section
   { "section_type": "listening", "time_elapsed_seconds": 2340, "results": {...} }
   Response: { "band_score": "7.0", "next_section": { "section_type": "reading" } }

5. Continue with remaining sections...

6. After final section:
   Response: { "mock_exam_completed": true, "overall_band": "7.0", "credits_used": 1.0 }


EXAMPLE FLOW - SECTION MODE:

1. Create mock exam:
   POST /api/v1/mock-exams/create
   { "exam_type": "ielts_academic", "mode": "section" }

2. Start any section (e.g., Writing):
   POST /api/v1/mock-exams/{id}/start-section
   { "section_type": "writing" }
   Response: { "credits_consumed": 0.25, "remaining_credits": 2.75 }

3. Pause if needed:
   POST /api/v1/mock-exams/{id}/pause

4. Resume later:
   POST /api/v1/mock-exams/{id}/resume

5. Complete sections in any order over time...
"""
