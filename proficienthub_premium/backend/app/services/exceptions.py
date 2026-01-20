"""
ProficientHub - Custom Exceptions
Business logic exceptions for consistent error handling
"""


class MockExamException(Exception):
    """Base exception for Mock Exam operations"""
    def __init__(self, message: str, code: str = "MOCK_EXAM_ERROR"):
        self.message = message
        self.code = code
        super().__init__(self.message)


class InsufficientCreditsError(MockExamException):
    """Raised when there are not enough credits for an operation"""
    def __init__(self, available: float, required: float):
        self.available = available
        self.required = required
        super().__init__(
            message=f"Insufficient credits: {available} available, {required} required",
            code="INSUFFICIENT_CREDITS"
        )


class PlanExpiredError(MockExamException):
    """Raised when trying to use an expired exam plan"""
    def __init__(self, plan_id: str):
        self.plan_id = plan_id
        super().__init__(
            message=f"Exam plan {plan_id} has expired",
            code="PLAN_EXPIRED"
        )


class PlanNotFoundError(MockExamException):
    """Raised when an exam plan is not found"""
    def __init__(self, exam_type: str):
        self.exam_type = exam_type
        super().__init__(
            message=f"No active plan found for exam type: {exam_type}",
            code="PLAN_NOT_FOUND"
        )


class StudentNotFoundError(MockExamException):
    """Raised when student is not found in any academy"""
    def __init__(self, user_id: str):
        self.user_id = user_id
        super().__init__(
            message="Student not found in any academy",
            code="STUDENT_NOT_FOUND"
        )


class MockExamNotFoundError(MockExamException):
    """Raised when a mock exam is not found"""
    def __init__(self, mock_exam_id: str):
        self.mock_exam_id = mock_exam_id
        super().__init__(
            message=f"Mock exam not found: {mock_exam_id}",
            code="MOCK_EXAM_NOT_FOUND"
        )


class SectionNotFoundError(MockExamException):
    """Raised when a section is not found in a mock exam"""
    def __init__(self, section_type: str, mock_exam_id: str):
        self.section_type = section_type
        self.mock_exam_id = mock_exam_id
        super().__init__(
            message=f"Section '{section_type}' not found in mock exam {mock_exam_id}",
            code="SECTION_NOT_FOUND"
        )


class SectionLockedError(MockExamException):
    """Raised when trying to access a locked section"""
    def __init__(self, section_type: str):
        self.section_type = section_type
        super().__init__(
            message=f"Section '{section_type}' is locked. Complete previous sections first.",
            code="SECTION_LOCKED"
        )


class SectionAlreadyCompletedError(MockExamException):
    """Raised when trying to start an already completed section"""
    def __init__(self, section_type: str):
        self.section_type = section_type
        super().__init__(
            message=f"Section '{section_type}' has already been completed",
            code="SECTION_ALREADY_COMPLETED"
        )


class AccessDeniedError(MockExamException):
    """Raised when user doesn't have access to a resource"""
    def __init__(self, resource: str = "resource"):
        self.resource = resource
        super().__init__(
            message=f"Access denied to {resource}",
            code="ACCESS_DENIED"
        )


class InvalidExamTypeError(MockExamException):
    """Raised when an invalid exam type is provided"""
    def __init__(self, exam_type: str, valid_types: list):
        self.exam_type = exam_type
        self.valid_types = valid_types
        super().__init__(
            message=f"Invalid exam type: '{exam_type}'. Valid types: {', '.join(valid_types)}",
            code="INVALID_EXAM_TYPE"
        )
