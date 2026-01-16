"""
ProficientHub - Mock Exam Service
Business logic for managing mock exams and credit consumption

CREDIT SYSTEM:
- 1 credit = 1 full mock exam (all 4 sections)
- 1 credit = 4 individual sections (0.25 each)
- Student chooses mode when starting exam

USAGE FLOW:
1. Student has X credits from academy's plan
2. Student starts Mock Exam #1
3. Student chooses: FULL_MOCK or SECTION mode
4. Credits are consumed as sections are completed
"""

from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from uuid import uuid4
import structlog

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, and_, or_
from sqlalchemy.orm import selectinload

from app.db.models_b2b import (
    Academy, AcademyExamPlan, AcademyStudent, StudentMockExam, MockExamSection,
    MockExamMode, MockExamStatus, SectionStatus, ExamPlanStatus,
    get_exam_time_config, EXAM_TIME_CONFIG
)

logger = structlog.get_logger(__name__)


class MockExamService:
    """
    Service for managing student mock exams and credit consumption
    """
    
    CREDIT_PER_SECTION = 0.25
    CREDIT_PER_FULL_MOCK = 1.0
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    # =========================================================================
    # CREDIT MANAGEMENT
    # =========================================================================
    
    async def get_student_credits(
        self, 
        user_id: str, 
        exam_type: str
    ) -> Dict[str, Any]:
        """
        Get available credits for a student for a specific exam type
        
        Returns:
            {
                "total_credits": 5,
                "used_credits": 2.25,
                "remaining_credits": 2.75,
                "remaining_full_mocks": 2,
                "remaining_sections": 11,
                "exam_plan_id": "...",
                "plan_name": "IELTS Academic - 5 exams",
                "expires_at": "2026-06-01T00:00:00Z"
            }
        """
        # Find student's academy membership
        student = await self._get_student_by_user(user_id)
        if not student:
            return {"error": "Student not found in any academy"}
        
        # Find active exam plan for this exam type
        plan = await self._get_active_plan(student.academy_id, exam_type)
        if not plan:
            return {"error": f"No active plan for {exam_type}"}
        
        remaining = plan.total_credits - plan.used_credits
        
        return {
            "total_credits": plan.total_credits,
            "used_credits": plan.used_credits,
            "remaining_credits": remaining,
            "remaining_full_mocks": int(remaining),
            "remaining_sections": int(remaining / self.CREDIT_PER_SECTION),
            "exam_plan_id": plan.id,
            "plan_name": plan.plan_name,
            "expires_at": plan.expires_at.isoformat() if plan.expires_at else None,
            "academy_name": student.academy.name
        }
    
    async def consume_credits(
        self, 
        exam_plan_id: str, 
        amount: float,
        mock_exam_id: str
    ) -> Tuple[bool, str]:
        """
        Consume credits from an exam plan
        
        Uses atomic UPDATE to prevent race conditions
        
        Returns:
            (success: bool, message: str)
        """
        from datetime import timezone
        from sqlalchemy import update
        
        # First, check and update expiration if needed
        plan = await self.session.get(AcademyExamPlan, exam_plan_id)
        
        if not plan:
            return False, "Plan not found"
        
        if plan.status != ExamPlanStatus.ACTIVE:
            return False, f"Plan is {plan.status.value}"
        
        now = datetime.now(timezone.utc)
        if plan.expires_at and plan.expires_at.replace(tzinfo=timezone.utc) < now:
            plan.status = ExamPlanStatus.EXPIRED
            await self.session.commit()
            return False, "Plan has expired"
        
        # Atomic update to prevent race conditions
        # This will only update if there are sufficient credits
        result = await self.session.execute(
            update(AcademyExamPlan)
            .where(
                and_(
                    AcademyExamPlan.id == exam_plan_id,
                    AcademyExamPlan.status == ExamPlanStatus.ACTIVE,
                    (AcademyExamPlan.total_credits - AcademyExamPlan.used_credits) >= amount
                )
            )
            .values(used_credits=AcademyExamPlan.used_credits + amount)
        )
        
        if result.rowcount == 0:
            return False, f"Insufficient credits or plan unavailable"
        
        # Refresh to get updated values
        await self.session.refresh(plan)
        
        # Check if exhausted after consumption
        if plan.used_credits >= plan.total_credits:
            plan.status = ExamPlanStatus.EXHAUSTED
            await self.session.commit()
        
        logger.info(
            "credits_consumed",
            plan_id=exam_plan_id,
            amount=amount,
            remaining=plan.total_credits - plan.used_credits,
            mock_exam_id=mock_exam_id
        )
        
        await self.session.commit()
        return True, f"Consumed {amount} credits"
    
    # =========================================================================
    # MOCK EXAM MANAGEMENT
    # =========================================================================
    
    async def get_student_mock_exams(
        self, 
        user_id: str, 
        exam_type: str
    ) -> List[Dict[str, Any]]:
        """
        Get all mock exams for a student for a specific exam type
        
        Returns list of mock exams with their status and progress
        """
        student = await self._get_student_by_user(user_id)
        if not student:
            return []
        
        plan = await self._get_active_plan(student.academy_id, exam_type)
        if not plan:
            return []
        
        # Get all mock exams for this student and plan
        query = (
            select(StudentMockExam)
            .where(
                and_(
                    StudentMockExam.student_id == student.id,
                    StudentMockExam.exam_plan_id == plan.id
                )
            )
            .options(selectinload(StudentMockExam.sections))
            .order_by(StudentMockExam.exam_number)
        )
        
        result = await self.session.execute(query)
        mock_exams = result.scalars().all()
        
        # Format response
        exams_data = []
        for mock in mock_exams:
            sections_data = [
                {
                    "section_type": s.section_type,
                    "order": s.order,
                    "status": s.status.value,
                    "time_limit_minutes": s.time_limit_minutes,
                    "time_elapsed_seconds": s.time_elapsed_seconds,
                    "band_score": s.band_score,
                    "percentage_score": s.percentage_score
                }
                for s in sorted(mock.sections, key=lambda x: x.order)
            ]
            
            exams_data.append({
                "id": mock.id,
                "exam_number": mock.exam_number,
                "mode": mock.mode.value,
                "status": mock.status.value,
                "topic": mock.topic,
                "credits_used": mock.credits_used,
                "overall_band": mock.overall_band,
                "overall_percentage": mock.overall_percentage,
                "sections": sections_data,
                "started_at": mock.started_at.isoformat() if mock.started_at else None,
                "completed_at": mock.completed_at.isoformat() if mock.completed_at else None,
                "progress": self._calculate_progress(mock)
            })
        
        return exams_data
    
    async def create_mock_exam(
        self,
        user_id: str,
        exam_type: str,
        mode: MockExamMode,
        topic: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a new mock exam for a student
        
        Args:
            user_id: User ID
            exam_type: Type of exam (e.g., ielts_academic)
            mode: FULL_MOCK or SECTION
            topic: Optional topic for exam content
            
        Returns:
            Created mock exam data
        """
        # Validate student and plan
        student = await self._get_student_by_user(user_id)
        if not student:
            return {"error": "Student not found in any academy"}
        
        plan = await self._get_active_plan(student.academy_id, exam_type)
        if not plan:
            return {"error": f"No active plan for {exam_type}"}
        
        # Check credits
        remaining = plan.total_credits - plan.used_credits
        required = self.CREDIT_PER_FULL_MOCK if mode == MockExamMode.FULL_MOCK else self.CREDIT_PER_SECTION
        
        if remaining < required:
            return {"error": f"Insufficient credits: {remaining} available"}
        
        # Get next exam number
        query = (
            select(StudentMockExam)
            .where(
                and_(
                    StudentMockExam.student_id == student.id,
                    StudentMockExam.exam_plan_id == plan.id
                )
            )
            .order_by(StudentMockExam.exam_number.desc())
            .limit(1)
        )
        result = await self.session.execute(query)
        last_exam = result.scalar_one_or_none()
        next_number = (last_exam.exam_number + 1) if last_exam else 1
        
        # Get time config
        time_config = get_exam_time_config(exam_type)
        
        # Create mock exam
        mock_exam = StudentMockExam(
            id=str(uuid4()),
            student_id=student.id,
            exam_plan_id=plan.id,
            user_id=user_id,
            exam_type=exam_type,
            exam_number=next_number,
            mode=mode,
            status=MockExamStatus.NOT_STARTED,
            topic=topic,
            total_time_limit_minutes=time_config["total_time_minutes"],
            credits_used=0.0
        )
        
        self.session.add(mock_exam)
        
        # Create sections based on exam type
        sections_config = time_config["sections"]
        for section_type, config in sections_config.items():
            # First section is available, rest are locked (for full mock)
            # All available for section mode
            if mode == MockExamMode.SECTION:
                status = SectionStatus.AVAILABLE
            else:
                status = SectionStatus.AVAILABLE if config["order"] == 1 else SectionStatus.LOCKED
            
            section = MockExamSection(
                id=str(uuid4()),
                mock_exam_id=mock_exam.id,
                section_type=section_type,
                order=config["order"],
                status=status,
                time_limit_minutes=config["time_minutes"],
                time_elapsed_seconds=0
            )
            self.session.add(section)
        
        await self.session.commit()
        
        logger.info(
            "mock_exam_created",
            mock_exam_id=mock_exam.id,
            user_id=user_id,
            exam_type=exam_type,
            mode=mode.value,
            exam_number=next_number
        )
        
        return {
            "id": mock_exam.id,
            "exam_number": next_number,
            "mode": mode.value,
            "status": MockExamStatus.NOT_STARTED.value,
            "exam_type": exam_type,
            "topic": topic,
            "total_time_limit_minutes": time_config["total_time_minutes"],
            "sections": [
                {
                    "section_type": s_type,
                    "order": cfg["order"],
                    "time_limit_minutes": cfg["time_minutes"],
                    "status": SectionStatus.AVAILABLE.value if (mode == MockExamMode.SECTION or cfg["order"] == 1) else SectionStatus.LOCKED.value
                }
                for s_type, cfg in sorted(sections_config.items(), key=lambda x: x[1]["order"])
            ],
            "remaining_credits_after": remaining - (0 if mode == MockExamMode.SECTION else 0)  # Credits consumed on completion
        }
    
    async def start_section(
        self,
        mock_exam_id: str,
        section_type: str,
        user_id: str
    ) -> Dict[str, Any]:
        """
        Start a section of a mock exam
        
        - Validates user owns this exam
        - Validates section is available
        - Consumes credits (for SECTION mode)
        - Generates exam content
        """
        # Get mock exam with sections
        query = (
            select(StudentMockExam)
            .where(StudentMockExam.id == mock_exam_id)
            .options(selectinload(StudentMockExam.sections))
        )
        result = await self.session.execute(query)
        mock_exam = result.scalar_one_or_none()
        
        if not mock_exam:
            return {"error": "Mock exam not found"}
        
        if mock_exam.user_id != user_id:
            return {"error": "Access denied"}
        
        # Find the section
        section = next((s for s in mock_exam.sections if s.section_type == section_type), None)
        if not section:
            return {"error": f"Section {section_type} not found"}
        
        if section.status == SectionStatus.COMPLETED:
            return {"error": "Section already completed"}
        
        if section.status == SectionStatus.LOCKED:
            return {"error": "Section is locked. Complete previous sections first."}
        
        if section.status == SectionStatus.IN_PROGRESS:
            # Resume existing section
            return {
                "id": section.id,
                "section_type": section.section_type,
                "status": section.status.value,
                "time_remaining_seconds": (section.time_limit_minutes * 60) - section.time_elapsed_seconds,
                "exam_session_id": section.exam_session_id,
                "message": "Resuming section"
            }
        
        # For SECTION mode, consume credits now
        if mock_exam.mode == MockExamMode.SECTION:
            success, msg = await self.consume_credits(
                mock_exam.exam_plan_id,
                self.CREDIT_PER_SECTION,
                mock_exam.id
            )
            if not success:
                return {"error": msg}
            mock_exam.credits_used += self.CREDIT_PER_SECTION
        
        # Update section status
        section.status = SectionStatus.IN_PROGRESS
        section.started_at = datetime.utcnow()
        
        # Update mock exam status if first section
        if mock_exam.status == MockExamStatus.NOT_STARTED:
            mock_exam.status = MockExamStatus.IN_PROGRESS
            mock_exam.started_at = datetime.utcnow()
        
        # TODO: Generate exam content here using ExamGenerator
        # For now, we'll just mark it as ready
        # section.exam_session_id = generated_exam_id
        
        await self.session.commit()
        
        logger.info(
            "section_started",
            mock_exam_id=mock_exam_id,
            section_type=section_type,
            user_id=user_id
        )
        
        return {
            "id": section.id,
            "section_type": section.section_type,
            "status": section.status.value,
            "time_limit_minutes": section.time_limit_minutes,
            "time_remaining_seconds": section.time_limit_minutes * 60,
            "exam_session_id": section.exam_session_id,
            "started_at": section.started_at.isoformat(),
            "message": "Section started successfully"
        }
    
    async def complete_section(
        self,
        mock_exam_id: str,
        section_type: str,
        user_id: str,
        time_elapsed_seconds: int,
        results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Complete a section and record results
        
        - Updates section with results
        - Unlocks next section (for FULL_MOCK mode)
        - Checks if all sections complete
        """
        # Get mock exam with sections
        query = (
            select(StudentMockExam)
            .where(StudentMockExam.id == mock_exam_id)
            .options(selectinload(StudentMockExam.sections))
        )
        result = await self.session.execute(query)
        mock_exam = result.scalar_one_or_none()
        
        if not mock_exam or mock_exam.user_id != user_id:
            return {"error": "Mock exam not found or access denied"}
        
        # Find the section
        section = next((s for s in mock_exam.sections if s.section_type == section_type), None)
        if not section:
            return {"error": f"Section {section_type} not found"}
        
        # Update section
        section.status = SectionStatus.COMPLETED
        section.completed_at = datetime.utcnow()
        section.time_elapsed_seconds = time_elapsed_seconds
        section.raw_score = results.get("raw_score")
        section.max_score = results.get("max_score")
        section.percentage_score = results.get("percentage_score")
        section.band_score = results.get("band_score")
        section.feedback = results.get("feedback", {})
        
        # For FULL_MOCK mode, unlock next section
        if mock_exam.mode == MockExamMode.FULL_MOCK:
            next_section = next(
                (s for s in mock_exam.sections if s.order == section.order + 1),
                None
            )
            if next_section and next_section.status == SectionStatus.LOCKED:
                next_section.status = SectionStatus.AVAILABLE
        
        # Check if all sections complete
        completed_sections = [s for s in mock_exam.sections if s.status == SectionStatus.COMPLETED]
        all_complete = len(completed_sections) == len(mock_exam.sections)
        
        if all_complete:
            mock_exam.status = MockExamStatus.COMPLETED
            mock_exam.completed_at = datetime.utcnow()
            
            # Calculate overall results
            overall = self._calculate_overall_results(mock_exam.sections, mock_exam.exam_type)
            mock_exam.overall_band = overall["band"]
            mock_exam.overall_percentage = overall["percentage"]
            mock_exam.section_results = overall["details"]
            
            # For FULL_MOCK mode, consume the full credit now
            if mock_exam.mode == MockExamMode.FULL_MOCK:
                success, msg = await self.consume_credits(
                    mock_exam.exam_plan_id,
                    self.CREDIT_PER_FULL_MOCK,
                    mock_exam.id
                )
                mock_exam.credits_used = self.CREDIT_PER_FULL_MOCK
        
        await self.session.commit()
        
        logger.info(
            "section_completed",
            mock_exam_id=mock_exam_id,
            section_type=section_type,
            band_score=section.band_score,
            all_complete=all_complete
        )
        
        response = {
            "section_id": section.id,
            "section_type": section_type,
            "status": section.status.value,
            "band_score": section.band_score,
            "percentage_score": section.percentage_score,
            "all_sections_complete": all_complete
        }
        
        if all_complete:
            response["mock_exam_completed"] = True
            response["overall_band"] = mock_exam.overall_band
            response["overall_percentage"] = mock_exam.overall_percentage
        else:
            # Return next section info
            next_section = next(
                (s for s in mock_exam.sections if s.status == SectionStatus.AVAILABLE),
                None
            )
            if next_section:
                response["next_section"] = {
                    "section_type": next_section.section_type,
                    "time_limit_minutes": next_section.time_limit_minutes
                }
        
        return response
    
    # =========================================================================
    # DASHBOARD DATA
    # =========================================================================
    
    async def get_student_dashboard(
        self,
        user_id: str,
        exam_type: str
    ) -> Dict[str, Any]:
        """
        Get complete dashboard data for a student
        
        Includes:
        - Credit status
        - All mock exams with progress
        - Statistics and analytics
        """
        credits = await self.get_student_credits(user_id, exam_type)
        if "error" in credits:
            return credits
        
        mock_exams = await self.get_student_mock_exams(user_id, exam_type)
        
        # Calculate statistics
        completed_exams = [e for e in mock_exams if e["status"] == "completed"]
        in_progress = [e for e in mock_exams if e["status"] == "in_progress"]
        
        stats = {
            "total_exams": len(mock_exams),
            "completed_exams": len(completed_exams),
            "in_progress_exams": len(in_progress),
            "average_band": None,
            "best_band": None,
            "improvement_trend": None
        }
        
        if completed_exams:
            bands = [e["overall_band"] for e in completed_exams if e.get("overall_band")]
            if bands:
                # Convert bands to numeric for calculation
                numeric_bands = [float(b) for b in bands if b]
                if numeric_bands:
                    stats["average_band"] = f"{sum(numeric_bands) / len(numeric_bands):.1f}"
                    stats["best_band"] = f"{max(numeric_bands):.1f}"
                    
                    # Calculate trend (last 3 vs first 3)
                    if len(numeric_bands) >= 3:
                        first_avg = sum(numeric_bands[:3]) / 3
                        last_avg = sum(numeric_bands[-3:]) / 3
                        stats["improvement_trend"] = round(last_avg - first_avg, 1)
        
        # Section-wise stats
        section_stats = {"reading": [], "writing": [], "listening": [], "speaking": []}
        for exam in completed_exams:
            for section in exam.get("sections", []):
                if section.get("band_score"):
                    section_stats[section["section_type"]].append(float(section["band_score"]))
        
        section_averages = {}
        for section, scores in section_stats.items():
            if scores:
                section_averages[section] = {
                    "average": round(sum(scores) / len(scores), 1),
                    "best": max(scores),
                    "attempts": len(scores)
                }
        
        return {
            "exam_type": exam_type,
            "credits": credits,
            "mock_exams": mock_exams,
            "statistics": stats,
            "section_averages": section_averages,
            "time_config": get_exam_time_config(exam_type)
        }
    
    # =========================================================================
    # HELPER METHODS
    # =========================================================================
    
    async def _get_student_by_user(self, user_id: str) -> Optional[AcademyStudent]:
        """Get academy student record for a user"""
        query = (
            select(AcademyStudent)
            .where(
                and_(
                    AcademyStudent.user_id == user_id,
                    AcademyStudent.is_active == True
                )
            )
            .options(selectinload(AcademyStudent.academy))
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
    
    async def _get_active_plan(
        self, 
        academy_id: str, 
        exam_type: str
    ) -> Optional[AcademyExamPlan]:
        """Get active exam plan for an academy and exam type"""
        query = (
            select(AcademyExamPlan)
            .where(
                and_(
                    AcademyExamPlan.academy_id == academy_id,
                    AcademyExamPlan.exam_type == exam_type,
                    AcademyExamPlan.status == ExamPlanStatus.ACTIVE
                )
            )
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
    
    def _calculate_progress(self, mock_exam: StudentMockExam) -> Dict[str, Any]:
        """Calculate progress percentage for a mock exam"""
        total_sections = len(mock_exam.sections)
        if total_sections == 0:
            return {"percentage": 0, "completed": 0, "total": 0}
        
        completed = sum(1 for s in mock_exam.sections if s.status == SectionStatus.COMPLETED)
        in_progress = sum(1 for s in mock_exam.sections if s.status == SectionStatus.IN_PROGRESS)
        
        # Weight in-progress as 50%
        progress = ((completed * 100) + (in_progress * 50)) / total_sections
        
        return {
            "percentage": round(progress),
            "completed": completed,
            "total": total_sections,
            "in_progress": in_progress
        }
    
    def _calculate_overall_results(
        self, 
        sections: List[MockExamSection],
        exam_type: str
    ) -> Dict[str, Any]:
        """Calculate overall band/score from section results"""
        
        # Get individual section scores
        section_scores = {}
        for section in sections:
            if section.band_score:
                section_scores[section.section_type] = {
                    "band": section.band_score,
                    "percentage": section.percentage_score
                }
        
        # Calculate overall (simple average for now)
        bands = [float(s["band"]) for s in section_scores.values() if s.get("band")]
        percentages = [s["percentage"] for s in section_scores.values() if s.get("percentage")]
        
        overall_band = None
        overall_percentage = None
        
        if bands:
            avg_band = sum(bands) / len(bands)
            # Round to nearest 0.5 for IELTS-style
            if exam_type.startswith("ielts"):
                overall_band = str(round(avg_band * 2) / 2)
            else:
                overall_band = f"{avg_band:.1f}"
        
        if percentages:
            overall_percentage = sum(percentages) / len(percentages)
        
        return {
            "band": overall_band,
            "percentage": overall_percentage,
            "details": section_scores
        }
