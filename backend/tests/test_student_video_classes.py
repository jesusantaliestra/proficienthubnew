"""
Test Student and Video Classes Endpoints
Tests for:
- Student profile, credits, use-credits, upcoming-classes, placement test
- Video classes list, enrollment, status update
Note: Some endpoints are in server.py, some in new routers
"""
import pytest
import requests
import os
import uuid
from datetime import datetime, timezone, timedelta

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
STUDENT_EMAIL = "gamification_test@demo.com"
STUDENT_PASSWORD = "Test123!"
INSTITUTION_EMAIL = "demo_academy@test.com"
INSTITUTION_PASSWORD = "Demo123!"


class TestStudentEndpoints:
    """Tests for Student endpoints (mix of server.py and student router)"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test fixtures"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        
        # Login as student
        response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": STUDENT_EMAIL,
            "password": STUDENT_PASSWORD
        })
        assert response.status_code == 200, f"Student login failed: {response.text}"
        data = response.json()
        self.student_token = data.get("access_token")
        self.student_user = data.get("user")
        assert self.student_token, "No access token received"
        
        self.auth_headers = {"Authorization": f"Bearer {self.student_token}"}
    
    def test_student_profile_endpoint(self):
        """Test GET /api/student/profile returns correct data (server.py endpoint)"""
        response = self.session.get(
            f"{BASE_URL}/api/student/profile",
            headers=self.auth_headers
        )
        
        assert response.status_code == 200, f"Profile endpoint failed: {response.text}"
        data = response.json()
        
        # Validate response structure (server.py format)
        assert "id" in data, "Missing 'id' in profile response"
        assert "email" in data, "Missing 'email' in profile response"
        assert "credits" in data, "Missing 'credits' in profile response"
        assert "current_exam" in data, "Missing 'current_exam' in profile response"
        
        # Validate data values
        assert data["email"] == STUDENT_EMAIL, f"Email mismatch: {data['email']}"
        assert isinstance(data["credits"], int), "Credits should be an integer"
        
        print(f"✓ Student profile returned: {data['email']}, credits: {data['credits']}")
    
    def test_student_credits_endpoint(self):
        """Test GET /api/student/credits returns credit balance (server.py endpoint)"""
        response = self.session.get(
            f"{BASE_URL}/api/student/credits",
            headers=self.auth_headers
        )
        
        assert response.status_code == 200, f"Credits endpoint failed: {response.text}"
        data = response.json()
        
        # Validate response structure (server.py format)
        assert "credits" in data, "Missing 'credits' in response"
        assert "credits_remaining" in data, "Missing 'credits_remaining' in response"
        assert isinstance(data["credits"], int), "Credits should be an integer"
        
        print(f"✓ Student credits: {data['credits']}, remaining: {data['credits_remaining']}")
    
    def test_student_use_credits_endpoint(self):
        """Test POST /api/student/use-credits deducts credits (server.py endpoint)"""
        # First get current credits
        credits_response = self.session.get(
            f"{BASE_URL}/api/student/credits",
            headers=self.auth_headers
        )
        initial_remaining = credits_response.json().get("credits_remaining", 0)
        
        # Use 1 credit (server.py uses query params: amount and action)
        response = self.session.post(
            f"{BASE_URL}/api/student/use-credits",
            headers=self.auth_headers,
            params={
                "amount": 1,
                "action": "ai_tutor"
            }
        )
        
        assert response.status_code == 200, f"Use credits failed: {response.text}"
        data = response.json()
        
        assert "credits_used" in data, "Missing 'credits_used' in response"
        assert "credits_remaining" in data, "Missing 'credits_remaining' in response"
        assert data["credits_used"] == 1, "Credits used should be 1"
        assert data["credits_remaining"] == initial_remaining - 1, f"Remaining credits mismatch: expected {initial_remaining - 1}, got {data['credits_remaining']}"
        
        print(f"✓ Used 1 credit, remaining: {data['credits_remaining']}")
    
    def test_student_use_credits_insufficient(self):
        """Test POST /api/student/use-credits fails with insufficient credits"""
        response = self.session.post(
            f"{BASE_URL}/api/student/use-credits",
            headers=self.auth_headers,
            params={
                "amount": 999999,  # Very large amount
                "action": "ai_tutor"
            }
        )
        
        # Should fail with 402 for insufficient credits (server.py uses 402)
        assert response.status_code == 402, f"Expected 402 for insufficient credits, got {response.status_code}"
        print("✓ Insufficient credits correctly rejected with 402")
    
    def test_student_upcoming_classes_endpoint(self):
        """Test GET /api/student/upcoming-classes returns enrolled classes (new router)"""
        response = self.session.get(
            f"{BASE_URL}/api/student/upcoming-classes",
            headers=self.auth_headers
        )
        
        assert response.status_code == 200, f"Upcoming classes failed: {response.text}"
        data = response.json()
        
        assert "classes" in data, "Missing 'classes' in response"
        assert isinstance(data["classes"], list), "Classes should be a list"
        
        print(f"✓ Upcoming classes returned: {len(data['classes'])} classes")
    
    def test_placement_test_check_endpoint(self):
        """Test GET /api/student/should-take-placement-test (new router)"""
        response = self.session.get(
            f"{BASE_URL}/api/student/should-take-placement-test",
            headers=self.auth_headers
        )
        
        assert response.status_code == 200, f"Placement test check failed: {response.text}"
        data = response.json()
        
        assert "should_take" in data, "Missing 'should_take' in response"
        assert isinstance(data["should_take"], bool), "should_take should be a boolean"
        
        # The response may have different fields based on implementation
        print(f"✓ Placement test check: should_take={data['should_take']}")
    
    def test_student_profile_requires_auth(self):
        """Test that student profile requires authentication"""
        response = self.session.get(f"{BASE_URL}/api/student/profile")
        assert response.status_code in [401, 403], f"Expected 401/403 without auth, got {response.status_code}"
        print("✓ Student profile correctly requires authentication")


class TestVideoClassesEndpoints:
    """Tests for Video Classes endpoints (server.py implementation)"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test fixtures"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        
        # Login as student
        student_response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": STUDENT_EMAIL,
            "password": STUDENT_PASSWORD
        })
        assert student_response.status_code == 200, f"Student login failed: {student_response.text}"
        student_data = student_response.json()
        self.student_token = student_data.get("access_token")
        self.student_user = student_data.get("user")
        self.student_headers = {"Authorization": f"Bearer {self.student_token}"}
        
        # Login as institution
        inst_response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": INSTITUTION_EMAIL,
            "password": INSTITUTION_PASSWORD
        })
        assert inst_response.status_code == 200, f"Institution login failed: {inst_response.text}"
        inst_data = inst_response.json()
        self.institution_token = inst_data.get("access_token")
        self.institution_user = inst_data.get("user")
        self.institution_headers = {"Authorization": f"Bearer {self.institution_token}"}
    
    def test_video_classes_list_endpoint(self):
        """Test GET /api/video-classes returns classes list (server.py format)"""
        response = self.session.get(
            f"{BASE_URL}/api/video-classes",
            headers=self.student_headers
        )
        
        assert response.status_code == 200, f"Video classes list failed: {response.text}"
        data = response.json()
        
        # Server.py returns live_classes, recorded_classes, stats
        assert "live_classes" in data, "Missing 'live_classes' in response"
        assert "recorded_classes" in data, "Missing 'recorded_classes' in response"
        assert "total" in data, "Missing 'total' in response"
        assert "stats" in data, "Missing 'stats' in response"
        
        assert isinstance(data["live_classes"], list), "live_classes should be a list"
        assert isinstance(data["recorded_classes"], list), "recorded_classes should be a list"
        
        print(f"✓ Video classes list: {len(data['live_classes'])} live, {len(data['recorded_classes'])} recorded, total: {data['total']}")
    
    def test_video_classes_list_with_filters(self):
        """Test GET /api/video-classes with query filters"""
        response = self.session.get(
            f"{BASE_URL}/api/video-classes",
            headers=self.student_headers,
            params={
                "exam_type": "ielts"
            }
        )
        
        assert response.status_code == 200, f"Filtered video classes failed: {response.text}"
        data = response.json()
        
        assert "live_classes" in data, "Missing 'live_classes' in response"
        print(f"✓ Filtered video classes: {len(data['live_classes'])} live classes for IELTS")
    
    def test_institution_create_video_class(self):
        """Test POST /api/video-classes creates a new class (institution only)"""
        # Schedule class for tomorrow
        scheduled_time = (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()
        
        response = self.session.post(
            f"{BASE_URL}/api/video-classes",
            headers=self.institution_headers,
            json={
                "title": f"TEST_Video Class {uuid.uuid4().hex[:8]}",
                "description": "Test video class for automated testing",
                "exam_type": "ielts",
                "skill": "speaking",
                "class_type": "live",
                "duration_minutes": 60,
                "scheduled_at": scheduled_time,
                "max_students": 30
            }
        )
        
        assert response.status_code == 200, f"Create video class failed: {response.text}"
        data = response.json()
        
        assert "id" in data, "Missing 'id' in response"
        
        self.created_class_id = data["id"]
        print(f"✓ Created video class: {data['id']}")
        
        # Cleanup
        self.session.delete(
            f"{BASE_URL}/api/video-classes/{data['id']}",
            headers=self.institution_headers
        )
    
    def test_student_cannot_create_video_class(self):
        """Test that students cannot create video classes"""
        scheduled_time = (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()
        
        response = self.session.post(
            f"{BASE_URL}/api/video-classes",
            headers=self.student_headers,
            json={
                "title": "Student Test Class",
                "description": "Should fail",
                "exam_type": "ielts",
                "skill": "speaking",
                "class_type": "live",
                "scheduled_at": scheduled_time
            }
        )
        
        assert response.status_code == 403, f"Expected 403 for student creating class, got {response.status_code}"
        print("✓ Students correctly cannot create video classes")
    
    def test_video_class_enrollment_flow(self):
        """Test full enrollment flow: create class -> enroll student"""
        # First create a class as institution
        scheduled_time = (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()
        
        create_response = self.session.post(
            f"{BASE_URL}/api/video-classes",
            headers=self.institution_headers,
            json={
                "title": f"TEST_Enrollment Test Class {uuid.uuid4().hex[:8]}",
                "description": "Test class for enrollment testing",
                "exam_type": "ielts",
                "skill": "listening",
                "class_type": "live",
                "duration_minutes": 45,
                "scheduled_at": scheduled_time,
                "max_students": 50
            }
        )
        
        assert create_response.status_code == 200, f"Create class failed: {create_response.text}"
        class_id = create_response.json()["id"]
        print(f"✓ Created class for enrollment test: {class_id}")
        
        # Now enroll as student
        enroll_response = self.session.post(
            f"{BASE_URL}/api/video-classes/{class_id}/enroll",
            headers=self.student_headers
        )
        
        assert enroll_response.status_code == 200, f"Enrollment failed: {enroll_response.text}"
        enroll_data = enroll_response.json()
        
        assert "message" in enroll_data, "Missing 'message' in enrollment response"
        print(f"✓ Student enrolled successfully: {enroll_data['message']}")
        
        # Try to enroll again - server.py returns 200 with "Already enrolled"
        duplicate_response = self.session.post(
            f"{BASE_URL}/api/video-classes/{class_id}/enroll",
            headers=self.student_headers
        )
        
        # Server.py returns 200 with "Already enrolled" message
        assert duplicate_response.status_code == 200, f"Duplicate enrollment response: {duplicate_response.status_code}"
        dup_data = duplicate_response.json()
        assert "Already enrolled" in dup_data.get("message", ""), "Expected 'Already enrolled' message"
        print("✓ Duplicate enrollment returns 'Already enrolled' message")
        
        # Cleanup - delete the class
        delete_response = self.session.delete(
            f"{BASE_URL}/api/video-classes/{class_id}",
            headers=self.institution_headers
        )
        assert delete_response.status_code == 200, f"Cleanup delete failed: {delete_response.text}"
        print(f"✓ Cleaned up test class: {class_id}")
    
    def test_institution_update_class_status(self):
        """Test PUT /api/video-classes/{class_id}/status updates status"""
        # First create a class
        scheduled_time = (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()
        
        create_response = self.session.post(
            f"{BASE_URL}/api/video-classes",
            headers=self.institution_headers,
            json={
                "title": f"TEST_Status Update Class {uuid.uuid4().hex[:8]}",
                "description": "Test class for status update",
                "exam_type": "ielts",
                "skill": "writing",
                "class_type": "live",
                "scheduled_at": scheduled_time
            }
        )
        
        assert create_response.status_code == 200, f"Create class failed: {create_response.text}"
        class_id = create_response.json()["id"]
        print(f"✓ Created class for status test: {class_id}")
        
        # Update status to 'live'
        status_response = self.session.put(
            f"{BASE_URL}/api/video-classes/{class_id}/status",
            headers=self.institution_headers,
            params={"status": "live"}
        )
        
        assert status_response.status_code == 200, f"Status update failed: {status_response.text}"
        status_data = status_response.json()
        
        assert "message" in status_data, "Missing 'message' in status response"
        print(f"✓ Status updated to 'live': {status_data['message']}")
        
        # Update status to 'ended' (server.py uses 'ended' not 'completed')
        complete_response = self.session.put(
            f"{BASE_URL}/api/video-classes/{class_id}/status",
            headers=self.institution_headers,
            params={"status": "ended"}
        )
        
        assert complete_response.status_code == 200, f"End status update failed: {complete_response.text}"
        print("✓ Status updated to 'ended'")
        
        # Test invalid status
        invalid_response = self.session.put(
            f"{BASE_URL}/api/video-classes/{class_id}/status",
            headers=self.institution_headers,
            params={"status": "invalid_status"}
        )
        
        assert invalid_response.status_code == 400, f"Expected 400 for invalid status, got {invalid_response.status_code}"
        print("✓ Invalid status correctly rejected")
        
        # Cleanup
        self.session.delete(
            f"{BASE_URL}/api/video-classes/{class_id}",
            headers=self.institution_headers
        )
        print(f"✓ Cleaned up test class: {class_id}")
    
    def test_student_cannot_update_class_status(self):
        """Test that students cannot update class status"""
        # First create a class as institution
        scheduled_time = (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()
        
        create_response = self.session.post(
            f"{BASE_URL}/api/video-classes",
            headers=self.institution_headers,
            json={
                "title": f"TEST_Student Status Test {uuid.uuid4().hex[:8]}",
                "description": "Test class for student status test",
                "exam_type": "ielts",
                "skill": "reading",
                "class_type": "live",
                "scheduled_at": scheduled_time
            }
        )
        
        assert create_response.status_code == 200, f"Create class failed: {create_response.text}"
        class_id = create_response.json()["id"]
        
        # Try to update status as student
        status_response = self.session.put(
            f"{BASE_URL}/api/video-classes/{class_id}/status",
            headers=self.student_headers,
            params={"status": "live"}
        )
        
        assert status_response.status_code == 403, f"Expected 403 for student updating status, got {status_response.status_code}"
        print("✓ Students correctly cannot update class status")
        
        # Cleanup
        self.session.delete(
            f"{BASE_URL}/api/video-classes/{class_id}",
            headers=self.institution_headers
        )
    
    def test_video_class_not_found(self):
        """Test enrollment returns 404 for non-existent class"""
        fake_id = str(uuid.uuid4())
        
        response = self.session.post(
            f"{BASE_URL}/api/video-classes/{fake_id}/enroll",
            headers=self.student_headers
        )
        
        assert response.status_code == 404, f"Expected 404 for non-existent class, got {response.status_code}"
        print("✓ Non-existent class correctly returns 404")
    
    def test_delete_video_class(self):
        """Test DELETE /api/video-classes/{class_id}"""
        # Create a class first
        scheduled_time = (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()
        
        create_response = self.session.post(
            f"{BASE_URL}/api/video-classes",
            headers=self.institution_headers,
            json={
                "title": f"TEST_Delete Class {uuid.uuid4().hex[:8]}",
                "description": "Test class for deletion",
                "exam_type": "ielts",
                "skill": "speaking",
                "class_type": "live",
                "scheduled_at": scheduled_time
            }
        )
        
        assert create_response.status_code == 200, f"Create class failed: {create_response.text}"
        class_id = create_response.json()["id"]
        print(f"✓ Created class for deletion test: {class_id}")
        
        # Delete the class
        delete_response = self.session.delete(
            f"{BASE_URL}/api/video-classes/{class_id}",
            headers=self.institution_headers
        )
        
        assert delete_response.status_code == 200, f"Delete failed: {delete_response.text}"
        print(f"✓ Deleted class: {class_id}")
        
        # Verify it's deleted - enrollment should fail
        enroll_response = self.session.post(
            f"{BASE_URL}/api/video-classes/{class_id}/enroll",
            headers=self.student_headers
        )
        
        assert enroll_response.status_code == 404, f"Expected 404 after deletion, got {enroll_response.status_code}"
        print("✓ Verified class is deleted (enrollment returns 404)")


class TestRoutersLoading:
    """Test that all routers load without errors"""
    
    def test_student_router_endpoints_accessible(self):
        """Verify student router endpoints are accessible"""
        session = requests.Session()
        
        # Login first
        login_response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": STUDENT_EMAIL,
            "password": STUDENT_PASSWORD
        })
        token = login_response.json().get("access_token")
        headers = {"Authorization": f"Bearer {token}"}
        
        # Test each student endpoint exists
        endpoints = [
            ("/api/student/profile", "GET"),
            ("/api/student/credits", "GET"),
            ("/api/student/upcoming-classes", "GET"),
            ("/api/student/should-take-placement-test", "GET")
        ]
        
        for endpoint, method in endpoints:
            if method == "GET":
                response = session.get(f"{BASE_URL}{endpoint}", headers=headers)
            else:
                response = session.post(f"{BASE_URL}{endpoint}", headers=headers)
            
            # Should not be 404 (route not found)
            assert response.status_code != 404, f"Endpoint {endpoint} not found"
            print(f"✓ Endpoint {endpoint} is accessible (status: {response.status_code})")
    
    def test_video_classes_router_endpoints_accessible(self):
        """Verify video classes router endpoints are accessible"""
        session = requests.Session()
        
        # Login first
        login_response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": STUDENT_EMAIL,
            "password": STUDENT_PASSWORD
        })
        token = login_response.json().get("access_token")
        headers = {"Authorization": f"Bearer {token}"}
        
        # Test video classes endpoint exists
        response = session.get(f"{BASE_URL}/api/video-classes", headers=headers)
        assert response.status_code == 200, f"Video classes endpoint failed: {response.text}"
        print(f"✓ Video classes endpoint is accessible (status: {response.status_code})")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
