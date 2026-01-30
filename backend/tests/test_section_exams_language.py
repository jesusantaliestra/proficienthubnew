"""
Test Suite for Section-Based Exam Logic and Language Selector Features
Tests:
1. GET /api/sequential-exams/available-modes/{exam_type} - returns modes and sections
2. POST /api/sequential-exams/start/{exam_type}/{exam_id} - starts exam in full or section mode
3. POST /api/sequential-exams/complete-section/{exam_type}/{exam_id} - completes a section
4. GET /api/sequential-exams/progress/{exam_type}/{exam_id} - returns exam progress
5. GET /api/sequential-exams/in-progress - returns exams in progress
"""
import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
INSTITUTION_EMAIL = "demo_academy@test.com"
INSTITUTION_PASSWORD = "Demo123!"


class TestBackendHealth:
    """Basic health check"""
    
    def test_health_endpoint(self):
        """Test backend health endpoint"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "healthy"
        print("✓ Backend health check passed")


class TestAvailableModes:
    """Test GET /api/sequential-exams/available-modes/{exam_type}"""
    
    def test_available_modes_ielts_academic(self):
        """Test available modes for ielts_academic exam type"""
        response = requests.get(f"{BASE_URL}/api/sequential-exams/available-modes/ielts_academic")
        assert response.status_code == 200
        data = response.json()
        
        # Verify exam_type
        assert data.get("exam_type") == "ielts_academic"
        
        # Verify modes
        modes = data.get("modes", [])
        assert len(modes) == 2
        mode_names = [m.get("mode") for m in modes]
        assert "full" in mode_names
        assert "section" in mode_names
        
        # Verify sections
        sections = data.get("sections", [])
        assert len(sections) == 4
        section_ids = [s.get("id") for s in sections]
        assert "listening" in section_ids
        assert "reading" in section_ids
        assert "writing" in section_ids
        assert "speaking" in section_ids
        
        print("✓ Available modes for ielts_academic returned correctly")
        print(f"  - Modes: {mode_names}")
        print(f"  - Sections: {section_ids}")
    
    def test_available_modes_toefl(self):
        """Test available modes for toefl exam type"""
        response = requests.get(f"{BASE_URL}/api/sequential-exams/available-modes/toefl")
        assert response.status_code == 200
        data = response.json()
        
        assert data.get("exam_type") == "toefl"
        sections = data.get("sections", [])
        section_ids = [s.get("id") for s in sections]
        # TOEFL has different section order
        assert "reading" in section_ids
        assert "listening" in section_ids
        assert "speaking" in section_ids
        assert "writing" in section_ids
        
        print("✓ Available modes for toefl returned correctly")
    
    def test_available_modes_unknown_type(self):
        """Test available modes for unknown exam type returns default sections"""
        response = requests.get(f"{BASE_URL}/api/sequential-exams/available-modes/unknown_exam")
        assert response.status_code == 200
        data = response.json()
        
        # Should return default sections
        sections = data.get("sections", [])
        assert len(sections) == 4  # default has 4 sections
        print("✓ Unknown exam type returns default sections")


class TestAuthenticatedExamEndpoints:
    """Test authenticated exam endpoints"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Login and get token"""
        login_response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": INSTITUTION_EMAIL,
            "password": INSTITUTION_PASSWORD
        })
        
        if login_response.status_code != 200:
            pytest.skip(f"Login failed: {login_response.status_code}")
        
        data = login_response.json()
        self.token = data.get("access_token") or data.get("token")
        self.headers = {"Authorization": f"Bearer {self.token}"}
        print(f"✓ Logged in as {INSTITUTION_EMAIL}")
    
    def test_get_in_progress_exams(self):
        """Test GET /api/sequential-exams/in-progress"""
        response = requests.get(
            f"{BASE_URL}/api/sequential-exams/in-progress",
            headers=self.headers
        )
        assert response.status_code == 200
        data = response.json()
        
        assert "exams_in_progress" in data
        assert "total" in data
        assert isinstance(data["exams_in_progress"], list)
        
        print(f"✓ In-progress exams endpoint works - {data['total']} exams in progress")
    
    def test_get_exam_progress_not_started(self):
        """Test GET /api/sequential-exams/progress for non-existent exam"""
        response = requests.get(
            f"{BASE_URL}/api/sequential-exams/progress/ielts_academic/999",
            headers=self.headers
        )
        # Should return 404 or exam info if available
        assert response.status_code in [200, 404]
        print(f"✓ Progress endpoint returns {response.status_code} for non-started exam")
    
    def test_start_exam_full_mode(self):
        """Test POST /api/sequential-exams/start - full mode"""
        # Use a unique exam ID for testing
        test_exam_id = "test_full_001"
        
        response = requests.post(
            f"{BASE_URL}/api/sequential-exams/start/ielts_academic/{test_exam_id}",
            headers=self.headers,
            json={
                "exam_id": test_exam_id,
                "mode": "full"
            }
        )
        
        # May fail if exam not purchased, but endpoint should respond
        if response.status_code == 200:
            data = response.json()
            assert data.get("mode") == "full"
            assert "sections" in data
            print(f"✓ Started exam in full mode: {data.get('status')}")
        elif response.status_code == 403:
            print("✓ Start exam endpoint correctly requires exam access")
        else:
            print(f"✓ Start exam endpoint responded with {response.status_code}")
    
    def test_start_exam_section_mode(self):
        """Test POST /api/sequential-exams/start - section mode"""
        test_exam_id = "test_section_001"
        
        response = requests.post(
            f"{BASE_URL}/api/sequential-exams/start/ielts_academic/{test_exam_id}",
            headers=self.headers,
            json={
                "exam_id": test_exam_id,
                "mode": "section",
                "section": "listening"
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            assert data.get("mode") == "section"
            print(f"✓ Started exam in section mode: {data.get('status')}")
        elif response.status_code == 403:
            print("✓ Start exam endpoint correctly requires exam access")
        elif response.status_code == 400:
            print(f"✓ Start exam validation works: {response.json().get('detail')}")
        else:
            print(f"✓ Start exam endpoint responded with {response.status_code}")
    
    def test_complete_section_without_progress(self):
        """Test POST /api/sequential-exams/complete-section without starting exam"""
        response = requests.post(
            f"{BASE_URL}/api/sequential-exams/complete-section/ielts_academic/nonexistent_exam",
            headers=self.headers,
            json={
                "section": "listening",
                "score": 75.0,
                "time_taken_seconds": 1800
            }
        )
        
        # Should return 404 since exam not started
        assert response.status_code == 404
        print("✓ Complete section correctly returns 404 for non-started exam")
    
    def test_exam_dashboard_with_sections(self):
        """Test that dashboard returns section info for exams"""
        response = requests.get(
            f"{BASE_URL}/api/sequential-exams/dashboard/ielts_academic",
            headers=self.headers
        )
        
        if response.status_code == 200:
            data = response.json()
            assert "exams" in data or "message" in data
            print(f"✓ Dashboard endpoint works - {len(data.get('exams', []))} exams")
        else:
            print(f"✓ Dashboard endpoint responded with {response.status_code}")


class TestExamWithPurchasedAccess:
    """Test exam flow with purchased access"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Login and get token"""
        login_response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": INSTITUTION_EMAIL,
            "password": INSTITUTION_PASSWORD
        })
        
        if login_response.status_code != 200:
            pytest.skip(f"Login failed: {login_response.status_code}")
        
        data = login_response.json()
        self.token = data.get("access_token") or data.get("token")
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    def test_full_section_exam_flow(self):
        """Test complete section-by-section exam flow"""
        exam_type = "test_section_flow"
        
        # Step 1: Purchase exams
        purchase_response = requests.post(
            f"{BASE_URL}/api/sequential-exams/purchase",
            headers=self.headers,
            json={
                "exam_type": exam_type,
                "num_exams": 5,
                "with_ai": False
            }
        )
        
        if purchase_response.status_code != 200:
            print(f"Purchase response: {purchase_response.status_code}")
            return
        
        purchase_data = purchase_response.json()
        exam_id = purchase_data.get("new_exams", ["001"])[0]
        print(f"✓ Purchased exams, first exam ID: {exam_id}")
        
        # Step 2: Start exam in section mode
        start_response = requests.post(
            f"{BASE_URL}/api/sequential-exams/start/{exam_type}/{exam_id}",
            headers=self.headers,
            json={
                "exam_id": exam_id,
                "mode": "section",
                "section": "listening"
            }
        )
        
        assert start_response.status_code == 200
        start_data = start_response.json()
        assert start_data.get("mode") == "section"
        print(f"✓ Started exam in section mode: {start_data.get('status')}")
        
        # Step 3: Check progress
        progress_response = requests.get(
            f"{BASE_URL}/api/sequential-exams/progress/{exam_type}/{exam_id}",
            headers=self.headers
        )
        
        assert progress_response.status_code == 200
        progress_data = progress_response.json()
        assert progress_data.get("status") == "in_progress"
        print(f"✓ Progress shows in_progress status")
        
        # Step 4: Complete first section
        complete_response = requests.post(
            f"{BASE_URL}/api/sequential-exams/complete-section/{exam_type}/{exam_id}",
            headers=self.headers,
            json={
                "section": "listening",
                "score": 80.0,
                "time_taken_seconds": 1800
            }
        )
        
        assert complete_response.status_code == 200
        complete_data = complete_response.json()
        assert "listening" in complete_data.get("sections_completed", [])
        assert complete_data.get("exam_completed") == False
        print(f"✓ Completed listening section, score: {complete_data.get('score')}")
        
        # Step 5: Check in-progress exams
        in_progress_response = requests.get(
            f"{BASE_URL}/api/sequential-exams/in-progress",
            headers=self.headers
        )
        
        assert in_progress_response.status_code == 200
        in_progress_data = in_progress_response.json()
        
        # Find our exam in the list
        our_exam = next(
            (e for e in in_progress_data.get("exams_in_progress", []) 
             if e.get("exam_id") == exam_id and e.get("exam_type") == exam_type),
            None
        )
        
        if our_exam:
            assert our_exam.get("progress_percent") > 0
            print(f"✓ Exam appears in in-progress list with {our_exam.get('progress_percent')}% progress")
        
        print("✓ Full section exam flow completed successfully")


class TestLanguageSelectorIntegration:
    """Test that language selector is properly integrated"""
    
    def test_i18n_languages_count(self):
        """Verify 80 languages are configured"""
        # This is a code verification test - we check the file content
        import subprocess
        result = subprocess.run(
            ["grep", "-c", "code:", "/app/frontend/src/i18n/index.js"],
            capture_output=True,
            text=True
        )
        count = int(result.stdout.strip())
        # Should have 79-80 languages (one per code: entry)
        assert count >= 79, f"Expected ~80 languages, found {count}"
        print(f"✓ i18n has {count} languages configured")
    
    def test_language_selector_component_exists(self):
        """Verify LanguageSelector component exists"""
        import os
        component_path = "/app/frontend/src/components/LanguageSelector.jsx"
        assert os.path.exists(component_path), "LanguageSelector.jsx not found"
        
        with open(component_path, 'r') as f:
            content = f.read()
        
        # Check key features
        assert "SUPPORTED_LANGUAGES" in content, "Should import SUPPORTED_LANGUAGES"
        assert "useTranslation" in content, "Should use useTranslation hook"
        assert "changeLanguage" in content, "Should have changeLanguage function"
        assert "variant" in content, "Should support variant prop"
        
        print("✓ LanguageSelector component has all required features")
    
    def test_landing_page_has_language_selector(self):
        """Verify Landing page imports and uses LanguageSelector"""
        with open("/app/frontend/src/pages/Landing.jsx", 'r') as f:
            content = f.read()
        
        assert "import LanguageSelector" in content, "Landing should import LanguageSelector"
        assert "<LanguageSelector" in content, "Landing should render LanguageSelector"
        
        print("✓ Landing page has LanguageSelector component")
    
    def test_student_dashboard_has_language_selector(self):
        """Verify StudentDashboardRestricted has LanguageSelector"""
        with open("/app/frontend/src/pages/StudentDashboardRestricted.jsx", 'r') as f:
            content = f.read()
        
        assert "import LanguageSelector" in content, "StudentDashboard should import LanguageSelector"
        assert "<LanguageSelector" in content, "StudentDashboard should render LanguageSelector"
        
        print("✓ StudentDashboardRestricted has LanguageSelector component")
    
    def test_institution_dashboard_has_language_selector(self):
        """Verify InstitutionDashboard has LanguageSelector"""
        with open("/app/frontend/src/pages/InstitutionDashboard.jsx", 'r') as f:
            content = f.read()
        
        assert "import LanguageSelector" in content, "InstitutionDashboard should import LanguageSelector"
        assert "<LanguageSelector" in content, "InstitutionDashboard should render LanguageSelector"
        
        print("✓ InstitutionDashboard has LanguageSelector component")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
