"""
B2B Auth System Tests
Tests for:
- Institution registration and login
- Institution branding setup (PUT /api/institution/branding)
- White-label student portal branding (GET /api/institution/branding/{slug})
- Student creation with provisional credentials (POST /api/institution/students/create)
- Student login returns requires_password_change=true for first login
- Password change flow (/api/auth/change-password)
- Student credits system (GET /api/student/credits)
"""

import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://b2b-exam-prep.preview.emergentagent.com').rstrip('/')

# Test credentials
ADMIN_EMAIL = "santaliestralimited@gmail.com"
ADMIN_PASSWORD = "Admin123!"
INSTITUTION_EMAIL = "demo_academy@test.com"
INSTITUTION_PASSWORD = "Demo123!"
STUDENT_EMAIL = "student1@demo.com"
STUDENT_PROVISIONAL_PASSWORD = "62Wuaor4R4Qp"


class TestInstitutionAuth:
    """Test institution registration and login flows"""
    
    def test_institution_login_success(self):
        """Test institution can login successfully"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": INSTITUTION_EMAIL, "password": INSTITUTION_PASSWORD}
        )
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert "access_token" in data
        assert "user" in data
        assert data["user"]["user_type"] == "institution"
        assert data["user"]["email"] == INSTITUTION_EMAIL
        assert "requires_password_change" in data
        assert data["requires_password_change"] == False  # Institution doesn't need password change
        
    def test_institution_login_invalid_credentials(self):
        """Test institution login fails with wrong password"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": INSTITUTION_EMAIL, "password": "wrongpassword"}
        )
        assert response.status_code == 401
        
    def test_admin_login_success(self):
        """Test admin can login successfully"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["user"]["user_type"] == "admin"


class TestInstitutionBranding:
    """Test institution branding setup and white-label portal"""
    
    @pytest.fixture
    def institution_token(self):
        """Get institution auth token"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": INSTITUTION_EMAIL, "password": INSTITUTION_PASSWORD}
        )
        return response.json()["access_token"]
    
    def test_get_institution_branding(self, institution_token):
        """Test GET /api/institution/branding returns current branding"""
        response = requests.get(
            f"{BASE_URL}/api/institution/branding",
            headers={"Authorization": f"Bearer {institution_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        
        # Verify branding structure
        assert "slug" in data
        assert "branding" in data
        assert "student_portal_url" in data
        
    def test_update_institution_branding(self, institution_token):
        """Test PUT /api/institution/branding updates branding settings"""
        branding_data = {
            "name": "Demo Language Academy",
            "logo_url": None,
            "primary_color": "#2563EB",
            "secondary_color": "#1E40AF",
            "tagline": "Master your English exam",
            "custom_domain": None,
            "hide_powered_by": True
        }
        
        response = requests.put(
            f"{BASE_URL}/api/institution/branding",
            json=branding_data,
            headers={"Authorization": f"Bearer {institution_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        
        assert "message" in data
        assert "student_portal_url" in data
        assert "demo-language-academy" in data["student_portal_url"]
        
    def test_get_whitelabel_branding_by_slug(self):
        """Test GET /api/institution/branding/{slug} returns white-label branding"""
        response = requests.get(f"{BASE_URL}/api/institution/branding/demo-language-academy")
        assert response.status_code == 200
        data = response.json()
        
        # Verify white-label branding structure
        assert "name" in data
        assert "primaryColor" in data
        assert "secondaryColor" in data
        assert "tagline" in data
        assert "hide_powered_by" in data
        
    def test_get_whitelabel_branding_invalid_slug(self):
        """Test GET /api/institution/branding/{slug} returns 404 for invalid slug"""
        response = requests.get(f"{BASE_URL}/api/institution/branding/nonexistent-institution")
        assert response.status_code == 404


class TestStudentCreation:
    """Test student creation with provisional credentials"""
    
    @pytest.fixture
    def institution_token(self):
        """Get institution auth token"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": INSTITUTION_EMAIL, "password": INSTITUTION_PASSWORD}
        )
        return response.json()["access_token"]
    
    def test_create_student_with_credentials(self, institution_token):
        """Test POST /api/institution/students/create creates student with provisional password"""
        unique_email = f"test_student_{uuid.uuid4().hex[:8]}@test.com"
        
        response = requests.post(
            f"{BASE_URL}/api/institution/students/create",
            json={
                "email": unique_email,
                "name": "Test Student",
                "exam_type": "ielts",
                "credits": 100
            },
            headers={"Authorization": f"Bearer {institution_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert "id" in data
        assert "email" in data
        assert data["email"] == unique_email
        assert "provisional_password" in data
        assert len(data["provisional_password"]) == 12  # 12 character password
        assert "credits" in data
        assert data["credits"] == 100
        assert "message" in data
        
        return data
        
    def test_create_student_duplicate_email(self, institution_token):
        """Test creating student with existing email fails"""
        response = requests.post(
            f"{BASE_URL}/api/institution/students/create",
            json={
                "email": STUDENT_EMAIL,  # Already exists
                "name": "Duplicate Student",
                "exam_type": "ielts",
                "credits": 100
            },
            headers={"Authorization": f"Bearer {institution_token}"}
        )
        assert response.status_code == 400
        assert "already registered" in response.json()["detail"].lower()
        
    def test_get_institution_students(self, institution_token):
        """Test GET /api/institution/students returns student list"""
        response = requests.get(
            f"{BASE_URL}/api/institution/students",
            headers={"Authorization": f"Bearer {institution_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, list)
        assert len(data) >= 1  # At least one student exists
        
        # Verify student structure
        student = data[0]
        assert "id" in student
        assert "email" in student
        assert "name" in student
        assert "institution_id" in student


class TestStudentLogin:
    """Test student login with provisional credentials and password change requirement"""
    
    def test_student_login_requires_password_change(self):
        """Test student login with provisional credentials returns requires_password_change=true"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": STUDENT_EMAIL, "password": STUDENT_PROVISIONAL_PASSWORD}
        )
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert "access_token" in data
        assert "user" in data
        assert data["user"]["user_type"] == "student"
        assert "requires_password_change" in data
        assert data["requires_password_change"] == True  # First login requires password change
        
    def test_student_login_invalid_credentials(self):
        """Test student login fails with wrong password"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": STUDENT_EMAIL, "password": "wrongpassword"}
        )
        assert response.status_code == 401


class TestPasswordChange:
    """Test password change flow"""
    
    @pytest.fixture
    def student_token(self):
        """Get student auth token"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": STUDENT_EMAIL, "password": STUDENT_PROVISIONAL_PASSWORD}
        )
        return response.json()["access_token"]
    
    def test_change_password_wrong_current(self, student_token):
        """Test password change fails with wrong current password"""
        response = requests.post(
            f"{BASE_URL}/api/auth/change-password",
            json={
                "current_password": "wrongpassword",
                "new_password": "NewSecure123!"
            },
            headers={"Authorization": f"Bearer {student_token}"}
        )
        assert response.status_code == 400
        assert "incorrect" in response.json()["detail"].lower()
        
    def test_change_password_too_short(self, student_token):
        """Test password change fails with short password"""
        response = requests.post(
            f"{BASE_URL}/api/auth/change-password",
            json={
                "current_password": STUDENT_PROVISIONAL_PASSWORD,
                "new_password": "short"
            },
            headers={"Authorization": f"Bearer {student_token}"}
        )
        assert response.status_code == 400
        assert "8 characters" in response.json()["detail"]


class TestStudentCredits:
    """Test student credits system"""
    
    @pytest.fixture
    def student_token(self):
        """Get student auth token"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": STUDENT_EMAIL, "password": STUDENT_PROVISIONAL_PASSWORD}
        )
        return response.json()["access_token"]
    
    def test_get_student_credits(self, student_token):
        """Test GET /api/student/credits returns credit balance"""
        response = requests.get(
            f"{BASE_URL}/api/student/credits",
            headers={"Authorization": f"Bearer {student_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        
        # Verify credits structure
        assert "credits" in data
        assert "credits_used" in data
        assert "credits_remaining" in data
        assert "current_exam" in data
        assert "exam_access" in data
        
        # Verify values
        assert data["credits"] >= 0
        assert data["credits_remaining"] == data["credits"] - data["credits_used"]
        
    def test_student_credits_forbidden_for_institution(self):
        """Test institution cannot access student credits endpoint"""
        # Login as institution
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": INSTITUTION_EMAIL, "password": INSTITUTION_PASSWORD}
        )
        token = response.json()["access_token"]
        
        # Try to access student credits
        response = requests.get(
            f"{BASE_URL}/api/student/credits",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 403


class TestInstitutionMetrics:
    """Test institution metrics and analytics"""
    
    @pytest.fixture
    def institution_token(self):
        """Get institution auth token"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": INSTITUTION_EMAIL, "password": INSTITUTION_PASSWORD}
        )
        return response.json()["access_token"]
    
    def test_get_institution_metrics(self, institution_token):
        """Test GET /api/institution/metrics returns analytics"""
        response = requests.get(
            f"{BASE_URL}/api/institution/metrics",
            headers={"Authorization": f"Bearer {institution_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        
        # Verify metrics structure
        assert "total_students" in data
        assert "avg_pass_probability" in data
        assert "avg_risk_score" in data
        assert "at_risk_students" in data
        assert "high_performers" in data


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
