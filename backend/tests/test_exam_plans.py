"""
Test Suite for Exam Plans & Consumable Mocks Feature
Tests: Plan creation, purchase, credit consumption, mock exams, PDF generation, upsells
"""
import pytest
import requests
import os
import time
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test data
TEST_TIMESTAMP = str(int(time.time()))
INSTITUTION_EMAIL = f"TEST_exam_plans_inst_{TEST_TIMESTAMP}@test.com"
INSTITUTION_PASSWORD = "TestPass123!"
STUDENT_EMAIL = f"TEST_exam_plans_student_{TEST_TIMESTAMP}@test.com"


class TestExamPlansSetup:
    """Setup tests - Create institution and student"""
    
    institution_token = None
    institution_id = None
    student_token = None
    student_id = None
    student_password = None
    plan_id = None
    purchase_id = None
    attempt_id = None
    
    @pytest.fixture(autouse=True)
    def setup_class_vars(self, request):
        """Share variables across test class"""
        request.cls.institution_token = TestExamPlansSetup.institution_token
        request.cls.institution_id = TestExamPlansSetup.institution_id
        request.cls.student_token = TestExamPlansSetup.student_token
        request.cls.student_id = TestExamPlansSetup.student_id
        request.cls.student_password = TestExamPlansSetup.student_password
        request.cls.plan_id = TestExamPlansSetup.plan_id
        request.cls.purchase_id = TestExamPlansSetup.purchase_id
        request.cls.attempt_id = TestExamPlansSetup.attempt_id
    
    def test_01_create_institution(self):
        """Create test institution"""
        response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": INSTITUTION_EMAIL,
            "name": "Test Exam Plans Institution",
            "password": INSTITUTION_PASSWORD,
            "user_type": "institution",
            "institution_name": "Test Academy"
        })
        
        assert response.status_code == 200, f"Failed to create institution: {response.text}"
        data = response.json()
        assert "access_token" in data
        assert data["user"]["user_type"] == "institution"
        
        TestExamPlansSetup.institution_token = data["access_token"]
        TestExamPlansSetup.institution_id = data["user"]["id"]
        print(f"✓ Institution created: {INSTITUTION_EMAIL}")
    
    def test_02_create_student(self):
        """Create test student under institution"""
        headers = {"Authorization": f"Bearer {TestExamPlansSetup.institution_token}"}
        
        response = requests.post(f"{BASE_URL}/api/institution/students/create", 
            headers=headers,
            json={
                "email": STUDENT_EMAIL,
                "name": "Test Exam Student",
                "exam_type": "oet",
                "credits": 100
            }
        )
        
        assert response.status_code == 200, f"Failed to create student: {response.text}"
        data = response.json()
        assert "provisional_password" in data
        assert data["exam_type"] == "oet"
        
        TestExamPlansSetup.student_id = data["id"]
        TestExamPlansSetup.student_password = data["provisional_password"]
        print(f"✓ Student created: {STUDENT_EMAIL}")
    
    def test_03_student_login(self):
        """Student logs in with provisional password"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": STUDENT_EMAIL,
            "password": TestExamPlansSetup.student_password
        })
        
        assert response.status_code == 200, f"Student login failed: {response.text}"
        data = response.json()
        assert "access_token" in data
        assert data["user"]["user_type"] == "student"
        assert data["user"]["institution_id"] == TestExamPlansSetup.institution_id
        
        TestExamPlansSetup.student_token = data["access_token"]
        print(f"✓ Student logged in successfully")


class TestExamPlansCRUD:
    """Test Plan CRUD operations by institution"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        self.institution_token = TestExamPlansSetup.institution_token
        self.student_token = TestExamPlansSetup.student_token
    
    def test_01_create_exam_plan(self):
        """Institution creates an exam plan"""
        headers = {"Authorization": f"Bearer {self.institution_token}"}
        
        response = requests.post(f"{BASE_URL}/api/exam-plans/plans", 
            headers=headers,
            json={
                "name": "OET Starter Pack",
                "exam_type": "oet",
                "mock_count": 5,
                "speaking_sessions": 2,
                "writing_evaluations": 3,
                "ai_tutor_hours": 5,
                "price": 49.99,
                "currency": "USD",
                "description": "Perfect for beginners",
                "features": ["5 Full Mocks", "2 Speaking Sessions", "AI Tutor Access"],
                "is_active": True
            }
        )
        
        assert response.status_code == 200, f"Failed to create plan: {response.text}"
        data = response.json()
        assert "id" in data
        assert data["plan"]["name"] == "OET Starter Pack"
        assert data["plan"]["mock_count"] == 5
        assert data["plan"]["price"] == 49.99
        
        TestExamPlansSetup.plan_id = data["id"]
        print(f"✓ Plan created: {data['id']}")
    
    def test_02_get_plans_as_institution(self):
        """Institution gets their plans"""
        headers = {"Authorization": f"Bearer {self.institution_token}"}
        
        response = requests.get(f"{BASE_URL}/api/exam-plans/plans", headers=headers)
        
        assert response.status_code == 200, f"Failed to get plans: {response.text}"
        data = response.json()
        assert "plans" in data
        assert len(data["plans"]) >= 1
        
        # Find our created plan
        our_plan = next((p for p in data["plans"] if p["id"] == TestExamPlansSetup.plan_id), None)
        assert our_plan is not None, "Created plan not found"
        print(f"✓ Institution can view {len(data['plans'])} plans")
    
    def test_03_get_plans_as_student(self):
        """Student gets available plans from their institution"""
        headers = {"Authorization": f"Bearer {self.student_token}"}
        
        response = requests.get(f"{BASE_URL}/api/exam-plans/plans", headers=headers)
        
        assert response.status_code == 200, f"Failed to get plans as student: {response.text}"
        data = response.json()
        assert "plans" in data
        
        # Student should see institution's plans
        our_plan = next((p for p in data["plans"] if p["id"] == TestExamPlansSetup.plan_id), None)
        assert our_plan is not None, "Student cannot see institution's plan"
        print(f"✓ Student can view {len(data['plans'])} available plans")
    
    def test_04_get_plan_details(self):
        """Get specific plan details"""
        headers = {"Authorization": f"Bearer {self.student_token}"}
        
        response = requests.get(f"{BASE_URL}/api/exam-plans/plans/{TestExamPlansSetup.plan_id}", headers=headers)
        
        assert response.status_code == 200, f"Failed to get plan details: {response.text}"
        data = response.json()
        assert data["id"] == TestExamPlansSetup.plan_id
        assert data["name"] == "OET Starter Pack"
        assert data["mock_count"] == 5
        print(f"✓ Plan details retrieved successfully")
    
    def test_05_update_plan(self):
        """Institution updates a plan"""
        headers = {"Authorization": f"Bearer {self.institution_token}"}
        
        response = requests.put(f"{BASE_URL}/api/exam-plans/plans/{TestExamPlansSetup.plan_id}", 
            headers=headers,
            json={
                "name": "OET Starter Pack - Updated",
                "exam_type": "oet",
                "mock_count": 6,  # Increased
                "speaking_sessions": 2,
                "writing_evaluations": 3,
                "ai_tutor_hours": 5,
                "price": 54.99,  # Price increased
                "currency": "USD",
                "description": "Perfect for beginners - Now with more mocks!",
                "features": ["6 Full Mocks", "2 Speaking Sessions", "AI Tutor Access"],
                "is_active": True
            }
        )
        
        assert response.status_code == 200, f"Failed to update plan: {response.text}"
        print(f"✓ Plan updated successfully")
    
    def test_06_student_cannot_create_plan(self):
        """Student cannot create plans (403)"""
        headers = {"Authorization": f"Bearer {self.student_token}"}
        
        response = requests.post(f"{BASE_URL}/api/exam-plans/plans", 
            headers=headers,
            json={
                "name": "Unauthorized Plan",
                "exam_type": "oet",
                "mock_count": 5,
                "price": 49.99
            }
        )
        
        assert response.status_code == 403, f"Expected 403, got {response.status_code}"
        print(f"✓ Student correctly denied plan creation (403)")


class TestPurchaseAndCredits:
    """Test plan purchase and credit system"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        self.institution_token = TestExamPlansSetup.institution_token
        self.student_token = TestExamPlansSetup.student_token
    
    def test_01_student_purchases_plan(self):
        """Student purchases a plan"""
        headers = {"Authorization": f"Bearer {self.student_token}"}
        
        response = requests.post(f"{BASE_URL}/api/exam-plans/purchase", 
            headers=headers,
            json={
                "plan_id": TestExamPlansSetup.plan_id,
                "payment_method": "stripe",
                "stripe_payment_intent_id": "pi_test_mock_payment"
            }
        )
        
        assert response.status_code == 200, f"Failed to purchase plan: {response.text}"
        data = response.json()
        assert "purchase_id" in data
        assert data["purchase"]["mocks_total"] == 6  # Updated value
        assert data["purchase"]["mocks_remaining"] == 6
        assert data["purchase"]["status"] == "completed"
        
        TestExamPlansSetup.purchase_id = data["purchase_id"]
        print(f"✓ Plan purchased: {data['purchase_id']}")
    
    def test_02_get_my_credits(self):
        """Student checks their credit balance"""
        headers = {"Authorization": f"Bearer {self.student_token}"}
        
        response = requests.get(f"{BASE_URL}/api/exam-plans/my-credits", headers=headers)
        
        assert response.status_code == 200, f"Failed to get credits: {response.text}"
        data = response.json()
        
        assert "credits" in data
        assert data["credits"]["mocks"]["remaining"] == 6
        assert data["credits"]["speaking"]["remaining"] == 2
        assert data["credits"]["writing"]["remaining"] == 3
        assert data["can_take_mock"] == True
        print(f"✓ Credits retrieved: {data['credits']['mocks']['remaining']} mocks remaining")
    
    def test_03_get_my_purchases(self):
        """Student views purchase history"""
        headers = {"Authorization": f"Bearer {self.student_token}"}
        
        response = requests.get(f"{BASE_URL}/api/exam-plans/my-purchases", headers=headers)
        
        assert response.status_code == 200, f"Failed to get purchases: {response.text}"
        data = response.json()
        
        assert "purchases" in data
        assert len(data["purchases"]) >= 1
        
        our_purchase = next((p for p in data["purchases"] if p["id"] == TestExamPlansSetup.purchase_id), None)
        assert our_purchase is not None
        print(f"✓ Purchase history retrieved: {len(data['purchases'])} purchases")
    
    def test_04_institution_cannot_purchase(self):
        """Institution cannot purchase plans (403)"""
        headers = {"Authorization": f"Bearer {self.institution_token}"}
        
        response = requests.post(f"{BASE_URL}/api/exam-plans/purchase", 
            headers=headers,
            json={
                "plan_id": TestExamPlansSetup.plan_id,
                "payment_method": "stripe"
            }
        )
        
        assert response.status_code == 403, f"Expected 403, got {response.status_code}"
        print(f"✓ Institution correctly denied purchase (403)")


class TestMockExamFlow:
    """Test mock exam start, submit, and credit consumption"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        self.student_token = TestExamPlansSetup.student_token
        self.institution_token = TestExamPlansSetup.institution_token
    
    def test_01_start_full_mock(self):
        """Student starts a full mock exam (consumes 1 credit)"""
        headers = {"Authorization": f"Bearer {self.student_token}"}
        
        response = requests.post(f"{BASE_URL}/api/exam-plans/start-mock", 
            headers=headers,
            json={
                "exam_type": "oet",
                "section": None,  # Full mock
                "timed": True
            }
        )
        
        assert response.status_code == 200, f"Failed to start mock: {response.text}"
        data = response.json()
        
        assert "attempt_id" in data
        assert data["exam_type"] == "oet"
        assert data["section"] is None
        assert "questions" in data
        assert data["mocks_remaining_after"] == 5  # 6 - 1 = 5
        
        TestExamPlansSetup.attempt_id = data["attempt_id"]
        print(f"✓ Mock started: {data['attempt_id']}, {data['mocks_remaining_after']} mocks remaining")
    
    def test_02_verify_credit_deduction(self):
        """Verify credit was deducted after starting mock"""
        headers = {"Authorization": f"Bearer {self.student_token}"}
        
        response = requests.get(f"{BASE_URL}/api/exam-plans/my-credits", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["credits"]["mocks"]["remaining"] == 5  # Was 6, now 5
        assert data["credits"]["mocks"]["used"] == 1
        print(f"✓ Credit deduction verified: {data['credits']['mocks']['used']} used")
    
    def test_03_submit_mock(self):
        """Student submits completed mock exam"""
        headers = {"Authorization": f"Bearer {self.student_token}"}
        
        response = requests.post(f"{BASE_URL}/api/exam-plans/submit-mock", 
            headers=headers,
            json={
                "attempt_id": TestExamPlansSetup.attempt_id,
                "answers": {
                    "q1": "A",
                    "q2": "B",
                    "q3": "C"
                },
                "time_taken_seconds": 3600
            }
        )
        
        assert response.status_code == 200, f"Failed to submit mock: {response.text}"
        data = response.json()
        
        assert data["attempt_id"] == TestExamPlansSetup.attempt_id
        assert "score" in data
        assert "section_scores" in data
        assert "feedback" in data
        assert data["pdf_available"] == True
        print(f"✓ Mock submitted: Score {data['score']}%")
    
    def test_04_get_attempt_details(self):
        """Get details of completed attempt"""
        headers = {"Authorization": f"Bearer {self.student_token}"}
        
        response = requests.get(f"{BASE_URL}/api/exam-plans/attempt/{TestExamPlansSetup.attempt_id}", headers=headers)
        
        assert response.status_code == 200, f"Failed to get attempt: {response.text}"
        data = response.json()
        
        assert data["id"] == TestExamPlansSetup.attempt_id
        assert data["status"] == "completed"
        assert "score" in data
        assert "feedback" in data
        print(f"✓ Attempt details retrieved")
    
    def test_05_start_section_practice_free(self):
        """Section practice is FREE (doesn't consume credits)"""
        headers = {"Authorization": f"Bearer {self.student_token}"}
        
        # Get current credits
        credits_before = requests.get(f"{BASE_URL}/api/exam-plans/my-credits", headers=headers).json()
        mocks_before = credits_before["credits"]["mocks"]["remaining"]
        
        # Start section practice
        response = requests.post(f"{BASE_URL}/api/exam-plans/start-mock", 
            headers=headers,
            json={
                "exam_type": "oet",
                "section": "reading",  # Section practice
                "timed": True
            }
        )
        
        assert response.status_code == 200, f"Failed to start section: {response.text}"
        data = response.json()
        
        # Credits should NOT be deducted for section practice
        assert data["mocks_remaining_after"] == mocks_before
        print(f"✓ Section practice started (FREE): {mocks_before} mocks still remaining")
    
    def test_06_get_exam_history(self):
        """Student views exam history"""
        headers = {"Authorization": f"Bearer {self.student_token}"}
        
        response = requests.get(f"{BASE_URL}/api/exam-plans/my-history?exam_type=oet&limit=10", headers=headers)
        
        assert response.status_code == 200, f"Failed to get history: {response.text}"
        data = response.json()
        
        assert "attempts" in data
        assert len(data["attempts"]) >= 1
        
        # Find our completed attempt
        our_attempt = next((a for a in data["attempts"] if a["id"] == TestExamPlansSetup.attempt_id), None)
        assert our_attempt is not None
        assert our_attempt["status"] == "completed"
        print(f"✓ Exam history retrieved: {len(data['attempts'])} attempts")


class TestPDFGeneration:
    """Test PDF feedback report generation"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        self.student_token = TestExamPlansSetup.student_token
        self.institution_token = TestExamPlansSetup.institution_token
    
    def test_01_download_pdf_as_student(self):
        """Student downloads PDF feedback report"""
        headers = {"Authorization": f"Bearer {self.student_token}"}
        
        response = requests.get(
            f"{BASE_URL}/api/exam-plans/attempt/{TestExamPlansSetup.attempt_id}/pdf", 
            headers=headers
        )
        
        assert response.status_code == 200, f"Failed to download PDF: {response.text}"
        assert response.headers.get("content-type") == "application/pdf"
        assert "attachment" in response.headers.get("content-disposition", "")
        assert len(response.content) > 100  # PDF should have content
        print(f"✓ PDF downloaded: {len(response.content)} bytes")
    
    def test_02_download_pdf_as_institution(self):
        """Institution can also download student's PDF"""
        headers = {"Authorization": f"Bearer {self.institution_token}"}
        
        response = requests.get(
            f"{BASE_URL}/api/exam-plans/attempt/{TestExamPlansSetup.attempt_id}/pdf", 
            headers=headers
        )
        
        assert response.status_code == 200, f"Institution failed to download PDF: {response.text}"
        assert response.headers.get("content-type") == "application/pdf"
        print(f"✓ Institution can download student's PDF")
    
    def test_03_pdf_not_found_for_invalid_attempt(self):
        """PDF returns 404 for invalid attempt"""
        headers = {"Authorization": f"Bearer {self.student_token}"}
        
        response = requests.get(
            f"{BASE_URL}/api/exam-plans/attempt/invalid-attempt-id/pdf", 
            headers=headers
        )
        
        assert response.status_code == 404
        print(f"✓ Invalid attempt returns 404")


class TestUpsellOptions:
    """Test upsell functionality when credits are low"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        self.student_token = TestExamPlansSetup.student_token
        self.institution_token = TestExamPlansSetup.institution_token
    
    def test_01_get_upsell_options(self):
        """Student gets upsell options"""
        headers = {"Authorization": f"Bearer {self.student_token}"}
        
        response = requests.get(f"{BASE_URL}/api/exam-plans/upsell-options", headers=headers)
        
        assert response.status_code == 200, f"Failed to get upsell: {response.text}"
        data = response.json()
        
        assert "current_credits" in data
        assert "available_plans" in data
        assert "quick_buys" in data
        
        # Verify quick buy options
        assert len(data["quick_buys"]) >= 1
        quick_buy_types = [qb["type"] for qb in data["quick_buys"]]
        assert "single_mock" in quick_buy_types
        print(f"✓ Upsell options retrieved: {len(data['available_plans'])} plans, {len(data['quick_buys'])} quick buys")
    
    def test_02_institution_cannot_view_upsells(self):
        """Institution cannot view upsell options (403)"""
        headers = {"Authorization": f"Bearer {self.institution_token}"}
        
        response = requests.get(f"{BASE_URL}/api/exam-plans/upsell-options", headers=headers)
        
        assert response.status_code == 403
        print(f"✓ Institution correctly denied upsell view (403)")


class TestInstitutionAnalytics:
    """Test institution analytics endpoints"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        self.institution_token = TestExamPlansSetup.institution_token
        self.student_token = TestExamPlansSetup.student_token
    
    def test_01_get_analytics_overview(self):
        """Institution gets analytics overview"""
        headers = {"Authorization": f"Bearer {self.institution_token}"}
        
        response = requests.get(f"{BASE_URL}/api/institution/analytics/overview", headers=headers)
        
        assert response.status_code == 200, f"Failed to get analytics: {response.text}"
        data = response.json()
        
        assert "kpis" in data
        assert "total_students" in data["kpis"]
        assert "risk_distribution" in data
        assert "exam_distribution" in data
        print(f"✓ Analytics overview: {data['kpis']['total_students']} students")
    
    def test_02_get_at_risk_students(self):
        """Institution gets at-risk students"""
        headers = {"Authorization": f"Bearer {self.institution_token}"}
        
        response = requests.get(f"{BASE_URL}/api/institution/analytics/at-risk", headers=headers)
        
        assert response.status_code == 200, f"Failed to get at-risk: {response.text}"
        data = response.json()
        
        # Response has 'students' and 'total_at_risk' keys
        assert "students" in data or "at_risk_students" in data
        assert "total_at_risk" in data
        print(f"✓ At-risk students: {data['total_at_risk']} total")
    
    def test_03_student_cannot_access_analytics(self):
        """Student cannot access institution analytics (403)"""
        headers = {"Authorization": f"Bearer {self.student_token}"}
        
        response = requests.get(f"{BASE_URL}/api/institution/analytics/overview", headers=headers)
        
        assert response.status_code == 403
        print(f"✓ Student correctly denied analytics access (403)")


class TestAuthenticationRequired:
    """Test that all endpoints require authentication"""
    
    def test_01_plans_requires_auth(self):
        """GET /plans requires authentication"""
        response = requests.get(f"{BASE_URL}/api/exam-plans/plans")
        assert response.status_code == 401
        print(f"✓ /plans requires auth (401)")
    
    def test_02_purchase_requires_auth(self):
        """POST /purchase requires authentication"""
        response = requests.post(f"{BASE_URL}/api/exam-plans/purchase", json={
            "plan_id": "test",
            "payment_method": "stripe"
        })
        assert response.status_code == 401
        print(f"✓ /purchase requires auth (401)")
    
    def test_03_credits_requires_auth(self):
        """GET /my-credits requires authentication"""
        response = requests.get(f"{BASE_URL}/api/exam-plans/my-credits")
        assert response.status_code == 401
        print(f"✓ /my-credits requires auth (401)")
    
    def test_04_start_mock_requires_auth(self):
        """POST /start-mock requires authentication"""
        response = requests.post(f"{BASE_URL}/api/exam-plans/start-mock", json={
            "exam_type": "oet"
        })
        assert response.status_code == 401
        print(f"✓ /start-mock requires auth (401)")
    
    def test_05_analytics_requires_auth(self):
        """GET /analytics/overview requires authentication"""
        response = requests.get(f"{BASE_URL}/api/institution/analytics/overview")
        # Returns 401 or 403 depending on auth middleware
        assert response.status_code in [401, 403]
        print(f"✓ /analytics/overview requires auth ({response.status_code})")


class TestEdgeCases:
    """Test edge cases and error handling"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        self.student_token = TestExamPlansSetup.student_token
        self.institution_token = TestExamPlansSetup.institution_token
    
    def test_01_purchase_nonexistent_plan(self):
        """Cannot purchase non-existent plan"""
        headers = {"Authorization": f"Bearer {self.student_token}"}
        
        response = requests.post(f"{BASE_URL}/api/exam-plans/purchase", 
            headers=headers,
            json={
                "plan_id": "nonexistent-plan-id",
                "payment_method": "stripe"
            }
        )
        
        assert response.status_code == 404
        print(f"✓ Non-existent plan returns 404")
    
    def test_02_submit_nonexistent_attempt(self):
        """Cannot submit non-existent attempt"""
        headers = {"Authorization": f"Bearer {self.student_token}"}
        
        response = requests.post(f"{BASE_URL}/api/exam-plans/submit-mock", 
            headers=headers,
            json={
                "attempt_id": "nonexistent-attempt-id",
                "answers": {},
                "time_taken_seconds": 100
            }
        )
        
        assert response.status_code == 404
        print(f"✓ Non-existent attempt returns 404")
    
    def test_03_get_nonexistent_attempt(self):
        """Cannot get non-existent attempt"""
        headers = {"Authorization": f"Bearer {self.student_token}"}
        
        response = requests.get(f"{BASE_URL}/api/exam-plans/attempt/nonexistent-id", headers=headers)
        
        assert response.status_code == 404
        print(f"✓ Non-existent attempt details returns 404")


class TestCleanup:
    """Cleanup test - deactivate plan"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        self.institution_token = TestExamPlansSetup.institution_token
    
    def test_01_deactivate_plan(self):
        """Institution deactivates (soft deletes) plan"""
        headers = {"Authorization": f"Bearer {self.institution_token}"}
        
        response = requests.delete(
            f"{BASE_URL}/api/exam-plans/plans/{TestExamPlansSetup.plan_id}", 
            headers=headers
        )
        
        assert response.status_code == 200, f"Failed to deactivate plan: {response.text}"
        print(f"✓ Plan deactivated successfully")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
