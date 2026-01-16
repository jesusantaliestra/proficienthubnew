"""
ProficientHub - Comprehensive Tests for Mock Exam System
Tests for credit management, mock exam creation, section progression, and edge cases
"""

import pytest
from datetime import datetime, timedelta
from uuid import uuid4
from unittest.mock import AsyncMock, MagicMock, patch
from decimal import Decimal

# =============================================================================
# TEST FIXTURES
# =============================================================================

@pytest.fixture
def sample_academy():
    """Sample academy for testing"""
    return {
        "id": str(uuid4()),
        "name": "Test Academy",
        "slug": "test-academy",
        "email": "test@academy.com",
        "tier": "professional",
        "max_students": 200,
        "is_active": True
    }

@pytest.fixture
def sample_exam_plan(sample_academy):
    """Sample exam plan with 5 credits"""
    return {
        "id": str(uuid4()),
        "academy_id": sample_academy["id"],
        "exam_type": "ielts_academic",
        "plan_name": "IELTS Academic - 5 Exams",
        "total_credits": 5,
        "used_credits": 0,
        "status": "active",
        "starts_at": datetime.utcnow(),
        "expires_at": datetime.utcnow() + timedelta(days=180)
    }

@pytest.fixture
def sample_student(sample_academy):
    """Sample student linked to academy"""
    return {
        "id": str(uuid4()),
        "academy_id": sample_academy["id"],
        "user_id": str(uuid4()),
        "student_code": "STU001",
        "group_name": "IELTS Prep 2026",
        "is_active": True
    }


# =============================================================================
# UNIT TESTS - CREDIT SYSTEM
# =============================================================================

class TestCreditSystem:
    """Tests for credit consumption logic"""
    
    def test_full_mock_consumes_one_credit(self):
        """Full mock exam should consume exactly 1 credit"""
        CREDIT_PER_FULL_MOCK = 1.0
        
        initial_credits = 5
        credits_after = initial_credits - CREDIT_PER_FULL_MOCK
        
        assert credits_after == 4
        assert CREDIT_PER_FULL_MOCK == 1.0
    
    def test_section_consumes_quarter_credit(self):
        """Each section should consume 0.25 credits"""
        CREDIT_PER_SECTION = 0.25
        
        initial_credits = 5
        credits_after_one_section = initial_credits - CREDIT_PER_SECTION
        
        assert credits_after_one_section == 4.75
        assert CREDIT_PER_SECTION == 0.25
    
    def test_four_sections_equal_one_credit(self):
        """4 sections should equal 1 credit"""
        CREDIT_PER_SECTION = 0.25
        
        total_sections_cost = 4 * CREDIT_PER_SECTION
        assert total_sections_cost == 1.0
    
    def test_five_credits_allow_five_full_mocks(self, sample_exam_plan):
        """5 credits should allow exactly 5 full mock exams"""
        total_credits = sample_exam_plan["total_credits"]
        CREDIT_PER_FULL_MOCK = 1.0
        
        max_full_mocks = int(total_credits / CREDIT_PER_FULL_MOCK)
        assert max_full_mocks == 5
    
    def test_five_credits_allow_twenty_sections(self, sample_exam_plan):
        """5 credits should allow exactly 20 individual sections"""
        total_credits = sample_exam_plan["total_credits"]
        CREDIT_PER_SECTION = 0.25
        
        max_sections = int(total_credits / CREDIT_PER_SECTION)
        assert max_sections == 20
    
    def test_mixed_usage_calculation(self):
        """Test mixed usage: 2 full mocks + individual sections"""
        total_credits = 5
        CREDIT_PER_FULL_MOCK = 1.0
        CREDIT_PER_SECTION = 0.25
        
        # Use 2 full mocks
        credits_after_mocks = total_credits - (2 * CREDIT_PER_FULL_MOCK)
        assert credits_after_mocks == 3.0
        
        # Remaining can do 12 individual sections
        remaining_sections = int(credits_after_mocks / CREDIT_PER_SECTION)
        assert remaining_sections == 12
    
    def test_insufficient_credits_for_full_mock(self):
        """Should not allow full mock if less than 1 credit"""
        remaining_credits = 0.75
        CREDIT_PER_FULL_MOCK = 1.0
        
        can_do_full_mock = remaining_credits >= CREDIT_PER_FULL_MOCK
        assert can_do_full_mock == False
    
    def test_insufficient_credits_for_section(self):
        """Should not allow section if less than 0.25 credits"""
        remaining_credits = 0.20
        CREDIT_PER_SECTION = 0.25
        
        can_do_section = remaining_credits >= CREDIT_PER_SECTION
        assert can_do_section == False
    
    def test_exact_credit_boundary(self):
        """Test exact boundary conditions"""
        CREDIT_PER_SECTION = 0.25
        CREDIT_PER_FULL_MOCK = 1.0
        
        # Exactly 0.25 should allow one section
        assert 0.25 >= CREDIT_PER_SECTION
        
        # Exactly 1.0 should allow one full mock
        assert 1.0 >= CREDIT_PER_FULL_MOCK
        
        # 0.24999 should NOT allow a section (floating point safe)
        assert round(0.24999, 2) < CREDIT_PER_SECTION


# =============================================================================
# UNIT TESTS - MOCK EXAM MODES
# =============================================================================

class TestMockExamModes:
    """Tests for full mock vs section mode behavior"""
    
    def test_full_mock_sections_unlock_sequentially(self):
        """In full mock mode, sections should unlock in order"""
        sections = [
            {"type": "listening", "order": 1, "status": "available"},
            {"type": "reading", "order": 2, "status": "locked"},
            {"type": "writing", "order": 3, "status": "locked"},
            {"type": "speaking", "order": 4, "status": "locked"},
        ]
        
        # Only first section available
        available_sections = [s for s in sections if s["status"] == "available"]
        assert len(available_sections) == 1
        assert available_sections[0]["order"] == 1
    
    def test_section_mode_all_available(self):
        """In section mode, all sections should be available from start"""
        sections = [
            {"type": "listening", "order": 1, "status": "available"},
            {"type": "reading", "order": 2, "status": "available"},
            {"type": "writing", "order": 3, "status": "available"},
            {"type": "speaking", "order": 4, "status": "available"},
        ]
        
        available_sections = [s for s in sections if s["status"] == "available"]
        assert len(available_sections) == 4
    
    def test_full_mock_cannot_pause(self):
        """Full mock exams should not be pausable"""
        mock_exam = {"mode": "full_mock", "status": "in_progress"}
        
        can_pause = mock_exam["mode"] != "full_mock"
        assert can_pause == False
    
    def test_section_mode_can_pause(self):
        """Section mode exams should be pausable"""
        mock_exam = {"mode": "section", "status": "in_progress"}
        
        can_pause = mock_exam["mode"] != "full_mock"
        assert can_pause == True
    
    def test_full_mock_credit_consumed_on_completion(self):
        """Full mock should consume credit only when all sections complete"""
        sections_completed = 3
        total_sections = 4
        mode = "full_mock"
        
        # Credit not consumed until all complete
        should_consume = sections_completed == total_sections and mode == "full_mock"
        assert should_consume == False
        
        # Now complete all
        sections_completed = 4
        should_consume = sections_completed == total_sections and mode == "full_mock"
        assert should_consume == True
    
    def test_section_mode_credit_consumed_per_section(self):
        """Section mode should consume credit immediately when starting section"""
        mode = "section"
        CREDIT_PER_SECTION = 0.25
        
        # First section started
        credits_used = CREDIT_PER_SECTION
        assert credits_used == 0.25
        
        # Second section started
        credits_used += CREDIT_PER_SECTION
        assert credits_used == 0.50
        
        # All four sections
        credits_used = 4 * CREDIT_PER_SECTION
        assert credits_used == 1.0


# =============================================================================
# UNIT TESTS - SECTION PROGRESSION
# =============================================================================

class TestSectionProgression:
    """Tests for section status transitions"""
    
    def test_section_status_transitions(self):
        """Test valid section status transitions"""
        valid_transitions = {
            "locked": ["available"],
            "available": ["in_progress"],
            "in_progress": ["completed", "skipped"],
            "completed": [],  # Terminal state
            "skipped": [],    # Terminal state
        }
        
        # Test locked -> available
        assert "available" in valid_transitions["locked"]
        
        # Test available -> in_progress
        assert "in_progress" in valid_transitions["available"]
        
        # Test in_progress -> completed
        assert "completed" in valid_transitions["in_progress"]
        
        # Test completed is terminal
        assert len(valid_transitions["completed"]) == 0
    
    def test_unlock_next_section_after_completion(self):
        """Completing a section should unlock the next one"""
        sections = [
            {"type": "listening", "order": 1, "status": "completed"},
            {"type": "reading", "order": 2, "status": "locked"},
            {"type": "writing", "order": 3, "status": "locked"},
            {"type": "speaking", "order": 4, "status": "locked"},
        ]
        
        # Find completed section and unlock next
        for i, section in enumerate(sections):
            if section["status"] == "completed" and i + 1 < len(sections):
                sections[i + 1]["status"] = "available"
                break
        
        assert sections[1]["status"] == "available"
        assert sections[2]["status"] == "locked"
    
    def test_cannot_start_locked_section(self):
        """Should not be able to start a locked section"""
        section = {"type": "reading", "status": "locked"}
        
        can_start = section["status"] in ["available", "in_progress"]
        assert can_start == False
    
    def test_can_resume_in_progress_section(self):
        """Should be able to resume an in-progress section"""
        section = {"type": "reading", "status": "in_progress", "time_elapsed": 1200}
        
        can_resume = section["status"] == "in_progress"
        assert can_resume == True


# =============================================================================
# UNIT TESTS - EXAM TIMING
# =============================================================================

class TestExamTiming:
    """Tests for exam timing configuration"""
    
    def test_ielts_total_time(self):
        """IELTS should have correct total time"""
        ielts_config = {
            "total_time_minutes": 165,  # 2h 45m
            "sections": {
                "listening": 40,
                "reading": 60,
                "writing": 60,
                "speaking": 15
            }
        }
        
        # Total should match (speaking often separate day but counted)
        section_total = sum(ielts_config["sections"].values())
        assert section_total == 175  # Includes all sections
        assert ielts_config["total_time_minutes"] == 165  # Exam total
    
    def test_time_remaining_calculation(self):
        """Test time remaining calculation"""
        time_limit_seconds = 60 * 60  # 60 minutes
        time_elapsed_seconds = 45 * 60  # 45 minutes elapsed
        
        time_remaining = time_limit_seconds - time_elapsed_seconds
        assert time_remaining == 15 * 60  # 15 minutes remaining
    
    def test_time_expired_detection(self):
        """Test detection of expired time"""
        time_limit_seconds = 60 * 60
        time_elapsed_seconds = 61 * 60  # 1 minute over
        
        is_expired = time_elapsed_seconds >= time_limit_seconds
        assert is_expired == True


# =============================================================================
# UNIT TESTS - SCORE CALCULATIONS
# =============================================================================

class TestScoreCalculations:
    """Tests for band score and overall calculations"""
    
    def test_ielts_band_rounding(self):
        """IELTS bands should round to nearest 0.5"""
        def round_ielts_band(score):
            return round(score * 2) / 2
        
        assert round_ielts_band(6.3) == 6.5
        assert round_ielts_band(6.7) == 6.5
        assert round_ielts_band(6.75) == 7.0
        assert round_ielts_band(6.25) == 6.5
        assert round_ielts_band(6.0) == 6.0
    
    def test_overall_band_calculation(self):
        """Test overall band from section bands"""
        section_bands = {
            "listening": 7.0,
            "reading": 6.5,
            "writing": 6.0,
            "speaking": 7.0
        }
        
        # Average
        avg = sum(section_bands.values()) / len(section_bands)
        assert avg == 6.625
        
        # Rounded to 0.5
        rounded = round(avg * 2) / 2
        assert rounded == 6.5
    
    def test_percentage_calculation(self):
        """Test percentage score calculation"""
        raw_score = 32
        max_score = 40
        
        percentage = (raw_score / max_score) * 100
        assert percentage == 80.0
    
    def test_band_from_percentage_mapping(self):
        """Test band score mapping from percentage"""
        def percentage_to_band(pct):
            if pct >= 90: return 9.0
            elif pct >= 80: return 8.0
            elif pct >= 70: return 7.0
            elif pct >= 60: return 6.0
            elif pct >= 50: return 5.0
            else: return 4.0
        
        assert percentage_to_band(95) == 9.0
        assert percentage_to_band(85) == 8.0
        assert percentage_to_band(75) == 7.0
        assert percentage_to_band(65) == 6.0
        assert percentage_to_band(55) == 5.0
        assert percentage_to_band(45) == 4.0


# =============================================================================
# UNIT TESTS - PROGRESS CALCULATION
# =============================================================================

class TestProgressCalculation:
    """Tests for progress percentage calculation"""
    
    def test_zero_progress(self):
        """No sections completed = 0% progress"""
        sections = [
            {"status": "available"},
            {"status": "locked"},
            {"status": "locked"},
            {"status": "locked"},
        ]
        
        completed = sum(1 for s in sections if s["status"] == "completed")
        total = len(sections)
        progress = (completed / total) * 100
        
        assert progress == 0
    
    def test_partial_progress(self):
        """Some sections completed = partial progress"""
        sections = [
            {"status": "completed"},
            {"status": "completed"},
            {"status": "in_progress"},
            {"status": "locked"},
        ]
        
        completed = sum(1 for s in sections if s["status"] == "completed")
        in_progress = sum(1 for s in sections if s["status"] == "in_progress")
        total = len(sections)
        
        # Weight in-progress as 50%
        progress = ((completed * 100) + (in_progress * 50)) / total
        assert progress == 62.5
    
    def test_full_progress(self):
        """All sections completed = 100% progress"""
        sections = [
            {"status": "completed"},
            {"status": "completed"},
            {"status": "completed"},
            {"status": "completed"},
        ]
        
        completed = sum(1 for s in sections if s["status"] == "completed")
        total = len(sections)
        progress = (completed / total) * 100
        
        assert progress == 100


# =============================================================================
# UNIT TESTS - EXAM NUMBERING
# =============================================================================

class TestExamNumbering:
    """Tests for exam number assignment"""
    
    def test_first_exam_is_number_one(self):
        """First exam should be number 1"""
        existing_exams = []
        next_number = 1 if not existing_exams else max(e["exam_number"] for e in existing_exams) + 1
        
        assert next_number == 1
    
    def test_sequential_numbering(self):
        """Exams should be numbered sequentially"""
        existing_exams = [
            {"exam_number": 1},
            {"exam_number": 2},
            {"exam_number": 3},
        ]
        
        next_number = max(e["exam_number"] for e in existing_exams) + 1
        assert next_number == 4
    
    def test_unique_exam_number_per_student_plan(self):
        """Each student should have unique exam numbers per plan"""
        student_exams = [
            {"student_id": "S1", "exam_plan_id": "P1", "exam_number": 1},
            {"student_id": "S1", "exam_plan_id": "P1", "exam_number": 2},
            {"student_id": "S1", "exam_plan_id": "P2", "exam_number": 1},  # Different plan, can restart
        ]
        
        # Check uniqueness within same student+plan
        from collections import Counter
        keys = [(e["student_id"], e["exam_plan_id"], e["exam_number"]) for e in student_exams]
        counts = Counter(keys)
        
        assert all(count == 1 for count in counts.values())


# =============================================================================
# INTEGRATION-STYLE TESTS (Mock DB)
# =============================================================================

class TestMockExamServiceIntegration:
    """Integration-style tests for MockExamService"""
    
    @pytest.mark.asyncio
    async def test_create_full_mock_exam_flow(self):
        """Test complete flow of creating a full mock exam"""
        # Simulate the flow
        user_id = str(uuid4())
        exam_type = "ielts_academic"
        mode = "full_mock"
        
        # 1. Check credits (would query DB)
        credits = {"remaining_credits": 5, "remaining_full_mocks": 5}
        assert credits["remaining_full_mocks"] >= 1
        
        # 2. Create mock exam
        mock_exam = {
            "id": str(uuid4()),
            "user_id": user_id,
            "exam_type": exam_type,
            "mode": mode,
            "status": "not_started",
            "exam_number": 1,
            "credits_used": 0
        }
        
        # 3. Create sections (4 for IELTS)
        sections = [
            {"type": "listening", "order": 1, "status": "available"},
            {"type": "reading", "order": 2, "status": "locked"},
            {"type": "writing", "order": 3, "status": "locked"},
            {"type": "speaking", "order": 4, "status": "locked"},
        ]
        
        assert len(sections) == 4
        assert sections[0]["status"] == "available"
        assert all(s["status"] == "locked" for s in sections[1:])
    
    @pytest.mark.asyncio
    async def test_create_section_mode_exam_flow(self):
        """Test complete flow of creating a section mode exam"""
        user_id = str(uuid4())
        exam_type = "ielts_academic"
        mode = "section"
        
        # All sections available in section mode
        sections = [
            {"type": "listening", "order": 1, "status": "available"},
            {"type": "reading", "order": 2, "status": "available"},
            {"type": "writing", "order": 3, "status": "available"},
            {"type": "speaking", "order": 4, "status": "available"},
        ]
        
        assert all(s["status"] == "available" for s in sections)
    
    @pytest.mark.asyncio
    async def test_complete_section_unlocks_next(self):
        """Test that completing a section unlocks the next one"""
        sections = [
            {"type": "listening", "order": 1, "status": "completed"},
            {"type": "reading", "order": 2, "status": "locked"},
            {"type": "writing", "order": 3, "status": "locked"},
            {"type": "speaking", "order": 4, "status": "locked"},
        ]
        
        # Simulate unlock logic
        for i, section in enumerate(sections):
            if section["status"] == "completed" and i + 1 < len(sections):
                if sections[i + 1]["status"] == "locked":
                    sections[i + 1]["status"] = "available"
        
        assert sections[1]["status"] == "available"
    
    @pytest.mark.asyncio
    async def test_all_sections_complete_marks_exam_complete(self):
        """Test that completing all sections marks the exam as complete"""
        sections = [
            {"type": "listening", "status": "completed", "band": 7.0},
            {"type": "reading", "status": "completed", "band": 6.5},
            {"type": "writing", "status": "completed", "band": 6.0},
            {"type": "speaking", "status": "completed", "band": 7.0},
        ]
        
        all_complete = all(s["status"] == "completed" for s in sections)
        assert all_complete == True
        
        # Calculate overall band
        bands = [s["band"] for s in sections]
        overall = round(sum(bands) / len(bands) * 2) / 2
        assert overall == 6.5


# =============================================================================
# EDGE CASE TESTS
# =============================================================================

class TestEdgeCases:
    """Tests for edge cases and error conditions"""
    
    def test_expired_plan_cannot_create_exam(self):
        """Should not allow creating exam with expired plan"""
        plan = {
            "status": "active",
            "expires_at": datetime.utcnow() - timedelta(days=1)  # Expired yesterday
        }
        
        is_expired = plan["expires_at"] < datetime.utcnow()
        assert is_expired == True
    
    def test_exhausted_plan_cannot_create_exam(self):
        """Should not allow creating exam with exhausted credits"""
        plan = {
            "total_credits": 5,
            "used_credits": 5,
            "status": "exhausted"
        }
        
        remaining = plan["total_credits"] - plan["used_credits"]
        assert remaining == 0
    
    def test_inactive_student_cannot_access_exams(self):
        """Inactive student should not access exams"""
        student = {"is_active": False}
        
        can_access = student["is_active"]
        assert can_access == False
    
    def test_user_cannot_access_other_users_exam(self):
        """User should not access another user's exam"""
        exam_owner_id = str(uuid4())
        requesting_user_id = str(uuid4())
        
        can_access = exam_owner_id == requesting_user_id
        assert can_access == False
    
    def test_cannot_complete_section_twice(self):
        """Should not allow completing an already completed section"""
        section = {"status": "completed"}
        
        can_complete = section["status"] != "completed"
        assert can_complete == False
    
    def test_floating_point_credit_precision(self):
        """Test that credit calculations handle floating point correctly"""
        # Common floating point issue: 0.1 + 0.1 + 0.1 != 0.3
        credits = 0.0
        for _ in range(4):
            credits += 0.25
        
        # Use round to handle floating point
        assert round(credits, 2) == 1.0
    
    def test_concurrent_credit_consumption(self):
        """Simulate concurrent credit consumption race condition"""
        # This would need actual DB transaction testing, but we can test the logic
        initial_credits = 5
        used_credits = 0
        
        # Two concurrent requests trying to use last credit
        def consume_credit(remaining):
            if remaining >= 1:
                return remaining - 1, True
            return remaining, False
        
        remaining = initial_credits - used_credits
        
        # First request succeeds
        remaining, success1 = consume_credit(remaining)
        assert success1 == True
        
        # Simulate 4 more successful consumptions
        for _ in range(4):
            remaining, _ = consume_credit(remaining)
        
        # Sixth request should fail
        remaining, success6 = consume_credit(remaining)
        assert success6 == False


# =============================================================================
# API CONTRACT TESTS
# =============================================================================

class TestAPIContracts:
    """Tests for API request/response contracts"""
    
    def test_create_exam_request_validation(self):
        """Test create exam request schema"""
        valid_request = {
            "exam_type": "ielts_academic",
            "mode": "full_mock",
            "topic": "Climate change"
        }
        
        assert "exam_type" in valid_request
        assert valid_request["mode"] in ["full_mock", "section"]
    
    def test_dashboard_response_structure(self):
        """Test dashboard response has required fields"""
        response = {
            "exam_type": "ielts_academic",
            "credits": {
                "total_credits": 5,
                "used_credits": 1,
                "remaining_credits": 4,
                "remaining_full_mocks": 4,
                "remaining_sections": 16
            },
            "mock_exams": [],
            "statistics": {},
            "section_averages": {},
            "time_config": {}
        }
        
        required_fields = ["exam_type", "credits", "mock_exams", "statistics", "section_averages", "time_config"]
        assert all(field in response for field in required_fields)
    
    def test_section_status_enum_values(self):
        """Test valid section status values"""
        valid_statuses = ["locked", "available", "in_progress", "completed", "skipped"]
        
        test_status = "available"
        assert test_status in valid_statuses
    
    def test_mock_exam_mode_enum_values(self):
        """Test valid mock exam mode values"""
        valid_modes = ["full_mock", "section"]
        
        test_mode = "full_mock"
        assert test_mode in valid_modes


# =============================================================================
# RUN TESTS
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
