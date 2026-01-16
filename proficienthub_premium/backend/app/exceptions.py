"""
ProficientHub - Custom Exceptions
Consistent error handling across the application
"""

from typing import Optional, Dict, Any


class ProficientHubError(Exception):
    """Base exception for all ProficientHub errors"""

    def __init__(
        self,
        message: str,
        code: str = "UNKNOWN_ERROR",
        status_code: int = 400,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "error": self.message,
            "code": self.code,
            "details": self.details
        }


# =============================================================================
# STUDENT ERRORS
# =============================================================================

class StudentNotFoundError(ProficientHubError):
    """Raised when student is not found in any academy"""

    def __init__(self, user_id: str):
        super().__init__(
            message="Student not found in any academy",
            code="STUDENT_NOT_FOUND",
            status_code=404,
            details={"user_id": user_id}
        )


class StudentInactiveError(ProficientHubError):
    """Raised when student account is inactive"""

    def __init__(self, user_id: str):
        super().__init__(
            message="Student account is inactive",
            code="STUDENT_INACTIVE",
            status_code=403,
            details={"user_id": user_id}
        )


# =============================================================================
# PLAN & CREDIT ERRORS
# =============================================================================

class PlanNotFoundError(ProficientHubError):
    """Raised when no active plan exists for exam type"""

    def __init__(self, exam_type: str, academy_id: Optional[str] = None):
        super().__init__(
            message=f"No active plan for {exam_type}",
            code="PLAN_NOT_FOUND",
            status_code=404,
            details={"exam_type": exam_type, "academy_id": academy_id}
        )


class PlanExpiredError(ProficientHubError):
    """Raised when plan has expired"""

    def __init__(self, plan_id: str, expired_at: str):
        super().__init__(
            message="Plan has expired",
            code="PLAN_EXPIRED",
            status_code=400,
            details={"plan_id": plan_id, "expired_at": expired_at}
        )


class PlanExhaustedError(ProficientHubError):
    """Raised when plan credits are exhausted"""

    def __init__(self, plan_id: str):
        super().__init__(
            message="Plan credits are exhausted",
            code="PLAN_EXHAUSTED",
            status_code=400,
            details={"plan_id": plan_id}
        )


class InsufficientCreditsError(ProficientHubError):
    """Raised when there aren't enough credits for an operation"""

    def __init__(self, required: float, available: float):
        super().__init__(
            message=f"Insufficient credits: {available} available, {required} required",
            code="INSUFFICIENT_CREDITS",
            status_code=400,
            details={"required": required, "available": available}
        )


# =============================================================================
# MOCK EXAM ERRORS
# =============================================================================

class MockExamNotFoundError(ProficientHubError):
    """Raised when mock exam is not found"""

    def __init__(self, mock_exam_id: str):
        super().__init__(
            message="Mock exam not found",
            code="MOCK_EXAM_NOT_FOUND",
            status_code=404,
            details={"mock_exam_id": mock_exam_id}
        )


class MockExamAccessDeniedError(ProficientHubError):
    """Raised when user doesn't have access to mock exam"""

    def __init__(self, mock_exam_id: str, user_id: str):
        super().__init__(
            message="Access denied to this mock exam",
            code="MOCK_EXAM_ACCESS_DENIED",
            status_code=403,
            details={"mock_exam_id": mock_exam_id, "user_id": user_id}
        )


class InvalidExamTypeError(ProficientHubError):
    """Raised when exam type is invalid"""

    def __init__(self, exam_type: str, valid_types: list):
        super().__init__(
            message=f"Invalid exam type: {exam_type}",
            code="INVALID_EXAM_TYPE",
            status_code=400,
            details={"exam_type": exam_type, "valid_types": valid_types}
        )


# =============================================================================
# SECTION ERRORS
# =============================================================================

class SectionNotFoundError(ProficientHubError):
    """Raised when section is not found"""

    def __init__(self, section_type: str, mock_exam_id: str):
        super().__init__(
            message=f"Section {section_type} not found",
            code="SECTION_NOT_FOUND",
            status_code=404,
            details={"section_type": section_type, "mock_exam_id": mock_exam_id}
        )


class SectionLockedError(ProficientHubError):
    """Raised when trying to start a locked section"""

    def __init__(self, section_type: str):
        super().__init__(
            message=f"Section {section_type} is locked. Complete previous sections first.",
            code="SECTION_LOCKED",
            status_code=400,
            details={"section_type": section_type}
        )


class SectionAlreadyCompletedError(ProficientHubError):
    """Raised when trying to complete an already completed section"""

    def __init__(self, section_type: str):
        super().__init__(
            message=f"Section {section_type} is already completed",
            code="SECTION_ALREADY_COMPLETED",
            status_code=400,
            details={"section_type": section_type}
        )


class CannotPauseFullMockError(ProficientHubError):
    """Raised when trying to pause a full mock exam"""

    def __init__(self, mock_exam_id: str):
        super().__init__(
            message="Full mock exams cannot be paused. They must be completed in one sitting.",
            code="CANNOT_PAUSE_FULL_MOCK",
            status_code=400,
            details={"mock_exam_id": mock_exam_id}
        )
