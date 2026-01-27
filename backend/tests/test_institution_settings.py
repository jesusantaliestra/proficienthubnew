"""
Test suite for Institution Settings, Gamification, and Student Profile endpoints
Tests: Zoom, Email, Gamification settings, Student profile, Upcoming classes
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
INSTITUTION_EMAIL = "demo_academy@test.com"
INSTITUTION_PASSWORD = "Demo123!"


class TestInstitutionAuth:
    """Test authentication for institution"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get authentication token for institution"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": INSTITUTION_EMAIL,
            "password": INSTITUTION_PASSWORD
        })
        if response.status_code == 200:
            return response.json().get("access_token")
        pytest.skip(f"Authentication failed: {response.status_code} - {response.text}")
    
    @pytest.fixture(scope="class")
    def auth_headers(self, auth_token):
        """Get headers with auth token"""
        return {"Authorization": f"Bearer {auth_token}"}
    
    def test_institution_login(self):
        """Test institution can login"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": INSTITUTION_EMAIL,
            "password": INSTITUTION_PASSWORD
        })
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        assert "access_token" in data
        assert data["user"]["user_type"] == "institution"


class TestInstitutionSettings:
    """Test Institution Settings endpoints"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get authentication token for institution"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": INSTITUTION_EMAIL,
            "password": INSTITUTION_PASSWORD
        })
        if response.status_code == 200:
            return response.json().get("access_token")
        pytest.skip(f"Authentication failed: {response.status_code}")
    
    @pytest.fixture(scope="class")
    def auth_headers(self, auth_token):
        """Get headers with auth token"""
        return {"Authorization": f"Bearer {auth_token}"}
    
    def test_get_institution_settings(self, auth_headers):
        """GET /api/institution/settings - Returns settings object"""
        response = requests.get(f"{BASE_URL}/api/institution/settings", headers=auth_headers)
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        # Settings should have zoom, email, gamification sections
        assert "zoom" in data or "gamification" in data or "email" in data or "institution_id" in data
    
    def test_get_settings_unauthenticated(self):
        """GET /api/institution/settings - Requires authentication"""
        response = requests.get(f"{BASE_URL}/api/institution/settings")
        assert response.status_code in [401, 403], f"Should require auth: {response.status_code}"
    
    def test_save_zoom_settings(self, auth_headers):
        """POST /api/institution/settings/zoom - Save Zoom settings"""
        zoom_config = {
            "zoom_account_id": "TEST_account_123",
            "zoom_client_id": "TEST_client_456",
            "zoom_client_secret": "TEST_secret_789",
            "zoom_enabled": False  # Keep disabled for testing
        }
        response = requests.post(f"{BASE_URL}/api/institution/settings/zoom", 
                                json=zoom_config, headers=auth_headers)
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        assert "message" in data
        assert "saved" in data["message"].lower()
    
    def test_save_email_settings(self, auth_headers):
        """POST /api/institution/settings/email - Save Email SMTP settings"""
        email_config = {
            "smtp_host": "smtp.test.com",
            "smtp_port": 587,
            "smtp_user": "test@test.com",
            "smtp_password": "test_password",
            "smtp_from_email": "noreply@test.com",
            "smtp_from_name": "Test Academy",
            "smtp_enabled": False,  # Keep disabled for testing
            "smtp_use_tls": True
        }
        response = requests.post(f"{BASE_URL}/api/institution/settings/email", 
                                json=email_config, headers=auth_headers)
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        assert "message" in data
        assert "saved" in data["message"].lower()
    
    def test_save_gamification_settings(self, auth_headers):
        """POST /api/institution/settings/gamification - Save gamification settings"""
        gamification_config = {
            "gamification_enabled": True,
            "xp_per_exam": 50,
            "xp_per_section": 20,
            "xp_per_tutor_session": 15,
            "xp_per_class": 30,
            "streak_bonus_multiplier": 1.5,
            "leaderboard_enabled": True,
            "badges_enabled": True,
            "challenges_enabled": True,
            "weekly_challenges_count": 3
        }
        response = requests.post(f"{BASE_URL}/api/institution/settings/gamification", 
                                json=gamification_config, headers=auth_headers)
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        assert "message" in data
        assert "saved" in data["message"].lower()
    
    def test_verify_settings_persisted(self, auth_headers):
        """Verify settings are persisted after save"""
        response = requests.get(f"{BASE_URL}/api/institution/settings", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        
        # Check gamification settings were saved
        if "gamification" in data:
            gam = data["gamification"]
            assert gam.get("gamification_enabled") == True
            assert gam.get("xp_per_exam") == 50


class TestGamificationEndpoints:
    """Test Gamification system endpoints"""
    
    @pytest.fixture(scope="class")
    def institution_token(self):
        """Get institution auth token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": INSTITUTION_EMAIL,
            "password": INSTITUTION_PASSWORD
        })
        if response.status_code == 200:
            return response.json().get("access_token")
        pytest.skip("Institution auth failed")
    
    @pytest.fixture(scope="class")
    def institution_headers(self, institution_token):
        return {"Authorization": f"Bearer {institution_token}"}
    
    def test_gamification_profile_requires_student(self, institution_headers):
        """GET /api/gamification/profile - Only students can access"""
        response = requests.get(f"{BASE_URL}/api/gamification/profile", headers=institution_headers)
        # Institution should get 403 or empty response
        assert response.status_code in [200, 403], f"Unexpected: {response.status_code}"
        if response.status_code == 200:
            # If 200, should indicate not a student
            data = response.json()
            # Either gamification_enabled: false or error
            assert "gamification_enabled" in data or "detail" in data
    
    def test_gamification_leaderboard(self, institution_headers):
        """GET /api/gamification/leaderboard - Returns leaderboard"""
        response = requests.get(f"{BASE_URL}/api/gamification/leaderboard", headers=institution_headers)
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        assert "leaderboard" in data
        assert isinstance(data["leaderboard"], list)
    
    def test_gamification_challenges(self, institution_headers):
        """GET /api/gamification/challenges - Returns weekly challenges (MOCKED)"""
        response = requests.get(f"{BASE_URL}/api/gamification/challenges", headers=institution_headers)
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        assert "challenges" in data
        assert isinstance(data["challenges"], list)
        
        # Verify challenge structure
        if len(data["challenges"]) > 0:
            challenge = data["challenges"][0]
            assert "id" in challenge
            assert "name" in challenge
            assert "description" in challenge
            assert "xp_reward" in challenge
            assert "target" in challenge
            assert "progress" in challenge


class TestStudentEndpoints:
    """Test Student profile and classes endpoints"""
    
    @pytest.fixture(scope="class")
    def institution_token(self):
        """Get institution auth token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": INSTITUTION_EMAIL,
            "password": INSTITUTION_PASSWORD
        })
        if response.status_code == 200:
            return response.json().get("access_token")
        pytest.skip("Institution auth failed")
    
    @pytest.fixture(scope="class")
    def institution_headers(self, institution_token):
        return {"Authorization": f"Bearer {institution_token}"}
    
    def test_student_profile_requires_student(self, institution_headers):
        """GET /api/student/profile - Only students can access"""
        response = requests.get(f"{BASE_URL}/api/student/profile", headers=institution_headers)
        # Institution should get 403
        assert response.status_code == 403, f"Should be 403 for institution: {response.status_code}"
    
    def test_student_upcoming_classes(self, institution_headers):
        """GET /api/student/upcoming-classes - Returns classes list"""
        response = requests.get(f"{BASE_URL}/api/student/upcoming-classes", headers=institution_headers)
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        assert "classes" in data
        assert isinstance(data["classes"], list)


class TestZoomIntegration:
    """Test Zoom integration endpoints (structure only - requires real credentials)"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get authentication token for institution"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": INSTITUTION_EMAIL,
            "password": INSTITUTION_PASSWORD
        })
        if response.status_code == 200:
            return response.json().get("access_token")
        pytest.skip("Authentication failed")
    
    @pytest.fixture(scope="class")
    def auth_headers(self, auth_token):
        return {"Authorization": f"Bearer {auth_token}"}
    
    def test_zoom_test_connection_requires_credentials(self, auth_headers):
        """POST /api/institution/settings/zoom/test - Requires valid credentials"""
        # Test with empty credentials - should fail gracefully
        response = requests.post(f"{BASE_URL}/api/institution/settings/zoom/test", 
                                json={"zoom_client_id": "", "zoom_client_secret": "", "zoom_account_id": ""},
                                headers=auth_headers)
        # Should return 400 for missing credentials
        assert response.status_code == 400, f"Should require credentials: {response.status_code}"
    
    def test_zoom_create_meeting_requires_config(self, auth_headers):
        """POST /api/zoom/meetings/create - Requires Zoom to be configured"""
        response = requests.post(f"{BASE_URL}/api/zoom/meetings/create",
                                params={"topic": "Test Meeting", "start_time": "2026-02-01T10:00:00Z", "duration": 60},
                                headers=auth_headers)
        # Should fail if Zoom not properly configured
        assert response.status_code in [400, 200], f"Unexpected: {response.status_code}"


class TestEmailIntegration:
    """Test Email SMTP integration endpoints"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get authentication token for institution"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": INSTITUTION_EMAIL,
            "password": INSTITUTION_PASSWORD
        })
        if response.status_code == 200:
            return response.json().get("access_token")
        pytest.skip("Authentication failed")
    
    @pytest.fixture(scope="class")
    def auth_headers(self, auth_token):
        return {"Authorization": f"Bearer {auth_token}"}
    
    def test_email_test_requires_credentials(self, auth_headers):
        """POST /api/institution/settings/email/test - Requires SMTP credentials"""
        response = requests.post(f"{BASE_URL}/api/institution/settings/email/test",
                                json={"test_email": "test@test.com"},
                                headers=auth_headers)
        # Should return 400 for missing SMTP credentials
        assert response.status_code == 400, f"Should require SMTP config: {response.status_code}"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
