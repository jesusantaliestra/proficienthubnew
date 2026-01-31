"""
OET Exam System Backend Tests
Tests for OET Nurse Dashboard, Mock Exams, and Exam Session endpoints
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
INSTITUTION_EMAIL = "demo_academy@test.com"
INSTITUTION_PASSWORD = "Demo123!"


class TestOETExamPublicEndpoints:
    """Test public OET exam endpoints (no auth required)"""
    
    def test_health_check(self):
        """Test backend health check"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        print("✓ Health check passed")
    
    def test_get_available_mocks_public(self):
        """Test GET /api/oet-exam/mocks/available - returns 3 mocks"""
        response = requests.get(f"{BASE_URL}/api/oet-exam/mocks/available")
        assert response.status_code == 200
        data = response.json()
        
        # Verify structure
        assert "mocks" in data
        assert "total" in data
        assert data["total"] == 3
        
        # Verify mock data
        mocks = data["mocks"]
        mock_ids = [m["id"] for m in mocks]
        assert "NUR-013-v2" in mock_ids
        assert "NUR-014" in mock_ids
        assert "NUR-015" in mock_ids
        
        # Verify first mock is available, others are locked
        nur_013 = next(m for m in mocks if m["id"] == "NUR-013-v2")
        assert nur_013["status"] == "available"
        assert nur_013["profession"] == "nursing"
        assert nur_013["total_duration"] == 175
        assert "sections" in nur_013
        
        nur_014 = next(m for m in mocks if m["id"] == "NUR-014")
        assert nur_014["status"] == "locked"
        
        nur_015 = next(m for m in mocks if m["id"] == "NUR-015")
        assert nur_015["status"] == "locked"
        assert nur_015["difficulty"] == "Advanced"
        
        print("✓ GET /api/oet-exam/mocks/available returns 3 mocks (1 available, 2 locked)")
    
    def test_get_oet_professions(self):
        """Test GET /api/oet-exam/professions - returns 12 healthcare professions"""
        response = requests.get(f"{BASE_URL}/api/oet-exam/professions")
        assert response.status_code == 200
        data = response.json()
        
        assert "professions" in data
        assert "total" in data
        assert data["total"] == 12
        
        # Verify nursing profession exists
        professions = data["professions"]
        nursing = next((p for p in professions if p["id"] == "nursing"), None)
        assert nursing is not None
        assert nursing["name"] == "Nursing"
        assert nursing["code"] == "NUR"
        
        # Verify other professions
        profession_ids = [p["id"] for p in professions]
        assert "medicine" in profession_ids
        assert "dentistry" in profession_ids
        assert "pharmacy" in profession_ids
        
        print("✓ GET /api/oet-exam/professions returns 12 healthcare professions")
    
    def test_get_exam_structure(self):
        """Test GET /api/oet-exam/exam-structure - returns OET exam format"""
        response = requests.get(f"{BASE_URL}/api/oet-exam/exam-structure")
        assert response.status_code == 200
        data = response.json()
        
        assert "structure" in data
        assert "bands" in data
        assert "total_duration_minutes" in data
        assert data["total_duration_minutes"] == 175
        
        # Verify 4 sections
        structure = data["structure"]
        assert "listening" in structure
        assert "reading" in structure
        assert "writing" in structure
        assert "speaking" in structure
        
        # Verify listening section
        listening = structure["listening"]
        assert listening["duration_minutes"] == 50
        assert listening["total_questions"] == 42
        assert "parts" in listening
        
        # Verify reading section
        reading = structure["reading"]
        assert reading["duration_minutes"] == 60
        assert reading["total_questions"] == 42
        
        # Verify writing section
        writing = structure["writing"]
        assert writing["duration_minutes"] == 45
        assert writing["total_questions"] == 1
        
        # Verify speaking section
        speaking = structure["speaking"]
        assert speaking["duration_minutes"] == 20
        assert speaking["total_roleplays"] == 2
        
        # Verify band scores
        bands = data["bands"]
        assert "A" in bands
        assert "B" in bands
        assert "C+" in bands
        assert "C" in bands
        assert "D" in bands
        assert "E" in bands
        
        print("✓ GET /api/oet-exam/exam-structure returns correct OET format")


class TestOETExamAuthenticatedEndpoints:
    """Test authenticated OET exam endpoints"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Login and get auth token"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": INSTITUTION_EMAIL, "password": INSTITUTION_PASSWORD}
        )
        if response.status_code == 200:
            self.token = response.json()["access_token"]
            self.headers = {"Authorization": f"Bearer {self.token}"}
        else:
            pytest.skip("Authentication failed - skipping authenticated tests")
    
    def test_get_student_dashboard(self):
        """Test GET /api/oet-exam/student/dashboard - returns dashboard data"""
        response = requests.get(
            f"{BASE_URL}/api/oet-exam/student/dashboard",
            headers=self.headers
        )
        assert response.status_code == 200
        data = response.json()
        
        # Verify dashboard structure
        assert "enrollment" in data
        assert "institution_config" in data
        assert "exam_history" in data
        assert "study_plan" in data
        assert "available_mocks" in data
        assert "next_steps" in data
        assert "profession_info" in data
        
        # Verify institution config
        config = data["institution_config"]
        assert "placement_test_enabled" in config
        assert "ai_tutor_enabled" in config
        assert "mock_exam_coach_enabled" in config
        
        # Verify profession info
        profession = data["profession_info"]
        assert profession["name"] == "Nursing"
        
        print("✓ GET /api/oet-exam/student/dashboard returns dashboard data")
    
    def test_get_mock_exam_content(self):
        """Test GET /api/oet-exam/mock/{mock_id}/content - returns exam content"""
        response = requests.get(
            f"{BASE_URL}/api/oet-exam/mock/NUR-013-v2/content?section=listening",
            headers=self.headers
        )
        assert response.status_code == 200
        data = response.json()
        
        assert data["mock_id"] == "NUR-013-v2"
        assert data["section"] == "listening"
        assert "content" in data
        
        content = data["content"]
        assert "part_a" in content
        assert "part_b" in content
        assert "part_c" in content
        
        # Verify Part A structure
        part_a = content["part_a"]
        assert part_a["name"] == "Part A: Consultation Extracts"
        assert part_a["questions"] == 24
        assert "extracts" in part_a
        
        # Verify Part B structure
        part_b = content["part_b"]
        assert part_b["name"] == "Part B: Workplace Extracts"
        assert part_b["questions"] == 6
        
        # Verify Part C structure
        part_c = content["part_c"]
        assert part_c["name"] == "Part C: Presentations and Interviews"
        assert part_c["questions"] == 12
        
        print("✓ GET /api/oet-exam/mock/NUR-013-v2/content returns exam content")
    
    def test_get_mock_exam_content_locked(self):
        """Test GET /api/oet-exam/mock/{mock_id}/content - returns 404 for locked exam"""
        response = requests.get(
            f"{BASE_URL}/api/oet-exam/mock/NUR-014/content",
            headers=self.headers
        )
        assert response.status_code == 404
        print("✓ GET /api/oet-exam/mock/NUR-014/content returns 404 for locked exam")
    
    def test_get_mock_exam_content_invalid_section(self):
        """Test GET /api/oet-exam/mock/{mock_id}/content - returns 400 for invalid section"""
        response = requests.get(
            f"{BASE_URL}/api/oet-exam/mock/NUR-013-v2/content?section=invalid",
            headers=self.headers
        )
        assert response.status_code == 400
        print("✓ GET /api/oet-exam/mock/NUR-013-v2/content returns 400 for invalid section")
    
    def test_get_institution_config(self):
        """Test GET /api/oet-exam/institution/config - returns institution OET config"""
        response = requests.get(
            f"{BASE_URL}/api/oet-exam/institution/config",
            headers=self.headers
        )
        # May return 403 if not associated with institution, or 200 with defaults
        assert response.status_code in [200, 403]
        
        if response.status_code == 200:
            data = response.json()
            assert "placement_test_enabled" in data
            assert "professions_offered" in data
            print("✓ GET /api/oet-exam/institution/config returns config")
        else:
            print("✓ GET /api/oet-exam/institution/config returns 403 (no institution)")


class TestOETExamContentValidation:
    """Test OET exam content data validation"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Login and get auth token"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": INSTITUTION_EMAIL, "password": INSTITUTION_PASSWORD}
        )
        if response.status_code == 200:
            self.token = response.json()["access_token"]
            self.headers = {"Authorization": f"Bearer {self.token}"}
        else:
            pytest.skip("Authentication failed")
    
    def test_listening_part_a_questions(self):
        """Verify Listening Part A has 24 questions with correct structure"""
        response = requests.get(
            f"{BASE_URL}/api/oet-exam/mock/NUR-013-v2/content?section=listening",
            headers=self.headers
        )
        assert response.status_code == 200
        data = response.json()
        
        part_a = data["content"]["part_a"]
        extracts = part_a["extracts"]
        
        # Count total questions across extracts
        total_questions = sum(len(e["questions"]) for e in extracts)
        assert total_questions == 24
        
        # Verify first extract has questions 1-12
        first_extract = extracts[0]
        assert first_extract["title"] == "Community Nurse Home Visit"
        assert len(first_extract["questions"]) == 12
        
        # Verify question structure
        q1 = first_extract["questions"][0]
        assert q1["id"] == 1
        assert "text" in q1
        assert "answer" in q1
        
        print("✓ Listening Part A has 24 questions with correct structure")
    
    def test_listening_part_b_multiple_choice(self):
        """Verify Listening Part B has 6 multiple choice questions"""
        response = requests.get(
            f"{BASE_URL}/api/oet-exam/mock/NUR-013-v2/content?section=listening",
            headers=self.headers
        )
        assert response.status_code == 200
        data = response.json()
        
        part_b = data["content"]["part_b"]
        extracts = part_b["extracts"]
        
        assert len(extracts) == 6
        
        # Verify each question has options A, B, C
        for extract in extracts:
            assert "options" in extract
            assert len(extract["options"]) == 3
            assert extract["options"][0].startswith("A.")
            assert extract["options"][1].startswith("B.")
            assert extract["options"][2].startswith("C.")
            assert extract["answer"] in ["A", "B", "C"]
        
        print("✓ Listening Part B has 6 multiple choice questions")
    
    def test_listening_part_c_interviews(self):
        """Verify Listening Part C has 12 questions from interviews/presentations"""
        response = requests.get(
            f"{BASE_URL}/api/oet-exam/mock/NUR-013-v2/content?section=listening",
            headers=self.headers
        )
        assert response.status_code == 200
        data = response.json()
        
        part_c = data["content"]["part_c"]
        extracts = part_c["extracts"]
        
        # Count total questions
        total_questions = sum(len(e["questions"]) for e in extracts)
        assert total_questions == 12
        
        # Verify interview structure
        interview = extracts[0]
        assert "title" in interview
        assert "questions" in interview
        
        print("✓ Listening Part C has 12 questions from interviews/presentations")


class TestOETExamMockSections:
    """Test mock exam section data"""
    
    def test_mock_sections_structure(self):
        """Verify mock exam has correct section structure"""
        response = requests.get(f"{BASE_URL}/api/oet-exam/mocks/available")
        assert response.status_code == 200
        data = response.json()
        
        nur_013 = next(m for m in data["mocks"] if m["id"] == "NUR-013-v2")
        sections = nur_013["sections"]
        
        # Verify listening section
        assert sections["listening"]["duration"] == 50
        assert sections["listening"]["questions"] == 42
        
        # Verify reading section
        assert sections["reading"]["duration"] == 60
        assert sections["reading"]["questions"] == 42
        
        # Verify writing section
        assert sections["writing"]["duration"] == 45
        assert sections["writing"]["questions"] == 1
        
        # Verify speaking section
        assert sections["speaking"]["duration"] == 20
        assert sections["speaking"]["questions"] == 2
        
        print("✓ Mock exam has correct section structure")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
